# Pre-registration: the eight cold-read invariant rows on the 2eeb3f0b3 book (2026-10-27)

**Item:** `the-eight-cold-read-rows-get-evaluators` (the director's correctness ruling of 26 Oct, step 4).
**Book:** `/var/tmp/fresh-grade-2eeb3f0b3/raw.json`, the raw export built from
`/var/tmp/fresh-run-out-2eeb3f0b3` by `/var/tmp/grade-2eeb3f0b3.sh` (1,291 accounts). No new run.

Written before any of the new evaluators ran on this book. What I had already seen, so nobody reads
more into the predictions than they hold: the export's field list per period and per account; that
every electricity period's `mpan` is 13 digits starting `10`, numbered in sequence (`1000000000116`,
`...117`, ...); and the histogram of `scheme_credit` adjustment amounts (1,319 rows: 747 at £67, 356 at
£66, and about 45 odd amounts, many appearing exactly twice). I had NOT computed a check digit or
matched one credit to one month.

## Which rows the raw export can grade

| row | gradeable? | why |
|---|---|---|
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | no | needs `region` and `contracted_terms.tariff_name`, neither exported. The MPAN distributor ID would give region, but every core here starts `10`, so it would say the whole book is Eastern: a reading, not a region. |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | **yes** | `adjustments.adjustment_reason == scheme_credit` with date and amount; the only scheme in the window is EBSS |
| INV_RENEWAL_NOTICE_42_TO_49_DAYS | no | needs `renewal_notices.date` (not exported; the decision lives in the company's log) |
| INV_OVERDUE_WITHIN_BALANCE | no | needs `periods.due_date` and a dated overdue/balance series; bill amounts are money the company worked out and are kept out of the export by design |
| INV_ESTIMATE_RUN_WITHIN_TENURE | no | the export is one fuel per account, so a run of estimated periods is a sub-run of that leg's own periods and the predicate holds by construction. An evaluator here could not fire. The defect class is in the page's counter, which is not in the export |
| INV_COLLECTIONS_EVENTS_ORDERED | no | needs `collections.events` (not exported) |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | no | needs a write-off adjustment with its reason, and `periods.due_date`. The export's only adjustment reason is `scheme_credit` |
| INV_MPAN_CORE_FORMAT | **yes** | `mpan` is on every period. The check digit follows the published algorithm (weights 3,5,7,13,17,19,23,29,31,37,41,43; sum mod 11 mod 10), written to the commons first |

## Predictions

**INV_MPAN_CORE_FORMAT** (unit: distinct electricity MPAN per account; 707 electricity accounts).
- The 13-digit and 10-23 legs: 0 breaches (every core seen is 13 digits starting `10`).
- The check-digit leg: the cores look numbered in sequence, not generated with a check digit, so
  about nine in ten fail by chance. **Predicted: 580 to 680 of about 707 breach.** If the generator
  does compute a check digit, the count is 0 and this prediction is wrong.

**INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23** (unit: domestic credit-paying electricity account-month
on supply, Oct 2022 to Mar 2023; prepayment accounts are the row's own GAP and are not graded).
- Gas leg: the odd amounts appearing exactly twice look like one household's credit split across
  two accounts. **Predicted: 10 to 40 credits on gas accounts.**
- Electricity leg: shortfalls where a credit only part-covered a small bill on a ledger written
  before the split, and joiners and leavers whose month is part-supplied. **Predicted: 30 to 120
  account-months breach.**

Each breach is traced to a cause and either fixed or filed in `DOMAIN_INVARIANT_EXCEPTIONS.yaml`
with that cause. The grade is written beside this file when it is known, and is never edited into the
predictions above.

## Grade (written after the run; the predictions above are unedited)

`python3 -m tools.domain_invariant_runner --raw /var/tmp/fresh-grade-2eeb3f0b3/raw.json`:

| row | predicted | found | verdict |
|---|---|---|---|
| INV_MPAN_CORE_FORMAT, format legs | 0 | 0 | held |
| INV_MPAN_CORE_FORMAT, check digit | 580-680 of ~707 | **637 of 707** | held |
| INV_EBSS, gas leg | 10-40 credits | **0** | **wrong**: the paired odd amounts are not one credit split across two fuels |
| INV_EBSS, electricity leg | 30-120 account-months | **291 of 2,295** (132 prepayment months not graded) | **wrong**, more than double the top of the range |

The six rows the raw export cannot grade are UNCHECKABLE, each naming its missing field
(`missing_export_fields`).

### Causes, every breach

**MPAN, 637.** `tools/generate_billing_ledger._mpan` is `"1"` plus the sum of the account id's
character codes, zero-padded. So it carries no check digit, every core reads distributor 10, and it
**collides**: 707 electricity accounts share 158 MPANs, 71 of them shared, one by 34 accounts. Two
households on one supply point is a defect no row tests yet. The same idea has two other homes:
`company/crm/customer_registry._mpan` (a byte-identical copy) and `tools/generate_customer_data._mpan`.
The last is a third design: an 11-digit bottom line with an 8-weight check digit, which is the
11-digit `19494047720` the cold reader saw (O31). One identifier, three implementations: the VAT
rule's shape. Fix: one home producing a unique 13-digit core with a valid check digit, then rebuild
the ledger. Filed as an exception until it lands.

**EBSS, 291.** The world credits the whole instalment every month
(`company/interfaces/bill_assembly.owed_after_scheme_credit`). A credit larger than the bill leaves
the account in credit, carried forward. The export does not show that. It carries the credit only
as the ledger's payment row records it:
- **177 short by an odd amount:** the ledger records `min(credit, printed_total)`
  (`generate_billing_ledger`, `scheme_applied`), so a £49.32 bill exports a £49.32 credit. The other
  £16.68 was credited and carried forward, and the export never shows it.
- **101 (36 above, 65 at £0):** the credit is dated at the household's payment date (due date plus
  days late), not when it was credited. A late payer's credit slips into the next month's window,
  or past March's window entirely.
- **5 at £0 on a credit invoice:** a bill at or below zero after the credit gets no payment row,
  so its credit is not exported at all.
- **5 at £0 for a joiner's first, part month** (OCC-a1e9ae835e65 Nov, OCC-bec72a04dec8 Oct,
  OCC-c0afcdf9fce8 Jan, OCC-e3e94f81161b Feb, OCC-eb8498f3f8aa Jan). EBSS guidance 5.4 gives the
  month's credit to whoever holds the account at 00:00 on the 1st, so none is due. The world is
  right and the row's "on supply on any day of the month" is looser than the guidance. The row's
  predicate is the invariant author's, so this is filed rather than edited.
