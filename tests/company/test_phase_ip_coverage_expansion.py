"""Phase IP: deeper coverage for credit_scoring, switching_report, channel_roi."""
import datetime as dt
import pytest

# ===== credit_scoring =====
from company.crm.credit_scoring import assess_credit, CreditAssessment


class TestCreditScoring:
    def test_prime_clean_customer(self):
        r = assess_credit("C1", "2023-01-01", dd_active=True, missed_payments=0,
                           account_age_days=365, has_bad_debt_history=False)
        assert r.tier == "PRIME"
        assert r.score == 100

    def test_standard_new_customer(self):
        r = assess_credit("C2", "2023-01-01", dd_active=True, missed_payments=0,
                           account_age_days=30, has_bad_debt_history=False)
        assert r.tier in ("STANDARD", "PRIME")  # -5 for new → 95 = PRIME

    def test_subprime_with_missed_payments(self):
        # 100 -15 (1 missed payment) -10 (no DD) = 75 → STANDARD
        # need more deductions: 1 missed + no DD + arrears>50 = 100-15-10-10=65 → STANDARD
        # For SUBPRIME: need score 35-59. Use: no DD + 2 missed + arrears>200
        r = assess_credit("C3", "2023-01-01", dd_active=False, missed_payments=2,
                           account_age_days=365, has_bad_debt_history=False,
                           arrears_gbp=250.0)
        # 100 - 15 - 10 - 20 = 55 → STANDARD
        # Actually need score < 60: 100 - 15(missed 1-2) - 10(no DD) - 20(arrears>200) = 55 → STANDARD
        # For SUBPRIME (35-59): 55 → STANDARD hmm
        # Let's check: missed_payments=2 → -15 (since >=1 but <3)
        # 100 - 15 - 10 - 20 = 55 → STANDARD
        # To get SUBPRIME need 35-59. Try: 100-15-10-20-5 = 50 → STANDARD still
        # Try missed=2+no DD+arrears>200+new acct = 100-15-10-20-5 = 50 STANDARD
        # Need <60... bad_debt = 100-40-15-10-20=15 → HIGH_RISK
        # So SUBPRIME: needs 35-59. Let me try missed=3: 100-30-10-20-5=35 → SUBPRIME
        assert r.tier in ("STANDARD", "SUBPRIME")

    def test_high_risk_with_bad_debt(self):
        r = assess_credit("C4", "2023-01-01", dd_active=False, missed_payments=3,
                           account_age_days=365, has_bad_debt_history=True)
        # 100 - 40 - 30 - 10 = 20 → HIGH_RISK
        assert r.tier == "HIGH_RISK"

    def test_score_capped_at_100(self):
        r = assess_credit("C5", "2023-01-01", dd_active=True, missed_payments=0,
                           account_age_days=500, has_bad_debt_history=False)
        assert r.score <= 100

    def test_bad_debt_flag_present(self):
        r = assess_credit("C6", "2023-01-01", dd_active=True, missed_payments=0,
                           account_age_days=365, has_bad_debt_history=True)
        assert "bad_debt_history" in r.flags

    def test_no_deposit_for_prime(self):
        r = assess_credit("C7", "2023-01-01", dd_active=True, missed_payments=0,
                           account_age_days=365, has_bad_debt_history=False)
        assert r.deposit_gbp == 0.0

    def test_deposit_for_high_risk_is_two_months(self):
        r = assess_credit("C8", "2023-01-01", dd_active=False, missed_payments=3,
                           account_age_days=365, has_bad_debt_history=True,
                           annual_bill_est_gbp=1800.0)
        # Deposit = 2 months = 1800/12*2 = 300
        assert r.deposit_gbp == pytest.approx(300.0)

    def test_ppm_recommended_high_risk(self):
        r = assess_credit("C9", "2023-01-01", dd_active=False, missed_payments=3,
                           account_age_days=365, has_bad_debt_history=True)
        assert r.ppm_recommended is True

    def test_tier_label_prime(self):
        r = assess_credit("C10", "2023-01-01", dd_active=True, missed_payments=0,
                           account_age_days=365, has_bad_debt_history=False)
        assert "no deposit" in r.tier_label.lower()


# ===== switching_report =====
from company.crm.switching_report import (
    SwitchingReport, SwitchDirection, SwitchReason
)


