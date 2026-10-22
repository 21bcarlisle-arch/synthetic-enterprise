# The bill estimate reads the annualised advance: one-variable table on 76a29bd92, and its prereg

**Direction item:** `the-bill-estimate-reads-the-annualised-advance-not-three-reads` (worker, 2026-10-22)
**Knowledge (K8):** `docs/market_research/unbilled_energy_and_revenue_assurance.md` K2, "How published
practice estimates an unread period".
**Built default off:** `DecisionPolicy.bill_estimate_reads_the_annualised_advance` →
`build_monthly_bills(annualised_advance_estimate=...)`. Control:
`tests/company/billing/test_the_estimate_reads_the_annualised_advance_when_switched_on.py`.

## 1. The one-variable table (read-only, before any build)

- **Run:** `docs/reports/run_output_latest.json` on the shared tree, `producing_commit` 76a29bd92.
  It is the run the long-run census read
  (`WORKER_RESULT_EVERY_RUN_OF_TWELVE_ESTIMATES_ON_THE_76A29BD92_RUN_OUTLIVES_ITS_READ_VISIT_BECAUSE_NO_VISIT_CAN_READ_2026-10-22.md`).
- **One process, one change.** Every estimated bill after the account's first read is re-estimated
  twice. Method A is `estimate_unread_kwh` on the latest three actual read periods, exactly as the
  run billed: it reproduces the billed `estimated_consumption_kwh` on **32,160 of 32,160** bills.
  Method B is `annualised_advance_kwh` over the register reads the company held before the period,
  times `profile_weight` for the period. Those reads are the change-of-supply opening read at 0,
  then each actual read's register, which is the cumulative advance. Where no advance of 182 days
  or more exists, B falls back to A, exactly as the build does. Bills before the first read are the
  registry opening estimate under both methods.
- **True use** is the world's `true_consumption_kwh` and is used only to grade.

### The 27 runs of 12+ estimates billed more than 25% off use

