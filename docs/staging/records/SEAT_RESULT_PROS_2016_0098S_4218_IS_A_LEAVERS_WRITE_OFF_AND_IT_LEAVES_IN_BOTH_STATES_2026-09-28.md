**Severity:** LATENT · **Lane:** D_billing_metering · **Atom:** `unminted` · **Class:** `measurements_that_mirror`

# PROS-2016-0098's −£4,218.43 is a leaver's write-off at close, and the account leaves in BOTH states

**2026-09-28.** This answers the question left open in
`SEAT_RESULT_THE_C1_BRACKET_RUNS_A_AND_B_GRADED_AND_C_PREDICTED_2026-09-28.md` §"What (b) shows".
It re-simulates nothing. It reads `/var/tmp/se-c1-bracket-{a,b}/value_cycle_ab.json`, their logs
`/var/tmp/longjob-c1-bracket-{a,b}-20260928.log`, and the engine at `fcba478b7`.

## Prediction, written at 14:49Z before opening either artefact

> I expect reading (1). The −£4,218 is the account's contribution margin over months it is on book
> in one state and off book in the other, not a failed-DD balance. Confidence about 70%. The main
> way this is wrong is that the diff is a leaver-fate write-off of unpaid bills. That is still
> reading (1)'s "not an open failed-DD balance", but it is not margin.

**Grade: reading right, mechanism wrong.** The mechanism is the alternative I named. The margin
goes the **other** way, in the account's favour.

## The frame was wrong first: there is no stay/leave pair

The account leaves in every one of the six arm-runs. What changes is **when** it leaves.

| arm, seed | leaves at | 1st renewal `p_retain` vs roll | bills (4c) |
|---|---|---|---|
| level, 11111 (low state) | **2017-03-23** | 0.2688 < 0.3763 → churned | 13 |
| level, 88888 (high state) | 2020-03-22 | 0.6254 > 0.3763 → renewed | 49 |
| value, both seeds | 2020-03-22 | — | 49 |
| control, both seeds | 2020-03-22 | — | 49 |

The roll is the same in every run. The elasticity re-draw moves the level arm's first-renewal
`p_retain` from 0.63 to 0.27, and that alone decides whether the household leaves in 2017 or in
2020. Every run then sends it through `[CHURN]`, and so through
`churned_billing_accounts.add(billing_account)` (`simulation/run_phase2b.py`, the retention-churn
branch).

## The ledger lines, level arm (the only arm that moves; the value arm is −£4,030.97 in both)

`level_arm_net_by_account_gbp` is `net_margin_gbp` summed **after** phase 4c's arrears engine has
replaced the flat placeholder `bad_debt_gbp` (`tools/run_value_cycle_ab.py::_net_by_billing_account`).
The log's per-customer lifetime P&L is printed **before** that replacement. The difference between
the two is the arrears engine's line for the account.

| line | leaves 2017 (11111) | leaves 2020 (88888) | diff |
|---|---|---|---|
| gross margin (`margin_gbp`) | 2,134.53 | 9,015.38 | |
| capital cost | 3.51 | 65.52 | |
| trading net after placeholder bad debt (pre-4c) | **294.29** | **1,735.67** | **+1,441.38** |
| arrears engine: write-off at close − DCA recovery − placeholder released | **+67.28** | **−5,592.53** | **−5,659.81** |
| leg 4b stayer provision | 0 (leaver) | 0 (leaver) | 0 |
| **realised net (artefact)** | **361.57** | **−3,856.86** | **−4,218.43** |

It closes to the penny. The same lines hold in (b): same pre-4c nets, same churn dates, and the
level arm's `[leg 4b]` is £1,931.58 in both seeds, which a leaver in both states predicts.

In words: keeping the household three more years earns £1,441 more trading margin. It also runs up
unpaid bills, which `balance_settlement_from_outcomes` writes off in full at the 2020-03-22 close
(`LEG_CLOSE`, because `cid in churned_ids`). That write-off is £5,660 net of the released
placeholder and of recovery.

**Not established from these artefacts:** how the −£5,659.81 splits between gross write-off, DCA
recovery and released placeholder, and which payment method the failed bills were on. The artefact
carries no per-account arrears lines, and the log prints none. I did not re-simulate to get them,
because the brief forbids it and a 6 GB run is in flight. Closing this needs a per-account
`bad_debt` / `recovered` column in the value-cycle artefact. That belongs to the next value-cycle
change, not to a re-run.

## Which reading holds

- **Reading (1) HOLDS, in its second form.** The £4,218 is a leaver-fate write-off that leg 4b
  excludes by design (`simulation/arrears_engine.py::stayer_provision_charges` skips
  `cid in churned_ids`). It is not an open failed-DD balance that leg 4b could provision in one
  state and not the other. Taken literally, the first clause is not quite right. In the 2020 state
  the account very likely does carry an open failed balance at the 31 Decembers of 2017–2019.
  That balance is correctly outside leg 4b, because the account leaves.
- **Reading (2) is REFUTED.** `churned_ids` carries exactly what happened: the account left in both
  states, and it is in `churned_ids` in both. There is no stay/leave split for it to drop, so there
  is no wiring defect and no finding to file.

## What this means for the thesis and for C4 to C6

- **The per-customer arm inferred nothing here.** The value arm's net on this account is identical
  in both seeds, and it keeps the account to 2020 in both. The whole selection signal is the
  **level** arm's elasticity draw. In seed 11111 the flat uplift happens to drive out, in 2017, a
  household that would go on to cost £5,660 in write-off. Seed 11111's −£3,508 selection is the
  level arm's luck on one coin, and the value arm has no skill in it. The thesis's first question
  therefore still has no answer from this bracket, whatever (c) returns.
- **C4's refuted mechanism is explained.** Leg 4b cannot reach this account in either state.
- **C5 and C6 rest on a false premise.** They assume the state-switching household is a stayer in
  one state. It is a leaver in both. My prediction for (c) is unchanged, and firmer: leg 4b is blind
  to this account under every C1 bucket, so the state distance stays at −£4,214.93 ± £1.
- **This number will move for a reason that has nothing to do with C1.** `fcba478b7` predates
  `254b4c1e4`, which releases this account's scale-held bills. It also predates `e83d571c3`, where
  the world answers the listing lookup. Held bills never reach `issued_bills`, so they can neither
  fail nor be written off. Any later run moves this account's write-off. **Prediction, filed now:**
  at HEAD this account's arrears line grows in magnitude past −£5,659.81, because more issued bills
  means more that can fail. The selection sign then depends even more on this one household, not
  less.
