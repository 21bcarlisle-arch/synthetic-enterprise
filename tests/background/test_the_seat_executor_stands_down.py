"""The first unattended writer in this project's history, and every leg here is a reason not to run.

`background/seat_executor.py` continues the seat's work without the director. It can only exist
because two things landed on 2026-08-31: `surgical_land` works from a worktree (`178bf5a56`), and
`tools/promote_worktree_landing` made integration a route with refusals rather than a remembered
git sequence. Before those, an autonomous seat would have been a second writer on the shared tree —
the configuration that caused August's damage.

SO THE CONTROLS ARE THE STAND-DOWNS. Running is what happens when it has run out of reasons not to,
which is the same shape as the promotion route one layer up. One leg holds that it CAN run, because
without it every other leg is satisfied by an executor that never does anything — the failure that
would make this whole build a very safe way of achieving nothing.
"""
from __future__ import annotations

import json
import os
import time

import pytest

from background import seat_executor


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    """No test here may touch the real log, pid file or worktree."""
    monkeypatch.setattr(seat_executor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    monkeypatch.setattr(seat_executor, "WORKTREE", tmp_path / "wt")
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: False)
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: False)


def _offer(monkeypatch, item):
    monkeypatch.setattr(seat_executor.delivery_lane, "next_item", lambda **k: item)


def test_it_stands_down_on_a_REDERIVED_item_while_an_interactive_seat_is_live(monkeypatch):
    """A human holding this seat and an executor drawing from the same queue is two writers.

    The item here was NOT handed off — it is a `direction.unreachable_focus` entry, re-derived
    from the tree every three hours. Nobody gave it away, and the live seat may be part-way
    through it with nothing claimed yet; the path guard cannot see that, because an unclaimed
    decision has no paths.

    MUTATION: drop the liveness check and this fires.
    """
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: True)
    monkeypatch.setattr(seat_executor, "_is_handed_off", lambda item, now=None: False)
    _offer(monkeypatch, {"id": "anything", "what": "w", "why": "y"})
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "not handed off" in detail


def test_a_HANDED_OFF_continuation_runs_even_though_the_seat_that_wrote_it_is_live(monkeypatch):
    """THE STAND-DOWN ASKS ABOUT CONTENTION, NOT PRESENCE — and this is the leg that says so.

    Measured 2026-08-31, the day the executor was armed: the liveness check ran FIRST and refused
    on a warm heartbeat alone, which made this executor unrunnable in precisely the situation it
    was built for. A continuation is the interactive seat writing down, deliberately and in full
    context, *"this piece is for whoever runs next"*. The seat that wrote it is nearly always
    still alive — it writes the handoff and then keeps working — so refusing on presence refuses
    every handoff there will ever be.

    MUTATION: put the liveness check back ahead of the draw, or make it ignore `_is_handed_off`,
    and this fires. That mutation is not hypothetical: it is the code as shipped this morning.
    """
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: True)
    monkeypatch.setattr(seat_executor, "_is_handed_off", lambda item, now=None: True)
    _offer(monkeypatch, {"id": "handed-over", "what": "w", "why": "y"})
    ran, detail = seat_executor.run_once(dry_run=True)
    assert "handed-over" in detail
    assert "interactive seat" not in detail


def test_whether_an_item_was_handed_off_is_asked_of_the_store_that_owns_it(tmp_path, monkeypatch):
    """`_is_handed_off` must not duck-type the item.

    By the time `next_item` returns one, a continuation and a focus item are the same shape, so a
    shape check would be a second and weaker answer to a question `seat_continuation` already owns
    — including the six-hour window that stops a handoff outliving the tree it reasoned about.
    This asserts the real store is consulted, and that expiry carries through.
    """
    from background import seat_continuation

    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    seat_continuation.hand_off("handed-over", what="w", why="y", done_means="d")
    item = {"id": "handed-over", "what": "w", "why": "y"}

    assert seat_executor._is_handed_off(item) is True
    assert seat_executor._is_handed_off({"id": "never-handed-over"}) is False
    # Past the window: the store drops it, so the executor stops treating it as given away.
    stale = time.time() + seat_continuation.STALE_AFTER_SECONDS + 60
    assert seat_executor._is_handed_off(item, now=stale) is False


