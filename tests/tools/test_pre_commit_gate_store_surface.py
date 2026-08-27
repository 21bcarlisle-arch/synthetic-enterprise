"""The MAP/STORE SIZE surface of the pre-commit test gate, proven able to FAIL (R15).

WHY THIS FILE EXISTS (2026-08-14, WORKER_FINDING_THE_MAPS_TWO_CONTROLS_ARE_UNREACHABLE_FROM_THE_MAP,
BLOCKING, lane H_harness). Two controls in `tests/design/test_simplifications_store.py` take
`docs/design/maturity_map.yaml` as their SUBJECT -- the 409,600 B spine ratchet and the
`simplifications_count`-vs-store-file check. Neither could be selected by editing the map.
Measured that day with `select_targets` called directly:

    docs/design/maturity_map.yaml            -> 7 targets, this file NOT among them
    docs/design/simplifications/<atom>.yaml  -> 2 targets, likewise not
    tools/simplifications_store.py           -> selects it
    tests/design/test_simplifications_store.py -> selects it

So both controls were reachable only from their own IMPLEMENTATION and from THEMSELVES.
Every edit that could break them was an edit that could not select them. The consequence was
observed rather than predicted: HEAD sat at 410,095 B -- 495 B over the ratchet -- with two
atoms declaring `simplifications_count` values their store files contradicted, and a commit
that EDITED THE MAP landed through `tools.surgical_land` at `gate-rc 0` on top of that state.

THE CLASS, and why it is permanent here. `tools.pre_commit_test_gate` selects tests by NAME
STEM. For a MODULE that is transient -- a moved or newly-created module is unreachable only
until something is named after it. For a DATA file there is no implementation stem to match,
ever, so a control whose subject is a committed artefact is unreachable ALWAYS. This is R15's
FAIL-SILENT shape at the SELECTION layer rather than inside the assertion: both control bodies
were correct and fired the moment anything ran them.

THE SAME THREE LAYERS as the site-surface and canon-surface files beside it, for the reason
those files state -- asserting a string is in a list is a gate extension that passes on
everything, which is the fail-open pattern this project already names:

  1. SELECTION -- a `docs/design/maturity_map.yaml` commit, and a store-file commit, each
     select the size/count controls. Mutation: drop the entry from STORE_CONTRACT_TESTS
     -> layer 1 fails.
  2. LIVE CONTROL -- the selected control, run against a tree whose map is ONE BYTE over the
     ratchet, actually goes RED and red for THIS reason. This is the finding's own explicit
     condition on the repair: "It must be mutation-proven from the data side. Editing the map
     to add one byte over the ratchet must RED at the commit. Adding the selection entry
     without that proof reproduces the defect one layer up -- a selection rule nothing checks
     is the same fail-silent."
  3. ANTI-TAUTOLOGY + NARROW TRIGGER -- the same control is GREEN on the unmutated tree (so
     layer 2's red is the byte, not the harness), and an unrelated docs commit still selects
     nothing.

Layer 2 runs against a MINIMAL COPY in tmp_path, never the real tree: `docs/design/maturity_map.yaml`
is written by the resident worker, the auto-processor and concurrent lanes, so mutating it in
place would race writers this repo explicitly warns about -- and mutating a file to prove a
control fires is how a real edit gets reverted (`feedback_mutation_restore_wipes_edit`).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import pre_commit_test_gate as gate

REPO_ROOT = Path(__file__).resolve().parents[2]
STORE_TEST = "tests/design/test_simplifications_store.py"
MAP_REL = "docs/design/maturity_map.yaml"
RATCHET_TEST = "test_map_within_size_ratchet_when_store_populated"
COUNTS_TEST = "test_counts_match_file_contents"


# --- Layer 1: the gate SELECTS the controls ----------------------------------

def test_a_map_commit_selects_the_size_and_count_controls():
    """The wiring itself -- the exact state measured on 2026-08-14, when it selected 7
    targets and this file was not one of them."""
    targets = gate.select_targets([MAP_REL])
    assert STORE_TEST in targets, (
        "a commit editing the maturity map does not run the controls whose SUBJECT is the "
        f"maturity map -- an oversized map cannot fail this gate. selected: {sorted(targets)}"
    )


def test_a_store_file_commit_selects_them_too():
    """The other side of the same contract: a store file is where a `simplifications_count`
    stops matching, and it is equally a data path with no implementation stem."""
    assert STORE_TEST in gate.select_targets(
        ["docs/design/simplifications/EP7_adapter_elexon_insights.yaml"]
    )


def test_the_declared_control_exists_on_disk():
    """A surface wired to a test file that does not exist is a fail-silent gate extension."""
    for rel in gate.STORE_CONTRACT_TESTS:
        assert (REPO_ROOT / rel).is_file(), f"{rel} is declared but missing"


# --- Layer 2: the selected control BITES -------------------------------------

@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A minimal copy: the map, the store, the loader, and the control itself."""
    root = tmp_path / "repo"
    (root / "tools").mkdir(parents=True)
    (root / "tests" / "design").mkdir(parents=True)
    (root / "docs" / "design").mkdir(parents=True)

    # THE MAP IS TWO FILES SINCE 2026-08-26, and the SET IS DERIVED rather than listed.
    #
    # This fixture copied `MAP_REL` alone and hard-coded `tools/simplifications_store.py` as the
    # only loader. The split (docs/design/MAP_SPLIT_2026-08-26.md) added
    # `maturity_map_closed.yaml` and `tools/maturity_map_store.py`, and
    # `tests/design/test_simplifications_store.py` -- the control this fixture exists to drive --
    # imports that loader. So the stand-in repo could no longer import the control at all, and
    # all three mutation tests below failed on `ImportError: cannot import name
    # 'maturity_map_store'` instead of on their own subjects. A mutation test that fails for the
    # wrong reason proves nothing about the control it was aimed at.
    #
    # `MAP_PARTS_REL` is the loader's OWN declaration of which files the map consists of, so a
    # third half, or a rename, is inherited here rather than needing this list edited again.
    from tools.maturity_map_store import MAP_PARTS_REL
    for rel in MAP_PARTS_REL:
        shutil.copy(REPO_ROOT / rel, root / rel)

    shutil.copytree(
        REPO_ROOT / "docs" / "design" / "simplifications",
        root / "docs" / "design" / "simplifications",
    )
    for pkg in ("tools", "tests", "tests/design"):
        src = REPO_ROOT / pkg / "__init__.py"
        if src.is_file():
            shutil.copy(src, root / pkg / "__init__.py")
    for module in ("simplifications_store.py", "maturity_map_store.py"):
        shutil.copy(REPO_ROOT / "tools" / module, root / "tools")
    shutil.copy(REPO_ROOT / STORE_TEST, root / STORE_TEST)
    return root


