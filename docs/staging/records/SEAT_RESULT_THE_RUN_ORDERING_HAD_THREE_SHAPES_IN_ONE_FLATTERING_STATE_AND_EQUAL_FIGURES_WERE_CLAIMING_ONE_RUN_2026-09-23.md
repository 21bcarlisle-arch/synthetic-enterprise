**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the run ordering held three shapes in one flattering state, and equal figures were being read as one run

*Lane 0 delivery, 2026-09-23. Drawn item: `publish-the-corrected-one-book-baseline-comparison`.
Pre-registration: `docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_THREE_STATE_RUN_ORDERING_WILL_REACH_2026-09-23.md`,
filed before the code existed and before any artefact pair was read for its stamps.*

## What this increment is, and what it is not

`b36b9cc3d` landed the measurement this item asked for — the floor drawn against the corrected arm
is admissible on the strong rule, the bounded reading is restored, and this book cannot settle the
selection sign by a factor of 436. It did not land the publish, and it named the one thing in the
way: **`is_the_later_run` is a two-valued flag over a three-valued question**, so the route that
points both panel constants at the corrected run publishes a contradiction. That is what this
increment removes. **It does not take the publish**; moving `CURRENT_WORLD_THREE_ARM_PATH` is the
step after, and both routes to it are already measured at 3 doors red and 7 doors red.

## The defect, and why the tie is live rather than hypothetical

```python
is_the_later_run = not (current_at and superseded_at and current_at < superseded_at)
```

`True` on that line meant any of **genuinely later**, **the same instant**, or **a stamp that could
not be read**. Only the first is what the field's name says, and the strict `<` puts the other two
in the branch that licences a currency claim — the flattering reading in both cases.

The tie is not a thought experiment. `756a86272` promoted the corrected 09-18 book onto the
canonical path, so **two different files on this disk carry one stamp**:

| file | `generated_at` | `producing_commit` |
|---|---|---|
| `value_cycle_ab_s1_three_arm.json` | 2026-09-18T05:43:40Z | `b329e702b` |
| `value_cycle_ab_s1_three_arm_20260918.json` | 2026-09-18T05:43:40Z | `b329e702b` |

P1 **holds**, and holds in the form predicted: the tie is drivable from two distinct files, so the
control is not proving its own fixture. The fourth state, `unstated`, is **not** reachable from any
three-arm artefact on disk — every one of the thirteen carries a stamp — but it *is* reachable in
production, because `_current_world_contrast`'s `superseded_run` parameter defaults to `None`. That
is a narrowing of P1 as written and it is recorded rather than glossed: the state is real, the route
to it is the producer's own signature and not an artefact.

## The second defect, which the pre-registration predicted and which was not in the item

P3 **holds**. `_against_the_panels_figure`'s equal branch said

> "It is the SAME advantage as the £X below — the two panels are one run's figure printed twice,
> not two measurements to compare."

on `point == old` **alone**. That is an assertion about run IDENTITY read off two floats. Two
genuinely different runs that agree on the advantage is the state this page enters the moment the
floor stops moving, and it is the strongest evidence the page could carry — a figure that held
across two draws. The sentence deleted it and told the reader there was nothing to compare. Two
shapes, one state, and nothing in the tree refused it.

## What was built

* `_how_the_two_runs_order(current_at, superseded_at)` → four states: `later`, `earlier`,
  `same_stamp`, `unstated`. `is_the_later_run` is **derived** from it and is now three-valued:
  `True` only on `later`, `False` only on `earlier`, `None` wherever the stamps do not order.
* `run_ordering` and `how_the_two_runs_order` published on **every** branch. Previously three of
  the four states published nothing about the ordering at all — `why_the_headline_omits_it` is
  `None` wherever the headline is not omitted — so a reader had one unexplained boolean.
* `why_the_headline_omits_it` retested as `is not False`, not truthiness. A falsy test would have
  put "THIS RUN IS NOT THE LATER OF THE TWO" on the tie and on the unread stamp: a withdrawal
  sentence on two states that withdraw nothing, which is the same class of defect as the flag.
* `_against_the_panels_figure`'s equal branch keyed to `run_ordering` rather than to arithmetic,
  with three sentences — held-across-two-runs, printed-twice, and not-established.

