"""Render-side tests for the Home door (site/index.html).

The Home door is the front door in every door's nav, yet -- like the Journey door
before its test landed -- it had no full render test (only the cross-door audit's
static scan). This closes that parity gap, mirroring site/world/test_world_door.py
and site/project/test_project_door.py.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/*.json the
page consumes, then assert the produced HTML contains the actual source values,
formatted the way the page's OWN gbp() helper formats them (Number.toLocaleString
"en-GB" grouping, round-half-up to whole pounds) -- the rendered pixel, not a
brittle Python float repr of the source.

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence -- the render is not a hard-coded constant).

R3 (the page is a rendering, never an author) and R1 (every claim links to its
evidence) are asserted structurally on the nav + evidence links.
"""
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE / "data"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _gbp(n) -> str:
    """Mirror the page's gbp(): '£' + toLocaleString('en-GB') grouped whole pounds,
    round-half-up, negative sign before the '£'. Not a Python float repr."""
    if n is None:
        return "--"
    whole = int(math.floor(abs(n) + 0.5))
    return ("-" if n < 0 else "") + "£" + f"{whole:,}"


def _live() -> dict:
    return {
        "dashboard": json.loads((DATA / "dashboard.json").read_text()),
        "supplier": json.loads((DATA / "supplier.json").read_text()),
        "method": json.loads((DATA / "method.json").read_text()),
        "lastBill": None,
    }


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
# R11: the page renders the live source values (the pixel, not a source string)
# ---------------------------------------------------------------------------
def test_pulse_strip_renders_live_treasury_and_ev():
    d = _live()
    out = _render(d)
    ps = out["pulse-strip"]["innerHTML"]
    p = d["dashboard"]["portfolio"]
    assert _gbp(p["treasury_end_gbp"]) in ps, ps
    assert _gbp(p["enterprise_value_gbp"]) in ps, ps
    # EV carries an R2 PROVISIONAL badge on the pulse strip.
    assert "PROVISIONAL" in ps


def test_thesis_sentence_renders_live_opex_household_figures():
    d = _live()
    out = _render(d)
    sent = out["thesis-sentence"]["innerHTML"]
    ol = d["dashboard"]["opex_ledger"]
    assert _gbp(ol["true_opex_per_household_gbp"]) in sent, sent
    assert _gbp(ol["benchmark_opex_per_household_gbp"]) in sent, sent
    gap = ol["benchmark_opex_per_household_gbp"] - ol["true_opex_per_household_gbp"]
    assert _gbp(gap) in sent, sent


def test_thesis_evidence_renders_freshness_stamp_and_source_link():
    d = _live()
    out = _render(d)
    ev = out["thesis-evidence"]["innerHTML"]
    # R2 freshness: the dashboard generated_at stamp is rendered on the surface.
    assert d["dashboard"]["meta"]["generated_at"] in ev, ev
    # R1: the thesis number cites its data source.
    assert 'href="./data/dashboard.json"' in ev, ev


# ---------------------------------------------------------------------------
# R15: independence -- a mutated source value must move the rendered pixel
# ---------------------------------------------------------------------------
def test_treasury_pixel_is_independent_of_render():
    d = _live()
    d["dashboard"]["portfolio"]["treasury_end_gbp"] = 424242
    out = _render(d)
    assert "£424,242" in out["pulse-strip"]["innerHTML"]


def test_thesis_true_cost_pixel_is_independent_of_render():
    d = _live()
    d["dashboard"]["opex_ledger"]["true_opex_per_household_gbp"] = 987
    out = _render(d)
    assert "£987" in out["thesis-sentence"]["innerHTML"]


def test_thesis_freshness_pixel_is_independent_of_render():
    d = _live()
    d["dashboard"]["meta"]["generated_at"] = "2099-01-01T00:00:00Z"
    out = _render(d)
    assert "2099-01-01T00:00:00Z" in out["thesis-evidence"]["innerHTML"]


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
    # Home is the current door -> marked active.
    assert 'href="./" class="nav-link active">Home</a>' in nav
    # The Director door is auth-gated and must NOT appear in the public nav.
    assert "./director/" not in nav, "Director door must not be in the public nav"
    assert ">Director</a>" not in nav


def test_at_least_one_claim_evidence_link():
    text = INDEX.read_text()
    # R1: the thesis figure and the door cards link out to their evidence surfaces.
    assert './data/dashboard.json' in text, "no data-source evidence link found"
    assert 'href="./company/"' in text or 'href="./method/"' in text, \
        "no claim->evidence link to an evidence door found"
