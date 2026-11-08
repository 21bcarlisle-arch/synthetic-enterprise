"""Phase 101: EPC efficiency advice tests."""

from company.billing.efficiency_advice import epc_advice, available_schemes, efficiency_summary


def test_epc_a_high_efficiency():
    advice = epc_advice("A")
    assert len(advice) > 0
    assert any("efficient" in t.lower() for t in advice)


def test_epc_g_has_eco4():
    advice = epc_advice("G")
    assert any("ECO4" in t for t in advice)


def test_epc_case_insensitive():
    assert epc_advice("d") == epc_advice("D")


def test_epc_none_returns_assessment_message():
    advice = epc_advice(None)
    assert len(advice) == 1
    assert "EPC" in advice[0]


def test_available_schemes_epc_d():
    customer = {"epc_rating": "D"}
    schemes = available_schemes(customer)
    assert "Great British Insulation Scheme" in schemes


def test_available_schemes_epc_e_has_eco4():
    customer = {"epc_rating": "E"}
    schemes = available_schemes(customer)
    assert "ECO4" in schemes


def test_efficiency_summary_structure():
    customer = {"epc_rating": "D"}
    s = efficiency_summary(customer)
    assert s["band"] == "D"
    assert isinstance(s["advice"], list)
    assert isinstance(s["available_schemes"], list)
    assert isinstance(s["is_high_efficiency"], bool)


def test_high_efficiency_flag_a():
    assert efficiency_summary({"epc_rating": "A"})["is_high_efficiency"] is True


def test_high_efficiency_flag_e():
    assert efficiency_summary({"epc_rating": "E"})["is_high_efficiency"] is False


def test_dashboard_has_efficiency_block():
    with open("company/portal/templates/dashboard.html") as f:
        html = f.read()
    assert "efficiency" in html
    assert "epc_rating" in html


def test_dashboard_route_returns_200():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1")
    assert r.status_code == 200


from company.billing.efficiency_advice import epc_advice, available_schemes, efficiency_summary


def test_epc_b_has_advice():
    advice = epc_advice("B")
    assert len(advice) > 0


def test_epc_d_has_advice():
    advice = epc_advice("D")
    assert len(advice) > 0


def test_epc_unknown_falls_back():
    result = epc_advice("Z")
    assert len(result) > 0


def test_available_schemes_unknown_epc_returns_empty():
    result = available_schemes({"epc_rating": "X"})
    assert result == []


def test_efficiency_summary_is_high_c():
    result = efficiency_summary({"epc_rating": "C"})
    assert result["is_high_efficiency"] is True


def test_efficiency_summary_is_not_high_e():
    result = efficiency_summary({"epc_rating": "E"})
    assert result["is_high_efficiency"] is False


def test_efficiency_summary_all_keys():
    result = efficiency_summary({"epc_rating": "D"})
    for key in ("epc_rating", "band", "is_high_efficiency", "advice", "available_schemes"):
        assert key in result
