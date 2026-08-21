"""RUNG-1 PUBLISH-GATE WEDGE draw -- R15 both-ways proof (director rulings UNWEDGE_PUBLISH_
PRIORITY_ZERO 2026-07-23 + WEDGE3_AND_RUNG1_MECHANISE 2026-07-24, the SECOND consumed-not-absorbed
on the same rule).

The mechanism: a publish gate that has been failing for >60 min while alerts fire and the tick
idles is PRIORITY-ZERO drawable work -- it blocks ALL publishing, so it outranks every product/
HARDEN lane. `supervisor._publish_gate_wedge_active()` is the detector; it is wired as the TOP rung
of `_self_refill_draw` and mirrored in `_is_drained_and_gated`.

R15 requires a control that can FAIL. These tests prove it BOTH ways:
  * MUST FIRE: this morning's exact state (>=3 failures in-window + alerts firing + no pass at HEAD +
    wedge_since >60 min ago) -> the detector returns a draw, `_self_refill_draw` returns it ABOVE the
    product lanes, and `_is_drained_and_gated` refuses rest.
  * MUST STAY SILENT: a passed gate (last_tested == HEAD), an empty/absent state, a lone flake
    (< threshold), and a wedge younger than 60 min all return None and leave rest/draw untouched.
The window-trim root cause is covered too: `alerted_at`/`failures` alone cap the measurable age below
60 min for a live wedge, so `wedge_since` (persistent, un-trimmed) is what makes ">60 min" provable.
"""
import json
from pathlib import Path

import pytest

from background import supervisor


HOUR = 60 * 60


def _wedged_state(now, *, n=8, wedge_since_age=2 * HOUR, alerted_age=30 * 60, include_wedge_since=True):
    """Construct a realistic wedged .publish_gate_state.json dict.

    Defaults mirror this morning's state: a sustained wedge (8 failures), the failures themselves
    all inside the trimmed 1h window, an alarm that fired ~30 min ago, and a PERSISTENT wedge_since
    ~2h old (the field the writer now stamps). `include_wedge_since=False` reproduces a LEGACY state
    file written before the wedge_since change landed."""
    failures = [
        {"ts": now - (i * 6 * 60), "reason": f"process_run_complete rc=1 on run_complete_{i}.md",
         "rc": 1, "kind": "test_regression", "git_hash": "deadbeef"}
        for i in range(n)
    ]
    state = {"failures": failures, "alerted_at": now - alerted_age}
    if include_wedge_since:
        state["wedge_since"] = now - wedge_since_age
    return state


# The REAL parser, captured before the autouse fixture below replaces the module attribute --
# otherwise the tests that put the parser itself on trial would exercise the stub and pass vacuously.
_REAL_LIVE_GATE_RUNS = supervisor._live_publish_gate_runs


@pytest.fixture(autouse=True)
def _no_live_gate(monkeypatch):
    """The draw now asks `ps` whether a gate run is in flight. Without this, EVERY test in this
    file would take the machine's process table as its subject -- green or red depending on
    whether a publish happened to be running (R15: a control that must win a race has the weather
    as its subject). Tests that are ABOUT the in-flight clause override this explicitly."""
    monkeypatch.setattr(supervisor, "_live_publish_gate_runs", lambda *a, **k: [])


def _write(tmp_path, monkeypatch, state, *, head="HEADHASH", last_tested="OLDHASH"):
    sp = tmp_path / ".publish_gate_state.json"
    lp = tmp_path / ".last_tested_hash"
    sp.write_text(json.dumps(state))
    lp.write_text(last_tested)
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", sp)
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", lp)
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: head)
    return sp, lp


def _green(tmp_path, sha, ts):
    """Stamp the gate's green CLOCK, exactly as `process_run_complete._record_gate_green_clock`
    does: `{"sha": ..., "ts": ...}` in a file BESIDE `.last_tested_hash`.

    Deliberately written to the same `tmp_path` as `_write` and never via a monkeypatched module
    attribute -- the production default is reached by the path the code derives, so a test that
    forgot to call this reads NO green rather than the real machine's."""
    (tmp_path / ".last_tested_green.json").write_text(json.dumps({"sha": sha, "ts": ts}))


def _blocking_record(tmp_path, now, *, node_ids=("tests/x.py::test_x",), age=0.0,
                     git_hash="deadbeef"):
    """Stamp the LIVE gate blocking record, exactly as `process_run_complete` writes it.

    Written to the same `tmp_path` as `_write` and never via a monkeypatched module attribute:
    the draw derives this path from the RESOLVED state path, so a test that forgot to call this
    reads NO record -- which is the honest "I don't know" -- rather than the real machine's."""
    (tmp_path / ".last_gate_blocking_tests.json").write_text(json.dumps(
        {"ts": now - age, "node_ids": list(node_ids), "git_hash": git_hash}))


# ─────────────────────────── MUST FIRE (the wedge is real and old) ──────────────────────────

