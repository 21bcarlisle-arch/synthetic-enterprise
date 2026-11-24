"""A long job still waiting on an artefact must not hold the memory that admits that artefact.

Defect this fires on (24 Nov 2026): the A4 arm (12000 MB) and land10 (6000 MB) were launched and
declared while they slept on files only the owed book could produce, and sim-runner deferred that
book every five minutes against their 18000 MB -- a cycle book <- land10 <- b11m7 <- A4 -> book.
The fix: `launch(awaits=...)` is refused as NoRoom while the path is absent, so the wait queues
in a unit with no launch record and no declared peak, and admission is asked at fire time.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from background import launch_long_job as llj
from background import resource_headroom as rh

BOOK_MB = 7066.0


class _Runner:
    def __call__(self, argv, **kw):
        if argv[:3] == ["systemctl", "--user", "show"]:
            return subprocess.CompletedProcess(
                argv, 0, "ActiveState=\nControlGroup=/user.slice/other.service\n", "")
        return subprocess.CompletedProcess(argv, 0, "", "")


@pytest.fixture
def box(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(llj, "own_cgroup", lambda *a, **k: "/user.slice/launcher.service")
    monkeypatch.setattr(llj, "_wait_for_pending_landings", lambda *a, **k: None)
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(f"MemTotal: {24034 * 1024} kB\nMemAvailable: {20000 * 1024} kB\n")
    return tmp_path, meminfo


def _launch_waiter(tmp_path, awaits):
    """Declared at 18000 MB: the A4 and land10 waiters together, which left the book no room."""
    return llj.launch("a4-like-arm", ["python3", "-m", "tools.nothing"],
                      artefact=str(tmp_path / "grade.out"), workdir=str(tmp_path),
                      log=str(tmp_path / "job.log"), records_path=tmp_path / "records.json",
                      runner=_Runner(), peak_mb=18000, residents=lambda: [],
                      guest_total_mb=24034, expect_minutes=30, awaits=[str(awaits)])


def _book_admitted(tmp_path, meminfo, residents):
    return rh.admit("book", weight_mb=BOOK_MB, reservations_path=tmp_path / "ledger.json",
                    launch_records_path=tmp_path / "records.json", residents=residents,
                    meminfo_path=meminfo)


def test_a_waiter_on_the_books_output_cannot_defer_the_book_and_a_running_job_still_counts(box):
    tmp_path, meminfo = box
    readout = tmp_path / "readout.json"           # what the book's readers produce, not yet there
    with pytest.raises(llj.NoRoom, match="awaiting"):
        _launch_waiter(tmp_path, readout)
    assert llj.declared_peaks(tmp_path / "records.json") == {}, "a waiter left a declaration"
    assert _book_admitted(tmp_path, meminfo, residents=[])["admitted"]

    # The file exists: the same launch now starts, declares, and DOES count against the book.
    readout.write_text("{}")
    entry = _launch_waiter(tmp_path, readout)
    unit = f"{entry['unit']}.service"
    assert llj.declared_peaks(tmp_path / "records.json") == {unit: 18000.0}
    running = [{"pid": 4242, "rss_mb": 300.0, "unit": unit, "command": "python3"}]
    held = _book_admitted(tmp_path, meminfo, residents=running)
    assert not held["admitted"] and "18000 MB" in held["reason"], held["reason"]


def test_sim_runner_does_not_yield_to_a_queue_that_awaits_an_artefact_but_does_to_one_awaiting_room(
        tmp_path):
    """The queue unit is where the waiter now waits. sim-runner yields to every queued long job
    (they wait for room); one still awaiting a missing file is not waiting for room, and yielding
    to it re-made the cycle one level up (24 Nov, 21:35Z)."""
    from background import sim_runner

    readout = tmp_path / "readout.json"

    def runner(argv, **kw):
        if "list-units" in argv:
            return subprocess.CompletedProcess(argv, 0, "longjob-a4-queued.service loaded active running q\n", "")
        return subprocess.CompletedProcess(argv, 0, (
            "ExecStart={ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -m background.launch_long_job "
            f"--in-queue-unit --job a4 --awaits {readout} --peak-mb 12000 -- run.sh ; ignore_errors=no }}\n"), "")

    assert sim_runner.queued_long_jobs(runner=runner) == []
    readout.write_text("{}")
    assert sim_runner.queued_long_jobs(runner=runner) == ["longjob-a4-queued.service"]
    unreadable = lambda argv, **kw: (runner(argv) if "list-units" in argv  # noqa: E731
                                     else subprocess.CompletedProcess(argv, 1, "", ""))
    assert sim_runner.queued_long_jobs(runner=unreadable) == ["longjob-a4-queued.service"]


def test_a_running_job_marked_waiting_does_not_count_until_its_path_exists(box):
    """land10's shape: already running, 6000 MB declared, its chain keyed on its unit so it cannot
    be stopped and re-armed behind `--awaits`. Marked waiting, its peak does not count and the book
    is admitted; once the path exists it counts again and the book is held."""
    tmp_path, meminfo = box
    records = tmp_path / "records.json"
    entry = llj.launch("land10-like", ["sh", "-c", "sleep 1"], artefact=str(tmp_path / "landed.txt"),
                       workdir=str(tmp_path), log=str(tmp_path / "l.log"), records_path=records,
                       runner=_Runner(), peak_mb=18000, residents=lambda: [],
                       guest_total_mb=24034, expect_minutes=30)
    resident = [{"pid": 77, "rss_mb": 5.0, "unit": f"{entry['unit']}.service", "command": "sh"}]
    assert not _book_admitted(tmp_path, meminfo, residents=resident)["admitted"]
    with pytest.raises(llj.LaunchRefused, match="live launch record"):
        llj.mark_waiting("no-such-job", str(tmp_path / "x"), records_path=records)
    ready = tmp_path / "book-ready"
    llj.mark_waiting("land10-like", str(ready), records_path=records)
    assert _book_admitted(tmp_path, meminfo, residents=resident)["admitted"]
    ready.write_text("")
    assert not _book_admitted(tmp_path, meminfo, residents=resident)["admitted"]
