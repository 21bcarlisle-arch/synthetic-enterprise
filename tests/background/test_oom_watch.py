"""The OOM door -- R15 both-ways proof (2026-08-24).

THE NAMED DEFECT this control exists to fire on: on 2026-08-24 the producer was OOM-killed
thirteen times over four hours, and RUNG 1d's doorbell said "this is not a run failing, it is
runs NOT HAPPENING" and prescribed a restart. Both of its inputs were structurally incapable of
seeing the kill -- the state file needs a Python-level exception to record anything, and
artefact age is equally consistent with dead and with killed-every-time.

So the mutation is not hypothetical and does not need inventing: the journal below is the real
record of that day, and `test_the_named_defect_fires` is the assertion that the control would
have named it. The FAIL side is `test_a_clean_journal_says_nothing` -- a control that reported
an OOM kill on a healthy unit would be worthless in the opposite direction.

The third case is the one R15 cares most about (FAIL-SILENT): an unreadable journal must not be
reported as a clean one. `test_an_unreadable_journal_is_not_a_clean_one` holds that line.
"""

from __future__ import annotations

import pytest

from background import oom_watch
from background.oom_watch import OomKill, producer_oom_clause, read_oom_kills

UNIT = "sim-runner.service"

# VERBATIM from `journalctl --user -u sim-runner.service -o short-iso` on 2026-08-24, the outage
# this control was built during. Kept byte-for-byte: a parser tested only against a record this
# repository wrote is a parser tested against its own assumptions.
REAL_JOURNAL = """\
2026-08-24T12:35:41+01:00 Skynet systemd[289]: sim-runner.service: The kernel OOM killer killed some processes in this unit.
2026-08-24T12:35:42+01:00 Skynet systemd[289]: sim-runner.service: Failed with result 'oom-kill'.
2026-08-24T12:35:42+01:00 Skynet systemd[289]: sim-runner.service: Consumed 29min 14.780s CPU time over 29min 18.728s wall clock time, 10.3G memory peak.
2026-08-24T12:35:47+01:00 Skynet systemd[289]: sim-runner.service: Scheduled restart job, restart counter is at 11.
2026-08-24T13:07:14+01:00 Skynet systemd[289]: sim-runner.service: The kernel OOM killer killed some processes in this unit.
2026-08-24T13:07:14+01:00 Skynet systemd[289]: sim-runner.service: Failed with result 'oom-kill'.
2026-08-24T13:07:14+01:00 Skynet systemd[289]: sim-runner.service: Consumed 30min 54.833s CPU time over 31min 32.309s wall clock time, 10.7G memory peak.
2026-08-24T13:07:19+01:00 Skynet systemd[289]: sim-runner.service: Scheduled restart job, restart counter is at 12.
2026-08-24T13:54:15+01:00 Skynet systemd[289]: sim-runner.service: The kernel OOM killer killed some processes in this unit.
2026-08-24T13:54:15+01:00 Skynet systemd[289]: sim-runner.service: Failed with result 'oom-kill'.
2026-08-24T13:54:15+01:00 Skynet systemd[289]: sim-runner.service: Consumed 41min 24.673s CPU time over 47min 1.190s wall clock time, 13.2G memory peak, 182M memory swap peak.
2026-08-24T13:54:20+01:00 Skynet systemd[289]: sim-runner.service: Scheduled restart job, restart counter is at 13.
"""

# The same unit on a healthy day: it restarts (deploys, reboots) without ever being killed.
CLEAN_JOURNAL = """\
2026-08-23T09:12:01+01:00 Skynet systemd[289]: sim-runner.service: Scheduled restart job, restart counter is at 2.
2026-08-23T11:40:55+01:00 Skynet systemd[289]: sim-runner.service: Consumed 9min 2.100s CPU time over 9min 4.000s wall clock time, 4.1G memory peak.
"""


def _reader(text):
    return lambda unit, since: text


