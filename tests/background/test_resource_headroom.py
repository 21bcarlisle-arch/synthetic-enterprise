"""R15 for the resource-headroom governor: every guard here kills a named mutation.

The governor's whole risk is FAIL-OPEN -- admitting a 6 GB job into a machine that has
1 GB left, which is precisely the shape that produced 64 lifetime oom-kills. So the tests
are written as mutations first: for each guard, the mutation that would delete it is named
in the test's own docstring, and the assertion is chosen so that mutation turns the test red.
"""
from __future__ import annotations

import json
import os

import pytest

from background import resource_headroom as rh

# --------------------------------------------------------------------------------------
# Fixtures: synthetic /proc surfaces, so a machine state can be CONSTRUCTED rather than
# waited for. The real /proc is exercised separately by test_the_real_proc_is_readable.
# --------------------------------------------------------------------------------------

def _meminfo(tmp_path, total_mb=16000, available_mb=8000, shmem_mb=1800, swap_free_mb=2000,
             name="meminfo"):
    p = tmp_path / name
    p.write_text(
        f"MemTotal:       {int(total_mb * 1024)} kB\n"
        f"MemFree:         {int(500 * 1024)} kB\n"
        f"MemAvailable:   {int(available_mb * 1024)} kB\n"
        f"Shmem:          {int(shmem_mb * 1024)} kB\n"
        f"SwapTotal:      {int(4096 * 1024)} kB\n"
        f"SwapFree:       {int(swap_free_mb * 1024)} kB\n",
        encoding="utf-8",
    )
    return p


def _vmstat(tmp_path, oom_kills=64, name="vmstat"):
    p = tmp_path / name
    p.write_text(f"pgmajfault 36910245\noom_kill {oom_kills}\n", encoding="utf-8")
    return p


def _psi(tmp_path, some=0.0, name="psi"):
    p = tmp_path / name
    p.write_text(
        f"some avg10=0.00 avg60={some:.2f} avg300=0.00 total=1337601743\n"
        f"full avg10=0.00 avg60=0.00 avg300=0.00 total=1309797657\n",
        encoding="utf-8",
    )
    return p


def _fake_proc(tmp_path, pid, starttime="12345"):
    """A /proc root where `pid` exists with a given starttime, comm containing ') (' on
    purpose -- a naive `raw.split()[21]` parse breaks on it."""
    d = tmp_path / "proc" / str(pid)
    d.mkdir(parents=True, exist_ok=True)
    # Fields AFTER comm, in real /proc/<pid>/stat order: index 0 is `state` (field 3), so
    # starttime (field 22) sits at index 19. Laid out explicitly so the fixture cannot drift
    # from the parser and quietly agree with a broken one.
    fields = ["0"] * 30
    fields[0] = "R"
    fields[19] = starttime
    # The comm deliberately contains an INNER ')' as well as spaces: `py) test (x`. A comm
    # with only a trailing ')' cannot discriminate `find` from `rfind` -- the first version
    # of this fixture had exactly that hole and a `find(")")` mutation survived it. The
    # kernel truncates comm to 15 chars but does NOT escape ')', so this is a real shape.
    (d / "stat").write_text(
        f"{pid} (py) test (x) " + " ".join(fields) + "\n",
        encoding="utf-8",
    )
    return tmp_path / "proc"


def _sample_kwargs(tmp_path, **kw):
    return {
        "meminfo_path": _meminfo(tmp_path, **kw),
        "vmstat_path": _vmstat(tmp_path),
        "psi_path": _psi(tmp_path),
    }


def _hold(path, pid, weight_mb, starttime="12345", job_class="sim_run"):
    rows = json.loads(path.read_text()) if path.exists() else []
    rows.append({"pid": pid, "starttime": starttime, "job_class": job_class,
                 "weight_mb": weight_mb, "since": "2026-08-10T00:00:00+00:00"})
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


# --------------------------------------------------------------------------------------
# THE INDEPENDENCE PAIR. Together these prove admission consults TWO sources, and neither
# alone is sufficient -- the tautology guard (R15 killer pattern 1).
# --------------------------------------------------------------------------------------

