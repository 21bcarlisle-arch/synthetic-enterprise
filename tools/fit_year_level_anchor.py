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
import datetime
import inspect
import json
import random
import statistics
import sys
from pathlib import Path

import tools.measure_departure_level as _instrument
import tools.published_route_split as published_route_split
from simulation.departure_level_anchor import NO_LEVEL_CORRECTION, world_level_identity
from simulation.departure_risks import (
    CAUSE_BILL_SHOCK,
    CAUSE_PRICE_POSITION,
    DECLARED_SENSITIVITY_SCALE,
    DECLARED_SHOCK_WEIGHT,
    SVT_INERTIA_ANNUAL_LONG_STAYER,
    SVT_INERTIA_ANNUAL_RECENT,
    SVT_INERTIA_BASE_WINDOW,
    SVT_LONG_STAYER_YEARS,
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
from simulation.renewal_engagement import PASSIVE_RENEWAL_RATE
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

    THE HAZARD CONSTRUCTION LIVES IN ONE PLACE AND THIS DELEGATES TO IT. `_renewal_probabilities`
    below builds the same call for the route-attribution block, and this module having two copies
    of it is the repo's VAT shape in miniature -- one requirement, two implementations, and a
    correction that reaches whichever one the next session happens to open. The fitter and the
    attribution must read the same world or the attribution is describing a world nobody fitted.
    """
    return statistics.fmean(_renewal_probabilities(rows, anchor))


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


# ═══════════════════════════════════════════════════════════════════════════
# WHICH ROUTE CARRIES THE YEAR-TO-YEAR AMPLITUDE
#
# `emergent_level_verdict` above says the world's unclamped level fails the band in six years of
# seven, all of them LOW. It does not say WHERE the miss comes from, and the finding that
# commissioned it guessed -- `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_...` §4 item 2 reads
# "`market_switching_multiplier` and `market_opportunity` already move the hazards year to year;
# they move them too little", and sent the next session to establish the household-level amplitude
# of switching response so that leg could be amplified against evidence.
#
# THAT GUESS IS WRONG AND THIS BLOCK IS WHAT MEASURES IT. The two routes are separable -- the
# renewal route is where `market_opportunity` acts, the SVT route is where it does not reach at
# all -- so the question "which one supplies the record's year-to-year movement" is arithmetic
# rather than argument. It had never been asked, because the level and the amplitude had never
# been separated: a world short on both looks like a world with one problem.
# ═══════════════════════════════════════════════════════════════════════════

#: Where the route attribution is written. Same discipline as `EMERGENT_VERDICT` and for the same
#: reason: a measurement that lives on a terminal cannot go stale loudly and cannot be a check.
ROUTE_ATTRIBUTION = PROJECT / "docs" / "reports" / "departure_level_route_attribution.json"

#: Resamples and seed for the interval below. FIXED, and the seed is committed rather than drawn:
#: an interval that moves between two runs of the same world is not a bound, and a control keyed to
#: one would be flaky in exactly the way that teaches a reader to re-run until green.
_ATTRIBUTION_RESAMPLES = 4000
_ATTRIBUTION_SEED = 20260904


def _relative_slope(xs: list[float], ys: list[float]) -> float | None:
    """Slope of y on x, expressed at the means so it is DIMENSIONLESS. `None` if undefined.

    WHY RELATIVE AND NOT THE RAW SLOPE. The two routes contribute levels an order of magnitude
    apart -- the SVT route 5.7-11.4pp, the renewal route 1.2-3.1pp -- so their raw slopes are not
    comparable and a reader shown both would read the bigger route as the more responsive one by
    arithmetic rather than by behaviour. Dividing by the ratio of the means gives the quantity the
    question actually asks for: **a point of record movement produces how many points of this
    route's own level**. 1.0 is "this route tracks the record proportionally"; 0.0 is "this route
    does not move with the record at all". Those two values are what the claims below are made
    against, and neither is a target.
    #
    # `tools/run_price_ladder._ols_slope` is the same least-squares arithmetic and is deliberately
    # NOT imported: its refusals are price-ladder ones ("every rung landed at the same price"), it
    # returns a raw slope this block cannot use, and reaching it drags `simulation.run_phase2b`
    # onto this module's import graph for six lines of algebra.
    """
    n = len(xs)
    if n < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 1e-12 or abs(my) <= 1e-12:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return slope * mx / my


def _route_series(
    per_year_values: dict[int, list[float]], accounts: dict[int, int], years: list[int]
) -> list[float]:
    """One route's contribution, in percentage points OF THE BOOK, per year.

    The denominator is accounts on the book and never the route's own decisions. A route's mean
    hazard per decision and its contribution to the book's departure rate are different quantities,
    and the second is the one the band is stated in -- so it is the only one that can be regressed
    against the band without dividing two numbers whose ratio is not a quantity.
    """
    return [100.0 * sum(per_year_values[y]) / accounts[y] for y in years]


def _bootstrap_interval(
    per_year_values: dict[int, list[float]], accounts: dict[int, int],
    years: list[int], xs: list[float],
) -> dict:
    """A 95% interval for one route's relative slope, resampling DECISIONS WITHIN EACH YEAR.

    THE BOUND THIS SAMPLE SIZE EARNS, AND IT IS NOT DECORATION. The renewal route stands on 13 to
    20 decisions per year. A slope through seven such points can look flat because the route is
    flat or because the route is thin, and the whole reading below turns on telling those apart --
    so the interval is published beside the point estimate and the two claims that matter are
    stated as "the interval excludes 1.0" and "the interval excludes 0.0" rather than as the point
    estimates, which on their own would be figures without the bound their sample size earns.

    Resampling is WITHIN the year and not across years: the seven years are the record and are not
    a sample of anything, so resampling them would be bootstrapping the GB switching history. What
    is uncertain is which households the capture happened to catch inside each year.
    """
    rng = random.Random(_ATTRIBUTION_SEED)
    draws: list[float] = []
    for _ in range(_ATTRIBUTION_RESAMPLES):
        resampled = {
            y: [vals[rng.randrange(len(vals))] for _ in range(len(vals))]
            for y, vals in ((y, per_year_values[y]) for y in years)
        }
        rel = _relative_slope(xs, _route_series(resampled, accounts, years))
        if rel is not None:
            draws.append(rel)
    if not draws:
        return {"available": False, "why_not": "no resample produced a defined slope"}
    draws.sort()
    return {
        "available": True,
        "lo": round(draws[int(0.025 * len(draws))], 4),
        "hi": round(draws[int(0.975 * len(draws))], 4),
        "resamples": _ATTRIBUTION_RESAMPLES,
        "seed": _ATTRIBUTION_SEED,
    }


def route_amplitude_attribution(renewal_rows: list[dict], svt_rows: list[dict]) -> dict:
    """Which of the world's two departure routes supplies the record's year-to-year movement.

    MEASURED AT `NO_LEVEL_CORRECTION`, for the same reason `emergent_level_verdict` is: the fitted
    per-year anchor acts on the renewal route alone, so any attribution taken under it would be
    reading the solver's compensation and calling it the mechanism. At the identity there is
    nothing to read but the hazards.

    THE ANSWER, on `c6_second_pass_departure_factors.json`, and it inverts the finding that
    commissioned it:

      * **SVT route** -- relative slope **+0.99**, 95% interval [+0.88, +1.11]. It tracks the
        record PROPORTIONALLY. The interval excludes 0.0 and contains 1.0, which is as close to
        "this route has the right amplitude" as seven years of record can say. It also carries
        70.5% to 87.2% of the emergent level.
      * **Renewal route** -- relative slope **-0.08**, 95% interval [-0.45, +0.31]. It supplies no
        year-to-year amplitude at all: the interval contains 0.0 and EXCLUDES 1.0. It contributes a
        near-constant 1.2-3.1pp whatever the record did.

    THE POINT ESTIMATES ARE NOT WHERE THE WEIGHT IS, and neither is 1.0 to three decimals: on
    seven years the SVT slope reads +0.82, +0.99 and +1.19 against the band's low endpoint, its
    midpoint and its high endpoint respectively (`regressor_robustness`). What survives all three,
    and survives the interval, is the ORDERING -- one route near 1 and the other near 0 -- and
    that is the whole claim. A reader taking +0.99 for a calibrated fact would be reading a
    precision this sample cannot support.

    So the world's rung-1 miss is not a compressed market response. The route that carries the
    response has the right shape and about half the level; the route the repair was aimed at is
    flat, and `market_opportunity` -- which acts only there -- cannot be the amplitude mechanism
    because the leg it multiplies does not move with the record however hard it is multiplied.

    `household_amplification_counterfactual` is what makes that decisive rather than descriptive:
    it re-measures the world with the two opportunity-scaled hazards scaled by a ladder of factors,
    up to and including the world's own churn ceiling. The level goes anywhere -- 6.9pp to 47pp --
    and the relative slope goes DOWN, because adding a flat quantity to a proportional one dilutes
    it. **No value of the household amplitude gap closes rung 1**, which is a statement about the
    mechanism's shape and does not depend on what the gap's answer turns out to be.

    `regressor_robustness` re-runs the whole attribution against the band's LOW and HIGH endpoints
    instead of its midpoint. The midpoint is a regressor here and emphatically not a target -- the
    canon's objection is to aiming at a point, and nothing in this function aims -- but a
    conclusion that only holds at one of three defensible choices of x is a conclusion about the
    choice, so all three are reported and the reader can see they agree.
    """
    bands = published_departure_band()
    book = union_by_year(renewal_rows, svt_rows)
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in renewal_rows:
        if row.get("sim_bill_shock_base") is not None:
            by_year[int(row["event_date"][:4])].append(row)
    svt_by_year: dict[int, list[float]] = collections.defaultdict(list)
    for row in svt_rows:
        svt_by_year[int(str(row["event_date"])[:4])].append(
            float(row["realized_churn_probability"])
        )
    years = sorted(
        y for y, (anchor, _r, _d) in fit_whole_book(renewal_rows, svt_rows).items()
        if anchor is not None and y in bands
    )
    accounts = {y: book[y]["accounts"] for y in years}

    renewal = {y: _renewal_probabilities(by_year[y], NO_LEVEL_CORRECTION) for y in years}
    svt = {y: list(svt_by_year[y]) for y in years}
    mids = [(bands[y][0] + bands[y][1]) / 2.0 for y in years]

    routes = {}
    for name, values in (("renewal_route", renewal), ("svt_route", svt)):
        series = _route_series(values, accounts, years)
        routes[name] = {
            "pp_of_book": {str(y): round(v, 4) for y, v in zip(years, series)},
            "decisions": {str(y): len(values[y]) for y in years},
            "relative_slope": round(_relative_slope(mids, series), 4),
            "interval_95": _bootstrap_interval(values, accounts, years, mids),
        }
    emergent = _route_series(
        {y: renewal[y] + svt[y] for y in years}, accounts, years
    )
    for name in routes:
        routes[name]["share_of_emergent_level"] = {
            str(y): round(routes[name]["pp_of_book"][str(y)] / e, 4)
            for y, e in zip(years, emergent)
        }

    return {
        "what_this_is": (
            "which of the world's two departure routes supplies the year-to-year AMPLITUDE the "
            "published record has, measured at `departure_level_anchor.NO_LEVEL_CORRECTION`. The "
            "rung-1 verdict beside this file says the unclamped level fails the band in six years "
            "of seven and does not say where the miss comes from; this says. `relative_slope` is "
            "dimensionless and taken at the means: 1.0 is a route that tracks the record "
            "proportionally, 0.0 is a route that does not move with it at all. Neither is a "
            "target and nothing here is fitted."
        ),
        "measured_at_anchor": NO_LEVEL_CORRECTION,
        "capture": str(_instrument.DEFAULT_TABLE.relative_to(PROJECT)),
        "world_level_digest": world_level_identity()["digest"],
        "years": [str(y) for y in years],
        "regressor": (
            "the published band's MIDPOINT per year. A regressor, not a target -- see "
            "`regressor_robustness` for the same attribution against both endpoints."
        ),
        "emergent_pp_of_book": {str(y): round(v, 4) for y, v in zip(years, emergent)},
        "routes": routes,
        "household_amplification_counterfactual": _amplification_counterfactual(
            renewal_rows, svt_rows, years, accounts, svt, mids, bands
        ),
        "regressor_robustness": {
            edge: {
                name: round(_relative_slope(
                    [bands[y][i] for y in years],
                    _route_series({"renewal_route": renewal, "svt_route": svt}[name],
                                  accounts, years),
                ), 4)
                for name in ("renewal_route", "svt_route")
            }
            for i, edge in ((0, "band_low_endpoint"), (1, "band_high_endpoint"))
        },
        "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --route-attribution",
    }


# ═══════════════════════════════════════════════════════════════════════════
# WHICH LEG OF THE SVT ROUTE IS SHORT
#
# `route_amplitude_attribution` above establishes that the SVT route carries the record's
# year-to-year SHAPE (relative slope +0.99) at about half its LEVEL, and that no amount of the
# repair prescribed for the renewal route can supply the rest. That leaves one question and it had
# never been asked: the SVT route's own level is a product of three factors, and nobody had measured
# which of them is short.
#
# THE FINDING THAT COMMISSIONED THIS NAMED THREE CANDIDATES -- "the hazard per SVT decision, the size
# of the SVT population, or the assignment that decides who reaches which route". Two of those three
# are the same quantity on a capture (an account reaches the SVT route in a year exactly when it is
# on the SVT product in that year), and there is a third factor nobody named: how much OF the year an
# SVT account actually spends exposed to the route. So the decomposition below is the arithmetic one
# and not the named one, and it says so.
# ═══════════════════════════════════════════════════════════════════════════

#: Where the shortfall decomposition is written. Same discipline and same reason as
#: `EMERGENT_VERDICT` and `ROUTE_ATTRIBUTION`: a reading that lives on a terminal cannot go stale
#: loudly, and cannot be a check.
SVT_SHORTFALL = PROJECT / "docs" / "reports" / "svt_route_shortfall_decomposition.json"

#: The three factors whose product IS the SVT route's contribution to the book's departure rate,
#: with the arithmetic ceiling each one can never pass. Declared as data rather than written out
#: three times below, because the whole reading is "which of these has the headroom" and a factor
#: whose ceiling lived in prose beside the loop would be the one nobody re-checked.
#:
#:   `reach`     accounts that take an SVT decision in the year, over accounts on the book. The
#:               finding's "size of the SVT population" AND its "assignment that decides who reaches
#:               which route" -- one quantity, and the ceiling is the whole book.
#:   `exposure`  SVT segment-days per reached account over a year. The factor nobody named. The
#:               ceiling is a household on the SVT product every day of the year.
#:   `hazard`    expected departures per SVT-account-YEAR of exposure. The finding's "hazard per SVT
#:               decision", re-expressed per account-year so it is comparable with the published
#:               annual rate the world derives it from. The ceiling is the world's churn ceiling.
_SVT_FACTOR_CEILINGS = {
    "reach": 1.0,
    "exposure": 1.0,
    "hazard": WORLD_MAX_CHURN_PROBABILITY,
}


def _svt_factors(svt_rows_for_year: list[dict], accounts: int) -> dict[str, float]:
    """The three factors for one year, and the contribution they multiply out to.

    EXPOSURE IS MEASURED IN SEGMENT-DAYS AND NOT IN DECISIONS, and that is the whole reason this is
    a separate factor rather than a decision count. Cap periods are not equal -- the capture's
    segments run from 1 to 92 days, because a household's first segment starts the day it arrives --
    so "decisions per account" would charge a 3-day segment the same as a 92-day one and would move
    when the cap calendar changed cadence rather than when the world's exposure changed. Days over a
    year is the quantity `svt_inertia_hazard` itself converts against.
    """
    reached = {row["customer_id"] for row in svt_rows_for_year}
    days: dict[str, float] = collections.defaultdict(float)
    for row in svt_rows_for_year:
        days[row["customer_id"]] += float(row["sim_segment_days"])
    expected = sum(float(row["realized_churn_probability"]) for row in svt_rows_for_year)
    reach = len(reached) / accounts
    exposure = statistics.fmean(days.values()) / 365.25
    return {
        "reach": reach,
        "exposure": exposure,
        # Expected departures per account-YEAR of SVT exposure. `expected / len(reached)` is the
        # per-account expectation over whatever exposure that account happened to have; dividing by
        # the exposure carries it to a full year, which is the unit `SVT_INERTIA_ANNUAL_RECENT` is
        # published in and therefore the only unit in which the two can be compared at all.
        "hazard": expected / len(reached) / exposure,
        "pp_of_book": 100.0 * expected / accounts,
    }


def svt_route_shortfall_decomposition(renewal_rows: list[dict], svt_rows: list[dict]) -> dict:
    """Which of the SVT route's three factors is short of the record, measured as a BOUND.

    MEASURED AT `NO_LEVEL_CORRECTION` for the reason the attribution beside it is: the per-year
    anchor acts on the renewal route, so the residual this reading asks the SVT route to cover would
    otherwise be the residual left after the solver had already closed the gap -- which is zero by
    construction, and would report the SVT route as not short at all.

    THE IDENTITY, exact and checked by `test_the_shortfall_decomposition_multiplies_out`:

        svt_pp_of_book  =  100 x reach x exposure x hazard

    THE QUESTION IS NOT "WHICH FACTOR IS SMALL" BUT "WHICH FACTOR HAS THE HEADROOM", and those are
    different questions with different answers. Every one of the three is below what the record
    needs. Only one of them can get there:

      * **reach** is already 0.67-0.98 of the book. Its ceiling is 1.0 -- every account on the SVT
        product -- which is a multiple of 1.02 to 1.49 against a required 1.48 to 2.14. It closes
        **1 year of 7**, and that year is 2023, whose band is the widest in the record.
      * **exposure** is already 0.64-0.81 of the year. Its ceiling is 1.0 -- every reached account
        on SVT every day -- a multiple of 1.24 to 1.55. It closes **1 of 7**, the same year.
      * **hazard** is 0.094-0.197 per account-year against a ceiling of
        `WORLD_MAX_CHURN_PROBABILITY`, a multiple of 4.8 to 10.2. It closes **7 of 7**.

    `bounded_factor_saturation` is what makes that decisive rather than suggestive, and it is the
    same shape of argument as the attribution's ceiling rung. Take BOTH bounded factors to their
    ceilings at once: the entire book on the SVT product, every day of the year. That world has no
    renewal population left, so the renewal route contributes nothing and the SVT route must carry
    the whole band on its own -- and at the hazard this world runs it reaches the band's LOW endpoint
    in **1 year of 7**. The two factors the finding named cannot close rung 1 between them, at any
    value they are capable of taking, and that does not depend on how the residual is apportioned.

    SO THE LEG IS THE HAZARD PER SVT-ACCOUNT-YEAR, and `required_hazard` says by how much. Holding
    reach and exposure where the world has them, the record needs 0.109 to 0.346 departures per
    SVT-account-year against the 0.094 to 0.197 the world produces. **Nothing here picks that
    number.** It is published as the size of a gap, and the gap's own units are the units of
    `SVT_INERTIA_ANNUAL_RECENT` = 0.20 / `SVT_INERTIA_ANNUAL_LONG_STAYER` = 0.10 so that the next
    session can take it to the published record rather than to a slot.

    WHERE THE COMPARISON IS CLEANEST, AND IT IS NOT EVERY YEAR. `svt_inertia_hazard` re-references
    the published pair by `market_switching_multiplier / svt_inertia_base_multiplier()`, and that
    divisor is the MEAN of the multiplier over `SVT_INERTIA_BASE_WINDOW` -- so the factor is 1.0
    ACROSS the window and not within each of its years: 0.962 at 2019 and 1.040 at 2020, against
    0.56 to 0.90 everywhere else. Inside the window the world is therefore running the published
    0.20 / 0.10 to within 4%, and its tenure mix there is 0% and 16% long-stayer so almost every
    decision is on the 0.20 branch. `base_window_comparison` reports that pair alone, and reports
    the ratio BOTH ways -- against the published rate and against the re-referenced rate the world
    actually ran -- because the two differ by that 4% and quoting one as the other is the shape this
    repo pays for. The record needs **1.6x to 1.7x** either way. That is a question for the source,
    and the source itself calls the pair a structural inference at confidence M whose own band tops
    out at 20% -- which is exactly the sourcing this reading exists to aim, and NOT a constant to
    move.
    """
    bands = published_departure_band()
    book = union_by_year(renewal_rows, svt_rows)
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in renewal_rows:
        if row.get("sim_bill_shock_base") is not None:
            by_year[int(row["event_date"][:4])].append(row)
    svt_by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in svt_rows:
        svt_by_year[int(str(row["event_date"])[:4])].append(row)
    years = sorted(
        y for y, (anchor, _r, _d) in fit_whole_book(renewal_rows, svt_rows).items()
        if anchor is not None and y in bands
    )

    per_year: dict[str, dict] = {}
    closes: dict[str, list[int]] = {name: [] for name in _SVT_FACTOR_CEILINGS}
    saturation_reaches: list[int] = []
    for year in years:
        accounts = book[year]["accounts"]
        factors = _svt_factors(svt_by_year[year], accounts)
        renewal_pp = 100.0 * _sum_probability(by_year[year], NO_LEVEL_CORRECTION) / accounts
        lo, hi = bands[year]
        # THE REQUIRED MULTIPLE IS TAKEN AT THE BAND'S LOW ENDPOINT AND NOT ITS MIDPOINT, which is
        # the opposite of the attribution's choice and deliberate. The attribution REGRESSES against
        # the band and wants its centre; this asks whether a factor can POSSIBLY close the gap, and
        # the honest form of "possibly" is the least the record will accept. All three endpoints are
        # published below so a reader can see the ordering does not turn on the choice.
        required = {
            "at_band_low": (lo - renewal_pp) / factors["pp_of_book"],
            "at_band_midpoint": ((lo + hi) / 2.0 - renewal_pp) / factors["pp_of_book"],
            "at_band_high": (hi - renewal_pp) / factors["pp_of_book"],
        }
        headroom = {
            name: _SVT_FACTOR_CEILINGS[name] / factors[name] for name in _SVT_FACTOR_CEILINGS
        }
        for name, room in headroom.items():
            if room >= required["at_band_low"]:
                closes[name].append(year)
        # BOTH BOUNDED FACTORS AT ONCE, AND THE RENEWAL ROUTE GOES TO ZERO WITH THEM. A world where
        # every account is on the SVT product every day of the year has no renewal decision left to
        # price, so leaving the renewal contribution in the sum would credit this counterfactual
        # with departures it has just abolished.
        saturated_pp = 100.0 * factors["hazard"]
        if saturated_pp >= lo:
            saturation_reaches.append(year)
        per_year[str(year)] = {
            "accounts": accounts,
            "svt_pp_of_book": round(factors["pp_of_book"], 4),
            "renewal_pp_of_book": round(renewal_pp, 4),
            "band_pct": [lo, hi],
            "factors": {name: round(factors[name], 6) for name in _SVT_FACTOR_CEILINGS},
            "required_multiple": {k: round(v, 4) for k, v in required.items()},
            "headroom_to_ceiling": {k: round(v, 4) for k, v in headroom.items()},
            "required_hazard": {
                k: round(factors["hazard"] * v, 6) for k, v in required.items()
            },
            "saturated_pp_of_book": round(saturated_pp, 4),
            "saturation_reaches_band": saturated_pp >= lo,
        }

    base_window = sorted(set(SVT_INERTIA_BASE_WINDOW) & set(years))
    return {
        "what_this_is": (
            "which of the three factors under the SVT route's LEVEL is short of the published "
            "record, measured at `departure_level_anchor.NO_LEVEL_CORRECTION`. "
            "`departure_level_route_attribution.json` beside this file establishes that the SVT "
            "route carries the record's year-to-year shape at about half its level and that the "
            "renewal route cannot supply the rest; this says which leg of the SVT route the level "
            "is missing from. The reading is a BOUND on each factor's ceiling, not a fit, and "
            "nothing here chooses a value."
        ),
        "measured_at_anchor": NO_LEVEL_CORRECTION,
        "capture": str(_instrument.DEFAULT_TABLE.relative_to(PROJECT)),
        "world_level_digest": world_level_identity()["digest"],
        "years": [str(y) for y in years],
        "identity": (
            "svt_pp_of_book == 100 x reach x exposure x hazard, exactly. `reach` is accounts "
            "taking an SVT decision over accounts on the book; `exposure` is SVT segment-days per "
            "reached account over 365.25; `hazard` is expected departures per SVT-account-YEAR of "
            "exposure, which is the unit `SVT_INERTIA_ANNUAL_RECENT` is published in."
        ),
        "on_the_three_the_finding_named": (
            "the finding asked for 'the hazard per SVT decision, the size of the SVT population, or "
            "the assignment that decides who reaches which route'. On a capture the last two are ONE "
            "quantity -- an account reaches the SVT route in a year exactly when it is on the SVT "
            "product in that year -- and the factor they leave out is EXPOSURE, how much of the "
            "year a reached account spends on the product. So this decomposes the arithmetic three "
            "and not the named three."
        ),
        "ceilings": dict(_SVT_FACTOR_CEILINGS),
        "years_a_factor_could_close_alone": {
            name: {
                "years": [str(y) for y in closes[name]],
                "of": len(years),
                "ceiling": _SVT_FACTOR_CEILINGS[name],
            }
            for name in _SVT_FACTOR_CEILINGS
        },
        "bounded_factor_saturation": {
            "what_this_is": (
                "reach AND exposure both at 1.0 -- the entire book on the SVT product every day of "
                "the year -- with the renewal route at zero, because that world has no renewal "
                "decision left to price. The SVT route then carries the whole band alone at the "
                "hazard this world runs. This is the two named factors at the most they can ever do."
            ),
            "reaches_band_low_in": len(saturation_reaches),
            "of": len(years),
            "years_reached": [str(y) for y in saturation_reaches],
        },
        "base_window_comparison": {
            "what_this_is": (
                "`svt_inertia_hazard` re-references the published pair by "
                "`market_switching_multiplier / svt_inertia_base_multiplier()`. That divisor is the "
                "MEAN of the multiplier over `SVT_INERTIA_BASE_WINDOW`, so the factor is 1.0 ACROSS "
                "the window and not within each of its years -- see `re_referencing_factor` per "
                "year below. Inside the window the world runs the published rate to within a few "
                "per cent; everywhere else the factor is 0.56 to 0.90 and a ratio quoted against "
                "the published rate would be measuring the re-referencing instead of the source. "
                "Both ratios are given because they differ, and quoting one as the other is how "
                "two correct figures become a quantity that is not one."
            ),
            "window": [str(y) for y in base_window],
            "published_annual_recent": SVT_INERTIA_ANNUAL_RECENT,
            "published_annual_long_stayer": SVT_INERTIA_ANNUAL_LONG_STAYER,
            "window_mean_re_referencing_factor": 1.0,
            "years": {
                str(y): {
                    "re_referencing_factor": round(
                        market_switching_multiplier(y) / svt_inertia_base_multiplier(), 4
                    ),
                    "world_hazard": per_year[str(y)]["factors"]["hazard"],
                    "required_hazard_at_band_low": per_year[str(y)]["required_hazard"]["at_band_low"],
                    "required_over_published_recent": round(
                        per_year[str(y)]["required_hazard"]["at_band_low"]
                        / SVT_INERTIA_ANNUAL_RECENT, 4
                    ),
                    "required_over_re_referenced_recent": round(
                        per_year[str(y)]["required_hazard"]["at_band_low"]
                        / (SVT_INERTIA_ANNUAL_RECENT
                           * market_switching_multiplier(y) / svt_inertia_base_multiplier()), 4
                    ),
                    "share_of_decisions_on_the_long_stayer_branch": round(
                        sum(
                            1 for row in svt_by_year[y]
                            if row["sim_years_on_svt"] >= SVT_LONG_STAYER_YEARS
                        ) / len(svt_by_year[y]), 4
                    ),
                }
                for y in base_window
            },
        },
        "per_year": per_year,
        "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --svt-shortfall",
    }


COMPOSITION_COUNTERFACTUAL = (
    PROJECT / "docs" / "reports" / "svt_composition_vs_published.json"
)


def published_composition_counterfactual(renewal_rows: list[dict], svt_rows: list[dict]) -> dict:
    """What rung 1 does if the world's SVT share is moved to the PUBLISHED one, and nothing else.

    THIS IS THE COMPOSITION QUESTION, MEASURED RATHER THAN SOURCED-AND-ARGUED. The decomposition
    beside this one showed that `reach` and `exposure` cannot close rung 1 at their ARITHMETIC
    ceilings of 1.0. That is a bound and bounds can be vacuous: 1.0 is a world with the entire book
    on SVT every day, which nobody claims is the record. The question a reader is entitled to ask
    next is what happens at the value the record ACTUALLY published, which is a smaller move, and
    whether the ceiling result was doing any work. It was, and this says by how much.

    THE COUNTERFACTUAL IS ON COMPOSITION ONLY. `reach x exposure` is the SVT account-day share --
    the same quantity the published statistic counts, which is why it and not `reach` is the thing
    rescaled here. Both routes move together because they are COMPLEMENTS: an account-day put onto
    the SVT product is an account-day taken off a fixed term, and the renewal decisions priced on
    those days go with it. The hazards are untouched, no constant is edited and no anchor moves.

    TWO ACCOUNTINGS ARE PUBLISHED, so that the verdict cannot be picked by choosing one:

      * `renewal_rescaled` scales the renewal route by `(1 - published) / (1 - world)`. This is the
        consistent one and it is the headline. You cannot move a third of the book onto SVT and
        keep the renewal decisions those accounts were going to make.
      * `renewal_held` leaves the renewal route where it is. It is arithmetically incoherent and it
        is reported because it is the MOST GENEROUS thing composition could possibly do -- the same
        reason the decomposition takes its required multiple at the band's low endpoint.

    THE RESULT, AND THE FIRST DRAFT OF THIS DOCSTRING GOT IT WRONG. It predicted 2024 would reach
    the band on `renewal_held` and miss on `renewal_rescaled`, from arithmetic done by hand against
    the SCHEDULE-derived SVT share (0.55) rather than the capture-derived one (0.606) this reading
    actually rescales. Run at real inputs, 2024 misses on both -- 12.10 and 10.65 against a band low
    of 12.5. The claim is corrected here rather than in a footnote.

    So: `years_newly_closed` is EMPTY on both accountings and on both published bases. The only year
    that reaches the band after the counterfactual is 2023, and 2023 was already reaching it before
    the counterfactual -- its `required_multiple.at_band_low` in the decomposition is 0.90, i.e.
    below 1. **Composition at the published share closes nothing that was not already closed.**
    `years_already_reaching_band` is published alongside `closes_rung1_at_published_high` precisely
    so that "1 of 5" cannot be read as composition having done that work.

    WHAT IS DELIBERATELY NOT DONE: 2020 and 2021 have no established published figure and are
    REFUSED rather than interpolated (`tools/published_tariff_mix` carries the reason). They are two
    of the seven fitted years, so the denominator here is 5 and not 7, and it is reported as 5 --
    a counterfactual that quietly renumbered itself to a fuller-looking 7 would be claiming coverage
    it does not have.
    """
    from tools.published_tariff_mix import DEFAULT_TARIFF_SHARE, default_tariff_share

    bands = published_departure_band()
    book = union_by_year(renewal_rows, svt_rows)
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in renewal_rows:
        if row.get("sim_bill_shock_base") is not None:
            by_year[int(row["event_date"][:4])].append(row)
    svt_by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in svt_rows:
        svt_by_year[int(str(row["event_date"])[:4])].append(row)
    fitted = sorted(
        y for y, (anchor, _r, _d) in fit_whole_book(renewal_rows, svt_rows).items()
        if anchor is not None and y in bands
    )

    per_year: dict[str, dict] = {}
    refused: dict[str, str] = {}
    for year in fitted:
        published = default_tariff_share(year, "all_domestic")
        if published is None:
            refused[str(year)] = (
                f"no established published default-tariff share for {year}; "
                f"{DEFAULT_TARIFF_SHARE[year].note if year in DEFAULT_TARIFF_SHARE else 'year absent from the series'}"
            )
            continue
        accounts = book[year]["accounts"]
        factors = _svt_factors(svt_by_year[year], accounts)
        world_share = factors["reach"] * factors["exposure"]
        renewal_pp = 100.0 * _sum_probability(by_year[year], NO_LEVEL_CORRECTION) / accounts
        lo, hi = bands[year]

        bases: dict[str, dict] = {}
        for basis in ("all_domestic", "as_published"):
            band = default_tariff_share(year, basis)
            if band is None:  # pragma: no cover - guarded by the refusal above
                continue
            endpoints: dict[str, dict] = {}
            for name, target in (("at_published_low", band[0]), ("at_published_high", band[1])):
                # A share above 1.0 is not a world, and clamping silently would report a
                # counterfactual that the arithmetic cannot produce as though it had been run.
                if not 0.0 < target <= 1.0:  # pragma: no cover - published bands are shares
                    raise ValueError(f"published share {target} for {year} is not a share")
                svt_pp = factors["pp_of_book"] * (target / world_share)
                rescaled = renewal_pp * (1.0 - target) / (1.0 - world_share)
                endpoints[name] = {
                    "published_svt_account_day_share": round(target, 4),
                    "composition_multiple": round(target / world_share, 4),
                    "svt_pp_of_book": round(svt_pp, 4),
                    "renewal_rescaled": {
                        "renewal_pp_of_book": round(rescaled, 4),
                        "total_pp_of_book": round(svt_pp + rescaled, 4),
                        "reaches_band_low": svt_pp + rescaled >= lo,
                        # What the hazard would STILL have to be multiplied by, after composition
                        # has done all it can. 1.0 or below means composition alone got there.
                        "hazard_multiple_still_required_at_band_low": (
                            round((lo - rescaled) / svt_pp, 4) if svt_pp > 0 else None
                        ),
                    },
                    "renewal_held": {
                        "renewal_pp_of_book": round(renewal_pp, 4),
                        "total_pp_of_book": round(svt_pp + renewal_pp, 4),
                        "reaches_band_low": svt_pp + renewal_pp >= lo,
                        "hazard_multiple_still_required_at_band_low": (
                            round((lo - renewal_pp) / svt_pp, 4) if svt_pp > 0 else None
                        ),
                    },
                }
            bases[basis] = endpoints

        per_year[str(year)] = {
            "accounts": accounts,
            "band_pct": [lo, hi],
            "world_svt_account_day_share": round(world_share, 4),
            "world_svt_pp_of_book": round(factors["pp_of_book"], 4),
            "world_renewal_pp_of_book": round(renewal_pp, 4),
            "world_total_pp_of_book": round(factors["pp_of_book"] + renewal_pp, 4),
            "bases": bases,
        }

    measurable = sorted(per_year)
    # A YEAR THAT WAS ALREADY IN BAND IS NOT A YEAR COMPOSITION CLOSED. Reporting "reaches the band
    # in 1 of 5" without this set would credit the counterfactual with a year it inherited, which is
    # the same shape as a ratio whose numerator and denominator count different things.
    already = [
        y for y in measurable
        if per_year[y]["world_total_pp_of_book"] >= per_year[y]["band_pct"][0]
    ]

    def _closes(accounting: str, basis: str) -> list[str]:
        return [
            y for y in measurable
            if per_year[y]["bases"][basis]["at_published_high"][accounting]["reaches_band_low"]
        ]

    def _newly(accounting: str, basis: str) -> list[str]:
        return [y for y in _closes(accounting, basis) if y not in already]

    return {
        "what_this_is": (
            "The world's SVT account-day share moved to the published GB domestic "
            "default-tariff share, hazards untouched, measured against the same rung-1 band the "
            "verdict uses. `reach x exposure` is rescaled because that product IS the published "
            "statistic's quantity; the renewal route moves with it because the two are complements."
        ),
        "measured_at_anchor": NO_LEVEL_CORRECTION,
        "why_this_anchor": (
            "the per-year anchor acts on the renewal route, so a composition counterfactual run "
            "under the fit would be moving a route the solver had already been paid to correct."
        ),
        "published_series": "tools/published_tariff_mix.DEFAULT_TARIFF_SHARE",
        "headline_accounting": "renewal_rescaled",
        "fitted_years": [str(y) for y in fitted],
        "years_measurable": measurable,
        "years_refused": refused,
        "years_already_reaching_band": already,
        "closes_rung1_at_published_high": {
            "renewal_rescaled": {
                basis: _closes("renewal_rescaled", basis) for basis in ("all_domestic", "as_published")
            },
            "renewal_held": {
                basis: _closes("renewal_held", basis) for basis in ("all_domestic", "as_published")
            },
        },
        "years_newly_closed_by_composition": {
            "renewal_rescaled": {
                basis: _newly("renewal_rescaled", basis) for basis in ("all_domestic", "as_published")
            },
            "renewal_held": {
                basis: _newly("renewal_held", basis) for basis in ("all_domestic", "as_published")
            },
        },
        "per_year": per_year,
        "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --composition",
    }


def _composition_main(table_path: Path) -> int:
    """`--composition`: the published-composition counterfactual, printed and WRITTEN.

    WRITES ON THE REFUSED OUTCOME TOO, for the reason its three siblings do: an absent artefact
    reads as "nobody ran it" and a stale one reads as current.
    """
    all_rows = json.loads(table_path.read_text())
    svt_rows, svt_reason = load_svt_decisions(table_path)
    refusal = (
        svt_reason if svt_rows is None
        else svt_composition_refusal(svt_rows)
        or account_denominator_refusal(all_rows, svt_rows)
    )
    if refusal is not None:
        COMPOSITION_COUNTERFACTUAL.write_text(json.dumps({
            "refused": refusal,
            "capture": str(table_path.relative_to(PROJECT)),
            "what_this_is": "no composition counterfactual could be measured from this capture.",
            "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --composition",
        }, indent=2) + "\n")
        print(f"REFUSED — no composition counterfactual from {table_path.name}: {refusal}")
        return 1
    reading = published_composition_counterfactual(all_rows, svt_rows)
    COMPOSITION_COUNTERFACTUAL.write_text(json.dumps(reading, indent=2) + "\n")
    print("── THE WORLD'S SVT SHARE MOVED TO THE PUBLISHED ONE, HAZARDS UNTOUCHED ──")
    print()
    print(f"{'year':>6} {'world':>7} {'published':>10} {'x':>6} {'band low':>9} "
          f"{'rescaled':>9} {'held':>7}")
    for year in reading["years_measurable"]:
        row = reading["per_year"][year]
        end = row["bases"]["all_domestic"]["at_published_high"]
        print(
            f"{year:>6} {row['world_svt_account_day_share']:>7.3f} "
            f"{end['published_svt_account_day_share']:>10.3f} "
            f"{end['composition_multiple']:>6.2f} {row['band_pct'][0]:>9.1f} "
            f"{end['renewal_rescaled']['total_pp_of_book']:>9.2f}"
            f"{'*' if end['renewal_rescaled']['reaches_band_low'] else ' '} "
            f"{end['renewal_held']['total_pp_of_book']:>6.2f}"
            f"{'*' if end['renewal_held']['reaches_band_low'] else ' '}"
        )
    print()
    for year, why in reading["years_refused"].items():
        print(f"  {year}: REFUSED — {why.split(';')[0]}")
    closes = reading["closes_rung1_at_published_high"]
    print()
    print(f"  reaches the band's low endpoint, consistent accounting: "
          f"{len(closes['renewal_rescaled']['all_domestic'])} of "
          f"{len(reading['years_measurable'])} measurable years "
          f"{closes['renewal_rescaled']['all_domestic']}")
    print(f"  ... on the most generous accounting composition can have: "
          f"{len(closes['renewal_held']['all_domestic'])} of "
          f"{len(reading['years_measurable'])} "
          f"{closes['renewal_held']['all_domestic']}")
    newly = reading["years_newly_closed_by_composition"]
    print(f"  ALREADY in band before the counterfactual: {reading['years_already_reaching_band']}")
    print(f"  NEWLY closed by composition: consistent "
          f"{newly['renewal_rescaled']['all_domestic']}, generous "
          f"{newly['renewal_held']['all_domestic']}")
    print(f"  written to {COMPOSITION_COUNTERFACTUAL.relative_to(PROJECT)}")
    return 0


INTERNAL_RETURN = PROJECT / "docs" / "reports" / "svt_internal_return_and_tenure.json"

#: The three fates an SVT stint can have in this world, and they are exhaustive by construction.
#: A stint's last captured segment either records a departure, or is followed by a fixed renewal
#: for the same account, or neither -- and "neither" is the window ending under the account, which
#: is a CENSORED observation and not a household that stayed. Named rather than inferred because
#: `returned / (returned + departed)` and `returned / all stints` are different quantities and the
#: reader must not have to work out which one a bare "return rate" meant.
STINT_DEPARTED = "departed"
STINT_RETURNED = "returned_to_fixed"
STINT_CENSORED = "still_on_svt_at_window_end"

#: How close after a stint's end a fixed renewal must fall to count as that stint's return. The
#: capture stamps a segment's `event_date` at its START and carries its length separately, so the
#: stint's end is a derived date and the renewal beside it can land a day either side of it. Two
#: days, and the control mutates it: at zero the returns this world actually has are still found,
#: which is what says the tolerance is slack rather than the thing producing the answer.
_RETURN_TOLERANCE_DAYS = 2


def _svt_stints(svt_rows: list[dict]) -> dict[str, list[list[dict]]]:
    """Split each account's captured SVT segments into maximal STINTS, newest last.

    A STINT IS A SPELL ON THE PRODUCT, NOT A SPELL IN THE CAPTURE. `sim_years_on_svt` accumulates
    across consecutive passive anniversaries -- an account that rolls passive twice has one stint
    of two years, not two stints -- and RESETS to zero when the account arrives on the product
    afresh. So the boundary is the reset, and the reset is the only evidence in this artefact that
    the account went somewhere else in between.

    THE RESET IS CORROBORATED AND NOT TRUSTED ALONE. Every one of this capture's 18 resets also
    carries a date gap between the stint's end and the next segment's start, and a fixed renewal
    inside that gap. Three independent marks of the same event; `test_the_stint_boundary_agrees_
    with_the_date_gap` holds the first two together, because a reset without a gap would mean the
    boundary is an artefact of the recorder rather than a move by the household.
    """
    by_account: dict[str, list[dict]] = collections.defaultdict(list)
    for row in svt_rows:
        by_account[row["customer_id"]].append(row)
    stints: dict[str, list[list[dict]]] = {}
    for account, rows in by_account.items():
        rows = sorted(rows, key=lambda r: r["event_date"])
        spells: list[list[dict]] = [[rows[0]]]
        for previous, current in zip(rows, rows[1:]):
            if float(current["sim_years_on_svt"]) < float(previous["sim_years_on_svt"]) - 1e-9:
                spells.append([current])
            else:
                spells[-1].append(current)
        stints[account] = spells
    return stints


def _stint_end(stint: list[dict]) -> datetime.date:
    """The day after a stint's last captured segment, which is the day the account left it."""
    last = stint[-1]
    return datetime.date.fromisoformat(last["event_date"]) + datetime.timedelta(
        days=int(last["sim_segment_days"])
    )


def _stint_fate(
    stint: list[dict],
    next_stint: list[dict] | None,
    renewal_dates: list[datetime.date],
    *,
    tolerance_days: int = _RETURN_TOLERANCE_DAYS,
) -> str:
    """Which of the three fates this stint had.

    THE RENEWAL MUST FALL INSIDE THIS STINT'S OWN INTERVAL and not merely after it. An account with
    three stints has renewals after all three, so "is there a later renewal" would credit the first
    stint with the third stint's return and would count one household's single move three times.
    """
    if stint[-1]["event_type"] == "churned":
        return STINT_DEPARTED
    end = _stint_end(stint)
    horizon = (
        datetime.date.fromisoformat(next_stint[0]["event_date"])
        if next_stint is not None
        else datetime.date.max
    )
    window_opens = end - datetime.timedelta(days=tolerance_days)
    if any(window_opens <= renewal < horizon for renewal in renewal_dates):
        return STINT_RETURNED
    return STINT_CENSORED


def svt_internal_return_and_tenure(renewal_rows: list[dict], svt_rows: list[dict]) -> dict:
    """The world's INTERNAL re-contract rate, and the tenure mix its level implies.

    MEASURED AT `NO_LEVEL_CORRECTION` LIKE EVERY READING IN THIS CHAIN -- and here the anchor is
    irrelevant to the answer rather than merely held fixed, because neither a stint's fate nor an
    account's SVT tenure is a probability. It is stated anyway: a reader who has followed §8-§12
    will ask, and "the anchor cannot reach this" is a better answer than silence.

    WHY THIS READING EXISTS. §15 concluded that the record's dominant internal-switching route --
    a default/SVT household taking a fix with its EXISTING supplier -- is *"a route
    `simulation/renewals.py` does not model at all"*. That was a grep for `same_supplier`, and the
    grep was right. The conclusion is not: `simulation/renewals.py` bounds a passive stint at the
    household's next anniversary and re-enters its own term loop there, so an active draw at that
    anniversary builds a fixed term WITH THIS SAME SUPPLIER. The route is modelled, it is unnamed,
    and until now it was unmeasured.

    THE THREE THINGS THIS SEPARATES, because a bare "internal switching rate" is three quantities:

      * `per_svt_account_year` -- returns over SVT account-years of exposure. The unit in which it
        can be compared with `renewal_engagement.PASSIVE_RENEWAL_RATE`, which is the per-anniversary
        draw that produces it.
      * `of_the_whole_book` -- returns over accounts on the book. The unit Ofgem CIM question C4
        publishes, whose base is all respondents, and therefore the ONLY one in which the world and
        the record can be put beside each other at all.
      * `long_stayer_share` -- the share of SVT account-DAYS carrying three or more years of tenure,
        which is what selects `SVT_INERTIA_ANNUAL_LONG_STAYER` over `SVT_INERTIA_ANNUAL_RECENT`.
        This is the quantity §14 put two published observations of into the tree, for the composition
        question, and which nothing has yet compared with the world.

    THE COMPARISON WITH THE RECORD KEEPS §15'S CONSERVATIVE DIRECTION. CIM C4's internal row is a
    SIX-MONTH recall; `of_the_whole_book` is a FULL YEAR. The world's year is compared against the
    record's half-year WITHOUT annualising the record, so wherever this reading says the world is
    below the record, it is below by at least that much. Annualising would make every gap larger and
    would need an assumption about repeat switching that nothing establishes.
    """
    book = union_by_year(renewal_rows, svt_rows)
    # BINNED ON `event_date`, NOT ON `market_year`, because `_svt_factors` bins on `event_date` and
    # `long_stayer_share_of_svt_account_days` is meant to be read beside section 9's
    # `share_of_decisions_on_the_long_stayer_branch`. Two binnings that agree on today's capture
    # would still be two, and the day they diverge the two readings would disagree for a reason
    # nobody could see.
    svt_by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in svt_rows:
        svt_by_year[int(str(row["event_date"])[:4])].append(row)
    renewal_dates: dict[str, list[datetime.date]] = collections.defaultdict(list)
    for row in renewal_rows:
        renewal_dates[row["customer_id"]].append(datetime.date.fromisoformat(row["event_date"]))

    fates_by_year: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    totals: collections.Counter = collections.Counter()
    for account, spells in _svt_stints(svt_rows).items():
        for index, stint in enumerate(spells):
            following = spells[index + 1] if index + 1 < len(spells) else None
            fate = _stint_fate(stint, following, renewal_dates.get(account, []))
            fates_by_year[_stint_end(stint).year][fate] += 1
            totals[fate] += 1

    per_year: dict[str, dict] = {}
    for year in sorted(svt_by_year):
        rows = svt_by_year[year]
        account_days = sum(float(row["sim_segment_days"]) for row in rows)
        long_days = sum(
            float(row["sim_segment_days"])
            for row in rows
            if float(row["sim_years_on_svt"]) >= SVT_LONG_STAYER_YEARS
        )
        account_years = account_days / 365.25
        accounts = book[year]["accounts"]
        returned = fates_by_year[year][STINT_RETURNED]
        long_share = long_days / account_days if account_days else 0.0
        per_year[str(year)] = {
            "svt_account_years": round(account_years, 4),
            "accounts_on_book": accounts,
            "stint_fates": {fate: fates_by_year[year][fate] for fate in _STINT_FATES},
            "internal_return_rate": {
                "per_svt_account_year": (
                    round(returned / account_years, 6) if account_years else None
                ),
                "of_the_whole_book": round(returned / accounts, 6) if accounts else None,
            },
            "long_stayer_share_of_svt_account_days": round(long_share, 6),
            # What the world's own two published endpoints compose to AT THE MIX THE WORLD IS
            # RUNNING. Not a check and not a target: it is the annual rate `svt_inertia_hazard`
            # would select on average this year before the market multiplier touches it, and it is
            # here so the tenure mix is visible as a RATE rather than only as a share.
            "blended_annual_rate_at_this_mix": round(
                SVT_INERTIA_ANNUAL_RECENT * (1.0 - long_share)
                + SVT_INERTIA_ANNUAL_LONG_STAYER * long_share,
                6,
            ),
        }

    account_years_total = sum(row["svt_account_years"] for row in per_year.values())
    published_band = published_route_split.svt_segment_churn_band()
    observed_hull = published_band["observed_mix_hull"]
    observed_long_share = sorted(
        observation.long_stayer_share
        for observation in published_route_split.SVT_TENURE_OBSERVATIONS
    )
    return {
        "what_this_is": (
            "the world's INTERNAL re-contract route -- an account leaving the SVT product for a "
            "fixed term with THIS SAME supplier -- measured on the committed capture at "
            "`departure_level_anchor.NO_LEVEL_CORRECTION`, beside the tenure mix that route's rate "
            "produces. Finding section 15 concluded the route was not modelled; it is, at "
            "`simulation/renewals.py`'s anniversary re-roll, and this is the first measurement of "
            "it."
        ),
        "measured_at_anchor": NO_LEVEL_CORRECTION,
        "the_anchor_cannot_reach_this": (
            "a stint's fate and an account's SVT tenure are not probabilities, so no value of the "
            "per-year level anchor changes any number in this reading. Stated rather than assumed."
        ),
        "years": sorted(per_year),
        "per_year": per_year,
        "totals": {
            "stint_fates": {fate: totals[fate] for fate in _STINT_FATES},
            "stints": sum(totals.values()),
            "svt_account_years": round(account_years_total, 4),
            "internal_return_rate_per_svt_account_year": (
                round(totals[STINT_RETURNED] / account_years_total, 6)
                if account_years_total
                else None
            ),
        },
        "the_draw_that_produces_it": {
            "constant": "simulation.renewal_engagement.PASSIVE_RENEWAL_RATE",
            "value": PASSIVE_RENEWAL_RATE,
            "published_as": (
                "`docs/market_research/svt_rates_active_passive_2016_2025.md` section 4: "
                "'Fixed at expiry -> active switch | ~35% | Inverse of SVT rollover share at "
                "expiry'. A rate defined AT A FIXED-TERM EXPIRY."
            ),
            "the_second_use_that_is_not_sourced": (
                "`simulation/renewals.py` draws the same constant at an SVT ANNIVERSARY, where "
                "`simulation/svt_product.py`'s own docstring says there is 'No term boundary ... "
                "nothing is renewed, nothing is offered, and the household makes no decision'. One "
                "published anchor, two events, and nothing in the tree sources the second."
            ),
            "realised_over_drawn": (
                round(
                    (totals[STINT_RETURNED] / account_years_total) / PASSIVE_RENEWAL_RATE, 6
                )
                if account_years_total and PASSIVE_RENEWAL_RATE
                else None
            ),
            "why_they_differ": (
                "`active_renewal_probability_for_customer` threads a PERSISTENT per-household "
                "engagement archetype through the draw, so the households that reach the SVT "
                "product are the disengaged tail and the population rate does not describe them. "
                "The realised rate is a fact about who is on the product, not about the constant."
            ),
        },
        "against_the_record": _internal_return_vs_record(per_year),
        "tenure_mix_vs_the_published_observations": {
            "what_this_is": (
                "section 14 put two published observations of the SVT segment's within-segment "
                "long-stayer share into the tree -- to compose the published churn band for the "
                "phi question -- and nothing has compared them with the world's own mix. This is "
                "that comparison, and it bears on section 9's headline because section 9's "
                "1.67x-1.71x was taken against the published RECENT endpoint at a mix of 0.000 and "
                "0.202."
            ),
            "observed_long_stayer_share": [
                round(observed_long_share[0], 6), round(observed_long_share[-1], 6)
            ],
            "observed_mix_hull_band": list(observed_hull),
            "years_whose_mix_is_inside_the_observed_range": [
                year for year, row in sorted(per_year.items())
                if observed_long_share[0]
                <= row["long_stayer_share_of_svt_account_days"]
                <= observed_long_share[-1]
            ],
            "years_whose_mix_is_below_every_observation": [
                year for year, row in sorted(per_year.items())
                if row["long_stayer_share_of_svt_account_days"] < observed_long_share[0]
            ],
            "what_this_does_to_section_9s_headline": _headline_at_the_observed_mix(
                renewal_rows, svt_rows, observed_hull, per_year
            ),
        },
        "what_this_does_not_do": (
            "it does not close rung 1, and that is knowable before it runs. The internal return is "
            "a mechanism INSIDE section 9's `exposure` factor, and section 9's saturation bound "
            "already put reach and exposure at their ceilings TOGETHER -- abolishing the renewal "
            "route with them -- and reached the band's low endpoint in 1 year of 7. Nothing here "
            "can do more than that bound already did."
        ),
        "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --internal-return",
    }


_STINT_FATES = (STINT_RETURNED, STINT_DEPARTED, STINT_CENSORED)


def _headline_at_the_observed_mix(
    renewal_rows: list[dict],
    svt_rows: list[dict],
    observed_hull: list[float],
    per_year: dict[str, dict],
) -> dict:
    """Section 9's `required / published` multiple, re-taken against a tenure-composed band.

    WHY THIS IS A DIFFERENT NUMBER AND NOT A CORRECTION TO ARITHMETIC. Section 9 divided the
    record's required hazard by the flat published `SVT_INERTIA_ANNUAL_RECENT = 0.20` and got
    1.67x at 2019 and 1.71x at 2020. 0.20 is the RECENT segment's upper endpoint -- the rate for a
    household under three years on the product -- and section 9 chose it because those two years
    are the base window where the market re-referencing factor is ~1.0 and because the world's mix
    there is almost all recent. Both true. What neither section could see is that section 14 then
    put two published observations of the SVT segment's tenure mix into the tree for a different
    question, and the world's mix in those two years (0.000 and 0.202) is BELOW both of them
    (0.370 and 0.558).

    So section 9's denominator is the published band's upper endpoint at a tenure mix nothing has
    observed. Re-taken against `observed_mix_hull` -- the band the published rates compose to at
    every mix between the two observations -- the multiple is LARGER. That widens section 9's gap
    in the same direction section 15's `J_svt >= 0` ceiling did, and it is a second, independent
    route to the same conclusion.

    BOTH ENDPOINTS ARE REPORTED AND THE GENEROUS ONE LEADS. The hull's HIGH end is the smallest
    multiple the composition admits, so quoting it alone would be the flattering choice and quoting
    the low end alone would be the alarming one.
    """
    shortfall = svt_route_shortfall_decomposition(renewal_rows, svt_rows)
    window = shortfall["base_window_comparison"]
    hull_low, hull_high = observed_hull
    years = {}
    for year, row in window["years"].items():
        required = row["required_hazard_at_band_low"]
        years[year] = {
            "world_long_stayer_share": per_year[year][
                "long_stayer_share_of_svt_account_days"
            ] if year in per_year else None,
            "required_hazard_at_band_low": required,
            "section_9_multiple_over_published_recent": row["required_over_published_recent"],
            "multiple_over_the_observed_mix_hull": {
                "at_the_hulls_high_end": round(required / hull_high, 4) if hull_high else None,
                "at_the_hulls_low_end": round(required / hull_low, 4) if hull_low else None,
            },
        }
    return {
        "what_this_is": (
            "section 9's headline multiple re-taken against the tenure-composed band from section "
            "14's two observations, instead of against the flat published recent endpoint."
        ),
        "published_recent_endpoint": window["published_annual_recent"],
        "observed_mix_hull": [hull_low, hull_high],
        "years": years,
        "direction": (
            "LARGER, in both base-window years and at both endpoints of the hull. Section 9's gap "
            "against the world's own source is understated, not overstated, and this is a second "
            "route to section 15's conclusion that arrives from the tenure mix rather than from "
            "the internal/external split."
        ),
    }


def _internal_return_vs_record(per_year: dict[str, dict]) -> dict:
    """The world's ANNUAL whole-book internal rate against CIM C4's SIX-MONTH internal row.

    THE DIRECTION IS DELIBERATE AND IT IS THE ONE THAT COSTS US. Comparing a year against a half
    year flatters the world; where the world still comes out BELOW the record it is below by at
    least that much. Annualising the record would need a repeat-switching assumption nothing
    establishes, and section 15 already refused to make it for the same row.

    A WAVE WHOSE RECALL WINDOW TOUCHES A YEAR THE CAPTURE DOES NOT COVER IS REFUSED, NOT SCORED.
    `None` with the missing years named, never a silent drop and never a zero -- an absent year and
    a year in which nobody re-contracted produce the same count otherwise.
    """
    waves = []
    for observation in published_route_split.SWITCHER_SPLIT_OBSERVATIONS:
        window = [str(year) for year in observation.recall_window_years]
        missing = [year for year in window if year not in per_year]
        record = observation.internal_rate_of_all_households
        if missing:
            waves.append({
                "wave": observation.wave,
                "fieldwork": observation.fieldwork,
                "recall_window_years": window,
                "record_internal_rate_six_months": round(record, 6),
                "world_internal_rate_year": None,
                "world_below_record": None,
                "refused": (
                    f"the capture carries no SVT year for {', '.join(missing)}, so this wave's "
                    f"window cannot be scored against it"
                ),
            })
            continue
        # The window's HIGHEST world year, because taking the maximum is the choice that argues
        # AGAINST a finding that the world is short.
        world = max(per_year[year]["internal_return_rate"]["of_the_whole_book"] for year in window)
        waves.append({
            "wave": observation.wave,
            "fieldwork": observation.fieldwork,
            "recall_window_years": window,
            "record_internal_rate_six_months": round(record, 6),
            "world_internal_rate_year": round(world, 6),
            "world_below_record": world < record,
            "refused": None,
        })
    scored = [wave for wave in waves if wave["refused"] is None]
    # THE LEVEL WAS THE WRONG QUESTION AND THE SPREAD IS THE RIGHT ONE, and this is derived here
    # rather than written as prose because a published cause authored by hand rots beside the
    # measurement that refutes it. The record's internal row is remarkably STABLE across the
    # crisis and after it; this world's is not, and "is the world above or below" cannot see that.
    record_rates = [wave["record_internal_rate_six_months"] for wave in scored]
    touched = sorted({year for wave in scored for year in wave["recall_window_years"]})
    world_rates = {
        year: per_year[year]["internal_return_rate"]["of_the_whole_book"] for year in touched
    }
    record_span = (min(record_rates), max(record_rates)) if record_rates else (None, None)
    inside = [
        year for year, rate in world_rates.items()
        if rate is not None and record_span[0] <= rate <= record_span[1]
    ]
    return {
        "what_this_is": (
            "Ofgem CIM question C4's 'switched tariff with the same supplier' row, base all "
            "respondents, over a SIX-MONTH recall, against this world's whole-book internal "
            "re-contract rate over a FULL YEAR."
        ),
        "waves": waves,
        "waves_scored": len(scored),
        "waves_the_world_is_below": [
            wave["wave"] for wave in scored if wave["world_below_record"]
        ],
        "the_shape_rather_than_the_level": {
            "what_this_is": (
                "whether this world's internal rate sits in the interval the record's six waves "
                "span. Derived, not asserted: the finding here is not that the world is short but "
                "that the record's internal route is STABLE and this world's is not."
            ),
            "record_spans": [
                round(record_span[0], 6) if record_span[0] is not None else None,
                round(record_span[1], 6) if record_span[1] is not None else None,
            ],
            "record_widest_ratio": (
                round(record_span[1] / record_span[0], 4)
                if record_span[0] else None
            ),
            "world_rate_in_each_year_the_waves_touch": world_rates,
            "years_touched": touched,
            "years_inside_the_records_span": inside,
        },
        "a_caveat_this_reading_does_not_resolve": (
            "C4's internal code is 'switched tariff with the same supplier' as the household "
            "reports it, and a fixed term expiring ONTO the default tariff is also a tariff change "
            "with the same supplier. Section 15 read the row as re-contracting onto a fix. If some "
            "of it is the opposite move, the record's internal row overstates the quantity this "
            "world's return route models, and the gap below is smaller than it reads. Nothing "
            "published separates the two directions and this reading does not assume one."
        ),
    }


def _internal_return_main(table_path: Path) -> int:
    """`--internal-return`: measure the world's internal re-contract route, print it, and WRITE it.

    WRITES ON THE REFUSED OUTCOME TOO, for the reason the mains beside it do: a missing file reads
    as 'nobody ran it' and a stale one reads as current.
    """
    all_rows = json.loads(table_path.read_text())
    svt_rows, svt_reason = load_svt_decisions(table_path)
    refusal = (
        svt_reason if svt_rows is None
        else svt_composition_refusal(svt_rows)
        or account_denominator_refusal(all_rows, svt_rows)
    )
    if refusal is not None:
        INTERNAL_RETURN.write_text(json.dumps({
            "refused": refusal,
            "capture": str(table_path.relative_to(PROJECT)),
            "what_this_is": (
                "no internal re-contract reading could be measured from this capture. The refusal "
                "is written rather than withheld."
            ),
            "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --internal-return",
        }, indent=2) + "\n")
        print(f"REFUSED — no internal-return reading from {table_path.name}: {refusal}")
        return 1
    reading = svt_internal_return_and_tenure(all_rows, svt_rows)
    INTERNAL_RETURN.write_text(json.dumps(reading, indent=2) + "\n")
    draw = reading["the_draw_that_produces_it"]
    totals = reading["totals"]
    print("── THE WORLD'S INTERNAL RE-CONTRACT ROUTE, WHICH §15 SAID IT DID NOT HAVE ──")
    print()
    print(f"  {totals['stints']} SVT stints: "
          f"{totals['stint_fates'][STINT_RETURNED]} returned to a fixed term with us, "
          f"{totals['stint_fates'][STINT_DEPARTED]} departed, "
          f"{totals['stint_fates'][STINT_CENSORED]} still on SVT at the window's end")
    print(f"  J_world = {totals['internal_return_rate_per_svt_account_year']:.4f} per SVT "
          f"account-year, against a drawn {draw['value']} "
          f"({draw['realised_over_drawn']:.3f}x)")
    print()
    print(f"{'year':>6} {'acct-yrs':>9} {'ret':>4} {'dep':>4} {'cens':>5} {'J/acct-yr':>10} "
          f"{'of book':>8} {'long-stayer':>12} {'blended':>8}")
    for year in reading["years"]:
        row = reading["per_year"][year]
        rate = row["internal_return_rate"]
        fates = row["stint_fates"]
        print(f"{year:>6} {row['svt_account_years']:>9.2f} {fates[STINT_RETURNED]:>4} "
              f"{fates[STINT_DEPARTED]:>4} {fates[STINT_CENSORED]:>5} "
              f"{(rate['per_svt_account_year'] or 0.0):>10.4f} "
              f"{(rate['of_the_whole_book'] or 0.0):>8.4f} "
              f"{row['long_stayer_share_of_svt_account_days']:>12.4f} "
              f"{row['blended_annual_rate_at_this_mix']:>8.4f}")
    record = reading["against_the_record"]
    print()
    print("── AGAINST THE RECORD (Ofgem CIM C4, six-month recall, vs this world's FULL YEAR) ──")
    print()
    for wave in record["waves"]:
        if wave["refused"] is not None:
            print(f"  W{wave['wave']} {wave['fieldwork']:>24}: REFUSED — {wave['refused']}")
            continue
        verdict = "world BELOW record" if wave["world_below_record"] else "world above record"
        print(f"  W{wave['wave']} {wave['fieldwork']:>24}: record "
              f"{wave['record_internal_rate_six_months']:.4f}/6mo  world "
              f"{wave['world_internal_rate_year']:.4f}/yr   {verdict}")
    print(f"  world is below the record in {len(record['waves_the_world_is_below'])} of "
          f"{record['waves_scored']} scored waves: {record['waves_the_world_is_below']}")
    shape = record["the_shape_rather_than_the_level"]
    print()
    print(f"  AND THE LEVEL IS THE WRONG QUESTION. The record's six waves span "
          f"{shape['record_spans'][0]:.4f}–{shape['record_spans'][1]:.4f} — a factor of "
          f"{shape['record_widest_ratio']:.2f} across the crisis and after it.")
    print(f"  This world sits inside that span in "
          f"{len(shape['years_inside_the_records_span'])} of "
          f"{len(shape['years_touched'])} years those waves touch: "
          + ", ".join(f"{y} {shape['world_rate_in_each_year_the_waves_touch'][y]:.4f}"
                      for y in shape["years_touched"]))
    mix = reading["tenure_mix_vs_the_published_observations"]
    print()
    print("── THE TENURE MIX §14 SOURCED, AGAINST THE WORLD'S ──")
    print()
    print(f"  observed within-segment long-stayer share: "
          f"{mix['observed_long_stayer_share'][0]:.4f} – {mix['observed_long_stayer_share'][1]:.4f}")
    print(f"  years inside that range: {mix['years_whose_mix_is_inside_the_observed_range']}")
    print(f"  years BELOW every observation: {mix['years_whose_mix_is_below_every_observation']}")
    headline = mix["what_this_does_to_section_9s_headline"]
    print()
    print(f"  §9's headline re-taken against the tenure-composed hull "
          f"{headline['observed_mix_hull']} instead of the flat "
          f"{headline['published_recent_endpoint']}:")
    for year, row in headline["years"].items():
        over = row["multiple_over_the_observed_mix_hull"]
        print(f"    {year}: world mix {row['world_long_stayer_share']:.3f}, "
              f"§9 said {row['section_9_multiple_over_published_recent']:.2f}x — at the hull it is "
              f"{over['at_the_hulls_high_end']:.2f}x to {over['at_the_hulls_low_end']:.2f}x")
    print(f"    {headline['direction']}")
    print()
    print(f"  {reading['what_this_does_not_do']}")
    print(f"  written to {INTERNAL_RETURN.relative_to(PROJECT)}")
    return 0


def _renewal_risks(row: dict, anchor: float) -> dict[str, float]:
    """`{cause: hazard}` for one captured renewal decision at one anchor.

    THE ONE PLACE THIS MODULE TURNS A CAPTURED ROW INTO HAZARDS. The fitter, the emergent sweep,
    the route attribution and the counterfactual all reach the world through here, so a correction
    to how a row is read cannot land in some of them and miss the others -- which is the failure
    `DEFAULT_TABLE`'s own note records this module already had once, in a different form.
    """
    return build_departure_risks(
        bill_shock_base=row["sim_bill_shock_base"],
        price_response=row["sim_price_response"],
        dissatisfaction_response=row["sim_dissatisfaction_response"],
        market_opportunity=row["sim_market_opportunity"],
        action_propensity=row["sim_action_propensity"],
        retention_offer_retained_fraction=1.0,
        sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
        shock_weight=DECLARED_SHOCK_WEIGHT,
        level_anchor=anchor,
    )


def _renewal_probabilities(rows: list[dict], anchor: float, amplify: float = 1.0) -> list[float]:
    """Per-household departure probability on the renewal route, one value per decision.

    `amplify` scales the two OPPORTUNITY-SCALED hazards and nothing else -- it is the counterfactual
    the finding's prescribed repair amounts to, applied at the only place that repair could act.
    Dissatisfaction is deliberately untouched: `build_departure_risks` does not scale it by
    `market_opportunity` on purpose, and amplifying it here would be measuring a different repair
    from the one being tested.
    """
    out = []
    for r in rows:
        risks = _renewal_risks(r, anchor)
        if amplify != 1.0:
            risks = {
                cause: (min(h * amplify, WORLD_MAX_CHURN_PROBABILITY)
                        if cause in _OPPORTUNITY_SCALED_CAUSES else h)
                for cause, h in risks.items()
            }
        out.append(total_departure_probability(risks))
    return out


#: The two hazards `build_departure_risks` scales by `market_opportunity`, and therefore the only
#: two a household-amplitude repair could reach. Named from the module that defines them rather
#: than spelled as strings, so a cause renamed there cannot leave this counterfactual silently
#: measuring one leg.
_OPPORTUNITY_SCALED_CAUSES = frozenset({CAUSE_BILL_SHOCK, CAUSE_PRICE_POSITION})

#: The amplification ladder. Doubling, because the question is which way the slope MOVES and a
#: ladder fine enough to argue about would invite reading a preferred rung off it. The bound the
#: argument actually rests on is `ceiling_rung` below, not the top of this ladder.
_AMPLIFICATION_LADDER = (1.0, 2.0, 4.0, 8.0)


def _amplification_counterfactual(
    renewal_rows: list[dict], svt_rows: list[dict], years: list[int],
    accounts: dict[int, int], svt: dict[int, list[float]], xs: list[float],
    bands: dict[int, tuple[float, float]],
) -> dict:
    """What amplifying the household opportunity response does to the level and to the amplitude.

    THE POINT OF THIS BLOCK IS A NEGATIVE RESULT AND IT IS THE USEFUL ONE. The finding's owed item
    2 is "repair the mechanism's compression", and the gap it is blocked on is the household-level
    amplitude of switching response. This walks that repair up to and past any value that gap could
    return, and reports that the relative slope FALLS the whole way while the level overshoots.
    A repair that cannot reach the defect it was prescribed for is worth knowing about before the
    evidence for it arrives, not after.
    """
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for row in renewal_rows:
        if row.get("sim_bill_shock_base") is not None:
            by_year[int(row["event_date"][:4])].append(row)
    rungs = []
    for amplify in _AMPLIFICATION_LADDER:
        renewal = {
            y: _renewal_probabilities(by_year[y], NO_LEVEL_CORRECTION, amplify) for y in years
        }
        series = _route_series({y: renewal[y] + svt[y] for y in years}, accounts, years)
        rungs.append({
            "amplification": amplify,
            "emergent_pp_of_book": {str(y): round(v, 4) for y, v in zip(years, series)},
            "relative_slope": round(_relative_slope(xs, series), 4),
            "in_band": sum(
                1 for y, v in zip(years, series) if _instrument.inside_band(v, *bands[y])
            ),
        })
    # THE BOUND, AND IT IS WHAT MAKES THIS A REFUTATION RATHER THAN A TREND. Every opportunity
    # hazard of every renewal household in every year set to the world's own churn ceiling: not a
    # plausible world, deliberately, because it is the MOST this leg can do by construction. A
    # ladder shows a direction and a reader may always suppose the next rung turns it round; a
    # ceiling cannot be argued past.
    ceiling = {
        y: [
            total_departure_probability({
                **_renewal_risks(r, NO_LEVEL_CORRECTION),
                CAUSE_BILL_SHOCK: WORLD_MAX_CHURN_PROBABILITY,
                CAUSE_PRICE_POSITION: WORLD_MAX_CHURN_PROBABILITY,
            })
            for r in by_year[y]
        ]
        for y in years
    }
    ceiling_series = _route_series({y: ceiling[y] + svt[y] for y in years}, accounts, years)
    return {
        "what_this_is": (
            "the world re-measured with the two opportunity-scaled hazards (bill shock and price "
            "position) multiplied by each factor, at the identity anchor. This is the repair "
            "`SEAT_FINDING_THE_LEVEL_IS_CLAMPED_...` §4 item 2 prescribes, walked past any value "
            "the household-amplitude gap could supply. The level rises without bound and the "
            "relative slope FALLS, because the renewal route contributes a near-constant and "
            "adding a constant to a proportional quantity dilutes its proportionality."
        ),
        "ladder": rungs,
        "ceiling_rung": {
            "what_this_is": (
                "both opportunity hazards at `departure_risks.WORLD_MAX_CHURN_PROBABILITY` for "
                "every renewal household in every year -- the upper bound on what amplifying this "
                "leg can do to the world, not a world anybody proposes."
            ),
            "emergent_pp_of_book": {
                str(y): round(v, 4) for y, v in zip(years, ceiling_series)
            },
            "relative_slope": round(_relative_slope(xs, ceiling_series), 4),
            "in_band": sum(
                1 for y, v in zip(years, ceiling_series) if _instrument.inside_band(v, *bands[y])
            ),
        },
        "reading": (
            "no amplification of the household opportunity response moves the relative slope "
            "toward 1.0 -- it falls monotonically, and at the world's own churn ceiling, which is "
            "the most this leg can ever do, the world's amplitude is essentially gone while its "
            "level overshoots every band. So the household-level amplitude gap -- however it is "
            "eventually answered -- is not what is holding rung 1."
        ),
    }


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


def _route_attribution_main(table_path: Path) -> int:
    """`--route-attribution`: measure which route carries the amplitude, print it, and WRITE it.

    WRITES ON THE REFUSED OUTCOME TOO, for the reason `_emergent_verdict_main` above does: a
    producer whose only failure mode is to write nothing leaves the previous run's file looking
    current, and this repo has been bitten by that absence twice.
    """
    all_rows = json.loads(table_path.read_text())
    svt_rows, svt_reason = load_svt_decisions(table_path)
    refusal = (
        svt_reason if svt_rows is None
        else svt_composition_refusal(svt_rows)
        or account_denominator_refusal(all_rows, svt_rows)
    )
    if refusal is not None:
        ROUTE_ATTRIBUTION.write_text(json.dumps({
            "refused": refusal,
            "capture": str(table_path.relative_to(PROJECT)),
            "what_this_is": (
                "no route attribution could be measured from this capture. The refusal is written "
                "rather than withheld: a missing file reads as 'nobody ran it', and a stale one "
                "left in place reads as current."
            ),
            "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --route-attribution",
        }, indent=2) + "\n")
        print(f"REFUSED — no route attribution from {table_path.name}: {refusal}")
        return 1
    att = route_amplitude_attribution(all_rows, svt_rows)
    ROUTE_ATTRIBUTION.write_text(json.dumps(att, indent=2) + "\n")
    print("── WHICH ROUTE CARRIES THE RECORD'S YEAR-TO-YEAR AMPLITUDE ──")
    print()
    print(f"{'route':>16} {'rel. slope':>11} {'95% interval':>20} {'n decisions':>12}")
    for name, route in att["routes"].items():
        iv = route["interval_95"]
        shown = f"[{iv['lo']:+.3f}, {iv['hi']:+.3f}]" if iv["available"] else iv["why_not"]
        print(f"{name:>16} {route['relative_slope']:>+11.4f} {shown:>20} "
              f"{sum(route['decisions'].values()):>12}")
    print()
    print("  1.0 = tracks the record proportionally.  0.0 = does not move with the record.")
    print()
    print(f"{'amplify':>9} {'rel. slope':>11} {'in band':>9}   the prescribed household repair, "
          f"walked past any value its gap could supply")
    for rung in att["household_amplification_counterfactual"]["ladder"]:
        print(f"{rung['amplification']:>9.1f} {rung['relative_slope']:>+11.4f} "
              f"{rung['in_band']:>4}/{len(att['years'])}")
    print()
    print(f"  {att['household_amplification_counterfactual']['reading']}")
    print(f"  written to {ROUTE_ATTRIBUTION.relative_to(PROJECT)}")
    return 0


def _svt_shortfall_main(table_path: Path) -> int:
    """`--svt-shortfall`: measure which leg of the SVT route is short, print it, and WRITE it.

    WRITES ON THE REFUSED OUTCOME TOO, for the reason the two mains above do.
    """
    all_rows = json.loads(table_path.read_text())
    svt_rows, svt_reason = load_svt_decisions(table_path)
    refusal = (
        svt_reason if svt_rows is None
        else svt_composition_refusal(svt_rows)
        or account_denominator_refusal(all_rows, svt_rows)
    )
    if refusal is not None:
        SVT_SHORTFALL.write_text(json.dumps({
            "refused": refusal,
            "capture": str(table_path.relative_to(PROJECT)),
            "what_this_is": (
                "no SVT shortfall decomposition could be measured from this capture. The refusal "
                "is written rather than withheld: a missing file reads as 'nobody ran it', and a "
                "stale one left in place reads as current."
            ),
            "how_to_regenerate": "python3 -m tools.fit_year_level_anchor --svt-shortfall",
        }, indent=2) + "\n")
        print(f"REFUSED — no SVT shortfall decomposition from {table_path.name}: {refusal}")
        return 1
    reading = svt_route_shortfall_decomposition(all_rows, svt_rows)
    SVT_SHORTFALL.write_text(json.dumps(reading, indent=2) + "\n")
    print("── WHICH LEG OF THE SVT ROUTE IS SHORT ──")
    print()
    print(f"  {reading['identity']}")
    print()
    print(f"{'year':>6} {'reach':>7} {'exposure':>9} {'hazard':>8} {'svt pp':>8} "
          f"{'needs x':>8}   headroom: reach / exposure / hazard")
    for year in reading["years"]:
        row = reading["per_year"][year]
        f, h = row["factors"], row["headroom_to_ceiling"]
        print(f"{year:>6} {f['reach']:>7.3f} {f['exposure']:>9.3f} {f['hazard']:>8.4f} "
              f"{row['svt_pp_of_book']:>8.3f} {row['required_multiple']['at_band_low']:>8.3f}   "
              f"{h['reach']:>5.2f} / {h['exposure']:>5.2f} / {h['hazard']:>5.2f}")
    print()
    for name, closed in reading["years_a_factor_could_close_alone"].items():
        print(f"  {name:>9}: closes {len(closed['years'])} of {closed['of']} years alone "
              f"(ceiling {closed['ceiling']})")
    sat = reading["bounded_factor_saturation"]
    print()
    print(f"  BOTH bounded factors at their ceiling, renewal route abolished with them: reaches "
          f"the band's low endpoint in {sat['reaches_band_low_in']} of {sat['of']} years.")
    for year, cmp_ in reading["base_window_comparison"]["years"].items():
        print(f"  {year} (published rate unmodified): world {cmp_['world_hazard']:.4f}/acct-yr, "
              f"record needs {cmp_['required_hazard_at_band_low']:.4f} = "
              f"{cmp_['required_over_published_recent']:.2f}x the published "
              f"{reading['base_window_comparison']['published_annual_recent']}")
    print(f"  written to {SVT_SHORTFALL.relative_to(PROJECT)}")

    # THE REQUIRED HAZARD IS PRINTED BESIDE WHAT THE RECORD ADMITS, and that pairing is the
    # finding's §11 second owed item rather than a decoration. `required_hazard` above is
    # conditional on the world's OWN SVT share, which the composition counterfactual then measured
    # as BELOW the published one -- so a reader who sees "the record needs 0.334" and nothing else
    # will read it as a repair to apply, and at 2017 applying it alongside the share correction
    # OVERSHOOTS the record. Each of those two readings holds the other's subject fixed by
    # construction, so neither can say so. This is the only place they are printed together.
    print()
    print("── AND WHAT THE PUBLISHED RECORD ADMITS FOR IT (tools.published_route_split) ──")
    print()
    print(f"{'year':>6} {'world':>8} {'needs':>8}   admissible H_svt, phi in [0,1] (all-domestic)")
    for year in reading["years"]:
        row = reading["per_year"][year]
        admissible = published_route_split.admissible_svt_churn(int(year), "all_domestic")
        needs = row["required_hazard"]["at_band_low"]
        head = f"{year:>6} {row['factors']['hazard']:>8.4f} {needs:>8.4f}   "
        if admissible is None:
            print(head + "REFUSED — no published default-tariff share for this year")
            continue
        lo, hi = admissible["admissible"]
        verdict = "admits it" if lo <= needs <= hi else "REFUSES the required hazard"
        print(head + f"{lo:>7.3f} – {hi:<7.3f}  {verdict}")
    print()
    print("  The interval is wide because phi -- the external share of active fixed-term renewals")
    print("  -- is UNESTABLISHED, not because the arithmetic is loose. Where it contains both the")
    print("  published 0.20 and the required value, the record cannot tell them apart, and that")
    print("  is a result. See finding §11 and docs/reports/published_route_split.json.")
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    table_path = Path(args[0]) if args else DEFAULT_TABLE
    if "--emergent-verdict" in argv[1:]:
        return _emergent_verdict_main(table_path)
    if "--route-attribution" in argv[1:]:
        return _route_attribution_main(table_path)
    if "--svt-shortfall" in argv[1:]:
        return _svt_shortfall_main(table_path)
    if "--composition" in argv[1:]:
        return _composition_main(table_path)
    if "--internal-return" in argv[1:]:
        return _internal_return_main(table_path)
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
