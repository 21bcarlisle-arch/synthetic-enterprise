"""THE DEFECT: a publish whose commit LANDED and whose push lost a race was graded a FAILURE by
the cycle that could not yet know, 58 times over 7.2 days, for commits origin received minutes
later.

`.publish_gate_state.json` on 2026-09-17: `episode_failures: 58`, `last_clean_publish: null`,
`wedge_since` 7.2 days, `total_red: 0`, `blocking_tests: []`. Failure #58's own evidence line
named `origin_reconcile` as the mechanism that would deliver its commit, recorded
`push_never_landed` against `84c8bdee7`, and `84c8bdee7` is on origin. The race is measured: 556s
of gated merge against a ~600s sibling push interval
(docs/staging/WORKER_RESULT_THE_FIFTY_EIGHT_FAILURE_PUBLISH_EPISODE_HAS_NO_RED_TEST_AND_THE_WEDGE_
IS_A_MERGE_TO_PUSH_RACE_2026-09-17.md).

WHAT THESE CONTROLS PROTECT, and each names the mutation that reds it:

  1. THE PARTITION IS REACHABLE. A deferral mechanism whose OVERDUE branch cannot be taken is a
     mechanism that buys silence, and one whose REACHED branch cannot be taken never records the
     publish. Asserted over the WHOLE partition in one control, per CLAUDE.md -- a guard that
     refuses everything passes every per-branch test.
  2. FAIL-CLOSED IS TOWARD THE ALARM. Unreadable, unstamped, sha-less: all OVERDUE. A deferral
     that cannot expire is a wedge that cannot be reported.
  3. A REMOTE WE COULD NOT READ IS NEVER `REACHED`. "Could not look" is not "arrived".
  4. THE GRADER RECORDS ONLY WHAT THE REF SAYS, and records the failure with a cause that was
     re-measured rather than the one the cycle guessed.
  5. A GREEN CYCLE MAY NOT CLEAR A WEDGE ITS PREDECESSOR'S FIGURES ARE STILL STUCK IN. This is
     the fail-open the repair itself would otherwise have opened.
  6. THE VERDICT IS CLEARED WHEN IT IS TAKEN, so one publish cannot be counted as two failures.
  7. THE KIND REACHES ITS READER. The supervisor's no-test-judged set decides whether a RUNG-1
     draw goes hunting a red test; a kind missing from it sends priority-zero work after a test
     that was green.
  8. THE BENIGN WINDOW IS THE DEADMAN'S, not a second one minted beside it.
"""
from __future__ import annotations

import ast
import json
import types
from pathlib import Path

from background import deadmans_switch as dms
from background import process_run_complete as prc
from background import publish_cause as pc
from background import publish_delivery_deferral as pdd

WINDOW = 2700.0


def _write(path, *, sha="abc123def", ts=1000.0, git_hash="deadbeef"):
    path.write_text(json.dumps({"ts": ts, "sha": sha, "git_hash": git_hash, "evidence": "x"}))


def test_every_verdict_in_the_partition_can_actually_be_taken(tmp_path):
    """ONE CONTROL OVER THE WHOLE PARTITION (CLAUDE.md: assert the rare branch CAN be taken
    before asserting what it does). A `verdict` that answered ABSORBING for everything would pass
    four separate per-branch tests and hold every wedge open forever.

    MUTATION: make any branch unreachable -- return ABSORBING unconditionally, or drop the
    `reached is True` leg -- and this reds naming the verdict that vanished.
    """
    p = tmp_path / "deferral.json"
    seen = {}
    seen["none"] = pdd.verdict(p, reached=False, now=2000.0, benign_seconds=WINDOW)[0]
    _write(p)
    seen["reached"] = pdd.verdict(p, reached=True, now=2000.0, benign_seconds=WINDOW)[0]
    seen["absorbing"] = pdd.verdict(p, reached=False, now=1100.0, benign_seconds=WINDOW)[0]
    seen["overdue"] = pdd.verdict(p, reached=False, now=1000.0 + WINDOW + 1,
                                  benign_seconds=WINDOW)[0]
    assert seen == {"none": pdd.NONE, "reached": pdd.REACHED,
                    "absorbing": pdd.ABSORBING, "overdue": pdd.OVERDUE}, seen
    # And every one of them hands the reader a sentence, on the refusal as much as the verdict.
    for reached, now in ((False, 2000.0), (True, 2000.0), (False, 1100.0)):
        _, evidence = pdd.verdict(p, reached=reached, now=now, benign_seconds=WINDOW)
        assert evidence.strip() and len(evidence) > 30, evidence