def test_denies_when_the_budget_is_exhausted_though_memory_looks_free(tmp_path):
    """MUTATION KILLED: dropping the declared-budget condition and admitting on measured
    memory alone. Memory looks free here (16 GB available) precisely BECAUSE the 9.7 GB
    subject-cost job that declared has not allocated its peak yet -- the collision that has
    not happened YET. This is the real pairing: subject_cost (oom-killed at 9,648 MB) against
    a sim_run (peaked at 13.5 G on 2026-08-24), which together cannot fit the 24 GB guest
    however free it looks now.

    RE-SIZED 2026-08-24 with the sim_run weight. The scenario was written at total=16000 /
    available=8000, where the measured condition ALSO denied once sim_run was re-derived from
    6,144 MB to 13,824 MB -- which would have quietly destroyed the independence this test
    exists to prove while leaving it green on the first two assertions. The numbers here are
    chosen so the measured condition still ADMITS and only the budget refuses; the mutation
    killed is unchanged.
    """
    res = tmp_path / "reservations.json"
    _hold(res, pid=4242, weight_mb=9728, job_class="subject_cost")
    proc = _fake_proc(tmp_path, 4242)

    d = rh.admit("sim_run", reservations_path=res, proc_root=proc,
                 **_sample_kwargs(tmp_path, total_mb=24000, available_mb=16000))

    assert d["admitted"] is False
    assert "budget exhausted" in d["reason"]
    assert d["committed_mb"] == pytest.approx(9728)
    # The measured condition would have ADMITTED this (16000 - 13824 > 1024): the denial can
    # only have come from the declared budget, which is what makes the pair independent.
    assert d["available_mb"] - d["weight_mb"] > rh.RESERVE_FOR_UNDECLARED_MB


def test_denies_when_memory_is_tight_though_the_ledger_is_empty(tmp_path):
    """MUTATION KILLED: dropping the measured-memory condition and admitting on the ledger
    alone. The ledger is EMPTY here -- everything eating the machine (a human's pytest, the
    agent seat, a leaked child) never declared, which is the ledger's permanent blind spot."""
    res = tmp_path / "reservations.json"
    res.write_text("[]", encoding="utf-8")

    d = rh.admit("sim_run", reservations_path=res, proc_root=tmp_path / "proc",
                 **_sample_kwargs(tmp_path, total_mb=16000, available_mb=1200))

    assert d["admitted"] is False
    assert "measured memory too tight" in d["reason"]
    assert d["committed_mb"] == 0


def test_admits_only_when_both_conditions_hold(tmp_path):
    """The positive control: without this, a mutation making admit() return False always
    would pass every other test in this file (`feedback_control_that_can_only_fail_wedges`)."""
    res = tmp_path / "reservations.json"
    res.write_text("[]", encoding="utf-8")

    d = rh.admit("publish_gate", reservations_path=res, proc_root=tmp_path / "proc",
                 **_sample_kwargs(tmp_path, total_mb=16000, available_mb=8000))

    assert d["admitted"] is True, d["reason"]


# --------------------------------------------------------------------------------------
# FAIL-CLOSED (R15 killer patterns 2 and 3).
# --------------------------------------------------------------------------------------

def test_unreadable_meminfo_defers_rather_than_assuming_room(tmp_path):
    """MUTATION KILLED: treating a missing measurement as 'no constraint observed'. An
    unavailable check is a FAILED check -- the classic fail-open on missing/empty input."""
    res = tmp_path / "reservations.json"
    res.write_text("[]", encoding="utf-8")

    d = rh.admit("sim_run", reservations_path=res, proc_root=tmp_path / "proc",
                 meminfo_path=tmp_path / "does_not_exist",
                 vmstat_path=_vmstat(tmp_path), psi_path=_psi(tmp_path))

    assert d["admitted"] is False
    assert "unmeasurable" in d["reason"]
    assert d["available_mb"] is None  # absent, never 0 and never a default


