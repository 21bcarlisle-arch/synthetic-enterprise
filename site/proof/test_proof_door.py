"""Full-door render tests for the Proof door (site/proof/index.html).

The Proof door had only panel-specific tests (test_coupled_gaps_panel.py,
test_killlist_panel.py) -- no door-level render test like the other canonical
doors. This closes that parity gap, mirroring site/world/test_world_door.py and
site/project/test_project_door.py, and complements (does not replace) the two
existing panel tests.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness that drives the WHOLE render sequence) against
the REAL published site/data/proof.json, then assert the produced HTML contains
the actual source values, formatted the way the page's OWN num() helper formats
them (Number.toLocaleString "en-GB" grouping) -- the rendered pixel, not a brittle
Python int repr.

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
HARNESS = HERE / "_door_harness.mjs"
DATA = HERE.parent / "data" / "proof.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _num(n) -> str:
    """Mirror the page's num(): Number.toLocaleString('en-GB') thousands grouping."""
    return f"{int(n):,}" if n is not None else "--"


def _live() -> dict:
    return json.loads(DATA.read_text())


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


# ---------------------------------------------------------------------------
# R11: the page renders the live source values (the pixel, not a source string)
# ---------------------------------------------------------------------------
def test_verification_kpis_render_live_values():
    d = _live()
    out = _render(d)
    kpis = out["verify-kpis"]["innerHTML"]
    v = d["verification"]
    # Rendered via num() -> toLocaleString grouping. Assert the grouped pixel.
    assert f'>{_num(v["expert_hour_passed"])}<' in kpis, kpis
    assert f'>{_num(v["findings_caught_total"])}<' in kpis, kpis
    assert f'>{_num(v["atom_count"])}<' in kpis, kpis


def test_build_note_renders_live_test_count_and_freshness():
    d = _live()
    out = _render(d)
    note = out["build-note"]["textContent"]
    # test_count rendered via toLocaleString grouping (e.g. 18,504).
    assert f'{_num(d["test_count"])} tests' in note, note
    # R2 freshness: the generated_at stamp is rendered on the surface.
    assert d["generated_at"] in note, note


def test_timeline_intro_renders_live_rule_count():
    d = _live()
    out = _render(d)
    intro = out["timeline-intro"]["textContent"]
    # "N permanent rules (R1-RN)" both track d.rule_count.
    assert f'{d["rule_count"]} permanent rules' in intro, intro
    assert f'R1-R{d["rule_count"]}' in intro, intro


def test_banked_note_is_honest_and_evidence_linked():
    d = _live()
    out = _render(d)
    note = out["banked-note"]["innerHTML"]
    # Levels banked reflect the live levels_banked map (honest, not rounded up).
    lb = d["verification"]["levels_banked"]
    for lvl, cnt in lb.items():
        assert f"{cnt} at L{lvl}" in note, (lvl, cnt, note)
    # R1: the banked claim cites its evidence (the maturity map).
    assert "maturity_map.yaml" in note, note


# ---------------------------------------------------------------------------
# R15: independence -- a mutated source value must move the rendered pixel
# ---------------------------------------------------------------------------
def test_defects_caught_pixel_is_independent_of_render():
    d = _live()
    d["verification"]["findings_caught_total"] = 424242
    out = _render(d)
    assert ">424,242<" in out["verify-kpis"]["innerHTML"]


def test_test_count_pixel_is_independent_of_render():
    d = _live()
    d["test_count"] = 999888
    out = _render(d)
    assert "999,888 tests" in out["build-note"]["textContent"]


def test_freshness_pixel_is_independent_of_render():
    d = _live()
    d["generated_at"] = "2099-01-01T00:00:00Z"
    out = _render(d)
    assert "2099-01-01T00:00:00Z" in out["build-note"]["textContent"]


def test_rule_count_pixel_is_independent_of_render():
    d = _live()
    d["rule_count"] = 77
    out = _render(d)
    intro = out["timeline-intro"]["textContent"]
    assert "77 permanent rules" in intro
    assert "R1-R77" in intro


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
    # Proof is the current door -> marked active.
    assert 'href="../proof/" class="nav-link active">Proof</a>' in nav
    # The Director door is auth-gated and must NOT appear in the public nav.
    assert "../director/" not in nav, "Director door must not be in the public nav"
    assert ">Director</a>" not in nav


def test_at_least_one_claim_evidence_link():
    d = _live()
    out = _render(d)
    # R1: the timeline rules link out to their retrospectives (the incident that
    # forged each rule), and the banked-levels claim cites the maturity map.
    combined = out["banked-note"]["innerHTML"]
    text = INDEX.read_text()
    assert 'class="evlink"' in text, "no evidence-link class present on the door"
    assert "maturity_map.yaml" in combined, "banked-levels claim not evidence-linked"
