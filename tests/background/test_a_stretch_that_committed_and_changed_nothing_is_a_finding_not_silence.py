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

import io
import json
import time
import types
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


# ── the COMPLEMENT of that subtraction: a declared daemon that is NOT there ──────────────────
def _enabled_rows():
    """The manifest rows that MUST be running, which is the population the absence leg reports
    over. Read off the manifest rather than typed, so a daemon added tomorrow is in the fixture."""
    from background.process_reconciler import SEAT_MATCH, load_manifest
    return [e for e in load_manifest()
            if e.get("state") == "enabled" and e.get("match") and e["match"] != SEAT_MATCH]


def _fake_journal(monkeypatch, ages, mute=()):
    """Drive the per-daemon log clock off a dict, so no assertion here depends on journalctl
    existing or on what this box happened to have logged.

    `mute` names the sessions whose newest journal line is systemd's own rather than the
    service's -- the third element of `_unit_last_write`'s return. Default False: a daemon is
    assumed to have spoken unless a test says otherwise, because the flattering assumption here
    is the loud one and it must be asked for explicitly.
    """
    monkeypatch.setattr(seat, "_unit_last_write",
                        lambda session: (ages.get(session, 300), "", session not in mute))


def test_A_DECLARED_DAEMON_THAT_IS_ABSENT_IS_NAMED_AND_A_PRESENT_ONE_IS_NOT(monkeypatch):
    """THE WHOLE PARTITION IN ONE CONTROL, and it has to be, for the reason CLAUDE.md gives: a
    reading hard-wired to "something is missing" names `background-worker` on every input and
    passes any test that only ever removes it. Both directions are asserted here against the SAME
    daemon, so neither leg can be dropped to make the other pass.

    THE DEFECT IT IS WRITTEN AGAINST. `running_now` matched the manifest against `ps` in order to
    SUBTRACT the declared daemons, and published only the count it had taken out. The complement
    was computed and thrown away, so the brief's sentence read identically whether ten daemons
    were up or none were -- a subtraction that hides absence, which is a control that cannot fail.

    MUTATION (the one the ask names): make `declared_absent` always empty, or drop
    `absence_sentence` from the assembled prompt, and the first half fails. Make it return every
    declared row regardless of `on_box` and the second half fails.
    """
    _fake_journal(monkeypatch, {"background-worker": 52_698})
    # The box is built FROM the manifest's own launch commands, so the partition is exactly one
    # daemon wide: every enabled daemon is present except `background-worker`. Hand-listing two
    # of them would leave the other nine absent too, and the header would fire in both halves.
    others = [_ps_line(100 + i, 400_000, 4000, "/usr/bin/" + e["command"])
              for i, e in enumerate(_enabled_rows()) if e["session"] != "background-worker"]
    _fake_ps(monkeypatch, others)
    gone = seat.running_now()
    assert [r["session"] for r in gone["declared_absent"]] == ["background-worker"], (
        "only the one daemon missing from this manufactured box may be listed")

    text = seat._prompt(_brief(running=gone))
    assert "DECLARED DAEMON(S) ARE NOT ON THE BOX" in text
    assert "background-worker" in text and "14h38m" in text, (
        "named, and with how long since it last wrote its own log")

    # PRESENT: the same daemon back on the box, and the line must DISAPPEAR.
    _fake_ps(monkeypatch, others + [
        _ps_line(102, 30, 47_000, "/usr/bin/python3 background/background_worker.py")])
    back = seat.running_now()
    assert not any(r["session"] == "background-worker" for r in back["declared_absent"])
    back_text = seat._prompt(_brief(running=back))
    assert "DECLARED DAEMON(S) ARE NOT ON THE BOX" not in back_text, (
        "a daemon that is running must not be reported absent -- a control that cries wolf on "
        "healthy input gets ignored, which is worse than no control")
    # Asserted on the SENTENCE, not on the whole prompt: the brief also serialises the `running`
    # dict as JSON below the sentence, so every declared daemon's NAME is in the text either way.
    # The claim this control makes is about the line the seat actually reads.
    assert "background-worker" in json.dumps(back["declared"]), "still measured, just not absent"


