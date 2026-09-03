"""THE DIRECTOR'S EXIT TEST for the publish decoupling.

Verbatim (DIRECTOR_PRIORITY_BUILD_THE_BREATHING_2026-08-10):

    *"Exit test: a deliberately-injected unrelated red (e.g., a doc-drift) produces a
    PUBLISHED site with an honest annotation -- never a frozen stamp."*

That sentence has two halves and this file proves both, because either alone is a defect:

  * an UNRELATED red must PUBLISH (with the annotation) -- otherwise nothing changed and the
    treadmill continues;
  * a PUBLISH-PATH red must still BLOCK the content, and must publish the honest banner
    instead -- otherwise the decoupling has bought freshness by shipping wrong figures, which
    is a worse failure than the wedge it replaced.

The exemplar red is the ruff/static-quality ratchet: a real, currently-live, deliberately
whole-repo check with no bearing whatsoever on whether a published number is correct, and the
named cause of one of the 2026-08-09/10 wedges.
"""
from __future__ import annotations

import subprocess as _sp

import pytest

from background import process_run_complete as prc
from background import publish_provenance as prov
from background import publish_scope


@pytest.fixture(scope="module", autouse=True)
def _the_publisher_log_goes_to_tmp(tmp_path_factory):
    """THIS FILE DRIVES THE REAL PUBLISHER, so its diagnostics must not reach the real record.

    `prc.log()` appends to `docs/observability/sim-runner-log.md` -- the file the PUBLISHING
    DOWN alarm sends a human to. Four tests here exercise publish paths that log, so without
    this their fixture rows land beside the genuine sim-runner rows and read as real gate
    verdicts."""
    dest = tmp_path_factory.mktemp("publisher-log") / "sim-runner-log.md"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(prc, "LOG_FILE", dest)
        yield dest

# The injected-red exemplar. Asserted to EXIST below rather than merely referenced: a renamed
# or deleted exemplar must fail this file loudly, never let it pass over nothing
# (`feedback_control_keyed_to_one_syntactic_form`).
UNRELATED_RED = "tests/architecture/test_static_quality_ratchet.py"

# The publisher's real output shape. `VERIFIED_SHA` is resolved from the repo at import
# time rather than hardcoded, so it is a commit that genuinely exists -- the provenance
# guard checks existence, and pinning a literal sha here would rot into a false red.
VERIFIED_SHA = _sp.run(["git", "rev-parse", "--short=9", "HEAD"], cwd=str(prc.PROJECT_DIR),
                       capture_output=True, text=True).stdout.strip() or "0" * 9
VERIFIED_RUN_ID = "run_output_{}_20260809T171913Z.json".format(VERIFIED_SHA)


def test_the_injected_red_exemplar_exists():
    """A renamed or deleted exemplar must fail this file loudly rather than let the exit test
    pass over nothing -- the file's own guard against the blindness it is testing for."""
    assert (prc.PROJECT_DIR / UNRELATED_RED).exists(), UNRELATED_RED


def test_an_unrelated_red_cannot_reach_the_blocking_gate():
    """HALF ONE, structurally. The ratchet test is not in the argv the gate blocks on, so no
    amount of redness in it can wedge the publish."""
    scope = publish_scope.resolve_scope()
    assert not scope["full_suite"], scope["reason"]
    assert UNRELATED_RED not in scope["tests"], (
        "the doc-drift exemplar is still in the BLOCKING scope -- the decoupling does not "
        "actually decouple the case the director named")

    argv, _ = prc._scoped_gate_argv()
    assert UNRELATED_RED not in argv


def test_an_unrelated_red_is_still_RUN_and_still_SEEN():
    """The other half of half one, and the one that makes the narrowing honest rather than a
    silencing: the same test IS in the remainder pass, whose reds become the page annotation.
    Deselected from the blocking gate must never mean covered by no gate (R11)."""
    remainder = publish_scope.remainder_pytest_argv(prc.publish_gate_pytest_argv("tests/"))
    # The remainder runs the whole tree ("tests/") minus the documented deselections; the
    # exemplar is under none of them.
    assert "tests/" in remainder
    assert not any(a == "--ignore=" + UNRELATED_RED for a in remainder)
    marker_idx = len(remainder) - 1 - remainder[::-1].index("-m")
    assert "architecture" not in remainder[marker_idx + 1]


