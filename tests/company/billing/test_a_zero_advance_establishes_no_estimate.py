"""Estimate against the meter (2026-10-28, SEAT_FINDING_A_SUCCESSOR_PAGE_PRINTS_A_DIFFERENT_MPAN_AND_
ESTIMATES_RUN_FIVE_TIMES_THE_METER, section 2). On the 1a02c46116 book, 10 of the 11 breaches of
INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER were occupier accounts estimated at 0 kWh, run after run,
while the next actual read found real use. The cause: the only actual read in the trailing window
was a 0 kWh first month (the occupier's move-in), and a window whose kWh is zero still has profile
weight, so it annualised to zero. A zero advance is a missing measurement, not a household that uses
nothing. That is the same rule `estimate_annual_consumption` already applies to a zero registry
EAC. So it establishes no estimate, and the bill falls back to the registry figure it opened on."""
from datetime import date

from company.billing.unread_month_estimate import estimate_unread_kwh


def test_a_window_of_zero_kwh_establishes_no_estimate():
    window = [(date(2021, 3, 1), date(2021, 3, 31), 0.0)]
    assert estimate_unread_kwh("gas", window, date(2021, 4, 1), date(2021, 4, 30)) is None


def test_a_window_with_use_still_estimates_and_a_zero_month_beside_it_still_counts():
    one = [(date(2021, 3, 1), date(2021, 3, 31), 1000.0)]
    two = one + [(date(2021, 4, 1), date(2021, 4, 30), 0.0)]
    a = estimate_unread_kwh("gas", one, date(2021, 5, 1), date(2021, 5, 31))
    b = estimate_unread_kwh("gas", two, date(2021, 5, 1), date(2021, 5, 31))
    assert a is not None and a > 0 and b is not None and 0 < b < a, (a, b)
