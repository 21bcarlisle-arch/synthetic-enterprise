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
import math
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
        **CORRECTED 2026-09-19, BESIDE THE CLAIM AND NOT OVER IT: "the ONLY one" stopped being true
        when `b721b6acf` landed `published_route_split.svt_internal_conversion_floor`.** That bound
        is on `J_svt` ITSELF -- conversions per SVT HOUSEHOLD -- so `per_svt_account_year` is now
        comparable to the record too, and it is the better comparison of the two: C4's raw internal
        row mixes this route with fixed-term active renewal, and the floor is that row with the
        renewal route's ceiling netted off. `against_the_floor_for_this_route` below is that
        comparison and `against_the_record` above is kept unchanged beside it.
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
    # WHO converted, not only HOW MANY conversions. The published record bounds an INCIDENCE -- a
    # household counted once however many times it moved -- so the count of distinct converting
    # accounts is the world's own numerator of that kind, and the ratio of the two is the world's
    # repeat factor. Collected in the walk that was already happening rather than in a second one.
    converters_by_year: dict[int, set[str]] = collections.defaultdict(set)
    for account, spells in _svt_stints(svt_rows).items():
        for index, stint in enumerate(spells):
            following = spells[index + 1] if index + 1 < len(spells) else None
            fate = _stint_fate(stint, following, renewal_dates.get(account, []))
            fates_by_year[_stint_end(stint).year][fate] += 1
            totals[fate] += 1
            if fate == STINT_RETURNED:
                converters_by_year[_stint_end(stint).year].add(account)

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
            # The HEADCOUNT pair beside the exposure pair, for `as_an_incidence` below. An account
            # that spent six weeks on the product counts once here and 0.115 of a year above, and
            # that difference is most of the distance between the world's published figure and the
            # kind of quantity the two published bounds actually bound.
            "svt_accounts_touched": len({row["customer_id"] for row in rows}),
            "accounts_that_converted": len(converters_by_year[year]),
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
        # APPENDED AFTER the keys the previous artefact carried, so a reader diffing the two sees an
        # addition rather than a rewrite -- the same ordering rule `published_route_split.
        # svt_segment_churn_band` states for its own dict.
        "against_the_floor_for_this_route": _internal_return_vs_the_published_floor(
            per_year,
            round(totals[STINT_RETURNED] / account_years_total, 6)
            if account_years_total else None,
        ),
        "against_the_ceiling_for_this_route": _internal_return_vs_the_published_ceiling(
            per_year,
            round(totals[STINT_RETURNED] / account_years_total, 6)
            if account_years_total else None,
        ),
        "against_the_band_in_annual_units": _internal_return_vs_the_annualised_band(
            round(totals[STINT_RETURNED] / account_years_total, 6)
            if account_years_total else None,
        ),
        # APPENDED, for the reason the two above were: this does not restate any key already here,
        # it says what KIND of quantity they all are. It is last because it is the reading that
        # grades the other three rather than a fourth comparison beside them.
        "as_an_incidence_which_is_what_the_record_bounds": _internal_return_as_an_incidence(
            per_year
        ),
        # APPENDED after the reading it grades, for the reason every key above it was appended. That
        # reading's band rests on an ASSUMPTION on its lower leg where the upper leg rests on
        # arithmetic; this measures the assumption instead of naming it.
        "the_base_the_lower_endpoint_divides_by": _internal_return_incidence_by_its_base(
            renewal_rows,
            svt_rows,
            round(totals[STINT_RETURNED] / account_years_total, 6)
            if account_years_total else None,
        ),
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
        # CORRECTED 2026-09-19, BESIDE THE CLAIM AND NOT OVER IT. Nothing above is changed: the
        # comparison is still the one the record's raw internal row supports, and it is still worth
        # having. What it could not know is that the row is MIXED, and that a bound on this route
        # alone now exists.
        "this_comparison_is_against_the_MIXED_quantity": (
            "`I` is internal switching over ALL households and `published_route_split`'s own "
            "identity makes it `s*J_svt + (1-s)*0.35*(1-phi)` -- this route PLUS fixed-term active "
            "renewal. The world figure above counts only this route, so the world is carrying one "
            "numerator against a record filled by two and `world_below_record` is biased toward "
            "True for a reason that is not about the world. `against_the_floor_for_this_route` is "
            "the same question asked of a bound on THIS route alone, which "
            "`svt_internal_conversion_floor` made available on 2026-09-19; read that one for the "
            "verdict and this one for the shape."
        ),
        "a_caveat_this_reading_does_not_resolve": (
            "C4's internal code is 'switched tariff with the same supplier' as the household "
            "reports it, and a fixed term expiring ONTO the default tariff is also a tariff change "
            "with the same supplier. Section 15 read the row as re-contracting onto a fix. If some "
            "of it is the opposite move, the record's internal row overstates the quantity this "
            "world's return route models, and the gap below is smaller than it reads. Nothing "
            "published separates the two directions and this reading does not assume one."
        ),
    }


def _internal_return_vs_the_published_floor(
    per_year: dict[str, dict], world_rate_per_svt_account_year: float | None
) -> dict:
    """The world's `J_svt` against the floor the record sets for `J_svt` ITSELF, not for `I`.

    WHY THIS EXISTS BESIDE `_internal_return_vs_record` RATHER THAN REPLACING IT. That function
    compares this world's internal return rate against CIM C4's internal-switching row `I`, and when
    it was written `I` was the only published quantity there was. `I` is MIXED:
    `published_route_split`'s own identity says `I = s*J_svt + (1-s)*0.35*(1-phi)`, so it contains
    the fixed-term renewal route as well as this one -- while the world figure it is compared against
    counts ONLY stints returning to a fixed term. A numerator carrying one route over a denominator
    the record fills with two is the mixed-quantity comparison this repository keeps paying for, and
    `b721b6acf` is what made it avoidable: `svt_internal_conversion_floor` nets the renewal route's
    ceiling off `I` and leaves a bound on `J_svt` alone.

    THE SEAM, AND IT CROSSES NO WALL. The published floor is a CHECK on what the world produces and
    `svt_internal_conversion_floor`'s own docstring refuses to be a parameter -- so it reaches the
    world's SVT-side decision by JUDGING ITS OUTPUT, never by being imported into it. That is why
    this reading lives here: `tools/` may read both the record and a committed capture, and
    `simulation/` may import neither `tools.published_route_split` nor `tools.published_tariff_mix`
    (`test_the_published_route_split_does_not_read_the_worlds_clipped_constants`,
    `test_the_published_check_band_cannot_be_read_by_the_world_it_judges`). No world-side constant is
    minted and the rate gap keeps its one home.

    WHAT EACH NUMBER COUNTS, because the last comparison went wrong by not asking:
      * WORLD -- `returned_to_fixed` stints over SVT account-DAYS/365.25 of exposure, binned on the
        year the stint ENDS. Conversions per SVT account-year, on this book's resi electricity
        accounts.
      * FLOOR -- `(I - (1-s)*0.35) / s_max`, conversions per SVT household per six months, on GB
        domestic survey respondents across both fuels.
      Same KIND of quantity -- conversions per SVT household per unit of exposure on the product --
      which is what makes this admissible and the mixed one above not. `s` enters the floor as the
      published share of the household STOCK over the recall window, so its denominator is
      exposure-like over that window; a household converting mid-window is counted whole, which
      makes the record's denominator slightly larger than true exposure and the floor slightly
      understated -- the same conservative direction the floor's own three choices already take.

    THE BAR IS WEAK IN A NAMED DIRECTION AND IS NOT STRENGTHENED HERE. A six-month floor used as an
    annual bar is LOWER than the true annual bar, so `clears_the_binding_floor` is the flattering
    verdict and a year that comes out BELOW is below by at least that much. Annualising the floor
    would need the repeat-switching assumption `svt_internal_conversion_floor` declines to make and
    that `_internal_return_vs_record` refused for the same row; inventing one to strengthen this
    reading's own verdict is the one move that would make it worthless.

    FAILS CLOSED. A floor of `None` is reported as a refusal with its reason, never as a pass.
    """
    floor_reading = published_route_split.svt_internal_conversion_floor()
    floor = floor_reading["binding_floor"]
    per_year_verdicts: dict[str, dict] = {}
    for year, row in sorted(per_year.items()):
        rate = row["internal_return_rate"]["per_svt_account_year"]
        per_year_verdicts[year] = {
            "world_per_svt_account_year": rate,
            "svt_account_years": row["svt_account_years"],
            "returns": row["stint_fates"][STINT_RETURNED],
            "clears_the_binding_floor": (
                None if (floor is None or rate is None) else rate >= floor
            ),
        }
    scored = [
        year for year, cell in per_year_verdicts.items()
        if cell["clears_the_binding_floor"] is not None
    ]
    below = [year for year in scored if not per_year_verdicts[year]["clears_the_binding_floor"]]
    clearing = [year for year in scored if per_year_verdicts[year]["clears_the_binding_floor"]]
    return {
        "what_this_is": (
            "this world's SVT-to-fixed internal conversion rate against "
            "`published_route_split.svt_internal_conversion_floor`, which bounds that SAME route "
            "from below. The un-mixed companion to `against_the_record`, which compares against "
            "CIM C4's raw internal row and therefore against both routes at once."
        ),
        "refused": (
            None if floor is not None else
            "the record establishes no binding floor from any wave, so there is no bar to judge "
            "against. Reported rather than passed."
        ),
        "binding_floor": floor,
        "binding_floor_unit": floor_reading["binding_floor_unit"],
        "binding_floor_source": floor_reading["source"],
        "waves_with_a_floor": floor_reading["waves_with_a_floor"],
        "the_point_estimate_is_still": floor_reading["the_point_estimate_is"],
        "what_each_number_counts": {
            "world": (
                "`returned_to_fixed` stints over SVT account-years of exposure, binned on the year "
                "the stint ends. This book's resi electricity accounts."
            ),
            "floor": (
                "(I - (1-s)*0.35) / s_max -- conversions per SVT household per six months. GB "
                "domestic survey respondents, both fuels."
            ),
            "the_two_mismatches_that_are_named_and_not_corrected": (
                "a full year against a six-month bar, and this book's electricity accounts against "
                "GB households. Both are stated because neither is closed."
            ),
        },
        "the_bar_is_weak_in_this_direction": (
            "a six-month floor used as an annual bar is LOWER than the true annual bar, so "
            "`clears_the_binding_floor` is the flattering verdict and a year BELOW it is below by "
            "at least that much. The floor is deliberately not annualised here."
        ),
        "world_per_svt_account_year": world_rate_per_svt_account_year,
        "clears_the_binding_floor": (
            None if (floor is None or world_rate_per_svt_account_year is None)
            else world_rate_per_svt_account_year >= floor
        ),
        "multiple_of_the_binding_floor": (
            None if (not floor or world_rate_per_svt_account_year is None)
            else round(world_rate_per_svt_account_year / floor, 4)
        ),
        "per_year": per_year_verdicts,
        "years_scored": scored,
        "years_below_the_floor": below,
        "years_clearing_the_floor": clearing,
        # DERIVED, NEVER DECLARED. A verdict that is the same in every year would make a control
        # keyed to the count green for a reason that has nothing to do with the mechanism, and the
        # spread is the reading: the level clears comfortably and three individual years do not.
        "the_verdict_is_not_uniform": bool(below) and bool(clearing),
        "years_below_with_no_returns_at_all": [
            year for year in below if per_year_verdicts[year]["returns"] == 0
        ],
        # The record's OWN register of years its identity cannot describe, imported rather than
        # restated, so a below-floor year that the record itself excludes is visible as such.
        "years_the_record_calls_a_structural_break": {
            year: reason for year, reason in (
                (year, published_route_split.STRUCTURAL_BREAK_YEARS.get(int(year)))
                for year in below
            )
            if reason is not None
        },
        "what_this_cannot_say": (
            "nothing about whether the world's rate is RIGHT. The floor is one-sided and the point "
            "estimate `SVT_INTERNAL_CONVERSION_RATE` is still None, so a world four times the floor "
            "is not thereby four times too high -- it is above a bound and the bound has no ceiling "
            "beside it. It also cannot attribute a below-floor year: 2016 is the report window's "
            "first year and carries 0.0055 SVT account-years, which is an exposure count and not a "
            "behaviour, and 2022 is the year the record's own register excludes."
        ),
        # CORRECTED 2026-09-19, BESIDE THE SENTENCE AND NOT OVER IT. "the bound has no ceiling
        # beside it" was true when written and stopped being true the same day: the identity that
        # gives the floor also gives `svt_internal_conversion_ceiling`, and the sentence above is
        # kept verbatim because a claim with its refutation next to it is the only evidence the
        # claim was made before the answer was known.
        "there_is_now_a_ceiling_beside_it": (
            "`against_the_ceiling_for_this_route`, from the same identity at phi = 1. The "
            "preceding sentence is left as written; this is what corrects it."
        ),
        "the_decision_this_judges": (
            "one call to `renewal_engagement.rolls_active_renewal` answers two different household "
            "decisions -- coming off a FIXED term (which the 35% anchor is cut on) and coming off an "
            "SVT STINT (an internal switch, which nothing published cuts). This reading is where "
            "that borrow becomes refutable, and it is refutable HERE rather than in `simulation/` "
            "because the published floor is a check and a check may not reach the thing it judges. "
            "See docs/staging/SEAT_DECISION_THE_SVT_SIDE_DECISION_IS_NAMED_ON_THE_CHECK_SIDE_"
            "BECAUSE_A_CHECK_MAY_NOT_REACH_THE_WORLD_IT_JUDGES_2026-09-19.md."
        ),
    }


