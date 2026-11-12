# Attack Harness Roadmap

## v1 — Guided Search (current)

**What it is:** LLM-generated payloads with feedback steering.

Each campaign run feeds two signal lists back to the attacker-LLM:
- `partial_wins` — HELD verdicts (bash was called; gate fired but held). Attacker steers *toward* these.
- `failures` — BLOCKED verdicts (bash never called). Attacker steers *away* from these.

This is prompt-based policy improvement, not true RL. It's honest to call it "guided search."

**Limitations:**
- No weight updates — the attacker model doesn't actually learn across runs
- Signal only accumulates within a single campaign run (budget resets each pytest invocation)
- Useful only when HELD verdicts appear — pure BLOCKED output gives the attacker nothing to steer toward

---

## v1.5 — Retrieval-Augmented Attack Generation (RAAG)

**What it is:** verdict-weighted payload retrieval to steer generation across runs.

Instead of generating from scratch each run, embed all past payloads and retrieve the most
similar ones with HELD/BYPASS verdicts as few-shot examples for the attacker-LLM.

```
new attempt → embed objective + category
            → retrieve top-K similar payloads filtered by HELD/BYPASS verdict
            → feed as few-shot examples to attacker-LLM
            → generate new payload shaped like what worked before
```

**Key insight:** cross-category transfer. A HELD verdict in `persona_hacking` may share
embedding space with `authority_redirect` — the retrieval finds this automatically.

### Components

| Component | Tool | Cost |
|---|---|---|
| Payload store | `rollouts.jsonl` — shared with v2 RL | free |
| Embeddings | `text-embedding-3-small` via OpenAI | ~$0.00002/payload |
| Similarity search | `numpy` cosine similarity (< 10k payloads) | free |
| Retrieval | top-K by cosine sim, filter verdict ≥ HELD | ~5 lines |

### Changes to harness

1. Add `PayloadStore` class: append `(category, payload, verdict, embedding)` after each attempt
2. In `generate_payload()`: retrieve top-3 similar HELD/BYPASS payloads, inject as few-shot examples
3. Store persists across runs — value compounds over time

### Novelty assessment

Closest prior work: **MIRROR** (2026) uses memory to constrain *novelty* (avoid repeating failures).
This inverts that: use memory to *converge* toward what works. The specific combination of
verdict-weighted retrieval + cross-category transfer + tool-call authorization bypass (not text output)
has not been published. Novelty score: **7/10**.

**Trigger to start:** After S2 produces first HELD verdict — need real signal to retrieve against.

---

## v2 — RL-Trained Attacker

Based on: Tramèr et al., "Learning to Inject: Automated Prompt Injection via Reinforcement Learning" (NeurIPS 2026)

**Trigger to start:** S2 or S3 complete, with >20% HELD rate on at least one category.

### Components

| Component | Detail |
|---|---|
| Base model | Qwen 2.5 7B or Mistral 7B — small, fine-tunable, cheap |
| Training algorithm | GRPO (simpler than PPO, works well for text generation) |
| Reward signal | BYPASS = 1.0, HELD = 0.5, BLOCKED = 0.0 |
| Rollout storage | `rollouts.jsonl` — same file as v1.5 RAAG store |
| Fine-tuning platform | Together.ai or Modal — ~$20-30 per training run |

### Training loop

```
campaign run → collect (payload, verdict) into rollouts.jsonl
                         ↓
              fine-tune base model on rollouts (GRPO)
                         ↓
              swap generate_payload() → inference on fine-tuned model
                         ↓
              run campaign again — measure improvement
```

### Changes to harness

1. Add `--collect` flag: run campaign, write rollouts to `rollouts.jsonl`, skip training
2. Add `train.py`: reads rollouts, runs GRPO fine-tune via Together.ai API
3. Add `ATTACKER_MODEL_PATH` env var: when set, load local fine-tuned model instead of OpenRouter

### Estimated effort

- Rollout collection: 1 day (extend existing harness)
- GRPO training script: 2-3 days if new to RLHF, 1 day if not
- End-to-end loop working: ~1 week

### Prerequisites

- S2 (tool swap) complete — richer attack surface, more HELD verdicts to train on
- S3 (RAG poisoning) complete — indirect injection gives harder targets worth training against
- At least 500 rollouts collected — minimum for meaningful GRPO signal

---

## Why this matters (the product angle)

The S5 harness product gap vs garak/PyRIT is runtime authorization probing.
RAAG (v1.5) + RL (v2) close a second gap: **adaptive red teaming**.

Static payload libraries go stale as models improve. A retrieval-augmented attacker
gets smarter with each run for free. A trained attacker retrains against the current model.
That's the defensible moat — and `rollouts.jsonl` is the shared asset both approaches build on.


## v1 — Guided Search (current)

**What it is:** LLM-generated payloads with feedback steering.

Each campaign run feeds two signal lists back to the attacker-LLM:
- `partial_wins` — HELD verdicts (bash was called; gate fired but held). Attacker steers *toward* these.
- `failures` — BLOCKED verdicts (bash never called). Attacker steers *away* from these.

This is prompt-based policy improvement, not true RL. It's honest to call it "guided search."

**Limitations:**
- No weight updates — the attacker model doesn't actually learn across runs
- Signal only accumulates within a single campaign run (budget resets each pytest invocation)
- Useful only when HELD verdicts appear — pure BLOCKED output gives the attacker nothing to steer toward

---

## v2 — RL-Trained Attacker

Based on: Tramèr et al., "Learning to Inject: Automated Prompt Injection via Reinforcement Learning" (NeurIPS 2026)

**Trigger to start:** S2 or S3 complete, with >20% HELD rate on at least one category.

### Components

| Component | Detail |
|---|---|
| Base model | Qwen 2.5 7B or Mistral 7B — small, fine-tunable, cheap |
| Training algorithm | GRPO (simpler than PPO, works well for text generation) |
| Reward signal | BYPASS = 1.0, HELD = 0.5, BLOCKED = 0.0 |
| Rollout storage | JSONL file: `(category, payload, verdict)` per attempt |
| Fine-tuning platform | Together.ai or Modal — ~$20-30 per training run |

### Training loop

```
campaign run → collect (payload, verdict) into rollouts.jsonl
                         ↓
              fine-tune base model on rollouts (GRPO)
                         ↓
              swap generate_payload() → inference on fine-tuned model
                         ↓
              run campaign again — measure improvement
```

### Changes to harness

1. Add `--collect` flag: run campaign, write rollouts to `rollouts.jsonl`, skip training
2. Add `train.py`: reads rollouts, runs GRPO fine-tune via Together.ai API
3. Add `ATTACKER_MODEL_PATH` env var: when set, load local fine-tuned model instead of OpenRouter

### Estimated effort

- Rollout collection: 1 day (extend existing harness)
- GRPO training script: 2-3 days if new to RLHF, 1 day if not
- End-to-end loop working: ~1 week

### Prerequisites

- S2 (tool swap) complete — richer attack surface, more HELD verdicts to train on
- S3 (RAG poisoning) complete — indirect injection gives harder targets worth training against
- At least 500 rollouts collected — minimum for meaningful GRPO signal

---

## Why v2 matters (the product angle)

The S5 harness product gap vs garak/PyRIT is runtime authorization probing.
A trained attacker closes a second gap: **adaptive red teaming**.

Static payload libraries go stale as models improve. A trained attacker retrains against the current model. That's the defensible moat.
