**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** —

# RESULT — the level leg's sign now reaches the reader, and the page had been summarising one leg of three

Class: measurements_that_mirror. RECORDED rather than BLOCKING: the defect is repaired and
landed, no published figure was wrong (the ones on the page were correct; two of three were
absent), and what is still owed is named at the foot of this document rather than left open here.

A published page stated a verdict on one leg of a three-leg advantage and was silent about the
other two. The leg it was silent about has a determined sign, and that sign reads against the
company.

**Lane 0 delivery**, claim
`the-level-leg-is-determined-but-the-page-still-reads-the-selection-leg-alone`.

---

## The premise, re-measured before starting

The item cited `c9bd2eae7` and the draw-time check said it was already an ancestor of
`origin/main`. It is — and the premise it carries is **not** spent. `c9bd2eae7` landed the
*reading* (the folded 18-seed family and the fold tool). What it explicitly left owed, in its own
commit message, is *"the page still reads the selection leg only"*. That is what this turn did.

One correction to the item's own words, recorded because it changes what the defect was:

> *"the page still tells a reader the split cannot be read at all"*

It does not, and had not for some days. `current_world.level_leg` already carried
`sign_determined: true` and the composed headline already said *"on this family the LEVEL is where
the measured advantage sits"*. **The defect was one block down and narrower than the item states,
and it is worse than the item states**: `_error_bar` — the block that owns the page's estimate, its
bar and its verdict sentence — read `selection_gbp` and nothing else.

## What was actually wrong

`level_advantage_gbp` has been in **every seed row of every noise floor this project has ever
written**. No summariser read it. So on the floor the live page is standing on right now:

| leg | family mean | sem | sems from zero | bar (t(n−1), n=9) | verdict | reached a sentence? |
|---|---|---|---|---|---|---|
| whole advantage | +£17,645.76 | 777.10 | 22.7 | 2.31 | POSITIVE | no |
| **price level** | **+£19,395.23** | **392.21** | **49.5** | 2.31 | **POSITIVE** | **no** |
| selection | −£1,749.47 | 613.46 | 2.9 | 2.31 | negative | yes |

The one leg that reached the reader was the one nearest its bar. The leg 49 standard errors from
zero published nothing at all.

**A leg nobody summarises is indistinguishable on the page from a leg with nothing in it** — and
the half the page was silent about is the half that reads against us: one flat margin at the same
price level, with **no per-customer inference in it anywhere**, beat the control by more than the
inference arm did. The enterprise value claimed here is the inference; what this book can
demonstrate is the price.

## What landed

- **`_legs_on_one_bar`** grades all three legs. One grader, one bar rule, one sentence
  generator — because *the contrast between the verdicts is the claim*, and a split verdict
  produced by two different rules would render exactly like a finding.
- **The rows come from `_seed_spreads`, not from a second derivation.** That function already
  reads every contrast out of the seed rows, already reconciles its selection reading against the
  spread the producer publishes, and already refuses all three legs on five separate grounds. A
  local derivation would have been a second implementation of the shape `CLAUDE.md` names by its
  cost — and the *permissive* one, since none of those five refusals would have come with it.
  A refusal here is `_seed_spreads`' refusal republished verbatim, asserted by a control.
- **`_selection_leg_reading` takes its subject as a parameter.** The selection leg's exact bytes
  are preserved (a door control is keyed to them).
- **`_the_verdicts_clause`** states the split in one sentence, and the against-us paragraph is
  **derived from the two signs** — a publish where the choosing turns positive drops it with
  nobody editing a string. Mutation-proven below.
- **The page renders a row per leg**, with `CANNOT BE CALLED` in amber, because a leg that
  rendered only when it resolved would make refusal and silence identical.
- `what_this_leg_is` for the level and selection legs is now written **once** and read by both
  blocks that describe them.

## Both branches are reachable on artefacts already in this repository

Measured, not constructed — a fabricated family would make every assertion unfalsifiable.

- `value_cycle_ab_s1_noise_floor.json` — **all three legs clear their own bar.**
- `value_cycle_ab_s1_noise_floor_20260910b.json` — **the legs SPLIT**: level POSITIVE, choosing
  cannot be called.
- and on the folded 18 (`..._folded18_20260917.json`, on `origin/main`): level **+63.0 sems**,
  choosing **1.80 against a 2.11 bar** — the exact reading the drawn item describes, produced by
  this code without it being told about that artefact.

## Five mutations, each firing on the control named for it

| mutation | control that reds |
|---|---|
| drop the level leg from the loop (the original defect, re-introduced) | `test_every_bounded_contrast_reaches_a_reading_of_its_own` |
| grade all three legs at the selection leg's family | `test_each_leg_is_graded_at_its_own_familys_bar_and_over_its_own_rows` |
| hardcode every verdict to unstateable | `test_the_level_leg_states_its_sign_because_its_own_family_determines_one` |
| soften the refusal into a per-leg reason | `test_a_floor_that_bounds_nothing_grades_no_leg_and_says_why` |
| flip the choosing positive | the against-us paragraph **drops itself** — proving it is derived |

## Still owed

- **`CURRENT_WORLD_NOISE_FLOOR_PATH` still points at the unfolded nine-seed floor.** Moving it to
  the folded 18 is a pointer move with the pairing rules at lines 184–271 to satisfy. It is
  *not* cosmetic: at n=18 the choosing leg's sign goes from **stateable negative** back to
  **cannot be called** (1.80 against 2.11), so the move makes the page *less* confident on the one
  leg where the larger family does not support the smaller one's verdict. That is the honest
  direction and it is the next item.
- The AUC floor `floor-auc-20260917` (seeds 1234567/2345678/3456789, disjoint from all 18) folds
  onto them for n=21 and would be the first family able to bound the AUC at all.
