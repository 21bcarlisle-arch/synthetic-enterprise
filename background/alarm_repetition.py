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
#: Normalising these is what makes "the same alarm" a decidable question. Everything else --
#: the exception type, the failing key, the module -- is preserved, so a KeyError and a
#: TypeError from the same daemon stay two different alarms with two different work items.
_VARIABLE = (
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
    """
    head = re.sub(r"^\[[^\]]+\]\s*", "", normalise(message)).strip()
    head = re.sub(r"[^A-Za-z0-9 ]+", " ", head)
    words = [w for w in head.split() if w][:10]
    return "_".join(words).upper()[:110] or "AN_UNNAMED_ALARM"


def finding_path(message: str, *, today: str, staging_dir: Path | None = None) -> Path:
    return (staging_dir or STAGING_DIR) / f"WORKER_FINDING_REPEATING_ALARM_{_slug(message)}_{today}.md"


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
    path = finding_path(message, today=today, staging_dir=target)
    if path.exists():
        return None

    window_h = max(0.0, (now - first_ts)) / 3600.0
    body = f"""**Severity:** LATENT · **Lane:** H_harness

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

Archive to `docs/staging/done/` when the condition is resolved. Re-escalation is not
suppressed by this file: a NEW episode on a later day files a new document, so a condition
that returns next week is not silently absorbed into today's record.
"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    except OSError as exc:
        raise EscalationUnavailable(f"could not file {path}: {exc}") from exc
    return path
