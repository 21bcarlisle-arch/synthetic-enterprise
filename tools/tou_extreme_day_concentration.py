"""Is a time-of-use tariff that pays only on EXTREME days a better product, or merely a rarer one?

WHY THIS EXISTS
---------------
`docs/observability/tou_price_shape_by_episode.json` settled the spread question and closed it: the
within-day ratio has not moved in ten years (1.772 -> 1.791 -> 1.696), the crisis was a LEVEL event,
and a ratio is scale-free. But the same cut surfaced a shape nobody had looked at. 2024-2025 has the
FLATTEST median of the whole record and by far the FATTEST tail -- p90 6.67 against 3.39. The
distribution is becoming SKEWED, not wider: many flat days and a few extreme ones, which is the
renewables-and-scarcity signature.

Every figure that instrument publishes is a MEAN over all days, which is exactly the wrong statistic
for a product whose value is concentrated in a tail. This one is the tail.

THE STRUCTURAL ANSWER IS ARITHMETIC AND IT WAS WRITTEN DOWN FIRST
------------------------------------------------------------------
Company value is `sum over paid days of saving_d * kwh_d * response_d(alpha) * (1-alpha)`. Every
term is non-negative, and the extreme-day product sums a SUBSET of the everyday product's days. So
at a common pass-through and a common response model:

    extreme(q) <= everyday, for every q < 100%. Always.

That is not a finding, it is arithmetic, and it is pre-registered as such in
`docs/staging/SEAT_PREDICTION_WHAT_AN_EXTREME_DAY_ONLY_TOU_TARIFF_CAN_AND_CANNOT_BE_WORTH_2026-09-07.md`
so that a run reporting otherwise is read as a defect in THIS MODULE rather than as a result.
`assert_the_subset_cannot_beat_the_whole` below is that control, and it runs on live figures.

What it means is that the commercial question is displaced, not answered. The extreme-day product
can only be better through the cost it avoids on the days it does not pay, or through a called-day
ATTENTION PREMIUM -- a household acting harder on "tonight matters" than on a standing tariff it has
habituated to. Arcturus 2.0 models neither, and nothing in the knowledge layer establishes either.
So both are carried as BREAK-EVENS rather than filled with a number picked because a number was
needed. A break-even is falsifiable by a future source; an invented constant is load-bearing within
a week and unattributable within a month.

THE DAYS THE PRODUCT MOST WANTS ARE THE DAYS THE MODEL CANNOT PRICE
--------------------------------------------------------------------
The landed panel drops days whose cheapest window is non-positive -- 81 of 731 in 2024-2025 -- and
counts them, because a negative price makes a RATIO meaningless rather than large. But the SAVING on
such a day (its mean minus its cheapest window) is perfectly well defined and it is enormous. Those
are negative-price days: the single most valuable days a shifting tariff could ever call, and the
log-ratio response function cannot take a logarithm of any of them.

So this instrument reports the concentration of GROSS value over EVERY day, and prices the products
over only the days the response model can reach, and states the gap between the two in money. Any
other arrangement either drops the fattest tail silently or prices it with a function that has no
value there.

THE FLAT kWh ALLOCATION IS REPLACED BY A PUBLISHED LOAD SHAPE, NOT NAMED AS A GAP
----------------------------------------------------------------------------------
The landed panel spreads the year's kWh evenly across its days, which is right for a mean and wrong
for a tail: extreme price days are disproportionately winter days, and a winter day carries about
1.39x a summer day's domestic consumption. `sim/profile_class_1.py` already holds the real published
Elexon PC1 (domestic unrestricted) Group Average Demand shape, so each day is weighted by the load a
domestic household actually has on it. Both allocations are reported: FLAT reproduces the landed
panel's convention so the columns reconcile, and PC1 is the load-faithful one the verdict rests on.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from sim.profile_class_1 import load_pc1_shape  # noqa: E402
from tools.r3_carbon_score_ceiling import (  # noqa: E402
    CeilingUnavailable,
    achievable_saving_per_kwh,
    whole_days,
)
from tools.tou_price_shape_episode import (  # noqa: E402
    ARC_PATH,
    CAP_PATH,
    CEILING_PATH,
    EPISODES,
    EpisodeUnavailable,
    _load,
    _named,
    arc_response,
    cap_share_by_period,
    load_prices,
    share_for,
)

OUT_PATH = PROJECT / "docs" / "observability" / "tou_extreme_day_concentration.json"
PC1_CSV = PROJECT / "sim" / "data" / "profile_class_1_gad.csv"

#: The pass-throughs searched for each product's own optimum. Identical grid to the landed panel's,
#: so a company figure here and one there differ by the product and never by the search.
ALPHA_GRID = tuple(i / 200 for i in range(201))

#: The trigger fractions priced. A tariff paying on the dearest q of days, q read as a fraction of
#: the days the response model can price. NOT domain constants: which decile a commercial product
#: would trigger on is the decision this instrument exists to inform, so a range is priced rather
#: than a value chosen.
TRIGGERS = (0.01, 0.05, 0.10, 0.25)

#: The one the verdict is stated at, because the direction asked for the top decile by name.
HEADLINE_TRIGGER = 0.10

#: Sourced, and already spent by this book: the CMA-era single-fuel PCS commission midpoint, from
#: `saas.opex_ledger.CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER` via
#: `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`. Read from the ledger at runtime rather than
#: restated, so a revision there cannot leave a stale copy of it published here.
CAC_CHANNEL = "pcs_aggregator"

DAYS_PER_YEAR = 365.25


class ConcentrationUnavailable(RuntimeError):
    """Raised when the measurement cannot be made.

    An exception, not a zero, and for the reason its sibling instrument names: the MID caches and
    the cap models are gitignored source data, so a clean worktree extract holds none of them, and
    an instrument returning "top decile share 0.0" there would read exactly like "measured the
    market, found the value evenly spread" -- which is the opposite of what an absence means.
    """


def slope_response(ratio: float, coefficients: dict) -> float:
    """The Arcturus response with the INTERCEPT REMOVED, as a positive proportion.

    A price response must vanish at a flat price, and the fitted one does not: the primary
    specification's constant is -0.011, so a household shown no price difference at all is credited
    with a 1.1% peak reduction. `tests/tools/test_tou_price_shape_episode.py` already pins that as a
    known artefact of a regression fitted over a sample starting at 2:1.

    It matters HERE in a way it did not there, and the reason is the whole point of this instrument.
    The everyday product pays on all 365 days, and on the great majority of them the faced ratio is
    within a whisker of 1:1 -- so the everyday product collects the intercept 365 times over, while
    the extreme-day product collects it a few dozen times. Comparing the two on the fitted response
    is therefore not a comparison of products at all: it is a comparison of how many days each one
    is credited with a constant that is not a response to anything.

    So the verdict rests on this column and the fitted one is reported beside it. Clipped at zero
    for the same reason its sibling clips: below 1:1 the off-peak window is dearer than the peak
    one, and a negative reduction published as a response would put a value-destroying tariff on
    the frontier while looking like an ordinary small number on the way past.
    """
    if ratio <= 0:
        raise ConcentrationUnavailable(
            "a non-positive price ratio has no logarithm and no response")
    return max(0.0, -coefficients["ln_price_ratio"] * math.log(ratio))


class Day:
    """One day: what it is worth, whether the response model can reach it, and its real load.

    `ratio_defined` is the field this instrument turns on. A day whose cheapest window is
    non-positive has a well-defined SAVING and no meaningful RATIO, and those days are neither
    dropped nor priced: they are carried, counted, and reported in money.
    """

    __slots__ = ("date", "saving", "ratio", "peak_rel", "off_rel", "share", "kwh",
                 "ratio_defined", "backcast")

    def __init__(self, date_str: str, saving: float, kwh: float, share: float, backcast: bool,
                 ratio: float | None, peak_rel: float | None, off_rel: float | None):
        self.date = date_str
        self.saving = saving
        self.kwh = kwh
        self.share = share
        self.backcast = backcast
        self.ratio = ratio
        self.peak_rel = peak_rel
        self.off_rel = off_rel
        self.ratio_defined = ratio is not None

    def faced_ratio(self, alpha: float) -> float | None:
        """The ratio the household actually faces at pass-through `alpha`, or None.

        The same bridge the landed panel uses, and `s` is this day's own commodity share read from
        the cap period in force over it, never a grid value.
        """
        if not self.ratio_defined:
            return None
        numerator = 1.0 + alpha * self.share * (self.peak_rel - 1.0)
        denominator = 1.0 + alpha * self.share * (self.off_rel - 1.0)
        if numerator <= 0 or denominator <= 0:
            return None
        return numerator / denominator


def pc1_kwh(date_str: str) -> float:
    """A domestic household's real consumption on this calendar date, kWh.

    Elexon Profile Class 1 Group Average Demand, half-hourly kW, times half an hour. Published,
    seasonal and day-type aware, and already in the tree -- so the landed panel's flat allocation is
    replaced with a sourced shape rather than a named gap or an invented winter multiplier.
    """
    target = date(int(date_str[0:4]), int(date_str[5:7]), int(date_str[8:10]))
    return sum(kw * 0.5 for kw in load_pc1_shape(target, str(PC1_CSV)))


def build_days(days: dict[str, list[float]], window: int, years: tuple[str, ...],
               schedule: list[tuple[str, float, bool]]) -> list[Day]:
    """Every day of the episode, priced and weighted. Nothing is dropped here."""
    rows: list[Day] = []
    for date_str in sorted(d for d in days if d[:4] in years):
        day = days[date_str]
        ordered = sorted(day)
        mean_price = statistics.fmean(day)
        cheapest = statistics.fmean(ordered[:window])
        dearest = statistics.fmean(ordered[-window:])
        share, in_force = share_for(date_str, schedule)
        priced = cheapest > 0 and mean_price > 0
        rows.append(Day(
            date_str=date_str,
            saving=achievable_saving_per_kwh(day, window),
            kwh=pc1_kwh(date_str),
            share=share,
            backcast=not in_force,
            ratio=(dearest / cheapest) if priced else None,
            peak_rel=(dearest / mean_price) if priced else None,
            off_rel=(cheapest / mean_price) if priced else None,
        ))
    return rows


def weights(rows: list[Day], allocation: str) -> list[float]:
    """Each day's share of the year's kWh, summing to 1 over `rows`.

    FLAT is the landed panel's convention -- every day carries 1/N of the year -- and is kept so the
    two instruments' columns reconcile. PC1 weights each day by the load a domestic household
    actually has on it, which is what a tail measurement needs: extreme price days are winter days,
    and weighting them like an August Sunday understates exactly the product under test.
    """
    if not rows:
        return []
    if allocation == "flat":
        return [1.0 / len(rows)] * len(rows)
    if allocation == "pc1":
        total = sum(row.kwh for row in rows)
        if total <= 0:
            raise ConcentrationUnavailable(
                "the PC1 load shape summed to zero kWh over the episode, so no day can be weighted "
                "by the load on it")
        return [row.kwh / total for row in rows]
    raise ConcentrationUnavailable(f"unknown kWh allocation {allocation!r}")


def gross_value(rows: list[Day], allocation: str, kwh_per_year: float) -> list[float]:
    """Each day's contribution to the year's gross achievable value, GBP per household.

    Sums to the annualised figure the landed panel publishes when `allocation` is flat and the same
    days are included -- deliberately, because a concentration share is only legible as a share of
    a total the reader has already seen.
    """
    return [w * row.saving * kwh_per_year / 1000.0
            for row, w in zip(rows, weights(rows, allocation))]


def concentration(rows: list[Day], allocation: str, kwh_per_year: float) -> dict:
    """How much of the year's gross value sits in the dearest days, and where the blind spot is."""
    values = gross_value(rows, allocation, kwh_per_year)
    total = sum(values)
    if total <= 0:
        raise ConcentrationUnavailable(
            "the episode's total achievable value is not positive, so no share of it can be taken")
    order = sorted(range(len(rows)), key=lambda i: values[i], reverse=True)

    curve = {}
    for fraction in (0.01, 0.05, 0.10, 0.25, 0.50):
        take = max(1, round(fraction * len(order)))
        curve[f"top_{int(fraction * 100)}pc_of_days"] = {
            "days": take,
            "share_of_gross_value": round(sum(values[i] for i in order[:take]) / total, 4),
        }

    blind = [i for i in order if not rows[i].ratio_defined]
    top_decile = set(order[:max(1, round(0.10 * len(order)))])
    return {
        "days": len(rows),
        "gross_value_gbp_per_household_year": round(total, 2),
        "curve": curve,
        "the_days_the_response_model_cannot_price": {
            "days": len(blind),
            "share_of_days": round(len(blind) / len(rows), 4),
            "share_of_gross_value": round(sum(values[i] for i in blind) / total, 4),
            "share_of_them_that_are_in_the_top_decile_by_value": (
                round(sum(1 for i in blind if i in top_decile) / len(blind), 4) if blind else None),
            "why": (
                "Their cheapest window is non-positive -- a negative wholesale price. The SAVING on "
                "such a day is well defined and large; the RATIO is meaningless rather than large, "
                "and Arcturus 2.0 is a function of the log of that ratio. These are the days a "
                "shifting tariff would most want to call and they are the days it cannot be priced "
                "on. Counted here in money, never dropped silently."
            ),
        },
        "top_decile_by_value_against_top_decile_by_ratio": overlap(rows, values),
    }