def test_it_stands_down_while_ANOTHER_executor_is_running(monkeypatch):
    """Two executors is the same defect as two writers, with the same cause.

    MUTATION: drop the pid check and this fires.
    """
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: True)
    _offer(monkeypatch, {"id": "anything", "what": "w", "why": "y"})
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "another executor" in detail


def test_it_stands_down_when_there_is_NOTHING_TO_DO_and_says_so(monkeypatch):
    """A legitimate resting state, recorded with its reason.

    Running anyway produces a confident restatement of the last decision, which reads downstream
    exactly like a decision — `delivery_seat`'s skip rule, one seat over.

    MUTATION: make an empty queue fall through to a session and this fires.
    """
    _offer(monkeypatch, None)
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "nothing to do" in detail


def test_it_stands_down_when_the_work_DUPLICATES_a_live_claim(monkeypatch):
    """The risk the director named, and the one I committed myself.

    An unattended writer cannot read the other claim's note and judge, so an overlap refuses here
    where a human-driven caller would only be warned.

    MUTATION: drop the `refuse_if_duplicated` call and this fires.
    """
    _offer(monkeypatch, {"id": "mine", "what": "w", "why": "y",
                         "paths": ["tools/measure_departure_level.py"]})

    def _clash(paths, exclude=None):
        raise seat_executor.DuplicateWork("someone-else already holds: tools/measure_departure_level.py")

    monkeypatch.setattr(seat_executor.seat_work_in_hand, "refuse_if_duplicated", _clash)
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "duplicates a live claim" in detail
    assert "someone-else" in detail, "the stand-down must name who holds the paths"


def test_it_CAN_run_when_nothing_objects__so_the_stand_downs_are_not_vacuous(monkeypatch):
    """Without this, an executor that never ran would pass every other leg in this file.

    Uses `--dry-run`, which runs every refusal and spawns nothing: what is asserted is that it
    REACHES the decision to run.

    MUTATION: make `run_once` always stand down and this fires.
    """
    _offer(monkeypatch, {"id": "real-work", "what": "w", "why": "y", "paths": []})
    ran, detail = seat_executor.run_once(dry_run=True)
    assert ran is False, "a dry run must not spawn"
    assert "would run real-work" in detail, (
        "the executor never reached a decision to run — every stand-down above proves nothing"
    )


def test_a_stand_down_is_RECORDED_and_never_raises(monkeypatch):
    """A tick that dies takes its reason with it; a tick that logs leaves the reason behind.

    MUTATION: let `StoodDown` propagate out of `run_once` and this fires.
    """
    _offer(monkeypatch, None)
    ran, _ = seat_executor.run_once()
    assert ran is False
    written = seat_executor.LOG_FILE.read_text()
    assert "STOOD DOWN" in written and "nothing to do" in written


def test_a_dead_executors_pid_file_does_not_block_the_machine_forever(monkeypatch, tmp_path):
    """A bare lock left by a killed process is a machine that never runs again.

    MUTATION: treat the pid file's existence as the lock and this fires.
    """
    monkeypatch.undo()
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    (tmp_path / "executor.pid").write_text("999999999")
    assert seat_executor._another_executor_is_running() is False, (
        "a pid file naming a dead process was read as a live executor"
    )
    (tmp_path / "executor.pid").write_text(str(os.getpid()))
    assert seat_executor._another_executor_is_running() is True


