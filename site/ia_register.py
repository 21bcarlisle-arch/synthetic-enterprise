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
    # are reached by ONE link each from the tab that absorbed them -- see PARENT_OF, which is
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
# replaces the LEGACY_TAIL habit of hanging extra links off every page's nav -- that is what made
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
PARENT_OF: dict[str, str] = {}


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
# LEGACY_TAIL IS EMPTY, 2026-08-19, and that is the point rather than an omission. It held the
# per-page extra links by which a reader could reach the orphans -- and it is precisely why the
# nav was never canonical: Home rendered eight items, Knowledge nine, and the director read two
# different sites on two pages. Every destination it carried is now either a nav tab, a declared
# child in PARENT_OF, or a 301. The register keeps the name so the shrink-only test still has a
# subject, and it must stay empty: a new entry means someone is hanging a link off one page again.
LEGACY_TAIL: dict[str, tuple[tuple[str, str], ...]] = {}


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
    reachable = {item.area for item in CANONICAL_NAV}
    # A child of a tab is reachable BY ITS PARENT, not by the top nav. Counting it here is what
    # lets /world/ stop being a tab without becoming an orphan -- and `fold_violations` below
    # checks the parent genuinely links to it, so this cannot become an alibi.
    reachable |= set(PARENT_OF)
    return reachable


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

    problems.extend(fold_violations(site))
    problems.extend(no_retired_nav_links(site))
    return problems


def fold_violations(site: Path = SITE) -> list[str]:
    """A declared fold must be a real link. Director ruling, 2026-08-19.

    THE FAILURE THIS EXISTS TO REFUSE: taking a page off the top nav, declaring it a child of
    some tab, and never adding the link -- which reads as tidy structure and IS an orphaning.
    `nav_reachable()` counts children as reachable, so without this check that function becomes
    an alibi: anything could be hidden by naming a parent for it.

    Fails toward REPORTING: an unreadable parent page counts as not linking, because a fold we
    cannot verify is one we have not made.
    """
    problems = []
    for child, parent in sorted(PARENT_OF.items()):
        page = site / parent.strip("/") / "index.html" if parent != "/" else site / "index.html"
        try:
            body = page.read_text(encoding="utf-8", errors="replace")
        except OSError:
            body = ""
        # THE NAV REGION IS STRIPPED FIRST, and the first draft of this check did not do that.
        # It passed on all three folds while none of the three content links existed -- because
        # the nav still carried `../world/` from before the fold, so the check was satisfied by
        # the very links the fold removes. A control that reads the thing it is replacing is not
        # a control. The link must be in the PAGE, where a reader can find it.
        body = re.sub(r"<!-- IA-NAV:START.*?IA-NAV:END -->", "", body, flags=re.S)
        # accept either an absolute or a relative href to the child
        slug = child.strip("/")
        if f'href="{child}"' not in body and f'href="../{slug}/"' not in body \
                and f'href="./{slug}/"' not in body and f'href="{slug}/"' not in body:
            problems.append(
                f"{child} is declared a child of {parent} but {parent} does not link to it -- "
                f"the fold is a claim, not a route, and {child} is orphaned in fact. Add the "
                f"one link, or give {child} a nav tab back"
            )
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
    resolved = area
    if target:
        resolved = target if target.endswith("/") else target + "/"
    # WALK UP TO THE NAV ANCESTOR (2026-08-19 fold). A retired page folds into a door, and after
    # the fold that door may itself be a CHILD -- /method/ 301s to /proof/, and /proof/ is now a
    # child of /harness/. Highlighting /proof/ would mark an entry the nav no longer has, which
    # is the same lie in a new place. One hop is enough for today's shape and a loop guard is
    # cheaper than an argument about whether it always will be.
    seen = set()
    while resolved in PARENT_OF and resolved not in seen:
        seen.add(resolved)
        resolved = PARENT_OF[resolved]
    return resolved


def render_nav(area: str, indent: str = "  ", site: Path = SITE) -> str:
    """The marked nav block for one area: canonical items, then that page's legacy
    tail, with `active` on the page's own entry (or its fold target, if retired)."""
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
    entries += list(LEGACY_TAIL.get(area, ()))
    seen_active = False
    for label, target in entries:
        active = not seen_active and target.split("#")[0] == active_area
        seen_active = seen_active or active
        classes = " ".join(c for c in (link_class, "active" if active else "") if c)
        attr = f' class="{classes}"' if classes else ""
        lines.append(f'<a href="{_relative(target, area)}"{attr}>{label}</a>')
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