def test_malformed_meminfo_defers(tmp_path):
    """A parseable-but-garbage /proc/meminfo must not resolve to a green either."""
    bad = tmp_path / "bad_meminfo"
    bad.write_text("MemTotal: not-a-number kB\nMemAvailable: \n", encoding="utf-8")
    res = tmp_path / "reservations.json"
    res.write_text("[]", encoding="utf-8")

    d = rh.admit("sim_run", reservations_path=res, proc_root=tmp_path / "proc",
                 meminfo_path=bad, vmstat_path=_vmstat(tmp_path), psi_path=_psi(tmp_path))

    assert d["admitted"] is False
    assert "unmeasurable" in d["reason"]


def test_an_undeclared_job_class_is_denied_not_treated_as_weightless(tmp_path):
    """MUTATION KILLED: `weight = CLASS_WEIGHTS_MB.get(job_class, 0)`. A default of zero
    makes every unknown job free, so the budget silently stops binding -- exactly how the
    32 GB constant became fiction."""
    res = tmp_path / "reservations.json"
    res.write_text("[]", encoding="utf-8")

    d = rh.admit("some_new_tool", reservations_path=res, proc_root=tmp_path / "proc",
                 **_sample_kwargs(tmp_path))

    assert d["admitted"] is False
    assert "undeclared weight" in d["reason"]
    assert d["weight_mb"] is None


# --------------------------------------------------------------------------------------
# RESERVATION LIFETIME -- the wedge guard and the PID-reuse guard.
# --------------------------------------------------------------------------------------

def test_a_dead_holders_reservation_is_reaped_not_honoured_forever(tmp_path):
    """MUTATION KILLED: summing all rows in the ledger regardless of liveness. A hard-killed
    holder never runs a finally block, so an unreaped ledger wedges the machine permanently
    at the first oom-kill -- the control that can only refuse."""
    res = tmp_path / "reservations.json"
    _hold(res, pid=999999, weight_mb=9728)  # pid absent from the fake /proc entirely
    proc = _fake_proc(tmp_path, 4242)

    assert rh.committed_mb(res, proc) == 0
    d = rh.admit("publish_gate", reservations_path=res, proc_root=proc,
                 **_sample_kwargs(tmp_path, available_mb=8000))
    assert d["admitted"] is True, d["reason"]


def test_pid_reuse_does_not_resurrect_a_dead_reservation(tmp_path):
    """MUTATION KILLED: liveness by `Path('/proc/<pid>').exists()` alone. The PID is alive
    here but it is a DIFFERENT process (starttime differs), so honouring the old claim would
    reserve 9.7 GB against a stranger."""
    res = tmp_path / "reservations.json"
    _hold(res, pid=4242, weight_mb=9728, starttime="11111")
    proc = _fake_proc(tmp_path, 4242, starttime="99999")  # recycled PID

    assert rh.committed_mb(res, proc) == 0


def test_liveness_survives_a_comm_containing_spaces_and_parens(tmp_path):
    """MUTATION KILLED: `raw.split()[21]`. pytest workers carry parenthesised names; a
    mis-parsed starttime makes every check answer 'different process' and silently disables
    the whole budget by reaping every live holder."""
    res = tmp_path / "reservations.json"
    _hold(res, pid=4242, weight_mb=6144, starttime="12345")
    proc = _fake_proc(tmp_path, 4242, starttime="12345")  # comm is "py test (x)"

    assert rh.committed_mb(res, proc) == pytest.approx(6144)


def test_reservation_context_manager_releases_on_exception(tmp_path):
    res = tmp_path / "reservations.json"
    proc_root = None  # use the real /proc: this process is genuinely live

    with pytest.raises(RuntimeError):
        with rh.reservation("publish_gate", reservations_path=res, proc_root=proc_root):
            assert rh.committed_mb(res, proc_root) == pytest.approx(1536)
            raise RuntimeError("boom")

    assert rh.committed_mb(res, proc_root) == 0


