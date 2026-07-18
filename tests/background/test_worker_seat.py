"""OPS1 sub-step 4: the worker-seat manager is the ONE bespoke process, and it stays THIN.

The mutation/thinness invariants here are what stop accretion restarting in this one file
(SUBSTEP4 §3). Its entire job is seed-by-id + keep-alive + report; anything else — reaping,
auto-advance, notification machinery — is forbidden, permanently, and tested."""
from __future__ import annotations

from pathlib import Path

from background import worker_seat as W

SRC = Path(W.__file__).read_text()


# ── seeding contract: dedicated session id, NEVER `claude -c` ──

def test_seat_argv_creates_with_session_id_when_no_prior_session(monkeypatch):
    monkeypatch.setattr(W, "_worker_session_exists", lambda: False)
    argv = W.seat_argv("/usr/bin/claude")
    assert "--session-id" in argv
    assert W.WORKER_SESSION_ID in argv
    assert "-c" not in argv and "--continue" not in argv          # never continue-most-recent


def test_seat_argv_resumes_the_same_id_when_it_exists(monkeypatch):
    monkeypatch.setattr(W, "_worker_session_exists", lambda: True)
    argv = W.seat_argv("/usr/bin/claude")
    assert "--resume" in argv
    assert W.WORKER_SESSION_ID in argv
    assert "-c" not in argv and "--continue" not in argv


def test_seat_argv_always_carries_the_bring_up_seed_not_an_advance_prompt(monkeypatch):
    monkeypatch.setattr(W, "_worker_session_exists", lambda: False)
    argv = W.seat_argv("/usr/bin/claude")
    assert W.SEED_PROMPT in argv


# ── G-R4: the seed brings-up-and-reports, then STOPS. It must NOT auto-advance. ──

def test_seed_prompt_forbids_self_advance():
    p = W.SEED_PROMPT.lower()
    assert "do not draw" in p or "does not self-advance" in p or "wait for" in p
    # the retired watchdog seed's auto-advance step must not reappear here
    assert "advance the project" not in p


# ── thinness: no reaping, no kill path, no notification machinery in this file ──

def test_no_process_kill_path_in_worker_seat():
    import re
    assert re.search(r"os\.kill\s*\(", SRC) is None
    assert "signal.SIGTERM" not in SRC and "signal.SIGKILL" not in SRC
    assert "pkill" not in SRC.replace("os.kill, signal, pkill", "")  # the docstring mention is allowed
    assert "def reap" not in SRC


def test_no_ntfy_machinery_in_worker_seat():
    """Alarming is the reconciler's job (G-N contract), not the seat manager's — it only writes
    a status line. No ntfy import/call may live here."""
    assert "send_ntfy" not in SRC
    assert "ntfy_utils" not in SRC


def test_reseed_is_bounded_not_an_infinite_loop():
    """Keep-alive re-seeds are bounded (the file-api 32,707 lesson applied to the seat): N
    re-seeds in a window -> hold + report, never an infinite silent respawn."""
    assert W.MAX_RESEEDS >= 1
    assert W.RESEED_WINDOW_SECONDS > 0
    assert "reseeds" in SRC  # the bound is actually implemented, not just declared


def test_report_writes_a_status_line_only(tmp_path, monkeypatch):
    monkeypatch.setattr(W, "STATUS_FILE", tmp_path / ".worker_seat_status")
    W._report("hello")
    assert (tmp_path / ".worker_seat_status").read_text().strip() == "hello"


def test_resolve_claude_falls_back_to_nvm_when_not_on_PATH(monkeypatch):
    """A systemd --user service has a bare (non-login) PATH with no nvm bin dir, so `which`
    returns None -- the seat must still find the absolute nvm binary or it can never seed under
    systemd. Mirrors session_watchdog's resolver."""
    import shutil
    import glob
    monkeypatch.setattr(shutil, "which", lambda _c: None)   # not on PATH (the systemd case)
    monkeypatch.setattr(glob, "glob", lambda pat: [
        "/home/rich/.nvm/versions/node/v20.0.0/bin/claude",
        "/home/rich/.nvm/versions/node/v22.1.0/bin/claude",
    ])
    assert W._resolve_claude() == "/home/rich/.nvm/versions/node/v22.1.0/bin/claude"  # highest version


def test_resolve_claude_prefers_PATH_when_present(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda _c: "/usr/local/bin/claude")
    assert W._resolve_claude() == "/usr/local/bin/claude"

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
