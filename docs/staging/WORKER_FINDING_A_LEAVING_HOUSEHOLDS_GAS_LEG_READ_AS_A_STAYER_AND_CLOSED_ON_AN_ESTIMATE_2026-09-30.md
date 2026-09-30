**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none (HEAD red register, `tests/tools/test_bill_correctness_addendum_defect4.py`)
**Evidence:** `tests/simulation/test_a_leaving_households_gas_leg_is_a_leaver.py`, `tests/tools/test_bill_correctness_addendum_defect4.py`

# A leaving household's gas leg read as a stayer, and the defect-4 gate was reading two catch-up shapes as breaks

**2026-09-30.** Found by a scheduled-tick worker drawing the HEAD red register. PB6 was not
drawable: its next step is the re-centred null arm, which is queued behind the ab5 lineage legs
(`longjob-pb6-null-arm-recentred-prior`).

## The register is a week stale

It was last rendered 2026-09-23. Of its four longest-standing reds, three now pass at HEAD:
`test_home_move_undeliverable_win` (2), `test_billing_tab_fix` (2) and
`test_price_response_curve_position_split` (1). `test_bill_correctness_addendum_defect4` was
still red, with 11 inversions on the 2026-09-28 book.

## The 11, by cause

| cause | cases | disposition |
|---|---|---|
| **A. The catch-up lands in the next year.** The 2026-08-24 netting removed the adjustment from the year it lands in, but never credited it back to the year it corrects. | SYN-2016-014 2016, SYN-2016-052 2016, SYN-2016-055 2019/2020/2023, SYN-2016-050 2021 | **Gate fixed.** The adjustment is re-attributed over `catchup_period_start..end` by day. Total conserved. |
| **B. The leg is still on supply at the window's end with an unresolved estimate.** The margin is on true consumption and the bill is on the estimate. Neither side is final. | PROS-2024-0197 2024, 2025 | **Gate fixed.** These are provisional and excluded. Only legs whose last invoice is in the window's final month qualify. A leaver is never provisional. |
| **C. The gas leg of a leaving household got no final read.** | PROS-2020-0132 2021 | **Code fixed.** See below. Clears on the next published run. |
| **D. A leaver's final actual bill is held by `validate_bills`.** | PROS-2016-0092 2017 (2,066.9 kWh Feb), PROS-2016-0098 2020 (1,537.1 kWh, forced catch-up) | **Open.** These are two of the three "actual" holds left by `SEAT_FINDING_FIVE_OF_THE_EIGHT_REMAINING_HELD_BILLS...`. A held final bill is never released, so the true-up is never billed. |

C and D are named in the gate's `KNOWN_OPEN_INVERSIONS`, each with its cause. They are named
rather than xfailed, so any other inversion still reds the gate. Delete each entry when its cause
lands. Without the allowance, this commit could not land: the gate selects a changed test file as
itself.

**Correction beside the claim.** My first provisional rule was "an estimate with no later actual
read". On the real book it excused 95 account-years, and most of them were leavers' gas legs
(cause C) and held finals (cause D). Those are exactly what the gate exists to catch. Keying the
rule to "still on supply at the window's end" cut it to 68, all in 2024-2025.
`test_only_a_leg_still_on_supply_can_hold_a_provisional_year` reds when the earlier rule is
restored (mutation run).

## C, the defect

`churned_billing_accounts` is keyed by household (`C1`). Every consumer in
`run_phase4c_on_phase2b.main` and `tools/generate_billing_ledger` tested
`bill["customer_id"] in roster`, and a bill is keyed by supply point (`C1g`). So the gas leg of
every leaving household was a stayer:

- `build_monthly_bills` gave it no SLC 21B final read. On the 2026-09-28 book there were 28 such
  legs, and **17 closed on an estimate**. All 92 electricity legs matched the roster: 89 closed on
  an actual read, and the other 3 are held finals (cause D).
- `arrears_engine` (`stayer_provision_charges`, `balance_settlement_from_outcomes`) priced their
  failed bills as a stayer's rather than writing them off at close.
- `generate_credit_refund_log` never raised their SLC 14 closure refund.
- The live control `test_main_window_holds_a_churned_accounts_final_read` asked the same
  bare-roster question, so it was blind to the same legs.

**Fix:** `simulation.household.supply_points_that_left(roster, supply_point_ids)`. It is used at
both places the set is built, and in the ledger/P&L agreement control. The live control now reads
by `household_of`. **Expected on the next run:** gas-leg final reads rise by up to 17. Leavers'
gas-leg failed bills move from stayer provision to write-off at close, so `bad_debt_gbp` moves.
I cannot yet say by how much.

## Not done, noted

- `saas/reporting/annual_report.py` ~4098 marks bill-shock events as churned by
  `ev["customer_id"] in churned_billing_accounts`. That is the same shape on the supplier side,
  which cannot import the world's helper. It needs `saas.customer_reaction._billing_account_id`.
- **In 19 of the 28 leaving dual-fuel households, the two legs' last bills fall on different
  dates.** Mostly the gas leg ends a quarter earlier. In PROS-2017-0065 and PROS-2020-0132 the gas
  leg outlives the electricity leg by months. One departure should end both legs. Unexplained.
- PROS-2024-0197, a one-person private renter, used 4,220 kWh of electricity in January 2025 and
  about 22 MWh over its 12 months (`fabric_physics` demand). The trailing-3 estimator billed it
  307 kWh a month. The seasonal half is the estimator gap the held-bills finding already names.
  The level looks absurd for the dwelling and has not been checked against the property record.
