"""The one-way-door predicate — CODE, not judgement (MAKE_IT_STICK.md item 2,
2026-07-12, director-decided: "the one-way-door list is CODE, not judgement.
A checkable predicate... Fails closed to escalation on genuine uncertainty.
Not re-derived each time.").

This governs the BUILDER's (agent's) own actions — a harness-level concern,
distinct from `company/governance/decision_rights.py` (the SIMULATED
COMPANY's internal decision rights, behind the epistemic wall). Do not
conflate the two: this module never touches simulation/company code, and
nothing in the simulated company's governance calls into it.

PROCEED_BY_DEFAULT.md's seven categories, verbatim:
1. Spending real money.
2. Real-world commitments: legal, regulatory, contractual; anything binding
   outside the repo.
3. Public claims that cannot be retracted (a PROVISIONAL-labelled figure IS
   retractable — does not count).
4. Irrecoverable data loss (canonical state with no backup).
5. Security posture / secrets exposure / safety-control changes.
6. Values decisions defining what the company is FOR (e.g. the Epoch-4
   fitness function).
7. Anything touching a real customer or a real market (none exist yet).

Everything else: PROCEED — this module is a gate for the rare case, not a
permission check for routine work. Absence of a match means "not a one-way
door", not "safe" in some broader sense; ordinary engineering judgement
(tests, review, reversibility) still applies to everything.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class OneWayDoorCategory(Enum):
    REAL_MONEY = "real_money"
    REAL_WORLD_COMMITMENT = "real_world_commitment"
    IRRETRACTABLE_PUBLIC_CLAIM = "irretractable_public_claim"
    IRRECOVERABLE_DATA_LOSS = "irrecoverable_data_loss"
    SECURITY_SAFETY_CONTROL = "security_safety_control"
    VALUES_DECISION = "values_decision"
    # 2026-07-12, ADVISOR_STEER_TWIN_READONLY.md, director-decided verbatim:
    # "Any changes to repo, keys, settings etc I should do." Distinct from
    # SECURITY_SAFETY_CONTROL (which is about THIS harness's own safety
    # mechanisms -- the verifier, staging flow, skip-permissions) -- this
    # category is about platform/infrastructure CAPABILITY: repo settings/
    # visibility/branch protection/GitHub controls, keys/tokens/secrets/
    # credentials, account settings/connectors/billing/model entitlements,
    # and anything else that changes what the machine is ALLOWED to do (as
    # opposed to what it does). The director's hands only, never the twin's,
    # never the agent's autonomous choice, regardless of reversibility.
    PLATFORM_ADMINISTRATION = "platform_administration"
    REAL_CUSTOMER_OR_MARKET = "real_customer_or_market"


@dataclass(frozen=True)
class OneWayDoorVerdict:
    is_one_way_door: bool
    category: OneWayDoorCategory | None
    reason: str


# Keyword signals per category — deliberately broad/over-inclusive (a false
# positive costs one unnecessary escalation; a false negative defeats the
# whole predicate). Not exhaustive by design — genuine uncertainty is
# handled by the `uncertain` parameter below, not by trying to enumerate
# every possible phrasing.
_CATEGORY_PATTERNS: dict[OneWayDoorCategory, list[str]] = {
    OneWayDoorCategory.REAL_MONEY: [
        r"\breal money\b", r"\bpurchase\b", r"\bpayment to\b", r"\bcharge (the |a )?card\b",
        r"\bwire transfer\b", r"\bbuy\b.*\bwith (real|actual) (money|funds)\b",
    ],
    OneWayDoorCategory.REAL_WORLD_COMMITMENT: [
        r"\bsign(ed|ing)? (a |the )?contract\b", r"\blegal(ly)? bind", r"\bregulatory filing\b",
        r"\bsubmit(ted)? to ofgem\b", r"\bbinding agreement\b", r"\bterms of service\b.*\bagree\b",
    ],
    OneWayDoorCategory.IRRETRACTABLE_PUBLIC_CLAIM: [
        r"\bpress release\b", r"\bannounce(ment)? (externally|publicly)\b",
        r"\bpublish\b(?!.*\bprovisional\b)",
    ],
    OneWayDoorCategory.IRRECOVERABLE_DATA_LOSS: [
        r"rm -rf", r"drop table", r"force[- ]push", r"push --force", r"git reset --hard",
        r"delete (the )?backup", r"--no-verify", r"\bwipe\b.*\b(database|repo|history)\b",
    ],
    OneWayDoorCategory.SECURITY_SAFETY_CONTROL: [
        r"security profile", r"skip[- ]permissions",
        r"(modify|change|disable|bypass|weaken|remove|alter).*(epistemic verifier|staging flow)",
        r"disable.*(hook|verifier|gate)", r"\bsudo\b",
    ],
    OneWayDoorCategory.VALUES_DECISION: [
        r"fitness function", r"mortality rule", r"what the company is for",
        r"\bchoose\b.*\bobjective\b", r"optimi[sz]e (purely |solely )?for enterprise value",
    ],
    OneWayDoorCategory.REAL_CUSTOMER_OR_MARKET: [
        r"\breal customer\b", r"\bproduction (api )?key\b", r"\blive (nbp|trading|market) (feed|order)\b",
        r"\breal bank account\b",
    ],
    OneWayDoorCategory.PLATFORM_ADMINISTRATION: [
        r"repo(sitory)? (settings|visibility)", r"branch protection", r"github (settings|controls|repo)",
        r"\b(api )?keys?\b.*(creat|rotat|generat|revoke)", r"(creat|rotat|generat|revoke)\w*.*\b(api )?keys?\b",
        r"\btokens?\b.*(creat|rotat|generat|revoke)", r"(creat|rotat|generat|revoke)\w*.*\btokens?\b",
        r"\bcredential", r"\bsecrets?\b.*(creat|rotat|generat|expose)", r"(creat|rotat|generat|expose)\w*.*\bsecrets?\b",
        r"account settings", r"\bconnector", r"\bbilling\b", r"\b(plan|model) entitlement",
        r"change what.*(allowed|permitted) to do", r"grant.*(broader|new|additional) (access|permission)",
    ],
}

_PROVISIONAL_CARVEOUT = re.compile(r"\bprovisional\b", re.IGNORECASE)


def classify_action(
    description: str,
    *,
    explicit_category: OneWayDoorCategory | None = None,
    uncertain: bool = False,
) -> OneWayDoorVerdict:
    """Classify a proposed builder action. `description` is a short,
    plain-English statement of what's about to happen (the same text that
    would go in a decision-log entry).

    `explicit_category`: pass when the caller already knows the category
    (e.g. code that knows it's about to touch `background/egress_allowlist.py`)
    — trusted directly, skipping keyword matching.

    `uncertain=True`: the caller genuinely doesn't know whether this is a
    one-way door. Fails CLOSED — always escalates, regardless of keyword
    match, per DIRECTOR_TWIN.md's "uncertain whether something is a one-way
    door? Escalate. Asymmetric cost." This is the escape hatch for the cases
    the keyword patterns were never going to anticipate.
    """
    if explicit_category is not None:
        return OneWayDoorVerdict(
            is_one_way_door=True,
            category=explicit_category,
            reason=f"explicitly categorised as {explicit_category.value}",
        )

    if uncertain:
        return OneWayDoorVerdict(
            is_one_way_door=True,
            category=None,
            reason="caller flagged genuine uncertainty -- fails closed to escalation",
        )

    lowered = description.lower()
    for category, patterns in _CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                if category == OneWayDoorCategory.IRRETRACTABLE_PUBLIC_CLAIM and _PROVISIONAL_CARVEOUT.search(lowered):
                    continue
                return OneWayDoorVerdict(
                    is_one_way_door=True,
                    category=category,
                    reason=f"matched pattern {pattern!r} for {category.value}",
                )

    return OneWayDoorVerdict(
        is_one_way_door=False,
        category=None,
        reason="no one-way-door category matched -- proceed, log the decision, director reverses at boundaries",
    )
