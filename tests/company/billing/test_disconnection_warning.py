import datetime as dt
import pytest
from company.billing.disconnection_warning import (
    DisconnectionWarning, WarningStep, WarningStatus,
    DisconnectionWarningRegister,
)


def make_warning(account_id="A1", step=WarningStep.WARNING_1,
                 issued=dt.date(2023, 6, 1), debt=250.0,
                 status=WarningStatus.PENDING):
    return DisconnectionWarning(
        account_id=account_id, warning_step=step,
        issued_date=issued, debt_amount_gbp=debt, status=status,
    )


class TestDisconnectionWarning:
    def test_earliest_next_action_warning(self):
        w = make_warning(step=WarningStep.WARNING_1, issued=dt.date(2023, 6, 1))
        assert w.earliest_next_action_date() == dt.date(2023, 6, 8)

    def test_earliest_next_action_notice(self):
        w = make_warning(step=WarningStep.DISCONNECTION_NOTICE, issued=dt.date(2023, 6, 1))
        assert w.earliest_next_action_date() == dt.date(2023, 6, 29)

    def test_can_escalate_true(self):
        w = make_warning(step=WarningStep.WARNING_1, issued=dt.date(2023, 6, 1),
                         status=WarningStatus.SENT)
        assert w.can_escalate(dt.date(2023, 6, 10)) is True

    def test_can_escalate_false_too_early(self):
        w = make_warning(step=WarningStep.WARNING_1, issued=dt.date(2023, 6, 1),
                         status=WarningStatus.SENT)
        assert w.can_escalate(dt.date(2023, 6, 5)) is False

    def test_can_escalate_false_not_sent(self):
        w = make_warning(step=WarningStep.WARNING_1, issued=dt.date(2023, 6, 1))
        assert w.can_escalate(dt.date(2023, 6, 10)) is False

    def test_frozen(self):
        w = make_warning()
        with pytest.raises((AttributeError, TypeError)):
            w.account_id = "X"


class TestDisconnectionWarningRegister:
    def _setup_full_sequence(self, reg, account_id="A1",
                             notice_date=dt.date(2023, 7, 1)):
        for step, date in [
            (WarningStep.WARNING_1, dt.date(2023, 5, 1)),
            (WarningStep.WARNING_2, dt.date(2023, 5, 15)),
            (WarningStep.WARNING_3, dt.date(2023, 6, 1)),
            (WarningStep.DISCONNECTION_NOTICE, notice_date),
        ]:
            reg.issue_warning(make_warning(account_id=account_id, step=step,
                                           issued=date, status=WarningStatus.SENT))

    def test_issue_warning(self):
        reg = DisconnectionWarningRegister()
        reg.issue_warning(make_warning())
        assert len(reg.outstanding_warnings()) == 1

    def test_mark_sent(self):
        reg = DisconnectionWarningRegister()
        reg.issue_warning(make_warning(account_id="A1", step=WarningStep.WARNING_1))
        result = reg.mark_sent("A1", WarningStep.WARNING_1, dt.date(2023, 6, 2))
        assert result.status == WarningStatus.SENT

    def test_resolve(self):
        reg = DisconnectionWarningRegister()
        reg.issue_warning(make_warning(account_id="A1", step=WarningStep.WARNING_1))
        result = reg.resolve("A1", WarningStep.WARNING_1, dt.date(2023, 6, 5))
        assert result.status == WarningStatus.RESOLVED

    def test_override(self):
        reg = DisconnectionWarningRegister()
        reg.issue_warning(make_warning(account_id="A1", step=WarningStep.WARNING_1))
        result = reg.override("A1", WarningStep.WARNING_1)
        assert result.status == WarningStatus.OVERRIDDEN

    def test_can_disconnect_false_incomplete_sequence(self):
        reg = DisconnectionWarningRegister()
        reg.issue_warning(make_warning(account_id="A1", step=WarningStep.WARNING_1,
                                       status=WarningStatus.SENT))
        assert reg.can_disconnect("A1", dt.date(2023, 9, 1)) is False

    def test_can_disconnect_true_after_notice_period(self):
        reg = DisconnectionWarningRegister()
        self._setup_full_sequence(reg, notice_date=dt.date(2023, 7, 1))
        assert reg.can_disconnect("A1", dt.date(2023, 8, 1)) is True

    def test_can_disconnect_false_within_notice_period(self):
        reg = DisconnectionWarningRegister()
        self._setup_full_sequence(reg, notice_date=dt.date(2023, 7, 1))
        assert reg.can_disconnect("A1", dt.date(2023, 7, 15)) is False

    def test_warnings_for_account(self):
        reg = DisconnectionWarningRegister()
        reg.issue_warning(make_warning(account_id="A1", step=WarningStep.WARNING_1))
        reg.issue_warning(make_warning(account_id="A2", step=WarningStep.WARNING_1))
        assert len(reg.warnings_for_account("A1")) == 1

    def test_outstanding_excludes_resolved(self):
        reg = DisconnectionWarningRegister()
        reg.issue_warning(make_warning(account_id="A1", step=WarningStep.WARNING_1))
        reg.resolve("A1", WarningStep.WARNING_1, dt.date(2023, 6, 5))
        assert len(reg.outstanding_warnings()) == 0

    def test_summary_keys(self):
        reg = DisconnectionWarningRegister()
        s = reg.warning_summary()
        for k in ("total_warnings", "outstanding", "resolved", "overridden"):
            assert k in s

    def test_update_raises_not_found(self):
        reg = DisconnectionWarningRegister()
        with pytest.raises(ValueError):
            reg.resolve("MISSING", WarningStep.WARNING_1, dt.date(2023, 6, 5))
