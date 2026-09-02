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


def test_the_channel_reads_the_SHARED_trees_log_not_the_importing_trees(tmp_path, monkeypatch):
    """A worktree import must still see the executor's real log.

    THE DEFECT, measured 2026-09-02 at the commit that built this channel: same code, same
    commit, two trees. From the shared tree `ids_run_since(now - 24h)` answered NINE ids; from a
    linked worktree it answered `[]`. `LOG_FILE` is derived from `__file__`, so a module imported
    out of a worktree looked for the log beside itself, did not find it, and returned empty
    without a word — and `focus_drawn_since` silently lost a whole channel, so `build_brief`
    reported `drawn: [], steered: false` with the note *"the previous direction named work and
    NONE of it was drawn — if this repeats, the steer is a no-op"*.

    That is the exact false reading this channel was built to abolish, arriving through path
    resolution instead of through logic. REACHABLE, not theoretical: a drawn tick runs in a
    worktree and is told to orient there.

    MUTATION: revert `ids_run_since`'s default to `LOG_FILE` and this fires.
    """
    shared = tmp_path / "shared"
    (shared / "docs" / "observability").mkdir(parents=True)
    git = ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-C", str(shared)]
    subprocess.run(["git", "init", "-q", str(shared)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "root"], check=True)
    worktree = tmp_path / "worktree"
    subprocess.run([*git, "worktree", "add", "-q", "--detach", str(worktree)], check=True)

    log_name = seat_executor.LOG_FILE.name
    (shared / "docs" / "observability" / log_name).write_text(
        "- [2026-09-02 15:36 UTC] RUNNING only-on-the-shared-tree in /var/tmp/wt on 9ebc2dfcc\n")

    # Stand where a worktree-imported module stands: PROJECT_DIR and LOG_FILE both inside it.
    monkeypatch.setattr(seat_executor, "PROJECT_DIR", worktree)
    monkeypatch.setattr(seat_executor, "LOG_FILE",
                        worktree / "docs" / "observability" / log_name)
    assert not seat_executor.LOG_FILE.exists(), "fixture is not standing where the defect was"

    assert seat_executor.ids_run_since(0.0) == ["only-on-the-shared-tree"], \
        "a worktree-imported channel silently lost the shared tree's log, so a steer that IS " \
        "biting reads as one that is not"


def test_a_shared_tree_with_NO_log_falls_back_to_this_trees(tmp_path, monkeypatch):
    """Resolving the shared tree must never LOSE a log that was readable before.

    The repair above reaches past this tree for the log. If the shared tree it finds has no log
    at all, the honest answer is the one we already had — a resolver that returned the absent
    shared path unconditionally would turn a working read into an empty one, which is the same
    silent channel loss pointing the other way.

    MUTATION: drop the `shared.exists()` fallback in `_shared_tree_log` and this fires.

    ESTABLISHED EQUIVALENCE, recorded rather than left as flattering silence: mutating the
    `git rev-parse` refusal guard ALONE survives every test here, because a failed `rev-parse`
    yields an empty stdout, `Path("")` is `Path(".")`, and the derived path then does not exist —
    so this fallback catches it. The two guards are one control with two expressions and each
    makes the other unreachable; the honest mutation moves both, and that combination IS caught
    by this test. Same shape the stand-down exclusion in `ids_run_since` documents against itself.
    """
    shared = tmp_path / "shared"
    shared.mkdir()
    subprocess.run(["git", "init", "-q", str(shared)], check=True)

    here = tmp_path / "here" / "docs" / "observability"
    here.mkdir(parents=True)
    log = here / seat_executor.LOG_FILE.name
    log.write_text("- [2026-09-02 15:36 UTC] RUNNING readable-right-here in /x on abc\n")

    monkeypatch.setattr(seat_executor, "PROJECT_DIR", shared)
    monkeypatch.setattr(seat_executor, "LOG_FILE", log)

    assert seat_executor.ids_run_since(0.0) == ["readable-right-here"], \
        "reaching for the shared tree threw away a log this tree could read"


# ------------------------------------------------------ the release message, the third instrument


