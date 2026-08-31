"""The one number this whole comparison exists to produce is the one it must usually refuse.

`tools/measure_churn_heterogeneity.ceiling_vs_belief` puts a company belief beside the world's own
ceiling and computes what fraction of the available discrimination the company captured. That
figure is quotable, memorable, and wrong on this book for two different reasons at once — so the
refusal is the load-bearing behaviour and the ratio is the exception.

WHY EACH LEG EXISTS, AND EACH IS A DEFECT THIS PROJECT HAS ALREADY PAID FOR:

* **one population** — a numerator counting 144 renewals over a denominator counting 1,410
  decisions across both routes. Two true numbers whose legs are different populations do not have
  a ratio (`feedback_two_true_numbers_whose_ratio_is_not_a_quantity`).
* **independence** — `saas.churn_model.build_churn_risk` SEEDS `effective_p_retain`, the very roll
  it is then graded against. It scores 0.6815 against a 0.7412 ceiling, which as a "92% of the
  ceiling captured" would be the world reading back its own input.
* **clears its own null** — `company_churn_estimate` reads inside its null. A cannot-tell divided
  by a ceiling yields a small percentage that carries the authority of a measurement and the
  content of noise. It is refused, never rounded to zero.
* **and the ceiling must survive a refused belief** — the defect found 2026-08-31: the cross-run
  refusal in `attach_company_beliefs` was allowed out of `report`, so the landed rung-3 control
  errored on every leg. Correct refusal, wrong blast radius.

KEYED TO THE PROPERTY. Nothing here asserts 0.7412 or 0.6815. When a fresh capture carries an
independent belief that clears its null, the ratio becomes legal and these legs must still pass —
what they hold is that each condition is *required*, not what today's answers are.
"""
from __future__ import annotations

import copy
import json

import pytest

from tools import measure_churn_heterogeneity as mch


def _belief(*, label="b", decisions=144, independent=True, clears=True, auc=0.65) -> dict:
    return {
        "belief": label,
        "field": "f",
        "available": True,
        "seeds_the_world_roll": not independent,
        "independent_of_the_outcome": independent,
        "reading": "",
        "decisions": decisions,
        "departures": 32,
        "pairs": 100,
        "belief_auc": auc,
        "null": {"low": 0.40, "high": 0.60, "median": 0.5, "permutations": 300},
        "clears_the_null": clears,
        "verdict": "",
        "tie_fraction": 0.1,
        "distinct_values": 13,
        "mean_believed": 0.2,
        "realised_rate": 0.22,
    }


def _route(beliefs, *, decisions=144, ceiling=0.7412) -> dict:
    return {"route": "renewal", "decisions": decisions, "oracle_auc": ceiling, "company_belief": beliefs}


def _only(result: dict) -> dict:
    assert len(result["readings"]) == 1
    return result["readings"][0]


def test_a_LEGAL_ratio_is_published_so_the_refusals_below_are_not_vacuous():
    """The control must be able to say YES, or every leg after it proves nothing.

    Without this, deleting the whole ratio computation and returning `None` unconditionally would
    pass every other test in this file.
    """
    r = _only(ceiling_vs_belief_of(_route([_belief(auc=0.65)])))
    assert r["refused_because"] is None
    assert r["excess_over_chance_captured"] == pytest.approx((0.65 - 0.5) / (0.7412 - 0.5))


def test_the_ratio_is_REFUSED_when_the_belief_seeds_the_roll_it_is_graded_against():
    """MUTATION: drop `independent` from the `legal` conjunction and this fires."""
    r = _only(ceiling_vs_belief_of(_route([_belief(independent=False)])))
    assert r["excess_over_chance_captured"] is None
    assert "seeds the world's own roll" in r["refused_because"]


def test_the_ratio_is_REFUSED_when_the_belief_sits_inside_its_own_null():
    """A cannot-tell over a ceiling is a percentage with the content of noise.

    MUTATION: drop `clears` from the conjunction and this fires.
    """
    r = _only(ceiling_vs_belief_of(_route([_belief(clears=False, auc=0.4988)])))
    assert r["excess_over_chance_captured"] is None
    assert "INSIDE its null" in r["refused_because"]


