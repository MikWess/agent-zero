"""
05_daemon_agent — Scheduled daemon agent

An agent that wakes up on a schedule, does a job, and goes back to sleep.

This example simulates a monitoring agent:
  - Every 10 seconds, it "checks system health" (simulated data)
  - Reports what it finds
  - Remembers what it saw in previous runs (using the memory pattern)

In production this would run as a cron job, a systemd service, or a Docker container.
OpenClaw is exactly this: a long-running daemon that processes incoming messages.

Input:  simulated system metrics (CPU, memory usage)
Output: agent commentary printed to stdout each tick
"""

import os
import random
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from scheduler import run_on_interval

# Import the memory helpers from example 04
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "04_memory_agent"))
from memory import load_memory, append_memory

load_dotenv()

MEMORY_PATH = os.path.join(os.path.dirname(__file__), "daemon_memory.md")

# ----- Simulated data source -----
# In a real agent this would be actual metrics: psutil, an API, a database query, etc.

def get_system_metrics() -> dict:
    """
    Simulate system health metrics.

    Takes:   nothing
    Returns: dict with cpu_percent and memory_percent
    """
    return {
        "cpu_percent": round(random.uniform(10, 95), 1),
        "memory_percent": round(random.uniform(20, 85), 1),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ----- The agent tick -----
# This runs once per schedule interval.

def agent_tick() -> None:
    """
    One cycle of the daemon agent:
    1. Read current metrics
    2. Load memory (what did we see before?)
    3. Ask the LLM to interpret and comment
    4. Save notable observations to memory
    """
    client = anthropic.Anthropic()

    # Get current data
    metrics = get_system_metrics()
    print(f"Metrics: CPU {metrics['cpu_percent']}% | Memory {metrics['memory_percent']}%")

    # Load memory to give the agent context about past runs
    memory = load_memory(MEMORY_PATH)
    memory_section = f"\nPrevious observations:\n{memory}\n" if memory else "\nNo previous observations yet.\n"

    system_prompt = f"""You are a system monitoring agent.
Your job: look at the current metrics, compare to history, and give a brief status report.
Be concise — 2-3 sentences max.
If something looks concerning (CPU > 80% or memory > 75%), flag it.
{memory_section}"""

    user_message = (
        f"Current metrics at {metrics['timestamp']}:\n"
        f"  CPU: {metrics['cpu_percent']}%\n"
        f"  Memory: {metrics['memory_percent']}%\n\n"
        "What's your status report?"
    )

    # Tools: agent can save observations for future runs
    save_tool = {
        "name": "save_observation",
        "description": "Save a notable observation to memory for future reference.",
        "input_schema": {
            "type": "object",
            "properties": {
                "observation": {"type": "string", "description": "What to remember"}
            },
            "required": ["observation"]
        }
    }

    messages = [{"role": "user", "content": user_message}]

    # Run the agent (simple loop — at most 3 iterations for a daemon tick)
    for _ in range(3):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system=system_prompt,
            tools=[save_tool],
            messages=messages
        )

        if response.stop_reason == "end_turn":
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "(no response)"
            )
            print(f"Agent: {final_text}")
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "save_observation":
                    obs = block.input["observation"]
                    append_memory(MEMORY_PATH, obs)
                    print(f"  [Saved]: {obs}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "Observation saved."
                    })
            messages.append({"role": "user", "content": tool_results})


def main():
    print("Starting daemon agent — monitors simulated system metrics")
    print("Uses the memory pattern to track observations across runs")
    print("Press Ctrl+C to stop\n")

    # Run the agent tick every 10 seconds, max 4 runs (so it doesn't run forever in demo)
    run_on_interval(
        fn=agent_tick,
        interval_seconds=10,
        max_runs=4,
    )


if __name__ == "__main__":
    main()