def test_fires_on_this_mornings_exact_state(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None
    assert "PUBLISH-GATE WEDGE" in msg and "RUNG 1" in msg and "PRIORITY ZERO" in msg
    # carries the diagnostic payload (R5): how long, how many, and the HEAD it never passed
    assert "min" in msg and "8 failures" in msg and "HEADHASH" in msg


def test_self_refill_draw_returns_wedge_above_product_lanes(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    # Even with a live BUILD atom available, the wedge rung MUST win (it is checked first).
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent",
                        lambda *a, **k: [{"id": "SOME_BUILD_ATOM"}])
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    out = supervisor._self_refill_draw()
    assert out is not None and "PUBLISH-GATE WEDGE" in out and "SOME_BUILD_ATOM" not in out


def test_is_drained_and_gated_refuses_rest_while_wedged(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    # Every OTHER lane empty -> the ONLY thing keeping the tick awake is the wedge rung.
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_actionable_backlog_item", lambda *a, **k: None)
    assert supervisor._is_drained_and_gated() is False


def test_fires_via_alerted_at_when_wedge_since_absent_but_old(tmp_path, monkeypatch):
    """LEGACY fallback: a state file written before wedge_since existed still fires if alerted_at
    (or the earliest in-window failure) is itself >60 min old -- fail-safe TOWARD drawing."""
    now = 1_800_000_000.0
    state = _wedged_state(now, include_wedge_since=False, alerted_age=95 * 60)
    _write(tmp_path, monkeypatch, state)
    assert supervisor._publish_gate_wedge_active(now=now) is not None


# ─────────────────────────── MUST STAY SILENT (no draw, rest allowed) ───────────────────────

def test_silent_when_gate_passed_at_head(tmp_path, monkeypatch):
    """INDEPENDENCE (R15 anti-tautology): even with failures on file, a pass at HEAD => stale
    failures => no phantom wedge draw."""
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now), head="SAMEHASH", last_tested="SAMEHASH")
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_silent_on_empty_state(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, {"failures": [], "alerted_at": None, "wedge_since": None})
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_silent_on_absent_state_file(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", tmp_path / "nope.json")
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", tmp_path / "nope_hash")
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: "H")
    assert supervisor._publish_gate_wedge_active(now=1_800_000_000.0) is None


def test_silent_on_lone_flake_below_threshold(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now, n=2))  # < PUBLISH_GATE_WEDGE_MIN_FAILURES
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_silent_when_wedge_younger_than_60_min(tmp_path, monkeypatch):
    """A fresh sustained wedge (alarm already fired, but only ~40 min old) must NOT yet draw -- the
    rule is 60 min. This is the boundary the window-trim problem hid; wedge_since makes it precise."""
    now = 1_800_000_000.0
    state = _wedged_state(now, wedge_since_age=40 * 60, alerted_age=20 * 60, include_wedge_since=True)
    # earliest failure also < 60 min (n=8 * 6min = 42min span), so no candidate is >60 min old
    _write(tmp_path, monkeypatch, state)
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_malformed_state_is_silent_not_raising(tmp_path, monkeypatch):
    sp = tmp_path / ".publish_gate_state.json"
    sp.write_text("{ this is not json")
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", sp)
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", tmp_path / "h")
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: "H")
    # never raises into the draw ladder
    assert supervisor._publish_gate_wedge_active(now=1_800_000_000.0) is None


# ══════════════════════════════════════════════════════════════════════════════
# ALARM → DIAL — the draw names the alarm's own filed cure
# (2026-08-09, DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH, draw 2b)
#
# The named defect: on 2026-08-08 the cure for a 7h wedge sat filed as
# WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD while the wedge alarm fired ten times and
# addressed only the director. RUNG 1 is already priority zero, so lifting the filed
# finding INTO this message is what "the alarm raises its own cure's draw priority"
# means mechanically: the finding stops competing with feature work in the staging
# backlog and becomes the priority-zero instruction.
#
# Both ways: cited findings must APPEAR, and a state with none must not emit an empty
# citation clause (a control that always prints its own success text cannot fail).
# ══════════════════════════════════════════════════════════════════════════════

def test_draw_names_the_filed_findings_the_alarm_cited(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["cited_findings"] = [
        "WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD_2026-08-08.md",
        "WORKER_FINDING_RELATIVE_HOOK_PATHS_WEDGE_SESSION_2026-08-08.md",
    ]
    _write(tmp_path, monkeypatch, state)
    _blocking_record(tmp_path, now)  # the live record warrants the cached payload
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None
    assert "FILED FINDINGS ALREADY HOLDING THE SUSPECTS" in msg
    assert "WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD_2026-08-08.md" in msg
    assert "draw these FIRST" in msg
    assert "NOT CITABLE" not in msg


def test_mutation_no_cited_findings_no_citation_clause(tmp_path, monkeypatch):
    """Strip the citation and the clause must VANISH — otherwise the draw would always
    claim to have a cure in hand, which is the fail-open shape."""
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))  # no cited_findings key at all
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "FILED FINDINGS" not in msg


