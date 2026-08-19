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

    ADVERTISED   in sitemap.xml, served, crawlable                          (10 areas)
    INTERNAL     served 200, deliberately absent from the sitemap           (2 areas)
    RETIRED      301 to a live door, page kept in-repo for reference        (5 areas)

As written the control is red on TWELVE of sixteen areas, and for seven of them
(5 RETIRED + 2 INTERNAL) that is correct behaviour the project chose deliberately --
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
`advertised_areas()` reads sitemap.xml. `retired_areas()` reads `_redirects`.
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
INTERNAL_DOORS = ("/director/", "/shadow/")


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

UNDER_CONSTRUCTION_DOORS: dict[str, tuple[str, str, str]] = {
    "/explore/": (
        "One real customer followed through six stages -- PRICED, CHOSEN, USED, BILLED, PAID, "
        "JUDGED -- showing at each stage what the world knew against what the company believed.",
        "Next: the traversal for a single customer. The stage data it renders already exists.",
        "SITE10_explore_traversal",
    ),
    "/harness/": (
        "How this project is actually run: the two-seat model, how work is chosen and "
        "sequenced, the named failure classes, and an honest count of what broke and why.",
        "Next: the method account. The known-limitations section moves here from Proof.",
        "SITE9_harness_tab_and_director_record",
    ),
}


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
    NavItem("Home", "/"),
    NavItem("The World", "/world/"),
    NavItem("The Company", "/company/"),
    # SITE7, 2026-08-18 (director pulled it forward ahead of Knowledge: "I want to see a
    # real new tab to judge whether the structure works before four more steps are built
    # on it"). THIS LINE plus a sitemap entry is the whole nav change -- sixteen pages
    # pick it up from `tools/render_site_nav.py --write`. That is what Step 0 bought.
    NavItem("Capabilities", "/capabilities/"),
    # SITE6 first half, 2026-08-18. The brief ranks Knowledge SECOND, before Capabilities --
    # domain competence is the credibility signal for the primary audience. It is placed here
    # rather than there only because the ruled order is a destination and this is a
    # migration: Home, World and Company are the doors a returning reader already knows, and
    # re-ordering them is SITE8's job with its own tests. Knowledge joins the nav now.
    NavItem("Knowledge", "/knowledge/"),
    # SITE9 + SITE10 doors opened EARLY and deliberately empty, per the director's ruling of
    # 2026-08-19: "holes beat wrong or unintelligible content. Put the final structure up now,
    # with honest 'being built' pages where the content isn't written." Both are
    # UNDER_CONSTRUCTION: routed from the nav, absent from the sitemap, and each page says what
    # it will show and roughly when. See UNDER_CONSTRUCTION_DOORS for the obligations.
    NavItem("Explore", "/explore/"),
    NavItem("Harness", "/harness/"),
    # PROOF STAYS, and this is a judgement rather than an oversight. SITE11 dissolves it into
    # Harness and the map records that it "genuinely must be last -- it re-points five live 301s
    # at homes that must already exist". Those homes do not exist yet: Harness is a placeholder.
    # The ruling says holes beat WRONG content; /proof/'s content is not wrong, it is merely
    # destined to move, so removing its door now would put a hole where working content is and
    # strand the five redirects the director specifically told me to protect. It leaves the nav
    # when Harness can receive what it holds.
    NavItem("Proof", "/proof/"),
)


