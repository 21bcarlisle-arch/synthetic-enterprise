"""The page and the collections desk read one payment record for every leg the triad posted.

The defect this names: `per_customer_behavioral` was built over the roster's customers only, so an
incoming occupier's account (`OCC-`) carried no `world_payment_truth`, and the arrears engine
(`_resolve_bills`) drew each of its bills' outcomes again. The billing ledger's page read that
second draw; the desk read the triad's. On the b2fc50facf book, 2,005 overdue-row breaches were the
two disagreeing.
"""
from simulation import world_payment_truth as wpt
from simulation.arrears_engine import _resolve_bills
from simulation.household_demand import HouseholdDemandRegister
from simulation.run_phase2b import _build_behavioral_trajectories


def _truth(result, days_late):
    return {"outcomes": {"2025-03": {"result": result, "days_late": days_late,
                                     "method": "standard_credit"}},
            "repayments": []}


def test_a_leg_off_the_roster_carries_the_triads_payment_truth():
    truth = {"C1": _truth("success", 0), "OCC-0000000000aa": _truth("failed", 0)}
    out = _build_behavioral_trajectories(
        [{"customer_id": "C1"}], HouseholdDemandRegister([]), None, payment_truth=truth)
    # The partition: the roster leg AND the occupier's leg both carry it.
    assert out["C1"][wpt.RECORD_KEY] == truth["C1"]
    assert out["OCC-0000000000aa"][wpt.RECORD_KEY] == truth["OCC-0000000000aa"]


def test_the_engine_reads_the_occupiers_outcome_from_that_truth():
    truth = {"OCC-0000000000aa": _truth("failed", 0)}
    behavioral = _build_behavioral_trajectories(
        [], HouseholdDemandRegister([]), None, payment_truth=truth)
    bill = {"customer_id": "OCC-0000000000aa", "period_start": "2025-03-01",
            "period_end": "2025-03-31", "commodity": "gas", "segment": "resi",
            "total_amount_gbp": 102.17, "true_cost_gbp": 102.17}
    rows = [r for r in _resolve_bills([bill], behavioral, 42) if r.get("period_end")]
    if not rows:
        # A bill shape the engine asks nobody for proves nothing about whose outcome it read.
        raise AssertionError("the fixture bill was not asked of a payer; fix the fixture")
    assert rows[0]["outcome"] == "failed"
    assert wpt.LAST_COUNTS.get("truth_bills") == 1
