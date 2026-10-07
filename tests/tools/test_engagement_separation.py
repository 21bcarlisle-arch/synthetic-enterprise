"""The published PB4 reading is what the world at this commit produces, and it can fail.

The feed is written by hand (`python3 -m tools.engagement_separation --write`), not by the publish
path, so the defect to guard is the world moving under a committed page: an archetype share, a
channel anchor or the elasticity draw changes and `site/data/engagement_separation.json` goes on
showing the old book. Keyed to the PROPERTY -- re-measure and compare -- never to today's figures.
"""
from __future__ import annotations

import json

import pytest

from tools import engagement_separation as es


@pytest.fixture(scope="module")
def measured() -> dict:
    return es.measure()


def test_the_published_reading_is_what_the_world_at_this_commit_produces(measured):
    published = json.loads(es.OUT_PATH.read_text(encoding="utf-8"))
    stale = [k for k in es.MEASURED_KEYS if published.get(k) != measured[k]]
    assert not stale, (
        f"site/data/engagement_separation.json no longer matches the world in {stale}; re-run "
        "`python3 -m tools.engagement_separation --write` and commit the feed with the change "
        "that moved it")


def test_every_engagement_group_is_reached_and_the_rare_count_can_be_nonzero(measured):
    """The partition control: every archetype and every channel the world draws has households on
    the book, and the headline's count is reachable rather than structurally zero."""
    from simulation.household_segments import EngagementLevel, PaymentChannel

    assert {g["archetype"] for g in measured["by_archetype"]} == {e.value for e in EngagementLevel}
    assert {g["channel"] for g in measured["by_channel"]} == {c.value for c in PaymentChannel}
    d = measured["disengaged_but_price_sensitive"]
    assert 0 < d["above_book_mean_elasticity"] < d["disengaged"]


def test_the_engagement_column_is_the_worlds_and_not_the_bare_archetype(measured):
    """DEFECT: reading the archetype alone drops the payment-channel half, which is the only part a
    supplier can observe. Within one archetype, channels must differ in mean engagement."""
    by_channel = {g["channel"]: g["engagement_mean"] for g in measured["by_channel"]}
    assert by_channel["prepayment"] < by_channel["direct_debit"]


def test_a_correlated_draw_would_leave_the_null(monkeypatch):
    """Anti-tautology arm: if elasticity were a function of engagement, the reading must say the
    association is outside the shuffle null. Without this, `outside_the_null: False` is
    unfalsifiable."""
    from simulation import household_segments as hs

    real = es.true_traits

    def coupled(ids):
        _, seed = real(ids)
        return {c: 0.2 + hs.active_renewal_probability_for_customer(c) for c in ids}, seed

    monkeypatch.setattr(es, "true_traits", coupled)
    assert es.measure()["association"]["outside_the_null"] is True


def test_the_bill_shock_gap_is_published_while_the_world_carries_none():
    from simulation import household_segments as hs

    block = es.build()["bill_shock_amplitude"]
    assert block["established"] is (hs.BILL_SHOCK_ENGAGEMENT_MULTIPLIER is not None)
    if not block["established"]:
        assert block["gap"] and block["code_gap"] == hs.BILL_SHOCK_ENGAGEMENT_GAP


def _row(cid: str, diff, churned: bool, p: float = 0.1) -> dict:
    return {"customer_id": cid, "price_differential_vs_market_reference": diff,
            "event_type": "churned" if churned else "renewed", "realized_churn_probability": p}


def test_every_saving_band_can_be_reached_and_a_thin_cell_is_refused_a_rate():
    """PB4 D4. The partition control first: one decision per band lands in that band and no other,
    so no band is structurally empty. Then the refusal: below MIN_CELL a cell carries no rate,
    and at MIN_CELL it does -- a cell that never prints a rate passes every 'too few' check."""
    bands = es.looked_by_saving([_row("A", d, False) for d in (-0.02, 0.03, 0.10, 0.30)])
    assert [b["n"] for b in bands] == [1] * 4
    assert all(b["world_probability_mean"] is None for b in bands)

    cell = es.looked_by_saving([_row("A", 0.10, i < 3, 0.2) for i in range(es.MIN_CELL)])[2]
    assert cell["world_probability_mean"] == 0.2 and cell["left"] == 3
    lo, hi = cell["left_ci95"]
    assert lo < 0.3 < hi


def test_both_routes_are_counted_per_archetype_and_only_for_the_book():
    """DEFECT: the renewal roll alone holds almost only households that LOOKED, so a per-archetype
    reading over it measures leaving-given-looking. The default-tariff route must be counted too,
    and a household not on the resi book (an SME, an unknown id) must not be."""
    renewals = [_row("A", 0.0, True, 0.4), _row("SME1", 0.0, True, 0.9)]
    svt = [{"customer_id": "D", "event_type": "churned", "realized_churn_probability": 0.03,
            "sim_segment_days": 365.25},
           {"customer_id": "D", "event_type": "stayed", "realized_churn_probability": 0.03,
            "sim_segment_days": 365.25}]
    rows = {g["archetype"]: g for g in es.by_archetype_both_routes(
        renewals, svt, {"A": "active", "D": "disengaged"})}
    assert rows["active"]["renewal_roll"]["n"] == 1 and rows["active"]["svt_left"] == 0
    assert rows["disengaged"]["svt_left"] == 1 and rows["disengaged"]["svt_years"] == 2.0
    assert rows["disengaged"]["expected_left_per_household"] == 0.06
    assert rows["passive"]["households"] == 0


def test_a_missing_capture_is_an_absence_with_its_reason(monkeypatch, tmp_path):
    monkeypatch.setattr(es, "CAPTURE_PATH", tmp_path / "absent.json")
    block = es.emerged()
    assert block["available"] is False and "no world capture" in block["reason"]
