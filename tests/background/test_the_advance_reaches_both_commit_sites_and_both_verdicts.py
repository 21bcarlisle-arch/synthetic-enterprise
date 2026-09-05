"""THE ADVANCE MADE TWO VERDICTS STALE AND ONLY ONE WAS RE-READ (2026-09-04).

`_advance_to_origin_or_say_why` landed earlier today and is right: when the fork is mechanical it
fast-forwards, and `git_commit_push` then RE-READS `_divergence_refusal` rather than assuming the
act had its effect. This suite is about the two things that repair did not reach, both found by
asking the question its own docstring asks -- *what else did the fast-forward invalidate?*

**ONE — the fail-closed provenance check graded the tree as it was BEFORE the move.**
`_provenance_is_publishable` runs ~40 lines ahead of the advance and reads
`site/data/publish_provenance.json` and `site/data/dashboard.json` FROM DISK. A fast-forward
rewrites every tracked path this tree has not modified. Origin is another publisher pushing that
same pair, so "origin changed the provenance file" is the ordinary case and "we did not modify it
this cycle" is any cycle that regenerated equal bytes -- and then this run's dashboard is committed
beside another run's provenance, which is precisely what `dashboard_meta_violations` exists to
refuse, arriving through the one door that had already been opened.

**TWO — the advance was wired at one of the two commit sites.** `_commit_and_push_paths` -- the
liveness heartbeat and the red-cycle banner -- carried the bare refusal. Those are the surfaces
whose whole job is to say the system is alive or behind, published exactly when content is not
publishing, so a fork silences them in the one state they exist for.

BOTH LEGS, EVERYWHERE. A re-check that refuses everything and a re-check that refuses nothing pass
different halves of this file, so every refusal here has a null beside it on the same fixture.
"""

from __future__ import annotations

import contextlib
import types

import pytest

from background import process_run_complete as prc


