**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** unminted

# RESULT — the churn-belief premise was spent, and the wedge underneath it had moved to a remedy that reverts corrections

The drawn item was *"the churn-belief renderer is unstaged so the site lane refuses every commit"*.
Both of its premises are spent, the third clause turned out to be a live defect in a different
module, and that is what this turn landed.

## The premise, re-measured before any work

The item's own PREMISE CHECK already warned that `d08b1b104` was an ancestor of `origin/main`. It
is, and so is the work:

| claim the item made | measured 2026-09-24 00:0x UTC | verdict |
|---|---|---|
| two hunks of `site/capabilities/index.html` are on disk and not in the index | `legs_the_belief_hears` count = 1 at HEAD, = 1 in the index, = 1 on disk | **spent** |
| `site/test_the_flat_churn_belief_reaches_the_reader.py` is 3 failed / 12 passed | **15 passed, 0 failed** at `origin/main` | **spent** |
| the site lane's refusal is those three reds | `.publish_gate_state.json` → `blocking_tests: []`, `total_red: 0` | **spent** |

The item's careful superset argument — *"do not `refresh_to_head` this file, the clock is
misleading, use `isolate_hunks` then `surgical_land --content`"* — was correct reasoning about a
pile that no longer exists. Nothing was landed against `site/`, because there was nothing to land.
This is the seventh instance of the class *a drawn item's claim about the tree is an un-re-asked
prediction*.

The live duplicate claim the draw flagged was **my own draw**, 40s old with `paths: []` — not a
rival.

## The clause that was NOT spent, and what it actually is

The item's real exit test was the third clause: *"finished when a figure moves on origin"*.
`last_clean_publish` was **2026-09-21 18:15:57Z — 53.8 hours cold**, and `wedge_since`
2026-09-21 20:40:07Z. But the cause had changed underneath the item. It is now `behind_origin`,
and the refusal routes the reader to `background/origin_reconcile`, which refuses in turn on
untracked paths blocking the fast-forward.

**That second refusal names a remedy which, applied literally, reverts landed corrections.**

`origin_reconcile._landing_clause` printed, for the `FF_UNTRACKED` kind:

> the 3 UNTRACKED path(s) clear by landing them (`python3 -m tools.surgical_land <path>`) or by
> removing them, whichever the holding lane wants

Two doors, offered as equals, landing first. They are not equals, and the asymmetry is
**definitional, not statistical**: `FF_UNTRACKED` means *origin already brings a copy of that
path*. So landing the local copy **replaces origin's file**; it does not add one. And an orphan
draft abandoned in a shared tree is routinely the **older** of the two, because the lane that wrote
it went on to land a fuller version from its own isolated worktree and left the draft behind.

Measured on the live population, of the three untracked blockers named:

| path | disk | origin | direction |
|---|---|---|---|
| `...THREE_ALARM_FAMILIES_BYPASS_NOTIFY...md` | 4672 B | identical | clears itself |
| `...THE_HEADER_IS_STAMPED_ONCE...md` | 7727 B | 9112 B | **disk is a strict SUBSET** — 19 deletions, 0 insertions |
| `...THE_ALARM_FAMILY_FILES_EIGHT_DISTINCT_NAMES...md` | 3042 B | 3995 B | **disk is the pre-correction draft** |

The third is the sharp one. Origin's copy carries a section headed
`## CORRECTION, same turn, kept beside the claim it replaces`, which exists *solely* to retract the
recommendation the disk draft still makes (*"run `collapse_alarms` as its own commit"* — refuted in
seconds by a `--dry-run` that emitted nothing). **Landing the disk copy would have deleted the
correction and reinstated a claim its own author had already refuted by measurement.** The refusal
named that as its first option.

This is the **third instance** of the defect
`tests/background/test_a_generated_blocker_is_not_offered_a_landing.py` already documents twice
(2026-09-09 `value_arms.json`, 2026-09-15 `orphan_baseline.json`) — *the remedy named the one
action that undoes another lane's fix*. Both prior instances were `FF_MODIFIED`. Nobody had asked
the question of `FF_UNTRACKED`, and that branch had **no control over its wording at all**: a
tree-wide grep for its text returned the producer line and nothing else.

## What landed

`background/origin_reconcile.py` — the untracked step now states the replacement, gives the one
command that settles direction (`git diff <(git show origin/main:<path>) <path>`), and names
removal as the lossless door **with where the bytes go** (`refs/preserved/origin-reconcile-orphan/`,
written before the clear). Keyed to the kind's definition, not to today's three paths.

`tests/background/test_a_generated_blocker_is_not_offered_a_landing.py` — two legs, in the file
that already owns this defect class rather than a new module. One asserts the untracked step names
the replacement and the direction check; one asserts the partition, so a single step that swallowed
both kinds cannot pass by telling each reader the other's door.

**Mutation-proven, and it fired on the leg written for it.** Restoring the pre-fix wording: 2
failed, 9 passed — exactly the two new legs, and no other.

## What I did NOT do, and why it is the right refusal

I did not touch the shared tree's untracked files, although clearing them is what advances
`last_clean_publish` and that was the item's stated exit test.

`origin_reconcile` was **in flight while I measured** (PID 2032986, `surgical_land --merge
origin/main` in a throwaway worktree), and its own commit message states the reason the shared tree
is off-limits: *"Done in a throwaway worktree with its own index, so the objection the publish
path's own refusal raises — a daemon merging unattended would move other lanes' uncommitted work —
cannot apply: the shared tree is never opened."* A seat reaching in by hand to `rm` two lanes'
orphan drafts is precisely the objection that design refuses, and doing it while two merges are
running is worse. The sanctioned door was already running.

So the 53.8-hour wedge is **not cleared by this turn**, and I am not claiming it is. What this turn
removed is the trap sitting one step down the remedy chain: the next reader routed to
`origin_reconcile` will no longer be told that landing an orphan draft is a free choice.

## The un-re-asked question this leaves

`last_clean_publish` has not moved. If the reconciler's in-flight merges clear it, the item is
finished by another lane's hand; if they do not, the next draw should ask **why an untracked
blocker population regenerates** rather than clearing the instances again — the 2026-09-10 note in
`_arriving_paths` records exactly that shape (`4 → 9 → 12 → 15` in one day) for a different cause,
and a second self-refilling instance would be the finding, not the files.

I predicted before looking that the wedge would still be the three site reds. **It was not** — they
had been green for some hours. The cause had moved and the item's diagnosis had rotted with it.
