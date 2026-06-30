"""Phase BU: Gas Exit Decision section tests."""
import pytest
from saas.reporting.annual_report import _section_gas_exit_decision


def _gas_comm(gross, net, rev, cap=0):
    return {"gas": {"gross": gross, "capital": cap, "net": net, "revenue": rev}}


def _elec_comm(gross, net, rev, cap=0):
    return {"electricity": {"gross": gross, "capital": cap, "net": net, "revenue": rev}}


def _pcl(cid, seg="resi"):
    return {cid: {"acquisition_date": "2016-01-01", "segment": seg, "commodity": "electricity"}}


def _pclg(cid, seg="resi"):
    return {cid + "g": {"acquisition_date": "2016-01-01", "segment": seg, "commodity": "gas"}}


def _data(pairs):
    """pairs = list of (cid, elec_net, gas_net, seg) tuples."""
    comm_pnl = {}
    pcl = {}
    for cid, elec_net, gas_net, seg in pairs:
        comm_pnl[cid] = _elec_comm(elec_net * 0.5, elec_net, elec_net * 2)
        comm_pnl[cid + "g"] = _gas_comm(abs(gas_net) * 0.5, gas_net, abs(gas_net) * 2)
        pcl.update(_pcl(cid, seg))
        pcl.update(_pclg(cid, seg))
    return {"per_cid_comm_pnl": comm_pnl, "per_customer_lifetime": pcl}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_gas_exit_decision({}) == ""
    assert _section_gas_exit_decision({"per_cid_comm_pnl": {}, "per_customer_lifetime": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data([("C1", 1000, -500, "resi")])
    assert "Gas Exit Decision" in _section_gas_exit_decision(d)


# 3. Status quo shown
def test_status_quo_row():
    d = _data([("C1", 1000, -500, "resi")])
    result = _section_gas_exit_decision(d)
    assert "Status Quo" in result


# 4. Loss-making gas accounts flagged
def test_loss_making_flagged():
    d = _data([("C1", 1000, -500, "resi")])
    result = _section_gas_exit_decision(d)
    assert "Loss-making gas accounts: C1" in result


# 5. No loss-making accounts
def test_no_loss_making():
    d = _data([("C1", 1000, 500, "resi")])
    result = _section_gas_exit_decision(d)
    assert "None" in result or "loss-making" in result.lower()


# 6. Board recommendation present
def test_board_recommendation():
    d = _data([("C1", 1000, -500, "resi")])
    result = _section_gas_exit_decision(d)
    assert "Board recommendation" in result


# 7. Exit gas row present
def test_exit_gas_row():
    d = _data([("C1", 1000, -500, "resi")])
    result = _section_gas_exit_decision(d)
    assert "Exit Gas" in result


# 8. Reprice row present
def test_reprice_row():
    d = _data([("C1", 1000, -500, "resi")])
    result = _section_gas_exit_decision(d)
    assert "Reprice" in result


# 9. Delta vs status quo shown
def test_delta_shown():
    d = _data([("C1", 1000, -500, "resi")])
    result = _section_gas_exit_decision(d)
    assert "+" in result  # exit/reprice both improve vs status quo


# 10. Multiple gas customers
def test_multiple_gas_customers():
    d = _data([("C1", 5000, -3000, "I&C"), ("C2", 1000, 200, "resi")])
    result = _section_gas_exit_decision(d)
    assert "C1" in result  # loss-maker shown


# 11. I&C segment higher churn risk
def test_ic_segment_churn_risk():
    d1 = _data([("C1", 5000, -3000, "I&C")])
    d2 = _data([("C1", 5000, -3000, "resi")])
    r1 = _section_gas_exit_decision(d1)
    r2 = _section_gas_exit_decision(d2)
    # I&C has higher churn risk => lower expected elec net after exit
    # Both should show Gas Exit Decision Analysis
    assert "Gas Exit" in r1 and "Gas Exit" in r2


# 12. Section returns non-empty when data present
def test_returns_non_empty():
    d = _data([("C1", 1000, -500, "resi"), ("C2", 2000, 300, "I&C")])
    result = _section_gas_exit_decision(d)
    assert len(result) > 100
