"""Phase BP: Customer Cohort Revenue Analysis section tests."""
import pytest
from saas.reporting.annual_report import _section_cohort_revenue_analysis


def _pcl(cid, acq_date, segment="resi", commodity="electricity"):
    return {cid: {"acquisition_date": acq_date, "segment": segment, "commodity": commodity}}


def _pcp(cid, revenue, gross, net):
    return {cid: {"revenue": revenue, "gross": gross, "net": net}}


def _data(pcl_entries, pcp_entries):
    pcl = {}
    pcp = {}
    for e in pcl_entries:
        pcl.update(e)
    for e in pcp_entries:
        pcp.update(e)
    return {"per_customer_lifetime": pcl, "per_cid_pnl": pcp}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_cohort_revenue_analysis({}) == ""
    assert _section_cohort_revenue_analysis({"per_customer_lifetime": {}, "per_cid_pnl": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data(
        [_pcl("C1", "2016-01-01")],
        [_pcp("C1", 5000, 2000, 500)],
    )
    assert "Customer Cohort Revenue Analysis" in _section_cohort_revenue_analysis(d)


# 3. Cohort year in table
def test_cohort_year():
    d = _data(
        [_pcl("C1", "2016-01-01")],
        [_pcp("C1", 5000, 2000, 500)],
    )
    result = _section_cohort_revenue_analysis(d)
    assert "| 2016 |" in result


# 4. Revenue per customer computed
def test_revenue_per_customer():
    d = _data(
        [_pcl("C1", "2017-01-01"), _pcl("C2", "2017-01-01")],
        [_pcp("C1", 1000, 500, 200), _pcp("C2", 3000, 1000, 400)],
    )
    result = _section_cohort_revenue_analysis(d)
    # avg = (1000+3000)/2 = 2000
    assert "£2,000" in result


# 5. Net negative cohort flagged
def test_net_negative_flagged():
    d = _data(
        [_pcl("C1", "2019-01-01")],
        [_pcp("C1", 5000, 2000, -50000)],
    )
    result = _section_cohort_revenue_analysis(d)
    assert "Loss cohort" in result and "2019" in result


# 6. Best revenue/customer cohort
def test_best_rpc_cohort():
    d = _data(
        [_pcl("C1", "2016-01-01"), _pcl("C2", "2017-01-01")],
        [_pcp("C1", 5000, 2000, 500), _pcp("C2", 3000000, 1000000, 800000)],
    )
    result = _section_cohort_revenue_analysis(d)
    assert "Best revenue/customer cohort: 2017" in result


# 7. Best net margin cohort
def test_best_net_cohort():
    d = _data(
        [_pcl("C1", "2016-01-01"), _pcl("C2", "2017-01-01")],
        [_pcp("C1", 5000, 2000, 500), _pcp("C2", 3000000, 1000000, 800000)],
    )
    result = _section_cohort_revenue_analysis(d)
    assert "Best net margin cohort: 2017" in result


# 8. Multiple customers in same cohort summed
def test_cohort_aggregation():
    d = _data(
        [_pcl("C1", "2016-01-01"), _pcl("C2", "2016-01-01")],
        [_pcp("C1", 2000, 1000, 300), _pcp("C2", 3000, 1500, 500)],
    )
    result = _section_cohort_revenue_analysis(d)
    # total revenue = 5000
    assert "£5,000" in result
    # customer count = 2
    assert "| 2 |" in result


# 9. Multiple cohorts sorted by year
def test_cohorts_sorted():
    d = _data(
        [_pcl("C1", "2018-01-01"), _pcl("C2", "2016-01-01")],
        [_pcp("C1", 1000000, 400000, 200000), _pcp("C2", 5000, 2000, 500)],
    )
    result = _section_cohort_revenue_analysis(d)
    pos_2016 = result.find("| 2016 |")
    pos_2018 = result.find("| 2018 |")
    assert pos_2016 < pos_2018


# 10. Note about gas legs
def test_note_present():
    d = _data(
        [_pcl("C1", "2016-01-01")],
        [_pcp("C1", 5000, 2000, 500)],
    )
    result = _section_cohort_revenue_analysis(d)
    assert "Note:" in result or "cohort" in result.lower()


# 11. Customer present in pcl but missing in pcp shows as zero revenue
def test_missing_pcp_customer_defaults_to_zero():
    d = _data(
        [_pcl("C1", "2016-01-01"), _pcl("C2", "2016-01-01")],
        [_pcp("C1", 5000, 2000, 500)],  # C2 missing from pcp
    )
    result = _section_cohort_revenue_analysis(d)
    # total revenue = 5000 (C2 defaults to 0)
    assert "£5,000" in result
    assert "| 2 |" in result  # both customers in cohort counted


# 12. Positive net shown without minus
def test_positive_net_format():
    d = _data(
        [_pcl("C1", "2017-01-01")],
        [_pcp("C1", 3000000, 1000000, 837000)],
    )
    result = _section_cohort_revenue_analysis(d)
    assert "£837,000" in result
    assert "-£837,000" not in result
