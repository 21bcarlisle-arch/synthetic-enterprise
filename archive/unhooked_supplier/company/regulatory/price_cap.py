from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Ofgem Default Tariff Cap (energy price cap) quarterly unit rates p/kWh and standing charges
# Representative dual-fuel annual equivalent for typical household (3100kWh elec, 12000kWh gas)
# Pre-cap era: SVT/standard variable tariff; cap launched Feb 2019 Q1
_PRICE_CAP_QUARTERLY: dict[str, dict] = {
    # Format: "YYYY-QN": {elec_p_kwh, gas_p_kwh, standing_elec_ppd, standing_gas_ppd, annual_bill_typical_gbp}
    "2019-Q1": {"elec_p_kwh": 17.14, "gas_p_kwh": 3.40, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1137},
    "2019-Q2": {"elec_p_kwh": 16.80, "gas_p_kwh": 3.35, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1116},
    "2019-Q3": {"elec_p_kwh": 16.90, "gas_p_kwh": 3.38, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1137},
    "2019-Q4": {"elec_p_kwh": 16.50, "gas_p_kwh": 3.30, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1109},
    "2020-Q1": {"elec_p_kwh": 16.40, "gas_p_kwh": 3.26, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1097},
    "2020-Q2": {"elec_p_kwh": 16.60, "gas_p_kwh": 3.30, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1119},
    "2020-Q3": {"elec_p_kwh": 16.50, "gas_p_kwh": 3.28, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1109},
    "2020-Q4": {"elec_p_kwh": 17.00, "gas_p_kwh": 3.35, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1138},
    "2021-Q1": {"elec_p_kwh": 16.80, "gas_p_kwh": 3.32, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1127},
    "2021-Q2": {"elec_p_kwh": 16.20, "gas_p_kwh": 3.26, "standing_elec_ppd": 24.0, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1091},
    "2021-Q3": {"elec_p_kwh": 18.90, "gas_p_kwh": 3.78, "standing_elec_ppd": 25.0, "standing_gas_ppd": 27.0, "annual_typical_gbp": 1277},
    "2021-Q4": {"elec_p_kwh": 20.80, "gas_p_kwh": 4.17, "standing_elec_ppd": 25.0, "standing_gas_ppd": 27.0, "annual_typical_gbp": 1277},
    "2022-Q1": {"elec_p_kwh": 28.34, "gas_p_kwh": 7.37, "standing_elec_ppd": 45.34, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1971},
    "2022-Q2": {"elec_p_kwh": 28.34, "gas_p_kwh": 7.37, "standing_elec_ppd": 45.34, "standing_gas_ppd": 26.0, "annual_typical_gbp": 1971},
    "2022-Q3": {"elec_p_kwh": 52.00, "gas_p_kwh": 14.97, "standing_elec_ppd": 45.0, "standing_gas_ppd": 27.0, "annual_typical_gbp": 3549},
    "2022-Q4": {"elec_p_kwh": 34.00, "gas_p_kwh": 10.32, "standing_elec_ppd": 46.0, "standing_gas_ppd": 28.0, "annual_typical_gbp": 2500},
    "2023-Q1": {"elec_p_kwh": 34.00, "gas_p_kwh": 10.32, "standing_elec_ppd": 46.0, "standing_gas_ppd": 28.0, "annual_typical_gbp": 2500},
    "2023-Q2": {"elec_p_kwh": 30.11, "gas_p_kwh": 8.55, "standing_elec_ppd": 52.97, "standing_gas_ppd": 29.60, "annual_typical_gbp": 2074},
    "2023-Q3": {"elec_p_kwh": 29.42, "gas_p_kwh": 7.42, "standing_elec_ppd": 53.35, "standing_gas_ppd": 29.60, "annual_typical_gbp": 1923},
    "2023-Q4": {"elec_p_kwh": 27.35, "gas_p_kwh": 6.89, "standing_elec_ppd": 53.37, "standing_gas_ppd": 29.62, "annual_typical_gbp": 1834},
    "2024-Q1": {"elec_p_kwh": 24.50, "gas_p_kwh": 6.04, "standing_elec_ppd": 61.64, "standing_gas_ppd": 31.65, "annual_typical_gbp": 1690},
    "2024-Q2": {"elec_p_kwh": 24.50, "gas_p_kwh": 6.04, "standing_elec_ppd": 61.64, "standing_gas_ppd": 31.65, "annual_typical_gbp": 1690},
    "2024-Q3": {"elec_p_kwh": 22.36, "gas_p_kwh": 5.48, "standing_elec_ppd": 61.64, "standing_gas_ppd": 31.65, "annual_typical_gbp": 1568},
    "2024-Q4": {"elec_p_kwh": 24.50, "gas_p_kwh": 6.24, "standing_elec_ppd": 61.64, "standing_gas_ppd": 31.65, "annual_typical_gbp": 1717},
    "2025-Q1": {"elec_p_kwh": 24.50, "gas_p_kwh": 6.33, "standing_elec_ppd": 61.64, "standing_gas_ppd": 31.65, "annual_typical_gbp": 1738},
}


_CAP_LAUNCH_QUARTER = (2019, 1)  # Ofgem Default Tariff Cap launched 1 Jan 2019


