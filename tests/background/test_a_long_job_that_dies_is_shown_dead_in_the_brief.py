"""A long job that dies is shown dead in the brief, beside the ones still running.

On 2026-09-29 `ab5-runA` was OOM-killed at 10:01Z and `ab5-runA2` exited 1 at 15:08Z. The launch
register settled both to `died` within minutes; every reader the seat orients on asked only what
was still alive, so each death stayed invisible for over an hour.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from background import delivery_seat as seat
from background import launch_liveness as ll

SINCE = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)

#: `ab5-runA2` exactly as the live register held it: settled before the exit time was kept, so
#: status and result live only in the evidence prose.
RUN_A2 = {
    "job": "ab5-runA2", "unit": "longjob-ab5-runa2", "artefact": "/var/tmp/se-ab5-out/runA2.json",
    "log": "/var/tmp/se-ab5-out/runA2.log", "rc_path": None,
    "launched_at": "2026-09-29T11:29:16Z", "asserted_live_by": [], "claim": "died",
    "settled_at": "2026-09-29T15:08:59Z",
    "evidence": "the user manager reports `longjob-ab5-runa2` Result=exit-code (ExecMainStatus=1) "
                "and no artefact at `/var/tmp/se-ab5-out/runA2.json`.",
}


def _register(tmp_path, rows):
    path = tmp_path / ".launch_records.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def _row(job, claim, launched, settled=None, **extra):
    return {"job": job, "unit": "longjob-" + job, "claim": claim, "launched_at": launched,
            "settled_at": settled, "artefact": None, "log": None, **extra}


def test_the_partition_dead_finished_old_and_live_each_land_where_they_belong(tmp_path):
    """THE CONTROL OVER THE WHOLE PARTITION, asserted before what any row says: a dead job in the
    window CAN appear, and so can a finished one, while a death before the window and a job still
    live do not. A reader that shows nothing passes every "does it exclude" leg alone.

    MUTATION: drop the `since` filter and `old-death` appears; drop the `LIVE` skip and `still`
    appears; filter to `died` only and `ok` vanishes.
    """
    path = _register(tmp_path, [
        RUN_A2,
        _row("ok", "finished", "2026-09-29T12:30:00Z", "2026-09-29T13:00:00Z"),
        _row("old-death", "died", "2026-09-28T01:00:00Z", "2026-09-28T02:00:00Z"),
        _row("still", "live", "2026-09-29T12:45:00Z"),
    ])
    seen = seat.ended_since(SINCE, register=path)
    jobs = {j["job"] for j in seen["jobs"]}
    assert "ab5-runA2" in jobs and "ok" in jobs
    assert jobs == {"ab5-runA2", "ok"}
    assert [d["job"] for d in seen["died"]] == ["ab5-runA2"]


def test_run_a2_appears_with_its_exit_status_and_its_settle_time_only_as_a_bound(tmp_path):
    """The first control the direction named. The record has no exit time, so the settle clock
    is reported as `ended_by` and `ended_at` stays empty rather than being filled with it.

    MUTATION: fall back `ended_at` to `settled_at` and the second assertion reds.
    """
    row = seat.ended_since(SINCE, register=_register(tmp_path, [RUN_A2]))["died"][0]
    assert (row["result"], row["exit_status"]) == ("exit-code", "1")
    assert row["ended_at"] is None and row["ended_by"] == "2026-09-29T15:08:59Z"


def test_a_death_launched_before_the_stretch_but_ended_inside_it_is_shown(tmp_path):
    """The stretch is about when it ENDED as much as when it began: a five-hour job launched
    before the last orientation and dying after it is the common case, not the edge."""
    early = dict(RUN_A2, launched_at="2026-09-29T06:00:00Z", exited_at="2026-09-29T12:10:00Z")
    seen = seat.ended_since(SINCE, register=_register(tmp_path, [early]))
    assert seen["died"][0]["ended_at"] == "2026-09-29T12:10:00Z"


def test_a_death_before_the_stretch_first_settled_inside_it_is_shown(tmp_path):
    """The previous orientation could not see a death nobody had settled yet, so this stretch is
    the first that can. MUTATION: drop `settled` from the window test and this row vanishes."""
    late = dict(RUN_A2, launched_at="2026-09-29T06:00:00Z", exited_at="2026-09-29T11:00:00Z",
                settled_at="2026-09-29T12:30:00Z")
    assert [d["job"] for d in seat.ended_since(SINCE, register=_register(tmp_path, [late]))[
        "died"]] == ["ab5-runA2"]


def test_an_unreadable_register_is_not_an_empty_one(tmp_path):
    path = tmp_path / ".launch_records.json"
    path.write_text("[{", encoding="utf-8")
    seen = seat.ended_since(SINCE, register=path)
    assert seen["available"] is False
    text = seat._prompt(_brief(ended=seen))
    assert "COULD NOT BE READ" in text and "'none died' is NOT what this says" in text


def _brief(**over):
    base = {"substantive_count": 0, "levels_recorded": [], "levels_moved": {},
            "director_inputs": [], "findings": {}, "live_direction_age_hours": 1.0,
            "shape": {"available": True, "shape_is_wrong": False, "count": 3,
                      "carrying_work": 3, "changed_nothing": 0, "findings": []}}
    base.update(over)
    return base


def test_the_brief_renders_the_dead_job_and_a_death_makes_the_stretch_material(tmp_path):
    """Done means the brief SHOWS it, and that a stretch whose only event was a death is not
    skipped as quiet -- skipping it is how the death stays invisible.

    MUTATION: remove the `died` clause from `is_material` and `material` is False; drop
    `ended_sentence` from `_prompt` and the job name is absent from the text.
    """
    ended = seat.ended_since(SINCE, register=_register(tmp_path, [RUN_A2]))
    brief = _brief(ended=ended)
    material, why = seat.is_material(brief)
    assert material is True and "ab5-runA2" in why
    text = seat._prompt(brief)
    assert "LONG JOBS THAT STOPPED" in text
    assert "DIED     ab5-runA2" in text and "status=1" in text


def test_a_stretch_whose_only_ending_was_a_success_stays_quiet(tmp_path):
    ended = seat.ended_since(SINCE, register=_register(tmp_path, [
        _row("ok", "finished", "2026-09-29T12:30:00Z", "2026-09-29T13:00:00Z")]))
    assert seat.is_material(_brief(ended=ended))[0] is False


def test_a_settle_now_keeps_the_exit_time_systemd_gave(tmp_path):
    """The settle clock is when somebody next asked; `ab5-runA` settled at 10:08:47Z after dying
    at 10:01:46Z. The re-ask keeps systemd's own exit time, in UTC, on the record.

    MUTATION: drop the copy loop in `check` and `exited_at` is absent from the record.
    """
    path = _register(tmp_path, [_row("ab5-runA", "live", "2026-09-29T08:51:17Z",
                                     artefact="/nonexistent/runA.json")])
    fields = {"ActiveState": "failed", "Result": "oom-kill", "ExecMainStatus": "9",
              "LoadState": "loaded", "ExecMainExitTimestamp": "Tue 2026-09-29 10:01:46 UTC"}
    ll.check(path, probe=lambda unit: fields)
    rec = json.loads(path.read_text())[0]
    assert rec["claim"] == "died"
    assert (rec["exited_at"], rec["result"], rec["exit_status"]) == (
        "2026-09-29T10:01:46Z", "oom-kill", "9")
    assert seat.ended_since(SINCE.replace(hour=9), register=path)["died"][0]["ended_at"] == (
        "2026-09-29T10:01:46Z")
