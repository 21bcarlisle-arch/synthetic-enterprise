"""Tests for background/build_executor.py — the SAFE-DARK executor foundation.

Covers Appendix-C steps 1-3 (AUTONOMOUS_EXECUTOR_SPEC.md):
  * skeleton primitives: dispatch_turn / reap_turn / _classify_infra_failure / env hygiene
  * THE RETURN-GATE (write_landed) with its R15 MUTATION TEST proving it catches
    submit-not-landed and fails closed on an unresolvable origin ref
  * run_once end-to-end against a STUB binary + a real local-then-pushed git fixture

No real `claude -p` turn is ever launched: dispatch is exercised only against a stub
script (or a fake Popen). No activation, no launcher wiring, no enable-flag is touched.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from background import agent_status, build_executor


# ---------------------------------------------------------------------------
# Isolation: redirect all side-effect files to tmp so tests never touch the repo
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _isolate_side_effects(tmp_path, monkeypatch):
    monkeypatch.setattr(build_executor, "LOG_FILE", tmp_path / "build-executor-log.md")
    monkeypatch.setattr(build_executor, "TURN_OUTPUT_DIR", tmp_path / "turns")
    monkeypatch.setattr(agent_status, "STATUS_FILE", tmp_path / "agent_status.json")
    monkeypatch.setattr(agent_status, "SITE_STATUS_FILE", tmp_path / "site_agent_status.json")


# ---------------------------------------------------------------------------
# Git fixtures — a real bare "origin" + working clone, and a no-remote repo
# ---------------------------------------------------------------------------
def _git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True
    )


@pytest.fixture
def git_repo(tmp_path):
    """A working clone with a pushed commit on origin/main and an UNpushed commit.

    Returns (work_dir, pushed_sha, unpushed_sha).
    """
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(remote)],
                   check=True, capture_output=True)
    work = tmp_path / "work"
    subprocess.run(["git", "clone", str(remote), str(work)], check=True, capture_output=True)
    _git(work, "config", "user.email", "t@example.com")
    _git(work, "config", "user.name", "Tester")
    _git(work, "checkout", "-b", "main")
    (work / "f.txt").write_text("hello")
    _git(work, "add", "f.txt")
    _git(work, "commit", "-m", "init")
    _git(work, "push", "-u", "origin", "main")
    pushed_sha = _git(work, "rev-parse", "HEAD").stdout.strip()

    # A committed-but-NOT-pushed commit — the submit-not-landed defect.
    (work / "f.txt").write_text("hello again")
    _git(work, "add", "f.txt")
    _git(work, "commit", "-m", "local only")
    unpushed_sha = _git(work, "rev-parse", "HEAD").stdout.strip()

    return work, pushed_sha, unpushed_sha


@pytest.fixture
def no_remote_repo(tmp_path):
    """A repo with a commit but NO origin remote — origin ref unresolvable."""
    repo = tmp_path / "lonely"
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "Tester")
    (repo / "f.txt").write_text("x")
    _git(repo, "add", "f.txt")
    _git(repo, "commit", "-m", "init")
    sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    return repo, sha


def _make_stub(tmp_path, claimed_sha, *, name="claude_stub.py"):
    """A stub `claude` binary that prints the schema-forced structured return."""
    stub = tmp_path / name
    payload = {
        "atom_id": "H10_autonomous_build_executor",
        "action": "build",
        "claimed_commit_sha": claimed_sha,
        "level_before": 0,
        "level_after": 1,
        "gate_status": "green",
    }
    stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        f"print({json.dumps(json.dumps(payload))})\n"
    )
    stub.chmod(0o755)
    return stub


# ===========================================================================
# STEP 1 — skeleton primitives
# ===========================================================================
def test_dispatch_turn_missing_binary_returns_none(tmp_path):
    handle = build_executor.dispatch_turn(
        "prompt", bin_path=tmp_path / "nope-does-not-exist"
    )
    assert handle is None


def test_dispatch_turn_env_hygiene_and_command_shape(tmp_path, monkeypatch):
    """Primitive #1/#11: headless invocation shape + per-launch env hygiene.

    ANTHROPIC_BASE_URL is scrubbed, DISABLE_AUTOUPDATER forced, model defaults to
    the named cheap-tier constant, and the dispatch NEVER touches the real bin
    (a fake Popen captures the call)."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://proxy.local")
    fake_bin = tmp_path / "fake-claude"
    fake_bin.write_text("#!/bin/sh\n")
    fake_bin.chmod(0o755)

    captured = {}

    class _FakeProc:
        pid = 4321

    def _fake_popen(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return _FakeProc()

    out = tmp_path / "turn.out"
    handle = build_executor.dispatch_turn(
        "SCOPE", out_path=out, bin_path=fake_bin, popen=_fake_popen
    )
    assert handle is not None
    cmd = captured["cmd"]
    assert cmd[0] == str(fake_bin)
    assert cmd[1] == "-p"
    assert "--model" in cmd and build_executor.AUTONOMOUS_TURN_MODEL in cmd
    assert "--dangerously-skip-permissions" in cmd
    assert cmd[-1] == "SCOPE"
    env = captured["kwargs"]["env"]
    assert "ANTHROPIC_BASE_URL" not in env
    assert env["DISABLE_AUTOUPDATER"] == "1"
    assert captured["kwargs"]["cwd"] == str(build_executor.PROJECT_DIR)


def test_reap_turn_captures_rc():
    class _Proc:
        returncode = 0

        def poll(self):
            return 0  # already exited

        def wait(self, timeout=None):
            return 0

    handle = build_executor.TurnHandle(
        proc=_Proc(), out_path=Path("/nonexistent"), prompt="p", model="m"
    )
    # No landed evidence (out_path unreadable) + an exited child -> verdict via exit.
    raw = build_executor.reap_turn(handle)
    assert raw.rc == 0
    assert raw.infra_failure is False
    assert raw.landed is False
    assert raw.surfaced_via == "exit"


def test_classify_infra_failure(tmp_path):
    out = tmp_path / "o.out"
    out.write_text("... ECONNREFUSED reaching api ...")
    assert build_executor._classify_infra_failure(1, out) is True
    # rc==0 is never an infra failure regardless of content.
    assert build_executor._classify_infra_failure(0, out) is False
    # non-zero but no transport marker -> a real failure, not infra.
    out.write_text("assertion error in the turn")
    assert build_executor._classify_infra_failure(1, out) is False


def test_parse_structured_return_picks_last_sha_object(tmp_path):
    out = tmp_path / "o.out"
    out.write_text(
        'noise {"unrelated": 1}\n'
        '{"claimed_commit_sha": "abc1234", "action": "build"}\n'
        'trailing {"claimed_commit_sha": "deadbeef", "action": "build"}\n'
    )
    ret = build_executor._parse_structured_return(out)
    assert ret["claimed_commit_sha"] == "deadbeef"


# ===========================================================================
# THE LANDED-EVIDENCE GATE ON reap_turn (R15 mutation test): the verdict must
# surface when work LANDS, never when the process DIES.
# ===========================================================================
def test_reap_surfaces_landed_before_a_hanging_child_exits(git_repo, tmp_path, monkeypatch):
    """MUTATION TEST (named defect: hung-but-successful child blocks the verdict).

    A child that LANDS its work — prints a structured return whose claimed_commit_sha
    is genuinely on origin — and then HANGS FOREVER must NOT block the cycle. reap_turn
    surfaces landed=True the instant the evidence is on origin and reaps the surplus
    child; it never waits for the process to exit.

    Mutation intent: the prior design blocked on `proc.wait(timeout)` FIRST, so this
    hanging child would wedge the reap for the full 30-min bound and surface via
    'timeout'. The assertions surfaced_via=='landed' and timed_out is False go RED
    under that (reverted) design — that is the control proving the gate fires.
    """
    work, pushed_sha, _ = git_repo
    monkeypatch.chdir(work)
    out = tmp_path / "turn.out"
    payload = {
        "atom_id": "H10", "action": "build",
        "claimed_commit_sha": pushed_sha, "gate_status": "green",
    }
    # Prints the landed return, flushes, then sleeps far past the reap timeout below.
    stub = tmp_path / "hang_stub.py"
    stub.write_text(
        "#!/usr/bin/env python3\n"
        "import sys, time\n"
        f"sys.stdout.write({json.dumps(json.dumps(payload))} + '\\n'); sys.stdout.flush()\n"
        "time.sleep(3600)\n"
    )
    stub.chmod(0o755)

    handle = build_executor.dispatch_turn("SCOPE", out_path=out, bin_path=stub, model="m")
    assert handle is not None
    # timeout=30 is only a safety net; a correct gate returns in well under a second.
    raw = build_executor.reap_turn(handle, fetch=False, poll_interval=0.02, timeout=30)

    assert raw.landed is True
    assert raw.surfaced_via == "landed"
    assert raw.claimed_sha == pushed_sha
    assert raw.timed_out is False
    # The surplus (still-hanging) child was reaped, not left running.
    assert handle.proc.poll() is not None


def test_reap_surfaces_failed_when_child_dies_without_landing(tmp_path):
    """Companion: a child that EXITS without landing surfaces a FAILED verdict just as
    promptly (via 'exit'), never a false success. Deterministic fakes, no wall clock."""
    class _DeadProc:
        returncode = 1

        def poll(self):
            return 1  # exited non-zero, nothing landed

        def wait(self, timeout=None):
            return 1

    out = tmp_path / "turn.out"
    out.write_text("some non-JSON turn output, no structured return\n")
    handle = build_executor.TurnHandle(proc=_DeadProc(), out_path=out, prompt="p", model="m")
    raw = build_executor.reap_turn(handle, fetch=False, sleep=lambda _s: None)
    assert raw.landed is False
    assert raw.surfaced_via == "exit"
    assert raw.claimed_sha is None


def test_reap_does_not_reach_timeout_when_work_lands(tmp_path):
    """The deadline is never consulted to a firing once landed evidence is in hand:
    an injected monotonic that would blow a tiny timeout on its 2nd read still yields
    a 'landed' verdict, proving landing short-circuits the timeout path."""
    class _HangingProc:
        returncode = None

        def poll(self):
            return None  # never exits on its own

        def kill(self):
            self.returncode = -9

        def wait(self, timeout=None):
            return self.returncode

    landed_ev = build_executor.LandedEvidence(
        landed=True, claimed_sha="abc1234",
        structured_return={"claimed_commit_sha": "abc1234"},
    )
    handle = build_executor.TurnHandle(
        proc=_HangingProc(), out_path=tmp_path / "x.out", prompt="p", model="m"
    )
    raw = build_executor.reap_turn(
        handle,
        probe=lambda: landed_ev,
        timeout=0,               # a deadline already in the past...
        monotonic=lambda: 100.0, # ...but landing on the first probe never checks it
        sleep=lambda _s: None,
    )
    assert raw.landed is True
    assert raw.surfaced_via == "landed"
    assert raw.timed_out is False
    assert handle.proc.returncode == -9  # surplus hanging child was killed


# ===========================================================================
# STEP 2 — THE RETURN-GATE: write_landed (R15 mutation test FIRST)
# ===========================================================================
def test_write_landed_true_for_genuinely_pushed_sha(git_repo, monkeypatch):
    work, pushed_sha, _ = git_repo
    monkeypatch.chdir(work)
    assert build_executor.write_landed(pushed_sha) is True


def test_return_gate_catches_submit_not_landed(git_repo, monkeypatch):
    """R15 MUTATION TEST (the named defect): a turn 'reports success' with a real,
    well-formed commit SHA that was NEVER pushed to origin. The gate MUST return
    FAILED. This is the exact submit-consumed != write-landed theatre the spec bans.

    Mutation intent: if write_landed were fail-open (e.g. returned True on a valid
    hex SHA without the merge-base ancestry check), this assertion would go red —
    the ancestry check against origin is what makes it fire.
    """
    work, pushed_sha, unpushed_sha = git_repo
    monkeypatch.chdir(work)
    assert unpushed_sha != pushed_sha
    # The SHA is a genuine, valid commit locally — but it is NOT on origin.
    assert build_executor.write_landed(unpushed_sha) is False


def test_return_gate_fail_closed_on_unresolvable_origin(no_remote_repo, monkeypatch):
    """R15 FAIL-SILENT killer: the SHA is a real local commit but there is no origin
    tracking ref to check against. An unavailable check is a FAILED check -> False."""
    repo, sha = no_remote_repo
    monkeypatch.chdir(repo)
    assert build_executor._resolve_origin_ref() is None
    assert build_executor.write_landed(sha) is False


def test_write_landed_false_for_bogus_sha(git_repo, monkeypatch):
    work, _, _ = git_repo
    monkeypatch.chdir(work)
    # Well-formed hex but not a real object.
    assert build_executor.write_landed("0123456789abcdef0123") is False


@pytest.mark.parametrize("bad", [None, "", "   ", "nothex!!", "abc", "g" * 8])
def test_write_landed_false_for_missing_or_malformed(bad, git_repo, monkeypatch):
    work, _, _ = git_repo
    monkeypatch.chdir(work)
    assert build_executor.write_landed(bad) is False


# ===========================================================================
# STEP 3 — run_once end-to-end (draw -> dispatch stub -> gate -> record)
# ===========================================================================
def test_run_once_success_on_pushed_sha(git_repo, tmp_path, monkeypatch):
    """Full cycle against the STUB bin + a real pushed commit whose SHA the gate
    reads back from origin -> SUCCESS."""
    work, pushed_sha, _ = git_repo
    monkeypatch.chdir(work)
    stub = _make_stub(tmp_path, pushed_sha)

    result = build_executor.run_once(
        draw_fn=lambda: "BUILD lane: atom H10 (test draw)",
        bin_path=stub,
        fetch=False,  # local fixture already has origin/main; no network
        out_path=tmp_path / "turn.out",
        poll_interval=0.01,
    )
    assert result.status == "success", result.detail
    assert result.landed is True
    assert result.claimed_sha == pushed_sha


def test_run_once_failed_on_unpushed_sha(git_repo, tmp_path, monkeypatch):
    """End-to-end submit-not-landed: the stub 'succeeds' and returns a real local
    SHA that was never pushed. run_once must record FAILED, never trust rc==0."""
    work, _, unpushed_sha = git_repo
    monkeypatch.chdir(work)
    stub = _make_stub(tmp_path, unpushed_sha)

    result = build_executor.run_once(
        draw_fn=lambda: "BUILD lane: atom H10 (test draw)",
        bin_path=stub,
        fetch=False,
        out_path=tmp_path / "turn.out",
        poll_interval=0.01,
    )
    assert result.status == "failed"
    assert result.landed is False
    assert "NOT on origin" in result.detail


def test_run_once_failed_when_no_sha_returned(git_repo, tmp_path, monkeypatch):
    """A turn that submits but returns no claimed_commit_sha -> FAILED (no evidence)."""
    work, _, _ = git_repo
    monkeypatch.chdir(work)
    # Stub prints a return object WITHOUT the SHA -> parsed as missing.
    stub = tmp_path / "claude_nosha.py"
    stub.write_text(
        "#!/usr/bin/env python3\n"
        'print(\'{"atom_id": "X", "action": "build", "gate_status": "green"}\')\n'
    )
    stub.chmod(0o755)

    result = build_executor.run_once(
        draw_fn=lambda: "BUILD lane draw",
        bin_path=stub,
        fetch=False,
        out_path=tmp_path / "turn.out",
        poll_interval=0.01,
    )
    assert result.status == "failed"
    assert result.claimed_sha is None
    assert "no claimed_commit_sha" in result.detail


def test_run_once_idles_on_wall(tmp_path, monkeypatch):
    """draw returns None (genuine wall) -> idle cycle, NO turn dispatched."""
    dispatched = {"called": False}

    def _no_dispatch(*a, **k):
        dispatched["called"] = True
        raise AssertionError("must not dispatch on a wall")

    monkeypatch.setattr(build_executor, "dispatch_turn", _no_dispatch)
    result = build_executor.run_once(draw_fn=lambda: None)
    assert result.status == "idle"
    assert dispatched["called"] is False


def test_run_once_error_on_missing_binary(tmp_path, monkeypatch):
    result = build_executor.run_once(
        draw_fn=lambda: "some draw",
        bin_path=tmp_path / "absent-bin",
        fetch=False,
        out_path=tmp_path / "turn.out",
    )
    assert result.status == "error"
    assert "binary missing" in result.detail


# ===========================================================================
# SAFE-DARK invariants — no activation surface in this module
# ===========================================================================
def test_module_has_no_daemon_entrypoint():
    """No main()/daemon loop: this module cannot self-activate."""
    assert not hasattr(build_executor, "main")


def test_module_never_references_the_console_only_flag():
    """The console-only kill switch (DIRECTOR_ANSWERS_C7 #6) is director-reserved:
    no agent code may create or modify it. This module reads no flag and creates
    none -- assert structurally (its source never even names the flag path), which
    holds regardless of whether the director has currently enabled it."""
    src = (build_executor.PROJECT_DIR / "background" / "build_executor.py").read_text()
    assert ".build_executor_enabled" not in src, "executor module must not touch the console-only flag"


class TestPredicateGatedEscalation:
    """DIRECTOR_ANSWER_DELEGATE_AND_PREDICATE_FIX (2026-07-16): a turn's self-reported
    gate_status='escalate' fires a director alert IFF the one_way_door predicate confirms
    a genuine door on its door_reason. Reversible review-gate -> downgraded (idle), not sent."""

    def _run_once_escalating(self, monkeypatch, *, door_reason, action="held-no-op"):
        import types
        monkeypatch.setattr(build_executor, "dispatch_turn", lambda *a, **k: object())
        raw = types.SimpleNamespace(
            structured_return={"gate_status": "escalate", "door_reason": door_reason, "action": action},
            claimed_sha=None, landed=False, rc=0, infra_failure=False,
        )
        monkeypatch.setattr(build_executor, "reap_turn", lambda *a, **k: raw)
        return build_executor.run_once(draw_fn=lambda: "drawn: SITE1/A8/B4 billing pricing epoch-gated")

    def test_reversible_review_gate_is_downgraded_not_escalated(self, monkeypatch):
        r = self._run_once_escalating(
            monkeypatch,
            door_reason="SITE1 doors are good enough — director Expert Hour / live-pixel sign-off to reach L3",
        )
        assert r.status == "idle"  # downgraded — NOT a director alert

    def test_genuine_epoch_curriculum_door_escalates(self, monkeypatch):
        r = self._run_once_escalating(monkeypatch, door_reason="open Epoch 4 for the B4 competitor field")
        assert r.status == "escalated"
        assert "Epoch 4" in (r.atom_reason or "")  # self-contained door_reason carried for the NTFY

    def test_genuine_real_money_door_escalates(self, monkeypatch):
        r = self._run_once_escalating(monkeypatch, door_reason="spend real money on a production API key")
        assert r.status == "escalated"

    def test_empty_door_reason_fails_safe_to_escalate(self, monkeypatch):
        # Nothing to classify -> never silently drop a possibly-genuine door.
        r = self._run_once_escalating(monkeypatch, door_reason="", action="")
        assert r.status == "escalated"

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
