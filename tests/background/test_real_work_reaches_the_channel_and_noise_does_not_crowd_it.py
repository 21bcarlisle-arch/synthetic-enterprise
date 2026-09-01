"""THE CHANNEL CARRIED WHAT WENT WRONG AND NOTHING OF WHAT GOT DONE.

Director, 2026-09-01: *"the channel under-reports you. Eight commits this evening produced no
message, while divergence and publishing alarms filled the mirror. I've read that as a stall twice
today when you were working normally. Real work should reach the channel and routine noise shouldn't
crowd it out."*

Measured before touching anything, from the outbound mirror and the digest queue for that day:

    64 outbound messages.  27 of them ONE tree-divergence condition.  20 publishing.
    19 commits landed.     0 landing notifications, instant or batched.
    Digest queue, whole life: 718 findings, 693 divergence, 358 drift, 1 routine landing.

Three defects, one per half of his sentence and one in between:

  SILENCE.   `routine_landing` -- one of the four deferrable categories he named himself in 2026-08-
             12 -- had no producer. Not delayed: never sent. The KINDS set is why nothing could be
             one: every member is a thing that went wrong, a batch of those, a reply, or a fixture.
  NOISE.     Tree divergence passed `top_squatters(m)` as its transition `state`, and that string
             carries an age in HOURS. One unchanging squat (the same file, 92.6h -> 110.4h across
             the day) was therefore a NEW state on every cycle: 27 pages, and -- worse -- the
             repeat-escalation that turns a nagging alarm into a drawn work item counts repeats of
             an UNCHANGED state, so the one condition that most deserved to become work was
             structurally unable to.
  CROWDING.  `compose()` rendered classes in `sorted()` order and spent its 25-line budget greedily,
             so `routine_landing` came last of four and 42 queued findings would have elided every
             landing even once they had a producer.
"""
from __future__ import annotations

import inspect

import pytest

from background import notification_digest as nd
from background import notify as notify_mod
from background import tree_divergence as td
from tools import surgical_land


# ── SILENCE: a landing reaches the channel ──────────────────────────────────────────────────
def test_a_landing_announces_itself_as_work_done_and_batches():
    """MUTATION: delete the `announce_landing(...)` call in `land()` and this fails -- which is the
    state the channel was in all day."""
    sent = {}

    def _fake(msg, **kw):
        sent.update(kw, message=msg)
        return "deferred:1"

    surgical_land.announce_landing("abc123def456", "the shock split lands", ["a.py", "b.py"],
                                   _notify=_fake)
    assert sent["kind"] == "work_done"
    assert sent["topic_class"] == nd.ROUTINE_LANDING
    assert "abc123def" in sent["message"] and "the shock split lands" in sent["message"]


def test_the_landing_door_actually_calls_it():
    """The producer must sit at the ONE door. `--no-verify` is a wall and this is the legal move,
    so a producer anywhere else reports only that caller's landings."""
    assert "announce_landing(" in inspect.getsource(surgical_land.land)


def test_a_landing_is_never_suppressed_as_a_repeat_of_another_landing():
    """An unkeyed `real_alarm` auto-keys on its own message with numbers normalised away (G-N4), so
    two landings with similar subjects would dedup and the second would silently vanish. `work_done`
    exists so that cannot happen, and this pins the reason rather than the spelling.

    MUTATION: change the kind to `real_alarm` in `announce_landing` and this fails.
    """
    src = inspect.getsource(surgical_land.announce_landing)
    assert 'kind="work_done"' in src
    assert "transition_key" not in src.split("_notify(")[-1].split("except")[0].replace(
        "# No transition key.", "")


def test_a_landing_can_never_page_him_instantly():
    """It is routine by construction: a landing is not action-needed, and batching was his own
    instruction. If `routine_landing` ever left the deferrable set this would be a page per commit,
    which is the opposite failure."""
    assert not nd.is_instant(nd.ROUTINE_LANDING)


