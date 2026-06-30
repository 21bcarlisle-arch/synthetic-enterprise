"""Tests for Porting Loss Register (Phase FL)."""
import datetime as dt
import pytest
from company.crm.porting_loss_register import (
    SwitchReason, WinbackEligibility, PortingLossRecord, PortingLossRegister,
)

SWITCH_DATE = dt.date(2024, 1, 1)
AS_OF = dt.date(2024, 9, 1)  # 8 months later
AS_OF_SOON = dt.date(2024, 3, 1)  # 2 months later


def make_loss(acct="C1", reason=SwitchReason.CHEAPER_TARIFF,
              margin=100.0, clv=500.0, dni=False, gdpr=False, date=SWITCH_DATE):
    return PortingLossRecord(
        account_id=acct, switch_date=date, reason=reason,
        annual_revenue_gbp=500.0, annual_margin_gbp=margin,
        h3_clv_gbp=clv, has_dni_flag=dni, has_gdpr_opt_out=gdpr,
    )


class TestPortingLossRecord:
    def test_is_margin_positive(self):
        assert make_loss(margin=100.0).is_margin_positive

    def test_not_margin_positive(self):
        assert not make_loss(margin=-10.0).is_margin_positive

    def test_winback_eligible(self):
        l = make_loss()
        assert l.winback_eligibility(AS_OF) == WinbackEligibility.ELIGIBLE

    def test_winback_too_soon(self):
        l = make_loss()
        assert l.winback_eligibility(AS_OF_SOON) == WinbackEligibility.TOO_SOON

    def test_winback_dni_flag(self):
        l = make_loss(dni=True)
        assert l.winback_eligibility(AS_OF) == WinbackEligibility.DNI_FLAG

    def test_winback_gdpr_opt_out(self):
        l = make_loss(gdpr=True)
        assert l.winback_eligibility(AS_OF) == WinbackEligibility.GDPR_OPT_OUT

    def test_winback_not_eligible_neg_margin(self):
        l = make_loss(margin=-10.0)
        assert l.winback_eligibility(AS_OF) == WinbackEligibility.NOT_ELIGIBLE

    def test_loss_summary(self):
        s = make_loss().loss_summary()
        assert "PortingLoss" in s and "C1" in s


class TestPortingLossRegister:
    def test_record(self):
        reg = PortingLossRegister()
        reg.record(make_loss())
        assert len(reg.winback_eligible(AS_OF)) == 1

    def test_losses_in_period(self):
        reg = PortingLossRegister()
        reg.record(make_loss(date=dt.date(2024, 1, 1)))
        reg.record(make_loss(acct="C2", date=dt.date(2023, 1, 1)))
        in_period = reg.losses_in_period(dt.date(2024, 1, 1), dt.date(2024, 12, 31))
        assert len(in_period) == 1

    def test_by_reason(self):
        reg = PortingLossRegister()
        reg.record(make_loss(reason=SwitchReason.POOR_SERVICE))
        reg.record(make_loss(acct="C2", reason=SwitchReason.CHEAPER_TARIFF))
        assert len(reg.by_reason(SwitchReason.POOR_SERVICE)) == 1

    def test_total_margin_lost(self):
        reg = PortingLossRegister()
        reg.record(make_loss(margin=100.0))
        reg.record(make_loss(acct="C2", margin=200.0))
        assert reg.total_margin_lost_gbp() == pytest.approx(300.0)

    def test_negative_margin_excluded(self):
        reg = PortingLossRegister()
        reg.record(make_loss(margin=-50.0))
        assert reg.total_margin_lost_gbp() == pytest.approx(0.0)

    def test_porting_loss_summary(self):
        reg = PortingLossRegister()
        reg.record(make_loss())
        s = reg.porting_loss_summary(AS_OF)
        assert "Porting Loss Register" in s