**The tie does NOT take the superseded-run withdrawal, and that is what makes this a split rather
than a widening.** "It is not the later of the two this page carries" is *false* of a run beside
its own stamp — our run would not be superseded, it would be the other panel. Publishing that
sentence on the tie replaces a wrong flag with a wrong sentence, which is not a repair.

## What the controls hold, and what they caught

`test_the_two_runs_ordering_has_a_state_for_every_shape_two_stamps_can_take` is one control over
the whole partition, **keyed by SHAPE and asserting DISTINCTNESS** — because a partition control
asserting N states over N+1 shapes is blind to exactly the collapse being repaired. It asserts four
shapes reach four distinct states *and* four distinct sentences, that `True` is reachable only from
the shape that earns it, and that the tie keeps the verdicts the later branch keeps.

`test_two_runs_that_agree_on_the_advantage_are_not_called_one_run_printed_twice` moves **only**
`run_ordering` across three legs with both figures identical, so the sentence is attributable to
the ordering and nothing else.

**The control went red on the producer's own first draft**, and the fix was in the producer. My
first two-runs sentence read "two runs agreeing is *not* one run printed twice" — the phrase
negated rather than absent. A reader skimming takes the phrase and not the "not" in front of it,
which is how a wrong reading survives the repair written to remove it. The sentence was rewritten
to say what held; the assertion was not weakened to admit the negation.

**Three mutations, each redding the leg written for it, each reverted and the tree verified
byte-clean against a pristine copy afterwards:** the tie answering `True`; the equal branch pinning
`RUN_STAMPS_ARE_EQUAL` instead of reading the payload; `why_the_headline_omits_it` back on
truthiness.

## The pointer census refused the new sentences, and registering them would have been the wrong door

The first draft of `_how_the_two_runs_order`'s four sentences said "the panel below". The full run
came back **318 passed, 1 failed**, and the failure was
`test_every_untied_here_relative_literal_has_a_recipe_that_drives_its_branch` naming
`_how_the_two_runs_order` as a symbol owning an untied here-relative pointer that no recipe drives.

Adding a `_RECIPES` row and a `_REFERENTS` row was the obvious move and it was the wrong one.
**This field has no door yet.** "Below" would have been a direction about a layout nobody has
built, registered against a render site that does not exist — the census would then have judged the
claim green for as long as the referent was also unrendered. A stamp identifies the other run from
the payload alone and cannot rot when the page is laid out, so all four sentences name the run by
its stamp and the symbol left the here-relative vocabulary entirely. Same repair as
`_renewal_stratification` and `_skill_sample_size_explanation` took in September, reached **before**
the sentence was ever published rather than after.

## What has a reader and what does not — stated, not implied

`run_ordering` **is production-reached**: `_against_the_panels_figure` consumes it and that sentence
renders in `#arms-headline`, so the tie and the two-runs-agreeing states reach a reader today.
`how_the_two_runs_order` is **payload-only — no door renders it yet.** That is said here rather
than left for someone to discover: it is the field the next increment's door answers the repeated-
figure refusal with, and until that door exists it is evidence in the feed and not on the page.

## The predictions, scored

| | prediction | outcome |
|---|---|---|
| P1 | all four states reachable; the tie from two different files | **held**, with `unstated` reachable from the producer's signature rather than from any artefact — recorded, not glossed |
| P2 | the live feed today is `earlier`, and the new field agrees with the published `false` | **held** — `run_ordering: earlier`, `is_the_later_run: False`, against `site/data/value_arms.json`'s `is_the_later_run: false` |
| P3 | the equal branch infers run identity from arithmetic and nothing refuses it | **held** |
| P4 | no site door rung changes colour | **held** — every reader of the flag gates on `is False` or `is not False`, so moving the tie and the unread stamp from `True` to `None` cannot move either; and `site/data/value_arms.json` is deliberately not regenerated in this increment, so the doors read the same bytes they read before it |

One prediction I did **not** register and should have: that the pointer census would refuse a new
symbol carrying a new here-relative phrase. It did, on the first full run, and it cost a cycle. The
census is doing its job; the omission is mine, and the generalisable form is that **any new
producer symbol whose sentence contains an above/below word owes a census row before it owes a
test** — recorded here rather than filed as a rule, because it is one instance.

P2 is the one that matters for trust: **no published verdict moved.** This split a state; it did
not change an answer.

## What is next, and it is the publish

