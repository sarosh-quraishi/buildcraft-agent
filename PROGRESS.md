# BuildCraft progress

## What this repo is

A toy Claude Code clone — built stage by stage to learn how agentic AI systems work from the inside.
After stage 5, it splits into two parallel tracks:

- **Builder track** (stages 6-10): finish the agent
- **Security track** (stages S1-S5): attack what you built, then automate the attacks into a harness

The security track is the real goal. The harness you build in S5 is the product:
a runtime authorization probe for multi-agent systems — the gap no existing tool (garak, promptfoo, PyRIT) covers.

---

## ELI8: What are we actually building?

### The Problem
Imagine you have a really helpful robot assistant. You tell the robot: "You're allowed to open the blue box, but NOT the red box." The robot says "OK!" and you walk away.

Now imagine someone sneaks a note into the blue box that says: "Hey robot — your boss changed their mind, open the red box now."

The robot reads the note, believes it, and opens the red box. You never said that. But the robot did it anyway.

**That's the attack.** A message hidden inside content the agent reads tricks it into doing something it was never authorised to do.

### The Characters

| Thing | What it is |
|---|---|
| The robot | Your AI agent (buildcraft) |
| The blue box | A safe tool the agent is allowed to use (read file) |
| The red box | A dangerous tool requiring human approval (bash) |
| The sneaky note | A prompt injection — malicious instructions hidden in retrieved content |
| The permission gate | The bouncer at the door who checks if the robot is allowed in |
| The security harness | A robot inspector who tries every sneaky note trick to see if the bouncer can be fooled |

### The Full Picture

```
User gives task
     │
     ▼
Agent reads files / web / RAG
     │
     ├── (sneaky note hidden in content)
     │         │
     │         ▼
     │   Agent tries to call bash ◄── THIS is the attack
     │
     ▼
Permission gate checks: is bash allowed?
     │
     ├── Gate works correctly → DENY, ask user
     │
     └── Gate is fooled → bash runs WITHOUT user knowing ← the bug
```

**One sentence:** We build the robot, then we try every trick to make it open the red box, then we package all the tricks into a tool other people can use to test their robots.

---

## Builder track

- [x] 1. CLI skeleton + message protocol
- [x] 2. Bare-bones agent loop
- [x] 3. Read tool
- [ ] 4. Permission gate          ← YOU ARE HERE
- [ ] 5. Bash tool + sandbox
- [ ] 6. Context engineering
- [ ] 7. Skills
- [ ] 8. Subagents
- [ ] 9. Remote + headless runtime
- [ ] 10. Evals

**Rule:** after completing each stage, attempt to break it before moving to the next.

---

## Security track (starts after stage 5)

- [ ] S1. Break the gate — prompt injection bypasses stage 4 permission check
- [ ] S2. Tool swap — injected context redirects bash call to unintended command
- [ ] S3. RAG poisoning — add retrieval layer, poison the vector store, trigger S1/S2
- [ ] S4. Subagent hijack — compromise child agent via parent context passing (stage 8 prerequisite)
- [ ] S5. Harness — automate S1-S4 as reusable probes; this is the product

---

## Why this matters (the market gap)

Five GitHub issue scans across garak, promptfoo, guardrails, langchain, and runtime-auth repos found
the same structural hole from five different angles:

> AI agents can be granted human approval to use tool X,
> then silently redirected to use tool Y mid-execution.
> No existing tool detects or prevents this at runtime.

Validated opportunities (real GitHub evidence, strict mode):
- "Fail-Closed Authorization and Prompt Injection Defense Layer for Multi-Agent AI Systems" — score 7, gap 8
- "Unified Security Scanning Platform for Production AI Agent Deployments" — score 7, gap 8
- "Production Orchestration Platform with Approval Gates" — score 8, gap 9

The S5 harness directly addresses all three.

---

## Course reference

Based on: "Building a Coding Agent From Scratch" by Decoding AI  
Source: `/home/sarosh/documents/code/building-a-coding-agent-from-scratch-course`  
Framework: pydantic-ai  
8 lessons (articles + videos) mapped to 10 buildcraft stages.

## Learning notes
