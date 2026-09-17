"""THE PUBLISH LANDING STARTED RACES IT COULD SEE IT HAD ALREADY LOST.

THE DEFECT, measured 2026-09-17 from `docs/observability/.publish_gate_state.json` (publish
failure #61, `episode_failures: 61`, `episode_clean_publishes: 0`, `last_clean_publish: null`,
`wedge_since` 7.45 days). The landing lost the compare-and-swap on BOTH attempts and recorded
*"the gate's verdict was about a tree that no longer existed and NO test is implicated"*. The two
commits that took it -- `118374229` at +94s into attempt 1 and `ce4806807` at +25s into attempt 2
-- each landed sooner than a gate chain COSTS on this machine (per-chain 250-333s through
September, `docs/observability/commit_hook_duration.jsonl`). A chain that lands 25 seconds after
ours starts did not begin in those 25 seconds: both rivals were already gating when this
publisher began, so neither attempt was winnable, and both were visible to `pgrep` before one
second of CPU was spent.

The repair is not a bigger budget -- the director ruled on 2026-08-21 that no gate budget grows
here, and this spends no gate time at all. It is `_wait_for_a_quiet_tree`: look first, and when
another writer's chain is already in flight, wait for it rather than burning a full chain proving
the tree is hot. Bounded by `_quiet_wait_budget_seconds`, past which the publisher races exactly
as it did before -- so the mechanism's worst case is the behaviour it replaces.

EVERY CONTROL HERE NAMES THE DEFECT IT CATCHES. The three that matter most are the ones a
plausible repair gets wrong: a waiter that can wait for its OWN gate (the shape
`tools/wait_for.py` exists to make unwritable), a wait folded into the per-CHAIN cost series (the
unit defect that wedged every commit in this tree on 2026-09-17, arriving through a new door
within the day), and a wait spent on the attempt that has no attempt after it.
"""
from __future__ import annotations

import inspect
import json
import time

import pytest

import background.process_run_complete as prc

# ---------------------------------------------------------------------------
# the budget: derived from this tree's own record, or absent
# ---------------------------------------------------------------------------

def _series(rows):
    return "\n".join(json.dumps(r) for r in rows) + "\n"


def _plant_series(tmp_path, monkeypatch, rows):
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True, exist_ok=True)
    (obs / prc.COMMIT_HOOK_DURATION_PATH.name).write_text(_series(rows), encoding="utf-8")
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)


def test_the_budget_is_this_trees_own_median_chain_cost_and_a_killed_chain_is_not_one(
        tmp_path, monkeypatch):
    """A NUMBER YOU NEED IS A QUESTION TO RESEARCH, NEVER A VALUE TO PICK. The wait is sized from
    the chain costs this tree actually recorded, and a KILLED chain is not one of them -- its row
    measures the deadline that stopped it, so keeping it would size the wait against the ceiling
    by construction.

    MUTATION: drop the `outcome == "timeout"` filter and the budget jumps to the killed row's
    900s; take a MAX instead of a median and the two known-bad multi-chain totals this machine
    recorded before the 2026-09-17 `chains=` repair (667s and 1381s) set the budget for months.
    """
    _plant_series(tmp_path, monkeypatch, [
        {"duration_seconds": 250.0, "outcome": "refused"},
        {"duration_seconds": 260.0, "outcome": "pass"},
        {"duration_seconds": 270.0, "outcome": "refused"},
        {"duration_seconds": 900.0, "outcome": "timeout"},
        {"duration_seconds": 1381.5, "outcome": "refused"},
    ])

    assert prc._recent_gate_chain_costs() == [250.0, 260.0, 270.0, 1381.5], (
        "the killed chain survived into the cost series, so the budget is sized against the "
        "deadline rather than against the work")
    assert prc._quiet_wait_budget_seconds() == pytest.approx(265.0), (
        "the budget is {}s, not the median of the chains this tree recorded -- a wait sized off "
        "an outlier is a publisher asleep".format(prc._quiet_wait_budget_seconds()))


