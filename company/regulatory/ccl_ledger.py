"""Climate Change Levy (CCL) Ledger.

CCL is a UK carbon tax on business energy consumption introduced in 2001.
Energy suppliers collect CCL from business (non-domestic) customers and
remit to HMRC via quarterly returns.

Key rules:
- Residential customers: FULLY EXEMPT (CCLExemptReason.RESIDENTIAL)
- Renewable electricity with a valid LEC: EXEMPT (CCLExemptReason.LEC_COVERED)
- SME, I&C, and other business customers: PAY CCL at HMRC annual rates

Rate history: 2019 was the pivotal year. Budget 2018 shifted UK tax policy from
National Insurance Contributions (NIC) to carbon taxes -- CCL rose 45% on
electricity (0.583->0.847 p/kWh) and 67% on gas (0.203->0.339 p/kWh).

HMRC source: www.gov.uk/guidance/rates-and-allowances-climate-change-levy
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CCLFuel(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


class CCLExemptReason(str, Enum):
    RESIDENTIAL = "residential"
    LEC_COVERED = "lec_covered"


_CCL_ELECTRICITY_P_KWH: Dict[int, float] = {
    2001: 0.430, 2007: 0.441, 2008: 0.456, 2009: 0.470, 2010: 0.470,
    2011: 0.485, 2012: 0.509, 2013: 0.524, 2014: 0.541, 2015: 0.554,
    2016: 0.554, 2017: 0.568, 2018: 0.583,
    2019: 0.847,
    2020: 0.811, 2021: 0.775, 2022: 0.775, 2023: 0.775, 2024: 0.775, 2025: 0.775,
}

# CORRECTED 2026-08-18 against the statutory commons
# (docs/domain_artefact_library/regulatory/ccl_main_rates.json), which is THE LAW rather
# than a reading of it. This table had gas flat at 0.465 from 2021 through 2025 and missed
# the rebalancing entirely: gas CCL rose each April toward PARITY with electricity, reaching
# it in April 2024. The sim's own table (simulation/policy_costs.py) had the trajectory
# right the whole time -- two modules published the same statutory quantity and disagreed by
# up to 67%.
#
# 2023, 2024 and 2025 are corrected: the commons carries them at `primary` provenance,
# sourced to gov.uk's published CCL rates, so the source settles it.
# 2022 is NOT corrected: the commons itself records that year as `recalled -- not fetched;
# neighbours differ so it cannot be bracketed`, so nothing here is authoritative enough to
# overwrite it with. It is caveated below instead of being quietly changed to look tidy.
_CCL_GAS_P_KWH: Dict[int, float] = {
    2001: 0.150, 2007: 0.154, 2008: 0.159, 2009: 0.164, 2010: 0.164,
    2011: 0.169, 2012: 0.178, 2013: 0.183, 2014: 0.189, 2015: 0.195,
    2016: 0.195, 2017: 0.198, 2018: 0.203,
    2019: 0.339,
    2020: 0.406, 2021: 0.465,
    2022: 0.465,   # DISPUTED: the commons says 0.568 at `recalled` provenance, unfetched.
    2023: 0.672,   # was 0.465 -- gov.uk, 1 Apr 2023 to 31 Mar 2024
    2024: 0.775,   # was 0.465 -- gov.uk, 1 Apr 2024: gas reaches parity with electricity
    2025: 0.775,   # was 0.465 -- gov.uk, 1 Apr 2025 to 31 Mar 2026
}

#: Years where this table and the statutory commons disagree and NEITHER side is
#: authoritative -- the commons records them as recalled rather than fetched. Published with
#: both positions rather than silently reconciled; a figure that disagrees with itself and
#: says so is worth more than one that agrees by fiat.
CCL_DISPUTED_YEARS: Dict[tuple, str] = {
    (2016, "electricity"): "this table 0.554, statutory commons 0.559 (commons: recalled, not fetched)",
    (2022, "gas"): "this table 0.465, statutory commons 0.568 (commons: recalled, not fetched)",
}


@dataclass(frozen=True)
class CCLCharge:
    account_id: str
    fuel: CCLFuel
    year: int
    consumption_kwh: float
    rate_p_per_kwh: float
    exempt_reason: Optional[CCLExemptReason] = None

    @property
    def is_exempt(self) -> bool:
        return self.exempt_reason is not None

    @property
    def charge_gbp(self) -> float:
        if self.is_exempt:
            return 0.0
        return round(self.consumption_kwh * self.rate_p_per_kwh / 100, 2)


@dataclass(frozen=True)
class CCLQuarterlyReturn:
    quarter_end: dt.date
    electricity_kwh: float
    gas_kwh: float
    electricity_due_gbp: float
    gas_due_gbp: float
    filed: bool = False

    @property
    def total_due_gbp(self) -> float:
        return round(self.electricity_due_gbp + self.gas_due_gbp, 2)

    @property
    def is_nil_return(self) -> bool:
        return self.total_due_gbp == 0.0


class CCLLedger:
    """Records CCL charges per account and generates HMRC quarterly returns."""

    def __init__(self) -> None:
        self._charges: List[CCLCharge] = []

    @staticmethod
    def rate_for_year(year: int, fuel: CCLFuel) -> float:
        """Return the CCL rate (p/kWh) for the given calendar year and fuel."""
        table = (_CCL_ELECTRICITY_P_KWH if fuel == CCLFuel.ELECTRICITY
                 else _CCL_GAS_P_KWH)
        if year in table:
            return table[year]
        closest = min(table.keys(), key=lambda y: abs(y - year))
        return table[closest]

    def record_charge(
        self,
        account_id: str,
        year: int,
        fuel: CCLFuel,
        consumption_kwh: float,
        *,
        is_business: bool,
        lec_covered: bool = False,
    ) -> CCLCharge:
        exempt_reason: Optional[CCLExemptReason] = None
        if not is_business:
            exempt_reason = CCLExemptReason.RESIDENTIAL
        elif lec_covered:
            exempt_reason = CCLExemptReason.LEC_COVERED

        rate = CCLLedger.rate_for_year(year, fuel)
        charge = CCLCharge(
            account_id=account_id,
            fuel=fuel,
            year=year,
            consumption_kwh=consumption_kwh,
            rate_p_per_kwh=rate,
            exempt_reason=exempt_reason,
        )
        self._charges.append(charge)
        return charge

    def charges_for_account(self, account_id: str) -> List[CCLCharge]:
        return [c for c in self._charges if c.account_id == account_id]

    def charges_for_year(self, year: int) -> List[CCLCharge]:
        return [c for c in self._charges if c.year == year]

    def total_due_gbp(self, year: int) -> float:
        """Total CCL liability to HMRC for the given calendar year."""
        return round(sum(c.charge_gbp for c in self.charges_for_year(year)), 2)

    def quarterly_return(
        self, quarter_end: dt.date, *, filed: bool = False
    ) -> CCLQuarterlyReturn:
        """Aggregate charges for the year of quarter_end into a return."""
        year = quarter_end.year
        relevant = self.charges_for_year(year)

        elec_kwh = sum(
            c.consumption_kwh for c in relevant
            if c.fuel == CCLFuel.ELECTRICITY and not c.is_exempt
        )
        gas_kwh = sum(
            c.consumption_kwh for c in relevant
            if c.fuel == CCLFuel.GAS and not c.is_exempt
        )
        elec_due = round(sum(
            c.charge_gbp for c in relevant if c.fuel == CCLFuel.ELECTRICITY
        ), 2)
        gas_due = round(sum(
            c.charge_gbp for c in relevant if c.fuel == CCLFuel.GAS
        ), 2)

        return CCLQuarterlyReturn(
            quarter_end=quarter_end,
            electricity_kwh=elec_kwh,
            gas_kwh=gas_kwh,
            electricity_due_gbp=elec_due,
            gas_due_gbp=gas_due,
            filed=filed,
        )

    def ccl_summary(self) -> dict:
        """Summary dict for board reporting."""
        years = sorted({c.year for c in self._charges})
        return {
            "total_charges_recorded": len(self._charges),
            "exempt_charges": sum(1 for c in self._charges if c.is_exempt),
            "chargeable_charges": sum(1 for c in self._charges if not c.is_exempt),
            "years_covered": years,
            "total_due_by_year": {y: self.total_due_gbp(y) for y in years},
            "residential_exempt": sum(
                1 for c in self._charges
                if c.exempt_reason == CCLExemptReason.RESIDENTIAL
            ),
            "lec_exempt": sum(
                1 for c in self._charges
                if c.exempt_reason == CCLExemptReason.LEC_COVERED
            ),
        }