def test_the_ratio_is_REFUSED_when_the_two_legs_count_different_populations():
    """MUTATION: drop `same_population` from the conjunction and this fires."""
    r = _only(ceiling_vs_belief_of(_route([_belief(decisions=1410)])))
    assert r["excess_over_chance_captured"] is None
    assert "not one population" in r["refused_because"]


def test_every_failing_condition_is_NAMED_not_just_the_first():
    """A refusal that names one of three causes sends the reader to fix the wrong thing.

    MUTATION: `return` after the first reason instead of collecting them, and this fires.
    """
    r = _only(ceiling_vs_belief_of(_route([_belief(decisions=1410, independent=False, clears=False)])))
    reason = r["refused_because"]
    assert "not one population" in reason
    assert "seeds the world's own roll" in reason
    assert "INSIDE its null" in reason


def test_a_belief_that_DOES_NOT_EXIST_is_not_a_belief_that_scored_at_chance():
    """Opposite findings, and a reader must not have to tell them apart from a missing row.

    MUTATION: make `belief_readings` emit `belief_auc: 0.5` for an unavailable belief instead of
    an `available: False` entry with a cause, and this fires.
    """
    absent = {
        "belief": "gone",
        "field": "f",
        "available": False,
        "reason": "the company forms no belief on this route",
        "seeds_the_world_roll": False,
    }
    r = _only(ceiling_vs_belief_of(_route([absent])))
    assert r["belief_auc"] is None
    assert r["excess_over_chance_captured"] is None
    assert r["refused_because"] == "the company forms no belief on this route"


def test_the_CEILING_survives_a_belief_join_that_refuses(tmp_path):
    """The blast-radius defect of 2026-08-31, made mechanical.

    `attach_company_beliefs` refuses when the capture and the run output are not the same run, and
    that refusal is right. It must not take the ceiling with it: the rung-3 reading is computed
    from the capture alone and never touches the run output.

    MUTATION: remove the `try/except Unreadable` around `attach_company_beliefs` in `report` and
    this fires — as it did in the live tree, erroring every leg of
    `tests/architecture/test_churn_carries_per_customer_signal.py`.

    THE SCOPE OF THE REFUSAL IS PART OF THE PROPERTY, and the first draft of this test got it
    wrong: it asserted that EVERY belief goes unavailable when the join refuses. Only
    `JOIN_SUPPLIED_FIELD` comes from the run output; the others are already on the capture row and
    are gradable whatever the join does. An over-broad refusal is its own defect — it would hide a
    real reading behind an unrelated failure, which is the same blast-radius mistake one direction
    over. Both halves are asserted here.

    AND THE SITUATION IS BUILT, NOT BORROWED — the second thing this test got wrong. It first ran
    `report()` on the committed capture and assumed that capture would always NEED the join. Hours
    later a fresh capture recorded `JOIN_SUPPLIED_FIELD` directly, `attach_company_beliefs` returned
    early with "the capture already carries the field", and the test `KeyError`ed on a refusal that
    correctly never happened. **A control coupled to an incidental property of an artefact fails
    when the artefact improves**, which is the wrong direction to be brittle in. So the capture that
    needs the join is constructed here by stripping the field, and this leg keeps testing the
    refusal path for as long as the code has one — and goes green by construction the day it does
    not, because `_needs_join` will be False and the assertions are skipped rather than inverted.
    """
    stripped = tmp_path / "capture_without_the_joined_field.json"
    rows = json.loads(mch.DEFAULT_TABLE.read_text())
    for row in rows:
        row.pop(mch.JOIN_SUPPLIED_FIELD, None)
    stripped.write_text(json.dumps(rows))
    companion = mch.svt_companion(mch.DEFAULT_TABLE)
    if companion.exists():
        mch.svt_companion(stripped).write_text(companion.read_text())

    unmatched = tmp_path / "not_the_same_run.json"
    unmatched.write_text('{"customer_events": [{"customer_id": "NOBODY", "event_date": "1970-01-01"}]}')
    reading = mch.report(stripped, permutations=100, run_output=unmatched)

    assert reading["oracle_auc"] is not None
    assert isinstance(reading["clears_the_null"], bool)
    prov = reading["company_belief_provenance"]
    assert prov["joined"] is False
    assert prov["refused"], "the refusal must be CARRIED, not swallowed — a reader needs its cause"

    seen = set()
    for entry in reading["per_route"].values():
        for belief in entry.get("company_belief", []):
            seen.add(belief["field"])
            if belief["field"] == mch.JOIN_SUPPLIED_FIELD:
                assert belief["available"] is False, (
                    "the belief the JOIN supplies was graded despite the join refusing: it is "
                    "being scored against outcomes it never saw"
                )
                assert belief.get("reason"), "an unavailable belief must carry its cause"
    assert mch.JOIN_SUPPLIED_FIELD in seen, (
        "the join-supplied belief is absent from the reading entirely — a refusal must leave a "
        "row saying so, not delete the column"
    )


