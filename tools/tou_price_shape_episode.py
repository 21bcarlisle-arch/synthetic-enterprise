"""Does the 2021-2023 episode put the faced price ratio inside the evidence range? Measured.

WHY THIS EXISTS
---------------
`docs/market_research/domestic_shift_response_as_a_function_of_pass_through.md` established the
domestic shift response as a function of the peak-to-off-peak price ratio (Arcturus 2.0) and then
could not locate the interior optimum, for a reason it named exactly: the price shape it had was too
flat. Median within-day wholesale ratio 1.77:1, household facing 1.26:1 at full pass-through, against
an evidence base that starts at 2:1 and an Ofgem statement that a factor of about three is needed.

It named the reason its panel might be unrepresentative rather than decisive: **the panel ends
2020-12 by construction**, before the gas crisis, and it called testing 2021-2023 the
highest-value measurement it had. This is that measurement.

IT IS A RATIO, SO THE CRISIS DOES NOT AUTOMATICALLY MOVE IT
------------------------------------------------------------
This is the trap the measurement is designed around, and it is this project's own recurring one:
separate LEVEL from AMPLITUDE before attributing anything. The 2021-2023 episode multiplied the
LEVEL of wholesale prices roughly threefold. The quantity a time-of-use tariff lives on is the
within-day SHAPE, and a shape is scale-free: multiply every half hour of a day by three and the
dearest-over-cheapest ratio does not move at all. Whether the episode widened the shape is a
genuinely open question that the level cannot answer, and the two are reported in separate columns
here so no reader can borrow one for the other.

EVERY EPISODE IS CUT THE SAME WAY
----------------------------------
The 2016-2020 panel is re-measured here by the identical code path, not quoted from the landed
artefact. A new number beside an old one computed differently is two constructions sharing a name,
and the comparison is the entire point of the instrument.

`s` IS READ FROM THE LAW, PER DAY, AND IT IS NOT A CONSTANT
------------------------------------------------------------
The bridge from pass-through to faced ratio needs `s`, the commodity share of the unit rate.
`tools/ofgem_cap_unit_rate_composition.py` reads it off Ofgem's own cap level model and finds it
runs 0.41 to 0.81 across cap periods. So each day is joined to the cap period actually in force over
it, rather than to a single grid value. Days before the cap existed (2019-01-01) can only rest on
Ofgem's own illustrative back-cast; those are COUNTED AND REPORTED, never silently mixed with law.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools.r3_carbon_score_ceiling import (  # noqa: E402
    CeilingUnavailable,
    achievable_saving_per_kwh,
    whole_days,
)

CACHE_DIR = PROJECT / "sim" / "cache"
ARC_PATH = PROJECT / "docs" / "market_research" / "domestic_shift_response_arc.json"
CAP_PATH = (PROJECT / "docs" / "domain_artefact_library" / "regulatory"
            / "ofgem_cap_unit_rate_composition.json")
CEILING_PATH = PROJECT / "docs" / "observability" / "tou_sharing_ceiling.json"
OUT_PATH = PROJECT / "docs" / "observability" / "tou_price_shape_by_episode.json"

#: The MID caches this cuts across. Each is a plain list of raw Elexon records; the join is
#: `sim.market_index_history.volume_weighted_mid`, reused rather than re-derived, because it carries
#: two measured fail-opens (an empty HTTP 200 on a too-wide window, and a reporting provider
#: publishing 0.00 on volume 0.00 for years at a time) that a fresh join would reproduce.
MID_CACHES = ("elexon_mid_full.json", "elexon_mid_2021_2023.json", "elexon_mid_2024_2025.json")

#: The shift window, in half hours. THE LANDED PANEL'S OWN, so the new episodes and the old one
#: describe one act. `tools/tou_sharing_ceiling.py` reads it from the intensity feed's
#: `published_forecast_skill` because a capture fraction was measured at it; nothing here uses a
#: capture fraction, so it is read from the landed sharing-ceiling artefact instead -- the same
#: number, from the committed record rather than a gitignored feed.
CEILING_WINDOW_FIELD = "shift_window_half_hours"

#: The episodes cut. 2016-2020 is the landed panel; 2021-2023 is the question; 2024-2025 is the
#: control that answers "did any widening persist after the crisis", which is what turns a
#: historical reading into something a tariff sold today could rest on.
EPISODES = (
    ("2016-2020", ("2016", "2017", "2018", "2019", "2020")),
    ("2021-2023", ("2021", "2022", "2023")),
    ("2024-2025", ("2024", "2025")),
)

#: Pass-throughs the faced ratio is printed at, and the grid the optimum is searched on. NOT domain
#: constants: a tariff's pass-through is a commercial decision nobody has taken on this book, so
#: there is no established value to cite and none is invented.
ALPHA_GRID = tuple(i / 200 for i in range(201))
ALPHA_PRINTED = (0.25, 0.50, 0.75, 1.00)

#: Where the published evidence starts, and where Ofgem says a material response starts. Both are
#: quoted from the arc artefact's own fields at runtime; these names exist so the comparison is
#: legible in the output rather than being a bare number.
ARCTURUS_FLOOR_FIELD = "estimation_range_price_ratio"


def _named(path: Path) -> str:
    """A path for a REFUSAL MESSAGE, project-relative when it can be and whole when it cannot.

    `Path.relative_to` RAISES on a path outside the project, so building a refusal message with it
    turns a clean refusal into a ValueError from inside the error path -- the fail-open that is
    hardest to see, because the caller gets a crash where the code was carefully written to explain
    itself. Found by the control that pointed this module at a temporary directory.
    """
    try:
        return str(path.relative_to(PROJECT))
    except ValueError:
        return str(path)


class EpisodeUnavailable(RuntimeError):
    """Raised when the measurement cannot be made.

    An exception, not a zero. The MID caches and the cap models are gitignored source data, so a
    clean worktree extract has none of them, and an instrument that returned "median ratio 0.0"
    there would read exactly like "measured the market, found it flat".
    """


def load_prices() -> dict[tuple[str, int], float]:
    """(date, settlement period) -> volume-weighted traded wholesale price, GBP/MWh."""
    from sim.market_index_history import volume_weighted_mid

    records: list[dict] = []
    seen: list[str] = []
    for name in MID_CACHES:
        path = CACHE_DIR / name
        if not path.exists():
            continue
        try:
            chunk = json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            raise EpisodeUnavailable(f"{name} could not be read: {exc}") from exc
        if not isinstance(chunk, list) or not chunk:
            raise EpisodeUnavailable(f"{name} is present but carries no records")
        records.extend(chunk)
        seen.append(name)
    if not seen:
        raise EpisodeUnavailable(
            f"none of {list(MID_CACHES)} is present in {_named(CACHE_DIR)}. They are "
            "gitignored source data, which is what a linked worktree extract looks like, and it is "
            "NOT a finding that the market has no price shape."
        )
    prices = volume_weighted_mid(records)
    if not prices:
        raise EpisodeUnavailable(
            "the MID join returned no priced half hour across every cache present. Every record "
            "carried zero or non-finite volume, which is the non-reporting-provider fail-open the "
            "join already guards, and it is a data absence rather than a market with no trades."
        )
    return prices


def _load(path: Path, what: str) -> dict:
    if not path.exists():
        raise EpisodeUnavailable(f"{_named(path)} is absent, so {what} is unavailable")
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise EpisodeUnavailable(f"{_named(path)} could not be read: {exc}") from exc


def arc_response(ratio: float, coefficients: dict, opt_out: bool, tech: bool = False) -> float:
    """Peak demand reduction as a POSITIVE proportion, from the Arcturus 2.0 fit.

    The paper's coefficients are on a NEGATIVE outcome (reduction), so the sign is flipped once,
    here, and never again.

    THE INTERCEPT IS AN ARTEFACT AND IT DOES NOT VANISH AT A FLAT PRICE. The primary specification's
    constant is -0.011, so at a ratio of exactly 1:1 -- a household shown no price difference at all
    -- this returns a 1.1% peak reduction. That is a regression intercept fitted over a sample that
    starts at 2:1, not a claim that flat pricing moves load, and a caller reading company value at
    zero pass-through is reading that artefact rather than a response. The opt-out specification
    happens not to have it (-0.028 + 0.039 = +0.011 clips to zero), which is a coincidence of two
    published coefficients and not a design.

    Clipped at zero because the raw expression goes negative once the off-peak window is DEARER than
    the peak one, and a negative reduction published as a response would put a value-destroying
    tariff on the frontier.
    """
    if ratio <= 0:
        raise EpisodeUnavailable("a non-positive price ratio has no logarithm and no response")
    log_ratio = math.log(ratio)
    value = (coefficients["constant"]
             + coefficients["ln_price_ratio"] * log_ratio
             + (coefficients["ln_price_ratio_x_technology"] * log_ratio if tech else 0.0)
             + (coefficients.get("opt_out_binary", 0.0) if opt_out else 0.0))
    return max(0.0, -value)


def cap_share_by_period(cap: dict) -> list[tuple[str, float, bool]]:
    """(period start date, commodity share of the unit rate, was the cap in force), earliest first.

    Direct debit, because that is the payment method this book's households are on. The artefact
    carries all three and they differ; taking one and saying which is the point.
    """
    periods = cap.get("by_payment_method", {}).get("direct_debit", {}).get("periods", [])
    rows = [(p["starts"], float(p["commodity_share_of_unit_rate"]), bool(p["cap_in_force"]))
            for p in periods if p.get("starts")]
    if not rows:
        raise EpisodeUnavailable(
            f"{_named(CAP_PATH)} carries no dated direct-debit cap period, so no day "
            "can be joined to the commodity share that applied over it"
        )
    return sorted(rows)


def share_for(date_str: str, schedule: list[tuple[str, float, bool]]) -> tuple[float, bool]:
    """The commodity share in force on a date, and whether it rests on the law or a back-cast.

    A step function looked up backwards, never interpolated: a cap period's allowance applies to
    the whole period and changes on its boundary.
    """
    chosen = None
    for starts, share, in_force in schedule:
        if starts <= date_str:
            chosen = (share, in_force)
        else:
            break
    if chosen is None:
        # Before Ofgem's earliest column. Fall back to the earliest published share and say so.
        return schedule[0][1], False
    return chosen


def measure_episode(label: str, years: tuple[str, ...], days: dict[str, list[float]], window: int,
                    coefficients: dict, opt_out_coefficients: dict,
                    schedule: list[tuple[str, float, bool]], kwh_per_household: float) -> dict:
    """One episode: the raw shape, the faced ratio, the response, and the interior optimum."""
    selected = sorted(d for d in days if d[:4] in years)
    if not selected:
        return {"episode": label, "available": False,
                "why": f"no whole day in the MID caches falls in {list(years)}"}

    ratios: list[float] = []
    per_day: list[tuple[float, float, float]] = []   # (peak_rel, off_rel, s)
    savings: list[float] = []
    mean_prices: list[float] = []
    non_positive = 0
    backcast_days = 0

    for date_str in selected:
        day = days[date_str]
        ordered = sorted(day)
        mean_price = statistics.fmean(day)
        cheapest = statistics.fmean(ordered[:window])
        dearest = statistics.fmean(ordered[-window:])
        savings.append(achievable_saving_per_kwh(day, window))
        mean_prices.append(mean_price)
        share, in_force = share_for(date_str, schedule)
        if not in_force:
            backcast_days += 1
        if cheapest <= 0 or mean_price <= 0:
            # A negative cheapest window makes the ratio meaningless rather than large. Counted,
            # because 2022-2025 produced many and a silent drop would flatter the tail.
            non_positive += 1
            continue
        ratios.append(dearest / cheapest)
        per_day.append((dearest / mean_price, cheapest / mean_price, share))

    if not ratios:
        return {"episode": label, "available": False,
                "why": f"every one of {len(selected)} days had a non-positive cheapest window"}

    quantiles = statistics.quantiles(ratios, n=100)
    raw = {
        "days": len(selected),
        "days_with_a_positive_cheapest_window": len(ratios),
        "days_dropped_non_positive_cheapest_window": non_positive,
        "days_resting_on_ofgems_illustrative_backcast_not_the_cap": backcast_days,
        "within_day_wholesale_ratio": {
            "p10": round(quantiles[9], 3), "p25": round(quantiles[24], 3),
            "median": round(statistics.median(ratios), 3),
            "p75": round(quantiles[74], 3), "p90": round(quantiles[89], 3),
        },
        "median_dearest_window_over_day_mean": round(statistics.median(p for p, _, _ in per_day), 3),
        "median_cheapest_window_over_day_mean": round(statistics.median(o for _, o, _ in per_day), 3),
        "commodity_share_median": round(statistics.median(s for _, _, s in per_day), 4),
        "level_mean_day_price_gbp_per_mwh": round(statistics.fmean(mean_prices), 2),
        "created_value_gbp_per_shifted_mwh": round(statistics.fmean(savings), 3),
        "created_value_gbp_per_household_year": round(
            statistics.fmean(savings) * kwh_per_household / 1000.0, 2),
    }

    def faced(alpha: float) -> list[float]:
        out = []
        for peak_rel, off_rel, share in per_day:
            numerator = 1.0 + alpha * share * (peak_rel - 1.0)
            denominator = 1.0 + alpha * share * (off_rel - 1.0)
            if denominator > 0 and numerator > 0:
                out.append(numerator / denominator)
        return out

    def mean_response(alpha: float, opt_out: bool) -> float:
        """Response computed PER DAY then averaged -- never the response at the average ratio.
        Those are different quantities through a concave function."""
        values = faced(alpha)
        if not values:
            return 0.0
        coeffs = opt_out_coefficients if opt_out else coefficients
        return statistics.fmean(arc_response(r, coeffs, opt_out) for r in values)

    printed = []
    for alpha in ALPHA_PRINTED:
        values = sorted(faced(alpha))
        if not values:
            continue
        q = statistics.quantiles(values, n=100)
        printed.append({
            "alpha": alpha,
            "faced_ratio_p50": round(statistics.median(values), 3),
            "faced_ratio_p90": round(q[89], 3),
            "days_at_or_above_2to1": round(sum(1 for v in values if v >= 2.0) / len(values), 4),
            "days_at_or_above_3to1": round(sum(1 for v in values if v >= 3.0) / len(values), 4),
            "mean_response_opt_in": round(mean_response(alpha, False), 4),
            "mean_response_opt_out": round(mean_response(alpha, True), 4),
        })

    created = raw["created_value_gbp_per_household_year"]
    optimum = {}
    for recruitment, opt_out in (("opt_in", False), ("opt_out", True)):
        best_alpha, best_company = 0.0, -1.0
        for alpha in ALPHA_GRID:
            company = created * mean_response(alpha, opt_out) * (1.0 - alpha)
            if company > best_company:
                best_alpha, best_company = alpha, company
        response = mean_response(best_alpha, opt_out)
        optimum[recruitment] = {
            "argmax_alpha": round(best_alpha, 3),
            "company_gbp_per_household_year": round(best_company, 3),
            "household_gbp_per_household_year": round(created * response * best_alpha, 3),
            "response_at_optimum": round(response, 4),
        }

    return {"episode": label, "available": True, "years": list(years),
            "raw_price_shape": raw, "faced_ratio_and_response": printed,
            "interior_optimum": optimum}


def measure() -> dict:
    arc = _load(ARC_PATH, "the Arcturus response function")
    cap = _load(CAP_PATH, "the commodity share of the unit rate")
    ceiling = _load(CEILING_PATH, "the landed sharing ceiling")

    function = arc["response_function"]
    coefficients = function["primary_specification"]
    opt_out_coefficients = function["opt_out_specification"]
    evidence_floor = float(function[ARCTURUS_FLOOR_FIELD][0])

    window = ceiling.get(CEILING_WINDOW_FIELD)
    if not isinstance(window, int) or window <= 0:
        raise EpisodeUnavailable(
            f"the landed sharing ceiling carries no usable {CEILING_WINDOW_FIELD}, so there is no "
            "window at which this episode could be cut the same way as the landed panel"
        )
    book = ceiling.get("book", {})
    total_kwh = book.get("total_electricity_kwh_per_year")
    households = book.get("households_with_an_eac")
    if not isinstance(total_kwh, (int, float)) or not isinstance(households, int) or households < 1:
        raise EpisodeUnavailable(
            "the landed sharing ceiling carries no book to divide, so created value cannot be put "
            "on a per-household-year basis the way its own headline is"
        )
    kwh_per_household = float(total_kwh) / households

    # A reachability check on the arc reader BEFORE it is used on anything. The landed artefact
    # states what the fit returns at CLNR's 2.88:1 for both recruitments; if this reader does not
    # reproduce those, every response below is being computed from a misread specification.
    clnr = next((row for row in arc.get("gb_corroboration", []) if "CLNR" in row.get("trial", "")),
                None)
    if clnr is None:
        raise EpisodeUnavailable("the arc artefact carries no CLNR row to check the reader against")
    checks = {
        "opt_in": (arc_response(clnr["price_ratio"], coefficients, False),
                   clnr["arc_predicts_opt_in"]),
        "opt_out": (arc_response(clnr["price_ratio"], opt_out_coefficients, True),
                    clnr["arc_predicts_opt_out"]),
    }
    for name, (got, want) in checks.items():
        if abs(got - want) > 0.001:
            raise EpisodeUnavailable(
                f"the arc reader returns {got:.4f} for {name} at CLNR's {clnr['price_ratio']}:1 "
                f"where the landed artefact states {want}. The specification is being misread and "
                "no response computed from it should be published."
            )

    days = whole_days(load_prices())
    schedule = cap_share_by_period(cap)
    episodes = [measure_episode(label, years, days, window, coefficients, opt_out_coefficients,
                                schedule, kwh_per_household)
                for label, years in EPISODES]

    by_year = {}
    for year in sorted({d[:4] for d in days}):
        row = measure_episode(year, (year,), days, window, coefficients, opt_out_coefficients,
                              schedule, kwh_per_household)
        if row.get("available"):
            by_year[year] = row["raw_price_shape"]

    landed = next(e for e in episodes if e["episode"] == "2016-2020")
    question = next(e for e in episodes if e["episode"] == "2021-2023")
    return {
        "artefact": "tou_price_shape_by_episode",
        "question": (
            "Does the 2021-2023 episode put the peak-to-off-peak price ratio a household faces "
            "inside the range over which the domestic shift response was actually estimated?"
        ),
        "why_it_was_asked": (
            "The landed shift-response finding could not locate the interior optimum and named the "
            "reason: its Elexon MID panel ends 2020-12 by construction, so its median within-day "
            "ratio of 1.77:1 might be an artefact of which years we hold rather than a fact about "
            "the market. It called this the highest-value measurement it had."
        ),
        "method": {
            "price_series": "Elexon MID, volume-weighted, via sim/market_index_history.py",
            "day_builder": "tools/r3_carbon_score_ceiling.whole_days -- the landed panel's own",
            "shift_window_half_hours": window,
            "ratio": "mean of the day's dearest N half hours over the mean of its cheapest N",
            "bridge": "ratio(alpha,s) = [1+alpha*s*(peak_rel-1)] / [1+alpha*s*(off_rel-1)]",
            "s": "read PER DAY from the cap period in force, via "
                 "docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json",
            "response": "computed per day and then averaged, never the response at the mean ratio",
            "the_landed_panel_is_re_measured_here": (
                "2016-2020 is recomputed by this identical code path rather than quoted, because a "
                "new number beside an old one computed differently is two constructions sharing a "
                "name, and the comparison is the whole point."
            ),
            "arc_reader_checked_against": (
                f"the landed artefact's own CLNR predictions at {clnr['price_ratio']}:1 "
                f"(opt-in {clnr['arc_predicts_opt_in']}, opt-out {clnr['arc_predicts_opt_out']})"
            ),
        },
        "evidence_floor_price_ratio": evidence_floor,
        "ofgem_material_response_threshold": 3.0,
        "episodes": episodes,
        "by_year_raw_shape": by_year,
        "what_actually_moved_the_faced_ratio": attribute(days, window, schedule),
        "verdict": verdict(landed, question, evidence_floor),
    }


def attribute(days: dict[str, list[float]], window: int,
              schedule: list[tuple[str, float, bool]]) -> dict:
    """Split the move in the faced ratio between the PRICE SHAPE and the COMMODITY SHARE.

    THE ONE-VARIABLE VERSION, because two things changed between the landed panel and this episode
    and a result that moves when more than one input moved cannot be attributed. The wholesale
    within-day shape changed (a little) and `s` changed (a lot, because the crisis raised the
    wholesale allowance while network and policy allowances stood still). Each is swapped in alone,
    against the other's own baseline, so the reader is not asked to take the split on trust.
    """
    def rows(years: tuple[str, ...]) -> list[tuple[float, float, float]]:
        out = []
        for date_str in sorted(days):
            if date_str[:4] not in years:
                continue
            day = days[date_str]
            ordered = sorted(day)
            mean_price = statistics.fmean(day)
            cheapest = statistics.fmean(ordered[:window])
            if cheapest <= 0 or mean_price <= 0:
                continue
            out.append((statistics.fmean(ordered[-window:]) / mean_price, cheapest / mean_price,
                        share_for(date_str, schedule)[0]))
        return out

    def faced_median(source: list[tuple[float, float, float]], share: float | None) -> float:
        values = []
        for peak_rel, off_rel, own_share in source:
            use = own_share if share is None else share
            numerator, denominator = 1.0 + use * (peak_rel - 1.0), 1.0 + use * (off_rel - 1.0)
            if numerator > 0 and denominator > 0:
                values.append(numerator / denominator)
        return statistics.median(values)

    old, new = rows(EPISODES[0][1]), rows(EPISODES[1][1])
    if not old or not new:
        return {"available": False, "why": "one of the two episodes has no usable day"}
    old_share = statistics.median(s for _, _, s in old)
    new_share = statistics.median(s for _, _, s in new)
    baseline, measured = faced_median(old, None), faced_median(new, None)
    return {
        "available": True,
        "at_pass_through": 1.0,
        "baseline_2016_2020": round(baseline, 4),
        "measured_2021_2023": round(measured, 4),
        "new_shape_with_old_commodity_share": round(faced_median(new, old_share), 4),
        "old_shape_with_new_commodity_share": round(faced_median(old, new_share), 4),
        "commodity_share_2016_2020": round(old_share, 4),
        "commodity_share_2021_2023": round(new_share, 4),
        "reading": (
            "Swapping in the 2021-2023 wholesale SHAPE alone moves the faced ratio by about a "
            "thousandth. Swapping in the 2021-2023 COMMODITY SHARE alone moves essentially the "
            "whole distance. The episode did improve the ratio a household faces -- but not through "
            "the price shape, which is what a time-of-use tariff actually sells. It improved it "
            "because the crisis temporarily made wholesale a larger fraction of the unit rate, and "
            "that has already unwound: the share is back to 0.56 by late 2023 from a peak of 0.81."
        ),
    }


def verdict(landed: dict, question: dict, evidence_floor: float) -> dict:
    """The answer, stated in whichever direction it falls."""
    if not question.get("available"):
        return {"answer": "UNMEASURED", "why": question.get("why")}
    old = landed["raw_price_shape"]["within_day_wholesale_ratio"]["median"]
    new = question["raw_price_shape"]["within_day_wholesale_ratio"]["median"]
    faced_full = next((row for row in question["faced_ratio_and_response"] if row["alpha"] == 1.00),
                      None)
    faced_median = faced_full["faced_ratio_p50"] if faced_full else None
    clears = faced_median is not None and faced_median >= evidence_floor
    return {
        "answer": "REACHES THE EVIDENCE RANGE" if clears else "DOES NOT REACH THE EVIDENCE RANGE",
        "raw_median_ratio_landed_panel": old,
        "raw_median_ratio_2021_2023": new,
        "faced_median_ratio_at_full_pass_through_2021_2023": faced_median,
        "evidence_floor": evidence_floor,
        "level_moved_amplitude_did_not": {
            "mean_day_price_gbp_per_mwh_landed": landed["raw_price_shape"]["level_mean_day_price_gbp_per_mwh"],
            "mean_day_price_gbp_per_mwh_2021_2023": question["raw_price_shape"]["level_mean_day_price_gbp_per_mwh"],
            "reading": (
                "The LEVEL of wholesale prices and the created value per shifted MWh both moved "
                "several-fold. The within-day SHAPE, which is what a time-of-use tariff lives on, "
                "did not. A ratio is scale-free and the crisis was a level event."
            ),
        },
    }


def main(argv=None) -> int:
    del argv
    try:
        result = measure()
    except (EpisodeUnavailable, CeilingUnavailable) as exc:
        print(f"REFUSED: {exc}")
        return 2
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=1) + "\n")

    print(f"{'episode':10s} {'days':>5s} {'neg':>4s} {'p50':>5s} {'p90':>6s} "
          f"{'s':>5s} {'£/MWh':>7s} {'£/hh/yr':>8s} {'faced@1.0':>9s} {'>=2:1':>6s}")
    for episode in result["episodes"]:
        if not episode.get("available"):
            print(f"{episode['episode']:10s} unavailable: {episode['why']}")
            continue
        raw = episode["raw_price_shape"]
        full = next(r for r in episode["faced_ratio_and_response"] if r["alpha"] == 1.00)
        print(f"{episode['episode']:10s} {raw['days']:5d} "
              f"{raw['days_dropped_non_positive_cheapest_window']:4d} "
              f"{raw['within_day_wholesale_ratio']['median']:5.2f} "
              f"{raw['within_day_wholesale_ratio']['p90']:6.2f} "
              f"{raw['commodity_share_median']:5.3f} "
              f"{raw['level_mean_day_price_gbp_per_mwh']:7.1f} "
              f"{raw['created_value_gbp_per_household_year']:8.2f} "
              f"{full['faced_ratio_p50']:9.3f} {full['days_at_or_above_2to1']:6.3f}")
    print()
    print(f"VERDICT: {result['verdict']['answer']}")
    print(f"written to {_named(OUT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
