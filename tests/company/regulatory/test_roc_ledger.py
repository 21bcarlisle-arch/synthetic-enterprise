"""Tests for Renewable Obligation Certificate (ROC) Ledger (Phase FH)."""
import datetime as dt
import pytest
from company.regulatory.roc_ledger import (
    ROCObligationStatus, ROCObligationRecord, ROCLedger,
    _ROC_OBLIGATION_LEVEL, _ROC_BUY_OUT_PRICE_GBP,
)

YEAR = 2023


class TestROCObligationRecord:
    def test_rocs_shortfall(self):
        r = ROCObligationRecord(YEAR, 10000.0, rocs_required=376.0,
                                rocs_surrendered=300.0)
        assert r.rocs_shortfall == pytest.approx(76.0)

    def test_no_shortfall_when_compliant(self):
        r = ROCObligationRecord(YEAR, 10000.0, rocs_required=376.0,
                                rocs_surrendered=376.0)
        assert r.rocs_shortfall == pytest.approx(0.0)

    def test_buy_out_cost(self):
        r = ROCObligationRecord(YEAR, 10000.0, rocs_required=376.0,
                                rocs_surrendered=0.0)
        expected = 376.0 * _ROC_BUY_OUT_PRICE_GBP[YEAR]
        assert r.buy_out_cost_for_shortfall == pytest.approx(expected)

    def test_is_fully_compliant(self):
        r = ROCObligationRecord(YEAR, 10000.0, rocs_required=376.0,
                                rocs_surrendered=376.0)
        assert r.is_fully_compliant

    def test_not_fully_compliant(self):
        r = ROCObligationRecord(YEAR, 10000.0, rocs_required=376.0,
                                rocs_surrendered=200.0)
        assert not r.is_fully_compliant

    def test_compliance_pct(self):
        r = ROCObligationRecord(YEAR, 10000.0, rocs_required=400.0,
                                rocs_surrendered=300.0)
        assert r.compliance_pct == pytest.approx(75.0)

    def test_obligation_summary(self):
        r = ROCObligationRecord(YEAR, 10000.0, rocs_required=376.0)
        s = r.obligation_summary()
        assert "ROC" in s and str(YEAR) in s


class TestROCLedger:
    def test_create_obligation(self):
        ledger = ROCLedger()
        o = ledger.create_obligation(YEAR, 10000.0)
        expected_rocs = 10000.0 * _ROC_OBLIGATION_LEVEL[YEAR]
        assert o.rocs_required == pytest.approx(expected_rocs)

    def test_surrender_full_compliance(self):
        ledger = ROCLedger()
        o = ledger.create_obligation(YEAR, 10000.0)
        updated = ledger.surrender_rocs(YEAR, o.rocs_required)
        assert updated.status == ROCObligationStatus.SURRENDERED
        assert updated.is_fully_compliant

    def test_surrender_partial(self):
        ledger = ROCLedger()
        ledger.create_obligation(YEAR, 10000.0)
        updated = ledger.surrender_rocs(YEAR, 100.0)
        assert updated.status == ROCObligationStatus.PARTIALLY_SURRENDERED

    def test_non_compliant_years(self):
        ledger = ROCLedger()
        ledger.create_obligation(YEAR, 10000.0)
        ledger.surrender_rocs(YEAR, 100.0)
        assert len(ledger.non_compliant_years()) == 1

    def test_total_buy_out_exposure(self):
        ledger = ROCLedger()
        ledger.create_obligation(YEAR, 10000.0)
        # No surrender yet -> exposure = rocs_required * buy_out_price
        exposure = ledger.total_buy_out_exposure_gbp()
        assert exposure > 0

    def test_roc_ledger_summary(self):
        ledger = ROCLedger()
        ledger.create_obligation(YEAR, 10000.0)
        s = ledger.roc_ledger_summary()
        assert "ROC Ledger" in s