# --------------------------------------------------------------------------- FIRES


def test_the_named_defect_fires():
    """The real 2026-08-24 journal, parsed: three kills, the latest at 13.2G, counter 13."""
    kills = read_oom_kills(unit=UNIT, journal_reader=_reader(REAL_JOURNAL))

    assert kills is not None
    assert [k.at for k in kills] == [
        "2026-08-24T12:35:42+01:00",
        "2026-08-24T13:07:14+01:00",
        "2026-08-24T13:54:15+01:00",
    ]
    assert [k.peak for k in kills] == ["10.3G", "10.7G", "13.2G"]
    assert [k.restart_counter for k in kills] == [11, 12, 13]


def test_the_clause_refuses_the_restart_prescription():
    """The doorbell's wrong repair is contradicted in the clause, not merely left unsaid."""
    clause = producer_oom_clause(unit=UNIT, journal_reader=_reader(REAL_JOURNAL))

    assert clause is not None
    assert "3 OOM kill(s)" in clause
    assert "13.2G" in clause
    assert "restart counter stands at 13" in clause
    # The two claims that make it actionable rather than merely informative.
    assert "NOT a dead producer" in clause
    assert "MEMORY decision" in clause


def test_the_swap_peak_suffix_does_not_displace_the_memory_peak():
    """The 13:54 line carries `13.2G memory peak, 182M memory swap peak` -- two peaks, and the
    one that killed it is the first. A parser taking the last number reports 182M and makes a
    13.2G kill look like a trivial one."""
    kills = read_oom_kills(unit=UNIT, journal_reader=_reader(REAL_JOURNAL))

    assert kills[-1].peak == "13.2G"


# ---------------------------------------------------------------------------- FAILS


def test_a_clean_journal_says_nothing():
    """The FAIL side: no kills, so no clause. A control that cannot be silent is not a control."""
    assert read_oom_kills(unit=UNIT, journal_reader=_reader(CLEAN_JOURNAL)) == []
    assert producer_oom_clause(unit=UNIT, journal_reader=_reader(CLEAN_JOURNAL)) is None


def test_another_units_kill_is_not_counted_as_this_ones():
    """Anti-tautology: the unit name is required on each line, so a reader handed a wider
    journal cannot attribute the publisher's kill to the producer."""
    other = REAL_JOURNAL.replace("sim-runner.service", "publish-gate.service")

    assert read_oom_kills(unit=UNIT, journal_reader=_reader(other)) == []


def test_a_peak_with_no_kill_ahead_of_it_is_not_attributed():
    """CLEAN_JOURNAL's `Consumed ... 4.1G memory peak` is an ordinary exit line. Attributing it
    would manufacture a kill out of a healthy run's bookkeeping."""
    kills = read_oom_kills(unit=UNIT, journal_reader=_reader(CLEAN_JOURNAL))

    assert kills == []


# ------------------------------------------------------- FAIL-SILENT IS A FAILED CHECK


@pytest.mark.parametrize(
    "broken_reader",
    [
        pytest.param(lambda unit, since: None, id="journal_declined"),
        pytest.param(
            lambda unit, since: (_ for _ in ()).throw(OSError("no journalctl")),
            id="reader_raised",
        ),
    ],
)
def test_an_unreadable_journal_is_not_a_clean_one(broken_reader):
    """R15's third killer pattern. None, never [] -- and the clause SAYS so, because the whole
    failure being repaired here is a doorbell asserting what it had not established."""
    assert read_oom_kills(unit=UNIT, journal_reader=broken_reader) is None

    clause = producer_oom_clause(unit=UNIT, journal_reader=broken_reader)
    assert clause is not None
    assert "COULD NOT BE READ" in clause
    assert "UNKNOWN" in clause


def test_journalctl_absent_is_unreadable_not_clean(monkeypatch):
    """The same line held at the real reader: no binary on the box is not evidence of health."""
    monkeypatch.setattr(oom_watch.shutil, "which", lambda name: None)

    assert read_oom_kills(unit=UNIT) is None


