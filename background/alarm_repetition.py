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
import json
import os
import re
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

# TOP LEVEL WITH NO `try`, which is `live_ledger_guard`'s own stated contract: if the guard cannot
# be imported, the writer must not import either, because an unavailable check is a FAILED check
# and never a silently skipped one. Safe against the import cycle this module lives inside --
# `notify` imports this, this imports the guard, and the guard imports nothing but stdlib.
from background.live_ledger_guard import guard_live_ledger_write

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"


def _write_document(path: Path, text: str) -> Exception | None:
    """THE ONLY DOOR ANY WRITE IN THIS MODULE GOES THROUGH. Returns the failure, or None.

    ONE DOOR RATHER THAN EIGHT, and the reason is `background/live_ledger_guard`: its refusal has
    to be REACHED by every write, or it is a check on whichever writer happened to remember it.
    Eight scattered `write_text` calls were eight places to forget; one is a place that cannot be,
    because there is nowhere else in the module to write from.

    THE GUARD IS A NO-OP FOR A STAGING DOCUMENT, and calling it there anyway is what makes the
    door uniform rather than conditional. It refuses only a write whose destination resolves
    inside `docs/observability/` -- which in this module is the state store alone -- so the two
    kinds of write get the same door and only one of them ever sees a refusal.

    NEVER RAISES, which is the module's founding rule: an exception on the way to filing a work
    item would swallow the page that prompted it. `LiveLedgerWriteUnderTest` is caught here with
    everything else and REPORTED rather than propagated, and every caller decides what its own
    failure means -- `escalate` raises `EscalationUnavailable`, the annotators carry on.
    """
    try:
        guard_live_ledger_write(path, writer=f"alarm_repetition writing {path.name}")
        path.write_text(text, encoding="utf-8")
        return None
    except Exception as exc:
        return exc

#: How many times an unchanged alarm may recur before it stops being a message and becomes
#: work. 3 is the same bar as RUNG 1d's `PRODUCER_STARVED_MIN_FAILURES` and rung 1's, chosen
#: for the same reason: sustained, not a lone flake. Deliberately NOT 1 -- a single retry that
#: then succeeds is noise in the draw, and a draw full of noise is the treadmill.
ESCALATE_AFTER_REPEATS = 3

# THREE COUNTS, AND THEY ARE NOT THE SAME COUNT
# ---------------------------------------------
# SAY WHAT THE THING IS BEFORE MEASURING IT. An alarm document carries three numbers that all
# sound like "how many times", and every defect this section exists to fix came from one of them
# being written where another was meant.
#
#   repeats      CONSECUTIVE FIRINGS WITHOUT A STATE CHANGE. The caller's, and only `notify()`
#                can know it, because only `notify()` holds the transition store that decides
#                when the streak breaks. It is an argument, it is OPTIONAL, and a caller that
#                does not measure it passes nothing.
#   days         DISTINCT DATES ON WHICH THE CONDITION WAS OBSERVED TO HOLD. The document's own,
#                read back from the machine-written lines every firing leaves behind.
#   members      DISTINCT MEMBERS OF THE FAMILY THAT HAVE FIRED. Also the document's own, read
#                from the instance list.
#
# THE MEASURED DEFECT, 2026-09-23/24 (finding `..._THREE_ALARM_FAMILIES_BYPASS_NOTIFY_AND_
# HARDCODE_REPEATS_1_...`, `612bd9ffe`, plus the wider measurement in `..._THE_HEADER_IS_STAMPED_
# ONCE_...`). Four call sites reach `escalate()` directly and had to supply `repeats` because it
# was required, so all four passed the literal `1`. `SEAT_CONTINUITY` opened with "fired **1
# times without its state changing**, over **95.9h**" above eight days of still-live lines and
# twenty-three enumerated members; `DELIVERY_LANE_STRANDED` said the same above eighteen. Their
# still-live lines repeated "1 repeats" verbatim every day, because a frozen constant is not a
# measurement of anything.
#
# AND THE HEADER WAS STAMPED ONCE FOR EVERYONE, not only for those four: it was written into the
# body at birth and never rewritten, so `STRETCH_LOG` led with "fired **3 times**" above a line
# reading 2132, and four of the seven documents carrying still-live lines understated themselves
# in their own first sentence. The literal `1` was the worst case of a defect the whole
# population had.
#
# SO THE TWO COUNTS THE DOCUMENT CAN ESTABLISH ARE DERIVED FROM THE DOCUMENT, EVERY FIRING, and
# the caller's count is reported beside them under its own name or declared absent. They are
# never summed and never differenced: `days` and `members` grow monotonically, while `repeats`
# is a streak counter that RESETS (`DEADMAN_WORKTREE_UNDECLARED` ran 3, 22, 51, 70, 106, 298, 3),
# so any arithmetic across the three is arithmetic across incommensurables.

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


