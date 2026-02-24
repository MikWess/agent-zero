"""
04_memory_agent — Agent with persistent file-based memory

The agent reads a MEMORY.md file at startup and injects it into the system prompt.
When it learns something important, it writes it back to the file.

This is the MEMORY.md pattern — the same one Claude Code uses for these notes.

Run this twice:
  1st run:  agent has no memory → answers from scratch, saves what it learned
  2nd run:  agent has memory → references what it saved from the first run

Input:  a task + memory file on disk
Output: agent response + updated memory file
"""

import os
from dotenv import load_dotenv
import anthropic
from memory import load_memory, append_memory

load_dotenv()

# The memory file lives next to this script
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "agent_memory.md")


# ----- Tool: save a memory -----
# The agent can call this tool to write something to long-term memory

SAVE_MEMORY_TOOL = {
    "name": "save_memory",
    "description": "Save an important fact or piece of information to long-term memory. Use this when you learn something the user wants remembered for future sessions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fact": {
                "type": "string",
                "description": "The fact or information to remember"
            }
        },
        "required": ["fact"]
    }
}


def run_agent(task: str) -> str:
    """
    Run the memory agent on a task.

    Takes:   a task string
    Returns: the agent's final response
    """
    client = anthropic.Anthropic()

    # Load whatever the agent has remembered from previous sessions
    existing_memory = load_memory(MEMORY_PATH)

    # Build the system prompt — inject memory if we have any
    if existing_memory:
        memory_section = f"""
Your long-term memory from previous sessions:
--- MEMORY START ---
{existing_memory}
--- MEMORY END ---

Use this memory to inform your responses.
"""
    else:
        memory_section = "\nYou have no long-term memory yet from previous sessions.\n"

    system_prompt = f"""You are a helpful personal assistant with persistent memory.

{memory_section}
When you learn something the user wants remembered for future conversations,
use the save_memory tool to store it.
"""

    print(f"Task: {task}")
    print(f"Memory file: {MEMORY_PATH}")
    print(f"Existing memory: {'yes (' + str(len(existing_memory)) + ' chars)' if existing_memory else 'none'}")
    print("=" * 60)

    messages = [{"role": "user", "content": task}]
    max_iterations = 5

    for iteration in range(1, max_iterations + 1):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            tools=[SAVE_MEMORY_TOOL],
            messages=messages
        )

        if response.stop_reason == "end_turn":
            # Extract and return the final text
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "(no response)"
            )
            return final_text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "save_memory":
                    fact = block.input["fact"]
                    append_memory(MEMORY_PATH, fact)
                    print(f"  [Memory saved]: {fact}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Saved to memory: {fact}"
                    })

            messages.append({"role": "user", "content": tool_results})

    return "(agent hit max iterations)"


def main():
    # First run: agent answers a personal question and saves what it learns.
    # Second run: agent has memory and can reference it.
    task = (
        "My name is Alex and I'm building a Python project called agent-zero. "
        "It's a learning repo for AI agent fundamentals. "
        "Please remember these details about me, then tell me what you now know about me."
    )

    result = run_agent(task)
    print(f"\nAgent response:\n{result}")
    print(f"\nMemory file updated: {MEMORY_PATH}")
    print("Run this script again to see the agent remember Alex and agent-zero!")


if __name__ == "__main__":
    main()
