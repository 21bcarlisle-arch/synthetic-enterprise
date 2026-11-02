"""Fetch National Gas's published daily calorific value per charging area (LDZ) into the lake.

G1 of `docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`: the CV a gas bill
must use is the billing period's average of these daily values (R5). The harness fetches; the bytes
become a file in `data/lake/national_gas_ldz_cv/`, never a runtime fetch by the company (W6).

The portal's find-gas-data download serves these items from gas day 1 Nov 2021 only. A request for an
earlier window returns an empty body, so 2016 to Oct 2021 stays a GAP named in the lake's PROVENANCE.

Every published VERSION is kept, with its publication time ("Applicable At"). A gas day's CV is
published on the day itself and again at about 10:30 the day after, and a few are revised months
later (LDZ(NO), 9-11 Aug 2022, republished as 36.0 on 7 Apr 2023). A supplier billing in Sep 2022
could not have seen that revision, so a reader takes the latest version published by its as-of.

    python3 -m tools.fetch_national_gas_ldz_cv            # fetch and write the tidy, gzipped CSV
"""

from __future__ import annotations

import csv
import gzip
import io
import subprocess
from datetime import date, datetime
from pathlib import Path

URL = "https://data.nationalgas.com/api/find-gas-data-download"
#: The 13 charging areas and their publication-object ids, as the portal's own folder list names them.
LDZ_IDS = {"EA": "PUBOB4507", "EM": "PUBOB4508", "NO": "PUBOB4509", "NE": "PUBOB4510",
           "NT": "PUBOB4511", "NW": "PUBOB4512", "SC": "PUBOB4513", "SE": "PUBOB4514",
           "SO": "PUBOB4515", "SW": "PUBOB4516", "WM": "PUBOB4517", "WN": "PUBOB4518",
           "WS": "PUBOB4519"}
OUT = Path("data/lake/national_gas_ldz_cv/ldz_daily_cv.csv.gz")


def _fetch_year(pub_id: str, year: int) -> str:
    query = (f"applicableFor=Y&dateFrom={year}-01-01&dateTo={year + 1}-01-01&dateType=GASDAY"
             f"&latestFlag=N&ids={pub_id}&type=CSV")
    return subprocess.run(["curl", "-s", "--max-time", "120", f"{URL}?{query}"],
                          check=True, capture_output=True, text=True).stdout


def _iso(day_month_year: str) -> str:
    return datetime.strptime(day_month_year, "%d/%m/%Y").date().isoformat()


def _iso_time(stamp: str) -> str:
    return datetime.strptime(stamp, "%d/%m/%Y %H:%M:%S").isoformat()


def fetch(last_gas_day: date = date(2025, 12, 31)) -> list[dict]:
    rows: dict[tuple[str, str, str], dict] = {}
    for ldz, pub_id in LDZ_IDS.items():
        for year in range(2016, last_gas_day.year + 1):
            for rec in csv.DictReader(io.StringIO(_fetch_year(pub_id, year))):
                gas_day = _iso(rec["Applicable For"])
                if gas_day > last_gas_day.isoformat():
                    continue
                published_at = _iso_time(rec["Applicable At"])
                rows[(ldz, gas_day, published_at)] = {"ldz": ldz, "gas_day": gas_day,
                                        "cv_mj_per_m3": float(rec["Value"]),
                                        "published_at": published_at}
    return [rows[k] for k in sorted(rows)]


def main() -> None:
    rows = fetch()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT, "wt", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["ldz", "gas_day", "cv_mj_per_m3", "published_at"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} published LDZ-day versions written to {OUT}")


if __name__ == "__main__":
    main()
