"""The CANON SURFACE half of the pre-commit test gate, proven able to FAIL (R15).

WHY THIS FILE EXISTS (2026-08-12 decay audit, §P2 of
docs/staging/ADVISOR_FINDINGS_CLAUDE_MD_DECAY_AUDIT_2026-08-07.md).

CLAUDE.md's central doctrine is "a rule lives in CLAUDE.md AND as enforced code, or not at all".
It was, for its whole life, the one document the commit gate could not see you editing:

  * `background/claude_md_integrity.py` sets MAX_CHARS = 35_000 as a fixed doctrine constant and
    `tests/tools/test_claude_md_integrity.py::test_real_claude_md_within_hard_limit` asserts the
    live file against it -- a real control, with real mutation tests behind it.
  * But the ONLY thing that ran that control was the full publish suite. On 2026-08-03 commit
    `52693115b` put CLAUDE.md 504 chars over the limit four hours after `08d31bcce` had
    deliberately trimmed it under. The test sat red at HEAD for four days while publishing was
    separately wedged, and nothing said so.
  * OPS5 (2026-08-10) added CLAUDE.md to the gate's CANON_SURFACE_FILES -- the trigger -- but
    wired it to `test_interim_bypass_retirement.py` only. Measured on 2026-08-12 before the fix:
    `select_targets(['CLAUDE.md'])` returned exactly that one test. The trigger existed, the
    control existed, and they had never been connected to each other.

So the ceiling could not fail a gate. This file is what makes the claim that it now can into
something checkable, and it deliberately does NOT stop at asserting a string is in a list -- "a
gate extension that passes on everything is the fail-open pattern this project already names".

THREE LAYERS, each failing on a different mutation:

  1. SELECTION -- the gate picks the integrity control for a CLAUDE.md commit.
     Mutation: drop it from CANON_SURFACE_TESTS -> layer 1 fails.
  2. LIVE CONTROL (the R15 proof proper) -- the selected test file, run against a tree whose
     CLAUDE.md is over the limit, actually goes RED, and red for THIS reason (its output names the
     hard limit). Mutation: raise MAX_CHARS to accommodate an oversize file, or gut the assertion
     -> layer 2 fails. This is the layer that makes layer 1 mean something: it proves the gate
     selects a control that BITES, not a name in a list.
  3. ANTI-TAUTOLOGY + NARROW TRIGGER -- the same run against an in-limit CLAUDE.md passes (so
     layer 2's red is caused by the oversize content, not by the harness), and an unrelated docs
     commit still selects nothing (so the fix did not tax every docs commit -- the gate's docstring
     is explicit that it was scoped narrow deliberately to keep the loop's cadence fast).

Layer 2 runs against a MINIMAL COPY of the tree in tmp_path, never the real one: both
`claude_md_integrity.PROJECT_DIR` and the test's own `REPO_ROOT` are derived from `__file__`, so a
copy relocates them cleanly. Mutating the real CLAUDE.md in place would race the other writers this
repo explicitly warns about (process_run_complete, the tick's invocation, an interactive session).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import pre_commit_test_gate as gate

REPO_ROOT = Path(__file__).resolve().parents[2]
INTEGRITY_TEST = "tests/tools/test_claude_md_integrity.py"
# The single test the ceiling lives in. Layer 2 runs ONLY this one: it needs nothing but CLAUDE.md
# and the integrity module, so the tmp copy stays small and the red is unambiguous.
CEILING_TEST = "test_real_claude_md_within_hard_limit"


# --- Layer 1: the gate SELECTS the control -----------------------------------

def test_a_claude_md_commit_selects_the_integrity_control():
    """The wiring itself. Fails if CLAUDE.md is dropped from CANON_SURFACE_FILES or the integrity
    test is dropped from CANON_SURFACE_TESTS -- the exact state measured on 2026-08-12."""
    targets = gate.select_targets(["CLAUDE.md"])
    assert INTEGRITY_TEST in targets, (
        "a commit editing CLAUDE.md does not run the control that measures CLAUDE.md — the size "
        f"ceiling cannot fail this gate. selected: {targets}"
    )


def test_the_canon_surface_still_carries_its_original_test():
    """The fix must ADD, not replace: OPS5's bypass-retirement guard is still selected."""
    assert "tests/tools/test_interim_bypass_retirement.py" in gate.select_targets(["CLAUDE.md"])


def test_the_integrity_control_is_declared_and_exists_on_disk():
    """select_targets filters CANON_SURFACE_TESTS through `(ROOT / t).exists()`, so a typo'd or
    moved path degrades SILENTLY to 'not selected' rather than erroring. That is fail-open on the
    wiring itself; assert both halves separately so a rename is loud."""
    assert INTEGRITY_TEST in gate.CANON_SURFACE_TESTS
    assert (REPO_ROOT / INTEGRITY_TEST).is_file()


