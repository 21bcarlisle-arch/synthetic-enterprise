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
