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

## CORRECTION, filed beside the claim — prediction 1 resolved, prediction 2 REFUTED

Written ~09:50Z, after `90d42eb21` gated and `promote_worktree_landing` refused with *"origin/main has
moved to b07b0af96"*. That refusal is what resolved prediction 1, which the section above had to
leave undecided.

**Prediction 1 — CONFIRMED.** The reconcile landed: `b07b0af96 merge origin/main: automatic
reconciliation in an isolated worktree`, and it carried the shared tree's own two commits
(`199743f80`, `7964c134c`) to origin with it.

**Prediction 2 — REFUTED, and in the dangerous way: right conclusion, wrong mechanism.** I predicted
`contains_origin` would stay False *because the tree's own 2 commits still had not reached origin — a
merge closes the behind leg, not the ahead leg.* Measured after the landing:

```
{'behind': 6, 'ahead': 0, 'contains_origin': False, 'gap_paths': 12}
```

`contains_origin` is indeed still False, so a check keyed to that flag would have gone green on my
reasoning. But **every clause of the reason is wrong.** The ahead leg CLOSED (2 → 0) — the reconciler
does close it, which I denied. The behind leg GREW (3 → **6**). And the shared checkout did not move
at all: still `7964c134c`. Had I pinned a control to "ahead stays non-zero" it would now be red for
the tree becoming *more* correct.

**Prediction 3 — CONFIRMED.** `last_clean_publish` unchanged at **2026-09-21T18:15:57Z**,
`episode_failures` unchanged at 46, the same two pre-landing failure records, and supervisor pid
3620344 still the 06:10Z process (3h16m). No publish attempt was recorded across the whole window.
The instrument is still absent from the shared working copy: `EXIT_SCOPED_GATE_REFUSED` 0,
`SCOPED_SUITE_RED` 0, its test file still not on disk.

## The seventh cause, in its corrected and final form

The refutation of prediction 2 IS the cause, and it is sharper than the finding as filed:

> **Closing the fork with origin and advancing the checkout are two different operations, and only
> the first has an owner.**

`origin_reconcile` makes *origin contain the shared tree* — and by explicit design does so in a
throwaway worktree, "never in the shared tree", so that a daemon merging unattended cannot move
another lane's uncommitted work. That design is right. But nothing makes *the shared tree contain
origin*. So every landing anywhere pushes the checkout further behind: 3 → 6 while this very finding
was in the gate. The instrument's arrival is blocked on a step with no daemon.

**And that step is now mechanically trivial, which it was not before.** `ahead` is 0, so:

```
git merge-base --is-ancestor HEAD origin/main   ->  YES
```

It is a pure **fast-forward**. No conflict, no judgement, nothing to resolve — where the publish gate
state's own evidence line had called closing this fork "a judgement for the seat".

**What actually blocks it is two files.** Of the 12 gap paths, exactly two are dirty in the shared
tree with in-place edits:

```
background/supervisor.py
site/test_the_book_is_bounded_by_compute_reaches_the_reader.py
```

Those are precisely the two paths this draw named as CONTESTED. A fast-forward would refuse rather
than overwrite them, which is correct behaviour and also the whole blockage: **the checkout cannot
advance because two of the twelve files it needs are held open by another lane's unlanded work.** Ten
of twelve are free.

This is why I did not advance it from here. The isolation of this worktree is the reason this seat is
allowed to run unattended; reaching into the shared tree to move a checkout over another lane's
in-place edits is the exact harm that isolation exists to prevent. The legal door for those two paths
is `isolate_hunks --survey` then `surgical_land --content`, landing the other lane's hunks without
reading the file — then the fast-forward is unblocked and needs no judgement at all.

## Carried forward

Done is **not** "the seventh cause is named" — it is named, and it is the finding. Done is: *a
publish failure record says whether its own namer was present in the tree that wrote it*, so that
"declined to attribute" and "no namer in this checkout" stop being identical bytes. Build it AFTER
the merge lands and the supervisor is restarted — in that order, because restarting first makes the
drift detector agree with itself.