def test_malformed_citation_never_breaks_the_draw(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["cited_findings"] = "not-a-list"
    _write(tmp_path, monkeypatch, state)
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "PUBLISH-GATE WEDGE" in msg and "FILED FINDINGS" not in msg


def test_draw_carries_episode_memory_when_it_exceeds_the_window(tmp_path, monkeypatch):
    """The draw, like the alarm, must not narrate hour seven as a fresh hour."""
    now = 1_800_000_000.0
    state = _wedged_state(now, n=6)
    state["episode_failures"] = 42
    _write(tmp_path, monkeypatch, state)
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert "EPISODE: 42 consecutive failures" in msg and "not a fresh hour" in msg


def test_mutation_episode_equal_to_window_adds_no_episode_clause(tmp_path, monkeypatch):
    """A genuinely fresh wedge (episode == window) must NOT gain the escalating language —
    the clause has to be able to be absent or it says nothing when present."""
    now = 1_800_000_000.0
    state = _wedged_state(now, n=6)
    state["episode_failures"] = 6
    _write(tmp_path, monkeypatch, state)
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "EPISODE:" not in msg


# ─── THE PASS THAT HEAD MOVED PAST (2026-08-12: the self-perpetuating false wedge) ──────────
#
# These use a REAL git repository rather than a stubbed ancestry oracle, deliberately. The
# defect being pinned is a claim about git ancestry, so a test that mocks `_commit_is_ancestor`
# would be asserting the mock's behaviour and would pass just as happily against the broken
# exact-equality check (R15 TAUTOLOGY). Real commits make the ordering the thing under test.


def _repo(tmp_path, monkeypatch):
    """A throwaway repo with a linear history, returning a commit-making closure.

    Isolated from the developer's identity/hooks so it cannot fail on an unconfigured box."""
    import subprocess

    root = tmp_path / "repo"
    root.mkdir()
    env = {
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
        "GIT_CONFIG_GLOBAL": str(tmp_path / "nonexistent-gitconfig"),
        "GIT_CONFIG_SYSTEM": str(tmp_path / "nonexistent-gitconfig"),
        "PATH": __import__("os").environ.get("PATH", ""),
    }

    def git(*args):
        r = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                           text=True, env=env, timeout=30)
        assert r.returncode == 0, f"git {args} failed: {r.stderr}"
        return r.stdout.strip()

    git("init", "-q", "-b", "main")

    def commit(msg):
        (root / "f.txt").write_text(msg)
        git("add", "f.txt")
        git("commit", "-q", "--no-verify", "-m", msg)
        return git("rev-parse", "--short", "HEAD")

    monkeypatch.setattr(supervisor, "PROJECT_DIR", root)
    return commit, git


def test_silent_when_the_gate_passed_after_the_failures_even_though_head_moved_on(
        tmp_path, monkeypatch):
    """THE LIVE DEFECT, on real ancestry: publishing a green is itself a commit.

    Observed 2026-08-12: the gate passed at 62818325d, published, and eight further commits
    landed. `.last_tested_hash != HEAD` forever after, so the RUNG-1 priority-zero doorbell
    fired every tick for ~75h / 201 "failures" while publishing was healthy the whole time --
    and each tick it woke committed its own work, pushing HEAD one further from the pass and
    arming the next draw harder. The detector was not merely stale; it fed itself.

    THE INSTRUMENT CHANGED UNDER THIS TEST ON 2026-08-20, and its subject did not. The clear used
    to be decided by ancestry (`passed_at` is a descendant of `failed_at`); it is now decided by
    the RECORDED GREEN CLOCK, and the ancestry here survives only as PROVENANCE (`passed_at` is
    on `head`'s history). The history below is left ascending on purpose so the two instruments
    agree in this case -- the test that pulls them apart is
    `test_the_ordering_mutation_a_green_recorded_later_but_committed_earlier`."""
    commit, _ = _repo(tmp_path, monkeypatch)
    failed_at = commit("the commit the gate was red at")
    passed_at = commit("the commit the gate went GREEN at")
    commit("the publish of that green result")
    head = commit("another lane landing meanwhile")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)
    _green(tmp_path, passed_at, now + 60)  # recorded AFTER every failure in the window

    assert supervisor._publish_gate_wedge_active(now=now) is None, (
        "a gate pass that is newer than every recorded failure, on HEAD's own history, "
        "means those failures are STALE -- drawing priority-zero unwedge work here is the "
        "phantom that burned 201 ticks"
    )


