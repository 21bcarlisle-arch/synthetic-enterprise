"""R15 for the renewal-churn-belief grade: prove every verdict it publishes can FAIL.

The instrument's job is to say whether a belief ranks who leaves, whether its level is right, and
whether bill shock moves the world the way the model assumes. Each of those three verdicts gets a
fixture on which it comes out the OTHER way, because a grade that reports "no ranking power" on
every input -- including a perfect predictor -- is not a measurement.

The three killer shapes are covered explicitly:
  * TAUTOLOGY   -- the oracle ceiling must be computed from the WORLD's probability, so a fixture
                   whose world truth is perfect and whose belief is constant must separate them.
  * FAIL-OPEN   -- a population with no departures, a run with no events, and an off-lattice
                   belief must all REFUSE rather than return a number that reads like a pass.
  * FAIL-SILENT -- a missing `realized_churn_probability` must not be averaged in as zero.
"""

import pytest

from saas.churn_model import BASE_ANNUAL_CHURN_PROBABILITY, CHURN_UPLIFT_PER_BILL_SHOCK
from tools.grade_renewal_churn_belief import (
    grade_belief,
    grade_run,
    rank_auc,
    recover_bill_shock_count,
)


def _event(account, date, k, retained, world_true=0.05, company=None, believed=None):
    """One renewal the world rolled, shaped exactly as `roll_lifecycle_event` stamps it."""
    event = {
        "customer_id": account,
        "event_date": date,
        "event_type": "renewed" if retained else "churned",
        "churn_probability": (
            believed if believed is not None
            else round(BASE_ANNUAL_CHURN_PROBABILITY + k * CHURN_UPLIFT_PER_BILL_SHOCK, 4)
        ),
        "realized_churn_probability": world_true,
    }
    if company is not None:
        event["company_churn_estimate"] = company
    return event


# ── DISCRIMINATION: the AUC must be able to reach both ends ────────────────────────────────

def test_a_perfectly_predictive_belief_scores_one():
    events = (
        [_event(f"A{i}", "2020-01-01", 0, retained=True) for i in range(10)]
        + [_event(f"B{i}", "2020-01-01", 12, retained=False) for i in range(5)]
    )
    grade = grade_run({"customer_events": events})
    assert grade["bill_shock_model"]["discrimination_auc"] == 1.0


def test_an_inverted_belief_scores_below_a_coin_flip():
    """The A/B's headline claim was an INVERSION. If this fixture did not come out below 0.5 the
    instrument could never have reproduced that finding, and its 0.5586 on the live book would be
    a statistic incapable of reporting the thing it was built to test."""
    events = (
        [_event(f"A{i}", "2020-01-01", 12, retained=True) for i in range(10)]
        + [_event(f"B{i}", "2020-01-01", 0, retained=False) for i in range(5)]
    )
    grade = grade_run({"customer_events": events})
    assert grade["bill_shock_model"]["discrimination_auc"] == 0.0


def test_a_constant_belief_scores_exactly_a_coin_flip_and_names_itself():
    events = (
        [_event(f"A{i}", "2020-01-01", 3, retained=True) for i in range(8)]
        + [_event(f"B{i}", "2020-01-01", 3, retained=False) for i in range(4)]
    )
    block = grade_run({"customer_events": events})["bill_shock_model"]
    assert block["discrimination_auc"] == 0.5
    assert block["belief_is_constant"] is True
    assert block["distinct_believed_values"] == 1


def test_a_population_with_no_departures_refuses_the_rank_statistic():
    """FAIL-OPEN killer. 0.5 is what a computed-and-uninformative belief scores; a belief that
    COULD NOT be scored must not be indistinguishable from it."""
    events = [_event(f"A{i}", "2020-01-01", i % 5, retained=True) for i in range(12)]
    block = grade_run({"customer_events": events})["bill_shock_model"]
    assert block["discrimination_auc"] is None
    assert "one outcome class is empty" in block["auc_unavailable_reason"]
    assert block["auc_population"] == {"retained": 12, "left": 0}


def test_rank_auc_returns_none_and_never_a_half_on_an_empty_class():
    assert rank_auc([], [0.4]) is None
    assert rank_auc([0.4], []) is None
    assert rank_auc([0.4], [0.4]) == 0.5


