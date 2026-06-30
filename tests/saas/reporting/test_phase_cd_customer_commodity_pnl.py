"""Phase CD: Customer Commodity P&L section tests."""
import pytest


def _section(pcp_dict):
    from saas.reporting.annual_report import _section_customer_commodity_pnl
    return _section_customer_commodity_pnl({"per_cid_comm_pnl": pcp_dict})


def _cid(elec_net=None, gas_net=None):
    d = {}
    if elec_net is not None:
        d["electricity"] = {"net": elec_net, "gross": elec_net + 1000, "capital": 100, "revenue": elec_net + 2000}
    if gas_net is not None:
        d["gas"] = {"net": gas_net, "gross": gas_net + 800, "capital": 50, "revenue": gas_net + 1500}
    return d


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section({}) == ""


# 2. Header present
def test_section_header():
    result = _section({"C1": _cid(elec_net=1000)})
    assert "Customer Lifetime P&L by Commodity" in result


# 3. Loss-making customers marked with *
def test_loss_marked():
    result = _section({"C5": _cid(elec_net=-42)})
    assert "*" in result


# 4. Profitable customer row does NOT contain asterisk marker
def test_profitable_not_marked():
    result = _section({"C_IC1": _cid(elec_net=837491)})
    # The asterisk marker " *" only appears in loss-making rows (after currency figure)
    assert " *" not in result.split("Loss-making")[0]  # no marker before summary section


# 5. Total row shown
def test_total_row():
    result = _section({"C1": _cid(elec_net=1000), "C2": _cid(gas_net=500)})
    assert "Total" in result


# 6. Gas loss-making listed in summary
def test_gas_loss_listed():
    result = _section({"C_IC3g": _cid(gas_net=-132711)})
    assert "Gas loss-making" in result


# 7. Loss-making account in summary
def test_loss_accounts_listed():
    result = _section({"C7": _cid(elec_net=-1378)})
    assert "Loss-making accounts" in result


# 8. Elec column shows — for gas-only customers
def test_elec_dash_for_gas_only():
    result = _section({"C1g": _cid(gas_net=652)})
    assert "—" in result


# 9. Gas column shows — for elec-only customers
def test_gas_dash_for_elec_only():
    result = _section({"C1": _cid(elec_net=421)})
    assert "—" in result


# 10. Total row sums elec and gas
def test_total_sums_correctly():
    result = _section({
        "C1": _cid(elec_net=1000),
        "C1g": _cid(gas_net=500),
    })
    assert "£1,500" in result  # Total = 1000 + 500


# 11. Gas portfolio net shown
def test_gas_portfolio_net():
    result = _section({"C1g": _cid(gas_net=652)})
    assert "Gas portfolio net" in result


# 12. Multiple customers all shown
def test_multiple_customers():
    result = _section({
        "C1": _cid(elec_net=1000),
        "C2": _cid(elec_net=2000),
        "C3": _cid(gas_net=300),
    })
    assert "C1" in result
    assert "C2" in result
    assert "C3" in result
