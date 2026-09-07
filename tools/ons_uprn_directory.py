"""Every GB address, with its output area and its 1 km cell. The centroid disappears here.

REUSE: tools/ons_uprn_directory.py
CLASS: CUSTOM
INDEX: searched "uprn", "onsud", "address", "output area", "lookup", "gazetteer".
       `tools/os_open_uprn.py` gives an address POINT and no geography, so it can say whether a cell
       holds an address and not which output area the address belongs to -- it stays, because that
       is the independent check that found this defect. `tools/weather_cell_weights.py` is the
       caller. ONSPD maps POSTCODES to output areas, which is the indirection this removes.

WHY THIS EXISTS
---------------
Director console, 2026-09-07:

    "My concern is that postcodes aren't precise enough for this. A postcode covers roughly fifteen
     addresses with one grid reference, and in sparse areas it can span a wide area -- which is
     exactly where the error was, and exactly where the weighting matters most for cell counts.
     So: why not place dwellings directly?"

He was right, and the version he was questioning was **a better approximation of the same
approximation**. It had stopped placing households AT postcode centroids, but the centroid still
chose the candidate cells: each output area's households went to the 3x3 neighbourhood of each of
its postcodes, split by the address count in those cells. Two errors survived that:

  * **20,959 cells that hold an address were unreachable** -- outside every 3x3 window -- holding
    61,351 addresses. Isolated properties, the sparse-rural tail, exactly where he predicted.
  * **94.5% of GB's addresses sat in cells claimed by five or more output areas**, and each claimant
    sized its share by ALL the addresses in the cell, including its neighbours'. Conservation held;
    the shape within an output area did not.

THE ONS UPRN DIRECTORY REMOVES BOTH, because it carries `UPRN, GRIDGB1E, GRIDGB1N, ..., OA21CD` in
one row: every address's grid reference AND its output area, assigned by ONS by point-in-polygon.
So an output area's households can be split across the cells its OWN addresses occupy, in proportion
to how many. No centroid, no window, no cross-area attribution.

AND IT IS NOT EXPENSIVE, which was the other thing he did not believe. Streaming all 41,386,453
addresses out of the zip and reducing them to 690,132 (output area, cell) pairs takes **70 seconds,
once**. The placement itself is then **half a second**. What made the earlier pipeline slow was the
k-means sweep and one accidental per-element function call, never the join.

WHAT THIS STILL DOES NOT DO
---------------------------
An address is not a dwelling. ONSUD carries every addressable property -- masts, substations, barns
-- so it says WHERE things are and not HOW MANY HOUSEHOLDS. The census still supplies the count per
output area and this supplies the shape within it, which is the division of labour the data
actually supports. A cell holding one house and one electricity substation is credited two
addresses' worth of its output area's households, and nothing here can tell them apart.
"""
from __future__ import annotations

import argparse
import collections
import io
import pickle
import sys
import time
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "onsud"
ARCHIVE = CACHE / "ONSUD_DEC_2025.zip"
STORE = CACHE / "oa_cell_addresses.pkl"

#: ONS UPRN Directory, December 2025 (Epoch 123), from the Open Geography Portal. Released every six
#: weeks; the epoch is pinned so a re-pull is a decision rather than a drift.
ITEM_ID = "cf1e4c08e78d48e387bcfab837f4e1d0"
DOWNLOAD = f"https://www.arcgis.com/sharing/rest/content/items/{ITEM_ID}/data"

#: Eleven regional files under `Data/`; the other 24 CSVs in the archive are name-and-code lookups
#: with entirely different schemas. The first build read all 35 and died on a ward-name table.
DATA_PREFIX = "Data/"

#: The December 2025 epoch. A count that moved would move every occupancy figure derived from it.
EXPECTED_ADDRESSES = 41_386_453
ADDRESS_COUNT_TOLERANCE = 0.05


