**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `does-minting-arrivals-widen-the-scored-decision-population`

# The stale-copy guard refuses a merge for adopting the other side's deletions, and the remedy it prints is the merge it just refused

*`tools.surgical_land --merge origin/main` refuses this tree with `[stale-copy] 2 path(s) would
revert work that has already landed`. They would not. For both named paths the merged tree is
**byte-identical to `origin/main`** — same blob sha — and this side is byte-identical to the
**merge-base**, with zero commits touching either file since `e436774b1`. The guard is reading the
merge legitimately ADOPTING the other side's deletions as this lane reverting them. Its printed
remedy, `tools.refresh_to_head`, cannot be run: it refreshes a working copy to **HEAD**, and HEAD is
precisely what is behind. Only the merge can un-stale those files, and the guard refuses the merge.*

---

## 1. What was refused, and the exact claim

```
[stale-copy] ❌ COMMIT REFUSED -- 2 path(s) would revert work that has already landed.
  tools/generate_dashboard_data.py  [strict_symbol_subset]
      would DELETE 1 name(s) HEAD has, and adds none:  - count_run_history_total
  tools/mirror_github_pages.py      [strict_symbol_subset]
      would DELETE 2 name(s) HEAD has, and adds none:  - DOCS_SHADOW  - SITE_SHADOW
```

## 2. The claim is false, and the merged tree is the arbiter

Merge-base `e436774b1`. Measured, not argued:

| question | `tools/generate_dashboard_data.py` | `tools/mirror_github_pages.py` |
|---|---|---|
| merge-base vs THIS side | **SAME** | **SAME** |
| this side's HEAD vs working tree | SAME | SAME |
| merge-base vs `origin/main` | DIFFERS | DIFFERS |
| commits on this side touching it since the merge-base | **none** | **none** |
| merged tree's blob vs `origin/main`'s blob | **IDENTICAL** | **IDENTICAL** |

Both files were changed on **one** side only. A three-way merge adopts `origin/main` outright —
there is nothing of this lane's to lose and nothing of origin's to revert, and the merged tree
carries origin's bytes exactly.

The names the guard says would be deleted were deleted **by origin**: `count_run_history_total` at
`d066d3534`, `DOCS_SHADOW` / `SITE_SHADOW` at `80e363721`. They are present on this side only
because this side has not merged yet. The guard compared the merge RESULT against **this side's
HEAD**, found them present there and absent in the result, and attributed the absence to this lane.

**Checked before any exemption was asked for, because this one is security-relevant:** the merged
tree carries **zero** paths under `docs/shadow/` and **zero** occurrences of `DOCS_SHADOW` or
`SITE_SHADOW`. `80e363721` deleted `docs/shadow/` after a £1.5m internal P&L sat on the public Pages
root for a month. That deletion survives the merge intact. The guard's refusal does not protect it;
the merge already does.

## 3. Why this is a wedge and not an inconvenience

On a **pathspec** commit the check is right, and it is one of the load-bearing controls in this
tree: a pathspec stages the working-tree copy, so an old copy really does delete a rival lane's
landed work. On a **merge** the same shape has the opposite meaning — adopting the other side's
deletion is the correct outcome and the only outcome — so the check inverts there.

**The remedy it prints is unreachable by construction.** `tools.refresh_to_head <path>` writes
**HEAD's** bytes over a stale working copy. Here the working copy already equals HEAD; both are
behind `origin/main`. Running it is a no-op. The only operation that can make those files current is
the merge, and the merge is what was refused. That is a closed loop, and it is the same family as
the publish-gate wedge whose red was "being behind".

`--drops <path>` does **not** clear it. It is a `surgical_land` flag; this check runs inside the
pre-commit hook chain, so the exemption never reaches it. Tried and recorded here so the next lane
does not spend a gate cycle discovering it.

## 4. What I did NOT establish, and will not guess

`python3 -m background.origin_reconcile` — the sanctioned automatic door, which closes the fork **in
an isolated worktree, never in the shared tree** — refuses the same fork with `REFUSED_GATE: on the
resulting tree (rc=1)`. It reports `behind: 6`.

**I cannot attribute that refusal to this guard.** The only gate output it surfaced was a *different*
check's verdict (`{"status": "HONEST", "honest": true, "stale_claims": []}`) with no stale-copy tail,
and an isolated worktree checked out at the merged tree would have origin's bytes for both files,
which is the condition under which this guard should pass. So either it is a second, independent
red, or it is this one reached by another route. **An absent answer must read as absent.** What is
established: the fork is 6 behind, both doors refuse, and the shared tree cannot currently close it.

*What would settle it:* run `origin_reconcile` with the full hook-chain tail captured rather than
the summary verdict, and read which check returned rc=1.

## 5. What this cost and what is still true

The delivery increment this was found under is landed and bound: `00d532464`, the repeating
`KeyError: 'SYN-2016-008'` alarm archived with its cause. That commit landed through the ordinary
pathspec door without complaint — **the wedge is on the merge only**, not on this lane's work. It is
local-only until the fork closes, which is not this claim's to fix.

Two gate cycles (~13 min each) were spent establishing the refusal is false rather than working
around it. Recorded so the next lane to meet it can skip both.
