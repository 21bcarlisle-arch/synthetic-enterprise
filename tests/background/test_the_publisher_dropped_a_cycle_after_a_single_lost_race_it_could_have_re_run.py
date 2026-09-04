"""THE DEFECT: the publish path's fork-advance was single-shot, so a commit arriving on origin
during the ~1s fast-forward discarded a whole completed cycle that one more second would have saved.

`ab6240611` gave the publisher `_advance_to_origin_or_say_why()` and a re-read, which is right and
is not what changes. What it did next was: refuse. Its docstring argued for that, on an estimate --
*"a second attempt would buy a fraction of a percent and cost a second network round trip"* -- and
the frequency in that estimate is correct. Measured 2026-09-04 after the fact, and the
pre-registration filed first (`SEAT_PREREGISTRATION_HOW_WIDE_THE_PUBLISHERS_LOST_RACE_WINDOW
_ACTUALLY_IS_2026-09-04.md`) predicted a WIDER window than the one that turned up and was refuted:

  * W = 0.873s exposed (n=5) -- two `git fetch` round trips to GitHub plus a 0.006s `--ff-only`.
  * 292s median gap between commits on `origin/main` (n=57 over 6h).
  * P(one attempt loses) = 0.30%; residual after three ~2.7e-8.

What the estimate got wrong was WHERE the round trip is spent, and it inverts the conclusion: a
retry that fires only on a LOST race costs nothing in the 99.7% of cycles that clear first time, so
it is 0.87s weighed against the 672s of simulation and gate the losing 0.30% throws away.

WHAT IS ASSERTED HERE is the loop's control flow, which is the publisher's own branching -- so the
divergence OBSERVATION is scripted and everything downstream of it is real, including
`_divergence_refusal` itself. The advance's contact with git is a different subject and is measured
against real repositories in
`test_a_publish_that_lost_the_race_closes_a_mechanical_fork_before_refusing.py`.

THE SAFETY PROPERTY, and it is the one worth breaking things over: the loop is over the LOST RACE
and nothing else. `surgical_land.land` retries only `BaseMoved` for the same reason -- a lost race
means the verdict described a tree that no longer exists, while every other refusal means it
described the right tree and said no. Retrying THAT is the 2026-09-01 incident, in which the publish
loop treated a non-fast-forward rejection as a transient and added an unpushable commit every twelve
minutes for nine hours.
"""
from __future__ import annotations

import contextlib
import types

import pytest

from background import process_run_complete as prc
from background import publish_cause as pc

ADVANCED = {"advanced": True, "reason": "fast-forwarded the shared tree onto origin/main"}
REAL_FORK = {"advanced": False, "reason": "this tree holds 1 commit(s) of its own, so the fork is "
                                          "REAL and closing it is a judgement"}
GIT_REFUSED = {"advanced": False, "reason": "git REFUSED the fast-forward (rc=128), which is the "
                                            "guard working and not a fault"}
UNREADABLE = {"advanced": False, "reason": "origin could not be fetched (rc=128), so the ref this "
                                           "would advance onto was never read"}


def _drive(monkeypatch, tmp_path, *, ahead_reads, advances):
    """Run `git_commit_push` with the divergence reads and the advance verdicts scripted.

    `ahead_reads` is consumed one per `_commits_origin_is_ahead_by()` call -- so it IS the story of
    what origin did while this cycle ran, and `_divergence_refusal` turns it into a refusal for
    real. `advances` is consumed one per advance; its last entry repeats, so a test can say "origin
    stays hot forever" without deciding how many times the loop will ask.

    Returns (returned, reason, evidence, advance_call_count, git_commands).
    """
    reads = list(ahead_reads)
    script = list(advances)
    seen = {"advances": 0}

    def next_ahead():
        # POP, NOT INDEX-AND-CLAMP. Running off the end must raise, because a loop that asks one
        # more time than the story accounts for is exactly the defect a clamped stub would hide.
        return reads.pop(0)

    def next_advance():
        seen["advances"] += 1
        return script.pop(0) if len(script) > 1 else script[0]

    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / "cause.json")
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_push_due", lambda: False)
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", next_ahead)
    monkeypatch.setattr(prc, "_advance_to_origin_or_say_why", next_advance)

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    outcome = {}
    returned = prc.git_commit_push("abc1234", 1000.0, outcome=outcome)
    # THE EVIDENCE IS READ BACK FROM THE CAUSE FILE, which is where the reader reads it -- the
    # outcome dict carries only the reason. Asserting on the string the code built, rather than on
    # the one that reached the record, would pass on a refusal whose evidence was never written.
    _cause, evidence = pc.read_cause(tmp_path / "cause.json", "abc1234")
    return returned, outcome.get("reason"), evidence or "", seen["advances"], calls


