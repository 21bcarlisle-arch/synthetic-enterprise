from __future__ import annotations
from dataclasses import replace
from typing import Optional
from company.crm.property_model import EPCRating, Property, PropertyType, TenureType

class HomeRegistry:
    def __init__(self):
        self._profiles = {}

    def register(self, account_id, prop):
        if not isinstance(prop, Property):
            raise TypeError("prop must be a Property instance")
        self._profiles[account_id] = prop

    def upgrade_epc(self, account_id, new_rating):
        prop = self.get_profile(account_id)
        upgraded = replace(prop, epc_rating=new_rating)
        self._profiles[account_id] = upgraded
        return upgraded

    def get_profile(self, account_id):
        try:
            return self._profiles[account_id]
        except KeyError:
            raise KeyError("No property registered for account {}".format(account_id))

    def get_profile_or_none(self, account_id):
        return self._profiles.get(account_id)

    def profiles_by_epc(self, rating):
        return [aid for aid, p in self._profiles.items() if p.epc_rating == rating]

    def profiles_by_type(self, property_type):
        return [aid for aid, p in self._profiles.items() if p.property_type == property_type]

    def eco4_eligible_accounts(self):
        return [aid for aid, p in self._profiles.items() if p.eco4_eligible]

    def fuel_poor_accounts(self):
        return [aid for aid, p in self._profiles.items() if p.is_fuel_poor]

    def psr_priority_accounts(self):
        return [aid for aid, p in self._profiles.items() if p.psr_priority_property]

    def epc_distribution(self):
        counts = {}
        for p in self._profiles.values():
            counts[p.epc_rating.value] = counts.get(p.epc_rating.value, 0) + 1
        return dict(sorted(counts.items()))

    def fuel_distribution(self):
        gas = sum(1 for p in self._profiles.values() if p.has_gas)
        return {"gas": gas, "electric": len(self._profiles) - gas}

    def tenure_distribution(self):
        counts = {}
        for p in self._profiles.values():
            counts[p.tenure.value] = counts.get(p.tenure.value, 0) + 1
        return counts

    def total_estimated_elec_kwh(self):
        return sum(p.estimated_annual_elec_kwh for p in self._profiles.values())

    def total_estimated_gas_kwh(self):
        return sum(p.estimated_annual_gas_kwh for p in self._profiles.values())

    def registry_summary(self):
        n = len(self._profiles)
        return {
            "total_accounts": n,
            "epc_distribution": self.epc_distribution(),
            "fuel_distribution": self.fuel_distribution(),
            "tenure_distribution": self.tenure_distribution(),
            "eco4_eligible": len(self.eco4_eligible_accounts()),
            "fuel_poor": len(self.fuel_poor_accounts()),
            "psr_priority": len(self.psr_priority_accounts()),
            "total_estimated_elec_kwh": round(self.total_estimated_elec_kwh(), 0),
            "total_estimated_gas_kwh": round(self.total_estimated_gas_kwh(), 0),
        }
