from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

GAS_EXIT_RESI_CHURN_RISK = 0.20
GAS_EXIT_IC_CHURN_RISK = 0.40

@dataclass(frozen=True)
class GasAccountProfile:
    customer_id: str
    segment: str
    gas_gross_gbp: float
    gas_capital_gbp: float
    gas_net_gbp: float
    gas_revenue_gbp: float
    elec_net_gbp: float
    combined_net_gbp: float

    @property
    def is_gas_accretive(self) -> bool:
        return self.gas_net_gbp >= 0

    @property
    def gas_roc(self):
        if self.gas_capital_gbp <= 0:
            return None
        return self.gas_net_gbp / self.gas_capital_gbp

    @property
    def breakeven_revenue_uplift_pct(self) -> float:
        if self.is_gas_accretive or self.gas_revenue_gbp <= 0:
            return 0.0
        return -self.gas_net_gbp / self.gas_revenue_gbp


@dataclass(frozen=True)
class GasScenarioResult:
    scenario_name: str
    total_net_gbp: float
    gas_net_gbp: float
    elec_net_gbp: float
    customers_retained: int
    customers_lost: int
    accounts_exited: list


class GasExitDecisionBook:
    def __init__(self, per_cid_comm_pnl, per_customer_lifetime, dual_fuel_pairs=None):
        self._pcp = per_cid_comm_pnl
        self._pcl = per_customer_lifetime
        self._pairs = dual_fuel_pairs or self._infer_pairs()
        self._profiles = self._build_profiles()

    def _infer_pairs(self):
        pairs = []
        for cid, comms in self._pcp.items():
            if cid.endswith("g"):
                elec_cid = cid[:-1]
                if elec_cid in self._pcp:
                    pairs.append((elec_cid, cid))
        return pairs

    def _build_profiles(self):
        profiles = []
        for elec_cid, gas_cid in self._pairs:
            comms = self._pcp.get(elec_cid, {})
            gas_comms = self._pcp.get(gas_cid, {})
            elec_data = comms.get("electricity", {})
            gas_data = gas_comms.get("gas", {})
            seg = self._pcl.get(elec_cid, {}).get("segment", "resi")
            profiles.append(GasAccountProfile(
                customer_id=elec_cid,
                segment=seg,
                gas_gross_gbp=gas_data.get("gross", 0.0),
                gas_capital_gbp=gas_data.get("capital", 0.0),
                gas_net_gbp=gas_data.get("net", 0.0),
                gas_revenue_gbp=gas_data.get("revenue", 0.0),
                elec_net_gbp=elec_data.get("net", 0.0),
                combined_net_gbp=elec_data.get("net", 0.0) + gas_data.get("net", 0.0),
            ))
        return profiles

    def status_quo(self):
        total = sum(p.combined_net_gbp for p in self._profiles)
        gas = sum(p.gas_net_gbp for p in self._profiles)
        elec = sum(p.elec_net_gbp for p in self._profiles)
        return GasScenarioResult(scenario_name="STATUS_QUO", total_net_gbp=total, gas_net_gbp=gas, elec_net_gbp=elec, customers_retained=len(self._profiles), customers_lost=0, accounts_exited=[])

    def exit_gas(self):
        elec_net_total = 0.0
        lost = []
        retained_count = 0
        for p in self._profiles:
            churn_risk = GAS_EXIT_IC_CHURN_RISK if p.segment == "I&C" else GAS_EXIT_RESI_CHURN_RISK
            expected_elec = p.elec_net_gbp * (1 - churn_risk)
            elec_net_total += expected_elec
            retained_count += 1
            if churn_risk >= GAS_EXIT_IC_CHURN_RISK:
                lost.append(p.customer_id)
        return GasScenarioResult(scenario_name="EXIT_GAS", total_net_gbp=elec_net_total, gas_net_gbp=0.0, elec_net_gbp=elec_net_total, customers_retained=retained_count, customers_lost=len(lost), accounts_exited=lost)

    def reprice_gas(self):
        gas_net_total = sum(p.gas_net_gbp if p.is_gas_accretive else 0.0 for p in self._profiles)
        elec_net_total = sum(p.elec_net_gbp for p in self._profiles)
        return GasScenarioResult(scenario_name="REPRICE_GAS", total_net_gbp=elec_net_total + gas_net_total, gas_net_gbp=gas_net_total, elec_net_gbp=elec_net_total, customers_retained=len(self._profiles), customers_lost=0, accounts_exited=[])

    def loss_making_accounts(self):
        return [p for p in self._profiles if not p.is_gas_accretive]

    def accretive_accounts(self):
        return [p for p in self._profiles if p.is_gas_accretive]

    def scenario_comparison(self):
        sq = self.status_quo()
        exit_s = self.exit_gas()
        reprice_s = self.reprice_gas()
        sq_net = sq.total_net_gbp
        return {
            "status_quo_net_gbp": round(sq_net, 2),
            "exit_gas_net_gbp": round(exit_s.total_net_gbp, 2),
            "reprice_gas_net_gbp": round(reprice_s.total_net_gbp, 2),
            "exit_vs_status_quo_gbp": round(exit_s.total_net_gbp - sq_net, 2),
            "reprice_vs_status_quo_gbp": round(reprice_s.total_net_gbp - sq_net, 2),
            "recommended_action": "REPRICE_GAS" if reprice_s.total_net_gbp > exit_s.total_net_gbp else "EXIT_GAS",
            "loss_making_accounts": [p.customer_id for p in self.loss_making_accounts()],
        }

    def gas_exit_summary(self):
        comp = self.scenario_comparison()
        loss_accs = self.loss_making_accounts()
        lines = [
            "Gas Exit Decision Book",
            "=" * 30,
            "Loss-making gas accounts: " + str(len(loss_accs)) + " (" + ", ".join(p.customer_id for p in loss_accs) + ")",
            "Status quo net (dual-fuel portfolio): " + str(round(comp["status_quo_net_gbp"], 2)),
            "Exit gas net (expected): " + str(round(comp["exit_gas_net_gbp"], 2)) + " (" + str(round(comp["exit_vs_status_quo_gbp"], 2)) + " vs SQ)",
            "Reprice gas net (break-even): " + str(round(comp["reprice_gas_net_gbp"], 2)) + " (" + str(round(comp["reprice_vs_status_quo_gbp"], 2)) + " vs SQ)",
            "Recommended action: " + comp["recommended_action"],
        ]
        return chr(10).join(lines)