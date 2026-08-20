#!/usr/bin/env python3
"""R15 proof for the director's rule of 2026-08-20:

    "a surface no reader can reach must never be able to block publishing."

THE SHAPE OF THE DEFECT IT CLOSES
---------------------------------
A gate compared the dashboard's headline figures to the exec summary in
`docs/observability/run_insights.json` and alarmed when they drifted. `/project` -- the
dashboard page -- had 301'd to `/proof/` since 2026-07-23, and no page on the site fetches
run_insights.json at all. So the comparison's two sides were a redirected page and a file
with no reader, and its entire output was keeping them agreeing with each other.

Nothing failed loudly enough to prompt "who is this for?", because a surface with no reader
accretes checks and alarms exactly like a real one. This control asks that question at the
one moment the cost becomes acute: when the surface can stop the site publishing.

WHY THE CHECK LIST IS PARSED FROM THE VERDICT, NOT LISTED HERE
--------------------------------------------------------------
A hand-written list of "the checks that block publishing" is a SECOND definition of the
verdict, and second definitions drift from the first silently -- this project has found that
defect in its own controls repeatedly (four door tests hard-coding the nav; a ceiling test
that would have gone red because the promotion SUCCEEDED). So the conjunction in
`generate()` is read out of the source and IS the list. Add an eighth check to the verdict
without declaring it and this goes red on the next commit.
"""
from __future__ import annotations

import ast
import inspect

import pytest

from tools import generate_dashboard_data as gdd
from tools import reader_reachability as rr


def _checks_in_the_verdict() -> set:
    """Every `_check_*` call whose result reaches generate()'s returned verdict.

    Read from the AST rather than by regex over the text: a check named inside a comment or
    a docstring is not a blocker, and the retirement note left in this exact function names
    two of them."""
    tree = ast.parse(inspect.getsource(gdd.generate))
    assigned = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                assigned.setdefault(target.id, []).append(node.value)

    verdicts = assigned.get("consistency_ok") or []
    assert verdicts, "generate() no longer computes `consistency_ok` -- update this control"
    names = set()
    for expr in verdicts:
        for sub in ast.walk(expr):
            if isinstance(sub, ast.Name):
                for value in assigned.get(sub.id, []):
                    for call in ast.walk(value):
                        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) \
                                and call.func.id.startswith("_check_"):
                            names.add(call.func.id)
    return names


# ---------------------------------------------------------------------------
# The three ratchet directions
# ---------------------------------------------------------------------------
def test_MUTATION_every_check_in_the_publish_verdict_declares_the_page_it_guards():
    """Direction 1: an undeclared blocker. This is how the retired comparison got in --
    it was added to the conjunction and never had to say who it was for."""
    undeclared = _checks_in_the_verdict() - set(gdd.PUBLISH_VERDICT_CHECKS)
    assert not undeclared, (
        f"{sorted(undeclared)} can stop the site publishing but do not name a reader-facing "
        "page. Add an entry to PUBLISH_VERDICT_CHECKS naming the page whose figures go wrong "
        "when the check fires -- or, if there is no such page, the check does not belong in "
        "the verdict."
    )


def test_MUTATION_every_declared_page_is_one_a_reader_can_actually_open():
    """Direction 2: THE ruling. Measured by walking the built site from the front door, not
    by asserting the page file exists -- `/project/index.html` existed for the whole month
    nobody could reach it."""
    reachable = rr.reachable()
    unreachable = {
        check: page for check, (page, _why) in gdd.PUBLISH_VERDICT_CHECKS.items()
        if page not in reachable
    }
    assert not unreachable, (
        f"these publish blockers guard pages no reader can reach: {unreachable}. "
        "Either restore the route to the page, or retire the check -- a surface with no "
        "reader must not be able to stop the site publishing (director, 2026-08-20)."
    )


def test_MUTATION_a_declaration_for_a_retired_check_ALSO_fails():
    """Direction 3, the one that rots quietly. Without it the table drifts into a record of
    what the gate used to do, and re-reading it years later tells you nothing true."""
    stale = set(gdd.PUBLISH_VERDICT_CHECKS) - _checks_in_the_verdict()
    assert not stale, (
        f"{sorted(stale)} are declared as publish blockers but no longer appear in "
        "generate()'s verdict. Delete the entries: a declaration nobody honours is worse "
        "than none, because it reads as coverage."
    )


