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

import fcntl
import hashlib
import json
import os
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
from background.agent_status import update_agent_status  # noqa: E402
# BELOW the sys.path.insert, not at the top of the file. This module is launched as a SCRIPT
# PATH (`python3 background/ntfy_responder.py`), so `background` is not importable until that
# insert has run -- a top-of-file `from background import ...` raises ModuleNotFoundError before
# a single line of the daemon executes. Caught by
# `tests/background/test_declared_entrypoints_import_in_script_mode.py`, which exists for exactly
# this, on the first full-suite run after the guard was wired in.
from background import inbound_secret_redaction  # noqa: E402
from background.notify import notify  # noqa: E402
from background.ntfy_utils import NTFY_AUTH_TOKEN, NTFY_TOPIC, sent_ids_unreadable, was_sent_by_us  # noqa: E402,E501

NTFY_POLL_URL = f"https://ntfy.sh/{NTFY_TOPIC}/json"


def log(msg: str) -> None:
    """Append to the responder log, with the inbound-credential guard applied HERE.

    LOG_FILE is `docs/observability/ntfy-responder-log.md` -- inside the working tree -- and
    several call sites below log `message[:60]`, which a 40-character token fits inside
    comfortably. Redacting at the three write call sites and not here would have left the
    third route open, which is the instance fix this was explicitly not to be. Guarding the
    function instead means every future log line inherits it without remembering.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {inbound_secret_redaction.redact(msg)[0]}"
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


# --- At-most-once EXECUTION (2026-07-29, DIRECTOR_RULING_FIX_DOUBLE_MESSAGING) ---
# CAUSE (observed, not inferred): TWO ntfy_responder.py processes were live at
# once (PIDs 266098 from 13:26 and 419021 from 18:20). The responder log records
# the SAME ntfy message id acked twice seconds apart -- e.g. 'AK0UhbkAV2Ko' at
# 17:37:31 and 17:37:42, staged as two different from_rich_*.md. A shared message
# ID proves this is neither double delivery by ntfy nor a retry path: it is one
# message read by two consumers.
#
# Why the pre-existing guards could not stop it: BOTH the `since` watermark and
# the `seen_hashes` replay-dedup are loaded ONCE at main() startup and held in
# process memory, then written back last-writer-wins. A sibling process's writes
# are never re-read, so neither guard can see a concurrent consumer -- they are
# structurally per-process and therefore blind by construction.
#
# The fix is two independent layers, because either alone leaves a hole:
#   1. SINGLETON LOCK -- only one responder may run. Fixes the actual root cause
#      (the second daemon) and REPORTS it, rather than hiding it behind a filter.
#   2. CLAIM LEDGER -- at-most-once execution regardless of how many consumers
#      exist. At-least-once *delivery* is fine; at-least-once *execution* is not.
# Layer 2 is what makes the guarantee hold even if layer 1 is ever bypassed
# (a manual run, a stale lock on a different mount) -- defence that does not
# depend on the daemon supervisor being correct.
CLAIMS_DIRNAME = ".ntfy_claimed_ids"
MAX_CLAIM_FILES = 2000
SINGLETON_LOCK_NAME = ".ntfy_responder.lock"


def _claims_dir() -> Path:
    """Directory of claimed message identities. Derived from PROJECT_DIR at CALL
    time (never a module constant) so the suite's autouse tmp_path isolation
    applies automatically -- a real-disk claim ledger leaking into tests is the
    SCHEDULED_FLAG class of defect."""
    return PROJECT_DIR / "background" / CLAIMS_DIRNAME


def _message_identity(record: dict) -> str:
    """Stable identity for one inbound message.

    ntfy's own message id is the identity when present: it is stable across
    re-delivery AND distinct between two genuinely different messages that
    happen to share a body. That distinction is the whole point -- the old
    content-hash dedup would have wrongly swallowed a director who sent 'yes'
    twice on purpose. Falls back to a body+time hash only when ntfy sends no id.
    """
    mid = str(record.get("id") or "").strip()
    if mid:
        # Filesystem-safe: the identity becomes a filename.
        return re.sub(r"[^A-Za-z0-9_.-]", "_", mid)[:64]
    body = record.get("message", "")
    return "h_" + hashlib.md5(f"{body}|{record.get('time', '')}".encode()).hexdigest()


def _prune_claims(directory: Path) -> None:
    """Keep the claim ledger bounded. Oldest-first, best-effort -- pruning must
    never break inbound processing."""
    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.stat().st_mtime)
    except OSError:
        return
    for stale in entries[:-MAX_CLAIM_FILES]:
        try:
            stale.unlink()
        except OSError:
            pass


def claim_message(identity: str) -> bool:
    """Atomically claim `identity` for execution. True iff THIS caller won it.

    O_CREAT|O_EXCL is an atomic test-and-set on a local filesystem, so two
    concurrent responders racing the same message can never both win -- exactly
    one gets True, the loser acknowledges and drops. This is the at-most-once
    EXECUTION guarantee, and it needs no lock and no coordination.

    Fail-CLOSED on an unexpected OS error: if we cannot prove we won the claim,
    we do not execute. A missed director message is recoverable (he resends and
    sees no ack); a double-executed act may not be.
    """
    directory = _claims_dir()
    try:
        directory.mkdir(parents=True, exist_ok=True)
        fd = os.open(directory / identity, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    except OSError as exc:
        log(f"Claim ledger unavailable for {identity!r} ({exc}) -- NOT executing (fail-closed)")
        return False
    try:
        os.write(fd, f"{time.time()}\n{os.getpid()}\n".encode())
    finally:
        os.close(fd)
    _prune_claims(directory)
    return True


def acquire_singleton_lock():
    """Take the exclusive responder lock. Returns the held file object (which the
    caller MUST keep referenced for the process lifetime -- closing it releases
    the lock), or None if another responder already holds it.

    flock is released automatically by the kernel when the holder dies, so a
    crashed responder never wedges its successor -- no stale-lock reaping needed.
    """
    path = PROJECT_DIR / "background" / SINGLETON_LOCK_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    # "a+" never truncates: opening "w" would have WIPED the holder's PID record before we
    # even attempted the lock, so a refused second instance left the file empty and the one
    # artefact a human reads to ask "who holds it?" answered nothing. Truncate only once we
    # have actually won.
    handle = open(path, "a+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    handle.seek(0)
    handle.truncate()
    handle.write(f"{os.getpid()}\n")
    handle.flush()
    return handle


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


# INBOUND-AS-INSTRUCTION GUARD (2026-07-29, responder_inbound_not_instruction_guard;
# DIRECTOR_RULING_ROTATE_SIGNING_KEY §4, R7/R8). The ntfy mobile app's built-in
# "Send test notification" produces a fixed machine-generated body, e.g.
#   "This is a test notification from the ntfy Android app. It has a level 3
#    priority. If you send another, it may look different."
# It carries zero authority (R7: injected/app text is a doorbell, not an instruction;
# R8: all inbound is untrusted data) and is NOT a director steer. Left ungated it
# staged as from_rich_*.md; each staged file re-granted a supervisor turn -> a model
# load (VRAM 1,383 -> 10,726 MiB, observed twice on 2026-07-29). That makes an
# app-test (or anyone who learns the public topic) a cheap denial-of-attention /
# VRAM-load vector. The guard matches ONLY this narrow, unambiguous machine string
# -- a genuine >25-char director steer is never phrased this way -- so no real
# instruction is ever dropped (the A/B/C/D short-answer-evaporation lesson,
# 2026-07-14: bias is always toward keeping a possibly-real steer, never toward
# a broad "looks non-directive" filter).
_APP_SELFTEST_RE = re.compile(r"\btest notification from the ntfy\b", re.IGNORECASE)


def _is_app_selftest(message: str) -> bool:
    """True iff `message` is the ntfy mobile app's built-in self-test notification
    (Android or iOS). High-precision by design: see _APP_SELFTEST_RE above."""
    return bool(_APP_SELFTEST_RE.search(message or ""))


def _write_to_staging(message: str) -> Path | None:
    """Write an inbound NTFY message to docs/staging/ so the Claude Code session
    picks it up on its next staging-directory poll. Returns the path written, or
    None if the message is a machine-generated ntfy-app self-test (never a
    director instruction) or is a reply-PIN closing an already-open escalation.

    Message LENGTH is never a reason to drop -- see the ruling note below."""
    # Inbound-as-instruction guard: an ntfy-app self-test is untrusted machine text
    # with zero authority -- never stage it (staging = a supervisor turn = a model
    # load). Matched narrowly so a real steer is never caught. See _is_app_selftest.
    if _is_app_selftest(message):
        return None
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
    # NO MINIMUM-LENGTH OR FORMAT CHECK ON DIRECTOR MESSAGES (2026-07-29,
    # DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY §4, authorised directly:
    # "Any minimum-length or format check on inbound director messages is
    # deleted -- 'yes', 'go' and 'PIN 07C3 PROCEED' must all work.").
    #
    # What used to be here: a `len(message) < 25` gate that dropped short
    # messages unless action_needed.open_items() was non-empty. It was already
    # known to lose real instructions (the 2026-07-14 W2_2 retro, where an
    # A/B/C/D curriculum answer evaporated) and was patched with the
    # open-items carve-out rather than removed. The carve-out FAILED OPEN in
    # the wrong direction twice over: it dropped the message when open_items()
    # raised, and -- the live case -- it dropped any terse unprompted steer
    # ("go", "yes", "ship it") whenever nothing happened to be formally open,
    # which is precisely when a short instruction is a NEW instruction rather
    # than an answer.
    #
    # The director is not a format to be validated. Length carries no signal
    # about authority, so gating on it can only ever lose real instructions;
    # the cost of staging a stray status ping is one supervisor turn, and the
    # cost of dropping a real steer is unbounded. The _is_app_selftest guard
    # above stays -- that discriminates MACHINE text from director text (R7/R8),
    # which is a different question from how long the director's sentence is.
    staging_dir = PROJECT_DIR / "docs" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = staging_dir / f"from_rich_{ts}.md"
    # Collision guard (2026-07-29): the name is second-granular, so two GENUINELY
    # DIFFERENT director messages arriving in the same second would have silently
    # overwritten each other -- losing one real instruction. De-duplicating
    # delivery must never become dropping a distinct message, so uniquify.
    if path.exists():
        path = staging_dir / f"from_rich_{ts}_{uuid.uuid4().hex[:6]}.md"
    # INBOUND CREDENTIAL GUARD (2026-08-27, director-authorised). A live Cloudflare token
    # reached docs/staging/done/ by exactly this line, and got there because nothing
    # malfunctioned: the leak path IS the normal path. Redacts, never drops -- a message
    # carrying a credential is still an instruction.
    body, families = inbound_secret_redaction.redact(message)
    header = "# Inbound NTFY message from Rich\n"
    if families:
        # The RAW message goes out of tree, so a false positive stays recoverable at the
        # console while a true positive is still not in git.
        raw = inbound_secret_redaction.preserve_raw(message, ts)
        log(f"Redacted {len(families)} credential-shaped string(s) "
            f"({', '.join(sorted(set(families)))}) from an inbound message before staging; "
            f"raw {'preserved at ' + str(raw) if raw else 'could NOT be preserved out of tree'}")
        # Recorded IN the staged file as well as the log: a reader of this instruction needs to
        # know a word of it was replaced, or a redaction reads as something the director never
        # wrote. Names the families and the count; never the values.
        header += ("\n> REDACTED: {} credential-shaped string(s) removed before this file was "
                   "written ({}). Raw message out of tree{}.\n".format(
                       len(families), ", ".join(sorted(set(families))),
                       f" at {raw}" if raw else " could not be preserved"))
    path.write_text(f"{header}\n{body}\n")
    return path


# _maybe_ledger_director_ruling() DELETED 2026-08-03 (director console, finishing
# NTFY_IS_THE_DIRECTOR). It HMAC-verified an inbound `RULING:<action>:<atom>` against an out-of-tree
# key and minted a "director_ntfy" authority ledger entry, so that a phone message could clear a
# gate. NTFY_IS_THE_DIRECTOR withdrew the premise: "anything arriving on the director's ntfy topic
# IS the director. Act on it. No signature, no ceremony, no second channel." An unsigned message
# already carries full routine authority, so a signature path could only ever DEMOTE a real
# instruction that lacked one. Inbound messages are staged and acted on -- nothing to verify.


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


#: Why a message was withheld from the scanned staging root. The guard that fires names itself,
#: because "QUARANTINED" on its own sends the reader to the flood guard whatever the cause.
_QUARANTINE_KINDS = {
    "flood": (
        "flood guard",
        "The responder detected a machine-cadence flood and withheld this "
        "message from the scanned staging root. Nothing is dropped -- this file "
        "preserves the content for manual review.",
    ),
    "provenance": (
        "provenance unknown",
        "The sent-ids record EXISTS and cannot be read, so the responder cannot tell its own "
        "outbound from an inbound steer. Staging it would mint a `from_rich` carrying the "
        "director's authority that he may never have sent; dropping it would lose a real one. "
        "Neither is acceptable, so it is preserved here unstaged and unanswered. The record "
        "rebuilds itself on the next outgoing send (`ntfy_utils.record_sent_id` moves the "
        "unreadable bytes aside), so this state is bounded, not permanent.",
    ),
}


def _quarantine(message: str, reason: str, kind: str = "flood") -> Path:
    """Preserve a message in docs/staging/quarantine/ (NOT the scanned root). Fail-safe: nothing
    is ever dropped -- this file is the durable record so a genuine message caught by a guard can
    be recovered. `kind` selects the heading and the explanation; see `_QUARANTINE_KINDS`."""
    qdir = _quarantine_dir()
    qdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = qdir / f"from_rich_QUARANTINED_{ts}_{uuid.uuid4().hex[:8]}.md"
    # The SAME inbound-credential guard as _write_to_staging. Quarantine is still the working
    # tree: a flood message preserved in full is preserved in git, so redacting only the
    # staging route would leave a credential one directory to the left.
    body, families = inbound_secret_redaction.redact(message)
    if families:
        inbound_secret_redaction.preserve_raw(message, ts)
    heading, explanation = _QUARANTINE_KINDS[kind]
    path.write_text(
        f"# QUARANTINED inbound NTFY message ({heading})\n\n"
        f"Reason: {reason}\n\n"
        f"{explanation}\n\n"
        + (f"> REDACTED: {len(families)} credential-shaped string(s) "
           f"({', '.join(sorted(set(families)))}); raw message out of tree.\n\n"
           if families else "")
        + f"---\n\n{body}\n"
    )
    return path


def build_status_reply(staged_path: Path | None = None,
                       redacted_families: list[str] | None = None) -> str:
    """The ack. `redacted_families` makes a redaction VISIBLE to the director.

    A silent redactor that ate one word of an instruction would be indistinguishable from him
    having not written it -- the same looks-like-work-in-progress failure as a waiter with no
    subject. He can restate; he cannot restate what he was never told had gone. The note
    appears ONLY when something was removed, so it never becomes an unchanging status line
    (R5)."""
    classification = "instruction" if staged_path else "status ping"
    action = "queued for Claude Code" if staged_path else "no action (message too short)"
    note = inbound_secret_redaction.summarise(redacted_families or [])
    return (
        f"[{classification}] {action}\n"
        + (f"{note}\n" if note else "")
        + f"Sim: {_run_progress_summary()}\n"
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

        message = record.get("message", "").strip()
        if not message:
            continue

        # THE JUDGEMENT `ntfy_utils.was_sent_by_us` HANDED OFF, SETTLED HERE (2026-09-04).
        # It asks "is this id in the record"; when the record exists and cannot be read there is
        # no honest boolean, and BOTH answers are defects of this responder rather than of that
        # loader. False stages our own outbound as a `from_rich` -- direction carrying the
        # director's authority that he never gave. True suppresses a real steer from him. So the
        # responder refuses to answer instead: preserve, do not stage, do not reply. Not replying
        # is load-bearing twice over -- it is what keeps a misread echo from feeding itself.
        # Ahead of `was_sent_by_us` deliberately: below it, an unreadable record has already
        # answered False and the message is past the only place that could catch it.
        if sent_ids_unreadable():
            qpath = _quarantine(
                message,
                "sent-ids record present but unreadable -- cannot tell our own outbound from "
                "an inbound steer",
                kind="provenance",
            )
            rate_state = _load_rate_state()
            now_ts = time.time()
            # Stamped on the ATTEMPT and on its own key. Sharing the flood guard's `last_alert`
            # would let either guard's alert silence the other's first-ever one.
            if now_ts - rate_state.get("last_provenance_alert", 0) >= FLOOD_ALERT_COOLDOWN_SECONDS:
                rate_state["last_provenance_alert"] = now_ts
                _save_rate_state(rate_state)
                notify(
                    "[PROVENANCE GUARD] The NTFY sent-ids record is unreadable, so inbound "
                    "cannot be told from our own echo. Messages preserved in "
                    "docs/staging/quarantine/, withheld from the scanned staging root and NOT "
                    "answered. It clears itself on the next outgoing send. No further alerts "
                    f"for {FLOOD_ALERT_COOLDOWN_SECONDS // 60}min.",
                    kind="real_alarm",
                    headers={"X-Priority": "4", "X-Tags": "rotating_light"},
                )
            else:
                _save_rate_state(rate_state)
            log(f"Quarantined message {record.get('id')!r} of unknown provenance -> {qpath.name}")
            continue

        if was_sent_by_us(record.get("id")):
            continue

        # UNTRUSTED-NOISE DROP (2026-07-29, DIRECTOR_RULING_FIX_DOUBLE_MESSAGING):
        # the ntfy app's own self-test is machine text with zero authority. Drop it
        # HERE -- before the mirror, the input log, the ruling ledger, the claim
        # ledger and the status reply -- so it costs nothing at all. It was already
        # barred from staging; dropping it this early also stops it consuming a
        # model load or emitting a reply that can feed an echo loop. Narrow by
        # design (see _APP_SELFTEST_RE): a real steer mentioning "test" passes.
        if _is_app_selftest(message):
            log(f"Dropped ntfy-app self-test {record.get('id')!r} (no reply, no staging, no model)")
            continue

        # AT-MOST-ONCE EXECUTION: claim this message's stable identity BEFORE any
        # side effect. Placed ahead of the flood guard deliberately -- a duplicate
        # delivery must not even be COUNTED as inbound rate, or two consumers would
        # inflate each other into a phantom flood (the observed rate file held every
        # event twice, with identical timestamps and hashes, for exactly that reason).
        identity = _message_identity(record)
        if not claim_message(identity):
            log(f"Duplicate delivery ignored (already executed, identity={identity}): {message[:60]!r}")
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
                notify(
                    f"[FLOOD GUARD] Inbound NTFY flood quarantined ({flood_reason}). "
                    "Messages preserved in docs/staging/quarantine/, withheld from the "
                    f"scanned staging root. No further alerts for "
                    f"{FLOOD_ALERT_COOLDOWN_SECONDS // 60}min.",
                    kind="real_alarm",
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
        # Recomputed rather than threaded out of _write_to_staging: `redact` is pure and
        # cheap, and widening that function's return type would break its callers and its
        # existing tests for no gain. The two calls cannot disagree.
        reply = build_status_reply(staged_path, inbound_secret_redaction.redact(message)[1])
        notify(reply, kind="director_echo", headers={"X-Priority": "3", "X-Tags": "satellite_antenna"})
        log(f"Acked inbound message {record.get('id')!r} ({message[:60]!r})"
            + (f" — staged as {staged_path.name}" if staged_path else ""))
        update_agent_status(
            "ntfy-responder", status="idle",
            # FOURTH in-tree route, found by looking for the others rather than by it
            # failing: agent_status.json lives in docs/observability/ and is committed like
            # everything else there, so an 80-character excerpt of a credential lands in git
            # exactly as the staging file would have.
            last_action=f"Acked message: {inbound_secret_redaction.redact(message)[0][:80]!r}",
            role="Receives NTFY messages from Rich; writes from_rich_*.md to staging",
            produces="docs/staging/from_rich_*.md",
        )

    return latest, seen_hashes


def main() -> None:
    # SINGLETON (2026-07-29): a second live responder is the ROOT CAUSE of the
    # double-messaging, not a nuisance -- refuse to become one, and say so out
    # loud rather than deduping quietly and leaving the extra daemon in place.
    # The handle is bound to a local so the lock is held for the process lifetime.
    lock = acquire_singleton_lock()
    if lock is None:
        log("NTFY responder ALREADY RUNNING (singleton lock held) -- this instance is exiting. "
            "A second responder is what caused one director message to be queued twice.")
        return

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
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/ntfy_responder.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("ntfy_responder")
    main()