def _run(tree: Path, test: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", f"{STORE_TEST}::{test}", "-q"],
        cwd=str(tree), capture_output=True, text=True, timeout=300,
    )


def test_the_selected_control_goes_RED_when_the_map_is_ONE_BYTE_over(tree: Path):
    """THE R15 PROOF, FROM THE DATA SIDE. The defect in the shape it actually arrives: an
    atom gains a field and the map crosses its ceiling. One byte, because the finding's
    condition is that the NEXT byte reds -- not that a large regression does."""
    import re

    map_path = tree / MAP_REL
    text = map_path.read_text(encoding="utf-8")

    # The ceiling is READ FROM THE CONTROL, never restated here: a hard-coded 409600 in
    # this file would keep passing after someone moved the line, which is the tautology
    # shape (a check whose subject is its own copy of the value).
    m = re.search(
        r"MAP_SIZE_CEILING\s*=\s*(\d+)\s*\*\s*(\d+)",
        (REPO_ROOT / STORE_TEST).read_text(encoding="utf-8"),
    )
    assert m, "MAP_SIZE_CEILING not found in the control -- this proof cannot size its mutation"
    ceiling = int(m.group(1)) * int(m.group(2))
    need = ceiling + 1 - len(text.encode("utf-8"))
    assert need > 0, (
        f"the real map is already at/over the ceiling ({len(text.encode())} vs {ceiling}) -- "
        "this proof needs a green baseline to push over"
    )
    pad = "#" + ("x" * (need - 2)) + "\n"
    map_path.write_text(text + pad, encoding="utf-8")
    assert len(map_path.read_bytes()) == ceiling + 1

    result = _run(tree, RATCHET_TEST)

    assert result.returncode != 0, (
        "the spine ratchet PASSED on a map one byte over its own ceiling -- the control the "
        f"gate now selects does not bite.\n{result.stdout}"
    )
    assert "over the" in result.stdout and str(ceiling) in result.stdout, (
        f"it failed, but not for being over the ratchet -- wrong reason:\n{result.stdout}"
    )


def test_the_count_control_goes_RED_on_a_declared_count_that_lies(tree: Path):
    """The other control on the same surface, mutated from the data side too: an atom
    declaring a `simplifications_count` its store file contradicts. This is the defect that
    was live at HEAD on 2026-08-14 (D30 and SITE2), undetected for the same reason."""
    import yaml

    map_path = tree / MAP_REL
    atoms = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    target = next(a["id"] for a in atoms if a.get("simplifications_count"))
    text = map_path.read_text(encoding="utf-8")
    lines, cur, out = text.splitlines(keepends=True), None, []
    for ln in lines:
        if ln.startswith("- id: "):
            cur = ln[6:].strip()
        if cur == target and ln.strip().startswith("simplifications_count:"):
            ln = "  simplifications_count: 9999\n"
        out.append(ln)
    map_path.write_text("".join(out), encoding="utf-8")

    result = _run(tree, COUNTS_TEST)

    assert result.returncode != 0, (
        "the count control PASSED on a map declaring a count its store file contradicts.\n"
        f"{result.stdout}"
    )
    assert target in result.stdout, (
        f"the failure does not name the atom whose count lies:\n{result.stdout}"
    )


def test_both_controls_are_GREEN_on_the_unmutated_tree(tree: Path):
    """ANTI-TAUTOLOGY. Without this, the two reds above could be the harness rather than the
    mutation -- and the whole file would prove nothing. It is also the standing check that
    the DRAIN held: this goes red the moment the real map crosses the ratchet again."""
    for test in (RATCHET_TEST, COUNTS_TEST):
        result = _run(tree, test)
        assert result.returncode == 0, (
            f"{test} is red on the real map with no mutation applied:\n"
            f"{result.stdout}\n{result.stderr}"
        )


# --- Layer 3: the trigger stayed NARROW --------------------------------------

def test_an_unrelated_docs_commit_still_runs_nothing():
    """The gate's cadence is deliberately fast; this must not tax every docs commit."""
    assert gate.select_targets(["docs/status/LATEST.md"]) == []
