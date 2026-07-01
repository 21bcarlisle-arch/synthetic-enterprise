from sim.generation_demand_history import (
    aggregate_renewable_generation,
    aggregate_wind_generation,
)

_RECORDS = [
    {"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Wind Onshore", "quantity": 100.0},
    {"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Wind Offshore", "quantity": 200.0},
    {"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Solar", "quantity": 50.0},
    {"settlementDate": "2024-01-01", "settlementPeriod": 2, "psrType": "Wind Onshore", "quantity": 10.0},
    {"settlementDate": "2024-01-01", "settlementPeriod": 2, "psrType": "Solar", "quantity": 5.0},
]


def test_aggregate_renewable_generation_sums_all_psr_types():
    totals = aggregate_renewable_generation(_RECORDS)
    assert totals[("2024-01-01", 1)] == 350.0
    assert totals[("2024-01-01", 2)] == 15.0


def test_aggregate_wind_generation_excludes_solar():
    totals = aggregate_wind_generation(_RECORDS)
    assert totals[("2024-01-01", 1)] == 300.0
    assert totals[("2024-01-01", 2)] == 10.0


def test_aggregate_renewable_empty():
    assert aggregate_renewable_generation([]) == {}


def test_aggregate_renewable_single_record():
    records = [{"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Solar", "quantity": 42.0}]
    result = aggregate_renewable_generation(records)
    assert result == {("2024-01-01", 1): 42.0}


def test_aggregate_renewable_two_different_keys():
    records = [
        {"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Solar", "quantity": 10.0},
        {"settlementDate": "2024-01-01", "settlementPeriod": 2, "psrType": "Solar", "quantity": 20.0},
    ]
    result = aggregate_renewable_generation(records)
    assert len(result) == 2
    assert result[("2024-01-01", 1)] == 10.0
    assert result[("2024-01-01", 2)] == 20.0


def test_aggregate_renewable_key_is_tuple_of_date_and_period():
    records = [{"settlementDate": "2024-06-15", "settlementPeriod": 24, "psrType": "Wind Onshore", "quantity": 5.0}]
    result = aggregate_renewable_generation(records)
    key = ("2024-06-15", 24)
    assert key in result


def test_aggregate_wind_empty():
    assert aggregate_wind_generation([]) == {}


def test_aggregate_wind_solar_only_returns_empty():
    records = [{"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Solar", "quantity": 100.0}]
    assert aggregate_wind_generation(records) == {}


def test_aggregate_wind_onshore_only():
    records = [{"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Wind Onshore", "quantity": 150.0}]
    result = aggregate_wind_generation(records)
    assert result[("2024-01-01", 1)] == 150.0


def test_aggregate_wind_offshore_only():
    records = [{"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Wind Offshore", "quantity": 200.0}]
    result = aggregate_wind_generation(records)
    assert result[("2024-01-01", 1)] == 200.0


def test_aggregate_wind_excludes_unknown_psr_type():
    records = [
        {"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Hydro Run-of-river", "quantity": 50.0},
        {"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Wind Onshore", "quantity": 30.0},
    ]
    result = aggregate_wind_generation(records)
    assert result[("2024-01-01", 1)] == 30.0


def test_aggregate_wind_multiple_periods_independent():
    records = [
        {"settlementDate": "2024-01-01", "settlementPeriod": 1, "psrType": "Wind Onshore", "quantity": 100.0},
        {"settlementDate": "2024-01-01", "settlementPeriod": 2, "psrType": "Wind Offshore", "quantity": 200.0},
    ]
    result = aggregate_wind_generation(records)
    assert result[("2024-01-01", 1)] == 100.0
    assert result[("2024-01-01", 2)] == 200.0


# 13. Aggregate renewable includes wind and solar
def test_aggregate_includes_solar():
    totals = aggregate_renewable_generation(_RECORDS)
    # SP1 has wind+solar = 350
    assert totals[("2024-01-01", 1)] == 350.0


# 14. Aggregate wind excludes solar
def test_aggregate_wind_excludes_solar():
    totals = aggregate_wind_generation(_RECORDS)
    # SP1 wind = 100 + 200 = 300 (no solar)
    assert totals[("2024-01-01", 1)] == 300.0


# 15. Empty input returns empty dict
def test_aggregate_renewable_empty():
    totals = aggregate_renewable_generation([])
    assert totals == {}
