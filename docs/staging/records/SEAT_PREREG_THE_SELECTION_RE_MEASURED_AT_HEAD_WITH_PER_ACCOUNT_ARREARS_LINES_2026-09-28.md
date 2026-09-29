**Severity:** RECORDED · **Lane:** D_billing_metering · **Claim:** `re-measure-the-selection-at-head-with-per-account-arrears-lines`

# Prereg: the selection re-measured at HEAD, through per-account arrears lines

**Written 2026-09-28 ~22:40Z, before any run. It lands in the same commit as the instrument, so the
run is at that commit.** The grading goes in `SEAT_RESULT_` beside this file.

## Why

Every graded run is at `fcba478b7`. That commit predates the held-bill release (`254b4c1e4`) and the
listing lookup (`e83d571c3`), the held-bill and credit-bill write-off fixes, and credit netting. Those
are the rules that make up `PROS-2016-0098`, and the selection sign rests on that one account. The C1
bracket could not split its −£5,659.81 arrears line, because the artefact had no per-account lines
(`records/SEAT_RESULT_PROS_2016_0098S_4218_IS_A_LEAVERS_WRITE_OFF_AND_IT_LEAVES_IN_BOTH_STATES_2026-09-28.md`).

## The instrument, landed in this commit

- `simulation/arrears_engine.py::emergent_bad_debt_lines` returns the charge split by line:
  write-off at close, statute-barred write-off, and leg 4b stayer provision.
  `compute_emergent_bad_debt` is now that split's `"total"`, and its figures are unchanged.
- `book_arrears_lines` books through the unchanged `apply_emergent_bad_debt` and
  `apply_debt_recovery`. It returns each customer's lines: pre-4c net, placeholder released, the
  three charge lines, line rounding, unbooked bad debt, DCA recovery and unbooked recovery.
- `tools/run_value_cycle_ab.py` folds those lines to the billing account and grades
  `arrears_reconciliation`, per account, to half a penny. It does this against the same
  `net_by_billing_account_gbp` column that `level_arm_net_by_account_gbp` and
  `value_arm_net_by_account_gbp` are drawn from. Each seed row carries
  `{value,level}_arm_arrears_lines_by_account_gbp`, `{value,level}_arm_arrears_reconciliation` and
  `{value,level}_arm_decisions_by_account`. The decision fields are the leaving date, the first
  renewal's `p_retain` against its roll, the renewal count and the bills issued.
- The control is `tests/tools/test_the_arrears_lines_reconcile_each_accounts_net_to_the_penny.py`.
  Twelve mutations were made across the engine and the tool, and **all 12 go red**. Two of them
  first survived, and the tests that catch them were added:
  - Taking the *last* churn rather than the first.
  - Rounding each folded line to the penny. Nine lines rounded separately can drift 4.5p, which
    refuses a net that was never wrong. This is the same defect as the 1.2p red that the lost
    rebuild's real-run control found.

**The lost rebuild.** An earlier invocation of this claim rebuilt these lines as a superset, in this
worktree, and never landed them. When this turn was drawn, the worktree was clean at origin/main and
no salvage ref held that rebuild. This commit is built from the older stranded shared-tree copy
(`SEAT_DISPOSITION_THE_STRANDED_ARREARS_LINES_…`), plus the rounding fix and the two tests.

## The run

`python3 -u -m tools.run_value_cycle_ab --level-arm --noise-floor-seeds 11111,88888 --out
/var/tmp/se-arrears-lines-head/value_cycle_ab.json` runs as a `background.launch_long_job` unit.
`SIM_STAYER_FAILED_DD_BUCKET` is unset, which is leg 4b at its HEAD default (off). The run is waited
on by `tools.wait_for --pid`. Nothing launches while another value-cycle run holds memory.

## Predictions

- **P0, the instrument.** `arrears_reconciliation.reconciles` is `True` for both arms in both seeds
  (4 of 4). Confidence 80%. The way this fails is a stage after 4c that moves `net_margin_gbp`, or a
  sub-penny accumulation I have not seen. If it fails, it is a finding about the instrument, and
  nothing below is graded until it is fixed.
- **P1 (filed by `875322e5a`, carried verbatim).** "At HEAD this account's arrears line grows in
  magnitude past −£5,659.81, because more issued bills means more that can fail." It is graded on
  the level arm's arrears-line state difference for `PROS-2016-0098`, 11111 − 88888, where the
  arrears line is realised net − pre-4c net. It holds if that difference is < −£5,659.81. My own
  confidence is 60%. The held-bill release adds issued bills to the account, but credit netting
  and the credit-bill fix both pull the other way.
- **P2.** `PROS-2016-0098` still leaves at different dates in the two seeds in the level arm:
  2017-03-23 in 11111 and 2020-03-22 in 88888. Confidence 70%. The roll and the elasticity
  re-draw do not read bills, but a world where a bill reaches a customer can move the reaction
  path.
- **P3.** The state distance, selection(11111) − selection(88888), stays within £500 of
  −£4,214.93. Confidence 45%. If P1 holds, the distance moves more negative by about the growth in
  that account's line, and the growth could be larger than £500. My point estimate is −£4,600.
- **P4.** Both selection signs are unchanged: 11111 negative, 88888 positive. Confidence 70%.

A P1–P4 miss is a result, not a defect. Only a P0 miss stops the grading.