def _parse_quarter(quarter: str) -> Optional[tuple]:
    """('2024-Q1') -> (2024, 1); None if the key is not a well-formed quarter."""
    if not isinstance(quarter, str):
        return None
    parts = quarter.split("-Q")
    if len(parts) != 2:
        return None
    try:
        year, q = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    return (year, q) if 1 <= q <= 4 else None


_COMMODITY_RATE_KEY = {"electricity": "elec_p_kwh", "elec": "elec_p_kwh", "gas": "gas_p_kwh"}


class CapStatus(str, Enum):
    BELOW_CAP = "below_cap"
    AT_CAP = "at_cap"
    EXCEEDS_CAP = "exceeds_cap"
    PRE_CAP = "pre_cap"  # genuinely before the cap launched (Q1 2019)
    UNKNOWN = "unknown"  # no ceiling could be established — NOT compliance


@dataclass(frozen=True)
class CapComplianceCheck:
    quarter: str
    commodity: str
    supplier_rate_p_kwh: float
    cap_rate_p_kwh: float = 0.0  # DECLARED by the caller; not the authority — see effective_cap_p_kwh

    @property
    def effective_cap_p_kwh(self) -> Optional[float]:
        """The PUBLISHED ceiling for this quarter and commodity, or None.

        The caller's `cap_rate_p_kwh` is not consulted. It used to be the only
        thing consulted: this class held a quarter key, the module held the full
        published table keyed by exactly that string, and the check never looked
        the rate up -- so a supplier charging 99p in a 24.5p quarter declared
        itself compliant by passing its own cap number (R15 tautology: the
        checked value was supplied by the party being checked). The ceiling now
        comes from the table, keyed on BOTH quarter and commodity, which also
        closes the separate hole where `commodity` was recorded and read by
        nothing, so a gas rate could be cleared against the electricity cap.
        """
        row = _PRICE_CAP_QUARTERLY.get(self.quarter)
        if row is None:
            return None
        key = _COMMODITY_RATE_KEY.get(str(self.commodity).strip().lower())
        return None if key is None else row[key]

    @property
    def headroom_p_kwh(self) -> Optional[float]:
        cap = self.effective_cap_p_kwh
        return None if cap is None else round(cap - self.supplier_rate_p_kwh, 4)

    @property
    def status(self) -> CapStatus:
        cap = self.effective_cap_p_kwh
        if cap is None:
            # No published ceiling. PRE_CAP -- which is compliant -- is correct
            # ONLY for a quarter genuinely before the cap launched. It used to be
            # the answer for every unrecognised key, so every quarter past the
            # table's end (2025-Q1), every case typo and every empty string made
            # any breach compliant (R15 fail-open). Those are now UNKNOWN, which
            # is not compliance: the ceiling could not be established.
            parsed = _parse_quarter(self.quarter)
            if parsed is not None and parsed < _CAP_LAUNCH_QUARTER:
                return CapStatus.PRE_CAP
            return CapStatus.UNKNOWN
        if self.supplier_rate_p_kwh > cap:
            return CapStatus.EXCEEDS_CAP
        if abs(cap - self.supplier_rate_p_kwh) < 0.01:
            return CapStatus.AT_CAP
        return CapStatus.BELOW_CAP

    @property
    def is_compliant(self) -> bool:
        return self.status in (CapStatus.BELOW_CAP, CapStatus.AT_CAP, CapStatus.PRE_CAP)


class PriceCapBook:
    def __init__(self) -> None:
        self._checks: list[CapComplianceCheck] = []

    @staticmethod
    def cap_data(quarter: str) -> Optional[dict]:
        return _PRICE_CAP_QUARTERLY.get(quarter)

    @staticmethod
    def elec_cap_p_kwh(quarter: str) -> Optional[float]:
        d = _PRICE_CAP_QUARTERLY.get(quarter)
        return d["elec_p_kwh"] if d else None

    @staticmethod
    def gas_cap_p_kwh(quarter: str) -> Optional[float]:
        d = _PRICE_CAP_QUARTERLY.get(quarter)
        return d["gas_p_kwh"] if d else None

    @staticmethod
    def typical_annual_bill(quarter: str) -> Optional[int]:
        d = _PRICE_CAP_QUARTERLY.get(quarter)
        return d["annual_typical_gbp"] if d else None

    def record_check(self, check: CapComplianceCheck) -> CapComplianceCheck:
        self._checks.append(check)
        return check

    def breach_quarters(self) -> list[CapComplianceCheck]:
        return [c for c in self._checks if c.status == CapStatus.EXCEEDS_CAP]

    def peak_annual_bill_year(self) -> int:
        return max(
            (q for q in _PRICE_CAP_QUARTERLY if q.endswith("-Q3") or q.endswith("-Q2")),
            key=lambda q: _PRICE_CAP_QUARTERLY[q]["annual_typical_gbp"]
        )[:4]

    def cap_summary(self) -> dict:
        peak_q = max(_PRICE_CAP_QUARTERLY, key=lambda q: _PRICE_CAP_QUARTERLY[q]["annual_typical_gbp"])
        return {
            "quarters_available": len(_PRICE_CAP_QUARTERLY),
            "peak_typical_annual_gbp": _PRICE_CAP_QUARTERLY[peak_q]["annual_typical_gbp"],
            "peak_quarter": peak_q,
            "breach_count": len(self.breach_quarters()),
        }