# ── CALIBRATION: the level verdict, asserted away from any fallback value ──────────────────

def test_the_level_ratio_and_calibration_error_are_exact():
    """Values chosen away from the model's own base rate: a fixture sitting AT the fallback is
    where a wrong arithmetic and a right one agree."""
    events = (
        [_event(f"A{i}", "2020-01-01", 5, retained=True) for i in range(9)]     # believed 0.20
        + [_event("B0", "2020-01-01", 5, retained=False)]                      # 1 of 10 left
    )
    block = grade_run({"customer_events": events})["bill_shock_model"]
    assert block["mean_believed_churn"] == pytest.approx(0.20)
    assert block["realised_churn_rate"] == pytest.approx(0.10)
    assert block["level_ratio_believed_over_realised"] == pytest.approx(2.0)
    # believed retention 0.80 minus realised retention 0.90: the company under-expects retention.
    assert block["calibration_error"] == pytest.approx(-0.10)


# ── THE BUCKET TABLE: n is renewals, accounts is households ────────────────────────────────

def test_the_bucket_table_counts_accounts_separately_from_renewals():
    """An unbalanced fixture on purpose: 11 renewals from 3 accounts. A balanced one could not see
    the difference between the two counts, and the whole point of the account column is that a
    bucket of 11 renewals from 3 households is 3 draws wearing 11 hats."""
    events = [
        _event(account, f"20{16 + i}-01-01", 12, retained=(i % 3 != 0))
        for account in ("A", "B", "C")
        for i in range(4)
    ][:11]
    block = grade_run({"customer_events": events})["bill_shock_model"]
    bucket = block["by_believed_bucket"][0]
    assert bucket["n"] == 11
    assert bucket["accounts"] == 3
    assert bucket["n"] != bucket["accounts"]


# ── PROVENANCE: an off-lattice belief is refused, not rounded into the base bucket ──────────

def test_an_off_lattice_belief_is_refused_rather_than_rounded():
    assert recover_bill_shock_count(0.05) == 0
    assert recover_bill_shock_count(0.41) == 12
    assert recover_bill_shock_count(0.077) is None      # not BASE + k * UPLIFT for integer k
    assert recover_bill_shock_count(0.95) is None       # at the cap the inversion is many-to-one

    events = (
        [_event(f"A{i}", "2020-01-01", 0, retained=True) for i in range(3)]
        + [_event("B0", "2020-01-01", 0, retained=False, believed=0.077)]
    )
    grade = grade_run({"customer_events": events})
    provenance = grade["belief_provenance"]
    assert provenance["graded_renewals"] == 4
    assert provenance["on_lattice"] == 3
    assert provenance["on_lattice_share"] == pytest.approx(0.75)
    assert provenance["off_lattice_sample"][0]["churn_probability"] == 0.077
    # excluded from the mechanism table rather than counted as k=0
    assert grade["mechanism"]["graded"] == 3
    assert sum(row["n"] for row in grade["mechanism"]["by_bill_shock_count"]) == 3


# ── REFUSALS: nothing to grade must raise, never publish an empty grade ─────────────────────

def test_a_run_with_no_customer_events_refuses():
    with pytest.raises(ValueError, match="no `customer_events`"):
        grade_run({"customer_events": []})
    with pytest.raises(ValueError, match="no `customer_events`"):
        grade_run({})


def test_a_run_whose_events_carry_no_outcome_refuses():
    events = [{"customer_id": "A", "event_date": "2020-01-01", "churn_probability": 0.05}]
    with pytest.raises(ValueError, match="logged belief and a lifecycle outcome"):
        grade_run({"customer_events": events})


def test_grade_belief_refuses_an_empty_population():
    with pytest.raises(ValueError, match="empty population"):
        grade_belief([], "believed_churn", "nothing")


# ── THE ORACLE CEILING: computed from the WORLD's number, not the belief ────────────────────

def test_the_oracle_ceiling_is_the_worlds_probability_and_not_a_mirror_of_the_belief():
    """TAUTOLOGY killer. The belief is CONSTANT here, so it can carry no information at all; the
    world's own probability is perfect. If the ceiling tracked the belief it would read 0.5."""
    events = (
        [_event(f"A{i}", "2020-01-01", 4, retained=True, world_true=0.01) for i in range(6)]
        + [_event(f"B{i}", "2020-01-01", 4, retained=False, world_true=0.99) for i in range(3)]
    )
    grade = grade_run({"customer_events": events})
    assert grade["bill_shock_model"]["discrimination_auc"] == 0.5
    assert grade["oracle_ceiling"]["discrimination_auc"] == 1.0
    assert grade["oracle_ceiling"]["n"] == 9


