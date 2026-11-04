**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The blind N15 row finds 11 "further bill missed" re-offers after paid bills on the b3ce2a4e73 book, where the fix predicted 0 (2026-11-04)

**Source.** `INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL` (`tools/domain_invariant_runner.py`, written blind from
`docs/market_research/company_debt_management.md`), run on `/var/tmp/fresh-grade-b3ce2a4e73/ledger.json`.

**What it counts.** Re-offers of the repayment plan where no bill of the billing account fell due since the journey's
previous offer, or every bill that did was paid in its window (cash issue..due inclusive on the leg, plus credit applied).

| Book | Breaches / re-offers |
|---|---:|
| 0a6391d186 (published) | 4,610 / 6,599 |
| b3ce2a4e73 (fresh, carries 6a3da3e48) | **11 / 1,241** |

The seat's own census of the same book read 0 of 2,224 (`records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_..._2026-11-04.md` (b)).
The two definitions differ in two named ways, so this is not yet a contradiction of the fix:
- **9 of the 11** are bills settled by `credit_applied_gbp` or a scheme credit. Counting cash only, the row reads 2 (both
  SYN-2016-021). The desk appears to treat a bill paid by credit as missed. The knowledge page says a bill is missed
  when it was not paid; a credit pays it. Candidate defect, not attributed.
- **The window.** The row opens at the previous offer ("further"); the census asked about bills falling due on the
  re-offer's day. SYN-2016-021 on 2023-09-18 is a re-offer with no bill due since the previous offer.

Examples: PROS-2021-0236 2024-08-22, SYN-2016-021 2023-09-18, SYN-2016-445 2023-02-19.

**Next.** Trace the 9 credit-settled cases against how the desk decides "missed"; if it reads cash only, the fix is to
count credit applied. The row's exception ceiling (4,610, N15) still holds the b3ce book inside it.

**Reverse:** delete this file.
