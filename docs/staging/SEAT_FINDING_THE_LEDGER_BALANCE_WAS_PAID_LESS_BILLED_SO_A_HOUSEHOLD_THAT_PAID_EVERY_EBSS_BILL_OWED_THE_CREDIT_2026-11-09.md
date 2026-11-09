**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The ledger balance was paid less billed, so a household that paid every EBSS bill owed the credit (2026-11-09)

*Delivery item `page-balance-omits-credit-on-closed-accounts`. Correctness stretch (director ruling,
26 Oct): the page printed debt nobody owes.*

## What it was

`docs/state/billing_ledger.json` carried each account's `balance_gbp` as `total_paid - total_billed +
total_deemed`. The account page (`tools/generate_payment_ledger_data.build_account_ledger`) walks the
same record and gets a different number, so one balance had two homes. The customer page
(`generate_company_data`), the shadow HTML "Balance" line and the dashboard's per-segment working
capital read the first. `company/billing/statement_export` re-walked it and agreed, because it had the
same omissions. The formula missed:

1. **The EBSS credit.** A credited bill is paid net of the credit, so every credited month stood owed.
   PROS-2020-0022 paid every bill and printed GBP 407.34 in debit. GBP 400 of that is the scheme credit
   and GBP 7.34 is what the desk wrote off.
2. **Repayments, resolutions, write-offs and Reg 6D refunds.**
3. **The book's date.** Payments dated after the book's last issue were counted (SYN-2016-382: GBP 275.28
   paid on 18 Jul 2025, against a book dated 4 Jul).
4. **A deemed bill's credit.** A bill booked to the deemed account was taken off net of its EBSS credit,
   so the payer owed the credit (OCC-25ff8966357a: GBP 134.00).

The page itself had one omission of its own: **a part payment on a failed collection that opened no
case was dropped.** A level DD can be part paid with nothing short, so no case opens. OCC-cede70b10116
INV7336 had GBP 52.46 received and printed as owed. 11 accounts on the 4dee9854a4 book have this shape.

## What changed

- `balance_gbp` is now the page's own closing balance, negated so the field keeps its sign (negative
  means owed). It is stamped with `balance_as_of_date`.
- The page posts a part payment whether or not a case opened.
- The statement walk now posts:
  - the credit;
  - the case stages that move money;
  - refunds;
  - the whole deemed bill;
  - nothing dated after `balance_as_of_date`.

Knowledge: `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "What is owed" and "A bill
the Energy Bills Support Scheme credit covered"; `energy_bills_support_scheme_delivery.md` (the
credit goes to the account).

## Graded on the 4dee9854a4 book (/var/tmp/grade-ondd/ledger.json), new code over the same records

| | before | after |
|---|---|---|
| statement walk vs stored balance, accounts disagreeing | 0 (both wrong together) | 0 of 1,302 |
| statement walk vs the page | 52 of 1,302 | 0 of 1,302 |
| accounts whose `balance_gbp` moves | | 640 |
| sum of debit balances (what the page says is owed) | GBP 198,701.22 | GBP 59,575.75 |
| PROS-2020-0022 | -407.34 | 0.00 |

**Published figures that move on the next ledger regeneration:**
- every customer page's balance;
- the dashboard's per-segment working capital, and so the ROCE that divides by it, which falls because
  credited months and written-off debt are no longer receivables;
- the shadow HTML balance lines.

The committed ledger (run 0a6391d186) is **not** regenerated in this commit: the publish owns it. Until
it is regenerated, the walk-closes test checks the walk against the page on every account, and checks the
stored figure only where the ledger declares `balance_as_of_date`.

## Open: the desk's write-off never reaches the page

This is the residue of the item's own measure: written-off accounts printing a balance. Of 152 accounts
the desk (`collections_desk_journeys`, stage `write_off`) wrote off:

- 120 still print a balance owed after it, GBP 20,566.56 in total;
- on 121 of them the page posts **no** write-off, or less than the desk's, GBP 17,782.71 in total.

The page posts write-offs only from the engine's per-invoice cases (`arrears_history` `WRITTEN_OFF`).
The desk's account-level write-off of a closed account ("closed_account_unpaid_a_year_after_its_final_bill") is a
company decision the page never shows. C2 (desk 219.57, page owed 272.62), C3, C7 (66.67 / 48.55) and C9
are in this set. It is not fixed here. Posting it needs a rule for splitting one account-level write-off
across two fuel legs, and a rule for what happens when the desk's figure and the page's balance differ
(the C7 level-collection gap, `58869f0f33`). It is the next piece of this item.
