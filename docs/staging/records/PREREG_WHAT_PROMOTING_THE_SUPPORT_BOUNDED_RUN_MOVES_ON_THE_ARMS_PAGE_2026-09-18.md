**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# What promoting the support-bounded run moves on the arms page

**Filed:** 2026-09-18, BEFORE running the publisher · **Claim id:**
`the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have`
**Grades:** `b329e702b` (the fix), `e15ccbe3d` (the structural prediction), `49f49dd8e` (the doors)
**The run:** `/var/tmp/value_cycle_ab_s1_three_arm_support_20260918.json`, world `39a192ce04c1eda8`,
producing commit `b329e702b`, `generated_at` 2026-09-18T05:43:40Z.

---

## Why this is pre-registered at all

The run's own numbers are already on disk and I have read them, so predicting *them* would be
filing a prediction after the answer. What is **not** yet known, and is what this registers, is
what the PUBLISHER does with them: which legs survive, which refuse, what the page ends up
asserting, and whether the four doors repaired in `49f49dd8e` stay green when the page gets more
honest. That is the measurement, and its answer is not in the artefact.

## The one thing already known, stated so it cannot be re-claimed as a prediction

`decision_population.same_priced_population.answer` is **`true`**, with
`net_refusals_of_renewals_the_other_arm_priced = 0`: value priced 104 / declined 3, level priced
107 / declined 3, and the whole 3-renewal gap is roster divergence. That is the drawn item's
"done means" for the run, and it is **read, not predicted**.

## P1 — the bounded legs withdraw rather than move

`e15ccbe3d` predicted this from a probe that bumped only `generated_at` on the published artefact:
`_seed_spreads(...).available` goes `False`, `_floor_admission(...).admitted` goes `False`,
`_staleness_caveat` fires, and `_legs_on_one_bar` republishes the refusal so **all three bounded
legs go unavailable together**. That probe was a stand-in. This is the real artefact, and the
prediction is now graded against it rather than against a copy with one field edited.

**I predict it holds unchanged.** The floor (`..._folded18_single_arm_20260917.json`,
2026-09-17T21:39:28Z) predates the run (2026-09-18T05:43:40Z), which is the only input the
staleness branch reads.

**What would refute it:** any bounded leg still stating a sign after the promotion.

## P2 — the selection residual reverses, and I cannot attribute it

| | published (09-10 run, commit `9cf9d16e`) | new run (commit `b329e702b`) |
|---|---|---|
| `level_gbp_per_mwh` | 20.00 | 41.00 |
| `value_advantage_gbp` | +16,792.24 | +4,579.23 |
| `level_advantage_gbp` | +17,124.87 | +252.21 |
| `selection_gbp` | **−332.64** | **+4,327.01** |
| `level_share_of_advantage` | 1.020 | 0.055 |

The published sentence — the level explains *all* of the advantage and the selection is worth less
than nothing — becomes its opposite. **This is not attributable to the support bound**, and I will
not publish it as if it were. Four commits touching the value arm landed between the two runs
(`e1895d6c8` departure cost, `27c7672f7`/`3088f8c71` the gas leg, `b329e702b` the frontier), the
level is *derived* from the value arm's own realised median and so moved 20.00 → 41.00 on its own,
and the book itself is a different size (2,037 → 2,824 renewals offered, 100 → 66 accounts priced).
Several things changed at once; the one-variable version has not been run.

**I predict the page must therefore state no attributed cause for the reversal.** If the publisher
emits a sentence crediting the arm fix with the flip, that is a defect this prereg is written to
catch, and I will fix it rather than ship it.

**What would refute the no-attribution stance:** a one-variable run — `b329e702b` with only the
support clamp reverted — returning the same `selection_gbp` sign as the new run. That is a 20-minute
leg and is NOT done here; until it is, the reversal is unattributed.

## P3 — the four doors repaired in `49f49dd8e` stay green

Those doors were keyed to the floor *admitting* the figure. This promotion is the first live case
where admission is refused, which is the case they were repaired for. **I predict they pass.** If
they red, the repair was keyed to the old answer after all and this is the run that proves it.

## P4 — `_later_runs_in_this_world` names the promoted file

`CURRENT_WORLD_THREE_ARM_PATH` stays pinned to `_20260908.json` (repointing it is a separate
decision with its own reverted history). So the guard should now name the newly promoted dated
copy as a later run in the same world. **I predict it fires and names `_20260918.json`.** A silent
pass would mean the guard does not see a promotion, which is what it exists for.

## What is NOT settled here, and stays owed

Re-running the folded-eighteen floor on the post-fix tree — 54 passes, ~18 hours. Until it runs the
page states no direction for the level leg or the selection leg, and the £4,327 above carries no
bound. A point estimate is not a finding.
