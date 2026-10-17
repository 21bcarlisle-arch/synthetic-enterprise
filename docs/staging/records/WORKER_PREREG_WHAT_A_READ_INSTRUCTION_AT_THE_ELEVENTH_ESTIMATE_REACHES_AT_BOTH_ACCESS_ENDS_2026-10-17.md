# Pre-registered: what a read instruction at the 11th estimate reaches, at both access ends

*Filed 2026-10-17, before the grade was written or run. Direction item
`the-company-instructs-a-read-before-the-21b4-year`. Knowledge:
`docs/market_research/read_access_and_theft_duties.md` §2.8.*

**Book:** `/var/tmp/closing-money-run-20261017.json` (cc23de757), the run §2.7 graded. Baseline
from that grade: open closing new demand £3,470.63. 25 open runs crossed the year, 12 of them
undercharges carrying £1,761.88. 198 runs closed inside the year carry £1,708.75. The 21BA bar on
the 12 crossed undercharge runs is £3,929.05.

**Instrument:** `python3 -m tools.closing_estimate_run_money --read-duty`, extended with the
instruction's two ends. It is a decomposition of the run's own bills, not a re-run. At `read`, a
visit on the 12th, 24th, 36th ... estimate in a row reads, so an open closing run keeps only the
estimates after its last visit. At `no_access`, nothing changes.

**Predictions:**
1. `no_access` reproduces the baseline exactly: £3,470.63 open new demand, and £3,929.05 bar on
   the 12 crossed undercharge runs. This is by construction, so it is a check on the instrument,
   not a finding.
2. At `read`, the 198 runs that closed inside the year are untouched: £1,708.75.
3. At `read`, the open new demand on the 25 crossed runs falls from £1,761.88 (undercharges) to
   between **£150 and £600**. What is left is each run's tail after its last visit, which is at most
   11 bills.
4. At `read`, total open closing new demand is between **£1,900 and £2,600**.
5. At `read`, the 21BA bar on what the visits true up is **£0**. Every visit trues up at most 11
   estimates plus its own bill, all inside 12 months.
6. Instructions raised over the whole book are between **1.0 and 1.4 times** the 21B.4 register's
   duty rows. There is one at each year of a run, against the register's one per run, so it is
   never fewer.
7. Instructions on prepayment: **0**.

## Graded (2026-10-17, after the run)

`python3 -m tools.closing_estimate_run_money --read-duty --instructed-read
/var/tmp/closing-money-run-20261017.json`. The DD book was reproduced.

*A correction to the wording above, before grading:* "open new demand" in 1, 3 and 4 means
**undercharge** new demand. Every baseline figure quoted is the undercharge figure (§2.7). Net of
overcharges, the same book's open new demand is £1,333.95. The predictions are graded on the
quantity they quoted.

| # | Predicted | Measured | Verdict |
|---|---|---|---|
| 1 | `no_access` = £3,470.63, with a £3,929.05 bar on the crossed undercharge runs | £3,470.63; £3,929.05 | **held** (instrument check) |
| 2 | £1,708.75 on the runs inside the year, untouched | £2,662.61 − £953.86 = £1,708.75 | **held** |
| 3 | crossed undercharge new demand £1,761.88 → £150–£600 | **£953.86** | **refuted, high** |
| 4 | total undercharge new demand £1,900–£2,600 | **£2,662.61** | **refuted, high** (by £62.61) |
| 5 | bar on what visits true up = £0 | £0.00, on £6,990.56 trued up | **held** |
| 6 | instructions 1.0–1.4× duty rows | 332 (electricity 211, gas 121) / 307 = 1.08 | **held** |
| 7 | prepayment instructions 0 | 0 | **held** |

**Why 3 and 4 missed.** £925.08 of the £953.86 is C7's last 6 bills, after its last visit at the
36th estimate. The other 11 crossed undercharge runs keep £28.78 between them. I predicted a tail
of at most 11 bills would be small. That is wrong for C7, an EV home billed on the TDCV fallback
(D48 finding), whose estimate is far below its use in every month. The decomposition keeps that
estimate after the visit. A real run would re-estimate from the visit's read, so C7's tail is an
overstatement at the read end, of a size this instrument cannot give.