def ceiling_vs_belief_of(route_entry: dict) -> dict:
    """Call the subject on a deep copy, so a leg cannot pass by mutating the fixture."""
    return mch.ceiling_vs_belief(copy.deepcopy(route_entry))


# ══════════════════════════════════════════════════════════════════════════════════════════════
# THE FOURTH CONDITION — a belief may clear its null on a reading its own route has WITHDRAWN
# ══════════════════════════════════════════════════════════════════════════════════════════════
#
# Added 2026-08-31 with `company.crm.churn_desk.estimate_svt_drift`, the company's first belief
# about the SVT route. It clears its null uncorrected (0.6054 against a high of 0.5883) and the
# three conditions above would all have passed, publishing "the company captures 88% of the
# ceiling's excess" as its first look at 61% of the book's departures. Offset for exposure it
# reads 0.4691, INSIDE its null, while the ceiling still clears at 0.6091: what it ordered was how
# long the segment ran. The withdrawn reading is the flattering one, which is the recurring shape.


def _offset(*, clears: bool, auc: float = 0.4691) -> dict:
    return {
        "offset": "belief divided by segment days, i.e. a per-exposure-day rate",
        "belief_auc_per_exposure_day": auc,
        "null": {"low": 0.4164, "high": 0.5834, "median": 0.5, "permutations": 300},
        "pairs": 7174,
        "clears_the_null": clears,
        "verdict": "",
        "reading": "",
    }


def test_the_ratio_is_REFUSED_when_the_belief_clears_only_BEFORE_the_exposure_offset():
    """The defect this condition exists for: legal on all three older conditions, still wrong."""
    b = _belief(auc=0.6054, clears=True)
    b["exposure_offset"] = _offset(clears=False)
    reading = _only(mch.ceiling_vs_belief(_route([b])))
    assert reading["excess_over_chance_captured"] is None
    assert reading["clears_its_null_after_exposure_offset"] is False
    assert "exposure offset" in reading["refused_because"]
    # The refusal must carry BOTH numbers, or a reader cannot see which one was withdrawn.
    assert "0.6054" in reading["refused_because"] and "0.4691" in reading["refused_because"]


def test_a_belief_that_SURVIVES_the_offset_is_still_published_so_the_condition_is_not_a_veto():
    """Mutation guard: a condition that refuses everything is not a control, it is an off switch."""
    b = _belief(auc=0.6054, clears=True)
    b["exposure_offset"] = _offset(clears=True, auc=0.62)
    reading = _only(mch.ceiling_vs_belief(_route([b])))
    assert reading["excess_over_chance_captured"] is not None
    assert reading["clears_its_null_after_exposure_offset"] is True


def test_a_route_with_NO_exposure_offset_is_not_treated_as_having_FAILED_one():
    """`None` means the route carries no exposure. It must not read as a failed offset.

    The fail-closed direction is wrong here and that is the point: refusing every renewal-route
    ratio because the renewal route has no segment length would delete the only comparison this
    instrument was built to make.
    """
    reading = _only(mch.ceiling_vs_belief(_route([_belief(auc=0.65, clears=True)])))
    assert reading["clears_its_null_after_exposure_offset"] is True
    assert reading["excess_over_chance_captured"] is not None


