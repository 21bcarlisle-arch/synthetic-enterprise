**Severity:** RECORD · **Lane:** stage 1 — the people layer · **Atom:** `W2_19_who_lives_where_money_and_composition`

# W2_19 layer one reaches no home, and at real inputs wiring it moves the mean headcount by 0.09

**2026-09-25, on the director's instruction that W2_19's numbers be printed at real inputs before it
ships.** Measured at origin/main `cd4cc7f2b` over the live book (`live_dwellings()`, `CUSTOMERS`).

## What is live today: 0 of 231

The ruling's layer one is *"the household you would EXPECT given the postcode"*.
`dwelling_records.people_count_for_area` implements it (TS017 by 2021 output area, falling back to
the national draw), and `household_physical_layer.people_count_for` delegates to it. **But no drawn
dwelling carries an `output_area`** — the dwelling dict has `property_type`, `epc_rating` and
`bedrooms`, nothing else — so `people_count_source` returns `national` for **231 of 231** homes. The
docstring says so honestly (*"every home takes that fallback"*). So the mechanism is built and gets
no input.

## What wiring it would do, printed before building it

Every home already has a sited coordinate (244/244; `household_siting` draws a 1 km cell PPS over
the region's households). Resolving that cell to an output area is sourced end to end: the cell comes
from the HadUK-Grid aux coordinates, and the OA from ONSUD address counts per (OA, cell)
(`~/.cache/.../onsud/oa_cell_addresses.pkl`), drawn PPS by addresses within the cell. The headcount
then comes from that OA's TS017 distribution through the existing function, unchanged.

| | national (live) | by output area |
|---|---|---|
| homes resolved | — | **217 / 231** (the 14 others are all Scotland; TS017 is E&W) |
| mean headcount | 2.429 | **2.336** (ONS E&W 2.359) |
| sd | 1.315 | 1.230 |
| 1 / 2 / 3 / 4 / 5 / 6+ | 27.2 / 36.4 / 12.9 / 16.1 / 5.1 / 2.3 % | 28.1 / 36.9 / 16.1 / 12.9 / 4.1 / 1.8 % |
| homes whose headcount changes | — | **64 / 217**, mean \|change\| 0.30 |
| distinct OAs | — | 207 |

The two draws share one uniform per home (`people_count_{cid}`), so a home moves only where its area
distribution differs from the national one. That is why only 64 homes change.

**This is the size the module predicted.** Across 24,783,116 E&W households an output area explains
**9.0%** of household-size variance (0.159 of 1.762); 91% is within-area. So wiring layer one makes
the world's occupancy correctly conditioned. It moves the book very little, and it does not make
occupancy inferable from an address. A supplier still has to meter it.

Script: `/var/tmp/se-hhshape-run-20260925/out/w219_print.py` (a probe, not a module).

## Why it is minted rather than shipped this turn

1. **Cost per run.** The cell index needs the HadUK `tas` grid loaded to recover lat/lon → (E,N).
   That was the slow part of this probe, and it would run inside every sim run. The cheap version is
   to have `household_siting` carry the cell key (or the OA) at draw time, since it already knows the
   cell. That changes the committed frame's schema, and it is a separate piece of work.
2. **Reproducibility.** Both inputs (TS017 34 MB, ONSUD pairs 15 MB) live only in `~/.cache`. A
   tree without them silently takes the national path, so the same seed would give different
   headcounts on different machines. `people_count_for_area` already has that property, but it is
   dormant. Wiring it makes the property live. It needs either a committed derived frame or a
   refusal, not a quiet fallback.
3. **Effect.** −0.09 mean people, toward the published figure. Real, and small.

Minted as the follow-on; see `seat_continuation`.
