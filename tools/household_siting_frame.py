"""Where a household in a given GB region actually is — the sampling frame for W2_18's coordinate.

REUSE: tools/household_siting_frame.py
CLASS: CUSTOM
INDEX: searched "coordinate", "lat lon", "region", "siting", "household weight", "postcode",
       "census". `tools/weather_cell_weights.py` already joins the censuses to the 1 km OSGB grid
       and this module CALLS it rather than repeating the placement -- the one thing it lacks is a
       REGION label per cell, which is added there as `census_weights(group_of=...)` (one grouping
       key threaded through the existing loop, not a second implementation).
       `tools/weather_cell_drivers.py` already carries the true latitude/longitude of every land
       cell from the normals file's auxiliary coordinates, so no OSGB->WGS84 transform is written
       here. `simulation/adoption_geography.py` holds a lat/lon per region, but it is ONE CENTROID
       PER REGION on the fourteen GSP groups -- a different vocabulary, and a centroid is not a
       household distribution (see WHY A CENTROID IS NOT THE ANSWER below). Nothing in the tree
       maps a household to a point.

WHY THIS EXISTS
---------------
`population_draw.SyntheticCustomer.to_customer_dict` renders `{"lat": None, "lon": None, "region":
...}` for 100% of drawn households. Measured 2026-09-06 over a 210-customer draw: 210 of 210 carry
no coordinate, with the region curriculum ON and ten real GB regions drawn. The derived weather
cells (W1_19-W1_22, W1_25) are keyed by COORDINATE, so every drawn household is refused by
`weather_cell_siting.cells_for_location` and the world's household heat load is driven by none of
the derivation. The full measurement is in
`docs/staging/SEAT_FINDING_W1_14_WAITED_ON_THE_WRONG_GAP_2026-09-06.md`.

The binding question is not wiring. It is: **what sources a household's coordinate?** The
curriculum's region marginal gives a REGION, and a region is not a point. Inventing one is the
fabrication `fabric_physics.latitude_for_weather_site` refuses one layer down, and the placeholder
is deliberately protected by `test_region_is_explicit_placeholder_not_fabricated`.

IT CAN BE SOURCED, AND THIS IS THE CHAIN
----------------------------------------
Every link is published and every one of them is already pulled and cached by this repository for
the weather-cell derivation. Nothing new is fetched except one column:

  1. **Census 2021 TS041** — households per 2021 output area, England and Wales (188,880 areas) —
     **and Scotland's Census 2022**, households per 2022 output area (46,351 areas). *How many
     households are there.* Both are already merged by `weather_cell_weights.read_households`,
     which fails closed on a missing Scotland; the frame lost Scotland at the REGION LABEL, one
     step later, not here.
  2. **OS Open UPRN** — addressable properties per 1 km OSGB cell. *Where inside an output area
     the addresses are.* (`tools/os_open_uprn.py`; the placement decision and its cost are
     `weather_cell_weights.census_weights`'s, not re-litigated here.)
  3. **ONSPD** — every live residential GB postcode with its output area, its grid reference and,
     the one column this module adds, **`RGN25CD`** — the ONS region. *Which region an output area
     is in.* England and Wales only; Scotland is one region and is read off the `S00` output-area
     code space instead, which is why it needs no row here.
  4. **HadUK-Grid normals** — the true latitude and longitude of each 1 km land cell, from the
     file's own auxiliary coordinates rather than an OSGB->WGS84 transform written here.

Composed: for each of the curriculum's ten regions, the household-weighted distribution over the
1 km cells that region's households actually occupy, each cell carrying the coordinate the weather
derivation itself uses. A drawn household's coordinate is then a DRAW from its region's own
household distribution — sourced, not fabricated, and reproducing the real within-region spread.

WHY A CENTROID IS NOT THE ANSWER, AND THIS IS THE POINT OF THE WHOLE FRAME
-------------------------------------------------------------------------
The cheap alternative is one point per region — `adoption_geography.REGION_FIELD` already holds
fourteen. It fails for exactly the reason the cells exist: a region is not climatically uniform, so
a centroid puts every household in one weather cell and the derivation's 21-cell partition collapses
to at most one cell per region. `measurement()` prices this rather than asserting it: it reports,
per region, the household-weighted spread of the three drivers and how many distinct cells the
region's households occupy, against the one a centroid would give.

WHAT IS OUT OF SCOPE, NAMED RATHER THAN SILENT
----------------------------------------------
**Northern Ireland.** Out of the company's market and carrying no OSGB grid reference in ONSPD.
This is the only entry on this list that is genuinely the sources' scope.

**SCOTLAND WAS ON THIS LIST UNTIL 2026-09-07 AND IT DID NOT BELONG HERE.** The note said the frame
carried no Scottish region because the curriculum's marginal draws none — a true sentence about the
curriculum, offered as the reason for a fact about the FRAME, and the two have different causes.
The frame's own cause was `region_namer`: it resolved every output area through the
England-and-Wales lookup, so all 46,270 Scottish output areas — **arriving with their household
counts already joined**, because `weather_cell_weights` pulls Scotland's Census 2022 and fails
closed without it — fell into `output_area_outside_the_grouping` and were discarded. That counter
was in the committed manifest from the first build, reading 46,270 against Scotland's 46,351 areas,
and nothing was watching it.

The frame now covers **eleven regions** and holds Scotland's 2.5 M households. What is still true
is the sentence about the curriculum: `region_marginal_synthetic_acquisitions` draws ten regions,
so **the world draws no Scottish household yet** and the frame's Scottish rows site nobody today.
That is deliberate and it is the next piece, not an oversight — the marginal is a ratified value
whose own `basis` inherited the same England-and-Wales scope from the same join, and recomputing it
over GB is a fidelity change to the world (R13), named and versioned, not a labelling fix. It is
recorded in
`docs/staging/SEAT_FINDING_SCOTLAND_WAS_NOT_OUTSIDE_THE_CENSUS_JOIN_IT_WAS_DROPPED_BY_THE_LABELLER_2026-09-07.md`.

`build()` therefore asserts the frame **covers** the curriculum's regions rather than equalling
them: the hazard is a drawn region that cannot be sited, and a frame region nobody draws is not
that hazard. Extras are named in the manifest as `regions_the_curriculum_does_not_draw`.

**A household's coordinate is a DRAW, not a discovery.** It is the world's ground truth for where
the household is, drawn from the published distribution of where households are. It is not a claim
that any particular household lives there, and it never crosses the epistemic wall as an address.
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
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# RUN AS A SCRIPT, `sys.path[0]` IS `tools/` AND NOT THE REPO ROOT -- the same defect
# `weather_cell_weights` documents; `test_the_frame_builds_THE_WAY_A_COMMAND_LINE_RUNS_IT` is the
# control, and it is why this line is here rather than in a comment.
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "census"
OA_REGION_CSV = CACHE / "oa21_to_region_england.csv"

ARTEFACT_DIR = PROJECT / "sim" / "household_siting"
FRAME_CSV = ARTEFACT_DIR / "region_household_frame.csv"
FRAME_MANIFEST = ARTEFACT_DIR / "region_household_frame.json"

#: ONS's OWN OUTPUT-AREA-TO-REGION LOOKUP, and the third source tried. It is one row per 2021
#: output area, which is what makes it the right one: a region per OUTPUT AREA is exactly the join
#: `weather_cell_weights` needs, and this table is a function by construction.
#:
#: THE TWO IT REPLACED, AND WHY, BECAUSE THE SECOND FAILED FOR A REAL REASON. ONSPD carries
#: `RGN25CD` per POSTCODE, and two ways of reading it were tried and abandoned: a distinct query
#: over (OA21CD, RGN25CD) at 31.8 seconds per 2,000-row page (47 minutes, because each page is a
#: fresh full scan), and an OBJECTID-ranged scan of 2.7 million postcodes -- which ran, and RAISED,
#: on output area E00174957 holding postcodes in BOTH London (E12000007) and the South East
#: (E12000008). That is not a data error: ONSPD assigns a region to a POSTCODE, and an output area
#: whose postcodes straddle a boundary genuinely has two. Reading it as an output-area attribute
#: would have picked whichever postcode came first in OBJECTID order and reported nothing. The
#: refusal that caught it is `pull_oa_regions`'s and is kept, because this source is only a
#: function while ONS says it is.
OA_LOOKUP = ("https://services1.arcgis.com/ESMARspQHYMw9BZ9/ArcGIS/rest/services/"
             "OA21_PARNCP25_LAD_CTYUA_RGN_CTRY_EW_LU/FeatureServer/0")

#: The lookup's own `maxRecordCount`. Asking for more returns that many and sets
#: `exceededTransferLimit`, which `pull_oa_regions` checks rather than assuming a short page.
PAGE = 1000

#: 2021 output areas in England and Wales. The pull asserts it, because a lookup that silently
#: returns a prefix is this project's most expensive recurring shape (`weather_cell_weights` was
#: handed 25,000 of 188,880 output areas by a capped nomis request, with no error anywhere).
EXPECTED_OUTPUT_AREAS = 188_880

#: ONS region codes to the names the curriculum's `region_marginal_synthetic_acquisitions` uses.
#: E12000006 IS PUBLISHED AS "East of England" AND THE CURRICULUM CALLS IT "East". The join is on
#: the CODE, so the name difference is a rendering choice recorded here rather than a silent
#: mismatch that would drop 10.7% of the book's households on a string compare.
REGION_NAMES = {
    "E12000001": "North East",
    "E12000002": "North West",
    "E12000003": "Yorkshire and The Humber",
    "E12000004": "East Midlands",
    "E12000005": "West Midlands",
    "E12000006": "East",
    "E12000007": "London",
    "E12000008": "South East",
    "E12000009": "South West",
}

#: WALES IS A COUNTRY AND NOT A REGION, so the lookup carries the country code in its region
#: column for every Welsh output area. The curriculum's marginal lists it beside the nine English
#: regions, so it is named here and joined the same way.
WALES_CODE = "W92000004"
WALES = "Wales"

#: SCOTLAND IS THE SAME SHAPE AS WALES -- one country, carried as one region -- and it needs no
#: lookup row at all, which is why it was lost. `OA_LOOKUP` is the England-and-Wales output-area
#: table, so `read_oa_regions` cannot hold a Scottish area and `region_namer` returned None for
#: every one of them. The join itself was never the limit: `weather_cell_weights.read_households`
#: merges Scotland's Census 2022 (46,351 areas) with TS041 and fails closed without it.
#:
#: MEASURED 2026-09-07 BEFORE THIS LINE EXISTED: of the 46,270 output areas the labeller dropped
#: into `output_area_outside_the_grouping`, **46,270 carried the S00 prefix and none did not**, and
#: they held 2,503,270 households -- 9.2% of the GB census total, counted by the join and discarded
#: one step later. The frame's own manifest had been recording that number since it was first
#: built.
#:
#: THE PREFIX IS THE CODE STANDARD, NOT AN INFERENCE. `S00` is NRS's output-area code space and is
#: wholly within Scotland, exactly as `weather_cell_weights._scotland_table` already relies on when
#: it reads the census pack. There is no Scottish equivalent of the London/South East straddle that
#: `pull_oa_regions` refuses on, because the country boundary is not a region boundary any output
#: area crosses.
SCOTLAND_OA_PREFIX = "S00"
SCOTLAND = "Scotland"

#: REGIONS THE FRAME CARRIES THAT THE CURRICULUM DOES NOT YET DRAW, ENUMERATED SO THE RELAXATION
#: BELOW IS BOUNDED. `build()` stopped demanding frame == curriculum on 2026-09-07, because that
#: equality is what kept Scotland's sourced households discarded: the frame could not carry a real
#: GB region until the world agreed to draw from it. Coverage (frame >= curriculum) is the property
#: that actually protects a drawn household.
#:
#: But a bare `>=` would also wave through a MISSPELLED region -- `"Scotand"` in the frame, nobody
#: drawn into it, no refusal anywhere -- which is a worse failure than the one being fixed because
#: it looks like coverage. So the extras are named here and `build()` refuses any it does not
#: recognise. Removing a name from this set is how the frame goes back to matching the world.
CARRIED_AHEAD_OF_THE_CURRICULUM = frozenset({SCOTLAND})


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


def pull_oa_regions(dest: Path = OA_REGION_CSV, progress=print) -> Path:
    """Every 2021 output area in England and Wales with its ONS region.

    Refuses on a short pull, on an unnameable region code, and on an output area that arrives
    twice with two different regions -- the last is what the ONSPD route actually did, and the
    check survives its cause because "the region is a function of the output area" is the
    assumption every household weight below rests on.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    q = urllib.parse.urlencode({"where": "1=1", "returnCountOnly": "true", "f": "json"})
    top = int(json.loads(_get(f"{OA_LOOKUP}/query?{q}"))["count"])
    if top != EXPECTED_OUTPUT_AREAS:
        raise ValueError(f"the lookup holds {top:,} output areas, expected "
                         f"{EXPECTED_OUTPUT_AREAS:,} -- the geography has changed and the census "
                         "household counts are keyed to the 2021 one")
    seen: dict[str, str] = {}
    cursor = ""
    while True:
        # A KEYSET SCAN, and the reason it is one is a WRONG DIAGNOSIS kept here beside its
        # correction, because the correction is the whole lesson.
        #
        # The offset-paged version came back with 178,605 of 188,880 output areas and the count
        # check below refused it. Offset paging over a large ordered set was the obvious culprit,
        # so the pager was rewritten to seek on the sort key -- and it returned 178,605. Exactly
        # the same number, by a method that cannot skip a row. The pager had never been the
        # problem: **all 10,275 of Wales's output areas carry a NULL region column** (asked of the
        # server: 10,275 Welsh rows, 10,275 null regions, and 178,605 + 10,275 = 188,880), because
        # Wales is a COUNTRY and this table's region column is England's. The `if not rgn:
        # continue` a few lines below was dropping every Welsh household -- 5.7% of the
        # curriculum's book, a whole region of the ten, silently.
        #
        # The keyset scan is kept because it is the better pager, not because it fixed anything.
        # What fixed it is reading the country column too. What FOUND it is the count check: it
        # was written for a different failure and caught this one, which is the argument for
        # asserting the total rather than trusting the loop.
        params = urllib.parse.urlencode({
            "where": f"OA21CD>'{cursor}'" if cursor else "1=1",
            "outFields": "OA21CD,RGN25CD,CTRY25CD", "returnGeometry": "false",
            "orderByFields": "OA21CD", "resultRecordCount": PAGE, "f": "json"})
        page = json.loads(_get(f"{OA_LOOKUP}/query?{params}"))
        rows = page.get("features", [])
        if not rows:
            break
        cursor = max((r["attributes"].get("OA21CD") or "") for r in rows)
        for feat in rows:
            a = feat["attributes"]
            oa = (a.get("OA21CD") or "").strip()
            # THE COUNTRY IS THE FALLBACK, NOT A CONVENIENCE: Wales has no region code in this
            # table at all, and the curriculum's marginal lists it beside the nine English
            # regions. An output area with neither is left out of `seen` and the count check
            # below refuses the whole pull rather than writing a lookup with a hole in it.
            rgn = ((a.get("RGN25CD") or "").strip() or (a.get("CTRY25CD") or "").strip())
            if not oa or not rgn:
                continue
            prior = seen.get(oa)
            if prior is not None and prior != rgn:
                raise ValueError(f"output area {oa} is in two regions ({prior}, {rgn}) -- the "
                                 "region is not a function of the output area, and every "
                                 "household weight below assumes it is")
            seen[oa] = rgn
        if len(seen) % (PAGE * 25) == 0:
            progress(f"[siting] oa->region {len(seen)}/{top}")
    if len(seen) != top:
        raise ValueError(f"pulled {len(seen):,} of {top:,} output areas -- a lookup that returns a "
                         "prefix and no error is how a household weight map covers 13% of England")
    unknown = sorted(set(seen.values()) - set(REGION_NAMES) - {WALES_CODE})
    if unknown:
        raise ValueError(f"the lookup returned region codes this module cannot name: {unknown}")
    with dest.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["oa", "region_code"])
        for oa in sorted(seen):
            out.writerow([oa, seen[oa]])
    progress(f"[siting] oa->region done: {len(seen)} output areas -> {dest}")
    return dest


