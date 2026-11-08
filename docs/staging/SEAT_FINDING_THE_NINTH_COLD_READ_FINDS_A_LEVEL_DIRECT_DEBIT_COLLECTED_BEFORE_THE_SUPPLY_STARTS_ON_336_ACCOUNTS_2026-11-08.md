**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The ninth cold read finds a level direct debit collected before the supply starts, on 336 accounts (N23, 2026-11-08)

**Found by.** The ninth cold read's O11, on the af31e73fa7 book, the second book to carry N20's level DD schedule.
- The reader saw "£131.07 in credit" and "No bills yet" on the day supply started: SYN-2016-592 on 14 Dec 2016,
  PROS-2017-0264 and PROS-2019-0246.
- It read these as an old supplier's credit carried over.
- The ledger says otherwise. SYN-2016-592's first level collection, £131.07, is dated **4 Dec 2016**, ten days before
  its supply started. PROS-2017-0264's first, £19.81, is dated 4 Aug 2017, against a start of 30 Aug.

**Confirmed over every page** (`/var/tmp/ninth-read/scripts/candidates.py`).
- **336 accounts** have a payment dated before their supply start, and every one is a direct debit.
- All 336 are level-DD accounts (`level_dd_collections` in the run output).
- The schedule puts the first collection on the collection day of the supply-start month, whether or not that day
  has already passed.

**Why it is wrong.**
- A mandate collects for a supply that exists. The first collection needs the advance notice (10 working days by
  default; `payments_and_direct_debit_2026-10-25.md`, "Advance notice").
- It also needs the AUDDIS lodgement, about 3 working days.
- So the first collection lands after the start, usually in the first month (`a_new_accounts_first_months_2026-10-30.md`).

**What it touches.**
- The welcome page prints a credit the household never had.
- On PROS-2025-0022 the payment record reads "0 of 0 bills paid" beside "£41.73 owed" (O12).
- Any first-month balance is one collection too high.

It does not touch N20's share leg, which reads collections against bills.

**Next.**
- A blind row has been written and landed `checkable: false`.
- The fix sits where the schedule chooses its first month (the level DD schedule that 8178e24218 saved). It must not
  move the share leg, so N20 stays at or under 0.30.
- This is the open level-DD item's territory (`fix-level-dd-households-dunned-per-bill`). That item should take it, or say why not.

**Reverse.** Delete this file.
