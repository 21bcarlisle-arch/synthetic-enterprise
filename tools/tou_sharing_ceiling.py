"""THE SHARING CEILING — what a time-of-use tariff could be worth, and to whom, before one exists.

REUSE: tools/tou_sharing_ceiling.py
CLASS: CUSTOM
INDEX: searched "ceiling", "bound", "time of use", "tariff", "sharing", "pass-through",
       "shift", "wholesale price", "half-hourly price". Eight ceiling instruments exist and none
       bounds this: five are EP13's dispatch bounds, one is R1's inference bound, one is R3's
       carbon bound and one is R4's product bound. R4's `tariff_fit` arm is the nearest and is a
       DIFFERENT quantity -- it bounds moving a household to a better FLAT rate, which the
       director's standing rule scores at exactly zero carbon; this bounds moving a household's
       load in TIME, which is the only lever that abates. THE WORLD SIDE IS NOT REIMPLEMENTED:
       `whole_days`, `achievable_saving_per_kwh` and `skill_free_saving_per_kwh` are imported from
       `tools/r3_carbon_score_ceiling.py` unchanged, deliberately, because this instrument's whole
       claim is that it measures THE SAME ACT R3 measures in the other currency, and the same act
       has to be the same code or the comparison is two constructions wearing one name. The price
       series is `sim/market_index_history.py`'s Elexon MID join, volume-weighted, reused rather
       than re-fetched -- it already carries the two live fail-opens that series has. R3's
       `share_curve` is the one thing deliberately NOT reused: it publishes a carbon column beside
       the money one, and this instrument has no carbon of its own to put in it. Filling it with
       0.0 would render as a measured zero.

WHY THIS EXISTS
---------------
`docs/staging/SEAT_FINDING_R3_MEASURES_VALUE_CREATED_AND_THIS_BOOK_HAS_NO_INSTRUMENT_OF_SHARING_IT_2026-09-07.md`,
found by putting R3's and R4's readings side by side:

    R3 bounds what perfect timing advice could ABATE -- 91.7 kgCO2e per household-year, £4.03 at
    the DESNZ traded carbon value, at a shiftable share of 1.0. R4 then has to place that in a
    product column and cannot: its `time_shifting` arm reports `gbp_per_household_year: None`,
    because a shifted kWh is cheaper only on a time-of-use tariff and THIS BOOK HOLDS NONE.

So the lever that abates has no bill-saving ceiling at all, and the lever that saves money abates
exactly zero. The value is created and there is no mechanism through which any of it is shared.
That is the mission's own first consequence -- *value is created and THEN shared, so every decision
has two sides* -- arriving as a missing product.

A time-of-use tariff is a programme, not an atom: it touches pricing, billing, the renewal path and
the customer's decision model. A49's discipline is that the ceiling comes first, and this is that
discipline applied to the gap A49's own instruments exposed. EP13 paid twelve passes to learn it.

WHAT THIS BOUNDS, AND THE DEFINITION IT INSISTS ON FIRST
---------------------------------------------------------
Two quantities, and conflating them is the failure this instrument exists to avoid:

  CREATED   The wholesale energy cost avoided when a kWh is drawn in the day's cheapest window
            instead of at the day's average price. The supplier buys less expensive electricity;
            in a merit-order market that is cheaper plant running instead of dearer plant, which is
            a real resource saving and not a transfer. A CEILING: the company holds both sides of
            the subtraction -- the half-hourly traded price it buys at, and its own EAC.

  SHARED    How that created value is split between the household's bill and the company's margin,
            through the tariff's PASS-THROUGH. This is NOT a bound and is never reported as one.
            It is an identity: the two shares sum to the created value at every pass-through.
            Sharing does not create value; it allocates it. A negative here retires nothing,
            because there is nothing here to be negative.

THE ONE RESULT THAT NEEDS NO PARAMETER, and it is the reason the frontier is published as a
frontier. At zero pass-through a household's bill does not change when it shifts, so it has no money
reason to shift, so nothing moves and the company keeps a share of nothing. At full pass-through the
company keeps a share of everything, which is none of it. **The company's own take is zero at BOTH
ends, so for any response that rises with pass-through its maximum is strictly interior.** No
elasticity is asserted, because none is established; the conclusion does not need one. Where the
interior optimum sits does need one, and that is a named gap rather than a number.

WHO CAN BE ON SUCH A TARIFF AT ALL, which is measured and not assumed. A time-of-use tariff needs
half-hourly settlement, which needs a smart meter. `meter_read_log.meter_type` says which households
have one, so the reachable population is COUNTED from the book. Every book-level figure here is over
that population and says so; the per-household figure is published over R3's denominator as well, so
the two instruments' columns can be read against each other without dividing two different books.

THE TWO ERRORS, IN OPPOSITE DIRECTIONS, both named because publishing only the flattering one is how
a ceiling becomes a sales figure:

  OVERSTATES  The price differential between two half hours is producer surplus PLUS the resource
              saving, and only the second is created value. This bound cannot separate them, so it
              is an upper bound on the creation as well as on the money.
  UNDERSTATES The counterfactual is the day's MEAN price, matching R3 exactly so the two columns
              are the same act. Households actually draw disproportionately in the evening peak,
              when the price is above the day's mean, so the real avoided cost is larger. And only
              the WHOLESALE leg is counted: avoided red-band DUoS, triad and capacity costs are
              real ToU value and are out of scope here.
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

from tools.r3_carbon_score_ceiling import (  # noqa: E402
    MIN_DAYS,
    MIN_HOUSEHOLDS,
    NULL_DRAWS,
    SHARE_CURVE,
    CeilingUnavailable,
    achievable_saving_per_kwh,
    book_run_output,
    electricity_eac,
    shift_window,
    skill_free_saving_per_kwh,
    whole_days,
)

OUT_PATH = PROJECT / "docs" / "observability" / "tou_sharing_ceiling.json"
R3_ARTEFACT = PROJECT / "docs" / "observability" / "r3_carbon_score_ceiling.json"
INTENSITY_FEED = PROJECT / "docs" / "market_data" / "grid_intensity_feed.json"

#: The pass-throughs the sharing frontier is PRINTED at. NOT a domain constant and nothing here
#: claims any of them: a tariff's pass-through is a commercial decision nobody has taken on this
#: book, so there is no established value to cite and none is invented. This is a print grid, the
#: same move R3 makes with `SHARE_CURVE` for the shiftable share it also cannot source.
PASS_THROUGH_GRID = (0.0, 0.25, 0.50, 0.75, 1.00)

#: Subsamples drawn when the null is recomputed at R3's panel size. Enough for a median and a
#: worst case, and it costs about a second. The MATCHED-PANEL ratio is the only clearance figure
#: this instrument permits to be read against R3's, for the reason `matched_panel_clearance` gives.
MATCHED_PANEL_DRAWS = 60

BOUND_KIND = "CEILING on the created value; the SPLIT is a FRONTIER and is not a bound at all"
BOUND_KIND_REASON = (
    "TRUE CEILING on what a time-of-use tariff could create. The company holds both sides of the "
    "subtraction -- the half-hourly traded wholesale price it buys at, and its own EAC -- and "
    "perfect foreknowledge of the day's price shape with every kWh moved is exactly the quantity a "
    "real tariff and real compliance approximate. Nothing buildable beats it, so a reading at or "
    "below the null RETIRES the time-of-use product outright. The pass-through split is a "
    "different kind of statement: the household's share and the company's share sum to the created "
    "value at every pass-through BY CONSTRUCTION, so a negative there is not possible and retires "
    "nothing. Sharing does not create value; it allocates it."
)
BOUND_SCOPE = (
    "The WHOLESALE ENERGY cost of moving domestic load within the day, on the ELECTRICITY book "
    "only. It bounds nothing about network charges, capacity, imbalance, gas, consumption "
    "reduction or physical measures."
)

#: Every direction of error this instrument knows about, with the direction stated. STRUCTURED
#: rather than prose because a control can read a direction and cannot read a paragraph, and
#: because an instrument that published only its understatements would be a sales figure.
KNOWN_ERRORS = (
    {
        "direction": "overstates",
        "what": (
            "The price differential between two half hours is producer surplus PLUS the resource "
            "saving from dispatching cheaper plant. Only the second is value CREATED; the first is "
            "value moved from a generator to the supplier. This bound cannot separate them, so it "
            "is an upper bound on the creation as well as on the money."
        ),
    },
    {
        "direction": "overstates",
        "what": (
            "The price shape is exogenous here. A book-wide shift would itself flatten the "
            "differential it is paid out of. At this book's size against ~28M GB homes that is "
            "negligible, and at national scale it is not -- which makes this a ceiling for THIS "
            "company and not for the policy."
        ),
    },
    {
        "direction": "understates",
        "what": (
            "The counterfactual is the DAY'S MEAN price, chosen to match R3's construction exactly "
            "so the money and carbon columns describe the same act. Households draw "
            "disproportionately in the evening peak, above the day's mean, so the cost actually "
            "avoided by moving their load is larger than this."
        ),
    },
    {
        "direction": "understates",
        "what": (
            "Only the WHOLESALE leg is counted. Avoided red-band DUoS, triad exposure and capacity "
            "costs are real value a time-of-use tariff creates and none of them is in this figure."
        ),
    },
    {
        "direction": "understates",
        "what": (
            "The panel is Elexon MID, which this repository holds from 2016-09 to 2020-12. It ends "
            "before the 2021-2023 price episode, when within-day differentials were far wider than "
            "anything in this window. A ceiling measured on calm years is not the ceiling of the "
            "years that followed."
        ),
    },
)


# --------------------------------------------------------------------------------------------
# The world side: what the day's price shape makes available to a household that can move load.
# --------------------------------------------------------------------------------------------

def half_hourly_wholesale_price() -> dict[tuple[str, int], float]:
    """(date, settlement period) -> the volume-weighted traded wholesale price, GBP/MWh.

    ELEXON MID, read from `sim/market_index_history.py`'s own cache and its own join. Re-deriving
    the join here would have re-derived its two measured fail-opens with it: a too-wide window that
    returns HTTP 200 with an empty list, and a reporting provider that publishes 0.00 on volume 0.00
    across four whole years. A naive mean across providers halves every price in the series.

    THIS DOES NOT CROSS THE EPISTEMIC WALL, and the question is worth asking of it rather than
    assumed: the traded wholesale price is the price a real GB supplier BUYS AT and Elexon publishes
    it. It is an observable, not ground truth. This module is also in `tools/`, outside the company,
    and computes a counterfactual the company never sees the answer to.

    THE CACHE IS GITIGNORED, so this refuses in a clean worktree extract rather than reporting a
    book that cannot save anything. An instrument that goes quiet where the data is absent reports
    "measured nothing" as "measured, found nothing", and those are opposite claims.
    """
    from sim.market_index_history import (
        MarketIndexUnavailable,
        cache_present,
        load_cached_market_index,
        volume_weighted_mid,
    )

    if not cache_present():
        raise CeilingUnavailable(
            "the Elexon MID cache is not present in this tree, so there is no half-hourly price "
            "shape to bound against. It is gitignored, which is what a linked worktree extract "
            "looks like, and it is NOT a finding that the price shape offers nothing."
        )
    try:
        records = load_cached_market_index()
    except (MarketIndexUnavailable, OSError, ValueError) as exc:
        raise CeilingUnavailable(f"the Elexon MID cache could not be read: {exc}") from exc
    prices = volume_weighted_mid(records)
    if not prices:
        raise CeilingUnavailable(
            "the MID join returned no priced half hour. Every record carried zero or non-finite "
            "volume, which is the non-reporting-provider fail-open the join already guards, and it "
            "is a data absence rather than a market in which nothing traded."
        )
    return prices


def created_value_per_shifted_kwh(days: dict[str, list[float]], window: int, seed: int) -> dict:
    """The wholesale cost avoided per kWh moved into the day's cheapest window, GBP/MWh.

    THE SAME TWO FUNCTIONS R3 USES, on prices instead of intensity multipliers, because the claim
    this instrument makes is that it measures the same act in the other currency. If the world side
    were rewritten here the two columns would be two constructions sharing a name, and a reader
    comparing them would be comparing the code rather than the currencies.

    The null is the same one too, and it is the one that works: picking the window from a SHUFFLED
    day and scoring it on the REAL one. Re-running the optimiser on a shuffled day returns the
    ceiling exactly -- a permutation does not change a sorted list -- and would read as a
    spectacular confirmation of nothing.
    """
    rng = random.Random(seed)
    hindsight: list[float] = []
    null_draws: list[list[float]] = [[] for _ in range(NULL_DRAWS)]
    per_year: dict[str, list[float]] = {}
    mean_price: list[float] = []

    for date_str, day in sorted(days.items()):
        saving = achievable_saving_per_kwh(day, window)
        hindsight.append(saving)
        mean_price.append(statistics.fmean(day))
        per_year.setdefault(date_str[:4], []).append(saving)
        for draw in range(NULL_DRAWS):
            null_draws[draw].append(skill_free_saving_per_kwh(day, window, rng))

    null_means = sorted(statistics.fmean(d) for d in null_draws)
    return {
        "hindsight_gbp_per_mwh": statistics.fmean(hindsight),
        "null_max_gbp_per_mwh": null_means[-1],
        "null_mean_gbp_per_mwh": statistics.fmean(null_means),
        "mean_day_price_gbp_per_mwh": round(statistics.fmean(mean_price), 3),
        "by_year_gbp_per_mwh": {y: round(statistics.fmean(v), 4)
                                for y, v in sorted(per_year.items())},
        "days": len(days),
        "years": sorted(per_year),
        "days_by_year": {y: len(v) for y, v in sorted(per_year.items())},
    }


def matched_panel_clearance(days: dict[str, list[float]], window: int, panel: int,
                            seed: int) -> dict:
    """The clearance ratio this instrument WOULD have reported on a panel the size of R3's.

    THIS IS THE ONLY CLEARANCE FIGURE THAT MAY BE READ AGAINST R3'S, and the reason is arithmetic
    rather than caution. R3's null is the maximum over 200 draws of a mean taken over 20 days; this
    instrument's whole-panel null is a mean over 1,500-odd days. A mean over more days has a smaller
    sampling spread, so the maximum over draws falls as the panel grows FOR REASONS THAT HAVE
    NOTHING TO DO WITH SIGNAL. Publishing the two raw ratios side by side would invite a reader to
    compare two panel sizes and call it a comparison of two levers -- which is this project's most
    expensive recurring shape, one number over another number that does not divide it.

    So the ratio is recomputed the way R3 computed its own: a subsample of `panel` days, hindsight
    and null both taken over that subsample, repeated so subsample luck is visible as a spread
    rather than hidden in a point.
    """
    if panel < 1 or panel > len(days):
        return {
            "available": False,
            "why": (
                f"R3's panel is {panel} day(s) and this one is {len(days)}, so no matched "
                "subsample can be drawn. The whole-panel ratio then stands alone and must NOT be "
                "read against R3's."
            ),
        }
    rng = random.Random(seed)
    keys = sorted(days)
    ratios: list[float] = []
    for _ in range(MATCHED_PANEL_DRAWS):
        sample = rng.sample(keys, panel)
        hindsight = statistics.fmean([achievable_saving_per_kwh(days[k], window) for k in sample])
        null_max = max(
            statistics.fmean([skill_free_saving_per_kwh(days[k], window, rng) for k in sample])
            for _ in range(NULL_DRAWS)
        )
        ratios.append(hindsight / null_max if null_max > 0 else float("inf"))
    finite = [r for r in ratios if r != float("inf")]
    return {
        "available": True,
        "panel_days": panel,
        "draws": MATCHED_PANEL_DRAWS,
        "median_ratio": round(statistics.median(finite), 2) if finite else None,
        "worst_ratio": round(min(finite), 2) if finite else None,
        "best_ratio": round(max(finite), 2) if finite else None,
        "clears_in_every_draw": all(r > 1.0 for r in ratios),
        "what_it_means": (
            "What this instrument would have reported if it had had R3's panel. It is the figure "
            "to read against R3's, and the whole-panel ratio is NOT."
        ),
    }


# --------------------------------------------------------------------------------------------
# The book side: who could be on such a tariff at all.
# --------------------------------------------------------------------------------------------

def smart_metered_households(payload: dict) -> set[str]:
    """The households a time-of-use tariff could actually be sold to.

    COUNTED, NOT ASSUMED, and it is the constraint that decides the size of the whole programme: a
    time-of-use tariff is settled half-hourly, and half-hourly settlement needs a smart meter. A
    traditional meter does not record WHEN anything happened, so there is no shape to price against
    and no estimate recovers one -- `company/carbon/half_hourly_footprint.py` makes the same
    distinction on the carbon side and calls the traditional-meter state PROFILED, never zero.

    Secondary legs are excluded by `household_of` rather than by a string suffix, matching R3: a
    gas leg registered under its electricity point's id has no timing lever at all.
    """
    from simulation.household import household_of

    smart: set[str] = set()
    rows = payload.get("meter_read_log")
    if not (isinstance(rows, list) and rows):
        return smart
    for row in rows:
        cid = row.get("customer_id")
        if not cid or row.get("meter_type") != "smart":
            continue
        if household_of(str(cid)) != str(cid):
            continue
        smart.add(str(cid))
    return smart


# --------------------------------------------------------------------------------------------
# The sharing side.
# --------------------------------------------------------------------------------------------

def sharing_frontier(created_gbp_per_household_year: float) -> list[dict]:
    """How the created value divides, at each pass-through. AN IDENTITY, NOT A MEASUREMENT.

    The two shares sum to the created value at every row, by construction, and that IS the finding
    rather than an artefact of the arithmetic: sharing does not create value. A reader who wants to
    know how much a time-of-use tariff is worth TO THE COMPANY is asking a question whose answer is
    a commercial decision, and the frontier is the honest shape of that answer.
    """
    return [
        {
            "pass_through": alpha,
            "household_gbp_per_household_year": round(created_gbp_per_household_year * alpha, 4),
            "company_gbp_per_household_year": round(
                created_gbp_per_household_year * (1.0 - alpha), 4),
        }
        for alpha in PASS_THROUGH_GRID
    ]


def money_share_curve(gbp_at_full: float) -> list[dict]:
    """The created value across shiftable shares. Linear, so the curve is the honest publication.

    R3's `share_curve` is deliberately NOT reused here even though the arithmetic is the same: it
    publishes a `kg_co2e_per_household_year` column beside the money one, and this instrument has no
    carbon of its own to put in it. Filling that column with 0.0 would render as a measured zero,
    which is the opposite of the truth -- the same act abates exactly what R3 says it abates, and
    R3 is where that column is read from.
    """
    return [
        {"shiftable_share": share, "gbp_per_household_year": round(gbp_at_full * share, 4)}
        for share in SHARE_CURVE
    ]


def the_carbon_column(created_hindsight_gbp_per_household_year: float) -> dict:
    """R3's abatement, READ rather than recomputed, and placed beside the money without being added.

    Two implementations of one quantity is how a figure comes to have two values and no owner. It
    is also why this reads R3's HINDSIGHT rung and not its corrected headline: the money figure has
    no forecast handicap applied (there is no measured price-forecast capture in this repository to
    apply) and no within-day overstatement correction (the price series is traded, not
    reconstructed, so there is nothing to correct). Hindsight against hindsight is the only pair of
    rungs that describes the same assumption on both sides.
    """
    if not R3_ARTEFACT.exists():
        return {
            "available": False,
            "why": (
                f"{R3_ARTEFACT.name} is not present, so the carbon column has nothing to read. Run "
                "`python3 -m tools.r3_carbon_score_ceiling --save` first. This instrument will NOT "
                "recompute the quantity R3 owns."
            ),
        }
    r3 = json.loads(R3_ARTEFACT.read_text(encoding="utf-8"))
    rung = (r3.get("rungs") or {}).get("hindsight_ceiling") or {}
    carbon_gbp = rung.get("gbp_per_household_year")
    return {
        "available": True,
        "source": "tools/r3_carbon_score_ceiling.py — read, not recomputed",
        "rung": "hindsight_ceiling",
        "households": (r3.get("book") or {}).get("households"),
        "kg_co2e_per_household_year": rung.get("kg_co2e_per_household_year"),
        "carbon_value_gbp_per_household_year": carbon_gbp,
        "money_over_carbon": (
            round(created_hindsight_gbp_per_household_year / carbon_gbp, 2)
            if isinstance(carbon_gbp, (int, float)) and carbon_gbp > 0 else None
        ),
        "why_these_are_never_summed": (
            "The money column is a WHOLESALE COST AVOIDED and the carbon column is TONNES VALUED at "
            "the DESNZ traded price. Two correct figures whose sum is not a quantity is this "
            "project's most expensive recurring shape. They are the same act read in two "
            "currencies and they belong in two columns."
        ),
        "why_the_ratio_IS_a_quantity": (
            "Both are pounds per household-year over the same book, from the same act -- moving "
            "every kWh into the day's cleanest six half hours -- at the same shiftable share of "
            "1.0. So their RATIO says which column the case for a time-of-use tariff rests on, "
            "even though their SUM says nothing."
        ),
    }


def the_interior_optimum() -> dict:
    """The one conclusion about sharing that needs no parameter, stated where it can be checked."""
    return {
        "company_take_at_pass_through_0": (
            "ZERO. At no pass-through a household's bill is identical whenever it draws its "
            "electricity, so it has no MONEY reason to move any of it. Nothing moves, nothing is "
            "created, and the company keeps a share of nothing. This is not a modelling choice -- "
            "it is the state of this book today, which is exactly why R4's time-shifting arm "
            "reports no pounds."
        ),
        "company_take_at_pass_through_1": (
            "ZERO. Everything the shift creates reaches the household's bill and the company "
            "retains none of it."
        ),
        "therefore": (
            "The company's own take is zero at BOTH ends of the frontier, so for any shift "
            "response that increases with pass-through its maximum is STRICTLY INTERIOR. That "
            "conclusion needs no elasticity and none is asserted: it follows from the two "
            "endpoints alone."
        ),
        "what_it_does_NOT_say": (
            "Where the interior optimum is. That needs the shift response as a function of "
            "pass-through, and nothing in the knowledge layer, the commons or the market research "
            "establishes one. It is a question to research, not a number to pick."
        ),
        "the_one_thing_that_still_moves_at_zero_pass_through": (
            "Carbon. A household that shifts for the carbon abates exactly what R3 measures, and "
            "none of that value reaches anyone's bill, so it cannot be shared through a tariff at "
            "all. That is the finding this instrument was built out of, restated as arithmetic: "
            "the carbon is created and the tariff is the only mechanism this book could have for "
            "sharing what the same act creates in money."
        ),
    }


# --------------------------------------------------------------------------------------------
# The measurement.
# --------------------------------------------------------------------------------------------

def measure(run_path: Path | None = None, prices: dict | None = None,
            seed: int = 20260907) -> dict:
    """The whole instrument. Every path that cannot produce a number raises."""
    prices = prices if prices is not None else half_hourly_wholesale_price()
    days = whole_days(prices)
    if len(days) < MIN_DAYS:
        raise CeilingUnavailable(
            f"the price series yields {len(days)} whole day(s) and a distribution needs at least "
            f"{MIN_DAYS}. A ceiling over a handful of days is a handful of days."
        )

    feed = json.loads(INTENSITY_FEED.read_text(encoding="utf-8"))
    window = shift_window(feed)

    world = created_value_per_shifted_kwh(days, window, seed)

    run_path = run_path or book_run_output()
    payload = json.loads(run_path.read_text(encoding="utf-8"))
    eac = electricity_eac(payload)
    if len(eac) < MIN_HOUSEHOLDS:
        raise CeilingUnavailable(
            f"{run_path.name} carries {len(eac)} household(s) with an electricity EAC and this "
            f"instrument reports nothing under {MIN_HOUSEHOLDS}. That is a data-availability "
            "refusal and NOT a finding that a time-of-use tariff is worthless."
        )
    smart = smart_metered_households(payload)
    reachable = sorted(set(eac) & smart)

    hindsight = world["hindsight_gbp_per_mwh"]
    null = world["null_max_gbp_per_mwh"]
    total_kwh = sum(eac.values())
    reachable_kwh = sum(eac[c] for c in reachable)

    # PER HOUSEHOLD OVER R3'S DENOMINATOR, so the two instruments' columns divide the same book.
    # The BOOK figure is over the reachable population only, because nobody else can be sold the
    # tariff. Saying which is which is the whole of the discipline here.
    per_household = hindsight * total_kwh / 1000.0 / len(eac)

    reachable_bound = (
        {
            "available": True,
            "households": len(reachable),
            "share_of_eac_book": round(len(reachable) / len(eac), 4),
            "electricity_kwh_per_year": round(reachable_kwh, 1),
            "book_gbp_per_year": round(hindsight * reachable_kwh / 1000.0, 2),
            "gbp_per_reachable_household_year": round(
                hindsight * reachable_kwh / 1000.0 / len(reachable), 2),
        }
        if len(reachable) >= MIN_HOUSEHOLDS else
        {
            "available": False,
            "households": len(reachable),
            "why": (
                f"only {len(reachable)} household(s) carry BOTH an electricity EAC and a smart "
                f"meter, and no book-level figure is reported under {MIN_HOUSEHOLDS}. A "
                "time-of-use tariff needs half-hourly settlement, so this is the population the "
                "programme could reach -- and a book figure over a handful of homes reads like a "
                "measurement of the book."
            ),
        }
    )

    clears = hindsight > null
    return {
        "bound_kind": BOUND_KIND,
        "bound_kind_reason": BOUND_KIND_REASON,
        "bound_scope": BOUND_SCOPE,
        "measures": {
            "created": (
                "wholesale energy cost avoided by drawing a kWh in the day's cheapest window "
                "instead of at the day's mean price. A resource saving, bounded from above."
            ),
            "shared": (
                "how that created value divides between the household's bill and the company's "
                "margin at a given tariff pass-through. An identity, never a bound."
            ),
        },
        "price_series": {
            "source": "Elexon Market Index Data (MID), volume-weighted across reporting providers",
            "reader": "sim/market_index_history.py — reused, not re-derived",
            "days": world["days"],
            "years": world["years"],
            "days_by_year": world["days_by_year"],
            "mean_day_price_gbp_per_mwh": world["mean_day_price_gbp_per_mwh"],
            "why_it_is_not_corrected_like_R3s": (
                "R3 divides by the reconstructed intensity shape's own measured within-day "
                "overstatement. This series is TRADED PRICE, not a reconstruction, so there is no "
                "overstatement measured against a published counterpart and nothing to correct. "
                "That is a difference in the data, not a lower standard."
            ),
        },
        "shift_window_half_hours": window,
        "world": world,
        "book": {
            "source_run": run_path.name,
            "households_with_an_eac": len(eac),
            "smart_metered_households": len(smart),
            "reachable": len(reachable),
            "total_electricity_kwh_per_year": round(total_kwh, 1),
            "why_the_two_denominators_differ": (
                "The per-household figure divides R3's book so the two instruments' columns are "
                "over the same denominator. The BOOK figure divides only the households a "
                "half-hourly-settled tariff could actually be sold to. Publishing one number over "
                "two populations is how a ratio comes to be a quantity nobody defined."
            ),
        },
        "created_value": {
            "rung": "hindsight_ceiling",
            "kind": "CEILING",
            "gbp_per_shifted_mwh": round(hindsight, 4),
            "pence_per_shifted_kwh": round(hindsight / 10.0, 4),
            "gbp_per_household_year": round(per_household, 2),
            "share_of_the_day_price": round(hindsight / world["mean_day_price_gbp_per_mwh"], 4),
            "note": (
                "Perfect foreknowledge of the day's price shape, perfect compliance, every kWh "
                "moved, at a shiftable share of 1.0. Unreachable by construction, which is what "
                "makes it a ceiling."
            ),
        },
        "null_ceiling": {
            "rung": "null_ceiling",
            "kind": "noise floor",
            "gbp_per_shifted_mwh": round(null, 4),
            "note": (
                f"The MAX over {NULL_DRAWS} draws of an optimiser with no skill: the window picked "
                "from a shuffled day and scored on the real one."
            ),
        },
        "matched_panel_clearance": matched_panel_clearance(
            days, window, r3_panel_days(), seed),
        "shiftable_share_curve": money_share_curve(per_household),
        "sharing_frontier": sharing_frontier(per_household),
        "the_interior_optimum": the_interior_optimum(),
        "the_carbon_column": the_carbon_column(per_household),
        "reachable_book": reachable_bound,
        "known_errors": [dict(e) for e in KNOWN_ERRORS],
        "refuses_to_total": (
            "There is no total here. The money column and R3's carbon column are the same act in "
            "two currencies and their sum is not a quantity; the household's share and the "
            "company's share of the money already sum to it by construction, so adding them to it "
            "would count the created value twice."
        ),
        "verdict": {
            "clears_the_null": clears,
            "whole_panel_ratio": round(hindsight / null, 2) if null > 0 else None,
            "whole_panel_ratio_is_NOT_comparable_to_R3s": (
                "It is computed over a panel two orders of magnitude larger, and the null's height "
                "falls with panel size for reasons that have nothing to do with signal. Read "
                "`matched_panel_clearance` against R3 instead."
            ),
            "retires_time_of_use": not clears,
        },
        "named_gaps": [
            "THE SHIFT RESPONSE as a function of pass-through. It is what decides where on the "
            "frontier the company's own optimum sits, and nothing in the knowledge layer, the "
            "commons or the market research establishes one. A question to research.",
            "SHIFTABLE SHARE of domestic load — R3's gap, and the same one here. The headline is "
            "at share 1.0 and the curve is published instead of a figure.",
            "NO MEASURED PRICE-FORECAST CAPTURE. R3 handicaps its ceiling by the intensity feed's "
            "own measured forecast capture; this repository holds no equivalent for the price, and "
            "applying the intensity one would multiply two different quantities together. A real "
            "time-of-use tariff is set from the DAY-AHEAD AUCTION clear, which is published before "
            "the day rather than forecast, so the handicap may be much smaller than R3's — but "
            "this repository holds no half-hourly day-ahead auction series to measure it on, so "
            "the gap between day-ahead knowledge and hindsight is UNMEASURED and is not assumed "
            "away.",
            "MID COVERAGE ends 2020-12 in this tree and begins 2016-09. The 2021-2023 price "
            "episode is outside the panel entirely.",
            "THE COST OF THE PRODUCT. Half-hourly settlement, a smart-meter rollout to the "
            "traditional-metered majority, and the shape and imbalance risk a supplier takes on "
            "when it prices a household half-hourly. None of it is in this figure, and a ceiling "
            "is a gross number by construction.",
        ],
    }


def r3_panel_days() -> int:
    """R3's own panel size, READ from its artefact so the matched comparison cannot go stale."""
    if not R3_ARTEFACT.exists():
        return 0
    try:
        r3 = json.loads(R3_ARTEFACT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    days = (r3.get("world") or {}).get("days")
    return int(days) if isinstance(days, int) and days > 0 else 0


def headline(result: dict) -> str:
    """One paragraph, and it has to survive being read alone."""
    created = result["created_value"]
    verdict = result["verdict"]
    matched = result.get("matched_panel_clearance") or {}
    carbon = result.get("the_carbon_column") or {}
    reach = result.get("reachable_book") or {}
    book = result["book"]

    if not verdict["clears_the_null"]:
        return (
            "THE TIME-OF-USE PRODUCT IS RETIRED. The day's cheapest window is not reliably cheaper "
            "than a window picked at random, so there is nothing for a tariff to pass through. "
            "Because this is a true CEILING on the created value, that retires the candidate "
            "outright rather than merely failing to support it."
        )

    lead = (
        f"A TIME-OF-USE TARIFF COULD CREATE £{created['gbp_per_household_year']:.2f} PER "
        f"HOUSEHOLD-YEAR ON THIS BOOK, and that is a CEILING: perfect foreknowledge of the day's "
        f"price shape, perfect compliance, every kWh moved. It is "
        f"£{created['gbp_per_shifted_mwh']:.2f}/MWh avoided — "
        f"{created['share_of_the_day_price'] * 100:.0f}% of the mean day price — over "
        f"{result['price_series']['days']} whole days of Elexon MID, "
        f"{result['price_series']['years'][0]}-{result['price_series']['years'][-1]}."
    )
    if matched.get("available"):
        lead += (
            f" At R3's own panel size it clears its skill-free null by "
            f"{matched['median_ratio']}x at the median and {matched['worst_ratio']}x at the worst "
            f"of {matched['draws']} draws; the whole-panel ratio of "
            f"{verdict['whole_panel_ratio']}x is larger only because the null falls with panel "
            "size, and is not the figure to read against R3."
        )
    if carbon.get("available") and carbon.get("money_over_carbon"):
        lead += (
            f" AND THE MONEY IS THE CASE, NOT THE CARBON: the same act — every kWh into the day's "
            f"cleanest six half hours — is worth {carbon['money_over_carbon']}x more in avoided "
            f"wholesale cost than in carbon at the DESNZ traded value "
            f"(£{carbon['carbon_value_gbp_per_household_year']:.2f} per household-year, "
            f"{carbon['kg_co2e_per_household_year']:.0f} kgCO2e). The two are never summed; they "
            "are the same act in two currencies. But only ONE of them can be shared with the "
            "household, because only one of them lands on a bill — which is why the tariff is the "
            "precondition for the abatement rather than a way of monetising it."
        )
    lead += (
        f" WHO IT COULD BE SOLD TO IS THE BINDING CONSTRAINT: half-hourly settlement needs a smart "
        f"meter, and {book['reachable']} of {book['households_with_an_eac']} households on this "
        f"book carry both a smart meter and an electricity EAC"
    )
    if reach.get("available"):
        lead += (
            f", so the whole reachable book is £{reach['book_gbp_per_year']:.0f} a year at the "
            "ceiling."
        )
    else:
        lead += ", which is under this instrument's floor for a book-level figure."
    lead += (
        " AND SHARING CREATES NOTHING: the household's share and the company's share sum to the "
        "created value at every pass-through. The company's take is zero at both ends of that "
        "frontier — nothing moves at zero pass-through, nothing is retained at full — so its own "
        "optimum is strictly interior, which follows from the endpoints and needs no elasticity. "
        "Where it sits does need one, and none is established."
    )
    return lead


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