@pytest.fixture()
def stores(tmp_path, monkeypatch):
    """Both claim stores, off the live records.

    BOTH, because `release_refusal_reason` reads the OTHER one to tell the matched pair apart, and
    the live `.seat_work_in_hand.json` really does hold ids while this suite runs -- a test that
    read it would pass or fail on what the tree happened to be doing.
    """
    lane = tmp_path / "delivery_lane_claims.json"
    hand = tmp_path / "work_in_hand.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", lane)
    monkeypatch.setattr(delivery_lane.claims_mod, "CLAIMS_FILE", hand)

    # AND THE TREE THIS PROCESS IS STANDING IN, which is an INPUT to the reason and was ambient
    # until it was caught. `release_refusal_reason`'s worktree clause reads `PROJECT_DIR`, so
    # these tests passed from the shared tree and FAILED, unmutated, from a linked worktree --
    # and a drawn tick runs in one. That is the same defect `8cb73c627` fixed for the executor's
    # log arriving inside the repair for it: a control whose verdict depends on who launched it.
    # Pinned to a PLAIN repo so the clause is exercised at its real equality (common == own),
    # not merely skipped by a git that refused.
    shared = tmp_path / "shared_repo"
    shared.mkdir()
    subprocess.run(["git", "init", "-q", str(shared)], check=True, capture_output=True)
    monkeypatch.setattr(delivery_lane, "PROJECT_DIR", shared)
    return type("Stores", (), {"lane": lane, "hand": hand, "shared": shared})()


def test_release_reports_whether_a_record_WAS_ACTUALLY_REMOVED(stores):
    """ASSERTED AGAINST THE STORE, which is the discipline the finding asks for by name.

    `release` returned `None` unconditionally, so the CLI's `print("released ...")` was true of
    nothing. The claim here is not "it returned False" but "the store still holds it" -- a return
    value is another self-report, and this whole chain is made of those.

    MUTATION: `return True` unconditionally, or restore `-> None`, and this fires.
    """
    delivery_lane.claims_mod.claim("real-claim", paths=[], path=stores.lane)
    assert "real-claim" in delivery_lane.claims_mod.held(path=stores.lane)

    assert delivery_lane.claims_mod.release("real-claim", path=stores.lane) is True
    assert "real-claim" not in delivery_lane.claims_mod.held(path=stores.lane), "the store kept it"

    # Releasing again removes nothing, and the store is the witness.
    assert delivery_lane.claims_mod.release("real-claim", path=stores.lane) is False
    assert "real-claim" not in delivery_lane.claims_mod.held(path=stores.lane)


def test_the_release_CLI_REFUSES_instead_of_printing_success(stores, capsys):
    """The measured pair from the finding: one id, one turn, two commands that disagreed.

    `--landed` said `bound NOTHING: it is NOT CLAIMED` and `--release` said `released <id>`. The
    CLI must now decline in the same voice `--landed` already uses, and exit non-zero so a caller
    that scripts it cannot read the refusal as a success.

    MUTATION: drop the `if not ...` guard and print unconditionally, or `return 0` on the refusal
    branch, and this fires.
    """
    rc = delivery_lane.main(["--release", "never-claimed"])
    out = capsys.readouterr().out
    assert rc == 1, "a release that let nothing go exited 0"
    assert "released NOTHING for never-claimed" in out
    assert "NOT CLAIMED here" in out

    # And the PASS branch is still reachable — a real claim releases and reports success.
    delivery_lane.claims_mod.claim("real-claim", paths=[], path=stores.lane)
    assert delivery_lane.main(["--release", "real-claim"]) == 0
    assert "released real-claim" in capsys.readouterr().out
    assert "real-claim" not in delivery_lane.claims_mod.held(path=stores.lane)


def test_the_refusal_NAMES_THE_MATCHED_PAIR_rather_than_reciting_causes(stores):
    """The one cause that means STOP AND LOOK, separated from the one that means "fine".

    An id held in `seat_work_in_hand` but not the delivery-lane store is the promoted route of
    §9.1 — the work is still in hand and the release could never have found it. Collapsing that
    into "not claimed" is how the seat would read a constant verdict as an ordinary one.

    MUTATION: return the generic NOT CLAIMED string for every case and this fires.
    """
    delivery_lane.claims_mod.claim("promoted-item", paths=[], path=stores.hand)

    why = delivery_lane.release_refusal_reason("promoted-item", path=stores.lane)
    assert "matched pair" in why and "still in hand" in why
    assert "NOT CLAIMED here" not in why, "the actionable cause was collapsed into the ordinary one"

    # An id in NEITHER store is the ordinary reading, and must not borrow the alarming one.
    plain = delivery_lane.release_refusal_reason("nowhere-at-all", path=stores.lane)
    assert "NOT CLAIMED here" in plain and "matched pair" not in plain


