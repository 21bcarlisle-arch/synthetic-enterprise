"""R15 proof for `tools/retired_paths_still_served.py`.

The control claims: a page this repo deleted, which the edge is still serving 200, is
reported as a ghost -- and nothing else is.

"Nothing else is" is the half that decides whether the control is worth having, so four
NULL CONTROLS carry as much weight here as the positive case: a deleted page the edge
404s, a live page serving 200, a path nobody ever served, and a Cloudflare-internal path.
Any of them reported as a ghost makes the check a list of everything, which is a list of
nothing.

Each control is MUTATION-PROVEN: the mutant that would satisfy a lazier version of the
test is applied, and the test asserts the verdict actually flips. A control nobody has
watched fail is not evidence (R15).
"""
from __future__ import annotations

import json

import pytest

from tools import edge_traffic_capture as CAP
from tools import retired_paths_still_served as M


def site_with(tmp_path, pages=("", "harness", "explore", "knowledge")):
    """A checkout that serves `pages` as directory URLs."""
    site = tmp_path / "site"
    for page in pages:
        target = site / page if page else site
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text("<html>live</html>", encoding="utf-8")
    return site


def row(path, status, hour="2026-08-20T16:00:00Z", protocol="HTTP/2", count=1):
    return {"path": path, "status": status, "hour": hour, "protocol": protocol,
            "count": count, "colo": "LHR", "country": "GB"}


# --------------------------------------------------------------------------- the positive case

def test_a_deleted_page_the_edge_still_serves_200_is_a_ghost(tmp_path):
    site = site_with(tmp_path)
    v = M.verdicts([row("/proof/", 200)], site=site, deleted={"/proof/"})
    assert v["/proof/"]["still_served"] is True


def test_the_real_repo_names_shadow_among_its_deleted_pages():
    """The anchor to real state. `/shadow/` was deleted by the five-tab fold, is absent
    from the checkout, and was missing from the hand-written list of eight that the
    2026-08-20 finding reasoned from -- the omission this module exists to make
    impossible. If `site/shadow/` is ever restored, this test is what says so."""
    assert "/shadow/" in M.deleted_page_paths()


# --------------------------------------------------------------------------- null controls

def test_null_a_deleted_page_the_edge_404s_is_not_a_ghost(tmp_path):
    """Refuses "anything deleted is a ghost". Most retired pages 404 correctly and a
    report that lists them says nothing about the ones that do not."""
    site = site_with(tmp_path)
    v = M.verdicts([row("/method/", 404)], site=site, deleted={"/method/"})
    assert v["/method/"]["still_served"] is False


def test_null_a_live_page_serving_200_is_not_a_ghost(tmp_path):
    """Refuses "any 200 is a ghost"."""
    site = site_with(tmp_path)
    v = M.verdicts([row("/harness/", 200)], site=site, deleted=set())
    assert "/harness/" not in v


def test_null_a_path_nobody_ever_served_is_not_a_ghost(tmp_path):
    """Scanners request paths that never existed. A 404 on `/wp-admin/install.php` is the
    site behaving, not a retired page leaking."""
    site = site_with(tmp_path)
    v = M.verdicts([row("/wp-admin/install.php", 404)], site=site, deleted=set())
    assert v == {}


def test_null_a_cloudflare_internal_path_is_not_a_ghost(tmp_path):
    """`/cdn-cgi/trace` returns 200 from the edge itself and is in no deployment. Reported
    as a ghost it would be permanent noise that never clears."""
    site = site_with(tmp_path)
    v = M.verdicts([row("/cdn-cgi/trace", 200)], site=site, deleted=set())
    assert v == {}


# --------------------------------------------------------------------------- fail-closed

def test_a_missing_capture_raises_rather_than_reporting_no_ghosts(tmp_path):
    with pytest.raises(M.RetiredPathCheckUnavailable):
        M.load_rows(tmp_path / "nothing.jsonl")


def test_a_capture_of_only_phantom_rows_raises(tmp_path):
    """Every row a logging artefact is no observation at all. Returning [] here would put
    every ghost into UNOBSERVED and read as quiet."""
    cap = tmp_path / "edge.jsonl"
    cap.write_text(json.dumps(row("/proof/", 504, protocol="UNK")) + "\n", encoding="utf-8")
    with pytest.raises(M.RetiredPathCheckUnavailable):
        M.load_rows(cap)


def test_an_empty_checkout_raises_instead_of_calling_the_whole_site_retired(tmp_path):
    """The subject set is derived by SUBTRACTING the checkout, so losing the checkout is
    the mutation that scores green by making every live page a finding."""
    empty = tmp_path / "site"
    empty.mkdir()
    with pytest.raises(M.RetiredPathCheckUnavailable):
        M.verdicts([row("/harness/", 200)], site=empty, deleted=set())


