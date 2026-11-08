import pytest
from company.risk.gas_procurement_policy import (
    GasProcurementStatus,
    GasCoverTarget,
    GasProcurementCheck,
    GasProcurementPolicyBook,
    GAS_MIN_COVER_PCT,
    GAS_STOP_LOSS_SBP_THRESHOLD_GBP_PER_MWH,
)


def _check(obligation=100.0, cover=85.0, sbp=20.0, date="2022-06-01"):
    return GasProcurementCheck(
        check_date=date,
        supply_obligation_mwh=obligation,
        forward_cover_mwh=cover,
        nbp_sbp_gbp_per_mwh=sbp,
    )


_target_2022 = GasCoverTarget(year=2022, min_cover_pct=0.85, max_cover_pct=1.05)
_target_std = GasCoverTarget(year=2020, min_cover_pct=0.80, max_cover_pct=1.05)


class TestGasProcurementCheck:
    def test_cover_pct_calculated(self):
        c = _check(obligation=100.0, cover=80.0)
        assert c.cover_pct == pytest.approx(0.80)

    def test_cover_pct_zero_obligation_returns_one(self):
        c = _check(obligation=0.0, cover=0.0)
        assert c.cover_pct == pytest.approx(1.0)

    def test_status_compliant(self):
        c = _check(obligation=100.0, cover=85.0, sbp=20.0)
        assert c.status(_target_2022) == GasProcurementStatus.COMPLIANT

    def test_status_short_cover(self):
        c = _check(obligation=100.0, cover=50.0, sbp=20.0)
        assert c.status(_target_std) == GasProcurementStatus.SHORT_COVER

    def test_status_over_hedged(self):
        c = _check(obligation=100.0, cover=110.0, sbp=20.0)
        assert c.status(_target_std) == GasProcurementStatus.OVER_HEDGED

    def test_status_stop_loss_alert_overrides(self):
        # Even if compliant on cover, crisis SBP triggers STOP_LOSS_ALERT
        c = _check(obligation=100.0, cover=90.0, sbp=GAS_STOP_LOSS_SBP_THRESHOLD_GBP_PER_MWH + 1)
        assert c.status(_target_std) == GasProcurementStatus.STOP_LOSS_ALERT

    def test_is_crisis_alert_false(self):
        c = _check(sbp=50.0)
        assert not c.is_crisis_alert

    def test_is_crisis_alert_true(self):
        c = _check(sbp=GAS_STOP_LOSS_SBP_THRESHOLD_GBP_PER_MWH + 0.01)
        assert c.is_crisis_alert

    def test_shortfall_zero_when_compliant(self):
        c = _check(obligation=100.0, cover=85.0)
        assert c.shortfall_mwh(_target_2022) == 0.0

    def test_shortfall_when_short(self):
        # min = 100 * 0.80 = 80; cover = 60; shortfall = 20
        c = _check(obligation=100.0, cover=60.0)
        assert c.shortfall_mwh(_target_std) == pytest.approx(20.0)

    def test_frozen(self):
        c = _check()
        with pytest.raises((AttributeError, TypeError)):
            c.supply_obligation_mwh = 999.0


class TestGasProcurementPolicyBook:
    def _book_with_checks(self):
        book = GasProcurementPolicyBook()
        book.check_cover("2022-01-15", 100.0, 50.0, 20.0, 2022)   # short (50% < 85%)
        book.check_cover("2022-06-15", 100.0, 90.0, 190.0, 2022)  # stop-loss alert
        book.check_cover("2022-09-15", 100.0, 88.0, 20.0, 2022)   # compliant
        return book

    def test_cover_target_year_known(self):
        book = GasProcurementPolicyBook()
        t = book.cover_target_for_year(2022)
        assert t.min_cover_pct == pytest.approx(0.85)

    def test_cover_target_default_for_unknown_year(self):
        book = GasProcurementPolicyBook()
        t = book.cover_target_for_year(2030)
        assert t.min_cover_pct == pytest.approx(GAS_MIN_COVER_PCT)

    def test_check_cover_returns_check(self):
        book = GasProcurementPolicyBook()
        c = book.check_cover("2022-01-01", 100.0, 85.0, 20.0, 2022)
        assert isinstance(c, GasProcurementCheck)

    def test_checks_for_year_filters(self):
        book = self._book_with_checks()
        checks = book.checks_for_year(2022)
        assert len(checks) == 3

    def test_checks_for_year_empty_other_year(self):
        book = self._book_with_checks()
        assert book.checks_for_year(2019) == []

    def test_non_compliant_checks(self):
        book = self._book_with_checks()
        nc = book.non_compliant_checks(2022)
        # short_cover + stop_loss_alert = 2 non-compliant
        assert len(nc) == 2

    def test_crisis_alerts(self):
        book = self._book_with_checks()
        crises = book.crisis_alerts()
        assert len(crises) == 1
        assert crises[0].nbp_sbp_gbp_per_mwh == pytest.approx(190.0)

    def test_mean_cover_pct(self):
        book = self._book_with_checks()
        mean = book.mean_cover_pct(2022)
        # (0.50 + 0.90 + 0.88) / 3 = 0.76
        assert mean == pytest.approx((0.50 + 0.90 + 0.88) / 3, abs=0.01)

    def test_mean_cover_empty_returns_zero(self):
        book = GasProcurementPolicyBook()
        assert book.mean_cover_pct(2022) == 0.0

    def test_policy_summary_keys(self):
        book = self._book_with_checks()
        s = book.policy_summary(2022)
        for k in ("total_checks", "non_compliant_checks", "crisis_alert_checks",
                  "mean_cover_pct", "compliance_rate_pct"):
            assert k in s

    def test_compliance_rate_perfect(self):
        book = GasProcurementPolicyBook()
        book.check_cover("2022-01-01", 100.0, 90.0, 20.0, 2022)
        book.check_cover("2022-02-01", 100.0, 88.0, 20.0, 2022)
        s = book.policy_summary(2022)
        assert s["compliance_rate_pct"] == pytest.approx(100.0)

    def test_2022_crisis_all_non_compliant_if_short(self):
        # Real 2022 scenario: supplier with 40% cover during NBP crisis
        book = GasProcurementPolicyBook()
        book.check_cover("2022-08-01", 1000.0, 400.0, 189.0, 2022)  # short + crisis
        nc = book.non_compliant_checks(2022)
        assert len(nc) == 1
        assert nc[0].status(book.cover_target_for_year(2022)) == GasProcurementStatus.STOP_LOSS_ALERT
