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

AND WHEN THE RUN CARRIES NO RECORDER, NO SIBLING IS WRITTEN (2026-08-31, second pass). That branch
is still live and still the repair -- see `emit_svt_sibling` -- but the sentence that used to stand
here, *"at this HEAD that is every run"*, IS NO LONGER TRUE and this note is what a reader consults
before deciding whether re-capturing is worth a ten-minute run. `run_phase2b` now carries the
recorder: `_svt_decisions` is built and returned under the `svt_decisions` key. It landed at
`6db30a350`, whose headline claim is about the SVT belief telling two households apart -- which is
why a finding filed one lane over on 2026-09-01 could still call the recorder outstanding in good
faith, and why the correction is dated here rather than silently applied.

WHAT THAT CHANGES FOR A READER OF THE COMMITTED ARTEFACTS, WHICH IS THE PART THAT BITES. Every SVT
sibling committed before 2026-09-01 -- the 1,266-row files under `ladder_churn_factors*` -- came
from a working tree carrying another lane's uncommitted roll and recorder, so their producer is in
no commit, and their renewal table is a DIFFERENT RUN (144 renewal decisions over 68 accounts
against 1,266 SVT decisions over 116 accounts, only 53 shared). A capture taken from this HEAD is
the first whose two files describe ONE RUN. Do not difference a cell across the two: that measures
the population, not the hazard.

BUT "ONE RUN" IS NOT "IN GIT", AND THE SECOND HALF OF THAT REPAIR IS STILL OWED (2026-09-01, third
pass). The RECORDER is committed at `6db30a350`. What is missing is what puts an account ON the SVT
product, so that the recorder has anything to record: at this HEAD `simulation/svt_product.py` still
says in its own docstring that *"no roster writes that"*. (That phrase was removed from
`svt_product.py` on 2026-09-04 because it had stopped being true; this paragraph is kept as the
dated observation it was, and the quotation is no longer expected to resolve.) So whether this tool
writes a populated
sibling or an empty one is decided by the WORKING TREE, not by the commit: run it on a clean checkout
of this HEAD and `emit_svt_sibling` prints `THE SVT RECORDER RAN AND RECORDED NOTHING`. Record the
tree state you ran on; do not read a populated sibling as evidence that the route is in git. Finding:
`docs/staging/done/WORKER_FINDING_THE_SVT_RECORDER_IS_IN_GIT_AND_THE_ROLL_THAT_FILLS_IT_IS_NOT_2026-09-01.md`.

    MEASURED 2026-09-01, fourth pass, and the paragraph above is CONFIRMED as a prediction and
    CORRECTED as a locator. A clean-tree run (`68ec6825b` == `origin/main`, every producer verified
    committed) printed `THE SVT RECORDER RAN AND RECORDED NOTHING` and captured 0 SVT segment
    decisions, exactly as promised. But it is NOT true that the missing piece is "the roll", and it
    was never `56 uncommitted lines in simulation/renewals.py`:

      * `rolls_active_renewal` is not in `renewals.py` and never has been. It is committed, at
        `simulation/renewal_engagement.py:65`, and is CALLED every renewal at `run_phase2b.py:1771`.
      * `build_svt_schedule` is likewise committed and called at `renewals.py:101` -- but only under
        `if tariff_type == SVT_TARIFF_TYPE`, which nothing ever writes.
      * The roll's answer feeds exactly one thing, `passive_churn_cap_for`, and then STOPS.
        `build_renewal_schedule` never receives it.

    So the gap is the ASSIGNMENT, not the roll: the world already decides, per household and against
    an Ofgem-anchored rate, who rolls onto SVT -- and then builds them a fixed term anyway. See
    `docs/staging/WORKER_FINDING_THE_WORLD_ALREADY_DECIDES_WHO_ROLLS_TO_SVT_AND_THEN_DISCARDS_THE_ANSWER_2026-08-30.md`,
    which scoped this correctly in August: *"not a missing rule, a discarded answer"*.

    WHY THE DISTINCTION IS WORTH THESE LINES, given the prediction was right either way. A reader
    who believes the roll is uncommitted goes looking for lost work to recover, and there is none to
    find. A reader who knows the roll is committed and DISCARDED goes to the one call site that
    drops it. The first search ends in a wrong conclusion about provenance; only the second ends in
    the repair. Grading:
    `docs/staging/WORKER_PREREGISTRATION_WHAT_A_RERUN_FROM_THE_CLEAN_TREE_MUST_SHOW_2026-09-01.md`.

    THE DIAGNOSIS ABOVE IS RIGHT AND ITS LAST PARAGRAPH IS WRONG (2026-09-01, fifth pass, the other
    lane, merged at `a70a7ceff`). The gap WAS the assignment — and the assignment existed, as
    uncommitted work, in this tree, while the paragraph above was being written. It is now committed
    at `8bf416115`, so at this HEAD every bullet above is false and the line numbers they cite have
    moved:

      * `rolls_active_renewal` IS in `renewals.py` — imported at line 42, called at line 154 inside
        `build_renewal_schedule`, which is the receiver the third bullet says never gets it.
      * `build_svt_schedule` has a SECOND call site at line 159, reached on the passive branch. The
        `if tariff_type == SVT_TARIFF_TYPE` gate at line 103 is still there and still unwritten-to;
        it was never the route.
      * `run_phase2b.py`'s call moved to line 1772.

    WHAT ACTUALLY WENT WRONG, WHICH IS WORTH MORE THAN THE LINE NUMBERS. The refutation was reached
    by inspecting the COMMITTED tree — `git show`, committed line numbers, a clean checkout — to
    disprove a claim whose entire subject was UNCOMMITTED. That method cannot return anything but
    "not there", for a true claim and a false one alike, so it could not have failed. **A claim about
    uncommitted work cannot be refuted from the committed tree**; it is refuted by reading the
    working tree, or it is not refuted.

    The cost was nearly 421 lines: the 56-line assignment, and `tests/simulation/test_svt_assignment.py`
    — nine tests with their R15 mutations already recorded — which was UNTRACKED and therefore
    invisible to every committed-tree search, `tests_for()` included. *"There is none to find"* is
    the sentence that would have stopped the next reader looking, and this is the
    `uncommitted_and_orphaned_work` class doing exactly what that register says it does. Finding:
    `docs/staging/done/WORKER_FINDING_A_CLAIM_ABOUT_UNCOMMITTED_WORK_WAS_REFUTED_FROM_THE_COMMITTED_TREE_2026-09-01.md`.

    Both lanes were right about their own tree and neither could see the other's: the clean-tree run
    correctly found an empty sibling BECAUSE the assignment was not yet committed. Re-running the
    capture from this HEAD is now a different experiment from either, and is owed.

