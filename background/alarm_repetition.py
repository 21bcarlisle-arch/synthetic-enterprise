#!/usr/bin/env python3
"""A repeating alarm becomes work, instead of becoming another message.

REUSE: background/alarm_repetition.py
CLASS: CUSTOM
INDEX: searched "dedup", "repeat", "escalat", "alarm", "transition", "suppress".
       `background/notify.py` is the nearest analogue and is REUSED WHOLE -- this is called
       from inside its transition block, not built beside it, and the threshold constants are
       imported from here rather than redeclared there. `background/notification_digest.py`
       batches by topic_class to cut VOLUME, which is a different question from "this is the
       same condition firing again"; a digest of six identical pages is still six identical
       pages. `background/self_clearing_alarm_census.py` measures alarms that clear themselves;
       this handles the ones that do not.

DIRECTOR INSTRUCTION, 2026-08-20: *"the alerts repeated identically all night. Both are the
repetition problem we agreed is a symptom, not an event. Fix the failures, and make a
repeating alert escalate itself into the draw instead of re-telling me."*

WHAT ACTUALLY HAPPENED, MEASURED
--------------------------------
The simulation producer failed six consecutive runs between 23:39Z and 00:26Z. Each failure
called `notify(..., kind="real_alarm")` from `sim_runner.py` with **no `transition_key`** --
so R5's transition-only rule, the whole point of the notify contract, was never engaged and
the director got six near-identical pages. "Near"-identical, not identical: the message
carries `after {elapsed:.0f}s`, so 252s / 255s / 253s made every page a unique string. Any
dedup keyed on exact text would have passed all six through as well.

The escalation path that SHOULD have turned this into work is RUNG 1d of the draw ladder,
which reads `.sim_producer_state.json` and was correctly written to by the runner on every
failure. Its thresholds were met -- 6 failures ≥ 3, 47 minutes > 30. It never fired, because
the supervisor logged nothing at all between 23:00 and 01:00. It was not ticking.

So the escalation existed and was structurally sound, and it depended on a separate observer
being awake. That is the defect the director's word "**itself**" names. An alarm that can only
become work if something else notices is an alarm that repeats when that something else is
asleep -- which is exactly the condition an outage tends to produce.

THE FIX, AND WHY IT SITS HERE
-----------------------------
Escalation happens on the alarm's own thread, in the one contract every alarm goes through.
No observer, no tick, no schedule. The Nth repetition of an unchanged alarm writes a staging
finding -- an artefact the draw ladder can win on -- and stops paging.

`notify()` is the only caller. This module holds the counting and the filing so that the
contract keeps reading as a contract.

FAIL-SAFE, IN THE DIRECTION THAT COSTS LEAST
--------------------------------------------
Escalation must NEVER be able to take down the alarm it is escalating: an exception filing a
finding would swallow the page that prompted it, converting a loud outage into a silent one.
Every path here is guarded and returns a falsy result on failure, and `notify()` treats that
as "not escalated" and carries on with its normal send/suppress decision.

The counting is also deliberately blind to how bad things are GETTING. "3 consecutive
failures" and "9 consecutive failures" normalise to the same key, so the ninth does not
re-page. That is intended: a worsening condition is the same condition, and the answer to it
is the work item, not another message at 4am.
"""
from __future__ import annotations

import hashlib
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

#: How many times an unchanged alarm may recur before it stops being a message and becomes
#: work. 3 is the same bar as RUNG 1d's `PRODUCER_STARVED_MIN_FAILURES` and rung 1's, chosen
#: for the same reason: sustained, not a lone flake. Deliberately NOT 1 -- a single retry that
#: then succeeds is noise in the draw, and a draw full of noise is the treadmill.
ESCALATE_AFTER_REPEATS = 3

#: How long an auto-keyed alarm must stay QUIET before its next firing counts as a new
#: episode -- pages again, and files its own work item.
#:
#: This exists because an auto-derived key has no recovery signal. A hand-keyed alarm passes
#: `state`, so clearing is a state change and the contract re-arms itself; an auto-keyed one
#: derives its state FROM THE MESSAGE, so the state can never change while the message is the
#: same, and without this the third repetition would silence that alarm permanently. The R15
#: proof for the recovery path is what surfaced that -- the design was wrong and the test that
#: was written to confirm it said so.
#:
#: 4h is chosen against the producer's own cadence: a run every ~8-9 minutes means a sustained
#: outage re-alarms every few minutes and stays ONE episode, while 4h of silence is ~27 missed
#: cycles -- unambiguously the condition having gone away and come back.
EPISODE_GAP_SECONDS = 4 * 3600

