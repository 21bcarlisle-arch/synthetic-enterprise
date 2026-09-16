**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the committed weather-cell artefact was the stale one, and the accept branch was never dead

Delivery seat, 2026-09-16, in an isolated worktree at `a7faea4ff`. Claim
`weather-coverage-is-the-cap-on-the-half-hourly-shape`. Pre-registered before any number below was
computed: `docs/staging/SEAT_PREREG_THE_WEATHER_CELL_RE_CUT_AND_WHAT_IT_DOES_TO_THE_ACCEPT_BRANCH_2026-09-16.md`.

## The result against the predictions

Listed with outcomes, including the one I could not answer as registered.

| # | Prediction | Outcome |
|---|---|---|
| Q1 | the re-cut is a small perturbation of the accept branch, not a wipe-out | **HELD, on a population I had to change.** 117 of 194,865 occupied land cells reach the accept branch, against 203 of 175,188. Not 0. |
| Q1 (as registered) | 0–6 of a 210-household draw, seed 7, most likely ~2 | **NOT ANSWERED — the draw is not reproducible.** See below. |
| Q2 | the committed `REACHABILITY_WITNESS` has expired | **HELD.** `(50.4689, -4.1492)` is `(6, 10, 12)` against London's `(16, 10, 12)` — it kept wind and sun, lost temperature. |
| Q3 | the published coverage figures move, downward | **HALF WRONG, and the wrong half is the interesting one.** `all_three` fell 2.0% → 1.91% as predicted. But annual **sunshine ROSE**, 17.3% → 24.9%, and winter temperature rose 20.4% → 21.1%. Only wind fell. |

**Q3 is the one worth keeping.** The 09-07 cut had concluded that the centroid-era figures
"overstated the archive" — true of that pair, and I carried it forward as a direction of travel. It
is not one. A placement change moves a k-means partition in whatever direction it moves; three of
four figures went the other way this time. The module now carries all three cuts as a table, and the
sentence about overstatement is scoped to the pair it was measured on.

## What was wrong, and it was the commit

The drawn item, and the finding behind it, said the shared tree's uncommitted `sim/weather_cells/`
regeneration was a regression that killed `cell_matched_site`. Re-measured with none of those bytes:

* `_derived()` in this worktree reproduces the shared tree's "regression" **byte-for-byte** —
  194,865 occupied cells, identical coverage, identical cell labels on all four archive sites.
* The **committed** artefact is the stale one, and it has been unreproducible for nine days.
  `f27695607` landed it at 02:06 on 2026-09-07; `~/.cache/synthetic-enterprise/onsud/
  oa_cell_addresses.pkl` was written at 07:33 and `oa_region.pkl` at 09:56 the same morning. The
  artefact was cut over a placement that was still being built, which then grew by 19,677 cells.
* `test_derive_reproduces_the_committed_artefact` was **red at HEAD in any clean worktree holding
  the caches**, for those nine days. It was catching the commit, not the shared tree.

The HadUK normals have not moved since 2026-09-05 and the land mask still asserts 245,077 cells, so
the drivers are identical. What changed is which cells hold households.

## The mechanism was never dead — an expired witness reports the same `None`

The finding's evidence for "it accepts nothing" was a three-coordinate table. Two of those
coordinates match nothing under either partition. The third was `REACHABILITY_WITNESS` itself, at
the moment it had expired. **One live probe, and it was the constant whose own note says it expires.**

| | 09-07 cut | 09-16 cut |
|---|---|---|
| London | 28 cells, furthest 301 km | **23**, furthest **306 km** |
| Manchester | 4 | **6**, furthest 3 km |
| Glasgow | 3 | **3**, furthest 1 km |
| Cotswolds | 168 | **85**, furthest **514 km — a cell in Fife** |
| **total reaching the accept branch** | **203** | **117** |

The Cotswolds row is the best statement of the mechanism this project has produced: an Oxfordshire
weather CSV is the derivation's answer for a household on the Fife coast, 514 km north. No proximity
rule reaches that and none ever would.

## What was built

1. **`sim/weather_cells/{site_cells.json, occupied_land_cells.csv}` re-cut**, from this worktree's
   own `--derive` — not copied from the shared tree, so the bytes are the ones this tree can
   reproduce.
2. **`REACHABILITY_WITNESS` re-measured** to `(50.5305, -4.2225)`, 306 km from London and the
   furthest of the 23 cells sharing all three of its cells. It is **1.4 km from the ORIGINAL
   centroid-era witness**: the place was right both times and the 09-07 partition was the odd one
   out. Its note now states the rule (`--derive` re-measures this in the same pass) rather than the
   instance, because it has now moved twice for the same reason.
3. **The test stopped keeping a second copy of the witness.** `tests/simulation/
   test_weather_cell_siting.py` hard-coded the coordinate, so one fact lived in two files and a
   re-derivation had to remember both. It now reads `wcs.REACHABILITY_WITNESS`.
