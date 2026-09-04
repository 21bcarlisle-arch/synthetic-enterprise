"""THE DEFECT: a daemon holding changed code kept serving, because nothing performed G-D2.

Every leg here is about the ACT half of deployment, and every one of them is a way the act could
kill a live seat or refuse forever. The partition is the whole safety argument, so it is tested as a
partition — each unit lands in exactly one of restart / defer / hold, and hold always carries a
reason.

The plan is PURE and the restarter is INJECTABLE, so nothing here touches a real daemon.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from background import deploy_restart as dr


def _proc(tmp_path, procs):
    """A fake /proc. `procs` is {pid: (comm, cgroup, ppid)}."""
    root = tmp_path / "proc"
    root.mkdir()
    for pid, (comm, cgroup, ppid) in procs.items():
        d = root / str(pid)
        d.mkdir()
        (d / "comm").write_text(comm + "\n")
        (d / "cgroup").write_text(cgroup + "\n")
        (d / "status").write_text(f"Name:\t{comm}\nPPid:\t{ppid}\n")
    return root


_USER = "0::/user.slice/user-1000.slice/user@1000.service"


def _row(session, **kw):
    row = {"session": session, "unit": f"{session}.service", "stale": True,
           "unresolved": None, "session_hosting": False, "mid_work": False,
           "mid_work_reason": None}
    row.update(kw)
    return row


def _report(rows, unresolved=None):
    return {"daemons": rows, "session_hosting_unresolved": unresolved}


# ── the partition ───────────────────────────────────────────────────────────────────────────────

def test_a_stale_daemon_that_hosts_nothing_is_restarted():
    """The plain case, and the one the director's standing authority is about."""
    plan = dr.restart_plan(_report([_row("sim-runner")]))
    assert plan["restart"] == ["sim-runner.service"]
    assert plan["defer"] == [] and plan["hold"] == {}


def test_a_stale_daemon_that_hosts_a_session_is_deferred_never_restarted():
    """MUTATION: drop the `session_hosting` branch and this fires. Restarting the unit that holds
    the tmux server kills the seat mid-turn, which is the one thing the authority excludes."""
    plan = dr.restart_plan(_report([_row("worker-seat-manager", session_hosting=True)]))
    assert plan["defer"] == ["worker-seat-manager.service"]
    assert plan["restart"] == []


def test_a_daemon_holding_no_changed_module_is_held_however_old_it_is():
    """MUTATION: key the plan to age rather than to changed modules and this fires.

    `token-proxy` had been up 10.9 days on 10.7-day-old code and held ZERO changed modules. Age is
    context; the changed-module set is the verdict. Restarting on age alone is churn that costs a
    daemon's warm state for nothing."""
    plan = dr.restart_plan(_report([_row("token-proxy", stale=False)]))
    assert plan["restart"] == [] and plan["defer"] == []
    assert "no changed module" in plan["hold"]["token-proxy.service"]


def test_unresolved_drift_is_never_treated_as_stale():
    """MUTATION: treat `unresolved` as restartable and this fires. Unknown is not stale — acting on
    an unanswered question is acting on absence, which is the R15 fail-open this repo pays for."""
    plan = dr.restart_plan(_report([_row("ghost", unresolved="unstamped")]))
    assert plan["restart"] == [] and plan["defer"] == []
    assert "unresolved" in plan["hold"]["ghost.service"]


def test_the_callers_own_unit_is_never_restarted():
    """MUTATION: drop the self guard and the restarter kills itself mid-plan, leaving the remaining
    daemons unrestarted and no record of why."""
    plan = dr.restart_plan(_report([_row("supervisor")]), self_unit="supervisor.service")
    assert plan["restart"] == []
    assert "own unit" in plan["hold"]["supervisor.service"]


def test_an_unresolved_session_set_stops_every_restart():
    """MUTATION: let an incomplete session set through and this fires.

    If one live session process cannot be resolved to a unit, the set of units that host a session
    is SMALLER than the truth — and a smaller set is exactly the shape that restarts a live seat.
    The whole plan must stop, not just that unit."""
    plan = dr.restart_plan(_report(
        [_row("sim-runner"), _row("naive-organ")],
        unresolved="a live session process could not be resolved"))
    assert plan["restart"] == [] and plan["defer"] == []
    assert len(plan["hold"]) == 2
    assert all("unresolved" in why for why in plan["hold"].values())


def test_every_unit_lands_in_exactly_one_bucket_with_a_reason():
    """The partition property. A unit in none of the three is invisible: not restarted, not
    deferred, and not explained."""
    rows = [_row("a"), _row("b", session_hosting=True), _row("c", stale=False),
            _row("d", unresolved="closure-unknown"), _row("e")]
    plan = dr.restart_plan(_report(rows), self_unit="e.service")
    placed = set(plan["restart"]) | set(plan["defer"]) | set(plan["hold"])
    assert placed == {f"{s}.service" for s in "abcde"}
    assert len(plan["restart"]) + len(plan["defer"]) + len(plan["hold"]) == 5
    assert all(why.strip() for why in plan["hold"].values())


# ── observing who hosts a session ───────────────────────────────────────────────────────────────