def test_a_deferral_that_cannot_be_read_or_aged_expires_rather_than_holding_forever(tmp_path):
    """FAIL-CLOSED TOWARD THE ALARM. MUTATION: return ABSORBING (or NONE) on an unreadable or
    unstamped record and a corrupt file buys unbounded silence on a live publish wedge -- the
    fail-open this whole module exists to avoid.

    `NaN` is the one that matters: `now - NaN > window` is False, so an unscreened timestamp
    would read as benign for ever. `recorded_instant_seconds` is what refuses it.
    """
    p = tmp_path / "deferral.json"
    p.write_text("{not json")
    assert pdd.verdict(p, reached=False, now=9e9, benign_seconds=WINDOW)[0] == pdd.OVERDUE
    p.write_text(json.dumps([1, 2, 3]))
    assert pdd.verdict(p, reached=False, now=9e9, benign_seconds=WINDOW)[0] == pdd.OVERDUE
    p.write_text(json.dumps({"sha": "", "ts": 1000.0}))
    assert pdd.verdict(p, reached=False, now=9e9, benign_seconds=WINDOW)[0] == pdd.OVERDUE
    # `NaN` is written as raw text because `json.dumps` emits the non-standard `NaN` literal and
    # `json.loads` accepts it -- which is exactly how one reaches the reader in the first place.
    for raw in ('{"sha": "abc123def", "ts": 0}',
                '{"sha": "abc123def", "ts": false}',
                '{"sha": "abc123def", "ts": NaN}',
                '{"sha": "abc123def", "ts": null}',
                '{"sha": "abc123def", "ts": "yesterday"}'):
        p.write_text(raw)
        assert pdd.verdict(p, reached=False, now=1001.0, benign_seconds=WINDOW)[0] == pdd.OVERDUE, (
            "an unstamped deferral read as benign: {}".format(raw))
    # And a window nobody can read is not a licence to wait either.
    _write(p)
    assert pdd.verdict(p, reached=False, now=1001.0, benign_seconds="soon")[0] == pdd.OVERDUE
    # A record with no sha is refused at the WRITE too, so it can never be created here.
    assert pdd.record(tmp_path / "x.json", "", "h", "e") is False


def test_a_remote_we_could_not_read_is_never_graded_reached(tmp_path):
    """"COULD NOT LOOK" IS NOT "ARRIVED". MUTATION: treat `reached=None` as True (or as
    "probably fine") and an offline remote publishes a clean-publish stamp for content nobody
    has seen -- the 2026-07-24 phantom-push lesson, arriving through the grader."""
    p = tmp_path / "deferral.json"
    _write(p)
    fresh, why = pdd.verdict(p, reached=None, now=1100.0, benign_seconds=WINDOW)
    assert fresh == pdd.ABSORBING and "could not be read" in why, why
    late, why_late = pdd.verdict(p, reached=None, now=1000.0 + WINDOW + 1, benign_seconds=WINDOW)
    assert late == pdd.OVERDUE and "could not be read" in why_late, why_late


def _grade(tmp_path, monkeypatch, *, reached, now, rec=True):
    p = tmp_path / "deferral.json"
    if rec:
        _write(p)
    monkeypatch.setattr(prc, "PUBLISH_DELIVERY_DEFERRAL_FILE", p)
    calls = {"success": 0, "failure": []}
    status = prc.grade_outstanding_delivery(
        now=now,
        fetch_fn=lambda: None,
        remote_head_fn=lambda: ("" if reached is None else "TIP"),
        ancestor_fn=lambda a, b, **k: bool(reached),
        benign_fn=lambda: WINDOW,
        success_fn=lambda: calls.__setitem__("success", calls["success"] + 1),
        failure_fn=lambda *a, **k: calls["failure"].append((a, k)),
    )
    return status, calls, p


