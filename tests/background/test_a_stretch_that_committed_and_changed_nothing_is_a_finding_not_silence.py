"""THE TWO SURFACES THAT READ 29 EMPTY MERGES AS HEALTH, and what each now does instead.

Director, 2026-09-02: *"Give the delivery seat that vantage: every orientation reads the last
stretch of commits as a list a person would read -- what landed, what it was, whether the shape is
right -- and treats a run of identical commits, or a stretch with nothing substantive, as a finding
about the machine rather than a sign of health."*

The instrument itself is held by
`test_a_daemon_producing_empty_merges_lit_up_every_liveness_surface.py`. This file holds the two
places that CONSUME it, because a correct instrument nobody reads is the shape that let a reaper
sit unwired from July to September.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import background.deadmans_switch as dms
import background.delivery_seat as seat

# ── the liveness clock ──────────────────────────────────────────────────────────────────────
_LOOP = "merge origin/main: automatic reconciliation in an isolated worktree"


def test_an_empty_commit_does_not_refresh_the_liveness_clock(monkeypatch):
    """THE STALL ALARM STAYED CLEAR FOR THE WHOLE OUTAGE.

    `_is_non_progress_commit` is a denylist of subject PREFIXES -- `chore(`, auto-process, HARDEN.
    The loop's subject matched none of them, so 29 commits that changed nothing whatsoever counted
    as forward progress and the watchdog reported a healthy machine.

    MUTATION: drop the `_commits_that_changed_nothing` leg and this returns 2000.0 -- the empty
    merge -- which is exactly what it did all afternoon.
    """
    monkeypatch.setattr(dms, "_recent_commits",
                        lambda n=200: [(2000.0, _LOOP), (1000.0, "a real change")])
    monkeypatch.setattr(dms, "_commits_that_changed_nothing", lambda: {(2000.0, _LOOP)})
    assert dms._last_meaningful_commit_epoch() == 1000.0


def test_the_subject_leg_is_still_load_bearing(monkeypatch):
    """BOTH LEGS, because neither implies the other: a `chore(` commit that really does write
    files is still not forward progress. Removing the old leg must not be a way to pass."""
    monkeypatch.setattr(dms, "_recent_commits",
                        lambda n=200: [(2000.0, "chore(provenance): banner"), (1000.0, "work")])
    monkeypatch.setattr(dms, "_commits_that_changed_nothing", lambda: set())
    assert dms._last_meaningful_commit_epoch() == 1000.0


def test_an_unreadable_history_leaves_the_subject_leg_standing_alone(monkeypatch):
    """THE LIMIT, ASSERTED SO IT IS DECLARED RATHER THAN DISCOVERED. When the content of the
    history cannot be read, this leg contributes nothing and behaviour is exactly what it was
    before -- not better, and importantly not worse."""
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: [(2000.0, _LOOP), (1000.0, "work")])
    monkeypatch.setattr(dms, "_commits_that_changed_nothing", lambda: set())
    assert dms._last_meaningful_commit_epoch() == 2000.0


def test_the_leg_never_takes_the_watchdog_down(monkeypatch):
    """A watchdog that dies of its own instrument is worse than one without it."""
    import background.commit_narrative as cn

    def _boom(*a, **kw):
        raise RuntimeError("git exploded")

    monkeypatch.setattr(cn, "read_commits", _boom)
    assert dms._commits_that_changed_nothing() == set()


def test_it_reads_the_real_history_without_raising():
    """The wire, against the actual repository -- `an_unwired_mechanism_has_no_red_state`: an
    ARMED-looking function that never successfully runs reads as "found nothing"."""
    assert isinstance(dms._commits_that_changed_nothing(), set)


# ── the seat's vantage ──────────────────────────────────────────────────────────────────────
def _brief(**over):
    base = {"substantive_count": 0, "levels_recorded": [], "levels_moved": {},
            "director_inputs": [], "findings": {}, "live_direction_age_hours": 1.0,
            "shape": {"available": True, "shape_is_wrong": False, "count": 3,
                      "carrying_work": 3, "changed_nothing": 0, "findings": []}}
    base.update(over)
    return base


def test_a_spinning_machine_is_material_where_it_used_to_read_as_a_quiet_night(monkeypatch):
    """THE INVERSION. `commits_since` classifies substantive BY FILENAME, and `git log
    --name-only` prints no filenames for a merge -- so all 29 scored non-substantive,
    `substantive_count` was 0, and the seat SKIPPED orienting. A machine committing every six
    minutes produced the identical brief to a machine doing nothing.

    MUTATION: remove the `shape_is_wrong` clause and this returns (False, "nothing to orient on").
    """
    material, why = seat.is_material(_brief(shape={
        "available": True, "shape_is_wrong": True, "count": 29, "carrying_work": 0,
        "changed_nothing": 29,
        "findings": [{"kind": "NO_WORK", "detail": "d", "commits": ["a"]},
                     {"kind": "METRONOME", "detail": "d", "commits": ["a"]}]}))
    assert material is True
    assert "NO_WORK" in why and "METRONOME" in why
    assert "machine fault" in why


def test_a_genuinely_quiet_stretch_is_still_not_material():
    """The floor. If this went material on every empty stretch the seat would orient hourly on
    nothing, and the finding would be noise inside a week."""
    material, why = seat.is_material(_brief())
    assert material is False and "nothing this stretch to orient on" in why


def test_a_sound_stretch_of_real_work_is_material_for_the_ORDINARY_reason():
    material, why = seat.is_material(_brief(substantive_count=4))
    assert material is True and "substantive" in why


# ── and the seat must actually SEE it ───────────────────────────────────────────────────────
def test_the_rendered_list_is_above_the_json_and_outside_its_truncation():
    """`brief` is dumped with a 60k cap and `commits` is the first big key, so a long stretch can
    push everything after it off the end -- including the one part meant to be READ. A vantage a
    truncation can silently remove is not a vantage.

    MUTATION: move `rendered` inside the `json.dumps(...)[:60_000]` and this fails, because the
    filler below is larger than the cap.
    """
    brief = _brief(commits=[{"sha": "x" * 40, "subject": "y" * 200} for _ in range(2000)])
    brief["shape"]["rendered"] = "!! 10:25 abcdef123 the loop's own commit"
    text = seat._prompt(brief)
    assert "abcdef123" in text
    assert text.index("abcdef123") < text.index("THE STRETCH, assembled from git")


def test_an_unreadable_shape_says_so_rather_than_reading_as_sound():
    """`fail_closed_on_unreadable_input`. A brief that silently omits the list would read as "the
    shape was checked and was fine", which is the reassuring answer and the wrong one."""
    text = seat._prompt(_brief(shape={"available": False, "why": "ImportError"}))
    assert "COULD NOT BE READ" in text and "ImportError" in text