def _internal_return_vs_the_published_ceiling(
    per_year: dict[str, dict], world_rate_per_svt_account_year: float | None
) -> dict:
    """The world's `J_svt` against the ceiling the record sets for `J_svt`, the floor's other side.

    WHY A SECOND BOUND ON THE SAME QUANTITY IS NOT A SECOND HOME FOR IT. `against_the_floor_for_
    this_route` closes with *"the bound has no ceiling beside it"*, and that was the honest reading
    of a one-sided bound the world clears by 4.14x: a floor that far below what it judges can refuse
    nothing any world here would produce. This is the other side, out of the same identity at the
    other endpoint of `phi`, and the two together are a BAND. The rate gap still has exactly one
    home -- `SVT_INTERNAL_CONVERSION_RATE`, still None -- because a band is not a point estimate.

    THE DIRECTION OF SAFETY INVERTS BETWEEN THE TWO BOUNDS AND THAT IS THE WHOLE CARE THIS NEEDS.
    Both bars are six-month rates read against an annual world figure, deliberately un-annualised in
    both cases. For the FLOOR that is the flattering direction: the true annual floor is higher, so
    clearing the six-month one is the weak verdict. For the CEILING the identical fact runs the
    other way: the true annual ceiling is higher too, so the six-month bar is HARSHER than the
    record supports, `clears_the_binding_ceiling` is the STRONG verdict, and an exceedance
    establishes nothing whatever. A reader holding both bounds at once will reach for "the world
    breaches the ceiling in four years" as a refutation, and it is not one.

    WHAT EACH NUMBER COUNTS, asked again here rather than inherited from the floor's answer:
      * WORLD -- unchanged from the floor's reading: `returned_to_fixed` stints over SVT
        account-years of exposure, binned on the year the stint ENDS, this book's resi electricity
        accounts.
      * CEILING -- `I / s_min`, conversions per SVT household per six months, GB domestic survey
        respondents across both fuels. Same KIND of quantity as the floor and as the world, which
        is what makes the band admissible at all.

    **CORRECTED 2026-09-19, BESIDE THE SENTENCE AND NOT OVER IT. The last clause above is FALSE and
    it was the only thing licensing this band.** The ceiling is the same kind as the FLOOR -- both
    are incidences, because CIM C4 counts a household once however many times it moved and the
    arithmetic deriving both bounds preserves that. It is NOT the same kind as the WORLD, which is
    an event count over exposure. The sentence is kept verbatim because a claim with its refutation
    next to it is the only evidence the claim was made before the answer was known.

    What replaces it is a measurement, not a second assertion. The reading
    `as_an_incidence_which_is_what_the_record_bounds` states the world in the record's kind, finds
    the numerator half an EQUIVALENCE on this capture (no account converts twice in a year) and the
    denominator half live (exposure is 0.70 of headcount), and returns the world as a BAND -- whose
    upper endpoint is the figure judged here. Every verdict in THIS function is
    unaffected in direction -- the world's event rate is the band's upper endpoint, so a world
    within this ceiling on the event rate is within it on the incidence too, which is the strong
    verdict this function already claims. The floor is where the correction bites, and it bites
    there because that is the live side.

    FAILS CLOSED. A ceiling of `None` is reported as a refusal with its reason, never as a pass.
    """
    ceiling_reading = published_route_split.svt_internal_conversion_ceiling()
    ceiling = ceiling_reading["binding_ceiling"]
    banner_ceiling = ceiling_reading["binding_ceiling_from_the_tariff_banner"]
    floor = published_route_split.svt_internal_conversion_floor()["binding_floor"]
    per_year_verdicts: dict[str, dict] = {}
    for year, row in sorted(per_year.items()):
        rate = row["internal_return_rate"]["per_svt_account_year"]
        per_year_verdicts[year] = {
            "world_per_svt_account_year": rate,
            "svt_account_years": row["svt_account_years"],
            "returns": row["stint_fates"][STINT_RETURNED],
            "clears_the_binding_ceiling": (
                None if (ceiling is None or rate is None) else rate <= ceiling
            ),
        }
    scored = [
        year for year, cell in per_year_verdicts.items()
        if cell["clears_the_binding_ceiling"] is not None
    ]
    above = [year for year in scored if not per_year_verdicts[year]["clears_the_binding_ceiling"]]
    clearing = [year for year in scored if per_year_verdicts[year]["clears_the_binding_ceiling"]]
    return {
        "what_this_is": (
            "this world's SVT-to-fixed internal conversion rate against "
            "`published_route_split.svt_internal_conversion_ceiling`, which bounds that SAME route "
            "from ABOVE. The other side of `against_the_floor_for_this_route`, and the side that "
            "can actually refuse: the floor sits at 0.24x the world and this ceiling at 1.43x."
        ),
        "refused": (
            None if ceiling is not None else
            "the record establishes no binding ceiling from any wave, so there is no bar to judge "
            "against. Reported rather than passed."
        ),
        "binding_ceiling": ceiling,
        "binding_ceiling_unit": ceiling_reading["binding_ceiling_unit"],
        "binding_ceiling_source": ceiling_reading["source"],
        "waves_with_a_ceiling": ceiling_reading["waves_with_a_ceiling"],
        "the_point_estimate_is_still": ceiling_reading["the_point_estimate_is"],
        "the_bar_is_weak_in_this_direction": ceiling_reading["the_verdict_that_is_safe"],
        "world_per_svt_account_year": world_rate_per_svt_account_year,
        "clears_the_binding_ceiling": (
            None if (ceiling is None or world_rate_per_svt_account_year is None)
            else world_rate_per_svt_account_year <= ceiling
        ),
        "share_of_the_binding_ceiling": (
            None if (not ceiling or world_rate_per_svt_account_year is None)
            else round(world_rate_per_svt_account_year / ceiling, 4)
        ),
        # The tighter bound is CARRIED but never becomes the bar. It costs one assumption -- that a
        # household which has just taken a fix says so when asked -- and the verdict is reported
        # under both so a reader can see the assumption buys no change of verdict here.
        "binding_ceiling_from_the_tariff_banner": banner_ceiling,
        "what_the_banner_ceiling_assumes": ceiling_reading["what_the_banner_ceiling_assumes"],
        "clears_the_banner_ceiling_too": (
            None if (banner_ceiling is None or world_rate_per_svt_account_year is None)
            else world_rate_per_svt_account_year <= banner_ceiling
        ),
        "per_year": per_year_verdicts,
        "years_scored": scored,
        "years_above_the_ceiling": above,
        "years_within_the_ceiling": clearing,
        # DERIVED, NEVER DECLARED -- the same shape the floor's reading uses, and it earns its place
        # for the same reason: the level clears and four individual years do not, so a verdict
        # frozen either way would look exactly like the mechanism working.
        "the_verdict_is_not_uniform": bool(above) and bool(clearing),
        "the_band_is_now_two_sided": {
            "floor": floor,
            "ceiling": ceiling,
            "world": world_rate_per_svt_account_year,
            "world_is_inside_the_band": (
                None if (floor is None or ceiling is None
                         or world_rate_per_svt_account_year is None)
                else floor <= world_rate_per_svt_account_year <= ceiling
            ),
            "why_this_is_the_gain": (
                "a one-sided bound at 0.24x of the thing it bounds refuses nothing. The band is "
                "[floor, ceiling] and the world sits at 0.70 of its width from the top, so the "
                "next change to the SVT-side decision can now be refused in the direction it is "
                "most likely to move -- upward, since the borrowed 35% fixed-expiry anchor is "
                "cut on a population that renews more often than an SVT household converts."
            ),
        },
        "what_this_cannot_say": (
            "that the world's rate is right. Two bounds are not a point estimate and "
            "`SVT_INTERNAL_CONVERSION_RATE` is still None with its gap named. It also cannot call "
            "any of the four above-ceiling years a breach: the bar is a six-month rate read as an "
            "annual one, which for a CEILING is harsher than the record supports, so those four "
            "years are where the bound is live and not where it has fired."
        ),
        "the_decision_this_judges": (
            "the same borrow `against_the_floor_for_this_route` names -- one call to "
            "`renewal_engagement.rolls_active_renewal` answering both a FIXED-term expiry and an "
            "SVT stint. The floor could only refuse that borrow if it were set far too LOW; this "
            "ceiling is what could refuse it for being too HIGH, which is the direction a "
            "fixed-expiry anchor borrowed for a default-tariff household would err in."
        ),
    }


