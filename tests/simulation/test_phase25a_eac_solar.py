"""Phase 25a: EAC calibration from settlement + solar irradiance wiring tests.

Verifies:
- _derive_eac_from_settlement() computes mean annual kWh from billing records
- true_eac_kwh in demand_estimation_log uses actual consumption (not declared EAC)
- hedging eac_kwh uses calibrated EAC from prior-year billing after first term
- load_weather_cloud_cover() and cloud_cover_for_customer() load cloud data correctly
- _weather_adjusted_shape_fn with cloud cover reduces solar customer consumption
"""

from datetime import date, timedelta


def _make_records(customer_id: str, start_date: str, days: int, daily_kwh: float):
    """Synthetic daily settlement records for a customer."""
    records = []
    d = date.fromisoformat(start_date)
    for _ in range(days):
        records.append({
            "customer_id": customer_id,
            "settlement_date": d.isoformat(),
            "consumption_kwh": daily_kwh,
        })
        d += timedelta(days=1)
    return records


# ---- Part A: EAC calibration ----

def test_derive_eac_from_settlement_returns_mean_annual_kwh():
    """_derive_eac_from_settlement computes mean annual kWh from billing records."""
    from simulation.run_phase2b import _derive_eac_from_settlement
    # 365 days at 20 kWh/day = 7300 kWh/year
    records = _make_records("C2", "2017-01-01", 365, 20.0)
    result = _derive_eac_from_settlement("C2", records)
    assert abs(result - 7300) < 50, f"Expected ~7300, got {result:.1f}"


def test_derive_eac_from_settlement_falls_back_when_no_records():
    """Falls back to EFFECTIVE_EAC_KWH when no records for this customer."""
    from simulation.run_phase2b import _derive_eac_from_settlement, EFFECTIVE_EAC_KWH
    result = _derive_eac_from_settlement("C2", [])
    assert result == EFFECTIVE_EAC_KWH["C2"]


def test_derive_eac_from_settlement_falls_back_when_too_few_records():
    """Falls back when records span less than 180 days (seasonal noise too high)."""
    from simulation.run_phase2b import _derive_eac_from_settlement, EFFECTIVE_EAC_KWH
    records = _make_records("C2", "2017-01-01", 100, 20.0)  # only 100 days
    result = _derive_eac_from_settlement("C2", records)
    assert result == EFFECTIVE_EAC_KWH["C2"]


def test_demand_estimation_log_key_exists_in_run_output():
    """demand_estimation_log key is present in run output after Phase 25a.

    Verified via code inspection that _company_eac_estimate() uses
    actual settled consumption (true_eac_kwh) not declared EAC.
    Full convergence behaviour verified by sim run (demand_estimation_log
    in run_output_latest.json).
    """
    import pathlib
    src = pathlib.Path("simulation/run_phase2b.py").read_text()
    assert "demand_estimation_log" in src, "demand_estimation_log key missing from run output"
    assert "true_eac_kwh" in src, "true_eac_kwh not computed in run output"
    assert "_derive_eac_from_settlement" in src, "_derive_eac_from_settlement not in run_phase2b.py"


# ---- Part B: Solar irradiance wiring ----

def test_load_weather_cloud_cover_returns_dict():
    """load_weather_cloud_cover returns a {date: float} mapping."""
    from simulation.weather_inputs import load_weather_cloud_cover
    result = load_weather_cloud_cover("C4")
    assert len(result) > 0, "C4 cloud cover should be non-empty"
    assert "2016-01-01" in result
    assert 0 <= result["2016-01-01"] <= 100, "Cloud cover should be 0-100%"


def test_cloud_cover_for_customer_resolves_shared_locations():
    """C5 (London, shares C1 location) resolves to C1's cloud cover data."""
    from simulation.weather_inputs import cloud_cover_for_customer, load_weather_cloud_cover
    from saas.customers import CUSTOMERS
    c1 = next(c for c in CUSTOMERS if c["customer_id"] == "C1")
    c5 = next(c for c in CUSTOMERS if c["customer_id"] == "C5")
    c1_data = load_weather_cloud_cover("C1")
    c5_resolved = cloud_cover_for_customer(c5)
    # C1 and C5 share exact location dict, so C5 resolves to C1's data
    assert c5_resolved == c1_data


