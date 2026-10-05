"""What a household's electricity actually emitted, half hour by half hour.

REUSE: company/carbon/half_hourly_footprint.py
CLASS: CUSTOM
INDEX: searched "carbon", "footprint", "intensity", "emission", "half-hourly", "meter read",
       "consumption feed". Four organs came back and each is used rather than rebuilt.
       `company/regulatory/carbon_emissions.grid_intensity_g_co2e_per_kwh` is the ONE annual
       series and is imported, never restated -- `tools/grid_intensity_guard.py` fails a second
       one and this module would have been the fourth. `company/billing/carbon_footprint.py` is
       the annual-only estimator this is the time-resolved sibling of; it keeps its job (an EAC
       and a year) and is untouched. `company/carbon/carbon_ledger.py` is the SAVED/SPENT/NET
       event ledger these emissions eventually become events in. `docs/market_data/
       grid_intensity_feed.json` is read by name, exactly as the price and consumption feeds
       are. What none of them has is a household number that moves within the day.

WHAT THIS MEASURES, AND WHAT IT IS NOT
---------------------------------------
EMISSIONS. Tonnes this household's electricity represents. A measurement.

NOT ABATEMENT, and the distinction is the first thing in the advisor's scope brief of
2026-08-04: *"Emissions -- tonnes this household's energy use represents. A measurement.
Abatement -- tonnes avoided versus what would otherwise have happened. A counterfactual, and
therefore always an estimate. Only the first is observable."*

So this module does not compute the mission's score and must never be read as though it had.
`£/tCO2e abated` needs a counterfactual, the brief ranks the four available bases, and it says
plainly that *"at the current book size none of the first three is viable. That is not a reason
to fabricate; it is a reason to say so."* The site's `NOT YET MEASURED` tag on the score stays
exactly where it is. What changes is that the layer underneath it now exists and is honest.

R12/CARBON_NOT_A_TARGET: everything here is a DIAGNOSTIC. Nothing in this module may be reached
by a fitness function, an atom draw, a risk committee, or any pricing or personalisation reward
-- `tests/company/test_carbon_not_a_target.py` is the grep-guard and it is mutation-tested. The
cheapest way to improve a carbon number is to pick easy households, which is the opposite of
the mission.

THE THREE-WAY SPLIT, WHICH IS THE POINT
----------------------------------------
Every account lands in exactly one of three states and the count of each is published beside
every figure, because a number without its sample size is a slogan:

  MEASURED  -- a half-hourly meter read met with the half hour's own grid intensity. The real
               thing, and the only state in which a timing effect exists at all.
  PROFILED  -- no half-hourly read. Emissions are known (annual consumption times the published
               annual intensity, which is what they have always been) and the TIMING EFFECT IS
               UNAVAILABLE, not zero. A traditional meter does not record when anything
               happened and no estimate recovers it.
  UNCOVERED -- neither. Named, never counted as zero.

249 of 263 accounts are PROFILED, because they have a traditional meter. That is not a defect
in this module; it is the honest state of the book, and it is the number that decides how much
of the mission is currently measurable at all. It is also the single change that would move
that number most: GB domestic smart-meter penetration is over half, and this book is at 5%.

THE FLAT COUNTERPART, and why it is computed every time
--------------------------------------------------------
Every figure is produced twice: once against the half-hourly shape, and once against the flat
annual intensity alone -- which is the method the whole tree used until today, and item 1 on
the brief's disqualification battery. The difference between them is the TIMING EFFECT, and it
is the only quantity here that is new information rather than a restatement.

It is also the honest way to size the claim. If a household's timed and flat numbers differ by
a fraction of a percent, then timing is not where its carbon is, and no amount of shifting
advice was ever going to help it. Publishing the flat number beside the timed one makes that
refutable instead of assumed.

THE ERROR DIRECTION, carried from the feed and repeated here because it will be quoted from
here. Since 2026-10-05 the feed is NESO's published series wherever NESO published (from
2018-05-11), with an estimate from Elexon's fuel mix before that date. So the shape is no longer
a model's. A timing benefit computed from it is still an UPPER BOUND on what advice could have
delivered, because it is outturn read with hindsight and a household acts on a forecast.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from company.regulatory.carbon_emissions import (
    GasFactorUnavailable,
    gas_factor_kg_co2e_per_kwh,
    grid_intensity_g_co2e_per_kwh,
    grid_intensity_level,
    grid_intensity_unavailable_reason,
)

PROJECT = Path(__file__).resolve().parent.parent.parent
INTENSITY_FEED = PROJECT / "docs" / "market_data" / "grid_intensity_feed.json"
CONSUMPTION_FEED = PROJECT / "docs" / "market_data" / "consumption_feed.json"

MEASURED = "measured"
PROFILED = "profiled"
UNCOVERED = "uncovered"

#: What is in every figure this module returns, carried forward by every consumer (R14 applied
#: to a carbon basis). The brief's rule: basis, sample size, period, counterfactual.
FOOTPRINT_BASIS = (
    "The day panels are the ELECTRICITY leg only -- for a gas-heated home a minority of its "
    "carbon; the household's year below adds its gas. Company estimate: its own published "
    "ANNUAL grid intensity "
    "(company/regulatory/carbon_emissions.py, the single owner) given half-hourly resolution "
    "by the published shape feed -- both NESO's national series, so shape x level is NESO's own "
    "half-hourly figure. National, outturn, generation basis (transmission and distribution "
    "losses not included), CO2 at the generator. "
    "NOT abatement -- there is no counterfactual here and none is implied."
)

#: Stated in the same breath as any total, because each is a real hole in the number and a
#: reader who is not told will assume the number is whole.
NOT_INCLUDED = [
    "gas in the half-hourly day panels -- a gas meter is not read by the half hour; the "
    "household's gas is in its yearly figure, from its billed gas",
    "upstream (well-to-tank) emissions of the gas, and the lifecycle and upstream emissions of "
    "the electricity's generation (NESO's factors are CO2 at the generator)",
    "transmission and distribution losses: the grid figure is per kWh GENERATED, and the "
    "electricity lost between the power station and the meter is not added. Whether it should "
    "be is an open definition decision; if it is, it will be its own named line",
    "fuels this supplier does not sell the household: gas or electricity bought elsewhere, oil, "
    "petrol",
    "abatement: what the household would have emitted otherwise. A counterfactual, not measured",
    "embodied carbon in any measure or asset fitted",
    "the company's own emissions serving them (that is the carbon ledger's SPENT side)",
    "any customer with neither a half-hourly read nor a profiled consumption figure",
]


class FootprintUnavailable(Exception):
    """The footprint could not be computed. Never a silent zero.

    Zero emissions is a spectacular result and an unavailable instrument must not be able to
    report one (R15 fail-silent). Every path that cannot produce a number raises instead.
    """


@dataclass(frozen=True)
class Footprint:
    """One account's electricity emissions over one period, both ways."""

    account_id: str
    method: str
    kwh: float
    co2e_kg_timed: float | None      # None when the meter cannot say WHEN anything happened
    co2e_kg_flat: float
    half_hours: int
    period_from: str
    period_to: str
    # THE FLAT COMPARATOR'S OWN SPAN when it is not a whole year: ((from, to), ...) per part year
    # whose level priced a read. 2025's level is the 1 Jan..7 Jun mean, about 6% above the full
    # year, so a page calling it "the year's average" misnames the very thing the timed figure is
    # measured against. Empty means every level used was a whole calendar year's.
    partial_level_spans: tuple[tuple[str, str], ...] = ()

    @property
    def timing_effect_pct(self) -> float:
        """How much of this household's carbon is about WHEN it drew, not how much.

        Negative means it drew at cleaner-than-average times; positive, dirtier.

        RAISES for a profiled account rather than returning 0.0, and the difference is the whole
        honesty of the column. Zero would mean "this household's timing is exactly average",
        which is a measurement nobody made; the truth is that its meter does not record time and
        so there is no answer. A caller has to handle the absence, which means the page has to
        show it (R15 fail-open: an unavailable measurement must not read as a benign one).
        """
        if self.co2e_kg_timed is None:
            raise FootprintUnavailable(
                f"{self.account_id} is {self.method}: its meter does not record when anything "
                "happened, so its timing effect is unavailable and is not zero"
            )
        if self.co2e_kg_flat == 0.0:
            raise FootprintUnavailable(
                f"{self.account_id} has a flat footprint of zero, so a timing effect against it "
                "would be a division by zero dressed up as a percentage"
            )
        return 100.0 * (self.co2e_kg_timed - self.co2e_kg_flat) / self.co2e_kg_flat


