"""B4_competitor_field (2026-08-24 BUILD, level 0 -> 1): the domestic SVT
ceiling / undercut-pressure signal in company/pricing/renewal_desk.py.

docs/design/simplifications/B4_competitor_field.yaml's FRAME: the world
publishes only an aggregate market-savings signal (never a per-competitor
tariff field), so the honest L1 undercut-pressure input is that aggregate,
handed in as a plain float exactly like published_policy_cost_per_mwh -- and
the ceiling is anchored on the published domestic SVT
(company/pricing/renewal_pricing_engine.py's own CMA-2016 SVT x 1.02
calibration, the first live wiring of it).
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from company.governance.decision_rights import reset_decision_log
from company.pricing.renewal_desk import (
    _apply_competitive_ceiling,
    _competitive_ceiling_gbp_per_mwh,
    quote_renewal,
)


@pytest.fixture(autouse=True)
def _fresh_log():
    reset_decision_log()
    yield
    reset_decision_log()


# ── _competitive_ceiling_gbp_per_mwh: the pure calibration ──────────────────


def test_ceiling_at_baseline_multiplier_is_svt_times_1_02():
    """multiplier == 1.0 is the 2024 new-normal baseline -- no undercut
    pressure beyond renewal_pricing_engine.py's own plain SVT x 1.02 cap."""
    assert _competitive_ceiling_gbp_per_mwh(200.0, 1.0) == 204.0


def test_ceiling_tightens_as_the_savings_signal_rises_above_baseline():
    """More savings available elsewhere (multiplier > 1.0, e.g. 2016's peak
    competition) must produce a LOWER ceiling than the plain SVT x 1.02 cap --
    an undercut-pressure signal that never moves is not a signal."""
    baseline = _competitive_ceiling_gbp_per_mwh(200.0, 1.0)
    pressured = _competitive_ceiling_gbp_per_mwh(200.0, 2.2)  # ~2016
    assert pressured < baseline


def test_ceiling_applies_no_extra_discount_below_baseline():
    """A quiet market (multiplier < 1.0 -- e.g. the 2022 crisis, nowhere
    cheaper to switch to) must NOT tighten the ceiling further: real suppliers
    faced no extra undercut pressure in exactly that regime."""
    assert _competitive_ceiling_gbp_per_mwh(200.0, 0.4) == _competitive_ceiling_gbp_per_mwh(200.0, 1.0)


def test_ceiling_saturates_rather_than_inverting():
    """An extreme savings signal must not push the ceiling below SVT itself --
    it saturates at the documented floor, it does not runaway."""
    ceiling = _competitive_ceiling_gbp_per_mwh(200.0, 50.0)
    assert 194.0 <= ceiling < 200.0


# ── _apply_competitive_ceiling: segment gate, SVT gate, cost floor ──────────


def _apply(unit_rate, **overrides):
    kwargs = dict(
        segment="resi",
        company_fwd=100.0,
        locked_policy=20.0,
        locked_network=30.0,
        published_svt_gbp_per_mwh=200.0,
        published_market_switching_multiplier=1.0,
    )
    kwargs.update(overrides)
    return _apply_competitive_ceiling(unit_rate, **kwargs)


def test_ceiling_binds_when_the_struck_rate_exceeds_it():
    # Struck rate 260 exceeds the ceiling (200 * 1.02 = 204).
    assert _apply(260.0) == 204.0


def test_ceiling_is_a_no_op_when_the_struck_rate_is_already_below_it():
    assert _apply(150.0) == 150.0


def test_ic_and_sme_segments_are_not_on_svt_and_are_unaffected():
    """Real GB SVT is a domestic-only Ofgem protection -- I&C/SME customers
    are never on it, so a struck rate far above the domestic ceiling must
    pass through unchanged for those segments."""
    assert _apply(500.0, segment="I&C") == 500.0
    assert _apply(500.0, segment="SME") == 500.0


def test_no_published_svt_is_a_no_op():
    """Before 2016 (or any date the world has no SVT record for),
    published_svt_gbp_per_mwh is None -- there is no ceiling to enforce, not a
    ceiling of zero."""
    assert _apply(500.0, published_svt_gbp_per_mwh=None) == 500.0


