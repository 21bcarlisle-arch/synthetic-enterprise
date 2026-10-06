**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B7_customer_state_layer_moves_and_shocks` · **Claim:** `b7-slice-4-the-change-of-tenancy-window-is-not-all-collected`

# B7 slice 4: the change-of-tenancy window is booked as occupier debt, not as paid

## Premise, re-measured at draw

The draw's duplicate-work note named this item's own id, held by this invocation (pid 406293). No
rival seat or `surgical_land` was running. HEAD equalled origin/main (`c7d104866`). Nothing on
origin routed the incoming leg's unnamed window anywhere: `unnamed_kwh_after_move` was only read
into the `home_move_outs` row. So the premise was live.

## Pre-registration (written before the first measurement)

On the 2016 run with moves forced on (three moves: C1 on 2016-04-21, SYN-2016-019 elec on
2016-11-29 and SYN-2016-024 gas on 2016-10-30):

- P1. Every incoming leg's settled rows dated before `move_date + 91 days` carry occupier debt
  equal to their revenue, and no ordinary bad-debt incidence. Rows on or after that day carry none.
- P2. The run's total occupier debt is positive and below GBP 600. Three windows of about three
  months of an SVT bill, with the two autumn windows cut at the report end.
- P3. Moves off: the run is byte-for-byte unchanged in money (no incoming legs, so nothing to book).

## What was built

- **`sim/customer_state_layer.py`**: `unnamed_until(move_date, setting)` is the move date plus
  `q1_unnamed_months_per_cot` months (91 days at the default). It is the same expectation
  `unnamed_kwh_after_move` prices and is not drawn per move. The toggle was derived as CoT debt
  accrued per move (Energy UK's £740m over about 2.0m moves, £474 per move), so it measures energy that
  went unpaid, not energy that was billed late.
- **`simulation/run_phase2b.py`**: `_admit_incoming_occupant` records each incoming leg's
  `unnamed_until`, and the `home_move_ins` row carries it. Each settled row of that leg dated before
  that day books `occupier_debt_gbp` equal to its revenue, deducted from net margin, with no
  ordinary bad-debt incidence on top. The run returns `total_occupier_debt`.
- **Why it is its own field and not `bad_debt_gbp`.** Phase 4c (`book_arrears_lines`) releases the
  `bad_debt_gbp` placeholder and re-books it from the arrears engine. That engine would collect this
  window as if a named household paid it, so a charge kept in `bad_debt_gbp` would be undone in 4c.

## Result against the pre-registration

2016 run, moves forced on. The four incoming legs are C1's two (2016-04-21, window to 2016-07-21),
SYN-2016-019's electricity leg (2016-11-29, window to 2017-02-28) and SYN-2016-024's gas leg
(2016-10-30, window to 2017-01-29).

- **P1 held.** 278 incoming-leg rows fall inside a window and 328 after. Every inside row carries
  occupier debt equal to its revenue and zero bad debt, and no row after a window carries any.
  A first draft rounded the debt per settlement period, and it then drifted about 2e-6 from the
  daily folded revenue. The debt is now stored unrounded.
- **P2 held.** Total occupier debt was **£292.34**: C1 electricity £82.18, C1 gas £88.74,
  SYN-019 £49.59 and SYN-024 £71.83. The two autumn windows are cut at the report end. On the same
  run, ordinary bad debt was £610.57.
- **P3 holds by construction.** With moves off no incoming leg is admitted, `_unnamed_until` stays
  empty, and no row is touched.

## Controls

- `tests/sim/test_customer_state_layer.py`: the window ends the register's months after the move,
  at each setting, and widens from low to high.
- `tests/simulation/test_a_home_move_ends_supply_in_the_run.py`: inside rows equal revenue with zero
  bad debt, after rows carry nothing, and no account other than an incoming one carries the field.
  A partition control requires rows on both sides of a window, and at least one inside row with
  revenue.

Four mutations, each red:

| Mutation | Result |
|---|---|
| Booking removed | red |
| Booked one day past the window | red |
| Booked on every account | red |
| Ordinary bad debt kept as well | red |

## Carried, not filled

1. **Recovery of the occupier debt is not established.** Nothing is recovered, so the bias now runs
   against the supplier, by whatever share of CoT debt is later collected. Ofgem's worst case is
   that it is all written off, so the bound is zero to the whole window.
2. **In 4c the window can also be charged at the ordinary rate.** Phase 4c still bills the
   incoming account's window and resolves it in `arrears_engine._resolve_bills` as an ordinary
   payer. So that energy can carry the ordinary write-off incidence on top of its occupier debt,
   a second-order double charge of a few per cent of the window. The fix is for bill assembly to
   mark the window's bills as the occupier's and for the engine to skip them. Not done here.
3. **The window is the expectation.** Every move is unnamed for exactly 91 days. The per-move
   spread, and the share of moves named on day one, are not modelled (the same gap
   `unnamed_kwh_after_move` carries).
4. **The director's activation item no longer names the old bias.** In
   `docs/direction/DIRECTION.yaml` (`home-moves-can-now-be-switched-on`), the proposal text was
   corrected to say the window is now booked as debt.