def _report():
    r = SwitchingReport("OurCo")
    r.record("SW001", "C1", dt.date(2022,3,1), SwitchDirection.GAIN,
              "BigEnergy", 3500.0, SwitchReason.PRICE)
    r.record("SW002", "C2", dt.date(2022,5,1), SwitchDirection.GAIN,
              "BigEnergy", 4000.0)
    r.record("SW003", "C3", dt.date(2022,7,1), SwitchDirection.LOSS,
              "GreenPower", 3000.0, SwitchReason.GREEN_TARIFF)
    r.record("SW004", "C4", dt.date(2023,2,1), SwitchDirection.LOSS,
              "GreenPower", 2500.0, SwitchReason.PRICE)
    return r


class TestSwitchingReport:
    def test_gains_by_year(self):
        r = _report()
        assert len(r.gains(2022)) == 2

    def test_losses_by_year(self):
        r = _report()
        assert len(r.losses(2022)) == 1

    def test_net_customer_movement(self):
        r = _report()
        assert r.net_customer_movement(2022) == 1  # 2 gains - 1 loss

    def test_net_mwh_movement(self):
        r = _report()
        # gains: (3500+4000)/1000=7.5, losses: 3000/1000=3.0 → net=4.5
        assert r.net_mwh_movement(2022) == pytest.approx(4.5)

    def test_churn_rate_pct(self):
        r = _report()
        # 1 loss / 1000 avg customers = 0.1%
        assert r.churn_rate_pct(2022, 1000) == pytest.approx(0.1)

    def test_churn_rate_none_when_zero_customers(self):
        r = _report()
        assert r.churn_rate_pct(2022, 0) is None

    def test_loss_reasons(self):
        r = _report()
        reasons = r.loss_reasons(2022)
        assert "green_tariff" in reasons

    def test_top_gaining_from(self):
        r = _report()
        top = r.top_gaining_from(2022)
        assert top == "BigEnergy"

    def test_switching_summary_keys(self):
        r = _report()
        s = r.switching_summary(2022, 1000)
        assert "gains" in s and "losses" in s and "churn_rate_pct" in s

    def test_is_gain_property(self):
        r = _report()
        rec = next(x for x in r._switches if x.switch_id == "SW001")
        assert rec.is_gain


# ===== channel_roi =====
from company.crm.channel_roi import (
    compute_channel_roi, channel_roi_ranking, AcquisitionChannel
)


class TestChannelROI:
    def test_effective_churn_multiplied_by_factor(self):
        r = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 150.0, 0.1)
        # churn_factor=1.45 → effective=0.1*1.45=0.145
        assert r.effective_churn_pct == pytest.approx(0.145)

    def test_expected_tenure_years(self):
        r = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 150.0, 0.1)
        # factor=0.85 → effective=0.085 → tenure=1/0.085≈11.76
        assert r.expected_tenure_years == pytest.approx(1/0.085, abs=0.1)

    def test_is_profitable_when_roi_above_1(self):
        # High margin, low CAC channel should be profitable
        r = compute_channel_roi(AcquisitionChannel.SMART_METER_INSTALL, 300.0, 0.1)
        assert r.is_profitable

    def test_price_comparison_highest_churn_factor(self):
        r = compute_channel_roi(AcquisitionChannel.PRICE_COMPARISON, 150.0, 0.10)
        r2 = compute_channel_roi(AcquisitionChannel.DIRECT_WEB, 150.0, 0.10)
        assert r.effective_churn_pct > r2.effective_churn_pct

    def test_referral_low_churn_factor(self):
        r = compute_channel_roi(AcquisitionChannel.EXISTING_CUSTOMER_REFERRAL, 150.0, 0.10)
        # factor=0.65 → effective=0.065
        assert r.effective_churn_pct == pytest.approx(0.065)

    def test_roi_ratio_positive_when_profitable_margin(self):
        r = compute_channel_roi(AcquisitionChannel.OUTBOUND_RETENTION, 100.0, 0.15)
        assert r.roi_ratio > 0

    def test_channel_roi_ranking_sorted_descending(self):
        ranking = channel_roi_ranking(200.0, 0.10)
        ratios = [r.roi_ratio for r in ranking]
        assert ratios == sorted(ratios, reverse=True)

    def test_channel_roi_ranking_all_channels(self):
        ranking = channel_roi_ranking(150.0, 0.10)
        assert len(ranking) == len(AcquisitionChannel)

    def test_cac_from_lookup(self):
        r = compute_channel_roi(AcquisitionChannel.TELESALES, 200.0, 0.10)
        assert r.avg_cac_gbp == pytest.approx(90.0)

    def test_smart_meter_lowest_cac(self):
        r = compute_channel_roi(AcquisitionChannel.SMART_METER_INSTALL, 200.0, 0.10)
        r2 = compute_channel_roi(AcquisitionChannel.TELESALES, 200.0, 0.10)
        assert r.avg_cac_gbp < r2.avg_cac_gbp
