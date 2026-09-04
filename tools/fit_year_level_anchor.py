"""Derive the per-year departure LEVEL anchor: the year's rate is the record's, the mix is ours.

Anchor: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
Write-up: `docs/market_research/gb_switching_rate_denominators.md` §8-§11.
Instrument that judges the result: `tools/measure_departure_level.py`.

WHY THIS IS A PER-YEAR TABLE AND NOT A CONSTANT, AND THAT WAS MEASURED RATHER THAN ASSUMED. The
2026-08-30 pass established that no single multiplicative scale on the market term can put the
world inside the published band: the non-market factor product (bill shock x felt price position x
action propensity x dissatisfaction) runs 0.0198 at 2017 to 0.1193 at 2022, a 6x spread whose shape
is unrelated to the record's -- 2022 is the record's TROUGH and carries the LARGEST product. Solving
for the single divisor that would put each year in its own band gives disjoint intervals with an
EMPTY intersection. One scale cannot do it and fitting one would be choosing which years to be
wrong about. See §9 prediction 4 of the write-up for the table.

WHAT THE ANCHOR IS AND IS NOT. It is one number per year, scaling every hazard in
`simulation/departure_risks.build_departure_risks` by the same factor. So it moves the year's
LEVEL and cannot move the reason MIX within the year -- the published record says how many
households left in 2020, the hazards say which ones and why. That separation is the whole point:
`market_departure_rate` states that inside 2016-2025 the level is historical ground truth in the
same sense as 2022 prices, and CLAUDE.md's third wall says the world does not model what the record
already states.

IT IS FITTED ON A CAPTURED RUN AND THEREFORE HAS A FIXED POINT TO REACH, and re-running this tool
IS the iteration. The captured columns are the hazard INPUTS -- bill shock, felt price position,
action propensity, dissatisfaction -- and none of them is a function of the anchor, so a refit on
capture N solves exactly for the population capture N had. What moves is the population itself:
raising the level means more departures, more re-acquisition and a different renewal book the
following year, so the anchor fitted on run N lands run N+1 NEAR the record rather than on it.
Capture, refit, capture again. The acceptance test is not this tool: it is
`tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band`,
measured through `tools/measure_departure_level.py` on the committed factor table.

Usage:
    python3 -m tools.fit_year_level_anchor [factor_table.json]
"""
from __future__ import annotations

import collections
import inspect
import json
import statistics
import sys
from pathlib import Path

import tools.measure_departure_level as _instrument
from simulation.departure_level_anchor import NO_LEVEL_CORRECTION, world_level_identity
from simulation.departure_risks import (
    DECLARED_SENSITIVITY_SCALE,
    DECLARED_SHOCK_WEIGHT,
    WORLD_MAX_CHURN_PROBABILITY,
    build_departure_risks,
    svt_inertia_base_multiplier,
    svt_inertia_hazard,
    total_departure_probability,
)
from simulation.market_switching_propensity import (
    market_departure_rate,
    market_switching_multiplier,
    published_departure_band,
)
from tools.departure_population import (
    account_denominator_refusal,
    banner,
    declare,
    load_svt_decisions,
    union_by_year,
)

PROJECT = Path(__file__).resolve().parent.parent

#: THE FITTER AND THE INSTRUMENT THAT JUDGES IT MUST READ THE SAME CAPTURE, so this is IMPORTED and
#: not a second copy of the path. `5554c2910` repointed `measure_departure_level` at the committed
#: pair and left this default naming `c2_departure_factors.json` -- so on 2026-09-03 the tool that
#: SOLVES the anchor and the tool that JUDGES it were reading different worlds, and a re-fit run the
#: documented way (`python3 -m tools.fit_year_level_anchor`, no argument) would have been solved
#: against the superseded capture and then graded against the committed one. Nothing would have
#: said so: both exit zero and both print a plausible table.
#:
#: That is this repo's VAT shape -- one requirement, several implementations, one of them repaired
#: and the others left live -- so the repair is an IMPORT rather than a second correct string. A
#: future repoint now cannot reach one tool and miss the other. Safe in this direction:
#: `measure_departure_level` does not import this module, so there is no cycle.
DEFAULT_TABLE = _instrument.DEFAULT_TABLE


def _mean_probability(rows: list[dict], anchor: float) -> float:
    """Population-mean departure probability for one year at one anchor.

    `retention_offer_retained_fraction` is 1.0 for the same reason `tools/fit_departure_hazards.py`
    holds it there: the quantity being anchored is `realized_churn_probability`, captured BEFORE
    any retention offer, so including the offer would fit a post-intervention level to a
    pre-intervention record.
    """
    return statistics.fmean(
        total_departure_probability(
            build_departure_risks(
                bill_shock_base=r["sim_bill_shock_base"],
                price_response=r["sim_price_response"],
                dissatisfaction_response=r["sim_dissatisfaction_response"],
                market_opportunity=r["sim_market_opportunity"],
                action_propensity=r["sim_action_propensity"],
                retention_offer_retained_fraction=1.0,
                sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
                shock_weight=DECLARED_SHOCK_WEIGHT,
                level_anchor=anchor,
            )
        )
        for r in rows
    )


