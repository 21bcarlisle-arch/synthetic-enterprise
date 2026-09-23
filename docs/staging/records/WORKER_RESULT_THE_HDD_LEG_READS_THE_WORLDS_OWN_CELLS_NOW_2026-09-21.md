**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# The HDD leg reads the world's own cells now, sixteen of eighteen premises move, and the two that still get a normal say so by name

Closes `WORKER_FINDING_THE_HDD_LEG_IS_A_THIRD_RESOLVER_AND_TEN_OF_EIGHTEEN_PREMISES_GET_A_CLIMATE_NORMAL_INSTEAD_OF_WEATHER_2026-09-21.md`
(BLOCKING, same lane and atom). W1_14 step 3 for this leg; the rest of the per-property design
(`_weather_source_customer_id`, `cell_matched_site`, `simulation/run_phase1b_weather_pull.py`) is
still standing and is what is left of step 3.

## What changed

`sim/weather_hdd._resolve_source_cid` — a string rule that stripped a trailing `g`, otherwise
passed the id through, and looked for `sim/weather_data/{id}.csv` — is **deleted**. In its place
`_premise_sky()` asks `simulation.weather_inputs.cell_weather_for_customer_id`, which is a roster
lookup onto `WeatherWorld.cell_id_for`: the same single rule the fabric leg has resolved by since
2026-09-17 and the demand-shape and forward-price legs since 2026-09-21. There is now **one**
implementation of "which sky did this household have", where this finding opened with three.

`get_hdd(date_str, customer_id)` keeps its signature and its bare float, because every caller does
arithmetic with it. The naming happens in a new `hdd_reading()` returning `HddReading(hdd, basis,
from_normal)`: a reading from the store says `basis="cell E529N0180"`, and a reading that had to
substitute the climate normal says so in the first words of its basis and carries the reason
verbatim — `"1991-2020 England & Wales monthly normal -- (52.4862,-1.8904) is 7.4 km from the
nearest cell the store holds (E414N0269), MAX_SNAP_KM is 5.0..."`.

## Measured, whole book, before and after

Annual HDD, 2018 (a cold year in the record) and 2022, for all 18 registered supply points.
`nan` is not a failure: it is the two premises the store genuinely holds no cell for, which stay
on the normal by design and now say so.

| id | 2018 was | 2018 now | Δ | 2022 was | 2022 now | Δ |
|---|---|---|---|---|---|---|
| C1 | 1841.1 | 1560.1 | −15.3% | 1667.2 | 1367.4 | −18.0% |
| C2 | 2056.6 | 1745.8 | −15.1% | 1864.1 | 1564.0 | −16.1% |
| C3 | 2471.9 | 2106.0 | −14.8% | 2195.8 | 1801.0 | −18.0% |
| C4 | 2213.0 | 2128.2 | −3.8% | 2018.8 | 1967.8 | −2.5% |
| C5 | 2086.1 | 1560.1 | −25.2% | 2086.1 | 1367.4 | −34.5% |
| C6 | 2086.1 | 1745.8 | −16.3% | 2086.1 | 1564.0 | −25.0% |
| C7 | 2086.1 | 1560.1 | −25.2% | 2086.1 | 1367.4 | −34.5% |
| C8 | 2086.1 | 1745.8 | −16.3% | 2086.1 | 1564.0 | −25.0% |
| C9 | 2086.1 | 2106.0 | +1.0% | 2086.1 | 1801.0 | −13.7% |
| C_IC1 | 2086.1 | *normal, named* | — | 2086.1 | *normal, named* | — |
| C_IC2 | 2086.1 | *normal, named* | — | 2086.1 | *normal, named* | — |
| C_IC3 | 2086.1 | 1934.9 | −7.2% | 2086.1 | 1689.6 | −19.0% |
| C_IC4 | 2086.1 | 1745.8 | −16.3% | 2086.1 | 1564.0 | −25.0% |
| C_IC3g | 2086.1 | 1934.9 | −7.2% | 2086.1 | 1689.6 | −19.0% |
| C1g | 1841.1 | 1560.1 | −15.3% | 1667.2 | 1367.4 | −18.0% |
| C2g | 2056.6 | 1745.8 | −15.1% | 1864.1 | 1564.0 | −16.1% |
| C3g | 2471.9 | 2106.0 | −14.8% | 2195.8 | 1801.0 | −18.0% |
| C4g | 2213.0 | 2128.2 | −3.8% | 2018.8 | 1967.8 | −2.5% |