def pull(dest: Path = ARCHIVE, progress=print) -> Path:
    """Fetch the archive. 540 MB, no key, Open Government Licence."""
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DOWNLOAD, timeout=3600) as src, dest.open("wb") as out:
        while chunk := src.read(1 << 22):
            out.write(chunk)
    progress(f"[onsud] {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def build_store(archive: Path = ARCHIVE, dest: Path = STORE, progress=print) -> dict:
    """{(output area, cell_x, cell_y): addresses}, streamed from the zip.

    NEVER UNPACKED. The eleven regional CSVs are about 20 GB unzipped and the only thing wanted
    from them is a 690,132-entry counter -- twenty megabytes. Reading them through the zip is what
    makes this a seventy-second step rather than a disk-management problem.
    """
    if not archive.is_file():
        raise FileNotFoundError(
            f"{archive} -- run `python3 tools/ons_uprn_directory.py --pull` first (540 MB)")
    counts: collections.Counter = collections.Counter()
    rows = unusable = 0
    started = time.time()
    with zipfile.ZipFile(archive) as zf:
        names = sorted(n for n in zf.namelist()
                       if n.startswith(DATA_PREFIX) and n.lower().endswith(".csv"))
        if not names:
            raise ValueError(f"{archive} carries no {DATA_PREFIX} CSVs; the archive has changed")
        for name in names:
            with zf.open(name) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                header = [h.strip('"') for h in text.readline().rstrip("\r\n").split(",")]
                try:
                    ie, ino, ioa = (header.index("GRIDGB1E"), header.index("GRIDGB1N"),
                                    header.index("OA21CD"))
                except ValueError as exc:
                    raise ValueError(f"{name} does not carry the expected columns: {exc}") from None
                for line in text:
                    field = line.rstrip("\r\n").split(",")
                    try:
                        east, north = field[ie].strip('"'), field[ino].strip('"')
                        oa = field[ioa].strip('"')
                        if not east or not north or not oa:
                            unusable += 1
                            continue
                        counts[(oa, int(east) // 1000, int(north) // 1000)] += 1
                    except (ValueError, IndexError):
                        unusable += 1
                        continue
                    rows += 1
            progress(f"[onsud] {name.rsplit('/', 1)[-1]:32s} {rows:,} addresses", flush=True)

    drift = abs(rows - EXPECTED_ADDRESSES) / EXPECTED_ADDRESSES
    if drift > ADDRESS_COUNT_TOLERANCE:
        raise ValueError(
            f"read {rows:,} addresses against an expected {EXPECTED_ADDRESSES:,} ({drift:.1%} out). "
            "Every household placement derived from this would move; refusing rather than absorbing "
            "an epoch that has changed under us.")
    store = dict(counts)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as fh:
        pickle.dump(store, fh, protocol=5)
    progress(f"[onsud] {rows:,} addresses, {unusable:,} unusable, {len(store):,} "
             f"(output area, cell) pairs, {len({k[0] for k in store}):,} output areas "
             f"in {time.time() - started:.0f}s -> {dest}")
    return store


def oa_cell_addresses(dest: Path = STORE) -> dict:
    """{(output area, cell_x, cell_y): addresses}.

    REFUSES ON ABSENCE. Every fallback available here is a postcode centroid in some form, and the
    whole reason this exists is that centroids place households where the addresses are not. A
    silent fallback would restore that invisibly on any machine that had not pulled.
    """
    if not dest.is_file():
        raise FileNotFoundError(
            f"{dest} is absent. Household placement needs every address's output area, and the "
            "alternatives all route through a postcode centroid -- which is the approximation this "
            "replaced. Run `python3 tools/ons_uprn_directory.py --pull --build` (540 MB, OGL).")
    with dest.open("rb") as fh:
        return pickle.load(fh)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pull", action="store_true", help="fetch the 540 MB archive")
    ap.add_argument("--build", action="store_true", help="reduce it to (output area, cell) counts")
    args = ap.parse_args(argv)
    if args.pull:
        pull()
    if args.build:
        build_store()
    if not (args.pull or args.build):
        ap.print_help(sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
