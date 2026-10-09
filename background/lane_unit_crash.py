"""A lane unit that crashes twice running is seen, and in one narrow shape repaired.

`worker-tick` and `seat-executor` are TIMER units, not daemons, so `declared_daemon_health` never
counts them: it asks whether a long-running process is on the box and when it last wrote, and a
oneshot that dies in 25 seconds every ten minutes is neither absent nor quiet. On 2026-10-09 both
died with the same `AttributeError` on every run from 09:05 to about 14:50 UTC. The orienting seat
diagnosed it at 11:22 and filed the fix as focus one -- for the two lanes that were crashing, so
nobody could act on it, and the director stopped his own review to apply it by hand
(`docs/staging/console/SEAT_REPLY_2026-10-09.md`, 13:57Z).

TWO LEGS, AND THE SECOND IS DELIBERATELY NARROW.

DETECT. A RUN is one systemd invocation, grouped by its invocation id, and it is FINISHED when
systemd has logged the start job's result -- `JOB_RESULT`, on its "Finished" or "Failed to start"
line. NOT the exit status: systemd logs `EXIT_STATUS` only when the main process FAILS, so a reader
keyed to it sees no clean run at all and reads a recovered lane as still crashing. That was this
module's first draft, refuted on the live journal the hour it was written. A run CRASHED when its
job result is not `done` and the service's own output in that invocation holds a Python traceback. Two consecutive crashes are
the two newest finished runs both crashing -- the one that is running now is not finished and is not
read. The seat brief names it and NTFY fires once per streak, keyed to the streak's first run.

REPAIR. Only when both tracebacks end in the SAME exception line, that exception is an ImportError
(or ModuleNotFoundError) or an AttributeError, and the innermost frame's file is a shared-tree
working copy that is tracked and differs from HEAD. That is exactly the 10-09 shape: a caller edited
in place, still calling a name only an uncommitted copy of another file had defined. The copy goes
to `refs/preserved/refresh-to-head/<slug>` through `refresh_to_head.preserve`, whose `-S` recovery
route is proved before anything is written, and HEAD's bytes go over it. EVERY OTHER CAUSE IS HELD
for a person and the hold says why: a KeyError or a crash in a file that matches HEAD is a bug in
committed code, and writing HEAD over it fixes nothing.

It rides `reconcile_watch` (every five minutes) rather than either lane, because a repair that ran
inside the unit it repairs would die with it.

A HOLD WAKES THE INTERACTIVE SESSION, BY A WAITER IT ARMED ITSELF. A held crash is one only a
person can fix, and the person who can is the interactive session -- which on 10-09 nothing reached.
Nothing may type into its pane (`tmux_relay`, banned 2026-07-15), so the delivery is a pull: the
session runs `--wait-held` as a background command, and when a held streak appears the command
exits and Claude Code re-invokes the session with its output. Each streak wakes it once.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

#: The lane units: timer-driven oneshots that do the autonomous work. The daemons are counted by
#: `delivery_seat.declared_daemon_health`; these were counted by nothing.
LANE_UNITS = ("worker-tick", "seat-executor")

#: The exceptions a stale working copy produces when one half of an edit is gone. Anything else is
#: not evidence that HEAD's copy would run, so it is held.
REPAIRABLE = ("ImportError", "ModuleNotFoundError", "AttributeError")

#: Journal lines read per unit. Each 10-09 crashed run wrote about 25; a run that spawns a model
#: turn writes more. Fewer than two finished runs in the window is reported, never read as clean.
JOURNAL_LINES = 3000

STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".lane_unit_crash.json"

#: The held streaks the interactive session has already been woken for, as `unit:streak_from`.
WOKEN_FILE = PROJECT_DIR / "docs" / "observability" / ".lane_unit_crash_woken.json"

_FRAME = re.compile(r'^\s+File "([^"]+)", line \d+, in ')


def _journal(unit: str, lines: int = JOURNAL_LINES) -> list[dict] | None:
    """The unit's journal as entries, or `None` when it could not be asked."""
    try:
        proc = subprocess.run(
            ["journalctl", "--user", "-u", "{}.service".format(unit), "-n", str(lines),
             "-o", "json", "--no-pager"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    out = []
    for line in (proc.stdout or "").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def _invocation(entry: dict) -> str | None:
    """The run an entry belongs to. The service's own lines carry `_SYSTEMD_INVOCATION_ID`;
    systemd's lines ABOUT the run (its exit status) carry `USER_INVOCATION_ID`."""
    return (entry.get("_SYSTEMD_INVOCATION_ID") or entry.get("USER_INVOCATION_ID")
            or entry.get("INVOCATION_ID"))


def _traceback(messages: list[str]) -> dict | None:
    """The LAST traceback in a run: its exception line and its innermost real file."""
    starts = [i for i, m in enumerate(messages) if m.startswith("Traceback (most recent call last)")]
    if not starts:
        return None
    frames, exc = [], None
    for msg in messages[starts[-1] + 1:]:
        match = _FRAME.match(msg)
        if match:
            frames.append(match.group(1))
        elif msg[:1].isspace():
            continue
        else:
            exc = msg.strip()
            break
    real = [f for f in frames if not f.startswith("<")]
    return {"exception": exc or "", "frame": real[-1] if real else None}


def runs(entries: list[dict]) -> list[dict]:
    """Finished runs, oldest first. A run with no job-result line is still going; it is not read."""
    order, msgs, status = [], {}, {}
    for entry in entries:
        inv = _invocation(entry)
        if not inv:
            continue
        if inv not in msgs:
            order.append(inv)
            msgs[inv] = []
        if entry.get("JOB_TYPE") == "start" and "JOB_RESULT" in entry:
            status[inv] = str(entry["JOB_RESULT"])
        elif entry.get("_SYSTEMD_INVOCATION_ID"):
            message = entry.get("MESSAGE")
            if isinstance(message, str):
                msgs[inv].append(message)
    out = []
    for inv in order:
        if inv not in status:
            continue
        tb = _traceback(msgs[inv])
        out.append({"invocation": inv, "job_result": status[inv],
                    "crashed": status[inv] != "done" and tb is not None,
                    "exception": tb["exception"] if tb else "",
                    "frame": tb["frame"] if tb else None})
    return out


def reading(unit: str, entries: list[dict] | None = None) -> dict:
    """Did the unit's two newest finished runs both crash? `available: False` names why not."""
    if entries is None:
        entries = _journal(unit)
    if entries is None:
        return {"unit": unit, "available": False, "why": "journalctl could not be asked"}
    finished = runs(entries)
    if len(finished) < 2:
        return {"unit": unit, "available": False,
                "why": "{} finished run(s) in the newest {} journal lines".format(
                    len(finished), JOURNAL_LINES)}
    last_two = finished[-2:]
    return {"unit": unit, "available": True,
            "crashed_twice": all(r["crashed"] for r in last_two),
            "runs": last_two,
            # The streak's first run: the oldest crashed run with no clean run after it.
            "streak_from": next((r["invocation"] for r in _streak(finished)), None)}


def _streak(finished: list[dict]) -> list[dict]:
    tail = []
    for run in reversed(finished):
        if not run["crashed"]:
            break
        tail.append(run)
    return list(reversed(tail))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, check=False)


def plan(read: dict, root: Path) -> dict:
    """`restore` with the repo path, or `hold` with the reason. Never both."""
    if not read.get("available") or not read.get("crashed_twice"):
        return {"action": "none"}
    first, second = read["runs"]
    exc = second["exception"]
    if first["exception"] != exc:
        return {"action": "hold", "why": "the two tracebacks end differently ({!r} then {!r})".format(
            first["exception"], exc)}
    kind = exc.split(":", 1)[0].strip()
    if kind not in REPAIRABLE:
        return {"action": "hold", "why": "{} is not an import or attribute error, so HEAD's copy "
                "is no evidence of a fix".format(kind or "an unparsed exception")}
    frame = second["frame"]
    if not frame or first["frame"] != frame:
        return {"action": "hold", "why": "the failing frame is not the same file in both runs"}
    try:
        rel = Path(frame).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return {"action": "hold", "why": "the failing frame {} is outside the shared tree".format(
            frame)}
    head = _git(root, "show", "HEAD:{}".format(rel))
    if head.returncode != 0:
        return {"action": "hold", "why": "{} is not tracked at HEAD".format(rel)}
    try:
        work = (root / rel).read_bytes()
    except OSError as exc_:
        return {"action": "hold", "why": "{} could not be read ({})".format(rel, exc_)}
    if work == head.stdout:
        return {"action": "hold", "why": "{} already matches HEAD, so the fault is in committed "
                "code".format(rel)}
    return {"action": "restore", "path": rel, "exception": exc}


def restore(root: Path, rel: str, unit: str, streak_from: str) -> str:
    """Preserve the copy to a ref, prove it is recoverable, write HEAD. Returns the recovery line.
    Raises before writing anything if the preservation cannot be proved."""
    from tools.refresh_to_head import (
        _blob_bytes,
        _clear_index_entry,
        _probe,
        _staged_paths,
        preserve,
        verify_recoverable,
    )
    work = (root / rel).read_bytes()
    slug = "lane-unit-crash-{}-{}".format(unit, streak_from[:12])
    ref, commit = preserve(root, [rel], slug, (
        "preserved {}'s working copy before lane_unit_crash restored HEAD\n\n"
        "{} crashed on two consecutive runs with the same import/attribute error whose innermost "
        "frame was this file, and this copy differed from HEAD. This commit is on no branch; it "
        "exists so the bytes are findable.".format(rel, unit)))
    route = verify_recoverable(root, commit, rel, work, _probe(root, rel, work))
    staged = rel in _staged_paths(root)
    (root / rel).write_bytes(_blob_bytes(root, "HEAD", rel))
    if staged:
        _clear_index_entry(root, rel)
    return "{} preserved as {} ({}); recover with: {}".format(rel, ref, commit[:9], route)


def _load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}


