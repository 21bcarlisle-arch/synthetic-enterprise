**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The arrears walk drops a payment dated after the account's last due date: 84 standard-credit payments on the af31e73fa7 book (2026-11-08)

**Found by.** The seat, while fixing N22 (`docs/staging/done/SEAT_FINDING_THE_NINTH_COLD_READ_FINDS_DIRECT_DEBITS_COLLECTED_ON_WEEKENDS_AND_CHRISTMAS_DAY_2026-11-08.md`).

**What.** `simulation/arrears_engine.balance_settlement_from_outcomes` walks each leg's events in date
order, and until 8 Nov it stopped at `horizon`, the leg's last due date. A payment dated later never
entered the walk.
- That dropped five DDs that the N22 roll moved past their due date. The fix lets only a DD's roll
  extend the walk (`last_event`), so the baseline stays byte-identical.
- It still drops a late payment by any other method. On the replayed af31e73fa7 ledger that is 84
  standard-credit payments on a final bill, paid 1 to 15 days late (for example, C5 due 2017-01-24,
  paid 2017-02-08, GBP 250.40).

**Measured.**
- All 84 bills print `paid`, and none carries an arrears case on its invoice.
- So no write-off is visible on the page today.
- I cannot yet say whether the walk's closing balance for these leavers counts the bill as still
  outstanding. If it does, `closing_out` and the write-off at close would read debt the household
  paid.

**Next.** Measure `closing_out` for the 84 legs with the walk run to `max(event)`. If any is owed
when
it should not be, extend `last_event` to every event and replay. The one variable is the horizon.

**Reverse.** Delete this file.

## Done (2026-11-08, worker tick): an equivalence, not a defect. No code change.

