**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `find-where-the-renewal-rule-prices-up-the-households-it-then-loses`) · **Class:** measurements_that_mirror

# RESULT — the arm prices up SMALL households, and its own churn belief is most optimistic exactly where it prices highest

Graded against `docs/staging/records/SEAT_PREREGISTRATION_WHICH_HOUSEHOLDS_THE_RENEWAL_ARM_PRICES_UP_2026-09-09.md`,
landed at **`cf9fd0e37`** before any count below was read. Three of eight predictions were refuted
and they are the informative ones.

Subject: `company/pricing/value_based_renewal.decide_margin` over all 251 accounts of the book,
via `tools/couple_value_based_pricing.compare`. Artefact:
`docs/observability/inside_the_renewal_rule.json`. Producer: `tools/inside_the_renewal_rule.py`.

---

## The answer, in one paragraph

**The arm prices up small households** — the rank correlation between a household's consumption and
the margin the arm chooses for it is **−0.576** on 251 accounts, against a permutation null of
−0.124..0.124. **And the company's belief about departure is ordered almost perfectly by the price
the arm itself chose**: the correlation between the chosen margin and the belief error is
**−0.8167**, same null. The higher the arm prices, the more optimistic it is about being able to.
In the top fifth of the book by price position the company believes departure is 0.4399 where the
world would make it **0.9500**. That is the arm buying departures it cannot see, measured on its
own decision rather than inferred from the realised A/B.

**But it is NOT a defect about household size.** Hold the price position fixed — the top tercile,
84 accounts — and split it by consumption, and the belief error is −48.9pp for the small half
against −48.45pp for the large: a gap of **−0.45pp inside a −1.25..1.30 null**. Size matters only
because size is what the arm prices on. **The defect lives on the price axis.**

## What the arm charges, and who it charges it to

| reading | value | null | outside? |
|---|---:|---|---|
| chosen margin vs `eac_kwh` | **−0.5760** | −0.1243..0.1243 | yes |
| chosen margin vs `expected_cost_gbp_per_year` | +0.3983 | −0.1245..0.1219 | yes |
| chosen margin vs the world's `price_differential_vs_svt` | **+0.9686** | −0.1212..0.1252 | yes |

The last row matters before any of the others can be read: both sides are looking at the same
lever. The arm's margin and the world's price position move together almost one-for-one, so a
disagreement between the two beliefs is a disagreement about the RESPONSE and not two measurements
of different things.

**It is a real decision and not a constant.** 183 distinct margins over 251 accounts, IQR
£132.00/MWh, modal margin holding 9.2% of the book. This module's own subject failed that test on
2026-08-25 (two grid constants carrying 72% of the book), so it is checked first and every
correlation above is read in its light.

**Segment and credit risk were not predicted and are not graded.** They also cannot carry anything:
249 of 251 accounts are `resi` and 248 are `medium` credit risk. The book has no variation on those
axes to find.

## The dose-response, and the reading it is NOT

Equal-count quintiles of the world's price position, at the price the arm chose for each account:

| price differential (median) | company believes p_leave | world would p_leave | past the calibrated window |
|---:|---:|---:|---:|
| −0.6425 | 0.4329 | 0.0180 | 0 of 50 |
| −0.5071 | 0.4404 | 0.0178 | 0 of 50 |
| +0.2675 | 0.4490 | 0.1305 | 4 of 50 |
| +0.9712 | 0.4471 | 0.4074 | 36 of 50 |
| **+1.4064** | **0.4399** | **0.9500** | 50 of 51 |

The company's column spans 1.6pp across the whole book. The world's spans 93pp.

**That is not evidence the churn model ignores price, and publishing it as such would have been
this project's own recurring defect.** Every row sits at its own argmax: the arm picks the margin
maximising `p_retain(m) × m × volume`, and the first-order condition of that maximisation pins the
believed departure probability to roughly one value at every optimum. A flat company column is what
a CORRECTLY WORKING maximiser produces. These rows cannot distinguish the two readings, because the
price is not a free variable in them, and the artefact says so on its face
(`dose_response.why_the_company_column_is_nearly_flat_and_what_that_is_NOT`).

What the table DOES establish is the comparison across each row: **the arm carries ONE indifference
point (~0.44) for the entire book, and the world's response at that point is not one number.** It
is 0.018 at the bottom and 0.950 at the top. The arm's single indifference point is calibrated to
the world only in the middle of its own book.

**The discriminating test, named so it can be run:** sweep the margin for a FIXED household and
read both curves against each other. `value_based_renewal.CANDIDATE_MARGINS_GBP_PER_MWH`'s docstring
already prints that table for the company side alone. It is not built and this result does not rest
on it.

## The predictions, graded

