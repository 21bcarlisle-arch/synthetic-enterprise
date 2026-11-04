"""Each section inside a page that mixes knowledge and insight is marked as one or the other
(director, 4 Nov: "A page that mixes the two marks each section"), and the marks come from the
insight rows' `section` field in site/data/knowledge_facets.json, never typed onto the page.

Each leg drives the page's own scripts, plus the shared site/knowledge/layer_marks.js inlined
where the page includes it, through the live harness against the committed feeds. The harness
only sees what scripts write, so headings a page writes in static markup (`k-sec-N`) are seeded
with their served text first, which is what a browser starts from.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
LIVE_HARNESS = SITE / "_live_harness.mjs"
MARKER = (HERE / "layer_marks.js").read_text(encoding="utf-8")
FACETS_URL = "../../data/knowledge_facets.json"
FACETS = json.loads((SITE / "data" / "knowledge_facets.json").read_text(encoding="utf-8"))
PAGES = FACETS["pages"]
MARKED = sorted(s for s, p in PAGES.items() if p["layer"] != "knowledge")
INCLUDE = '<script src="../layer_marks.js"></script>'


def _render(slug: str, facets=None) -> dict:
    html = (HERE / slug / "index.html").read_text(encoding="utf-8")
    seeds = {m.group(1): m.group(2) for m in re.finditer(r'<h2 class="sec" id="(k-sec-\d+)">([\s\S]*?)</h2>', html)}
    seed = "".join(f"document.getElementById({json.dumps(k)}).innerHTML = {json.dumps(v)};\n"
                   for k, v in seeds.items())
    html = html.replace(INCLUDE, f"<script>{MARKER}</script>").replace("<script>", f"<script>{seed}", 1)
    feeds = {u: json.loads((SITE / "data" / u.rsplit("/", 1)[1]).read_text(encoding="utf-8"))
             for u in set(re.findall(r'fetch\("(\.\./\.\./data/[^"?]+\.json)', html))
             if (SITE / "data" / u.rsplit("/", 1)[1]).exists()}
    if facets is not None:
        feeds[FACETS_URL] = facets
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
    try:
        proc = subprocess.run(["node", str(LIVE_HARNESS), f.name], input=json.dumps(feeds),
                              capture_output=True, text=True, timeout=120)
    finally:
        Path(f.name).unlink()
    assert proc.returncode == 0, proc.stderr[:600]
    out = json.loads(proc.stdout)
    assert out["_meta"]["scriptErrors"] == [], (slug, out["_meta"]["scriptErrors"])
    return out


def _marks(out: dict) -> list[str]:
    return [m for v in out.values() if isinstance(v, dict) and "innerHTML" in v
            for m in re.findall(r'<a class="layer-mark[^>]*>([^<]*)</a>', v["innerHTML"])]


def _copy() -> dict:
    return json.loads(json.dumps(FACETS))


def test_every_page_with_insight_includes_the_marker_under_its_own_name():
    assert MARKED, "the record carries no mixed or insight page"
    for slug in MARKED:
        html = (HERE / slug / "index.html").read_text(encoding="utf-8")
        assert f'{INCLUDE}\n<script>if (typeof layerMarks === "function") layerMarks("{slug}");</script>' in html, slug


def test_every_insight_row_marks_its_own_section_and_the_rest_say_knowledge():
    for slug in MARKED:
        page = PAGES[slug]
        marks = _marks(_render(slug))
        for r in page["insights"]:
            assert any(m.startswith(f"Our insight · {r['status']}") for m in marks), (slug, r["section"])
        assert not any("not placed" in m for m in marks), (slug, marks)
        assert sum(m.startswith("Our insight ·") for m in marks) == len(page["insights"]), (slug, marks)
        if page["layer"] == "mixed":
            assert "Knowledge" in marks, (slug, marks)


def test_MUTATION_a_row_naming_no_heading_is_shown_unplaced_not_dropped():
    f = _copy()
    slug = MARKED[0]
    f["pages"][slug]["insights"][0]["section"] = "A heading this page does not have"
    assert "1 insight not placed on a section" in _marks(_render(slug, f))


def test_MUTATION_a_page_reclassified_as_knowledge_carries_no_marks():
    f = _copy()
    slug = MARKED[0]
    f["pages"][slug]["layer"] = "knowledge"
    assert _marks(_render(slug, f)) == []


def test_MUTATION_a_row_past_its_review_date_says_review_overdue():
    slug = MARKED[0]
    for when, overdue in (("2020-01-01", True), ("2099-01-01", False)):
        f = _copy()
        for r in f["pages"][slug]["insights"]:
            r["review_by"] = when
        assert any(m.endswith("review overdue") for m in _marks(_render(slug, f))) is overdue, when


def test_MUTATION_FAIL_CLOSED_an_unreadable_record_says_so_on_the_page():
    slug = MARKED[0]
    marks = _marks(_render(slug, {"pages": {}}))
    assert marks == ["Knowledge or insight: the record could not be loaded"], marks
