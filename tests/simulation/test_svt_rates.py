"""Tests for Phase 39a SVT rate lookup, both fuels."""
from datetime import date as _date

import pytest

from simulation.svt_rates import (
    _SVT_GAS_PRECAP_PENCE_PER_KWH,
    get_svt_elec_rate_gbp_per_mwh,
    get_svt_gas_rate_gbp_per_mwh,
)


def test_returns_float_for_known_quarter():
    rate = get_svt_elec_rate_gbp_per_mwh("2024-04-01")
    assert isinstance(rate, float)
    assert rate > 0


def test_jan_2019_matches_ofgem_cap():
    # Ofgem cap Jan 2019: 16.52p/kWh = 165.2 £/MWh
    rate = get_svt_elec_rate_gbp_per_mwh("2019-01-15")
    assert abs(rate - 165.2) < 0.1


def test_oct_2022_reflects_crisis():
    # Energy crisis peak: 51.89p/kWh = 518.9 £/MWh
    rate = get_svt_elec_rate_gbp_per_mwh("2022-11-01")
    assert abs(rate - 518.9) < 1.0


def test_quarter_fallthrough_within_year():
    # March is in Q1 (Jan period)
    rate_jan = get_svt_elec_rate_gbp_per_mwh("2024-01-01")
    rate_mar = get_svt_elec_rate_gbp_per_mwh("2024-03-31")
    assert rate_jan == rate_mar


def test_quarter_boundary_april():
    # April period differs from January period
    rate_mar = get_svt_elec_rate_gbp_per_mwh("2024-03-31")
    rate_apr = get_svt_elec_rate_gbp_per_mwh("2024-04-01")
    # 2024 Q1: 27.4p → 274 £/MWh, Q2: 24.5p → 245 £/MWh
    assert rate_apr < rate_mar


def test_before_2016_returns_none():
    rate = get_svt_elec_rate_gbp_per_mwh("2015-12-31")
    assert rate is None


def test_2026_is_published_not_extrapolated():
    # Named `test_2026_extrapolated_returns_float` until 2026-09-08, when the extrapolation it was
    # named for was deleted: the commons publishes 2026 from Ofgem's cap level model v1.31.
    rate = get_svt_elec_rate_gbp_per_mwh("2026-06-01")
    assert isinstance(rate, float)
    assert rate > 0


def test_2029_carries_the_standing_instrument_forward():
    # Not an extrapolation: past the published schedule the last published level stands, which is
    # `price_cap_enforcement`'s rule and is asserted properly in
    # `test_the_elec_svt_leg_reads_the_commons.py`.
    rate = get_svt_elec_rate_gbp_per_mwh("2029-09-15")
    assert isinstance(rate, float)
    assert rate > 0


def test_gbp_per_mwh_unit_conversion():
    # Rate should be roughly 10× the p/kWh value
    # Jan 2025: 24.86p/kWh → 248.6 £/MWh
    rate = get_svt_elec_rate_gbp_per_mwh("2025-01-01")
    assert abs(rate - 248.6) < 0.5


def test_crisis_rate_much_higher_than_normal():
    rate_2020 = get_svt_elec_rate_gbp_per_mwh("2020-06-01")
    rate_2022_oct = get_svt_elec_rate_gbp_per_mwh("2022-11-01")
    assert rate_2022_oct > rate_2020 * 2.5


# `_quarter_start_month` and its eight tests were deleted on 2026-09-08. Their subject was the
# walk-back over a quarterly key table, and the table is gone: the electricity leg reads the
# published window boundaries from the commons, which are six-monthly to Sep-2022 and quarterly
# after, so a function that rounded a month to a quarter could not have expressed them. Kept as
# a note rather than silently: eight green tests disappearing is a thing a reader should be
# told the reason for.


def test_q1_2022_crisis_rate():
    rate = get_svt_elec_rate_gbp_per_mwh("2022-01-01")
    assert rate == pytest.approx(208.0)


