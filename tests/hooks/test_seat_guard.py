"""Seat-guard tests (.claude/hooks/_seat.py + the per-hook guard).

WHY: .claude/hooks/ is committed, so EVERY Claude Code session on this repo --
including foreign cloud sessions that are NOT the resident worker seat -- runs
these hooks. The dangerous case is pull_next_work.py consuming the resident
seat's instruction channel from an alien sandbox. The guard makes each
resident-seat hook provably INERT in a foreign seat.

This file proves, per R15 (a control must be able to FAIL), both directions
for every GUARDED hook:
  * FOREIGN seat  -> the hook is inert (exit 0, no stdout/stderr, no writes).
  * RESIDENT seat -> the guard passes through (the hook proceeds past it).
plus _seat.py's own unit behaviour, and the STRUCTURAL LOCK that no future
hook can ship unguarded silently.

MUTATION PROOF (run by hand, reported in the PR): neutering
is_resident_seat() to `return True` reds exactly the foreign-inertness tests
here (they set SE_SEAT=foreign, which an always-True function ignores) and
nothing else -- the resident-passthrough tests and every other suite force
SE_SEAT=resident (or already expect active behaviour), so always-True leaves
them green.
"""
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))
import _seat  # noqa: E402

# The one UNIVERSAL hook: pure refusal-safety, zero repo writes -- runs in
# EVERY seat, so it is deliberately NOT guarded. Dated allowlist, shrink-
# preferred: a hook joins this list only with a per-hook justification in the
# PR, and the default for anything new is GUARDED.
UNIVERSAL_HOOKS = {"block_sudo.py"}  # 2026-08-05, ccm/seat-guard

# ---------------------------------------------------------------------------
# _seat.py unit behaviour
# ---------------------------------------------------------------------------


def _make_marker(home: Path) -> Path:
    marker = home / ".config" / "synthetic-enterprise" / ".env.ntfy"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("SE_NTFY_TOPIC=not-a-real-secret\n")
    return marker


