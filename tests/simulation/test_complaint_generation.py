"""W2_37: complaints come from the triggers the world produced, and the silent unhappy are their own population."""
import random

import pytest

from simulation.complaint_generation import (
    CAUSE_SHARE,
    NEAREST_ANCHOR_GAP,
    CalibrationRefused,
    complaint_probability_given_trigger,
    complaints_per_account_quarter,
    draw_complaints,
    draw_silent_unhappy,
    silent_unhappy_probability,
)
from simulation.complaint_generation import (
    ComplaintCause as C,
)

PERIOD = "2025Q4"


def _book(n=60_000, seed=37):
    """A synthetic book whose trigger rates differ by cause, as a real world's would."""
    rates = {c: 0.02 + 0.01 * i for i, c in enumerate(C)}
    rng = random.Random(seed)
    book = {f"H{i}": {c for c in C if rng.random() < rates[c]} for i in range(n)}
    prevalence = {c: sum(c in t for t in book.values()) / n for c in C}
    return book, prevalence


def test_the_book_reproduces_the_published_rate_and_cause_mix_whatever_the_world_trigger_rates():
    """Defect: per-trigger probabilities picked, not derived, so the complaint count follows the
    world's trigger rates instead of the published record (the 3% + 35pp roll this replaces)."""
    book, prevalence = _book()
    p = complaint_probability_given_trigger(PERIOD, prevalence)
    counts = {c: 0 for c in C}
    for hid, met in book.items():
        for c in draw_complaints(hid, PERIOD, met, p):
            counts[c] += 1
    total = sum(counts.values())
    assert total / len(book) == pytest.approx(complaints_per_account_quarter(PERIOD).value, rel=0.1)
    billing = sum(counts[c] for c in (C.CATCH_UP_BILL, C.DISPUTED_USAGE, C.DISPUTED_BALANCE,
                                      C.OTHER_BILLING)) / total
    assert billing == pytest.approx(0.38 / 1.18, abs=0.05)


def test_a_household_that_met_only_a_billing_failure_can_complain_and_one_that_met_nothing_cannot():
    """Defect: complaints keyed to a price rise alone, so a catch-up bill with no rate change
    never produces one (communications_sentiment_and_nps.md §6.1)."""
    _, prevalence = _book()
    p = complaint_probability_given_trigger(PERIOD, prevalence)
    fired = [hid for hid in (f"X{i}" for i in range(5_000))
             if draw_complaints(hid, PERIOD, {C.CATCH_UP_BILL}, p)]
    assert fired, "no household complained about a catch-up bill alone"
    assert all(draw_complaints(f"Y{i}", PERIOD, set(), p) == [] for i in range(5_000))
    assert C.PRICE_RISE not in {c for hid in fired for c in draw_complaints(hid, PERIOD,
                                                                            {C.CATCH_UP_BILL}, p)}


def test_the_calibration_both_accepts_and_refuses_and_a_refusal_names_its_cause():
    _, prevalence = _book()
    accepted = complaint_probability_given_trigger(PERIOD, prevalence)
    too_rare = {**prevalence, C.CATCH_UP_BILL: 1e-6}
    missing = {c: v for c, v in prevalence.items() if c is not C.METER}
    with pytest.raises(CalibrationRefused, match="catch_up_bill"):
        complaint_probability_given_trigger(PERIOD, too_rare)
    with pytest.raises(CalibrationRefused, match="meter"):
        complaint_probability_given_trigger(PERIOD, missing)
    assert accepted and all(0 < v <= 1 for v in accepted.values())


def test_the_silent_unhappy_never_complained_and_complaints_stay_a_floor_on_dissatisfaction():
    """Defect: dissatisfaction built around complaints, so the unhappy who never complain are
    invisible (director's ruling, 2026-10-05)."""
    book, prevalence = _book()
    p = complaint_probability_given_trigger(PERIOD, prevalence)
    complained = {hid for hid, met in book.items() if draw_complaints(hid, PERIOD, met, p)}
    uncomplained = sum(1 for hid, met in book.items() if met and hid not in complained) / len(book)
    badly_handled = 0.57 * 4 * len(complained) / len(book)   # a year of quarters like this one
    q = silent_unhappy_probability(PERIOD, badly_handled, uncomplained)
    silent = {hid for hid, met in book.items()
              if draw_silent_unhappy(hid, PERIOD, bool(met), hid in complained, q)}
    assert silent and not silent & complained
    assert all(book[hid] for hid in silent)
    assert (len(silent) / len(book) + badly_handled) == pytest.approx(0.06, rel=0.1)
    assert len(silent) > len(complained)


def test_the_silent_unhappy_derivation_refuses_when_complaints_would_exceed_dissatisfaction():
    assert 0 < silent_unhappy_probability(PERIOD, 0.02, 0.4) < 1
    with pytest.raises(CalibrationRefused, match="floor"):
        silent_unhappy_probability(PERIOD, 0.07, 0.4)
    with pytest.raises(CalibrationRefused, match="did not complain"):
        silent_unhappy_probability(PERIOD, 0.0, 0.01)


def test_an_unpublished_quarter_carries_its_gap_and_a_published_one_does_not():
    """Defect: the 2016-2024 anchor read as established when it is 2025's figure standing in."""
    assert complaints_per_account_quarter("2025-11-15").basis == "published"
    gap = complaints_per_account_quarter("2022-10-01")
    assert gap.basis == NEAREST_ANCHOR_GAP and gap.period == "2025Q4"
    assert sum(CAUSE_SHARE.values()) == pytest.approx(1.0)