def test_the_retired_exec_summary_comparison_is_not_declared():
    """The specific instance, named. If `_check_consistency` returns to the module it must
    not quietly reappear here as though it had always been legitimate."""
    assert "_check_consistency" not in gdd.PUBLISH_VERDICT_CHECKS
    assert not hasattr(gdd, "_check_consistency"), (
        "the dashboard-vs-exec-summary comparison is back; it was retired 2026-08-20 because "
        "no reader could reach either side of it"
    )


# ---------------------------------------------------------------------------
# The oracle underneath -- it decides whether a check lives or dies, so it is driven hardest
# ---------------------------------------------------------------------------
def _site(tmp_path, pages: dict, redirects: str = ""):
    for url, links in pages.items():
        d = tmp_path if url == "/" else tmp_path / url.strip("/")
        d.mkdir(parents=True, exist_ok=True)
        body = "".join(f'<a href="{h}">x</a>' for h in links)
        (d / "index.html").write_text(f"<html><body>{body}</body></html>", encoding="utf-8")
    if redirects:
        (tmp_path / "_redirects").write_text(redirects, encoding="utf-8")
    return tmp_path


def test_a_page_linked_from_the_front_door_is_reachable(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "MIN_PLAUSIBLE_REACHABLE", 1)
    site = _site(tmp_path, {"/": ["./a/"], "/a/": []})
    assert rr.reachable(site) == {"/", "/a/"}


def test_MUTATION_a_page_linked_only_from_an_unreachable_page_is_NOT_reachable(tmp_path, monkeypatch):
    """Transitive closure from the FRONT DOOR, not 'is anything pointing at it'. `/project/`
    was linked from `/director/` and `/shadow/`; both were themselves unreachable, and
    counting inbound links would have called it live."""
    monkeypatch.setattr(rr, "MIN_PLAUSIBLE_REACHABLE", 1)
    site = _site(tmp_path, {"/": [], "/orphan/": ["../buried/"], "/buried/": []})
    assert rr.reachable(site) == {"/"}


def test_MUTATION_a_link_to_a_REDIRECT_SOURCE_does_not_make_it_reachable(tmp_path, monkeypatch):
    """The exact reason the dashboard page read as live for a month: pages still linked to
    `/project/`, but `site/_redirects` sent every reader who followed one to `/proof/`."""
    monkeypatch.setattr(rr, "MIN_PLAUSIBLE_REACHABLE", 1)
    site = _site(tmp_path, {"/": ["./gone/"], "/gone/": []},
                 redirects="# c\n/gone /kept/ 301\n/gone/* /kept/ 301\n")
    assert rr.reachable(site, site / "_redirects") == {"/"}


def test_a_dynamic_js_href_is_not_counted_as_a_route(tmp_path, monkeypatch):
    """Under-claiming reachability is the fail-closed direction here: it over-reports
    blockers, and a false report costs a conversation while a missed one costs an outage."""
    monkeypatch.setattr(rr, "MIN_PLAUSIBLE_REACHABLE", 1)
    site = tmp_path
    (site / "index.html").write_text(
        '<html><body><a href="./x/"+esc(id)+"/">x</a></body></html>', encoding="utf-8")
    (site / "x").mkdir()
    (site / "x" / "index.html").write_text("<html></html>", encoding="utf-8")
    assert rr.reachable(site) == {"/"}


def test_MUTATION_FAIL_CLOSED_a_missing_front_door_raises(tmp_path):
    """An unavailable check is a FAILED check. Returning an empty set here would mark every
    publish blocker as guarding nothing and invite retiring all seven."""
    with pytest.raises(rr.ReachabilityUnavailable):
        rr.reachable(tmp_path)


def test_MUTATION_FAIL_CLOSED_an_implausibly_small_walk_raises(tmp_path):
    """The subtler half. A front door that parses but yields two pages is a broken WALK, not
    a shrunken site -- and it fails in the direction that looks like a clean result."""
    site = _site(tmp_path, {"/": ["./a/"], "/a/": []})
    with pytest.raises(rr.ReachabilityUnavailable) as exc:
        rr.reachable(site)
    assert "broken walk" in str(exc.value)


def test_the_live_site_walk_agrees_with_the_five_tab_nav():
    """Independence: the oracle is checked against the nav register, which is a DIFFERENT
    definition of the door set, so a bug that lost half the site would have to occur in both
    to pass."""
    import sys
    sys.path.insert(0, str(rr.SITE))
    from ia_register import CANONICAL_NAV

    reach = rr.reachable()
    for item in CANONICAL_NAV:
        assert item.area in reach, (
            f"{item.area} is a canonical nav door but the walk cannot reach it from the "
            "front door -- either the nav is not rendered on the home page, or the walk is wrong"
        )