def test_the_user_manager_is_never_mistaken_for_the_owning_unit(tmp_path):
    """MUTATION: drop the `_USER_MANAGER_RE` filter and this fires.

    `user@1000.service` appears in EVERY user cgroup path, so without the filter this names ONE
    unit for every process on the box — every daemon reads as session-hosting and the deployment
    step becomes a permanent no-op that looks like caution. The first draft did exactly that.

    NOT tested here, because it is an EQUIVALENCE and saying so is the point: swapping `found[-1]`
    for `found[0]` changes nothing. Measured 2026-09-04 over every live process, zero have more
    than one non-user-manager service in their cgroup, so after the filter the list has exactly one
    element. `[-1]` is defence against nesting this machine does not do; it is not load-bearing and
    is not claimed to be."""
    root = _proc(tmp_path, {7: ("tmux: server", f"{_USER}/app.slice/sim-runner.service", 1)})
    assert dr._unit_of_pid(7, root) == "sim-runner.service"
    assert dr._unit_of_pid(7, root) != "user@1000.service"


def test_a_seat_in_a_transient_scope_is_resolved_up_to_its_owning_service(tmp_path):
    """MUTATION: drop the parent walk and this fires. A seat's own `claude` process sits in a
    `tmux-spawn-<uuid>.scope`, which names no service — asking its cgroup directly answers nothing,
    and 'nothing' would read as 'hosts no session'."""
    root = _proc(tmp_path, {
        10: ("tmux: server", f"{_USER}/app.slice/worker-seat-manager.service", 1),
        11: ("claude", f"{_USER}/app.slice/tmux-spawn-abc.scope", 10),
    })
    units, unresolved = dr.session_hosting_units(root)
    assert unresolved is None
    assert units == frozenset({"worker-seat-manager.service"})


def test_a_viewer_does_not_make_a_unit_session_hosting(tmp_path):
    """MUTATION: match `tmux` as a substring — the first draft's rule — and this fires.

    A `tmux: client` is someone LOOKING at a session, not the session. On this box one is attached
    over tailscale. Counting it would defer the restart of any managed daemon a viewer happened to
    connect from, forever, on evidence that nobody is working in it."""
    root = _proc(tmp_path, {
        20: ("tmux: client", f"{_USER}/app.slice/sanity-daemon.service", 1),
    })
    units, unresolved = dr.session_hosting_units(root)
    assert unresolved is None
    assert units == frozenset(), "a viewer was mistaken for a hosted session"


def test_an_unresolvable_session_process_makes_the_whole_answer_unresolved(tmp_path):
    """MUTATION: skip the unresolvable process instead of failing the answer, and this fires — the
    set silently shrinks to the units it COULD resolve, which is the fail-open."""
    root = _proc(tmp_path, {
        30: ("claude", f"{_USER}/app.slice/tmux-spawn-xyz.scope", 99),  # parent 99 does not exist
    })
    units, unresolved = dr.session_hosting_units(root)
    assert unresolved and "could not be resolved" in unresolved
    assert units == frozenset()


def test_an_unreadable_proc_restarts_nothing(tmp_path):
    """An unavailable check is a FAILED check (R15), never a clean one."""
    units, unresolved = dr.session_hosting_units(tmp_path / "does-not-exist")
    assert units == frozenset() and unresolved and "unreadable" in unresolved


# ── the turn boundary ───────────────────────────────────────────────────────────────────────────

def test_a_live_seat_in_ANOTHER_unit_does_not_make_this_one_busy(monkeypatch, tmp_path):
    """THE LATENT DEFECT, found 2026-09-04 by asking whether the deferred branch had ever fired in
    PRODUCTION rather than whether it was reachable in a test.

    There is ONE heartbeat file for the machine and the busy test read it for EVERY unit -- `unit`
    appeared nowhere but the message string. A second deferred host, with no seat in it at all,
    would be marked busy by whatever seat happened to be working elsewhere, and would stay stale
    for ever.

    WHAT THIS IS NOT, recorded because I got it wrong first: it is NOT why the branch had fired
    zero times in 48 ticks. Measured, the deferred unit held this interactive session's own live
    `claude` process, so busy was the correct answer and restarting would have killed the seat
    mid-turn. Eight hours of zero fires is explained by eight hours of a working seat.

    MUTATION: drop the `unit in live` scoping and fall back to the global heartbeat -- this fires.
    """
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    (obs / ".seat_heartbeat.json").write_text("{}")   # warm: someone is working RIGHT NOW
    monkeypatch.setattr(dr, "_REPO", tmp_path)
    monkeypatch.setattr(dr, "units_holding_a_live_seat",
                        lambda *a, **k: frozenset({"worker-tick.service"}))

    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert not busy, "another unit's live seat marked this one busy: " + why
    assert "worker-tick.service" in why and "not worker-seat-manager.service" in why

    # ...and the same call for the unit that DOES hold the seat must still say busy, or the
    # scoping has simply turned the signal off.
    busy_here, why_here = dr.unit_has_working_seat("worker-tick.service")
    assert busy_here and "live in worker-tick.service" in why_here


def test_a_live_seat_process_is_read_from_proc_not_from_the_heartbeats_pid(tmp_path):
    """The first draft attributed the heartbeat through the `pid` it records. That pid belongs to
    the PreToolUse HOOK that writes it -- a subprocess that has exited before any reader looks --
    so every attribution returned None and every call fell into the fail-closed branch while
    looking like a measurement. A field that can only ever answer 'cannot tell' is worse than no
    field. MUTATION: resolve the heartbeat pid instead and this fires, because the pid is dead."""
    root = _proc(tmp_path, {
        50: ("claude", f"{_USER}/app.slice/worker-tick.service", 1),
        51: ("tmux: server", f"{_USER}/app.slice/worker-seat-manager.service", 1),
        52: ("python3", f"{_USER}/app.slice/sim-runner.service", 1),
    })
    live = dr.units_holding_a_live_seat(root)
    assert live == frozenset({"worker-tick.service"}), (
        "a tmux server or a plain daemon was counted as a live seat, or the live one was missed"
    )


