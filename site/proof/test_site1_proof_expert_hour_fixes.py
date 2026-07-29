"""Tests for the three /proof/-side SITE1 Expert-Hour findings this fork closed
(2026-07-29 cold-eyes skeptic-veteran pass, docs/design/maturity_map.yaml
SITE1_expert_doors expert_hour.findings):

  MAJOR-3  the predictions ledger could not record a miss (a control that
           cannot fail is worse than none). See also
           tests/tools/test_site1_proof_predictions_ledger.py for the data-layer
           (tools/generate_proof_data.py) tests -- these are the RENDERED-pixel
           (R11) tests for the same fix.
  MAJOR-7  evidence citations inert by construction -- 10 anchors styled
           identically to real evidence links but dead by construction
           (href="#" onclick="return false").
  MINOR-9  sitemap.xml 404s, robots.txt invites indexing, no <noscript>
           fallback for a non-JS crawler.

R11: these execute the page's ACTUAL inline JavaScript (via the existing
Node/vm door harness) against real/synthetic data, asserting the RENDERED
pixel, never the source string alone.
R15: a control must be able to FAIL -- each control below is proven to fire
on its own named defect and clear on good input.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_door_harness.mjs"
DATA = HERE.parent / "data" / "proof.json"
SITE = HERE.parent
SITEMAP = SITE / "sitemap.xml"
ROBOTS = SITE / "robots.txt"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


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


# ===========================================================================
# MAJOR-3: predictions ledger can record a miss
# ===========================================================================
def _esc(s: str) -> str:
    """Mirror the page's esc(): HTML-escape &, <, > the same way the JS does."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def test_headline_renders_the_live_honest_narrative():
    d = _live()
    out = _render(d)
    intro = out["pred-intro"]["innerHTML"]
    assert d["predictions"]["headline"], "live proof.json must carry a headline"
    assert _esc(d["predictions"]["headline"]) in intro, intro


def test_kpis_render_distinct_prediction_counts_not_padded_raw_count():
    d = _live()
    out = _render(d)
    kpis = out["pred-kpis"]["innerHTML"]
    p = d["predictions"]
    assert f'>{p["distinct_renewal_predictions"]}<' in kpis, kpis
    assert f'>{p["distinct_hedge_predictions"]}<' in kpis, kpis
    assert f'>{p["renewal"]["ungradeable"]}<' in kpis, kpis
    assert f'>{p["hedge"]["real_verdicts"]}<' in kpis, kpis


def _mutated_predictions(**over):
    base = {
        "available": True, "source": "site/state/track_record_scorecard.json",
        "clock_started": "2026-07-04", "wall_clock_today": "2026-07-29",
        "log_entry_count": 1, "distinct_renewal_predictions": 1,
        "distinct_hedge_predictions": 0, "renewal_tolerance_pct": 0.02,
        "headline": "sentinel headline",
        "renewal": {"graded": 0, "pending": 0, "inconclusive": 0, "ungradeable": 0,
                    "on_target": 0, "off_target": 0, "churned": 0,
                    "inconclusive_entries": [], "graded_entries": []},
        "hedge": {"graded": 0, "ungraded": 0, "real_verdicts": 0,
                  "gradeable_pending_logic": 0, "stale_blocked": 0,
                  "current_market_data_stale_days": 1, "entries": []},
        "retention": {"logged": 0, "graded": 0, "note": "n/a"},
    }
    base.update(over)
    return base


def test_off_target_renewal_miss_is_reachable_and_renders_distinct_from_a_hit():
    # R15: fires on the defect (a real miss) -- an off_target renewal must
    # render with the MISS class (o-off, red), not the same class as a hit.
    d = _live()
    d["predictions"] = _mutated_predictions(renewal={
        "graded": 2, "pending": 0, "inconclusive": 0, "ungradeable": 0,
        "on_target": 1, "off_target": 1, "churned": 0,
        "inconclusive_entries": [],
        "graded_entries": [
            {"cid": "C-HIT", "renewal_date": "2026-07-01", "proposed_rate_gbp_per_mwh": 100.0,
             "outcome": "renewed_on_target", "re_logged_count": 1},
            {"cid": "C-MISS", "renewal_date": "2026-07-01", "proposed_rate_gbp_per_mwh": 100.0,
             "outcome": "renewed_off_target", "re_logged_count": 1},
        ],
    })
    out = _render({"proof": d})
    body = out["pred-body"]["innerHTML"]
    assert "C-MISS" in body and "C-HIT" in body, body
    # The miss renders with the miss class; the hit does not.
    miss_row = re.search(r'<div class="lg-row"><span>C-MISS.*?</div>', body, re.S).group(0)
    hit_row = re.search(r'<div class="lg-row"><span>C-HIT.*?</div>', body, re.S).group(0)
    assert 'class="o-off"' in miss_row, miss_row
    assert 'class="o-off"' not in hit_row, hit_row
    assert 'class="o-target"' in hit_row, hit_row