def test_mutation_fires_when_the_recorded_pass_PREDATES_the_failures(tmp_path, monkeypatch):
    """MUTATION (the direction that must still draw): reverse the ordering only.

    Same shape as above, same non-equal hashes -- but the green came BEFORE the red. That is a
    genuine wedge: the gate has not passed since it started failing. If this went silent the
    fix would have bought its quiet by disarming the alarm, which is the harmful direction.

    THE NULL CONTROL FOR THE 2026-08-20 CLOCK REPAIR (R15). The green is stamped, and stamped
    BEFORE the failures. Without this pin the repair degenerates into "any green ever recorded
    silences the alarm" -- the fail-open shape, strictly worse than the bug it replaced."""
    commit, _ = _repo(tmp_path, monkeypatch)
    passed_at = commit("an OLD green, before the breakage")
    failed_at = commit("the commit that broke the gate")
    head = commit("still broken, still committing")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)
    _green(tmp_path, passed_at, now - 3 * HOUR)  # a real green, but it came FIRST

    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "PUBLISH-GATE WEDGE" in msg, (
        "a pass that predates the failures proves nothing -- the wedge is real and must draw"
    )


def test_mutation_fires_when_the_pass_is_on_a_branch_HEAD_never_took(tmp_path, monkeypatch):
    """MUTATION (independence): a green on abandoned history is not a green for HEAD.

    Newer by timestamp, descendant of nothing HEAD carries. Publishing happens from HEAD, so a
    pass HEAD cannot reach says nothing about whether HEAD can publish.

    THE PROVENANCE LEG, PUT ON TRIAL DIRECTLY (R15, 2026-08-20). The clock is stamped AFTER every
    failure, so the ORDER question is satisfied and the ONLY thing left refusing the clear is
    ancestry doing its other, still-valid job. Delete the `_commit_is_ancestor` line from
    `_gate_pass_supersedes_failures` -- i.e. throw the branch out with the clock -- and this test
    is the one that goes red."""
    commit, git = _repo(tmp_path, monkeypatch)
    failed_at = commit("the commit the gate was red at")
    git("checkout", "-q", "-b", "sidetrack")
    passed_at = commit("a green that only ever existed on a side branch")
    git("checkout", "-q", "main")
    head = commit("main carries on without it")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)
    _green(tmp_path, passed_at, now + 60)  # the ORDER question is satisfied; provenance is not

    assert supervisor._publish_gate_wedge_active(now=now) is not None, (
        "a pass off HEAD's history must not silence the draw"
    )


def test_unknowable_ancestry_still_draws(tmp_path, monkeypatch):
    """FAIL-SAFE: an unavailable check is a FAILED check (R15), never a convenient pass.

    Hashes git cannot resolve (pruned, malformed, a state file from another machine) must leave
    the alarm exactly as armed as it was found. The clock is stamped and newer, so the ONLY thing
    unresolved here is the provenance question git cannot answer."""
    commit, _ = _repo(tmp_path, monkeypatch)
    head = commit("only commit")

    now = 1_800_000_000.0
    state = _wedged_state(now)  # git_hash "deadbeef" -- no such object
    _write(tmp_path, monkeypatch, state, head=head, last_tested="cafebabe")
    _green(tmp_path, "cafebabe", now + 60)

    assert supervisor._publish_gate_wedge_active(now=now) is not None


def test_a_pass_at_the_same_commit_as_the_failure_still_draws(tmp_path, monkeypatch):
    """No recorded clock resolves toward drawing: a SHA alone cannot say which came last.

    This WAS an explicit same-SHA guard in the predicate. Since 2026-08-20 the ordering comes
    from the recorded green clock instead, so the guard was deleted as redundant -- and this
    state, which stamps no clock at all, must still draw. It is therefore also the FAIL-SILENT
    leg at its most ordinary: the sidecar simply is not there yet."""
    commit, _ = _repo(tmp_path, monkeypatch)
    both = commit("green and red both recorded here")
    head = commit("HEAD has moved on")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = both
    _write(tmp_path, monkeypatch, state, head=head, last_tested=both)

    assert supervisor._publish_gate_wedge_active(now=now) is not None


# ── THE ORDERING INSTRUMENT RAN BACKWARDS (2026-08-20, the third consecutive RUNG-1 tick) ──
#
# `_gate_pass_supersedes_failures` asked git ancestry "which came last". Since OPS3 the publish
# queue drains NEWEST-MARKER-FIRST, and both SHAs compared are marker subject commits -- so
# across one drain ancestry is ANTI-CORRELATED with time. Live at 16:31Z: three failures
# ascending in ts (14:07/14:37/15:07Z) whose SHAs strictly DESCEND in history, and a green
# recorded 27 min later on a commit 3 EARLIER. The alarm stayed armed on a gate that was green
# and publishing, for three ticks. Evidence: docs/staging/done/WORKER_FINDING_THE_WEDGES_
# ORDERING_INSTRUMENT_RUNS_BACKWARDS_SINCE_THE_QUEUE_BECAME_A_STACK_2026-08-20.md.


