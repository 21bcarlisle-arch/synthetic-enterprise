"""Pre-commit TEST GATE (director P0, 2026-07-17): a commit with red tests is STRUCTURALLY
IMPOSSIBLE, not merely discouraged.

Why a mechanism, not a resolution: on 2026-07-17 two commits landed with red tests because the
process was "run tests, then commit" -- a remembered discipline, and remembered disciplines are
exactly what failed (twice). The same principle as everything else in the operational rebuild:
structural impossibility over remembered care (reaper deleted -> exit-143 impossible; this gate ->
red-commit impossible). It matters MOST right now because parallel-safety controls (the gate-wall,
the reconcilers) are being built with an autonomously-committing loop: if red commits are possible,
a subtly-broken safety control could land looking green in the log.

What runs (fast, so the loop's cadence is not taxed):
  - the SAFETY-CONTROL set ALWAYS, whenever any CODE/config file is staged -- these protect the
    controls even when an unrelated dependency (e.g. background/notify.py, which every alarm routes
    through) changes.
  - the test file for each changed source file (background/X.py -> tests/**/test_X.py; a changed
    test file -> itself).
A pure docs/site/data commit (no code/config staged) runs nothing -- it cannot break a control.
Any failure -> exit 1 -> the commit is ABORTED. The only bypass is git's own --no-verify, which
this repo's own one_way_door.py flags as a dangerous pattern; none of our committers use it.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Always run when code/config changes -- the controls the director is protecting tonight.
CONTROL_TESTS = [
    "tests/background/test_gate_authorization.py",
    "tests/background/test_fork_reconciler.py",
    "tests/background/test_transport_failure_loud.py",
    "tests/background/test_deadmans_switch.py",
    "tests/background/test_status_honesty.py",
    "tests/hooks/test_pull_next_work.py",
]

# A staged path under any of these = a code/config change that could break a control or its own
# tests -> run the gate. Anything else (docs/status, docs/reports, site/data, observability) is
# pure data and cannot break a control -> skip (keep the loop's commit cadence fast).
CODE_PREFIXES = (
    "background/", ".claude/", "tests/", "tools/",
    "saas/", "company/", "sim/", "simulation/", "interface/",
)


def staged_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=str(ROOT), capture_output=True, text=True,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def tests_for(path: str) -> list[str]:
    """Map a changed file to its test file(s): a changed test file -> itself; a changed *.py ->
    tests/**/test_<stem>.py if present."""
    p = Path(path)
    if p.suffix != ".py":
        return []
    if p.name.startswith("test_") and (ROOT / p).exists():
        return [str(p)]
    return [str(c.relative_to(ROOT)) for c in ROOT.glob(f"tests/**/test_{p.stem}.py")]


def select_targets(files: list[str]) -> list[str]:
    """The set of test files to run for this commit, or [] to skip (no code/config staged)."""
    if not any(f.startswith(CODE_PREFIXES) for f in files):
        return []
    targets = {t for t in CONTROL_TESTS if (ROOT / t).exists()}
    for f in files:
        targets.update(tests_for(f))
    return sorted(targets)


def main() -> int:
    targets = select_targets(staged_files())
    if not targets:
        return 0  # pure docs/data commit -- nothing that can break a control
    print(f"[test-gate] {len(targets)} test file(s): {', '.join(targets)}")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *targets, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(ROOT),
    )
    if r.returncode != 0:
        sys.stderr.write(
            "\n[test-gate] ❌ TESTS FAILED -- COMMIT REFUSED.\n"
            "[test-gate] A red commit is structurally impossible (director P0, 2026-07-17). "
            "Fix the tests, then commit.\n"
        )
        return 1
    print("[test-gate] ✓ all targeted tests green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
