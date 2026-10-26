"""The curtained validator grades each default-tariff term's rate against Ofgem's published cap.

`unit_charge_at_contract` proves the bill charges the term record's rate, but the term record is
ours. For a default tariff the cap is the one outside source that bounds it, read here from the
commons alone: single-register `ofgem_default_tariff_cap_windows.json` ex-VAT, multi-register
`ofgem_cap_multi_register_unit_rates.json`.

Measured 2026-10-26 on the 4ae8da9b0f book, regenerated: 27,197 periods graded, 0 above, every rate
at its ceiling (ratio 1.0000). A 1% raise on every graded term fails all 27,197.
docs/staging/SEAT_FINDING_THE_DEFAULT_TARIFF_TERM_RATE_AGAINST_THE_PUBLISHED_CAP_2026-10-26.md.
"""
from __future__ import annotations

import pytest

from tools import bill_validation_comparison as cmp
from tools import independent_bill_validator as v

# Jan-Mar 2023: Ofgem electricity 674.7 GBP/MWh inc 5% VAT; the EPG was 340.0.
JAN_2023_CAP = 64.2571


def _term(rate, start="2023-01-01", end="2023-04-01", tariff="svt"):
    return {"tariff_effective_from": start, "tariff_effective_to": end, "tariff_type": tariff,
            "unit_rate_p_per_kwh": rate, "tou_unit_rates": None}


def _period(terms, start="2023-01-01", end="2023-01-31", commodity="electricity", registers=1):
    regs = [{"register_id": str(i), "register_label": label, "unit_rate_p_per_kwh": 1.0}
            for i, label in enumerate(["Peak", "Off-peak"][:registers] if registers > 1
                                      else ["Anytime"])]
    return {"period_start": start, "period_end": end, "commodity": commodity,
            "registers": regs if registers > 1 else [], "contracted_terms": terms}


def _line(period, segment="resi"):
    return v.default_tariff_rate_against_cap(period, segment=segment)


def _claim(period, segment="resi"):
    built = {"period_start": "x", "period_end": "x",
             "lines": [v.default_tariff_rate_against_cap(period, segment=segment)]}
    issued = {"period_start": "x", "period_end": "x", "lines": []}
    claims = cmp.compare_bill(built, issued, statutory_vat={}, read_volume_kwh=None)
    return next((c for c in claims if c["claim"] == "default_tariff_rate_within_cap"), None)


def test_every_verdict_can_be_reached():
    """THE PARTITION, asserted whole: a check that only ever agreed (as it does on the whole real
    book) passes every leg test below."""
    seen = {
        _line(_period([_term(JAN_2023_CAP)]))["status"],
        _line(_period([_term(JAN_2023_CAP, tariff="fixed")]))["status"],
        _line(_period([_term(30.0, "2026-01-01", "2026-04-01")], "2026-01-01", "2026-01-31",
                      registers=2))["status"],
    }
    assert seen == {v.CAP_CHECKED, v.NOT_APPLICABLE, v.UNCHECKABLE}
    verdicts = {_claim(_period([_term(JAN_2023_CAP)]))["verdict"],
                _claim(_period([_term(JAN_2023_CAP + 0.01)]))["verdict"],
                _claim(_period([_term(30.0, "2026-01-01", "2026-04-01")], "2026-01-01",
                               "2026-01-31", registers=2))["verdict"]}
    assert verdicts == {cmp.AGREED, cmp.DISAGREED, cmp.UNCHECKABLE}


def test_a_default_rate_above_the_cap_disagrees_and_names_the_window():
    """Mutation: a default term struck a hundredth of a penny over the Jan 2023 level."""
    claim = _claim(_period([_term(JAN_2023_CAP + 0.01)]))
    assert claim["verdict"] == cmp.DISAGREED
    assert claim["validator_says"] == pytest.approx(JAN_2023_CAP, abs=1e-4)
    assert "2023-01-01..2023-03-31" in claim["how"]


def test_in_an_epg_window_the_ceiling_is_ofgems_level_not_the_guarantee():
    """The term includes the Treasury's receipt, so a strike at the Ofgem level is lawful. A
    ceiling at the EPG (32.38p) would call every correct crisis SVT term a breach."""
    assert _claim(_period([_term(JAN_2023_CAP)]))["verdict"] == cmp.AGREED


