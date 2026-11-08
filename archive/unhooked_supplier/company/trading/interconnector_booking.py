"""Interconnector Capacity Booking Register (Phase FQ).

While the UK's interconnector capacity bookings are primarily done by generators
and large traders, suppliers with I&C customers sometimes book interconnector
capacity to access cheaper continental prices.

Capacity is auctioned by NESO (previously National Grid) and the interconnector
operators (Eleclink, Nemo, BritNed, etc.). Results are published.

Types of capacity products:
- Daily: booked day-ahead (most common for opportunistic trading)
- Monthly: short-term flexibility
- Annual: longer-term baseload procurement

From the observable perspective:
- NESO publishes interconnector utilisation and capacity auctions
- Capacity prices and utilisation rates are public
- I&C customers with half-hourly meters may benefit from import timing

Simplified model: company books capacity to import at continental prices
when UK price premium exceeds capacity booking cost.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class InterconnectorId(str, Enum):
    IFA = "IFA"          # France, 2000 MW
    IFA2 = "IFA2"        # France, 1000 MW
    NEMO = "NEMO"        # Belgium, 1000 MW
    BRITNED = "BRITNED"  # Netherlands, 1000 MW
    NSL = "NSL"          # Norway, 1400 MW
    MOYLE = "MOYLE"      # Ireland, 500 MW
    EWIC = "EWIC"        # Ireland, 500 MW


class BookingPeriod(str, Enum):
    DAILY = "daily"
    MONTHLY = "monthly"
    ANNUAL = "annual"


@dataclass(frozen=True)
class InterconnectorBooking:
    booking_id: str
    interconnector: InterconnectorId
    period_type: BookingPeriod
    period_start: dt.date
    period_end: dt.date
    capacity_mw: float
    capacity_price_gbp_per_mw: float
    expected_continental_price_gbp_per_mwh: float
    expected_uk_price_gbp_per_mwh: float

    @property
    def total_capacity_cost_gbp(self) -> float:
        return self.capacity_mw * self.capacity_price_gbp_per_mw

    @property
    def price_spread_gbp_per_mwh(self) -> float:
        return self.expected_uk_price_gbp_per_mwh - self.expected_continental_price_gbp_per_mwh

    @property
    def is_arbitrage_positive(self) -> bool:
        return self.price_spread_gbp_per_mwh > 0

    @property
    def days_in_period(self) -> int:
        return (self.period_end - self.period_start).days + 1

    @property
    def expected_mwh_imported(self) -> float:
        return self.capacity_mw * 24 * self.days_in_period

    @property
    def expected_saving_gbp(self) -> float:
        if not self.is_arbitrage_positive:
            return 0.0
        return (self.expected_mwh_imported * self.price_spread_gbp_per_mwh
                - self.total_capacity_cost_gbp)

    def booking_summary(self) -> str:
        return (
            "InterconnectorBooking " + self.booking_id + " " + self.interconnector.value + ": "
            + str(self.capacity_mw) + "MW "
            + self.period_type.value + " "
            "spread=" + str(round(self.price_spread_gbp_per_mwh, 2)) + " GBP/MWh "
            + ("PROFITABLE" if self.expected_saving_gbp > 0 else "NOT_PROFITABLE")
        )


class InterconnectorBookingRegister:

    def __init__(self) -> None:
        self._bookings: List[InterconnectorBooking] = []
        self._next_id = 1

    def record(self, booking: InterconnectorBooking) -> InterconnectorBooking:
        self._bookings.append(booking)
        return booking

    def bookings_for_interconnector(
        self, ic: InterconnectorId
    ) -> List[InterconnectorBooking]:
        return [b for b in self._bookings if b.interconnector == ic]

    def profitable_bookings(self) -> List[InterconnectorBooking]:
        return [b for b in self._bookings if b.expected_saving_gbp > 0]

    def total_expected_saving_gbp(self) -> float:
        return sum(b.expected_saving_gbp for b in self._bookings)

    def total_capacity_cost_gbp(self) -> float:
        return sum(b.total_capacity_cost_gbp for b in self._bookings)

    def interconnector_booking_summary(self) -> str:
        n = len(self._bookings)
        n_profitable = len(self.profitable_bookings())
        total_saving = self.total_expected_saving_gbp()
        return (
            "Interconnector Bookings: " + str(n) + " bookings. "
            "Profitable: " + str(n_profitable) + ". "
            "Expected saving: GBP" + str(round(total_saving, 0)) + "."
        )