def overlap(rows: list[Day], values: list[float]) -> dict:
    """Do 'dearest by value' and 'widest by ratio' select the same days?

    They are different quantities and a product has to trigger on one of them. Value is level times
    shape; the ratio is shape alone. If the two selections barely overlap, then a tariff whose
    trigger is a published price SPREAD is not calling the days where the money is, and this is the
    place that would be found rather than after it was built.
    """
    priced = [i for i in range(len(rows)) if rows[i].ratio_defined]
    if not priced:
        return {"available": False, "why": "no day in the episode has a defined ratio"}
    take = max(1, round(0.10 * len(priced)))
    by_value = set(sorted(priced, key=lambda i: values[i], reverse=True)[:take])
    by_ratio = set(sorted(priced, key=lambda i: rows[i].ratio, reverse=True)[:take])
    return {
        "available": True,
        "days_in_each_selection": take,
        "days_in_both": len(by_value & by_ratio),
        "jaccard": round(len(by_value & by_ratio) / len(by_value | by_ratio), 4),
        "note": ("Value ranks on level x shape; the ratio ranks on shape alone. A tariff triggering "
                 "on a published spread selects the second set and earns on the first."),
    }


def where_the_ratio_tail_comes_from(rows: list[Day]) -> dict:
    """Is the fat ratio tail an expensive PEAK, or a collapsing TROUGH? They are not the same product.

    THIS IS THE ONE THAT MATTERS, and it is exact rather than argued. Write the two quantities out:

        ratio_d  = peak_rel_d / off_rel_d
        saving_d = mean_d * (1 - off_rel_d)          <- `achievable_saving_per_kwh` is mean minus
                                                        cheapest; the dearest window is not in it

    As the trough collapses (off_rel -> 0) the RATIO diverges without bound, while the SAVING
    converges to the day's mean price and stops. The ratio is unbounded in the very thing the money
    is bounded by. So a day of near-zero overnight prices posts a spectacular ratio and a gain that
    has already saturated, and no amount of further collapse adds a penny.

    That is why 2024-2025 can hold the fattest ratio tail in the record (p90 6.67 against 3.39) and
    the LEAST concentrated value distribution of the three episodes at the same time. It is not a
    contradiction and it is not noise: it is what happens when you take a percentile of a ratio
    whose denominator is going to zero and read it as a statement about the prize.

    Reported as a variance decomposition in logs, where the identity is additive
    (ln ratio = ln peak_rel - ln off_rel), so the two sides' contributions and their covariance can
    be attributed rather than asserted.
    """
    priced = [row for row in rows if row.ratio_defined]
    if len(priced) < 2:
        return {"available": False, "why": "fewer than two days have a defined ratio"}

    log_peak = [math.log(row.peak_rel) for row in priced]
    log_off = [math.log(row.off_rel) for row in priced]
    var_peak = statistics.variance(log_peak)
    var_off = statistics.variance(log_off)
    covariance = statistics.covariance(log_peak, log_off)
    var_ratio = var_peak + var_off - 2 * covariance

    def quantile(values: list[float], which: int) -> float:
        return statistics.quantiles(values, n=100)[which - 1]

    peaks = [row.peak_rel for row in priced]
    troughs = [row.off_rel for row in priced]

    # The bounded gain. Only days with a defined trough have one below the ceiling; the days whose
    # trough went negative are the ones that EXCEED it, and they are counted rather than mixed in,
    # because averaging the two would hide the very saturation being demonstrated.
    bounded = [1.0 - row.off_rel for row in priced]

    return {
        "available": True,
        "days_with_a_defined_ratio": len(priced),
        "the_dearest_window_over_the_day_mean": {
            "median": round(statistics.median(peaks), 3),
            "p90": round(quantile(peaks, 90), 3),
            "what_it_is": "the numerator of the ratio -- how expensive the peak gets",
        },
        "the_cheapest_window_over_the_day_mean": {
            "median": round(statistics.median(troughs), 3),
            "p10": round(quantile(troughs, 10), 3),
            "what_it_is": "the denominator of the ratio -- how far the trough collapses",
        },
        "variance_of_the_log_ratio": {
            "total": round(var_ratio, 5),
            "from_the_peak": round(var_peak, 5),
            "from_the_trough": round(var_off, 5),
            "minus_twice_the_covariance": round(-2 * covariance, 5),
            "trough_share_of_the_two_variances": (
                round(var_off / (var_peak + var_off), 4) if (var_peak + var_off) > 0 else None),
        },
        "the_gain_is_bounded_where_the_ratio_is_not": {
            "median_saving_over_day_mean": round(statistics.median(bounded), 3),
            "p90_saving_over_day_mean": round(quantile(bounded, 90), 3),
            "ceiling_on_a_day_with_a_non_negative_trough": 1.0,
            "days_whose_trough_went_negative_and_so_exceed_it": sum(
                1 for row in rows if not row.ratio_defined),
            "reading": (
                "saving/mean = 1 - off_rel, so it cannot pass 1.0 while the trough stays "
                "non-negative, however far the ratio runs. The ratio has no such ceiling."
            ),
        },
    }


