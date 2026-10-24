# Pre-registration: the shared rise billed at the notice, against the same rise recorded only

**Written 2026-10-24, before any run of this code. NOT LAUNCHED.** Claim
`c34-the-renewal-price-shares-the-value-advice-creates` (Lane 0, seat direction). The build is
writer 7 (`company.pricing.renewal_rate_chain.bill_the_shared_rise`), the desk's `rise_at_notice`
and the run's caller after `observe_roll`, behind `DecisionPolicy.renewal_rate_bills_the_shared_rise`,
which is off on every standing policy. Knowledge: `docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md` §4e.
The only numbers read so far are §4e's constructed table and §4a/§4d's published readings. No
decision from a run of this code has been read.

## The question, and what it cannot answer

**Q.** When the company bills the rise C35 prices, on exactly the renewals where C34 would advise,
does the world's staying response cost the company more than its own pricing assumed?

**What this pair cannot answer.** It cannot say whether value is created. The world delivers no
advice: no world mechanism gives an advised household the hazard cut or the saving the company
credits it with (§4e). So the billed arm charges a price rise and the household gets nothing for it.
**Any margin gain on the billed arm is a transfer (M2), and no reading of this pair may present it
as the price half working.** The household side is a loss by construction, and the record states
it as one.

## Arms

Both use the per-customer switches tool's harness (`tools/per_customer_switch_arms.py` pattern;
the arm is not yet added there), with the same seed, book, window and commit:

- **recorded** — `CURRENT_POLICY` with `next_best_action_decides_at_renewal` and
  `next_best_action_shares_by_retention_rise` on. The rise is priced and logged, and not billed.
- **billed** — the same, plus `renewal_rate_bills_the_shared_rise`.

One variable differs. The window is the full run. Only renewals from 2019 can carry a rise
(there is no published default before then).

## Predictions

- **O1, off arm unchanged.** `CURRENT_POLICY` at this build equals its parent byte for byte (`cmp`
  on the run output), over the short window to 2017-06-30.
- **O2, recorded unchanged.** The recorded arm equals the C35 records-only arm at the parent
  (`cmp`). Billing code that is off changes no row.
- **B1, reach.** Over 2019–2025, `shared_rise_log` bills a rise on **between 5% and 25%** of
  resi roll legs. The basis: §4e bills 1 in 18 at the median headroom and 12 in 18 at GBP 4 or
  more, and §4d refused 158 of 372 above the headroom. The roll leg alone carries less room
  than the household.
- **B2, every billed rate** lies in (struck, published default ex VAT], and every rise is between
  GBP 0.30 and 4.50 a month.
- **B3, the cost side.** Over the billed legs, the excess departures the billed arm shows over the
  recorded arm, as a share of billed legs, is **at most** what the published slope implies
  (0.0015 × 12 × rise per leg, summed). §4a measured the world's own slope at 0.00065, under half
  of that. **Refuted if** excess departures exceed the slope-implied count by more than the
  binomial 95% bound on the billed-leg count.
- **B4, transfer.** The billed arm's margin from billed legs exceeds the recorded arm's. Stated so
  that a refutation is visible, and graded as a transfer, not as value.
- **B5, the household.** The household side is negative on every billed leg (rise paid, no advice
  delivered). Reported as a sum, in GBP, with its count.

## What would refute the design, not just a number

- B1 under 1%: the roll leg's headroom is not what §4e's input reading says, or the churn belief
  puts nearly every account outside C34's reach. Either way the switch does nothing at scale.
- B3 refuted: the company's floor-twice rule is not a safe bound on the world's response. That
  is the one result here that would change the design.

## Not done here

Launching. The arm needs adding to the arms tool. The pair waits for a decision on whether a
transfer-only grade is worth an arm-hour before the world delivers advice (§4e GAP 10).