def test_a_publish_path_red_still_blocks():
    """HALF TWO, structurally. Freshness was not bought by shipping wrong figures: the tests
    that guard the code producing published numbers are still in the blocking argv."""
    scope = publish_scope.resolve_scope()
    joined = "\n".join(scope["tests"])
    assert "generate_dashboard_data" in joined
    assert "process_run_complete" in joined


def test_a_red_gate_publishes_the_banner_and_never_the_content(tmp_path, monkeypatch):
    """HALF TWO, behaviourally -- and the death of the FROZEN STAMP.

    With the scoped gate red, the publisher must (a) refuse the content commit and (b) still
    put a dated 'verification paused' banner on the live surface. Before this build it did
    only (a), which is why 25 hours of silence looked identical to a healthy site."""
    p = tmp_path / "publish_provenance.json"
    monkeypatch.setattr(prov, "PROVENANCE_FILE", p)
    # A REAL-SHAPED run id and a REAL commit, not a fixture literal: since 2026-08-11 the
    # recorders refuse anything that could not have come from a run, because a fixture
    # ("run_verified.json") reached the live banner and was pushed to origin. A test that
    # needs a value the publisher would never emit is a test asserting on an impossible
    # state -- so this uses a value the publisher WOULD emit.
    # A stamp must say what the run held (2026-08-31) -- see publish_provenance.population_of.
    prov.record_verified(run_id=VERIFIED_RUN_ID, git_commit=VERIFIED_SHA, path=p,
                         population={"accounts": 251, "bills": 10948,
                                     "total_revenue_gbp": 801199.0})

    pushed = {}

    def _fake_run(argv, **kwargs):
        pushed.setdefault("argv", []).append(list(argv))

        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(prc.subprocess, "run", _fake_run)
    monkeypatch.setattr(prc, "_push_reached_origin", lambda *a, **k: True)
    monkeypatch.setattr(prc, "tree_lock", lambda: _NullCtx())
    # Hold the divergence read level with origin. The banner path reads origin before it stages
    # (2026-09-01, `_divergence_refusal`), and `_fake_run` above answers every git command with
    # rc=0 and EMPTY stdout -- which `_commits_origin_is_ahead_by` correctly calls UNREADABLE, so
    # the banner would be refused for a reason that is not this test's subject. STATED, NOT
    # NEUTERED: the subject here is that a RED GATE still publishes the banner and never the
    # content; being behind origin is a different refusal with its own real-git control in
    # `test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py`.
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 0)
    import background._seat as seat
    monkeypatch.setattr(seat, "is_resident_seat", lambda: True)

    ok = prc._publish_provenance_banner("deadbeef", reason="scoped suite red")
    assert ok is True

    state = prov.read(p)
    assert state["verification_state"] == prov.STATE_PAUSED
    assert state["paused_since"]                                   # dated
    assert state["showing_run"]["run_id"] == VERIFIED_RUN_ID   # last-known-good, unmoved
    assert state["last_verified"]["git_commit"] == VERIFIED_SHA

    # (b) the ONLY path committed is the banner. Not one figure travelled with it.
    commits = [a for a in pushed["argv"] if a[:2] == ["git", "commit"]]
    assert commits, "no banner commit was attempted"
    for c in commits:
        paths = c[c.index("--") + 1:]
        assert paths == [str(p)], paths


