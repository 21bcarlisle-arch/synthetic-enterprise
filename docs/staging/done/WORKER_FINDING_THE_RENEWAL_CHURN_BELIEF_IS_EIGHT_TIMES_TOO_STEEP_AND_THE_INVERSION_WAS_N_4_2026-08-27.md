# The renewal churn belief is 7.8x too steep on 478 renewals, and the inversion was n=4

**Severity:** LATENT · **Lane:** B_commercial
**Date:** 2026-08-27. **Author:** the delivery seat, Lane 0 direction
*"grade the renewal churn belief over the whole book"*.
**Instrument:** `tools/grade_renewal_churn_belief.py` (new). **Artefact:**
`docs/observability/renewal_churn_belief_grade.json`. **R15:**
`tests/tools/test_grade_renewal_churn_belief.py`, 18 tests, every verdict given a fixture on
which it comes out the other way.

## THE BOOK THIS RAN ON, named before anything is claimed about it

`docs/reports/run_output_latest.json` = `run_output_c50a99449_20260827T110902Z.json`, the
full-window auto-process run at git `c50a99449`, finished 2026-08-27T11:18Z, net £152,114.
`renewal_margin_arm` defaults to `flat_rules` (`company/policy/decision_policy.py:85`) and this
run carries no `value_arm_log`, so it is the **CONTROL** book.

| | |
|---|---|
| renewals the world rolled | **478** |
| billing accounts behind them | **157** |
| window | 2016-12-31 .. 2025-06-06 |
| churned / retained | 37 / 441 |
| beliefs recovered on the model's lattice | 478 of 478 (100%) |

The A/B graded **25**. The ladder's common population was **22**. This is 19x either, and it is
the same world, the same seeds and the same decade.

## THE ANSWER, in one sentence

**The inversion is not real — it was n=4 and n=11 in a different belief's bucket table; on 478
renewals the belief's ordering is correct, its ranking power is close to nil (AUC 0.5586 against
an oracle ceiling of 0.8109), and its error is a DOSE error: `build_churn_risk` moves 3.0
percentage points of churn per bill shock where the world delivers 0.39, a factor of 7.8.**

## 1. Discrimination and calibration, over every renewal

`saas.churn_model.build_churn_risk` — the belief the direction named, logged per renewal by
`roll_lifecycle_event` as `churn_probability`:

| believed p_retain | n | accounts | mean believed | realised retention | left |
|---|---|---|---|---|---|
| 0.4–0.6 | 119 | 79 | 0.590 | **0.899** | 12 |
| 0.6–0.8 | 95 | 58 | 0.671 | **0.916** | 8 |
| 0.8–1.0 | 264 | 157 | 0.935 | **0.936** | 17 |

`discrimination_auc` **0.5586** · `calibration_error` **−0.1262** · mean believed churn 0.2036
against a realised 0.0774 (**x2.63**).

The company's own price-keyed estimate (`company.crm.churn_model.estimate_churn_probability`,
logged as `company_churn_estimate`) on the same 478:

| believed p_retain | n | accounts | mean believed | realised retention | left |
|---|---|---|---|---|---|
| 0.2–0.4 | 1 | 1 | 0.390 | 0.000 | 1 |
| 0.4–0.6 | 2 | 2 | 0.589 | 1.000 | 0 |
| 0.6–0.8 | 48 | 36 | 0.744 | 0.917 | 4 |
| 0.8–1.0 | 427 | 147 | 0.917 | 0.925 | 32 |

`discrimination_auc` **0.5275** · mean believed churn 0.1028 against a realised 0.0774 (**x1.33**).

**Both beliefs are monotone in the right direction and both are almost flat.** Across 34 points of
believed retention the first moves realised retention by 3.7 points; the second, across 17 points
of belief, moves it by 0.8.

## 2. Is the inversion at believed p_retain 0.35–0.62 real? **No.**

The A/B's inverted rows, beside the same range measured on 478:

| A/B (25 priced) | | | this instrument (478 rolled) | | |
|---|---|---|---|---|---|
| believed | realised | n | believed | realised | n (accounts) |
| 0.346 | 0.818 | 11 | | | |
| 0.557 | 0.250 | 4 | 0.590 | **0.899** | 119 (79) |
| 0.616 | 0.000 | **4** | | | |
| 0.928 | 1.000 | 6 | 0.935 | 0.936 | 264 (157) |

