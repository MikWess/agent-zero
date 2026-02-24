"""
scheduler.py — Simple interval-based scheduler

Runs a function on a fixed interval (every N seconds).
This is the core of a daemon agent — it wakes up, does its job, sleeps, repeats.

Input/Output:
  run_on_interval(fn, interval_seconds, max_runs) → runs fn() repeatedly
"""

import time
from datetime import datetime
from typing import Callable, Optional


def run_on_interval(
    fn: Callable,
    interval_seconds: int = 60,
    max_runs: Optional[int] = None,
) -> None:
    """
    Call fn() every interval_seconds seconds.

    Takes:
      fn:               the function to run each tick
      interval_seconds: how long to wait between runs (default: 60)
      max_runs:         stop after this many runs (None = run forever)

    Returns: nothing (runs until max_runs is hit or KeyboardInterrupt)

    Usage:
      run_on_interval(my_agent_fn, interval_seconds=30, max_runs=5)
    """
    run_count = 0

    print(f"Scheduler started — running every {interval_seconds}s", end="")
    if max_runs:
        print(f" for {max_runs} run(s)")
    else:
        print(" (press Ctrl+C to stop)")

    while True:
        run_count += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*50}")
        print(f"[Run #{run_count}] {now}")
        print(f"{'='*50}")

        # Run the agent function
        try:
            fn()
        except Exception as e:
            # Log the error but don't crash the daemon — keep running
            print(f"[Error in run #{run_count}]: {e}")

        # Check if we've hit the run limit
        if max_runs and run_count >= max_runs:
            print(f"\nScheduler: reached max_runs ({max_runs}), stopping.")
            break

        # Sleep until the next run
        print(f"\nSleeping {interval_seconds}s until next run...")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
            break