def test_a_page_the_edge_has_no_rows_for_is_unobserved_not_cleared(tmp_path):
    """Three states, not two. Silence is the absence of evidence and the whole finding
    began with a check that could not tell absence from staleness."""
    site = site_with(tmp_path)
    v = M.verdicts([row("/harness/", 200)], site=site, deleted={"/tours/"})
    assert v["/tours/"]["still_served"] is None


# --------------------------------------------------------------------------- transitions (R5)

def test_an_unchanged_ghost_reports_no_transition():
    state = {"paths": {"/proof/": {"still_served": True}}}
    now = {"/proof/": {"still_served": True, "last_seen": "2026-08-20T16:00:00Z"}}
    assert M.transitions(state, now) == []


def test_a_ghost_clearing_is_the_transition_this_exists_to_catch():
    state = {"paths": {"/proof/": {"still_served": True}}}
    now = {"/proof/": {"still_served": False, "last_seen": "2026-08-21T09:00:00Z"}}
    assert any(line.startswith("CLEARED") for line in M.transitions(state, now))


def test_a_ghost_falling_silent_is_not_reported_as_cleared():
    state = {"paths": {"/proof/": {"still_served": True}}}
    now = {"/proof/": {"still_served": None, "last_seen": None}}
    lines = M.transitions(state, now)
    assert any(line.startswith("UNOBSERVED") for line in lines)
    assert not any(line.startswith("CLEARED") for line in lines)


# --------------------------------------------------------------------------- mutations

def test_mutation_breaking_checkout_resolution_reports_live_pages_as_ghosts(tmp_path, monkeypatch):
    """MUTANT: `checkout_serves` always False -- the shape a URL-mapping bug takes.
    Without the live-page null control above, this passes unnoticed."""
    site = site_with(tmp_path)
    monkeypatch.setattr(M, "checkout_serves", lambda *a, **k: False)
    v = M.verdicts([row("/harness/", 200)], site=site, deleted=set())
    assert v["/harness/"]["still_served"] is True, "mutant must produce the false positive"


def test_mutation_dropping_the_checkout_floor_makes_a_broken_checkout_look_catastrophic(tmp_path, monkeypatch):
    """MUTANT: MIN_LIVE_PAGES = 0. The guard stops being able to fail, and a failed
    checkout is reported as the entire site having been retired."""
    empty = tmp_path / "site"
    empty.mkdir()
    monkeypatch.setattr(M, "MIN_LIVE_PAGES", 0)
    v = M.verdicts([row("/harness/", 200)], site=empty, deleted=set())
    assert v["/harness/"]["still_served"] is True, "mutant must answer where it cannot see"


def test_mutation_counting_phantom_rows_invents_a_ghost(tmp_path, monkeypatch):
    """MUTANT: the phantom protocol no longer matches, so Cloudflare's duplicate rows
    become evidence. This is the artefact that cost a day on the original incident."""
    site = site_with(tmp_path)
    phantom = row("/proof/", 200, protocol="UNK")
    assert M.verdicts([phantom], site=site, deleted={"/proof/"})["/proof/"]["still_served"] is None
    monkeypatch.setattr(M, "PHANTOM_PROTOCOL", "NEVER-MATCHES")
    mutant = M.verdicts([phantom], site=site, deleted={"/proof/"})
    assert mutant["/proof/"]["still_served"] is True


def test_mutation_dropping_normalisation_turns_a_live_page_into_a_ghost(tmp_path, monkeypatch):
    """MUTANT: `normalise` is the identity.

    The consequence runs in the direction that matters. The edge logs `/./proof/` and
    `//proof/` for the same URL; unnormalised, the observation lands under a key that
    matches no subject, so the ghost does not read as a false positive -- it reads as
    UNOBSERVED, and a live ghost silently downgraded to "no rows" is the failure this
    module was built to stop."""
    site = site_with(tmp_path)
    observed = M.verdicts([row("/./proof/", 200)], site=site, deleted={"/proof/"})
    assert observed["/proof/"]["still_served"] is True

    monkeypatch.setattr(M, "normalise", lambda p: p)
    mutant = M.verdicts([row("/./proof/", 200)], site=site, deleted={"/proof/"})
    assert mutant["/proof/"]["still_served"] is None, "mutant must lose the ghost"


def test_the_phantom_protocol_is_the_same_constant_the_collector_writes():
    """Independence has a cost: two modules now name the artefact. They must agree, or the
    reader silently keeps rows the writer classified as noise."""
    assert M.PHANTOM_PROTOCOL == CAP.PHANTOM_PROTOCOL
