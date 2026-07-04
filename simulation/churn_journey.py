"""Churn journey state machine (Phase QL, SIM-side hidden state).

Orchestrates the dormant Phase DZ/EA/EB/ED behavioral-physics modules
(resentment_ledger, reputation_index, activation_energy) into the per-customer
journey specified in docs/design/PROCESS_MODEL.md Section 2:

    CONTENT -> IRRITATED -> IN_MARKET -> COMPARING -> (SWITCHED | STAYED_SVT)
                                                              -> POST_DECISION_WINDOW

Plus a HOME_MOVE_CHURNED forced-churn subtype that bypasses the funnel
entirely (existing simulation/household.py life-event handling triggers it).

SIM-side only: this module tracks HIDDEN state. The company must never read
ChurnJourneyState directly -- it observes only exhaust (complaints, contact
events, renewal-window flags) via company/crm/retention_risk.py and friends,
unchanged by this module. This module does not decide switch-vs-stay itself
(that stays simulation.customer_events.roll_lifecycle_event's job) -- it only
tracks whether a customer has reached the COMPARING decision point.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from company.core.activation_energy import ActionType, ActivationEnergyProfile
from company.core.reputation_index import GlobalReputationIndex
from company.core.resentment_ledger import (
    CustomerResentmentState,
    FrictionEventType,
    ResentmentLedger,
)

# A customer becomes IRRITATED well before their resentment stock reaches the
# irreversible churn-trigger threshold ResentmentLedger.check_threshold uses --
# this is the "starts silently shopping-curious" intermediate stage.
IRRITATED_THRESHOLD_FRACTION = 0.35


class ChurnJourneyState(str, Enum):
    CONTENT = "content"
    IRRITATED = "irritated"
    IN_MARKET = "in_market"
    COMPARING = "comparing"
    SWITCHED = "switched"
    STAYED_SVT = "stayed_svt"
    POST_DECISION_WINDOW = "post_decision_window"
    HOME_MOVE_CHURNED = "home_move_churned"


_TERMINAL_STATES = frozenset({
    ChurnJourneyState.SWITCHED,
    ChurnJourneyState.STAYED_SVT,
    ChurnJourneyState.HOME_MOVE_CHURNED,
})


@dataclass
class CustomerJourney:
    """One customer's position in the churn journey (SIM-side hidden state)."""

    customer_id: str
    resentment: CustomerResentmentState
    activation_energy: ActivationEnergyProfile
    state: ChurnJourneyState = ChurnJourneyState.CONTENT
    entered_in_market_at: Optional[dt.date] = None
    decided_at: Optional[dt.date] = None

    def _profile_with_gri(self, gri_multiplier: float) -> ActivationEnergyProfile:
        return ActivationEnergyProfile(
            account_id=self.activation_energy.account_id,
            base_ae_switching=self.activation_energy.base_ae_switching,
            tenure_years=self.activation_energy.tenure_years,
            is_ppm=self.activation_energy.is_ppm,
            good_resolutions=self.activation_energy.good_resolutions,
            gri_multiplier=gri_multiplier,
        )

    def advance(
        self,
        as_of: dt.date,
        gri: GlobalReputationIndex,
        renewal_window_open: bool = False,
        perceived_bill_saving_gbp: float = 0.0,
    ) -> ChurnJourneyState:
        """Advance the journey by one evaluation period.

        Does not decide switch-vs-stay -- only whether the customer has
        reached (or been forced into) the COMPARING decision point this period.
        """
        if self.state in _TERMINAL_STATES:
            return self.state

        if self.resentment.is_burned:
            # Irreversible resentment burn forces market entry regardless of
            # renewal timing, mirroring the SIM ground-truth churn trigger.
            if self.state not in (ChurnJourneyState.IN_MARKET, ChurnJourneyState.COMPARING):
                self.entered_in_market_at = self.entered_in_market_at or as_of
            self.state = ChurnJourneyState.COMPARING
            return self.state

        score = self.resentment.current_score(as_of)
        threshold = self.resentment.churn_threshold

        # At most one stage transition per evaluation period (settlement-period
        # cadence) -- an elif chain, not a fall-through cascade, so a customer
        # can be observed sitting in each intermediate state.
        if self.state == ChurnJourneyState.CONTENT:
            if score >= threshold * IRRITATED_THRESHOLD_FRACTION:
                self.state = ChurnJourneyState.IRRITATED

        elif self.state == ChurnJourneyState.IRRITATED:
            gri_mult = gri.activation_energy_multiplier(as_of)
            profile = self._profile_with_gri(gri_mult)
            ae = profile.effective_ae_for(ActionType.SWITCH_SUPPLIER)
            if renewal_window_open and perceived_bill_saving_gbp > ae:
                self.state = ChurnJourneyState.IN_MARKET
                self.entered_in_market_at = as_of

        elif self.state == ChurnJourneyState.IN_MARKET:
            self.state = ChurnJourneyState.COMPARING

        return self.state

    def record_decision(self, as_of: dt.date, switched: bool) -> ChurnJourneyState:
        """Record the terminal decision made at COMPARING (from roll_lifecycle_event)."""
        self.state = ChurnJourneyState.SWITCHED if switched else ChurnJourneyState.STAYED_SVT
        self.decided_at = as_of
        return self.state

    def record_home_move(self, as_of: dt.date) -> ChurnJourneyState:
        """Home move is a forced-churn subtype -- bypasses the funnel entirely."""
        self.state = ChurnJourneyState.HOME_MOVE_CHURNED
        self.decided_at = as_of
        return self.state

    def is_catchable(self) -> bool:
        """False for home-move churns.

        A real supplier could never predict these from behavioral precursors,
        so they must be excluded from any recall/precision metric
        (docs/design/PROCESS_MODEL.md Section 2).
        """
        return self.state != ChurnJourneyState.HOME_MOVE_CHURNED


