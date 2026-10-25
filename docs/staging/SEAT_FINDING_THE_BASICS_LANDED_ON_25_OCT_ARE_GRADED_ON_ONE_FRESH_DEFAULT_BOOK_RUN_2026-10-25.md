**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B13_a_dual_fuel_household_is_one_account_across_both_fuels`

# The basics landed on 25 Oct are graded on one fresh default-book run

Worker, 25 Oct. Today five basics landed, but no single run carries all of them yet. This finding
files the predictions before that run launches. The grade gets written beside them, and none of
the predictions may be edited afterwards.

## The run

- **Code:** origin/main `1dda242d0e`. That includes:
  - 3e3136ee2: closure refunds on the reg 6D schedule;
  - c5a3e96fe: one collections ledger per dual-fuel household;
  - 43ef011072: the company decides debt objections;
  - f8c389e9ca: E6's arrears overlay on by default.
- **Book:** default book, default `CURRENT_POLICY`, no `SE_POPULATION_SEED` override, full window
  (`report_end=None`).
- **Worktree:** a clean one at `/var/tmp/se-basics-run-1dda242d0e`.
- **Script:** `/var/tmp/basics-run-scripts/arm.py`. It pickles the raw output key by key into
  `/var/tmp/basics-run-out/`, writes `arm.json` in the shape E6's `grade.py` reads, and writes
  `DONE.json` last.
- **Launch:** `background/launch_long_job.py`, job `basics-default-book-1dda242d0e`.
- **Predictions filed:** 2026-10-25 22:05Z, before launch.
- **Running alongside:** the seat's second-seed E6 arm (`longjob-arrears-overlay-arm-seed-61101`).
  Memory holds both: 16.6 GB was free, and that arm peaks at 6.3 GB.

## Predictions

| Leg | Question | Prediction |
|---|---|---|
| (a) | Closure refunds paid more than 10 working days after the final bill's issue (3e3136ee2) | **0** |
| (b) | Dual-fuel households with more than one collections ledger (c5a3e96fe) | **0** |
| (c) | Debt objections: requests the company was asked, objections it raised, objections it declined (no-object answers), and objections the world drew itself | **>0 asked, >0 raised, >0 declined, 0 world-drawn**. Rate of raised over asked: below 6% (the 2016-19 probe found 1 in 59) |
| (d) | ADDACS 1 records, and what the desk did after each | **>0 records.** I cannot predict what the desk did; I will record it without grading it |
| (e) | Default-tariff invoices above min(cap, EPG) for their period | **0** |
| (f) | E6's 2023 step on this book, read with E6's own `grade.py` | End-2023 arrears growth per indebted account is above its baseline and above end-2022, so leg (c) of the switch-on rule holds. Its value need not equal the 2.29 E6 measured, because this run has the crisis overlay off (default) and EP12's objections keep some indebted leavers on the book |

## What each leg moves, if it holds

The map was read before launch. Each atom moves only as far as its own next level's definition
allows. Where that definition asks for more than a run can show, the grade says so and the row
names what it still lacks.

- (a) and (e): `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`.
  3e3136ee2's finding is filed against D48.
- (b): `B13_a_dual_fuel_household_is_one_account_across_both_fuels`, at L1. Its L2 asks for the gas
  fix on contact (`_splice_a_refix`), which a run cannot supply. A green (b) is evidence for B13,
  but it cannot move B13 to L2.
- (c): `EP12_adapter_css_rec_switching`, at L2, target 3.
- (d): `W2_41_a_household_cancels_its_mandate_as_its_own_act`, at L1. Its row says "the run does
  not route it yet". So my prediction of more than 0 ADDACS records **in the run output** may be
  refuted, because the records may be drawn by the world and consumed inside the company without
  ever reaching the output. If so, the grade says leg (d) cannot be read from the output. It does
  not count that as 0.
- (f): `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build`, at L1,
  target 2.

## Grade

*(written after the run, below this line; the predictions above are not edited)*

**The run did not finish.** About 25 minutes in, the company's own preventive invariant refused a
dunning step and stopped the run:

```
DunningOfAClearedDebtError: ACC-SYN-2016-048 reminder_2 on 2020-10-12 with the ledger at GBP 0.0 (cured None)
```

The refusal was raised in `run_phase2b._post_month_bill` → `LivePaymentTriad.record_period` →
`advance_collections_journey` (log: `/var/tmp/basics-run-out.log`). SYN-2016-048 is a dual-fuel
household. Its electricity leg runs terms 15 (2020-01-01 → 2020-02-07) and 16 (2020-02-07 →
2021-02-06). Its gas leg prints no term 16.

No leg (a)-(f) can be graded from this run, because it wrote no output.

**Two commits are new since the last default-book full run that completed** (E6's arm at
`e623c3354a`):

- c5a3e96fe: one ledger per dual household, walked only once every leg still posting has posted;
- 43ef011072: EP12, where a departure the company objects to becomes a stay.

I cannot yet say which one causes the refusal, or whether it takes both.

**Prediction, filed 2026-10-25 before the one-variable run.** Same commit, same book,
`SE_DEBT_OBJECTION=0`, which restores no-objection departures and leaves c5a3e96fe on. My guess,
held at about 60%: the run gets past 2020-10-12 without this refusal, which would make EP12 the
cause. The mechanism I suspect is a departure objected to on one leg of a dual household but not
the other, which leaves the account's legs out of step. If the same refusal fires at the same
account and date, the cause is c5a3e96fe alone.

**Result of the one-variable run (job `longjob-basics-default-book-1dda242d0e-objection-off`,
`SE_DEBT_OBJECTION=0`, confirmed in the unit's environment): refuted.** The same refusal fires on
the same account on the same day:

```
DunningOfAClearedDebtError: ACC-SYN-2016-048 reminder_2 on 2020-10-12 with the ledger at GBP 0.0 (cured None)
```

So EP12 is not the cause. The guess was about 60%, and it was wrong.

**The cause, by elimination: c5a3e96fe.** Three code commits are new since `e623c3354a` across
`simulation/`, `company/`, `saas/` and `background/live_payment_triad.py`:

- 43ef011072 (EP12): now ruled out.
- f8c389e9ca: flips a policy default that E6's completed arm already ran with, so it is not the
  cause. One difference remains: that arm also had the crisis overlay on. That is the remote
  alternative, since provision does not post to the ledger.
- c5a3e96fe: what remains.

The invariant predates every one of them (`e2fd1bc15c`, 4 Oct). c5a3e96fe's own runs stopped at
2017-12-31, so no full window ever ran it. The seat's second-seed E6 arm carries c5a3e96fe without
EP12 and ran past mid-2022 on seed 61101. So the defect depends on the seed. It is not universal.

**Suspected mechanism, not yet read on the account.** c5a3e96fe makes two changes:

1. It re-keys the early cure from `(account, due date)` to `invoice_ref`, which is per leg.
2. It walks one account to `min(previous_due of this leg, the walk bound)`.

SYN-2016-048's electricity leg starts a one-year term on 2020-02-07, and its gas leg prints no
term after 2020-02-07. A balance cleared by one leg's cash would then never register as a cure on
the journey that the other leg's overdue bill opened. That journey goes on dunning a ledger at
GBP 0.00.

**Consequences.**

- No default-book full run can finish at origin today.
- The basics grade has nothing to read. Legs (a)-(f) are **ungraded**, and no map row moves on
  this finding. B13, W2_41, EP12, E6 and D48 keep their levels.
- If the weekly published run is a default-book full run, it will stop at the same point. That is
  why this finding is BLOCKING.

**Next, in order.**

1. Read ACC-SYN-2016-048's journey and ledger between 2020-02 and 2020-10. Read them in-process on
   a run stopped just before the refusal, not by eye from the log.
2. Fix the mechanism as a class. A cure is the account's ledger reaching zero, not one invoice's
   payment. Add a control that reproduces the two-leg shape, and give it a mutant.
3. Relaunch `/var/tmp/basics-run-scripts/arm.py` at the fix's origin commit, and grade it with
   `/var/tmp/basics-run-scripts/grade.py` against the predictions above, unedited.

If the fix cannot land quickly, the reversible alternative is to revert c5a3e96fe. That restores
the two-journey defect it closed, so it is the second choice.