def test_the_grader_records_a_publish_only_when_the_ref_says_so(tmp_path, monkeypatch):
    """THE RE-MEASUREMENT IS THE REPAIR. MUTATION: grade from the deferral record's own evidence
    instead of asking the remote, and the grader becomes a tautology -- it would confirm whatever
    the cycle that could not know had already written."""
    # ARRIVED: one success, no failure, and the record is retired.
    status, calls, p = _grade(tmp_path, monkeypatch, reached=True, now=1100.0)
    assert status == pdd.REACHED and calls["success"] == 1 and calls["failure"] == []
    assert not p.exists(), "a verdict was taken and the record was left behind"

    # STILL ABSORBING: nothing is recorded in either direction.
    status, calls, _ = _grade(tmp_path, monkeypatch, reached=False, now=1100.0)
    assert status == pdd.ABSORBING and calls["success"] == 0 and calls["failure"] == []

    # EXPIRED: a real failure, with the re-measured cause and the kind that does not accuse a
    # hook chain that passed.
    status, calls, p = _grade(tmp_path, monkeypatch, reached=False, now=1000.0 + WINDOW + 1)
    assert status == pdd.OVERDUE and calls["success"] == 0 and len(calls["failure"]) == 1
    _, kwargs = calls["failure"][0]
    assert kwargs["cause"] == pc.LOST_PUSH_RACE, kwargs
    assert kwargs["kind"] == prc.DELIVERY_NOT_REACHED_KIND, kwargs
    assert kwargs["rc"] == prc.EXIT_PUBLISH_DELIVERY_DEFERRED, kwargs
    assert kwargs["git_hash"] == "deadbeef", kwargs
    assert "non-fast-forward" in kwargs["cause_evidence"], kwargs["cause_evidence"]
    assert not p.exists(), "the overdue verdict was taken and the record was left behind"

    # NOTHING OUTSTANDING: the grader is a no-op and writes nothing.
    status, calls, _ = _grade(tmp_path, monkeypatch, reached=True, now=1100.0, rec=False)
    assert status == pdd.NONE and calls["success"] == 0 and calls["failure"] == []


def test_the_deferred_outcome_is_neither_a_success_nor_a_retryable_no_op():
    """THE THREE PROPERTIES THAT KEEP THIS FROM BEING A WHITEWASH, stated over the module's own
    vocabulary rather than over today's numbers.

    MUTATION: put `COMMITTED_DELIVERY_DEFERRED` in `RETRYABLE_PUBLISH_OUTCOMES` and it buys rc=0,
    which `record_publish_gate_outcome` routes into `record_publish_gate_success` -- the exact
    2026-08-19 disarm-by-rc-0 defect. Map it to `EXIT_PUBLISH_DID_NOT_LAND` and the 58-failure
    record returns.
    """
    assert prc.COMMITTED_DELIVERY_DEFERRED not in prc.RETRYABLE_PUBLISH_OUTCOMES
    code = prc.publish_exit_code(prc.COMMITTED_DELIVERY_DEFERRED)
    assert code == prc.EXIT_PUBLISH_DELIVERY_DEFERRED
    assert code not in (0, prc.EXIT_PUBLISH_DID_NOT_LAND)
    assert code not in prc.NO_PUBLISH_EXIT_CODES, (
        "'evidence of nothing about the gate's health' is the wrong reading: the gate passed and "
        "the commit landed")
    # The deferring branch may not stamp a push clock or a content-publish clock: those are the
    # two writes that would make an undelivered publish look delivered to every other reader.
    src = Path(prc.__file__).read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "git_commit_push")
    deferring = [n for n in ast.walk(fn)
                 if isinstance(n, ast.If)
                 and any(isinstance(r, ast.Return)
                         and "COMMITTED_DELIVERY_DEFERRED" in ast.dump(r)
                         for r in ast.walk(n))]
    assert deferring, "no branch in git_commit_push returns the deferred outcome"
    names = {c.func.id for n in deferring for c in ast.walk(n)
             if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
    assert "_record_push_time" not in names and "_record_content_published" not in names, names
    assert "record" in {getattr(c.func, "attr", "") for n in deferring for c in ast.walk(n)
                        if isinstance(c, ast.Call)}, (
        "the deferring branch must WRITE the deferral -- an outcome nothing can grade is worse "
        "than a pessimistic verdict")


def test_a_green_cycle_cannot_clear_a_wedge_over_figures_that_never_reached_origin(
        tmp_path, monkeypatch):
    """THE FAIL-OPEN THE REPAIR WOULD OTHERWISE HAVE OPENED. With the previous cycle's content
    committed but undelivered, the next cycle finds nothing to commit -- retryable, rc=0 -- and
    would have bought a clean-publish stamp for a publish the public never saw.

    MUTATION: delete the `_deferral == ABSORBING` leg from the rc=0 branch and this reds: the
    router answers "success" and `record_publish_gate_success` runs.
    """
    marker = tmp_path / "run_complete_x.md"
    marker.write_text("x")
    monkeypatch.setattr(prc, "_marker_git_hash", lambda m: "cafe1234")
    monkeypatch.setattr(prc, "_green_is_on_record_for", lambda h: True)
    cleared = []
    monkeypatch.setattr(prc, "record_publish_gate_success",
                        lambda *a, **k: cleared.append(True))

    monkeypatch.setattr(prc, "grade_outstanding_delivery", lambda *a, **k: pdd.ABSORBING)
    assert prc.record_publish_gate_outcome(str(marker), 0) == "unproven"
    assert cleared == [], "a wedge was cleared while a previous publish was still undelivered"

    # AND THE CONTROL CAN PASS: with nothing outstanding, the same green cycle clears normally.
    monkeypatch.setattr(prc, "grade_outstanding_delivery", lambda *a, **k: pdd.NONE)
    assert prc.record_publish_gate_outcome(str(marker), 0) == "success"
    assert cleared == [True]


def test_the_deferring_cycle_records_neither_a_success_nor_a_failure(tmp_path, monkeypatch):
    """rc=80 IS THE THIRD ANSWER. MUTATION: fall through to the generic `record_publish_gate_
    failure` at the foot of the router and every deferred cycle is a recorded failure again --
    which is the 58-failure episode, restored."""
    marker = tmp_path / "run_complete_y.md"
    marker.write_text("y")
    monkeypatch.setattr(prc, "_marker_git_hash", lambda m: "cafe1234")
    graded = []
    monkeypatch.setattr(prc, "grade_outstanding_delivery",
                        lambda *a, **k: graded.append(True) or pdd.ABSORBING)
    monkeypatch.setattr(prc, "record_publish_gate_success",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("success")))
    monkeypatch.setattr(prc, "record_publish_gate_failure",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("failure")))
    assert prc.record_publish_gate_outcome(
        str(marker), prc.EXIT_PUBLISH_DELIVERY_DEFERRED) == "deferred"
    assert graded == [True], "the owed verdict was not re-graded before the new one was recorded"


