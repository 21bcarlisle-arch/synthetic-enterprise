"""A TRUTHFUL NAME WITH AN UNTRUTHFUL MESSAGE: `REFUSED_RACE` paged the director as BLOCKED_WORK.

`background/origin_reconcile.py` learned on 2026-09-05 to tell a lost push race apart from a
reconciler that cannot push (landed 3d5694078). Nothing downstream read the new name.
`deadmans_switch._check_origin_fork` enumerated LEVEL/RECONCILED/PUSHED/FAST_FORWARDED as clear and
GATE_RUNNING as quiet, and *everything else* fell through to one `real_alarm` classed BLOCKED_WORK
saying:

    landings and publishing stay blocked until someone reconciles.

For an outcome that clears itself on the next five-minute cadence. There is nothing to reconcile —
the merge gated CLEAN and only the push lost — and nothing for him to do. It costs the only scarce
resource here, because BLOCKED_WORK is the class he acts on.

THE DEFECT THIS FILE'S CONTROLS NAME IS NOT "IT PAGED". It is that the message and the outcome
disagreed, in both directions:

  * a self-healing race told him work was blocked when it was not, and
  * the obvious repair — suppress it beside GATE_RUNNING — would have been WORSE, because the two
    states are opposites. GATE_RUNNING means nothing was LOOKED at. A race means the reconciler
    looked, built the merge, gated it clean, and still could not push: the fork IS open and it
    STAYED open. Suppressing that outright is a fail-silent hole exactly where it hurts — a
    reconciler that has stopped converging would then never page at all.

So the partition is three-way, and the discriminator is whether the race is doing the one thing that
makes it benign: HEALING. Below `RACE_PERSISTENCE_SECONDS` it is logged and nothing is sent; at or
beyond it he hears about it under BLOCKED_WORK, which by then is true; and when the episode cannot
be MEASURED it is reported rather than assumed, because an unmeasurable episode is precisely the
state in which self-healing cannot be shown.

WHY THE PARTITION IS ASSERTED WHOLE BEFORE ANY LEG'S MEANING. CLAUDE.md: *when a branch exists to be
taken rarely, assert it CAN be taken before asserting what it does.* A handler hard-wired to stay
silent passes every "it does not page" test in this file, and destroys the fail-silent guard that is
half its purpose; one hard-wired to page passes every "it pages" test and reinstates the defect.
`test_all_three_race_outcomes_are_REACHABLE` is one control over the whole partition, from one set
of inputs, and it fires on either hard-wiring.

AND THE EPISODE CLOCK IS THE SELF-CLEARING-ALARM CLASS (PW2). The alarm's severity is derived from
a state file the race path itself writes — the 2026-08-09 shape, where a 10h26m outage paged as a
fresh 14 minutes because every failure rewrote the episode start.
`test_the_race_path_CANNOT_shorten_the_episode_its_own_alarm_reads` is the guard, and the repair is
`episode_monotonic.guard_episode` rather than a sixth hand-rolled low-water loop.
"""
from __future__ import annotations

import json
import time
from types import SimpleNamespace

import pytest

from background import deadmans_switch as ds
from background import origin_reconcile as orc

#: Comfortably inside and comfortably outside the window, expressed against the constant rather
#: than as literals. Keyed to the PROPERTY: if `RACE_PERSISTENCE_SECONDS` is ever re-derived, these
#: still mean "a race that is still healing" and "one that has stopped", which is what is asserted.
_INSIDE = ds.RACE_PERSISTENCE_SECONDS * 0.5
_BEYOND = ds.RACE_PERSISTENCE_SECONDS * 1.5


@pytest.fixture
def fork(tmp_path, monkeypatch):
    """Drive `_check_origin_fork` end to end against a stubbed reconciler.

    END TO END AND NOT AT `_report_lost_push_race`, deliberately: the defect was in the ROUTING —
    `REFUSED_RACE` reaching the fall-through alarm — so a control that called the new handler
    directly would pass with the handler unwired, which is the state the bug was in.
    """
    monkeypatch.setattr(ds, "ORIGIN_RACE_EPISODE_FILE", tmp_path / ".origin_race_episode.json")
    sent: list[tuple[str, dict]] = []
    logged: list[str] = []
    cleared: list[str] = []
    monkeypatch.setattr(ds, "notify", lambda msg, **kw: sent.append((msg, kw)) or "id")
    monkeypatch.setattr(ds, "log", lambda m, path=None: logged.append(m))
    monkeypatch.setattr(ds, "clear_transition", lambda k: cleared.append(k))

    def run(status, *, detail="the push lost the race", behind=3):
        monkeypatch.setattr(orc, "reconcile",
                            lambda *a, **k: {"status": status, "detail": detail,
                                             "behind": behind, "ahead": 2})
        ds._check_origin_fork()

    def open_episode(age_seconds, *, races=4):
        """Plant an episode that STARTED `age_seconds` ago. Written as a file and not as a patched
        clock because the file is the thing under test: the alarm's severity comes off disk, and a
        control that stubbed the clock would never touch the record."""
        ds.ORIGIN_RACE_EPISODE_FILE.write_text(json.dumps(
            {"race_since": time.time() - age_seconds, "races": races}), encoding="utf-8")

    def episode():
        return json.loads(ds.ORIGIN_RACE_EPISODE_FILE.read_text(encoding="utf-8"))

    return SimpleNamespace(sent=sent, logged=logged, cleared=cleared,
                           run=run, open_episode=open_episode, episode=episode)


