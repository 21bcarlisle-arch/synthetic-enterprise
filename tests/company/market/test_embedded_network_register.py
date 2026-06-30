"""Tests for Embedded Network Supply Register (Phase DO)."""
import datetime as dt
import pytest
from company.market.embedded_network_register import (
    EmbeddedNetworkType, ENOStatus, EmbeddedNetworkRecord,
    EmbeddedNetworkRegister,
    _MAX_EMBEDDED_RATE_PCT_ABOVE_DNO, _MIN_SWITCHING_NOTICE_DAYS,
)


@pytest.fixture
def reg():
    return EmbeddedNetworkRegister()


DATE = dt.date(2023, 6, 1)
PARENT_MPAN = "1012345678901"


def register_en(reg, rate=28.5, dno_rate=25.0, unit_count=20,
                network_type=EmbeddedNetworkType.RESIDENTIAL_BLOCK,
                status=ENOStatus.ACTIVE):
    return reg.register(
        network_type=network_type,
        eno_name="BlockCo Ltd",
        parent_mpan=PARENT_MPAN,
        unit_count=unit_count,
        registered_at=DATE,
        rate_pence_per_kwh=rate,
        dno_rate_pence_per_kwh=dno_rate,
        status=status,
    )


class TestEmbeddedNetworkRecord:
    def test_is_active_status(self, reg):
        rec = register_en(reg, status=ENOStatus.ACTIVE)
        assert rec.is_active

    def test_terminated_not_active(self, reg):
        rec = register_en(reg, status=ENOStatus.TERMINATED)
        assert not rec.is_active

    def test_rate_premium_pct(self, reg):
        # 28.5 / 25.0 - 1 = 14%
        rec = register_en(reg, rate=28.5, dno_rate=25.0)
        assert rec.rate_premium_pct == pytest.approx(14.0)

    def test_rate_compliant_under_limit(self, reg):
        rec = register_en(reg, rate=28.5, dno_rate=25.0)  # 14% < 20%
        assert rec.is_rate_compliant

    def test_rate_non_compliant_over_limit(self, reg):
        # 30 / 25 - 1 = 20%, same as limit = compliant
        rec = register_en(reg, rate=30.0, dno_rate=25.0)  # exactly 20%
        assert rec.is_rate_compliant

    def test_rate_non_compliant_above_limit(self, reg):
        # 30.1 / 25 = 20.4% > 20%
        rec = register_en(reg, rate=30.1, dno_rate=25.0)
        assert not rec.is_rate_compliant

    def test_rate_excess_pct_non_compliant(self, reg):
        rec = register_en(reg, rate=31.0, dno_rate=25.0)  # 24% premium
        excess = rec.rate_excess_pct
        assert excess == pytest.approx(4.0)

    def test_rate_excess_pct_zero_when_compliant(self, reg):
        rec = register_en(reg, rate=28.0, dno_rate=25.0)
        assert rec.rate_excess_pct == pytest.approx(0.0)

    def test_zero_dno_rate_returns_zero_premium(self, reg):
        rec = register_en(reg, rate=28.5, dno_rate=0.0)
        assert rec.rate_premium_pct == pytest.approx(0.0)

    def test_network_id_assigned(self, reg):
        rec = register_en(reg)
        assert rec.network_id.startswith("EN-")


class TestEmbeddedNetworkRegister:
    def test_get_by_id(self, reg):
        rec = register_en(reg)
        assert reg.get(rec.network_id) is rec

    def test_get_missing_returns_none(self, reg):
        assert reg.get("EN-9999") is None

    def test_sequential_ids(self, reg):
        r1 = register_en(reg)
        r2 = register_en(reg)
        assert r1.network_id != r2.network_id

    def test_terminate(self, reg):
        rec = register_en(reg)
        terminated = reg.terminate(rec.network_id, dt.date(2024, 1, 1))
        assert terminated.status == ENOStatus.TERMINATED
        assert terminated.end_date == dt.date(2024, 1, 1)

    def test_active_networks_excludes_terminated(self, reg):
        r1 = register_en(reg)
        register_en(reg, status=ENOStatus.TERMINATED)
        active = reg.active_networks()
        assert len(active) == 1
        assert active[0].network_id == r1.network_id

    def test_non_compliant_rates(self, reg):
        register_en(reg, rate=28.0, dno_rate=25.0)  # 12% compliant
        register_en(reg, rate=31.0, dno_rate=25.0)  # 24% non-compliant
        assert len(reg.non_compliant_rates()) == 1

    def test_total_units(self, reg):
        register_en(reg, unit_count=15)
        register_en(reg, unit_count=25)
        assert reg.total_units() == 40

    def test_terminated_units_excluded(self, reg):
        register_en(reg, unit_count=15)
        register_en(reg, unit_count=25, status=ENOStatus.TERMINATED)
        assert reg.total_units() == 15

    def test_by_type_aggregates_units(self, reg):
        register_en(reg, unit_count=10, network_type=EmbeddedNetworkType.RESIDENTIAL_BLOCK)
        register_en(reg, unit_count=5, network_type=EmbeddedNetworkType.COMMERCIAL_PARK)
        register_en(reg, unit_count=8, network_type=EmbeddedNetworkType.RESIDENTIAL_BLOCK)
        by_type = reg.by_type()
        assert by_type[EmbeddedNetworkType.RESIDENTIAL_BLOCK.value] == 18
        assert by_type[EmbeddedNetworkType.COMMERCIAL_PARK.value] == 5

    def test_terminated_networks_list(self, reg):
        register_en(reg, status=ENOStatus.TERMINATED)
        register_en(reg)
        assert len(reg.terminated_networks()) == 1

    def test_constants(self):
        assert _MAX_EMBEDDED_RATE_PCT_ABOVE_DNO == 20.0
        assert _MIN_SWITCHING_NOTICE_DAYS == 28

    def test_embedded_network_summary(self, reg):
        register_en(reg)
        s = reg.embedded_network_summary()
        assert "Embedded Network Register" in s
        assert "20" in s  # references 20% cap

    def test_empty_register_summary(self, reg):
        s = reg.embedded_network_summary()
        assert "0 active" in s