def read_oa_regions(path: Path = OA_REGION_CSV) -> dict[str, str]:
    """{output area code: ONS region code} for England. Raises if the pull has not run."""
    if not path.is_file():
        raise FileNotFoundError(f"{path} -- run `python3 -m tools.household_siting_frame --pull`")
    with path.open(encoding="utf-8") as fh:
        return {r["oa"].strip(): r["region_code"].strip() for r in csv.DictReader(fh)}


def region_namer(path: Path = OA_REGION_CSV):
    """`oa -> GB region name`, or None for an output area the frame cannot place.

    ELEVEN REGIONS: the nine English ones, Wales, and Scotland. Scotland is answered from the `S00`
    code space and never from `lookup`, because `OA_LOOKUP` is the England-and-Wales table and has
    no Scottish row to hold -- see `SCOTLAND_OA_PREFIX` for the measurement that says this was a
    lost region and not the join's scope.

    None is still the answer for anything neither route names, and `census_weights` counts those as
    `output_area_outside_the_grouping` rather than absorbing them into a region, because households
    quietly folded into the wrong region would move that region's weather and leave the national
    total looking right. That is how Scotland stayed lost: the counter was correct and nobody read
    it.
    """
    codes = {**{c: n for c, n in REGION_NAMES.items()}, WALES_CODE: WALES}
    lookup = read_oa_regions(path)

    def region_of(oa: str) -> str | None:
        if oa.startswith(SCOTLAND_OA_PREFIX):
            return SCOTLAND
        code = lookup.get(oa)
        return codes.get(code) if code else None

    return region_of


