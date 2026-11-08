"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/regulatory/price_cap.py — the SECOND Ofgem Default Tariff Cap
authority in this codebase (the first, company/pricing/ofgem_price_cap.py, was
characterized in the previous pass). This one holds a quarterly p/kWh table and
a compliance check that decides whether the company's own rate breaches the cap.

Values in the quarterly table are published regulatory history (R13 baseline);
these tests record what the module returns, not a judgement on the levels. All
quarter keys are literals and the module reads no clock.

The cross-module comparison at the bottom is deliberately included: two modules
answering the same regulatory question with different numbers is the finding.
"""
from __future__ import annotations

from datetime import date

import pytest

from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date
from company.regulatory.price_cap import (
    CapComplianceCheck,
    CapStatus,
    PriceCapBook,
)


def check(quarter="2024-Q1", commodity="electricity", supplier=20.0, cap=24.5):
    return CapComplianceCheck(
        quarter=quarter, commodity=commodity,
        supplier_rate_p_kwh=supplier, cap_rate_p_kwh=cap,
    )


# ---------------------------------------------------------------------------
# The quarterly table
# ---------------------------------------------------------------------------


def test_the_table_covers_2019_q1_to_2025_q1_inclusive():
    assert PriceCapBook().cap_summary()["quarters_available"] == 25
    assert PriceCapBook.cap_data("2019-Q1") is not None
    assert PriceCapBook.cap_data("2025-Q1") is not None
    assert PriceCapBook.cap_data("2025-Q2") is None


@pytest.mark.parametrize(
    "quarter,elec,gas,typical",
    [
        ("2019-Q1", 17.14, 3.40, 1137),
        ("2021-Q4", 20.80, 4.17, 1277),
        ("2022-Q3", 52.00, 14.97, 3549),
        ("2022-Q4", 34.00, 10.32, 2500),
        ("2024-Q3", 22.36, 5.48, 1568),
        ("2025-Q1", 24.50, 6.33, 1738),
    ],
)
def test_published_quarterly_levels(quarter, elec, gas, typical):
    assert PriceCapBook.elec_cap_p_kwh(quarter) == elec
    assert PriceCapBook.gas_cap_p_kwh(quarter) == gas
    assert PriceCapBook.typical_annual_bill(quarter) == typical


@pytest.mark.parametrize("quarter", ["2018-Q4", "2026-Q1", "2024-q1", "2024Q1", "", "Q1-2024"])
def test_every_unrecognised_quarter_string_returns_none_from_every_lookup(quarter):
    # Exact, case-sensitive key match. A lowercase quarter or a transposed
    # "Q1-2024" is not an error — it is silently "no cap data".
    assert PriceCapBook.cap_data(quarter) is None
    assert PriceCapBook.elec_cap_p_kwh(quarter) is None
    assert PriceCapBook.gas_cap_p_kwh(quarter) is None
    assert PriceCapBook.typical_annual_bill(quarter) is None


def test_the_table_has_no_forward_carry_so_it_runs_out_after_2025_q1():
    # SURPRISE: the sibling module (company/pricing/ofgem_price_cap.py) documents
    # forward-carry precisely because returning None "would silently un-cap every
    # resi customer — the FAIL-OPEN pattern R15 names". This module has the
    # opposite behaviour: past 2025-Q1 every lookup returns None, and (see
    # below) a compliance check for such a quarter is classed PRE_CAP/compliant.
    assert PriceCapBook.elec_cap_p_kwh("2025-Q2") is None
    assert get_cap_unit_rate_for_date("electricity", date(2025, 4, 1)) == 270.3


# ---------------------------------------------------------------------------
# CapComplianceCheck — the compliance control
# ---------------------------------------------------------------------------


def test_a_rate_under_the_cap_is_below_cap_and_compliant():
    c = check(supplier=20.0, cap=24.5)
    assert c.headroom_p_kwh == 4.5
    assert c.status is CapStatus.BELOW_CAP
    assert c.is_compliant is True


def test_a_rate_over_the_cap_is_a_breach():
    c = check(supplier=30.0, cap=24.5)
    assert c.headroom_p_kwh == -5.5
    assert c.status is CapStatus.EXCEEDS_CAP
    assert c.is_compliant is False


def test_at_cap_is_a_one_hundredth_of_a_penny_band_below_the_cap_only():
    # AT_CAP requires |headroom| < 0.01 AND supplier <= cap, because the
    # EXCEEDS_CAP test runs first. A rate 0.005p ABOVE the cap is a breach, not
    # "at cap" — the tolerance band is one-sided.
    assert check(supplier=24.5, cap=24.5).status is CapStatus.AT_CAP
    assert check(supplier=24.495, cap=24.5).status is CapStatus.AT_CAP
    assert check(supplier=24.505, cap=24.5).status is CapStatus.EXCEEDS_CAP
    assert check(supplier=24.48, cap=24.5).status is CapStatus.BELOW_CAP


def test_a_fabricated_cap_from_the_caller_no_longer_clears_a_breach():
    # R15 MUTATION PROOF (was the frozen defect, and the highest-value finding in
    # this module). `cap_rate_p_kwh` is supplied by the CALLER — the party being
    # checked. The class held a quarter key and a full published table keyed by
    # exactly that string and never looked the rate up, so a supplier charging
    # 99p/kWh in a 24.5p quarter declared itself BELOW_CAP by passing its own cap
    # number. The ceiling now comes from the table; the caller's number is inert.
    fabricated = check(quarter="2024-Q1", supplier=99.0, cap=150.0)
    assert PriceCapBook.elec_cap_p_kwh("2024-Q1") == 24.5   # the real ceiling
    assert fabricated.effective_cap_p_kwh == 24.5
    assert fabricated.status is CapStatus.EXCEEDS_CAP
    assert fabricated.is_compliant is False


def test_the_declared_cap_cannot_move_the_verdict_in_either_direction():
    # Independence, stated as a property: for a quarter in the table the verdict
    # is identical whatever the caller declares.
    verdicts = {check(quarter="2024-Q1", supplier=99.0, cap=c).status
                for c in (0.0, 24.5, 150.0, -1.0)}
    assert verdicts == {CapStatus.EXCEEDS_CAP}


def test_a_gas_rate_is_checked_against_the_gas_cap_not_the_electricity_one():
    # R15 MUTATION PROOF: `commodity` was recorded and read by nothing, so a gas
    # rate of 6.3p was cleared against the 24.5p ELECTRICITY cap with "18.2p of
    # headroom". The lookup is now keyed on commodity as well as quarter.
    c = check(commodity="gas", supplier=6.3, cap=24.5)
    assert PriceCapBook.gas_cap_p_kwh("2024-Q1") == 6.04
    assert c.effective_cap_p_kwh == 6.04
    assert c.status is CapStatus.EXCEEDS_CAP   # 6.3p IS over the 6.04p gas cap
    assert c.is_compliant is False


def test_an_unrecognised_commodity_is_not_compliance():
    c = check(commodity="oil", supplier=1.0)
    assert c.effective_cap_p_kwh is None
    assert c.status is CapStatus.UNKNOWN
    assert c.is_compliant is False


def test_an_unrecognised_quarter_is_no_longer_compliance():
    # R15 MUTATION PROOF (was the frozen defect, fail-open class). The quarter key
    # did exactly one thing: if it was not in the table the status was PRE_CAP,
    # which `is_compliant` treats as compliant. So a 500p/kWh rate was reported
    # compliant for "2026-Q1" (past the table's 2025-Q1 end), "2024-q1" (a case
    # typo) and "" (missing) — every future quarter and every typo cleared any
    # breach. Those are UNKNOWN now: the ceiling could not be established, which
    # is not the same as the rate being lawful.
    for quarter in ("2026-Q1", "2024-q1", "", "unknown"):
        c = check(quarter=quarter, supplier=500.0, cap=24.5)
        assert c.status is CapStatus.UNKNOWN, quarter
        assert c.is_compliant is False, quarter


def test_pre_cap_is_still_correct_for_genuinely_pre_cap_quarters():
    # The narrow case the PRE_CAP branch was designed for still holds — 2018
    # predates the Default Tariff Cap — which is why the fail-open was easy to
    # miss. This is the other half of the mutation: the fix must not turn a
    # genuinely pre-cap quarter into a breach.
    assert check(quarter="2018-Q4", supplier=500.0).status is CapStatus.PRE_CAP
    assert check(quarter="2018-Q4", supplier=500.0).is_compliant is True


def test_headroom_is_withheld_when_no_ceiling_could_be_established():
    # The headroom number used to be computed unconditionally from the CALLER's
    # own cap, so an unrecognised quarter still published a confident -475.5p
    # headroom next to its "compliant" verdict. No ceiling now means no headroom.
    c = check(quarter="2026-Q1", supplier=500.0, cap=24.5)
    assert c.headroom_p_kwh is None
    assert c.is_compliant is False


def test_headroom_rounds_to_four_decimal_places():
    assert check(supplier=20.000004).headroom_p_kwh == 4.5
    assert check(supplier=20.12345).headroom_p_kwh == 4.3766


def test_a_compliance_check_is_frozen():
    c = check()
    with pytest.raises(Exception):
        c.supplier_rate_p_kwh = 0.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PriceCapBook — the register of checks
# ---------------------------------------------------------------------------


def test_record_check_stores_and_returns_the_check_unvalidated():
    book = PriceCapBook()
    c = check(supplier=30.0, cap=24.5)
    assert book.record_check(c) is c
    assert book.breach_quarters() == [c]


def test_breach_quarters_only_sees_checks_that_were_recorded():
    # SURPRISE: the breach register is populated entirely by callers choosing to
    # call record_check. A book reporting zero breaches is indistinguishable from
    # a book nothing was ever recorded into — `cap_summary()["breach_count"]`
    # reads 0 in both cases.
    book = PriceCapBook()
    assert book.breach_quarters() == []
    assert book.cap_summary()["breach_count"] == 0


def test_the_same_breach_recorded_twice_counts_twice():
    book = PriceCapBook()
    c = check(supplier=30.0, cap=24.5)
    book.record_check(c)
    book.record_check(c)
    assert book.cap_summary()["breach_count"] == 2


def test_cap_summary_reports_the_2022_q3_peak_from_the_table():
    book = PriceCapBook()
    assert book.cap_summary() == {
        "quarters_available": 25,
        "peak_typical_annual_gbp": 3549,
        "peak_quarter": "2022-Q3",
        "breach_count": 0,
    }


def test_peak_annual_bill_year_returns_a_string_despite_its_int_annotation():
    # SURPRISE: annotated `-> int`, returns `"2022"` — a 4-character slice of the
    # quarter key. `peak_annual_bill_year() == 2022` is False; any caller doing
    # arithmetic or an int comparison on it breaks or silently mismatches.
    peak = PriceCapBook().peak_annual_bill_year()
    assert peak == "2022"
    assert isinstance(peak, str)
    assert peak != 2022


def test_peak_annual_bill_year_only_considers_q2_and_q3_quarters():
    # SURPRISE: the generator filters to quarters ending -Q2 or -Q3, so a peak
    # falling in a Q1 or Q4 can never be found. It happens to give the right
    # answer here only because 2022-Q3 (£3,549) is also the table-wide max — the
    # unfiltered `cap_summary` peak agrees by coincidence, not by construction.
    book = PriceCapBook()
    assert book.peak_annual_bill_year() == book.cap_summary()["peak_quarter"][:4]


# ---------------------------------------------------------------------------
# Cross-module: two cap authorities, two answers for the same quarter
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "quarter,on_date,regulatory_p_kwh,pricing_p_kwh",
    [
        ("2019-Q1", date(2019, 1, 1), 17.14, 16.52),
        ("2022-Q3", date(2022, 7, 1), 52.00, 28.34),
        ("2024-Q1", date(2024, 1, 1), 24.50, 28.62),
    ],
)
def test_the_two_cap_modules_disagree_on_the_same_quarter_in_both_directions(
    quarter, on_date, regulatory_p_kwh, pricing_p_kwh
):
    # SURPRISE: company/regulatory/price_cap.py and company/pricing/
    # ofgem_price_cap.py both claim to hold the Ofgem domestic electricity cap
    # unit rate, and give different ceilings for the same date — 2022-Q3 by a
    # factor of 1.8, and in 2024-Q1 the regulatory book is the TIGHTER of the
    # two. Which module a caller reaches for decides whether a rate is a breach.
    assert PriceCapBook.elec_cap_p_kwh(quarter) == regulatory_p_kwh
    assert get_cap_unit_rate_for_date("electricity", on_date) / 10.0 == pytest.approx(
        pricing_p_kwh, abs=0.005
    )


def test_the_regulatory_books_quarter_labels_do_not_line_up_with_calendar_quarters():
    # Evidence, not inference: this module's "2022-Q3" carries 52.00p/kWh and a
    # £3,549 typical annual bill — the published levels of the cap period that
    # began 1 OCTOBER 2022 — while the sibling module's 1 Jul 2022 window is
    # 283.4 £/MWh (28.34p), which is this module's "2022-Q1"/"2022-Q2" figure.
    # The two tables are the same regulatory history under different labels, so
    # any code that joins them on a date is comparing different quarters.
    assert PriceCapBook.elec_cap_p_kwh("2022-Q3") == 52.00
    assert PriceCapBook.typical_annual_bill("2022-Q3") == 3549
    assert PriceCapBook.elec_cap_p_kwh("2022-Q1") == 28.34
    assert get_cap_unit_rate_for_date("electricity", date(2022, 7, 1)) == 283.4


def test_the_regulatory_book_ignores_the_energy_price_guarantee_where_the_sibling_applies_it():
    # For Oct-Dec 2022 the sibling returns min(cap, EPG) = 340 £/MWh (34.0p).
    # This module's Oct-2022-level entry ("2022-Q3") is the UN-guaranteed 52.0p.
    # A customer's ceiling therefore differs by 18p/kWh depending on the module.
    assert get_cap_unit_rate_for_date("electricity", date(2022, 11, 1)) == 340.0
    assert PriceCapBook.elec_cap_p_kwh("2022-Q3") == 52.0
    assert PriceCapBook.elec_cap_p_kwh("2022-Q4") == 34.0