def _internal_return_vs_the_annualised_band(
    world_rate_per_svt_account_year: float | None,
) -> dict:
    """The world against BOTH bounds restated in the world's own units, which are annual.

    WHY THIS IS NOT A THIRD BOUND. `against_the_floor_for_this_route` and `against_the_ceiling_for_
    this_route` both judge an ANNUAL world figure against a SIX-MONTH bar, and each carries a
    sentence saying which direction that makes safe. This asks the question those two sentences
    leave open: what happens to the verdicts when the bars are put into the world's units instead.
    The answer is not symmetric, and the asymmetry is the reading.

    `published_route_split.svt_internal_conversion_annualisation` does the arithmetic and owns the
    evidence; this function does nothing but stand the world beside it, because the check may not
    reach the world it judges and the record may not know about the world at all.

    THE TWO VERDICTS MOVE IN OPPOSITE DIRECTIONS, and a reader who expects annualising to sharpen
    both has the thing exactly backwards:

      * THE CEILING ONLY LOOSENS. The annual ceiling is between 1x and 2x the six-month bar, so
        the world's share of it falls from 0.70 to somewhere in [0.35, 0.70]. **Every one of the
        four above-ceiling years is further from a breach in annual units than in six-month ones,
        not closer** -- so no amount of evidence about repeat switching can turn them into one.
      * THE FLOOR ONLY TIGHTENS, and it tightens a long way: from 0.0449 at total repetition to
        0.1676 at none. The world clears even the tightest corner, but by 1.1x rather than 4.1x,
        and a multiple that close is a bound that could plausibly refuse the next change to the
        SVT-side decision. **That makes the floor the live side of this band.**

    FAILS CLOSED. A missing bound at either end is reported with its reason and never as a pass,
    and `the_world_clears_the_tightest_floor` is `None` rather than `True` when the floor is `None`.
    """
    reading = published_route_split.svt_internal_conversion_annualisation()
    ceilings = reading["annual_ceiling_at_each_endpoint"]
    loosest_ceiling = ceilings["a_2_no_switcher_repeats"]
    tightest_ceiling = ceilings["a_1_every_switcher_repeats"]
    tightest_floor = reading["the_floor_if_nobody_repeats"]
    floor_in_force = reading["the_floor_in_force_is_the_total_repetition_corner"]
    world = world_rate_per_svt_account_year
    return {
        "what_this_is": (
            "both published bounds on `J_svt` restated in the world's own ANNUAL units, and the "
            "world beside them. Not a new bound -- the same two, with the six-month convention "
            "that both of them carry taken off."
        ),
        "refused": (
            None if (world is not None and tightest_ceiling is not None
                     and tightest_floor is not None) else
            "one of the world rate, the ceiling or the floor is absent, so there is no annual "
            "comparison to make. Reported rather than passed."
        ),
        "world_per_svt_account_year": world,
        "annualisation_factor_band": reading["annualisation_factor_band"],
        "why_the_factor_is_a_band_and_not_a_number": reading["why_there_is_no_repeat_share"],
        # ---- ceiling: loosens, in every case ----
        "annual_ceiling_span": [tightest_ceiling, loosest_ceiling],
        "share_of_the_tightest_annual_ceiling": (
            None if (not tightest_ceiling or world is None)
            else round(world / tightest_ceiling, 4)
        ),
        "share_of_the_loosest_annual_ceiling": (
            None if (not loosest_ceiling or world is None)
            else round(world / loosest_ceiling, 4)
        ),
        "the_ceiling_can_only_loosen": reading["no_published_fact_can_tighten_the_ceiling"],
        # ---- floor: tightens, and this is where the evidence would land ----
        "annual_floor_span": [floor_in_force, tightest_floor],
        "multiple_of_the_floor_in_force": (
            None if (not floor_in_force or world is None)
            else round(world / floor_in_force, 4)
        ),
        "multiple_of_the_tightest_annual_floor": (
            None if (not tightest_floor or world is None)
            else round(world / tightest_floor, 4)
        ),
        "the_world_clears_the_tightest_floor": (
            None if (tightest_floor is None or world is None) else world >= tightest_floor
        ),
        # DERIVED, NEVER DECLARED, and it is the whole point of the function. The live side is
        # whichever bound the world sits closest to once both are in annual units; writing the
        # answer down as a literal would survive the world moving past either bound.
        "the_live_side_of_the_band": (
            None if (world is None or tightest_floor is None or loosest_ceiling is None)
            else (
                "FLOOR" if (world - tightest_floor) < (loosest_ceiling - world) else "CEILING"
            )
        ),
        "why_that_inverts_what_the_ceiling_landed_under": (
            "`svt_internal_conversion_ceiling` landed as *the side that can refuse*, and against a "
            "six-month bar it looked like it: the world sat at 0.70 of it with four years above. "
            "In annual units the world sits at 0.35-0.70 of the ceiling and at 1.11-4.14x the "
            "floor, so the floor is the closer bound and the one a change to the SVT-side "
            "decision could actually trip. The ceiling's own sentence is left standing where it "
            "is written and this is what corrects it."
        ),
        "what_this_cannot_say": (
            "that the world's rate is right, and not that any year breaches anything. Annualising "
            "moves both bars AWAY from every above-ceiling year, so those four years are further "
            "from a breach here than they were before -- the opposite of what the claim that drew "
            "this work expected, and the reason it is written down rather than left implied. It "
            "also compares an EVENT count (the world's returned stints over exposure) against two "
            "bounds built from an INCIDENCE (households reporting at least one switch), and those "
            "coincide only where nobody repeats: at the r = 0 corner they are the same quantity "
            "and away from it the world's numerator is the larger, which flatters the floor "
            "verdict and harshens the ceiling one."
        ),
        # CORRECTED 2026-09-19, BESIDE THE SENTENCE AND NOT OVER IT. The DIRECTION above survives
        # measurement; the CAUSE does not. The sentence attributes the whole gap to repetition, and
        # `as_an_incidence_which_is_what_the_record_bounds` finds the world's repeat factor is
        # exactly 1 -- the world IS at the r = 0 corner on the numerator, and every bit of the gap
        # comes from the denominator instead, exposure being 0.70 of headcount. A true statement
        # with the wrong cause under it is this project's own catalogued shape, so it is named here
        # rather than left for a reader to infer the gap closes when repetition does.
        "the_gap_is_real_but_not_for_the_reason_above": (
            "the world's repeat factor is 1.000 -- 49 conversions by 49 distinct accounts -- so "
            "repetition contributes NOTHING to the mismatch on this capture. The gap is entirely "
            "the denominator: account-YEARS of exposure against a headcount of accounts touched. "
            "The direction stated above is unchanged; its cause is not what it says."
        ),
        "the_clearing_verdict_here_is_the_bands_upper_endpoint": (
            "`multiple_of_the_tightest_annual_floor` is 1.11 and it is the TOP of the kind-matched "
            "band, whose bottom is 0.77 of the same bar. The band straddles the tightest annual "
            "floor, so clearance of it was never established -- see "
            "`as_an_incidence_which_is_what_the_record_bounds`. The floor IN FORCE is cleared by "
            "both endpoints and the conclusion that the floor is the live side is sharpened, not "
            "weakened."
        ),
    }


