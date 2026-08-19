"""Tests for Phase OG: Renewable Obligation (RO) Cost Observatory."""
import pytest
from company.regulatory.roc_ledger import (
    ROCLedger,
    ROCObligationRecord,
    ROCObligationStatus,
    _ROC_OBLIGATION_LEVEL,
    _ROC_BUY_OUT_PRICE_GBP,
)


class TestROCObligationLevel:
    """The published series, not a smooth stand-in for it.

    REPAIRED 2026-08-19. Every assertion in this class used to pin the invented ramp:
    0.317 rising +0.006/yr to 0.389, and a buy-out price escalating ~3.4%/yr. Worse,
    `test_level_increases_each_year` ENFORCED the defect — it asserted the monotonicity
    that the real series does not have, so correcting the table to the published figures
    would have been reported as a regression. The assertions below are chosen to be the
    ones a ramp CANNOT satisfy.
    """

    def test_2016_level(self):
        # DECC, The Renewables Obligation for 2016/17: 0.348 ROCs/MWh in England,
        # Scotland and Wales. Was pinned at 0.317.
        assert _ROC_OBLIGATION_LEVEL[2016] == pytest.approx(0.348)

    def test_2025_level(self):
        # DESNZ, RO level for 2025 to 2026: 0.493 ROCs/MWh in GB. Was pinned at 0.389.
        assert _ROC_OBLIGATION_LEVEL[2025] == pytest.approx(0.493)

    def test_the_level_dips_in_2023_because_a_ramp_cannot(self):
        """The single assertion no monotonic table can pass.

        The GB obligation level fell from 0.491 (OY 2022-23) to 0.469 (OY 2023-24) and
        returned to 0.491. A table that only ever rises is not this series, whatever its
        endpoints are — which is why this replaces the old increases-every-year test
        rather than being added alongside it.
        """
        assert _ROC_OBLIGATION_LEVEL[2023] < _ROC_OBLIGATION_LEVEL[2022]
        assert _ROC_OBLIGATION_LEVEL[2024] > _ROC_OBLIGATION_LEVEL[2023]
        assert _ROC_OBLIGATION_LEVEL[2023] == pytest.approx(0.469)

    def test_buy_out_price_increases(self):
        prices = [_ROC_BUY_OUT_PRICE_GBP[y] for y in sorted(_ROC_BUY_OUT_PRICE_GBP.keys())]
        assert all(prices[i] < prices[i + 1] for i in range(len(prices) - 1))

    def test_the_buy_out_price_spikes_in_2023_not_escalates(self):
        """Monotonicity alone passed on the invented table too; the STEP SIZE does not.

        Ofgem's price went GBP52.88 -> GBP59.01 (+11.6%) -> GBP64.73 (+9.7%). The pinned
        table added ~3.4% a year through exactly those years.
        """
        step = _ROC_BUY_OUT_PRICE_GBP[2023] / _ROC_BUY_OUT_PRICE_GBP[2022] - 1.0
        assert step > 0.08, f"2023-24 buy-out step {step:.1%} — the RPI-ish ramp is back"

    def test_2023_buy_out_price(self):
        # Ofgem RO suppliers page: GBP59.01 for 2023-24. `roc_ledger`'s own docstring
        # cited Ofgem for GBP54.35. A citation is not an agreement.
        assert _ROC_BUY_OUT_PRICE_GBP[2023] == pytest.approx(59.01)


class TestROCObligationRecord:
    def test_rocs_required_formula(self):
        rec = ROCObligationRecord(
            obligation_year=2022,
            total_mwh_supplied=10000.0,
            rocs_required=10000.0 * 0.370,
        )
        assert rec.rocs_required == pytest.approx(3700.0)

    def test_shortfall_when_nothing_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2020, total_mwh_supplied=5000.0,
            rocs_required=1790.0, rocs_surrendered=0.0,
        )
        assert rec.rocs_shortfall == pytest.approx(1790.0)

    def test_no_shortfall_when_fully_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2020, total_mwh_supplied=5000.0,
            rocs_required=1790.0, rocs_surrendered=1790.0,
        )
        assert rec.rocs_shortfall == pytest.approx(0.0)
        assert rec.is_fully_compliant

    def test_buy_out_cost_for_shortfall(self):
        price = _ROC_BUY_OUT_PRICE_GBP[2022]
        rec = ROCObligationRecord(
            obligation_year=2022, total_mwh_supplied=5000.0,
            rocs_required=1850.0, rocs_surrendered=0.0,
        )
        assert rec.buy_out_cost_for_shortfall == pytest.approx(1850.0 * price)

    def test_compliance_pct_zero_when_none_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2019, total_mwh_supplied=3000.0,
            rocs_required=1053.0, rocs_surrendered=0.0,
        )
        assert rec.compliance_pct == pytest.approx(0.0)

    def test_compliance_pct_100_when_fully_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2019, total_mwh_supplied=3000.0,
            rocs_required=1053.0, rocs_surrendered=1053.0,
        )
        assert rec.compliance_pct == pytest.approx(100.0)


