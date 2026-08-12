"""R15 for the published provenance banner (background/publish_provenance.py).

The ruling names one cardinal sin by name -- **fake-fresh: re-stamping stale runs** -- and
cites this weekend's four-times-republished figure as the counterexample. So the tests below
are not "does it write a JSON file"; they are attempts to COMMIT that sin through the API and
assertions that the API refuses to let them.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from background import publish_provenance as prov

# PUBLISHER-SHAPED, NOT FIXTURE-SHAPED (2026-08-11). The recorders now REFUSE a run id or
# sha that no run could have produced, because the literal "run_verified.json" reached the
# live banner and was pushed to origin. These stand-ins keep the a/b contrast these tests
# are built on while being values the publisher would actually emit; existence of the sha is
# not checked at the write, so they need not be commits in this repo.
SHA_A = "a1b2c3d4e"
SHA_B = "b2c3d4e5f"
RUN_A = "run_output_{}_20260809T031627Z.json".format(SHA_A)
RUN_B = "run_output_{}_20260810T041627Z.json".format(SHA_B)


def _at(minutes):
    return datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _p(tmp_path):
    return tmp_path / "publish_provenance.json"


def test_a_verified_publish_advances_freshness(tmp_path):
    p = _p(tmp_path)
    state = prov.record_verified(run_id=RUN_A, git_commit=SHA_A, path=p, now=_at(0))
    assert state["verification_state"] == prov.STATE_VERIFIED
    assert state["showing_run"]["run_id"] == RUN_A
    assert state["last_verified"]["git_commit"] == SHA_A
    assert state["paused_since"] is None


def test_a_pause_cannot_move_the_served_run_by_a_byte(tmp_path):
    """THE CARDINAL SIN, attempted directly. A red gate must never be able to make the served
    figures look newer than the last run that was actually verified."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, path=p, now=_at(0))
    before = json.loads(p.read_text())

    for i in range(1, 40):
        prov.record_paused(reason="scoped gate red", path=p, now=_at(i))

    after = json.loads(p.read_text())
    assert after["showing_run"] == before["showing_run"]
    assert after["last_verified"] == before["last_verified"]
    assert after["verification_state"] == prov.STATE_PAUSED


def test_paused_since_is_stamped_once_not_re_stamped_every_cycle(tmp_path):
    """The same sin wearing the opposite coat. A banner that reads 'paused since 30 seconds
    ago' for 25 hours is a fresh-looking lie about staleness -- the pause timestamp must be the
    TRANSITION, not the last time anything ran."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, path=p, now=_at(0))
    first = prov.record_paused(path=p, now=_at(5))["paused_since"]
    for i in range(6, 60):
        prov.record_paused(path=p, now=_at(i))
    assert prov.read(p)["paused_since"] == first
    assert "12:05" in first, first


def test_recovery_clears_the_pause_and_advances(tmp_path):
    """R11: the RELEASE of a hold must have a tested effect. A pause that could never clear
    would be an orphan transition -- and a site permanently branded stale is as ignored as one
    that never says anything."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, path=p, now=_at(0))
    prov.record_paused(path=p, now=_at(5))
    state = prov.record_verified(run_id=RUN_B, git_commit=SHA_B, path=p, now=_at(90))
    assert state["paused_since"] is None
    assert state["verification_state"] == prov.STATE_VERIFIED
    assert state["showing_run"]["run_id"] == RUN_B


