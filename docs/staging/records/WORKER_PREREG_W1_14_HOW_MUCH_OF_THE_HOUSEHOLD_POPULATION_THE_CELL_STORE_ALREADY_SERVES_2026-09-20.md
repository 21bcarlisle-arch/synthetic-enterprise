# PRE-REGISTRATION — W1_14: how much of the household population does the CELL store already serve?

**Severity:** RECORDED
**Lane:** W1_market_weather
**Written 2026-09-20 BEFORE the measurement was run. Kept beside the answer, not revised away.**

## Why this question, and why it is not the question the atom asks

W1_14's `block_reason` (written 2026-09-07) says the whole remaining gap is **a data pull**: four
real Open-Meteo archive sites (`sim/weather_data/C1-C4.csv`) against a decision of 21 cells per
driver, covering **2.0% of GB households on all three drivers at once**, and 203 of 175,188
occupied land cells reaching a site. Its stated sequence is "re-land `_has_archive` first, then
pull".

That sequence is **wrong in direction**, and the tree says so at HEAD:

- `simulation/fabric_demand_path.py:133` records that the remedy sentence read
  *"sim/weather_data/{site}.csv does not exist -- pull that coordinate"* **until 2026-09-17**, when
  it was replaced because it "was an instruction to do the thing the director refused in writing:
  one download per property".
- `sim/weather_world.py` (landed 2026-09-16) carries the director's refusal verbatim: *"The world
  exists, and a property reads its conditions from it... Two households in the same cell must
  experience identical weather."*
- The replacement remedy is `ADD_THE_CELL_REMEDY` — extend the **per-cell store**, never a
  per-property pull.

So the atom's named next action is the refused design. The question that actually decides W1_14's
level is therefore not "how many properties have we pulled" but **how much of the household
population the per-cell store can already serve** — because that store, not the four CSVs, is
where this world's weather now lives.

## The measurement

`sim/weather_world/cells.json` holds **221 cells**; `WeatherWorld.cell_id_for` snaps a coordinate
to the nearest held cell and **refuses beyond `MAX_SNAP_KM = 5.0`**. Two populations:

1. **The supply book** — every premise in `registered_supply_points()`, by coordinate.
2. **The drawn household population** — `draw_population(7, acquisitions_per_year_lambda=40.0,
   draw_region=True)`, the same sharp configuration `test_a_drawn_household_has_a_coordinate...`
   uses.

For each: what share resolves to a cell inside 5 km, and what is the snap-distance distribution.

## THE PREDICTIONS, before running

1. **Supply book: 18/18 resolve.** The store was built over the cells the book occupies, so a
   premise it cannot serve would mean the build set and the book have diverged.
2. **Drawn households: between 50% and 90% resolve.** The store's 221 cells at a 5 km snap cover
   on the order of 17,000 km² of a ~230,000 km² GB land area — about 7% geographically. Households
   are not uniform over land, and the build set was chosen from occupied book cells, so the
   household-weighted share should be far above the geographic share. I predict it lands well
   above the four-site archive's 2.0% and well short of 100%.
3. **Directional claim under test:** the cell store already serves **more than an order of
   magnitude** more households than the four per-property archives, i.e. the atom's `block_reason`
   understates where W1_14 actually stands by describing a superseded design.

If prediction 2 comes back **above 90%**, my frame is wrong in the flattering direction: the store
would already be a near-complete answer and W1_14's remaining work is a wiring job, not a coverage
one. If it comes back **below 50%**, the coverage gap is real but is a *cell-store extension*, not
a per-property pull — the remedy changes, the blocker does not.

**Neither outcome licenses a level move on its own.** L2 is "mechanically real"; `weather_inputs`
still resolves per-property and does not read the store at all, so the world's household heat load
is still not driven by the cells whatever this number says.
