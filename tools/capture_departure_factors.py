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

TWO ROUTES, TWO FILES (2026-08-31). The world now has a second way to leave -- drifting off the
standard variable product, C1b -- which never reaches a renewal roll. This tool writes
`<out>.json` (renewal decisions, unchanged) and `<out>_svt_segment_decisions.json` (every SVT
segment decision with its outcome, which is the DENOMINATOR C1b named as owed and nothing recorded).
A reader whose subject is the whole book unions them; a reader whose subject is renewal decisions
is unaffected. See the note at the write for why they are not one file.

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
            # THE INDEPENDENT COMPANY BELIEF, AND IT IS HERE SO THE NEXT READING NEED NOT JOIN.
            # `company.crm.churn_model.estimate_churn_probability` is the only company-side belief
            # that does NOT seed `effective_p_retain`, so it is the one leg on this route that can
            # be graded against the world's ceiling without the tautology `build_churn_risk` has.
            # Captures taken before 2026-08-31 lack it, and `measure_churn_heterogeneity` joins it
            # from the run output for those -- a cross-artefact join it has to verify row by row.
            # Recording it here retires that join rather than leaving a second code path alive.
            "company_churn_estimate": event.get("company_churn_estimate"),
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
        result = rp2b.main()
    finally:
        rp2b.roll_lifecycle_event = original

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(captured, indent=1))
    print(f"captured {len(captured)} renewal factor rows -> {out_path}")

    # ─────────────────────────────────────────────────────────────────────────────────────────
    # THE SECOND ROUTE, IN A SECOND FILE, AND THE SEPARATION IS THE POINT
    # ─────────────────────────────────────────────────────────────────────────────────────────
    # C1b gave SVT accounts a way to leave that never reaches a renewal roll, so this tool -- and
    # therefore `fit_year_level_anchor`, `measure_departure_level` and the C2 reason mix -- went
    # from seeing the whole book to seeing a minority of it, silently, on the commit that landed
    # the route. Nothing went red: the table still had 465 rows of the population it could see.
    #
    # NOT UNIONED INTO `out_path`. An SVT decision carries no `churn_probability`, no
    # `sim_price_response` and no `sim_bill_shock_base` -- there was no renewal decision for any of
    # them to describe. Appending them to the renewal table would hand every existing reader rows
    # whose keys are None and let a mean be taken over two populations. Two files, and the reader
    # that wants the whole book unions them deliberately, per the note in `run_phase2b`.
    svt = result.get("svt_decisions", []) if isinstance(result, dict) else []
    svt_path = out_path.with_name(out_path.stem + "_svt_segment_decisions.json")
    svt_path.write_text(json.dumps(svt, indent=1))
    departed = sum(1 for r in svt if r.get("event_type") == "churned")
    print(f"captured {len(svt)} SVT segment decisions ({departed} departed) -> {svt_path}")
    if not svt:
        # LOUD, BECAUSE AN EMPTY SECOND FILE READS EXACTLY LIKE A BOOK WITH NOBODY ON SVT.
        print(
            "  ⚠ NO SVT SEGMENT DECISIONS CAPTURED. Either no account sat on the standard variable "
            "product in this run, or `run_phase2b` stopped populating `svt_decisions`. Those are "
            "very different and this tool cannot tell them apart — check before reading any rate "
            "computed from this file.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    raise SystemExit(main(target))
