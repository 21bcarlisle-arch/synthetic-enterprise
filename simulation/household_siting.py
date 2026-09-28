"""A coordinate for a drawn household — W2_18, the world side.

REUSE: simulation/household_siting.py
CLASS: CUSTOM
INDEX: searched "coordinate", "lat", "siting", "region", "location". `simulation/weather_cell_
       siting.py` sites a coordinate that already EXISTS in the derived cells and refuses one that
       does not — it is this module's consumer, not its duplicate, and its no-coordinate refusal
       names W2_18 as the remedy. `simulation/adoption_geography.py` carries one lat/lon per GSP
       group as a spatial-correlation centroid, which is a different vocabulary and one point per
       region (see `tools/household_siting_frame` on why a centroid is not a household
       distribution). `simulation/population_draw.py` is the caller. The frame this reads is built
       by `tools/household_siting_frame.py`; the placement, the censuses and the address record are
       all `tools/weather_cell_weights.py`'s and are not repeated.

WHAT IT DOES, AND WHAT IT REFUSES TO DO
---------------------------------------
Given a customer id and the region the curriculum drew for it, return the coordinate of a 1 km cell
drawn from **that region's own household distribution** — the census's households, placed on OS
Open UPRN's address record, carrying the HadUK-Grid normals' own latitude and longitude. A cell with
twice the households is twice as likely. So the drawn coordinate is sourced from where households
actually are, and the within-region spread of the weather drivers survives, which is the entire
reason the derived cells exist.

**Given a region the frame does not cover, it returns None and says why.** That is the placeholder
region `UNKNOWN_SYNTHETIC` in the default draw, and it is not a failure: a region that is not a real
region has no household distribution, and inventing a coordinate for it is the fabrication
`fabric_physics.latitude_for_weather_site` refuses one layer down and
`test_region_is_explicit_placeholder_not_fabricated` protects one layer up. **The coordinate follows
the region and needs no dial of its own**: turn the director's region curriculum on
(`draw_population(draw_region=True)`) and the households are sited; leave it off and they are
honestly unsited.

C-S2 (RNG isolation)
--------------------
The draw uses this module's OWN named substream, keyed on the customer id, so it is
order-independent and cannot shift `population_draw`'s acquisition sequence by a single value. It
deliberately does not reuse `population_draw._cohort_substream`: this module is imported BY that one
and reaching back into it for a private helper would be an import cycle, where the property that
matters — a stream nothing else consumes — is three lines.
"""
from __future__ import annotations

import bisect
import csv
import gzip
import random
from pathlib import Path
from typing import Optional

from simulation.rng_substream import substream

#: The committed frame. Built by `python3 -m tools.household_siting_frame --build`, which needs the
#: census pulls in `~/.cache`; READ here, so a fresh worktree with no cache still sites households.
FRAME_PATH = Path(__file__).resolve().parents[1] / "sim" / "household_siting" / (
    "region_household_frame.csv")

STREAM_NAME = "W2_18_household_siting"

#: W2_19: which output areas each sited cell's households are in. Built by
#: `python3 -m tools.household_siting_frame --build-output-areas` from the address placement, keyed
#: row for row to `FRAME_PATH`.
OUTPUT_AREA_FRAME_PATH = FRAME_PATH.parent / "cell_output_area_frame.csv.gz"

#: Its own stream, so drawing the output area cannot move the cell draw above by a single value:
#: every coordinate in the book is byte-identical to the one it had before areas existed.
OUTPUT_AREA_STREAM_NAME = "W2_19_output_area_in_cell"

_frame_cache: Optional[dict] = None
_frame_cache_path: Optional[Path] = None
_oa_cache: Optional[dict] = None
_oa_cache_path: Optional[Path] = None


def _substream(customer_id: str, base_seed: int, stream: str = STREAM_NAME) -> random.Random:
    """An ISOLATED `random.Random` for one customer's siting draw (C-S2)."""
    return substream(stream, f"{customer_id}", base_seed)


def load_frame(path: Optional[Path] = None) -> dict:
    """{region: (lats, lons, cumulative households)}. Cached per process by path.

    FAIL-CLOSED (R15): a missing or empty frame RAISES. It never falls back to an unweighted or
    centroid draw, because a silent fallback here would put every household in one place per region
    and the output would still look like a coordinate.
    """
    global _frame_cache, _frame_cache_path
    target = Path(path) if path is not None else FRAME_PATH
    if _frame_cache is not None and _frame_cache_path == target:
        return _frame_cache
    if not target.is_file():
        raise FileNotFoundError(
            f"{target} -- the household siting frame is absent. Build it with "
            "`python3 -m tools.household_siting_frame --pull --build` (it needs the census pulls "
            "in ~/.cache/synthetic-enterprise/census).")
    lats: dict[str, list[float]] = {}
    lons: dict[str, list[float]] = {}
    cum: dict[str, list[float]] = {}
    with target.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            region = row["region"]
            if region not in cum:
                lats[region], lons[region], cum[region] = [], [], []
            households = float(row["households"])
            if households <= 0:
                continue
            lats[region].append(float(row["lat"]))
            lons[region].append(float(row["lon"]))
            running = cum[region][-1] if cum[region] else 0.0
            cum[region].append(running + households)
    if not cum:
        raise ValueError(f"{target} holds no cell with households -- an empty frame would site "
                         "every household nowhere and report no error")
    built = {r: (lats[r], lons[r], cum[r]) for r in cum}
    _frame_cache, _frame_cache_path = built, target
    return built


