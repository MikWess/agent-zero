# 04 — Memory

## The problem

LLMs don't remember anything between calls. Every time you send a request, you start fresh. The model has no idea what you said yesterday, last hour, or even 5 minutes ago — unless you include it in the current request.

This creates a challenge: how do you give an agent memory?

---

## The 4 types of memory

### 1. In-context memory (short-term)
**What it is:** The conversation history you send with every request.

**How it works:** You maintain a `messages` list. Every user message, assistant response, tool call, and tool result gets appended. On each LLM call, you send the whole list. The model "remembers" because you're giving it the full transcript.

**Limit:** Context windows are finite. GPT-4 has 128k tokens. Claude has 200k. A long conversation eventually won't fit.

**Use when:** You want the agent to remember everything within a single session.

```python
# Everything the agent has done this session
messages = [
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "Paris."},
    {"role": "user", "content": "What's the population there?"},
    # model sees all of the above when answering this
]
```

---

### 2. External memory (long-term)
**What it is:** Files, databases, or key-value stores that exist outside the model.

**How it works:** The agent writes important things to a file (or DB) and reads from it at the start of each session. You inject the relevant parts into the system prompt or early messages.

**This is the MEMORY.md pattern** — exactly what Claude Code uses for these notes.

**Use when:** You need memory that survives between sessions.

```python
# At session start: load memory into context
memory = open("MEMORY.md").read()
messages = [{"role": "user", "content": f"Your memory:\n{memory}\n\nNow: {task}"}]

# During session: agent writes new learnings back to the file
```

---

### 3. Semantic memory (weights)
**What it is:** Knowledge baked into the model during training.

**How it works:** You don't do anything — it's already there. When you ask Claude "what's the capital of France?" it knows because it was trained on that data. You can't update this without retraining or fine-tuning.

**Use when:** General world knowledge. You rely on this all the time without thinking about it.

---

### 4. Episodic memory (RAG)
**What it is:** A searchable store of past experiences or documents. Retrieve only what's relevant.

**How it works:** Embed your documents/memories as vectors. At query time, embed the current question and find the closest matches. Inject those matches into context.

**Use when:** You have a large knowledge base that won't fit in context. Instead of loading everything, load only what's relevant to the current task. (Think: customer support bot that searches your docs.)

---

## The context window problem

Your context window is like a whiteboard — finite space. Once it fills up, you have to make choices:

| Strategy | How it works | Tradeoff |
|---|---|---|
| **Sliding window** | Only keep the last N messages | Forgets early context |
| **Summarization** | Summarize old messages into one | Lossy — details lost |
| **Write-on-important** | Agent writes key facts to a file | Requires good judgment |
| **RAG** | Only load relevant memories | Needs embedding infra |

For simple personal agents, **summarization + external file** is usually enough. That's what most real agents use.

---

## The MEMORY.md pattern in practice

Claude Code (the tool you're using right now) uses external memory exactly like this:

1. Reads `MEMORY.md` at the start of every session → injected into system prompt
2. Writes new learnings to `MEMORY.md` when something important is discovered
3. Each project gets its own section — old projects don't bloat new sessions

This is the simplest effective memory system for a personal agent. No vector DB required.

---

## Next

Read `05-system-prompts.md` to understand how to shape agent behavior through the system prompt.
