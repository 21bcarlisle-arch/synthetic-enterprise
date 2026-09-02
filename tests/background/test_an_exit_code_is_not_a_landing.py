"""The seat executor's verdict must read its SUBJECT, not its own process.

THE DEFECT THIS FILE EXISTS FOR, and it is measured rather than imagined.
`docs/observability/seat-executor-log.md` carries, on 2026-09-02:

    [15:46 UTC] FINISHED land-the-dd-inference-organ-and-unwedge-every-lanes-publish: rc=0
    [16:42 UTC] FINISHED land-the-dd-inference-organ-and-unwedge-every-lanes-publish: rc=0
    [17:56 UTC] FINISHED land-the-dd-inference-organ-and-unwedge-every-lanes-publish: rc=0

Four turns, eleven hours, nothing landed, the publish still wedged — and each one DISCHARGED the
handoff, so the seat that had ranked the item read four successes and re-ranked around it. The
verdict was `f"{work_id}: rc={proc.returncode}"`. An exit code is a fact about a PROCESS; the
claim is about a TREE. R15's fail-silent killer, in the instrument least able to notice it,
because it was the one reporting on itself.

Every test below names the mutation it dies to. The one that matters most is
`test_the_verdict_is_not_the_exit_code`: it pins BOTH directions, so reverting to `returncode`
cannot pass by flipping a sign.
"""
from __future__ import annotations

import subprocess
import time

import pytest

from background import delivery_lane, delivery_seat, seat_executor


@pytest.fixture()
def turn(tmp_path, monkeypatch):
    """A run_once that reaches the spawn without touching the shared tree or the network."""
    monkeypatch.setattr(seat_executor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    monkeypatch.setattr(seat_executor, "WORKTREE", tmp_path / "wt")
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: False)
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: False)
    monkeypatch.setattr(seat_executor, "_is_handed_off", lambda item, now=None: True)
    monkeypatch.setattr(seat_executor, "_resolve_claude", lambda: "claude")
    monkeypatch.setattr(seat_executor, "ensure_worktree", lambda base: tmp_path / "wt")
    monkeypatch.setattr(seat_executor, "guard_live_ledger_write",
                        lambda path, writer="": path)
    monkeypatch.setattr(seat_executor.delivery_lane, "CLAIMS_FILE", tmp_path / "claims.json")
    # TWO stores, because `run_once` writes its claim to one and `_still_claimed` reads the other.
    # That mismatch is a real defect, filed separately -- it is why every turn in the live log
    # logged `DISCHARGED`. It is NOT what this file pins, so both are redirected off the live
    # records here rather than reconciled.
    monkeypatch.setattr(seat_executor.seat_work_in_hand, "CLAIMS_FILE",
                        tmp_path / "work_in_hand.json")
    monkeypatch.setattr(seat_executor.delivery_lane, "next_item",
                        lambda **k: {"id": "the-item", "what": "w", "why": "y"})
    (tmp_path / "wt").mkdir()

    dropped: list[str] = []
    monkeypatch.setattr(seat_executor, "seat_continuation_drop",
                        lambda wid: dropped.append(wid) or True)

    def spawn(returncode: int = 0):
        """Stub the two subprocesses `run_once` makes: the base sha, then the session."""
        def fake_run(cmd, **kwargs):
            if cmd[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="basesha0000\n", stderr="")
            return subprocess.CompletedProcess(cmd, returncode, stdout="", stderr="")
        monkeypatch.setattr(seat_executor.subprocess, "run", fake_run)

    return type("Turn", (), {
        "spawn": staticmethod(spawn),
        "dropped": dropped,
        "log": lambda self=None: (tmp_path / "log.md").read_text(),
    })()


def _landed(monkeypatch, *, at: float, paths: list[str]):
    monkeypatch.setattr(seat_executor, "bound_landing", lambda wid: (at, paths))


def _shared_tree(monkeypatch, *, changed: set[str], unreadable: str = ""):
    monkeypatch.setattr(seat_executor, "shared_tree_changes_since",
                        lambda base: (changed, unreadable))


