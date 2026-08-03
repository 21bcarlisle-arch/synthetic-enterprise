"""No published link may point at a URL this site 301s away (R10 class guard).

THE DEFECT THIS CLOSES
----------------------
SITE_V5 (`DIRECTOR_RULING_SITE_REBUILD_V5_STRUCTURE_2026-07-23`) folded Method,
Simplified, Journey, Tours, Platform, Casebook and WIP-flow into /proof/ and
redirected their URLs. The redirects are correct and were verified live:

    /tours/  301 -> /proof/     /platform/  301 -> /proof/
    /method/ 301 -> /proof/     /supplier/  301 -> /company/

What nobody re-checked was everything still POINTING at those URLs. The door
markup was clean, but `site/data/glossary.json` -- whose own intro promises
"Every term links to the door where you can see it working" -- still sent
**11 of its 26 terms** to a redirect, five of them to `../supplier/#ch-<chart>`
anchors that do not exist on the door the redirect lands on. Following one was a
bounce to the top of an unrelated page.

WHY A CLASS GUARD AND NOT ELEVEN EDITS (R10)
--------------------------------------------
The instance fix is repointing eleven links. The CLASS is "any future IA change
that adds a redirect silently strands every link aimed at the old URL". So the
forbidden set is DERIVED from `site/_redirects` itself, never typed here: add a
redirect tomorrow and every stale link to it fails the same day.

The second half of the class is the anchor. A link to `/company/#ch-var` is
*technically* alive -- 200, no redirect -- and still lands the reader nowhere,
because no element carries that id. Both halves are checked.

ANTI-PIN (R15)
--------------
Nothing here pins a count, a URL or a term. It asserts a relationship between two
artefacts the site already publishes (`_redirects`, the door markup) and the links
it ships. Regenerating the glossary or restructuring a door cannot make it cry
wolf; only genuinely stranding a reader can.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))
from live_pixel_verify import canonical_doors  # noqa: E402

REDIRECTS = SITE / "_redirects"
GLOSSARY = SITE / "data" / "glossary.json"

_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']')
_ID_RE = re.compile(r'id=["\']([^"\']+)["\']')


def redirect_sources() -> set[str]:
    """Every path `_redirects` 301s AWAY from, normalised to `/name`.

    Fail-closed: an unreadable or ruleless redirects file raises rather than
    yielding an empty forbidden set. A guard whose forbidden set silently empties
    passes everything -- the classic fail-open shape.
    """
    try:
        lines = REDIRECTS.read_text(encoding="utf-8").splitlines()
    except OSError as e:  # pragma: no cover - environment defect
        raise AssertionError(f"_redirects unreadable: {e}") from e
    out = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("/"):
            src = parts[0].rstrip("*").rstrip("/")
            if src and src != "/favicon.ico":
                out.add(src)
    assert out, "_redirects yielded no 301 sources -- guard would pass vacuously"
    return out


def door_file(door: str) -> Path:
    stem = door.strip("/")
    return SITE / stem / "index.html" if stem else SITE / "index.html"


def normalise(link: str) -> str:
    """A page-relative link -> the site-absolute path it resolves to."""
    path = link.split("#")[0].split("?")[0]
    path = re.sub(r"^\.\.?/", "/", path)
    return "/" + path.strip("/") if path.strip("/") else "/"


def published_links() -> list[tuple[str, str]]:
    """(source, link) for every link the canonical door set publishes -- both the
    hrefs in door markup and the `see_url`s the glossary feed renders into it."""
    links: list[tuple[str, str]] = []
    for door in canonical_doors():
        p = door_file(door)
        if p.exists():
            for h in _HREF_RE.findall(p.read_text(encoding="utf-8")):
                if not h.startswith(("http", "mailto:", "#", "data:")):
                    links.append((door, h))
    feed = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    for term in feed["terms"]:
        if term.get("see_url"):
            links.append((f"glossary.json:{term['term']}", term["see_url"]))
    assert links, "no published links discovered -- guard would pass vacuously"
    return links


# ---------------------------------------------------------------------------
def test_no_published_link_targets_a_redirected_url():
    """Half one of the class: nothing may aim at a URL we 301 away."""
    forbidden = redirect_sources()
    stranded = [
        (src, link) for src, link in published_links()
        if normalise(link) in forbidden
    ]
    assert not stranded, (
        "these published links point at URLs site/_redirects 301s away, so the "
        f"reader is bounced instead of landing: {stranded}"
    )


def test_every_published_anchor_resolves_on_its_target_door():
    """Half two: a link to `#ch-var` on a door with no such id lands nowhere.

    Only anchors into the canonical door set are checkable, which is the set that
    matters -- those are the links this site controls end to end.
    """
    door_ids: dict[str, set[str]] = {}
    for door in canonical_doors():
        p = door_file(door)
        if p.exists():
            door_ids[door] = set(_ID_RE.findall(p.read_text(encoding="utf-8")))

    dangling = []
    for src, link in published_links():
        if "#" not in link:
            continue
        frag = link.split("#", 1)[1]
        if not frag:
            continue
        target = normalise(link)
        target = target if target.endswith("/") else target + "/"
        if target not in door_ids:
            continue
        # Anchors the door's own script writes at render time are legitimate but
        # invisible to a static id scan; the glossary feed only ever targets
        # server-rendered section ids, which are.
        if frag not in door_ids[target]:
            dangling.append((src, link))
    assert not dangling, (
        f"these links target an anchor id that does not exist on the door they "
        f"land on: {dangling}"
    )


def test_glossary_promise_holds_for_every_term():
    """The feed's own intro claims 'Every term links to the door where you can
    see it working'. A claim the site publishes about itself is a testable claim."""
    feed = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    assert "links to the door" in feed["meta"]["intro"], (
        "fixture precondition: the glossary still makes this promise"
    )
    doors = set(canonical_doors())
    broken = []
    for term in feed["terms"]:
        url = term.get("see_url")
        if not url:
            broken.append((term["term"], "no see_url at all"))
            continue
        target = normalise(url)
        target = target if target.endswith("/") else target + "/"
        if target not in doors:
            broken.append((term["term"], url))
    assert not broken, f"terms whose 'see' link is not a canonical door: {broken}"


