**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# SEAT PROPOSAL — a personal payment plan per customer and debt management as a next best action, designed as one (2026-10-11)

*Delivery seat. For the director's reading before anything is built into the run (his instruction, 2026-10-11:
"Design, then bring it to me before building into the run"). Knowledge first, per his standing rule: the pages
this rests on were written and published the same day and are cited by section below.*

## 0. The idea in one paragraph

**Credit risk sets how far a customer's balance may drift from zero, not how much they pay over the year**
(director). Every customer's plan has the same two parts: an **amount** -- the company's one forecast of the next
twelve months at the rates it knows, plus the balance to clear -- and an **envelope** -- how far the running
balance may sit from zero before the plan acts, and how fast it closes the gap when it does. Low risk: a wide
envelope, smoothing, prompt refund of surplus credit, no catch-up shocks. Higher risk: a narrow envelope held near
zero, with the winter shortfall carried in the forecast's seasonal shape rather than recovered as a catch-up. Debt
is what happens when a balance leaves its envelope; the next best action is the plan's own correction, escalated
within the rules. Credits and debits net across the portfolio in the accounts -- but **not** in Ofgem's cash
coverage test, which counts gross credit (§3c), so the portfolio sets a ceiling on how much credit the low-risk
envelopes may hold in aggregate.

## 1. What the rules require (knowledge pages, landed 2026-10-11)

- **The amount** must be set on the best and most current information, including reads and what the customer or
  a third party has said, and reassessed when new information is likely to change it materially (SLC 27.15, Ofgem
  decision 26 Aug 2022; `what_a_supplier_holds_to_size_a_direct_debit.md`). No mandated review cadence.
- **Refund** of credit on request is a duty; proactive refund is a service choice above it (same page).
- **After two missed monthly payments** the supplier must make proactive contact (SLC 27.5B); repayment rates are
  set on ability to pay, with pauses and monitoring of failed plans (SLC 27.8A; Consumer Standards decision
  18 Oct 2023; `company_debt_management.md`).
- **Deposits** only where reasonable, none if a safe prepayment meter is accepted (SLC 27.3-27.4); **payment-method
  differences** must be cost-reflective (27.2A); **involuntary prepayment** runs through hard gates no score
  bypasses (SLC 28B, 2023 code); **vulnerability** overrides any tier.
- **Capital** (`bad_debt_provisioning.md`): Capital Target GBP 115 ANA per dual-fuel customer; the supplier
  must notify Ofgem when cash falls below 20% of **gross** customer credit balances; Ofgem may direct ringfencing.
- **UNCLEAR, and the design avoids depending on it:** whether a credit-risk tier alone may be the stated 27.15
  basis for a HIGHER amount. So risk never raises the annual amount here; it sets the envelope and the correction
  speed, while the amount stays the forecast plus the balance to clear -- lawful under 27.15 on its face.

## 2. The forecast the amount rests on (finding landed 2026-10-11)

Today the company holds four forecasts and the DD review uses the worst of them for later years
(`SEAT_FINDING_SEVERAL_CONSUMPTION_FORECASTS_..._2026-10-11.md`). The plan uses **one per property**: level from
the trailing twelve months of the company's own data where a year exists (measured MAPE 1.9% electricity, 3.2% gas)
and the registry figure before that; seasonal shape from the account's own last year where it exists (0.54 /
0.99 points) and the published monthly shares before; priced at the rates fixed for the term and the company's
forward view beyond. **GAP (owed, a build):** normal-weather adjustment exists nowhere in the code; until it does,
the forecast is labelled "actual-weather shape". The same forecast is to feed purchasing, unbilled estimation and
customer value -- one forecast, as the director asked -- but that unification is its own step after this design.

## 3. The levers

### 3a. Supplier-controlled, for customers already on a fixed DD -- tested as RESULTS

| Lever | What the company chooses | Rule it sits under |
|---|---|---|
| Amount | forecast + balance to clear, spread over a chosen horizon | 27.15 |
| Review trigger | material-change rule: reassess when the forecast or balance moves the amount by more than a threshold, on each read | 27.15 (no cadence) |
| Size of change | cap per review on the step up; the remainder carried in the envelope | 27.15 discretion |
| Surplus credit | refund above the envelope's top, promptly (low risk) or at review | 27.16 floor; proactive above it |
| Envelope | balance band by risk tier; correction speed back to zero | design choice (§1 UNCLEAR avoided) |
| Contact timing | before a large review step; at first missed payment; 27.5B at two | 27.5B |
| Debt-plan terms | repayment rate from ability to pay; pause; monitoring | 27.8A |

