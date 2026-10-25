**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` §8.8a

# A credit bill in the middle of an account's life is never set against the next charge

Found by naming the rows behind the 7 move-outs the ledger closes in credit (60 founder supply
points to 2020-12-31, budget 0, seed 42; probe `/var/tmp/credit_refund_probe/name_rows.py`, output
`/var/tmp/credit_refund_probe/r60/named.json`).

**What.** 5 of the 7 credits are a credit bill (`outcome == "credit"`, a negative bill) from the
middle of the account's life: SYN-2016-016g (−£14.54, Dec 2016), SYN-2016-018 (−£2.23, Nov 2017),
SYN-2016-032g (−£13.65, Jun 2017), SYN-2016-035g (−£20.54, May 2017) and SYN-2016-040g (−£6.21 in
Mar 2017, −£0.21 in Aug 2019). Each sat on the account until the move, for 5 weeks to about 2½ years.
In the meantime every later bill was paid in full. The other 2 are a negative final bill, and those
are right.

**Why.** `arrears_engine.balance_settlement_from_outcomes` sets a credit against arrears only (a failed
bill). A `success` row pays its bill in full, whatever credit is waiting.

**Why it matters.** A statement of account carries the balance forward (SLC 27.17). So a credit would
ordinarily come off the next bill's amount due, and the household would pay that much less. The run
instead collects the full amount and holds the household's money. Cash is overstated by the held
credits, and the closing credit is larger than it would be.

**I cannot yet say** whether the world or the bill is the right place to fix this. It could be the
payment truth paying "amount due" rather than the bill's charges, or the bill carrying a brought-forward
line. Practitioner check before building: do suppliers on a variable DD net a credit off the next
collection, and on a fixed DD hold it until the annual review?

## Done (2026-10-25)

**Correction, beside the claim above:** SLC 27.17 is the six-week final bill. It does not carry a
balance forward. The rules that do are SLC 27.16 (Credit is payments less ALL charges due under the
contract, a running account per fuel; refunded on request) and SLC 31H.12(a), (c) (the bill says what
is owed and what to pay). They were read in the consolidated licence text, pp.245-246 and 342-345.
That closes the "operative text not retrieved" gap in `what_a_supplier_holds_to_size_a_direct_debit.md`.

**Ruling (K8, `home_moves.md` s.8.8a, choices 11-13):** fix it in the walk, not the payment truth. A
paid bill on the same fuel's contract uses up the credit waiting on the account. The household pays the
charges less the credit, or nothing. `credits_applied` records the netting against the paid bill. The
billing ledger prints the smaller payment, and the payment ledger records no £0 "payment received"
for a bill the credit covered whole. The practitioner question (does a variable DD net a credit off
the next collection?) is not published anywhere I found. It is filed as GAP G8.13, and the build
follows the bill rule. A fixed DD holding the credit until review is choice 4's level-DD case, which
waits on DD3.

**Choice 12 is an equivalence, not a branch.** A credit waits only when nothing on its fuel is
outstanding, because it nets arrears first. So whether a credit-covered bill restarts the limitation
clock cannot matter. The first draft had a special case and a test for it. Both were removed.

**Measured** (60 founders to 2020-12-31, seed 42, budget 0; the before arm is a clean origin/main
worktree at fde0f7f0f7, the after arm the same plus this change; probe
`/var/tmp/midlife_credit_probe/name_rows.py`). Prediction filed before the run: 7 to 2 closing in
credit, the two negative final bills left, refunds 7 to 2, bad debt up by £0 or more.

| | before | after |
|---|---|---|
| Move-outs closing in credit | 7 (£118.62) | 2 (£61.24): SYN-2016-016 −£37.92, SYN-2016-022g −£23.32 |
| Refunds recorded (late) | 7 (1) | 2 (0) |
| Settled at close | 20 | 25 |
| owed_unrefunded / refunded_not_owed | 0 / 0 | 0 / 0 |

The prediction held. One account moved the other way, and that is the rule working:
OCC-6e59dd8b63e8g's £18.55 credit (Mar 2018) now comes off its next paid bill. So its Feb 2019
failure is owed in full, and it closes owing £80.00 rather than £61.45. *Correction to my own first
reading:* the "Bad debt £3,217.34" line, identical in both logs, is printed by `run_phase2b` and does
not read this walk. The walk's write-off for that account rises £18.55 by construction (s.8.8a
choice 1), but that line was not measured here.

**Named limits.**
- A repayment's excess credit is netted in the walk but not in the billing ledger's payment, because
  the ledger never showed that excess as money in. This is a known gap and was not widened.
- `generate_billing_ledger`'s success-bill netting has no unit test of its own. The payment ledger's
  part of it does (mutation-checked), and so does the walk (mutation-checked).