# ---------------------------------------------------------------------------- the verdict itself


def test_the_verdict_is_not_the_exit_code(turn, monkeypatch):
    """BOTH directions, which is what makes this survive a revert rather than a sign flip.

    An exit-0 turn that moved nothing is a FAILURE; a non-zero turn that landed an increment is a
    SUCCESS. The old code had both backwards. Pinning only the first would let `returncode` come
    back by inverting it somewhere; pinning both leaves no reading of the exit code that passes.

    MUTATION: restore `detail = f"{work_id}: rc={proc.returncode}"` and log it as FINISHED. Leg A
    fires (rc=0 would read FINISHED). Invert that to appease leg A and leg B fires.
    """
    # LEG A — exited clean, subject did not move.
    _landed(monkeypatch, at=0.0, paths=[])
    turn.spawn(returncode=0)
    ran, detail = seat_executor.run_once()
    assert ran is True, "the session DID run; the boolean means spawned, not succeeded"
    assert detail.startswith("LANDED NOTHING: the-item,"), detail
    assert "FINISHED" not in turn.log()

    # LEG B — exited dirty, subject moved anyway. A session can crash after landing an increment,
    # and the increment is what the claim is about.
    _landed(monkeypatch, at=time.time() + 30, paths=["background/seat_executor.py"])
    _shared_tree(monkeypatch, changed={"background/seat_executor.py"})
    turn.spawn(returncode=1)
    ran, detail = seat_executor.run_once()
    assert "LANDED NOTHING" not in detail, detail
    assert "rc=1" in detail and "moved on the shared tree" in detail
    assert "FINISHED the-item: rc=1" in turn.log()


def test_a_turn_that_landed_nothing_does_NOT_discharge_the_claim(turn, monkeypatch):
    """The half that makes the refusal worth reading.

    A named refusal that still let the handoff be consumed would be a louder version of the same
    eleven hours: the item would be dropped from `seat_continuation` and never re-offered, so the
    next tick would take something else and the ranked work would go quiet with a red line in a
    log nobody reads. The refusal has to leave the work IN THE POOL.

    MUTATION: move the `subject_moved` branch below the discharge, or let it fall through to the
    `_still_claimed` block, and this fires.
    """
    _landed(monkeypatch, at=0.0, paths=[])
    turn.spawn(returncode=0)
    seat_executor.run_once()

    assert turn.dropped == [], "a turn that landed nothing consumed the handoff"
    assert "DISCHARGED" not in turn.log()


def test_a_turn_that_landed_discharges_exactly_as_before(turn, monkeypatch):
    """THE PASS BRANCH IS REACHABLE, which is the check this project keeps having to add.

    A verdict whose success branch cannot be reached reports a constant refusal and is worth less
    than the constant pass it replaced — the seat would learn to ignore `LANDED NOTHING` inside a
    day. The existing discharge behaviour (claim released ⇒ handoff dropped) must still happen on
    a turn that really landed.

    MUTATION: make `subject_moved` return False unconditionally and this fires.
    """
    _landed(monkeypatch, at=time.time() + 30, paths=["docs/observability/x.json"])
    _shared_tree(monkeypatch, changed={"docs/observability/x.json", "unrelated.py"})
    turn.spawn(returncode=0)
    ran, detail = seat_executor.run_once()

    assert "1 of 1 bound path(s) moved on the shared tree" in detail
    # The claim was made by run_once and never released by the stubbed session, so nothing is
    # discharged here — but the FINISHED line, not a refusal, is what reaches the log.
    assert "FINISHED the-item:" in turn.log()
    assert "LANDED NOTHING" not in turn.log()


# ------------------------------------------------------------------- the two legs, separately


