"""Historical gas price data ingestion — TTF proxy, used in place of UK NBP.

ACCEPTED PROXY FOR PHASE 2B: source is FRED PNGASEUUSDM (IMF "Global price of
Natural Gas, Europe"), monthly in USD/MMBtu. Downloaded via wget. This series
is based on the Dutch TTF hub — the continental European benchmark — NOT the
UK NBP. NBP and TTF are distinct trading points that move closely together
but are not identical. The original primary source (NGT MIPI API at
data.nationalgas.com PUBOB603, true UK NBP SAP) requires OAuth login for
downloads as of 2026, so this TTF-derived series is used as a proxy. See
docs/data-sources/gas-nbp.md for the full provenance discussion.

Resolution: monthly only, expanded to one repeated value per calendar day.
This is coarser than the half-hourly Elexon SSP data used for electricity —
accepted for Phase 2b given gas retail billing is monthly-cycle anyway.

Historical Ground Truth: real IMF/TTF-sourced market prices only; no invented
data.

Output schema (matches SSP schema for compatibility with forward_curve.py):
  settlementDate: YYYY-MM-DD
  systemSellPrice: float, £/MWh

Unit conversion:
  USD/MMBtu × (1/GBPUSD) / 0.29307_MWh_per_MMBtu = £/MWh
  Fixed GBPUSD = 1.28 (reasonable multi-year average for 2016-2025).
"""

import csv
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, timedelta

FRED_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv"
    "?id=PNGASEUUSDM&cosd=2015-01-01&coed=2025-07-01"
)
OUTPUT_PATH = "sim/gas_data/nbp_sap.csv"

GBPUSD = 1.28
# 1 MMBtu (International Table Btu, 1,055.05585 J) is 0.293071 MWh: NIST SP 811 Appendix B,
# https://www.nist.gov/pml/special-publication-811
MWH_PER_MMBTU = 0.29307

#: The first day of the daily record. NOT the simulation's start (2016-01-01): a contract struck on
#: that day prices off the 90 days BEFORE it (`sim.forward_curve.generate_forward_price`'s default
#: lookback), and a record starting on the day itself left a day-one gas founder with an empty
#: window and a ValueError (2026-10-06, the 4,000-founder scale measurement). The same FRED series
#: publishes those months, so the record reaches back to the first whole month the lookback
#: touches -- real history, not a fill. Electricity has the same need and its record CANNOT meet
#: it: see `sim.system_prices_history.RECORD_START`.
RECORD_START = "2015-10-01"
RECORD_END = "2025-06-07"
#: None: the record reaches a full lookback before the founders' first day, so nothing is short.
#: `sim.forward_curve.short_first_term_lookbacks` refuses a short first term on a record with no reason.
SHORT_RECORD_REASON: str | None = None


def fetch_fred_csv() -> str:
    """Download FRED CSV via wget. Returns raw CSV text."""
    result = subprocess.run(
        ["wget", "-q", "--timeout=30", "--tries=2", "-O", "-", FRED_URL],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"wget failed (rc={result.returncode}): {result.stderr}")
    return result.stdout


def parse_fred_csv(raw_csv: str) -> dict[str, float]:
    """Parse FRED CSV into {YYYY-MM: price_gbp_mwh}."""
    prices = {}
    for line in raw_csv.strip().splitlines()[1:]:  # skip header
        parts = line.split(",")
        if len(parts) < 2:
            continue
        obs_date, value_str = parts[0].strip(), parts[1].strip()
        try:
            usd_mmbtu = float(value_str)
        except ValueError:
            continue
        gbp_mwh = usd_mmbtu / (GBPUSD * MWH_PER_MMBTU)
        year_month = obs_date[:7]  # YYYY-MM
        prices[year_month] = round(gbp_mwh, 4)
    return prices


def expand_to_daily(
    monthly_prices: dict[str, float],
    start_date: str,
    end_date: str,
) -> list[dict]:
    """Expand monthly prices to one record per calendar day."""
    records = []
    current = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    while current <= end:
        ym = current.strftime("%Y-%m")
        price = monthly_prices.get(ym)
        if price is not None:
            records.append(
                {"settlementDate": current.isoformat(), "systemSellPrice": price}
            )
        current += timedelta(days=1)

    return records


def write_csv(records: list[dict], path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["settlementDate", "systemSellPrice"])
        writer.writeheader()
        writer.writerows(records)


def load_nbp_history(path: str = OUTPUT_PATH) -> list[dict]:
    """Load NBP SAP history from CSV. Returns list of {settlementDate, systemSellPrice}."""
    records = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            records.append(
                {
                    "settlementDate": row["settlementDate"],
                    "systemSellPrice": float(row["systemSellPrice"]),
                }
            )
    return records


# ------------------------------------------------------------------ the DAILY GB gas price (SAP)
# National Gas Transmission's System Average Price, actual day, republished by ONS under the Open
# Government Licence v3 as part of its real-time indicators ("System Average Price (SAP) of gas",
# workbook table "1.Daily SAP Gas", p/kWh, coverage Jan 2018 onwards). This is the daily series
# PUBOB603 names, reached without the MIPI portal's OAuth login. It is a SEPARATE record from
# `nbp_sap.csv` (the monthly TTF proxy above), which the world's forward curve still reads; this one
# exists so an instrument can see within-month gas price shape. It starts on 2018-01-01, so it
# cannot replace the monthly proxy for the world's 2015-10 lookback.
ONS_SAP_PAGE = (
    "https://www.ons.gov.uk/economy/economicoutputandproductivity/output/datasets/"
    "systemaveragepricesapofgas"
)
#: The edition ingested (published 12 Nov 2026). Pinned so the record is reproducible byte for byte.
ONS_SAP_XLSX_URL = (
    "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/"
    "systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset121126.xlsx"
)
ONS_SAP_XLSX_SHA256 = "fd2edff11ad6fe6176683b71827f033598399db80e186118385d2a0595029bcc"
SAP_DAILY_PATH = "sim/gas_data/sap_daily.csv"
#: The record is clipped to the world's historical window: the ONS table runs past 2025, and
#: nothing after the record's end may enter the world.
SAP_DAILY_START = "2018-01-01"
SAP_DAILY_END = "2025-12-31"

