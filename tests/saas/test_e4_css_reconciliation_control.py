"""Atom E4 (L2->L3) — R15 mutation tests for the CSS reconciliation control.

R15 (controls-that-cannot-fail): a control counts as evidence only if a MUTATION TEST
proves it FIRES on its own named defect. Here we take a valid CSS built from the live
run output, inject each named reconciliation defect, and assert
`verify_css_reconciliation` reports it — then confirm the clean structure passes. The
three killer patterns are each probed: TAUTOLOGY (an independent-path tie that cannot be
faked by construction), FAIL-OPEN (non-finite / missing figures), FAIL-SILENT (the
control is wired into render + the annual-report wrapper so a broken CSS is loud).
"""

import copy
import json
from pathlib import Path

import pytest

from saas.reporting.css_statement import (
    CSS_SEGMENTS,
    build_css,
    render_css,
    verify_css_reconciliation,
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


def _has(violations, needle):
    return any(needle in v for v in violations)


# --- baseline: the control PASSES on clean data (else every mutation test is vacuous) --

def test_clean_passes(css, data):
    assert verify_css_reconciliation(css, data) == []


# --- Control C: settlement -> billed bridge ------------------------------------------

def test_mutation_bridge_fires(css, data):
    """DEFECT: statutory billed revenue no longer ties to settlement + basis diff."""
    m = copy.deepcopy(css)
    m["reconciliation"]["statutory_billed_revenue_gbp"] += 1_000_000.0
    out = verify_css_reconciliation(m, data)
    assert _has(out, "bridge"), out
    # and clean still passes (control is not stuck-on)
    assert verify_css_reconciliation(css, data) == []


def test_mutation_bridge_basis_diff_fires(css, data):
    """DEFECT: the basis-difference reconciling item is corrupted."""
    m = copy.deepcopy(css)
    m["reconciliation"]["revenue_basis_difference_gbp"] += 500_000.0
    assert _has(verify_css_reconciliation(m, data), "bridge")


# --- Control A: per-segment waterfall reconciling to revenue < GBP1 ------------------

def test_mutation_waterfall_fires(css, data):
    """DEFECT: one segment's transportation cost is scaled so the waterfall no longer
    reconciles to that segment's revenue."""
    m = copy.deepcopy(css)
    s = CSS_SEGMENTS[0]
    m["segments"][s]["transportation_gbp"] *= 1.5
    m["segments"][s]["transportation_gbp"] += 10_000.0  # ensure > tol even if base is 0
    out = verify_css_reconciliation(m, data)
    assert _has(out, "waterfall") or _has(out, "transport+env"), out


def test_mutation_transport_env_split_fires(css, data):
    """DEFECT: transport + env no longer sums to the (exact) non-commodity total."""
    m = copy.deepcopy(css)
    s = CSS_SEGMENTS[0]
    m["segments"][s]["environmental_gbp"] += 25_000.0
    assert _has(verify_css_reconciliation(m, data), "transport+env") or \
        _has(verify_css_reconciliation(m, data), "waterfall")


# --- Control B: per-segment sums == aggregate (persisted-artifact integrity) ---------

def test_mutation_aggregate_sum_fires(css, data):
    """DEFECT: one segment's stored revenue diverges from the aggregate that summed it."""
    m = copy.deepcopy(css)
    m["segments"][CSS_SEGMENTS[0]]["revenue_gbp"] += 750_000.0
    out = verify_css_reconciliation(m, data)
    assert _has(out, "aggregate 'revenue_gbp'"), out


def test_mutation_aggregate_other_direct_fires(css, data):
    """DEFECT (was FAIL-OPEN, 2026-07-27 red-team): the aggregate `other_direct_gbp` is a
    RENDERED audited line ('Other direct costs (capital/collateral charges)') and part of
    the aggregate column's own waterfall, yet was ABSENT from Control B's aggregate tie —
    and Control A checks only the per-segment waterfall, never the aggregate column's. A
    post-construction transform/serialisation corruption of the aggregate figure therefore
    rendered a broken audited line AND a non-reconciling aggregate waterfall while every
    control stayed silent. Must now fire the aggregate==sum-of-segments tie."""
    m = copy.deepcopy(css)
    seg_sum = sum(m["segments"][s]["other_direct_gbp"] for s in CSS_SEGMENTS)
    m["aggregate"]["other_direct_gbp"] = seg_sum + 5_000_000.0
    out = verify_css_reconciliation(m, data)
    assert _has(out, "aggregate 'other_direct_gbp'"), out
    # clean still passes (control is not stuck-on)
    assert verify_css_reconciliation(css, data) == []


def test_mutation_aggregate_non_commodity_fires(css, data):
    """DEFECT (was FAIL-OPEN, same class): the aggregate `non_commodity_gbp` feeds the
    settlement→statutory reconciliation table (`css_settlement_non_commodity_gbp`) yet was
    also absent from Control B's tie — a corrupted aggregate figure passed silently."""
    m = copy.deepcopy(css)
    m["aggregate"]["non_commodity_gbp"] += 5_000_000.0
    out = verify_css_reconciliation(m, data)
    assert _has(out, "aggregate 'non_commodity_gbp'"), out


# --- Control B': INDEPENDENT tie (escapes the aggregate==sum tautology) --------------

def test_mutation_independent_topline_fires(data, css):
    """DEFECT: a segment_split key fails to classify and is silently dropped, so the
    aggregate (summed from classified buckets) no longer ties to the top-line settlement
    revenue (a DIFFERENT data path: years[*].revenue_gbp). This is the genuinely
    non-tautological reconciliation — it cannot be satisfied by construction."""
    md = copy.deepcopy(data)
    moved = 0.0
    for yd in md.get("years", {}).values():
        ss = yd.get("segment_split") or {}
        if "resi electricity" in ss:
            moved += ss["resi electricity"].get("revenue_gbp", 0.0)
            ss["resi zzunknownfuel"] = ss.pop("resi electricity")  # unclassifiable commodity
    assert moved > 0, "fixture precondition: expected a classified 'resi electricity' key"
    m = build_css(md)
    out = verify_css_reconciliation(m, md)
    assert _has(out, "independent tie"), out


def test_independent_tie_not_tautological(css, data):
    """A pure tautology (aggregate defined as the sum) could never distinguish the two
    sides. Prove independence: the top-line source and the aggregate come from different
    fields, so a top-line-only perturbation is DETECTED even though every segment bucket
    is internally consistent."""
    md = copy.deepcopy(data)
    # perturb ONLY the top-line year revenue, leaving segment buckets untouched
    first_year = next(iter(md["years"]))
    md["years"][first_year]["revenue_gbp"] += 2_000_000.0
    out = verify_css_reconciliation(css, md)
    assert _has(out, "independent tie"), out


def test_fail_open_nan_topline_year_revenue_fires(css, data):
    """DEFECT (R15 killer pattern 2, NaN-blind comparison on Control B''s independent leg):
    a non-finite years[*].revenue_gbp makes `topline` NaN, so `abs(agg - NaN) > tol`
    evaluates silently False and the ONE genuinely-independent tie is disabled while every
    finite segment/aggregate figure stays clean — so NO other control fires. This is a
    DIFFERENT data path (the top-line source) from Control B's segment values guarded on
    2026-07-25/07-27. The finite guard must fire on it, not pass silently."""
    md = copy.deepcopy(data)
    y0 = next(iter(md["years"]))
    md["years"][y0]["revenue_gbp"] = float("nan")
    m = build_css(md)
    # sanity: the corruption leaves aggregate + all segments finite (so ONLY the guard catches it)
    assert all(
        isinstance(m["segments"][s]["revenue_gbp"], float)
        and m["segments"][s]["revenue_gbp"] == m["segments"][s]["revenue_gbp"]
        for s in CSS_SEGMENTS
    )
    out = verify_css_reconciliation(m, md)
    assert _has(out, "independent tie: fail-open guard"), out


# --- FAIL-OPEN killer: non-finite / missing figures must NOT pass silently -----------

def test_fail_open_nan_fires(css, data):
    m = copy.deepcopy(css)
    m["segments"][CSS_SEGMENTS[0]]["revenue_gbp"] = float("nan")
    assert _has(verify_css_reconciliation(m, data), "fail-open guard")


def test_fail_open_nan_volume_fires(css, data):
    """DEFECT (was FAIL-OPEN): a non-finite `volume_mwh` in a segment, with the
    aggregate left finite (a serialisation/transform bug on the persisted artifact),
    previously escaped every check — Control B's only guard was on the aggregate, and
    a NaN seg_sum makes `abs(finite - NaN) > tol` evaluate silently False. volume_mwh
    is absent from the _MONEY_KEYS guard, so the control returned clean while the
    rendered WACOE line would show 'nan'. Must now fire the fail-open guard."""
    m = copy.deepcopy(css)
    m["segments"][CSS_SEGMENTS[0]]["volume_mwh"] = float("nan")
    out = verify_css_reconciliation(m, data)
    assert _has(out, "fail-open guard"), out
    assert _has(out, "volume_mwh"), out
    # clean still passes (control is not stuck-on)
    assert verify_css_reconciliation(css, data) == []


def test_fail_open_nan_gross_margin_fires(css, data):
    """DEFECT (was FAIL-OPEN): same class for `gross_margin_gbp` — a headline rendered
    row referenced only by Control B, not by the _MONEY_KEYS guard nor the waterfall."""
    m = copy.deepcopy(css)
    m["segments"][CSS_SEGMENTS[0]]["gross_margin_gbp"] = float("nan")
    out = verify_css_reconciliation(m, data)
    assert _has(out, "fail-open guard"), out
    assert _has(out, "gross_margin_gbp"), out


def test_fail_open_none_bridge_fires(css, data):
    m = copy.deepcopy(css)
    m["reconciliation"]["statutory_billed_revenue_gbp"] = None
    assert _has(verify_css_reconciliation(m, data), "fail-open guard")


def test_fail_open_missing_segment_fires(css, data):
    m = copy.deepcopy(css)
    del m["segments"][CSS_SEGMENTS[0]]
    assert _has(verify_css_reconciliation(m, data), "missing segment")


# --- FAIL-SILENT killer: unavailable/malformed structure fails CLOSED ----------------

def test_fail_silent_none_structure_fails_closed():
    assert verify_css_reconciliation(None) != []
    assert verify_css_reconciliation({}) != []
    assert verify_css_reconciliation({"segments": {}}) != []


# --- FAIL-SILENT wiring: a broken CSS is LOUD in the render, not swallowed -----------

def test_render_shows_loud_banner_on_violation(data):
    """render_css must embed the loud reconciliation banner when the control fires,
    rather than emitting a clean-looking statement."""
    md = copy.deepcopy(data)
    for yd in md.get("years", {}).values():
        ss = yd.get("segment_split") or {}
        if "resi electricity" in ss:
            ss["resi zzunknownfuel"] = ss.pop("resi electricity")
    out = render_css(md)
    assert "CSS RECONCILIATION CONTROL FIRED" in out


def test_render_clean_has_no_banner(data):
    out = render_css(data)
    assert "CSS RECONCILIATION CONTROL FIRED" not in out
    # sanity: the statement still renders its core lines
    assert "Consolidated Segmental Statement" in out


def test_annual_report_wrapper_surfaces_errors_loudly(monkeypatch):
    """The annual-report wrapper must surface an unexpected render error loudly, not
    swallow the whole CSS backbone to '' (the FAIL-SILENT hole)."""
    import saas.reporting.annual_report as ar
    import saas.reporting.css_statement as cs

    def _boom(_data):
        raise RuntimeError("synthetic render failure")

    monkeypatch.setattr(cs, "render_css", _boom)
    out = ar._section_consolidated_segmental_statement({})
    assert "CSS SECTION ERROR" in out
    assert out != ""


# --- FAIL-SILENT sibling: the board KPI block must fail the SAME way as the CSS half --

def test_board_kpi_wrapper_surfaces_errors_loudly(monkeypatch):
    """SIBLING-HALF DEFECT (was FAIL-SILENT): _section_board_kpi_block previously
    swallowed ANY exception to '', so a malformed data structure could vanish the entire
    board KPI block from the annual report with no trace — while its already-hardened
    sibling (_section_consolidated_segmental_statement) stayed loud. The two halves of
    atom E4 must fail identically. Assert the board block now surfaces the error loudly."""
    import saas.reporting.annual_report as ar
    import saas.reporting.css_statement as cs

    def _boom(_data):
        raise RuntimeError("synthetic kpi failure")

    monkeypatch.setattr(cs, "render_board_kpis", _boom)
    out = ar._section_board_kpi_block({})
    assert "BOARD KPI SECTION ERROR" in out
    assert out != ""


def test_board_kpi_wrapper_stays_silent_on_no_book():
    """The legitimate silent case (no years / pre-segment fixture) must STAY silent —
    the loud banner fires only on an UNEXPECTED error, not on a clean empty render."""
    import saas.reporting.annual_report as ar
    assert ar._section_board_kpi_block({}) == ""
    assert "BOARD KPI SECTION ERROR" not in ar._section_board_kpi_block({})