# ---------------------------------------------------------------------------
# R15 mutation proofs -- the guard must fire on its own named defect.
# ---------------------------------------------------------------------------
def test_mutation_a_link_to_a_redirected_url_is_caught():
    forbidden = redirect_sources()
    assert "/tours" in forbidden, "precondition: /tours is a live 301 source"
    assert normalise("../tours/") in forbidden, (
        "MUTATION SURVIVED: a link to the 301'd /tours/ was not recognised"
    )
    assert normalise("../proof/") not in forbidden, (
        "control is over-broad: it flags the canonical destination too"
    )


def test_mutation_a_dangling_anchor_is_caught():
    ids = set(_ID_RE.findall(door_file("/company/").read_text(encoding="utf-8")))
    assert "hedge-body" in ids, "precondition: a real anchor resolves"
    assert "ch-var" not in ids, (
        "MUTATION SURVIVED: the retired #ch-var anchor appears to exist after all"
    )


def test_mutation_empty_redirect_source_set_fails_closed():
    """FAIL-OPEN proof: if `_redirects` ever yields nothing, the guard must raise
    rather than pass everything."""
    original = REDIRECTS.read_text(encoding="utf-8")
    try:
        REDIRECTS.write_text("# all rules removed\n", encoding="utf-8")
        with pytest.raises(AssertionError, match="no 301 sources"):
            redirect_sources()
    finally:
        REDIRECTS.write_text(original, encoding="utf-8")
    assert REDIRECTS.read_text(encoding="utf-8") == original, "restore failed"