**The one variable.** The walk's horizon. `balance_settlement_from_outcomes` was run twice on the
replayed af31e73fa7 book (`run_output_af31e73fa7_20261107T225950Z.json`, code at origin `d2173cb2d7`).
The first run was as shipped (`last_event` = last due date, extended only by a DD's roll). The second
was run to `max(event)`, with `last_event = max([horizon] + [e[0] for e in events])`. The probe swaps
only that one line in the function's source and keeps everything else.

**Result, whole book.**
- write-offs: 280 before, 280 after, identical.
- `closing_out`: 857 before, 857 after, identical.
- credits netted: 0 keys differ.
- No household reads as owing after it paid, so there is no red-on-today test to write.

**Why this is an equivalence and not a missing case.**
- *The debt side cannot fire.* Only `failed` and `dispute` rows enter `outstanding`. A `success` row
  pays its own bill and never adds debt. So dropping one cannot leave a paid bill in `closing_out` or
  in a write-off at close.
- *Leg A (latent, did not fire): a credit drawn late.* If credit is waiting on the fuel when the
  late payment lands, the payment would take it (`_draw`). Dropping the payment leaves that credit in
  `closing_out`, which overstates a credit balance (a refund owed), not a debt. It did not fire here.
- *Leg B (latent, did not fire): a late payment restarting the bar clock.* That could move a
  statute-barred write-off to the close leg. It did not fire here either.
- If either leg fires on a later book, the remedy is the one-line extension above. The book-wide
  diff is the test for it.

**Count.** The probe counts **83** legs where the finding said 84, using the engine's resolved rows
(non-DD `success` paid after the leg's last due date). All 83 are `standard_credit`, paid 1 to 15 days
late, and 44 of them are leavers. I cannot yet say where the one-leg difference comes from. The
finding's 84 was counted on the ledger, not on the engine rows.

**Per leg, before → after** (cid | fuel | due | days late | GBP | leaver | closing_out before | after | write-off before | after):

```
C5 | electricity | 2017-01-24 | 15 | 250.40 | True | 0 | 0 | 0.00 | 0.00
OCC-218d26f2bb03 | electricity | 2025-06-24 | 8 | 19.43 | False | None | None | 0.00 | 0.00
OCC-b3b4e19ff255 | electricity | 2025-02-09 | 9 | 68.12 | True | 141.72 | 141.72 | 141.72 | 141.72
OCC-cc0c78690877g | gas | 2025-06-21 | 14 | 7.27 | False | None | None | 0.00 | 0.00
PROS-2016-0075 | electricity | 2019-10-15 | 12 | 35.46 | True | 0 | 0 | 0.00 | 0.00
PROS-2016-0098 | electricity | 2021-09-16 | 35 | 74.27 | True | 72.06 | 72.06 | 72.06 | 72.06
PROS-2016-0098 | electricity | 2021-10-14 | 16 | 80.97 | True | 72.06 | 72.06 | 72.06 | 72.06
PROS-2016-0264 | electricity | 2025-06-29 | 14 | 11.60 | False | None | None | 0.00 | 0.00
PROS-2017-0393 | electricity | 2020-12-15 | 28 | 37.09 | True | 76.7 | 76.7 | 76.70 | 76.70
PROS-2017-0393 | electricity | 2021-01-03 | 28 | 25.22 | True | 76.7 | 76.7 | 76.70 | 76.70
PROS-2017-0393g | gas | 2021-01-15 | 27 | 12.81 | True | 0 | 0 | 0.00 | 0.00
PROS-2018-0016 | electricity | 2025-06-21 | 31 | 154.17 | False | None | None | 0.00 | 0.00
PROS-2018-0016g | gas | 2025-06-19 | 12 | 53.64 | False | None | None | 0.00 | 0.00
PROS-2020-0013 | electricity | 2025-01-16 | 14 | 87.38 | True | 0 | 0 | 0.00 | 0.00
PROS-2020-0013 | electricity | 2025-01-24 | 23 | 22.82 | True | 0 | 0 | 0.00 | 0.00
PROS-2020-0013g | gas | 2025-01-14 | 35 | 77.61 | True | 45.95 | 45.95 | 45.95 | 45.95
PROS-2020-0013g | gas | 2025-01-24 | 22 | 29.98 | True | 45.95 | 45.95 | 45.95 | 45.95
PROS-2020-0016 | electricity | 2025-05-27 | 30 | 66.20 | False | None | None | 0.00 | 0.00
PROS-2020-0016 | electricity | 2025-06-21 | 18 | 9.29 | False | None | None | 0.00 | 0.00
PROS-2020-0048 | electricity | 2021-02-15 | 44 | 38.44 | True | 0 | 0 | 0.00 | 0.00
PROS-2020-0048 | electricity | 2021-03-06 | 42 | 17.24 | True | 0 | 0 | 0.00 | 0.00
PROS-2021-0217 | electricity | 2025-05-14 | 42 | 90.30 | False | None | None | 0.00 | 0.00
PROS-2021-0217 | electricity | 2025-06-19 | 35 | 82.67 | False | None | None | 0.00 | 0.00
PROS-2021-0217 | electricity | 2025-06-22 | 44 | 19.50 | False | None | None | 0.00 | 0.00
PROS-2021-0236g | gas | 2025-06-24 | 9 | 5.09 | False | None | None | 0.00 | 0.00
PROS-2021-0362 | electricity | 2024-11-02 | 28 | 44.54 | True | 0 | 0 | 0.00 | 0.00
PROS-2021-0362g | gas | 2024-10-17 | 38 | 93.28 | True | 59.56 | 59.56 | 59.56 | 59.56
PROS-2021-0362g | gas | 2024-10-29 | 34 | 58.82 | True | 59.56 | 59.56 | 59.56 | 59.56
PROS-2022-0356g | gas | 2025-06-18 | 25 | 52.50 | False | None | None | 0.00 | 0.00
PROS-2022-0356g | gas | 2025-06-22 | 31 | 10.76 | False | None | None | 0.00 | 0.00
PROS-2023-0013g | gas | 2024-02-01 | 33 | 94.28 | True | 40.45 | 40.45 | 40.45 | 40.45
PROS-2023-0385 | electricity | 2025-06-24 | 21 | 19.92 | False | None | None | 0.00 | 0.00
SYN-2016-001 | electricity | 2025-05-18 | 55 | 80.01 | False | None | None | 0.00 | 0.00
SYN-2016-001 | electricity | 2025-06-24 | 54 | 16.07 | False | None | None | 0.00 | 0.00
SYN-2016-023 | electricity | 2025-06-21 | 7 | 11.59 | False | None | None | 0.00 | 0.00
SYN-2016-023g | gas | 2025-06-23 | 15 | 9.42 | False | None | None | 0.00 | 0.00
SYN-2016-026 | electricity | 2017-02-18 | 6 | 17.20 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-048 | electricity | 2025-06-28 | 3 | 13.59 | False | None | None | 0.00 | 0.00
SYN-2016-067 | electricity | 2017-02-17 | 24 | 62.83 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-067 | electricity | 2017-03-02 | 34 | 35.94 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-077 | electricity | 2017-02-15 | 24 | 32.81 | True | 31.36 | 31.36 | 31.36 | 31.36
SYN-2016-077 | electricity | 2017-03-08 | 28 | 19.17 | True | 31.36 | 31.36 | 31.36 | 31.36
SYN-2016-082 | electricity | 2025-06-25 | 14 | 9.12 | False | None | None | 0.00 | 0.00
SYN-2016-082g | gas | 2025-05-14 | 72 | 63.91 | False | None | None | 0.00 | 0.00
SYN-2016-082g | gas | 2025-06-19 | 58 | 38.20 | False | None | None | 0.00 | 0.00
SYN-2016-082g | gas | 2025-06-23 | 53 | 6.44 | False | None | None | 0.00 | 0.00
SYN-2016-094 | electricity | 2025-06-22 | 10 | 20.61 | False | None | None | 0.00 | 0.00
SYN-2016-115 | electricity | 2020-01-17 | 12 | 70.97 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-159 | electricity | 2025-06-14 | 41 | 111.03 | False | None | None | 0.00 | 0.00
SYN-2016-159 | electricity | 2025-06-21 | 15 | 13.76 | False | None | None | 0.00 | 0.00
SYN-2016-174 | electricity | 2021-03-27 | 39 | 54.26 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-174 | electricity | 2021-04-18 | 35 | 56.32 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-174g | gas | 2021-04-15 | 29 | 32.54 | True | 38.65 | 38.65 | 38.65 | 38.65
SYN-2016-174g | gas | 2021-04-21 | 20 | 4.73 | True | 38.65 | 38.65 | 38.65 | 38.65
SYN-2016-178g | gas | 2018-08-14 | 77 | 21.50 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-178g | gas | 2018-09-26 | 45 | 20.84 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-178g | gas | 2018-10-16 | 62 | 27.80 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-206 | electricity | 2025-04-14 | 41 | 154.91 | True | 168.9 | 168.9 | 168.90 | 168.90
SYN-2016-206 | electricity | 2025-05-08 | 20 | 102.82 | True | 168.9 | 168.9 | 168.90 | 168.90
SYN-2016-206g | gas | 2025-05-11 | 27 | 64.88 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-240 | electricity | 2025-05-20 | 45 | 68.82 | False | None | None | 0.00 | 0.00
SYN-2016-240 | electricity | 2025-06-27 | 84 | 14.69 | False | None | None | 0.00 | 0.00
SYN-2016-306g | gas | 2024-07-18 | 9 | 2.80 | True | 22.2 | 22.2 | 22.20 | 22.20
SYN-2016-320 | electricity | 2018-10-17 | 14 | 43.83 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-376 | electricity | 2018-02-20 | 20 | 67.64 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-380 | electricity | 2025-05-14 | 76 | 166.58 | False | None | None | 0.00 | 0.00
SYN-2016-380 | electricity | 2025-06-18 | 80 | 154.74 | False | None | None | 0.00 | 0.00
SYN-2016-380 | electricity | 2025-06-23 | 69 | 32.55 | False | None | None | 0.00 | 0.00
SYN-2016-382 | electricity | 2025-06-24 | 24 | 275.28 | False | None | None | 0.00 | 0.00
SYN-2016-445g | gas | 2025-06-23 | 22 | 4.78 | False | None | None | 0.00 | 0.00
SYN-2016-457 | electricity | 2020-01-15 | 20 | 92.06 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-457g | gas | 2020-01-19 | 17 | 89.04 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-487g | gas | 2025-06-16 | 26 | 29.76 | False | None | None | 0.00 | 0.00
SYN-2016-487g | gas | 2025-06-24 | 21 | 4.51 | False | None | None | 0.00 | 0.00
SYN-2016-498 | electricity | 2022-12-17 | 37 | 35.78 | True | 54.27 | 54.27 | 54.27 | 54.27
SYN-2016-498g | gas | 2023-01-06 | 10 | 154.79 | True | 0 | 0 | 0.00 | 0.00
SYN-2016-499 | electricity | 2019-04-19 | 39 | 39.02 | True | 36.57 | 36.57 | 36.57 | 36.57
SYN-2016-525g | gas | 2025-06-26 | 43 | 5.75 | False | None | None | 0.00 | 0.00
SYN-2016-536g | gas | 2021-11-20 | 26 | 18.57 | True | 43.26 | 43.26 | 43.26 | 43.26
SYN-2016-541 | electricity | 2025-05-15 | 41 | 220.04 | False | None | None | 0.00 | 0.00
SYN-2016-549 | electricity | 2025-06-15 | 11 | 82.15 | False | None | None | 0.00 | 0.00
SYN-2016-549g | gas | 2025-06-23 | 37 | 6.90 | False | None | None | 0.00 | 0.00
SYN-2016-601g | gas | 2020-03-16 | 8 | 48.26 | True | 0 | 0 | 0.00 | 0.00
```

Non-leavers have no `closing_out` (None). Reverse: move this file back to `docs/staging/`.