def _save_state(state: dict) -> None:
    try:
        from background.live_ledger_guard import guard_live_ledger_write
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        guard_live_ledger_write(STATE_FILE, writer="lane_unit_crash._save_state").write_text(
            json.dumps(state, indent=1))
    except OSError:
        pass


def check(root: Path | None = None, journal=None, notify=None, state: dict | None = None,
          now: datetime | None = None) -> list[str]:
    """One pass over every lane unit: page once per streak, repair or hold. Returns what it did."""
    if root is None:
        from background.seat_continuation import shared_tree_dir
        root = shared_tree_dir(PROJECT_DIR)
    persist = state is None
    state = _load_state() if state is None else state
    now = now or datetime.now(timezone.utc)
    done = []
    for unit in LANE_UNITS:
        read = reading(unit, None if journal is None else journal(unit))
        if not read.get("available") or not read["crashed_twice"]:
            continue
        key = read["streak_from"]
        if state.get(unit, {}).get("streak_from") == key:
            continue
        step = plan(read, root)
        exc = read["runs"][-1]["exception"]
        if step["action"] == "restore":
            try:
                outcome = "REPAIRED: " + restore(root, step["path"], unit, key)
            except Exception as err:  # noqa: BLE001 -- a refused preservation is a hold
                outcome = "HELD for a person: the preservation refused ({})".format(err)
        else:
            outcome = "HELD for a person: " + step["why"]
        text = ("{} ended its last two runs with the same traceback: {}\n{}".format(
            unit, exc, outcome))
        if notify is None:
            from background.notify import notify as notify
        notify(text, kind="real_alarm", headers={"X-Tags": "rotating_light",
                                                 "X-Priority": "high"})
        state[unit] = {"streak_from": key, "at": now.isoformat(timespec="seconds"),
                       "exception": exc, "outcome": outcome}
        done.append(text)
    if persist and done:
        _save_state(state)
    return done


