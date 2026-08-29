"""The probe that makes the producer's footprint measurable without running the job that OOMs.

The defect it serves is recorded in
`WORKER_FINDING_THE_PRODUCER_OOMS_BECAUSE_THE_BOOK_GREW_AND_SETTLEMENT_SCALES_WITH_IT_2026-08-24.md`:
the footprint repair is the only one of three that is not the director's, and its own test loop is
the 40-minute 14GB run that cannot complete. This tool measures short horizons instead.

WHAT IS UNDER TEST is mostly the REFUSAL. A probe that launches a second heavy job beside a live
producer run would compete for exactly the memory it is measuring and could cause the OOM it is
investigating -- a measurement that changed its own subject. So the guard is the load-bearing part
and it is tested in all three directions: fires, stands down, and fails CLOSED.
"""
from __future__ import annotations

import subprocess

import pytest

from tools import settlement_footprint_probe as probe


class _Proc:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


def test_the_probe_REFUSES_while_a_producer_run_is_in_flight(monkeypatch):
    """THE GUARD. Competing for the memory under measurement is how a probe causes the outage it
    is investigating."""
    monkeypatch.setattr(probe.subprocess, "run", lambda *a, **k: _Proc(stdout="2795477\n"))

    assert probe.a_run_is_in_flight() == "2795477"
    assert probe.main(["--years", "2017"]) == 2, "a refusal must be a non-zero exit"


def test_MUTATION_the_probe_stands_down_on_an_idle_box(monkeypatch):
    """R15 null control. A guard that always refused would pass the test above on a tool that
    could never run at all, which is the same as not having built it."""
    monkeypatch.setattr(probe.subprocess, "run", lambda *a, **k: _Proc(stdout="", returncode=1))
    assert probe.a_run_is_in_flight() is None

    measured = []
    monkeypatch.setattr(probe, "measure",
                        lambda y, **k: measured.append(y) or {"end_year": y, "ok": True,
                                                              "peak_rss_mb": 100.0})
    assert probe.main(["--years", "2017"]) == 0
    assert measured == [2017], "an idle box must actually be measured"


def test_the_guard_FAILS_CLOSED_when_it_cannot_tell(monkeypatch):
    """R15 fail-silent: an unavailable check is a FAILED check. The harmful direction here is
    launching a second 14GB job, not skipping a measurement, so an unusable pgrep must refuse."""
    def _boom(*a, **k):
        raise OSError("pgrep missing")

    monkeypatch.setattr(probe.subprocess, "run", _boom)
    live = probe.a_run_is_in_flight()

    assert live is not None and "refusing" in live.lower()
    assert probe.main(["--years", "2017"]) == 2


def test_force_overrides_the_guard_deliberately(monkeypatch):
    """The override exists so an idle box is not held hostage by a stale detection -- but it must
    be explicit, never the default."""
    monkeypatch.setattr(probe, "a_run_is_in_flight", lambda: "999")
    monkeypatch.setattr(probe, "measure", lambda y, **k: {"end_year": y, "ok": True,
                                                          "peak_rss_mb": 100.0})
    assert probe.main(["--years", "2017", "--force"]) == 0


def test_a_child_killed_by_the_OOM_killer_is_REPORTED_not_hidden(monkeypatch):
    """The interesting outcome, not an error to swallow. A probe that reported only successful
    horizons would derive its scaling from the survivors of the very bound it is measuring."""
    monkeypatch.setattr(probe.subprocess, "run",
                        lambda *a, **k: _Proc(returncode=-9, stderr="Maximum resident set size (kbytes): 14198884"))

    row = probe.measure(2025)
    assert row["ok"] is False
    assert row["killed_by_signal"] == 9
    assert row["peak_rss_mb"] == pytest.approx(13866.1, abs=1.0)


def test_the_scaling_separates_per_year_cost_from_fixed_cost():
    """The reading that decides whether the footprint work is worth doing: a large FIXED term means
    shortening the window will not save the producer, and the effort belongs elsewhere."""
    out = probe.summarise([
        {"end_year": 2017, "peak_rss_mb": 2000.0},
        {"end_year": 2019, "peak_rss_mb": 4000.0},
    ])

    assert out["slope_mb_per_year"] == pytest.approx(1000.0)
    assert "fixed" in out["note"]


def test_one_horizon_cannot_produce_a_scaling_law():
    """VACUITY GUARD. A slope from a single point is invented, not measured."""
    out = probe.summarise([{"end_year": 2017, "peak_rss_mb": 2000.0}])
    assert out["slope_mb_per_year"] is None
    assert "at least two" in out["note"]


# ---------------------------------------------------------------------------
# The guard's SUBJECT: a matched command line is not the same thing as a run.
# Class `a_pgrep_waiter_matches_the_agent_whose_prompt_quotes_the_subject`,
# observed live 2026-08-29 while taking the settlement-ceiling measurement.
# ---------------------------------------------------------------------------


def _pgrep_returning(*pids):
    return lambda *a, **k: _Proc(stdout="".join(f"{p}\n" for p in pids))