def _committed(calls) -> bool:
    return any(c[:2] == ["git", "commit"] for c in calls)


# ── Reachability first: every leg of the partition must be attainable ────────────────────────

def test_all_three_ends_of_the_loop_are_reachable_and_not_one_of_them_always(tmp_path,
                                                                            monkeypatch):
    """ONE CONTROL OVER THE WHOLE PARTITION, before any control over what a single leg does.

    A bounded retry has three ends -- cleared first time, cleared after losing, exhausted -- and a
    loop that took any ONE of them unconditionally would pass a per-leg suite written the obvious
    way. CLAUDE.md's rule, learned by entering that trap three times in one afternoon: assert the
    rare branch CAN be taken before asserting what it does.

    MUTATION: set `PUBLISH_ADVANCE_ATTEMPTS = 1` and the middle leg reds (the recovery becomes
    unreachable); remove the `break` on a clean re-read and the first leg reds.
    """
    first_time = _drive(monkeypatch, tmp_path, ahead_reads=[2, 0], advances=[ADVANCED])
    after_losing = _drive(monkeypatch, tmp_path, ahead_reads=[2, 1, 0], advances=[ADVANCED])
    exhausted = _drive(monkeypatch, tmp_path, ahead_reads=[2, 1, 1, 1], advances=[ADVANCED])

    assert _committed(first_time[4]) and first_time[3] == 1
    assert _committed(after_losing[4]) and after_losing[3] == 2
    assert not _committed(exhausted[4]) and exhausted[1] == prc.BEHIND_ORIGIN


# ── The recovery this change exists for ──────────────────────────────────────────────────────

def test_a_race_lost_by_one_commit_is_re_run_instead_of_discarding_the_cycle(tmp_path,
                                                                            monkeypatch):
    """THE DEFECT ITSELF. Origin moves once more during the 0.87s advance; the old code refused
    there and threw away a full simulation and a 672s gate.

    MUTATION: `break` unconditionally after the first re-read and this reds -- no commit is made.
    """
    returned, reason, _evidence, advances, calls = _drive(
        monkeypatch, tmp_path, ahead_reads=[3, 1, 0], advances=[ADVANCED])

    assert advances == 2, "the second advance is the whole repair"
    assert reason != prc.BEHIND_ORIGIN
    assert _committed(calls), \
        "a cycle that could be published by one more 0.9s fast-forward must be published"
    assert returned is True


def test_the_loop_is_bounded_and_a_hot_origin_still_ends_in_a_refusal(tmp_path, monkeypatch):
    """An origin that keeps moving must exhaust the bound and REFUSE, not spin inside a publish
    cycle that has to finish. The bound is read from the constant, not from the number 3, so the
    control follows the dial rather than pinning today's setting.

    MUTATION: make the loop `while True` and this hangs/reds; raise the bound and it still passes.
    """
    _returned, reason, _evidence, advances, calls = _drive(
        monkeypatch, tmp_path,
        ahead_reads=[9] * (prc.PUBLISH_ADVANCE_ATTEMPTS + 1), advances=[ADVANCED])

    assert advances == prc.PUBLISH_ADVANCE_ATTEMPTS
    assert reason == prc.BEHIND_ORIGIN
    assert not _committed(calls), "an exhausted retry is a refusal, never a commit"


# ── The safety asymmetry: only a LOST RACE is retryable ──────────────────────────────────────

