"""sim/profile_class_2.py -- the PC2 (domestic Economy 7) table, and that it is the published one.

Provenance: docs/data-sources/profile-class-2.md.
"""

import hashlib
from datetime import date, timedelta
from pathlib import Path

from sim.profile_class_1 import load_pc1_shape
from sim.profile_class_2 import CSV_PATH, load_pc2_shape

#: SHA-256 of UKERC's ProfileClass2.csv as fetched on 2026-10-22. The table is a published record, so
#: any edit to it is a defect, and this is the check that fires.
_UKERC_SHA256 = "08457653933eee376c619489358e837c71f8301abcdd36555eba8c4c1359e60b"


def _overnight_share(loader, year=2019):
    total = night = 0.0
    d = date(year, 1, 1)
    while d.year == year:
        s = loader(d)
        total += sum(s)
        night += sum(s[:14])
        d += timedelta(days=1)
    return night / total


def test_the_table_is_ukercs_file_byte_for_byte():
    assert hashlib.sha256(Path(CSV_PATH).read_bytes()).hexdigest() == _UKERC_SHA256


def test_a_day_is_48_non_negative_half_hours():
    shape = load_pc2_shape("2016-01-04")
    assert len(shape) == 48 and all(v >= 0 for v in shape)


def test_the_loader_reads_pc2_and_not_pc1():
    """The two tables share a layout and a calendar, so a loader pointed at the wrong file would pass
    every structural check. Only the night share tells them apart: 44.5% against 15.2% in 2019."""
    pc2, pc1 = _overnight_share(load_pc2_shape), _overnight_share(load_pc1_shape)
    assert 0.40 < pc2 < 0.50
    assert 0.13 < pc1 < 0.17
