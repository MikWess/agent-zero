# 03 — Tools

## What is a tool?

A tool is a function your Python code defines that the LLM is allowed to call.

The LLM doesn't *run* the tool — it just outputs a structured request saying "I want to call this tool with these arguments." Your code reads that request, runs the actual function, and gives the result back to the LLM.

```
LLM:  "I need to know the weather. Call get_weather(city='Denver')"
        ↓
Your code: actually calls get_weather("Denver") → "72°F, sunny"
        ↓
LLM:  receives "72°F, sunny" and continues reasoning
```

The model never touches the real world directly. **You** do. The model just tells you what it wants.

---

## Tool schema

To give a tool to a model, you define a schema — a description of what the tool does and what arguments it takes. The schema is written in JSON Schema.

### Anthropic format

```python
{
    "name": "get_weather",
    "description": "Get the current weather for a city. Returns temperature and conditions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name, e.g. 'Denver' or 'New York'"
            }
        },
        "required": ["city"]
    }
}
```

### OpenAI format

```python
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Returns temperature and conditions.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'Denver' or 'New York'"
                }
            },
            "required": ["city"]
        }
    }
}
```

The difference: Anthropic uses `input_schema` at the top level. OpenAI wraps everything inside `"function": {}` and calls the parameters key `parameters` instead of `input_schema`.

---

## How the model "decides" to call a tool

The model doesn't really "decide" — it generates tokens. But it was trained to output a structured tool-call block when the description of a tool matches what it needs.

**This is why descriptions matter.** If your description says "look up the current temperature," the model will use the tool when it needs temperature. If the description is vague or wrong, the model will either use the wrong tool or not use it at all.

Good tool description: "Multiply two numbers and return their product."
Bad tool description: "Does math stuff."

---

## How your code handles a tool call

When the LLM responds with a tool call, you:

1. Read the tool name and arguments from the response
2. Look up the matching Python function
3. Call it with the arguments
4. Package the result as a `tool_result` message
5. Append it to the conversation and loop

```python
# Anthropic example
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            fn = tools_map[block.name]       # look up the function
            result = fn(**block.input)        # call it
            # Add the result to messages and loop again
```

---

## Side-by-side: Anthropic vs OpenAI tool calling

| | Anthropic | OpenAI |
|---|---|---|
| Schema key | `input_schema` | `parameters` (inside `function`) |
| Wrapper | none — tool is a flat dict | `{"type": "function", "function": {...}}` |
| Stop signal | `stop_reason == "tool_use"` | `finish_reason == "tool_calls"` |
| Tool call in response | `block.type == "tool_use"` | `choice.message.tool_calls[i]` |
| Arguments | `block.input` (dict) | `json.loads(call.function.arguments)` (string → parse) |
| Result message role | `"user"` with `tool_result` block | `"tool"` role with `tool_call_id` |

OpenAI returns arguments as a JSON *string* that you have to parse. Anthropic returns them as a dict directly.

---

## Next

Read `04-memory.md` to understand how agents remember things — within a session and across sessions.
