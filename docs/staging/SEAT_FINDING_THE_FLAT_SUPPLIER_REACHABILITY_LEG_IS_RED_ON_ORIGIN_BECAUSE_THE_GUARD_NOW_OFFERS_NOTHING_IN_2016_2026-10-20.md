**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Claim:** `land-c35s-caller-from-the-se-c35-worktree` (Lane 0 delivery)

# The flat supplier's reachability leg is red on origin: the retention guard now makes no offer in 2016

Found 2026-10-20 ~16:00 BST by the delivery seat, while pre-running the gates for C35's engine caller.

## What fails

`tests/company/policy/test_the_flat_supplier_policy_makes_no_retention_offer.py::test_a_run_under_the_flat_supplier_makes_no_retention_offer`
fails on a clean `origin/main` worktree (`d9ad04e71`), with the C35 change absent:

    AssertionError: {'current': (0, 0), 'flat_supplier': (0, 0)}

The leg's reachability half asserts that `CURRENT_POLICY` offers in the window to `2016-12-31`, so
that the flat arm's zero is the policy's. It no longer offers there.

## Why

`c61d8b608` made the retention guard weigh the term's contribution, not the spread over wholesale.
On the full book, offers fell from 92 to 9 (`records/SEAT_PREREG_THE_RETENTION_GUARD_ON_THE_TERMS_CONTRIBUTION_2026-10-20.md`,
graded in `42d4e8e3d`). The earliest of the nine is 2017-11-15 (`SYN-2016-517`), read from
`/var/tmp/se-ret-margin/off_book.json`. So the 2016 window holds none. The guard is doing what it
was built to do. What broke is the control's premise that the current policy offers in 2016.

## What it means

The flat leg is now unfalsifiable as written. With both arms at zero, a flat arm that still offered
through some route would be no more visible than one that offers nothing. Whether the gate
selects this test for a given commit decides whether it refuses landings. Either way the control
proves nothing until it is repaired.

## The repair, not made here

Moving `WINDOW_END` to 2017-12-31 would catch the one 2017 offer. That keys the control to today's
answer, and one future guard change would empty it again. It also doubles the test's ~4-minute run.
The property is "the flat arm offers nothing by any route where the current arm would". So the
reachability half should come from a run in which current is known to offer. That means a fixture
policy differing from `CURRENT_POLICY` only in fields that admit offers through the guard (its
floor), with the flat arm given the same guard fields. B11's owner should pick the shape.
