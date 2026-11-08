"""The box's one memory budget (director, 2026-10-08): "Make one memory budget for the whole box that
everything goes through: runs from every lane, test gates and landings. Anything that doesn't fit
queues instead of co-running."

Defect these fire on: the 2026-10-08 vulnerability landing's test gate was killed by the OOM reaper
beside three lanes' 10-11 GB of runs, because the gate and direct runs never asked the governor, the
ledger lived inside whichever tree imported it, and the launch door kept a sum of its own.
"""
from pathlib import Path

import pytest

from background import launch_long_job as llj
from background import resource_headroom as rh


def _box(tmp_path, available_mb, total_mb=24000.0):
    return {"reservations_path": tmp_path / "ledger.json", "launch_records_path": tmp_path / "lr.json",
            "residents": [], "meminfo_path": _meminfo(tmp_path, total_mb, available_mb)}


def _meminfo(tmp_path, total_mb, available_mb) -> Path:
    p = tmp_path / f"meminfo_{available_mb}"
    p.write_text(f"MemTotal: {int(total_mb * 1024)} kB\nMemAvailable: {int(available_mb * 1024)} kB\n")
    return p


def test_a_job_that_does_not_fit_QUEUES_and_starts_when_room_appears(tmp_path, monkeypatch):
    """Both sides in one test: it must wait while the box is full (a door that always admits
    passes the second half) and must start once room appears (a door that never admits passes the
    first)."""
    monkeypatch.delenv(rh.ADMITTED_ENV, raising=False)
    calls = {"n": 0}
    full, roomy = _box(tmp_path, 1500.0), _box(tmp_path, 20000.0)
    real_admit = rh.admit

    def admit(job_class, **kw):
        calls["n"] += 1
        kw.update(full if calls["n"] < 3 else roomy)
        return real_admit(job_class, **kw)

    monkeypatch.setattr(rh, "admit", admit)
    slept = []
    with rh.queued("commit_gate", weight_mb=4000, sleep=slept.append,
                   reservations_path=tmp_path / "ledger.json",
                   deferral_log_path=tmp_path / "deferrals.jsonl") as decision:
        assert decision["admitted"]
        assert rh.ADMITTED_ENV in __import__("os").environ
        held = rh.live_reservations(tmp_path / "ledger.json")
        assert [r["job_class"] for r in held] == ["commit_gate"]
    assert len(slept) == 2, "it did not wait while the box was full"
    assert rh.live_reservations(tmp_path / "ledger.json") == [], "the reservation outlived the job"
    assert (tmp_path / "deferrals.jsonl").read_text().count('"queued": true') == 1


def test_a_job_that_never_fits_says_why_instead_of_waiting_forever(tmp_path, monkeypatch):
    monkeypatch.delenv(rh.ADMITTED_ENV, raising=False)
    monkeypatch.setattr(rh, "admit", lambda jc, **kw: _refused())
    with pytest.raises(rh.QueueTimeout, match="never fitted"):
        with rh.queued("commit_gate", weight_mb=4000, deadline_seconds=0, sleep=lambda s: None,
                       reservations_path=tmp_path / "ledger.json",
                       deferral_log_path=tmp_path / "d.jsonl"):
            pass


def _refused():
    return {"admitted": False, "reason": "budget exhausted: test"}


def test_work_inside_an_admitted_holder_is_not_counted_twice(tmp_path, monkeypatch):
    """A run inside an admitted gate or a launched long job passes straight through and holds no
    second reservation. Mutation: ignoring ADMITTED_ENV reserves twice and reds this."""
    monkeypatch.setenv(rh.ADMITTED_ENV, "longjob:longjob-x")
    monkeypatch.setattr(rh, "admit", lambda *a, **k: pytest.fail("an admitted holder asked again"))
    with rh.queued("sim_run", weight_mb=7000, reservations_path=tmp_path / "ledger.json"):
        assert rh.live_reservations(tmp_path / "ledger.json") == []