# --------------------------------------------------------------------------------------
# EPISODE MEMORY and R5 transitions.
# --------------------------------------------------------------------------------------

def test_episode_records_since_worst_and_victims(tmp_path):
    """The flag's requirement (1) verbatim: since-when, worst, victims. A level-only report
    would pass a weaker assertion; each of the three is asserted separately."""
    ep = tmp_path / "episode.json"

    first = rh.observe(episode_path=ep, **_sample_kwargs(tmp_path, available_mb=1000))
    assert first["transition"] == "entered"
    assert first["episode"]["worst_available_mb"] == pytest.approx(1000)

    # Deeper, and two processes died inside the window.
    worse = rh.observe(
        episode_path=ep,
        meminfo_path=_meminfo(tmp_path, available_mb=400, name="meminfo2"),
        vmstat_path=_vmstat(tmp_path, oom_kills=66, name="vmstat2"),
        psi_path=_psi(tmp_path, some=41.0, name="psi2"),
    )
    assert worse["transition"] is None
    assert worse["episode"]["worst_available_mb"] == pytest.approx(400)
    assert worse["episode"]["since"] == first["episode"]["since"], "episode start must persist"
    assert worse["episode"]["victims"] == 2

    # A shallower sample must NOT erase the worst -- that is the whole point of the memory.
    back = rh.observe(episode_path=ep,
                      meminfo_path=_meminfo(tmp_path, available_mb=1200, name="meminfo3"),
                      vmstat_path=_vmstat(tmp_path, oom_kills=66, name="vmstat3"),
                      psi_path=_psi(tmp_path, name="psi3"))
    assert back["episode"]["worst_available_mb"] == pytest.approx(400)


def test_victims_unknown_is_none_not_zero(tmp_path):
    """MUTATION KILLED: `victims = kills_now - opened or 0`. 'Nobody died' and 'the counter
    was unreadable' are different facts and must not render identically."""
    ep = tmp_path / "episode.json"
    r = rh.observe(episode_path=ep,
                   meminfo_path=_meminfo(tmp_path, available_mb=1000),
                   vmstat_path=tmp_path / "no_vmstat",
                   psi_path=_psi(tmp_path))
    assert r["episode"]["victims"] is None


def test_alarm_fires_on_transition_only(tmp_path):
    """R5: a repeating alarm is an ignored alarm."""
    ep = tmp_path / "episode.json"

    entered = rh.observe(episode_path=ep, **_sample_kwargs(tmp_path, available_mb=1000))
    assert rh.alarm_line(entered) is not None
    assert "MEMORY PRESSURE" in rh.alarm_line(entered)

    still = rh.observe(episode_path=ep,
                       meminfo_path=_meminfo(tmp_path, available_mb=900, name="m2"),
                       vmstat_path=_vmstat(tmp_path, name="v2"), psi_path=_psi(tmp_path, name="p2"))
    assert rh.alarm_line(still) is None, "unchanged status must not re-announce"

    recovered = rh.observe(episode_path=ep,
                           meminfo_path=_meminfo(tmp_path, available_mb=9000, name="m3"),
                           vmstat_path=_vmstat(tmp_path, name="v3"),
                           psi_path=_psi(tmp_path, name="p3"))
    assert recovered["transition"] == "recovered"
    line = rh.alarm_line(recovered)
    assert "MEMORY RECOVERED" in line and "worst" in line


def test_hysteresis_holds_the_band_inside_the_gap():
    """Without the gap a machine sitting on the threshold pages on every sample."""
    mid = (rh.PRESSURE_FLOOR_MB + rh.RECOVERED_FLOOR_MB) / 2
    assert rh.band(mid, "pressure") == "pressure"
    assert rh.band(mid, "ok") == "ok"
    assert rh.band(rh.PRESSURE_FLOOR_MB - 1, "ok") == "pressure"
    assert rh.band(rh.RECOVERED_FLOOR_MB + 1, "pressure") == "ok"
    assert rh.band(None) == "unknown"


