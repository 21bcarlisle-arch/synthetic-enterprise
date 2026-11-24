"""A guard that scans a whole folder is selected for a change to any file in it.

ITS DEFECT: on 24 Nov 2026 two reds reached origin with green receipts. 6bdfe9c85 added
`MEDIA_SWITCHING_COUPLING_RANGE` to simulation/activation_energy.py with no anchor, and 7fe0e91d2
archived a director steer to docs/staging/advisor/done/ with no `Decision:` line. Each guard reads
its subject by scanning a folder, so the gate's stem, import and data-surface edges never reached
it, and `select_targets` ran 18 and 31 other tests instead.

MUTATIONS (2026-11-24, each applied and reverted): empty `SCAN_SUBJECT_TESTS` -> 3 red (both
selections and the scope agreement); drop the `scan_subject_tests` union from `select_targets` -> 2
red (both selections); `scan_subject_tests` ignores the suffix -> 1 red (the README).
"""
from __future__ import annotations

from background import director_concerns
from tools import pre_commit_test_gate as gate
from tools import world_constant_anchors

WORLD = "tests/architecture/test_a_world_constant_cites_its_anchor_or_is_a_labelled_range.py"
CONCERNS = "tests/background/test_director_concerns.py"


def test_a_NEW_world_file_selects_the_world_constant_scan():
    """No file of this name exists, so nothing but the folder can reach the guard."""
    for package in world_constant_anchors.SCOPE:
        assert WORLD in gate.select_targets([f"{package}/a_file_no_edge_reaches.py"]), package


def test_an_archived_steer_selects_the_decision_code_guard():
    path = f"{director_concerns.ADVISOR_DONE_REL}/DIRECTOR_STEER_A_NEW_ONE_2026-11-24.md"
    assert CONCERNS in gate.select_targets([path])


def test_the_declared_folders_are_the_scans_own():
    """Keyed to the property: the declaration covers exactly the folders each guard reads."""
    keys = set(gate.SCAN_SUBJECT_TESTS)
    for package in world_constant_anchors.SCOPE:
        assert (f"{package}/", ".py") in keys
    assert (f"{director_concerns.ADVISOR_DONE_REL}/DIRECTOR_", ".md") in keys
    for (_, _), tests in gate.SCAN_SUBJECT_TESTS.items():
        assert all((gate.ROOT / t).exists() for t in tests), tests


def test_a_file_the_scan_does_not_read_selects_nothing_from_it():
    """The rare branch: the folder match is not a catch-all."""
    assert gate.scan_subject_tests("simulation/README.md") == []
    assert gate.scan_subject_tests("docs/staging/advisor/STEER_NOT_DONE.md") == []
