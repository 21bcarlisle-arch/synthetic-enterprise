**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-nine-seed-floor-by-the-three-pointer-recipe-and-own-it-to-the-rendered-selection-leg`) · **Class:** measurements_that_mirror

# RESULT — the leg-conditioning column reaches the reader, and the deferral that held it back expired when the nine-seed floor landed

Graded against `docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_NINE_SEED_PAIR_MOVE_PUBLISHES_AND_WHICH_OF_ITS_LEGS_ARE_DECIDED_ALREADY_2026-09-09.md`,
landed at `3e85fefe3` **before the nine-seed floor existed**. R1–R7 are that document's, not mine.

## The premise, re-measured on real disk and git before any work

The drawn item names three pointers. Two are spent and the third is live — **the opposite of the
split the previous tick recorded**:

| # | Pointer | State this tick | Evidence |
|---|---|---|---|
| 1 | `three_arm_20260909c.json` → `THREE_ARM_PATH` | **LIVE — and it is the whole item** | canonical path held the `01:24:34Z` run (md5 `2d3819c2`, identical to `_20260909.json`) at HEAD *and* at `origin/main` |
| 2 | `noise_floor_20260909b.json` → `NOISE_FLOOR_PATH` | spent | canonical floor md5 `24da1d28`, byte-identical to the nine-seed artefact |
| 3 | `CURRENT_WORLD_NOISE_FLOOR_PATH` → the nine-seed floor | spent | constant already reads `..._20260909b.json` |

### Correction, beside the claim it corrects

`SEAT_RESULT_THE_SELECTION_LEG_READS_THE_NINE_SEED_FLOOR_AND_THE_PREREGS_IMPOSSIBLE_NARROWING_DROPPED_A_DIVISOR_2026-09-09.md`
graded pointer 1 **"not needed — `method_skill.fixed_horizon.leg_conditioning` is already `true` on
the canonical path's current run"**. That is false, and it was false when written:

```
origin/main:docs/observability/value_cycle_ab_s1_three_arm.json
    generated_at = 2026-09-09T01:24:34Z
    method_skill.fixed_horizon keys -> leg_conditioning ABSENT
origin/main:site/data/value_arms.json
    method_skill.fixed_horizon.leg_conditioning.available = false
    reason: "the run that produced this artefact predates the per-leg conditioning split"
