**Severity:** RECORDED · **Lane:** E_finance_treasury · **Epoch:** 3 · **Atom:** `B6_collateral_cash_death_loop`

# R6: acquisition spend now reaches the collateral desk, and the company is £316,009 from the trigger

Director, 2026-08-28: *"R6 is the prize and I want it reached — acquisition spend driving collateral
demands is the mechanism the CMA records for suppliers weakening their own balance sheets, and it's
the first thing that would make SURVIVE mean something."*

**It is reached, and it does not fire.** Both halves of that sentence are the finding.

---

## 1. What was missing, and why the obvious wire was the wrong one

The CMA's mechanism is one sentence: growth means acquisition costs paid up front, which

> "weakened a firm's balance sheet … increasing the perceived riskiness of the supplier and,
> therefore, the quantity of collateral that trading counterparties required."

This repository has had a growth campaign and a collateral book for months with nothing between
them. But **the quantity of collateral required could not rise**, whatever happened to the balance
sheet, and that is a structural fact rather than a missing parameter. The only collateral modelled
was variation margin, `max(0, -netted_mtm)` — the amount by which the company is out-of-the-money.
That is already 100% of the OTM exposure. No assessment of the supplier can make it more.

What a real counterparty adds when it grows uneasy is an **independent amount**: collateral posted
over and above the mark. `company/trading/initial_margin_register.py` describes exactly this, and
the B6 FRAME records at §1.9 that it is `initial_margin_gbp=0.0` on every call the live run makes.
That zero is the hole R6 fits.

## 2. No invented rate, and the shape that avoided one

The first design set the independent amount as a percentage of notional per credit band. That is how
real CSAs are written and it would have meant inventing the band table — **the precise defect R1
existed to remove**, three days later, in a new place. The shipped design has no tunable percentage
in it at all:

| | | source |
|---|---|---|
| **WHEN** it is demanded | when FREE EQUITY — net assets less the capital the regulator already obliges against the customer book — no longer covers the gross exposure being run | MCR £130/account, Ofgem decision 26 July 2023 |
| **HOW MUCH** | the exposure that could accrue over a stressed close-out | 5-day horizon: `initial_margin_register.py:11`, "sized to cover a defined stressed holding period (typically 5 days)" |
| the close-out move | **MEASURED** from the observable price history, point-in-time | the run's own Elexon record |

The trigger is a bright line, not a tuned threshold: below it, the counterparty is looking at a name
whose own balance sheet cannot absorb its own position.

## 3. It closes the one-directional death as a side effect

B6 FRAME §1.9 records that the model can only kill on a price FALL, because a long hedge book goes
in-the-money on a spike and posts no variation margin at all. An independent amount is about the
supplier's credit, not the position's sign. **A counterparty the company is in-the-money with now
forms a call for the first time.** Not designed for; it falls out.

Demonstrated on a two-name book, identical positions and marks throughout:

| balance sheet | calls | collateral demanded |
|---|---|---|
| £5,000,000 | 1 | £100,000 |
| £50,000 | **2** | **£156,000** |

Same book. 56% more collateral, because the equity fell.

## 4. THE RESULT: the mechanism does not fire on the published company

Measured against the published run (`docs/reports/run_output_latest.json`):

| | |
|---|---|
| net assets (final treasury) | £337,305.65 |
| accounts | 13 → MCR claim £1,690 |
| **free equity** | **£335,615.65** |
| peak net exposure (2021-12-31) | £19,606.81 |
| worst 5-day move in the mark, by 2025-06-07 | 28.0% |
| independent amount demanded | **£0.00** — `free_equity_covers_exposure` |
| **headroom to the trigger** | **£316,008.84** |

**The company would have to lose £316,009 of equity — 6.8× its entire ten-year campaign spend of
£46,408 — before a counterparty asked it for a penny above the mark.** Its free equity is 17× its
own peak position.

**Nothing was tuned to make this fire and nothing should be** (R12). The distance IS the answer, and
it confirms a finding PB2 already recorded from the other direction: *"a supplier holding this much
capital against a book this small is over-capitalised, and the published company is small because it
is a fixture rather than because it is poor."* R6 is the first thing to put a number on it.

**This is what SURVIVE now means**: not a binary, but £316,009 of distance to the first collateral
demand, on a book whose peak position is £19,607.

### 4a. CORRECTION 2026-08-29: the "accounts" row above was the wrong population

Left standing rather than edited, per the convention that a figure quoted and then corrected must
stay findable beside its correction.

**`accounts = 13` is the STATIC FOUNDER ROSTER**, read off `run_output.by_billing_account` — a
per-account detail view keyed off `saas.customers.CUSTOMERS`, resolved at import, which can never
hold an account the acquisition funnel won. It is not a census of anything and I read it as one.

Worse, the **code** was not using 13 either. `run_phase2b` passed
`accounts_held = len(_ALL_KNOWN_CUSTOMERS)` = **24**: the per-COMMODITY legs of that same static
roster. Wrong in three separate ways at once — every dual-fuel household counted twice against a
charge levied per *account*; not one funnel win visible; and no domestic/non-domestic or cessation
split, though SLC 27's capital regime is a domestic obligation on accounts actually supplied.