def test_a_worktree_commit_that_was_never_promoted_reads_LANDED_NOTHING(monkeypatch):
    """LEG 2, and it is the exact failure the eleven hours were made of.

    `record_landing` reads `git show`, which reads the shared OBJECT DATABASE — and a linked
    worktree writes into it. So a commit made in the executor's worktree and never promoted binds
    to the claim perfectly well. Leg 1 alone therefore passes for the precise defect this whole
    verdict exists to catch, and only asking the shared tree separates them.

    MUTATION: drop the `shared_tree_changes_since` call and trust the binding, and this fires.
    """
    _landed(monkeypatch, at=time.time(), paths=["company/billing/dd_review.py"])
    _shared_tree(monkeypatch, changed={"docs/observability/some-other-lane.json"})

    moved, why = seat_executor.subject_moved("the-item", "basesha", time.time() - 60)
    assert moved is False
    assert "never promoted" in why and "promote_worktree_landing" in why


def test_a_landing_bound_on_a_PREVIOUS_turn_does_not_certify_this_one(monkeypatch):
    """LEG 1's freshness clause — the across-turns fail-open, which is how four turns read green.

    "The claim has bound paths" is TRUE from the moment the first turn lands and stays true
    forever, so a verdict keyed to it would pass every subsequent no-op turn. The binding has to
    be NEWER than the turn that is being judged.

    MUTATION: replace `landed_at <= since` with `not landed_paths` and this fires.
    """
    started = time.time()
    _landed(monkeypatch, at=started - 3600, paths=["background/seat_executor.py"])
    _shared_tree(monkeypatch, changed={"background/seat_executor.py"})

    moved, why = seat_executor.subject_moved("the-item", "basesha", started)
    assert moved is False
    assert "during this turn" in why


def test_an_unreadable_shared_tree_fails_CLOSED(monkeypatch):
    """An unavailable check is a failed check, and this one has a right direction to fail in.

    Reading it as LANDED is how a broken git invocation would quietly restore the old behaviour.
    Reading it as NOTHING costs a repeated turn on work that was in fact done — recoverable, and
    the item stays claimed and re-offered rather than consumed.

    MUTATION: `return True` on the unreadable branch, or swallow the reason and carry on, and
    this fires.
    """
    _landed(monkeypatch, at=time.time(), paths=["a.py"])
    _shared_tree(monkeypatch, changed=set(), unreadable="the shared tree could not be read -- x")

    moved, why = seat_executor.subject_moved("the-item", "basesha", time.time() - 60)
    assert moved is False
    assert "could not be read" in why


def test_shared_tree_changes_reads_BOTH_ends_and_only_the_FAR_side(tmp_path, monkeypatch):
    """Leg 2 against a real repository, because a stubbed git proves nothing about git.

    TWO REFS: a landing is observable at the shared HEAD before its push, and at `origin/main`
    when the shared HEAD sits behind. Reading either alone calls a real landing nothing.

    THREE-DOT: only the far side's changes count. The base a turn starts on is `origin/main` AT
    THAT MOMENT, and by the time the turn ends the shared tree can have diverged from it rather
    than advanced past it — a fast-forward is not guaranteed on a tree four lanes write to. Under
    two-dot, everything the base carried and the far side does not reads as CHANGED, so another
    lane's divergence would certify this tick's claim. The fixture is built diverged for exactly
    that reason: an ancestor-only fixture makes `..` and `...` identical and the mutation survives.

    MUTATION: drop either ref from the loop, or switch `...` to `..`, and this fires.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args, cwd=repo):
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (repo / "common.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-qm", "common ancestor")
    ancestor = git("rev-parse", "HEAD").stdout.strip()

    # THE BASE the turn started on, carrying a file NEITHER end of the shared tree has now.
    (repo / "only_on_base.txt").write_text("1\n")
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").stdout.strip()

    # The shared HEAD and `origin/main`, each diverged from that base off the common ancestor.
    git("checkout", "-q", "-B", "main", ancestor)
    (repo / "on_head.txt").write_text("1\n")
    git("add", ".")
    git("commit", "-qm", "head")
    git("checkout", "-q", ancestor)
    (repo / "on_origin.txt").write_text("1\n")
    git("add", ".")
    git("commit", "-qm", "origin")
    git("update-ref", "refs/remotes/origin/main", git("rev-parse", "HEAD").stdout.strip())
    git("checkout", "-q", "main")

    monkeypatch.setattr(seat_executor, "PROJECT_DIR", repo)
    changed, unreadable = seat_executor.shared_tree_changes_since(base)

    assert unreadable == ""
    assert changed == {"on_head.txt", "on_origin.txt"}, "one end of the shared tree went unread"
    # Under two-dot this is present (the far side "deleted" it) and certifies a tick that did
    # nothing but sit through somebody else's divergence.
    assert "only_on_base.txt" not in changed
    assert "common.txt" not in changed


def test_an_unknown_base_sha_is_UNREADABLE_not_EMPTY(tmp_path, monkeypatch):
    """git refusing and git answering "nothing changed" are different results.

    Collapsing them is the fail-open: every turn would report an empty change set, which the
    caller reads as a real observation that nothing moved rather than as a failed check. Here it
    matters less (both refuse) but it is the reason the reason-string exists at all — the log has
    to say WHICH, or the next reader debugs the wrong thing.

    MUTATION: return `(set(), "")` on a non-zero git and this fires.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True,
                   capture_output=True)
    monkeypatch.setattr(seat_executor, "PROJECT_DIR", repo)

    changed, unreadable = seat_executor.shared_tree_changes_since("deadbeefdeadbeef")
    assert changed == set()
    assert "could not be read" in unreadable

    assert seat_executor.shared_tree_changes_since("")[1].startswith("the turn recorded no base")


