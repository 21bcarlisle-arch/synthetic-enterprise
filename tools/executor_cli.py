#!/usr/bin/env python3
"""Thin CLI frontend for the governed build-executor (AUTONOMOUS_EXECUTOR_SPEC.md §C.1).

  * `--once`   : run ONE gated cycle (draw -> dispatch -> gate on landed evidence -> record)
                 and print the outcome. This is the attended L1 step (§C.6 #6): safe with the
                 builder present, a single manual invocation, NOT the unattended daemon.
  * `--daemon` : run the self-continuing headless loop (executor_governor.run_loop). DARK by
                 default — it dispatches nothing unless the director's console-only enable flag
                 (`docs/observability/.build_executor_enabled`) is present. Refuses to run
                 unbounded: pass --max-turns-per-hour (the director's C.7 #1 budget number) or
                 --max-cycles.

This CLI creates NO enable flag and adds NO launcher wiring — turning the loop ON is a
director-console-only safety step (§C.5). Running `--daemon` with the flag absent is a safe
no-op by construction.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from background import build_executor, executor_governor  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="one gated cycle, then exit")
    mode.add_argument("--daemon", action="store_true", help="self-continuing loop (kill-switch gated)")
    ap.add_argument("--max-turns-per-hour", type=int, default=None,
                    help="TurnBudget cap (director's C.7 #1 number); required for an unbounded --daemon")
    ap.add_argument("--max-cycles", type=int, default=None,
                    help="stop after N cycles (a bounded run / test guard)")
    args = ap.parse_args(argv)

    if args.once:
        result = build_executor.run_once()
        print(f"[executor --once] status={result.status} landed={result.landed} "
              f"sha={result.claimed_sha} detail={result.detail}")
        return 0 if result.status in ("success", "idle") else 1

    # --daemon
    if args.max_turns_per_hour is None and args.max_cycles is None:
        print("refusing to run an unbounded daemon: pass --max-turns-per-hour "
              "(director's budget number) or --max-cycles.", file=sys.stderr)
        return 2
    budget = (
        executor_governor.TurnBudget(max_turns_per_window=args.max_turns_per_hour)
        if args.max_turns_per_hour is not None
        else None
    )
    summary = executor_governor.run_loop(budget=budget, max_cycles=args.max_cycles)
    print(f"[executor --daemon] stopped: {summary.stop_reason} after {summary.cycles} cycle(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
