**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `does-minting-arrivals-widen-the-scored-decision-population`

> **CLOSED 2026-09-22 by the operation this document said was impossible.** The claim was that the
> merge could not be made: the guard refused it and the remedy it printed (`refresh_to_head`) was a
> no-op against a HEAD that was itself behind. §6 (2026-09-21) located the real refusing leg — the
> hook chain's own re-stage — and repaired it by re-asking only the DELTA rather than the whole
> tree.
>
> Closed on live evidence rather than on the repair being present. `tools.surgical_land --merge
> origin/main` was run on the shared tree today and LANDED as `669546e87`, printing
> `[stale-copy] 4 path(s) adopted from origin/main (95035ad29) unchanged on this side since the
> merge-base, so not this lane's loss`. That is the exact reading §2 argued for and the guard
> would not give. The control is
> `tests/tools/test_stale_copy_refusal.py::test_a_restage_by_the_hook_chain_itself_re_asks_only_the_paths_it_moved`,
> which runs both legs of the partition on one tree state, so a guard that refused everything or
> passed everything fails one of them.
>
> The merge was the precondition for the staging archival this finding was BLOCKING
> (`22c07b232`, `b45f13ca1`).
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

---

## 6. CORRECTION (2026-09-21, delivery seat) — §1's diagnosis is wrong, and §4's open question is settled

*Kept beside the claim rather than revised over it: this section is the only evidence the
measurement was designed before its answer was known.*

**`strict_symbol_subset` was never the defect, and neither was `adopted_from_merge`.** Both are
correct. Re-measured on the live fork today (HEAD 9 ahead / 7 behind, merge-base `e436774b1`):

```
adopted_from_merge(HEAD, origin/main, <47 merge paths>)  -> 46 paths exempt
violations(HEAD, <merged tree>, ..., merge_ref=None)     -> [generate_dashboard_data.py, mirror_github_pages.py]
violations(HEAD, <merged tree>, ..., merge_ref=origin/main) -> []
```

So `surgical_land --merge`'s OWN call passes, and prints that it did:
`[stale-copy] 46 path(s) adopted from origin/main (0bdee00b7) unchanged on this side since the
merge-base`. §2's table is right about the merged tree; §1's attribution of the refusal to `--merge`'s
own guard call is not.

**§4's question — *which check returned rc=1* — answered by keeping the full gate tail.** The
`REFUSED_GATE` detail is `_classify_merge_failure`'s 400 characters after `GATE RED`, which is why
it showed the honesty verdict and no stale-copy tail. Run with both streams kept, the refusing leg
is the hook's own `python3 -m tools.stale_copy_refusal --staged`, and the route to it is:

1. `_land_once` judges the merged tree WITH the merge ref, passes, and pins the already-gated token
   to `91a49e0e3`.
2. The **FIRST block of `tools/git-hooks/pre-commit`** re-stamps `docs/status/LATEST.md` and
   `git add`s it. `docs/status/LATEST.md` is one of the 47 paths this merge carries, so the index
   the hook writes out is `eb8cb2718`, not the tree the token names.
3. The sha comparison in `staged()` therefore fails and the WHOLE tree is re-asked — with no merge
   ref and no `--drops`. That re-ask is what printed §1's refusal, which is why its wording is
   `COMMIT REFUSED` and not `MERGE REFUSED`: `refusal_text` was called with `merge_ref=None`.

Attributed on ONE tree state, both directions run: on the same extract, the whole-tree re-ask
returns those two paths and the delta re-ask returns none.

**So the class is right and the instance was misplaced.** §3 stands unaltered — on a pathspec commit
the check is correct, on a merge the same shape inverts — and so does the closed-loop reading of
`refresh_to_head`. What was missing is that the inversion was not reachable through `--merge`'s
call at all; it was reachable through the hook leg behind it, and only on a landing that carries a
path the hook itself re-stages. `--drops` not clearing it (§3, last paragraph) has the same cause:
the hook leg cannot see the landing's exemptions either.

**Repaired** by re-asking the DELTA — the paths that differ between the tree the token names and
the tree the index now writes out — rather than the whole tree. See `staged()` and
`tests/tools/test_stale_copy_refusal.py::test_a_restage_by_the_hook_chain_itself_re_asks_only_the_paths_it_moved`,
which runs both legs of the partition on one tree state so a guard that refused everything or
passed everything fails one of them.
