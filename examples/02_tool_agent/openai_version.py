"""
02_tool_agent — OpenAI version

Same as the Anthropic version — agent with a calculator tool.
Compare side-by-side to see the key differences in how tool calls work.

Key differences from Anthropic:
- Tool schema uses "parameters" not "input_schema", wrapped in {"type": "function", ...}
- finish_reason is "tool_calls" not "tool_use"
- Tool calls are in message.tool_calls, not response.content blocks
- Arguments come back as a JSON STRING — you must json.loads() them
- Tool result uses role="tool" and tool_call_id= (not "user" + tool_use_id)
"""

import json
import os
from dotenv import load_dotenv
from agent_zero.calculator import calculator
from openai import OpenAI

load_dotenv()


# ----- The actual tool function (same as Anthropic version) -----



# ----- Tool schema (OpenAI format) -----
# Notice: wrapped in {"type": "function", "function": {...}}
# and uses "parameters" instead of "input_schema"
CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression and return the numeric result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A valid math expression, e.g. '12 * 7'"
                }
            },
            "required": ["expression"]
        }
    }
}


def main():
    client = OpenAI()

    user_question = "What is (144 / 12) + (7 * 8)?"

    print(f"User: {user_question}")
    print("=" * 50)

    # OpenAI: system prompt goes in messages, not as a separate param
    messages = [
        {"role": "system", "content": "You are a math assistant. Use the calculator tool for all arithmetic."},
        {"role": "user", "content": user_question}
    ]

    # Step 1: Call the LLM with the tool available
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=256,
        tools=[CALCULATOR_TOOL],
        messages=messages
    )

    choice = response.choices[0]
    print(f"LLM finish reason: {choice.finish_reason}")

    # Step 2: Handle the tool call
    if choice.finish_reason == "tool_calls":
        for call in choice.message.tool_calls:
            print(f"\nLLM wants to call: {call.function.name}")

            # OpenAI returns arguments as a JSON STRING — must parse it
            args = json.loads(call.function.arguments)
            print(f"Arguments: {args}")

            # Run the actual tool
            result = calculator(**args)
            print(f"Tool result: {result}")

            # Add the assistant message (contains the tool_calls)
            messages.append(choice.message)

            # Add the tool result — role is "tool" (not "user" like Anthropic)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,  # must match call.id
                "content": result
            })

        # Step 3: Call the LLM again to get the final answer
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=256,
            tools=[CALCULATOR_TOOL],
            messages=messages
        )

        print(f"\nAgent: {final_response.choices[0].message.content}")

    elif choice.finish_reason == "stop":
        print(f"\nAgent: {choice.message.content}")


if __name__ == "__main__":
    main()
