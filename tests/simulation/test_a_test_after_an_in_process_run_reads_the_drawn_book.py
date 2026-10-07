"""A test that runs after an in-process `run_phase2b.main` reads the book import drew (H50 L2).

Defects this catches (2026-10-07):

* `main` leaves its registry-EAC rewrite and its wins in module-level book state, by design (phase
  4c reads the rewrite after it returns). A test that reads the roster after another test ran
  `main` saw that run's book: H40's `test_c1_eac_calibrated_to_ofgem_tdcv_medium` read 1604.4 for
  a drawn 2500, and `test_c4_solar_reduces_multiplier` red with it, in census order. Delete
  `_phase2b_book_is_put_back` from tests/conftest.py and the pair below reds.
* `start_from_the_drawn_book` clears `ACQUIRED_CUSTOMERS`, and no control could see it: no
  in-process window short enough for a test wins one (0 to 2017-02-28 and 0 to 2017-12-31, read
  2026-10-07; wins come only from a home-move churn the company goes to market for). The seed
  below is the record a win appends, built by the same function. Delete the `.clear()` and the
  last test reds.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import simulation.run_phase2b as p2b

ROOT = Path(__file__).resolve().parents[2]

# The two accounts H40's reds read, each moved off its drawn EAC (2500, 5500). C1's is the 1604.4
# H40 saw; C4's only has to differ from 5500, which is all a rewrite does to the reader.
_WHAT_MAIN_WROTE = {"C1": 1604.4, "C4": 2750.0}

_H40_REDS = [
    "tests/saas/test_customers.py::test_c1_eac_calibrated_to_ofgem_tdcv_medium",
    "tests/simulation/test_phase_c_household_demand.py::"
    "TestEACMultiplierComposite::test_c4_solar_reduces_multiplier",
]


def _record(cid):
    return next(c for c in p2b.ELEC_CUSTOMERS if c["customer_id"] == cid)


def test_a_run_leaves_its_rewrite_and_its_wins_in_the_book():
    """The writer half of the pair: the writes `main` makes, made directly, and left in place."""
    for cid, eac in _WHAT_MAIN_WROTE.items():
        _record(cid)["eac_kwh"] = eac
        p2b.EFFECTIVE_EAC_KWH[cid] = eac
    p2b.ACQUIRED_CUSTOMERS.append(
        p2b.make_acquired_customer("C3_3", p2b.get_customer("C3"), "2017-06-30"))
    assert {cid: _record(cid)["eac_kwh"] for cid in _WHAT_MAIN_WROTE} == _WHAT_MAIN_WROTE
    assert p2b.ACQUIRED_CUSTOMERS


@pytest.mark.parametrize("reader", _H40_REDS)
def test_the_next_test_reads_the_drawn_book(reader):
    me = Path(__file__).relative_to(ROOT).as_posix()
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:randomly",
         f"{me}::test_a_run_leaves_its_rewrite_and_its_wins_in_the_book", reader],
        cwd=ROOT, capture_output=True, text=True, timeout=900)
    # Both must have run, or a reader that was never collected would pass for free.
    assert "2 passed" in run.stdout, run.stdout[-3000:] + run.stderr[-2000:]


def test_a_run_starts_with_none_of_the_last_runs_wins():
    p2b.ACQUIRED_CUSTOMERS.append(
        p2b.make_acquired_customer("C3_3", p2b.get_customer("C3"), "2017-06-30"))
    assert p2b.ACQUIRED_CUSTOMERS, "the seed did not reach the run's book: the clear is unexercised"
    p2b.start_from_the_drawn_book()
    assert p2b.ACQUIRED_CUSTOMERS == []