4. **`test_one_driver_disagreeing_refuses_the_whole_substitution` rewritten and renamed**
   `test_a_partial_agreement_refuses_the_whole_substitution` — see below, it is the real R15 finding
   in this turn.
5. **The module's published figures corrected in place**, superseded values kept beside their
   corrections in a three-row table rather than overwritten.

## The R15 finding: a control keyed to a PAIR, not to the property

`test_one_driver_disagreeing_refuses_the_whole_substitution` proved that the all-three AND was
load-bearing by naming Birmingham and Manchester: on the 09-07 partition Birmingham shared
Manchester's wind cell and neither other, so relaxing the AND to an OR would accept it.

Under this cut **Birmingham is `(0, 5, 15)` and shares nothing with any site on any driver**. The
test went red — and the red was not the control working. Had the pair been silently repaired, or
had the first three assertions been deleted as "stale", the survivor (`cell_matched_site(BIRMINGHAM)
is None`) would have **passed under the OR mutation too**, because a coordinate agreeing on nothing
is refused by an OR as readily as by an AND. The defect would have been completely ungraded with the
suite reading green.

*This is the catalogued shape "key a control to the property, not to today's answer", with the extra
turn that the partition the control is keyed to is itself a regenerated artefact — so the control
expires on a `--derive` run, exactly as the witness does, and neither is a code change anybody
reviews.*

The rewrite FINDS the partial agreements in the committed artefact instead of naming a pair:
asserts the population is **non-empty first** (a control that can only refuse passes against a
mechanism that refuses everything), then asserts every member of it is refused.

**Mutation-proven, 2026-09-16.** Swapping `site_cells["cells"] == sited["cells"]` for
`any(... == ...)` in `cell_matched_site` turns the rewritten control **red** on
`(50.1197, -5.2389)` returning `C1`. The old Birmingham-keyed control would have passed that
mutation. 14/14 green with the mutation reverted.

## Two things measured that I am NOT fixing here

**1. The 210-household figure has no reproducible population.** The module publishes "210/210 drawn
households resolve, and 2 of them match an archive site". Neither the module nor the 09-07 result
document records the draw: `draw_population(7)` yields **five** customers on the committed defaults,
and the 210 came from `docs/reports/run_output_f4b0b6334_*.json`, which is not in the tree. A
published count whose population cannot be re-drawn cannot be re-measured, and inventing a draw to
answer it would be reporting a new number as the old one. The module now says so and publishes a
grid-level property instead. *The population-level expectation, which IS reproducible, moves 2.0% →
1.91%, so ~4.2 → ~4.0 expected accepts on any 210-household draw; the observed 2 at 09-07 was
consistent with that and remains so.*

**2. The siting frame and the re-cut grid now disagree on 111 cells — 3 households.**
`sim/household_siting/region_household_frame.csv` holds 179,931 rows over **175,188 distinct
coordinates**, which is the 09-07 grid's count exactly: the frame is cut over the same occupied set
the superseded artefact was. The re-cut did not only add cells — 19,788 gained, **111 lost** — and
the frame still places 3 households in the 111. They receive the artefact refusal, which is correct
as far as this module can see, because this module's occupancy IS the completed placement.

It is a disagreement between two artefacts, not a property of a coordinate. **The frame is W2_18's
and 3 of 24,664,502 households is not a licence to regenerate another atom's 5 MB artefact from this
seat.** Named in the module at the paragraph that has to be re-measured if it is ever regenerated,
where the honest outcome is 0 miss.

## What this does NOT close, and it is the whole of the director's Stage 1 item

**The archive is four CSVs before this turn and four CSVs after.** 96.7% of the settled book is
still on `legacy_pc1_rescaled`; 213 of 228 eligibility verdicts are still the weather-coverage
refusal. The 09-07 re-cut was a LOOKUP fix; this one is a STALENESS fix; **neither is an
archive-breadth fix and no re-derivation can be one.**

What this turn bought is that the mechanism which widens coverage is now provably alive, provably
reproducible, and its controls survive the next `--derive`. That was the precondition and it was
genuinely broken — just not in the direction the item said.

## Next, and it is a pull

1. **Pull Open-Meteo for the cells the book actually occupies.** Before writing any of it: the
   shared tree holds `tools/pull_book_weather.py`, `tools/build_weather_world.py`,
   `sim/weather_world/` (7.9 MB) and `docs/design/W1_23_WEATHER_PHASE2_FRAME.md`, all uncommitted
   with mtimes of 2026-09-06 to 2026-09-09 — **eight days stranded, not a live lane**. That is a
   week of somebody's work on exactly this problem and it must be read before a line is written, or
   the REUSE gate is the least of it.
2. **Make the eligibility verdict name the site it could not find.** 213 identical refusals cannot
   tell anyone which archives to pull. Cheapest remaining lever, and it makes (1) targetable
   instead of guessed.
