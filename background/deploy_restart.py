"""G-D2, the deployment step: a daemon holding changed code is restarted, or it says why not.

WHAT THIS CLOSES. `OPERATIONAL_LAYER_DESIGN.md` §G-D2 has said since the operational layer was
designed that "the deployment step that lands a commit touching a daemon's code is the *same* step
that restarts that daemon (or marks it for restart). **There is no path where code lands and the old
process keeps serving silently.**" G-D1 and G-D3 were built — `boot_sha` stamps, `code_closure`
resolves what a daemon imports, `process_reconciler.loaded_code_drift` compares the two, and
`reconcile_watch` reports it every five minutes. The act-half was never built, so on 2026-09-04 ten
of eleven running daemons held changed modules, `sim-runner` 145 of them, and the report had been
saying so accurately for days with nothing acting on it.

THE AUTHORITY, and it is why this is a mechanism rather than a habit (director, 2026-09-04):

    "Restart any daemon that does not host the interactive session whenever its loaded code is
    behind disk. For the ones that do host the session, restart them at a turn boundary of your own
    choosing, never mid-work — and build that as a mechanism rather than remembering it."

THE PARTITION IS OBSERVED, NEVER DECLARED, and that is the whole safety argument. A manifest field
saying which unit hosts the seat is a declaration, and a declaration drifts — `process_reconciler`
carries the scar in its own comment, where a `launched_by` field excluded from the answer the exact
seven daemons that ran pre-cure code through a ten-hour wedge. So session-hosting is read from
`/proc`: any unit whose cgroup contains a live interactive-session process, with transient
`tmux-spawn-*.scope` children resolved up their parent chain to the owning service. On the machine
this was written on that returns TWO units, `worker-seat-manager.service` and
`worker-tick.service`, and only one of them was the one a person would have named.

FAIL CLOSED IN EVERY DIRECTION, because every failure here costs a live session:
  * session detection unresolved -> restart NOTHING and say why. An unreadable `/proc` must never
    read as "no session is hosted".
  * a daemon whose drift is UNRESOLVED (unstamped, closure-unknown, sha-unresolved) is NOT
    eligible. Unknown is not stale, and restarting on an unanswered question is acting on absence.
  * the caller's own unit is never restarted, whatever else is true.
  * a session-hosting unit is never restarted by `--apply`. It is DEFERRED, and the deferred
    restart fires only when that unit is observed to hold no working seat.

WHY NOT IN `reconcile_watch`. Because `tests/background/test_reconcile_watch.py::
test_the_drift_check_never_restarts_anything` pins that boundary deliberately — "a reconcile that
silently restarted things would be the accretion OPS1 forbids". Reporting and acting are different
guarantees (G-D3 and G-D2) and they get different units.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent

#: The one place a reader goes for "how old is what each daemon is running". Written by `--report`.
REPORT_PATH = _REPO / "docs" / "observability" / "daemon_deployment.json"
#: Units whose restart was deferred because they host a working seat, and the reason each time.
DEFERRED_PATH = _REPO / "docs" / "observability" / ".daemon_restart_deferred.json"

#: A process whose presence in a cgroup means "a person's session lives HERE" -- as opposed to
#: "a person is LOOKING at it from here", which is a different fact and must not be confused with
#: it. `tmux: server` OWNS the pane a seat runs in, so restarting its unit takes the session with
#: it even though the seat's own process sits in a transient scope; `claude` is the seat itself.
#:
#: `tmux: client` IS DELIBERATELY EXCLUDED, and it was in the first draft. A client is a VIEWER:
#: on this box one is attached over tailscale, and its parent chain resolves to
#: `tailscaled.service`, which would have marked that unit session-hosting. Harmless there because
#: tailscaled is not a managed daemon -- and the general case is not harmless at all. A viewer
#: attached from inside any managed unit would defer that daemon's restart FOREVER, on evidence
#: that nobody is working in it, only watching it. Narrowing a fail-closed set needs an argument,
#: and this is it: restarting a viewer's unit drops a connection, never a turn.
def _is_session_owner(comm: str) -> bool:
    return comm == "claude" or comm.startswith("tmux: server")
_SERVICE_RE = re.compile(r"([A-Za-z0-9@_.\-]+\.service)")
#: The user manager owns every user unit, so it appears in EVERY cgroup path and names nothing.
#: Matching it would mark every daemon session-hosting and freeze the whole mechanism to a no-op --
#: which is the safe direction, and still wrong, so it is excluded explicitly rather than by luck.
_USER_MANAGER_RE = re.compile(r"^user@\d+\.service$")


def _sh(*args: str, timeout: float = 10.0) -> str | None:
    try:
        return subprocess.check_output(args, text=True, timeout=timeout,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _unit_of_pid(pid: int | str, proc_root: Path | str = "/proc") -> str | None:
    """The LEAF service a pid runs under, or None.

    WHAT ACTUALLY DOES THE WORK HERE IS THE USER-MANAGER FILTER, not the `[-1]`, and the first
    version of this docstring claimed otherwise. `user@1000.service` appears in EVERY user cgroup
    path, so without the filter this returns one unit for every process on the box — which was the
    first draft's bug. With the filter, `[-1]` and `[0]` are EQUIVALENT on this machine: measured
    2026-09-04 across every live process, ZERO have more than one non-user-manager service in their
    cgroup path. `[-1]` is kept as defence against nesting that does not occur here, and it is
    recorded as unproven rather than dressed up as the guard — the mutation that swaps it survives,
    and that is an equivalence, not a hole."""
    try:
        cgroup = (Path(proc_root) / str(pid) / "cgroup").read_text()
    except Exception:
        return None
    found = [u for u in _SERVICE_RE.findall(cgroup) if not _USER_MANAGER_RE.match(u)]
    return found[-1] if found else None


def _ppid(pid: int | str, proc_root: Path | str = "/proc") -> int | None:
    try:
        for line in (Path(proc_root) / str(pid) / "status").read_text().splitlines():
            if line.startswith("PPid:"):
                return int(line.split()[1])
    except Exception:
        return None
    return None


def _resolve_owning_unit(pid: int, proc_root: Path | str = "/proc", hops: int = 8) -> str | None:
    """The unit a session process belongs to, walking up out of a transient scope.

    A seat's own `claude` process sits in `…/app.slice/tmux-spawn-<uuid>.scope`, whose leaf is a
    SCOPE and not a service — so asking its cgroup directly answers nothing. Its parent chain
    reaches the `tmux: server`, which IS in the owning service. Bounded hops: a cycle or an
    unreadable parent returns None, which the caller treats as unresolved rather than as absent.
    """
    seen = set()
    cur: int | None = pid
    while cur and cur > 1 and hops > 0 and cur not in seen:
        seen.add(cur)
        unit = _unit_of_pid(cur, proc_root)
        if unit:
            return unit
        cur = _ppid(cur, proc_root)
        hops -= 1
    return None


def session_hosting_units(proc_root: Path | str = "/proc") -> tuple[frozenset[str], str | None]:
    """`(units hosting a live interactive session, unresolved reason or None)`.

    OBSERVED. Every live process whose name carries a session marker is resolved to the service
    that owns it. A marker process that cannot be resolved makes the whole answer UNRESOLVED —
    not a smaller set — because a smaller set is exactly the shape that restarts a live seat.
    """
    root = Path(proc_root)
    units: set[str] = set()
    unresolved: list[str] = []
    try:
        entries = [p for p in root.iterdir() if p.name.isdigit()]
    except Exception as exc:  # noqa: BLE001 -- the reason is the payload
        return frozenset(), f"/proc is unreadable ({exc!r}), so no daemon may be restarted"
    for p in entries:
        try:
            comm = (p / "comm").read_text().strip()
        except Exception:
            continue  # the process exited between listing and reading; not a marker we missed
        if not _is_session_owner(comm):
            continue
        unit = _resolve_owning_unit(int(p.name), root)
        if unit:
            units.add(unit)
        else:
            unresolved.append(f"{p.name}:{comm}")
    if unresolved:
        return frozenset(units), (
            "a live session process could not be resolved to a unit ({}), so the "
            "session-hosting set is INCOMPLETE and nothing may be restarted".format(
                ", ".join(sorted(unresolved)[:6]))
        )
    return frozenset(units), None


def _uptime_s() -> float | None:
    try:
        return float(Path("/proc/uptime").read_text().split()[0])
    except Exception:
        return None


#: Where the kernel exposes each unit's process set. `systemctl show -p ControlGroup` gives the
#: path RELATIVE to this root, so the two are always joined rather than either being guessed.
_CGROUP_ROOT = Path("/sys/fs/cgroup")


def unit_is_mid_work(unit: str) -> tuple[bool, str | None]:
    """Is this daemon in the middle of a job? `(mid_work, reason)`, fail-closed on doubt.

    THE DEFECT THIS PREVENTS, and it was minutes from happening the first time this ran. The timer
    fires every ten minutes. `sim-runner` is a `while True` loop whose body is a TWELVE-minute
    simulation, so it is almost always mid-run — and a restart on a ten-minute cadence would have
    killed every run before it finished, forever, while the deployment step reported success. The
    company would have stopped producing runs entirely and every surface would have called it
    healthy, because "restarted 9 units" is exactly what working looks like from here.

    THE OBSERVABLE IS THE CGROUP, not a per-daemon declaration of what busy means. A managed daemon
    at rest is one process; a daemon running a job has spawned a child, and the kernel already
    knows. Measured 2026-09-04 across all eleven: nine had exactly one process, and the two that
    had two were `sim-runner` (mid-simulation) and `background-worker` (mid-tick). It
    discriminates, which is the only reason it is worth having — a signal that said "busy" for
    everything would defer forever and call it caution.

    This generalises the director's own rule rather than adding one. He said session hosts are
    restarted "at a turn boundary of your own choosing, never mid-work". Mid-work is the operative
    half and it is not special to seats.
    """
    rel = _sh("systemctl", "--user", "show", unit, "-p", "ControlGroup", "--value")
    if not rel:
        return True, "the unit's cgroup path could not be read, which is not evidence of idle"
    procs = _CGROUP_ROOT / rel.lstrip("/") / "cgroup.procs"
    try:
        pids = [line for line in procs.read_text().splitlines() if line.strip()]
    except Exception as exc:  # noqa: BLE001
        return True, "cgroup.procs is unreadable ({!r}), which is not evidence of idle".format(exc)
    if len(pids) > 1:
        return True, "{} process(es) in the cgroup, so a job is in flight".format(len(pids))
    return False, None


def _unit_running_age_s(unit: str, now: float | None = None) -> float | None:
    """How long this unit's main process has been up, in seconds. MONOTONIC, never parsed.

    THE BUG THIS REPLACES, caught 2026-09-04 the first time the figure was printed at real inputs.
    The first version asked systemd for `ExecMainStartTimestamp` -- a HUMAN string, "Fri 2026-09-04
    07:08:10 BST" -- and handed it to `date -d`. GNU date resolves the abbreviation **BST** to
    BANGLADESH Standard Time (UTC+6), not British Summer Time (UTC+1), so every age came out
    exactly 5 hours wrong: nine daemons that had restarted five MINUTES earlier were reported as
    having run for 5.0 HOURS. Plausible, stable, and false — and it would have been the headline
    figure on a page that exists to make staleness a reading.

    `ExecMainStartTimestampMonotonic` is microseconds since boot, against `/proc/uptime` in the
    same frame. No timezone, no locale, no abbreviation. Either both are readable or the age is
    None and prints as "?" — an unknown age must never be a plausible number.

    Same family as the marker-name lesson in this repo (UTC filenames against local mtimes
    manufacturing a phantom outage): whenever two clocks meet, at least one is lying about which
    frame it is in.
    """
    raw = _sh("systemctl", "--user", "show", unit, "-p",
              "ExecMainStartTimestampMonotonic", "--value")
    uptime = _uptime_s()
    if not raw or uptime is None:
        return None
    try:
        started_monotonic_s = float(raw) / 1_000_000.0
    except ValueError:
        return None
    if started_monotonic_s <= 0:
        return None  # never started, or systemd could not answer -- not "up since boot"
    return round(uptime - started_monotonic_s, 1)


def _commit_epoch(sha: str) -> float | None:
    raw = _sh("git", "-C", str(_REPO), "show", "-s", "--format=%ct", sha)
    try:
        return float(raw) if raw else None
    except ValueError:
        return None


def daemon_deployment_report(drift: dict | None = None, now: float | None = None) -> dict:
    """THE ONE PLACE: every daemon's loaded-code age beside its running age.

    The two are different questions and reading either alone misleads:
      * RUNNING AGE is how long this process has been up. Long is not wrong — the deadman must
        outlive what it watches.
      * LOADED-CODE AGE is how old the code it holds is, taken from the commit time of the SHA it
        booted from. A daemon that restarted an hour ago onto a stale checkout has a small running
        age and a large loaded-code age, and only this pair can tell you so.
      * BEHIND_S is the gap between them and disk: HEAD's commit time minus the boot SHA's. It is
        the number that makes "ten of eleven are stale" a reading rather than a discovery.

    `modules_behind` stays the ACTIONABLE figure and is not replaced by any of the above: a daemon
    can be days behind in time and hold nothing that changed, which is GREEN and must read as green.
    """
    from background import boot_sha
    from background.process_reconciler import evaluate_boot_sha_drift

    now = time.time() if now is None else now
    drift = evaluate_boot_sha_drift() if drift is None else drift
    hosting, hosting_unresolved = session_hosting_units()
    head = drift.get("head") or boot_sha.current_head()
    head_epoch = _commit_epoch(head) if head else None

    rows = []
    for session in sorted(drift.get("population") or []):
        unit = f"{session}.service"
        sha = boot_sha.read_boot_sha(session)
        running_age = _unit_running_age_s(unit, now)
        mid_work, mid_work_reason = unit_is_mid_work(unit)
        booted_epoch = _commit_epoch(sha) if sha else None
        changed = (drift.get("stale_detail") or {}).get(session) or []
        rows.append({
            "session": session,
            "unit": unit,
            "boot_sha": sha,
            "running_age_s": running_age,
            "loaded_code_age_s": None if booted_epoch is None else round(now - booted_epoch, 1),
            "behind_s": (None if (booted_epoch is None or head_epoch is None)
                         else round(head_epoch - booted_epoch, 1)),
            "modules_behind": len(changed),
            "modules": sorted(changed)[:20],
            "unresolved": (drift.get("unresolved") or {}).get(session),
            "session_hosting": unit in hosting,
            "mid_work": mid_work,
            "mid_work_reason": mid_work_reason,
            # A daemon holding nothing that changed is GREEN however old it is. Time behind is
            # context; the changed-module set is the verdict.
            "stale": bool(changed),
        })
    return {
        "generated_at_s": round(now, 1),
        "head": head,
        "head_commit_epoch": head_epoch,
        "session_hosting_units": sorted(hosting),
        "session_hosting_unresolved": hosting_unresolved,
        "vacuous": bool(drift.get("vacuous")),
        "daemons": rows,
        "summary": {
            "observed": len(rows),
            "stale": sum(1 for r in rows if r["stale"]),
            "unresolved": sum(1 for r in rows if r["unresolved"]),
            "session_hosting": sum(1 for r in rows if r["session_hosting"]),
            "mid_work": sum(1 for r in rows if r["mid_work"]),
        },
    }


def restart_plan(report: dict, self_unit: str | None = None) -> dict:
    """PURE, so it is mutation-testable without touching a real daemon.

    Returns `{"restart": [...], "defer": [...], "hold": {unit: reason}}`. Every unit in the report
    lands in exactly one of the three, and `hold` always carries a reason — a unit that is silently
    in none of them is the fail-open this partition exists to prevent.
    """
    restart: list[str] = []
    defer: list[str] = []
    hold: dict[str, str] = {}

    blocked = report.get("session_hosting_unresolved")
    for row in report.get("daemons") or []:
        unit = row["unit"]
        if row.get("unresolved"):
            hold[unit] = ("drift is unresolved ({}), and unknown is not stale -- restarting on an "
                          "unanswered question is acting on absence".format(row["unresolved"]))
        elif not row.get("stale"):
            hold[unit] = "holds no changed module it imports, so it is current whatever its age"
        elif row.get("mid_work"):
            hold[unit] = "a job is in flight ({}); never restart mid-work".format(
                row.get("mid_work_reason") or "reason unrecorded")
        elif self_unit and unit == self_unit:
            hold[unit] = "this is the caller's own unit; restarting it would kill the restarter"
        elif blocked:
            hold[unit] = "session-hosting set is unresolved ({}), so nothing is restarted".format(
                blocked)
        elif row.get("session_hosting"):
            defer.append(unit)
        else:
            restart.append(unit)
    return {"restart": sorted(restart), "defer": sorted(defer), "hold": hold}


def unit_has_working_seat(unit: str, drift_free: bool = False) -> tuple[bool, str]:
    """Is a seat MID-WORK in this unit right now? `(busy, reason)`, fail-closed on doubt.

    THE TURN BOUNDARY, observed rather than announced.

    CORRECTED WITHIN THE HOUR OF FIRST LANDING, and the first version could never have fired. It
    returned BUSY whenever the unit was in the session-hosting set — but being in that set is what
    makes a unit DEFERRED in the first place, and a hosted unit holds its tmux server and seat
    process permanently, between turns as much as during them. So the condition was always true,
    the deferred branch was unreachable, and `worker-seat-manager` would have sat stale forever
    while the log said "DEFERRED" every ten minutes. That is a permanent no-op wearing caution's
    clothes — the same shape this module refuses for viewers a few lines up, made by the same hand
    on the same afternoon.

    HOSTING AND BUSY ARE DIFFERENT FACTS. Hosting decides WHICH ROUTE a unit takes (defer, never
    restart-on-sight). Busy decides WHEN the deferred route fires. Conflating them collapses the
    second into the first.

    The signals that do mean busy, BUSY winning on any of them, because a lost turn costs more
    than one more ten-minute tick:
      * a job in flight in the unit's cgroup, and
      * a seat heartbeat younger than `_SEAT_IDLE_S`.
    An unreadable heartbeat reads as BUSY. "I could not tell" must never authorise the restart.

    THE HEARTBEAT IS THE RIGHT CLOCK, checked rather than assumed: it carries the live seat's own
    `session_id` and `tool_count` and is rewritten on every tool call, so it is warm exactly while
    a seat is working and cold exactly between turns. And a restart here is not a decapitation —
    `worker_seat.py` is a seed-by-id create-or-resume manager whose stated job is to bring the seat
    back, which is why this is a turn boundary rather than a shutdown.
    """
    # THE PROCESS COUNT IS USELESS FOR THIS UNIT CLASS, and using it was the SECOND version of
    # this bug (2026-09-04, corrected within the hour of the first correction). `unit_is_mid_work`
    # reads "more than one process in the cgroup", which is right for a daemon that spawns a child
    # per job -- and a session host's RESTING state is already two: the tmux server plus the seat
    # process, both of which persist between turns. So it returned busy forever, and the deferred
    # branch stayed exactly as unreachable as it had been when the test was `unit in hosting`.
    # I separated hosting from busy and then picked a busy signal whose baseline, for hosts, is
    # indistinguishable from work.
    #
    # FOR A SESSION HOST THE HEARTBEAT IS THE WHOLE ANSWER, and it is the one the director's phrase
    # points at: "never mid-work" means not mid-TURN. The heartbeat carries the live seat's own
    # session_id and is rewritten on every tool call, so it is warm exactly while a seat is working.
    # A job running in a host unit IS the seat's work, so the heartbeat covers it -- there is no
    # third thing for the process count to catch here.
    heartbeat = _REPO / "docs" / "observability" / ".seat_heartbeat.json"
    try:
        age = time.time() - heartbeat.stat().st_mtime
    except Exception as exc:  # noqa: BLE001
        return True, "the seat heartbeat is unreadable ({!r}), which is not evidence of idle".format(
            exc)
    if age < _SEAT_IDLE_S:
        return True, "the seat heartbeat moved {:.0f}s ago (< {:.0f}s)".format(age, _SEAT_IDLE_S)
    return False, "no session process in {} and the seat heartbeat is {:.0f}s old".format(unit, age)


#: How quiet a seat must be before its host may be restarted. Not a tuning knob dressed as a
#: constant: it is one supervisor grant interval, so a seat between turns clears it and a seat
#: thinking does not. Deliberately NOT sourced from the domain -- this is a property of this
#: machine's own scheduling, not of the world.
_SEAT_IDLE_S = 900.0


def apply_restarts(units, runner=None, self_unit: str | None = None) -> dict:
    """Restart each unit. `runner` is injectable so the tests never touch a real daemon."""
    run = runner or (lambda unit: _sh("systemctl", "--user", "restart", unit, timeout=60.0))
    done, failed = [], {}
    for unit in units:
        if self_unit and unit == self_unit:
            failed[unit] = "refused: this is the caller's own unit"
            continue
        result = run(unit)
        if result is None:
            failed[unit] = "systemctl restart returned no result"
        else:
            done.append(unit)
    return {"restarted": sorted(done), "failed": failed}


def _self_unit() -> str | None:
    return _resolve_owning_unit(os.getpid())


def main(argv: list[str]) -> int:
    report = daemon_deployment_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    plan = restart_plan(report, self_unit=_self_unit())

    s = report["summary"]
    print("head {}  observed {}  stale {}  unresolved {}  session-hosting {}".format(
        (report.get("head") or "?")[:9], s["observed"], s["stale"], s["unresolved"],
        s["session_hosting"]))
    for row in report["daemons"]:
        print("  {:22s} running {:>7s}  code {:>7s}  behind {:>7s}  modules {:>4d}{}{}".format(
            row["session"], _hms(row["running_age_s"]), _hms(row["loaded_code_age_s"]),
            _hms(row["behind_s"]), row["modules_behind"],
            ("  SEAT-HOST" if row["session_hosting"] else "")
            + ("  MID-WORK" if row["mid_work"] else ""),
            "  UNRESOLVED:" + row["unresolved"] if row["unresolved"] else ""))
    print("\nplan: restart {} | defer {} | hold {}".format(
        len(plan["restart"]), len(plan["defer"]), len(plan["hold"])))

    if "--apply" not in argv:
        print("(report only; pass --apply to perform the deployment step)")
        return 0

    outcome = apply_restarts(plan["restart"], self_unit=_self_unit())
    print("restarted: {}".format(", ".join(outcome["restarted"]) or "nothing"))
    for unit, why in sorted(outcome["failed"].items()):
        print("  FAILED {}: {}".format(unit, why))

    fired, still = [], {}
    for unit in plan["defer"]:
        busy, why = unit_has_working_seat(unit)
        if busy:
            still[unit] = why
            continue
        fired.append(unit)
    if fired:
        out = apply_restarts(fired, self_unit=_self_unit())
        outcome["restarted"].extend(out["restarted"])
        outcome["failed"].update(out["failed"])
        print("deferred units restarted at a turn boundary: {}".format(", ".join(out["restarted"])))
    DEFERRED_PATH.write_text(json.dumps(
        {"generated_at_s": report["generated_at_s"], "still_deferred": still}, indent=2,
        sort_keys=True) + "\n")
    for unit, why in sorted(still.items()):
        print("  DEFERRED {}: {}".format(unit, why))
    return 0


def _hms(seconds) -> str:
    if seconds is None:
        return "?"
    seconds = float(seconds)
    if seconds < 0:
        return "ahead"
    if seconds < 3600:
        return "{:.0f}m".format(seconds / 60)
    if seconds < 86400:
        return "{:.1f}h".format(seconds / 3600)
    return "{:.1f}d".format(seconds / 86400)


if __name__ == "__main__":
    import sys
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/deploy_restart.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("deploy_restart")
    raise SystemExit(main(sys.argv[1:]))
