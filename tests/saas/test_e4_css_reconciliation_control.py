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


# --- FAIL-OPEN killer: non-finite / missing figures must NOT pass silently -----------

def test_fail_open_nan_fires(css, data):
    m = copy.deepcopy(css)
    m["segments"][CSS_SEGMENTS[0]]["revenue_gbp"] = float("nan")
    assert _has(verify_css_reconciliation(m, data), "fail-open guard")


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
