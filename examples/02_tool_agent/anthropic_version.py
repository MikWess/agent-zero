"""
02_tool_agent — Anthropic version

An agent with one tool it can call: a calculator.
The model doesn't do the math itself — it calls our tool, and we do the math.

Input:  a math question
Output: the model's answer (backed by the actual tool result)

Flow:
  user asks math question
    → LLM says "call calculator(expression='...')"
    → we evaluate the expression
    → we give result back to LLM
    → LLM writes a final answer
"""

import os
from dotenv import load_dotenv
from agent_zero.calculator import calculator
import anthropic

load_dotenv()


# ----- The actual tool function -----
# This is what our code runs when the model "calls" the calculator tool.



# ----- Tool schema -----
# This is what we give to the LLM so it knows the tool exists and how to call it.
CALCULATOR_TOOL = {
    "name": "calculator",
    "description": "Evaluate a mathematical expression and return the numeric result. Use this for any arithmetic.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A valid math expression, e.g. '12 * 7' or '(100 + 50) / 3'"
            }
        },
        "required": ["expression"]
    }
}


def main():
    client = anthropic.Anthropic()

    user_question = "What is (144 / 12) + (7 * 8)?"

    print(f"User: {user_question}")
    print("=" * 50)

    # Build the initial message list
    messages = [{"role": "user", "content": user_question}]

    # Step 1: Call the LLM with the tool available
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system="You are a math assistant. Use the calculator tool for all arithmetic.",
        tools=[CALCULATOR_TOOL],  # give the model the tool schema
        messages=messages
    )

    print(f"LLM stop reason: {response.stop_reason}")

    # Step 2: Handle the tool call
    if response.stop_reason == "tool_use":
        # Find the tool_use block in the response content
        for block in response.content:
            if block.type == "tool_use":
                print(f"\nLLM wants to call: {block.name}({block.input})")

                # Run the actual tool
                result = calculator(**block.input)
                print(f"Tool result: {result}")

                # Add the assistant's response (with tool call) to messages
                messages.append({"role": "assistant", "content": response.content})

                # Add the tool result as a user message (this is Anthropic's format)
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,  # must match the block.id above
                            "content": result
                        }
                    ]
                })

        # Step 3: Call the LLM again — it now sees the tool result and writes the answer
        final_response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system="You are a math assistant. Use the calculator tool for all arithmetic.",
            tools=[CALCULATOR_TOOL],
            messages=messages
        )

        print(f"\nAgent: {final_response.content[0].text}")

    elif response.stop_reason == "end_turn":
        # Model answered without using a tool (shouldn't happen here, but handle it)
        print(f"\nAgent: {response.content[0].text}")


if __name__ == "__main__":
    main()
