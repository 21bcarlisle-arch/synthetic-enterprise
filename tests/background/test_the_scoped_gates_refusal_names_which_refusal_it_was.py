"""R15: the publisher's OWN scoped gate must say WHICH refusal it was, and carry the observation.

THE DEFECT, observed with evidence (R9), not inferred. `docs/observability/sim-runner-log.md` and
`.publish_gate_state.json` on 2026-09-24, one cycle, four minutes apart:

    06:51:17Z  .last_gate_blocking_tests.json  {"node_ids": ["FAILED tests/background/test_the_
               liveness_surfaces_refusals_left_only_an_orphaned_log_line.py::test_a_wedged_tree_
               and_a_hot_origin_are_told_apart_in_the_record"], "total_red": 1,
               "graded_sha": "35f9e346229b00b19aba32eee816c960f11dd6a5"}
    06:55:10Z  .publish_gate_state.json        {"cause": "unattributed", "cause_evidence":
               "recorded with no observation attached (rc=1, kind=test_regression) -- this exit
               path names no cause, so which one it was is NOT established here"}

The publisher held the answer, wrote it down, and then left by a door that could not carry it.
`_run_gate_in` collapses the suite's return code to `result.returncode == 0` -- a BOOLEAN -- and
`_gate_refusal` returned a bare `1` for every non-zero, so `record_publish_gate_outcome` had only
the generic fall-through, which passes NO cause and lets `_classify_gate_failure` call the whole
thing `test_regression`. That is the sixth cause of the publish-outage series and the fifth time
this module has paid for the same shape (rc=77, rc=78, rc=79, the two outer deadline kills).

WHAT IS UNDER TEST. The refusal is a PARTITION over four observable shapes, and the control is
written over the whole partition rather than one leg per branch -- a guard that refuses
EVERYTHING passes a per-leg suite.

  shape                                    ->  (exit code, kind, cause)
  the inner clock expired                  ->  (78, gate_timeout,          -- unjudged)
  rc>0 and a node id was named             ->  (81, test_regression,       scoped_suite_red)
  rc>0 and nothing was named, or rc<0      ->  (81, scoped_gate_unjudged,  scoped_gate_unjudged)
  no subject: the checkout never happened  ->  (81, scoped_gate_unjudged,  scoped_gate_unjudged)

FOUR SHAPES, THREE STATES, AND THE COLLAPSE IS DELIBERATE -- so it is asserted rather than left
to the reader. `test_the_two_unjudged_shapes_share_a_state_and_not_an_evidence_line` holds both
halves of that: the state is the same because the READER's answer is the same (nothing was
judged, implicate nobody), and the EVIDENCE must still differ because the two send a diagnostician
to different places. A partition control asserting only "N states over N+1 shapes" cannot see a
collapse it did not intend; this one names the collapse it does.
"""
import json

import pytest

import background.process_run_complete as prc
import background.publish_cause as pc
import background.supervisor as sup

MARKER_HASH = "6fd5aa1dc"
OTHER_HASH = "e664b5720"
MARKER_NAME = "run_complete_20260924T064310Z.md"
RED_NODE = ("FAILED tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_"
            "log_line.py::test_a_wedged_tree_and_a_hot_origin_are_told_apart_in_the_record")
