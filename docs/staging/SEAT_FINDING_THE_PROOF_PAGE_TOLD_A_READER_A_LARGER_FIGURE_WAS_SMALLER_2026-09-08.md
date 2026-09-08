# FINDING — the proof page told a reader a larger figure was smaller, and named a cause for a move that went the other way

**Severity:** BLOCKING · **Lane:** G_data_learning

**Found 2026-09-08 ~22:20Z, on the live `site/data/value_arms.json`, while preparing the promotion
of the 2026-09-08b value-arms run.** Fixed in the same turn. Not hypothetical and not a control gap:
this sentence was on the published surface.

## What was published

The headline of the value-arms proof page read, verbatim:

> IN THE WORLD AS IT IS NOW, the same comparison gives **£17,739**, measured 2026-09-08T00:19:54Z.
> That figure CLEARS the £1,522 this same contrast moves across 3 seed re-draws in this same world,
> the first bound this page has held that was measured where the figure was. **It is a SMALLER
> advantage than the £12,071 below, not a larger one: what moved is the floor, which fell further
> than the advantage did.**

£17,739 is **larger** than £12,071. Three separate claims, all wrong at once:

1. **The direction is inverted.** The figure is 47% larger than the one it is compared against.
2. **The correct reading is explicitly foreclosed** — "not a larger one" — so a reader who noticed
   the arithmetic was told the page had already considered and rejected it.
3. **A cause is attributed to a move that went the other way.** "What moved is the floor, which fell
   further than the advantage did" describes a collapse. The advantage rose.

Beside it, in the same block, `against_the_superseded_panel` read "That figure and this one were
measured in **DIFFERENT WORLDS**, on different dates, by different commits — more than one thing
changed". The canonical 2026-08-31 artefact carries **no `world_identity` at all**
(`value_cycle_ab_s1_three_arm_20260831.json` → `world_identity: None`), so the page could not
establish either world, and `_world_provenance` on the same page separately reports that run under
`runs_that_cannot_name_their_world`. One page, two blocks, contradicting each other about the same
artefact.

## Why it was reachable

Both sentences were **prose asserting a relationship between two artefacts**, written when that
relationship held, in a function that could see neither artefact's identity.

`_current_world_clause`'s tail was authored when the current-world advantage was £2,335.87 — the
comment at `generate_value_arms_data.py:4100` still records "the advantage itself collapsed from
£12,071 to £2,336 between worlds", which is the pair the sentence is true of. On 2026-09-08T04:10Z
`CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` were moved to the 2026-09-08 run
in `8e90037a5`. That landing moved the constants correctly, in one commit, with the pair rule
observed and a careful record of why. **It did not move the sentence that described what the
constants pointed at**, because nothing connected them.

This is the project's named class — *a published cause authored as prose goes stale beside the
measurement that refutes it* — and the £12,071 literal was one promotion away from being wrong
whatever happened, because `THREE_ARM_PATH`'s own documented convention (`AUC_RUN_HISTORY`'s
comment) is that **the newest run is PROMOTED onto it**.

## Two controls made it worse, not better

Both were pinned to today's answer, which is the shape CLAUDE.md names as exactly backwards:

- `site/test_the_baseline_comparison_reaches_the_reader.py` asserted the literal
  `"SMALLER advantage" in advantage_region`, with the honest intent "a bare 'clears' lets a reader
  take a collapse for a win". After `8e90037a5` that rung **required the page to call a larger
  figure smaller**, and the producer obliged it from a literal. A control that reds when the page
  starts telling the truth is not a control.
- `tests/tools/test_generate_value_arms_data.py` asserted `"12,071" in built["headline"]` and
  `"DIFFERENT WORLDS" in block["against_the_superseded_panel"]`. The first goes red on any
  promotion; the second **asserted the false half of the sentence**.

So the defect had a green suite around it, and the suite was part of the mechanism.

## What was done

Both sentences are now derived, and the defect is fixed as a class rather than as two instances.

