**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B7_customer_state_layer_moves_and_shocks` · **Claim:** `b7-slice-5-the-occupier-window-is-not-also-written-off-in-4c`

# B7 slice 5: the change-of-tenancy window is not also written off in phase 4c

## Premise, re-measured at draw

The landing check named `b9d1ec2f1` as having moved `simulation/run_phase2b.py` since this item was
handed on. That commit is the first-term lookback guard. It does not touch the occupier window.
On origin, `arrears_engine._resolve_bills` still resolved every issued bill of an incoming leg as an
ordinary payer's, including bills whose rows already carried `occupier_debt_gbp` (slice 4,
`dfa787a37`). So the premise was live. The duplicate-work note named this item's own id, and no
rival claim under another name was found.

## Pre-registration (written before the first measurement)

Done means: a bill carries the share of its charges that the world has already booked as occupier
debt, and the arrears engine collects and writes off only the rest.

- P1. Moves off: no bill carries `occupier_share`, and `_resolve_bills` returns the same rows as
  before. This holds by construction, because the scaling runs only when the share is positive.
- P2. 2016 run with moves forced on: for each incoming leg, bill months wholly inside the window
  have share 1.0. The month the window ends has 0 < share < 1. Later months carry no share. For C1
  (window 2016-04-21 to 07-21) that is April to June, then July, then August onward.
- P3. On that same run, ordinary bad debt moves by **GBP 0.00**. In a run that ends in 2016, a write-off
  needs the account to close (it is a leaver) or a six-year statute bar. The incoming legs are
  admitted in 2016 and none leaves inside the year. Stayer provision (leg 4b) is off. So the 2016
  run cannot show the double count at all. The control has to be a unit test on a leaver book.
- P4. Unit book of high-stress leavers: a bill marked wholly the occupier's is absent from the
  resolved rows. A half-marked bill is asked for half its total. Unmarked bills draw the same
  outcomes. The emergent total falls.

## What was built

- **`company/billing/monthly_bill_assembly.py`**: a bill whose month holds rows with
  `occupier_debt_gbp` carries `occupier_debt_gbp` (the sum) and `occupier_share` (that sum over the
  month's settled revenue, capped at 1). It is a share and not a flag because the month the occupant
  is named holds rows on both sides of the window. A real supplier knows which of its charges it
  billed to "the occupier", so the label stays on the right side of the wall. Two limits are noted
  and not fixed here. The naming day is the register's expectation, not an observed event. On a split
  bill the share is applied to the whole billed total, so a catch-up folded onto it is split too.
- **`simulation/arrears_engine._resolve_bills`**: a bill with share 1 is skipped. A split bill is
  asked for `total x (1 - share)`. With no share the amount is untouched, not even re-rounded, so P1
  holds byte for byte. Both callers (`balance_settlement`, which feeds the billing ledger and the
  debt recovery, and `emergent_bad_debt_lines`, the P&L) go through this one function, so the ledger
  and the P&L still agree by construction. The DD rails (`supplier_dd_stops`) still see every issued
  bill. Whether an unnamed occupier's bill should reach the rails at all is not settled here. It
  moves no money, because the stop only relabels the paying method.

## Result against the pre-registration

- **P1 holds by construction.** It is guarded by the positive-share condition.
- **P2 held.** The new run-test leg found whole-window, split and after-window bills on the incoming
  legs. Whole bills had share 1.0, split bills were strictly between 0 and 1, and later bills
  carried none. The 2016 run marked 13 bills.
- **P3 held.** Emergent bad debt was GBP 84.30 with the mark and GBP 84.30 with it stripped from the
  same bills, measured in one process. No incoming leg is among the leavers. So the double count was
  real in mechanism but latent in a one-year run. It bites once an incoming leg leaves, or its
  window bills reach a statute bar.
- **P4 held.** See the controls below.

## Controls and mutations

- `tests/simulation/test_the_occupier_window_is_not_written_off_twice.py`. Its partition control
  requires that the marked months WOULD be written off unmarked, and that unmarked months are also
  written off.
- `tests/simulation/test_a_home_move_ends_supply_in_the_run.py::test_a_bill_carries_the_share_of_its_charges_that_is_occupier_debt`.

| Mutation | Result |
|---|---|
| Engine ignores the share | red |
| A split bill is skipped like a whole one | **green at first**. The cause was a missing test, not an equivalence: the leg never required the split rows to exist. With that leg added it is red. |
| Stamp removed at assembly | red |
| Flag, not share (every marked bill gets 1.0) | red |

## Carried, not filled

Recovery of change-of-tenancy debt is still a GAP (slice 4). Nothing books against it.
