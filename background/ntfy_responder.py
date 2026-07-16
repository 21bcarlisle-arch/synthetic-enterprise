#!/usr/bin/env python3
"""NTFY instant-ack responder — always-on, independent of the main session.

Problem this solves: the 'claude' tmux session (the main Claude Code agent)
can be deep in a long GPU-bound background simulation run, a multi-minute
tool call, or simply mid-thought when Rich sends a message via NTFY. The
existing two-way channel (`session_watchdog.py`'s `check_inbound_commands`)
relays the message into that session, but the relay only *types* the
message — it doesn't guarantee a timely reply, and Rich has no feedback that
anything happened.

This script polls the same shared NTFY topic (SE_NTFY_TOPIC, see
ntfy_utils.py) independently (its own watermark file, so it doesn't
interfere with session_watchdog's), and for
every inbound message NOT sent by us, immediately replies with a short status
snapshot: what the latest background simulation run is doing (if any), GPU
utilisation, and the current git HEAD. This is a templated reply — no LLM
call, so it never competes with the simulation for GPU and is always fast.

It does NOT interpret, action, or replace anything — session_watchdog still
relays the message into the 'claude' session as before, and the Staging
Directory Protocol still applies for substantial instructions. This is purely
an instant "I heard you, here's what's running" ack so Rich always gets a
response, regardless of what else is happening.

Logs to docs/observability/ntfy-responder-log.md.
Persists its watermark to background/.ntfy_responder_since.json.
"""

import hashlib
import json
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

PROJECT_DIR = Path("/home/rich/synthetic-enterprise")
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "ntfy-responder-log.md"
STATE_FILE = PROJECT_DIR / "background" / ".ntfy_responder_since.json"
SEEN_HASHES_FILE = PROJECT_DIR / "background" / ".ntfy_responder_seen_hashes.json"
OBSERVABILITY_DIR = PROJECT_DIR / "docs" / "observability"

# ntfy.sh can replay old messages with new timestamps on network blips.
# We keep a rolling set of content hashes (last MAX_SEEN_HASHES messages)
# so replayed identical content is silently dropped regardless of timestamp.
MAX_SEEN_HASHES = 500

POLL_INTERVAL_SECONDS = 20
RUN_LOG_GLOB = "*_run.log"
RUN_LOG_FRESH_SECONDS = 3600  # ignore run logs not touched in the last hour

# --- Inbound flood guard (2026-07-15, inbound_tagging_and_rate_guard part B) ---
# A machine-cadence flood (e.g. an echo loop of our own un-tagged status
# replies, or a hostile/faulty publisher hammering the topic) must NOT reach
# the scanned staging root, where each staged from_rich re-grants supervisor
# turns. Detection is by a rolling window: N inbound in the window, OR K
# identical bodies in the window, = flood. Flood messages are QUARANTINED
# (written to docs/staging/quarantine/, which supervisor.py's iterdir()+is_file()
# scan excludes automatically) -- never dropped silently, so nothing is lost and
# a real message caught in the tail of a flood can still be recovered by hand.
# On flood we also SUPPRESS the status reply: the reply is precisely what feeds
# an echo loop. One alert per FLOOD_ALERT_COOLDOWN_SECONDS.
FLOOD_WINDOW_SECONDS = 600          # rolling 10-minute window
FLOOD_MAX_IN_WINDOW = 8             # >= this many inbound in the window = flood
FLOOD_IDENTICAL_THRESHOLD = 3       # >= this many identical bodies in window = flood
FLOOD_ALERT_COOLDOWN_SECONDS = 3600
FLOOD_MAX_TRACKED_EVENTS = 500      # hard cap on retained (ts, hash) events

PROGRESS_RE = re.compile(
    r"progress: ([\d,]+) settlement periods processed "
    r"\(latest: (\S+) period (\d+), treasury £([\d.]+)\)"
)

# Standalone script -- add the repo root so `from background.ntfy_utils
# import ...` works regardless of how it's invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from background.ntfy_utils import NTFY_TOPIC, NTFY_AUTH_TOKEN, send_ntfy, was_sent_by_us  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402

