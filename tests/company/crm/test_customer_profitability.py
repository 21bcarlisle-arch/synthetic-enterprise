import pytest
from company.crm.customer_profitability import (
    estimate_prior_term_net_margin,
    compute_profitability_uplift,
    NET_NEGATIVE_UPLIFT_GBP_PER_MWH,
    MIN_RECORDS_FOR_JUDGEMENT,
)


def _records(cid, n, net_margin=10.0, term_start="2021-01-01", settlement_date="2021-06-01", commodity="electricity"):
    return [
        {
            "customer_id": cid,
            "settlement_date": settlement_date,
            "term_start": term_start,
            "net_margin_gbp": net_margin,
            "commodity": commodity,
        }
        for _ in range(n)
    ]


class TestEstimatePriorTermNetMargin:
    def test_none_when_no_records(self):
        result = estimate_prior_term_net_margin("C1", "2022-01-01", [])
        assert result is None

    def test_none_when_fewer_than_min_records(self):
        recs = _records("C1", n=MIN_RECORDS_FOR_JUDGEMENT - 1, settlement_date="2021-06-01")
        result = estimate_prior_term_net_margin("C1", "2022-01-01", recs)
        assert result is None

    def test_returns_sum_of_margin_when_sufficient_records(self):
        recs = _records("C1", n=MIN_RECORDS_FOR_JUDGEMENT, net_margin=5.0, settlement_date="2021-06-01")
        result = estimate_prior_term_net_margin("C1", "2022-01-01", recs)
        assert result == pytest.approx(5.0 * MIN_RECORDS_FOR_JUDGEMENT)

    def test_filters_by_customer_id(self):
        recs = _records("C2", n=MIN_RECORDS_FOR_JUDGEMENT, settlement_date="2021-06-01")
        result = estimate_prior_term_net_margin("C1", "2022-01-01", recs)
        assert result is None

    def test_only_electricity_records(self):
        # Gas records should be excluded
        recs = _records("C1", n=MIN_RECORDS_FOR_JUDGEMENT, commodity="gas", settlement_date="2021-06-01")
        result = estimate_prior_term_net_margin("C1", "2022-01-01", recs)
        assert result is None

    def test_only_records_before_term_start(self):
        # Records with settlement_date >= term_start should be excluded
        recs = _records("C1", n=MIN_RECORDS_FOR_JUDGEMENT, settlement_date="2022-06-01")
        result = estimate_prior_term_net_margin("C1", "2022-01-01", recs)
        assert result is None

    def test_negative_net_margin(self):
        recs = _records("C1", n=MIN_RECORDS_FOR_JUDGEMENT, net_margin=-2.0, settlement_date="2021-06-01")
        result = estimate_prior_term_net_margin("C1", "2022-01-01", recs)
        assert result < 0


class TestComputeProfitabilityUplift:
    def test_zero_when_insufficient_history(self):
        uplift = compute_profitability_uplift("C1", "2022-01-01", [])
        assert uplift == 0.0

    def test_uplift_when_prior_term_negative(self):
        recs = _records("C1", n=MIN_RECORDS_FOR_JUDGEMENT, net_margin=-5.0, settlement_date="2021-06-01")
        uplift = compute_profitability_uplift("C1", "2022-01-01", recs)
        assert uplift == pytest.approx(NET_NEGATIVE_UPLIFT_GBP_PER_MWH)

    def test_zero_when_prior_term_positive(self):
        recs = _records("C1", n=MIN_RECORDS_FOR_JUDGEMENT, net_margin=20.0, settlement_date="2021-06-01")
        uplift = compute_profitability_uplift("C1", "2022-01-01", recs)
        assert uplift == 0.0
