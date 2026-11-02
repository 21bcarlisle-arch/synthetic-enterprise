"""National Gas's published daily calorific value per charging area (LDZ), as the record holds it.

G1 of `docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`. The bytes are
`data/lake/national_gas_ldz_cv/ldz_daily_cv.csv.gz` (fetched by `tools.fetch_national_gas_ldz_cv`;
provenance beside it). The world reads them here and hands the supplier what was published by a
given moment, as a real supplier receives it; the company never opens the file (W6).

Two readings of one gas day, and they differ on purpose:
- `published_cv(ldz, gas_day, as_of)`: the latest version published by `as_of`, which is all a
  supplier could have used. None before the first publication.
- `final_cv(ldz, gas_day)`: the last version on the record, which is the world's best reading of
  the gas that actually flowed.

The portal serves the series from gas day 1 Nov 2021 (`FIRST_GAS_DAY`). Before that both return
None: 2016 to Oct 2021 is a GAP, not a value to fill.

`ldz_for_output_area(oa)` says which charging area a sited household is in, from Xoserve's
postcode list joined to the census output areas (`data/lake/xoserve_postcode_ldz/`). The ONS region
is not the answer: London is NT, SE and EA, Yorkshire NE and EM, Wales WS and WN.
"""

from __future__ import annotations

import bisect
import csv
import gzip
from functools import lru_cache
from pathlib import Path

LAKE_FILE = Path(__file__).resolve().parent.parent / "data/lake/national_gas_ldz_cv/ldz_daily_cv.csv.gz"
#: The first gas day the portal's LDZ CV items serve; an earlier window returns an empty body.
FIRST_GAS_DAY = "2021-11-01"
CHARGING_AREAS = ("EA", "EM", "NE", "NO", "NT", "NW", "SC", "SE", "SO", "SW", "WM", "WN", "WS")
OUTPUT_AREA_LDZ_FILE = LAKE_FILE.parent.parent / "xoserve_postcode_ldz/output_area_ldz.csv.gz"


@lru_cache(maxsize=1)
def _versions() -> dict[tuple[str, str], tuple[list[str], list[float]]]:
    """(ldz, gas_day) -> (publication times ascending, values in that order)."""
    out: dict[tuple[str, str], tuple[list[str], list[float]]] = {}
    with gzip.open(LAKE_FILE, "rt", newline="") as fh:
        for row in sorted(csv.DictReader(fh), key=lambda r: r["published_at"]):
            times, values = out.setdefault((row["ldz"], row["gas_day"]), ([], []))
            times.append(row["published_at"])
            values.append(float(row["cv_mj_per_m3"]))
    return out


def published_cv(ldz: str, gas_day: str, as_of: str) -> float | None:
    """The CV for `gas_day` in `ldz` as last published at or before `as_of` (ISO date or datetime)."""
    entry = _versions().get((ldz, gas_day))
    if entry is None:
        return None
    times, values = entry
    # A bare date means the end of that day.
    bound = as_of if "T" in as_of else f"{as_of}T23:59:59"
    i = bisect.bisect_right(times, bound)
    return values[i - 1] if i else None


def final_cv(ldz: str, gas_day: str) -> float | None:
    """The last version of the gas day's CV on the record."""
    entry = _versions().get((ldz, gas_day))
    return entry[1][-1] if entry else None


@lru_cache(maxsize=1)
def _output_area_ldz() -> dict[str, str]:
    with gzip.open(OUTPUT_AREA_LDZ_FILE, "rt", newline="") as fh:
        return {row["output_area"]: row["ldz"] for row in csv.DictReader(fh)}


def ldz_for_output_area(output_area: str | None) -> str | None:
    """The LDZ most of the output area's gas postcodes are in, or None where the list names none.

    None is an output area with no postcode on Xoserve's list (mostly off the gas grid). The five
    independent networks (LC, LO, LS, LT, LW) come back as their own codes, which are not in
    `CHARGING_AREAS` and have no published CV."""
    return _output_area_ldz().get(output_area) if output_area else None


class PublishedCalorificValues:
    """The supplier's CV feed in the simulation: what National Gas had published by `as_of`.

    Satisfies `company.billing.gas_volume_conversion.CalorificValueFeed`."""

    def published_cv(self, ldz: str, gas_day: str, as_of: str) -> float | None:
        return published_cv(ldz, gas_day, as_of)
