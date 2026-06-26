from __future__ import annotations

from dataclasses import dataclass
from datetime import date

_KWH_PER_THERM = 29.31
_LONG_CREDIT_FACTOR = 0.85


@dataclass
class DailyNomination:
    date: date
    gas_account_id: str
    nominated_kwh: float
    actual_kwh: float
    nbp_spot_gbp_per_therm: float


class GasNominationBook:
    def __init__(self):
        self._nominations = []

    def nominate(self, nom):
        self._nominations.append(nom)

    def imbalance_kwh(self, target_date, gas_account_id):
        for n in self._nominations:
            if n.date == target_date and n.gas_account_id == gas_account_id:
                return n.actual_kwh - n.nominated_kwh
        return 0.0

    def cash_out_cost_gbp(self, target_date, gas_account_id):
        nom = next((n for n in self._nominations if n.date == target_date and n.gas_account_id == gas_account_id), None)
        if nom is None:
            return 0.0
        imb_kwh = nom.actual_kwh - nom.nominated_kwh
        if abs(imb_kwh) < 0.001:
            return 0.0
        imb_therms = imb_kwh / _KWH_PER_THERM
        if imb_kwh > 0:
            return round(imb_therms * nom.nbp_spot_gbp_per_therm, 2)
        return round(imb_therms * nom.nbp_spot_gbp_per_therm * _LONG_CREDIT_FACTOR, 2)

    def nomination_accuracy_pct(self, tolerance=0.05):
        if not self._nominations:
            return 0.0
        accurate = sum(1 for n in self._nominations if n.actual_kwh > 0 and abs(n.actual_kwh - n.nominated_kwh) / n.actual_kwh <= tolerance)
        return round(accurate / len(self._nominations) * 100.0, 1)

    def monthly_cashout_gbp(self, year, month):
        seen = set()
        total = 0.0
        for n in self._nominations:
            if n.date.year == year and n.date.month == month:
                key = (n.date, n.gas_account_id)
                if key not in seen:
                    seen.add(key)
                    total += self.cash_out_cost_gbp(n.date, n.gas_account_id)
        return round(total, 2)

    def annual_cashout_gbp(self, year):
        return round(sum(self.monthly_cashout_gbp(year, m) for m in range(1, 13)), 2)

    def worst_imbalance_periods(self, n=5):
        events = []
        for nom in self._nominations:
            cost = self.cash_out_cost_gbp(nom.date, nom.gas_account_id)
            if cost != 0.0:
                events.append({
                    "date": nom.date.isoformat(),
                    "gas_account_id": nom.gas_account_id,
                    "imbalance_kwh": round(nom.actual_kwh - nom.nominated_kwh, 1),
                    "nbp_spot_gbp_per_therm": nom.nbp_spot_gbp_per_therm,
                    "cost_gbp": cost,
                })
        events.sort(key=lambda e: abs(e["cost_gbp"]), reverse=True)
        return events[:n]

    def balancing_summary(self):
        total_cost = 0.0
        short_count = 0
        long_count = 0
        for n in self._nominations:
            cost = self.cash_out_cost_gbp(n.date, n.gas_account_id)
            total_cost += cost
            imb = n.actual_kwh - n.nominated_kwh
            if imb > 0.001:
                short_count += 1
            elif imb < -0.001:
                long_count += 1
        return {
            "total_nominations": len(self._nominations),
            "short_periods": short_count,
            "long_periods": long_count,
            "nomination_accuracy_pct": self.nomination_accuracy_pct(),
            "total_cashout_gbp": round(total_cost, 2),
            "net_position": "cost" if total_cost > 0 else "receipt" if total_cost < 0 else "balanced",
        }
