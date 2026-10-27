**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# A bill the EBSS covered in part was recorded as paid in full by the household (2026-10-27)

Open item (b) of the blind-suite finding's export section
(`SEAT_FINDING_THE_BLIND_INVARIANT_SUITE_ON_THE_67A893E749_BOOK_...2026-10-26.md`). Part of the
correctness stretch (`advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`,
step 4).

## Pre-registration (filed 2026-10-27 before the ledger was rebuilt on 4ae8da9b0f)

**What is counted.** A *part-covered bill* is an issued ledger bill whose payment row is not a credit
bill and whose month carries a scheme credit (`ebss_credit_gbp` > 0, so resi electricity, Oct 2022
to Mar 2023) smaller than the printed total. *Overstated* is the sum, over those bills, of the
credit the ledger's payment row includes as though the household paid it.

**Prediction**, from the knowledge page's £87.6k of winter credit on 989ce4f1c2 (a different run)
at about £66.5 a bill, less the 218 bills settled whole: **1,000 to 1,400 part-covered bills, £65k to
£90k overstated.** Outside that range means the page's figure does not carry to this book, or the
definition above misses bills.

## Result, on 4ae8da9b0f (ledger rebuilt from the same run file, before and after this commit)

| | before | after |
|---|---|---|
| part-covered bills | 1,100 (1,050 paid, 50 failed) | 1,100 |
| payment overstated by the credit | **£73,353.00** | **£804.00** (see residual) |
| scheme credit carried beside the payment | £0 | £72,549.00 |
| raw export: adjustments | £11,703.36 | £84,197.76 |
| raw export: payments dated Oct 2022 to Jun 2023 | £365,113.10 | £295,969.17 |
| account ledgers: total collected | £2,775,250.64 | £2,706,039.71 |
| account ledgers: identity breaks (billed = collected + scheme credit + balance + written off) | 0 | 0 |
| negative payments | 0 | 0 |

The prediction held: 1,100 is inside 1,000 to 1,400, and £73,353 is inside £65k to £90k.

On the failed bills, the export already sent only the part paid, so the export's overstatement was
the 1,050 paid bills. The ledger row overstated all 1,100.

**The residual £804** is 12 bills of £67 on three `OCC-` occupier accounts, January to March 2023.
They have no engine row: the engine collects nothing from a named payer for them. So no credit is
netted on the payment, which is still drawn in the ledger. Whether an occupier's deemed account
should carry the credit is a question for the engine, not this ledger. Named; not built.

## The company-balance question: no, the company itself was right

The engine already netted the credit everywhere the company keeps money:
- `arrears_engine._resolve_bills`, which drives bad debt and write-offs in the P&L;
- `dd_collection_book` at the bill's amount;
- `run_phase2b`'s held month, which is what the household budget weighs.

Each asks `owed_after_scheme_credit`. The ledger's arrears cases were built from the engine row, so
they were net too. Only the ledger's payment row copied the printed total. That row fed two things:
the raw export, and the household account ledger on Explore.

**On the account ledger, a second defect of the same cause.** The account ledger did not show the
credit at all. On a bill the credit settled whole (218 bills), nothing was received, so the bill
stood owed in the running balance for ever. On a part-covered bill, the whole bill was counted as
collected. Both now carry a `scheme_credit` entry, which lowers the balance and is not counted as
collected. The Explore page's ledger line prints the credit where it is non-zero.

## What changed
- `tools/generate_billing_ledger.py`: the payment is the bill less the credit, never more than the
  bill. The payment and the invoice carry `scheme_credit_gbp`.
- `company/billing/raw_account_export.py`: `scheme_credit_gbp` exports as an adjustment, and the rest
  as a payment. A ledger written before this change still reads correctly.
- `tools/generate_payment_ledger_data.py`: adds the `scheme_credit` entry and `total_scheme_credit_gbp`.
- Knowledge (K8): `docs/market_research/energy_bills_support_scheme_delivery.md`, "A bill the credit
  covered in part". Two GAPs are marked: the carry-forward rule, and the DD refund route.
- Three tests, each shown red on the old code and green on the new.