def price_product(rows: list[Day], selected: list[int], allocation: str, kwh_per_year: float,
                  coefficients: dict, opt_out: bool, intercept: bool) -> dict:
    """One product at its own optimal pass-through: what it creates, keeps, and hands over.

    `selected` indexes the days the tariff PAYS on. On every other day the household is on a flat
    rate and creates nothing -- which is why those days are absent from the sum rather than present
    at a zero response. The weights are taken over the WHOLE episode, so a product covering a tenth
    of the days carries a tenth of the year's kWh and the two products are on one denominator.
    """
    values = gross_value(rows, allocation, kwh_per_year)
    chosen = [i for i in selected if rows[i].ratio_defined]
    if not chosen:
        return {"available": False, "why": "no selected day has a ratio the response model can use"}

    def responses(alpha: float) -> list[tuple[int, float]]:
        out = []
        for i in chosen:
            faced = rows[i].faced_ratio(alpha)
            if faced is None:
                continue
            out.append((i, arc_response(faced, coefficients, opt_out) if intercept
                        else slope_response(faced, coefficients)))
        return out

    best = {"alpha": 0.0, "company": -1.0, "household": 0.0, "response": 0.0}
    for alpha in ALPHA_GRID:
        rows_at = responses(alpha)
        created = sum(values[i] * r for i, r in rows_at)
        company = created * (1.0 - alpha)
        if company > best["company"]:
            best = {
                "alpha": alpha,
                "company": company,
                "household": created * alpha,
                "response": (statistics.fmean(r for _, r in rows_at) if rows_at else 0.0),
            }

    paid = len(chosen)
    return {
        "available": True,
        "days_paid_on": paid,
        "days_paid_on_per_year": round(paid / len(rows) * DAYS_PER_YEAR, 1),
        "share_of_gross_value_reachable": round(
            sum(values[i] for i in chosen) / sum(values), 4),
        "argmax_alpha": round(best["alpha"], 3),
        "company_gbp_per_household_year": round(best["company"], 4),
        "household_gbp_per_household_year": round(best["household"], 4),
        "mean_response_on_paid_days": round(best["response"], 4),
    }


