"""Phase AS: Gas Exit Analysis section in annual report tests."""
import pytest
from saas.reporting.annual_report import _section_gas_exit_analysis


def _pcp(pairs):
    result = {}
    for cid, en, gn in pairs:
        result[cid] = {"electricity": {"net": en, "gross": en * 1.5, "capital": 0.0, "revenue": en * 2}}
        gr = abs(gn) * 2
        result[cid + "g"] = {"gas": {"net": gn, "gross": gr, "capital": abs(gn) * 0.1, "revenue": gr * 1.2}}
    return result


def _pcl(segs):
    return {cid: {"segment": s} for cid, s in segs}


def _data(pairs, segs):
    return {"per_cid_comm_pnl": _pcp(pairs), "per_customer_lifetime": _pcl(segs)}


# 1. Empty pcp returns empty
def test_empty_returns_empty():
    assert _section_gas_exit_analysis({}) == ""
    assert _section_gas_exit_analysis({"per_cid_comm_pnl": {}}) == ""


# 2. Header present with gas data
def test_header_present():
    d = _data([("C1", 500.0, 300.0)], [("C1", "resi")])
    result = _section_gas_exit_analysis(d)
    assert "Gas Supply Exit Decision Analysis" in result


# 3. Scenario comparison table shown
def test_scenario_table_shown():
    d = _data([("C1", 500.0, 300.0), ("C2", 200.0, -100.0)], [("C1", "resi"), ("C2", "resi")])
    result = _section_gas_exit_analysis(d)
    assert "STATUS_QUO" in result
    assert "EXIT_GAS" in result
    assert "REPRICE_GAS" in result


# 4. Recommended action shown
def test_recommended_action_shown():
    d = _data([("C_IC3", 80000.0, -130000.0)], [("C_IC3", "I&C")])
    result = _section_gas_exit_analysis(d)
    assert "Recommended action" in result


# 5. Loss-making accounts section shown
def test_loss_making_section():
    d = _data([("C4", 100.0, -200.0)], [("C4", "resi")])
    result = _section_gas_exit_analysis(d)
    assert "Loss-Making Gas Accounts" in result
    assert "C4g" in result


# 6. Revenue uplift shown for loss-making accounts
def test_uplift_shown():
    d = _data([("C_IC3", 80000.0, -130000.0)], [("C_IC3", "I&C")])
    result = _section_gas_exit_analysis(d)
    assert "%" in result


# 7. Accretive accounts listed
def test_accretive_accounts_listed():
    d = _data([("C1", 500.0, 300.0), ("C2", 200.0, -100.0)], [("C1", "resi"), ("C2", "resi")])
    result = _section_gas_exit_analysis(d)
    assert "Accretive gas accounts" in result
    assert "C1g" in result


# 8. Board decision note shown
def test_board_decision_note():
    d = _data([("C1", 500.0, 300.0)], [("C1", "resi")])
    result = _section_gas_exit_analysis(d)
    assert "Board Decision" in result


# 9. No profiles (no trailing-g keys) returns empty
def test_no_gas_cids_returns_empty():
    pcp = {"C1": {"electricity": {"net": 500.0, "gross": 750.0, "capital": 0.0, "revenue": 1000.0}}}
    result = _section_gas_exit_analysis({"per_cid_comm_pnl": pcp})
    assert result == ""


# 10. vs-status-quo delta shown
def test_vs_status_quo_shown():
    d = _data([("C1", 500.0, 300.0)], [("C1", "resi")])
    result = _section_gas_exit_analysis(d)
    assert "vs Status Quo" in result