def escalate(message: str, *, key: str, first_ts: float, repeats: int | None = None,
             staging_dir: Path | None = None, now: float | None = None) -> Path | None:
    """File the work item for a repeating alarm. Returns the path, or None if it already exists.

    `repeats` IS THE CALLER'S OWN QUANTITY AND IS OPTIONAL — see THREE COUNTS above. Pass it
    only if you actually measure consecutive firings without a state change, which in practice
    means `notify()`. A caller that reaches here directly passes nothing and the document says
    so; it does not invent a number, and the two counts the document derives from itself are
    stated whether or not this one is.

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
        _record(path, key=key, first_ts=first_ts, observed=today)
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
        _record(live, key=key, first_ts=first_ts)
        _note_still_live(live, today=today, repeats=repeats, window_h=(now - first_ts) / 3600.0)
        _note_instance(live, instance(key, message), today=today)
        # LAST, ALWAYS, so the counts are read back from a document that already carries today's
        # lines. Ordering it before the two writers would restate yesterday's numbers under
        # today's date, which is the frozen header rebuilt one day behind itself.
        _refresh_counts(live, key=key, repeats=repeats, first_ts=first_ts, now=now)
        return None

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

## The alarm, verbatim

```
{message.strip()}
```

## What is known without diagnosing anything

- Signature: `{key}` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: {datetime.fromtimestamp(first_ts, timezone.utc).isoformat(timespec="seconds")}
- {_threshold_line(repeats)}
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
    except OSError as exc:
        raise EscalationUnavailable(f"could not file {path}: {exc}") from exc
    failure = _write_document(path, body)
    if failure is not None:
        raise EscalationUnavailable(f"could not file {path}: {failure}") from failure
    # THE FIRST FIRING IS AN INSTANCE TOO. Listing only the members that arrive AFTER the
    # document exists loses the one that caused it -- a sixteen-claim family would enumerate
    # fifteen, and the missing one would be the earliest, which is the one whose age the
    # document's own header is about.
    # THE REBIRTH, AND IT IS WHAT MAKES CLEARING LOSSLESS RATHER THAN MERELY SURVIVABLE.
    # A fresh body above carries no history at all. If the store holds any -- because this
    # document was cleared, archived-and-returned under a stem it shares, or swept out of the
    # tree -- it is written back here, so the document a draw reads is the same document, not a
    # stub that happens to have the right title. The header alone would not do: a reader who
    # cannot see the dated lines the counts are counted from has no way to check them.
    _replay_history(path, _record(path, key=key, first_ts=first_ts), today=today)
    _note_instance(path, instance(key, message), today=today)
    # THE COUNTS BLOCK IS INSERTED, NEVER STAMPED, and this is the same call the live branch
    # above makes -- one derivation point for the whole module. The birth body deliberately
    # carries no counts paragraph of its own: a provisional one written here and corrected a
    # line later would be a second place the numbers come from, and the second place is always
    # the one that rots. If this cannot write, the document arrives with no counts at all --
    # visibly incomplete, which is the direction that cannot mislead a draw.
    _refresh_counts(path, key=key, repeats=repeats, first_ts=first_ts, now=now)
    return path


def _replay_history(path: Path, entry: dict, *, today: str) -> bool:
    """Write the store's dated lines back into a freshly-born document. Never raises.

    THE LINES MATCH `_STILL_LIVE_DATE` AND `_INSTANCE_LINE` EXACTLY, which is not cosmetic: it is
    what keeps the document a superset of the store rather than a summary of it, so
    `_observation_dates` -- the pure document reader -- still returns the same set the store holds.
    The day those two disagree is the day the store stops being falsifiable from the artefact.

    THE WORDING SAYS WHERE THE LINE CAME FROM. A replayed line is a record of an observation made
    on that date; it is NOT this firing observing anything about that date, and a reader who
    cannot tell the two apart would read a re-derived document as forty firings of one condition.
    """
    observed = [d for d in entry.get("observed") or [] if d != today]
    instances = entry.get("instances") or {}
    if not observed and not instances:
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        for date in sorted(observed):
            text = _append_under(text, "## Still live", (
                f"- **{date}** — still live. The condition was observed to hold on this date. "
                f"Restored from `{_state_file(_staging_dir_of(path)).name}` when this document "
                f"was re-derived; the observation is that date's, not today's."))
        for name, date in sorted(instances.items()):
            if f"- `{name}` (" not in text:
                text = _append_under(text, INSTANCES_HEADING, f"- `{name}` (first seen {date})")
    except OSError:
        return False
    return _write_document(path, text) is None


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
    # THE STORE FIRST, AND UNCONDITIONALLY. The early return below is about the RENDERING -- this
    # member is already listed, so the line need not be written again -- and it must not be
    # allowed to mean "the store need not hear about it" as well. A document re-derived after a
    # clear would otherwise re-list a member the store had never been told about.
    _record(path, instances={name: today})
    if f"- `{name}` (" in text:
        return
    _write_document(path, _append_under(text, INSTANCES_HEADING,
                                       f"- `{name}` (first seen {today})"))


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


def _note_still_live(path: Path, *, today: str, repeats: int | None, window_h: float) -> None:
    """Append one dated line recording that the condition has not changed.

    Idempotent per DAY: a second call on the same date rewrites nothing, so a tick that runs
    forty-eight times cannot turn one document into forty-eight lines -- which would be the
    same defect at a finer grain.

    THE LINE NO LONGER OPENS WITH THE CALLER'S NUMBER. It used to read "{repeats} repeats over
    {window_h}h", which for the four direct call sites was the literal `1` written out again
    under a new date -- `DELIVERY_LANE_STRANDED` carried four consecutive days of "1 repeats
    over 1.7h", identical because they were not measurements. The line now leads with what this
    call OBSERVED (the date, and that the condition held) and carries the caller's streak
    afterwards, named as the caller's and omitted entirely when the caller does not measure it.
    """
    marker = f"- **{today}**"
    # SAME ORDER AS `_note_instance`, same reason: the store records that the condition was
    # observed today whether or not the rendering needs another line for it.
    _record(path, observed=today)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return  # a document we cannot read is not one we can annotate; the alarm still fires
    if marker in text:
        return
    line = (f"{marker} — still live. The condition was observed to hold again today. "
            f"No second document filed: this condition already has one."
            + (f" The observer reports {repeats} consecutive firing(s) without a state change, "
               f"over {window_h:.1f}h — its streak, not this document's total."
               if repeats is not None else
               " This observer reaches `escalate()` directly and measures no streak."))
    _write_document(path, _append_under(text, "## Still live", line))


# ---------------------------------------------------------------------------------------------
# WHAT THE DOCUMENT RECORDS ABOUT ITSELF
# ---------------------------------------------------------------------------------------------
# The readers below are SHARED between `escalate()` and the re-ask, and that sharing is the
# point rather than a convenience: both ask the same question -- "what has the alarm machinery
# actually written into this document?" -- and two readers of one record would drift.
#
# ONLY MACHINE-WRITTEN LINES COUNT. A human note added today saying "drawn, being worked" is
# evidence that somebody is LOOKING, which is a different fact from the condition holding, and
# letting it count would let attention masquerade as the thing attention was paid to.

_STILL_LIVE_DATE = re.compile(r"^- \*\*(\d{4}-\d{2}-\d{2})\*\* — still live\.", re.M)
_INSTANCE_DATE = re.compile(r"^- `.*` \(first seen (\d{4}-\d{2}-\d{2})\)", re.M)
#: The same line as `_INSTANCE_DATE`, capturing the MEMBER as well as the date. Two patterns over
#: one line rather than one, because `_INSTANCE_DATE` answers "how many members fired" for the
#: counts block and this one answers "which ones, and when" for the store -- and a single pattern
#: serving both would have to be read twice with the second capture discarded, which is where a
#: later edit silently changes the count.
_INSTANCE_LINE = re.compile(r"^- `([^`]*)` \(first seen (\d{4}-\d{2}-\d{2})\)", re.M)
_FILENAME_DATE = re.compile(r"_(\d{4}-\d{2}-\d{2})\.md$")
_SIGNATURE_LINE = re.compile(r"^- Signature: `([^`]+)`", re.M)

#: Where the re-ask records itself. A SEPARATE section from "Still live" on purpose, and the
#: distinction is load-bearing rather than cosmetic: the readers here must never read a line the
#: re-ask itself wrote, or the first re-ask would refresh the document's apparent age and nothing
#: could ever clear again -- a control reading its own output and agreeing with itself. Only an
#: alarm FIRING may write "Still live"; only the re-ask may write here.
REASK_HEADING = "## Re-asked"


# ---------------------------------------------------------------------------------------------
# THE STORE BEHIND THE DOCUMENT
# ---------------------------------------------------------------------------------------------
# DIRECTOR DIRECTION, Lane 0, 2026-09-24: *"give it a state store on an untracked path and derive
# the document from it, so clearing the document is lossless."*
#
# THE DEFECT, AND IT IS STRUCTURAL RATHER THAN A BUG. Until this landed, the document WAS the
# store -- its own header said so, verbatim: the counts are "DERIVED from this document's own
# dated lines", and there was no json anywhere behind them. That made ONE FILE THREE THINGS:
#
#   1. the STATE STORE, rewritten in place by every firing;
#   2. the PUBLISHED WORK ITEM a draw reads and a seat archives;
#   3. a TRACKED PATH that origin also carries its own copy of.
#
# Any two of those are fine. All three are a self-refilling merge collision. MEASURED 2026-09-24:
# the shared tree sat ten commits behind origin/main; `origin_reconcile` succeeded every five
# minutes and the fast-forward BEHIND the merge was refused on 11-12 paths, NINE of them these
# documents; the alarm machinery re-dirtied them within the hour, so no drain cleared it and no
# cadence absorbed it. The daemons in that tree were running code 55 modules behind, which means
# every landed daemon repair was inert. The fork was never the cause.
#
# THE SPLIT. (1) moves here, to an untracked json that nothing merges. (2) and (3) stay exactly
# where they are, and the document becomes a RENDERING: deleting it costs the rendering only, and
# the next firing rebuilds it complete.
#
# UNION, NEVER SUBTRACTION, and that is the whole safety argument. The store is SEEDED FROM THE
# DOCUMENTS THEMSELVES on first touch, so the ten days of history already written into them is
# absorbed rather than abandoned, and no path here removes a date. A store that could shrink would
# be a worse home for the history than the document already was.
#
# THE ONE PLACE IT MAY FORGET is `_close_episode`, and that is not subtraction: an archived
# condition that RETURNS is a new episode and an R3 two-strike signal, which is the same reason
# `escalate()` refuses to search `done/`. The closed episode is kept beside the live one rather
# than dropped, so the two-strike reading has something to read.
#
# NOT THE GENERATED-PATHS ORACLE. The cheaper fix -- declare the stem generated so
# `advance_shared_tree` may clear the files -- was refused in the direction it fails: it lets the
# tree delete ten days of alarm history into `refs/preserved`, which nothing reads back. Clearing
# has to be LOSSLESS BEFORE it is PERMITTED, and this is that order, not the other one.

#: The untracked store. `.gitignore`d beside `.notify_transitions.json`, which is the same kind of
#: thing for the same reason: runtime state about what this machine has observed, not a record.
ALARM_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".alarm_repetition_state.json"


def _staging_dir_of(path: Path) -> Path:
    """The staging ROOT a document belongs to, whether it sits there or in `in_progress/`.

    The same rule `_archive_cleared` uses to find `done/`, and it must stay the same rule: a
    parked document and a root one are the same document to every reader here, so they must
    resolve to the same store.
    """
    return path.parent.parent if path.parent.name == "in_progress" else path.parent


def _state_file(staging_dir: Path) -> Path:
    """Where the store lives for `staging_dir`.

    SCOPED THE SAME WAY `escalate()`'s pytest guard is scoped, and for the same measured reason: a
    test that redirects the staging directory to a `tmp_path` is exercising the mechanism honestly
    and gets its own store automatically, with no fixture to remember and nothing to stub. Keying
    on "was an argument given" instead would make the store untestable or the tests dirty the real
    one, and this module has already paid for that mistake once.
    """
    try:
        if staging_dir.resolve() == (PROJECT_DIR / "docs" / "staging").resolve():
            return ALARM_STATE_FILE
    except OSError:
        pass
    return staging_dir / ".alarm_repetition_state.json"


def document_stem(path: Path) -> str:
    """The identity a document and its store entry share: the filename without its filing date.

    NOT the filename. A document that is cleared and re-derived is born under TODAY's date, so
    keying the store on the full name would give the reborn document an empty history -- which is
    precisely the loss this store exists to prevent. The stem is what `_live_finding_for` already
    treats as one condition's identity, so the store and the collapse rule agree by construction.
    """
    return _FILENAME_DATE.sub("", path.name) or path.stem


def _blank_entry() -> dict:
    """An entry that has never been written to. Every field present, so no reader needs `.get`."""
    return {"key": None, "first_ts": None, "filed": None,
            "observed": [], "instances": {}, "reasked": [], "episodes": []}


def _read_state(staging_dir: Path) -> dict:
    """The whole store, keyed by document stem, or `{}` on ANY failure.

    `{}` IS SAFE HERE because every reader unions the store with the document it is about, so an
    unreadable store can only fail to ADD history -- it can never remove what the document itself
    still says. That is the same one-directional argument `_read_transitions_for_reask` makes, and
    it holds for the same reason: this record is used to widen a reading, never to narrow one.
    """
    try:
        data = json.loads(_state_file(staging_dir).read_text(encoding="utf-8"))
    except Exception:
        return {}
    documents = data.get("documents") if isinstance(data, dict) else None
    return documents if isinstance(documents, dict) else {}


def _write_state(staging_dir: Path, documents: dict) -> bool:
    """Persist the store. Never raises; returns False if it could not be written.

    THE REFUSAL IS `live_ledger_guard`'s, NOT A SECOND SPELLING OF IT. The store lives under
    `docs/observability/`, which makes it exactly the subject that guard already owns, and this
    module had no business growing its own `PYTEST_CURRENT_TEST` test beside it -- the first draft
    did, and it was narrower: it recognised one hard-coded path where the guard recognises the
    whole directory, so a second store added tomorrow would have been unprotected.

    IT IS NEEDED FOR A REASON `escalate()`'s OWN GUARD DOES NOT COVER. The readers seed the store
    as a side effect of being read, so a test that merely COUNTS a real document would otherwise
    write the live store. Under pytest the readers therefore stay pure and answer from the
    document alone -- which is the old behaviour exactly, so no test can be made to pass by the
    seeding.
    """
    target = _state_file(staging_dir)
    try:
        guard_live_ledger_write(target, writer="alarm_repetition._write_state")
        target.parent.mkdir(parents=True, exist_ok=True)
        # ATOMIC AND PID-SUFFIXED. Several daemons reach `notify()` at once on this box, and a
        # shared temp name is how two concurrent writers produce one truncated file.
        tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps({"documents": documents}, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
        tmp.replace(target)
        return True
    except Exception:
        return False


def _merged_entry(entry: dict | None, path: Path, text: str | None = None) -> dict:
    """`entry` widened by everything `path`'s own text establishes. Pure; never writes.

    THIS IS THE MIGRATION, and it is a merge rather than a script so that there is nothing to run
    and nothing to remember. Every document filed before the store existed seeds itself the first
    time anything touches it, and every document filed after it re-seeds harmlessly, because union
    with what you already hold is the identity.
    """
    merged = dict(_blank_entry())
    merged.update({k: v for k, v in (entry or {}).items() if v is not None})
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""  # a document we cannot read subtracts nothing; that is the point
    body = _without_reask_section(text)

    observed = set(merged["observed"]) | set(_STILL_LIVE_DATE.findall(body))
    instances = dict(merged["instances"])
    for name, date in _INSTANCE_LINE.findall(body):
        instances.setdefault(name, date)
        observed.add(date)
    filed = _FILENAME_DATE.search(path.name)
    if filed:
        # THE FILING DATE IS AN OBSERVATION -- the same rule `_observation_dates` has always
        # applied. On a re-derived document that is TODAY's date and it is still true: the firing
        # that rebuilt the document observed the condition.
        observed.add(filed.group(1))
        merged["filed"] = min(filed.group(1), merged["filed"] or filed.group(1))
    signature = _SIGNATURE_LINE.search(text)
    if signature:
        merged["key"] = merged["key"] or signature.group(1)

    merged["observed"] = sorted(observed)
    merged["instances"] = instances
    merged["reasked"] = sorted(set(merged["reasked"]) | set(_REASK_DATE.findall(_reask_section(text))))
    return merged


def absorb(path: Path, text: str | None = None) -> dict:
    """This document's store entry, seeded from the document itself, persisted if it grew.

    READING SEEDS, deliberately, and this is the one place in the module where a read writes. The
    alternative -- seed only on the next FIRING -- leaves a window, per family, in which clearing
    the document still loses its history, and the window is exactly as long as that family's
    cadence. The direction this fails in is a redundant write of a file nothing merges.

    Never raises, and returns the merged entry whether or not it could be stored, so a read-only
    filesystem degrades to the old document-only behaviour rather than to an exception inside a
    notification path.
    """
    staging = _staging_dir_of(path)
    documents = _read_state(staging)
    stem = document_stem(path)
    merged = _merged_entry(documents.get(stem), path, text)
    if merged != documents.get(stem):
        documents[stem] = merged
        _write_state(staging, documents)
    return merged


def _record(path: Path, **fields) -> dict:
    """Union `fields` into this document's entry and persist. The only writer's door.

    `observed` and `reasked` take a date, `instances` a `{name: date}`, `key`/`first_ts` a scalar
    that is only accepted if the entry does not already carry an EARLIER one -- an episode's start
    does not move because a later observer passed a later clock.
    """
    staging = _staging_dir_of(path)
    documents = _read_state(staging)
    stem = document_stem(path)
    entry = _merged_entry(documents.get(stem), path)

    if fields.get("observed"):
        entry["observed"] = sorted(set(entry["observed"]) | {fields["observed"]})
    if fields.get("reasked"):
        entry["reasked"] = sorted(set(entry["reasked"]) | {fields["reasked"]})
    for name, date in (fields.get("instances") or {}).items():
        entry["instances"].setdefault(name, date)
        entry["observed"] = sorted(set(entry["observed"]) | {date})
    if fields.get("key"):
        entry["key"] = entry["key"] or fields["key"]
    if fields.get("first_ts") is not None:
        held = entry["first_ts"]
        entry["first_ts"] = float(fields["first_ts"]) if held is None \
            else min(float(held), float(fields["first_ts"]))

    documents[stem] = entry
    _write_state(staging, documents)
    return entry


def _close_episode(path: Path, *, today: str) -> None:
    """Retire this stem's live history when its document is archived. The one forgetting path.

    NOT A DELETE. The episode is moved beside the live entry, because a condition that returns
    after being archived is the R3 two-strike signal and the second strike is only legible against
    the first. What must NOT survive is the live history, or a fresh episode would inherit the old
    one's dates and its header would claim continuous observation across the gap -- the same error
    as searching `done/`, arriving through the store instead of through the filename.
    """
    staging = _staging_dir_of(path)
    documents = _read_state(staging)
    stem = document_stem(path)
    entry = _merged_entry(documents.get(stem), path)
    episodes = list(entry["episodes"])
    episodes.append({"closed": today, "observed": entry["observed"],
                     "instances": entry["instances"], "reasked": entry["reasked"],
                     "first_ts": entry["first_ts"], "filed": entry["filed"]})
    documents[stem] = dict(_blank_entry(), key=entry["key"], episodes=episodes)
    _write_state(staging, documents)

#: The self-updating block at the head of every alarm document. Everything between these markers
#: is DERIVED from the document's own machine-written lines and rewritten on every firing, so the
#: first sentence a draw reads ages with the document instead of with its first firing.
#:
#: MARKERS RATHER THAN A HEADING, because this block sits above the first `## ` and `_append_under`
#: -- the module's other writer -- works in terms of `## ` sections. A heading here would put the
#: counts inside the section machinery and make every appended line land in the wrong place.
COUNTS_BEGIN = "<!-- counts:begin -->"
COUNTS_END = "<!-- counts:end -->"

#: The opening words of the fixed paragraph this block replaced. Kept so the ten documents filed
#: before 2026-09-24 are REPAIRED IN PLACE on their next firing rather than growing a second,
#: contradicting header beside the frozen one.
_LEGACY_COUNTS_OPENER = "**Filed automatically by "


@dataclass(frozen=True)
class DocumentCounts:
    """The two counts an alarm document can establish about itself. See THREE COUNTS at the top.

    Neither is the caller's `repeats`, and none of the three may be summed with another.
    """
    days: int
    members: int
    first: str | None
    last: str | None


def _without_reask_section(text: str) -> str:
    """`text` with the re-ask's own section removed -- see REASK_HEADING."""
    lines = text.splitlines()
    try:
        start = lines.index(REASK_HEADING)
    except ValueError:
        return text
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return "\n".join(lines[:start] + lines[end:])


