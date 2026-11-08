#!/usr/bin/env python3
"""The Knowledge tab is ONE classification: three parts read from the record, the themes under them,
and "Building it" read from the map's own register (director's steer of 5 Nov, item 2, brought
forward by his 8 Nov ruling: "use tokens this week on site").

THE DEFECT THIS FIRES ON. Before the reshape the tab grouped pages into six themes while the map
grouped the same pages into four spines -- two classifications of one set, the several-homes class
in our own filing -- and engineering practice had no home on the tab at all. So:

  * PARTS -- the page's three parts, their headings and the themes under each are the record's
    `parts`, in order, and every theme sits in exactly one part.
  * BUILDING IT -- its cards are the register's `build` concepts (docs/design/the_map/concepts.yaml),
    label and definition quoted, each linking to that concept's panel on the map. A concept added to
    the register and missing here, or a card the register does not have, fails.
  * CARBON is a filter, not a section: the cards marked for it are exactly those whose own quoted
    title, blurb or why line names carbon, and no theme is called Carbon.
  * WHAT WE'VE LEARNED needs the facet record's layer on each card, so every topic card must carry
    the layer slot the script reads it from.
"""
from __future__ import annotations

import html as htmllib
import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent
INDEX = SITE / "knowledge" / "index.html"
RECORD = SITE / "data" / "knowledge_wholesale.json"
REGISTER = ROOT / "docs" / "design" / "the_map" / "concepts.yaml"

_PART_OPEN = re.compile(r'<section class="part" id="part-(?P<id>[^"]+)" data-part="(?P=id)">\s*'
                        r'<h2 class="part-h">(?P<h>.*?)</h2>\s*<p class="part-why">(?P<why>.*?)</p>', re.S)
_THEME_OPEN = re.compile(r'<section class="theme" id="theme-(?P<id>[^"]+)"')
_TOPIC_CARD = re.compile(r'<a class="card" href="\./(?P<slug>[^"/]+)/"(?P<attrs>[^>]*)>(?P<body>.*?)</a>', re.S)
_PRACTICE_CARD = re.compile(
    r'<a class="card practice" href="\.\./model/map/#c-(?P<id>[^"]+)" data-concept="(?P=id)">\s*'
    r'<div class="card-h">(?P<h>.*?)</div>\s*<div class="card-p">(?P<p>.*?)</div>', re.S)
CARBON = re.compile(r"carbon|CO2", re.I)


@pytest.fixture(scope="module")
def markup() -> str:
    return INDEX.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def build_concepts() -> list[dict]:
    reg = yaml.safe_load(REGISTER.read_text(encoding="utf-8"))
    return [c for c in reg["concepts"] if any(p.split("/")[0] == "build" for p in c.get("placed", []))]


def _layout(markup: str) -> list[dict]:
    """Each part in page order with the themes that open after it and before the next part."""
    parts = [{"id": m.group("id"), "title": htmllib.unescape(m.group("h")),
              "why": htmllib.unescape(m.group("why")), "at": m.start(), "themes": []}
             for m in _PART_OPEN.finditer(markup)]
    for t in _THEME_OPEN.finditer(markup):
        owner = [p for p in parts if p["at"] < t.start()]
        if owner:
            owner[-1]["themes"].append(t.group("id"))
        else:
            parts.append({"id": None, "themes": [t.group("id")], "at": t.start()})
    return parts


def _part_drift(record: dict, markup: str) -> list[str]:
    got = _layout(markup)
    bad = []
    if [p["id"] for p in got] != [p["id"] for p in record.get("parts", [])]:
        bad.append(f"parts {[p['id'] for p in got]} != record {[p['id'] for p in record.get('parts', [])]}")
    for want, have in zip(record.get("parts", []), got):
        if (have.get("title"), have.get("why")) != (want["title"], want["why"]):
            bad.append(f"part {want['id']} heading or line differs from the record")
        if have["themes"] != want["themes"]:
            bad.append(f"part {want['id']} holds themes {have['themes']} != record {want['themes']}")
    placed = [t for p in record.get("parts", []) for t in p["themes"]]
    if sorted(placed) != sorted(t["id"] for t in record["themes"]) or len(placed) != len(set(placed)):
        bad.append(f"the record's parts place themes {placed}, not each of {[t['id'] for t in record['themes']]} once")
    return bad


