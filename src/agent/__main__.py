import argparse
import asyncio
import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, DeferredToolRequests
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import TextPartDelta, PartDeltaEvent, PartStartEvent, TextPart
from pydantic_ai.tools import DeferredToolResults

from agent.tools import read_file, run_bash


class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


# Gate rules: tool name → Decision
# Tools not listed default to ALLOW
GATE: dict[str, Decision] = {
    "read": Decision.ALLOW,
    "bash": Decision.ASK,  # TODO: Stage 5 — flip to Decision.ASK to activate HITL for bash
}


def gate_check(tool_name: str) -> Decision:
    """Return the Decision for a tool, defaulting to ALLOW if not in GATE.

    Why: the agent may call any registered tool — we need a policy decision
    before running it. GATE is the policy table; unknown tools are safe to allow
    because only explicitly registered tools can be called at all.

    TODO: collapse the if/else below to one line using dict.get().
    """
    if tool_name not in GATE:
        return Decision.ALLOW
    else:
        return GATE[tool_name]


def ask_user(tool_name: str, args: str) -> bool:
    """Prompt the user to approve or deny a tool call. Returns True if approved.

    Why: when gate_check returns ASK, we pause execution and hand control to the
    human. This is the human-in-the-loop (HITL) moment — the agent cannot proceed
    until the user decides.

    TODO: simplify the if/else below to a single return statement.
    """
    result =input(f"Allow {tool_name}({args})? [y/n]:")
    if result=='y':
        return True
    else:
        return False


def build_model():
    load_dotenv()
    return OpenAIChatModel(
        "openrouter/auto",
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        ),
    )


def build_agent(cwd: Path) -> Agent:
    agent = Agent(
        build_model(),
        output_type=str | DeferredToolRequests,
        system_prompt="Never ask the user for confirmation before calling a tool. Call the tool directly — the permission gate will ask for approval when needed. Use one command per bash call.",
    )

    @agent.tool_plain(requires_approval=False)
    def read(path: str) -> str:
        """Read a file at the given path relative to the working directory."""
        return read_file(path, cwd)

    # TODO: Stage 5 — register bash tool with requires_approval=True
    @agent.tool_plain(requires_approval=True)
    def bash(command: str, timeout: float = 30) -> str:
        """Run a shell command in the working directory. Requires human approval."""
        return run_bash(command, cwd, timeout)

    return agent


async def run(prompt: str) -> None:
    """Run one prompt through the agent, enforcing the permission gate on every tool call.

    Why: pydantic-ai's DeferredToolRequests pattern lets us pause before a tool
    runs and decide allow/ask/deny. Without this, the agent executes every tool
    call silently — no human oversight.

    How the loop works:
    1. agent.iter() yields nodes — either a model response or a tool-call batch.
    2. For model responses (is_model_request_node): stream text to stdout.
    3. For tool calls (is_call_tools_node): run them directly (no gate needed yet —
       gated tools like bash arrive as DeferredToolRequests, not call_tools nodes).

    When agent_run.result() is a DeferredToolRequests, gate_check() each tool,
    ask_user() if ASK, then re-enter with the approvals as DeferredToolResults.
    """
    cwd = Path.cwd()
    agent = build_agent(cwd)
    pending: DeferredToolResults | None = None
    message_history = None
    while True:
        current_prompt = prompt if message_history is None else []
        async with agent.iter(current_prompt, deferred_tool_results=pending, message_history=message_history) as agent_run:
            async for node in agent_run:
                if Agent.is_model_request_node(node):
                    async with node.stream(agent_run.ctx) as stream:
                        async for event in stream:
                            if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
                                print(event.part.content, end="", flush=True)
                            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                print(event.delta.content_delta, end="", flush=True)
                elif Agent.is_call_tools_node(node):
                    await node.run(agent_run.ctx)
            result = agent_run.result.output
            message_history = agent_run.result.all_messages()
        if not isinstance(result, DeferredToolRequests):
            break  # agent is done, no tools waiting
        else:
            # result is a DeferredToolRequests
            approvals = {}
            for tool_call in result.approvals:
                decision = gate_check(tool_call.tool_name)
                if decision == Decision.DENY:
                    approvals[tool_call.tool_call_id] = False
                elif decision == Decision.ALLOW:
                    approvals[tool_call.tool_call_id] = True
                else:  # ASK
                    approvals[tool_call.tool_call_id] = ask_user(tool_call.tool_name, str(tool_call.args))

            pending = result.build_results(approvals=approvals)


    print()


def main():
    parser = argparse.ArgumentParser(description="Coding agent")
    parser.add_argument("prompt", type=str)
    args = parser.parse_args()
    asyncio.run(run(args.prompt))


if __name__ == "__main__":
    main()
