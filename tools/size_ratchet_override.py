#!/usr/bin/env python3
"""SP3 -- the size-ratchet override helper: a NAMED, LOGGED exception, never a silent one.

Ruling s8 requires the ratchet to carry "a named, logged override rather than a silent one". This
reuses `background/decision_log.py` -- the repo's existing append-only decision primitive -- rather
than inventing a parallel override log, because building a second log inside the atom whose job is
to stop duplication would be self-refuting.

THE OVERRIDE IS SCOPED TO ONE FILE AT ONE LINE COUNT. It authorises `<path>` up to `<lines>` and
nothing else: grow that file again and the gate fires again, needing a fresh logged decision. A
per-file-forever exemption would be the fail-open the DISCOVER's R15 plan (test 6) names explicitly.

Usage:
    python3 tools/size_ratchet_override.py --file saas/reporting/annual_report.py --lines 9300 \\
        --why "..." --reverse "..."
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.size_ratchet_gate import OVERRIDE_PREFIX  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Log a scoped size-ratchet override.")
    parser.add_argument("--file", required=True, help="the path being authorised to grow")
    parser.add_argument("--lines", required=True, type=int, help="the new line count authorised")
    parser.add_argument("--why", required=True, help="why this growth is right (not 'to pass')")
    parser.add_argument("--reverse", required=True, help="the single act that undoes it")
    args = parser.parse_args(argv)

    if not args.why.strip() or not args.reverse.strip():
        print("[size-ratchet-override] --why and --reverse must be non-empty", file=sys.stderr)
        return 1

    from background.decision_log import log_decision

    entry = log_decision(
        what=f"{OVERRIDE_PREFIX} {args.file} @ {args.lines}",
        why=args.why,
        how_to_reverse=args.reverse,
    )
    print(
        f"[size-ratchet-override] logged: {args.file} authorised to {args.lines} lines "
        f"at {entry['timestamp']}\n  why: {args.why}\n  reverse: {args.reverse}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
