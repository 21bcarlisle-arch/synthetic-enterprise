"""Controls on `tools/dual_leg_opposite_signs.py`, the instrument that grades the opposite-sign prereg.

Synthetic fixtures only. Reading a dual-book run before the publish run is committed reads the
answer before the grade, so no test here may load one.
"""
from __future__ import annotations

from datetime import date

import pytest

from simulation.arrears_engine import payment_method
from simulation.dd_balance_book import BalancePoint
from tools.dual_leg_opposite_signs import read_arm, read_run

MONTHS = ["2024-12", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05"]


def _traj(months, balances):
    return [BalancePoint(month=m, collected_gbp=0.0, consumed_gbp=0.0, balance_gbp=b)
            for m, b in zip(months, balances)]


def _book():
    # C1 crosses: electricity in credit while gas is in winter debit, then the reverse. Feb's
    # electricity £0.50 sits inside the ±£1 band. Nov's electricity point has no gas partner.
    # C2 is in credit on both legs and closes a month before the run ends. C5's gas leg closes a
    # month early while its electricity runs on. C3 and C4g have one leg.
    return {
        "C1": _traj(["2024-11"] + MONTHS, [50, 5, 5, 0.5, -3, -3, -10]),
        "C1g": _traj(MONTHS, [-20, -30, -40, 10, 10, 25]),
        "C2": _traj(MONTHS[:5], [10] * 5),
        "C2g": _traj(MONTHS[:5], [10] * 5),
        "C3": _traj(MONTHS, [-50] * 6),
        "C4g": _traj(MONTHS, [50] * 6),
        "C5": _traj(MONTHS, [10] * 6),
        "C5g": _traj(MONTHS[:5], [10] * 5),
    }


def test_each_reading_matches_the_hand_count():
    """DEFECT: a reading counts a different thing from the one the prereg defines -- one leg's
    months, a sign inside the ±£1 band, a single-fuel home, or a household with a leg closed
    before run end.

    By hand: three dual homes (C3, C4g have one leg). C1 has 6 shared months, 5 opposite (Feb is in
    the band); C2 and C5 have 5 each, none opposite: 5 of 16. C1's gas-debit opposite months are Dec and Jan,
    both in Dec-Apr. At run end only C1 is open: -£10 electricity against £25 gas, so £10 nets.
    """
    got = read_arm(_book(), "2025-05")
    assert got["N1_population"] == 3 and got["N1_open_at_run_end"] == 1
    assert got["N2_opposite_at_run_end"] == 1 and got["N2_share"] == 1.0
    assert got["N2_share_gas_credit_electricity_debit"] == 1.0
    assert (got["N3_household_months"], got["N3_opposite_months"]) == (16, 5)
    assert got["N3_gas_debit_months"] == 2 and got["N3_gas_debit_share_dec_to_apr"] == 1.0
    assert (got["N4_ever_opposite"], got["N4_share"]) == (1, 0.3333)
    assert got["N5_median_nettable_gbp"] == pytest.approx(10.0)
    assert got["N5_share_electricity_smaller"] == 1.0


def test_an_empty_population_reads_as_unknown_not_zero():
    """DEFECT: a book with no dual home prints shares of 0, which reads as a refuted prediction."""
    got = read_arm({"C3": _traj(MONTHS, [-50] * 6)}, "2025-05")
    assert got["N1_population"] == 0
    assert got["N2_share"] is None and got["N4_share"] is None
    assert got["N5_median_nettable_gbp"] is None


def _a_dual_direct_debit_household() -> str:
    for i in range(1, 500):
        cid = f"C{i}"
        if (payment_method("resi", 10.0, cid, "electricity") == "direct_debit"
                and payment_method("resi", 10.0, f"{cid}g", "gas") == "direct_debit"):
            return cid
    raise AssertionError("no household with both legs on direct debit in C1..C499")


def _bills(cid: str, commodity: str, amount: float) -> list[dict]:
    out = []
    for i in range(6):
        end = date(2025, i + 1, 28)
        out.append({"customer_id": cid, "period_start": end.replace(day=1).isoformat(),
                    "period_end": end.isoformat(), "total_amount_gbp": amount,
                    "segment": "resi", "commodity": commodity})
    return out


def test_the_books_own_route_admits_a_dual_household_and_finds_it_opposite():
    """DEFECT: the run route never reaches a dual household -- a leg id the book does not carry,
    or a closed set that drops both legs -- so every reading is None and looks like a clean read.

    Electricity bills £30 against a £25 debit, so it falls into debit; gas bills £40 against £50,
    so it builds credit. Both arms must see one dual home, open at run end, opposite every month.
    """
    hh = _a_dual_direct_debit_household()
    run = {"bills": _bills(hh, "electricity", 30.0) + _bills(f"{hh}g", "gas", 40.0),
           "opening_dd_by_customer": {hh: 25.0, f"{hh}g": 50.0}}
    out = read_run(run)
    assert out["run_end_month"] == "2025-06"
    for arm in out["arms"].values():
        assert arm["N1_population"] == 1 and arm["N1_open_at_run_end"] == 1
        assert arm["N3_household_months"] == 6 and arm["N3_opposite_months"] == 6
        assert arm["N2_share_gas_credit_electricity_debit"] == 1.0
        assert arm["N5_median_nettable_gbp"] == pytest.approx(30.0)


def test_a_run_with_no_dd_book_is_refused_with_its_reason():
    """DEFECT: a run without bills prints an empty table instead of saying why there is none."""
    with pytest.raises(SystemExit, match="no bills or no opening DD"):
        read_run({"bills": [], "opening_dd_by_customer": {}})