def test_the_AGENT_whose_PROMPT_quotes_the_module_is_not_a_producer_run(monkeypatch):
    """THE DEFECT. `pgrep -f` matches the whole command line, so the autonomous worker launched
    as `claude -p "<prompt mentioning tools.run_annual_report>"` was reported as the producer the
    probe had to stand down for. It cannot ever clear: the agent's prompt is its own argv, so the
    guard refused every point of the measurement it had been told to take, and `--force` -- which
    disables the guard entirely -- was the only way past it."""
    monkeypatch.setattr(probe.subprocess, "run", _pgrep_returning("4050583"))
    monkeypatch.setattr(probe, "_argv_of", lambda pid: [
        "/home/rich/.nvm/versions/node/v24.16.0/bin/claude", "-p",
        "--dangerously-skip-permissions", "--model", "claude-opus-5",
        "You are the autonomous worker ... `tools/settlement_ceiling_probe.py` calls "
        "`tools.run_annual_report._run_and_extract` ... stand the live producer down",
    ])

    assert probe.a_run_is_in_flight() is None, (
        "a process that MENTIONS the module in an argument is not running it"
    )


def test_a_real_producer_launch_IS_still_detected(monkeypatch):
    """The other half, or the fix above is just a disabled guard. `background/sim_runner.py:240`
    launches exactly this argv, and it must still stop the probe."""
    monkeypatch.setattr(probe.subprocess, "run", _pgrep_returning("4021373"))
    monkeypatch.setattr(probe, "_argv_of", lambda pid: [
        "/usr/bin/python3", "-m", "tools.run_annual_report", "--out", "/tmp/report.md",
    ])

    assert probe.a_run_is_in_flight() == "4021373"


def test_the_producer_is_found_BEHIND_a_mentioner(monkeypatch):
    """Order is not a filter. The agent's pid sorts first here, and returning `pids[0]` after
    discarding nothing -- or discarding and then giving up -- would both miss the real run."""
    monkeypatch.setattr(probe.subprocess, "run", _pgrep_returning("100", "200"))
    argvs = {
        "100": ["bash", "-c", "grep -n tools.run_annual_report background/sim_runner.py"],
        "200": ["/usr/bin/python3", "-m", "tools.run_annual_report"],
    }
    monkeypatch.setattr(probe, "_argv_of", lambda pid: argvs[pid])

    assert probe.a_run_is_in_flight() == "200"


def test_an_UNREADABLE_argv_still_refuses(monkeypatch):
    """FAIL-CLOSED, preserved. `/proc/<pid>/cmdline` is unreadable for a process owned by another
    user, and for one that exited between `pgrep` and the read. Neither is evidence of an idle
    box, so neither may clear the guard -- the shape check narrows the guard's subject, and must
    not turn a second way of not knowing into a pass."""
    monkeypatch.setattr(probe.subprocess, "run", _pgrep_returning("2795477"))
    monkeypatch.setattr(probe, "_argv_of", lambda pid: None)

    assert probe.a_run_is_in_flight() == "2795477"


def test_a_script_path_launch_counts_as_a_run():
    """`python3 tools/run_annual_report.py` puts no `-m` in argv and is the same job."""
    assert probe._argv_is_a_producer_run(
        ["/usr/bin/python3", "/home/rich/synthetic-enterprise/tools/run_annual_report.py"]
    )
    assert not probe._argv_is_a_producer_run(
        ["/usr/bin/python3", "/home/rich/synthetic-enterprise/tools/run_annual_report_test.py"]
    )


def test_argv_of_reads_this_process(tmp_path):
    """The reader is not mocked anywhere real, so it is exercised once against a live `/proc`.
    A `_argv_of` that always returned None would leave every test above passing while the guard
    silently reverted to matching substrings."""
    import os

    argv = probe._argv_of(str(os.getpid()))
    assert argv and any("pytest" in a or "python" in a for a in argv)


def test_a_process_that_merely_NAMES_the_file_as_an_argument_is_not_a_run():
    """CAUGHT BY PRINTING AT REAL INPUTS, not by thinking. The first repair above narrowed the
    `-m` branch and left the script-path branch matching ANY argv element ending in
    `tools/run_annual_report.py`. Within the hour, `python3 -m tools.surgical_land <paths...>`
    -- landing that very repair, with the file listed as a path to commit -- was reported as a
    live producer run.

    An argument is not an invocation. The module or script is the FIRST argv element after the
    interpreter's own options; everything after it is the program's data."""
    assert not probe._argv_is_a_producer_run(
        ["timeout", "2400", "python3", "-m", "tools.surgical_land",
         "tools/run_annual_report.py", "simulation/settlement_clocks.py"]
    )
    assert not probe._argv_is_a_producer_run(
        ["/usr/bin/python3", "-m", "tools.surgical_land", "tools/run_annual_report.py"]
    )
    assert not probe._argv_is_a_producer_run(
        ["/usr/bin/python3", "-m", "pytest", "tests/", "-k", "run_annual_report"]
    )


def test_a_NON_python_process_is_never_a_run():
    """`git`, `grep`, an editor -- none of them run the report however their argv reads. Pinning
    this is what stops the next widening of the script-path branch reaching them."""
    assert not probe._argv_is_a_producer_run(["git", "add", "tools/run_annual_report.py"])
    assert not probe._argv_is_a_producer_run(["vim", "tools/run_annual_report.py"])
    assert not probe._argv_is_a_producer_run([])


def test_interpreter_OPTIONS_do_not_hide_the_module():
    """`python3 -u -m tools.run_annual_report` is the same job. Scanning must skip the
    interpreter's own flags rather than give up at the first one."""
    assert probe._argv_is_a_producer_run(
        ["/usr/bin/python3", "-u", "-m", "tools.run_annual_report"]
    )
    assert probe._argv_is_a_producer_run(
        ["/usr/bin/python3", "-m", "tools.run_annual_report.cli"]
    )
