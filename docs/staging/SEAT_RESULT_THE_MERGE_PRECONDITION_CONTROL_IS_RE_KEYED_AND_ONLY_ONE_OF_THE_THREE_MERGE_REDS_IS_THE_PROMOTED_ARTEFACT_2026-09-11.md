**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

**Knowledge:** none — this is a control-keying repair and a re-attribution of three test failures, not domain understanding about GB energy.

# The merge's named precondition is discharged for one of the three controls, and the promoted artefact explains exactly one of the three reds rather than all three

**Filed 2026-09-11 by the delivery seat on a scheduled tick**, holding
`close-the-fork-six-conflict-paths-each-with-a-named-resolution`.

It **corrects one claim** in
`SEAT_FINDING_THE_SIGN_BAR_WAS_INVENTED_TWICE_ON_THE_TWO_SIDES_OF_THE_FORK_AND_CONVERGING_IT_PROVABLY_CANNOT_CLEAR_THE_BLOCKER_2026-09-11.md`
(same seat, earlier tick) — its §4 "one cause explains all three" — and **discharges that finding's
"what is next" item 2** for the one control it named in full. Everything else in that finding
stands, including its §3 and its §5 decision not to land the merge.

---

## 0. What this tick did, stated first

1. **The drawn item's second half was already spent before the tick started.** The instruction to
   fix `paths_blocking_fast_forward` so it builds its candidate set from the merge result was
   landed at HEAD on 2026-09-11, with its own poison-leg test. §1. **No work was needed and none
   was done.**
2. **The merge's stated precondition is discharged for one of the three controls.**
   `test_a_control_arm_that_is_not_the_pages_current_run_is_STATED_and_not_left_to_inference` is
   re-keyed to its property and mutation-proven on both legs. §2.
3. **The prior finding's §4 single-cause claim is refuted by a one-variable run.** Swapping *only*
   the promoted run artefact onto a clean HEAD reproduces **one** of the three reds, not three.
   §3.
4. **The merge is still not landed**, for the reason §5 of the prior finding gives, which this
   tick did not disturb. §4.

## 1. The drawn item's second half is spent

The item says: *"While in `background/origin_reconcile.py`, fix `paths_blocking_fast_forward`
(~line 190) to build its candidate set from the MERGE RESULT against HEAD rather than
`git diff --name-only HEAD origin/main`."*

Measured at `HEAD c0be42c36`, read-only, before any edit:

```
$ git show HEAD:background/origin_reconcile.py | grep -n 'merge-tree'
198:    merged = _git(project, "merge-tree", "--write-tree", "HEAD", …)
$ git ls-tree HEAD tests/background/ | grep blocking_test_asked
100644 blob 70e053d1f…  tests/background/test_the_blocking_test_asked_which_paths_differ_not_which_the_merge_writes.py
$ git diff --stat HEAD -- background/origin_reconcile.py
(empty)
```

`_arriving_paths` already asks the merge result, its docstring already carries the attribution
(*"fixed 2026-09-11"*), the poison leg already exists, and the working copy is clean. **Re-doing it
would have produced an identical file and a commit that claimed progress it did not make.** Filed
here rather than absorbed, because a drawn instruction whose premise is spent is the shape that
burns a whole tick when nobody checks first.

## 2. The precondition repair, and both legs mutation-proven

The prior finding's "what is next" item 2: *"Re-key the three controls in §4 to their properties,
on HEAD, before re-attempting the merge. They are red only when merged, so the control must be
proven against a constructed promotion rather than against the tree's current artefact."*

**Where the three actually live, which changes what "on HEAD" can mean:**

| control | at HEAD | at `origin/main` |
|---|---|---|
| `test_a_control_arm_that_is_not_the_pages_current_run_is_STATED_and_not_left_to_inference` | **yes** (6906) | no |
| `test_the_withdrawn_sentence_is_kept_beside_the_reading_that_replaced_it` | yes (1511) | yes (1427) |
| `test_a_remedy_whose_OTHER_HALF_IS_EMPTY_is_refused_and_not_rounded_to_zero_percent` | **no** | yes (1577) |

Only the first is repairable on HEAD alone AND is the one the prior finding spelled out in full.
The third does not exist here at all and arrives with the merge, so "re-key it on HEAD" has no
referent — stated plainly rather than reported as two-of-three done.