def test_A_MUTE_DAEMON_AND_A_QUIET_ONE_DO_NOT_RENDER_AS_THE_SAME_ROW(monkeypatch):
    """THE WHOLE PARTITION IN ONE CONTROL, for the reason CLAUDE.md gives about rare branches: a
    reading hard-wired to call everything mute passes any test that only ever shows it a mute
    daemon. Both classes are asserted here against the SAME brief, at the SAME age, so neither
    leg can be dropped to make the other pass -- and the shared age is the point, because it is
    what makes the two rows indistinguishable to the OLD reading.

    THE DEFECT IT IS WRITTEN AGAINST (2026-09-22, lane 0). Four declared daemons were on the box,
    `active (running)` under systemd, counted present by the census, and had produced no line of
    their own since starting -- `worker-seat-manager` for 106 hours. Every liveness reading this
    machine keeps said they were fine, because every one of them asks whether the process EXISTS.
    A process that exists and does nothing passed all of them. `ntfy-responder` is the only
    channel the director has, so "he said nothing" and "we stopped listening" had the same shape.

    MUTATION: delete the `not r.get("mute")` filter from the quiet population in `_prompt` and
    the mute daemon sorts back into the quiet sentence -- the first assertion fails because the
    quietest-daemon phrase names it. Make `_mute_sentence` return "" and the second fails.
    """
    # SAME age for both, so the only thing telling them apart is which clock's line it was.
    _fake_journal(monkeypatch, {"worker-seat-manager": 384_000, "token-proxy": 384_000},
                  mute=["worker-seat-manager"])
    _fake_ps(monkeypatch, [_ps_line(100 + i, 400_000, 4000, "/usr/bin/" + e["command"])
                           for i, e in enumerate(_enabled_rows())])
    seen = seat.running_now()
    rows = {r["session"]: r for r in seen["declared"]}
    assert rows["worker-seat-manager"]["mute"] is True
    assert rows["token-proxy"]["mute"] is False, "a daemon that spoke is never mute"

    text = seat._prompt(_brief(running=seen))
    # QUIET: the quietest-daemon sentence must name the one that SPOKE, never the mute one --
    # at 106h40m they are the same number, so this can only pass by reading the right field.
    assert "The quietest has not written its own log for 106h40m (`token-proxy`)" in text
    # MUTE: said separately, in its own words, naming the daemon the quiet sentence excluded.
    assert "DECLARED DAEMON(S) ARE MUTE, WHICH IS NOT THE SAME AS QUIET" in text
    assert "worker-seat-manager" in text.split("ARE MUTE, WHICH IS NOT THE SAME AS QUIET")[1]

    # AND THE OTHER DIRECTION: with nothing mute, the loud sentence must DISAPPEAR entirely.
    # A reading that prints a mute header on a healthy box gets ignored, which is worse than none.
    _fake_journal(monkeypatch, {"worker-seat-manager": 384_000, "token-proxy": 384_000})
    healthy = seat._prompt(_brief(running=seat.running_now()))
    assert "ARE MUTE, WHICH IS NOT THE SAME AS QUIET" not in healthy


