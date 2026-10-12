"""`--list` counts the book cells the pull still owes, not only the ones the store never held.

THE DEFECT. On 2026-10-11 `--list` read "0 book cell(s) the store has never held" while 478 of the
book's 600 cells held HadUK temperature and no ERA5 wind, cloud or precipitation. A lane-0 item
named that line as its done-condition, and the strict control on the book
(`test_every_settling_domestic_premise_reads_a_complete_stored_cell`) still named 396 premises
refused for want of complete weather. "Held" and "complete" are different questions.

The count and the fetch list share one predicate (`book_cells_incomplete`), so the number a reader
waits on is the number `--build` drives to zero.
"""
from __future__ import annotations

from tools import build_weather_world as bww

ERA5_ROW = {"date": "2020-01-01", **{f: 1.0 for f in bww.FIELDS}}
TEMPERATURE_ONLY_ROW = {"date": "2020-01-01", **{f: (1.0 if f in bww.LEVELLED else "")
                                                  for f in bww.FIELDS}}
CELLS = {k: {"cell_id": k, "latitude": 52.0, "longitude": -1.0}
         for k in ("COMPLETE", "TEMP_ONLY", "NEVER_HELD")}
HELD = {"COMPLETE": [ERA5_ROW], "TEMP_ONLY": [TEMPERATURE_ONLY_ROW], "LEFT_THE_BOOK": [ERA5_ROW]}


def test_a_temperature_only_cell_and_a_never_held_cell_are_owed_and_a_complete_one_is_not():
    owed = bww.book_cells_incomplete(CELLS, HELD)
    # The partition, in one assertion: both owed shapes are named AND the complete shape is not,
    # so a predicate that answers "everything" or "nothing" is red here.
    assert sorted(owed) == ["NEVER_HELD", "TEMP_ONLY"], owed


def test_list_prints_the_owed_count_when_no_book_cell_is_missing_from_the_store(monkeypatch, capsys):
    """The exact 2026-10-11 shape: every book cell held, one of them temperature-only."""
    cells = {k: v for k, v in CELLS.items() if k != "NEVER_HELD"}
    monkeypatch.setattr(bww, "book_cells", lambda: cells)
    monkeypatch.setattr(bww, "_existing_rows", lambda: (HELD, set(HELD)))
    monkeypatch.setattr(bww, "_stored_geometry", lambda: ({k: {} for k in HELD}, {}))
    assert bww.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "0 book cell(s) the store has never held" in out, out
    assert "BOOK CELLS NOT YET COMPLETE: 1 " in out, out
