from saas.customer_reaction import score_experience_signals


def _record(customer_id, settlement_date, revenue_gbp, wholesale_cost_gbp):
    return {
        "customer_id": customer_id,
        "settlement_date": settlement_date,
        "revenue_gbp": revenue_gbp,
        "wholesale_cost_gbp": wholesale_cost_gbp,
    }


def test_first_period_has_no_rolling_avg_or_expectation_gap():
    records = [_record("C1", "2016-01-15", 100.0, 80.0)]
    signals = score_experience_signals(records)

    period = signals["C1"][0]
    assert period["billing_period"] == "2016-01"
    assert period["actual_bill_gbp"] == 100.0
    assert period["actual_cost_gbp"] == 80.0
    assert period["rolling_avg_gbp"] is None
    assert period["bill_shock_score"] is None
    assert period["bill_shock_triggered"] is False
    assert period["expected_bill_gbp"] is None
    assert period["expectation_gap_gbp"] is None
    assert period["cumulative_exposure_gbp"] == -20.0


def test_bill_shock_triggers_above_threshold():
    records = [
        _record("C1", "2016-01-01", 100.0, 80.0),
        _record("C1", "2016-02-01", 100.0, 80.0),
        # 50% jump should trigger (> 0.15)
        _record("C1", "2016-03-01", 150.0, 80.0),
    ]
    signals = score_experience_signals(records)

    march = signals["C1"][2]
    assert march["rolling_avg_gbp"] == 100.0
    assert march["bill_shock_score"] == 0.5
    assert march["bill_shock_triggered"] is True


def test_bill_shock_does_not_trigger_below_threshold():
    records = [
        _record("C1", "2016-01-01", 100.0, 80.0),
        # 10% jump should not trigger (<= 0.15)
        _record("C1", "2016-02-01", 110.0, 80.0),
    ]
    signals = score_experience_signals(records)

    feb = signals["C1"][1]
    assert feb["bill_shock_score"] == 0.1
    assert feb["bill_shock_triggered"] is False


def test_rolling_avg_uses_window_of_prior_periods_only():
    records = [
        _record("C1", "2016-01-01", 100.0, 0.0),
        _record("C1", "2016-02-01", 200.0, 0.0),
        _record("C1", "2016-03-01", 300.0, 0.0),
        _record("C1", "2016-04-01", 400.0, 0.0),
        _record("C1", "2016-05-01", 500.0, 0.0),
        _record("C1", "2016-06-01", 600.0, 0.0),
        _record("C1", "2016-07-01", 700.0, 0.0),
    ]
    signals = score_experience_signals(records, rolling_window=6)

    # July (8th period would be excluded) sees the average of Jan-Jun (1..6)
    july = signals["C1"][6]
    assert july["rolling_avg_gbp"] == sum(range(100, 700, 100)) / 6


def test_expectation_gap_uses_previous_bill_times_1_02():
    records = [
        _record("C1", "2016-01-01", 100.0, 0.0),
        _record("C1", "2016-02-01", 105.0, 0.0),
    ]
    signals = score_experience_signals(records)

    feb = signals["C1"][1]
    assert feb["expected_bill_gbp"] == 102.0
    assert feb["expectation_gap_gbp"] == 3.0


def test_cumulative_exposure_accumulates_across_periods():
    records = [
        _record("C1", "2016-01-01", 100.0, 110.0),  # under-recovered by 10
        _record("C1", "2016-02-01", 100.0, 120.0),  # under-recovered by 20
    ]
    signals = score_experience_signals(records)

    assert signals["C1"][0]["cumulative_exposure_gbp"] == 10.0
    assert signals["C1"][1]["cumulative_exposure_gbp"] == 30.0


def test_multiple_records_in_one_billing_period_are_summed():
    records = [
        _record("C1", "2016-01-01", 50.0, 40.0),
        _record("C1", "2016-01-15", 50.0, 40.0),
    ]
    signals = score_experience_signals(records)

    assert len(signals["C1"]) == 1
    assert signals["C1"][0]["actual_bill_gbp"] == 100.0
    assert signals["C1"][0]["actual_cost_gbp"] == 80.0


def test_dual_fuel_legs_are_combined_into_one_bill():
    records = [
        _record("C1", "2016-01-01", 60.0, 50.0),
        _record("C1g", "2016-01-15", 40.0, 30.0),
        _record("C2", "2016-01-01", 90.0, 70.0),
    ]
    signals = score_experience_signals(records)

    assert "C1g" not in signals
    assert signals["C1"][0]["actual_bill_gbp"] == 100.0
    assert signals["C1"][0]["actual_cost_gbp"] == 80.0
    assert signals["C2"][0]["actual_bill_gbp"] == 90.0


def test_customers_are_independent():
    records = [
        _record("C1", "2016-01-01", 100.0, 80.0),
        _record("C2", "2016-01-01", 200.0, 150.0),
    ]
    signals = score_experience_signals(records)

    assert set(signals.keys()) == {"C1", "C2"}
    assert signals["C1"][0]["actual_bill_gbp"] == 100.0
    assert signals["C2"][0]["actual_bill_gbp"] == 200.0


from saas.customer_reaction import _billing_account_id


def test_billing_account_id_strips_gas_suffix():
    assert _billing_account_id("C1g") == "C1"


def test_billing_account_id_no_suffix():
    assert _billing_account_id("C1") == "C1"


def test_billing_account_id_ic_gas_suffix():
    assert _billing_account_id("C_IC3g") == "C_IC3"


def test_billing_account_id_single_char_g():
    # 'g' alone should not be stripped (len == 1)
    assert _billing_account_id("g") == "g"


def test_billing_account_id_c5_electricity():
    assert _billing_account_id("C5") == "C5"