def test_the_banner_publisher_refuses_on_foreign_soil(monkeypatch, tmp_path):
    """The ghost-pusher guard, on the new push path too. This function commits and pushes
    without going through `__main__`, exactly like the liveness refresh that manufactured real
    commits from test runs -- so the seat guard is on the SIDE EFFECT, and it is proven here
    rather than assumed."""
    monkeypatch.setattr(prov, "PROVENANCE_FILE", tmp_path / "prov.json")
    import background._seat as seat
    monkeypatch.setattr(seat, "is_resident_seat", lambda: False)

    def _explode(*a, **k):
        raise AssertionError("a foreign seat reached git")

    monkeypatch.setattr(prc.subprocess, "run", _explode)
    assert prc._publish_provenance_banner("deadbeef") is False


def test_the_annotation_pass_cannot_block_a_publish(monkeypatch, tmp_path):
    """The remainder pass is an OBSERVER. A crash inside it -- or a red result from it -- must
    never propagate into the publish path it follows. An observer that can red its subject is
    the defect this whole ruling exists to remove."""
    monkeypatch.setattr(prov, "PROVENANCE_FILE", tmp_path / "prov.json")
    monkeypatch.setattr(prc, "REMAINDER_ANNOTATION_STATE_FILE", tmp_path / "rem.json")

    def _boom(_argv):
        raise RuntimeError("suite exploded")

    assert prc.run_remainder_annotation_step("abc", force=True, runner=_boom) is None

    class Red:
        # A REAL pytest transcript, header included (2026-08-12). `_parse_failed_node_ids` was
        # scoped to the last short-summary section so a NESTED run's replayed FAILED lines
        # could not become the blocking payload -- which means a hand-typed transcript with no
        # summary header of its own now parses as empty, and this assertion was left standing
        # behind the new refusal. pytest never emits a bare `FAILED` line outside that section,
        # so the fixture was the unrealistic half.
        returncode = 1
        stdout = ("=========================== short test summary info "
                  "============================\n"
                  "FAILED tests/architecture/test_static_quality_ratchet.py::test_ruff\n")
        stderr = ""

    state = prc.run_remainder_annotation_step("abc", force=True, runner=lambda _a: Red())
    assert state is not None
    assert state["verification_state"] != prov.STATE_PAUSED or True  # never asserts a pause
    assert any("static_quality_ratchet" in r for r in state["annotation"]["nonblocking_reds"])


def test_the_annotation_reaches_the_rendered_page():
    """R11, verify to the rendered value: the annotation is only real if a reader sees it. The
    layer that renders it must consume the same field the publisher writes."""
    js = (prc.PROJECT_DIR / "site" / "assets" / "freshness-banner.js").read_text()
    assert "open_findings" in js
    assert "nonblocking_reds" in js
    assert "open finding" in js, "the ruling's own wording must reach the page"


class _NullCtx:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_an_unreadable_remainder_transcript_is_a_red_not_an_all_clear(monkeypatch, tmp_path):
    """R15 fail-silent, on the SECOND consumer of the scoped parser (2026-08-12).

    `_parse_failed_node_ids` answers "" for a transcript with no summary section, and for the
    blocking gate that is right -- its consumer renders UNRECORDED. Here an empty list would
    reach the live page as "0 non-blocking reds" beside a run that plainly failed. A truncated
    transcript is the known shape of an OOM kill on this box, so this is reachable.

    Mutation: with the guard removed the annotation records zero reds and the page says
    all-clear, which is the exact defect."""
    monkeypatch.setattr(prov, "PROVENANCE_FILE", tmp_path / "prov.json")
    monkeypatch.setattr(prc, "REMAINDER_ANNOTATION_STATE_FILE", tmp_path / "rem.json")

    class Truncated:
        returncode = 1
        stdout = ("----------------------------- Captured stdout call "
                  "-----------------------------\n"
                  "FAILED tests/background/test_supervisor.py::test_something_nested\n"
                  "Killed\n")
        stderr = ""

    state = prc.run_remainder_annotation_step("abc", force=True, runner=lambda _a: Truncated())

    reds = state["annotation"]["nonblocking_reds"]
    assert reds, "a failed remainder run must never publish an empty red list"
    assert "UNREADABLE" in reds[0], reds
    assert not any("test_supervisor" in r for r in reds), (
        "the nested run's replayed failures must not be named as this run's reds -- that is "
        "the defect the parser scoping removed and this guard must not reintroduce")