def test_a_tree_with_no_readable_cost_series_buys_no_wait_at_all(tmp_path, monkeypatch):
    """FAIL-OPEN, AND THE DIRECTION IS THE ARGUMENT. Not waiting costs one publish cycle, retried
    on the next completed run; waiting on a budget nobody can justify costs the cycle itself, and
    a publisher asleep is indistinguishable from the wedge it exists to end.

    This is also why driving the publisher against a scratch repository takes no wait: the series
    is re-derived from `PROJECT_DIR` on every call, so a foreign tree has no budget and cannot
    stall a suite on whatever this machine happens to be gating.

    MUTATION: read the frozen `COMMIT_HOOK_DURATION_PATH` constant instead of re-deriving from
    `PROJECT_DIR`, and a landing into any other checkout starts waiting on THIS tree's rivals.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)

    assert prc._recent_gate_chain_costs() == []
    assert prc._quiet_wait_budget_seconds() == 0.0

    outcome = prc._wait_for_a_quiet_tree("a quiet tree")
    assert outcome["waited_seconds"] == 0.0
    assert outcome["verdict"] == "unbudgeted", (
        "an unbudgeted wait reported {!r} -- the reader cannot tell 'nothing to wait for' from "
        "'no budget to wait with', and only one of those is a defect".format(outcome["verdict"]))


# ---------------------------------------------------------------------------
# the probe: a rival is another writer's chain, never our own
# ---------------------------------------------------------------------------

def test_our_own_gate_chain_is_not_a_rival_and_a_strangers_is(monkeypatch):
    """THE WAITER THAT WAITS FOR ITSELF. `tools/wait_for.py` strikes out this process and its
    ANCESTORS -- that is what stops a waiter matching its own argv -- and it cannot know about a
    DESCENDANT. Every gate this module runs is a descendant, so a probe that only trusts the
    ancestor exclusion can be handed its own child and wait out the whole budget for a process
    that is waiting on it.

    ONE ASSERTION OVER THE WHOLE PARTITION rather than a leg per case: a probe that answers
    "quiet" to everything passes any single-case test, and that is the fail-open direction here.

    MUTATION: drop the `mine not in ancestry(pid)` filter and the own-chain case reports a rival.
    """
    import os

    mine = os.getpid()
    ours, theirs = 4242, 4343

    def ancestry(pid=None):
        if pid is None:
            return {mine}
        return {ours, mine} if pid == ours else {theirs, 1}

    def only(pids):
        return lambda pattern, exclude: (list(pids), len(pids))

    own = prc._rival_gate_probe(matcher=only([ours]), ancestry=ancestry, pattern="x")
    stranger = prc._rival_gate_probe(matcher=only([theirs]), ancestry=ancestry, pattern="x")
    both = prc._rival_gate_probe(matcher=only([ours, theirs]), ancestry=ancestry, pattern="x")

    assert own()[0] is False and stranger()[0] is True and both()[0] is True, (
        "own={} stranger={} both={} -- the probe cannot tell this publisher's own gate from "
        "another writer's, so it either waits for itself or never waits at all".format(
            own()[0], stranger()[0], both()[0]))
    assert str(theirs) in stranger()[1] and str(ours) not in both()[1], (
        "the probe's detail line does not name the rival it is waiting for, so a wait that never "
        "ends leaves nothing in the log to say who held it")


def test_a_probe_that_cannot_look_starts_the_gate_instead_of_holding_the_publish():
    """AN OBSERVER THAT CAN TAKE DOWN WHAT IT OBSERVES IS ITSELF A DEFECT. This function's only
    power is to DELAY, so its failure can cost at most the delay it would have bought -- letting
    an exception out of it would turn an optimisation into an outage of the one pipeline that
    reaches a visible surface.

    But it may not fail SILENTLY either: the reason reaches the returned dict, so a cycle that
    never waited can be told from one that waited and lost.

    MUTATION: re-raise instead of returning, and one unreadable `pgrep` fails every publish.
    """
    def broken():
        raise RuntimeError("pgrep is not on this machine")

    outcome = prc._wait_for_a_quiet_tree("a quiet tree", probe=broken, budget=60.0)

    assert outcome["waited_seconds"] == 0.0
    assert outcome["verdict"] == "unreadable"
    assert "RuntimeError" in outcome["detail"] and "pgrep" in outcome["detail"], (
        "the failure to look was swallowed -- the record says the publisher did not wait and "
        "gives no way to find out why")


def test_every_verdict_the_quiet_wait_can_return_is_reachable():
    """A CONTROL OVER THE WHOLE PARTITION. Each of these four is a different next move for a
    reader of the log -- no budget, nothing to wait for, waited and the rival went, waited out
    the budget -- and a wait that collapses two of them into one sentence is how "it is not
    firing" and "it fired and was not enough" become indistinguishable, which is exactly the
    ambiguity the 2026-09-17 refusal had.

    MUTATION: return a single constant verdict and this reds naming the ones that vanished.
    """
    quiet = prc._wait_for_a_quiet_tree("s", probe=lambda: (False, "nobody"), budget=60.0)

    seen = [False]

    def present_then_gone():
        was, seen[0] = seen[0], True
        return (not was), "rival"

    finished = prc._wait_for_a_quiet_tree(
        "s", probe=present_then_gone, budget=60.0,
        waiter=lambda subject, deadline, probe, emit=None: {
            "verdict": "FINISHED", "waited_seconds": 12.0, "subject": subject, "detail": "gone"})
    expired = prc._wait_for_a_quiet_tree(
        "s", probe=lambda: (True, "rival"), budget=60.0,
        waiter=lambda subject, deadline, probe, emit=None: {
            "verdict": "DEADLINE", "waited_seconds": deadline, "subject": subject, "detail": "!"})
    unbudgeted = prc._wait_for_a_quiet_tree("s", budget=0.0)

    verdicts = {quiet["verdict"], finished["verdict"], expired["verdict"],
                unbudgeted["verdict"]}
    assert verdicts == {"quiet", "FINISHED", "DEADLINE", "unbudgeted"}, (
        "the reachable verdicts are {} -- a branch that cannot be reached is not a branch, and "
        "one that answers for two conditions hides one of them".format(sorted(verdicts)))
    assert expired["waited_seconds"] == 60.0, "an expired budget reported no time spent"


# ---------------------------------------------------------------------------
# the landing: where the wait is taken, and where it must not be counted
# ---------------------------------------------------------------------------

class _FakeBaseMoved(Exception):
    parent = "a" * 40
    observed = "b" * 40


def _drive_landing(tmp_path, monkeypatch, *, land, wait_seconds=0.0, waits=None):
    """Drive the REAL `_land_publish_commit` over a fake `surgical_land.land`.

    The lander is the subject, so it is not stubbed; everything around it is. `land` is called
    with the same `on_lost` production passes, which is the seam the between-attempt wait hangs
    off -- a fake that never calls it would let a broken hook pass.
    """
    from tools import surgical_land

    waits = [] if waits is None else waits
    recorded = []

    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_record_commit_hook_duration",
                        lambda seconds, git_hash, outcome, **kw: recorded.append(
                            (seconds, outcome, kw.get("chains"))))

    def fake_wait(subject, **kwargs):
        waits.append(subject)
        if wait_seconds:
            time.sleep(wait_seconds)
        return {"verdict": "FINISHED", "waited_seconds": wait_seconds, "subject": subject,
                "detail": "fake"}

    monkeypatch.setattr(prc, "_wait_for_a_quiet_tree", fake_wait)
    monkeypatch.setattr(surgical_land, "land", land)

    target = tmp_path / "site" / "data" / "dashboard.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}\n", encoding="utf-8")

    result = prc._land_publish_commit([str(target)], "msg", "abc1234")
    return result, recorded, waits


def test_the_wait_is_not_recorded_as_time_the_gate_spent(tmp_path, monkeypatch):
    """THE UNIT DEFECT, ARRIVING THROUGH A NEW DOOR. `commit_hook_duration.jsonl` is a per-CHAIN
    series graded against the deadline that kills ONE chain: `suite_duration_watch`'s banding,
    its headroom ratio and its transition alarm all read it that way. On 2026-09-17 a multi-chain
    TOTAL in that series reddened the headroom control by seven seconds and refused every commit
    in the shared tree with a demand no re-measurement could satisfy.

    Seconds spent WAITING are not seconds the gate spent either, and folding them in would
    recreate that failure within a day of the repair -- with the added sting that the waiting is
    what the deadline is NOT bounding.

    MUTATION: record `time.monotonic() - started` instead of `_gated_seconds()` and the recorded
    cost carries the wait, which on a real 235s budget is worse than the 667s row that wedged
    the tree.
    """
    gate_seconds, wait_seconds = 0.12, 0.30

    def land(root, paths, message, attempts=None, on_lost=None):
        time.sleep(gate_seconds)
        on_lost(1, _FakeBaseMoved("moved"))
        time.sleep(gate_seconds)
        return "c" * 40

    result, recorded, waits = _drive_landing(
        tmp_path, monkeypatch, land=land, wait_seconds=wait_seconds)

    assert result["sha"] == "c" * 40
    assert len(recorded) == 1
    seconds, outcome, chains = recorded[0]
    assert outcome == "pass" and chains == 2
    assert seconds == pytest.approx(2 * gate_seconds, abs=0.12), (
        "{:.2f}s was recorded as the cost of two gate chains that ran {:.2f}s -- the wait is "
        "inside the stopwatch, so a series the deadline grades now counts time no deadline "
        "bounds".format(seconds, 2 * gate_seconds))
    assert result["waited_seconds"] == pytest.approx(wait_seconds, abs=0.01), (
        "the landing does not report what it waited, so the refusal cannot say whether the race "
        "was entered blind")


def test_a_wait_is_taken_before_the_first_attempt_and_between_attempts_but_never_after_the_last(
        tmp_path, monkeypatch):
    """THREE FACTS IN ONE ASSERTION, because each alone passes a broken version of the other two.

    * Before attempt 1, or the FIRST chain is the one started into a race already running -- and
      in the episode this closes, attempt 1 was the doomed one.
    * Between attempts, or attempt 2 starts into the very writer that just took attempt 1.
    * NEVER after the last attempt: `on_lost` fires on the attempt that EXHAUSTS the loop too,
      and waiting for a quiet tree we will never gate against is pure delay on the path that is
      already the failure.

    MUTATION: drop the `attempt < PUBLISH_LAND_ATTEMPTS` guard and the exhausted landing waits a
    whole budget after its last chain, adding the wait to the wedge it is reporting.
    """
    from tools import surgical_land

    def land(root, paths, message, attempts=None, on_lost=None):
        for attempt in range(1, attempts + 1):
            on_lost(attempt, _FakeBaseMoved("moved"))
        raise surgical_land.LandingRefused(
            "HEAD moved under the gate on all {} attempt(s)".format(attempts))

    result, recorded, waits = _drive_landing(tmp_path, monkeypatch, land=land)

    assert result["sha"] == ""
    assert len(waits) == prc.PUBLISH_LAND_ATTEMPTS, (
        "{} wait(s) for {} attempt(s): {} -- one before each attempt and none after the last is "
        "the only shape that spends no time on a chain that will not run".format(
            len(waits), prc.PUBLISH_LAND_ATTEMPTS, waits))
    assert "1/{}".format(prc.PUBLISH_LAND_ATTEMPTS) in waits[0]
    assert "2/{}".format(prc.PUBLISH_LAND_ATTEMPTS) in waits[1]


def test_the_refusal_says_whether_the_landing_ever_waited(tmp_path, monkeypatch):
    """TWO CONDITIONS WITH OPPOSITE REMEDIES WORE ONE SENTENCE. "Lost the race on all 2 attempts"
    was true of a publisher that started blind and of one that waited out a full budget first --
    the first wants this mechanism fixed, the second wants the GATE's cost cut. A reader who
    cannot tell them apart tunes the wrong one, which is how this wedge reached its fourth
    stretch and its fifth diagnosis.

    MUTATION: drop `_wait_clause` from the evidence and both cycles file the identical string.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    # The live-ledger guard refuses a test process's write to the real observability records --
    # correctly; this cycle records a cause and a gate state, and both belong in tmp_path.
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / "cause.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / "blocking.json")
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / "gate_state.json")
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 0)
    monkeypatch.setattr(prc, "_clear_two_rooms_before_commit", lambda *a, **k: {})
    monkeypatch.setattr(prc, "_commit_pathspec", lambda *a, **k: ["site/data/dashboard.json"])
    monkeypatch.setattr(prc, "_record_commit_refusal_reds", lambda *a, **k: [])

    def refusal(waited):
        """The EVIDENCE AS RECORDED, read back off `publish_cause`'s file rather than off the
        outcome dict -- that file is what every downstream reader of a wedged publish quotes, so
        a clause that never reaches it has not reached anyone."""
        outcome = {}
        monkeypatch.setattr(
            prc, "_land_publish_commit",
            lambda pathspec, msg, git_hash: {
                "sha": "", "refusal": "HEAD moved under the gate on all 2 attempt(s)",
                "lost": [1, 2], "waited_seconds": waited})
        prc.git_commit_push("abc1234", 1000.0, outcome)
        assert outcome["reason"] == prc.COMMIT_REFUSED
        return json.loads(prc.PUBLISH_CAUSE_FILE.read_text(encoding="utf-8"))["evidence"]

    blind, waited = refusal(0.0), refusal(240.0)

    assert blind != waited, (
        "a landing that waited 240s and one that waited none file the identical evidence, so the "
        "record cannot say whether the quiet-tree wait is firing")
    assert "240s" in waited and "NO waiting was bought" in blind, (
        "blind={!r}\nwaited={!r}".format(blind, waited))


def test_the_lander_still_declares_a_chain_count_at_every_recording_exit():
    """THE NEIGHBOUR THIS CHANGE COULD HAVE BROKEN. Subtracting the wait touched all three of
    `_land_publish_commit`'s recording exits, and an exit that loses its `chains=` while gaining
    the subtraction writes a multi-chain total into a per-chain series again -- the 2026-09-17
    defect, restored by the commit repairing its sibling.

    Kept here as well as in `test_a_multi_chain_landing_is_not_recorded_as_one_chain.py` because
    that file grades the COUNT and this one grades the SECONDS, and the two arguments now share
    one expression.
    """
    source = inspect.getsource(prc._land_publish_commit)

    assert source.count("_record_commit_hook_duration(") == 3
    assert source.count("_record_commit_hook_duration(_gated_seconds()") == 3, (
        "a recording exit reads the raw stopwatch rather than the gated seconds, so its row "
        "carries whatever that cycle spent waiting")
    assert source.count("chains=_chains_run(") == 3
