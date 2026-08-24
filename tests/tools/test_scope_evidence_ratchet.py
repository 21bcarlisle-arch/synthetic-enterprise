"""R15 contract for the scope-evidence ratchet.

THE DEFECT IT EXISTS TO CATCH, reproduced in miniature by
`test_a_claimed_level_pointing_at_a_deleted_file_is_REFUSED`: an atom at `level_current: 3`
naming three site pages, all three deleted by a director-ruled restructure four days earlier.
A level is a claim about evidence; a deleted path is not evidence.

WHY THE CONTROL IS INTERESTING AT ALL is the other half -- that it must NOT fire on the map's
17 legitimate level-0 proposals, each naming the files it would create. A control that refuses
those makes the map unable to describe future work, and would be turned off inside a week. So
the tests below spend as much effort proving it stays quiet as proving it fires.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from tools import scope_evidence_ratchet as ser

REPO = Path(ser.__file__).resolve().parent.parent


def _map(body: str) -> str:
    return textwrap.dedent(body)


# --------------------------------------------------------------------------- #
# It fires                                                                     #
# --------------------------------------------------------------------------- #

def test_a_claimed_level_pointing_at_a_deleted_file_is_REFUSED(tmp_path: Path):
    """The 2026-08-24 finding in miniature -- E2_revenue_reconciliation's actual shape."""
    (tmp_path / "kept.py").write_text("x = 1\n")
    text = _map("""
        - id: E2_revenue_reconciliation
          level_current: 3
          file_scope: ["kept.py", "site/supplier/index.html"]
        """)

    bad = ser.violations(text, root=tmp_path, tracked=frozenset({"kept.py"}))

    assert bad == [("E2_revenue_reconciliation", 3, "site/supplier/index.html", ser.DELETED)]


def test_every_missing_path_is_named_not_just_the_first(tmp_path: Path):
    """A refusal that names one of three gone pages sends the reader back three times."""
    text = _map("""
        - id: A
          level_current: 3
          file_scope: ["a.py", "b.py", "c.py"]
        """)

    assert len(ser.violations(text, root=tmp_path, tracked=frozenset())) == 3


def test_the_block_list_style_is_read_as_well_as_the_inline_one(tmp_path: Path):
    """The map carries BOTH styles today, and an unread style is an unchecked atom."""
    text = _map("""
        - id: A
          level_current: 2
          file_scope:
          - background/session_watchdog.py
          - background/worker_seat.py
        """)

    assert len(ser.violations(text, root=tmp_path, tracked=frozenset())) == 2


# --------------------------------------------------------------------------- #
# It stays quiet -- the half that decides whether anyone keeps it              #
# --------------------------------------------------------------------------- #

def test_an_UNBUILT_proposal_naming_files_it_would_create_is_NOT_a_violation(tmp_path: Path):
    """17 atoms in the live map are exactly this. Refusing them would make the map unable to
    describe work that has not happened yet, which is most of what a maturity map is for."""
    text = _map("""
        - id: B10_competitor_switching_response
          level_current: 0
          level_target: 3
          loop_stage: idle
          file_scope: ["sim/competitor_field.py", "tests/sim/test_competitor_switching.py"]
        """)

    assert ser.violations(text, root=tmp_path, tracked=frozenset()) == []


def test_an_atom_with_no_file_scope_at_all_is_not_a_violation(tmp_path: Path):
    text = _map("""
        - id: A
          level_current: 3
          file_scope: []
        """)

    assert ser.violations(text, root=tmp_path, tracked=frozenset()) == []


def test_a_DIRECTORY_scope_counts_as_present(tmp_path: Path):
    """`site/harness/` and `company/carbon` are directories, and several atoms scope that way."""
    (tmp_path / "site" / "harness").mkdir(parents=True)
    text = _map("""
        - id: A
          level_current: 2
          file_scope: ["site/harness/"]
        """)

    assert ser.violations(text, root=tmp_path,
                          tracked=frozenset({"site/harness/index.html"})) == []


# --------------------------------------------------------------------------- #
# The parser -- where this control's own fail-silent hole was                  #
# --------------------------------------------------------------------------- #

def test_the_parser_agrees_with_yaml_on_every_atom():
    """THE TEST THAT KILLED THE FIRST IMPLEMENTATION, kept because it is the only thing that
    would have caught it.

    The first draft read the map with regexes to avoid a third-party import inside a hook.
    Cross-checked against yaml on the real file it disagreed on FOUR records: a trailing
    `# comment` after `level_current: 1` defeated the scalar match, and an inline list wrapped
    across lines yielded an EMPTY file_scope -- and an empty scope means "nothing to check", so
    three atoms would have been silently exempt from the control on its first day. Every other
    test in this file passed throughout.
    """
    text = (REPO / "docs" / "design" / "maturity_map.yaml").read_text(encoding="utf-8")
    mine = {a["id"]: (a["level_current"], sorted(a["file_scope"])) for a in ser.parse_atoms(text)}
    truth = {a["id"]: (a.get("level_current"), sorted(a.get("file_scope") or []))
             for a in yaml.safe_load(text) if isinstance(a, dict) and a.get("id")}

    assert set(mine) == set(truth), "the parser sees a different set of atoms than yaml does"
    disagreeing = {k: (mine[k], truth[k]) for k in truth if mine[k] != truth[k]}
    assert not disagreeing, f"parser disagrees with yaml on: {disagreeing}"


