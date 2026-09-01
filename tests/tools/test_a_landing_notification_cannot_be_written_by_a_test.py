"""A TEST MUST NOT BE ABLE TO WRITE THE DIRECTOR'S CHANNEL.

`ntfy_utils.send_ntfy` has had a hard pytest guard since 2026-07-16 (director: *"my phone is
spamming with test pages"*). The DEFERRAL path reaches neither that function nor its guard: a
deferrable `notify()` appends straight to the append-only digest queue and returns before any send
is attempted. That was harmless while nothing deferrable fired under test.

It stopped being harmless on 2026-09-01, when landings became notifications. `surgical_land` is the
one door every landing in this project goes through, and `tests/tools/test_surgical_land.py` lands
real commits into fixture repositories -- dozens of them, every run. Without a guard each one would
append a `[LANDED]` row to the LIVE queue and ride the next real digest to his phone, and the same
ledger would then be cited back as evidence of what the machine had done. That is the shape recorded
in `feedback_telemetry_a_test_can_write_is_not_telemetry`: a usage figure reported from a ledger
that was 23% pytest output.

THIS FILE LIVES IN `tests/tools/` ON PURPOSE. `tests/background/conftest.py` pins the queue at an
absent tmp path for its whole directory, so the guard is unreachable -- and therefore untestable --
from there. `tests/tools/` has no such conftest, which is exactly why the guard has to exist: it is
the directory where landings actually happen.
"""
from __future__ import annotations

import inspect

from background import notification_digest as nd
from tools import surgical_land


def test_an_unredirected_queue_is_a_no_op_under_pytest():
    """MUTATION: delete the PYTEST_CURRENT_TEST guard in `defer()` and this fails -- and the real
    queue gains a row from a test, which is the defect."""
    before = nd._DEFAULT_QUEUE_FILE.read_text() if nd._DEFAULT_QUEUE_FILE.exists() else ""
    assert nd.QUEUE_FILE == nd._DEFAULT_QUEUE_FILE, (
        "this test is only meaningful where the queue has NOT been redirected; if a conftest "
        "starts pinning it for tests/tools/ then the guard has become unreachable here and this "
        "file must move to a directory where it is not"
    )
    result = nd.defer("a landing written by a test", kind="work_done",
                      topic_class=nd.ROUTINE_LANDING)
    assert result == "deferred:pytest-suppressed"
    after = nd._DEFAULT_QUEUE_FILE.read_text() if nd._DEFAULT_QUEUE_FILE.exists() else ""
    assert after == before
    assert "a landing written by a test" not in after


def test_a_redirected_queue_still_exercises_the_real_body(monkeypatch, tmp_path):
    """Both directions (R15). Blanket-guarding on PYTEST_CURRENT_TEST alone would make the deferral
    mechanism unfalsifiable, which is the very defect the guard is written to fix -- so a test that
    redirects the path gets the real append."""
    monkeypatch.setattr(nd, "QUEUE_FILE", tmp_path / "q.jsonl")
    assert nd.defer("real body", kind="work_done", topic_class=nd.ROUTINE_LANDING) == "deferred:1"
    assert "real body" in (tmp_path / "q.jsonl").read_text()


def test_a_landing_announcement_can_never_fail_a_landing():
    """The commit already exists when this runs. A notifier that can raise into the landing path
    would turn a successful, gated commit into a caller-visible failure -- an observer that can fail
    the thing it observes is itself a defect."""
    def _boom(*a, **kw):
        raise RuntimeError("the channel is down")

    assert surgical_land.announce_landing("abc123", "x", ["a.py"], _notify=_boom) is None
    assert "except Exception" in inspect.getsource(surgical_land.announce_landing)


# ── THE PRODUCER MUST BE ABLE TO PRODUCE, AND MUST SAY SO WHEN IT CANNOT ─────────────────────
def test_the_announcer_works_without_a_daemons_environment(monkeypatch, tmp_path):
    """SHIPPED BROKEN AND CAUGHT WITHIN MINUTES (2026-09-01). `background/ntfy_utils` raises at
    IMPORT time when `SE_NTFY_TOPIC` is unset — deliberately, so a daemon dies at start rather than
    finding its only channel dead when it needs it. Nobody had met the consequence until landings
    became notifications: `background.notify` is not importable outside a daemon's environment, and
    that includes a DEFERRED notification which never touches the wire at all.

    This tool is run BY HAND, by every lane, from shells that never sourced `start_worker.sh`. So
    the commit that added the producer landed and announced nothing.

    IN A SUBPROCESS, and that is not fussiness. The first draft used `monkeypatch.delenv` and the
    mutation SURVIVED: `background.ntfy_utils` was already in `sys.modules` from this file's own
    imports, so the raise this test exists to provoke could not happen. A control that cannot fail
    is worse than none, and it took removing the fix and watching the test stay green to see it.
    Only a FRESH interpreter, with the variable genuinely absent, reproduces a lane's bare shell.

    MUTATION: remove the `load_secret_env()` call from `announce_landing` and this fails.
    """
    import os
    import subprocess
    import sys

    queue = tmp_path / "q.jsonl"
    probe = (
        "import sys\n"
        "from background import notification_digest as nd\n"
        f"nd.QUEUE_FILE = __import__('pathlib').Path({str(queue)!r})\n"
        "from tools import surgical_land as sl\n"
        "r = sl.announce_landing('abc123def', 'a landing from a bare shell', ['a.py'])\n"
        "print(r)\n"
    )
    env = {k: v for k, v in os.environ.items() if k != "SE_NTFY_TOPIC"}
    env.pop("PYTEST_CURRENT_TEST", None)   # a fresh process is not inside this test
    proc = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                          cwd=str(surgical_land.ROOT), env=env, timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert "SE_NTFY_TOPIC is not set" not in proc.stderr, proc.stderr
    assert "could NOT announce" not in proc.stderr, proc.stderr
    assert proc.stdout.strip().startswith("deferred:"), (proc.stdout, proc.stderr)
    assert "a landing from a bare shell" in queue.read_text()


def test_the_announcer_never_takes_the_signing_key_with_it():
    """The topic and nothing else. Reading `.env.ntfy` wholesale also loads `SE_WAKE_HMAC_KEY`, the
    authority-signing key `MODEL_FACING_FORBIDDEN_SECRETS` exists to keep out of processes like this
    one — a helper that hands out more authority than its caller asked for is a worse defect than
    the silence it was written to fix.

    Both legs: the default asks for the topic only, AND the forbidden set is refused even when a
    caller explicitly asks for it."""
    from background import secrets_location as sl
    env = {}
    sl.load_secret_env(environ=env)
    assert set(env) <= {"SE_NTFY_TOPIC"}, env.keys()
    env2 = {}
    sl.load_secret_env(only=tuple(sl.MODEL_FACING_FORBIDDEN_SECRETS), environ=env2)
    assert env2 == {}, "the forbidden set is the floor and outranks any caller's `only`"


def test_an_unannounceable_landing_says_so_on_stderr(capsys):
    """A notifier that cannot fail a landing must still not fail SILENTLY — that combination is
    exactly what shipped this evening, and it is the shape the producer exists to report."""
    def _boom(*a, **kw):
        raise RuntimeError("the channel is down")

    assert surgical_land.announce_landing("abc123", "x", ["a.py"], _notify=_boom) is None
    err = capsys.readouterr().err
    assert "could NOT announce" in err and "abc123" in err
