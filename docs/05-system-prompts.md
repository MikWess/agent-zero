# 05 — System Prompts

## What is a system prompt?

A system prompt is a special message you send before the conversation starts. It sets the rules, persona, and context for the entire session. The model treats it as authoritative — it shapes everything that follows.

```python
messages = [
    # This comes first and the model always "sees" it
    {"role": "system", "content": "You are a helpful coding assistant..."},

    # Then the actual conversation
    {"role": "user", "content": "How do I reverse a list in Python?"},
]
```

Note: Anthropic's API has a separate `system=` parameter instead of a system message in the list, but the effect is the same.

---

## The 3 layers of a good system prompt

### 1. Persona
Who the agent is. Sets the tone, style, and expertise.

```
You are a senior software engineer with expertise in Python and distributed systems.
You are direct, precise, and skip unnecessary pleasantries.
```

### 2. Instructions
What the agent should and shouldn't do. Rules for behavior.

```
Rules:
- Always explain your reasoning before giving an answer
- If you're unsure, say so instead of guessing
- When writing code, add comments explaining each section
- Prefer simple solutions over clever ones
```

### 3. Context injection
Relevant data the agent needs for this session. This is the power move.

```
Your current memory:
--- MEMORY START ---
Project: agent-zero at /Users/michaelwessman/agent-zero/
Stack: Python 3.9, anthropic, openai
Status: building examples
--- MEMORY END ---

Available tools:
- read_file(path): Read a file from disk
- write_file(path, content): Write content to a file
```

By injecting context, you turn a generic LLM into a specialized agent that knows your specific situation.

---

## Before and after: adding context injection

**Before** (generic LLM):
```
System: You are a helpful assistant.
User: What should I work on next?
```
→ The model has no idea what you're working on. Useless.

**After** (context-injected agent):
```
System: You are a productivity assistant.

Current projects:
- agent-zero: building example 03_loop_agent (in progress)
- chronicle: 57 tests passing, phase 2 complete
- luma-scout: 20 tests passing, needs deployment

Today's focus: agent-zero loop example

User: What should I work on next?
```
→ Now the model gives a real, specific answer.

---

## How OpenClaw does it

OpenClaw injects skill documentation directly into the system prompt at session start:

```
You are OpenClaw, a personal AI assistant connected to WhatsApp.

--- SKILL: google-calendar ---
You have access to Google Calendar. Use these tools to manage events:
- add_event(title, date, time): Create a new event
- list_events(date): List events for a date
...

--- SKILL: agent-hub ---
You have access to the Agent Hub task manager:
- add_task(title, due_date): Add a task to the inbox
- list_tasks(): Show all tasks
...
```

Every skill is a markdown file (`SKILL.md`) that gets read from disk and concatenated into the system prompt. This is how OpenClaw gains new abilities — just drop a new `SKILL.md` in the skills directory.

---

## Practical tips

**Be specific.** "Be helpful" is useless. "Answer in 3 sentences or fewer unless asked to elaborate" is useful.

**Front-load critical rules.** Models attend more to the beginning of context. Put your most important instructions first.

**Keep it lean.** The system prompt burns tokens every call. Don't dump your entire codebase in there. Inject only what's needed for the current session.

**Use sections and headers.** The model parses your system prompt just like text. Organized prose = better behavior.

---

## Next

Read `06-apis.md` to see the exact structure of Anthropic and OpenAI API calls side by side.