def test_an_annotation_can_never_pause_or_unpause_the_site(tmp_path):
    """A noisy finding count must not become an outage, and it must not be able to launder a
    paused site into a verified-looking one either. The annotation is a different KIND of
    claim and has no write access to the state that says how fresh the numbers are."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, path=p, now=_at(0))
    prov.record_paused(path=p, now=_at(5))
    state = prov.record_annotation(open_findings=140, nonblocking_reds=["FAILED x"] * 50,
                                   path=p, now=_at(6))
    assert state["verification_state"] == prov.STATE_PAUSED
    assert state["paused_since"] is not None
    assert state["showing_run"]["run_id"] == RUN_A
    # Bounded payload, but the TOTAL is preserved -- a truncated list that also truncated the
    # count would understate repo health on the public page.
    assert len(state["annotation"]["nonblocking_reds"]) == prov.MAX_ANNOTATED_REDS
    assert state["annotation"]["nonblocking_reds_total"] == 50
    assert state["annotation"]["open_findings"] == 140


def test_a_missing_or_corrupt_file_reads_as_paused_never_as_verified(tmp_path):
    """FAIL-CLOSED. 'I cannot tell you what was verified' must render as 'nothing is
    verified'. A corrupt file that read as VERIFIED would publish a fresh-looking banner over
    an unknown state -- the cardinal sin by accident."""
    missing = tmp_path / "nope.json"
    assert prov.read(missing)["verification_state"] == prov.STATE_PAUSED
    assert prov.read(missing)["last_verified"] is None

    corrupt = _p(tmp_path)
    corrupt.write_text("{not json at all")
    assert prov.read(corrupt)["verification_state"] == prov.STATE_PAUSED

    listy = tmp_path / "listy.json"
    listy.write_text("[1,2,3]")
    assert prov.read(listy)["verification_state"] == prov.STATE_PAUSED


def test_a_test_cannot_write_the_published_provenance_claim():
    """R15 for the ISOLATION guard, caught in the act 2026-08-10.

    The publish decoupling made `_process()` stamp this file, so the ordinary publisher tests
    that drive `_process()` wrote a run id of "abc1234" into the REAL published surface — and
    the live publisher committed it as a public freshness claim. It failed to reach origin only
    because the branch happened to be diverged; nothing about the design stopped it.

    `site/data/publish_provenance.json` is therefore in `tests/conftest.py::
    _PROTECTED_WRITE_PATHS`, and this asserts the guard FIRES on it rather than trusting that
    a path added to a list is a path that is protected. A guard list only ever protects the
    paths somebody thought of; the one thing that can be proven is that this one was.
    """
    import pytest as _pytest
    with _pytest.raises(RuntimeError, match="TEST ISOLATION"):
        prov.record_paused(reason="this must never reach the live surface")


def test_the_banner_sentence_names_the_pause_and_the_run(tmp_path):
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, path=p, now=_at(0))
    verified_line = prov.banner_line(prov.read(p))
    assert "Verified" in verified_line and RUN_A in verified_line

    prov.record_paused(path=p, now=_at(5))
    paused_line = prov.banner_line(prov.read(p))
    # The three facts the ruling requires a visitor to be able to read off the page.
    assert "Verification paused since" in paused_line
    assert "12:05" in paused_line          # since WHEN
    assert RUN_A in paused_line      # showing WHAT


def test_the_python_sentence_and_the_rendered_one_carry_the_same_facts():
    """The publisher logs `banner_line`; the browser renders freshness-banner.js. Two
    hand-written sentences drift, and then the log describes a page that says something else.
    Pinned by the strings both sides must contain."""
    js = (prov.PROJECT_DIR / "site" / "assets" / "freshness-banner.js").read_text()
    for phrase in ["Verification paused since", "showing run", "last verified", "Verified "]:
        assert phrase in js, phrase


def test_the_banner_layer_fails_loud_not_silent():
    """The failure mode of a freshness widget is silent: the fetch 404s, nothing renders, and
    the page looks confidently current. The layer must render an UNKNOWN state instead and
    expose the fault for the R11 live verifier."""
    js = (prov.PROJECT_DIR / "site" / "assets" / "freshness-banner.js").read_text()
    assert "Freshness unknown" in js
    assert "PoesysFreshness" in js
    assert 'data-freshness-state' in js


def test_every_live_data_door_opts_into_the_banner():
    """A door that renders live figures without the layer is a page that cannot tell you how
    old its numbers are -- the exact defect. The front door is deliberately absent: it renders
    no live figure and carries no script by documented design."""
    site = prov.PROJECT_DIR / "site"
    for door in ["company", "proof", "world", "now", "project"]:
        html = (site / door / "index.html").read_text()
        assert "freshness-banner.js" in html, door
    assert "freshness-banner.js" not in (site / "index.html").read_text(), (
        "the front door renders no live figure and must stay script-free "
        "(DIRECTOR_RULING_FRONT_MISSION_BLOCK)")
