"""How big the dwelling is, and who lives in it given that: bedrooms from floor area, headcount from bedrooms.

REUSE: tools/dwelling_size_joint.py
CLASS: CUSTOM
INDEX: searched "dwelling size joint", "bedrooms given floor area", "household size by bedrooms".
       `tools/people_physical_layer.py` owns the Census TS017 headcount prior per output area and
       its committed-file pattern is copied here, not re-derived. `tools/need_stock_joint.py` owns
       NEED's six-onto-four property-type fold, which is imported, not restated. Nothing held a
       bedrooms-given-area relation from a source: `premise_population.draw_premise_from_joint`
       inverted an area midpoint at an unsourced 14 m2 per bedroom, and nothing conditioned a
       headcount on bedrooms at all.

THE TWO DEFECTS THIS CLOSES (SEAT_FINDING_THE_3_02_HEADCOUNT_WAS_THE_INSTRUMENTS_NOT_THE_BOOKS)
------------------------------------------------------------------------------------------------
1. Bedrooms came from `round(2 + (area_midpoint - base) / 14)`, clamped to 1..6. On 4,000 drawn
   homes that gave 23% one-bed and 24% six-plus-bed. The real stock (VOA, 31 March 2025) is 16%
   and 1%.
2. Headcount was drawn from the output area's TS017 distribution independently of the dwelling.
   A six-bed home was single as often as a one-bed. Census 2021 RM136 says 74% of one-bed homes
   hold one person, and 11% of 4+-bed homes do.

THE THREE SOURCES, all published, all dated, raw counts committed in `COMMITTED`:

  * **VOA Council Tax: stock of properties, table CTSOP3.0, at 31 March 2025** (published
    22 May 2026). England and Wales: dwellings by Council Tax band x property type x bedrooms
    (1..6+, "Not known" excluded). It gives P(bedrooms | type, band).
  * **DESNZ NEED anonymised 50k sample, 2026** (HMRC-sourced floor-area band and council tax band
    on every row). It gives P(band | type, floor area), which marginalises VOA's table onto the
    floor-area band the fitted joint draws.
  * **ONS Census 2021 RM136, tenure x household size x number of bedrooms**, England and Wales,
    all tenures. It gives P(bedrooms | household size), with size and bedrooms each capped at 4+.

WHAT IS ASSUMED, named rather than discovered later:

  * Bedrooms are independent of floor area GIVEN property type and council tax band. Band is a
    valuation, so it carries size and location together; within a band the area is not used.
  * Bedrooms are independent of the output area GIVEN household size. That is the Bayes step:
    P(size | area, bedrooms) is proportional to P(size | area) x P(bedrooms | size). It holds the
    area's own TS017 distribution as the prior and moves each home along it by its dwelling.
  * The NEED 50k sample is stratified, not population-weighted. Within one (type, floor area)
    cell the council-tax mix is taken as the sample gives it.

THE INDEPENDENT CHECK. EHS 2012 (Floor Space in English Homes, technical report Fig 2.5) publishes
mean usable floor area by bedrooms: 47, 71, 95 and 158 m2 for 1, 2, 3 and 4+. None of the three
sources above contains floor area by bedrooms, so this is an out-of-sample test of the
independence assumption. `ehs_floor_area_check()` prints it.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "dwelling_size"
VOA_ODS = CACHE / "ctsop34.ods"
RM136_CSV = CACHE / "rm136_ew.csv"
NEED_CSV = Path.home() / ".cache" / "synthetic-enterprise" / "need_2026" / "anon2026_50k.csv"
COMMITTED = PROJECT / "sim" / "people" / "dwelling_size_counts.json"

VOA_URL = ("https://assets.publishing.service.gov.uk/media/6a0ee006f71ef78abbd59d69/"
           "2025_CT_SoP_Tables_3_4.ods")
RM136_URL = ("https://www.nomisweb.co.uk/api/v01/dataset/NM_2236_1.data.csv?geography=2092957703"
             "&c2021_hhtenure_5=0&measures=20100&select=c2021_hhsize_6,c2021_hhsize_6_name,"
             "c2021_bedrooms_5,c2021_bedrooms_5_name,obs_value")

#: NEED's property types onto VOA's CTSOP3.0 column groups. Both terraces are VOA's one
#: "Terraced House"; VOA has no end/mid split.
NEED_TO_VOA_TYPE = {
    "Bungalow": "Bungalow", "Flat": "Flat / Maisonette", "End terrace": "Terraced House",
    "Mid terrace": "Terraced House", "Semi detached": "Semi-Detached House",
    "Detached": "Detached House",
}
VOA_BEDROOMS = {"1 Bedroom": 1, "2 Bedrooms": 2, "3 Bedrooms": 3, "4 Bedrooms": 4,
                "5 Bedrooms": 5, "6+ Bedrooms": 6}
#: RM136's codes, read from the dataset's own definition: size 2..5 = 1, 2, 3, 4+ people;
#: bedrooms 1..4 = 1, 2, 3, 4+. Code 0 is the total and size code 1 is "0 people" (all zero).
RM136_SIZE = {"2": 1, "3": 2, "4": 3, "5": 4}
RM136_BEDS = {"1": 1, "2": 2, "3": 3, "4": 4}

#: EHS 2012, Floor Space in English Homes technical report, Fig 2.5, `floory` (new definition).
EHS_2012_MEAN_AREA_BY_BEDROOMS_M2 = {1: 47.0, 2: 70.9, 3: 94.7, 4: 158.4}


def _voa_counts(path: Path = VOA_ODS) -> dict[str, dict[str, dict[int, int]]]:
    """`{voa_type: {council_tax_band: {bedrooms: dwellings}}}` for England and Wales."""
    import pandas as pd

    sheet = pd.read_excel(path, engine="odf", sheet_name="CTSOP3_0", header=None)
    header = [str(c) for c in sheet.iloc[4].tolist()]
    out: dict[str, dict[str, dict[int, int]]] = {}
    for _, row in sheet.iloc[5:].iterrows():
        if row.iloc[0] != "ENGWAL" or row.iloc[4] == "All":
            continue
        band = str(row.iloc[4])
        for col, name in enumerate(header):
            if ":" not in name:
                continue
            voa_type, beds = (part.strip() for part in name.split(":", 1))
            if beds not in VOA_BEDROOMS:
                continue
            value = row.iloc[col]
            count = 0 if str(value) in ("[c]", "nan", "-") else int(value)
            out.setdefault(voa_type, {}).setdefault(band, {})[VOA_BEDROOMS[beds]] = count
    if sorted(out) != sorted(set(NEED_TO_VOA_TYPE.values())):
        raise ValueError(f"CTSOP3.0 property types {sorted(out)} are not the five this maps")
    return out


def _rm136_counts(path: Path = RM136_CSV) -> dict[int, dict[int, int]]:
    """`{household_size_cell: {bedrooms_cell: households}}`, both cells 1..4 with 4 meaning 4+."""
    out: dict[int, dict[int, int]] = {}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            size, beds = row["C2021_HHSIZE_6"], row["C2021_BEDROOMS_5"]
            if size in RM136_SIZE and beds in RM136_BEDS:
                out.setdefault(RM136_SIZE[size], {})[RM136_BEDS[beds]] = int(row["OBS_VALUE"])
    if sum(sum(c.values()) for c in out.values()) < 24_000_000:
        raise ValueError("RM136 holds fewer than the 24.8m England and Wales households")
    return out


def _need_counts(path: Path = NEED_CSV) -> dict[str, int]:
    """`{"<NEED type>|<floor area band>|<council tax band>": rows}` from the NEED 50k sample."""
    out: dict[str, int] = {}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = f"{row['PROP_TYPE']}|{row['FLOOR_AREA_BAND']}|{row['COUNCIL_TAX_BAND']}"
            out[key] = out.get(key, 0) + 1
    return out


def commit_counts(dest: Path = COMMITTED, progress=print) -> dict:
    """Write the three sources' raw counts to the committed file the world reads."""
    payload = {
        "sources": {
            "voa_ctsop30": f"VOA Council Tax stock of properties CTSOP3.0, England and Wales, "
                           f"at 2025-03-31, published 2026-05-22: {VOA_URL}",
            "need_type_area_band": "DESNZ NEED anonymised 50k sample anon2026_50k.csv, "
                                   "published 2026-06-11: PROP_TYPE|FLOOR_AREA_BAND|"
                                   "COUNCIL_TAX_BAND row counts",
            "rm136": f"ONS Census 2021 RM136, all tenures, England and Wales: {RM136_URL}",
        },
        "voa_ctsop30": _voa_counts(),
        "need_type_area_band": dict(sorted(_need_counts().items())),
        "rm136": _rm136_counts(),
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    progress(f"[dwelling-size] committed counts -> {dest}")
    return payload


_cache: dict | None = None


def committed_counts(path: Path | None = None) -> dict:
    """The committed counts. RAISES when absent: no file is never "no conditioning"."""
    global _cache
    if path is None and _cache is not None:
        return _cache
    src = COMMITTED if path is None else path
    if not src.is_file():
        raise FileNotFoundError(
            f"{src} is absent. It holds the VOA, NEED and RM136 counts the world draws bedrooms "
            "and headcount from; rebuild it with `python3 tools/dwelling_size_joint.py --commit`.")
    data = json.loads(src.read_text(encoding="utf-8"))
    if path is None:
        _cache = data
    return data


def bedrooms_given_dwelling(counts: dict | None = None) -> dict[tuple[str, str], dict[int, float]]:
    """P(bedrooms | world property type, NEED floor-area band), bedrooms 1..6 (6 = 6+).

    Each NEED row contributes VOA's P(bedrooms | its own type, its own council tax band), so a
    bungalow folded into DETACHED carries a bungalow's bedrooms, not a detached house's.
    """
    from tools.need_stock_joint import PROPERTY_TYPE

    counts = committed_counts() if counts is None else counts
    voa = counts["voa_ctsop30"]
    acc: dict[tuple[str, str], dict[int, float]] = {}
    for key, rows in counts["need_type_area_band"].items():
        need_type, area, band = key.split("|")
        by_beds = voa[NEED_TO_VOA_TYPE[need_type]].get(band)
        total = sum(by_beds.values()) if by_beds else 0
        if not total:
            continue
        cell = acc.setdefault((PROPERTY_TYPE[need_type], area), {})
        for beds, n in by_beds.items():
            cell[int(beds)] = cell.get(int(beds), 0.0) + rows * n / total
    return {k: {b: v / sum(c.values()) for b, v in sorted(c.items())} for k, c in acc.items()}


def bedrooms_likelihood_by_size(counts: dict | None = None) -> dict[int, dict[int, float]]:
    """P(bedrooms cell | household size cell) from RM136, both cells 1..4 (4 = 4+)."""
    counts = committed_counts() if counts is None else counts
    out: dict[int, dict[int, float]] = {}
    for size, by_beds in counts["rm136"].items():
        total = sum(by_beds.values())
        out[int(size)] = {int(b): n / total for b, n in by_beds.items()}
    return out


def condition_sizes_on_bedrooms(size_counts: dict[int, float], bedrooms: int,
                                counts: dict | None = None) -> dict[int, float]:
    """An area's TS017 size distribution, moved by this dwelling's bedrooms (Bayes, RM136)."""
    likelihood = bedrooms_likelihood_by_size(counts)
    beds_cell = max(1, min(4, int(bedrooms)))
    return {size: n * likelihood[max(1, min(4, int(size)))][beds_cell]
            for size, n in size_counts.items()}


def ehs_floor_area_check(counts: dict | None = None) -> dict[int, tuple[float, float]]:
    """`{bedrooms cell: (derived mean area m2, EHS 2012 mean m2)}` over the NEED rows."""
    from tools.demand_case_coverage import AREA_MIDPOINT

    counts = committed_counts() if counts is None else counts
    joint = bedrooms_given_dwelling(counts)
    rows_by_cell: dict[tuple[str, str], int] = {}
    from tools.need_stock_joint import PROPERTY_TYPE
    for key, rows in counts["need_type_area_band"].items():
        need_type, area, _ = key.split("|")
        cell = (PROPERTY_TYPE[need_type], area)
        rows_by_cell[cell] = rows_by_cell.get(cell, 0) + rows
    num: dict[int, float] = {}
    den: dict[int, float] = {}
    for cell, p_beds in joint.items():
        for beds, p in p_beds.items():
            b = min(4, beds)
            w = rows_by_cell[cell] * p
            num[b] = num.get(b, 0.0) + w * AREA_MIDPOINT[cell[1]]
            den[b] = den.get(b, 0.0) + w
    return {b: (num[b] / den[b], EHS_2012_MEAN_AREA_BY_BEDROOMS_M2[b]) for b in sorted(num)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--commit", action="store_true", help="rewrite the committed counts")
    args = ap.parse_args(argv)
    if args.commit:
        commit_counts()
    for (ptype, area), p in sorted(bedrooms_given_dwelling().items()):
        print(f"{ptype:14s} area {area}: " + " ".join(f"{b}:{v:.2f}" for b, v in p.items()))
    for b, (derived, ehs) in ehs_floor_area_check().items():
        print(f"bedrooms {b}{'+' if b == 4 else ' '}  derived mean area {derived:6.1f} m2  "
              f"EHS 2012 {ehs:6.1f} m2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