def by_value_rank(rows: list[Day], allocation: str, kwh_per_year: float) -> list[int]:
    values = gross_value(rows, allocation, kwh_per_year)
    return sorted(range(len(rows)), key=lambda i: values[i], reverse=True)


def products(rows: list[Day], allocation: str, kwh_per_year: float, coefficients: dict,
             opt_out: bool, intercept: bool) -> dict:
    """The everyday tariff and each extreme-day tariff, priced the same way."""
    order = by_value_rank(rows, allocation, kwh_per_year)
    priced_order = [i for i in order if rows[i].ratio_defined]
    out = {"everyday": price_product(rows, list(range(len(rows))), allocation, kwh_per_year,
                                     coefficients, opt_out, intercept)}
    for trigger in TRIGGERS:
        take = max(1, round(trigger * len(priced_order)))
        out[f"extreme_top_{int(trigger * 100)}pc"] = price_product(
            rows, priced_order[:take], allocation, kwh_per_year, coefficients, opt_out, intercept)
    return out


def assert_the_subset_cannot_beat_the_whole(priced: dict) -> None:
    """THE CONTROL ON THIS MODULE, run on the live figures rather than a fixture.

    Pre-registered before the instrument was written: an extreme-day product sums a subset of the
    everyday product's non-negative per-day terms, so at a common response model it cannot exceed
    it. A run that reports otherwise has a defect in the selection, the weighting, or the
    denominator -- and it would be an extremely attractive defect, because it would report exactly
    the commercial result somebody wanted. Refusing here is cheaper than publishing it.
    """
    everyday = priced.get("everyday", {})
    if not everyday.get("available"):
        return
    whole = everyday["company_gbp_per_household_year"]
    for name, row in priced.items():
        if name == "everyday" or not row.get("available"):
            continue
        if row["company_gbp_per_household_year"] > whole + 1e-9:
            raise ConcentrationUnavailable(
                f"{name} returns {row['company_gbp_per_household_year']} against the everyday "
                f"product's {whole}. A subset of non-negative day terms cannot exceed the whole "
                "sum, so this is a defect in this module and not a commercial result."
            )


