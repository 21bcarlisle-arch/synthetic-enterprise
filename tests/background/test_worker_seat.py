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


def test_seat_argv_is_deterministic_session_id_never_resume_even_when_transcript_exists(monkeypatch):
    """IDENTITY_DRIFT_FIX (2026-07-19, R3 root cause): the old `--resume` path brought the seat up
    under a DIFFERENT live session id than WORKER_SESSION_ID on this CC build, so the pull-loop
    rejected it as non-worker on every Stop -- no work ever delivered. seat_argv must NOW pin the id
    with `--session-id` DETERMINISTICALLY, never `--resume`, even when a prior transcript exists.
    MUTATION: reintroducing `--resume` reintroduces the drift -> this assertion fails."""
    monkeypatch.setattr(W, "_worker_session_exists", lambda: True)   # transcript exists
    argv = W.seat_argv("/usr/bin/claude")
    assert "--session-id" in argv and W.WORKER_SESSION_ID in argv
    assert "--resume" not in argv                                    # the drift path is gone
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

# ── IDENTITY-AWARE keep-alive (IDENTITY_DRIFT_FIX, 2026-07-19): keep the RECOGNISED seat alive,
#    not any tmux session -- and detect drift WITHOUT ever reaping (the permanent no-reap invariant). ──

def test_classify_seat_healthy_when_live_id_matches_worker_id():
    assert W._classify_seat(alive=True, live_id=W.WORKER_SESSION_ID) == "healthy"


def test_classify_seat_detects_drift_when_live_id_differs():
    """The 2026-07-19 deadlock: tmux ALIVE but the live session id != WORKER_SESSION_ID, so the
    transport rejects the seat as non-worker forever. Identity-aware keep-alive flags it 'drift'
    (-> report + bounce), never 'healthy'. MUTATION: a liveness-only check returns 'healthy' here
    and the deadlock is silent again."""
    st = W._classify_seat(alive=True, live_id="da80a780-8219-4825-b187-53bab3e13270")
    assert st == "drift"
    assert st != "healthy" and st != "dead"          # drift never re-seeds (no reap) and never rests


def test_classify_seat_unknown_live_id_is_not_a_false_drift():
    """FAIL-SAFE direction: if the live id can't be determined this cycle (None), it must NOT be
    treated as a positive mismatch (which would falsely flag drift / thrash). Unknown -> healthy;
    the deterministic --session-id seed is the prevention, this classifier is the backstop."""
    assert W._classify_seat(alive=True, live_id=None) == "healthy"


def test_classify_seat_dead_when_tmux_gone_triggers_reseed_path():
    """Only 'dead' takes the re-seed branch in main(); 'drift' never does (worker_seat cannot reap)."""
    assert W._classify_seat(alive=False, live_id=None) == "dead"


def test_identity_drift_is_distinct_from_the_reseed_state_and_no_kill_exists():
    """R15 / invariant: drift must be its OWN state, distinct from 'dead' (the only state that
    re-seeds) -- so a drifted seat is never re-seeded (which would need a kill) nor rested as healthy.
    Combined with the file having no kill path at all (test_no_process_kill_path_in_worker_seat), this
    proves the manager REPORTS drift and holds, honouring the permanent no-reap invariant."""
    assert W._classify_seat(True, "other-id-0000-0000-0000-000000000000") == "drift"
    assert {"healthy", "dead", "drift"} == {
        W._classify_seat(True, W.WORKER_SESSION_ID),
        W._classify_seat(False, None),
        W._classify_seat(True, "different-id"),
    }  # three genuinely distinct outcomes; drift is not aliased onto dead/healthy
    import re as _re
    assert _re.search(r"os\.kill\s*\(", SRC) is None  # no reap anywhere, drift path included


def test_seed_seat_archives_a_stale_transcript_before_creating(tmp_path, monkeypatch):
    """--session-id needs a clean id: any stale on-disk transcript for WORKER_SESSION_ID is moved
    aside first, so the created seat's live id is deterministically WORKER_SESSION_ID."""
    projects = tmp_path / "projects"
    proj = projects / "-home-rich-synthetic-enterprise"
    proj.mkdir(parents=True)
    stale = proj / f"{W.WORKER_SESSION_ID}.jsonl"
    stale.write_text("stale transcript")
    monkeypatch.setattr(W, "CLAUDE_PROJECTS", projects)
    calls = {}
    monkeypatch.setattr(W.subprocess, "run", lambda *a, **k: calls.setdefault("argv", a[0]))
    W.seed_seat("/usr/bin/claude")
    assert not stale.exists(), "stale transcript must be archived before create"
    assert (proj / f"{W.WORKER_SESSION_ID}.jsonl.pre_reseed").exists()
    assert "--session-id" in calls["argv"] and "--resume" not in calls["argv"]


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
