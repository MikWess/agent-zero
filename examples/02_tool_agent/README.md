# Example 02 — Tool Agent

## Concept

The model doesn't actually execute tools — it *requests* them. Your code does the work.

This example shows the full tool call cycle:
1. LLM receives a question + a tool schema
2. LLM says "I want to call tool X with args Y"
3. Your code runs the tool
4. You send the result back to the LLM
5. LLM writes the final answer

## Input → Output

```
Input:  "What is (144 / 12) + (7 * 8)?"

--- behind the scenes ---
LLM wants to call: calculator({"expression": "(144 / 12) + (7 * 8)"})
Tool result: 68

Output: "The result is 68."
```

## How to run

```bash
python examples/02_tool_agent/anthropic_version.py
python examples/02_tool_agent/openai_version.py
```

## What to look for

- The model doesn't do the math — it generates a *request* to call the calculator
- The stop reason changes: `tool_use` / `tool_calls` instead of `end_turn` / `stop`
- There are **two** LLM calls: one to get the tool request, one to get the final answer
- The `block.id` / `call.id` must be included when you return the result

## Key difference: returning the result

```python
# Anthropic: tool result goes as a "user" message with a tool_result block
messages.append({
    "role": "user",
    "content": [{"type": "tool_result", "tool_use_id": block.id, "content": result}]
})

# OpenAI: tool result gets its own "tool" role message
messages.append({
    "role": "tool",
    "tool_call_id": call.id,
    "content": result
})
```

## Key difference: reading the arguments

```python
# Anthropic: already a dict
args = block.input  # {"expression": "(144 / 12) + (7 * 8)"}

# OpenAI: a JSON string — must parse it
args = json.loads(call.function.arguments)  # parse first!
```

## Related doc

`docs/03-tools.md` — tool schemas and the full tool call cycle
