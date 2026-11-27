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

## Attributed and fixed (delivery seat, 27 Nov 2026)

- **The writer is B12's bad-debt allowance**, at the top of `company/pricing/renewal_rate_chain.py::decide_renewal_rate`.
  The run loop hands a first fixed term the book's belief (the "A FIRST TERM'S FIXED STRIKE CARRIES THE BOOK'S
  BELIEF TOO" block in `simulation/run_phase2b.py`). The chain then adds `unit_rate × default_belief_rate`.
  On `PROS-2016-0003g`, 32.25825 / 31.626 = **1.019992**. That is `PRIOR_LOSS_RATE` = 0.020 to four places, as
  an empty book's belief would be. The learned belief falling below the prior after 2019 explains why the
  median fell from 1.024 to 1.010. Writers 1 and 2 never reach a term with index 0, and writer 3 has
  `MIN_TERM_INDEX_FOR_UPLIFT`. The portfolio premium shown on the rows is the account-state record's reading,
  not a writer that acted on the term.
- **Which way a real supplier does it:** it prices its allowances into the quote before showing it, and never
  re-runs pricing over a formed contract. This is set out in §13 of the fuel page, amended today.
- **Built:** `RenewalDecisionInputs.contracted_at_quote`. With it set, the chain adds no allowance and applies
  no cap hold. If the rate still moves, it refuses with a named `ValueError`. Control:
  `tests/company/pricing/test_a_quoted_first_term_bills_at_its_quote.py`. Its partition legs fire in both
  directions, and dropping the run-loop keyword reds it (mutation performed).
- **Prediction for the next book carrying this:** 103/103 quoted gas term-0 legs bill their quote exactly, and
  so do S2's four electricity PROS-2021 legs. The electricity legs were not attributed, so this is the part
  that can refute. If another writer moves them, the run dies on the refusal and names the term.
- **Open:** the quote carries no bad-debt allowance (GAP in §13). Handed on as its own one-variable item.
