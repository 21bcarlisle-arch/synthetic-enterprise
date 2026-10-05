"""C29: the retention guard can weigh the value it protects by the household's own engagement.

The defect each leg names: a guard that pays a discount to an account that will not look at all is
a transfer, and an estimate that read the anniversary it is deciding (or anything later) would be
look-ahead the supplier does not have.
"""
from __future__ import annotations

import dataclasses

from company.crm.engagement_estimate import engagement_at, value_protected
from company.policy.decision_policy import CURRENT_POLICY, NAIVE_POLICY, VALUE_ARM_POLICY

YEAR = 365


def _term(cid: str, start: str, kind: str) -> dict:
    return {"customer_id": cid, "commodity": "electricity", "term_start": start, "tariff_type": kind}


def _book() -> tuple[list[dict], dict[str, str]]:
    """Two direct-debit accounts with opposite records over three anniversaries."""
    terms = []
    for cid, kind in (("A", "fixed"), ("B", "svt")):
        terms.append(_term(cid, "2016-01-01", "fixed"))
        for y in (2017, 2018, 2019):
            terms.append(_term(cid, f"{y}-01-01", kind))
    return terms, {"A": "direct_debit", "B": "direct_debit"}


def _at(cid, as_of, terms, channels, departures=()):
    return engagement_at(cid, as_of, terms=terms, departures=list(departures),
                         channel_by_account=channels, fuel="electricity", contract_length_days=YEAR)


def test_the_weighting_can_both_refuse_and_keep_an_offer():
    """The partition first: a guard that refused everything would pass every other leg."""
    low, high = 0.05, 0.9
    cost = 40.0
    assert 100.0 + 20.0 > cost
    assert value_protected(100.0, 20.0, low) <= cost
    assert value_protected(100.0, 20.0, high) > cost
    assert value_protected(100.0, 20.0, None) == 100.0 + 20.0


def test_an_engaged_record_weighs_more_than_a_rolled_one():
    terms, channels = _book()
    a = _at("A", "2020-01-01", terms, channels)
    b = _at("B", "2020-01-01", terms, channels)
    assert a.anniversaries == b.anniversaries == 3
    assert a.estimate > b.estimate


def test_the_anniversary_being_decided_and_later_history_are_not_read():
    terms, channels = _book()
    # On 2019-01-01 the 2019 term row may already be written: it must not count.
    before = _at("A", "2019-01-01", terms, channels)
    assert before.anniversaries == 2
    later = terms + [_term("A", "2020-01-01", "svt"), _term("A", "2021-01-01", "svt")]
    assert _at("A", "2019-01-01", later, channels) == before


def test_a_departure_counts_only_once_it_has_happened():
    terms, channels = _book()
    terms = [t for t in terms if not (t["customer_id"] == "B" and t["term_start"] >= "2019")]
    gone = [{"customer_id": "B", "commodity": "electricity", "event_date": "2019-01-01",
             "event_type": "churned", "departure_occasion": "renewal"}]
    assert _at("B", "2019-01-01", terms, channels, gone).chose == 0
    after = _at("B", "2019-06-01", terms, channels, gone)
    assert after.chose == 1 and after.anniversaries == 3


def test_no_book_and_no_channel_give_no_estimate_rather_than_an_invented_one():
    terms, channels = _book()
    assert _at("A", "2016-06-01", terms, channels) is None
    assert _at("Z", "2020-01-01", terms, channels) is None


def test_the_other_fuel_is_not_read():
    terms, channels = _book()
    gas = [dict(t, commodity="gas") for t in terms]
    assert _at("A", "2020-01-01", gas, channels) is None


def test_no_standing_policy_weighs_engagement_so_no_run_moves_until_an_arm_asks():
    for policy in (CURRENT_POLICY, NAIVE_POLICY, VALUE_ARM_POLICY):
        assert policy.retention_weighs_engagement is False
    assert dataclasses.replace(CURRENT_POLICY, retention_weighs_engagement=True).retention_weighs_engagement
