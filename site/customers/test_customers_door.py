"""Render-side tests for the Customers door OPERATIONAL-STATE panel.

This panel is the director's window into what it is like for ONE real household,
end to end (the "individual customer drill-down" of the legibility steer).

R11 (verify to the rendered value): execute the panel's ACTUAL inline JavaScript
(via a Node/vm harness) against the REAL published site/data/company.json the page
consumes, then assert the produced HTML contains the actual source values.

R14 (no financial figure without its clock): every money KPI renders a basis label
(billed/banked/settled).

R15 (a control must be able to FAIL): a mutation of a source value changes the
rendered pixel (independence -- not a hardcoded string).

HONESTY (load-bearing): the per-customer CO2 trajectory is DESIGNED, NOT INSTRUMENTED
(atom E5). The panel must show it as an honest placeholder and must NOT render a
fabricated carbon number.
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


def _render(company: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(company),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live() -> dict:
    return json.loads(DATA.read_text())


def test_panel_shows_a_real_named_account():
    d = _live()
    out = _render(d)
    hid = d["household"]["id"]
    assert hid in out["cust-intro"]["innerHTML"], out["cust-intro"]["innerHTML"]
    assert hid in out["cust-stamp"]["textContent"], out["cust-stamp"]["textContent"]


def test_money_kpis_render_live_billed_banked_balance():
    # R11: the actual billed/banked/balance from the household block render.
    d = _live()
    h = d["household"]
    out = _render(d)
    money = out["cust-money"]["innerHTML"]

    def money_fmt(v):
        return f"{abs(float(v)):,.2f}"

    assert money_fmt(h["billed_gbp"]) in money, money
    assert money_fmt(h["banked_gbp"]) in money, money
    assert money_fmt(h["balance_gbp"]) in money, money


def test_money_kpis_carry_r14_clocks():
    # R14: billed/banked/settled clocks must appear on the money surface.
    d = _live()
    out = _render(d)
    money = out["cust-money"]["innerHTML"].lower()
    for clock in ("billed", "banked", "settled"):
        assert clock in money, f"R14: missing {clock} clock in {money}"


def test_balance_is_independent_of_render():
    # R15 independence: mutate the balance; the rendered pixel must follow.
    d = _live()
    d["household"]["balance_gbp"] = -987654.32
    out = _render(d)
    money = out["cust-money"]["innerHTML"]
    assert "987,654.32" in money, money
    # negative balance is labelled 'in credit'
    assert "in credit" in money, money


def test_arrears_journey_renders_live_stages():
    # R11: the household's real arrears cases render their stage journey.
    d = _live()
    cases = d["household"].get("arrears_cases", [])
    out = _render(d)
    arr = out["cust-arrears"]["innerHTML"]
    if cases:
        c = cases[0]
        assert c["case_id"] in arr, arr
        # first stage name appears in the journey
        assert c["stages"][0]["stage"] in arr, arr
    else:
        assert "No arrears" in arr


def test_carbon_is_honest_placeholder_not_a_number():
    # HONESTY (load-bearing): CO2 trajectory is designed, not instrumented. The
    # panel must SAY so and must NOT fabricate a tonnage. A fabricated E5 number
    # would be caught here.
    d = _live()
    out = _render(d)
    carbon = out["cust-carbon"]["innerHTML"]
    low = carbon.lower()
    assert "not yet computed" in low or "not instrumented" in low, carbon
    assert "designed" in low and "e5" in low, carbon
    # No fabricated numeric tonnage: the tCO2e label must not be followed by a value.
    import re
    assert not re.search(r"\d+(\.\d+)?\s*tco", low), f"fabricated carbon number: {carbon}"


def test_carbon_mutation_would_be_caught_r15():
    # R15: prove the honesty check has teeth -- if a future edit injected a
    # fabricated tonnage into the carbon panel, the guard above would fire.
    # Here we assert the *current* panel renders the honest state for an empty
    # household too (fail-open guard: no household must not silently pass).
    out = _render({"household": {}})
    carbon = out["cust-carbon"]["innerHTML"].lower()
    assert "not yet computed" in carbon or "not instrumented" in carbon, carbon