| | prediction | outcome |
|---|---|---|
| **P1** | ρ(margin, `eac_kwh`) < −0.30 — the arm prices small households up | **CONFIRMED.** −0.5760, outside its null |
| **P2** | the rule discriminates: IQR > £30/MWh, modal share < 20% | **CONFIRMED.** £132.00, 9.2%, 183 distinct margins |
| **P3** | the arm understates departure on > 60% of accounts | **REFUTED, and by a long way.** It understates on 80 of 251 (31.9%) and the median belief error is **+31.0pp** — on the median account the company is PESSIMISTIC, not optimistic. The understatement is real but concentrated, not general |
| **P4** | ρ(belief error, chosen margin) < 0 | **CONFIRMED, and it is the headline.** −0.8167. Also −0.7975 on the pre-repair scale, so it is not an artefact of the bill-scale repair |
| **P5** | the belief still ranks the world: ρ > 0.50 | **REFUTED.** ρ = 0.2600 — outside its null (−0.1156..0.1324) so not nothing, but nowhere near ordering the book. Neither "a maximiser working correctly on a one-sided objective" (which needed a high rank correlation) nor "maximising noise" (which needed ρ ≤ 0.20). The middle case, and it was the one I had no name for |
| **P6** | ρ(price position, margin) > 0.70 | **CONFIRMED.** +0.9686 |
| **P7** | > half the book past the calibrated window, so magnitudes unquotable | **REFUTED.** 90 of 251 (35.9%), so the artefact publishes magnitudes rather than withholding them. The refusal machinery is built and armed at 50%; it simply did not fire |
| **P8** | with the probe repaired, the belief error is worse for small households at the same price position | **REFUTED.** −48.9pp small against −48.45pp large, gap −0.45pp, null −1.25..1.30. Size does not carry it |

**P3, P5 and P8 are the ones worth having.** P8's refutation is what turns "the arm mistreats small
households" into "the arm mistreats the price it chose", which is a different defect with a
different remedy. P5's refutation removes the frame the drawn item itself proposed — the item said
*"a high churn AUC beside this is a maximiser working correctly on a one-sided objective"*, and the
AUC is not high. P3 says the arm's optimism is not a general bias to be levelled away.

## The instrument was measuring the wrong household, and that is fixed

Found before the predictions were written and recorded there as prior knowledge, not as a result.

`simulation/customer_events.py:608` — the world the A/B actually runs — feels a price differential
against **the household's own annual bill**. `tools/couple_value_based_pricing.belief_versus_truth`
called the same curve with no bill, so it defaulted to `CALIBRATION_ANNUAL_BILL_GBP` = £1,700: every
row was the response of a market-average household wearing that household's price. It is the exact
defect `customer_events` was repaired for on 2026-08-27 ("a small flat and a large house at the same
percentage were modelled as facing the same money"), and the probe never got the repair.

It was not random with respect to what the probe is read for. **The arm selects on household size,
so the bias pointed straight at the population under study.**

What the repair moved, both scales published on every row so it stays one variable:

| | own bill | market average |
|---|---:|---:|
| median belief error | +31.0pp | +5.4pp |
| understates the world on | 31.9% | 46.6% |
| rows whose belief error changed at all | 112 of 251 | — |

249 of 251 accounts are now scored on their own bill; 2 are non-domestic and correctly keep the
market-average scale, because a domestic switching curve run on a 4 GWh site returns a ×599.6
multiplier (`bill_scale_for`). **The headline finding survives the repair in both directions**:
ρ(margin, belief error) is −0.8167 repaired and −0.7975 unrepaired.

`bill_scale_for` moved from `simulation/customer_events` to `simulation/market_switching_propensity`
in the same step — one implementation, living with the curve whose calibration it gates, rather than
a second copy in the tool.

## Controls

`tests/tools/test_inside_the_renewal_rule.py`, 16 controls. Poison round first; six mutations run,
six killed — but only after two of them survived and were chased down:

* **the tie-ranking mutation survived twice.** Replacing the shared average rank with the tie
  group's first position left all 16 green, then left them green again against a fixture built to
  catch it. Both fixtures were EQUIVALENCES: any labelling constant within a tie group and equally
  spaced between groups gives the same correlation, so 6-and-6 tie groups cannot separate the two
  rules. Unequal groups (2-8-2) can, and that is the leg that kills it. Recorded in the test rather
  than quietly fixed, because "survived" meant two different things on the way through.
* **the planted size-wedge was unfindable** in its first fixture, because I had made consumption
  and price position perfectly collinear — so the top differential tercile held only large
  households. That is the estimator being right: when price position determines size exactly, no
  band holds one fixed. A second draft then produced a −70.0pp gap sitting INSIDE a −70.0..70.0
  null, which is now its own control (`test_a_wide_gap_on_a_SHORT_band_is_correctly_reported_as_
  inside_its_own_null`) — it is what stops the real book's −0.45pp being read as a small effect
  rather than as no measurable effect.

No control is pinned to a measured correlation. A test asserting ρ = −0.576 would go red when the
book changes for a good reason and stay green if the statistic broke.

## What this cannot say

Nothing here is an outcome. These rows carry what the arm WOULD charge and what the world WOULD do
at that price, so **this cannot confirm or refute the realised A/B's 0.2686 cross stratum** — it
says what the rule does that would produce it. Both sides also descend from the same DESNZ switching
series, so every belief-versus-world figure measures whether the company's chain preserves the order
and level of a curve it shares with the world, which is weaker than a forecast against an unrelated
outcome and is the honest claim.

## What is next

1. **The defect now has a shape and a location: the arm's indifference point is one number where
   the world's is a curve.** The remedy is a pricing question and therefore the director's, not a
   constant for this seat to move (R12 — every figure here is a diagnostic).
2. **The fixed-household margin sweep**, which is the one cut that would separate "the model's
   price response is too flat" from "these rows are all at their own optimum". Cheap; not built.
3. **A second seed and a second world** for the realised A/B remains the open item from
   `SEAT_RESULT_THE_ESTIMANDS_INVERSION...`, and is untouched by this.
4. **35.9% of the book is scored past the world's calibrated window.** Magnitudes are publishable
   at that share and are published, but the top quintile is 50 of 51 beyond it — so the 0.9500 in
   the dose-response table is the world's last informed slope, not an observation.
