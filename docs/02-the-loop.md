# 02 — The Loop

## The fundamental pattern

Every agent is built around the same loop:

```
                 ┌─────────────────────────────┐
                 │                             │
  goal ──► THINK ──► ACT ──► OBSERVE ──► THINK │
                 │                             │
                 └─────────────────────────────┘
                              │
                          (done?) ──► exit
```

1. **Think** — Send the current state (goal + conversation so far) to the LLM. Ask: "what should I do next?"
2. **Act** — If the LLM says "call a tool," call it. If it says "I'm done," exit.
3. **Observe** — Take the tool's result and add it back to the conversation.
4. **Repeat** — Send the updated conversation back to the LLM and think again.

---

## How it looks in code (pseudocode)

```python
messages = [{"role": "user", "content": goal}]

for _ in range(MAX_ITERATIONS):
    response = llm.call(messages)

    if response.is_done:
        print(response.text)
        break

    if response.wants_tool:
        tool_name = response.tool_name
        tool_args = response.tool_args

        # Execute the tool
        result = run_tool(tool_name, tool_args)

        # Add BOTH the tool call AND its result to the conversation
        messages.append(response.as_message())
        messages.append(tool_result_message(tool_name, result))

    # Loop again — LLM sees the result and decides what to do next
```

The conversation is the agent's working memory. Every action and its result gets appended to it, so the LLM always has full context of what it's tried and what happened.

---

## Termination: how does the agent stop?

Agents stop in one of three ways:

### 1. The LLM decides it's done
The model returns a plain text response instead of a tool call — that's the signal that it believes the task is complete. Your code checks: "is this a tool call or a final answer?"

### 2. A tool signals completion
Some agents use a special `finish` tool: `{"name": "finish", "result": "..."}`. When the LLM calls it, you exit the loop and return the result.

### 3. Max iterations (safety valve)
**Always add a max iterations cap.** Without it, a confused agent will loop forever (burning tokens and money). 10–20 iterations is usually enough for most tasks.

```python
MAX_ITERATIONS = 15  # safety valve — always include this

for i in range(MAX_ITERATIONS):
    ...

else:
    # The loop ran out of iterations without finishing
    print("Agent hit max iterations — bailing out")
```

---

## What's in the conversation at each step?

After 2 tool calls, the `messages` list looks like this:

```python
[
    {"role": "user",      "content": "What's 12 * 7, then add 5?"},
    {"role": "assistant", "content": [{"type": "tool_use", "name": "multiply", "input": {"a": 12, "b": 7}}]},
    {"role": "user",      "content": [{"type": "tool_result", "content": "84"}]},
    {"role": "assistant", "content": [{"type": "tool_use", "name": "add", "input": {"a": 84, "b": 5}}]},
    {"role": "user",      "content": [{"type": "tool_result", "content": "89"}]},
    # Now the LLM sees everything and gives the final answer
]
```

The model sees the full history and reasons over it. This is why the conversation IS the agent's short-term memory.

---

## Next

Read `03-tools.md` to understand what tools are and how to define them so the LLM can call them.
