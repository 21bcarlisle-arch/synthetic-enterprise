#!/usr/bin/env python3
"""Message dispatcher — flags inbound NTFY messages that must interrupt, by keyword.

ntfy_responder.py handles auto-ack. For each new from_rich_*.md in docs/staging/ this
classifies it by a fixed keyword list and routes it:
  URGENT — a keyword in _URGENT_KEYWORDS ("wrong", "idle", "stop", ...). Action: prepend
           an URGENT header and send a HIGH-priority NTFY; the file stays in staging and
           the supervisor's poll serves it first, straight off disk.
  NORMAL — everything else. Action: prepend a NORMAL header, leave in staging.

The ambiguous-case classifier was local Qwen, and it was the only thing that could
return FYI (move to staging/fyi/, no notification). The model was evicted 2026-08-10,
from which date every non-keyword message fell to NORMAL; the Qwen call and the FYI
route were removed 2026-09-27. Nothing the director sends is filed away unread.

Logs to docs/observability/dispatcher-log.md.
State file: background/.dispatcher_seen.json
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "dispatcher-log.md"
STATE_FILE = PROJECT_DIR / "background" / ".dispatcher_seen.json"
POLL_INTERVAL_SECONDS = 15

SESSION_NAME = "claude"

sys.path.insert(0, str(PROJECT_DIR))
from background.notify import notify  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.episode_prior import load_episode_prior, preserve_unreadable, prior_unreadable  # noqa: E402,E501

# PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md): the dispatcher
# NO LONGER types URGENT messages into the live 'claude' pane. Keystroke
# injection is deleted (banned; five deaths). The dispatcher still classifies
# every from_rich_*.md and, for URGENT, sends a high-priority NTFY and prepends
# a URGENT header -- but the message reaches the session via STAGING + the
# pull-loop draw (supervisor.find_work serves URGENT-classified from_rich files
# first), not by typing into the director's console.

# Files the dispatcher has already classified. Persisted across restarts.
# Value: classification ("urgent"|"normal"; "fyi" in entries before 2026-09-27)
_SEEN_FILE = PROJECT_DIR / "background" / ".dispatcher_seen.json"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _load_seen() -> tuple[dict[str, str], str]:
    """`(seen, verdict)` over the classification memory. See `background/episode_prior.py`.

    MEASURED 2026-09-04, against a live prior of two classified filenames. The old body was
    `json.loads` under `except (json.JSONDecodeError, Exception)` -- which is just
    `except Exception` -- returning `{}` on the way out:

        missing file      -> {}                    correct
        empty file        -> {}                    every classification lost
        truncated         -> {}                    every classification lost
        json null         -> None                  from a function annotated -> dict[str, str]
        [1, 2, 3]         -> [1, 2, 3]             likewise, a list
        ["x", 2]          -> ['x', 2]              likewise
        {"other": 1}      -> {'other': 1}          a mapping that is not this record

    `null` and the two lists PARSE, so the except-clause never saw them, and the next thing the
    caller does is `seen[path.name] = classification` -- TypeError on a list, and the `.get`
    paths raise AttributeError on None. The dispatcher runs on every staged file.

    The `{}` rows are the destructive half and the reason this carrier was ranked first: this is
    a read-modify-write, so `{}` is not merely a lost suppression -- the very next `_save_seen`
    writes that `{}` back over the file. Every from_rich the dispatcher had already classified
    and routed becomes unseen, is re-classified, and is re-routed and re-notified. That is the
    stale-from_rich re-jam the archive-on-answer mechanism in staging_watcher exists to stop,
    arriving by a different door.
    """
    return load_episode_prior(_SEEN_FILE)


def _save_seen(seen: dict[str, str]) -> None:
    _SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SEEN_FILE.write_text(json.dumps(seen, indent=2))


def _preserve_unreadable_seen() -> str | None:
    """Move an unreadable seen-map aside before the rebuild writes over it. Where it went.

    Never overwrites an earlier copy, because the FIRST loss is the one that still holds the
    classifications. That loop is `episode_prior.preserve_unreadable` since 2026-09-04 -- five
    modules had written it out separately and a sixth caller was one copy too many.
    """
    return preserve_unreadable(_SEEN_FILE)


_URGENT_KEYWORDS = frozenset([
    "urgent", "stop", "immediately", "wrong", "broken", "incorrect",
    "investigation", "investigate", "idle", "nothing", "silence",
    "radio silence", "are you", "doing anything",
])


def classify_message(message: str) -> str:
    """'urgent' if the message carries an explicit urgency keyword, else 'normal'."""
    lower = message.lower()
    if any(kw in lower for kw in _URGENT_KEYWORDS):
        return "urgent"
    return "normal"


def _prepend_urgency_header(path: Path, classification: str) -> None:
    """Add a dispatcher header to the top of the staging file."""
    existing = path.read_text()
    header = f"<!-- Dispatcher: {classification.upper()} (classified {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}) -->\n"
    path.write_text(header + existing)


def route_message(path: Path, message: str, classification: str) -> None:
    """Apply routing action based on classification.

    PULL-LOOP MIGRATION (2026-07-15): URGENT no longer types into the pane. It
    prepends a URGENT header and sends a high-priority NTFY; the file stays in
    staging where the pull-loop draw (supervisor.find_work) serves it first."""
    if classification == "urgent":
        _prepend_urgency_header(path, "urgent")
        notify(
            f"[DISPATCHER: URGENT] Message from Rich flagged as urgent: {message[:100]}",
            kind="real_alarm",
            headers={"X-Priority": "5", "X-Tags": "warning"},
        )
        log(f"URGENT classified: {path.name} — high-priority NTFY sent; served via staging + pull-loop draw (no pane injection)")

    else:  # normal
        _prepend_urgency_header(path, "normal")
        log(f"NORMAL: {path.name} — left in staging for Claude's next staging-poll")


def check_once(seen: dict[str, str]) -> dict[str, str]:
    """Scan staging/ for new from_rich_*.md files. Classify and route each.
    Returns updated seen dict."""
    if not STAGING_DIR.is_dir():
        return seen

    files = sorted(
        p for p in STAGING_DIR.glob("from_rich_*.md")
        if p.name not in seen
    )

    for path in files:
        message_text = ""
        try:
            content = path.read_text()
            # Skip files already processed in a prior dispatcher run (have header).
            # Prevents re-routing stale files after a dispatcher restart.
            if content.startswith("<!-- Dispatcher:"):
                seen[path.name] = "already-processed"
                _save_seen(seen)
                continue
            # Extract the actual message (after the header line)
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("# Inbound NTFY") or line.startswith("<!--"):
                    continue
                message_text = " ".join(lines[i:]).strip()
                break
        except Exception:
            seen[path.name] = "normal"
            continue

        if not message_text:
            seen[path.name] = "normal"
            continue

        classification = classify_message(message_text)
        seen[path.name] = classification
        # Save before routing so a crash during send_ntfy/tmux doesn't cause
        # the file to be re-processed (and re-notified) on the next restart.
        _save_seen(seen)
        route_message(path, message_text, classification)
        update_agent_status(
            "dispatcher", status="idle",
            last_action=f"Classified {path.name} as {classification.upper()}",
            role="Flags inbound NTFY messages URGENT by keyword, else NORMAL",
            produces="docs/observability/dispatcher-log.md, routes to staging/",
        )

    return seen


def main() -> None:
    log("Dispatcher started")
    seen, verdict = _load_seen()
    if prior_unreadable(verdict):
        # PRESERVE BEFORE THE FIRST _save_seen, which is a whole-map overwrite and would destroy
        # the only record of what had already been classified and routed. Said on the surface:
        # every staged from_rich is about to be treated as new, so the director may be re-notified
        # about messages he has already had an answer to.
        preserved = _preserve_unreadable_seen()
        log(f"Dispatcher started with a PRESENT AND UNREADABLE seen-map, not an absent one: "
            f"every already-classified staged file will be re-classified and may be re-routed. "
            f"Old bytes kept at {preserved or '(could not be preserved)'}.")

    while True:
        try:
            seen = check_once(seen)
        except Exception as e:
            log(f"Dispatcher error: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/dispatcher.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("dispatcher")
    main()