```

The run that carries `leg_conditioning` is `_20260909c.json` (`13:58:12Z`). The dismissal read the
*selection leg* — which pointer 3 had genuinely fixed — and generalised it to the column, which is
fed by a different constant. That is the same two-feeds-one-page confusion the BLOCKING finding
`SEAT_FINDING_THE_NINE_SEED_FLOORS_STATED_PUBLISH_PATH_DOES_NOT_REACH_THE_LEG_THE_RUN_EXISTS_TO_SETTLE_2026-09-09.md`
exists to name, entering through the other door.

## The hazard that deferred this, and why it had expired

`SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`
declined this exact promote, and its reason was **measured, not argued**:

> `_seed_spreads(floor 06:57:00Z, run 14:00:00Z) -> available: False` — "Publishing it costs the
> page **every directional claim it makes**, in exchange for one column."

That was correct against the floor of the hour. `_staleness_caveat` refuses a spread older than the
point it bounds, and the `06:57:00Z` three-seed floor is older than the `13:58:12Z` run.

**The nine-seed floor is stamped `15:17:31Z` — later than the run.** The deferral's precondition was
a stamp comparison, and the thing it compared against moved. The hazard is evaluated rather than the
proxy re-read: probed in memory through `build()` before anything was copied, nothing written.

```
BASELINE (THREE_ARM_PATH = 01:24:34Z)      leg_conditioning False   contrast_bounds True  seeds 9
POINTER 1 (THREE_ARM_PATH <- 09-09c)       leg_conditioning TRUE    contrast_bounds True  seeds 9
```

This is the pre-registration's row **(c)** — which it recorded as a *mechanism probe whose numbers
are not publishable*, because it reached that state by hand-restamping the floor's `generated_at`.
Row (c)'s condition is now real and reached by a real run. The prereg's own sentence — *"a floor of
the same world stamped after 13:58:12Z restores the bounds"* — is what happened.

## The predictions, graded

- **R1 — HOLDS, and it was decided before the run.** The column renders **0 / 0 / 0 / 37 of 40,
  residue 3, one reason**, read from the artefact: three legs conditioned on survival seeing 0
  departures each of 40, `every_priced_decision_pounds_outcome` seeing 37 of 40 and
  `conditioned_on_survival: false`, residue 3 under the single reason
  `horizon_open_at_the_end_of_the_settled_book`. `priced_decisions_that_could_not_be_keyed` is 0.
- **R2 — HOLDS.** `contrast_bounds.available` true, `seeds: 9`, `world_measured_in`
  `39a192ce04c1eda8`.
- **R3 — HOLDS.** The reconciliation passes on the nine-seed floor; had it not, all three contrasts
  would have been withheld and there would be no page to land.
- **R4 — HOLDS, and its poison round is what makes this attributable.** `current_world.selection_leg`
  is **byte-unchanged** by this promote: still `resolved: null`, `n = 9`,
  `floor_generated_at 2026-09-09T15:17:31Z`. It reads `CURRENT_WORLD_*`, which did not move. Pointer
  1 moves the column and moves nothing else — the mirror image of the row-2 poison in the BLOCKING
  finding, and together the two prove the constants are independent in both directions rather than
  argued from their names.
- **R5 — vacuous, as it was pre-declared to be.** The leg states no direction. Not graded as a
  survival.
- **R6 — HOLDS.** No figure on the page loses its stated direction. `value_advantage_gbp` and
  `level_advantage_gbp` do not appear in the changed set at all.
- **R7 — HOLDS, and this is the one worth keeping.** The identical prediction one step earlier was
  **refuted 10-lost-3-gained**. This time the full leaf diff is: **4 lost, 30 gained, 19 changed**,
  and all four losses are withheld-placeholder fields being replaced by the content they were
  standing in for:

```
- method_skill.fixed_horizon.leg_conditioning.reason        ("...predates the per-leg conditioning split")
- method_skill.fixed_horizon.pair_strata.derived_because    ("...predates `method_skill...`")
- method_skill.fixed_horizon.pair_strata.strata.cross.reason
- method_skill.fixed_horizon.pair_strata.strata.cross.concordance_withheld = 0.2686355710549259
```

Of the 19 changed, 17 are provenance (`run_generated_at` `01:24:34Z`→`13:58:12Z`, producing commit
`62334dc76`→`8b846013e`, and the superseded-panel prose that quotes them). The two that are not:
`leg_conditioning.available` false→true, and `pair_strata.derived_by_identity_here` true→false.

**The nothing-lost claim is stated as a diff and not as a conviction, because its predecessor was
wrong.**

## `concordance_withheld` and `concordance` are the same float, and that is the check passing

`0.2686355710549259` moves from the withheld field to the published one **unchanged to sixteen
digits**. An identical number normally refutes a diagnosis; here it is the confirmation, and the
distinction is which two things agree. Before, the page derived the cross stratum's concordance
locally by the partition identity and withheld it for want of an interval. After, the run supplies
it from its own per-decision signs. Two independent routes to one quantity agreeing exactly is what
"the split is an identity" asserts — and the artefact carries its own `pair_strata` block
(`comparable_pairs`, `strata`, `estimand_concordance`), so the after-value is genuinely the run's
and not the fallback still running under a flipped flag.

## What this discharges

`SEAT_FINDING_THE_CROSS_STRATUMS_BOUNDED_BRANCH_STATED_A_BARE_NUMBER_AND_NO_ARTEFACT_ON_DISK_COULD_REACH_IT_2026-09-09.md`
is **LATENT no longer — it is discharged.** That finding says in its own words: *"the artefact
produced at 13:15Z today carries the old sentence, and `..._20260909c.json` is the re-run that
carries the repaired one"*, and severity LATENT *"because the live feed is on the identity fallback
and takes the withheld branch. It is one promotion away from mattering."* This is that promotion.
The live page now reads:

> The departure is carried by the 4,588 cross pairs, which read 0.2686 **against the 0.4105–0.5887
> a no-information signal reaches on this stratum's own 4,588 pairs**: in 73% of
> departure-against-survivor pairs the arm had given the DEPARTURE the higher margin.

The number reaches the reader with the interval its own pairs earn, on its own pair count. The
branch that had never executed anywhere in the tree now executes on the published feed.

## What is NOT claimed

The selection leg **still states no direction**, and this promote did not touch it. The item's
done-condition is met in its refusal arm, not its direction arm: the leg states a refusal that names
the nine-seed spread — 9 re-draws running −3,036.25 to +1,260.93, 5 of 9 clearing the bound, family
on both sides of zero. That was already true before this turn and is unchanged by it. **What this
turn adds is the column, not the direction.**

Nothing here licenses reading the restored `contrast_bounds` as a stronger result: it is a nine-point
sample of a quantity whose sign is not established, and `n` sits beside every spread it publishes.