def test_the_oracle_ceiling_can_itself_come_out_below_a_coin_flip():
    events = (
        [_event(f"A{i}", "2020-01-01", 4, retained=True, world_true=0.99) for i in range(6)]
        + [_event(f"B{i}", "2020-01-01", 4, retained=False, world_true=0.01) for i in range(3)]
    )
    assert grade_run({"customer_events": events})["oracle_ceiling"]["discrimination_auc"] == 0.0


# ── THE MECHANISM VERDICT: the sign must be able to come out negative ───────────────────────

def test_the_mechanism_reports_a_disagreeing_sign_when_bill_shock_predicts_the_opposite():
    """The candidate the direction names -- bill shock predicting the OPPOSITE of the model's
    assumption -- must be a verdict this instrument can actually return. Here the world's true
    probability FALLS as shocks rise."""
    events = (
        [_event(f"A{i}", "2020-01-01", 0, retained=True, world_true=0.30) for i in range(5)]
        + [_event(f"B{i}", "2020-01-01", 10, retained=False, world_true=0.02) for i in range(5)]
    )
    mech = grade_run({"customer_events": events})["mechanism"]
    assert mech["sign_agrees_with_model"] is False
    assert mech["world_true_uplift_per_shock_endpoints"] < 0


def test_the_attenuation_factor_is_the_assumed_dose_over_the_delivered_one():
    """10 shocks apart, world true rising 0.03 across them = 0.003/shock against an assumed 0.03,
    so the model's dose is 10x what the world delivers. Exact, and away from 1.0 in both legs."""
    events = (
        [_event(f"A{i}", "2020-01-01", 0, retained=True, world_true=0.02) for i in range(5)]
        + [_event(f"B{i}", "2020-01-01", 10, retained=False, world_true=0.05) for i in range(5)]
    )
    mech = grade_run({"customer_events": events})["mechanism"]
    assert mech["sign_agrees_with_model"] is True
    assert mech["world_true_uplift_per_shock_endpoints"] == pytest.approx(0.003)
    assert mech["attenuation_factor"] == pytest.approx(10.0)


def test_a_missing_world_probability_is_not_averaged_in_as_zero():
    """FAIL-SILENT killer. Dropping the field must shrink the population the mean is taken over,
    not pull the mean toward zero -- which would inflate the attenuation factor precisely when the
    world stopped publishing its own truth."""
    events = [_event(f"A{i}", "2020-01-01", 6, retained=True, world_true=0.20) for i in range(4)]
    for event in events[:2]:
        del event["realized_churn_probability"]
    row = grade_run({"customer_events": events})["mechanism"]["by_bill_shock_count"][0]
    assert row["n"] == 4
    assert row["world_true_n"] == 2
    assert row["world_true_churn_probability_mean"] == pytest.approx(0.20)


def test_the_company_estimate_is_graded_as_a_separate_belief():
    """The company's own estimate does NOT feed the world's roll, so it is the independent leg and
    must be reported separately rather than folded into the bill-shock model's numbers."""
    events = (
        [_event(f"A{i}", "2020-01-01", 12, retained=True, company=0.02) for i in range(6)]
        + [_event(f"B{i}", "2020-01-01", 0, retained=False, company=0.90) for i in range(3)]
    )
    grade = grade_run({"customer_events": events})
    assert grade["bill_shock_model"]["discrimination_auc"] == 0.0
    assert grade["company_estimate"]["discrimination_auc"] == 1.0
    assert grade["independence"]["belief_and_outcome_share_a_source"] is True


def test_a_run_with_no_company_estimate_says_so_rather_than_scoring_nothing():
    events = [_event(f"A{i}", "2020-01-01", 2, retained=(i % 2 == 0)) for i in range(6)]
    block = grade_run({"customer_events": events})["company_estimate"]
    assert block["available"] is False
    assert "no renewal carries a company churn estimate" in block["reason"]
