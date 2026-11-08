"""Tests for BSC Settlement Run Tracking Register (Phase DH)."""
import datetime as dt

import pytest
from dateutil.relativedelta import relativedelta

from company.market.bsc_settlement_run_register import (
    _MATERIAL_VARIANCE_THRESHOLD,
    _SETTLEMENT_RUN_MONTHS,
    AdjustmentDirection,
    BSCSettlementRunRegister,
    SettlementRunRecord,
    SettlementRunType,
)
from company.regulatory.settlement_reconciliation import ELEXON_RUN_MONTHS


@pytest.fixture
def reg():
    return BSCSettlementRunRegister()


SD = dt.date(2023, 1, 15)      # settlement date
RECV = dt.date(2023, 1, 29)    # when SF PCAN received


class TestSettlementRunRecord:
    def test_sf_no_adjustment(self, reg):
        rec = reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0)
        assert rec.adjustment_gbp == pytest.approx(0.0)
        assert rec.direction == AdjustmentDirection.NIL

    def test_r1_credit(self, reg):
        rec = reg.record_run(SD, SettlementRunType.R1,
                             dt.date(2023, 6, 15), 980.0, 240.0, prior_charges_gbp=250.0)
        assert rec.adjustment_gbp == pytest.approx(-10.0)
        assert rec.direction == AdjustmentDirection.CREDIT

    def test_r1_debit(self, reg):
        rec = reg.record_run(SD, SettlementRunType.R1,
                             dt.date(2023, 6, 15), 1020.0, 265.0, prior_charges_gbp=250.0)
        assert rec.adjustment_gbp == pytest.approx(15.0)
        assert rec.direction == AdjustmentDirection.DEBIT

    def test_nil_adjustment_within_threshold(self, reg):
        rec = reg.record_run(SD, SettlementRunType.R1,
                             dt.date(2023, 6, 15), 1000.0, 250.005, prior_charges_gbp=250.0)
        assert rec.direction == AdjustmentDirection.NIL

    def test_variance_pct_sf_is_none(self, reg):
        rec = reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0)
        assert rec.variance_pct is None

    def test_variance_pct_r2(self, reg):
        rec = reg.record_run(SD, SettlementRunType.R2,
                             dt.date(2024, 3, 15), 1100.0, 280.0, prior_charges_gbp=250.0)
        expected = abs(280.0 - 250.0) / 250.0
        assert rec.variance_pct == pytest.approx(expected)

    def test_is_material_above_threshold(self, reg):
        rec = reg.record_run(SD, SettlementRunType.R2,
                             dt.date(2024, 3, 15), 1100.0, 280.0, prior_charges_gbp=250.0)
        assert rec.is_material

    def test_not_material_below_threshold(self, reg):
        # 2% variance
        rec = reg.record_run(SD, SettlementRunType.R1,
                             dt.date(2023, 6, 15), 1000.0, 255.0, prior_charges_gbp=250.0)
        assert not rec.is_material

    def test_is_final_rf_only(self, reg):
        rf = reg.record_run(SD, SettlementRunType.RF,
                            dt.date(2025, 5, 1), 1000.0, 252.0, prior_charges_gbp=250.0)
        r3 = reg.record_run(SD, SettlementRunType.R3,
                            dt.date(2025, 3, 1), 1000.0, 251.0, prior_charges_gbp=250.0)
        assert rf.is_final
        assert not r3.is_final

    def test_pcan_reference_stored(self, reg):
        rec = reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0,
                             pcan_reference="PCAN-2023-001")
        assert rec.pcan_reference == "PCAN-2023-001"

    # THE DEFECT THESE NAME. Until 2026-09-06 the three tests here were
    # `test_expected_run_date_sf` / `_r1_five_months` / `_rf_28_months`, each
    # pinning one hand-typed month figure -- 0, 5 and 28 -- to a literal date.
    # Every one of those figures was wrong against Elexon's published timetable,
    # and because the control was keyed to TODAY'S ANSWER rather than to the
    # property, all three passed for as long as the module stayed wrong and
    # would have gone red on the day it was corrected. That is exactly backwards.
    # Keyed to the property instead: the run date is the SOURCED lag applied to
    # the settlement date, for every run, whatever Elexon's figures become.

    def test_every_runs_expected_date_is_the_SOURCED_lag_from_the_settlement_date(self, reg):
        # Month arithmetic done by a different route from the subject's own
        # (relativedelta, not hand-rolled modulo), so agreement is evidence
        # rather than a mirror of the implementation.
        settlement_date = dt.date(2023, 1, 17)
        for run in SettlementRunType:
            rec = reg.record_run(settlement_date, run, RECV, 1000.0, 250.0)
            expected = (settlement_date
                        + relativedelta(months=ELEXON_RUN_MONTHS[run.value])).replace(day=1)
            assert rec.expected_run_date == expected, (
                f"{run.value}: expected {expected}, got {rec.expected_run_date}"
            )

    def test_the_register_holds_NO_timetable_of_its_own(self, reg):
        # The finding this file's module docstring records: one legal timetable,
        # four implementations, a sourced correction that reached two of them.
        # This is the leg that makes a fifth copy here impossible -- it goes red
        # if the map is ever re-typed, and stays green when Elexon's own numbers
        # change, because both sides move together.
        assert _SETTLEMENT_RUN_MONTHS == {
            run: ELEXON_RUN_MONTHS[run.value] for run in SettlementRunType
        }


