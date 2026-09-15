**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

# The fork's merged feed republishes a sentence its own record calls withdrawn, and the two sign homes stop agreeing

**Filed 2026-09-11 by the delivery seat on a scheduled tick**, holding
`the-fork-is-one-conflicted-file-and-it-holds-the-selection-legs-two-homes`. It corrects the
premise of that drawn item and of
`SEAT_FINDING_THE_RECONCILERS_BLOCKING_TEST_ASKS_WHICH_PATHS_DIFFER_NOT_WHICH_THE_MERGE_WOULD_WRITE_SO_IT_REFUSES_FOREVER_ON_THIS_BRANCHS_OWN_DELETIONS_2026-09-10.md`
(§4), which measured the fork at **one** conflicted path on 2026-09-10.

---

## 1. The drawn item's two premises are both spent, and the second one matters

**"The merge's single conflicted path."** Re-measured this tick, read-only, at
`HEAD f58820ea1` / `origin/main`, merge base `8dd060194`:

```
$ git merge-tree --write-tree HEAD origin/main        -> 82fa4f0e5  (rc=1)
  docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md  (add/add)
  simulation/net_new_acquisition.py                   (content)
  site/data/value_arms.json                           (content)
  tests/tools/test_generate_value_arms_data.py        (content)
  tools/pre_commit_test_gate.py                       (content)
```

**Five, not one**, and the divergence is 26 ahead / 31 behind, not 21 / 24. Both sides kept
committing into the same files for a day after that finding was written.

**"Both homes carry the same `sems_from_zero: 1.7865206920288081` under different keys."** True of
the two sides' stale bytes. **False of the bytes the merged producer actually emits** — §3.

## 2. Four of the five are resolved, and the resolutions are on disk

Resolved in a real worktree with a `.git` (`/var/tmp/se-lane0-merge-20260911`, locked), per §5 of
the finding above. None of the four is a judgement between two lanes; all four are two lanes' work
that git could not interleave:

| path | what the two sides were doing | resolution |
|---|---|---|
| `tools/pre_commit_test_gate.py` | each adds a DIFFERENT entry to the always-run list; HEAD's comment says the seat-guard line is WITHHELD because it was red, origin's change is the one that made it green | both entries; HEAD's withholding paragraph deleted **because origin discharged it** |
| `tests/tools/test_generate_value_arms_data.py` | two different blocks appended to the end of one file; no shared helper, fixture or test name | both blocks |
| `docs/staging/records/SEAT_PREREGISTRATION_…_2026-09-11.md` | **two independent pre-registrations of one drawn item, written the same day from two bases that had silently diverged** | both, in one file |
| `simulation/net_new_acquisition.py` | HEAD lifted the count cull out behind `settle_within_budget` so a selection rule could be measured; origin wrote the difference chooser INLINE in the block that lift had just emptied | the chooser folded **into** the seam |

The last two are the ones worth reading.

**The pre-registration is two documents and both are kept.** The bands do not agree — origin's
copy predicts a KS ratio ≥1.25× with a kill below 1.10×, the shared tree's [1.2×, 2.0×] — and both
lanes have since measured (`9076ffc36`: *worse than three-quarters of random draws of its own
size*; `3957ba848`: 0.12798 culled against 0.08241 chosen, 1.553×). A pre-registration's only value
is being provably older than its answer. Adopting one side would have deleted one of two
predictions **after both answers were known**, which is the single edit a record of this kind
cannot survive.

**The settlement conflict is two halves of one change, and adopting either side alone loses the
other's whole point** — take origin's and the rule is unmeasurable again, take HEAD's and the
chooser is gone. Folding the chooser into the seam is strictly better than either side shipped:
`tools/settlement_choice_probe.py` monkeypatches `settle_within_budget`, so the chooser is now on
the measurable side of the seam, which is what the lift existed for. `weight_by_year` is returned
and unpacked because a row downstream reads it — caught by lint, not by inspection.

## 3. The fifth path cannot be resolved, and the reason is a published falsehood

`site/data/value_arms.json` is generated, so the resolution is to regenerate from the merged
producer. Done, in the real worktree, and §5's trap is cleared — this is the field that finding
said was the whole of it:

```
publishing_tree_commit                  f58820ea1…   (not null)
objective.established                   true         (not false)
objective.clause                        "The renewal objective is the same rule at both commits…"
```

**And the merged tree's own control refuses the result.**