def test_the_launch_door_counts_a_reservation_above_its_holders_measured_size():
    """A gate that reserved 4 GB but has not grown yet must still keep a long job out. Mutation:
    dropping `reserved` from co_residence admits the job and reds this."""
    residents = [{"pid": 101, "rss_mb": 300.0, "unit": "x", "command": "pytest"}]
    room = llj.co_residence(15000, residents, 24032, reserved={})
    full = llj.co_residence(15000, residents, 24032, reserved={101: 9000.0})
    assert room["admitted"] and not full["admitted"]


def test_the_ledger_is_one_file_for_the_box_not_one_per_tree():
    """The ledger lived under the importing tree's docs/observability, so a gate in a clean extract
    and a run in a worktree each kept their own. It must sit outside every tree."""
    from background.resource_headroom import PROJECT_DIR, RESERVATIONS_PATH
    assert PROJECT_DIR not in RESERVATIONS_PATH.parents


def test_landings_come_before_experiments_and_a_landing_is_never_held_by_itself(tmp_path, monkeypatch):
    """Director, 2026-10-09: "When a landing is ready, the box budget reserves its test-gate memory
    and holds any new long-job launch, from any lane, until it lands." THE WHOLE PARTITION: with a
    landing pending, other work is held; the landing's own gate is not; with none pending, nothing
    is held; a dead claimant holds nothing. A hold that held everything would pass the first leg."""
    monkeypatch.delenv(rh.LANDING_ENV, raising=False)
    landings = tmp_path / "landings.json"
    assert rh.landing_hold_reason(landings) is None
    with rh.landing_pending("test landing", path=landings):
        assert rh.landing_hold_reason(landings) is None, "a landing was held by its own claim"
        monkeypatch.delenv(rh.LANDING_ENV)
        assert "landings come before experiments" in (rh.landing_hold_reason(landings) or "")
        monkeypatch.setenv(rh.LANDING_ENV, "test landing")
    monkeypatch.delenv(rh.LANDING_ENV, raising=False)
    assert rh.landing_hold_reason(landings) is None, "the claim outlived the landing"
    landings.write_text('[{"pid": 999999999, "starttime": "1", "label": "dead", "since": "x"}]')
    assert rh.landing_hold_reason(landings) is None, "a dead landing holds the box"


def test_a_new_long_job_waits_for_a_pending_landing_then_starts(monkeypatch):
    """The launch door holds, not refuses outright: it waits while a landing is pending and goes
    ahead once it clears; past its deadline it names the landing."""
    reasons = iter(["landings come before experiments: 1 pending", None])
    said, slept = [], []
    assert llj._wait_for_pending_landings(said.append, deadline_seconds=3600, sleep=slept.append,
                                          reason_fn=lambda: next(reasons)) is None
    assert slept and any("HELD" in s for s in said)
    stuck = llj._wait_for_pending_landings(lambda s: None, deadline_seconds=0, sleep=lambda s: None,
                                           reason_fn=lambda: "landings come before experiments")
    assert stuck and "landing" in stuck


def test_a_test_process_never_waits_on_the_real_pending_landings(monkeypatch):
    """Defect (2026-10-09): the gate's own tests called launch() in-process and sat in the 90-minute
    hold behind the real pending landing until the gate's 3,600 s limit fired. Inside a test process
    the real register is never read; an injected one still is (the partition test above)."""
    monkeypatch.delenv(rh.LANDING_ENV, raising=False)
    monkeypatch.setattr(rh, "pending_landings",
                        lambda path=None, proc_root=None: [{"pid": 1, "label": "real"}])
    assert rh.landing_hold_reason() is None


def _claimant(label, kind=None):
    """A live process standing in for another landing or run, and its register row."""
    import subprocess
    proc = subprocess.Popen(["sleep", "300"])
    row = {"pid": proc.pid, "starttime": rh._proc_starttime(proc.pid), "label": label, "since": "x"}
    if kind:
        row["kind"] = kind
    return proc, row


