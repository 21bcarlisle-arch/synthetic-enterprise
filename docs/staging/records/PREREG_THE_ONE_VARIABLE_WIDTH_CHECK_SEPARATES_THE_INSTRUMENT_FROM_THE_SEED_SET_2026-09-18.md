**Severity:** INFORMATIONAL · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# Pre-registration: is the 3.31x width difference the INSTRUMENT or the SEED SET?

**Filed:** 2026-09-18, BEFORE the run was launched. **Claim id:** `land-the-publisher-comment-repair-and-run-the-one-variable-width-check`

## The confound this run exists to break

Two families disagree about the WIDTH of the selection residual, and the published NEGATIVE sign
rests entirely on that width:

| family | seeds | instrument | n | mean GBP | sd GBP |
|---|---|---|---|---|---|
| `folded18_single_arm_20260917` (published) | 11111..555555 | **spliced, 3 commits** | 18 | -959.78 | 1631.80 |
| `20260910` | 11111..99999 | `4e7938f673` | 9 | -1749.47 | 1840.39 |
| `next12_20260917` | 3100001..3100012 | `a178b56d6` | 12 | -1069.48 | **5398.31** |

The twelve REPLICATE the level (109.69 GBP from the published mean, 0.07 of a sem) and REFUTE the
width (3.31x, F = 10.94 on df (11,17), two-sided p = 2.3e-05). Instrument and seed set are
**confounded**: the wide family is the only one with those twelve seeds AND the only one on
`a178b56d6`.

## The run

Seeds `3100001..3100012` at `4e7938f673` — the seed set held fixed, the instrument moved back.
Run in `/var/tmp/se-floorrun-20260910`, which is already checked out at `4e7938f673` and whose
`tools/run_value_cycle_ab.py` is byte-identical to that commit (md5 `9bd6cb02...`). That is the
same checkout the nine-seed `20260910` family was drawn in, so the instrument leg is not merely
the same commit but the same working checkout.

## THE PREDICTION, and I do not know the answer

**I predict the width is a property of the INSTRUMENT, not of the seed set** — that these twelve
seeds at `4e7938f673` will come back NARROW, near the 1840.39 of the nine rather than the 5398.31
of the twelve at `a178b56d6`.

**Why.** The seeds permute only the per-household elasticity assignment within one population.
Narrowness has already been reproduced across *three distinct seed blocks* (11111.., 111111..,
and the 20260910 nine) on the older instruments, and the pooled 18 stays at 1631.80. A seed block
being intrinsically 3x more dispersed would have to be a coincidence those three blocks all
avoided. An instrument change altering pricing sensitivity is the cheaper explanation.

**I may be wrong, and the shape that would make me wrong** is that the twelve seeds sit in a
different region of the elasticity draw space — a possibility I cannot rule out from the artefacts,
because no family before next12 used a 31xxxxx seed block.

## THE DECISION RULE, fixed now so the answer cannot choose it

Let `sd_X` be `selection_gbp_spread.stdev` of the new run.

- **`sd_X < 3000`** → prediction CONFIRMED. The width is the instrument's. The published sign's
  width is defensible on its own instrument, and next12's width is a property of `a178b56d6`.
- **`sd_X > 4000`** → prediction REFUTED. The width is the seed set's. The published NEGATIVE is
  contingent on its particular seed block, and `NOISE_FLOOR_PATH`'s sign must be withdrawn from
  the page, not merely caveated.
- **`3000 <= sd_X <= 4000`** → INDETERMINATE. Neither leg is stated; the page says so.

Formally I will also report the F-ratio against both parents: `sd_X` vs 5398.31 on df (11,11) —
the instrument leg — and `sd_X` vs 1840.39 on df (11,8) — the seed-set leg.

**What this run CANNOT settle.** It does not tell us which instrument is CORRECT. It tells us
which variable the width belongs to. Choosing between two instruments by their answers is the
thing the `NOISE_FLOOR_PATH` comment block already refuses to do, and this run does not license it.
