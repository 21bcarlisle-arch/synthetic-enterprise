"""Which gas charging area (LDZ) each census output area is in, from Xoserve's postcode list.

The CV a gas bill converts at is its charging area's (R5 of
`docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`), and the ONS region a drawn
household carries is not a charging area: London is NT, SE and EA, Yorkshire is NE and EM, Wales is WS
and WN. A household is sited in an output area (W2_19, `simulation/household_siting.py`), so this joins
the two published records that name an output area's LDZ:

- Xoserve's "Postcode Exit Zone List" (May 2017, created by the network operators): postcode -> LDZ;
- the ONS Postcode Directory already in the census cache (`tools.household_siting_frame`): postcode -> OA.

Each output area takes the LDZ most of its matched postcodes are in, with that share kept beside it.
An output area with no postcode on Xoserve's list (off the gas grid, or a postcode newer than May 2017)
is absent, not guessed.

    python3 -m tools.xoserve_output_area_ldz      # fetch, join, write the lake file
"""

from __future__ import annotations

import collections
import csv
import gzip
import io
import subprocess
import tempfile
import zipfile
from pathlib import Path

URL = "https://www.xoserve.com/media/2008/postcode-exit-zone-list-may-2017.zip"
ONSPD = Path.home() / ".cache/synthetic-enterprise/census/onspd_gb_live_residential.csv"
OUT = Path("data/lake/xoserve_postcode_ldz/output_area_ldz.csv.gz")


def _postcode_ldz(zip_path: Path) -> dict[str, str]:
    import openpyxl

    book = zipfile.ZipFile(zip_path)
    wb = openpyxl.load_workbook(io.BytesIO(book.read(book.namelist()[0])), read_only=True)
    out: dict[str, str] = {}
    # One sheet per distribution network (WWU, SGN, NGN, NG); SGN's has a leading "Row" column.
    for ws in wb.worksheets:
        rows = ws.iter_rows(values_only=True)
        col = {str(h).strip(): i for i, h in enumerate(next(rows)) if h}
        for r in rows:
            outcode, incode, ldz = r[col["Outcode"]], r[col["Incode"]], r[col["LDZ"]]
            if outcode and incode and ldz:
                out[f"{outcode}{incode}".replace(" ", "")] = str(ldz).strip()
    return out


def output_area_ldz(postcode_ldz: dict[str, str], onspd: Path) -> list[tuple[str, str, int, float]]:
    """(output_area, modal LDZ, matched postcodes, modal share) for every OA with a matched postcode."""
    per_oa: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    with onspd.open(newline="") as fh:
        for row in csv.DictReader(fh):
            ldz = postcode_ldz.get(row["pcds"].replace(" ", ""))
            if ldz:
                per_oa[row["oa"]][ldz] += 1
    rows = []
    for oa, counts in sorted(per_oa.items()):
        ldz, n = counts.most_common(1)[0]
        total = sum(counts.values())
        rows.append((oa, ldz, total, round(n / total, 4)))
    return rows


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "pcz.zip"
        subprocess.run(["curl", "-sSL", "--max-time", "300", "-o", str(zip_path), URL], check=True)
        rows = output_area_ldz(_postcode_ldz(zip_path), ONSPD)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT, "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["output_area", "ldz", "postcodes", "share"])
        w.writerows(rows)
    print(f"{OUT}: {len(rows)} output areas")


if __name__ == "__main__":
    main()