```
FAILED tests/tools/test_generate_value_arms_data.py::
  test_the_withdrawn_sentence_is_kept_beside_the_reading_that_replaced_it
AssertionError: a sentence recorded as withdrawn is still the sentence being published:
  "On this evidence the advantage is the price level, and the per-customer choosing is
   worth less than nothing."
                                                          (59 other tests in the file passed)
```

The merged feed puts a sentence its own withdrawal record names **back into the headline**. Neither
parent does this. The cause is a number that only exists on the merged tree:

| | HEAD | origin/main | **merged** |
|---|---|---|---|
| `error_bar.selection_leg.sems_from_zero` | 1.7865 | *(key absent)* | **2.8518** |
| `error_bar.selection_leg.sign_is_stateable` | false | *(absent)* | **true** (`sign: negative`) |
| `current_world.selection_leg.distance_to_a_sign.sems_from_zero` | *(absent)* | 1.7865 | **1.7865** |
| …`.sems_needed_to_state_a_sign` | — | 2.0 | 2.0 → **not stateable**, needs 12 seeds, has 9 |

HEAD's `error_bar` block reads origin's newer floor artefacts, the estimate moves from −£1,078 to
−£1,749 against a near-identical bound, 1.79 SEMs becomes 2.85, the sign becomes stateable, and the
withdrawn sentence comes back. **Both parents said "not stateable". The merge says both at once.**

**So the answer to the drawn item's question is that neither home can be deleted inside a merge
resolution, and that was the wrong question.** They are not two homes for one quantity — the
scalars differ by 60% and are computed over different families. They are two quantities with one
name, which is this project's most expensive recurring shape, and the merge is where it becomes
visible rather than where it is caused.

**And the reconciliation that exists to catch exactly this is blind to it.** HEAD's own
`error_bar.distinguishable_reconciliation` (landed `cb431653b`, mutation-proven) compares the
floor's rule at 2 SEM against the page's at 1.96 and reports `agree: true` — because both of its
two rules read `error_bar`, and neither reads `current_world.selection_leg.distance_to_a_sign`. A
control written against two answers, on a feed that now holds three. Its own author's comment names
the failure: *"the feed now holds THREE answers to one question"*.

## 4. What I did NOT do, and why

**I did not land the merge.** Landing it publishes a withdrawn claim to the reader. The refusal is
the control's, not mine, and it is correct.

**I did not hand-edit the feed to clear the red.** A generated feed whose bytes did not come from
its producer is worse than the wedge — the conflict resolution would then be a content change
wearing a merge's receipt, which is the shape `surgical_land`'s resolve-rule 1 exists to stop.

**I did not adopt one side's bytes to make the conflict go away.** Either choice silently picks
which of two disagreeing sign answers the page states, without the disagreement ever being seen.

The four resolved paths and the regenerated feed are preserved outside the repo so the next tick
re-derives none of this: the worktree `/var/tmp/se-lane0-merge-20260911` (locked, merge in
progress) and `/var/tmp/se-merged-value-arms-20260911.json`.

## 5. What IS landed this tick

§6 of the finding this corrects: `paths_blocking_fast_forward`'s candidate set is now the merge
result's diff against HEAD, not the endpoint diff. Measured on the real tree, **33 blocking paths
→ 24**, with both self-regenerating head-red false positives gone. Mutation-proven: restoring the
endpoint diff reds exactly one assertion,
`test_a_path_THIS_BRANCH_DELETED_is_no_longer_reported`, and nothing else. Two poison legs prove
the narrowing cannot hide a true positive, and the first draft of the conflict leg **was wrong and
the fixture caught it** — a conflict that is only committed blocks the merge but not the checkout,
so poisoning against conflicts needs a path that is conflicted AND dirty. 41 existing reconciler
assertions stay green.

## What is next

1. **The sign disagreement is the fork's blocker and it is a real defect, not a merge artefact.**
   One of the two blocks must stop answering "can the sign be stated", or the reconciliation must
   be widened to all three answers and the headline keyed to the conservative one. That is a
   producer change with its own controls, in daylight — not a conflict resolution.
2. Then the merge relands unchanged: the four resolutions above are settled and preserved, and only
   the feed needs regenerating against the repaired producer.
3. The `.gitignore` lines `e4aa02359` deferred for both head-red paths. Its stated reason for
   deferring was the fork; §5 does not close the fork, so this stays parked behind item 2.
