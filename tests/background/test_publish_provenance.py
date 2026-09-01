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


#: A complete tree identity for the red count. Every annotation test that publishes reds has to
#: carry one now, which is itself the point: there is no way to write the count without saying
#: where it came from, including by accident in a fixture.
_MEASURED_ON = {"git_commit": SHA_A, "tree_state": prov.TREE_WORKING}
#: Every `record_verified` call needs a population since 2026-08-31: a stamp that names a run and
#: says nothing about it is refused, because the page's whole claim is about that run and the run
#: itself is 27 MB and not retained. Declared once so the shape of a stamp stays one fact.
POP = {"accounts": 251, "bills": 10948, "total_revenue_gbp": 801199.0}


def _at(minutes):
    return datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _p(tmp_path):
    return tmp_path / "publish_provenance.json"


def test_a_verified_publish_advances_freshness(tmp_path):
    p = _p(tmp_path)
    state = prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    assert state["verification_state"] == prov.STATE_VERIFIED
    assert state["showing_run"]["run_id"] == RUN_A
    assert state["last_verified"]["git_commit"] == SHA_A
    assert state["paused_since"] is None


def test_a_pause_cannot_move_the_served_run_by_a_byte(tmp_path):
    """THE CARDINAL SIN, attempted directly. A red gate must never be able to make the served
    figures look newer than the last run that was actually verified."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
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
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
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
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    prov.record_paused(path=p, now=_at(5))
    state = prov.record_verified(run_id=RUN_B, git_commit=SHA_B, population=POP, path=p, now=_at(90))
    assert state["paused_since"] is None
    assert state["verification_state"] == prov.STATE_VERIFIED
    assert state["showing_run"]["run_id"] == RUN_B


def test_recovery_clears_the_REASON_and_not_only_the_flag(tmp_path):
    """The test above pauses with NO reason, so it runs at the one value where clearing and not
    clearing `paused_reason` are indistinguishable -- and for two days they were.

    Observed 2026-08-26 on the live endpoint, not inferred: `poesys.net/data/publish_
    provenance.json` served `paused_since: null`, `verification_state: "verified"` and
    `paused_reason: "scoped publish-path suite red at git=4683e68f7; blocking tests: ..."` in the
    same object. `4683e68f7` is 2026-08-24. Every green publish since had cleared the flag and
    left the sentence, so the public file asserted red and green simultaneously.

    MUTATION (must fire): drop `state["paused_reason"] = None` from `record_verified`.
    """
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    prov.record_paused(reason="scoped publish-path suite red at git=deadbeef1",
                       path=p, now=_at(5))
    paused = prov.read(p)
    # NULL CONTROL: the reason has to be THERE first, or a green assertion below proves only that
    # nothing ever wrote it.
    assert "deadbeef1" in str(paused["paused_reason"])

    state = prov.record_verified(run_id=RUN_B, git_commit=SHA_B, population=POP, path=p, now=_at(90))
    assert not state.get("paused_reason"), (
        "the pause cleared but its explanation did not: a reader fetching this file is told the "
        "gate is verified and, in the same object, why it is red -- {!r}".format(
            state.get("paused_reason"))
    )
    # And it must survive the round trip to disk, which is what the endpoint actually serves.
    assert not json.loads(p.read_text())["paused_reason"]


def test_an_annotation_can_never_pause_or_unpause_the_site(tmp_path):
    """A noisy finding count must not become an outage, and it must not be able to launder a
    paused site into a verified-looking one either. The annotation is a different KIND of
    claim and has no write access to the state that says how fresh the numbers are."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    prov.record_paused(path=p, now=_at(5))
    state = prov.record_annotation(open_findings=140, nonblocking_reds=["FAILED x"] * 50,
                                   measured_on=_MEASURED_ON, path=p, now=_at(6))
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
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
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


# `test_every_live_data_door_opts_into_the_banner` LIVED HERE and is now
# `tests/background/test_publish_provenance_banner_adoption.py`, derived rather than typed
# (2026-08-21, WORKER_FINDING_THE_FRESHNESS_BANNER_REACHES_NO_PAGE_AND_ITS_CONTROL_ASKS_FIVE_
# DELETED_DOORS). It asserted five door names -- company, proof, world, now, project -- and a
# sixth clause exempting the front door for "rendering no live figure".
#
# BOTH HALVES WERE WRONG, and the move is not tidying. `03dd8c49e` deleted all five doors on the
# director's ruling, so the check raised FileNotFoundError: its red said MISSING PAGE while the
# property was violated in a way it could not see -- the banner was on no page at all. And the
# exemption was false before that: measured over `03dd8c49e^`, the front door read
# `dashboard.json` and carried no banner, as did eighteen other live-data pages this list never
# named. It was green on a tree where four fifths of its own population was uncovered.
#
# The replacement derives the population from the pages themselves and is selected by the gate on
# any staged `site/**.html` (SITE_SURFACE_TESTS), which is the half that lets it stay true.


