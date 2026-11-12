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