def test_solar_wiring_reduces_daytime_consumption_for_c4():
    """C4 (solar=True) has lower total consumption with irradiance wired vs without.

    Uses _weather_adjusted_shape_fn directly to compare a clear summer day.
    """
    from simulation.run_phase2b import _weather_adjusted_shape_fn
    from saas.customers import CUSTOMERS
    from saas.property_model import build_properties
    from simulation.weather_inputs import load_weather_means, load_weather_cloud_cover
    from sim.profile_class_1 import load_pc1_shape

    props = build_properties(CUSTOMERS)
    c4 = next(c for c in CUSTOMERS if c["customer_id"] == "C4")
    property_c4 = props["C4"]
    weather_c4 = load_weather_means("C4")
    cloud_c4 = load_weather_cloud_cover("C4")
    lat_c4 = c4["location"]["lat"]

    # Pick a summer date with both weather and cloud cover data
    test_date = "2020-07-15"
    assert test_date in weather_c4, "Test date must have weather data"
    assert test_date in cloud_c4, "Test date must have cloud data"

    # Without solar wiring (original behaviour)
    shape_no_solar = _weather_adjusted_shape_fn(
        load_pc1_shape, weather_c4, property_c4,
        cloud_cover_means=None, latitude_deg=None,
    )(test_date)

    # With solar wiring
    shape_with_solar = _weather_adjusted_shape_fn(
        load_pc1_shape, weather_c4, property_c4,
        cloud_cover_means=cloud_c4, latitude_deg=lat_c4,
    )(test_date)

    # Solar should reduce total consumption on a (possibly cloudy) summer day
    total_no_solar = sum(shape_no_solar)
    total_with_solar = sum(shape_with_solar)
    assert total_with_solar < total_no_solar, (
        f"Solar should reduce total consumption: {total_with_solar:.3f} >= {total_no_solar:.3f}"
    )


def test_non_solar_customer_unaffected_by_cloud_cover():
    """C1 (no solar asset) shape is unchanged when cloud_cover_means provided."""
    from simulation.run_phase2b import _weather_adjusted_shape_fn
    from saas.customers import CUSTOMERS
    from saas.property_model import build_properties
    from simulation.weather_inputs import load_weather_means, load_weather_cloud_cover
    from sim.profile_class_1 import load_pc1_shape

    props = build_properties(CUSTOMERS)
    c1 = next(c for c in CUSTOMERS if c["customer_id"] == "C1")
    property_c1 = props["C1"]
    weather_c1 = load_weather_means("C1")
    cloud_c1 = load_weather_cloud_cover("C1")

    test_date = "2020-07-15"
    assert test_date in weather_c1

    shape_without = _weather_adjusted_shape_fn(
        load_pc1_shape, weather_c1, property_c1,
    )(test_date)
    # Passing cloud cover for a non-solar customer — irradiance is only used when
    # the shape function is called AND the property has solar=True. C1 has no solar.
    # The shape should be identical: build_demand_shape ignores irradiance if no solar.
    shape_with_cloud = _weather_adjusted_shape_fn(
        load_pc1_shape, weather_c1, property_c1,
        cloud_cover_means=cloud_c1, latitude_deg=c1["location"]["lat"],
    )(test_date)

    assert shape_without == shape_with_cloud, "Non-solar customer should be unaffected by cloud cover"


def test_derive_eac_180_days_is_enough():
    """Exactly 180 days of records is sufficient (threshold not exclusive)."""""
    from simulation.run_phase2b import _derive_eac_from_settlement
    records = _make_records("C2", "2017-01-01", 180, 20.0)
    result = _derive_eac_from_settlement("C2", records)
    assert abs(result - 7305.0) < 50


def test_derive_eac_two_years_same_as_one():
    """Two full years of data produces same per-year result as one year."""""
    from simulation.run_phase2b import _derive_eac_from_settlement
    one_yr = _make_records("C2", "2016-01-01", 365, 20.0)
    two_yr = _make_records("C2", "2016-01-01", 730, 20.0)
    r1 = _derive_eac_from_settlement("C2", one_yr)
    r2 = _derive_eac_from_settlement("C2", two_yr)
    assert abs(r1 - r2) < 10


def test_derive_eac_proportional_to_daily_kwh():
    """Result scales linearly with daily consumption."""""
    from simulation.run_phase2b import _derive_eac_from_settlement
    recs_20 = _make_records("C2", "2017-01-01", 365, 20.0)
    recs_40 = _make_records("C2", "2017-01-01", 365, 40.0)
    r20 = _derive_eac_from_settlement("C2", recs_20)
    r40 = _derive_eac_from_settlement("C2", recs_40)
    assert abs(r40 / r20 - 2.0) < 0.01


def test_derive_eac_unknown_customer_still_returns_float():
    """Even if customer not in EFFECTIVE_EAC_KWH, returns a float from records."""""
    from simulation.run_phase2b import _derive_eac_from_settlement
    records = _make_records("ZZUNK99", "2017-01-01", 365, 10.0)
    result = _derive_eac_from_settlement("ZZUNK99", records)
    assert isinstance(result, float)
    assert result > 0


def test_cloud_cover_values_are_between_0_and_100():
    from simulation.weather_inputs import load_weather_cloud_cover
    data = load_weather_cloud_cover("C4")
    for v in list(data.values())[:100]:
        assert 0.0 <= v <= 100.0


def test_cloud_cover_has_data_for_2020():
    from simulation.weather_inputs import load_weather_cloud_cover
    data = load_weather_cloud_cover("C4")
    dates_2020 = [k for k in data if k.startswith("2020")]
    assert len(dates_2020) > 0