| account | fuel | pay | bills | run | billed / true kWh | three-read error | annualised error | |err| cut? | bills on fallback |
|---|---|---|---|---|---|---|---|---|---|
| SYN-2016-274g | gas | direct_debit | 13 | 2016-07 to 2017-07 | 17,785 / 6,671 | +167% | +167% | NO | 13 |
| PROS-2016-0263g | gas | direct_debit | 15 | 2019-02 to 2020-04 | 14,257 / 5,967 | +139% | +156% | NO | 0 |
| SYN-2016-136g | gas | direct_debit | 13 | 2016-06 to 2017-06 | 16,684 / 10,398 | +60% | +60% | NO | 13 |
| SYN-2016-541 | elec | standard_credit | 15 | 2020-02 to 2021-04 | 1,963 / 4,568 | -57% | -58% | NO | 0 |
| SYN-2016-190g | gas | prepayment | 13 | 2016-04 to 2017-04 | 14,012 / 26,099 | -46% | -46% | NO | 0 + 13 pre-read |
| SYN-2016-001g | gas | direct_debit | 21 | 2021-09 to 2023-05 | 14,538 / 9,937 | +46% | +14% | yes | 0 |
| PROS-2017-0233 | elec | direct_debit | 24 | 2017-08 to 2019-07 | 7,253 / 13,414 | -46% | -46% | NO | 0 + 24 pre-read |
| SYN-2016-221 | elec | direct_debit | 22 | 2022-03 to 2023-12 | 15,688 / 10,972 | +43% | +29% | yes | 0 |
| SYN-2016-148g | gas | prepayment | 16 | 2016-05 to 2017-08 | 14,928 / 10,482 | +42% | +42% | NO | 16 |
| SYN-2016-444g | gas | direct_debit | 21 | 2018-07 to 2020-03 | 29,079 / 20,591 | +41% | +14% | yes | 0 |
| SYN-2016-445g | gas | direct_debit | 14 | 2020-09 to 2021-10 | 10,283 / 7,292 | +41% | -6% | yes | 0 |
| PROS-2017-0336 | elec | direct_debit | 14 | 2019-04 to 2020-05 | 38,658 / 27,651 | +40% | +7% | yes | 0 |
| SYN-2016-107g | gas | direct_debit | 19 | 2016-03 to 2017-09 | 7,437 / 12,091 | -38% | -38% | NO | 0 + 19 pre-read |
| PROS-2017-0393g | gas | direct_debit | 15 | 2019-10 to 2020-12 | 13,243 / 9,606 | +38% | +2% | yes | 0 |
| SYN-2016-150g | gas | direct_debit | 14 | 2022-09 to 2023-10 | 18,025 / 13,120 | +37% | -1% | yes | 0 |
| PROS-2018-0016g | gas | direct_debit | 14 | 2020-08 to 2021-09 | 24,229 / 17,663 | +37% | -1% | yes | 0 |
| SYN-2016-299 | gas | direct_debit | 13 | 2017-06 to 2018-06 | 8,880 / 6,507 | +36% | -2% | yes | 0 |
| SYN-2016-471 | elec | direct_debit | 15 | 2016-10 to 2017-12 | 2,080 / 3,214 | -35% | -35% | NO | 0 + 15 pre-read |
| SYN-2016-275g | gas | direct_debit | 15 | 2016-07 to 2017-09 | 9,294 / 7,085 | +31% | +31% | NO | 15 |
| SYN-2016-213g | gas | direct_debit | 13 | 2023-06 to 2024-06 | 24,765 / 18,924 | +31% | -3% | yes | 0 |
| SYN-2016-476 | gas | prepayment | 13 | 2023-06 to 2024-06 | 13,015 / 9,971 | +31% | -2% | yes | 0 |
| PROS-2016-0042g | gas | direct_debit | 18 | 2016-08 to 2018-01 | 15,637 / 11,996 | +30% | +30% | NO | 18 |
| SYN-2016-445g | gas | direct_debit | 21 | 2018-11 to 2020-07 | 14,831 / 11,423 | +30% | +9% | yes | 0 |
| SYN-2016-085 | elec | direct_debit | 12 | 2018-03 to 2019-02 | 5,121 / 4,001 | +28% | +1% | yes | 0 |
| PROS-2018-0016g | gas | direct_debit | 17 | 2021-11 to 2023-03 | 34,869 / 27,248 | +28% | +5% | yes | 0 |
| OCC-564700946c93 | elec | direct_debit | 24 | 2021-09 to 2023-08 | 6,113 / 4,852 | +26% | +10% | yes | 0 |
| OCC-87715bf1d9e7 | gas | direct_debit | 13 | 2020-09 to 2021-09 | 11,800 / 9,410 | +25% | +14% | yes | 0 |

|error| cut on 16/27; median |err| A 37.9% B 14.1%

**Of the 11 "NO" rows, 9 are ties where the method cannot apply.** Five runs have no advance of
182 days yet: every bill is on fallback, and all are 2016 accounts with few reads. Four run before
the first read (`pre-read`). Two runs get worse: PROS-2016-0263g (+139% to +156%) and SYN-2016-541
(-57% to -58%).

**Of the 18 runs where the method applies, it cuts the error on 16.** None of the 2022-23
overcharges among the 27 gets worse: SYN-2016-221 goes +43% to +29%, SYN-2016-001g +46% to +14%,
SYN-2016-150g +37% to -1%, PROS-2018-0016g +28% to +5%, OCC-564700946c93 +26% to +10%.

**The case that prompted the item does not come out clean.** PROS-2017-0336's 2019-20 run goes from
+40% to +7%. Its 2021-23 run (-20%, the +£4,224.94 catch-up) goes to **+22%**: 50,797 kWh billed
against 41,715 used. Its advance was struck over a year when the electrically heated home used more.
A summer read no longer sets the level, but a high-use year does. The AQ is weather-corrected for
exactly this reason, and our advance is not (K2 GAP).

