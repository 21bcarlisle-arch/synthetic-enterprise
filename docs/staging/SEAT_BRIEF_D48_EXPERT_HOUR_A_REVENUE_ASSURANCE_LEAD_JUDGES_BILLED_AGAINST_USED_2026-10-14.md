**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** none -- a brief for a blind review of a built capability; the knowledge note it rests on is W2_36's first file, and the published figures are site/data/billing_accuracy.json

# D48's Expert Hour, ready to run: a revenue-assurance lead judges billed against used (2026-10-14)

**Fate (2026-10-14):** ATOM -- D48 is at L2, loop_stage harden (ec0c00917); this brief is the harden step's input, drawn by the ordinary loop.

D48 recorded L2 on the published /capabilities/ figures (ec0c00917), and the live site serves them.
Harden is a blind review, run as C32's was (tools/blind_review.py, priors first, the builder's
context withheld until adjudication).

## 1. Run it (blind)

```
python3 tools/blind_review.py --packet D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used \
  --domain billing \
  --persona "GB revenue-assurance lead who has run billed-versus-settled reconciliation at a domestic supplier" \
  --plain-words "$(cat <this file's section 2 text>)"
```

The packet renders as accepted (checked 2026-10-14). The restatement is recorded as `restated`.
Then `--record` the battery the reviewer writes.

## 2. The plain-words restatement (blind-safe: no code names, no results)

Each month the supplier compares what it billed each household against the energy the meter later showed was used, by kind: bills on estimated reads versus actual reads, the true-ups when an actual read arrives, any undercharge it may no longer recover because it is more than a year old (back-billing), and the energy used but not yet billed at the month's end (the accrual). It reports, from what a real supplier can see: the share of billed electricity and gas that was estimated, the size of the true-ups each year, the share of undercharge it is barred from recovering, and the share of its customers who have had no bill on an actual read in the last twelve months, set beside the published figure for the median GB supplier with a confidence interval. Electricity and gas are reported separately.

## 3. Shown only AFTER the reviewer's priors and battery are recorded

These are the live figures (run_output_2248e3baf_20261013T134447Z, poesys.net/data/billing_accuracy.json):
- **Estimated share of billed kWh: 66% electricity, 65% gas.** The parking finding expected a
  revenue-assurance reader to go to this first; it quoted 58% on an older run. Slice 4 attributed
  the level to the world's flat gas-heated homes. Re-ask that attribution at 66%: it has not been
  re-measured on this book.
- **No bill on an actual read in 12 months:** electricity 6/195 = 3.1% (95% 1.4-6.5%), gas 7/113
  = 6.2% (95% 3.0-12.2%), against the published median supplier at 5.2-5.6%. Neither can be told
  apart from it.
- K1 year-end true-up grades and K3 barred share of undercharge, by year, in the same file.

## 4. Adjudicate against the code, not the description

company/billing/billing_accuracy.py, site/test_the_billing_accuracy_reaches_the_reader.py (8/8 on
the live feed), and W2_36's knowledge note. Confirm or refute each MAJOR in a table, as C32's
finding did. The level moves to L3 only if no MAJOR is confirmed and live. A confirmed one is
fixed or parked with its reason, and the level stays at L2.
