# Example 05 — Daemon Agent

## Concept

A daemon is an agent that runs on a schedule — not triggered by a human, but by time. It wakes up, does a job, sleeps, repeats.

This example shows:
- A simple interval scheduler (wake up every N seconds)
- An agent that monitors simulated system metrics each tick
- Memory across ticks — the agent remembers what it saw before and compares

OpenClaw is essentially a daemon: it runs continuously in Docker, sleeping until a WhatsApp message arrives, then waking up to handle it.

## Input → Output

```
Starting daemon agent — monitoring simulated system metrics
Press Ctrl+C to stop

==================================================
[Run #1] 2024-01-15 10:00:00
==================================================
Metrics: CPU 67.3% | Memory 41.2%
Agent: All systems nominal. CPU at 67% and memory at 41% are within acceptable ranges.
  [Saved]: Run 1 - CPU 67.3%, Memory 41.2% — normal

Sleeping 10s until next run...

==================================================
[Run #2] 2024-01-15 10:00:10
==================================================
Metrics: CPU 88.5% | Memory 43.1%
Agent: ⚠️ CPU spike to 88.5% — elevated from the 67% seen last run. Memory stable at 43%.
  [Saved]: Run 2 - CPU spike to 88.5% flagged

Sleeping 10s until next run...
```

## How to run

```bash
python examples/05_daemon_agent/agent.py

# Runs 4 times (every 10 seconds) then stops
# Watch it build up memory across runs

# Inspect what it remembered
cat examples/05_daemon_agent/daemon_memory.md

# Reset
rm examples/05_daemon_agent/daemon_memory.md
```

## Files

| File | What it does |
|---|---|
| `scheduler.py` | `run_on_interval(fn, seconds, max_runs)` — the timing loop |
| `agent.py` | The monitoring agent — reads metrics, reasons, saves observations |
| `daemon_memory.md` | Created on first run — observations across ticks |

## The daemon pattern

```python
def agent_tick():
    data = get_current_data()      # what's happening right now?
    memory = load_memory(path)     # what have I seen before?
    response = llm.call(data + memory)  # reason about it
    if notable: save_memory(path, observation)  # remember this

run_on_interval(agent_tick, interval_seconds=60)  # wake up every minute
```

## Production deployment

In production you'd run this as:
- **Cron job**: `* * * * * python agent.py` (runs every minute)
- **Systemd service**: persistent process, auto-restart on crash
- **Docker container**: like OpenClaw — containerized, always running

## Related docs

- `docs/04-memory.md` — memory types
- `docs/07-openclaw-anatomy.md` — OpenClaw as a real daemon agent