### D48 estimated-bill error by year (every estimated bill after a first read, both methods)

| year | est. bills | on fallback | three-read billed/true | annualised billed/true | three-read mean |bill err| | annualised mean |bill err| |
|---|---|---|---|---|---|---|
| 2016 | 1604 | 1340 | 1.056 | 1.062 | 19.9% | 19.7% |
| 2017 | 4743 | 1559 | 1.011 | 1.004 | 16.1% | 15.4% |
| 2018 | 4467 | 317 | 1.006 | 0.992 | 16.0% | 14.8% |
| 2019 | 3762 | 320 | 1.008 | 0.998 | 16.6% | 15.4% |
| 2020 | 3374 | 352 | 1.036 | 1.018 | 17.0% | 15.2% |
| 2021 | 3169 | 259 | 1.012 | 0.996 | 16.9% | 15.8% |
| 2022 | 3167 | 180 | 1.021 | 1.016 | 15.1% | 14.4% |
| 2023 | 3198 | 91 | 1.019 | 1.007 | 15.2% | 14.1% |
| 2024 | 3127 | 156 | 1.006 | 0.990 | 14.4% | 13.0% |
| 2025 | 1549 | 116 | 1.001 | 0.996 | 15.5% | 14.6% |

The mean per-bill error falls in 2017-2025, by 0.7 to 1.9 percentage points. 2016 ties, because 84%
of its bills have no long enough advance. Pooled billed/true moves closer to 1 in 8 of 10 years.

### Catch-ups, book-wide: a PROJECTION, not a measurement

Each catch-up the run billed, scaled by (true − B) / (true − A) kWh over the run it closes. This is
linear in kWh. It ignores price moves within the run and the second-order effects a re-run
carries (a different DD, different reads at different times). That is why the arm below exists.

| year | overcharges ≥ £500, three-read | annualised | overcharge sum, three-read | annualised | undercharges ≥ £500, three-read | annualised | sum of |catch-up|, three-read | annualised |
|---|---|---|---|---|---|---|---|---|
| 2016 | 0 | 0 | -1,455 | -1,491 | 0 | 0 | 5,125 | 5,126 |
| 2017 | 1 | 1 | -8,380 | -8,501 | 3 | 3 | 20,368 | 19,488 |
| 2018 | 1 | 1 | -7,998 | -5,594 | 3 | 3 | 17,227 | 13,054 |
| 2019 | 0 | 0 | -6,704 | -4,496 | 1 | 3 | 14,293 | 10,999 |
| 2020 | 1 | 0 | -8,204 | -4,036 | 1 | 0 | 13,694 | 7,982 |
| 2021 | 0 | 0 | -6,706 | -4,442 | 1 | 1 | 12,288 | 9,917 |
| 2022 | 0 | 1 | -10,339 | -8,077 | 1 | 2 | 17,767 | 15,911 |
| 2023 | 6 | 5 | -25,310 | -24,793 | 4 | 4 | 45,648 | 40,286 |
| 2024 | 2 | 2 | -15,051 | -10,857 | 2 | 2 | 26,697 | 21,250 |
| 2025 | 1 | 1 | -6,137 | -4,391 | 2 | 2 | 12,127 | 8,814 |

- **Sum of |catch-up| falls from £185.2k to £152.8k (−17.5%)**, and falls in every year but 2016.
- **2022-23 overcharge sum falls from −£35.6k to −£32.9k.** By count, £500+ overcharges go from
  0 to 1 in 2022 and from 6 to 5 in 2023.
- **The tail does not improve: catch-ups of £500 or more go from 30 to 31.** Most of the large
  three-read catch-ups shrink. New ones appear where use moved away from the advance year:
  SYN-2016-169g −£66 → +£2,214, PROS-2020-0016g +£13 → +£2,044, SYN-2021-001 −£118 → −£1,715,
  SYN-2016-565 −£424 → −£2,934.