def test_the_owed_verdict_is_graded_on_every_return_code_the_router_grades(tmp_path, monkeypatch):
    """A DEFERRAL MUST NOT BE HELD OPEN BY THE RED CYCLES THAT MOST NEED IT GRADED.

    The two `NO_PUBLISH_EXIT_CODES` return before the grading and are outside this claim: on
    those the publisher never ran, so it has no later observation to offer.

    MUTATION: move the `grade_outstanding_delivery()` call inside the rc==0 branch and this reds
    on rc=77 -- a repeating red would hold an expired delivery unreported indefinitely.
    """
    src = Path(prc.__file__).read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "record_publish_gate_outcome")
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
             and getattr(n.func, "id", "") == "grade_outstanding_delivery"]
    assert len(calls) == 1, "one grading per routed cycle, not none and not several"
    # It is in the function BODY, not nested inside any rc branch.
    body_ifs = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.If)]
    nested = [i for i in body_ifs
              if any(getattr(c.func, "id", "") == "grade_outstanding_delivery"
                     for c in ast.walk(i) if isinstance(c, ast.Call))]
    assert nested == [], (
        "the grading is inside a conditional, so some return codes never take the owed verdict")


def test_the_kind_reaches_the_reader_that_decides_whether_to_hunt_a_red_test():
    """THE LABEL-WITHOUT-A-READER SHAPE. The supervisor's `WEDGE_KINDS_NO_TEST_JUDGED` decides
    whether a RUNG-1 draw is sent after a red test; a kind absent from it sends priority-zero
    work to run a ~10-minute suite for a red that does not exist.

    MUTATION: remove the kind from the supervisor's set, or rename it on one side only, and this
    reds -- which is the drift a string copied between two modules invites.
    """
    from background import supervisor
    assert prc.DELIVERY_NOT_REACHED_KIND in supervisor.WEDGE_KINDS_NO_TEST_JUDGED
    # And the kind has a LABEL, so the alarm does not print a bare slug at its reader.
    label = prc._gate_failure_label(prc.DELIVERY_NOT_REACHED_KIND)
    assert label != prc.DELIVERY_NOT_REACHED_KIND and "no gate refused" in label, label
    # The cause it travels with must suppress the blocking list: no test was judged red here.
    assert pc.no_test_was_judged(pc.LOST_PUSH_RACE)