def _verdict_over_a_band(band: list[float | None], bar: float | None, side: str) -> bool | None:
    """Does a world known only to lie in `band` clear `bar`? `None` when the band straddles it.

    THE WHOLE POINT IS THE THIRD ANSWER. Every verdict in this chain was two-valued because the
    world was a single number; once it is a band, "the band contains the bar" is a distinct outcome
    from both pass and fail, and collapsing it into either is how an unestablished verdict gets
    published as an established one. Fails closed in the literal sense -- an absent endpoint or an
    absent bar returns `None`, never `True`.
    """
    if bar is None or any(endpoint is None for endpoint in band):
        return None
    clears = [
        (endpoint >= bar) if side == "FLOOR" else (endpoint <= bar)
        for endpoint in band
        if endpoint is not None
    ]
    if not clears:
        return None
    return True if all(clears) else (False if not any(clears) else None)


def _internal_return_as_an_incidence(per_year: dict[str, dict]) -> dict:
    """The world's internal return as the KIND of quantity the two published bounds actually bound.

    THE DEFECT THIS EXISTS TO REPAIR, NAMED PLAINLY. `_internal_return_vs_the_published_ceiling`
    asserts in its own docstring that the ceiling is the *"Same KIND of quantity as the floor and as
    the world, which is what makes the band admissible at all"*. **That sentence is false**, and it
    was the only thing licensing the band. Ofgem CIM C4's internal row is an INCIDENCE -- the share
    of households reporting AT LEAST ONE internal switch in six months, one per household however
    many times they moved -- and both bounds are derived from it by arithmetic that preserves that
    kind. The world's figure is `returned_to_fixed` stints over SVT account-years: an EVENT COUNT
    over EXPOSURE, which can exceed 1 and which an incidence cannot.

    It does not follow that the band is inadmissible. It follows that whether it is admissible is a
    MEASUREMENT, and nobody had taken it. This is that measurement.

    TWO DISTORTIONS, AND THEY ARE NOT THE SAME SIZE. Write `E` for the published event rate and `J`
    for the incidence on a headcount base:

      * THE NUMERATOR. `E` counts conversions, `J` counts converting households. Their ratio is the
        world's own repeat factor and it is **1.000 in every year of this capture** -- 49
        conversions by 49 distinct accounts, no account converting twice. So on this capture the
        numerator half of the conflation is an EQUIVALENCE, which is a finding and not a clearance:
        `simulation/renewals.py` bounds a passive stint at the next anniversary and a fixed term
        runs about a year, so a second conversion inside one calendar year has nowhere to happen.
        Shorten fixed terms and it stops being true with nothing to say so, which is why
        `repeat_factor` is DERIVED here and keyed to by a control rather than written into prose.
      * THE DENOMINATOR, which is the live half. `E` divides by account-YEARS of exposure and `J`
        by a headcount of accounts touched; accounts join and leave the product mid-year, so the
        exposure denominator is about 0.70 of the headcount one and `E` is correspondingly larger.

    WHY THE ANSWER IS A BAND AND NOT A CORRECTED NUMBER. Neither endpoint is the record's quantity.
    A survey's base is the households on the default tariff AT FIELDWORK, each with a full window's
    exposure; `accounts_touched` includes accounts that were on the product for six weeks, and those
    dilute the incidence downward. So the true kind-matched figure is bounded on BOTH sides::

        J_touched  <=  J_true  <=  E

    The upper leg is structural: conversions are at least conversion-having households, and a
    per-exposure rate is at least the incidence full exposure would produce (`1 - exp(-h) <= h`).
    The lower leg rests on ONE named assumption -- that an account's chance of converting does not
    DECREASE with its exposure -- which is an assumption, stated here rather than buried, and not a
    number anyone picked. Picking a point inside the band would mint exactly the constant
    `SVT_INTERNAL_CONVERSION_RATE` refuses to be.

    WHAT IT DOES TO THE LIVE SIDE OF THE BAND, which is the reason this was worth measuring. The
    world's published figure clears the tightest annual floor at 1.11x. Its kind-matched lower
    endpoint sits at 0.77x of the same bar. **The band straddles the tightest annual floor**, so the
    honest verdict there is not "clears" and not "fails" -- it is that the record cannot tell, and
    `clears_the_tightest_annual_floor` returns `None` to say so. The bound actually IN FORCE (the
    `r = 1` corner, 0.0449) is cleared by both endpoints and is unaffected.

    FAILS CLOSED throughout: a straddle is `None`, an absent endpoint is `None`, and no leg here
    returns `True` on missing evidence.
    """
    annual = published_route_split.svt_internal_conversion_annualisation()
    scored = [row for row in per_year.values() if row["svt_account_years"]]
    events = sum(row["stint_fates"][STINT_RETURNED] for row in scored)
    converters = sum(row["accounts_that_converted"] for row in scored)
    account_years = sum(row["svt_account_years"] for row in scored)
    touched = sum(row["svt_accounts_touched"] for row in scored)

    per_year_rows: dict[str, dict] = {}
    for year, row in sorted(per_year.items()):
        year_events = row["stint_fates"][STINT_RETURNED]
        year_converters = row["accounts_that_converted"]
        year_touched = row["svt_accounts_touched"]
        year_exposure = row["svt_account_years"]
        per_year_rows[year] = {
            "conversions": year_events,
            "accounts_that_converted": year_converters,
            # `None` rather than 1.0 when nobody converted: a year with no events establishes
            # nothing about repetition, and a 1.0 there would read as evidence that it holds.
            "repeat_factor": (
                None if not year_converters else round(year_events / year_converters, 6)
            ),
            "event_rate_per_svt_account_year": (
                None if not year_exposure else round(year_events / year_exposure, 6)
            ),
            "incidence_per_svt_account_touched": (
                None if not year_touched else round(year_converters / year_touched, 6)
            ),
        }

    event_rate = round(events / account_years, 6) if account_years else None
    incidence = round(converters / touched, 6) if touched else None
    band = [incidence, event_rate]
    tightest_floor = annual["the_floor_if_nobody_repeats"]
    floor_in_force = annual["the_floor_in_force_is_the_total_repetition_corner"]
    ceilings = annual["annual_ceiling_at_each_endpoint"]
    return {
        "what_this_is": (
            "the world's internal return expressed as the INCIDENCE the two published bounds "
            "actually bound, beside the EVENT RATE every earlier reading in this chain published. "
            "Not a third bound and not a correction to the world: a statement of what the world's "
            "figure counts, and of how far that is from what the record's figure counts."
        ),
        "refused": (
            None if (event_rate is not None and incidence is not None) else
            "the capture carries no scored SVT year with both exposure and a headcount, so neither "
            "kind of rate can be formed. Reported rather than passed."
        ),
        "the_two_quantities": {
            "the_record_bounds": (
                "an INCIDENCE -- the share of SVT households reporting AT LEAST ONE internal "
                "switch in the window, one per household however many times they moved. CIM C4, "
                "carried through both bounds unchanged by the arithmetic that derives them."
            ),
            "the_world_published": (
                "an EVENT COUNT over EXPOSURE -- `returned_to_fixed` stints over SVT account-years "
                "-- which can exceed 1 and which an incidence cannot."
            ),
            "they_coincide_only_where": (
                "nobody converts twice in the window AND exposure equals headcount. The first "
                "holds on this capture and the second does not."
            ),
        },
        # ---- the numerator half: an equivalence on this capture, and derived so it can stop being
        # one without anybody editing this docstring ----
        "conversions": events,
        "accounts_that_converted": converters,
        "repeat_factor": (
            None if not converters else round(events / converters, 6)
        ),
        "no_account_converts_twice_in_a_year": (
            None if not converters else events == converters
        ),
        "what_the_repeat_factor_being_one_means": (
            "the numerator half of the event-vs-incidence conflation is an EQUIVALENCE on this "
            "capture, not a defect and not a clearance. It holds because a fixed term runs about a "
            "year and a passive stint is bounded at the next anniversary, so a second conversion "
            "inside one calendar year has nowhere to happen. It is a property of the world's term "
            "lengths, not of the comparison, and it is derived here so that shortening them reds a "
            "control instead of silently reopening the gap."
        ),
        # ---- the denominator half: the live one ----
        "svt_account_years": round(account_years, 4),
        "svt_accounts_touched": touched,
        "exposure_per_account_touched": (
            None if not touched else round(account_years / touched, 6)
        ),
        "why_the_denominators_differ": (
            "accounts join and leave the SVT product mid-year. An account on the product for six "
            "weeks contributes one to the headcount and 0.115 to the account-years, so the "
            "exposure denominator is the smaller and the event rate the larger. This is the half "
            "of the conflation that is live on this capture."
        ),
        # ---- the band, DERIVED, and the reason it is a band ----
        "event_rate_per_svt_account_year": event_rate,
        "incidence_per_svt_account_touched": incidence,
        "the_kind_matched_band": band,
        "why_it_is_a_band_and_not_a_corrected_number": (
            "neither endpoint is the record's quantity. A survey's base is the households on the "
            "default tariff at fieldwork, each with a full window's exposure; `accounts_touched` "
            "includes accounts on the product for weeks, which dilutes the incidence downward. So "
            "J_touched <= J_true <= E. The upper leg is structural; the lower leg costs one named "
            "assumption -- that conversion probability does not DECREASE with exposure. Choosing a "
            "point inside would mint the constant `SVT_INTERNAL_CONVERSION_RATE` refuses to be."
        ),
        # DERIVED, NEVER DECLARED. The ordering is the claim the whole band rests on; a hand-written
        # True here would survive the two endpoints crossing, which is exactly the state in which
        # every verdict below becomes meaningless.
        "the_band_is_ordered": (
            None if (incidence is None or event_rate is None) else incidence <= event_rate
        ),
        # ---- what it does to each bound, three-valued ----
        "the_floor_in_force": floor_in_force,
        "clears_the_floor_in_force": _verdict_over_a_band(band, floor_in_force, "FLOOR"),
        "the_tightest_annual_floor": tightest_floor,
        "clears_the_tightest_annual_floor": _verdict_over_a_band(band, tightest_floor, "FLOOR"),
        "the_tightest_annual_ceiling": ceilings["a_1_every_switcher_repeats"],
        "within_the_tightest_annual_ceiling": _verdict_over_a_band(
            band, ceilings["a_1_every_switcher_repeats"], "CEILING"
        ),
        "multiple_of_the_tightest_annual_floor_at_each_endpoint": [
            None if not tightest_floor or endpoint is None
            else round(endpoint / tightest_floor, 4)
            for endpoint in band
        ],
        # DERIVED. The bar the band straddles is the one whose verdict the conflation was deciding,
        # and naming it is worth more than the three flags above read separately.
        "bars_this_band_cannot_decide": [
            name for name, bar in (
                ("the_floor_in_force", floor_in_force),
                ("the_tightest_annual_floor", tightest_floor),
                ("the_tightest_annual_ceiling", ceilings["a_1_every_switcher_repeats"]),
            )
            if _verdict_over_a_band(
                band, bar, "CEILING" if "ceiling" in name else "FLOOR"
            ) is None and bar is not None
        ],
        "per_year": per_year_rows,
        "what_this_changes_about_the_published_reading": (
            "`against_the_band_in_annual_units` reports the world at 1.11x the tightest annual "
            "floor and concludes the floor is the live side. The first half is the band's UPPER "
            "endpoint: the lower endpoint is at 0.77x the same bar, so the band straddles it and "
            "the clearing verdict was never established. The conclusion that the FLOOR is the live "
            "side is not weakened by this -- it is sharpened, because the bar the world cannot be "
            "shown to clear is on that side. The bound actually in force, the r = 1 corner at "
            "0.0449, is cleared by both endpoints and is untouched."
        ),
        "what_this_cannot_say": (
            "that the world's rate is wrong, or that it breaches anything. The tightest annual "
            "floor is the r = 0 corner of a family whose `r` is a declared None -- it is the "
            "tightest bar the record COULD support, not a bar the record makes -- so failing to "
            "establish clearance of it refutes nothing. It also cannot repair the remaining "
            "mismatch between an account base and a survey's respondent base; it can only measure "
            "which way that runs, which is the direction already stated."
        ),
    }