#: Everything that legitimately varies between two firings of the SAME condition. Each pattern
#: was taken from a real repeating alarm, not imagined:
#:   elapsed/duration   "after 252s" / "after 255s"    -- sim_runner's six pages
#:   counters           "3 consecutive" / "9 consecutive"
#:   git hashes         "(git=a77784f4a)" / "(git=a11556e23)"
#:   timestamps         ISO stamps and HH:MM:SS in the body
#:   byte/KB sizes      "4117 KB"
#:   session UUIDs      "session c7e894aa-3221-45f7-8713-" -- seat_continuity's eighteen copies
#: Normalising these is what makes "the same alarm" a decidable question. Everything else --
#: the exception type, the failing key, the module -- is preserved, so a KeyError and a
#: TypeError from the same daemon stay two different alarms with two different work items.
_VARIABLE = (
    # UUIDs, and this one MUST run before the git-hash rule below or it never fires.
    #
    # MEASURED, 2026-08-25: the staging root held EIGHTEEN copies of one alarm --
    # WORKER_FINDING_REPEATING_ALARM_SESSION_B_C_D_A_A_E_STOPPED_MID_WORK_..., _F_E_EE_A_E_...,
    # _C_C_A_..., one every thirty minutes for nine hours -- because `seat_continuity` puts the
    # dead session's id in its subject and a UUID SURVIVES this normaliser in pieces. The
    # `{7,40}` rule below eats a UUID's 8- and 12-character groups, but its 4-character groups
    # are too short to match; the trailing number rule then eats their digits and leaves the
    # LETTERS. `c7e894aa-3221-45f7-8713-` normalised to `# #f# #` and slugged to `SESSION_F`,
    # while `f0e2ee4a-e5b1-4c3d-9a2b-` slugged to `SESSION_E_B_C_D_A_B`. Two firings of one
    # condition, two filenames, two documents -- the "process re-creating a finding hourly"
    # defect that `_slug`'s own docstring says it exists to prevent, walking straight through it.
    #
    # Order is the whole fix: run first and the whole token goes; run second and there is
    # nothing hyphen-shaped left to match. Deliberately tolerant of TRUNCATION (`[:24]` is what
    # seat_continuity stores, which cuts mid-group and leaves a trailing hyphen) and it needs
    # three-plus hex groups, so `pre-commit-gate` and `test-driven-code` are untouched.
    re.compile(r"\b[0-9a-f]{4,}(?:-[0-9a-f]{2,}){2,}-?"),    # UUIDs, whole or truncated
    re.compile(r"\b[0-9a-f]{7,40}\b"),                       # git hashes / digests
    re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?Z?\b"),  # timestamps
    re.compile(r"\b\d{2}:\d{2}(:\d{2})?\b"),                 # clock times
    # Any number, LAST -- and deliberately without a trailing \b. The first version had one,
    # and it silently failed on the exact strings this exists for: in "after 252s" there is no
    # word boundary between "252" and "s", so the elapsed time survived normalisation and the
    # six overnight pages still produced six distinct signatures. It looked right and did
    # nothing, which is why it was checked against the real messages rather than invented ones.
    re.compile(r"\d[\d,]*(?:\.\d+)?"),
)


class EscalationUnavailable(RuntimeError):
    """Filing the work item failed. Never silently 'escalated'."""


def normalise(message: str) -> str:
    """The alarm with everything that legitimately varies between firings removed."""
    normalised = message
    for pattern in _VARIABLE:
        normalised = pattern.sub("#", normalised)
    return re.sub(r"\s+", " ", normalised).strip().lower()


def alarm_signature(message: str) -> str:
    """A stable key for "this alarm, again", ignoring what legitimately varies.

    Returns a short hash rather than the normalised text so the transitions store stays small
    and a key can never accidentally be read as a message.
    """
    return "auto:" + hashlib.sha256(normalise(message).encode("utf-8")).hexdigest()[:16]


