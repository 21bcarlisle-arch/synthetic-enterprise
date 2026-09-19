"""Does minting default-tariff arrivals WIDEN or NARROW the population of scored decisions?

THE QUESTION, AND WHY IT IS NOT ANSWERABLE FROM AN ARTEFACT ALREADY ON DISK. The rank (selection)
leg of the thesis claim is bounded by the Mann-Whitney null on the value arm's scored renewal
decisions, and that null is a closed form in the two outcome counts — so the ONLY thing that can
narrow it is more decisions. The arrival producer (C6, `simulation/arrival_route.py`) changed which
product an account OPENS on, which is upstream of every renewal it is offered. Nobody has asked
whether that moves the decision count by a handful or by a factor, and the two artefacts either
side of it were produced days and dozens of commits apart, so their difference is not attributable
to it.

ONE VARIABLE, AND THE SYMBOL IS NAMED. Two passes at ONE HEAD over ONE seed and ONE roster,
differing in exactly one rebind: `simulation.population_draw._draw_tariff_type` returning `None`.
That is not an approximation of the pre-producer world, it IS it — `tariff_type` is a dataclass
field defaulting to `None` and the pre-producer `_draw_one` never passed it, so the off leg draws
the byte-identical book the producer's own commit message says it drew (`226 None`).

ONE WORLD PER PROCESS, AND THAT IS NOT FASTIDIOUSNESS. `simulation/run_phase2b.py` binds
`CUSTOMERS = live_population()` at IMPORT. A rebind applied after that import reaches the draw
module and changes nothing at all, because the book was already drawn — the inert-patch shape that
cost the roster run of 2026-09-18 a whole invocation. So the patch is applied before the first
import of the world, each leg is its own process, and `--both` sequences them.

THE PATCH IS OBSERVED TO FIRE, PER LEG. `roster_tariff_type_census` counts the labels on the book
this process actually bound, and the leg RAISES if the off leg finds an `svt` or the on leg finds
none. A rebind that reaches no call site produces two byte-identical worlds, a difference of
exactly zero, and the most flattering possible headline: "the producer costs the instrument
nothing". `noise_floor`'s patch-fires counter exists for the same reason and this is the same
mechanism, not a second opinion about it.

VALUE ARM ONLY, DELIBERATELY. The question is about the value arm's own denominator. The control
arm prices nothing by construction (`run_value_cycle_ab` raises if it does), so a control pass
would add an hour of the only box and no decision to count. Nothing here is a money figure and
nothing here may be read as one: a decision count is a count of OPPORTUNITIES TO BE GRADED, never
evidence about the selection leg's sign.

R12: diagnostic. No stage count here is a target, and specifically not a cue to relax a guard so
the experiment gets a bigger n.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

#: The 95% two-sided normal multiplier, spelled the same way `generate_value_arms_data` spells it
#: so a half-width from this file and one from that file are the same quantity.
Z_95 = 1.959963984540054

LEG_OFF = "arrivals_off"
LEG_ON = "arrivals_on"


def patch_the_arrival_producer_off() -> None:
    """Rebind `_draw_tariff_type` to the silence it returned before C6 existed.

    MUST be called before anything imports `simulation.run_phase2b`. Raises rather than warning if
    the symbol is not there: a rebind of a name that has moved is exactly the inert patch this
    module is built to make impossible.
    """
    from simulation import population_draw

    if not hasattr(population_draw, "_draw_tariff_type"):
        raise AssertionError(
            "`simulation.population_draw` has no `_draw_tariff_type` to rebind -- the arrival "
            "producer has moved and this leg would silently measure nothing. Refusing.")
    population_draw._draw_tariff_type = lambda *_args, **_kwargs: None


def roster_tariff_type_census() -> dict:
    """The labels on the book THIS process bound, read off `run_phase2b` rather than re-drawn.

    Re-drawing the book here to count it would count a book no pass ran over -- the two-artefact
    mispairing in miniature. The roster is the one the pass used or it is not evidence about it.
    """
    from simulation.run_phase2b import CUSTOMERS, SUCCESSOR_CUSTOMERS

    counts: dict[str, int] = {}
    by_commodity: dict[str, dict[str, int]] = {}
    for record in list(CUSTOMERS) + list(SUCCESSOR_CUSTOMERS):
        label = repr(record.get("tariff_type"))
        counts[label] = counts.get(label, 0) + 1
        commodity = str(record.get("commodity"))
        by_commodity.setdefault(commodity, {})
        by_commodity[commodity][label] = by_commodity[commodity].get(label, 0) + 1
    return {
        "records": len(CUSTOMERS) + len(SUCCESSOR_CUSTOMERS),
        "live_records": len(CUSTOMERS),
        "successor_records": len(SUCCESSOR_CUSTOMERS),
        "by_tariff_type": dict(sorted(counts.items())),
        "by_commodity": {k: dict(sorted(v.items())) for k, v in sorted(by_commodity.items())},
        "svt_records": counts.get(repr("svt"), 0),
    }


def _assert_the_patch_fired(leg: str, census: dict) -> None:
    """The leg's own counter, and it RAISES rather than reporting a zero difference."""
    svt = census["svt_records"]
    if leg == LEG_OFF and svt:
        raise AssertionError(
            "the OFF leg drew {} record(s) labelled 'svt' -- the rebind did not reach the draw, "
            "so this leg is the same world as the ON leg and their difference would be zero for "
            "a reason that has nothing to do with the producer. VOID, not a result.".format(svt))
    if leg == LEG_ON and not svt:
        raise AssertionError(
            "the ON leg drew NO record labelled 'svt' -- the arrival producer reached no account "
            "on this roster, so there is nothing here to measure and a zero difference would read "
            "as 'the producer costs the instrument nothing'. VOID, not a result.")