@dataclass(frozen=True)
class BookFootprint:
    """The whole book, with the coverage that decides what it is allowed to claim."""

    accounts: tuple[Footprint, ...]
    counts: Mapping[str, int]
    uncovered: tuple[str, ...] = field(default_factory=tuple)

    @property
    def measured_share(self) -> float:
        total = sum(self.counts.values())
        if total <= 0:
            raise FootprintUnavailable("an empty book has no coverage share")
        return self.counts.get(MEASURED, 0) / total

    def coverage_statement(self) -> str:
        """The sentence that goes beside every figure.

        BUILT FROM THE COUNTS, never written out beside them. The measured/profiled split moves
        every time a smart meter is fitted, and a hand-written sentence would have gone stale on
        the first one -- the same defect this project has already filed against a page that told
        three households they had no smart meter when they did.
        """
        measured = self.counts.get(MEASURED, 0)
        profiled = self.counts.get(PROFILED, 0)
        uncovered = self.counts.get(UNCOVERED, 0)
        total = measured + profiled + uncovered
        if total == 0:
            return "No accounts. There is nothing here to have a coverage statement about."

        parts = [
            "{} of {} account(s) are MEASURED -- a real half-hourly meter read met with the "
            "grid's intensity in that half hour.".format(measured, total)
        ]
        if profiled:
            parts.append(
                "{} are PROFILED: their emissions are known but their TIMING EFFECT IS "
                "UNAVAILABLE, not zero -- a traditional meter does not record when anything "
                "happened, and no estimate recovers it.".format(profiled)
            )
        if uncovered:
            parts.append(
                "{} are UNCOVERED -- no read and no profiled consumption. They are named, not "
                "counted as zero.".format(uncovered)
            )
        if measured == 0:
            parts.append(
                "NOTHING here is measured. Every figure below is an estimate about an average "
                "household."
            )
        return " ".join(parts)


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise FootprintUnavailable(f"could not read {path.name}: {exc}") from exc


