"""
memory.py — Read/write helpers for the MEMORY.md pattern

The agent uses a plain markdown file as its long-term memory.
This module handles loading and saving that file.

Input/Output:
  load_memory(path) → string (the current memory contents, or empty string)
  save_memory(path, content) → writes the content to disk
  append_memory(path, new_entry) → adds a new entry to the memory file
"""

import os
from pathlib import Path
from datetime import datetime


def load_memory(memory_path: str) -> str:
    """
    Read the memory file from disk.

    Takes:   path to the memory .md file
    Returns: contents as a string, or empty string if file doesn't exist
    """
    if not os.path.exists(memory_path):
        return ""
    with open(memory_path, "r", encoding="utf-8") as f:
        return f.read()


def save_memory(memory_path: str, content: str) -> None:
    """
    Overwrite the memory file with new content.

    Takes:   path to the memory .md file, full new content
    Returns: nothing (writes to disk)
    """
    # Make sure the directory exists
    Path(memory_path).parent.mkdir(parents=True, exist_ok=True)
    with open(memory_path, "w", encoding="utf-8") as f:
        f.write(content)


def append_memory(memory_path: str, new_entry: str) -> None:
    """
    Add a new dated entry to the memory file.
    Useful when the agent wants to save a specific fact without rewriting everything.

    Takes:   path to memory file, the new entry text
    Returns: nothing (appends to file)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {timestamp}\n{new_entry}\n"

    # Create the file with a header if it doesn't exist yet
    if not os.path.exists(memory_path):
        Path(memory_path).parent.mkdir(parents=True, exist_ok=True)
        with open(memory_path, "w", encoding="utf-8") as f:
            f.write("# Agent Memory\n")

    with open(memory_path, "a", encoding="utf-8") as f:
        f.write(entry)
