"""C29's first BUILD control: the per-account engagement estimate ranks households, by the world's
own trait, better than payment channel alone -- and only when there is a per-account trait to find.

The thresholds are the pre-registration's, written before any ranking was measured:
`docs/staging/records/SEAT_PREREGISTRATION_C29_DOES_A_PER_ACCOUNT_ENGAGEMENT_ESTIMATE_RANK_BETTER_
THAN_THE_CHANNEL_2026-10-05.md` (P4: the null's lift stays within 0.10 of zero, P5: the planted lift
is at least 0.30). The book arm needs a run output, which a linked checkout does not carry, so its
reading lives in the finding beside that record and the arms here need no run.
"""
from __future__ import annotations

import random

import pytest

from company.crm.engagement_estimate import (
    CHOSE,
    ROLLED,
    estimate_engagement,
    renewal_outcomes_from_terms,
)
from tools import c29_engagement_ranking as rank

PLANTED_LIFT_FLOOR = 0.30
NULL_LIFT_CEILING = 0.10


@pytest.fixture(scope="module")
def planted():
    outcomes, channel, truth = rank.world_rolls(5, at_channel_rate=False)
    return estimate_engagement(outcomes, channel), truth


@pytest.fixture(scope="module")
def null():
    outcomes, channel, truth = rank.world_rolls(5, at_channel_rate=True)
    return estimate_engagement(outcomes, channel), truth


def test_both_arms_reach_their_own_branch_of_the_estimator(planted, null):
    """The partition first: a planted world must yield a finite prior strength (the estimate moves
    off the channel) and a null world must yield none (it collapses onto the channel). An estimator
    that always collapsed, or never did, would pass one arm's threshold for the wrong reason."""
    assert {e.prior_strength is None for e in planted[0].values()} == {False}
    assert {e.prior_strength is None for e in null[0].values()} == {True}


def test_the_estimate_ranks_the_worlds_trait_better_than_the_channel_when_the_trait_is_there(planted):
    result = rank.lift(*planted)
    assert result["lift"] >= PLANTED_LIFT_FLOOR, result


def test_the_estimate_finds_nothing_when_only_the_channel_carries_signal(null):
    result = rank.lift(*null)
    assert result["lift"] < NULL_LIFT_CEILING, result


def test_the_null_arm_keeps_each_channels_level_and_removes_only_the_household():
    """The null removes the per-household trait and nothing else. If it flattened the channels too,
    a low lift would be the channel losing its signal rather than the estimate finding none."""
    truth = {"a": 0.6, "b": 0.1, "c": 0.02, "d": 0.3}
    channel = {"a": "dd", "b": "dd", "c": "pp", "d": "pp"}
    assert rank.roll_probabilities(truth, channel, at_channel_rate=False) == truth
    null_p = rank.roll_probabilities(truth, channel, at_channel_rate=True)
    assert null_p["a"] == null_p["b"] == pytest.approx(0.35)
    assert null_p["c"] == null_p["d"] == pytest.approx(0.16)


def test_an_anniversary_is_read_once_from_the_suppliers_own_term_record():
    # The shape the run writes: one fixed year, a default stint cut into cap periods, a re-fix,
    # then a second stint. Two decisions after acquisition and a third at the next anniversary.
    terms = [
        {"term_start": "2016-01-01", "tariff_type": "fixed"},
        {"term_start": "2016-12-31", "tariff_type": "svt"},
        {"term_start": "2017-01-01", "tariff_type": "svt"},
        {"term_start": "2017-04-01", "tariff_type": "svt"},
        {"term_start": "2017-12-31", "tariff_type": "fixed"},
        {"term_start": "2018-12-31", "tariff_type": "svt"},
        {"term_start": "2019-01-01", "tariff_type": "svt"},
        {"term_start": "2019-12-31", "tariff_type": "svt"},
    ]
    assert renewal_outcomes_from_terms(terms, contract_length_days=365) == [
        ROLLED, CHOSE, ROLLED, ROLLED]
    assert renewal_outcomes_from_terms(terms[:1], contract_length_days=365,
                                       left_at_renewal=True) == [CHOSE]
    assert renewal_outcomes_from_terms(terms[:1], contract_length_days=365) == []


def test_the_book_reader_takes_only_what_the_company_recorded():
    payload = {
        "account_state_log": [
            {"customer_id": "A", "commodity": "electricity", "term_start": "2016-01-01",
             "tariff_type": "fixed"},
            {"customer_id": "A", "commodity": "electricity", "term_start": "2016-12-31",
             "tariff_type": "fixed"},
            {"customer_id": "A", "commodity": "gas", "term_start": "2016-12-31",
             "tariff_type": "svt"},
            {"customer_id": "B", "commodity": "electricity", "term_start": "2016-01-01",
             "tariff_type": "fixed"},
            {"customer_id": "NOBILL", "commodity": "electricity", "term_start": "2016-01-01",
             "tariff_type": "fixed"},
        ],
        "customer_events": [
            {"customer_id": "B", "commodity": "electricity", "event_type": "churned",
             "departure_occasion": "renewal"},
        ],
        "bills": [
            {"customer_id": "A", "commodity": "electricity", "payment_channel": "direct_debit"},
            {"customer_id": "B", "commodity": "electricity", "payment_channel": "prepayment"},
        ],
    }
    outcomes, channel = rank.book_record(payload)
    assert outcomes == {"A": [CHOSE], "B": [CHOSE]}
    assert channel == {"A": "direct_debit", "B": "prepayment"}


def test_the_book_null_shuffles_records_only_among_accounts_on_one_channel():
    outcomes = {"a": [CHOSE], "b": [ROLLED, ROLLED], "c": [CHOSE, CHOSE, CHOSE], "d": []}
    channel = {"a": "dd", "b": "dd", "c": "pp", "d": "pp"}
    shuffled = rank.shuffled_within_channel(outcomes, channel, random.Random(0))
    for ch in ("dd", "pp"):
        mine = sorted(map(tuple, (outcomes[a] for a in channel if channel[a] == ch)))
        theirs = sorted(map(tuple, (shuffled[a] for a in channel if channel[a] == ch)))
        assert mine == theirs
    # And it moves something, or the null would be the real record graded twice.
    many = {f"x{i}": [CHOSE] * i for i in range(20)}
    moved = rank.shuffled_within_channel(many, {a: "dd" for a in many}, random.Random(0))
    assert moved != many


def test_a_book_with_no_anniversary_is_refused_rather_than_given_a_channel_rate():
    with pytest.raises(ValueError, match="no account on this book has reached an anniversary"):
        estimate_engagement({"a": []}, {"a": "direct_debit"})