def test_no_entries_matched_is_a_clean_answer_not_a_failure(monkeypatch):
    """journalctl exits 1 when `--grep` matches nothing. That is the healthy case and must not
    be read as an unreadable journal, or a healthy producer would page as unknown forever."""

    class _Result:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(oom_watch.shutil, "which", lambda name: "/usr/bin/journalctl")
    monkeypatch.setattr(oom_watch.subprocess, "run", lambda *a, **k: _Result())

    assert read_oom_kills(unit=UNIT) == []


# ------------------------------------------------------------- THE DETECTOR IT SERVES


def test_rung_1d_carries_the_clause_and_drops_the_false_assertion(tmp_path):
    """The consumer end (R11-in-spirit: assert the rendered message, not just the helper).

    A silent producer with a readable OOM record must no longer tell the reader the runs are
    not happening -- that is the exact sentence that was wrong for four hours.
    """
    from background import supervisor

    reports = tmp_path / "reports"
    reports.mkdir()
    stale = reports / "run_output_probe.json"
    stale.write_text("{}")
    import os

    old = 1_000_000.0
    os.utime(stale, (old, old))

    state = tmp_path / ".sim_producer_state.json"
    state.write_text('{"last_result": "failed"}')

    draw = supervisor._producer_starved_active(
        now=old + supervisor.PRODUCER_ARTEFACT_STALE_SECONDS + 3600,
        state_path=state,
        reports_dir=reports,
        hold_flag=tmp_path / "absent_hold",
        oom_clause_fn=lambda: producer_oom_clause(
            unit=UNIT, journal_reader=_reader(REAL_JOURNAL)
        ),
    )

    assert draw and "PRODUCER SILENT" in draw
    assert "THE RUNS ARE HAPPENING AND THE KERNEL IS KILLING THEM" in draw
    assert "runs NOT HAPPENING" not in draw


def test_rung_1d_is_unharmed_when_the_door_is_clean(tmp_path):
    """The FAIL side at the consumer end: a clean journal leaves the existing doorbell intact,
    so this control cannot quietly rewrite a message it has no evidence about."""
    from background import supervisor

    reports = tmp_path / "reports"
    reports.mkdir()
    stale = reports / "run_output_probe.json"
    stale.write_text("{}")
    import os

    old = 1_000_000.0
    os.utime(stale, (old, old))

    state = tmp_path / ".sim_producer_state.json"
    state.write_text('{"last_result": "failed"}')

    draw = supervisor._producer_starved_active(
        now=old + supervisor.PRODUCER_ARTEFACT_STALE_SECONDS + 3600,
        state_path=state,
        reports_dir=reports,
        hold_flag=tmp_path / "absent_hold",
        oom_clause_fn=lambda: producer_oom_clause(
            unit=UNIT, journal_reader=_reader(CLEAN_JOURNAL)
        ),
    )

    assert draw and "PRODUCER SILENT" in draw
    assert "KERNEL IS KILLING THEM" not in draw


def test_a_raising_clause_never_reaches_the_draw_ladder(tmp_path):
    """FAIL-SAFE: the rung's contract is that it never raises into the draw. A journal read is
    new I/O on that path, so the guard is asserted, not assumed."""
    from background import supervisor

    reports = tmp_path / "reports"
    reports.mkdir()
    stale = reports / "run_output_probe.json"
    stale.write_text("{}")
    import os

    old = 1_000_000.0
    os.utime(stale, (old, old))

    def _explode():
        raise RuntimeError("journal exploded")

    draw = supervisor._producer_starved_active(
        now=old + supervisor.PRODUCER_ARTEFACT_STALE_SECONDS + 3600,
        state_path=tmp_path / "absent_state.json",
        reports_dir=reports,
        hold_flag=tmp_path / "absent_hold",
        oom_clause_fn=_explode,
    )

    assert draw and "PRODUCER SILENT" in draw