def test_work_done_is_a_declared_kind_with_its_own_tag():
    """G-N2: the type is STRUCTURAL and the director sees it. Work done must not arrive wearing an
    alarm's tag -- the tag is how he tells 'I did something' from 'something is wrong' at a glance,
    which is the distinction the whole channel was missing."""
    assert "work_done" in notify_mod.KINDS
    assert notify_mod._KIND_TAG["work_done"] != notify_mod._KIND_TAG["real_alarm"]


# ── NOISE: one condition is one state ───────────────────────────────────────────────────────
def _measure(lanes, oldest, total):
    return {"by_lane": {ln: {"count": 5, "oldest_age_hours": oldest} for ln in lanes},
            "total_files": total, "oldest_age_hours": oldest}


def test_the_same_squat_ageing_is_the_same_state():
    """THE 27-PAGE DEFECT, in one assertion. Same lanes, a day older, a few files either way.

    MUTATION: return `top_squatters(m)` from `divergence_state` and this fails -- the state moves,
    the transition check suppresses nothing, and the repeat-escalation never counts to three.
    """
    a = _measure(["W2", "D"], 92.6, 252)
    b = _measure(["W2", "D"], 110.4, 263)
    assert td.divergence_state(a) == td.divergence_state(b)


def test_a_new_lane_squatting_is_a_new_state():
    """The suppression must not become deafness: a lane starting or finishing is a real change and
    still pages at once."""
    assert td.divergence_state(_measure(["W2"], 5.0, 20)) \
        != td.divergence_state(_measure(["W2", "D"], 5.0, 20))
    assert td.divergence_state(_measure(["W2", "D"], 5.0, 20)) \
        != td.divergence_state(_measure(["D"], 5.0, 20))


def test_an_unmeasurable_tree_has_its_own_state():
    """An unavailable measure is severe and must not share a state with any real reading."""
    st = td.divergence_state({"unavailable": True, "unavailable_reason": "x"})
    assert st == "unavailable" and st != td.divergence_state(_measure(["W2"], 1.0, 1))


def test_the_publisher_passes_the_identity_not_the_rendering():
    from background import process_run_complete as prc
    src = inspect.getsource(prc._publish_tree_divergence)
    assert "state=_td.divergence_state(m)" in src
    assert "state=_td.top_squatters(m)" not in src


# ── CROWDING: every class gets a floor, and work leads ───────────────────────────────────────
def test_landings_are_not_elided_by_a_loud_class():
    """THE REAL NUMBERS from 2026-09-01: 42 findings and 13 drift queued against a 25-line budget.
    Under the old greedy-in-sorted-order spend, all eight landings were elided.

    MUTATION: restore `for cls in sorted(by_class)` with a shared greedy budget and this fails.
    """
    entries = []
    for cls, n in (("finding_announcement", 42), ("drift", 13), ("routine_landing", 8)):
        for i in range(n):
            entries.append({"seq": len(entries) + 1, "class": cls, "message": f"{cls} {i}"})
    text = nd.compose(entries)
    assert text.count("routine_landing ") >= 1
    assert sum(1 for ln in text.splitlines() if "routine_landing " in ln and ln.startswith("   #")) == 8


def test_what_was_done_leads_the_digest():
    entries = [{"seq": 1, "class": "drift", "message": "d"},
               {"seq": 2, "class": "routine_landing", "message": "l"}]
    body = nd.compose(entries).splitlines()
    assert body[1].startswith("— routine_landing"), body


def test_every_class_present_gets_at_least_one_line():
    """The floor. A class that queued one item must not be invisible because another queued forty --
    the same discipline as a population floor on a scanning control."""
    entries = [{"seq": i, "class": "finding_announcement", "message": "f"} for i in range(1, 200)]
    entries.append({"seq": 999, "class": "drift", "message": "the one drift notice"})
    text = nd.compose(entries)
    assert "the one drift notice" in text


def test_elision_still_names_the_file_that_holds_everything():
    """G-N4 is untouched: nothing is dropped, and a digest that hides its own truncation is how a
    batched item becomes a lost one."""
    entries = [{"seq": i, "class": "drift", "message": f"d{i}"} for i in range(1, 200)]
    text = nd.compose(entries)
    assert "more not shown" in text and nd.QUEUE_FILE.name in text
