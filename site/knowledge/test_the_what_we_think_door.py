"""The five facets reach the reader: a layer label on every Knowledge card, and every insight
published and filterable on "What we think, and how sure we are" (director, 4 Nov: "Publish
insights. Don't hold back"; "Let the site filter by any facet").

Each leg drives the page's own JavaScript against the committed facet record through the live
harness. Expected values are computed here from the record, never typed.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
PAGE = HERE / "what-we-think.html"
INDEX = HERE / "index.html"
LIVE_HARNESS = SITE / "_live_harness.mjs"
FACETS_URL = "../data/knowledge_facets.json"
TOPICS_URL = "../data/knowledge_wholesale.json"
FACETS = json.loads((SITE / "data" / "knowledge_facets.json").read_text(encoding="utf-8"))
TOPICS = json.loads((SITE / "data" / "knowledge_wholesale.json").read_text(encoding="utf-8"))
PAGES = FACETS["pages"]
ROWS = sum(len(p["insights"]) for p in PAGES.values())


def _render(html: Path, feeds: dict, hash_: str = "") -> dict:
    proc = subprocess.run(["node", str(LIVE_HARNESS), str(html), hash_], input=json.dumps(feeds),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[:600]
    out = json.loads(proc.stdout)
    assert out["_meta"]["scriptErrors"] == [], out["_meta"]["scriptErrors"]
    return out


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _both(facets=None) -> dict:
    return {FACETS_URL: facets if facets is not None else FACETS, TOPICS_URL: TOPICS}


def _counts(out: dict) -> str:
    return out["facet-counts"]["textContent"]


def test_unfiltered_the_page_publishes_every_page_and_every_insight():
    out = _render(PAGE, _both())
    assert f"{len(PAGES)} of {len(PAGES)} pages and {ROWS} of {ROWS} insights" in _counts(out)
    assert out["facet-insights"]["innerHTML"].count("<tr>") == ROWS + 1
    assert out["facet-pages"]["innerHTML"].count("<tr>") == len(PAGES) + 1


def test_every_filter_on_the_page_can_both_admit_and_exclude():
    """The partition control: each worked example selects something, and not everything. A
    filter that admits all or nothing would pass every leg below that reads only its members."""
    for hash_ in ("#domain=customer_needs_and_behaviour", "#status=hypothesis",
                  "#reads=world&grade=below_dp", "#status=refuted", "#sim=yes", "#layer=insight"):
        text = _counts(_render(PAGE, _both(), hash_))
        pages, rows = int(text.split(" of ")[0]), int(text.split(" and ")[1].split(" of ")[0])
        assert 0 < pages < len(PAGES) and 0 < rows < ROWS, (hash_, text)


def test_below_dp_world_reads_are_exactly_the_records_pages():
    out = _render(PAGE, _both(), "#reads=world&grade=below_dp")
    want = sorted(s for s, p in PAGES.items() if p["trust"]["grade_floor"] in ("S", "A")
                  and any(u.startswith("world:") for u in p["use"]))
    html = out["facet-pages"]["innerHTML"]
    got = sorted(seg.split('/">')[0] for seg in html.split('<tr><td><a href="./')[1:])
    assert got == want


def test_a_refuted_insight_stays_visible_struck_through_with_what_refuted_it():
    refuted = [r for p in PAGES.values() for r in p["insights"] if r["status"] == "refuted"]
    assert refuted, "the record carries no refuted insight to show"
    html = _render(PAGE, _both(), "#status=refuted")["facet-insights"]["innerHTML"]
    for r in refuted:
        assert f'<td class="st-refuted">{_esc(r["claim"])}' in html, r["claim"]
        assert _esc(r["falsified_by"]) in html


def test_MUTATION_a_planted_sim_insight_is_published_and_marked_as_ours():
    f = json.loads(json.dumps(FACETS))
    slug = next(s for s, p in f["pages"].items() if p["layer"] == "knowledge")
    f["pages"][slug]["insights"].append({
        "claim": "PLANTED sim insight", "section": "x", "status": "hypothesis", "rests_on": ["run"],
        "from_sim": True, "falsified_by": "y", "checked": "2026-11-04", "review_by": "2027-02-01",
        "use": []})
    html = _render(PAGE, _both(f), "#sim=yes")["facet-insights"]["innerHTML"]
    assert "PLANTED sim insight <span class=\"layer-badge layer-insight\">From our simulation</span>" in html


def test_the_index_labels_every_card_with_its_layer_and_follows_the_record():
    out = _render(INDEX, _both())
    names = {"knowledge": "Knowledge", "insight": "Insight", "mixed": "Knowledge + insight"}
    for slug, p in PAGES.items():
        assert out[f"layer-{slug}"]["textContent"] == names[p["layer"]], slug
    f = json.loads(json.dumps(FACETS))
    slug = next(s for s, p in f["pages"].items() if p["layer"] == "knowledge")
    f["pages"][slug]["layer"] = "insight"
    assert _render(INDEX, _both(f))[f"layer-{slug}"]["textContent"] == "Insight"


def test_MUTATION_FAIL_CLOSED_an_unreadable_facet_record_says_so_on_both_surfaces():
    page = _render(PAGE, {TOPICS_URL: TOPICS})
    assert "could not be loaded" in _counts(page)
    assert not (page.get("facet-insights") or {}).get("innerHTML", "").strip()
    index = _render(INDEX, {TOPICS_URL: TOPICS})
    assert "could not be loaded" in index["layer-note"]["textContent"]
    assert not any(v["textContent"] for k, v in index.items()
                   if k.startswith("layer-") and k != "layer-note")
