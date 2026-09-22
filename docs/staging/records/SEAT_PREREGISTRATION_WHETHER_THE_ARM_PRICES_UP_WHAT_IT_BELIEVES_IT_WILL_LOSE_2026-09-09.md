**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — find where the renewal rule prices up the households it then loses) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — does the arm price UP the households it already believes it will lose?

**Written 2026-09-09, before the discriminating numbers were read.** What I had read when I wrote
this is listed below, to the field, so a reader can tell a prediction from a recital. Everything
under "predictions" was unknown to me at the time of writing.

Commissioned by the Lane 0 delivery item
`find-where-the-renewal-rule-prices-up-the-households-it-then-loses`, whose brief is:

> Find which household features `saas/` renewal pricing prices up, and whether the churn model it
> already prices against predicts the departure it is buying — a high churn AUC beside this is a
> maximiser working correctly on a one-sided objective, which `method_skill.reading` names and
> nothing has tested.

The established prior it follows from:
`SEAT_RESULT_THE_ESTIMANDS_INVERSION_IS_NOT_THE_TIE_MASS_IT_IS_THE_ARM_PRICING_UP_THE_CUSTOMERS_IT_LOST_2026-09-09.md`
— the cross stratum reads **0.2686** over 4,588 departure-against-survivor pairs, so in 73% of
those pairs the arm had given the DEPARTURE the higher margin, and the whole of the estimand's
distance from chance is that stratum.

---

## What was already in hand when this was written

Read before writing, from `docs/observability/value_cycle_ab_s1_three_arm_20260909.json`
(world digest `39a192ce04c1eda8`, producing commit `62334dc76`) and
`company/pricing/value_based_renewal.py`. **None of it is a prediction.**

- `belief_vs_outcome.discrimination_auc` = **0.6269578**, `auc_population` = 83 retained / 40 left,
  `scored_decisions` = 123 rows, each carrying `believed_p_retain`, `retained` and
  `chosen_margin_gbp_per_mwh`. `mean_believed_p_retain` 0.6913 against
  `realised_retention_rate` 0.6748, `calibration_error` 0.0165.
- `belief_vs_outcome.reading` already names the shape this item tests: *"Above 0.5 with a large
  `calibration_error` means the arm ranks customers correctly and misjudges the level."* It does
  **not** name the one-sided-objective reading, which is what this document is for.
- `decision_shape`: 214 priced, 64 declined, median chosen margin 20.0 GBP/MWh against a control
  margin of 2.0, `endpoint_at_ceiling` 151.
- `decide_margin` in `company/pricing/value_based_renewal.py` maximises
  `expected_value_gbp(margin, eac_mwh, cost_to_serve, p_retain, expected_periods)` over a candidate
  grid, with `p_leave` re-estimated per candidate by `enriched_churn_estimate`.
- The first ten rows of `scored_decisions` are visible in the artefact and I have read them; they
  are 10 of 123 and I have not computed any statistic over the file.

## The mechanism this predicts against, stated so it can lose

A per-customer expected-value maximiser scores `p_retain(m) × m × V × T − costs`. **If a household's
retention is low and flat in price at the top of the grid, there is little retention left to
protect, so the maximiser harvests.** If that is what is happening, the arm is not making an error
at all — it is optimising correctly against an objective that never charges it for the departure,
and the inversion is a property of the objective rather than of the estimate.

The rival explanation is that the belief is simply wrong in the direction that matters: the arm
prices up households it believes are STICKY, and the world takes them anyway. That would make the
inversion an estimation defect, repairable by a better churn model, and it would be refuted by a
churn AUC meaningfully above chance.

---

## Predictions

Over the 123 rows of `belief_vs_outcome.scored_decisions`, unless a row states otherwise.

| | prediction |
|---|---|
| **P1** | Spearman rank correlation between `believed_p_retain` and `chosen_margin_gbp_per_mwh` is **negative**, and |ρ| ≥ 0.30. The arm prices UP where it believes retention is low. |
| **P2** | Mean `believed_p_retain` is **lower** for the 40 departures than for the 83 survivors — this must hold, since AUC 0.627 > 0.5 already implies it, and it is filed as a consistency check, not a discovery. |
| **P3** | The **margin's own AUC against departure** — chosen margin as a predictor of leaving, over these 123 rows — is **above 0.5**, in 0.55–0.70. This is the belief_vs_outcome population's version of the cross-stratum 0.2686 and it should point the same way. |
| **P4** | **The mediation leg.** Within believed-`p_retain` strata (quartiles of the belief), the margin's AUC against departure falls toward 0.5 — I predict the pooled within-stratum AUC lands in 0.45–0.58, i.e. **most of P3 is the belief**, not something the belief cannot see. |
| **P5** | On a one-at-a-time sweep of `decide_margin` at real book inputs, the chosen margin is **monotonically non-increasing in `eac_kwh`** over the observed range — a bigger household has more volume at risk, so the maximiser protects it. I am least confident in this one. |
| **P6** | On the same sweep, chosen margin is **non-decreasing in `bill_shock_count`** — more prior shocks means a higher baseline p_leave, less retention to protect, and so a higher harvest. |
| **P7** | `expected_value_gbp` contains **no term charging the arm for a departure** — no CAC-to-replace, no book-level term, no continuation value forgone beyond the horizon it already truncates at. If P7 holds, the objective is one-sided as a matter of construction and no amount of churn-model accuracy fixes it. |

## What would refute the one-sided-objective reading

Any of: P1 comes back positive or near zero (the arm does not price against its own belief);
P3 comes back at or below 0.5 (the margin does not select departures in this population); or
P4 comes back at P3's own level (the belief mediates nothing, so the inversion is information the
churn model does not have and the finding is an estimation defect after all).

## What this cannot settle, stated in advance

- One world, one seed, 88 accounts on the estimand and 123 scored decisions here. **Direction, not
  magnitude.** The `belief_vs_outcome` population is not the fixed-horizon estimand's population
  (123 against 161, different matching rule), so no figure here bounds a figure there and I will
  not net them against each other.
- Decisions are clustered on accounts; nothing here is an account-level standard error.
- A sweep over `decide_margin` establishes what the RULE does at inputs I chose. It is a statement
  about the function, not about the book, and it will be labelled as such.
