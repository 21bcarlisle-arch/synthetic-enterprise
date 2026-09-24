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
  * `behind_origin`     — `git rev-list --count HEAD..FETCH_HEAD` is non-zero (or unreadable)
                          BEFORE the commit. A fetched ref, read ahead of the commit, is what
                          separates this from `push_never_landed`.
  * `lost_push_race`    — `git ls-remote`, read AFTER the absorbing cadence has had its turn and
                          the benign window has expired. The observation that separates it from
                          `push_never_landed` is git's own non-fast-forward rejection on stderr
                          plus a second, later read of the ref — one read cannot tell a race
                          from a standstill, which is why 58 races were filed as standstills.

  * `scoped_suite_red` /
    `scoped_gate_unjudged`— the publisher's OWN pytest run, made BEFORE any commit is attempted.
                          The observation is the pair (the suite's return code, whether it named
                          a node id): rc>0 with a FAILED line is a judged red, rc<0 or rc>0 with
                          no FAILED line is a gate that refused without judging. Added 2026-09-24
                          as the sixth cause of the publish outage series — this refusal was the
                          one exit in the module that still left by a bare `return 1`, so every
                          reader inferred `test_regression` from it whatever had happened.

Five, not the three the direction named: `provenance_refused` and `behind_origin` are real paths
to rc=77, and folding either into one of the three to make the count match would be exactly the
invention this module exists to stop. The contract is "names EXACTLY ONE", not "one of exactly
three". `behind_origin` was added on 2026-09-01, when the publish loop's own retry was found to
be widening the fork it was blocked by: it committed, was rejected non-fast-forward, left the
throttle untouched, and did it again twelve minutes later. Recorded as `push_never_landed` every
time, which is true and sends the reader to the wrong repair — the ref did not advance, but the
fixable fact was that the commit should never have been made.

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
commit landed; on a provenance refusal nothing ran at all; on a behind-origin refusal git was
never invoked past the read. In none of those four did any test go red — so the alarm must not
attach a blocking list or suspects, which on those causes are whatever an earlier cycle left
behind. Naming nobody beats naming the innocent.

`gate_refusal` is deliberately NOT in that set: there the hook chain did judge, and
`_record_commit_refusal_reds` writes its reds against the same git hash in the same moment.

ONE NAME OVER TWO EXPERIENCES — THE 2026-09-02/03 CORRECTION
-------------------------------------------------------------
The paragraph above was right about the cause it described and wrong about the set of cycles
that reach it, and the correction stands here beside the claim rather than replacing it. "The
hook chain did judge" is true only when the gate that refused WAS the test gate. The chain runs
several gates before it, each able to short-circuit the whole thing: the orphan ratchet, the
finding-class consolidation gate, the write-time gate, the level-promotion gate. When one of
those refuses, `git commit` returns non-zero having run NO test — and `gate_refusal` was
recorded anyway, which told every reader the opposite of what happened.

OBSERVED, and it is the reason this exists (2026-09-02, 18.7 hours of publishing down):
`tools/artefact_rerun_diff.py` sat staged and unfrozen, so the orphan ratchet refused every
publish commit in the tree. The publisher's own log printed the banner verbatim —
`orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS` — and two lines later recorded
`Publish commit REFUSED with no FAILED/ERROR summary ... recording NO blocking test`. Because
the cause was `gate_refusal`, `no_test_was_judged` answered False, the suppression below never
fired, and `.publish_gate_state.json` went on naming five tests in
`test_a_staged_document_no_longer_blocks_every_landing.py` as the blockers. Those five were
GREEN — 20 passed in 0.09s — and had been left behind by an earlier cycle at a different commit.
For hours the register sent every reader to run a suite that was never the problem, while the
answer sat in the line above it.

So the split is by the OBSERVATION, exactly like the other five: did the hook chain's output
name a red test, or did it name a gate? `NON_TEST_GATE_REFUSAL` is the second, it belongs in
this set because nothing was judged on it, and the gate's own name travels in the evidence line
so the record points at the thing that actually refused. A register that names five green tests
is worse than one that says nothing, because it is confidently wrong about where to look.

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

from background.episode_monotonic import recorded_instant_seconds
from background.live_ledger_guard import guard_live_ledger_write

