#!/usr/bin/env python3
"""The IA register's controls (SITE4 / Step 0 of the website structure programme).

WHAT THIS POLICES
-----------------
1. **The three-state register (C3).** Every deployed area is ADVERTISED, INTERNAL or
   RETIRED; an area in none of the three is the failure. An ADVERTISED area with no
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
    assert set(states.values()) <= {reg.ADVERTISED, reg.INTERNAL, reg.RETIRED,
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
    assert len(by_state[reg.ADVERTISED]) >= 4, by_state
    assert by_state[reg.INTERNAL] == ["/director/", "/shadow/"], by_state
    assert by_state[reg.RETIRED], "the retirement convention has no members -- did a migration delete instead of redirect?"


def test_orphan_debt_is_exactly_the_current_orphans():
    """Shrink-only. An entry that is no longer an orphan is stale credit; an orphan
    with no entry is new debt arriving unannounced. Both are violations, and
    `register_violations()` reports both -- proven by the two mutations below."""
    states = reg.classify()
    reachable = reg.nav_reachable()
    orphans = {a for a, s in states.items() if s == reg.ADVERTISED and a not in reachable}
    assert orphans == set(reg.ORPHAN_DEBT), (
        f"orphans={sorted(orphans)} debt={sorted(reg.ORPHAN_DEBT)}"
    )


def test_every_debt_entry_names_the_step_that_clears_it():
    for area, owner in reg.ORPHAN_DEBT.items():
        assert re.match(r"SITE\d+ -- \S", owner), (
            f"{area}'s debt entry must name the owning step, got {owner!r} -- "
            "a debt register with no owner is a list of complaints"
        )


def test_no_nav_entry_points_at_a_redirect_source():
    assert reg.no_retired_nav_links() == []


def test_the_canonical_nav_only_routes_to_deployed_areas():
    deployed = set(reg.deployed_areas())
    for item in reg.CANONICAL_NAV:
        assert item.area in deployed, (
            f"nav routes to {item.area}, which is not deployed -- brief §9.2 forbids "
            "an intermediate state where the nav points at a page that does not exist"
        )


def test_the_nav_exemption_is_exactly_one_declared_mirror():
    assert set(reg.NAV_EXEMPT) == {"/shadow/"}, (
        "the exemption list is where a nav control goes to die -- one member, declared, "
        f"with its reason. Got {sorted(reg.NAV_EXEMPT)}"
    )
    assert len(reg.NAV_EXEMPT["/shadow/"]) > 40, "an exemption without a reason is an allowlist"


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


def test_MUTATION_a_nav_entry_pointing_at_a_redirect_source_fires(tree, monkeypatch):
    retired = next(iter(reg.retired_areas(tree / "_redirects")))
    monkeypatch.setitem(reg.LEGACY_TAIL, "/company/", (("Ghost door", retired),))
    problems = reg.no_retired_nav_links(tree)
    assert any(retired in p and "301 source" in p for p in problems), problems


@pytest.mark.parametrize("victim", ["sitemap.xml", "_redirects", "index.html"])
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


def test_the_generated_evidence_page_carries_the_register_nav():
    """/evidence/ is rewritten every ~30 minutes by its generator, so it is the one
    page a hand edit cannot hold. Its nav must come from the register too."""
    html = (SITE / "evidence" / "index.html").read_text(encoding="utf-8")
    assert reg.render_nav("/evidence/", indent="") in html, (
        "the generated evidence page's nav is not the register's render -- "
        "check tools/generate_evidence_data.py::render_html"
    )


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


def test_a_retired_page_highlights_the_door_it_folded_into():
    """A reader who lands on a retired page is looking at content that now lives
    behind another door; highlighting a door that is no longer in the IA would be a
    lie the register can avoid telling."""
    states = reg.classify()
    retired = [a for a, s in states.items() if s == reg.RETIRED]
    assert retired, "no retired areas -- this control would be vacuous"
    for area in retired:
        target = reg.active_target(area)
        assert target != area, f"{area} folds into nothing"
        rendered = reg.render_nav(area)
        assert f'"{reg._relative(target, area)}" class="nav-link active"' in rendered, rendered


def _nav_block(html: str) -> str:
    m = re.search(
        re.escape(reg.NAV_START) + r"(.*?)" + re.escape(reg.NAV_END), html, re.S
    )
    assert m, "no rendered nav region found"
    return m.group(1)


# --- mutations (R15) -------------------------------------------------------
def test_MUTATION_a_hand_edited_nav_fires(tree):
    victim = tree / "company" / "index.html"
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
    assert "/company/" in renderer.stale(tree)


def test_MUTATION_a_deleted_nav_marker_fires(tree):
    victim = tree / "company" / "index.html"
    victim.write_text(victim.read_text().replace(reg.NAV_START, ""))
    assert "/company/" in renderer.stale(tree)


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
    assert len(after) >= 14, f"a tab move reached only {len(after)} page(s): {after}"
    assert renderer.stale(tree) == [], "the register did not restore"


# ---------------------------------------------------------------------------
# 3. The director-record condition (ruled 2026-08-18, reserved class 3)
# ---------------------------------------------------------------------------
def test_the_director_record_is_not_crawlable_yet():
    assert reg.director_record_publication_violations() == []


def test_the_director_record_is_still_internal_and_noindexed():
    """The state the condition protects. If this ever goes green because /director/
    was published, the release record below is what must have made it legal."""
    if reg.director_record_release() is not None:
        pytest.skip("the director has released the record; the condition is discharged")
    assert "/director/" in reg.INTERNAL_DOORS
    assert "/director/" not in reg.advertised_areas()
    assert "noindex" in (SITE / "director" / "index.html").read_text(encoding="utf-8")


def test_MUTATION_advertising_the_director_record_without_a_release_fires(tree):
    sitemap = tree / "sitemap.xml"
    sitemap.write_text(
        sitemap.read_text().replace(
            "</urlset>", f"<url><loc>{reg.CANONICAL_HOST}/director/</loc></url></urlset>"
        )
    )
    problems = reg.director_record_publication_violations(tree)
    assert any("sitemap" in p for p in problems), problems


def test_MUTATION_dropping_the_noindex_without_a_release_fires(tree):
    victim = tree / "director" / "index.html"
    victim.write_text(victim.read_text().replace("noindex", "index"))
    problems = reg.director_record_publication_violations(tree)
    assert any("noindex" in p for p in problems), problems


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
