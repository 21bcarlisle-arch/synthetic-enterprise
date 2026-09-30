"""The publisher's gate asks the memory governor before its suite starts, and is counted while it runs.

THE DEFECT. `resource_headroom.CLASS_WEIGHTS_MB` has carried `publish_gate` and `census` weights
since 2026-08-10, and until this file nothing asked for them: after 38ee201e6 the only `admit()`
caller was sim-runner, and `reservation()` had no caller at all -- so sim-runner's admission
summed a reservation ledger nobody wrote, and a gate running beside a long job was one of the
undeclared residents the arithmetic cannot see (the shape 19:07Z died of).

Two halves, and each is a mutation this file kills:
  * REFUSED  -> the suite never starts, a deferral receipt is written, and the refusal is recorded
    as UNJUDGED with the governor's reason -- never as a red test.
  * ADMITTED -> the suite runs INSIDE a live `publish_gate` reservation, so a concurrent asker's
    `committed_mb` counts it; and the reservation is gone afterwards.
The partition is asserted over both, so a gate that defers everything cannot pass.
"""
import json

import pytest

import background.process_run_complete as prc
import background.publish_cause as pc
from background import resource_headroom as rh
from tests.background.publish_gate_root_shape import materialise_repo_shaped_root

GIT_HASH = "38ee201e6"


@pytest.fixture
def _publish_gate_admitted():
    """Overrides the directory's admit-by-default seam: the real `_gate_admission` is the subject."""


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / ".last_publish_cause.json")
    monkeypatch.setattr(rh, "RESERVATIONS_PATH", tmp_path / "reservations.json")
    monkeypatch.setattr(rh, "DEFERRAL_LOG_PATH", tmp_path / "deferrals.jsonl")


def _governor(monkeypatch, admitted):
    asked = []

    def _admit(job_class, **kw):
        asked.append(job_class)
        return {"job_class": job_class, "admitted": admitted,
                "reason": "admitted: test" if admitted else "budget exhausted: 22000 MB declared"}

    monkeypatch.setattr(rh, "admit", _admit)
    return asked


def _drive(monkeypatch, tmp_path):
    """Run the real `run_fast_tests`; record what the suite saw of the reservation ledger."""
    seen = {}

    def _suite(head_dir, full_env, git_hash):
        seen["reserved_mb"] = rh.committed_mb()
        seen["classes"] = [r["job_class"] for r in rh.live_reservations()]
        return True, False

    monkeypatch.setattr(prc, "_run_gate_in", _suite)
    monkeypatch.setattr(prc, "_repair_derived_artefacts_in", lambda head_dir: None)

    import contextlib

    @contextlib.contextmanager
    def _checkout():
        yield materialise_repo_shaped_root(tmp_path / "head")

    monkeypatch.setattr(prc, "_head_checkout", _checkout)
    verdict = prc.run_fast_tests(GIT_HASH)
    return verdict, seen


def test_the_gate_is_governed_in_both_directions(monkeypatch, tmp_path):
    outcomes = {}
    for admitted in (True, False):
        asked = _governor(monkeypatch, admitted)
        verdict, seen = _drive(monkeypatch, tmp_path)
        assert asked == ["publish_gate"], "the gate did not ask the governor before its suite"
        outcomes[admitted] = (verdict, seen)

    # ADMITTED: the suite ran, inside a reservation a concurrent asker counts.
    verdict, seen = outcomes[True]
    assert verdict == (True, False)
    assert seen["classes"] == ["publish_gate"]
    assert seen["reserved_mb"] == rh.CLASS_WEIGHTS_MB["publish_gate"]
    assert rh.live_reservations() == [], "the reservation outlived the suite"

    # REFUSED: the suite never started; the refusal is receipted and recorded as unjudged.
    verdict, seen = outcomes[False]
    assert verdict == (False, False)
    assert seen == {}, "a deferred gate ran its suite anyway"
    receipts = [json.loads(line) for line in
                (tmp_path / "deferrals.jsonl").read_text().splitlines()]
    assert [r["job_class"] for r in receipts] == ["publish_gate"]
    cause, evidence = pc.read_cause(prc.PUBLISH_CAUSE_FILE, GIT_HASH)
    assert cause == pc.SCOPED_GATE_UNJUDGED
    assert "DEFERRED" in evidence and "budget exhausted" in evidence


def test_a_deferred_gate_is_refused_as_unjudged_never_as_a_red(monkeypatch, tmp_path):
    """The wedge router reads the recorded cause: a deferral must implicate no test."""
    _governor(monkeypatch, admitted=False)
    (tests_ok, timed_out), _ = _drive(monkeypatch, tmp_path)
    code, _line, reason = prc._gate_refusal(
        timed_out, GIT_HASH, [], cause=prc._scoped_gate_cause(GIT_HASH)[0])
    assert code == prc.EXIT_SCOPED_GATE_REFUSED
    assert "UNJUDGED" in reason


def test_a_governor_that_raises_defers_the_gate(monkeypatch, tmp_path):
    def _boom(job_class, **kw):
        raise OSError("meminfo unreadable")

    monkeypatch.setattr(rh, "admit", _boom)
    verdict, seen = _drive(monkeypatch, tmp_path)
    assert verdict == (False, False) and seen == {}
    assert "raised OSError" in (tmp_path / "deferrals.jsonl").read_text()