def test_the_shape_is_built_from_the_real_stretch_and_never_raises():
    """The wire again, on the real repository."""
    since = datetime.now(timezone.utc) - timedelta(hours=6)
    shape = seat.commit_shape(since)
    assert shape["available"] is True
    assert isinstance(shape["count"], int) and "rendered" in shape


# ── what is ON THE BOX, which no reading above can see ──────────────────────────────────────
def _ps_line(pid, etimes, rss, args, euid=None):
    import os
    return "{} {} {} {} {}".format(pid, etimes, rss,
                                   os.geteuid() if euid is None else euid, args)


def _fake_ps(monkeypatch, lines):
    """Drive `running_now` off a manufactured `ps`, so the assertions are about the READING and
    not about whatever happened to be on the box when the suite ran."""
    import subprocess as sp

    class _R:
        returncode = 0
        stdout = "\n".join(lines) + "\n"

    monkeypatch.setattr(seat.subprocess, "run",
                        lambda *a, **k: _R() if a and a[0][:1] == ["ps"] else sp.run(*a, **k))


def test_A_LONG_JOB_IS_SEEN_AND_AN_IDLE_BOX_SAYS_SO_POSITIVELY(monkeypatch):
    """THE WHOLE PARTITION IN ONE ASSERTION, for the same reason the heartbeat leg needs one.

    A reading hard-wired to "nothing is running" satisfies every test written about the idle box;
    one hard-wired to "something is running" satisfies every test about the busy one. Only both
    sides together can fail either way, so both are asserted here and neither can be dropped to
    make the other pass.

    THE SECOND CLAUSE IS THE POINT: an empty list and a `ps` that never ran look identical on the
    page and mean opposite things, so "nothing long is running" has to be POSITIVELY measured.
    """
    repo = str(seat.PROJECT_DIR)
    busy = [_ps_line(4172305, 9000, 47000, "/usr/bin/python3 -m tools.surgical_land -m msg"),
            _ps_line(4172397, 200, 191000, "/usr/bin/python3 {}/tools/pre_commit_test_gate.py"
                     .format(repo))]
    _fake_ps(monkeypatch, busy)
    seen = seat.running_now()
    assert seen["available"] is True and seen["nothing_long_running"] is False
    assert [j["what"] for j in seen["jobs"]] == [
        "tools.surgical_land", "{}/tools/pre_commit_test_gate.py".format(repo)]
    assert seen["jobs"][0]["elapsed"] == "2h30m", "readable at a glance, not a second count"
    assert seen["jobs"][0]["pid"] == 4172305 and seen["jobs"][0]["rss_mb"] > 0

    _fake_ps(monkeypatch, [_ps_line(9, 5, 100, "/usr/bin/python3 {}/tools/x.py".format(repo))])
    idle = seat.running_now()
    assert idle["available"] is True, "the ps RAN; that is what makes the next line a statement"
    assert idle["nothing_long_running"] is True and idle["jobs"] == []