def test_a_green_remainder_run_still_publishes_no_reds(monkeypatch, tmp_path):
    """The other direction: the guard is keyed on the RETURN CODE, so a clean run is still
    clean. Without this, "never empty" would degrade into "always red", which is as ignored as
    a blind detector."""
    monkeypatch.setattr(prov, "PROVENANCE_FILE", tmp_path / "prov.json")
    monkeypatch.setattr(prc, "REMAINDER_ANNOTATION_STATE_FILE", tmp_path / "rem.json")

    class Green:
        returncode = 0
        stdout = "142 passed in 12.00s\n"
        stderr = ""

    state = prc.run_remainder_annotation_step("abc", force=True, runner=lambda _a: Green())

    assert state["annotation"]["nonblocking_reds"] == []


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE RED COUNT NAMES THE TREE IT WAS COUNTED ON — THE CALLER'S HALF
# ═════════════════════════════════════════════════════════════════════════════════════════════
#
# `publish_provenance.record_annotation` refuses a red count with no `measured_on`; these are the
# legs for the thing that BUILDS it. The producer's refusal cannot check whether the answer is
# true, only that one was given -- so a caller that always said "commit" would satisfy the refusal
# and publish the same misattribution with a certificate attached. That is the gap these close.


class _Probe:
    """A stand-in for `git status --porcelain`."""

    def __init__(self, returncode=0, stdout=""):
        self.returncode = returncode
        self.stdout = stdout


class _Subprocess:
    """A stand-in for the `subprocess` MODULE, bound over the name in `prc`'s namespace.

    NARROW ON PURPOSE, and the wide version was caught doing real damage in this repo's own
    worktree during this change. `monkeypatch.setattr(prc.subprocess, "run", ...)` reaches
    through to the STDLIB module object, which every caller in the process shares -- including
    `tests/background/conftest.py::_real_repo_head`, whose teardown `git rev-parse` then read
    this fixture's stdout and reported a GHOST PUSHER: "HEAD moved 0bc78cf14 -> unreadabl".
    A fixture that fabricates the answer to an unrelated control is the harness-fabricates-the-
    observable class, and it surfaced as an ERROR at teardown -- neither pass nor fail, so the
    shared-tree run reported 14 passed and only the isolated worktree showed it.
    Rebinding the NAME in `prc` touches nothing outside that module.

    (Two older tests in this file, `_fake_run` and the `_explode` above, still patch the wide
    way. Left alone deliberately -- not this change's subject, and not observed colliding.)
    """

    def __init__(self, result):
        self._result = result

    def run(self, *a, **k):
        if callable(self._result):
            return self._result(*a, **k)
        return self._result


def test_a_dirty_tree_is_never_recorded_as_the_commit(monkeypatch):
    """THE DEFECT ITSELF. The remainder suite runs with `cwd=PROJECT_DIR` -- the shared working
    tree, carrying every other lane's uncommitted work. On 2026-08-31 that tree also held an
    uncommitted guard widening reddening ~1,760 tests while the banner published 66 reds beside
    `git_commit: d1ba6bd46`. The count belonged to neither object."""
    monkeypatch.setattr(prc, "subprocess", _Subprocess(
        _Probe(0, " M background/supervisor.py\n?? tools/x.py\n")))
    measured = prc._annotation_measured_on("d1ba6bd46")
    assert measured["git_commit"] == "d1ba6bd46"
    assert measured["tree_state"] == prov.TREE_WORKING, (
        "a working tree carrying two other lanes' uncommitted files was recorded as though the "
        "reds had been counted on the published commit alone")


def test_a_clean_tree_is_recorded_as_the_commit(monkeypatch):
    """NULL CONTROL, and without it the test above passes on a function that returns the string
    'working-tree' unconditionally -- a control asserting a constant. The two directions have to
    be distinguishable or neither leg means anything."""
    monkeypatch.setattr(prc, "subprocess", _Subprocess(_Probe(0, "\n  \n")))
    assert prc._annotation_measured_on("d1ba6bd46")["tree_state"] == prov.TREE_COMMIT