def test_the_uncorrected_belief_reading_is_marked_SUPERSEDED_in_the_reading_itself():
    """Not beside it. A reader taking `belief_auc` must meet the withdrawal at that key.

    The per-factor table had exactly this defect and it was fixed the same day; this is the same
    repair for the belief, and it is a separate assertion because it was a separate omission.
    """
    rows = [
        {"route": "svt_segment", "market_year": 2020, "event_type": "stayed",
         "f": 0.02, "sim_segment_days": 90},
        {"route": "svt_segment", "market_year": 2020, "event_type": "churned",
         "f": 0.03, "sim_segment_days": 91},
    ]
    entry = {"belief_auc": 0.6, "clears_the_null": True}
    mch._supersede_uncorrected_belief(entry)
    assert entry["belief_auc_superseded_by"] == "exposure_offset.belief_auc_per_exposure_day"
    assert "exposure offset" in entry["belief_auc_superseded_because"]
    assert entry["clears_the_null_superseded_by"] == "exposure_offset.clears_the_null"
    # And the offset is actually COMPUTED for a route carrying exposure, not merely stamped.
    assert mch.belief_exposure_offset(rows, lambda r: r["f"], 50) is not None


def test_the_offset_is_keyed_to_the_EXPOSURE_FIELD_not_to_the_routes_name():
    """Keyed to the property. A route that gains exposure inherits the offset with no edit."""
    with_exposure = [{"sim_segment_days": 30}, {"sim_segment_days": 1}]
    assert mch.route_carries_exposure(with_exposure) is True
    # Renewal rows carry no segment length, so there is nothing to divide by.
    assert mch.route_carries_exposure([{"sim_bill_shock_base": 0.03}]) is False
    # ALL, not ANY: a partial offset would rank two scales against each other.
    assert mch.route_carries_exposure([{"sim_segment_days": 30}, {}]) is False
    # A non-positive exposure cannot be divided by and must not read as offsettable.
    assert mch.route_carries_exposure([{"sim_segment_days": 0}]) is False
    assert mch.belief_exposure_offset([{"x": 1}], lambda r: r["x"], 10) is None


def test_the_replayed_svt_belief_equals_the_stamped_one():
    """The anti-fabrication proof, and it is the load-bearing one for the whole SVT reading.

    The instrument grades a belief the capture never recorded, by replaying the company's own
    estimator over two observables the capture DID record. That is only legitimate if the replay
    reproduces what the run would have stamped -- otherwise the harness is grading a channel it
    invented, which is a failure this project has already paid for. So: a row carrying a stamped
    value must come back UNCHANGED (the stamp wins), and a row without one must come back with
    exactly the value the company's function returns for it.
    """
    from company.crm.churn_desk import SvtSegmentObservation, estimate_svt_drift

    observables = {"sim_years_on_svt": 1.5, "sim_segment_days": 91}
    truth = estimate_svt_drift(SvtSegmentObservation(years_on_svt=1.5, segment_days=91))

    unstamped = {"route": "svt_segment", **observables}
    stamped = {"route": "svt_segment", **observables, "company_svt_drift_estimate": 0.123}
    out, prov = mch.derive_company_beliefs([unstamped, stamped])

    assert out[0]["company_svt_drift_estimate"] == truth
    assert out[1]["company_svt_drift_estimate"] == 0.123, "a stamped value must win over the replay"
    assert prov["derived"]["company_svt_drift_estimate"] == 1
    # The band must actually be load-bearing, or the replay is testing arithmetic only.
    long_stayer = estimate_svt_drift(SvtSegmentObservation(years_on_svt=9.0, segment_days=91))
    assert long_stayer < truth


def test_a_row_missing_an_observable_is_left_UNFILLED_rather_than_defaulted():
    """A default would silently change the population out from under the ceiling."""
    out, prov = mch.derive_company_beliefs(
        [{"route": "svt_segment", "sim_years_on_svt": 1.5}]  # no `sim_segment_days`
    )
    assert "company_svt_drift_estimate" not in out[0]
    assert prov["derived"] == {}


def test_the_replay_is_NOT_applied_to_a_route_the_belief_is_not_defined_on():
    """A renewal row must not acquire an SVT belief because it happens to carry the columns."""
    out, _ = mch.derive_company_beliefs(
        [{"route": "renewal", "sim_years_on_svt": 1.5, "sim_segment_days": 91}]
    )
    assert "company_svt_drift_estimate" not in out[0]
