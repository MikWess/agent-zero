# Example 03 — Loop Agent

## Concept

This is the full agent loop: think → act → observe → repeat until done.

The agent has two tools and a multi-step task. You'll see each iteration printed as it runs — the model calling tools, getting results, calling more tools, then writing the final answer.

## Input → Output

```
Task: "Count the words in 'The quick brown fox jumps over the lazy dog'.
       Multiply that count by 3 and add 10. Give me both results."

[Iteration 1] Calling LLM...
  Stop reason: tool_use
  Called: get_word_count({"text": "The quick..."}) → 9

[Iteration 2] Calling LLM...
  Stop reason: tool_use
  Called: calculator({"expression": "9 * 3 + 10"}) → 37

[Iteration 3] Calling LLM...
  Stop reason: end_turn
[Done] Agent finished after 3 iteration(s)

Final answer:
The sentence has 9 words. 9 × 3 + 10 = 37.
```

## How to run

```bash
python examples/03_loop_agent/anthropic_version.py
python examples/03_loop_agent/openai_version.py
```

## What to look for

- **Multiple iterations** — the loop runs multiple times before finishing
- **Tool chaining** — output of one tool becomes input to the next (word count → calculator)
- **Max iterations** — the safety valve (set to 10 here) prevents infinite loops
- **`end_turn` / `stop`** — these are the signals that the agent is done

## The loop structure

```python
for iteration in range(1, max_iterations + 1):
    response = llm.call(messages)

    if response.is_done:
        return response.text     # ← exit the loop

    if response.wants_tools:
        results = run_all_tools(response.tool_calls)
        messages.extend(results)  # ← add results, loop again
```

## Related docs

- `docs/02-the-loop.md` — explains the think→act→observe cycle
- `docs/03-tools.md` — tool schemas and dispatching
