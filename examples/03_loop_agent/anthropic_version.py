"""
03_loop_agent — Anthropic version

Full think→act→observe loop with multiple tools.
The agent runs until it decides it's done (or hits max iterations).

Tools available:
  - calculator(expression)  → evaluates math
  - get_word_count(text)    → counts words in a string

The agent is given a multi-step task that requires using both tools.

Input:  a task that requires multiple tool calls
Output: visible loop steps + final answer
"""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

# ----- Tool functions -----

def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def get_word_count(text: str) -> str:
    """Count the number of words in a string."""
    count = len(text.split())
    return str(count)


# Map tool names to functions — used when dispatching tool calls
TOOLS_MAP = {
    "calculator": calculator,
    "get_word_count": get_word_count,
}

# ----- Tool schemas -----

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a mathematical expression. Use for any arithmetic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression like '12 * 7'"}
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_word_count",
        "description": "Count the number of words in a piece of text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to count words in"}
            },
            "required": ["text"]
        }
    }
]


def run_agent(task: str, max_iterations: int = 10) -> str:
    """
    Run the think→act→observe loop until the agent finishes or hits max_iterations.

    Takes:   a task string and optional iteration limit
    Returns: the agent's final response text
    """
    client = anthropic.Anthropic()

    # Start with just the user's task
    messages = [{"role": "user", "content": task}]

    print(f"Task: {task}")
    print("=" * 60)

    for iteration in range(1, max_iterations + 1):
        print(f"\n[Iteration {iteration}] Calling LLM...")

        # THINK: ask the model what to do next
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system="You are a helpful assistant with access to tools. Use tools as needed to complete the task.",
            tools=TOOLS,
            messages=messages
        )

        print(f"  Stop reason: {response.stop_reason}")

        # CHECK: did the model finish?
        if response.stop_reason == "end_turn":
            # Model gave a final answer — extract and return the text
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "(no text response)"
            )
            print(f"\n[Done] Agent finished after {iteration} iteration(s)")
            return final_text

        # ACT + OBSERVE: model wants to call one or more tools
        if response.stop_reason == "tool_use":
            # Add the assistant's response (containing tool_use blocks) to messages
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call in this response
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    fn = TOOLS_MAP.get(block.name)
                    if fn is None:
                        result = f"Unknown tool: {block.name}"
                    else:
                        result = fn(**block.input)

                    print(f"  Called: {block.name}({block.input}) → {result}")

                    # Collect all tool results to send back together
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # OBSERVE: add all tool results back as a single user message
            messages.append({"role": "user", "content": tool_results})
            # Loop again — model sees results and decides what to do next

    # Safety valve: if we hit max iterations, return what we have
    print(f"\n[Stopped] Hit max iterations ({max_iterations})")
    return "(agent hit max iterations without finishing)"


def main():
    # A task that requires both tools and multiple steps
    task = (
        "I have a sentence: 'The quick brown fox jumps over the lazy dog'. "
        "First, tell me how many words are in it. "
        "Then multiply that word count by 3 and add 10. "
        "Give me both results."
    )

    result = run_agent(task)
    print(f"\nFinal answer:\n{result}")


if __name__ == "__main__":
    main()
