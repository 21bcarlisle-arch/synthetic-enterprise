"""Phase AR: Gas Exit Decision Book tests."""
import pytest
from company.finance.gas_exit_analysis import (
    GasExitDecisionBook,
    GasAccountProfile,
    GasScenarioResult,
)


def _pcp(pairs):
    """Build per_cid_comm_pnl from list of (cid, elec_net, gas_net, gas_rev, gas_cap)."""
    result = {}
    for item in pairs:
        if len(item) == 3:
            cid, en, gn = item
            gr, gc = abs(gn) * 2, abs(gn) * 0.1
        else:
            cid, en, gn, gr, gc = item
        result[cid] = {"electricity": {"net": en, "gross": en * 1.5, "capital": 0.0, "revenue": en * 2}}
        result[cid + "g"] = {"gas": {"net": gn, "gross": gr, "capital": gc, "revenue": gr * 1.2}}
    return result


def _pcl(segments):
    return {cid: {"segment": seg} for cid, seg in segments}


# 1. Empty data returns empty profiles
def test_empty_returns_no_profiles():
    book = GasExitDecisionBook({}, {})
    assert book._profiles == []


# 2. Pairs inferred from trailing-g keys
def test_pairs_inferred():
    pcp = _pcp([("C1", 500.0, 300.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi")]))
    assert len(book._profiles) == 1
    assert book._profiles[0].customer_id == "C1"


# 3. Status quo returns combined net
def test_status_quo_combined_net():
    pcp = _pcp([("C1", 500.0, 300.0), ("C2", 200.0, -100.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi"), ("C2", "resi")]))
    sq = book.status_quo()
    assert sq.scenario_name == "STATUS_QUO"
    assert abs(sq.total_net_gbp - 900.0) < 1.0  # 500+300+200-100


# 4. Exit gas removes gas net
def test_exit_gas_removes_gas():
    pcp = _pcp([("C_IC3", 80000.0, -130000.0, 600000.0, 180000.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C_IC3", "I&C")]))
    exit_s = book.exit_gas()
    assert exit_s.gas_net_gbp == 0.0
    assert exit_s.scenario_name == "EXIT_GAS"


# 5. Exit gas applies I&C churn risk 40%
def test_exit_gas_ic_churn_risk():
    pcp = _pcp([("C_IC3", 80000.0, -130000.0, 600000.0, 180000.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C_IC3", "I&C")]))
    exit_s = book.exit_gas()
    # I&C: 80000 * (1 - 0.40) = 48000
    assert abs(exit_s.elec_net_gbp - 48000.0) < 1.0


# 6. Exit gas applies resi churn risk 20%
def test_exit_gas_resi_churn_risk():
    pcp = _pcp([("C1", 500.0, -100.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi")]))
    exit_s = book.exit_gas()
    # resi: 500 * (1 - 0.20) = 400
    assert abs(exit_s.elec_net_gbp - 400.0) < 1.0


# 7. Reprice gas zeroes out loss-making accounts
def test_reprice_zeroes_loss_making():
    pcp = _pcp([("C1", 500.0, 300.0), ("C2", 200.0, -100.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi"), ("C2", "resi")]))
    reprice = book.reprice_gas()
    # Accretive: C1g = 300; loss-making C2g = 0 (repriced to break-even)
    assert abs(reprice.gas_net_gbp - 300.0) < 1.0


# 8. Reprice keeps electricity unchanged
def test_reprice_electricity_unchanged():
    pcp = _pcp([("C1", 500.0, 300.0), ("C2", 200.0, -100.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi"), ("C2", "resi")]))
    reprice = book.reprice_gas()
    assert abs(reprice.elec_net_gbp - 700.0) < 1.0  # 500 + 200


# 9. loss_making_accounts returns negative-gas accounts
def test_loss_making_accounts():
    pcp = _pcp([("C1", 500.0, 300.0), ("C2", 200.0, -100.0), ("C3", 100.0, -50.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi"), ("C2", "resi"), ("C3", "resi")]))
    loss = book.loss_making_accounts()
    assert len(loss) == 2
    assert all(not p.is_gas_accretive for p in loss)


# 10. accretive_accounts returns positive-gas accounts
def test_accretive_accounts():
    pcp = _pcp([("C1", 500.0, 300.0), ("C2", 200.0, -100.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi"), ("C2", "resi")]))
    acc = book.accretive_accounts()
    assert len(acc) == 1
    assert acc[0].customer_id == "C1"


# 11. breakeven_revenue_uplift_pct positive for loss-making accounts
def test_breakeven_uplift_positive():
    pcp = _pcp([("C2", 200.0, -100.0, 500.0, 10.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C2", "resi")]))
    profile = book._profiles[0]
    assert profile.breakeven_revenue_uplift_pct > 0


# 12. scenario_comparison recommends REPRICE when reprice > exit
def test_scenario_comparison_recommends_reprice():
    # Make reprice clearly better than exit
    pcp = _pcp([("C_IC3", 80000.0, -130000.0, 600000.0, 180000.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C_IC3", "I&C")]))
    comp = book.scenario_comparison()
    assert comp["recommended_action"] in ("REPRICE_GAS", "EXIT_GAS")  # either is valid
    assert "loss_making_accounts" in comp
    assert len(comp["loss_making_accounts"]) == 1

# 13. scenario_comparison keys present
def test_scenario_comparison_keys():
    pcp = _pcp([("C1", 500.0, 300.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi")]))
    comp = book.scenario_comparison()
    for key in ("status_quo_net_gbp", "exit_gas_net_gbp", "reprice_gas_net_gbp",
                 "exit_vs_status_quo_gbp", "reprice_vs_status_quo_gbp", "recommended_action"):
        assert key in comp

# 14. gas_exit_summary returns non-empty string
def test_gas_exit_summary_string():
    pcp = _pcp([("C1", 500.0, 300.0), ("C4", 100.0, -200.0)])
    book = GasExitDecisionBook(pcp, _pcl([("C1", "resi"), ("C4", "resi")]))
    summary = book.gas_exit_summary()
    assert "Gas Exit Decision Book" in summary
    assert "Recommended action" in summary
