# Increment 3: the legs of tests/company/test_phase_in_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IN: deeper coverage for network_charge_ledger, carbon_emissions, ofgem_supply_return."""
import datetime as dt
import pytest

# ===== network_charge_ledger =====
from company.market.network_charge_ledger import (
    NetworkChargeLedger, NetworkChargeType
)


def _ledger():
    ledger = NetworkChargeLedger()
    ledger.set_rate(2022, NetworkChargeType.TNUOS, "electricity", 25.0)
    ledger.set_rate(2022, NetworkChargeType.DUOS, "electricity", 15.0)
    ledger.post_charge("C1", "M001", dt.date(2022,1,1), dt.date(2022,3,31),
                        NetworkChargeType.TNUOS, 10.0, 25.0)
    ledger.post_charge("C1", "M001", dt.date(2022,1,1), dt.date(2022,3,31),
                        NetworkChargeType.DUOS, 10.0, 15.0)
    ledger.post_charge("C2", "M002", dt.date(2022,4,1), dt.date(2022,6,30),
                        NetworkChargeType.BSUOS, 5.0, 8.0)
    return ledger


class TestNetworkChargeLedger:
    def test_get_rate_returns_latest(self):
        ledger = _ledger()
        assert ledger.get_rate(2022, NetworkChargeType.TNUOS, "electricity") == pytest.approx(25.0)

    def test_get_rate_none_when_absent(self):
        ledger = _ledger()
        assert ledger.get_rate(2023, NetworkChargeType.TNUOS, "electricity") is None

    def test_charge_gbp(self):
        ledger = _ledger()
        rec = ledger._records[0]
        assert rec.charge_gbp == pytest.approx(250.0)  # 10 MWh * 25

    def test_total_charges_gbp_for_customer(self):
        ledger = _ledger()
        total = ledger.total_charges_gbp("C1", dt.date(2022,1,1), dt.date(2022,3,31))
        assert total == pytest.approx(400.0)  # 250 + 150

    def test_total_charges_gbp_no_overlap(self):
        ledger = _ledger()
        total = ledger.total_charges_gbp("C1", dt.date(2023,1,1), dt.date(2023,3,31))
        assert total == pytest.approx(0.0)

    def test_charges_by_type(self):
        ledger = _ledger()
        by_type = ledger.charges_by_type(2022)
        assert "tnuos" in by_type and "duos" in by_type

    def test_portfolio_total_gbp(self):
        ledger = _ledger()
        total = ledger.portfolio_total_gbp(2022)
        # TNUoS=250, DUoS=150, BSUoS=40
        assert total == pytest.approx(440.0)

    def test_annual_summary_keys(self):
        ledger = _ledger()
        s = ledger.annual_summary(2022)
        assert "total_gbp" in s and "by_type" in s and "record_count" in s

    def test_annual_summary_record_count(self):
        ledger = _ledger()
        s = ledger.annual_summary(2022)
        assert s["record_count"] == 3

    def test_charges_by_type_bsuos(self):
        ledger = _ledger()
        by_type = ledger.charges_by_type(2022)
        assert by_type.get("bsuos") == pytest.approx(40.0)  # 5*8