class TestSeatModule:
    def test_marker_present_no_override_is_resident(self, tmp_path, monkeypatch):
        _make_marker(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("SE_SEAT", raising=False)
        assert _seat.is_resident_seat() is True

    def test_marker_absent_no_override_is_foreign(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))  # no marker created
        monkeypatch.delenv("SE_SEAT", raising=False)
        assert _seat.is_resident_seat() is False

    def test_override_foreign_wins_over_present_marker(self, tmp_path, monkeypatch):
        _make_marker(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("SE_SEAT", "foreign")
        assert _seat.is_resident_seat() is False

    def test_override_resident_wins_over_absent_marker(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))  # no marker
        monkeypatch.setenv("SE_SEAT", "resident")
        assert _seat.is_resident_seat() is True

    def test_unrecognised_override_falls_back_to_marker(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))  # no marker
        monkeypatch.setenv("SE_SEAT", "banana")
        assert _seat.is_resident_seat() is False
        _make_marker(tmp_path)
        assert _seat.is_resident_seat() is True

    def test_marker_path_tracks_home_at_call_time(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        assert _seat.resident_marker_path() == (
            tmp_path / ".config" / "synthetic-enterprise" / ".env.ntfy"
        )


# ---------------------------------------------------------------------------
# Subprocess-invoked guarded hooks (run exactly as Claude Code runs them)
# ---------------------------------------------------------------------------

BLOCK_CLAIM = HOOKS_DIR / "block_unevidenced_claim.py"
BLOCK_PIT = HOOKS_DIR / "block_point_in_time_read.py"
LANE_WALL = HOOKS_DIR / "lane_wall_hook.py"


def _run(script: Path, payload: dict, *, seat: str | None, tmp_home: Path,
         cwd: Path = REPO_ROOT, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a hook as a real subprocess with a controlled HOME (no resident
    marker) so the ONLY thing that can make it resident is SE_SEAT=resident."""
    env = {"HOME": str(tmp_home), "PATH": os.environ["PATH"]}
    if seat is not None:
        env["SE_SEAT"] = seat
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
    )


# A Bash payload that block_unevidenced_claim.py would BLOCK (an executed
# send_ntfy carrying a "fixed" claim with no verifiable commit SHA).
_CLAIM_PAYLOAD = {
    "tool_name": "Bash",
    "tool_input": {
        "command": (
            "python3 -c 'from background.ntfy_utils import send_ntfy; "
            "send_ntfy(\"fixed the dashboard, it is live now\")'"
        )
    },
}

# An Edit payload that block_point_in_time_read.py would FLAG (company-layer
# code taking a full historical dataset with no as_of/bisect bound).
_PIT_PAYLOAD = {
    "tool_name": "Edit",
    "tool_input": {
        "file_path": "company/pricing_engine.py",
        "new_string": "settled = run_settlement(all_records)\n",
    },
}

# A Read payload that lane_wall_hook.py would DENY under SE_LANE=supplier.
_LANE_PAYLOAD = {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}}


class TestBlockUnevidencedClaimGuard:
    def test_foreign_seat_is_inert(self, tmp_path):
        r = _run(BLOCK_CLAIM, _CLAIM_PAYLOAD, seat=None, tmp_home=tmp_path)
        assert r.returncode == 0
        assert r.stdout == ""
        assert r.stderr == ""

    def test_resident_seat_passes_through_and_blocks(self, tmp_path):
        r = _run(BLOCK_CLAIM, _CLAIM_PAYLOAD, seat="resident", tmp_home=tmp_path)
        assert r.returncode == 2
        assert "block_unevidenced_claim.py" in r.stderr


class TestBlockPointInTimeReadGuard:
    def test_foreign_seat_is_inert(self, tmp_path):
        r = _run(BLOCK_PIT, _PIT_PAYLOAD, seat=None, tmp_home=tmp_path)
        assert r.returncode == 0
        assert r.stdout == ""
        assert r.stderr == ""

    def test_resident_seat_passes_through_and_flags(self, tmp_path):
        r = _run(BLOCK_PIT, _PIT_PAYLOAD, seat="resident", tmp_home=tmp_path)
        assert r.returncode == 2
        assert "block_point_in_time_read.py" in r.stderr


class TestLaneWallGuard:
    def _denial_log(self, cwd: Path) -> Path:
        return cwd / "docs" / "observability" / "lane_hook_denials.jsonl"

    def test_foreign_seat_is_inert_and_writes_nothing(self, tmp_path):
        repo = tmp_path / "repo"
        home = tmp_path / "home"
        repo.mkdir()
        home.mkdir()
        r = _run(LANE_WALL, _LANE_PAYLOAD, seat=None, tmp_home=home, cwd=repo,
                 extra_env={"SE_LANE": "supplier"})
        assert r.returncode == 0
        assert r.stdout == ""
        assert r.stderr == ""
        assert not self._denial_log(repo).exists()

    def test_resident_seat_passes_through_and_denies(self, tmp_path):
        repo = tmp_path / "repo"
        home = tmp_path / "home"
        repo.mkdir()
        home.mkdir()
        r = _run(LANE_WALL, _LANE_PAYLOAD, seat="resident", tmp_home=home, cwd=repo,
                 extra_env={"SE_LANE": "supplier"})
        assert r.returncode == 2
        assert "lane_wall_hook.py" in r.stderr
        assert self._denial_log(repo).exists()  # proceeded past the guard


# ---------------------------------------------------------------------------
# In-process guarded hooks (side effect is a file/observability write that is
# cleanest to observe by importing the module and pointing it at a tmp target)
# ---------------------------------------------------------------------------


def _load_fresh(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, HOOKS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestStampHumanPresenceGuard:
    """The observed-live bug: a foreign session dirtied
    docs/observability/.human_last_input. Prove the guard stops the stamp."""

    def _setup(self, tmp_path, monkeypatch):
        mod = _load_fresh("stamp_seatguard", "stamp_human_presence.py")
        stamp = tmp_path / ".human_last_input"
        monkeypatch.setattr(mod, "_STAMP", stamp)
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"prompt": "a human line"})))
        return mod, stamp

    def test_foreign_seat_does_not_stamp(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("SE_SEAT", "foreign")
        mod, stamp = self._setup(tmp_path, monkeypatch)
        mod.main()
        assert not stamp.exists()
        out = capsys.readouterr()
        assert out.out == "" and out.err == ""

    def test_resident_seat_stamps(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SE_SEAT", "resident")
        mod, stamp = self._setup(tmp_path, monkeypatch)
        mod.main()
        assert stamp.exists()  # proceeded past the guard


class TestLogInstructionsLoadedGuard:
    def _setup(self, tmp_path, monkeypatch):
        mod = _load_fresh("logil_seatguard", "log_instructions_loaded.py")
        log = tmp_path / "instructions_loaded_log.jsonl"
        monkeypatch.setattr(mod, "LOG_PATH", log)
        # The hook also self-guards on PYTEST_CURRENT_TEST; drop it so the ONLY
        # thing keeping it inert in the foreign case is the seat guard.
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(
            {"load_reason": "path_glob_match", "file_path": "/x.md", "file_name": "x.md"})))
        return mod, log

    def test_foreign_seat_does_not_log(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SE_SEAT", "foreign")
        mod, log = self._setup(tmp_path, monkeypatch)
        assert mod.main() == 0
        assert not log.exists()

    def test_resident_seat_logs(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SE_SEAT", "resident")
        mod, log = self._setup(tmp_path, monkeypatch)
        assert mod.main() == 0
        assert log.exists()  # proceeded past the guard


class TestLogDirectorInputGuard:
    """Observed via a spy on the log sink -- the real sink pushes to the private
    ops repo, so we never let it run; we only assert whether the hook REACHED
    it."""

    def _setup(self, monkeypatch):
        mod = _load_fresh("logdi_seatguard", "log_director_input.py")
        calls = []
        monkeypatch.setattr(
            "background.director_input_log.classify_and_log_message",
            lambda *a, **k: calls.append(a),
        )
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(
            {"prompt": "hello there", "session_id": "abc"})))
        return mod, calls

    def test_foreign_seat_does_not_log(self, monkeypatch, capsys):
        monkeypatch.setenv("SE_SEAT", "foreign")
        mod, calls = self._setup(monkeypatch)
        assert mod.main() == 0
        assert calls == []
        out = capsys.readouterr()
        assert out.out == "" and out.err == ""

    def test_resident_seat_logs(self, monkeypatch):
        monkeypatch.setenv("SE_SEAT", "resident")
        mod, calls = self._setup(monkeypatch)
        assert mod.main() == 0
        assert calls  # proceeded past the guard and reached the sink


class TestPullNextWorkGuard:
    """THE dangerous hook: it must never draw work for a foreign session. The
    guard is the first act of main(); decide() is where the draw happens, so we
    prove decide() is never reached in a foreign seat."""

    def _setup(self, monkeypatch):
        mod = _load_fresh("pnw_seatguard", "pull_next_work.py")
        calls = []
        monkeypatch.setattr(mod, "decide", lambda payload: calls.append(payload) or None)
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": "x"})))
        return mod, calls

    def test_foreign_seat_never_draws(self, monkeypatch, capsys):
        monkeypatch.setenv("SE_SEAT", "foreign")
        mod, calls = self._setup(monkeypatch)
        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code == 0
        assert calls == []  # decide() (the draw) never reached
        out = capsys.readouterr()
        assert out.out == "" and out.err == ""

    def test_resident_seat_reaches_the_draw(self, monkeypatch):
        monkeypatch.setenv("SE_SEAT", "resident")
        mod, calls = self._setup(monkeypatch)
        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code == 0
        assert calls  # proceeded past the guard into decide()


# ---------------------------------------------------------------------------
# Structural lock: no future hook ships unguarded silently
# ---------------------------------------------------------------------------


class TestStructuralLock:
    def _hook_files(self) -> list[Path]:
        return sorted(
            p for p in HOOKS_DIR.glob("*.py")
            if p.name != "_seat.py" and not p.name.startswith("__")
        )

    def test_every_hook_is_guarded_or_explicitly_universal(self):
        offenders = []
        for p in self._hook_files():
            src = p.read_text()
            guarded = "is_resident_seat" in src
            if p.name in UNIVERSAL_HOOKS:
                # A universal hook must NOT be guarded (it runs in every seat).
                assert not guarded, f"{p.name} is on UNIVERSAL_HOOKS but imports the guard"
            elif not guarded:
                offenders.append(p.name)
        assert not offenders, (
            f"unguarded hooks not on UNIVERSAL_HOOKS: {offenders} -- add the seat "
            "guard (default) or justify adding them to UNIVERSAL_HOOKS in the PR"
        )

    def test_universal_allowlist_entries_exist(self):
        for name in UNIVERSAL_HOOKS:
            assert (HOOKS_DIR / name).is_file(), f"{name} on UNIVERSAL_HOOKS but not present"

    def test_there_is_at_least_one_guarded_hook(self):
        # Sanity: the lock is meaningless if nothing is guarded.
        guarded = [p.name for p in self._hook_files() if "is_resident_seat" in p.read_text()]
        assert len(guarded) >= 1
