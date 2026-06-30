"""Customer Onboarding Journey Tracker (Phase FE).

When a customer switches to the supplier, they go through an onboarding
journey with multiple stages. Poor onboarding is the leading cause of
first-year churn (customers who regret switching).

SLC 14.2: Welcome pack within 15 working days of supply start.
SLC 22.1: First bill within 3 months of supply start.
SLC 7.5: Smart meter offer within 12 months of becoming customer.

Onboarding stages:
1. SWITCH_REQUESTED: MPAS/Xoserve switch triggered
2. COOL_OFF: 14-day cooling-off period (Consumer Contracts Regs 2013)
3. OBJECTION_WINDOW: Previous supplier has 20 WD to object
4. SWITCH_CONFIRMED: Erec/Xoserve confirmed switch date
5. SUPPLY_START: Customer on supply (day 1)
6. WELCOME_PACK_ISSUED: Welcome pack sent (SLC 14.2: ≤15 WD)
7. FIRST_BILL_ISSUED: First bill (SLC 22.1: ≤3 months)
8. SMART_METER_OFFERED: Smart meter offered (SLC 7.5: ≤12m)
9. ONBOARDING_COMPLETE: All obligations met
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class OnboardingStage(str, Enum):
    SWITCH_REQUESTED = "switch_requested"
    COOL_OFF = "cool_off"
    OBJECTION_WINDOW = "objection_window"
    SWITCH_CONFIRMED = "switch_confirmed"
    SUPPLY_START = "supply_start"
    WELCOME_PACK_ISSUED = "welcome_pack_issued"
    FIRST_BILL_ISSUED = "first_bill_issued"
    SMART_METER_OFFERED = "smart_meter_offered"
    ONBOARDING_COMPLETE = "onboarding_complete"
    OBJECTION_RECEIVED = "objection_received"   # exception path


_COOL_OFF_DAYS = 14
_OBJECTION_WINDOW_WORKING_DAYS = 20
_WELCOME_PACK_WORKING_DAYS = 15
_FIRST_BILL_DAYS = 92           # 3 months approx
_SMART_METER_OFFER_DAYS = 365   # 12 months


def _add_working_days(date: dt.date, n: int) -> dt.date:
    d = date
    added = 0
    while added < n:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d


@dataclass(frozen=True)
class OnboardingEvent:
    stage: OnboardingStage
    occurred_at: dt.date
    notes: str = ""


@dataclass(frozen=True)
class OnboardingJourney:
    account_id: str
    switch_request_date: dt.date
    events: tuple  # of OnboardingEvent

    @property
    def current_stage(self) -> Optional[OnboardingStage]:
        if not self.events:
            return None
        return sorted(self.events, key=lambda e: e.occurred_at)[-1].stage

    @property
    def supply_start_date(self) -> Optional[dt.date]:
        for e in self.events:
            if e.stage == OnboardingStage.SUPPLY_START:
                return e.occurred_at
        return None

    def welcome_pack_deadline(self) -> Optional[dt.date]:
        if self.supply_start_date is None:
            return None
        return _add_working_days(self.supply_start_date, _WELCOME_PACK_WORKING_DAYS)

    def first_bill_deadline(self) -> Optional[dt.date]:
        if self.supply_start_date is None:
            return None
        return self.supply_start_date + dt.timedelta(days=_FIRST_BILL_DAYS)

    def smart_meter_offer_deadline(self) -> Optional[dt.date]:
        if self.supply_start_date is None:
            return None
        return self.supply_start_date + dt.timedelta(days=_SMART_METER_OFFER_DAYS)

    def is_welcome_pack_overdue(self, as_of: dt.date) -> bool:
        deadline = self.welcome_pack_deadline()
        if deadline is None:
            return False
        pack_issued = any(
            e.stage == OnboardingStage.WELCOME_PACK_ISSUED for e in self.events
        )
        return not pack_issued and as_of > deadline

    def is_first_bill_overdue(self, as_of: dt.date) -> bool:
        deadline = self.first_bill_deadline()
        if deadline is None:
            return False
        bill_issued = any(
            e.stage == OnboardingStage.FIRST_BILL_ISSUED for e in self.events
        )
        return not bill_issued and as_of > deadline

    def is_onboarding_complete(self) -> bool:
        return any(
            e.stage == OnboardingStage.ONBOARDING_COMPLETE for e in self.events
        )

    def journey_summary(self) -> str:
        stage = self.current_stage
        return (
            "Onboarding " + self.account_id + ": "
            "stage=" + (stage.value if stage else "none") + " "
            "start=" + str(self.supply_start_date or "TBC")
        )


class OnboardingJourneyTracker:

    def __init__(self) -> None:
        self._journeys: List[OnboardingJourney] = []

    def start_journey(
        self, account_id: str, switch_request_date: dt.date
    ) -> OnboardingJourney:
        event = OnboardingEvent(
            OnboardingStage.SWITCH_REQUESTED, switch_request_date
        )
        j = OnboardingJourney(
            account_id=account_id,
            switch_request_date=switch_request_date,
            events=(event,),
        )
        self._journeys.append(j)
        return j

    def advance_stage(
        self, account_id: str, stage: OnboardingStage, occurred_at: dt.date, notes: str = ""
    ) -> Optional[OnboardingJourney]:
        for i, j in enumerate(self._journeys):
            if j.account_id == account_id:
                new_event = OnboardingEvent(stage, occurred_at, notes)
                updated = OnboardingJourney(
                    account_id=j.account_id,
                    switch_request_date=j.switch_request_date,
                    events=j.events + (new_event,),
                )
                self._journeys[i] = updated
                return updated
        return None

    def journey_for(self, account_id: str) -> Optional[OnboardingJourney]:
        for j in self._journeys:
            if j.account_id == account_id:
                return j
        return None

    def incomplete_journeys(self) -> List[OnboardingJourney]:
        return [j for j in self._journeys if not j.is_onboarding_complete()]

    def overdue_welcome_packs(self, as_of: dt.date) -> List[OnboardingJourney]:
        return [j for j in self._journeys if j.is_welcome_pack_overdue(as_of)]

    def overdue_first_bills(self, as_of: dt.date) -> List[OnboardingJourney]:
        return [j for j in self._journeys if j.is_first_bill_overdue(as_of)]

    def onboarding_summary(self, as_of: dt.date) -> str:
        n = len(self._journeys)
        incomplete = len(self.incomplete_journeys())
        wp_overdue = len(self.overdue_welcome_packs(as_of))
        fb_overdue = len(self.overdue_first_bills(as_of))
        return (
            "Onboarding (" + str(as_of) + "): "
            + str(n) + " journeys. "
            "Incomplete: " + str(incomplete) + ". "
            "Welcome pack overdue: " + str(wp_overdue) + ". "
            "First bill overdue: " + str(fb_overdue) + "."
        )
