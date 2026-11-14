"""Moratorium records: the protections a supplier has itself put on an account.

THIS MODULE DOES NOT DECIDE THE LICENCE RULE. Whether the published record protects a
household from disconnection is decided once, in
`company/regulatory/priority_services_register.disconnection_protection`, from its needs
categories, the date and the household composition (atom C32; commons
`docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md`).
`can_disconnect` asks that decider and adds the records held here; it never reaches a
regulatory answer of its own.

It used to. It held a second winter, November to March, which is one month short of the
published October to March in the direction that removes protection, and a blanket rule
that no domestic customer may be disconnected in winter, which no licence condition says
(SLC 27.10's prohibition is the pensionable-age limb only; the wider all-year pledge is
Energy UK's voluntary commitment). Its `is_vulnerable` argument was accepted and never
read. None of it had a production caller, which is why it was still wrong.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional

from company.regulatory.priority_services_register import (
    WINTER_MONTHS,
    DisconnectionDetermination,
    DisconnectionProtection,
    HouseholdComposition,
    PensionableAge,
    PSRCategory,
    disconnection_protection,
    pensionable_age_from_birth_date,
)

# The supplier's own policy, not the licence: the Energy UK Vulnerability Commitment ("Safety
# Net", commons S5), adopted 2026-11-14 on canon M3's health floor. SLC 27.10/27.11 are winter
# duties; this keeps households from disconnection all year. S5 is a welfare test on "age,
# health, disability or severe financial insecurity", not category membership; this is its
# categorical reading, erring toward protection. Mental health is on the "health" ground and a
# child five or under on "age" (added after C32's fifth pass, item 5). These six PROHIBIT. Any
# other vulnerability evidence the company holds reads CANNOT_DETERMINE, because the welfare
# test is live and the company has no welfare assessment (C32's sixth pass, commons s.4). So
# sensory impairment, language, temporary life changes, the uncategorised needs and every
# agent flag block as well, and a future assessment may clear those but never the six.
SAFETY_NET_CATEGORIES = frozenset({
    PSRCategory.DISABILITY,
    PSRCategory.CHRONIC_ILLNESS,
    PSRCategory.PENSIONABLE_AGE,
    PSRCategory.MEDICAL_EQUIPMENT,
    PSRCategory.MENTAL_HEALTH,
    PSRCategory.CHILD_UNDER_5,
})


def safety_net_protection(
    categories,
    *,
    as_of: dt.date,
    household: HouseholdComposition = HouseholdComposition.UNKNOWN,
    date_of_birth: Optional[dt.date] = None,
) -> DisconnectionDetermination:
    """The supplier's own disconnection answer: the licence, then the Safety Net on top.

    Same signature as the licence decider, so a record can run its counterfactuals (an
    undetermined needs code or flag, a registration naming no need, a birth date in the
    untranscribed band) against THIS, not only against the licence. Before 2026-11-14 the net
    was read on established categories alone, so a July household whose only evidence was
    code 26 "oxygen use", an agent's `serious_illness` flag or a birth date making it 80 was
    permitted (C32 fifth Expert Hour, found before the pass ran).
    """
    licence = disconnection_protection(
        categories, as_of=as_of, household=household, date_of_birth=date_of_birth
    )
    if not licence.may_disconnect:
        return licence
    held = SAFETY_NET_CATEGORIES.intersection(categories)
    age = (pensionable_age_from_birth_date(date_of_birth, as_of)
           if date_of_birth is not None else PensionableAge.NOT_ESTABLISHED)
    if age is PensionableAge.ESTABLISHED:
        held = held | {PSRCategory.PENSIONABLE_AGE}
    if held:
        return DisconnectionDetermination(
            DisconnectionProtection.PROHIBITED,
            "Supplier policy, not the licence: this supplier operates the Energy UK Safety "
            "Net all year and does not disconnect a household holding "
            f"{', '.join(sorted(c.value for c in held))}. The licence alone would permit it.",
        )
    if age is PensionableAge.CANNOT_DETERMINE:
        return DisconnectionDetermination(
            DisconnectionProtection.CANNOT_DETERMINE,
            f"born {date_of_birth.isoformat()}: whether this is pensionable age turns on the "
            "untranscribed cohort tables, and the Safety Net would protect it all year. Ask "
            "before any disconnection.",
        )
    other = sorted(PSRCategory(c).value for c in categories)
    if other:
        return _welfare_unassessed(other)
    return licence


def _welfare_unassessed(evidence) -> DisconnectionDetermination:
    return DisconnectionDetermination(
        DisconnectionProtection.CANNOT_DETERMINE,
        f"{', '.join(evidence)}: the Safety Net is a welfare test and this supplier holds no "
        "welfare assessment, so whether this household can safeguard its welfare is not "
        "known. Assess before any disconnection.",
    )


def _held_evidence(record) -> tuple:
    """Every piece of vulnerability evidence a record holds, as labels. A flag record holds
    its flags; a register record is a registration, whatever its codes name."""
    flags = getattr(record, "flags", None)
    if flags is not None:
        return tuple(f"flagged {getattr(f, 'value', f)}" for f in flags)
    codes = tuple(f"needs code {c}" for c in record.needs_codes)
    return codes or ("on the Priority Services Register",)


def safety_net_on_record(
    record,
    as_of: dt.date,
    household: HouseholdComposition = HouseholdComposition.UNKNOWN,
    date_of_birth: Optional[dt.date] = None,
) -> DisconnectionDetermination:
    """The company's answer for a household it holds a record on (`PSRRecord` or
    `VulnerabilityRecord`).

    The record's own counterfactuals run against `safety_net_protection` first. Some evidence
    never reaches a category, so no counterfactual can see it: an uncategorised needs code
    such as post-hospital recovery, and the operational flags (bereavement, job loss, payment
    difficulty, fuel poverty, PPM self-disconnection). Until C32's sixth pass, each of those was
    permitted in July. Any evidence held now reads CANNOT_DETERMINE when nothing else blocks.
    """
    answer = record.disconnection_protection(
        as_of, household, date_of_birth, decider=safety_net_protection
    )
    if not answer.may_disconnect:
        return answer
    evidence = _held_evidence(record)
    return _welfare_unassessed(evidence) if evidence else answer


class MoratoriumType(str, Enum):
    WINTER_DOMESTIC = "winter_domestic"    # a winter hold the supplier chose to place
    VULNERABLE_YEAR_ROUND = "vulnerable_year_round"  # an all-year hold the supplier chose to place
    DEBT_MORATORIUM = "debt_moratorium"    # discretionary moratorium during hardship


class DisconnectionRisk(str, Enum):
    NO_RISK = "no_risk"
    PROTECTED = "protected"       # moratorium applies; cannot disconnect
    AT_RISK = "at_risk"           # outside moratorium; debt escalating


def is_winter_period(date: dt.date) -> bool:
    """The published winter months, read from the one decider rather than restated."""
    return date.month in WINTER_MONTHS


@dataclass(frozen=True)
class MoratoriumRecord:
    account_id: str
    moratorium_type: MoratoriumType
    start_date: dt.date
    end_date: Optional[dt.date]  # None = ongoing (vulnerable year-round)
    reason: str = ""

    def is_active(self, as_of: dt.date) -> bool:
        if as_of < self.start_date:
            return False
        if self.end_date is not None and as_of > self.end_date:
            return False
        return True

    def protection_status(self, as_of: dt.date) -> DisconnectionRisk:
        if self.is_active(as_of):
            return DisconnectionRisk.PROTECTED
        return DisconnectionRisk.NO_RISK


class WinterMoratoriumRegister:
    """Tracks the protections this supplier has placed on accounts itself.

    These are holds of our own choosing -- a hardship pause, a winter hold, an all-year
    hold -- and they only ever ADD protection to what the licence rule already gives.
    """

    def __init__(self) -> None:
        self._records: List[MoratoriumRecord] = []

    def register(self, record: MoratoriumRecord) -> MoratoriumRecord:
        self._records.append(record)
        return record

    def end_moratorium(self, account_id: str, end_date: dt.date) -> Optional[MoratoriumRecord]:
        import dataclasses
        for i, r in enumerate(self._records):
            if r.account_id == account_id and r.end_date is None:
                updated = dataclasses.replace(r, end_date=end_date)
                self._records[i] = updated
                return updated
        return None

    def active_protections(self, as_of: dt.date) -> List[MoratoriumRecord]:
        return [r for r in self._records if r.is_active(as_of)]

    def is_protected(self, account_id: str, as_of: dt.date) -> bool:
        return any(
            r.account_id == account_id and r.is_active(as_of)
            for r in self._records
        )

    def can_disconnect(
        self,
        account_id: str,
        as_of: dt.date,
        *,
        categories: Optional[Iterable[PSRCategory]] = None,
        record=None,
        household: HouseholdComposition = HouseholdComposition.UNKNOWN,
        date_of_birth: Optional[dt.date] = None,
    ) -> bool:
        """False if one of our own holds is active, or the supplier's decider does not clear
        it: the licence with the Safety Net on top (`safety_net_protection`).

        Pass the household's `record` (a `PSRRecord` or a `VulnerabilityRecord`) where one is
        held: its undetermined codes and flags, and a registration naming no need, are then
        weighed against the net as well as the licence, and any evidence the record holds
        blocks (`safety_net_on_record`). `categories` alone sees only what is established. One of the two is required on purpose: a caller that does not know the
        household's needs must say `categories=()` out loud, rather than inherit an empty set
        that reads as "nobody here is protected".
        """
        if (categories is None) == (record is None):
            raise TypeError("can_disconnect needs exactly one of categories= or record=")
        if self.is_protected(account_id, as_of):
            return False
        if record is not None:
            return safety_net_on_record(record, as_of, household, date_of_birth).may_disconnect
        return safety_net_protection(
            tuple(categories), as_of=as_of, household=household, date_of_birth=date_of_birth
        ).may_disconnect

    def vulnerable_protections(self, as_of: dt.date) -> List[MoratoriumRecord]:
        return [r for r in self.active_protections(as_of)
                if r.moratorium_type == MoratoriumType.VULNERABLE_YEAR_ROUND]

    def winter_protections(self, as_of: dt.date) -> List[MoratoriumRecord]:
        return [r for r in self.active_protections(as_of)
                if r.moratorium_type == MoratoriumType.WINTER_DOMESTIC]

    def moratorium_summary(self, as_of: dt.date) -> dict:
        active = self.active_protections(as_of)
        return {
            "total_records": len(self._records),
            "active_protections": len(active),
            "vulnerable_year_round": len(self.vulnerable_protections(as_of)),
            "winter_domestic": len(self.winter_protections(as_of)),
            "in_winter_period": is_winter_period(as_of),
        }
