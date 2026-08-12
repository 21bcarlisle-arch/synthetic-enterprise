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


def _write(tmp_path, monkeypatch, state, *, head="HEADHASH", last_tested="OLDHASH"):
    sp = tmp_path / ".publish_gate_state.json"
    lp = tmp_path / ".last_tested_hash"
    sp.write_text(json.dumps(state))
    lp.write_text(last_tested)
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", sp)
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", lp)
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: head)
    return sp, lp


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
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None
    assert "FILED FINDINGS ALREADY HOLDING THE SUSPECTS" in msg
    assert "WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD_2026-08-08.md" in msg
    assert "draw these FIRST" in msg


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
    arming the next draw harder. The detector was not merely stale; it fed itself."""
    commit, _ = _repo(tmp_path, monkeypatch)
    failed_at = commit("the commit the gate was red at")
    passed_at = commit("the commit the gate went GREEN at")
    commit("the publish of that green result")
    head = commit("another lane landing meanwhile")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)

    assert supervisor._publish_gate_wedge_active(now=now) is None, (
        "a gate pass that is newer than every recorded failure, on HEAD's own history, "
        "means those failures are STALE -- drawing priority-zero unwedge work here is the "
        "phantom that burned 201 ticks"
    )


def test_mutation_fires_when_the_recorded_pass_PREDATES_the_failures(tmp_path, monkeypatch):
    """MUTATION (the direction that must still draw): reverse the ordering only.

    Same shape as above, same non-equal hashes -- but the green came BEFORE the red. That is a
    genuine wedge: the gate has not passed since it started failing. If this went silent the
    fix would have bought its quiet by disarming the alarm, which is the harmful direction."""
    commit, _ = _repo(tmp_path, monkeypatch)
    passed_at = commit("an OLD green, before the breakage")
    failed_at = commit("the commit that broke the gate")
    head = commit("still broken, still committing")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = failed_at
    _write(tmp_path, monkeypatch, state, head=head, last_tested=passed_at)

    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None and "PUBLISH-GATE WEDGE" in msg, (
        "a pass that predates the failures proves nothing -- the wedge is real and must draw"
    )


def test_mutation_fires_when_the_pass_is_on_a_branch_HEAD_never_took(tmp_path, monkeypatch):
    """MUTATION (independence): a green on abandoned history is not a green for HEAD.

    Newer by timestamp, descendant of nothing HEAD carries. Publishing happens from HEAD, so a
    pass HEAD cannot reach says nothing about whether HEAD can publish."""
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

    assert supervisor._publish_gate_wedge_active(now=now) is not None, (
        "a pass off HEAD's history must not silence the draw"
    )


def test_unknowable_ancestry_still_draws(tmp_path, monkeypatch):
    """FAIL-SAFE: an unavailable check is a FAILED check (R15), never a convenient pass.

    Hashes git cannot resolve (pruned, malformed, a state file from another machine) must leave
    the alarm exactly as armed as it was found."""
    commit, _ = _repo(tmp_path, monkeypatch)
    head = commit("only commit")

    now = 1_800_000_000.0
    state = _wedged_state(now)  # git_hash "deadbeef" -- no such object
    _write(tmp_path, monkeypatch, state, head=head, last_tested="cafebabe")

    assert supervisor._publish_gate_wedge_active(now=now) is not None


def test_a_pass_at_the_same_commit_as_the_failure_still_draws(tmp_path, monkeypatch):
    """Ambiguous ordering resolves toward drawing: same SHA cannot say which came last."""
    commit, _ = _repo(tmp_path, monkeypatch)
    both = commit("green and red both recorded here")
    head = commit("HEAD has moved on")

    now = 1_800_000_000.0
    state = _wedged_state(now)
    state["failures"][-1]["git_hash"] = both
    _write(tmp_path, monkeypatch, state, head=head, last_tested=both)

    assert supervisor._publish_gate_wedge_active(now=now) is not None
