**Severity:** INFO · **Lane:** W1_market_weather · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# RESULT: W1_14 moves L1 -> L2, because every premise the run settles now reads its own cell

**Why L2 was withheld.** The row said L2 must wait until the world's heat load is DRIVEN by the
cells, not merely reachable through them. On 2026-09-07 about 99% of drawn households got no weather
from the cells.

**What was measured (2026-09-30, HEAD `b36addf94`, published book seed 20260724).** The book is
`ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS`, 250 premises. Each leg was read through
the code's own census, not a re-implementation of it:

| Leg | Instrument | Refused / on the normal |
|---|---|---|
| shape + price, temperature | `weather_refusals_for_book(book, TEMPERATURE_FIELD)` | 0 / 250 |
| shape, cloud cover | `weather_refusals_for_book(book, CLOUD_COVER_FIELD)` | 0 / 250 |
| gas HDD | `hdd_reading(d, id).from_normal` after `adopt_book(book)` | 0 / 95 |
| physics | `WeatherWorld.cell_id_for` over every located premise | 0 / 250 |

The ACQUIRED book is empty at this seed. SUCCESSOR resolves 6/6.

A first run of the census passed `temperature_2m_mean` / `cloud_cover_mean` and got 250/250 refused.
Those are field names the store does not hold, so the census refused every premise, as it should.
The module's own `*_FIELD` constants give the rows above.

**What L2 does NOT claim. This is the L3 gap.** The store is built by `tools.build_weather_world.book_cells`
from the book drawn at ONE seed. The cell-coverage probe was re-run at the book seeds the A/B harness
knows how to draw (`BOOK_MEMBER_PREAMBLE`: rebind `_DEFAULT_BASE_SEED`, then import):

| book seed | CUSTOMERS resolving a cell |
|---|---|
| 20260724 (published) | 244 / 244 |
| 7 | 106 / 243 |
| 42 | 118 / 250 |
| 11, 88888 | do not import. `run_phase2b.py:305` raises `KeyError: 'aq_kwh'`, because a drawn gas record lacks it |

None of this is reachable today. `run_value_cycle_ab.book_seed_authorisation_refusal` refuses every
non-default book seed until the EP17 ruling file exists. The renewal-noise seeds (7/11/42/88888 in
`--level-arm`) re-roll behaviour on the SAME book. They do not re-draw it.

If EP17 is ever authorised, two things become due before its first run:
1. Rebuild the store over the authorised seeds' books with `build_weather_world --build`.
2. Fix the `aq_kwh` crash.

Without the rebuild, over half of those households would settle on the unadjusted base shape. That
would be named per premise in `weather_refusal_by_customer`, so it is visible but not correct.

**Probe:** `/tmp/w114/probe.py` (not committed). It is a 20-line coordinate loop over
`WeatherWorld.cell_id_for`.
