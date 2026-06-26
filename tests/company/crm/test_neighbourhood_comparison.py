import pytest
from company.crm.neighbourhood_comparison import (
    ConsumptionRating, NeighbourhoodComparison, build_neighbourhood_comparison
)


SAMPLE = [2000, 2200, 2500, 2800, 3000, 3200, 3500, 3800, 4200, 4800]


def test_build_basic():
    c = build_neighbourhood_comparison('C001', 'SW1', 'semi_detached', 2, 3500.0, SAMPLE)
    assert c.neighbour_count == 10
    assert c.neighbour_median_kwh == 3200.0


def test_vs_median_pct_higher():
    c = build_neighbourhood_comparison('C002', 'E1', 'terraced', 3, 4200.0, SAMPLE)
    assert c.vs_median_pct == pytest.approx(31.2)


def test_vs_median_pct_lower():
    c = build_neighbourhood_comparison('C003', 'E1', 'terraced', 1, 2000.0, SAMPLE)
    assert c.vs_median_pct < 0


def test_rating_much_higher():
    c = build_neighbourhood_comparison('C004', 'N1', 'detached', 4, 4500.0, SAMPLE)
    assert c.consumption_rating == ConsumptionRating.MUCH_HIGHER


def test_rating_similar():
    c = build_neighbourhood_comparison('C005', 'N1', 'semi_detached', 2, 3050.0, SAMPLE)
    assert c.consumption_rating == ConsumptionRating.SIMILAR


def test_rating_much_lower():
    c = build_neighbourhood_comparison('C006', 'W2', 'flat', 1, 1800.0, SAMPLE)
    assert c.consumption_rating == ConsumptionRating.MUCH_LOWER


def test_potential_saving_kwh():
    c = build_neighbourhood_comparison('C007', 'W2', 'terraced', 2, 4000.0, SAMPLE)
    assert c.potential_saving_kwh > 0


def test_no_saving_if_below_efficient():
    c = build_neighbourhood_comparison('C008', 'W2', 'flat', 1, 1800.0, SAMPLE)
    assert c.potential_saving_kwh == 0.0


def test_empty_sample_raises():
    with pytest.raises(ValueError):
        build_neighbourhood_comparison('C009', 'EC1', 'flat', 1, 3000.0, [])


def test_summary_keys():
    c = build_neighbourhood_comparison('C010', 'SE1', 'terraced', 2, 3200.0, SAMPLE)
    s = c.summary()
    assert 'consumption_rating' in s
    assert 'potential_saving_kwh' in s
    assert 'vs_median_pct' in s
