#!/usr/bin/env python3
"""
REUSE: tools/console_instruction_record.py
CLASS: CUSTOM
INDEX: searched "director input", "console", "transcript", "staging record", "from_rich".
       Three rows are close and none of them covers the console.
       `background/ntfy_responder.py` writes every INBOUND NTFY message to
       `docs/staging/from_rich_TIMESTAMP.md`. That is exactly the mechanism this needs and it
       is deliberately NOT extended: it is a listener on a network topic, and the console is
       not a topic. Its OUTPUT SHAPE is copied on purpose, so a console record and an ntfy
       record look alike to every reader and to `pull_forward_proposal.director_sources`.
       `background/director_input_log.py` logs inputs to the PRIVATE ops repo, channel-tagged
       and HMAC-verified. It is the audit trail, not a director source: nothing in
       `DIRECTOR_SOURCE_DIRS` reads it, which is precisely why 381 sources could report silence
       while the instruction sat in that log. Left alone; this fills the gap it does not cover.
       `background/director_comments.py` holds the director's comments ON artefacts, a
       different subject.

THE DIRECTOR'S WORDS IN THE PANE, WRITTEN WHERE THE MACHINE READS.

Director instruction, 2026-08-19: "a console-only instruction is invisible to 381
director-facing sources; fix that so my words in the pane leave a trace the machine can read."

WHAT WENT WRONG, precisely, because the fix only makes sense against it. On 2026-08-19 the
director unblocked `EP6_wall_protocol_typing` in the console. Under CLAUDE.md that is full
authority. It is not a FILE, and every mechanism in this project that asks "did the director
say so?" reads files: `pull_forward_proposal.release_verdict` scanned 381 sources across
`docs/staging`, `in_progress` and `done`, found nothing, and correctly returned PENDING. A
worker tick then re-parked the atom on that evidence, also correctly. Two mechanisms behaved
perfectly and the outcome was still wrong, because the input never reached disk.

NTFY ALREADY HAD THIS SOLVED and the console did not. `ntfy_responder` writes every inbound
message to `docs/staging/from_rich_*.md`, which is why an ntfy instruction is visible to the
door and a console instruction is not. The asymmetry was invisible because the two channels are
equal in authority and unequal in evidence.

VERBATIM ONLY, AND THE LIMIT IS THE POINT. This captures the director's turns EXACTLY as typed
and does nothing else. It does NOT expand shorthand, and that is a deliberate refusal rather
than an omission: he writes "move EP1 and EP6 to build", while `release_verdict` matches on the
FULL atom id, so this record alone will not release `EP6_wall_protocol_typing`. Making it do so
would mean this module deciding which atom he meant -- putting words in his mouth and
auto-granting releases from a paraphrase, which is inventing authority, the thing CLAUDE.md
names as a defect in itself. What the capture provides is EVIDENCE. When a specific release is
needed, the agent still writes a resolution record that cites this one, and the difference from
before is that the citation now points at something on disk that the director can check.

FAIL-CLOSED, and this is the failure that matters. An unreadable transcript RAISES. It must
never write an empty record, because an empty record is indistinguishable from a director who
said nothing -- which is the exact confusion that cost EP6 a day. Silence and blindness must
never render the same.

THE RULE, 2026-09-07, the director's own words: **a session that takes director input without
capturing it is a FINDING.** Same shape as the stretch log's -- raised by `--check`, never a
refusal, because blocking a commit would not write the missing turns and would stop the work the
turns were asking for. `check()` compares this record against `.human_last_input`, the presence
hook's independent stamp of a genuine keystroke, and a director who has typed while the record
stands still is the finding. Two signals, because one signal cannot tell silence from blindness --
which is exactly how six days went missing while every reader saw a quiet director.

NOT A SECOND AUTHORITY CHANNEL. This adds no gate, no approval step, no ceremony on the
director's path (CLAUDE.md: "do not invent authority checks"). The console already carried full
authority. This only stops that authority evaporating when the pane scrolls.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

# Where the harness keeps session transcripts. DERIVED FROM THE LAUNCH DIRECTORY, never
# hardcoded, and that is the whole of the 2026-09-07 defect.
#
# The harness slugs the session's working directory to name the transcript folder: a seat
# launched from `/` writes to `~/.claude/projects/-`, one launched from the project writes to
# `~/.claude/projects/-home-rich-synthetic-enterprise`. This module had `-` baked in. On
# 2026-09-03 the seat moved under systemd, its launch directory became the project, and every
# transcript from that moment landed in the other folder. The old one still EXISTED and still
# held sixteen real transcripts, so the fail-closed guard below -- which refuses when there is
# no transcript at all -- never fired. Six days of console input were not captured and nothing
# reported anything, because a directory that has gone cold reads exactly like a director who
# has said nothing.
#
# So: derive the slug, and read the legacy folder too rather than orphaning what it holds.
def _slug(path: Path) -> str:
    """The harness's transcript-folder name for a working directory."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


