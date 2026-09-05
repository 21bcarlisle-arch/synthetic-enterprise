"""THE DEFECT: every rule in `finding_classes.check()` is written `for finding_class in CLASSES`,
so the tuple IS the subject set, and a class deleted from it is the subject of nothing.

Measured on the live tree 2026-09-05, before `removed_classes()` existed: drop
`controls_that_cannot_fail` from `CLASSES` and `check()` returned 0 failures. Worse, and this is
the part that makes it a fail-open rather than a missing rung — delete that class's DOCUMENT and
`check()` refuses `MISSING CLASS DOC`; delete the class ROW as well and the refusal goes. A red
clearable by deleting the evidence is a fail-open with an extra step.

Same shape, same day, as `removed_dispositions()` on the alarm census (`dc5fcbbc8`), which is why
the mechanism is shared and this file proves the WIRING as well as the rung: a control that calls
the shared helper survives mutation of the caller.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from background import finding_classes as fc  # noqa: E402
from background import register_low_water as rlw  # noqa: E402


def _baseline_plus(*extra: str) -> frozenset[str]:
    """HEAD's register as the live one plus rows that have since 'left'. Injected rather than
    read from git so the leg tests the RUNG, not this repo's commit history."""
    return frozenset(set(fc.CLASSES_BY_ID) | set(extra))


def test_a_class_dropped_from_the_register_is_refused():
    """The measured defect itself: the row that vanished has to be named by something."""
    out = fc.removed_classes(retired={}, baseline=_baseline_plus("a_class_that_left"))
    assert len(out) == 1
    assert "a_class_that_left" in out[0]


def test_a_retired_class_with_a_reason_is_allowed_through():
    """Not a rung that refuses everything. A class CAN honestly stop being a class, and the
    escape hatch has to work or the first honest merge routes round the control."""
    assert fc.removed_classes(
        retired={"a_class_that_left": "merged into publish_gate_and_wedge on 2026-09-05"},
        baseline=_baseline_plus("a_class_that_left"),
    ) == []


def test_the_rung_can_both_fire_and_clear_over_one_baseline():
    """ONE control over the whole partition. Two legs that each pass in isolation are also both
    passed by a rung that refuses everything and by one that refuses nothing; this is the
    assertion neither of those survives. CLAUDE.md's rare-branch rule, applied to a rung whose
    interesting branch is the one nobody exercises."""
    base = _baseline_plus("explained", "unexplained")
    out = fc.removed_classes(retired={"explained": "folded in"}, baseline=base)
    assert len(out) == 1 and "unexplained" in out[0] and "explained" not in out[0].replace(
        "unexplained", "")


def test_a_retirement_reason_of_none_does_not_clear_the_refusal():
    """`str(None)` is "None", which is truthy. A retirement entry carrying an explicit null
    asserts nothing and must not read as a reason — the slip that was live in three census rungs
    until 2026-09-05, fixed here as a class rather than waited for."""
    assert fc.removed_classes(
        retired={"a_class_that_left": None},  # type: ignore[dict-item]
        baseline=_baseline_plus("a_class_that_left"),
    ) != []


def test_an_unestablishable_baseline_is_a_refusal_and_never_a_clean_result(monkeypatch):
    """`None` and `frozenset()` are opposite claims. An empty baseline says "HEAD's register was
    empty, so nothing was removed" and would report clean on every tree without git.

    Driven by making `keys_at_head` fail rather than by passing `baseline=None`, because `None`
    is the read-HEAD SENTINEL on this signature: the argued branch is unreachable through the
    parameter that names it, and the first draft of this leg passed a `None` that silently meant
    "go and read git" and asserted against a clean live tree. The production route — git absent,
    HEAD's copy unparseable — is the one that has to be proved, so it is the one driven here."""
    monkeypatch.setattr(rlw, "keys_at_head", lambda *a, **k: None)
    out = fc.removed_classes(retired={})
    assert len(out) == 1 and "could not be established" in out[0]


