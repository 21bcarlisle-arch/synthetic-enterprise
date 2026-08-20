#!/usr/bin/env python3
"""The IA register's controls (SITE4 / Step 0 of the website structure programme).

WHAT THIS POLICES
-----------------
1. **The three-state register (C3).** Every deployed area is ADVERTISED, INTERNAL or
   INTERNAL; an area in neither is the failure. An ADVERTISED area with no
   route from the canonical nav is a defect unless it is recorded in `ORPHAN_DEBT`
   with the step that clears it -- and the debt register can only SHRINK.
2. **Every page's nav is the register's render.** Sixteen areas, twelve hand-authored
   nav shapes, and every later step of the programme moves a tab. If a page's nav can
   drift from the register, Step 0 bought nothing.
3. **The director-record condition**, ruled 2026-08-18 (reserved class 3): `/director/`
   may not be made crawlable until the director has read its rendered content.

WHY THE MUTATIONS ARE HALF THIS FILE (R15)
------------------------------------------
"No control counts as evidence unless a MUTATION TEST proves it fires on its own named
defect." Every control here has one, and they are written against the three killer
patterns by name:

  TAUTOLOGY   -- the checked value must not derive from the source it checks. The nav
                 control compares COMMITTED HTML against a render; the register control
                 compares the TREE against sitemap.xml and _redirects. Neither side is
                 computed from the other.
  FAIL-OPEN   -- a missing/empty/malformed sitemap, `_redirects` or tree must RAISE,
                 not yield an empty register that reports everything fine.
  FAIL-SILENT -- an unreadable director-release record reads as NOT RELEASED, because
                 the failure that matters is publishing on a record nobody can parse.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))
sys.path.insert(0, str(SITE.parent))

import ia_register as reg  # noqa: E402
from tools import render_site_nav as renderer  # noqa: E402


@pytest.fixture
def tree(tmp_path):
    """A throwaway copy of the real site tree. Mutations happen HERE, never in the
    working tree -- a control whose own test can leave the repo dirty is a control
    nobody will run twice."""
    dest = tmp_path / "site"
    shutil.copytree(
        SITE, dest,
        ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".pytest_cache"),
    )
    return dest


# ---------------------------------------------------------------------------
# 1. The three-state register
# ---------------------------------------------------------------------------
def test_the_register_is_green_at_head():
    assert reg.register_violations() == []


def test_every_deployed_area_is_in_exactly_one_state():
    states = reg.classify()
    assert states, "the register classified nothing -- that is the fail-open shape"
    # UNDER_CONSTRUCTION joined the states on 2026-08-19 (director ruling: "under-construction
    # is a legitimate state and the machine should be able to express it"). It is a CLAIMED
    # state like the other three -- the failure this asserts is UNCLASSIFIED, a page a reader
    # can reach that nothing in the repo claims, and an early door is claimed loudly.
    assert set(states.values()) <= {reg.ADVERTISED, reg.INTERNAL,
                                    reg.UNDER_CONSTRUCTION}, (
        "an UNCLASSIFIED area is deployed and unclaimed: "
        f"{[a for a, s in states.items() if s == reg.UNCLASSIFIED]}"
    )


def test_the_three_states_are_the_measured_census():
    """The counts the proposal was ruled on, asserted rather than remembered.

    Not a pin on WHICH areas -- that would go red on every legitimate IA move and is
    the false-positive class this project has stalled on. It pins the SHAPE: three
    states, all populated, nothing unclaimed.
    """
    states = reg.classify()
    by_state = {s: sorted(a for a, st in states.items() if st == s) for s in set(states.values())}
    assert len(by_state[reg.ADVERTISED]) >= 5, by_state
    # 2026-08-20: INTERNAL is legitimately EMPTY now, and RETIRED no longer exists. The director ruled
    # that the five tabs are the site, so there are no deliberately-unadvertised pages left
    # and no pages kept in-repo behind a 301 -- the redirects survive, the directories do not.
    # Pinning "all three states populated" would now fail on the correct arrangement, which is
    # the false-positive class this test's own docstring warns about.
    assert by_state.get(reg.INTERNAL, []) == [], (
        f"an internal door reappeared: {by_state.get(reg.INTERNAL)}. Every deployed page is "
        "supposed to be one of the five tabs or reachable from them."
    )
    assert by_state.get(reg.UNCLASSIFIED, []) == [], by_state


def test_orphan_debt_is_exactly_the_current_orphans():
    """Shrink-only. An entry that is no longer an orphan is stale credit; an orphan
    with no entry is new debt arriving unannounced. Both are violations, and
    `register_violations()` reports both -- proven by the two mutations below."""
    states = reg.classify()
    reachable = reg.nav_reachable()
    orphans = {a for a, s in states.items() if s == reg.ADVERTISED and a not in reachable
               and a not in reg.NAV_EXEMPT}
    assert orphans == set(reg.ORPHAN_DEBT), (
        f"orphans={sorted(orphans)} debt={sorted(reg.ORPHAN_DEBT)}"
    )


def test_every_debt_entry_names_the_step_that_clears_it():
    """Empty today, and the assertion is kept rather than deleted: the register is the thing
    that must stay disciplined, not this run of it. All four content entries were discharged
    on 2026-08-20 exactly as each had predicted."""
    for area, owner in reg.ORPHAN_DEBT.items():
        assert re.match(r"SITE\d+ -- \S", owner), (
            f"{area}'s debt entry must name the owning step, got {owner!r} -- "
            "a debt register with no owner is a list of complaints"
        )


def test_the_canonical_nav_only_routes_to_deployed_areas():
    deployed = set(reg.deployed_areas())
    for item in reg.CANONICAL_NAV:
        assert item.area in deployed, (
            f"nav routes to {item.area}, which is not deployed -- brief §9.2 forbids "
            "an intermediate state where the nav points at a page that does not exist"
        )


def test_every_nav_exemption_carries_a_reason():
    """The exemption list is where a nav control goes to die. It is EMPTY as of 2026-08-20 --
    its one member was the /shadow/ mirror, now deleted -- and the shape is still asserted so
    a new exemption cannot arrive as a bare path."""
    for area, reason in reg.NAV_EXEMPT.items():
        assert len(reason) > 40, f"{area} is exempted without a reason -- that is an allowlist"


def test_only_two_page_depths_exist():
    """`_relative()` is deliberately not a general path solver. If a third depth ever
    appears it must fail here, not silently render a plausible wrong href."""
    for area in reg.deployed_areas():
        assert area == "/" or area.count("/") == 2, f"unexpected depth: {area}"


# --- mutations (R15) -------------------------------------------------------
def test_MUTATION_an_advertised_area_with_no_nav_route_and_no_debt_entry_fires(tree):
    (tree / "brand-new").mkdir()
    (tree / "brand-new" / "index.html").write_text("<html><body>hi</body></html>")
    sitemap = tree / "sitemap.xml"
    sitemap.write_text(
        sitemap.read_text().replace(
            "</urlset>", f"<url><loc>{reg.CANONICAL_HOST}/brand-new/</loc></url></urlset>"
        )
    )
    problems = reg.register_violations(tree)
    assert any("/brand-new/" in p and "no route from the canonical nav" in p for p in problems), problems


def test_MUTATION_a_deployed_area_in_no_state_at_all_fires(tree):
    (tree / "stowaway").mkdir()
    (tree / "stowaway" / "index.html").write_text("<html><body>hi</body></html>")
    problems = reg.register_violations(tree)
    assert any("/stowaway/" in p and "neither" in p for p in problems), problems


def test_MUTATION_a_stale_debt_entry_fires(tree, monkeypatch):
    """The half a debt register usually lacks: an entry that has been discharged but
    still sits there claiming the credit."""
    monkeypatch.setitem(reg.ORPHAN_DEBT, "/world/", "SITE9 -- imaginary")
    problems = reg.register_violations(tree)
    assert any("/world/" in p and "no longer an orphan" in p for p in problems), problems


def test_MUTATION_a_nav_route_to_a_missing_page_fires(tree, monkeypatch):
    monkeypatch.setattr(reg, "CANONICAL_NAV", reg.CANONICAL_NAV + (reg.NavItem("Ghost", "/ghost/"),))
    monkeypatch.setattr(reg, "CANONICAL_NAV_AREAS", tuple(i.area for i in reg.CANONICAL_NAV))
    problems = reg.register_violations(tree)
    assert any("/ghost/" in p and "not a deployed area" in p for p in problems), problems


# `_redirects` LEFT this list on 2026-08-20: the register no longer reads it (retired_areas is
# gone with the RETIRED state), so its absence is no longer a degraded register -- it is a site
# with no redirects, which is now the normal condition.
@pytest.mark.parametrize("victim", ["sitemap.xml", "index.html"])
def test_MUTATION_FAIL_OPEN_a_missing_source_raises_rather_than_reporting_green(tree, victim):
    """The single most important property here. A register that quietly degrades to an
    empty set reports a perfectly green IA for a site that has been deleted."""
    (tree / victim).unlink()
    with pytest.raises(reg.IaRegisterUnavailable):
        reg.register_violations(tree)


def test_MUTATION_FAIL_OPEN_an_empty_sitemap_raises(tree):
    (tree / "sitemap.xml").write_text('<?xml version="1.0"?><urlset></urlset>')
    with pytest.raises(reg.IaRegisterUnavailable):
        reg.register_violations(tree)


def test_MUTATION_FAIL_OPEN_a_malformed_sitemap_raises(tree):
    (tree / "sitemap.xml").write_text("not xml at all, not even close")
    with pytest.raises(reg.IaRegisterUnavailable):
        reg.register_violations(tree)


# ---------------------------------------------------------------------------
# 2. Every page's nav is the register's render
# ---------------------------------------------------------------------------
def test_every_owned_page_renders_the_register_nav():
    assert renderer.stale() == [], (
        "a page's committed nav is not what site/ia_register.py renders -- "
        "run `python3 -m tools.render_site_nav --write`"
    )


def test_every_deployed_area_is_owned_declared_generated_or_exempt():
    """No page falls between the stools. This is the control that makes the other nav
    control mean something: without it, a page could avoid the render simply by not
    looking like one the renderer recognises."""
    owned = {area for area, _ in renderer.pages()}
    accounted = owned | set(reg.NAV_EXEMPT) | set(reg.GENERATED_NAV)
    assert set(reg.deployed_areas()) == accounted, (
        f"unaccounted areas: {sorted(set(reg.deployed_areas()) - accounted)}"
    )


# RETIRED 2026-08-20 with the page. /evidence/ was deleted under the director's ruling that
# the five tabs are the site; its 301 lands on /harness/. The property this test guarded -- a
# GENERATED page's nav must be the register's render, not a copy that drifts -- has no
# generated page left to guard, so it is removed rather than left pointing at a missing file.


def test_no_page_renders_two_active_entries():
    for area, path in renderer.pages():
        block = _nav_block(path.read_text(encoding="utf-8"))
        assert block.count("active") <= 1, f"{area}: more than one active entry\n{block}"


def test_the_pages_that_cannot_highlight_themselves_are_exactly_the_unreached_ones():
    """A second, independent reading of the same defect. A page with NO active entry is
    a page whose own door the nav does not reach -- it cannot say "you are here". Today
    that is true of three pages, and every one of them is either recorded orphan debt or
    a deliberately internal door. It goes green on its own as ORPHAN_DEBT shrinks, which
    is what a debt register should do to the controls around it.
    """
    unreached = set()
    for area, path in renderer.pages():
        if "active" not in _nav_block(path.read_text(encoding="utf-8")):
            unreached.add(area)
    unexplained = unreached - set(reg.ORPHAN_DEBT) - set(reg.INTERNAL_DOORS)
    assert not unexplained, (
        f"pages that cannot say 'you are here' and are not recorded as debt: {sorted(unexplained)}"
    )


def _nav_block(html: str) -> str:
    m = re.search(
        re.escape(reg.NAV_START) + r"(.*?)" + re.escape(reg.NAV_END), html, re.S
    )
    assert m, "no rendered nav region found"
    return m.group(1)


# --- mutations (R15) -------------------------------------------------------
def test_MUTATION_a_hand_edited_nav_fires(tree):
    # DERIVED. This named site/company/index.html, which was deleted on 2026-08-20 and took
    # both mutation proofs down with it -- the same stale-literal defect these tests exist to
    # catch, in the tests themselves.
    victim = next(p for p in sorted(tree.rglob("index.html"))
                  if reg.NAV_START in p.read_text(encoding="utf-8"))
    # THE LABEL IS DERIVED, and the reason is that this control silently stopped working when it
    # was not. It corrupted the literal string `>Proof</a>`; the 2026-08-19 fold took Proof off
    # the nav, so the replace matched nothing, the file was rewritten unchanged, and `stale()`
    # correctly reported no drift -- a MUTATION test that mutates nothing and passes for the
    # wrong reason, which is the FAIL-SILENT shape R15 names. Taking a label from the register
    # means the corruption is always real.
    label = next(i.label for i in reg.CANONICAL_NAV if i.area != "/")
    before = victim.read_text()
    after = before.replace(f'class="nav-link">{label}</a>', f'class="nav-link">{label}XX</a>')
    assert after != before, (
        f"the mutation changed nothing -- {label!r} is not in the rendered nav, so this test "
        "would pass without testing anything"
    )
    victim.write_text(after)
    victim_area = "/" if victim.parent == tree else "/" + victim.parent.relative_to(tree).as_posix() + "/"
    assert victim_area in renderer.stale(tree)


def test_MUTATION_a_deleted_nav_marker_fires(tree):
    # DERIVED. This named site/company/index.html, which was deleted on 2026-08-20 and took
    # both mutation proofs down with it -- the same stale-literal defect these tests exist to
    # catch, in the tests themselves.
    victim = next(p for p in sorted(tree.rglob("index.html"))
                  if reg.NAV_START in p.read_text(encoding="utf-8"))
    victim.write_text(victim.read_text().replace(reg.NAV_START, ""))
    victim_area = "/" if victim.parent == tree else "/" + victim.parent.relative_to(tree).as_posix() + "/"
    assert victim_area in renderer.stale(tree)


def test_MUTATION_a_new_page_with_no_nav_block_at_all_fires(tree):
    (tree / "newcomer").mkdir()
    (tree / "newcomer" / "index.html").write_text("<html><body>no nav here</body></html>")
    with pytest.raises(ValueError, match="no site-level <nav>"):
        renderer.stale(tree)


def test_MUTATION_moving_a_tab_in_the_register_makes_every_page_stale(tree):
    """The property Step 0 exists to buy: a tab move is ONE line, and it reaches every
    page. If this mutation left pages green, the nav would not really derive from the
    register."""
    before = renderer.stale(tree)
    assert before == [], before
    original = reg.CANONICAL_NAV
    try:
        reg.CANONICAL_NAV = original + (reg.NavItem("Knowledge", "/knowledge/"),)
        after = renderer.stale(tree)
    finally:
        reg.CANONICAL_NAV = original
    # DERIVED. This was `>= 14`, a pin on the page count of the day, and the 2026-08-20 fold
    # took the site to five nav-rendered pages -- so the control failed for the one reason it
    # must not, a legitimate IA change. What it actually has to prove is that the move reaches
    # EVERY page that renders the nav, whatever that number is today.
    nav_pages = [area for area, _ in renderer.pages()]
    assert sorted(after) == sorted(nav_pages), (
        f"a tab move reached {sorted(after)} but the nav is rendered on {sorted(nav_pages)} -- "
        "a page that does not go stale is a page whose nav does not derive from the register"
    )
    assert len(after) >= 5, f"only {len(after)} page(s) render the nav at all: {after}"
    assert renderer.stale(tree) == [], "the register did not restore"


# ---------------------------------------------------------------------------
# 3. The director-record condition (ruled 2026-08-18, reserved class 3)
#
# DISCHARGED 2026-08-20 BY DELETION, and three tests here are retired with it. The condition
# was that /director/ may not be made CRAWLABLE until the director has read its rendered
# content -- a reserved class 3 item (an irretractable public claim in the company's name).
# The page is now deleted and 301'd to /harness/, so it cannot be crawled by any route: a
# stronger guarantee than the condition asked for, arrived at from the other direction.
#
# What survives is the release machinery itself (director_record_release,
# director_record_publication_violations and their fail-closed proofs below), because the
# condition would apply again the moment any director-facing record is published. What is gone
# is the three tests that asserted the state of a specific deleted page.
# ---------------------------------------------------------------------------
def test_MUTATION_advertising_the_director_record_without_a_release_fires(tree):
    sitemap = tree / "sitemap.xml"
    sitemap.write_text(
        sitemap.read_text().replace(
            "</urlset>", f"<url><loc>{reg.CANONICAL_HOST}/director/</loc></url></urlset>"
        )
    )
    problems = reg.director_record_publication_violations(tree)
    assert any("sitemap" in p for p in problems), problems


def test_MUTATION_removing_it_from_internal_doors_without_a_release_fires(tree, monkeypatch):
    monkeypatch.setattr(reg, "INTERNAL_DOORS", ("/shadow/",))
    problems = reg.director_record_publication_violations(tree)
    assert any("INTERNAL_DOORS" in p for p in problems), problems


def test_a_real_release_record_releases_it(tmp_path, tree):
    """R11, no orphan transitions: a hold must define -- and have TESTED -- what its
    release actually triggers. Here it is. Without this, the condition could be
    discharged by a record that does nothing, and nobody would know."""
    record = tmp_path / "release.json"
    record.write_text(json.dumps({
        "released": True,
        "director_words": "read it, publish it",
        "render_shown": "docs/observability/director_record_render_2026-08-18.txt",
    }))
    assert reg.director_record_release(record) is not None


@pytest.mark.parametrize("payload", [
    '{"released": false}',
    '{"released": true}',                                    # no evidence of what was shown
    '{"released": true, "director_words": "go"}',            # half the evidence
    '{"released": "yes", "director_words": "go", "render_shown": "x"}',  # not the boolean
    'not json at all',
    '[]',
])
def test_MUTATION_FAIL_SILENT_a_weak_or_broken_release_record_does_not_release(tmp_path, payload):
    """An unreadable check is a FAILED check. Every one of these must read as
    NOT RELEASED -- publishing on a record nobody can parse is the failure that
    matters, and a truthy-string `"released": "yes"` is how it would arrive."""
    record = tmp_path / "release.json"
    record.write_text(payload)
    assert reg.director_record_release(record) is None


def test_MUTATION_FAIL_SILENT_a_missing_release_record_does_not_release(tmp_path):
    assert reg.director_record_release(tmp_path / "nope.json") is None


def test_live_pixel_verify_shares_this_registers_internal_doors():
    """One definition, not two. `live_pixel_verify.py` used to carry its own copy;
    two lists that must agree are two lists that will not."""
    import live_pixel_verify

    assert live_pixel_verify.INTERNAL_DOORS is reg.INTERNAL_DOORS


def test_site_reachability_shares_this_registers_internal_doors():
    """The THIRD copy, found by the write-time reuse gate rather than by this atom --
    `tools/site_reachability.py` had its own hand-written {director, shadow}. On a
    reachability control that is the worse one: an internal door that later goes public
    would go on being excluded, so nothing would check a reader could get to it.
    """
    from tools.site_reachability import SITEMAP_DECLARED_EXCLUSIONS as excl

    for door in reg.INTERNAL_DOORS:
        assert door.strip("/") + "/" in excl, f"{door} lost its reachability exclusion"


def test_MUTATION_a_new_internal_door_reaches_site_reachability_without_editing_it(monkeypatch):
    """The property the shared definition buys: declaring a door INTERNAL in the register
    must reach the reachability control on its own. If this fires, someone re-typed the
    list somewhere and the three copies are back."""
    import importlib

    from tools import site_reachability

    monkeypatch.setattr(reg, "INTERNAL_DOORS", reg.INTERNAL_DOORS + ("/backstage/",))
    fresh = site_reachability._internal_door_exclusions()
    assert "backstage/" in fresh, fresh
    assert "ia_register.py declares /backstage/ INTERNAL" in fresh["backstage/"], (
        "a door with no reason recorded here must still EXCLUDE, saying so -- dropping it "
        "silently would report a deliberate internal door as an orphan"
    )
    importlib.reload(site_reachability)


# RETIRED 2026-08-20 with the redirects themselves. Three tests here policed properties of the
# RETIRED state: that no nav entry pointed at a 301 source, that the control fired when one did,
# and that a retired page highlighted the door it folded into. `site/_redirects` went from forty
# rules to two (favicon and www, neither a page), so there is no retired page, no fold, and no
# 301 source to point at. The director's ruling: "no one has ever visited those URLs. There is
# no history to protect, so stop protecting it."
#
# What replaces them is smaller and asks a better question -- tools/reader_reachability.py walks
# the built site from the front door and every page must be reachable, which is the property the
# three above were approximating.
def test_the_only_redirects_left_are_the_ones_a_reader_actually_needs():
    """A guard on the SHAPE, not the count: this file is where redirects come back one
    convenient exception at a time. Both survivors are paths a browser or a person produces
    unprompted -- not URLs preserved because deleting them felt risky."""
    lines = [l.strip() for l in (SITE / "_redirects").read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.strip().startswith("#")]
    assert len(lines) <= 1, (
        f"{len(lines)} redirect rules; the ruling of 2026-08-20 left ONE. A new one needs an "
        f"answer to 'whose journey breaks without it, today?' -- not a page that used to exist. "
        f"Rules: {lines}"
    )
    sources = [l.split()[0] for l in lines]
    assert any("favicon" in s for s in sources), "the favicon rule went -- browsers request it unprompted"
    # The www rule was kept for half a day on the reasoning that "people type www", then deleted
    # once checked: www.poesys.net has no DNS record, so the rule could never fire. If it comes
    # back it needs a checked reason, which is why its absence is asserted rather than tolerated.
    assert not any("www." in s for s in sources), (
        "a www rule is back. www.poesys.net had no DNS record on 2026-08-20, so such a rule "
        "cannot fire -- if that has changed, say so here rather than restoring it silently"
    )
