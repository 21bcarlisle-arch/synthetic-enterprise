"""C2's reason mix, published as an INTERVAL over the parameter no instrument identifies.

Pre-registration: `docs/staging/WORKER_PREREGISTRATION_WHAT_A_DEPARTURE_WITH_A_CAUSE_MUST_SHOW_2026-08-30.md`.
The non-identification: `docs/staging/WORKER_FINDING_THE_P0_CALIBRATION_IS_EITHER_INFEASIBLE_OR_IT_CHOOSES_THE_ANSWER_2026-08-30.md`.
Level anchor: `simulation/departure_level_anchor.py`; `tools/fit_year_level_anchor.py`.

WHAT THIS TOOL USED TO BE, AND WHY IT IS NOT THAT ANY MORE. It fitted C2's P0 calibration -- one
global sensitivity scale bisected onto the population mean of the composed form, so the LEVEL would
be held and the DECOMPOSITION would be the only thing that moved. That question is closed twice
over. P0 came back NON-IDENTIFYING (every `a_shock` from 0.87 down reproduced the mean exactly while
the reason mix ran from 99.9% to 56.6% bill-shock), and then the level anchor DISCHARGED the
equation P0 was: the year's level is the published record's, so there is no population mean left for
a scale to hit. Fitting it again would be fitting to a constraint that is already satisfied by
construction, which is the shape of a calibration that reports its own inputs.

WHAT IS LEFT IS THE THING THAT WAS ALWAYS THE MEASUREMENT: the reason mix. And its parameter is
still free. No domestic instrument separates "my own bill rose" from "someone else is cheaper" --
Ofgem's Consumer Impacts survey codes both as one answer, and only the non-domestic instrument
splits them, on a population the evidence records as differing in kind. So the feasible FAMILY is
swept -- `(a_shock, scale)` pairs, both coordinates, because that is the shape the set has -- and the
mix is reported as an INTERVAL over it, never as a point. A point would be this project publishing
its own free parameter back as a finding.

THE LEVEL IS RE-ANCHORED AT EVERY POINT OF THE SWEEP, which is what makes the interval about the
mix alone. Without that, moving `a_shock` would move the level too and the interval would be over
two things at once -- and the reader would have no way to tell which one it was reading.

WHAT THE INTERVAL IS NOT ALLOWED TO BE CHECKED AGAINST HERE. The published mover-mix (why people
say they switched) is reserved by the roadmap as a CHECK on this output. Identifying `a_shock` from
it and then reporting agreement with it would be a tautology wearing a validation.

Usage:  python3 -m tools.fit_departure_hazards [factor_table.json]
"""
import collections
import json
import statistics
import sys
from pathlib import Path

from simulation.departure_risks import (
    DECLARED_SENSITIVITY_SCALE,
    DECLARED_SHOCK_WEIGHT,
    ORDERED_CAUSES,
    build_departure_risks,
    cause_shares,
    total_departure_probability,
)
from simulation.market_switching_propensity import market_departure_rate
from tools.departure_population import ROUTE_CAUSES, ROUTE_RENEWAL, banner, declare

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_TABLE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"
MIX_ARTEFACT = PROJECT / "docs" / "reports" / "c2_reason_mix_interval.json"

#: The feasible family, verbatim from the P0 finding's own measured table: `(a_shock, scale)` PAIRS,
#: not a sweep of `a_shock` at a fixed scale.
#:
#: THE PAIR IS THE POINT AND THE FIRST DRAFT OF THIS SWEPT ONE COORDINATE. `a_shock` alone, at the
#: declared scale, gives a mix interval of 55%-68% bill-shock, which looks like a reassuringly
#: narrow result and is an artefact of holding the other coordinate still. The feasible SET is the
#: family that satisfied P0, along which BOTH moved together -- and across it the mix runs from
#: 99.9% to 56.6%. Publishing the one-coordinate slice would have understated the bound by more
#: than 40pp while carrying the word "interval".
#:
#: 0.87 is where the P0 fit first became feasible; 0.50 is the far end the finding measured to. The
#: world runs at the last row -- see `DECLARED_SHOCK_WEIGHT` for why that is a fidelity choice under
#: R13 and not a tie-break -- and the page carries the whole range as the bound the declared point
#: does not have.
FEASIBLE_PAIRS = (
    (0.87, 0.000053),
    (0.80, 0.007649),
    (0.70, 0.018395),
    (0.60, 0.029018),
    (0.50, 0.039520),
)


