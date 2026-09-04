#!/usr/bin/env python3
"""Intelligent message dispatcher — classifies inbound NTFY messages and routes
by urgency.

ntfy_responder.py handles auto-ack (always-on, fast, no LLM). This script adds
a classification layer on top: for each new from_rich_*.md that appears in
docs/staging/, it calls Qwen to decide whether the message is urgent, normal,
or informational, then routes accordingly.

Classification → routing:
  URGENT — something that should interrupt active work (fundamental correctness
            issue, design decision that would cause wasted work if missed).
            Action: send HIGH-priority NTFY immediately, relay to Claude session
            via tmux (same mechanism as session_watchdog).
  NORMAL — a real instruction that needs action but can wait for Claude to pick
            it up in its normal staging-poll cycle.
            Action: add urgency header to the file, leave in staging/.
  FYI    — informational: acknowledgement, status update, comment Rich wants
            logged but that doesn't require a response.
            Action: move to staging/fyi/, log it, no notification.

Routing table (scalable to multiple agents — add entries per destination):
  ROUTING_TABLE = {
      "urgent": ["ntfy_high", "tmux_relay"],   # interrupt + relay
      "normal": ["staging"],                    # leave in staging, add header
      "fyi":    ["fyi_dir"],                    # move to fyi/
  }

Logs to docs/observability/dispatcher-log.md.
State file: background/.dispatcher_seen.json

FAST-PATH HINT, not the guarantee (2026-07-09, doorbell failure #4): the
URGENT tmux relay below shortens the wait from "up to 2 minutes" to
"seconds" when it works, but background/supervisor.py's own poll
independently detects any unprocessed from_rich_*.md carrying the
"Dispatcher: URGENT" header (see route_message's _prepend_urgency_header)
straight off disk -- it does not depend on this relay, or on dispatcher.py
being alive, to eventually grant a turn for it.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
FYI_DIR = STAGING_DIR / "fyi"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "dispatcher-log.md"
STATE_FILE = PROJECT_DIR / "background" / ".dispatcher_seen.json"
POLL_INTERVAL_SECONDS = 15

SESSION_NAME = "claude"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:14b"

sys.path.insert(0, str(PROJECT_DIR))
from background.notify import notify  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.episode_prior import load_episode_prior, prior_unreadable  # noqa: E402

# PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md): the dispatcher
# NO LONGER types URGENT messages into the live 'claude' pane. Keystroke
# injection is deleted (banned; five deaths). The dispatcher still classifies
# every from_rich_*.md and, for URGENT, sends a high-priority NTFY and prepends
# a URGENT header -- but the message reaches the session via STAGING + the
# pull-loop draw (supervisor.find_work serves URGENT-classified from_rich files
# first), not by typing into the director's console.

# Files the dispatcher has already classified. Persisted across restarts.
# Value: classification ("urgent"|"normal"|"fyi")
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

    Same shape as `ntfy_utils._preserve_unreadable_sent_ids`; never overwrites an earlier copy,
    because the FIRST loss is the one that still holds the classifications.
    """
    for suffix in ("", *(f".{n}" for n in range(1, 10))):
        target = _SEEN_FILE.with_name(_SEEN_FILE.name + f".unreadable{suffix}")
        if target.exists():
            continue
        try:
            _SEEN_FILE.replace(target)
        except OSError:
            return None
        return target.name
    return None


def _call_qwen(prompt: str, max_tokens: int = 100) -> str:
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", OLLAMA_URL,
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "model": OLLAMA_MODEL,
                 "prompt": prompt,
                 "stream": False,
                 "options": {"num_predict": max_tokens, "temperature": 0.0},
             })],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("response", "").strip()
    except Exception:
        pass
    return ""


_URGENT_KEYWORDS = frozenset([
    "urgent", "stop", "immediately", "wrong", "broken", "incorrect",
    "investigation", "investigate", "idle", "nothing", "silence",
    "radio silence", "are you", "doing anything",
])


def classify_message(message: str) -> str:
    """Classify a message as 'urgent', 'normal', or 'fyi'.

    Fast-path: if the message contains explicit urgency keywords, return
    'urgent' without calling Qwen (Qwen has missed these before).
    Falls back to Qwen for ambiguous cases.
    """
    lower = message.lower()

    # Explicit urgency signals — don't trust Qwen with these
    if any(kw in lower for kw in _URGENT_KEYWORDS):
        return "urgent"

    prompt = f"""You are a message classifier for an energy simulation operator (Rich) communicating with an autonomous AI agent (Claude Code). Classify this inbound message from Rich.

Message: "{message}"

Rules:
- URGENT: Rich is asking why something is wrong or why the agent is idle; or has spotted a correctness problem; or has explicitly flagged urgency. Examples: "gross margin looks wrong", "are you idle", "why no messages", "URGENT", "investigation", "stop what you're doing".
- NORMAL: a real instruction, request, or design steer that needs action but is not an emergency. Examples: "start the next phase", "review the report", "when GPU is free, run X", "add feature Y".
- FYI: informational only, no action required. Examples: "I'll be back in an hour", "nice work", "ok", acknowledgement.

Respond with EXACTLY one word: urgent, normal, or fyi
/no_think"""

    response = _call_qwen(prompt, max_tokens=10)
    response_lower = response.lower().strip()

    if "urgent" in response_lower:
        return "urgent"
    if "fyi" in response_lower:
        return "fyi"
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

    elif classification == "fyi":
        FYI_DIR.mkdir(parents=True, exist_ok=True)
        dest = FYI_DIR / path.name
        path.rename(dest)
        log(f"FYI routed: {path.name} → staging/fyi/ (no notification)")

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
            role="Classifies inbound NTFY messages (URGENT/NORMAL/FYI) using Qwen3:14b",
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
