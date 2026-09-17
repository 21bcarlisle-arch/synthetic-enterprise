**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The published eighteen pools two value arms, and the sign it cannot state is stateable on one

**Claim:** `the-selection-leg-is-six-seeds-short-of-a-sign-and-its-point-estimate-is-negative`
**Pre-registered in:**
`SEAT_PREREGISTRATION_CAN_THE_SELECTION_LEG_FAMILY_BE_REFOLDED_LARGER_THAN_EIGHTEEN_FROM_THE_TREE_2026-09-17.md`
**Artefact:** `docs/observability/value_cycle_ab_s1_noise_floor_folded18_single_arm_20260917.json`

---

## The headline

`value_cycle_ab_s1_noise_floor_folded18_20260917.json` — the eighteen-seed family the
level-vs-selection split publishes — is folded from two runs whose **value arms are different code**.
Nine of its seeds were drawn on `c066c114`, nine on `9f0ab066`. The same nine seeds re-run on a tree
whose value arm is byte-identical to `9f0ab066` return a `selection_gbp` that is **£671.31 lower, on
every one of the nine, paired, at 20.4 sems from zero.**

Fold the eighteen so that every member sits on **one** value arm and the figure changes character:

| family | mean | stdev | sem | sems from zero | sign stateable | seeds_needed |
|---|---|---|---|---|---|---|
| published (two value arms) | **-624.13** | 1472.89 | 347.16 | 1.80 | **no** | 23 |
| single value arm (18 seeds) | **-959.78** | 1631.80 | 384.62 | **2.50** | **yes, negative** | 12 |

The claim this item is named for — *"six seeds short of a sign"* — is an artefact of the pool. On one
value arm the family is not six seeds short of anything: it needs 12 and holds 18, and it states a
**negative** sign today. `tools.fold_noise_floor_family` reaches the same number independently:
`sems from zero 2.495 / distinguishable from zero at 2 sems: True`.

## The decomposition, and it closes exactly

The item's WHY splits the eighteen at the book seam and finds the halves £908 apart, *"1.34 standard
errors of their difference and therefore itself unstateable, so pooling is NOT refuted"*. That seam
is the **run** seam: the book-less half is all of `20260909b`, the book-naming half is all of
`20260910b`. So the £908 is confounded, and the tree already held the artefact that separates it —
`value_cycle_ab_s1_noise_floor_20260910.json`, the *same nine seeds* re-drawn on a later tree.

Three measurements, all at world `39a192ce04c1eda8`, `mode=all`, clock `settled-realised`, level arm
£20.00/MWh:

| | seeds | producing commit | mean | sem |
|---|---|---|---|---|
| A (fold member) | 11111–99999 | `c066c114` | -1078.17 | 603.50 |
| R (replica) | 11111–99999 | `4e7938f6` | -1749.47 | 613.46 |
| B (fold member) | 111111–999999 | `9f0ab066` | -170.09 | 310.59 |

`git diff --name-only 9f0ab066 4e7938f6 -- simulation/ company/ saas/ tools/run_value_cycle_ab.py`
is **empty**: R's value arm is the same code as B's. The two commits are three minutes apart and
differ only in site, docs, tests and tooling. So R is B's value arm applied to A's seeds, and:

```
published gap   A - B  =  -908.08
  TREE step     A - R  =  +671.31   paired, same 9 seeds, stdev 98.87, sem 32.96 -> 20.4 sems
  SEED-SET      R - B  = -1579.38   common value arm, 2.30 sems
  tree + seedset       =  -908.08   reconstructs the gap exactly
```

**Both components are larger than the net and they point in opposite directions.** The £908 looked
like unstateable noise because a £671 deterministic tree step and a £1,579 seed-set difference nearly
cancelled. Neither is noise, and on a common value arm the two seed halves differ at **2.30 sems** —
above the bar the item used to declare them indistinguishable. The item's conclusion that *"pooling
is NOT refuted and the family must not be cut on this evidence"* does not survive: pooling **is**
refuted, on evidence that was already in `docs/observability/` and had not been paired.

## Why nothing caught it

`c21d9209e` refused the AUC fold four hours ago for exactly this class — *"pooling them would not
widen a noise family, it would average two operating points and publish the step between them as
redraw noise."* That refusal keys on the **level arm**: `level_gbp_per_mwh` 38.50/38.50/36.25 against
20.00, visible in one column.

