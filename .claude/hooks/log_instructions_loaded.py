#!/usr/bin/env python3
"""InstructionsLoaded hook -- logs every CLAUDE.md/.claude/rules/*.md load
event to docs/observability/instructions_loaded_log.jsonl.

H7_skills_and_rules (2026-07-12, HARDEN pass): the path-scoped rules in
.claude/rules/ inject silently by design (per the official docs -- no
visible confirmation the way Skill invocation has). This hook is the
concrete, observable evidence mechanism the official docs themselves
recommend for exactly this ("useful for debugging path-specific rules or
lazy-loaded files in subdirectories") -- it turns an opaque internal
matching decision into a real, checkable log line, closing the same class
of gap H6_lane_wall_development_pilot's own HARDEN pass demanded (execute
adversarial cases against the real mechanism, don't theorize about it).

Exit code is ignored for this hook type (side-effect logging only, cannot
block) -- always exits 0.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
LOG_PATH = PROJECT_DIR / "docs" / "observability" / "instructions_loaded_log.jsonl"


def main() -> int:
    # Same test-isolation guard as background/director_input_log.py's
    # append_entry() / background/ntfy_mirror.py's append_mirror_entry()
    # (2026-07-09 tmux-leak-class incident) -- a real subprocess-based hook
    # test (unlike an in-process monkeypatch) has no way to redirect this
    # script's own LOG_PATH, so without this guard every subprocess smoke
    # test pollutes the real observability log (confirmed directly: the
    # first version of this hook, with no guard, wrote a real test payload
    # to docs/observability/instructions_loaded_log.jsonl the first time its
    # own subprocess test ran).
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return 0
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "load_reason": payload.get("load_reason"),
        "file_path": payload.get("file_path"),
        "file_name": payload.get("file_name"),
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
