**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `commit-or-untrack-the-head-red-artefacts-so-a-clean-worktree-stops-reading-830`) · **Class:** controls_that_cannot_fail

# PRE-REGISTRATION — whether untracking the head-red observation turns a false 830 into a false zero

Written before the change and before the gate run. The premise re-measurement below was done first
and is not part of what is pre-registered; the four predictions are.

## The premise, re-measured this turn (not a prediction — this was already known)

The drawn item cites `b7fcbfed6`, already an ancestor of `origin/main`. The premise is **live, not
spent**, and the split is sharper than the item states:

| | this isolated worktree (at HEAD) | shared tree |
|---|---:|---:|
| `head_red_register.drawable()` | **830** | **43** |
| runs recorded in `head_red_observed.json` | **1** | 10 |
| latest run row | `2026-09-02T04:30:02`, `passed: null`, `OSError x760` | `2026-09-10T03:46:53`, `passed: 33697` |

The single committed row is the ENOSPC/tmpfs wreck — and by `record()`'s own docstring it is a hand
transcription that `record()` would now **refuse** (`UnobservedRunRefused`, no pass count). The
committed `HEAD_RED_REGISTER.md` disagrees with the committed JSON it is rendered from: the document
says 21 owed (committed `108ff5a68`, 2026-09-05), the JSON says 830 (committed `bc57c8e30`,
2026-09-02). **Two tracked files, one derivation, three days apart, mutually contradictory.** That
disagreement is itself the evidence that these are not artefacts: a derived file and its source
cannot drift when both are generated together.

## What I am about to do

Untrack both, and add the state that untracking otherwise destroys.

## The predictions

**P1 — untracking alone is FAIL-OPEN, and by a bigger margin than the 830 it fixes.**
`load_observed()` returns `{"runs": [], "tests": {}}` for a missing store; `owed()` returns `[]`;
`drawable()` returns `[]`; `staging_rooms._with_the_head_red_register` drops the register from the
queue entirely when `drawable()` is empty. So a clean checkout after a bare `git rm --cached` reads
**nothing is red at HEAD** — the exact failure `load_observed`'s own docstring says must never
happen (*"It can never read as 'nothing is red', which is the failure that would matter"*).
I predict the bare untrack produces `drawable() == []` **and** the register absent from
`work_queue()`, with nothing anywhere naming the absence. If either is false, my reading of the
splice is wrong and I will say so here.

**P2 — the fix is a third state, not a louder zero.** `UNOBSERVED` (no census has run here) must be
distinguishable from `OBSERVED` with zero owed (a census ran and found nothing). Both are zero and
they mean opposite things. I predict that before the change **no function in the module can tell
them apart** — `render()` alone has the branch (`if not runs`) and it is the only place, so the
DRAW and the DOORBELL are both blind to it. Checkable by reading the call sites.

**P3 — the doorbell clause will change bytes on the shared tree, and this is the leg that can fail
open.** A fail-closed control cannot move live bytes on a correct feed. This one is not fail-closed:
it is a *rendering*, so it MUST change the doorbell line on the shared tree, where the state is
OBSERVED with 43 owed. I predict the shared-tree doorbell primary goes from `HEAD_RED_REGISTER.md`
as a bare 7th name among ~139 to a clause naming both the owed count and the longest-standing
`runs_red`. **If the rendered line is byte-identical, the change did not reach the reader** and the
whole item is undischarged regardless of what the tests say.

**P4 — I do NOT predict the register leaves the queue on the shared tree.** 43 are still owed there;
the draw is correct and stays. This item is about what a clean worktree reads and what the doorbell
carries, not about suppressing real work. If my change reduces the shared tree's owed count, it is a
defect, not a success.

## What would refute the decision itself

If any control, gate or test requires `docs/observability/head_red_observed.json` or
`docs/staging/reference/HEAD_RED_REGISTER.md` to be **tracked** — as opposed to merely present — then
"machine state" is the wrong call and they must instead be committed nightly by the census. I have
not checked this yet. Recorded here so the answer cannot be fitted to the decision I have already
made.

## The reasoning that decides it, stated before the gates run

Three properties, each independently sufficient:

1. `record()` writes it on every census run — **machine-written**, and the module's own docstring
   splits OBSERVATION (machine) from ACCEPTANCE (`head_red_baseline.json`, human, `"NOTHING WRITES
   THIS FILE AUTOMATICALLY"`). Only the second is a property of the tree.
2. `del runs[:-MAX_RUNS_KEPT]` — **it deletes its own history to a rolling 30 rows.** A file that
   truncates itself is a cache, not a record.
3. It describes *one machine, at one HEAD, on one night*. A checkout inherits it as though it were
   established fact, which is how 830 got authority it never earned.

The acceptance list stays tracked: a person wrote it, and it IS a property of the tree.