class TestROCLedgerOperations:
    def test_create_obligation_computes_rocs(self):
        ledger = ROCLedger()
        ob = ledger.create_obligation(2020, 10000.0)
        assert ob.rocs_required == pytest.approx(10000.0 * _ROC_OBLIGATION_LEVEL[2020])

    def test_total_buy_out_exposure_two_years(self):
        ledger = ROCLedger()
        ob1 = ledger.create_obligation(2022, 5000.0)
        ob2 = ledger.create_obligation(2023, 5100.0)
        expected = ob1.buy_out_cost_for_shortfall + ob2.buy_out_cost_for_shortfall
        assert ledger.total_buy_out_exposure_gbp() == pytest.approx(expected)

    def test_obligation_for_year_retrieval(self):
        ledger = ROCLedger()
        ledger.create_obligation(2021, 4000.0)
        ob = ledger.obligation_for_year(2021)
        assert ob is not None
        assert ob.total_mwh_supplied == pytest.approx(4000.0)

    def test_obligation_for_missing_year_returns_none(self):
        ledger = ROCLedger()
        assert ledger.obligation_for_year(2030) is None

    def test_surrender_marks_compliant(self):
        ledger = ROCLedger()
        ledger.create_obligation(2019, 3000.0)
        rocs_needed = 3000.0 * _ROC_OBLIGATION_LEVEL[2019]
        updated = ledger.surrender_rocs(2019, rocs_needed)
        assert updated is not None
        assert updated.status == ROCObligationStatus.SURRENDERED
        assert updated.is_fully_compliant

    def test_non_compliant_years_empty_when_open(self):
        ledger = ROCLedger()
        ledger.create_obligation(2018, 2000.0)
        assert ledger.non_compliant_years() == []

    def test_roc_ledger_summary_string(self):
        ledger = ROCLedger()
        ledger.create_obligation(2021, 4000.0)
        summary = ledger.roc_ledger_summary()
        assert "1 obligation years" in summary
        assert "GBP" in summary


class TestROCBoardSection:
    def _make_data(self, stale: bool = False):
        """The section's data as a run freezes it.

        The default is now the PUBLISHED rates (0.491 / £52.88 and 0.469 / £59.01), because
        a fixture stating the 2022-23 obligation level as 0.370 was itself a copy of the
        defect. `stale=True` restores the shipped-and-wrong rates, which is what the
        correction-block tests below are for.
        """
        if stale:
            y2022 = {
                "elec_mwh": 5000.0, "rocs_required": 1850.0,
                "obligation_level": 0.370, "buy_out_price_gbp": 52.88,
                "buy_out_cost_gbp": 97828.0,
            }
            y2023 = {
                "elec_mwh": 5100.0, "rocs_required": 1917.6,
                "obligation_level": 0.376, "buy_out_price_gbp": 54.35,
                "buy_out_cost_gbp": 104242.0,
            }
        else:
            y2022 = {
                "elec_mwh": 5000.0, "rocs_required": 2455.0,
                "obligation_level": 0.491, "buy_out_price_gbp": 52.88,
                "buy_out_cost_gbp": 129820.0,
            }
            y2023 = {
                "elec_mwh": 5100.0, "rocs_required": 2391.9,
                "obligation_level": 0.469, "buy_out_price_gbp": 59.01,
                "buy_out_cost_gbp": 141146.0,
            }
        return {
            "roc_summary": {
                "total_buy_out_cost_gbp": 270966.0,
                "per_year": {"2022": y2022, "2023": y2023},
            },
            "management_accounts": {
                "2022": {"income_statement": {"revenue_gbp": 1500000.0}},
                "2023": {"income_statement": {"revenue_gbp": 1600000.0}},
            },
        }

    def _render(self, stale: bool = False):
        from saas.reporting.annual_report import _section_roc_obligations
        return _section_roc_obligations(self._make_data(stale=stale))

    def test_section_renders(self):
        out = self._render()
        assert "Renewable Obligation" in out

    def test_section_shows_years(self):
        out = self._render()
        assert "2022" in out
        assert "2023" in out

    def test_section_shows_mwh(self):
        out = self._render()
        assert "5,000" in out or "5000" in out

    def test_section_shows_buy_out_cost(self):
        out = self._render()
        assert "129,820" in out or "129820" in out

    def test_section_shows_revenue_pct(self):
        out = self._render()
        assert "%" in out

    def test_section_empty_without_data(self):
        from saas.reporting.annual_report import _section_roc_obligations
        assert _section_roc_obligations({}) == ""

    def test_section_shows_total_row(self):
        out = self._render()
        assert "Total" in out


