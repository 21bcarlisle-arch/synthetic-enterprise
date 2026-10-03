"""The two arms' renewals are joined per account, and a roster difference is never "decided differently".

b6a21c885 found that no artefact recorded what either arm decided, so the +880 carried by the value
arm's priced accounts could not be split into "the arms decided differently here" and "the same
decision happened differently". `tools.run_value_cycle_ab.decided_differently_by_account` is that
join. A renewal present in one log only means the books had already diverged. It is counted in its
own column, because counting it as a different decision would inflate the very set the grade
partitions on.
"""

from __future__ import annotations

from tools.run_value_cycle_ab import (
    RENEWAL_BELIEF_FIELDS,
    RENEWAL_DECISION_FIELDS,
    _renewal_decision_rows,
    decided_differently_by_account,
)


def _row(cid, term, *, declined=False, rate=100.0, commodity="electricity"):
    return {"customer_id": cid, "commodity": commodity, "term_start": term, "declined": declined,
            "chosen_margin_gbp_per_mwh": None if declined else 20.0,
            "offered_rate_gbp_per_mwh": None if declined else rate}


def _logs():
    value = [
        _row("A", "2017-03-23", rate=100.0),                        # same in both
        _row("A", "2018-03-23", rate=101.0),                        # rates differ
        _row("Ag", "2018-03-23", commodity="gas", declined=True),   # declined vs priced
        _row("B", "2019-01-01", declined=True),                     # both declined: same
        _row("C", "2020-06-01"),                                    # value log only
    ]
    level = [
        _row("A", "2017-03-23", rate=100.0),
        _row("A", "2018-03-23", rate=99.0),
        _row("Ag", "2018-03-23", commodity="gas", rate=50.0),
        _row("B", "2019-01-01", declined=True),
        _row("D", "2021-02-02"),                                    # level log only
    ]
    return value, level


def test_every_branch_of_the_join_is_taken():
    """A join whose fixture never reaches a branch passes whatever that branch does."""
    joined = decided_differently_by_account(*_logs())
    totals = {k: sum(r[k] for r in joined.values()) for k in next(iter(joined.values()))}
    for key in ("renewals_in_both_logs", "declined_in_one_arm_only", "offered_a_different_rate",
                "in_value_log_only", "in_level_log_only", "decided_differently"):
        assert totals[key] > 0, key


def test_the_join_counts_per_billing_account_and_keeps_roster_differences_apart():
    joined = decided_differently_by_account(*_logs())
    # A and Ag are one account: two renewals decided differently out of three in both logs.
    assert joined["A"] == {"renewals_in_both_logs": 3, "declined_in_one_arm_only": 1,
                           "offered_a_different_rate": 1, "in_value_log_only": 0,
                           "in_level_log_only": 0, "decided_differently": 2}
    assert joined["B"]["decided_differently"] == 0
    assert joined["B"]["renewals_in_both_logs"] == 1
    assert joined["C"] == {"renewals_in_both_logs": 0, "declined_in_one_arm_only": 0,
                           "offered_a_different_rate": 0, "in_value_log_only": 1,
                           "in_level_log_only": 0, "decided_differently": 0}
    assert joined["D"]["in_level_log_only"] == 1
    assert joined["D"]["decided_differently"] == 0


def test_a_priced_row_with_no_rate_cannot_be_shown_equal():
    value = [_row("A", "2017-03-23", rate=100.0)]
    level = [_row("A", "2017-03-23", rate=100.0)]
    level[0]["offered_rate_gbp_per_mwh"] = None
    assert decided_differently_by_account(value, level)["A"]["offered_a_different_rate"] == 1


def test_an_arm_that_did_not_run_is_absent_not_empty():
    value, _level = _logs()
    assert _renewal_decision_rows(None) is None
    assert decided_differently_by_account(value, None) is None


def test_the_decision_rows_keep_declines_and_only_the_decision_fields():
    arm = {"phase2b": {"value_arm_log": [
        {**_row("A", "2017-03-23"), "believed_p_retain": 0.4},
        _row("B", "2019-01-01", declined=True),
    ]}}
    rows = _renewal_decision_rows(arm)
    assert len(rows) == 2
    assert all(set(r) == {*RENEWAL_DECISION_FIELDS, *RENEWAL_BELIEF_FIELDS} for r in rows)
    assert rows[1]["declined"] is True

