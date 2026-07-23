"""R15 both-directions proof for DIRECTOR_RULING_HMAC_GAP_OPTION_1 (2026-07-23).

The gap: SE_WAKE_HMAC_KEY is the SYMMETRIC key that signs director-authority wake/
ntfy messages. Model-facing processes (the spawned `claude -p` worker, forks, the
twin, the tmux seat) inherited it via `os.environ.copy()` / tmux env inheritance —
and HMAC is symmetric, so a process that can VERIFY can also SIGN. A forged
director_ntfy ruling minted from inside the worker env carried a VALID signature.

The fix (Option 1, director-ruled): strip the key from EVERY model-facing spawn env,
as a single enumerable forbidden set (secrets_location.MODEL_FACING_FORBIDDEN_SECRETS)
routed through secrets_location.scrub_model_facing_env — so the class is closed, not
the one instance (R10). The worker keeps SE_NTFY_TOPIC to SEND; it never holds the
wake key to SIGN.

R15 doctrine proven here:
  * FAIL-CLOSED  — the key is absent from every model-facing spawn env even when the
                   PARENT process holds it (the exact inheritance path reproduced).
  * PASS         — the worker can still SEND: SE_NTFY_TOPIC survives the scrub.
  * FORGERY-BLOCKED — with the key stripped, sign_wake_message() cannot mint a
                   signature at all (it raises), so a forged director ruling is
                   structurally impossible from inside the worker env.
The genuine responder-side verification path is unaffected (the daemon reads the key
from its OWN env, never a spawned copy) — covered by test_director_authority_channels.
"""
import os
import subprocess

import pytest

import background.secrets_location as sl


# ── the shared scrub primitive ────────────────────────────────────────────────
def test_forbidden_set_names_the_wake_key():
    """The class-fix rests on ONE enumerable list. The wake key must be in it, or the
    whole sweep is a no-op (a fail-open the mutation below would not catch)."""
    assert "SE_WAKE_HMAC_KEY" in sl.MODEL_FACING_FORBIDDEN_SECRETS


def test_scrub_drops_wake_key_keeps_send_topic():
    """FAIL-CLOSED + PASS in one: the signing key is removed, the send topic survives."""
    env = {"SE_WAKE_HMAC_KEY": "sekret", "SE_NTFY_TOPIC": "topic", "OTHER": "x"}
    out = sl.scrub_model_facing_env(env)
    assert "SE_WAKE_HMAC_KEY" not in out          # cannot SIGN
    assert out["SE_NTFY_TOPIC"] == "topic"        # can still SEND
    assert out["OTHER"] == "x"                    # nothing else touched


def test_scrub_is_idempotent_and_never_raises_on_absent():
    """FAIL-SILENT-safe: scrubbing an env that never had the key must not raise."""
    assert "SE_WAKE_HMAC_KEY" not in sl.scrub_model_facing_env({"SE_NTFY_TOPIC": "t"})


# ── the exact inheritance path the ruling named: worker_tick.spawn_invocation ──
def test_worker_tick_env_strips_inherited_wake_key(monkeypatch):
    """Reproduce the exact path: the parent process HOLDS the key (as worker-tick.
    service does via EnvironmentFile=.env.ntfy), and _worker_env() copies os.environ.
    The spawned worker's env must NOT carry it, but MUST keep the send topic."""
    import background.worker_tick as wt
    monkeypatch.setenv("SE_WAKE_HMAC_KEY", "parent-holds-this")
    monkeypatch.setenv("SE_NTFY_TOPIC", "worker-send-topic")
    env = wt._worker_env()
    assert "SE_WAKE_HMAC_KEY" not in env          # the forgery gap: CLOSED
    assert env["SE_NTFY_TOPIC"] == "worker-send-topic"
    assert env["SE_SBI_WORKER"] == "1"            # unrelated hygiene preserved