def test_hosting_a_session_does_not_by_itself_make_a_unit_busy(monkeypatch, tmp_path):
    """THE CORRECTION, kept as a control so it cannot come back.

    The first version of `unit_has_working_seat` returned BUSY whenever the unit was in the
    session-hosting set. But hosting is what makes a unit DEFERRED, and a hosted unit holds its
    tmux server permanently — between turns as much as during them. So the condition was always
    true, the deferred branch was unreachable, and the seat host would have sat stale forever while
    the log printed "DEFERRED" every ten minutes: a permanent no-op wearing caution's clothes.

    MUTATION: reinstate `if unit in hosting: return True` and this fires.

    Hosting decides WHICH ROUTE; busy decides WHEN that route fires. They are different facts."""
    monkeypatch.setattr(dr, "session_hosting_units",
                        lambda *a, **k: (frozenset({"worker-seat-manager.service"}), None))
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "units_holding_a_live_seat", lambda *a, **k: frozenset())
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    hb = obs / ".seat_heartbeat.json"
    hb.write_text("{}")
    import os
    old_t = os.stat(hb).st_mtime - (dr._SEAT_IDLE_S + 60)
    os.utime(hb, (old_t, old_t))
    monkeypatch.setattr(dr, "_REPO", tmp_path)

    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert not busy, "a session host with a cold heartbeat is a turn boundary, not busy: " + why


def test_the_hosts_resting_process_count_does_not_make_it_busy(monkeypatch, tmp_path):
    """THE SECOND CORRECTION, pinned so neither version of the bug can return.

    Having separated hosting from busy, the first repair used `unit_is_mid_work` as the busy
    signal — "more than one process in the cgroup". That is right for a daemon that spawns a child
    per job and WRONG for a session host, whose RESTING state is already two processes: the tmux
    server and the seat, both of which persist between turns. So it returned busy forever and the
    deferred branch stayed exactly as unreachable as before. One trap, entered twice, by two doors.

    MUTATION: reinstate the `unit_is_mid_work` call in `unit_has_working_seat` and this fires.

    For a session host the heartbeat is the whole answer: a job running in a host unit IS the
    seat's work, so there is no third thing the process count could catch."""
    monkeypatch.setattr(dr, "unit_is_mid_work",
                        lambda unit: (True, "2 process(es) in the cgroup, so a job is in flight"))
    monkeypatch.setattr(dr, "units_holding_a_live_seat", lambda *a, **k: frozenset())
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    hb = obs / ".seat_heartbeat.json"
    hb.write_text("{}")
    import os
    old_t = os.stat(hb).st_mtime - (dr._SEAT_IDLE_S + 60)
    os.utime(hb, (old_t, old_t))
    monkeypatch.setattr(dr, "_REPO", tmp_path)

    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert not busy, (
        "the host's resting tmux-server-plus-seat pair was read as work, so the deferred restart "
        "can never fire: " + why
    )


def test_a_warm_heartbeat_is_what_makes_a_host_busy(monkeypatch, tmp_path):
    """The live direction, and the null control's partner: warm heartbeat -> busy, so the pair
    proves the signal discriminates rather than always answering one way."""
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    (obs / ".seat_heartbeat.json").write_text("{}")   # just written = warm
    monkeypatch.setattr(dr, "_REPO", tmp_path)
    monkeypatch.setattr(dr, "units_holding_a_live_seat", lambda *a, **k: frozenset())
    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert busy and "no seat process could be placed" in why


def test_an_unreadable_heartbeat_reads_as_busy(monkeypatch, tmp_path):
    """MUTATION: treat an unreadable heartbeat as idle and this fires. 'I could not tell' must
    never authorise a restart that costs a turn."""
    monkeypatch.setattr(dr, "_REPO", tmp_path)  # no heartbeat file exists under here
    monkeypatch.setattr(dr, "units_holding_a_live_seat", lambda *a, **k: frozenset())
    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert busy and "unreadable" in why


def test_a_quiet_unit_with_a_cold_heartbeat_is_a_turn_boundary(monkeypatch, tmp_path):
    """The only path that lets a session host restart. Both signals must say idle."""
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "units_holding_a_live_seat", lambda *a, **k: frozenset())
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    hb = obs / ".seat_heartbeat.json"
    hb.write_text("{}")
    import os
    old = os.stat(hb).st_mtime - (dr._SEAT_IDLE_S + 60)
    os.utime(hb, (old, old))
    monkeypatch.setattr(dr, "_REPO", tmp_path)
    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert not busy, why
    assert "between turns" in why


# ── the act ─────────────────────────────────────────────────────────────────────────────────────

def test_apply_refuses_its_own_unit_even_if_the_plan_named_it():
    """Belt and braces: the plan excludes it, and so does the act. A caller passing a hand-built
    list must not be able to kill the restarter."""
    calls = []
    out = dr.apply_restarts(["a.service", "b.service"],
                            runner=lambda u: calls.append(u) or "ok",
                            self_unit="a.service")
    assert calls == ["b.service"]
    assert out["restarted"] == ["b.service"]
    assert "refused" in out["failed"]["a.service"]


def test_a_failing_restart_is_recorded_and_does_not_stop_the_rest():
    def runner(unit):
        return None if unit == "bad.service" else "ok"
    out = dr.apply_restarts(["bad.service", "good.service"], runner=runner)
    assert out["restarted"] == ["good.service"]
    assert "bad.service" in out["failed"]


