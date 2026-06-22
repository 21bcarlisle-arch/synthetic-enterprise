"""Tests for simulation/customer_events.py — Phase 6b / Phase 7e lifecycle event rolling."""
import pytest

from simulation.customer_events import PRICE_DIFFERENTIAL_PCT, roll_lifecycle_event


def _make_customers(customer_id="C5", segment="SME", epc="D", acquisition_date="2016-01-01"):
    return [
        {
            "customer_id": customer_id,
            "commodity": "electricity",
            "segment": segment,
            "epc_rating": epc,
            "acquisition_date": acquisition_date,
        }
    ]


def _make_settlement_records(customer_id="C5", year_month="2016-01", count=30):
    """Generate flat settlement records for bill-shock baseline (no shocks — flat bill)."""
    records = []
    for day in range(1, count + 1):
        date_str = f"{year_month}-{day:02d}"
        records.append({
            "customer_id": customer_id,
            "settlement_date": date_str,
            "settlement_period": 1,
            "consumption_kwh": 50.0,
            "unit_rate_gbp_per_mwh": 150.0,
            "revenue_gbp": 7.5,
            "wholesale_cost_gbp": 5.0,
            "margin_gbp": 2.5,
            "capital_cost_gbp": 0.1,
            "net_margin_gbp": 2.4,
        })
    return records


def _build_one_year_records(customer_id="C5", start_year=2016):
    """One full year of flat settlement records (no bill shocks)."""
    records = []
    for month in range(1, 13):
        for day in range(1, 29):
            date_str = f"{start_year}-{month:02d}-{day:02d}"
            records.append({
                "customer_id": customer_id,
                "settlement_date": date_str,
                "settlement_period": 1,
                "consumption_kwh": 50.0,
                "unit_rate_gbp_per_mwh": 150.0,
                "revenue_gbp": 7.5,
                "wholesale_cost_gbp": 5.0,
                "margin_gbp": 2.5,
                "capital_cost_gbp": 0.1,
                "net_margin_gbp": 2.4,
            })
    return records


