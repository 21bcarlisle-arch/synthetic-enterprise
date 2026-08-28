"""The fidelity door's derived qualifier — `tools/generate_fidelity_data.py`.

SCOPE, STATED PLAINLY: this file covers ONE function. `generate_fidelity_data.py` had no tests at
all before 2026-08-28, and this is not an attempt to close that — it is the coverage owed by a
single change, and the wider gap is recorded in
`docs/staging/WORKER_FINDING_THE_PUBLISHED_HEADLINE_SAID_THE_ARM_EARNED_MORE_WHILE_IT_EARNED_LESS_2026-08-28.md`
rather than left implied by an empty directory.

WHY THE CHANGE. The MAE reading published "structural model beats best-of-naive-family in ONLY
N/M years" with `only` as a constant beside a computed count. True at the 4/10 it was written
against, and it would have published "in only 9/10 years" without anything failing. A judgement
word that cannot change when its evidence changes is the same defect as a directional clause that
cannot — the class found in the value-arms headline the same day, and this instance was found by
sweeping for it.
"""
from __future__ import annotations

import pytest

from tools.generate_fidelity_data import _beat_qualifier


def test_a_minority_of_years_reads_as_only():
    """The state the sentence was written against, which must still read the same way."""
    assert _beat_qualifier(4, 10) == "only "


def test_a_strong_majority_does_NOT_read_as_only():
    """THE DEFECT. Fires on: a constant `only`, which would publish a good result as a poor one."""
    assert "only" not in _beat_qualifier(9, 10)
    assert "only" not in _beat_qualifier(10, 10)
    assert _beat_qualifier(9, 10) == "a clear "


def test_the_middle_band_makes_no_claim():
    """A qualifier is a claim, and the honest thing at a near-tie is to make none.

    Fires on: a two-branch qualifier that must call every result either poor or clear.
    """
    assert _beat_qualifier(5, 10) == ""
    assert _beat_qualifier(6, 10) == ""


def test_the_qualifier_turns_at_the_stated_thresholds():
    """The boundaries are part of the claim, so they are pinned rather than left to drift."""
    assert _beat_qualifier(49, 100) == "only "
    assert _beat_qualifier(50, 100) == ""
    assert _beat_qualifier(79, 100) == ""
    assert _beat_qualifier(80, 100) == "a clear "


def test_an_empty_window_makes_no_claim_and_does_not_divide():
    """FAIL-OPEN killer at the degenerate end: zero years must not raise, and must not be
    described as either poor or clear."""
    assert _beat_qualifier(0, 0) == ""


@pytest.mark.parametrize("beaten,total", [(0, 10), (10, 10), (1, 3), (3, 3)])
def test_the_qualifier_is_always_a_prefix_that_reads_as_english(beaten, total):
    """The value is concatenated straight in front of "N/M years", so it must either be empty or
    end in a space. Fires on: a qualifier that renders as "aclear8/10 years"."""
    q = _beat_qualifier(beaten, total)
    assert q == "" or q.endswith(" ")
    assert q.strip() in ("", "only", "a clear")