def test_the_ordering_mutation_a_green_recorded_later_but_committed_earlier(
        tmp_path, monkeypatch):
    """THE SUBJECT MUTATION: this morning's exact recorded shape. MUST CLEAR.

    The failures ascend in `ts` while their SHAs descend through history, and the green sits at a
    commit that is an ANCESTOR of all three -- so every ancestry answer available points the
    wrong way and only the clock is right. Under the pre-repair predicate this returned a
    PRIORITY-ZERO draw; that divergence is this control firing on its own named defect.

    The failure ROWS are also shuffled relative to their timestamps, because the list order is
    precisely what stopped being trustworthy: the verdict must come from `max(ts)`, never from
    `failures[-1]`."""
    commit, _ = _repo(tmp_path, monkeypatch)
    passed_at = commit("43766e01e -- the marker the drain published LAST and committed FIRST")
    oldest_in_history = commit("c24e81e07 -- newest failure by the clock, oldest commit")
    middle = commit("8ba61d802")
    newest_in_history = commit("81449dcb4 -- oldest failure by the clock, newest commit")
    head = commit("the publish commit and whatever landed after it")

    now = 1_800_000_000.0
    state = _wedged_state(now, n=3)
    # ts ascending 14:07 -> 14:37 -> 15:07; SHAs strictly DESCENDING through history.
    for f, sha, age in zip(state["failures"],
                           [newest_in_history, middle, oldest_in_history],
                           [60 * 60, 30 * 60, 0]):
        f["git_hash"], f["ts"] = sha, now - age
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)
    _green(tmp_path, passed_at, now + 27 * 60)  # 27 minutes after the newest failure

    assert supervisor._publish_gate_wedge_active(now=now) is None, (
        "the gate recorded a green AFTER every failure, on HEAD's history -- ancestry disagrees "
        "only because the queue drains newest-first, and ancestry is no longer the clock"
    )


def test_null_control_ancestry_says_superseded_and_the_clock_says_otherwise(
        tmp_path, monkeypatch):
    """THE NULL CONTROL THAT PROVES THE CLOCK REPLACED ANCESTRY RATHER THAN JOINING IT.

    Here ancestry says exactly what it used to say to grant a clear -- the green is a DESCENDANT
    of the failure commit -- but the recorded green clock is older than the newest failure. The
    old predicate cleared this; the repaired one must draw. Without this pin, a repair that kept
    ancestry as an OR-branch alongside the clock would pass every other test in this file while
    leaving the original defect fully intact."""
    commit, _ = _repo(tmp_path, monkeypatch)
    failed_at = commit("the gate went red here")
    passed_at = commit("a green committed AFTER it -- ancestry's answer is 'superseded'")
    head = commit("HEAD moved on")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)
    _green(tmp_path, passed_at, now - 3 * HOUR)  # ...but it was recorded BEFORE the failures

    assert supervisor._publish_gate_wedge_active(now=now) is not None, (
        "ancestry must no longer be able to grant a clear on its own -- the clock decides order"
    )


@pytest.mark.parametrize("payload", [
    None,                                          # never written -- every tree until the next green
    "{not json at all",                            # truncated / corrupt
    '{"sha": "SOMEONE_ELSES", "ts": 1800000060}',  # a sidecar left by an EARLIER green
    '{"sha": "PASSED", "ts": "recently"}',         # a ts that is not a clock
    '{"sha": "PASSED"}',                           # the half-write
    '["PASSED", 1800000060]',                      # right values, wrong shape
])
def test_fail_silent_an_unusable_green_clock_keeps_the_alarm_armed(
        tmp_path, monkeypatch, payload):
    """FAIL-SILENT (R15): an unavailable check is a FAILED check, never a convenient pass.

    Every row here is a state where the ORDER question genuinely cannot be answered. All of them
    must draw. Note the third: a sidecar naming a DIFFERENT sha must not lend its timestamp to
    the hash file's -- the two halves are one record or they are nothing."""
    commit, _ = _repo(tmp_path, monkeypatch)
    failed_at = commit("the gate went red here")
    passed_at = commit("a green, on HEAD's history, newer by ancestry")
    head = commit("HEAD moved on")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)
    if payload is not None:
        (tmp_path / ".last_tested_green.json").write_text(payload.replace("PASSED", passed_at))

    assert supervisor._publish_gate_wedge_active(now=now) is not None, (
        f"an unusable green record ({payload!r}) must leave RUNG 1 exactly as armed as it was"
    )


def test_the_clock_is_read_beside_the_hash_file_not_beside_the_module_default(
        tmp_path, monkeypatch):
    """THE HALF-A-CONTROL MUTATION (R15, `feedback_a_two_part_control_can_have_each_half_read_a_
    different_tree`) -- which is the class this whole repair belongs to.

    A `_recorded_green_clock` that defaulted to the production `LAST_TESTED_GREEN_FILE` even when
    the hash path was redirected would make every test in this file read the real machine's green
    while reading a fixture's hash: the two halves of one record, taken from two trees. Proven by
    construction rather than asserted -- the clock is written ONLY at the redirected location and
    the module default is left pointing wherever it points."""
    commit, _ = _repo(tmp_path, monkeypatch)
    failed_at = commit("red")
    passed_at = commit("green")
    head = commit("head")
    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _, lp = _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)

    assert supervisor.LAST_TESTED_GREEN_FILE.parent != lp.parent, "fixture premise"
    assert supervisor._recorded_green_clock(passed_at, last_tested_path=lp) is None
    _green(tmp_path, passed_at, now + 60)
    assert supervisor._recorded_green_clock(passed_at, last_tested_path=lp) == now + 60
    assert supervisor._publish_gate_wedge_active(now=now) is None


