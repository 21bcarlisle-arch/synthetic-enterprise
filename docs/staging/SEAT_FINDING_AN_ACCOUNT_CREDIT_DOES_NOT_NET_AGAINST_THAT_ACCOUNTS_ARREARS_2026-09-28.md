**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_payment_channel_dd_consistency_invariant`

# FINDING: a credit on an account did not net against that account's arrears

Claim `an-account-credit-does-not-net-against-that-accounts-arrears`. The draw's duplicate-work note
named a live claim with this same id. That was the draw's own write, not another piece of work, so
there was no disposition to take.

## The rule, from the published licence

SLC 27.16 (electricity and gas supply standard conditions; consolidated to 18 July 2022) defines
**"Credit" as "the amount by which the payments made by a Domestic Customer … exceeds the total
amount of Charges which is due and payable … under that Domestic Supply Contract."** A credit
therefore exists only NET of the charges due on the same contract. It is a single balance per
contract, and a credit on a contract that still has arrears is not a credit at all: it reduces the
arrears. The contract is per fuel, because each licence governs its own fuel's contract. So the
netting is per `(customer, commodity)`, never across fuels.

Nothing we hold says which of several outstanding bills a credit discharges. Where a running account
has no appropriation, the common law discharges the earliest debit first (*Devaynes v Noble*,
"Clayton's Case", 1816). The engine uses that rule, oldest first.

A credit note is the supplier reducing its own charges. The debtor has not paid anything, so it is
not an acknowledgment or part-payment under Limitation Act s.29(5), and it does not restart the
six-year clock.

A credit that finds no arrears waits on the account and nets against arrears that come later. SLC
27.16 refunds it only if the customer asks, and that request is not modelled.

## Pre-registration (written BEFORE the measurement; real run output of 2026-09-28T00:18Z, 10,681 bills, 155 credit bills)

- **P1.** Credit bills that net against at least some outstanding arrears on the same
  `(customer, commodity)`: **5 to 30**.
- **P2.** Total write-off (the engine and the ledger, which agree at £17,359.26) falls by
  **£100 to £1,500**.
- **P3.** Written-off cases that a credit clears entirely, so they are no longer written off:
  **0 to 10**.

## Measured: HEAD against this change, in one process

| run output | write-off before | write-off after | cases before → after | credit bills netted | GBP netted | cases cleared entirely / in part |
|---|---|---|---|---|---|---|
| 2026-09-28T00:18Z (shared tree) | £17,408.05 | **£15,201.69** | 187 → 160 | 101 of 155 | £12,811.32 | 27 / 10 |
| 2026-09-09 (committed, what the gate reads) | £13,535.68 | **£11,070.30** | 160 → 148 | 121 of 170 | £11,600.79 | 12 / 12 |

The ledger and `compute_emergent_bad_debt` agree to the penny on both runs, at £15,201.69 and
£11,070.30.

**All three predictions were REFUTED, and all in the same direction.** P1 said 5 to 30 credit bills
and the answer was 101. P2 said £100 to £1,500 and the answer was £2,206. P3 said 0 to 10 and the
answer was 27. I priced a credit as meeting arrears only when it arrived while arrears were open.
But a credit waits on the account, so it also meets arrears that come later: the median gap from the
debited bill to the credit applied is 258 days, the p90 1,170. Most of the £12.8k netted sits on
stayers' open balances, where it moves no P&L line.
Also: HEAD's own write-off is £17,408.05, not the £17,359.26 in `2bb03a094`'s message. `b33f08d2e`
removed the consumption floor and moved the held set in between.

## What changed

- `simulation/arrears_engine.balance_settlement(_from_outcomes)` returns the write-offs and the
  credits netted against each case. `balance_write_offs` is its first half, so its callers are
  unchanged.
- `tools/generate_billing_ledger` reads both. A case's `arrears_gbp` is what is still owed after
  credit, which every consumer that sums it (the payment ledger, the shadow page, the decision
  ledger) already treats as the written-off or open amount. `face_gbp` and `credit_applied_gbp`
  sit beside it, and `CREDIT_APPLIED` stages mark where each credit went. A case the credits settle
  in full ends on `CREDIT_APPLIED`, and its invoice reads `settled_by_credit`.
- **Interconnection defect fixed on the way.** At HEAD
  `test_a_held_bill_and_a_credit_bill_are_never_written_off` was RED: `b33f08d2e` dropped the resi
  floor, so its 0 kWh "held" fixture was issued. The fixture is now held on footing, and the test
  asserts the gate holds it.
- Controls: one partition test over cleared in full, netted in part, carried forward, and the other
  fuel left alone; tests for oldest first and for the limitation clock; and a real-book leg asserting
  that a `CREDIT_APPLIED` exists. Mutations that fire: no netting (3 red), no carry-forward (1),
  pooling the fuels (1), a credit restarting the clock (1), newest first (2), and the ledger printing
  the face amount (1). **Equivalent:** dropping the fuel filter on the credit loop fires nothing,
  because `_net` draws from a pool keyed by the item's own fuel. The property lives in the pool key,
  and mutating that key is what fires.

## Residual, named

- **For a practitioner (the director).** A £194 credit from November 2018 waits on SYN-2016-021's gas
  account until arrears begin in March 2020. SLC 27.16 refunds only on request, so carrying it is
  what the licence text implies. Whether suppliers in practice refund a large idle credit at the
  annual DD review is not written anywhere I found. If they do, less of this credit would be
  available to net.
- A partly credited bill that stays open still reads `overdue` at its full face on the per-invoice
  surface, while the household balance is net of the credit.
- **Another red, not this change's.** `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py::test_the_vat_charged_on_every_catchup_bill_matches_the_NET_base_across_the_real_book`
  fails the same way at HEAD, with all five of this change's modules reverted: 774 catch-up bills
  against a literal floor of `>= 900`. It is a bound pinned to today's answer, and it no longer holds
  on the committed book.
- The same holds for `tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`:
  18 customer-years, identical with HEAD's engine and ledger, read from an on-disk artefact.
- **The landing door.** The first attempt was refused as `predates_landing`, because the ledger rewrite
  dropped 2bb03a094's two `"stages": _arrears_stages(amount, ...` lines. The hunk now keeps HEAD's
  two branches verbatim and rebinds `amount` to what is still owed, which is also the smaller diff.
  Post-close recoveries agree too: £2,279.10 in the ledger and the engine.