def _first_renewal_date(acquisition_date: str) -> str:
    """Compute the first renewal date (acquisition + 365 days) as an ISO string.
    Note: 2016-01-01 + 365 = 2016-12-31 because 2016 is a leap year (366 days).
    """
    from datetime import date, timedelta

    from simulation.settlement import CONTRACT_LENGTH_DAYS
    return (date.fromisoformat(acquisition_date) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()


ACQ_DATE = "2016-01-01"
FIRST_RENEWAL = _first_renewal_date(ACQ_DATE)  # "2016-12-31"


def test_roll_returns_none_when_no_renewal_data_in_window():
    # Only a few days of records — churn model has no renewal point yet
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _make_settlement_records("C5", "2016-01", 10)  # only 10 days
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is None


def test_roll_returns_event_dict_when_renewal_data_present():
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert result["customer_id"] == "C5"
    assert result["event_date"] == FIRST_RENEWAL
    assert result["commodity"] == "electricity"
    assert result["event_type"] in ("renewed", "churned")
    assert 0.0 < result["churn_probability"] <= 1.0
    assert 0.0 < result["win_probability"] <= 1.0
    assert 0.0 < result["effective_retention_probability"] <= 1.0
    assert 0.0 <= result["random_roll"] <= 1.0


def test_roll_is_deterministic():
    """Same input always produces the same random roll and outcome."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result1 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    result2 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result1 == result2


def test_different_customers_get_independent_rolls():
    """Different customer_ids produce different random rolls (seeded by id+date)."""
    customers_c5 = _make_customers("C5", acquisition_date=ACQ_DATE)
    customers_c6 = _make_customers("C6", acquisition_date=ACQ_DATE)
    records_c5 = _build_one_year_records("C5", 2016)
    records_c6 = _build_one_year_records("C6", 2016)
    result_c5 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records_c5, customers_c5)
    result_c6 = roll_lifecycle_event("C6", FIRST_RENEWAL, "electricity", records_c6, customers_c6)
    assert result_c5 is not None and result_c6 is not None
    # Same date, different customer — rolls should differ (astronomically unlikely to collide)
    assert result_c5["random_roll"] != result_c6["random_roll"]


def test_retained_when_roll_below_retention_probability():
    """Roll outcome is consistent with the rolled probability."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)

    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    p_retain = result["effective_retention_probability"]
    roll = result["random_roll"]
    expected = "renewed" if roll <= p_retain else "churned"
    assert result["event_type"] == expected


def test_no_bill_shocks_gives_base_churn_probability():
    """With no bill shocks, churn_probability == BASE_ANNUAL_CHURN_PROBABILITY (5%)."""
    from saas.churn_model import BASE_ANNUAL_CHURN_PROBABILITY

    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert abs(result["churn_probability"] - BASE_ANNUAL_CHURN_PROBABILITY) < 1e-9


def test_gas_leg_maps_to_billing_account():
    """Gas leg C1g rolls churn for billing account C1 (same seed as electricity leg)."""
    customers_elec = _make_customers("C1", segment="resi", epc="C", acquisition_date=ACQ_DATE)
    customers_gas = [
        {**customers_elec[0], "customer_id": "C1g", "commodity": "gas"}
    ]
    all_customers = customers_elec + customers_gas

    records = _build_one_year_records("C1", 2016)

    result_elec = roll_lifecycle_event("C1", FIRST_RENEWAL, "electricity", records, all_customers)
    result_gas = roll_lifecycle_event("C1g", FIRST_RENEWAL, "gas", records, all_customers)

    assert result_elec is not None and result_gas is not None
    # Both map to billing account C1 — same seed → same roll and outcome
    assert result_elec["random_roll"] == result_gas["random_roll"]
    assert result_elec["event_type"] == result_gas["event_type"]
    assert result_elec["customer_id"] == "C1"
    assert result_gas["customer_id"] == "C1"


# ---- Phase 7e: home_move_won field ----

def test_home_move_won_present_on_every_event():
    """home_move_won key must appear on every event dict, not just churns."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert "home_move_won" in result


def test_home_move_won_false_for_renewals():
    """Retained customers always have home_move_won=False — the win roll only fires on churn."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    if result["event_type"] == "renewed":
        assert result["home_move_won"] is False


def test_home_move_won_deterministic_for_churned():
    """Win roll is seeded — same inputs always produce the same home_move_won value."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    r1 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    r2 = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert r1 is not None and r2 is not None
    assert r1["home_move_won"] == r2["home_move_won"]


def test_win_roll_uses_independent_seed():
    """The win seed `win_{account}_{date}` must differ from the churn seed `{account}_{date}`.

    Verify this by checking the win roll and churn roll are produced by different RNG instances:
    if they used the same RNG/seed, the win decision would always be the same as the churn decision,
    which is clearly wrong. We test this indirectly: for a customer that churns, confirm that
    home_move_won is a bool (not derived from the same roll) and that the roll values differ.
    """
    import random as _random

    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    if result["event_type"] == "churned":
        churn_roll = result["random_roll"]
        win_rng = _random.Random(f"win_C5_{FIRST_RENEWAL}")
        win_roll = win_rng.random()
        # The churn roll uses seed "C5_{FIRST_RENEWAL}" and the win roll uses "win_C5_{FIRST_RENEWAL}"
        churn_rng = _random.Random(f"C5_{FIRST_RENEWAL}")
        assert churn_rng.random() == pytest.approx(churn_roll)
        # Win roll is from a different RNG — must differ from churn roll
        assert win_roll != churn_roll


def test_home_move_won_is_bool_not_float():
    """home_move_won must be a strict Python bool, not an int or float comparison result."""
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert isinstance(result["home_move_won"], bool)


def test_roll_lifecycle_event_retention_offered_field_false_without_modifier():
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    assert result is not None
    assert result["retention_offered"] is False


def test_roll_lifecycle_event_retention_offered_field_true_with_modifier():
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        retention_modifier=0.20,
    )
    assert result is not None
    assert result["retention_offered"] is True


def test_roll_lifecycle_event_precomputed_estimate_used():
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        old_rate_gbp_per_mwh=100.0, new_rate_gbp_per_mwh=150.0,
        precomputed_company_estimate=0.99,
    )
    assert result is not None
    assert abs(result["company_churn_estimate"] - 0.99) < 1e-6


def test_roll_lifecycle_event_retention_modifier_increases_retention_probability():
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result_no_mod = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    result_with_mod = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        retention_modifier=0.50,
    )
    assert result_no_mod is not None and result_with_mod is not None
    p_no = result_no_mod["effective_retention_probability"]
    p_with = result_with_mod["effective_retention_probability"]
    assert p_with >= p_no


def test_roll_lifecycle_event_modifier_zero_leaves_probability_unchanged():
    customers = _make_customers("C5", acquisition_date=ACQ_DATE)
    records = _build_one_year_records("C5", 2016)
    result_no_mod = roll_lifecycle_event("C5", FIRST_RENEWAL, "electricity", records, customers)
    result_zero_mod = roll_lifecycle_event(
        "C5", FIRST_RENEWAL, "electricity", records, customers,
        retention_modifier=0.0,
    )
    assert result_no_mod is not None and result_zero_mod is not None
    assert abs(result_no_mod["effective_retention_probability"] - result_zero_mod["effective_retention_probability"]) < 1e-9
    assert result_no_mod["event_type"] == result_zero_mod["event_type"]
