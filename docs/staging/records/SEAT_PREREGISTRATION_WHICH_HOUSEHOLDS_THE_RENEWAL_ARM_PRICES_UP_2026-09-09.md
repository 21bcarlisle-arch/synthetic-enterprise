**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `find-where-the-renewal-rule-prices-up-the-households-it-then-loses`) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — which households the value arm prices up, and whether its own churn model can see the departure it is buying

Written **before** any of the counts below were read. The instrument runs in 2.4 seconds, so the
only thing that makes these predictions worth anything is that they are on disk first.

The item this discharges is the Lane 0 direction drawn 2026-09-09, which follows from
`docs/staging/SEAT_RESULT_THE_ESTIMANDS_INVERSION_IS_NOT_THE_TIE_MASS_IT_IS_THE_ARM_PRICING_UP_THE_CUSTOMERS_IT_LOST_2026-09-09.md`:
the value arm gave the DEPARTURE the higher margin in 73% of departure-against-survivor pairs
(cross stratum 0.2686 over 4,588 pairs). That is attributed to the arm and not to the instrument.
Nobody has looked inside the rule.

---

## The instrument, and why it is not the A/B

`tools/couple_value_based_pricing.generate()` reprices the **whole book** — 251 accounts, 2.4s —
through `company/pricing/value_based_renewal.decide_margin`, the same function the A/B's arm calls,
and publishes per account: the chosen margin, the household's observable features, and both sides
of the price response.

It is **not** the realised A/B and cannot replace it: it reports what the arm would DECIDE, never
what it would earn, and scoring an arm on the expected value it maximises is R15's tautology with
money in it. What it is good for is the question actually drawn — *which households* — because it
has 251 rows where the A/B's cross stratum has 37 signals.

## What each column counts, said before it is used

| column | what it actually is |
|---|---|
| `value_margin_gbp_per_mwh` | the arm's argmax over the £0.25 lattice, per account |
| `implied_bill_change_pct` | **NOT a bill change.** `100 × (value_margin − flat_margin) / avg_rate` — a change in the UNIT RATE. The name is wrong and this document does not use it as a bill figure |
| `price_differential_vs_svt` | the WORLD's key: the offered unit rate against the published SVT for that term start |
| `company_believes_p_leave` | `enriched_churn_estimate(current_rate, offered_rate, tenure, eac, segment)` at the arm's own chosen price |
| `world_would_p_leave` | the world's base churn scaled by `churn_position_multiplier(differential)` |
| `belief_error_pp` | `100 × (believed − world)`. Negative = the company understates departure |

## The defect in the instrument, found before these predictions and stated as prior knowledge

`simulation/customer_events.py:608` — the world the A/B actually ran — feels the differential
against **the household's own annual bill**:

```python
_price_response = churn_position_multiplier(
    felt, annual_bill_gbp=_bill_scale_for(_segment, _annual_bill_gbp(...)))
```

`tools/couple_value_based_pricing.belief_versus_truth` (line 549) calls the same curve with **no
bill at all**, so it defaults to `CALIBRATION_ANNUAL_BILL_GBP = 1700.0` — one market-average bill
for every household. That is precisely the defect `customer_events` was repaired for on
2026-08-27 ("a small flat and a large house at the same percentage were modelled as facing the
same money"), and the probe never got the repair.

This is **not** a prediction, it is a reading of two call sites, and it matters here for a reason
that is not general: if the arm's selection is concentrated by household SIZE, then this bias is
aimed at exactly the population under study, and its `world_would_p_leave` is the response of a
£1,700 household wearing this household's price. So the fix is a precondition of the measurement,
not a by-product of it, and both the before and the after are reported below.

---

## The predictions

Each names its own falsifier. Spearman throughout, on the accounts the probe scored.

| | prediction | falsified by |
|---|---|---|
| **P1** | The arm prices **small** consumption up: ρ(`value_margin`, `eac_kwh`) < −0.30 | ρ ≥ 0, or \|ρ\| < 0.30 — in which case the arm's selection is not on size and P8's mechanism is dead |
| **P2** | The rule genuinely discriminates rather than landing on a constant: IQR of `value_margin` > £30/MWh, and the modal margin holds < 20% of the book | a narrow IQR — the "decision" would be a constant read back, which this module's own grid docstring says it has been before |
| **P3** | The arm systematically **understates** departure at its own chosen price: `belief_error_pp` < 0 for more than 60% of scored accounts | a majority at or above zero |
| **P4** | And the understatement **grows with the price it chose**: ρ(`belief_error_pp`, `value_margin`) < 0 | ρ ≥ 0 |
| **P5** | The belief still **ranks**: ρ(`company_believes_p_leave`, `world_would_p_leave`) > 0.50. The failure is level, not order — *a maximiser working correctly on a one-sided objective* | ρ ≤ 0.20, which would mean the arm is maximising noise and the whole rule, not its calibration, is the defect |
| **P6** | The world reads the arm's margin almost directly: ρ(`price_differential_vs_svt`, `value_margin`) > 0.70 | a weak correlation — the two sides would not be looking at the same lever at all |
| **P7** | More than half of scored accounts carry `world_curve_beyond_calibration: true`, so the **size** of every belief error here is extrapolated and only its **direction** is established | fewer than half — the magnitudes would then be inside the evidence and could be quoted |
| **P8** | **The mechanism.** With the probe repaired to pass the household's own bill, the belief error gets WORSE (more negative) for small households relative to large ones: within the top tercile of `price_differential_vs_svt`, median `belief_error_pp` is more negative in the bottom `eac_kwh` half than the top half | the two halves are equal or reversed. Then size is not the axis and P1's correlation, if it held, buys nothing |

**What P8 is really asking.** The world converts a percentage differential into POUNDS before it
responds. The company's rate model keys on the percentage. For a household whose bill is small,
a large £/MWh margin is a small number of pounds — so the company is relaxed — while the world,
scoring the same household after the repair, sees a smaller absolute shortfall too. The prediction
is therefore that the repair **narrows** the gap for small households and the pre-repair probe was
overstating the world's response for them. If P8 falls the other way, the arm's exposure is worse
than the probe has been saying, not better.

**One variable at a time.** P1–P7 are reported on the probe AS IT STANDS, and again after the
repair. Nothing else in the probe is touched in the same step: the arm, the grid, the ceiling and
the book are all as they were at `b01c77d16`.

## What was NOT predicted, and is reported whichever way it falls

Which `segment` and which `credit_risk` the arm prices up. I have no mechanism to predict either,
so they are read out as a table and not graded.

## What done means for the drawn item

The item states no exit test, so this is it. Done is: a landed instrument that names, over the
whole 251-account book, (a) which observable household features the arm prices up and how
strongly, (b) whether the company's churn model at the arm's own chosen price ranks and levels the
world's departure probability, with the extrapolation bound on the page rather than in a footnote,
and (c) the repaired probe, so the world side is the world's response to THIS household. Controls
that can fail, poison round first.

**Not in scope and stated so:** changing the arm. A diagnostic never becomes a target (R12), and a
rule that is wrong in a nameable direction is a finding for the director, not a constant for me to
move.
