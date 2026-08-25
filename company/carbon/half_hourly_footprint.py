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
here: the shape's clean end is optimistic (no coal, no interconnector imports), so a timing
benefit computed from it is an UPPER BOUND on the real one.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from company.regulatory.carbon_emissions import grid_intensity_g_co2e_per_kwh

PROJECT = Path(__file__).resolve().parent.parent.parent
INTENSITY_FEED = PROJECT / "docs" / "market_data" / "grid_intensity_feed.json"
CONSUMPTION_FEED = PROJECT / "docs" / "market_data" / "consumption_feed.json"

MEASURED = "measured"
PROFILED = "profiled"
UNCOVERED = "uncovered"

#: What is in every figure this module returns, carried forward by every consumer (R14 applied
#: to a carbon basis). The brief's rule: basis, sample size, period, counterfactual.
FOOTPRINT_BASIS = (
    "Electricity emissions only. Company estimate: its own published ANNUAL grid intensity "
    "(company/regulatory/carbon_emissions.py, the single owner) given half-hourly resolution "
    "by the published shape feed. Generation-based, national, outturn, no loss correction. "
    "NOT abatement -- there is no counterfactual here and none is implied."
)

#: Stated in the same breath as any total, because each is a real hole in the number and a
#: reader who is not told will assume the number is whole.
NOT_INCLUDED = [
    "gas -- a near-constant factor per kWh burned, and the only lever on it is using less",
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
    for read in reads:
        date_str = str(read.get("date") or "")
        period = read.get("period")
        kwh = read.get("kwh")
        if not date_str or period is None or kwh is None:
            continue
        factor = shape.get((date_str, int(period)))
        if factor is None:
            continue
        level = grid_intensity_g_co2e_per_kwh(int(date_str[:4]))
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
