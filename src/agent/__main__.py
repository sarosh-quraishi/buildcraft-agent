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

from agent.tools import read_file


class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


# Gate rules: tool name → Decision
# Tools not listed default to ALLOW
GATE: dict[str, Decision] = {
    "read": Decision.ALLOW,
    # TODO: when you add bash in Stage 5, set it to Decision.ASK
}


def gate_check(tool_name: str) -> Decision:
    # TODO: return the Decision for tool_name, defaulting to ALLOW if not in GATE
    ???


def ask_user(tool_name: str, args: str) -> bool:
    """Print a prompt and return True if user approves."""
    # TODO: print "Allow {tool_name}({args})? [y/n]: " and return True if input is "y"
    ???


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
    agent = Agent(build_model(), output_type=str | DeferredToolRequests)

    @agent.tool_plain(requires_approval=False)
    def read(path: str) -> str:
        """Read a file at the given path relative to the working directory."""
        return read_file(path, cwd)

    return agent


async def run(prompt: str) -> None:
    cwd = Path.cwd()
    agent = build_agent(cwd)
    pending: DeferredToolResults | None = None

    async with agent.iter(prompt, deferred_tool_results=pending) as agent_run:
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

    print()


def main():
    parser = argparse.ArgumentParser(description="Coding agent")
    parser.add_argument("prompt", type=str)
    args = parser.parse_args()
    asyncio.run(run(args.prompt))


if __name__ == "__main__":
    main()