def regions(path: Optional[Path] = None) -> set[str]:
    """The regions the frame can site a household in."""
    return set(load_frame(path))


def siting_refusal(region: str, path: Optional[Path] = None) -> Optional[str]:
    """Why `region` cannot be sited, or None if it can. The refusal NAMES ITS REASON (R15)."""
    covered = load_frame(path)
    if region in covered:
        return None
    return (f"{region!r} is not a region of the household siting frame, so no household "
            f"distribution exists for it and no coordinate can be sourced. The frame covers "
            f"{sorted(covered)}. If this is the draw's placeholder region, that is the correct "
            f"answer and the remedy is the director's region curriculum "
            f"(`draw_population(draw_region=True)`), not a coordinate invented here. If it is a "
            f"real region the curriculum has gained, rebuild the frame: "
            f"`python3 -m tools.household_siting_frame --pull --build` refuses on exactly this "
            f"mismatch")


def coordinate_for_customer(
    customer_id: str,
    base_seed: int,
    region: str,
    path: Optional[Path] = None,
) -> Optional[tuple[float, float]]:
    """(lat, lon) drawn from `region`'s household distribution, or None if it has none.

    Probability-proportional-to-households over the region's 1 km cells, by bisection on the
    cumulative weights rather than a linear scan: a region holds tens of thousands of cells and this
    is called once per drawn household.
    """
    frame = load_frame(path)
    cells = frame.get(region)
    if cells is None:
        return None
    lats, lons, cum = cells
    i = _cell_index(customer_id, base_seed, cum)
    return lats[i], lons[i]


def _cell_index(customer_id: str, base_seed: int, cum: list[float]) -> int:
    """The drawn cell's row in its region. ONE draw, shared by the coordinate and the area."""
    x = _substream(customer_id, base_seed).random() * cum[-1]
    return min(bisect.bisect_left(cum, x), len(cum) - 1)


def load_output_area_frame(path: Optional[Path] = None) -> dict:
    """{(region, lat, lon): (output areas, cumulative households)}. Cached per process by path.

    FAIL-CLOSED like `load_frame`. An absent frame RAISES and does not return an empty map. An
    empty map would give every home no area and a national headcount, and the output would look
    exactly like a book that had never been conditioned.
    """
    global _oa_cache, _oa_cache_path
    target = Path(path) if path is not None else OUTPUT_AREA_FRAME_PATH
    if _oa_cache is not None and _oa_cache_path == target:
        return _oa_cache
    if not target.is_file():
        raise FileNotFoundError(
            f"{target} -- the output-area frame is absent, so no sited home can be given the "
            "output area its headcount prior is keyed on. Build it with "
            "`python3 -m tools.household_siting_frame --build-output-areas`.")
    built: dict[tuple[str, float, float], tuple[list[str], list[float]]] = {}
    with gzip.open(target, mode="rt", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["region"], float(row["lat"]), float(row["lon"]))
            oas, cum = built.setdefault(key, ([], []))
            oas.append(row["output_area"])
            cum.append((cum[-1] if cum else 0.0) + float(row["households"]))
    if not built:
        raise ValueError(f"{target} holds no output area -- an empty frame would leave every "
                         "home unconditioned and report no error")
    _oa_cache, _oa_cache_path = built, target
    return built


def output_area_for_customer(
    customer_id: str,
    base_seed: int,
    region: str,
    path: Optional[Path] = None,
    output_area_path: Optional[Path] = None,
) -> Optional[str]:
    """The 2021 output area of the home `coordinate_for_customer` sited, or None if it sited none.

    The cell is the SAME cell, re-derived from the same stream, so the area always lies in the
    square the coordinate names. Within the cell the area is drawn PPS over each output area's share
    of the cell's households, on its own stream.

    A SITED HOME WITH NO AREA RAISES. None means only "this region has no household distribution",
    the same None `coordinate_for_customer` returns. A cell of the household frame missing from the
    output-area frame means the two frames were built apart, and a home that quietly carried no
    area would take the national headcount without saying so.
    """
    frame = load_frame(path)
    cells = frame.get(region)
    if cells is None:
        return None
    lats, lons, cum = cells
    i = _cell_index(customer_id, base_seed, cum)
    areas = load_output_area_frame(output_area_path).get((region, lats[i], lons[i]))
    if areas is None:
        raise KeyError(
            f"{customer_id}: sited in {region} at ({lats[i]}, {lons[i]}), a cell the output-area "
            f"frame does not carry. The two frames were built from different cells. Rebuild with "
            f"`python3 -m tools.household_siting_frame --build-output-areas`.")
    oas, oa_cum = areas
    x = _substream(customer_id, base_seed, OUTPUT_AREA_STREAM_NAME).random() * oa_cum[-1]
    return oas[min(bisect.bisect_left(oa_cum, x), len(oas) - 1)]