def test_A_MUTE_DAEMONS_ESTABLISHED_CAUSE_REACHES_THE_BRIEF_AND_AN_UNESTABLISHED_ONE_IS_ASKED_FOR(
        monkeypatch):
    """BOTH SIDES OF THE PARTITION AT ONCE, against two daemons that are mute for the SAME number
    of seconds, so the only thing that can separate them is whether the manifest has a cause.

    THE DEFECT IT IS WRITTEN AGAINST (2026-09-22, lane 0). The causes for four mute daemons were
    established correctly -- one of them, `worker-seat-manager`, naming a failure mode nobody had
    thought of -- written into `log_silence` on their manifest rows, and `grep -rn log_silence`
    over the whole repository returned the manifest and NOTHING ELSE. No reader read the key.
    `declared_daemon_health` built its row from the journal alone, so a daemon with a perfectly
    good cause on file rendered identically to one nobody had ever looked at, and the brief went
    on asking for work that was already done. A finding filed where no reader looks is not filed.

    WHY THE TWO KEYS MUST STAY SEPARATE, which is the other half of the claim. `why_no_log` is a
    MEASURED absence -- this reading could not get a number. `declared_cause` is a DECLARED one --
    a human established why and wrote it down. Collapsing a declared cause into a measured absence
    is the same defect the reader was built to fix, one level up, so this control asserts the
    caused daemon still carries its measurement and is still counted mute.

    MUTATION: drop `declared_cause` from the row dict in `declared_daemon_health` and the caused
    daemon's text vanishes -- the first assert fails. Render the causes but not the uncaused list
    (or vice versa) and one of the two section assertions fails. Merge the two populations so
    every mute row prints under one heading and the "asks nothing of you" separation collapses:
    the `ACTIONABLE_ONLY` assert fails, because a caused daemon would appear in it.
    """
    CAUSE = "MUTE BY CONSTRUCTION -- no write-out path at all, established against live pid."
    # Built by STRIPPING the live manifest rather than by hand, so this fixture cannot drift into
    # asserting a cause the manifest no longer carries -- then exactly one cause is put back.
    entries = [{k: v for k, v in e.items() if k != "log_silence"} for e in _enabled_rows()]
    for e in entries:
        if e["session"] == "worker-seat-manager":
            e["log_silence"] = CAUSE

    # IDENTICAL AGE, both mute: the cause is the ONLY discriminator left in the input.
    monkeypatch.setattr(seat, "_unit_last_write", lambda s: (384_000, "", False))
    rows = seat.declared_daemon_health(
        {e["match"] for e in entries}, entries=entries)
    by = {r["session"]: r for r in rows}
    assert by["worker-seat-manager"]["declared_cause"] == CAUSE, "the manifest key must reach the row"
    assert by["supervisor"]["declared_cause"] == "", "a row with no cause on file declares that"
    # The measurement is NOT displaced by the declaration -- both are still true of this daemon.
    assert by["worker-seat-manager"]["mute"] is True
    assert by["worker-seat-manager"]["last_log"] == "106h40m"

    text = seat._mute_sentence(rows)
    # THE ESTABLISHED CAUSE IS CARRIED THROUGH, verbatim enough to be useful at the point of read.
    assert "no write-out path at all" in text, "an established cause must reach the brief"
    # AND THE UNESTABLISHED ONE IS STILL ASKED FOR, under a heading that says it is the ask.
    actionable = text.split("NO CAUSE ON FILE")[1].split("CAUSE ESTABLISHED AND ON FILE")[0]
    assert "supervisor" in actionable, "a daemon nobody has investigated is the actionable list"
    assert "worker-seat-manager" not in actionable, \
        "ACTIONABLE_ONLY -- a daemon whose cause is on file must never be asked for again"

    # THE DEFINITION IS ON THE PAGE, not inferred from the count. Two definitions gave 4 and 5
    # over one box in one morning; a reader who cannot see which is in force reads that as decay.
    assert "MUTE HERE MEANS DEFINITION B" in text


def test_THE_LOG_AGE_IS_TAKEN_ON_THE_MONOTONIC_CLOCK_NOT_THE_CORRECTABLE_WALL_CLOCK(monkeypatch):
    """The age must survive a wall-clock correction, because on this box it did not.

    THE MEASUREMENT THIS IS KEYED TO (2026-09-22, the real journal). Four units' newest entries
    carried realtime stamps 52,609 SECONDS -- 14.61h -- before the units' own start, an
    impossibility the brief published as a fact. The guest's realtime clock had run 14.61h behind
    while those lines were stamped and was resynchronised afterwards; the identical offset on
    daemons whose start times differ by two days is what rules out coincidence. Monotonic stamps
    cannot be corrected, so `uptime - __MONOTONIC_TIMESTAMP` is the true age.

    MUTATION -- and it is a mutation OF THE STAMP, which is what the ask named: the realtime
    stamp below is deliberately 14.61h earlier than the monotonic one describes. Restore the old
    `time.time() - realtime` body and the age comes back 52,609s too large and this fails. Keyed
    to the PROPERTY (the two clocks disagree, follow the uncorrectable one), not to today's
    answer, so it stays green when the box's clock is behaving and red whenever the code regresses.
    """
    boot = "abc123def456"
    uptime = 500_000.0
    true_age, skew = 3_600.0, 52_609.0
    entry = {
        "__REALTIME_TIMESTAMP": str(int((time.time() - true_age - skew) * 1e6)),  # <-- MUTATED
        "__MONOTONIC_TIMESTAMP": str(int((uptime - true_age) * 1e6)),
        "_BOOT_ID": boot,
        "_SYSTEMD_USER_UNIT": "dispatcher.service",
    }
    monkeypatch.setattr(seat, "_boot_id", lambda: boot)
    monkeypatch.setattr(seat.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(stdout=json.dumps(entry), returncode=0))
    monkeypatch.setattr("builtins.open", lambda *a, **k: io.StringIO("{} 0.0".format(uptime)))

    age, why, spoke = seat._unit_last_write("dispatcher")
    assert abs(age - true_age) <= 2, (
        "the age must follow the monotonic stamp ({}s); the realtime stamp says {}s and it is "
        "the one that was corrected".format(true_age, true_age + skew))
    assert why == "", "a clean monotonic reading carries no caveat"
    assert spoke is True, "_SYSTEMD_USER_UNIT names the service itself, so the service spoke"


