"""Tests for the universal account hierarchy (M2 / D5)."""
import datetime as dt

import pytest

from company.crm.account_hierarchy import (
    Account,
    AccountHierarchy,
    AccountingModel,
    Agreement,
    Fuel,
    InvoicingMode,
    PartyType,
    Segment,
    default_accounting_model,
    default_invoicing_mode,
)

D = dt.date(2024, 1, 1)


def _hierarchy_dual_fuel_resi():
    h = AccountHierarchy()
    h.register_party("P1", "Alice Thompson", PartyType.INDIVIDUAL)
    h.open_account("A1", "P1", Segment.RESIDENTIAL, D)
    h.add_agreement("A1", "AG-E", Fuel.ELECTRICITY, "1234567890123", "Fixed 24", D)
    h.add_agreement("A1", "AG-G", Fuel.GAS, "9876543210", "Fixed 24", D)
    return h


# --- defaults / fork ---

def test_resi_defaults_to_balance_based():
    assert default_accounting_model(Segment.RESIDENTIAL) == AccountingModel.BALANCE_BASED

def test_micro_sme_defaults_to_balance_based():
    assert default_accounting_model(Segment.MICRO_SME) == AccountingModel.BALANCE_BASED

def test_ic_defaults_to_open_item():
    assert default_accounting_model(Segment.IC) == AccountingModel.OPEN_ITEM

def test_sme_defaults_to_open_item():
    assert default_accounting_model(Segment.SME) == AccountingModel.OPEN_ITEM

def test_resi_default_invoicing_is_combined():
    assert default_invoicing_mode(Segment.RESIDENTIAL) == InvoicingMode.COMBINED

def test_ic_default_invoicing_is_per_site():
    assert default_invoicing_mode(Segment.IC) == InvoicingMode.PER_SITE

def test_segment_business_flag():
    assert Segment.IC.is_business
    assert Segment.SME.is_business
    assert Segment.MICRO_SME.is_business
    assert not Segment.RESIDENTIAL.is_business


# --- dual-fuel resi: one party, one account, two agreements, one statement ---

def test_dual_fuel_resi_one_account_two_agreements():
    h = _hierarchy_dual_fuel_resi()
    acc = h.account("A1")
    assert len(acc.agreements) == 2
    assert acc.is_dual_fuel
    assert acc.emits_one_statement
    assert sorted(acc.fuels) == ["electricity", "gas"]

def test_dual_fuel_not_multisite():
    acc = _hierarchy_dual_fuel_resi().account("A1")
    assert not acc.is_multisite

def test_account_for_supply_point_reverse_lookup():
    h = _hierarchy_dual_fuel_resi()
    assert h.account_for_supply_point("9876543210").account_id == "A1"
    assert h.account_for_supply_point("nope") is None


# --- multi-site I&C: one party, many agreements ---

def test_multisite_ic_many_agreements():
    h = AccountHierarchy()
    h.register_party("P9", "Nexus Ltd", PartyType.ORGANISATION)
    h.open_account("A9", "P9", Segment.IC, D)
    for i in range(4):
        h.add_agreement("A9", f"AG-{i}", Fuel.ELECTRICITY, f"10000000000{i:02d}",
                        "HH Flex", D, site_label=f"Site {i}")
    acc = h.account("A9")
    assert len(acc.active_agreements()) == 4
    assert acc.is_multisite
    assert acc.accounting_model == AccountingModel.OPEN_ITEM

def test_consolidated_invoicing_emits_one_statement():
    h = AccountHierarchy()
    h.register_party("P9", "Nexus Ltd", PartyType.ORGANISATION)
    h.open_account("A9", "P9", Segment.IC, D, invoicing_mode=InvoicingMode.CONSOLIDATED)
    assert h.account("A9").emits_one_statement

def test_per_site_invoicing_not_one_statement():
    acc = AccountHierarchy()
    acc.register_party("P9", "Nexus", PartyType.ORGANISATION)
    a = acc.open_account("A9", "P9", Segment.IC, D)  # default per_site
    assert not a.emits_one_statement


# --- idempotency / order-independence (C-S1/C-S2) ---

def test_add_agreement_idempotent():
    h = _hierarchy_dual_fuel_resi()
    acc = h.account("A1")
    # re-add same agreement id — must not duplicate
    acc.add_agreement(Agreement("AG-E", "A1", Fuel.ELECTRICITY, "1234567890123", "New Tariff", D))
    assert len(acc.agreements) == 2
    assert acc.agreement("AG-E").tariff_name == "New Tariff"  # upserted in place

def test_add_agreement_wrong_account_rejected():
    acc = Account("A1", "P1", Segment.RESIDENTIAL, AccountingModel.BALANCE_BASED,
                  InvoicingMode.COMBINED, D)
    with pytest.raises(ValueError):
        acc.add_agreement(Agreement("X", "OTHER", Fuel.GAS, "9", "T", D))

def test_open_account_unknown_party_rejected():
    h = AccountHierarchy()
    with pytest.raises(KeyError):
        h.open_account("A1", "GHOST", Segment.RESIDENTIAL, D)


# --- agreement active-at date logic ---

def test_agreement_active_at():
    ag = Agreement("AG", "A1", Fuel.GAS, "9", "T", dt.date(2024, 1, 1), dt.date(2024, 6, 1))
    assert ag.is_active_at(dt.date(2024, 3, 1))
    assert not ag.is_active_at(dt.date(2023, 12, 1))   # before start
    assert not ag.is_active_at(dt.date(2024, 7, 1))    # after end

def test_multiple_accounts_one_party():
    h = _hierarchy_dual_fuel_resi()
    h.open_account("A2", "P1", Segment.MICRO_SME, D)  # same landlord, a business acct
    assert len(h.accounts_for_party("P1")) == 2


# --- portfolio summary ---

def test_portfolio_summary_counts():
    h = _hierarchy_dual_fuel_resi()
    s = h.portfolio_summary()
    assert s["account_count"] == 1
    assert s["agreement_count"] == 2
    assert s["dual_fuel_accounts"] == 1
    assert s["by_accounting_model"]["balance_based"] == 1
