**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `value-arms-error-bar` · **Status:** DESIGN, unbuilt ·
**Evidence:** `docs/market_research/how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`

# The write-off rule, re-keyed to the balance at close

**2026-09-27.** This is a design and nothing more. `compute_emergent_bad_debt` is not changed by the
commit that files it. The frame question is still open with the director as the practitioner
(`SEAT_FINDING_A_FAILED_BILL_IS_WRITTEN_OFF_IN_FULL_IFF_THE_CUSTOMER_EVER_LEAVES_2026-09-27.md`). Any
build waits for his answer or for his silence past the next seat orientation, whichever comes first.
**The case below rests on the evidence note alone, and no company result is used anywhere in it.**

## What the evidence changed about the frame

The finding recommended two rules: *"unpaid balance at close, plus persistent-arrears write-off for
stayers"*. The published record supports the first. It does **not** support the second as a
write-off clock. A stayer's aged arrears cost money through **provision**, and the only write-offs
of live accounts are external events: a regulatory scheme, a redress settlement, or the statute bar.
The design therefore has two legs, and the second one is a provision rather than a write-off.

There is also a wall reading the finding did not make. **A write-off and a provision are the
SUPPLIER's accounting acts, not facts about the world.** The world owns the cash truth: what was
paid and when, when the account closed, and what a collector later recovered. The decision to call
a balance lost is a judgement the company makes from things it can observe (the balance's age, the
payment method, live or final). Today the world makes that decision on the company's behalf and
writes the answer into the company's P&L records (`run_phase4c_on_phase2b.apply_emergent_bad_debt`).
This design keeps the build inside `simulation/` for now, so it is buildable without moving the
wall. It names the move as the eventual home of the loss decision rather than pretending the world
owns it.

## The rule

**World state, per customer account:** a running `unpaid_balance_gbp`, with the dates of each
contribution, replacing the per-bill terminal case.

1. **A failed payment adds to the balance. It is not a case.** A failed DD bill contributes its
   amount to the balance. The existing `payment_outcome` draw is kept as it stands; see C1 on what
   its "failed" means.
2. **The balance is paid down while the account is live.** Later successful payments and any
   repayment arrangement reduce it (C3).
3. **At close**, meaning a churned account's final bill: the balance still unpaid **after on-supply
   collection** is the final-account debt. Post-close recovery (the existing DCA / sale stages,
   whose constants are already flagged illustrative in `ASSUMPTIONS.md`) reduces it. **The remainder
   is the write-off.**
4. **A stayer** is never written off by this rule. Leg 4a: a balance is statute-barred six years
   after its last part-payment or acknowledgement (s.5 / s.29(5)). A paying stayer does not reach
   it, so this leg exists for completeness and is expected to fire rarely. **Assert it CAN fire
   before asserting what it does.** Leg 4b: the cost of a stayer's aged arrears is the PROVISION,
   and its rates are `None` (C6). Until they are sourced, a stayer's arrears cost stays at zero **as
   a declared gap, stated on every surface that differences leavers against stayers**, and not as a
   silent zero.
5. **`bad_debt_gbp` must say which quantity it is.** Ofgem's bad-debt charge is provisions plus
   write-offs. Until leg 4b has rates, the line is **write-offs only**, and its label and basis say
   so.

## Constants: each one sourced, or an honest None