def test_A_DAEMON_YOUNGER_THAN_THE_JOB_FLOOR_IS_STILL_PRESENT(monkeypatch):
    """`deploy_restart` cycles several declared daemons every ten minutes, so a perfectly healthy
    daemon is routinely a few seconds old. The elapsed floor exists to keep short-lived JOBS out
    of the list; if it runs BEFORE the daemon match it also drops young daemons out of the
    present set and reports a running daemon as MISSING -- on this box, several times an hour.

    MUTATION: move the `etimes < floor_seconds` test back above the `_runs_daemon` match and this
    fails; the daemon below is 3 seconds old against a 60-second floor.
    """
    _fake_journal(monkeypatch, {})
    _fake_ps(monkeypatch, [
        _ps_line(102, 3, 47_000, "/usr/bin/python3 background/background_worker.py")])
    seen = seat.running_now()
    assert not any(r["session"] == "background-worker" for r in seen["declared_absent"])
    assert seen["jobs"] == [], "a daemon is never a job, at any age"


def test_AN_UNREADABLE_BOX_NEVER_SAYS_EVERY_DECLARED_DAEMON_IS_PRESENT(monkeypatch):
    """The fail-open twin of the leg above, and the one that would actually have shipped: when the
    `ps` does not run, `declared_absent` is empty for the reason that proves nothing at all. An
    empty absence list and an unasked question are the same shape and opposite in meaning.

    MUTATION: drop the `available` guard in front of the absence block and this fails -- the
    else-branch cheerfully reports "EVERY DECLARED DAEMON IS ON THE BOX (0 of them)".
    """
    def _boom(*a, **k):
        raise OSError("no ps on this box")

    monkeypatch.setattr(seat.subprocess, "run", _boom)
    text = seat._prompt(_brief(running=seat.running_now()))
    assert "EVERY DECLARED DAEMON IS ON THE BOX" not in text
    assert "WHAT IS RUNNING COULD NOT BE READ" in text


def test_EVERY_ENABLED_DAEMON_IN_THE_MANIFEST_CAN_ACTUALLY_BE_MATCHED_ON_THIS_BOX():
    """THE WIRE, and the leg that pays for itself. `naive-organ` is launched `-m
    background.naive_organ`, and its manifest row declared `match: naive_organ` -- a bare stem
    that `_runs_daemon`'s basename-equality test can never match against any argument. It was
    invisible while the only consumer counted daemons in order to subtract them, and became a
    permanently-absent healthy daemon the moment absence was reported.

    This keys on the PROPERTY (every enabled row is matchable against its own declared launch
    command) rather than on today's answer, so it stays green when a daemon is added correctly and
    reds when a row is added with an unmatched token.
    """
    from background.process_reconciler import SEAT_MATCH, _runs_daemon, load_manifest

    unmatched = [e["session"] for e in load_manifest()
                 if e.get("state") == "enabled" and e.get("match")
                 and e["match"] != SEAT_MATCH
                 and not _runs_daemon(e["command"], e["match"])]
    assert not unmatched, (
        "these enabled daemons declare a `match` their own `command` cannot satisfy, so they "
        "would be reported absent forever: {}".format(unmatched))


def test_the_absence_leg_is_built_from_the_real_box_and_never_raises():
    """The wire on the real machine, for the argv or journal format no fixture above can imagine."""
    seen = seat.running_now()
    assert seen["available"] is True, seen.get("why")
    assert isinstance(seen["declared"], list) and seen["declared"], "the manifest has enabled rows"
    for row in seen["declared"]:
        assert row["session"] and isinstance(row["on_box"], bool)
        assert row["last_log_seconds"] is None or row["last_log_seconds"] >= 0
        assert (row["last_log"] is None) == (row["last_log_seconds"] is None), (
            "a missing age and a rendered one must never disagree about whether it is known")
