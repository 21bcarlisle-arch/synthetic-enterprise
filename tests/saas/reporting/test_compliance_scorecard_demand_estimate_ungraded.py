"""The SLC 20-24 check over a demand-estimation log holding an ungraded row.

`error_pct` is None until the run settles the year ahead of the estimate. On 2026-10-13 the
weekly publish died after 6,979 s on `abs(None)` here; the obvious repair, `or 0.0`, would
instead publish a perfect forecast nobody made (K2). This reds on either.
"""
from company.regulatory.compliance_scorecard import ComplianceDomain, RAGStatus
from saas.reporting.compliance_scorecard_population import populate_compliance_scorecard


def _data(log):
    return {
        "years": {"2024": {"revenue_gbp": 1.0, "avg_clarity": 0.9, "active_customer_ids": ["C1"]}},
        "demand_estimation_log": log,
    }


def _info_check(log):
    sc = populate_compliance_scorecard(_data(log))
    return sc.latest_check(ComplianceDomain.INFORMATION_TRANSPARENCY)


def _row(err):
    return {"customer_id": "C1", "term_start": "2024-04-01", "error_pct": err}


def test_an_ungraded_estimate_is_excluded_from_the_mean_not_counted_as_zero():
    check = _info_check([_row(30.0), _row(None)])
    # A zero substitution would give 15.0 and AMBER; the graded mean is 30.0 and RED.
    assert check.metric_value == 30.0
    assert check.status == RAGStatus.RED
    assert "1 not graded" in check.notes


def test_nothing_graded_is_unavailable_and_never_green():
    check = _info_check([_row(None), _row(None)])
    assert check.metric_value is None
    assert check.status != RAGStatus.GREEN
    assert "unavailable" in check.notes and "0 of 2" in check.notes


def test_the_graded_branch_can_be_green():
    # Control over the partition: the fail-closed arm must not swallow a real answer.
    check = _info_check([_row(4.0), _row(-6.0)])
    assert check.metric_value == 5.0 and check.status == RAGStatus.GREEN