def _risks_for(row: dict, pair: tuple[float, float], anchor: float) -> dict[str, float]:
    """The competing risks for one captured renewal.

    `retention_offer_retained_fraction` is deliberately 1.0: the quantity being anchored is
    `realized_churn_probability`, captured BEFORE any retention offer, so including the offer here
    would compare a post-intervention probability against a pre-intervention record.
    """
    return build_departure_risks(
        bill_shock_base=row["sim_bill_shock_base"],
        price_response=row["sim_price_response"],
        dissatisfaction_response=row["sim_dissatisfaction_response"],
        market_opportunity=row["sim_market_opportunity"],
        action_propensity=row["sim_action_propensity"],
        retention_offer_retained_fraction=1.0,
        shock_weight=pair[0],
        sensitivity_scale=pair[1],
        level_anchor=anchor,
    )


def _anchor_for(rows: list[dict], pair: tuple[float, float], target: float) -> float:
    """Bisect this year's anchor onto the published rate at this `(a_shock, scale)` pair.

    Same bisection as `tools/fit_year_level_anchor.py` and deliberately not imported from it: that
    tool derives the anchor the WORLD runs at, at the declared pair, and is the thing whose output
    is committed. This one re-anchors at every sweep point so the interval is about the mix alone.
    A shared helper would make it too easy to change one and silently move the other.
    """
    lo, hi = 0.0, 1.0
    for _ in range(60):
        if statistics.fmean(
            total_departure_probability(_risks_for(r, pair, hi)) for r in rows
        ) >= target:
            break
        hi *= 2.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        mean = statistics.fmean(
            total_departure_probability(_risks_for(r, pair, mid)) for r in rows
        )
        if mean < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


#: The causes this sweep's population can express, and it is a STRICT SUBSET of `ORDERED_CAUSES`.
#:
#: WHY THE LIST IS NARROWED RATHER THAN LEFT TO COME OUT OF THE ARITHMETIC, and this is the trap
#: that made the repair urgent. `build_departure_risks` defaults `svt_inertia` to 0.0 and no
#: renewal row carries `sim_svt_inertia`, because a renewal decision is not an SVT segment. So
#: sweeping over `ORDERED_CAUSES` would have published `svt_inertia: 0.0%` -- a well-formed number
#: that every reader takes for "almost nobody leaves this way", when C1b measured it as 50 of 82
#: departures on the same capture and `departure_risks` calls it the single largest departure route
#: in a real domestic book. **A quantity this population cannot observe must arrive as `None` with
#: a reason, never as a small number.**
MIX_CAUSES = ROUTE_CAUSES[ROUTE_RENEWAL]

#: Why the causes outside `MIX_CAUSES` are absent, carried into the artefact so the page can say it
#: rather than a reader having to know it.
UNOBSERVABLE_REASON = (
    "This mix is a decomposition of the RENEWAL hazard, taken over renewal decisions. C1b added a "
    "second departure route -- an account drifting off the standard variable product at a segment "
    "boundary -- which strikes no rate and reaches no renewal roll, so no row in this population "
    "can carry it. Its share here is UNKNOWN, not zero."
)

