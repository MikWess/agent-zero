# agent-zero

Learn how an AI agent calls tools, repeats a task, and remembers information using small Python examples. Each step is visible; there is no agent framework to learn first.

## Three useful things to try

1. **Understand tool calling before building your own assistant.** Run example 02, then compare the Anthropic and OpenAI versions. Both ask the model to use a calculator; the printed tool call shows where the model stops and your code takes over.
2. **Prototype a small multi-step workflow.** Run example 03 and change its `task` string to combine arithmetic and word counting. Watch the loop execute tools and stop at the iteration limit. These are the only supplied tools; web browsing and file access are not built in.
3. **Learn persistent memory and scheduled work.** Run example 04 twice to see a saved fact survive between processes. Then run example 05 for four scheduled reports on **simulated** CPU/memory readings. Replace the data source yourself before treating it as monitoring.

## Run your first example

Requires Python 3.9+ and an API key for the provider you choose. API calls may incur charges; the local helper tests below require no keys.

```sh
git clone https://github.com/MikWess/agent-zero.git
cd agent-zero
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
cp .env.example .env
```

Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`, then run one:

```sh
python examples/01_hello_agent/anthropic_version.py
python examples/01_hello_agent/openai_version.py
```

Only the selected provider needs a key. Examples 04 and 05 use Anthropic. The model names live in each script; choose an available model there if your account rejects the default.

## Learning path

| Step | Read | Run |
| --- | --- | --- |
| 1: One request | [What is an agent?](docs/01-what-is-an-agent.md) | `python examples/01_hello_agent/anthropic_version.py` |
| 2: A calculator tool | [Tools](docs/03-tools.md) | `python examples/02_tool_agent/anthropic_version.py` |
| 3: Repeated tool calls | [The loop](docs/02-the-loop.md) | `python examples/03_loop_agent/anthropic_version.py` |
| 4: Memory on disk | [Memory](docs/04-memory.md) | `python examples/04_memory_agent/agent.py` |
| 5: Scheduled runs | [Daemon example](examples/05_daemon_agent/README.md) | `python examples/05_daemon_agent/agent.py` |

Steps 01–03 also have `openai_version.py`. See [system prompts](docs/05-system-prompts.md) and [API differences](docs/06-apis.md) for the underlying concepts.

## Data and limits

Memory is plain UTF-8 Markdown beside the example script (`agent_memory.md` or `daemon_memory.md`). It is ignored by Git. Read or delete those generated files to inspect or reset memory. Prompts and remembered facts are sent to the selected model provider when an example runs.

The calculator accepts numbers, parentheses, `+`, `-`, `*`, `/`, `//`, and `%`. It rejects Python calls, attribute access, exponentiation, oversized expressions, and out-of-range values. The examples are learning programs, not hardened multi-user services. Scheduled reports use random data, and iteration limits can stop an agent before it finishes.

## Check changes without calling a model

```sh
python -m unittest discover -s tests -v
python -m compileall -q agent_zero examples
```

If `agent_zero` cannot be imported, activate the virtual environment and rerun `python -m pip install -e .` from this repository's root.
