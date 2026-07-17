"""Director per-page comments -- DIRECTOR_COMMENTS_BOX.md.

Every site page carries a small feedback affordance (site/*/index.html's
shared `director-comments.js` widget). The director's only route to leave a
comment "with zero friction" from a PUBLIC static site (GitHub Pages, no
backend) is a message bus -- so the widget POSTs directly to a dedicated,
comments-only ntfy.sh topic (SE_COMMENTS_TOPIC), distinct from the main
two-way SE_NTFY_TOPIC channel used for everything else in this project.

Hard authentication (non-negotiable, per the staged doc): the topic name
itself is necessarily embedded in public JS (an anonymous browser has to
know where to POST), so it provides zero protection on its own -- anyone
reading page source can find it. The real check is the PIN
(SE_COMMENTS_PIN) the director enters once client-side (stored in
localStorage from then on, never in any tracked file) and this daemon
validates SERVER-SIDE before a submission is ever staged. A message with a
missing/wrong PIN is discarded here -- logged, never written to
docs/staging/, per the doc's "rejected before entering any queue."

Honest residual limitation (no free message bus offers real per-sender
auth): if someone both (a) reads the public page source to find the
comments topic AND (b) separately subscribes to that topic to snoop
traffic, they could in principle capture a legitimate PIN from a real
submission in transit and replay it later. This is the same trust model
already accepted for the main SE_NTFY_TOPIC (secrecy of an unguessable
random string, not cryptographic sender auth) -- the difference here is
the topic itself is not secret, only the PIN is. The blast radius is
bounded regardless: per R7/R8, a comment is DATA with ZERO authority, it
only ever surfaces for human triage like any from_rich message -- a forged
comment is queue noise, never an executed action.

Single responsibility, own polling loop, own watermark file -- does not
share state with ntfy_responder.py (a different daemon, a different
topic, deliberately not merged into it, matching the "one dumb loop, one
job" lesson from THE SUPERVISOR rebuild rather than growing another
multi-responsibility daemon).
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background.notify import notify  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "director-comments-log.md"
STATE_FILE = PROJECT_DIR / "background" / ".director_comments_since.json"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

POLL_INTERVAL_SECONDS = 20

COMMENTS_TOPIC: Optional[str] = os.environ.get("SE_COMMENTS_TOPIC")
COMMENTS_PIN: Optional[str] = os.environ.get("SE_COMMENTS_PIN")


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _load_since() -> float:
    if STATE_FILE.is_file():
        try:
            return json.loads(STATE_FILE.read_text()).get("since", 0.0)
        except (json.JSONDecodeError, OSError):
            return 0.0
    return 0.0


def _save_since(since: float) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"since": since}))


def parse_comment_submission(message: str) -> Optional[dict]:
    """Expected format (see site/*/index.html's director-comments.js):
        PIN:<pin>
        PAGE:<path>
        STATE:<short visible-state description>
        DATA_TS:<data generated_at / commit, if available>
        ---
        <comment text>
    Returns None if the PIN is missing/wrong or the format doesn't parse --
    the caller must never stage a None result."""
    if not COMMENTS_PIN:
        return None
    if "---" not in message:
        return None
    header, _, body = message.partition("---")
    fields: dict[str, str] = {}
    for line in header.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip().upper()] = value.strip()

    if fields.get("PIN") != COMMENTS_PIN:
        return None

    return {
        "page": fields.get("PAGE", "(unknown page)"),
        "state": fields.get("STATE", ""),
        "data_ts": fields.get("DATA_TS", ""),
        "comment": body.strip(),
    }


def _write_comment_to_staging(parsed: dict) -> Path:
    # Microsecond precision, plus an incrementing suffix on collision --
    # a single check_once() call can process several queued submissions
    # within the same second (found live via a test sending 2 in one poll
    # cycle, which silently overwrote the first with second-level-only
    # precision).
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    base_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    path = STAGING_DIR / f"from_rich_comment_{base_ts}.md"
    suffix = 0
    while path.exists():
        suffix += 1
        path = STAGING_DIR / f"from_rich_comment_{base_ts}_{suffix}.md"
    path.write_text(
        "# Director page comment\n\n"
        f"**Page:** {parsed['page']}\n"
        f"**Visible state:** {parsed['state'] or '(not provided)'}\n"
        f"**Data timestamp/commit:** {parsed['data_ts'] or '(not provided)'}\n\n"
        f"{parsed['comment']}\n"
    )
    return path


def check_once(since: float) -> float:
    """Poll once for messages posted after `since` on the comments topic.
    Returns the new watermark. Never raises on a network hiccup -- same
    best-effort contract as every other NTFY poller in this codebase."""
    if not COMMENTS_TOPIC:
        log("SE_COMMENTS_TOPIC not set -- skipping poll")
        return since

    poll_url = f"https://ntfy.sh/{COMMENTS_TOPIC}/json"
    try:
        response = requests.get(poll_url, params={"poll": "1", "since": int(since)}, timeout=10)
    except requests.RequestException as e:
        log(f"Poll error: {e}")
        return since

    latest = since
    for line in response.text.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("event") != "message":
            continue
        msg_time = record.get("time", 0)
        if msg_time <= since:
            continue
        latest = max(latest, msg_time)

        message = record.get("message", "")
        parsed = parse_comment_submission(message)
        if parsed is None:
            log(f"Rejected submission (missing/wrong PIN or malformed) id={record.get('id')!r}")
            continue

        staged_path = _write_comment_to_staging(parsed)
        log(f"Comment staged as {staged_path.name} -- page={parsed['page']!r}")
        notify(f"Comment received from {parsed['page']} and queued for review.", kind="director_echo")
        update_agent_status(
            "director-comments", status="idle",
            last_action=f"Staged comment from {parsed['page']}",
            role="Validates PIN-authenticated director page comments, stages accepted ones",
            produces="docs/staging/from_rich_comment_*.md",
        )

    return latest


def main() -> None:
    if not COMMENTS_TOPIC or not COMMENTS_PIN:
        log("SE_COMMENTS_TOPIC/SE_COMMENTS_PIN not set -- cannot start (load background/.env.ntfy first)")
        return
    log("Director comments daemon started")
    since = _load_since()
    while True:
        try:
            since = check_once(since)
            _save_since(since)
        except Exception as e:
            log(f"Cycle error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
