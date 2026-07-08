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
from background.ntfy_utils import send_ntfy, sign_wake_message  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.tmux_relay import send_keys_when_idle  # noqa: E402

# Files the dispatcher has already classified. Persisted across restarts.
# Value: classification ("urgent"|"normal"|"fyi")
_SEEN_FILE = PROJECT_DIR / "background" / ".dispatcher_seen.json"

# Filename -> message text for URGENT relays not yet confirmed-delivered
# (root-cause fix, docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md,
# 2026-07-08: a live incident showed a signed wake landing partially in a
# busy pane and never submitting). Classification/header/NTFY happen
# immediately in route_message() regardless -- only the tmux wake itself is
# retried here, each poll cycle, until send_keys_when_idle() confirms
# delivery. In-memory only, matching staging_watcher's same tradeoff: a
# restart before delivery drops the retry, but the high-priority NTFY
# already sent is the durable fallback.
_pending_urgent: dict[str, str] = {}


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


def _relay_to_claude(message: str) -> bool:
    """Attempt to type `message` into the 'claude' tmux session (same as
    session_watchdog), via background.tmux_relay.send_keys_when_idle --
    refuses to run under pytest (see that module's docstring), refuses to
    send at all unless the pane is currently idle, and verifies after
    sending that the text was actually consumed rather than trusting a
    fire-and-forget send.

    Root-cause fix (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md,
    2026-07-08): a live incident showed exactly this relay's signed text
    landing partially in the target pane's input box and never submitting
    -- "queues input while busy" does not reliably hold. Returns False on
    any failure; callers must retry, never assume delivery.

    HMAC-signed (docs/staging/NTFY_CHANNEL_HARDENING.md, 2026-07-08) -- see
    staging_watcher._relay_wake_to_claude for the same pattern. The
    trailing HMAC hex digest doubles as the consumption-verification
    marker."""
    suffix = (
        " [DISPATCHER: URGENT — this message has been classified as requiring "
        "immediate attention. Pause current work, read this, and respond.]"
    )
    signed = sign_wake_message(message + suffix)
    marker = signed.rsplit("|", 1)[-1]
    return send_keys_when_idle(SESSION_NAME, signed, marker)


def route_message(path: Path, message: str, classification: str) -> None:
    """Apply routing action based on classification."""
    if classification == "urgent":
        _prepend_urgency_header(path, "urgent")
        _pending_urgent[path.name] = message
        send_ntfy(
            f"[DISPATCHER: URGENT] Message from Rich flagged as urgent: {message[:100]}",
            headers={"X-Priority": "5", "X-Tags": "warning"},
        )
        log(f"URGENT classified: {path.name} — high-priority NTFY sent, wake queued (retried until confirmed)")

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


def _attempt_pending_urgent() -> None:
    """Attempt delivery of any queued URGENT relay(s) not yet confirmed --
    called once per main() cycle. Only clears an entry on CONFIRMED
    delivery (idle pane + consumption verified); on failure (busy, or
    stuck-unconsumed), leaves it queued for the next cycle's retry, per
    the root-cause fix's "never fire into a mid-turn session, hold and
    retry" requirement. Classification/header/NTFY already happened in
    route_message() regardless of wake delivery."""
    if not _pending_urgent:
        return
    for name in sorted(_pending_urgent):
        message = _pending_urgent[name]
        if _relay_to_claude(message):
            log(f"URGENT wake delivered (confirmed): {name}")
            del _pending_urgent[name]
        else:
            log(f"URGENT wake not yet delivered (session busy or unconfirmed) -- retrying next cycle: {name}")


def main() -> None:
    log("Dispatcher started")
    seen = _load_seen()

    while True:
        try:
            seen = check_once(seen)
        except Exception as e:
            log(f"Dispatcher error: {e}")

        try:
            _attempt_pending_urgent()
        except Exception as e:
            log(f"Pending-urgent-relay attempt error: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
