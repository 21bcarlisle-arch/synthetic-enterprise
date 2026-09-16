# SEAT FINDING — the advantage leg and the level SHARE are still one-run figures under nine-seed bounds, and the share crosses 100% when you ask the family

**Severity:** LATENT · **Lane:** A_strategy_governance

**Date:** 2026-09-10 (delivery seat, found while repairing the SELECTION leg's population on the
same page)

**Class:** `measurements_that_mirror`

---

## The short version

The selection leg was repaired today: its estimate is now the nine-seed family's mean and its
bound is that family's standard error, over the same nine. **The other two figures in the same
headline sentence were not**, and they have the identical shape.

| what a reader meets | population of the FIGURE | population of the BOUND beside it |
|---|---|---|
| `£17,444 MORE than flat rules` | ONE run | 9 seeds (`±£2,282`) |
| `the price level accounts for 98%` | ONE run (a ratio of two one-run figures) | none at all |
| ~~`£319` for the choosing~~ → `-£1,078` | 9 seeds ✅ | 9 seeds ✅ |

## The numbers, from `site/data/value_arms.json` at this landing

```
contrast              one run        9-seed mean    9-seed sd     9-seed sem
value_advantage_gbp   17,443.97      18,321.31      2,281.52      760.51
level_advantage_gbp   17,124.87      19,399.47      1,176.65      392.22
selection_gbp            319.10      -1,078.17      1,810.50      603.50   <- repaired today
```

## Two separate defects, and the second is the worse one

**1. The advantage leg is the same mix, and its verdict does not change.** `£17,443.97` is one
run; `±£2,282` is nine. Paired like with like the family's mean is `£18,321.31` against a
`£760.51` standard error — **24.1 standard errors from zero**, so the page says "MORE than flat
rules" either way. That is exactly why it would sit there unnoticed: the mix is invisible when it
does not flip an answer, and it is the same mix that WAS flipping one leg over.

**2. The level SHARE is a ratio of two one-run figures, and it crosses 100% when you ask the
family.** The page prints "the price level accounts for **98%** of the per-customer arm's
advantage", which is `17,124.87 / 17,443.97 = 0.9817`. The same ratio over the nine-seed means is
`19,399.47 / 18,321.31 = ` **`1.0589`** — the level leg is **106%** of the advantage, because the
selection leg is negative. Those are not two estimates of one quantity that happen to differ by
eight points. They are on opposite sides of the line a reader uses to decide whether the choosing
contributed anything: 98% reads as "almost all of it, and a sliver was the choosing"; 106% reads
as "all of it, and the choosing gave some back".

**Before dividing two numbers, say out loud what each one counts.** The numerator and the
denominator here are both one-run contrasts, so the ratio is at least internally consistent — but
it is published under a page whose other legs are now nine-seed figures, and it carries no bound
of its own in either population.

## Why this is LATENT and not BLOCKING

Nothing on the page currently states a wrong DIRECTION from either. The advantage leg's sign is
the same in both populations and clears by 24 standard errors; the share is withheld entirely
unless the advantage leg resolves (`_selection_sentence.share_clause` gates on
`_resolvable(advantage, advantage_spread)`). What is wrong is the pairing, and the 98%-versus-106%
gap is the evidence that the pairing is not cosmetic.

## What the repair is, and why it was not done in the same landing

The machinery exists: `generate_value_arms_data._leg_over_its_own_family` takes any contrast from
`_seed_spreads` and returns the estimate, the bound, the seed counts and the gate. Applying it to
`value_advantage_gbp` is the same shape as the selection leg.

It was held back for one reason: `_arm_vs_control_clause` and the share clause are the sentences
that decide whether the page names a winner AT ALL, and moving both legs' gates in one landing
would have made the selection leg's correction unattributable if anything moved. **When a result
moves and more than one thing changed, you cannot attribute it.** The selection leg was the drawn
work and the thesis; this is the same repair one leg over, on a leg whose answer is not in doubt.

**Prediction, filed before the work:** applying `_leg_over_its_own_family` to
`value_advantage_gbp` changes the rendered figure from `£17,444` to `£18,321` and the bound from
`±£2,282` to `±£761`, and does NOT change the stated direction. The share, recomputed over the
family, moves from `98%` to `106%` and therefore needs a sentence saying it can exceed 100% when
the selection leg is negative — a share above one is not a bug there, it is the finding.

## Where it is

* `tools/generate_value_arms_data.py` — `_arm_vs_control_clause` (the advantage leg's sentence),
  `_selection_sentence.share_clause` (the share), `_clears_its_floor` (the per-run deviation
  quoted beside a figure).
* `site/capabilities/index.html` — `#arms-headline`, and `#arms-composition` for the share census.
* `site/test_the_baseline_comparison_reaches_the_reader.py` —
  `test_the_rendered_selection_ESTIMATE_and_its_BOUND_are_over_the_SAME_seed_count` is the control
  to extend, not to copy: it is written over one contrast and the extension is a parametrisation.
