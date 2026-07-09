"""Obligations register -- Phase 1 of DOMAIN_SENSE_AND_COMPLIANCE.md.

A risk-tiered, single source of truth for every regulatory/legal obligation
this company is subject to. Company-side (inside the wall): this is fidelity,
not QA -- a real UK supplier's compliance function maintains exactly this kind
of register.

Why this exists rather than a fresh compliance system: company/regulatory/ +
company/compliance/ already track ~10 obligation areas individually
(ofgem_obligations.py, compliance.py, slc_compliance_tracker.py,
compliance_scorecard.py's RAG dashboard, social_obligation_register.py,
green_claims_audit.py, consumer_duty.py, and others) -- but none of them
classifies risk the way the director's principles require: impact x
likelihood, with impact ranked physical-harm-to-people worst, then financial
harm to customers, then licence/regulatory, then company-financial, then
reputational; and risk tier driving control type, testing depth/frequency,
and reporting visibility. This module is that missing risk-tiering layer. It
does not reimplement any existing tracker's compliance logic -- each entry's
`existing_tracker` field points at the module that already monitors it, so
the register classifies risk without duplicating monitoring code.

Design note on risk_tier(): billing accuracy (SLC 6/7) is CUSTOMER_FINANCIAL
impact, which nominally ranks below PHYSICAL_HARM -- but the director's own
Principle 1 ("bills must be accurate, above all... 100% preventive
validation, zero tolerance") makes it Tier 1 regardless. The mapping below
reflects that: CUSTOMER_FINANCIAL impact reaches Tier 1 at MEDIUM/HIGH
likelihood (a system issuing thousands of bills has high hit-rate on any
latent bug class -- see R10's C6 SME-as-Household precedent), matching the
director's explicit call without needing a special case.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ImpactTier(str, Enum):
    """Ranked worst-to-least-severe per the director's binding principle 2."""
    PHYSICAL_HARM = "physical_harm"
    CUSTOMER_FINANCIAL = "customer_financial"
    LICENCE_REGULATORY = "licence_regulatory"
    COMPANY_FINANCIAL = "company_financial"
    REPUTATIONAL = "reputational"