The two rows carrying the inversion were **4 renewals each**. On the whole book the same region of
belief holds 119 renewals from 79 households and its realised retention sits *below* the confident
bucket's, which is the direction the belief predicts. There is no inversion to explain.

**One honest limit, and it is load-bearing.** The A/B's `believed_p_retain` is the VALUE ARM's
number — `company/pricing/value_based_renewal.py` via `enriched_churn_estimate`, evaluated at the
margin the arm chose. It is not `build_churn_risk`, and a control run does not produce it. What
this instrument can say is (a) the belief the direction named shows no inversion on 478, and (b)
the arm's own belief FAMILY, graded at the rate the flat rule actually charged, shows none either
— but puts only **3 of 478** renewals in the 0.35–0.62 band at all. That band is largely
manufactured by the arm's own pricing: it is where the arm's belief goes when the arm charges
more. Regrading the arm's belief at population scale therefore needs a full-window value-arm run
(≈28 min measured) with this same grade pointed at its `value_arm_log`. That is the next
instrument and it is not built here.

## 3. Why AUC 0.5586 is a real failure and not small-n: the oracle ceiling

The world publishes its own fully-adjusted `realized_churn_probability` per renewal — the number
the dice were actually rolled against. Graded by the identical statistic on the identical
population it scores **0.8109**.

So this population IS rankable, comfortably. A belief scoring 0.5586 against a 0.8109 ceiling is
a belief leaving most of the available information on the table, not a statistic defeated by 37
departures. Without this control, "AUC near 0.5" and "37 events is too few" are the same reading;
with it, they are not. (R15: the control that could have made this finding vacuous is built and
published, not assumed away.)

## 4. THE MECHANISM: the sign is right and the dose is wrong by ~8x

`build_churn_risk` is `BASE_ANNUAL_CHURN_PROBABILITY + k x CHURN_UPLIFT_PER_BILL_SHOCK`, so the
belief is a pure function of k, the bill shocks in the twelve months before the renewal. Every
belief on this run inverts cleanly to its k (478 of 478 on the lattice), which puts the dose,
the world's true probability at that dose, and the outcome in one table:

| bill shocks k | n | accounts | believed churn | world true p_churn | realised |
|---|---|---|---|---|---|
| 0 | 199 | 157 | 0.050 | 0.0280 | 0.065 |
| 1 | 37 | 36 | 0.080 | 0.0615 | 0.027 |
| 2 | 10 | 9 | 0.110 | 0.0998 | 0.100 |
| 3 | 4 | 4 | 0.140 | 0.0566 | 0.250 |
| 4 | 4 | 4 | 0.170 | 0.0495 | 0.000 |
| 5 | 10 | 7 | 0.200 | 0.1411 | 0.100 |
| 6 | 12 | 7 | 0.230 | 0.0365 | 0.083 |
| 7 | 4 | 3 | 0.260 | 0.2025 | 0.000 |
| 8 | 19 | 19 | 0.290 | 0.0402 | 0.000 |
| 9 | 6 | 6 | 0.320 | 0.1453 | 0.333 |
| 10 | 15 | 14 | 0.350 | 0.0603 | 0.133 |
| 11 | 39 | 36 | 0.380 | 0.1263 | 0.077 |
| 12 | 119 | 79 | 0.410 | 0.0745 | 0.101 |

**The candidate mechanism the direction named — that bill shock predicts the OPPOSITE of what the
model assumes — is REFUTED.** `sign_agrees_with_model` is true: 0 shocks realises 6.5% churn, 12
shocks realises 10.1%, and the world's own true probability rises from 0.0280 to 0.0745 across the
same span. Bill shock does push a customer out of the door on this book.

**What is wrong is the DOSE.** The model adds 3.00 pp of churn per shock; the world delivers 0.39
pp per shock end to end (`attenuation_factor` **x7.76**). And the base is over-stated too: at k=0
the model says 5.0% where the world's true probability averages 2.8%. Read together, the belief's
range across the observed dose is 5%→41% while the world's is 2.8%→7.5%.

