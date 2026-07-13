"""Tests for simulation/segment_debt_obligation.py -- the WORLD ground truth
(answer key) for atom W2_9_segment_debt_tnc.

Covers: the correct per-segment obligation, the LPCDCA statutory-rate history,
the fail-closed edges, and the deterministic segment-OBSERVATION channel that
creates the coupled gap against C11.
"""
from datetime import date

import pytest

from simulation import segment_debt_obligation as w29


# ---------------------------------------------------------------------------
# Correct obligation per segment (the answer key)
# ---------------------------------------------------------------------------

def test_business_gets_statutory_interest_and_late_charges():
    for seg in ("sme", "iandc", "i&c", "microbusiness"):
        ob = w29.correct_obligation(seg, date(2023, 3, 15))
        assert ob.terms_class == w29.BUSINESS_TERMS
        assert ob.statutory_interest_lawful is True
        assert ob.late_charge_lawful is True
        assert ob.payment_conditioned_tariff_lawful is True
        assert ob.statutory_interest_rate is not None


def test_domestic_gets_neither_interest_nor_late_charge():
    for seg in ("resi", "residential", "domestic", "household"):
        ob = w29.correct_obligation(seg, date(2023, 3, 15))
        assert ob.terms_class == w29.DOMESTIC_TERMS
        assert ob.statutory_interest_lawful is False
        assert ob.late_charge_lawful is False
        assert ob.statutory_interest_rate is None
        # DD-discount / good-payer gating stays lawful for domestic too.
        assert ob.payment_conditioned_tariff_lawful is True


def test_unrecognised_segment_fails_closed():
    with pytest.raises(ValueError):
        w29.correct_obligation("gold_tier", date(2023, 3, 15))
    with pytest.raises(ValueError):
        w29.correct_obligation(None, date(2023, 3, 15))


def test_as_of_must_be_a_date():
    with pytest.raises(TypeError):
        w29.correct_obligation("sme", "2023-03-15")


# ---------------------------------------------------------------------------
# Statutory-rate history (LPCDCA = BoE base on the reference date + 8pts)
# ---------------------------------------------------------------------------

def test_statutory_rate_matches_real_anchors():
    # base 3.50% @31Dec2022 -> 11.50% for H1 2023.
    assert w29.statutory_interest_rate(date(2023, 3, 1)) == pytest.approx(0.1150)
    # base 0.10% @30Jun2020 -> 8.10% for H2 2020 (near-zero-base-rate era).
    assert w29.statutory_interest_rate(date(2020, 9, 1)) == pytest.approx(0.0810)
    # base 0.50% @31Dec2015 -> 8.50% for H1 2016.
    assert w29.statutory_interest_rate(date(2016, 3, 1)) == pytest.approx(0.0850)


def test_rate_moves_across_the_window_not_one_hardcoded_value():
    rates = {w29.statutory_interest_rate(date(y, 3, 1)) for y in range(2016, 2026)}
    # The rate genuinely varies across the modelled span (not a single value).
    assert len(rates) > 3


def test_rate_fails_closed_outside_anchored_history():
    assert w29.statutory_interest_rate(date(2015, 1, 1)) is None
    assert w29.statutory_interest_rate(date(2030, 1, 1)) is None


def test_lpcdca_margin_is_eight_points():
    assert w29.LPCDCA_MARGIN == 0.08
    assert w29.LPCDCA_EFFECTIVE_FROM == date(1998, 11, 1)


def test_statutory_interest_amount_business_vs_domestic():
    biz = w29.correct_obligation("sme", date(2023, 3, 15))
    # 1000 GBP overdue 365 days at 11.50% -> ~115.00.
    assert biz.statutory_interest_due(1000.0, 365) == pytest.approx(115.0, abs=0.5)
    dom = w29.correct_obligation("resi", date(2023, 3, 15))
    assert dom.statutory_interest_due(1000.0, 365) == 0.0
    # No accrual on a zero balance / zero days.
    assert biz.statutory_interest_due(0.0, 365) == 0.0
    assert biz.statutory_interest_due(1000.0, 0) == 0.0


# ---------------------------------------------------------------------------
# Segment-observation channel (the wall: what the company records, deterministic)
# ---------------------------------------------------------------------------

def test_observed_segment_is_deterministic():
    a = w29.observed_segment("sme", "CUST-001")
    b = w29.observed_segment("sme", "CUST-001")
    assert a == b


def test_observed_segment_usually_correct_but_sometimes_misrecorded():
    # Over a population, SOME microbusinesses land on a domestic record.
    obs = [w29.observed_segment("sme", f"S{i:05d}") for i in range(2000)]
    n_domestic = sum(1 for o in obs if o == "resi")
    # Non-zero (mislabels happen) but a small minority (most are correct).
    assert 0 < n_domestic < len(obs) * 0.25


def test_observed_domestic_mostly_stays_domestic():
    obs = [w29.observed_segment("resi", f"D{i:05d}") for i in range(2000)]
    n_business = sum(1 for o in obs if o in ("sme", "iandc"))
    assert 0 < n_business < len(obs) * 0.10


def test_observed_segment_rejects_unknown():
    with pytest.raises(ValueError):
        w29.observed_segment("gold_tier", "X1")


def test_true_terms_class_dispatch():
    assert w29.true_terms_class("resi") == w29.DOMESTIC_TERMS
    assert w29.true_terms_class("sme") == w29.BUSINESS_TERMS
    assert w29.true_terms_class("iandc") == w29.BUSINESS_TERMS
    assert w29.is_business_segment("sme") is True
    assert w29.is_business_segment("resi") is False
