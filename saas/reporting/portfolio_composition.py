from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Gross margin concentration thresholds
_CONCENTRATION_RED = 90.0    # >90% in one segment = severe concentration risk
_CONCENTRATION_AMBER = 70.0  # >70% = material concentration

# Electricity gross margin share benchmarks (Ofgem Retail Market Monitoring)
_ELEC_SHARE_LOW = 60.0   # electricity typically 60-90% of gross for mixed portfolio
_ELEC_SHARE_HIGH = 95.0


@dataclass(frozen=True)
class PortfolioComposition:
    year: int
    resi_gross_pct: float
    sme_gross_pct: float
    ic_gross_pct: float
    elec_gross_pct: float
    gas_gross_pct: float
    total_gross_gbp: float
    dominant_segment: str          # "resi", "sme", or "ic"
    concentration_rag: Literal["GREEN", "AMBER", "RED"]


def _dominant(resi: float, sme: float, ic: float) -> str:
    if ic >= resi and ic >= sme:
        return "ic"
    if resi >= sme:
        return "resi"
    return "sme"


def _concentration_rag(dominant_pct: float) -> Literal["GREEN", "AMBER", "RED"]:
    if dominant_pct >= _CONCENTRATION_RED:
        return "RED"
    if dominant_pct >= _CONCENTRATION_AMBER:
        return "AMBER"
    return "GREEN"


def _build_composition(yr_str: str, year_data: dict) -> PortfolioComposition:
    ss = year_data.get("segment_split", {})
    cs = year_data.get("commodity_split", {})

    resi_gross = sum(v.get("gross_gbp", 0.0) for k, v in ss.items() if k.startswith("resi"))
    sme_gross = sum(v.get("gross_gbp", 0.0) for k, v in ss.items() if k.startswith("SME"))
    ic_gross = sum(v.get("gross_gbp", 0.0) for k, v in ss.items() if k.startswith("I&C"))
    total = resi_gross + sme_gross + ic_gross

    elec_gross = cs.get("electricity", {}).get("gross_gbp", 0.0)
    gas_gross = cs.get("gas", {}).get("gross_gbp", 0.0)
    total_fuel = elec_gross + gas_gross

    def _pct(num, denom):
        return num / denom * 100 if denom > 0 else 0.0

    resi_pct = _pct(resi_gross, total)
    sme_pct = _pct(sme_gross, total)
    ic_pct = _pct(ic_gross, total)
    dom = _dominant(resi_pct, sme_pct, ic_pct)
    dom_pct = {"resi": resi_pct, "sme": sme_pct, "ic": ic_pct}[dom]

    return PortfolioComposition(
        year=int(yr_str),
        resi_gross_pct=resi_pct,
        sme_gross_pct=sme_pct,
        ic_gross_pct=ic_pct,
        elec_gross_pct=_pct(elec_gross, total_fuel),
        gas_gross_pct=_pct(gas_gross, total_fuel),
        total_gross_gbp=total,
        dominant_segment=dom,
        concentration_rag=_concentration_rag(dom_pct),
    )


def build_composition_series(run_data: dict) -> list[PortfolioComposition]:
    years_raw = run_data.get("years", {})
    return [
        _build_composition(yr, years_raw[yr])
        for yr in sorted(years_raw.keys())
    ]