# ── the reading ─────────────────────────────────────────────────────────────────────────────────

def test_the_report_carries_both_ages_for_every_daemon(monkeypatch):
    """THE VISIBILITY THIS OWES: loaded-code age BESIDE running age, in one place, for every
    observed daemon. MUTATION: drop either field and this fires.

    They answer different questions. A daemon restarted an hour ago onto a stale checkout has a
    small running age and a large loaded-code age, and only the pair can say so."""
    drift = {"head": "abc1234", "population": ["sim-runner"], "stale_detail": {"sim-runner": ["x.py"]},
             "unresolved": {}, "vacuous": False}
    monkeypatch.setattr(dr, "session_hosting_units", lambda *a, **k: (frozenset(), None))
    monkeypatch.setattr(dr, "_unit_running_age_s", lambda unit, now=None: 4000.0)
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "_commit_epoch", lambda sha: 900.0)
    monkeypatch.setattr("background.boot_sha.read_boot_sha", lambda s: "deadbee")
    report = dr.daemon_deployment_report(drift=drift, now=5000.0)

    row = report["daemons"][0]
    for field in ("running_age_s", "loaded_code_age_s", "unincorporated_for_s", "modules_behind"):
        assert field in row, f"the one place does not carry {field}"
    assert row["running_age_s"] == 4000.0
    assert row["loaded_code_age_s"] == 4100.0
    assert report["summary"]["stale"] == 1 and report["summary"]["observed"] == 1


def test_the_report_is_json_serialisable_because_it_is_written_to_disk(monkeypatch):
    drift = {"head": "abc1234", "population": [], "stale_detail": {}, "unresolved": {},
             "vacuous": False}
    monkeypatch.setattr(dr, "session_hosting_units", lambda *a, **k: (frozenset({"u.service"}), None))
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "_commit_epoch", lambda sha: 900.0)
    json.dumps(dr.daemon_deployment_report(drift=drift, now=5000.0))


@pytest.mark.parametrize("seconds,expected", [(None, "?"), (30, "0m"), (5400, "1.5h"), (172800, "2.0d")])
def test_the_age_reads_as_a_person_would_say_it(seconds, expected):
    assert dr._hms(seconds) == expected


# ── the time column and the verdict column must have ONE subject ────────────────────────────────

def test_the_time_column_cannot_disagree_with_the_verdict(monkeypatch, tmp_path):
    """THE DEFECT THIS OWNS, live on 2026-09-04 in the reading the director ordered:

        deadmans-switch   behind 0m    5 changed module(s) it imports
        dispatcher        behind 2.7h  current

    The verdict counts imports differing from the WORKING TREE; the old time figure was HEAD's
    commit time minus the boot SHA's, whose subject is COMMITTED HISTORY. On a tree several lanes
    hold uncommitted work in, those never agree, so the column a reader takes for severity pointed
    the opposite way to the verdict beside it.

    MUTATION (the exact code deleted): restore `head_epoch - booted_epoch` and this fires on the
    green daemon, which then reports a positive time behind while holding nothing that changed.
    """
    (tmp_path / "old.py").write_text("x")
    os.utime(tmp_path / "old.py", (1000.0, 1000.0))
    drift = {"head": "abc1234", "unresolved": {}, "vacuous": False,
             "population": ["red-one", "green-one"],
             # SAME boot sha for both -- which is why the old figure was identical on every row and
             # per-daemon on none of them.
             "stale_detail": {"red-one": ["old.py"]}}
    monkeypatch.setattr(dr, "_REPO", tmp_path)
    monkeypatch.setattr(dr, "session_hosting_units", lambda *a, **k: (frozenset(), None))
    # RUNNING SINCE t=0, so old.py (mtime 1000) genuinely landed after this process started. The
    # fixture used to say 10.0, which described a process alive for ten seconds and behind on a
    # file written 4000s earlier -- impossible, and the state the restart loop was built on. The
    # assertions below are unchanged; only the world they run in is now one that can exist.
    monkeypatch.setattr(dr, "_unit_running_age_s", lambda unit, now=None: 5000.0)
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "_commit_epoch", lambda sha: 900.0)
    monkeypatch.setattr("background.boot_sha.read_boot_sha", lambda s: "deadbee")
    rows = {r["session"]: r for r in
            dr.daemon_deployment_report(drift=drift, now=5000.0)["daemons"]}

    assert rows["green-one"]["unincorporated_for_s"] == 0.0, (
        "a daemon holding nothing that changed reported time behind -- the column disagrees with "
        "its own verdict"
    )
    assert rows["red-one"]["unincorporated_for_s"] == 4000.0
    for row in rows.values():
        assert bool(row["unincorporated_for_s"]) == bool(row["modules_behind"]), (
            "the time column and the verdict column parted company on {}".format(row["session"])
        )


def test_the_time_behind_is_per_daemon_and_not_a_property_of_the_commit(tmp_path):
    """The old column gave eleven rows two distinct values, both properties of a SHA rather than of
    any process. MUTATION: return a constant and this fires -- two daemons booted at the same
    commit, holding different unincorporated code, must read differently."""
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "b.py").write_text("b")
    os.utime(tmp_path / "a.py", (1000.0, 1000.0))
    os.utime(tmp_path / "b.py", (4000.0, 4000.0))
    older = dr.unincorporated_for_s(["a.py"], now=5000.0, repo=tmp_path)
    newer = dr.unincorporated_for_s(["b.py"], now=5000.0, repo=tmp_path)
    assert older == 4000.0 and newer == 1000.0
    assert older != newer