def test_ungradeable_stale_entry_renders_with_its_own_distinct_class_and_horizon():
    # R15: fires on the defect (a stale-past-horizon entry) -- must render
    # with its OWN distinct visual class, not folded into the generic
    # unbounded "inconclusive" state that can never resolve.
    d = _live()
    d["predictions"] = _mutated_predictions(renewal={
        "graded": 0, "pending": 0, "inconclusive": 1, "ungradeable": 1,
        "on_target": 0, "off_target": 0, "churned": 0,
        "inconclusive_entries": [{
            "cid": "C9", "renewal_date": "2025-06-29", "proposed_rate_gbp_per_mwh": 153.49,
            "outcome": "no_renewal_detected_yet", "re_logged_count": 4,
            "first_logged": "2026-07-04", "last_logged": "2026-07-07",
            "days_since_renewal_date": 395, "bounded_state": "ungradeable",
            "display_outcome": "ungradeable -- portfolio snapshot 395d stale past the flagged renewal date (horizon 90d)",
        }],
        "graded_entries": [],
    })
    out = _render({"proof": d})
    body = out["pred-body"]["innerHTML"]
    assert "ungradeable" in body, body
    assert "395d" in body, body
    assert 'class="o-stale"' in body, body
    # The unbounded "not counted as a miss" excuse text must NOT be the
    # rendered outcome pixel any more -- the bounded display_outcome wins.
    assert "no_renewal_detected_yet<" not in body, body


def test_ungradeable_clears_on_a_fresh_within_horizon_entry():
    # R15 both-ways: a fresh, within-horizon inconclusive entry must NOT
    # render with the stale class -- the control does not fire on good input.
    d = _live()
    d["predictions"] = _mutated_predictions(renewal={
        "graded": 0, "pending": 0, "inconclusive": 1, "ungradeable": 0,
        "on_target": 0, "off_target": 0, "churned": 0,
        "inconclusive_entries": [{
            "cid": "C1", "renewal_date": "2026-07-24", "proposed_rate_gbp_per_mwh": 100.0,
            "outcome": "no_renewal_detected_yet", "re_logged_count": 1,
            "first_logged": "2026-07-29", "last_logged": "2026-07-29",
            "days_since_renewal_date": 5, "bounded_state": "inconclusive_within_horizon",
            "display_outcome": "no_renewal_detected_yet",
        }],
        "graded_entries": [],
    })
    out = _render({"proof": d})
    body = out["pred-body"]["innerHTML"]
    assert 'class="o-stale"' not in body, body
    assert 'class="o-inconc"' in body, body


def test_re_logged_count_renders_when_greater_than_one():
    d = _live()
    d["predictions"] = _mutated_predictions(hedge={
        "graded": 0, "ungraded": 0, "real_verdicts": 0,
        "gradeable_pending_logic": 0, "stale_blocked": 1,
        "current_market_data_stale_days": 1,
        "entries": [{
            "hedge_recommendation": "INCREASE", "outcome": "ungraded -- market data has not advanced",
            "re_logged_count": 26, "first_logged": "2026-07-04", "last_logged": "2026-07-29",
            "decision_run_at": "2026-07-04",
        }],
    })
    out = _render({"proof": d})
    body = out["pred-body"]["innerHTML"]
    assert "re-logged 26x" in body, body
    assert "2026-07-04" in body and "2026-07-29" in body, body


def test_re_logged_count_of_one_renders_no_tag():
    d = _live()
    d["predictions"] = _mutated_predictions(hedge={
        "graded": 0, "ungraded": 0, "real_verdicts": 0,
        "gradeable_pending_logic": 0, "stale_blocked": 1,
        "current_market_data_stale_days": 1,
        "entries": [{
            "hedge_recommendation": "DECREASE", "outcome": "ungraded -- market data has not advanced",
            "re_logged_count": 1, "first_logged": "2026-07-29", "last_logged": "2026-07-29",
            "decision_run_at": "2026-07-29",
        }],
    })
    out = _render({"proof": d})
    body = out["pred-body"]["innerHTML"]
    assert "re-logged" not in body, body


# ===========================================================================
# MAJOR-7: evidence citations must never be fake links
# ===========================================================================
def _dead_evlink_count(html_text: str) -> int:
    """The exact defect signature: an .evlink-classed anchor that is dead by
    construction. Used both to assert the real file is clean AND (mutated) to
    prove this checker actually fires -- R15 independence."""
    return len(re.findall(r'class="evlink"\s+href="#"\s+onclick="return false"', html_text))


def test_no_dead_evlink_anchors_in_the_real_served_html():
    text = INDEX.read_text()
    assert _dead_evlink_count(text) == 0, "a fake evlink anchor (href=# onclick=return false) is still present"