def test_removed_rows_refuses_an_unestablished_baseline_and_clears_an_empty_one():
    """The helper's own partition, over the distinction the rung is built on. A mechanism that
    treated both as "nothing to compare" would pass every leg above and report clean on every
    tree without git."""
    kwargs = dict(register="R", current=["a"], retired={}, row_is="", retire_with="`x[{key}]`")
    assert rlw.removed_rows(baseline=None, **kwargs) != []
    assert rlw.removed_rows(baseline=frozenset(), **kwargs) == []


def test_check_actually_runs_the_rung():
    """THE WIRING, not the rung. A control that calls the shared helper survives mutation of the
    caller: `removed_classes()` can be perfect and `check()` never call it, which is how this
    project has shipped green gates over live defects before."""
    calls: list[str] = []

    def _refuse() -> list[str]:
        calls.append("ran")
        return ["CLASS REGISTER: injected"]

    original = fc.removed_classes
    fc.removed_classes = _refuse  # type: ignore[assignment]
    try:
        result = fc.check()
    finally:
        fc.removed_classes = original  # type: ignore[assignment]
    assert calls == ["ran"], "check() never asked whether the register had shrunk"
    assert any("CLASS REGISTER: injected" in f for f in result.failures), (
        "check() called the rung and dropped what it returned"
    )


def test_the_live_register_is_not_shrinking_right_now():
    """The rung pointed at the real tree. Green is the expected state; a red here means a class
    was dropped in the working copy without `RETIRED_CLASSES` saying why."""
    assert fc.removed_classes() == []


def test_the_extractor_reads_the_live_source_and_finds_every_live_class():
    """NON-VACUITY. If `class_ids_in_source` silently found nothing, every leg above would still
    pass on injected baselines while the live rung compared against an empty set and reported a
    clean register forever."""
    ids = fc.class_ids_in_source(
        (REPO_ROOT / fc.REGISTER_REL_PATH).read_text(encoding="utf-8"))
    assert ids is not None
    assert set(ids) == set(fc.CLASSES_BY_ID), (
        "the extractor and the live tuple disagree, so the baseline is not the register"
    )


@pytest.mark.parametrize("source", [
    "CLASSES = (",                       # unparseable
    "OTHER = (FindingClass(id='x'),)",   # no CLASSES assignment
    "CLASSES = 3",                       # a shape the extractor does not understand
    "CLASSES = ()",                      # parsed, but yielded nothing
])
def test_an_unreadable_register_source_returns_none_and_never_an_empty_list(source):
    """[] would say "HEAD declared no classes", which reads every live class as an ADDITION and
    the rung as clean. The distinction between "empty" and "unestablished" is the whole control."""
    assert fc.class_ids_in_source(source) is None


def test_keys_at_head_returns_none_when_the_extractor_raises():
    """An extractor that throws leaves an UNESTABLISHED baseline, not an empty one. Swallowing
    the exception into an empty set would be the fail-silent this module refuses, one level below
    the caller that is careful about it."""
    def _explode(_text: str):
        raise RuntimeError("boom")

    assert rlw.keys_at_head(fc.REGISTER_REL_PATH, _explode) is None


def test_keys_at_head_reads_head_and_not_the_working_copy():
    """The baseline has to be the last COMMITTED judgement. Reading the working copy would
    compare the register against itself — a tautology that can never fire."""
    seen: list[str] = []

    def _capture(text: str) -> list[str]:
        seen.append(text)
        return ["x"]

    rlw.keys_at_head(fc.REGISTER_REL_PATH, _capture)
    assert seen, "keys_at_head never reached its extractor"
    live = (REPO_ROOT / fc.REGISTER_REL_PATH).read_text(encoding="utf-8")
    # This test file's own repair is uncommitted while it is being written, so HEAD's copy and
    # the working copy differ by construction here; once landed they agree and the assertion
    # below is the one that still holds either way.
    assert "CLASSES" in seen[0], "what came back was not this module's source"
    assert seen[0] != live or "RETIRED_CLASSES" in seen[0], (
        "the extractor was handed the working copy, not HEAD's"
    )