def load_shape(path: Path | None = None) -> tuple[dict[tuple[str, int], float], dict[str, list]]:
    """(half-hourly shape, typical day by year) from the published feed.

    Raises rather than returning empties: a missing feed means this instrument did not run, and
    an instrument that did not run must not report a household emitting nothing.
    """
    feed = _load(path or INTENSITY_FEED)
    records = feed.get("records") or []
    shape = {
        (str(r["date"]), int(r["period"])): float(r["shape"])
        for r in records
        if r.get("date") is not None and r.get("period") is not None and r.get("shape") is not None
    }
    typical = feed.get("typical_day") or {}
    if not shape and not typical:
        raise FootprintUnavailable(
            "the grid-intensity feed carries neither half-hourly records nor a typical day, so "
            "nothing here can be given a time of day"
        )
    return shape, typical


def measured_footprint(
    account_id: str,
    reads: Sequence[Mapping],
    shape: Mapping[tuple[str, int], float],
) -> Footprint:
    """One account's emissions from its OWN half-hourly reads. The real measurement.

    A read whose half hour has no published shape is DROPPED, and the dropped count shows up as
    a smaller `half_hours` rather than as a quietly cleaner household: substituting 1.0 for a
    missing shape would be the flat method smuggled in one half hour at a time, and it would
    always push the timed figure back toward the flat one, i.e. toward "timing does not matter".
    """
    timed_g = flat_g = 0.0
    kwh_total = 0.0
    used = 0
    dates: list[str] = []
    partial_spans: dict[str, tuple[str, str] | None] = {}
    for read in reads:
        date_str = str(read.get("date") or "")
        period = read.get("period")
        kwh = read.get("kwh")
        if not date_str or period is None or kwh is None:
            continue
        factor = shape.get((date_str, int(period)))
        if factor is None:
            continue
        # PART YEARS ARE RIGHT HERE, and only here: a published shape value lies inside the span
        # its year's level was averaged over, so shape x level is the published gram figure.
        level = grid_intensity_g_co2e_per_kwh(int(date_str[:4]), allow_partial=True)
        if level is None:
            raise FootprintUnavailable(
                f"{account_id}: a published shape half hour on {date_str} has no published "
                "annual level -- "
                + str(grid_intensity_unavailable_reason(int(date_str[:4]), allow_partial=True)))
        if date_str[:4] not in partial_spans:
            published = grid_intensity_level(int(date_str[:4]))
            partial_spans[date_str[:4]] = None if published.complete else (
                str(published.covers_from), str(published.covers_to))
        timed_g += float(kwh) * level * factor
        flat_g += float(kwh) * level
        kwh_total += float(kwh)
        used += 1
        dates.append(date_str)

    if used == 0:
        raise FootprintUnavailable(
            f"{account_id} has no half-hourly read that meets a published grid-intensity half "
            "hour, so there is no measurement -- not a zero"
        )
    return Footprint(
        account_id=account_id,
        method=MEASURED,
        kwh=round(kwh_total, 4),
        co2e_kg_timed=round(timed_g / 1000.0, 4),
        co2e_kg_flat=round(flat_g / 1000.0, 4),
        half_hours=used,
        period_from=min(dates),
        period_to=max(dates),
        partial_level_spans=tuple(span for _y, span in sorted(partial_spans.items()) if span),
    )


