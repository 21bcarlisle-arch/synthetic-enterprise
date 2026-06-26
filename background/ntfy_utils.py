"""Shared ntfy.sh helpers for background processes.

See docs/instructions/NTFY_TWO_WAY_PROTOCOL.md. `session_watchdog.py` polls
the `skynet-synthetic` topic for short steering messages Rich sends from the
ntfy app on his phone (Two-Way NTFY Command Channel). To avoid treating our
own outgoing notifications as incoming commands (a feedback loop), every
message sent via `send_ntfy()` has its ntfy-assigned id recorded in
`SENT_IDS_FILE`; `was_sent_by_us()` checks an incoming message's id against
that record.

Auth: if the `skynet-synthetic` topic is reserved/protected, set
NTFY_AUTH_TOKEN=t_... in the environment. Both publish and subscribe calls
will include `Authorization: Bearer <token>`. Without the env var the scripts
fall back to unauthenticated access (public topics only).

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import json
import os
import subprocess
from pathlib import Path

NTFY_TOPIC = "skynet-synthetic"
NTFY_PUBLISH_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
NTFY_AUTH_TOKEN: str | None = os.environ.get("NTFY_AUTH_TOKEN")

SENT_IDS_FILE = Path("/home/rich/synthetic-enterprise/docs/observability/.sent_ntfy_ids.json")
MAX_SENT_IDS = 500


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
    inbound-command poller can recognise and skip it), and return the id (or
    None if the request or id-parsing failed)."""
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
    return msg_id