NTFY_POLL_URL = f"https://ntfy.sh/{NTFY_TOPIC}/json"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _load_since() -> float:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())["since"]
        except (json.JSONDecodeError, KeyError):
            pass
    return time.time()


def _save_since(since: float) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"since": since}))


def _content_hash(message: str) -> str:
    return hashlib.md5(message.encode()).hexdigest()


def _load_seen_hashes() -> list[str]:
    if SEEN_HASHES_FILE.exists():
        try:
            return json.loads(SEEN_HASHES_FILE.read_text())
        except (json.JSONDecodeError, ValueError):
            pass
    return []


def _save_seen_hashes(hashes: list[str]) -> None:
    SEEN_HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_HASHES_FILE.write_text(json.dumps(hashes[-MAX_SEEN_HASHES:]))


def _latest_run_log() -> Path | None:
    """Most recently modified `*_run.log`, if touched within the last
    RUN_LOG_FRESH_SECONDS — otherwise None (no active run)."""
    candidates = list(OBSERVABILITY_DIR.glob(RUN_LOG_GLOB))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    if time.time() - latest.stat().st_mtime > RUN_LOG_FRESH_SECONDS:
        return None
    return latest


def _run_progress_summary() -> str:
    run_log = _latest_run_log()
    if run_log is None:
        return "no active background simulation run"

    # Read the tail of the file without loading it all into memory.
    with open(run_log, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 8192))
        tail = f.read().decode(errors="replace")

    matches = PROGRESS_RE.findall(tail)
    if not matches:
        return f"{run_log.name} active, no progress line found in tail yet"

    periods, date, period, treasury = matches[-1]
    wake_ups = tail.count("[RISK COMMITTEE] Woken")
    return (
        f"{run_log.name}: {periods} periods processed, latest {date} "
        f"period {period}, treasury £{treasury}"
        + (f", {wake_ups} risk-committee wake-up(s) in the visible tail" if wake_ups else "")
    )


def _gpu_summary() -> str:
    for nvidia_smi in ("nvidia-smi", "/usr/lib/wsl/lib/nvidia-smi"):
        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                util, used, total = (x.strip() for x in result.stdout.strip().split(","))
                return f"GPU {util}% util, {used}/{total} MiB VRAM"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return "GPU status unavailable"


def _git_head_summary() -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h %s"],
            capture_output=True, text=True, cwd=PROJECT_DIR, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else "git HEAD unavailable"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "git HEAD unavailable"


def _write_to_staging(message: str) -> Path | None:
    """Write an inbound NTFY message to docs/staging/ so the Claude Code session
    picks it up on its next staging-directory poll. Returns the path written, or
    None if the message is too short to warrant staging (plain status pings)."""
    # ANSWER-CORRELATION (2026-07-16, answer-re-dispatch fix): if this inbound is a
    # reply that CLOSES an open escalation (starts with its reply-PIN), resolve that
    # escalation and do NOT re-ingest it as a fresh urgent from_rich command. Without
    # this, every answer Rich NTFY'd back was re-flagged URGENT and re-queued.
    try:
        from background.action_needed import resolve_by_pin
        tokens = message.strip().split()
        if tokens:
            first = tokens[0].strip(":#").upper()
            candidate = (tokens[1].strip(":#").upper()
                         if first == "PIN" and len(tokens) > 1 else first)
            closed = resolve_by_pin(candidate, message.strip())
            if closed:
                log(f"Inbound CLOSED escalation {closed} via reply-PIN {candidate} "
                    "-- resolved + [RECORDED]; NOT re-staged as a fresh command")
                return None
    except Exception as exc:  # never let correlation crash the responder
        log(f"answer-correlation skipped (non-fatal): {exc}")
    if len(message) < 25:
        # A short message is normally a status ping to ignore -- UNLESS a
        # director question is open, in which case a terse "B" / "yes" is the
        # EXPECTED shape of the answer, not noise. Silently dropping it is
        # exactly what let the W2_2 curriculum answer evaporate (2026-07-14
        # retro): A/B/C/D answers are inherently under 25 chars. When anything
        # is awaiting the director, stage the short reply; only drop it when
        # nothing is open (a genuine status ping).
        try:
            from background.action_needed import open_items
            if not open_items():
                return None
        except Exception:
            return None  # can't confirm an open item -> keep the old safe default
    staging_dir = PROJECT_DIR / "docs" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = staging_dir / f"from_rich_{ts}.md"
    path.write_text(f"# Inbound NTFY message from Rich\n\n{message}\n")
    return path