LEGACY_TRANSCRIPT_DIRS = (Path.home() / ".claude" / "projects" / "-",)

TRANSCRIPT_DIR = Path(os.environ.get(
    "SE_TRANSCRIPT_DIR",
    str(Path.home() / ".claude" / "projects" / _slug(Path(__file__).resolve().parents[1]))))


def transcript_dirs() -> list[Path]:
    """Every folder that could hold this project's transcripts, newest-relevant first.

    The union, not a choice: the legacy folder holds real history and the derived one holds
    everything since the launch directory changed. Reading only one is what broke.
    """
    seen, out = set(), []
    for d in (TRANSCRIPT_DIR, *LEGACY_TRANSCRIPT_DIRS):
        if d.is_dir() and str(d) not in seen:
            seen.add(str(d))
            out.append(d)
    return out


#: Where the presence hook stamps a genuine human keystroke. This is the ONLY signal in the tree
#: that says "the director is at the console right now", and comparing it against the newest
#: captured turn is what turns a silent lapse into a finding.
HUMAN_PRESENCE_STAMP = PROJECT_DIR / "docs" / "observability" / ".human_last_input"

#: How far the newest captured turn may lag the newest human keystroke before that is a finding.
#: Twelve hours, not minutes: a capture writes when the director TYPES, so a quiet night is not
#: a lapse, and a day in which he spoke and nothing was written is.
CAPTURE_LAG_FINDING_HOURS = 12.0

# Turns the harness injects into the user role that are NOT the director speaking. Each is a
# real prefix observed in the live transcript, not a guess.
# NOTE the shape: `<local-command-...>` is matched by PREFIX, not enumerated. The first draft
# listed `<local-command-caveat>` literally and shipped a record whose opening turn was
# `<local-command-stdout>Auto-compact window set to auto` -- harness output quoted as the
# director's words, in a file the release door reads. Enumerating a family one member at a time
# is how the next member gets through.
_NOT_THE_DIRECTOR = (
    "<local-command-",
    "<command-name>",
    "<command-message>",
    "<command-args>",
    "<system-reminder>",
    "[SYSTEM NOTIFICATION",
    "<task-notification>",
    "Caveat:",
)
#: Prompts the MACHINE injects into the user role. These are not the harness quoting itself
#: (that is `_NOT_THE_DIRECTOR` above) -- they are whole turns a daemon writes to drive a
#: session, and they are the reason this module must never classify a transcript after the
#: fact. Measured 2026-09-07: an interactive seat, an autonomous worker tick and a delivery-seat
#: dispatch all record `userType: "external"`, the same cwd and the same version. THERE IS NO
#: STRUCTURAL DIFFERENCE between the director speaking and a daemon speaking; only the text
#: differs, and matching text is the enumeration this module already warns about elsewhere.
#: Kept as a floor for the scanning path, never as the mechanism -- the mechanism is the
#: UserPromptSubmit hook, which classifies at the one moment the answer is actually known.
DAEMON_PROMPT_MARKERS = (
    "[SUPERVISOR:",
    "[AUTONOMOUS",
    "Session resuming after crash or usage-limit reset",
    "You are the autonomous worker",
    "You hold the DELIVERY SEAT",
    "You are the delivery seat",
    "Worker seat (re)started",
)

_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


