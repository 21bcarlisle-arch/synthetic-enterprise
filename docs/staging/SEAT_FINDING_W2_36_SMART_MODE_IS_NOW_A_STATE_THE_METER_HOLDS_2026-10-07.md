**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# W2_36: a smart meter out of smart mode now stays out, so a smart home can go a year unread

## What changed

`read_access_and_theft_duties.md` (landed `fbe24afea`) named this as code gap 5. The register row
`q6_smart_not_in_smart_mode_share` said the same: `simulation/meter_reads.py` "types its own 0.10
and draws it afresh each month; it should read this row and hold the state". Both are now done:

- the share is read from the register, so it is no longer typed in the module;
- each account draws its smart-mode state once (`is_not_in_smart_mode`, seeded by its id) and
  holds it for life;
- a home whose meter is out of smart mode is read by the two traditional read classes.

**The exit hazard is not invented.** DESNZ and Ofgem publish the stock, not the transitions
(gap 9), and the 90-day repair duty starts in 2026, after the window. "Held for life" is the
persistent end of the range. The old monthly draw was the memoryless end, and the register says
the truth is a state. The module records the gap in a comment, not as a placeholder number.

## Measured, against a prediction written first

Smart meters, 4,000 accounts × 120 months, `simulate_read` itself, HEAD against the change in one
process:

| | actual-read share | 12-month windows with no read | traditional-mode share |
|---|---|---|---|
| HEAD (monthly draw) | 0.8972 | 0.0000 | 0.10 of months |
| this change | 0.9011 | **0.0073** | 0.095 of accounts |

The prediction was 0.10 × 0.07 ≈ 0.007, and it held. The level of estimation hardly moves. What
changes is who carries it: before, every smart home had an estimated bill now and then and none
ever went a year unread. Now about a tenth carry all of it, and a smart home can reach the 12-month
back-billing limit.

## Controls

`tests/simulation/test_meter_reads.py::test_a_smart_meter_out_of_smart_mode_stays_out_so_its_home_can_go_a_year_unread`
asserts that both modes are reachable, that the share matches the register, that an
out-of-mode home can go a year unread, and that an in-mode home cannot. Two mutations each turned
it red: restoring the monthly draw, and making `is_not_in_smart_mode` always False. The register
leg is added to `test_the_read_process_is_read_from_the_assumption_register`.
`test_traditional_meters_estimated_more_often_than_smart` used to compare one smart id ("C2") with
one traditional id. C2 now holds traditional mode for life, so the test compares populations.
`tests/simulation/test_run_phase4c_on_phase2b.py`'s `_realistic_36_month_records` said it drew "a real
traditional-meter customer" and defaulted to C1, which is smart in `saas/customers`. Its estimated
bills came only from smart mode redrawn monthly, so it went red (one-variable control: green on
HEAD's module, red on this one). It now defaults to C3, which is traditional. The byte-identity
test, which forces every read, names C1 explicitly.

## Not done, still open

- **Key both read traits to the premise, not the account.** A locked cupboard, a landlord's key
  and poor WAN coverage outlive a tenant (Ofgem 2018 p.8). `ReadArrivalFeed.read_for` receives only
  `customer_id`, so this crosses the seam and belongs to the interface steward.
- **Re-run Q2's barred-revenue invariance.** Smart homes now add to the unread tail. The Q2 proof
  covered traditional meters only, so its invariance claim should be re-measured on the full run
  (owed to D48 with the π sweep).
- The read-visit lever (gap 1) still waits on the practitioner question the note holds.
