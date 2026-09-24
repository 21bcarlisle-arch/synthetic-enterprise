**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the re-ask had already run six minutes earlier, and running it where the item said to would have archived two conditions observed that day

Drawn as
`alarm-reask-has-never-been-applied-so-the-new-attention-term-runs-entirely-on-its-fallback`.
Answers
`docs/staging/records/SEAT_PREREG_WHAT_A_RE_ASK_RUN_FROM_AN_ISOLATED_WORKTREE_GRADES_DIFFERENTLY_2026-09-24.md`,
which was **confirmed on run A, REFUTED on run B, and confirmed on run C** — the refutation is the
finding and it is kept beside the prediction below rather than instead of it.

## The premise, re-measured: spent, and spent six minutes before this turn began

The item asked for one command on the premise that it *"has never been applied: zero of the ten
live alarm documents carry a `## Re-asked` section"*. True when written. Measured at draw:

| fact | value |
|---|---|
| `465a0dfca`, adding BOTH `reask()` and its only caller | 2026-09-23 23:12:02Z |
| the caller | `background/staging_watcher.py:888`, inside the tick loop |
| running `staging_watcher.py` (pid 2413962) started | 2026-09-24 02:00:23Z |
| all ten live documents rewritten, one archived `cleared` | 2026-09-24 02:00:25Z |
| this invocation started | 2026-09-24 ~02:06Z |

**The command was never missing. The restart was.** `reask()` and its caller landed into a daemon
that was already running, and a long-lived Python process holds the code it booted with; the
function was inert for **2h48m** and applied two seconds into the first tick of the next process.
The item was drawn inside that window. So the item's own diagnosis — *"two mechanisms are waiting
on the same unrun command"* — named a cause it had not tested, and the untested half was the one
that mattered: nothing in this repository relates a landed change inside a daemon's source to the
code version of the daemon actually running. That is the generalisable defect here and it is
**not** fixed by this commit; it is handed off below.

What the daemon's run did, for the record: ten documents gained
`- **2026-09-24** — re-asked: **still_holds**.` and
`..._VALUE_ARM_CHOOSES_A_BOUND_NOT_A_CUSTOMER_WAS_CLAIMED_2026-08-25.md` archived itself to
`done/` as `cleared`, quiet since 2026-08-25. So leg 1 of the ORDER 60 attention term
(`unattended_since`) is live on the shared tree, and this commit lands those eleven writes so it
is live at HEAD too — the daemon annotates the queue and never commits, which is the second half of
the same shape.

## What the three runs said

| run | configuration | predicted | measured |
|---|---|---|---|
| A | this worktree, no store on disk | 7 `still_holds`, 3 `cannot_tell`, 0 `cleared` | **exactly that** |
| B | the same worktree, shared store copied in, one variable | 9 `still_holds`, 1 `cleared` | **7 `still_holds`, 3 `cleared`** |
| C | did any live verdict turn on the store? | none | **none** — every applied line reads `observed <date>, within the 3-day bar` |

**Run B refuted the prediction and the mechanism behind it.** I predicted the store would rescue
`deadman_origin_fork` and `seat-claim` through the contradiction leg. It cannot: **four of the nine
live families have no key in that store at all** — `deadman_origin_fork`, `delivery-lane-stranded`,
`seat-claim`, `seat-continuity` — because they call `escalate()` directly and have never written
it. The module already knew this and says so in
`test_MUTATION_an_ABSENT_key_ALONE_never_clears_a_RECENTLY_OBSERVED_document`; **I predicted
without reading the controls on the leg I was predicting about**, which is the whole reason the
prediction was wrong and is worth more than the prediction being right would have been.

So run B graded `cleared` on two documents that carried a still-live line stamped **that same day**
in the shared tree's copies and were firing hourly. Had this turn obeyed the drawn item literally —
`--apply`, in the seat's isolated worktree, which is where the seat runs — it would have archived
two live conditions out of the director's queue **and written into `done/` the evidence that it was
right to**. Run A was safe only by the magnitude of the drift: `machinery_heartbeat` fell back to
the documents, read 2026-09-22, and missed a one-day bar by two days. A checkout one day fresher
clears that bar with both rescue legs still absent.

## Why no existing leg could catch it, and what now does

Every other leg of `reask()` interrogates a document — how old its lines are, whether the store
contradicts them, whether the machinery wrote anything. All of them read their inputs *through* the
position of the process doing the reading, and all of them are confident about it. The stale copy
and the missing store are properties of **where the process is standing**, and a leg that reads
documents cannot ask about that. `_read_transitions_for_reask`'s own docstring argued an empty read
was safe because *"the heartbeat leg below still has to pass"* — and the heartbeat's other source
is the graded documents themselves, so one fresh document keeps it alive with no store at all.

`clearing_vantage_refusal()` now asks the prior question once, before any document is graded, and
only of the live queue:

1. **a linked git worktree** (`.git` is a file, not a directory) — HEAD's copies are not the live
   queue, and HEAD is behind the daemon's writes by construction rather than by accident.
2. **no transition store on disk** — distinct from an empty one, which is a real reading of a quiet
   system. An absent *file* means this process is not where `notify()` writes.

It withholds only the irreversible half: the reading is still taken and still annotated, and the
`cannot_tell` line names which leg refused. Keyed to the property (*can this process see the live
queue?*), not to today's dates or today's drift. It does not apply when a caller **names** a
`staging_dir`, because such a caller built that room and answers for it — and if it did apply, the
guard would fire in the gate's checkout and not in the main tree, giving opposite verdicts in two
places both meant to be authoritative.

Verified on the exact configuration that failed: the same run that graded 3 `cleared` now grades
0 `cleared` and 3 `cannot_tell`, each naming the worktree.

**Four mutations, each caught by the leg written for it** (`63 passed` restored after each):

| mutation | caught by |
|---|---|
| the guard is never consulted | both vantage controls |
| the worktree leg cannot fire | the worktree control + the scope control's fixture assertion |
| the store leg refuses even with the store present (a guard that refuses everything) | both one-variable legs |
| the guard applied to a named population too | the scope control + `..._NEVER_OVERWRITES_AN_EARLIER_EPISODE_in_done` |

Both controls carry a **one-variable leg** that repairs the vantage and nothing else and asserts
the clear becomes reachable, because without it each would pass for a guard that refuses
everything — the trap CLAUDE.md records being entered three times in one afternoon.

## What is NOT fixed, named rather than left to be inferred

1. **A landed change inside a running daemon is inert until restart, and nothing measures the
   gap.** 2h48m here; the only reason it ended is that something restarted the watcher at
   02:00:23Z. This is the whole cause of the drawn item and it remains open.
2. **The store cannot be the backstop its reader claims** for the four families that bypass
   `notify()`. The remedy is to give those families a firing record — `escalate()` writing a
   transition key — not to refuse to clear them, which would make four of nine queue items
   permanently unretireable, the cost `REASK_QUIET_DAYS` was chosen against. Related:
   `SEAT_FINDING_THREE_ALARM_FAMILIES_BYPASS_NOTIFY_AND_HARDCODE_REPEATS_1_...`.
3. **Two documents collapse onto one family.** `..._VALUE_ARM_...` and `..._SEAT_CLAIM_...` both
   resolve to family `seat-claim`, so ten live documents are nine families and any per-family
   reading of this population counts one of them twice. The daemon cleared one and held the other
   on their own lines, so nothing has yet gone wrong by it.
