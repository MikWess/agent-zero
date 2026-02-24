"""
03_loop_agent — OpenAI version

Same multi-tool loop as the Anthropic version.
Compare side-by-side to see the structural differences.

Key differences:
- finish_reason is "tool_calls" instead of "tool_use"
- Tool calls are at choice.message.tool_calls (not response.content blocks)
- Arguments are JSON strings — must json.loads() them
- Tool results use role="tool" and tool_call_id=
- Assistant message appended as choice.message object (not a list of content blocks)
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ----- Tool functions (same as Anthropic version) -----

def calculator(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def get_word_count(text: str) -> str:
    count = len(text.split())
    return str(count)


TOOLS_MAP = {
    "calculator": calculator,
    "get_word_count": get_word_count,
}

# ----- Tool schemas (OpenAI format) -----

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression. Use for any arithmetic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression like '12 * 7'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_word_count",
            "description": "Count the number of words in a piece of text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to count words in"}
                },
                "required": ["text"]
            }
        }
    }
]


def run_agent(task: str, max_iterations: int = 10) -> str:
    """
    Run the think→act→observe loop using OpenAI.

    Takes:   a task string and optional iteration limit
    Returns: the agent's final response text
    """
    client = OpenAI()

    # System prompt goes in messages for OpenAI
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools. Use tools as needed."},
        {"role": "user", "content": task}
    ]

    print(f"Task: {task}")
    print("=" * 60)

    for iteration in range(1, max_iterations + 1):
        print(f"\n[Iteration {iteration}] Calling LLM...")

        # THINK
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=512,
            tools=TOOLS,
            messages=messages
        )

        choice = response.choices[0]
        print(f"  Finish reason: {choice.finish_reason}")

        # CHECK: did the model finish?
        if choice.finish_reason == "stop":
            print(f"\n[Done] Agent finished after {iteration} iteration(s)")
            return choice.message.content

        # ACT + OBSERVE: model wants to call tools
        if choice.finish_reason == "tool_calls":
            # Append the assistant message (which contains tool_calls)
            # OpenAI: append the whole message object, not content blocks
            messages.append(choice.message)

            # Process each tool call
            for call in choice.message.tool_calls:
                fn = TOOLS_MAP.get(call.function.name)

                # OpenAI: arguments are a JSON string — parse them
                args = json.loads(call.function.arguments)

                if fn is None:
                    result = f"Unknown tool: {call.function.name}"
                else:
                    result = fn(**args)

                print(f"  Called: {call.function.name}({args}) → {result}")

                # OpenAI: each tool result is its own message with role="tool"
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                })

    print(f"\n[Stopped] Hit max iterations ({max_iterations})")
    return "(agent hit max iterations without finishing)"


def main():
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
