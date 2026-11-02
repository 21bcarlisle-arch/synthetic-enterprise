"""R15: a book the domain-invariant gate refuses is recorded as that, never as a red test.

OBSERVED (2026-11-02, docs/observability/sim-runner-log.md + .publish_gate_state.json): the gate
logged "Domain-invariant gate REFUSED the publish ... INV_RENEWAL_NOTICE_42_TO_49_DAYS 1171" and
left by a bare `return 1`, so the record read `kind: test_regression, cause: unattributed` five
times for bb58608b91, and the RUNG-1 draw was sent to diagnose a pytest red that never existed.
"""
import inspect
import json

import pytest

import background.process_run_complete as prc
import background.publish_cause as pc
import background.supervisor as sup

MARKER_HASH = "bb58608b91"
MARKER_NAME = "run_complete_20261102T070308Z.md"
REFUSAL = "INV_RENEWAL_NOTICE_42_TO_49_DAYS 1171 (no exception)"


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / ".last_publish_cause.json")
    monkeypatch.setattr(prc, "DOMAIN_INVARIANT_JSON", tmp_path / "domain_invariants.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    done = tmp_path / "staging" / "done"
    done.mkdir(parents=True)
    (done / MARKER_NAME).write_text("# Run complete\n\nGit: {}\n".format(MARKER_HASH))
    monkeypatch.setattr(prc, "DONE_DIR", done)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    yield done / MARKER_NAME


def _route(marker, graded_at):
    prc.DOMAIN_INVARIANT_JSON.write_text(json.dumps(
        {"git": graded_at, "verdict": {"refuse": True, "enforce": True, "refusal": REFUSAL}}))
    assert prc.record_publish_gate_outcome(str(marker), prc.EXIT_DOMAIN_INVARIANT_REFUSED) == "failure"
    return json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())["failures"][-1]


def test_the_refusal_is_recorded_with_the_breaches_it_named(_isolate):
    """MUTATION: delete the rc=82 branch in `record_publish_gate_outcome` and the generic
    fall-through records `test_regression`/`unattributed` -- the 2 Nov record -- and this reds."""
    failure = _route(_isolate, MARKER_HASH)
    assert failure["kind"] == prc.DOMAIN_INVARIANT_REFUSED_KIND
    assert failure["cause"] == pc.DOMAIN_INVARIANT_REFUSED
    assert REFUSAL in failure["cause_evidence"]


def test_a_table_graded_at_another_commit_is_not_read_as_this_books(_isolate):
    """MUTATION: drop the git match in `_domain_invariant_cause` and another book's breaches are
    cited as this one's, and this reds."""
    failure = _route(_isolate, "e664b5720")
    assert failure["kind"] == prc.DOMAIN_INVARIANT_REFUSED_KIND, "still no test was judged"
    assert failure["cause"] == pc.UNATTRIBUTED
    assert REFUSAL not in failure["cause_evidence"]


def test_the_production_refusal_leaves_by_its_own_door():
    """The code can be routed only if `_process` returns it. MUTATION: restore `return 1` after
    the refusal log line and this reds."""
    src = inspect.getsource(prc._process)
    after = src.split("Domain-invariant gate REFUSED the publish", 1)[1]
    first_return = after.split("return", 1)[1].split("\n", 1)[0].strip()
    assert first_return == "EXIT_DOMAIN_INVARIANT_REFUSED"
    assert prc._classify_gate_failure(prc.EXIT_DOMAIN_INVARIANT_REFUSED) == "test_regression", (
        "if the generic classifier ever names rc=82 itself, the router branch is no longer the "
        "only thing keeping it from reading as a red -- re-establish which one is load-bearing")


def test_the_kind_is_heard_by_the_draw_and_a_red_still_silences_it():
    """A label with no reader is the sibling defect; and a clause that is printed when a test IS
    red tells a worker not to look for it. Both legs, over one draw."""
    assert prc.DOMAIN_INVARIANT_REFUSED_KIND in prc.UNJUDGED_GATE_KINDS
    assert prc.DOMAIN_INVARIANT_REFUSED_KIND in sup.WEDGE_KINDS_NO_TEST_JUDGED
    assert pc.DOMAIN_INVARIANT_REFUSED in pc.NO_TEST_JUDGED_CAUSES
    only_book = [{"kind": prc.DOMAIN_INVARIANT_REFUSED_KIND}] * 3
    clause = sup._wedge_no_test_judged_clause(only_book, False)
    assert "DOMAIN_INVARIANTS.md" in clause
    assert sup._wedge_no_test_judged_clause(only_book + [{"kind": "test_regression"}], False) == ""
    assert prc._gate_failure_label(prc.DOMAIN_INVARIANT_REFUSED_KIND) != prc.DOMAIN_INVARIANT_REFUSED_KIND