def test_THE_DECLARED_DAEMONS_ARE_SUBTRACTED_OR_THE_ONE_JOB_THAT_MATTERS_IS_BURIED(monkeypatch):
    """THE STATED FAILURE CONDITION FOR THIS READING, in the ask's own words: *"a process reading
    that lists every python process including the four permanent daemons, so the one long job
    that matters is buried -- it has to be readable at a glance or it gets skipped exactly when
    the box is busiest."*

    And the daemons are not merely noisy, they are the LONGEST-lived things on the box -- days
    against a job's minutes -- so any sort by elapsed puts every one of them ABOVE the row that
    matters. Subtracting them is what makes this a reading rather than a dump.

    MUTATION: drop the `_runs_daemon` filter and this fails on the first assertion.
    """
    repo = str(seat.PROJECT_DIR)
    _fake_ps(monkeypatch, [
        _ps_line(101, 400000, 4000, "/usr/bin/python3 {}/background/dispatcher.py".format(repo)),
        _ps_line(102, 390000, 15000, "/usr/bin/python3 background/ntfy_responder.py"),
        _ps_line(103, 380000, 48000, "/usr/bin/python3 background/supervisor.py"),
        _ps_line(104, 370000, 30000, "/usr/bin/python3 background/deadmans_switch.py"),
        _ps_line(105, 600, 90000, "/usr/bin/python3 -m simulation.run_phase2b --seeds 12"),
    ])
    seen = seat.running_now()
    assert [j["what"] for j in seen["jobs"]] == ["simulation.run_phase2b"], (
        "the four permanent daemons are older than the job and would sort above it")
    assert seen["daemons_subtracted"] == 4


