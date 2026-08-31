"""The seat's work, continued without the director — in its own worktree, one bounded piece.

Director, 2026-08-31: *"the contradiction resolves onto me pressing enter. That has been the
biggest single drag on this project for a fortnight."* This is the piece that removes it.

WHAT IT IS, IN ONE LINE: a bounded `claude -p` session in an ISOLATED worktree that takes the next
claimed piece of seat work, lands it through `surgical_land`, promotes it through
`promote_worktree_landing`, and exits.

WHY THIS CAN EXIST NOW AND COULD NOT THIS MORNING
--------------------------------------------------
`background/delivery_seat.py` may not write code, and its own docstring gives the reason:
*"reverting would make this the second writer it exists not to be."* That reason was sound and is
now obsolete — not by argument, by two landings:

  * `178bf5a56` — `surgical_land` works from a `git worktree`. The probe also showed that a
    worktree land commits to the worktree's own DETACHED HEAD and leaves `main` untouched, so an
    isolated writer cannot move the shared branch by committing.
  * `tools/promote_worktree_landing` — integration is now a route with four refusals rather than a
    remembered sequence of git commands.

So this is not a second writer on the shared tree. **It writes no CODE there at all** — every edit
it makes is in the worktree, and the only shared-tree files it touches are its own two
observability files, `SHARED_TREE_WRITES` below.

That distinction is stated precisely because the first draft of this docstring claimed it never
wrote to the shared tree *at all*, which was false the moment it logged anything. A log and a pid
file cannot live in the worktree: `ensure_worktree` resets that tree at the start of every turn, so
a pid written there would vanish before the liveness check that needs it, and the log would lose
every turn's record. Both live in `docs/observability/`, the directory every daemon in this project
appends to by design, and `test_the_executor_writes_no_code_to_the_shared_tree` holds the list to
exactly those two.

THE FOUR REFUSALS BEFORE IT RUNS, and each is a way an unattended writer goes wrong
-----------------------------------------------------------------------------------
  * **another executor is running.** A pid file with a liveness check, not a bare lock — a lock
    left by a killed process is a machine that never runs again.
  * **an interactive seat is live AND the item was not handed over.** The heartbeat
    `.claude/hooks/stamp_seat_heartbeat.py` stamps on every tool call a session makes; if it is
    warm, a human is holding this seat. What that protects against is TWO WRITERS CHOOSING FROM
    THE SAME QUEUE, so the refusal asks about contention rather than presence. A re-derived
    `direction.unreachable_focus` item stands down: nobody gave it away and the live seat may be
    part-way through it with nothing claimed, which the path guard cannot see. **A continuation
    runs.** It is the seat writing down, deliberately and in full context, *"this piece is for
    whoever runs next"* — and the seat that wrote it is nearly always still alive, because it
    writes the handoff and then keeps working. Refusing on presence refuses every handoff there
    will ever be, which is what the first version of this module did.
  * **there is nothing to do.** No continuation and no unclaimed focus item is a legitimate
    resting state, recorded with its reason. `delivery_seat`'s skip rule already says why: running
    anyway produces a confident restatement, which reads downstream exactly like a decision.
  * **the work duplicates a live claim.** `seat_work_in_hand.refuse_if_duplicated`, keyed on
    PATHS rather than names, because the duplication that actually happened was two writers
    choosing the same work under two different labels.

WHAT IT STILL CANNOT DO, AND THESE ARE NOT HYPOTHETICAL
--------------------------------------------------------
It cannot tell whether its own work was any good. Every landing is gated and every finding filed,
and the director reviews retrospectively — that is a mitigation, not a proof, and an unattended
writer can be confidently wrong for hours. It also cannot see work another writer has decided on
but not yet claimed; the path guard closes the claimed case only.

**It is OFF by default.** `--once` runs a single bounded turn; nothing schedules it. Arming it is a
separate act, deliberately, so that the first unattended writer in this project's history is
started by someone rather than by a landing.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import delivery_lane, seat_work_in_hand  # noqa: E402
from background.live_ledger_guard import guard_live_ledger_write  # noqa: E402
from background.seat_work_in_hand import DuplicateWork  # noqa: E402
from tools.wait_for import pid_is_alive  # noqa: E402

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "seat-executor-log.md"
PID_FILE = PROJECT_DIR / "docs" / "observability" / ".seat_executor.pid"

#: EVERY path in the shared tree this module may write. The claim "it is not a second writer" rests
#: on this list being exhaustive and on both entries being observability rather than code, so the
#: list is the control's subject rather than a comment.
SHARED_TREE_WRITES = (LOG_FILE, PID_FILE)
WORKTREE = Path(os.environ.get("SE_EXECUTOR_WORKTREE", "/var/tmp/se-seat-executor"))

#: A bounded turn. Long enough for a real piece of work including a capture; short enough that a
#: wedged session frees the lane the same hour.
SESSION_TIMEOUT_SECONDS = 90 * 60

MODEL = os.environ.get("SE_EXECUTOR_MODEL", "claude-opus-5")


class StoodDown(Exception):
    """A named reason this tick is not running. Never an error — a recorded decision."""


def log(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    with LOG_FILE.open("a") as fh:
        fh.write(f"- [{stamp}] {message}\n")


def _interactive_seat_is_live(now: float | None = None) -> bool:
    """Is a human-driven seat session holding this seat right now?

    ASKS `seat_continuity.state()` RATHER THAN RE-DERIVING LIVENESS. The first draft of this
    carried its own `INTERACTIVE_SEAT_WARM_SECONDS` threshold, which would have been a second
    answer to a question that already has an owner — the exact defect the end-to-end canon names,
    written into the module built to remove it. `seat_continuity` already reasons about this
    properly: death needs TWO signals (a silent heartbeat AND no live interactive process), with a
    fail-silent escape at `CERTAINLY_DEAD_SECONDS` so a stopped machine cannot look alive forever.

    ABSENT reads as NOT LIVE, deliberately. The safe direction here is to RUN: standing down on a
    missing observability file would give this executor a way to be silently switched off by an
    unrelated deletion, which is the control-goes-quiet class rather than a safety property.
    """
    from background import seat_continuity

    try:
        return seat_continuity.state(now=now) == seat_continuity.LIVE
    except Exception:  # noqa: BLE001 - liveness must never take the tick down
        return False


def _is_handed_off(item: dict, now: float | None = None) -> bool:
    """Was this item written by the interactive seat as a continuation, rather than re-derived?

    ASKS `seat_continuation` RATHER THAN INFERRING FROM THE ITEM'S SHAPE. A continuation and a
    focus item are both `{"id": ..., "what": ...}` dicts by the time `next_item` returns one, so a
    duck-type check would be a second, weaker answer to a question the store already owns -- and
    the store applies the six-hour window, which is what stops a handoff from outliving the tree it
    reasoned about.

    Absent or unreadable store reads as NOT handed off, which is the conservative direction here:
    it costs a stand-down that says why, and the alternative would let an unreadable file license
    an unattended writer to run beside a live seat.
    """
    from background import seat_continuation

    try:
        return any(c.get("id") == item.get("id") for c in seat_continuation.live(now=now))
    except Exception:  # noqa: BLE001 - a handoff store must never cost the machine a tick
        return False


#: A worktree declares itself IN USE by dropping this file with the owning pid in it. Any writer
#: may write one -- the seat executor does it automatically, an interactive session working in a
#: worktree can do it by hand -- and the daemons that sweep worktrees read it.
OWNER_MARKER = ".se_worktree_owner"


def worktree_is_live(path) -> bool:
    """Is a writer's process still working inside this worktree?

    THE ONE HOME FOR THE QUESTION, and it is public because two daemons outside this module have to
    ask it. `background/fork_salvage` sweeps worktrees for uncommitted work and commits it;
    `background/fork_reconciler` reaps worktree directories and its reaper is ARMED. Both were
    written when no worktree on this machine had a resident writer — reasonably, because until
    2026-08-31 none did.

    WHAT IT COST, TWICE IN ONE EVENING. `fork_salvage` committed `SALVAGE(auto)` inside
    `/var/tmp/se-seat-executor` four minutes into the executor's first turn — an ungated commit
    under a running writer's HEAD, which rode onto `main` beneath the landing because the promotion
    route was then verifying only the tip. **Ninety minutes later it did the same to the delivery
    seat's own landing worktree**, mid-preparation, and the first version of this function did not
    cover it: it compared against `WORKTREE` and nothing else, so it exempted the executor and left
    every other writer exposed. That is the wrong subject. The property is *a live writer*, not
    *this module's path*.

    And `fork_reconciler`'s reaper is the sharper one, still un-fired only by luck: it refuses a
    DIRTY worktree, and the executor is dirty for most of a turn — but there is a window at the
    start of every turn, after `ensure_worktree` resets and cleans and before the first edit, when
    the tree is clean and detached at `origin/main`, which is to say MERGED and **reap-eligible**.
    `git worktree remove` on a live writer is the whole turn gone.

    ANY WRITER MAY DECLARE ITSELF, which is what makes this general rather than a special case for
    one daemon. `OWNER_MARKER` holds the owning pid; this executor writes one for its own worktree,
    and a session working in a worktree by hand can write one too. The executor's own `PID_FILE` is
    still honoured for the worktree it owns, so nothing depends on the marker having been written.

    A PID **WITH A LIVENESS CHECK**, never the file's mere existence. A killed writer leaves its
    marker behind, and that worktree holds exactly the abandoned work those daemons exist to rescue
    and reap — the 2026-08-03 sweeps found modules that existed nowhere else, one `rm -rf` from
    being lost. Exempting a path outright would trade one collision for a class of silent losses.
    """
    try:
        resolved = Path(path).resolve()
    except (OSError, ValueError):
        return False

    # 1. THE MARKER, which any writer can drop. Checked first because it is the general answer.
    try:
        marker = int((resolved / OWNER_MARKER).read_text().strip())
        if pid_is_alive(marker):
            return True
    except (OSError, ValueError):
        pass

    # 2. THIS EXECUTOR'S OWN WORKTREE, via the pid file it already keeps. Kept so the executor is
    #    covered even on a turn where the marker could not be written.
    try:
        if resolved != WORKTREE.resolve():
            return False
        return pid_is_alive(int(PID_FILE.read_text().strip()))
    except (OSError, ValueError):
        return False


def _still_claimed(work_id: str) -> bool:
    """Is the lane's claim on this id still held? An unreadable store reads as STILL CLAIMED.

    Conservative in the direction that costs a repeat rather than a loss: mistakenly discharging a
    handoff loses the seat's judgement about what comes next, and mistakenly keeping one costs a
    tick that finds the work already done and says so.
    """
    try:
        return work_id in delivery_lane.held()
    except Exception:  # noqa: BLE001
        return True


def seat_continuation_drop(work_id: str) -> bool:
    """Drop a discharged continuation. Never raises -- a handoff store must not cost a tick."""
    try:
        from background import seat_continuation

        return bool(seat_continuation.drop(work_id))
    except Exception:  # noqa: BLE001
        return False


def _another_executor_is_running() -> bool:
    """A pid file WITH a liveness check. A bare lock left by a killed process never runs again.

    `/proc` RATHER THAN THE SIGNAL-0 PROBE, and that is a safety invariant rather than a style
    choice. `tests/background/test_substep4_exit.py::test_reaper_absent_no_kill_path_in_background`
    greps every `background/*.py` for any signal-sending call, because the exit-143 vector that
    killed an interactive session came from a reaper in this directory; the control is deliberately
    blind to the signal ARGUMENT, since a probe and a kill differ by one integer and a grep that
    trusted the integer would have to be right about every future edit. The first draft of this
    function used the signal-0 probe and reddened that control plus its twin in
    `test_process_reconciler.py`, wedging the operational-layer signal for every lane.

    `tools.wait_for.pid_is_alive` is the reuse, and it is also the better probe: the signal form
    raises PermissionError for a live process owned by someone else -- which the first draft had to
    special-case, and `/proc` does not. `background/worker_tick.py::_pid_alive` reaches the same
    conclusion for the same reason; this one is public and takes no second copy.
    """
    try:
        pid = int(PID_FILE.read_text().strip())
    except (OSError, ValueError):
        return False
    return pid_is_alive(pid)


def ensure_worktree(base: str) -> Path:
    """The executor's own worktree at `base`, created if absent and reset to it if present.

    RESET, not merge: this worktree holds no history worth keeping between turns. Anything it
    landed was promoted at the end of the turn that landed it, and anything it did not land was not
    finished — carrying that forward would hand the next turn a tree it did not build.
    """
    if not (WORKTREE / ".git").exists():
        WORKTREE.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "worktree", "add", "--detach", "-q", str(WORKTREE), base],
            cwd=str(PROJECT_DIR), check=True, capture_output=True, timeout=300,
        )
    else:
        subprocess.run(["git", "fetch", "--quiet", "origin"],
                       cwd=str(WORKTREE), capture_output=True, timeout=300)
        subprocess.run(["git", "reset", "--hard", "-q", base],
                       cwd=str(WORKTREE), check=True, capture_output=True, timeout=300)
        subprocess.run(["git", "clean", "-qfd"],
                       cwd=str(WORKTREE), capture_output=True, timeout=300)
    return WORKTREE


def _resolve_claude() -> str | None:
    for candidate in (os.environ.get("CLAUDE_BIN"), "claude",
                      str(Path.home() / ".nvm/versions/node/v24.16.0/bin/claude")):
        if not candidate:
            continue
        try:
            if subprocess.run(["which", candidate], capture_output=True,
                              text=True, timeout=10).returncode == 0:
                return candidate
        except Exception:  # noqa: BLE001
            continue
    return None


CHARTER = """You are the delivery seat, continuing work autonomously in an ISOLATED git worktree.