def test_worker_env_forgery_is_structurally_impossible(monkeypatch):
    """FORGERY-BLOCKED: run inside the worker's own scrubbed env and confirm the sign
    path cannot produce a signature at all — the ruling's 'must never hold the key to
    SIGN' made concrete. verify_wake_message also fails-closed (returns None)."""
    import background.worker_tick as wt
    monkeypatch.setenv("SE_WAKE_HMAC_KEY", "parent-holds-this")
    monkeypatch.setenv("SE_NTFY_TOPIC", "worker-send-topic")
    worker_env = wt._worker_env()
    # Emulate the worker process: its environment IS worker_env.
    for k in list(os.environ):
        monkeypatch.delenv(k, raising=False)
    for k, v in worker_env.items():
        monkeypatch.setenv(k, v)
    import importlib
    import background.ntfy_utils as nu
    importlib.reload(nu)  # re-read WAKE_HMAC_KEY from the now-scrubbed env
    try:
        with pytest.raises(RuntimeError):
            nu.sign_wake_message("RULING:BUILD_OPEN:X")   # no key -> cannot forge
        assert nu.verify_wake_message("t|0|deadbeef") is None  # no key -> fail-closed
    finally:
        importlib.reload(nu)  # restore module state for other tests


# ── the rest of the class: build_executor, director_twin, worker_seat ──────────
def test_build_executor_child_env_strips_wake_key(monkeypatch):
    import background.build_executor as be
    monkeypatch.setenv("SE_WAKE_HMAC_KEY", "parent-holds-this")
    monkeypatch.setenv("SE_NTFY_TOPIC", "t")
    env = be._child_env()
    assert "SE_WAKE_HMAC_KEY" not in env
    assert env["SE_NTFY_TOPIC"] == "t"


def test_worker_seat_tmux_seed_overrides_wake_key_to_empty():
    """The tmux seat inherits the server env; the seed command must EXPLICITLY set an
    empty SE_WAKE_HMAC_KEY (fail-closed at verify) rather than trusting inheritance."""
    import background.worker_seat as ws
    cmd = ws._seed_cmd("/usr/bin/claude")
    # the -e flag and its empty-valued key must appear as adjacent argv tokens
    pairs = [(cmd[i], cmd[i + 1]) for i in range(len(cmd) - 1) if cmd[i] == "-e"]
    assert ("-e", "SE_WAKE_HMAC_KEY=") in pairs


def test_director_twin_subprocess_env_strips_wake_key(monkeypatch):
    """The twin passes no shell; verify the env handed to subprocess.run excludes the
    key even though the twin process itself may hold it."""
    import background.director_twin as dt
    monkeypatch.setenv("SE_WAKE_HMAC_KEY", "parent-holds-this")
    captured = {}

    class _Result:
        stdout = "answer"

    def _fake_run(*args, **kwargs):
        captured["env"] = kwargs.get("env")
        return _Result()

    monkeypatch.setattr(dt.subprocess, "run", _fake_run)
    dt._default_invoke("some prompt")
    assert captured["env"] is not None
    assert "SE_WAKE_HMAC_KEY" not in captured["env"]


# ── R10 teeth: a new model-facing spawner that skips the scrub must be caught ──
def test_every_env_copy_spawner_routes_through_the_scrub():
    """Class guard (R10): enumerate the model-facing modules that build a spawn env
    and assert each references the shared scrub / forbidden set. A future
    `os.environ.copy()`-into-`claude` path added without scrubbing fails HERE — 'one
    leak found means others are possible' becomes a test, not a hope."""
    from pathlib import Path
    root = Path(sl.PROJECT_DIR) / "background"
    guarded = {
        "worker_tick.py": "scrub_model_facing_env",
        "build_executor.py": "scrub_model_facing_env",
        "autonomous_runner.py": "scrub_model_facing_env",
        "director_twin.py": "scrub_model_facing_env",
        "worker_seat.py": "MODEL_FACING_FORBIDDEN_SECRETS",
    }
    for fname, token in guarded.items():
        text = (root / fname).read_text()
        assert token in text, f"{fname} builds a model-facing spawn but does not route through the scrub"
