# The gas estimate floors the annualised advance at nine months: projection and prereg

**Direction item:** `the-gas-estimate-floors-the-annualised-advance-at-nine-months` (worker, 2026-10-22)
**Knowledge (K8):** `docs/market_research/unbilled_energy_and_revenue_assurance.md` K2, "Design choice 1
amended: gas may take the AQ's own floor".
**Built default off:** `DecisionPolicy.bill_estimate_floors_the_gas_advance_at_nine_months` →
`build_monthly_bills(gas_advance_floor_nine_months=...)` → `annualised_advance_kwh(...,
min_advance_days=GAS_AQ_MIN_ADVANCE_DAYS)`. It does nothing unless
`bill_estimate_reads_the_annualised_advance` is also on. Control:
`tests/company/billing/test_the_gas_estimate_floors_the_advance_at_nine_months.py`.
**Base:** the annualised arm of
`WORKER_PREREG_THE_BILL_ESTIMATE_READS_THE_ANNUALISED_ADVANCE_2026-10-22.md` (default-on is proposed to
the director and not yet answered). The floor is measured against the advance, not against three reads.
*Corrected 2026-10-24: the default-on was answered. The advance has defaulted ON on every standing
policy since the director's 23 Oct ruling (82f4b20bc). So the `annualised` arm below is the standing
policy and the `--annualised-advance` flag is now redundant but harmless. The floor stays off.*

## 1. The one-variable projection (read-only, before the build)

- **Run:** `/var/tmp/se-annualised-arms-out/annualised.json`, the annualised arm at 30674a4bd.
- **One process, one change.** For every gas bill, the register reads are rebuilt from the bills:
  the change-of-supply opening read at 0, then each actual bill's period end at cumulative true use.
  Every estimated gas bill after the first read is re-estimated with the 182-day floor and with the
  273-day floor, each falling back to the latest three actual periods. The 182-day leg reproduces
  the billed estimate on **14,462 of 14,616** bills (99.0%). The 154 misses are not chased here.
- **True use** is the world's `true_consumption_kwh`, used only to grade.

| year | gas est. bills | moved by the floor | mean \|err\|, 182 | 273 | on the moved bills, 182 | 273 |
|---|---|---|---|---|---|---|
| 2016 | 783 | 92 | 28.98% | 29.16% | 21.8% | 23.4% |
| 2017 | 2,193 | 472 | 21.25% | 21.62% | 20.4% | 22.1% |
| 2018 | 2,049 | 218 | 19.44% | 19.41% | 19.5% | 19.2% |
| 2019 | 1,706 | 176 | 21.71% | 21.72% | 21.4% | 21.5% |
| 2020 | 1,500 | 158 | 20.83% | 20.93% | 17.8% | 18.8% |
| 2021 | 1,427 | 134 | 21.23% | 21.19% | 19.2% | 18.7% |
| 2022 | 1,409 | 120 | 18.23% | 17.94% | 22.6% | 19.3% |
| 2023 | 1,440 | 113 | 17.36% | 17.21% | 20.8% | 18.9% |
| 2024 | 1,412 | 123 | 16.48% | 16.33% | 17.1% | 15.3% |
| 2025 | 697 | 49 | 17.07% | 16.88% | 18.5% | 15.7% |

**Pooled, 2016-2025: 20.08% against 20.09%. The projection says the floor is a wash on gas error.**
It moves 1,655 bills, 11% of the gas estimates. In 2016-2017 a 6-8 month advance beats three
monthly reads, because the three reads are the only alternative early in an account's life. From
2021 the floor helps: a short advance there is more often a recent one struck across one season.

Span of the advance the 182-day floor chose, in months (bills): 6: 366, 7: 567, 8: 694, 9: 800,
10: 1,383, 11: 1,622, 12: 2,397, 13+: 4,537. The floor reaches the 6-8 month spans (1,627 bills,
near the 1,655 moved) plus the shortest end of month 9.

## 2. Pre-registration (filed before either arm runs)

**Arms.** Both run at one commit, serially, from a locked worktree at origin/main after this
record lands, through `background.launch_long_job`:
- `annualised`: `python3 -m tools.read_instruction_arms register <out>/annualised.json --annualised-advance`.
- `floor`: the same, plus `--gas-nine-month-floor`.

Outputs go to `/var/tmp/se-gasfloor-arms-out/`. Nothing reads or writes the earlier arms' directories.

**Instrument.** As in the annualised prereg, section 2: estimated-bill error is
|`total_consumption_kwh` / `true_consumption_kwh` − 1| over `billing_basis == "estimated"` bills
with true use above 0 after the account's first actual bill, by `period_start` year, **here split by
fuel**. A catch-up is `catchup_adjustment_gbp` on a bill.

**Predictions** (floor against annualised, same commit):
- **PF1. Electricity does not move.** At least 99% of electricity bills have the same
  `total_consumption_kwh` to the penny-kWh (0.01) in both arms. 85%. A miss means the floor leaks
  across fuels or a second-order path (a dual household's shared DD, a read instruction) moves an
  electricity estimate.
- **PF2. Pooled gas error is a wash.** The mean per-bill gas error 2016-2025, floor minus
  annualised, is within ±0.3 pp (point 0.0). 70%.
- **PF3. The year split.** Gas error is higher under the floor in both 2016 and 2017, and lower in
  at least 4 of the 5 years 2021-2025. 55%. The projection gives exactly this. The arm compounds
  effects the projection cannot see (section 4 of the annualised prereg), so it is held loosely.
- **PF4. Money moved by catch-ups.** Sum |catch-up| over all bills, floor / annualised, in
  [0.95, 1.05] (point 1.00). 70%.
- **PF5. Tail.** The count of |catch-up| ≥ £500 is within ±3 of the annualised arm's (point 0). 75%.

**Decision rule, fixed now.**
- **The floor is proposed only if it is better on the money and no worse on the bill:** pooled gas
  error lower by at least 0.3 pp, PF4's ratio at or under 0.97, and PF5's count not higher. Then
  the seat adds it to the default-on proposal already in `for_the_director`.
- **Otherwise the switch stays off.** The D48 record says the AQ's floor, a settlement rule, does
  not make a better bill estimate on this book, with the numbers. The six-month floor stands for
  both fuels.
- **Next in either case:** the cap on the advance's weight against the three-read level for an
  account whose recent reads diverge (the annualised prereg, section 4), aimed at PROS-2017-0336.

## 3. Launch

*Build landed 2026-10-24 from the shared working tree, where it sat uncommitted for two days and held the
checkout behind origin. Delivery item `the-gas-floor-build-in-the-shared-tree-lands-or-yields`.
`tools/read_instruction_arms.py` was re-based onto origin's tri-state advance flag: the floor is now
refused when the arm's EFFECTIVE policy has the advance off, and the payload stamps the policy's own
value. Neither arm has been launched.*

*(filled at launch: the commit, the unit, the times. No outcome has been read.)*