class TestROCObservatorySelfCheck:
    """R15 on the renderer's own correction block, both ways.

    THE DEFECT (2026-08-19): the section rendered the run's frozen rates without ever asking
    whether they were the published ones, and published GBP1,267,231 against a published-
    constants figure of GBP1,753,689 for months. Repairing the constants alone would NOT have
    repaired this page, because `run_output_latest.json` is frozen at the run that wrote it —
    so the page would have stayed wrong until some later run happened to land.
    """

    def _render(self, stale: bool):
        from saas.reporting.annual_report import _section_roc_obligations
        return _section_roc_obligations(TestROCBoardSection()._make_data(stale=stale))

    def test_mutation_stale_rates_are_declared_on_the_page(self):
        """THE NAMED DEFECT, replayed. Freeze the shipped rates and the page must say so."""
        out = self._render(stale=True)
        assert "NOT THE PUBLISHED ONES" in out
        assert "2022" in out and "2023" in out

    def test_the_correction_states_the_corrected_total_not_just_a_warning(self):
        """A warning with no number is not a correction: a reader cannot act on 'may be wrong'."""
        out = self._render(stale=True)
        # 5000 x 0.491 x 52.88 + 5100 x 0.469 x 59.01, on the run's OWN volumes
        assert "£270,966" in out, out[-900:]

    def test_null_control_correct_rates_render_no_correction_block(self):
        """The block must be caused by the DISAGREEMENT, not by the block existing.

        Without this, a renderer that always warned would pass the mutation above.
        """
        out = self._render(stale=False)
        assert "NOT THE PUBLISHED ONES" not in out
        assert "Renewable Obligation" in out

    def test_the_check_reads_the_commons_not_the_frozen_rate(self, monkeypatch):
        """INDEPENDENCE (R15 tautology guard). Move the published series and the verdict moves.

        If the section compared the frozen rate to itself — which is what rendering it
        unchecked amounts to — this would still report clean.
        """
        from saas.reporting import annual_report
        from company.regulatory import roc_ledger

        monkeypatch.setitem(roc_ledger._ROC_OBLIGATION_LEVEL, 2022, 0.491)
        monkeypatch.setitem(roc_ledger._ROC_OBLIGATION_LEVEL, 2023, 0.469)
        assert "NOT THE PUBLISHED ONES" not in annual_report._section_roc_obligations(
            TestROCBoardSection()._make_data(stale=False)
        )
        # now move the LAW, leaving the frozen run data alone
        monkeypatch.setitem(roc_ledger._ROC_OBLIGATION_LEVEL, 2022, 0.777)
        assert "NOT THE PUBLISHED ONES" in annual_report._section_roc_obligations(
            TestROCBoardSection()._make_data(stale=False)
        )

    def test_a_year_the_commons_does_not_cover_is_silence_not_a_correction(self):
        """Absence of a pin is not evidence of disagreement. A year outside the commons'
        window must not be reported as a stale rate — that would be a fail-LOUD defect, and
        it would train readers to ignore the block."""
        from saas.reporting.annual_report import _section_roc_obligations

        data = TestROCBoardSection()._make_data(stale=False)
        data["roc_summary"]["per_year"]["1999"] = {
            "elec_mwh": 100.0, "rocs_required": 0.0,
            "obligation_level": 0.0, "buy_out_price_gbp": 0.0,
            "buy_out_cost_gbp": 0.0,
        }
        assert "NOT THE PUBLISHED ONES" not in _section_roc_obligations(data)