### 3b. Customer-chosen -- run only as SENSITIVITIES across a take-up range, never as findings

| Lever | Published take-up | Toggle (range) |
|---|---|---|
| Change payment method | migration rates exist for some paths (`gb_payment_method_migration_rates.md`); voluntary DD-to-other on a shock NOT ESTABLISHED | `q3_dd_cancel_after_shock_share`, 0-0.1, ASSUMED range (no published rate) |
| Seasonal plan (pay more in winter) | NOT ESTABLISHED (no cap category) | `q3_seasonal_plan_take_up`, 0-0.2, ASSUMED range |
| Opt-in buffer | NOT ESTABLISHED | `q3_buffer_take_up`, 0-0.2, ASSUMED range |
| Move the collection date to payday | GB effect NOT ESTABLISHED; analogues: -36% late payment (US, bill timed to benefits), -30% on-time when payday falls after due (Argentina) | `q3_payday_alignment_failure_reduction`, 0-0.36 (the upper end is the US analogue's effect on late payment, not a GB figure); take-up 0-0.3, ASSUMED range |

All four are labelled toggles with these ranges in `assumption_toggles.yaml` before any run reads them. An ASSUMED range has no published basis: it bounds the sensitivity, it is not evidence, and a result that turns on it is reported as turning on an unpublished number.

## 4. What the company knows to choose them (the wall)

Its own forecast (§2); its bills, reads and estimated-read flags; each account's running balance; DD collection
outcomes (returns, failures); its own default belief (`company/pricing/default_belief.py`, by method and arrears
state); the Priority Services Register (disclosure only); and, for ability to pay, what the customer tells it in
a debt conversation. **Never** the household's hidden finances, job loss or pay-or-heat state -- those are the
world's, and only the world's response to the plan sees them.

## 5. Scoring

Primary: **forecast customer lifetime value** per home and **portfolio value**. Counted beside it, never folded in
without a price: bill shock (a DD step above the company's existing 15% large-increase flag, `company/billing/dd_review.py` -- a modelling convention, not a published threshold), **gross credit held** (and
its distance from the 20% cash-coverage trigger), failed payments, complaints (via the world's complaint response),
hardship (homes in debt beyond 91 days; homes self-rationing). **Vulnerable and stretched households reported
separately** -- vulnerable as the company knows it (PSR) and, for grading only, as the world knows it (latent V1/V2
and income stress).

## 6. The test

The lean decision set, as the save and retention offers were graded: each customer-year a coin-drawn arm, the
world's hidden finances, job loss (`simulation/life_events.py`) and pay-or-heat (`simulation/self_rationing.py`)
deciding the response. Arms:
1. **Today:** flat annual review, last twelve months billed GBP, +/-5% variance (`company/billing/dd_review.py`).
2. **Simple rules:** rates-in-force review (the rule SLC 27.15 now supports); quarterly review; refund all credit
   above one month's amount.
3. **The plan:** the envelope design of §3a, tiered by the company's own risk belief.
Then the 40-founder-plus-wins and founders-only seed families for the settled-run read-out, reported by origin
(founders vs campaign wins), per the director's condition.

## 7. Does the world press back? (census, 2026-10-11) -- what is missing

The world's payment-method mix is well sourced (DD 72/75%, the rest split evenly), but its **dynamics** are not:
1. **Method is drawn once and never chosen again**, uncoupled from income, tenure or vulnerability -- the research
   says prepayment skews to low income, renters and debt, and that method is largely inertia.
2. **The only live change is supplier-driven**: a DD stopped after two consecutive returns, to pay on receipt.
3. **Debt to prepayment is unwired** (`company/billing/payment_method_register.py` has no caller).
4. **A mover does not inherit the home's meter or method**; the incoming occupant redraws.
5. **Cancelling a DD after a bill shock (DD4b) is named and unbuilt** -- the world cannot punish a catch-up shock,
   so a plan that avoids shocks would earn nothing for it.
6. **Job loss and pay-or-heat** change payment outcomes, never method; **financial vulnerability (V2) drives
   nothing**.

For this test, (5) is the one that blocks the supplier result: without it, avoiding bill shock is worth nothing in
the world. It is world work admitted under the director's rule, built with its own knowledge page and a labelled
range. (1), (3) and (4) matter for the customer-chosen levers and for debt; they are listed, ranked, and not built
for this test unless the director wants them first.

## 8. What I would like from the director

Nothing to start the knowledge-backed parts. Two choices are his: whether DD4b (the world's response to a bill
shock) is built first so the plan's shock-avoidance can be graded at all (recommended), and whether to begin with
the supplier-controlled levers only (recommended), leaving the customer-chosen ones as later sensitivities.