def test_A_PROCESS_THAT_MERELY_MENTIONS_A_MODULE_IS_NOT_NAMED_AS_RUNNING_IT(monkeypatch):
    """CAUGHT ON THE LIVE BOX on this reading's first run, not imagined. A sibling `claude -p`
    seat was named `tools.surgical_land`, because its PROMPT recites `python3 -m tools.surgical_
    land` as the instruction for how to land. Scanning every token for `-m` reads a process that
    MENTIONS a module as one that RUNS it -- the same defect `process_reconciler._runs_daemon`
    was written to refuse, reached again from a different direction.

    MUTATION: scan all tokens for `-m` instead of stopping at the interpreter's first non-option
    argument, and this names the seat `tools.surgical_land`.
    """
    repo = str(seat.PROJECT_DIR)
    _fake_ps(monkeypatch, [
        _ps_line(4073589, 1700, 476000,
                 "/home/rich/.nvm/bin/claude -p --model claude-opus-5 "
                 "You hold the delivery seat in {} -- land with python3 -m tools.surgical_land "
                 "and never --no-verify".format(repo)),
    ])
    seen = seat.running_now()
    assert [j["what"] for j in seen["jobs"]] == ["claude"], (
        "a module recited in a prompt is not a module the process is running")


def test_AN_UNREADABLE_BOX_IS_NOT_REPORTED_AS_AN_IDLE_ONE(monkeypatch):
    """`fail_closed_on_unreadable_input` once more, and it is the failure with teeth here: the
    consequence of reading "nothing is running" when the truth is "I could not tell" is the seat
    LAUNCHING a duplicate of a job already in flight. The seventeen-hour duplicate floor run is
    the precedent, and it cost a whole day of the box.

    MUTATION: return `{"nothing_long_running": True}` on the failure path and this fails twice --
    once on the flag, once on the sentence the seat actually reads.
    """
    def _boom(*a, **k):
        raise OSError("no ps on this box")

    monkeypatch.setattr(seat.subprocess, "run", _boom)
    seen = seat.running_now()
    assert seen["available"] is False
    assert seen.get("nothing_long_running") is None, (
        "'could not tell' must not wear 'nothing is running' as its answer")
    text = seat._prompt(_brief(running=seen))
    assert "WHAT IS RUNNING COULD NOT BE READ" in text and "no ps on this box" in text
    assert "NOTHING LONG IS RUNNING" not in text, (
        "the positive statement is reserved for a ps that actually ran")


def test_WHAT_IS_RUNNING_IS_A_SENTENCE_ABOVE_THE_JSON_AND_OUTSIDE_ITS_TRUNCATION():
    """Six consecutive orientations ran this `ps` BY HAND. A fact the seat must dig out of 60k of
    JSON is one it will dig out on a quiet stretch and skip on a busy one -- which is precisely
    when the box has a job on it.

    MUTATION: leave `running` as a brief key only, and this fails on the filler below.
    """
    brief = _brief(commits=[{"sha": "x" * 40, "subject": "y" * 200} for _ in range(2000)],
                   running={"available": True, "nothing_long_running": False, "count": 1,
                            "daemons_subtracted": 9, "floor_seconds": 60,
                            "jobs": [{"pid": 4172305, "elapsed": "2h30m", "rss_mb": 46.5,
                                      "what": "simulation.run_phase2b", "elapsed_seconds": 9000,
                                      "argv_head": "x"}]})
    text = seat._prompt(brief)
    assert "simulation.run_phase2b" in text
    assert text.index("simulation.run_phase2b") < text.index("THE STRETCH, assembled from git")
    assert "4172305" in text and "2h30m" in text


def test_the_box_reading_is_built_from_the_real_ps_and_never_raises():
    """The wire, on the real machine -- the leg that would have caught an argv format this parser
    cannot read, which no manufactured `ps` above can."""
    seen = seat.running_now()
    assert seen["available"] is True, seen.get("why")
    assert isinstance(seen["count"], int) and isinstance(seen["daemons_subtracted"], int)
    assert seen["nothing_long_running"] is (seen["count"] == 0)
    for job in seen["jobs"]:
        assert job["elapsed_seconds"] >= seat.ELAPSED_FLOOR_SECONDS
        assert job["what"] and not job["what"].startswith("/usr/bin/python")