def test_the_executor_writes_no_code_to_the_shared_tree():
    """The claim the whole design rests on, held as a list rather than a sentence.

    Every edit it makes is in its worktree. The only shared-tree files it may touch are its own
    log and pid — both in `docs/observability/`, which every daemon here appends to by design.

    MUTATION: add any other shared-tree path to `SHARED_TREE_WRITES`, or write one directly, and
    this fires.
    """
    allowed = {p.name for p in seat_executor.SHARED_TREE_WRITES}
    assert allowed == {"seat-executor-log.md", ".seat_executor.pid"}
    for path in seat_executor.SHARED_TREE_WRITES:
        rel = path.relative_to(seat_executor.PROJECT_DIR)
        assert str(rel).startswith("docs/observability/"), (
            f"{rel} is a shared-tree write outside observability — the executor would be a second "
            "writer on the code tree, which is the thing it is built not to be"
        )


#: The ONLY things allowed to INVOKE the executor. It was armed on 2026-08-31, deliberately and on
#: the director's instruction, so the question this leg asks changed shape twice: first from "is
#: anything scheduling it" to "is the scheduler the DECLARED one", and then -- when this leg caught
#: `fork_salvage` and `fork_reconciler` the moment they began ASKING the executor whether its
#: worktree is live -- from "mentions it" to "invokes it". A daemon that reads a predicate does not
#: schedule a turn, and a control that cannot tell those apart forces an allow-list that grows
#: every time somebody asks the executor a question.
_ARMED_BY = {
    "background/seat-executor.service",   # ExecStart -- the oneshot itself
    "background/seat-executor.timer",     # its schedule (named in the .service's Description)
    "background/schedule_manifest.yaml",  # the IaC declaration both are installed from
}

#: What INVOKING it looks like, as opposed to importing something from it. Each of these starts a
#: turn; none of them can be produced by reading a predicate.
#:
#: THE TWO PYTHON ENTRY POINTS CARRY THEIR CALL PAREN (2026-08-31), and this is the SAME refinement
#: this list already made once, one step further. It moved from "mentions the module" to "invokes
#: it" when `fork_salvage` and `fork_reconciler` began calling `worktree_is_live` and were reported
#: as new schedulers. It then fired again on `background/delivery_lane.py`, whose new
#: `hand_off_focus` docstring EXPLAINS the executor's stand-down and had to name the function it
#: was explaining. Prose about a function is not a call to it, and a control that cannot tell those
#: apart makes every accurate comment about this module a reason to extend an allow-list -- which
#: is the shape the docstring above already rejects.
#:
#: `(` IS THE PROPERTY, not a convenience: a Python call cannot be written without it, and a
#: mention in a sentence essentially never carries one. The subprocess forms below need no paren
#: because a shell invocation is already unambiguous.
_INVOCATION_PATTERNS = (
    "background.seat_executor --once",
    "background/seat_executor.py",
    "seat_executor.run_once(",
    "seat_executor.main(",
    "-m background.seat_executor",
    "seat-executor.service",
)


