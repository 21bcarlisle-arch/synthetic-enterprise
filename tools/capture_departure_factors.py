"""Capture the per-renewal factor table the C2 competing-risks calibration is fitted on.

WHY THIS EXISTS AND WHY IT IS NOT A SECOND RUN OF THE WORLD. C2's P0 calibration
(`docs/staging/WORKER_PREREGISTRATION_WHAT_A_DEPARTURE_WITH_A_CAUSE_MUST_SHOW_2026-08-30.md`)
has to fit the per-cause sensitivities so that population-mean realised churn does not move. That
fit needs the JOINT distribution of every factor the composed form multiplies together -- bill
shock, market opportunity, felt price position, income stress, tenure, satisfaction -- and the
published event log carries only three of them. The rest arrive as ARGUMENTS to
`simulation.customer_events.roll_lifecycle_event` and are discarded once it returns.

So this wraps that one function, records its arguments beside the event it returned, and runs the
world ONCE. The wrapper does not change a single number: it calls the real function and passes the
real return value straight back, which is what makes the captured table a description of the
CURRENT world rather than of a reimplementation of it. Fitting against a reimplementation is how a
calibration comes out right about a world that does not exist.

Point-in-time is not at risk here: nothing captured is fed back into the run, and the file is
written after `main()` returns.

Usage:  python3 -m tools.capture_departure_factors [output_path]
"""
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT / "docs" / "reports" / "c2_departure_factors.json"


def main(out_path: Path) -> int:
    import simulation.run_phase2b as rp2b

    captured: list[dict] = []
    # PATCH THE CALLER'S NAMESPACE, NOT THE DEFINING MODULE'S. `run_phase2b` does
    # `from simulation.customer_events import roll_lifecycle_event`, so the name is bound in ITS
    # module dict and rebinding `customer_events.roll_lifecycle_event` captures nothing at all --
    # the run would complete, the file would be written, and it would be EMPTY rather than wrong,
    # which is the failure mode that reads as success. Same trap `tools/_ladder_chase_arm.py`
    # documents for `pressure_ledger_scope`.
    original = rp2b.roll_lifecycle_event

    def capturing(*args, **kwargs):
        event = original(*args, **kwargs)
        if event is None:
            return None
        stress = kwargs.get("income_stress")
        row = {
            "customer_id": event["customer_id"],
            "event_date": event["event_date"],
            # The factor arguments, exactly as the world handed them over.
            "income_stress": stress.value if stress is not None else None,
            "satisfaction_score": kwargs.get("satisfaction_score"),
            "market_year": kwargs.get("market_year"),
            "passive_churn_cap": kwargs.get("passive_churn_cap"),
            "retention_modifier": kwargs.get("retention_modifier"),
            "new_rate_gbp_per_mwh": kwargs.get("new_rate_gbp_per_mwh"),
            # And what the composed form actually produced from them.
            "churn_probability": event["churn_probability"],
            "realized_churn_probability": event["realized_churn_probability"],
            "effective_retention_probability": event["effective_retention_probability"],
            "price_differential_vs_market_reference": event.get(
                "price_differential_vs_market_reference"),
            "market_switching_multiplier": event.get("market_switching_multiplier"),
            # The C2 factor decomposition, emitted by `roll_lifecycle_event` itself.
            "sim_bill_shock_base": event.get("sim_bill_shock_base"),
            "sim_market_opportunity": event.get("sim_market_opportunity"),
            "sim_price_response": event.get("sim_price_response"),
            "sim_action_propensity": event.get("sim_action_propensity"),
            "sim_dissatisfaction_response": event.get("sim_dissatisfaction_response"),
            # The year's level term and the risk that fired. Captured so the departure
            # decomposition can be replayed from this table alone: with the factors, the anchor
            # and the roll, `resolve_departure` reproduces the cause exactly, which is what lets
            # the realised reason mix be measured without a second run of the world.
            "sim_level_anchor": event.get("sim_level_anchor"),
            "departure_cause": event.get("departure_cause"),
            # `is_active_renewal` and `engagement_level` are NOT captured here: the caller sets
            # them on the event dict AFTER this function returns, so they are absent at this
            # point. They are joined back from the published event log on (customer_id,
            # event_date) instead. Reading them here would record None for all 708 rows.
            "event_type": event["event_type"],
            "random_roll": event["random_roll"],
        }
        captured.append(row)
        return event

    rp2b.roll_lifecycle_event = capturing
    try:
        rp2b.main()
    finally:
        rp2b.roll_lifecycle_event = original

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(captured, indent=1))
    print(f"captured {len(captured)} renewal factor rows -> {out_path}")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    raise SystemExit(main(target))
