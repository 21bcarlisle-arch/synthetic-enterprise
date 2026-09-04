"""The weekly rhythm: Monday sets the ranking, Friday reviews it, each armed by the one before.

DIRECTOR, 2026-09-04: *"The mothball audit has sat parked since late July. It has no trigger and no
schedule — nothing draws it, so it runs only when I remember. The pruning ritual and the decay audit
are the same. Meanwhile the drain outranks them every week, because a pile that is visibly growing
always looks more urgent than an audit that has never fired. That is a mechanism problem, not a
priority problem."*

WHAT THIS IS NOT, because that is most of the design. It is not a queue, a ranker, an executor, a
scheduler or a second direction record. Every one of those already exists and the rituals decayed
anyway, so adding another would be the shape this repo has paid for most often — 117 harness atoms
and 34 alarm documents. The whole mechanism is ONE BATON and ONE DUE CHECK, and it borrows
everything else:

  * THE CLOCK is `daily-self-note.timer`: `OnCalendar=*-*-* 07:00:00`, `Persistent=true`. systemd's
    calendar is LOCAL time, so it is already the director's Monday and not a UTC one, and Persistent
    replays a tick the machine slept through. No new timer.
  * THE DAY is `ZoneInfo("Europe/London")`, read here and nowhere else. Never `date -d`, which
    resolves BST to *Bangladesh* Standard Time (UTC+6) and put a five-hour error on a live page
    twice this week. Between 23:00 and 00:00 UTC in summer the London date is already tomorrow, so
    a UTC day would fire Monday's step on Sunday night.
  * THE QUEUE is `docs/staging/`, whose root is RUNG 1 in the supervisor's own ladder — above the
    dial-weighted lanes where new feature work lives, below the priority-zero rungs where a live
    defect lives. That is exactly the band the director asked for: *"Overdue outranks new features
    ... I don't want a stale audit beating a live defect."* Nothing here re-implements that ordering.
  * THE RANKING LIVES IN MONDAY'S OWN DOCUMENT, and that is a correction to this module's first
    draft. It said to write the week's ranking into `DIRECTION.yaml`, which cannot hold one:
    `direction.FOCUS_MAX_AGE_HOURS` is 12.0, so that record is a STRETCH record, rewritten every
    few hours, and a weekly ranking placed there would have expired by Monday evening. The Monday
    document sits in the staging root all week — RUNG 1, in front of every orientation — and
    Friday's step reads it. `DIRECTION.yaml` still carries each stretch's focus and draws FROM the
    week's ranking; it does not store it.
  * A DEFERRAL is still `DIRECTION.yaml`'s `not_now`, whose validator already REFUSES an entry
    without a `what` and a `why`. "Deliberately deferred with a stated reason" was mechanised
    before this existed, and nothing here re-implements it.

THE CHAIN, which is the requirement that no step fires from the director remembering. Closing a step
is the ONLY thing that arms the next one: Monday's close arms Friday, Friday's close arms the
following Monday. There is exactly one unchained arm in the system — the bootstrap, when no baton
exists at all — and it happens once.

A STEP THAT HAS NOT FIRED IS A FINDING, filed once, at LATENT, in the lane that owns the ritual. It
is a finding about THE WORK not happening, never about this module: *"If the rhythm starts producing
findings about itself, it has failed."* So an unreadable baton is rebuilt and reported in the tick's
own output; it never mints a document.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_DIR = Path(__file__).resolve().parent.parent
BATON = PROJECT_DIR / "docs" / "observability" / ".weekly_rhythm.json"
STAGING = PROJECT_DIR / "docs" / "staging"

#: The director's own clock. His days are the anchor, not the machine's.
LONDON = ZoneInfo("Europe/London")

MONDAY, FRIDAY = 0, 4
MONDAY_STEP = "monday_ranking"
FRIDAY_STEP = "friday_review"
#: Which weekday each step falls on, and which step follows it. The chain is this dict.
STEPS = {
    MONDAY_STEP: {"weekday": MONDAY, "next": FRIDAY_STEP,
                  "title": "Monday: retrospective on the week gone, and the ranking for the week ahead"},
    FRIDAY_STEP: {"weekday": FRIDAY, "next": MONDAY_STEP,
                  "title": "Friday: what actually happened against Monday's ranking, and the adjustment"},
}

_FILENAME_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})|(\d{4})(\d{2})(\d{2})")


#: The rituals that decayed, and the evidence each leaves when it runs.
#:
#: `last_done` IS READ FROM THE ARTEFACT, never from a field anyone maintains. A hand-kept
#: "last run" date is an exhortation with a timestamp: it goes stale exactly when the ritual does,
#: and silently. Doing the ritual writes a dated document; that document IS the record.
#:
#: `every_days` is not a domain constant and is not dressed as one — it is the director's own
#: cadence for his own housekeeping, and the only claim made for it is that it is longer than a
#: week, so a ritual cannot be overdue every single Monday and become noise.
RITUALS = (
    {"id": "mothball_audit", "every_days": 90, "lane": "H_harness",
     "glob": "docs/design/MOTHBALL_*.md",
     "what": "Re-run the mothball question over the apparatus: for every gate, queue, window and "
             "reporting ritual, what is this actually for under THE STANDARD? Mothball what cannot "
             "say. Verdicts belong in a new dated docs/design/MOTHBALL_<date>.md."},
    {"id": "harness_pruning", "every_days": 60, "lane": "H_harness",
     "glob": "docs/design/HARNESS_PRUNE_*.md",
     "what": "The harness pruning ritual (HARNESS_BEST_PRACTICE_ASSESSMENT.md §6): which controls "
             "have never fired, which duplicate another, which are keyed to today's answer. "
             "Verdicts belong in a new dated docs/design/HARNESS_PRUNE_<date>.md."},
    {"id": "claude_md_decay_audit", "every_days": 45, "lane": "H_harness",
     "glob": "docs/**/*DECAY_AUDIT_*.md",
     "what": "The CLAUDE.md decay audit: which rules in CLAUDE.md are now enforced elsewhere, which "
             "have no enforcement at all, and which describe a machine that no longer exists. "
             "Findings belong in a new dated *_DECAY_AUDIT_<date>.md."},
)


def london_today(now: datetime | None = None) -> date:
    """The director's date. THE ONE CLOCK READ IN THIS MODULE.

    `datetime.now(ZoneInfo("Europe/London"))`, never a UTC date and never a parsed abbreviation.
    Both failure modes are live in this repo's record within the last week: `date -d "... BST"`
    resolves to Bangladesh (UTC+6) and put five hours of error on a published page, and comparing
    UTC filenames against local mtimes manufactured a phantom outage. In summer the London date
    rolls over an hour before the UTC one, so a UTC "today" fires Monday's step on Sunday evening.
    """
    return (now.astimezone(LONDON) if now is not None else datetime.now(LONDON)).date()


def next_weekday_after(day: date, weekday: int) -> date:
    """The next `weekday` STRICTLY after `day`.

    Strictly, so closing a step on its own due date cannot arm the next one for the same day, and
    so a Friday review closed late on Friday arms the following Monday rather than today.
    """
    ahead = (weekday - day.weekday()) % 7
    return day + timedelta(days=ahead or 7)


def _dates_in(glob: str) -> list[date]:
    out = []
    for path in PROJECT_DIR.glob(glob):
        m = _FILENAME_DATE.search(path.name)
        if not m:
            continue
        parts = [p for p in m.groups() if p]
        try:
            out.append(date(int(parts[0]), int(parts[1]), int(parts[2])))
        except ValueError:
            continue
    return out


def last_done(ritual: dict) -> date | None:
    """When this ritual last left evidence, or None if it never has.

    NEVER-RUN IS ITS OWN STATE and must not collapse into "done long ago". The harness pruning
    ritual has never produced an artefact at all — it was adopted and never fired — and a mechanism
    that reported it as merely stale would be describing a different, smaller problem.
    """
    dates = _dates_in(ritual["glob"])
    return max(dates) if dates else None


def overdue_rituals(today: date | None = None) -> list[dict]:
    """Which rituals are past their cadence, newest-overdue last. Each row states WHY it is overdue,
    because "never" and "83 days late" call for different sentences in the ranking."""
    today = today or london_today()
    out = []
    for ritual in RITUALS:
        done = last_done(ritual)
        if done is None:
            out.append({**ritual, "last_done": None, "days_over": None, "why": "never run"})
        elif (today - done).days > ritual["every_days"]:
            over = (today - done).days - ritual["every_days"]
            out.append({**ritual, "last_done": done.isoformat(), "days_over": over,
                        "why": f"last run {done.isoformat()}, {over} day(s) past a "
                               f"{ritual['every_days']}-day cadence"})
    out.sort(key=lambda r: (r["days_over"] is not None, r["days_over"] or 0))
    return out


PARKED = "docs/staging/in_progress"


def _readable(excerpt: str) -> str:
    """The parked note's OPEN clause, as prose. These notes sit inside HTML comments and markdown
    blockquotes, so a raw slice carries `-->` and `>` into a document a person reads."""
    text = " ".join(excerpt.split())
    for terminator in ("-->", "##", "# "):
        if terminator in text:
            text = text.split(terminator)[0]
    return text.strip(" *>-").strip()[:140]
_OPEN_NOTE = re.compile(r"\bOPEN:\s*(.{0,160})", re.S)


def parked_with_open_item(today: date | None = None, root: Path | None = None) -> list[dict]:
    """Parked work that STATED what remained, oldest first.

    THE SUBJECT IS DERIVED, NOT LISTED, and that is the whole reason this is not three hand-written
    ritual names. The director's example — the mothball audit — is not overdue on any cadence; it is
    PARKED MID-WAY, and its own parked note says so: *"OPEN: execute the MOTHBALL-verdict rows"*. A
    registry naming three rituals would have missed it and would go stale the first time a fourth
    thing parked itself. `RITUALS` above still exists because it catches the opposite case — a
    ritual that has NEVER run leaves no artefact anywhere to find.

    AND IT IS NOT THE WHOLE ROOM. `in_progress/` holds 120 documents; surfacing all of them every
    Monday is a pile, not a rhythm, and the seat has already declined the bulk drain in
    `DIRECTION.yaml`'s `not_now` with a stated reason that still stands. The narrow signal is a
    document that said what remained and then stopped: measured 2026-09-04, that is FOUR, and the
    oldest is the one the director named. The rest of the room is reported as a count and an age,
    which makes the pile visible without dumping it into a ranking.
    """
    today = today or london_today()
    directory = (root or PROJECT_DIR) / PARKED
    out = []
    for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        try:
            head = path.read_text(errors="replace")[:1200]
        except OSError:
            continue
        note = _OPEN_NOTE.search(head)
        if not note:
            continue
        m = _FILENAME_DATE.search(path.name)
        age = None
        if m:
            parts = [p for p in m.groups() if p]
            try:
                age = (today - date(int(parts[0]), int(parts[1]), int(parts[2]))).days
            except ValueError:
                age = None
        out.append({"name": path.name, "age_days": age,
                    "open": _readable(note.group(1))})
    out.sort(key=lambda r: -(r["age_days"] or 0))
    return out


def parked_room(root: Path | None = None) -> dict:
    """How big the pile is and how old its oldest is — a measurement, never a list."""
    directory = (root or PROJECT_DIR) / PARKED
    names = sorted(directory.glob("*.md")) if directory.is_dir() else []
    ages = []
    for path in names:
        m = _FILENAME_DATE.search(path.name)
        if not m:
            continue
        parts = [p for p in m.groups() if p]
        try:
            ages.append((london_today() - date(int(parts[0]), int(parts[1]), int(parts[2]))).days)
        except ValueError:
            continue
    return {"documents": len(names), "oldest_days": max(ages) if ages else None}


def _blank(step: str, due_on: date, armed_by: str) -> dict:
    return {"step": step, "due_on": due_on.isoformat(), "armed_by": armed_by,
            "armed_at": datetime.now(LONDON).isoformat(),
            "opened_at": None, "closed_at": None, "finding_filed_for": None}


def read_baton(path: Path | None = None) -> dict | None:
    try:
        record = json.loads((path or BATON).read_text())
    except Exception:  # noqa: BLE001 -- an unreadable baton is rebuilt, never a finding
        return None
    return record if isinstance(record, dict) and record.get("step") in STEPS else None


def write_baton(record: dict, path: Path | None = None) -> None:
    target = path or BATON
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def close(step: str, now: datetime | None = None, path: Path | None = None) -> dict:
    """Record a step done, and ARM THE NEXT ONE. This is the whole chain.

    Nothing else arms a step. There is no schedule that says "Friday happens on Fridays" — Friday
    happens because Monday finished and said so, which is what makes the rhythm self-firing rather
    than a calendar somebody has to keep believing in.
    """
    today = london_today(now)
    record = read_baton(path) or _blank(step, today, "bootstrap")
    if record["step"] != step:
        raise ValueError(
            f"the rhythm is waiting on {record['step']}, not {step} -- closing a step that is not "
            "armed would silently skip the one that is")
    record["closed_at"] = datetime.now(LONDON).isoformat()
    write_baton(record, path)
    nxt = STEPS[step]["next"]
    armed = _blank(nxt, next_weekday_after(today, STEPS[nxt]["weekday"]), step)
    write_baton(armed, path)
    return armed


def _step_doc(step: str, due_on: date) -> Path:
    return STAGING / f"WEEKLY_RHYTHM_{step.upper()}_{due_on.isoformat()}.md"


def _finding_doc(step: str, due_on: date) -> Path:
    return STAGING / f"SEAT_FINDING_THE_WEEKLY_{step.upper()}_DID_NOT_FIRE_{due_on.isoformat()}.md"


def monday_document_for(friday: date, staging: Path | None = None) -> Path | None:
    """The Monday document whose week this Friday closes, or None.

    Friday's whole job is reviewing against Monday's ranking, so it must be able to FIND it. Looked
    up by the Monday date this Friday follows rather than by scanning for the newest, because a
    Friday review that ran late must still review ITS OWN week and not the one that started since.
    """
    monday = friday - timedelta(days=(friday.weekday() - MONDAY) % 7)
    candidate = (staging or STAGING) / f"WEEKLY_RHYTHM_{MONDAY_STEP.upper()}_{monday.isoformat()}.md"
    if candidate.is_file():
        return candidate
    archived = (staging or STAGING) / "done" / candidate.name
    return archived if archived.is_file() else None


def _step_body(step: str, due_on: date, overdue: list[dict]) -> str:
    lines = [f"# {STEPS[step]['title']}", "",
             f"**Due:** {due_on.isoformat()} (Europe/London). Armed by the step before it.", ""]
    if step == MONDAY_STEP:
        lines += [
            "**Write the week's ranking into the section at the foot of THIS document.** It stays "
            "in the staging root until Friday closes it, so every orientation this week meets it. "
            "It does not go in `DIRECTION.yaml`: `direction.FOCUS_MAX_AGE_HOURS` is 12.0, so that "
            "record is a stretch record and a weekly ranking placed there expires by Monday "
            "evening. Each stretch's `focus` draws FROM the ranking below; a deliberate deferral "
            "goes in that stretch's `not_now`, which already refuses an entry with no `why`.", "",
            "**Overdue outranks new feature work.** Anything below goes into `focus` unless it "
            "goes into `not_now` with a reason. It does not outrank a live defect — the "
            "priority-zero rungs still come first, which is the ordering the supervisor already "
            "applies to this queue.", ""]
    else:
        monday_doc = monday_document_for(due_on)
        where = _rel(monday_doc) if monday_doc else "NOT FOUND — say so in the review rather than "\
            "reconstructing it from memory; a review with no ranking to review is itself the finding"
        lines += [
            f"Monday's ranking for this week is in `{where}`. Read it against what actually landed, "
            "item by item, and adjust. A review that only records outcomes teaches nothing: where a "
            "ranked item did not move, say whether it was wrong to rank it or wrong to leave it.",
            ""]
    if overdue:
        lines += ["## Overdue rituals, measured from their own artefacts", ""]
        for row in overdue:
            lines.append(f"- **{row['id']}** ({row['why']}) — {row['what']}")
        lines.append("")
    else:
        lines += ["## Overdue rituals", "", "None. Every ritual is inside its cadence.", ""]

    parked = parked_with_open_item(due_on)
    room = parked_room()
    lines += ["## Parked work that stated what remained", ""]
    if parked:
        for row in parked:
            age = f"{row['age_days']}d" if row["age_days"] is not None else "undated"
            lines.append(f"- **{row['name']}** ({age}) — OPEN: {row['open']}")
    else:
        lines.append("None. Nothing parked is carrying a stated open item.")
    lines += ["",
              f"The rest of the parked room is {room['documents']} document(s), oldest "
              f"{room['oldest_days']} day(s). That is a count, deliberately, not a list: the bulk "
              "drain is already declined in `DIRECTION.yaml`'s `not_now` with a reason that still "
              "stands, and re-listing it every week would make this rhythm the noise it exists to "
              "replace.", ""]
    if step == MONDAY_STEP:
        lines += ["## The ranking for this week", "",
                  "_Written by the Monday step. Ordered. Anything above the line outranks new "
                  "feature work; nothing here outranks a live defect._", "",
                  "1. ", "2. ", "3. ", "",
                  "### Deliberately not this week, and why", "", "- ", ""]
    else:
        lines += ["## What actually happened", "",
                  "_Against Monday's ranking, item by item. Where one did not move, say whether it "
                  "was wrong to rank it or wrong to leave it._", "", "- ", ""]
    lines += ["---", "",
              "Close it with `python3 -m background.weekly_rhythm --close` in the same act that "
              "archives this file. Closing is what arms the next step; nothing else does.", ""]
    return "\n".join(lines)


def _rel(path: Path) -> str:
    """The path as a reader would type it. A test's staging room is outside the repo, and a
    diagnostic that raises on its own path formatting is the observer redding its subject."""
    try:
        return str(path.relative_to(PROJECT_DIR))
    except ValueError:
        return path.name


def _finding_body(step: str, due_on: date, today: date, overdue: list[dict]) -> str:
    late = (today - due_on).days
    names = ", ".join(r["id"] for r in overdue) or "none"
    return "\n".join([
        "**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — weekly rhythm",
        "",
        f"# The weekly {step.replace('_', ' ')} was due {due_on.isoformat()} and has not fired",
        "",
        f"**Found:** {today.isoformat()}, by `background.weekly_rhythm` on the daily 07:00 local "
        f"tick. {late} day(s) late.",
        "",
        "The director's instruction of 2026-09-04 made this a finding by construction: *\"If a step "
        "has not fired when it should have, that is a finding.\"* The step is not late because "
        "anyone forgot — it is late because it was armed, staged, and not done.",
        "",
        f"Rituals waiting on it: **{names}**.",
        "",
        "## The repair",
        "",
        f"Do the step. `{_rel(_step_doc(step, due_on))}` carries it. Then "
        "`python3 -m background.weekly_rhythm --close`, which arms the next step and is the only "
        "thing that does.",
        "",
        "**Discharged:** when the step is closed. This finding is filed ONCE per due date — the "
        "baton records that it was — so a step that stays open does not mint a document a day.",
        "",
    ])


def tick(now: datetime | None = None, path: Path | None = None, staging: Path | None = None) -> dict:
    """The daily due check. Returns what it did, and does at most one thing.

    Dispositions, all four reachable: BOOTSTRAP (no baton), WAITING (armed, not yet due), OPENED
    (due today or later, staged for the queue), FINDING (still open the day after it was due).
    """
    today = london_today(now)
    staging_dir = staging or STAGING
    record = read_baton(path)
    if record is None:
        record = _blank(MONDAY_STEP, next_weekday_after(today - timedelta(days=1), MONDAY),
                        "bootstrap")
        write_baton(record, path)
        return {"action": "BOOTSTRAP", "step": record["step"], "due_on": record["due_on"]}

    step, due_on = record["step"], date.fromisoformat(record["due_on"])
    if record.get("closed_at"):
        return {"action": "WAITING", "step": step, "due_on": record["due_on"],
                "why": "the armed step is already closed"}
    if today < due_on:
        return {"action": "WAITING", "step": step, "due_on": record["due_on"],
                "why": f"not due for {(due_on - today).days} day(s)"}

    overdue = overdue_rituals(today)
    doc = staging_dir / _step_doc(step, due_on).name
    if not record.get("opened_at"):
        staging_dir.mkdir(parents=True, exist_ok=True)
        doc.write_text(_step_body(step, due_on, overdue))
        record["opened_at"] = datetime.now(LONDON).isoformat()
        write_baton(record, path)
        return {"action": "OPENED", "step": step, "due_on": record["due_on"],
                "doc": str(doc), "overdue": [r["id"] for r in overdue]}

    if today > due_on and record.get("finding_filed_for") != record["due_on"]:
        finding = staging_dir / _finding_doc(step, due_on).name
        finding.write_text(_finding_body(step, due_on, today, overdue))
        record["finding_filed_for"] = record["due_on"]
        write_baton(record, path)
        return {"action": "FINDING", "step": step, "due_on": record["due_on"],
                "doc": str(finding), "days_late": (today - due_on).days}

    return {"action": "WAITING", "step": step, "due_on": record["due_on"],
            "why": "already open, and its finding is already filed" if record.get(
                "finding_filed_for") else "open and due today"}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tick", action="store_true", help="the daily due check")
    ap.add_argument("--close", action="store_true", help="record the armed step done and arm the next")
    ap.add_argument("--status", action="store_true", help="print the baton and the overdue rituals")
    args = ap.parse_args(argv)

    if args.close:
        record = read_baton()
        if record is None:
            print("no baton -- run --tick once to bootstrap")
            return 1
        armed = close(record["step"])
        print(f"closed {record['step']}; armed {armed['step']} for {armed['due_on']}")
        return 0
    if args.status or not args.tick:
        record = read_baton()
        today = london_today()
        print(f"today (Europe/London): {today.isoformat()} ({today.strftime('%A')})")
        print(f"baton: {record}")
        for row in overdue_rituals(today):
            print(f"  OVERDUE {row['id']}: {row['why']}")
        return 0
    print(tick())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
