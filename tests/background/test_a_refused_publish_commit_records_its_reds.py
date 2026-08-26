"""The publish COMMIT's refusal must reach the RECORD, not only the log (2026-08-26).

THE DEFECT THIS CLOSES, observed. `docs/observability/sim-runner-log.md` at 2026-08-26 04:40Z:

    - [2026-08-26 04:40 UTC] [process_run] Nothing to commit or commit failed (rc=1)
      git/hook output (last 40 lines):
      =========================== short test summary info ===========================
      FAILED tests/background/test_derived_artefact_register.py::TestStaleness::test_staleness...
      ... six of them ...
      6 failed, 471 passed, 1 skipped in 636.44s (0:10:36)
      [test-gate] ❌ TESTS FAILED -- COMMIT REFUSED.

while `docs/observability/.publish_gate_state.json`, through FIVE consecutive refusals, read
`blocking_tests: []`, `total_red: 0`, `suspects: {}`. The publisher's own scoped gate had been
GREEN -- so `_clear_blocking_tests` had just retired the previous record -- and the pre-commit
HOOK CHAIN's verdict was captured, tailed into a log, and dropped everywhere a reader looks.

That is R15's FAIL-SILENT shape at the record layer: the diagnostic was taken and thrown away,
so the wedge draw, the alarms and four direction records reasoned about a deadline while the
machine held the answer. The `_COMMIT_DEADLINE` raise from 600s to 840s the day before was
bought with that blindness -- the gate that night finished in 636s and was refused on TESTS.

R15, BOTH DIRECTIONS, because a parser that always finds something is the fail-open twin of the
fail-silent it replaces:
  * FIRES  -- a refusal carrying a real red populates `blocking_tests`, `total_red`, `suspects`
              and the fired alert.
  * STAYS EMPTY -- a clean empty-index no-op, and a NON-TEST gate refusal (scope-evidence,
              level-promotion, the finding-class gate), record NOTHING. Absent reads as absent.

MUTATIONS EACH TEST KILLS:
  * `..._records_the_hook_chains_failing_tests`  -- delete the `_record_commit_refusal_reds`
        call from the refusal branch of `git_commit_push` (i.e. restore 2026-08-26 behaviour).
  * `..._reach_the_state_file_the_alarm_reads`   -- same, one process boundary further out.
  * `..._a_clean_empty_index_records_nothing`    -- move the call out of the `if refused:` guard
        so the commonest branch on this path (a run whose surfaces did not change) records too.
  * `..._a_non_test_refusal_records_no_blocking_test` -- BOTH fail-open shapes land here, and
        both were driven: (a) write the record on every refusal, empty included
        (`_write_blocking_tests([], ...)`), (b) fall back to a whole-stream scan when the
        summary section is absent -- that fixture carries an OLD red's node id echoed by an
        earlier hook, so the fallback records yesterday's test as today's cause.
  * `..._are_read_from_both_streams`             -- implement it by passing the log line's own
        `_tail` through: `stderr_tail(a) or stderr_tail(b)` returns ONE stream, and it is the
        stream that does not carry the answer.
  * `..._the_banner_path_records_its_refusal`    -- fix only the caught instance (R10).
  * `..._the_depth_claim_does_not_invent_a_bound`-- reuse CENSUS_PARTIAL, whose text asserts a
        50-failure census bound that never fired.
"""
from __future__ import annotations

import contextlib
import json

import pytest

from background import process_run_complete as prc
from background import supervisor as sup

# The real 2026-08-26 refusal, trimmed to two of its six node ids. REAL repo paths, because
# `wedge_suspects` resolves the blame trail by reading the test file's imports -- a fabricated
# path would make the suspect assertion below pass on a mechanism that resolves nothing.
RED_A = ("FAILED tests/background/test_derived_artefact_register.py::TestStaleness"
         "::test_staleness_fires_for_EVERY_registered_artefact")
RED_B = ("FAILED tests/tools/test_generate_proof_coupled_gaps.py"
         "::test_empty_ledger_fails_closed_not_silent")

