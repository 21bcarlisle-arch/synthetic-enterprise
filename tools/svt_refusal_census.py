"""What the arm's product gate refuses, counted in the unit the WORLD built it in.

WHY THIS EXISTS (2026-09-19)
----------------------------
`renewal_funnel` publishes `product_not_upliftable = 2490`, 88.2% of the 2,824 renewals the
world offered, and it is the single largest drop in the value arm's funnel. Two readings of that
integer license opposite work and the funnel cannot tell them apart:

  * 2,490 HOUSEHOLD DECISIONS the company is blind to  -> the gate is the ceiling on the
    method's reach, and relaxing it is the highest-value thing available.
  * 2,490 CAP SEGMENTS inside far fewer household boundaries, at none of which this supplier
    struck a rate -> the gate is the BOUNDARY OF THE SUBJECT and relaxing it buys nothing.

The funnel's unit is the TERM — one row per `decide_renewal_rate` call
(`simulation/run_phase2b.py`, inside the chronological term loop). A passive renewal roll does
not emit one term: `simulation.svt_product.build_svt_schedule` emits ONE SEGMENT PER CAP PERIOD
for the whole stint, and every segment is its own row. So the refused count is a count of cap
periods, and the number of boundaries behind it is not readable from the funnel at all.

WHAT THIS COUNTS, SAID BEFORE ANYTHING IS DIVIDED
-------------------------------------------------
Three units, never mixed, each named on its own key:

  SEGMENT   one row emitted by `build_svt_schedule` — one published cap period. The unit the
            funnel counts and the unit the gate refuses.
  STINT     one CALL of `build_svt_schedule` — one unbroken spell on the default tariff,
            beginning at the boundary where `renewal_engagement.rolls_active_renewal` came up
            passive. The stint is taken from the call boundary and is NOT re-derived by scanning
            for contiguous SVT segments: two consecutive passive rolls emit contiguous segments,
            and a contiguity scan silently merges them (it read 280 stints where there are 986).
  BOUNDARY  the anniversary that TERMINATES a stint, at which the builder's loop re-enters and
            `rolls_active_renewal` is asked again. This is the only unit at which a household
            decides anything, and there is at most one per stint.

THE CLASS SPLIT THIS EXISTS TO PUBLISH. A stint's terminating boundary is reached iff the
anniversary falls inside the window — that IS the builder's `while term_start <= report_end`,
read rather than restated. So:

  a_decision_follows    the stint ends at a live boundary; the household is asked again.
  no_decision_follows   the stint runs past the window end; the household is never asked
                        inside this world. At most one per leg, and the count equals the number
                        of legs that end the window on the cap — which is the control on it.

THIS CENSUS IS PRE-CHURN AND SAYS SO. It reads the schedules the world BUILDS. `renewal_funnel`
counts what REACHED THE ARM and is already net of two world-side exclusions the chain never sees
(a term on an account that had already churned; an unactivated successor term). The two
populations are different and this module never divides one by the other: `population` names
which one every count here belongs to, so a reader cannot take a share from this census and
apply it to the funnel's without noticing.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts that most stints end at a
live boundary, or that segments outnumber boundaries. Feed it a world whose households never
roll and every count is zero and it says so; feed it one whose cap stints are absorbing and
`no_decision_follows` carries all of them. R12: a diagnostic. No count here is a target, and
specifically this is not a cue to relax `UPLIFTABLE_TARIFF_TYPES` so the refused count falls.

REUSE
-----
REUSE: tools/svt_refusal_census.py
CLASS: CUSTOM
INDEX: searched "svt refusal census", "product gate", "product_not_upliftable", "tariff type",
       "renewal funnel", "stint", "cap segment", "rolls_active_renewal", "decisions that
       existed".
       `tools/product_gate_refusal.py` reads the funnel's `product_not_upliftable_by_tariff_type`
       and says WHICH PRODUCTS were refused; it has no access to the world that built them and
       cannot say how many boundaries they sit inside. It answers a different question in the
       funnel's own unit and is not extended here.
       `tools/decisions_by_account_class.py` splits the DECISION population by how an account
       joined the book — the terms that got PAST the gate. This is the other side of the same
       gate and neither reads the other.
       `tools/decisions_that_existed.py` owns the membership rule over funnel stages and is
       about the arm's stage vocabulary; this module never touches a funnel.
       `simulation.svt_product.build_svt_schedule` is the PRODUCER and is instrumented rather
       than re-implemented: the stint is its call, so a change to how a stint is built moves
       this census without anybody editing it.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta

#: The census's own population, stamped on the result so a share taken from here cannot be
#: applied to a funnel count without the reader seeing that they are different censuses.
POPULATION = (
    "the schedules the world BUILDS, before the two world-side exclusions `renewal_funnel` is "
    "already net of (a term on an account that had already churned; an unactivated successor "
    "term). A count here is never comparable term-for-term with a funnel count."
)


def census(report_end: str | None = None) -> dict:
    """Build every leg's renewal schedule and count the refused SVT terms three ways.

    Imports are function-local: this module is a diagnostic and importing it must not draw the
    population as a side effect of `simulation.run_phase2b`'s module body.
    """
    import simulation.renewals as renewals_mod
    import simulation.run_phase2b as p2b
    from sim.cache_store import get_cached_prices
    from sim.gas_prices_history import load_nbp_history
    from simulation.renewals import build_renewal_schedule

    end = p2b.effective_report_end(report_end)

    # ONE STINT IS ONE CALL. Wrapping the producer is what makes the stint the world's own unit
    # rather than this module's guess at it — see the module docstring on the contiguity scan
    # that got it wrong. Both builders are wrapped because each imported the name separately.
    calls: list[dict] = []

    def _wrap(real):
        def inner(customer_id, original_acquisition_date, report_end_date, price_records,
                  lookback_temps_fn=None, *, fuel):
            segments = real(customer_id, original_acquisition_date, report_end_date,
                            price_records, lookback_temps_fn=lookback_temps_fn, fuel=fuel)
            calls.append({
                "customer_id": customer_id, "fuel": fuel,
                "stint_start": original_acquisition_date, "segments": len(segments),
            })
            return segments
        return inner

    real_elec, real_gas = renewals_mod.build_svt_schedule, p2b.build_svt_schedule
    renewals_mod.build_svt_schedule = _wrap(real_elec)
    p2b.build_svt_schedule = _wrap(real_gas)
    try:
        earliest = min(date.fromisoformat(c["acquisition_date"])
                       for c in p2b.ELEC_CUSTOMERS + p2b.GAS_CUSTOMERS)
        elec_records = get_cached_prices(
            max((earliest - timedelta(days=365)).isoformat(), p2b.EARLIEST_SSP_DATE), end)
        if elec_records is None:
            return {"available": False, "why": (
                "no cached SSP range covers this window, and this diagnostic will not reach the "
                "network to build one — run the sim's own fetch first")}
        gas_records = load_nbp_history()

        # eac_kwh and lookback temperatures reach only `generate_forward_price`. They move every
        # RATE in the schedule and no date, no tariff type and no roll, so the structure this
        # census counts is identical to the run's. A nominal EAC here is not a fabricated domain
        # constant: it is an argument this census does not read back.
        schedules: dict[tuple[str, str], list[dict]] = {}
        for c in p2b.ELEC_CUSTOMERS:
            schedules[("electricity", c["customer_id"])] = build_renewal_schedule(
                c["customer_id"], c["acquisition_date"], end, elec_records, 3100,
                segment=c.get("segment", "resi"),
                tariff_type=p2b.resolved_tariff_type(c),
                deemed_gap_days=c.get("deemed_gap_days", 0))
        for c in p2b.GAS_CUSTOMERS:
            schedules[("gas", c["customer_id"])] = p2b._build_gas_renewal_schedule(
                c, gas_records, report_end=end, tariff_type=p2b.resolved_tariff_type(c))
    finally:
        renewals_mod.build_svt_schedule = real_elec
        p2b.build_svt_schedule = real_gas

    return classify(calls, schedules, end)


def classify(calls: list[dict], schedules: dict, window_end: str) -> dict:
    """Count the refused SVT terms three ways, from stints already observed.

    SEPARATE FROM `census` SO IT CAN BE REFUTED WITHOUT BUILDING A WORLD. The counting rules
    here are where this module's defects live — the stint unit, the class rule, the identity
    control — and a rule reachable only behind a two-minute schedule build is a rule nobody
    mutates. `calls` is one dict per `build_svt_schedule` call; `schedules` is keyed
    `(commodity, customer_id)`.
    """
    from simulation.renewals import CONTRACT_LENGTH_DAYS
    from simulation.svt_product import SVT_TARIFF_TYPE

    end_d = date.fromisoformat(window_end)
    segments = Counter()
    stints = Counter()
    per_stint = Counter()
    for call in calls:
        anniversary = (date.fromisoformat(call["stint_start"])
                       + timedelta(days=CONTRACT_LENGTH_DAYS))
        call["cls"] = ("a_decision_follows" if anniversary <= end_d
                       else "no_decision_follows")
        segments[call["cls"]] += call["segments"]
        stints[call["cls"]] += 1
        per_stint[call["segments"]] += 1

    # WHICH WAY THE TERMINATING ROLL WENT, read off the schedule AT the anniversary rather than
    # inferred from what sits next to the stint. Adjacency cannot tell a new stint from a
    # continuation, which is the same trap the stint unit itself fell into.
    # KEYED OFF THE SCHEDULE'S OWN KEY, NOT OFF THE TERM. Not every builder stamps
    # `customer_id` into every row it emits — the gas builder does not — and reading it from the
    # row raised `KeyError` on the first real world this was pointed at. The owning leg is
    # already the dict key here and cannot be missing.
    kind_at = {(cid, t["acquisition_date"]): t.get("tariff_type")
               for (_commodity, cid), sched in schedules.items() for t in sched}
    rolled = Counter()
    for call in calls:
        if call["cls"] != "a_decision_follows":
            continue
        anniversary = (date.fromisoformat(call["stint_start"])
                       + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()
        kind = kind_at.get((call["customer_id"], anniversary))
        rolled["passive" if kind == SVT_TARIFF_TYPE
               else "no_term_emitted" if kind is None else "active"] += 1

    term0 = Counter()
    decision_eligible = 0
    for sched in schedules.values():
        for index, term in enumerate(sched):
            if index == 0:
                term0[term.get("tariff_type")] += 1
            elif term.get("tariff_type") != SVT_TARIFF_TYPE:
                decision_eligible += 1

    first_term_start = {
        cid: sched[0]["acquisition_date"]
        for (_commodity, cid), sched in schedules.items() if sched
    }
    total_segments = sum(segments.values())
    total_stints = sum(stints.values())
    return {
        "available": True,
        "population": POPULATION,
        "window_end": window_end,
        "legs": len(schedules),
        "terms_total": sum(len(s) for s in schedules.values()),
        "svt_segments_total": total_segments,
        "svt_stints_total": total_stints,
        # A RATIO OF TWO UNITS, AND IT NAMES BOTH. Segments per stint is the whole reason the
        # funnel's integer misreads: it is how many funnel rows one household boundary produces.
        "segments_per_stint_mean": (round(total_segments / total_stints, 4)
                                    if total_stints else None),
        "segments_per_stint_histogram": dict(sorted(per_stint.items())),
        "class_a_decision_follows": {
            "segments": segments["a_decision_follows"],
            "stints": stints["a_decision_follows"],
            "boundaries": stints["a_decision_follows"],
            "terminating_roll_came_up_active": rolled["active"],
            "terminating_roll_came_up_passive": rolled["passive"],
            "terminating_roll_emitted_no_term": rolled["no_term_emitted"],
            "what_this_counts": (
                "stints whose anniversary falls inside the window, so the builder's loop "
                "re-enters and `rolls_active_renewal` decides again. `boundaries` equals "
                "`stints` because a stint has exactly one terminating anniversary — it is the "
                "same event counted under the name of the unit a reader is asking about."
            ),
        },
        "class_no_decision_follows": {
            "segments": segments["no_decision_follows"],
            "stints": stints["no_decision_follows"],
            "what_this_counts": (
                "stints running past the window end: the household is never asked again inside "
                "this world. At most one per leg."
            ),
        },
        # THE CONTROL ON THE SPLIT, and it is an identity rather than a second opinion: a stint
        # with no decision after it can only be a leg's last, so the count must equal the legs
        # that end the window on the cap. If these diverge the class rule is wrong.
        "legs_ending_the_window_on_svt": sum(
            1 for s in schedules.values()
            if s and s[-1].get("tariff_type") == SVT_TARIFF_TYPE),
        "term0_by_tariff_type": dict(term0),
        "decision_eligible_terms": decision_eligible,
        "what_decision_eligible_counts": (
            "non-SVT terms at term index >= 1 in the built schedule: the terms that clear the "
            "gate AND the acquisition-term rule. This census's own analogue of the funnel's "
            "`decisions_that_existed`, over this census's own population, and NOT the same "
            "number — it is pre-churn. The funnel's remaining guard, `no_observed_history`, is "
            "not readable from a schedule and is 0 on the live funnel."
        ),
        "arrival_origin_stints": sum(
            1 for call in calls
            if first_term_start.get(call["customer_id"]) == call["stint_start"]),
        "what_arrival_origin_counts": (
            "stints beginning at the leg's own first term — a household that ARRIVED on the "
            "default tariff rather than rolling onto it mid-tenure. Zero here is the check on "
            "`run_phase2b`'s claim that no caller mints a default-tariff arrival today."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    print(json.dumps(census(), indent=1))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
