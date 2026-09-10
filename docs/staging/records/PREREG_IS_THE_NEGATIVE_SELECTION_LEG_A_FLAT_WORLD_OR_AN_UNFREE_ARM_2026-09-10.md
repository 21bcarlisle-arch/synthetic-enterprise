# PRE-REGISTRATION — is the −£335.40 selection leg a flat world, or an arm that could not speak?

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3
**Written:** 2026-09-10, by the delivery seat, before the third leg below was computed.
**Claim:** `separate-a-flat-world-from-an-unfree-arm-before-anything-is-widened-or-tuned`
**Artefact under test:** `docs/observability/value_cycle_ab_s1_three_arm_departure_20260909.json`
(world digest `39a192ce04c1eda8`, producing commit `e1895d6c8`).

---

## The question, and why it is not a matter of taste

`level_vs_selection` on the departure run publishes:

| field | value |
|---|---|
| `value_arm_net_gbp` | 164,680.47 |
| `level_arm_net_gbp` | 165,015.87 |
| `selection_gbp` | **−335.40** |
| `level_share_of_advantage` | 1.0200 |

Beside it, the same block's `how_to_read_this` asserts a cause:

> *"with a world whose households differ only by circumstance there is almost nothing for
> per-customer selection to select ON, and the level should carry it."*

That sentence is **unmeasured prose sitting next to measured numbers.** It names one of two
candidate causes and it has never been differenced against the other:

- **CAUSE A — a flat world.** Households do not differ in any way the arm could act on, so a
  per-customer view has nothing to add over a flat level. The remedy is a *world-fidelity*
  decision and it belongs to the director's baseline, blind to company results (R13).
- **CAUSE B — an arm that could not speak.** `bound_attribution` says **139 of 215 priced
  renewals (64.65%) had their margin set by a bound, not by anything about the customer** — 138
  by the lawful Ofgem cap, 1 by the churn model's support frontier. On those decisions the arm
  expressed no per-customer view because it was not allowed to. The remedy is a *company
  mechanism* question already named in
  `SEAT_FINDING_THE_RENEWAL_ARM_CANNOT_HEAR_A_HOUSEHOLD_IN_DISTRESS_AND_PRICES_THE_CRISIS_YEAR_HARDEST_2026-09-09.md`.

Deciding this wrong spends weeks in the wrong lane. Hence this file.

---

## THE SPLIT, NAMED BEFORE ANYTHING IS COMPUTED

The value arm's **215 priced renewals** partition, by `value_arm_log`'s own per-decision
`ceiling_bound` / `extrapolation_bound` flags as `bound_attribution` reads them, into exactly two
disjoint halves that exhaust the population:

- **FREE — 76 decisions** (`chosen_freely`), median margin **£35.00/MWh**.
- **BOUND — 139 decisions** (`decided_by_the_lawful_ceiling` 138 + `decided_by_the_model_support_bound` 1),
  median margin **£12.00/MWh**.

76 + 139 = 215. That is the split. Nothing below is allowed to redefine it.

---

## Leg 1 — the money leg. Already established as NOT COMPUTABLE, and this is a reading, not a prediction

Stated plainly so no reader takes its absence for an oversight. Before any arithmetic was run, the
artefact's schema was walked. The selection leg is a difference of two **whole-run totals**, and the
artefact carries, for the level arm, only the twelve scalars in its `level_arm` block plus
`level_arm_decision_shape`. There is **no per-account and no per-decision figure for the level arm
anywhere in the file.** `margin_movers` and `bound_attribution.realised_margin_movement` both
compare the value arm against the **control** arm, not against the level arm.

So Leg 1 cannot be run here. The result document must say what run could, and must say it
concretely rather than as an aspiration.

## Leg 2 — the floor. Also read before computing, and also not a prediction

`docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json` re-ran this three-arm A/B once
per seed over nine seeds with only the per-household elasticity assignment re-drawn, on the **same
world digest** `39a192ce04c1eda8`. It publishes `selection_gbp_spread` and
`selection_distinguishable_from_zero`. Those figures were read before this file was written and are
reproduced in the result. The result must state what they do to the question as posed.

## Leg 3 — THE BELIEF→PRICE CHANNEL. This is the real pre-registration

This is the one leg whose answer is not known as this is written.

`belief_vs_outcome.scored_decisions` publishes **124 per-decision records**, each carrying
`believed_p_retain`, `chosen_margin_gbp_per_mwh` and the realised `retained`. The artefact already
publishes `discrimination_auc = 0.6163` for the **belief** against realised retention (85 retained,
39 left) — i.e. the arm's belief *does* rank households better than chance.

That single published number already bears on Cause A: **a world with nothing to select on cannot
produce a belief that ranks who leaves.** What is NOT published, and what is computed for the first
time in the result, is whether that ranking survives the journey from belief to price:

1. **ρ** — Spearman rank correlation between `believed_p_retain` and `chosen_margin_gbp_per_mwh`
   over all 124 records.
2. **AUC(price)** — the area under the ROC of `chosen_margin_gbp_per_mwh` against realised
   `retained`, on the identical 124 records and the identical outcome the published
   `discrimination_auc = 0.6163` uses. Reported with its sign convention stated: a value **below**
   0.5 means a higher price associates with **leaving**, which is the direction the world should
   produce if the price reaches the household at all.

### The predictions

**P3a.** If Cause B is material, the price is a poor carrier of the belief, because on 64.65% of
priced decisions the price is the Ofgem cap — a function of the term's date and the account's fuel
mix, and not of that household. **I predict |ρ| < 0.35.**

**P3b.** For the same reason, the price should carry **less** of the retention information than the
belief does. **I predict |AUC(price) − 0.5| < 0.1163**, i.e. the price is strictly closer to
chance than the belief's 0.6163 is.

**What refutes this reading.** If ρ comes back strong (|ρ| > 0.6) **and** |AUC(price) − 0.5| ≥
0.1163, then the arm IS expressing its per-customer view in the price it charges, the bound is not
destroying the channel, and Cause B is weakened — leaving Cause A standing on the money leg's
silence rather than on this file's argument. That outcome is to be written up exactly as loudly as
the other one.

**What neither outcome licenses.** Leg 3 is measured on the **belief and the price**, not on the
**money**. It cannot, by construction, attribute a pound of the −£335.40 to either cause. It can
only say whether the mechanism Cause B names is present in this run. Any sentence in the result
that slides from "the channel is broken" to "therefore the £335.40 is Cause B" is a defect and must
be caught in review.

---

## The proxy this deliberately REFUSES, named in advance

There is an obvious shortcut: the bound-decided median margin is £12.00/MWh and the freely-chosen
median is £35.00/MWh, so one could threshold `chosen_margin_gbp_per_mwh` on the 124 published
records and call the low half "bound". **That is refused.** The lawful cap moves with each term's
own cap window — it is far higher through 2022–23 than in 2019 — so ceiling-decided margins are not
a contiguous low band, and a freely-chosen decision at a low margin exists by construction. A
threshold proxy for bound status would be wrong in both directions and would answer with a
confident number. The honest move is to record that the join needs **one field** — `ceiling_bound`
carried onto the per-decision records the artefact already publishes — and to name that as the
cheapest thing that would unblock it.

---

## Done means

The result names which cause the data supports, **or** names plainly that this artefact cannot
separate them and states what run could, with the producer fields and the seed count written down
as numbers rather than as "more".