def fit_year_anchor(rows: list[dict], target: float) -> float:
    """Bisect the year's anchor onto the published rate.

    Monotone by construction: every hazard is increasing in the anchor and `1 - PROD(1-h)` is
    increasing in every hazard, so there is no local solution to land on. Fails closed rather than
    silently returning the bracket end if the target is unreachable -- a year whose factors cannot
    reach its published rate even at the world's churn ceiling is a finding about the mechanism,
    not a number to clamp.
    """
    lo, hi = 0.0, 1.0
    for _ in range(60):
        if _mean_probability(rows, hi) >= target:
            break
        hi *= 2.0
    else:
        raise SystemExit(
            f"unreachable target {target:.4f}: even an anchor of {hi:.1f} leaves the year's mean "
            f"at {_mean_probability(rows, hi):.4f}. Every hazard is clipped at the world's churn "
            f"ceiling, so this says the year's factor population cannot carry the published rate. "
            f"That is a result about the mechanism -- do not clamp it."
        )
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _mean_probability(rows, mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE WHOLE-BOOK FIT
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: Tolerance for the composition check below, in probability units. The capture rounds
#: `sim_svt_inertia` to six decimals and `realized_churn_probability` likewise, so an exact
#: comparison would fail on rounding alone. Set at the rounding, not above it: this check exists to
#: catch a MISSING FACTOR of ~2-6x, and a tolerance that could hide one would make the check a
#: formality. Derived from the artefact's own precision rather than chosen.
_COMPOSITION_TOLERANCE = 1e-5


def svt_composition_refusal(svt_rows: list[dict]) -> str | None:
    """Does the world compose the SVT hazard the way this fit assumes? `None` if it does.

    THE WHOLE-BOOK FIT HOLDS THE SVT CONTRIBUTION FIXED AND SOLVES THE RENEWAL ANCHOR AROUND IT,
    and that is only legitimate if the year level anchor does not scale the SVT route. It does not,
    and the check is here rather than in a comment because the alternative is unfalsifiable.

    MEASURED ON THE 2026-08-31 CAPTURE, all 1,266 rows: `realized_churn_probability` equals
    `svt_inertia_hazard(...) x action_propensity`, with the recorded
    `sim_level_anchor` NOT multiplied in. **That capture is now STALE and this function says so** --
    the hazard gained a required `market_switching_multiplier` on 2026-09-01, so those 1,266 rows
    reproduce only under the market-blind form and land in the third branch below, not the first.
    `simulation.departure_risks.build_departure_risks`
    computes `CAUSE_SVT_INERTIA = clip(level_anchor x svt_inertia x action_propensity)` — it
    disagrees, and today that line is unreachable because no production caller passes
    `svt_inertia=`. **The world's composition is the correct one.** `svt_inertia_hazard` is derived
    from an ALREADY-ABSOLUTE published annual rate (0.20 recent / 0.10 long-stayer); multiplying it
    by a year anchor of ~4.6 would put annual drift off SVT near 65% against a published 20%.
    Anchoring an absolute published rate a second time destroys the only level anyone could check.

    So this refuses if the capture ever starts matching the ANCHORED form, and names which. A fit
    solved under one composition while the world runs the other lands the world nowhere in
    particular, and nothing downstream would report it: every row would still be well-formed and
    the fitted table would still print.
    """
    unanchored = anchored = neither = market_blind = 0
    example = None
    for row in svt_rows:
        raw = svt_inertia_hazard(
            years_on_svt=row["sim_years_on_svt"],
            segment_days=row["sim_segment_days"],
            market_switching_multiplier=market_switching_multiplier(row["market_year"]),
        )
        # THE THIRD COMPOSITION, AND IT IS A STALENESS TEST RATHER THAN A DISAGREEMENT. A capture
        # taken before the SVT hazard was given its market term reproduces exactly under a factor
        # of 1.0 -- which is what passing the base-window multiplier back in reconstructs. Without
        # this leg such a capture lands in `neither` and reads as "the world runs a hazard this
        # fit does not model", sending the reader to hunt a mechanism disagreement that is really
        # just an artefact older than the code. Naming it is the difference between "re-run the
        # capture" and a day spent in `departure_risks.py`.
        market_blind_raw = svt_inertia_hazard(
            years_on_svt=row["sim_years_on_svt"],
            segment_days=row["sim_segment_days"],
            market_switching_multiplier=svt_inertia_base_multiplier(),
        )
        propensity = row["sim_action_propensity"]
        recorded = row["realized_churn_probability"]
        anchor = row.get("sim_level_anchor", 1.0)
        if abs(raw * propensity - recorded) <= _COMPOSITION_TOLERANCE:
            unanchored += 1
        elif abs(min(raw * propensity * anchor, WORLD_MAX_CHURN_PROBABILITY) - recorded) <= _COMPOSITION_TOLERANCE:
            anchored += 1
        elif abs(market_blind_raw * propensity - recorded) <= _COMPOSITION_TOLERANCE:
            market_blind += 1
        else:
            neither += 1
            example = example or row
    total = len(svt_rows)
    if market_blind:
        return (
            f"{market_blind} of {total} SVT rows reproduce under a MARKET-BLIND hazard -- this "
            f"capture predates the market term on `svt_inertia_hazard` and is stale. The floors "
            f"it records are the flat 0.20/0.10 the record contradicts, so fitting against them "
            f"would solve the renewal anchor around a world that no longer exists. Re-run "
            f"`tools/capture_departure_factors.py`; do not fit this table."
        )
    if anchored:
        return (
            f"{anchored} of {total} SVT rows carry the year level anchor in their realised "
            f"probability. This fit holds the SVT contribution FIXED while solving the renewal "
            f"anchor around it, which is wrong if the anchor scales the SVT route too — and "
            f"scaling it would anchor an already-absolute published rate (0.20/0.10 annual drift) "
            f"a second time. Settle which composition the world runs before fitting."
        )
    if neither:
        return (
            f"{neither} of {total} SVT rows are reproduced by NEITHER composition (e.g. "
            f"{example['customer_id']} on {example['event_date']}: recorded "
            f"{example['realized_churn_probability']}). The SVT hazard this fit models is not the "
            f"one the world ran, so the contribution held fixed here is not the world's."
        )
    if not unanchored:
        return "this capture has no SVT segment decisions to establish a composition from."
    return None


def fit_whole_book(
    renewal_rows: list[dict], svt_rows: list[dict]
) -> dict[int, tuple[float | None, str | None, dict]]:
    """`{year: (anchor, refusal, diagnostics)}` — the year anchor fitted against the WHOLE BOOK.

    THE TARGET IS THE ONE THING THAT CHANGED AND IT IS THE ONLY THING THAT MATTERED. The old fit
    solved `mean realised probability over RENEWAL DECISIONS == published rate`. Post-C1b that
    fits the world to the selected subset of households who took a fixed deal — the ones who
    demonstrably shop — against a published whole-population rate. This solves

        (expected departures on BOTH routes) / (accounts on the book)  ==  published rate

    which has the record's own numerator and the record's own denominator.

    THE SVT CONTRIBUTION IS TAKEN FROM THE CAPTURE'S RECORDED PROBABILITIES, not recomputed: a
    contribution recomputed by this tool would be a reimplementation, and fitting against a
    reimplementation is how a calibration comes out right about a world that does not exist.
    `svt_composition_refusal` is what establishes that holding it fixed is legitimate.

    THREE REFUSALS, AND EACH NAMES A DIFFERENT STATE. They are separate because a reader who sees
    one blank year must be able to tell which:

      * **partial year** — the capture's first and last year. Exposure is a fraction of a year, so
        the account denominator is not an account-year and any anchor solved on it is solving a
        different equation. On the 2026-08-31 capture 2016 would otherwise fit at 15.99 off ONE
        renewal decision and three accounts.
      * **no renewal population** — the year has SVT decisions and no renewal decisions at all, so
        there is nothing to solve an anchor against whatever the target. 2022 is this, exactly:
        zero renewal decisions in the capture, which is also why the renewal-only instrument's
        summary printed `nan`.
      * **unreachable** — the SVT route alone already expects more departures than the record
        allows for the whole book, so no renewal anchor >= 0 can bring it down. This is a result
        about the mechanism and NOT a number to clamp; the same discipline `fit_year_anchor` above
        applies in the opposite direction. 2022 is this too, and independently: an SVT floor of
        12.80% against a published 2.9-4.3%.
    """
    book = union_by_year(renewal_rows, svt_rows)
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in renewal_rows:
        if row.get("sim_bill_shock_base") is not None:
            by_year[int(row["event_date"][:4])].append(row)
    svt_expected: dict[int, float] = collections.defaultdict(float)
    for row in svt_rows:
        svt_expected[int(str(row["event_date"])[:4])] += float(row["realized_churn_probability"])

    out: dict[int, tuple[float | None, str | None, dict]] = {}
    for year in sorted(book):
        accounts = book[year]["accounts"]
        target_pct = 100.0 * market_departure_rate(year)
        floor = svt_expected[year]
        floor_pct = 100.0 * floor / accounts
        diag = {
            "accounts": accounts,
            "renewal_decisions": len(by_year[year]),
            "svt_decisions": book[year]["decisions"]["svt_segment"],
            "target_pct": target_pct,
            "svt_floor_pct": floor_pct,
        }
        # EVERY APPLICABLE CAUSE, NOT THE FIRST ONE. 2022 fails two of these independently — no
        # renewal population AND an unreachable SVT floor — and a reader shown only the first
        # would fix it by finding some renewal decisions, which would not help. A short-circuit
        # here reports the cheapest cause rather than the binding one.
        causes = []
        if book[year]["partial_year"]:
            causes.append("partial year at the capture's edge")
        if not by_year[year]:
            causes.append("no renewal decisions in this year")
        if floor_pct > target_pct:
            causes.append(f"unreachable: SVT alone expects {floor_pct:.2f}% against a target "
                          f"of {target_pct:.2f}%")
        if causes:
            out[year] = (None, "; ".join(causes), diag)
            continue
        target = accounts * market_departure_rate(year)
        residual = target - floor
        lo, hi = 0.0, 1.0
        for _ in range(60):
            if _sum_probability(by_year[year], hi) >= residual:
                break
            hi *= 2.0
        else:
            out[year] = (None, "the renewal route cannot carry the residual at any anchor", diag)
            continue
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if _sum_probability(by_year[year], mid) < residual:
                lo = mid
            else:
                hi = mid
        anchor = (lo + hi) / 2.0
        diag["achieved_pct"] = 100.0 * (floor + _sum_probability(by_year[year], anchor)) / accounts
        out[year] = (anchor, None, diag)
    return out


def emergent_level_sweep(
    renewal_rows: list[dict], svt_rows: list[dict], anchors: list[float] | None = None
) -> dict:
    """What the world's level would BE at one constant anchor for every year, instead of seven.

    THE COUNTERFACTUAL THE LADDER ASKS FOR, AND IT IS THE OPPOSITE QUESTION TO `fit_whole_book`.
    That function asks "what scalar makes this year hit the published rate"; this one asks "if no
    scalar were fitted per year, where would the level land". `DIRECTOR_CANON_WORLD_VALIDATION_
    LADDER_2026-08-31` requires the second question to be answerable — aggregates are meant to
    emerge from individuals and be CHECKED against the band, and a world that can only report the
    fitted answer cannot tell whether it has a mechanism or only a solver.

    Reported per year against the band's TWO endpoints, never against `market_departure_rate`
    alone. That function returns the high end by the director's 2026-08-30 tie-break, and asking
    whether an emergent level "hits" a single endpoint would re-import the very point-target this
    measurement exists to get away from. Containment is the property; the endpoint is not.

    Measured 2026-09-03 on `c6_second_pass_departure_factors.json`: the best single constant is
    k≈2.8 and it puts **2 of 7 fitted years inside their bands**, against 7 of 7 for the per-year
    fit — where 7 of 7 is true by construction and carries no information. Ordering of the emergent
    level against the record is rho +0.68 (n=7, p=0.11: suggestive, not established), while the
    emergent spread is 9.1–19.6 against a record spread of 12.5–23.0. The mechanism is COMPRESSED,
    roughly twofold, rather than pointed the wrong way — which is a rung 2 magnitude question and
    is where the repair goes.

    Returns `{"bands": {...}, "sweep": [{"anchor": k, "achieved_pct": {...}, "in_band": n}, ...],
    "best": {...}}`. It emits no constant and never writes one: this is an instrument that reports
    where an unfitted world stands, and a caller that turned its `best` into a new world constant
    would have re-introduced the clamp under a longer name.
    """
    bands = published_departure_band()
    book = union_by_year(renewal_rows, svt_rows)
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in renewal_rows:
        if row.get("sim_bill_shock_base") is not None:
            by_year[int(row["event_date"][:4])].append(row)
    svt_expected: dict[int, float] = collections.defaultdict(float)
    for row in svt_rows:
        svt_expected[int(str(row["event_date"])[:4])] += float(row["realized_churn_probability"])

    # The fitted years only. Pulling in a year `fit_whole_book` refuses would compare an emergent
    # level against a band the fit itself declines to solve on, which is choosing the population
    # after seeing the answer.
    years = sorted(
        y for y, (anchor, _r, _d) in fit_whole_book(renewal_rows, svt_rows).items()
        if anchor is not None and y in bands
    )
    if anchors is None:
        anchors = [round(0.2 * i, 1) for i in range(5, 46)]      # 1.0 .. 9.0

    sweep = []
    for k in anchors:
        achieved = {
            y: 100.0 * (svt_expected[y] + _sum_probability(by_year[y], k)) / book[y]["accounts"]
            for y in years
        }
        sweep.append({
            "anchor": k,
            "achieved_pct": achieved,
            "in_band": sum(1 for y in years if bands[y][0] <= achieved[y] <= bands[y][1]),
        })
    best = max(sweep, key=lambda row: (row["in_band"], -row["anchor"]))
    return {
        "years": years,
        "bands": {y: bands[y] for y in years},
        "sweep": sweep,
        "best": best,
        "n_years": len(years),
    }


#: Where the rung-1 verdict is written, and it is committed rather than printed.
#:
#: WHY AN ARTEFACT AND NOT A PRINTED TABLE. `emergent_level_sweep` above has printed this since
#: 2026-09-03 and nothing in the tree could read it. A measurement that only exists on somebody's
#: terminal cannot go stale loudly, cannot be cited, and cannot be a check -- which left the world's
#: ONLY standing band verdict the one taken off the fitted anchors, where achieved equals published
#: to four decimals in every fitted year BY CONSTRUCTION. The canon
#: (`DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31`, rung 1) requires the band to be a check the
#: world can FAIL. This file is what it fails.
EMERGENT_VERDICT = PROJECT / "docs" / "reports" / "departure_level_rung1_verdict.json"


def emergent_level_verdict(renewal_rows: list[dict], svt_rows: list[dict]) -> dict:
    """The world's rung-1 verdict: where the level lands with NO per-year scalar fitted at all.

    THE ANCHOR HERE IS `NO_LEVEL_CORRECTION` AND THAT IS NOT A CONSTANT CHOSEN TO FILL A SLOT. It
    is 1.0, the multiplicative IDENTITY -- `departure_level_anchor` already establishes it as "the
    arithmetic form of 'no calibration is identified'", and `build_departure_risks` already carries
    it as the default. So this measurement invents nothing. That distinction is the whole reason
    this function exists rather than a table fitted at some better constant: the finding
    `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_...` establishes that the best single constant (k≈2.8) puts
    2 of 7 years in band against 1 of 7 here -- but 2.8 is a number nobody has a source for, and
    swapping seven fitted scalars for one invented one is trading a clamp for a placeholder. The
    identity is the only anchor value on offer that is not a claim.

    SO THIS IS THE MECHANISM'S OWN ANSWER, unscaled: the hazards say what they say, the SVT route
    contributes what the capture recorded, and the band is asked whether it contains the result. It
    can say no, and it does -- which is the property `test_the_worlds_realised_departure_rate_is_
    inside_the_published_band` structurally cannot have, because its subject ran under the fit.

    WHAT IT IS NOT: it is not a proposal to set the world's anchor to 1.0. The per-year table stays
    where it is and stays declared as a clamp; this is the reading BESIDE it, and the gap between
    the two is the rung-1 debt stated as a number instead of an argument.

    Distances are signed and in percentage points: negative is below the band's low edge, positive
    above its high edge, 0.0 inside. Judged through the instrument's own `inside_band`, at the
    precision the commons publishes its endpoints to, so this verdict and the fitted one cannot
    disagree at a band edge for a reason that is only rounding.
    """
    sweep = emergent_level_sweep(renewal_rows, svt_rows, anchors=[NO_LEVEL_CORRECTION])
    achieved = sweep["sweep"][0]["achieved_pct"]
    years: dict[str, dict] = {}
    for year in sweep["years"]:
        lo, hi = sweep["bands"][year]
        got = achieved[year]
        below, above = _instrument.band_margins(got, lo, hi)
        if _instrument.inside_band(got, lo, hi):
            outside, verdict = 0.0, "IN BAND"
        elif below < 0.0:
            outside, verdict = below, "LOW"
        else:
            outside, verdict = -above, "HIGH"
        years[str(year)] = {
            "band_pct": [lo, hi],
            "emergent_pct": round(got, 4),
            "pp_outside_band": round(outside, 4),
            "verdict": verdict,
        }
    failing = sorted(int(y) for y, v in years.items() if v["verdict"] != "IN BAND")
    return {
        "what_this_is": (
            "the world's departure LEVEL measured with NO per-year level anchor fitted -- every "
            "year at `departure_level_anchor.NO_LEVEL_CORRECTION`, the multiplicative identity -- "
            "against the published GB domestic switching band. This is rung 1 of "
            "DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31: a check the world can fail. The "
            "fitted per-year table in `simulation/departure_level_anchor.py` achieves the "
            "published rate to four decimals in every fitted year by construction and therefore "
            "answers a different question -- whether the world has DRIFTED off its anchor, not "
            "whether its mechanism produces the record's level."
        ),
        "measured_at_anchor": NO_LEVEL_CORRECTION,
        "capture": str(_instrument.DEFAULT_TABLE.relative_to(PROJECT)),
        "world_level_digest": world_level_identity()["digest"],
        "years": years,
        "years_failing": failing,
        "in_band": sweep["n_years"] - len(failing),
        "n_years": sweep["n_years"],
        "worst_pp_outside": (
            min((years[str(y)]["pp_outside_band"] for y in failing), default=0.0)
        ),
        "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --emergent-verdict",
    }


def _sum_probability(rows: list[dict], anchor: float) -> float:
    """Expected departures over these renewal rows at one anchor. A SUM, not a mean.

    The whole-book target is a count over accounts, so the renewal route has to contribute a COUNT.
    `_mean_probability` above divides by the renewal decisions, which is the denominator this fit
    exists to stop using.
    """
    return _mean_probability(rows, anchor) * len(rows) if rows else 0.0


#: Parameter names through which the market could reach `svt_inertia_hazard`. The check below is
#: STRUCTURAL -- does the function have a route for the market year to arrive at all -- rather than
#: a comparison against today's hazard values. A control keyed to the current numbers would go red
#: the moment the SVT rates were refined for any reason and green again on any refit, which is the
#: "keyed to today's answer" shape; a control keyed to the SIGNATURE says exactly what the claim
#: says: this hazard cannot see the market.
_MARKET_PARAMETER_NAMES = frozenset(
    {"market_year", "market_switching_multiplier", "market_multiplier", "market_opportunity"}
)


def svt_market_invariance_refusal() -> str | None:
    """May a whole-book anchor be emitted while the SVT route cannot see the market? `None` if yes.

    **DISCHARGED 2026-09-01 — this refusal is DOWN, and everything below is kept in the past tense
    on purpose.** `svt_inertia_hazard` now takes a required `market_switching_multiplier`, wired
    through `simulation/svt_product.inertia_hazard_for_term` from each cap segment's own start
    year, and re-referenced inside `departure_risks` to the 2019-20 window §4 inferred the two
    constants in. The predicate below is unchanged and still the only thing that decides: it reads
    the live signature, so if the term is ever removed this refusal comes back up by itself. What
    is recorded here is WHY it was up, because a discharged refusal with its reasoning deleted is
    how the same defect gets re-argued from scratch in six weeks.

    THE ROUTE CARRYING 61% OF THIS WORLD'S DEPARTURES WAS INVARIANT TO THE RECORD IT IS FITTED
    AGAINST. `svt_inertia_hazard` took `years_on_svt` and `segment_days` and nothing else. Every
    renewal-route hazard carried `market_switching_multiplier`, which is the record's own level
    ratio inside 2016-2025. The SVT route did not, so it ran the same 0.20/0.10 through a decade
    whose published switching rate moves 5.3x.

    MEASURED 2026-08-31 on `ladder_churn_factors.json`, pre-registered before the run:

      * The SVT floor and the published band midpoint are rank-correlated at **-0.26** over
        2017-2024 -- near zero and the wrong sign (P1, predicted |rho| < 0.4).
      * The floor's coefficient of variation is **0.336x** the record's: flat where the record
        swings (P3, predicted < 0.5x).
      * **2022 is unreachable at every point in the published band** (P2). The record's trough
        allows 4.30% for the whole book; the SVT route alone expects 12.80% at the band top and
        still **8.99%** at the band BOTTOM (0.15/0.05), 2.09x the target. Clearing it needs the
        published pair scaled to 0.354x, and the band bottom is only 0.750x of the top. So this is
        a property of the MECHANISM and not a constant chosen at the wrong end of its band.

    WHY THIS BLOCKS THE CONSTANT RATHER THAN MERELY WARNING. With the whole-book total pinned to
    the record, the SVT floor and the renewal anchor are in a zero-sum: 2023's floor consumes 12.43
    of the 12.50 available and the fit drives the renewal anchor to **0.03**, near-total extinction
    of the only route the company can price against. Pasting that table into
    `simulation/departure_level_anchor.py` would not be a level -- it would be this defect wearing
    a calibration's clothes, and every downstream reason-mix reading would inherit it.

    AND THE §7 TIE-BREAK INVERTS ITS OWN SIGN HERE, which is the part worth keeping. `0.20` was
    taken at the TOP of its band under the director's anti-flattering rule, on the argument that
    the company "loses accounts it has NO renewal lever on". That argument was made when the SVT
    route was sized on its own. Once both routes share one anchored total, a HIGHER SVT floor
    LOWERS the renewal anchor -- it hands the company LESS churn on the route it can actually price
    against. The anti-flattering choice became a flattering one when the denominator was unioned,
    and nothing would have reported that.

    WHAT LIFTED IT, MEASURED ON 2026-09-01 RATHER THAN INHERITED FROM THE 08-31 CHECK. The filed
    repair was `floor x market_switching_multiplier(year)`, predicting 2022 at 3.42%. That form was
    wrong in a way found before it was written: the multiplier is 2024-referenced and the two SVT
    constants are inferred against a 2019-20 market, so it levelled them up by 1.375776 in every
    year (`WORKER_FINDING_THE_SVT_FLOORS_FILED_REPAIR_APPLIES_A_2024_REFERENCED_RATIO_TO_A_2019_20_
    RATE_2026-08-31.md`). The landed form re-references to the inference window, and was
    pre-registered per year before running
    (`WORKER_PREREGISTRATION_WHAT_GIVING_THE_SVT_HAZARD_A_MARKET_TERM_MUST_MOVE_2026-09-01.md`):

        floor rank-correlation vs the published midpoint 2017-2024   -0.26  ->  +0.90
        floor CV ratio against the record                             0.37  ->   1.04
        2022 SVT floor against a 4.30% target                       12.80%  ->  2.33%
        2023 renewal anchor                                          0.030  ->  2.442

    So 2022 is reachable with headroom where the published band's own BOTTOM left it at 8.99%, and
    the priceable route stopped being extinct. This refusal lifts by construction when the
    parameter exists, so it could not outlive the defect it named -- and it did not.

    IT IS NOT THE LAST GATE, and that was pre-registered too. Every committed capture was produced
    by the market-blind world, so `svt_composition_refusal` above now refuses them as STALE. The
    whole-book fit still emits no constant; it refuses for an honest and different reason.
    """
    params = set(inspect.signature(svt_inertia_hazard).parameters)
    if params & _MARKET_PARAMETER_NAMES:
        return None
    return (
        "`svt_inertia_hazard` takes "
        f"{sorted(params)} -- no market term, so the route carrying most of this world's "
        "departures is invariant to the record the anchor is fitted against. Measured: rank "
        "correlation -0.26 against the published midpoint 2017-2024, and 2022 unreachable at "
        "EVERY point in the published SVT band (8.99% at the band bottom against a 4.30% target). "
        "The whole-book fit is therefore solving for a renewal anchor that absorbs the SVT route's "
        "market error -- 2023 comes out at 0.03. Wire the market term into the SVT hazard; do not "
        "paste this table."
    )


def emission_refusal(decl: dict) -> str | None:
    """Why this capture may not hand over a `YEAR_LEVEL_ANCHOR` block, or `None` if it may.

    THE REFUSAL IS THE REPAIR, AND A PRINTED CAVEAT WOULD NOT HAVE BEEN. C1b's author wrote the
    staleness down at the site, named this tool, and predicted exactly what would happen on the
    next capture. It happened. So the debt carries something that FAILS: the per-year diagnostic
    table below still prints, because a measurement withheld is a measurement nobody can argue
    with, but the constant a reader would paste into `simulation/departure_level_anchor.py` does
    not come out of a population that is not the book.

    TWO DISTINCT REFUSALS, because they are two different states and a reader must be able to tell
    them apart:

      * **the capture cannot see the SVT route at all** -- it may or may not be the book, and this
        tool cannot establish which. Fitting anyway would be asserting the thing that is unknown.
      * **the capture CAN see it and the renewal route is a minority** -- measured 2026-08-31 at
        39% of departures. Fitting here is worse than the staleness it appears to cure: the
        households on the standard variable product never reach the renewal roll, so what is left
        is the SELECTED subset who demonstrably shop, and anchoring their mean onto a
        whole-population published rate fits the world to a sub-population.

    What lifts it is item 1 of the finding and is not a wider band: a whole-book departure target
    that both routes are fitted against together.
    """
    if not decl["covers_svt_route"]:
        return (
            "this table's population cannot be established as the book. " + decl["warning"]
        )
    share = decl["share_of_departures_visible"]
    if share is not None and share < 1.0:
        return (
            f"the renewal route carries only {share:.0%} of the departures in this capture "
            f"({decl['departures']}). Anchoring a mean over renewal decisions onto a "
            f"whole-population published switching rate would fit the world to the SELECTED "
            f"subset of households that reach a renewal roll at all."
        )
    return None


def _emergent_verdict_main(table_path: Path) -> int:
    """`--emergent-verdict`: measure the unfitted level, print it, and WRITE it.

    IT WRITES ON EVERY OUTCOME, including the refused one, and that is deliberate. A tool whose
    only failure mode is to write nothing leaves the previous run's file on disk looking current --
    the absence is silent and the reader sees a verdict from a world that no longer exists. So a
    refusal is a verdict too, and it lands in the same place under the same name.
    """
    all_rows = json.loads(table_path.read_text())
    svt_rows, svt_reason = load_svt_decisions(table_path)
    refusal = (
        svt_reason if svt_rows is None
        else svt_composition_refusal(svt_rows)
        or account_denominator_refusal(all_rows, svt_rows)
    )
    if refusal is not None:
        EMERGENT_VERDICT.write_text(json.dumps({
            "refused": refusal,
            "capture": str(table_path.relative_to(PROJECT)),
            "what_this_is": (
                "no rung-1 verdict could be measured from this capture. The refusal is written "
                "rather than withheld: a missing file reads as 'nobody ran it', and a stale one "
                "left in place reads as current."
            ),
            "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --emergent-verdict",
        }, indent=2) + "\n")
        print(f"REFUSED — no rung-1 verdict from {table_path.name}: {refusal}")
        return 1
    verdict = emergent_level_verdict(all_rows, svt_rows)
    EMERGENT_VERDICT.write_text(json.dumps(verdict, indent=2) + "\n")
    print(f"── RUNG 1: the level with NO per-year anchor fitted (k={NO_LEVEL_CORRECTION}) ──")
    print()
    print(f"{'year':>6} {'band lo':>9} {'band hi':>9} {'emergent %':>11} {'pp outside':>11}  verdict")
    for year in sorted(verdict["years"], key=int):
        row = verdict["years"][year]
        lo, hi = row["band_pct"]
        print(f"{year:>6} {lo:>9.1f} {hi:>9.1f} {row['emergent_pct']:>11.4f} "
              f"{row['pp_outside_band']:>11.4f}  {row['verdict']}")
    print()
    print(f"  {verdict['in_band']} of {verdict['n_years']} years inside their band; "
          f"{len(verdict['years_failing'])} fail, worst {verdict['worst_pp_outside']:+.2f}pp.")
    print(f"  written to {EMERGENT_VERDICT.relative_to(PROJECT)}")
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    table_path = Path(args[0]) if args else DEFAULT_TABLE
    if "--emergent-verdict" in argv[1:]:
        return _emergent_verdict_main(table_path)
    all_rows = json.loads(table_path.read_text())
    rows = [r for r in all_rows if r.get("sim_bill_shock_base") is not None]
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_year[int(r["event_date"][:4])].append(r)

    decl = declare(table_path, all_rows)
    print(banner(decl))
    print()
    print(f"factor table: {table_path}   ({len(rows)} renewals)")
    print(f"declared pair: a_shock={DECLARED_SHOCK_WEIGHT}  scale={DECLARED_SENSITIVITY_SCALE}")
    print()
    print(f"{'year':>6} {'n':>4} {'record %':>9} {'unanchored %':>13} {'anchor':>9} "
          f"{'achieved %':>11}")
    fitted: dict[int, float] = {}
    for year in sorted(by_year):
        year_rows = by_year[year]
        target = market_departure_rate(year)
        base = 100.0 * _mean_probability(year_rows, 1.0)
        anchor = fit_year_anchor(year_rows, target)
        fitted[year] = anchor
        achieved = 100.0 * _mean_probability(year_rows, anchor)
        print(f"{year:>6} {len(year_rows):>4} {100.0 * target:>9.2f} {base:>13.3f} "
              f"{anchor:>9.4f} {achieved:>11.3f}")
    print()
    print("  THE TABLE ABOVE IS THE RENEWAL ROUTE ALONE and is a diagnostic, not the world's level:")
    print("  its `record %` target is a whole-population published rate and its population is the")
    print("  households that reached a renewal roll. The whole-book fit is what emits a constant.")
    print()

    svt_rows, svt_reason = load_svt_decisions(table_path)
    book_refusal = account_denominator_refusal(all_rows, svt_rows)
    composition = None if svt_rows is None else svt_composition_refusal(svt_rows)
    if book_refusal is None and composition is None:
        print("── WHOLE-BOOK FIT: both routes, over the accounts on the book ──")
        print()
        result = fit_whole_book(all_rows, svt_rows)
        print(f"{'year':>6} {'accts':>6} {'nRen':>5} {'nSVT':>5} {'record %':>9} "
              f"{'SVT floor %':>12} {'anchor':>9} {'achieved %':>11}")
        for year in sorted(result):
            anchor, refusal, diag = result[year]
            shown = f"{anchor:>9.4f}" if anchor is not None else f"{'—':>9}"
            achieved = (f"{diag['achieved_pct']:>11.3f}" if anchor is not None
                        else f"{'—':>11}")
            print(f"{year:>6} {diag['accounts']:>6} {diag['renewal_decisions']:>5} "
                  f"{diag['svt_decisions']:>5} {diag['target_pct']:>9.2f} "
                  f"{diag['svt_floor_pct']:>12.2f} {shown} {achieved}")
        print()
        for year in sorted(result):
            if result[year][1] is not None:
                print(f"  {year}: NOT FITTED — {result[year][1]}")
        fitted_book = {y: a for y, (a, _r, _d) in result.items() if a is not None}
        print()

        # THE FITTED ANSWER MAY NEVER BE PRINTED WITHOUT THE UNFITTED ONE BESIDE IT.
        #
        # Every `achieved %` in the table above equals its `record %` to four decimals, in every
        # fitted year, because that is what the bisection solves for. Read alone it looks like a
        # world passing a check; it is a world clamped onto one. `DIRECTOR_CANON_WORLD_VALIDATION_
        # LADDER_2026-08-31`: *"The one move that is always wrong: clamping an aggregate to pass a
        # check."* This block is the cheapest thing that stops the clamped number travelling on
        # its own, and it is here rather than in a separate tool for exactly that reason — a
        # report a reader has to go and ask for is one they will not ask for.
        sweep = emergent_level_sweep(all_rows, svt_rows)
        best = sweep["best"]
        print("── IF NO SCALAR WERE FITTED PER YEAR: where the level would land ──")
        print()
        print(f"{'year':>6} {'band lo':>9} {'band hi':>9} {'emergent %':>11}   at one constant "
              f"anchor k={best['anchor']:.1f}")
        for year in sweep["years"]:
            lo, hi = sweep["bands"][year]
            got = best["achieved_pct"][year]
            mark = "  in band" if lo <= got <= hi else ("  LOW" if got < lo else "  HIGH")
            print(f"{year:>6} {lo:>9.1f} {hi:>9.1f} {got:>11.2f}{mark}")
        print()
        print(f"  {best['in_band']} of {sweep['n_years']} fitted years land inside their band at "
              f"the best single constant, against {sweep['n_years']} of {sweep['n_years']} above.")
        print("  The table above is 7/7 BY CONSTRUCTION and carries no information about the")
        print("  mechanism. This one does. A gap between them is rung 1 debt, and the canon's")
        print("  repair for it goes to the individual model -- never to the target.")
        print()

        # THE DIAGNOSTIC TABLE ABOVE ALWAYS PRINTS AND THE CONSTANT BELOW DOES NOT. A measurement
        # withheld is a measurement nobody can argue with, so the per-year fit stays visible; what
        # is refused is the block a reader would paste into the world.
        invariance = svt_market_invariance_refusal()
        if invariance is not None:
            print("  REFUSED — no YEAR_LEVEL_ANCHOR block is emitted from this whole-book fit.")
            print(f"  Reason: {invariance}")
            print("  See docs/staging/WORKER_FINDING_THE_ROUTE_CARRYING_MOST_DEPARTURES_IS_"
                  "INVARIANT_TO_THE_RECORD_IT_IS_FITTED_AGAINST_2026-08-31.md.")
            return 1
        print("  YEAR_LEVEL_ANCHOR: dict[int, float] = {")
        for year in sorted(fitted_book):
            print(f"    {year}: {fitted_book[year]:.6f},")
        print("  }")
        print()
        print("  A YEAR ABSENT FROM THIS BLOCK IS ABSENT ON PURPOSE and must NOT be interpolated.")
        print("  `departure_level_anchor.year_level_anchor` already falls back to the reference")
        print("  year for a year it does not carry, and that fallback is declared and readable;")
        print("  a value invented to fill the gap would not be. See the per-year causes above.")
        return 0

    if book_refusal is not None:
        print("  NO WHOLE-BOOK FIT — the two routes cannot be read on an account denominator.")
        print(f"  Reason: {book_refusal}")
    else:
        print("  NO WHOLE-BOOK FIT — the world and this fit disagree about the SVT composition.")
        print(f"  Reason: {composition}")
    if svt_reason:
        print(f"  ⚠ {svt_reason}")
    print()

    refusal = emission_refusal(decl)
    if refusal is not None:
        print("  REFUSED — no YEAR_LEVEL_ANCHOR block is emitted from this capture.")
        print(f"  Reason: {refusal}")
        print("  The per-year table above is a DIAGNOSTIC on this population and is not the")
        print("  world's level. Lifting this needs a whole-book departure target that both")
        print("  routes are fitted against together — never a widened band, and never this")
        print("  table pasted into simulation/departure_level_anchor.py. See item 1 of")
        print("  docs/staging/WORKER_FINDING_C1B_ADDED_A_DEPARTURE_ROUTE_AND_EVERY_INSTRUMENT"
              "_MEASURING_DEPARTURES_KEPT_READING_THE_OLD_POPULATION_2026-08-31.md.")
        return 1
    print("  YEAR_LEVEL_ANCHOR: dict[int, float] = {")
    for year in sorted(fitted):
        print(f"    {year}: {fitted[year]:.6f},")
    print("  }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
