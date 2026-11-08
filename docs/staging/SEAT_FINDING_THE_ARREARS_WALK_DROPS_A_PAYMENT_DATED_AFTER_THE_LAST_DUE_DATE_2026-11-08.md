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