# ──────────── THE WORLD MOVED AFTER THE READING WAS TAKEN (2026-08-17, both ways) ────────────
#
# The draw named its failures' count, ts and reason but never their `git_hash`, so it announced
# "no pass at HEAD" about failures recorded at a commit whose fix had already landed -- twice in
# one hour, each time at PRIORITY ZERO. The repair is TEXT ONLY. The direction that matters most
# here is the SILENT one: a repair that suppressed the draw would blind RUNG 1 to any wedge that
# survives a commit, so every test below also asserts the draw is still RETURNED.


def _at(state, git_hash):
    for f in state["failures"]:
        f["git_hash"] = git_hash
    return state


def test_superseded_clause_fires_when_every_failure_predates_head(tmp_path, monkeypatch):
    """MUST FIRE: all failures at an ancestor of HEAD -> say so, name the log command, keep drawing."""
    now = 1_000_000.0
    _write(tmp_path, monkeypatch, _at(_wedged_state(now), "OLDCOMMIT"), head="HEADHASH")
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    monkeypatch.setattr(supervisor, "_commit_is_ancestor",
                        lambda a, d: True if (a, d) == ("OLDCOMMIT", "HEADHASH") else None)
    msg = supervisor._publish_gate_wedge_active()
    assert msg is not None, "the draw must STILL FIRE -- there is no green at HEAD"
    assert "HEAD HAS MOVED SINCE EVERY RECORDED FAILURE" in msg
    assert "git log --oneline OLDCOMMIT..HEADHASH" in msg
    assert "does not mean the wedge is over" in msg


def test_superseded_clause_is_silent_when_failures_are_at_head(tmp_path, monkeypatch):
    """MUST STAY SILENT -- THE REGRESSION-CATCHING DIRECTION. Failures recorded AT HEAD are the
    real, reproduced-at-this-tree wedge; nothing may soften the draw."""
    now = 1_000_000.0
    _write(tmp_path, monkeypatch, _at(_wedged_state(now), "HEADHASH"), head="HEADHASH",
           last_tested="OLDHASH")
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    msg = supervisor._publish_gate_wedge_active()
    assert msg is not None
    assert "HEAD HAS MOVED" not in msg


def test_superseded_clause_is_silent_on_a_mixed_hash_set(tmp_path, monkeypatch):
    """A wedge that OUTLIVED a commit is the case this must never soften -> unknown -> no clause."""
    now = 1_000_000.0
    state = _at(_wedged_state(now), "OLDCOMMIT")
    state["failures"][0]["git_hash"] = "NEWERCOMMIT"
    _write(tmp_path, monkeypatch, state, head="HEADHASH")
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    # Selective on purpose: a blanket True would ALSO satisfy _gate_pass_supersedes_failures and
    # return None, so the test would "pass" for the wrong reason.
    monkeypatch.setattr(
        supervisor, "_commit_is_ancestor",
        lambda a, d: True if (a, d) in (("OLDCOMMIT", "HEADHASH"), ("NEWERCOMMIT", "HEADHASH")) else None)
    msg = supervisor._publish_gate_wedge_active()
    assert msg is not None
    assert "HEAD HAS MOVED" not in msg


@pytest.mark.parametrize("gh", ["", "unknown", None])
def test_superseded_clause_is_silent_without_a_usable_hash(tmp_path, monkeypatch, gh):
    """FAIL-OPEN GUARD (R15): a legacy record with no hash reads as unknown and prints nothing."""
    now = 1_000_000.0
    _write(tmp_path, monkeypatch, _at(_wedged_state(now), gh), head="HEADHASH")
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    monkeypatch.setattr(supervisor, "_commit_is_ancestor", lambda a, d: True)
    msg = supervisor._publish_gate_wedge_active()
    assert msg is not None
    assert "HEAD HAS MOVED" not in msg


def test_superseded_clause_is_silent_when_git_cannot_answer(tmp_path, monkeypatch):
    """Ancestry UNKNOWABLE (pruned object, git failure) -> unknown -> unchanged message."""
    now = 1_000_000.0
    _write(tmp_path, monkeypatch, _at(_wedged_state(now), "OLDCOMMIT"), head="HEADHASH")
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    monkeypatch.setattr(supervisor, "_commit_is_ancestor", lambda a, d: None)
    msg = supervisor._publish_gate_wedge_active()
    assert msg is not None
    assert "HEAD HAS MOVED" not in msg