The attenuation is not mysterious, and the code says where it happens.
`simulation/customer_events.roll_lifecycle_event` takes the base rate and multiplies it through
the passive-renewer cap, the market-year switching multiplier, the price-position multiplier,
income stress and satisfaction. Each of those is a fidelity mechanism decided on its own merits
(R13 baseline, not curriculum). Their COMPOUND effect on the bill-shock signal has never been
measured, and it is a 7.8x compression: the model's largest lever arrives at the roll as its
smallest. **That is the repair to draw next, and it is deliberately not made here** — the
direction says diagnose then stop, and R12 says the AUC is a diagnostic, never a thing to move.
No constant in `saas/churn_model.py` was touched by this work.

## 5. The four published numbers, restated on 478

| published | measured on | restated here |
|---|---|---|
| A/B `discrimination_auc` **0.4653** | 25 priced, 9 departures | **0.5586** for `build_churn_risk`, **0.5275** for the company estimate — above a coin flip, far below the 0.8109 ceiling |
| A/B inversion at believed 0.35–0.62 | n=11, n=4, n=4 | **not present**: 119 renewals from 79 accounts, monotone in the right direction |
| ladder level error, believed **33%** vs realised **5.5%** | 22 decisions, pooled intercepts | same DIRECTION, one fifth the magnitude: the same belief family reads **10.3%** believed against **7.7%** realised (x1.33); the named belief reads **20.4%** vs **7.7%** (x2.63) |
| arm `calibration_error` **−0.0774** | 25 priced | **−0.1262** for `build_churn_risk`, **−0.0254** for the company estimate |

Every one of the four moves. None of them was WRONG for its own population — each was a correct
statistic over a set of 22–25 decisions that the arm's own pricing chose. The population was the
artefact, and the direction that drew this was right that one instrument diagnoses all four.

## 6. Independence — what this grade is NOT

**The belief and the outcome share a source, and that is stated in the artefact rather than left
for a reader to find** (`independence.reading`). `roll_lifecycle_event` SEEDS the world's
`effective_p_retain` from the same `build_churn_risk` number before applying its multipliers. So
section 1's grade of that belief is not "a forecast against an unrelated tally"; it measures
whether the world's own adjustment chain preserves the ordering and the level of the base rate it
starts from. Section 4 is the same fact stated usefully: it does preserve the ordering and
compresses the level by 7.8x.

The `company_churn_estimate` leg does NOT feed the roll — it is computed from the old rate, the
new rate and tenure, and is the company's own read. That is the independent grade, and it scores
0.5275.

## 7. What this does not say

It does not say the value arm is worthless; the arm's £7,066 realised advantage is a different
measurement on a different book and is untouched here. It does not say the world is wrong — the
world's own probability ranks its own outcomes at 0.81, which is what a coherent world does. It
does not price anything, change any constant, or repair the estimator.

**Open question, filed rather than answered.** A recount of the bill-shock dose from the run's
`bills` log (12,372 bills, aggregated to the billing account, YoY at the 15% threshold) reproduces
the logged k exactly for 200 of 478 renewals. The two paths do not share a basis — the belief is
computed from settlement `revenue_gbp` while the bills log carries billed totals including VAT,
and held/estimated bills move amounts between periods — so this is **not a check that passed or
failed**, and it is recorded here so the next reader does not spend the same hour discovering it.
Whether an account-level bill-shock count can be recovered from published bills at all is worth
one atom; it is not evidence against anything above.

## Reproduce

```
python3 -m tools.grade_renewal_churn_belief --markdown
python3 -m pytest tests/tools/test_grade_renewal_churn_belief.py -q   # 18 passed
```

Defaults to `docs/reports/run_output_latest.json`; `--run-output` points it at any finished run
that publishes `customer_events`, including a value-arm run when one exists.

## Why LATENT and not BLOCKING

No published figure is wrong. The A/B's 0.4653 and the ladder's 33%/5.5% are correct statistics
over their own populations, and their READING — "the belief is confidently wrong exactly where it
is making decisions" — is what does not survive a 19x larger book. Superseding a reading with a
bigger measurement, in a document that states both, is the ruling's "explicitly recorded and
accepted" disposition rather than a lane refusal. A reader who thinks the reading was load-bearing
enough to count as a figure should overturn this line; the evidence is in the table above either
way.