#: Credential shapes redacted before anything is written. GitHub push protection caught a live
#: Cloudflare API token in a console record on 2026-09-07 -- the director had pasted it into the
#: pane, the capture recorded it verbatim, and the backfill carried it into a file bound for a
#: remote. Nothing was published; the block is what stopped it.
#:
#: A VERBATIM CAPTURE OF A HUMAN'S TYPING WILL EVENTUALLY CONTAIN A SECRET. That is a property of
#: the channel, not an accident, so redaction belongs here rather than in a reviewer's attention.
#: The marker is left in place on purpose: a turn that silently loses a span reads as a turn he
#: never typed, which is the confusion this whole module exists to remove.
_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    # A credential NAMED as one, whatever its shape -- this is the pattern that catches the next
    # provider rather than the last one.
    # NO leading \b: the word is usually welded into a name (`CF_TOKEN`, `API_SECRET`), and the
    # connector is usually a word (`the token is ...`), so both were missed by the first draft.
    re.compile(r"(?i)(?:api[ _-]?key|secret|token|password|passwd|bearer)"
               r"[^A-Za-z0-9]{0,4}(?:is|=|:)?\s*([A-Za-z0-9_\-.]{16,})"),
    # Cloudflare-shaped: 40 chars of base64url. A 40-character HEX string is a git sha and is
    # deliberately NOT matched -- this record is full of them and redacting those would gut it.
    # High-entropy opaque strings. THREE EXCLUSIONS, each learned by a false positive that would
    # have gutted the record rather than protected it:
    #   * a 40-char HEX string is a git sha, and this record is made of them;
    #   * a UUID is a transcript FILENAME -- the first draft redacted every `Source:` provenance
    #     line in 33 files, 16 spans each, destroying the only pointer back to the source;
    #   * an underscore-separated identifier is a python path or an atom id, not a credential.
    re.compile(r"\b(?![0-9a-f]{40}\b)"
               r"(?![0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b)"
               r"(?=[A-Za-z0-9_-]*[A-Za-z])(?=[A-Za-z0-9_-]*[0-9])"
               r"(?![A-Za-z0-9]*_[A-Za-z0-9]*_)"
               r"[A-Za-z0-9_-]{32,64}\b"),
)

REDACTION = "<REDACTED: credential-shaped, removed by the console capture>"


def redact(text: str) -> str:
    """Strip credential-shaped spans from a turn before it is written.

    FAIL TOWARD REDACTING. A false positive costs one unreadable span in a record whose source
    transcript still exists; a false negative publishes a live credential to a remote.
    """
    out = text or ""
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            out = pattern.sub(lambda m: m.group(0).replace(m.group(1), REDACTION), out)
        else:
            out = pattern.sub(REDACTION, out)
    return out


def is_director_prompt(text: str) -> bool:
    """Is this turn the director speaking, rather than the harness or a daemon?

    The judgement, in one place, so the hook and the scanner cannot drift apart.
    """
    stripped = (text or "").lstrip()
    if not stripped:
        return False
    return not stripped.startswith(_NOT_THE_DIRECTOR + DAEMON_PROMPT_MARKERS)


class TranscriptUnavailable(RuntimeError):
    """The transcript could not be read. NEVER silently an empty record."""


def newest_transcript(directory: Path | None = None) -> Path:
    d = Path(directory) if directory is not None else TRANSCRIPT_DIR
    try:
        files = sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError as exc:
        raise TranscriptUnavailable(f"{d} could not be listed: {exc}") from exc
    if not files:
        raise TranscriptUnavailable(
            f"no *.jsonl transcript under {d} -- refusing to write an empty record, because "
            "an empty record reads as 'the director said nothing'"
        )
    return files[0]


