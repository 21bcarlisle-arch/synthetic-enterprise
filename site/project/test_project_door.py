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
    "regulatory": "regulatory.json",
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
# Key Discoveries: the hedge-cover band is a COMPANY output rendered off
# dashboard.json.trading.hedge_annual (R11), with an R2 passport (basis +
# freshness + PROVISIONAL).
# ---------------------------------------------------------------------------
def test_hedge_band_renders_live_min_max_avg_hf():
    d = _live()
    out = _render(d)
    ha = d["dashboard"]["trading"]["hedge_annual"]
    avgs = [r["avg_hf"] for r in ha if r.get("avg_hf") is not None]
    assert avgs, "fixture precondition: hedge_annual has avg_hf values"
    lo, hi = min(avgs), max(avgs)
    # The page renders lo-hi with JS Number.toFixed(2); mirror that formatting.
    assert out["disc-hedge-band"]["textContent"] == f"{lo:.2f}-{hi:.2f}"


def test_hedge_passport_renders_freshness_and_provisional():
    d = _live()
    out = _render(d)
    pp = out["disc-hedge-passport"]["textContent"]
    # R2 passport: PROVISIONAL badge + the dashboard generated_at freshness stamp.
    assert "PROVISIONAL" in pp, pp
    assert d["dashboard"]["meta"]["generated_at"] in pp, pp


def test_hedge_band_is_independent_of_render():
    # R15: a mutated source value must move the rendered pixel (not a constant).
    d = _live()
    d["dashboard"]["trading"]["hedge_annual"] = [
        {"year": 2016, "avg_hf": 0.12},
        {"year": 2017, "avg_hf": 0.99},
    ]
    out = _render(d)
    assert out["disc-hedge-band"]["textContent"] == "0.12-0.99"


def test_key_discoveries_figures_link_to_evidence():
    text = INDEX.read_text()
    # R1: each narrative discovery figure links to the source that established it.
    # ~30 suppliers + £3,549 / 3-4% switching -> market-research findings; hedge
    # band -> the point-in-time-leak review-gate finding.
    assert "market_research/energy_market_complexity_june2026.md" in text, \
        "supplier-failure benchmark link missing"
    assert "market_research/churn_price_elasticity.md" in text, \
        "price-elasticity benchmark link missing"
    assert "review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md" in text, \
        "hedge finding link missing"


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
# Regulatory tab: build-status claims render off regulatory.json (R11), and are
# independent of the render (R15). The published rates + legal-basis rows stay
# static commons -- only the drift-prone build-status bits are data-backed.
# ---------------------------------------------------------------------------
def test_regulatory_counts_render_live_values():
    d = _live()
    out = _render(d)
    reg = d["regulatory"]
    assert out["reg-module-count"]["textContent"] == str(reg["module_count"])
    assert out["reg-domain-count"]["textContent"] == str(reg["slc_domain_count"])
    assert out["reg-slc-domains"]["textContent"] == str(reg["slc_domain_count"])
    assert out["reg-overall-rag"]["textContent"] == reg["overall_rag"]


def test_regulatory_freshness_stamp_renders():
    d = _live()
    out = _render(d)
    # R2/freshness: the generated_at stamp from the source is rendered on the tab.
    assert d["regulatory"]["generated_at"] in out["reg-freshness"]["textContent"]


def test_regulatory_status_badges_render_live_status():
    d = _live()
    out = _render(d)
    by_key = {s["key"]: s["status"] for s in d["regulatory"]["schemes"]}
    for key in ("RO", "FMD", "WHD", "SR"):
        assert by_key[key] in out[f"reg-badge-{key}"]["innerHTML"], (key, by_key[key])


def test_regulatory_module_count_is_independent_of_render():
    # R15: a mutated source value must move the rendered pixel (not a constant).
    d = _live()
    d["regulatory"]["module_count"] = 987654
    out = _render(d)
    assert out["reg-module-count"]["textContent"] == "987654"


def test_regulatory_badge_status_is_independent_of_render():
    d = _live()
    # flip a WIRED scheme to a sentinel; the rendered badge must follow.
    d["regulatory"]["schemes"] = [
        {"key": "RO", "label": "RO", "status": "SENTINEL_STATUS", "basis": "x"}
    ]
    out = _render(d)
    assert "SENTINEL_STATUS" in out["reg-badge-RO"]["innerHTML"]


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