# --------------------------------------------------------------------- THE PEAK READING
#
# `read_unit_memory_peaks_mb` answers a different question to `read_oom_kills` and is proven
# separately. The defect it exists to prevent is a SIZING one: on 2026-08-24 the governor's
# declared weight for this unit's job was 6,144 MB while the unit was peaking at 13.5 G, so
# `admit()` was sizing it at less than half its real footprint. The weight had been measured
# once, on 2026-08-10, and nothing ever contradicted it.


def test_peaks_are_read_from_runs_that_survived_not_only_from_corpses():
    """MUTATION KILLED: reusing `read_oom_kills` and taking `.peak` off each kill.

    That mutation looks equivalent and is not. It can only see runs that DIED, so it biases
    the estimate low by exactly the runs that fitted -- and the number needed for sizing is
    what the job takes when it SURVIVES. CLEAN_JOURNAL has a 4.1G peak and no kill at all:
    the kill-based reading returns nothing here, this one returns the peak.
    """
    from background.oom_watch import read_unit_memory_peaks_mb

    assert read_oom_kills(unit=UNIT, journal_reader=_reader(CLEAN_JOURNAL)) == []

    peaks = read_unit_memory_peaks_mb(unit=UNIT, journal_reader=_reader(CLEAN_JOURNAL))
    assert peaks == [pytest.approx(4.1 * 1024)]


def test_every_peak_in_the_window_is_returned_newest_last():
    """The real record: three kills, three peaks, in journal order."""
    from background.oom_watch import read_unit_memory_peaks_mb

    peaks = read_unit_memory_peaks_mb(unit=UNIT, journal_reader=_reader(REAL_JOURNAL))
    assert peaks == [
        pytest.approx(10.3 * 1024),
        pytest.approx(10.7 * 1024),
        pytest.approx(13.2 * 1024),
    ]
    assert max(peaks) == pytest.approx(13.2 * 1024)


def test_the_swap_peak_is_not_read_as_a_memory_peak():
    """MUTATION KILLED: a looser regex that takes the last size on the line.

    The 13.2G line ends `, 182M memory swap peak` -- a mutation that grabbed the trailing
    size would report this unit as peaking at 182 MB and every drift check would read clean.
    """
    from background.oom_watch import read_unit_memory_peaks_mb

    peaks = read_unit_memory_peaks_mb(unit=UNIT, journal_reader=_reader(REAL_JOURNAL))
    assert all(p > 1024 for p in peaks)


def test_another_units_peak_is_not_counted_as_this_ones():
    """The unit name is required in the line, so a wider journal cannot cross-contaminate."""
    from background.oom_watch import read_unit_memory_peaks_mb

    foreign = (
        "2026-08-24T10:00:00+01:00 Skynet systemd[289]: other.service: Consumed 1min 0.000s "
        "CPU time over 1min 0.000s wall clock time, 22.0G memory peak.\n"
    )
    assert read_unit_memory_peaks_mb(unit=UNIT, journal_reader=_reader(foreign)) == []


@pytest.mark.parametrize(
    "broken_reader",
    [
        pytest.param(lambda unit, since: None, id="journal_declined"),
        pytest.param(
            lambda unit, since: (_ for _ in ()).throw(OSError("no journalctl")),
            id="reader_raised",
        ),
    ],
)
def test_an_unreadable_journal_gives_none_not_an_empty_peak_list(broken_reader):
    """R15 FAIL-SILENT. [] means 'answered, no peak recorded'; None means nobody knows.

    MUTATION KILLED: `return peaks` initialised outside the guard, so an unreadable journal
    returns []. A caller doing `max(peaks or [0])` would then size every job at zero and
    admit all of them -- fail-open, from a check that never ran.
    """
    from background.oom_watch import read_unit_memory_peaks_mb

    assert read_unit_memory_peaks_mb(unit=UNIT, journal_reader=broken_reader) is None


