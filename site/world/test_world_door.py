"""Render-side tests for the World door (site/world/index.html).

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/world.json
the page consumes, then assert the produced HTML contains the actual source values
-- the rendered pixel, not the source string.

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence -- the render is not a hard-coded constant), and the
R12 diagnostic-not-target framing must be rendered verbatim on the wall band.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "world.json"
WEATHER = HERE.parent / "data" / "weather.json"
MARKET = HERE.parent / "data" / "market.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict, weather_path: Path | None = None, market_path: Path | None = None) -> dict:
    # If weather is needed, write the (possibly mutated) weather dict to a temp
    # file so the harness can load it via argv[3]; the intra-day market feed via
    # argv[4]; otherwise pass the live file(s).
    args = [NODE, str(HARNESS), str(INDEX)]
    if weather_path is not None:
        args.append(str(weather_path))
        if market_path is not None:
            args.append(str(market_path))
    proc = subprocess.run(
        args,
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _render_with_weather(data: dict, weather: dict, tmp_path) -> dict:
    wp = tmp_path / "weather.json"
    wp.write_text(json.dumps(weather))
    return _render(data, weather_path=wp)


def _render_full(data: dict, weather: dict, market: dict, tmp_path) -> dict:
    wp = tmp_path / "weather.json"
    wp.write_text(json.dumps(weather))
    mp = tmp_path / "market.json"
    mp.write_text(json.dumps(market))
    return _render(data, weather_path=wp, market_path=mp)


def _live() -> dict:
    return json.loads(DATA.read_text())


def _live_weather() -> dict:
    return json.loads(WEATHER.read_text())


def _live_market() -> dict:
    return json.loads(MARKET.read_text())


def test_crossings_render_live_names_and_rag():
    d = _live()
    out = _render(d)
    body = out["crossings"]["innerHTML"]
    assert d["wall"]["crossings"], "fixture precondition: world should have wall crossings"
    for c in d["wall"]["crossings"]:
        assert c["name"] in body, f"missing crossing {c['name']}"
        # RAG band is divergence magnitude (R12), rendered as a badge.
        assert c["rag"] in body


def test_library_counts_render_live():
    d = _live()
    out = _render(d)
    kpis = out["lib-kpis"]["innerHTML"]
    counts = d["anchors"]["library"]["counts"]
    assert f">{counts['OK']}<" in kpis, kpis
    assert f">{counts['WARN']}<" in kpis


def test_wall_band_renders_r12_diagnostic_framing():
    out = _render(_live())
    band = out["wall-band"]["innerHTML"].lower()
    # R12: RAG is divergence magnitude, not a verdict / target.
    assert "not a verdict" in band or "diagnostic" in band or "not a target" in band


def test_build_note_renders_freshness_stamp():
    d = _live()
    out = _render(d)
    note = out["build-note"]["innerHTML"] + out["build-note"]["textContent"]
    assert "generated" in note.lower()
    # The generated stamp from the file must appear on the surface.
    gen = d.get("generated_at", "")
    assert gen[:10] in note, note


def test_crossing_divergence_value_is_independent_of_render():
    # R15 independence: mutate a crossing's divergence value; the rendered pixel
    # must follow the data, not a baked-in constant.
    d = _live()
    d["wall"]["crossings"][0]["divergence_value"] = "SENTINEL_999X"
    out = _render(d)
    assert "SENTINEL_999X" in out["crossings"]["innerHTML"]


# --- World OPERATIONAL STATE panel (director's window: what the world is doing now) ---

def test_world_state_renders_latest_month_and_stamp(tmp_path):
    # R11: the state panel's freshness stamp + current-weather KPIs render the
    # ACTUAL latest realised month from weather.json, not a hardcoded date.
    d = _live()
    w = _live_weather()
    latest = w["monthly"][-1]
    out = _render_with_weather(d, w, tmp_path)
    stamp = out["state-stamp"]["textContent"]
    assert latest["month"] in stamp, f"latest month {latest['month']} not in stamp {stamp}"
    kpis = out["wstate-kpis"]["innerHTML"]
    # current temperature and HDD from the realised series
    assert f"{latest['mean_temp_c']}" in kpis, kpis
    assert f"{round(latest['hdd'])} HDD" in kpis, kpis


def test_world_state_market_ssp_renders_live_settled_value(tmp_path):
    # R11 + R14: the market KPI renders the latest settled annual-mean SSP from
    # world.json's blindfold crossing, carrying a settled basis label.
    d = _live()
    w = _live_weather()
    bf = [c for c in d["wall"]["crossings"] if c.get("id") == "blindfold"][0]
    ssp = bf["series"][-1]
    out = _render_with_weather(d, w, tmp_path)
    kpis = out["wstate-kpis"]["innerHTML"]
    assert f"£{ssp['mean']}" in kpis, kpis
    assert "settled" in kpis.lower(), "R14: market figure must carry its settled clock"


def test_world_state_regime_is_computed_not_asserted(tmp_path):
    # R15 independence: force the latest month far above its calendar-month
    # baseline; the regime classifier must flip to COLDER THAN USUAL from the
    # DATA, proving it is computed, not a baked string.
    d = _live()
    w = _live_weather()
    # push the last December to an extreme HDD
    w["monthly"][-1]["hdd"] = 9999.0
    out = _render_with_weather(d, w, tmp_path)
    regime = out["wstate-regime"]["innerHTML"]
    assert "COLDER THAN USUAL" in regime, regime
    # and the trajectory shows the mutated value
    assert "9999 HDD" in regime, regime


def test_world_state_regime_ties_to_cold_and_still_physics(tmp_path):
    # The regime narrative must name the shipped cold-and-still price physics
    # (W1_6 chain / W1_3 tail) so the director can connect weather -> price.
    d = _live()
    w = _live_weather()
    out = _render_with_weather(d, w, tmp_path)
    regime = out["wstate-regime"]["innerHTML"].lower()
    assert "cold-and-still" in regime and "w1_6" in regime, regime


def test_world_state_basis_names_r12_diagnostic(tmp_path):
    # R12: the regime is a diagnostic, never a target -- must be stated on-surface.
    d = _live()
    w = _live_weather()
    out = _render_with_weather(d, w, tmp_path)
    basis = out["wstate-basis"]["innerHTML"].lower()
    assert "diagnostic" in basis and "never a target" in basis, basis


# --- Directive 1: the settlement lag made legible (two dated clocks + distance) ---
#
# These use a CONTROLLED market fixture (not the live market.json): the real
# price_feed.json is rewritten by a background daemon and degrades to gas-only in
# a worktree lacking the gitignored SSP cache, so asserting against the live feed
# would be flaky. Feed volatility is covered separately in
# tools/test_generate_market_data.py (derivation + fail-closed).

def _market_fixture() -> dict:
    """A deterministic intra-day electricity session, shaped exactly like
    tools/generate_market_data.py emits (verified against the real 48-HH feed)."""
    return {
        "available": True,
        "published_at": "2026-07-17T11:07:42Z",
        "settlement_frontier": "2025-06-07T22:30:00Z",
        "evidence_url": "../data/market.json",
        "electricity": {
            "unit": "£/MWh",
            "as_of_period": "2025-06-07T22:30:00Z",
            "first_period": "2025-06-06T23:00:00Z",
            "point_count": 48,
            "latest_price": 100.58,
            "session_open": 121.0,
            "session_close": 100.58,
            "session_high": 144.8,
            "session_high_period": "2025-06-07T00:30:00Z",
            "session_low": 66.76,
            "session_low_period": "2025-06-07T01:30:00Z",
            "session_mean": 105.94,
            "session_range": 78.04,
            "last_change_gbp": -9.37,
            "last_change_pct": -8.52,
            "trajectory": [
                {"period": f"2025-06-07T{h:02d}:00:00Z", "price": 100.0 + h} for h in range(6)
            ],
        },
    }


def test_world_state_lag_renders_two_dates_and_computed_distance(tmp_path):
    # R11: the lag statement renders the ACTUAL weather as-of month and the
    # settlement frontier month, plus the whole-month distance between them --
    # the director's "world is at X, books at Y" gap.
    d = _live()
    w = _live_weather()
    mk = _market_fixture()
    weather_asof = w["monthly"][-1]["month"]                 # e.g. "2025-12"
    settle_asof = mk["settlement_frontier"][:7]              # "2025-06"
    wy, wm = int(weather_asof[:4]), int(weather_asof[5:7])
    sy, sm = int(settle_asof[:4]), int(settle_asof[5:7])
    lag = (wy - sy) * 12 + (wm - sm)
    out = _render_full(d, w, mk, tmp_path)
    lag_html = out["wstate-lag"]["innerHTML"]
    assert weather_asof in lag_html, lag_html
    assert settle_asof in lag_html, lag_html
    assert f"{lag}-month" in lag_html, lag_html
    assert "settlement lag" in lag_html.lower(), lag_html
    # Director's framing: the distance is real, not a bug -- shown, not pinned away.
    assert "not a bug" in lag_html.lower(), lag_html


def test_world_state_lag_distance_is_computed_not_asserted(tmp_path):
    # R15 independence: move the settlement frontier; the rendered lag distance
    # must FOLLOW the data (proving it is computed from the two dates, not a baked
    # "6-month" string).
    d = _live()
    w = _live_weather()
    mk = _market_fixture()
    w["monthly"][-1]["month"] = "2025-12"
    mk["settlement_frontier"] = "2025-01-07T22:30:00Z"
    out = _render_full(d, w, mk, tmp_path)
    lag_html = out["wstate-lag"]["innerHTML"]
    assert "11-month" in lag_html, lag_html   # 2025-12 minus 2025-01
    assert "2025-01" in lag_html, lag_html


def test_world_state_stamp_carries_both_clocks(tmp_path):
    # R14/Directive 1: the panel stamp names BOTH as-of clocks so the reader sees
    # the two are not the same clock.
    d = _live()
    w = _live_weather()
    mk = _market_fixture()
    out = _render_full(d, w, mk, tmp_path)
    stamp = out["state-stamp"]["textContent"].lower()
    assert "weather" in stamp and "settled books" in stamp, stamp


# --- Directive 2: the intra-day market movement (what the market is DOING) ---

def test_world_state_intraday_movement_renders(tmp_path):
    # R11: the intra-day KPIs render the latest price, last move, and session
    # range from market.json -- the movement, not the annual mean.
    d = _live()
    w = _live_weather()
    mk = _market_fixture()
    e = mk["electricity"]
    out = _render_full(d, w, mk, tmp_path)
    kpis = out["wstate-kpis"]["innerHTML"]
    idz = out["wstate-intraday"]["innerHTML"]
    assert f"£{e['latest_price']}" in kpis, kpis
    assert f"£{e['session_low']}" in kpis and f"£{e['session_high']}" in kpis, kpis
    # The last half-hour move magnitude is on-surface.
    assert f"£{abs(e['last_change_gbp'])}" in kpis, kpis
    # The trajectory sparkline names the session as intra-day wholesale.
    assert "intra-day wholesale" in idz.lower(), idz


def test_world_state_intraday_price_is_independent_of_render(tmp_path):
    # R15 independence: mutate the latest intra-day price to a sentinel; the
    # rendered movement KPI must follow the data, not a hard-coded constant.
    d = _live()
    w = _live_weather()
    mk = _market_fixture()
    mk["electricity"]["latest_price"] = 777.77
    out = _render_full(d, w, mk, tmp_path)
    kpis = out["wstate-kpis"]["innerHTML"]
    assert "£777.77" in kpis, kpis


def test_world_state_intraday_carries_clock_and_asof(tmp_path):
    # R14: the intra-day wholesale figure carries its clock (£/MWh, observed/
    # wholesale) and its as-of period (the settlement frontier), demonstrating the
    # lag against the weather clock.
    d = _live()
    w = _live_weather()
    mk = _market_fixture()
    out = _render_full(d, w, mk, tmp_path)
    kpis = out["wstate-kpis"]["innerHTML"].lower()
    assert "£/mwh" in kpis, kpis
    assert "observed" in kpis and "as of" in kpis, kpis


def test_live_market_json_is_valid_and_clocked_when_available():
    # Guards the committed artifact: market.json must be valid JSON, and when it
    # reports an intra-day session it must carry the £/MWh clock + as-of period
    # (R14). Tolerant of the fail-closed (gas-only feed) state.
    mk = _live_market()
    assert isinstance(mk, dict) and "available" in mk
    if mk.get("available") and mk.get("electricity"):
        e = mk["electricity"]
        assert e["unit"] == "£/MWh"
        assert e["as_of_period"] and mk["settlement_frontier"] == e["as_of_period"]


def test_world_state_intraday_absent_feed_degrades_gracefully(tmp_path):
    # R15 fail-closed: an unavailable feed must not fabricate a session -- the
    # panel says so, and the weather/lag panels still render.
    d = _live()
    w = _live_weather()
    mk = {"available": False, "electricity": None}
    out = _render_full(d, w, mk, tmp_path)
    idz = out["wstate-intraday"]["innerHTML"].lower()
    assert "unavailable" in idz, idz
    # weather KPIs still present
    assert f"{round(w['monthly'][-1]['hdd'])} HDD" in out["wstate-kpis"]["innerHTML"]
