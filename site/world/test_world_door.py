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

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict, weather_path: Path | None = None) -> dict:
    # If weather is needed, write the (possibly mutated) weather dict to a temp
    # file so the harness can load it via argv[3]; otherwise pass the live file.
    args = [NODE, str(HARNESS), str(INDEX)]
    if weather_path is not None:
        args.append(str(weather_path))
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


def _live() -> dict:
    return json.loads(DATA.read_text())


def _live_weather() -> dict:
    return json.loads(WEATHER.read_text())


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
