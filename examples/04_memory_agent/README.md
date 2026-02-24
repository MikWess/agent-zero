# Example 04 — Memory Agent

## Concept

Agents don't remember anything between sessions by default. This example implements the **external memory pattern**: the agent reads a file at startup, and writes to it when it learns something worth keeping.

This is exactly how Claude Code's `MEMORY.md` works.

## Input → Output

**First run** (no memory yet):
```
Task: "My name is Alex and I'm building agent-zero..."
Memory file: examples/04_memory_agent/agent_memory.md
Existing memory: none

[Memory saved]: User's name is Alex
[Memory saved]: Alex is building agent-zero, a Python learning repo for AI agents

Agent response:
"Nice to meet you, Alex! I've saved your details. You're building
agent-zero — a learning repo for AI agent fundamentals in Python."
```

**Second run** (memory exists):
```
Memory file: examples/04_memory_agent/agent_memory.md
Existing memory: yes (150 chars)

Agent response:
"Welcome back, Alex! I remember you're working on agent-zero —
your Python learning repo for AI agent fundamentals."
```

## How to run

```bash
# Run twice to see memory in action
python examples/04_memory_agent/agent.py
python examples/04_memory_agent/agent.py

# Inspect the memory file
cat examples/04_memory_agent/agent_memory.md

# Reset memory to start fresh
rm examples/04_memory_agent/agent_memory.md
```

## The memory pattern

```
Session start:
  1. Load MEMORY.md → inject into system prompt
  2. Agent has context from all previous sessions

During session:
  3. Agent decides what's worth saving
  4. Calls save_memory(fact="...") tool
  5. Your code writes it to MEMORY.md

Next session:
  6. Go to step 1 — that memory is now part of context
```

## Files

| File | What it does |
|---|---|
| `memory.py` | Load/save/append helpers for the memory file |
| `agent.py` | The agent — loads memory, runs task, saves new learnings |
| `agent_memory.md` | Created on first run — this is the memory file (safe to delete) |

## Related docs

- `docs/04-memory.md` — all 4 memory types and when to use each
- `docs/05-system-prompts.md` — how context injection works
