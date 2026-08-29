# What does each published account count actually count?

**2026-08-29, delivery seat, lane 0.** Direction: *"That is five populations and no statement
anywhere of what each one counts."*

This project's own rule is **"before dividing two numbers, say out loud what each one counts."**
This was the largest live instance of breaking it, and it sat directly under a published solvency
claim.

---

## 1. The census

Printed from the artefacts themselves, not transcribed. Reproduce with
`pytest tests/company/risk/test_mcr_account_population.py` for the selection controls, and the
table below from `docs/reports/run_output_latest.json`, `site/data/value_arms.json` and
`site/data/book_growth.json` as at the 2026-08-29 publish.

| Figure | Count | What it selects |
|---|---:|---|
| `run_output.by_billing_account` | **13** | The **static founder roster** (`saas.customers.CUSTOMERS`), dual-fuel legs collapsed. Resolved at import, so it can never hold an account the funnel won. Settled or not, on supply or not. |
| `run_output.enterprise_value_account_count` | **113** | The **valued subset of the settled book**: billing accounts with a renewal point, still on supply at the last settled day, and with an observed margin. |
| `three_horizon_clv.portfolio.population.available` | **167** | The **settled book**: every billing account with at least one settlement record in the window, any segment, ceased or not. |
| — of which still on supply | **127** | The above less the 40 read as ceased on the supplier's own 35-day continuity rule. |
| — of which **domestic** and on supply | **120** | **The MCR population.** See §2. |
| `value_arms.book.billing_accounts_settled_in_window` | **210** | The settled book **of a different run** — the A/B run's own world. Not comparable to 167 without saying so. |
| `value_arms.book.accounts_at_end_of_window` | **128** | The above, still on supply at that run's window end. |
| `book_growth.years[-1].book_after` | **172** | **Settled** accounts on the book after the 2025 campaign year. |
| `book_growth.years[-1].accounts_after` | **587** | The **commercial book**: 82 founders plus 505 accounts the funnel won, settled or not. Our settlement engine processes a uniform **17.9%** sample of them. |
| *(was)* collateral `balance_sheet.accounts_held` | **24** | **None of the above.** The per-**commodity** legs of the import-time static roster. |

**There were six populations, not five.** The sixth was the one carrying the money.

---

## 2. The population the collateral desk is entitled to see, and the wall question

**The wall question, asked out loud.** The MCR is a company-side figure, so the test is not what
the sim knows — it is what a real supplier's own finance function would have in front of it.

> Could a real UK supplier's finance function put this number in front of a trading counterparty?

**Yes, and it is close to the only number it could:** how many domestic accounts it bills, on
supply today, dual fuel counted once. Every leg of the selection is a read of the supplier's **own
settlement record** and its **own customer register**. Nothing consults the world's
`churned_billing_accounts`; the supplier reads cessation off its own 35-day continuity rule and is
allowed to be wrong about it — that gap is a measurable quantity, not something to paper over.

**The selection**, in `saas.capital.solvency.mcr_accounts_on_supply`:

1. Distinct **billing accounts** with a settlement record — dual-fuel legs collapsed, because
   £130 is levied per account, not per meter.
2. Less accounts read as **ceased** (35-day continuity). A customer who has gone obliges no
   capital.
3. Less accounts outside `MCR_DOMESTIC_SEGMENTS`. SLC 27's capital adequacy regime is a
   **domestic** obligation. The excluded count is *published*, not dropped — an exclusion that
   cannot be counted hides what it removed.

An account with **no segment label is treated as domestic**: the default must cost us, never waive
an obligation on our own missing data.

### Why not the commercial book (587)?

`free_equity = net_assets − accounts × £130` is a **subtraction**, so both sides must count one
supplier. `net_assets` is `final_treasury`, read off the settled record. So the account count is
read off the settled record too.

The commercial book is a real and larger supplier, and the **growth desk is right to plan against
it** — it nets 587 against the *founding capital*, which is that same supplier's balance sheet.
Both desks are now internally consistent; they were simply never labelled, so they read as one
company contradicting itself.

