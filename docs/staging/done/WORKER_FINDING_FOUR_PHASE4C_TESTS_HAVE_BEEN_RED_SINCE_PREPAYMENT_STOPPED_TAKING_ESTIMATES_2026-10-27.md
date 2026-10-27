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

## Done

Delivery seat, 27 Oct 2026, item `the-phase4c-tests-are-keyed-to-the-prepayment-basis`. All 55 tests
in the file pass on the worktree (789 s, one module-scoped `main(report_end="2018-12-31")`).

**Corrections to the record above.**
- "The registry has none" holds only for C1-C9. The live book has standard-credit homes:
  `SYN-2016-002` (both fuels) is one.
- The "K2/K3 grade reads `0.0`" failure is **test 3's**, not test 4's. A meter-charged leg has no
  estimated kWh, so every K2/K3 share on C4 is 0.0 by construction.
- Test 4 had two causes. 37 churned prepayment legs close on `prepayment_meter`, which is not a
  read status. Separately, one gas leg (`OCC-3c914ee8cef5g`) is the per-fuel smart-mode draw
  (c77a181fa4, b67d8c3ee4): its household draw of 0.077 is in smart mode at electricity's 6.8%
  share and out of it at gas's 14.2%. The test's oracle asked with no commodity, so it judged
  a gas leg by the electricity share. The second cause is not prepayment's, and the run found it.

**What changed (tests only; no product code moved).**
1. Test 1 is keyed to the channel. A bill on a prepayment channel must be `prepayment_meter`, with
   `settlement_read_status` equal to the log's status. Any other bill's basis must equal the log's
   status. Both sides of the partition must be present. The set of bases was not widened.
2. Tests 2 and 3 use a standard-credit subject (`_on_receipt_home`, which asserts the channel
   rather than assuming it). SLC 21BA's cap on an estimate binds where the bill is the demand, and a
   prepayment meter charges true use, so it has no estimate to cap. The DD arm of test 2 is kept.
3. Test 4 reads a meter-charged leg's closing read from `settlement_read_status` and asks smart
   mode and `simulate_read` with the bill's own fuel.

**Mutations, each red.** Mutations 1-3 ran against a pickled run, the rest live.
- A credit leg billed as `prepayment_meter` reds test 1.
- A meter-charged period's read status flipped reds test 1.
- Removing every prepayment period reds test 1 on the partition guard.
- Subject back to C4 reds test 2 on the basis list and test 3 on the K2 zero.
- A direct-debit subject reds the channel precondition.
- The fuel dropped from test 4's oracle reds it on the OCC gas leg.
- Reading `billing_basis` instead of `settlement_read_status` reds test 4 on SYN-2016-032.