def test_the_benign_window_is_the_deadmans_own_and_not_a_second_one():
    """ONE NAME, ONE VALUE. The deadman's constant is derived there from BLOCKED_THRESHOLD_
    SECONDS and its comment says why a second tolerance for this condition must not exist.

    MUTATION: hard-code a window in either module and this reds -- and the AST leg reds even if
    the two numbers happen to agree on the day it is written, which is the whole point.
    """
    assert prc._race_benign_seconds() == float(dms.RACE_PERSISTENCE_SECONDS)
    tree = ast.parse(Path(pdd.__file__).read_text(encoding="utf-8"))
    minted = [t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
              for t in n.targets if isinstance(t, ast.Name)
              and t.id.isupper() and ("SECONDS" in t.id or "WINDOW" in t.id)]
    assert minted == [], (
        "the deferral ledger minted its own tolerance for a condition the machine already "
        "declares one for: {}".format(minted))


def test_an_unreadable_benign_window_expires_the_deferral(monkeypatch):
    """AN UNAVAILABLE CHECK IS A FAILED CHECK. MUTATION: return a large default when the
    deadman cannot be imported and an import error becomes an unbounded licence to wait."""
    import builtins
    real = builtins.__import__

    def _boom(name, *a, **k):
        if name == "background.deadmans_switch":
            raise ImportError("no deadman here")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _boom)
    assert prc._race_benign_seconds() == 0.0


def test_the_module_is_wired_into_the_publish_path():
    """AN UNWIRED MECHANISM IS NOT A MECHANISM. MUTATION: delete the `publish_delivery_deferral`
    import from the publisher and this reds by name rather than leaving a module nothing runs."""
    src = Path(prc.__file__).read_text(encoding="utf-8")
    assert "publish_delivery_deferral" in src
    assert isinstance(prc.publish_delivery_deferral, types.ModuleType)
    assert prc.PUBLISH_DELIVERY_DEFERRAL_FILE.name == ".publish_delivery_deferral.json"


def test_a_failed_owed_grading_still_records_this_cycles_verdict(tmp_path, monkeypatch):
    """9. THE OWED VERDICT MAY NOT COST THE CURRENT ONE, AND MAY NOT BUY IT EITHER.

    THE DEFECT (2026-09-26, found by the operational-layer signal going red for 5 consecutive
    hourly checks): `grade_outstanding_delivery()` fetches origin, asks ancestry and writes two
    observability files -- all on behalf of a PREVIOUS cycle -- and it sat bare under this
    router's single outer `except Exception`. So any error in that leg returned None and THIS
    cycle's failure was never recorded: the wedge streak stops growing at exactly the moment
    something is wrong, which is the router's whole subject.

    BOTH DIRECTIONS IN ONE CONTROL, because the repair's own fail-open is the mirror image:
      * a raised grading must not suppress a red cycle's recorded failure; and
      * it must not be read as "nothing outstanding" on a GREEN cycle either -- `_deferral` is
        then None, which `== ABSORBING` answers False for, so an ERROR would have bought the
        clean-publish stamp that leg exists to withhold.

    MUTATION: remove the `try` around the grading call and the first leg reds (the router
    answers None and records nothing). Drop the `_deferral_ungraded` check from the rc==0 branch
    and the second reds (the router answers "success" and the wedge clears).
    """
    marker = tmp_path / "run_complete_z.md"
    marker.write_text("z")
    monkeypatch.setattr(prc, "_marker_git_hash", lambda m: "cafe1234")
    monkeypatch.setattr(prc, "_green_is_on_record_for", lambda h: True)

    def _raises(*a, **k):
        raise OSError("the deferral surface is unwritable")

    monkeypatch.setattr(prc, "grade_outstanding_delivery", _raises)

    recorded, cleared = [], []
    monkeypatch.setattr(prc, "record_publish_gate_failure",
                        lambda *a, **k: recorded.append(k))
    monkeypatch.setattr(prc, "record_publish_gate_success",
                        lambda *a, **k: cleared.append(True))

    assert prc.record_publish_gate_outcome(str(marker), 1) == "failure", (
        "an error grading a PREVIOUS cycle's delivery discarded THIS cycle's verdict")
    assert len(recorded) == 1 and recorded[0]["rc"] == 1, recorded

    assert prc.record_publish_gate_outcome(str(marker), 0) == "unproven", (
        "an ungradable owed delivery was read as 'nothing outstanding' and bought a clean publish")
    assert cleared == [], "the wedge was cleared on a delivery nobody could grade"

    # AND THE CONTROL CAN PASS BOTH WAYS: with the grading answering NONE, the same green cycle
    # clears normally -- so neither leg above is green merely because rc=0 never clears anything.
    monkeypatch.setattr(prc, "grade_outstanding_delivery", lambda *a, **k: pdd.NONE)
    assert prc.record_publish_gate_outcome(str(marker), 0) == "success"
    assert cleared == [True]
