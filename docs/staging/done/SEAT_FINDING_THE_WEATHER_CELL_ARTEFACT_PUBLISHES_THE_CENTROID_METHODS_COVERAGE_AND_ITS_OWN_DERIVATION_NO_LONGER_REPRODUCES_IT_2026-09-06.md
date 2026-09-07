**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load · **Class:** figures_on_a_superseded_clock

# FINDING: the committed weather-cell artefact carries the centroid method's coverage figures, its own derivation no longer reproduces it, and the control that says so is red at HEAD

**Measured 2026-09-06 BST in the shared tree, and PROVED PRE-EXISTING at HEAD** — found while
landing the household coordinate (W2_18) and explicitly not caused by it: with
`tools/weather_cell_weights.py` restored byte-for-byte from HEAD, the failure reproduces with
identical numbers.

## The red

`tests/simulation/test_weather_cell_siting.py::test_derive_reproduces_the_committed_artefact`:

```
fresh["coverage"] != committed["coverage"]
  winter_temp   0.2036  vs  0.2051
  annual_wind   0.2782  vs  0.3072
  annual_sun    0.1725  vs  0.2792
  all_three     0.0200  vs  0.0348
```

## The cause, and it is dated

`sim/weather_cells/site_cells.json` records `"occupied_land_cells": 121668`. That is the **postcode
centroid** method's figure — `weather_cell_weights.census_weights` names it explicitly ("the
centroid method's occupied cells 121,668"). The placement moved to the **OS Open UPRN address
record** on 2026-09-06, which occupies 175,188 cells, on the director's own challenge to the claim
that 47% of GB kilometres hold no address.

So the artefact was not regenerated when the thing it is derived from changed. Everything on it is
one method behind.

## Why it matters more than a stale number

The four figures above are **published claims about what the weather archive covers**, and the
committed ones are all HIGHER than the truth on the current placement. `annual_sun` is the
extreme: **27.9% claimed against 17.3% measured** — the archive covers a little over half of what
the artefact says it does. `all_three`, the figure `weather_cell_siting.siting_refusal` prints in
its refusal text, reads 3.48% and is 2.00%.

This is `figures_on_a_superseded_clock` exactly: two methods, one artefact, and the surface quoting
the older one with no marker that it is older.

## What it is NOT

It is not W2_18's, and it is not the household coordinate's. The proof is the reverted-file rerun
above: identical numbers with HEAD's `weather_cell_weights.py`.

It is also not obviously a one-line fix, which is why this is a finding rather than a repair.
Regenerating the artefact moves four published percentages, and the coverage figures appear in
`simulation/weather_cell_siting.py`'s own docstring table, in
`docs/market_research/how_many_weather_cells_britain_needs_and_why_the_answer_is_a_curve.md`, and in
the refusal text the seam emits. The regeneration and the surfaces have to move together, and that
is W1_14's lane's call, not a passing lane's.

## What to do

1. Regenerate `sim/weather_cells/site_cells.json` from the current placement (`derive()` is the
   expensive path and it reproduces — it is the disagreement that is the finding, not an inability
   to compute).
2. Move the four percentages wherever they are quoted, in the same commit.
3. Keep `test_derive_reproduces_the_committed_artefact` exactly as it is. It did its job: it is the
   only thing in the tree that noticed, and it noticed on the day.
