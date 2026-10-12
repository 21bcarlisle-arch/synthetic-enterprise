**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# Pre-registration: how much of the world's missing year-on-year variation is the weather store not reaching the redrawn book

Written 2026-10-11T06:25Z, before any store extension or re-run. Claim
`world-household-consumption-is-too-steady-year-on-year`, handed on by
`docs/staging/SEAT_FINDING_THE_COMPANY_HOLDS_SIX_CONSUMPTION_FORECASTS_AND_THE_WORLD_IS_TOO_STEADY_TO_RANK_THEM_2026-10-11.md` §3.
This is a fidelity change, decided blind to company results. This file is not edited after the run.

## Which parts of the published spread the world should produce

The published reference is NEED 2026, consecutive-year electricity pairs: median |change| 14.7%,
2021→2022 median ratio 0.923 (`docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md`).
That spread bundles four things. The decision, per component:

| component | should the world produce it? | where it would come from | sized by published evidence? |
|---|---|---|---|
| **weather** (heating, lighting, solar) | **yes** | the per-cell store through `fabric_physics` / `fabric_seasonal_split` | the weather is; the response is the fabric model's |
| **household change** (occupancy, appliances, behaviour, life events) | **yes** | the household register already moves EV, solar, heat pump; nothing moves occupancy or behaviour | **no** — NEED cannot separate it from the two artefacts below. GAP, filed, not invented |
| **the 2022 price response** | **yes** | nothing in the world today | **partly** — 0.923 is the NEED ratio, but 2022 was also a warm year, so it is weather + price + artefacts together. GAP until split |
| change of occupier | **no** — a new occupier is a new household in the world (B7 move-out/void), not a change in this one | — | — |
| EAC↔AA transitions, 100 kWh rounding | **no** — these are how the INDUSTRY FIGURE is wrong, not how the household changed. They belong to the registry read-error item, on the company's observable, never to true consumption | — | — |

So 14.7% is an upper bound for what true household consumption should do, and the target is the
first three rows only. No number for rows 2 and 3 is written into the world by this claim.

## What I found before predicting anything (read, not measured against a target)

The finding called `legacy_pc1_rescaled` and `population_70_30_split` "pinned providers", as if
they were a modelling choice. In the graded run (`7379375f6`) they are not:

- **278 of the 280** `legacy_pc1_rescaled` electricity premises are legacy because
  `fabric_eligibility` refused them `no weather archive for this customer's location` (the other
  two are non-domestic).
- At HEAD, `python3 -m tools.build_weather_world --list`: **600 cells the book occupies; 496 the
  store has never held.** The store was completed for the earlier book (`f0ba399a4`, "every book
  cell") and the book was redrawn after it.
- A gas premise with no cell reads the 1991–2020 monthly HDD normal (`sim.weather_hdd.hdd_reading`),
  which is the same number every year: 131 of 290 gas premises at HEAD.
- Nothing refused this. `coverage_refusals` raises only on an archive that stops short of the
  window, not on a premise with no cell, so half the book left physics in silence.

The weather leg is therefore not "give the legacy provider variation"; it is **put the redrawn
book's cells in the store**, which moves those premises onto the providers that already vary.

## The one-variable step

Change: extend `sim/weather_world/` to the book's cells with the existing builder
(`tools/build_weather_world --build`: HadUK temperature from the local grids, ERA5 wind/cloud/precip
from Open-Meteo). No code change to any demand provider. Then re-run the 2016–2025 annual report
and the census below plus the grading appendix of the forecasts finding.

## Predictions

| # | prediction |
|---|---|
| P1 | `legacy_pc1_rescaled` falls from 280 to **≤ 10** (only no-register / non-domestic remain). |
| P2 | `population_70_30_split` falls from 139 to **≤ 15**. |
| P3 | book-wide median \|year-on-year change\| of true consumption: electricity rises from ~0.3% to **0.4–0.8%**, gas from ~0.4% to **2–4%**. Both stay **≥ 15× below** NEED's 14.7%. |
| P4 | 2021→2022 median ratio: electricity stays **≥ 0.98** (no price response exists); gas is **0.88–0.93** (the warm year alone). |
| P5 | F4 (trailing 12 settled months) stays the best level forecast on both fuels, with median \|annual error\| **< 4%**: the weather leg cannot unseat "last year" because household change is still absent. |
| P6 | the run's fabric-eligibility refusals for `no weather archive` fall from 282 to **0**. |

If P1/P2 hold and P3/P5 hold, the weather leg is closed and the year-on-year gap is
**household change and the price response**, both GAPs needing published sizing before any world
term is written.

## What would refute the frame

- P1 holds but P3 electricity stays ≤ 0.3%: then fabric electricity is itself too steady, and the
  0.5% the finding measured on fabric premises was a selection, not the provider's behaviour.
- P6 does not reach 0 after the store reports complete: then a second hole sits between the store
  and eligibility.
