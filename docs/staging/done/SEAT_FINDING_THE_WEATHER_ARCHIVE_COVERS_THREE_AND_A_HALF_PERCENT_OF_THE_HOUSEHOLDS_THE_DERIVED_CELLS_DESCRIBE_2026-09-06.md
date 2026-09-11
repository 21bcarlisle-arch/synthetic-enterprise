**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14_weather_cells_for_household_heat_load

**Knowledge:** `docs/market_research/the_cell_decision_and_what_the_world_actually_uses.md` (W1_27's
decision — 21 cells per driver, held separately) and
`docs/market_research/how_many_weather_cells_britain_needs_and_why_the_answer_is_a_curve.md` (W1_21's
curve). This finding is the seam BETWEEN that decision and the world, measured rather than argued.

# The weather archive covers 3.5% of the households the derived cells describe

**Found 2026-09-06**, delivery seat, working the lane-0 direction *"wire the derived cells behind the
sim's weather seam, or W1_14's row names the successor that owns it."*

---

## The premise the direction carried, and why it was wrong

The direction read the gap as a **mapping** problem: five modules at level 3 in `tools/`, imported by
nothing in `simulation/`, `company/` or `saas/`, so write the import. It also offered an escape —
defer the wiring to W1_23 or W1_24 and say so in W1_14's row.

**Both halves are wrong, and the second is circular.** `W1_23` and `W1_24` each carry
`depends_on: [W1_14_...]` and a `block_reason` whose opening condition is *"opens when phase 1
lands"*. They cannot own the wiring that makes phase 1 land; they wait on it. There was no successor
to name.

And the wiring is not the blocker either. I wrote it, and it works, and it changes nothing — because
of what it measured on the way.

## What the seam measured

`simulation/weather_cell_siting.py` places a premise in the derived cells and asks whether an archive
site shares them. Cut exactly as `weather_cell_derivation.per_driver_curve` cuts them (one weighted
k-means per standardised driver, `n_init=1`, `random_state=0`, k=21) over the 121,668
household-occupied 1 km land cells, the four sites the archive covers — `sim/weather_data/C1-C4.csv`,
London, Manchester, Glasgow, Cotswolds — occupy **4 of the 21 cells on every driver**:

| driver | cells occupied | GB households in a covered cell |
|---|---:|---:|
| winter temperature | 4 / 21 | **20.5%** |
| annual wind | 4 / 21 | 30.7% |
| annual sunshine | 4 / 21 | 27.9% |
| **all three at once** | — | **3.5%** |

The joint row is the one that binds. The archive CSV carries temperature, cloud and wind in one row,
so a substitution takes all three or none — you cannot borrow Manchester's temperature without also
borrowing its wind.

**Neither uncovered location in the supply book clears it.** Birmingham (`C_IC1`, `C_IC2`) shares
Manchester's wind cell (19) and neither its temperature cell (15 vs 16) nor its sunshine cell (7 vs
17). Teesside (`C_IC3`, `C_IC3g`) shares nothing with anything. Both stay refused, exactly as they
were before — but the refusal now names the driver that disagreed instead of reading like a
coordinate typo.

## So the blocker is archive breadth, and it is now written down

**Seventeen more real weather pulls**, not a cleverer lookup. Four points against a decision of
twenty-one cells is a gap no mapping written in this repository can close, and that is now W1_14's
`block_reason` rather than a thing each session rediscovers.

W1_14 moves **0 → 1** on that evidence and not further. L1 is "exists, been built in any form" and
the seam exists; L2 is "mechanically real", and the world's household heat load is still not driven
by the cells. Recording L2 here would have published a claim the 3.5% refutes.

## Two smaller things found on the way

1. **W1_14's `file_scope` named `tools/generate_weather_cells_data.py`, which has never existed in
   any commit.** A level-0 row's `file_scope` is checked by nothing, so it named a program no build
   ever wrote — and it was the path a fresh session would have gone looking for. Replaced with the
   three paths the seam lands in.

2. **`the_cell_decision_and_what_the_world_actually_uses.md` is stale on wind.** It states, in bold,
   that wind is *"absent at the data-contract level"* and that `DailyWeather` has no wind field.
   `simulation/fabric_physics.DailyWeather` now carries `wind_speed_mean_ms` as a required field with
   no default. Another lane closed it under W1_26 after that page was written. **Not corrected here**
   — it is W1_26's to correct beside its own claim, and this note is the pointer.

## The control that had to exist before any of the above meant anything

Every refusal above passes against a mechanism that refuses *everything*, which is the trap this
project has entered through three separate doors in one afternoon. So the accept branch is proved
reachable from the committed artefact, on a real GB coordinate: a 1 km cell on the **north Cornish
coast, 304 km from London**, which the derivation puts in all three of London's cells. It also fixes
what the branch means — a witness next door could not tell climate matching from a proximity test.

Four mutations, four kills, against a baseline run green through the identical command: the accept
branch forced closed; all-three relaxed to any-driver; `CELLS_PER_DRIVER` 21 → 13; and the coverage
masks unioned instead of intersected.

## Limits

- **The cells are the phase-1 heat-load partition** — winter temperature, annual wind, annual
  sunshine, on the 1991–2020 normals. A cell says two places have the same 30-year climate, not the
  same weather on a given day. W1_22 is what carries the day-to-day question.
- **3.5% is a household share of GB, not of this company's book.** The book is 18 supply points at 6
  locations; the figure is what the archive would cover if the book were drawn from GB households,
  which is what the population draw is for.
- **The siting artefact holds only the coordinates it was asked about.** A coordinate absent from it
  is refused, never placed by nearest-anything — `derive()` is what extends it.