#: THE ONLY NUMBER ANYONE HAS FOR THE SVT ROUTE, AND IT IS NOT A MEASUREMENT OF THIS WORLD.
#:
#: This sentence used to end `UNOBSERVABLE_REASON` as a bare *"on the two-route capture of
#: 2026-08-31 it was 50 of 82 departures"*, sitting inside the published mix artefact with nothing
#: to say where it came from. It came from `docs/reports/ladder_churn_factors_svt_segment_decisions
#: .json`, which is committed and whose PRODUCER IS IN NO COMMIT: `run_phase2b` has no
#: `_svt_decisions` recorder, `simulation/svt_product.py` says no roster assigns the product and
#: that an account on it cannot leave, and `test_svt_product.py::test_no_account_is_on_the_svt_
#: product_yet` holds that. So the figure describes a world with an SVT departure route -- not this
#: one -- and a reader had no way to tell.
#:
#: Kept rather than deleted, because it is the only size estimate the route has and deleting it
#: would leave the reader with no sense of scale at all. Separated and attributed, because an
#: unattributed one reads as this world's answer. Finding:
#: `docs/staging/WORKER_FINDING_A_FOREIGN_SVT_SIBLING_IS_WHAT_MAKES_THE_ACCOUNT_DENOMINATOR_CONTROL_PASS_2026-08-31.md`.
UNOBSERVABLE_SCALE_HINT = (
    "The only figure anyone has for this route's size is 50 of 82 departures, and it is NOT a "
    "reading of this world: it comes from `docs/reports/ladder_churn_factors_svt_segment_"
    "decisions.json`, an artefact that is committed but whose producer is in no commit. This "
    "world has no SVT departure route for a capture to see. Treat it as an order of magnitude "
    "from a tree that had one, never as a measured share here."
)


def expected_mix(rows: list[dict], pair: tuple[float, float]) -> dict[str, float]:
    """Hazard-weighted expected cause shares over every renewal, at the record's level.

    EXPECTED, NOT REALISED, and the difference must survive to the page. The realised mix is a few
    hundred departures over a decade; the expected mix is what the hazards say across every
    renewal, and it is the only one with enough behind it to carry an interval at all.

    OVER `MIX_CAUSES` AND NOT `ORDERED_CAUSES` -- see that constant for the number this would
    otherwise have published. The shares still sum to one because the causes left out are exactly
    the ones whose hazard is identically zero on every row of this population.
    """
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_year[int(r["event_date"][:4])].append(r)
    agg = {c: 0.0 for c in MIX_CAUSES}
    weight = 0.0
    for year, year_rows in by_year.items():
        anchor = _anchor_for(year_rows, pair, market_departure_rate(year))
        for r in year_rows:
            risks = _risks_for(r, pair, anchor)
            p = total_departure_probability(risks)
            shares = cause_shares(risks)
            for c in MIX_CAUSES:
                agg[c] += shares.get(c, 0.0) * p
            # FAIL LOUD RATHER THAN QUIETLY RENORMALISE. If a cause outside `MIX_CAUSES` ever
            # carries hazard on a renewal row, the three shares below no longer sum to one and the
            # published interval silently becomes a share of a share. That is a finding about the
            # hazard model, not a number to divide away.
            leaked = {c: s for c, s in shares.items() if c not in MIX_CAUSES and s > 0.0}
            if leaked:
                raise SystemExit(
                    f"a renewal row carries hazard on a cause this population cannot observe "
                    f"({leaked}). The mix over {list(MIX_CAUSES)} would no longer sum to one. "
                    f"Establish where that hazard came from before publishing anything."
                )
            weight += p
    return {c: agg[c] / weight for c in MIX_CAUSES} if weight else {}


