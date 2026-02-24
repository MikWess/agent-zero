# 06 — The APIs

## Two APIs, same idea

Both Anthropic and OpenAI provide HTTP APIs that take a conversation (list of messages) and return the model's next response. The concepts are identical. The format differs.

---

## Anthropic Messages API

### Basic call (no tools)

```python
import anthropic

client = anthropic.Anthropic(api_key="...")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",   # separate param, not in messages list
    messages=[
        {"role": "user", "content": "What is 2 + 2?"}
    ]
)

print(response.content[0].text)   # "4"
print(response.stop_reason)       # "end_turn" = normal finish
```

### Call with tools

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a math assistant.",
    tools=[
        {
            "name": "add",
            "description": "Add two numbers.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    ],
    messages=[{"role": "user", "content": "What is 12 + 7?"}]
)

# Check if the model wants to call a tool
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            print(block.name)    # "add"
            print(block.input)   # {"a": 12, "b": 7}  ← already a dict
            print(block.id)      # "toolu_..." ← need this to return the result
```

### Returning a tool result to Anthropic

```python
# After running the tool, add both the assistant's tool_use AND your result
messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": block.id,   # must match the tool_use id above
            "content": "19"            # the result as a string
        }
    ]
})
```

---

## OpenAI Chat Completions API

### Basic call (no tools)

```python
from openai import OpenAI

client = OpenAI(api_key="...")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},  # in the list
        {"role": "user", "content": "What is 2 + 2?"}
    ]
)

print(response.choices[0].message.content)  # "4"
print(response.choices[0].finish_reason)    # "stop" = normal finish
```

### Call with tools

```python
response = client.chat.completions.create(
    model="gpt-4o",
    tools=[
        {
            "type": "function",       # ← required wrapper
            "function": {
                "name": "add",
                "description": "Add two numbers.",
                "parameters": {       # ← called "parameters" not "input_schema"
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            }
        }
    ],
    messages=[
        {"role": "system", "content": "You are a math assistant."},
        {"role": "user", "content": "What is 12 + 7?"}
    ]
)

# Check if the model wants to call a tool
if response.choices[0].finish_reason == "tool_calls":
    for call in response.choices[0].message.tool_calls:
        print(call.function.name)                          # "add"
        print(json.loads(call.function.arguments))         # ← string, must parse
        print(call.id)                                     # "call_..." ← need this
```

### Returning a tool result to OpenAI

```python
import json

# Append the assistant message (includes the tool_calls)
messages.append(response.choices[0].message)

# Then append the tool result — role is "tool" not "user"
messages.append({
    "role": "tool",                  # ← different from Anthropic
    "tool_call_id": call.id,         # must match call.id above
    "content": "19"
})
```

---

## Side-by-side comparison

| | Anthropic | OpenAI |
|---|---|---|
| Client | `anthropic.Anthropic()` | `openai.OpenAI()` |
| System prompt | `system=` param | `{"role": "system"}` in messages |
| Model param | `model=` | `model=` |
| Token limit | `max_tokens=` | `max_tokens=` |
| Tool schema key | `input_schema` | `parameters` (inside `function`) |
| Tool wrapper | none | `{"type": "function", "function": {}}` |
| Stop signal | `stop_reason == "tool_use"` | `finish_reason == "tool_calls"` |
| Tool call location | `response.content` (list of blocks) | `response.choices[0].message.tool_calls` |
| Arguments type | dict (already parsed) | string (must `json.loads()`) |
| Tool call ID | `block.id` | `call.id` |
| Result role | `"user"` with `tool_result` content block | `"tool"` role |
| Result ID key | `tool_use_id` | `tool_call_id` |

---

## Common gotchas

**Anthropic: always set `max_tokens`** — it's required. OpenAI has a default, Anthropic doesn't.

**OpenAI: parse the arguments** — `call.function.arguments` is a JSON string. Always `json.loads()` it before using.

**Anthropic: tool results go in a "user" message** — the role is `"user"`, not `"tool"`. This trips people up.

**Both: the tool call ID must match** — when you return a result, the ID must match the ID that came in the tool call. If it doesn't match, the API will error.

---

## Next

Read `07-openclaw-anatomy.md` to see how a complete, production-level personal agent system is structured.
