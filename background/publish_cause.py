"""THE ATTRIBUTED CAUSE OF A PUBLISH THAT DID NOT LAND — one name, and the evidence for it.

WHY THIS MODULE EXISTS (2026-08-30, nine hours and nine episodes with no attribution)
-------------------------------------------------------------------------------------
`process_run_complete.git_commit_push` KNOWS which of its failure paths it took. It names one
of `COMMIT_REFUSED` / `COMMIT_TIMEOUT` / `PUSH_DID_NOT_REACH_ORIGIN` / `PROVENANCE_REFUSED`,
acts on it (the fingerprint decision), and then collapses all four into the single exit code
`EXIT_PUBLISH_DID_NOT_LAND` (77). The wedge router runs in a DIFFERENT PROCESS, sees only that
code, and writes the record every reader then works from:

    "the publish COMMIT did not land ... the commit was refused/timed out/never reached origin"

Three alternatives in one sentence is not a diagnosis. Observed in
`docs/observability/.publish_gate_state.json` on 2026-08-30: `wedge_since` 05:27:59Z,
`episode_failures: 9`, `total_red: 0`, and that same sentence on every entry — nine consecutive
episodes producing no attribution at all, while `origin/main` sat five commits behind HEAD. The
answer was in the publisher's own hands at the moment of failure each time and was thrown away
between processes.

This is the same class as the record this module sits beside (`publish_gate_blocking_read`): a
diagnostic that WAS taken and then dropped at the record layer. R15 FAIL-SILENT.

THE EVIDENCE IS OBSERVED, NEVER INFERRED FROM THE EXIT STATUS
--------------------------------------------------------------
That is the whole point, and it is why this is a record and not a lookup table on rc. Each
cause is separable at the moment it happens, by a different observation:

  * `gate_refusal`      — `git commit` returned a code and the hook chain named (or did not
                          name) reds. The rc and the red count ARE the evidence.
  * `deadline_kill`     — an elapsed wall time against the publisher's own budget. A stopwatch,
                          not a status.
  * `push_never_landed` — `git ls-remote` says the remote ref did not advance to local HEAD.
                          The REF is the evidence; a push can return 0 and land nothing, which
                          is the 3.5-hour origin-freeze of 2026-07-24.
  * `provenance_refused`— the fail-closed stamp check refused before any git ran.

Four, not the three the direction named: `provenance_refused` is a real fourth path to rc=77,
and folding it into one of the three to make the count match would be exactly the invention
this module exists to stop. The contract is "names EXACTLY ONE", not "one of exactly three".

FAIL-CLOSED, AND KEYED TO THE COMMIT IT IS ABOUT
-------------------------------------------------
`read_cause` answers `UNATTRIBUTED` for absent, unreadable, malformed, stale AND
git-hash-mismatched. The last of those is the one that matters and it is not defensive
boilerplate: a record left by an EARLIER cycle is evidence about a different cycle, and citing
it is precisely the carried-forward-blocking-list defect this repo has already paid four clocks
for. An unattributed failure says so in those words. "We cannot tell" is a result.

Nothing here is keyed to a current wedge, a current commit, or a current streak. The record is
written by whichever cycle fails and refused by any reader looking at a different one, so the
mechanism is unchanged by today's episode clearing on its own.

NO-TEST-JUDGED IS A PROPERTY OF THE CAUSE
------------------------------------------
`NO_TEST_JUDGED_CAUSES` is what makes the attribution ACT rather than merely read better. On a
deadline kill the suite was killed mid-verdict; on a push failure the hook chain passed and the
commit landed; on a provenance refusal nothing ran at all. In none of those three did any test
go red — so the alarm must not attach a blocking list or suspects, which on those causes are
whatever an earlier cycle left behind. Naming nobody beats naming the innocent.

`gate_refusal` is deliberately NOT in that set: there the hook chain did judge, and
`_record_commit_refusal_reds` writes its reds against the same git hash in the same moment.

REUSE: background/publish_cause.py
CLASS: CUSTOM
INDEX: searched "publish cause", "gate failure kind", "attribution record" — the closest row is
       `background/publish_gate_blocking_read.py`, which reads the BLOCKING record (which tests
       are red). That answers a different question and cannot answer this one: on three of the
       four causes here no test is red at all, which is the fact being recorded. The kind
       vocabulary in `process_run_complete._gate_failure_label` is a LABEL for an rc, keyed to
       exit codes rather than to observations, and widening it would have needed a fifth and
       sixth exit code to carry a distinction the publisher already holds in a variable. Written
       new, as a stdlib-only leaf, for the same reason `publish_gate_blocking_read` is one: the
       supervisor's RUNG-1 draw must be able to ask this without importing the publish path.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from background.live_ledger_guard import guard_live_ledger_write

#: The publish COMMIT was refused — by git itself or by a pre-commit gate. A red MAY exist.
GATE_REFUSAL = "gate_refusal"
#: The pre-commit hook chain outran the publisher's deadline and was killed. Nothing was judged.
DEADLINE_KILL = "deadline_kill"
#: The commit landed locally and origin did not move. Verified against the remote ref.
PUSH_NEVER_LANDED = "push_never_landed"
#: The fail-closed provenance check refused before git ran. Nothing was staged, judged or sent.
PROVENANCE_REFUSED = "provenance_refused"
#: Not a cause: the honest answer when no usable record exists for the failure being described.
UNATTRIBUTED = "unattributed"

#: Every cause this module will accept a write for. A write naming anything else is refused
#: rather than stored, because a reader that trusts the field must be able to trust the set.
CAUSES = frozenset({GATE_REFUSAL, DEADLINE_KILL, PUSH_NEVER_LANDED, PROVENANCE_REFUSED})

#: Causes on which NO test returned a verdict, so no blocking list or suspect may be attached.
#: See the module docstring. `GATE_REFUSAL`'s absence is the content of this set, not an
#: oversight — that is the one cause where a named red is real evidence about THIS cycle.
NO_TEST_JUDGED_CAUSES = frozenset({DEADLINE_KILL, PUSH_NEVER_LANDED, PROVENANCE_REFUSED})

#: Mirrors the publisher's blocking-record bound for the same reason that one has a default:
#: a reader outside the publish path must not import the publisher to learn a policy. Held
#: equal by a control, never by memory.
DEFAULT_MAX_AGE_SECONDS = 2 * 3800


def record_cause(path, cause, evidence, git_hash, *, now=None) -> bool:
    """Write the attributed cause of ONE non-landing publish cycle. Never raises.

    Returns True iff a record was written. An unrecognised `cause` writes NOTHING and returns
    False: a record whose cause is outside `CAUSES` would be read by a caller that believes the
    set is closed, and a wrong name is worse than the absence that reads as "we cannot tell".
    """
    if cause not in CAUSES:
        return False
    try:
        p = Path(path)
        # THE LIVE-LEDGER GUARD, and it is not decoration (adopted 2026-08-30). This module's
        # writer was the 75th un-guarded observability writer against a ratchet floor of 74, and
        # `tests/background/test_live_ledger_guard.py` reads the WORKING TREE -- so an untracked
        # file refused EVERY commit in the repository. Publishing was down for ten hours on it,
        # which means the module written to attribute a non-landing publish was itself the cause
        # of one. The ratchet's own message says the honest response is to widen the guard rather
        # than the bound, so that is what this is.
        guard_live_ledger_write(path, writer="publish_cause.record_cause")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(
            {"ts": time.time() if now is None else float(now),
             "cause": str(cause),
             "evidence": str(evidence or "")[:600],
             "git_hash": str(git_hash)},
            sort_keys=True))
        return True
    except (OSError, TypeError, ValueError):
        return False


def read_cause(path, git_hash, *, now=None, max_age=DEFAULT_MAX_AGE_SECONDS):
    """(cause, evidence) for the failure at `git_hash`, or (UNATTRIBUTED, why-not).

    The second element is ALWAYS a sentence a reader can act on: on an attribution it is the
    observation that decided it, and on `UNATTRIBUTED` it is why no attribution was available.
    A reader is never handed a bare "unknown" it has to interpret.
    """
    now = time.time() if now is None else float(now)
    p = Path(path)
    try:
        rec = json.loads(p.read_text())
    except FileNotFoundError:
        return UNATTRIBUTED, ("the publisher recorded no cause for this cycle -- so which of "
                              "the four it was is NOT established here")
    except (json.JSONDecodeError, OSError, ValueError):
        return UNATTRIBUTED, ("the publisher's cause record is unreadable -- so which of the "
                              "four it was is NOT established here")
    if not isinstance(rec, dict):
        return UNATTRIBUTED, "the publisher's cause record is malformed (not an object)"
    ts = rec.get("ts")
    if not isinstance(ts, (int, float)) or now - float(ts) > max_age:
        return UNATTRIBUTED, ("the publisher's cause record is older than this alarm's bound, "
                              "so it describes a different cycle")
    cause = rec.get("cause")
    if cause not in CAUSES:
        return UNATTRIBUTED, "the publisher's cause record names no recognised cause"
    recorded_hash = rec.get("git_hash")
    if str(recorded_hash) != str(git_hash):
        # THE ONE THAT MATTERS. An in-window record from ANOTHER commit is evidence about
        # another cycle; citing it is the carried-forward-blocking-list defect wearing a new
        # field name. Say which commit it was about, so the reader can see that for themselves.
        return UNATTRIBUTED, ("the only cause on record is for git={}, and this failure is at "
                              "git={} -- it describes a different cycle, so nothing is claimed "
                              "about this one").format(str(recorded_hash)[:9], str(git_hash)[:9])
    evidence = rec.get("evidence")
    return str(cause), (str(evidence) if isinstance(evidence, str) and evidence.strip()
                        else "recorded with no evidence line")


def no_test_was_judged(cause) -> bool:
    """Did this cause leave every test unjudged? Unattributed answers False, deliberately.

    FAIL-SAFE DIRECTION IS TOWARD SHOWING THE BLOCKING LIST. Suppressing it when a test really
    IS red would tell a reader not to look for the red, which is unsafe; showing a stale one is
    misdirection the surrounding prose already labels. So only a POSITIVELY attributed
    no-test-judged cause suppresses, and "we cannot tell" never does."""
    return cause in NO_TEST_JUDGED_CAUSES
