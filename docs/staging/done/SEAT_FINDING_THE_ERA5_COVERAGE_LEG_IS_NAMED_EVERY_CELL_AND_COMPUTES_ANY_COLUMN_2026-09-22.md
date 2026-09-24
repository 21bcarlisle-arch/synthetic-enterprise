**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** none — incidental, found while declaring a coverage reduction

# The ERA5 coverage leg is named "every cell carries the ERA5 columns" and computes "any column, any row"

**Found** while writing the reduction-dimension declaration `check_era5_coverage` owed, closing one of
the seven `origin/main` reds. **Not fixed here: the fix is a judgement about what partial ERA5
coverage means for the fabric path, and that is the weather lane's, not a red-clearing commit's.**

## The leg

`tools/validate_weather_world.py::check_era5_coverage`:

```python
bare = sorted(
    cell for cell in cells["cells"]
    if not any(r.get(f) not in ("", None)
               for r in series.get(regime_of_cell.get(cell, cell), [])
               for f in ERA5_FIELDS))
```

`ERA5_FIELDS` is `('wind_speed_mean_ms', 'cloud_cover_pct', 'precipitation_mm')`.

## The two gaps between the name and the arithmetic

1. **THE FIELD COLLAPSE.** A cell is `bare` only if **no** field is present in **any** row. A cell
   holding wind and **no cloud** is therefore not bare and the leg **passes** it — while this
   module's own header says the fabric path reads cloud cover and *"a cell with temperature and no
   cloud cannot drive it"*. The leg's name says `every`; the code says `any`.
2. **THE TIME COLLAPSE.** One non-empty row passes the whole cell. How much of a cell's ten-year
   series actually carries the columns is not in the figure at all.

The failure message is honest about the population it counts (`N of M cell(s) hold temperature
only`) — it is the leg NAME and the header's stated purpose that the arithmetic does not deliver.

## What was done, and what deliberately was not

Both collapses are now **declared**, which is the mechanism this repo built for exactly this and
which makes the gap visible without deciding it. The banner reads:

    coverage of the share of store cells holding any ERA5 archive column at all:
      measured over any_era5_column_present (jointly);
      blind to within_cell_time_coverage;
      collapses any_era5_column_present = wind_speed_mean_ms + cloud_cover_pct + precipitation_mm

The claim string is `"the share of store cells holding any ERA5 archive column at all"` — deliberately
naming what is computed rather than what the leg is called.

**`any` was NOT changed to `all`.** It would change a world-fidelity verdict, and:

- it is a question about what a partially-pulled cell means for the fabric path, which the weather
  lane owns;
- the store is described elsewhere as having been "88% pulled", so tightening this may turn a passing
  leg into a failing one on real committed bytes — that is possibly the correct outcome and it is a
  decision, not a tidy-up;
- making one lane's judgement inside a commit whose subject is clearing another lane's reds is how a
  judgement stops being anyone's.

## Why this class matters beyond the instance

This is the canon's own shape, in its own words: it *"flatters in a consistent direction — always
making the sample look smaller and the coverage look better — which is why it must be looked for
rather than waited for."* Nothing over a NUMBER could have caught it: the arithmetic is correct on the
quantity it names. What was missing sat upstream, in nothing saying which axes the figure varied over.
The declaration was the thing that found it, on its first real application.

## What is NOT claimed

I have not established how many store cells are currently in the "some columns but not all" state.
The leg would have to be re-run with `all` to say, and that is the weather lane's measurement to take
— it is the first step, ahead of changing the operator.

**What done means:** the weather lane decides whether partial ERA5 coverage is acceptable to the
fabric path; the leg's NAME and its arithmetic agree either way; and if `any` is the right operator,
the leg is renamed to say so rather than the declaration carrying the whole confession.