def run_one_leg(leg: str, report_end: str | None = None) -> dict:
    """One value-arm pass over one world, with the funnel and the scored roster it produced."""
    if leg not in (LEG_OFF, LEG_ON):
        raise AssertionError("leg must be {!r} or {!r}; got {!r}".format(LEG_OFF, LEG_ON, leg))
    if leg == LEG_OFF:
        patch_the_arrival_producer_off()

    # IMPORTED HERE AND NOT AT MODULE TOP. This import binds the world; doing it above would draw
    # the book before the rebind above could reach the draw. See the module docstring.
    from company.policy.decision_policy import VALUE_ARM_POLICY, policy_scope
    from simulation.run_phase4c_on_phase2b import main as run_phase4c
    from tools.run_value_cycle_ab import (
        belief_vs_outcome,
        producing_commit,
        renewal_funnel,
        world_identity,
    )

    census = roster_tariff_type_census()
    _assert_the_patch_fired(leg, census)

    started = time.time()
    with policy_scope(VALUE_ARM_POLICY):
        result = run_phase4c(report_end=report_end, policy=VALUE_ARM_POLICY)
    elapsed = time.time() - started

    funnel = renewal_funnel(result, "value_arm")
    outcome = belief_vs_outcome(result)
    return {
        "leg": leg,
        "what_this_leg_is": (
            "the world WITHOUT the C6 arrival producer -- `_draw_tariff_type` rebound to None, "
            "which is the field's own dataclass default and therefore the pre-producer book"
            if leg == LEG_OFF else
            "the world AS BUILT at this commit, with the C6 arrival producer live"),
        "producing_commit": producing_commit(),
        "world_identity": world_identity(),
        "report_end": report_end,
        "pass_seconds": round(elapsed, 1),
        "roster_tariff_type_census": census,
        "renewal_funnel": funnel,
        "belief_vs_outcome": outcome,
    }


def _null(roster) -> dict:
    """This leg's own tie-corrected null, from `generate_value_arms_data`, never respelled here.

    The closed form is written down once in this repository and validated there against the exact
    enumeration. A second copy in this file would be a second thing to keep in step, and a ruler
    that has drifted from the enumeration it claims to approximate is one nobody notices is wrong.
    """
    from tools.generate_value_arms_data import _auc_from_a_roster

    return _auc_from_a_roster(roster)