def _rate_state_file() -> Path:
    """Resolved at CALL time from the module global PROJECT_DIR (same pattern as
    _write_to_staging) so a test's monkeypatch of PROJECT_DIR redirects it."""
    return PROJECT_DIR / "background" / ".ntfy_responder_rate.json"


def _quarantine_dir() -> Path:
    """docs/staging/quarantine/ -- a subdirectory, so supervisor.py's
    iterdir()+is_file() staging scan skips it automatically (verified against
    _unprocessed_staging_files)."""
    return PROJECT_DIR / "docs" / "staging" / "quarantine"


def _load_rate_state() -> dict:
    p = _rate_state_file()
    if p.exists():
        try:
            state = json.loads(p.read_text())
            if isinstance(state, dict):
                state.setdefault("events", [])
                state.setdefault("last_alert", 0)
                return state
        except (json.JSONDecodeError, ValueError, OSError):
            pass
    return {"events": [], "last_alert": 0}


def _save_rate_state(state: dict) -> None:
    p = _rate_state_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state))


def _register_inbound_and_detect_flood(
    content_hash: str, now: float, state: dict
) -> tuple[bool, str | None]:
    """Record this inbound arrival in the rolling window and decide whether we
    are in a flood. Mutates `state["events"]` in place (caller persists it).

    A flood is EITHER a raw-rate flood (>= FLOOD_MAX_IN_WINDOW inbound within
    FLOOD_WINDOW_SECONDS -- catches distinct-body echo loops whose bodies vary,
    e.g. our own status replies that differ only by GPU%/HEAD) OR an
    identical-body flood (>= FLOOD_IDENTICAL_THRESHOLD copies of one body in the
    window -- caught BEFORE the replay-dedup so it is quarantined and preserved
    rather than silently deduped)."""
    window_start = now - FLOOD_WINDOW_SECONDS
    events = [e for e in state.get("events", []) if e[0] >= window_start]
    events.append([now, content_hash])
    events = events[-FLOOD_MAX_TRACKED_EVENTS:]
    state["events"] = events

    count = len(events)
    identical = sum(1 for e in events if e[1] == content_hash)
    minutes = FLOOD_WINDOW_SECONDS // 60
    if identical >= FLOOD_IDENTICAL_THRESHOLD:
        return True, f"{identical} identical-body messages within {minutes}min"
    if count >= FLOOD_MAX_IN_WINDOW:
        return True, f"{count} inbound messages within {minutes}min"
    return False, None


def _quarantine(message: str, reason: str) -> Path:
    """Preserve a flood message in docs/staging/quarantine/ (NOT the scanned
    root). Fail-safe: nothing is ever dropped -- this file is the durable
    record so a genuine message caught in a flood tail can be recovered."""
    qdir = _quarantine_dir()
    qdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = qdir / f"from_rich_QUARANTINED_{ts}_{uuid.uuid4().hex[:8]}.md"
    path.write_text(
        "# QUARANTINED inbound NTFY message (flood guard)\n\n"
        f"Reason: {reason}\n\n"
        "The responder detected a machine-cadence flood and withheld this "
        "message from the scanned staging root. Nothing is dropped -- this file "
        "preserves the content for manual review.\n\n---\n\n"
        f"{message}\n"
    )
    return path


def build_status_reply(staged_path: Path | None = None) -> str:
    classification = "instruction" if staged_path else "status ping"
    action = "queued for Claude Code" if staged_path else "no action (message too short)"
    return (
        f"[{classification}] {action}\n"
        f"Sim: {_run_progress_summary()}\n"
        f"{_gpu_summary()}\n"
        f"HEAD: {_git_head_summary()}"
    )


