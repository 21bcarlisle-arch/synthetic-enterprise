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

# Where the harness keeps session transcripts. Overridable for tests and for a machine that
# stores them elsewhere; the default is this machine's real path.
TRANSCRIPT_DIR = Path(os.environ.get(
    "SE_TRANSCRIPT_DIR", str(Path.home() / ".claude" / "projects" / "-")))

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
_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


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
    for line in raw.splitlines():
        try:
            rec = json.loads(line)
        except Exception:  # noqa: BLE001 - one bad line is not a blind transcript
            continue
        if rec.get("type") != "user":
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
        text = text.strip()
        if not text or any(text.startswith(p) for p in _NOT_THE_DIRECTOR):
            continue
        text = _REMINDER_RE.sub("", text).strip()
        if not text:
            continue
        turns.append((str(rec.get("timestamp") or ""), text))
    if not turns:
        raise TranscriptUnavailable(
            f"{transcript.name} holds no director turn at all -- that is a broken read or the "
            "wrong file, not a silent director, and writing it as a record would erase the "
            "difference"
        )
    return turns


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


def write(directory: Path | None = None, staging: Path | None = None) -> list[Path]:
    """Write one record per calendar day. Idempotent: a day whose content is unchanged is not
    rewritten, so this can run every worker cycle without churning the tree."""
    transcript = newest_transcript(directory)
    out_dir = Path(staging) if staging is not None else STAGING_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for day, turns in by_day(director_turns(transcript)).items():
        body = render(day, turns, transcript.name)
        path = out_dir / f"DIRECTOR_CONSOLE_{day}.md"
        if path.exists() and path.read_text(encoding="utf-8") == body:
            continue
        path.write_text(body, encoding="utf-8")
        written.append(path)
    return written


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
    args = ap.parse_args(argv)
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
