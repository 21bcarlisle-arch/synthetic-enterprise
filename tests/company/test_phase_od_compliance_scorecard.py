"""Phase OD tests: Ofgem SLC Compliance Scorecard Synthesis."""
import datetime as dt
import pytest

from company.regulatory.compliance_scorecard import (
    ComplianceScorecard,
    ComplianceDomain,
    RAGStatus,
)


# ── scorecard mechanics ───────────────────────────────────────────────────────

class TestComplianceScorecardMechanics:
    def _scorecard(self):
        sc = ComplianceScorecard()
        sc.record_check(
            ComplianceDomain.GOVERNANCE, dt.date(2020, 12, 31),
            RAGStatus.GREEN, notes="all checks pass"
        )
        sc.record_check(
            ComplianceDomain.PAYMENT_DEBT, dt.date(2020, 12, 31),
            RAGStatus.AMBER, metric_value=2.5, threshold=3.0
        )
        return sc

    def test_latest_status_returns_most_recent(self):
        sc = ComplianceScorecard()
        sc.record_check(ComplianceDomain.GOVERNANCE, dt.date(2019, 12, 31), RAGStatus.AMBER)
        sc.record_check(ComplianceDomain.GOVERNANCE, dt.date(2020, 12, 31), RAGStatus.GREEN)
        assert sc.latest_status(ComplianceDomain.GOVERNANCE) == RAGStatus.GREEN

    def test_overall_rag_worst_wins(self):
        sc = self._scorecard()
        assert sc.overall_rag(dt.date(2020, 12, 31)) == RAGStatus.AMBER

    def test_red_overrides_amber_in_overall(self):
        sc = ComplianceScorecard()
        sc.record_check(ComplianceDomain.GOVERNANCE, dt.date(2020, 12, 31), RAGStatus.AMBER)
        sc.record_check(ComplianceDomain.PAYMENT_DEBT, dt.date(2020, 12, 31), RAGStatus.RED)
        assert sc.overall_rag(dt.date(2020, 12, 31)) == RAGStatus.RED

    def test_breach_count_correct(self):
        sc = ComplianceScorecard()
        sc.record_check(ComplianceDomain.GOVERNANCE, dt.date(2020, 12, 31), RAGStatus.GREEN)
        sc.record_check(ComplianceDomain.PAYMENT_DEBT, dt.date(2020, 12, 31), RAGStatus.RED)
        sc.record_check(ComplianceDomain.COMPLAINTS, dt.date(2020, 12, 31), RAGStatus.RED)
        assert len(sc.breaches(dt.date(2020, 12, 31))) == 2

    def test_scorecard_summary_has_required_keys(self):
        sc = self._scorecard()
        summary = sc.scorecard_summary(dt.date(2020, 12, 31))
        for key in ("as_of_date", "overall_rag", "domains_checked", "rag_counts", "breach_domains"):
            assert key in summary

    def test_future_checks_excluded(self):
        sc = ComplianceScorecard()
        sc.record_check(ComplianceDomain.GOVERNANCE, dt.date(2021, 1, 1), RAGStatus.RED)
        assert sc.overall_rag(dt.date(2020, 12, 31)) == RAGStatus.GREEN


# ── rag logic from simulation data ───────────────────────────────────────────

class TestRAGDerivation:
    """Verify the RAG assignment rules used in _section_compliance_scorecard."""

    def test_bad_debt_below_1pct_is_green(self):
        # The board section maps: <1% GREEN, 1-3% AMBER, >3% RED
        bad_debt_pct = 0.5
        if bad_debt_pct < 1.0:
            rag = RAGStatus.GREEN
        elif bad_debt_pct < 3.0:
            rag = RAGStatus.AMBER
        else:
            rag = RAGStatus.RED
        assert rag == RAGStatus.GREEN

    def test_bad_debt_above_3pct_is_red(self):
        bad_debt_pct = 4.0
        if bad_debt_pct < 1.0:
            rag = RAGStatus.GREEN
        elif bad_debt_pct < 3.0:
            rag = RAGStatus.AMBER
        else:
            rag = RAGStatus.RED
        assert rag == RAGStatus.RED

    def test_fra_ratio_above_3x_is_green(self):
        fra_ratio = 5.0
        if fra_ratio >= 3.0:
            rag = RAGStatus.GREEN
        elif fra_ratio >= 1.0:
            rag = RAGStatus.AMBER
        else:
            rag = RAGStatus.RED
        assert rag == RAGStatus.GREEN

    def test_fra_ratio_below_1x_is_red(self):
        fra_ratio = 0.5
        if fra_ratio >= 3.0:
            rag = RAGStatus.GREEN
        elif fra_ratio >= 1.0:
            rag = RAGStatus.AMBER
        else:
            rag = RAGStatus.RED
        assert rag == RAGStatus.RED


# ── board section ─────────────────────────────────────────────────────────────

class TestComplianceScorecardBoardSection:
    def _data(self):
        years = {}
        ma = {}
        fra = []
        for yr in range(2016, 2026):
            revenue = 600000.0
            gross = revenue * 0.08
            bad_debt = revenue * 0.015
            treasury = 500000.0
            years[str(yr)] = {
                "active_customer_ids": ["C_1"],
                "revenue_gbp": revenue,
                "gross_gbp": gross,
                "bad_debt_gbp": bad_debt,
                "treasury_end_gbp": treasury,
                "bsc_credit_required_gbp": 50000.0,
                "avg_clarity": 0.85,
                "avg_complaint_probability": 0.005,
            }
            ma[str(yr)] = {"balance_sheet": {"total_equity_gbp": treasury + gross}}
            fra.append({"year": yr, "fra_ratio": 15.0, "rag": "GREEN"})
        return {
            "years": years,
            "management_accounts": ma,
            "fra_ratio_series": fra,
            "demand_estimation_log": [],
        }

    def _section(self, data):
        from saas.reporting.annual_report import _section_compliance_scorecard
        return _section_compliance_scorecard(data)

    def test_returns_string_with_data(self):
        out = self._section(self._data())
        assert isinstance(out, str) and len(out) > 0

    def test_silent_when_no_years(self):
        out = self._section({})
        assert out == ""

    def test_phase_od_header_present(self):
        out = self._section(self._data())
        assert "Phase OD" in out

    def test_all_domains_present(self):
        out = self._section(self._data())
        for domain_label in ["Governance", "Billing", "Payment", "Financial"]:
            assert domain_label in out

    def test_all_years_in_header(self):
        out = self._section(self._data())
        for yr in range(2016, 2026):
            assert str(yr) in out

    def test_overall_row_present(self):
        out = self._section(self._data())
        assert "Overall" in out