def test_the_tab_has_three_parts_and_each_theme_sits_in_one(record, markup):
    assert [p["id"] for p in record["parts"]] == ["world", "supplier", "build"]
    assert not _part_drift(record, markup), _part_drift(record, markup)


def test_MUTATION_a_theme_moved_between_parts_is_caught(record, markup):
    moved = json.loads(json.dumps(record))
    moved["parts"][0]["themes"].remove("households")
    moved["parts"][1]["themes"].append("households")
    assert any("holds themes" in b for b in _part_drift(moved, markup))
    lost = json.loads(json.dumps(record))
    lost["parts"][0]["themes"].remove("other-markets")
    assert any("not each of" in b for b in _part_drift(lost, markup))


def _practice_drift(build: list[dict], markup: str) -> list[str]:
    part = markup[markup.index('id="part-build"'):]
    cards = [(m.group("id"), htmllib.unescape(m.group("h")), htmllib.unescape(m.group("p")))
             for m in _PRACTICE_CARD.finditer(part)]
    want = [(c["id"], c["prefLabel"], c["definition"]) for c in build]
    return [] if cards == want else [f"Building it shows {cards}, register says {want}"]


def test_building_it_is_the_registers_build_spine(build_concepts, markup):
    assert build_concepts, "the register has no build concepts; Building it would be read from nothing"
    assert not _practice_drift(build_concepts, markup), _practice_drift(build_concepts, markup)
    mapped = (SITE / "model" / "map" / "index.html").read_text(encoding="utf-8")
    for c in build_concepts:
        assert f'id="c-{c["id"]}"' in mapped, f"the map page has no panel #c-{c['id']} for its card to land on"


def test_MUTATION_a_concept_added_to_the_register_is_missing_from_building_it(build_concepts, markup):
    extra = build_concepts + [{"id": "build.new", "prefLabel": "New", "definition": "A new practice."}]
    assert _practice_drift(extra, markup)


def _carbon_drift(record: dict, markup: str) -> list[str]:
    marked = {m.group("slug") for m in _TOPIC_CARD.finditer(markup) if 'data-carbon="1"' in m.group("attrs")}
    named = {t["id"] for t in record["topics"]
             if CARBON.search(" ".join([t["title"], t.get("blurb", ""), t.get("why", "")]))}
    return [] if marked == named else [f"carbon filter marks {sorted(marked)}, the record names carbon on {sorted(named)}"]


def test_carbon_is_a_filter_over_every_part_not_a_section(record, markup):
    assert "carbon" not in {t["id"] for t in record["themes"]}, "Carbon is a theme again"
    assert not _carbon_drift(record, markup), _carbon_drift(record, markup)
    by_theme = {t["id"]: t["theme"] for t in record["topics"]}
    marked = [m.group("slug") for m in _TOPIC_CARD.finditer(markup) if 'data-carbon="1"' in m.group("attrs")]
    assert len({by_theme[s] for s in marked}) > 1, "the carbon filter covers one theme only, so it is a section by another name"


def test_MUTATION_a_carbon_card_left_unmarked_is_caught(record, markup):
    stripped = markup.replace('data-carbon="1"', "", 1)
    assert _carbon_drift(record, stripped)


def test_every_topic_card_carries_the_layer_slot_the_learned_filter_reads(record, markup):
    cards = {m.group("slug"): m.group("body") for m in _TOPIC_CARD.finditer(markup)}
    missing = [t["id"] for t in record["topics"] if f'id="layer-{t["id"]}"' not in cards.get(t["id"], "")]
    assert not missing, f"cards with no layer slot inside them, invisible to What we've learned: {missing}"
    facets = json.loads((SITE / "data" / "knowledge_facets.json").read_text(encoding="utf-8"))["pages"]
    learned = [s for s, f in facets.items() if f.get("layer") in ("insight", "mixed")]
    assert learned, "no page is insight or mixed, so the learned filter can never show anything"


def test_the_filter_script_parses(markup):
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", markup)
    js = "\n".join(scripts)
    assert "function applyFilter(" in js
    proc = subprocess.run(["node", "--check", "--input-type=commonjs", "-"], input=js,
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[:400]
