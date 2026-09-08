"""W2_30 gas half: each household's seasonal gas shape is its OWN, and it moves the
shape without moving the level.

Every test here names the defect it fires on. The defect being removed is that
`gas_settlement` hands every domestic customer the same 70/30 split, so two homes at the
same AQ have identical seasonal shapes to every decimal place.
"""

import math

import pytest

from simulation.gas_settlement import (
    _GAS_BOILER_HEATING_FRACTION,
    GAS_HDD_REFERENCE_ANNUAL,
    resi_daily_gas_kwh,
)
from simulation.household_demand_shape import (
    MIN_DAYS_FOR_FIT,
    MIN_HDD_SPREAD_FOR_IDENTIFIABILITY,
    NOT_VALIDATED_STATEMENT,
    SeasonalGasRefusal,
    SeasonalGasSplit,
    every_split_declares_it_is_not_validated,
    level_is_preserved,
    population_spread_is_material,
    seasonal_gas_split,
    seasonal_gas_splits_for_book,
)


#: A reference year of daily HDD that sums to the settlement reference, so
#: `level_is_preserved` is defined against it. Built by spreading each reference month's
#: HDD evenly across its days -- the same construction `sim.weather_hdd.get_hdd` falls
#: back to when a day has no recorded temperature.
def _reference_year_hdd() -> list[float]:
    from calendar import monthrange

    from sim.weather_hdd import REFERENCE_MONTHLY_HDD

    days = []
    for month in range(1, 13):
        n = monthrange(2021, month)[1]
        days.extend([REFERENCE_MONTHLY_HDD[month] / n] * n)
    # Rescale so the year sums to the reference exactly (month lengths are not 30).
    total = sum(days)
    return [d * GAS_HDD_REFERENCE_ANNUAL / total for d in days]


def _series_at(fraction: float, aq_kwh: float = 12000.0) -> tuple[list[float], list[float]]:
    """A household whose daily gas IS the two-term form at a known heating fraction.
    Recovering `fraction` from this is the fit's minimum obligation."""
    hdd = _reference_year_hdd()
    kwh = [resi_daily_gas_kwh(aq_kwh, h, heating_fraction=fraction) for h in hdd]
    return kwh, hdd


# ---------------------------------------------------------------------------
# The fit recovers what it should, and it is not pinned to today's answer
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fraction", [0.35, 0.55, 0.70, 0.85])
def test_the_fit_recovers_the_fraction_the_series_was_built_at(fraction):
    """Keyed to the PROPERTY, not to a number: whatever split a household's own physics
    implies, the fit returns THAT one. A fit hard-wired to the population 0.70 passes a
    single-value test and fails this one at 0.35."""
    kwh, hdd = _series_at(fraction)
    split = seasonal_gas_split("C1g", kwh, hdd)
    assert isinstance(split, SeasonalGasSplit)
    assert split.heating_fraction == pytest.approx(fraction, abs=1e-6)


def test_two_households_at_the_same_aq_get_different_fractions():
    """THE SHIPPED DEFECT. Under the population constant these two are byte-identical;
    the whole atom is that they should not be."""
    lossy, hdd = _series_at(0.85)
    tight, _ = _series_at(0.40)
    a = seasonal_gas_split("lossy", lossy, hdd)
    b = seasonal_gas_split("tight", tight, hdd)
    assert abs(a.heating_fraction - b.heating_fraction) > 0.4


# ---------------------------------------------------------------------------
# The refusals are real, and they name their reason
# ---------------------------------------------------------------------------


def test_a_window_with_no_cold_days_is_refused_rather_than_fitted():
    """Fires on the fabrication this module exists not to do: with no HDD spread the two
    terms are collinear and any fraction fits, so a returned number would be set by
    rounding noise."""
    hdd = [0.5] * 200
    kwh = [resi_daily_gas_kwh(12000.0, h, heating_fraction=0.7) for h in hdd]
    out = seasonal_gas_split("flat", kwh, hdd)
    assert isinstance(out, SeasonalGasRefusal)
    assert "HDD" in out.reason and str(MIN_HDD_SPREAD_FOR_IDENTIFIABILITY) in out.reason


def test_a_short_window_is_refused():
    kwh, hdd = _series_at(0.7)
    out = seasonal_gas_split("short", kwh[: MIN_DAYS_FOR_FIT - 1], hdd[: MIN_DAYS_FOR_FIT - 1])
    assert isinstance(out, SeasonalGasRefusal)
    assert str(MIN_DAYS_FOR_FIT) in out.reason


def test_gas_that_does_not_rise_with_cold_is_refused_not_given_a_zero_fraction():
    """A household whose gas falls as it gets colder has no space-heating term to find.
    Returning 0.0 would publish 'this home does no heating' as a measurement; refusing
    says we cannot tell, which is the honest result."""
    hdd = _reference_year_hdd()
    kwh = [20.0 - 0.5 * h for h in hdd]
    out = seasonal_gas_split("inverted", kwh, hdd)
    assert isinstance(out, SeasonalGasRefusal)
    assert "does not rise with cold" in out.reason


def test_mismatched_series_lengths_raise():
    kwh, hdd = _series_at(0.7)
    with pytest.raises(ValueError):
        seasonal_gas_split("bad", kwh, hdd[:-1])


# ---------------------------------------------------------------------------
# The level is preserved -- the property that makes the switch safe
# ---------------------------------------------------------------------------


