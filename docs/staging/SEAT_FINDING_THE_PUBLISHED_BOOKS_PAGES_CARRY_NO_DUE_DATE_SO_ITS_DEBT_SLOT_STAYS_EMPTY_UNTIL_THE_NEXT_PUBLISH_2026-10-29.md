**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The published book's pages carry no due date, so its debt slot stays empty until the next publish (2026-10-29)

**What is published.** The book in `site/data/customers` came from the 26 Oct auto-publish of the
run at 4ae8da9b0f. Its pages were exported before a bill carried `invoice_number`, `due_date` and
`document_type`. None of the 52,782 bills on its pages has a due date. The household summary's payment record
therefore counts no bill as due, missed or paid, and the debt slot's check cannot read a missed
payment from that page at all.

**Before this change.** The live cast (built 28 Oct by the older generator) showed SYN-2016-356 at
"Missed a payment" with "5 payments, 2 returned, 0 missed". That was the third cold read's
complaint, and it still applied.

**After this change.** Rebuilt over the same pages, the debt slot is empty. Its reason names this
cause: "its bills carry no due date, so its payment record cannot count a payment missed".

**On the published run's own inputs it fills.** The pages were rebuilt from that run's output
(`run_output_latest.json.gz`, stamped 4ae8da9b0f) with today's code, in scratch tree
`/var/tmp/onemiss/pubtree`, using `/var/tmp/third-read-scripts/pages.py`.
- 602 households match the debt rule; 157 pass every check.
- The slot fills with SYN-2016-592. Its record reads "93 of 97 bills paid, 0 returned, 4 missed"
  at its "Missed a payment" moment (29 Jan 2025), and the counters agree with every moment after.
- The cast fills 7 of 8 slots; only `storage_heating` is empty.

**Forty-five refusals remain on those inputs, all of one class, and it is not the definition.** In
all 45, the desk opened a journey on the 29th of a month while every bill on the page was paid on
its due date. The desk dated a bill differently from the billing ledger in that run.
9ad5af9a75 (28 Oct, after 4ae8da9b0f) gave the desk the billing ledger's due date. The 209c3350ab
book, built after it, shows none of this class.

**What closes it.** The next publish rebuilds the pages with due dates. Nothing to build: when the
publisher next runs, `ACCOUNTED_BY["debt"]` reports this entry as spent, and it should be dropped
along with this file.
