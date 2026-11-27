**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome`

# A quoted first term is re-priced above its quote by the renewal chain

Found by the delivery seat while grading S2 on the gas-quoted book, 27 Nov 2026
(`docs/staging/records/SEAT_GRADE_S2_GASQ_THE_CAP_HOLD_ARM_ON_THE_GAS_QUOTED_BOOK_2026-11-27.md`, G1).

## What is wrong

A won first term is meant to be contracted on the strike the household was quoted. SLC 23 says the
contract is formed on the Principal Terms the household was given. SLC 22C says its charges cannot rise
during the fix. Both are set out in `docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §13.

`simulation/renewals.py::contracted_first_term` does set the term's unit rate to the quote. But the run
loop then passes that term through the company's renewal chain (`decide_renewal(...)`,
`simulation/run_phase2b.py:3974`, `struck_unit_rate_per_mwh=unit_rate`), and the chain's output is the
rate that is billed and logged.

## Measured (off arm at 5e075efa94, `/var/tmp/se-s2-gasq-grade/quote_vs_billed.out`)

- **All 103 quoted gas first terms** are billed above their quote. Billed rate ÷ quote runs from
  **1.0019 to 1.0283**, with a median of 1.018.
- **0 of the 103** are within 1p/MWh of the quote.
- By year, the median runs from 1.010 (2025) to 1.024 (2019).
- Some legs carry no `portfolio_premium_pct` and still read about 1.02. So the portfolio premium is
  not the only writer adding to the quote. Which writer it is has not been attributed yet.
- Electricity has the same shape. In S2's arm, its four PROS-2021 legs read arm ÷ quote = 1.0040–1.0042.
- The cap hold then tests the **re-priced** rate. The company's gas gate tested the **quote**. So 4
  Sept-2024 legs that passed the gate are clamped at the cap line in the off arm, and billed
  quote × 1.0106 with the hold deleted.

## Why it matters

- The household is billed a price it was not shown. That is a transfer (M2), and so far it is small:
  about 1–3% on gas.
- More importantly, it falsifies every reading that says "contracted at its quote". That includes the
  G1 premise, and S1's electricity P2′ premise.

## What done means

The work is done when a quoted term 0 bills the quote to the penny, in both fuels. Two ways to get there:

- the chain's writers skip a term whose `struck_by == "first_term_quote"`, or
- the quote is struck through the same writers before it is shown.

Either is a company decision, and the knowledge page must say which one a real supplier does first.
It is held by a control that reds if any quoted leg's billed term-0 rate ≠ its quote.

## GAP

Which of the chain's writers adds the uplift is not yet attributed. The first step is to read
`rate_decomposition_log` for one quoted leg, for example `PROS-2016-0003g` (quote 31.626, billed
32.258).