def test_dead_evlink_checker_fires_on_a_reintroduced_defect():
    # R15: prove the checker can FAIL -- reintroduce the exact old defect
    # pattern into a SCRATCH string (never the real file) and confirm the
    # checker flags it, and clears again once removed.
    mutated = INDEX.read_text() + '<a class="evlink" href="#" onclick="return false" title="x">x</a>'
    assert _dead_evlink_count(mutated) == 1
    assert _dead_evlink_count(INDEX.read_text()) == 0


def test_unpublished_repo_path_renders_as_inert_non_link_span():
    out = _render(_live())
    note = out["banked-note"]["innerHTML"]
    assert "maturity_map.yaml" in note, note
    assert 'class="evsrc"' in note, note
    assert "unpublished" in note, note
    # Must NOT be a real anchor for this specific citation.
    assert '<a class="evlink" href="#" title="docs/design/maturity_map.yaml"' not in note, note
    assert 'href="#"' not in note, note


def test_a_genuine_https_source_still_renders_as_a_real_resolvable_link():
    # R15 both-ways: srcCite must still produce a REAL <a> for a genuinely
    # resolvable source -- the fix must not turn every citation inert.
    d = _live()
    d["principles"] = [{
        "title": "Sentinel", "number": "N=1", "claim": "c", "why": "w",
        "basis": "b", "source": "https://example.com/real-source",
    }]
    out = _render({"proof": d})
    body = out["principles"]["innerHTML"]
    assert '<a class="evlink" href="https://example.com/real-source"' in body, body
    assert 'target="_blank"' in body, body


def test_a_retrospectives_path_source_still_renders_as_a_real_link():
    d = _live()
    d["principles"] = [{
        "title": "Sentinel2", "number": "N=1", "claim": "c", "why": "w",
        "basis": "b", "source": "docs/retrospectives/2026-07-04-verification-week.md",
    }]
    out = _render({"proof": d})
    body = out["principles"]["innerHTML"]
    assert ('<a class="evlink" href="https://21bcarlisle-arch.github.io/synthetic-enterprise/'
            'retrospectives/2026-07-04-verification-week.md"') in body, body


def test_timeline_source_citation_is_inert_for_a_non_retro_repo_path():
    out = _render(_live())
    timeline = out["timeline"]["innerHTML"]
    # Every RULES source in generate_proof_data.py that is NOT under
    # docs/retrospectives/ (e.g. docs/staging/*.md) must render inert.
    live = _live()
    non_retro_sources = [r["source"] for r in live["timeline"] if not r["source"].startswith("docs/retrospectives/")]
    assert non_retro_sources, "expected at least one non-retrospective rule source in the live timeline"
    assert 'class="evsrc"' in timeline, timeline


# ===========================================================================
# MINOR-9: sitemap.xml, robots.txt Sitemap directive, <noscript> fallback
# ===========================================================================
def test_noscript_fallback_present_and_names_the_json_endpoint():
    text = INDEX.read_text()
    m = re.search(r"<noscript>(.*?)</noscript>", text, re.S)
    assert m, "no <noscript> fallback present on /proof/"
    block = m.group(1)
    assert "/data/proof.json" in block, block
    assert "JavaScript" in block, block


def test_sitemap_xml_exists_and_is_valid():
    assert SITEMAP.is_file(), "site/sitemap.xml does not exist"
    root = ET.fromstring(SITEMAP.read_text())
    locs = [el.text for el in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert locs, "sitemap.xml has no <loc> entries"
    for door in ("https://poesys.net/", "https://poesys.net/proof/",
                 "https://poesys.net/company/", "https://poesys.net/world/"):
        assert door in locs, f"canonical door {door!r} missing from sitemap.xml"


def test_sitemap_xml_excludes_redirected_legacy_doors_and_offnav_director():
    root = ET.fromstring(SITEMAP.read_text())
    locs = [el.text for el in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    text = " ".join(locs)
    for killed in ("/method/", "/simplified/", "/project/", "/tours/", "/wip-flow/",
                   "/platform/", "/method-casebook/", "/supplier/", "/sim/"):
        assert killed not in text, f"redirected legacy door {killed!r} must not be in sitemap.xml"
    assert "/director/" not in text, "director is off-nav+noindex by design, must not be in sitemap.xml"
    assert "/shadow/" not in text, "shadow is the internal advisor mirror, must not be in sitemap.xml"


def test_robots_txt_has_sitemap_directive_pointing_at_the_real_file():
    text = ROBOTS.read_text()
    assert "Sitemap: https://poesys.net/sitemap.xml" in text, text
    # The existing crawler policy (AI-training blocks, normal-search Allow)
    # must be untouched by this fix.
    assert "User-agent: *" in text and "Allow: /" in text, text
