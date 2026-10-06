"""B7 slice 5: a bill the world already booked as change-of-tenancy occupier debt is not collected,
or written off at the ordinary rate, a second time by the arrears engine.

Slice 4 books the window's energy as `occupier_debt_gbp` on the settled rows. Bill assembly stamps
that share on the bill (`occupier_share`), and `_resolve_bills` asks a named payer only for the rest.
The run test in `test_a_home_move_ends_supply_in_the_run.py` shows the stamp reaches real bills; a
2016 run has no leaver among the incoming legs, so only a leaver book can show the write-off move.
"""
import simulation.arrears_engine as ae
from tests.tools.test_generate_billing_ledger_pw import _resi_bill

N_HOUSEHOLDS = 40


def _book():
    """A stressed year for 40 resi households, every one of which leaves at the end of it."""
    bills, behavioral = [], {}
    for i in range(N_HOUSEHOLDS):
        cid = f"B7S5-{i:02d}"
        behavioral[cid] = {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]}
        bills += [_resi_bill(cid, "2022-%02d-28" % m, 150.0) for m in range(1, 13)]
    return bills, behavioral, {b["customer_id"] for b in bills}


def _marked(bills):
    """The first three months wholly the occupier's, the fourth half."""
    out = []
    for b in bills:
        month = int(b["period_end"][5:7])
        b = dict(b)
        if month <= 3:
            b["occupier_share"] = 1.0
        elif month == 4:
            b["occupier_share"] = 0.5
        out.append(b)
    return out


def _key(r):
    return (r["customer_id"], r["period_end"])


def test_the_marked_months_would_be_written_off_unmarked():
    """Partition control: if no marked month failed and was written off, every leg below passes
    whether or not the engine reads the mark."""
    bills, behavioral, leavers = _book()
    written, _ = ae.balance_settlement_from_outcomes(
        ae._resolve_bills(bills, behavioral, 42), leavers)
    months = {int(pe[5:7]) for (_c, pe, _f) in written}
    assert months & {1, 2, 3} and 4 in months and months - {1, 2, 3, 4}, sorted(months)


def test_a_bill_wholly_the_occupiers_is_not_resolved_and_a_split_bill_is_asked_for_the_rest():
    bills, behavioral, _ = _book()
    plain = {_key(r): r for r in ae._resolve_bills(bills, behavioral, 42)}
    marked = {_key(r): r for r in ae._resolve_bills(_marked(bills), behavioral, 42)}
    assert not [k for k in marked if int(k[1][5:7]) <= 3]
    assert len([k for k in marked if int(k[1][5:7]) == 4]) == N_HOUSEHOLDS
    for k, r in marked.items():
        if int(k[1][5:7]) == 4:
            assert r["amount_gbp"] == 75.0, r
        else:
            assert (r["outcome"], r["days_late"], r["amount_gbp"]) == (
                plain[k]["outcome"], plain[k]["days_late"], plain[k]["amount_gbp"]), r


def test_the_occupiers_share_leaves_the_written_off_total():
    bills, behavioral, leavers = _book()
    plain = ae.balance_write_offs_from_outcomes(ae._resolve_bills(bills, behavioral, 42), leavers)
    marked = ae.balance_write_offs_from_outcomes(
        ae._resolve_bills(_marked(bills), behavioral, 42), leavers)
    assert not [k for k in marked if int(k[1][5:7]) <= 3]
    assert sum(w["amount_gbp"] for w in marked.values()) < sum(
        w["amount_gbp"] for w in plain.values())
