# The hooks checkout is waiting for a fast-forward that a diverged tree can never pass

*Filed 2026-09-25 by the delivery seat, from the same drawn item as
`SEAT_FINDING_THE_LIVE_HOOK_REPORT_READS_CLEAN_ON_A_HAND_PATCH...`.*

**Class:** `publish_gate_and_wedge` — the shared tree cannot advance and the reconciler that exists
to advance it is refused by its own door on every run.

**Lane:** `H_harness`

**Severity:** BLOCKING. A gate the trunk declares is not running for any `git commit` made in the
shared tree, and the stated remedy cannot execute, so the gap does not close by waiting.

---

## The chain, each link measured rather than assumed

1. `core.hooksPath` = `/home/rich/synthetic-enterprise/tools/git-hooks` — the shared tree's
   **working copy**, resolved to that same absolute path from every linked worktree.
2. That copy is a clean snapshot of the shared tree's HEAD (`025b2793c`) — verified by blob:
   disk, index and HEAD agree. It is **not** a mixture.
3. The shared HEAD is **3 behind and 9 ahead** of `origin/main`, and one of the behind commits
   (`bfa285755`) touches the hook. So the live chain is missing `live_hook_drift` — the reporter
   naming its own absence, and `python3 -m tools.live_hook_drift` in the shared tree is
   `ModuleNotFoundError`.
4. The only door that advances that checkout is
   `background.origin_reconcile.advance_shared_tree`, and it **fast-forwards**.
   `git merge-base --is-ancestor HEAD origin/main` → **false**. Git will not fast-forward a
   diverged branch, and that module already knows it: *"Diverging branches can't be
   fast-forwarded"* is quoted in its own docstring.
5. So the advance is refused **every time the reconciler runs, forever**, until the ahead leg
   reaches the trunk.
6. And the ahead leg cannot: `6a422ea0f` carries neither a `surgical_land` receipt nor a hook-gate
   mark, and `promote_worktree_landing` refuses the whole leg on it.

**Every surface in the tree said "the remedy is the reconciler advancing the SHARED checkout."
For this tree that sentence names an operation that cannot run.** A reader who believed it waited
for something structurally impossible while the missing gate went on not running.

## What landed for it

`tools/live_hook_drift.advance_blocked_reason` asks the owning checkout whether it can
fast-forward onto the reference at all, and the report now prints
`AND THE ADVANCE IS NOT AVAILABLE: …` beside the remedy it overrides — in **both** report
branches, which is a correction: the first draft's control was satisfied by the clean-branch
append and stayed green when the differing-branch one was deleted. That mutation went green, was
treated as a missing test rather than an equivalence, and the control now exercises both returns.

Keyed to the property (*can this checkout fast-forward onto the reference?*), so the day the tree
is levelled it goes **quiet**, not red.

## What is NOT fixed, and the recommendation

The knot itself. `6a422ea0f` was made at 2026-09-24 20:35, **before the hook-gate mark mechanism
existed** — `934343669` landed it later that night. The guard's own refusal says so plainly: *"A
commit older than that mark may well have been gated and simply cannot show it."* So the door is
refusing a commit for lacking evidence that had not been invented when the commit was made, and
the two remedies it offers are both unavailable: re-landing it means rewriting eight commits of
other lanes' work beneath it, and `reset`ting past it destroys them.

**Recommendation, for the director because it touches the hook-bypass wall and nothing else here
does.** The cut I judge correct is *not* an amnesty for unmarked commits — that would reopen the
exact hole the mark was built to close, since a hook-gated commit and a `--no-verify` one are
byte-identical to that function. It is that **advancing the checkout and promoting the ahead leg
are two different operations, and only the second needs the wall.** The hooks working copy needs
`origin/main`'s bytes present; it does not need the local commits pushed. A *merge* of
`origin/main` into the shared tree advances the working copy — and therefore the live gate chain —
while leaving the ahead leg exactly as unpromoted, and as refused, as it is today. The reconciler
conflates the two by only ever offering `--ff-only`.

I am not making that change from a worktree: a merge in the shared tree with other lanes' work
uncommitted in it is precisely what `surgical_land` exists to prevent, and the item forbids it by
name. It needs to run in the shared tree, under the tree lock, by a lane that owns it.
