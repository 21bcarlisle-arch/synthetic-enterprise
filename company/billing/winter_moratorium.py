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

import dataclasses
import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional

from company.regulatory.priority_services_register import (
    DO_NOT_INSTALL_CHECK,
    WINTER_MONTHS,
    DisconnectionDetermination,
    DisconnectionProtection,
    HouseholdComposition,
    PensionableAge,
    ProtectionRecord,
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


# ---------------------------------------------------------------------------
# THE ENFORCEMENT GATE: every action the company can take on a domestic debt, against every
# protection ground, in one table (C32, 2026-11-15; commons
# psr_eligibility_and_disconnection_protection.md s.5, which publishes the same table with each
# cell's clause and file:line). Passes three to eight each found one more limb of one obligation
# missing; the table lists every cell so the next one is not found by a reviewer first.
# `may_take` applies exactly the cells the table marks COVERED, and the control
# (tests/company/billing/test_the_enforcement_table.py) engages each one and asserts refusal.
# ---------------------------------------------------------------------------

class EnforcementAction(str, Enum):
    DISCONNECTION = "disconnection"
    WARRANT_PPM_INSTALL = "warrant_ppm_install"
    REMOTE_SWITCH_TO_PREPAY = "remote_switch_to_prepay_mode"
    CONSENT_PPM_OFFER = "consent_ppm_offer"
    AGENCY_HANDOFF = "debt_path_referral_and_agency_handoff"
    SELF_DISCONNECTION_SUPPORT = "self_disconnection_support"
    #: SLC 14.4(a): blocking a domestic household's switch away for Outstanding Charges. Live in
    #: every run (`company/market/transfer_objection_register.decide_debt_objection`).
    DEBT_OBJECTION = "debt_objection_on_switching"
    #: Debt recovered from a prepayment meter's top-ups after a move. The world takes the weekly
    #: deduction; the company asks this row at every read (`_read_meter_recoveries`) and, refused,
    #: pauses it through `suspend_deduction` (C37).
    METER_RECOVERY = "recovery_through_the_meter"


#: The actions no company path takes today. Listed so a route built later meets the gate's
#: answer, not an empty one; `may_take` answers them on the same table as the rest.
UNROUTED_ACTIONS = frozenset({EnforcementAction.DISCONNECTION, EnforcementAction.WARRANT_PPM_INSTALL,
                              EnforcementAction.REMOTE_SWITCH_TO_PREPAY,
                              EnforcementAction.AGENCY_HANDOFF})


@dataclass(frozen=True)
class EnforcementCase:
    """What the company holds about one household on one day, as far as enforcement turns on it.

    Every precondition defaults to the answer that refuses: an unrecorded step is an untaken one.
    `record` / `categories` follow `can_disconnect`: exactly one, where an action's table reads them.
    """
    account_id: str
    as_of: dt.date
    record: object = None
    categories: Optional[tuple] = None
    household: HouseholdComposition = HouseholdComposition.UNKNOWN
    date_of_birth: Optional[dt.date] = None
    own_hold: bool = False
    breathing_space: bool = False
    #: SLC 27.6(a)(ii)/27.8: an arrangement offer the household ANSWERED (agreed at an instalment,
    #: or declined). An offer with no answer named no instalment, so it is not a 27.8 offer (C32
    #: tenth pass, item 5: 69 of 69 live offers were unanswered and each satisfied this column).
    arrangement_offered: bool = False
    #: SLC 27.6(a)(iii): the dated S&RP finding (`company/billing/prepayment_suitability.py`). A
    #: bare True carries no date, so the gate cannot say it was in effect, and refuses it.
    suitability: Optional[ProtectionRecord] = None
    #: SLC 27A: the dated record of the self-disconnection watch that would cover this household.
    self_disconnection_watch: Optional[ProtectionRecord] = None
    ppm_route_exhausted: bool = False
    #: SLC 28B: the four dated precondition records (`SLC28B_PRECONDITIONS`), each its own record.
    involuntary_preconditions: tuple = ()


@dataclass(frozen=True)
class EnforcementDetermination:
    action: EnforcementAction
    refusals: tuple  # every ground that refuses, as (column, reason); empty means permitted

    @property
    def permitted(self) -> bool:
        return not self.refusals

    @property
    def reason(self) -> str:
        return "; ".join(r for _c, r in self.refusals)


NO_SUITABILITY_FINDING = ("no safe-and-reasonably-practicable finding is recorded for this household, "
                          "so no prepayment meter is offered (SLC 27.6(a)(iii); PPM guidance via 28.4)")
NOT_SUITABLE = "the household's safe-and-reasonably-practicable finding is negative (SLC 27.6(a)(iii))"
NO_SELF_DISCONNECTION_WATCH = (
    "no self-disconnection watch would cover this household on a prepayment meter, and SLC 27A.1 "
    "requires all reasonable steps to identify self-disconnection from the day it is on one")
SELF_DISCONNECTING = (
    "the watch has seen this household's meter run out of credit, and SLC 27A.1(b) answers that with "
    "support under 27.8: the weekly deduction is paused (27.8A(d)(iv)) until a review of its ability "
    "to pay re-instates it, and no such review is built, so the pause holds")
NO_ARRANGEMENT_OFFERED = ("no affordable arrangement has been offered and answered on this debt, and SLC "
                          "27.6/27.8 order that offer before any recovery step (27.8C: charges not "
                          "recoverable until 27.5-27.8 are met); an offer the household has not "
                          "answered calculated no instalment under 27.8, so it is not one (27.6(a)(ii))")
NOT_PPM_FIRST = ("SLC 27.9: no disconnection for unpaid charges until all reasonable steps to recover "
                 "them through a prepayment meter are taken, and none is recorded")
IN_BREATHING_SPACE = ("a Debt Respite moratorium is active: SI 2020/1311 reg 7(7)(a) forbids any step "
                      "to collect the moratorium debt")
OWN_HOLD = "this supplier has placed its own hold on the account (WinterMoratoriumRegister)"
NO_INVOLUNTARY_PRECONDITIONS = (
    "SLC 28B: an involuntary prepayment meter needs the Debt Trigger, at least 10 contact attempts, a "
    "Site Welfare Visit and a do-not-install check (75+ without support, a child under 2), each a "
    "dated record in effect on the day")

#: The day each dated clause came into force. 27A: Ofgem's self-disconnection decision of Oct
#: 2020, in force 15 Dec 2020 (`docs/market_research/company_debt_management.md`, 27A note).
#: 28B: Ofgem's PPM licence decision of Sep 2023, licence from 8 Nov 2023 after the Code of
#: Practice of 18 Apr 2023 (`docs/market_research/debt_and_collections.md` s.3).
CLAUSE_IN_FORCE = {"slc_27a_self_disconnection": dt.date(2020, 12, 15),
                   "slc_28b_involuntary_ppm": dt.date(2023, 11, 8)}

SELF_DISCONNECTION_WATCH = "slc_27a_self_disconnection_watch"
SAFE_AND_PRACTICABLE = "slc_27_6_a_iii_safe_and_practicable"
DEBT_TRIGGER = "slc_28b_debt_trigger"
CONTACT_ATTEMPTS = "slc_28b_contact_attempts"
SITE_WELFARE_VISIT = "slc_28b_site_welfare_visit"
#: 28B's four preconditions, each its own dated record (ninth pass, item 6). The do-not-install
#: check is a household fact and is made in the PSR module.
SLC28B_PRECONDITIONS = (DEBT_TRIGGER, CONTACT_ATTEMPTS, SITE_WELFARE_VISIT, DO_NOT_INSTALL_CHECK)
#: "At least 10 attempts to contact, through several channels" (SLC 28B / Code of Practice 2023;
#: `docs/market_research/debt_and_collections.md` s.3). The channel mix is not checked: GAP.
SLC28B_MIN_CONTACT_ATTEMPTS = 10


def _in_force(ground: str, on: dt.date) -> str:
    """The clause's standing on `on`. Before it is in force this supplier applies it as its own
    policy (design choice, erring toward protection, F11): the refusal stands and says so, rather
    than an anachronistic licence citation or a permission the floor would not give."""
    start = CLAUSE_IN_FORCE[ground]
    if on >= start:
        return f"in force from {start}"
    return (f"not in force until {start}; applied before then as this supplier's own policy, "
            "a design choice")


def _self_disconnection_check(case, action):
    """No usable watch refuses every row. On recovery through the meter, a watch that has SEEN
    an interruption refuses too: 27A.1(b) answers it with support under 27.8, and recovery at a
    rate the household is going off supply under is not one set on its ability to pay (C37)."""
    record = case.self_disconnection_watch
    why = NO_SELF_DISCONNECTION_WATCH if record is None else record.unusable_on(case.as_of)
    if why is None and action is EnforcementAction.METER_RECOVERY:
        seen = sorted(d for d in record.evidence if d <= case.as_of)
        if seen:
            why = f"{SELF_DISCONNECTING} (interruptions seen: {', '.join(map(str, seen))})"
    if why is None:
        return None
    return f"{why} (SLC 27A: {_in_force('slc_27a_self_disconnection', case.as_of)})"


def _involuntary_check(case, _action):
    held = {r.kind: r for r in case.involuntary_preconditions}
    why = []
    for kind in SLC28B_PRECONDITIONS:
        record = held.get(kind)
        if record is None:
            why.append(f"no {kind} is recorded")
            continue
        bad = record.unusable_on(case.as_of)
        if bad is None and kind == CONTACT_ATTEMPTS:
            n = sum(1 for d in record.evidence if d <= case.as_of)
            if n < SLC28B_MIN_CONTACT_ATTEMPTS:
                bad = (f"{kind}: {n} attempts recorded by {case.as_of}; 28B needs at least "
                       f"{SLC28B_MIN_CONTACT_ATTEMPTS}")
        if bad is not None:
            why.append(bad)
    if not why:
        return None
    return (f"{NO_INVOLUNTARY_PRECONDITIONS} (SLC 28B: "
            f"{_in_force('slc_28b_involuntary_ppm', case.as_of)}): " + "; ".join(why))


def _decider_answers(case: EnforcementCase):
    if (case.categories is None) == (case.record is None):
        raise TypeError("this action reads the household's needs: pass exactly one of categories= "
                        "or record= (categories=() out loud when none are held)")
    cats = tuple(case.categories) if case.categories is not None else tuple(case.record.categories)
    licence = disconnection_protection(cats, as_of=case.as_of, household=case.household,
                                       date_of_birth=case.date_of_birth)
    if case.record is not None:
        company = safety_net_on_record(case.record, case.as_of, case.household, case.date_of_birth)
    else:
        company = safety_net_protection(cats, as_of=case.as_of, household=case.household,
                                        date_of_birth=case.date_of_birth)
    return licence, company


def _licence_check(case, _action):
    licence, _ = _decider_answers(case)
    return None if licence.may_disconnect else licence.reason


def _company_layer_check(case, action):
    """For disconnection, the supplier's decider (licence, then the Safety Net). For any other
    action the licence's winter clauses do not govern it, so what bars it is the evidence alone:
    any vulnerability evidence held, or a birth date that is or may be pensionable age, means the
    welfare test is live and unassessed. Design choice (commons s.5), erring toward protection."""
    if action is EnforcementAction.DISCONNECTION:
        _, company = _decider_answers(case)
        return None if company.may_disconnect else company.reason
    if (case.categories is None) == (case.record is None):
        raise TypeError("this action reads the household's needs: pass exactly one of categories= "
                        "or record= (categories=() out loud when none are held)")
    evidence = (list(_held_evidence(case.record)) if case.record is not None
                else sorted(PSRCategory(c).value for c in case.categories))
    if case.date_of_birth is not None and pensionable_age_from_birth_date(
            case.date_of_birth, case.as_of) is not PensionableAge.NOT_ESTABLISHED:
        evidence.append(f"born {case.date_of_birth.isoformat()}")
    return _welfare_unassessed(evidence).reason if evidence else None


def _suitability_check(case, _action):
    record = case.suitability
    if record is None:
        return NO_SUITABILITY_FINDING
    if not isinstance(record, ProtectionRecord) or record.kind != SAFE_AND_PRACTICABLE:
        return f"{NO_SUITABILITY_FINDING}; {record!r} is not a dated S&RP finding"
    why = record.unusable_on(case.as_of)
    if why is None:
        return None
    if dataclasses.replace(record, met=True).unusable_on(case.as_of) is None:
        return f"{NOT_SUITABLE}: " + "; ".join(record.evidence)  # in effect, and it found the bar
    return f"{why} (SLC 27.6(a)(iii))"


_CHECKS = {
    "arrangement": lambda c, _a: None if c.arrangement_offered else NO_ARRANGEMENT_OFFERED,
    "suitability": _suitability_check,
    "ppm_first": lambda c, _a: None if c.ppm_route_exhausted else NOT_PPM_FIRST,
    "licence": _licence_check,
    "company_layer": _company_layer_check,
    "self_disconnection": _self_disconnection_check,
    "involuntary": _involuntary_check,
    "own_hold": lambda c, _a: OWN_HOLD if c.own_hold else None,
    "breathing_space": lambda c, _a: IN_BREATHING_SPACE if c.breathing_space else None,
}

#: The columns: every protection ground, the clause it rests on, and the check that reads it. Three
#: licence columns share one decider; each is engaged separately by the control.
PROTECTION_GROUNDS = {
    "slc_27_5_to_27_8_ability_to_pay": ("SLC 27.5, 27.5B, 27.6, 27.8, 27.8A, 27.8C", "arrangement"),
    "slc_27_6_a_iii_safe_and_practicable": ("SLC 27.6(a)(iii); S&RP guidance via 28.4", "suitability"),
    "slc_27_9_ppm_before_disconnection": ("SLC 27.9, 27.9A", "ppm_first"),
    "slc_27_10_winter_pensionable": ("SLC 27.10", "licence"),
    "slc_27_11_winter_reasonable_steps": ("SLC 27.11", "licence"),
    "slc_27_11a_ascertain": ("SLC 27.11(A)", "licence"),
    "slc_27a_self_disconnection": ("SLC 27A.1", "self_disconnection"),
    "slc_28_15_proportionate": ("SLC 28.15", None),
    "slc_28b_involuntary_ppm": ("SLC 28B; PPM guidance s.5.2, s.5.6", "involuntary"),
    "own_hold_winter_moratorium": ("supplier policy: WinterMoratoriumRegister", "own_hold"),
    "energy_uk_safety_net": ("Energy UK Vulnerability Commitment (voluntary; adopted)", "company_layer"),
    "psr_needs_codes": ("SLC 26; needs codes (CVS 2025 App. 6)", "company_layer"),
    "breathing_space": ("SI 2020/1311 reg 7", "breathing_space"),
}

COVERED, GAP, NOT_APPLICABLE = "covered", "GAP", "n/a"
_D, _W, _R, _C, _A, _S, _O = (EnforcementAction.DISCONNECTION, EnforcementAction.WARRANT_PPM_INSTALL,
                              EnforcementAction.REMOTE_SWITCH_TO_PREPAY,
                              EnforcementAction.CONSENT_PPM_OFFER, EnforcementAction.AGENCY_HANDOFF,
                              EnforcementAction.SELF_DISCONNECTION_SUPPORT,
                              EnforcementAction.DEBT_OBJECTION)


def _row(covered=(), gap=()):
    return {g: (COVERED if g in covered else GAP if g in gap else NOT_APPLICABLE)
            for g in PROTECTION_GROUNDS}


_LICENCE = ("slc_27_10_winter_pensionable", "slc_27_11_winter_reasonable_steps", "slc_27_11a_ascertain")
_ALWAYS = ("slc_27_5_to_27_8_ability_to_pay", "own_hold_winter_moratorium", "breathing_space")
_PPM = ("slc_27_6_a_iii_safe_and_practicable", "slc_27a_self_disconnection")

#: THE TABLE. A cell is COVERED (the gate refuses when the ground is engaged), GAP (the ground
#: may bar the action and the published record read here does not say how; named in the commons)
#: or n/a (the clause does not govern this action). No cell is "absent": that state is what this
#: table exists to remove. The support row is never barred: support is not a step to collect.
ENFORCEMENT_TABLE = {
    _D: _row(_ALWAYS + _LICENCE + ("slc_27_9_ppm_before_disconnection", "energy_uk_safety_net",
                                   "psr_needs_codes"),
             gap=("slc_28_15_proportionate",)),
    _W: _row(_ALWAYS + _PPM + ("slc_28b_involuntary_ppm", "energy_uk_safety_net", "psr_needs_codes"),
             gap=("slc_28_15_proportionate",)),
    _R: _row(_ALWAYS + _PPM + ("slc_28b_involuntary_ppm", "energy_uk_safety_net", "psr_needs_codes"),
             gap=("slc_28_15_proportionate",)),
    _C: _row(_ALWAYS + _PPM, gap=("psr_needs_codes",)),
    _A: _row(_ALWAYS + ("energy_uk_safety_net", "psr_needs_codes"), gap=("slc_28_15_proportionate",)),
    _S: _row(),
    # The objection keeps the household supplied, so the winter, PPM and Safety Net cells do not
    # govern it. Breathing Space: reg 7(7)(a) "a step to collect", read as covering a block whose
    # notice tells the household to pay to leave (a reading, commons s.5). Own hold: design choice.
    # 27.8 order, PSR needs and 28.15: no published text read says how they bear on an objection.
    _O: _row(("own_hold_winter_moratorium", "breathing_space"),
             gap=("slc_27_5_to_27_8_ability_to_pay", "psr_needs_codes", "slc_28_15_proportionate")),
    # A deduction from top-ups to recover moratorium debt is plainly "a step to collect" (reg
    # 7(7)(a)). Own hold: design choice. 27A: a watch that has seen an interruption pauses it
    # (27A.1(b) via 27.8A(d)(iv); C37, commons s.5). Ability to pay on the rate, the welfare
    # columns and 28.15: not read for recovery.
    EnforcementAction.METER_RECOVERY: _row(
        ("own_hold_winter_moratorium", "breathing_space", "slc_27a_self_disconnection"),
        gap=("slc_27_5_to_27_8_ability_to_pay", "energy_uk_safety_net", "psr_needs_codes",
             "slc_28_15_proportionate")),
}

_CONTACT = ("dunning contact: a step to collect in Breathing Space, held by the one selector "
            "(arrears_engine.select_dunning_step returns MORATORIUM_HOLD). No row, so the ground has "
            "one implementation; no other column bars a contact")

#: THE CENSUS (ninth pass, item 12): every name under which the company acts on a domestic debt,
#: and the row that governs it or why it has none. The names are every stage the domestic
#: collections desk can enter (`collections_journey.lawful_successors`), every call the desk makes
#: through its world door (`self._plan_offers`), the world-asked objection door
#: (`company/interfaces/transfer_objection.__all__`) and the objection register's write. The control
#: derives that set from the code and reds on a name missing here or here and gone from the code.
DEBT_STEP_CENSUS = {
    "missed_payment": "a record that a bill went unpaid; nothing is done to the household",
    "reminder": _CONTACT, "reminder_2": _CONTACT, "final_notice": _CONTACT,
    "repayment_plan_offer": _CONTACT, "arrangement_offered": _CONTACT,
    "repayment_plan_reoffer": _CONTACT, "answer_plan_offer": _CONTACT,
    "moratorium_hold": "the hold itself: no step is taken",
    "prepayment_or_debt_agency": EnforcementAction.CONSENT_PPM_OFFER,
    "prepayment_offered": EnforcementAction.CONSENT_PPM_OFFER,
    "request_prepayment_move": EnforcementAction.CONSENT_PPM_OFFER,
    "prepayment_withheld": "the gate's refusal of the Consent offer, recorded",
    "prepayment": "the world changed the meter on a Consent offer: the offer's outcome",
    "arrangement": "the household agreed a plan: an outcome",
    "cured": "the debt is paid: an outcome",
    "write_off": "relief: the company gives the debt up",
    "get_plan_instalments": "a read of what the household paid on a plan it agreed",
    "get_meter_recoveries": EnforcementAction.METER_RECOVERY,
    "suspend_deduction": ("the pause the desk lodges when the recovery_through_the_meter row "
                          "refuses: it stops a step, it takes none"),
    "get_meter_supply_events": ("the 27A watch's read of what the meter reported (SLC 27A.1): a duty "
                                "to watch, the self_disconnection_support row, not a step to collect"),
    "ask_prepayment_suitability": ("a question the household answers at the Consent rung; its "
                                   "answers make the S&RP finding the offer's gate reads"),
    "request_debt_objection": EnforcementAction.DEBT_OBJECTION,
    "raise_objection": EnforcementAction.DEBT_OBJECTION,
}


def may_take(action: EnforcementAction, case: EnforcementCase) -> EnforcementDetermination:
    """Whether the company may take `action` on this household now: every COVERED cell of its row
    is asked, and each that refuses is named. One call per action; no route may skip it."""
    refusals, asked, said = [], set(), set()
    for ground, state in ENFORCEMENT_TABLE[action].items():
        check = PROTECTION_GROUNDS[ground][1]
        if state != COVERED or check in asked:
            continue
        asked.add(check)
        reason = _CHECKS[check](case, action)
        if reason is not None and reason not in said:  # the net repeats a licence refusal
            said.add(reason)
            refusals.append((ground, reason))
    return EnforcementDetermination(action, tuple(refusals))