def profiled_footprint(account_id: str, annual_kwh: float, year: int) -> Footprint:
    """An account with no half-hourly read: emissions known, TIMING NOT MEASURABLE.

    `co2e_kg_timed` is None here, and getting to that was the one real design argument in this
    module. The first version spread the year's kWh evenly across the published typical day and
    reported the result as a timed figure. It is wrong twice over and both errors flatter:

      * a household is not flat. Real domestic demand peaks in the early evening, which is
        exactly when GB's grid is dirtiest, so an even spread UNDERSTATES a profiled
        household's carbon -- and understating a customer's emissions is the direction a
        supplier would like;
      * the number it produces is a fact about the average grid meeting a flat load. It is not
        a fact about this household, and it would have appeared in a per-account column, under
        that household's name, indistinguishable from the three accounts where the figure is
        real.

    Spreading by the household's PROFILE CLASS shape instead would fix the first error and not
    the second: the timing effect would still be the profile's, identical for every account on
    that profile, and it would still sit in a column implying it was theirs. The honest answer
    is that a traditional meter does not record when anything happened, so nothing can recover
    it, and this says so instead of estimating around it.

    So a profiled account gets its emissions -- annual consumption times the published annual
    intensity, which is what it has always been -- and its timing effect is UNAVAILABLE. The
    count of these against the measured ones is the coverage statement, and on this book it is
    249 against 3.
    """
    level = grid_intensity_g_co2e_per_kwh(int(year))
    if level is None:
        raise FootprintUnavailable(
            f"{account_id or 'household'} {year}: no whole-year grid intensity -- "
            + str(grid_intensity_unavailable_reason(int(year))))
    return Footprint(
        account_id=account_id,
        method=PROFILED,
        kwh=round(float(annual_kwh), 4),
        co2e_kg_timed=None,
        co2e_kg_flat=round(float(annual_kwh) * level / 1000.0, 4),
        half_hours=0,
        period_from=f"{year}-01-01",
        period_to=f"{year}-12-31",
    )


# ---------------------------------------------------------------------------------------------
# THE HOUSEHOLD: electricity AND gas, from what this supplier billed (2026-10-05)
# ---------------------------------------------------------------------------------------------
#
# Everything above is electricity, and until 2026-10-05 it was the only household carbon figure
# the company published. For a gas-heated home that is about 15% of its carbon on the 2025 grid
# (docs/market_research/household_carbon_and_the_measures_that_save_it.md §2-3), and it would
# have shown a heat pump -- gas off, electricity up -- as a carbon INCREASE. The legs below are
# the household's own billed kWh: a gas bill is read from its own gas meter, so the gas leg is a
# fact the supplier holds, not an estimate about an average home.
#
# TWO THINGS THIS DOES NOT KNOW, each said on the record rather than assumed:
#   * a fuel bought from ANOTHER supplier. "No gas supply on record" is this supplier's record.
#   * DESNZ's 2022 gas factor (`GAS_FACTOR_GAPS`): a 2022 gas leg has kWh and no kg.
#
# WHY A GAS ACCOUNT CLOSED is a fact the supplier's own records hold, and a closure is read
# through it (`gas_closure_cause`). Until 2026-10-05 every closure was a 0 kg gas leg, so a
# household that only moved its gas to another supplier read as a 2,173 kg cut -- larger than a
# real heat pump's 1,738 kg (docs/market_research/practitioner_questions_as_assumption_toggles.md
# Q5). A meter removal is a job the supplier itself orders; a switch away arrives as a loss
# notice; a household that left arrives as a loss on every point it held. Only the first means the
# gas stopped. After the other two the gas is burnt on someone else's meter, and after an
# unexplained one we do not know, so neither is a zero.

