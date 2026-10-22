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

## 4. Graded (2026-10-22, delivery seat): three held, two refuted, the decision rule says propose default on

**Validity.** Both arms exited 0 at **30674a4bdd** (`control` 15:37:46Z to 16:38:21Z, `annualised`
16:38:21Z to 17:41:04Z). Each payload carries its own switch: `_bill_estimate_reads_the_annualised_advance`
is False in `control.json` and True in `annualised.json`. Both books bill 53,110 bills, and the
error population (estimated bills after the account's first actual bill, true use above 0) holds
the same count in every year under both arms, so the comparison is between the same bills. Graded
in one process (a scratch script that reads both files and nothing else, not kept) against the
instrument in section 2.

| | prediction | control | annualised | verdict |
|---|---|---|---|---|
| **PA** tail | count of \|catch-up\| ≥ £500 within ±4 of control (point +1) | 30 | **24** (−6) | **REFUTED**, in the favourable direction: the tail improved, which I predicted it would not |
| **PB** money moved | sum \|catch-up\| ratio in [0.70, 0.92] (point 0.83) | £187,975 | £147,136 | **HELD** at 0.783 |
| **PC** D48 error by year | lower in ≥ 8 of 9 years 2017-2025; 2016 within ±1 pp | | | **HELD**: lower in **9 of 9**; 2016 −0.22 pp |
| **PD** 2022-23 overcharges | negative catch-ups closing 2022-23, ratio in [0.75, 1.00] (point 0.92) | −£35,740 | −£28,241 | **HELD** at 0.790 (0.784 if keyed on the catch-up's run end, not the bill) |
| **PE** PROS-2017-0336 | its 2021-23 catch-up becomes a credit of £2,000-£6,000 | +£4,224.94 | **−£1,451.63** | **REFUTED**: the sign turned as predicted, but the credit is below the band |

### D48 estimated-bill error by year (the arms, not the projection)

| year | est. bills | billed/true, control | annualised | mean \|bill err\|, control | annualised | change |
|---|---|---|---|---|---|---|
| 2016 | 1,585 | 1.056 | 1.063 | 19.9% | 19.7% | −0.22 pp |
| 2017 | 4,697 | 1.008 | 1.002 | 16.2% | 15.6% | −0.59 pp |
| 2018 | 4,457 | 0.997 | 0.986 | 16.0% | 15.0% | −0.99 pp |
| 2019 | 3,759 | 1.006 | 0.996 | 16.9% | 15.6% | −1.31 pp |
| 2020 | 3,369 | 1.035 | 1.017 | 17.3% | 15.6% | −1.70 pp |
| 2021 | 3,150 | 1.011 | 0.994 | 17.2% | 16.1% | −1.08 pp |
| 2022 | 3,157 | 1.020 | 1.014 | 15.3% | 14.6% | −0.64 pp |
| 2023 | 3,189 | 1.019 | 1.007 | 15.4% | 14.3% | −1.09 pp |
| 2024 | 3,113 | 1.003 | 0.987 | 14.7% | 13.3% | −1.35 pp |
| 2025 | 1,548 | 1.001 | 0.995 | 15.6% | 14.6% | −0.98 pp |

The per-bill error falls in every year. Pooled billed/true does not uniformly move toward 1: it
does in 2017, 2019-2023 and 2025, and overshoots to the low side in 2016, 2018 and 2024 (0.986,
0.987). The annualised estimate leans slightly low in those years; it is not a bias the
three-read estimate was free of (it leaned high in 2020 by 3.5%).

### Catch-ups by year

| year | overcharges ≤ −£500, control | annualised | undercharges ≥ £500, control | annualised | overcharge sum, control | annualised | sum \|catch-up\|, control | annualised |
|---|---|---|---|---|---|---|---|---|
| 2016 | 0 | 0 | 0 | 0 | −1,454 | −1,497 | 5,106 | 5,122 |
| 2017 | 1 | 1 | 3 | 3 | −8,492 | −9,051 | 20,528 | 20,262 |
| 2018 | 1 | 1 | 3 | 3 | −8,036 | −5,884 | 17,482 | 13,827 |
| 2019 | 0 | 0 | 1 | 3 | −6,732 | −4,780 | 14,593 | 11,574 |
| 2020 | 1 | 0 | 1 | 0 | −8,441 | −4,316 | 14,335 | 8,694 |
| 2021 | 0 | 0 | 1 | 1 | −6,714 | −4,530 | 12,467 | 10,220 |
| 2022 | 0 | 0 | 1 | 1 | −10,445 | −7,780 | 17,961 | 13,882 |
| 2023 | 6 | 2 | 4 | 2 | −25,295 | −20,461 | 45,969 | 33,104 |
| 2024 | 2 | 2 | 2 | 2 | −15,225 | −10,562 | 27,335 | 21,136 |
| 2025 | 1 | 1 | 2 | 2 | −6,125 | −4,714 | 12,199 | 9,317 |

Catch-ups raised: 4,485 to 4,256. 2023, the year of the large overcharges, carries most of the
gain: £500+ catch-ups 10 to 4, sum |catch-up| −£12.9k.

### Every catch-up of £500 or more

**Gone under the annualised arm (9), plus one sign change:** SYN-2016-565 2020-02 +£702.00; PROS-2017-0336 2020-06
−£2,035.05; SYN-2016-487 2023-03 −£555.20; PROS-2018-0016g 2023-04 −£784.69; PROS-2018-0137g
2023-04 +£570.16; SYN-2016-531g 2023-04 −£754.66; OCC-564700946c93 2023-09 −£630.52;
SYN-2016-150g 2023-11 −£728.43; SYN-2016-221 2024-08 −£509.62. PROS-2017-0336's 2023-03
catch-up stays over £500 but changes sign (below). 30 − 9 + 3 = 24.

**New under the annualised arm (3):** PROS-2017-0336 2019-02 +£532.19 (was +£292.94);
SYN-2016-565 2019-05 +£786.18 (was under £500); SYN-2016-565 2024-07 −£1,796.83 (was under £500).

**Shrunk:** SYN-2016-042 +£1,117.18 → +£654.49; SYN-2016-225 2018-05 +£761.13 → +£500.12;
SYN-2016-565 2022-07 +£1,054.21 → +£1,024.30;
SYN-2016-565 2023-04 +£3,464.34 → +£2,435.00; SYN-2016-221 2024-01 −£1,680.65 → −£1,075.86;
PROS-2017-0336 2025-03 +£2,179.81 → +£904.17.
**Grew** (0336 also grew on its new 2019-02 catch-up and on one under £500, 2023-11): PROS-2017-0336 2021-05 +£576.45 → +£1,022.11; 2023-09 −£1,146.23 → −£1,451.48; 2024-07
+£1,710.29 → +£2,316.45; 2025-06 −£657.93 → −£758.60; and 2018-11 −£1,290.75 → −£1,364.81.
**Unchanged to the penny (9):** SYN-2016-225 2017-05, SYN-2016-582 2017-07, PROS-2017-0117 2017-11,
PROS-2017-0336 2018-02, OCC-b1aaf5ab7f3d 2018-09, PROS-2017-0233 2019-08, PROS-2022-0178 2023-06,
PROS-2024-0010 2024-05, PROS-2025-0106 2025-06. Most are early in an account's life, consistent
with the build falling back to three reads where no 182-day advance exists; I did not check each.

### PROS-2017-0336

Its 2021-06 to 2023-02 run closes at **−£1,451.63** (a credit) under the annualised arm, against
+£4,224.94 under control. The swing is £5,676.57, so the advance overshoots by about a third of the
three-read miss, not by the +22% the section-1 projection implied (which would have
put the credit near the middle of PE's band). Of its 14 catch-ups, the annualised arm shrinks the
absolute value of 4, grows 7 and leaves 3 alone: its total |catch-up| goes from £15,845 to
£11,860; the 2023-03 and 2020-06 runs carry most of the fall. It is still the book's largest
source of catch-ups under both methods (next: SYN-2016-565, £8,461 → £8,577). A
high-use electrically heated home whose use moves year to year is not what either method fixes.

### Where the projection in section 1 was wrong

The projection predicted the tail at 30 to 31 and PA was registered on it. The arm gives 24. The
linear kWh scaling ignores everything a re-run changes besides one run's kWh. My unchecked
hypothesis is that a smaller estimate error compounds into later runs (a nearer DD, a nearer
opening level), which the projection cannot see. The four "new" catch-ups the
projection listed (SYN-2016-169g, PROS-2020-0016g, SYN-2021-001, SYN-2016-565 −£2,934) did not
appear at £500+ in the arm except SYN-2016-565's, at −£1,797. The projection under-stated the
benefit. PE was refuted for the same reason in the other sense: the projection over-stated the
overshoot on 0336.

### The other side of the ledger (M2)

Company net falls £318.89 (£716,914.02 to £716,595.13), all of it in bad debt
(£8,265.72 to £8,584.61). Customers are billed closer to what they used and £40.8k less money moves
by catch-up. This is accuracy, not a transfer: the bills are nearer the truth in every year. I
cannot yet say which accounts carry the +£319 of bad debt; it is small against the catch-up change
and I did not chase it in this turn.

### Decision rule applied

**PB held, PC held, and PA did not rise (it fell by 6).** The rule fixed in section 2 says the
seat proposes default on in `for_the_director` with these arms. Raised as a concern; the switch
stays off until he answers. **Next variant: the gas 9-month floor** (Xoserve's AQ minimum, K2
design choice 1), then a cap on the advance's weight against the three-read level for an account
whose recent reads diverge, the change aimed at accounts like PROS-2017-0336.