# ── the partition, whole, before any leg's meaning ──────────────────────────────────────────────
def test_all_three_race_outcomes_are_REACHABLE(fork):
    """ONE CONTROL OVER THE WHOLE PARTITION. Every other test below asks whether one leg does the
    right thing, and a handler hard-wired to ONE answer passes the ones that agree with it.

    MUTATION: make `_report_lost_push_race` return before it notifies (the naive "suppress it beside
    GATE_RUNNING" repair) and this fails. Make it always notify — the pre-repair behaviour — and
    this fails too. Both mutations pass some of the tests below; neither passes this.
    """
    fork.open_episode(_INSIDE)
    fork.run(orc.REFUSED_RACE)
    healing = len(fork.sent)

    fork.open_episode(_BEYOND)
    fork.run(orc.REFUSED_RACE)
    persisting = len(fork.sent)

    ds.ORIGIN_RACE_EPISODE_FILE.write_text("{ this is not json", encoding="utf-8")
    fork.run(orc.REFUSED_RACE)
    unmeasurable = len(fork.sent)

    assert healing == 0, "a race that is still healing must not page"
    assert persisting == 1, "a race that has stopped healing must page"
    assert unmeasurable == 2, "a race whose episode cannot be read must page"


# ── the defect itself ───────────────────────────────────────────────────────────────────────────
def test_a_healing_race_does_not_tell_him_work_is_blocked(fork):
    """THE REPORTED DEFECT, stated as the sentence he actually received.

    MUTATION: delete the `REFUSED_RACE` branch from `_check_origin_fork` so it falls through to the
    fork alarm again — the exact pre-repair code — and this fails on both assertions.
    """
    fork.run(orc.REFUSED_RACE)

    assert fork.sent == [], "a self-healing race is not something he can act on"
    blob = " ".join(fork.logged)
    assert "BENIGN" in blob and "self-healing" in blob, \
        "it must still be in the record — quiet is not the same as invisible"


def test_a_healing_race_is_not_classed_BLOCKED_WORK_by_any_route(fork):
    """Keyed to the CLASS and not to the sentence. The message could be reworded tomorrow; what may
    not happen is a self-healing outcome reaching the instant channel he acts on."""
    fork.run(orc.REFUSED_RACE)
    fork.run(orc.REFUSED_RACE)
    assert not [kw for _, kw in fork.sent if kw.get("kind") == "real_alarm"]


def test_the_race_is_NOT_suppressed_the_way_GATE_RUNNING_is(fork):
    """THE FAIL-SILENT HALF, and the reason this was not a two-line suppression.

    A race that never heals is a reconciler that has stopped converging — the fork is open, it
    stayed open, and nothing is reaching origin. That IS blocked work, and by the time this fires
    the fork has been open for as long as this module's own definition of it.

    MUTATION: suppress `REFUSED_RACE` unconditionally beside `GATE_RUNNING` and this fails.
    """
    fork.open_episode(_BEYOND, races=9)
    fork.run(orc.REFUSED_RACE)

    assert len(fork.sent) == 1
    msg, kw = fork.sent[0]
    assert kw["kind"] == "real_alarm"
    assert kw["topic_class"] == ds._digest_classes().BLOCKED_WORK
    assert "NOT converging" in msg


def test_the_persistent_race_message_does_not_ask_him_to_MERGE_anything(fork):
    """The old message's instruction was the false part, not its loudness: *"until someone
    reconciles"*. There is nothing to reconcile — the merge gates clean every cycle, which is why
    the push is the only thing that fails. A page he cannot act on is the cost being paid here, so
    the persistent case has to name what is actually wrong.

    MUTATION: reuse the fall-through message for the persistent case and this fails.
    """
    fork.open_episode(_BEYOND)
    fork.run(orc.REFUSED_RACE)
    msg = fork.sent[0][0]
    assert "until someone reconciles" not in msg
    assert "NOTHING TO MERGE BY HAND" in msg
    assert "pushing to origin faster than a gate run takes" in msg


