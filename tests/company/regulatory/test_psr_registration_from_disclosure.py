"""The company's Priority Services Register is built from disclosures only, and nothing on the
company side can read the world's latent vulnerability (director, 2026-10-08)."""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import pytest

from company.interfaces.supply_book import open_priority_services_register
from company.regulatory.priority_services_register import (
    DisconnectionProtection,
    HouseholdComposition,
    PSRCategory,
    PSRRecord,
    disconnection_protection,
)
from interface.contracts.registration_loss_seam import CSS_SENDER
from simulation.registration_loss_feed import CSS_PROVIDER_CREDENTIAL
from simulation.vulnerability_state import DisclosedRegistration, wire_registrations

_ROOT = Path(__file__).resolve().parents[3]
_ON = dt.date(2016, 4, 1)
# C1, its gas leg C1g and C2 are on the hand-authored roster, so the supply book holds them.


def _wire(account: str, codes=()):
    return wire_registrations([DisclosedRegistration(account, _ON, codes)])[0]


def test_a_disclosure_registers_the_account_from_its_own_date():
    """Defect: a notice that reaches the register and registers nothing, or on another date."""
    register = open_priority_services_register()
    register.receive_registration_wire(_wire("C1"))
    record = register.get_record("C1")
    assert record is not None and record.registration_date == _ON
    assert [r.account_id for r in register.active_records] == ["C1"]


def test_a_disclosure_for_a_point_the_book_does_not_hold_registers_nothing_and_says_why():
    """Defect: the register admitting a disclosure without asking the supply book, so a point
    this supplier does not supply lands on its PSR. Partition: a held point IS registered."""
    from company.regulatory.priority_services_register import NOT_ON_THIS_BOOK

    register = open_priority_services_register()
    assert register.receive_registration_wire(_wire("NOT-ON-THE-BOOK-1")) is None
    assert register.receive_registration_wire(_wire("C1")) is not None
    assert [r.account_id for r in register.active_records] == ["C1"]
    assert register.registration_exceptions() == [{
        "supply_point_id": "NOT-ON-THE-BOOK-1", "registered_on": _ON.isoformat(),
        "reason": NOT_ON_THIS_BOOK}]


def test_a_registration_naming_codes_with_no_mapping_is_refused_with_its_reason():
    """Defect: a needs code silently registered as no category, so a protection owed is lost."""
    with pytest.raises(ValueError, match="no needs-code -> PSRCategory mapping"):
        open_priority_services_register().receive_registration_wire(_wire("C1", (14,)))


def test_a_wire_carrying_a_latent_state_or_from_another_sender_is_refused():
    """Defect: the company's belt missing -- a notice carrying the world's financial flag decoded
    and registered, or a registration accepted from a sender that is not the household."""
    leaking = _wire("C1")
    leaking["envelope"]["payload"]["financially_vulnerable"] = True
    with pytest.raises(Exception, match="world truth"):
        open_priority_services_register().receive_registration_wire(leaking)
    # An authenticated participant that is not the household's channel: the switching service.
    relayed = _wire("C1")
    relayed["sender"] = relayed["envelope"]["sender"] = CSS_SENDER
    relayed["credential"] = CSS_PROVIDER_CREDENTIAL
    with pytest.raises(ValueError, match="not the household disclosure channel"):
        open_priority_services_register().receive_registration_wire(relayed)
    open_priority_services_register().receive_registration_wire(_wire("C1g"))


def test_protection_for_a_registered_customer_is_still_decided_by_its_categories_alone():
    """Defect: the knowledge-source change moving the protection a REGISTERED customer gets. The
    published rule is asked of the record's categories, so the same categories give the same
    answer whether the record came from a disclosure or was registered directly."""
    register = open_priority_services_register()
    register.register(PSRRecord("D-1", (PSRCategory.PENSIONABLE_AGE,), (), _ON, _ON))
    register.receive_registration_wire(_wire("C2"))
    winter = dt.date(2016, 12, 1)
    alone = HouseholdComposition.LIVES_ALONE
    direct = disconnection_protection(register.get_record("D-1").categories, as_of=winter,
                                      household=alone)
    disclosed = disconnection_protection(register.get_record("C2").categories, as_of=winter,
                                         household=alone)
    assert direct.protection is DisconnectionProtection.PROHIBITED
    assert disclosed.protection is DisconnectionProtection.NOT_ESTABLISHED


_LATENT_NAMES = {"psr_type_vulnerable", "financially_vulnerable", "discloses_psr",
                 "vulnerability_state", "VulnerabilityState"}


def _offenders(roots) -> list[str]:
    found = []
    for root in roots:
        for path in sorted((_ROOT / root).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                module = getattr(node, "module", None) if isinstance(node, ast.ImportFrom) else None
                names = ({a.name for a in node.names} if isinstance(node, ast.Import) else set())
                if (module and module.endswith("vulnerability_state")) or any(
                        n.endswith("vulnerability_state") for n in names):
                    found.append(f"{path.relative_to(_ROOT)} imports {module or names}")
                if isinstance(node, ast.Attribute) and node.attr in _LATENT_NAMES:
                    found.append(f"{path.relative_to(_ROOT)} reads .{node.attr}")
                if isinstance(node, ast.Constant) and node.value in _LATENT_NAMES:
                    found.append(f"{path.relative_to(_ROOT)} names {node.value!r}")
    return found


def test_no_company_or_saas_module_reads_the_latent_vulnerability_states():
    """Defect: the company reading the world's hidden state -- the PSR-type flag, the financial
    flag or the disclosure roll -- instead of the registration that crossed the seam. The scan
    is first shown able to fire on the world module that holds the states."""
    assert _offenders(["simulation"])
    assert _offenders(["company", "saas"]) == []
