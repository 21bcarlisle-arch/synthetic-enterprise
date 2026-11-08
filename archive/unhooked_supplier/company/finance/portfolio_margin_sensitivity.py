"""Portfolio margin sensitivity analyser — five-factor sensitivity table.

The company analyses how its net margin responds to key operating variables:
1. Wholesale price shift (±10%, ±20%)
2. Demand volume change (±5%, ±10%)
3. Churn rate increase (+5pp, +10pp)
4. Non-commodity cost escalation (+5%, +10%)
5. Fixed cost increase (£5k, £10k)

Epistemic constraint: uses observed wholesale cost fraction, observed churn rate,
observed margin fractions from management accounts. Never reads SIM internals.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SensitivityFactor(str, Enum):
    WHOLESALE_PRICE = "wholesale_price"
    DEMAND_VOLUME = "demand_volume"
    CHURN_RATE = "churn_rate"
    NON_COMMODITY_COST = "non_commodity_cost"
    FIXED_COST = "fixed_cost"


@dataclass(frozen=True)
class SensitivityScenario:
    factor: SensitivityFactor
    label: str
    shock_magnitude: float
    base_net_margin_gbp: float
    stressed_net_margin_gbp: float
    delta_gbp: float
    delta_pct: float

    @property
    def is_adverse(self) -> bool:
        return self.delta_gbp < 0

    @property
    def severity(self) -> str:
        abs_delta_pct = abs(self.delta_pct)
        if abs_delta_pct < 5:
            return "LOW"
        if abs_delta_pct < 15:
            return "MEDIUM"
        return "HIGH"


class PortfolioMarginSensitivityBook:
    """Computes portfolio net margin sensitivity to five operational factors."""

    def __init__(
        self,
        base_revenue_gbp: float,
        base_wholesale_cost_gbp: float,
        base_non_commodity_cost_gbp: float,
        base_fixed_cost_gbp: float,
        base_bad_debt_gbp: float,
        base_capital_cost_gbp: float,
        base_active_customers: int,
        base_churn_rate_pct: float,
    ) -> None:
        self._rev = base_revenue_gbp
        self._whl = base_wholesale_cost_gbp
        self._ncc = base_non_commodity_cost_gbp
        self._fixed = base_fixed_cost_gbp
        self._bad_debt = base_bad_debt_gbp
        self._cap = base_capital_cost_gbp
        self._n = base_active_customers
        self._churn = base_churn_rate_pct
        self._base_net = self._compute_net(
            self._rev, self._whl, self._ncc, self._fixed, self._bad_debt, self._cap
        )

    def _compute_net(self, rev, whl, ncc, fixed, bad_debt, cap) -> float:
        gm = rev - whl - ncc
        net = gm - cap - bad_debt - fixed
        return net

    @property
    def base_net_margin_gbp(self) -> float:
        return self._base_net

    def wholesale_price_shock(self, shock_pct: float) -> SensitivityScenario:
        """Wholesale price shifts by shock_pct% — affects cost, not revenue (fixed-price tariff)."""
        stressed_whl = self._whl * (1 + shock_pct / 100)
        stressed_net = self._compute_net(self._rev, stressed_whl, self._ncc, self._fixed, self._bad_debt, self._cap)
        delta = stressed_net - self._base_net
        delta_pct = (delta / abs(self._base_net) * 100) if self._base_net != 0 else 0.0
        return SensitivityScenario(
            factor=SensitivityFactor.WHOLESALE_PRICE,
            label="Wholesale +{:.0f}%".format(shock_pct) if shock_pct >= 0 else "Wholesale {:.0f}%".format(shock_pct),
            shock_magnitude=shock_pct,
            base_net_margin_gbp=self._base_net,
            stressed_net_margin_gbp=stressed_net,
            delta_gbp=delta,
            delta_pct=delta_pct,
        )

    def demand_volume_shock(self, shock_pct: float) -> SensitivityScenario:
        """Demand volume shifts — affects revenue and wholesale cost proportionally."""
        factor = 1 + shock_pct / 100
        stressed_rev = self._rev * factor
        stressed_whl = self._whl * factor
        stressed_net = self._compute_net(stressed_rev, stressed_whl, self._ncc, self._fixed, self._bad_debt, self._cap)
        delta = stressed_net - self._base_net
        delta_pct = (delta / abs(self._base_net) * 100) if self._base_net != 0 else 0.0
        return SensitivityScenario(
            factor=SensitivityFactor.DEMAND_VOLUME,
            label="Demand {:.0f}%".format(shock_pct),
            shock_magnitude=shock_pct,
            base_net_margin_gbp=self._base_net,
            stressed_net_margin_gbp=stressed_net,
            delta_gbp=delta,
            delta_pct=delta_pct,
        )

    def churn_shock(self, additional_churn_pct: float) -> SensitivityScenario:
        """Additional churn — loses margin proportional to new churn rate."""
        # Estimate: each additional % churn loses proportional net margin per customer
        lost_customers = self._n * additional_churn_pct / 100
        margin_per_customer = self._base_net / self._n if self._n > 0 else 0
        lost_margin = lost_customers * margin_per_customer
        stressed_net = self._base_net - lost_margin  # losing customer margin
        delta = stressed_net - self._base_net
        delta_pct = (delta / abs(self._base_net) * 100) if self._base_net != 0 else 0.0
        return SensitivityScenario(
            factor=SensitivityFactor.CHURN_RATE,
            label="Churn +{:.0f}pp".format(additional_churn_pct),
            shock_magnitude=additional_churn_pct,
            base_net_margin_gbp=self._base_net,
            stressed_net_margin_gbp=stressed_net,
            delta_gbp=delta,
            delta_pct=delta_pct,
        )

    def non_commodity_cost_shock(self, shock_pct: float) -> SensitivityScenario:
        """Non-commodity cost escalation (network, policy levies)."""
        stressed_ncc = self._ncc * (1 + shock_pct / 100)
        stressed_net = self._compute_net(self._rev, self._whl, stressed_ncc, self._fixed, self._bad_debt, self._cap)
        delta = stressed_net - self._base_net
        delta_pct = (delta / abs(self._base_net) * 100) if self._base_net != 0 else 0.0
        return SensitivityScenario(
            factor=SensitivityFactor.NON_COMMODITY_COST,
            label="NCC +{:.0f}%".format(shock_pct),
            shock_magnitude=shock_pct,
            base_net_margin_gbp=self._base_net,
            stressed_net_margin_gbp=stressed_net,
            delta_gbp=delta,
            delta_pct=delta_pct,
        )

    def fixed_cost_shock(self, additional_gbp: float) -> SensitivityScenario:
        """Fixed cost increase (staffing, systems, regulatory overhead)."""
        stressed_fixed = self._fixed + additional_gbp
        stressed_net = self._compute_net(self._rev, self._whl, self._ncc, stressed_fixed, self._bad_debt, self._cap)
        delta = stressed_net - self._base_net
        delta_pct = (delta / abs(self._base_net) * 100) if self._base_net != 0 else 0.0
        return SensitivityScenario(
            factor=SensitivityFactor.FIXED_COST,
            label="Fixed +£{:,.0f}".format(additional_gbp),
            shock_magnitude=additional_gbp,
            base_net_margin_gbp=self._base_net,
            stressed_net_margin_gbp=stressed_net,
            delta_gbp=delta,
            delta_pct=delta_pct,
        )

    def standard_sensitivity_table(self) -> list[SensitivityScenario]:
        """Standard 10-row sensitivity table for board reporting."""
        return [
            self.wholesale_price_shock(+10),
            self.wholesale_price_shock(+20),
            self.demand_volume_shock(-5),
            self.demand_volume_shock(-10),
            self.churn_shock(5),
            self.churn_shock(10),
            self.non_commodity_cost_shock(5),
            self.non_commodity_cost_shock(10),
            self.fixed_cost_shock(5_000),
            self.fixed_cost_shock(10_000),
        ]

    def most_sensitive_factor(self) -> SensitivityFactor:
        """Which factor causes the largest absolute delta?"""
        scenarios = self.standard_sensitivity_table()
        return max(scenarios, key=lambda s: abs(s.delta_gbp)).factor

    def sensitivity_summary(self) -> str:
        scenarios = self.standard_sensitivity_table()
        lines = ["Portfolio Margin Sensitivity Analysis", "=" * 40, "Base net margin: £{:,.0f}".format(self._base_net), ""]
        for s in scenarios:
            lines.append("{}: stressed=£{:,.0f} delta=£{:,.0f} ({:.1f}%) [{}]".format(
                s.label,
                s.stressed_net_margin_gbp,
                s.delta_gbp,
                s.delta_pct,
                s.severity,
            ))
        msf = self.most_sensitive_factor()
        lines.append("\nMost sensitive factor: {}".format(msf.value))
        return chr(10).join(lines)