@pytest.mark.parametrize(
    "text,expected_mb",
    [
        ("13.5G", 13824.0),
        ("854M", 854.0),
        ("1T", 1024.0 * 1024.0),
        ("256K", 0.25),
    ],
)
def test_iec_suffixes_convert_to_mb(text, expected_mb):
    from background.oom_watch import parse_memory_size_mb

    assert parse_memory_size_mb(text) == pytest.approx(expected_mb)


@pytest.mark.parametrize("junk", ["", "   ", "nope", "12X", None])
def test_an_unparseable_size_is_none_never_zero(junk):
    """MUTATION KILLED: `except ValueError: return 0.0`.

    Zero is a REAL peak, so collapsing a parse failure onto it makes every comparison against
    a declared weight read clean. The unparseable case must be droppable, not falsely small.
    """
    from background.oom_watch import parse_memory_size_mb

    assert parse_memory_size_mb(junk) is None


# ------------------------------------------------------------------- THE LIVE PEAK
#
# The journal writes a peak when a unit STOPS. sim-runner is a long-lived loop doing run
# after run inside one unit lifetime, so a journal-only reading is POST-MORTEM -- it reports
# the previous lifetime and is blind to growth inside the current one. Measured 2026-08-24:
# journal 13,824 MB against MemoryPeak 22,703 MB on the running unit, same moment.


class _Ran:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def test_the_live_peak_is_read_in_mb():
    from background.oom_watch import read_unit_memory_peak_live_mb

    # The real value observed on 2026-08-24, in bytes.
    got = read_unit_memory_peak_live_mb(unit=UNIT, runner=lambda argv: _Ran("23805833216\n"))
    assert got == pytest.approx(22703.0, abs=1.0)


def test_the_live_peak_asks_the_running_unit_not_the_journal():
    """MUTATION KILLED: querying MemoryCurrent, which is what the unit holds RIGHT NOW.

    Current is not peak: sampled between runs it reads near zero, and a weight check against
    it would call every job tiny. The property name is part of the contract.
    """
    from background.oom_watch import read_unit_memory_peak_live_mb

    seen = {}

    def _runner(argv):
        seen["argv"] = argv
        return _Ran("1048576")

    read_unit_memory_peak_live_mb(unit=UNIT, runner=_runner)
    assert "MemoryPeak" in seen["argv"]
    assert "MemoryCurrent" not in seen["argv"]
    assert UNIT in seen["argv"]


@pytest.mark.parametrize(
    "stdout,rc",
    [
        pytest.param("[not set]", 0, id="never_ran"),
        pytest.param("", 0, id="unknown_property"),
        pytest.param("   ", 0, id="blank"),
        pytest.param("infinity", 0, id="non_numeric"),
        pytest.param("23805833216", 1, id="systemctl_refused"),
    ],
)
def test_an_unreadable_live_peak_is_none_never_zero(stdout, rc):
    """R15 FAIL-OPEN. 0.0 would read as a tiny job and clear every drift check.

    `[not set]` is systemd's own answer for a unit that has never run, and it is the case a
    naive int() cast turns into an exception or a zero.
    """
    from background.oom_watch import read_unit_memory_peak_live_mb

    assert read_unit_memory_peak_live_mb(
        unit=UNIT, runner=lambda argv: _Ran(stdout, rc)
    ) is None


def test_a_runner_that_raises_is_unreadable_not_clean():
    from background.oom_watch import read_unit_memory_peak_live_mb

    def _boom(argv):
        raise OSError("no systemctl")

    assert read_unit_memory_peak_live_mb(unit=UNIT, runner=_boom) is None


def test_systemctl_absent_is_unreadable_not_clean(monkeypatch):
    from background.oom_watch import read_unit_memory_peak_live_mb

    monkeypatch.setattr(oom_watch.shutil, "which", lambda name: None)
    assert read_unit_memory_peak_live_mb(unit=UNIT) is None
