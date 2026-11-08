"""Every company deadline counts working days on the one calendar (atom SP2_1, level 3).

Subject: the eighteen company modules migrated off private weekend-only working-day copies on
2026-10-03 (after the four billing ones landed in 5dbf5808b), and the guard's allowlist, which now
holds no company entry at all. The calendar: `company/compliance/working_days.py`. Thirteen
listed modules reached no run and left for archive/unhooked_supplier/ with their legs (archive
increment 3b, 2026-11-08); the binding legs below hold the ones that stay.

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
from company.regulatory.gsop import GSOPBook, GSOPType
from tools.working_day_guard import BASELINE_ALLOWLIST

D = dt.date

ADD = [
    "company.crm.change_of_tenancy_register",
    "company.crm.service_log",
    "company.market.transfer_objection_register",
    "company.regulatory.gsop",
]
BETWEEN = [
    "company.billing.credit_refund",
    "company.billing.energy_theft_book",
]


@pytest.mark.parametrize("mod", ADD)
def test_each_deadline_module_binds_the_canonical_add(mod):
    assert importlib.import_module(mod).add_working_days is canonical.add_working_days


@pytest.mark.parametrize("mod", BETWEEN)
def test_each_counting_module_binds_the_canonical_count(mod):
    assert importlib.import_module(mod).working_days_between is canonical.working_days_between


def test_gsop_payment_due_moves_across_christmas_and_not_without_it():
    book = GSOPBook()
    kind = next(k for k in GSOPType if k.name == "REFUND_DELAY")   # 10 working days
    # Fri 20 Dec 2024 + 10: 25, 26 Dec and 1 Jan out -> Wed 8 Jan 2025 (was Fri 3 Jan).
    assert book.record_trigger("C1", kind, D(2024, 12, 20)).payment_due_date == D(2025, 1, 8)
    assert book.record_trigger("C2", kind, D(2024, 11, 1)).payment_due_date == D(2024, 11, 15)


def test_no_company_copy_is_exempt_any_more():
    company = sorted(e for e in BASELINE_ALLOWLIST if e.startswith("company/"))
    assert company == [], f"company copies still allowlisted: {company}"
    assert BASELINE_ALLOWLIST, "the world's simulation/ copies are still there to migrate"