def _slug(message: str) -> str:
    """A filename-safe subject from the alarm's own words -- so the finding is named for what
    it found, which is what background/finding_classes.py classifies on.

    Built from the NORMALISED text, which matters more than it looks: on the raw message the
    six overnight pages would have produced WORKER_FINDING_..._AFTER_252S_..., _255S_, _253S_
    -- three different filenames, so the idempotence-by-path in escalate() would have filed a
    fresh document per repetition. That is the "process re-creating a finding hourly" defect
    that cost four manual clears, rebuilt inside its own remedy.

    STILL NOT AN IDENTITY, and that is what `family()` below exists to fix -- see its docstring.
    This remains the document's SUBJECT (its title and its filename tail for auto-keyed
    alarms), because a document called `SEAT_CLAIM` and nothing else tells a reader nothing.
    """
    head = re.sub(r"^\[[^\]]+\]\s*", "", normalise(message)).strip()
    head = re.sub(r"[^A-Za-z0-9 ]+", " ", head)
    words = [w for w in head.split() if w][:10]
    return "_".join(words).upper()[:110] or "AN_UNNAMED_ALARM"


def family(key: str) -> str:
    """THE CONDITION'S IDENTITY, taken from the key the CALLER DECLARED.

    MEASURED, 2026-08-28 (director, having read all 49 documents in the staging root): of 37
    auto-filed alarm documents, 16 said `[SEAT] <work-id> was claimed and has not moved` and 8
    said `<directory-list> left uncommitted by a session that stopped mid-work`. Two
    conditions, twenty-four documents. His words: "one document per firing, ten of them the
    identical finding and twelve of them 'claimed and hasn't moved'."

    WHY THE EXISTING GUARDS ALL PASSED IT. `normalise()` removes what varies NUMERICALLY --
    elapsed times, counters, hashes, timestamps, UUIDs -- because every repetition this module
    had ever been shown varied that way. These two vary in PROSE: a work-id in one, an
    enumerated path list in the other. No number is involved, so the normaliser had nothing to
    remove, `_slug` produced a different filename per firing, and `escalate`'s
    idempotence-by-path filed a fresh document each time. Adding a seventeenth regex for
    work-ids would have fixed these two and waited for the eighteenth shape.

    THE KEY WAS ALREADY RIGHT AND WAS BEING THROWN AWAY. `seat_continuity` passes
    `key="seat-continuity"` -- one stable string for all eight of its documents.
    `seat_work_in_hand` passes `key=f"seat-claim:{work_id}"` -- a family and an instance,
    correctly separated by a colon. Both callers had already declared the identity this module
    needed, and `finding_path()` ignored `key` entirely and re-derived identity from the
    message. So this is not a new contract; it is reading the one that existed.

    An `auto:` key is the sha of the normalised message and is ALREADY the whole family -- it
    has no instance half and must not be split (a hex digest can contain no colon, but saying
    so in code is cheaper than relying on it).
    """
    if key.startswith("auto:"):
        return key
    return key.split(":", 1)[0]


def instance(key: str, message: str) -> str:
    """WHICH member of the family fired -- the thing a single document must LIST rather than
    lose.

    Collapsing sixteen documents into one is only an improvement if the sixteen work-ids
    survive the collapse. They do: the instance is the key's own tail where the caller
    provided one (`seat-claim:land-the-ceiling-priced-half-the-book`), and the normalised
    subject otherwise, so a family whose members differ only in prose still enumerates them.
    """
    if not key.startswith("auto:") and ":" in key:
        return key.split(":", 1)[1]
    return re.sub(r"^\[[^\]]+\]\s*", "", normalise(message)).strip()[:120]


def _family_slug(key: str, message: str) -> str:
    """The filename tail: the declared family for a keyed alarm, the subject for an auto one."""
    if key.startswith("auto:"):
        return _slug(message)
    return re.sub(r"[^A-Za-z0-9]+", "_", family(key)).strip("_").upper()[:110] or "AN_UNNAMED_ALARM"


def finding_path(message: str, *, today: str, key: str = "auto:",
                 staging_dir: Path | None = None) -> Path:
    return (staging_dir or STAGING_DIR) / (
        f"WORKER_FINDING_REPEATING_ALARM_{_family_slug(key, message)}_{today}.md"
    )


