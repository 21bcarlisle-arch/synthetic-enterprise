"""Tests for Price Transparency Publication Register (Phase DL)."""
import datetime as dt
import pytest
from company.pricing.price_transparency_register import (
    PublicationChannel, TariffType, UpdateStatus, TariffPublication,
    PriceTransparencyRegister, _MAX_UPDATE_HOURS, _MIN_NOTICE_DAYS_ON_RATE_CHANGE,
)


@pytest.fixture
def reg():
    return PriceTransparencyRegister()


NOW = dt.datetime(2024, 6, 1, 12, 0, 0)
DATE = dt.date(2024, 6, 1)


def make_pub(reg, unit_rate=28.5, standing=60.0, tariff_type=TariffType.FIXED,
             channel=PublicationChannel.WEBSITE, status=UpdateStatus.PUBLISHED,
             prev_rate=None, end_date=dt.date(2025, 6, 1)):
    return reg.publish(
        tariff_name="Poesys Fixed Jun-25",
        fuel="ELECTRICITY",
        tariff_type=tariff_type,
        standing_charge_pence_per_day=standing,
        unit_rate_pence_per_kwh=unit_rate,
        effective_date=DATE,
        published_at=NOW,
        channel=channel,
        end_date=end_date,
        exit_fee_gbp=50.0,
        status=status,
        previous_unit_rate=prev_rate,
    )


class TestTariffPublication:
    def test_pub_created(self, reg):
        pub = make_pub(reg)
        assert pub.tariff_name == "Poesys Fixed Jun-25"
        assert pub.tariff_type == TariffType.FIXED
        assert pub.is_fixed

    def test_rate_change_pct_increase(self, reg):
        pub = make_pub(reg, unit_rate=30.0, prev_rate=28.5)
        assert pub.rate_change_pct == pytest.approx((30.0 - 28.5) / 28.5)
        assert pub.is_rate_increase

    def test_rate_change_pct_decrease(self, reg):
        pub = make_pub(reg, unit_rate=25.0, prev_rate=28.5)
        assert pub.rate_change_pct < 0
        assert not pub.is_rate_increase

    def test_rate_change_none_no_previous(self, reg):
        pub = make_pub(reg)
        assert pub.rate_change_pct is None
        assert not pub.is_rate_increase

    def test_not_stale_when_published(self, reg):
        pub = make_pub(reg, status=UpdateStatus.PUBLISHED)
        as_of = NOW + dt.timedelta(hours=100)
        assert not pub.is_stale(as_of)

    def test_stale_when_pending_over_48h(self, reg):
        pub = make_pub(reg, status=UpdateStatus.PENDING)
        as_of = NOW + dt.timedelta(hours=50)
        assert pub.is_stale(as_of)

    def test_not_stale_pending_within_48h(self, reg):
        pub = make_pub(reg, status=UpdateStatus.PENDING)
        as_of = NOW + dt.timedelta(hours=47)
        assert not pub.is_stale(as_of)

    def test_annual_cost_estimate(self, reg):
        pub = make_pub(reg, unit_rate=28.5, standing=60.0)
        expected = (60.0 * 365 / 100) + (28.5 * 3100.0 / 100)
        assert pub.annual_cost_estimate_gbp == pytest.approx(expected)

    def test_no_fixed_for_svt(self, reg):
        pub = make_pub(reg, tariff_type=TariffType.VARIABLE_SVT)
        assert not pub.is_fixed


class TestPriceTransparencyRegisterQueries:
    def test_active_tariffs_in_window(self, reg):
        make_pub(reg)
        active = reg.active_tariffs(DATE)
        assert len(active) == 1

    def test_active_excludes_withdrawn(self, reg):
        make_pub(reg, status=UpdateStatus.WITHDRAWN)
        assert reg.active_tariffs(DATE) == []

    def test_active_excludes_future(self, reg):
        reg.publish(
            tariff_name="Future Tariff", fuel="ELECTRICITY",
            tariff_type=TariffType.FIXED, standing_charge_pence_per_day=65.0,
            unit_rate_pence_per_kwh=30.0,
            effective_date=dt.date(2025, 1, 1),
            published_at=NOW, channel=PublicationChannel.WEBSITE,
        )
        assert reg.active_tariffs(DATE) == []

    def test_active_excludes_expired(self, reg):
        reg.publish(
            tariff_name="Expired", fuel="ELECTRICITY",
            tariff_type=TariffType.FIXED, standing_charge_pence_per_day=60.0,
            unit_rate_pence_per_kwh=28.5,
            effective_date=dt.date(2023, 1, 1),
            published_at=NOW, channel=PublicationChannel.WEBSITE,
            end_date=dt.date(2023, 12, 31),
        )
        assert reg.active_tariffs(DATE) == []

    def test_stale_publications(self, reg):
        make_pub(reg, status=UpdateStatus.PENDING)
        stale = reg.stale_publications(NOW + dt.timedelta(hours=50))
        assert len(stale) == 1

    def test_by_channel(self, reg):
        make_pub(reg, channel=PublicationChannel.WEBSITE)
        make_pub(reg, channel=PublicationChannel.OFGEM_FEED)
        make_pub(reg, channel=PublicationChannel.WEBSITE)
        by_ch = reg.by_channel()
        assert by_ch[PublicationChannel.WEBSITE.value] == 2
        assert by_ch[PublicationChannel.OFGEM_FEED.value] == 1

    def test_rate_increases(self, reg):
        make_pub(reg, unit_rate=30.0, prev_rate=28.5)
        make_pub(reg, unit_rate=25.0, prev_rate=28.5)
        increases = reg.rate_increases()
        assert len(increases) == 1

    def test_withdrawn_list(self, reg):
        make_pub(reg)
        make_pub(reg, status=UpdateStatus.WITHDRAWN)
        assert len(reg.withdrawn()) == 1

    def test_cheapest_active(self, reg):
        make_pub(reg, unit_rate=28.5, standing=60.0)
        make_pub(reg, unit_rate=25.0, standing=55.0)
        cheapest = reg.cheapest_active(DATE)
        assert cheapest is not None
        assert cheapest.unit_rate_pence_per_kwh == 25.0

    def test_cheapest_active_none_when_empty(self, reg):
        assert reg.cheapest_active(DATE) is None

    def test_price_transparency_summary(self, reg):
        make_pub(reg)
        s = reg.price_transparency_summary()
        assert "Price Transparency Register" in s

    def test_constants(self):
        assert _MAX_UPDATE_HOURS == 48
        assert _MIN_NOTICE_DAYS_ON_RATE_CHANGE == 30

    def test_svt_no_end_date(self, reg):
        pub = make_pub(reg, tariff_type=TariffType.VARIABLE_SVT, end_date=None)
        # SVT with no end date should still be active
        as_of = dt.date(2030, 1, 1)
        active = reg.active_tariffs(as_of)
        assert len(active) == 1
