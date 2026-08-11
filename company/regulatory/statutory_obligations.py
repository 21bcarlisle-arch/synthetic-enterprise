"""The supplier's own statutory obligation costs: RO, FiT levelisation, CCL.

KNIFE pass 3, `A_composition_lift` step 17, 2026-08-11, disposition register
§3l. Before this, `simulation/run_phase2b.py::main()` computed all three itself
— it opened a `ROCLedger`, a `FITBook` and a `CCLLedger`, accumulated the annual
volumes off the settled records, and reached for three of those modules' PRIVATE
rate tables (`_ROC_OBLIGATION_LEVEL`, `_ROC_BUY_OUT_PRICE_GBP`,
`_FIT_LEVELISATION_RATE_PER_MWH`) to build the per-year figures. That was three
of that module's wall crossings.

WHY THIS IS THE SUPPLIER'S AND NOT THE WORLD'S. Working out what you owe under
the Renewables Obligation, the FiT levelisation levy and the Climate Change Levy
is not physics — it is a licensed supplier doing its own statutory accounting off
its own supply volumes, and getting it wrong is what Ofgem and HMRC fine
suppliers for. The world's job is to have supplied the volumes; deciding the
obligation level, which customers are CCL-liable, and what the buy-out costs is
the supplier's reading of its own obligations, and it is allowed to be wrong.

WHAT ARRIVES AND WHAT DOES NOT. The settled records (the supplier's own billing
output) and the two I&C customer-id sets (its own book segmentation) — both
things a real supplier reads off its own systems. This module imports nothing
from `simulation/` or `sim/`; the records arrive as plain dicts through the one
signature. The three ledgers it composes are stdlib-only company modules, so no
edge is created in either direction.

WHY IT IS A GROUP AND NOT THREE ITEMS. RO and FiT are computed off ONE shared
accumulator — the annual electricity volume supplied (`_elec_mwh_by_year` in the
code this replaced). Cutting them separately would have left the world holding
that intermediate and threading it into both doors, which is a seam that
publishes a pull: half a cut. CCL joins them because it is the same process on
the same input at the same point in the report — the supplier's annual statutory
return — and it is the only one of the three that needs the segmentation.

BEHAVIOUR IS UNCHANGED BY CONSTRUCTION. The three blocks are transcribed
statement-for-statement, in their original order, off the same inputs; the
rounding is at the same places and the summary dicts carry the same keys. The
one thing that genuinely changed hands: the private rate tables are now read
INSIDE the layer that owns them, so the world no longer reaches through a
sibling module's underscore.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from company.regulatory.ccl_ledger import CCLFuel, CCLLedger
from company.regulatory.fit_book import _FIT_LEVELISATION_RATE_PER_MWH, FITBook
from company.regulatory.roc_ledger import (
    _ROC_BUY_OUT_PRICE_GBP,
    _ROC_OBLIGATION_LEVEL,
    ROCLedger,
)

__all__ = ["StatutoryObligations", "build_statutory_obligations"]


@dataclass(frozen=True)
class StatutoryObligations:
    """The three statutory obligation summaries, as the report consumes them."""

    roc_summary: dict
    fit_summary: dict
    ccl_summary: dict


def _annual_elec_mwh(settled_records: Sequence[Mapping]) -> dict:
    """Electricity volume supplied per year, MWh. The RO/FiT shared accumulator.

    This is the intermediate that makes RO and FiT ONE group rather than two
    items: it is derived once and read by both. Keeping it a named function
    rather than inlining it twice is what stops the two blocks drifting apart.
    """
    _elec_mwh_by_year: dict = defaultdict(float)
    for _rec in settled_records:
        if _rec.get("commodity", "elec") != "gas":
            _yr_roc = _rec.get("settlement_date", "")[:4]
            if _yr_roc:
                _elec_mwh_by_year[_yr_roc] += _rec.get("consumption_kwh", 0.0) / 1000.0
    return _elec_mwh_by_year


def _roc_summary(all_years: list[str], _elec_mwh_by_year: dict) -> dict:
    """Phase OG: Renewable Obligation (RO) cost."""
    _roc_ledger = ROCLedger()
    _roc_per_year = {}
    for _yr_roc in all_years:
        _mwh = _elec_mwh_by_year.get(_yr_roc, 0.0)
        _oblig = _roc_ledger.create_obligation(int(_yr_roc), round(_mwh, 1))
        _price = _ROC_BUY_OUT_PRICE_GBP.get(int(_yr_roc), 50.0)
        _level = _ROC_OBLIGATION_LEVEL.get(int(_yr_roc), 0.35)
        _roc_per_year[_yr_roc] = {
            "elec_mwh": round(_mwh, 1),
            "rocs_required": round(_oblig.rocs_required, 1),
            "obligation_level": _level,
            "buy_out_price_gbp": _price,
            "buy_out_cost_gbp": round(_oblig.rocs_required * _price, 0),
        }
    return {
        "total_buy_out_cost_gbp": round(
            sum(v["buy_out_cost_gbp"] for v in _roc_per_year.values()), 0
        ),
        "per_year": _roc_per_year,
    }


def _fit_summary(all_years: list[str], _elec_mwh_by_year: dict) -> dict:
    """Phase OH: FiT Levelisation Levy."""
    _fit_book = FITBook()
    _fit_per_year = {}
    for _yr_fit in all_years:
        _mwh_fit = _elec_mwh_by_year.get(_yr_fit, 0.0)
        _levy_rate = _FIT_LEVELISATION_RATE_PER_MWH.get(int(_yr_fit), 0.0)
        _levy_gbp = _fit_book.levelisation_charge_gbp(int(_yr_fit), _mwh_fit * 1000.0)
        _fit_per_year[_yr_fit] = {
            "elec_mwh": round(_mwh_fit, 1),
            "levy_rate_gbp_per_mwh": _levy_rate,
            "fit_levy_gbp": round(_levy_gbp, 2),
        }
    return {
        "total_fit_levy_gbp": round(
            sum(v["fit_levy_gbp"] for v in _fit_per_year.values()), 2
        ),
        "per_year": _fit_per_year,
    }


def _ccl_summary(
    settled_records: Sequence[Mapping],
    all_years: list[str],
    ic_elec_customer_ids: frozenset[str] | set[str],
    ic_gas_customer_ids: frozenset[str] | set[str],
) -> dict:
    """Phase OI: Climate Change Levy (CCL) -- I&C elec + gas pass-through."""
    _ccl_ledger = CCLLedger()
    _ccl_elec_by_year: dict = defaultdict(float)
    _ccl_gas_by_year: dict = defaultdict(float)
    for _rec in settled_records:
        _yr_ccl = _rec.get("settlement_date", "")[:4]
        if not _yr_ccl:
            continue
        _cid_ccl = _rec.get("customer_id", "")
        if _cid_ccl in ic_elec_customer_ids and _rec.get("commodity", "elec") != "gas":
            _ccl_elec_by_year[_yr_ccl] += _rec.get("consumption_kwh", 0.0)
        elif _cid_ccl in ic_gas_customer_ids and _rec.get("commodity") == "gas":
            _ccl_gas_by_year[_yr_ccl] += _rec.get("consumption_kwh", 0.0)
    _ccl_per_year = {}
    for _yr_ccl in all_years:
        _yr_int_ccl = int(_yr_ccl)
        _elec_kwh = _ccl_elec_by_year.get(_yr_ccl, 0.0)
        _gas_kwh = _ccl_gas_by_year.get(_yr_ccl, 0.0)
        _elec_rate = _ccl_ledger.rate_for_year(_yr_int_ccl, CCLFuel.ELECTRICITY)
        _gas_rate = _ccl_ledger.rate_for_year(_yr_int_ccl, CCLFuel.GAS)
        _elec_ccl = round(_elec_kwh * _elec_rate / 100.0, 2)
        _gas_ccl = round(_gas_kwh * _gas_rate / 100.0, 2)
        _ccl_per_year[_yr_ccl] = {
            "elec_kwh": round(_elec_kwh, 0),
            "gas_kwh": round(_gas_kwh, 0),
            "elec_rate_p_per_kwh": _elec_rate,
            "gas_rate_p_per_kwh": _gas_rate,
            "ccl_elec_gbp": _elec_ccl,
            "ccl_gas_gbp": _gas_ccl,
            "ccl_total_gbp": round(_elec_ccl + _gas_ccl, 2),
        }
    return {
        "total_ccl_gbp": round(sum(v["ccl_total_gbp"] for v in _ccl_per_year.values()), 2),
        "per_year": _ccl_per_year,
    }


def build_statutory_obligations(
    settled_records: Sequence[Mapping],
    report_years: Iterable[str],
    ic_elec_customer_ids: frozenset[str] | set[str],
    ic_gas_customer_ids: frozenset[str] | set[str],
) -> StatutoryObligations:
    """Compute the supplier's RO, FiT-levelisation and CCL positions.

    `settled_records` are the supplier's own settled billing records;
    `report_years` the four-digit years it reports on; the two id sets its own
    I&C book, elec and gas.
    """
    all_years = sorted(report_years)
    elec_mwh_by_year = _annual_elec_mwh(settled_records)

    return StatutoryObligations(
        roc_summary=_roc_summary(all_years, elec_mwh_by_year),
        fit_summary=_fit_summary(all_years, elec_mwh_by_year),
        ccl_summary=_ccl_summary(
            settled_records, all_years, ic_elec_customer_ids, ic_gas_customer_ids
        ),
    )
