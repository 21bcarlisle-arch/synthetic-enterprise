**Severity:** INFO · **Lane:** B_commercial · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Claim:** `repair-the-flat-arms-reachability-control` (Lane 0 delivery)

# The flat arm's reachability repair was spent by abe7ce533 before it was drawn

Delivery seat, 2026-10-20. Drawn item: repair
`test_the_flat_supplier_policy_makes_no_retention_offer.py::test_a_run_under_the_flat_supplier_makes_no_retention_offer`,
without moving `WINDOW_END`, by a fixture policy that differs only in the guard's floor.

**Premise re-measured: spent.** `abe7ce533` (origin/main tip at draw, claim
`repair-the-flat-supplier-reachability-leg`) landed the repair and moved the source finding to
`done/`. The item's DONE holds: the leaking-flat mutation (`retention_tiers=((0.0, 0.03),)`) is
KILLED on all three flat legs, the gate is green (receipt rc 0), and the finding has left the root.

**Departures from the item's shape, and why they stand.** The item said "do not move WINDOW_END".
That rested on the inherited diagnosis that `c61d8b608` emptied 2016. The landing measured that
2016 holds 3 renewals and none of them gets past the churn threshold, so neither arm is ever asked
by the guard. No guard-floor fixture can make a 2016 window reach the guard. Moving to 2017-12-31
is not keying the control to today's answer. The control now asserts the property (current reaches
the cut: offers plus withheld-after-cut > 0, independent of the guard's economics) before asserting
flat's zero, which is the one-control-over-the-partition shape the item asked for. The fixture
policy is therefore not needed. Nothing was rebuilt.

**Observed, not mine:** at draw the shared tree had this test file deleted on disk while it is
tracked at HEAD. That is shared-tree checkout dirt (the same `git status` shows many `AD` staging
rows). It is not a defect on origin.