def _observation_dates(path: Path, text: str) -> set[str]:
    """Every date on which this condition was observed to hold — the DOCUMENT's own answer.

    The filing date in the FILENAME is one of them: it is the first firing, and a document whose
    condition has held for exactly one day would otherwise report zero observations of itself.

    KEPT PURE, and kept as the document's answer alone, even though every caller now wants the
    union with the store. It is the seed `_merged_entry` absorbs and it is what a reader reaches
    for to ask "what would this document say if the store vanished" — which, since the whole claim
    of the store is that it is a SUPERSET, is the only question that can falsify it.
    """
    body = _without_reask_section(text)
    dates = set(_STILL_LIVE_DATE.findall(body)) | set(_INSTANCE_DATE.findall(body))
    filed = _FILENAME_DATE.search(path.name)
    if filed:
        dates.add(filed.group(1))
    return dates


def document_counts(path: Path, text: str | None = None) -> DocumentCounts:
    """What is known about this condition, counted rather than asserted.

    THE NAME IS NOW HALF RIGHT AND IS KEPT ANYWAY. These are the counts the DOCUMENT PUBLISHES,
    which is what every caller means by it; they are no longer derived from the document's own
    text alone, because that text is a rendering that may have been cleared since the last firing.
    The source is the store unioned with whatever the rendering still carries — a superset of the
    old answer in every case, and identical to it for a document nothing has cleared.
    """
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
    entry = absorb(path, text)
    dates = entry["observed"]
    return DocumentCounts(days=len(dates), members=len(entry["instances"]),
                          first=dates[0] if dates else None,
                          last=dates[-1] if dates else None)


