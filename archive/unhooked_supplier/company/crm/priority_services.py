from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional, Dict


class PSRNeed(str, Enum):
    LARGE_PRINT_BILLS = "large_print_bills"
    BRAILLE_BILLS = "braille_bills"
    AUDIO_BILLS = "audio_bills"
    ADVANCE_NOTICE = "advance_notice"           # advance notice before any interruption
    NOMINEE_BILLING = "nominee_billing"         # bills sent to a named carer/nominee
    MEDICALLY_DEPENDENT = "medically_dependent" # relies on electricity for medical equipment
    HEARING_IMPAIRED = "hearing_impaired"
    VISUALLY_IMPAIRED = "visually_impaired"
    CHRONIC_ILLNESS = "chronic_illness"
    OTHER = "other"


_REVIEW_PERIOD_DAYS = 365


@dataclass
class PSREntry:
    customer_id: str
    needs: List[PSRNeed]
    added_date: date
    review_due_date: date
    nominee_name: Optional[str] = None
    nominee_contact: Optional[str] = None

    def is_due_for_review(self, as_of: date) -> bool:
        return as_of >= self.review_due_date

    def is_medically_dependent(self) -> bool:
        return PSRNeed.MEDICALLY_DEPENDENT in self.needs

    def requires_nominee_contact(self) -> bool:
        return PSRNeed.NOMINEE_BILLING in self.needs


@dataclass
class PSRBook:
    """Priority Services Register — tracks customers with specialist service needs."""

    _entries: Dict[str, PSREntry] = field(default_factory=dict)

    def register(
        self,
        customer_id: str,
        needs: List[PSRNeed],
        added_date: date,
        nominee_name: Optional[str] = None,
        nominee_contact: Optional[str] = None,
    ) -> PSREntry:
        review_due = added_date + timedelta(days=_REVIEW_PERIOD_DAYS)
        entry = PSREntry(
            customer_id=customer_id,
            needs=list(needs),
            added_date=added_date,
            review_due_date=review_due,
            nominee_name=nominee_name,
            nominee_contact=nominee_contact,
        )
        self._entries[customer_id] = entry
        return entry

    def update_needs(self, customer_id: str, needs: List[PSRNeed]) -> bool:
        if customer_id not in self._entries:
            return False
        self._entries[customer_id].needs = list(needs)
        return True

    def is_registered(self, customer_id: str) -> bool:
        return customer_id in self._entries

    def get(self, customer_id: str) -> Optional[PSREntry]:
        return self._entries.get(customer_id)

    def due_for_review(self, as_of: date) -> List[PSREntry]:
        return [e for e in self._entries.values() if e.is_due_for_review(as_of)]

    def medically_dependent_customers(self) -> List[str]:
        """Customer IDs relying on electricity for medical equipment (priority in outages)."""
        return [cid for cid, e in self._entries.items() if e.is_medically_dependent()]

    def nominee_contacts(self) -> List[PSREntry]:
        return [e for e in self._entries.values() if e.requires_nominee_contact()]

    def portfolio_summary(self) -> dict:
        n = len(self._entries)
        med_dep = len(self.medically_dependent_customers())
        with_nominee = sum(1 for e in self._entries.values() if e.nominee_name)
        need_counts: Dict[str, int] = {}
        for e in self._entries.values():
            for need in e.needs:
                need_counts[need.value] = need_counts.get(need.value, 0) + 1
        return {
            "total_registered": n,
            "medically_dependent": med_dep,
            "with_nominee": with_nominee,
            "need_breakdown": need_counts,
        }
