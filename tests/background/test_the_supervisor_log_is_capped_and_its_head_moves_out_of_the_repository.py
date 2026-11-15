"""The defect: `supervisor.log()` appended to `docs/observability/supervisor-log.md` with nothing
trimming it -- 694 MB in the working tree on 15 Nov 2026, read by every tree scan.

A write past the cap must leave the live file under the cap, move the head out to the archive
directory, and keep the newest entries whole. The control first: the rotation CAN fire, so a cap
that never rotates (or a check that never trips) cannot pass these as "nothing to do".
"""

from __future__ import annotations

import re

import pytest


@pytest.fixture
def capped(tmp_path, monkeypatch):
    from background import supervisor as sup

    monkeypatch.setattr(sup, "LOG_FILE", tmp_path / "tree" / "supervisor-log.md")
    monkeypatch.setattr(sup, "LOG_ARCHIVE_DIR", tmp_path / "outside")
    monkeypatch.setattr(sup, "LOG_CAP_BYTES", 4_000)
    monkeypatch.setattr(sup, "LOG_KEEP_BYTES", 1_000)
    return sup


def _write(sup, n):
    for i in range(n):
        sup.log(f"entry {i:04d} " + "x" * 60)


def test_a_write_past_the_cap_rotates_and_leaves_the_live_file_under_it(capped):
    sup = capped
    _write(sup, 200)  # ~16 KB written against a 4 KB cap

    archives = list(sup.LOG_ARCHIVE_DIR.glob("supervisor-log_*.md"))
    assert archives, "the cap never rotated -- the branch that exists to be taken was not taken"
    assert sup.LOG_FILE.stat().st_size <= sup.LOG_CAP_BYTES

    live = sup.LOG_FILE.read_text()
    assert "entry 0199" in live, "the newest entry must stay in the tree"
    assert "entry 0000" not in live, "the head must have moved out"
    assert "Log capped: older entries are in" in live
    # Every kept line is a whole entry: the cut lands on an entry boundary, never mid-line.
    whole = re.compile(r"^- \[[^\]]+\] (entry \d{4} x{60}|Log capped: older entries are in \S+\.md)$")
    for line in live.strip().splitlines():
        assert whole.match(line), line


def test_nothing_is_lost_across_the_rotation(capped):
    sup = capped
    _write(sup, 200)
    archives = list(sup.LOG_ARCHIVE_DIR.glob("*.md"))
    assert archives, "no archive written: an empty scan would call a log that never rotated lossless"
    text = "".join(p.read_text() for p in archives) + sup.LOG_FILE.read_text()
    for i in range(200):
        assert f"entry {i:04d} " in text, i


def test_under_the_cap_nothing_moves(capped):
    sup = capped
    _write(sup, 5)
    assert not sup.LOG_ARCHIVE_DIR.exists()
    assert "entry 0000" in sup.LOG_FILE.read_text()