def test_a_non_race_refusal_still_carries_the_original_instruction(fork):
    """The fall-through alarm was RIGHT for the cases it was written for and is not what changed.
    A conflict genuinely does need a person, and this is the control that the repair narrowed the
    branch rather than gutting it.

    MUTATION: route every refusal through the race handler and this fails.
    """
    fork.run(orc.REFUSED_CONFLICT, detail="both lanes edited docs/status/LATEST.md")
    assert len(fork.sent) == 1
    msg, kw = fork.sent[0]
    assert "until someone reconciles" in msg
    assert kw["topic_class"] == ds._digest_classes().BLOCKED_WORK


# ── the episode clock: the self-clearing-alarm class (PW2) ──────────────────────────────────────
def test_the_race_path_CANNOT_shorten_the_episode_its_own_alarm_reads(fork):
    """THE 2026-08-09 SHAPE, in this control's own subject: the failure path writes the state its
    alarm reads, so each new failure could rewrite the episode start and a standing race would
    report as a fresh one forever — and therefore never cross the threshold, never page.

    MUTATION: write `{"race_since": now}` directly instead of routing through `guard_episode` and
    this fails: the start jumps to now, the age collapses, and the alarm goes quiet.
    """
    fork.open_episode(_BEYOND, races=6)
    started = fork.episode()["race_since"]

    for _ in range(3):
        fork.run(orc.REFUSED_RACE)

    assert fork.episode()["race_since"] == pytest.approx(started), \
        "an open episode's start is a LOW-water mark; only a close may move it"
    assert fork.episode()["races"] >= 9, "and its counter is a high-water mark"
    assert len(fork.sent) == 3, "it must keep reporting, not go quiet as it repeats"


def test_every_cadence_of_one_episode_carries_the_SAME_transition_state(fork):
    """Keyed to the EPISODE, not to today's count or today's `behind` — both of which move every
    cadence, and a state that changes every cycle is a transition check that cannot suppress
    anything. That is how this channel has buried its own signal before.

    MUTATION: key the state on `behind` or on the race count and this fails.
    """
    fork.open_episode(_BEYOND)
    fork.run(orc.REFUSED_RACE, behind=3)
    fork.run(orc.REFUSED_RACE, behind=11)
    assert len({kw["state"] for _, kw in fork.sent}) == 1


def test_an_UNREADABLE_episode_record_is_REPORTED_and_never_read_as_fresh(fork):
    """ABSENT and PRESENT-BUT-UNREADABLE are opposite facts (`background/episode_prior.py`), and
    here the difference decides whether a race may be called benign at all. It may not: a race is
    benign only in so far as it is self-healing, and an unreadable record is exactly the state in
    which that cannot be shown. "We cannot tell" is a result and belongs on the surface.

    MUTATION: treat an unreadable record as an absent one — the conflation five carriers shipped —
    and this fails, because a standing race would then read as its own first cadence forever.
    """
    ds.ORIGIN_RACE_EPISODE_FILE.write_text("{ truncated", encoding="utf-8")
    fork.run(orc.REFUSED_RACE)

    assert len(fork.sent) == 1
    msg, kw = fork.sent[0]
    assert "CANNOT SAY" in msg and "unreadable" in msg
    assert kw["state"] == "race:unmeasurable"
    assert (ds.ORIGIN_RACE_EPISODE_FILE.parent / ".origin_race_episode.json.unreadable").exists(), \
        "the bytes must be kept: the rebuild that follows would otherwise destroy the evidence"


def test_reaching_origin_CLOSES_the_episode_and_the_next_race_is_benign_again(fork):
    """The ONLY way the episode shortens, and it is not on the failure path. A close is an outcome
    the reconciler reported, never something the race branch decided about itself.

    MUTATION: close the episode from the race path too and
    `test_the_race_path_CANNOT_shorten_the_episode_its_own_alarm_reads` fails; never close it and
    this one does, because a machine that pushed successfully an hour ago would still be paging.
    """
    fork.open_episode(_BEYOND, races=7)
    fork.run(orc.REFUSED_RACE)
    assert len(fork.sent) == 1

    fork.run(orc.PUSHED, detail="1 gated landing(s) pushed")
    assert not ds.ORIGIN_RACE_EPISODE_FILE.exists()
    assert ds._ORIGIN_FORK_KEY in fork.cleared
    assert any("race episode CLOSED" in m for m in fork.logged), \
        "how long it ran is the one thing the closing log line must keep"

    fork.run(orc.REFUSED_RACE)
    assert len(fork.sent) == 1, "a new episode starts healing, not where the last one ended"


