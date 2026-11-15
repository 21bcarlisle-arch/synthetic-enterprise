**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

# A Breathing Space moratorium is now drawn live, and four legs of it are not (2026-11-15)

Found building W2_44 (direction, lane 0). Knowledge: `docs/market_research/debt_and_collections.md`,
"The entry rate (E9, 2026-11-15)".

## What changed live
- **The world** (`simulation/debt_respite_draw.py`) draws a standard moratorium once per household
  per billed month. It draws only when the month's bill went unpaid in the world's truth. The rate
  is about 1.3-1.9% a year per indebted account: registrations x 0.37 energy share / Ofgem indebted
  accounts. The share's range is 0.27-0.40. Nothing is drawn before 4 May 2021, and the 12-month
  repeat bar is held.
- **The notice** crosses framed and authenticated: debt-respite seam v2, sender
  `BREATHING-SPACE-REGISTER-01`, stand-in credential. Both books are told.
- **The company** (`PaymentObservationConsumer.observe_moratorium_start_wire`) calls
  `register_entry`. The frozen debt is the company's own ledger balance on the application day.
- **Every Breathing Space cell can now engage**: dunning's `MORATORIUM_HOLD`, the debt objection,
  the Consent offer and C37's meter recovery. Until today `register_entry` had no caller.

## Prediction, filed before any run measures it
Per run, the count of moratoria drawn is about 0.0015 x (household-months after 4 May 2021 whose bill
went unpaid). It is published as `LivePaymentTriad.moratoria_notified`. The count should be small
(tens, not hundreds, on a book of a few thousand), and debt objections should fall by about that
count at most. If a run shows more than 2x the formula, the 12-month bar or the household-month
dedupe is not holding.

## Not drawn, each a way the world is still wrong
1. **Mental health crisis moratoria** (1.5-1.7% of registrations). They have no end a source sizes,
   and a register with no end notice holds one forever. *Next:* an end notice keyed to a treatment
   length, once one is sourced.
2. **Midway cancellation** (day 25-35). No source counts it. Omitting it over-protects.
3. **Added-debt notices** (reg 15). They matter only once the world has a second debt.
4. **Nation.** The world holds none, so Scottish households, who fall under the moratorium on
   diligence, are drawn under the E&W scheme. The rate's GB denominator keeps the expected total
   right.

## What would move the rate
A count of moratoria naming an energy creditor, from an Insolvency Service creditor-type table or
an Ofgem RFI. StepChange's yearbook data sheet (xlsx, not read) may hold 2021-23 shares.