def _threshold_line(repeats: int | None) -> str:
    """What to say about `ESCALATE_AFTER_REPEATS` for this document, including when it did not apply.

    AN HONEST ABSENCE, NAMED. The old line read "Repeats before escalation: 1 (threshold
    `ESCALATE_AFTER_REPEATS`)" on every document the four direct callers filed -- which states a
    number BELOW the bar the constant exists to set, next to the constant, as though the bar had
    been cleared. Saying the threshold was never applied is both true and more useful: it tells a
    reader the document's existence is not evidence of sustained repetition, so they should read
    the derived counts above instead of trusting this line.
    """
    if repeats is None:
        return (f"Repeats before escalation: **not measured**. This condition's observer calls "
                f"`escalate()` directly rather than through `notify()`, so there is no transition "
                f"store to count a streak against and `ESCALATE_AFTER_REPEATS` "
                f"(= {ESCALATE_AFTER_REPEATS}) was never applied to it. What the document can "
                f"establish about itself is counted at the top; this is a stated absence, not a "
                f"zero.")
    return (f"Repeats before escalation: {repeats} (threshold `ESCALATE_AFTER_REPEATS` = "
            f"{ESCALATE_AFTER_REPEATS}, applied by `notify()`)")


def _counts_paragraph(counts: DocumentCounts, *, key: str, repeats: int | None,
                      window_h: float) -> str:
    """The derived opening paragraph. Every number in it is read back off the document."""
    if counts.first and counts.last and counts.first != counts.last:
        span = f", between **{counts.first}** and **{counts.last}**"
    elif counts.first:
        span = f", on **{counts.first}**"
    else:
        span = ""
    streak = (
        f"Separately, the observer that last filed reported **{repeats} consecutive firing(s) "
        f"without a state change**, over **{window_h:.1f}h**. That is `notify()`'s streak "
        f"counter, which resets; it is not a total and does not combine with the two counts above."
        if repeats is not None else
        f"This condition's observer calls `escalate()` directly rather than through `notify()`, "
        f"so no consecutive-firing count exists for it and `ESCALATE_AFTER_REPEATS` "
        f"(= {ESCALATE_AFTER_REPEATS}) was never applied. That absence is stated rather than "
        f"filled with a placeholder count."
    )
    derived = (
        f"**Filed automatically by `background/alarm_repetition.py`, not by a person.** This "
        f"condition has been **observed to hold on {counts.days} separate day(s)**{span}, and "
        f"**{counts.members} member(s)** of the family `{family(key) if key else 'unknown'}` have "
        f"fired. Both counts are DERIVED from this document's own dated lines every time the "
        f"alarm fires again, so they age with the document rather than with its first firing."
    )
    # WRAPPED, because these documents are read as RAW TEXT in a draw prompt rather than
    # rendered, and the rest of the body is hand-wrapped at this width.
    return "\n\n".join(textwrap.fill(p, width=95) for p in (derived, streak))