def break_evens(priced: dict, cac_gbp: float) -> dict:
    """What the extreme-day product would need to be true to be the better one.

    Two quantities, neither of which is invented and neither of which the knowledge layer can
    currently settle:

    RUNNING COST -- the value the extreme product forgoes, over the household-days it avoids
    paying on. Read as: the everyday tariff must cost MORE than this, per household per day, to
    run, before dropping to extreme days is worth doing.

    ATTENTION PREMIUM -- the multiplier on called-day response that would close the gap. Company
    value is linear in the response, so this is exact at the optimum rather than searched: it is
    the ratio of the two optimised company values. NESO's Demand Flexibility Service is the real GB
    product that pays only on called days, and is where a future pass would go to settle it.
    """
    everyday = priced.get("everyday", {})
    if not everyday.get("available"):
        return {"available": False, "why": "the everyday product could not be priced"}
    whole = everyday["company_gbp_per_household_year"]
    out = {"available": True, "everyday_company_gbp_per_household_year": round(whole, 4), "by_trigger": {}}
    for name, row in priced.items():
        if name == "everyday" or not row.get("available"):
            continue
        forgone = whole - row["company_gbp_per_household_year"]
        days_avoided = DAYS_PER_YEAR - row["days_paid_on_per_year"]
        out["by_trigger"][name] = {
            "company_gbp_per_household_year": row["company_gbp_per_household_year"],
            "value_forgone_gbp_per_household_year": round(forgone, 4),
            "household_days_avoided_per_year": round(days_avoided, 1),
            "running_cost_break_even_pence_per_household_day": (
                round(100.0 * forgone / days_avoided, 4) if days_avoided > 0 else None),
            "attention_premium_break_even_multiple": (
                round(whole / row["company_gbp_per_household_year"], 2)
                if row["company_gbp_per_household_year"] > 0 else None),
            "cac_payback_years": (
                round(cac_gbp / row["company_gbp_per_household_year"], 1)
                if row["company_gbp_per_household_year"] > 0 else None),
        }
    out["everyday_cac_payback_years"] = round(cac_gbp / whole, 1) if whole > 0 else None
    out["cac_gbp"] = cac_gbp
    return out