**TWO DIFFERENT CAUSES ARE IN THAT COLUMN AND MUST NOT BE AVERAGED.** Ten premises (C5–C9, the
four I&C, C_IC3g) moved because they were on a flat climate normal and now see weather at all.
Eight (C1–C4 and their gas twins) moved because their source changed from an ERA5 ~9 km archive to
HadUK-Grid 1 km, which reads ~1.2 C warmer at an urban cell — the urban heat island the coarser
reanalysis cannot resolve, already measured and recorded in `simulation/weather_inputs.py` when
the shape and price legs made the same move. A single mean over the eighteen would report neither.

The third row of the original finding is closed arithmetically: **C1 and C7 are one coordinate and
now read the identical number every day of the record**, where they sat 12–20% apart.

An R13 fidelity decision, taken blind to what it does to company results. It moves settled gas
volumes down across the book, so it moves revenue and cost; that is the world becoming able to
press back, not a result.

## Why C_IC1 and C_IC2 are still on the normal, and why that is fail-closed now

Birmingham (52.4862, −1.8904) is 7.4 km from the nearest cell the store holds against a
`MAX_SNAP_KM` of 5.0. The remedy is `fabric_demand_path.ADD_THE_CELL_REMEDY` — add the cell — and
never a per-property pull, which is the design the director refused in writing on 2026-09-16. What
changed is that the substitution can no longer pass as weather: `HddReading.from_normal` is the
question a caller asks, and `basis` is the sentence a printed record carries. **`get_hdd`'s bare
float still cannot say it**, which is stated in its own docstring rather than left for a reader to
discover; a caller that needs provenance must ask `hdd_reading`.

## The control, and the mutations it survived

`tests/sim/test_the_hdd_leg_reads_the_premises_own_cell.py::test_the_resolver_discriminates_a_premise_with_a_cell_from_one_without`
is **one test over the whole partition** — C7 (held) and C_IC1 (refused) in a single function —
because a resolver that returns the normal for everything satisfies every assertion about what a
normal looks like, and one that returns a cell for everything satisfies every assertion about what
weather looks like. Proven in-process, with no mutation written to the shared tree:

| mutation | partition control |
|---|---|
| `_premise_sky` returns no cell for every id | **RED** on the held leg, by the assertion written for it |
| `_premise_sky` returns one cell for every id | **RED** on the refused leg, by the assertion written for it |

`test_two_premises_at_one_coordinate_read_one_sky` stays green under both, and that is an
**equivalence, not a missing test**: a one-way resolver hands both ids the same sky by
construction. Recorded in the test's own docstring so the green is not read as coverage it is not.

## One thing that was a latent second defect, fixed here rather than filed

`simulation.weather_inputs.shared_world()` had no caller: the runner passes its loaded world to
every leg explicitly, so the process singleton never engaged. The HDD leg cannot be passed a
world — `get_hdd` sits five frames under `run_gas_term` with no world in any signature on the way
down — so it would have loaded a **second** copy of the store (8 MB gzip, ~450 MB resident) which
could then drift from the first. `adopt_shared_world()` is the explicit door, called once in
`run_phase2b` immediately after `WeatherWorldSource.load()`. Passing a world to `shared_world()`
still does NOT adopt it, deliberately: the W1_14 controls hand it two-cell fakes, and a fixture
that became the process singleton would settle somebody else's book.

## What this does not do

- It does not retire the per-property archives. `load_weather_means` and the four CSVs are still
  read by the W1_14 siting controls; `_weather_source_customer_id` and `cell_matched_site` are
  still standing.
- It does not re-measure anything downstream of gas volume. Revenue, margin and hedge figures move
  and have not been re-cut here; attributing those is a separate measurement and mixing it into
  this commit would make both unattributable.
