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

## Done (seat, 8 Nov 2026)

Taken here with N22, as the drawn direction asked, not by `fix-level-dd-households-dunned-per-bill`.
Both concern the date a collection lands, and the level schedule is where both are dated.

**Knowledge (K8).** `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "The day a
collection lands": the first collection may not precede supply start.
- The rule rests on Octopus's published practice, quoted word for word, and on logic. No licence
  clause was found that forbids it in terms (GAP 3).

**Evaluator.** `INV_FIRST_LEVEL_DD_IS_NOT_COLLECTED_BEFORE_SUPPLY_START` is now `checkable: true`
(`tools/domain_invariant_runner.ev_first_dd_not_before_supply`). It grades an account whose first
payment is a DD, against its first period's start.
- **Red on af31e73fa7:** 336 accounts with a first DD before supply. 268 breach (more than 3 days
  early) and 68 flag (1-3 days early). That is the cold read's count exactly.

**Fix.** `level_collection_dates` (`simulation/dd_level_collection_book.py`): a payment day before the
leg's supply start is scheduled on the supply start date (`supply_starts`, its earliest bill's
`period_start`), then rolled by `collected_on`.
- The amount and the month it pays for are unchanged, so N20's share leg cannot move.
- 415 level collections were held to supply start.

**Replay on af31e73fa7:** 268 breaches -> **0**, 68 early flags -> **0**.

**Residual, named.**
- 192 accounts flag on the far side, a first DD more than 45 days after supply. 191 of them were
  there before this change.
- That edge is the row's own stated belief (GAP 4), and why those first collections come late is
  not yet asked. It is a flag, not a breach.