def brief_sentence(readings: list[dict] | None = None, state: dict | None = None) -> str:
    """The seat brief's line. Empty when no lane unit's last two runs both crashed."""
    if readings is None:
        readings = [reading(unit) for unit in LANE_UNITS]
    state = _load_state() if state is None else state
    crashed = [r for r in readings if r.get("available") and r.get("crashed_twice")]
    blind = [r for r in readings if not r.get("available")]
    out = ""
    if crashed:
        out += ("\n\n{} LANE UNIT(S) CRASHED ON BOTH OF THEIR LAST TWO RUNS. These are the lanes "
                "that carry out focus items, so a fix filed as a focus item will not run:\n".format(
                    len(crashed))
                + "\n".join("  {:<14} {}{}".format(
                    r["unit"], r["runs"][-1]["exception"],
                    "\n                 " + state[r["unit"]]["outcome"]
                    if state.get(r["unit"], {}).get("streak_from") == r["streak_from"] else
                    "\n                 not yet acted on by reconcile_watch")
                    for r in crashed) + "\n")
    if blind:
        out += "\n\nLANE UNIT CRASH READING UNAVAILABLE for {} -- which is NOT a clean reading.".format(
            "; ".join("{} ({})".format(r["unit"], r["why"]) for r in blind))
    return out