HOOK_REFUSAL_STDOUT = (
    "[test-gate] 477 blocking test(s) selected\n"
    "E       AssertionError: fail-open guard: expected >=1 coupled world atom at >=L2\n"
    "=========================== short test summary info ============================\n"
    + RED_A + "\n" + RED_B + "\n"
    "6 failed, 471 passed, 1 skipped in 636.44s (0:10:36)\n"
    "[test-gate] TESTS FAILED -- COMMIT REFUSED.\n"
    "[test-gate] A red commit is structurally impossible (director P0, 2026-07-17).\n"
)

# A refusal with no test in it at all -- the other half of the observed population (2026-08-25
# 19:13Z and 19:43Z were both this shape). ADVERSARIAL ON PURPOSE: the stream really does carry
# the WORDS of an old red, because an earlier hook echoes the staged log lines the PREVIOUS
# cycle's refusal wrote into it. A whole-stream scan would record yesterday's tests as the cause
# of today's non-test refusal, which is the guess this whole mechanism exists to refuse.
NON_TEST_REFUSAL_STDOUT = (
    "[status-honesty] the staged docs/observability/sim-runner-log.md carries these lines from "
    "the PREVIOUS cycle:\n"
    + RED_A + "\n"
    "[scope-evidence] COMMIT REFUSED -- 1 atom(s) CLAIM A LEVEL on evidence that is not in the "
    "tree this commit would create. A level is a claim about evidence; a path that was deleted, "
    "or never committed, is not evidence.\n"
)

CLEAN_NO_OP_STDOUT = (
    "On branch main\n"
    "nothing to commit, working tree clean\n"
)


class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class _Sink:
    def __init__(self):
        self.messages = []

    def __call__(self, msg, *a, **k):
        self.messages.append(msg)
        return "sent-id"


@pytest.fixture(autouse=True)
def _isolate_records(tmp_path, monkeypatch):
    """Every file this mechanism writes lands in the scratch tree, never the live records."""
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