# ----------------------------------------------------------- the binding survives its own release


def test_a_landing_stays_readable_after_the_claim_is_RELEASED(tmp_path, monkeypatch):
    """`--release` pops the claim, and the bound paths go with it.

    That is right for a store of what is IN HAND and wrong for the reader that runs AFTER the
    tick — which is this verdict. A tick that landed and then released would otherwise be
    indistinguishable from a tick that landed nothing, and the verdict would have no choice but
    to fall back to the exit code.

    MUTATION: drop `_remember_landing` from `record_landing`, or read the tombstone off the claim
    instead of the draw ledger, and this fires.
    """
    store = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", store)
    monkeypatch.setattr(delivery_lane, "_commit_facts",
                        lambda commit: (time.time() + 10, ["background/x.py", "docs/y.md"]))

    delivery_lane.claims_mod.claim("some-work", paths=[], path=store)
    assert delivery_lane.record_landing("some-work", commit="HEAD", path=store)

    when, paths = delivery_lane.last_landing("some-work", path=store)
    assert paths == ["background/x.py", "docs/y.md"]
    assert when > 0

    delivery_lane.claims_mod.release("some-work", path=store)
    assert "some-work" not in delivery_lane.held(path=store)
    assert delivery_lane.last_landing("some-work", path=store) == (when, paths), \
        "the release took the evidence with it"


def test_a_REFUSED_landing_writes_no_tombstone(tmp_path, monkeypatch):
    """The tombstone is EVIDENCE, so every refusal `record_landing` makes must leave none.

    Otherwise leg 1 of the verdict passes for a tick that ran `--landed` and was told no, which is
    the self-report the whole verdict exists to stop trusting.

    NAMED NON-COVERAGE, because the flattering reading was available: mutating the `if bound:`
    guard to `if True:` kills no test, and that is an EQUIVALENCE rather than a hole. Every route
    by which `bind_paths` answers `[]` is refused by one of the returns below it, so the guard is
    unreachable-as-a-decision today; `delivery_lane.record_landing` says so beside it. What is
    covered here is the refusals that actually fire.

    MUTATION: hoist `_remember_landing` above any of the three `return []` guards and this fires.
    """
    store = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", store)
    monkeypatch.setattr(delivery_lane, "_commit_facts", lambda commit: (time.time() + 10, ["a.py"]))

    # 1. Never claimed — there is no deadline to inform.
    assert delivery_lane.record_landing("never-claimed", commit="HEAD", path=store) == []
    assert delivery_lane.last_landing("never-claimed", path=store) == (0.0, [])

    # 2. Claimed, but the commit is unreadable or touched nothing.
    delivery_lane.claims_mod.claim("real-work", paths=[], path=store)
    monkeypatch.setattr(delivery_lane, "_commit_facts", lambda commit: (0.0, []))
    assert delivery_lane.record_landing("real-work", commit="HEAD", path=store) == []
    assert delivery_lane.last_landing("real-work", path=store) == (0.0, [])

    # 3. Claimed and readable, but the commit predates the first draw — somebody else's work.
    monkeypatch.setattr(delivery_lane, "_commit_facts", lambda commit: (time.time() - 9999, ["a.py"]))
    assert delivery_lane.record_landing("real-work", commit="HEAD", path=store) == []
    assert delivery_lane.last_landing("real-work", path=store) == (0.0, [])


