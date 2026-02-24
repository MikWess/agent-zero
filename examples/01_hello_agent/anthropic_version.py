"""
01_hello_agent — Anthropic version

The simplest possible agent: one system prompt, one user message, one response.
No tools. No loop. Just the bare minimum to see an LLM call work.

Input:  a hardcoded question
Output: the model's response printed to stdout
"""

import os
from dotenv import load_dotenv
import anthropic

# Load ANTHROPIC_API_KEY from .env file
load_dotenv()


def main():
    # Create the Anthropic client — reads ANTHROPIC_API_KEY from env
    client = anthropic.Anthropic()

    # The system prompt sets who the agent is and how it behaves
    system_prompt = """You are a concise assistant.
Answer questions directly and briefly — one or two sentences max."""

    # The user's question — in a real agent this would come from user input
    user_question = "What makes an AI agent different from a regular chatbot?"

    print(f"User: {user_question}")
    print("-" * 50)

    # Make the API call
    # - model: which Claude to use
    # - max_tokens: required by Anthropic (unlike OpenAI which has a default)
    # - system: the system prompt (separate param, not in messages)
    # - messages: the conversation so far
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # fast + cheap for learning
        max_tokens=256,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_question}
        ]
    )

    # response.content is a list of blocks — for a simple text response
    # there's just one block with type "text"
    answer = response.content[0].text

    print(f"Agent: {answer}")
    print("-" * 50)
    print(f"Stop reason: {response.stop_reason}")  # "end_turn" = finished normally
    print(f"Tokens used: {response.usage.input_tokens} in / {response.usage.output_tokens} out")


if __name__ == "__main__":
    main()