#: The publish COMMIT was refused by the pre-commit hook chain AND the hook chain named at least
#: one red test. The named reds are evidence about THIS commit.
GATE_REFUSAL = "gate_refusal"
#: The publish COMMIT was refused by a NAMED NON-TEST gate — the orphan ratchet, the finding-class
#: consolidation gate, the write-time gate, the level-promotion gate. Those gates run BEFORE the
#: test gate in the chain and short-circuit it, so no test returned a verdict. See the docstring
#: section below: this is the half of `GATE_REFUSAL` that was wrongly assumed to have judged.
NON_TEST_GATE_REFUSAL = "non_test_gate_refusal"
#: The pre-commit hook chain outran the publisher's deadline and was killed. Nothing was judged.
DEADLINE_KILL = "deadline_kill"
#: The commit landed locally and origin did not move. Verified against the remote ref.
PUSH_NEVER_LANDED = "push_never_landed"
#: The fail-closed provenance check refused before git ran. Nothing was staged, judged or sent.
PROVENANCE_REFUSED = "provenance_refused"
#: Origin was AHEAD of local HEAD (or unreadable) when the publish path was about to commit, so
#: the commit was refused before it was created. Distinct from `PUSH_NEVER_LANDED`, which is the
#: same fork observed one commit too late: there the local commit already exists and the fork is
#: one wider. The observation is `git rev-list --count HEAD..FETCH_HEAD` after a fetch.
BEHIND_ORIGIN = "behind_origin"
#: The commit landed locally and gated, the push WAS issued, git rejected it non-fast-forward
#: because origin moved while the absorbing merge was being gated, and the absorbing cadence has
#: since had its turn and STILL not delivered it. Re-measured against the remote ref after the
#: cadence, never inferred from the push's rc — see `publish_delivery_deferral`.
#:
#: DISTINCT FROM `PUSH_NEVER_LANDED`, and the distinction is the repair. There the ref stood still
#: with NOTHING to explain it: a phantom "Everything up-to-date", auth, a dead remote — a push to
#: be MADE. Here the push was made and lost a race that is measured at 556s of gate against a
#: ~600s sibling push interval — a race to be WON. For 58 consecutive cycles over 7.2 days every
#: one of these was filed as the other, which sent every reader at a push that was being issued
#: correctly every time.
LOST_PUSH_RACE = "lost_push_race"
#: THE PUBLISHER'S OWN SCOPED GATE ran and at least one test came back RED. A test WAS judged, at
#: a sha the record names, so the blocking list is evidence about THIS cycle. Distinct from
#: `GATE_REFUSAL` on the axis of WHICH GATE: that one is the pre-commit hook chain refusing a
#: publish COMMIT, this one is the pytest run `process_run_complete` makes for itself BEFORE any
#: commit is attempted. Folding them together would send a reader to the hook output when the
#: answer is in the publisher's own suite, and the two run at different shas.
SCOPED_SUITE_RED = "scoped_suite_red"
#: THE PUBLISHER'S OWN SCOPED GATE refused and NO test returned a verdict — the pytest child was
#: killed by a signal (rc<0, observed rc=-15 on four separate days), pytest exited non-zero
#: without a FAILED/ERROR summary line (collection error, usage error, nothing collected), or the
#: gate had no subject at all because a clean HEAD checkout could not be materialised. The
#: OBSERVATION that separates it from `SCOPED_SUITE_RED` is the pair (the suite's return code,
#: whether any node id was named) — both held by `_run_gate_in` at the moment it happens.
SCOPED_GATE_UNJUDGED = "scoped_gate_unjudged"
#: Not a cause: the honest answer when no usable record exists for the failure being described.
UNATTRIBUTED = "unattributed"