# ---------------------------------------------------------------------------
# The expensive path. Everything below reads `~/.cache/synthetic-enterprise`.
# ---------------------------------------------------------------------------


def frame() -> tuple[dict[str, list[tuple[float, float, float]]], dict]:
    """({region: [(lat, lon, households), ...]}, diagnostics) over 1 km land cells.

    THE COORDINATES ARE THE DERIVATION'S OWN. Each cell's latitude and longitude come from the
    HadUK-Grid normals file's auxiliary coordinates, the same values `weather_cell_drivers` reads,
    so a household sited here lands in the cell the weather derivation would put it in — rather
    than in whatever an OSGB->WGS84 transform written in this module happened to give.

    A CELL OFF THE LAND GRID IS COUNTED, NOT DROPPED SILENTLY. Coastal and estuary postcodes sit in
    squares HadUK classifies as sea and they carry real households; `weather_cell_weights.
    aligned_to_land` documents that for the ungrouped map and the same figure is reported here per
    region, because a region that is mostly coast would lose the most and look ordinary.
    """
    import numpy as np

    from tools import weather_cell_drivers as wcd
    from tools import weather_cell_weights as wcw

    by_region, drops = wcw.census_weights(group_of=region_namer())
    d = wcd.drivers()
    keys = list(zip((d["east"] // 1000).astype(int).tolist(),
                    (d["north"] // 1000).astype(int).tolist()))
    index = {k: i for i, k in enumerate(keys)}
    lat = d["latitude"]

    with wcd._open("tas") as ds:
        xs = ds.coords["projection_x_coordinate"].values
        ys = ds.coords["projection_y_coordinate"].values
        lon_grid = ds.coords["longitude"].values
    lon = lon_grid[np.searchsorted(ys, d["north"]), np.searchsorted(xs, d["east"])]

    out: dict[str, list[tuple[float, float, float]]] = {}
    per_region = {}
    off_cells = off_households = 0.0
    for region, cells in sorted(by_region.items()):
        rows, lost = [], 0.0
        for cell, households in cells.items():
            i = index.get(cell)
            if i is None:
                off_cells += 1
                lost += households
                continue
            rows.append((round(float(lat[i]), 4), round(float(lon[i]), 4), round(households, 3)))
        rows.sort()
        out[region] = rows
        off_households += lost
        per_region[region] = {
            "cells": len(rows),
            "households": round(sum(r[2] for r in rows)),
            "households_off_the_land_grid": round(lost),
        }
    diagnostics = {**drops,
                   "cells_off_the_land_grid": int(off_cells),
                   "households_off_the_land_grid": round(off_households),
                   "per_region": per_region,
                   "regions": sorted(out)}
    return out, diagnostics


def expected_regions() -> set[str]:
    """The regions the curriculum's marginal actually draws — the frame must cover exactly these.

    READ FROM THE CURRICULUM, NOT LISTED HERE. A frame that lists its own regions cannot notice the
    director adding one, and the failure mode is silent: an unlisted region draws a household the
    frame cannot site, and the coordinate goes back to None for that slice alone.
    """
    from simulation.population_draw import _load_cohort_curriculum, region_weights_from_curriculum

    return set(region_weights_from_curriculum(_load_cohort_curriculum()))


def build(progress=print) -> dict:
    """Write the committed frame and its manifest. Refuses on a region set that does not match."""
    rows, diagnostics = frame()
    want = expected_regions()
    missing = want - set(rows)
    if missing:
        raise ValueError(
            f"the frame covers {sorted(rows)} and the curriculum's region marginal draws "
            f"{sorted(want)}. Missing: {sorted(missing)}. A household drawn into a region the "
            "frame does not cover cannot be sited, and the coordinate would silently go back to "
            "None for that slice alone.")
    # COVERAGE, NOT EQUALITY, AND THE DIRECTION MATTERS. The hazard is a curriculum region the
    # frame cannot site; a frame region the curriculum never draws sites nobody. But the extras are
    # ENUMERATED and not merely counted -- see `CARRIED_AHEAD_OF_THE_CURRICULUM` for why a bare
    # `>=` would be a worse control than the equality it replaced.
    extra = set(rows) - want
    unknown = extra - CARRIED_AHEAD_OF_THE_CURRICULUM
    if unknown:
        raise ValueError(
            f"the frame carries {sorted(unknown)}, which the curriculum does not draw and "
            f"`CARRIED_AHEAD_OF_THE_CURRICULUM` does not name. A region no household is ever "
            "drawn into sites nobody and refuses nothing, so a misspelt one is invisible. Name it "
            "there with its reason, or fix the label.")
    diagnostics["regions_the_curriculum_does_not_draw"] = sorted(extra)
    ARTEFACT_DIR.mkdir(parents=True, exist_ok=True)
    with FRAME_CSV.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["region", "lat", "lon", "households"])
        for region in sorted(rows):
            for lat, lon, households in rows[region]:
                out.writerow([region, f"{lat:.4f}", f"{lon:.4f}", f"{households:.3f}"])
    manifest = {
        "source": "Census 2021 TS041 + OS Open UPRN + ONSPD (RGN25CD) + HadUK-Grid 1 km normals",
        "placement": "tools.weather_cell_weights.census_weights(group_of=ONS region)",
        "cells": sum(len(v) for v in rows.values()),
        "households": round(sum(h for v in rows.values() for _, _, h in v)),
        "diagnostics": diagnostics,
    }
    FRAME_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    progress(f"[siting] frame: {manifest['cells']} cells, {manifest['households']:,} households "
             f"-> {FRAME_CSV}")
    return manifest


def measurement() -> dict:
    """What the frame buys over one point per region — the figure that decides whether it is worth
    having, rather than an assertion that it is.

    Per region: the cells its households occupy and the household-weighted spread of the three
    heat-load drivers WITHIN the region. A centroid gives one point, one cell and a within-region
    spread of exactly zero by construction, so every figure here is variation a centroid throws
    away. Reported beside the national spread, because a region whose internal spread approaches
    the national one is a region the region label was never telling you much about.
    """
    import numpy as np

    from tools import weather_cell_drivers as wcd
    from tools import weather_cell_weights as wcw

    named = ("winter_temp", "annual_wind", "annual_sun")
    d = wcd.drivers()
    by_region, _ = wcw.census_weights(group_of=region_namer())
    keys = list(zip((d["east"] // 1000).astype(int).tolist(),
                    (d["north"] // 1000).astype(int).tolist()))
    index = {k: i for i, k in enumerate(keys)}

    def spread(rows, w) -> dict:
        entry = {}
        for name in named:
            v = d[name][rows]
            mean = float(np.average(v, weights=w))
            entry[name] = {
                "household_mean": round(mean, 3),
                "household_sd": round(float(np.sqrt(np.average((v - mean) ** 2, weights=w))), 3),
                "min": round(float(v.min()), 3), "max": round(float(v.max()), 3)}
        return entry

    out: dict[str, dict] = {}
    all_rows: list[int] = []
    all_w: list[float] = []
    for region, cells in sorted(by_region.items()):
        idx = [(index[c], w) for c, w in cells.items() if c in index]
        if not idx:
            continue
        rows = np.array([i for i, _ in idx])
        w = np.array([x for _, x in idx])
        all_rows.extend(rows.tolist())
        all_w.extend(w.tolist())
        out[region] = {"cells": len(rows), "households": round(float(w.sum())), **spread(rows, w)}
    out["ENGLAND_AND_WALES"] = {
        "cells": len(all_rows), "households": round(sum(all_w)),
        **spread(np.array(all_rows), np.array(all_w))}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pull", action="store_true", help="pull the ONSPD output-area/region lookup")
    ap.add_argument("--build", action="store_true", help="write the committed frame + manifest")
    ap.add_argument("--measure", action="store_true", help="what the frame buys over a centroid")
    args = ap.parse_args(argv)
    if args.pull:
        pull_oa_regions()
    if args.build:
        print(json.dumps(build(), indent=2))
    if args.measure:
        print(json.dumps(measurement(), indent=2))
    if not (args.pull or args.build or args.measure):
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover - command line
    raise SystemExit(main())
