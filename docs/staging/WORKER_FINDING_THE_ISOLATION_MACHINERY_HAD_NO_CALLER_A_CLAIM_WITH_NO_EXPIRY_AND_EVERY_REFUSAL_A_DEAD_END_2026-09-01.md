# [WORKER FINDING] The isolation machinery had no caller, a claim with no expiry, and every refusal a dead end

**Severity:** RECORDED (all three fixed and dogfooded in the same turn) · **Lane:** H_harness
**Epoch:** 3 · **Atom:** `H24_worktree_dir_autoreap`
**Found:** 2026-09-01, on the director's console instruction: *"Six undeclared worktrees are
accreting and being reported rather than cleared — that's the isolation machinery working with
nothing tidying up behind it. Give them a lifetime."*

## Class registration

Belongs to `no_caller_and_never_runs`. Three unwired mechanisms turned up inside one module in one
hour, and every one of them had been *written*, *reviewed*, *tested* and *documented as the remedy
for something*.

**It does not, however, move that class's count, and I was wrong to write that it did.** This
document is RECORDED — fixed in the same turn — and `derive_memberships` excludes RECORDED documents
from every class population on purpose: *"a RECORDED document is a landed record with nothing owed…
folding reports of FIXES into a class of DEFECTS would inflate every instance list with work already
done."* That is correct for CONSOLIDATION, which is what the exclusion was written for. Whether it is
correct for the DEBT reading that now ranks classes in the draw is a different question, and it is
filed separately as `WORKER_FINDING_A_CLASS_THAT_IS_ALWAYS_FIXED_ON_SIGHT_CARRIES_NO_DEBT_2026-09-01`
rather than assumed either way here.

Also touches `controls_keyed_to_a_structure_that_moved` (the `live writer` refusal below).

## The three, each sufficient on its own

**1. The reaper had no caller, from the day it was built.** `fork_reconciler.evaluate_worktree_reap`
(2026-07-18): two modes, its own arming flag, refusals for locked / live / dirty / main / bare, no
`--force`, serialized through the shared tree lock, mutation-proven both ways. Nothing in this
repository has ever called it. The only worktree code on the deadman cycle is
`_check_worktree_reconcile`, the REPORTER. So the director's sentence is the literal architecture:
being reported was all the machinery could do.

Its own atom record predicted this in terms, on 2026-08-03, as requirement (4) of four:
> *"arm the flag and wire it to the reconcile-watch/deadman cadence, else the mechanism stays a
> library nobody calls — MAKE_IT_STICK: an unwired reaper is prose."*

**And the flag had since been armed.** `.worktree_reap_enabled` exists. That is worse than neither,
because `enforce=True` on a function no scheduler calls reads to any reader — including me, an hour
ago — as a reaper that is running and finding nothing to do.

**2. An ownership claim never expired.** `seat_executor.worktree_is_live` asked one question: is the
named pid alive? Five of the six markers named **pid 215 — the tmux server**, started 2026-08-24 and
alive for as long as the console is. So five worktrees read as *held by a live writer* a full day
after their writers had gone; the reaper refused them and `fork_salvage` skipped them, both
correctly given what they were told.

Not one careless write. **A bare pid is a weak identity, and the pid a hand-working session can most
easily name is the longest-lived process on the box.** The class fix is a lease: whatever pid is
named, the claim dies of old age.

**3. Every refusal was a dead end.** A dirty worktree is never reaped — and nothing was cleaning it.
A detached ORPHAN is *"refused until it is tagged"* — and nothing was tagging it.
`salvage_detached_head` was written as the door out of that exact refusal, says so in its docstring,
and had **never been called**. The module's own docstring warns about this shape —
*"a refusal with no door beside it is a stall wearing a control's clothes"* — and then leaves the
door unwalked.

## And one control that had gone quiet

`live writer` was missing from `_LIVE_REFUSALS`. The refusal was written at both reap doors on
2026-08-31 and never registered in the vocabulary that decides what a refusal MEANS, so the one
refusal that most emphatically says *the control is working* ("it is in use, not abandoned") scored
as the control being STUCK — five in-use worktrees counting toward `STRANDED_WORKTREE_ALARM_AT`.

Harmless while nothing acted on the stranded set. **The moment `advance_stranded` did, it would have
committed into a live writer's tree** — which is precisely the 2026-08-31 incident the live-writer
refusal was written to prevent, arriving through the other door. Caught while writing the guard, not
by running it.

## And the fail-silent repair that landed on one branch of two

The 2026-08-03 repair made `WORKTREE_REAP_CLEAN` unreachable while a stranded population exists —
**in report-first mode only**. In enforce mode "removed nothing" still printed CLEAN. The first live
enforce pass tonight printed `WORKTREE_REAP_CLEAN` over six stranded worktrees with `alarm: True`
beside it. A status and an alarm that disagree is worse than either being wrong.

The fix took the branch it was looking at as its subject rather than the property. "Reaped nothing
while unable to act" means the same thing in both modes.

## What was delivered, and the proof

`deadmans_switch._check_worktree_reap` (the caller) · `seat_executor.OWNER_LEASE_SECONDS` (the
lease, derived from `SESSION_TIMEOUT_SECONDS` + grace, not picked) · `fork_reconciler.advance_stranded`
(the preserving step) · `live writer` in `_LIVE_REFUSALS` · the stranded status on both branches.

Dogfooded end to end on the live tree, three passes of the machinery's own lifecycle:

| pass | what the mechanism did |
|---|---|
| 1 | 6 stranded → 5 dirty trees salvaged to their own HEADs, 1 detached orphan tagged |
| 2 | 5 newly-detached HEADs tagged; `se-seat-executor` reaped |
| 3 | the remaining 5 reaped |

`git worktree list` is now the main worktree alone, `alarm: False`, and every scrap is preserved
under six `salvage/detached-*` tags. 24 tests; the four load-bearing mutations were applied,
confirmed failing, and reverted.

## What this finding does not claim

Not that any single guard was wrong — every refusal in that module is individually correct and most
are mutation-proven. Not that the arming flag was set carelessly. The claim is narrower and is about
the SHAPE: **this project keeps building correct mechanisms and not connecting them**, and a
mechanism with no caller has no red state, so nothing can observe that it is not running. That is
why it goes to `no_caller_and_never_runs` with three instances rather than being fixed quietly.
