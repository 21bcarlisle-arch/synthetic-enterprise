**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Four phase 4c tests have been red on main since a prepayment leg stopped being sent estimated bills (2026-10-27)

Found by the worker tick taking a W2_36 slice (the hub-shared smart-mode draw), while running
`tests/simulation/test_run_phase4c_on_phase2b.py` before landing. The tick confirmed the reds are
not its own: on a clean worktree at HEAD `26cc72f7b` **without** the slice, the first two below
fail the same way (2 failed, 687 s). Nothing in `HEAD_RED_REGISTER.md` or staging named them.

**The four, at HEAD 26cc72f7b:**
1. `test_main_produces_meter_read_log_matching_bills`: a bill's `billing_basis` is
   `prepayment_meter` where the meter-read log's status is `actual`. The test still holds the
   basis set to `{actual, estimated}`.
2. `test_an_estimated_run_past_12_months_is_not_forced_and_its_final_read_meets_the_cap`
3. `test_billing_accuracy_finds_the_barred_energy_the_read_process_makes_and_none_when_every_read_is_actual`
4. `test_main_window_closes_a_churned_account_on_an_actual_read_only_where_the_world_has_a_reason`
   (the K2/K3 grade reads `0.0` where the test needs `> 0`).

**Cause (read, not run per test).** `3e19e5676` (26 Oct 22:12) made a prepayment leg get a meter
charge and a statement, never an estimated credit bill. Tests 2 and 3 take **C4** as their
subject because "the registry's non-direct-debit homes are prepayment". C4 now has no estimated
run, so the SLC 21BA cap on the estimate has no subject. Test 1's basis domain predates the new
basis. That commit's own landing selection did not include this file.

**What would close it (the D lane's call, not made here).** The back-billing cap on the estimate
needs a non-DD *credit* subject, such as a quarterly on-receipt payer. The registry has none.
There are two ways out: give the fixture one such account, or state in the tests that the cap on
the estimate has no subject on the registry book, and keep the DD arm. Test 1 should accept
`prepayment_meter` only where the leg's channel is prepayment, which keys it to the property. It
should not just widen the set.

**Interconnection.** Every landing whose selection pulls in this file goes red on these four and
names a file it did not touch.