def test_the_per_household_fraction_does_not_move_the_annual_volume():
    """`run_phase2b` refused the gas switch because driving gas from fabric while the AQ
    belief stayed frozen would lock in a hedge mismatch. This control is the reason that
    objection does not apply: at reference HDD the annual total is the AQ whatever the
    fraction is, so the shape moves and the level does not."""
    hdd = _reference_year_hdd()
    kwh, _ = _series_at(0.85)
    split = seasonal_gas_split("C1g", kwh, hdd)
    assert level_is_preserved(split, 12000.0, hdd)


def test_level_preservation_fires_when_the_two_terms_stop_scaling_together():
    """The control CAN fail: a split whose flat term no longer scales with the AQ moves
    the annual volume, and that is exactly the AQ mismatch. Constructed by handing the
    control a reference year that is not a reference year -- the one input that makes the
    two totals genuinely differ -- and it raises rather than passing vacuously."""
    hdd = _reference_year_hdd()
    kwh, _ = _series_at(0.85)
    split = seasonal_gas_split("C1g", kwh, hdd)
    warm_year = [h * 0.5 for h in hdd]
    with pytest.raises(ValueError, match="reference-HDD year"):
        level_is_preserved(split, 12000.0, warm_year)


def test_a_fraction_outside_the_unit_interval_is_refused_by_settlement():
    with pytest.raises(ValueError):
        resi_daily_gas_kwh(12000.0, 5.0, heating_fraction=1.4)


def test_the_default_fraction_is_the_shipped_population_constant():
    """The seam is a pure forward extension: a caller that passes nothing settles exactly
    as it did before this module existed."""
    for hdd in (0.0, 3.0, 11.3):
        assert resi_daily_gas_kwh(12000.0, hdd) == resi_daily_gas_kwh(
            12000.0, hdd, heating_fraction=_GAS_BOILER_HEATING_FRACTION
        )


# ---------------------------------------------------------------------------
# The book-level controls
# ---------------------------------------------------------------------------


def _book_of(fractions):
    kwh_hdd = {f"H{i}": _series_at(f) for i, f in enumerate(fractions)}
    customers = [{"customer_id": cid} for cid in kwh_hdd]
    splits, refusals = seasonal_gas_splits_for_book(
        customers=customers, daily_gas_series_for=lambda c: kwh_hdd[c["customer_id"]]
    )
    return splits, refusals


def test_a_book_of_identical_fractions_fires_the_spread_control():
    """POISON ROUND FIRST. The control must be able to fail before its pass means
    anything: a book where every household got the same fraction is the shipped defect,
    and `population_spread_is_material` says so."""
    splits, _ = _book_of([0.70] * 8)
    assert not population_spread_is_material(list(splits.values()))


def test_a_book_of_real_fractions_passes_the_spread_control():
    splits, _ = _book_of([0.35, 0.45, 0.55, 0.62, 0.70, 0.78, 0.85, 0.90])
    assert population_spread_is_material(list(splits.values()))


def test_the_spread_control_refuses_a_book_too_small_to_judge():
    splits, _ = _book_of([0.4, 0.6, 0.8])
    with pytest.raises(ValueError):
        population_spread_is_material(list(splits.values()))


def test_every_customer_lands_in_exactly_one_of_splits_or_refusals():
    """No silent absence: a household keeping the population constant is in the record
    with its reason, not missing from it."""
    kwh, hdd = _series_at(0.7)
    customers = [{"customer_id": "has"}, {"customer_id": "none"}]
    splits, refusals = seasonal_gas_splits_for_book(
        customers=customers,
        daily_gas_series_for=lambda c: (kwh, hdd) if c["customer_id"] == "has" else None,
    )
    assert set(splits) == {"has"}
    assert [r.customer_id for r in refusals] == ["none"]
    assert "no fabric trace" in refusals[0].reason


# ---------------------------------------------------------------------------
# The director decision
# ---------------------------------------------------------------------------


def test_no_split_can_ever_claim_it_was_validated():
    """Canon section 6 is a director decision, not a gap. There is no argument that sets
    this and no code path that returns True."""
    splits, _ = _book_of([0.4, 0.6, 0.8, 0.5, 0.7])
    assert every_split_declares_it_is_not_validated(list(splits.values()))
    assert all(not s.validated for s in splits.values())


def test_the_validation_control_refuses_an_empty_set():
    """A vacuous pass over nothing is exactly the reading this control must not give."""
    with pytest.raises(ValueError):
        every_split_declares_it_is_not_validated([])


def test_the_not_validated_statement_names_both_sources_and_says_the_level_is_unchanged():
    """It is a statement for a reader, not a footnote marker: it must say what was
    modelled, why nothing checked it, and what it does NOT change."""
    assert "NOT been validated" in NOT_VALIDATED_STATEMENT
    assert "Profile Class 1" in NOT_VALIDATED_STATEMENT
    assert "SERL" in NOT_VALIDATED_STATEMENT
    assert "unchanged" in NOT_VALIDATED_STATEMENT


def test_the_fit_reports_its_own_quality_rather_than_filtering_on_it():
    """R12: the fit statistic is a diagnostic. A household whose physics the two-term form
    describes badly is still returned, with the poor r-squared visible, rather than
    dropped so the book looks tidier."""
    hdd = _reference_year_hdd()
    kwh, _ = _series_at(0.7)
    noisy = [k * (1.0 + 0.4 * math.sin(i)) for i, k in enumerate(kwh)]
    split = seasonal_gas_split("noisy", noisy, hdd)
    assert isinstance(split, SeasonalGasSplit)
    assert split.fit_r_squared < 0.99
