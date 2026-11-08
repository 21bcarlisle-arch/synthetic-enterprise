**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The ninth cold read finds direct debits collected on weekends and on Christmas Day: 29% of collections fall on a day Bacs does not settle (N22, 2026-11-08)

**Found by.** The ninth cold read's O18, on the af31e73fa7 book
(`records/SEAT_READING_THE_NINTH_COLD_READ_ON_THE_AF31E73FA7_BOOK_2026-11-08.md`). The reader, a revenue-assurance
auditor, quoted "25 Dec 2017 payment received £-46.85", "26 Feb 2017" (a Sunday), "10 May 2025" (a Saturday) and
"14 Oct 2017" (a Saturday). None of the eight earlier reads raised it.

**Confirmed over every page.** The page files are `/var/tmp/ninth-read/tree/site/data/customers/`, and the script is
`/var/tmp/ninth-read/scripts/candidates.py`.
- 10,546 of 36,096 direct-debit collections (**29.2%**) fall on a non-working day: 5,184 on a Saturday, 5,191 on a
  Sunday and 171 on 25 Dec, 26 Dec or 1 Jan.
- They are spread over 922 accounts.
- 2/7 is 28.6%. So the collection dates are drawn with no working-day calendar at all.

**Why it is wrong.** Bacs processes and settles on banking days only. A collection due on a weekend or bank holiday
settles on the next working day (or the one before, under the originator's rules). The knowledge page
`docs/market_research/payments_and_direct_debit_2026-10-25.md` already counts in working days for advance notice,
AUDDIS and ARUDD. No row grades the date a collection lands.

**What it touches.** Every dated DD credit on the page ledger. It also touches the level DD schedule
(`level_dd_collections`, a fixed day of the month), and so any "missed by the due date" test that compares a
collection date with a due date.

**Next.** A blind row has been written (`INV_*` rows from `/var/tmp/ninth-read/blind_rows_N22_N24.yaml`, landed
`checkable: false`). Its evaluator is owed. The fix belongs where collection dates are drawn. **I cannot yet say** whether that is the
world's draw or the supplier's schedule, because I have not read either for this.

**Reverse.** Delete this file.

## Whose date it is (seat, 8 Nov 2026, written before the fix)

**It is the world's.** Two places date a DD, and both are on the world side. Neither applies a calendar.
- **Level DD:** `simulation/dd_level_collection_book.build_dd_level_collection_book` dates each one
  `f"{month}-{payment_day}"`.
- **Bill-sized DD:** `simulation/arrears_engine.bill_due_date` plus `days_late`, which is 0 for a DD.
  It is printed by `tools/generate_billing_ledger` and walked by `balance_settlement_from_outcomes`.

The supplier's instruction is a payment day on the mandate (`staggered_payment_day`, a fact the world
holds and hands over). Bacs settles that instruction on the first processing day on or after it.
That roll is rails physics, so the fix goes in the world. Both paths call one function,
`simulation/bacs_processing_day.collected_on`, and the level schedule reaches it through
`level_collection_dates`. A staggered payment day in step 2 calls the same function.

## Done (seat, 8 Nov 2026)

**Knowledge (K8).** `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "The day a
collection lands". It records what a processing day is, that the roll is forward, the four GAPs, and
the build's choices. The calendar is
`docs/domain_artefact_library/regulatory/england_and_wales_bank_holidays.json`, the same GOV.UK source
of record as `company/compliance/working_days.py`. It agrees with that file on every day 2016–2025.

**Evaluator.** `INV_DD_COLLECTION_IS_DATED_ON_A_BACS_PROCESSING_DAY` is now `checkable: true`
(`tools/domain_invariant_runner.ev_dd_on_a_processing_day`). The runner reads the commons calendar
itself, not either lane's reading of it.
- **Red on af31e73fa7:** 11,067 of 36,098 DD collections, over 924 accounts. That is 5,184 Saturday,
  5,192 Sunday and 691 bank holiday.
- The cold read's 10,546 counted only Sat, Sun, 25 and 26 Dec and 1 Jan. Easter, May, August and
  substitute days add 521, as the row's GAP 3 predicted.
- Split by path, on the ledger's payment rows: 8,798 level and 2,484 bill-sized. That count includes
  202 failed presentations, which the raw export does not carry as payments received.

**Fix.** Both paths roll through `collected_on`.
- **A second defect the replay found.** The engine's walk stopped at the last due date. A final DD due
  on a Sunday and collected on the Monday was dropped, and a stale credit netting stood in its place:
  5 accounts, GBP 38.56 (PROS-2020-0126g, due Sun 22 Jun 2025). Now only a DD's roll extends the walk
  (`last_event`).
- `horizon` is unchanged for the statute bar and the closing date. The baseline ledger is byte-identical
  with the roll switched off.

**Replay on af31e73fa7** (`run_output_af31e73fa7_20261107T225950Z.json`, level schedule re-dated by
`level_collection_dates`, ledger regenerated):
- 11,067 -> **0**.
- 11,523 payment dates moved, and **no amount moved**.
- With the roll switched off, current code reproduces the book's ledger exactly, so nothing else is
  mixed into that figure.
- Other rows: `INV_DD_STEP_CHANGE` flags 553 -> 552 (order only). `INV_DD_CADENCE`, `INV_PAYMENT_AMOUNT_SIGN`,
  `INV_COLLECTIONS_EVENTS_ORDERED` and `INV_OVERDUE_WITHIN_BALANCE` are unchanged.

**Controls.** `tests/simulation/test_a_direct_debit_lands_on_a_bacs_processing_day_and_not_before_supply.py`
is mutation-proven. Each of these makes it go red:
- no roll;
- a weekend-only calendar;
- the old horizon.

**Not done here, named.**
- `simulation/bacs_rails._add_working_days` still skips weekends only. It should call `collected_on`'s
  calendar, which retires its last `working_day_guard` allowlist entry.
- The two blind rows that need a scheduled date (`INV_DD_DUE_ON_A_NON_PROCESSING_DAY_...` and the
  Monday-share row) stay `checkable: false` until the ledger exports `scheduled_collection_date`. The
  level schedule now carries `scheduled_date`.
- Seen in passing: the walk still drops a non-DD payment dated after the last due date. That is 84
  standard-credit payments on the fixed ledger. Filed as its own finding,
  `SEAT_FINDING_THE_ARREARS_WALK_DROPS_A_PAYMENT_DATED_AFTER_THE_LAST_DUE_DATE_2026-11-08.md`.