#: What makes a top-level field of `.publish_gate_state.json` a REFUSAL RECORD in this module's
#: vocabulary: one cycle's attributed cause, stamped and hashed. Today `liveness_surface_refusal`
#: is the only one. The scan in `held_refusal` is by SUFFIX rather than against a hard-coded list
#: because the failure this module exists to stop is an answer nobody thought to look for -- a
#: list would have to be remembered on the day the second surface starts recording its refusals,
#: and the whole defect being repaired here is that nobody remembered to look in the field beside
#: the one they read.
REFUSAL_FIELD_SUFFIX = "_refusal"
#: ...and the publish record that RETIRES a refusal of the same prefix. `liveness_surface_refusal`
#: is a latch cleared by `_record_liveness_surface_publish`, but a latch that fails to clear is
#: exactly the shape that would make this function cite a refusal the surface has since recovered
#: from -- so the retirement is re-derived from the two stamps rather than trusted.
PUBLISH_FIELD_SUFFIX = "_last_publish"

#: Every cause this module will accept a write for. A write naming anything else is refused
#: rather than stored, because a reader that trusts the field must be able to trust the set.
CAUSES = frozenset({GATE_REFUSAL, NON_TEST_GATE_REFUSAL, DEADLINE_KILL, PUSH_NEVER_LANDED,
                    PROVENANCE_REFUSED, BEHIND_ORIGIN, LOST_PUSH_RACE,
                    SCOPED_SUITE_RED, SCOPED_GATE_UNJUDGED})

#: Causes on which NO test returned a verdict, so no blocking list or suspect may be attached.
#: See the module docstring. `GATE_REFUSAL`'s absence is the content of this set, not an
#: oversight — that is the one cause where a named red is real evidence about THIS cycle.
#: `SCOPED_SUITE_RED` is absent for exactly the same reason and `SCOPED_GATE_UNJUDGED` is present
#: for its mirror: the two exist BECAUSE that split was being made by an exit code that could not
#: carry it.
NO_TEST_JUDGED_CAUSES = frozenset({NON_TEST_GATE_REFUSAL, DEADLINE_KILL, PUSH_NEVER_LANDED,
                                   PROVENANCE_REFUSED, BEHIND_ORIGIN, LOST_PUSH_RACE,
                                   SCOPED_GATE_UNJUDGED})

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
    # The SAME screen as every other timestamp reader here (2026-09-04, the wedge-detector sweep).
    # `isinstance(ts, (int, float))` alone let three shapes past, and the fail direction differed
    # for each: `0`/`False` read as ancient and fell into the stale branch by luck, but `NaN` fails
    # `now - NaN > max_age`, so an unaged record would have been cited as attribution for EVERY
    # cycle forever -- the carried-forward-blocking-list defect this whole function exists to stop,
    # arriving through the age bound instead of the hash check. `recorded_instant_seconds` refuses
    # all three, and an unstamped record is UNATTRIBUTED, which is this module's stated direction.
    recorded = recorded_instant_seconds(ts)
    if recorded is None or now - recorded > max_age:
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


