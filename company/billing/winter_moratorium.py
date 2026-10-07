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
    HouseholdComposition,
    PSRCategory,
    disconnection_protection,
)


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
        categories: Iterable[PSRCategory],
        household: HouseholdComposition = HouseholdComposition.UNKNOWN,
    ) -> bool:
        """False if one of our own holds is active, or the licence rule does not clear it.

        `categories` has no default on purpose: a caller that does not know the household's
        needs categories must say `()` out loud, rather than inherit an empty set that reads
        as "nobody here is protected".
        """
        if self.is_protected(account_id, as_of):
            return False
        return disconnection_protection(
            categories, as_of=as_of, household=household
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