def test_the_oldest_unincorporated_change_is_the_one_reported(tmp_path):
    """Not the newest and not the mean: the figure answers "how long has this daemon been running
    without code that is on the disk", and the honest answer is the longest such interval."""
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "b.py").write_text("b")
    os.utime(tmp_path / "a.py", (1000.0, 1000.0))
    os.utime(tmp_path / "b.py", (4900.0, 4900.0))
    assert dr.unincorporated_for_s(["a.py", "b.py"], now=5000.0, repo=tmp_path) == 4000.0


def test_the_publisher_reads_only_keys_this_report_actually_emits(monkeypatch):
    """THE DEFECT THIS OWNS, and it was live at HEAD for the minutes between two commits.

    The producer's field was renamed here; `tools/generate_proof_data.py::_deployment` and the page
    it feeds still asked for the old name. Nothing linked them, so both sides were green, both
    suites passed, and the published column rendered "?" on every one of eleven rows -- which is
    the exact symptom that started this repair. A rename across an artefact seam is invisible to
    every control that only looks at one side of it.

    The seam is a JSON file on disk, deliberately (a publishing tool that imports the producer
    drags the process reconciler onto its graph). The cost of a seam is that the compiler cannot
    see across it, so a control must. Read as TEXT, not imported, for the same reason.

    MUTATION: ask for any key the report does not emit and this fires.
    """
    source = (Path(dr.__file__).resolve().parents[1]
              / "tools" / "generate_proof_data.py").read_text()
    body = source.split("def _deployment(")[1].split("\ndef ")[0]
    asked = set(re.findall(r'r\.get\("([^"]+)"\)', body))
    assert asked, "no artefact keys found -- the control is reading the wrong function"

    drift = {"head": "abc1234", "population": ["sim-runner"], "unresolved": {}, "vacuous": False,
             "stale_detail": {"sim-runner": ["x.py"]}}
    monkeypatch.setattr(dr, "session_hosting_units", lambda *a, **k: (frozenset(), None))
    monkeypatch.setattr(dr, "_unit_running_age_s", lambda unit, now=None: 1.0)
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "_commit_epoch", lambda sha: 900.0)
    monkeypatch.setattr("background.boot_sha.read_boot_sha", lambda s: "deadbee")
    emitted = set(dr.daemon_deployment_report(drift=drift, now=5000.0)["daemons"][0])

    assert asked <= emitted, (
        "the publisher asks this artefact for {}, which it does not emit -- the page will render "
        "those columns empty on every row and both suites will stay green".format(
            sorted(asked - emitted))
    )


def test_every_state_of_the_time_column_is_reachable(tmp_path):
    """THE RULE THIS REPO PAID FOR THREE TIMES IN ONE AFTERNOON (restart_plan's defer branch):
    when a branch exists to be taken rarely, assert it CAN be taken before asserting what it does.

    Here the rare branch is the third state -- behind, but undatable. Without this leg a version
    that could only ever return 0.0 or a number would pass every other test in this block, and the
    undatable case would silently render as "0m", which is the fail-open answer.
    """
    (tmp_path / "there.py").write_text("x")
    os.utime(tmp_path / "there.py", (1000.0, 1000.0))
    nothing_behind = dr.unincorporated_for_s([], now=5000.0, repo=tmp_path)
    datable = dr.unincorporated_for_s(["there.py"], now=5000.0, repo=tmp_path)
    undatable = dr.unincorporated_for_s(["deleted.py"], now=5000.0, repo=tmp_path)

    assert nothing_behind == 0.0
    assert datable and datable > 0
    assert undatable is None, (
        "a daemon whose missing code is a DELETED file is behind and undatable; None prints '?' "
        "and 0.0 prints '0m', and only one of those is true"
    )
    assert len({nothing_behind, datable, undatable}) == 3


def test_a_change_already_on_disk_when_the_process_started_is_code_it_HAS(tmp_path):
    """THE DEFECT THIS OWNS: three daemons restarted every ten minutes for hours on 2026-09-04.

    `changed_paths_since` diffs the boot COMMIT against the WORKING TREE, so three modules carrying
    uncommitted edits 27h old marked six daemons stale. `restart_plan` restarts anything stale, and
    a restart stamps `boot_sha := HEAD` WITHOUT touching the working tree -- so the daemon was stale
    again the moment it came up. The remedy could not clear its own trigger.

    MUTATION: drop the mtime comparison and this fires. A file written before the process started is
    a file the process loaded.
    """
    (tmp_path / "long_uncommitted.py").write_text("x")
    os.utime(tmp_path / "long_uncommitted.py", (1000.0, 1000.0))
    kept, resolved = dr.unincorporated_since_start(
        ["long_uncommitted.py"], running_age_s=600.0, now=5000.0, repo=tmp_path)
    assert resolved and kept == [], (
        "a process that started at t=4400 was reported behind on a file written at t=1000, which "
        "is the loop: restarting cannot change either number"
    )


def test_a_change_that_landed_after_the_process_started_is_still_behind(tmp_path):
    """THE OTHER SIDE, and the one that stops the fix being a fail-open. MUTATION: return [] always
    and this fires. worker-seat-manager is the live instance -- up 10.8 days, holding a module
    rewritten 60h ago, and it must stay red when the other six go green."""
    (tmp_path / "landed_after.py").write_text("x")
    os.utime(tmp_path / "landed_after.py", (4800.0, 4800.0))
    kept, resolved = dr.unincorporated_since_start(
        ["landed_after.py"], running_age_s=600.0, now=5000.0, repo=tmp_path)
    assert resolved and kept == ["landed_after.py"]