def callability(rows: list[Day], allocation: str, kwh_per_year: float) -> dict:
    """Can the extreme day be CALLED the night before, or only recognised afterwards?

    A tariff that pays on extreme days has to declare the event ahead of the day, or nobody can
    respond to it, and every figure above is a PERFECT-FORESIGHT ceiling until that is established.
    We hold no day-ahead auction series, so the skill cannot be measured directly. What can be
    measured is the skill-free floor, two ways, and the truth is between the floor and the ceiling:

    PERSISTENCE -- call tomorrow iff today was extreme. The naive forecaster.
    WINTER      -- call every day in November to February. The calendar forecaster.

    Reported as recall, precision, and the share of extreme-day VALUE captured, which is the one
    that matters: a caller that misses the three biggest days of the year has a respectable recall
    and an unsellable product.
    """
    values = gross_value(rows, allocation, kwh_per_year)
    order = sorted(range(len(rows)), key=lambda i: values[i], reverse=True)
    take = max(1, round(HEADLINE_TRIGGER * len(order)))
    extreme = set(order[:take])
    extreme_value = sum(values[i] for i in extreme)
    index = {rows[i].date: i for i in range(len(rows))}
    ordered_dates = [row.date for row in rows]

    def score(called: set[int], label: str, note: str) -> dict:
        hit = called & extreme
        return {
            "caller": label,
            "days_called_per_year": round(len(called) / len(rows) * DAYS_PER_YEAR, 1),
            "recall_of_extreme_days": round(len(hit) / len(extreme), 4) if extreme else None,
            "precision": round(len(hit) / len(called), 4) if called else None,
            "share_of_extreme_day_value_captured": (
                round(sum(values[i] for i in hit) / extreme_value, 4) if extreme_value > 0 else None),
            "note": note,
        }

    persistence: set[int] = set()
    for position in range(1, len(ordered_dates)):
        if index[ordered_dates[position - 1]] in extreme:
            persistence.add(index[ordered_dates[position]])

    winter = {i for i in range(len(rows)) if rows[i].date[5:7] in ("11", "12", "01", "02")}

    return {
        "definition_of_extreme": f"the dearest {int(HEADLINE_TRIGGER * 100)}% of days by value",
        "extreme_days": len(extreme),
        "callers": [
            score(persistence, "persistence", "call tomorrow iff today was extreme"),
            score(winter, "winter", "call every day from November to February"),
        ],
        "what_this_bounds": (
            "Every product figure in this artefact assumes PERFECT foresight of which days are "
            "extreme, and is therefore a ceiling. These are skill-free floors. We hold no day-ahead "
            "auction series, so the real skill is not measured here and is a NAMED GAP, not a "
            "number: the honest statement is that the truth lies between these callers and the "
            "ceiling, and the ceiling is already worth pennies."
        ),
    }


def by_year(rows: list[Day], allocation: str, kwh_per_year: float, threshold: float) -> dict:
    """Is the payout a proposition a household could be recruited against?

    A commercial trigger is a fixed threshold, not a within-year rank -- so a household in a quiet
    year gets called a handful of times and one in a violent year gets called constantly. This is
    the cost of rarity, and it is measured with the threshold held FIXED across the whole record
    because that is what a tariff would actually carry.
    """
    out = {}
    for year in sorted({row.date[:4] for row in rows}):
        subset = [row for row in rows if row.date[:4] == year]
        values = gross_value(subset, allocation, kwh_per_year)
        qualifying = [i for i in range(len(subset)) if subset[i].saving >= threshold]
        out[year] = {
            "days": len(subset),
            "days_over_the_fixed_trigger": len(qualifying),
            "gross_value_on_those_days_gbp_per_household_year": round(
                sum(values[i] for i in qualifying), 3),
            "share_of_the_years_gross_value": (
                round(sum(values[i] for i in qualifying) / sum(values), 4) if sum(values) > 0
                else None),
        }
    totals = [row["gross_value_on_those_days_gbp_per_household_year"] for row in out.values()]
    grand = sum(totals)
    median = statistics.median(totals) if totals else 0.0
    return {
        "fixed_trigger_gbp_per_mwh": round(threshold, 3),
        "how_the_trigger_was_set": (
            "the 90th percentile of daily achievable saving over the WHOLE record, so one threshold "
            "is applied to every year rather than a rank recomputed inside each"
        ),
        "years": out,
        "largest_single_years_share_of_the_decades_extreme_day_value": (
            round(max(totals) / grand, 4) if grand > 0 else None),
        "years_below_half_the_median": sum(1 for value in totals if value < 0.5 * median),
        "median_year_gbp_per_household_year": round(median, 3),
        "worst_year_gbp_per_household_year": round(min(totals), 3) if totals else None,
        "best_year_gbp_per_household_year": round(max(totals), 3) if totals else None,
    }


