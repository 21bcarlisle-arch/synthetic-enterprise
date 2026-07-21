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

import os
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

# THE LEVEL SURFACE (director P0, 2026-07-21): these two files ARE data, but a change to either is
# a level/ledger claim whose downstream effects MUST be validated at COMMIT time, not left to the
# full publish suite. Twice on 2026-07-21 a maturity-map change reached the publish gate red: the
# morning's unbacked self-promotion, and a LEGITIMATE ledger-backed W1_5 L1->L3 ratification that
# flipped a level-dependent count in a proof test. Neither is under CODE_PREFIXES, so the test-gate
# skipped both as "pure data". A change here now runs the LEVEL-SENSITIVE tests -- the reconciler
# (the self-promotion guard), the level gate itself, the coupled-triad gate, and the proof panel
# whose counts derive from live map levels. Director's ask made mechanism: a level-quality claim's
# effect is caught at commit time.
LEVEL_SURFACE_FILES = (
    "docs/design/maturity_map.yaml",
    "docs/observability/gate_authorizations.jsonl",
)
LEVEL_SENSITIVE_TESTS = [
    "tests/background/test_fronts_reconciler.py",
    "tests/background/test_gate_authorization.py",
    "tests/tools/test_level_promotion_gate.py",
    "tests/tools/test_generate_proof_coupled_gaps.py",
    "tests/test_coupled_triad_gate.py",
]


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
    """The set of test files to run for this commit, or [] to skip (no code/config/level-surface
    staged)."""
    code_changed = any(f.startswith(CODE_PREFIXES) for f in files)
    level_surface_changed = any(f in LEVEL_SURFACE_FILES for f in files)
    if not code_changed and not level_surface_changed:
        return []  # pure docs/data commit that touches no control and no level surface
    targets: set[str] = set()
    if code_changed:
        targets.update(t for t in CONTROL_TESTS if (ROOT / t).exists())
    if level_surface_changed:
        targets.update(t for t in LEVEL_SENSITIVE_TESTS if (ROOT / t).exists())
    for f in files:
        targets.update(tests_for(f))
    return sorted(targets)


def _gitless_env(env: dict) -> dict:
    """Strip every GIT_* key from an environment mapping.

    CRITICAL: during a `git commit` the hook inherits GIT_INDEX_FILE / GIT_DIR / GIT_WORK_TREE /
    GIT_PREFIX pointing at the IN-PROGRESS commit. Any git-touching test (e.g. build_executor,
    retro_cadence_check, worker_seat) then runs `git` subprocesses that operate on the REAL
    worktree index -- observed corrupting it (phantom deletions) and once producing a commit that
    deleted the whole tree; a leaked GIT_DIR is also the likely setter of the core.bare=true
    corruption. Scrubbing GIT_* makes gate-run tests use their own tmp repos, never the commit's
    index. (H24_precommit_gate_git_env_isolation)
    """
    return {k: v for k, v in env.items() if not k.startswith("GIT_")}


def main() -> int:
    targets = select_targets(staged_files())
    if not targets:
        return 0  # pure docs/data commit -- nothing that can break a control
    print(f"[test-gate] {len(targets)} test file(s): {', '.join(targets)}")
    gitless_env = _gitless_env(os.environ)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *targets, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(ROOT),
        env=gitless_env,
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