@pytest.mark.parametrize("verdict, what", [
    (REAL_FORK, "we hold commits of our own, so no fast-forward can ever close it"),
    (GIT_REFUSED, "git refused, and git's refusal IS the guard"),
    (UNREADABLE, "origin could not be read, so nothing was observed to act on"),
])
def test_a_refusal_to_advance_is_never_retried_however_many_attempts_remain(verdict, what,
                                                                           tmp_path, monkeypatch):
    """THE PROPERTY THAT KEEPS THIS FROM BEING THE 2026-09-01 RETRY. That incident was a publish
    loop treating a STATE as a transient: `origin/main..HEAD` = 3 against `HEAD..origin/main` = 23,
    two of the three local commits made by the loop itself, after its own push had already been
    rejected non-fast-forward. Each identical re-attempt made it one commit worse.

    None of the three verdicts below is a moment that re-running can change, so each must be
    terminal on attempt ONE -- with two attempts still unspent, which is what makes this a control
    over the asymmetry and not over the bound.

    MUTATION: delete the `if not _advance["advanced"]: break` and every case here reds at
    `advances == 1`, because the loop runs the full three.
    """
    _returned, reason, evidence, advances, calls = _drive(
        monkeypatch, tmp_path, ahead_reads=[4], advances=[verdict])

    assert advances == 1, "not retryable: " + what
    assert reason == prc.BEHIND_ORIGIN
    assert not _committed(calls)
    assert verdict["reason"][:40] in evidence, \
        "the refusal must carry the advance's own reason, not a summary of it"


def test_a_lost_race_and_a_real_fork_do_not_read_the_same_in_the_refusal(tmp_path, monkeypatch):
    """Two causes now end at `BEHIND_ORIGIN`, and they are tuned by different people: three lost
    races means origin is hotter than the 292s this bound was set against and the BOUND is the
    thing to revisit; a refusal to advance means the fork is real and no bound would have helped.
    A reader who cannot tell them apart tunes the wrong one -- which is the failure the
    `NOT_ADVANCED`-names-no-cause finding recorded three separate seats making by hand.

    MUTATION: drop the `if _lost:` re-wording and this reds -- both refusals read identically.
    """
    _r1, _c1, lost_evidence, _a1, _g1 = _drive(
        monkeypatch, tmp_path,
        ahead_reads=[9] * (prc.PUBLISH_ADVANCE_ATTEMPTS + 1), advances=[ADVANCED])
    _r2, _c2, fork_evidence, _a2, _g2 = _drive(
        monkeypatch, tmp_path, ahead_reads=[9], advances=[REAL_FORK])

    assert lost_evidence != fork_evidence
    assert "SUCCEEDED" in lost_evidence and str(prc.PUBLISH_ADVANCE_ATTEMPTS) in lost_evidence, \
        "an exhausted retry must say the fast-forwards WORKED and origin outran them anyway"
    assert "REAL" in fork_evidence and "SUCCEEDED" not in fork_evidence, \
        "a real fork must not be reported as a lost race"


def test_the_bound_is_more_than_one_and_is_not_a_free_dial_on_the_refusal(tmp_path, monkeypatch):
    """Keyed to the PROPERTY, not to today's 3. Two things must both hold: the bound permits a
    retry at all (=1 restores the defect), and raising it cannot convert a refusal into a publish,
    because the loop breaks on the first non-advance. The second is what makes the first safe.

    MUTATION: `PUBLISH_ADVANCE_ATTEMPTS = 1` reds the first assertion.
    """
    assert prc.PUBLISH_ADVANCE_ATTEMPTS > 1

    monkeypatch.setattr(prc, "PUBLISH_ADVANCE_ATTEMPTS", 50)
    _returned, reason, _evidence, advances, calls = _drive(
        monkeypatch, tmp_path, ahead_reads=[4], advances=[REAL_FORK])

    assert advances == 1 and reason == prc.BEHIND_ORIGIN and not _committed(calls), \
        "attempts is CPU spent on a race, never permission to publish onto a real fork"
