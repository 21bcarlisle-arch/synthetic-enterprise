**Severity:** RECORD · **Lane:** W2_customer_generator · **Atom:** none — Lane 0 delivery (`what-the-siting-frame-rebuild-moves-in-the-book`)

# Pre-registration: what the siting-frame rebuild (d9374ae9e) moves in the book

**Written 2026-09-27 18:45 BST, before any run.** Follows
`PREREG_REBUILD_THE_SITING_FRAME_ON_THE_ADDRESS_PLACEMENT_2026-09-27.md`, whose result says outright
that the book effect was not measured.

## Premise check

The item's cited commit is on origin/main, but that commit is the change this item measures, so
the premise is not spent. The duplicate claim the draw flagged is the draw's own write:
`.seat_work_in_hand.json` was written 18:36, it holds only this id, and its paths are `[]`.

## The one variable

`simulation.household_siting.FRAME_PATH` and `OUTPUT_AREA_FRAME_PATH` point at
`d9374ae9e^:sim/household_siting/*` (OLD) or at HEAD's copies (NEW). Both arms run the same code,
seed, window and weather store. They run in two processes because `run_phase2b` binds the roster
at import. Harness: `tools/siting_frame_counterfactual.py`. It reads the book with
`tools.fabric_settlement_gap.measure()`, the same book-level reader that tool publishes from, and
does not re-implement the demand path.

## Predictions

- **P0. The book's account set is identical in both arms.** The cell and area draws are on their
  own substreams, and I expect nothing that picks winners to read the coordinate. If ids differ,
  every number below is a composition change as well as a siting change, and I will report that
  rather than the totals.
- **P1. ≥ 90% of homes change their 1 km frame cell.** The cell draw is one uniform against a
  cumulative-household array, and the rebuild reordered and reweighted every region's rows.
- **P2. ≥ 90% of sited E&W homes change their output area.** This follows from P1.
- **P3. The weather-store resolution (`WeatherWorld.cell_id_for`: the 221 cells within 5 km, or a
  refusal) changes for ≥ 50% of homes.** The eligible (fabric-driven) share stays near the
  2026-09-20 figure of 37%, ± 10 points in each arm.
- **P4. Mean headcount per home moves by less than 0.2, sign unknown.** Two nearly independent
  redraws over ~155 homes, each with SE ≈ 0.09.
- **P5. Book kWh, meaning `fabric_annual_*_kwh` summed over eligible premises.** The TOTAL moves
  by whatever the eligible COUNT moves, so I will report the per-eligible-premise mean beside it.
  The per-premise means move by < 10% on each fuel, sign unknown. A larger move says the premises
  that swap in and out differ in fabric, not in weather.

Kill line: if P0 fails, the result is "the rebuild changed WHO is in the book". That is a finding
in itself, and no kWh move can be attributed to weather or headcount.

## Result (filed 19:05 BST after both arms ran; predictions above unedited)

Arms: `/tmp/sfc/old.json` (12m40s) and `/tmp/sfc/new.json` (9m55s). Both ran at HEAD `d9374ae9e` in
an isolated worktree, default seed, window 2016-01-01 → 2025-06-07. There are 244 accounts and 155
homes; a dual-fuel `PROS-x`/`PROS-xg` pair counts as one home.

| | Predicted | Measured | |
|---|---|---|---|
| P0 | same accounts | **identical, 244 = 244** | hit |
| P1 | ≥ 90% change 1 km cell | **75.5%** (117 of 155) | **MISS** |
| P2 | ≥ 90% change output area | **75.5%**, exactly the homes that changed cell | **MISS** (follows P1) |
| P3 | ≥ 50% change store resolution; eligible share 37% ± 10 | **41.3%** change; eligible **132 → 102** of 149 electricity premises (89% → 68%) | **MISS on both legs** |
| P4 | abs(Δ mean headcount) < 0.2 | **2.297 → 2.355 (+0.058)**; 26% of homes change headcount, mean abs move 0.33 | hit |
| P5 | per-eligible mean < 10% | elec **4,071 → 3,779 (−7.2%)**, gas **11,259 → 11,048 (−1.9%)** | hit, for the wrong reason |

**Book fabric kWh (sum of `fabric_annual_*_kwh` over the fabric-driven premises):** electricity
537,328 → 385,472 (**−28.3%**), gas 1,486,247 → 1,126,879 (**−24.2%**). **The 102 premises that are
fabric-driven in both arms move +0.31% (elec) and +0.51% (gas).** So the new cell's weather and
the new headcount together move a home's demand by about half a percent. **The whole −28% is 30
premises leaving the fabric-driven book.** No premise joined.

**Why they left.** In the new arm all 30 are refused with *"no cell ((lat,lon) is X km from the
nearest cell the store holds … The store covers the cells the book occupies"*. The per-cell
weather store (`sim/weather_world/daily.csv.gz`, 221 cells) was pulled on 2026-09-17
(`7d9eabe49`) for the cells the book occupied on the OLD frame. The rebuild moved 30 electricity
premises to cells 5.1–58.6 km from any stored cell, and they now settle on the legacy shape.

**The store was already stale before the rebuild.** On the OLD frame at today's HEAD, 12
electricity premises were already off-store, so the book grew or moved after 09-17 without a
re-pull. The new frame makes it 42: 41 with no cell within 5 km, and 1 in a cell holding
temperature only.

**Why P1 missed.** I reasoned that reordering the cumulative array moves every draw. A quarter of
homes kept their cell, because a region's rows keep much the same order and the rebuild's weights
moved only slightly for most cells. I did not measure that before predicting.

**Why P3 missed.** I anchored on the 2026-09-20 figure of 37% of the DRAWN POPULATION served. That
is a different population: the book's premises are the ones the store was pulled FOR, so the
old-frame book sat at 89%. The right prior was "nearly all, until the siting moves".

**What this means downstream.** Any result compared across `d9374ae9e` that reads the settled book
is not the siting change. It is a 30-premise population change on the fabric path: 28% of
fabric-driven electricity volume moved back onto the legacy shape. Finding:
`docs/staging/SEAT_FINDING_THE_SITING_REBUILD_MOVED_30_PREMISES_OFF_THE_WEATHER_STORE_AND_28_PERCENT_OF_FABRIC_VOLUME_ONTO_THE_LEGACY_SHAPE_2026-09-27.md`.
