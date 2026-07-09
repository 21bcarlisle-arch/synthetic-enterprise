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
    """Append `msg_id` to SENT_IDS_FILE, keeping at most MAX_SENT_IDS entries."""
    ids: list[str] = []
    if SENT_IDS_FILE.is_file():
        try:
            ids = json.loads(SENT_IDS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ids = []
    ids.append(msg_id)
    ids = ids[-MAX_SENT_IDS:]
    SENT_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SENT_IDS_FILE.write_text(json.dumps(ids), encoding="utf-8")


def was_sent_by_us(msg_id: str | None) -> bool:
    """True if `msg_id` was recorded by a prior `send_ntfy()` call."""
    if not msg_id or not SENT_IDS_FILE.is_file():
        return False
    try:
        ids = json.loads(SENT_IDS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return msg_id in ids


def send_ntfy(message: str, headers: dict[str, str] | None = None) -> str | None:
    """POST `message` to the shared ntfy topic, record its id (so the
    inbound-command poller can recognise and skip it), mirror it
    (secret-scrubbed) for the advisor (ADVISOR_VISIBILITY.md), and return
    the id (or None if the request or id-parsing failed)."""
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

    return msg_id
