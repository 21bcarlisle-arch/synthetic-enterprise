**Severity:** BLOCKING — 23 tests are RED in the shared working tree right now, on the census's
own rung suites, and every lane that runs them sees a red it did not cause · **Lane:** H_harness ·
**Epoch:** 3 · **Atom:** none — LANE 0 delivery, the third-question generalisation ·
**Class:** uncommitted_and_orphaned_work

# The shared tree holds a superseded draft of the census that deletes two landed rungs, and 23 tests are red behind it

Filed 2026-09-05 by the autonomous worker. Drawn work was the third question asked of the
register-shaped siblings (`removed_dispositions()` generalised). The drawn item's premise begins
*"the census now has all three rungs"* — **true at HEAD and on origin, false in the shared working
tree**, which is what this finding is about. The drawn work itself landed separately and is not
blocked by this.

## 1. What was measured

`background/self_clearing_alarm_census.py` is dirty in the shared tree: **105 insertions, 231
deletions** against HEAD. What the working copy removes and adds:

| function | HEAD | origin/main | shared working tree |
|---|---|---|---|
| `removed_dispositions` | present | present | **deleted** |
| `shared_loader_answers` | present | present | **deleted** |
| `load_retired`, `_dispositions_at_head`, `_claim_sentences` | present | present | **deleted** |
| `rows_graded_by_resemblance`, `_cited_siblings`, `_own_carriers_named` | absent | absent | added |

Running the three rung suites against the shared tree as it stands:

```
tests/background/test_the_register_can_lose_a_row_and_take_the_alarm_with_it.py
tests/background/test_one_answer_standing_on_several_census_rows.py
tests/background/test_the_rows_that_concluded_on_a_sibling.py
→ 23 failed, 16 passed
```

The file's mtime is `08:20:08`. `dc5fcbbc8` — the commit that landed `removed_dispositions()` —
is timestamped `08:16:39`. The draft was written **three and a half minutes after** the work it
deletes had already landed, and has not been touched in the hours since.

## 2. What the draft actually is

It is not new work racing landed work. It is **the superseded side**.

`8cd3bfc25`, the most recent commit to this file, is titled:

> *the resemblance rung was built against citations, so it was blind to the answer that cites
> nothing*

That commit replaced a citation-keyed resemblance rung with `shared_loader_answers` +
`_claim_sentences`, which grade by the ANSWER rather than by the CITATION. The working copy holds
`rows_graded_by_resemblance` + `_cited_siblings` — **a rung keyed to citations**, i.e. precisely
the approach `8cd3bfc25` measured as blind and replaced. A lane wrote it from a base older than
both of the last two commits and the tree still carries it.

This is the shape already in the record as *"the file that held the advance for nine attempts
carried work origin had already reimplemented"*, and as *"a merge adopting one side's rewrite
silently deletes the other's additive work"*. It is the same defect one step earlier: before any
merge, sitting in the working tree.

## 3. Why this is not self-correcting

The reassuring reading is "the gate will catch it" — and the gate *would*: a pathspec commit of
this file stages the working-tree copy, the 23 tests go red, and the land is refused. That is
real, and it is why this is BLOCKING rather than a silent data-loss finding.

But it is not a resolution, for three reasons:

1. **The red is charged to whoever next touches the file.** A lane landing an unrelated one-line
   change to the census by pathspec inherits 23 failures it did not cause, spends a full ~12-minute
   gate cycle discovering that, and has no way to tell from the refusal that the cause is a stale
   draft rather than its own edit.
2. **The cure for the red is the deletion.** The fastest way for that lane to get green is to make
   the working copy match HEAD — which is correct here, but it is the same "delete the evidence to
   clear the refusal" gradient this whole class of control exists to remove. Nothing in the refusal
   says which direction is right.
3. **A pathspec is not protection here.** The rule that stops a pathspec sweeping another lane's
   work protects other FILES. A file another lane has edited *in place* carries their work inside
   yours, and that is exactly this file's state.

## 4. What I did not do, and why

I did not touch `background/self_clearing_alarm_census.py`. It is another lane's uncommitted work
in a shared tree, `git checkout <path>` is forbidden here, and "this draft looks superseded to me"
is a judgement I can make about the code but not about whether the lane holding it has a reason I
cannot see. Restoring HEAD's copy would also be indistinguishable, in the diff, from the 2026-09-05
incident where a rewrite from a pre-sweep copy deleted 33 annotations.

The honest act from a bounded invocation is to measure it precisely, name which side is superseded
with the evidence, and file it. **The seat is the only place that can hold this**, because it is
the only vantage that sees both the landed commits and the tree state at once.

## 5. Recommendation

Discard the working-tree copy in favour of HEAD's, from the seat, deliberately:

- The draft's rung (`rows_graded_by_resemblance`, citation-keyed) is the approach `8cd3bfc25`
  already measured as blind to the answer that cites nothing, and replaced. Nothing in it is
  additive over HEAD.
- Nothing else in the tree imports the three added names — they are unreachable.
- If any part of it is wanted, it is one function and it can be re-derived against the current
  base, where `shared_loader_answers` already occupies the ground it was aiming at.

If a lane does hold a reason for that draft, this finding is the place to say so, and the reason
belongs beside the code rather than in a working tree nobody can attribute.

## 6. A second, separate observation from the same turn: the claim was never in the store

The tick's instructions were explicit — *"IMMEDIATELY AFTER EACH COMMIT, run `--landed
census-register-low-water-third-question`; skip it and the claim is swept back into the pool in 100
minutes however much you landed."* The commit landed as `605ec3995`. The bind refused:

```
bound NOTHING to census-register-low-water-third-question: it is NOT CLAIMED
```

`CLAIMS_FILE` resolved to the **shared tree** (`/home/rich/synthetic-enterprise/docs/observability/
.delivery_lane_claims.json`), so this is not the per-worktree-store trap that `refusal_reason` was
taught to name on 2026-09-05. The store is simply **empty** — it holds no claims at all, for any id.

I did not forge a `claimed_at` to make the bind succeed. Work landed before it was claimed can never
be bound and is re-offered forever, and a fabricated claim timestamp is how that becomes permanent.
The consequence is stated rather than hidden: **`605ec3995` is landed and the delivery lane cannot
see it**, so this item is liable to be re-drawn and rediscovered by a later turn.

This is an instance of the class already parked as
`WORKER_FINDING_THE_SANCTIONED_MERGE_ROUTE_LANDS_WORK_THE_DELIVERY_LANE_CANNOT_SEE_2026-09-03.md`,
noted here rather than minted as a rival. What this instance adds is that the store was empty
*at bind time on a tick that had just drawn the item* — so the gap is between the DRAW and the
STORE, not between the land and the bind.

## 7. What this cost, stated plainly

Nothing yet, in landed terms — HEAD and origin are both intact and the drawn work landed around
it. The cost so far is 23 red tests that every lane in this tree now has to reason past, and a
premise in the delivery queue (*"the census now has all three rungs"*) that reads as true from
git and false from the tree.

## Class registration

Belongs to `controls_that_cannot_fail`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 3 matches for `controls_that_cannot_fail` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
