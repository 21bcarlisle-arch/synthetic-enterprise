"""Where Britain's addresses actually are, at 1 km, from OS Open UPRN.

REUSE: tools/os_open_uprn.py
CLASS: CUSTOM
INDEX: searched "uprn", "address", "os open", "property", "gazetteer", "postcode".
       `tools/weather_cell_weights.py` places households from ONSPD postcode CENTROIDS and is the
       caller this exists to correct. `tools/fetch_haduk_grid.py` pulls a different archive on a
       different protocol and shares only the cache-root convention, two lines, copied not imported.
       Nothing in the tree reads an address point.

WHY THIS EXISTS
---------------
Director console, 2026-09-06, on the published map:

    "The classification comes from postcode centroids as far as I can tell, and a centroid is a
     point. A cell containing scattered dwellings whose postcode centroid falls in the neighbouring
     cell reads as empty -- which would undercount exactly where you'd expect, in sparse rural,
     isolated farms and dispersed roads. 53% is a plausible-sounding number and that is what makes
     it worth checking."

**He was right, and the undercount is 23 percentage points.** OS Open UPRN carries a British
National Grid coordinate for every addressable property in GB -- 41,629,393 of them -- which answers
"does an address exist in this square kilometre" directly rather than by proxy.

    GB land cells with at least one address     195,045   84.7%
    ... with ten or more                        120,464   52.3%
    the centroid method's occupied cells        121,668   52.9%

So the centroid method was never measuring "has an address". It was measuring, to within half a
percent, **"has ten or more addressable properties"** -- a hamlet or larger. Of the model's 121,668
occupied cells, exactly TWO hold no UPRN, so the placement is right where it puts things; it is the
absence that overstated.

WHAT THE CHECK DID NOT OVERTURN, AND THIS IS THE POINT
------------------------------------------------------
Re-placing every output area's households across the cells its addresses actually occupy, in
proportion to how many each holds, moves the household-weighted driver means by **1.2%, 1.0% and
0.1% of a standard deviation**. The 483,958 addresses on land the old method called empty are 1.2%
of GB's addresses -- a long thin tail of isolated properties. So the coverage claim was wrong by a
lot and every answer that rests on the WEIGHTS is unmoved, which was measured rather than hoped.

A UPRN IS AN ADDRESSABLE PROPERTY, NOT A DWELLING. It includes masts, substations, barns and bus
shelters. That is exactly right for "does an address exist here" and wrong for "how many households
are here" -- so the household COUNTS still come from the censuses and UPRN density is used only to
place them WITHIN an output area, where the census already fixes the total.
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "uprn"
ARCHIVE = CACHE / "osopenuprn.zip"
GRID = CACHE / "uprn_per_km_cell.npy"

#: OS Open UPRN, GB, CSV. Open Government Licence; no key, no account.
DOWNLOAD = ("https://api.os.uk/downloads/v1/products/OpenUPRN/downloads"
            "?area=GB&format=CSV&redirect")

#: The HadUK 1 km grid this is counted onto. Its origin is -199,500 m, so a cell's column is
#: `(easting + 200000) // 1000` -- the same arithmetic every other module here uses, stated once.
GRID_SHAPE = (1450, 900)
GRID_ORIGIN_M = -200_000

#: The August 2026 release. A count that moved would move every occupancy figure published from it,
#: so the expectation is pinned and `build_grid` refuses a wild departure rather than absorbing it.
EXPECTED_UPRNS = 41_629_393
UPRN_COUNT_TOLERANCE = 0.05


def pull(dest: Path = ARCHIVE, progress=print) -> Path:
    """Fetch the archive. 618 MB, one file, no key."""
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DOWNLOAD, timeout=1800) as src, dest.open("wb") as out:
        while chunk := src.read(1 << 22):
            out.write(chunk)
    progress(f"[uprn] {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def build_grid(archive: Path = ARCHIVE, dest: Path = GRID, progress=print):
    """Count addressable properties per 1 km cell, streaming the zip.

    NEVER UNPACKED TO DISK. The CSV is 2.27 GB and the only thing wanted from it is a 1450x900
    count -- ten megabytes. Reading it through the zip keeps the working set small enough that this
    can run on the regeneration cycle beside everything else.
    """
    import numpy as np

    if not archive.is_file():
        raise FileNotFoundError(f"{archive} -- run `python3 tools/os_open_uprn.py --pull` first")
    grid = np.zeros(GRID_SHAPE, dtype=np.int32)
    placed = dropped = 0
    with zipfile.ZipFile(archive) as zf:
        name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
        with zf.open(name) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
            header = text.readline()
            if "X_COORDINATE" not in header or "Y_COORDINATE" not in header:
                raise ValueError(f"OS Open UPRN has changed shape; header is {header!r}")
            while chunk := text.readlines(1 << 24):
                xs = np.empty(len(chunk))
                ys = np.empty(len(chunk))
                k = 0
                for line in chunk:
                    parts = line.split(",", 3)
                    if len(parts) < 3 or not parts[1] or not parts[2]:
                        dropped += 1
                        continue
                    try:
                        xs[k] = float(parts[1])
                        ys[k] = float(parts[2])
                    except ValueError:
                        dropped += 1
                        continue
                    k += 1
                cols = ((xs[:k] - GRID_ORIGIN_M) // 1000).astype(np.int64)
                rows = ((ys[:k] - GRID_ORIGIN_M) // 1000).astype(np.int64)
                on = ((cols >= 0) & (cols < GRID_SHAPE[1])
                      & (rows >= 0) & (rows < GRID_SHAPE[0]))
                np.add.at(grid, (rows[on], cols[on]), 1)
                placed += int(on.sum())
                dropped += int((~on).sum())

    drift = abs(placed - EXPECTED_UPRNS) / EXPECTED_UPRNS
    if drift > UPRN_COUNT_TOLERANCE:
        raise ValueError(
            f"placed {placed:,} UPRNs against an expected {EXPECTED_UPRNS:,} ({drift:.1%} out). "
            "Every occupancy figure published from this grid would move; refusing rather than "
            "absorbing a release that has changed under us.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    np.save(dest, grid)
    progress(f"[uprn] {placed:,} placed, {dropped:,} dropped, "
             f"{int((grid > 0).sum()):,} cells hold at least one -> {dest}")
    return grid


def cell_counts(dest: Path = GRID):
    """The 1450x900 grid of addressable properties per 1 km cell.

    REFUSES ON ABSENCE rather than falling back to postcode centroids. The whole finding is that
    centroids undercount by 23 points, so a silent fallback would restore the defect on any machine
    that had not pulled -- and it would restore it invisibly, which is worse than not having it.
    """
    import numpy as np

    if not dest.is_file():
        raise FileNotFoundError(
            f"{dest} is absent. Household placement needs the address record: postcode centroids "
            "undercount occupied cells by 23 percentage points and there is no honest fallback. "
            "Run `python3 tools/os_open_uprn.py --pull --build` (618 MB, Open Government Licence).")
    return np.load(dest)


def coverage(drivers, gb_mask) -> dict:
    """How much of GB land holds an address, at several thresholds.

    Published because "no address here" and "fewer than ten addresses here" are different claims
    and the old figure was quietly the second one.
    """

    grid = cell_counts()
    cols = ((drivers["east"] - GRID_ORIGIN_M) // 1000).astype(int)
    rows = ((drivers["north"] - GRID_ORIGIN_M) // 1000).astype(int)
    per_cell = grid[rows, cols]
    land = int(gb_mask.sum())
    return {
        "gb_land_cells": land,
        "addresses": int(per_cell[gb_mask].sum()),
        "cells_with_at_least": {str(t): int((gb_mask & (per_cell >= t)).sum())
                                for t in (1, 3, 5, 10, 25)},
        "share_with_any_address": round(float((gb_mask & (per_cell >= 1)).sum() / land), 4),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pull", action="store_true", help="fetch the 618 MB archive")
    ap.add_argument("--build", action="store_true", help="count addresses per 1 km cell")
    args = ap.parse_args(argv)
    if args.pull:
        pull()
    if args.build:
        build_grid()
    if not (args.pull or args.build):
        ap.print_help(sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