Findings on the foreign artefact:
`docs/staging/WORKER_FINDING_AN_EMPTY_SVT_SIBLING_WOULD_HAVE_CERTIFIED_THE_RENEWAL_ROUTE_AS_THE_WHOLE_BOOK_2026-08-31.md`,
`docs/staging/WORKER_FINDING_A_FOREIGN_SVT_SIBLING_IS_WHAT_MAKES_THE_ACCOUNT_DENOMINATOR_CONTROL_PASS_2026-08-31.md`.

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
        # `departure_population.declare` report `covers_svt_route: false` with a named reason.
        #
        # THE REASON CHANGED UNDER THIS BRANCH AND THE BRANCH DID NOT (2026-09-04). It used to read
        # that `simulation/svt_product.py` says no roster assigns the product and that *"an account
        # on this product cannot currently leave"*, held there by
        # `test_svt_product.py::test_no_account_is_on_the_svt_product_yet` — so an absent sibling
        # was a FACT ABOUT THE WORLD. All three clauses are now false: C1b
        # (`simulation/renewals.py`) assigns mid-tenure from the household's own engagement roll
        # and never touches the roster, `svt_product.inertia_hazard_for_term` gives the product a
        # departure hazard, and that interlock was retired and re-keyed to
        # `test_an_account_on_the_svt_product_can_leave_it`. Most of this book now lives on SVT and
        # can leave it.
        #
        # So the refusal stands and its meaning has inverted: a missing `svt_decisions` key is a
        # RECORDER GAP in this run, not a world with nothing to record. `covers_svt_route: false`
        # is still the honest declaration — but a reader who hits it should now go looking for why
        # the recorder did not run, rather than concluding the route is empty by construction.
        #
        # Writing `[]` instead would flip every downstream declaration to `covers_svt_route: true`,
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