def test_note_line_is_red_when_unmeasured(tmp_path):
    """R15 killer pattern 3: an absent measurement renders RED, never a fabricated green."""
    assert "RED" in rh.note_line(episode_path=tmp_path / "absent.json")


# --------------------------------------------------------------------------------------
# THE FALSIFIABLE EXIT, quoted from the flag: "a synthetic contention window produces a
# deferral and an alarm, never an oom-kill."
# --------------------------------------------------------------------------------------

def test_a_synthetic_contention_window_produces_a_deferral_and_an_alarm(tmp_path):
    """The flag's exit criterion, end to end and in its own terms.

    Reconstructs the measured 2026-08-10 window: a sim run holding 6 GB while the machine
    has ~1.2 GB left, and a publish gate arriving. The kernel's answer was to kill the
    largest innocent. The governor's answer must be a DEFERRAL with a RECEIPT.
    """
    res = tmp_path / "reservations.json"
    ep = tmp_path / "episode.json"
    log = tmp_path / "deferrals.jsonl"
    _hold(res, pid=4242, weight_mb=6144, job_class="sim_run")
    proc = _fake_proc(tmp_path, 4242)
    kwargs = _sample_kwargs(tmp_path, total_mb=16000, available_mb=1200)

    decision = rh.admit("publish_gate", reservations_path=res, proc_root=proc, **kwargs)
    assert decision["admitted"] is False, "the gate must defer, not collide"

    rh.record_deferral(decision, log_path=log)
    receipt = json.loads(log.read_text().strip())
    assert receipt["job_class"] == "publish_gate"
    assert receipt["admitted"] is False
    assert receipt["reason"], "a deferral without a diagnosable reason is just a stall"
    assert receipt["committed_mb"] == pytest.approx(6144)
    assert receipt["available_mb"] == pytest.approx(1200)

    watch = rh.observe(episode_path=ep, **kwargs)
    assert watch["transition"] == "entered"
    assert "MEMORY PRESSURE" in rh.alarm_line(watch)


# --------------------------------------------------------------------------------------
# The instrument must work on THIS machine, not only on fixtures.
# --------------------------------------------------------------------------------------

@pytest.mark.skipif(not rh.MEMINFO.exists(), reason="non-Linux: /proc/meminfo absent")
def test_the_real_proc_is_readable_and_the_numbers_are_sane():
    """A governor that only works against fixtures governs nothing (the tautology shape:
    the test would pass on a box where every read fails)."""
    obs = rh.sample()
    assert obs["total_mb"] and obs["total_mb"] > 1000
    assert obs["available_mb"] is not None and 0 < obs["available_mb"] <= obs["total_mb"]
    assert obs["oom_kills_total"] is not None and obs["oom_kills_total"] >= 0
    # This box: 15.9 GB real, NOT the 32 GB the estimating code believed.
    assert obs["total_mb"] < 32000


@pytest.mark.skipif(not rh.MEMINFO.exists(), reason="non-Linux: /proc absent")
def test_this_live_process_reads_as_live():
    """The liveness primitive against a process known to exist -- if this ever fails, every
    reservation is reaped instantly and the budget silently stops binding."""
    assert rh._proc_starttime(os.getpid()) is not None
    assert rh._is_live({"pid": os.getpid(), "starttime": rh._proc_starttime(os.getpid())})


# --------------------------------------------------------------------------------------
# WEIGHT DRIFT -- a declared weight is a MEASUREMENT WITH A DATE ON IT (2026-08-24).
#
# THE NAMED DEFECT: `CLASS_WEIGHTS_MB["sim_run"]` said 6,144 MB, sourced to an RSS sample
# taken on 2026-08-10. Fourteen days later the job it names was OOM-killed fourteen times in
# one day at peaks up to 13.5 G. The weight was never wrong when written and was never
# re-checked, so `admit()` was sizing the largest job on the box at 2.2x under its real
# footprint -- fail-open, in the one direction this governor exists to prevent.
#
# These tests are the mechanism that stops that recurring, so they are written to fire on the
# OLD CONSTANT against the REAL journal of the day it failed.
# --------------------------------------------------------------------------------------

