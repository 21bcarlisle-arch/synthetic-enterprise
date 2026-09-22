**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# The HDD leg is a THIRD resolver, and ten of eighteen premises get a 1991-2020 climate normal where the world has their weather

BLOCKING is lane-scoped; every other lane proceeds untouched. It blocks here because W1_14's step 3
is "retire the per-property design", and this is the instance of it that is still **changing settled
numbers** — a lane that closes W1_14 on the strength of the seam migration alone will close it over
a leg that silently substitutes climatology for weather on 10 of 18 premises.

## The three resolvers, and what each one answers

"Which sky did this household have" had two implementations until 2026-09-21 and now has two again,
because the one this tick repaired was the middle one:

| leg | resolver | source |
|---|---|---|
| fabric physics (4c-1) | `WeatherWorldSource.site_for` → `WeatherWorld.cell_id_for` | the per-cell store |
| demand shape + forward price (4c-2/4c-3) | **was** exact `location` match → a customer_id with a CSV; **now** `cell_id_for` | the per-cell store, since 2026-09-21 |
| gas/HDD (`sim/weather_hdd.get_hdd`) | `_resolve_source_cid`: **strip a trailing `g` from the customer_id, else pass through** | `sim/weather_data/{id}.csv`, else a monthly NORMAL |

`_resolve_source_cid` is a STRING RULE with no notion of location at all. It resolves `C1g -> C1`
and everything else to itself, so any premise whose own id is not one of the four archive filenames
finds no CSV — and `get_hdd` then returns `REFERENCE_MONTHLY_HDD[month] / 30.0`, the 1991-2020
England & Wales monthly normal, flat across every day of that month, for every year.

## Measured on the live book, 2026-09-21

**8 of 18 premises read a real daily temperature. 10 get the climate normal:** C5, C6, C7, C8, C9,
C_IC1, C_IC2, C_IC3, C_IC4, C_IC3g. Five of those ten (C5, C6, C7, C8, C9) sit in a cell the store
holds every day of, and three of them share a cell with an archived premise that does read weather.

The substitution is not small, and it is not centred:

| | 2018 | 2022 |
|---|---|---|
| C7 annual HDD from its own CELL | 1560.1 | 1367.4 |
| C7 annual HDD from `get_hdd` (the normal) | 2086.1 | 2086.1 |
| error | **+33.7%** | **+52.6%** |
| C1 — SAME CELL, reads its CSV | 1841.1 | 1667.2 |

Three things in that table are each independently wrong:

1. **The normal is the same number every year** (2086.1 in both columns), so a premise on the normal
   cannot respond to a cold winter at all. 2022 is a fact, not a scenario, and this leg cannot see it.
2. **It is biased high by a third to a half**, because the 1991-2020 normal is colder than the
   2016-2025 record at a 1 km urban cell — the same urban-heat-island signal that makes HadUK read
   +1.19 C warmer than ERA5 at London.
3. **C1 and C7 are in one cell and are 12-20% apart.** That is precisely the attribution failure the
   per-cell architecture exists to end, in a third place, arithmetically: the difference between
   these two households' gas demand is currently attributable to which resolver their id happened to
   satisfy.

## Why nothing noticed

The fallback is a legal, documented branch: `get_hdd`'s docstring explains the non-finite guard in
detail and says nothing about the missing-file path, because a missing file was once only possible
for a customer with no weather at all. Every test of `get_hdd` drives it with `C1`-`C4` or with
temperatures passed in, so the fallback is never the subject. And the value it returns is a
plausible HDD — nothing downstream can distinguish "a mild month" from "no weather for this premise".

## The remedy, and what it is not

It is **not** a fifth archive pull. `get_hdd(date_str, customer_id)` takes an ID and no coordinate,
which is why it resolves by string: the signature cannot ask the store. So the remedy is a seam
change — the HDD leg must take the premise's daily temperature series (which
`weather_inputs.weather_means_for_customer` now returns from the store) or the cell, rather than
re-deriving a source from an id — and it will move settled gas numbers for 10 premises, which is a
change to make deliberately and measure, not to fold into another commit.

Not done in this tick deliberately: the seam migration this finding came out of is landed and
measured on its own, and `get_hdd` has 11 test files against it. Mixing the two would make both
unattributable, which is the rule this project has paid for most often.
