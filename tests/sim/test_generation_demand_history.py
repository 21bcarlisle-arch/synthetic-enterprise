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