def _register(path, row):
    import json
    rows = json.loads(path.read_text()) if path.exists() else []
    path.write_text(json.dumps(rows + [row]))


def _end(proc):
    proc.kill()
    proc.wait()


def test_a_waiting_run_is_admitted_between_overlapping_landings(tmp_path, monkeypatch):
    """Defect (2026-11-08): no book from 03:59 UTC, 156 sim_run deferrals that day, every one a
    landing hold. Each landing registered while the last was still gating, so "any landing pending"
    was true at every cycle and the runner was never admitted. First in, first out: a landing that
    registers AFTER the run was refused waits behind it, so the run goes when the landings that were
    ahead of it finish, however many arrive later."""
    monkeypatch.delenv(rh.LANDING_ENV, raising=False)
    landings = tmp_path / "landings.json"
    procs = []
    try:
        first, row = _claimant("landing 0")
        procs.append(first)
        _register(landings, row)
        assert rh.landing_hold_reason(landings, wait_as="sim-runner"), "a pending landing did not hold"
        admitted_at = None
        previous = first
        for n in range(1, 6):  # the stream: each landing registers before the previous one ends
            nxt, row = _claimant(f"landing {n}")
            procs.append(nxt)
            _register(landings, row)
            _end(previous)
            previous = nxt
            if rh.landing_hold_reason(landings, wait_as="sim-runner") is None:
                admitted_at = n
                break
        assert admitted_at == 1, f"the run was never admitted through {n} overlapping landings"
        assert not any(r.get("kind") == rh.WAITER_KIND for r in rh.pending_landings(landings)), \
            "an admitted run kept its place and would hold the landings behind it"
    finally:
        for p in procs:
            if p.poll() is None:
                _end(p)


def test_a_landing_waits_only_for_runs_that_were_refused_before_it(tmp_path, monkeypatch):
    """The other side of the partition, and the control that the run does not jump the queue: a
    landing registered BEFORE the run still holds it; a landing registered AFTER a waiting run is
    held by it; a landing ahead of the waiting run is not; a landing's own child work never is."""
    import os
    monkeypatch.delenv(rh.LANDING_ENV, raising=False)
    me = {"pid": os.getpid(), "starttime": rh._proc_starttime(os.getpid()), "label": "me", "since": "x"}
    procs = []
    try:
        # Control: a landing ahead of the run holds it, even after the run takes its place.
        landing, row = _claimant("earlier landing")
        procs.append(landing)
        ahead = tmp_path / "ahead.json"
        _register(ahead, row)
        assert "landings come before experiments" in (rh.landing_hold_reason(ahead, wait_as="run") or "")
        later, row = _claimant("later landing")
        procs.append(later)
        _register(ahead, row)
        assert "earlier landing" in (rh.landing_hold_reason(ahead, wait_as="run") or ""), \
            "the run jumped a landing that was pending before it"
        _end(landing)
        assert rh.landing_hold_reason(ahead, wait_as="run") is None, "the later landing held the run"

        # The landing's side: held by a waiting run ahead of it, not by one behind it.
        run, run_row = _claimant("sim-runner", kind=rh.WAITER_KIND)
        procs.append(run)
        monkeypatch.setenv(rh.LANDING_ENV, "me")
        behind = tmp_path / "behind.json"
        _register(behind, run_row)
        _register(behind, me)
        assert "first in, first out" in (rh.landing_hold_reason(behind) or ""), \
            "a landing registered after a waiting run went first"
        before = tmp_path / "before.json"
        _register(before, me)
        _register(before, run_row)
        assert rh.landing_hold_reason(before) is None, "a run refused after the landing held it"
        assert rh.landing_hold_reason(tmp_path / "child.json") is None, "the landing's own work was held"
    finally:
        for p in procs:
            if p.poll() is None:
                _end(p)
