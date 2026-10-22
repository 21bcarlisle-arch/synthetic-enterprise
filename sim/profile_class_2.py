"""Profile Class 2 (domestic Economy 7) half-hourly consumption shape.

The values in sim/data/profile_class_2_gad.csv are UKERC's `ProfileClass2.csv`, verbatim: the 1997
Group Average Demand table from the same archive, and in the same layout, as PC1's. Provenance and
what decides a home's registration on PC2: docs/data-sources/profile-class-2.md.

The season and day-type calendar is the BSC's own and is class-agnostic, so this reads PC1's.
"""

from pathlib import Path

from sim.profile_class_1 import load_pc1_shape

# Anchored to this file, for the reason sim/profile_class_1.py gives.
CSV_PATH = str(Path(__file__).resolve().parent / "data" / "profile_class_2_gad.csv")


def load_pc2_shape(target_date, csv_path: str = CSV_PATH) -> list[float]:
    """48 half-hourly kWh for an average PC2 customer on target_date, settlement period 1 first."""
    return load_pc1_shape(target_date, csv_path)


if __name__ == "__main__":
    shape = load_pc2_shape("2016-01-04")
    print(f"2016-01-04: {len(shape)} periods, daily total = {sum(shape):.2f} kWh, "
          f"00:00-07:00 share = {sum(shape[:14]) / sum(shape):.1%}")
