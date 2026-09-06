"""Household weight per 1 km OSGB cell, from the censuses via postcode.

REUSE: tools/weather_cell_weights.py
CLASS: CUSTOM
INDEX: searched "census", "postcode", "household weight", "ONSPD", "output area", "weights".
       `tools/fetch_haduk_grid.py` pulls a different archive (CEDA) on a different protocol and
       shares only the cache-root convention, which is copied rather than imported because it is two
       lines. `simulation/population_draw.py` holds household counts for the DRAWN population, which
       is precisely the source this atom is forbidden to use. Nothing in the tree joins an
       administrative geography to an OSGB grid.

WHY THIS EXISTS
---------------
The weather ruling's decision 9, verbatim: *"Household weights come from the censuses (England &
Wales 2021, Scotland 2022) via postcode, NOT from the SIM's drawn population."*

That prohibition is the whole reason this is its own atom. Weighting the cells by the population the
SIM drew would make the coverage curve a statement about our own draw rather than about Britain, and
the circularity would be invisible in the output: the curve would look identical and mean nothing.

**And the weighting is the point, not a refinement.** `W1_19` measured the three drivers over the
245,077 land cells unweighted, which gives every empty Highland cell the same say as Birmingham. The
director's question was how much granularity captures the variation *for households*. An
area-weighted answer over-represents the uplands, which is the wrong direction for a supplier in
exactly the way that matters: it is the sparse, cold, windy end of the distribution that an
unweighted fit spends its cells on.

HOW THE JOIN WORKS, AND THE ONE CHOICE IN IT
--------------------------------------------
Three sources, all open:

  1. **ONSPD** (ONS Postcode Directory, live service) -- every UK postcode with its OSGB easting and
     northing to 1 m, its 2021/2022 output-area code, its country, its termination date and whether
     it is a small (residential) or large (single-organisation) user. This is the "via postcode" the
     ruling names.
  2. **Census 2021 TS041** (nomis `NM_2059_1`) -- number of households per 2021 output area, England
     and Wales. 188,880 areas.
  3. **Scotland's Census 2022** -- households per 2022 output area. Scotland is 8% of GB households
     and it is the cold, windy 8%; dropping it would bias the cell derivation in the single
     direction that matters most.

An output area holds several postcodes and the census does not say how its households divide between
them. **THE CHOICE, REPLACED 2026-09-06: households follow the ADDRESS RECORD within their output
area**, in proportion to how many addressable properties each 1 km cell actually holds.

The method it replaced split them equally across the area's postcode CENTROIDS, and a centroid is a
point. The director asked whether it was really true that 47% of GB kilometres hold no address; OS
Open UPRN says 15.3% do, and the centroid method was measuring "ten or more addressable properties"
to within half a percent while sounding like "anybody at all". `placement_cost()` measures what the
change is worth rather than asserting it, and the answer is two numbers pointing opposite ways:
occupied cells 121,668 -> 175,188, and the household-weighted driver means moving by 1.2%, 1.0% and
0.1% of a standard deviation. **The coverage claim was badly wrong and every answer resting on the
weights was unmoved.**

Postcodes with no grid reference, terminated postcodes, and large-user postcodes are excluded; each
exclusion is counted and reported, because a silent drop here would move the weights.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "census"

# RUN AS A SCRIPT, `sys.path[0]` IS `tools/` AND NOT THE REPO ROOT, so `from tools import ...`
# raises ModuleNotFoundError -- and pytest fixes the path before any test can import this module,
# so every test stays green while the command line is dead. Fifth module in this repository to
# ship that defect; `test_the_weighted_table_runs_THE_WAY_A_COMMAND_LINE_RUNS_IT` is the control.
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

ONSPD = ("https://services1.arcgis.com/ESMARspQHYMw9BZ9/ArcGIS/rest/services/"
         "ONSPD_Online_latest_Postcode_Centroids/FeatureServer/0")
NOMIS_TS041 = ("https://www.nomisweb.co.uk/api/v01/dataset/NM_2059_1.data.csv"
               "?geography=TYPE150&measures=20100&select=geography_code,obs_value")

#: NOMIS CAPS AN UNPAGED REQUEST AT 25,000 ROWS AND SAYS SO NOWHERE IN THE PAYLOAD. The first pull
#: returned exactly 25,000 of the 188,880 output areas -- a well-formed CSV, correct headers, real
#: values -- and would have produced a household weight map covering 13% of England with no error
#: anywhere. `pull_ts041` pages until a short page arrives and then asserts the total.
NOMIS_PAGE = 25_000
TS041_EXPECTED_AREAS = 188_880

#: Scotland's Census 2022 publishes no per-table API. The output-area topic pack is a 70 MB zip of
#: 71 CSVs; UV402 (accommodation type by household) is the one that carries a household TOTAL per
#: output area, under the column "All occupied households". UV406 (household size) totals to the
#: same figure and is the cross-check `pull_scotland` makes rather than trusting one column header.
SCOTLAND_ZIP = ("https://www.scotlandscensus.gov.uk/media/"
                "zz85kfinmf97whklasd98gfkadft5hj4f_Topic2H_20241120_1747/"
                "Census-2022-Output-Area-v1.zip")
SCOTLAND_EXPECTED_AREAS = 46_351

#: The three GB countries. Northern Ireland is out of scope: HadUK-Grid covers the UK, but the
#: company's market is GB and NI postcodes carry no OSGB grid reference in ONSPD.
GB_COUNTRIES = ("E92000001", "W92000004", "S92000003")

PAGE = 2000
ONSPD_CSV = CACHE / "onspd_gb_live_residential.csv"
TS041_CSV = CACHE / "ts041_households_by_oa21.csv"
SCOTLAND_CSV = CACHE / "scotland_2022_households_by_oa.csv"


def _get(url: str, tries: int = 5) -> bytes:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as fh:
                return fh.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:  # pragma: no cover - network
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"gave up after {tries} attempts: {url[:120]}") from last


def onspd_count(where: str = "1=1") -> int:
    q = urllib.parse.urlencode({"where": where, "returnCountOnly": "true", "f": "json"})
    return int(json.loads(_get(f"{ONSPD}/query?{q}"))["count"])


def pull_onspd(dest: Path = ONSPD_CSV, progress=print) -> Path:
    """Every live residential GB postcode with its grid reference and output area.

    PAGED BY OBJECTID RANGE, NOT BY `resultOffset`. Offset paging over 2.7 million rows makes the
    server re-scan from the start on every page and the pull slows to a crawl by page 400; an
    OBJECTID range is an indexed lookup and stays flat.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    top = onspd_count()
    fields = "PCDS,OA21CD,EAST1M,NORTH1M,CTRY25CD"
    where_country = " OR ".join(f"CTRY25CD='{c}'" for c in GB_COUNTRIES)
    kept = 0
    with dest.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["pcds", "oa", "east", "north", "country"])
        lo = 0
        while lo <= top:
            hi = lo + PAGE
            where = (f"OBJECTID>{lo} AND OBJECTID<={hi} AND DOTERM IS NULL "
                     f"AND USRTYPIND='0' AND ({where_country})")
            q = urllib.parse.urlencode({"where": where, "outFields": fields,
                                        "returnGeometry": "false", "f": "json"})
            page = json.loads(_get(f"{ONSPD}/query?{q}"))
            for feat in page.get("features", []):
                a = feat["attributes"]
                east, north = a.get("EAST1M"), a.get("NORTH1M")
                if not east or not north:
                    continue          # counted as a drop by census_weights(), not silently lost
                out.writerow([a["PCDS"], a.get("OA21CD") or "", int(east), int(north),
                              a["CTRY25CD"]])
                kept += 1
            lo = hi
            if lo % (PAGE * 50) == 0:
                progress(f"[weights] onspd {lo}/{top} scanned, {kept} kept")
    progress(f"[weights] onspd done: {kept} live residential GB postcodes -> {dest}")
    return dest


