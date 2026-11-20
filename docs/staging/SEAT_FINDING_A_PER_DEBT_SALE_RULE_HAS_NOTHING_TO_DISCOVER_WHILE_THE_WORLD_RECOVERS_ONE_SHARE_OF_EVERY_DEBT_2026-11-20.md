**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# A per-debt sale rule has nothing to discover while the world recovers one share of every debt (2026-11-20)

Drawn item: `knife3-a-per-debt-sale-rule-from-the-companys-own-contact-history`. It asked for
`company/billing/collections_journey.sells_written_off_debt` to use a per-debt expected recovery,
built from the company's own ledger and contact records, instead of the book-wide
`PRIOR_POST_CLOSE_RECOVERY`. I measured the premise before building, and **the rule was not built.**

## What was measured (origin/main 22f1dfa987)

- **The world recovers exactly one share of every worked debt.** `simulation/arrears_engine.dca_recovered_amount`
  returns `arrears_gbp * post_write_off_recovery_share()[0]`. Its `archetype` argument is "accepted
  and not read". `post_write_off_recovery_share()` returns `(0.122, "1 - prov_coverage_final_bill_over_90d:
  Centrica ARA 2025 Note 17 ...")`. Nothing about the debt changes that share: not age, balance,
  contact, arrangement or leg.
- **A sale is also one price for every debt.** `debt_sale_price_share()` is one register value, `None` today.
- **The company's expected recovery is the same published figure as the world's realised one.**
  `PRIOR_POST_CLOSE_RECOVERY = 1 - 0.878 = 0.122`, and the world reads `1 - prov_coverage_final_bill_over_90d`
  from the same register row, so both are 0.122.

## What follows

1. Both options are linear in face value with constant shares, so the value-maximising choice is
   the same for every debt: sell all of them if the price is above 0.122, otherwise work all of them.
   In this world a per-debt rule can only match the book-wide rule or do worse. Whatever per-debt
   spread it estimated would be either learned (and then flat, because the world is flat) or asserted
   (an invented spread, which K-first forbids). Building it now would add a mechanism that cannot fail.
2. The book-wide rule cannot fail either. The company's belief and the world's truth are one number
   read from one source, so the world cannot defeat the company on this choice (the coupled-triad
   principle, `tests/test_coupled_triad_gate.py`). This is latent only because no sale price is wired.
   Once one is wired, the company is right about every sale by construction.
3. **World first (W7).** The per-debt company rule waits for a world where recovery after write-off
   varies with something a supplier can see. The world's recovery must also be drawn apart from
   the company's prior, not read off the same row.

## What evidence exists for per-debt variation (knowledge page s.7.7, amended in this commit)

- ESTABLISHED in direction, but not on this population: Energy UK Fig. 5 reports recovery of debt
  under 12 months old at 60%, 56% and 38% (2022-23 to 2024-25), and over 12 months at 31%, 15% and 9%.
  The definition is not disclosed, and the figures cover arrears, not written-off closed balances.
- ESTABLISHED in aggregate only: Centrica's recoveries of previously written-off receivables were about
  2-6% of a year's write-offs. No split is given.
- GAP: any published GB energy recovery after write-off, split by an observable (contact,
  arrangement history, balance or age). Also GAP: an energy debt-sale price split by "paying" versus
  "non-paying" portfolio. That this split exists is a practitioner point to research, not a number to pick.

## Handed on

`world-first-post-write-off-recovery-that-varies-by-what-a-supplier-sees` (sim lane, knowledge first).
The per-debt company rule is its successor, and it should not be drawn before then.

**Addendum (2026-11-20, a parallel draw of the same item).** Before this finding reached it, a
second draw had built and gated the company-side rule. It is held, not landed, at branch
`knife3-per-debt-sale` (9fcd4a53fa), for the successor to pick up rather than rebuild:
`cash_forecast_provision.post_close_cell` and `RollRates.post_close_recovery_for`,
`collections_journey.expected_post_close_recovery`, and a `sensitive` exclusion on
`sells_written_off_debt`. Six tests come with it, and three mutations each turn tests red. The
estimator learns per cell and shrinks to the book-wide figure, so in today's flat world it is
flat. That agrees with point 1 above. New evidence went to s.7.7. A broker's debt-sale material
says sellers exclude "accounts not eligible for sale due to sensitive circumstances" (TDX/Equifax),
so the vulnerability GAP is corrected. L.E.K. puts purchasers' collections at about 2x price, so
about 11-19p per GBP, which brackets 0.122.