class TestBSCSettlementRunRegisterQueries:
    def test_runs_for_date(self, reg):
        reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0)
        reg.record_run(SD, SettlementRunType.R1, dt.date(2023, 6, 1), 1000.0, 248.0, 250.0)
        reg.record_run(dt.date(2022, 3, 1), SettlementRunType.SF, dt.date(2022, 3, 15), 500.0, 120.0)
        runs = reg.runs_for_date(SD)
        assert len(runs) == 2

    def test_by_run_type(self, reg):
        reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0)
        reg.record_run(dt.date(2022, 3, 1), SettlementRunType.SF, dt.date(2022, 3, 15), 500.0, 120.0)
        reg.record_run(SD, SettlementRunType.R1, dt.date(2023, 6, 1), 1000.0, 248.0, 250.0)
        sf_runs = reg.by_run_type(SettlementRunType.SF)
        assert len(sf_runs) == 2

    def test_material_variances(self, reg):
        reg.record_run(SD, SettlementRunType.R2,
                       dt.date(2024, 3, 1), 1100.0, 280.0, prior_charges_gbp=250.0)
        reg.record_run(SD, SettlementRunType.R1,
                       dt.date(2023, 6, 1), 1000.0, 252.0, prior_charges_gbp=250.0)
        material = reg.material_variances()
        assert len(material) == 1
        assert material[0].run_type == SettlementRunType.R2

    def test_credits(self, reg):
        reg.record_run(SD, SettlementRunType.R1,
                       dt.date(2023, 6, 1), 980.0, 240.0, prior_charges_gbp=250.0)
        reg.record_run(SD, SettlementRunType.R2,
                       dt.date(2024, 3, 1), 990.0, 235.0, prior_charges_gbp=240.0)
        assert len(reg.credits()) == 2

    def test_debits(self, reg):
        reg.record_run(SD, SettlementRunType.R1,
                       dt.date(2023, 6, 1), 1020.0, 265.0, prior_charges_gbp=250.0)
        assert len(reg.debits()) == 1

    def test_total_adjustment_excludes_sf(self, reg):
        reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0)
        reg.record_run(SD, SettlementRunType.R1,
                       dt.date(2023, 6, 1), 1020.0, 265.0, prior_charges_gbp=250.0)
        assert reg.total_adjustment_gbp() == pytest.approx(15.0)

    def test_total_credit_debit(self, reg):
        reg.record_run(SD, SettlementRunType.R1,
                       dt.date(2023, 6, 1), 980.0, 240.0, prior_charges_gbp=250.0)
        assert reg.total_credit_gbp() == pytest.approx(10.0)
        assert reg.total_debit_gbp() == pytest.approx(0.0)

    def test_finalised_dates(self, reg):
        reg.record_run(SD, SettlementRunType.RF,
                       dt.date(2025, 5, 1), 1000.0, 251.0, prior_charges_gbp=250.0)
        reg.record_run(SD, SettlementRunType.R3,
                       dt.date(2025, 3, 1), 1000.0, 250.5, prior_charges_gbp=250.0)
        finalised = reg.finalised_dates()
        assert SD in finalised
        assert len(finalised) == 1

    def test_run_type_breakdown(self, reg):
        reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0)
        reg.record_run(SD, SettlementRunType.R1,
                       dt.date(2023, 6, 1), 1000.0, 248.0, prior_charges_gbp=250.0)
        breakdown = reg.run_type_breakdown()
        assert breakdown[SettlementRunType.SF.value] == 1
        assert breakdown[SettlementRunType.R1.value] == 1

    def test_settlement_summary_string(self, reg):
        reg.record_run(SD, SettlementRunType.SF, RECV, 1000.0, 250.0)
        s = reg.settlement_summary()
        assert "BSC Settlement Run Register" in s
        assert "1" in s

    def test_material_variance_threshold_constant(self):
        assert _MATERIAL_VARIANCE_THRESHOLD == 0.05

    def test_empty_register_summary(self, reg):
        s = reg.settlement_summary()
        assert "0 runs" in s