**The defect.** The `same` leg was `_rerun_block()`, whose canonical arm is whatever
`THREE_ARM_PATH` holds today. It asserted nothing while the pinned baseline and the canonical run
happened to be the same file, and went red the moment a newer run was promoted — on a tree where
nothing was wrong. **Keyed to today's answer, not to the property.**

**The repair** hands the pinned baseline in AS the canonical run, so the case is constructed:

```python
same = _rerun_block(canonical=_load(DEPARTURE_BASELINE))["baseline_is_the_pages_current_run"]
```

*When the page's current run IS the control arm, the flag says so* — true under every promotion,
including the one that reddened the old spelling.

**Reproduced and proven** in a clean worktree cut from `HEAD c0be42c36`
(`/var/tmp/se-lane0-rekey-20260911`), one variable: `origin/main`'s
`docs/observability/value_cycle_ab_s1_three_arm.json` (`2026-09-10T14:04:08Z`, produced at
`9cf9d16ed`) copied over HEAD's (`2026-09-09T13:58:12Z`, `8b846013e`).

```
old spelling, promoted artefact   ->  FAILED   (assert False is True)
new spelling, promoted artefact   ->  3 passed (with its two siblings)
```

**R15, both legs, each mutation run and reverted** against
`generate_value_arms_data._departure_term_rerun`'s `baseline_is_the_pages_current_run`:

```
… else False)  -> FAILED  assert False is True    (the `same` leg fires)
… else True)   -> FAILED  assert True is False    (the `moved` leg fires)
restored       -> 1 passed
```

Neither leg is an equivalence. The `moved` leg is unchanged and was already correct; it is listed
because a repair to one leg of a two-leg control has to show the other leg still fires.

## 3. The promoted artefact explains ONE of the three reds, not three

The prior finding's §4 reads: *"The single cause is that the merge changes which run is
canonical, and it is neither side's code."* That is **too strong**, and the one-variable run above
refutes it.

On a clean HEAD with **only** the canonical artefact swapped for origin's:

```
test_a_control_arm_that_is_not_the_pages_current_run…   FAILED
test_the_withdrawn_sentence_is_kept_beside_the_reading… PASSED
```

The promoted artefact is *sufficient* for the control-arm red and *not* for the withdrawn-sentence
red. The third red cannot be attributed to it either, since that control does not exist at HEAD.
So there are at least two causes, and the withdrawn-sentence red is **not** explained by the
promotion — which is consistent with the same finding's §5 (*"it publishes to the reader a sentence
the feed's own withdrawal record names as withdrawn … the control refusing it is right"*) and
inconsistent with its own §4. **§5 is the one that survives.**

*Why §4 got it wrong, said against my own earlier pass:* §4 attributed by running the three in
clean HEAD, clean origin and merged, and reading "green, green, red" as one cause. Three green-red
tables with the same shape do not make one cause — the merged tree changes the producer, the feed
AND the canonical artefact at once, and **when more than one thing changed, the result cannot be
attributed.** The one-variable run is what separates them, and it took four minutes.

## 4. What is next, re-ordered by what §3 changes

1. **The withdrawn-sentence red is a producer/feed question, not a promotion question**, and it is
   the one genuinely holding the merge. It must be attributed on its own variable — merged
   producer against HEAD's feed, and HEAD's producer against the merged feed — before anyone
   decides whether the sentence or the control is wrong.
2. **`test_a_remedy_whose_OTHER_HALF_IS_EMPTY…` can only be graded on the merged tree**, since it
   exists on one side. It is not a "re-key on HEAD" item and should stop being listed as one.
3. The prior finding's items 1 (the sign blocker) and 3 (the bar drift, with the defaulted
   parameter removed) are untouched and still stand in that order.
4. **Then the merge relands.** The four non-feed resolutions are settled twice independently
   (`/var/tmp/lane0-resolve-20260911/`); the register resolution was re-derived this tick and the
   union is 33 instances / 7 BLOCKING, which `rederive_in` will confirm or correct at the gate.

## What I did NOT do

**I did not land the merge**, and I did not re-key any control inside a merge resolution. Both for
the prior finding's reason, which §3 strengthens rather than weakens: the withdrawn-sentence
control is now the only one of the three with no benign explanation, so landing the merge while
quieting it would be the clearest possible case of removing the evidence a refusal was earned.

**I did not touch `background/origin_reconcile.py`.** §1.