# ── Per-page render profile ───────────────────────────────────────────────────
# The site has two nav GRAMMARS and this module renders both rather than forcing one,
# because collapsing them is a CSS change on the front door and Step 0 is explicitly
# not that. The home page wraps `<nav class="doors">` in `<header class="site-nav">`
# and styles its links bare; every other page uses `<nav class="site-nav">` with
# `.nav-link`. The LOGO is deliberately untouched on every page -- it is not a route,
# and its inconsistency (`poesys.` / `⚡ Poesys` / `Poesys`) is the declared subject of
# `site/test_brand_token_adoption.py`'s debt register, which owns it.
HOME_LINK_CLASS = ""
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
LEGACY_TAIL: dict[str, tuple[tuple[str, str], ...]] = {
    # absorbed by SITE10 (Explore reconciles /customers/) + SITE11 (/proof/ anchors)
    "/customers/": (
        ("Now", "/now/"),
        ("Method", "/proof/#method-anchor"),
        ("Journey", "/proof/#project-anchor"),
        ("Simplified", "/proof/#simplified-anchor"),
    ),
    # absorbed by SITE8 (Home carries the "latest" strip /now/ duplicates)
    "/now/": (
        ("Now", "/now/"),
        ("Customers", "/customers/"),
        ("Method", "/proof/#method-anchor"),
    ),
    "/privacy/": (("Customers", "/customers/"),),
    # NO self-entry here, deliberately. /wip-flow/ carried a non-clickable
    # `<span class="nav-link active">WIP + Flow</span>`; rendering it as a real link
    # made `site/test_link_walk.py` red on the first pass, correctly -- /wip-flow is a
    # 301 SOURCE, and DIRECTOR_RULING_CANONICAL_DOOR_A forbids an internal link to one.
    # A RETIRED page's active door is the door it folded into (see active_target), and
    # no nav on this site may link to a redirect source; `no_retired_nav_links()`
    # enforces that for every page, not just this one.
    "/wip-flow/": (
        ("Customers", "/customers/"),
        ("Method", "/proof/#method-anchor"),
    ),
    # absorbed by SITE6 -- the glossary PAGE dies (the glossary LAYER survives)
    "/glossary/": (("Glossary", "/glossary/"),),
    # Knowledge's own entry is gone -- it is a canonical tab now. Glossary stays until
    # SITE6's second half dissolves that page.
    "/knowledge/": (("Glossary", "/glossary/"),),
    # the three RETIRED pages that render /proof/'s absorbed anchors; absorbed by
    # SITE11 when /proof/ is dissolved and its anchors re-home
    "/method/": (
        ("Method", "/proof/#method-anchor"),
        ("Journey", "/proof/#project-anchor"),
        ("Simplified", "/proof/#simplified-anchor"),
    ),
    "/simplified/": (
        ("Method", "/proof/#method-anchor"),
        ("Journey", "/proof/#project-anchor"),
        ("Simplified", "/proof/#simplified-anchor"),
    ),
    "/tours/": (
        ("Method", "/proof/#method-anchor"),
        ("Journey", "/proof/#project-anchor"),
        ("Simplified", "/proof/#simplified-anchor"),
    ),
}


# ── The six real orphans ──────────────────────────────────────────────────────
# ADVERTISED to crawlers, with no route from the canonical nav. This is the defect the
# brief's §7 control #1 was reaching for, and it is REAL -- unlike the twelve the
# control as written would have reported. Step 0 red-lists them; it does not fix them.
# Each names the step that gives it a route (or takes it off the sitemap).
#
# SHRINK-ONLY: `test_ia_register.py` fails if an entry here is no longer an orphan
# (stale debt claiming credit) and fails on any orphan NOT here (new debt sneaking in).
ORPHAN_DEBT: dict[str, str] = {
    "/glossary/": "SITE6 -- the glossary page is 301'd to Knowledge and leaves the sitemap",
    "/customers/": "SITE10 -- reconciled into Explore, which is a canonical tab",
    "/evidence/": "SITE9 -- the machine record folds into Harness behind a drill-down",
    "/now/": "SITE8 -- Home carries the dated 'latest' strip this page duplicates",
    "/privacy/": "SITE8 -- a footer route, not a tab; Home's foot is its home",
}


# ── The one nav exemption ─────────────────────────────────────────────────────
# /shadow/ is a GENERATED mirror of the whole site at a second root
# (tools/generate_shadow_html.py). Its nav routes within the mirror
# (/shadow/customers/, /shadow/sim/, ...) and giving it the canonical nav would route
# a shadow reader onto the live site -- the opposite of what a mirror is for. Exactly
# one member, asserted as exactly one member, with its reason in the register rather
# than in a reviewer's memory.
GENERATED_NAV: dict[str, str] = {
    # /evidence/ is the only ADVERTISED area whose page is generated -- rewritten every
    # ~30 minutes on the publish path -- so a hand edit to it is overwritten within the
    # hour. Its nav comes from THIS register, rendered by the generator named here.
    # `tools/render_site_nav.py` therefore skips it by declaration rather than by the
    # accident of what its markup happens to look like, and the control asserts the
    # generated page anyway.
    "/evidence/": "tools/generate_evidence_data.py",
}


