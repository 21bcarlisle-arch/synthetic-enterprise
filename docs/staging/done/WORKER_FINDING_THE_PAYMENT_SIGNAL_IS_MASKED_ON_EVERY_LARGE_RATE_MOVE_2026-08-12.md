# WORKER FINDING — the company's payment/experience churn signal is masked on every large rate move

**Severity:** LATENT · **Lane:** C_customer_ops

**Filed** 2026-08-12, from KNIFE3 step 20 (`A_composition_lift`, register §3o).
**Class** company-model fidelity. **Not** a wall crossing, and deliberately NOT fixed in the
step that found it (B7: a wall pass never moves a number in the same commit as an import).
**Rank requested** backlog, unless the churn-accuracy figure is about to be published.

## Observed, with evidence

`company/crm/enriched_churn_estimate.py` combines its two inputs as

    result = max(rate_estimate, payment_estimate) * market_conditions_multiplier(renewal_year)

Both `enriched_churn_estimate` and `enriched_passive_churn_estimate` use that rule.

Measured on the step-20 seam fixture (`tests/company/interfaces/test_churn_estimation_seam.py`
— one resi account, £180 → £240/MWh, a +33% rise, `bill_shock_count=2`,
`behaviour_score=POOR`, `satisfaction_score=41.0`):

  * **ACTIVE arm** — the estimate is `0.5513` with the full payment signal and `0.5513` with
    `bill_shock_count=0`. Setting `behaviour_score=None` also moves it by nothing. The rate arm
    dominates the `max()`, so the entire payment/experience signal is discarded.
  * **PASSIVE arm** — the same three inputs each move the estimate, because passive rate
    sensitivity is deliberately near-inert.

This is `observed-with-evidence`: the control that found it is
`test_mutation_a_dropped_keyword_moves_the_answer`, which FAILED on its first run against the
active arm and was split per-arm with the reason written into it rather than the fixture being
reshaped until it passed.

## Why it may matter (inferred, not observed)

`max()` means the two models never combine — the louder one wins outright. A customer who is
BOTH facing a large rise AND sliding into arrears is estimated identically to one facing the
same rise with a clean payment record. Phase QK extended the enriched estimate to passive
rollers precisely because the payment signal was absent there; this is the same absence one
level up, on the arm where the majority of the company's churn *value* sits (active renewers
are the ones a retention offer can save).

Whether that is wrong is a **modelling** question, not an arithmetic one, and it is the
company's own to get wrong — a real supplier's retention model may legitimately take the worse
of two views. What is NOT defensible is that it happens **silently**: nothing in the harness
reports how often the payment arm is masked, so the company cannot tell whether its
payment-behaviour investment is doing anything at renewal.

## Recommendation — and I am not asking, this is what the next draw on this should do

1. **Measure before changing anything.** Add a per-renewal diagnostic to the churn desk
   recording which arm won, and report the masked-fraction per year on the calibration surface
   alongside recall/precision. If the payment arm wins ~never, `combined_churn_probability` is
   dead weight on the active arm and the company should know that about itself.
2. **Only then** consider whether the combination rule should stay `max()`. R12 applies: the
   masked-fraction is a DIAGNOSTIC, and the fix is never "tune until recall improves".
3. Do not touch `enriched_churn_estimate`'s arithmetic in the same change as the measurement.

## What this finding is NOT

Not a claim that the churn model is broken, and not a wall crossing — `enriched_churn_estimate`
is entirely company-side and reads only observables. The step-20 cut moved WHO calls it, not
what it computes; every pre/post value is identical, asserted against the sequence transcribed
from `7a199defe`.