@pytest.fixture
def publish(tmp_path, monkeypatch):
    """Drive the real `git_commit_push` against a scratch tree whose `git commit` REFUSES.

    Same shape as `test_the_publish_commit_carries_only_its_own_work.py`'s fixture: the publish
    surface exists on disk so the pathspec filter keeps it, and git is a stub. The stub is what
    lets the refusal's OUTPUT be chosen per test, which is the whole subject here.
    """
    repo = tmp_path / "repo"
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)
    monkeypatch.setattr(prc, "STAGING_DIR", repo / "docs" / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", repo / "docs" / "staging" / "done")
    monkeypatch.setattr(prc, "LATEST_MD", repo / "docs" / "status" / "LATEST.md")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", tmp_path / ".last_push_time.json")
    monkeypatch.setattr(prc, "tree_lock", lambda: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_MARKERS_ARCHIVED_BY_THIS_RUN", [])

    for rel in ("docs/reports/ANNUAL_REPORT.md", "docs/status/LATEST.md",
                "site/data/dashboard.json"):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
    (repo / "docs" / "staging" / "done").mkdir(parents=True, exist_ok=True)

    def _run(stdout="", stderr="", rc=1):
        def fake_run(cmd, **kwargs):
            if cmd[:2] == ["git", "commit"]:
                return _FakeCompleted(rc, stdout, stderr)
            if cmd[:2] == ["git", "rev-parse"]:
                # A scratch tree with no history: git has heard of nothing on disk, which is
                # what the pathspec filter asks. `add` and everything else succeeds.
                return _FakeCompleted(1)
            return _FakeCompleted(0)

        monkeypatch.setattr(prc.subprocess, "run", fake_run)
        outcome = {}
        prc.git_commit_push("abc1234", 1000.0, outcome)
        return outcome

    return _run


# ── FIRES ───────────────────────────────────────────────────────────────────────────────────

def test_a_refused_publish_commit_records_the_hook_chains_failing_tests(publish):
    outcome = publish(stdout=HOOK_REFUSAL_STDOUT)
    assert outcome["reason"] == prc.COMMIT_REFUSED

    node_ids, git_hash = prc.last_blocking_tests()
    assert node_ids == [RED_A, RED_B], node_ids
    assert git_hash == "abc1234", "the record must name the commit the refusal was measured at"

    census, total_red = prc.last_red_census()
    assert census == prc.CENSUS_HOOK_CHAIN
    assert total_red == 2


def test_the_recorded_reds_reach_the_state_file_the_alarm_and_the_draw_read(publish):
    """The RUNG-1 unwedge draw's ONLY input is the state file -- so the evidence must survive
    the process boundary into it, exactly as it does for the publisher's own scoped gate."""
    publish(stdout=HOOK_REFUSAL_STDOUT)
    prc.record_publish_gate_failure("the publish COMMIT did not land", rc=77,
                                    git_hash="abc1234", now=100,
                                    kind="commit_did_not_land", send_ntfy_fn=_Sink())

    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert state["blocking_tests"] == [RED_A, RED_B]
    assert state["total_red"] == 2
    assert state["red_census"] == prc.CENSUS_HOOK_CHAIN
    # Suspects are DERIVED from the red (never a recency fallback), so a populated red set must
    # produce a populated trail -- that is the difference between a citation and a guess.
    assert state["suspects"]["test_files"] == [
        "tests/background/test_derived_artefact_register.py",
        "tests/tools/test_generate_proof_coupled_gaps.py",
    ]


def test_the_fired_alert_names_the_test_that_refused_the_commit(publish):
    publish(stdout=HOOK_REFUSAL_STDOUT)
    sink = _Sink()
    for t in (0, 10, 20):
        prc.record_publish_gate_failure("the publish COMMIT did not land", rc=77,
                                        git_hash="abc1234", now=t,
                                        kind="commit_did_not_land", send_ntfy_fn=sink)

    assert len(sink.messages) == 1, sink.messages
    assert "test_staleness_fires_for_EVERY_registered_artefact" in sink.messages[0]


def test_the_node_ids_are_read_from_both_streams_not_from_the_log_tail(publish):
    """THE DIFFERENTIAL against the cheap implementation.

    The log line's own payload is `stderr_tail(stderr) or stderr_tail(stdout)` -- ONE stream.
    The hook chain's pytest writes its summary to STDOUT while git writes its own errors to
    STDERR, so on a commit that produces both, the tail carries the stream WITHOUT the answer.
    Passing that tail through would have looked like a fix and recorded nothing.
    """
    git_noise = "hint: the pre-commit hook exited with code 1\n"
    tail = prc.stderr_tail(git_noise) or prc.stderr_tail(HOOK_REFUSAL_STDOUT)
    assert RED_A not in tail, "premise broken: the tail already carries the node ids"

    publish(stdout=HOOK_REFUSAL_STDOUT, stderr=git_noise)

    node_ids, _ = prc.last_blocking_tests()
    assert node_ids == [RED_A, RED_B], node_ids


def test_the_banner_path_records_its_refusal_too(tmp_path, monkeypatch):
    """R10, the class not the instance: the banner/heartbeat chokepoint meets the SAME hook
    chain refusing the SAME tree, and discarded the node ids in exactly the same way."""
    repo = tmp_path / "repo"
    target = repo / "site" / "data" / "publish_provenance.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}")
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)
    monkeypatch.setattr(prc, "tree_lock", lambda: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_git_add_or_refuse", lambda *a, **k: True)
    monkeypatch.setattr(prc.subprocess, "run",
                        lambda cmd, **kw: _FakeCompleted(1, HOOK_REFUSAL_STDOUT, ""))

    assert prc._commit_and_push_paths([str(target)], "msg", label="Provenance banner",
                                      git_hash="deadbee") is False
    node_ids, git_hash = prc.last_blocking_tests()
    assert node_ids == [RED_A, RED_B]
    assert git_hash == "deadbee"


# ── STAYS EMPTY ─────────────────────────────────────────────────────────────────────────────

def test_a_clean_empty_index_no_op_records_nothing(publish):
    """The fail-OPEN twin. A recorder that runs on every non-zero rc would reach the commonest
    branch on this path -- a run whose surfaces did not change -- and say "Publish commit
    REFUSED" about a commit nothing refused."""
    said = []
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(prc, "log", lambda m: said.append(str(m)))
        outcome = publish(stdout=CLEAN_NO_OP_STDOUT)
    assert outcome["reason"] == prc.NOTHING_TO_COMMIT
    assert not any("REFUSED" in m for m in said), \
        "a clean no-op was narrated as a refusal:\n" + "\n".join(said)

    assert not prc.GATE_BLOCKING_TESTS_FILE.exists()
    node_ids, git_hash = prc.last_blocking_tests()
    assert node_ids == [] and git_hash is None

    prc.record_publish_gate_failure("x", rc=1, git_hash="abc1234", now=100, send_ntfy_fn=_Sink())
    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert state["blocking_tests"] == []
    assert state["total_red"] == 0
    assert state["suspects"] == {}


def test_a_non_test_refusal_records_no_blocking_test(publish):
    """A gate that refuses without running a test names NO test, and the record must say so
    rather than reach for the nearest plausible one -- the exact defect `wedge_suspects` and
    GATE_BLOCKING_TESTS_FILE were built to end."""
    said = []
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(prc, "log", lambda m: said.append(str(m)))
        outcome = publish(stdout=NON_TEST_REFUSAL_STDOUT)

    assert outcome["reason"] == prc.COMMIT_REFUSED
    assert not prc.GATE_BLOCKING_TESTS_FILE.exists()
    assert prc.last_blocking_tests() == ([], None)
    joined = "\n".join(said)
    assert "no FAILED/ERROR summary" in joined, \
        "the absence was SILENT -- a reader cannot tell it from a recorder that never ran"


def test_a_replayed_summary_from_an_inner_run_is_not_the_refusals_red(publish):
    """The parser is scoped to the LAST summary section. A hook chain that replays a nested
    pytest transcript (this repo's own tests print them) must not have the inner run's node ids
    recorded as the cause of the refusal."""
    replayed = (
        "=========================== short test summary info ============================\n"
        "FAILED tests/fixtures/inner_replayed_transcript.py::test_not_the_cause\n"
        + HOOK_REFUSAL_STDOUT
    )
    publish(stdout=replayed)
    node_ids, _ = prc.last_blocking_tests()
    assert node_ids == [RED_A, RED_B], node_ids


# ── THE DEPTH CLAIM ─────────────────────────────────────────────────────────────────────────

def test_the_depth_claim_does_not_invent_a_census_bound_that_never_fired():
    """`CENSUS_PARTIAL`'s text asserts the report-only census hit its own 50-failure bound. The
    hook chain has no such bound: it stops at the first REFUSING HOOK. Reusing the status would
    have made the alarm state a mechanism that did not run -- so this is a fourth status, and
    both payload builders must render it without borrowing that claim."""
    alarm = prc._census_clause(prc.CENSUS_HOOK_CHAIN, 6, 6)
    draw = sup._wedge_depth_clause(prc.CENSUS_HOOK_CHAIN, 6, 6)

    for text in (alarm, draw):
        assert "6" in text
        assert "hook" in text.lower()
        assert str(prc.GATE_RED_CENSUS_MAXFAIL) not in text
        assert "DEPTH UNKNOWN" not in text


def test_an_unknown_census_word_still_degrades_to_fail_fast_only(tmp_path):
    """The status vocabulary stays closed: a record written by something that does not share
    this module's constants cannot make a depth claim by naming it."""
    rec = tmp_path / "rec.json"
    rec.write_text(json.dumps({"ts": 0.0, "census": "invented", "total_red": 9,
                               "node_ids": [RED_A], "git_hash": "abc"}))
    assert prc.last_red_census(now=0.0, path=rec) == (prc.CENSUS_FAIL_FAST_ONLY, 0)
