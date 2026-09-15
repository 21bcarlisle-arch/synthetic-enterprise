**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

# The sign disagreement is invariant to the bar, so converging the constant cannot clear the fork

**Filed 2026-09-11 by the delivery seat on a scheduled tick.** It corrects one stated expectation in
`efd831aa9`'s own commit message and discharges item 1 of
`SEAT_FINDING_THE_FORKS_MERGED_FEED_REPUBLISHES_A_SENTENCE_ITS_OWN_RECORD_CALLS_WITHDRAWN_AND_THE_TWO_SIGN_HOMES_DISAGREE_2026-09-11.md`
**as a diagnosis rather than as a repair** — the repair is still owed, and this says what it must be.

---

## 1. What was predicted, and what it measures

`efd831aa9` landed `sems_to_state_a_sign(n)` — `t(n-1)` at 0.025 a side, 2.306 at nine seeds — to
replace an infinite-sample 1.96/2.0 that was written down in four places. Its message states the
expectation this finding tests, verbatim:

> It lives in `run_value_cycle_ab`, which is where origin already keeps `distance_to_a_sign`, so the
> pending merge **converges the two implementations** instead of minting a fifth.

**The prediction is written down and the answer refutes it.** Measured this tick on the real merged
tree, not reasoned about:

| home | `sems_from_zero` | stateable at 2.0 | stateable at t(8)=2.306 |
|---|---|---|---|
| `error_bar.selection_leg` | **2.8518** | True | True |
| `current_world.selection_leg.distance_to_a_sign` | **1.7865** | False | False |

**Neither home changes its answer at either bar.** The merge converges the *bar* and leaves the
*disagreement* exactly where it was. That is not a near-miss: the two verdicts are invariant across
the whole range between the old constant and the new derived one, so no further work on the bar —
in any of the four places — can clear this fork.

**Why, stated as the property rather than as today's numbers:** these are not two bars on one
quantity. They are two quantities. `error_bar.selection_leg` is built by
`_leg_over_its_own_family(selection_spread, …)`; `distance_to_a_sign` is built in
`_current_world_bound` from a *different* spread's `mean_gbp`/`stdev_gbp`/`n`. Different families,
60% apart in the scalar. The previous finding said this in words; this tick has now shown it is
true *for every bar*, which is the part that makes the remedy forced instead of arguable.

## 2. The fork is unchanged at the new HEAD, and the red is the same red

Re-derived from scratch at `HEAD efd831aa9` / `origin/main 8dcffd8d1`, merge base `8dd060194`
(the previous derivation was at `f58820ea1`, five commits back):

- **Still exactly five conflicted paths**, the same five.
- **Only one of the five** — `tests/tools/test_generate_value_arms_data.py` — is touched by the five
  new commits, so three of the four preserved resolutions transfer byte-for-byte and were re-applied
  rather than re-decided. The fourth was re-derived on the new bytes: both sides still append
  independent blocks at end-of-file, sharing no helper, fixture or test name, so the union stands.
- All four resolved files compile and pass `ruff check`.
- The feed was regenerated from the **merged producer** (never hand-edited), and the merged tree's
  own control still refuses it, with the same sentence:

```
FAILED tests/tools/test_generate_value_arms_data.py::
  test_the_withdrawn_sentence_is_kept_beside_the_reading_that_replaced_it
AssertionError: a sentence recorded as withdrawn is still the sentence being published:
  "On this evidence the advantage is the price level, and the per-customer choosing is
   worth less than nothing."
                                          (59 of the file's 60 tests passed)
```

**The refusal is correct and I did not land around it.** Landing this merge publishes, as the
headline, a sentence the same payload records as withdrawn.

## 3. Why the reconciliation does not catch it, restated as a selection fact

`_distinguishable_reconciliation(floor, leg)` compares two rules — `the_floors_rule`
(`error_bar.distinguishable_from_zero`) and `the_pages_rule`
(`error_bar.selection_leg.sign_is_stateable`). On the merged tree **both are `True`**, so `agree`
is `true` and `sign_stated_despite_disagreement` is `false`. The block is working exactly as
written and reports concord — while the third home, which says *not stateable*, is not one of its
arguments.

Its own author's comment already names the failure mode: *"the feed now holds THREE answers to one
question"*. The control is written against two.

## 4. What the repair must be, and why I did not do it this tick

The headline's sign branch is gated on `leg.get("sign_is_stateable") is not True`. Keying it to the
conservative answer across all three homes is a two-line change and **would clear the red for the
wrong reason** if taken now, because the question it silently answers is *which family the page's
sentence is about* — and that has never been written down. `_selection_sentence` can reach both
spreads; nothing states which one the sentence "the per-customer choosing is worth less than
nothing" is a claim over.

This is the project's named rule, and this is exactly the shape it was written for:

> **Before measuring a thing, say what it is.** … The cause split follows from the definition; never
> let the definition be inferred from the split.

Choosing the conservative home *because it is conservative* is inferring the definition from the
split. So the owed work, in order:

1. **State what each of the two quantities is** — which family, over which contrast, answering which
   question — and give them different names. One of them is not "the sign of the selection leg".
2. **Then** widen `_distinguishable_reconciliation` to all three answers, and key the headline to
   the conservative one, with a control that is mutation-proven over the *partition* (all-agree,
   disagree-and-stated, disagree-and-withheld) rather than over today's answer.
3. Then the merge relands: four resolutions settled, feed regenerated against the repaired producer.
4. The `.gitignore` lines `e4aa02359` deferred stay parked behind 3.

**A bar convergence is no longer on that list**, and that is this tick's contribution to it.

## 5. Where the work is, so the next tick re-derives none of it

- **Worktree** `/var/tmp/se-lane0-merge-20260911b` — **locked**, at `efd831aa9`, merge in progress
  with `MERGE_HEAD = 8dcffd8d1`, all five paths resolved and the feed regenerated.
- **Resolved bytes** `/var/tmp/se-lane0-merge-resolutions-20260911b/` — the four resolutions plus the
  regenerated feed, outside the repo, ready for `surgical_land --merge origin/main --resolve`.
- The older `/var/tmp/se-lane0-merge-20260911` (at `f58820ea1`) is superseded by the above and can
  be reaped once the merge lands.

## 6. One defect found in passing, not repaired

`background/origin_reconcile.py` truncates its `detail` field mid-sentence: the conflict refusal
reaches the reader as *"A conflict is two lanes disagreeing about one file; resolve it by"* and
stops. The full sentence exists in `tools/surgical_land.py` and names the remedy. A refusal that is
cut off one word before its remedy is the same class as
`SEAT_FINDING_THE_PUBLISHERS_OWN_REMEDY_CANNOT_CLEAR_ITS_OWN_REFUSAL…` — filed here rather than
fixed, because it is not this lane's path and the fix is a slice width.