def fold(off: dict, on: dict) -> dict:
    """The two legs' counts side by side, and what they do to the width of the null.

    STATES THE SIGN IN WORDS as well as in numbers, because the whole point of the question is
    whether the rank leg got cheaper, stayed the same, or did not move at all -- and a reader given
    two sd values and no sentence will pick whichever one flatters the route they arrived with.
    """
    rows = {}
    for leg in (off, on):
        funnel = leg["renewal_funnel"]
        outcome = leg["belief_vs_outcome"]
        existed = (funnel.get("decisions_that_existed") or {})
        stages = {s["stage"]: s["count"] for s in funnel.get("stages", [])}
        null = _null(outcome.get("scored_decisions"))
        rows[leg["leg"]] = {
            "svt_records_on_the_roster": leg["roster_tariff_type_census"]["svt_records"],
            "renewals_the_world_offered": funnel.get("renewals_the_world_offered"),
            "stages": stages,
            "product_not_upliftable_by_tariff_type": funnel.get(
                "product_not_upliftable_by_tariff_type"),
            "decisions_that_existed": existed.get("decisions_that_existed"),
            "priced": funnel.get("priced"),
            "declined": funnel.get("declined"),
            "scored_decisions": (null.get("decisions") if null.get("available") else None),
            "retained": (null.get("retained") if null.get("available") else None),
            "left": (null.get("left") if null.get("available") else None),
            "discrimination_auc": outcome.get("discrimination_auc"),
            "null": null,
            "pass_seconds": leg.get("pass_seconds"),
        }
    a, b = rows[LEG_OFF], rows[LEG_ON]

    def _half_width(row):
        null = row["null"]
        return Z_95 * null["null_sd"] if null.get("available") else None

    def _distance_in_its_own_sd(row):
        null, auc = row["null"], row["discrimination_auc"]
        if not null.get("available") or not isinstance(auc, (int, float)):
            return None
        return (auc - 0.5) / null["null_sd"]

    off_hw, on_hw = _half_width(a), _half_width(b)
    delta_decisions = (
        None if a["decisions_that_existed"] is None or b["decisions_that_existed"] is None
        else b["decisions_that_existed"] - a["decisions_that_existed"])
    width_ratio = None if not off_hw or on_hw is None else on_hw / off_hw

    # WHAT IT WOULD TAKE, in the same units, so the answer is not just a sign. The null narrows as
    # ~1/sqrt(n) at a fixed outcome ratio, so the decisions needed to halve the half-width is the
    # question a reader asks next and it is arithmetic, not another run.
    needed_to_halve = None
    if a["scored_decisions"] and a["retained"] and a["left"]:
        share = a["retained"] / a["scored_decisions"]
        target = Z_95 * a["null"]["null_sd"] / 2.0
        n = a["scored_decisions"]
        while n < 100_000:
            n1 = max(1, round(n * share))
            n2 = max(1, n - n1)
            if Z_95 * math.sqrt((n1 + n2 + 1) / (12.0 * n1 * n2)) <= target:
                needed_to_halve = n
                break
            n += 1

    return {
        "what_this_is": (
            "Two value-arm passes at ONE commit over ONE seed and ONE roster, differing in exactly "
            "one rebound symbol (`simulation.population_draw._draw_tariff_type`). The counts are "
            "the value arm's own decision population; the widths are each leg's OWN "
            "Mann-Whitney null, tie-corrected off its own scored roster."),
        "legs": rows,
        "decisions_that_existed_delta": delta_decisions,
        "scored_decisions_delta": (
            None if a["scored_decisions"] is None or b["scored_decisions"] is None
            else b["scored_decisions"] - a["scored_decisions"]),
        "null_half_width_95": {LEG_OFF: off_hw, LEG_ON: on_hw},
        "null_half_width_ratio_on_over_off": width_ratio,
        "auc_distance_from_half_in_its_own_null_sd": {
            LEG_OFF: _distance_in_its_own_sd(a), LEG_ON: _distance_in_its_own_sd(b)},
        "scored_decisions_needed_to_halve_the_off_legs_half_width": needed_to_halve,
        "did_the_rank_leg_get_cheaper": _verdict(width_ratio),
        "reading": (
            "A decision count is a count of OPPORTUNITIES TO BE GRADED. It is not a result about "
            "the selection leg's sign and may not travel as one. Each AUC above is graded against "
            "the null of the roster it was scored on and against no other family's ruler."),
    }


