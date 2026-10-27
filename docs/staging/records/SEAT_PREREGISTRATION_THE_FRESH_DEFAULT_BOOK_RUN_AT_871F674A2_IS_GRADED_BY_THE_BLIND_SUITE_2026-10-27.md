**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION: the fresh default-book run at 871f674a2a, graded by the blind suite

Filed 2026-10-27 before launch. The predictions below are not edited after the run.

## The run

- **Code:** origin/main `871f674a2a`, run from a clean worktree `/var/tmp/se-fresh-run-871f674a2`.
  It contains 00c082202, 58af1fe57, 3e19e5676, 8e9fb022d, 36ce8dc53, 871f674a2 and f89db6ff3.
- **Configuration:** the same as Monday's 4ae8da9b0f run: default book, default `CURRENT_POLICY`, no
  `SE_POPULATION_SEED` override, `report_end=None`. Script `/var/tmp/fresh-run-scripts/arm.py` is
  Monday's `arm.py` unchanged; it pickles to `/var/tmp/fresh-run-out-871f674a2/`.
- **Resource:** Monday's equivalent run took 56 min wall and peaked at 5.5 GB. No run was live at launch.
- **First run to carry f89db6ff3's monthly fields.** Any difference from the 67a893e749 book that
  those fields explain cannot be separated from the fixes by this run alone.
- **Grade:** rebuild the ledger and the raw export with origin code
  (`/var/tmp/fresh-run-scripts/build_ledger.py`, `export_raw.py`), run
  `tools/domain_invariant_runner.py` over every household, append the per-invariant table to
  `SEAT_FINDING_THE_BLIND_INVARIANT_SUITE_ON_THE_67A893E749_BOOK...2026-10-26.md` beside this file's
  predictions. Each breach is fixed or recorded as a named, dated exception.

## Predictions (reference book: 67a893e749 arm A, 1,291 accounts)

| Invariant | Was | Predicted | Which commit predicts it |
|---|---|---|---|
| INV_UNIT_RATE_SVT_ELEC | 496 | **0** | 58af1fe57 (prepayment priced at the prepayment cap) |
| INV_UNIT_RATE_SVT_GAS | 462 reported by that commit | **0** | 58af1fe57 |
| INV_STANDING_CHARGE_SVT_ELEC | 2,986 | **0** | 00c082202 |
| INV_STANDING_CHARGE_SVT_GAS | 4,226 | **0** | 00c082202 |
| INV_READ_MONOTONIC | 29 | **0** | 8e9fb022d |
| Register ids carrying two labels | 39 | **0** | 8e9fb022d |
| INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER | 501 | **0** | 36ce8dc53 (classed by printed registers) |
| INV_PPM_NOT_CREDIT_BILLED | UNCHECKABLE | **runs; 1 account (the SME leg) breached, 0 domestic** | 3e19e5676 / 871f674a2 (document type now exported) |
| Serials switching register count (one to two) | 66 | **about 66, not 39** | 8e9fb022d fixed ids, not counts: the count follows the term (SLC 28AD), so it should not move |

Where "39" appears: it is the earlier count of ids carrying two labels, not the serial-switch
count. If the grade reads 39 serials switching, that is a refutation of "unchanged" and is reported
as one.

Not predicted, reported as found: INV_PAYMENT_AMOUNT_SIGN (83 before; 871f674a2 says its Nones were
two source defects, so I expect fewer but cannot size it), INV_PERIODS_CONTIGUOUS (1 before; no
landed commit addresses it), INV_VAT_RATE, INV_NON_COMMODITY_WITHIN_ALL_IN and
INV_PERIOD_MATCHES_READS (now in the export; no prior count).

## Done means

Every row above is graded against the table; every breach is fixed or a named dated exception.
This is the ruling's exit test: the suite runs on the full book of a fresh run with zero
unexplained breaches.
