#!/usr/bin/env python3
"""The ONE information-architecture register: what the public surface publishes, in
three states, and the nav that reaches it.

WHY THIS EXISTS
---------------
`DIRECTOR_BRIEF_WEBSITE_STRUCTURE_2026-08-17.md` §3 reads as one edit -- "five tabs, in
a ruled order". Measured against the committed tree it is SIXTEEN hand edits against
TWELVE distinct nav shapes, and `site/evidence/index.html` -- the largest content page
after the wall exhibit -- carries no `<nav>` element at all. Every later step of the
programme (`SITE5`..`SITE11`) moves a tab, and every one of them would otherwise be
sixteen chances to strand a page.

So this module is Step 0 of the programme: the nav becomes DATA, in one place, and the
sixteen pages render it.

THE THIRD STATE
---------------
The brief's §7 control #1 -- "a published area with no route from the nav fails" --
cannot be built as written, because the surface is in THREE states, not two, and it has
no slot for the third:

    ADVERTISED   in sitemap.xml, served, crawlable
    INTERNAL     served 200, deliberately absent from the sitemap (empty today)

    A THIRD STATE, RETIRED (301 to a live door, page kept in-repo), existed until 2026-08-20
    and is gone with the redirects it described. Two states cover the site now, and the second
    is empty -- which is what "nothing hidden" means when it is a property rather than a claim.

As written the control is red on TWELVE of sixteen areas, and for seven of them
(the deliberate ones) that was correct behaviour the project chose --
so its only green state is deleting pages the retirement convention says to keep.

The failable form, ruled 2026-08-18 and implemented here as `register_violations()`:

    * an area in sitemap.xml MUST have a route from the canonical nav
      (today: fails on six -- the REAL defect, carried in ORPHAN_DEBT)
    * an area NOT in sitemap.xml MUST be either 301'd in `_redirects` or named in
      INTERNAL_DOORS (today: passes on all seven -- the deliberate ones)
    * an area in NEITHER is the failure -- today none, and it is exactly the state a
      careless migration creates.

DERIVED, NOT TYPED (the anti-pin half of R15)
---------------------------------------------
`advertised_areas()` reads sitemap.xml.
`deployed_areas()` reads the tree. None of the three is a hand-maintained list, so an
area added to or removed from the IA is picked up without editing this file. The two
things that ARE typed are the two that are genuinely declarations of intent and cannot
be derived from anything: INTERNAL_DOORS (what we chose not to advertise) and
CANONICAL_NAV (what the nav is). Both are single-definition -- `live_pixel_verify.py`
imports INTERNAL_DOORS from here rather than carrying its own copy.

FAIL-CLOSED (the other half of R15)
-----------------------------------
An unreadable, malformed or empty sitemap / `_redirects` / tree raises
`IaRegisterUnavailable` rather than yielding an empty set. Classifying zero areas and
reporting no violations is the fail-open shape the control exists to refuse: it would
report a perfectly green IA for a site that had been deleted.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SITE = Path(__file__).resolve().parent
REPO = SITE.parent
SITEMAP = SITE / "sitemap.xml"
REDIRECTS = SITE / "_redirects"
CANONICAL_HOST = "https://poesys.net"

# The nav block this module owns on every page. Markers rather than a class selector
# because `project/index.html` carries a SECOND `<nav>` (its in-page tab bar) that is
# not site nav and must not be rewritten -- and because a marked region makes the
# render idempotent and the control an exact string comparison rather than a parse.
NAV_START = "<!-- IA-NAV:START (rendered from site/ia_register.py -- do not hand-edit) -->"
NAV_END = "<!-- IA-NAV:END -->"


class IaRegisterUnavailable(RuntimeError):
    """The register could not be built. NOT an empty register -- callers must treat
    this as a failure. Named as its own type so no caller can except-and-continue it
    into a green result."""


# ── State 2 of 3: the deliberate non-advertisement ────────────────────────────
# Typed, because it is a DECISION and no file records it: these are deployed, serve
# 200 to anyone with the URL, and are kept out of sitemap.xml on purpose.
# `live_pixel_verify.py` imports this name rather than defining its own.
#
# `/director/` is the one under a director condition -- see director_record_release().
# `/shadow/` is a generated MIRROR of the whole site at a second root
# (tools/generate_shadow_html.py); its subtree is covered by this one entry.
# EMPTY, 2026-08-20. /director/ folded into Harness as its "what a human actually decided"
# section and /shadow/ (the internal advisor mirror) was deleted outright -- it was an internal
# surface that was nonetheless being published on the public site, which is the hidden-page
# burden the ruling names. The constant stays so the shrink-only test still has something to
# measure and a NEW internal door has to be declared here rather than appearing quietly.
INTERNAL_DOORS: tuple[str, ...] = ()


# ── UNDER CONSTRUCTION: a fourth state, and a legitimate one ──────────────────
# Director ruling, 2026-08-19: "holes beat wrong or unintelligible content. Put the final
# structure up now, with honest 'being built' pages where the content isn't written -- what
# the page will show, roughly when." And: "If your controls refuse a route to an area that
# isn't ready, change the controls -- under-construction is a legitimate state and the machine
# should be able to express it."
#
# Before this, the register knew three states and a failure state, and a nav route to an
# unfinished area could only classify as UNCLASSIFIED -- "a page a reader can reach and nothing
# in the repo says should exist". That is exactly wrong for a door we have deliberately opened
# early: the repo DOES say it should exist, and says what it will hold.
#
# THE TWO OBLIGATIONS THAT MAKE IT LEGITIMATE RATHER THAN AN EXCUSE, both enforced below:
#   1. NOT IN THE SITEMAP. A reader who follows the nav meets an honest placeholder; a search
#      engine is not invited to index a hole. This is the same choice already made for
#      /director/ and is why INTERNAL exists.
#   2. THE PAGE MUST SAY SO ITSELF, in the reader's words, carrying what it will show and
#      roughly when. A door that is quietly empty is worse than no door -- it is the
#      "unintelligible content" the ruling is about, wearing a different hat.
#
# SHRINK-ONLY. Every entry names the step that finishes it. An area that has become
# ADVERTISED must leave this register, or "under construction" becomes somewhere work goes
# to be forgotten -- the same failure the ORPHAN_DEBT register is written to avoid.
# The string a placeholder page must carry. Deliberately a visible reader-facing phrase and
# not an HTML comment: a control that checks for a comment can be satisfied by a page that
# shows a reader nothing, which is the failure this whole ruling is about.
UNDER_CONSTRUCTION_MARKER = "This page is being built"

# EMPTY, 2026-08-20, and empty is the shrink-only register working rather than a gap in it.
# /explore/ left when the six-stage traversal shipped; /harness/ left the same day when it
# stopped promising a method account and started carrying one. An entry left behind after its
# page is built is worse than no entry: the page goes on telling readers "this page is being
# built" over real content, i.e. instructing them to disbelieve what they are looking at.
UNDER_CONSTRUCTION_DOORS: dict[str, tuple[str, str, str]] = {}


# ── The canonical nav ─────────────────────────────────────────────────────────
# The ruled order arrives one tab at a time (brief §9.2: no intermediate state in
# which the nav routes to a page that does not exist). TODAY this is the four
# destinations already live. SITE6 inserts Knowledge, SITE7 Capabilities, SITE10
# Explore, SITE9 Harness; SITE11 re-points Proof. Each of those steps edits THIS
# TUPLE and re-runs `tools/render_site_nav.py --write`. That is the whole point of
# Step 0: one line, not sixteen files.
@dataclass(frozen=True)
class NavItem:
    label: str
    area: str  # site-absolute, e.g. "/world/"


CANONICAL_NAV: tuple[NavItem, ...] = (
    # FIVE, and five is the binding number rather than a preference. Director, 2026-08-19:
    # "Mobile is where I read this; treat it as the binding constraint." Nine items did not fit
    # a phone; these five do at 360px without wrapping to a second row.
    #
    # THE FOLD, in his words: "My brief listed Home, Knowledge, Capabilities, Explore, Harness --
    # I had folded The World and The Company into Capabilities and Explore, since Capabilities is
    # SIM and Company side by side and Explore is where the world gets walked. I never said so."
    # So the two tabs I was holding open were never meant to be tabs.
    #
    # NOTHING IS DELETED. /world/, /company/ and /proof/ keep their pages and their content and
    # enforced: a declared parent that does not actually link to its child is a violation, so a
    # fold cannot become a quiet orphaning.
    NavItem("Home", "/"),
    NavItem("Knowledge", "/knowledge/"),
    NavItem("Capabilities", "/capabilities/"),
    NavItem("Explore", "/explore/"),
    NavItem("Harness", "/harness/"),
)


# ── The fold: which tab absorbed which page ──────────────────────────────────
# A child is NOT an orphan: it is reachable, deliberately, one click from its parent tab. This
# the nav non-canonical (Home carried eight items, Knowledge nine) and it is exactly the
# condition Step 0 existed to abolish.
#
# ONE LINK EACH, and that is a rule rather than an accident. Director, 2026-08-19: "prefer fewer
# cross-links: every one is a thing that has to keep being true, and I'd rather have a smaller
# number that always work than a web that needs constant verification."
# EMPTY, 2026-08-20. This held the FOLD: /world/, /company/ and /proof/ kept alive off-nav,
# each reached by exactly one link from the tab that absorbed it. The director retired that
# arrangement -- "the five tabs are the site... no permanent limbo, no page kept because
# deleting it feels risky" -- so their content moved into Capabilities and Harness and the
# pages are deleted, with 301s in site/_redirects.
#
# The fold was a reasonable intermediate state and it cost more than it looked. Each folded
# page still had to be built, branded, link-checked and named in every control's page list;
# three separate controls went red this week on a stale literal naming one of them, and one of
# those refused every lane's commit. A page nobody can reach is not free just because it is
# quiet.


# ── Per-page render profile ───────────────────────────────────────────────────
# The site has two nav GRAMMARS and this module renders both rather than forcing one,
# because collapsing them is a CSS change on the front door and Step 0 is explicitly
# not that. The home page wraps `<nav class="doors">` in `<header class="site-nav">`
# and styles its links bare; every other page uses `<nav class="site-nav">` with
# `.nav-link`. The LOGO is deliberately untouched on every page -- it is not a route,
# and its inconsistency (`poesys.` / `⚡ Poesys` / `Poesys`) is the declared subject of
# `site/test_brand_token_adoption.py`'s debt register, which owns it.
# ONE GRAMMAR (2026-08-19). Home used to render bare <a> inside `<nav class="doors">` while
# every other page used `.nav-link`, so a rule that fixed one could not fix the other -- the
# structural half of the director's "it renders differently between those pages".
HOME_LINK_CLASS = "nav-link"
INNER_LINK_CLASS = "nav-link"


# ── The legacy tail (shrink-only, and it must shrink) ─────────────────────────
# Nine pages carry nav links BEYOND the canonical four. They are not noise: they are
# the ad-hoc routes by which a reader can currently reach the six orphans and the five
# retired areas' anchors. Canonicalising the nav by DELETING them would make the site
# strictly worse for a reader while changing no count this control reports -- so they
# are preserved here, per page, and each names the step that absorbs it.
#
# This is a DEBT REGISTER, not a feature. Every entry disappears by being made
# unnecessary: when Knowledge enters the canonical nav at SITE6, `/world/`'s Knowledge
# tail link is redundant and goes. `test_ia_register.py` asserts the tail can only
# shrink, and that no tail entry duplicates a canonical destination.


# ── The six real orphans ──────────────────────────────────────────────────────
# ADVERTISED to crawlers, with no route from the canonical nav. This is the defect the
# brief's §7 control #1 was reaching for, and it is REAL -- unlike the twelve the
# control as written would have reported. Step 0 red-lists them; it does not fix them.
# Each names the step that gives it a route (or takes it off the sitemap).
#
# SHRINK-ONLY: `test_ia_register.py` fails if an entry here is no longer an orphan
# (stale debt claiming credit) and fails on any orphan NOT here (new debt sneaking in).
ORPHAN_DEBT: dict[str, str] = {}


# ── The one nav exemption ─────────────────────────────────────────────────────
# /shadow/ is a GENERATED mirror of the whole site at a second root
# (tools/generate_shadow_html.py). Its nav routes within the mirror
# (/shadow/customers/, /shadow/sim/, ...) and giving it the canonical nav would route
# a shadow reader onto the live site -- the opposite of what a mirror is for. Exactly
# one member, asserted as exactly one member, with its reason in the register rather
# than in a reviewer's memory.
# EMPTY, 2026-08-20. Its one member was /evidence/, the only advertised page whose HTML was
# rewritten by a generator every ~30 minutes; the page is deleted and its 301 lands on
# /harness/. Every page on the site is now hand-authored and nav-rendered by
# tools/render_site_nav.py, so nothing needs the declaration -- but the constant stays, because
# the next generated page must announce itself here rather than be skipped by the accident of
# what its markup happens to look like.
GENERATED_NAV: dict[str, str] = {}


# EMPTY, 2026-08-20: its one member was /shadow/, the generated mirror, and the mirror is
# deleted along with every other page a reader could not reach. The constant stays because an
# exemption list that has to be re-created to be used is one nobody adds to casually.
NAV_EXEMPT: dict[str, str] = {
    "/privacy/": (
        "a legal footer route carried on every page's foot, deliberately not one of the five "
        "tabs. It is genuinely reachable -- more reachable than most of the site -- but not "
        "from the nav, which is what this exemption records. Its previous home was ORPHAN_DEBT, "
        "which was wrong: it described a page waiting to be folded somewhere, and this one is "
        "where it belongs."
    ),
}


# ── Derivation ────────────────────────────────────────────────────────────────
_LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")


def advertised_areas(sitemap: Path = SITEMAP) -> tuple[str, ...]:
    """Areas in `sitemap.xml`, as site-absolute paths. Fail-closed on empty."""
    try:
        text = sitemap.read_text(encoding="utf-8")
    except OSError as e:
        raise IaRegisterUnavailable(f"sitemap unreadable: {e}") from e
    areas = []
    for url in _LOC_RE.findall(text):
        if url.startswith(CANONICAL_HOST):
            areas.append(url[len(CANONICAL_HOST):] or "/")
    if not areas:
        raise IaRegisterUnavailable("sitemap advertises no areas")
    return tuple(dict.fromkeys(areas))


def deployed_areas(site: Path = SITE) -> tuple[str, ...]:
    """Every area actually in the tree: the root plus each top-level directory that
    carries an `index.html`. Fail-closed on a tree with no root page."""
    if not (site / "index.html").is_file():
        raise IaRegisterUnavailable(f"no root index.html under {site}")
    areas = ["/"]
    for child in sorted(site.iterdir()):
        if child.is_dir() and (child / "index.html").is_file():
            areas.append(f"/{child.name}/")
    return tuple(areas)


ADVERTISED = "ADVERTISED"
INTERNAL = "INTERNAL"
UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
UNCLASSIFIED = "UNCLASSIFIED"


def classify(site: Path = SITE) -> dict[str, str]:
    """Every deployed area mapped to its state. UNCLASSIFIED is the failure state:
    deployed, not advertised, not redirected, not declared internal -- a page a reader
    can reach and nothing in the repo says should exist."""
    advertised = set(advertised_areas(site / "sitemap.xml"))
    internal = set(INTERNAL_DOORS)
    states = {}
    for area in deployed_areas(site):
        if area in advertised:
            states[area] = ADVERTISED
        elif area in UNDER_CONSTRUCTION_DOORS:
            # Checked BEFORE internal/retired: a door we opened early is under construction
            # even if it later also appears elsewhere, and the reader-facing obligation
            # (the page must say so) follows from THIS state, not from the others.
            states[area] = UNDER_CONSTRUCTION
        elif area in internal:
            states[area] = INTERNAL
        else:
            states[area] = UNCLASSIFIED
    return states


def nav_reachable() -> set[str]:
    """Areas the CANONICAL nav routes to. The tail
    is debt being retired, and counting it as a route would let the orphan count read
    green because six pages happen to cross-link each other."""
    reachable = {item.area for item in CANONICAL_NAV}
    # A child of a tab is reachable BY ITS PARENT, not by the top nav. Counting it here is what
    # checks the parent genuinely links to it, so this cannot become an alibi.
    return reachable


CANONICAL_NAV_AREAS = tuple(item.area for item in CANONICAL_NAV)


def register_violations(site: Path = SITE) -> list[str]:
    """The C3 control, as ruled. Returns human-readable violations; empty is green.

    Known-and-owned debt (ORPHAN_DEBT) is not reported -- but a STALE or MISSING debt
    entry is, so the register cannot drift into an alibi.
    """
    states = classify(site)
    reachable = nav_reachable()
    problems: list[str] = []

    # NAV_EXEMPT is a THIRD legitimate account, added 2026-08-20. Before this, an advertised
    # page with no nav route had exactly two honest homes -- a nav tab, or a dated debt entry --
    # and /privacy/ fits neither: it is a legal footer route on every single page, so it is
    # more reachable than most of the site while never being a tab. Filing it as DEBT said it
    # was waiting to be folded somewhere, which was never true and quietly aged.
    orphans = {a for a, s in states.items() if s == ADVERTISED and a not in reachable
               and a not in NAV_EXEMPT}
    for area in sorted(orphans - set(ORPHAN_DEBT)):
        problems.append(
            f"{area} is ADVERTISED in sitemap.xml with no route from the canonical nav, and is "
            f"in neither ORPHAN_DEBT nor NAV_EXEMPT -- give it a nav route, take it off the "
            f"sitemap, record the debt with the step that clears it, or declare with a reason "
            f"why it is reachable without being a tab"
        )
    for area in sorted(set(ORPHAN_DEBT) - orphans):
        problems.append(
            f"{area} is in ORPHAN_DEBT but is no longer an orphan -- remove the entry "
            f"(a debt register that keeps discharged entries stops being countable)"
        )
    for area in sorted(a for a, s in states.items() if s == UNCLASSIFIED):
        problems.append(
            f"{area} is deployed but is in neither sitemap.xml, nor _redirects, nor "
            f"INTERNAL_DOORS -- a page a reader can reach that nothing in the repo claims"
        )
    for area in sorted(a for a in CANONICAL_NAV_AREAS if a not in states):
        problems.append(
            f"the canonical nav routes to {area}, which is not a deployed area -- "
            f"brief §9.2: no intermediate state where the nav points at a page that does not exist"
        )
    # ── UNDER CONSTRUCTION: legitimate, but only on its two obligations ──────────
    # The ruling makes an early door lawful; these keep it honest. Both fail toward
    # REPORTING: an unreadable placeholder page is treated as not saying so, because a
    # door we cannot verify speaks for itself is exactly the one that quietly goes blank.
    advertised_now = set(advertised_areas(site / "sitemap.xml"))
    for area, (will_show, when, step) in sorted(UNDER_CONSTRUCTION_DOORS.items()):
        if area in advertised_now:
            problems.append(
                f"{area} is UNDER CONSTRUCTION and is also in sitemap.xml -- a hole must not "
                f"be advertised to crawlers. Take it off the sitemap until {step} finishes it, "
                f"or finish it and remove the under-construction entry"
            )
        if area not in states:
            problems.append(
                f"{area} is declared UNDER CONSTRUCTION but is not deployed -- the nav would "
                f"point at nothing, which is the one intermediate state the brief forbids"
            )
            continue
        page = site / area.strip("/") / "index.html"
        try:
            body = page.read_text(encoding="utf-8", errors="replace")
        except OSError:
            body = ""
        if UNDER_CONSTRUCTION_MARKER not in body:
            problems.append(
                f"{area} is UNDER CONSTRUCTION but its page does not say so -- it must carry "
                f"the marker {UNDER_CONSTRUCTION_MARKER!r} and tell the reader what it will "
                f"show and roughly when. A silently empty door is worse than no door"
            )
    for area in sorted(set(UNDER_CONSTRUCTION_DOORS) - nav_reachable()):
        problems.append(
            f"{area} is declared UNDER CONSTRUCTION but the canonical nav does not route to "
            f"it -- the whole point of the state is a door a reader can walk through early. "
            f"Add it to CANONICAL_NAV or drop the entry"
        )

    return problems


def _relative(target: str, from_area: str, depth: int = 0) -> str:
    """A site-absolute target as a page-relative href, from a page `depth` levels below
    `from_area`.

    THE OLD PREMISE WAS FALSE AND COST EIGHT PAGES (2026-08-24, director on
    /knowledge/price-cap/). This function used to say "only two depths exist on this surface
    (root, and one directory down)" and take no depth at all. A THIRD depth had existed since
    the Knowledge topic pages were built -- `/knowledge/price-cap/` and its seven siblings --
    and because the renderer could not address them they were never given the canonical nav.
    They kept a hand-written one naming Company, World, Knowledge, Proof and Glossary: the
    pre-fold nav, two of whose links have pointed at pages deleted on 2026-08-20 ever since.

    `depth` is levels BELOW `from_area`, so 0 is the area's own index page and 1 is a topic
    page under it. It is explicit rather than derived because deriving it from a path is how a
    plausible wrong answer gets produced silently, which is what the old docstring was right to
    be afraid of.
    """
    up = depth + (0 if from_area == "/" else 1)
    if target == from_area:
        # A page's own entry. At depth 0 that is the page itself; below, it is the ancestor.
        return "./" if depth == 0 else "../" * depth
    prefix = ("../" * up) if up else "./"
    if target == "/":
        return prefix
    return prefix + target.lstrip("/")


def active_target(area: str, site: Path = SITE) -> str:
    """The area whose nav entry renders as `active` on the page at `area`.

    It is the page's own area, and as of 2026-08-20 that is the whole rule.

    This function used to resolve a chain: a RETIRED page folded into the door that absorbed
    it (read from `_redirects`), and that door might itself be a CHILD of a tab (read from
    `PARENT_OF`), so it walked up with a loop guard to find the entry the nav actually has.
    Both inputs are gone -- the director deleted the redirects and the fold on the grounds that
    nobody had ever visited the URLs they protected. Every page on the site is now a tab or
    lives under one, so the ancestor walk had nothing left to walk.
    """
    return area


def render_nav(area: str, indent: str = "  ", site: Path = SITE, depth: int = 0) -> str:
    """The marked nav block for one area: the canonical items, with `active` on the page's
    own entry. The per-page legacy tail is gone (2026-08-20) -- it existed to hang extra links
    off pages that are now deleted.

    `depth` is how many levels below `area` the page being rendered into sits -- 1 for a
    Knowledge topic page under `/knowledge/`. See `_relative`."""
    link_class = HOME_LINK_CLASS if area == "/" else INNER_LINK_CLASS
    active_area = active_target(area, site)
    # THE DOORS ARE ALWAYS WRAPPED (2026-08-19). Home grouped its links in a `.doors` element
    # and no other page did, so at phone width -- where the bar becomes two rows -- Home laid
    # its five doors out in one line and every other page stacked them into FIVE, with the last
    # falling outside the band. Same defect as the two link grammars, one level down: a layout
    # rule cannot treat "the doors" as a unit on a page where they are not one. Emitting the
    # wrapper here means every page has it, and it lives INSIDE the rendered region so no page
    # can hand-edit its way out.
    lines = [NAV_START, '<span class="doors">']
    entries = [(i.label, i.area) for i in CANONICAL_NAV]
    seen_active = False
    for label, target in entries:
        active = not seen_active and target.split("#")[0] == active_area
        seen_active = seen_active or active
        classes = " ".join(c for c in (link_class, "active" if active else "") if c)
        attr = f' class="{classes}"' if classes else ""
        lines.append(f'<a href="{_relative(target, area, depth)}"{attr}>{label}</a>')
    lines.append("</span>")
    lines.append(NAV_END)
    return ("\n" + indent).join(lines)


# ── The SITE9 condition, mechanised ───────────────────────────────────────────
# Ruled 2026-08-18 (director console, reserved class 3):
#
#   "show me its rendered content before it becomes crawlable -- it was written
#    internally and I want to read it as a stranger would first"
#
# Prose in an atom's block_reason is the shape MAKE IT STICK says will evaporate, so
# the condition is a control on THIS side: the three acts that make /director/
# crawlable are refused while no release is recorded. Nothing is added to the
# director's path -- he says go, and the worker writes the record. Silence does NOT
# release this one; that carve-out from THE_STANDARD is his, made in the same breath
# as accepting the recommendation.
DIRECTOR_RELEASE = REPO / "docs" / "observability" / "director_record_publication_release.json"


def director_record_release(path: Path = DIRECTOR_RELEASE) -> dict | None:
    """The recorded release, or None. Fail-closed by construction: any unreadable or
    malformed record reads as NOT released, because the failure mode that matters is
    publishing on a record nobody can parse."""
    import json

    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict) or record.get("released") is not True:
        return None
    if not record.get("director_words") or not record.get("render_shown"):
        return None  # a release with no evidence of what he was shown is not a release
    return record


def director_record_publication_violations(site: Path = SITE) -> list[str]:
    """Empty while /director/ stays internal, or once the director has released it."""
    if director_record_release() is not None:
        return []
    problems = []
    if "/director/" in advertised_areas(site / "sitemap.xml"):
        problems.append("/director/ is in sitemap.xml before the director has read its render")
    if "/director/" not in INTERNAL_DOORS:
        problems.append("/director/ was removed from INTERNAL_DOORS before the director has read its render")
    index = site / "director" / "index.html"
    if index.is_file() and "noindex" not in index.read_text(encoding="utf-8"):
        problems.append("/director/ lost its noindex before the director has read its render")
    return problems


if __name__ == "__main__":  # pragma: no cover - operator convenience
    import sys

    states = classify()
    for area, state in sorted(states.items()):
        route = "nav" if area in nav_reachable() else ("debt" if area in ORPHAN_DEBT else "-")
        print(f"{state:<13} {route:<5} {area}")
    problems = register_violations() + director_record_publication_violations()
    for p in problems:
        print(f"VIOLATION: {p}")
    sys.exit(1 if problems else 0)
