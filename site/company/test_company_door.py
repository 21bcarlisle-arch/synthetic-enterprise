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
