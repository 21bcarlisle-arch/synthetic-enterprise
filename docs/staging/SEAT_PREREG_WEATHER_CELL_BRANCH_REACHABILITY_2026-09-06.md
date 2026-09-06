# PRE-REGISTRATION — is the derived weather cells' substitution branch reachable by any household?

**Date:** 2026-09-06
**Lane:** W1_market_weather
**Severity:** RECORDED — a pre-registration, filed BEFORE the measurement it names, so that the
predictions cannot be revised into agreement with the answer. Delivery claim
`the-weather-cells-reach-the-world-or-w1-14-says-why-not`.
**Status:** ANSWERED — see `SEAT_FINDING_W1_14_WAITED_ON_THE_WRONG_GAP_2026-09-06.md`. All four
predictions confirmed; P2 came back stronger than predicted (the curriculum draws ten real GB
regions and every one still carries no coordinate).

## Why this is being asked

`simulation/weather_cell_siting.cell_matched_site` is the sim-side seam W1_14 landed on 2026-09-06
(commit `8ff0fc2d5`). It is step 2 of `weather_inputs._weather_source_customer_id`: exact location
match first, derived-cell substitution second, refusal third.

W1_14's row names the L1→L2 blocker as **archive breadth** — "the supply book has 6 distinct
locations and 4 have archives, so Birmingham and Teesside are the whole gap … TWO pulls close it".
That framing was written from the supply book's LOCATIONS. It was never asked of the supply book's
**households**, and this atom's subject is *household* heat load.

Two facts, both already in the tree, put the framing in doubt:

1. Every location holding a **resi** premise (London, Manchester, Glasgow, Cotswolds) already has an
   archive CSV, so those premises answer at step 1 and never reach step 2. Birmingham and Teesside
   hold only `C_IC1`, `C_IC2`, `C_IC3`, `C_IC3g` — all **I&C**.
2. `simulation/population_draw.py:314` renders every drawn customer's location as
   `{"lat": None, "lon": None, "region": self.region}`. `cells_for_location` returns `None` when
   `lat` is `None`.

If both hold, the two pulls the row waits on buy weather for the I&C book and change nothing for
household heat load — and the binding constraint is a missing coordinate at the draw, not archive
breadth.

## Predictions, recorded before running anything

- **P1.** For every customer in `company.interfaces.supply_book.registered_supply_points()`,
  `cell_matched_site` is either never consulted (step 1 answered) or returns `None`. **Count of
  supply-book premises resolved BY the cell branch: 0.**
- **P2.** For a drawn population from `simulation.population_draw`, `cells_for_location` returns
  `None` for **100%** of drawn customers, because `lat is None` — a refusal with a *siting* reason
  ("has not been sited against the derived weather cells"), which reads as a derivation gap and is
  actually a placeholder coordinate.
- **P3.** Landing the two pulls named in W1_14's `block_reason` (Birmingham, Teesside) moves the
  count in P1 from 0 to 0 for **households**, because both are I&C-only locations. It moves I&C
  coverage, which is a different atom's subject.
- **P4.** Therefore step 2 of `_weather_source_customer_id` is, today, a branch **no premise in this
  world can take** — the exact R15 shape ("a branch that exists to be taken rarely" taken never),
  and its only reachability evidence is `REACHABILITY_WITNESS`, a synthetic Cornish coordinate that
  is explicitly "not a premise".

## What would refute each

- P1/P3 refuted if any resi premise sits at a location without an archive CSV, or if Birmingham or
  Teesside holds a resi premise.
- P2 refuted if any production path fills `lat`/`lon` on a drawn customer before weather resolution.
- P4 refuted if either of the above is refuted.

## What follows either way

If confirmed: W1_14's `block_reason` is measuring the wrong set and must be corrected in the row —
the honest statement is that the household gap is a **coordinate at the draw**, which is
`W2_18_the_housing_joint_the_sample_and_the_ceiling` / `W1_24` territory, and archive breadth is the
**I&C** gap. The two pulls stay worth doing; they stop being what this atom waits on.

If refuted: the row is right, the pulls are the work, and this file is the record that the seat
checked and was wrong.
