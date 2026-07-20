"""Render-side tests for the Now door (site/now/index.html) -- the operational window.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/*.json the
page consumes (company.json + weather.json + market.json + decisions.json), then
assert the produced HTML contains the actual source values -- the rendered pixel,
not the source string.

R14 (no financial figure without its clock): every money metric asserts its clock
label (settled / billed / banked) is on the rendered surface.

R15 (a control must be able to FAIL): mutating a source value (price, temp, balance,
net position, settlement frontier) must move the rendered pixel -- proving the render
is data-driven, not a baked constant. The carbon panel gets the INVERSE mutation:
injecting a bogus per-account carbon number must NOT surface a tCO2e figure -- the
honest "designed, not instrumented" placeholder never fabricates a number.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
COMPANY = HERE.parent / "data" / "company.json"
WEATHER = HERE.parent / "data" / "weather.json"
MARKET = HERE.parent / "data" / "market.json"
DECISIONS = HERE.parent / "data" / "decisions.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(company: dict, weather_path: Path, market_path: Path, decisions_path: Path) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX), str(weather_path), str(market_path), str(decisions_path)],
        input=json.dumps(company),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live_company() -> dict:
    return json.loads(COMPANY.read_text())


def _live_weather() -> dict:
    return json.loads(WEATHER.read_text())


def _live_market() -> dict:
    return json.loads(MARKET.read_text())


def _live_decisions() -> dict:
    return json.loads(DECISIONS.read_text())


def _render_live(company: dict | None = None) -> dict:
    return _render(company or _live_company(), WEATHER, MARKET, DECISIONS)


def _write(tmp_path, name: str, obj: dict) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(obj))
    return p


# --- Deterministic market fixture (the live price_feed can degrade to gas-only in a
#     worktree lacking the gitignored SSP cache, so pin the intra-day session here;
#     shape verified against tools/generate_market_data.py's real 48-HH emission). ---
def _market_fixture() -> dict:
    return {
        "available": True,
        "settlement_frontier": "2025-06-07T22:30:00Z",
        "evidence_url": "../data/market.json",
        "electricity": {
            "unit": "£/MWh",
            "as_of_period": "2025-06-07T22:30:00Z",
            "point_count": 48,
            "latest_price": 100.58,
            "session_high": 144.8,
            "session_low": 66.76,
            "session_mean": 105.94,
            "session_range": 78.04,
            "last_change_gbp": -9.37,
            "last_change_pct": -8.52,
            "trajectory": [{"period": f"2025-06-07T{h:02d}:00:00Z", "price": 100.0 + h} for h in range(6)],
        },
    }


# =========================== PANEL 1: WORLD ===========================

def test_panel1_renders_live_weather_and_market(tmp_path):
    c = _live_company()
    w = _live_weather()
    mk = _market_fixture()
    latest = w["monthly"][-1]
    e = mk["electricity"]
    out = _render(c, WEATHER, _write(tmp_path, "market.json", mk), DECISIONS)
    metrics = out["p1-metrics"]["innerHTML"]
    assert f"{latest['mean_temp_c']}" in metrics, metrics
    assert f"{round(latest['hdd'])} HDD" in metrics, metrics
    assert f"£{e['latest_price']}" in metrics, metrics
    assert f"£{e['session_low']}" in metrics and f"£{e['session_high']}" in metrics, metrics
    assert f"£{abs(e['last_change_gbp'])}" in metrics, metrics


def test_panel1_lag_renders_two_dates_and_computed_distance(tmp_path):
    c = _live_company()
    w = _live_weather()
    mk = _market_fixture()
    weather_asof = w["monthly"][-1]["month"]
    settle_asof = mk["settlement_frontier"][:7]
    wy, wm = int(weather_asof[:4]), int(weather_asof[5:7])
    sy, sm = int(settle_asof[:4]), int(settle_asof[5:7])
    lag = (wy - sy) * 12 + (wm - sm)
    out = _render(c, WEATHER, _write(tmp_path, "market.json", mk), DECISIONS)
    lag_html = out["p1-lag"]["innerHTML"]
    assert weather_asof in lag_html, lag_html
    assert settle_asof in lag_html, lag_html
    assert f"{lag}-month" in lag_html, lag_html
    assert "settlement lag" in lag_html.lower(), lag_html


def test_panel1_lag_distance_is_computed_not_asserted(tmp_path):
    # R15 independence: move the settlement frontier; the rendered lag follows.
    c = _live_company()
    w = _live_weather()
    mk = _market_fixture()
    mk["settlement_frontier"] = "2025-01-07T22:30:00Z"
    wp = _write(tmp_path, "w.json", {"monthly": [{"month": "2025-12", "mean_temp_c": 7.0, "hdd": 240.0}]})
    out = _render(c, wp, _write(tmp_path, "market.json", mk), DECISIONS)
    lag_html = out["p1-lag"]["innerHTML"]
    assert "11-month" in lag_html, lag_html      # 2025-12 minus 2025-01
    assert "2025-01" in lag_html, lag_html


def test_panel1_regime_is_computed_not_asserted(tmp_path):
    # R15 independence: force the latest month to an extreme HDD; the regime pill
    # must flip to COLDER THAN USUAL from the DATA, proving it is computed.
    c = _live_company()
    w = _live_weather()
    w["monthly"][-1]["hdd"] = 9999.0
    out = _render(c, _write(tmp_path, "w.json", w), MARKET, DECISIONS)
    assert "COLDER THAN USUAL" in out["p1-pill"]["textContent"], out["p1-pill"]


def test_panel1_price_is_independent_of_render(tmp_path):
    # R15 independence: mutate the latest intra-day price to a sentinel.
    c = _live_company()
    mk = _market_fixture()
    mk["electricity"]["latest_price"] = 777.77
    out = _render(c, WEATHER, _write(tmp_path, "market.json", mk), DECISIONS)
    assert "£777.77" in out["p1-metrics"]["innerHTML"], out["p1-metrics"]


# =========================== PANEL 2: SUPPLIER ===========================

def test_panel2_renders_live_hedge_net_and_collections():
    c = _live_company()
    out = _render_live(c)
    metrics = out["p2-metrics"]["innerHTML"]
    t = c["trading_risk"]
    f = c["finance"]
    assert f"{t['latest_avg_hf'] * 100:.1f}%" in metrics, metrics
    # R14: the net-position figure carries its settled clock.
    assert "settled clock" in metrics, metrics
    assert f"{f['collection_rate_pct']:.1f}%" in metrics, metrics


def test_panel2_net_position_is_independent_of_render():
    # R15 independence: mutate the settled net margin; £-scale pixel follows.
    c = _live_company()
    c["finance"]["settled_net_margin_gbp"] = 4200000
    out = _render_live(c)
    assert "£4.20m" in out["p2-metrics"]["innerHTML"], out["p2-metrics"]


def test_panel2_hedge_band_pill_is_computed():
    # R15: a hedge ratio outside the 0.80-0.90 band flips the pill off ON PLAN.
    c = _live_company()
    c["trading_risk"]["latest_avg_hf"] = 0.50
    out = _render_live(c)
    assert out["p2-pill"]["textContent"] == "OFF BAND", out["p2-pill"]
    c["trading_risk"]["latest_avg_hf"] = 0.85
    out = _render_live(c)
    assert out["p2-pill"]["textContent"] == "ON PLAN", out["p2-pill"]


def test_panel2_renders_last_decision_with_why():
    c = _live_company()
    dec = _live_decisions()
    d0 = dec["decisions"][0]
    out = _render_live(c)
    body = out["p2-decision"]["innerHTML"]
    # The last decision's action AND its why are on the surface.
    assert d0["what"][:40] in body, body
    assert d0["why"][:40] in body, body


# =========================== PANEL 3: CUSTOMER ===========================

def test_panel3_renders_live_household_money_with_clocks():
    c = _live_company()
    h = c["household"]
    out = _render_live(c)
    metrics = out["p3-metrics"]["innerHTML"]

    def gbp(v):
        return ("-" if v < 0 else "") + "£" + f"{abs(v):,.2f}"

    assert gbp(h["billed_gbp"]) in metrics, metrics
    assert gbp(h["banked_gbp"]) in metrics, metrics
    assert gbp(h["balance_gbp"]) in metrics, metrics
    # R14: billed and banked clocks are on the surface.
    assert "billed clock" in metrics and "banked clock" in metrics, metrics


def test_panel3_selector_offers_only_real_household_and_honest_presets():
    c = _live_company()
    out = _render_live(c)
    sel = out["p3-selector"]["innerHTML"]
    # The one REAL account is the selected segment...
    assert c["household"]["id"] in sel, sel
    # ...and the segment presets are HONESTLY marked not-yet, never fabricated.
    assert "soon" in sel.lower(), sel
    assert "segmentation" in sel.lower(), sel


def test_panel3_balance_pill_is_computed():
    # R15: flip the balance positive; the pill leaves IN CREDIT for OUTSTANDING.
    c = _live_company()
    c["household"]["balance_gbp"] = 88.88
    out = _render_live(c)
    assert out["p3-pill"]["textContent"] == "OUTSTANDING", out["p3-pill"]
    assert "£88.88" in out["p3-metrics"]["innerHTML"]


def test_panel3_payments_and_arrears_chips_render():
    c = _live_company()
    h = c["household"]
    out = _render_live(c)
    chips = out["p3-chips"]["innerHTML"]
    assert f"{h['failed_payment_count']} failed" in chips, chips


# =========================== PANEL 4: CARBON (honest, never a number) ===========================

def test_panel4_carbon_names_e5_and_neso_and_shows_no_number():
    c = _live_company()
    out = _render_live(c)
    body = out["p4-body"]["innerHTML"]
    low = body.lower()
    assert "not instrumented" in low or "designed but not instrumented" in low, body
    assert "e5" in low and "neso" in low, body
    assert "half-hourly" in low, body
    # NEVER a fabricated tCO2e number: no digit precedes a tCO2e/tonne unit.
    assert not re.search(r"\d[\d,.]*\s*tco", low), body
    assert not re.search(r"\d[\d,.]*\s*tonne", low), body


def test_panel4_carbon_ignores_injected_fake_number():
    # R15 (inverse): even if a bogus per-account carbon number is present in the
    # household block, the honest placeholder must NOT surface it -- no number.
    c = _live_company()
    c["household"]["carbon_tco2e"] = 4242
    c["household"]["annual_co2_tonnes"] = 3131
    out = _render_live(c)
    body = out["p4-body"]["innerHTML"]
    assert "4242" not in body and "3131" not in body, body


# =========================== STRUCTURE ===========================

def test_build_note_renders_freshness_stamp():
    c = _live_company()
    out = _render_live(c)
    note = out["build-note"]["textContent"]
    assert "rendering of repo data only" in note, note
    if c.get("generated_at"):
        assert c["generated_at"] in note, note


def test_canonical_nav_present_with_now_first():
    nav = INDEX.read_text()
    m = re.search(r'<nav class="site-nav">(.*?)</nav>', nav, re.S)
    assert m, "site-nav block not found"
    block = m.group(1)
    # Now is the current door (active) and the first nav item.
    assert 'href="./" class="nav-link active">Now</a>' in block, block
    for label in ("Home", "Company", "World", "Customers", "Proof", "Method"):
        assert f">{label}</a>" in block, f"nav missing {label!r}"
