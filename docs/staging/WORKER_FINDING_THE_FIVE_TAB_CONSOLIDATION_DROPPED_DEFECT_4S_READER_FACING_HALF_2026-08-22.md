**Severity:** LATENT · **Lane:** D_billing_metering

# The five-tab consolidation dropped Defect 4's reader-facing half, and the only check that would have said so was itself deleted by the same commit's fallout.

Filed 2026-08-22 while clearing the 34 FileNotFoundError entries in the 2026-08-22 HEAD-green
census. It is filed rather than fixed because the fix is a SITE content decision — where a
reader-facing explanation belongs on the five-tab site — and this pass was a weekend
budget-conservation pass with a scope of "clear the census, change nothing else".

## What was found

`03dd8c49e` (2026-08-20, the director's own commit: *"eleven pages deleted, their content moved"*)
deleted `site/customers/index.html`. The ruling records `customers -> Explore, which supersedes
it`, and states plainly that *"the URL and the content do not always agree, which is the point"* —
so supersession was never a promise that every element made the trip.

One element did not. `BILL_CORRECTNESS_ADDENDUM.md` Defect 4 has two halves:

1. a DATA invariant — billed total is never less than gross margin for any real customer-year; and
2. a READER-FACING requirement — *"define what annual_pnl gross means"* somewhere a reader can see
   it, which the deleted page satisfied with a reconciliation note in its Accounts tab.

Half 1 is intact and still tested
(`tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`).
Half 2 is gone from the shipped site.

## The measurement, so nobody has to re-derive it

Run at 2026-08-22 over the working tree, against `site/**/*.html`:

- `"commodity trading margin"` — **0 files**.
- `"Billing &amp; Payments"` — **0 files**.

Both strings were the assertions of `test_accounts_tab_explains_gross_vs_billed_distinction`.
Neither appears on `/explore/` (the page the ruling names as superseding customers), nor on
`/capabilities/`, `/harness/`, `/knowledge/`, `/privacy/` or the home door. The only hit for the
looser term `gross` anywhere in the live site is `site/explore/index.html`, and it is not this
explanation. **Re-pointing the test at the superseding page was the preferred fix and was not
available, because there is nothing there to point at.**

## Why this was worth a document rather than a silent deletion

The test that asserted half 2 could not pass after 2026-08-20 and has been removed today, because
a test that reads a deleted file reports the deletion once per nightly census for ever and masks
real regressions behind a permanently-red count. But the other guards removed in the same sweep
were MIRRORS of a Python port kept alongside them — losing those cost redundancy only. This one
was different: it was the sole check on a requirement with no other coverage, so deleting it
quietly would have converted a live requirement into no requirement, with the deletion looking
identical to the harmless ones in the diff.

That asymmetry is the finding. The removal is recorded in a comment at the test's former site in
`tests/tools/test_bill_correctness_addendum_defect4.py`, which names this document.

## What this document is asking for

Decide where the gross-vs-billed reconciliation note lives on the five-tab site — most likely
Explore, which is the door that took over the customer-facing surface — write it there, and
restore a check in `test_bill_correctness_addendum_defect4.py` pointing at its new home. If the
director's view is instead that the note is surface the consolidation was right to drop, record
that and amend `BILL_CORRECTNESS_ADDENDUM.md` Defect 4 so the requirement stops existing
explicitly rather than by attrition.

Archive to `docs/staging/done/` when either has happened.

## Related, not claimed as fixed here

The same sweep found that `test_site_structure.py`'s expert-door mobile-pass guard had been
reading a hand-kept list of six doors — `company, proof, world, method, glossary, tours` — **all
six of which `03dd8c49e` deleted**, so from 2026-08-20 until 2026-08-22 that control raised
FileNotFoundError on the first entry instead of checking any door that actually shipped. It has
been changed to derive its subject set from disk (every `site/*/index.html`), the same
allowlist-to-derived move `f5d8ffa96` made for the R14 basis gate three days earlier. That one IS
fixed in this pass and is mentioned only because it is the second instance of one class this week:
**a control whose subject set is a hand-kept list silently stops having subjects when the thing it
names is deleted.** A third instance would justify promoting it from instance to class.
