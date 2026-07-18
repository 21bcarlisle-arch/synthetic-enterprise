"""Render-side tests for the Journey door (site/project/index.html).

This door is the canonical Journey destination in every door's nav, yet it was the
only public door without a render test. This closes that gap, mirroring the pattern
of site/world/test_world_door.py and site/method/test_method_door.py.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/*.json the
page consumes, then assert the produced HTML contains the actual source values --
the rendered pixel, not the source string.

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence -- the render is not a hard-coded constant).

R3 (the page is a rendering, never an author) and R1 (every claim links to its
evidence) are asserted structurally on the nav + evidence links.
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
DATA = HERE.parent / "data"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

# The page's inline Promise.all fetches these six data files, bound to D/PH/MM/TM/PP/DT.
_FILES = {
    "dashboard": "dashboard.json",
    "phases": "phases.json",
    "maturity_map": "maturity_map.json",
    "test_mix": "test_mix.json",
    "provisional_plan": "provisional_plan.json",
    "director_twin": "director_twin.json",
}


def _live() -> dict:
    return {k: json.loads((DATA / fn).read_text()) for k, fn in _FILES.items()}


def _render(payload: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# R11: the page renders the live source values (not a source string, the pixel)
# ---------------------------------------------------------------------------
def test_investor_kpis_render_live_phase_count_and_tests():
    d = _live()
    out = _render(d)
    kpis = out["inv-kpis"]["innerHTML"]
    # "Phases shipped" pixel == phases.json total_phases, verbatim.
    assert f">{d['phases']['total_phases']}<" in kpis, kpis
    # "Tests passing" pixel == last test_progression value, rendered via
    # Number.toLocaleString("en-GB") (thousands grouped). Mirror that grouping
    # instead of a brittle bare-int assertion.
    last_tests = d["phases"]["test_progression"][-1][1]
    grouped = f"{last_tests:,}"
    assert f">{grouped}<" in kpis, kpis


def test_build_evidence_domain_count_renders_live_test_mix():
    d = _live()
    out = _render(d)
    # the "N distinct real business domains under test" pixel == test_mix areas count.
    assert out["be-domain-count"]["textContent"] == str(len(d["test_mix"]["areas"]))


def test_maturity_map_renders_live_atom_names():
    d = _live()
    out = _render(d)
    body = out["mm-view-body"]["innerHTML"]
    assert d["maturity_map"]["atoms"], "fixture precondition: maturity map has atoms"
    # The default Activity view groups every atom by loop_stage; each atom's name
    # is rendered. Assert a representative live atom name is present.
    names = [a["name"] for a in d["maturity_map"]["atoms"]]
    assert any(n in body for n in names), "no live atom name rendered on the map"


def test_epoch2_strip_renders_live_movements():
    d = _live()
    out = _render(d)
    strip = out["epoch2-strip"]["innerHTML"]
    movements = d["maturity_map"].get("epoch2_movements") or []
    assert movements, "fixture precondition: epoch2_movements present"
    for m in movements:
        assert m["id"] in strip, f"movement {m['id']} not rendered"


def test_provisional_plan_renders_live_generated_stamp():
    d = _live()
    out = _render(d)
    body = out["pp-body"]["innerHTML"]
    # R2/freshness: the generated_at stamp from the source file is rendered.
    assert d["provisional_plan"]["generated_at"] in body, body


def test_director_twin_renders_live_fidelity_counts():
    d = _live()
    out = _render(d)
    body = out["dt-body"]["innerHTML"]
    f = d["director_twin"]["fidelity"]
    assert f">{f['answered']} answered" in body or f"{f['answered']} answered" in body, body


# ---------------------------------------------------------------------------
# R15: independence -- a mutated source value must move the rendered pixel
# ---------------------------------------------------------------------------
def test_phase_count_is_independent_of_render():
    d = _live()
    d["phases"]["total_phases"] = 424242
    out = _render(d)
    assert ">424242<" in out["inv-kpis"]["innerHTML"]


def test_atom_name_is_independent_of_render():
    d = _live()
    d["maturity_map"]["atoms"][0]["name"] = "SENTINEL_999X_ATOM"
    out = _render(d)
    assert "SENTINEL_999X_ATOM" in out["mm-view-body"]["innerHTML"]


def test_domain_count_is_independent_of_render():
    d = _live()
    d["test_mix"]["areas"] = d["test_mix"]["areas"][:3]
    out = _render(d)
    assert out["be-domain-count"]["textContent"] == "3"


# ---------------------------------------------------------------------------
# R3 (nav is canonical) and R1 (claim -> evidence)
# ---------------------------------------------------------------------------
def _site_nav(text: str) -> str:
    m = re.search(r'<nav class="site-nav">(.*?)</nav>', text, re.S)
    assert m, "site-nav block not found"
    return m.group(1)


def test_canonical_nav_present_and_director_absent():
    nav = _site_nav(INDEX.read_text())
    for label in ("Home", "Company", "World", "Proof", "Method", "Journey", "Simplified"):
        assert f">{label}</a>" in nav, f"nav missing canonical door {label!r}"
    # Journey is the current door -> marked active.
    assert 'href="../project/" class="nav-link active">Journey</a>' in nav
    # The Director door is auth-gated and must NOT appear in the public nav.
    assert "../director/" not in nav, "Director door must not be in the public nav"
    assert ">Director</a>" not in nav


def test_at_least_one_claim_evidence_link():
    text = INDEX.read_text()
    # R1: factual claims link out to their evidence surfaces (other doors / the
    # method track record). At least one such evidence link must be present.
    assert 'href="../method/' in text or 'href="../proof/' in text, \
        "no claim->evidence link to an evidence door found"