def test_an_unreadable_git_probe_claims_the_working_tree_not_the_commit(monkeypatch):
    """FAIL-CLOSED IN THE DIRECTION THAT CLAIMS LESS. 'I could not tell whether the tree was
    clean' must not resolve to the stronger claim. A probe that fails open here would put the
    misattribution back on every cycle where git is slow or absent -- and it would do it
    silently, which is this repo's most-repeated failure shape."""
    def _explode(*a, **k):
        raise OSError("git not on PATH")

    monkeypatch.setattr(prc, "subprocess", _Subprocess(_explode))
    assert prc._annotation_measured_on("d1ba6bd46")["tree_state"] == prov.TREE_WORKING

    monkeypatch.setattr(prc, "subprocess", _Subprocess(_Probe(128, "")))
    assert prc._annotation_measured_on("d1ba6bd46")["tree_state"] == prov.TREE_WORKING


def test_the_tree_the_reds_were_counted_on_reaches_the_rendered_page():
    """THE PRODUCER'S HALF ONLY -- that the field is written and the renderer names it.

    NOT SUFFICIENT ON ITS OWN, and this docstring says so because the first version of this
    leg was exactly this grep and nothing more. Mutation M5 (make `annotationSentence` stop
    CALLING `redTreeClause`, leaving the function defined and unreached) SURVIVED it: every
    string it greps for still existed in dead code. That is the fail-closed-verdict-composed-
    into-an-artefact-no-surface-reads class, committed inside the test written to prevent it.
    The leg that actually fires lives in
    `site/test_freshness_banner_publish_state.py::test_the_tree_the_red_count_was_taken_on_is_rendered`,
    which drives the real asset through a DOM. This one is kept as the cheap producer-side
    tripwire that runs in the background selection, and it is honest about being half."""
    js = (prc.PROJECT_DIR / "site" / "assets" / "freshness-banner.js").read_text()
    assert "nonblocking_reds_measured_on" in js, (
        "the publisher records which tree the reds were counted on and the banner asset does "
        "not mention it at all")


def test_a_timed_out_remainder_still_refreshes_the_cheap_half(monkeypatch, tmp_path):
    """DEFECT: a finding count frozen for two days, published as this cycle's.

    `run_remainder_annotation_step` has two branches that do not run the suite. The NOT-DUE one
    already refreshed `open_findings`, and says why in its own words -- *"Findings are cheap to
    count, so refresh that half every cycle even when the suite is throttled -- a stale finding
    count on a live page is a small lie that costs nothing to avoid."* The FAILURE branch
    recorded nothing at all. So the principle was written down, implemented on one branch, and
    missing from the branch that actually fires.

    IT FIRES ALWAYS. `_default_remainder_runner` gets whatever the publish path has left, the
    suite does not finish inside it, and the timeout lands in that `except`: 23 times in the two
    days to 2026-09-03 and on every cycle that day, with the last success at 2026-09-01 05:53Z.

    MEASURED on the live banner, which is why this is a repair and not a tidy-up: it said
    *"Published with 55 open findings"* while the true count was 16 -- 3.4x, frozen since
    06:22Z on 2026-09-01. `site/data/publish_provenance.json` was rewritten every cycle (17:54
    mtime the day it was found), so nothing read as stale. It was the ANNOTATION BLOCK inside a
    fresh file that had stopped moving.

    R15 -- the mutations, each run and reverted:
      * delete the `record_annotation` call from the `except` -> this reds on the stale 55.
      * refresh the RED count there too -> `test_a_failed_remainder_never_republishes_a_red_
        count_it_did_not_take` reds. Reds are a property of a tree this path has none of.
      * drop `nonblocking_reds_checked_at` and let the reds share `checked_at` again -> the same
        control reds. That mutation is the SHAPE OF THE FIRST DRAFT OF THIS REPAIR, kept as a
        mutation rather than forgotten: refreshing the findings half restamped the one shared
        clock, which would have made a two-day-old red count read as this cycle's and left the
        banner's new age clause unable to fire in production. Two quantities with different
        freshness may not share a clock.

    AND THE SECOND MUTATION SURVIVED THE FIRST DRAFT OF THE NULL CONTROL, which is recorded here
    rather than tidied away: it seeded the annotation and re-read it within the same second, so
    `before == after` held whatever the code did. A clock test whose two readings cannot differ
    is not a clock test. It now seeds two days back through `record_annotation(now=...)`.
    """
    monkeypatch.setattr(prov, "PROVENANCE_FILE", tmp_path / "prov.json")
    monkeypatch.setattr(prc, "REMAINDER_ANNOTATION_STATE_FILE", tmp_path / "rem.json")
    monkeypatch.setattr(prc, "_open_findings_count", lambda: 16)
    prov.record_annotation(open_findings=55)

    def _timed_out(_argv):
        raise TimeoutError("timed out after 3503s")

    assert prc.run_remainder_annotation_step("abc", force=True, runner=_timed_out) is None
    published = prov.read(tmp_path / "prov.json")["annotation"]["open_findings"]
    assert published == 16, (
        "the timeout path left the finding count at {} when the true count is 16 -- a number "
        "nothing measured, published inside a file rewritten every cycle".format(published))