def test_every_state_of_the_start_dating_is_reachable(tmp_path):
    """The partition, over one control rather than a leg per branch — a filter that dropped
    EVERYTHING would pass the first leg above and every other test in this block.

    Four states and each names a different world: nothing changed; changed but already loaded;
    changed after start; and undatable. The last two both fail CLOSED, and that is the property.
    """
    (tmp_path / "before.py").write_text("x")
    os.utime(tmp_path / "before.py", (1000.0, 1000.0))
    (tmp_path / "after.py").write_text("x")
    os.utime(tmp_path / "after.py", (4800.0, 4800.0))

    nothing = dr.unincorporated_since_start([], 600.0, now=5000.0, repo=tmp_path)
    already_had = dr.unincorporated_since_start(["before.py"], 600.0, now=5000.0, repo=tmp_path)
    genuinely = dr.unincorporated_since_start(["after.py"], 600.0, now=5000.0, repo=tmp_path)
    both = dr.unincorporated_since_start(
        ["before.py", "after.py"], 600.0, now=5000.0, repo=tmp_path)
    deleted = dr.unincorporated_since_start(["gone.py"], 600.0, now=5000.0, repo=tmp_path)
    undatable_start = dr.unincorporated_since_start(["before.py"], None, now=5000.0, repo=tmp_path)

    assert nothing == ([], True)
    assert already_had == ([], True)
    assert genuinely == (["after.py"], True)
    assert both == (["after.py"], True), "the mixed set must keep exactly the half it lacks"
    assert deleted == (["gone.py"], True), (
        "a change that will not stat is a DELETION -- undatable, and dropping it would silently "
        "shrink a staleness set, which is the fail-open this reading exists to stop"
    )
    assert undatable_start == (["before.py"], False), (
        "with no running age the process start cannot be dated, so nothing may be dropped; an "
        "undatable process is not a current one"
    )


def test_no_published_time_behind_can_exceed_the_rows_own_running_age(monkeypatch, tmp_path):
    """KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. At HEAD on 2026-09-04 six of eleven published
    rows broke this — up to 27 hours of 'time behind' on processes ten minutes old — which is
    impossible under the meaning the column claims ("the interval it has been running without
    this"). Once the set is dated from the process the bound holds by construction, so this control
    goes red if the subject ever drifts back off the process, whatever the numbers are that day.
    """
    (tmp_path / "old.py").write_text("x")
    os.utime(tmp_path / "old.py", (1000.0, 1000.0))
    (tmp_path / "recent.py").write_text("x")
    os.utime(tmp_path / "recent.py", (4900.0, 4900.0))
    drift = {"head": "abc1234", "unresolved": {}, "vacuous": False,
             "population": ["short-lived", "long-lived"],
             "stale_detail": {"short-lived": ["old.py"], "long-lived": ["old.py", "recent.py"]}}
    ages = {"short-lived.service": 600.0, "long-lived.service": 5000.0}
    monkeypatch.setattr(dr, "_REPO", tmp_path)
    monkeypatch.setattr(dr, "session_hosting_units", lambda *a, **k: (frozenset(), None))
    monkeypatch.setattr(dr, "_unit_running_age_s", lambda unit, now=None: ages[unit])
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "_commit_epoch", lambda sha: 900.0)
    monkeypatch.setattr("background.boot_sha.read_boot_sha", lambda s: "deadbee")
    rows = {r["session"]: r for r in
            dr.daemon_deployment_report(drift=drift, now=5000.0)["daemons"]}

    for row in rows.values():
        behind = row["unincorporated_for_s"]
        if isinstance(behind, (int, float)) and row["running_age_s"] is not None:
            assert behind <= row["running_age_s"], (
                "{} publishes {}s behind against a process alive for {}s -- the column is measuring "
                "a file's age, not this daemon's".format(
                    row["session"], behind, row["running_age_s"])
            )
    # NOT A CONSTANT-GREEN: the two rows must still differ, or the bound was bought by zeroing.
    assert rows["short-lived"]["modules_behind"] == 0
    assert rows["long-lived"]["modules_behind"] == 2
    assert rows["short-lived"]["predates_start"] == 1, (
        "what the dating removed must be published, or a staleness set shrinks silently"
    )


# ── never mid-work ──────────────────────────────────────────────────────────────────────────────

def _cgroup(tmp_path, monkeypatch, rel, pids):
    monkeypatch.setattr(dr, "_sh", lambda *a, **k: rel)
    d = tmp_path / rel.lstrip("/")
    d.mkdir(parents=True)
    (d / "cgroup.procs").write_text("".join(f"{p}\n" for p in pids))
    monkeypatch.setattr(dr, "_CGROUP_ROOT", tmp_path)


def test_a_daemon_with_a_job_in_flight_is_mid_work(tmp_path, monkeypatch):
    """MUTATION: drop the `len(pids) > 1` branch and this fires.

    `sim-runner` is a `while True` whose body is a TWELVE-minute simulation against a TEN-minute
    timer, so without this it would be killed before finishing every single time — forever — while
    the deployment step logged "restarted 9 units" and every surface called that healthy."""
    _cgroup(tmp_path, monkeypatch, "app.slice/sim-runner.service", [111, 222])
    busy, why = dr.unit_is_mid_work("sim-runner.service")
    assert busy and "in flight" in why


