"""The glossary is a LAYER, not just a page (SITE_CONSTITUTION migration item 8).

WHAT THE CONSTITUTION ASKED FOR
-------------------------------
Migration item 8, "Cross-cutting last-mile", lists a **glossary layer** -- listed
beside the mobile pass, i.e. a property of every door, not a door of its own. What
existed was a glossary PAGE: 26 good definitions at /glossary/ that a reader could
only use by already knowing they were there. A term used mid-sentence on /proof/
was not inspectable from /proof/.

WHAT MAKES IT A LAYER
---------------------
  L1  the definitions stay in ONE place -- `site/data/glossary.json` (binding rule
      3: the site renders, never authors). A door names a term; it never restates
      a definition in its own markup, so a definition cannot fork per door.
  L2  every term has a stable, addressable identity: `/glossary/#t-<slug>`, so any
      door -- or any external link -- can deep-link a specific definition.
  L3  a door opts in with two lines and gets in-place inspection plus that
      permalink on every marked term.

WHAT THESE TESTS ACTUALLY DRIVE (R11)
-------------------------------------
Not the source string. `_layer_harness.mjs` runs the REAL asset against a DOM and
reports what it did to the elements; the slug comparison evaluates BOTH real
implementations (the layer's and the page's inline one) and compares their output
over every term in the live feed. A comment claiming they agree is not evidence.

THE FAILURE MODE THIS IS BUILT AGAINST (R15)
--------------------------------------------
A glossary layer fails SILENTLY by nature: mistype `data-gloss`, the lookup
misses, and the term renders as ordinary text. Nothing is broken on screen; the
feature is simply absent. So the layer records misses on `unresolved` and stamps
`data-gloss-state="unresolved"` in the DOM, and the tests below assert both that
a real term resolves AND that a bogus one is reported -- a control that only ever
sees success cannot fail.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
LAYER = SITE / "assets" / "glossary-layer.js"
PAGE = SITE / "glossary" / "index.html"
HARNESS = SITE / "glossary" / "_layer_harness.mjs"
FEED = SITE / "data" / "glossary.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

sys.path.insert(0, str(SITE))


def feed() -> dict:
    return json.loads(FEED.read_text(encoding="utf-8"))


def drive(marks: list[str], data: dict | None = None) -> dict:
    """Run the real layer asset over a DOM carrying `marks` as [data-gloss]."""
    payload = {"feed": data if data is not None else feed(), "marks": marks}
    proc = subprocess.run(
        [NODE, str(HARNESS), str(LAYER), str(PAGE)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"layer harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


# --------------------------------------------------------------------------- L1
def test_the_layer_asset_holds_no_definitions_of_its_own():
    """L1: the asset is machinery, not content. If a definition were inlined here
    it would silently outrank the feed and the site would be authoring, not
    rendering (binding rule 3)."""
    src = LAYER.read_text(encoding="utf-8")
    for term in feed()["terms"]:
        assert term["definition"][:50] not in src, (
            f"the layer asset restates the definition of {term['term']} -- "
            "definitions live in site/data/glossary.json only"
        )


# --------------------------------------------------------------------------- L2
def test_slug_contract_matches_between_page_and_layer():
    """L2, and the reason the duplication is safe: both real implementations are
    evaluated and compared over every live term. Edit one, this goes red."""
    out = drive([])
    mismatched = {
        t: (out["slugs"][t], out["pageSlugs"][t])
        for t in out["slugs"] if out["slugs"][t] != out["pageSlugs"][t]
    }
    assert not mismatched, (
        f"slug contract has drifted between site/assets/glossary-layer.js and "
        f"site/glossary/index.html: {mismatched}"
    )


def test_every_term_gets_a_distinct_non_empty_anchor():
    """A collision would make two terms share one permalink, so a deep link would
    land on whichever rendered last."""
    out = drive([])
    slugs = out["slugs"]
    assert all(v and v != "t-" for v in slugs.values()), "a term produced an empty slug"
    dupes = {v for v in slugs.values() if list(slugs.values()).count(v) > 1}
    assert not dupes, f"slug collisions: {dupes}"


def test_the_glossary_page_renders_the_anchor_ids_the_layer_links_to():
    """L2 end to end (R11): the page must actually PUT those ids on the cards, or
    every cross-door deep link lands at the top of an unstyled list. Driven
    through the page's own render harness, so this is the rendered pixel."""
    render = subprocess.run(
        [NODE, str(SITE / "glossary" / "_render_harness.mjs"), str(PAGE)],
        input=json.dumps(feed()), capture_output=True, text=True, timeout=60,
    )
    assert render.returncode == 0, render.stderr
    html = json.loads(render.stdout)["glist"]["innerHTML"]
    slugs = drive([])["slugs"]
    missing = [t for t, s in slugs.items() if f'id="{s}"' not in html]
    assert not missing, f"terms rendered with no anchor id: {missing}"


# --------------------------------------------------------------------------- L3
def test_a_marked_term_resolves_to_a_permalink_and_its_definition():
    """L3: the layer's actual output on a real term, read off the element."""
    term = feed()["terms"][0]
    out = drive([term["term"]])
    assert out["unresolved"] == [], out["unresolved"]
    el = out["elements"][0]
    assert el["attrs"]["data-gloss-state"] == "resolved"
    assert el["attrs"]["data-gloss-href"] == "../glossary/#" + out["slugs"][term["term"]]
    assert term["definition"][:40] in el["attrs"]["title"], (
        "the definition did not reach the element's title -- nothing is inspectable"
    )
    assert "gloss-term" in el["classes"]


