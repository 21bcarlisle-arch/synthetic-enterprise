"""Shared ntfy.sh helpers for background processes.

See docs/instructions/NTFY_TWO_WAY_PROTOCOL.md. `session_watchdog.py` polls
the shared NTFY topic for short steering messages Rich sends from the ntfy
app on his phone (Two-Way NTFY Command Channel). To avoid treating our own
outgoing notifications as incoming commands (a feedback loop), every message
sent via `send_ntfy()` has its ntfy-assigned id recorded in `SENT_IDS_FILE`;
`was_sent_by_us()` checks an incoming message's id against that record.

Topic rotation (2026-07-08, docs/staging/NTFY_CHANNEL_HARDENING.md): the
topic name is a secret, no longer committed to git. It is loaded ONLY from
the environment (SE_NTFY_TOPIC), sourced from the gitignored
background/.env.ntfy file — see background/start_worker.sh's env-loading
block. This module raises loudly at import time if the variable is unset
rather than falling back to any default, so a mis-launched process cannot
silently talk over a stale/exposed topic.

Auth: if the topic is reserved/protected, set NTFY_AUTH_TOKEN=t_... in the
environment. Both publish and subscribe calls will include
`Authorization: Bearer <token>`. Without the env var the scripts fall back to
unauthenticated access (public topics only).

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import fcntl
import hashlib
import hmac
import json
import os
import subprocess
import time
from pathlib import Path

NTFY_TOPIC: str | None = os.environ.get("SE_NTFY_TOPIC")
if not NTFY_TOPIC:
    raise RuntimeError(
        "SE_NTFY_TOPIC is not set. Load background/.env.ntfy before "
        "starting this process (see background/start_worker.sh) -- there is "
        "no committed default topic any more (2026-07-08 rotation, "
        "docs/staging/NTFY_CHANNEL_HARDENING.md)."
    )
NTFY_PUBLISH_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
NTFY_AUTH_TOKEN: str | None = os.environ.get("NTFY_AUTH_TOKEN")
WAKE_HMAC_KEY: str | None = os.environ.get("SE_WAKE_HMAC_KEY")

SENT_IDS_FILE = Path("/home/rich/synthetic-enterprise/docs/observability/.sent_ntfy_ids.json")
MAX_SENT_IDS = 500


def sign_wake_message(text: str, timestamp: int | None = None) -> str:
    """Build a 'text|timestamp|hexhmac' payload for a tmux-relayed wake
    message, signed with SE_WAKE_HMAC_KEY. Raises if the key isn't loaded --
    an unsigned wake message must never be sent silently."""
    if not WAKE_HMAC_KEY:
        raise RuntimeError(
            "SE_WAKE_HMAC_KEY is not set -- cannot sign a wake message. "
            "Load background/.env.ntfy first."
        )
    ts = timestamp if timestamp is not None else int(time.time())
    payload = f"{text}|{ts}"
    digest = hmac.new(WAKE_HMAC_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}|{digest}"


def verify_wake_message(signed: str, max_age_seconds: int = 300) -> str | None:
    """Verify a 'text|timestamp|hexhmac' payload produced by
    `sign_wake_message`. Returns the original text if the signature is valid
    and not stale, otherwise None -- callers must treat None as untrusted
    input (log it, do not act on it as a real wake)."""
    if not WAKE_HMAC_KEY:
        return None
    try:
        text, ts_str, digest = signed.rsplit("|", 2)
        ts = int(ts_str)
    except ValueError:
        return None
    expected = hmac.new(
        WAKE_HMAC_KEY.encode(), f"{text}|{ts}".encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, digest):
        return None
    if abs(time.time() - ts) > max_age_seconds:
        return None
    return text


def record_sent_id(msg_id: str) -> None:
    """Append `msg_id` to SENT_IDS_FILE (keeping at most MAX_SENT_IDS), under
    an exclusive file lock so concurrent daemon sends cannot LOSE an id via a
    read-modify-write race.

    A lost id is exactly the echo-loop defect this file exists to prevent
    (2026-07-15, inbound_tagging_and_rate_guard): multiple daemons
    (health_check, action_needed, session_watchdog, the responder's own
    replies) can call send_ntfy concurrently on this one shared tree; the
    previous unlocked read-append-write meant two overlapping senders each read
    the same list, appended their own id, and the last writer clobbered the
    other's id. An unrecorded id makes was_sent_by_us() return False for our
    OWN outbound, so ntfy_responder captures it as INBOUND and stages a bogus
    from_rich -- which was observed live for our own [ACTION NEEDED] and
    [HEALTH CHECK] sends. The flock serialises the whole read-modify-write; the
    write is atomic (tmp + os.replace) so a concurrent was_sent_by_us() reader
    never sees a truncated/partial file."""
    SENT_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock_path = SENT_IDS_FILE.with_name(SENT_IDS_FILE.name + ".lock")
    with open(lock_path, "w") as lock_f:
        fcntl.flock(lock_f, fcntl.LOCK_EX)
        try:
            ids: list[str] = []
            if SENT_IDS_FILE.is_file():
                try:
                    ids = json.loads(SENT_IDS_FILE.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    ids = []
            ids.append(msg_id)
            ids = ids[-MAX_SENT_IDS:]
            tmp_path = SENT_IDS_FILE.with_name(SENT_IDS_FILE.name + ".tmp")
            tmp_path.write_text(json.dumps(ids), encoding="utf-8")
            os.replace(tmp_path, SENT_IDS_FILE)
        finally:
            fcntl.flock(lock_f, fcntl.LOCK_UN)


def was_sent_by_us(msg_id: str | None) -> bool:
    """True if `msg_id` was recorded by a prior `send_ntfy()` call."""
    if not msg_id or not SENT_IDS_FILE.is_file():
        return False
    try:
        ids = json.loads(SENT_IDS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return msg_id in ids


def send_ntfy(message: str, headers: dict[str, str] | None = None,
              *, _allow_real_send: bool = False) -> str | None:
    """POST `message` to the shared ntfy topic, record its id (so the
    inbound-command poller can recognise and skip it), mirror it
    (secret-scrubbed) for the advisor (ADVISOR_VISIBILITY.md), and return
    the id (or None if the request or id-parsing failed)."""
    # HARD PYTEST GUARD (2026-07-16, director: "my phone is spamming with test
    # messages"). NEVER POST a real NTFY from inside a test run. A test that
    # exercises any notification path WITHOUT mocking send_ntfy would otherwise
    # buzz the director's PHONE with synthetic content ("fake reason", "atom X") --
    # and EVERY process that runs the suite (the publish gate each cycle, an
    # auto-resumed session's recovery checklist, an interactive `pytest` run) did
    # exactly that. pytest sets PYTEST_CURRENT_TEST for the duration of every test;
    # this makes a real send STRUCTURALLY IMPOSSIBLE there, independent of whether
    # each individual test remembers to mock (MAKE_IT_STICK: mechanism, not
    # discipline). This is the ONE fix for the whole test-spam class; a test that
    # needs to assert on a send mocks send_ntfy (replacing this function) as before.
    import os
    if os.environ.get("PYTEST_CURRENT_TEST") and not _allow_real_send:
        # A test that genuinely exercises the POST/parse internals (with curl mocked)
        # passes _allow_real_send=True; everything else is suppressed so no test can
        # buzz the director's phone by forgetting to mock.
        return "pytest-suppressed"  # sentinel: a real POST never happens under pytest
    cmd = ["curl", "-s"]
    if NTFY_AUTH_TOKEN:
        cmd += ["-H", f"Authorization: Bearer {NTFY_AUTH_TOKEN}"]
    for key, value in (headers or {}).items():
        cmd += ["-H", f"{key}: {value}"]
    cmd += ["-d", message, NTFY_PUBLISH_URL]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        msg_id = json.loads(result.stdout).get("id")
    except json.JSONDecodeError:
        msg_id = None

    if msg_id:
        record_sent_id(msg_id)

    try:
        from background.ntfy_mirror import append_mirror_entry
        append_mirror_entry("out", message, topic=NTFY_TOPIC)
    except Exception:
        pass  # mirroring must never block or break a real send

    try:
        from background.director_input_log import append_entry
        append_entry("ntfy", message, direction="out", hmac_verified=None)
    except Exception:
        pass  # logging must never block or break a real send

    return msg_id