def test_a_daemon_at_rest_is_not_mid_work(tmp_path, monkeypatch):
    """THE NULL CONTROL, and the leg above is worthless without it. A guard that answered 'busy'
    for everything would pass that test and defer every daemon forever, which is the fail-closed
    direction and still a permanent no-op. Measured on the real box: nine of eleven daemons had
    exactly one process, so this branch is reachable."""
    _cgroup(tmp_path, monkeypatch, "app.slice/dispatcher.service", [111])
    busy, why = dr.unit_is_mid_work("dispatcher.service")
    assert not busy and why is None


def test_an_unreadable_cgroup_is_mid_work(tmp_path, monkeypatch):
    """An unavailable check is a FAILED check. 'I could not tell' must not authorise a restart."""
    monkeypatch.setattr(dr, "_sh", lambda *a, **k: "app.slice/ghost.service")
    monkeypatch.setattr(dr, "_CGROUP_ROOT", tmp_path)
    busy, why = dr.unit_is_mid_work("ghost.service")
    assert busy and "unreadable" in why


def test_a_unit_whose_cgroup_path_is_unknown_is_mid_work(monkeypatch):
    monkeypatch.setattr(dr, "_sh", lambda *a, **k: None)
    busy, why = dr.unit_is_mid_work("ghost.service")
    assert busy and "could not be read" in why


def test_the_plan_holds_a_mid_work_daemon_with_its_reason():
    """MUTATION: drop the mid_work branch from `restart_plan` and this fires."""
    row = _row("sim-runner", mid_work=True, mid_work_reason="2 process(es) in the cgroup")
    plan = dr.restart_plan(_report([row]))
    assert plan["restart"] == [] and plan["defer"] == []
    assert "mid-work" in plan["hold"]["sim-runner.service"]
    assert "2 process(es)" in plan["hold"]["sim-runner.service"]


# ── the age itself, not a stub of it ────────────────────────────────────────────────────────────

def test_the_running_age_is_the_monotonic_difference_and_carries_no_offset(monkeypatch):
    """MUTATION: add any offset to the returned age — or go back to parsing systemd's human
    timestamp — and this fires.

    THE BUG IT PINS, found by printing the figure at real inputs rather than by reasoning. The
    first version asked systemd for `ExecMainStartTimestamp`, a human string ending in "BST", and
    handed it to `date -d`. GNU date reads BST as BANGLADESH Standard Time (UTC+6), not British
    Summer Time (UTC+1), so every age was exactly 5 hours wrong: nine daemons restarted five
    MINUTES earlier were reported as having run 5.0 HOURS. Plausible, stable, and false.

    The report-level test cannot catch this — it stubs this function out. A figure that was
    explicitly ordered needs a control on the arithmetic that produces it, not on its presence.
    """
    monkeypatch.setattr(dr, "_sh", lambda *a, **k: "60000000")   # 60s since boot, in microseconds
    monkeypatch.setattr(dr, "_uptime_s", lambda: 3660.0)          # box up for 61 minutes
    assert dr._unit_running_age_s("any.service") == 3600.0        # exactly one hour, no offset


def test_an_unstarted_unit_has_no_running_age_rather_than_the_uptime(monkeypatch):
    """A unit systemd cannot date reports 0 monotonic. Subtracting it would return the BOX's
    uptime and read as a daemon that has run since boot — the most plausible wrong answer
    available."""
    monkeypatch.setattr(dr, "_sh", lambda *a, **k: "0")
    monkeypatch.setattr(dr, "_uptime_s", lambda: 3660.0)
    assert dr._unit_running_age_s("never-started.service") is None


def test_an_unreadable_uptime_gives_no_age_rather_than_a_plausible_one(monkeypatch):
    monkeypatch.setattr(dr, "_sh", lambda *a, **k: "60000000")
    monkeypatch.setattr(dr, "_uptime_s", lambda: None)
    assert dr._unit_running_age_s("any.service") is None


# ── every disposition must be REACHABLE ─────────────────────────────────────────────────────────

def test_a_session_host_with_a_job_in_flight_is_deferred_not_held():
    """MUTATION: test `mid_work` before `session_hosting` in `restart_plan` and this fires.

    THE THIRD INSTANCE OF ONE TRAP IN ONE AFTERNOON, and the reason the reachability control below
    exists. `mid_work` counts processes in the unit's cgroup, and a session host's RESTING state is
    already two — the tmux server and the seat. Tested first, it holds the host permanently and
    `defer` stays EMPTY on the only unit deferral exists for, while the log prints a plausible
    hold reason every ten minutes.

    A host's timing is decided at FIRE time by `unit_has_working_seat`, off the seat heartbeat,
    which is the only signal that distinguishes a working seat from an idle one."""
    row = _row("worker-seat-manager", session_hosting=True, mid_work=True,
               mid_work_reason="2 process(es) in the cgroup")
    plan = dr.restart_plan(_report([row]))
    assert plan["defer"] == ["worker-seat-manager.service"], (
        "the seat host was held rather than deferred, so the deferred restart can never fire: "
        + repr(plan["hold"])
    )