def unanswered_holds(state: dict, woken: list[str]) -> list[str]:
    """`unit:streak_from` of every held streak no session has yet been woken for."""
    return ["{}:{}".format(unit, row.get("streak_from")) for unit, row in sorted(state.items())
            if str(row.get("outcome", "")).startswith("HELD")
            and "{}:{}".format(unit, row.get("streak_from")) not in woken]


def _read_json(path: Path, empty):
    """Missing is the ordinary no-crash-yet state; a file that cannot be parsed is NOT quiet."""
    from tools.wait_for import ProbeUnreadable
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return empty
    except (OSError, ValueError) as err:
        raise ProbeUnreadable("{} could not be read ({})".format(path.name, err)) from err


def wait_held(deadline_s: float, state_path: Path | None = None, woken_path: Path | None = None,
              emit=print, **wait_kw) -> int:
    """Block until a held lane crash this session has not been woken for exists, then say it and
    exit 0. A hold already present when armed is delivered at once. 1 = deadline, re-arm;
    3 = the record could not be read, which is said rather than read as quiet."""
    from tools.wait_for import DEADLINE, wait
    state_path = STATE_FILE if state_path is None else state_path
    woken_path = WOKEN_FILE if woken_path is None else woken_path
    found: list[str] = []

    def probe() -> tuple[bool, str]:
        # `present` is the QUIET, so its ending is wait()'s FINISHED and a hold at arm time is
        # its NEVER_STARTED; both are the delivery.
        found[:] = unanswered_holds(_read_json(state_path, {}), _read_json(woken_path, []))
        return not found, "held: " + ", ".join(found) if found else "no lane crash is held"

    out = wait("a lane unit crash held for a person", deadline_s, probe, emit=emit, **wait_kw)
    if out["verdict"] == DEADLINE:
        return 1
    if not found:
        emit("LANE CRASH RECORD UNREADABLE -- cannot tell whether a lane is held: " + out["detail"])
        return 3
    state = _read_json(state_path, {})
    for key in found:
        unit = key.split(":", 1)[0]
        emit("\nLANE UNIT CRASH HELD FOR A PERSON -- {}: {}\n  {}".format(
            unit, state[unit].get("exception", ""), state[unit].get("outcome", "")))
    emit("\nThese are the lanes that carry out focus items, so a fix filed as one will not run. "
         "Read `journalctl --user -u <unit>.service`, fix it, and re-arm this waiter.")
    woken = _read_json(woken_path, []) + found
    woken_path.parent.mkdir(parents=True, exist_ok=True)
    from background.live_ledger_guard import guard_live_ledger_write
    guard_live_ledger_write(woken_path, writer="lane_unit_crash.wait_held").write_text(
        json.dumps(woken, indent=1))
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wait-held", action="store_true",
                        help="block until a crash is held for a person; run it in the background")
    parser.add_argument("--deadline", type=float, default=None,
                        help="seconds; required with --wait-held (tools/wait_for's ceiling)")
    args = parser.parse_args(argv)
    if args.wait_held:
        if args.deadline is None:
            parser.error("--wait-held needs --deadline: a waiter names its subject and its end")
        return wait_held(args.deadline)
    for unit in LANE_UNITS:
        print(json.dumps(reading(unit), indent=1))
    print(brief_sentence() or "no lane unit crashed on both of its last two runs")
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/lane_unit_crash.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("lane_unit_crash")
    raise SystemExit(main())