def pull_ts041(dest: Path = TS041_CSV, progress=print) -> Path:
    """Households per 2021 output area, England and Wales, from nomis. Paged, then counted."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    header = ""
    offset = 0
    while True:
        url = f"{NOMIS_TS041}&RecordLimit={NOMIS_PAGE}&RecordOffset={offset}"
        lines = _get(url).decode("utf-8-sig").splitlines()
        if not lines:
            break
        header = header or lines[0]
        body = [ln for ln in lines[1:] if ln.strip()]
        rows.extend(body)
        progress(f"[weights] ts041 {len(rows)} areas")
        if len(body) < NOMIS_PAGE:
            break
        offset += NOMIS_PAGE
    if len(rows) < TS041_EXPECTED_AREAS:
        raise RuntimeError(
            f"nomis returned {len(rows)} output areas, expected {TS041_EXPECTED_AREAS}. "
            "A short answer here is silent: the CSV is well formed and the weights it produces "
            "look plausible while covering a fraction of England.")
    dest.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    progress(f"[weights] ts041 -> {dest} ({len(rows)} areas)")
    return dest


def _scotland_table(zip_path: Path, prefix: str) -> dict[str, int]:
    """{output area: first numeric column} from one Scotland's Census output-area CSV.

    The files carry three lines of title before the header, and suppressed cells are "-" rather
    than 0 or blank.
    """
    import zipfile

    with zipfile.ZipFile(zip_path) as zf:
        name = next(n for n in zf.namelist() if n.startswith(prefix))
        lines = zf.read(name).decode("utf-8-sig", "replace").splitlines()
    out: dict[str, int] = {}
    for row in csv.reader(lines):
        if len(row) < 2 or not row[0].startswith("S00"):
            continue
        val = row[1].strip()
        out[row[0].strip()] = 0 if val in ("-", "") else int(float(val.replace(",", "")))
    return out


def pull_scotland(dest: Path = SCOTLAND_CSV, progress=print) -> Path:
    """Households per 2022 output area, Scotland, with a second table as the cross-check."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    archive = dest.parent / "scot_oa_topic.zip"
    if not archive.is_file():
        archive.write_bytes(_get(SCOTLAND_ZIP))
        progress(f"[weights] scotland zip -> {archive} ({archive.stat().st_size} bytes)")

    accommodation = _scotland_table(archive, "UV402")
    size = _scotland_table(archive, "UV406")
    if len(accommodation) < SCOTLAND_EXPECTED_AREAS:
        raise RuntimeError(f"UV402 holds {len(accommodation)} output areas, "
                           f"expected {SCOTLAND_EXPECTED_AREAS}")
    # TWO TABLES, ONE TOTAL. "All occupied households" is a column HEADING, and a heading is a claim
    # about what a column counts. UV406 counts the same households by size and must agree.
    disagree = {k: (v, size.get(k)) for k, v in accommodation.items() if size.get(k) != v}
    if len(disagree) > len(accommodation) // 100:
        raise RuntimeError(f"UV402 and UV406 disagree on {len(disagree)} of {len(accommodation)} "
                           "output areas -- the column being read is not the household total")

    with dest.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["oa", "households"])
        for code in sorted(accommodation):
            out.writerow([code, accommodation[code]])
    progress(f"[weights] scotland -> {dest} ({len(accommodation)} areas, "
             f"{sum(accommodation.values())} households, {len(disagree)} cross-check mismatches)")
    return dest