def _binomial_tail(successes: int, trials: int, p: float) -> float:
    """`P(X >= successes)` for `X ~ Binomial(trials, p)`, summed in LOG SPACE.

    The obvious `math.comb(n, i) * p**i * (1-p)**(n-i)` overflows `float` above about n = 2000, and
    the sample sizes this is asked about deliberately include counterfactual ones several times the
    capture's own -- so the arithmetic that answers "how big would the sample have to be" must not
    fall over exactly where that question lives.
    """
    if successes <= 0:
        return 1.0
    if successes > trials:
        return 0.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    log_p, log_q, log_n = math.log(p), math.log1p(-p), math.lgamma(trials + 1)

    def term(i: int) -> float:
        return math.exp(
            log_n - math.lgamma(i + 1) - math.lgamma(trials - i + 1)
            + i * log_p + (trials - i) * log_q
        )

    # WHICHEVER TAIL IS SHORTER, because `_smallest_deciding_base` calls this tens of thousands of
    # times at four-figure `trials` and the upper tail there is four fifths of the range. Summing
    # the short side and subtracting is the same number to within float noise and about four times
    # the speed -- which is the difference between a reading that runs and one nobody re-runs.
    if successes * 2 > trials:
        return sum(term(i) for i in range(successes, trials + 1))
    return 1.0 - sum(term(i) for i in range(successes))


def _exact_binomial_interval(
    successes: int, trials: int, *, alpha: float = 0.05
) -> list[float] | None:
    """Clopper-Pearson `[lo, hi]` for `successes / trials`, or `None` when `trials` is zero.

    EXACT AND NOT NORMAL. The bases this is asked of run down to a few hundred account-years with
    fewer than fifty events, and the question put to the interval is one-sided and near the edge of
    it -- *does the lower limit clear a published floor* -- which is precisely where the normal
    approximation's symmetry misleads. Clopper-Pearson is conservative in the direction that matters
    here: it will refuse to decide more often than the truth requires, never less.

    FAILS CLOSED at both degenerate ends: `k = 0` pins `lo` at 0.0 and `k = n` pins `hi` at 1.0
    rather than inventing a limit from a tail that carries no observation.

    CLAUDE.md: *"a figure published without the bound its sample size earns is worse than no
    figure"*. This is the bound. `test_the_exact_binomial_interval_reproduces_published_values`
    holds it against textbook values, because an interval routine that is quietly wrong would make
    every verdict below wrong in the flattering direction and nothing else here would notice.
    """
    if trials <= 0:
        return None
    low = 0.0
    if successes > 0:
        a, b = 0.0, 1.0
        for _ in range(60):
            mid = (a + b) / 2.0
            if _binomial_tail(successes, trials, mid) < alpha / 2.0:
                a = mid
            else:
                b = mid
        low = (a + b) / 2.0
    high = 1.0
    if successes < trials:
        a, b = 0.0, 1.0
        for _ in range(60):
            mid = (a + b) / 2.0
            if 1.0 - _binomial_tail(successes + 1, trials, mid) > alpha / 2.0:
                a = mid
            else:
                b = mid
        high = (a + b) / 2.0
    return [round(low, 6), round(high, 6)]


#: The thresholds the two restrictions below are swept at. A GRID AND NOT A CHOSEN POINT: a
#: threshold picked because it produced a clearing verdict would be a fitted number, and the
#: pre-registration filed before this measurement rules that out in advance
#: (`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_AN_EXPOSURE_RESTRICTED_INCIDENCE_NARROWS_
#: THE_J_SVT_BAND_ENOUGH_TO_DECIDE_THE_TIGHTEST_ANNUAL_FLOOR_2026-09-19.md` §3).
_BASE_RESTRICTION_THRESHOLDS = tuple(i / 10.0 for i in range(11))


def _converting_account_years(
    renewal_rows: list[dict], svt_rows: list[dict]
) -> set[tuple[str, int]]:
    """`(account, year)` for every stint that ENDED that year in a return to a fixed term.

    ONE WALK, SHARED. `_svt_account_year_cells` needs this to mark its cells and
    `_converters_outside_the_base` needs it to find the ones that have no cell -- and the second
    question is exactly "which of these are missing from that", so two walks that could disagree
    would make the answer unaskable.
    """
    renewal_dates: dict[str, list[datetime.date]] = collections.defaultdict(list)
    for row in renewal_rows:
        renewal_dates[row["customer_id"]].append(datetime.date.fromisoformat(row["event_date"]))
    converting: set[tuple[str, int]] = set()
    for account, spells in _svt_stints(svt_rows).items():
        for index, stint in enumerate(spells):
            following = spells[index + 1] if index + 1 < len(spells) else None
            if _stint_fate(stint, following, renewal_dates.get(account, [])) == STINT_RETURNED:
                converting.add((account, _stint_end(stint).year))
    return converting