def test_a_release_reason_that_BLOWS_UP_still_names_its_class(stores, monkeypatch):
    """It runs on a failure path; a reason that raised would lose the refusal it explains.

    MUTATION: let the exception escape and this fires.
    """
    monkeypatch.setattr(delivery_lane.claims_mod, "held",
                        lambda **k: (_ for _ in ()).throw(RuntimeError("store on fire")))
    why = delivery_lane.release_refusal_reason("anything", path=stores.lane)
    assert "could not be derived" in why and "RuntimeError" in why


def test_the_refusal_NAMES_THE_WORKTREE_when_that_is_where_it_is_standing(stores, tmp_path,
                                                                          monkeypatch):
    """§6's trap, pinned against a REAL linked worktree rather than a stubbed answer.

    A child running `--release` with its cwd in the executor's worktree writes the WORKTREE's
    store; `ensure_worktree` resets it next turn, so the shared tree never hears the release. The
    reason has to say so, because "not claimed" would send the reader to the wrong store entirely.

    THIS CLAUSE IS WHY THE FIXTURE PINS `PROJECT_DIR`. It is a property of where the PROCESS
    stands, not of the id, so it fires for every id once it fires at all — which means it MASKS
    the other two causes rather than joining them. Covering it here is what keeps that a
    deliberate ordering instead of an accident nobody measured.

    MUTATION: drop the `common != own` comparison, or return the generic string here, and this
    fires.
    """
    worktree = tmp_path / "linked"
    git = ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-C", str(stores.shared)]
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "root"], check=True)
    subprocess.run([*git, "worktree", "add", "-q", "--detach", str(worktree)], check=True,
                   capture_output=True)
    monkeypatch.setattr(delivery_lane, "PROJECT_DIR", worktree)

    why = delivery_lane.release_refusal_reason("nowhere-at-all", path=stores.lane)
    assert "LINKED WORKTREE" in why and "shared tree" in why

    # The id-specific cause still OUTRANKS it: the matched pair is actionable and the worktree
    # clause would otherwise swallow it on the executor's own route, where it matters most.
    delivery_lane.claims_mod.claim("promoted-item", paths=[], path=stores.hand)
    assert "matched pair" in delivery_lane.release_refusal_reason("promoted-item",
                                                                  path=stores.lane)
# ------------------------------------------------------------- the ROUTE decides the store
#
# WHY THIS SECTION EXISTS AND WHY IT DRIVES `run_once` RATHER THAN A FIXTURE.
#
# Everything above stubs `bound_landing`, so it pins the verdict's LOGIC and is silent about the
# production claim path. That gap was not hypothetical: while every test above was green and
# honest, the verdict was a CONSTANT `LANDED NOTHING` on the executor's busiest route, because
# `run_once` wrote its claim to `seat_work_in_hand`'s store and `record_landing` looked for it in
# `delivery_lane`'s. A tick that really landed and really promoted `8cb73c627` was scored as having
# landed nothing. The old verdict could never say NO; its replacement could never say YES.
#
# So these tests stub NOTHING between `run_once` and the stores. They let the ROUTE choose where
# the claim lands -- which is the thing that was wrong -- and a fixture that claimed directly would
# pass under the defect, which is exactly the trap the finding's §9.6 names.
#
# Finding: docs/staging/done/SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md


