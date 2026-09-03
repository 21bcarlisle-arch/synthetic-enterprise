"""Controls on the two-arm direct-debit comparison in `tools/dd_opening_arms.py`.

Each test names the defect it exists to catch. The subject is an EXPERIMENT, and an
experiment that quietly compares two different populations, or that averages a
household in credit against one in debit, produces a number that reads as a result
and is not one — which is precisely the class this repository has paid for most.
"""
from __future__ import annotations

from tools.dd_opening_arms import (
    _matched_window0,
    _split_credit_debit,
    diff_run_outputs,
    flat_opening_by_customer,
)

# Two customers, three bills each, the first bill deliberately NOT the smallest so
# a rule that took min() rather than first-by-date would be caught too.
BILLS = [
    {"customer_id": "A", "period_end": "2019-01-31", "total_amount_gbp": 90.0,
     "segment": "resi", "commodity": "electricity"},
    {"customer_id": "A", "period_end": "2019-02-28", "total_amount_gbp": 40.0,
     "segment": "resi", "commodity": "electricity"},
    {"customer_id": "B", "period_end": "2019-03-31", "total_amount_gbp": 25.0,
     "segment": "resi", "commodity": "gas"},
    {"customer_id": "B", "period_end": "2019-04-30", "total_amount_gbp": 60.0,
     "segment": "resi", "commodity": "gas"},
]


def test_the_flat_arm_is_the_first_issued_bill_and_not_any_other_bill():
    """DEFECT: the baseline arm silently stops being the rule the organ displaced.

    The whole comparison is worthless if the flat arm is not `seq[0][1]`. A rule that
    took the mean, the min or the last bill would still produce a plausible-looking
    diff, and nothing else in the experiment would notice.
    """
    flat = flat_opening_by_customer(BILLS, direct_debit_only=False)
    assert flat == {"A": 90.0, "B": 25.0}


def test_the_dd_filtered_map_is_a_subset_of_the_unfiltered_one():
    """DEFECT: the two organs group differently and one map is used for both.

    `dd_balance_book` filters to direct-debit bills before taking `seq[0]`;
    `dd_review_runner` does not. Feeding one map to both would put a customer's
    non-DD first bill into the DD book's opening amount.
    """
    unfiltered = flat_opening_by_customer(BILLS, direct_debit_only=False)
    filtered = flat_opening_by_customer(BILLS, direct_debit_only=True)
    assert set(filtered) <= set(unfiltered)


def test_credit_and_debit_are_reported_separately_and_never_netted():
    """DEFECT: a household +200 in credit and one -200 in debit average to zero.

    "The mean drift is about zero" is the exact shape CLAUDE.md names — two
    populations with different experiences and different remedies, differenced into
    one number that describes neither. If this ever returns a single mean, the
    published drift figure becomes a statement nobody can act on.
    """
    split = _split_credit_debit([200.0, -200.0, 50.0])
    assert split["in_credit"]["n"] == 2
    assert split["in_debit"]["n"] == 1
    assert split["in_credit"]["mean_gbp"] == 125.0
    assert split["in_debit"]["mean_gbp"] == -200.0
    # There is no netted field to read by accident.
    assert "mean_gbp" not in split


def test_a_sample_of_one_earns_no_interval():
    """DEFECT: a one-observation interval of [x, x] publishes perfect confidence.

    A figure published without the bound its sample size earns is worse than no
    figure, and the fail-open reading of a bound is a zero-width one.
    """
    split = _split_credit_debit([42.0])
    assert split["in_credit"]["n"] == 1
    assert split["in_credit"]["ci95_gbp"] == [None, None]


def test_the_matched_comparison_holds_the_population_fixed():
    """DEFECT: comparing the arms over their UNION attributes the refusal to the rule.

    The estimate arm refuses every pre-2019 account, so its book is smaller. If the
    matched block took the union rather than the intersection it would compare 178
    accounts under one rule with 96 under the other and call the difference the
    rule's doing. Mutating `&` to `|` in `_matched_window0` turns this red.
    """
    flat_w = {"A": {0: -100.0}, "B": {0: -300.0}, "C": {0: -50.0}}
    est_w = {"A": {0: -10.0}, "B": {0: -400.0}}
    m = _matched_window0(flat_w, est_w)
    assert m["n_matched_accounts"] == 2
    assert m["flat"]["n_accounts"] == 2
    assert m["estimate"]["n_accounts"] == 2
    # A closer to zero, B further: the paired counts must split, not both fall one way.
    assert m["n_estimate_closer_to_zero"] == 1
    assert m["n_flat_closer_to_zero"] == 1


def test_the_diff_states_what_did_not_move_as_well_as_what_did():
    """DEFECT: "only the DD keys moved" is a claim about the keys nobody looked at.

    A diff that returns only its hits cannot distinguish "101 keys were compared and
    held" from "101 keys were never read". The complement is the evidence.
    """
    a = {"x": 1, "y": 2, "z": 3}
    b = {"x": 1, "y": 99, "z": 3}
    d = diff_run_outputs(a, b)
    assert d["moved_keys"] == ["y"]
    assert d["unmoved_keys"] == ["x", "z"]
    assert not set(d["moved_keys"]) & set(d["unmoved_keys"])
    assert d["leaf_diffs"]["y"] == ["y: 2 -> 99"]