YOU ARE NOT ON THE SHARED TREE. Your cwd is a linked worktree; nothing you do here can touch
another writer's uncommitted work. That isolation is the whole reason you are allowed to run.

HOW TO LAND, and there is no other way:
  1. `python3 -m tools.surgical_land -m "<message>" <exact paths>` — the sanctioned door. It works
     from this worktree. Hook bypass is a wall: never --no-verify, never a hand-built commit.
  2. `python3 -m tools.promote_worktree_landing . --work-id <your claim id>` — gets the landing onto
     origin/main, or refuses with a named cause. If it refuses because origin moved, re-gate on the
     new base and land again. Never force anything.

IF IT IS BIGGER THAN ONE TURN, LAND THE PART YOU FINISHED. A landed increment proves the work is
moving; an unlanded whole proves nothing and is lost when this turn ends.

WRITE DOWN WHAT YOU FOUND. A finding in docs/staging/ with its severity header, and a
pre-registration BEFORE any measurement whose answer you do not already know.

WHEN YOU ARE DONE, hand the next piece on:
  `python3 -m background.seat_continuation --hand-off ID WHAT WHY DONE_MEANS`
"""


def build_prompt(item: dict) -> str:
    return CHARTER + "\n\nTHE WORK:\n\n" + delivery_lane.doorbell(item)


def run_once(*, dry_run: bool = False, now: float | None = None) -> tuple[bool, str]:
    """One bounded turn. Returns `(ran, detail)`; a stand-down is `(False, reason)`, never a raise."""
    try:
        if _another_executor_is_running():
            raise StoodDown("another executor is already running")

        item = delivery_lane.next_item(now=now)
        if item is None:
            raise StoodDown("nothing to do: no continuation and no unclaimed focus item")

        work_id = item["id"]

        # THE SEAT-IS-LIVE STAND-DOWN NOW ASKS ABOUT CONTENTION, NOT PRESENCE (2026-08-31).
        #
        # It used to run FIRST and refuse on a warm heartbeat alone, which made this executor
        # unrunnable in exactly the situation it was built for. What it is protecting against is
        # TWO WRITERS CHOOSING WORK FROM THE SAME QUEUE. A continuation is not that: it is the
        # interactive seat writing down, deliberately and in full context, *"this piece is for
        # whoever runs next"*. Standing down on a handoff because the session that WROTE the
        # handoff is still alive refuses the one thing the mechanism exists to do -- and the
        # session is nearly always still alive, because it writes the handoff and then keeps
        # working.
        #
        # A FOCUS ITEM IS DIFFERENT and still stands down. `direction.unreachable_focus` is
        # re-derived from the tree every three hours; nobody handed it over, and a live seat may
        # well be part-way through it with nothing claimed yet. That is real contention, and the
        # path guard cannot see it because an unclaimed decision has no paths.
        if _interactive_seat_is_live(now) and not _is_handed_off(item, now=now):
            raise StoodDown(
                f"an interactive seat is live and {work_id!r} was not handed off to a tick -- "
                "a re-derived focus item may be work that seat is already part-way through"
            )

        try:
            seat_work_in_hand.refuse_if_duplicated(
                list(item.get("paths") or []), exclude=work_id)
        except DuplicateWork as exc:
            raise StoodDown(f"the work duplicates a live claim: {exc}") from exc

        if dry_run:
            # A DRY RUN THAT WRITES NOTHING CANNOT DEMONSTRATE ANYTHING. Every other outcome of
            # this function reaches the log -- RUNNING, FINISHED, STOOD DOWN -- and this one
            # returned silently, so "the executor can reach a handed-off focus item" was an
            # argument about the code rather than a record of it having happened. It is marked
            # DRY RUN in the ledger precisely so it can never be read back as a real turn.
            log(f"DRY RUN: would run {work_id} -- all four refusals passed")
            return False, f"would run {work_id} (dry run)"

        claude_bin = _resolve_claude()
        if claude_bin is None:
            raise StoodDown("claude binary not found")

        base = subprocess.run(["git", "rev-parse", "origin/main"], cwd=str(PROJECT_DIR),
                              capture_output=True, text=True, timeout=60).stdout.strip()
        worktree = ensure_worktree(base or "origin/main")
        delivery_lane.claims_mod.claim(work_id, note=str(item.get("what") or "")[:200], paths=[])
        # Guarded like every other live-record write here: an unattended writer whose pid file a
        # test can forge is one a test can make look alive or dead.
        guard_live_ledger_write(PID_FILE, writer="seat_executor.run_once").write_text(
            str(os.getpid()))
        # DECLARE THE WORKTREE IN USE, in the worktree itself, so the daemons that sweep worktrees
        # can see it without knowing anything about this module. See `worktree_is_live`.
        try:
            (worktree / OWNER_MARKER).write_text(str(os.getpid()) + "\n")
        except OSError:
            pass  # a marker that cannot be written costs the PID_FILE route below, not the turn
        log(f"RUNNING {work_id} in {worktree} on {base[:9]}")

        try:
            proc = subprocess.run(
                [claude_bin, "-p", "--dangerously-skip-permissions", "--model", MODEL,
                 build_prompt(item)],
                cwd=str(worktree), capture_output=True, text=True,
                timeout=SESSION_TIMEOUT_SECONDS,
                env=dict(os.environ, DISABLE_AUTOUPDATER="1", SE_SEAT_EXECUTOR="1"),
            )
            detail = f"{work_id}: rc={proc.returncode}"
        except subprocess.TimeoutExpired:
            detail = f"{work_id}: did not finish inside {SESSION_TIMEOUT_SECONDS}s"
        finally:
            PID_FILE.unlink(missing_ok=True)

        # A RELEASED CLAIM DISCHARGES THE HANDOFF (2026-08-31), and the two stores had never
        # spoken. `seat_continuation` re-offers a live continuation on every tick until its six-hour
        # window closes; `delivery_lane` claims are released by the tick calling `--release` when it
        # judges the work finished. Nothing connected them, so the FIRST handoff this executor ever
        # took was drawn twice -- 18:12 and again at 19:06 on the same id.
        #
        # RE-OFFERING IS DELIBERATE while work is unfinished: the charter tells a tick to land the
        # part it finished, and a piece bigger than one turn must come back. So the signal is not
        # "a turn ended", it is "the tick said it was done" -- which is exactly what releasing the
        # claim means. If it did not release, the continuation stands and the next tick continues.
        if not _still_claimed(work_id):
            if seat_continuation_drop(work_id):
                log(f"DISCHARGED {work_id}: the tick released its claim, so the handoff is done "
                    "and will not be re-offered")
        log(f"FINISHED {detail}")
        return True, detail

    except StoodDown as reason:
        log(f"STOOD DOWN: {reason}")
        return False, str(reason)


def main(argv=None) -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--once", action="store_true", help="run a single bounded turn")
    ap.add_argument("--dry-run", action="store_true",
                    help="run every refusal and name what it WOULD take; spawn nothing")
    ap.add_argument("--status", action="store_true", help="print what a turn would do now")
    args = ap.parse_args(argv)

    if args.status or args.dry_run:
        ran, detail = run_once(dry_run=True)
        print(json.dumps({"would_run": ran, "detail": detail,
                          "interactive_seat_live": _interactive_seat_is_live(),
                          "another_executor": _another_executor_is_running()}, indent=1))
        return 0
    if args.once:
        ran, detail = run_once()
        print(detail)
        return 0 if ran else 0
    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    from background._seat import refuse_if_foreign  # seat guard, FIRST act

    refuse_if_foreign("seat_executor")
    raise SystemExit(main())