def test_the_only_thing_that_invokes_it_is_the_declared_schedule():
    """ARMED 2026-08-31, and the control moved from "nothing runs it" to "only the declared thing
    runs it" -- then from "nothing mentions it" to "nothing INVOKES it".

    The original leg asserted nothing on this machine invoked the executor at all, because the
    first unattended writer in this project's history had to be started by a person rather than by
    a landing. It was, and the director's instruction is in the commit that armed it.

    WHAT REPLACES IT MATTERS MORE THAN WHAT IT SAID. An unattended writer that can be started from
    anywhere is one an unrelated landing can arm by accident, and a second invoker would mean two
    schedules with no shared notion of how often it may run or what has already claimed the work.

    AND THE SUBJECT IS INVOCATION, NOT MENTION -- which this leg established by firing on its own
    author. When `fork_salvage` and `fork_reconciler` started calling
    `seat_executor.worktree_is_live` (so they would stop committing into and reaping a LIVE
    writer's worktree), a substring check on the module name reported them as new invokers. They
    are readers. Keying on mention would have meant an allow-list extended for every question
    anyone asks the executor, and an allow-list that grows on contact stops being a control.

    MUTATION: add `subprocess.run(["python3", "-m", "background.seat_executor", "--once"])`
    anywhere under `background/`, `tools/`, `systemd/` or `.claude/` and this fires with the path
    named.
    """
    from pathlib import Path

    project = seat_executor.PROJECT_DIR
    invokers = []
    for tree in ("background", "tools", "systemd", ".claude"):
        base = project / tree
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in (
                ".py", ".timer", ".service", ".sh", ".json", ".yaml",
            ):
                continue
            if path.name.startswith("test_") or path == Path(seat_executor.__file__):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if any(pattern in text for pattern in _INVOCATION_PATTERNS):
                invokers.append(str(path.relative_to(project)))

    unexpected = sorted(set(invokers) - _ARMED_BY)
    assert unexpected == [], (
        f"the seat executor is INVOKED from something outside its declared schedule: "
        f"{unexpected}. One unattended writer means one schedule; a second invoker has no shared "
        "notion of cadence or of what has already been claimed."
    )
    # POPULATION FLOOR. Without it this passes just as happily on the day someone deletes the
    # units and the executor stops being scheduled at all -- a control that goes quiet instead of
    # loud, which is this repo's most-repeated failure.
    assert _ARMED_BY.issubset(set(invokers)), (
        f"the declared schedule is missing: {sorted(_ARMED_BY - set(invokers))}. An armed executor "
        "with no unit is a handoff mechanism nobody fires, which is the drag it was built to remove."
    )


# ── A RELEASED CLAIM DISCHARGES THE HANDOFF (2026-08-31) ─────────────────────────────────────────
# The first handoff this executor ever took was drawn TWICE — 18:12 and again at 19:06 on the same
# id — because `seat_continuation` re-offers a live continuation on every tick until its six-hour
# window closes, and nothing told it the work was done. The two stores had never spoken.
#
# Re-offering is DELIBERATE while work is unfinished: the charter tells a tick to land the part it
# finished, so a piece bigger than one turn must come back. The signal is therefore not "a turn
# ended" but "the tick said it was done", which is what releasing the lane claim means.

def test_a_turn_that_released_its_claim_discharges_the_handoff(monkeypatch, tmp_path):
    """MUTATION: drop the discharge and this fires — the continuation survives a finished turn."""
    from background import seat_continuation

    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    seat_continuation.hand_off("done-and-released", what="w", why="y", done_means="d")
    monkeypatch.setattr(seat_executor.delivery_lane, "held", lambda *a, **k: set())

    assert seat_executor._still_claimed("done-and-released") is False
    assert seat_executor.seat_continuation_drop("done-and-released") is True
    assert [i["id"] for i in seat_continuation.live()] == []


def test_a_turn_that_KEPT_its_claim_leaves_the_handoff_standing(monkeypatch, tmp_path):
    """THE LEG THAT PROTECTS MULTI-TURN WORK. A tick that landed an increment and did not release
    has said the piece is unfinished; dropping the continuation there would lose the seat's
    judgement about what comes next and leave the rest of the work unowned."""
    from background import seat_continuation

    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    seat_continuation.hand_off("still-going", what="w", why="y", done_means="d")
    monkeypatch.setattr(seat_executor.delivery_lane, "held", lambda *a, **k: {"still-going"})

    assert seat_executor._still_claimed("still-going") is True
    assert [i["id"] for i in seat_continuation.live()] == ["still-going"]


def test_an_unreadable_claim_store_keeps_the_handoff(monkeypatch):
    """Conservative in the direction that costs a REPEAT rather than a LOSS.

    Mistakenly discharging loses the seat's judgement about what comes next; mistakenly keeping
    costs a tick that finds the work already done and says so. The second is much the cheaper
    error, so an unreadable store reads as STILL CLAIMED.
    """
    def _explode(*a, **k):
        raise RuntimeError("claims unreadable")

    monkeypatch.setattr(seat_executor.delivery_lane, "held", _explode)
    assert seat_executor._still_claimed("anything") is True