def test_q3_2022_crisis_rate():
    rate = get_svt_elec_rate_gbp_per_mwh("2022-07-01")
    assert rate == pytest.approx(283.4)


def test_q4_2022_extreme_crisis_rate():
    rate = get_svt_elec_rate_gbp_per_mwh("2022-10-01")
    assert rate == pytest.approx(518.9)


def test_q1_2023_is_the_OFGEM_CAP_and_the_name_used_to_say_EPG():
    """674.7, the Ofgem cap for Jan-Mar 2023 -- NOT the 340.0 the EPG held the household's unit
    rate at. This test was called `test_q1_2023_epg_rate` and asserted 670.0, which is neither
    instrument: a transcription of the cap under the name of the other one. Both halves are fixed
    here, and `test_the_elec_svt_leg_reads_the_commons.py` is what keeps the choice deliberate.
    """
    from datetime import date as _d

    from simulation.price_cap_enforcement import ofgem_cap_unit_rate_gbp_per_mwh_inc_vat

    rate = get_svt_elec_rate_gbp_per_mwh("2023-01-01")
    assert rate == pytest.approx(674.7)
    assert rate == pytest.approx(
        ofgem_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", _d(2023, 1, 1))
    )


# ---------------------------------------------------------------------------
# GAS (2026-09-06). WHAT EACH TEST HERE NAMES AS ITS OWN DEFECT:
#
#   * `test_the_gas_series_is_NOT_the_electricity_series` — the defect the
#     replaced `run_phase2b` comment warned about and then caused by omission:
#     one fuel's cap standing in for the other's, so the spread published against
#     a gas unit rate is a difference between two commodities. It is also the
#     reachability control for this whole block: a `get_svt_gas_rate_gbp_per_mwh`
#     that simply forwards to the electricity accessor passes every other test
#     below.
#   * `test_gas_is_answerable_for_EVERY_year_of_the_record` — the defect that was
#     live: 449 of 2,098 account-state rows carried `svt_rate_gbp_per_mwh = None`
#     because this module had no gas leg, and `r1_inference_ceiling` published
#     146-of-164 as the field's own scope. A per-year sweep is what makes the
#     None state unreachable rather than merely unobserved.
#   * `test_the_post_cap_gas_leg_has_no_SECOND_home_in_this_module` — the defect
#     of restating a published series that already lives in the regulation
#     commons. Two homes for one number drift, and the drift is invisible because
#     both sides look sourced.
#   * `test_pre_cap_gas_sits_inside_the_PUBLISHED_band` — the defect of a
#     midpoint that has quietly moved off its source. Keyed to the range in
#     `docs/market_research/svt_rates_active_passive_2016_2025.md` §1, not to
#     today's answer.
# ---------------------------------------------------------------------------
#: `svt_rates_active_passive_2016_2025.md` §1, pre-cap table, p/kWh. The source
#: states these as ranges at M confidence; the module carries the midpoint.
_PUBLISHED_PRECAP_GAS_BAND_PENCE = {
    2016: (3.8, 4.2),
    2017: (2.1, 3.5),
    2018: (3.5, 4.0),
}

#: The years the world's own record spans (CLAUDE.md: "the 2016-2025 record is
#: what happened"). Every one of them must be answerable for gas.
_RECORD_YEARS = tuple(range(2016, 2026))


def test_the_gas_series_is_NOT_the_electricity_series():
    same = [
        y for y in _RECORD_YEARS
        if get_svt_gas_rate_gbp_per_mwh(f"{y}-04-01")
        == get_svt_elec_rate_gbp_per_mwh(f"{y}-04-01")
    ]
    assert not same, (
        f"gas and electricity return the same rate in {same} -- one fuel's cap is "
        "standing in for the other's"
    )
    # And gas is the CHEAPER fuel per kWh in every year of the published record,
    # which is the direction the source table shows throughout.
    for y in _RECORD_YEARS:
        gas = get_svt_gas_rate_gbp_per_mwh(f"{y}-04-01")
        elec = get_svt_elec_rate_gbp_per_mwh(f"{y}-04-01")
        assert gas < elec, f"{y}: gas {gas} is not below electricity {elec}"


