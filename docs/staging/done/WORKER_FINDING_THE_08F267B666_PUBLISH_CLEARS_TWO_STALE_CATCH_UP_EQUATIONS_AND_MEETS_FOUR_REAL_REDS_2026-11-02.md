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

## Done

*Delivery seat, 2026-11-03, claim `the-four-publish-reds-cleared-or-named`.* All four reproduced on
the 0a6391d186 book (the shared tree's ledger and `run_output_latest.json.gz`, 02:14Z / 01:47Z), so
they were re-asked there. Each was traced before a side was chosen.

| red | cause, traced | disposition |
|---|---|---|
| VAT, C5/110 and C5/113 (curtained and statement) | **Not a billing defect. The tests' equation was stale.** `_resolve_catchup` sums each month's own VAT difference, as §15 of `back_billing_and_liability.md` requires. C5/113: August was billed 1,266 kWh at 20% (40.8/day), the read put it at 882.2 kWh (28.5/day, 5%), so -31.50 + 5.62 = -25.88 to the penny. Splitting at the carrying bill's own rate, as this finding proposed, would have charged 22.50 of standard-rate VAT on a reduced-rate supply. | Both tests now grade the month's own VAT on its own lines, and the catch-up on its run (`catchup_vat_breach`): 6,431 of 6,431 catch-up bills pass. Mutation: the bill-rate split reds C5/113, and a 10p error reds 5,598 domestic catch-ups. C5/110's bill-rate split stays inside 5-20%, so the export alone cannot see it; the new unit pin `test_an_sme_catch_up_corrects_each_months_vat_at_that_months_rate_not_the_bills` holds the code path. |
| contracted tariff, 262 | All 262 are domestic catch-up bills on two-register meters. `_volume_by_label`'s multi-register branch priced each register's whole advance, which since 1bdd86b849 includes the catch-up's kWh. The one-register path and `_energy_per_register` already took it off. OCC-23ee23cb44e4 Apr 2022: 243.9 Day + -333.5 Night = 281.0 month + -370.6 catch-up. | Fixed in the validator: 52,612 agreed and 216 bounded, with 0 disagreeing and none moved to uncheckable. The unit test reds without the fix. |
| event walk, 253 | All 253 are occupier accounts, and every gap equals `total_deemed_gbp` to the penny. The ledger takes bills booked to the unnamed occupier's or owner's deemed account off the payer's balance. The statement walk had no event for them. The payment-ledger page already shows one. | `statement_export.account_events` now emits a `deemed_account` event, giving 0 of 1,293 disagreeing. There is a unit test with its mutation. |
| crisis IFRS 9 step-up, 0.33% vs 0.72% | The floor is right: Centrica's residential charge ran 1.1-3.1% of revenue in 2019-2025, and four suppliers 1.6-3.9% in 2023-24 (`bad_debt_provisioning.md` 3.2). The known cause is the world's payment draw, which has no price input (W2_38, finding of 2026-10-16). **But the committed 4ae8da9b0f book passes**, on one year-end: 2023 at 1.55% with 2022 at 0.32%. At end-2023 its pay-on-receipt debt over 90 days was GBP 9,335 against 3,348 on 0a6391d186, and its 2023 write-offs were 1,869 against 169. Both the code (debt-phantom fixes such as c144971dab and 54f76662d1) and the cast changed between the two books, so **I cannot yet say** whether that lump was defect-made debt or cast noise. | **Named, dated exception** in the test (filed 2026-11-03, retired by W2_38). It has a ceiling: it lifts a failure only at or above 0a6391d186's 0.3295%, a worse book refuses, and a book that clears the floor passes. A leg test proves the ceiling refuses. **Prediction, filed before the next fresh run:** on current code, the crisis-years IFRS 9 charge reads under 1.0% again, and no single year from 2022 to 2023 reaches 1.2%. |

`test_every_run_the_committed_dashboard_publishes_is_in_the_committed_ledger` is not one of the
four. It is the `{}` dashboard clobber, held by
`SEAT_FINDING_THE_0A6391D186_PUBLISH_PASSED_ITS_GATE_AND_WAS_REFUSED_ON_A_DASHBOARD_EMPTIED_MID_GATE_2026-11-03.md`.
