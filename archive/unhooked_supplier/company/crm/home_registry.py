from __future__ import annotations
import datetime as dt
from dataclasses import replace
from typing import Optional
from company.crm.property_model import (
    EPCRating, Property, PropertyType, TenureType, TRACKED_BELIEF_FIELDS,
)
from company.crm import property_discovery

class HomeRegistry:
    """Company-side belief store, keyed by account_id.

    Populate it via the discovery methods below (register_from_signup /
    record_epc_lookup / record_tariff_registration / record_engineer_visit)
    -- each corresponds to a real OBSERVABLE event a UK supplier could
    actually witness. `register()` remains available for tests/callers that
    already hold a fully-formed Property (e.g. constructed via the
    discovery module themselves), but nothing in this class or its callers
    may build that Property from sim-side ground truth
    (saas/property_model.py) -- see company/crm/property_discovery.py.
    """

    def __init__(self):
        self._profiles = {}

    def register(self, account_id, prop):
        if not isinstance(prop, Property):
            raise TypeError("prop must be a Property instance")
        self._profiles[account_id] = prop

    def register_from_signup(self, account_id, uprn, as_of=None, **disclosed):
        """Open a belief for a brand-new account from the onboarding
        disclosure event (company/crm/property_discovery.open_belief_from_signup).
        `disclosed` accepts property_type/tenure/bedrooms/occupants/has_gas --
        anything omitted is filled from an unconfirmed population-average
        default, never from ground truth."""
        as_of = as_of or dt.date.today()
        prop = property_discovery.open_belief_from_signup(uprn, as_of, **disclosed)
        self._profiles[account_id] = prop
        return prop

    def record_epc_lookup(self, account_id, epc_rating, as_of=None):
        """An EPC-certificate-register lookup event."""
        as_of = as_of or dt.date.today()
        prop = self.get_profile(account_id)
        updated = property_discovery.apply_epc_lookup(prop, epc_rating, as_of)
        self._profiles[account_id] = updated
        return updated

    def record_tariff_registration(self, account_id, as_of=None, **kwargs):
        """The customer registers for an EV/solar-export tariff."""
        as_of = as_of or dt.date.today()
        prop = self.get_profile(account_id)
        updated = property_discovery.apply_tariff_registration(prop, as_of, **kwargs)
        self._profiles[account_id] = updated
        return updated

    def record_engineer_visit(self, account_id, as_of=None, **kwargs):
        """A meter-engineer site visit corrects floor area/bedrooms/occupants."""
        as_of = as_of or dt.date.today()
        prop = self.get_profile(account_id)
        updated = property_discovery.apply_engineer_visit(prop, as_of, **kwargs)
        self._profiles[account_id] = updated
        return updated

    def upgrade_epc(self, account_id, new_rating, as_of=None):
        """Kept for existing callers: a re-lookup that finds a new EPC
        rating (e.g. following an insulation upgrade). Delegates to the
        same discovery path as record_epc_lookup so provenance is always
        stamped, never silently mutated."""
        return self.record_epc_lookup(account_id, new_rating, as_of=as_of)

    def belief_confidence(self, account_id):
        """Per-attribute {source, confidence, as_of} plus the overall
        confidence gauge for this account's current belief."""
        prop = self.get_profile(account_id)
        return {
            "overall_confidence": prop.overall_confidence,
            "attributes": {
                name: {
                    "value": getattr(prop, name).value if hasattr(getattr(prop, name), 'value')
                             else getattr(prop, name),
                    "source": prop.source_for(name),
                    "confidence": prop.confidence_for(name),
                    "as_of": str(prop.as_of_for(name)) if prop.as_of_for(name) else None,
                }
                for name in TRACKED_BELIEF_FIELDS
            },
        }

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