# ------------------------------------------------------------------------ the drawn channel


def test_the_drawn_channel_reads_the_executors_OWN_LOG(tmp_path, monkeypatch):
    """`build_brief` reported `drawn: []` for ids this log named seven times.

    The atom stall tracker is keyed by maturity-map atom id and a Lane 0 slug is by construction
    not one; `delivery_lane.drawn_since` records what `draw()` handed out, and the executor's
    busiest route — a PROMOTED CONTINUATION — never goes through `draw()`. So the one route that
    had actually run was in neither channel, and a steer that WAS biting presented as one that
    was not.

    MUTATION: drop `ids_run_since` from `focus_drawn_since`, or let it count STOOD DOWN lines,
    and this fires.
    """
    log = tmp_path / "log.md"
    log.write_text(
        "- [2026-09-02 15:36 UTC] RUNNING land-the-organ in /var/tmp/wt on 9ebc2dfcc\n"
        "- [2026-09-02 15:46 UTC] FINISHED land-the-organ: rc=0 -- 2 of 2 bound path(s) moved\n"
        "- [2026-09-02 16:06 UTC] STOOD DOWN: an interactive seat is live, so 'declined-item' is "
        "PROMOTED rather than run\n"
        "- [2026-09-02 17:37 UTC] LANDED NOTHING: quiet-turn, bound paths unchanged since abc\n"
        "- [2026-08-01 09:00 UTC] RUNNING far-too-old in /var/tmp/wt on 1111111\n"
    )
    cutoff = time.strptime("2026-09-02 00:00", "%Y-%m-%d %H:%M")
    import calendar
    since = calendar.timegm(cutoff)

    assert seat_executor.ids_run_since(since, path=log) == ["land-the-organ", "quiet-turn"]
    assert "declined-item" not in seat_executor.ids_run_since(since, path=log), \
        "a stand-down is not a turn; counting it reports a steer as biting on the turns it was " \
        "refused"
    assert seat_executor.ids_run_since(since - 40 * 86400, path=log) == [
        "far-too-old", "land-the-organ", "quiet-turn"]


def test_the_brief_UNIONS_the_executors_log_into_the_drawn_channel(monkeypatch):
    """The seam: `focus_drawn_since` has to actually consult it.

    A channel that exists and is not wired is the same as no channel — this project's most common
    defect and the reason `test_a_cited_constant_has_a_caller` exists at all.

    MUTATION: revert `focus_drawn_since` to the two-channel union and this fires.
    """
    from datetime import datetime, timedelta, timezone

    monkeypatch.setattr(delivery_seat, "atoms_drawn_since", lambda since: ["AN_ATOM"])
    monkeypatch.setattr(delivery_lane, "drawn_since", lambda cutoff: ["a-drawn-slug"])
    monkeypatch.setattr(seat_executor, "ids_run_since",
                        lambda cutoff, path=None: ["a-slug-only-the-executor-ran"])

    drawn = delivery_seat.focus_drawn_since(datetime.now(timezone.utc) - timedelta(hours=3))
    assert "a-slug-only-the-executor-ran" in drawn
    assert {"AN_ATOM", "a-drawn-slug"} <= set(drawn), "the union dropped an existing channel"


def test_a_missing_executor_log_costs_the_orientation_NOTHING(tmp_path):
    """It is read from an orientation that must not be lost to an absent file.

    MUTATION: let the `OSError` escape and this fires.
    """
    assert seat_executor.ids_run_since(0.0, path=tmp_path / "nope.md") == []