- **3 at £0, not yet explained:** the second full month on three `OCC-` accounts
  (OCC-bec72a04dec8 Nov, OCC-e3e94f81161b Mar, OCC-eb8498f3f8aa Feb), each bill paid in full with no
  credit. My guess is that the credit went to the unnamed occupier's deemed account
  (`occupier_scheme_credit_gbp`) for a month the named household already held. That is NOT
  established.

All of these come from how the export carries the credit, except the 5 (the predicate) and the 3
(open). Filed as one exception with these counts until the ledger carries the whole credit, dated
when it was applied.

## The fixes, graded on the same run's ledger rebuilt (no new run)

The rebuild used `/var/tmp/fresh-run-scripts/build_ledger.py` and `export_raw.py` on
`/var/tmp/fresh-run-out-2eeb3f0b3`, one fix at a time:
- `/var/tmp/eight-rows-mpan-regrade`: the MPAN fix alone.
- `/var/tmp/eight-rows-ebss-regrade`: both fixes.

| row | before | MPAN fix | + EBSS fix |
|---|---|---|---|
| INV_MPAN_CORE_FORMAT | 637 of 707 | **0 of 707** (707 distinct cores, from 158) | 0 |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | 291 of 2,295 | 291 | **12 of 2,295** |

- **MPAN:** `company/crm/customer_registry.mpan_core` is now the one home for the core. The ledger
  and the customer pages read it, and the core is 13 digits with the check digit. The exception is
  retired.
- **EBSS:** the ledger puts the month's whole credit on the invoice (`scheme_credit_month_gbp`).
  It does so wherever the engine resolved the bill, and as the occupier's credit where that account
  held it. The export carries it dated at the invoice's issue date.

The rebuild also takes INV_PERIODS_CONTIGUOUS from 4 to 0. That is not attributed here: the rebuild
also carries code that landed on HEAD after 13:41 (fccc0a41c7 among it), and neither fix touches
period dates.

**A correction to the causes above.** All 12 residual breaches are on five `OCC-` accounts in the
unnamed-occupier window. They are not "5 joiners and 3 unexplained": that split was too fine. The
occupier path (`run_phase2b`, `occupier_scheme_credit`) sizes their credit by the occupier's debt
and dates it by the settlement record. Four of the 12 are first part-months, where guidance 5.4
gives no credit (OCC-a1e9ae835e65 Nov, OCC-bec72a04dec8 Oct, OCC-e3e94f81161b Feb,
OCC-eb8498f3f8aa Jan). OCC-c0afcdf9fce8, which I had counted as a joiner, joined on 3 Jan, and its
breach is February. The exception is now scoped to those five accounts with a ceiling of 12.

## Item 4: the occupier path records the month's whole credit (prediction, written before any run)

Fix: `occupier_scheme_credit` opens the month's credit on the 1st and `opened` records it whole
(`occupier_scheme_month_credit_gbp`); the bill, ledger and both guards read it. Tests:
`tests/simulation/test_an_occupier_account_carries_the_ebss_credit.py` (two new, red before).

Prediction for the next fresh run, graded with the same runner: the 7 occupier-account months fall
to 0 to 2 (a residual would mean a window opening on the 1st with a different cause); the 5 PROS
months are unchanged, since they are the named-household path. **Total 5 to 7, from 12.** A total
above 7 refutes the claim that the occupier breaches are the debt-sizing. The exception's ceiling
stays 12 until that run exists.