def test_every_disposition_is_reachable():
    """THE STRUCTURAL CONTROL, and it is worth more than any leg above.

    Three separate defects this afternoon all had the same shape: a branch that could never be
    taken, whose log read exactly like the mechanism working. Each was caught by hand, one at a
    time, after the previous fix. A partition with an unreachable outcome is not a partition — so
    this asserts that over a representative population EVERY outcome is produced, and it would have
    caught all three at once rather than none.

    MUTATION: make any branch unreachable — reorder the plan so `mid_work` precedes
    `session_hosting`, or restore the hosting test inside `unit_has_working_seat` — and the
    corresponding bucket empties, firing this."""
    rows = [
        _row("idle-and-stale"),                                     # -> restart
        _row("seat-host", session_hosting=True, mid_work=True),     # -> defer
        _row("busy", mid_work=True, mid_work_reason="2 in cgroup"),  # -> hold
        _row("current", stale=False),                                # -> hold
        _row("unknown", unresolved="unstamped"),                     # -> hold
    ]
    plan = dr.restart_plan(_report(rows), self_unit="deploy-restart.service")
    assert plan["restart"], "no input can reach RESTART -- the mechanism can never act"
    assert plan["defer"], "no input can reach DEFER -- the seat host would never be restarted"
    assert plan["hold"], "no input can reach HOLD -- nothing can ever be protected"
    assert plan["restart"] == ["idle-and-stale.service"]
    assert plan["defer"] == ["seat-host.service"]
    assert set(plan["hold"]) == {"busy.service", "current.service", "unknown.service"}


def test_the_turn_boundary_is_reachable_for_a_session_host(monkeypatch, tmp_path):
    """The companion at the FIRE-time end: a deferred unit must have some state in which it is not
    busy, or deferral is a permanent hold wearing a different word."""
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    hb = obs / ".seat_heartbeat.json"
    hb.write_text("{}")
    import os
    cold = os.stat(hb).st_mtime - (dr._SEAT_IDLE_S + 60)
    os.utime(hb, (cold, cold))
    monkeypatch.setattr(dr, "_REPO", tmp_path)
    monkeypatch.setattr(dr, "session_hosting_units",
                        lambda *a, **k: (frozenset({"worker-seat-manager.service"}), None))
    monkeypatch.setattr(dr, "units_holding_a_live_seat", lambda *a, **k: frozenset())
    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert not busy, "a session host has no state in which it is idle: " + why


def test_the_mtime_proxy_cannot_override_the_exact_content_answer(monkeypatch):
    """THE FINDING OF THE PREREGISTERED ARMS (2026-09-04, four arms over eleven daemons).

    Two lanes fixed the ten-minute restart loop two minutes apart and both mechanisms went live in
    one merge: CONTENT (`boot_sha.dirty_blobs` — what the daemon actually loaded) and MTIME
    (`unincorporated_since_start` — when the disk last changed). Both are REMOVAL filters, so
    composing them removes a path if EITHER removes it, and the pair is then no better at catching
    real staleness than MTIME alone. Measured: arm C (mtime only) equalled arm A (both) on every
    one of eleven rows.

    That is not a tie, because MTIME's false NEGATIVE is reachable here. `cp -p` preserves mtime,
    so content that genuinely changed can look untouched — and this session used `cp -p` a dozen
    times restoring files during mutation testing. Composing let the proxy override the exact
    answer in exactly the direction that leaves stale code serving.

    MUTATION: apply `unincorporated_since_start` unconditionally — the pre-finding composition —
    and this fires, because the mtime filter then drops a path the content stamp says is missing.
    """
    drift = {"head": "abc1234", "population": ["stamped"], "unresolved": {}, "vacuous": False,
             "stale_detail": {"stamped": ["changed_with_old_mtime.py"]}}
    monkeypatch.setattr(dr, "session_hosting_units", lambda *a, **k: (frozenset(), None))
    monkeypatch.setattr(dr, "_unit_running_age_s", lambda unit, now=None: 60.0)
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "_commit_epoch", lambda sha: 900.0)
    monkeypatch.setattr("background.boot_sha.read_boot_sha", lambda s: "deadbee")
    # the stamp CAN answer exactly: this path's content differs from what the daemon loaded
    monkeypatch.setattr("background.boot_sha.read_boot_blobs", lambda s: {"a.py": "hash"})
    # ...and the proxy would drop it, because `cp -p` left the mtime older than the process start
    monkeypatch.setattr(dr, "unincorporated_since_start", lambda paths, age, now, repo=None: ([], True))

    row = dr.daemon_deployment_report(drift=drift, now=5000.0)["daemons"][0]
    assert row["modules_behind"] == 1, (
        "the mtime proxy removed a path the content stamp says the daemon is missing — the pair is "
        "then no better than the proxy alone, in the direction that leaves stale code serving"
    )


def test_the_proxy_still_covers_a_daemon_whose_stamp_predates_the_content_field(monkeypatch):
    """THE NULL CONTROL, and the reason the proxy is kept rather than deleted. A stamp written
    before `dirty_blobs` existed cannot answer, and on the arms that was the difference between
    sim-runner reading 5 and reading 10. MUTATION: skip the dating whenever blobs are absent too
    and this fires."""
    drift = {"head": "abc1234", "population": ["unstamped-tree"], "unresolved": {}, "vacuous": False,
             "stale_detail": {"unstamped-tree": ["old.py", "new.py"]}}
    monkeypatch.setattr(dr, "session_hosting_units", lambda *a, **k: (frozenset(), None))
    monkeypatch.setattr(dr, "_unit_running_age_s", lambda unit, now=None: 60.0)
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
    monkeypatch.setattr(dr, "_commit_epoch", lambda sha: 900.0)
    monkeypatch.setattr("background.boot_sha.read_boot_sha", lambda s: "deadbee")
    monkeypatch.setattr("background.boot_sha.read_boot_blobs", lambda s: None)  # cannot answer
    monkeypatch.setattr(dr, "unincorporated_since_start",
                        lambda paths, age, now, repo=None: (["new.py"], True))

    row = dr.daemon_deployment_report(drift=drift, now=5000.0)["daemons"][0]
    assert row["modules_behind"] == 1 and row["predates_start"] == 1, (
        "the proxy was skipped for a daemon whose stamp cannot answer, which is the whole loop back"
    )