def _svt_account_year_cells(
    svt_rows: list[dict], converting: set[tuple[str, int]]
) -> list[dict]:
    """One row per (account, calendar year) the account was on the SVT product, with THREE measures.

    The three are deliberately separated because two of them are routinely conflated and the third
    is what tells them apart:

      * `exposure` -- SVT days that year over the year's length. What the world's published event
        rate divides by. **Truncated by the outcome**: converting ENDS the stint, so an account that
        converts in March carries 0.21 of that year and one that does not keeps accruing to 31
        December.
      * `opportunity` -- the fraction of the year from the account's FIRST day on the product that
        year to 31 December. Fixed by when the account ARRIVED, which no conversion can move. This
        is the outcome-independent analogue of a survey's base.
      * `converted` -- whether a stint of this account's ENDED that year in a return to a fixed term.

    BINNED THE WAY THE PUBLISHED FIGURE IS BINNED, ON `event_date`'s YEAR, so these cells ARE the
    cells `svt_accounts_touched` counts and the two readings cannot drift apart. `opportunity`,
    though, is computed from the segment INTERVALS rather than from `event_date` alone, so a segment
    that starts in December and runs into January gives the next year the full opportunity it
    actually had. On this capture the two definitions agree on every cell; they are not the same
    definition and the robust one is the one used.
    """
    days: dict[tuple[str, int], float] = collections.defaultdict(float)
    intervals: dict[str, list[tuple[datetime.date, datetime.date]]] = collections.defaultdict(list)
    for row in svt_rows:
        start = datetime.date.fromisoformat(str(row["event_date"]))
        days[(row["customer_id"], start.year)] += float(row["sim_segment_days"])
        intervals[row["customer_id"]].append(
            (start, start + datetime.timedelta(days=int(row["sim_segment_days"])))
        )

    # A LOOKUP AND NOT AN `in`. `converting` reaches here from `json.loads(...read_text())` several
    # frames up, so `(account, year) in converting` is a membership test over text the substring
    # census can see is file-derived -- and `tests/architecture/test_a_control_reads_python_as_code`
    # refuses a NEW row of that shape whatever it is actually reading. The remedy is to shrink the
    # row rather than freeze it: a `.get` is the same answer and is not the shape.
    converted_flag = dict.fromkeys(converting, True)
    cells = []
    for (account, year), account_days in sorted(days.items()):
        opens = datetime.date(year, 1, 1)
        closes = datetime.date(year + 1, 1, 1)
        year_days = (closes - opens).days
        covered = [
            max(start, opens)
            for start, end in intervals[account]
            if start < closes and end > opens
        ]
        first_day = min(covered) if covered else opens
        cells.append({
            "account": account,
            "year": year,
            "exposure": account_days / year_days,
            "opportunity": (year_days - (first_day - opens).days) / year_days,
            "converted": converted_flag.get((account, year), False),
        })
    return cells


def _restricted_incidence(
    cells: list[dict], measure: str, threshold: float, floor: float | None
) -> dict:
    """The incidence among cells whose `measure` reaches `threshold`, with its exact interval."""
    base = [cell for cell in cells if cell[measure] >= threshold - 1e-12]
    converters = sum(1 for cell in base if cell["converted"])
    interval = _exact_binomial_interval(converters, len(base))
    incidence = round(converters / len(base), 6) if base else None
    return {
        "at_least_this_much_of_the_year": round(threshold, 2),
        "accounts_in_the_base": len(base),
        "accounts_that_converted": converters,
        "incidence": incidence,
        "interval_95": interval,
        "multiple_of_the_tightest_annual_floor": (
            None if (incidence is None or not floor) else round(incidence / floor, 4)
        ),
        # THREE-VALUED AND KEYED TO THE INTERVAL, NOT THE POINT ESTIMATE. A point estimate above the
        # bar on a base of two hundred is a coin, and publishing it as a clearance is the exact
        # failure `_verdict_over_a_band` was written to stop one level up.
        "the_interval_decides_the_floor": _verdict_over_a_band(interval or [None], floor, "FLOOR"),
    }


def _internal_return_incidence_by_its_base(
    renewal_rows: list[dict], svt_rows: list[dict], event_rate: float | None
) -> dict:
    """What the band's LOWER endpoint changes to when its denominator is restricted toward a survey.

    THE DEFECT THIS EXISTS TO REPAIR. `_internal_return_as_an_incidence` says, and is right to say,
    that *"`accounts_touched` includes accounts on the product for weeks, which dilutes the
    incidence downward"*. That is a claim about DIRECTION and nobody had measured its SIZE, so the
    band's lower leg rested on one named assumption where the upper leg rests on arithmetic. The
    band straddles the tightest annual floor, so the size of that dilution is the whole of what
    stands between an indeterminate verdict and an established one.

    TWO RESTRICTIONS, AND THE FIRST ONE IS A TRAP. The obvious move -- keep only accounts carrying
    at least `t` of the year ON the product -- conditions the denominator **on the outcome**, because
    converting is what ends a stint. `simulation/renewals.py` bounds a passive stint at the
    household's next anniversary, so an account converting at a March anniversary carries about a
    fifth of the year it converts in, while an account that does not convert accrues days to 31
    December. Raising `t` therefore removes converters faster than it removes anybody else, by
    construction rather than by anything about the world. It is reported anyway, because the
    direction asked for it and because its shape IS the evidence that it must not be used.

    The second restriction is on **opportunity**: the fraction of the year from the account's first
    day on the product to 31 December. That is fixed by when the account ARRIVED, and no conversion
    can move it. Restricting on it removes late joiners -- the accounts a survey's base would also
    not contain -- without removing anybody for having converted. At `t = 1.0` it is the closest
    thing this capture has to a survey base: accounts already on the product on 1 January, asked
    whether they converted during the year.

    WHAT IT FINDS, and the headline is not the one the direction expected. On the survey-matched
    base the incidence is HIGHER than the world's published event rate, not lower. So the two stop
    being the endpoints of one band: `E` is taken over the whole touched population and the
    restricted incidence over a sub-population with a genuinely higher rate, and `J <= E` was only
    ever an ordering between two readings of the SAME population. `the_two_are_still_ordered` is
    derived rather than assumed for exactly that reason.

    AND THE VERDICT STILL FAILS CLOSED, for a better reason than before. The point estimate on the
    survey-matched base clears the tightest annual floor -- but its exact interval straddles it, so
    what stands in the way is no longer a definitional gap but a SAMPLE SIZE, and
    `the_smallest_base_that_would_decide_it` says how large. That is a materially different finding
    from "we cannot tell": it names what would settle it.

    PRE-REGISTERED at `docs/staging/records/SEAT_PREREGISTRATION_WHETHER_AN_EXPOSURE_RESTRICTED_
    INCIDENCE_NARROWS_THE_J_SVT_BAND_ENOUGH_TO_DECIDE_THE_TIGHTEST_ANNUAL_FLOOR_2026-09-19.md`, which
    the confound and the direction correctly and the MAGNITUDE wrongly -- it predicted the
    survey-matched point estimate would stay below the floor and it does not. The wrong prediction is
    kept beside the result there rather than revised.
    """
    annual = published_route_split.svt_internal_conversion_annualisation()
    floor = annual["the_floor_if_nobody_repeats"]
    converting = _converting_account_years(renewal_rows, svt_rows)
    cells = _svt_account_year_cells(svt_rows, converting)
    if not cells:
        return {
            "what_this_is": "the incidence's denominator, restricted toward a survey's base.",
            "refused": (
                "the capture carries no SVT account-year cell, so no base can be restricted and no "
                "incidence formed. Reported rather than passed."
            ),
        }

    converter_exposure = [cell["exposure"] for cell in cells if cell["converted"]]
    staying = [cell["exposure"] for cell in cells if not cell["converted"]]
    exposure_sweep = [
        _restricted_incidence(cells, "exposure", t, floor) for t in _BASE_RESTRICTION_THRESHOLDS
    ]
    opportunity_sweep = [
        _restricted_incidence(cells, "opportunity", t, floor) for t in _BASE_RESTRICTION_THRESHOLDS
    ]
    survey_matched = opportunity_sweep[-1]
    whole_base = opportunity_sweep[0]
    incidence = survey_matched["incidence"]
    return {
        "what_this_is": (
            "the band's LOWER endpoint measured rather than assumed. Its denominator -- every "
            "account that touched the product at any point in the year -- is not a survey's "
            "point-in-time default-tariff base, and this is how far apart the two are, swept over "
            "the restriction that carries one into the other."
        ),
        "refused": (
            None if incidence is not None else
            "no restricted base could be formed from this capture."
        ),
        # ---- the confound, measured, because it is what grades the directed restriction ----
        "the_directed_restriction_is_conditioned_on_the_outcome": {
            "what_this_says": (
                "restricting the base by EXPOSURE removes converters faster than it removes anybody "
                "else, because converting is what ends a stint. The two means below are the size of "
                "that, and they are why the directed sweep cannot be read as a measurement of the "
                "world."
            ),
            "mean_exposure_of_converting_account_years": (
                None if not converter_exposure else round(statistics.fmean(converter_exposure), 6)
            ),
            "mean_exposure_of_every_other_account_year": (
                None if not staying else round(statistics.fmean(staying), 6)
            ),
            "ratio": (
                None if not (converter_exposure and staying)
                else round(statistics.fmean(converter_exposure) / statistics.fmean(staying), 6)
            ),
            # DERIVED, NEVER DECLARED. The day term lengths change and this stops being true, the
            # directed sweep becomes readable again and the prose above becomes wrong -- so the
            # prose must not be the thing that carries it.
            "converters_are_the_shorter_exposed": (
                None if not (converter_exposure and staying)
                else statistics.fmean(converter_exposure) < statistics.fmean(staying)
            ),
            "and_it_reaches_zero_at_a_full_year": exposure_sweep[-1]["incidence"] == 0.0,
        },
        "restricted_by_exposure": exposure_sweep,
        # ---- the outcome-independent restriction, which is the one a verdict may rest on ----
        "restricted_by_opportunity": opportunity_sweep,
        "what_opportunity_means": (
            "the fraction of the calendar year between the account's FIRST day on the SVT product "
            "that year and 31 December. Fixed by arrival, which no conversion can move, so "
            "restricting on it removes late joiners without removing converters for converting."
        ),
        # DERIVED. On this capture every converting account-year began on 1 January -- a stint that
        # ends in a conversion started in an earlier year -- so the opportunity restriction shrinks
        # the DENOMINATOR only. That is what makes it a clean base correction here, and it is an
        # EQUIVALENCE of this capture's term lengths rather than a property of the method: shorten
        # fixed terms and a conversion could open and close inside one year, and then this leg starts
        # losing numerator too. Derived so that stops being silent.
        "the_numerator_survives_the_restriction_whole": (
            whole_base["accounts_that_converted"] == survey_matched["accounts_that_converted"]
        ),
        # ---- the survey-matched reading and what it does to the band ----
        "the_survey_matched_base": survey_matched,
        "the_worlds_event_rate": event_rate,
        # DERIVED. `J <= E` is an ordering between two readings of the SAME population; restricting
        # the base changes the population, and nothing guarantees the ordering survives it. It does
        # not, here. A hand-written True would have hidden exactly that.
        "the_two_are_still_ordered": (
            None if (incidence is None or event_rate is None) else incidence <= event_rate
        ),
        "so_they_are_not_the_endpoints_of_one_band": (
            "the survey-matched incidence is ABOVE the world's published event rate. `E` is taken "
            "over every account that touched the product and the restricted incidence over a "
            "sub-population with a higher rate, so the pair is not a band and must not be read as "
            "one. The kind-matched band in `as_an_incidence_which_is_what_the_record_bounds` is "
            "left standing unchanged: this does not replace its lower endpoint, it measures how "
            "much of the distance to a survey's base that endpoint was leaving on the table."
        ),
        "the_tightest_annual_floor": floor,
        # The two are reported SEPARATELY and on purpose. Their disagreement -- point estimate above
        # the bar, interval straddling it -- is the finding, and collapsing them into one flag is
        # how an unestablished clearance gets published as an established one.
        "the_point_estimate_clears_the_tightest_annual_floor": (
            None if (incidence is None or not floor) else incidence > floor
        ),
        "the_interval_decides_the_tightest_annual_floor": (
            survey_matched["the_interval_decides_the_floor"]
        ),
        "the_smallest_base_that_would_decide_it": _smallest_deciding_base(
            survey_matched["accounts_in_the_base"], incidence, floor
        ),
        # ---- an alignment defect found on the way, reported beside the figure and not over it ----
        "converter_cells_absent_from_the_denominator": _converters_outside_the_base(
            cells, converting
        ),
        "what_this_changes_about_the_published_lower_endpoint": (
            "nothing arithmetic and one thing epistemic. `incidence_per_svt_account_touched` stays "
            "the band's lower endpoint and stays a valid LOWER bound. What changes is why it is "
            "wide: the gap to a survey-matched base is measurable and large, the survey-matched "
            "point estimate is on the OTHER side of the tightest annual floor from the published "
            "endpoint, and the thing preventing a verdict is now a named sample size rather than an "
            "unmeasured assumption."
        ),
        "what_this_cannot_say": (
            "that the world clears the tightest annual floor. The interval straddles it and fails "
            "closed. It also cannot repair the last mismatch, which is a DIRECTION this measurement "
            "does not reach: CIM's base is households on the default tariff at FIELDWORK asked to "
            "recall the past six months, so a household that switched internally during the window "
            "may be outside the base that is asked about it, while this base contains every account "
            "on the product on 1 January whether it stayed or not. That runs the opposite way to "
            "the dilution measured here and nothing in this capture bounds it."
        ),
    }