def _refresh_counts(path: Path, *, key: str, repeats: int | None, first_ts: float,
                    now: float) -> bool:
    """Rewrite the counts block from the document's own content. Never raises.

    THE ONE PLACE THE HEADER NUMBERS COME FROM, reached at birth and on every later firing. The
    old code stamped them into the body once and nothing ever touched them again: `STRETCH_LOG`
    led with "fired **3 times**" above a still-live line reading 2132, and four of the seven
    documents carrying still-live lines understated themselves in their own first sentence.

    Three placements, in order, and the third is what makes the repair automatic:
      1. Between the markers, if this document already has them.
      2. Over the legacy fixed paragraph, if it has that instead -- so a document filed before
         2026-09-24 is repaired the next time its condition is observed, with no migration to
         run and nothing to remember.
      3. Immediately after the title, if it has neither. This is the BIRTH path, so the insert
         branch is exercised by every new document rather than only by old ones -- a branch that
         only ran during a migration would be dead code the day the migration finished.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    counts = document_counts(path, text)
    window_h = max(0.0, now - first_ts) / 3600.0
    paragraph = _counts_paragraph(counts, key=key, repeats=repeats, window_h=window_h)
    block = f"{COUNTS_BEGIN}\n{paragraph}\n{COUNTS_END}"

    if COUNTS_BEGIN in text and COUNTS_END in text:
        head, _, rest = text.partition(COUNTS_BEGIN)
        _, _, tail = rest.partition(COUNTS_END)
        updated = head + block + tail
    else:
        lines = text.splitlines()
        start = next((i for i, ln in enumerate(lines)
                      if ln.startswith(_LEGACY_COUNTS_OPENER)), None)
        if start is not None:
            end = start
            while end < len(lines) and lines[end].strip():
                end += 1
        else:
            title = next((i for i, ln in enumerate(lines) if ln.startswith("# ")), None)
            if title is None:
                return False
            start = end = title + 1
            while start < len(lines) and not lines[start].strip():
                start = end = start + 1
        tail = lines[end:]
        while tail and not tail[0].strip():
            tail.pop(0)  # the blank that closed the paragraph we replaced, not a second one
        updated = "\n".join(lines[:start] + block.splitlines() + [""] + tail) + "\n"

    return _write_document(path, updated) is None


# ---------------------------------------------------------------------------------------------
# THE RE-ASK
# ---------------------------------------------------------------------------------------------
# DIRECTOR DIRECTION, 2026-09-23 (Lane 0): *"an alarm document whose condition no longer holds
# archives itself WITH the evidence it re-ran; one whose condition still holds gains an instance
# line rather than sitting unchanged."*
#
# WHAT WAS MISSING. Everything above this line is written by an alarm FIRING. Nothing is written
# by an alarm NOT firing. So a condition that self-clears leaves its document in the staging root
# byte-for-byte identical to one that is still burning, and the nine (now ten) documents in the
# root at ORDER 60 cannot be ranked against each other at all: there is no reading of any of them
# that says whether anyone has looked since it was filed.
#
# WHAT I EXPECTED THE SIGNAL TO BE, AND WHY THAT WAS WRONG. `notify()` stamps `last_seen` into
# `.notify_transitions.json` on every FIRING, so the obvious re-ask is "how long since this
# family's key last moved". MEASURED, 2026-09-23, against the ten live documents: FOUR of the ten
# families have no key in that store at all -- and only ONE of the four is absent because the
# condition cleared (`deadman_origin_fork`; `deadmans_switch` calls `clear_transition()`, which
# DELETES the key, so absence there is a positive clear written by the observer that owns the
# condition). The other three -- `seat-continuity`, `seat-claim:*`, `delivery-lane-stranded:*` --
# call `escalate()` DIRECTLY and never go through `notify()`, so they have never written that
# store and never will. `seat-continuity` stamped a still-live line yesterday and is absent from
# the store; a store-only re-ask would have read it as eight days quiet and archived live work.
# Three of ten, in the fail-open direction. The pre-registration for this is in
# `docs/staging/SEAT_PREREG_WHICH_OF_THE_NINE_ALARM_CONDITIONS_A_RE_ASK_WOULD_FIND_CLEARED_2026-09-23.md`
# and it was refuted on both the split and the mechanism.
#
# THE SIGNAL BOTH POPULATIONS DO WRITE is the document itself. `_note_still_live` and
# `_note_instance` are reached on EVERY call where the document already exists, whether the caller
# came through `notify()` or straight into `escalate()`. So the newest machine-written dated line
# in a document IS the last time that condition was observed to hold, for every family, with no
# registry of observers to keep in step with the code.
#
# THE STORE IS STILL READ, but only ever to CONTRADICT staleness, never to confirm it -- a key
# that fired recently proves the condition holds even if nobody annotated the document, and a key
# that is absent proves nothing either way.


#: How long an alarm document may go with NO observation of its condition before the re-ask reads
#: the silence as the condition having cleared.
#:
#: ORIGIN: measured, 2026-09-23, over the whole live population rather than chosen. All ten
#: documents in `docs/staging/` carry consecutive DAILY still-live lines while their condition
#: holds -- the widest gap any of them shows between two observations is `tree_divergence` at
#: 36.1h. Three days of silence is therefore at least three of that family's own missed cycles,
#: for every family in the population. Deliberately not tighter: a document filed late in the day
#: and re-asked early the next has "yesterday" as its newest line, and one day would archive it.
#:
#: The bar can afford to be this low because archiving is REVERSIBLE BY DESIGN and not by luck:
#: `escalate()` deliberately does not search `done/`, so a condition that returns after being
#: archived files a fresh document and is an R3 two-strike signal. A wrong archive costs one
#: re-filing; a wrong hold costs a permanent unrankable queue item, which is the defect.
REASK_QUIET_DAYS = 3

#: How recently the alarm-filing machinery must have observed SOMETHING for silence to be
#: evidence of anything at all.
#:
#: This is the fail-open leg and it is the whole reason the re-ask has a third verdict. If every
#: observer is down -- a frozen guest, a dead supervisor -- then NO document gains a line, every
#: document looks quiet, and a re-ask without this check would archive the entire queue at exactly
#: the moment the queue was most load-bearing. One day is the same bar as the daily cadence the
#: population demonstrably keeps.
REASK_HEARTBEAT_DAYS = 1

#: The document stem every alarm document carries, and the population the re-ask asks about.
ALARM_DOCUMENT_STEM = "WORKER_FINDING_REPEATING_ALARM_"

STILL_HOLDS = "still_holds"
CLEARED = "cleared"
CANNOT_TELL = "cannot_tell"

#: The three verdicts, as a closed set, so a caller can assert the partition rather than a leg.
REASK_VERDICTS = (STILL_HOLDS, CLEARED, CANNOT_TELL)

@dataclass(frozen=True)
class Reask:
    """One document's re-ask: the verdict AND the evidence it was reached from.

    `reason` is not decoration. A verdict with no stated basis is exactly the shape that made the
    ten documents unrankable in the first place -- the point of the re-ask is that a reader can
    see what was asked and what answered, so `reason` is carried on every verdict including the
    ones nobody will argue with.
    """
    path: Path
    key: str
    family: str
    verdict: str
    last_observed: str | None
    reason: str
    applied: bool = False


def alarm_documents(staging_dir: Path | None = None) -> list[Path]:
    """Every live alarm document: the staging root and `in_progress/`, never `done/`.

    The same two rooms `_live_finding_for` searches and for the same reason -- a document in
    `done/` has been dispositioned and is not the re-ask's business.
    """
    root = staging_dir or STAGING_DIR
    out: list[Path] = []
    for room in (root, root / "in_progress"):
        try:
            out.extend(sorted(room.glob(f"{ALARM_DOCUMENT_STEM}*.md")))
        except OSError:
            continue  # an unreadable room is not evidence that nothing is filed
    return out


def last_observed(path: Path, text: str | None = None) -> str | None:
    """The newest date on which this condition was OBSERVED TO HOLD, as `YYYY-MM-DD`, or None.

    The NEWEST of exactly the dates the counts block COUNTS -- one reader, `_observation_dates`,
    for both. Two readers of the same record would drift, and a re-ask that archived on a
    different set of dates from the one the document's own header reports would be unarguable
    with.
    """
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
    dates = absorb(path, text)["observed"]
    return max(dates) if dates else None


#: The re-ask's own dated line, written by `_note_reask` and `_archive_cleared` and by nothing
#: else. The MIRROR of `_STILL_LIVE_DATE`: that one reads what the ALARM wrote, this one reads
#: what LOOKING wrote, and the two channels are kept apart at `REASK_HEADING` above.
_REASK_DATE = re.compile(r"^- \*\*(\d{4}-\d{2}-\d{2})\*\* — re-asked:", re.M)


def _reask_section(text: str) -> str:
    """Just the re-ask's own section -- the exact complement of `_without_reask_section`.

    THE COMPLEMENT AND NOT A GREP, so the two readers below partition the document rather than
    overlap it. A regex run over the whole text would happen to give the same answer today,
    because only the re-ask writes that phrase; it would stop doing so the first time anybody
    quoted a re-ask line in a hand-written note, and the failure would be silent.
    """
    lines = text.splitlines()
    try:
        start = lines.index(REASK_HEADING)
    except ValueError:
        return ""
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return "\n".join(lines[start:end])


def last_attention(path: Path, text: str | None = None) -> str | None:
    """The newest date on which somebody LOOKED at this document, or None if nobody ever has.

    THE OTHER HALF OF `last_observed`, and the distinction is the whole point. `last_observed`
    answers "when did this condition last hold", which for an alarm is when its own machinery
    last WROTE. This answers "when did anybody last ask whether it still matters". The comment
    above `_STILL_LIVE_DATE` says attention must never masquerade as the thing attention was paid
    to; that cuts both ways, and this is the side of the cut nothing read until now.

    None is a real answer and not a failure: a document with no re-ask section has never been
    looked at since it was filed, and the caller -- `unattended_since` below -- is what decides
    what to do about that.
    """
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
    dates = absorb(path, text)["reasked"]
    return max(dates) if dates else None


def _midnight_utc(date: str) -> float:
    """`YYYY-MM-DD` as a UTC epoch. Raises on anything else, which the caller catches."""
    return datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()


def unattended_since(path: Path, text: str | None = None) -> float:
    """The instant since which nothing has looked at this document, as a UTC epoch.

    ASCENDING IS LONGEST-NEGLECTED-FIRST, which is what makes this usable directly as a queue
    sub-key: `background/staging_rooms.work_queue` sorts the alarm band on it.

    Three sources, in order, and the fallbacks are not defensive padding -- each is the honest
    answer to "when was this last looked at" for a document the one above cannot describe:

      1. The newest re-ask line. Somebody asked, on that date, whether this still matters.
      2. Failing that, the FILING DATE in the filename. Nobody has ever re-asked, so the last
         moment a decision was made about this document is the moment it was filed. A firing does
         not move it, which is the entire difference from `st_mtime`.
      3. Failing that, `0.0` -- the top of the band. A document whose own name will not say when
         it was filed is the one least likely to have been read by anybody, and sending it to the
         front is the direction that gets it looked at rather than the direction that buries it.

    DELIBERATELY NOT `st_mtime` AT ANY STEP, including as a last resort. mtime is the term this
    replaced and it is ANTI-correlated with attention on this population -- every firing rewrites
    the document, so the loudest condition looks freshest. A fallback to it would restore the
    inversion for exactly the documents the other legs could not describe, silently.
    """
    observed = last_attention(path, text)
    if observed:
        try:
            return _midnight_utc(observed)
        except ValueError:
            pass
    filed = _FILENAME_DATE.search(path.name)
    if filed:
        try:
            return _midnight_utc(filed.group(1))
        except ValueError:
            pass
    return 0.0


def _read_transitions_for_reask() -> dict:
    """The notify transition store, or `{}` -- imported late because `notify` imports this module.

    Returns `{}` on ANY failure. That is the safe direction here and only here: the store is used
    exclusively to CONTRADICT a stale-looking document, so an empty read can never manufacture a
    clear, only fail to prevent one -- and the heartbeat leg below still has to pass.
    """
    try:
        from background.notify import TRANSITIONS_FILE
        data = json.loads(Path(TRANSITIONS_FILE).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _family_last_seen(fam: str, transitions: dict) -> float | None:
    """When any member of `fam` last FIRED, from the transition store, or None if it holds none."""
    seen = [float(v.get("last_seen") or v.get("ts") or 0)
            for k, v in transitions.items()
            if isinstance(v, dict) and family(k) == fam]
    return max(seen) if seen else None


def machinery_heartbeat(documents: list[Path], transitions: dict,
                        *, now: float | None = None) -> str | None:
    """The newest DATE on which the alarm-filing machinery observed ANYTHING, or None.

    WHAT THIS PROVES AND WHAT IT DOES NOT, stated here rather than left for a reader to assume:
    it proves that SOME observer reached `escalate()` or `notify()` recently, so silence about one
    family is silence against a working background, not against a stopped one. It does NOT prove
    that the specific observer owning any one family ran. That is a real gap and it is why
    `REASK_QUIET_DAYS` is three of a family's own cycles and not one -- a single observer down for
    a day cannot reach the bar on its own.

    A DATE AND NOT AN EPOCH, deliberately, because the documents can only supply a date. Mixing
    the two was the first draft's defect and it failed in the fail-CLOSED direction rather than
    harmlessly: a date floors to midnight UTC, so a document annotated at 23:00 yesterday read as
    47h old against a 24h bar, and every stale document in the room came back `cannot_tell`
    because the machinery looked dead. Printing the verdicts at the real inputs is what caught it.
    """
    dates: set[str] = set()
    for v in transitions.values():
        if not isinstance(v, dict):
            continue
        stamp = float(v.get("last_seen") or v.get("ts") or 0)
        if stamp > 0:
            dates.add(datetime.fromtimestamp(stamp, timezone.utc).strftime("%Y-%m-%d"))
    for path in documents:
        observed = last_observed(path)
        if observed:
            dates.add(observed)
    return max(dates) if dates else None


def reask(*, staging_dir: Path | None = None, now: float | None = None,
          apply: bool = False) -> list[Reask]:
    """Re-ask every live alarm document whether its condition still holds.

    Three verdicts, and the third is the point:
      STILL_HOLDS  -- observed within `REASK_QUIET_DAYS`, or the transition store says it fired.
                      The document gains a dated re-ask line, so "somebody looked and it is still
                      burning" becomes readable instead of being indistinguishable from nobody
                      having looked.
      CLEARED      -- quiet past the bar, no contradicting firing, and the machinery demonstrably
                      alive. The document archives itself to `done/` carrying the evidence.
      CANNOT_TELL  -- the machinery is quiet, or the document carries no machine-written date at
                      all. Fails CLOSED: the document stays in the queue and gains a line naming
                      the reason, because "we cannot tell" is a result and belongs on the surface.

    `apply=False` (the default) decides everything and writes nothing, so the verdicts can be read
    before they are acted on. Nothing about the decision changes between the two.
    """
    # THE SAME HARD PYTEST GUARD `escalate()` CARRIES, and for a sharper reason: escalate can only
    # ADD a document to the director's queue, and this can REMOVE one. A test run that archived
    # his live queue would be the worst version of the defect this whole module exists to fix.
    target = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    if (os.environ.get("PYTEST_CURRENT_TEST") is not None
            and target.resolve() == (PROJECT_DIR / "docs" / "staging").resolve()):
        return []

    now = time.time() if now is None else now
    today = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d")
    quiet_before = (datetime.fromtimestamp(now, timezone.utc)
                    - timedelta(days=REASK_QUIET_DAYS)).strftime("%Y-%m-%d")
    heartbeat_before = (datetime.fromtimestamp(now, timezone.utc)
                        - timedelta(days=REASK_HEARTBEAT_DAYS)).strftime("%Y-%m-%d")

    documents = alarm_documents(target)
    transitions = _read_transitions_for_reask()
    heartbeat = machinery_heartbeat(documents, transitions, now=now)
    machinery_alive = heartbeat is not None and heartbeat >= heartbeat_before

    out: list[Reask] = []
    for path in documents:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        sig = _SIGNATURE_LINE.search(text)
        key = sig.group(1) if sig else ""
        fam = family(key) if key else ""
        observed = last_observed(path, text)
        fired = _family_last_seen(fam, transitions) if fam else None
        fired_h = None if fired is None else (now - fired) / 3600.0

        if observed is None:
            verdict, reason = CANNOT_TELL, (
                "no machine-written observation date in this document and none in its filename, "
                "so there is nothing to date the silence from")
        elif observed > quiet_before:
            verdict, reason = STILL_HOLDS, (
                f"observed {observed}, within the {REASK_QUIET_DAYS}-day bar")
        elif fired_h is not None and fired_h <= REASK_QUIET_DAYS * 24:
            # THE STORE CONTRADICTING THE DOCUMENT. Only ever in this direction: a firing proves
            # the condition holds, so it overrules a stale-looking document. The reverse -- an
            # absent key read as a clear -- is the fail-open move this leg exists instead of.
            verdict, reason = STILL_HOLDS, (
                f"document last annotated {observed}, but `{fam}` fired {fired_h:.1f}h ago in the "
                "notify transition store, which contradicts the silence")
        elif not machinery_alive:
            verdict, reason = CANNOT_TELL, (
                f"quiet since {observed}, but the alarm-filing machinery itself last observed "
                f"anything on {heartbeat or 'no date at all'} (bar is {heartbeat_before}), so "
                "this silence is not evidence about the condition — it is evidence about the "
                "observers")
        else:
            verdict, reason = CLEARED, (
                f"no observation since {observed}, past the {REASK_QUIET_DAYS}-day bar; "
                + (f"`{fam}` last fired {fired_h:.1f}h ago" if fired_h is not None
                   else f"no key for `{fam}` in the notify transition store")
                + f"; and the machinery observed other conditions on {heartbeat}, so the "
                  "silence is the observers running and not seeing it")

        r = Reask(path=path, key=key, family=fam, verdict=verdict,
                  last_observed=observed, reason=reason)
        if apply:
            r = _apply_reask(r, today=today)
        out.append(r)
    return out


def _apply_reask(r: Reask, *, today: str) -> Reask:
    """Act on one verdict. Never raises: a re-ask that cannot write is not a re-ask that lies."""
    try:
        if r.verdict == CLEARED:
            return Reask(**{**r.__dict__, "applied": _archive_cleared(r, today=today)})
        return Reask(**{**r.__dict__, "applied": _note_reask(r, today=today)})
    except OSError:
        return r


def _note_reask(r: Reask, *, today: str) -> bool:
    """Record that the condition WAS re-asked today, and what the answer was.

    Idempotent per day per verdict: a re-ask that runs every tick must not turn one document into
    forty-eight lines, which is the pile rebuilt inside one file -- the exact defect
    `_note_still_live` learned the same way. Keyed on the verdict as well as the date so a
    document that changes answer within a day records BOTH, because that transition is the news.
    """
    marker = f"- **{today}** — re-asked: **{r.verdict}**."
    _record(r.path, reasked=today)
    try:
        text = r.path.read_text(encoding="utf-8")
    except OSError:
        return False
    if marker in text:
        return False
    return _write_document(r.path,
                           _append_under(text, REASK_HEADING, f"{marker} {r.reason}.")) is None


def _archive_cleared(r: Reask, *, today: str) -> bool:
    """Move a cleared document to `done/` carrying the evidence the re-ask ran.

    NEVER OVERWRITES. A file already in `done/` under this name is an EARLIER EPISODE of the same
    family, and an archival that clobbered it would destroy the only record that the condition has
    returned before -- which is the R3 two-strike signal the whole no-searching-`done/` rule
    exists to preserve. A collision gets a suffix, never a silent replacement.
    """
    try:
        text = r.path.read_text(encoding="utf-8")
    except OSError:
        return False
    body = _append_under(text, REASK_HEADING, (
        f"- **{today}** — re-asked: **{CLEARED}**. {r.reason}.\n"
        f"\n"
        f"## Re-asked and cleared, {today}\n"
        f"\n"
        f"Archived by `background/alarm_repetition.reask()`, not by a person, and not because "
        f"anybody diagnosed it.\n"
        f"\n"
        f"- **What was asked:** has the condition behind `{r.key or 'an unparseable signature'}` "
        f"been observed to hold since it was last annotated?\n"
        f"- **Last observation:** {r.last_observed}\n"
        f"- **The answer, and what carried it:** {r.reason}.\n"
        f"- **What this does NOT claim:** that the condition was fixed, or why it stopped. Only "
        f"that nothing has observed it for {REASK_QUIET_DAYS} days while the observers were "
        f"demonstrably running. If it returns it files a FRESH document — `escalate()` does not "
        f"search `done/` — and that fresh document is an R3 two-strike signal worth more than "
        f"this one was.\n"))
    archive = r.path.parent / ARCHIVE_ROOM if r.path.parent.name != "in_progress" \
        else r.path.parent.parent / ARCHIVE_ROOM
    archive.mkdir(parents=True, exist_ok=True)
    dest = archive / r.path.name
    n = 2
    while dest.exists():
        dest = archive / f"{r.path.stem}_REASK_{n}{r.path.suffix}"
        n += 1
    if _write_document(dest, body) is not None:
        return False
    # BEFORE THE UNLINK, so a crash between the two leaves the document in place with its history
    # retired rather than the document gone with its history live -- the direction that would make
    # a returning condition inherit the closed episode's dates.
    _close_episode(r.path, today=today)
    r.path.unlink()
    return True


#: The archive room. Named here rather than imported from `background.staging_rooms`
#: (`ARCHIVE_DIRNAME`) only because that module imports heavily and this one is reached from
#: inside `notify()`, which must stay cheap and must never fail for a reason of its own.
ARCHIVE_ROOM = "done"


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Re-ask whether each alarm document's condition holds")
    p.add_argument("--reask", action="store_true", help="report a verdict per alarm document")
    p.add_argument("--apply", action="store_true",
                   help="with --reask, act: annotate the live ones, archive the cleared ones")
    a = p.parse_args(argv)
    if not a.reask:
        p.print_help()
        return 2
    results = reask(apply=a.apply)
    if not results:
        print("no alarm documents")
        return 0
    width = max(len(r.path.name) for r in results)
    for r in sorted(results, key=lambda r: (REASK_VERDICTS.index(r.verdict), r.path.name)):
        print(f"{r.verdict:<12} {r.path.name:<{width}}  {r.reason}")
    counts = {v: sum(1 for r in results if r.verdict == v) for v in REASK_VERDICTS}
    print("\n" + " · ".join(f"{v}: {counts[v]}" for v in REASK_VERDICTS)
          + (f" · applied: {sum(1 for r in results if r.applied)}" if a.apply else " (reported only)"))
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/alarm_repetition.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("alarm_repetition")
    raise SystemExit(main())