NAV_EXEMPT: dict[str, str] = {
    "/shadow/": (
        "generated mirror at a second root; its nav is the mirror's own IA and the "
        "canonical nav would route a shadow reader onto the live site"
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


def retired_areas(redirects: Path = REDIRECTS) -> dict[str, str]:
    """Areas that are a 301 SOURCE in `_redirects`, mapped to their target.

    Only top-level area sources count (`/method`, `/method/*`); the favicon and the
    www-canonicalisation rules are not areas. Fail-closed on an unreadable file --
    but NOT on an empty result, because a site with no retired areas is a legitimate
    state (it was this project's state before 2026-07-18).
    """
    try:
        lines = redirects.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        raise IaRegisterUnavailable(f"_redirects unreadable: {e}") from e
    out: dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2 or not parts[0].startswith("/"):
            continue  # absolute-URL rules (www canonicalisation) are not areas
        source, target = parts[0], parts[1]
        if source.endswith("/*"):
            source = source[:-1]
        elif not source.endswith("/"):
            source = source + "/"
        if source.count("/") != 2 or "." in source:  # "/method/" -> 2; skip files
            continue
        out.setdefault(source, target)
    return out


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
RETIRED = "RETIRED"
UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
UNCLASSIFIED = "UNCLASSIFIED"


def classify(site: Path = SITE) -> dict[str, str]:
    """Every deployed area mapped to its state. UNCLASSIFIED is the failure state:
    deployed, not advertised, not redirected, not declared internal -- a page a reader
    can reach and nothing in the repo says should exist."""
    advertised = set(advertised_areas(site / "sitemap.xml"))
    retired = set(retired_areas(site / "_redirects"))
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
        elif area in retired:
            states[area] = RETIRED
        else:
            states[area] = UNCLASSIFIED
    return states


def nav_reachable() -> set[str]:
    """Areas the CANONICAL nav routes to. Deliberately excludes LEGACY_TAIL: the tail
    is debt being retired, and counting it as a route would let the orphan count read
    green because six pages happen to cross-link each other."""
    return {item.area for item in CANONICAL_NAV}


def register_violations(site: Path = SITE) -> list[str]:
    """The C3 control, as ruled. Returns human-readable violations; empty is green.

    Known-and-owned debt (ORPHAN_DEBT) is not reported -- but a STALE or MISSING debt
    entry is, so the register cannot drift into an alibi.
    """
    states = classify(site)
    reachable = nav_reachable()
    problems: list[str] = []

    orphans = {a for a, s in states.items() if s == ADVERTISED and a not in reachable}
    for area in sorted(orphans - set(ORPHAN_DEBT)):
        problems.append(
            f"{area} is ADVERTISED in sitemap.xml with no route from the canonical nav, "
            f"and is not in ORPHAN_DEBT -- give it a nav route, take it off the sitemap, "
            f"or record the debt with the step that clears it"
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

    problems.extend(no_retired_nav_links(site))
    return problems


def no_retired_nav_links(site: Path = SITE) -> list[str]:
    """No nav entry, canonical or tail, may point at a 301 SOURCE.

    `DIRECTOR_RULING_CANONICAL_DOOR_A` (2026-07-24): an internal link to a redirect
    source lands the reader one bounce late on a door that is not the canonical one.
    `site/test_link_walk.py` polices the whole site for this and caught the register's
    first draft doing it on `/wip-flow/`; this check keeps the register itself from
    ever re-proposing one, which is the earlier and cheaper place to fail.
    """
    retired = set(retired_areas(site / "_redirects"))
    problems = []
    for area, entries in [("<canonical>", tuple((i.label, i.area) for i in CANONICAL_NAV))] + sorted(
        LEGACY_TAIL.items()
    ):
        for label, target in entries:
            if target.split("#")[0] in retired:
                problems.append(
                    f"{area} nav entry {label!r} points at {target}, which is a 301 source"
                )
    return problems


CANONICAL_NAV_AREAS = tuple(item.area for item in CANONICAL_NAV)


# ── Rendering ─────────────────────────────────────────────────────────────────
def _relative(target: str, from_area: str) -> str:
    """A site-absolute target as a page-relative href, from the page at `from_area`.

    Only two depths exist on this surface (root, and one directory down), so this is
    deliberately not a general path solver -- a general one would silently produce a
    plausible wrong answer if a third depth ever appeared. `deployed_areas()` only
    ever yields those two, and `test_ia_register.py` asserts it.
    """
    if target == from_area:
        return "./"  # a page's own entry, the convention every hand-written nav used
    prefix = "./" if from_area == "/" else "../"
    if target == "/":
        return prefix
    return prefix + target.lstrip("/")


def active_target(area: str, site: Path = SITE) -> str:
    """The area whose nav entry renders as `active` on the page at `area`.

    Normally the page's own area. For a RETIRED page it is the door the page has been
    FOLDED INTO -- derived from `_redirects`, not typed -- because a reader on
    `/project/` is looking at content that now lives behind Proof, and highlighting a
    door that no longer exists in the IA would be a lie the register can avoid telling.
    """
    target = retired_areas(site / "_redirects").get(area)
    if target:
        return target if target.endswith("/") else target + "/"
    return area


def render_nav(area: str, indent: str = "  ", site: Path = SITE) -> str:
    """The marked nav block for one area: canonical items, then that page's legacy
    tail, with `active` on the page's own entry (or its fold target, if retired)."""
    link_class = HOME_LINK_CLASS if area == "/" else INNER_LINK_CLASS
    active_area = active_target(area, site)
    lines = [NAV_START]
    entries = [(i.label, i.area) for i in CANONICAL_NAV]
    entries += list(LEGACY_TAIL.get(area, ()))
    seen_active = False
    for label, target in entries:
        active = not seen_active and target.split("#")[0] == active_area
        seen_active = seen_active or active
        classes = " ".join(c for c in (link_class, "active" if active else "") if c)
        attr = f' class="{classes}"' if classes else ""
        lines.append(f'<a href="{_relative(target, area)}"{attr}>{label}</a>')
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
