"""Render-side tests for the Tours door (site/tours/index.html).

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/tours.json
the page consumes, then assert the produced HTML contains the actual source values
-- the rendered pixel, not the source string. Each persona tour is rendered by
selecting it in the harness, exactly as a click would.

R15 (a control must be able to FAIL): a mutation of a source stop must change the
rendered pixel (independence), and every persona's stops must actually render for
its own selected tab.
"""
import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "tours.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict, persona: str | None = None) -> dict:
    cmd = [NODE, str(HARNESS), str(INDEX)]
    if persona:
        cmd.append(persona)
    proc = subprocess.run(
        cmd,
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live() -> dict:
    return json.loads(DATA.read_text())


def test_data_wellformed():
    d = _live()
    assert d["personas"], "fixture precondition: tours should have personas"
    for p in d["personas"]:
        assert p["id"] and p["label"] and p["one_liner"] and p["intro"]
        stops = p["stops"]
        assert len(stops) == 10, f"{p['id']} must have 10 stops (brief), has {len(stops)}"
        ns = sorted(s["n"] for s in stops)
        assert ns == list(range(1, 11)), f"{p['id']} stops must be numbered 1..10, got {ns}"
        for s in stops:
            assert s["title"] and s["look_at"] and s["why"] and s["url"]


def test_all_persona_tabs_render():
    d = _live()
    out = _render(d)
    tabs = out["tabs"]["innerHTML"]
    for p in d["personas"]:
        assert p["label"] in tabs, f"missing tab {p['label']}"
        assert p["one_liner"] in tabs


def test_each_persona_tour_renders_its_own_stops():
    d = _live()
    for p in d["personas"]:
        out = _render(d, persona=p["id"])
        tour = out["tour"]["innerHTML"]
        assert p["intro"][:30] in tour, f"{p['id']} intro missing"
        for s in p["stops"]:
            assert s["title"] in tour, f"{p['id']} missing stop title {s['title']}"
            assert s["url"] in tour, f"{p['id']} missing stop url {s['url']}"
            assert s["why"][:30] in tour, f"{p['id']} missing stop why for {s['title']}"


def test_default_tour_is_first_persona():
    d = _live()
    out = _render(d)  # no persona selected -> defaults to first
    tour = out["tour"]["innerHTML"]
    first = d["personas"][0]
    assert first["stops"][0]["title"] in tour


def test_intro_renders_from_data():
    d = _live()
    out = _render(d)
    assert d["meta"]["intro"][:30] in out["hero-p"]["textContent"]


def test_mutation_stop_changes_pixel():
    """R15: prove the render is independent of a hard-coded constant."""
    d = _live()
    pid = d["personas"][0]["id"]
    base = _render(d, persona=pid)["tour"]["innerHTML"]
    sentinel = "ZZ_MUTATION_SENTINEL_STOP_ZZ"
    mutated = copy.deepcopy(d)
    original_title = mutated["personas"][0]["stops"][0]["title"]
    mutated["personas"][0]["stops"][0]["title"] = sentinel
    out = _render(mutated, persona=pid)["tour"]["innerHTML"]
    assert sentinel in out, "mutated stop title did not reach the pixel"
    assert original_title in base and original_title not in out, (
        "render appears to ignore source stop title (hard-coded?)"
    )
