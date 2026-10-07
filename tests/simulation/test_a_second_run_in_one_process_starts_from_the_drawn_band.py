"""A second phase-2b run in one process starts from the book import drew, not the last run's.

Defect this catches (H50, 2026-10-07): `run_phase2b.main` writes a fabric premise's own-reads
registry EAC into the shared roster dicts and `EFFECTIVE_EAC_KWH`, and appends its wins to
`ACQUIRED_CUSTOMERS`. Nothing put them back, so the A/B's second arm started on the first arm's
book, and `test_c1_eac_calibrated_to_ofgem_tdcv_medium` read 1604.4 for a drawn 2500 after an
earlier test ran `main`. Delete the `start_from_the_drawn_book()` call at the top of `_main` and
the last assertion here reds.
"""
from __future__ import annotations

import pytest

import simulation.run_phase2b as p2b

# The shortest window that holds a year of reads, so the rewrite branch is taken, not skipped.
_A_YEAR_OF_READS = "2017-02-28"


class _RunStarted(Exception):
    pass


def _the_book_a_run_starts_from(monkeypatch) -> dict:
    """Start a run, read the book at its first step, and stop it there."""
    seen = {}

    def stop(report_end):
        seen["eac"] = {c["customer_id"]: c["eac_kwh"]
                       for c in p2b.ELEC_CUSTOMERS + p2b.SUCCESSOR_ELEC_CUSTOMERS}
        seen["effective"] = dict(p2b.EFFECTIVE_EAC_KWH)
        seen["acquired"] = [c["customer_id"] for c in p2b.ACQUIRED_CUSTOMERS]
        raise _RunStarted

    with monkeypatch.context() as m:
        m.setattr(p2b, "effective_report_end", stop)
        with pytest.raises(_RunStarted):
            p2b.main(report_end=_A_YEAR_OF_READS)
    return seen


def test_a_second_run_starts_from_the_book_the_first_started_from(monkeypatch):
    first = _the_book_a_run_starts_from(monkeypatch)
    p2b.main(report_end=_A_YEAR_OF_READS)
    left = {c["customer_id"]: c["eac_kwh"] for c in p2b.ELEC_CUSTOMERS + p2b.SUCCESSOR_ELEC_CUSTOMERS}
    rewritten = [cid for cid in left if left[cid] != first["eac"][cid]]
    # The run must have written into the book, or the comparison below is equal for free.
    assert rewritten, "the run rewrote no registry EAC: this control would compare an untouched book"
    second = _the_book_a_run_starts_from(monkeypatch)
    assert second == first, (
        f"the second run started on the first run's book: {len(rewritten)} rewritten EAC(s), "
        f"e.g. {[(cid, first['eac'][cid], second['eac'][cid]) for cid in rewritten[:3]]}; "
        f"acquired {second['acquired'][:3]}")