@pytest.fixture()
def routed(tmp_path, monkeypatch):
    """A `run_once` with REAL claim stores and a session that acts like a tick.

    The two stores are real files at real paths, and the stubbed session runs the same
    `record_landing` / `release` calls the charter tells a tick to run -- against the store its own
    cwd would resolve to. Nothing between `run_once` and those files is patched.
    """
    shared = tmp_path / "shared" / "docs" / "observability" / ".delivery_lane_claims.json"
    worktree = tmp_path / "wt"
    (worktree / "docs" / "observability").mkdir(parents=True)
    shared.parent.mkdir(parents=True)

    monkeypatch.setattr(seat_executor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    monkeypatch.setattr(seat_executor, "WORKTREE", worktree)
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: False)
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: False)
    monkeypatch.setattr(seat_executor, "_is_handed_off", lambda item, now=None: True)
    monkeypatch.setattr(seat_executor, "_resolve_claude", lambda: "claude")
    monkeypatch.setattr(seat_executor, "ensure_worktree", lambda base: worktree)
    monkeypatch.setattr(seat_executor, "guard_live_ledger_write", lambda path, writer="": path)
    monkeypatch.setattr(seat_executor.delivery_lane, "CLAIMS_FILE", shared)
    monkeypatch.setattr(seat_executor.seat_work_in_hand, "CLAIMS_FILE",
                        tmp_path / "work_in_hand.json")
    monkeypatch.setattr(seat_executor.delivery_lane, "next_item",
                        lambda **k: {"id": "the-item", "what": "w", "why": "y"})
    # Leg 2 is pinned separately above; here the shared tree always agrees, so a failure in these
    # tests is unambiguously leg 1 -- the claim store -- and never the git read.
    _shared_tree(monkeypatch, changed={"background/seat_executor.py"})

    dropped: list[str] = []
    monkeypatch.setattr(seat_executor, "seat_continuation_drop",
                        lambda wid: dropped.append(wid) or True)

    def child_binds(store):
        """What `python3 -m background.delivery_lane --landed the-item` does from a given cwd.

        The cwd is what selects the store: a tick in the worktree imports the worktree's module,
        a tick on the shared tree imports the shared one. That is simulated by the explicit
        `path=`, and it is the whole subject of these tests.
        """
        def run_it():
            monkeypatch.setattr(delivery_lane, "_commit_facts",
                                lambda commit: (time.time() + 30,
                                                ["background/seat_executor.py"]))
            return delivery_lane.record_landing("the-item", path=store)
        return run_it

    def spawn(child=None, returncode: int = 0):
        def fake_run(cmd, **kwargs):
            if cmd[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="basesha0000\n", stderr="")
            if child is not None:
                child()
            return subprocess.CompletedProcess(cmd, returncode, stdout="", stderr="")
        monkeypatch.setattr(seat_executor.subprocess, "run", fake_run)

    return type("Routed", (), {
        "shared": shared,
        "worktree_store": worktree / "docs" / "observability" / shared.name,
        "spawn": staticmethod(spawn),
        "child_binds": staticmethod(child_binds),
        "dropped": dropped,
        "log": lambda self=None: (tmp_path / "log.md").read_text(),
    })()


def test_the_verdict_can_say_YES_on_the_PROMOTED_route(routed):
    """THE ONE THIS REPAIR EXISTS FOR. A promoted item is the executor's busiest route.

    A promotion never goes through `delivery_lane.draw()`, so nothing claims the id in the
    delivery-lane store before the turn -- `run_once` is the only thing that can. When it did not,
    the child's `--landed` refused with `NOT CLAIMED`, nothing was ever bound, and leg 1 could
    never pass. The verdict was a constant, which is not a control (R15's fourth shape).

    MUTATION: drop `_worktree_claims()` from the claim loop in `run_once` and this fires -- the
    child binds into a store holding no claim, `record_landing` refuses, and the turn scores
    LANDED NOTHING. That is the measured 2026-09-02 behaviour, restored exactly.
    """
    routed.spawn(child=routed.child_binds(routed.worktree_store))
    ran, detail = seat_executor.run_once()

    assert "LANDED NOTHING" not in detail, \
        f"a promoted turn that really bound a landing was scored as landing nothing: {detail}"
    assert "moved on the shared tree" in detail
    assert "FINISHED the-item:" in routed.log()


def test_the_verdict_can_say_YES_on_the_DRAWN_route(routed):
    """The other arm of the union, and §9.6's clause: BOTH routes, because the route picks the
    store. A drawn tick runs on the shared tree, so its `--landed` reaches the SHARED store; a
    promoted one runs in the worktree. A control that exercised only one would pass whichever
    half of the repair was written.

    MUTATION: drop `delivery_lane.CLAIMS_FILE` from `bound_landing`'s store list and this fires
    while the promoted test above stays green.
    """
    routed.spawn(child=routed.child_binds(routed.shared))
    ran, detail = seat_executor.run_once()

    assert "LANDED NOTHING" not in detail, detail
    assert "FINISHED the-item:" in routed.log()