def main(table_path: Path) -> int:
    all_rows = json.loads(table_path.read_text())
    rows = [r for r in all_rows if r.get("sim_bill_shock_base") is not None]
    decl = declare(table_path, all_rows)
    print(banner(decl))
    print()
    print(f"rows: {len(rows)}   table: {table_path}")
    print(f"declared: a_shock={DECLARED_SHOCK_WEIGHT}  scale={DECLARED_SENSITIVITY_SCALE}")
    print()
    print(f"{'a_shock':>9} {'scale':>10} " + " ".join(f"{c:>17}" for c in MIX_CAUSES))
    sweep: dict[str, dict[str, float]] = {}
    for pair in FEASIBLE_PAIRS:
        mix = expected_mix(rows, pair)
        sweep[f"a_shock={pair[0]:.2f},scale={pair[1]:.6f}"] = mix
        declared = (pair[0] == DECLARED_SHOCK_WEIGHT
                    and pair[1] == DECLARED_SENSITIVITY_SCALE)
        marker = "  <- the world runs here" if declared else ""
        print(f"{pair[0]:>9.2f} {pair[1]:>10.6f} "
              + " ".join(f"{mix[c]:>16.1%}" for c in MIX_CAUSES) + marker)
    interval = {
        c: [min(m[c] for m in sweep.values()), max(m[c] for m in sweep.values())]
        for c in MIX_CAUSES
    }
    unobservable = [c for c in ORDERED_CAUSES if c not in MIX_CAUSES]
    print()
    print("  THE INTERVAL, which is the figure that goes on the page:")
    for c in MIX_CAUSES:
        lo, hi = interval[c]
        print(f"    {c:>16}: {lo:.1%} to {hi:.1%}")
    for c in unobservable:
        print(f"    {c:>16}: NOT OBSERVABLE on this population — not 0%, unknown")
    print()
    if unobservable:
        print(f"  {UNOBSERVABLE_REASON}")
        print()
        print(f"  {UNOBSERVABLE_SCALE_HINT}")
        print()
    print("  The width is not noise and it is not a confidence interval. It is the range the")
    print("  reason mix takes across every value of `a_shock` the evidence cannot rule out --")
    print("  the split between 'my own bill rose' and 'someone else is cheaper', which no")
    print("  domestic instrument measures separately. A point estimate here would be this")
    print("  project reporting its own free parameter back as a measurement.")

    MIX_ARTEFACT.parent.mkdir(parents=True, exist_ok=True)
    MIX_ARTEFACT.write_text(json.dumps({
        "produced_by": "tools/fit_departure_hazards.py",
        "factor_table": (
            str(table_path.relative_to(PROJECT)) if table_path.is_relative_to(PROJECT)
            else str(table_path)),
        "renewals": len(rows),
        "declared_shock_weight": DECLARED_SHOCK_WEIGHT,
        "declared_sensitivity_scale": DECLARED_SENSITIVITY_SCALE,
        "free_parameter": "a_shock -- the split of the price family between 'my own bill rose' "
                          "and 'someone else is cheaper'. No domestic instrument separates them; "
                          "Ofgem's Consumer Impacts survey codes both as one answer.",
        "level": "every point of the sweep is re-anchored onto the published GB domestic "
                 "switching record, so the interval is over the reason mix alone and not over "
                 "the level as well.",
        "basis": "EXPECTED shares, hazard-weighted over every renewal in the captured run. NOT "
                 "the realised mix.",
        # WHICH CAUSES THIS MIX CAN AND CANNOT SEE, machine-readable beside the interval rather
        # than as prose somewhere else. Every reader of this artefact before 2026-08-31 was reading
        # three of four causes as if they were four of four, and nothing in the file said otherwise.
        "population": decl,
        "causes_in_the_interval": list(MIX_CAUSES),
        "causes_not_observable_on_this_population": {c: None for c in unobservable},
        "causes_not_observable_reason": UNOBSERVABLE_REASON if unobservable else None,
        # ATTRIBUTED, NOT ASSERTED. See `UNOBSERVABLE_SCALE_HINT` for why the 50-of-82 figure is
        # carried as a hint about a different tree rather than as a share of this capture.
        "causes_not_observable_scale_hint": UNOBSERVABLE_SCALE_HINT if unobservable else None,
        "sweep": sweep,
        "interval": interval,
    }, indent=1))
    print(f"\n  -> {MIX_ARTEFACT.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TABLE
    raise SystemExit(main(path))
