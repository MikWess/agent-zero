# agent-zero

**An agent is a loop that thinks, acts, and observes — until the job is done.**

This repo teaches agent fundamentals from scratch. You'll read short concept docs, then run working Python examples that use the real Anthropic and OpenAI APIs. No frameworks — just raw API calls so you can see exactly what's happening.

---

## What you'll learn

| Concept | Doc | Example |
|---|---|---|
| What an agent is vs a chatbot | `docs/01-what-is-an-agent.md` | `examples/01_hello_agent/` |
| The think → act → observe loop | `docs/02-the-loop.md` | `examples/03_loop_agent/` |
| Tools — what they are and how to define them | `docs/03-tools.md` | `examples/02_tool_agent/` |
| Memory — 4 types, when to use each | `docs/04-memory.md` | `examples/04_memory_agent/` |
| System prompts — persona, instructions, context | `docs/05-system-prompts.md` | `examples/01_hello_agent/` |
| Anthropic vs OpenAI API differences | `docs/06-apis.md` | all examples |
| OpenClaw anatomy — a real agent system | `docs/07-openclaw-anatomy.md` | `examples/05_daemon_agent/` |

---

## Setup

```bash
# 1. Clone and enter the repo
cd ~/agent-zero

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e .

# 4. Set your API keys
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY and OPENAI_API_KEY
```

---

## How to use this repo

**Read the docs first, then run the examples.**

The docs are in `docs/` numbered 01–07. Read them in order — each one builds on the last. They're short and practical. No walls of theory.

Then run the matching examples to see the concepts in action:

```bash
# Simplest possible agent
python examples/01_hello_agent/anthropic_version.py
python examples/01_hello_agent/openai_version.py

# Agent with a tool it can call
python examples/02_tool_agent/anthropic_version.py
python examples/02_tool_agent/openai_version.py

# Full think→act→observe loop with multiple tools
python examples/03_loop_agent/anthropic_version.py
python examples/03_loop_agent/openai_version.py

# Agent with persistent file-based memory
python examples/04_memory_agent/agent.py

# Scheduled daemon agent that runs on an interval
python examples/05_daemon_agent/agent.py
```

Each example folder has its own `README.md` explaining exactly what it does and what to look for in the output.

---

## Repo structure

```
agent-zero/
├── docs/                    # Concept docs — read these first
│   ├── 01-what-is-an-agent.md
│   ├── 02-the-loop.md
│   ├── 03-tools.md
│   ├── 04-memory.md
│   ├── 05-system-prompts.md
│   ├── 06-apis.md
│   └── 07-openclaw-anatomy.md
│
└── examples/                # Working Python examples — run these after reading
    ├── 01_hello_agent/      # One prompt, one response — the bare minimum
    ├── 02_tool_agent/       # Agent with one callable tool
    ├── 03_loop_agent/       # Full loop: think→act→observe until done
    ├── 04_memory_agent/     # Persistent memory via MEMORY.md pattern
    └── 05_daemon_agent/     # Scheduled agent that wakes up on a timer
```
