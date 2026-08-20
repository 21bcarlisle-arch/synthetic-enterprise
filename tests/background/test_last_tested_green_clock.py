"""THE GREEN'S CLOCK -- the WRITER half of the `.last_tested_hash` contract's 2026-08-20 repair.

`.last_tested_hash` records WHICH commit the publish gate last passed at and nothing about WHEN.
Its wedge-detector consumer needed "when", so it borrowed git ancestry as a clock -- and since
OPS3 made the publish queue a STACK (`order = list(reversed(pending))`, newest marker first),
ancestry is ANTI-CORRELATED with time across a drain. Observed live 2026-08-20 16:31Z: a green
recorded at 15:34:03Z sat THREE COMMITS BEHIND the failure it was supposed to supersede, and the
RUNG-1 priority-zero alarm stayed armed through three consecutive ticks on a gate that was green
and publishing. Evidence: docs/staging/done/WORKER_FINDING_THE_WEDGES_ORDERING_INSTRUMENT_RUNS_
BACKWARDS_SINCE_THE_QUEUE_BECAME_A_STACK_2026-08-20.md.

The repair is a sidecar, `.last_tested_green.json` = {"sha": ..., "ts": ...}, written by the SAME
writer in the SAME rc=0 branch. The READER half is proven in test_publish_gate_wedge_draw.py.
This module owns the writer, and the property that matters is not "it writes a file" -- it is
that the file is written on EXACTLY the same trigger as the hash it describes. A sidecar written
on any other trigger (a red, a timeout, an unavailable checkout) would be a green claim the gate
never made, which collapses the independence the whole wedge cross-check rests on.

R15 both ways, on the three named defects:
  * FAIL-OPEN -- a clock stamped on a RED. Proven absent by running the red path.
  * BREAKING THE PIPELINE IT MONITORS -- an unwritable sidecar must not red a publish the suite
    already passed, and must leave the alarm ARMED rather than silently cleared.
  * WRITING THE LIVE RECORD FROM A SANDBOX -- the sidecar's location is DERIVED from the hash
    file's, so a test that redirects the hash cannot leave a fixture value in the production
    file. This one was caught in the act rather than imagined: see
    `test_mutation_the_sidecar_written_at_the_module_default_lands_in_the_live_record`.
"""
import json
import subprocess

import pytest

from background import process_run_complete as prc


@pytest.fixture
def gate(tmp_path, monkeypatch):
    """`_run_gate_in` with everything around the subprocess stubbed, and both record files
    redirected into tmp_path. Returns a runner taking the suite's return code.

    ONLY THE HASH IS REDIRECTED, deliberately: the sidecar's location is derived from it by
    `_green_clock_path`, and this fixture would hide that if it named the sidecar separately.
    `green_file` below is therefore a PREDICTION of where the writer will land it, not an
    instruction -- which is what makes it worth asserting."""
    hash_file = tmp_path / ".last_tested_hash"
    green_file = tmp_path / prc.LAST_TESTED_GREEN_FILE.name
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", hash_file)
    monkeypatch.setattr(prc, "_scoped_gate_argv",
                        lambda run_root=None: (["true"], {"reason": "stub", }))
    monkeypatch.setattr(prc, "_record_gate_duration", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_clear_blocking_tests", lambda *a, **k: None)
    monkeypatch.setattr(prc, "run_red_census", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_log_gate_failure_payload", lambda *a, **k: None)
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)

    def run(rc, git_hash="abc1234"):
        monkeypatch.setattr(prc.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(
            args=["true"], returncode=rc, stdout="", stderr=""))
        return prc._run_gate_in(tmp_path, {}, git_hash)

    return run, hash_file, green_file


def test_a_green_stamps_the_sha_and_the_clock_together(gate):
    """MUST FIRE: rc=0 writes BOTH halves, naming the same commit."""
    run, hash_file, green_file = gate
    published, _ = run(0)

    assert published is True
    assert hash_file.read_text().strip() == "abc1234"
    rec = json.loads(green_file.read_text())
    assert rec["sha"] == "abc1234", "the two halves must describe one green"
    assert isinstance(rec["ts"], float) and rec["ts"] > 1_700_000_000


def test_mutation_a_RED_stamps_neither(gate):
    """THE FAIL-OPEN MUTATION, and the direction that would be catastrophic.

    A clock written on a red is a green claim the gate never made -- and because the reader
    treats a clock newer than the failures as "those failures are stale", it would silence the
    RUNG-1 alarm exactly when publishing is genuinely frozen. Move the
    `_record_gate_green_clock` call one line up, out of the `rc == 0` branch, and this reds."""
    run, hash_file, green_file = gate
    published, _ = run(1)

    assert published is False
    assert not hash_file.exists()
    assert not green_file.exists(), "a red must leave NO claim that the gate passed"


def test_a_timeout_stamps_neither(gate, monkeypatch):
    """The same rule for the gate that never finished. `_run_gate_in` re-raises, and a suite that
    did not return cannot have returned zero -- `test_a_timed_out_gate_blocks_the_publish` pins
    the hash side of this; the clock must not become the loophole."""
    run, hash_file, green_file = gate
    monkeypatch.setattr(prc.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(
        subprocess.TimeoutExpired(cmd=["true"], timeout=1)))

    with pytest.raises(subprocess.TimeoutExpired):
        prc._run_gate_in(hash_file.parent, {}, "abc1234")

    assert not hash_file.exists()
    assert not green_file.exists()


def test_an_unwritable_clock_never_reds_a_publish_the_suite_passed(gate, monkeypatch, tmp_path):
    """MUST NOT BREAK THE PIPELINE IT MONITORS. The sidecar write fails; the publish still
    succeeds and the hash -- the file two other consumers depend on -- is still written.

    The cost is stated rather than hidden: with no clock recorded the wedge reader answers "no
    green is claimed" and RUNG 1 stays ARMED. A lost stamp buys a phantom draw, never silence."""
    run, hash_file, green_file = gate
    # The sabotage is at the RESOLVED location, one layer below the constant, because the
    # constant no longer decides where the write goes -- `_green_clock_path` does.
    monkeypatch.setattr(prc, "_green_clock_path", lambda: tmp_path / "no-such-dir" / "green.json")

    published, _ = run(0)

    assert published is True, "a monitoring record must never red a green suite"
    assert hash_file.read_text().strip() == "abc1234"
    assert not green_file.exists()


def test_the_stamp_reports_whether_it_landed(tmp_path, monkeypatch):
    """`_record_gate_green_clock` returns its own outcome, so both directions are assertable
    rather than inferred from a side effect that may not exist (R15: a control that cannot be
    observed failing is not evidence)."""
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    ok = tmp_path / prc.LAST_TESTED_GREEN_FILE.name
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)
    assert prc._record_gate_green_clock("abc1234", now=1_800_000_000.0) is True
    assert json.loads(ok.read_text()) == {"sha": "abc1234", "ts": 1_800_000_000.0}

    monkeypatch.setattr(prc, "_green_clock_path", lambda: tmp_path / "nope" / "green.json")
    assert prc._record_gate_green_clock("abc1234") is False


