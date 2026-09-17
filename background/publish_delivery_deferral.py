"""A PUBLISH WHOSE COMMIT LANDED AND WHOSE PUSH LOST A RACE — the verdict is HELD, then graded
on the remote ref, not declared while the mechanism that delivers it is still mid-turn.

WHY THIS MODULE EXISTS (2026-09-17, a 7.2-day publish wedge and 58 recorded "failures")
--------------------------------------------------------------------------------------
`.publish_gate_state.json` read `episode_failures: 58`, `last_clean_publish: null`,
`wedge_since` 7.2 days, `total_red: 0`, `blocking_tests: []` — 58 consecutive publishing
failures with no red test anywhere. The publisher's own evidence line on failure #58:

    the commit LANDED locally (HEAD 84c8bdee7) and `git ls-remote` shows origin/main at
    c57a03f6d, which does NOT contain it -- `origin_reconcile` was run to absorb this disjoint
    publish and origin STILL does not have it -- the hook chain passed, so no test is implicated

And `84c8bdee7` **is on origin now**. It got there minutes after the publisher exited, carried by
the very cadence its own evidence line named. So the verdict was not merely pessimistic: it was
taken before the thing it was about had finished happening, and every cycle took it again.

THE RACE, MEASURED (docs/staging/WORKER_RESULT_THE_FIFTY_EIGHT_FAILURE_PUBLISH_EPISODE_HAS_NO_
RED_TEST_AND_THE_WEDGE_IS_A_MERGE_TO_PUSH_RACE_2026-09-17.md):

  * `origin_reconcile` merge -> gate -> push, end to end:  **556 s**
  * the sibling lane's push interval at the time:          **~600 s**

The reconciler merges, gates clean, and pushes. Origin moves during the ~9-minute gate, git
rejects the push non-fast-forward, and that whole gate run is spent. Won by hand on the second
attempt in the same tick — so the repair is to let the cadence have its turn, not to re-roll the
dice inside a publish cycle that cannot afford one.

WHY NOT SIMPLY RETRY INSIDE THE CYCLE. `PUBLISH_PATH_ALLOWANCE_SECONDS` is 900 s and covers
everything after the gate returns green — site regeneration, the report, the mirror, the
hook-chain commit at `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` (880 s) and the push. One 556-second
absorbing cadence barely fits; a second one cannot, and the director ruled on 2026-08-21 that no
gate budget grows here. A retry loop inside the cycle would be killed by the publisher's own
wrapper and recorded as `deadline_kill` — an attribution strictly worse than the one it replaced.

WHAT IS HELD, AND WHAT THAT COSTS
----------------------------------
The record here says: a gated commit exists locally, its push lost a race over paths this commit
does not write, and the absorbing cadence owns delivery. It is NOT a claim that the publish
succeeded, and nothing in this module can make one. `REACHED` is answerable only from the remote
ref — the caller reads `git ls-remote` and hands the answer in.

SILENCE IS BOUNDED, AND NOT BY A NUMBER OF THIS MODULE'S OWN. `verdict` takes `benign_seconds`
from its caller, which borrows `deadmans_switch.RACE_PERSISTENCE_SECONDS` — the quantity this
machine ALREADY declares for "when a lost push race stops being benign", derived there from
`BLOCKED_THRESHOLD_SECONDS` ("how long may work sit undelivered before that is worth a person's
attention"). Minting a second tolerance for one condition is how one name comes to carry two
values, and the deadman's comment says so at the constant itself. Past that window the verdict is
`OVERDUE` and the caller records a real failure with a re-measured cause.

FAIL-CLOSED IS TOWARD THE ALARM, ON EVERY BRANCH. An unreadable record, a record with no sha, an
unstamped record: all `OVERDUE`, because the alternative is a deferral that can never expire and
therefore a wedge that can never be reported. A remote we could not read is never `REACHED`, and
past the window it is `OVERDUE` with the evidence line saying the ref was unreadable rather than
claiming a race nobody observed.

REUSE: background/publish_delivery_deferral.py
CLASS: CUSTOM
INDEX: searched "publish deferral", "push deferred", "delivery verdict", "publish cause". The two
       closest rows are siblings and neither can answer this:
         * `background/publish_cause.py` records WHICH cause a non-landing cycle had, for a reader
           in another process. It is keyed to a failure that has already been decided; the whole
           content here is that the decision is not due yet.
         * `background/publish_freshness.py` records WHEN content was last published and is
           reachable from the one call site that has proved origin advanced. It is the stamp taken
           after this module's `REACHED`, not a way of getting there.
       `COMMITTED_PUSH_THROTTLED` is the nearest existing OUTCOME with this shape — committed,
       delivery not yet attempted — and it needs no ledger because the next cycle simply pushes.
       Here the next cycle cannot: the delivery is with a different mechanism, so what the
       outstanding delivery IS has to be written down somewhere a later process can read it.
       Written new, stdlib-only, for the reason `publish_cause` is a leaf: the verdict writer must
       be able to ask this without importing the publish path.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from background.episode_monotonic import recorded_instant_seconds
from background.live_ledger_guard import guard_live_ledger_write

#: The deferred commit is on origin, read from the remote ref. The publish HAPPENED.
REACHED = "reached"
#: Not on origin yet, and the window this machine itself calls benign has not expired.
ABSORBING = "absorbing"
#: Not on origin, and the benign window is spent. A failure is owed and its cause is nameable.
OVERDUE = "overdue"
#: No delivery is outstanding. Not a verdict about anything.
NONE = "none"

#: How much of the caller's evidence sentence is kept. Mirrors `publish_cause`'s bound for the
#: same reason that one has one: a record that can grow without limit is a record that can fill
#: a disk the publish path needs.
EVIDENCE_CHARS = 600


def record(path, sha, git_hash, evidence, *, now=None) -> bool:
    """Write the ONE outstanding delivery. Never raises; returns True iff a record was written.

    A record with no `sha` is refused rather than stored: the whole point of the record is that a
    later process can ask the remote about a specific commit, and a deferral naming no commit
    would be graded `OVERDUE` forever — an alarm with no subject.
    """
    if not str(sha or "").strip():
        return False
    try:
        p = Path(path)
        # The live-ledger guard, for the reason `publish_cause.record_cause` gives at its own
        # call: a test process that writes here would hand the next real cycle a fixture's
        # deferral to grade, and the grading records a publish-gate failure.
        guard_live_ledger_write(path, writer="publish_delivery_deferral.record")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(
            {"ts": (float(now) if now is not None else time.time()),
             "sha": str(sha),
             "git_hash": str(git_hash),
             "evidence": str(evidence or "")[:EVIDENCE_CHARS]},
            sort_keys=True))
        return True
    except (OSError, TypeError, ValueError):
        return False


def read(path):
    """The outstanding delivery record, or None for absent/unreadable/malformed.

    None means "no record I can read", and `verdict` splits those two experiences: absent is
    `NONE` (nothing is outstanding), unreadable is `OVERDUE` (something was, and I can no longer
    say what) — which is why this returns a plain None and the SPLIT is made by the caller that
    knows whether the file exists.
    """
    try:
        rec = json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return None
    return rec if isinstance(rec, dict) else None


def clear(path) -> None:
    """Retire the record once a verdict has been TAKEN on it. Never raises.

    Called on `REACHED` and on `OVERDUE` alike: both are verdicts, and a record left behind a
    verdict is the carried-forward-blocking-list defect this repo has already paid four clocks
    for — the next cycle would grade the same delivery again and record a second failure for one
    publish.
    """
    try:
        Path(path).unlink()
    except (FileNotFoundError, OSError):
        return


def verdict(path, *, reached, now, benign_seconds):
    """(status, evidence) for the outstanding delivery. `status` is one of the four constants.

    `reached` is the caller's answer from the REMOTE REF — True/False/None, where None is "I could
    not read origin". It is threaded in rather than measured here so this module stays a leaf and
    so there is exactly one reader of `git ls-remote` on the publish path.

    THE AGE IS WHAT SEPARATES ABSORBING FROM OVERDUE, and `recorded_instant_seconds` is what
    screens it: `0`, `False` and `NaN` all mean "nobody stamped this", and the last of those is
    the one that matters — `now - NaN > window` is False, so an unstamped record would read as
    benign forever and the deferral could never expire.
    """
    if not Path(path).exists():
        return NONE, "no publish delivery is outstanding"
    rec = read(path)
    if rec is None:
        return OVERDUE, ("a delivery deferral exists and is unreadable, so which commit was "
                         "owed cannot be established -- a verdict is owed rather than withheld, "
                         "because a deferral that cannot expire cannot be reported")
    sha = str(rec.get("sha") or "")
    if not sha.strip():
        return OVERDUE, ("the delivery deferral names no commit, so the remote cannot be asked "
                         "about it -- graded overdue rather than held open forever")
    if reached is True:
        return REACHED, ("the deferred publish commit {} IS on origin, read from the remote ref "
                         "-- the absorbing cadence delivered it after this publisher had "
                         "exited".format(sha[:9]))
    recorded = recorded_instant_seconds(rec.get("ts"))
    if recorded is None:
        return OVERDUE, ("the delivery deferral for {} carries no usable timestamp, so how long "
                         "it has been outstanding is NOT established -- graded overdue, because "
                         "an unaged deferral would read as benign forever".format(sha[:9]))
    waited = max(0.0, float(now) - recorded)
    try:
        window = max(0.0, float(benign_seconds))
    except (TypeError, ValueError):
        # An unreadable window is not a licence to wait. See the module docstring: fail-closed
        # here means toward the alarm, so the deferral expires immediately.
        window = 0.0
    seen = ("origin does not contain it" if reached is False
            else "origin could not be read, so its absence is not established either")
    if waited <= window:
        return ABSORBING, ("the publish commit {} landed and is gated; {}; it has been with the "
                           "absorbing cadence for {:.0f}s of the {:.0f}s this machine calls "
                           "benign".format(sha[:9], seen, waited, window))
    return OVERDUE, ("the publish commit {} landed and is gated, and after {:.0f}s -- past the "
                     "{:.0f}s this machine itself calls benign for a lost push race -- {}. The "
                     "push WAS issued and git rejected it non-fast-forward; the absorbing "
                     "cadence has had its turn and the commit is still not delivered"
                     .format(sha[:9], waited, window, seen))
