"""A landing started inside a bounded executor turn runs in a unit of its own, so the turn's teardown
cannot kill it.

THE DEFECT. `seat-executor.service` is `Type=oneshot` with `KillMode=control-group`: when the turn
returns, systemd SIGKILLs everything left in its cgroup. A `surgical_land` takes 10-30 minutes of
gates, so one started late in a 5400 s turn is still running at teardown and dies there. It happened
twice on 22 Nov, and `doomed_at_teardown` logged each one by name the moment before the kill:

  * 01:10Z and 02:45Z, the GSOP turn: `tools.surgical_land --drops simulation/gain_registration.py`
    (pids 2309122, 3176409), killed mid-pre-commit. The work was redone and landed as 20a58061f.
  * 07:15Z, the reg 6C turn: pid 945604, killed mid-pre-commit; 08:56Z, its retry (pid 2268653),
    the same way. Five turns in a row that day ran to 5400 s and landed nothing.

THE ROUTE. `tools/surgical_land.main` calls `hand_off` before it gates anything. Outside an executor
turn (`SE_SEAT_EXECUTOR` unset) it returns None and nothing changes. Inside one, it re-runs the same
argv in a transient `longjob-land-*` unit through `background/launch_long_job` (the one launcher:
`systemd_run_argv`, `verify_detached`, and a liveness record that `holds` the worktree, so the next
turn's salvage-and-reset leaves it alone -- see `seat_executor.worktree_is_live`), then FOLLOWS the
unit and returns its exit status. The turn sees the landing's output exactly as before; if the turn
is killed while following, the landing carries on. When the landing succeeds and the executor named
the claim (`SE_WORK_ID`), the unit also promotes it, because a landed commit that never reaches
origin is lost at the next turn's reset just as surely as a killed one. A promotion that loses the
race to a moved origin is re-landed and promoted again inside the same unit (`promote_until_landed`),
so one landing is one register row whose exit says whether its content reached origin. When the
turn set `SE_LANDED_SIGNAL`, the unit then writes the landed sha to that file, so a continuation held
on this landing is released even when the turn that armed it has already ended.

IF THE HAND-OFF CANNOT BE MADE (no systemd, a refusal), the landing runs in place only when the turn
has longer left than `LANDING_WINDOW_SECONDS`. Inside that window it is REFUSED BY NAME and the
diff is saved to a `refs/salvage/bounded-landing/*` ref, so the work outlives the refusal.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

#: Set by `seat_executor.run_once` on the turn's environment.
TURN_ENV = "SE_SEAT_EXECUTOR"
DEADLINE_ENV = "SE_TURN_DEADLINE"
WORK_ID_ENV = "SE_WORK_ID"
#: Set by a TURN that holds a continuation on its own landing (`DO NOT DRAW BEFORE <path> EXISTS`):
#: an absolute path the landing unit writes the landed sha to once the content is on origin. WHY
#: (2026-11-25): MSC increment A landed in its unit after its turn had ended, so nothing wrote the
#: file B was held on and B waited until a human wrote it by hand
#: (docs/staging/SEAT_FINDING_A_LANDING_FINISHED_BY_ITS_OWN_UNIT_HANDS_NOTHING_ON_2026-11-25.md).
#: The unit is the only process alive when such a landing finishes, so the unit writes it.
LANDED_SIGNAL_ENV = "SE_LANDED_SIGNAL"
#: Set inside the landing unit, so the landing it runs does not hand off a second time.
IN_UNIT_ENV = "SE_DETACHED_LANDING"

#: How long before the turn's kill a landing can no longer be trusted to finish in place. Not a
#: domain constant: `launch_long_job.LANDING_HOLD_SECONDS` records that "a landing's gate takes
#: 10-30 minutes", and the reg 6C landing (pid 945604) was still in pre-commit when the 07:15Z
#: teardown killed it. The top of that range is the window.
LANDING_WINDOW_SECONDS = 30 * 60

SALVAGE_REF_PREFIX = "refs/salvage/bounded-landing/"


def seconds_left(env=None, now: float | None = None) -> float | None:
    """Seconds until the turn is killed, or None when the executor did not say."""
    env = os.environ if env is None else env
    try:
        return float(env[DEADLINE_ENV]) - (time.time() if now is None else now)
    except (KeyError, ValueError):
        return None


def in_bounded_turn(env=None) -> bool:
    env = os.environ if env is None else env
    return env.get(TURN_ENV) == "1" and not env.get(IN_UNIT_ENV)


def save_salvage_ref(cwd: str, *, now: float | None = None, runner=subprocess.run) -> str | None:
    """Save the worktree's whole diff against HEAD (untracked files included) as a blob under a
    salvage ref, and return the ref. Uses a throwaway index, so the worktree's own index, HEAD and
    files are untouched. None when git refuses; the caller says so."""
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now))
    ref = f"{SALVAGE_REF_PREFIX}{Path(cwd).resolve().name}-{stamp}"
    index = Path("/tmp") / f"se-bounded-landing-index-{os.getpid()}"
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    try:
        for args in (["read-tree", "HEAD"], ["add", "--all", "--", "."]):
            if runner(["git", *args], cwd=cwd, env=env, capture_output=True,
                      timeout=300).returncode != 0:
                return None
        diff = runner(["git", "diff", "--cached", "--binary", "HEAD"], cwd=cwd, env=env,
                      capture_output=True, timeout=300)
        if diff.returncode != 0:
            return None
        blob = runner(["git", "hash-object", "-w", "--stdin"], cwd=cwd, input=diff.stdout,
                      capture_output=True, timeout=60)
        sha = (blob.stdout or b"").decode().strip()
        if blob.returncode != 0 or not sha:
            return None
        if runner(["git", "update-ref", ref, sha], cwd=cwd, capture_output=True,
                  timeout=60).returncode != 0:
            return None
        return ref
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        index.unlink(missing_ok=True)


def unit_environment(env, cwd: str, unit: str) -> dict:
    """What the landing unit is given of the turn's environment: its claim, and the file to write
    when it lands. A relative signal path is resolved against the worktree, which is the unit's own
    working directory too, so both name the same file."""
    unit_env = {IN_UNIT_ENV: unit, "PYTHONPATH": cwd}
    if env.get(WORK_ID_ENV):
        unit_env[WORK_ID_ENV] = env[WORK_ID_ENV]
    if env.get(LANDED_SIGNAL_ENV):
        unit_env[LANDED_SIGNAL_ENV] = str(Path(cwd, env[LANDED_SIGNAL_ENV]))
    return unit_env


def write_landed_signal(path: str, worktree: Path, *, runner=subprocess.run) -> str | None:
    """Write the worktree's HEAD sha (the commit the promotion put on origin) to `path`, whole or
    not at all: a temporary file renamed into place, so a waiter never reads a half-written file.
    Returns the sha, or None with the reason printed when it could not."""
    try:
        res = runner(["git", "rev-parse", "HEAD"], cwd=str(worktree), capture_output=True,
                     text=True, timeout=60)
        sha = (res.stdout or "").strip()
        if res.returncode != 0 or not sha:
            raise OSError(f"git rev-parse HEAD said rc={res.returncode}: {res.stderr!r}")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
        tmp.write_text(sha + "\n", encoding="utf-8")
        os.replace(tmp, target)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"LANDED, but the signal file {path} could NOT be written ({exc}); whatever is held "
              "on it waits until it is written by hand.", flush=True)
        return None
    print(f"landed signal written: {path} holds {sha[:9]}", flush=True)
    return sha


def _launch(argv: list, cwd: str, env, *, runner=subprocess.run) -> tuple[str, str]:
    """Start the landing in its own unit and record it. Returns `(unit, log)`; raises
    `launch_long_job.LaunchRefused` with the reason when it cannot."""
    from background import launch_liveness
    from background import launch_long_job as llj

    job = f"land-{Path(cwd).name}-{int(time.time())}"
    unit = llj.unit_name(job)
    log = f"/var/tmp/{unit}.log"
    unit_env = unit_environment(env, cwd, unit)
    # THE ARGV GOES BY FILE, NOT ON THE COMMAND LINE: systemd expands `${VAR}` in a unit's
    # ExecStart (measured on systemd 259), so a commit message would be rewritten in transit.
    argv_file = Path(f"/var/tmp/{unit}.argv.json")
    argv_file.write_text(json.dumps(list(argv)), encoding="utf-8")
    command = [sys.executable, "-m", "background.bounded_landing", "--run-file", str(argv_file)]
    run = llj.systemd_run_argv(unit, command, workdir=cwd, log=log, env=unit_env,
                               description=f"surgical_land from a bounded turn in {cwd} "
                                           "(background.bounded_landing)")
    try:
        res = runner(run, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise llj.LaunchRefused(f"`systemd-run` could not be run: {exc}") from exc
    if res.returncode != 0:
        raise llj.LaunchRefused(f"`systemd-run` refused with rc={res.returncode}: "
                                f"{(res.stderr or res.stdout or '').strip()[:300]}")
    detached, why = llj.verify_detached(unit, runner=runner)
    if detached is False:
        llj.stop(unit, runner=runner)
        raise llj.LaunchRefused(f"the detach did not hold: {why}")
    try:
        launch_liveness.record(job, unit, log, log=log, workdir=cwd, holds=[cwd])
    except Exception as exc:  # noqa: BLE001 - unrecorded must not stay running (launch_long_job)
        llj.stop(unit, runner=runner)
        raise llj.LaunchRefused(f"its liveness record could not be written ({exc})") from exc
    return unit, log


def _follow(unit: str, log: str, left: float | None, *, out) -> int:
    from background import launch_long_job as llj

    deadline = llj.FOLLOW_DEADLINE_SECONDS if left is None else max(left, 60.0)
    llj.follow_unit(unit, log, deadline_seconds=deadline, poll_seconds=10.0,
                    say=lambda line: print(line, file=out))
    try:
        print(Path(log).read_text(errors="replace"), file=out)
    except OSError as exc:
        print(f"(the landing's log {log} could not be read: {exc})", file=out)
    if llj.name_is_held(unit):
        print(f"the landing is STILL RUNNING in {unit}; it will finish and promote without this "
              "turn. Ask it: `systemctl --user status " + unit + "`.", file=out)
        return 75  # EX_TEMPFAIL: not a result yet
    fields = llj._show(unit, "ExecMainStatus") or {}
    try:
        return int(fields.get("ExecMainStatus") or 1)
    except ValueError:
        return 1


def hand_off(argv: list, *, cwd: str | None = None, env=None, launch=None, follow=None,
             salvage=None, now: float | None = None, out=None) -> int | None:
    """None: land in place. An int: the landing was handled here, and this is its exit status."""
    env = os.environ if env is None else env
    out = out or sys.stdout
    if not in_bounded_turn(env):
        return None
    cwd = str(Path(cwd or os.getcwd()).resolve())
    launch = launch or _launch
    follow = follow or _follow
    salvage = salvage or save_salvage_ref
    left = seconds_left(env, now)
    try:
        unit, log = launch(list(argv), cwd, env)
    except Exception as exc:  # noqa: BLE001 - every refusal is named below
        reason = str(exc) or repr(exc)
        if left is not None and left > LANDING_WINDOW_SECONDS:
            print(f"HAND-OFF FAILED ({reason}); {int(left)} s are left in this turn, more than the "
                  f"{LANDING_WINDOW_SECONDS} s landing window, so landing in place.", file=out)
            return None
        ref = salvage(cwd, now=now)
        when = "the executor did not say" if left is None else f"{int(left)} s"
        print(f"REFUSED: an in-cgroup surgical_land from a bounded turn with {when} left, inside "
              f"its {LANDING_WINDOW_SECONDS} s landing window, would be SIGKILLed at teardown, and "
              f"the hand-off to its own unit failed: {reason}. "
              + (f"The diff is saved: `git cat-file -p {ref} | git apply`." if ref else
                 "The diff could NOT be saved to a salvage ref; the next turn's fork_salvage "
                 "commit is the only copy."), file=out)
        return 3
    print(f"HANDED OFF: this landing runs in {unit}, outside this turn's cgroup, so the turn's "
          f"teardown cannot kill it. Log: {log}. Following it now.", file=out)
    return follow(unit, log, left, out=out)


def _run_in_unit(argv: list) -> int:
    """What the unit runs: the landing, then, if it landed and a claim was named, the promotion."""
    from tools import pre_commit_test_gate, surgical_land

    work_id = os.environ.get(WORK_ID_ENV)
    # ONE HOLD from the landing's base read to its push: a waiter that re-reads origin on
    # acquiring the lock then sees this push, not the base before it (see `promote_until_landed`).
    with pre_commit_test_gate.LandingGateLock("land and promote {}".format(work_id or "")):
        rc = surgical_land.main(argv)
        if rc == 0 and work_id:
            rc = promote_until_landed(Path("."), work_id)
        signal = os.environ.get(LANDED_SIGNAL_ENV)
        if rc == 0 and signal:
            write_landed_signal(signal, Path("."))
    return rc


def promote_until_landed(worktree: Path, work_id: str, *, attempts: int | None = None,
                         say=None) -> int:
    """Promote the worktree's landing; when origin moved under it, re-land on the new origin and
    promote again, INSIDE THIS JOB. 0 once the landing's content is on origin, 2 otherwise.

    WHY (2026-11-23). This used to promote once and exit 2 on a lost race. The next turn then ran
    `surgical_land --merge origin/main` as a new job, which could lose the race again: 01:14-01:21Z,
    land-se-seat-executor-1795394035, -1795396520 and -1795396769 were registered DIED with their
    work reaching origin through three merges that authored nothing (f68028b7f, 755536805,
    965a59053). Every orientation reads that register to decide whether work was lost.

    A lost race is answered by `surgical_land.replay`: the same change as one commit on the new
    origin, gated again with tests selected only on what both sides touched. A merge is made only
    when replay says it does not apply (a path both sides changed, a merge landing). Any other
    refusal, and a red gate above all, ends the job refused on the first sight of it.
    """
    from tools import pre_commit_test_gate
    from tools import promote_worktree_landing as pwl
    from tools import surgical_land as sl

    say = say or (lambda line: print(line, flush=True))
    attempts = attempts or sl.DEFAULT_ATTEMPTS
    # THE PUSH IS INSIDE THE LANDING-GATE LOCK (2026-11-25). The replay re-reads origin once it
    # holds the lock; that only helps if a holder's landing has REACHED origin before it lets go.
    # Released at its gate's end, c355db288 pushed seconds after the waiter had already read the
    # base it was about to move.
    with pre_commit_test_gate.LandingGateLock("promote {}".format(work_id)):
        return _promote_holding_the_lock(worktree, work_id, attempts, say, pwl, sl)


def _promote_holding_the_lock(worktree, work_id, attempts, say, pwl, sl) -> int:
    for attempt in range(1, attempts + 1):
        say(f"landed; promoting for {work_id} (attempt {attempt} of {attempts})")
        try:
            result = pwl.promote(worktree, work_id=work_id)
        except pwl.AlreadyOnOrigin as exc:
            say(f"ON ORIGIN already, so nothing was lost: {exc}")
            return 0
        except pwl.NotFastForward as exc:
            moved_to = exc.remote_head
            say(f"lost the promotion race: {exc}")
        except pwl.PromotionRefused as exc:
            say(f"promotion for {work_id} REFUSED: {exc}")
            return 2
        else:
            say(f"promoted {result['commit'][:9]} -> origin/main ({len(result['paths'])} "
                f"path(s), from {result['from'][:9]})")
            say(result["binding"])
            return 0
        if attempt == attempts:
            break
        try:
            sha = sl.replay(worktree, moved_to)
            on = sl._git_text(worktree, "rev-parse", sha + "^")
            say(f"replayed as {sha[:9]} on {on[:9]}")
        except sl.NothingToLand as exc:
            say(f"ON ORIGIN already, so nothing was lost: {exc}")
            return 0
        except sl.NotReplayable as why:
            say(f"not replayable ({why}); merging {moved_to[:9]} instead")
            try:
                sha = sl.land(worktree, [], f"merge origin/main: fold {moved_to[:9]} under the "
                              "landing that lost its promotion race", merge=moved_to)
                say(f"landed MERGE {sha[:9]}")
            except sl.LandingRefused as exc:
                say(f"the merge onto {moved_to[:9]} was REFUSED: {exc}")
                return 2
        except sl.LandingRefused as exc:
            say(f"the replay onto {moved_to[:9]} was REFUSED: {exc}")
            return 2
    say(f"promotion for {work_id} REFUSED: origin moved under all {attempts} attempt(s); the "
        "landing is committed in this worktree and not on origin")
    return 2


if __name__ == "__main__":  # pragma: no cover - the unit's entry point
    from background._seat import refuse_if_foreign  # seat guard, FIRST act

    refuse_if_foreign("bounded_landing")
    if len(sys.argv) == 3 and sys.argv[1] == "--run-file":
        raise SystemExit(_run_in_unit(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))))
    print("usage: python3 -m background.bounded_landing --run-file <json list of surgical_land argv>")
    raise SystemExit(2)