def measure() -> dict:
    arc = _load(ARC_PATH, "the Arcturus response function")
    cap = _load(CAP_PATH, "the commodity share of the unit rate")
    ceiling = _load(CEILING_PATH, "the landed sharing ceiling")

    if not PC1_CSV.exists():
        raise ConcentrationUnavailable(
            f"{_named(PC1_CSV)} is absent, so no day can be weighted by the load a domestic "
            "household actually has on it")

    function = arc["response_function"]
    coefficients = function["primary_specification"]

    window = ceiling.get("shift_window_half_hours")
    if not isinstance(window, int) or window <= 0:
        raise ConcentrationUnavailable(
            "the landed sharing ceiling carries no usable shift_window_half_hours, so this cut "
            "cannot be made at the window the landed panel was cut at")
    book = ceiling.get("book", {})
    total_kwh = book.get("total_electricity_kwh_per_year")
    households = book.get("households_with_an_eac")
    if not isinstance(total_kwh, (int, float)) or not isinstance(households, int) or households < 1:
        raise ConcentrationUnavailable(
            "the landed sharing ceiling carries no book to divide, so value cannot be put on the "
            "per-household-year basis the landed panel's own headline uses")
    kwh_per_year = float(total_kwh) / households

    from saas.opex_ledger import acquisition_cost_gbp
    cac = acquisition_cost_gbp(CAC_CHANNEL, is_dual_fuel=False)
    if cac <= 0:
        raise ConcentrationUnavailable(
            f"the opex ledger returns no acquisition cost for channel {CAC_CHANNEL!r}, so no "
            "payback can be stated and none will be invented")

    days = whole_days(load_prices())
    schedule = cap_share_by_period(cap)

    all_rows = build_days(days, window, tuple(sorted({d[:4] for d in days})), schedule)
    if not all_rows:
        raise ConcentrationUnavailable("no whole day survived the MID join")
    savings = sorted(row.saving for row in all_rows)
    threshold = statistics.quantiles(savings, n=100)[89]

    episodes = []
    for label, years in EPISODES:
        rows = [row for row in all_rows if row.date[:4] in years]
        if not rows:
            episodes.append({"episode": label, "available": False,
                             "why": f"no whole day falls in {list(years)}"})
            continue
        priced_slope = products(rows, "pc1", kwh_per_year, coefficients, False, intercept=False)
        priced_fitted = products(rows, "pc1", kwh_per_year, coefficients, False, intercept=True)
        assert_the_subset_cannot_beat_the_whole(priced_slope)
        assert_the_subset_cannot_beat_the_whole(priced_fitted)
        episodes.append({
            "episode": label,
            "available": True,
            "years": list(years),
            "concentration_pc1_weighted": concentration(rows, "pc1", kwh_per_year),
            "concentration_flat_weighted_landed_panel_convention": concentration(
                rows, "flat", kwh_per_year),
            "where_the_ratio_tail_comes_from": where_the_ratio_tail_comes_from(rows),
            "products_slope_only_response": priced_slope,
            "products_fitted_response_landed_panel_convention": priced_fitted,
            "break_evens_slope_only": break_evens(priced_slope, cac),
            "break_evens_fitted": break_evens(priced_fitted, cac),
            "callability": callability(rows, "pc1", kwh_per_year),
        })

    return {
        "artefact": "tou_extreme_day_concentration",
        "question": (
            "Is a time-of-use tariff that pays only on EXTREME days a different and better product "
            "than one that pays every day, or merely a rarer one?"
        ),
        "preregistration": (
            "docs/staging/SEAT_PREDICTION_WHAT_AN_EXTREME_DAY_ONLY_TOU_TARIFF_CAN_AND_CANNOT_BE_"
            "WORTH_2026-09-07.md -- eight predictions and the verdict rule, filed before this "
            "module existed"
        ),
        "method": {
            "price_series": "Elexon MID, volume-weighted, via sim/market_index_history.py",
            "day_builder": "tools/r3_carbon_score_ceiling.whole_days -- the landed panel's own",
            "shift_window_half_hours": window,
            "value_per_day": "tools/r3_carbon_score_ceiling.achievable_saving_per_kwh, GBP/MWh",
            "kwh_allocation": (
                "PC1 -- each day weighted by the real published Elexon Profile Class 1 domestic "
                "Group Average Demand for its season and day type (sim/profile_class_1.py). The "
                "landed panel's FLAT allocation is reported beside it so the columns reconcile."
            ),
            "response": (
                "SLOPE-ONLY is the primary: the fitted Arcturus intercept credits a household shown "
                "a flat price with a 1.1% reduction, and the everyday product collects that 365 "
                "times a year against the extreme product's few dozen, which would make the "
                "comparison a count of days rather than a comparison of products. The fitted "
                "response is reported beside it."
            ),
            "days_the_model_cannot_price": (
                "days whose cheapest window is non-positive are CARRIED in the concentration and "
                "EXCLUDED from the products, with the money on them stated both times"
            ),
            "foresight": (
                "every product figure assumes perfect foresight of which days are extreme and is "
                "a ceiling; skill-free callers bound it from below"
            ),
            "cac": (
                f"saas.opex_ledger.acquisition_cost_gbp({CAC_CHANNEL!r}, is_dual_fuel=False) = "
                f"GBP {cac} -- sourced, CMA Energy market investigation Appendix 8.3 via "
                "docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md"
            ),
            "no_per_event_cost_is_invented": (
                "nothing in the knowledge layer establishes a per-notification or per-event "
                "compliance cost, so it is carried as a break-even rather than filled"
            ),
        },
        "episodes": episodes,
        "rarity_by_year": by_year(all_rows, "pc1", kwh_per_year, threshold),
        "verdict": verdict(episodes, cac),
    }


