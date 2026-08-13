"""The company's customer-experience desk — one book of how its customers feel.

KNIFE pass 3, `A_composition_lift` step 21, disposition register §3p. Before
this, `simulation/run_phase2b.py::main()` opened four of the company's CRM books
itself (`company.crm.satisfaction_accumulator`, `company.crm.nps_tracker`,
`company.crm.complaints`, `company.crm.payment_behaviour_analytics`), threaded
them through the renewal loop, and made every one of the company's bookkeeping
decisions on the way past: that a bill shock costs trust, that a raised
complaint costs more, that resolving one on time gives some back, that a CSAT
answer and an NPS answer land in different books, that satisfaction decays
twelve months per renewal term, that a complaint about a bill is filed under
BILLING. Four wall crossings for one process.

None of those are the world's decisions. What the world owns is that a bill
went up, that a survey was answered with a number, that a customer got in touch
and that the contact was or was not closed on time, and that a payment landed
on time, late or not at all. What those events MEAN for the supplier's view of
its own customer — which book they land in, what they cost, how fast the memory
fades — is the supplier's own CRM design, and it is ALLOWED TO BE WRONG: the
gap between this desk's satisfaction score and the world's hidden satisfaction
is a quantity the COUPLED TRIAD scores, not an error to remove.

WHAT CROSSES NOW is four observations of things the company can see on its own
systems, and four reads back. Every threshold, delta, decay rate, category and
routing rule is unreachable from the SIM.

THE DEFECT THIS CUT INVITES, named because the step template requires the
invited defect to be named rather than discovered. Before the cut, a CSAT
response and an NPS response were two DIFFERENT call sites against two
DIFFERENT objects — `_company_sat_acc.record_css_score(...)` and
`_nps_tracker.record(...)`. You could not route one to the other without
writing a visibly different line. They are now one `observe_survey_response`
distinguished by an `instrument` FIELD. A caller that fills that field in
wrongly silently posts CSAT answers into the published NPS, and every test that
drives this desk directly stays green, because the desk did exactly what it was
told. `tests/company/crm/test_customer_experience_desk.py` therefore checks the
REAL construction sites in `simulation/run_phase2b.py` by AST, with a vacuity
guard on how many it found, and mutation-proves that check fires on the swap.

THE READ DIRECTION. This module imports nothing from `simulation/` or `sim/`:
the observations arrive as frozen dataclasses through one signature each.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

from company.crm.complaints import ComplaintBook, ComplaintCategory
from company.crm.nps_tracker import NPSTracker
from company.crm.payment_behaviour_analytics import BehaviourScore, PaymentBehaviourAnalytics
from company.crm.satisfaction_accumulator import CustomerSatisfactionAccumulator

# The company's own reading of its own contract book: a fixed-term retail
# account comes round once a year, so one renewal is twelve months of
# satisfaction memory fading toward baseline. The world does not tell the desk
# how long its terms are — the supplier wrote them.
_RENEWAL_DECAY_MONTHS = 12

# The satisfaction score is published to four decimal places (the per-customer
# behavioural trajectory the Sim tab charts).
_SATISFACTION_DP = 4


class SurveyInstrument(str, Enum):
    """Which of the company's two solicited-feedback instruments answered.

    A field rather than two methods is the whole invited defect above; it is a
    field because the world genuinely dispatches both instruments at the same
    moment in the same loop and a single door keeps the seam one door wide.
    """

    CSAT = "csat"
    NPS = "nps"


@dataclass(frozen=True)
class RenewalReached:
    """A term boundary the company reached on its own book.

    `bill_shock` is the company's own billing observation (this account's unit
    rate rose more than the shock threshold against the rate this company
    itself last charged it) — not a read of anyone's felt experience.
    """

    customer_id: str
    account_id: str
    renewal_year: int
    bill_shock: bool


@dataclass(frozen=True)
class SurveyResponse:
    """A customer answered one of the company's surveys with a number.

    The company sees the RESPONSE and nothing behind it. Whether the customer
    chose to answer at all, and what they truly felt, stay the world's.
    """

    customer_id: str
    account_id: str
    instrument: SurveyInstrument
    score_0_10: int
    responded_on: date
    segment: str
    channel: str


@dataclass(frozen=True)
class CustomerContact:
    """A customer got in touch, and the contact was or was not closed on time.

    `about_bill_shock` is again the company's own billing observation, and
    `resolved_on_time` is its own service record. What the customer felt about
    the outcome is not here.
    """

    customer_id: str
    account_id: str
    contacted_on: date
    about_bill_shock: bool
    resolved_on_time: bool


@dataclass(frozen=True)
class PaymentOutcome:
    """What happened to one bill: ON_TIME, LATE or DD_FAILED, off the company's
    own cash and direct-debit returns."""

    customer_id: str
    due_date: date
    result: str
    days_late: int
    amount_gbp: float


class CustomerExperienceDesk:
    """The four books, and every decision that used to sit in the run loop."""

    def __init__(self) -> None:
        self._satisfaction = CustomerSatisfactionAccumulator()
        self._nps = NPSTracker()
        self._complaints = ComplaintBook()
        self._payments = PaymentBehaviourAnalytics()

    # ---- observations ----------------------------------------------------

    def observe_renewal(self, event: RenewalReached) -> None:
        """Age this customer's satisfaction memory, charge the bill shock if
        there was one, and snapshot the year.

        THE ORDER IS LOAD-BEARING and is the company's, not the caller's: the
        decay runs FIRST so a term's worth of forgetting is applied to the score
        the customer arrived with, and the shock is charged AFTER, against the
        aged score. Decaying afterwards would silently damp every shock by one
        month of mean-reversion. `test_the_decay_runs_before_the_shock` fires on
        the swap.
        """
        self._satisfaction.apply_monthly_decay(
            event.customer_id, months=_RENEWAL_DECAY_MONTHS
        )
        if event.bill_shock:
            self._satisfaction.record_bill_shock(event.customer_id)
        self._satisfaction.record_year_snapshot(event.customer_id, event.renewal_year)

    def observe_survey_response(self, event: SurveyResponse) -> None:
        """Post one answered survey to the book its instrument belongs in.

        The two arms are genuinely disjoint — a CSAT answer never reaches the
        NPS book and an NPS answer never moves satisfaction. That is the
        company's design (NPS is a reputation measure reported in aggregate;
        CSAT is a per-customer trust signal), and
        `test_the_two_survey_arms_do_not_collapse` proves the disjointness
        rather than assuming it.
        """
        if event.instrument is SurveyInstrument.CSAT:
            self._satisfaction.record_css_score(event.customer_id, event.score_0_10)
        elif event.instrument is SurveyInstrument.NPS:
            self._nps.record(
                event.account_id,
                event.score_0_10,
                event.responded_on,
                segment=event.segment,
                channel=event.channel,
            )
        else:  # pragma: no cover - the enum has two members
            raise ValueError(f"unknown survey instrument: {event.instrument!r}")

    def observe_contact(self, event: CustomerContact) -> None:
        """File the contact as a complaint and charge it to trust.

        The category, the description and both trust deltas are the company's
        own complaint-handling policy.
        """
        self._complaints.raise_complaint(
            event.account_id,
            ComplaintCategory.BILLING,
            event.contacted_on,
            description=(
                "bill-shock-driven contact"
                if event.about_bill_shock
                else "routine contact"
            ),
        )
        self._satisfaction.record_complaint_raised(event.customer_id)
        if event.resolved_on_time:
            self._satisfaction.record_complaint_resolved(event.customer_id)

    def observe_payment(self, event: PaymentOutcome) -> None:
        """Add one settled (or unsettled) bill to the payment behaviour history."""
        self._payments.record_payment(
            event.customer_id,
            {
                "customer_id": event.customer_id,
                "due_date": event.due_date,
                "result": event.result,
                "days_late": event.days_late,
                "amount_gbp": event.amount_gbp,
            },
        )

    # ---- the company's beliefs, read back --------------------------------

    def satisfaction_score(self, customer_id: str) -> float:
        return self._satisfaction.get_satisfaction(customer_id)

    def payment_behaviour_score(self, customer_id: str) -> Optional[BehaviourScore]:
        return self._payments.get_score(customer_id)

    def nps_annual_summary(self, year: int) -> dict:
        return self._nps.annual_summary(year)

    def complaint_annual_summary(self, year: int) -> dict:
        return self._complaints.annual_summary(year)

    def behavioural_record(self, customer_id: str) -> dict:
        """The per-customer experience record the Sim tab charts.

        Key order is part of the contract: this dict is spliced into the
        published `per_customer_behavioral` entry between the world's own
        income/life-event trajectories and its bill-shock dates.
        """
        score = self._payments.get_score(customer_id)
        metrics = self._payments.get_metrics(customer_id)
        satisfaction = self._satisfaction.get_satisfaction(customer_id)
        return {
            "payment_behaviour_score": score.value if score else None,
            "payment_behaviour_metrics": {
                "on_time_rate": metrics["on_time_rate"],
                "late_rate": metrics["late_rate"],
                "dd_fail_rate": metrics["dd_fail_rate"],
            } if metrics else None,
            "company_satisfaction_score": (
                round(satisfaction, _SATISFACTION_DP) if satisfaction else None
            ),
            "satisfaction_score_trajectory": self._satisfaction.get_trajectory(customer_id),
            "payment_miss_trajectory": self._payments.get_miss_trajectory(customer_id),
        }