def check_once(since: float, seen_hashes: list[str]) -> tuple[float, list[str]]:
    """Poll once for messages posted after `since`, not sent by us. For each,
    send an instant status ack. Returns (new watermark, updated seen_hashes).

    Content-hash dedup: ntfy.sh replays old messages with new timestamps on
    network blips. We maintain a rolling list of MD5 hashes of processed
    message bodies so identical content is dropped regardless of timestamp.
    """
    _headers = {"Authorization": f"Bearer {NTFY_AUTH_TOKEN}"} if NTFY_AUTH_TOKEN else {}
    try:
        response = requests.get(
            NTFY_POLL_URL, params={"poll": "1", "since": int(since)}, timeout=10,
            headers=_headers,
        )
    except requests.RequestException as e:
        log(f"Poll error: {e}")
        return since, seen_hashes

    seen_set = set(seen_hashes)
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

        if was_sent_by_us(record.get("id")):
            continue

        message = record.get("message", "").strip()
        if not message:
            continue

        h = _content_hash(message)

        # Flood guard (2026-07-15): register every inbound arrival and detect a
        # machine-cadence flood BEFORE the replay-dedup below -- an
        # identical-body flood would otherwise be silently dropped by dedup and
        # never counted, and a distinct-body echo loop would restage forever.
        # On flood: QUARANTINE (preserve, never drop) into the UNSCANNED
        # docs/staging/quarantine/ dir, alert once with cooldown, and DO NOT
        # reply -- the status reply is what feeds an echo loop.
        rate_state = _load_rate_state()
        flooding, flood_reason = _register_inbound_and_detect_flood(
            h, record.get("time", time.time()), rate_state
        )
        if flooding:
            qpath = _quarantine(message, flood_reason)
            now_ts = time.time()
            if now_ts - rate_state.get("last_alert", 0) >= FLOOD_ALERT_COOLDOWN_SECONDS:
                rate_state["last_alert"] = now_ts
                send_ntfy(
                    f"[FLOOD GUARD] Inbound NTFY flood quarantined ({flood_reason}). "
                    "Messages preserved in docs/staging/quarantine/, withheld from the "
                    f"scanned staging root. No further alerts for "
                    f"{FLOOD_ALERT_COOLDOWN_SECONDS // 60}min.",
                    headers={"X-Priority": "4", "X-Tags": "rotating_light"},
                )
            _save_rate_state(rate_state)
            log(f"Quarantined inbound flood message {record.get('id')!r} -> "
                f"{qpath.name} ({flood_reason})")
            continue
        _save_rate_state(rate_state)

        if h in seen_set:
            log(f"Duplicate content ignored (hash={h[:8]}, id={record.get('id')!r}): {message[:60]!r}")
            continue

        seen_hashes.append(h)
        seen_set.add(h)

        try:
            from background.ntfy_mirror import append_mirror_entry
            append_mirror_entry("in", message, topic=NTFY_TOPIC)
        except Exception:
            pass  # mirroring must never block real inbound processing

        try:
            # DIRECTOR_INPUT_LOG.md channel-tagged log (2026-07-11): this
            # call site unambiguously KNOWS its own channel is "ntfy" --
            # pass channel_hint rather than relying on classify_channel()'s
            # inference, which is for cases (the UserPromptSubmit hook)
            # that don't already know.
            from background.director_input_log import classify_and_log_message
            classify_and_log_message(message, channel_hint="ntfy")
        except Exception:
            pass  # logging must never block real inbound processing

        staged_path = _write_to_staging(message)
        reply = build_status_reply(staged_path)
        send_ntfy(reply, headers={"X-Priority": "3", "X-Tags": "satellite_antenna"})
        log(f"Acked inbound message {record.get('id')!r} ({message[:60]!r})"
            + (f" — staged as {staged_path.name}" if staged_path else ""))
        update_agent_status(
            "ntfy-responder", status="idle",
            last_action=f"Acked message: {message[:80]!r}",
            role="Receives NTFY messages from Rich; writes from_rich_*.md to staging",
            produces="docs/staging/from_rich_*.md",
        )

    return latest, seen_hashes


def main() -> None:
    since = _load_since()
    seen_hashes = _load_seen_hashes()
    log("NTFY responder started")
    while True:
        try:
            new_since, seen_hashes = check_once(since, seen_hashes)
            if new_since != since:
                since = new_since
                _save_since(since)
            _save_seen_hashes(seen_hashes)
        except Exception as e:
            log(f"Responder error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
