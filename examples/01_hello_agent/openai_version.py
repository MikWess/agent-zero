"""
01_hello_agent — OpenAI version

Same as the Anthropic version: one system prompt, one user message, one response.
Compare this side-by-side with anthropic_version.py to see the API differences.

Input:  a hardcoded question
Output: the model's response printed to stdout
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load OPENAI_API_KEY from .env file
load_dotenv()


def main():
    # Create the OpenAI client — reads OPENAI_API_KEY from env
    client = OpenAI()

    # Same question as the Anthropic version
    user_question = "What makes an AI agent different from a regular chatbot?"

    print(f"User: {user_question}")
    print("-" * 50)

    # OpenAI difference: system prompt goes IN the messages list as role="system"
    # (Anthropic has a separate system= param outside the messages list)
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast + cheap for learning
        max_tokens=256,
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant. Answer questions directly and briefly — one or two sentences max."
            },
            {
                "role": "user",
                "content": user_question
            }
        ]
    )

    # OpenAI difference: response is under choices[0].message.content
    # (Anthropic is response.content[0].text)
    answer = response.choices[0].message.content

    print(f"Agent: {answer}")
    print("-" * 50)
    print(f"Stop reason: {response.choices[0].finish_reason}")  # "stop" = finished normally
    print(f"Tokens used: {response.usage.prompt_tokens} in / {response.usage.completion_tokens} out")


if __name__ == "__main__":
    main()