def test_a_LANDED_NOTHING_turn_leaves_the_item_DRAWABLE_AGAIN(routed):
    """THE PRICE THE OBVIOUS REPAIR WOULD HAVE PAID, and the reason it was not the one taken.

    `delivery_lane.next_item` skips any id in `held()`. That filter is the entire mechanism by
    which an item is not handed out twice -- so a claim left standing when the turn ends does not
    protect anything, it SUPPRESSES THE RE-OFFER that `LANDED NOTHING` exists to produce. The item
    would then wait for the 100-minute sweep instead of the next tick: the verdict would say no
    correctly and the work would not come back, which is the same defect one door along.

    MUTATION: delete the `_hand_back` call in `run_once` and this fires.
    """
    routed.spawn(child=None)  # a session that lands nothing at all
    ran, detail = seat_executor.run_once()
    assert detail.startswith("LANDED NOTHING: the-item,"), detail

    assert "the-item" not in delivery_lane.held(path=routed.shared), \
        "the refused turn held on to its own claim, so next_item will skip the re-offer"
    assert routed.dropped == [], "a turn that landed nothing consumed the handoff"


def test_the_executors_OWN_hand_back_is_not_read_as_the_tick_releasing(routed):
    """ORDER, and it is the repair rebuilding the defect out of itself if it is wrong.

    `_still_claimed` asks *did the TICK release*; `_hand_back` is the executor's own bookkeeping.
    Run the hand-back first and the two are indistinguishable: every turn would look like a tick
    saying it had finished, and the unconditional discharge this whole repair removes would be
    back -- built, this time, out of the repair.

    Here the tick lands but never releases, so the work is unfinished and the handoff must STAND.

    MUTATION: move `_hand_back(...)` above `tick_released = not _still_claimed(...)` and this
    fires.
    """
    routed.spawn(child=routed.child_binds(routed.worktree_store))
    ran, detail = seat_executor.run_once()

    assert "LANDED NOTHING" not in detail, detail
    assert routed.dropped == [], \
        "the executor's own hand-back was read as the tick reporting the work finished"
    assert "DISCHARGED" not in routed.log()


def test_the_tick_RELEASING_really_does_discharge(routed):
    """THE PASS BRANCH, WHICH HAS NEVER ONCE BEEN REACHED IN THIS MODULE'S LIFE.

    §7 of the finding asked for exactly this and could not write it: no test reached
    `_still_claimed` with a True answer, so a condition that had never been false survived in a
    module whose own docstring is about that failure. Both branches now exist, so the discharge is
    a control rather than a constant in either direction.

    MUTATION: make `_still_claimed` return True unconditionally and this fires; make it return
    False unconditionally and the test above fires. Neither constant passes both.
    """
    def lands_then_releases():
        routed.child_binds(routed.worktree_store)()
        # `python3 -m background.delivery_lane --release the-item`, run from the worktree.
        assert delivery_lane.claims_mod.release("the-item", path=routed.worktree_store) is True, \
            "the tick's release found nothing to remove -- run_once never claimed there"

    routed.spawn(child=lands_then_releases)
    ran, detail = seat_executor.run_once()

    assert "LANDED NOTHING" not in detail, detail
    assert routed.dropped == ["the-item"], "the tick said it was finished and was not believed"
    assert "DISCHARGED the-item" in routed.log()


def test_the_hand_back_releases_only_the_claim_THIS_turn_took(routed):
    """A hand-back that cleared whatever was there would free another writer's live claim.

    MUTATION: drop the `claimed_at` comparison in `_hand_back` and this fires.
    """
    def another_writer_reclaims_it():
        # Someone else takes the id after `run_once` claimed it and before the turn ends. That
        # claim is theirs, with their own `claimed_at`, and it must outlive this turn.
        delivery_lane.claims_mod.claim("the-item", path=routed.shared, now=1.0)

    routed.spawn(child=another_writer_reclaims_it)
    seat_executor.run_once()

    assert "the-item" in delivery_lane.held(path=routed.shared), \
        "the hand-back released a claim this turn did not take"