- `_what_differs_between_two_runs` **counts** which of the world, the date and the producing commit
  differ between the two runs. An absent field is `unestablished` — never counted as differing
  (which would manufacture the attribution refusal) and never as matching (which would manufacture
  a one-variable claim). `differs_from_the_superseded_panel` publishes the count beside the sentence
  that reads it.
- `_against_the_superseded_panel` selects its attribution clause from that count: **≥2 differ** →
  "more than one thing changed, cannot be attributed to any one of them"; **exactly 1** → "this is
  the one-variable version, attributable to that alone only if nothing this page cannot see also
  moved"; **0 and all read** → "it is the SAME RUN … one figure printed twice, not a comparison";
  **0 read, some unreadable** → nothing established, nothing attributed. The director's own refusal
  ("may not be read as the company having got better or worse at choosing") moved to the invariant
  tail, so it now reaches the reader on **every** branch — it was previously reachable only on the
  branch the sentence was authored for.
- `_against_the_panels_figure` derives SMALLER / LARGER / SAME from the two figures, and **claims no
  cause at all**. The old cause was measured for one pair and cannot be true of every pair.
- Both controls rekeyed to the property: the door asserts the direction the feed's own two figures
  imply, and the producer suite asserts the subject run's own advantage reaches the headline.

`site/data/value_arms.json` regenerated. The headline now reads "It is a **LARGER** advantage than
the £12,071 below. WHY it differs is not stated here: more than one thing differs between the two
runs, so no single one of them can be credited with the move" — and the panel sentence names the
date and the commit as what differs, with the world listed as **unestablished**.

## Mutation evidence

Reachability proved by a poison round before the battery, because "survived" is ambiguous:

- **Poison A** — absence counted as a difference (`differ.append` in place of `unestablished`):
  **killed**, on the partition assert.
- **Poison B** — the literal direction restored (`direction = "SMALLER"`): **killed**, and it
  reproduces the published sentence exactly, which is the evidence the new control covers the real
  defect and not a paraphrase of it.

`test_the_superseded_panels_attribution_is_COUNTED_and_the_whole_partition_is_reachable` asserts all
four states of the count in **one** assert, because a counter stuck on "two or more" would satisfy
every per-branch assertion that mattered on the day it was written — which is how the original
survived.

Suites: `tests/tools/test_generate_value_arms_data.py` + `site/test_the_baseline_comparison_reaches_the_reader.py`
— **231 passed, 1 skipped**.

## What is next

This finding is a precondition of the promotion it was found during, not a substitute for it. Still
owed, and handed on:

1. **Promote the 2026-09-08b pair.** `value_cycle_ab_s1_three_arm_20260908b.json` (21:01:30Z,
   `b8bcbac2c`) carries `method_skill.fixed_horizon` and `method_skill.survivorship`; the canonical
   path still holds the 2026-08-31 run, so the page publishes neither estimand. The matching floor
   was in flight at 22:50Z (PID 2900491, `--redraw-mode all`, seeds 11111/22222/33333, drawing
   accounts from the 09-08b arms). **`_staleness_caveat` compares stamps only, so the floor must
   stamp after 21:01:30Z or the promotion must be abandoned rather than shipped with a caveat** —
   that is the reverted 2026-09-08 mistake on the canonical pair instead of the current-world one.
2. **Then decide the current-world constants.** Measured this turn: pointing `CURRENT_WORLD_*` at
   the same run as the canonical pair is now *honest* (the same-run branch says so in words) but
   makes the two-block structure a tautology. Leaving them at the 00:19:54Z run leaves an older
   same-world run leading the headline as "the world as it is now" while a newer one is the
   canonical figure — `composition.later_runs_in_this_world` does fire and name it, which is why
   this is a judgement and not a defect.
3. **Sweep for the same shape.** These were two instances found by promoting one artefact. Any
   published sentence naming a figure from an artefact a constant points at is the same hazard.
   `_current_world_clause` and `_composition_in_this_world` are now derived; nothing has established
   that they were the only two.