class Likelihood(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskTier(str, Enum):
    TIER_1 = "tier_1"  # preventive gate, 100% continuous, immediate NTFY + held artefact
    TIER_2 = "tier_2"  # detective, statistical sample, daily/per-run
    TIER_3 = "tier_3"  # periodic, rolls up into the periodic compliance report


class ControlType(str, Enum):
    PREVENTIVE_GATE = "preventive_gate"
    DETECTIVE_SAMPLING = "detective_sampling"


class ValidationDepth(str, Enum):
    FULL_POPULATION = "full_population"
    STATISTICAL_SAMPLE = "statistical_sample"


class ValidationFrequency(str, Enum):
    CONTINUOUS = "continuous"
    PER_BILL_RUN = "per_bill_run"
    DAILY = "daily"
    PHASE_CLOSE = "phase_close"
    PERIODIC = "periodic"


class ReportingVisibility(str, Enum):
    IMMEDIATE_NTFY = "immediate_ntfy"       # Tier 1: director + held artefact
    PERIODIC_REPORT = "periodic_report"     # Tier 2/3: rolls into the compliance report


def derive_risk_tier(impact: ImpactTier, likelihood: Likelihood) -> RiskTier:
    """Impact x likelihood -> risk tier. See module docstring for why
    CUSTOMER_FINANCIAL reaches Tier 1 at MEDIUM/HIGH likelihood despite
    ranking below PHYSICAL_HARM in raw severity."""
    if impact == ImpactTier.PHYSICAL_HARM:
        return RiskTier.TIER_1
    if impact == ImpactTier.CUSTOMER_FINANCIAL:
        return RiskTier.TIER_1 if likelihood in (Likelihood.MEDIUM, Likelihood.HIGH) else RiskTier.TIER_2
    if impact == ImpactTier.LICENCE_REGULATORY:
        return RiskTier.TIER_2 if likelihood in (Likelihood.MEDIUM, Likelihood.HIGH) else RiskTier.TIER_3
    if impact == ImpactTier.COMPANY_FINANCIAL:
        return RiskTier.TIER_2 if likelihood == Likelihood.HIGH else RiskTier.TIER_3
    return RiskTier.TIER_3  # REPUTATIONAL


_DEFAULT_CONTROL_BY_TIER = {
    RiskTier.TIER_1: ControlType.PREVENTIVE_GATE,
    RiskTier.TIER_2: ControlType.DETECTIVE_SAMPLING,
    RiskTier.TIER_3: ControlType.DETECTIVE_SAMPLING,
}
_DEFAULT_DEPTH_BY_TIER = {
    RiskTier.TIER_1: ValidationDepth.FULL_POPULATION,
    RiskTier.TIER_2: ValidationDepth.STATISTICAL_SAMPLE,
    RiskTier.TIER_3: ValidationDepth.STATISTICAL_SAMPLE,
}
_DEFAULT_VISIBILITY_BY_TIER = {
    RiskTier.TIER_1: ReportingVisibility.IMMEDIATE_NTFY,
    RiskTier.TIER_2: ReportingVisibility.PERIODIC_REPORT,
    RiskTier.TIER_3: ReportingVisibility.PERIODIC_REPORT,
}


@dataclass(frozen=True)
class Obligation:
    """One row of the register.

    `existing_tracker` names the company/ module that already monitors this
    obligation (None if genuinely uncovered -- a real gap to flag, not to
    silently backfill here). `testing_frequency` and the tier-derived
    defaults (control_type/testing_depth/reporting_visibility) can be
    overridden per-obligation when judgment differs from the mechanical
    default -- always paired with `rationale` explaining why.
    """
    id: str
    name: str
    source: str  # law/SLC reference, e.g. "Ofgem SLC 6/7", "Consumer Contracts Regulations 2013"
    impact: ImpactTier
    likelihood: Likelihood
    rationale: str
    existing_tracker: Optional[str] = None
    testing_frequency: ValidationFrequency = ValidationFrequency.PERIODIC
    control_type_override: Optional[ControlType] = None
    testing_depth_override: Optional[ValidationDepth] = None
    reporting_visibility_override: Optional[ReportingVisibility] = None

    @property
    def risk_tier(self) -> RiskTier:
        return derive_risk_tier(self.impact, self.likelihood)

    @property
    def control_type(self) -> ControlType:
        return self.control_type_override or _DEFAULT_CONTROL_BY_TIER[self.risk_tier]

    @property
    def testing_depth(self) -> ValidationDepth:
        return self.testing_depth_override or _DEFAULT_DEPTH_BY_TIER[self.risk_tier]

    @property
    def reporting_visibility(self) -> ReportingVisibility:
        return self.reporting_visibility_override or _DEFAULT_VISIBILITY_BY_TIER[self.risk_tier]


# Seed register (Phase 1): spans every category the director's principle 2
# names. Not exhaustive -- extending this list (and wiring newly-identified
# `existing_tracker=None` gaps to a real monitor) is ongoing register
# maintenance, not a one-off population exercise.
REGISTER: list[Obligation] = [
    Obligation(
        id="slc_6_7_billing_accuracy",
        name="Billing must be accurate",
        source="Ofgem SLC 6/7",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.HIGH,
        rationale=(
            "Director's Principle 1, binding: 100% of bills validated before issue, zero "
            "tolerance, continuous. High likelihood because every bill run hits the same "
            "code paths at volume -- a latent bug class (R10's C6 SME-as-Household "
            "precedent) recurs every run until the class itself is closed, not sampled."
        ),
        existing_tracker=None,  # the gap this programme's Phase 3 (pre-bill gate) fills
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="slc_31a_back_billing_cap",
        name="Back-billing cap -- cannot bill >12 months of unbilled consumption",
        source="Ofgem SLC 31A / Citizens Advice back-billing guidance",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.MEDIUM,
        rationale=(
            "Real financial harm if breached (surprise multi-year bill), but the forced "
            "catch-up mechanism in simulation/meter_reads.py already structurally prevents "
            "the cap being exceeded -- medium not high likelihood."
        ),
        existing_tracker="simulation/meter_reads.py (MAX_CONSECUTIVE_ESTIMATED_PERIODS)",
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="slc_14_credit_refunds",
        name="Credit refunds within 10 working days of account closure",
        source="Ofgem SLC 14",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.MEDIUM,
        rationale="Real customer financial harm (delayed money) if the SLA is missed.",
        existing_tracker="company/billing/credit_refund.py + simulation/credit_refund_events.py",
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="gsop_auto_compensation",
        name="Guaranteed Standards of Performance -- automatic compensation payments",
        source="Ofgem GSOP Regulations",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.MEDIUM,
        rationale="Missed auto-compensation is direct customer financial harm plus a licence breach.",
        existing_tracker="company/billing (GSOP compensation physics, Phase 3 unhappy-paths)",
        testing_frequency=ValidationFrequency.DAILY,
    ),
    Obligation(
        id="psr_vulnerability_duties",
        name="Priority Services Register -- vulnerable customer welfare duties",
        source="Ofgem SLC 0 / Consumer Duty / PSR Code of Practice",
        impact=ImpactTier.PHYSICAL_HARM,
        likelihood=Likelihood.LOW,
        rationale=(
            "The one obligation in this register where a failure (missing a PSR flag before "
            "a supply interruption for a life-support/medically-dependent customer) can "
            "plausibly cause physical harm, not just financial loss -- Tier 1 regardless of "
            "likelihood, per the director's impact ranking. Likelihood is genuinely low in "
            "this sim (no real supply interruptions modelled yet) but the tier does not "
            "relax because of that -- impact alone forces Tier 1 here."
        ),
        existing_tracker="company/crm (vulnerability_register)",
        testing_frequency=ValidationFrequency.CONTINUOUS,
    ),
    Obligation(
        id="vat_by_segment",
        name="VAT must be charged at the correct rate by customer segment",
        source="VAT Act 1994 (domestic 5%, business 20%, de minimis rules)",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.HIGH,
        rationale=(
            "Same class as R10's C6 defect (SME billed as Household at 20% VAT instead of "
            "5%) -- confirmed high-likelihood given it already happened. Tier 1, needs the "
            "invariants library (Phase 2) to give the gate (Phase 3) a real segment->rate map."
        ),
        existing_tracker=None,
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="settlement_industry_code",
        name="Settlement / industry-code duties (BSC, MRA metering data obligations)",
        source="BSC / MRA",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Licence/regulatory impact, low likelihood given settlement already anchored to real Elexon data.",
        existing_tracker="company/billing/metering_exception.py, meter_read_validation.py",
        testing_frequency=ValidationFrequency.PHASE_CLOSE,
    ),
    Obligation(
        id="marketing_switching_rules",
        name="Marketing and switching conduct rules (cooling-off, misleading claims)",
        source="Consumer Contracts Regulations 2013 / Ofgem SLC (marketing standards)",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Licence/regulatory impact; the 14-day cooling-off constant is already hard-anchored.",
        existing_tracker="simulation/acquisition_funnel.py",
        testing_frequency=ValidationFrequency.PHASE_CLOSE,
    ),
    Obligation(
        id="smart_meter_rollout_targets",
        name="Smart meter rollout progress reporting",
        source="Ofgem SLC 22 / SLC 45",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Reporting obligation, not a customer-facing control; existing tracker already RAGs this.",
        existing_tracker="company/regulatory/compliance.py, ofgem_obligations.py",
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="whd_eco_social_obligation_spend",
        name="Warm Home Discount / ECO social obligation spend",
        source="WHD Scheme Regulations 2011 / ECO4 2022-2026",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Mandatory spend tracked continuously by an existing dedicated register.",
        existing_tracker="company/regulatory/social_obligation_register.py",
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="green_claims_rego",
        name="Green tariff REGO backing must match claimed renewable supply",
        source="Fuel Mix Disclosure Regulations 2005",
        impact=ImpactTier.REPUTATIONAL,
        likelihood=Likelihood.LOW,
        rationale="Mis-selling risk is real but reputational/licence, not direct customer financial harm; existing tracker already audits this.",
        existing_tracker="company/compliance/green_claims_audit.py",
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="consumer_duty_four_outcomes",
        name="Consumer Duty -- good outcomes across products, price, understanding, support",
        source="FCA-style Consumer Duty applied via Ofgem SLC 0 (2023)",
        impact=ImpactTier.REPUTATIONAL,
        likelihood=Likelihood.LOW,
        rationale="Broad conduct standard; existing scorecard already RAGs the four pillars periodically.",
        existing_tracker="company/compliance/consumer_duty.py",
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
]


def tier_1_obligations() -> list[Obligation]:
    return [o for o in REGISTER if o.risk_tier == RiskTier.TIER_1]


def obligations_without_a_tracker() -> list[Obligation]:
    """Real gaps: obligations with no existing_tracker pointer -- these are
    what a real compliance function would flag as unmonitored, not something
    to silently paper over."""
    return [o for o in REGISTER if o.existing_tracker is None]


def register_summary() -> dict:
    """Portfolio-level view: counts by tier, list of Tier-1 obligations, and
    real gaps -- the shape a Head of Compliance would want on one screen."""
    by_tier = {tier: 0 for tier in RiskTier}
    for o in REGISTER:
        by_tier[o.risk_tier] += 1
    return {
        "total_obligations": len(REGISTER),
        "by_tier": {tier.value: count for tier, count in by_tier.items()},
        "tier_1_ids": [o.id for o in tier_1_obligations()],
        "gaps_without_tracker": [o.id for o in obligations_without_a_tracker()],
    }