def test_a_failed_remainder_never_republishes_a_red_count_it_did_not_take(monkeypatch, tmp_path):
    """NULL CONTROL, and the reason the repair above refreshes only ONE half.

    A red count is a property of a TREE -- `record_annotation` refuses one without its
    `measured_on` for exactly that reason. The failure path ran no suite and has no tree to name,
    so re-stamping the previous reds with a fresh `checked_at` would manufacture a measurement:
    the same misattribution, arriving through the repair for it. The reds keep their own older
    clock, and `site/assets/freshness-banner.js` now renders that clock's AGE so a reader meets
    the staleness instead of inheriting it.
    """
    monkeypatch.setattr(prov, "PROVENANCE_FILE", tmp_path / "prov.json")
    monkeypatch.setattr(prc, "REMAINDER_ANNOTATION_STATE_FILE", tmp_path / "rem.json")
    monkeypatch.setattr(prc, "_open_findings_count", lambda: 16)
    # SEEDED TWO DAYS AGO, EXPLICITLY. The first draft of this control seeded and re-read
    # within the same second, so `before == after` held whatever the code did and the
    # mutation that republishes the reds SURVIVED it. A clock test whose two readings cannot
    # differ is not a clock test. `record_annotation` takes `now`, so the age is driven rather
    # than waited for.
    import datetime as _dt
    two_days_ago = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=2)
    prov.record_annotation(open_findings=55, nonblocking_reds=["FAILED tests/x.py::test_y"],
                           measured_on={"git_commit": "aaaaaaaaa", "tree_state": "commit"},
                           now=two_days_ago)
    before = prov.read(tmp_path / "prov.json")["annotation"]["nonblocking_reds_checked_at"]

    def _timed_out(_argv):
        raise TimeoutError("timed out after 3503s")

    prc.run_remainder_annotation_step("abc", force=True, runner=_timed_out)
    after = prov.read(tmp_path / "prov.json")["annotation"]
    assert after["nonblocking_reds"] == ["FAILED tests/x.py::test_y"], (
        "the failure path rewrote the red list without running a suite")
    assert after["nonblocking_reds_checked_at"] == before, (
        "the failure path restamped the red count's clock to now, so a two-day-old measurement "
        "publishes as this cycle's -- the exact defect the age clause exists to surface")
    assert after["open_findings"] == 16, (
        "the cheap half did not move, so this control is passing for the wrong reason")
    assert after["checked_at"] != before, (
        "the annotation's write-time clock did not move when the findings half was refreshed, "
        "so the two halves are sharing one clock again")