def test_an_UNPARSEABLE_map_FAILS_rather_than_passing(tmp_path: Path, monkeypatch):
    """R15 fail-silent: an unavailable check has FAILED, not succeeded. A control that returns
    0 when it could not read its subject is the most expensive kind of green."""
    broken = tmp_path / "maturity_map.yaml"
    broken.write_text("- id: A\n  file_scope: [unclosed\n", encoding="utf-8")
    monkeypatch.setattr(ser, "MAP_PATH", broken)

    assert ser.main() == 1


def test_a_MISSING_map_FAILS_rather_than_passing(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ser, "MAP_PATH", tmp_path / "not-here.yaml")

    assert ser.main() == 1


# --------------------------------------------------------------------------- #
# The live tree, and the wiring                                                #
# --------------------------------------------------------------------------- #

def test_the_LIVE_map_is_clean(capsys: pytest.CaptureFixture):
    """No frozen baseline exists, so this is the whole ratchet: the tree is at zero and any
    regression shows up here as well as in the hook."""
    assert ser.main() == 0, capsys.readouterr().err


def test_the_ratchet_is_WIRED_into_the_pre_commit_hook():
    """A control nobody runs is a file. E2's own control sat red for four days for exactly
    this reason -- it was outside every recent commit's path selection."""
    hook = (REPO / "tools" / "git-hooks" / "pre-commit").read_text(encoding="utf-8")

    assert "tools.scope_evidence_ratchet" in hook, (
        "the ratchet is not run by the hook, so it protects nothing"
    )


# --------------------------------------------------------------------------- #
# Not in git -- the kind the live tree taught this control on its first run    #
# --------------------------------------------------------------------------- #

def test_evidence_ON_DISK_but_NEVER_COMMITTED_is_refused_and_named_as_ITS_OWN_kind(
    tmp_path: Path,
):
    """THE FIRST THING THIS CONTROL FOUND, and it was not the thing it was written for.

    Run against the working directory it was clean. Run inside the pre-commit extract -- which
    is built from git objects, not from disk -- it refused `PB2_opening_book_won_not_assigned`
    at L3 for `docs/design/PB2_INVERSION_BUILD.md`: a completed build record, sitting on disk,
    never committed. Its own sibling `PB2_JOIN_KEY_BUILD.md` was in git; this one was not.

    That is WORSE than a deleted path, not a false positive -- an L3 claim whose evidence dies
    with one working tree -- and this repo already tracks the class as
    `uncommitted_and_orphaned_work`. But "missing" is the wrong word for a file you can open,
    and would send a reader hunting a deletion that never happened. Two kinds, two sentences,
    both refusing.
    """
    (tmp_path / "committed.md").write_text("in git\n")
    (tmp_path / "on_disk_only.md").write_text("never committed\n")
    text = _map("""
        - id: PB2_opening_book_won_not_assigned
          level_current: 3
          file_scope: ["committed.md", "on_disk_only.md"]
        """)

    bad = ser.violations(text, root=tmp_path, tracked=frozenset({"committed.md"}))

    assert bad == [("PB2_opening_book_won_not_assigned", 3, "on_disk_only.md", ser.UNCOMMITTED)]


def test_a_DIRECTORY_scope_is_in_git_when_any_tracked_file_lives_under_it(tmp_path: Path):
    """`git ls-files` lists files, never directories, so a naive membership test would call
    every directory scope uncommitted -- and `site/harness/`, `company/carbon` and a dozen
    others are directory scopes on claimed levels. That failure mode is loud rather than
    silent, but it would have made the control unusable on its first day."""
    (tmp_path / "site" / "harness").mkdir(parents=True)
    text = _map("""
        - id: A
          level_current: 2
          file_scope: ["site/harness/", "site/harness"]
        """)

    assert ser.violations(text, root=tmp_path,
                          tracked=frozenset({"site/harness/index.html"})) == []


def test_when_git_CANNOT_be_asked_the_check_degrades_to_existence_and_claims_nothing_more(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """FAIL-SILENT, carefully: an unreadable git is not evidence that a file is uncommitted.

    Asserting `UNCOMMITTED` when the probe failed would manufacture a defect out of a broken
    subprocess, and this control's whole value is that its refusals are believable. So the
    git half switches off and the existence half -- which needs no git -- keeps running.
    """
    (tmp_path / "here.md").write_text("x\n")
    monkeypatch.setattr(ser, "_tracked_paths", lambda root: None)
    text = _map("""
        - id: A
          level_current: 3
          file_scope: ["here.md", "gone.md"]
        """)

    bad = ser.violations(text, root=tmp_path)

    assert bad == [("A", 3, "gone.md", ser.DELETED)], (
        "a failed git probe either invented an uncommitted finding or suppressed a real deletion"
    )