def test_in_flight_clause_fires_and_suspends_the_enumerate_instruction(tmp_path, monkeypatch):
    """MUST FIRE: a live gate run -> warn, and WITHDRAW the 'run the argv without -x' remedy that
    would OOM it on this 15GB cgroup."""
    now = 1_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    monkeypatch.setattr(supervisor, "_live_publish_gate_runs",
                        lambda *a, **k: [{"pid": 126285, "elapsed_s": 1609}])
    msg = supervisor._publish_gate_wedge_active()
    assert msg is not None
    assert "A GATE RUN IS IN FLIGHT RIGHT NOW" in msg
    assert "PID 126285" in msg
    assert "~26 min" in msg
    assert "SUSPENDED" in msg


def test_in_flight_clause_is_silent_when_no_gate_is_running(tmp_path, monkeypatch):
    """MUST STAY SILENT: nothing running -> the enumerate instruction stands unchanged."""
    now = 1_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    msg = supervisor._publish_gate_wedge_active()
    assert msg is not None
    assert "IN FLIGHT" not in msg
    assert "run the gate's argv without `-x`" in msg


def test_live_gate_runs_parses_ps_and_ignores_grep_and_junk():
    """The parser, on trial directly: real `ps -eo pid,etimes,args` shape."""
    out = (
        "    PID ELAPSED COMMAND\n"
        " 126285    1609 /usr/bin/python3 /home/rich/synthetic-enterprise/background/"
        "process_run_complete.py /home/rich/.../run_complete_20260817T104521Z.md\n"
        " 140778       6 grep process_run_complete.py\n"
        "  bogus    xxx  /usr/bin/python3 background/process_run_complete.py m.md\n"
        " 999999      12 /usr/bin/python3 background/other_thing.py\n"
    )
    assert _REAL_LIVE_GATE_RUNS(lambda: out) == [{"pid": 126285, "elapsed_s": 1609}]


def test_live_gate_runs_is_empty_when_ps_is_unavailable():
    """UNAVAILABLE -> [] -> no warning -> the draw is exactly what it was before this existed."""
    def _boom():
        raise OSError("no ps")
    assert _REAL_LIVE_GATE_RUNS(_boom) == []


# ══════════════════════════════════════════════════════════════════════════════
# THE CACHE MUST AGREE WITH THE RECORD, NOT SUBSTITUTE FOR IT
# (2026-08-20, WORKER_FINDING_THE_WEDGE_STATE_LAUNDERS_THE_ALARMS_OWN_I_DONT_KNOW_
#  INTO_A_CONFIDENT_STALE_ANSWER, BLOCKING, lane H_harness)
#
# `process_run_complete.last_blocking_tests()` fails closed on four distinct unknowns --
# absent, unreadable, malformed, STALE -- and says so as `([], None)`. That contract was
# in force and NO READER ASKED IT. `record_publish_gate_failure` copied the ANSWER into
# `.publish_gate_state.json` and dropped the WARRANT: the cached copy carries no `ts` of
# its own and no age bound, so the one surface the RUNG-1 draw reads could not tell "the
# last gate's red was X" from "no gate has recorded a red since X was repaired". On
# 2026-08-20 the draw dispatched seven findings cited from a red repaired an hour before
# the pin was taken, and three consecutive priority-zero ticks spent themselves on it.
#
# R15 -- three mutations, each on its own named defect, exactly as the finding specified:
#   * FAIL-OPEN ON ABSENCE   : record gone, cached payload populated -> withhold.
#   * FAIL-OPEN ON STALENESS : record present but past its age bound -> withhold.
#   * NULL CONTROL           : fresh, in-age record -> the draw NAMES the payload.
# Without the null control the cheapest wrong repair -- never citing anything at all --
# passes both mutation legs and destroys the alarm it was meant to make honest.
# ══════════════════════════════════════════════════════════════════════════════

def _laundered_state(now):
    """A wedged state carrying the exact payload shape that was dispatched on 2026-08-20."""
    state = _wedged_state(now)
    state["cited_findings"] = ["WORKER_FINDING_STALE_SUSPECT_2026-08-19.md"]
    state["blocking_tests"] = [
        "FAILED tests/saas/reporting/test_partial_year_clv_headline_guard.py::"
        "test_the_final_partial_year_still_values_the_book"
    ]
    state["red_census"] = "complete"
    state["total_red"] = 1
    return state


def test_mutation_absent_record_withholds_the_cached_blocking_payload(tmp_path, monkeypatch):
    """FAIL-OPEN ON ABSENCE -- the live defect, reproduced. No record on disk, a fully
    populated cache: the draw must still FIRE (the wedge is real) and must name NOTHING."""
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _laundered_state(now))
    assert not (tmp_path / ".last_gate_blocking_tests.json").exists(), "precondition: no record"
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "PUBLISH-GATE WEDGE" in msg, "the wedge draw must still fire"
    assert "FILED FINDINGS" not in msg
    assert "WORKER_FINDING_STALE_SUSPECT_2026-08-19.md" not in msg
    assert "NOT CITABLE AND HAS BEEN WITHHELD" in msg
    assert "ENUMERATE AT HEAD" in msg
    # and the depth claim, drawn from the same uncitable cache, falls with it
    assert "DEPTH UNKNOWN" in msg
    assert "enumerated the WHOLE red set" not in msg


