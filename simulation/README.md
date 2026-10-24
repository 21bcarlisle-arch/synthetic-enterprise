# simulation/

The world's households and the run loop: demand, life events, payments,
settlement, and the runners (`run_phase*`) that move the world and the company
through simulated time. `sim/` is the world's market; this package is its
people. Both are the WORLD side of the epistemic wall.

## What this package may import from the supplier (corrected 2026-10-24)

*This section used to say code here "may import from both `sim/` and `saas/`".
That was the July layout and it is wrong: `saas/` is the supplier, and since
2026-08-05 every `simulation -> company|saas` import that does not land on
`company/interfaces/` (the seam) is a wall crossing held by
`tests/architecture/test_epistemic_wall_ratchet.py`, ruled per edge in
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`.*

- The runners may call the supplier **through the seam only**: they hand it what
  a real supplier could observe as of the simulated moment, and take back its
  decisions.
- World behaviour (who leaves, who pays, what a household does) is built from
  world state alone, with no reference to any supplier model (W7 principle 1).
  The edges that still break this are `owed` rows in the register, each with an
  owning atom and a due date.

Reaching backwards in time is fine; handing the supplier a sneak preview of the
future defeats the Point-in-Time Blindfold.

In short: `sim/` ↔ `saas/` is a one-way mirror; this is the room with the
clock on the wall, advancing time and reading off both sides at the current
moment only.
