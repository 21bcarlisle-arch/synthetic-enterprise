"""Render-side tests for the Company door (site/company/index.html).

R11 (verify to the rendered value): execute the page's ACTUAL inline JavaScript
(via a Node/vm harness) against the REAL published site/data/company.json the page
consumes, then assert the produced HTML contains the actual source values.

R14 (no financial figure without its clock): every financial KPI must render a
basis label (settled/billed/banked).

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "company.json"
CAPS = HERE.parent / "data" / "capabilities.json"
COV = HERE.parent / "data" / "saas_coverage.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live() -> dict:
    return json.loads(DATA.read_text())


def _caps() -> dict:
    return json.loads(CAPS.read_text())


def test_finance_kpis_carry_basis_label_r14():
    out = _render(_live())
    kpis = out["finance-kpis"]["innerHTML"]
    # R14: a financial figure without its clock is a defect. The net-margin KPI
    # must render a settled/billed/banked basis label.
    assert any(b in kpis.lower() for b in ("settled", "billed", "banked")), kpis


def test_trading_hedge_fraction_renders_live_value():
    d = _live()
    out = _render(d)
    kpis = out["trading-kpis"]["innerHTML"]
    hf = d["trading_risk"]["latest_avg_hf"]
    pct = f"{hf * 100:.1f}%"
    assert pct in kpis, f"expected {pct} in {kpis}"


def test_obligations_count_renders_live():
    d = _live()
    out = _render(d)
    kpis = out["oblig-kpis"]["innerHTML"]
    count = d["compliance"]["obligations_register"]["count"]
    assert f">{count}<" in kpis, kpis


def test_household_is_a_real_named_account():
    d = _live()
    out = _render(d)
    intro = out["hh-intro"]["innerHTML"]
    acct = d["household"]["id"]
    assert acct in intro, f"account {acct} not rendered in {intro}"


def test_settled_net_margin_is_independent_of_render():
    # R15 independence: mutate the settled net margin; the rendered pixel must follow.
    d = _live()
    d["finance"]["settled_net_margin_gbp"] = 42424242.0
    out = _render(d)
    body = out["finance-kpis"]["innerHTML"] + out["bridge-body"]["innerHTML"]
    assert "42" in body and ("42.4" in body or "42,424" in body or "42.42" in body), body


# --- RC6 (DIRECTOR §C, 2026-07-23): financials are unit economics, never bare totals ---


def test_finance_states_book_size_N_and_draw_rc6():
    # The finance panel must state N (the drawn sample) and the draw, and lead with a
    # per-customer figure -- the director does not accept "totals from a random sample".
    d = _live()
    n = d["stress_bands"]["total"]
    out = _render(d)
    intro = out["finance-intro"]["innerHTML"]
    kpis = out["finance-kpis"]["innerHTML"]
    assert f"N={n}" in intro, intro
    assert "drawn sample" in intro.lower(), intro
    assert "Net margin / customer" in kpis, kpis
    note = out["finance-unit-note"]["innerHTML"]
    assert f"N={n}" in note and "not meaningful in isolation" in note, note


def test_finance_totals_marked_scales_with_book_rc6():
    # Every cumulative total must carry the "scales with drawn book" caveat.
    out = _render(_live())
    kpis = out["finance-kpis"]["innerHTML"]
    assert "scales with drawn book" in kpis, kpis


def test_finance_per_customer_follows_book_size_rc6():
    # R15 (a control must be able to FAIL): the £/customer figure and its stated
    # denominator must follow N. Mutate the sample size; both the denominator label
    # and the rendered value must change -- a hardcoded ratio would fail this.
    d = _live()
    d["finance"]["latest_year_net_margin_gbp"] = 700000.0
    d["stress_bands"]["total"] = 7
    out = _render(d)
    kpis = out["finance-kpis"]["innerHTML"]
    assert "÷ 7 sampled customers" in kpis, kpis
    assert "100,000.00" in kpis, kpis  # 700000 / 7, denominator-stated
    # And a different N moves the value (independence, not a constant):
    d["stress_bands"]["total"] = 14
    out2 = _render(d)
    assert "50,000.00" in out2["finance-kpis"]["innerHTML"], out2["finance-kpis"]["innerHTML"]


def test_cost_to_serve_rendered_as_distribution_not_total_rc6_r11():
    # RC6 §C (DIRECTOR 2026-07-23): cost-to-serve is a DISTRIBUTION, never a bare
    # total. R11 (verify to the rendered value): the live per-customer min/median/max
    # from company.json.cost_to_serve must appear in the rendered pixel, framed as a
    # spread, with N and the segment split -- not a single headline number.
    d = _live()
    cts = d.get("cost_to_serve")
    if not (cts and cts.get("available")):
        # R2: the running auto-processor may still be on the pre-cost_to_serve
        # generator and regenerate company.json without the field until it restarts.
        # Don't wedge the publish gate on that transient -- the always-on R15
        # guarantee lives in tools/test_generate_company_data.py (tests the function).
        pytest.skip("cost_to_serve not in live company.json yet (pre-deploy / old generator process)")
    out = _render(d)
    html = out["cost-to-serve-dist"]["innerHTML"]
    assert "distribution, not the total" in html, html
    assert f"N={cts['n']}" in html, html
    # The actual live min/median/max render (comma-grouped £ to 2dp):
    for key in ("min_gbp", "median_gbp", "max_gbp"):
        shown = f"{cts[key]:,.2f}"
        assert shown in html, (key, shown, html)
    # Coverage-cell distribution: every segment's median renders.
    for seg in cts["by_segment"]:
        assert seg["segment"] in html and f"{seg['median_gbp']:,.2f}" in html, (seg, html)


def test_cost_to_serve_distribution_follows_source_r15():
    # R15 (a control must be able to FAIL): the rendered spread must FOLLOW the
    # source values -- a hardcoded/baked figure would fail this. Mutate the median
    # and max in the source; the rendered pixel must move.
    d = _live()
    if not (d.get("cost_to_serve") or {}).get("available"):
        pytest.skip("cost_to_serve not in live company.json yet (pre-deploy / old generator process)")
    d["cost_to_serve"]["median_gbp"] = 1234.56
    d["cost_to_serve"]["max_gbp"] = 98765.43
    out = _render(d)
    html = out["cost-to-serve-dist"]["innerHTML"]
    assert "1,234.56" in html and "98,765.43" in html, html


def test_cost_to_serve_fail_closed_when_unavailable_r15():
    # FAIL-CLOSED: an unavailable distribution must NOT render a silently-zero total
    # as if it were a real figure -- it must say so.
    d = _live()
    d["cost_to_serve"] = {"available": False, "n": 0}
    out = _render(d)
    html = out["cost-to-serve-dist"]["innerHTML"]
    assert "unavailable" in html.lower(), html
    assert "distribution, not the total" not in html, html


# --- SURFACE-3 single job: the SaaS shown as PRODUCT (SITE_V5, ruling 2026-07-23) ---


def test_capability_headline_renders_live_run_value():
    # R11: a real capability headline from the latest run must appear as a rendered
    # pixel in the capability grid (render-not-author).
    caps = _caps()
    hedge = next(c for c in caps["cards"] if c["id"] == "risk-hedging")
    out = _render(_live())
    grid = out["cap-grid"]["innerHTML"]
    assert hedge["headline"] in grid, f"expected {hedge['headline']!r} in capability grid"
    # a null-headline capability degrades to an honest PLANNED label, never a faked figure.
    assert "not yet measured" in grid.lower(), "carbon (null headline) must render honestly, not fabricated"


def test_capability_grid_is_independent_of_render_r15():
    # R15 independence: inject a mutated capabilities payload; the pixel must follow.
    sentinel = "SENTINEL-9931 units shipped"
    payload = {
        "company": _live(),
        "capabilities": {"generated_at": "test", "cards": [
            {"id": "x", "name": "Sentinel Capability", "description": "d",
             "evidence_link": "../world/", "headline": sentinel}]},
    }
    out = _render(payload)
    assert sentinel in out["cap-grid"]["innerHTML"], "mutated headline did not reach the pixel"


def test_coverage_maps_real_market_vendors():
    # The 'shown as product' framing: the coverage map names the real vendors the
    # one product stands in for.
    out = _render(_live())
    body = out["cov-body"]["innerHTML"]
    assert "Kraken" in body or "Gentrack" in body, body
    assert "Brady" in body or "NetSuite" in body, body


def test_decisions_are_a_plain_english_layer_not_raw_log_rc1():
    # RC1 (DIRECTOR_AXIS1 verdict 2026-07-23): internal registers/logs are SOURCES,
    # never surfaces. The governance panel must render a plain-English presentation
    # layer with a drill-down link, NOT dump the raw decision-log "what"/"why" text.
    d = json.loads(DATA.read_text())
    out = _render(d)
    panel = out["state-decisions"]["innerHTML"]
    # a drill-down to the raw artefact is present...
    assert "decisions.json" in panel, "missing drill-down to the raw decision log"
    # ...and the raw internal decision-log entries are NOT dumped onto the surface.
    decs = json.loads((HERE.parent / "data" / "decisions.json").read_text()).get("decisions", [])
    raw_texts = [x.get("what", "") for x in decs if len(x.get("what", "")) > 25]
    for t in raw_texts:
        assert t not in panel, f"raw decision-log exhaust leaked onto the surface: {t[:40]!r}"


def test_never_surfaces_an_effort_metric():
    # The single job forbids effort metrics on this surface. saas_coverage.json
    # carries a test_count (18504) for internal use; it must NOT reach the product
    # surface (capability grid or coverage map).
    out = _render(_live())
    surface = (out["cap-grid"]["innerHTML"] + out["cap-passport"]["innerHTML"]
               + out["cov-body"]["innerHTML"] + out["cov-kpis"]["innerHTML"]
               + out["cov-passport"]["innerHTML"] + out["cov-intro"]["innerHTML"])
    for effort in ("18504", "18,504", "tests collected", "commits/day"):
        assert effort not in surface, f"effort metric {effort!r} leaked onto the product surface"
