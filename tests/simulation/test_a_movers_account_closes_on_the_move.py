"""A home mover's account closes on the move date, and every closure consequence reaches it.

`run_phase2b` keeps movers off `churned_billing_accounts`, rightly: a move is not a registration
loss. But phase 4c, the billing ledger and the decision probe built their closure roster from that
list alone, so a mover's account never closed. The arrears engine priced its unpaid final bill as a
stayer's live arrears and never wrote it off, and an SLC 14 credit was never refunded. Separately,
`extract_report_data` dropped `home_move_outs`, so nothing reading the published run could see the
movers. The ledger was one of those readers, and so was `forward_clv`, which read the published
run as a world without moves.

Each control names the defect it fails on:

* the partition fails if the movers are left out (the defect), or if the incoming occupant or a
  stayer is swept in;
* the chain control fails if the closure roster stops reaching the close write-off. The bare
  roster is asserted too: it shows the mover's failed final bill really does stay open without the
  repair, so the repaired arm is not green by accident;
* the reducer controls fail if `home_move_outs` is dropped, or if an absent key becomes `[]`.
  `home_move_outs` is not a `*_log`, so the reduction census cannot see it.
"""
from datetime import date

from saas.reporting.annual_report import extract_report_data
from simulation.arrears_engine import LEG_CLOSE, balance_settlement_from_outcomes
from simulation.household import households_whose_account_closed, supply_points_that_left

MOVER, MOVER_GAS, STAYER, SWITCHER, INCOMING = "C2", "C2g", "C3", "C1", "OCC-abc"

PHASE2B = {
    "churned_billing_accounts": [SWITCHER],
    "home_move_outs": [
        {"household": MOVER, "customer_id": MOVER, "commodity": "electricity",
         "move_date": "2021-06-14"},
        {"household": MOVER, "customer_id": MOVER_GAS, "commodity": "gas",
         "move_date": "2021-06-14"},
    ],
}
SUPPLY_POINTS = [SWITCHER, MOVER, MOVER_GAS, STAYER, INCOMING]


def test_a_mover_is_a_closed_account_and_a_stayer_or_the_incoming_occupant_is_not():
    assert households_whose_account_closed(PHASE2B) == {SWITCHER, MOVER}
    closed = supply_points_that_left(households_whose_account_closed(PHASE2B), SUPPLY_POINTS)
    assert closed == {SWITCHER, MOVER, MOVER_GAS}


def test_a_world_without_moves_closes_only_the_departures():
    assert households_whose_account_closed({"churned_billing_accounts": [SWITCHER]}) == {SWITCHER}
    assert households_whose_account_closed(
        {"churned_billing_accounts": [SWITCHER], "home_move_outs": None}) == {SWITCHER}


def _final_bill(outcome):
    return {"customer_id": MOVER, "period_end": "2021-06-14", "commodity": "electricity",
            "amount_gbp": 84.0, "due_date": date(2021, 7, 12), "method": "standard_credit",
            "outcome": outcome, "days_late": 0}


def test_a_movers_unpaid_final_bill_is_written_off_at_close():
    resolved = [_final_bill("failed")]
    bare = supply_points_that_left(PHASE2B["churned_billing_accounts"], SUPPLY_POINTS)
    stranded, _ = balance_settlement_from_outcomes(resolved, bare)
    assert stranded == {}, (
        "the bare roster now closes the mover, so this control has lost the defect it exists for")

    closed = supply_points_that_left(households_whose_account_closed(PHASE2B), SUPPLY_POINTS)
    written_off, _ = balance_settlement_from_outcomes(resolved, closed)
    row = written_off[(MOVER, "2021-06-14", "electricity")]
    assert row["leg"] == LEG_CLOSE
    assert row["amount_gbp"] == 84.0


def _run_output(**phase2b):
    base = {"all_records": [], "committee_wake_ups": [], "hedge_evolution": {},
            "starting_treasury": 0.0, "final_treasury": 0.0, "total_gross": 0.0,
            "total_capital": 0.0, "administration_event": None, "customer_events": []}
    base.update(phase2b)
    return {"phase2b": base, "years": {"2017": {}}}


def test_the_reducer_forwards_the_movers():
    reduced = extract_report_data(_run_output(**PHASE2B))
    assert reduced["home_move_outs"] == PHASE2B["home_move_outs"]
    assert households_whose_account_closed(reduced) == {SWITCHER, MOVER}


def test_the_reducer_keeps_an_absent_move_register_absent():
    """Absent means moves are off; `[]` would claim a world with moves in which nobody moved."""
    assert extract_report_data(_run_output())["home_move_outs"] is None


def _bill(cid, outcome, amount, due, commodity="electricity"):
    return {"customer_id": cid, "period_end": due.replace(day=1).isoformat(), "commodity": commodity,
            "amount_gbp": amount, "due_date": due, "method": "standard_credit",
            "outcome": outcome, "days_late": 0}


def test_the_closing_balance_takes_each_branch_and_is_the_write_off_at_close():
    """Each closed account's balance at its final bill (home_moves.md s.8.8a), from the walk that
    writes it off. One leaver owes, one is in credit, one is settled, and the stayer has none.

    The partition fails if the balance is never written (the defect: every run handed
    `move_out_final_bills` None), if a branch cannot be reached, if a stayer is given a closing
    balance, or if the debt published differs from the debt the P&L writes off at close."""
    owes, credit, settled, stayer = "L-OWE", "L-CR", "L-SET", "S-1"
    resolved = [
        _bill(owes, "success", 50.0, date(2021, 5, 12)),
        _bill(owes, "failed", 84.0, date(2021, 6, 12)),
        _bill(credit, "success", 50.0, date(2021, 5, 12)),
        _bill(credit, "credit", -17.5, date(2021, 6, 12)),
        _bill(settled, "failed", 30.0, date(2021, 5, 12)),
        _bill(settled, "credit", -30.0, date(2021, 6, 12)),
        _bill(stayer, "failed", 40.0, date(2021, 6, 12)),
    ]
    closing: dict[str, float] = {}
    written_off, _ = balance_settlement_from_outcomes(resolved, {owes, credit, settled}, closing)
    assert closing == {owes: 84.0, credit: -17.5, settled: 0.0}
    assert closing[owes] > 0 and closing[credit] < 0 and closing[settled] == 0
    at_close = sum(v["amount_gbp"] for (cid, _pe, _c), v in written_off.items()
                   if cid == owes and v["leg"] == LEG_CLOSE)
    assert at_close == closing[owes]
    # The out-parameter changes nothing it does not own.
    assert balance_settlement_from_outcomes(resolved, {owes, credit, settled})[0] == written_off