@pytest.fixture()
def publisher(tmp_path, monkeypatch):
    """`process_run_complete` with its world neutralised and every git call recorded.

    STUBBED, and the subject says why: what git answers on a forked tree is measured against real
    git in the two sibling suites. The subject HERE is the publisher's own branching -- which
    verdicts it re-reads after it acts -- and that is only visible with the observations held.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / "cause.json")
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_push_due", lambda: False)
    monkeypatch.setattr(prc, "_commit_pathspec", lambda *a, **k: ["site/data/dashboard.json"])
    monkeypatch.setattr(prc, "_clear_two_rooms_before_commit", lambda *a, **k: {})
    monkeypatch.setattr(prc, "_record_commit_hook_duration", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_git_add_or_refuse", lambda *a, **k: True)

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    return calls


def _committed(calls):
    return any(c[:2] == ["git", "commit"] for c in calls)


def _staged(calls):
    return any(c[:2] == ["git", "add"] for c in calls)


def _cleared_by_the_advance(monkeypatch, *, advanced=True):
    """Hold the world at "behind, then the advance closed it" and count the provenance reads.

    `_divergence_refusal` answers behind ONCE and level after that, which is the state the advance
    produces when it works. Returns the list the provenance stub appends a verdict to.
    """
    answers = iter([
        "origin/main is 4 commit(s) AHEAD of HEAD, so a commit created here could only be "
        "rejected non-fast-forward",
    ])
    monkeypatch.setattr(prc, "_divergence_refusal", lambda *a, **k: next(answers, None))
    monkeypatch.setattr(prc, "_advance_to_origin_or_say_why",
                        lambda *a, **k: {"advanced": advanced, "reason": "stubbed"})
    return []


def _provenance_verdicts(monkeypatch, verdicts, seen):
    """`_provenance_is_publishable` answering `verdicts` in order, recording each call."""
    answers = iter(verdicts)

    def stub(paths, *, label="publish"):
        verdict = next(answers)
        seen.append((label, verdict))
        return verdict
    monkeypatch.setattr(prc, "_provenance_is_publishable", stub)


# ── ONE: the advance invalidates the provenance verdict, at the content commit ───────────────

def test_a_provenance_the_advance_broke_refuses_the_publish(publisher, monkeypatch):
    """THE DEFECT. The check passed on the pre-advance tree and would fail on the tree actually
    about to be committed. Publishing anyway is the fixture-value class arriving through a door
    that was already open -- a page of figures attributed to a run that did not produce them.

    MUTATION: delete the re-read after the advance and this reds on all three assertions -- the
    outcome is PUBLISHED, a `git commit` appears, and only one provenance verdict was taken.
    """
    calls = publisher
    seen = _cleared_by_the_advance(monkeypatch)
    _provenance_verdicts(monkeypatch, [True, False], seen)

    outcome = {}
    returned = prc.git_commit_push("abc1234", 1000.0, outcome=outcome)

    assert returned is False
    assert outcome.get("reason") == prc.PROVENANCE_REFUSED, \
        "a stamp broken by our own fast-forward is a provenance refusal, not a publish"
    assert not _committed(calls) and not _staged(calls), \
        "nothing may be staged or committed once the stamp is known bad"
    assert len(seen) == 2, "the verdict must be RE-TAKEN on the tree the advance produced"


def test_a_provenance_that_survives_the_advance_still_publishes(publisher, monkeypatch):
    """THE NULL, ON THE SAME FIXTURE. Without it the re-check could refuse unconditionally and
    every assertion above would still pass -- which would silently convert the repair into the
    wedge it was built to end.

    MUTATION: `return False` from the re-check and this reds; refuse whenever `_advance` fired
    and this reds.
    """
    calls = publisher
    seen = _cleared_by_the_advance(monkeypatch)
    _provenance_verdicts(monkeypatch, [True, True], seen)

    outcome = {}
    prc.git_commit_push("abc1234", 1000.0, outcome=outcome)

    assert outcome.get("reason") != prc.PROVENANCE_REFUSED
    assert _committed(calls), "a cycle whose stamp survived the advance must reach its commit"
    assert len(seen) == 2


def test_the_provenance_is_not_re_read_when_nothing_moved(publisher, monkeypatch):
    """SCOPE. The re-read exists because the tree MOVED; a level tree never reaches the advance,
    so a second read there would be cost with no question behind it -- and, worse, would make the
    control above pass on a version that re-reads unconditionally and therefore proves nothing
    about the advance.

    MUTATION: hoist the re-check out of the `_advance["advanced"]` branch and this reds.
    """
    calls = publisher
    monkeypatch.setattr(prc, "_divergence_refusal", lambda *a, **k: None)
    seen = []
    _provenance_verdicts(monkeypatch, [True], seen)

    prc.git_commit_push("abc1234", 1000.0)

    assert len(seen) == 1, "an unmoved tree must be graded once, not twice"
    assert _committed(calls)


# ── TWO: the banner/heartbeat site gets the same advance and the same re-reads ────────────────

def test_the_banner_site_tries_the_advance_before_refusing(publisher, monkeypatch):
    """THE CLASS, NOT THE INSTANCE. This file says twice, in its own comments, that a guard placed
    only where the incident was observed is what makes a class recur -- and the advance landed at
    `git_commit_push` alone. The heartbeat and the red-cycle banner are blocked by the same fork
    and are the surfaces a reader consults precisely when content is not publishing.

    MUTATION: delete the advance block from `_commit_and_push_paths` and this reds -- the commit
    never happens, which is the five-hour silence this repairs.
    """
    calls = publisher
    seen = _cleared_by_the_advance(monkeypatch)
    _provenance_verdicts(monkeypatch, [True, True], seen)

    prc._commit_and_push_paths(["site/data/dashboard.json"], "banner",
                               label="Liveness heartbeat")

    assert _committed(calls), "a mechanical fork must not silence the liveness surface"
    assert len(seen) == 2, "the stamp must be re-graded on the tree the advance produced"
    # The RETURN value is deliberately not asserted: this function reports whether ORIGIN
    # advanced, verified by `ls-remote`, and the stub answers empty. Its subject is the push,
    # which is a different mechanism with its own controls; asserting it here would be grading a
    # channel this fixture does not model.


def test_the_banner_site_still_refuses_when_the_advance_cannot_clear_the_fork(publisher,
                                                                              monkeypatch):
    """THE NULL FOR THE LEG ABOVE, and the property the predecessor held. A real divergence, or a
    fast-forward git refuses, still stops the banner before staging -- a commit there deepens the
    fork exactly as a content commit does.

    MUTATION: proceed regardless of `_advance["advanced"]` and this reds -- a commit appears on a
    tree that is still behind.
    """
    calls = publisher
    seen = _cleared_by_the_advance(monkeypatch, advanced=False)
    _provenance_verdicts(monkeypatch, [True], seen)

    returned = prc._commit_and_push_paths(["site/data/dashboard.json"], "banner",
                                          label="Liveness heartbeat")

    assert returned is False
    assert not _committed(calls) and not _staged(calls)


def test_the_banner_site_refuses_a_provenance_the_advance_broke(publisher, monkeypatch):
    """AND THE SAME STAMP HAZARD HERE. `_commit_and_push_paths` is the path that publishes
    `publish_provenance.json` on a red cycle -- the file the fast-forward is most likely to have
    replaced with origin's -- so the site that carries the banner is the last place this re-read
    may be missing.

    MUTATION: drop the `_provenance_is_publishable` re-read from the advance branch and this
    reds -- a banner commits a stamp that was verified against a tree that no longer exists.
    """
    calls = publisher
    seen = _cleared_by_the_advance(monkeypatch)
    _provenance_verdicts(monkeypatch, [True, False], seen)

    returned = prc._commit_and_push_paths(["site/data/publish_provenance.json"], "banner",
                                          label="Provenance banner")

    assert returned is False
    assert not _committed(calls) and not _staged(calls)
    assert len(seen) == 2


# ── THREE: the seam between this repair and the bounded retry that landed beside it ───────────
#
# NEITHER LANE COULD SEE THIS. The re-read above was written against a single-shot advance; origin
# then wrapped that advance in `PUBLISH_ADVANCE_ATTEMPTS` and re-read the DIVERGENCE per attempt.
# Composed, the loop can fast-forward, lose the race, and fast-forward again -- so there are now
# several trees the stamp could be graded against, and only the last one is the tree that gets
# committed. Nothing above exercises a second iteration, so nothing above grades that choice.


def _lost_a_race_then_cleared(monkeypatch, events):
    """Behind, advanced, overtaken anyway, advanced again, clear -- with the order recorded.

    ONE ORDERED LOG for both mechanisms on purpose: which of them ran LAST is the whole question,
    and two separate counters cannot answer it.
    """
    answers = iter([
        "origin/main is 4 commit(s) AHEAD of HEAD",   # the state that enters the loop
        "origin/main is 1 commit(s) AHEAD of HEAD",   # attempt 1 fast-forwarded and was overtaken
    ])

    def refusal(*a, **k):
        return next(answers, None)

    def advance(*a, **k):
        events.append("advance")
        return {"advanced": True, "reason": "stubbed"}

    monkeypatch.setattr(prc, "_divergence_refusal", refusal)
    monkeypatch.setattr(prc, "_advance_to_origin_or_say_why", advance)


def test_the_stamp_is_graded_on_the_last_tree_the_retry_produced(publisher, monkeypatch):
    """The re-read must sit under the loop's SUCCESS branch, not beside its advance.

    Two fast-forwards happen here and only the second one's tree is committed. Grading per attempt
    would spend a verdict on a tree already superseded -- and, worse, would let a stamp that was
    good on attempt 1's tree carry the commit built on attempt 2's.

    MUTATION: re-read the provenance after every advance rather than only when the fork closed,
    and the interleaving reds (three verdicts, and one of them before the last advance). Move the
    `break` above the re-read and it reds on `len(seen)` -- the retry path publishes ungraded.
    """
    calls = publisher
    seen = []
    _lost_a_race_then_cleared(monkeypatch, events := [])

    def stub(paths, *, label="publish"):
        events.append("provenance")
        seen.append(label)
        return True
    monkeypatch.setattr(prc, "_provenance_is_publishable", stub)

    prc.git_commit_push("abc1234", 1000.0)

    assert events.count("advance") == 2, \
        "the fixture must actually reach a second attempt or this grades nothing"
    assert events == ["provenance", "advance", "advance", "provenance"], \
        "the stamp is graded once before the loop and once after the LAST fast-forward"
    assert _committed(calls), "a cycle that won on the retry must still reach its commit"


def test_a_stamp_the_second_fast_forward_broke_refuses_the_publish(publisher, monkeypatch):
    """THE REFUSAL LEG, on the retry path specifically. The control above would pass unchanged if
    the re-read there returned a value nobody acted on; this is the same interleaving with the
    verdict turned, and it must stop the commit.

    MUTATION: ignore the re-read's result on the retry path and this reds -- a commit appears
    carrying a stamp verified against a tree two fast-forwards ago.
    """
    calls = publisher
    _lost_a_race_then_cleared(monkeypatch, events := [])
    verdicts = iter([True, False])
    monkeypatch.setattr(prc, "_provenance_is_publishable",
                        lambda paths, *, label="publish": next(verdicts))

    outcome = {}
    returned = prc.git_commit_push("abc1234", 1000.0, outcome=outcome)

    assert returned is False
    assert outcome.get("reason") == prc.PROVENANCE_REFUSED
    assert not _committed(calls) and not _staged(calls)
    assert events.count("advance") == 2, "the refusal must come from the RETRY path, not the first"