def held_refusal(state, *, now=None, max_age=DEFAULT_MAX_AGE_SECONDS):
    """The live attributed cause this state record is ALREADY HOLDING — or (None, why-not).

    `unattributed` WAS A FALSE NEGATIVE SITTING BESIDE THE ANSWER (2026-09-24)
    --------------------------------------------------------------------------
    Observed in `docs/observability/.publish_gate_state.json`, 48 consecutive failures open:

        citation_at_head        "not_established"
        citation_at_head_reason "no red is named on this failure, so there is no citation to
                                 re-ask. This is not evidence that HEAD is green."
        total_red               0
        liveness_surface_refusal {"cause": "push_never_landed", "git_hash": "18cc753b7...",
                                  "evidence": "the commit was created here and `git ls-remote`
                                  says origin did not advance to it (push rc=1, ...)"}

    The front door read the first field, found nothing to cite, and said so. An attributed,
    stamped, hash-keyed cause was two keys away in the SAME FILE. The same shape had already run
    for three hours on the `dead` reading of the same field, where the summary's own sentence —
    *"the red it cites is DEAD at HEAD, so the cause is unattributed"* — was false in the
    direction that matters: a cause WAS held.

    `unattributed` is this module's most valuable answer and that is exactly why it must not be
    reachable while an attribution is in hand. "We cannot tell" is a result; "we did not look"
    wearing its clothes is not. A module whose job is to say why a publish did not happen must
    not be the reason a human runs pytest by hand to find out.

    THE SCREENS, AND EVERY ONE OF THEM FAILS CLOSED
    ------------------------------------------------
    A record is only returned when all four hold, and each is an OBSERVATION rather than a trust:

      * its `cause` is in `CAUSES` — the same closed set `record_cause` will accept a write for.
      * its `ts` passes `recorded_instant_seconds` AND is inside `max_age`. Same bound and same
        screen as `read_cause`, for the same reason: an undated record would be cited as the
        attribution for every cycle forever.
      * it has not been RETIRED by a later publish on its own surface. `<prefix>_refusal` is
        cleared by `<prefix>_last_publish`, and a latch that fails to clear is the one way this
        function could name a surface that has since recovered — so the two stamps are compared
        here rather than the clearing being assumed to have happened.
      * where several survive, the NEWEST wins. Not "the first found": a dict ordering is not a
        clock, and citing the older of two live refusals is the carried-forward defect again.

    NOT hash-keyed to the caller's failure, and that is the ONE relaxation from `read_cause`.
    This is deliberate and it is the difference between the two functions. `read_cause` answers
    "what was THIS cycle's cause" and must refuse another commit's record. This one answers "is
    this publisher's own state holding a cause nobody surfaced", which is a question about the
    RECORD, not about one cycle — the refusal's own `git_hash` travels back to the caller so the
    reader sees which commit it is about and can judge for themselves. A summary that named the
    commit would have ended the outage; silence did not.

    Returns `(record, "")` on a hit, or `(None, sentence)`. The sentence is never a bare
    "unknown": it NAMES the fields that were held and says why each was not enough, so a reader
    who thinks the answer is in one of them can go and look. That is the second half of the
    contract — either name the live cause, or say which inputs you had and why they failed.
    """
    now = time.time() if now is None else float(now)
    if not isinstance(state, dict):
        return None, ("the publisher's state is not an object, so no refusal record could be "
                      "inspected -- this is NOT evidence that the failure had no cause")
    empty, rejected, live = [], [], []
    for field in sorted(state):
        if not field.endswith(REFUSAL_FIELD_SUFFIX):
            continue
        rec = state.get(field)
        if not isinstance(rec, dict):
            # Held and empty is still an input that was HELD -- the why-not names it, because
            # "the latch is clear" and "there is no latch" are different facts to a reader.
            empty.append(field)
            continue
        cause = rec.get("cause")
        if cause not in CAUSES:
            rejected.append("{} names no recognised cause".format(field))
            continue
        recorded = recorded_instant_seconds(rec.get("ts"))
        if recorded is None:
            rejected.append("{} carries no readable stamp, so it cannot be dated at all"
                            .format(field))
            continue
        if now - recorded > max_age:
            rejected.append("{} is {:.1f}h old, past this reader's {:.1f}h bound, so it "
                            "describes an earlier episode"
                            .format(field, (now - recorded) / 3600.0, max_age / 3600.0))
            continue
        published = state.get(field[:-len(REFUSAL_FIELD_SUFFIX)] + PUBLISH_FIELD_SUFFIX)
        cleared = (recorded_instant_seconds(published.get("ts"))
                   if isinstance(published, dict) else None)
        if cleared is not None and cleared >= recorded:
            rejected.append("{} was retired by a later {}, so that surface has since published"
                            .format(field, field[:-len(REFUSAL_FIELD_SUFFIX)]
                                    + PUBLISH_FIELD_SUFFIX))
            continue
        live.append((recorded, field, rec))
    if live:
        recorded, field, rec = max(live, key=lambda held: held[0])
        evidence = rec.get("evidence")
        return {
            "field": field,
            "cause": str(rec.get("cause")),
            "evidence": (str(evidence) if isinstance(evidence, str) and evidence.strip()
                         else "recorded with no evidence line"),
            "git_hash": str(rec.get("git_hash")),
            "label": str(rec.get("label")) if isinstance(rec.get("label"), str) else None,
            "ts": recorded,
            "age_seconds": round(max(0.0, now - recorded), 1),
        }, ""
    if not empty and not rejected:
        return None, ("the publisher's state carries no refusal record at all, so there is "
                      "nothing here to name -- which is NOT evidence the failure had no cause")
    held = ["{} is empty".format(f) for f in empty] + rejected
    return None, "the publisher held {}".format("; ".join(held))
