**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The 068b5e3cc8 book does not pass the publisher's gate: the scratch grade that said it did could not read the closed-account row (2026-11-11)

**Correcting 6fff2c257, beside its claim.** 6fff2c257 says the 068b5e3cc8 book "passes the gate through origin's
page": 0 unexcepted, 9 excepted, refuse False (`/var/tmp/grade-d1/control-068-at-3f74/grade.txt`). That grade came
from the scratch `grade.py` chain (`/var/tmp/grade-dca2-scripts/after_run.sh`), which builds page records in memory
and does **not** build `final_bills`. So `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` read **NOT_IN_EXPORT** there
(line 97 of that grade.txt). A row that cannot be read was counted as a pass.

**Measured through the publisher's own function.** I rebuilt the pages from the same book with the publisher's chain
(customer pages, ledger, invoices, payments, consumption, reaction chain, sample, customers.json, explore_cast, then
explore_hh_day and explore_carbon) in a scratch tree at origin 6fff2c2575 (`/var/tmp/tenth-read/tree`). Then I called
`background.process_run_complete._domain_invariant_gate_permits_publish("068b5e3cc8")` from that tree
(`/var/tmp/tenth-read/gate.txt`):

> PERMITS False … INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO 3 (3 breaches exceed the exception's max_breached 2)

1,688 closed fuel legs were checked; 3 breached, 89 flagged. Two of the breaches are the exception's named pair
(PROS-2016-0263g GBP 1.65, PROS-2017-0351 GBP 21.86). **The third is new: SYN-2016-493, GBP 11.56 of credit
unrefunded since its 30 Jun 2022 final bill.** Of the 82 rows, four were NOT_IN_EXPORT on the scratch grade and are
graded here. Three of them are clean or flagged (CAST_TARIFF_LABEL 47 checked, MISSED_BILL 28, ESTIMATE_RUN_WITHIN_TENURE
1), and the closed-account row is the one that breaches. Every other row's verdict and breach count match.

**SYN-2016-493's ledger, as a lead and not yet a trace.** Before the final bill the balance was GBP 24.46 in credit.
On 5 Jul 2022 the final bill was raised (GBP 26.13), leaving GBP 1.67 owed. On 14 Jul a "credit balance refunded on
closing the account" of GBP 12.90 was paid out, taking the debt to GBP 14.57. On 19 Jul the direct debit collected
the full bill face, GBP 26.13, leaving GBP 11.56 in credit. A close that nets the final bill against the credit would
have collected GBP 1.67 and refunded nothing. This looks like the exception's own class (a close refund sized apart
from what the final collection takes), but I have not traced where the GBP 12.90 comes from.

**Consequences.**
- The tenth cold read's book does not pass at origin's head. That read is graded as a read on a refused book; see
  `records/SEAT_READING_THE_TENTH_COLD_READ_ON_THE_068B5E3CC8_BOOK_2026-11-11.md`.
- The publish offer that 6fff2c257 filed (`run_complete_20261111T005928Z.md`) will fail closed at the publisher's
  gate on this row. Nothing wrong reaches the site.
- **Downstream.** `launch_d1_book.sh` grades the D1 book through the same `after_run.sh` chain, so a D1 book can be
  called a pass on the same blind row. The one-leg fix is to grade through the publisher's function on
  publisher-built pages (`/var/tmp/tenth-read/scripts/build.sh` then `gate.py`), and not through `grade.py`.

**What would retire this.** Either the exception is widened, with a reason, to cover the class rather than the two
named legs, once SYN-2016-493 is traced to the same mechanism; or the short refund is fixed and graded 0 on a fresh
book. Either way, the next "passes the gate" claim is made through `_domain_invariant_gate_permits_publish`.

## Reverse

Delete this file. Nothing outside `docs/staging/` is touched.

## SYN-2016-493 traced (2026-11-11, worker)

The GBP 12.90 is the walk's credit after a -42.56 credit bill (Feb 2018) was drawn against INV47681 at
its 42.87 face, while the level DD paid 31.00. The page then printed that 31.00 collection as 0.00. So
the walk was 42.56 short of the true credit (55.46), and the page was 31.00 short. The final 26.13 was
collected at face on 19 Jul, after the refund. This is not the exception's class. It is mechanism B of
home_moves.md §8.8c, fixed in the commit that adds this section. Through the publisher's gate on the
rebuilt 068b5e3cc8 pages, INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO reads **0 breached** (FLAGGED 87 of
1,687; it was 3 breached). The excepted pair, PROS-2016-0263g and PROS-2017-0351, also close at 0.00. So
once a fresh book confirms this, the exception can be retired. The gate still refuses on
INV_REFUND_WITHIN_THE_PAGE_CREDIT (12, residual named in the 205 finding). This stays BLOCKING until a
fresh book passes.

## Retired (2026-11-11 23:20, worker)

The fresh book has passed. The publisher's gate ran on the 6fe7827ab2 book (cab13bbd18, carrying s.8.8c and s.8.8d),
graded at 2e401fe1fc and published at e816040ce8. Its committed `docs/reports/domain_invariants.json` (git
6fe7827ab2) reads: INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO FLAGGED, **0 breached** of 1,687 (87 flagged);
INV_REFUND_WITHIN_THE_PAGE_CREDIT CLEAN, 0 of 176; refuse False, unexcepted []. The closed-account row is not in the
excepted list, so the pair the exception named (PROS-2016-0263g, PROS-2017-0351) closes at zero without it. The
exception's `retired_by` asked for a trace, a fix, and 0 on a fresh run. The trace is the section above, the fix is
cab13bbd18, and the 0 is this book. So the exception is removed from `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml` in
this commit. A future breach on this row now refuses the publish at 1, not 3.

Still open, and not part of this finding: `launch_d1_book.sh` grades through `after_run.sh`. That is the downstream
consequence named above. The 2e401fe1fc grade went through `grade_one.sh` and the publisher, not through the scratch
chain, so this retirement does not rest on it.

Reverse: restore the 19-line exception block from this commit's parent and move this file back to the staging root.