BILLED = "billed"
NO_SUPPLY = "no_supply_on_record"
GAS_CLOSED = "closed"

#: Why a gas leg closed, from this supplier's own records (`gas_closure_cause`).
REMOVED = "removed"                # a meter removal or cap this supplier ordered
SWITCHED_AWAY = "switched_away"    # a loss notice on the gas point; the household's electricity stayed
ACCOUNT_CLOSED = "account_closed"  # the household left this supplier on every point it held
UNKNOWN = "unknown"                # no record says which
CLOSURE_CAUSES = (REMOVED, SWITCHED_AWAY, ACCOUNT_CLOSED, UNKNOWN)

#: THE ONE DIAL: the causes after which the household's gas truly stopped, so its gas carbon is a
#: known zero and a fall can be claimed. Every other cause leaves the gas carbon NOT KNOWN.
GAS_STOPPED_CAUSES = frozenset({REMOVED})

#: What the page says for a closure whose gas went on burning elsewhere.
GAS_ELSEWHERE_REASON = "gas now supplied elsewhere \u2014 not a saving we can see"

#: Why `removal_ordered` is False on every production call today. Said once, here, so a caller
#: that cannot set it names this rather than inventing a reading.
REMOVAL_RECORD_GAP = (
    "no record in this company can identify a gas meter removal: `company/billing/meter_assets.py`"
    " has a 'removed' status nothing sets, `company/market/mprn_register.py` has no production "
    "caller and no removal transition, and `company/billing/account_closure.ClosureReason` has no "
    "meter-removal reason. So `removed` is unreachable on the published book; a closure with no "
    "loss notice is `unknown`, and a rise in electricity is never read as a removal"
)

NO_GAS_SUPPLY_REASON = "no gas supply on record"
NO_ELECTRICITY_SUPPLY_REASON = "no electricity supply on record"

#: Months a billed leg must cover for its year to be compared with another. A part year against a
#: whole one compares seasons, and for gas the winter is most of the year.
FULL_YEAR_MONTHS = 12

ELECTRICITY_LEG_BASIS = (
    "Electricity this supplier billed the household for in the year, times the company's own "
    "published annual grid intensity for that year (company/regulatory/carbon_emissions.py). "
    "NESO's published national series (Historic GB Generation Mix), demand-weighted over the "
    "year, generation basis with transmission and distribution losses not included, CO2 at the "
    "generator. A year the series covers only in part has no figure."
)
GAS_LEG_BASIS = (
    "Gas this supplier billed the household for in the year -- kWh read from its own gas meter, "
    "converted at gross calorific value -- times DESNZ's natural-gas conversion factor for that "
    "year (Scope 1, kgCO2e per kWh gross CV). Combustion at the home only; the upstream "
    "well-to-tank factor is excluded."
)
CHANGE_BASIS = (
    "This supplier's own billed kWh in two whole years. Weather is not removed: a cold year "
    "raises gas with nothing in the home changed."
)
TOTAL_BASIS = (
    "Electricity plus gas, each on its own basis. Emissions, not abatement: nothing here says "
    "what the household would have emitted otherwise."
)


@dataclass(frozen=True)
class Leg:
    """One fuel's year for one household. `co2e_kg` is None only when the factor is not known."""

    fuel: str
    status: str
    kwh: float
    co2e_kg: float | None
    months_billed: int
    basis: str
    reason: str | None = None
    closed_on: str | None = None
    closure_cause: str | None = None

    @property
    def full_year(self) -> bool:
        """Comparable with another year: billed all year, or not supplied by us all year."""
        return self.status != BILLED or self.months_billed >= FULL_YEAR_MONTHS


def _no_supply(fuel: str) -> Leg:
    return Leg(fuel=fuel, status=NO_SUPPLY, kwh=0.0, co2e_kg=0.0, months_billed=0,
               basis=ELECTRICITY_LEG_BASIS if fuel == "electricity" else GAS_LEG_BASIS,
               reason=NO_GAS_SUPPLY_REASON if fuel == "gas" else NO_ELECTRICITY_SUPPLY_REASON)