# ═════════════════════════════════════════════════════════════════════════════════════════════
# A RED COUNT MUST NAME THE TREE IT WAS COUNTED ON
# ═════════════════════════════════════════════════════════════════════════════════════════════
#
# THE DEFECT, observed on the live endpoint 2026-08-31. `publish_provenance.json` served
# `nonblocking_reds_total: 66` in the same object as `git_commit: "d1ba6bd46"`, and the banner
# rendered "66 non-blocking test reds elsewhere in the repository". A reader joins those two and
# concludes there are 66 reds at d1ba6bd46.
#
# There are not. `run_remainder_annotation_step` had `git_hash` in its hand, wrote it into its own
# private state file, and did NOT pass it to `record_annotation`; and the suite it counts runs with
# `cwd=PROJECT_DIR`, the shared working tree, carrying every lane's uncommitted work. That evening
# the tree also held an uncommitted widening of `tests/production_surface_guard.py` reddening ~1,760
# tests. The published 66 was counted on a tree that has never existed in the history.
#
# WHY THE OBVIOUS REPAIR IS THE ONE THAT HAD TO BE BLOCKED. Passing `git_hash` through — a
# one-line change, and the first thing anyone would write — makes it strictly WORSE: an
# unattributed number becomes a number confidently attributed to a commit that did not produce it.
# Unattributed cannot be checked; misattributed reads as established. So the leg below is aimed at
# the REPAIR, not only at the original defect, and that is what makes it able to fail against the
# next passer-by rather than only against the past.


def test_a_red_count_may_not_be_published_without_the_tree_it_was_counted_on(tmp_path):
    """FAIL-CLOSED at the write. A count with no tree is a number about no tree."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    try:
        prov.record_annotation(nonblocking_reds=["FAILED a::b"], path=p, now=_at(1))
    except ValueError as exc:
        assert "tree" in str(exc).lower()
    else:
        raise AssertionError(
            "a non-blocking red count was published with nothing saying which tree produced it, "
            "which is exactly what put 66 reds beside d1ba6bd46 on the live banner")
    # NULL CONTROL: the refusal must not have written a half-annotation on its way out.
    assert "nonblocking_reds_total" not in (prov.read(p).get("annotation") or {})


def test_naming_the_commit_alone_is_refused_because_that_is_the_misattribution(tmp_path):
    """THE LEG THAT AIMS AT THE REPAIR. `measured_on={"git_commit": sha}` is the natural
    one-line fix and it is the worse outcome: it asserts the count belongs to that commit.
    Both fields, or neither."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    try:
        prov.record_annotation(nonblocking_reds=["FAILED a::b"],
                               measured_on={"git_commit": SHA_A}, path=p, now=_at(1))
    except ValueError as exc:
        assert "tree_state" in str(exc)
    else:
        raise AssertionError(
            "a red count was accepted carrying a commit and no tree state, so it now CLAIMS to "
            "be a property of that commit -- the misattribution, published as established")


def test_the_tree_the_reds_were_counted_on_survives_to_the_served_artefact(tmp_path):
    """It has to reach the file the endpoint serves, not merely the returned dict -- a verdict
    composed into an object no published surface reads is the failure mode this repo repeats."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    prov.record_annotation(nonblocking_reds=["FAILED a::b"] * 3,
                           measured_on={"git_commit": SHA_B, "tree_state": prov.TREE_WORKING},
                           path=p, now=_at(1))
    served = json.loads(p.read_text())["annotation"]
    assert served["nonblocking_reds_total"] == 3
    assert served["nonblocking_reds_measured_on"] == {
        "git_commit": SHA_B, "tree_state": prov.TREE_WORKING}
    # AND IT MUST BE ABLE TO DISAGREE WITH THE PUBLISHED COMMIT, which is the whole point: the
    # count was taken on SHA_B's tree while SHA_A is what the banner says is showing. If these
    # two were wired to the same source the field would be decoration.
    assert json.loads(p.read_text())["showing_run"]["git_commit"] == SHA_A


def test_an_open_findings_only_annotation_still_needs_no_tree(tmp_path):
    """SCOPE CONTROL, and it is the leg that stops this becoming ceremony. `open_findings`
    counts files in `docs/staging/` -- the same on any tree at that path -- and the cheap
    findings-only refresh runs on every cycle. Requiring a tree there would have made the
    guard something a caller routes around, and a guard nobody obeys is worse than none."""
    p = _p(tmp_path)
    prov.record_verified(run_id=RUN_A, git_commit=SHA_A, population=POP, path=p, now=_at(0))
    state = prov.record_annotation(open_findings=47, path=p, now=_at(1))
    assert state["annotation"]["open_findings"] == 47