| # | Constant | Value | Origin |
|---|---|---|---|
| C1 | Whether the existing `_DD_FAILURE_PROB` (3/12/35%) is the per-PRESENTATION failure rate or the rate after re-presentation | **None — GAP (2026-09-27)** | Minted unsourced in Phase MW (`c1e3e5105`) as "per payment event", copied into PP and QD. No published DD return rate (energy or economy-wide) and no source segments by income stress. `docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md`; what is missing: `SEAT_FINDING_THE_STAYER_PROVISION_RATE_IS_SOURCED_BUT_WHICH_BUCKET_A_FAILED_DD_STAYER_SITS_IN_TURNS_ON_C1_WHICH_HAS_NO_SOURCE_2026-09-27.md`. |
| C2 | DD re-presentation: count and window | up to 2 re-presentations, within 30 days, same amount; British Gas retries at +14d and stops the DD after a second failure | Bacs scheme rules as published by bureaux (Movimo, Access PaySuite); British Gas help page. **Sourced.** |
| C2b | Probability that a re-presentation succeeds | **None** | No published energy-sector cure rate. Bureau marketing figures are not a source. |
| C3 | Paydown of a live balance: weekly repayment on an arrangement | £6.01/wk electricity, £4.40/wk gas (Q4 2025) | Ofgem debt & arrears indicators via `company_debt_management.md` §2. **Sourced, but only for 2025.** Earlier years need their own quarters. |
| C3b | Share of arrears households on an arrangement | **None as a probability** | The published "~3/4 of debt BY VALUE has no plan" is a value share. Dividing it into a household probability is the two-counts-one-ratio defect. |
| C4 | Days from close to write-off | **None** | Supplier policy. Ofgem records it varies (Appendix 2 Dec 2024 §2.22; CfI Apr 2023 §4.4). The write-off YEAR still needs a date, so the build must pick a convention and label it as a convention (recommended: the final bill's due date, which is the latest point the world's own cash truth fixes). |
| C5 | Order of DCA placement and write-off | **None** | Published practice places DCA referral before write-off (60–90d after internal fail); the sim runs it after. The record does not settle this either way. |
| C6 | Provision rate on live arrears by age × method | **Rates SOURCED for one supplier (2026-09-27); application to a stayer NOT, so still None in code** | Centrica ARA 2025 Note 17: live DD >90d 7.4% (2024: 4.4%), live pay-on-receipt >90d 50.3% (54.6%), final bills 84.0% (85.6%); provision ÷ gross receivables at year end. Which bucket a failed-DD stayer sits in turns on C1 (net-of-retry ⇒ DD stopped ⇒ pay-on-receipt), a tenfold difference. Energy UK Fig. 5 still undefined (footnote: "Energy UK's analysis"). `SEAT_FINDING_THE_STAYER_PROVISION_RATE_IS_SOURCED_BUT_WHICH_BUCKET_A_FAILED_DD_STAYER_SITS_IN_TURNS_ON_C1_WHICH_HAS_NO_SOURCE_2026-09-27.md` |
| C6b | Closed-account provision rate | **None** | The DRS ~75% is a blend across methods AND account types for 2022–24 debt. It is a bound, not a closed-account rate. |
| C7 | Statute bar | 6 years from last part-payment / acknowledgement | Limitation Act 1980 s.5, s.29(5). **Sourced.** |
| C8 | Scheme / redress write-offs | not applied | DRS phase 1 launches in 2026, outside the 2016–2025 record. The British Gas 2023 redress is one supplier's settlement. Neither is a rule for our supplier. |

C1 and C2b block leg 1's re-presentation. The build does not need to wait on them: it can keep
today's draw and treat a "failed" bill as a balance contribution, which is the conservative reading
and a strict improvement on "terminal case". C2 is then wired only once C1 is settled.

## What the build must prove (for whoever draws it)

- **One-variable run:** change the rule alone and hold everything else still. Write the predicted
  direction on the selection residual BEFORE the run. The prediction: the leaver's write-off
  falls, because cured bills leave the total, and the stayer's cost is unchanged at zero, because
  leg 4b is a gap. The sign therefore moves toward retention. Let the run refute it.
- **Partition control:** in one fixture, one account reaches each of close-with-balance,
  close-cleared, stayer-with-balance and stayer-statute-barred. The rare leg is asserted reachable
  first.
- **Agreement control:** `tools.generate_billing_ledger` and the P&L must still agree by
  construction. The ledger reads the same balance, and does not re-derive it.
- `compute_debt_recovery` must key off the same closed-balance population.

## How to reverse

The rule is one function and its two consumers. Reverting the build commit restores today's
behaviour byte-for-byte. Nothing here is a one-way door.
