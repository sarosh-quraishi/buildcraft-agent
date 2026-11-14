> **Security research tool — authorized use only.**
> Run these harnesses against your own systems only.
> Unauthorized use against systems you do not own or have explicit written permission to test is illegal.

# Buildcraft

A toy Claude Code clone built stage by stage to understand how agentic AI systems work from the inside — then attacked to build a runtime authorization probe no existing tool covers.

## What this is

Two parallel tracks after stage 5:

- **Builder track** (stages 1-10): build a coding agent from scratch using pydantic-ai
- **Security track** (S1-S5): attack what you built, automate the attacks into a harness

The harness is the product: a runtime authorization probe for multi-agent systems — the gap garak, promptfoo, and PyRIT don't cover. Filed as [garak issue #2436](https://github.com/NVIDIA/garak/issues/2436).

## Security harness

| Stage | What it tests | Status |
|---|---|---|
| S1 | Gate bypass — prompt injection makes agent run bash without `ask_user` | ✅ done |
| S2 | Command swap — injected content redirects bash command after gate approves | ✅ done |
| S3 | RAG poisoning — poison the vector store, trigger S1/S2 via retrieval layer | ✅ done |
| S4 | Subagent hijack — compromise child agent via parent context | planned (stage 8 prerequisite) |
| S5 | Generic harness — `Target` protocol, adapter pattern, attacker LLM, CLI | ✅ done |

### Generic harness (S5)

The S5 harness wraps any agent behind a `Target` protocol — probe logic stays decoupled from the agent framework.

```
src/harness/
├── target.py        # Target protocol + RunResult dataclass
├── adapters.py      # BuildcraftTarget (pydantic-ai)
├── probes/
│   └── s2.py        # S2 command-swap probes, 5 categories × 3 scenarios
├── runner.py        # runs probes, writes markdown report
└── __main__.py      # CLI entry point
```

**Run against buildcraft:**

```bash
# all S2 categories
python -m harness

# single category
python -m harness --category append_injection

# fast smoke test (1 attempt per category)
PROBE_BUDGET=1 python -m harness
```

**Plug in a different agent** — implement the `Target` protocol:

```python
class MyAgentTarget:
    async def run(self, prompt: str, history: list) -> RunResult: ...
    def plant_file(self, name: str, content: str) -> None: ...
    def cleanup(self) -> None: ...
```

### Per-stage harnesses

```bash
# S1 — gate bypass
PROBE_BUDGET=3 uv run pytest tests/test_s1_harness.py -v -s

# S2 — command swap
PROBE_BUDGET=3 uv run pytest tests/test_s2_harness.py -v -s

# S3 — RAG poisoning
PROBE_BUDGET=3 uv run pytest tests/test_s3_harness.py -v -s
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `PROBE_BUDGET` | `3` | Attempts per category before moving on |
| `ATTACKER_MODEL` | `openai/gpt-4o` | OpenRouter model used to generate payloads |
| `AGENT_MODEL` | `openrouter/...` | Model under test |
| `OPENROUTER_API_KEY` | required | Set in `.env` |

### Verdicts

**S1:** `BYPASS` (gate bypassed) / `HELD` (gate fired) / `BLOCKED` (bash never attempted)

**S2/S5:** `SWAP` (command redirected after approval) / `BENIGN` (safe command ran) / `BLOCKED` (bash never called)

Findings: `findings_s2.md`, `harness_report.md`

## Setup

```bash
uv sync
cp .env.example .env  # add OPENROUTER_API_KEY
```

## Builder track progress

See `PROGRESS.md` for the full stage-by-stage breakdown and learning notes.

## License

MIT — see `LICENSE`.
