"""Tests for Interconnector Capacity Booking Register (Phase FQ)."""
import datetime as dt
import pytest
from company.trading.interconnector_booking import (
    InterconnectorId, BookingPeriod, InterconnectorBooking,
    InterconnectorBookingRegister,
)

START = dt.date(2024, 1, 1)
END = dt.date(2024, 1, 31)


def make_booking(bk_id="ICB-001", ic=InterconnectorId.IFA, cap=100.0,
                 cap_price=5.0, uk_price=80.0, cont_price=60.0):
    return InterconnectorBooking(
        booking_id=bk_id, interconnector=ic,
        period_type=BookingPeriod.MONTHLY,
        period_start=START, period_end=END,
        capacity_mw=cap, capacity_price_gbp_per_mw=cap_price,
        expected_continental_price_gbp_per_mwh=cont_price,
        expected_uk_price_gbp_per_mwh=uk_price,
    )


class TestInterconnectorBooking:
    def test_capacity_cost(self):
        b = make_booking(cap=100.0, cap_price=5.0)
        assert b.total_capacity_cost_gbp == pytest.approx(500.0)

    def test_spread_positive(self):
        b = make_booking(uk_price=80.0, cont_price=60.0)
        assert b.price_spread_gbp_per_mwh == pytest.approx(20.0)

    def test_is_arbitrage_positive(self):
        assert make_booking(uk_price=80.0, cont_price=60.0).is_arbitrage_positive

    def test_not_arbitrage_positive(self):
        assert not make_booking(uk_price=60.0, cont_price=80.0).is_arbitrage_positive

    def test_days_in_period(self):
        b = make_booking()
        assert b.days_in_period == 31

    def test_expected_mwh(self):
        b = make_booking(cap=100.0)
        assert b.expected_mwh_imported == pytest.approx(100.0 * 24 * 31)

    def test_expected_saving(self):
        b = make_booking(cap=100.0, cap_price=1.0, uk_price=80.0, cont_price=60.0)
        # spread=20, mwh=74400, saving=74400*20 - 100*1 = 1488000-100
        assert b.expected_saving_gbp > 0

    def test_zero_saving_when_arbitrage_negative(self):
        b = make_booking(uk_price=60.0, cont_price=80.0)
        assert b.expected_saving_gbp == pytest.approx(0.0)

    def test_booking_summary(self):
        s = make_booking().booking_summary()
        assert "InterconnectorBooking" in s


class TestInterconnectorBookingRegister:
    def test_record_and_retrieve(self):
        reg = InterconnectorBookingRegister()
        reg.record(make_booking())
        assert len(reg.bookings_for_interconnector(InterconnectorId.IFA)) == 1

    def test_profitable_bookings(self):
        reg = InterconnectorBookingRegister()
        reg.record(make_booking(uk_price=80.0, cont_price=60.0))  # profitable
        reg.record(make_booking(bk_id="B2", uk_price=60.0, cont_price=80.0))  # not
        assert len(reg.profitable_bookings()) == 1

    def test_total_expected_saving(self):
        reg = InterconnectorBookingRegister()
        reg.record(make_booking(uk_price=80.0, cont_price=60.0))
        assert reg.total_expected_saving_gbp() > 0

    def test_interconnector_summary(self):
        reg = InterconnectorBookingRegister()
        reg.record(make_booking())
        s = reg.interconnector_booking_summary()
        assert "Interconnector Bookings" in s