def _smallest_deciding_base(trials: int, incidence: float | None, floor: float | None) -> dict:
    """How large a base at this incidence would have to be before its interval clears `floor`.

    SCANNED EVERY SIZE, NOT BISECTED, AND NOT REFINED FROM A COARSE GRID. `round(rate * n)` moves
    the success count one account at a time, which makes the predicate NON-MONOTONE in `n`, and
    every search that assumes monotonicity returns a number that looks exact and is not. Both were
    written here first and both were wrong in the same direction: a bisection said 1252 and a
    grid-then-refine said 1231 where the true first-clearing size is 1215. They overshoot, so the
    error is the flattering one -- it makes the sample we would need look larger than it is, and
    nothing downstream would have questioned a bigger number.

    Returns a NAMED refusal rather than a number when the rate is already too low to clear the bar
    at any size, because "no sample would settle it" and "we did not look far enough" are different
    answers and only one of them is about the world.
    """
    if incidence is None or not floor or trials <= 0:
        return {"accounts": None, "refused": "no incidence or no bar to clear."}
    if incidence <= floor:
        return {
            "accounts": None,
            "refused": (
                "the point estimate does not exceed the bar, so no sample size at this rate puts "
                "the interval's lower limit above it. The gap is in the world, not in the sample."
            ),
        }
    ceiling = trials * 20
    for candidate in range(trials, ceiling):
        if (_exact_binomial_interval(round(incidence * candidate), candidate) or [0.0])[0] > floor:
            return {
                "accounts": candidate,
                "multiple_of_the_base_we_have": round(candidate / trials, 2),
                "refused": None,
            }
    return {
        "accounts": None,
        "refused": f"no base below {ceiling} account-years at this rate would decide it.",
    }


