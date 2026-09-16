**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SIM] PUBLISH REFUSED, ORIGIN AHEAD -- origin/main is 2 commit(s) AHEAD of HEAD, so a commit created here could only be rejected non-fast-forward and would widen the fork by one mo

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **3.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[SIM] PUBLISH REFUSED, ORIGIN AHEAD -- origin/main is 2 commit(s) AHEAD of HEAD, so a commit created here could only be rejected non-fast-forward and would widen the fork by one more. Reconcile first: `python3 -m tools.surgical_land --merge origin/main` -- no commit was created, so the fork is not one wider than it was. Nothing is wrong with the run or the suite; the tree needs reconciling.
```

## What is known without diagnosing anything

- Signature: `auto:76dbcc7f5f569c55` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-03T09:25:17+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
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

## Resolved 2026-09-04 -- the condition was real and the tree is now level

The alarm was right and it was not a false positive. The shared tree was found 0 ahead / 4 behind
origin/main: a rival lane had pushed the published-route-split work from an isolated worktree, and
nothing fast-forwards the shared checkout, so every daemon running from it was executing code the
branch had moved past. Pushed is not imported.

Reconciled by a pure fast-forward under the tree lock, f65597f72 to 7c9f9131e, six files and no
merge commit. Divergence is now 0/0. Two things were checked because both have bitten before: the
fast-forward was refused at first by an UNTRACKED twin of a staging file the incoming commits add,
which was removed only after proving it byte-identical to origin's blob, so nothing unlanded was
destroyed; and the six incoming paths were diffed against HEAD afterwards to confirm no silent
revert was left armed in the working tree.

Why the alarm could fire for three hours unconverged: nothing in the architecture fast-forwards
the shared tree. The alarm names the remedy but no daemon performs it, so the condition can only
clear when a seat happens to look. That is the standing gap this episode exposes, and it is left
stated here rather than fixed by minting a daemon to watch a daemon.

## Still live

Nothing. The condition named above is cleared; a recurrence files a fresh document as a new
episode, per the paragraph above.

## Instances seen
- `publish refused, origin ahead -- origin/main is # commit(s) ahead of head, so a commit created here could only be reject` (first seen 2026-09-03)
