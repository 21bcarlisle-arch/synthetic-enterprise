"""Every company deadline counts working days on the one calendar (atom SP2_1, level 3).

Subject: the eighteen company modules migrated off private weekend-only working-day copies on
2026-10-03 (after the four billing ones landed in 5dbf5808b), and the guard's allowlist, which now
holds no company entry at all. The calendar: `company/compliance/working_days.py`.

THREE LEGS, each failing on a different defect:
  1. BINDING -- every migrated module's working-day name IS the canonical function, so a local
     copy re-inserted under the same name reds here even before the guard runs.
  2. BEHAVIOUR -- a deadline read through each lane's public API moves across a real bank holiday,
     and still lands where it always did when no holiday is in the way (the reachability half: a
     deadline that never moved, or always moved, fails one of the two).
  3. THE ALLOWLIST -- no company path is exempt any more; only the world's simulation/ copies are.
"""
from __future__ import annotations

import datetime as dt
import importlib

import pytest

from company.compliance import working_days as canonical
from company.crm.service_ticket import ServiceTicket, TicketCategory, TicketStatus
from company.market.erroneous_transfer import ETClaim, ETStatus
from company.regulatory.gsop import GSOPBook, GSOPType
from company.trading.emir_reporting_register import _add_working_days as emir_deadline
from tools.working_day_guard import BASELINE_ALLOWLIST

D = dt.date

ADD = [
    "company.crm.change_of_tenancy_register",
    "company.crm.onboarding_journey",
    "company.crm.service_log",
    "company.crm.service_ticket",
    "company.market.bsc_performance_assurance_register",
    "company.market.bsc_settlement_dispute_register",
    "company.market.css_performance_register",
    "company.market.dcc_meter_registration",
    "company.market.meter_technical_investigation_register",
    "company.market.mop_appointment_register",
    "company.market.mpas_standing_data_correction_register",
    "company.market.transfer_objection_register",
    "company.regulatory.annual_compliance_attestation_register",
    "company.regulatory.gsop",
    "company.trading.bsc_credit_register",
    "company.trading.emir_reporting_register",
]
BETWEEN = [
    "company.market.erroneous_transfer",
    "company.regulatory.gsop_tracker",
    "company.billing.credit_refund",
    "company.billing.dd_indemnity",
    "company.billing.deemed_contract",
    "company.billing.energy_theft_book",
]


@pytest.mark.parametrize("mod", ADD)
def test_each_deadline_module_binds_the_canonical_add(mod):
    assert importlib.import_module(mod).add_working_days is canonical.add_working_days


@pytest.mark.parametrize("mod", BETWEEN)
def test_each_counting_module_binds_the_canonical_count(mod):
    assert importlib.import_module(mod).working_days_between is canonical.working_days_between


def _ticket(opened):
    return ServiceTicket("T1", "A1", list(TicketCategory)[0], opened, TicketStatus(list(TicketStatus)[0]))


def test_slc_18_7_acknowledgement_moves_across_easter_and_not_without_it():
    # Thu 28 Mar 2024 + 3 working days: Good Friday and Easter Monday out -> Thu 4 Apr
    # (the weekend-only copy said Tue 2 Apr).
    assert _ticket(D(2024, 3, 28)).acknowledgement_deadline == D(2024, 4, 4)
    # A week later, no holiday: Thu 4 Apr + 3 -> Tue 9 Apr, as the weekend-only copy also said.
    assert _ticket(D(2024, 4, 4)).acknowledgement_deadline == D(2024, 4, 9)


def test_gsop_payment_due_moves_across_christmas_and_not_without_it():
    book = GSOPBook()
    kind = next(k for k in GSOPType if k.name == "REFUND_DELAY")   # 10 working days
    # Fri 20 Dec 2024 + 10: 25, 26 Dec and 1 Jan out -> Wed 8 Jan 2025 (was Fri 3 Jan).
    assert book.record_trigger("C1", kind, D(2024, 12, 20)).payment_due_date == D(2025, 1, 8)
    assert book.record_trigger("C2", kind, D(2024, 11, 1)).payment_due_date == D(2024, 11, 15)


def test_emir_t_plus_1_keeps_its_17_00_deadline_and_skips_the_holiday():
    tz = dt.timezone.utc
    # Thu 24 Dec 2020 executed -> T+1 is Tue 29 Dec (25 Dec and the 28 Dec substitute day out).
    got = emir_deadline(dt.datetime(2020, 12, 24, 9, tzinfo=tz), 1)
    assert got == dt.datetime(2020, 12, 29, 17, tzinfo=tz)
    got = emir_deadline(dt.datetime(2020, 12, 10, 9, tzinfo=tz), 1)
    assert got == dt.datetime(2020, 12, 11, 17, tzinfo=tz)


def test_erroneous_transfer_keeps_its_interval_and_drops_the_holiday():
    """[claim_date, as_of): the claim day counts and as_of does not -- unchanged. Only the
    calendar moved: Mon 3 Jan 2022 was the New Year substitute bank holiday."""
    claim = ETClaim("E", "M", "A", D(2022, 1, 3), "Old", "New", ETStatus.OPEN)
    assert claim.working_days_open(D(2022, 1, 10)) == 4
    clean = ETClaim("E", "M", "A", D(2022, 1, 10), "Old", "New", ETStatus.OPEN)
    assert clean.working_days_open(D(2022, 1, 17)) == 5     # claim day counted, as before
    assert clean.working_days_open(D(2022, 1, 10)) == 0


def test_no_company_copy_is_exempt_any_more():
    company = sorted(e for e in BASELINE_ALLOWLIST if e.startswith("company/"))
    assert company == [], f"company copies still allowlisted: {company}"
    assert BASELINE_ALLOWLIST, "the world's simulation/ copies are still there to migrate"
