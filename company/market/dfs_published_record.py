"""The published NESO Demand Flexibility Service record, one winter per row.

Source: `docs/market_research/neso_dfs_called_day_response_2026-09-07.md`, which reads NESO's own
winter reviews. Every figure here is one a real GB supplier could read off a public data portal --
31 of them were counterparties to the service in its first winter. Nothing here crosses the wall.

WHY THIS MODULE EXISTS, rather than two copies of a number.

`flexibility_potential.py` and `ic_flexibility_revenue.py` each carried `_DFS_RATE_GBP_PER_MWH = 4.5`
commented "NESO DFS average 2022-24". The realised rate was GBP3,316/MWh in 2022/23 and GBP241/MWh in
2024/25, so the constant was wrong by 737x and 54x -- and `flexibility_potential.py`'s own module
docstring said suppliers earn "GBP3-6/kWh", which IS GBP3,000-6,000/MWh. One file disagreed with
itself by a factor of about a thousand, in ten lines, and two files carried the same wrong value.
That is the shape CLAUDE.md names as the most expensive one here: one fact, several implementations,
and nothing able to notice when one of them is corrected. So the fact lives once.

THE RATE IS NOT A CONSTANT, and that is the substantive finding rather than a modelling convenience.
DFS was a winter-contingency scheme in 2022/23 with a Guaranteed Acceptance Price of GBP3,000/MWh,
and a merit-based margin tool by 2024/25 clearing at GBP100-1,290/MWh. The price fell 13.8x when the
service had to compete. A single scalar cannot represent that and should not be asked to.

THE EVENT RATE IS SOURCED, NOT DERIVED, and this is a finding too. 20 of 2022/23's 22 events were
TESTS on a published calendar ("two onboarding tests in the first month, two regular tests per month
thereafter") -- only 2 were called by system conditions. NESO's live-event trigger was a
discretionary day-ahead margin judgement, never a published rule against an observable series. So an
event rate derived from a price or stress signal would model the wrong generating process for the
founding winter and an unpublished one thereafter. Deriving it depends on `W1_6_physics_price_signal`
(`level_current: 0`) and stays a named gap.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class DFSWinter:
    """One winter of the published record. `None` means NOT ESTABLISHED, never zero.

    `winter_start_year` is the calendar year the winter opens in: 2022 is winter 2022/23.
    """

    winter_start_year: int
    delivered_mwh: Optional[float]
    paid_gbp: Optional[float]
    events: Optional[int]
    events_called_by_system_conditions: Optional[int]
    registered_participants: Optional[int]
    best_event_participation: Optional[int]
    delivery_fraction_of_committed: Optional[float]
    source: str

    @property
    def established(self) -> bool:
        return self.delivered_mwh is not None and self.paid_gbp is not None

    @property
    def realised_rate_gbp_per_mwh(self) -> Optional[float]:
        """What a MWh of delivered turn-down actually paid. `None` when not established.

        Derived from the two published totals rather than quoted, because the quoted headline
        prices (a GBP3,000/MWh guaranteed acceptance, a GBP1,290/MWh highest accepted bid) are
        neither volume-weighted nor what the service settled at.
        """
        if not self.established or not self.delivered_mwh:
            return None
        return round(self.paid_gbp / self.delivered_mwh, 2)

    @property
    def opt_in_fraction(self) -> Optional[float]:
        """Share of REGISTERED participants that delivered in the single best-attended event.

        An upper bound on participation, not an average: it is the best event of the winter.
        """
        if self.best_event_participation is None or not self.registered_participants:
            return None
        return round(self.best_event_participation / self.registered_participants, 4)


# Winter 2022/23: NESO "Demand Flexibility Service: Winter 2022/23 review", August 2023.
#   22 events = 20 tests (40 SPs) + 2 live (5 SPs). Delivery 2,667.7 + 680.0 MWh; cost GBP8.0m +
#   GBP3.1m. Live events delivered 680.0 of 795.4 MWh procured. >1.6m households and businesses.
# Winter 2023/24: NOT ESTABLISHED -- see the research note. Secondary reporting gives 2,507 MWh and
#   3,759 MWh and does not reconcile; no primary NESO end-of-year report was retrieved. Recorded as
#   a gap because an average of two irreconcilable secondary figures would read as established.
# Winter 2024/25: NESO "Demand Flexibility Service", published 3 July 2025.
#   56 Service Requirements, volume procured on 44. Delivered 3,917.7 MWh of 5,449.6 accepted;
#   paid GBP943,983. 1.98m registered MPANs; best event 443,224 (19 Mar 25). Delivery 71.90% of bid.
_RECORD: Dict[int, DFSWinter] = {
    2022: DFSWinter(
        winter_start_year=2022,
        delivered_mwh=3347.7,
        paid_gbp=11_100_000.0,
        events=22,
        events_called_by_system_conditions=2,
        registered_participants=1_600_000,
        best_event_participation=None,  # not published per event for 2022/23
        delivery_fraction_of_committed=0.855,  # live events, 680.0 of 795.4 MWh procured
        source="NESO Winter 2022/23 review, Aug 2023 (Tables 1-3)",
    ),
    2023: DFSWinter(
        winter_start_year=2023,
        delivered_mwh=None,
        paid_gbp=None,
        events=None,
        events_called_by_system_conditions=None,
        registered_participants=None,
        best_event_participation=None,
        delivery_fraction_of_committed=None,
        source="NOT ESTABLISHED: no primary NESO end-of-year report retrieved; "
        "secondary reports give 2,507 MWh and 3,759 MWh and do not reconcile",
    ),
    2024: DFSWinter(
        winter_start_year=2024,
        delivered_mwh=3917.7,
        paid_gbp=943_983.0,
        events=44,
        events_called_by_system_conditions=44,  # merit-based; every procured event was a real call
        registered_participants=1_980_000,
        best_event_participation=443_224,
        delivery_fraction_of_committed=0.7190,
        source="NESO DFS report, 3 July 2025 (Winter 2024/25)",
    ),
}

FIRST_WINTER = 2022

# The winter a caller gets when it does not name one. The LATEST established winter, not the best
# or the average: DFS's price fell 13.8x between its first winter and its third, so "a" DFS rate is a
# question about which year, and defaulting to the crisis winter would flatter every figure downstream.
LATEST_ESTABLISHED_WINTER = 2024

# The called-day attention premium, settled against this same record.
#
# NESO's own live-vs-test comparison: live events delivered consumption reduction "20% higher than
# test events" -- the largest salience contrast the real product ever ran, since a live event was a
# nationally reported margin emergency and a test was a routine scheduled hour. It bought 1.20x.
# It was not bought at a constant price either: live paid GBP4,559/MWh against GBP3,000 for tests,
# so per unit of price signal the called day returned 0.79x -- LESS response per pound.
#
# Carried here because `tools/tou_extreme_day_concentration.py` publishes a break-even of 2.53x that
# this refutes, and a number that settles a published break-even should not live only in prose.
CALLED_DAY_RESPONSE_PREMIUM = 1.20
CALLED_DAY_RESPONSE_PREMIUM_UPPER_BOUND = 2.04


# What one registered domestic participant actually delivered, in kW, during an event.
#
# NESO publishes the domestic delivery distribution as bins rather than a mean: "91% of delivery was
# below 1kW, and 9% between 1kW and 10kW", stated as "consistent with previous winters". Taking bin
# midpoints (0.5 kW and 5.5 kW) gives 0.91*0.5 + 0.09*5.5 = 0.95 kW. The midpoint step is an
# assumption and is named here rather than buried: the bins are published, the mean is not.
#
# This is the constant that makes the rest of the arithmetic behave. The modules this record replaces
# credited a household with its RATED asset power -- a 7.4 kW charger, a 5 kW battery -- delivered in
# full at every event. Correcting only the rate (4.5 -> 3,315.71) while leaving rated power in place
# produced GBP461/yr for a single EV household in 2022/23, against a service that paid GBP6.94 per
# participant across that entire winter. A partial correction here is worse than the defect.
REFERENCE_PARTICIPANT_FLEX_KW = 0.95


def revenue_gbp_per_participant_winter(winter_start_year: int) -> Optional[float]:
    """What the service paid, per registered participant, across one whole winter.

    The anchor for everything below: it is two published totals divided, so a book priced off it
    reconciles with what DFS actually settled instead of with what a rated asset could theoretically
    have delivered. GBP6.94 in 2022/23; GBP0.48 in 2024/25.
    """
    row = _RECORD.get(winter_start_year)
    if row is None or not row.established or not row.registered_participants:
        return None
    return round(row.paid_gbp / row.registered_participants, 4)


def revenue_gbp_for_flex_kw(flex_kw: float, winter_start_year: int) -> Optional[float]:
    """DFS revenue for one participant of a given flex capacity, over one winter.

    Anchored absolutely on the published per-participant economics and weighted relatively by how
    much flex the customer has against `REFERENCE_PARTICIPANT_FLEX_KW`. So a book of average
    households reproduces the published total, and a book of EV-and-battery households earns more --
    without ever asserting that a 7.4 kW charger turns down 7.4 kW at every event, which the
    published delivery distribution says it does not.

    Returns `None` when the winter is not established, and callers must not read that as zero: for
    2023/24 the service ran and paid, and what is missing is our knowledge of how much.
    """
    base = revenue_gbp_per_participant_winter(winter_start_year)
    if base is None:
        return None
    return round(base * (flex_kw / REFERENCE_PARTICIPANT_FLEX_KW), 2)


def winter(winter_start_year: int) -> Optional[DFSWinter]:
    """The published row, or `None` for a year the service did not run."""
    return _RECORD.get(winter_start_year)


def realised_rate_gbp_per_mwh(winter_start_year: int) -> Optional[float]:
    """`None` for a year with no service and for a year that is not established.

    Callers must tell those apart if it matters to them -- `winter(y)` carries the reason. What they
    must NOT do is substitute zero, which would read as "the service paid nothing" rather than "we
    cannot say", and that distinction is the whole point of the row for 2023/24.
    """
    row = _RECORD.get(winter_start_year)
    return row.realised_rate_gbp_per_mwh if row else None


def events(winter_start_year: int) -> Optional[int]:
    """Events with volume procured. `None` where not established."""
    row = _RECORD.get(winter_start_year)
    return row.events if row else None


def participation_haircut(winter_start_year: int) -> Optional[float]:
    """Opt-in x delivery: the share of a registered participant's rated flex that actually settles.

    The two constants this module replaces credited every enrolled customer with full rated power at
    every event. The published record says at best 22.4% of registered participants turned up to any
    single event, and 71.9% of committed volume was delivered. Neither is a modelling choice.
    """
    row = _RECORD.get(winter_start_year)
    if row is None:
        return None
    opt_in, delivery = row.opt_in_fraction, row.delivery_fraction_of_committed
    if opt_in is None or delivery is None:
        return None
    return round(opt_in * delivery, 4)
