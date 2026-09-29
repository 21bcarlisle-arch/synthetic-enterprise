**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `PB6_the_engagement_observable_crosses_the_seam`

# The engagement factor counts its own prior twice, and learns against the wrong expectation

**2026-09-29.** Found by a scheduled-tick worker while drawing the EH-1 remedy on PB6
(Expert Hour `15248367c`).

## What was printed, before any change

`CompetitivePressureLedger.payment_method_engagement_reading` at HEAD `4c4dac99d`. The book is one
where prepayment customers leave at EXACTLY the published CIM relative rate (0.585 x the direct-debit
rate), with a uniform 0.08 belief on every renewal:

| prepayment renewals | raw ratio | w | learned factor | published prior |
|---:|---:|---:|---:|---:|
| 200 | 0.644 | 0.514 | 0.466 | 0.585 |
| 2,000 | 0.643 | 0.914 | 0.391 | 0.585 |
| 20,000 | 0.638 | 0.991 | **0.375** | 0.585 |

**Correction, kept beside the claim.** That book was built wrong. It set the prepayment rate to
0.585 x the DIRECT-DEBIT rate, but the factor and the CIM prior are both relative to the whole BOOK.
Rebuilt correctly (book rate 0.08, prepayment 0.0468, direct debit 0.0883), HEAD's rule reads 0.440
/ 0.360 / 0.344 at 200 / 2,000 / 20,000 prepayment renewals. The defect is the same shape, and on
the correct book it is larger. A book that confirms the prior drives the belief AWAY from it. With more evidence the factor tends to
`prior x ratio`, which is the prior counted twice, rather than to `ratio`.

## Two defects, one of them named by the Expert Hour

- **EH-1b (new, not in the Expert Hour).** `posterior = prior x ratio ** w` is the right blend for
  the market-wide multiplier, because there the ratio is a RESIDUAL. It is realised losses over a
  predicted loss count that already includes the prior. The engagement ratio is not a residual.
  `p_channel / p_book` is itself an estimate of the factor, so the blend has to be geometric
  between the two estimates: `prior x (ratio / prior) ** w`. At w = 0 that returns the prior, and
  as w goes to 1 it returns the evidence.
- **EH-1 (the Expert Hour's first doubt).** The ratio is a marginal. It needs to be the channel's
  observed/expected against the PRE-factor belief, taken relative to the book's observed/expected
  on the same belief. Otherwise arrears, and every other term already correlated with channel,
  gets learned again as "engagement".

## Pre-registration (filed before the remedy was run on any book)

1. On the book above, the remedied factor converges to the prior, within 2% at 20,000 renewals.
2. On a book where the pre-factor belief ALREADY predicts prepayment's lower departures (for
   example, through the arrears term), and they leave at exactly that predicted rate, the remedied
   factor goes toward **1.0**. The raw rule reads the same book as roughly 0.58 x 0.58.
3. Real run: the company's end-of-run prepayment factor moves UP toward 1.0 compared with HEAD.
   **I cannot yet say by how much.** This is not measured in this increment. It is EH-2's
   planted/null run, and that run is only meaningful once this remedy is in place.

## What remains a named gap, not a number

The CIM w6 prior is a survey MARGINAL (switching rate by payment method across the population).
Under O/E the likelihood is CONDITIONAL on everything else the belief carries. The two are
different quantities, so the blend is between a marginal prior and a conditional estimate. Nothing
in `docs/market_research/` or the regulation commons publishes a CIM rate conditioned on arrears.
The gap is stated in the code, not filled with a number: as evidence accumulates the weight moves to
the conditional reading, which is the direction that shrinks the error.

## Result, after the remedy, printed with the same instrument

| case | 200 | 2,000 | 20,000 |
|---|---:|---:|---:|
| P1: channel leaves at exactly the published relative rate (prior 0.585) | 0.586 | 0.590 | **0.585** |
| P1 with HEAD's rule, same book | 0.440 | 0.360 | 0.344 |
| P2: the pre-factor belief already predicts the lower rate, and it lands there | 0.732 | 0.942 | **0.993** |

Predictions 1 and 2 held. Prediction 1 was first checked against the mis-built book above and read
0.638. The cause was the book, not the rule, and both readings are recorded here. Prediction 3 (the
real run) is still open and is EH-2's run.

Landed in the same commit as this finding: `company/crm/competitive_pressure.py` (O/E counters,
the reading, and `log_space_weight_for_variance`), `company/crm/churn_desk.py` (the desk books the
pre-factor belief), and the controls in
`tests/company/crm/test_the_company_learns_engagement_from_its_own_book.py`.