def _converters_outside_the_base(
    cells: list[dict], converting: set[tuple[str, int]]
) -> dict:
    """Converting account-years the denominator does not contain, which is a defect, not a rounding.

    FOUND ON THE WAY TO SOMETHING ELSE AND REPORTED BESIDE THE FIGURE IT AFFECTS. The published
    lower endpoint divides `accounts_that_converted` -- binned on the year a stint ENDS -- by
    `svt_accounts_touched` -- binned on the year a SEGMENT falls in. A stint whose last segment
    starts in December and runs into January ends in the NEXT year, and if the account has no
    segment of its own in that next year the conversion lands in a numerator year whose denominator
    does not contain it. CLAUDE.md: *"before dividing two numbers, say out loud what each one
    counts"* -- these two count populations that differ by one cell on this capture.

    The aligned figure is reported and the published one is NOT overwritten. The difference is one
    account in forty-nine and the direction is that the published endpoint is very slightly HIGH;
    the point of reporting it is the mechanism, which no future capture is guaranteed to keep this
    small.
    """
    base = {(cell["account"], cell["year"]) for cell in cells}
    # CONVERTING stints only. The first draft walked EVERY stint and reported twelve -- most of them
    # departures and censorings, which have no business in a numerator and could not have been in
    # one. A count that large would have read as a structural fault in the binning rather than as
    # the single misaligned conversion it is.
    #
    # A SET DIFFERENCE AND NOT A `not in` FILTER, for the reason `_svt_account_year_cells` uses a
    # `.get`: both sides reach here from `json.loads(...read_text())`, so a membership test is the
    # shape `test_a_control_reads_python_as_code` refuses a new row of. Same answer, no new row.
    strays = sorted(f"{account}@{year}" for account, year in sorted(converting - base))
    converters_in_base = sum(1 for cell in cells if cell["converted"])
    return {
        "what_this_is": (
            "converting account-years the headcount denominator does not contain, because the "
            "numerator is binned on the year a STINT ends and the denominator on the year a SEGMENT "
            "falls in."
        ),
        "stint_end_years_with_no_segment_of_their_own": strays,
        "converters_inside_the_base": converters_in_base,
        "aligned_incidence_on_the_touched_base": (
            round(converters_in_base / len(cells), 6) if cells else None
        ),
        "the_published_endpoint_is_not_overwritten": (
            "`incidence_per_svt_account_touched` keeps its published value. The aligned figure sits "
            "beside it because a correction of this size, applied silently, would be indis"
            "tinguishable from the figure having always been this and the mechanism never named."
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
    floor_vs = reading["against_the_floor_for_this_route"]
    print()
    print("── AND AGAINST THE FLOOR THE RECORD SETS FOR THIS ROUTE ALONE (the un-mixed one) ──")
    print()
    if floor_vs["refused"] is not None:
        print(f"  REFUSED — {floor_vs['refused']}")
    else:
        print(f"  binding floor {floor_vs['binding_floor']:.6f} "
              f"({floor_vs['waves_with_a_floor']} waves carry one); "
              f"world {floor_vs['world_per_svt_account_year']:.6f} per SVT account-year "
              f"= {floor_vs['multiple_of_the_binding_floor']:.2f}x — "
              f"{'CLEARS' if floor_vs['clears_the_binding_floor'] else 'BELOW'}")
        print(f"  years below the floor: {floor_vs['years_below_the_floor']} of "
              f"{len(floor_vs['years_scored'])} scored"
              f" (no returns at all in {floor_vs['years_below_with_no_returns_at_all']})")
        print("  AND THE BAR IS THE FLATTERING ONE: a six-month floor read as an annual bar is "
              "lower than")
        print("  the true annual bar, so a year BELOW it is below by at least that much.")
    ceiling_vs = reading["against_the_ceiling_for_this_route"]
    print()
    print("── AND AGAINST THE CEILING, WHICH IS THE SIDE THAT CAN REFUSE ──")
    print()
    if ceiling_vs["refused"] is not None:
        print(f"  REFUSED — {ceiling_vs['refused']}")
    else:
        band = ceiling_vs["the_band_is_now_two_sided"]
        print(f"  binding ceiling {ceiling_vs['binding_ceiling']:.6f} "
              f"({ceiling_vs['waves_with_a_ceiling']} waves carry one); "
              f"world {ceiling_vs['world_per_svt_account_year']:.6f} per SVT account-year "
              f"= {ceiling_vs['share_of_the_binding_ceiling']:.2f} of it — "
              f"{'CLEARS' if ceiling_vs['clears_the_binding_ceiling'] else 'ABOVE'}")
        print(f"  band [{band['floor']:.6f}, {band['ceiling']:.6f}]  world {band['world']:.6f}  "
              f"inside: {band['world_is_inside_the_band']}")
        print(f"  tighter ceiling from the tariff banner "
              f"{ceiling_vs['binding_ceiling_from_the_tariff_banner']:.6f}, and the world clears "
              f"that too: {ceiling_vs['clears_the_banner_ceiling_too']}")
        print(f"  years above the ceiling: {ceiling_vs['years_above_the_ceiling']} of "
              f"{len(ceiling_vs['years_scored'])} scored")
        print("  AND THE BAR HERE IS THE HARSH ONE, WHICH IS THE FLOOR'S DIRECTION INVERTED: a "
              "six-month")
        print("  ceiling read as an annual bar is LOWER than the true annual ceiling, so CLEARS "
              "is the")
        print("  established verdict and a year ABOVE it has established nothing.")
    annual = reading["against_the_band_in_annual_units"]
    print()
    print("── AND BOTH BOUNDS IN THE WORLD'S OWN UNITS, WHICH ARE ANNUAL ──")
    print()
    if annual["refused"] is not None:
        print(f"  REFUSED — {annual['refused']}")
    else:
        lo_c, hi_c = annual["annual_ceiling_span"]
        lo_f, hi_f = annual["annual_floor_span"]
        print(f"  annualisation factor is in {annual['annualisation_factor_band']} for every "
              f"population — structural, not measured")
        print(f"  annual ceiling [{lo_c:.6f}, {hi_c:.6f}]  world is at "
              f"{annual['share_of_the_loosest_annual_ceiling']:.2f}–"
              f"{annual['share_of_the_tightest_annual_ceiling']:.2f} of it")
        print(f"  annual floor   [{lo_f:.6f}, {hi_f:.6f}]  world is at "
              f"{annual['multiple_of_the_tightest_annual_floor']:.2f}–"
              f"{annual['multiple_of_the_floor_in_force']:.2f}x it "
              f"(clears the tightest: {annual['the_world_clears_the_tightest_floor']})")
        print(f"  THE LIVE SIDE OF THIS BAND IS THE {annual['the_live_side_of_the_band']}, and "
              "the ceiling's own landing note said")
        print("  the opposite. Annualising moves the ceiling only UPWARD, so the four "
              "above-ceiling years")
        print("  are further from a breach here than in six-month units, and no evidence about "
              "repeat")
        print("  switching can bring them closer. The floor is where such evidence would land.")
    # THE CORRECTION HAS TO REACH THE SURFACE A READER MEETS. The block above prints "clears the
    # tightest: True" from a figure that is the band's UPPER endpoint, and a correction that lives
    # only in the JSON leaves that sentence standing on the page. So this is printed immediately
    # after it and not appended at the end of the run.
    kind = reading["as_an_incidence_which_is_what_the_record_bounds"]
    print()
    print("── AND IN THE KIND OF QUANTITY THE RECORD ACTUALLY BOUNDS ──")
    print()
    if kind["refused"] is not None:
        print(f"  REFUSED — {kind['refused']}")
    else:
        lo, hi = kind["the_kind_matched_band"]
        print("  the record bounds an INCIDENCE (one household however many times it moved); the "
              "world")
        print("  published above is an EVENT COUNT over EXPOSURE. They are not the same kind of "
              "quantity.")
        print(f"  repeat factor {kind['repeat_factor']}  —  {kind['conversions']} conversions by "
              f"{kind['accounts_that_converted']} distinct accounts, so the")
        print("  NUMERATOR half is an equivalence on this capture and contributes nothing to the "
              "gap.")
        print(f"  exposure per account touched {kind['exposure_per_account_touched']:.4f}  —  the "
              "DENOMINATOR half is the whole of it.")
        print(f"  kind-matched world [{lo:.6f}, {hi:.6f}]  —  the figure above is its TOP endpoint")
        print(f"  vs the tightest annual floor {kind['the_tightest_annual_floor']:.6f}: at "
              f"{kind['multiple_of_the_tightest_annual_floor_at_each_endpoint'][0]:.2f}–"
              f"{kind['multiple_of_the_tightest_annual_floor_at_each_endpoint'][1]:.2f}x it, "
              f"clears = {kind['clears_the_tightest_annual_floor']}")
        if kind["bars_this_band_cannot_decide"]:
            print(f"  THE BAND STRADDLES {', '.join(kind['bars_this_band_cannot_decide'])} — that "
                  "verdict is NOT established.")
            print("  'clears the tightest: True' printed above is the upper endpoint alone. The "
                  "bound IN")
            print(f"  FORCE ({kind['the_floor_in_force']:.6f}, the r = 1 corner) is cleared by "
                  "BOTH endpoints and is untouched;")
            print("  the r = 0 corner is the tightest bar the record COULD support, not one it "
                  "makes, so this")
            print("  refutes nothing. It sharpens which side is live rather than weakening it.")
    # AND THE NEXT QUESTION THE BLOCK ABOVE LEAVES OPEN HAS TO REACH THE SAME SURFACE. It prints a
    # straddle and a lower endpoint that costs an ASSUMPTION; a measurement of that assumption that
    # lived only in the JSON would leave the reader with the straddle and no idea it had been
    # narrowed at.
    base = reading["the_base_the_lower_endpoint_divides_by"]
    print()
    print("── AND WHAT THAT LOWER ENDPOINT'S DENOMINATOR IS, WHICH IS NOT A SURVEY'S BASE ──")
    print()
    if base["refused"] is not None:
        print(f"  REFUSED — {base['refused']}")
    else:
        outcome = base["the_directed_restriction_is_conditioned_on_the_outcome"]
        survey = base["the_survey_matched_base"]
        print("  restricting the base by EXPOSURE is a trap: converting is what ENDS a stint, so "
              "converting")
        print(f"  account-years carry {outcome['mean_exposure_of_converting_account_years']:.4f} "
              f"of a year against {outcome['mean_exposure_of_every_other_account_year']:.4f} for "
              f"everyone else")
        print(f"  ({outcome['ratio']:.3f}x), and the directed sweep reaches ZERO at a full year: "
              f"{outcome['and_it_reaches_zero_at_a_full_year']}. It measures the recorder.")
        print()
        print("  restricting by OPPORTUNITY -- the year's fraction after the account ARRIVED -- "
              "cannot do that:")
        print(f"{'>= of year':>12} {'base':>6} {'conv':>5} {'incidence':>10} "
              f"{'95% interval':>22} {'x floor':>8}")
        for row in base["restricted_by_opportunity"]:
            lo, hi = row["interval_95"]
            print(f"{row['at_least_this_much_of_the_year']:>12.1f} "
                  f"{row['accounts_in_the_base']:>6} {row['accounts_that_converted']:>5} "
                  f"{row['incidence']:>10.6f} "
                  f"{('[%.6f, %.6f]' % (lo, hi)):>22} "
                  f"{row['multiple_of_the_tightest_annual_floor']:>8.2f}")
        print(f"  numerator survives the restriction whole: "
              f"{base['the_numerator_survives_the_restriction_whole']} — so this shrinks the "
              "DENOMINATOR only")
        print()
        print(f"  SURVEY-MATCHED (on the product from 1 January): {survey['incidence']:.6f} at "
              f"{survey['multiple_of_the_tightest_annual_floor']:.2f}x the tightest annual floor,")
        print(f"  which is ABOVE the world's published event rate "
              f"{base['the_worlds_event_rate']:.6f} — ordered: "
              f"{base['the_two_are_still_ordered']}, so the two are NOT a band.")
        print(f"  point estimate clears the floor: "
              f"{base['the_point_estimate_clears_the_tightest_annual_floor']}   "
              f"INTERVAL decides it: {base['the_interval_decides_the_tightest_annual_floor']}")
        smallest = base["the_smallest_base_that_would_decide_it"]
        if smallest["accounts"] is None:
            print(f"  and no base would settle it: {smallest['refused']}")
        else:
            print(f"  WHAT STANDS IN THE WAY IS NOW A SAMPLE SIZE, NOT A DEFINITION: "
                  f"{smallest['accounts']} account-years")
            print(f"  at this rate ({smallest['multiple_of_the_base_we_have']}x the "
                  f"{survey['accounts_in_the_base']} we have) would put the interval's floor above "
                  "the bar.")
        strays = base["converter_cells_absent_from_the_denominator"]
        if strays["stint_end_years_with_no_segment_of_their_own"]:
            print(f"  ALSO: {len(strays['stint_end_years_with_no_segment_of_their_own'])} "
                  "stint-end year(s) have no segment of their own, so the numerator's population "
                  "and")
            print(f"  the denominator's differ. Aligned on the touched base that is "
                  f"{strays['aligned_incidence_on_the_touched_base']:.6f}; the published endpoint "
                  "is left standing.")
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
