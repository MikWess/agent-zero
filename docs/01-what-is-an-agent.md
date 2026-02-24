# 01 — What is an agent?

## Chatbot vs agent

A **chatbot** is one-shot: you send a message, it replies, done.

A **agent** is a loop: it receives a goal, decides what to do, does something, checks the result, and keeps going until the goal is met.

```
Chatbot:   user input → LLM → response           (one round)

Agent:     goal → think → act → observe → think → act → ... → done
```

The key difference: **an agent can take actions and react to what happens.**

---

## The 3 core properties

Every agent has three things:

### 1. Perception
The agent receives input — a user message, a file, a sensor reading, a webhook, a cron trigger. Something kicks it off and gives it context to work with.

### 2. Memory
The agent has some way to remember. At minimum, it has the current conversation in its context window. More powerful agents have external memory (files, databases) so they can remember across sessions.

### 3. Action
The agent can *do things* — call tools, write files, hit APIs, send messages. This is what separates an agent from a plain LLM call. Tools give it hands.

---

## Real examples

**OpenClaw** — a WhatsApp-connected AI assistant.
- Perception: WhatsApp message arrives via webhook
- Memory: conversation history stored as JSONL on disk, loaded into context
- Action: tools like `add_task`, `check_calendar`, `send_reply`

**browser-agent** — AI that controls a real browser.
- Perception: user types a task ("book me a flight")
- Memory: in-context only (the current session)
- Action: tools like `navigate`, `click`, `type_text`, `screenshot`

**You, right now** — reading this doc.
- Perception: reading text
- Memory: your brain (long-term) + working memory (short-term)
- Action: writing code, running commands, making decisions

---

## The mental model

Think of an agent as a person sitting at a computer:
- They read the task (perception)
- They remember what they know (memory)
- They open apps, type things, click buttons (action)
- They look at what happened (observe)
- They decide what to do next (think again)

The LLM is the "thinking" part. The tools are the "hands." The loop is the "workflow."

---

## Next

Read `02-the-loop.md` to see exactly how the think→act→observe cycle works in code.
