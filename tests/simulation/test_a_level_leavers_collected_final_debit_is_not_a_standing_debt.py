"""A level leaver's final bill that asked the scheme's debit and was collected paid it
(home_moves.md s.8.8f choices 26-27).

Defect this file exists to catch: the world collects the debit on the final bill while the page's
close still holds it as a standing debt (s.8.8b choice 3), so the page prints owed what the mandate
already took, and the desk and the page disagree on rows 4 and 7 of the domain-invariant gate.
"""
from datetime import date, timedelta
from types import SimpleNamespace

import simulation.world_payment_truth as wpt
from simulation.arrears_engine import balance_settlement_from_outcomes


def _row(month, outcome, debit=0.0):
    pe = f"2020-{month:02d}-28"
    return {"customer_id": "L", "period_end": pe, "commodity": "electricity", "amount_gbp": 50.0,
            "due_date": date.fromisoformat(pe) + timedelta(days=14), "method": "direct_debit",
            "outcome": outcome, "days_late": 0, "debit_paid_gbp": debit}


#: Paid 40 a month against two 50 bills: the scheme left 20. The third is the final bill, off level.
_LEVEL = {"L": [{"month": f"2020-{m:02d}", "collection_date": f"2020-{m:02d}-19", "amount_gbp": 40.0}
                for m in (1, 2)]}


def _close(final_outcome, debit):
    closing = {}
    written, _ = balance_settlement_from_outcomes(
        [_row(1, "success"), _row(2, "success"), _row(3, final_outcome, debit)], {"L"}, closing,
        level_dd_collections=_LEVEL)
    return closing["L"], round(sum(w["amount_gbp"] for w in written.values()), 2)


def test_both_fates_are_reached_the_debit_collected_and_the_debit_still_standing():
    assert _close("success", 20.0)[0] == 0.0 and _close("success", 0.0)[0] == 20.0


def test_a_failed_final_bill_leaves_its_face_and_the_debit_owed():
    closing, written = _close("failed", 0.0)
    assert closing == 70.0 and written == 50.0


def test_the_payment_truth_carries_the_debit_onto_the_final_month():
    month = wpt.bill_month_of(5)
    rec = SimpleNamespace(customer_id="L", period_index=5, result="success", days_late=0,
                          payment_method="direct_debit", account_id="A", due_date=date(2020, 6, 1),
                          settled_on=None)
    triad = SimpleNamespace(
        records=[rec], _final_bill_part_share={}, _crossed_settlements=[],
        _household_plans=SimpleNamespace(_terms={}),
        _final_month_nets=[{"leg": "L", "bill_month": month, "debit_asked_gbp": 20.0},
                           {"leg": "L", "bill_month": "1999-01", "debit_asked_gbp": 9.0}])
    out = wpt.build(triad, date(2025, 6, 30))
    assert out["L"]["outcomes"][month]["debit_asked_gbp"] == 20.0
    assert "1999-01" not in out["L"]["outcomes"]


def test_the_engine_counts_the_debit_paid_only_on_a_whole_success():
    """The resolved final bill carries `debit_paid_gbp` from the truth's ask when its collection
    succeeded whole, and 0 when it failed or was part-paid (choice 26). All three fates are reached."""
    import simulation.arrears_engine as ae
    from tests.simulation.test_world_payment_truth import MONTHS, _book, _truth

    def paid(result, part=None):
        truth = _truth(failed=(), months=MONTHS)
        last = truth["outcomes"][MONTHS[-1][:7]]
        last.update(result=result, debit_asked_gbp=20.0)
        if part:
            last["part_share"] = part
        bills, behavioral, _ = _book(truth)
        rows = [r for r in ae._resolve_bills(bills, behavioral, 42) if r["period_end"] == MONTHS[-1]]
        return [r.get("debit_paid_gbp") for r in rows if r["outcome"] != "repayment"]

    assert paid("success") == [20.0]
    assert paid("failed") == [0.0]
    assert paid("success", part=0.5) == [0.0]