The population the collateral desk is entitled to see is **domestic billing accounts on supply at
the mark**, counted from the supplier's own settled record — 120, not 13 and not 24. The full
census of the six populations this repository publishes, the epistemic-wall question answered, and
why the commercial book (587) is the *growth* desk's correct answer and not this one:
`docs/design/ACCOUNT_POPULATION_CENSUS_2026-08-29.md`. Enforced by
`saas.capital.solvency.mcr_accounts_on_supply` and twelve mutation-proven controls in
`tests/company/risk/test_mcr_account_population.py`.

At the run current on 2026-08-29 (net assets £331,361.47, gross marked exposure £66,963.44):

| basis | n | MCR claim | free equity | headroom |
|---|---:|---:|---:|---:|
| what the code used | 24 | £3,120 | £328,241.47 | £261,278.03 |
| **correct** | **120** | **£15,600** | **£315,761.47** | **£248,798.03** |

**§4's conclusion is unchanged and I am not softening it: the mechanism is reached and does not
fire.** Free equity covers the exposure by 3.7× even on the corrected basis — it would still not
fire at the commercial book's 587 accounts (£188,088 of headroom). What changes is that the
distance is now denominated on a population with a name, and the repair moves the number in the
direction that costs the company, which is the direction a repair should be able to move. Free
equity was overstated by £12,480.

## 5. Two defects of my own, both found by printing the numbers at real inputs

Neither would have been found by reading, and both were in the same function.

1. **The feed keys were invented.** `close_out_move_fraction_from_history` defaulted to
   `settlement_date` / `price_gbp_per_mwh` — plausible names, the shape of a small internal feed
   elsewhere in the repo, and **absent from the live Elexon record**, which uses `settlementDate` /
   `systemSellPrice`. It parsed **0 of 165,386 rows** and returned `None` for every date in the
   decade. The call site turns `None` into NaN, which *demands* an independent amount from every
   counterparty. A control keyed to a structure that does not exist, failing loudly in the wrong
   direction and inflating every published margin figure. It now raises on a key mismatch, because
   that is our bug and must not read as "unmeasurable".

2. **The right keys gave an absurd number.** Worst 5-day moves of 310% (2017) rising to 681% (2025)
   — an independent amount of nearly seven times the position. Those are real moves in the
   BALANCING market, and **the position is not marked there.** The mark is an EWMA of daily means
   (`company/pricing/tariff_engine.py`), so the close-out move must be the move in that EWMA. Taking
   the half-life from the engine rather than restating it, the measured move is 15.2% by 2017 rising
   to 28.0% after 2022 — a plausible stressed close-out that rises through the crisis, point-in-time.

## 6. What R6 does NOT claim

**This is not a model of how GB domestic suppliers failed in 2021-22.** Ofgem's own Financial
Resilience Transparency Report, citing the Oxera review, gives the dominant root cause as the
opposite: suppliers that *"had not purchased energy in advance to 'hedge' their risk and could not
afford to buy energy at elevated prices"* — naked exposure, not collateral calls on a hedged book.
The collateral-drain mechanism is strongly evidenced one level up the chain (Uniper/Fortum, 2022).
R6 is the CMA's **growth** channel, a different claim about a different decade, and our own research
file warns in terms against building the death loop as if it were THE 2021 UK cause.

## WORK THIS CREATES

1. **The book the mechanism acts through is suppressed.** From 2018 the settlement engine booked
   ZERO of every year's wins (see the founder-book finding). Acquisition spend cannot weaken a
   balance sheet through a book nothing reaches, so the growth half of the CMA loop is currently
   throttled by a harness limit rather than by commerce. **This is the top item.**
2. **The £316,009 headroom is itself the PB2 finding, now priced.** Whether the published company
   should be capitalised at £337k against a 13-account book is a curriculum question and the
   director's; it is now askable with a number attached.
3. **The independent amount is binary once triggered** — the same demand at £98k of free equity as
   at £18k. A real counterparty asks more of a weaker name. Graduating it needs a credit-standing
   scale, which is exactly the band table this design refused to invent, so it waits for evidence
   rather than for a decision.
4. **B6 FRAME §1.10's three fail-opens are still open**, and are not touched here: a single
   non-finite mark still walks through `margin_call_book.py:194`, `:87` and
   `collateral_death_test.py:160` and returns "survived". R6 adds no fourth — an unreadable balance
   sheet DEMANDS rather than waives — but it does not close the three that exist.

## Where the work is

`company/risk/independent_amount.py` (new), wired through
`company/finance/margin_call_book.build_margin_calls_from_mtm(balance_sheet=...)` →
`company/risk/counterparty_collateral_desk` → `simulation/run_phase2b`'s live collateral call, which
passes the supplier's own treasury, account count and measured close-out move. 26 controls in
`tests/company/risk/test_independent_amount.py`, including the wiring assertion — an unwired credit
model is the R1 defect wearing different clothes.

`balance_sheet=None` reproduces the pre-R6 book exactly, and the seam's conformance test now asserts
that every figure the pre-cut sequence produced is bit-identical through the door, plus exactly two
declared new keys.

## Still live
