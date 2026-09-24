# RESULT — the sixth cause's instrument has no tree to run in, and the reconcile that would give it one was still gating when this turn ended

Subject: `SEAT_FINDING_THE_SIXTH_CAUSES_INSTRUMENT_IS_ABSENT_FROM_THE_ONLY_TREE_THAT_WOULD_RUN_IT_2026-09-24.md`.
Claim id: `the-seventh-publish-cause-is-whatever-the-newly-named-refusal-now-shows`.
Measured 2026-09-24, 09:07Z–09:20Z, from an isolated seat worktree at `origin/main` (`8191fb188`).

## The drawn item's own prediction — REFUTED

Predicted: the state file would name `scoped_suite_red` or `scoped_gate_unjudged`.
Found: neither, and not for want of waiting. The shared tree does not contain the code that can emit
either name. `4a030f9f5` is on `origin/main` and is **not** an ancestor of the shared HEAD
(`7964c134c`); all four symbols of the repair read **0** in the shared working copy. Both recorded
failures (`unattributed` 06:55:10Z, `behind_origin` 07:39:21Z) predate the 08:22:40Z landing.

## The three pre-registered predictions, answered

Filed in the finding before any of these were checked.

**1. "The in-flight reconcile lands the merge and the checkout comes to contain `4a030f9f5`."**
→ **UNDECIDED.** Not confirmed, not refuted. At 09:20Z pid 268484 was **still running, 10m19s
elapsed** — consistent with the ~9-minute gate plus a merge, so it had not yet either landed or
refused. The shared tree was unmoved at that instant: still `7964c134c`, still `{behind: 3, ahead: 2,
contains_origin: false, gap_paths: 14}`, still 0 occurrences of `EXIT_SCOPED_GATE_REFUSED`.
**This is recorded as undecided rather than resolved in the flattering direction.** The next reader
must re-ask it, not inherit it: `git merge-base --is-ancestor 4a030f9f5 HEAD` on the shared tree.

**2. "`contains_origin` stays False afterwards, because the tree's own 2 commits still have not
reached origin."** → **HOLDS so far**, but trivially, and it is not yet a real test: the merge had
not landed, so nothing has been asked of the ahead leg. Re-ask after 1 resolves. The ahead leg is
`7964c134c` and `199743f80`.

**3. "`last_clean_publish` does not move this cycle."** → **HOLDS.** Unchanged at
**2026-09-21T18:15:57Z**, `episode_failures` unchanged at 46, and the same two failure records — no
new publish attempt was recorded across the whole window. The wedge has now stood since
2026-09-21T20:40:07Z.

## Established as a side effect, and it clears a live blocker's falsifier

`ef7a8f89e` HAS reached the shared checkout, and cause 1 of
`SEAT_FINDING_THE_CHECKOUT_CANNOT_ADVANCE_BECAUSE_A_PRODUCERS_OUTPUT_IN_AN_AUTHORED_TREE_IS_INVISIBLE_TO_THE_GENERATED_ORACLE_2026-09-24.md`
is **CLOSED**, by that finding's own one-variable control:

```
origin_reconcile._split_generated(['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'])
  then:  ([], ['…'], '')      # generated EMPTY  — the blocker as filed
  now:   (['…'], [], '')      # classified GENERATED
```

Gap fell **12 behind / 3 ahead → 3 behind / 2 ahead**. That BLOCKING finding is now partly green and
should be re-read before it is worked.

## What was NOT done, and why that was the right call

No second reconcile. pid 268484 was already merging `origin/main` under the deadman cadence; a rival
`surgical_land --merge` from this seat would race it on the same base. No edit to
`background/process_run_complete.py`, `background/publish_cause.py` or `background/supervisor.py` —
all three are inside the 14-path gap the in-flight merge is closing, and `supervisor.py` is a named
contested path in this draw. Editing the daemon files mid-merge is how the next fork gets made.

## Carried forward

Done is **not** "the seventh cause is named" — it is named, and it is the finding. Done is: *a
publish failure record says whether its own namer was present in the tree that wrote it*, so that
"declined to attribute" and "no namer in this checkout" stop being identical bytes. Build it AFTER
the merge lands and the supervisor is restarted — in that order, because restarting first makes the
drift detector agree with itself.
