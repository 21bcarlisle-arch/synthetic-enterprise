# The renewal price now charges a clean prepayment household more than a clean direct-debit one

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-company-default-belief-is-measured-against-its-own-ledger` (Lane 0 delivery)

**2026-10-03.** Found while wiring the company's book-learned default belief into the value rule.

## What is true at origin/main (`e69dbbfe5`)

`tests/company/pricing/test_the_price_rests_only_on_observables_a_supplier_may_use.py` is **red at
HEAD**. It fails on two tests, and neither is on `HEAD_RED_REGISTER.md`:

- `test_the_price_rests_only_on_declared_supplier_observables`: `decide_margin` prices against
  `billed_last_year_gbp`, `payment_method` and `unpaid_bills_by_age`, and none of them is declared.
- `test_payment_method_cannot_reach_the_price_at_all`: `value_based_renewal.py` mentions
  `payment_method`, `prepay` and `prepayment`.

Both came in with `e0370bf94` ("the renewal price reads payment history"). Its gate selected
controls by module stem and this file's name does not carry the stem, so the gate never ran it.
Reproduced in a clean worktree at `e69dbbfe5`: 2 failed, 4 passed.

**The control guards a director ruling.** Its docstring quotes it (2026-09-23): declining on payment
behaviour, credit position or arrears history is ordinary practice, but "shifting cost onto
prepayment customers, isn't". The control refuses that by construction: payment method may not reach
the price.

## The cost-shift, measured

`decide_margin`, value arm, 2,700 kWh, tenure 2 years, cost to serve GBP 60, standing charge GBP 99.
No unpaid bills, and a year's billing on the ledger. Only `payment_method` changes:

| current / base rate (GBP/MWh) | direct debit | standard credit | prepayment |
|---|---|---|---|
| 215 / 205 | 106.50 | 106.50 | **108.50** |
| 300 / 280 | 156.75 | 156.75 | **159.50** |

The cause is mechanical. A clean DD or standard-credit account reads its own non-payment share, which
is zero, and that replaces the segment prior. Prepayment has no published live provision row, so its
share cannot be read and the 2% segment prior stands. Two households with the same clean record are
priced GBP 2.00-2.75/MWh apart because of how they pay. That is the shift the ruling names.

## What this claim did about it

- `company/pricing/default_belief.py` learns the book's bad-debt charge **by arrears state only**,
  against a whole-book prior (2.0% of residential revenue, `docs/market_research/ASSUMPTIONS.md`). It
  has no payment-method argument. Method is used only to read each charge on its published provision
  row.
- Behind `DecisionPolicy.renewal_default_belief = "own_book"`, the price uses that rate in place of
  both the segment table and the persistence term. A clean prepayment household then pays what a clean
  DD one does. This is controlled by
  `test_on_the_book_rate_a_clean_prepayment_household_pays_what_a_clean_direct_debit_one_does`.
- The new parameter `default_belief_rate` also lands in the observables control's undeclared list.
  The argument for admitting it: it is a number the company computes from its own ledger about
  accounts in this arrears state, and the account's payment method cannot move it. The control file is
  NOT edited here. Editing it would make the landing gate run a file that is already red at HEAD, for
  reasons that are not this claim's.

## Not done, and why

The stock term (`receivable_provision_rates`) still picks its live row by payment method on either
switch setting. For a debtor, method still moves the price. Prepayment debt has no row, so it moves
the price down, not up. Making it method-free means a blended live row, which nobody has sourced. The
segment-table path also keeps the shift above. Both belong to `e0370bf94`'s owner and to the ruling's
owner. Recommendation, put to the director on NTFY: make `own_book` the default once the console
seat's probe has read it. That removes the shift for clean accounts. Then decide whether the stock
term may keep its per-method row. If it may, the control declares the three parameters with that
argument and turns green. If it may not, the stock term needs a method-free row.

## Resolved, 2026-10-03 (delivery item `the-renewal-price-honours-the-prepayment-ruling-at-default`)

The director decided the open question above (`docs/direction/DIRECTION.yaml`): the stock term's
per-method row may stay, and the control asserts the PROPERTY that no clean account is priced higher
for how it pays, on both switch settings. Done:

- **The control asserts the property.** `test_a_clean_account_is_not_priced_for_how_it_pays` runs
  `decide_margin` over 4 rate cases x 3 consumptions x 2019/2022/2023 x both
  `renewal_default_belief` settings, outside a run AND inside a run whose book has taught the company
  that the channels shop differently. A second leg does the same with `learn_price_response` on, and
  a third shows a DEBTOR's price still moves with method, so the property cannot pass because method
  reaches nothing. The word ban is gone. `payment_method`, `unpaid_bills_by_age`,
  `billed_last_year_gbp`, `default_belief_rate` and `stayer_default_rate_gbp_per_mwh` are declared,
  each with its argument.
- **The segment-table shift is gone.** `observed_non_payment_provision_rate` returns 0 for a clean
  year before it looks up a row, so a clean prepayment account no longer falls to the 2% prior.
- **The gate selects the control** for `value_based_renewal.py`, `default_belief.py`,
  `discovered_price_sensitivity.py` and `enriched_churn_estimate.py` (`SUBJECT_TESTS`, not a rename).
- **The flip is MADE.** `DecisionPolicy.renewal_default_belief` defaults to `own_book`. Both release
  conditions hold on origin/main: the director's (B8, `4e17d1247`, landed) and the item's (the
  Grading section of `SEAT_PREREG_THE_CHOICE_IS_HELD_DOWN_BY_A_TOO_STEEP_BELIEF_..._2026-10-03.md`
  is filled in). **That prereg's next re-run (the world's debt-objection draw) must take its
  objection-off baseline at or after this commit.** Its graded figures at `c822e470e` priced on
  `segment_table` with the channel in the price, so a comparison against them has three variables.

### A second, larger channel into the price, found by the property

Prediction, written before the in-run measurement: on `own_book` the bad-debt shift vanishes, but
since `4e17d1247` passed `payment_method` into the price's churn belief, a clean prepayment household
would still price HIGHER on both settings, through PB7's learned engagement factor and B8's
per-channel slope. **It held, and was larger than the cost term.** In a run whose book had learned DD
engagement 1.54 and prepayment 0.35 (synthetic book, 2023 renewal, 215/180 uncapped, learning off), a
clean household was priced at margin GBP 48 (DD), 108.75 (standard credit) and 160 (prepayment) per
MWh. With learning on, B8's slope, learned only where a channel has closed renewals, priced clean DD
up to GBP 2.75/MWh below clean prepayment with the cap binding. Outside a run both channels read
neutral, which is why the original check missed it.

**Fixed.** The price now reads a channel-blind belief (`enriched_churn_estimate(channel_blind=True)`):
engagement at the book's own 1.0, and B8's slope pooled over every channel
(`discovered_price_sensitivity.EVERY_CHANNEL`). B8 still reaches the price. The control asserts that
learning moves some price on the grid. The churn desk's own belief keeps the channel: the ruling lets
the belief hear it and forbids only the price. All three mutations fire: per-channel slope, slope
dropped, and `4e17d1247`'s channel restored.

**What I cannot yet say:** how many real renewals the channel moved. The magnitudes above come from a
book built to differ by channel. The real book's learned engagement by method was not measured here.
The next full run on this commit prices every clean account channel-blind whatever the book learned.

## On the real book: what the channel would have moved (claim `the-price-channel-blind-belief-measured-on-the-real-book`)

**2026-10-04 04:25 BST. Pre-registered before either full run started.**

**What is measured, and where.** "The default policy" does not price on the churn belief. Its arm is
`flat`, and `renewal_margin_uplift` returns before `decide_margin` is reached, so the channel cannot
move a price under it: the count is **0 by construction**, and that is not a measurement. The
measurement is on the value arm with its default switches (`VALUE_ARM_POLICY`: `own_book` default
belief, learned price response off), and again with B8 on (`VALUE_ARM_LEARNED_POLICY`). Both runs are
at `75c7d7b5f`, one seed, full decade, which is after `ba320e2d2`. Every `decide_margin` call is
answered as the run answered it (`channel_blind=True`) and then re-asked in the same process and the
same pressure-ledger scope with `channel_blind=False`. The shadow answer never reaches the run.
Script: `/var/tmp/channel_blind/measure.py`.

**"Clean" and "priced differently."** Clean means a resi renewal with `arrears_state == "no_debt"`
and no unpaid bills. Priced differently means the chosen margin differs by at least GBP 0.01/MWh. The
search lands on a GBP 0.25 grid, so in practice that means at least one step.

**What is already known.** A smoke run to 2018-12-31 had 59 decisions, 34 of them clean resi. Every
channel's engagement factor was exactly 1.0 and every B8 correction was 0.0, so nothing moved. The
channel can only reach the price once this book's own leavers have pulled a method's factor away
from 1.0. B8 learning starts in 2020.

**Predictions:**
- P1, value arm: of the clean resi renewals, **5 to 25** are priced differently over the decade. All
  of them fall in 2020 or later.
- P2, value arm: the mean absolute margin difference for a method is **below GBP 2/MWh** for every
  method. That is two orders of magnitude below the synthetic book's GBP 112/MWh.
- P3, value arm: the sign by method follows each method's learned engagement factor. A factor below
  1.0 means kept-channel prices higher. I do not predict which method goes which way. The prior is
  1.0 and only the book's leavers decide.
- P4, learned arm: more clean renewals move than on the value arm, **10 to 40**.

### Results (2026-10-04 05:20 BST)

The predictions above were written before any full run started. They were gated into local
commits at 04:08 (`695630e4c`) and 04:19 (`dc7938d9b`). The corrected runs that the grading uses
were launched at 04:34. Both runs used the code at `75c7d7b5f`: the
worktree was at `dc7938d9b`, which differs from it only in docs. Seed: the default book. Raw rows are
in `/var/tmp/channel_blind/{value_arm,value_learned}.json`. They hold one row per `decide_margin`
call, with both answers and every channel's engagement factor and B8 correction at that call.

**Two corrections to the pre-registration, made before results were read:**

- "Every channel's engagement factor was exactly 1.0" in the 2018 smoke was a misreading. By 2018
  the book had learned DD 1.026, SC 0.760 and PP 0.925.
- The first full value-arm run measured **0 of 70**, and that zero came from the instrument, not the
  price. The scorer stopped passing `payment_method` into `enriched_churn_estimate` at `ba320e2d2`,
  so flipping `channel_blind` to False alone is a no-op. The shadow now puts the method back, which
  is exactly the call `4e17d1247` made. Its first smoke after that moved 26 of 43, so the shadow can
  fire. The no-op run's log is kept as `value_arm_NOOP_SHADOW.log`.

| | value arm (`VALUE_ARM_POLICY`) | value arm + B8 (`VALUE_ARM_LEARNED_POLICY`) |
|---|---|---|
| value-arm decisions / clean resi | 168 / 70 | 173 / 71 |
| **clean resi priced differently** | **36** (26 up, 10 down) | **31** (24 up, 7 down) |
| by year | 2017 10, 2018 11, 2019 5, 2020 4, 2021 1, 2023 1, 2024 4 | 2017 10, 2018 9, 2019 5, 2020 2, 2021 1, 2024 4 |
| DD: n, mean signed, mean abs, range (GBP/MWh) | 54, +0.80, 1.22, -3.00 to +8.25 | 54, +0.25, 0.43, -1.75 to +2.00 |
| standard credit | 9, +3.97, 3.97, 0 to +21.00 | 9, +1.14, 1.14, 0 to +6.00 |
| **prepayment** | 7, **+1.86**, 1.86, 0 to +6.75 | 8, **+7.53**, 7.53, 0 to **+37.50** |
| GBP/yr at kept price, summed DD / SC / PP | +266 / +245 / +59 | +31 / +88 / +229 |
| none declined only with the channel kept | yes | yes |

Signed difference = kept-channel margin minus the margin the run actually charged. Positive means
keeping the channel would have charged that household more.

**Learned engagement factor by method** (the book's own value is always 1.000), read at the last
decision of each year:

| year | value arm DD / SC / PP | value arm + B8 DD / SC / PP |
|---|---|---|
| 2017 | 0.975 / 1.000 / 1.000 | 0.975 / 1.000 / 1.000 |
| 2018 | 1.026 / 0.760 / 0.925 | 1.026 / 0.760 / 0.925 |
| 2019 | 0.910 / 0.609 / 1.028 | 0.982 / 0.646 / 0.780 |
| 2020 | 0.913 / 0.586 / 0.991 | 0.986 / 0.619 / 0.679 |
| 2021 | 0.967 / 0.445 / 0.994 | 1.036 / 0.486 / 0.668 |
| 2023 | 1.018 / 0.364 / 0.988 | 1.084 / 0.401 / 0.653 |
| 2024 | 1.033 / 0.331 / 0.965 | 1.099 / 0.367 / 0.606 |
| 2025 | 1.077 / 0.247 / 0.996 | 1.149 / 0.275 / 0.594 |

In the learned run, B8's electricity correction for prepayment stays between -0.025 and +0.093 over
the decade. The pooled correction, which the channel-blind price reads, starts at +0.451 in 2018
and ends at -0.031.

**Grading:**

- **P1 REFUTED on both legs.** 36 moved, not 5 to 25. The first moves are in 2017, not 2020 or
  later. A factor of 0.975, which is 2.5% off the book, already moved 10 DD prices by GBP
  0.50-1.75/MWh. The value arm's optimum is flat enough that a small factor crosses a GBP 0.25 grid
  step.
- **P2 HELD for DD (1.22) and prepayment (1.86); REFUTED for standard credit (3.97).** The book
  learned that standard credit shops a quarter as much as the book by 2025, and one 2024 SC renewal
  would have been priced GBP 21/MWh higher.
- **P3 HELD, 36 of 36** on the value arm: every move went the way that method's factor sits against
  1.0. On the learned arm it held for SC and PP, and for 20 of 26 on DD. B8's per-channel slope
  breaks the factor-only rule there.
- **P4 REFUTED.** 31 is inside 10 to 40, but P4 said more would move than on the value arm, and
  fewer did. B8 is not an extra channel term stacked on top. It changes what the blind price
  itself reads, through the pooled slope, so the two policies are different books, not one book
  with more channel.

**What this says about the claim.** On the real book, the channel was never mainly a prepayment
shift.

- On the value arm alone it moved DD prices both ways, and charged standard credit the most.
- With B8 on, it charged prepayment most: +GBP 37.50, +17.75 and +5.00/MWh on three clean 2018
  electricity renewals, about GBP 229/yr between them. That is a third of the synthetic book's GBP
  112/MWh, on real households. It came from PP's B8 correction being 0.0 while the pooled one was
  +0.45.

So for any value-arm run on code from `4e17d1247` (2026-10-03 15:57) to `ba320e2d2` (2026-10-04
00:20), the prices of clean prepayment and standard-credit households were raised by the channel.
The size depends on the policy. Neither run had a household whose offer the channel took away
entirely.

`ba320e2d2` removed all of this, which is what the 2026-09-23 ruling asks for. Nothing here argues
for putting the channel back.

**What stays open:**

- One seed.
- The per-method learned factors move hard on a book with 7-9 clean SC/PP renewals in a decade.
  The SC factor reaching 0.25 is the book's own leavers, priced by a prior of CIM's width. Whether
  that is sound learning or noise is not settled here.