def test_the_ceiling_never_prices_below_the_cost_floor():
    """A genuine wholesale spike (cost floor above the ceiling) must reach its
    full struck rate, or at worst be pulled down to cost -- never below it.
    Matches renewal_pricing_engine.py's own NO_OFFER-preserving shape: an
    undercut ceiling may cost margin, it may never force a sale below cost."""
    # cost_floor = 400 (company_fwd) + 20 + 30 = 450, far above the SVT
    # ceiling (204). The struck rate (900) is pulled down to cost, not to the
    # ceiling below it.
    result = _apply(900.0, company_fwd=400.0)
    assert result == 450.0
    assert result > _competitive_ceiling_gbp_per_mwh(200.0, 1.0)


def test_a_below_cost_floor_struck_rate_is_unaffected():
    """The floor only ever raises the effective cap; it cannot itself lower an
    already-low struck rate below cost (that is COST_PLUS pricing's own
    concern, upstream of this function, and out of scope here)."""
    assert _apply(120.0, company_fwd=400.0) == 120.0


# ── Integration: quote_renewal actually applies it ───────────────────────────


def _records(start: str, end: str, price: float = 300.0) -> list[dict]:
    s, e = date.fromisoformat(start), date.fromisoformat(end)
    out, cur = [], s
    while cur <= e:
        out.append({"settlementDate": cur.isoformat(), "systemSellPrice": price})
        cur += timedelta(days=1)
    return out


def test_quote_renewal_caps_a_resi_offer_at_the_competitive_ceiling():
    ts = date.fromisoformat("2017-06-01")
    offer = quote_renewal(
        customer_id="C_CEIL",
        term_start=ts,
        notice_date=ts - timedelta(days=42),
        tariff_type="fixed",
        segment="resi",
        eac_kwh=2800,
        observable_price_records=_records("2016-01-01", "2018-01-01", 300.0),
        published_policy_cost_per_mwh=25.0,
        published_network_cost_per_mwh=40.0,
        prior_fixed_unit_rate=None,
        fallback_forward_price_gbp_per_mwh=300.0,
        published_svt_gbp_per_mwh=140.0,
        published_market_switching_multiplier=1.0,
    )
    # A high-forward, resi, domestic-SVT-published offer is capped well below
    # what an uncapped cost-plus rate would have struck.
    assert offer.unit_rate_gbp_per_mwh <= max(
        140.0 * 1.02, offer.company_forward_price_gbp_per_mwh + 25.0 + 40.0
    )


def test_quote_renewal_leaves_ic_offers_unaffected_by_the_same_svt():
    ts = date.fromisoformat("2017-06-01")
    resi = quote_renewal(
        customer_id="C_RESI_CMP", term_start=ts, notice_date=ts - timedelta(days=42),
        tariff_type="fixed", segment="resi", eac_kwh=2800,
        observable_price_records=_records("2016-01-01", "2018-01-01", 300.0),
        published_policy_cost_per_mwh=25.0, published_network_cost_per_mwh=40.0,
        prior_fixed_unit_rate=None, fallback_forward_price_gbp_per_mwh=300.0,
        published_svt_gbp_per_mwh=140.0, published_market_switching_multiplier=1.0,
    )
    ic = quote_renewal(
        customer_id="C_IC_CMP", term_start=ts, notice_date=ts - timedelta(days=42),
        tariff_type="fixed", segment="I&C", eac_kwh=2800,
        observable_price_records=_records("2016-01-01", "2018-01-01", 300.0),
        published_policy_cost_per_mwh=25.0, published_network_cost_per_mwh=40.0,
        prior_fixed_unit_rate=None, fallback_forward_price_gbp_per_mwh=300.0,
        published_svt_gbp_per_mwh=140.0, published_market_switching_multiplier=1.0,
    )
    # Same market conditions, same published SVT -- I&C is not on SVT in
    # reality, so it must not be pulled down by a domestic-only ceiling.
    assert ic.unit_rate_gbp_per_mwh > resi.unit_rate_gbp_per_mwh