def test_an_abbreviation_resolves_to_its_full_term():
    """Doors write `SSP` in prose, not `System Sell Price`. If abbreviations did
    not resolve, the layer would miss most real usage."""
    abbr_term = next(t for t in feed()["terms"] if t.get("abbr"))
    out = drive([abbr_term["abbr"]])
    assert out["unresolved"] == [], f"abbreviation {abbr_term['abbr']} did not resolve"
    assert out["elements"][0]["attrs"]["data-gloss-href"].endswith(
        out["slugs"][abbr_term["term"]]
    ), "an abbreviation resolved to the wrong term's permalink"


def test_every_glossed_term_on_every_door_resolves():
    """The class guard for adoption (R10): a `data-gloss` typo ANYWHERE in the
    canonical door set is caught here, not by a reader noticing a word stopped
    being clickable.

    Scanning the doors rather than a list of known adopters means a door that
    adopts the layer tomorrow is covered on the day it does, with no list to
    update -- the same inversion `site/test_brand_token_adoption.py` applies to
    the brand frontier.
    """
    import re

    from live_pixel_verify import canonical_doors

    marks: list[tuple[str, str]] = []
    for door in canonical_doors():
        stem = door.strip("/")
        p = (SITE / stem / "index.html") if stem else (SITE / "index.html")
        if not p.exists():
            continue
        for m in re.findall(r'data-gloss="([^"]+)"', p.read_text(encoding="utf-8")):
            marks.append((door, m))

    assert marks, (
        "no door marks up any glossary term -- the layer is built but adopted "
        "nowhere, so this guard would pass vacuously"
    )

    # Un-escape the one HTML entity the doors legitimately use inside the attribute.
    names = [m.replace("&amp;", "&") for _, m in marks]
    out = drive(names)
    assert out["unresolved"] == [], (
        f"these doors mark up terms that are not in site/data/glossary.json: "
        f"{[(d, m) for (d, m), n in zip(marks, names) if n in out['unresolved']]}"
    )


def test_mutation_a_typo_in_a_door_would_be_caught():
    """R15 for the guard above: prove it fires on the defect it names."""
    out = drive(["PROVISIONAL", "PROVISIONNAL"])
    assert out["unresolved"] == ["PROVISIONNAL"], (
        "MUTATION SURVIVED: a mistyped data-gloss on a door was not reported"
    )


def test_the_recorded_permalink_actually_navigates():
    """R11's no-orphan-transitions clause: `data-gloss-href` is only real if
    something acts on it. The layer's delegated click handler is invoked here for
    real and `location` must end up at the term's permalink -- a flag whose
    release triggers nothing is a defect, not a feature."""
    term = feed()["terms"][0]
    out = drive([term["term"]])
    expected = "../glossary/#" + out["slugs"][term["term"]]
    assert out["clickReturned"] == expected, (
        f"clicking a glossed term returned {out['clickReturned']!r}, not the permalink"
    )
    assert out["locationAfterClick"] == expected, (
        "the permalink was recorded but clicking it navigated nowhere -- "
        "an orphan transition (R11)"
    )


def test_an_unresolved_term_navigates_nowhere():
    """The other half: a term the layer could not resolve must not become a
    clickable link to a dead anchor. Silence here is correct; a wrong destination
    is not."""
    out = drive(["Sytem Sel Price"])
    assert out["clickReturned"] is None, (
        "an unresolved term produced a navigation target"
    )
    assert out["locationAfterClick"] == "https://poesys.net/proof/", (
        "an unresolved term navigated the reader away"
    )


# ------------------------------------------------------- R15: it must FAIL loud
def test_mutation_an_unknown_term_is_reported_not_swallowed():
    """THE named defect: a mistyped `data-gloss` must be loud, not invisible."""
    out = drive(["Sytem Sel Price"])
    assert out["unresolved"] == ["Sytem Sel Price"], (
        "MUTATION SURVIVED: an unresolvable term was silently left as plain text. "
        "A layer whose misses are invisible is worse than no layer."
    )
    assert out["elements"][0]["attrs"]["data-gloss-state"] == "unresolved"
    assert "data-gloss-href" not in out["elements"][0]["attrs"]


def test_mutation_a_renamed_term_breaks_its_permalink():
    """Independence: the permalink is DERIVED from the feed, not hard-coded. Rename
    a term in the data and the anchor must follow."""
    data = feed()
    original = data["terms"][0]["term"]
    data["terms"][0]["term"] = "Mutated Sentinel Term"
    out = drive(["Mutated Sentinel Term"], data)
    assert out["unresolved"] == []
    assert out["elements"][0]["attrs"]["data-gloss-href"] == (
        "../glossary/#t-mutated-sentinel-term"
    ), "the permalink did not follow the mutated source term"
    assert original not in out["elements"][0]["attrs"].get("title", "")


def test_mutation_a_definition_edit_reaches_the_element():
    """R15 independence for the inspection text: the title is read from the feed
    at render time, never baked into the asset."""
    data = feed()
    sentinel = "ZZ_LAYER_DEFINITION_SENTINEL_ZZ"
    data["terms"][0]["definition"] = sentinel
    out = drive([data["terms"][0]["term"]], data)
    assert sentinel in out["elements"][0]["attrs"]["title"], (
        "MUTATION SURVIVED: the element's definition is not sourced from the feed"
    )
