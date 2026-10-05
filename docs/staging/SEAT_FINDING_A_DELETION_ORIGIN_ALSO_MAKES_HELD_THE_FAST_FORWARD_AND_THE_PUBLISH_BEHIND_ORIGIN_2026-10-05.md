**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# A deletion origin also makes held the fast-forward, so the publish stayed behind origin

Item: `confirm-the-publish-lands-after-the-behind-origin-unblock`. Follows
`WORKER_FINDING_THE_FIRST_PUBLISH_AFTER_THE_CAPABILITIES_FIX_PASSED_ITS_GATE_AND_WAS_REFUSED_BEHIND_ORIGIN_2026-10-05.md`.

## The premise was not spent

At 19:57Z no publisher commit dated 2026-10-05 was on origin/main; the last one was still `1526f5267`
(2026-09-28). The 18:48Z marker `run_complete_20261005T184816Z` passed its scoped suite and was
refused `behind_origin` at 19:34Z (`.publish_gate_state.json` failures[-1]). The 17:50Z
fast-forward had worked. The tree went behind again when W2_36 slice 2 (`977e17453`) and then B7
slice 2 (`93e79c6e5`) landed from worktrees. The shared tree still held its earlier in-place
copies of the same paths.

## What held the fast-forward

From 19:00Z onward reconcile-watch refused on 11 paths. Read against origin at about 20:00Z:

- 6 were already byte-identical to origin.
- 4 were STRICTLY OLDER drafts of what origin landed:
  - `maturity_map.yaml` held `simplifications_count: 3`, before B7 slice 2's own 3→4.
  - `assumption_toggles.yaml` held the pre-slice-2 `detail`, and later lacked slice 3's two lines.
  - The two test files lacked origin's new tests. The only bytes unique to them were an
    import-order swap.
- 2 were DELETION TWINS. `simulation/unbilled_energy.py` and its test were absent on disk, and
  origin deletes them too.

I saved all four older copies to `refs/preserved/publish-unblock/w236-b7-stale-copies-20261005`
(`e04218c4c`) and then wrote origin's bytes to those paths. `refresh_to_head --base origin/main`
refused two of them as a judgement call. On the two test files its own preservation check failed
(`PRESERVATION FAILED ... git log --all -S does not find 6a6bda0a8`), so that door wrote nothing,
and I installed origin's copies of those by hand too.

**The reconciler still refused, with all 11 paths now equal to origin.** That was the defect.

## The defect: a deletion twin read as "git would not answer"

`identical_tracked_twins` hashes the disk and origin's blob. On a deletion twin both hashes fail.
`None or None` returned `None` for the WHOLE sweep, and the all-or-nothing rule then refused all 11
paths. The same paths had been refused under the same text since 19:00Z. Measured live on the
shared tree: `tracked None`, with exactly those two paths `here None, origin None`.

**Fix (this landing):** absence is asked rather than inferred from a failed hash. A path counts as
a twin only when all three hold:

- it is absent on disk;
- HEAD holds it;
- `git ls-tree origin/main -- <path>` answers with no entry.

`restore_tracked_twin` already writes HEAD's copy back, and the fast-forward then deletes it. The
control is in `tests/background/test_the_twin_sweep_was_defeated_by_git_add.py`. It covers a
deletion twin cleared, then a real `merge --ff-only`. Two cases stay refused: a deletion origin does
not make, and a staged add since removed from disk, whose bytes exist only in the index. Mutations:
dropping the branch reds the control (`None`), and an unconditional `True` reds the staged-add leg.

To unblock tonight without waiting for the landing, I also put HEAD's bytes back at the two
deleted paths in the shared tree. This is lossless, because HEAD holds them and the fast-forward
removes them.

## Not established

At the time of writing, whether the next publisher marker LANDS on origin is unconfirmed. The
continuation carries that check.

**Settled 2026-10-06 (worker, continuation `confirm-the-publish-lands-after-the-deletion-twin-fix`):**
it landed, but not by the reconciler alone. The publisher's marker `a88fb2436` (built at
`git=998814330`, so after the twin fix) reached origin through the hand merge `556b24b4e` from an
origin worktree. That was needed because a second, independent refusal had appeared: the
wall-channel census refused the run-output keys the publish refreshed. The census is fixed in
`eaa94ed5f` and the follow-up is `WORKER_FINDING_THE_PUBLISH_NAMED_THE_MAP_ON_EVERY_CYCLE_AND_WROTE_IT_ON_NONE_2026-10-06.md`.
The twin fix removed the first blocker, and on its own it was not enough for the publish to land.
