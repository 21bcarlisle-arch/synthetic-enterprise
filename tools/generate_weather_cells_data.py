"""The weather cells, published for the site's Knowledge section.

REUSE: tools/generate_weather_cells_data.py
CLASS: CUSTOM
INDEX: searched "generate", "site data", "knowledge", "cells", "map", "raster".
       `tools/generate_dashboard_data.py` and `tools/generate_delivery_page.py` publish company
       figures, not derived research. The three weather modules this stands on --
       `weather_cell_drivers`, `weather_cell_weights`, `weather_cell_derivation` -- are IMPORTED,
       and this is the runner named in `W1_14`'s own file_scope that they were frozen against as
       deliberately dormant. It computes nothing they compute; it downsamples and serialises.

WHY THIS EXISTS
---------------
Director console, 2026-09-06:

    "Make the weather cells visible on the site -- Knowledge section, with a map or whatever
     visualisation actually explains it. This is the first genuinely map-shaped thing the project
     has and the site has never carried a visual explanation of anything... Explanatory rather than
     decorative -- a domain reader should learn something they didn't know."

THREE THINGS THE PAGE HAS TO CONVEY, and the data each needs:

  1. **What a cell IS.** Climate classes, not contiguous regions. A map will show scattered patches
     sharing a colour and that reads as a bug unless it is said. Needs the per-cell band assignment
     on a real grid -- `map` below.
  2. **The coverage curve.** 34 / 89 / 987 on one shared partition against ~21 per driver held
     separately, so granularity reads as a price list rather than a fact. Needs both curves.
  3. **Half of Britain's land holds nobody**, which is why the wind map looks more complicated than
     it is. Needs the populated mask on the same grid, and the concentration figures.

THE MAP IS PUBLISHED AT 5 km, NOT 1 km, AND THAT IS THE ONLY LOSSY STEP
------------------------------------------------------------------------
The derivation runs on 245,077 land cells at 1 km. Serialising that per-cell would be a megabyte of
JSON for a picture 900 pixels wide, so the map is downsampled 5x by taking each 5 km block's
MODAL band -- not its mean, because a band id is a label and the mean of two labels is a third
label that belongs to neither. `downsample_modal` is the whole of it and it is tested for exactly
that confusion. Every NUMBER on the page comes from the full-resolution derivation; only the
picture is coarsened, and the page says so.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

OUT = PROJECT / "site" / "data" / "weather_cells.json"

#: 5 km blocks. 1450x900 at 1 km becomes 290x180, which is a legible picture and a small file.
BLOCK_KM = 5

#: The cell counts the page draws. `W1_27`'s decision is 21 per driver; the joint curve is `W1_21`'s.
DECISION_CELLS = 21
JOINT_TARGETS = ((0.90, 34), (0.95, 89), (0.99, 987))
CURVE_KS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987)

#: The driver the map is drawn on. Winter temperature is the one a heat-load reader came for.
MAP_DRIVER = "winter_temp"


def downsample_modal(labels, rows, cols, shape, block=BLOCK_KM):
    """Coarsen a per-cell LABEL grid by taking each block's most common label.

    A BAND ID IS A LABEL, NOT A QUANTITY. Averaging band 2 and band 8 gives band 5, which is a real
    band that neither cell belongs to and which will sit on the map looking like a place. The mode
    is the only summary that returns a label one of the cells actually has.

    Returns (grid, height, width) with -1 where a block holds no land.
    """
    import numpy as np

    height, width = shape
    out_h, out_w = -(-height // block), -(-width // block)
    grid = np.full((out_h, out_w), -1, dtype=int)
    br, bc = rows // block, cols // block
    key = br.astype(np.int64) * out_w + bc
    order = np.argsort(key, kind="stable")
    key_sorted, lab_sorted = key[order], np.asarray(labels)[order]
    bounds = np.flatnonzero(np.diff(key_sorted)) + 1
    for start, end in zip(np.r_[0, bounds], np.r_[bounds, len(key_sorted)]):
        block_labels = lab_sorted[start:end]
        counts = np.bincount(block_labels)
        grid.flat[key_sorted[start]] = int(counts.argmax())
    return grid, out_h, out_w


def _rle(values) -> str:
    """Run-length encode a row of small ints as `count:value` pairs, comma separated.

    A band map is enormously runny -- climate does not change every kilometre -- so this is what
    turns 52,200 cells into a few kilobytes. The page decodes it; nothing else reads it.
    """
    out, run, prev = [], 0, None
    for v in values:
        if v == prev:
            run += 1
        else:
            if prev is not None:
                out.append(f"{run}:{prev}")
            prev, run = v, 1
    if prev is not None:
        out.append(f"{run}:{prev}")
    return ",".join(out)


def build() -> dict:
    import numpy as np
    from sklearn.cluster import KMeans

    from tools import weather_cell_derivation as wcd
    from tools import weather_cell_drivers as drv
    from tools import weather_cell_weights as wgt

    d = drv.drivers()
    weights_all, coverage = wgt.aligned_to_land(d)
    occupied = weights_all > 0

    z, native, weights, mean, sd = wcd._space(True)
    index = wcd.DRIVERS.index(MAP_DRIVER)
    km = KMeans(n_clusters=DECISION_CELLS, n_init=1, random_state=0).fit(
        z[:, [index]], sample_weight=weights)

    # RE-LABEL THE BANDS IN DRIVER ORDER. k-means numbers its clusters arbitrarily, so a colour
    # ramp keyed to the raw label would put the coldest and warmest cells next to each other in the
    # legend and the map would look like noise. This is the difference between a picture that
    # explains and one that decorates.
    centres = km.cluster_centers_[:, 0]
    rank = {old: new for new, old in enumerate(np.argsort(centres))}
    bands = np.array([rank[int(lab)] for lab in km.labels_])

    east, north = d["east"][occupied], d["north"][occupied]
    # HadUK's grid starts at -199,500 m, so a cell's column is (easting + 200000) // 1000.
    cols = ((east + 200_000) // 1000).astype(int)
    rows = ((north + 200_000) // 1000).astype(int)
    grid, out_h, out_w = downsample_modal(bands, rows, cols, drv.GRID_SHAPE)

    # THE SAME GRID, over ALL land -- and as a DENSITY, not a flag.
    #
    # A binary "does this 5 km block contain anyone" reads 81% occupied against the 49.6% truth at
    # 1 km, because one populated square in twenty-five colours the whole block. The picture would
    # then contradict the number printed beside it, which is the worst thing an explanatory chart
    # can do. So each block carries how many of its 1 km cells are populated, banded 0-4, and the
    # page shades by it. `test_the_population_map_agrees_with_the_published_1km_share` holds the
    # picture to the figure.
    all_cols = ((d["east"] + 200_000) // 1000).astype(int)
    all_rows = ((d["north"] + 200_000) // 1000).astype(int)
    land = np.zeros_like(grid)
    lr, lc = all_rows // BLOCK_KM, all_cols // BLOCK_KM
    np.add.at(land, (lr, lc), 1)

    populated = np.zeros_like(grid)
    np.add.at(populated, (rows // BLOCK_KM, cols // BLOCK_KM), 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        share = np.where(land > 0, populated / np.maximum(land, 1), 0.0)
    # 0 = land with nobody on it; 1-4 = quartiles of occupancy within the block.
    density = np.where(land == 0, -1, np.clip(np.ceil(share * 4), 0, 4)).astype(int)

    band_stats = []
    for b in range(DECISION_CELLS):
        m = bands == b
        band_stats.append({
            "band": b,
            "winter_temp": round(float(np.average(native[m, index], weights=weights[m])), 2),
            "household_share": round(float(weights[m].sum() / weights.sum()), 4),
            "cells": int(m.sum()),
        })

    per_driver = wcd.per_driver_curve(CURVE_KS, space=(z, native, weights, mean, sd))
    joint = wcd.coverage_curve(CURVE_KS, space=(z, native, weights, mean, sd))

    order = np.argsort(-weights)
    cum = np.cumsum(weights[order]) / weights.sum()

    return {
        "_note": "Generated by tools/generate_weather_cells_data.py. Every NUMBER is computed at "
                 "1 km over 245,077 land cells; only the MAP is downsampled to 5 km.",
        "grid": {
            "block_km": BLOCK_KM, "height": out_h, "width": out_w,
            "driver": MAP_DRIVER,
            "note": "rows are south-to-north; -1 is sea or unpopulated land",
            "bands_rle": [_rle(row.tolist()) for row in grid],
            "density_rle": [_rle(row.tolist()) for row in density],
            "density_note": "-1 sea, 0 land with no household, 1-4 quartiles of the block's "
                            "1 km cells that hold households",
            "populated_1km_cells": int(populated.sum()),
            "land_1km_cells_in_map": int(land.sum()),
        },
        "bands": band_stats,
        "coverage": {
            "joint": joint,
            "per_driver": per_driver,
            "joint_targets": [{"target": t, "cells": c} for t, c in JOINT_TARGETS],
            "decision_cells": DECISION_CELLS,
        },
        "emptiness": {
            "land_cells": coverage["land_cells"],
            "land_cells_with_households": coverage["land_cells_with_households"],
            "households": coverage["households_placed"],
            "concentration": {f"{int(s * 100)}pc": int(np.searchsorted(cum, s)) + 1
                              for s in (0.5, 0.8, 0.9, 0.95, 0.99)},
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help=f"write {OUT.relative_to(PROJECT)}")
    args = ap.parse_args(argv)
    data = build()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
        print(f"[weather-cells] {OUT.relative_to(PROJECT)} "
              f"({OUT.stat().st_size} bytes, {data['grid']['height']}x{data['grid']['width']} map)")
        return 0
    print(json.dumps({k: v for k, v in data.items() if k != "grid"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