**Verdict on the item's rule.** "Cuts the error on most of the 27": yes (16 of 27, 16 of the 18
where it applies). "Does not worsen the 2022-23 overcharges": yes, both on the 27 and in the
book-wide sum. So it is built, default off. **What it does not do is end the large catch-up.** It
moves the bill shock from accounts with a short summer window to accounts whose use changed since
the advance year.

**Mutations, run in a scratch origin worktree.** (1) The advance branch was forced off with the
switch on. The on/off control and the planted-rate control both went red. (2) The change-of-supply
opening read was dropped, so the advance opens at the first actual read. The on/off control went
red. The fallback leg (three months of reads) has no mutation: it holds whether or not the guard is
there, because `annualised_advance_kwh` itself refuses an advance under 182 days. That is an
equivalence, not a missing test.

## 2. Pre-registration (filed before either arm runs)

**Arms.** Both run at one commit, serially, from a locked worktree at origin/main after this
record lands, through `background.launch_long_job`:
- `control`: `python3 -m tools.read_instruction_arms register <out>/control.json`. This is the
  standing policy (the read instruction is on, at the register access end).
- `annualised`: the same, plus `--annualised-advance`.

Outputs go to `/var/tmp/se-annualised-arms-out/`. The arms do not touch `/var/tmp/se-pcs-arms-out`
or `/var/tmp/se-pcs-arms16-out`.

**Instrument.** Bills from each arm's `bills`. A catch-up is `catchup_adjustment_gbp` on a bill.
Estimated-bill error is |`total_consumption_kwh` / `true_consumption_kwh` − 1| over bills with
`billing_basis == "estimated"` and `true_consumption_kwh > 0` that fall after the account's first
actual bill, grouped by `period_start` year: the population of the table in section 1.

**Predictions** (annualised against control, at the same commit):
- **PA. Tail.** The count of |catch-up| ≥ £500 is within ±4 of the control's (point +1). 70%. I
  am predicting no improvement in the tail.
- **PB. Money moved by catch-ups.** Sum |catch-up|, annualised / control, is in [0.70, 0.92]
  (point 0.83). 70%.
- **PC. D48 error by year.** The mean per-bill error is lower in at least 8 of the 9 years
  2017-2025. 75%. 2016 is within ±1 pp. 80%.
- **PD. 2022-23 overcharges.** The sum of negative catch-ups closing in 2022-2023, annualised /
  control, is in [0.75, 1.00] (point 0.92). 65%.
- **PE. The motivating account.** PROS-2017-0336's catch-up closing its 2021-23 run turns into an
  overcharge (a credit) of £2,000-£6,000. 60%.

**Decision rule, fixed now.**
- **If PB and PC hold and PA does not rise by more than 4,** the estimate is better on the money
  and no worse in the tail. The seat proposes the default on, in `for_the_director` with these
  arms. It is a billing-accuracy change to every standing policy.
- **If PB or PC fails,** the projection was wrong about the instrument. The D48 record says so,
  with the numbers, and the switch stays off.
- **In either case the next variant is the gas 9-month floor** (Xoserve's AQ minimum, K2 design
  choice 1). After that comes a cap on the advance's weight against the three-read level for an
  account whose recent reads diverge. That is the change that would address the new tail.

## 3. Launch

Launched 2026-10-22T15:37:46Z at **30674a4bd** (the commit that landed this record and the switch),
from the locked worktree `/var/tmp/se-annualised-arms`, as unit
`longjob-annualised-advance-arms-30674a4bd` (`background.launch_long_job`, admitted at 7,000 MB
peak). `control` then `annualised`, serially, by `/var/tmp/se-annualised-arms-out/run.sh`; each arm
writes `<arm>.json`, `<arm>.log` and `<arm>.rc` there. Nothing reads or writes
`/var/tmp/se-pcs-arms-out` or `/var/tmp/se-pcs-arms16-out`. No outcome has been read.
