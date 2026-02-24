# 07 — OpenClaw Anatomy

## What is OpenClaw?

OpenClaw is a personal AI assistant that lives in Docker and connects to WhatsApp. It's a real, complete agent system — not a demo. Dissecting it shows how all the pieces from docs 01–06 come together.

---

## The layers

```
WhatsApp message
      ↓
WhatsApp Business API (gateway)
      ↓
OpenClaw container (Docker)
  ├── Message router — receives webhook, routes to agent
  ├── CLI agent — the main loop (think→act→observe)
  ├── Session manager — stores JSONL transcripts per session
  ├── Skill loader — reads SKILL.md files, injects into system prompt
  └── Tool executor — runs whatever tool the LLM requests
      ↓
External services (calendar, task manager, email, etc.)
```

---

## Input → Output at each layer

### WhatsApp → Gateway
- **In:** User sends "add dentist appointment Tuesday at 2pm" via WhatsApp
- **Out:** HTTP POST to OpenClaw with `{sender_id, message_text, timestamp}`

### Gateway → Agent
- **In:** Raw webhook payload
- **Out:** Structured message handed to the session manager + agent loop

### Session manager
- **In:** New message + `sender_id`
- **Out:** Loads existing JSONL transcript for that sender (or starts fresh), appends new message
- **Storage:** `~/.openclaw/agents/main/sessions/{sender_id}.jsonl`

Each line in the JSONL file is one turn:
```json
{"role": "user", "content": "What's on my calendar tomorrow?", "timestamp": "..."}
{"role": "assistant", "content": "...", "timestamp": "..."}
```

### Skill loader
- **In:** `~/.openclaw/workspace/skills/` directory
- **Out:** Concatenated skill docs injected into system prompt

Each skill is a folder with a `SKILL.md` file:
```
~/.openclaw/workspace/skills/
├── google-calendar/
│   └── SKILL.md    ← "You can manage Google Calendar. Tools: add_event, list_events..."
├── agent-hub/
│   └── SKILL.md    ← "You can manage tasks. Tools: add_task, list_tasks..."
└── gmail-triage/
    └── SKILL.md    ← "You can triage Gmail. Tools: fetch_emails, classify..."
```

The system prompt becomes:
```
You are OpenClaw, a personal AI assistant.

--- SKILL: google-calendar ---
[contents of google-calendar/SKILL.md]

--- SKILL: agent-hub ---
[contents of agent-hub/SKILL.md]
```

This is how you add new capabilities to OpenClaw without touching the core agent — just drop a new skill folder.

### Agent loop
- **In:** Full system prompt (with skills) + full conversation history + new user message
- **Out:** Either a text reply or a tool call request

```python
# Simplified version of what the agent does
while True:
    response = llm.call(system_prompt + conversation_history)

    if response.is_final_answer:
        send_whatsapp_reply(response.text)
        save_to_session(response)
        break

    if response.wants_tool:
        result = run_tool(response.tool_name, response.tool_args)
        conversation_history.append(tool_result(result))
        # loop again
```

### Tool executor
- **In:** Tool name + arguments from the LLM
- **Out:** Result string passed back into conversation

Tools are mapped to shell commands or Python functions. For example:
- `add_event` → calls `gcalcli` with the right flags
- `add_task` → makes an HTTP POST to the Agent Hub API
- `list_emails` → calls the gmail-triage CLI

---

## Memory in OpenClaw

OpenClaw uses two memory layers:

**In-context (short-term):** The full JSONL transcript loaded each session. The model sees everything you've said in that conversation thread.

**External (long-term):** Claude Code's `MEMORY.md` is injected into Claude's context when you use Claude Code in this project. OpenClaw doesn't currently have a separate long-term memory — but it could: you'd write key facts to a `memory.md` file and inject it at session start.

---

## The flow, end to end

```
1. You send "Add dentist Tuesday 2pm" on WhatsApp

2. WhatsApp webhook → OpenClaw receives it

3. Session manager loads your conversation history from disk

4. Skill loader reads all SKILL.md files → builds system prompt

5. LLM call: system prompt + history + new message
   → LLM responds: "I'll add that event. Calling add_event."

6. Tool executor: runs gcalcli with the parsed args
   → gcalcli returns: "Event added: Dentist - Tue Feb 25 2:00pm"

7. Result goes back into conversation, LLM generates reply:
   "Done! I added 'Dentist' on Tuesday at 2pm to your calendar."

8. Reply sent back to WhatsApp

9. Both turns (user + assistant) saved to JSONL transcript
```

---

## Key design decisions

**JSONL for transcripts** — append-only, easy to parse, one line per turn. No database needed.

**SKILL.md injection** — skills are documentation, not code. The LLM reads the docs and knows what to do. Adding a skill = adding a folder.

**Tools map to real executables** — `gcalcli`, API calls, CLI tools. The agent doesn't implement calendar logic — it just knows *how to call* existing tools.

**Stateless between sessions** — each message loads the full history fresh. No long-running process to manage.

---

## Now you see the whole picture

| Concept | Where in OpenClaw |
|---|---|
| Agent loop | Main agent loop in the container |
| Perception | WhatsApp webhook → message router |
| In-context memory | JSONL transcript loaded per session |
| External memory | Could be added as memory.md injection |
| Tools | gcalcli, Agent Hub API, gmail-triage CLI |
| System prompt | Built from persona + concatenated SKILL.md files |
| Termination | LLM gives a text reply (no more tool calls) |

This is it. This is what an agent system looks like when it's real.