Here the level arm agrees to **£4.27** across the same paired comparison while the value arm moves
**£671.31**. The step is entirely in the value arm, the level column looks identical, and the same
reasoning that refused the AUC fold sails straight past this one.

`fold_noise_floor_family` is not silent — it sets `producing_commit.commit = null` and says *"FOLDED
from 2 runs drawn by 2 distinct code tree(s)"*. But it **notes** the multi-tree provenance and
publishes the pooled spread anyway, and nothing keys on the note. It also cannot yet tell the benign
case from the defect: R+B is also "2 distinct code trees" and is *fine*, because the value arm is
identical. Commit identity is the wrong resolution for this question; the value-arm file set is the
right one.

## The twelve seeds in flight will not reach 24, and that is not a reason to stop them

`longjob-floor-next12-20260917` is pinned at `7da627b90`. Against `4e7938f6` that tree differs in
**18 simulation files** — including `simulation/customer_events.py`, `simulation/renewals.py`,
`simulation/svt_rates.py` and `tools/run_value_cycle_ab.py` — across 377 commits. So its twelve seeds
are **not poolable** with the published eighteen, nor with R or B. The unit's own description, *"take
the selection leg's book-named family to 24"*, is unreachable by folding.

It is still the right job to be running, for a reason the item does not give: it will be the **first
single-value-arm family of twelve drawn in one run**, and twelve is precisely the price of a sign on
the single-arm evidence above. It should be read on its own, not folded.

## Corrections to my own work in this turn, kept beside the claim

- I first reported the tree step as accounting for "-74% of the gap". That was wrong twice: the sign
  was inverted, and it compared A against R while the gap is A against B. The honest version is the
  decomposition above, which closes to the penny.
- I then over-corrected, recording that the paired step *"does not decompose the halves' gap"*
  because R sits on a third commit. The `git diff` over the value-arm paths refutes that caveat: R
  and B share the value arm, so it does decompose. Measuring beat both of my guesses.

## What the pre-registrations returned

- **Held.** *"The published eighteen is already the maximal legitimate fold."* The census of 16
  floor artefacts found **zero** additional foldable members — every other one fails on repeated
  seeds, a different `mode` (`only`/`except` probes), a different world digest, or a different level
  operating point. Nothing was omitted from the eighteen by accident.
- **Held.** *"Per-seed `selection_gbp` in `20260909b` and `20260910` will differ despite identical
  seeds, and materially against the family's spread."* They differ on all nine, by £588.63–£855.45
  against a family stdev of £1,472.89.
- **Not graded, and not gradeable this turn.** The item's own *"the refolded family will NOT state a
  sign at 24 and the negative point estimate will hold"* is a prediction about a 30-seed fold that
  the paragraph above shows cannot be built. Its point-estimate half holds and strengthens: every
  single-arm reading here is negative, and more negative than the published -624. Its
  sign half is **refuted at 18 on one arm** — the sign is stateable, and negative.
- **Spent premise.** `/var/tmp/value_cycle_ab_floor_with_auc_20260917.json` is byte-identical to
  `docs/observability/value_cycle_ab_s1_noise_floor_auc3_20260917.json`, landed in `ab71cf877`. The
  instruction to copy and commit it was already discharged by another route.

## What should happen next

1. **Do not fold `next12` into the eighteen when it lands.** Read it as its own twelve-seed
   single-arm family. This is the one that will go wrong quietly if nobody writes it down.
2. **Give `fold_noise_floor_family` a value-arm predicate.** It should refuse — or at minimum price —
   a fold whose members' `simulation/`, `company/`, `saas/` and `run_value_cycle_ab.py` bytes differ,
   and stay silent when only site/docs/tests moved. Commit identity is too coarse in both directions.
   The control must be keyed to the property (does the value arm differ?) and not to today's
   membership.
3. **Decide what the page publishes.** The published -624.13 with "no sign" is a mixture of two value
   arms; the single-arm -959.78 states a negative sign. Re-pointing the page is a publishing decision
   with a live figure on the other end, so it is left to a reviewable step rather than taken inside
   this finding — but the page currently understates what our own evidence supports, and the artefact
   it would read is landed beside this document.