def test_the_ceiling_divides_out_the_vat_in_force_for_that_fuel():
    """Domestic electricity is zero-rated from 2026-10-01 (`uk_vat_rates.json`): the 263.2 row is
    26.32p ex-VAT, not 25.07p. Gas in the same window stays at 5%."""
    elec = _line(_period([_term(26.32, "2026-10-01", "2027-01-01")], "2026-10-01", "2026-10-31"))
    gas = _line(_period([_term(79.7 / 10 / 1.05, "2026-10-01", "2027-01-01")], "2026-10-01",
                        "2026-10-31", commodity="gas"))
    assert elec["within"] and elec["graded"][0]["ceiling_p_per_kwh"] == pytest.approx(26.32)
    assert gas["within"]
    assert not _line(_period([_term(26.33, "2026-10-01", "2027-01-01")], "2026-10-01",
                             "2026-10-31"))["within"]


def test_a_term_across_a_cap_change_is_held_to_every_window_it_touches():
    """A rate that is lawful in October 2021 (20.8p inc VAT) is 1.76p over September's 18.95p."""
    line = _line(_period([_term(208.0 / 10 / 1.05, "2021-09-01", "2021-11-01")],
                         "2021-09-15", "2021-10-14"))
    assert line["status"] == v.CAP_CHECKED and not line["within"]
    assert [g["within"] for g in line["graded"]] == [False, True]


def test_the_multi_register_benchmark_grades_a_multi_register_period():
    """Oct-Dec 2022, the cap model's multi-register level is 46.54p ex-VAT against 49.246p
    single-rate: a single-rate strike on a two-register meter is above its ceiling."""
    line = _line(_period([_term(46.54, "2022-10-01", "2023-01-01")], "2022-10-01", "2022-10-31",
                         registers=2))
    assert line["within"]
    assert not _line(_period([_term(49.0, "2022-10-01", "2023-01-01")], "2022-10-01",
                             "2022-10-31", registers=2))["within"]


@pytest.mark.parametrize("period, segment", [
    (_period([_term(30.0, "2026-01-01", "2026-04-01")], "2026-01-01", "2026-01-31", registers=2),
     "resi"),
    (_period([_term(30.0, "2027-01-01", "2027-04-01")], "2027-01-01", "2027-01-31"), "resi"),
])
def test_where_the_commons_has_no_level_it_fails_closed_and_says_why(period, segment):
    """Post-P15b multi-register, and past the last published window: the company carries the last
    level forward, and that is its reading, not the law's."""
    line = _line(period, segment)
    assert line["status"] == v.UNCHECKABLE and line["why"]


def test_off_a_domestic_default_tariff_there_is_no_claim_at_all():
    """A fixed term, a business account and a pre-cap day are not agreement, and are not counted
    as one."""
    assert _claim(_period([_term(99.0, tariff="fixed")])) is None
    assert _claim(_period([_term(99.0)]), segment="SME") is None
    assert _claim(_period([_term(99.0, "2018-06-01", "2018-12-01")], "2018-06-01",
                          "2018-06-30")) is None


def test_only_the_days_from_the_caps_start_are_graded():
    """Jan 2019's level is 15.73p ex-VAT; December 2018 days carry no ceiling."""
    line = _line(_period([_term(15.73, "2018-12-01", "2019-04-01")], "2018-12-15", "2019-01-14"))
    assert line["status"] == v.CAP_CHECKED and line["within"]
    assert [g["window"] for g in line["graded"]] == ["2019-01-01..2019-03-31"]


def test_a_term_is_not_graded_on_the_day_the_next_one_starts():
    """`tariff_effective_to` is exclusive: the next term starts on it. Mutation: an inclusive end
    held the April 2023 SVT (47.91p ex-VAT) to July's 28.68p for one day, on a bill that crosses
    the fall."""
    april = 506.0 / 10 / 1.05
    july = 301.1 / 10 / 1.05
    line = _line(_period([_term(april, "2023-04-01", "2023-07-01"),
                          _term(july, "2023-07-01", "2023-10-01")], "2023-06-15", "2023-07-14"))
    assert line["status"] == v.CAP_CHECKED and line["within"]
    assert [g["window"] for g in line["graded"]] == ["2023-04-01..2023-06-30",
                                                     "2023-07-01..2023-09-30"]
