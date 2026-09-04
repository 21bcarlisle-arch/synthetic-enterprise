"""THE DEFECT: a daemon holding changed code kept serving, because nothing performed G-D2.

Every leg here is about the ACT half of deployment, and every one of them is a way the act could
kill a live seat or refuse forever. The partition is the whole safety argument, so it is tested as a
partition — each unit lands in exactly one of restart / defer / hold, and hold always carries a
reason.

The plan is PURE and the restarter is INJECTABLE, so nothing here touches a real daemon.
"""
from __future__ import annotations

import json

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
    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert busy and "heartbeat moved" in why


def test_an_unreadable_heartbeat_reads_as_busy(monkeypatch, tmp_path):
    """MUTATION: treat an unreadable heartbeat as idle and this fires. 'I could not tell' must
    never authorise a restart that costs a turn."""
    monkeypatch.setattr(dr, "_REPO", tmp_path)  # no heartbeat file exists under here
    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert busy and "unreadable" in why


def test_a_quiet_unit_with_a_cold_heartbeat_is_a_turn_boundary(monkeypatch, tmp_path):
    """The only path that lets a session host restart. Both signals must say idle."""
    monkeypatch.setattr(dr, "unit_is_mid_work", lambda unit: (False, None))
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
    assert "heartbeat is" in why


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
    for field in ("running_age_s", "loaded_code_age_s", "behind_s", "modules_behind"):
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
    busy, why = dr.unit_has_working_seat("worker-seat-manager.service")
    assert not busy, "a session host has no state in which it is idle: " + why
