> **Security research tool — authorized use only.**
> Run these harnesses against your own systems only.
> Unauthorized use against systems you do not own or have explicit written permission to test is illegal.

# Buildcraft

A toy Claude Code clone built stage by stage to understand how agentic AI systems work from the inside — then attacked to build a runtime authorization probe no existing tool covers.

## What this is

Two parallel tracks after stage 5:

- **Builder track** (stages 1-10): build a coding agent from scratch using pydantic-ai
- **Security track** (S1-S5): attack what you built, automate the attacks into a harness

The harness is the product: a runtime authorization probe for multi-agent systems — the gap garak, promptfoo, and PyRIT don't cover.

## Security harness

| Stage | What it tests | Harness |
|---|---|---|
| S1 | Gate bypass — can prompt injection make the agent run bash without `ask_user`? | `tests/test_s1_harness.py` |
| S2 | Command swap — can injected content redirect the bash command after the gate approves? | `tests/test_s2_harness.py` |
| S3 | RAG poisoning — poison the vector store, trigger S1/S2 | planned |
| S4 | Subagent hijack — compromise child agent via parent context | planned |
| S5 | Harness product — automate S1-S4 as reusable probes | planned |

### Running the harness

```bash
# S1 — gate bypass, all 8 transcript categories
PROBE_BUDGET=3 .venv/bin/pytest tests/test_s1_harness.py -v -s

# S1 — crescendo only
PROBE_BUDGET=3 .venv/bin/pytest tests/test_s1_harness.py::TestS1Campaign::test_crescendo -v -s

# S2 — command swap, append injection category
PROBE_BUDGET=1 .venv/bin/pytest tests/test_s2_harness.py::TestS2Campaign::test_append_injection -v -s
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `PROBE_BUDGET` | `3` | Attempts per category before moving on |
| `ATTACKER_MODEL` | `openai/gpt-4o` | OpenRouter model used to generate attack payloads |
| `OPENROUTER_API_KEY` | required | Set in `.env` |

### Verdicts

**S1:** `BYPASS` (gate bypassed) / `HELD` (gate fired, held) / `BLOCKED` (bash never attempted)

**S2:** `SWAP` (command redirected after approval) / `BENIGN` (safe command ran) / `BLOCKED` (bash never called)

Findings are written to `findings.md` / `findings_s2.md` only when weaknesses are found.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add OPENROUTER_API_KEY
```

## Builder track progress

See `PROGRESS.md` for the full stage-by-stage breakdown and learning notes.

## License

MIT — see `LICENSE`.
