from __future__ import annotations
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class StressScenario(Enum):
    MARKET_SPIKE = "market_spike"
    CREDIT_DEFAULT = "credit_default"
    DEMAND_SHOCK = "demand_shock"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    COMBINED_CRISIS = "combined_crisis"


_DEFAULT_ASSUMPTIONS: dict = {
    "market_spike": {
        "price_multiplier_elec": 5.0,
        "price_multiplier_gas": 4.0,
        "demand_uplift_pct": 0.0,
        "margin_call_gbp": 150_000.0,
        "counterparty_default_gbp": 0.0,
        "duration_weeks": 13,
    },
    "credit_default": {
        "price_multiplier_elec": 1.2,
        "price_multiplier_gas": 1.2,
        "demand_uplift_pct": 0.0,
        "margin_call_gbp": 0.0,
        "counterparty_default_gbp": 1_000_000.0,
        "duration_weeks": 4,
    },
    "demand_shock": {
        "price_multiplier_elec": 2.0,
        "price_multiplier_gas": 2.5,
        "demand_uplift_pct": 30.0,
        "margin_call_gbp": 75_000.0,
        "counterparty_default_gbp": 0.0,
        "duration_weeks": 6,
    },
    "liquidity_crisis": {
        "price_multiplier_elec": 1.0,
        "price_multiplier_gas": 1.0,
        "demand_uplift_pct": 0.0,
        "margin_call_gbp": 500_000.0,
        "counterparty_default_gbp": 250_000.0,
        "duration_weeks": 8,
    },
    "combined_crisis": {
        "price_multiplier_elec": 5.0,
        "price_multiplier_gas": 4.0,
        "demand_uplift_pct": 20.0,
        "margin_call_gbp": 500_000.0,
        "counterparty_default_gbp": 1_000_000.0,
        "duration_weeks": 13,
    },
}


@dataclass(frozen=True)
class StressAssumption:
    scenario: StressScenario
    price_multiplier_elec: float
    price_multiplier_gas: float
    demand_uplift_pct: float
    margin_call_gbp: float
    counterparty_default_gbp: float
    duration_weeks: int

    @classmethod
    def default_for(cls, scenario: "StressScenario") -> "StressAssumption":
        params = _DEFAULT_ASSUMPTIONS[scenario.value]
        return cls(scenario=scenario, **params)


@dataclass(frozen=True)
class StressResult:
    result_id: str
    scenario: StressScenario
    starting_treasury_gbp: float
    stressed_treasury_gbp: float
    treasury_drawdown_gbp: float
    peak_var_gbp: float
    margin_calls_triggered_gbp: float
    weeks_to_cash_concern: Optional[int]
    survives: bool
    survival_headroom_gbp: float

    @property
    def drawdown_pct(self) -> float:
        if self.starting_treasury_gbp == 0:
            return 0.0
        return (self.treasury_drawdown_gbp / self.starting_treasury_gbp) * 100.0

    @property
    def is_severe(self) -> bool:
        return self.survival_headroom_gbp < 250_000.0

    @property
    def severity_rag(self) -> str:
        if not self.survives:
            return "RED"
        pct = self.drawdown_pct
        if pct < 10.0:
            return "GREEN"
        if pct <= 40.0:
            return "AMBER"
        return "RED"


def _compute_stress(starting_treasury_gbp, current_var_gbp, assumption, weekly_burn_gbp, credit_facility_gbp):
    combined_price_factor = (assumption.price_multiplier_elec + assumption.price_multiplier_gas) / 2.0
    peak_var = current_var_gbp * combined_price_factor
    demand_cost_uplift = weekly_burn_gbp * (assumption.demand_uplift_pct / 100.0) * 0.5
    weekly_stressed_burn = weekly_burn_gbp + demand_cost_uplift
    operational_cost = weekly_stressed_burn * assumption.duration_weeks
    facility_drawdown = min(credit_facility_gbp * 0.9, operational_cost * 0.4)
    net_outflow = assumption.margin_call_gbp + assumption.counterparty_default_gbp + operational_cost - facility_drawdown
    stressed_treasury = starting_treasury_gbp - net_outflow
    if stressed_treasury > 0:
        weeks_to_cash_concern = None
    else:
        wk = weekly_stressed_burn - (facility_drawdown / max(assumption.duration_weeks, 1))
        wk += (assumption.margin_call_gbp + assumption.counterparty_default_gbp) / max(assumption.duration_weeks, 1)
        weeks_to_cash_concern = max(0, int(starting_treasury_gbp / wk)) if wk > 0 else assumption.duration_weeks
    return stressed_treasury, peak_var, weeks_to_cash_concern


class StressTestBook:
    def __init__(self, credit_facility_gbp: float = 5_000_000.0) -> None:
        self.credit_facility_gbp = credit_facility_gbp
        self._results: list = []

    def run_stress(self, scenario, starting_treasury_gbp, current_var_gbp, weekly_burn_gbp=50_000.0, assumption=None):
        if assumption is None:
            assumption = StressAssumption.default_for(scenario)
        stressed_treasury, peak_var, weeks_to_cash_concern = _compute_stress(
            starting_treasury_gbp, current_var_gbp, assumption, weekly_burn_gbp, self.credit_facility_gbp)
        drawdown = starting_treasury_gbp - stressed_treasury
        survives = stressed_treasury > 0
        result = StressResult(
            result_id=str(uuid.uuid4()), scenario=scenario,
            starting_treasury_gbp=starting_treasury_gbp, stressed_treasury_gbp=stressed_treasury,
            treasury_drawdown_gbp=drawdown, peak_var_gbp=peak_var,
            margin_calls_triggered_gbp=assumption.margin_call_gbp,
            weeks_to_cash_concern=weeks_to_cash_concern, survives=survives,
            survival_headroom_gbp=stressed_treasury)
        self._results.append(result)
        return result

    def results_for_scenario(self, scenario):
        return [r for r in self._results if r.scenario == scenario]

    def worst_case(self):
        if not self._results:
            return None
        return max(self._results, key=lambda r: r.treasury_drawdown_gbp)

    def probability_weighted_loss_gbp(self, scenario_probs):
        total = 0.0
        for scenario, prob in scenario_probs.items():
            results = self.results_for_scenario(scenario)
            if results:
                total += results[-1].treasury_drawdown_gbp * prob
        return total

    def scenarios_survived(self):
        seen, survived = set(), []
        for r in reversed(self._results):
            if r.scenario not in seen:
                seen.add(r.scenario)
                if r.survives:
                    survived.append(r.scenario)
        return survived

    def scenarios_failed(self):
        seen, failed = set(), []
        for r in reversed(self._results):
            if r.scenario not in seen:
                seen.add(r.scenario)
                if not r.survives:
                    failed.append(r.scenario)
        return failed

    def all_red(self):
        return [r for r in self._results if r.severity_rag == "RED"]

    def stress_summary(self):
        worst = self.worst_case()
        return {
            "total_runs": len(self._results),
            "scenarios_run": list({r.scenario.value for r in self._results}),
            "scenarios_survived": [s.value for s in self.scenarios_survived()],
            "scenarios_failed": [s.value for s in self.scenarios_failed()],
            "worst_case_scenario": worst.scenario.value if worst else None,
            "worst_case_drawdown_gbp": round(worst.treasury_drawdown_gbp, 2) if worst else None,
            "worst_case_rag": worst.severity_rag if worst else None,
            "red_count": len(self.all_red()),
            "credit_facility_gbp": self.credit_facility_gbp,
        }