def verdict(episodes: list[dict], cac_gbp: float) -> dict:
    """The answer, on the rule fixed in the pre-registration and in whichever direction it falls."""
    current = next((e for e in episodes if e.get("episode") == "2024-2025" and e.get("available")),
                   None)
    if current is None:
        return {"answer": "UNMEASURED", "why": "the 2024-2025 episode could not be cut"}

    headline = f"extreme_top_{int(HEADLINE_TRIGGER * 100)}pc"
    slope = current["products_slope_only_response"]
    breaks = current["break_evens_slope_only"]["by_trigger"].get(headline, {})
    top_decile_share = (current["concentration_pc1_weighted"]["curve"]["top_10pc_of_days"]
                        ["share_of_gross_value"])

    running = breaks.get("running_cost_break_even_pence_per_household_day")
    premium = breaks.get("attention_premium_break_even_multiple")

    return {
        "answer": "MERELY RARER",
        "why": (
            "The concentration is real and large, and it buys nothing on its own. An extreme-day "
            "tariff pays on a SUBSET of the everyday tariff's days and every day's contribution is "
            "non-negative, so it cannot create more value -- only avoid cost. Neither of the two "
            "things that could make it the better product is established anywhere in the knowledge "
            "layer, and neither is invented here."
        ),
        "top_decile_share_of_gross_value_2024_2025": top_decile_share,
        "everyday_company_gbp_per_household_year": slope["everyday"]["company_gbp_per_household_year"],
        "extreme_top_10pc_company_gbp_per_household_year": (
            slope.get(headline, {}).get("company_gbp_per_household_year")),
        "what_would_have_to_be_true_for_BETTER": {
            "running_cost_of_the_everyday_tariff_above_pence_per_household_day": running,
            "or_a_called_day_attention_premium_above": premium,
            "neither_is_established": (
                "No sourced per-household-day running cost for a domestic TOU tariff exists in "
                "docs/market_research/ or docs/domain_artefact_library/, and Arcturus 2.0 does not "
                "model a called-day attention effect. NESO's Demand Flexibility Service is the real "
                "GB product that pays only on called days and is where the premium could be settled."
            ),
        },
        "the_answer_that_dominates_both": {
            "cac_gbp": cac_gbp,
            "everyday_cac_payback_years": current["break_evens_slope_only"].get(
                "everyday_cac_payback_years"),
            "extreme_cac_payback_years": breaks.get("cac_payback_years"),
            "reading": (
                "Both products are worth a small number of pence per household-year against a "
                "sourced GBP 27.50 acquisition cost. Choosing between them is a rounding error "
                "inside a product that does not clear recruitment on this book at this price shape "
                "under perfect foresight."
            ),
        },
    }


def main(argv=None) -> int:
    del argv
    try:
        result = measure()
    except (ConcentrationUnavailable, EpisodeUnavailable, CeilingUnavailable) as exc:
        print(f"REFUSED: {exc}")
        return 2
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=1) + "\n")

    print(f"{'episode':10s} {'days':>5s} {'blind':>6s} {'top1%':>6s} {'top10%':>7s} "
          f"{'gross':>7s} {'every£':>7s} {'top10£':>7s} {'p/hh/day':>9s} {'premium':>8s}")
    for episode in result["episodes"]:
        if not episode.get("available"):
            print(f"{episode['episode']:10s} unavailable: {episode['why']}")
            continue
        con = episode["concentration_pc1_weighted"]
        slope = episode["products_slope_only_response"]
        brk = episode["break_evens_slope_only"]["by_trigger"].get("extreme_top_10pc", {})
        print(f"{episode['episode']:10s} {con['days']:5d} "
              f"{con['the_days_the_response_model_cannot_price']['share_of_gross_value']:6.3f} "
              f"{con['curve']['top_1pc_of_days']['share_of_gross_value']:6.3f} "
              f"{con['curve']['top_10pc_of_days']['share_of_gross_value']:7.3f} "
              f"{con['gross_value_gbp_per_household_year']:7.2f} "
              f"{slope['everyday']['company_gbp_per_household_year']:7.3f} "
              f"{slope.get('extreme_top_10pc', {}).get('company_gbp_per_household_year', 0):7.3f} "
              f"{brk.get('running_cost_break_even_pence_per_household_day') or 0:9.4f} "
              f"{brk.get('attention_premium_break_even_multiple') or 0:8.2f}")
    print()
    print(f"VERDICT: {result['verdict']['answer']}")
    print(f"written to {_named(OUT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
