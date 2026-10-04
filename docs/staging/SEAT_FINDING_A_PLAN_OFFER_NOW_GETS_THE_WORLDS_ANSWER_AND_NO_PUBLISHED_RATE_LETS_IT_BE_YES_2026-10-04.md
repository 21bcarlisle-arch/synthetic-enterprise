# A plan offer now gets the world's answer, and no published rate lets that answer be yes

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey` · **Claim:** `the-world-answers-a-plan-offer` (Lane 0 delivery)

## Premise, re-measured at draw

`49ce42e6c` is on origin and is the item's starting point, not its spending: it records an OFFER
with `household_acceptance: None` and no world answer exists anywhere in `simulation/`. The
duplicate claim the draw named is this item's own id (the executor's own write; no rival seat or
`surgical_land` on this subject in `ps`). Not spent.

## Knowledge first: what is published

`docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md`. **No published rate of
plan take-up among domestic debtors offered one, and no published rate of instalments kept or plans
broken.** Ofgem publishes quarter-end stocks only (Q2 2026: 2.9% of electricity accounts repaying
under an arrangement, 4.0% in arrears without one; 75% of debt value sits with no plan). A stock is
take-up x keeping x plan length x spell length, and cannot be divided back into take-up. Three
sources could not be fully read (two image-based Ofgem PDFs, one 403); the doc names them.

## Pre-registration (written before the wired run)

Baseline, `simulation.run_phase2b.main(report_end="2017-12-31")` at `ba50ef5e6`: 369 journeys,
364 `arrangement_offered` stages, exits cured 318 / open 51.

Prediction for the same run with the world wired through the seam: **369 / 364 / 318 / 51
unchanged**, and every one of the 364 offers carries `household_acceptance: None` with the WORLD's
take-up gap as its reason (not the company's old self-authored text). Any change in a count refutes
the claim that a None answer is inert.

## Result

**The prediction held.** Same run, wired: 369 journeys, 364 offers, cured 318 / open 51, and all
364 offers carry `household_acceptance: None` with the world's take-up gap as the reason. A None
answer is inert, as it should be.

## What was built

- `simulation/plan_offer_response.py` -- the household's answer. `PUBLISHED_BASIS` holds None for
  take-up, keeping and the instalment, each with its reason. On a sourced basis it draws acceptance,
  then each monthly instalment paid or missed, from named substreams; nothing dated after `through`
  is returned.
- `company/interfaces/sim_interface.py` -- `answer_plan_offer` and `get_plan_instalments` on the
  base, stub and live seam. Only the observable answer crosses: accepted, instalment, reason, and
  each instalment's due date and whether it was paid.
- `company/billing/collections_journey.py` -- the desk asks the seam at the offer. Agreed: the plan
  goes ACTIVE and the journey ends on the **`arrangement` exit**. Declined: the plan is cancelled and
  the ladder resumes. No answer: the world's reason is recorded. While a plan is ACTIVE no new
  journey opens; a plan the company's own two-miss rule defaults lets the next missed bill open one.
- Wired live through `background/live_payment_triad.py` (both the company and the D8 shadow).

**Exits reached, by test, through an injected world:** `arrangement`, and a broken plan back into
collections. Live: still none beyond `cured` and open, because the world cannot say yes.

## What it leaves open, named

1. **The rates.** Take-up, keeping and the affordable instalment are all unpublished. A practitioner
   (or a supplier's collections data) is the third side here. The stock shares cannot stand in.
2. ~~**Plan cash never reaches the ledger.**~~ **Closed 2026-10-04** by
   `plan-instalments-post-to-the-ledger`: paid instalments now post as ledger cash
   (`SEAT_FINDING_PLAN_INSTALMENTS_NOW_POST_TO_THE_LEDGER_AND_A_REPAID_PLAN_FREES_THE_ACCOUNT_2026-10-04.md`).
   As first written: Instalments move the plan book only, so the ladder's
   overdue balance never falls. A plan repaid in full therefore REFUSES
   (`PlanPaydownNotOnLedgerError`) rather than letting the next bill dun a repaid debt. Posting plan
   payments as ledger credits through the payment seam is the next piece. It is needed before any
   sourced rate can be switched on for a ten-year run.
3. **An odd reading, not this item's:** 364 of 369 journeys on the 2017 run reach the day-28 plan
   offer, some on debts of GBP 13-16, and 318 still cure. So most journeys cure AFTER day 28. That
   is either late payers who pay between day 28 and 56 (plausible), or a sign the world's lateness
   draw runs long. Worth one look by whoever next measures the lateness distribution.
