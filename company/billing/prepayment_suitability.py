"""The company's safe-and-reasonably-practicable (S&RP) finding for a prepayment meter (C32, item 1).

SLC 27.6(a)(iii) puts a prepayment meter on the menu only "where safe and reasonably practicable",
and the S&RP guidance binds every PPM through 28.4, so a Consent offer needs the supplier's own
finding: the household's yes is not one. Rules and design choices: commons
`docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md` s.5,
"The S&RP assessment". The guidance text is `docs/market_research/company_debt_management.md`.

The finding is a dated `ProtectionRecord`, read by the enforcement gate like 27A's and 28B's. It is
negative on a do-not-install ground (guidance 3.7). It is "for a person to decide" on any other
evidence held (3.8, 3.9): the company has no welfare officer, so it never finds those positive.
It is positive only where the household was ASKED and answered every question "no". Holding no
evidence is not having asked, so with no conversation on record there is no finding at all.

Live, the household's answers come back through `SimInterface.ask_prepayment_suitability` (W2_43),
asked at the Consent rung (`PaymentObservationConsumer._prepayment_suitability`).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, fields
from typing import Iterable, Optional

from company.billing.winter_moratorium import SAFE_AND_PRACTICABLE, UNANSWERED_EVIDENCE
from company.regulatory.priority_services_register import ProtectionRecord, PSRCategory

#: SLC 28.3: contact every PPM customer at least once a year to assess whether a PPM remains safe and
#: reasonably practicable. That is the longest the licence lets a finding stand, and the only
#: published period, so a finding lapses a year after the household was asked.
FINDING_LAPSE_DAYS = 365

#: Guidance 3.7, read from the PSR categories (categorical, erring toward protection: a PSR "chronic
#: illness" is not always "chronic/severe or terminal").
DO_NOT_INSTALL_CATEGORIES = frozenset({PSRCategory.MEDICAL_EQUIPMENT, PSRCategory.CHRONIC_ILLNESS})

#: Guidance 3.9 encourages a check where an adult is over 65.
FURTHER_ASSESSMENT_AGE = 65


@dataclass(frozen=True)
class SuitabilityAnswers:
    """The household's answers on one dated S&RP conversation. True: the ground applies. None: not
    answered, which counts as the bar (as in 28B's do-not-install check)."""
    asked_on: dt.date
    # 3.7, do not install
    cannot_access_operate_or_top_up: Optional[bool] = None
    continuous_supply_health_need: Optional[bool] = None
    over_75_without_support: Optional[bool] = None
    child_under_2: Optional[bool] = None
    severe_or_terminal_condition: Optional[bool] = None
    # 3.8 and 3.9, further assessment
    child_5_or_under: Optional[bool] = None
    serious_medical_or_mental_condition: Optional[bool] = None
    pregnancy_or_bereavement: Optional[bool] = None
    adult_over_65_or_child_under_16: Optional[bool] = None


_DO_NOT_INSTALL_ANSWERS = ("cannot_access_operate_or_top_up", "continuous_supply_health_need",
                           "over_75_without_support", "child_under_2", "severe_or_terminal_condition")


def _age_on(born: dt.date, on: dt.date) -> int:
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


def assess_prepayment_suitability(on: dt.date, *, categories: Iterable = (), needs_codes: Iterable = (),
                                  date_of_birth: Optional[dt.date] = None,
                                  answers: Optional[SuitabilityAnswers] = None,
                                  ) -> Optional[ProtectionRecord]:
    """The S&RP finding on `on`, from what the company holds that day. None: no finding (never asked).

    `evidence` on the record names every ground that decided it, so a withheld offer says why."""
    held = sorted(PSRCategory(c).value for c in categories)
    bar = [f"do-not-install (3.7): {c}" for c in held if PSRCategory(c) in DO_NOT_INSTALL_CATEGORIES]
    person = [f"further assessment (3.8), for a person to decide: {c}" for c in held
              if PSRCategory(c) not in DO_NOT_INSTALL_CATEGORIES]
    person += [f"further assessment, for a person to decide: needs code {n}" for n in sorted(needs_codes)]
    if date_of_birth is not None and _age_on(date_of_birth, on) > FURTHER_ASSESSMENT_AGE:
        person.append(f"further assessment (3.9), for a person to decide: born {date_of_birth}")
    if answers is not None and answers.asked_on <= on:
        for f in fields(answers):
            if f.name == "asked_on":
                continue
            value = getattr(answers, f.name)
            if value is None:
                bar.append(f"{UNANSWERED_EVIDENCE}{f.name}")
            elif value:
                (bar if f.name in _DO_NOT_INSTALL_ANSWERS else person).append(
                    f"{'do-not-install (3.7)' if f.name in _DO_NOT_INSTALL_ANSWERS else 'further assessment (3.8/3.9), for a person to decide'}: {f.name}")
        learned = answers.asked_on
    elif bar or person:
        learned = on  # a negative finding needs no conversation: the evidence held is the bar
    else:
        return None
    return ProtectionRecord(SAFE_AND_PRACTICABLE, learned, learned + dt.timedelta(days=FINDING_LAPSE_DAYS),
                            met=not (bar or person), evidence=tuple(bar + person))
