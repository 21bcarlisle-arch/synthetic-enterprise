"""Phase PW -- Population Anchor I&C arrears separation tests."""
import json

from tools.population_anchor import _arrears_check_by_year, ARREARS_BENCHMARK_NORMAL_HI


def _ledger_ic(*arrears_list):
    customers = {}
    for cid, opened_date in arrears_list:
        seg = "I&C" if "_IC" in cid else "resi"
        if cid not in customers:
            customers[cid] = {"segment": seg, "arrears_history": []}
        customers[cid]["arrears_history"].append({"opened_date": opened_date})
    return {"customers": customers}


def test_ic_arrears_rate_pct_field_present():
    ledger = _ledger_ic(("C_IC1", "2020-03-01"))
    years = {"2020": {"active_customer_ids": ["C_IC1", "C_IC2"]}}
    result = _arrears_check_by_year(ledger, years)
    assert "ic_arrears_rate_pct" in result[0]
    assert "ic_arrears_count" in result[0]
    assert "ic_active_customers" in result[0]


def test_ic_aggregate_rate_pct_present():
    ledger = _ledger_ic(("C_IC1", "2020-03-01"))
    years = {"2020": {"active_customer_ids": ["C_IC1", "C_IC2"]}}
    result = _arrears_check_by_year(ledger, years)
    assert "ic_aggregate_rate_pct" in result[0]


def test_portfolio_type_note_present():
    ledger = {"customers": {}}
    years = {"2020": {"active_customer_ids": ["C1", "C2"]}}
    result = _arrears_check_by_year(ledger, years)
    assert "portfolio_type_note" in result[0]


def test_ic_aggregate_rate_green_when_below_benchmark():
    customers = {}
    for i in range(1, 21):
        cid = "C_IC%d" % i
        customers[cid] = {"segment": "I&C", "arrears_history": []}
    customers["C_IC1"]["arrears_history"].append({"opened_date": "2020-03-01"})
    ledger = {"customers": customers}
    active = ["C_IC%d" % i for i in range(1, 21)]
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["rag"] == "GREEN"
    assert result[0]["ic_aggregate_rate_pct"] == 5.0


def test_ic_aggregate_rate_red_when_above_amber():
    customers = {}
    for i in range(1, 21):
        cid = "C_IC%d" % i
        customers[cid] = {"segment": "I&C", "arrears_history": []}
    for i in range(1, 5):
        customers["C_IC%d" % i]["arrears_history"].append({"opened_date": "2020-01-01"})
    ledger = {"customers": customers}
    active = ["C_IC%d" % i for i in range(1, 21)]
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["rag"] == "RED"


def test_no_ic_customers_falls_back_to_overall():
    ledger = _ledger_ic(*[("C%d" % i, "2020-01-01") for i in range(1, 10)])
    active = ["C%d" % i for i in range(1, 101)]
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["rag"] == "AMBER"


def test_rag_uses_ic_aggregate_not_per_year():
    customers = {"C_IC1": {"segment": "I&C", "arrears_history": [{"opened_date": "2016-03-01"}]}}
    for yr in range(2017, 2021):
        cid = "C_IC%d" % (yr - 2014)
        customers[cid] = {"segment": "I&C", "arrears_history": []}
    ledger = {"customers": customers}
    years_data = {}
    for i, yr in enumerate(range(2016, 2021)):
        cid = "C_IC%d" % (i + 1)
        years_data[str(yr)] = {"active_customer_ids": [cid]}
    result = _arrears_check_by_year(ledger, years_data)
    agg_rate = result[0]["ic_aggregate_rate_pct"]
    for r in result:
        expected = "RED" if agg_rate > 15.0 else ("AMBER" if agg_rate > 8.0 else "GREEN")
        assert r["rag"] == expected


def test_ic_per_year_rate_calculated():
    customers = {
        "C_IC1": {"segment": "I&C", "arrears_history": [{"opened_date": "2020-05-01"}]},
        "C_IC2": {"segment": "I&C", "arrears_history": []},
        "C_IC3": {"segment": "I&C", "arrears_history": []},
        "C_IC4": {"segment": "I&C", "arrears_history": []},
    }
    ledger = {"customers": customers}
    active = ["C_IC1", "C_IC2", "C_IC3", "C_IC4"]
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["ic_arrears_count"] == 1
    assert result[0]["ic_active_customers"] == 4
    assert abs(result[0]["ic_arrears_rate_pct"] - 25.0) < 0.01