def test_the_writer_and_the_reader_agree_on_the_shape(tmp_path, monkeypatch):
    """THE SEAM ITSELF -- the two halves are in different modules, so nothing but this asserts
    that what one writes is what the other parses. Round-trip, no hand-built fixture: the reader
    is handed the writer's actual bytes at the writer's actual path.

    This is the pin that would have caught the ORIGINAL defect's cousin -- a producer and a
    consumer each individually correct about a record neither of them shares."""
    from background import supervisor

    hash_file = tmp_path / ".last_tested_hash"
    hash_file.write_text("abc1234")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", hash_file)
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)

    assert prc._record_gate_green_clock("abc1234", now=1_800_000_000.0) is True
    assert supervisor._recorded_green_clock("abc1234", last_tested_path=hash_file) == 1_800_000_000.0
    assert supervisor._recorded_green_clock("a-different-sha", last_tested_path=hash_file) is None
    # The two halves agree on the NAME as well as the shape: the writer derives its filename from
    # its own constant and the reader from the supervisor's, so a rename on one side alone would
    # split the record silently. Nothing else in either module asserts they are the same string.
    assert prc.LAST_TESTED_GREEN_FILE.name == supervisor.LAST_TESTED_GREEN_FILE.name


def test_mutation_the_sidecar_written_at_the_module_default_lands_in_the_live_record(
        gate, monkeypatch, tmp_path):
    """THE THIRD MUTATION, on a defect observed in production rather than imagined.

    Restore the first draft's write target -- `LAST_TESTED_GREEN_FILE` instead of the derived
    `_green_clock_path()` -- and this test reds, because a fixture that redirected only the hash
    file then stamps the REAL `docs/observability/.last_tested_green.json`. That is not a
    hypothetical: on 2026-08-20 the live file was found holding `{"sha": "deadbeef"}` written at
    17:41:55Z, later than the machine's actual green at 17:03:38Z, by
    `tests/background/test_process_run_complete.py:1325`.

    The assertion is on the RESOLVED LOCATION, not on the absence of a live file: asserting
    "the production path was not written" would need to read production state to decide a test's
    verdict, which is the same boundary crossing in the other direction."""
    run, hash_file, green_file = gate
    module_default = prc.LAST_TESTED_GREEN_FILE

    published, _ = run(0)

    assert published is True
    assert prc._green_clock_path() == green_file, "the sidecar must follow the hash file"
    assert green_file.exists() and json.loads(green_file.read_text())["sha"] == "abc1234"
    assert prc._green_clock_path() != module_default, (
        "the writer resolved to the production path from inside a sandbox -- this is how a "
        "fixture SHA reaches the live wedge record")
    assert tmp_path in prc._green_clock_path().parents
