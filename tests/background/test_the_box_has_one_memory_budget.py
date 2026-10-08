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
