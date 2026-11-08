"""Switching Cost Model (Phase DK).

When a customer switches away from the supplier, the supplier incurs both direct
and indirect costs. Understanding per-customer switching cost informs:
- Retention offer pricing (how much to spend to keep a customer)
- Acquisition pricing (floor under which acquisition is not worth it)
- Bad debt provisioning at account closure

Direct switching costs (per switch):
- Final meter read (manual = £20-40; smart = £2-5)
- Final bill production and postage (£8-15)
- MPAS/MPAN deregistration processing (£15-20 industry admin)
- Agent de-appointment (DA/DC, £10-20)
- CoT/CoS admin staff time (£25-45)

Indirect costs:
- Bad debt risk on outstanding balance (3-8% of outstanding balance)
- Revenue loss from credit balance refund timing
- Loss of meter data access (COS requires next supplier takes over)

Post-2022 context: Ofgem and suppliers tightened switching processes. High switching
volume 2021-22 as customers fled fixed tariffs. Switching now takes 2-3 business days
(faster switching; was 21 days pre-2019).

Epistemic: company knows its own cost structure. Cannot see competitor retention costs.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MeterType(str, Enum):
    LEGACY_MANUAL = "legacy_manual"    # manual read required, £20-40
    SMART_SMETS1 = "smart_smets1"      # SMETS1 smart, moderate cost
    SMART_SMETS2 = "smart_smets2"      # SMETS2, low cost automated


class CustomerSegment(str, Enum):
    DOMESTIC = "domestic"
    SME = "sme"
    I_AND_C = "i_and_c"


_METER_READ_COST_GBP: dict = {
    MeterType.LEGACY_MANUAL: 30.0,
    MeterType.SMART_SMETS1: 8.0,
    MeterType.SMART_SMETS2: 2.5,
}

_FINAL_BILL_COST_GBP = 12.0          # bill production + postage
_MPAS_DEREGISTER_COST_GBP = 17.5    # industry admin
_DA_DC_DEAPPOINT_COST_GBP = 15.0    # metering agent de-appointment
_STAFF_COST_GBP: dict = {
    CustomerSegment.DOMESTIC: 35.0,
    CustomerSegment.SME: 65.0,
    CustomerSegment.I_AND_C: 150.0,
}
_BAD_DEBT_RATE_DOMESTIC = 0.05       # 5% of outstanding balance
_BAD_DEBT_RATE_COMMERCIAL = 0.03     # 3% of outstanding balance (lower: credit scored)


@dataclass(frozen=True)
class SwitchingCostBreakdown:
    meter_type: MeterType
    segment: CustomerSegment
    outstanding_balance_gbp: float          # positive = customer owes us
    is_dual_fuel: bool = False

    @property
    def meter_read_cost_gbp(self) -> float:
        base = _METER_READ_COST_GBP[self.meter_type]
        return base * (2 if self.is_dual_fuel else 1)  # elec + gas for dual fuel

    @property
    def final_bill_cost_gbp(self) -> float:
        return _FINAL_BILL_COST_GBP * (1.5 if self.is_dual_fuel else 1.0)

    @property
    def mpas_cost_gbp(self) -> float:
        return _MPAS_DEREGISTER_COST_GBP

    @property
    def da_dc_cost_gbp(self) -> float:
        return _DA_DC_DEAPPOINT_COST_GBP

    @property
    def staff_cost_gbp(self) -> float:
        return _STAFF_COST_GBP[self.segment]

    @property
    def bad_debt_risk_gbp(self) -> float:
        if self.outstanding_balance_gbp <= 0:
            return 0.0
        rate = (_BAD_DEBT_RATE_DOMESTIC if self.segment == CustomerSegment.DOMESTIC
                else _BAD_DEBT_RATE_COMMERCIAL)
        return self.outstanding_balance_gbp * rate

    @property
    def total_cost_gbp(self) -> float:
        return (
            self.meter_read_cost_gbp
            + self.final_bill_cost_gbp
            + self.mpas_cost_gbp
            + self.da_dc_cost_gbp
            + self.staff_cost_gbp
            + self.bad_debt_risk_gbp
        )

    @property
    def direct_cost_gbp(self) -> float:
        return (
            self.meter_read_cost_gbp
            + self.final_bill_cost_gbp
            + self.mpas_cost_gbp
            + self.da_dc_cost_gbp
            + self.staff_cost_gbp
        )

    def cost_summary(self) -> dict:
        return {
            "meter_read": self.meter_read_cost_gbp,
            "final_bill": self.final_bill_cost_gbp,
            "mpas": self.mpas_cost_gbp,
            "da_dc": self.da_dc_cost_gbp,
            "staff": self.staff_cost_gbp,
            "bad_debt_risk": self.bad_debt_risk_gbp,
            "total": self.total_cost_gbp,
            "direct": self.direct_cost_gbp,
        }


class SwitchingCostModel:
    """Computes per-customer switching cost and retention offer bounds."""

    @staticmethod
    def estimate(
        meter_type: MeterType,
        segment: CustomerSegment,
        outstanding_balance_gbp: float = 0.0,
        is_dual_fuel: bool = False,
    ) -> SwitchingCostBreakdown:
        return SwitchingCostBreakdown(
            meter_type=meter_type,
            segment=segment,
            outstanding_balance_gbp=outstanding_balance_gbp,
            is_dual_fuel=is_dual_fuel,
        )

    @staticmethod
    def max_retention_offer_gbp(
        annual_margin_gbp: float,
        switch_cost: SwitchingCostBreakdown,
        margin_floor_pct: float = 0.3,
    ) -> float:
        """Max offer = switch cost avoided + margin above floor."""
        if annual_margin_gbp <= 0:
            return switch_cost.total_cost_gbp
        floor = annual_margin_gbp * margin_floor_pct
        headroom = max(0.0, annual_margin_gbp - floor)
        return switch_cost.total_cost_gbp + headroom

    @staticmethod
    def portfolio_summary(switches: list) -> str:
        if not switches:
            return "Switching Cost Model: no switches recorded."
        total_cost = sum(s.total_cost_gbp for s in switches)
        avg_cost = total_cost / len(switches)
        smart_pct = sum(1 for s in switches
                        if s.meter_type == MeterType.SMART_SMETS2) / len(switches)
        return (
            f"Switching Cost Model: {len(switches)} switches, "
            f"total cost £{total_cost:,.0f}, avg £{avg_cost:,.0f}/switch. "
            f"SMETS2 proportion: {smart_pct:.0%} (lower cost)."
        )
