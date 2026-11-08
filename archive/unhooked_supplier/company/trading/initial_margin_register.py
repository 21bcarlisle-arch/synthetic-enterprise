"""Initial Margin Register for OTC and cleared energy derivatives.

UK energy suppliers posting exchange-cleared or bilateral OTC forward
contracts must post initial margin (IM) at trade inception. IM is held
as collateral by the clearing house or counterparty until the trade matures.

Unlike variation margin (Phase CC — daily mark-to-market settlement),
initial margin is:
- Posted once at trade inception
- Returned at trade maturity or close
- Sized to cover a defined stressed holding period (typically 5 days)
- Held in a segregated account (CASS rules)

During the 2022 energy crisis:
1. Spot/forward prices spiked → positions moved deep out-of-the-money
2. Variation margin calls drained cash daily (Phase CC)
3. Clearing houses issued margin calls to INCREASE initial margin
4. Combined cash drain destroyed supplier liquidity within weeks

Epistemic: the company reads its own initial margin ledger and clearing
confirmations. It does NOT read the sim's forward curve parameters.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class MarginAccountType(str, Enum):
    BILATERAL_OTC = "bilateral_otc"      # Posted to named counterparty
    EXCHANGE_CLEARED = "exchange_cleared"  # Posted to CCP (ICE, LME Clear)
    INTERNAL_NETTING = "internal_netting"  # Netted across portfolio


class IMStatus(str, Enum):
    POSTED = "posted"       # Currently held as collateral
    RETURNED = "returned"   # Trade matured; IM returned
    CALLED = "called"       # Clearing house increased IM requirement
    PARTIAL = "partial"     # Partial return on partial close


@dataclass(frozen=True)
class InitialMarginRecord:
    margin_id: str
    trade_id: str
    counterparty: str
    account_type: MarginAccountType
    notional_mwh: float
    margin_posted_gbp: float
    posted_date: date
    expected_return_date: date
    actual_return_date: Optional[date] = None
    status: IMStatus = IMStatus.POSTED
    # During a margin call, clearing house increases requirement
    additional_call_gbp: float = 0.0

    @property
    def total_held_gbp(self) -> float:
        """Total collateral currently locked up."""
        return self.margin_posted_gbp + self.additional_call_gbp

    @property
    def is_active(self) -> bool:
        return self.status in (IMStatus.POSTED, IMStatus.CALLED)

    @property
    def margin_rate_pct_of_notional(self) -> float:
        """IM as % of notional value (MWh × assumed £100/MWh proxy)."""
        notional_value = self.notional_mwh * 100  # proxy £100/MWh
        if notional_value == 0:
            return 0.0
        return self.total_held_gbp / notional_value * 100


class InitialMarginRegister:
    """Tracks all initial margin posts across the derivative portfolio."""

    def __init__(self) -> None:
        self._records: list[InitialMarginRecord] = []

    def post_margin(
        self,
        margin_id: str,
        trade_id: str,
        counterparty: str,
        account_type: MarginAccountType,
        notional_mwh: float,
        margin_posted_gbp: float,
        posted_date: date,
        expected_return_date: date,
    ) -> InitialMarginRecord:
        record = InitialMarginRecord(
            margin_id=margin_id,
            trade_id=trade_id,
            counterparty=counterparty,
            account_type=account_type,
            notional_mwh=notional_mwh,
            margin_posted_gbp=margin_posted_gbp,
            posted_date=posted_date,
            expected_return_date=expected_return_date,
        )
        self._records.append(record)
        return record

    def issue_additional_call(
        self, margin_id: str, additional_gbp: float
    ) -> InitialMarginRecord:
        """Clearing house increases IM requirement on an existing position."""
        old = next(r for r in self._records if r.margin_id == margin_id)
        updated = InitialMarginRecord(
            margin_id=old.margin_id,
            trade_id=old.trade_id,
            counterparty=old.counterparty,
            account_type=old.account_type,
            notional_mwh=old.notional_mwh,
            margin_posted_gbp=old.margin_posted_gbp,
            posted_date=old.posted_date,
            expected_return_date=old.expected_return_date,
            actual_return_date=old.actual_return_date,
            status=IMStatus.CALLED,
            additional_call_gbp=old.additional_call_gbp + additional_gbp,
        )
        self._records = [updated if r.margin_id == margin_id else r for r in self._records]
        return updated

    def return_margin(self, margin_id: str, return_date: date) -> InitialMarginRecord:
        old = next(r for r in self._records if r.margin_id == margin_id)
        updated = InitialMarginRecord(
            margin_id=old.margin_id,
            trade_id=old.trade_id,
            counterparty=old.counterparty,
            account_type=old.account_type,
            notional_mwh=old.notional_mwh,
            margin_posted_gbp=old.margin_posted_gbp,
            posted_date=old.posted_date,
            expected_return_date=old.expected_return_date,
            actual_return_date=return_date,
            status=IMStatus.RETURNED,
            additional_call_gbp=old.additional_call_gbp,
        )
        self._records = [updated if r.margin_id == margin_id else r for r in self._records]
        return updated

    @property
    def active_records(self) -> list[InitialMarginRecord]:
        return [r for r in self._records if r.is_active]

    @property
    def total_locked_gbp(self) -> float:
        """Total cash locked as IM across all active positions."""
        return sum(r.total_held_gbp for r in self.active_records)

    @property
    def total_additional_calls_gbp(self) -> float:
        """Total additional calls received (crisis indicator)."""
        return sum(r.additional_call_gbp for r in self._records)

    def records_by_counterparty(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for r in self.active_records:
            result[r.counterparty] = result.get(r.counterparty, 0.0) + r.total_held_gbp
        return result

    def im_summary(self) -> str:
        active = len(self.active_records)
        locked = self.total_locked_gbp
        additional = self.total_additional_calls_gbp
        lines = [
            "Initial Margin Register",
            "Active positions: {} | Total locked: £{:,.0f}".format(active, locked),
            "Additional calls received: £{:,.0f}".format(additional),
        ]
        return chr(10).join(lines)