def electricity_leg(year: int, billed_kwh: float | None, months_billed: int) -> Leg:
    """`billed_kwh` None means the household has no electricity account with this supplier."""
    if billed_kwh is None:
        return _no_supply("electricity")
    kwh = float(billed_kwh)
    try:
        co2e_kg = profiled_footprint("", kwh, int(year)).co2e_kg_flat
    except FootprintUnavailable:
        return Leg(fuel="electricity", status=BILLED, kwh=round(kwh, 4), co2e_kg=None,
                   months_billed=int(months_billed), basis=ELECTRICITY_LEG_BASIS,
                   reason=f"grid intensity not established for {year}: "
                          + str(grid_intensity_unavailable_reason(int(year))))
    return Leg(fuel="electricity", status=BILLED, kwh=round(kwh, 4), co2e_kg=co2e_kg,
               months_billed=int(months_billed), basis=ELECTRICITY_LEG_BASIS)


def gas_closure_cause(*, gas_point_lost: bool, household_left: bool,
                      removal_ordered: bool = False) -> str:
    """Why a gas leg closed, from what this supplier's own records hold.

    `removal_ordered`: a meter removal or cap this supplier itself ordered (an RGMA removal job,
    the point Terminated). No record in the company holds that today (`REMOVAL_RECORD_GAP`), so
    every production caller passes False. `gas_point_lost`: a registration-loss notice on the gas
    point (`company/crm/cos_process.CoSRegister.losses_notified`). `household_left`: the household
    was lost on every point it held with us, so it left rather than moved one fuel.

    Records that contradict each other -- a removal we ordered AND a loss to another supplier --
    are `unknown`, not whichever reads better. Nothing here looks at the electricity bill.
    """
    if removal_ordered:
        return UNKNOWN if (gas_point_lost or household_left) else REMOVED
    if household_left:
        return ACCOUNT_CLOSED
    if gas_point_lost:
        return SWITCHED_AWAY
    return UNKNOWN


def _closure_reason(closed_on: str, cause: str) -> str:
    if cause == REMOVED:
        return (f"gas meter removed {closed_on} on this supplier's own order; the home burns no "
                "gas on a meter")
    if cause == SWITCHED_AWAY:
        return (f"{GAS_ELSEWHERE_REASON}: the gas point was lost to another supplier {closed_on} "
                "while this supplier kept the electricity")
    if cause == ACCOUNT_CLOSED:
        return f"{GAS_ELSEWHERE_REASON}: the household left this supplier {closed_on}"
    return (f"gas account closed {closed_on}; nothing billed since. This supplier holds no removal "
            "order and no loss notice for it, so why the gas stopped is not known and no change "
            "is claimed from it")


def gas_leg(year: int, billed_kwh: float | None, months_billed: int,
            closed_on: str | None = None, closure_cause: str = UNKNOWN) -> Leg:
    """The household's gas for `year`, from its own billed gas.

    `billed_kwh` None: no gas account on record -> 0 with the reason. `closed_on` before the year
    began and nothing billed in it: the account closed, and the closure IS the status, so a fall to
    zero can never read as an ordinary low year. Its gas carbon is a known 0 only when the cause
    is in `GAS_STOPPED_CAUSES`; otherwise it is NOT KNOWN (None), because the gas is still burnt
    -- on another supplier's meter, or for a reason not on file. A billed year whose DESNZ factor
    is not established keeps its kWh and has no kg -- never a neighbouring year's factor.
    """
    year = int(year)
    if billed_kwh is None:
        return _no_supply("gas")
    if closed_on is not None and str(closed_on) < f"{year}-01-01" and not months_billed:
        if closure_cause not in CLOSURE_CAUSES:
            raise ValueError(f"gas closure cause {closure_cause!r} is not one of {CLOSURE_CAUSES}")
        return Leg(fuel="gas", status=GAS_CLOSED, kwh=0.0,
                   co2e_kg=0.0 if closure_cause in GAS_STOPPED_CAUSES else None,
                   months_billed=0, basis=GAS_LEG_BASIS, closed_on=str(closed_on),
                   closure_cause=closure_cause,
                   reason=_closure_reason(str(closed_on), closure_cause))
    kwh = float(billed_kwh)
    try:
        factor = gas_factor_kg_co2e_per_kwh(year)
    except GasFactorUnavailable as exc:
        return Leg(fuel="gas", status=BILLED, kwh=round(kwh, 4), co2e_kg=None,
                   months_billed=int(months_billed), basis=GAS_LEG_BASIS,
                   reason=f"gas factor not established for {year}: {exc}")
    return Leg(fuel="gas", status=BILLED, kwh=round(kwh, 4),
               co2e_kg=round(kwh * factor, 4), months_billed=int(months_billed),
               basis=GAS_LEG_BASIS)


