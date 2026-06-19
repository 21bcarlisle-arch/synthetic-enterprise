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
"""

import json
import re
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
from background.ntfy_utils import send_ntfy  # noqa: E402

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


def _load_seen() -> dict[str, str]:
    if _SEEN_FILE.exists():
        try:
            return json.loads(_SEEN_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            pass
    return {}


def _save_seen(seen: dict[str, str]) -> None:
    _SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SEEN_FILE.write_text(json.dumps(seen, indent=2))


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


def _relay_to_claude(message: str) -> None:
    """Type message into the 'claude' tmux session (same as session_watchdog)."""
    suffix = (
        " [DISPATCHER: URGENT — this message has been classified as requiring "
        "immediate attention. Pause current work, read this, and respond.]"
    )
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", SESSION_NAME, message + suffix, "Enter"],
            capture_output=True, timeout=5,
        )
    except Exception:
        pass


def route_message(path: Path, message: str, classification: str) -> None:
    """Apply routing action based on classification."""
    if classification == "urgent":
        _prepend_urgency_header(path, "urgent")
        _relay_to_claude(message)
        send_ntfy(
            f"[DISPATCHER: URGENT] Message from Rich flagged as urgent: {message[:100]}",
            headers={"X-Priority": "5", "X-Tags": "warning"},
        )
        log(f"URGENT routed: {path.name} — relayed to Claude session + high-priority NTFY")

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
        route_message(path, message_text, classification)

    if files:
        _save_seen(seen)

    return seen


def main() -> None:
    log("Dispatcher started")
    seen = _load_seen()

    while True:
        try:
            seen = check_once(seen)
        except Exception as e:
            log(f"Dispatcher error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
