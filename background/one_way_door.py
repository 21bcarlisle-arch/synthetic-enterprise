"""The one-way-door predicate — CODE, not judgement (MAKE_IT_STICK.md item 2,
2026-07-12, director-decided: "the one-way-door list is CODE, not judgement.
A checkable predicate... Not re-derived each time.").

CALIBRATION (ONE_WAY_DOOR_DEFAULTS_TO_ACT.md, 2026-07-16, director-decided):
the burden of proof is on "it's a door". Reversibility is the DEFAULT VERDICT —
an action proceeds autonomously unless it PROVABLY matches a criterion below;
"I'm not sure" resolves to PROCEED-and-log, not to a fail-closed escalation. The
door LIST is unchanged and the hard walls still stop every time; only the
ambiguity default flipped (a needless escalation halts the loop + spends
director attention, so it is a defect, exactly as a needless stop is).

This governs the BUILDER's (agent's) own actions — a harness-level concern,
distinct from `company/governance/decision_rights.py` (the SIMULATED
COMPANY's internal decision rights, behind the epistemic wall). Do not
conflate the two: this module never touches simulation/company code, and
nothing in the simulated company's governance calls into it.

RE-SCOPE TO REALITY (2026-07-29, DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY
item 5, confirmed directly by the director on the NTFY channel the same evening,
`docs/staging/done/from_rich_20260729_192946.md`, verbatim: *"'safety control'
means protecting a real person, real money, or a public claim in the company's
name. A control that stops a simulation is not one — re-tag those and release
them. This message is the authorisation; ntfy is me."*):

**A category only RESERVES an action if its consequence lands OUTSIDE the
simulation.** The reserved set is now exactly four real-world consequences —
real money, real people (contacting them / their safety), a public claim in
Poesys's name, and a live credential that grants a stranger real capability
under the director's real identity. Every other category still CLASSIFIES (it
informs, and the classification is logged), but it no longer GATES: a verdict on
a released category returns `is_one_way_door=False` with `advisory_category`
set. The ruling's own test for a retention is "name the real-world consequence
it prevents — and if the consequence is internal to a simulation, that is not a
reason", so each entry below carries its consequence or its release reason.

RESERVED — gates, every time:
1. REAL_MONEY — money leaves a real account (now also billing plans and model
   entitlements: changing the plan spends real money).
2. REAL_WORLD_COMMITMENT — binds a real person or organisation outside the repo
   (a signed contract, a regulatory filing).
3. IRRETRACTABLE_PUBLIC_CLAIM — a claim in the company's name that cannot be
   withdrawn (a PROVISIONAL-labelled figure IS retractable — does not count).
4. REAL_CUSTOMER_OR_MARKET — touches a real person or a live market.
5. LIVE_CREDENTIAL_EXPOSURE — a real key/token/secret. Retained with its
   real-world consequence named: a leaked live credential lets someone who is
   not the director act, and spend, as him. That consequence is not internal to
   any simulation. (Split out of the old PLATFORM_ADMINISTRATION, whose
   remaining members are settings, not credentials.)

RELEASED — classifies and informs, never gates:
- IRRECOVERABLE_DATA_LOSS — the loss is repo/simulation state, recoverable from
  origin and history. No real person, no real money.
- SECURITY_SAFETY_CONTROL — these are the HARNESS's own controls (the verifier,
  the hooks, the staging flow, skip-permissions). Disarming one stops a
  simulation; it protects nobody real. This is the exact category the director
  re-tagged by name.
- VALUES_DECISION — the curriculum and the fitness function. R13 and LAW A still
  govern as canon (a curriculum change is a named, versioned, director-authored
  artefact, never silent parameter drift), but canon is now enforced by that
  artefact discipline, NOT by a permission gate on this predicate.
- PLATFORM_ADMINISTRATION — repo settings, visibility, branch protection,
  connectors. The director may still prefer to make these himself; a preference
  is a DIAL, and a dial informs, it does not block.

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
    # 2026-07-29 (DIRECTOR_RULING item 5 re-scope): split OUT of
    # PLATFORM_ADMINISTRATION, which is otherwise released. Retained as a wall
    # with its real-world consequence named, exactly as the ruling requires:
    # a live key/token/secret lets someone who is NOT the director act, and
    # spend, as him. That consequence lands outside every simulation, so it is
    # the "real money / real people" wall wearing a technical hat -- not a
    # control that merely stops a sim. Settings are a dial; credentials are not.
    LIVE_CREDENTIAL_EXPOSURE = "live_credential_exposure"


@dataclass(frozen=True)
class OneWayDoorVerdict:
    is_one_way_door: bool
    category: OneWayDoorCategory | None
    reason: str
    # ONE_WAY_DOOR_DEFAULTS_TO_ACT.md rule 2: when the verdict is "proceed" reached
    # THROUGH ambiguity (the caller was unsure but nothing provably matched a wall), the
    # call must be RECORDED so it is auditable. This flag lets decision_log/action_needed
    # mark it as an ambiguous-reversible proceed rather than a plainly-clear one.
    ambiguous_reversible_proceed: bool = False
    # 2026-07-29 DIRECTOR_RULING item 5: released categories are now informational only.
    # A verdict on a released category returns `is_one_way_door=False` with `advisory_category`
    # set, so callers can log the classification even though it does not gate. This preserves
    # the audit trail and lets a dialed preference (e.g. "director prefers to do this") stay
    # visible to readers, while accepting that "released" means "no gate."
    advisory_category: OneWayDoorCategory | None = None


# Keyword signals per category — deliberately broad/over-inclusive (a false
# positive costs one unnecessary escalation; a false negative defeats the
# whole predicate). Not exhaustive by design — an action the keywords miss is
# handled by `provably_irreversible` (caller-asserted, inverted burden), not by
# trying to enumerate every possible phrasing.
_CATEGORY_PATTERNS: dict[OneWayDoorCategory, list[str]] = {
    OneWayDoorCategory.REAL_MONEY: [
        r"\breal money\b", r"\bpurchase\b", r"\bpayment to\b", r"\bcharge (the |a )?card\b",
        r"\bwire transfer\b", r"\bbuy\b.*\bwith (real|actual) (money|funds)\b",
        # 2026-07-29: "Approve £4,000/month of real spend on the data feed" matched
        # NOTHING above -- the commonest way a real purchase is actually phrased here
        # (approve/spend/subscription) was absent, so the wall read PROCEED on real
        # spending. Widening detection is safety-INCREASING, so it needs no director
        # authorisation (the console convention governs safety-REDUCING changes).
        # NOTE the deliberate omission: a bare currency-amount regex is NOT added.
        # This project prints simulated £ figures on every surface (treasury, margin,
        # VM outstanding), so `[£$]\d+` would fire constantly on the simulation's own
        # output -- a control false-positive that jams the pipeline is its own defect.
        # Every pattern below therefore pairs money with a REAL-WORLD spend context.
        r"\breal spend(ing)?\b", r"\bspend(ing)? (real|actual)\b",
        r"\bapprove\b[^.]{0,40}\bspend(ing)?\b",
        r"\b(paid|billable) subscription\b", r"\bcredit card\b",
        r"\bout of pocket\b", r"\btop ?up (the )?(account|balance|credit)\b",
        # 2026-07-29 re-scope: moved here from PLATFORM_ADMINISTRATION (now released).
        # Changing a billing plan or a model entitlement SPENDS REAL MONEY -- it is a
        # money wall, not a settings preference, and must not be released with settings.
        r"\bbilling\b", r"\b(plan|model) entitlement",
        # 2026-08-03: found by the action_needed reserved-class guard's own R15 test. "Authorise a
        # real card payment for the paid Elexon feed subscription" and "pay for the subscription
        # with the company card" both matched NOTHING above -- `payment to` requires a recipient,
        # `charge the card` requires that exact verb, and `paid subscription` missed "paid ... feed
        # subscription". This classifier is now the ONLY thing between the loop and real spending
        # (every other gate was deleted with the permission machinery), so a gap here is a gap in a
        # WALL, not in a dial. Widening detection stays safety-INCREASING and needs no authorisation.
        # DELIBERATE OMISSIONS, same reasoning as the currency-amount note above: `invoice` and
        # `direct debit` are core SIMULATED domain vocabulary here (the company issues invoices and
        # runs DD collections every settlement period), so either would fire on the simulation's own
        # routine work -- a control that jams the pipeline is its own defect. Every pattern below
        # pairs money with a REAL-WORLD purchasing context that the simulation never uses.
        r"\bcard payment\b", r"\bpay(ing)? for\b[^.]{0,40}\bsubscription\b",
        r"\b(company|corporate|real) card\b",
        r"\bsubscri(be|ption)\b[^.]{0,30}\b(paid|cost|fee)\b", r"\breal (card|bank) \w+\b",
    ],
    OneWayDoorCategory.REAL_WORLD_COMMITMENT: [
        r"\bsign(ed|ing)? (a |the )?contract\b", r"\blegal(ly)? bind", r"\bregulatory filing\b",
        r"\bsubmit(ted)? to ofgem\b", r"\bbinding agreement\b", r"\bterms of service\b.*\bagree\b",
    ],
    OneWayDoorCategory.IRRETRACTABLE_PUBLIC_CLAIM: [
        r"\bpress release\b", r"\bannounce(ment)? (externally|publicly)\b",
        # "publish" is deliberately broad, but it has a MACHINERY sense (the publish
        # PIPELINE / gate / cache / loop) that is reversible engineering, not a public
        # claim. That word-sense collision false-fired -- see the _PUBLISH_MACHINERY_
        # carveout below and decision_log 2026-07-18 (a BUILD-open sequencing question
        # mentioning the "publish pipeline" was mis-routed to the director). Same shape
        # as the epoch-adjective tighten (test_open_build_in_the_open_epoch_is_not_a_door).
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
        # Epoch curriculum = the director's instrument (R13/LAW A, DIRECTOR_ANSWER_
        # FINISH_NOT_OPEN.md: opening a NEW epoch is a deliberate category-6 call).
        # Deliberately narrow to ACTUALLY-OPENING-AN-EPOCH: "open epoch 4" (a number)
        # or "open a new / the next epoch". It must NOT match the ADJECTIVE "the open
        # epoch" (= the current epoch) — "BUILD-open within THE OPEN EPOCH" is
        # REVERSIBLE, the twin's call, NOT a door (2026-07-16: that false match was
        # re-escalating open-build every draw) — nor "epoch-gated"/"epoch sequencing".
        r"open(ing)?\s+epoch\s*\d",
        r"open(ing)?\s+(a\s+new|the\s+next)\s+epoch\b",
        r"\bcurriculum\s+(decision|change|choice)\b",
    ],
    OneWayDoorCategory.REAL_CUSTOMER_OR_MARKET: [
        r"\breal customer\b", r"\bproduction (api )?key\b", r"\blive (nbp|trading|market) (feed|order)\b",
        r"\breal bank account\b",
    ],
    OneWayDoorCategory.PLATFORM_ADMINISTRATION: [
        r"repo(sitory)? (settings|visibility)", r"branch protection", r"github (settings|controls|repo)",
        r"account settings", r"\bconnector",
        r"change what.*(allowed|permitted) to do", r"grant.*(broader|new|additional) (access|permission)",
    ],
    # RESERVED. Credentials moved here verbatim out of PLATFORM_ADMINISTRATION so the
    # released-settings half cannot take the credential half down with it.
    OneWayDoorCategory.LIVE_CREDENTIAL_EXPOSURE: [
        r"\b(api )?keys?\b.*(creat|rotat|generat|revoke)", r"(creat|rotat|generat|revoke)\w*.*\b(api )?keys?\b",
        r"\btokens?\b.*(creat|rotat|generat|revoke)", r"(creat|rotat|generat|revoke)\w*.*\btokens?\b",
        r"\bcredential", r"\bsecrets?\b.*(creat|rotat|generat|expose)", r"(creat|rotat|generat|expose)\w*.*\bsecrets?\b",
    ],
}

# 2026-07-29 DIRECTOR_RULING item 5: released categories (advisory only, no gate).
# These classify and inform, but is_one_way_door is False; the verdict's
# `advisory_category` is set instead, so callers can log the classification.
# Each is released because its real-world consequence (if any) is internal
# to the simulation: stopping a simulation protects no one real.
_RELEASED_CATEGORIES = frozenset({
    OneWayDoorCategory.IRRECOVERABLE_DATA_LOSS,
    OneWayDoorCategory.SECURITY_SAFETY_CONTROL,
    OneWayDoorCategory.VALUES_DECISION,
    OneWayDoorCategory.PLATFORM_ADMINISTRATION,
})

# The four real-world consequences, derived as the COMPLEMENT of the released set so the
# two can never silently disagree (a new enum member defaults to RESERVED -- fail-closed
# on the walls, which is the safe direction for the half that protects real people).
RESERVED_CATEGORIES = frozenset(
    c for c in OneWayDoorCategory if c not in _RELEASED_CATEGORIES
)

_PROVISIONAL_CARVEOUT = re.compile(r"\bprovisional\b", re.IGNORECASE)

# The MACHINERY sense of "publish": the publish PIPELINE / gate / cache / loop /
# workflow -- reversible engineering, not an irretractable public claim. Registered
# false-fire (decision_log 2026-07-18): the bare `\bpublish\b` pattern matched a
# BUILD-open SEQUENCING question that merely mentioned the "publish pipeline" and
# mis-routed it to the director (the INVERSE of R15 fail-open -- a control that
# FALSE-FIRES, spending the one scarce resource on noise). Tightens the pattern to
# the CLAIM sense: a "publish" match is carved out ONLY when a machinery term is
# present AND no genuine public-claim OBJECT is (so "publish the report figure via
# the publish pipeline" still fires -- the carveout errs toward the door).
_PUBLISH_MACHINERY_CARVEOUT = re.compile(
    r"\b(pipeline|gate|cache|loop|workflow|hook|daemon|scheduler|cron|"
    r"health\s*check|site\s*build|rebuild|re-?sync|deploy(ment)?|refresh)\b",
    re.IGNORECASE,
)
# A genuine irretractable-public-claim OBJECT: a figure/number/report/result/claim/
# statement (or an outward-facing surface/audience). Its presence DEFEATS the
# machinery carveout so a real claim that happens to mention the pipeline still
# escalates. Kept over-inclusive on purpose -- a false door here costs one
# escalation, a false PROCEED publishes an unretractable claim.
_PUBLIC_CLAIM_OBJECT = re.compile(
    r"\b(figure|number|report|result|claim|statement|margin|profit|revenue|"
    r"earnings|forecast|headline|annual report|press|externally|publicly|"
    r"public site|to the public|announce)\b",
    re.IGNORECASE,
)


def classify_action(
    description: str,
    *,
    explicit_category: OneWayDoorCategory | None = None,
    uncertain: bool = False,
    provably_irreversible: bool = False,
) -> OneWayDoorVerdict:
    """Classify a proposed builder action. `description` is a short,
    plain-English statement of what's about to happen (the same text that
    would go in a decision-log entry).

    THE BURDEN OF PROOF IS ON "IT'S A DOOR" (ONE_WAY_DOOR_DEFAULTS_TO_ACT.md,
    2026-07-16, director-decided). Reversibility is the DEFAULT VERDICT: an
    action PROCEEDS autonomously UNLESS it PROVABLY matches a one-way-door
    criterion. "I'm not sure" resolves to PROCEED-and-log, never to ASK — a
    needless escalation is a defect exactly as a needless stop is (it halts the
    loop and consumes director attention, the only scarce resource). This
    recalibrates — does NOT weaken — the door LIST: the walls below still stop,
    every time; only the DEFAULT on ambiguity flips from ask to proceed.

    Escalation fires on exactly three PROVABLE signals:
    - `explicit_category`: the caller already knows the category (e.g. code
      about to touch `background/egress_allowlist.py`) — trusted directly.
    - a keyword pattern match against the (unchanged) door LIST below.
    - `provably_irreversible=True`: the caller has established the action has NO
      reversible form (no archive-not-delete / branch-not-main / draft-not-
      publish / flag-off-default) AND it is not merely unclear — a genuine
      irreversible action the keyword patterns did not anticipate. This is the
      inverted-burden escape hatch: the caller must PROVE irreversibility, not
      merely feel unsure.

    `uncertain=True` (unsure whether this is a door, but a reversible form is
    available / reversibility is not disproven) NO LONGER escalates by itself —
    it resolves to PROCEED, flagged `ambiguous_reversible_proceed` so the call
    is recorded (rule 2: proceed AND log). It escalates only if one of the three
    provable signals above ALSO fires. This overturns the prior fail-closed-on-
    uncertainty behaviour, per the director's calibration.
    """
    if explicit_category is not None:
        # A caller naming a RELEASED category no longer gates either -- otherwise
        # explicit_category would be a back door around the 2026-07-29 re-scope, and
        # the permission machinery would survive in its most-used call path.
        if explicit_category in _RELEASED_CATEGORIES:
            return OneWayDoorVerdict(
                is_one_way_door=False,
                category=None,
                reason=(
                    f"explicitly categorised as {explicit_category.value}, which is RELEASED "
                    "(2026-07-29 ruling item 5: its consequence is internal to the simulation) "
                    "-- classified and logged, not gated"
                ),
                advisory_category=explicit_category,
            )
        return OneWayDoorVerdict(
            is_one_way_door=True,
            category=explicit_category,
            reason=f"explicitly categorised as {explicit_category.value}",
        )

    lowered = description.lower()
    # A released match must NEVER short-circuit the scan: "disable the verifier so we can
    # spend real money on the feed" matches SECURITY_SAFETY_CONTROL (released) before
    # REAL_MONEY (reserved) in dict order, and returning on the first match would read
    # PROCEED on a real-money action. So: remember the first released match, keep scanning,
    # and only fall back to it once every reserved category has been ruled out.
    first_released: tuple[OneWayDoorCategory, str] | None = None
    for category, patterns in _CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                if category == OneWayDoorCategory.IRRETRACTABLE_PUBLIC_CLAIM:
                    if _PROVISIONAL_CARVEOUT.search(lowered):
                        continue
                    # Machinery sense of "publish" (pipeline/gate/cache/loop) with no
                    # genuine public-claim object -> reversible engineering, not a door.
                    if (
                        _PUBLISH_MACHINERY_CARVEOUT.search(lowered)
                        and not _PUBLIC_CLAIM_OBJECT.search(lowered)
                    ):
                        continue
                if category in _RELEASED_CATEGORIES:
                    if first_released is None:
                        first_released = (category, pattern)
                    break  # this category is decided; keep scanning the reserved ones
                return OneWayDoorVerdict(
                    is_one_way_door=True,
                    category=category,
                    reason=f"matched pattern {pattern!r} for {category.value}",
                )

    if first_released is not None:
        released_category, released_pattern = first_released
        return OneWayDoorVerdict(
            is_one_way_door=False,
            category=None,
            reason=(
                f"matched pattern {released_pattern!r} for {released_category.value}, a RELEASED "
                "category (2026-07-29 ruling item 5: a control that stops a SIMULATION is not a "
                "safety control) -- PROCEED, record the undo, say what you did"
            ),
            advisory_category=released_category,
        )

    # PROVABLE irreversibility (caller-asserted, keyword-missed): the only non-keyword
    # path to escalation now that the burden of proof has inverted.
    if provably_irreversible:
        return OneWayDoorVerdict(
            is_one_way_door=True,
            category=None,
            reason="caller established the action is PROVABLY irreversible (no reversible form) -- escalate",
        )

    # Ambiguity with a reversible form: proceed AND log (rule 2), do NOT ask. The
    # burden of proof sat on "it's a door" and nothing provably matched -> reversible.
    if uncertain:
        return OneWayDoorVerdict(
            is_one_way_door=False,
            category=None,
            reason=(
                "caller unsure but nothing provably matched a wall and a reversible form is "
                "available -- PROCEED-and-log per ONE_WAY_DOOR_DEFAULTS_TO_ACT.md rule 2 "
                "(reversibility is the default verdict; a needless escalation is a defect)"
            ),
            ambiguous_reversible_proceed=True,
        )

    return OneWayDoorVerdict(
        is_one_way_door=False,
        category=None,
        reason="no one-way-door category matched -- proceed, log the decision, director reverses at boundaries",
    )
