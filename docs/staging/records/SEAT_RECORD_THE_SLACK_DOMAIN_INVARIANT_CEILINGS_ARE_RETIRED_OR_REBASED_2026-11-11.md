**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Record: the five slack domain-invariant ceilings are retired (four) or re-based (one) (2026-11-11)

Lane-0 item `the-slack-domain-invariant-ceilings-are-retired-or-rebased`, handed off by dc3e7dfeb4's record
(`SEAT_RECORD_THE_D1_E1587EC5B_BOOK_IS_REFUSED_BY_THE_PUBLISHERS_GATE_SO_THE_ELEVENTH_READ_DOES_NOT_RUN_2026-11-11.md`,
"Slack ceilings, not touched here"). It serves step 4 of the director's ruling of 26 Oct (a breach blocks the publish or is
a named, dated exception). It does not discharge that ruling. The advisor file stays in the queue.

**Premise re-measured at draw.** All three cited commits are on origin/main. The five blocks were still in
`docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml` at dc3e7dfeb4, so the premise held.

**What "done" means here.** Each row answers the record's open question: does it read 0 because it was fixed, or
because the chain does not reach it? Then retire or re-base each row against that answer.

## The question per row: reached, or not?

Read from the publisher-gate reports of both books: `/var/tmp/tenth-read/tree/docs/reports/domain_invariants.json`
(068b5e3cc8) and `/var/tmp/eleventh-read/tree/docs/reports/domain_invariants.json` (e1587ec5b). The two books read
identically on all five rows.

| row | ceiling | checked | breached | decision |
|---|---|---|---|---|
| `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` | 1 | 1,302 | 0 | **retired** |
| `INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL` | 14 | 8,836 | 0 | **retired** |
| `INV_BACK_BILLING_ON_RECEIPT_FROM_ISSUE` | 16 | 560 (13 unbounded) | 0 | **retired** |
| `INV_CAST_TARIFF_LABEL_IS_THE_BILLED_TERM` | 42 | 47 (25 flagged) | 0 | **retired** |
| `INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL` | 4,610 | 1,248 | 19 | **re-based to 19, new class** |

Every row is reached: the checked count is far above 0. So a 0 is a measured 0, not a row the chain never reached.
The rule applied is keyed to that property, not to each `retired_by` text. A row that is reached and reads 0 on two
fresh books is retired, because a ceiling above 0 would only hide a regression. Two `retired_by` texts are not met in
the letter:

- **The revenue row** asked for a bound on an open run of under-estimates (class B, PROS-2017-0117), and that bound was
  never written. The account no longer breaches. If class B returns, the publish now refuses and the row is traced
  again. That is the fail-closed direction.
- **The carbon row** keeps a named residual for the panel's own shape: no true-up kWh in the months it reconciles. That
  residual reads 0 here.

Flags never refuse (`runner.gate` counts breaches only). The cast row's 25 flags are a separate matter: a default tariff
dated "since" its first whole bill. They are not part of this item.

## The re-offer row: N15's class is gone, and a different one is left

I ran the evaluator with its five-example cap lifted, in the eleventh read's scratch tree. All 19 breaches had the same
side, `no bill due since the previous offer`. In every one, the re-offer came 1 to 9 days after the journey's previous
offer, with no household bill falling due in between. None of them was a bill paid in its window. That was N15's class,
which the 4,610 ceiling was set for, and it now reads 0.

The 19, with the gap to the previous offer in days:

- PROS-2016-0092: 2018-04-25 (2)
- PROS-2017-0393: 2018-12-11 (3)
- SYN-2016-012: 2016-04-05 (5), 2016-04-12 (7)
- SYN-2016-048: 2023-11-18 (2)
- SYN-2016-070: 2016-06-15 (2)
- SYN-2016-206: 2016-05-26 (1)
- SYN-2016-256: 2022-11-12 (4)
- SYN-2016-356: 2016-11-12 (4)
- SYN-2016-360: 2016-09-13 (7)
- SYN-2016-380: 2022-06-21 (6)
- SYN-2016-406: 2019-02-05 (6)
- SYN-2016-512: 2018-02-15 (2)
- SYN-2016-519: 2017-10-10 (5)
- SYN-2016-538: 2023-03-28 (1), 2023-04-28 (3)
- SYN-2016-549: 2018-10-05 (3), 2018-12-25 (5), 2019-01-25 (9)

**The cause is not traced; I cannot yet say which explanation holds.** Two hypotheses are open:

- **(i) The row is too narrow.** In `company/billing/collections_journey.py` (`advance`), the desk's `missed` set also
  holds returned level-DD collections and missed closing or leg statements. The row's window counts only bills, so a
  lawful re-offer on a returned collection reads as a breach.
- **(ii) The desk is wrong.** It re-offers on a day it should not.

The exception is re-based to 19 as a defect, not an explanation. Its `retired_by` now names tracing the trigger day.

## The gate is unchanged on both books

Both books were re-gated against the new register using `runner.gate` and their saved results:

- **068b5e3cc8:** refused, 25 unexcepted across two rows (the overdue row, which D1 has since retired, and the closed
  account row).
- **e1587ec5b:** refused, 208 unexcepted across two rows (the closed account row and the refund row).

Each verdict is the same as before the edit. The edit adds no refusal and lifts none.

**Reverse:** restore the four blocks and the old re-offer block from git history.