@dataclass(frozen=True)
class HouseholdFootprint:
    """A household's year: electricity, gas and total, reported separately, each with its basis."""

    household_id: str
    year: int
    electricity: Leg
    gas: Leg

    @property
    def total_co2e_kg(self) -> float:
        missing = [leg for leg in (self.electricity, self.gas) if leg.co2e_kg is None]
        if missing:
            raise FootprintUnavailable(
                f"{self.household_id} {self.year}: no total, because the "
                + " and ".join(f"{leg.fuel} leg has no figure ({leg.reason})" for leg in missing))
        return round(float(self.electricity.co2e_kg) + float(self.gas.co2e_kg), 4)

    @property
    def full_year(self) -> bool:
        return self.electricity.full_year and self.gas.full_year

    def as_dict(self) -> dict:
        try:
            total, why = self.total_co2e_kg, None
        except FootprintUnavailable as exc:
            total, why = None, str(exc)
        # The bases are NOT repeated per row: they are three sentences that do not vary by
        # household or year, and a publisher carries them once (`ELECTRICITY_LEG_BASIS`,
        # `GAS_LEG_BASIS`, `TOTAL_BASIS`). Per row they made the feed eighteen times larger.
        out = {"year": self.year, "full_year": self.full_year, "total_co2e_kg": total}
        if why:
            out["total_unavailable"] = why
        for leg in (self.electricity, self.gas):
            row = {"status": leg.status, "kwh": leg.kwh, "co2e_kg": leg.co2e_kg,
                   "months_billed": leg.months_billed}
            if leg.reason:
                row["reason"] = leg.reason
            if leg.closed_on:
                row["closed_on"] = leg.closed_on
                row["closure_cause"] = leg.closure_cause
            out[leg.fuel] = row
        return out


def household_change(before: HouseholdFootprint, after: HouseholdFootprint) -> dict:
    """What changed between two whole years, leg by leg, on this supplier's own meters.

    THE HEAT-PUMP CASE IS WHY THIS EXISTS: gas down or closed and electricity up is a net fall
    exactly when the gas no longer burnt outweighs the extra electricity's carbon, and only a
    figure carrying both legs can say so. Refuses a part year on either side rather than compare a
    winter with a whole year, and refuses a closed gas leg whose gas did not stop
    (`GAS_STOPPED_CAUSES`): a household that moved its gas elsewhere still burns it.
    """
    for fp in (before, after):
        if not fp.full_year:
            raise FootprintUnavailable(
                f"{fp.household_id} {fp.year} is a part year (electricity "
                f"{fp.electricity.months_billed}, gas {fp.gas.months_billed} month(s) billed), so "
                "a change against it would be a change of season")
        if fp.gas.status == GAS_CLOSED and fp.gas.closure_cause not in GAS_STOPPED_CAUSES:
            raise FootprintUnavailable(
                f"{fp.household_id} {fp.year}: no change is claimed across this gas closure "
                f"({fp.gas.closure_cause}) -- {fp.gas.reason}")
    total = round(after.total_co2e_kg - before.total_co2e_kg, 4)
    return {
        "from_year": before.year,
        "to_year": after.year,
        "electricity_change_kg": round(float(after.electricity.co2e_kg)
                                       - float(before.electricity.co2e_kg), 4),
        "gas_change_kg": round(float(after.gas.co2e_kg) - float(before.gas.co2e_kg), 4),
        "total_change_kg": total,
        "net_fall": total < 0.0,
        "gas_closed": after.gas.status == GAS_CLOSED and before.gas.status == BILLED,
        "gas_closure_cause": after.gas.closure_cause,
        # basis: CHANGE_BASIS, carried once by the publisher rather than on every change.
    }