GRADED = "35f9e346229b00b19aba32eee816c960f11dd6a5"


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Every record this control touches, redirected -- a test that writes the LIVE wedge state
    would poison the detector it is checking."""
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / ".last_publish_cause.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


@pytest.fixture
def archived_marker(tmp_path, monkeypatch):
    """The marker in `done/` this cycle produced. Its location proves nothing about the publish
    -- it is archived whether the gate refused or not."""
    done = tmp_path / "staging" / "done"
    done.mkdir(parents=True)
    marker = done / MARKER_NAME
    marker.write_text("# Run complete\n\nGit: {}\n".format(MARKER_HASH))
    monkeypatch.setattr(prc, "DONE_DIR", done)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    return marker


def _route(marker):
    """Drive the router the way the sweeping process does, and return the record it wrote."""
    verdict = prc.record_publish_gate_outcome(str(marker), prc.EXIT_SCOPED_GATE_REFUSED)
    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    return verdict, state["failures"][-1]


# ── The partition ────────────────────────────────────────────────────────────────────────────

def test_the_four_refusal_shapes_do_not_leave_by_one_door(archived_marker):
    """THE WHOLE PARTITION IN ONE CONTROL, over the states a reader actually switches on.

    MUTATION: restore `_gate_refusal`'s pre-fix `return (1, ...)` for the non-timeout branch and
    the three non-timeout rows collapse onto rc=1 -> the generic fall-through -> one state. That
    is the defect verbatim, and it reds here on the distinctness assertion below rather than on
    any single row's expected value.
    """
    states = {}
    # the inner clock -- already carved out in 2026-08-21, included so a repair that re-merges it
    # cannot pass by only checking the two new rows.
    states["timeout"] = (prc._gate_refusal(True, MARKER_HASH, [])[0], "gate_timeout")

    for label, rc, nodes in (("judged_red", 1, [RED_NODE]),
                             ("killed_child", -15, []),
                             ("no_subject", None, [])):
        prc.PUBLISH_CAUSE_FILE.unlink(missing_ok=True)
        prc._record_scoped_gate_cause(rc, nodes, MARKER_HASH, GRADED)
        code = prc._gate_refusal(False, MARKER_HASH, nodes,
                                 cause=prc._scoped_gate_cause(MARKER_HASH)[0])[0]
        _, entry = _route(archived_marker)
        states[label] = (code, entry["kind"])

    assert states["timeout"][0] == prc.EXIT_GATE_TIMED_OUT
    assert states["judged_red"] == (prc.EXIT_SCOPED_GATE_REFUSED, "test_regression")
    assert states["killed_child"] == (prc.EXIT_SCOPED_GATE_REFUSED, prc.SCOPED_GATE_UNJUDGED_KIND)
    assert len(set(states.values())) == 3, (
        "four observable refusal shapes produced {} distinguishable states {!r} -- a reader can "
        "only act on what the record distinguishes, and 'a test is red' and 'the suite was "
        "killed' are different repairs".format(len(set(states.values())), states))


def test_the_two_unjudged_shapes_share_a_state_and_not_an_evidence_line(archived_marker):
    """THE COLLAPSE, NAMED. A killed child and an unbuildable checkout give the reader the same
    instruction -- implicate nobody -- so they share (code, kind, cause) deliberately. What they
    must NOT share is the evidence: one sends a diagnostician to the signal and the memory
    headroom, the other to `_head_checkout`. A collapse that also flattened the evidence would
    be indistinguishable from the defect this file is about.

    MUTATION: return a single constant evidence string from `_record_scoped_gate_cause`'s else
    branch and this reds on the inequality, while every row of the partition control above still
    passes.
    """
    seen = {}
    for label, rc in (("killed_child", -15), ("no_subject", None)):
        prc.PUBLISH_CAUSE_FILE.unlink(missing_ok=True)
        prc._record_scoped_gate_cause(rc, [], MARKER_HASH, GRADED)
        _, entry = _route(archived_marker)
        seen[label] = entry

    assert seen["killed_child"]["cause"] == seen["no_subject"]["cause"] == pc.SCOPED_GATE_UNJUDGED
    assert seen["killed_child"]["cause_evidence"] != seen["no_subject"]["cause_evidence"]
    assert "signal 15" in seen["killed_child"]["cause_evidence"]
    assert "never ran" in seen["no_subject"]["cause_evidence"]


# ── The observation survives the process boundary ────────────────────────────────────────────

def test_a_judged_red_reaches_the_record_with_the_node_and_the_sha_it_was_graded_at(
        archived_marker):
    """THE 2026-09-24 RECORD, INVERTED. The publisher observed one red at a named sha; the record
    said "recorded with no observation attached". Both facts must now be IN the record, because
    the record is the thing that gets quoted -- the log is not readable by the alarm.

    MUTATION: delete the `_record_scoped_gate_cause` call from `_run_gate_in` and this reds on
    `cause == unattributed`, which is the live behaviour of 2026-09-24 06:55:10Z exactly.
    """
    prc._record_scoped_gate_cause(1, [RED_NODE], MARKER_HASH, GRADED)
    verdict, entry = _route(archived_marker)

    assert verdict == "failure"
    assert entry["cause"] == pc.SCOPED_SUITE_RED
    assert entry["cause"] != pc.UNATTRIBUTED
    assert "recorded with no observation attached" not in entry["cause_evidence"]
    assert RED_NODE.split("::")[-1] in entry["cause_evidence"], "the red must be nameable"
    assert GRADED[:9] in entry["cause_evidence"], (
        "the sha the suite was GRADED at is the only thing that makes the red reproducible -- "
        "the marker's own hash is a different commit and a 12-minute suite outlives it")


def test_the_production_gate_run_is_what_writes_the_record(monkeypatch, tmp_path):
    """THE CHAIN, not the rule. Every assertion above drives `_record_scoped_gate_cause`
    directly, and every one of them stays green while NO production caller reaches it -- this
    repo's catalogued fail-open shape. This leg drives the REAL `run_fast_tests` over a faked
    pytest result, so the wiring inside `_run_gate_in` is the thing under test.

    MUTATION: delete the `_record_scoped_gate_cause(...)` call from `_run_gate_in` and this reds
    on an absent record, while all seven other legs still pass.
    """
    import contextlib

    from tests.background.publish_gate_root_shape import materialise_repo_shaped_root

    class _Result:
        returncode = -15
        stdout = "collected 1805 items\n"
        stderr = ""

    # NEVER HAND-TYPED. A stand-in root built here would be exactly the shape `resolve_scope`
    # refuses, so the gate would return `_checkout_unavailable_verdict()` before argv is built
    # and this leg would pass while testing the wrong branch -- the 2026-08-12 defect that
    # wedged publishing twice from two different test files.
    checkout = materialise_repo_shaped_root(tmp_path / "head")

    @contextlib.contextmanager
    def fake_checkout():
        yield checkout

    monkeypatch.setattr(prc, "_head_checkout", fake_checkout)
    monkeypatch.setattr(prc.subprocess, "run", lambda argv, **kw: _Result())
    assert prc.run_fast_tests(MARKER_HASH) == (False, False)

    cause, evidence = prc._scoped_gate_cause(MARKER_HASH)
    assert cause == pc.SCOPED_GATE_UNJUDGED, (
        "the gate ran, was killed, and left no record of it -- so the router is back to "
        "inferring `test_regression` from an exit code"
    )
    assert "rc=-15" in evidence


def test_an_unjudged_gate_is_not_recorded_as_a_test_regression(archived_marker):
    """THE ACCUSATION WITH NO ACCUSED, which this module has now paid for five times. A killed
    suite filed as `test_regression` sends the RUNG-1 draw to diagnose a red that does not exist.

    MUTATION: take the kind from `_classify_gate_failure(rc)` instead of from the cause -- rc=81
    is positive, so the classifier answers `test_regression` and this reds.
    """
    prc._record_scoped_gate_cause(-15, [], MARKER_HASH, GRADED)
    _, entry = _route(archived_marker)

    assert entry["kind"] == prc.SCOPED_GATE_UNJUDGED_KIND != "test_regression"
    assert prc._classify_gate_failure(prc.EXIT_SCOPED_GATE_REFUSED) == "test_regression", (
        "the inference this branch exists to override has itself changed -- re-derive the "
        "override rather than deleting it"
    )


def test_a_carried_forward_blocking_list_does_not_survive_an_unjudged_gate(archived_marker):
    """The suppression must fire on the CAUSE, not on a list the previous cycle left behind.
    A gate that judged nothing has no blockers, and naming yesterday's is naming the innocent.

    MUTATION: drop `SCOPED_GATE_UNJUDGED` from `publish_cause.NO_TEST_JUDGED_CAUSES` and the
    record names a green test as the blocker of a wedge it had nothing to do with.
    """
    prc._write_blocking_tests([RED_NODE], OTHER_HASH)
    prc._record_scoped_gate_cause(-15, [], MARKER_HASH, GRADED)
    _, _ = _route(archived_marker)
    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())

    assert state["blocking_tests"] == [], (
        "a gate on which NO test returned a verdict named {} as blocking".format(
            state["blocking_tests"])
    )


# ── The filter: same commit, wrong subject ───────────────────────────────────────────────────

def test_a_commit_route_record_at_this_hash_cannot_name_the_gates_refusal(archived_marker):
    """`PUBLISH_CAUSE_FILE` is shared with the rc=77 route and keyed by git hash -- so a
    `commit_refused` record written by an EARLIER cycle at an unmoved HEAD is in-window and
    hash-matched here, and reading it would attribute a gate refusal to a commit that this cycle
    never attempted. Same commit, wrong subject.

    MUTATION: drop the `cause not in SCOPED_GATE_CAUSES` filter in `_scoped_gate_cause` and the
    record reads `gate_refusal` -- a sentence pointing at hook output that was never produced.
    """
    pc.record_cause(prc.PUBLISH_CAUSE_FILE, pc.GATE_REFUSAL,
                    "`git commit` returned rc=1 and the hook chain named 2 red test(s)",
                    MARKER_HASH)
    _, entry = _route(archived_marker)

    assert entry["cause"] == pc.UNATTRIBUTED
    assert "is about a publish COMMIT and not about this gate" in entry["cause_evidence"], (
        "the refusal to attribute must NAME its reason -- an `unattributed` with an empty "
        "evidence line is the shape this whole repair is about"
    )


def test_an_absent_record_says_so_rather_than_guessing(archived_marker):
    """THE NULL CONTROL. With nothing on record the answer is `unattributed` WITH a sentence,
    never a plausible name. A fix that answered `scoped_suite_red` by default would pass every
    row above and be the same defect with better grammar."""
    prc.PUBLISH_CAUSE_FILE.unlink(missing_ok=True)
    _, entry = _route(archived_marker)

    assert entry["cause"] == pc.UNATTRIBUTED
    assert entry["cause_evidence"].strip(), "a refusal with no reason is the defect"
    assert MARKER_HASH in entry["cause_evidence"]


# ── The label has a reader ────────────────────────────────────────────────────────────────────

def test_the_unjudged_kind_is_read_by_the_draw_that_acts_on_it():
    """A LABEL WITH NO READER is this repo's other recurring shape, catalogued in the
    supervisor's own comment above `WEDGE_KINDS_NO_TEST_JUDGED`: three sites wrote a kind for a
    year and the draw that the intent was ABOUT read the `reason` string instead.

    MUTATION: add the kind in `process_run_complete` and not in the supervisor's set, and this
    reds -- which is the state every one of those three sites was in when it was written.
    """
    assert prc.SCOPED_GATE_UNJUDGED_KIND in prc.UNJUDGED_GATE_KINDS
    assert prc.SCOPED_GATE_UNJUDGED_KIND in sup.WEDGE_KINDS_NO_TEST_JUDGED
    assert pc.SCOPED_SUITE_RED not in sup.WEDGE_KINDS_NO_TEST_JUDGED, (
        "a judged red IS a test to go and run -- suppressing it would be the opposite error"
    )
    assert prc._gate_failure_label(prc.SCOPED_GATE_UNJUDGED_KIND) != prc.SCOPED_GATE_UNJUDGED_KIND, (
        "the kind has no prose label, so the alarm prints the enum name at the reader"
    )