The reason the first publish route published a contradiction is gone. What remains before
`CURRENT_WORLD_THREE_ARM_PATH` can move onto the corrected run is the three doors
`b36b9cc3d` measured — led by
`test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved`, which
refuses a page rendering the selection figure twice with nothing telling a reader which panel a
repeated figure belongs to. That refusal is **correct**, and `how_the_two_runs_order` is now the
field a renderer can answer it with.

---

## POSTSCRIPT — this increment was written twice, because the first landing never reached main

*Added 2026-09-23 06:2x UTC, Lane 0, under `give-the-repeated-figure-refusal-the-door-the-ordering-now-answers-it-with`.*

Everything above was true of `ad03d5725`, which **gated green (rc=0, 920 passed) and then never
became an ancestor of `main`.** It survives only as `refs/preserved/run-ordering-three-state/ad03d5725`.
Its promotion was refused by path contention, retried on a re-gated merge base, and the retry was
SIGKILLed at its bounded tick's teardown (`seat-executor-log.md`, 04:06 and 04:35 UTC). A later tick
holding the same claim moved on to a different subject, so the recovery was owned by nobody.

**The successor item was drawn on the assumption the producer already carried the field.** It read:
*"`run_ordering` now reaches a reader ... `how_the_two_runs_order` is payload-only and no door
renders it ... the door is the only missing half."* On the shared tree neither symbol existed at all
— `grep` over every `.py` and `.html` returned zero — and HEAD still carried the original
`is_the_later_run = not (current_at and superseded_at and current_at < superseded_at)` at line 14065.
Building the door first would have rendered a field that was not produced.

Two things are generalisable, and both are about **where a claim's evidence lives**:

1. **`git for-each-ref --contains`, not `git branch --contains`.** A gated commit parked on a
   `refs/preserved/` ref is invisible to a branch query, so "this landed" and "this exists" read the
   same. The receipt in the commit message says `gate-rc: 0` and that is a statement about a *tree
   that was gated*, never about `main`.
2. **A bounded tick cannot own a multi-step promotion.** The gate plus the promote exceeded the
   tick, twice, and the work was complete and correct each time. What was missing was not effort but
   a place for the half-finished promotion to be recorded as *owed*.

### The contention that refused it was a REVERT wearing another lane's clothes

The path the promotion could not take was `tests/tools/test_generate_value_arms_data.py`. In the
shared tree that file was `MM` — which reads as another lane's live work, and is the reading that
makes waiting look right. It was not. Its working copy was stamped **2026-09-22T10:31Z** while the
last commit to its own path was **864bc1e15 at 2026-09-23T03:17Z** — seventeen hours *older* than
the landing it sat on top of, and **1,771 lines shorter**. Landing it by pathspec would have
reverted the ceiling repair. `isolate_hunks` separates hunks by author and could not have caught
this, because there was no rival author: the file predated its own landing.

This increment was therefore landed with `surgical_land --content`, from bytes built outside the
repo as `HEAD` + the recovered additions, so the stale working copy was never read and never swept.
The stale copy is **still stale on the shared tree** and is left that way deliberately: the index
holds a third revision of it, so `refresh_to_head` there is a separate judgement with its own
evidence to gather, not a tail-end of this one.

### What is re-verified on the new base rather than inherited

`ad03d5725`'s green is not evidence about `main` as it stands now — origin/main gained 340 lines in
`tools/generate_value_arms_data.py` from the ceiling repair after that commit's base. So the two
controls were re-run against the recovered producer on an extract of current `HEAD`, and both were
re-mutated rather than trusted:

| mutation | leg that fired |
|---|---|
| tie returns `is_the_later_run: True` (the original defect restored) | *"a run compared against a panel carrying its own stamp claims to be the LATER of the two"* — `assert True is None` |
| `unstated` returns `same_stamp` (two shapes, one state) | the **distinctness** leg — `dict_values(['later','earlier','same_stamp','same_stamp'])` against `len(...) == 4` |

The second is the one worth naming: the control asserts the four states are *distinct*, not merely
that four calls return something. A partition control that counts states rather than comparing them
is blind to exactly the collapse this whole increment exists to remove.

**The door is still not built.** `how_the_two_runs_order` reaches the payload and no render site
reads it, which is the state this record's last section describes — unchanged, and now true of `main`
rather than of a preserved ref.