# Peaks as systemd recorded them for sim-runner.service on 2026-08-24, in MB.
_REAL_PEAKS_MB = [10.3 * 1024, 10.7 * 1024, 13.2 * 1024, 13.5 * 1024]


def _peaks(values):
    return lambda unit, since: list(values)


def test_the_named_defect_fires_on_the_pre_fix_constant(monkeypatch):
    """THE test. The 2026-08-24 record against the weight that was live that morning."""
    monkeypatch.setitem(rh.CLASS_WEIGHTS_MB, "sim_run", 6144)

    verdict = rh.weight_drift("sim_run", peaks_reader=_peaks(_REAL_PEAKS_MB))

    assert verdict["drifted"] is True
    assert verdict["observed_peak_mb"] == pytest.approx(13824.0)
    assert "2.2x under its measured footprint" in verdict["detail"]

    alarm = rh.weight_drift_alarm([verdict])
    assert "DECLARED JOB WEIGHT OUTGROWN" in alarm
    assert "fail-open" in alarm


def test_the_re_derived_constant_covers_the_record_it_was_derived_from():
    """ANTI-REGRESSION, and the reason this is not just a one-off edit.

    The repair for the above was to re-derive the constant from systemd's record. This holds
    that repair: whatever `sim_run` says today must still cover the peak that killed it. A
    future edit that lowers it back under 13.5 G turns this red.
    """
    verdict = rh.weight_drift("sim_run", peaks_reader=_peaks(_REAL_PEAKS_MB))

    assert verdict["drifted"] is False, verdict["detail"]
    assert rh.weight_drift_alarm([verdict]) is None


def test_a_weight_that_still_covers_the_record_is_not_flagged():
    """The FAIL side: a control that flagged a healthy weight would be worthless."""
    verdict = rh.weight_drift("sim_run", peaks_reader=_peaks([2048.0, 3072.0]))

    assert verdict["drifted"] is False
    assert "still covers" in verdict["detail"]


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(lambda unit, since: None, id="journal_unreadable"),
        pytest.param(lambda unit, since: [], id="journal_empty"),
    ],
)
def test_an_unchecked_weight_is_not_a_clean_one(reader):
    """R15 killer pattern 3, and the whole failure mode restated.

    MUTATION KILLED: `verdict["drifted"] = bool(peaks and max(peaks) > declared)`, which
    renders both of these as False -- i.e. as "this weight is fine". The state being
    repaired IS a weight nobody has checked lately, so "we could not check" must never
    render as the clean answer. It is None, and the alarm says so out loud.
    """
    verdict = rh.weight_drift("sim_run", peaks_reader=reader)

    assert verdict["drifted"] is None
    assert verdict["observed_peak_mb"] is None

    alarm = rh.weight_drift_alarm([verdict])
    assert alarm is not None, "an unverified weight must not pass silently"
    assert "UNVERIFIED" in alarm


def test_a_class_with_no_unit_is_unverified_rather_than_silently_clean():
    """`subject_cost` is started ad hoc and leaves no journal, so it CANNOT be re-derived.

    That is a real limit and it is reported as one. A control that returned False here would
    be claiming to have checked three weights while only ever checking one.
    """
    verdict = rh.weight_drift("subject_cost")

    assert verdict["drifted"] is None
    assert "no independent record" in verdict["detail"] or "hand-measured" in verdict["detail"]


def test_an_undeclared_class_has_nothing_to_check():
    verdict = rh.weight_drift("no_such_class")

    assert verdict["drifted"] is None
    assert verdict["declared_mb"] is None


