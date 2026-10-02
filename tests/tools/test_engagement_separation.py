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