# --- Layer 2: the selected control actually BITES (the R15 mutation proof) ----

def _minimal_tree(root: Path, claude_md_text: str) -> Path:
    """A tmp tree holding just enough for CEILING_TEST: the integrity module and its test, plus a
    CLAUDE.md to measure. `background` is a namespace package here exactly as it is in the repo
    (there is no background/__init__.py), so the import resolves the same way."""
    (root / "background").mkdir(parents=True)
    (root / "tests" / "tools").mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "background" / "claude_md_integrity.py", root / "background")
    shutil.copy2(REPO_ROOT / INTEGRITY_TEST, root / "tests" / "tools")
    for pkg in (root / "tests" / "__init__.py", root / "tests" / "tools" / "__init__.py"):
        pkg.write_text("")
    (root / "CLAUDE.md").write_text(claude_md_text, encoding="utf-8")
    return root


def _run_ceiling_test(tree: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["PYTHONPATH"] = str(tree)
    return subprocess.run(
        [sys.executable, "-m", "pytest", f"{INTEGRITY_TEST}::{CEILING_TEST}",
         "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(tree), capture_output=True, text=True, env=env,
    )


@pytest.fixture(scope="module")
def real_claude_md() -> str:
    return (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")


def test_the_selected_control_goes_red_on_an_oversize_claude_md(tmp_path, real_claude_md):
    """THE MUTATION. The advisor's non-negotiable, verbatim: "a mutation showing it fires on an
    oversize instruction file committed alone".

    Padding is applied to the REAL file's text rather than to synthetic filler, so the mutation
    reproduces the actual 2026-08-03 regression shape — a healthy CLAUDE.md that someone appended a
    paragraph to — and not a degenerate all-'x' document that might trip some other check first.

    The pad is sized to land a FIXED distance past MAX_CHARS, not to add a fixed increment. A fixed
    increment silently stops being a mutation as soon as the file is trimmed — which is exactly what
    happened the first time this test ran, minutes after the audit's trim freed 8k of headroom. A
    mutation test that quietly stops mutating is the fail-open pattern in miniature.
    """
    from background import claude_md_integrity as integ

    over_by = 504  # the exact breach 52693115b landed on 2026-08-03
    deficit = (integ.MAX_CHARS + over_by) - len(real_claude_md)
    assert deficit > 0, "CLAUDE.md is already over the limit — fix that before reading this failure"
    oversize = real_claude_md + "\n<!-- " + ("pad " * (deficit // 4 + 1)) + "-->"
    assert len(oversize) > integ.MAX_CHARS, "the mutation must actually breach the limit"

    r = _run_ceiling_test(_minimal_tree(tmp_path / "over", oversize))

    assert r.returncode != 0, (
        "the control the gate selects PASSED on a CLAUDE.md over its own hard limit — the gate "
        f"selects a test that cannot fail.\n{r.stdout}\n{r.stderr}"
    )
    assert "hard limit" in (r.stdout + r.stderr), (
        "the control went red, but not for the size breach — the red must be caused by the "
        f"mutation, not by the harness.\n{r.stdout}\n{r.stderr}"
    )


def test_the_selected_control_is_green_on_the_real_claude_md(tmp_path, real_claude_md):
    """ANTI-TAUTOLOGY (R15): the red above must come from the oversize content, not from running in
    a tmp tree. Same harness, unmutated file, must pass. This also means HEAD's CLAUDE.md is
    asserted in-limit from a second, independent direction."""
    r = _run_ceiling_test(_minimal_tree(tmp_path / "ok", real_claude_md))
    assert r.returncode == 0, (
        "the control failed on the REAL, in-limit CLAUDE.md — the mutation test above proves "
        f"nothing until this passes.\n{r.stdout}\n{r.stderr}"
    )


# --- Layer 3: the trigger stays narrow ---------------------------------------

def test_an_unrelated_docs_commit_still_runs_nothing():
    """The gate's docstring is explicit that it was scoped narrow deliberately, and the advisor's
    risk note names 'the gate widening taxes the commit loop' as the mitigation to hold. A pure
    docs commit that touches no canon/level/mint/store surface must still select zero tests."""
    assert gate.select_targets(["docs/status/LATEST.md"]) == []
    assert gate.select_targets(["docs/reports/ANNUAL_REPORT.md", "site/data/dashboard.json"]) == []


def test_the_other_canon_file_also_selects_the_bypass_guard():
    """CANON_SURFACE_FILES carries two entries; SURGICAL_LANDING.md is the other. It is the doc that
    states the one legal move replacing the retired bypass, so it keeps its own guard — but it is
    NOT measured by claude_md_integrity, so it should not pull that control in."""
    targets = gate.select_targets(["docs/design/SURGICAL_LANDING.md"])
    assert "tests/tools/test_interim_bypass_retirement.py" in targets