def _verdict(width_ratio) -> str:
    """The sentence the question was asked for. Three states, and 'not at all' is one of them."""
    if width_ratio is None:
        return ("cannot tell -- at least one leg produced no rank statistic, so it has no null and "
                "no width to compare")
    if width_ratio < 0.95:
        return ("cheaper: the arrivals-on null is {:.1%} of the arrivals-off null, so the producer "
                "bought real width".format(width_ratio))
    if width_ratio > 1.05:
        return ("NOT AT ALL -- the arrivals-on null is WIDER, at {:.1%} of the arrivals-off null. "
                "The producer moved decisions OUT of the priceable population on net".format(
                    width_ratio))
    return ("the same, within 5%: the arrivals-on null is {:.1%} of the arrivals-off null, so this "
            "route does not move the rank leg's cost".format(width_ratio))


def _leg_path(out_dir: Path, leg: str, stamp: str) -> Path:
    return out_dir / "arrival_decision_population_{}_{}.json".format(
        "off" if leg == LEG_OFF else "on", stamp)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--leg", choices=[LEG_OFF, LEG_ON],
                    help="run ONE world in THIS process and write it to --out")
    ap.add_argument("--both", action="store_true",
                    help=("run both legs as child processes, in order, then fold them. One world "
                          "per process because `run_phase2b` binds the book at import."))
    ap.add_argument("--fold", nargs=2, metavar=("OFF_LEG", "ON_LEG"), type=Path,
                    help="fold two leg artefacts already on disk. Runs nothing.")
    ap.add_argument("--out", type=Path, help="where this leg or this fold is written")
    ap.add_argument("--out-dir", type=Path, default=PROJECT_DIR / "docs" / "observability")
    ap.add_argument("--stamp", default="20260919",
                    help="filename stamp for the leg artefacts under --both")
    ap.add_argument("--end-year", help="truncate the window (faster, and a DIFFERENT population)")
    args = ap.parse_args(argv)
    report_end = "{}-12-31".format(args.end_year) if args.end_year else None

    if args.fold:
        off = json.loads(args.fold[0].read_text(encoding="utf-8"))
        on = json.loads(args.fold[1].read_text(encoding="utf-8"))
        folded = fold(off, on)
        out = args.out or (args.out_dir / "arrival_decision_population.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(folded, indent=2), encoding="utf-8")
        print("folded -> {}".format(out))
        print("  decisions_that_existed  {} -> {}  (delta {})".format(
            folded["legs"][LEG_OFF]["decisions_that_existed"],
            folded["legs"][LEG_ON]["decisions_that_existed"],
            folded["decisions_that_existed_delta"]))
        print("  {}".format(folded["did_the_rank_leg_get_cheaper"]))
        return 0

    if args.both:
        paths = {}
        for leg in (LEG_OFF, LEG_ON):
            path = _leg_path(args.out_dir, leg, args.stamp)
            argv_child = [sys.executable, "-m", "tools.arrival_decision_population",
                          "--leg", leg, "--out", str(path)]
            if args.end_year:
                argv_child += ["--end-year", args.end_year]
            print("launching {} -> {}".format(leg, path), flush=True)
            completed = subprocess.run(argv_child, cwd=str(PROJECT_DIR))
            if completed.returncode != 0:
                print("{} FAILED rc={} -- no fold, because a fold over one leg is not a "
                      "comparison".format(leg, completed.returncode), flush=True)
                return completed.returncode
            paths[leg] = path
        return main(["--fold", str(paths[LEG_OFF]), str(paths[LEG_ON])]
                    + (["--out", str(args.out)] if args.out else []))

    if not args.leg:
        ap.error("one of --leg, --both or --fold is required")
    leg = run_one_leg(args.leg, report_end=report_end)
    out = args.out or _leg_path(args.out_dir, args.leg, args.stamp)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(leg, indent=2), encoding="utf-8")
    funnel = leg["renewal_funnel"]
    print("{}: {} svt on the roster; priced {} declined {}; decisions_that_existed {}; {:.0f}s"
          .format(args.leg, leg["roster_tariff_type_census"]["svt_records"],
                  funnel.get("priced"), funnel.get("declined"),
                  (funnel.get("decisions_that_existed") or {}).get("decisions_that_existed"),
                  leg["pass_seconds"]))
    print("  wrote {}".format(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