def read_households() -> dict[str, int]:
    """Households by output-area code, both censuses merged.

    FAILS CLOSED ON A MISSING SOURCE. An empty Scotland file would silently produce GB weights with
    no Scotland in them -- a 8% shortfall concentrated in the coldest, windiest cells, which is the
    one bias this atom exists to avoid. It refuses instead.
    """
    if not TS041_CSV.is_file():
        raise FileNotFoundError(f"{TS041_CSV} -- run `--pull` first")
    out: dict[str, int] = {}
    with TS041_CSV.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("GEOGRAPHY_CODE") or row.get("geography_code") or "").strip()
            val = (row.get("OBS_VALUE") or row.get("obs_value") or "").strip()
            if code and val:
                out[code] = int(float(val))
    if not SCOTLAND_CSV.is_file():
        raise FileNotFoundError(
            f"{SCOTLAND_CSV} is absent. Scotland is 8% of GB households and it is the cold, windy "
            "8%; weights without it would bias the cell derivation in the direction that matters "
            "most. Run `--pull-scotland`.")
    with SCOTLAND_CSV.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            code, val = row["oa"].strip(), row["households"].strip()
            if code and val:
                out[code] = int(float(val))
    return out


def census_weights() -> tuple[dict[tuple[int, int], float], dict[str, int]]:
    """({(cell_x, cell_y): households}, drop counts), placed on the ADDRESS RECORD.

    Cell indices are floor(metres / 1000), which is the HadUK-Grid 1 km cell containing the point:
    the grid's x coordinates are cell CENTRES at 500 m, 1500 m, ... so index i spans [i*1000,
    (i+1)*1000).

    THE PLACEMENT CHANGED ON 2026-09-06 AND THE DIRECTOR IS WHY. It used to split an output area's
    households equally across its postcode CENTROIDS -- and a centroid is a point, so a cell holding
    scattered dwellings whose postcode centroid fell next door read as empty. He asked whether it
    was really true that 47% of GB kilometres hold no address. It was not:

        GB land cells with at least one address (OS Open UPRN)   195,045   84.7%
        ... with ten or more                                     120,464   52.3%
        the centroid method's occupied cells                     121,668   52.9%

    The centroid method was measuring "has ten or more addressable properties" to within half a
    percent, and calling it "has anybody". Households are now spread across the cells an output
    area's addresses actually occupy, in proportion to how many each holds.

    THE COUNTS STILL COME FROM THE CENSUSES. A UPRN is an addressable property -- masts, barns and
    substations included -- which is exactly right for "is there an address here" and wrong for "how
    many households". UPRN density places; the census counts, and the census total for an output
    area is conserved exactly.
    """

    from tools import os_open_uprn as uprn

    if not ONSPD_CSV.is_file():
        raise FileNotFoundError(f"{ONSPD_CSV} -- run `--pull` first")
    households = read_households()
    grid = uprn.cell_counts()

    by_oa: dict[str, list[tuple[int, int]]] = defaultdict(list)
    drops = {"no_output_area": 0, "output_area_not_in_census": 0}
    with ONSPD_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            oa = row["oa"].strip()
            if not oa:
                drops["no_output_area"] += 1
                continue
            by_oa[oa].append((int(row["east"]), int(row["north"])))

    weights: dict[tuple[int, int], float] = defaultdict(float)
    fell_back = 0
    for oa, points in by_oa.items():
        n = households.get(oa)
        if n is None:
            drops["output_area_not_in_census"] += 1
            continue
        # THE OUTPUT AREA'S REACH: the cells its postcodes land in AND their immediate neighbours,
        # because the whole finding is that an area's addresses spill into cells no centroid
        # occupies. Bounded at one cell so a dense urban area does not smear across a city.
        reach = set()
        for east, north in points:
            col = (east + 200_000) // 1000
            row_ = (north + 200_000) // 1000
            for dc in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if 0 <= row_ + dr < grid.shape[0] and 0 <= col + dc < grid.shape[1]:
                        reach.add((row_ + dr, col + dc))
        counts = {rc: int(grid[rc]) for rc in reach}
        total = sum(counts.values())
        if total == 0:
            # NO ADDRESS ANYWHERE NEAR a populated output area is a contradiction, not a state.
            # It happens for a handful of areas whose postcodes are newer than the UPRN release;
            # they fall back to centroids and are COUNTED, because a silent fallback here would be
            # the defect this whole method replaced.
            fell_back += 1
            share = n / len(points)
            for east, north in points:
                weights[(east // 1000, north // 1000)] += share
            continue
        for (row_, col), k in counts.items():
            if k:
                weights[(col - 200, row_ - 200)] += n * k / total

    drops["census_areas_with_no_live_postcode"] = len(set(households) - set(by_oa))
    drops["output_areas_placed_on_centroids_for_want_of_an_address"] = fell_back
    return dict(weights), drops


#: A land cell further than this from any live GB residential postcode is not GB land at all.
#: NOT A ROUND NUMBER PICKED FOR TIDINESS -- the distance distribution over empty land cells is
#: sharply bimodal and this sits in the gap: 108,533 empty cells lie within 10 km of a postcode,
#: 965 in 10-20 km, and 13,207 beyond 50 km. The far mode is Northern Ireland, which the HadUK
#: land mask covers and ONSPD gives no OSGB grid reference for.
GB_REACH_KM = 20.0

#: Published GB land area, England + Wales + Scotland, as the independent check on the mask this
#: produces. ONS Standard Area Measurements: 130,279 + 20,779 + 77,933 km^2.
GB_LAND_AREA_KM2 = 228_991


def placement_cost() -> dict:
    """What moving households from postcode centroids onto the address record is worth.

    TWO NUMBERS POINTING OPPOSITE WAYS, which is the whole finding and the reason both are
    published. The COVERAGE claim was wrong by 23 percentage points. The WEIGHTS -- and therefore
    every cell count, coverage curve and correlation derived from them -- barely moved, because the
    addresses the centroid method missed are a long thin tail: 1.2% of Britain's, too few to shift a
    weighted mean and more than enough to ruin a map.
    """
    import numpy as np

    from tools import os_open_uprn as uprn
    from tools import weather_cell_drivers as drv

    households = read_households()
    grid = uprn.cell_counts()
    by_oa: dict[str, list[tuple[int, int]]] = defaultdict(list)
    with ONSPD_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["oa"].strip():
                by_oa[row["oa"].strip()].append((int(row["east"]), int(row["north"])))
    centroid: dict[tuple[int, int], float] = defaultdict(float)
    for oa, points in by_oa.items():
        n = households.get(oa)
        if n is None:
            continue
        share = n / len(points)
        for east, north in points:
            centroid[(east // 1000, north // 1000)] += share

    # THE ADDRESS PLACEMENT, BUILT ONCE. `census_weights()` is not called here, and the reason is
    # worth a line: the first draft wrote `[census_weights()[0].get(k, 0.0) for k in keys]`, which
    # calls it ONCE PER CELL -- 245,077 times, each re-reading 1.67 million postcodes. It ran for
    # twenty-five minutes at full CPU without finishing and would have taken weeks. A function call
    # in a comprehension's expression is evaluated per element, and a slow one hides there
    # perfectly: the code reads like a lookup.
    address: dict[tuple[int, int], float] = defaultdict(float)
    for oa, points in by_oa.items():
        n = households.get(oa)
        if n is None:
            continue
        reach = set()
        for east, north in points:
            col, row_ = (east + 200_000) // 1000, (north + 200_000) // 1000
            for dc in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if 0 <= row_ + dr < grid.shape[0] and 0 <= col + dc < grid.shape[1]:
                        reach.add((row_ + dr, col + dc))
        counts = {rc: int(grid[rc]) for rc in reach}
        total = sum(counts.values())
        if total == 0:
            share = n / len(points)
            for east, north in points:
                address[(east // 1000, north // 1000)] += share
            continue
        for (row_, col), k in counts.items():
            if k:
                address[(col - 200, row_ - 200)] += n * k / total

    d = drv.drivers()
    gb, _ = gb_reachable(d)
    keys = list(zip((d["east"] // 1000).astype(int).tolist(),
                    (d["north"] // 1000).astype(int).tolist()))
    old = np.array([centroid.get(k, 0.0) for k in keys])
    new = np.array([address.get(k, 0.0) for k in keys])

    out = {"gb_land_cells": int(gb.sum()),
           "occupied_on_centroids": int((gb & (old > 0)).sum()),
           "occupied_on_addresses": int((gb & (new > 0)).sum()),
           # CONSERVATION IS ABOUT WHAT WAS PLACED, NOT WHAT LANDED ON THE LAND GRID. The first
           # version compared `old.sum()` to `new.sum()` -- both restricted to the 245,077 land
           # cells -- and reported false, because address placement moves some coastal households
           # ONTO the grid that centroid placement left in a sea square. That is the two methods
           # differing, which is the point, not households going missing.
           "households_placed_on_centroids": round(sum(centroid.values())),
           "households_placed_on_addresses": round(sum(address.values())),
           "households_conserved": abs(sum(centroid.values()) - sum(address.values())) < 1.0,
           "households_on_land_grid": {"centroids": round(float(old.sum())),
                                       "addresses": round(float(new.sum()))},
           "driver_shift_in_sd": {}}
    for name in ("winter_temp", "annual_wind", "annual_sun"):
        v = d[name]
        mo = float(np.average(v[gb & (old > 0)], weights=old[gb & (old > 0)]))
        mn = float(np.average(v[gb & (new > 0)], weights=new[gb & (new > 0)]))
        sd = float(np.sqrt(np.average((v[gb & (old > 0)] - mo) ** 2, weights=old[gb & (old > 0)])))
        # A SHIFT IN STANDARD DEVIATIONS NEEDS A STANDARD DEVIATION. With one occupied cell there
        # is none, and the honest answer is None rather than a crash or a flattering zero -- the
        # whole point of this figure is to say whether the re-placement moved the weights, and
        # "cannot tell" is a different answer from "did not".
        out["driver_shift_in_sd"][name] = None if sd == 0.0 else round(abs(mn - mo) / sd, 4)
    return out


def gb_reachable(drivers, threshold_km: float = GB_REACH_KM):
    """(mask of land cells that are in GREAT BRITAIN, diagnostics).

    THE DEFECT THIS EXISTS TO CLOSE. HadUK-Grid's mask is the UNITED KINGDOM, and 16,210 of its
    245,077 land cells are Northern Ireland. ONSPD carries no OSGB grid reference for NI postcodes
    and this company's market is GB, so every one of those cells arrives with zero households -- and
    on a map it is indistinguishable from an empty Highland glen. Absence rendered as emptiness.

    It also moved a published figure: "half of Britain's land holds nobody" was 49.6% counting NI as
    empty British land, and is 52.9% occupied over GB alone.

    THE DISCRIMINATOR IS DISTANCE TO THE NEAREST LIVE GB POSTCODE, not a drawn box, because a box
    around NI is a judgement and the distance is a measurement. Cross-checked against the published
    GB land area: the mask this returns is within half a percent of it.
    """
    import numpy as np
    from scipy.spatial import cKDTree

    if not ONSPD_CSV.is_file():
        raise FileNotFoundError(f"{ONSPD_CSV} -- run `--pull` first")
    points = []
    with ONSPD_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            points.append((int(row["east"]), int(row["north"])))
    tree = cKDTree(np.array(points, dtype=float))
    distance, _ = tree.query(np.column_stack([drivers["east"], drivers["north"]]), k=1)
    mask = distance <= threshold_km * 1000.0

    cells = int(mask.sum())
    drift = abs(cells - GB_LAND_AREA_KM2) / GB_LAND_AREA_KM2
    if drift > 0.03:
        raise ValueError(
            f"the GB mask holds {cells:,} 1 km cells against a published land area of "
            f"{GB_LAND_AREA_KM2:,} km2 ({drift:.1%} out). The threshold is no longer separating "
            "Great Britain from the rest of the mask; refusing rather than publishing a map of "
            "somewhere else.")
    return mask, {"gb_land_cells": cells,
                  "not_gb_land_cells": int((~mask).sum()),
                  "published_gb_land_km2": GB_LAND_AREA_KM2,
                  "threshold_km": threshold_km}


def aligned_to_land(drivers: dict) -> tuple["object", dict]:
    """(weight per land cell, in the driver arrays' order; the households that fall off the grid).

    THE ONE THING THIS FUNCTION EXISTS TO MAKE VISIBLE. A postcode's 1 km cell is not always a
    HadUK land cell: coastal and estuary postcodes sit in squares the grid classifies as sea, and
    they carry real households. Aligning silently would drop them and leave a total that still
    looks like the census. The count comes back with the weights.
    """
    import numpy as np

    weights, drops = census_weights()
    keys = list(zip((drivers["east"] // 1000).astype(int).tolist(),
                    (drivers["north"] // 1000).astype(int).tolist()))
    vec = np.array([weights.get(k, 0.0) for k in keys])
    land = set(keys)
    off = [(k, v) for k, v in weights.items() if k not in land]
    return vec, {
        **drops,
        "cells_off_the_land_grid": len(off),
        "households_off_the_land_grid": round(sum(v for _, v in off)),
        "households_placed": round(float(vec.sum())),
        "land_cells_with_households": int((vec > 0).sum()),
        "land_cells": len(keys),
    }


def weighted_measurement() -> dict:
    """W1_20's published table: what household weighting does to W1_19's unweighted figures."""
    import numpy as np

    from tools import weather_cell_drivers as wcd

    d = wcd.drivers()
    w_, off = aligned_to_land(d)

    def wcorr(a: str, b: str) -> float:
        ca = d[a] - np.average(d[a], weights=w_)
        cb = d[b] - np.average(d[b], weights=w_)
        return round(float(np.average(ca * cb, weights=w_) / np.sqrt(
            np.average(ca * ca, weights=w_) * np.average(cb * cb, weights=w_))), 3)

    def wq(key: str, q: float) -> float:
        order = np.argsort(d[key])
        vals, ws = d[key][order], w_[order]
        return round(float(np.interp(q, np.cumsum(ws) / ws.sum(), vals)), 2)

    names = ("annual_temp", "winter_temp", "annual_wind", "annual_sun")
    order = np.argsort(-w_)
    cum = np.cumsum(w_[order]) / w_.sum()

    return {
        "coverage": off,
        "medians": {k: {"area": round(float(np.median(d[k])), 2), "household": wq(k, 0.5),
                        "household_p05": wq(k, 0.05), "household_p95": wq(k, 0.95)}
                    for k in names},
        "spread": {k: {"area_sd": round(float(d[k].std()), 3),
                       "household_sd": round(float(np.sqrt(np.average(
                           (d[k] - np.average(d[k], weights=w_)) ** 2, weights=w_))), 3)}
                   for k in names},
        "correlations": {f"{a}_x_{b}": {"area": round(float(np.corrcoef(d[a], d[b])[0, 1]), 3),
                                        "household": wcorr(a, b)}
                         for a, b in (("latitude", "annual_sun"), ("latitude", "annual_temp"),
                                      ("annual_temp", "annual_sun"),
                                      ("annual_temp", "annual_wind"),
                                      ("winter_temp", "winter_wind"),
                                      ("winter_wind", "annual_sun"))},
        "concentration": {f"{int(s * 100)}pc": int(np.searchsorted(cum, s)) + 1
                          for s in (0.5, 0.8, 0.9, 0.95, 0.99)},
    }


def summary() -> dict:
    weights, drops = census_weights()
    tot = sum(weights.values())
    top = sorted(weights.items(), key=lambda kv: -kv[1])[:5]
    return {
        "cells_with_households": len(weights),
        "households": round(tot),
        "drops": drops,
        "busiest_cells": [{"cell": list(c), "households": round(h)} for c, h in top],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pull", action="store_true", help="fetch ONSPD and TS041 into the cache")
    ap.add_argument("--summary", action="store_true", help="print the per-cell weight summary")
    ap.add_argument("--choice-cost", action="store_true",
                    help="measure address placement against the centroid method it replaced")
    ap.add_argument("--weighted", action="store_true",
                    help="recompute W1_20's table: weighting against W1_19's unweighted figures")
    args = ap.parse_args(argv)

    if args.weighted:
        print(json.dumps(weighted_measurement(), indent=2))
        return 0

    if args.pull:
        pull_ts041()
        pull_scotland()
        pull_onspd()
        return 0
    if args.choice_cost:
        print(json.dumps(placement_cost(), indent=2))
        return 0
    if args.summary:
        print(json.dumps(summary(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
