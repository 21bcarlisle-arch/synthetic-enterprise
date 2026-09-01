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

TWO ROUTES, TWO FILES (2026-08-31). The world is to gain a second way to leave -- drifting off the
standard variable product, C1b -- which never reaches a renewal roll. This tool writes
`<out>.json` (renewal decisions, unchanged) and, WHEN THE RUN CARRIES AN SVT RECORDER,
`<out>_svt_segment_decisions.json` (every SVT segment decision with its outcome, which is the
DENOMINATOR C1b named as owed and nothing recorded). A reader whose subject is the whole book unions
them; a reader whose subject is renewal decisions is unaffected. See the note at the write for why
they are not one file.

AND WHEN THE RUN CARRIES NO RECORDER, NO SIBLING IS WRITTEN (2026-08-31, second pass). At this HEAD
that is every run: `run_phase2b`'s return dict has 63 keys and `svt_decisions` is not one of them,
because `067a00dfd` landed the SVT PRODUCT and not the SVT departure route -- `simulation/svt_product
.py` states plainly that *"an account on this product cannot currently leave"* and that no roster
assigns one. The 1,266-row siblings under `ladder_churn_factors*` came from a working tree carrying
another lane's uncommitted roll and recorder; their producer is not in git. Finding:
`docs/staging/WORKER_FINDING_AN_EMPTY_SVT_SIBLING_WOULD_HAVE_CERTIFIED_THE_RENEWAL_ROUTE_AS_THE_WHOLE_BOOK_2026-08-31.md`.

Usage:  python3 -m tools.capture_departure_factors [output_path]
"""
import json
import sys
from pathlib import Path

from tools.departure_population import svt_sibling

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
    return emit_svt_sibling(result, out_path)


def emit_svt_sibling(result: object, out_path: Path) -> int:
    """Write the SVT sibling beside `out_path` — or deliberately not write it. Returns the rc.

    SPLIT OUT OF `main` SO IT CAN BE TESTED WITHOUT RUNNING THE WORLD. The decision below is the
    whole of the repair and `main` is a ten-minute run; a control that could only reach this by
    running the world would not have been written, which is how the defect it fixes survived.
    """
    # THE DEFAULT WAS THE DEFECT AND IT WAS FOUR CHARACTERS WIDE. This read
    # `result.get("svt_decisions", [])`, which collapses the two states the whole two-file design
    # exists to keep apart — *"the recorder ran and nobody drifted off SVT"* and *"there is no
    # recorder"* — into the SAME empty file. `departure_population.load_svt_decisions` says in its
    # own docstring that a reader must not have to tell those apart by inference, and this is the
    # only place in the chain where they are still distinguishable, because only here is the run's
    # own return dict in scope. Read with NO default so the absence survives as `None`.
    svt = result.get("svt_decisions") if isinstance(result, dict) else None
    svt_path = svt_sibling(out_path)

    if svt is None:
        # NO SIBLING IS WRITTEN, AND NOT WRITING IT IS THE REPAIR. An absent sibling is what makes
        # `departure_population.declare` report `covers_svt_route: false` with a named reason — and
        # that is TRUE of this world. `simulation/svt_product.py` says the product exists, that no
        # roster assigns it, and that *"an account on this product cannot currently leave"*;
        # `test_svt_product.py::test_no_account_is_on_the_svt_product_yet` holds it there. Writing
        # `[]` instead would flip every downstream declaration to `covers_svt_route: true`,
        # `share_of_departures_visible: 1.0`, `causes_not_observable: []` and `warning: null` — the
        # renewal route certifying its own blind spot as the whole book, off a file that measured
        # nothing.
        print(
            "  ⚠ NO SVT RECORDER IN THIS RUN. `run_phase2b` returned no `svt_decisions` key at "
            "all, so this run cannot say anything about the SVT departure route — not even that "
            "it is empty. NO SIBLING FILE WAS WRITTEN, deliberately: every reader downstream will "
            "now report `covers_svt_route: false` with its reason, which is the honest answer. An "
            "empty file here would have read as a measured zero.",
            file=sys.stderr,
        )
        if svt_path.exists():
            # A STALE SIBLING BESIDE A FRESH TABLE IS A CROSS-RUN JOIN AND IT IS REFUSED, NOT
            # DELETED. The two files would then describe two different runs while every reader
            # unions them as one capture. Refusing names it; deleting another lane's committed
            # artefact from inside a capture tool is a bigger blast radius than this needs.
            print(
                f"  ✗ REFUSING TO LEAVE {svt_path.name} BESIDE A FRESH RENEWAL TABLE. It was "
                f"written by a different run — this one has no recorder — and every reader joins "
                f"the two as one capture. Move it aside, or re-capture to a stem of its own.",
                file=sys.stderr,
            )
            return 2
        return 0

    svt_path.write_text(json.dumps(svt, indent=1))
    departed = sum(1 for r in svt if r.get("event_type") == "churned")
    print(f"captured {len(svt)} SVT segment decisions ({departed} departed) -> {svt_path}")
    if not svt:
        # A MEASURED ZERO, AND IT IS NOW SAFE TO WRITE ONE. Reaching here means the key was
        # PRESENT: the recorder ran and found nobody on the product. That is a reading over both
        # routes which found nothing on one, and `declare_rows` is right to call it coverage.
        print(
            "  ⚠ THE SVT RECORDER RAN AND RECORDED NOTHING. Nobody sat on the standard variable "
            "product in this run. This is a measured zero and not a missing measurement — the "
            "missing case writes no file at all.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    raise SystemExit(main(target))