Netting 587 accounts of MCR against a treasury earned on 17.9% of them would mix two suppliers,
and the only repair in that direction is to scale the treasury up by the sample rate — inventing a
number, the defect R1 exists to remove. **The settled-book answer has no invented number in it.**

---

## 3. R6's basis: repaired, not defended

`WORKER_FINDING_R6_JOINS_ACQUISITION_SPEND_TO_COLLATERAL...` §4 read `accounts` = 13 from
`by_billing_account`. **13 is the founder roster and is the wrong population.** So was the 24 the
code was actually using — wrong in three separate ways at once:

- per-**commodity** legs, so every dual-fuel household counted twice against a per-account charge;
- bound at **import**, so not one of the accounts the funnel won was visible;
- **no domestic/non-domestic split**, and no cessation.

At the published run's own net assets of **£331,361.47** and gross marked exposure of
**£66,963.44**:

| basis | n | MCR claim | free equity | headroom to the trigger |
|---|---:|---:|---:|---:|
| **was** — static per-commodity legs | 24 | £3,120 | £328,241.47 | £261,278.03 |
| **now** — domestic accounts on supply | **120** | **£15,600** | **£315,761.47** | **£248,798.03** |
| *(the commercial book, for contrast)* | 587 | £76,310 | £255,051.47 | £188,088.03 |

**The verdict does not change at any of the three.** Free equity covers the exposure by 3.7× even
on the harshest basis, so R6's central result stands exactly as recorded: the mechanism is reached
and does not fire, and the distance IS the answer. What changes is that the distance is now
denominated on a population with a name. **Free equity was overstated by £12,480.**

Nothing was tuned to make this fire, and the repair moves the number in the direction that costs
the company, which is the direction a repair should be able to move.

---

## 4. What is now true, and what is not

**Enforced in code** (`tests/company/risk/test_mcr_account_population.py`, 12 controls, each
mutation-proven against the specific defect it names):

- The desk **counts** the accounts rather than being told a number — a census the run does not
  reach is the R1 defect in different clothes.
- A **null control**: omit either half of the census input and the caller's own number stands.
  Without it, "the desk counts for you" is satisfiable by a desk that ignores its inputs.
- The **reconciliation** — published `free_equity_gbp` and published `accounts_held` must satisfy
  the identity that produced them. This is the control that outlives this repair: it goes red
  whenever either side of the subtraction is restated independently of the other, which is the
  class rather than this instance.
- A caller that does not name its population is published as **`unnamed`**, never given a
  plausible label. A wrong name is worse than no name — it sends the next reader to the wrong
  roster.

**Named at the producer, so the artefact carries it and not just this file:**

| producer | field it now emits |
|---|---|
| `saas/reporting/annual_report.py` | `by_billing_account_population`, `enterprise_value_account_population` |
| `company/risk/counterparty_collateral_desk.py` | `accounts_held`, `accounts_population`, `accounts_selection` on the margin summary |
| `tools/run_value_cycle_ab.py` | `book.what_each_count_selects` |
| `tools/generate_book_growth_data.py` | `what_each_count_selects` |

**One of those labels turned out to be wrong, not merely unnamed.** The arms artefact's
`accounts_at_end_of_window` reads as "the book at the end" and is not: it is
`enterprise_value.portfolio.account_count`, the **valued subset** — accounts with a renewal point,
still on supply, *and* with an observed margin. It is smaller than the book at the end by however
many accounts could not be valued. The key is left alone, because renaming it would void every
artefact that already cites it; what it counts is now stated beside it.

**Not done, and named rather than left to be rediscovered:**

- `company/finance/treasury.mcr_headroom` and `saas/capital/solvency.compute_solvency_signal`
  both take a `customer_count` from their caller and neither names it. They are the next two
  places the same defect can re-enter.
- The 17.9% settlement sample is the reason the settled book and the commercial book differ at
  all. It is an **engine** limit, not a commercial result, and it is what makes "which supplier?"
  a live question rather than a pedantic one.
