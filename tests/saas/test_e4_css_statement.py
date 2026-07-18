"""Atom E4 — Consolidated Segmental Statement (CSS) invariants.

Tests the CSS builder against the live extracted run output. The binding property:
every figure reconciles (no hand-typed numbers), and honest gaps are labelled, not
fabricated.
"""

import json
from pathlib import Path

import pytest

from saas.reporting.css_statement import (
    CSS_SEGMENTS,
    build_css,
    build_board_kpis,
    render_css,
    render_board_kpis,
)

_RUN_OUTPUT = Path("docs/reports/run_output_latest.json")


@pytest.fixture(scope="module")
def data() -> dict:
    if not _RUN_OUTPUT.exists():
        pytest.skip("run_output_latest.json not present")
    return json.loads(_RUN_OUTPUT.read_text())


@pytest.fixture(scope="module")
def css(data) -> dict:
    c = build_css(data)
    if c is None:
        pytest.skip("run output lacks per-segment settlement data")
    return c


def test_four_segments_present(css):
    assert set(css["segments"].keys()) == set(CSS_SEGMENTS)


def test_per_segment_waterfall_reconciles(css):
    """Revenue = fuel + transportation + environmental + other-direct + contribution."""
    for s in CSS_SEGMENTS:
        x = css["segments"][s]
        waterfall = (
            x["fuel_gbp"] + x["transportation_gbp"] + x["environmental_gbp"]
            + x["other_direct_gbp"] + x["contribution_gbp"]
        )
        assert abs(waterfall - x["revenue_gbp"]) < 1.0, s


def test_transport_plus_env_equals_non_commodity(css):
    for s in CSS_SEGMENTS:
        x = css["segments"][s]
        assert abs(x["transportation_gbp"] + x["environmental_gbp"] - x["non_commodity_gbp"]) < 1.0, s


def test_aggregate_is_sum_of_segments(css):
    for key in ("revenue_gbp", "fuel_gbp", "gross_margin_gbp", "contribution_gbp",
                "transportation_gbp", "environmental_gbp", "volume_mwh"):
        seg_sum = sum(css["segments"][s][key] for s in CSS_SEGMENTS)
        assert abs(css["aggregate"][key] - seg_sum) < 1.0, key


def test_reconciliation_bridges_settlement_to_statutory(css):
    """CSS settlement revenue + basis difference == statutory billed revenue."""
    rec = css["reconciliation"]
    bridged = rec["css_settlement_revenue_gbp"] + rec["revenue_basis_difference_gbp"]
    assert abs(bridged - rec["statutory_billed_revenue_gbp"]) < 1.0


def test_wacoe_equals_fuel_over_volume(css):
    for s in CSS_SEGMENTS:
        x = css["segments"][s]
        if x["volume_mwh"] > 0 and x["wacoe_gbp_per_mwh"] is not None:
            assert abs(x["wacoe_gbp_per_mwh"] - x["fuel_gbp"] / x["volume_mwh"]) < 1e-6, s


def test_gas_has_wacog_electricity_does_not(css):
    assert css["segments"]["Gas — Domestic"]["wacog_p_per_th"] is not None
    assert css["segments"]["Electricity — Domestic"]["wacog_p_per_th"] is None


def test_honest_gaps_labelled_not_fabricated(data):
    md = render_css(data)
    # D&A is a named gap, not a fabricated number
    assert "honest gap" in md.lower()
    assert "Depreciation & amortisation" in md
    # per-segment indirect allocation is a named gap
    assert "named gap" in md.lower()


def test_r14_basis_labels_present(data):
    md = render_css(data)
    for token in ("settlement basis", "billed", "banked", "settled"):
        assert token in md.lower(), token


def test_render_contains_all_css_lines(data):
    md = render_css(data)
    for line in ("Revenue from sale of energy", "Direct fuel costs", "Gross margin",
                 "Transportation", "Environmental & social", "EBITDA", "EBIT",
                 "Reconciliation", "Hedging policy note", "WACOE"):
        assert line in md, line


def test_board_kpis_present(data):
    k = build_board_kpis(data)
    assert k is not None
    md = render_board_kpis(data)
    for token in ("Churn %", "Complaints per 1,000", "ARPU by segment",
                  "Direct Debit share", "Estimated-read rate", "awaiting market backdrop".title()):
        assert token in md or token.lower() in md.lower(), token


def test_arpu_by_segment_uses_real_meter_points(data, css):
    k = build_board_kpis(data)
    for s in CSS_SEGMENTS:
        mp = css["segments"][s]["meter_points"]
        rev = css["segments"][s]["revenue_gbp"]
        if mp > 0:
            expected = rev / mp / k["n_years"]
            assert abs(k["arpu"][s] - expected) < 1e-6, s


def test_silent_on_empty_data():
    assert build_css({}) is None
    assert render_css({}) == ""
    assert build_board_kpis({}) is None
    assert render_board_kpis({}) == ""
