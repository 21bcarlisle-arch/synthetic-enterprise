"""Priority Services Register (PSR) — consumer vulnerability tracking.

UK energy suppliers maintain a PSR identifying customers with additional needs.
SLC 26B: maintain PSR, offer ≥1 core service, share with network operators.

PSR eligibility: pensionable age, disability, medical equipment dependency,
child <5, chronic illness, mental health, visual/hearing impairment, language.

Core services: priority reconnection, nominee scheme, gas safety check,
alternative format, password scheme, advance interruption notice.

THIS MODULE IS THE ONE DECIDER for the two regulatory outcomes of the obligation —
PSR eligibility and disconnection protection — because its vocabulary is the published
one (`docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md`,
census in `docs/staging/SEAT_RESULT_THE_OBLIGATION_HAS_FIVE_IMPLEMENTATIONS_AND_THE_ONE_MATCHING_THE_REGULATOR_HAS_NO_CALLER_2026-09-05.md`).
`company/crm/vulnerability_register.py` holds the OPERATIONAL vocabulary — what our own
agents flag — and delegates here rather than deciding either outcome from a table of
actions keyed by its own flags. Atom C32.

Two properties of the published rule that no numeric scale can express, and which are
why the delegation exists at all (commons §2, §3):

  * **There is no published scale.** No source assigns a weight, score or ranking to any
    needs category, so a regulatory outcome reached through a threshold is not a
    different reading of the regulation — it is not a reading of it.
  * **Disconnection protection is SEASONAL and turns on household composition.** SLC 27.10
    prohibits disconnecting a customer of pensionable age in the winter months where they
    live alone or only with others of pensionable age or under 18. A determination made
    without the date and without the composition is a determination that cannot be made,
    and this module says so rather than returning False.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class PSRCategory(str, Enum):
    PENSIONABLE_AGE = "pensionable_age"
    DISABILITY = "disability"
    MEDICAL_EQUIPMENT = "medical_equipment"
    CHILD_UNDER_5 = "child_under_5"
    CHRONIC_ILLNESS = "chronic_illness"
    MENTAL_HEALTH = "mental_health"
    VISUAL_IMPAIRMENT = "visual_impairment"
    HEARING_IMPAIRMENT = "hearing_impairment"
    LANGUAGE_SUPPORT = "language_support"


class PSRService(str, Enum):
    PRIORITY_RECONNECTION = "priority_reconnection"
    NOMINEE_SCHEME = "nominee_scheme"
    GAS_SAFETY_CHECK = "gas_safety_check"
    ALTERNATIVE_FORMAT = "alternative_format"
    PASSWORD_SCHEME = "password_scheme"
    ADVANCE_INTERRUPTION_NOTICE = "advance_interruption_notice"


class HouseholdComposition(str, Enum):
    """The limb of SLC 27.10 that turns on who else lives there (commons §2).

    UNKNOWN is a first-class member, not a missing value: a supplier very often does not
    know, and the honest determination in that case is `CANNOT_DETERMINE`, never `False`.
    """

    LIVES_ALONE = "lives_alone"
    ONLY_PENSIONABLE_OR_UNDER_18 = "only_pensionable_or_under_18"
    OTHER_ADULTS_PRESENT = "other_adults_present"
    UNKNOWN = "unknown"


class DisconnectionProtection(str, Enum):
    PROHIBITED = "prohibited"
    REASONABLE_STEPS = "reasonable_steps"
    CANNOT_DETERMINE = "cannot_determine"
    NOT_ESTABLISHED = "not_established"


@dataclass(frozen=True)
class DisconnectionDetermination:
    protection: DisconnectionProtection
    reason: str

    @property
    def may_disconnect(self) -> bool:
        """False unless the published record positively fails to protect this customer.

        `CANNOT_DETERMINE` answers False. Failing closed here costs a collections action;
        failing open disconnects someone the licence protects.
        """
        return self.protection is DisconnectionProtection.NOT_ESTABLISHED


# CITED: October to March, per Citizens Advice adviser guidance and a UK Parliament written
# answer citing SLC 27.10 (commons S4, §2). NOT November-March: `consumer_vulnerability_register`
# says Nov-Mar in its docstring, which is one month short in the direction that removes
# protection from customers who have it.
WINTER_MONTHS = frozenset({10, 11, 12, 1, 2, 3})

# The composition limb of the SLC 27.10 prohibition: lives alone, or only with others of
# pensionable age or under 18 (commons §2).
_PROHIBITION_COMPOSITIONS = frozenset(
    {HouseholdComposition.LIVES_ALONE, HouseholdComposition.ONLY_PENSIONABLE_OR_UNDER_18}
)

# The weaker all-reasonable-steps limb names three terms and only three: disabled,
# chronically sick, or of pensionable age (commons §2). MEDICAL_EQUIPMENT is deliberately
# absent — see `disconnection_protection`.
_REASONABLE_STEPS_CATEGORIES = frozenset(
    {PSRCategory.DISABILITY, PSRCategory.CHRONIC_ILLNESS, PSRCategory.PENSIONABLE_AGE}
)


def disconnection_protection(
    categories,
    *,
    as_of: date,
    household: HouseholdComposition = HouseholdComposition.UNKNOWN,
) -> DisconnectionDetermination:
    """The published disconnection rule, and the only place in `company/` that decides it.

    MEDICAL_EQUIPMENT alone returns `CANNOT_DETERMINE`, which will read as too weak until
    you read the commons. Dependency on electrically-powered medical equipment is a PSR
    needs code but is not one of the three terms in the reasonable-steps limb, and
    promoting it to automatic year-round protection is *stronger* than SLC 27.10 and
    *weaker* than the Energy UK commitment, matching neither (commons §3.3). The old
    `vulnerability_register` did exactly that, from a dict. Whether such a customer is also
    disabled or chronically sick is a fact about them we may hold; it is not established by
    this category, so this says it cannot tell.
    """
    held = set(categories)
    in_winter = as_of.month in WINTER_MONTHS

    if PSRCategory.PENSIONABLE_AGE in held and in_winter:
        if household in _PROHIBITION_COMPOSITIONS:
            return DisconnectionDetermination(
                DisconnectionProtection.PROHIBITED,
                "SLC 27.10: pensionable age, winter month, and the household is within the "
                "composition limb.",
            )
        if household is HouseholdComposition.UNKNOWN:
            return DisconnectionDetermination(
                DisconnectionProtection.CANNOT_DETERMINE,
                "SLC 27.10 turns on household composition and we do not hold it. Pensionable "
                "age and a winter month are established, so the prohibition may apply.",
            )

    if held & _REASONABLE_STEPS_CATEGORIES:
        return DisconnectionDetermination(
            DisconnectionProtection.REASONABLE_STEPS,
            "All reasonable steps to avoid disconnection: the household includes a person "
            "disabled, chronically sick, or of pensionable age.",
        )

    if PSRCategory.MEDICAL_EQUIPMENT in held:
        return DisconnectionDetermination(
            DisconnectionProtection.CANNOT_DETERMINE,
            "Dependency on electrically-powered medical equipment is a needs code but is not "
            "one of the three terms in the reasonable-steps limb; whether this customer is "
            "also disabled or chronically sick is not established by the category.",
        )

    return DisconnectionDetermination(
        DisconnectionProtection.NOT_ESTABLISHED,
        "No category held establishes a disconnection protection in the published record. "
        "The Energy UK Vulnerability Commitment is voluntary and is not modelled here.",
    )


class NeedsCodeEvidence(str, Enum):
    EVIDENCED = "evidenced"
    CANNOT_DETERMINE = "cannot_determine"
    NOT_A_NEEDS_CODE = "not_a_needs_code"


@dataclass(frozen=True)
class NeedsCodeMatch:
    term: str
    evidence: NeedsCodeEvidence
    category: PSRCategory | None
    reason: str


# An operational term maps to a needs code ONLY where it is the SAME concept. Anything
# else would be a regulatory position taken by a dict, which is the defect atom C32 was
# opened for: `ELDERLY -> PENSIONABLE_AGE` invents an age criterion the flag does not carry,
# and `CHILD_DEPENDENT -> CHILD_UNDER_5` invents an age the flag does not carry either.
_TERM_EVIDENCES_NEEDS_CODE = {
    "medical_equipment": PSRCategory.MEDICAL_EQUIPMENT,
    "disabled": PSRCategory.DISABILITY,
    "language_barrier": PSRCategory.LANGUAGE_SUPPORT,
}

# Concept overlaps a needs code, but the published criterion is NOT established by the term.
# Each reason names the missing criterion, so the refusal can itself be found wrong.
_TERM_CANNOT_DETERMINE = {
    "elderly": (
        PSRCategory.PENSIONABLE_AGE,
        "the published criterion is pensionable age; 'elderly' carries no age criterion at "
        "all, and the 75 that two modules independently invented is refuted, not unsourced.",
    ),
    "child_dependent": (
        PSRCategory.CHILD_UNDER_5,
        "the needs code is a child under five (S3) or under six (S2 — the sources disagree); "
        "a dependent child is neither.",
    ),
    "serious_illness": (
        PSRCategory.CHRONIC_ILLNESS,
        "the needs code is chronic illness or a long-term medical condition; a serious acute "
        "illness is not established to be either.",
    ),
    "mental_health": (
        PSRCategory.MENTAL_HEALTH,
        "the needs code is a mental health condition causing difficulty understanding the "
        "bill; the flag is unqualified.",
    ),
}


def needs_code_for(term: str) -> NeedsCodeMatch:
    """Grade one operational term against the published needs codes.

    Three answers, not two. The middle one is the point: a term that overlaps a needs code
    without establishing it is neither eligible nor ineligible, and collapsing it either way
    is how a mapping table comes to hold a regulatory position nobody chose.
    """
    key = term.lower()
    if key in _TERM_EVIDENCES_NEEDS_CODE:
        category = _TERM_EVIDENCES_NEEDS_CODE[key]
        return NeedsCodeMatch(
            term, NeedsCodeEvidence.EVIDENCED, category, "same concept as the published needs code."
        )
    if key in _TERM_CANNOT_DETERMINE:
        category, reason = _TERM_CANNOT_DETERMINE[key]
        return NeedsCodeMatch(term, NeedsCodeEvidence.CANNOT_DETERMINE, category, reason)
    return NeedsCodeMatch(
        term,
        NeedsCodeEvidence.NOT_A_NEEDS_CODE,
        None,
        "an operational state, not a published PSR needs code. It may order our own triage; "
        "it confers nothing.",
    )


@dataclass(frozen=True)
class PSRRecord:
    account_id: str
    categories: tuple[PSRCategory, ...]
    services_enrolled: tuple[PSRService, ...]
    registration_date: date
    review_due_date: date
    shared_with_network: bool = False
    is_active: bool = True

    @property
    def is_electricity_dependent(self) -> bool:
        return PSRCategory.MEDICAL_EQUIPMENT in self.categories

    @property
    def needs_priority_reconnection(self) -> bool:
        return (
            self.is_electricity_dependent
            or PSRCategory.PENSIONABLE_AGE in self.categories
        )

    def is_review_overdue(self, as_of: date) -> bool:
        return as_of > self.review_due_date

    @property
    def has_at_least_one_service(self) -> bool:
        return len(self.services_enrolled) > 0

    @property
    def is_compliant(self) -> bool:
        return self.has_at_least_one_service


class PriorityServicesRegister:
    """Tracks PSR records and monitors SLC 26B compliance."""

    # CITED: Ofgem, "More customers in vulnerable situations to receive help under the Priority
    # Services Register", press release 25 October 2016 — "Around 3.6 million electricity and 3
    # million gas customers (13% of customers for both fuels) are signed up to suppliers'
    # Priority Services Register." Commons S6.
    #
    # It replaces `UK_PSR_RATE_PCT = 31.0  # UK benchmark`, which cited nothing and which no
    # published figure supports. The likely origin of a number near 31 is Ofgem's finding that
    # ~40% of households COULD access PSR support and have not signed up — the eligible share,
    # not the registered one. Two different quantities, and the constant was named for neither.
    UK_PSR_REGISTERED_PCT_2016 = 13.0
    UK_PSR_REGISTERED_PCT_AS_OF = date(2016, 10, 25)

    def __init__(self) -> None:
        self._records: dict[str, PSRRecord] = {}

    def register(self, record: PSRRecord) -> PSRRecord:
        self._records[record.account_id] = record
        return record

    def get_record(self, account_id: str) -> PSRRecord | None:
        return self._records.get(account_id)

    def deregister(self, account_id: str) -> None:
        record = self._records.get(account_id)
        if record:
            self._records[account_id] = PSRRecord(
                account_id=record.account_id,
                categories=record.categories,
                services_enrolled=record.services_enrolled,
                registration_date=record.registration_date,
                review_due_date=record.review_due_date,
                shared_with_network=record.shared_with_network,
                is_active=False,
            )

    @property
    def active_records(self) -> list[PSRRecord]:
        return [r for r in self._records.values() if r.is_active]

    @property
    def electricity_dependent(self) -> list[PSRRecord]:
        return [r for r in self.active_records if r.is_electricity_dependent]

    @property
    def priority_reconnection_customers(self) -> list[PSRRecord]:
        return [r for r in self.active_records if r.needs_priority_reconnection]

    @property
    def non_compliant_records(self) -> list[PSRRecord]:
        return [r for r in self.active_records if not r.is_compliant]

    @property
    def network_shared_count(self) -> int:
        return sum(1 for r in self.active_records if r.shared_with_network)

    def overdue_reviews(self, as_of: date) -> list[PSRRecord]:
        return [r for r in self.active_records if r.is_review_overdue(as_of)]

    def psr_penetration_pct(self, total_domestic_accounts: int) -> float:
        if total_domestic_accounts == 0:
            return 0.0
        return len(self.active_records) / total_domestic_accounts * 100

    def penetration_against_published(self, total_domestic_accounts: int) -> dict:
        """Our registered share beside the only published one we could source, WITH ITS DATE.

        The published figure is nine years old and the register has grown since; Ofgem
        broadened eligibility again from January. So the gap is a prompt to look, never a
        target — a book below 13% is not thereby non-compliant, and a book above it is not
        thereby done. The date travels with the number for exactly that reason.
        """
        return {
            "our_pct": self.psr_penetration_pct(total_domestic_accounts),
            "published_pct": self.UK_PSR_REGISTERED_PCT_2016,
            "published_as_of": self.UK_PSR_REGISTERED_PCT_AS_OF,
            "published_is_stale": True,
            "note": (
                "Ofgem, 25 Oct 2016, registered share for both fuels. Not a current rate and "
                "not the eligible share (~40% of households, Ofgem survey Jan-Feb 2024)."
            ),
        }

    def psr_summary(self, as_of: date) -> str:
        n = len(self.active_records)
        n_elec_dep = len(self.electricity_dependent)
        n_non_compliant = len(self.non_compliant_records)
        n_overdue = len(self.overdue_reviews(as_of))
        lines = [
            "Priority Services Register (SLC 26B)",
            "Active: {:d} | Electricity-dependent: {:d}".format(n, n_elec_dep),
            "Non-compliant (no services): {:d} | Reviews overdue: {:d}".format(
                n_non_compliant, n_overdue
            ),
        ]
        return chr(10).join(lines)