def escalate(message: str, *, key: str, repeats: int, first_ts: float,
             staging_dir: Path | None = None, now: float | None = None) -> Path | None:
    """File the work item for a repeating alarm. Returns the path, or None if it already exists.

    IDEMPOTENT by path: the same alarm on the same day refiles nothing. That is the whole
    point -- an escalation that filed once per repetition would be the original defect wearing
    a different hat, and this project has already spent four manual clears on a process that
    re-created one archived finding hourly.
    """
    # HARD PYTEST GUARD, and it is here for a measured reason rather than a theoretical one.
    # Within hours of this module going live, FIVE findings appeared in docs/staging/ and one
    # of them quoted `SOME_DOC.md` -- a fixture filename from
    # tests/background/test_deadmans_switch.py. A test run was filing real work items into the
    # director's queue.
    #
    # `send_ntfy` has carried a guard of exactly this shape since 2026-07-16 ("my phone is
    # spamming with test messages"), and I built the escalation beside that guard rather than
    # behind it: the SEND was protected and the WRITE was not. R15's own doctrine says a test
    # fixture must be STRUCTURALLY unable to reach the director, and a document in his draw
    # queue reaches him just as surely as a page does.
    #
    # Scoped to the REAL staging directory, resolved -- not to "no argument was given". A test
    # that redirects the module's STAGING_DIR to a tmp_path is exercising the mechanism
    # honestly and must still work, or this guard makes the module untestable, which is how a
    # guard like this ends up deleted. Keying on the ARGUMENT instead was my first attempt and
    # it broke five end-to-end tests, because notify() calls escalate() without one.
    target = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    if (os.environ.get("PYTEST_CURRENT_TEST") is not None
            and target.resolve() == (PROJECT_DIR / "docs" / "staging").resolve()):
        return None

    now = time.time() if now is None else now
    today = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d")
    path = finding_path(message, today=today, key=key, staging_dir=target)
    if path.exists():
        _note_instance(path, instance(key, message), today=today)
        return None

    # ONE DOCUMENT PER SIGNATURE, NOT ONE PER SIGNATURE PER DAY (2026-08-24, director
    # console: "Stop filing findings where a class document already covers them").
    #
    # THE DEFECT, MEASURED. Idempotence above is keyed on a path that CONTAINS THE DATE, so
    # an unchanged condition refiled itself every midnight. On the morning of 2026-08-24 the
    # staging root held NINE of these documents -- three signatures on each of 08-22, 08-23
    # and 08-24 -- and every one of the nine said the same thing about the same unchanged
    # condition. That was 15 of the 18 actionable items in the root, so the tick's own draw
    # prompt was three-quarters this module talking about itself. The escalation built to
    # stop a process re-creating a finding hourly was re-creating one daily; the docstring
    # above says that defect "wearing a different hat" is exactly what to watch for, and it
    # was watching the wrong clock.
    #
    # WHAT REPLACES IT. A live document for this signature -- in the root or parked in
    # `in_progress/` -- is UPDATED IN PLACE with a dated still-live line. Nothing is lost:
    # the fact worth having on the second day is "this is still happening, and now for
    # longer", which is one line, not a second copy of the first document. `done/` is
    # deliberately NOT searched: a condition that returns after being archived is a NEW
    # episode and an R3 two-strike signal, and it must be able to file again.
    live = _live_finding_for(message, key=key, staging_dir=target)
    if live is not None:
        _note_still_live(live, today=today, repeats=repeats, window_h=(now - first_ts) / 3600.0)
        _note_instance(live, instance(key, message), today=today)
        return None

    window_h = max(0.0, (now - first_ts)) / 3600.0
    # THE CHAIN, FROM BIRTH (2026-08-28, the director's P8: "not one file carries a lane, an
    # epoch or an atom id, so the queue is disconnected from the map entirely"). Stamping it
    # HERE rather than asking a later turn to add it is the difference between a field that is
    # filled in and one that is exhorted: an auto-filed document nobody stamps is exactly the
    # document that ends up unchained, and thirty-seven of them were.
    #
    # `unassigned`/`unminted` are DECLARED, not blank. An alarm has not been triaged against
    # the map at the moment it is filed, and saying so is the honest value; what would be
    # dishonest is guessing an epoch, and what would be useless is leaving the field out and
    # letting "nobody looked" and "looked, nothing yet" render identically.
    body = f"""**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# {message.strip().splitlines()[0][:180]}

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **{repeats} times without its state changing**, over **{window_h:.1f}h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a {repeats}th page does not.

## The alarm, verbatim

```
{message.strip()}
```

## What is known without diagnosing anything

- Signature: `{key}` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: {datetime.fromtimestamp(first_ts, timezone.utc).isoformat(timespec="seconds")}
- Repeats before escalation: {repeats} (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Still live

## Instances seen
"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    except OSError as exc:
        raise EscalationUnavailable(f"could not file {path}: {exc}") from exc
    # THE FIRST FIRING IS AN INSTANCE TOO. Listing only the members that arrive AFTER the
    # document exists loses the one that caused it -- a sixteen-claim family would enumerate
    # fifteen, and the missing one would be the earliest, which is the one whose age the
    # document's own header is about.
    _note_instance(path, instance(key, message), today=today)
    return path


def _live_finding_for(message: str, *, key: str, staging_dir: Path) -> Path | None:
    """An UNACTIONED document already covering this alarm's FAMILY, or None.

    Searches the staging root and `in_progress/` and not `done/` -- see the reasoning at the
    call site. Matching is by the same stem `finding_path` builds, which since 2026-08-28 is
    the caller's declared FAMILY rather than the message's slug: that is the change that makes
    sixteen documents about sixteen stale claims into one document listing sixteen claims.

    THE SLUG STEM IS STILL SEARCHED, second, and only for keyed alarms. Twenty-four documents
    already existed under slug names when the family rule went in, and a lookup that only knew
    the new shape would have filed a twenty-fifth beside them on the first firing -- the exact
    "process re-creating a finding" defect, reintroduced by its own fix. The migration renames
    them; this makes the window between the code landing and the migration running safe, and
    it stays because a document a human renamed by hand must not spawn a sibling either.
    """
    stems = [f"WORKER_FINDING_REPEATING_ALARM_{_family_slug(key, message)}_"]
    slug_stem = f"WORKER_FINDING_REPEATING_ALARM_{_slug(message)}_"
    if slug_stem not in stems:
        stems.append(slug_stem)
    for stem in stems:
        for room in (staging_dir, staging_dir / "in_progress"):
            try:
                matches = sorted(room.glob(f"{stem}*.md"))
            except OSError:
                continue  # an unreadable room is not evidence that nothing is filed
            if matches:
                return matches[0]
    return None


#: The heading under which a family document enumerates which of its members have fired.
INSTANCES_HEADING = "## Instances seen"


def _note_instance(path: Path, name: str, *, today: str) -> None:
    """Record that this member of the family has fired, once, ever.

    IDEMPOTENT PER INSTANCE rather than per day, which is the opposite of `_note_still_live`
    below and deliberately so. "This condition is still happening" is news once a day; "the
    claim on `land-the-ceiling-priced-half-the-book` went stale" is news once, and a document
    that re-listed it every day would be the collapsed pile rebuilt inside one file.

    The list is what makes the collapse lossless. Without it, folding sixteen documents into
    one would discard the sixteen work-ids, and a fix that loses the finding is not a fix.
    """
    if not name:
        return
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    if f"- `{name}` (" in text:
        return
    updated = _append_under(text, INSTANCES_HEADING, f"- `{name}` (first seen {today})")
    try:
        path.write_text(updated, encoding="utf-8")
    except OSError:
        return


def _append_under(text: str, heading: str, line: str) -> str:
    """Return `text` with `line` added at the END OF `heading`'s SECTION, creating the heading
    at the bottom if it is absent.

    Appending to the end of the FILE was the shape both note-writers used, and it worked only
    while there was exactly one section to append to. A document now carries two -- "Still
    live" and "Instances seen" -- and end-of-file appending would file every still-live line
    under whichever heading happened to be last. Section-aware placement is the difference
    between a document that stays readable after forty firings and one that does not.
    """
    lines = text.rstrip().splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return "\n".join(lines) + f"\n\n{heading}\n{line}\n"
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    body = lines[:end]
    while body and not body[-1].strip():
        body.pop()
    return "\n".join(body + [line] + lines[end:]) + "\n"


def _note_still_live(path: Path, *, today: str, repeats: int, window_h: float) -> None:
    """Append one dated line recording that the condition has not changed.

    Idempotent per DAY: a second call on the same date rewrites nothing, so a tick that runs
    forty-eight times cannot turn one document into forty-eight lines -- which would be the
    same defect at a finer grain.
    """
    marker = f"- **{today}**"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return  # a document we cannot read is not one we can annotate; the alarm still fires
    if marker in text:
        return
    line = (f"{marker} — still live. {repeats} repeats over {window_h:.1f}h without the "
            f"state changing. No second document filed: this condition already has one.")
    try:
        path.write_text(_append_under(text, "## Still live", line), encoding="utf-8")
    except OSError:
        return
