**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The 08f267b666 publish: two stale catch-up equations are fixed, and four real reds still refuse it

*Worker tick, 2026-11-02, working the publish-gate wedge (RUNG 1). The site still serves the
4ae8da9b0 book from 26 Oct.*

## The refusal chain, in order

1. **behind_origin.** Cleared by 20:01 (the seat landed its stretch log); the episode closed at 20:23.
2. **Size.** `docs/state/billing_ledger.json` was 143.8 MB, over GitHub's 100 MiB limit. The writer
   is now compact (58d49405e2 and 5654fa2e7, merged in d15740fb2); this book's ledger is 91.2 MB.
   The durable gzip choice is filed LATENT in
   `WORKER_FINDING_THE_BILLING_LEDGER_OUTGREW_GITHUBS_FILE_LIMIT_AND_COMPACT_LEAVES_13_PERCENT_2026-11-02.md`.
3. **`test_every_real_period_exports_readings_that_reproduce_our_own_volume`**, 6,428 of 52,828.
   This was a stale equation and is fixed in f5b852ba4. Since 1bdd86b849 (E1/E3), a catch-up bill
   opens on the last estimated reading, so its advance is `consumption_kwh + catchup_kwh`. Every
   period reproduces to within 2.4e-11 kWh.

Re-attempted once by hand at 21:03 (marker stamped `publish-rearmed`). The size check passed, and
the hook chain refused on step 3.

## Run against the same book after those fixes (working-tree ledger, 21:3x UTC)

| test | on this book | cause |
|---|---|---|
| curtained `test_every_bills_vat_matches_the_rate_the_PUBLISHED_LAW_says_applies` | 6,219 -> **2** | Stale equation: a bill that prints `catchup_vat_gbp` carries its catch-up inside the VAT, and the base left it out. Fixed in this commit, keyed on that declaration (the committed 4ae8da9b0f book prints none and stays at 0). The **2 are real** (below). |
| statement `test_the_vat_charged_on_every_catchup_bill_matches_the_NET_base_across_the_real_book` | 2 "on neither" | the same 2 bills |
| statement `test_the_event_walk_closes_where_the_ledger_says_it_closes` | OCC accounts, e.g. OCC-00909e50a521 walk -102.30 vs ledger 0.00 | **not established** |
| `test_the_published_book_charges_its_contracted_tariff` | 262 disagree, e.g. OCC-23ee23cb44e4 2022-04 +55.51 | **not established** |
| `test_live_run_output_shows_crisis_step_up_ifrs9_charge` | crisis bad debt 0.33% vs pre-crisis 0.72%, floor 1.0% | real domain result, correctness stretch |
| `test_every_run_the_committed_dashboard_publishes_is_in_the_committed_ledger` | empty `run_history` | probably the working-tree dashboard without its committed ledger; re-ask on the publish's own tree |

### The 2 real VAT errors: C5 (profile class 3), catch-up bills

- **C5/110** (2016-06, undercharge). `catchup_adjustment_gbp` 187.08 carries `catchup_vat_gbp`
  37.41, which is **20%**, on a bill whose `vat_rate` is 0.05. `catchup_raw_delta_gbp` 224.49 =
  187.08 x 1.2, so the raw delta was split as gross at 20%.
- **C5/113** (2016-09, overcharge). Adjustment -45.02 and catchup VAT -25.88: the VAT is just the
  remainder of the -70.90 raw delta, not any rate.

At 31 kWh/day on this bill, and 13 kWh/day over the catch-up's four months, the domestic 5% rate
applies either way. The defect is in how the catch-up splits its raw delta into net and VAT when
the account is not domestic-classed. Look at the catch-up VAT split where `catchup_vat_gbp` is set
(the bill assembly behind `catchup_raw_delta_gbp`).

## Next

The four rows marked "not established" or "real" are correctness-stretch work under the director's
26 Oct ruling. A book that breaches them should not publish, and the gate is doing what he asked.
The site keeps serving the 26 Oct book until they clear or are recorded as named, dated exceptions.