def test_mutation_stale_record_withholds_the_cached_blocking_payload(tmp_path, monkeypatch):
    """FAIL-OPEN ON STALENESS -- a record that exists but is past its own age bound is one
    of the four unknowns, and must reach this reader as one."""
    from background import process_run_complete as prc
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _laundered_state(now))
    _blocking_record(tmp_path, now, age=prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS + 60)
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "PUBLISH-GATE WEDGE" in msg
    assert "FILED FINDINGS" not in msg
    assert "NOT CITABLE AND HAS BEEN WITHHELD" in msg


def test_mutation_malformed_record_withholds_the_cached_blocking_payload(tmp_path, monkeypatch):
    """The third and fourth unknowns share a leg: unreadable/malformed must not read as
    'a fresh record naming nothing', and must never raise into the draw ladder."""
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _laundered_state(now))
    (tmp_path / ".last_gate_blocking_tests.json").write_text("{not json")
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "NOT CITABLE AND HAS BEEN WITHHELD" in msg


def test_null_control_a_fresh_record_lets_the_payload_through(tmp_path, monkeypatch):
    """NULL CONTROL -- the alarm must still work. Same cache, same draw, only the record's
    freshness moves: the citation, the named test count and the census depth all return.

    This is the leg that kills the cheapest wrong repair (cite nothing, ever)."""
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _laundered_state(now))
    _blocking_record(tmp_path, now, age=60.0)
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None
    assert "FILED FINDINGS ALREADY HOLDING THE SUSPECTS" in msg
    assert "WORKER_FINDING_STALE_SUSPECT_2026-08-19.md" in msg
    assert "NOT CITABLE" not in msg
    # the census depth claim is warranted again, so the loud default steps aside
    assert "enumerated the WHOLE red set" in msg
    assert "DEPTH UNKNOWN" not in msg


def test_the_withholding_clause_is_absent_when_there_is_nothing_to_withhold(
        tmp_path, monkeypatch):
    """A clause that always prints cannot fail, and cannot be evidence that anything was
    withheld. An honest empty cache + an absent record must produce NO withholding text."""
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))  # no cited_findings, no blocking_tests
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "PUBLISH-GATE WEDGE" in msg
    assert "NOT CITABLE" not in msg and "WITHHELD" not in msg


def test_a_raising_reader_withholds_rather_than_crashing_the_draw_ladder(tmp_path, monkeypatch):
    """R15 FAIL-SILENT: an unavailable check is a FAILED check, and here failing means
    WITHHOLDING. The real helper is on trial -- the delegated reader is what is broken, not
    the helper -- so this cannot pass by asserting a stub's behaviour.

    Both halves matter: the draw must still FIRE (a broken suspect-reader must never blind
    RUNG 1 to a real wedge, which would be strictly worse than saying nothing), and it must
    not raise into the ladder that every lower rung is queued behind."""
    from background import publish_gate_blocking_read as reader
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _laundered_state(now))
    _blocking_record(tmp_path, now)  # a record that WOULD warrant the payload

    def _boom(*_a, **_k):
        raise RuntimeError("reader gone")
    # The DELEGATE is what breaks. Since 2026-08-21 that is the leaf reader, not
    # `process_run_complete.last_blocking_tests` -- the supervisor no longer imports the
    # publisher at all (see `test_publish_scope.py::test_the_supervisor_does_not_import_the_
    # publish_path`). Patching the publisher here would leave this test passing over a stub
    # nothing calls, which is the tautology shape it was written to avoid.
    monkeypatch.setattr(reader, "read_blocking_record", _boom)

    # READ THE RECORD THE PRODUCTION CALL READS (2026-08-21). This guard used to assert on
    # `_live_gate_blocking_record(now=now)` with NO `record_path`, i.e. the DEFAULT
    # `PROJECT_DIR/docs/observability/.last_gate_blocking_tests.json` -- and that form cannot
    # fail. `now` is a fixed 2027 timestamp, so any record really on disk is ~1664x past the
    # age bound and answers ([], None) from STALENESS whether or not the patch above took
    # effect (measured: the unpatched call returns ([], None) at this `now`); in the gate's
    # HEAD checkout the file is untracked and absent, which answers ([], None) too. So the one
    # line standing between this test and the tautology its own docstring disclaims was
    # proving the age bound, not the delegation. Point it at the FRESH record this test wrote
    # -- the same path `_publish_gate_wedge_active` derives -- and the assertion becomes a real
    # measurement of the patched delegate: unpatched, this record WOULD be cited.
    record = tmp_path / supervisor.GATE_BLOCKING_TESTS_FILENAME
    assert record.exists(), "precondition: a record the unpatched reader would cite"
    assert supervisor._live_gate_blocking_record(now=now, record_path=record) == ([], None)
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "PUBLISH-GATE WEDGE" in msg, "a broken reader must not blind RUNG 1"
    assert "FILED FINDINGS" not in msg
    assert "NOT CITABLE AND HAS BEEN WITHHELD" in msg
