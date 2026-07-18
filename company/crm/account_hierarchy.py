"""Universal account hierarchy — party -> account -> agreement -> supply point.

M2 (D5_account_hierarchy_payments). One skeleton across every segment; segments
differ only in BREADTH and the ACCOUNTING MODEL, never in shape:

    party ──1:N── account ──1:N── agreement ──1:1── supply point (MPAN / MPRN)

- Dual-fuel resi: one party, one account, TWO agreements (elec MPAN + gas MPRN),
  ONE combined statement (invoicing_mode = COMBINED).
- Multi-site I&C: one party, many agreements; CONSOLIDATED (one invoice) vs
  PER_SITE invoicing is an account-level setting.
- SME: same skeleton, breadth in between.

This module is the SPINE that pre-existing partial views hang off, not a
replacement for them — it deliberately does NOT rip up:
  - company/crm/dual_fuel_account.py  (DualFuelAccount — the resi elec+gas view)
  - company/crm/multisite_account.py  (MultisiteAccount — the I&C site book)
  - company/crm/supply_point_register.py (SupplyPointRecord — MPAN/MPRN registry)
Those remain the segment-specialised read models; an Agreement here carries the
supply_point_ref (MPAN/MPRN) that keys into SupplyPointRegister, so the two
stay reconcilable without duplicating meter data.

Epistemic wall: this is company-side operational state (who we bill, under what
agreement) — entirely company-knowable. No simulation internals are read.

Scale constraints: the hierarchy is plain data; agreements can be added one at a
time in any order (C-S1) and add_agreement is idempotent on agreement_id (C-S2).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Segment(str, Enum):
    """Customer segment. Governs default accounting model + dunning path breadth,
    NOT the hierarchy shape."""
    RESIDENTIAL = "residential"
    MICRO_SME = "micro_sme"     # <= 10 employees / low consumption; treated resi-like for AR
    SME = "sme"
    IC = "ic"                   # industrial & commercial / half-hourly

    @property
    def is_business(self) -> bool:
        """B2B for the purposes of the Late Payment of Commercial Debts Act."""
        return self in (Segment.MICRO_SME, Segment.SME, Segment.IC)


class AccountingModel(str, Enum):
    """The fork: how payments meet bills on the ledger."""
    BALANCE_BASED = "balance_based"   # rolling balance, no bill-matching (resi / micro-SME)
    OPEN_ITEM = "open_item"           # payment allocates to specific invoices (SME / I&C)


class InvoicingMode(str, Enum):
    COMBINED = "combined"        # one statement across all agreements (dual-fuel resi)
    CONSOLIDATED = "consolidated"  # one invoice across many sites (I&C, opt-in)
    PER_SITE = "per_site"        # one invoice per agreement/site (I&C, default)


class PartyType(str, Enum):
    INDIVIDUAL = "individual"
    ORGANISATION = "organisation"


class Fuel(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


def default_accounting_model(segment: Segment) -> AccountingModel:
    """Segment default. Overridable per account (a large SME on open-item, a
    small one balance-based) — this is the default, not a hard rule."""
    if segment in (Segment.RESIDENTIAL, Segment.MICRO_SME):
        return AccountingModel.BALANCE_BASED
    return AccountingModel.OPEN_ITEM


def default_invoicing_mode(segment: Segment) -> InvoicingMode:
    if segment.is_business and segment in (Segment.SME, Segment.IC):
        return InvoicingMode.PER_SITE
    return InvoicingMode.COMBINED


@dataclass(frozen=True)
class Agreement:
    """A supply agreement for ONE supply point (one MPAN or one MPRN).

    A dual-fuel resi account has two of these; a multi-site I&C account has many.
    supply_point_ref keys into company/crm/supply_point_register.py.
    """
    agreement_id: str
    account_id: str
    fuel: Fuel
    supply_point_ref: str          # MPAN (13 digits, elec) or MPRN (10 digits, gas)
    tariff_name: str
    start_date: dt.date
    end_date: Optional[dt.date] = None
    site_label: str = ""           # e.g. "Head Office", "Warehouse 2"; blank for resi

    @property
    def is_active(self) -> bool:
        return self.end_date is None

    def is_active_at(self, as_of: dt.date) -> bool:
        if self.start_date > as_of:
            return False
        return self.end_date is None or self.end_date > as_of


@dataclass
class Account:
    """A billing account — the level the balance/ledger lives at, and the level a
    statement is produced for. Belongs to exactly one party; holds >=1 agreement."""
    account_id: str
    party_id: str
    segment: Segment
    accounting_model: AccountingModel
    invoicing_mode: InvoicingMode
    opened_date: dt.date
    agreements: List[Agreement] = field(default_factory=list)
    currency: str = "GBP"

    def add_agreement(self, agreement: Agreement) -> Agreement:
        """Attach an agreement. IDEMPOTENT on agreement_id (C-S2): re-adding the
        same agreement is harmless and does not duplicate. Order-independent (C-S1)."""
        if agreement.account_id != self.account_id:
            raise ValueError(
                f"agreement {agreement.agreement_id} belongs to account "
                f"{agreement.account_id}, not {self.account_id}"
            )
        for i, existing in enumerate(self.agreements):
            if existing.agreement_id == agreement.agreement_id:
                self.agreements[i] = agreement  # replace-in-place (idempotent upsert)
                return agreement
        self.agreements.append(agreement)
        return agreement

    def agreement(self, agreement_id: str) -> Optional[Agreement]:
        return next((a for a in self.agreements if a.agreement_id == agreement_id), None)

    def active_agreements(self, as_of: Optional[dt.date] = None) -> List[Agreement]:
        if as_of is None:
            return [a for a in self.agreements if a.is_active]
        return [a for a in self.agreements if a.is_active_at(as_of)]

    def supply_point_refs(self) -> List[str]:
        return [a.supply_point_ref for a in self.agreements]

    @property
    def fuels(self) -> List[str]:
        return sorted({a.fuel.value for a in self.active_agreements()})

    @property
    def is_dual_fuel(self) -> bool:
        active = self.active_agreements()
        return (
            any(a.fuel == Fuel.ELECTRICITY for a in active)
            and any(a.fuel == Fuel.GAS for a in active)
        )

    @property
    def is_multisite(self) -> bool:
        # more than one supply point of the same fuel ⇒ multiple sites
        elec = [a for a in self.active_agreements() if a.fuel == Fuel.ELECTRICITY]
        gas = [a for a in self.active_agreements() if a.fuel == Fuel.GAS]
        return len(elec) > 1 or len(gas) > 1

    @property
    def emits_one_statement(self) -> bool:
        """True when the whole account bills as ONE statement (dual-fuel resi,
        or an I&C account set to CONSOLIDATED)."""
        return self.invoicing_mode in (InvoicingMode.COMBINED, InvoicingMode.CONSOLIDATED)

    def summary(self) -> dict:
        return {
            "account_id": self.account_id,
            "party_id": self.party_id,
            "segment": self.segment.value,
            "accounting_model": self.accounting_model.value,
            "invoicing_mode": self.invoicing_mode.value,
            "agreement_count": len(self.agreements),
            "active_agreements": len(self.active_agreements()),
            "fuels": self.fuels,
            "is_dual_fuel": self.is_dual_fuel,
            "is_multisite": self.is_multisite,
        }


@dataclass
class Party:
    """The legal/natural person we contract with. One party may hold multiple
    accounts (e.g. a landlord with resi + a business account)."""
    party_id: str
    name: str
    party_type: PartyType

    @property
    def is_business(self) -> bool:
        return self.party_type == PartyType.ORGANISATION


class AccountHierarchy:
    """Registry over parties and accounts. The single entry point for building
    and querying the party->account->agreement->supply-point tree."""

    def __init__(self) -> None:
        self._parties: Dict[str, Party] = {}
        self._accounts: Dict[str, Account] = {}

    # --- construction ---
    def register_party(self, party_id: str, name: str, party_type: PartyType) -> Party:
        p = Party(party_id=party_id, name=name, party_type=party_type)
        self._parties[party_id] = p
        return p

    def open_account(
        self,
        account_id: str,
        party_id: str,
        segment: Segment,
        opened_date: dt.date,
        accounting_model: Optional[AccountingModel] = None,
        invoicing_mode: Optional[InvoicingMode] = None,
    ) -> Account:
        if party_id not in self._parties:
            raise KeyError(f"unknown party {party_id}; register_party first")
        acc = Account(
            account_id=account_id,
            party_id=party_id,
            segment=segment,
            accounting_model=accounting_model or default_accounting_model(segment),
            invoicing_mode=invoicing_mode or default_invoicing_mode(segment),
            opened_date=opened_date,
        )
        self._accounts[account_id] = acc
        return acc

    def add_agreement(
        self,
        account_id: str,
        agreement_id: str,
        fuel: Fuel,
        supply_point_ref: str,
        tariff_name: str,
        start_date: dt.date,
        end_date: Optional[dt.date] = None,
        site_label: str = "",
    ) -> Agreement:
        acc = self._accounts.get(account_id)
        if acc is None:
            raise KeyError(f"unknown account {account_id}; open_account first")
        ag = Agreement(
            agreement_id=agreement_id,
            account_id=account_id,
            fuel=fuel,
            supply_point_ref=supply_point_ref,
            tariff_name=tariff_name,
            start_date=start_date,
            end_date=end_date,
            site_label=site_label,
        )
        return acc.add_agreement(ag)

    # --- query ---
    def party(self, party_id: str) -> Optional[Party]:
        return self._parties.get(party_id)

    def account(self, account_id: str) -> Optional[Account]:
        return self._accounts.get(account_id)

    def accounts_for_party(self, party_id: str) -> List[Account]:
        return [a for a in self._accounts.values() if a.party_id == party_id]

    def accounts_by_segment(self, segment: Segment) -> List[Account]:
        return [a for a in self._accounts.values() if a.segment == segment]

    def account_for_supply_point(self, supply_point_ref: str) -> Optional[Account]:
        for acc in self._accounts.values():
            if supply_point_ref in acc.supply_point_refs():
                return acc
        return None

    def portfolio_summary(self) -> dict:
        accs = list(self._accounts.values())
        by_model: Dict[str, int] = {}
        by_segment: Dict[str, int] = {}
        for a in accs:
            by_model[a.accounting_model.value] = by_model.get(a.accounting_model.value, 0) + 1
            by_segment[a.segment.value] = by_segment.get(a.segment.value, 0) + 1
        return {
            "party_count": len(self._parties),
            "account_count": len(accs),
            "agreement_count": sum(len(a.agreements) for a in accs),
            "dual_fuel_accounts": sum(1 for a in accs if a.is_dual_fuel),
            "multisite_accounts": sum(1 for a in accs if a.is_multisite),
            "by_accounting_model": by_model,
            "by_segment": by_segment,
        }
