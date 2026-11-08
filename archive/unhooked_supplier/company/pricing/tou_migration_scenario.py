"""ToU Migration Impact Scenario -- Phase V.

Models the impact on supplier margin and customer revenue if a fraction of
EV customers migrate from flat-rate tariffs to ToU tariffs.

Builds on Phase U (CrossSubsidyRegister). Answers the product strategy question:
"If we launch an EV ToU tariff and X% of customers take it up, what happens to
total supplier margin?" -- All inputs company-observable. Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from company.pricing.ev_cross_subsidy import CrossSubsidyRecord


@dataclass(frozen=True)
class MigrationScenario:
    migration_rate_pct: float
    total_ev_accounts: int
    migrated_count: int
    retained_count: int
    baseline_margin_gbp: float
    post_migration_margin_gbp: float
    baseline_revenue_gbp: float
    post_migration_revenue_gbp: float
    total_customer_saving_gbp: float

    @property
    def margin_delta_gbp(self) -> float:
        return round(self.post_migration_margin_gbp - self.baseline_margin_gbp, 2)

    @property
    def revenue_delta_gbp(self) -> float:
        return round(self.post_migration_revenue_gbp - self.baseline_revenue_gbp, 2)

    @property
    def avg_customer_saving_gbp(self) -> float:
        if self.migrated_count == 0:
            return 0.0
        return round(self.total_customer_saving_gbp / self.migrated_count, 2)

    @property
    def is_margin_positive(self) -> bool:
        return self.margin_delta_gbp >= 0


class ToUMigrationScenarioBook:
    """Models the supplier margin impact of EV customers migrating to ToU tariffs.

    Each scenario takes a migration rate and the CrossSubsidyRegister to compute
    the overall P&L impact. Customers migrate in order of lowest cross-subsidy
    first (they are most likely to switch -- least valuable flat-rate customers).
    """

    def __init__(self) -> None:
        self._scenarios: list = []

    def run_scenario(
        self,
        records: list,
        migration_rate_pct: float,
    ) -> MigrationScenario:
        """Compute migration scenario for given EV customer records and migration rate."""
        if not 0.0 <= migration_rate_pct <= 100.0:
            raise ValueError(f"migration_rate_pct must be 0-100, got {migration_rate_pct}")
        n = len(records)
        n_migrated = round(n * migration_rate_pct / 100.0)
        # Customers most likely to migrate: those with lowest cross-subsidy (least flat-rate benefit)
        sorted_by_subsidy = sorted(records, key=lambda r: r.cross_subsidy_gbp)
        migrated = sorted_by_subsidy[:n_migrated]
        retained = sorted_by_subsidy[n_migrated:]

        baseline_margin = round(sum(r.flat_margin_gbp for r in records), 2)
        baseline_revenue = round(sum(r.flat_revenue_gbp for r in records), 2)

        post_margin = round(
            sum(r.tou_margin_gbp for r in migrated)
            + sum(r.flat_margin_gbp for r in retained),
            2,
        )
        post_revenue = round(
            sum(r.tou_revenue_gbp for r in migrated)
            + sum(r.flat_revenue_gbp for r in retained),
            2,
        )

        total_saving = round(sum(r.customer_saving_gbp for r in migrated), 2)

        scenario = MigrationScenario(
            migration_rate_pct=migration_rate_pct,
            total_ev_accounts=n,
            migrated_count=n_migrated,
            retained_count=n - n_migrated,
            baseline_margin_gbp=baseline_margin,
            post_migration_margin_gbp=post_margin,
            baseline_revenue_gbp=baseline_revenue,
            post_migration_revenue_gbp=post_revenue,
            total_customer_saving_gbp=total_saving,
        )
        self._scenarios.append(scenario)
        return scenario

    def compare_rates(
        self, records: list, rates_pct: list
    ) -> list:
        """Run multiple migration rate scenarios and return sorted by migration_rate_pct."""
        return [self.run_scenario(records, r) for r in sorted(rates_pct)]

    def scenarios_run(self) -> list:
        return list(self._scenarios)

    def best_supplier_scenario(self) -> Optional:
        if not self._scenarios:
            return None
        return max(self._scenarios, key=lambda s: s.post_migration_margin_gbp)

    def portfolio_summary(self) -> dict:
        if not self._scenarios:
            return {"scenarios_run": 0}
        best = self.best_supplier_scenario()
        return {
            "scenarios_run": len(self._scenarios),
            "best_supplier_rate_pct": best.migration_rate_pct if best else None,
            "best_supplier_margin_gbp": best.post_migration_margin_gbp if best else None,
        }
