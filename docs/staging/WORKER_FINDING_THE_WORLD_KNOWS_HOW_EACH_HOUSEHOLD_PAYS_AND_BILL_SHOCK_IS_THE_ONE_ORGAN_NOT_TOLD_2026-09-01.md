# [WORKER FINDING] The world knows how each household pays, and bill shock is the one organ not told

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Found:** 2026-09-01, defining bill shock before measuring it again, on the director's instruction.
**Knowledge:** `docs/market_research/what_bill_shock_is.md`.

## Class registration

Belongs to `no_caller_and_never_runs`.

## The definition, in one line

Bill shock is **two experiences in two populations**, not one experience with three causes. For a
household paying a level direct debit the shock is a **material change in the amount collected**, or
a **balance it does not understand** — the bill shocks nobody. For a household paying the full
amount the shock **is the bill**. ~74% of GB domestic households pay by direct debit; ~13% standard
credit; ~13% prepayment, for whom neither definition applies at all.

**Which definition applies to a household is decided entirely by how it pays.**

## The world already knows how each household pays

`simulation/household_segments.payment_channel_for_customer()` exists and is consumed by three
organs:

| consumer | what it uses the channel for |
|---|---|
| `simulation/arrears_engine.py` | arrears behaviour by channel |
| `simulation/final_bill_outcome.py` | gone-away recovery (DD ×0.75, standard credit ×1.40) |
| `simulation/run_phase2b.py` | satisfaction (`sim_satisfaction`'s payment-channel delta) |

**`bill_shock_pct` is the fourth organ and it is not told.**
`saas/bill_generator.generate_bill(customer_id, settlement_records, contract_type,
previous_bill_total_gbp, segment, commodity)` takes no payment channel. So the one field that decides
**which definition of shock applies** is computed, held, and consumed by three other organs — and
the shock measure is blind to it.

This is the third instance today of the same shape: the world decides something and the organ that
needs the answer is not given it. The others are
`..._THE_WORLD_ALREADY_DECIDES_WHO_ROLLS_TO_SVT_AND_THEN_DISCARDS_THE_ANSWER_2026-08-30` and the DD
`large_increase` flag that routes nowhere.

## And the population is wrong in a second way

Measured on the live book, 251 accounts:

| | our world | published GB |
|---|---:|---:|
| direct debit | **68.1%** (171) | ~74% |
| standard credit | **31.9%** (80) | ~13% |
| prepayment | **0%** | ~13% |

**There is no prepayment channel.** `PaymentChannel` has two members, so the non-DD 26% of the
published record is folded entirely into standard credit — which is why our standard-credit
population is **2.5× the published share**.

That matters for the definition rather than only for the level: prepayment households have **no bill
to be shocked by and no direct debit to be changed**. Their equivalent experience is an unaffordable
top-up or self-disconnection, a different measurement with a different remedy. Modelling them as
standard credit gives 13% of GB households a bill-shock experience they do not have, and it does so
in the population where affordability pressure is highest.

*(The DD/non-DD binary is a deliberate, recorded simplification — `dd_attribution_confound_w2_10.md`
says so in terms: "Modelled as a **binary** DD-vs-non-DD world; non-DD folds standard credit +
prepayment together (26%)." It was the right simplification for the question that page was asking,
which is DD-discount confounding. It is the wrong one for bill shock, because bill shock is
**defined** by payment method rather than merely correlated with it. A simplification is scoped to
the question it was made for; this finding is that it has been inherited by a question it does not
fit.)*

## Why this makes the current measure meaningless rather than imprecise

`bill_shock_pct` is definition B's quantity — the difference between two bills — applied to
everybody. For the ~68% of our book on direct debit, it differences two statements the household
does not pay. Not a noisy estimate of their experience: **a measurement of a different thing.**

And the fault does not lie with the number: it lies with there having been no definition to check it
against. That is the general failure the director named, and this is its clearest instance.

## What is owed

1. **Pass the payment channel into the shock measure**, and branch the definition on it. The channel
   already exists and already has three callers; this is a wiring, not a model.
2. **Add prepayment as a third channel**, or exclude prepayment households from bill shock
   explicitly. Either is honest; folding them into standard credit is not.
3. **For definition A, measure the change in the amount COLLECTED** (and the balance beside it),
   which means the DD amount has to become a modelled quantity rather than a review artefact — see
   `..._EVERY_CUSTOMERS_FIRST_DIRECT_DEBIT_IS_SET_FROM_HALF_A_MONTH_2026-09-01` and its correction,
   which establishes that our DD has no estimated annual consumption behind it at all.
4. **Only then the cause split**, which now follows from the definition rather than preceding it.

**None of it is done here.** Each moves published figures and each needs its own pre-registration;
and item 3 depends on the DD having a mechanism, which it does not yet.

## What this finding does not claim

Not that the world's payment-channel model is wrong — it is sourced, it drives three organs, and its
binary simplification is recorded where it was made. Not that the 68.1%/31.9% split is a defect in
itself; it is close to the published DD share and the discrepancy is the absent third channel. The
claim is narrower: **the one attribute that determines which definition of bill shock applies is the
one attribute the shock measure cannot see.**
