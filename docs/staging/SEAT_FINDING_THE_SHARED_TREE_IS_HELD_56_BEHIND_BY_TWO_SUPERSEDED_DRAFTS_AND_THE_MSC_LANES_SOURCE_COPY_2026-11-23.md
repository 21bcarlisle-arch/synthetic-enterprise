**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared tree is held 56 commits behind origin by three working copies: two superseded drafts and the MSC lane's source copy

Found by the delivery seat, 23 Nov 2026 ~20:50Z, on claim `the-shared-checkout-actually-reaches-origin`.

**The premise holds.** The reconciler fix `b0b05661f` is on origin. The shared checkout
`/home/rich/synthetic-enterprise` is still at `779054e30b`, which is **56 behind and 0 ahead** of
`origin/main` `f23c8cab0a`. Its working copy has 2,768 dirty entries. Every reconcile-watch pass
since then ends the same way. The last one read was 20:43Z in
`docs/observability/reconcile-watch-log.md`:

> NOT_ADVANCED [STILL OPEN]: [origin's reconciler @f23c8cab0] ... 3 of 35 blocking path(s) could
> NOT be proven lossless or carried, so clearing the 32 that could would touch files and still not
> advance. Nothing was written.

The reconciler is already running origin's code (`@f23c8cab0`), so a stale reconciler is not the
cause. The 32 paths it can carry include `background/bounded_landing.py` and
`background/origin_reconcile.py`, which are byte-identical to origin. Those are the twins of
the reconciler's own fix. The advance is all-or-nothing, so three paths hold all of it.

## The three paths, one by one

| Path | What the bytes are | Whose | Disposition |
|---|---|---|---|
| `simulation/run_phase2b.py` (mtime 06:18Z, +90/−9 vs HEAD) | The **MSC wiring** (`market_stabilisation_charge_events`, `book_market_stabilisation_charge`), which is NOT on origin, sitting on a base older than `a525847e98` (it still holds the "won from a gas-only household ... not built" refusal that origin replaced). | **A live lane.** The MSC landing, claim `phase4c-reads-the-shared-run-so-the-msc-gate-fits`, session pid 1858008, worktree `/var/tmp/se-p4c-wt`, which was running a probe (pid 1859894) at the time of reading. That worktree holds a REBASED copy of this file (7 MSC references, on origin's base). | **Not moved.** This is live work. Once the MSC lane lands, this shared copy is that lane's pre-rebase source and is superseded in substance. It will still not merge cleanly onto origin, because its base predates the gas-only fix. |
| `saas/reporting/annual_report.py` (mtime 05:32Z, +5/−3) | The **Reg 6C lane's pre-landing draft**, written 3 minutes before `cc9f08ae3d` (05:35Z). Its only line that is on neither origin nor HEAD is `"switching_gsop_payments": _NO_READER`. That draft dropped the reg 6ZA forward, and the landed 6C commit deliberately **kept** it. | **Orphaned: no lane.** 6C is landed (`cc9f08ae3d`, `09ae79aa0c`), and no live claim names it. The MSC worktree carries its own correct copy (both 6C keys and the gsop forward). | **Recorded here.** The reconciler ages it out at the 48h line, **~25 Nov 05:32Z**, preserved on a ref. |
| `tests/simulation/test_run_phase2b.py` (mtime 22 Nov 09:23Z, +73/−8) | **Byte-identical to the blob in the SALVAGE commits `a00ac96e63` and `5fd13f5f66`**: the 6C test draft on a base older than `83570bd1c0`. Every line in it is either on origin or in `83570bd1c0^`. Its "32 lines not on origin" are the truncated 2016-2017 fixture that `83570bd1c0` removed, and **HEAD already contains `83570bd1c0`**. So this copy predates a landing and would revert it. | **Orphaned: no lane.** Its content is landed (`cc9f08ae3d` + `83570bd1c0`) and preserved on the salvage commits. | **Recorded here.** It ages out at **~24 Nov 09:23Z**. |

**When the advance can happen without anyone touching bytes:** about 25 Nov 06:18Z, the latest of
the three 48h lines (run_phase2b's). That holds only if the MSC lane lands from its worktree
and nobody rewrites the shared copies before then. If the MSC lane lands sooner, run_phase2b
stays the last holder until its own age line passes.

## The defect this exposes in the reconciler (not fixed this turn: fixing it alone would not advance the tree)

`origin_reconcile._superseded_verdict` takes HEAD as the copy's base for its three-way leg,
`_merge_onto_origin`. A copy written on an **older** base (the "predates landing" shape) conflicts
with that leg. The line count then reports lines that a commit HEAD already contains removed as
"not on origin, so it is live work". `test_run_phase2b.py` shows the shape exactly: every line
in it is in `83570bd1c0^ ∪ origin`.

A sound extra leg would ask whether the copy's change, taken from a blob of this path that is
**on origin's first-parent history**, changes nothing when applied onto origin. That would prove
supersession for this shape. On today's set it would clear only `test_run_phase2b.py`. The
other two would still hold, so the advance would not happen sooner. It is recorded, not built, on
the rule that a change to the bytes-discarding path needs its own mutation-proven test. The class
is uncommitted-and-orphaned work (pre-landing drafts left in the shared tree after their
subject landed).

## The duplicate check

`phase4c-reads-the-shared-run-so-the-msc-gate-fits` is **different work**: it lands the MSC change.
This item asks why the shared tree will not advance. They meet at `run_phase2b.py`, and this item's
answer there is "wait for that lane". The claim was not released as a duplicate.

## Done means

HEAD equals `origin/main` at one reading, and the next reconcile-watch line reads ADVANCED. That
is not reachable this turn without moving another lane's bytes (a wall) or bytes the reconciler's
age line protects. So this finding is the deliverable, and the check is handed on with a
DO-NOT-DRAW-BEFORE date.