def test_observe_surfaces_drift_and_only_on_transition(tmp_path, monkeypatch):
    """R5, held on the new reading exactly as on the pressure band.

    A drifted weight is a STANDING condition -- it persists until a human edits the table --
    so an alarm every cycle would be the repeating-status noise R5 exists to stop. The set of
    flagged classes is remembered in the episode; only a CHANGE speaks.
    """
    monkeypatch.setitem(rh.CLASS_WEIGHTS_MB, "sim_run", 6144)
    ep = tmp_path / "episode.json"
    drift = {"peaks_reader": _peaks(_REAL_PEAKS_MB)}

    first = rh.observe(episode_path=ep, drift_kwargs=drift,
                       **_sample_kwargs(tmp_path, available_mb=9000))
    assert "DECLARED JOB WEIGHT OUTGROWN" in first["shadow_alarm"]

    again = rh.observe(episode_path=ep, drift_kwargs=drift,
                       meminfo_path=_meminfo(tmp_path, available_mb=9000, name="m2"),
                       vmstat_path=_vmstat(tmp_path, name="v2"),
                       psi_path=_psi(tmp_path, name="p2"))
    assert again.get("shadow_alarm") is None, "unchanged drift must not re-announce (R5)"

    # And it speaks again when the condition CLEARS, so a repair is visible.
    rh.CLASS_WEIGHTS_MB["sim_run"] = 13824
    repaired = rh.observe(episode_path=ep, drift_kwargs=drift,
                          meminfo_path=_meminfo(tmp_path, available_mb=9000, name="m3"),
                          vmstat_path=_vmstat(tmp_path, name="v3"),
                          psi_path=_psi(tmp_path, name="p3"))
    assert repaired["episode"]["weight_drift_flagged"] == []


def test_a_drift_check_that_raises_never_takes_the_observer_down(tmp_path):
    """A governor that can crash the worker is a worse outage than the one it prevents.

    The pressure sample must still be returned, and the failure must be SAID rather than
    swallowed into a green.
    """
    def _boom(unit, since):
        raise RuntimeError("journal exploded")

    result = rh.observe(episode_path=tmp_path / "ep.json",
                        drift_kwargs={"peaks_reader": _boom},
                        **_sample_kwargs(tmp_path, available_mb=9000))

    assert result["sample"]["available_mb"] == 9000
    assert "failed check" in (result.get("shadow_alarm") or "")


def test_the_live_peak_joins_the_sample_and_can_be_the_only_thing_that_fires():
    """THE post-mortem gap, as a test. The journal is CLEAN here -- every recorded peak fits
    the declared weight -- and the growth is entirely inside the running unit lifetime, which
    is the regime a journal-only reading cannot see at all.

    MUTATION KILLED: dropping the live reader and trusting the journal alone. That mutation
    leaves this green only if the journal happens to have caught a restart; on the real
    sim-runner it reported 13,824 MB while the unit stood at 22,703 MB.
    """
    verdict = rh.weight_drift(
        "sim_run",
        peaks_reader=_peaks([4096.0, 8192.0]),
        live_reader=lambda unit: 22703.0,
    )

    assert verdict["drifted"] is True
    assert verdict["live_peak_mb"] == pytest.approx(22703.0)
    assert verdict["observed_peak_mb"] == pytest.approx(22703.0)


def test_an_injected_journal_does_not_silently_recruit_the_real_boxes_live_peak():
    """DETERMINISM, and it is not academic: this box's live peak is currently ABOVE every
    weight in the table, so a test that constructed a small journal would flip to drifted
    from the machine it happens to run on. Injecting either reader means the observation set
    is what was injected.
    """
    verdict = rh.weight_drift("sim_run", peaks_reader=_peaks([2048.0]))

    assert verdict["live_peak_mb"] is None
    assert verdict["observed_peak_mb"] == pytest.approx(2048.0)
    assert verdict["drifted"] is False


def test_a_live_peak_alone_is_an_observation_even_when_the_journal_is_unreadable():
    """An unreadable journal is still a failed check -- but a live reading is real evidence,
    so it becomes the sample rather than being discarded into 'unknown'."""
    verdict = rh.weight_drift(
        "sim_run",
        peaks_reader=lambda unit, since: None,
        live_reader=lambda unit: 22703.0,
    )

    assert verdict["drifted"] is True
    assert verdict["observed_peak_mb"] == pytest.approx(22703.0)