def director_turns(transcript: Path) -> list[tuple[str, str]]:
    """[(iso_timestamp, verbatim_text)] for every turn the DIRECTOR typed, in order.

    Tool results and harness-injected user-role turns are excluded by shape, never by guessing
    at content: a turn carrying a `tool_result` block is machine output, and the prefixes in
    `_NOT_THE_DIRECTOR` are all harness scaffolding observed in the live file.
    """
    try:
        raw = transcript.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise TranscriptUnavailable(f"{transcript} could not be read: {exc}") from exc

    turns: list[tuple[str, str]] = []
    seen: set[str] = set()

    def _keep(stamp, text: str) -> None:
        text = _REMINDER_RE.sub("", (text or "").strip()).strip()
        # ONE JUDGEMENT, SHARED WITH THE HOOK. This used to test `_NOT_THE_DIRECTOR` only --
        # harness scaffolding -- and let DAEMON-INJECTED turns through, because until 2026-09-03
        # the folder it read held no daemon sessions and the gap was invisible. Pointed at the
        # real folder on 2026-09-07 it swept them in: 67% of that day's "director turns" and 84%
        # of the next were "You are the autonomous worker...", quoted as his words in a file the
        # release door reads as his authority. Worse than the silence it replaced.
        if not is_director_prompt(text):
            return
        text = redact(text)
        key = " ".join(text.split())
        if key in seen:
            return
        seen.add(key)
        turns.append((str(stamp or ""), text))

    for line in raw.splitlines():
        try:
            rec = json.loads(line)
        except Exception:  # noqa: BLE001 - one bad line is not a blind transcript
            continue
        kind = rec.get("type")
        # THE TURN HE TYPED BETWEEN TURNS (2026-08-25). A message sent while a turn is already
        # running is not written as a `user` record at all -- it is QUEUED, and the transcript
        # holds it as `{"type": "queue-operation", "operation": "enqueue", "content": ...}`.
        # This capture read `type == "user"` only, so the single most consequential instruction
        # of that day -- the standing mandate that created the delivery seat -- left NO trace on
        # disk while the module whose whole purpose is to leave one reported eight turns and a
        # clean run. That is the EP6 failure again, one channel over: the mechanism behaved
        # perfectly and the input never reached the file.
        #
        # DEDUPED BY TEXT, not by uuid: `enqueue` and `remove` carry the SAME content (queued,
        # then dequeued when it is delivered), and a message that also lands as a real `user`
        # record would otherwise appear twice. First occurrence wins, so the recorded timestamp
        # is when he SENT it rather than when the machine got round to it.
        if kind == "queue-operation" and rec.get("operation") == "enqueue":
            _keep(rec.get("timestamp"), rec.get("content") if isinstance(rec.get("content"), str) else "")
            continue
        if kind != "user":
            continue
        content = (rec.get("message") or {}).get("content")
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                continue
            text = " ".join(b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text")
        else:
            continue
        _keep(rec.get("timestamp"), text)
    if not turns:
        raise TranscriptUnavailable(
            f"{transcript.name} holds no director turn at all -- that is a broken read or the "
            "wrong file, not a silent director, and writing it as a record would erase the "
            "difference"
        )
    return turns


#: How far back to look for transcripts that could still hold turns for a day being written.
#: Bounded because `observe()` runs in the worker loop and the transcript directory is ~75 MB
#: across fourteen files; three days covers every day this tool writes a record for.
RECENT_TRANSCRIPT_DAYS = 3.0


def recent_transcripts(directory: Path | None = None,
                       days: float = RECENT_TRANSCRIPT_DAYS) -> list[Path]:
    """Every transcript recent enough to hold a turn for a day being written, newest first.

    WHY NOT JUST THE NEWEST (2026-08-25, found while landing the queued-turn fix above). `write()`
    regenerates one record PER CALENDAR DAY from a SINGLE transcript, and there is more than one
    session per day: running this from session B rewrote `DIRECTOR_CONSOLE_2026-08-24.md`, which
    had been built from session A, and session A's three turns were simply gone. The record most
    likely to be overwritten is the one written by whichever session was not last to run -- so the
    turns that vanish are chosen by scheduling accident.

    That is this module's own founding failure with the sign flipped: it exists because the
    director's words evaporated when the pane scrolled, and it was quietly deleting them when a
    second session ran.

    ALWAYS INCLUDES THE NEWEST, whatever its mtime, so a machine with an odd clock still gets the
    live session. Unreadable entries are skipped here and surface as a raise downstream if NOTHING
    is readable -- silence and blindness must never render the same.
    """
    d = Path(directory) if directory is not None else TRANSCRIPT_DIR
    newest = newest_transcript(d)
    try:
        files = sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        return [newest]
    cutoff = newest.stat().st_mtime - days * 86400.0
    keep = [p for p in files if p == newest or p.stat().st_mtime >= cutoff]
    return keep or [newest]


def director_turns_across(paths: list[Path]) -> tuple[list[tuple[str, str]], list[str]]:
    """([(ts, text)] merged across transcripts in timestamp order, [transcript names used]).

    DEDUPED BY TEXT, exactly as within one transcript: the same instruction can appear in two
    sessions (a resumed session replays context), and recording it twice would read as the
    director having said it twice.
    """
    merged: dict[str, tuple[str, str]] = {}
    used: list[str] = []
    for path in paths:
        try:
            turns = director_turns(path)
        except TranscriptUnavailable:
            # A transcript with no director turn is not a failure HERE -- it is a session he
            # never spoke in. It only fails when NOTHING readable holds a turn (below).
            continue
        used.append(path.name)
        for ts, text in turns:
            key = " ".join(text.split())
            if key not in merged or (ts and ts < merged[key][0]):
                merged[key] = (ts, text)
    if not merged:
        raise TranscriptUnavailable(
            "no transcript in the recent window holds a director turn -- that is a broken read, "
            "not a silent director, and writing it as a record would erase the difference"
        )
    return sorted(merged.values(), key=lambda row: row[0]), sorted(used)


def by_day(turns: list[tuple[str, str]]) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {}
    for ts, text in turns:
        out.setdefault((ts or "unknown")[:10], []).append((ts, text))
    return out


def render(day: str, turns: list[tuple[str, str]], transcript_name: str) -> str:
    lines = [
        "**Severity:** RECORDED · **Lane:** H_harness",
        "",
        f"# Director console — verbatim record, {day}",
        "",
        "> **The director did not write or stage this file. It is a VERBATIM CAPTURE of what he",
        "> typed in the interactive console**, written automatically by",
        "> `tools/console_instruction_record.py` so that his words leave a trace the machine can",
        "> read. Under CLAUDE.md the console already carries full authority; what it did not carry",
        "> was EVIDENCE, and on 2026-08-19 that cost `EP6_wall_protocol_typing` a wrongful re-park",
        "> after 381 director-facing sources correctly reported silence.",
        ">",
        "> **Quoted exactly, never paraphrased, never expanded.** Shorthand is left as shorthand:",
        "> \"move EP1 and EP6 to build\" is recorded as written, so this file does NOT by itself",
        "> release `EP6_wall_protocol_typing` — the release door matches full atom ids. Resolving",
        "> shorthand to an atom is a judgement, and it belongs in a separate record that cites",
        "> this one, not in an automatic capture that would be putting words in his mouth.",
        "",
        f"Source: `{transcript_name}` · {len(turns)} turn(s).",
        "",
    ]
    for ts, text in turns:
        lines.append(f"### {ts}")
        lines.append("")
        for para in text.split("\n"):
            lines.append(f"> {para}" if para.strip() else ">")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write(directory: Path | None = None, staging: Path | None = None,
          days: float = RECENT_TRANSCRIPT_DAYS) -> list[Path]:
    """Write one record per calendar day. Idempotent: a day whose content is unchanged is not
    rewritten, so this can run every worker cycle without churning the tree.

    MERGES, NEVER REGENERATES, and that is not tidiness -- it is the difference between a
    backstop and a shredder. This function only reads transcripts modified in the last
    `RECENT_TRANSCRIPT_DAYS` days, so a day whose transcripts have aged out regenerates from
    NOTHING. Run on 2026-09-07 it rewrote the 2026-09-03 record from 22,907 bytes to 10,592,
    silently deleting turns it could no longer see -- a capture destroying the very evidence it
    exists to keep, in the same hour it was being repaired for losing six days.

    So the union wins: turns already on disk are kept, new ones are added, and dedup is by text
    exactly as within a transcript. A turn can only leave this record by a human deleting it.
    """
    all_turns, used = director_turns_across(recent_transcripts(directory, days))
    out_dir = Path(staging) if staging is not None else STAGING_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for day, turns in by_day(all_turns).items():
        path = record_path(day, staging)
        merged, seen = [], set()
        for stamp, text in turns_in_record(path) + turns:
            key = " ".join(text.split())
            # Keep an EXISTING daemon misattribution out on the way back in: a record written
            # before the filter was wired holds turns that were never his, and merging must not
            # preserve them just because they are already on disk.
            if key in seen or not is_director_prompt(text):
                continue
            seen.add(key)
            merged.append((stamp, text))
        merged.sort(key=lambda pair: pair[0])
        body = render(day, merged, ", ".join(used))
        # WRITE INTO THE ROOM THAT ALREADY HOLDS IT (2026-08-25). Reaching back across several
        # days means most of them have already been read and archived, and re-creating their
        # record in the staging ROOT would ring a doorbell for a turn that was actioned days ago
        # -- and leave the same document in two rooms making mutually exclusive claims, which
        # `background/finding_classes.py` refuses by name. An archived day's record still gets
        # richer as more transcripts are merged; it just does not come back to life.
        if path.exists() and path.read_text(encoding="utf-8") == body:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        written.append(path)
    return written


def turns_in_record(path: Path) -> list[tuple[str, str]]:
    """[(stamp, verbatim text)] already recorded in a file -- the inverse of `render`.

    Needed because `write()` must MERGE rather than regenerate; see its docstring.
    """
    if not path.is_file():
        return []
    out: list[tuple[str, str]] = []
    for chunk in re.split(r"^### ", path.read_text(encoding="utf-8"), flags=re.M)[1:]:
        lines = chunk.split("\n")
        stamp = lines[0].strip()
        body = "\n".join(line[2:] if line.startswith("> ") else "" for line in lines[1:])
        if body.strip():
            out.append((stamp, body.strip()))
    return out


def record_path(day: str, staging: Path | None = None) -> Path:
    """Where this day's record lives -- ONE resolution, used by the live hook and the scan.

    AN EXISTING COPY WINS, in `done/` then `console/` then the root, so a day already archived is
    appended to in place rather than resurrected into a second room -- two rooms holding one
    document is what `background/finding_classes.py` refuses by name, and it is what these two
    writers did to 2026-09-03 before this helper existed.

    A NEW day lands in the ROOT, deliberately. Filing it straight into `console/` looked tidier
    and was wrong: the root is where the doorbell reads, so a fresh instruction that skips it is
    an instruction nothing wakes up for -- which is most of what this module exists to prevent.
    `staging_migrate_rooms` moves it to `console/` afterwards, and that is the established flow.
    """
    out_dir = Path(staging) if staging is not None else STAGING_DIR
    name = f"DIRECTOR_CONSOLE_{day}.md"
    for candidate in (out_dir / "done" / name, out_dir / "console" / name, out_dir / name):
        if candidate.exists():
            return candidate
    return out_dir / name


def append_turn(stamp: str, text: str, staging: Path | None = None) -> Path | None:
    """Append ONE director turn to today's record, at the moment he types it.

    THIS IS THE MECHANISM; `write()` is the backstop. Scanning transcripts afterwards cannot
    tell the director from a daemon -- measured 2026-09-07, both record `userType: "external"`
    with identical cwd and version -- so the only place the answer is reliably known is the
    prompt-submit hook, where the turn arrives on its own with the session's own identity around
    it. Capture there and the classification problem does not arise.

    Idempotent on an exact repeat, so a retried hook cannot double-write. Returns the path when
    it wrote, None when the turn was already there or was not the director's.
    """
    if not is_director_prompt(text):
        return None
    text = redact(text)
    day = (stamp or "")[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise ValueError(f"refusing to file a turn under {day!r}; a record needs its real day")
    path = record_path(day, staging)

    body = "\n".join([f"### {stamp}", ""]
                     + [f"> {line}" if line.strip() else ">" for line in text.split("\n")]
                     + [""])
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if body.strip() in existing:
            return None
        path.write_text(existing.rstrip() + "\n\n" + body, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        # The live header cannot carry a turn COUNT -- the file grows one submission at a time,
        # so any number written at creation is wrong by the second turn. Replaced rather than
        # left at "0 turn(s)", which would read as a record of a director who said nothing.
        header = render(day, [], "captured live at the console").rstrip()
        header = header.replace("Source: `captured live at the console` · 0 turn(s).",
                                "Captured live at the console, one turn per submission, by "
                                "`.claude/hooks/capture_director_console.py`.")
        path.write_text(header + "\n\n" + body, encoding="utf-8")
    return path


def reply_path(day: str, staging: Path | None = None) -> Path:
    """Where the seat's replies for one day live -- beside the turns they answer.

    A SEPARATE DOCUMENT, not a section of the console record, and the separation is the point.
    `pull_forward_proposal.director_sources` reads DIRECTOR_CONSOLE_* as the director's own words.
    Putting the seat's replies in that file would hand a release door the machine's words carrying
    his authority -- the same defect that let daemon prompts into this record earlier today, one
    step further along. Same room, same day, same redaction, different name.
    """
    out_dir = Path(staging) if staging is not None else STAGING_DIR
    name = f"SEAT_REPLY_{day}.md"
    for candidate in (out_dir / "done" / name, out_dir / "console" / name, out_dir / name):
        if candidate.exists():
            return candidate
    # STRAIGHT INTO THE ROOM, unlike a director turn, and the asymmetry is the point. A new
    # DIRECTOR_CONSOLE day lands in the staging ROOT because the root is where the doorbell reads
    # and a fresh instruction is something a session must wake up for. NOBODY HAS TO ACTION THE
    # SEAT'S OWN WORDS. Filing them in the root would ring a doorbell for a document with no ask
    # in it and add a document a day to a queue whose own sediment check already reports filing
    # outrunning dispositioning by +155 over seven days.
    return out_dir / "console" / name


def _reply_header(day: str) -> str:
    return "\n".join([
        "**Severity:** RECORDED · **Lane:** H_harness",
        "",
        f"# The seat's replies — verbatim record, {day}",
        "",
        "> **These are the DELIVERY SEAT's words, not the director's.** The companion file",
        f"> `DIRECTOR_CONSOLE_{day}.md` holds what he typed; this holds what was said back, so a",
        "> reader arriving at an instruction can see the answer without waiting for a stretch",
        "> report to close. Director, 2026-09-07: *\"it records what I send and not what you reply",
        "> ... between the two there's a window where my advisor can see the instruction and not",
        "> the answer.\"*",
        ">",
        "> **Nothing here carries the director's authority.** It is kept under a separate name for",
        "> exactly that reason: the release door reads `DIRECTOR_CONSOLE_*` as his own words, and",
        "> a reply filed under that prefix would be the machine speaking with his voice.",
        "",
    ])


def append_reply(stamp: str, text: str, staging: Path | None = None) -> Path | None:
    """Append ONE seat reply, at the moment the turn ends. Idempotent on an exact repeat.

    Redacted on the same terms as a director turn: the seat quotes tokens, paths and occasionally
    a secret the director pasted, and a reply record is bound for the same published tree.
    """
    if not (text or "").strip():
        return None
    text = redact(text)
    day = (stamp or "")[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise ValueError(f"refusing to file a reply under {day!r}; a record needs its real day")
    path = reply_path(day, staging)
    body = "\n".join([f"### {stamp}", ""]
                     + [f"> {line}" if line.strip() else ">" for line in text.split("\n")]
                     + [""])
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if body.strip() in existing:
            return None
        path.write_text(existing.rstrip() + "\n\n" + body, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_reply_header(day) + "\n" + body, encoding="utf-8")
    return path


def _newest_captured_day(staging: Path | None = None) -> str | None:
    out_dir = Path(staging) if staging is not None else STAGING_DIR
    days = []
    # ALL THREE ROOMS. The first draft globbed the root and `done/` and missed `console/` --
    # which is where `record_path` actually files them -- so the control reported a four-day
    # lapse over records that were sitting on disk. A check that reads a different directory
    # from the writer is the very defect this module was being repaired for, reproduced inside
    # its own guard within the hour.
    for d in (out_dir, out_dir / "console", out_dir / "done"):
        if d.is_dir():
            days += [m.group(1) for p in d.glob("DIRECTOR_CONSOLE_*.md")
                     if (m := re.search(r"(\d{4}-\d{2}-\d{2})", p.name))]
    return max(days) if days else None


def check(staging: Path | None = None, now: float | None = None) -> tuple[int, str]:
    """A capture that has stopped must say so. Returns (0, ok) or (1, why it is a finding).

    THE DEFECT THIS EXISTS FOR: on 2026-09-03 the transcript folder went cold and every reader
    of this record saw a director who had said nothing. Silence and blindness rendered the same,
    which is the failure the module docstring says it refuses -- it refused it for an UNREADABLE
    transcript and not for a STALE one, and stale is the state that actually occurred.

    So the control compares two independent signals: `.human_last_input`, stamped by the
    presence hook on every genuine keystroke, against the newest day this record holds. The
    director typing while the record stands still is exactly the lapse, and it is the one
    comparison nothing in the tree was making.
    """
    import time

    now = time.time() if now is None else now
    if not HUMAN_PRESENCE_STAMP.is_file():
        return 1, (f"{HUMAN_PRESENCE_STAMP} is absent, so there is no independent signal that the "
                   "director is at the console and this record cannot be shown to be current. "
                   "That is a finding, not an all-clear.")
    try:
        last_human = float(HUMAN_PRESENCE_STAMP.read_text(encoding="utf-8").strip())
    except (OSError, ValueError) as exc:
        return 1, f"{HUMAN_PRESENCE_STAMP} is unreadable ({exc}); cannot show the capture is live."

    captured = _newest_captured_day(staging)
    if captured is None:
        return 1, "no DIRECTOR_CONSOLE record exists at all, and the director has been present."

    human_day = time.strftime("%Y-%m-%d", time.localtime(last_human))
    lag_h = (last_human - time.mktime(time.strptime(captured + " 23:59", "%Y-%m-%d %H:%M"))) / 3600
    if lag_h > CAPTURE_LAG_FINDING_HOURS:
        return 1, (
            f"CONSOLE CAPTURE HAS LAPSED: the director last typed on {human_day} and the newest "
            f"captured turn is {captured} -- {lag_h / 24:.1f} day(s) of console input with no "
            f"record. Two independent signals disagree, which is the only way this is visible; "
            f"a cold transcript folder reads exactly like a director who said nothing. "
            f"Reading: {', '.join(str(d) for d in transcript_dirs()) or 'NO transcript folder'}.")
    # THE OTHER HALF OF THE PAIR. A day that holds his turns and no replies is the same lapse one
    # channel over -- the advisor sees the instruction and not the answer, which is the window the
    # director named. Checked against the RECORD rather than against a clock, because a reply is
    # owed per day of conversation and not per elapsed hour.
    out_dir = Path(staging) if staging is not None else STAGING_DIR
    if turns_in_record(record_path(captured, staging)) and not turns_in_record(
            reply_path(captured, staging)):
        return 1, (
            f"THE SEAT'S SIDE IS MISSING for {captured}: that day's DIRECTOR_CONSOLE record holds "
            f"turns and its SEAT_REPLY record holds none, so a reader sees the instruction and not "
            f"the answer. Either the Stop hook is not firing or it is writing somewhere this does "
            f"not read. Looked in {out_dir}, {out_dir / 'console'} and {out_dir / 'done'}.")

    return 0, (f"console capture current: last keystroke {human_day}, newest record "
               f"{captured}, and that day carries both sides of the conversation.")


def observe() -> dict:
    """Worker-loop entry point, shaped like the headroom governors so it joins that loop.

    R5: reports only when a record actually changed, so a quiet session logs nothing.
    """
    try:
        written = write()
    except TranscriptUnavailable as exc:
        return {"changed": True, "alarm": f"CONSOLE RECORD UNAVAILABLE: {exc}"}
    if not written:
        return {"changed": False}
    return {"changed": True, "verdict": f"{len(written)} record(s) updated",
            "written": [str(p.relative_to(PROJECT_DIR)) for p in written]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--write", action="store_true", help="write the console record(s)")
    ap.add_argument("--backfill", metavar="DAYS", type=float,
                    help="widen the transcript window to recover days that have aged out; "
                         "pair with --from-dir to keep the read bounded")
    ap.add_argument("--from-dir", metavar="PATH",
                    help="read only this transcript folder (a backfill over every folder is "
                         "gigabytes; a folder that has gone cold is small and is usually the one "
                         "holding the missing days)")
    ap.add_argument("--check", action="store_true",
                    help="refuse if the capture has lapsed (compares .human_last_input)")
    args = ap.parse_args(argv)
    if args.check:
        code, message = check()
        print(message)
        return code
    if args.backfill:
        written = write(directory=Path(args.from_dir) if args.from_dir else None,
                        days=args.backfill)
        print(f"backfill merged {len(written)} record(s): "
              + (", ".join(str(w.relative_to(PROJECT_DIR)) for w in written) or "no change"))
        return 0
    try:
        if args.write:
            written = write()
            print(f"wrote {len(written)} record(s): "
                  + ", ".join(str(p.relative_to(PROJECT_DIR)) for p in written)
                  if written else "no change -- records already current")
            return 0
        turns = director_turns(newest_transcript())
        print(f"{len(turns)} director turn(s) across {len(by_day(turns))} day(s)")
        for day, t in sorted(by_day(turns).items()):
            print(f"  {day}: {len(t)} turn(s)")
    except TranscriptUnavailable as exc:
        print(f"CONSOLE RECORD UNAVAILABLE: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
