"""Six census carriers whose `benign` verdict had answered a different question.

`benign` on `docs/design/self_clearing_alarm_dispositions.json` means ONE thing: no write to this
file can shorten an episode. 34 of the 46 rows carried no `loader` field, which is a gap and not a
pass -- the question of whether the carrier tells ABSENT from PRESENT-BUT-UNREADABLE had simply
never been put to them. Measured 2026-09-05, against a LIVE PRIOR control leg in every case:

    run_history.json          live prior 100 runs   -> append kept 100, KPI 100
      truncated / empty                             -> kept 1     99 RUNS DESTROYED, KPI 100 -> 1
      null                                          -> TypeError from append AND from BOTH
                                                       dashboard readers (len(None), uncaught)
      {"a": 1} / [1,2,3] / "abc"                    -> AttributeError in append (swallowed by
                                                       _process), and the KPI PUBLISHED 1 / 3 / 3
    .supervisor_map_exhausted_state.json
      null / [1,2,3] / "abc"                        -> AttributeError at supervisor.py's
                                                       `state.get`, inside the supervisor cycle
    .wedge_suspect_hit_rate.json  live prior 20 eps -> all seven unreadable states left 1
    .harden_cooldown.json         live prior 8 atoms-> all seven loaded 0; the next stamp writes 1
    .ntfy_digest_state.json       live prior 5 pend -> all seven returned 30 (the whole queue),
      null / [1,2,3] / "abc"                        -> AttributeError in pending()
    retired_paths_served.json     [1,2,3] / "abc"   -> AttributeError in transitions()

THE LIVE-PRIOR LEG IS NOT DECORATION. Without it every assertion below is satisfiable by a
harness that destroys the prior itself, or by a loader that returns empty unconditionally -- and
"the corrupt case matches the good case" would then read as a pass. It is asserted FIRST in each
test, and it is what makes the unreadable legs mean something.

WHAT IS PINNED IS THE PROPERTY, NOT TODAY'S ANSWER. These do not assert a run count or an episode
count; they assert that a readable record is fully accounted for, that an unreadable one is never
silently rebuilt over, and that no member of the partition raises. A repair that makes the code
MORE honest keeps them green.

MUTATIONS THESE MUST CATCH (each verified to fail this file):
  * `load_list_prior(hp, item_type=dict)` -> `load_list_prior(hp)`     (items unscreened again)
  * `preserve_unreadable(hp)` deleted from append_run_history / _append_suspect_outcome
  * `load_episode_prior(X)` -> `json.loads(X.read_text())` in any of the four loaders
  * `count_run_history_total` returning `len(json.loads(...))` again
  * any loader's `isinstance` screen widened to admit a non-mapping / non-list
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from background import notification_digest as nd  # noqa: E402
from background import process_run_complete as prc  # noqa: E402
from background import supervisor as sup  # noqa: E402
from tools import generate_dashboard_data as gdd  # noqa: E402
from tools import generate_insights as gi  # noqa: E402
from tools import retired_paths_still_served as rp  # noqa: E402

#: Every way a state file can exist and not be usable. `null`, a mapping, a list of the wrong
#: items and a bare string all PARSE -- which is why an `except JSONDecodeError` never saw them,
#: and why they are the members that were actually live.
UNREADABLE_RAW = pytest.mark.parametrize("raw", [
    pytest.param("", id="empty-file"),
    pytest.param('{"a": 1', id="truncated"),
    pytest.param("null", id="json-null"),
    pytest.param("[1, 2, 3]", id="list-of-ints"),
    pytest.param('"abc"', id="a-bare-string"),
])

LIVE_HISTORY = [
    {"git_hash": "abc%03d" % i, "generated_at": "t%d" % i, "net_margin_gbp": 1.0,
     "executive_summary": "s", "headline_metrics": {}}
    for i in range(100)
]


def _insights(git_hash="deadbeef"):
    return gi.RunInsights(git_hash=git_hash, generated_at="now", net_margin_gbp=42.0,
                          executive_summary="a new run", insights=[])


def _carrier(tmp_path: Path, name: str) -> Path:
    """A state file in a directory of its OWN. `tmp_path` is shared with session fixtures that
    drop `sim_runner_real_tree/` into it, and `_preserved_beside` would then read a directory --
    the first draft of this file failed 13 ways on exactly that, which is a harness defect
    masquerading as a code one."""
    d = tmp_path / name.lstrip(".").replace(".", "_")
    d.mkdir()
    return d / name


def _preserved_beside(p: Path) -> list[str]:
    """The bytes `preserve_unreadable` moved aside, read back. A list so "nothing was kept" and
    "something was kept" are different values rather than a bool nobody can debug."""
    return [f.read_text() for f in p.parent.iterdir() if f.name != p.name and f.is_file()]


# --------------------------------------------------------------- run_history.json

def test_a_readable_run_history_is_fully_accounted_for(tmp_path):
    """REACHABILITY, and it is load-bearing for every assertion below. A loader that answered
    empty unconditionally would satisfy all of them; this is the leg that refuses it.

    MUTATION: make `load_list_prior` return `([], UNREADABLE)` always -- only this test fails,
    and that is exactly the signal, because such a loader is a total data loss the others call
    correct."""
    p = _carrier(tmp_path, "run_history.json")
    p.write_text(json.dumps(LIVE_HISTORY))
    assert gdd.count_run_history_total(p) == 100
    assert len(gdd.extract_run_history(p)) == 10
    gi.append_run_history(_insights(), p)
    assert len(json.loads(p.read_text())) == 100, "100 kept + 1 new, capped at 100"
    assert not _preserved_beside(p), "a READABLE prior must never be moved aside"


@UNREADABLE_RAW
def test_an_unreadable_run_history_is_preserved_rather_than_written_over(tmp_path, raw):
    """The read-modify-write is the defect, not the read. `history = []` followed by a write is
    how 100 runs became 1 -- and the run count is PUBLISHED, so the loss reached the director's
    own Project tab as a plausible smaller number.

    MUTATION: delete the `preserve_unreadable(hp)` call -- the rebuild still happens (that is
    correct and unavoidable; the process must keep running), so the ONLY evidence the record
    existed is the preserved copy."""
    p = _carrier(tmp_path, "run_history.json")
    p.write_text(raw)
    gi.append_run_history(_insights(), p)
    assert raw in _preserved_beside(p), "the unreadable bytes are the only copy of the record"


@UNREADABLE_RAW
def test_the_published_run_count_is_never_fabricated_from_a_corrupt_record(tmp_path, raw):
    """`len()` answers for a string and for a list of ints, so `"abc"` published "Sim runs: 3".
    A count is a claim about runs we can account for; a record we cannot parse accounts for none.

    Asserts the two readers AGREE as well as their value: a KPI that disagrees with the list it
    is drawn from is the severity-column defect wearing different clothes.

    MUTATION: `item_type=dict` -> unscreened; `[1, 2, 3]` returns 3 again and this reds."""
    p = _carrier(tmp_path, "run_history.json")
    p.write_text(raw)
    assert gdd.count_run_history_total(p) == 0
    assert gdd.extract_run_history(p) == []
    assert gdd.count_run_history_total(p) == len(gdd.extract_run_history(p))


def test_the_run_history_readers_answer_zero_for_absent_and_for_unreadable_alike(tmp_path):
    """The CONFLATION here is deliberate and this pins that it was chosen, not overlooked: both
    render 0, because a display of "runs we can account for" is honest in both cases. What is NOT
    conflated is the disposal of the bytes -- absent has none, unreadable keeps its own."""
    absent = _carrier(tmp_path, "gone.json")
    assert gdd.count_run_history_total(absent) == 0
    gi.append_run_history(_insights(), absent)
    assert not _preserved_beside(absent), "there was nothing to preserve"


# ------------------------------------------- .supervisor_map_exhausted_state.json

@pytest.fixture
def map_state(tmp_path, monkeypatch):
    """`MAP_EXHAUSTED_STATE_FILE` is an absolute path into the shared tree. Repointed FIRST,
    before anything is called, so a failing branch cannot write a live observability surface --
    and `ntfy` is stubbed so a red here can never page the director."""
    p = tmp_path / ".supervisor_map_exhausted_state.json"
    monkeypatch.setattr(sup, "MAP_EXHAUSTED_STATE_FILE", p)
    sent: list = []
    monkeypatch.setattr(sup, "ntfy", lambda *a, **k: sent.append(a))
    monkeypatch.setattr(sup, "log", lambda *a, **k: None)
    return p, sent


def test_a_recorded_exhausted_state_still_suppresses_the_repeat_escalation(map_state):
    """REACHABILITY for the partition below: the edge detector must be able to SUPPRESS, or
    "no escalation" would be free and the unreadable legs would prove nothing."""
    p, sent = map_state
    p.write_text(json.dumps({"exhausted": True}))
    sup.check_map_exhausted_escalation(True)
    assert sent == [], "an unchanged exhausted state must not re-page (R5)"
    sup.check_map_exhausted_escalation(False)
    assert json.loads(p.read_text()) == {"exhausted": False}, "and it must clear"


@UNREADABLE_RAW
def test_the_supervisor_cycle_survives_a_map_exhausted_state_it_cannot_read(map_state, raw):
    """The raise did not kill the supervisor -- `main` catches everything -- it stopped the CYCLE
    completing, every two minutes, forever, while the log read like the mechanism working. That
    is the alive-and-deaf shape, and it fired on the branch whose whole job is to make a stuck
    machine visible.

    Losing the suppression (one duplicate NTFY of an escalation we WANT sent) is the accepted
    cost and is asserted here as the intended behaviour, not merely tolerated.

    MUTATION: restore `json.loads(...)` under `except (JSONDecodeError, OSError)` -- three of the
    five ids raise again."""
    p, sent = map_state
    p.write_text(raw)
    sup.check_map_exhausted_escalation(True)          # must not raise
    assert len(sent) == 1, "an unreadable prior fails OPEN to escalating, never to silence"
    assert json.loads(p.read_text()) == {"exhausted": True}, "and it re-arms the suppression"


# ------------------------------------------------- .wedge_suspect_hit_rate.json

def test_a_readable_suspect_series_keeps_every_earlier_episode(tmp_path):
    """REACHABILITY. H42's measured evidence is a series; an appender that kept only the newest
    would pass every corrupt-file test below."""
    p = _carrier(tmp_path, ".wedge_suspect_hit_rate.json")
    # Sized off the module's OWN cap rather than a literal: at exactly the cap the append is
    # indistinguishable from a total reset, which is the assertion this leg exists to make.
    prior = max(2, prc.WEDGE_SUSPECT_HIT_RATE_MAX_EPISODES - 3)
    p.write_text(json.dumps({"episodes": [{"ep": i} for i in range(prior)]}))
    prc._append_suspect_outcome({"ep": "new"}, p)
    assert len(json.loads(p.read_text())["episodes"]) == prior + 1


@UNREADABLE_RAW
def test_an_unreadable_suspect_series_is_preserved_before_it_is_rebuilt(tmp_path, raw):
    """This one destroys silently and reads afterwards as "not yet measured" -- the flattering
    reading, and the reason the row was ranked above the pure readers.

    MUTATION: delete the preserve -- the series still resets to 1 (unavoidable) and nothing
    anywhere records that 20 episodes existed."""
    p = _carrier(tmp_path, ".wedge_suspect_hit_rate.json")
    p.write_text(raw)
    prc._append_suspect_outcome({"ep": "new"}, p)
    assert raw in _preserved_beside(p)


# ----------------------------------------------------- .ntfy_digest_state.json

@pytest.fixture
def digest(tmp_path, monkeypatch):
    sp, qp = tmp_path / ".ntfy_digest_state.json", tmp_path / "ntfy_digest_queue.jsonl"
    monkeypatch.setattr(nd, "STATE_FILE", sp)
    monkeypatch.setattr(nd, "QUEUE_FILE", qp)
    qp.write_text("\n".join(json.dumps({"seq": i, "text": "n%d" % i}) for i in range(1, 31)))
    return sp


def test_a_readable_digest_watermark_holds_back_what_was_already_sent(digest):
    """REACHABILITY: the watermark must be able to suppress 25 of 30, or "returns everything"
    below is not a finding."""
    digest.write_text(json.dumps({"digested_through_seq": 25, "last_digest_ts": 1e12}))
    assert len(nd.pending()) == 5


@UNREADABLE_RAW
def test_an_unreadable_digest_watermark_does_not_stop_the_flush_by_raising(digest, raw):
    """Two consequences, one cause. `null` / `[1,2,3]` / `"abc"` raised AttributeError out of
    `pending()`, so nothing flushed at all; the truncated file read the watermark as 0, which is
    a REPLAY of every notification ever deferred rather than a lost suppression.

    The replay is left unguarded on purpose -- the next successful flush rewrites the watermark
    from the entries it actually carried, so the record self-repairs and the replay is loud
    enough to notice. What is NOT acceptable is the raise, and that is what this pins."""
    digest.write_text(raw)
    assert len(nd.pending()) == 30, "fails open to sending too much, never to silence"


# -------------------------------------------------- retired_paths_served.json

def test_the_retired_path_watcher_reports_only_what_changed_against_a_readable_prior():
    """REACHABILITY for the partition below: `transitions` must be able to report NOTHING."""
    prev = {"paths": {"/x/": {"still_served": True, "last_seen": "h"}}}
    assert rp.transitions(prev, {"/x/": {"still_served": True, "last_seen": "h"}}) == []


@UNREADABLE_RAW
def test_an_unreadable_retired_path_prior_re_reports_rather_than_raising(tmp_path, monkeypatch,
                                                                        raw):
    """`null` answered correctly BY ACCIDENT -- `None or {}` is `{}` -- which is what made the
    list and string members look impossible.

    THE SUBJECT IS `rp._load_previous_state`, NOT `load_episode_prior`. The first draft called the
    helper directly and SURVIVED the mutation that restored the old inline `except ValueError`
    read: it was asserting the helper against itself while the caller went unexamined. `run()`
    cannot be called instead -- it refuses without a real site checkout -- so the module grew the
    named seam this asks.

    No preserve is earned: `current` is recomputed in full from the edge rows. The cost is that
    every live ghost re-reports once, which is noisy and not wrong -- pinned as intended, so a
    later reader does not "fix" it into silence."""
    p = _carrier(tmp_path, "retired_paths_served.json")
    p.write_text(raw)
    monkeypatch.setattr(rp, "STATE", p)
    changes = rp.transitions(rp._load_previous_state(),
                             {"/x/": {"still_served": True, "last_seen": "h"}})
    assert len(changes) == 1 and "NEW GHOST" in changes[0]
