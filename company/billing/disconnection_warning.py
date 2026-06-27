"""Disconnection Warning Register: SLC 27/SoP Regs warning sequence compliance."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class WarningStep(str, Enum):
    WARNING_1 = "warning_1"       # first contact; inform of arrears
    WARNING_2 = "warning_2"       # second contact; payment plan offered
    WARNING_3 = "warning_3"       # final warning; 7-day notice
    DISCONNECTION_NOTICE = "disconnection_notice"  # 28-day formal notice


class WarningStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    RESOLVED = "resolved"    # customer engaged; disconnection cancelled
    OVERRIDDEN = "overridden" # vulnerable/winter moratorium applies


_MIN_DAYS_BETWEEN_WARNINGS = 7
_DISCONNECTION_NOTICE_DAYS = 28   # minimum notice before action
_COOLING_OFF_DAYS = 28


@dataclass(frozen=True)
class DisconnectionWarning:
    account_id: str
    warning_step: WarningStep
    issued_date: dt.date
    debt_amount_gbp: float
    status: WarningStatus = WarningStatus.PENDING
    responded_date: Optional[dt.date] = None

    def earliest_next_action_date(self) -> dt.date:
        if self.warning_step == WarningStep.DISCONNECTION_NOTICE:
            return self.issued_date + dt.timedelta(days=_DISCONNECTION_NOTICE_DAYS)
        return self.issued_date + dt.timedelta(days=_MIN_DAYS_BETWEEN_WARNINGS)

    def can_escalate(self, as_of: dt.date) -> bool:
        return (as_of >= self.earliest_next_action_date()
                and self.status == WarningStatus.SENT)


class DisconnectionWarningRegister:
    """Tracks the mandatory warning sequence before disconnection.

    Real calibration:
    - Ofgem SLC 27 / Gas/Electricity SoP Regulations 2015: mandatory sequence before
      disconnection of credit-meter customers.
    - Minimum 4 contacts (3 warnings + formal notice); cooling-off periods enforced.
    - Formal disconnection notice: minimum 28 days before action.
    - Prohibited: disconnecting without completing the full warning sequence;
      disconnecting vulnerable/PSR customers at any time; disconnecting any domestic
      customer during winter (Nov-Mar).
    - Key 2023 issue: Ofgem investigated several suppliers for issuing disconnection
      threats without completing the mandatory sequence.
    """

    def __init__(self) -> None:
        self._warnings: List[DisconnectionWarning] = []

    def issue_warning(self, warning: DisconnectionWarning) -> DisconnectionWarning:
        self._warnings.append(warning)
        return warning

    def _update(self, account_id: str, step: WarningStep, **kwargs) -> DisconnectionWarning:
        import dataclasses
        for i, w in enumerate(self._warnings):
            if w.account_id == account_id and w.warning_step == step:
                updated = dataclasses.replace(w, **kwargs)
                self._warnings[i] = updated
                return updated
        raise ValueError(f"Warning not found for {account_id} step {step}")

    def mark_sent(self, account_id: str, step: WarningStep,
                  sent_date: dt.date) -> DisconnectionWarning:
        return self._update(account_id, step, status=WarningStatus.SENT,
                            issued_date=sent_date)

    def resolve(self, account_id: str, step: WarningStep,
                responded_date: dt.date) -> DisconnectionWarning:
        return self._update(account_id, step, status=WarningStatus.RESOLVED,
                            responded_date=responded_date)

    def override(self, account_id: str, step: WarningStep) -> DisconnectionWarning:
        return self._update(account_id, step, status=WarningStatus.OVERRIDDEN)

    def warnings_for_account(self, account_id: str) -> List[DisconnectionWarning]:
        return [w for w in self._warnings if w.account_id == account_id]

    def can_disconnect(self, account_id: str, as_of: dt.date) -> bool:
        account_warnings = self.warnings_for_account(account_id)
        sent_steps = {w.warning_step for w in account_warnings
                      if w.status == WarningStatus.SENT}
        required = {WarningStep.WARNING_1, WarningStep.WARNING_2,
                    WarningStep.WARNING_3, WarningStep.DISCONNECTION_NOTICE}
        if not required.issubset(sent_steps):
            return False
        notice = next((w for w in account_warnings
                       if w.warning_step == WarningStep.DISCONNECTION_NOTICE
                       and w.status == WarningStatus.SENT), None)
        if notice is None:
            return False
        return as_of >= notice.earliest_next_action_date()

    def outstanding_warnings(self) -> List[DisconnectionWarning]:
        return [w for w in self._warnings
                if w.status in (WarningStatus.PENDING, WarningStatus.SENT)]

    def warning_summary(self) -> dict:
        return {
            "total_warnings": len(self._warnings),
            "outstanding": len(self.outstanding_warnings()),
            "resolved": sum(1 for w in self._warnings
                             if w.status == WarningStatus.RESOLVED),
            "overridden": sum(1 for w in self._warnings
                               if w.status == WarningStatus.OVERRIDDEN),
        }