class ChurnJourneyRegister:
    """Portfolio-level orchestrator wiring ResentmentLedger + ActivationEnergy
    + GlobalReputationIndex into per-customer journeys."""

    def __init__(self, gri: Optional[GlobalReputationIndex] = None) -> None:
        self._resentment = ResentmentLedger()
        self._journeys: Dict[str, CustomerJourney] = {}
        self.gri = gri if gri is not None else GlobalReputationIndex()

    def register_customer(
        self,
        customer_id: str,
        tenure_years: float = 0.0,
        is_ppm: bool = False,
        churn_threshold: float = 50.0,
    ) -> CustomerJourney:
        resentment_state = self._resentment._get_or_create(customer_id, churn_threshold)
        ae_profile = ActivationEnergyProfile(
            account_id=customer_id,
            base_ae_switching=100.0,
            tenure_years=tenure_years,
            is_ppm=is_ppm,
        )
        journey = CustomerJourney(
            customer_id=customer_id,
            resentment=resentment_state,
            activation_energy=ae_profile,
        )
        self._journeys[customer_id] = journey
        return journey

    def record_friction(
        self,
        customer_id: str,
        event_type: FrictionEventType,
        as_of: dt.date,
        amplifier: float = 1.0,
        description: str = "",
    ) -> None:
        self._resentment.record_friction(
            customer_id, event_type, as_of, amplifier=amplifier, description=description,
        )

    def advance(
        self,
        customer_id: str,
        as_of: dt.date,
        renewal_window_open: bool = False,
        perceived_bill_saving_gbp: float = 0.0,
    ) -> ChurnJourneyState:
        journey = self._journeys[customer_id]
        return journey.advance(
            as_of, self.gri,
            renewal_window_open=renewal_window_open,
            perceived_bill_saving_gbp=perceived_bill_saving_gbp,
        )

    def get_journey(self, customer_id: str) -> Optional[CustomerJourney]:
        return self._journeys.get(customer_id)

    def get_state(self, customer_id: str) -> Optional[ChurnJourneyState]:
        journey = self._journeys.get(customer_id)
        return journey.state if journey else None

    def portfolio_summary(self, as_of: dt.date) -> str:
        n = len(self._journeys)
        by_state: Dict[str, int] = {}
        for j in self._journeys.values():
            by_state[j.state.value] = by_state.get(j.state.value, 0) + 1
        return (
            f"Churn Journey Register: {n} customers tracked as of {as_of.isoformat()}. "
            f"By state: {by_state}."
        )
