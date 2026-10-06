**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# D48: the billing-accuracy measure now has a reader, and the 12-month snapshot cannot be told apart from the median supplier

## What was wrong

`simulation/run_phase4c_on_phase2b.py` has returned `billing_accuracy` on every run since slice 1
(`2b8644248`). `saas/reporting/annual_report.py` builds the saved run output from that return, and
it never carried the key. So the published run output did not have it, and no page could show it.
D48 had four slices of measurement and no reader. Level 2 needs VERIFY evidence on a deployed surface,
so this was the gap that kept it at 1.

## What landed

- `annual_report.py` forwards `billing_accuracy` into the run output. It reads no field of it.
- `company/billing/billing_accuracy.published_view` decides what a reader meets:
  - per fuel: the K2 estimated share with its kWh, the undercharges and overcharges found at a
    read, and K3 barred energy with its count;
  - the K2 snapshot with a Wilson 95% interval, set beside the published median supplier;
  - the K1 year-end grades;
  - one named account.

  A missing or empty measure is published as an absence with its reason, never as zeros.
- `tools/generate_dashboard_data.generate` writes `site/data/billing_accuracy.json`. The publisher's
  `site/data/*.json` glob picks the file up.
- `/capabilities/` has a section for it, held by `site/test_the_billing_accuracy_reaches_the_reader.py`.
  Four mutations each turned the named test red, and the absence test stayed green through all four.
  The page's other eleven door tests now supply the feed.
- The comparator is `PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12`. Ofgem, *Decision:
  Protecting consumers from backbills* (2018) p.10, citing Citizens Advice, reports 94.80% and
  94.40% of consumers with a bill on a read in the past year at the 2017 median supplier. The
  constant is the complement of those two figures.
- The wall census gets one flat row and its nested pin, added by hand before the artefact has the
  key. A publish stages no `.py` file, so the census never checks it, and the widening would
  otherwise refuse the next unrelated `.py` commit (WORKER_FINDING_A_PUBLISH_THAT_WIDENS_THE_RUN_OUTPUT_IS_NOT_CENSUSED,
  2026-10-05). Until that publish, the row reads as paid down, which the baseline's rule tolerates.

## The reading, on slice 4's decade capture (`/tmp/d48s4/after.pkl`, 8,742 bills)

| | Electricity | Gas |
|---|---|---|
| On supply at 2025-06 with 12+ bills | 48 | 27 |
| No bill on a read in the last 12 months | 2 (4.2%, 95% 1.2% to 14.0%) | 1 (3.7%, 95% 0.7% to 18.3%) |
| Published median supplier, 2017 | 5.2% to 5.6% | 5.2% to 5.6% |
| Verdict | cannot be told apart | cannot be told apart |

The point estimates are below the median supplier. At 48 and 27 accounts, the intervals are about
ten times wider than the published band. **The book is too small to say whether this supplier's
read process is better or worse than a real median supplier's.** The page says so in words.

Two caveats are printed on the page:
- Accounts with fewer than twelve bills are left out, because a 12-month window cannot be read on
  them.
- The Citizens Advice measure counts all consumers, including the 2017 smart base and customer
  reads.

## Not done, and what is owed

- **The rendered value has not changed yet.** The run output the current publish read
  (`run_output_998814330_…`) predates the key, so the live feed is the named absence. The next
  publisher cycle writes the figures. When it does, D48's L1→L2 claim is that published page, and
  the level is recorded through `tools/level_promotion_gate.py`. It is not recorded before then.
- Per-supplier Citizens Advice percentages for 2016–2025 remain a GAP (note §2 K2). With them, the
  comparator could be a distribution rather than one median.
