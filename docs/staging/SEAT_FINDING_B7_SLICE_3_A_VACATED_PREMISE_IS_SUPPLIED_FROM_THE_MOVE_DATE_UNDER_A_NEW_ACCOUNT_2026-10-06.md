**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B7_customer_state_layer_moves_and_shocks` · **Claim:** `b7-slice-3-the-incoming-occupant-so-moves-can-be-switched-on`

# B7 slice 3: a vacated premise is supplied from the move date under a new account

## What was built

With home moves on, the run no longer lets a premise stop at the move. At each move-out leg the run
admits the incoming occupant:

- **`sim/customer_state_layer.py`**: `incoming_occupant_record` builds the incoming account from
  the vacated leg.
  - The meter point, its annual quantity and the dwelling are copied, because they belong to the
    premise.
  - The account id is the slice-1 `incoming.occupancy_id`. The gas leg keeps the gas suffix, so
    `household_of` treats the two legs as one household.
  - The terms are `deemed_contract` on `ARRIVAL_DEFAULT_TARIFF_TYPE` (svt).
  - Supply starts on the move date.
- **Supply and occupancy are kept apart.** The supplier stays registered and the meter keeps
  recording through any void. In a void the owner is the deemed customer, so the premise is never
  unsupplied. The occupancy start stays `None`, and its reason is kept in the run's own
  `home_move_ins` register, not on the supplier's book.
- **`saas/customers.py`**: there is a fifth registration book, `INCOMING_OCCUPANT_CUSTOMERS`, with
  its accessor in `company/interfaces/supply_book.py`. It is kept apart from `ACQUIRED_CUSTOMERS`
  because the meter point never left this supplier, so it is not a win and costs no CPA. The run
  clears it at the start.
- **`simulation/run_phase2b.py`**: `_admit_incoming_occupant` splices `build_svt_schedule`
  segments for the new account into the term heap. This is the same door a declined fix uses.
  - Per-meter-point inputs (weather, cloud cover, fabric trace, property, EAC, and the fabric
    eligibility verdict) are aliased from the premise.
  - The account's own state starts empty.
  - The incoming household moves on the same hazard, so a premise can turn over again.

## Evidence (2016 run, moves forced on)

- C1 moved on 2016-04-21. `OCC-6387bf64272a` (electricity) and `OCC-6387bf64272ag` (gas) are
  supplied from 2016-04-21, on svt, in three cap-period segments to year end.
- SYN-2016-019 (electricity, 2016-11-29) and SYN-2016-024 (gas, 2016-10-30) are each followed the
  same day.

New controls:

- `tests/simulation/test_a_home_move_ends_supply_in_the_run.py`: three tests. One checks that the
  vacated premise is supplied the day after the mover's last day, with a partition control that at
  least one incoming leg settled. One checks that the incoming occupant is its own household on
  svt. One checks that a dual-fuel premise's two legs go to one incoming household.
- `tests/sim/test_customer_state_layer.py`: one test of the record.

Five mutations, each red:

| Mutation | Tests red |
|---|---|
| Admission removed | 3 |
| Supply a day late | 2 |
| Gas leg loses its suffix | 2 |
| Incoming id derived from the mover's | 2 |
| Mover's tariff type kept | 2 |

With moves off, which is the production setting, the run is unchanged by construction. The book is
empty, every `+ _incoming_occupant_book` adds nothing, and `home_move_ins` is only emitted when
moves are on.

## What this slice does NOT do (carried, not filled)

1. **The incoming occupant pays for the whole unnamed window.** Energy from the move date is now
   settled and billed to the new account at the default tariff. W2_36's change-of-tenancy gap
   (`unnamed_kwh_after_move`) is energy that, in reality, is often never collected. So with moves
   on, collection is overstated by roughly that energy until the debt side reads the gap.
2. **The incoming household's tenure is drawn from its own id.** It is not taken from the
   dwelling. A rented flat usually stays rented, and no source on file gives the conditional.
3. **The supplier's EAC estimate for the new account starts from nothing.** In the industry the
   meter point's history survives a change of tenancy. Here, `_company_eac_estimate` falls back to
   the declared EAC for the new account.
4. **Reporting paths that iterate the four older books do not yet see the fifth.**
   `saas/reporting/annual_report.py` (lines 392 and 4873) and
   `simulation/run_phase4c_on_phase2b.py`. They matter only once moves are on.

None of these blocks the activation proposal. Item 1 is the one to weigh. It errs in the
supplier's favour, by about `q1_unnamed_months_per_cot` months of each premise's annual quantity
per move.

## What it unblocks

With the activation file switched on, B11's `move_outs_from_run_output` would get a non-empty
`home_move_outs`. A move would also stop reading as a lost premise. The activation is the
director's (curriculum), so it is proposed on his list and not flipped here.
