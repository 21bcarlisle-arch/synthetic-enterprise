"""Phase BQ: BSC Credit Obligation and Regulatory Levy tests."""
import pytest
from saas.reporting.annual_report import (
    _section_bsc_regulatory_levies,
    _section_cm_supplier_levy,
)


def _yr(bsc_cr, cm, mute, ccl, gas_net):
    return {
        "bsc_credit_required_gbp": bsc_cr,
        "cm_levy_gbp": cm,
        "mutualization_levy_gbp": mute,
        "ccl_gbp": ccl,
        "gas_network_cost_gbp": gas_net,
    }


def _data(*year_tuples):
    return {"years": {str(2016 + i): _yr(*t) for i, t in enumerate(year_tuples)}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_bsc_regulatory_levies({}) == ""
    assert _section_bsc_regulatory_levies({"years": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data((10210, 37170, 100685, 71853, 54433))
    assert "BSC Credit Obligation" in _section_bsc_regulatory_levies(d)


# 3. Year row present
def test_year_row():
    d = _data((10210, 37170, 100685, 71853, 54433))
    assert "| 2016 |" in _section_bsc_regulatory_levies(d)


# 4. Peak BSC credit flagged
def test_peak_bsc_year():
    d = _data((100, 500, 0, 200, 0), (10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "Peak BSC credit obligation: 2017" in result


# 5. Mutualization 0 shows dash
def test_zero_mutualization_dash():
    d = _data((100, 500, 0, 200, 0))
    result = _section_bsc_regulatory_levies(d)
    assert "—" in result


# 6. Mutualization non-zero shown
def test_nonzero_mutualization():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£100,685" in result


# 7. First mutualization year noted
def test_first_mutualization_year():
    d = _data((100, 500, 0, 200, 0), (200, 600, 41818, 72054, 50441))
    result = _section_bsc_regulatory_levies(d)
    assert "2017" in result and "first appeared in" in result


# 8. BSC credit amount correct
def test_bsc_credit_value():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£10,210" in result


# 9. CM levy correct
def test_cm_levy_value():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£37,170" in result


# 10. CCL value correct
def test_ccl_value():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£71,853" in result


# 11. BSC note present
def test_bsc_note():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "Elexon" in result or "BSC credit" in result.lower()


# 12. Multiple years sorted
def test_years_sorted():
    d = _data(
        (5291, 50148, 41818, 72054, 50441),
        (10210, 37170, 100685, 71853, 54433),
    )
    result = _section_bsc_regulatory_levies(d)
    pos_2016 = result.find("| 2016 |")
    pos_2017 = result.find("| 2017 |")
    assert pos_2016 < pos_2017


# 13. Peak BSC credit year shown
def test_peak_bsc_year_shown():
    d = {"years": {
        "2022": {"bsc_credit_required_gbp": 80000.0, "cm_levy_gbp": 500.0,
                 "mutualization_levy_gbp": 0.0, "ccl_gbp": 100.0, "gas_network_cost_gbp": 200.0},
        "2021": {"bsc_credit_required_gbp": 20000.0, "cm_levy_gbp": 400.0,
                 "mutualization_levy_gbp": 0.0, "ccl_gbp": 80.0, "gas_network_cost_gbp": 150.0},
    }}
    result = _section_bsc_regulatory_levies(d)
    assert "Peak BSC credit" in result and "2022" in result


# 14. Mutualization dash when zero
def test_mutualization_dash_when_zero():
    d = {"years": {"2022": {"bsc_credit_required_gbp": 10000.0, "cm_levy_gbp": 500.0,
                             "mutualization_levy_gbp": 0.0, "ccl_gbp": 100.0,
                             "gas_network_cost_gbp": 200.0}}}
    result = _section_bsc_regulatory_levies(d)
    assert "—" in result


# 15. Mutualization first year noted when non-zero
def test_mutualization_first_year_noted():
    d = {"years": {
        "2021": {"bsc_credit_required_gbp": 5000.0, "cm_levy_gbp": 200.0,
                 "mutualization_levy_gbp": 0.0, "ccl_gbp": 50.0, "gas_network_cost_gbp": 100.0},
        "2022": {"bsc_credit_required_gbp": 8000.0, "cm_levy_gbp": 300.0,
                 "mutualization_levy_gbp": 1500.0, "ccl_gbp": 70.0, "gas_network_cost_gbp": 120.0},
    }}
    result = _section_bsc_regulatory_levies(d)
    assert "Mutualization levy first appeared" in result and "2022" in result


# ---------------------------------------------------------------------------
# a53: the CM Supplier Levy statutory section, and its live reconciliation.
#
# This page already carried a CM figure -- the `CM` column of the Policy Cost &
# Levy Breakdown, which is the settlement pass-through. a53 added the supplier's
# OWN statutory position beside it. Two totals for one levy on one page is this
# project's fourth-home failure unless the delta is reconciled ON THE PAGE, so
# what these controls guard is the reconciliation, not the table.
# ---------------------------------------------------------------------------


def _cm_data(rows, settled):
    """rows: {year: (mwh, levy_or_None, cost_or_None)}; settled: {year: settlement figure}."""
    return {
        "cm_statutory_summary": {
            "published_years": [y for y, r in sorted(rows.items()) if r[1] is not None],
            "per_year": {
                y: {
                    "elec_mwh": r[0],
                    "levy_gbp_per_mwh": r[1],
                    "cm_levy_gbp": r[2],
                    "peak_period_demand_kw": None,
                    "unpublished_reason": (
                        None if r[1] is not None
                        else f"Ofgem Annex 9 publishes no levy for obligation year {y}."
                    ),
                }
                for y, r in rows.items()
            },
        },
        "years": {y: {"cm_levy_gbp": v} for y, v in settled.items()},
    }


def test_cm_supplier_levy_empty_returns_empty():
    assert _section_cm_supplier_levy({}) == ""
    assert _section_cm_supplier_levy({"cm_statutory_summary": {"per_year": {}}}) == ""


def test_a_delta_explained_by_obligation_year_keying_is_declared_explained():
    """100 MWh/yr; levy steps 1.00 -> 2.00; a 30% Jan-Mar quarter gives a 30.0 delta.

    The BAND is what is asserted, not the number: the section must recognise a winter-quarter
    share as the whole explanation for the difference.
    """
    d = _cm_data(
        rows={"2019": (100.0, 1.00, 100.0), "2020": (100.0, 2.00, 200.0)},
        settled={"2019": 100.0, "2020": 170.0},
    )
    out = _section_cm_supplier_levy(d)
    assert "30.0%" in out
    assert "and about nothing else" in out
    assert "NOT EXPLAINED BY YEAR KEYING" not in out


def test_a_delta_too_large_for_the_keying_is_declared_a_finding():
    """THE SAME FIXTURE with the settlement figure moved so the implied quarter is 80%.

    No winter quarter is 80% of a year, so the difference cannot be the Apr-Mar bucketing --
    it is a segment filter, a fuel, or a volume basis. This is the leg that makes the section's
    reconciliation a control rather than a decoration: without it, the page would say "explained
    by keying" for any delta whatsoever.
    """
    d = _cm_data(
        rows={"2019": (100.0, 1.00, 100.0), "2020": (100.0, 2.00, 200.0)},
        settled={"2019": 100.0, "2020": 120.0},
    )
    out = _section_cm_supplier_levy(d)
    assert "NOT EXPLAINED BY YEAR KEYING" in out
    assert "2020" in out
    assert "and about nothing else" not in out


def test_an_unpublished_year_renders_as_a_gap_beside_the_settlements_carried_forward_number():
    """The defect: an unpublished year rendered as GBP0.00, or silently dropped from the table.

    Both would read as a fact. The settlement column legitimately shows a figure for that year
    because the world's reading carries its rate forward, so the row must appear, must be empty
    on the company side, and must say why.
    """
    d = _cm_data(
        rows={"2024": (100.0, 7.27, 727.0), "2025": (50.0, None, None)},
        settled={"2024": 700.0, "2025": 363.5},
    )
    out = _section_cm_supplier_levy(d)
    assert "| 2025 |" in out, "the unpublished year must not vanish from the table"
    assert "NOT PUBLISHED" in out and "NO FIGURE" in out
    assert "GBP0.00" not in out, "a zero would read as 'this levy cost nothing'"
    assert "GBP363.50" in out, "the settlement's carried-forward figure is still shown"
    assert "obligation year 2025" in out, "the refusal must name its reason"
    # Partition guard: 2024 is published in the same table, so this is not a section that
    # renders every year as a gap.
    assert "| 2024 |" in out and "GBP7.27" in out