_XL = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_XL_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_SAP_SHEET = "1.Daily SAP Gas"


def _xlsx_sheet_rows(data: bytes, sheet_name: str) -> list[list[str | None]]:
    """Cell values of one worksheet, row by row, read with the standard library only."""
    import io

    z = zipfile.ZipFile(io.BytesIO(data))
    shared: list[str] = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{_XL}si"):
            shared.append("".join(t.text or "" for t in si.iter(f"{_XL}t")))
    rid = next(s.get(f"{_XL_REL}id") for s in ET.fromstring(z.read("xl/workbook.xml")).iter(f"{_XL}sheet")
               if s.get("name") == sheet_name)
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = next(r.get("Target") for r in rels if r.get("Id") == rid).lstrip("/")
    target = target if target.startswith("xl/") else "xl/" + target
    rows = []
    for r in ET.fromstring(z.read(target)).iter(f"{_XL}row"):
        vals = []
        for c in r.findall(f"{_XL}c"):
            v = c.find(f"{_XL}v")
            x = None if v is None else v.text
            if x is not None and c.get("t") == "s":
                x = shared[int(x)]
            vals.append(x)
        rows.append(vals)
    return rows


def parse_ons_sap_xlsx(data: bytes, start: str = SAP_DAILY_START,
                       end: str = SAP_DAILY_END) -> list[dict]:
    """Daily SAP from the ONS workbook as `{settlementDate, systemAveragePrice}` in £/MWh.

    p/kWh to £/MWh is x10 (100 p per £, 1,000 kWh per MWh). A day ONS marks unavailable ("[x]") is
    left out, never filled: a gap is a gap."""
    lo, hi = date.fromisoformat(start), date.fromisoformat(end)
    out = []
    for row in _xlsx_sheet_rows(data, _SAP_SHEET):
        if len(row) < 2 or row[0] is None or row[1] is None:
            continue
        try:
            serial, p_kwh = int(float(row[0])), float(row[1])
        except ValueError:
            continue  # header, title, or "[x]"
        d = date(1899, 12, 30) + timedelta(days=serial)  # Excel 1900 date system
        if lo <= d <= hi:
            out.append({"settlementDate": d.isoformat(), "systemAveragePrice": round(p_kwh * 10.0, 4)})
    return out


def load_sap_daily(path: str = SAP_DAILY_PATH) -> dict[date, float]:
    """The daily GB gas price, {gas day: £/MWh}, 2018-01-01 to 2025-12-31."""
    with open(path, newline="") as f:
        return {date.fromisoformat(r["settlementDate"]): float(r["systemAveragePrice"])
                for r in csv.DictReader(f)}


def build_sap_daily(xlsx_path: str, out_path: str = SAP_DAILY_PATH) -> int:
    """Write the daily record from a downloaded ONS workbook; refuses an edition it was not pinned to."""
    import hashlib

    data = open(xlsx_path, "rb").read()
    got = hashlib.sha256(data).hexdigest()
    if got != ONS_SAP_XLSX_SHA256:
        raise ValueError(f"ONS SAP workbook sha256 {got} is not the pinned edition "
                         f"{ONS_SAP_XLSX_SHA256}: re-pin deliberately, do not ingest blind")
    records = parse_ons_sap_xlsx(data)
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["settlementDate", "systemAveragePrice"])
        w.writeheader()
        w.writerows(records)
    return len(records)


if __name__ == "__main__" and sys.argv[1:2] == ["--sap-daily"]:
    # python3 -m sim.gas_prices_history --sap-daily <downloaded workbook>  (fetch: ONS_SAP_XLSX_URL)
    print(f"wrote {build_sap_daily(sys.argv[2])} days to {SAP_DAILY_PATH}")
    sys.exit(0)


if __name__ == "__main__":
    print("Fetching FRED PNGASEUUSDM (TTF gas proxy, USD/MMBtu, monthly)...")
    raw = fetch_fred_csv()
    monthly = parse_fred_csv(raw)
    print(f"  {len(monthly)} monthly records parsed")

    print(f"Expanding to daily ({RECORD_START} → {RECORD_END})...")
    records = expand_to_daily(monthly, RECORD_START, RECORD_END)
    print(f"  {len(records)} daily records generated")

    write_csv(records, OUTPUT_PATH)
    print(f"Written: {OUTPUT_PATH}")

    # Sanity check
    sample_dates = ["2016-01-01", "2022-08-01", "2025-06-01"]
    for d in sample_dates:
        match = next((r for r in records if r["settlementDate"] == d), None)
        if match:
            p = match["systemSellPrice"]
            p_therm = p * 0.29307 / 0.01  # £/MWh → p/therm approx
            print(f"  {d}: £{p:.2f}/MWh  (~{p_therm:.0f} p/therm)")
