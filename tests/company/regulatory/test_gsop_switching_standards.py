"""The switching guaranteed standards (regs 6ZA, 6ZB, 6C), as the regulations write them.

Source: `docs/market_research/switching_mechanics_2026-10-25.md` s.6 (legislation.gov.uk, read
21 Nov 2026). Each test names the defect it exists to catch.
"""
from datetime import date

import pytest

from company.regulatory.gsop import (
    SWITCHING_STANDARDS,
    GSOPBook,
    GSOPType,
    erroneous_transfer_return_failed_on,
    switch_speed_deadline,
    switch_speed_failed_on,
)


def test_a_switch_before_the_standard_existed_owes_nothing():
    """Defect: a 2018 slow switch priced at £30 the supplier never owed (6ZA is from 1 May 2020)."""
    assert switch_speed_deadline(date(2020, 4, 30), date(2020, 4, 20)) is None
    assert switch_speed_failed_on(None, date(2020, 7, 1)) is None
    with pytest.raises(ValueError, match="6ZB"):
        GSOPBook().record_trigger("C1", GSOPType.ERRONEOUS_TRANSFER, date(2019, 6, 3))


def test_the_2020_rule_is_15_working_days_beginning_with_the_information_day():
    """Defect: counting from the day AFTER (one working day too generous), or calendar days."""
    # Mon 1 Jun 2020 is day 1; 15 working days end Fri 19 Jun 2020.
    deadline = switch_speed_deadline(date(2020, 6, 1), date(2020, 5, 20))
    assert deadline == date(2020, 6, 19)
    assert switch_speed_failed_on(deadline, date(2020, 6, 19)) is None
    assert switch_speed_failed_on(deadline, date(2020, 6, 22)) == date(2020, 6, 20)


def test_from_april_2024_the_clock_is_5_days_after_cooling_off_unless_early_start():
    """Defect: keeping 15 days after S.I. 2024/108, or starting the 5 days at the information day
    when the customer did not ask to start inside cooling-off."""
    contract = date(2024, 6, 3)  # Monday; the 14 days run to Sun 16 Jun
    late = switch_speed_deadline(date(2024, 6, 4), contract)
    early = switch_speed_deadline(date(2024, 6, 4), contract, early_start_requested=True)
    assert early == date(2024, 6, 10)    # Tue 4 .. Mon 10: five working days
    assert late == date(2024, 6, 21)     # first working day after the 16th is Mon 17; +4 -> Fri 21
    after_5pm = switch_speed_deadline(date(2024, 6, 4), contract, contract_after_5pm=True,
                                      early_start_requested=True)
    assert after_5pm == date(2024, 6, 11)


def test_the_gaining_supplier_pays_the_flat_standard_payment_of_its_day():
    """Defect: a switching failure after 2 Jan 2025 paid at the 2015 £30, not £40 (S.I. 2024/1166)."""
    book = GSOPBook()
    assert book.record_trigger("C1", GSOPType.SWITCH_SPEED, date(2024, 12, 31)).amount_gbp == 30.0
    assert book.record_trigger("C1", GSOPType.SWITCH_SPEED, date(2025, 1, 2)).amount_gbp == 40.0
    assert SWITCHING_STANDARDS[GSOPType.SWITCH_SPEED].payer == "new"
    assert SWITCHING_STANDARDS[GSOPType.ERRONEOUS_TRANSFER].payer == "new"
    assert SWITCHING_STANDARDS[GSOPType.ERRONEOUS_TRANSFER_RETURN].payer == "old"


def test_the_old_supplier_fails_6c_on_the_22nd_working_day_after_agreement():
    """Defect: an unreturned customer never becomes a failure because only a return date is checked."""
    agreed = date(2021, 3, 1)  # Monday; 21 working days beginning that day end Mon 29 Mar
    assert erroneous_transfer_return_failed_on(agreed, date(2021, 3, 29), date(2021, 6, 1)) is None
    assert erroneous_transfer_return_failed_on(agreed, None, date(2021, 3, 29)) is None
    assert erroneous_transfer_return_failed_on(agreed, None, date(2021, 3, 31)) == date(2021, 3, 30)
    assert erroneous_transfer_return_failed_on(date(2019, 4, 1), None, date(2019, 9, 1)) is None
