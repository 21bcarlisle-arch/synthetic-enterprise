"""R3: THE CARBON SCORE CEILING — the most a £/tCO2e score could be worth if it worked perfectly.

REUSE: tools/r3_carbon_score_ceiling.py
CLASS: CUSTOM
INDEX: searched "ceiling", "bound", "carbon", "abatement", "tCO2e", "timing", "shift". Six ceiling
       instruments exist and NONE touches R3: five are EP13's dispatch bounds
       (`ep13_input_ceiling`, `ep13_ccgt_level_ceiling`, `ep13_ccgt_swap_ceiling`,
       `ep13_peer_bound`, `settlement_ceiling_probe`) and one is R1's
       (`r1_inference_ceiling`). This is the SAME MOVE ON A DIFFERENT SUBJECT as R1's: the
       three-rung shape (baseline / ceiling / null), the fail-closed population floors and the
       "state whether it is a CEILING or a FLOOR" discipline are taken from it deliberately.
       `company/carbon/half_hourly_footprint.py` is the nearest organ on the CARBON side and
       answers a different question — what the book EMITS, which is a measurement; this asks what
       it could ABATE, which is a counterfactual. `sim/neso_carbon_intensity.py::forecast_skill`
       already measures how much of a day's achievable shift a real forecast captures, so the
       forecast rung READS that rather than re-deriving it.

WHY THIS EXISTS
---------------
Director canon, 2026-09-04 (`DIRECTOR_CANON_RERANKING_THE_ARC`), R3 — The score:

    "£ per tonne of CO2e abated still reads NOT YET MEASURED. It is the number the whole project
     exists to produce, and it is also the only measure that would let the company optimise for
     something other than margin."

And item 5 of the same document: *"The ceiling-before-programme discipline from EP13 applied to
R1-R4 before building."* EP13 ran TWELVE passes without moving off L2; the ceiling arrived at pass
seven and retired five candidate programmes outright. A49 exists so R3 does not repeat that.

A score is worth nothing unless there is abatement to score, so the ceiling question is not "how
good could the score be" but **how much carbon this book could abate at all**.

WHAT THIS BOUNDS, AND WHAT IT DELIBERATELY DOES NOT
----------------------------------------------------
The electricity carbon SHAPE offers exactly one lever: **timing**. The advisor scope brief
(`docs/domain_artefact_library/scope_briefs/ADVISOR_SCOPE_BRIEF_CARBON_2026-08-04.md`, §B) is
explicit and it is the practitioner side of the knowledge layer, not a modelling choice:

    "Gas ... a near-constant factor per kWh burned. No time-shifting benefit exists, because gas
     emits when burned. The only lever is using less. ... Time-shifting only pays in electricity."

So this instrument bounds the TIMING lever on ELECTRICITY, and it says so on its own surface.
Reduction and physical measures are R4's subject and are listed in `not_bounded_by_this` rather
than left for a reader to infer. A ceiling that quietly implied it covered them would be the exact
conflation EP13's tenth pass made.

THE RUNGS — one book, one method, scored the same way
------------------------------------------------------
    baseline          no score at all. The book's emissions on its own timing. Abatement is zero
                      BY CONSTRUCTION, carried so the other rungs have a floor to beat.
    hindsight_ceiling every shiftable kWh drawn in the cleanest window of its own day, with
                      PERFECT FOREKNOWLEDGE of the half-hourly shape. This is the number R3's
                      claim is about.
    forecast_ceiling  the same reallocation acting on the PUBLISHED FORECAST instead of hindsight,
                      handicapped by the feed's own MEASURED `capture_mean`. The scope brief's
                      rule: "Shifting advice must be judged on forecast; achieved abatement on
                      outturn." A household cannot act on hindsight.
    null_ceiling      the same optimiser picking its window from a SHUFFLED day and being scored on
                      the REAL one. The rung that makes the others falsifiable.

AND THE NULL HAS TO DESTROY THE SIGNAL WITHOUT DESTROYING THE FREEDOM. The obvious null — shuffle
the day and re-run the optimiser — measures NOTHING: a shuffle is a permutation, the sorted values
are unchanged, and the cleanest window of a shuffled day is the cleanest window of the day. It
returns the ceiling exactly and reads like a spectacular confirmation. The null that works picks
BY the shuffled shape and scores BY the real one, which is the same construction
`sim/neso_carbon_intensity.py::_capture_fractions` uses for forecast skill and is not a
coincidence: a forecast with no skill IS a shuffle.

THE PARAMETER NOBODY HAS ESTABLISHED, and why the headline does not need it. Abatement is linear in
the SHIFTABLE SHARE of household load, and no published source in this repository establishes one —
grep over `docs/market_research/`, `docs/domain_artefact_library/` and `docs/institutional/`
returns nothing. Knowledge-first is a rule: a number invented for that slot would be load-bearing
within a week and unattributable within a month. So the headline is reported at **share = 1.0**,
where every kWh moves. That is physically absurd as a programme and it is exactly what a ceiling
is: unreachable by construction, so nothing buildable can beat it. The linear curve across shares
is published beside it and the missing parameter is named in `named_gaps`.

CEILING OR FLOOR — the declaration EP13 paid two passes to learn it needed
---------------------------------------------------------------------------
`hindsight_ceiling` is a **true CEILING**. Perfect foreknowledge of the half-hourly shape is
exactly the quantity a real forecast approximates, and perfect compliance is exactly what advice
approximates, so no buildable method beats it. A negative or at-the-null reading therefore RETIRES
the time-shifting candidate outright.

It is a ceiling OF THE TIMING LEVER. A negative here retires nothing about reduction, measures or
gas, and `bound_scope` says so in the payload so a downstream reader cannot widen it silently.

TWO ERRORS IN OPPOSITE DIRECTIONS, both measured and neither hidden. The reconstructed shape's
WITHIN-DAY swing is measured too large — 1.35x to 1.54x against the published NESO series, per year
in the feed's own `versus_published` — so a ceiling computed on it OVERSTATES. Averaging days into
a typical day FLATTENS within-day spread, so the typical-day rung UNDERSTATES. Both are computed,
both are published, and the corrected reading divides the real-day figure by the feed's own
per-year factor rather than by a number chosen here.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from company.carbon.half_hourly_footprint import INTENSITY_FEED, load_shape  # noqa: E402
from company.regulatory.carbon_emissions import (  # noqa: E402
    grid_intensity_g_co2e_per_kwh,
    grid_intensity_is_extrapolated,
)

OUT_PATH = PROJECT / "docs" / "observability" / "r3_carbon_score_ceiling.json"

#: What a shifted tonne is worth, GBP per tCO2e. NOT PICKED: DESNZ, "Traded carbon values used for
#: modelling purposes, 2025", Table 1, Market Traded Carbon Values central case for 2025 —
#: £44/tCO2e in real 2025 GBP. Read into this repository on 2026-07-25 and recorded in
#: `docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md`.
#: THE TRADED SERIES IS THE RIGHT ONE HERE and that is a domain judgement, not a convenience: GB
#: grid generation sits inside the UK ETS, so an abated grid tonne is a traded tonne. The
#: NON-traded value (~£80-90/tCO2e) would roughly double every money figure below and this
#: repository holds it only as an ASSERTED anchor in
#: `docs/market_research/population_coverage/value_outcome_model.json`, whose own note calls it
#: asserted. An asserted number may not be the comparator in a ceiling; it is named in
#: `named_gaps` instead.
TRADED_CARBON_VALUE_GBP_PER_TONNE = 44.0

#: Fewest whole days the intensity shape must yield before this instrument reports anything.
#: FAIL CLOSED. A ceiling computed over three days is three days wearing a ceiling's name, and the
#: neighbouring `forecast_skill` refuses below its own day floor for the same reason.
MIN_DAYS = 10
#: Fewest half hours a day must carry to be a day at all. Taken from
#: `sim/neso_carbon_intensity.py`, whose docstring gives the reason this instrument would otherwise
#: have had to learn: the cleanest six half hours of a truncated day are scored against a mean that
#: never saw the missing ones, so a short day inflates the achievable saving.
MIN_PERIODS_PER_DAY = 40
#: Fewest households carrying an electricity EAC before a book-level figure is reported. FAIL
#: CLOSED, and taken from R1's own hard-won floor: a linked worktree carries no gitignored run
#: outputs, and an instrument that returns "0 households, ceiling 0.0" reads exactly like
#: "measured the book, found nothing" when it means "measured nothing".
MIN_HOUSEHOLDS = 20
#: Draws of the skill-free optimiser that make the noise floor. The floor reported is the MAX over
#: draws, not the mean, because the question a null answers is how high chance REACHES.
NULL_DRAWS = 200
#: Shiftable shares the curve is printed at. Not a belief about any of them — the point of printing
#: the curve is that the instrument does not hold one.
SHARE_CURVE = (0.05, 0.10, 0.20, 0.50, 1.00)

#: A49's own requirement, and VALUES rather than prose in a docstring so a control over them reads
#: what the payload carries instead of reading the source text. A test that greps a docstring is
#: satisfied by a comment and says nothing about what the instrument publishes.
BOUND_KIND = "CEILING"
BOUND_KIND_REASON = (
    "TRUE CEILING. Perfect foreknowledge of the half-hourly intensity shape is exactly the "
    "quantity a real forecast approximates, and perfect compliance is exactly what advice "
    "approximates, so no buildable method beats `hindsight_ceiling`. A reading at or below the "
    "null therefore RETIRES the time-shifting candidate outright, which is what a floor could "
    "never do."
)
BOUND_SCOPE = (
    "The TIMING lever on ELECTRICITY only. A negative here retires nothing about consumption "
    "reduction, physical measures or gas."
)
#: Every lever this ceiling does NOT bound, named so a reader cannot widen the figure silently. A
#: timing ceiling read as a bound on the whole carbon programme would retire the mission on the
#: strength of a lever that was never the whole of it.
NOT_BOUNDED_BY_THIS = (
    "reduction -- using less. Abates both kWh and carbon and is R4's subject.",
    "gas -- a near-constant factor per kWh burned. It emits when burned, so no timing benefit "
    "exists and none is claimed (scope brief §B).",
    "physical measures -- efficiency, solar, heat pumps. R4's subject, and bounded there.",
    "tariff switching -- moves money, never carbon. The director's standing rule: savings count "
    "only from reduced or time-shifted usage, never from discounting.",
    "embodied carbon in any measure or asset fitted.",
    "rebound -- part of a saving returns as extra comfort. It cannot reduce a TIMING ceiling (the "
    "kWh is unchanged), which is why it is out of scope here and in scope for every reduction "
    "figure R4 reports.",
)


class CeilingUnavailable(Exception):
    """This instrument could not measure. Never a silent zero.

    Zero abatable carbon is a programme-retiring result and an unavailable instrument must not be
    able to report one (R15 fail-silent). Every path that cannot produce a number raises.
    """


# --------------------------------------------------------------------------------------------
# The world side: what the grid's shape makes available to a household that can move load.
# --------------------------------------------------------------------------------------------

def whole_days(shape: dict[tuple[str, int], float]) -> dict[str, list[float]]:
    """date -> its half-hourly intensity multipliers, ordered by settlement period.

    Short days are dropped rather than padded, for `MIN_PERIODS_PER_DAY`'s reason.
    """
    by_date: dict[str, dict[int, float]] = {}
    for (date_str, period), multiplier in shape.items():
        by_date.setdefault(date_str, {})[int(period)] = float(multiplier)
    return {
        date_str: [periods[p] for p in sorted(periods)]
        for date_str, periods in by_date.items()
        if len(periods) >= MIN_PERIODS_PER_DAY
    }


def shift_window(feed: dict) -> int:
    """How many half hours a household's shifted load lands in.

    READ FROM THE FEED, never chosen here, and the reason is that this number has to MATCH the one
    `capture_mean` was measured at. `capture_mean` is the fraction of a day's achievable saving
    captured by acting on the forecast FOR A GIVEN WINDOW; applying a capture measured at six half
    hours to a saving computed at one would be two different quantities multiplied together, which
    is this project's most expensive recurring shape.
    """
    skill = feed.get("published_forecast_skill") or {}
    window = skill.get("shift_window_half_hours")
    if not isinstance(window, int) or window <= 0:
        raise CeilingUnavailable(
            "the intensity feed carries no `shift_window_half_hours`, so there is no window at "
            "which `capture_mean` was measured and no honest way to apply it"
        )
    return window


def achievable_saving_per_kwh(day: list[float], window: int) -> float:
    """Multiplier units of intensity avoided per kWh moved into this day's cleanest window.

    The day's mean minus the mean of its `window` cleanest half hours — DELIBERATELY IDENTICAL to
    `_capture_fractions`'s `achievable`, because `capture_mean` is a fraction OF THIS QUANTITY and
    the two must be the same thing or the forecast rung is a category error.

    UNWEIGHTED mean over the day's half hours, matching that function. It is also the right mean
    for the counterfactual: the load being moved is being taken from a day, not from the demand
    profile of the nation.
    """
    if len(day) < MIN_PERIODS_PER_DAY:
        raise CeilingUnavailable(f"a day of {len(day)} half hours is not a day")
    if window >= len(day):
        raise CeilingUnavailable(
            f"a shift window of {window} covers the whole {len(day)}-half-hour day, so there is "
            "nothing to move load away from and the saving is zero by construction"
        )
    mean = statistics.fmean(day)
    cleanest = statistics.fmean(sorted(day)[:window])
    return mean - cleanest


def skill_free_saving_per_kwh(day: list[float], window: int, rng: random.Random) -> float:
    """The same saving, with the window picked by a SHUFFLED day and scored on the real one.

    THIS IS THE NULL, and the obvious alternative is worthless. Shuffling the day and re-running
    the optimiser returns `achievable_saving_per_kwh` EXACTLY — a permutation does not change a
    sorted list — so it would report the ceiling as its own noise floor and read as a spectacular
    confirmation. Picking by the shuffle and scoring by the truth is what a forecast with no skill
    actually is, and it is the construction `_capture_fractions` uses.
    """
    order = list(range(len(day)))
    rng.shuffle(order)
    chosen = order[:window]
    return statistics.fmean(day) - statistics.fmean([day[i] for i in chosen])


def within_day_overstatement(feed: dict, years: set[str]) -> dict:
    """How much the reconstructed shape's within-day swing exceeds the published series'.

    MEASURED IN THE FEED, per year, and read from it rather than restated here — a restated
    correction factor is a number that goes stale beside the measurement that produced it. Years
    the feed has no comparison for are NAMED, not silently dropped: the correction then rests on
    the years it has, and a reader can see which.
    """
    rows = ((feed.get("versus_published") or {}).get("by_year") or {})
    factors: dict[str, float] = {}
    for year in sorted(years):
        row = rows.get(year)
        got = row.get("within_day_swing_overstated_by") if isinstance(row, dict) else None
        if isinstance(got, (int, float)) and got > 0:
            factors[year] = float(got)
    uncovered = sorted(years - set(factors))
    if not factors:
        return {
            "available": False,
            "why": "the feed compares no year this book's days fall in",
            "years_uncovered": uncovered,
        }
    return {
        "available": True,
        "by_year": factors,
        "mean": round(statistics.fmean(factors.values()), 4),
        "years_uncovered": uncovered,
        "what_it_means": (
            "The reconstructed shape swings more WITHIN a day than the published NESO series "
            "does, so a timing benefit computed on it is too large by about this factor. It is "
            "the only axis a household can act on -- the washing moves from 6pm to 2am, not to a "
            "windier Tuesday -- so it is the correct correction for a shifting claim and the "
            "annual p95/p5 figure is not."
        ),
    }


# --------------------------------------------------------------------------------------------
# The book side: whose electricity this is.
# --------------------------------------------------------------------------------------------

def book_run_output(directory: Path | None = None) -> Path:
    """The run output with the most households carrying an electricity EAC.

    NOT the newest, and that is a correction rather than a preference. `r1_inference_ceiling`'s
    `newest_run_output` picks by mtime and excludes `run_output_latest.json`; in a linked worktree
    every candidate it can see carries ZERO usable rows, because run outputs are gitignored and
    only the tracked stand-ins are extracted. Picking by mtime here would make this instrument
    refuse for a reason that has nothing to do with the book. Picking by what the file actually
    CONTAINS cannot go quiet in that way, and the file chosen is named in the payload.
    """
    directory = directory or (PROJECT / "docs" / "reports")
    best: tuple[int, Path] | None = None
    for path in sorted(directory.glob("run_output*.json")):
        try:
            rows = electricity_eac(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError, CeilingUnavailable):
            continue
        if best is None or len(rows) > best[0]:
            best = (len(rows), path)
    if best is None or best[0] == 0:
        raise CeilingUnavailable(
            f"no run output under {directory} carries a single electricity EAC, so there is no "
            "book to bound. This is what a linked worktree with no gitignored run data looks "
            "like, and it is NOT a measurement of an empty book."
        )
    return best[1]


def electricity_eac(payload: dict) -> dict[str, float]:
    """household -> the company's own estimate of its ELECTRICITY annual consumption, kWh.

    `company_eac_kwh` is on the company's own book (twelve months of its own billing), so this
    whole instrument stays the right side of the epistemic wall: it bounds what a real supplier
    could do with what a real supplier holds.

    GAS LEGS ARE EXCLUDED, and this is disqualification-battery item 10 of the carbon scope brief
    -- "gas modelled as time-varying carbon". A household's gas leg is registered under its
    electricity point's id plus a suffix, and `r1_inference_ceiling.observable_rows` AVERAGES the
    two into one household row. Reusing that reader would have credited gas kWh with an
    electricity timing benefit, in an instrument whose entire subject is that gas has no timing.
    The leg is identified by `household_of`, not by a string suffix, so the seam has one owner.
    """
    from simulation.household import household_of

    per_id: dict[str, list[float]] = {}
    for value in payload.values():
        if not (isinstance(value, list) and value and isinstance(value[0], dict)):
            continue
        for row in value:
            cid = row.get("customer_id")
            got = row.get("company_eac_kwh")
            if not cid or isinstance(got, bool) or not isinstance(got, (int, float)):
                continue
            if household_of(str(cid)) != str(cid):
                continue  # a secondary leg -- gas. It has no timing lever.
            per_id.setdefault(str(cid), []).append(float(got))
    return {cid: statistics.fmean(v) for cid, v in per_id.items() if v and statistics.fmean(v) > 0}


def secondary_legs_excluded(payload: dict) -> int:
    """How many EAC-carrying rows the gas filter removed. Published so the exclusion is visible.

    A count that is zero is the honest reading of a run whose gas legs carry no EAC, and a count
    that RISES is the reading of a book that grew them. Neither is an error; a silent filter is.
    """
    from simulation.household import household_of

    seen: set[str] = set()
    for value in payload.values():
        if not (isinstance(value, list) and value and isinstance(value[0], dict)):
            continue
        for row in value:
            cid = row.get("customer_id")
            got = row.get("company_eac_kwh")
            if not cid or isinstance(got, bool) or not isinstance(got, (int, float)):
                continue
            if household_of(str(cid)) != str(cid):
                seen.add(str(cid))
    return len(seen)


# --------------------------------------------------------------------------------------------
# The measurement.
# --------------------------------------------------------------------------------------------

def _grams_per_shifted_kwh(days: dict[str, list[float]], window: int, seed: int) -> dict:
    """The three world-side rungs, in gCO2e avoided per kWh moved, averaged over days.

    Each day is converted to grams with ITS OWN YEAR's annual intensity, which is the whole
    decarbonisation trend and would be erased by using one year's figure for all of them.
    """
    rng = random.Random(seed)
    hindsight: list[float] = []
    null_draws: list[list[float]] = [[] for _ in range(NULL_DRAWS)]
    per_year: dict[str, list[float]] = {}
    extrapolated: set[str] = set()

    for date_str, day in sorted(days.items()):
        year = int(date_str[:4])
        if grid_intensity_is_extrapolated(year):
            extrapolated.add(str(year))
        annual = grid_intensity_g_co2e_per_kwh(year)
        grams = achievable_saving_per_kwh(day, window) * annual
        hindsight.append(grams)
        per_year.setdefault(str(year), []).append(grams)
        for draw in range(NULL_DRAWS):
            null_draws[draw].append(skill_free_saving_per_kwh(day, window, rng) * annual)

    null_means = sorted(statistics.fmean(d) for d in null_draws)
    return {
        "hindsight_g_per_kwh": statistics.fmean(hindsight),
        "null_max_g_per_kwh": null_means[-1],
        "null_mean_g_per_kwh": statistics.fmean(null_means),
        "null_p95_g_per_kwh": null_means[int(0.95 * (len(null_means) - 1))],
        "by_year_g_per_kwh": {y: round(statistics.fmean(v), 4) for y, v in sorted(per_year.items())},
        "days": len(days),
        "years": sorted(per_year),
        "extrapolated_intensity_years": sorted(extrapolated),
    }


def capture_fraction(feed: dict) -> dict:
    """How much of the achievable saving acting on a real published forecast delivers.

    Read from the feed's own measurement. It is NOT clamped into [0, 1] there and is not clamped
    here: `capture_min` is negative and `capture_days_worse_than_average` is non-zero, which means
    there are days the forecast actively misled on. Clamping would delete exactly those days.
    """
    skill = feed.get("published_forecast_skill") or {}
    mean = skill.get("capture_mean_across_years")
    if not isinstance(mean, (int, float)):
        raise CeilingUnavailable(
            "the intensity feed carries no measured forecast capture, so the forecast rung would "
            "have to assume one -- and an assumed handicap in a ceiling is the ceiling"
        )
    return {
        "capture_mean": float(mean),
        "worst_year": skill.get("capture_worst_year"),
        "window_half_hours": skill.get("shift_window_half_hours"),
        "window_sensitivity": skill.get("window_sensitivity_capture_mean"),
    }


def measure(run_path: Path | None = None, seed: int = 20260907) -> dict:
    """The whole instrument. Every refusal names its reason."""
    feed = json.loads(INTENSITY_FEED.read_text(encoding="utf-8"))
    shape, typical = load_shape()
    days = whole_days(shape)
    if len(days) < MIN_DAYS:
        raise CeilingUnavailable(
            f"the intensity feed yields {len(days)} whole day(s) and a distribution needs at "
            f"least {MIN_DAYS}. A ceiling over a handful of days is a handful of days."
        )

    window = shift_window(feed)
    world = _grams_per_shifted_kwh(days, window, seed)
    capture = capture_fraction(feed)

    run_path = run_path or book_run_output()
    payload = json.loads(run_path.read_text(encoding="utf-8"))
    book = electricity_eac(payload)
    if len(book) < MIN_HOUSEHOLDS:
        raise CeilingUnavailable(
            f"{run_path.name} carries {len(book)} household(s) with an electricity EAC and this "
            f"instrument reports nothing under {MIN_HOUSEHOLDS}. That is a data-availability "
            "refusal and NOT a finding that the book cannot abate."
        )

    total_kwh = sum(book.values())
    hindsight_g = world["hindsight_g_per_kwh"]
    forecast_g = hindsight_g * capture["capture_mean"]
    null_g = world["null_max_g_per_kwh"]

    def rung(g_per_kwh: float, name: str, kind: str, note: str) -> dict:
        tonnes = g_per_kwh * total_kwh / 1e6
        return {
            "rung": name,
            "kind": kind,
            "g_co2e_per_shifted_kwh": round(g_per_kwh, 4),
            "book_tco2e_per_year": round(tonnes, 4),
            "book_gbp_per_year": round(tonnes * TRADED_CARBON_VALUE_GBP_PER_TONNE, 2),
            "gbp_per_household_year": round(
                tonnes * TRADED_CARBON_VALUE_GBP_PER_TONNE / len(book), 4),
            "kg_co2e_per_household_year": round(tonnes * 1000.0 / len(book), 3),
            "note": note,
        }

    rungs = {
        "baseline": {
            "rung": "baseline",
            "kind": "reference",
            "g_co2e_per_shifted_kwh": 0.0,
            "book_tco2e_per_year": 0.0,
            "book_gbp_per_year": 0.0,
            "gbp_per_household_year": 0.0,
            "kg_co2e_per_household_year": 0.0,
            "note": "No score at all. Abatement is zero BY CONSTRUCTION, not by measurement.",
        },
        "hindsight_ceiling": rung(
            hindsight_g, "hindsight_ceiling", "CEILING",
            "Perfect foreknowledge of the half-hourly shape, perfect compliance, every kWh moved. "
            "Unreachable by construction, which is what makes it a ceiling.",
        ),
        "forecast_ceiling": rung(
            forecast_g, "forecast_ceiling", "CEILING",
            "The same, acting on the PUBLISHED FORECAST -- what a household could actually act on "
            "-- handicapped by the feed's own measured capture of "
            f"{capture['capture_mean']:.4f}. Still perfect compliance, so still a ceiling.",
        ),
        "null_ceiling": rung(
            null_g, "null_ceiling", "noise floor",
            f"The MAX over {NULL_DRAWS} draws of an optimiser with no skill: window picked from a "
            "shuffled day, scored on the real one. How high chance reaches.",
        ),
    }

    overstatement = within_day_overstatement(feed, set(world["years"]))
    corrected = None
    if overstatement["available"]:
        factor = overstatement["mean"]
        corrected = rung(
            forecast_g / factor, "forecast_ceiling_corrected", "CEILING",
            "The forecast ceiling divided by the feed's own measured within-day overstatement of "
            f"{factor:.4f}. This is the honest headline: it removes the one exaggeration this "
            "repository has measured in the shape, on the one axis a household can act on.",
        )

    clears = hindsight_g > null_g
    return {
        "bound_kind": BOUND_KIND,
        "bound_kind_reason": BOUND_KIND_REASON,
        "bound_scope": BOUND_SCOPE,
        "not_bounded_by_this": list(NOT_BOUNDED_BY_THIS),
        "book": {
            "source_run": run_path.name,
            "households": len(book),
            "secondary_legs_excluded": secondary_legs_excluded(payload),
            "total_electricity_kwh_per_year": round(total_kwh, 1),
            "median_eac_kwh": round(statistics.median(book.values()), 1),
        },
        "world": world,
        "shift_window_half_hours": window,
        "forecast_capture": capture,
        "rungs": rungs,
        "within_day_overstatement": overstatement,
        "corrected_headline": corrected,
        "shiftable_share_curve": share_curve(
            (corrected or rungs["forecast_ceiling"])["gbp_per_household_year"],
            (corrected or rungs["forecast_ceiling"])["kg_co2e_per_household_year"],
        ),
        "carbon_value": {
            "gbp_per_tonne": TRADED_CARBON_VALUE_GBP_PER_TONNE,
            "basis": "DESNZ traded carbon values 2025, Table 1, central case, real 2025 GBP",
            "why_traded_and_not_non_traded": (
                "GB grid generation sits inside the UK ETS, so an abated grid tonne is a traded "
                "tonne. The non-traded value would roughly double every money figure here and "
                "this repository holds it only as an ASSERTED anchor, which may not be the "
                "comparator in a ceiling."
            ),
            "never_a_target": (
                "The cheapest way to improve a £/tonne score is to pick easy households, which is "
                "the opposite of the mission. This figure is a diagnostic (scope brief §D)."
            ),
        },
        "verdict": {
            "clears_the_null": clears,
            "hindsight_over_null": round(hindsight_g / null_g, 2) if null_g > 0 else None,
            "retires_time_shifting": not clears,
        },
        "named_gaps": [
            "SHIFTABLE SHARE of domestic load. Nothing in the knowledge layer, the commons or the "
            "market research establishes one, so the headline is reported at share = 1.0 and the "
            "curve is published instead of a figure. This is the single number that would turn "
            "the ceiling into an estimate, and it is a question to research.",
            "The non-traded (appraisal) carbon value is held only as an asserted anchor "
            "(~£80-90/tCO2e). Sourcing it would roughly double every money figure above.",
            "Book depth (A46): every figure here is a per-year rate over a book whose renewal "
            "history is thin, so what a ceiling can be DEMONSTRATED over is bounded separately.",
            "The shape is exogenous: a book-wide shift would itself move the merit order. At 164 "
            "households against ~28M GB homes that is negligible, and at national scale it is "
            "not -- which makes this a ceiling for THIS company and not for the policy.",
        ],
        "caveats": [
            f"Computed over {world['days']} whole days in years {', '.join(world['years'])}. That "
            "is a small panel and the figure carries its sample size for that reason.",
            "The typical-day cross-check below understates within-day spread because averaging "
            "days flattens it; the real-day rungs overstate it by the measured factor. The two "
            "bracket the answer rather than agreeing.",
        ],
        "typical_day_cross_check": typical_day_check(typical, window),
    }


def share_curve(gbp_at_full: float, kg_at_full: float) -> list[dict]:
    """Abatement is LINEAR in the shiftable share, so the curve is the honest publication.

    A single headline at some believable share would be a number picked because a number was
    needed. The curve says the same thing without pretending to know which row is real.
    """
    return [
        {
            "shiftable_share": share,
            "gbp_per_household_year": round(gbp_at_full * share, 4),
            "kg_co2e_per_household_year": round(kg_at_full * share, 3),
        }
        for share in SHARE_CURVE
    ]


def typical_day_check(typical: dict[str, list[float]], window: int) -> dict:
    """The same saving computed on each year's TYPICAL day, over the whole 2016-2025 record.

    Carried because the real-day panel covers four years and this covers ten, so it is the only
    view of the TREND -- and the trend is the finding a single figure would hide: the grid
    decarbonising shrinks the absolute headroom a timing programme has, so R3 is worth strictly
    less every year it is not built.

    UNDERSTATES, and is labelled so. A typical day is an average of days and averaging flattens
    within-day spread, so the cleanest window of a typical day is less clean than the cleanest
    window of a real one.
    """
    out: dict[str, float] = {}
    for year, day in sorted(typical.items()):
        if len(day) < MIN_PERIODS_PER_DAY:
            continue
        annual = grid_intensity_g_co2e_per_kwh(int(year))
        out[year] = round(achievable_saving_per_kwh(list(day), window) * annual, 4)
    if not out:
        return {"available": False, "why": "no year's typical day carries a full set of periods"}
    years = sorted(out)
    return {
        "available": True,
        "g_per_kwh_by_year": out,
        "first_year": years[0],
        "last_year": years[-1],
        "change_pct": round(100.0 * (out[years[-1]] - out[years[0]]) / out[years[0]], 1),
        "reads": (
            "UNDERSTATES the real-day figure -- averaging days flattens within-day spread. It is "
            "carried for the TREND, not for the level."
        ),
    }


def headline(result: dict) -> str:
    """One paragraph, and it has to survive being read alone."""
    corrected = result.get("corrected_headline") or result["rungs"]["forecast_ceiling"]
    hindsight = result["rungs"]["hindsight_ceiling"]
    verdict = result["verdict"]
    book = result["book"]
    trend = result.get("typical_day_cross_check") or {}

    if not verdict["clears_the_null"]:
        lead = (
            "R3 IS RETIRED ON TIMING. The perfect-foreknowledge ceiling does not clear an "
            "optimiser with no skill, and because this is a true CEILING that retires the "
            "time-shifting candidate outright rather than merely failing to support it."
        )
    else:
        lead = (
            f"R3's timing ceiling CLEARS its null by {verdict['hindsight_over_null']}x, so there "
            "is real carbon in the grid's shape for a score to point at."
        )

    body = (
        f" At perfect foreknowledge, perfect compliance and EVERY kWh moved, the whole "
        f"{book['households']}-household book abates "
        f"{hindsight['book_tco2e_per_year']:.2f} tCO2e/yr -- "
        f"£{hindsight['gbp_per_household_year']:.2f} per household-year at the DESNZ traded "
        f"carbon value. Acting on a real forecast and correcting the shape's own measured "
        f"within-day exaggeration takes that to "
        f"£{corrected['gbp_per_household_year']:.2f} per household-year "
        f"({corrected['kg_co2e_per_household_year']:.1f} kgCO2e). Those are CEILINGS at a "
        "shiftable share of 1.0, which no household has; at a tenth of load moved the figure is a "
        "tenth of that."
    )

    if trend.get("available"):
        body += (
            f" And it is shrinking: on the typical-day series the headroom moved "
            f"{trend['change_pct']:+.1f}% between {trend['first_year']} and {trend['last_year']} "
            "as the grid decarbonised, so the programme is worth less every year it is not built."
        )

    return lead + body


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--run", type=Path, default=None, help="run output to read the book from")
    parser.add_argument("--seed", type=int, default=20260907)
    parser.add_argument("--save", action="store_true", help=f"write {OUT_PATH.name}")
    args = parser.parse_args(argv)

    try:
        result = measure(run_path=args.run, seed=args.seed)
    except CeilingUnavailable as exc:
        print(f"REFUSED: {exc}")
        return 2

    result["headline"] = headline(result)
    print(json.dumps(result, indent=2))
    print("\n" + result["headline"])
    if args.save:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