def test_gas_is_answerable_for_EVERY_year_of_the_record():
    unanswered = [
        (y, q) for y in _RECORD_YEARS for q in (1, 4, 7, 10)
        if get_svt_gas_rate_gbp_per_mwh(f"{y}-{q:02d}-01") is None
    ]
    assert not unanswered, f"no gas rate for {unanswered}"


def test_gas_before_2016_is_None_exactly_as_electricity_is():
    assert get_svt_gas_rate_gbp_per_mwh("2015-12-31") is None
    assert get_svt_elec_rate_gbp_per_mwh("2015-12-31") is None


def test_the_post_cap_gas_leg_has_no_SECOND_home_in_this_module():
    assert set(_SVT_GAS_PRECAP_PENCE_PER_KWH) == {2016, 2017, 2018}, (
        "a post-2018 gas rate has been written into this module; the published "
        "cap lives in docs/domain_artefact_library/regulatory/"
        "ofgem_default_tariff_cap_windows.json and is read, never restated"
    )


def test_the_post_cap_gas_leg_IS_the_commons():
    """THE OFGEM CAP ROW since 2026-09-08. This asserted the BINDING instrument until then, and
    the electricity leg carried the cap, so the two fuels answered different questions across
    2022-10..2023-06 -- one field, two quantities, in the only three quarters where they differ.
    """
    from simulation.price_cap_enforcement import (
        ofgem_cap_unit_rate_gbp_per_mwh_inc_vat,
    )
    for y in range(2019, 2026):
        for q in (1, 4, 7, 10):
            d = f"{y}-{q:02d}-01"
            assert get_svt_gas_rate_gbp_per_mwh(d) == (
                ofgem_cap_unit_rate_gbp_per_mwh_inc_vat("gas", _date.fromisoformat(d))
            ), d


#: The ELECTRICITY column of the same §1 pre-cap table, p/kWh, same M confidence and same ±15%
#: caveat. Added 2026-09-08 with the band pin the gas leg already had: until then the electricity
#: pre-cap years were three values inside a 46-row quarter-keyed table, and a table keyed by tuples
#: is invisible to `tests/architecture/test_year_keyed_rate_table_census.py`, so nothing anywhere
#: held them against their source.
_PUBLISHED_PRECAP_ELEC_BAND_PENCE = {
    2016: (13.5, 14.5),
    2017: (13.5, 14.5),
    2018: (14.5, 16.0),
}


def test_pre_cap_elec_sits_inside_the_PUBLISHED_band():
    """DEFECT: a midpoint that has quietly moved off its source. The same control the gas leg
    carries, on the fuel whose pre-cap years had none.
    """
    for year, (low, high) in _PUBLISHED_PRECAP_ELEC_BAND_PENCE.items():
        pence = get_svt_elec_rate_gbp_per_mwh(f"{year}-06-01") / 10.0
        assert low <= pence <= high, (
            f"{year}: {pence}p/kWh is outside the published {low}-{high}p range"
        )


def test_pre_cap_gas_sits_inside_the_PUBLISHED_band():
    for year, (low, high) in _PUBLISHED_PRECAP_GAS_BAND_PENCE.items():
        pence = get_svt_gas_rate_gbp_per_mwh(f"{year}-06-01") / 10.0
        assert low <= pence <= high, (
            f"{year}: {pence}p/kWh is outside the published {low}-{high}p range"
        )


def test_gas_crisis_rate_is_far_above_the_pre_crisis_level():
    # The same property the electricity crisis test asserts, on the fuel that
    # CAUSED the crisis. Gas went from ~3p/kWh in 2020 to a capped double figure.
    assert (
        get_svt_gas_rate_gbp_per_mwh("2022-11-01")
        > get_svt_gas_rate_gbp_per_mwh("2020-06-01") * 2.5
    )
