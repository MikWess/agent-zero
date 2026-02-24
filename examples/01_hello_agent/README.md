# Example 01 — Hello Agent

## Concept

This is the bare minimum: one prompt in, one response out. No tools, no loop.

It demonstrates:
- How to create an API client (Anthropic vs OpenAI)
- How the system prompt is passed (different between the two APIs)
- How to read the response text
- What the response object looks like

## Input → Output

```
Input:  "What makes an AI agent different from a regular chatbot?"

Output: (Claude or GPT answers in 1-2 sentences)
        Stop reason: end_turn / stop
        Tokens used: X in / Y out
```

## How to run

```bash
# Make sure you're in the repo root with your venv active
source .venv/bin/activate

python examples/01_hello_agent/anthropic_version.py
python examples/01_hello_agent/openai_version.py
```

## What to look for

- **Stop reason:** `end_turn` (Anthropic) or `stop` (OpenAI) means the model finished naturally
- **Token counts:** Notice how even a tiny question uses tokens for both input and output
- **API difference:** Anthropic uses `system=` as a separate param; OpenAI puts it in `messages` as `role: "system"`

## Key code pattern

```python
# Anthropic
response = client.messages.create(
    model="...",
    max_tokens=256,
    system="You are...",        # ← separate param
    messages=[{"role": "user", "content": "..."}]
)
text = response.content[0].text

# OpenAI
response = client.chat.completions.create(
    model="...",
    messages=[
        {"role": "system", "content": "You are..."},  # ← in messages
        {"role": "user", "content": "..."}
    ]
)
text = response.choices[0].message.content
```

## Related doc

`docs/06-apis.md` — full comparison of both APIs