def test_a_non_race_REFUSAL_also_closes_the_episode(fork):
    """A conflict is not a lost race, and leaving the race episode open under it would let a later
    race inherit a clock it did not earn — an alarm reporting an episode longer than the evidence,
    which is the mirror of the defect above and just as dishonest.

    MUTATION: close the episode only on the success branch and this fails.
    """
    fork.open_episode(_INSIDE)
    fork.run(orc.REFUSED_GATE, detail="the merged tree is red")
    assert not ds.ORIGIN_RACE_EPISODE_FILE.exists()


def test_GATE_RUNNING_neither_closes_nor_extends_an_open_episode(fork):
    """Nothing was looked at, so nothing about the race was observed either way. Closing would
    assert a healing that was not seen; extending would count a cycle that never tried as a loss.
    The episode is measured in ELAPSED TIME precisely so a stretch of unlooked-at cycles does
    neither.

    MUTATION: add `_close_race_episode` or `_extend_race_episode` to the GATE_RUNNING branch and
    this fails.
    """
    fork.open_episode(_INSIDE, races=2)
    before = fork.episode()

    fork.run(orc.GATE_RUNNING, detail="the publish gate holds the lock")

    assert fork.episode() == before
    assert fork.sent == []
    assert fork.cleared == [], "a cycle that did not look may not clear the fork alarm either"


# ── THE SIBLING TWO LINES BELOW, which carried the same assumption ──────────────────────────────
#
# The race repair (f25935bc5) keyed its own alarm on the EPISODE and left the fall-through alarm it
# had just been carved out of still keying on `f"{status}:{behind}"`. CLAUDE.md's rule is that when
# one control is keyed to a moving answer you grep every sibling; this is that sibling, and these
# two controls are what the grep owed.
#
# MEASURED before it was touched, over the 117 fall-through cadences in
# docs/observability/deadmans-switch-log.md between 2026-09-02 08:28 and 2026-09-05 13:12 (92
# NOT_ADVANCED, 16 REFUSED_CONFLICT, 5 REFUSED_GATE, 4 ERROR): 58 sends under `{status}:{behind}`
# against 36 under the status alone — 22 pages caused by nothing but another lane pushing to
# origin. A LOWER bound: REFUSED_CONFLICT and REFUSED_GATE never print `behind` in their detail
# line, so their moves could not be counted from the log at all.
def test_the_fall_through_forks_state_does_not_move_when_only_behind_moves(fork):
    """THE DEFECT. `behind` counts commits on ORIGIN, so it changes whenever any other lane pushes
    — nothing to do with whether THIS fork closed. Keyed on it, one standing refusal presented a
    new state every five-minute cadence and re-sent every cycle, which is precisely what
    `re_escalate_after=RE_ESCALATE_SECONDS` ("re-alert hourly while still stuck") is there to
    prevent and cannot, because an ever-changing state never reaches the unchanged path.

    MUTATION: restore `state=f"{r['status']}:{r['behind']}"` and this fails.
    """
    fork.run(orc.NOT_ADVANCED, detail="the shared tree will not fast-forward", behind=12)
    fork.run(orc.NOT_ADVANCED, detail="the shared tree will not fast-forward", behind=13)

    assert len(fork.sent) == 2, "the fixture bypasses notify's own suppression; both reach it"
    assert len({kw["state"] for _, kw in fork.sent}) == 1, \
        "one standing refusal is one condition, however far origin has run on"
    assert "12" in fork.sent[0][0] and "13" in fork.sent[1][0], \
        "and the count still belongs in the MESSAGE — it says how bad it is, not whether to tell him"


def test_a_DIFFERENT_refusal_STATUS_is_still_a_different_state(fork):
    """THE OTHER HALF, and without it the repair above is unfalsifiable: `state="OPEN"` passes every
    assertion in the test above and buries a fork whose cause changed under one that had already
    been reported. What may not move the key is `behind`; what MUST move it is the condition.

    MUTATION: hard-wire the state to any constant and this fails while its sibling above passes.
    """
    fork.run(orc.NOT_ADVANCED, detail="the shared tree will not fast-forward", behind=4)
    fork.run(orc.REFUSED_CONFLICT, detail="both lanes edited docs/status/LATEST.md", behind=4)
    fork.run(orc.REFUSED_GATE, detail="the merged tree is red", behind=4)

    assert len({kw["state"] for _, kw in fork.sent}) == 3


# ── the threshold is derived, not picked ────────────────────────────────────────────────────────
def test_the_race_window_is_the_modules_OWN_blocked_threshold(fork):
    """CLAUDE.md: *a number you need is a question to research, never a value to pick.* The question
    "how long may work sit undelivered before that is worth his attention" already has an answer in
    this module, and an open fork is undelivered work. Giving the race a second number would be one
    name carrying two values by another route.

    MUTATION: replace `RACE_PERSISTENCE_SECONDS` with any independent literal and this fails.
    """
    assert ds.RACE_PERSISTENCE_SECONDS == ds.BLOCKED_THRESHOLD_SECONDS
