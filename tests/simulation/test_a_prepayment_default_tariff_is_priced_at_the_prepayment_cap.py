"""A prepayment household's default tariff never exceeds its own payment method's cap (SLC 28AD).

Every SVT segment was priced at the published level, which is the direct-debit column. On the
67a893e749 book that put 496 electricity and 462 gas prepayment term-windows over the prepayment cap
(`SEAT_FINDING_THE_BLIND_INVARIANT_SUITE_ON_THE_67A893E749_BOOK_...`, breach class 1). The cap
column read here is the commons' own (`ofgem_cap_unit_rate_composition.json`), not the code's.
"""

from __future__ import annotations

import ast
import json
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPOSITION = json.loads((ROOT / "docs/domain_artefact_library/regulatory/"
                          "ofgem_cap_unit_rate_composition.json").read_text())
SERIES = {"electricity": "by_payment_method", "gas": "gas_by_payment_method"}


def _capped_periods(fuel: str, method: str):
    return [p for p in COMPOSITION[SERIES[fuel]][method]["periods"] if p["cap_in_force"]]


def _dd_segment(fuel: str, start: str) -> dict:
    """A segment as `build_svt_schedule` writes its rate legs: the published level, ex-VAT."""
    from simulation import svt_product

    cap_of, charged_of = svt_product._RATE_LEGS_BY_FUEL[fuel]
    d = date.fromisoformat(start)
    rate, charged = svt_product._ex_vat(cap_of(start)), svt_product._ex_vat(charged_of(start))
    from simulation.price_cap_enforcement import hmt_epg_receipt_gbp_per_mwh

    return {"acquisition_date": start, "unit_rate_gbp_per_mwh": rate,
            "household_charged_unit_rate_gbp_per_mwh": charged,
            "hmt_epg_receipt_gbp_per_mwh": svt_product._ex_vat(hmt_epg_receipt_gbp_per_mwh(fuel, d)),
            "tariff_type": "svt"}


@pytest.mark.parametrize("fuel", ["electricity", "gas"])
def test_a_prepayment_svt_rate_never_exceeds_the_windows_prepayment_cap(fuel):
    from simulation.svt_product import price_segment_for_payment_method

    over = []
    for p in _capped_periods(fuel, "prepayment"):
        seg = price_segment_for_payment_method(
            _dd_segment(fuel, p["starts"]), fuel=fuel, method_held="prepayment")
        p_per_kwh = seg["unit_rate_gbp_per_mwh"] / 10.0
        if p_per_kwh > p["unit_rate_p_per_kwh_ex_vat"] * (1 + 1e-9):
            over.append((p["starts"], round(p_per_kwh, 3), p["unit_rate_p_per_kwh_ex_vat"]))
        assert seg["unit_rate_gbp_per_mwh"] == pytest.approx(
            seg["household_charged_unit_rate_gbp_per_mwh"] + seg["hmt_epg_receipt_gbp_per_mwh"])
    assert not over, f"{fuel} prepayment SVT above its own cap column (start, rate, cap): {over}"


@pytest.mark.parametrize("fuel", ["electricity", "gas"])
def test_the_method_column_both_moves_a_rate_and_leaves_one_standing(fuel):
    """The partition, so a reader that moved nothing or moved everything cannot pass: prepayment is
    re-priced in some window, left at the DD level in some window, and never raised above it."""
    from simulation.svt_product import price_segment_for_payment_method

    lowered = kept = 0
    for p in _capped_periods(fuel, "prepayment"):
        dd = _dd_segment(fuel, p["starts"])
        ppm = price_segment_for_payment_method(dict(dd), fuel=fuel, method_held="prepayment")
        assert ppm["unit_rate_gbp_per_mwh"] <= dd["unit_rate_gbp_per_mwh"] + 1e-9
        if ppm["unit_rate_gbp_per_mwh"] < dd["unit_rate_gbp_per_mwh"] - 1e-9:
            lowered += 1
        else:
            kept += 1
    assert lowered and kept, (lowered, kept)


@pytest.mark.parametrize("method", ["direct_debit", "standard_credit", None])
def test_direct_debit_and_standard_credit_segments_are_left_as_built(method):
    from simulation.svt_product import price_segment_for_payment_method

    for fuel in SERIES:
        for p in _capped_periods(fuel, "direct_debit"):
            seg = _dd_segment(fuel, p["starts"])
            assert price_segment_for_payment_method(
                dict(seg), fuel=fuel, method_held=method) == seg


def test_an_unknown_payment_method_is_refused_by_name():
    from simulation.svt_product import price_segment_for_payment_method

    with pytest.raises(ValueError, match="no cap column"):
        price_segment_for_payment_method(
            _dd_segment("electricity", "2021-04-01"), fuel="electricity", method_held="cheque")


def test_the_epg_receipt_on_a_prepayment_bill_is_its_own_cap_less_the_epg():
    """Jan 2023 electricity: the household pays the EPG either way; the Treasury pays the
    prepayment cap's gap, not the DD cap's."""
    from simulation.svt_product import _ex_vat, stamp_hmt_epg_receipt

    ppm_col = next(p for p in _capped_periods("electricity", "prepayment")
                   if p["starts"] == "2023-01-01")["unit_rate_p_per_kwh_ex_vat"] * 10.0
    epg_ex = _ex_vat(340.0)
    rec = stamp_hmt_epg_receipt([{"settlement_date": "2023-01-15T00:00", "consumption_kwh": 1000.0}],
                                fuel="electricity", method_held="prepayment")[0]
    assert rec["hmt_epg_receipt_gbp_per_mwh"] == pytest.approx(ppm_col - epg_ex)
    dd = stamp_hmt_epg_receipt([{"settlement_date": "2023-01-15T00:00", "consumption_kwh": 1000.0}],
                               fuel="electricity")[0]
    assert dd["hmt_epg_receipt_gbp_per_mwh"] > rec["hmt_epg_receipt_gbp_per_mwh"]


def test_the_run_loop_prices_each_svt_segment_at_the_method_the_company_holds():
    """Wiring: the term loop hands every domestic SVT segment to the re-pricer with the method read
    from the company's register, and the EPG stamp with the same method. Delete either call and
    the decade run bills prepayment at the DD cap again with every unit test above still green."""
    tree = ast.parse((ROOT / "simulation/run_phase2b.py").read_text())
    calls = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            kws = {k.arg: k.value for k in node.keywords}
            calls.setdefault(node.func.id, []).append(kws)
    priced = calls.get("price_segment_for_payment_method", [])
    assert any(isinstance(k.get("method_held"), ast.Name)
               and k["method_held"].id == "_svt_priced_method" for k in priced), priced
    stamped = calls.get("stamp_hmt_epg_receipt", [])
    assert stamped and all(isinstance(k.get("method_held"), ast.Name)
                           and k["method_held"].id == "_svt_priced_method" for k in stamped)
    resolved = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "_svt_priced_method" for t in n.targets)
                and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)
                and n.value.func.attr == "get_payment_method"]
    assert resolved, "_svt_priced_method is not read from the company's method register"
