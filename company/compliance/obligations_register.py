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
`tracker_paths` field points at the module(s) that already monitor it, so
the register classifies risk without duplicating monitoring code.

Design note on risk_tier(): billing accuracy (SLC 6/7) is CUSTOMER_FINANCIAL
impact, which nominally ranks below PHYSICAL_HARM -- but the director's own
Principle 1 ("bills must be accurate, above all... 100% preventive
validation, zero tolerance") makes it Tier 1 regardless. The mapping below
reflects that: CUSTOMER_FINANCIAL impact reaches Tier 1 at MEDIUM/HIGH
likelihood (a system issuing thousands of bills has high hit-rate on any
latent bug class -- see R10's C6 SME-as-Household precedent), matching the
director's explicit call without needing a special case.

F7 coverage + traceability (2026-07-14, INVARIANT_LIBRARY_REDTEAM.md C7).
Three structural defects the red-team found in the seed register, closed here
as a CLASS (R10), not as instances:

  1. PHYSICAL-HARM COVERAGE HOLE. The top severity tier held exactly one row
     (PSR). Gas-safety, PPM self-disconnection, the winter moratorium and
     wrongful-disconnection conduct are textbook physical-harm domains with
     live trackers but had no register row, so they could never reach Tier-1
     via derive_risk_tier(). Those rows now exist.

  2. UNVERIFIED `existing_tracker` FREE TEXT -> resolve-or-degrade. The
     old `existing_tracker` string was never machine-checked; a tracker
     pointing at a deleted module read as "covered". Coverage is now asserted
     against `tracker_paths` (repo-relative paths that must exist on disk):
     `tracker_resolves()` degrades an obligation whose cited module has gone
     away to a GAP rather than a silent pass (`degraded_trackers()`).

  3. NO ENFORCING-INVARIANT KEY -> SLC-citation drift undetected. The
     back-billing row cited "SLC 31A" while its enforcing invariant cited
     "SLC 21BA" (real UK domestic back-billing is SLC 21B/21BA; "31A" was
     wrong) and the two shared no cross-reference key. Rows that a named
     domain invariant enforces now carry `enforcing_invariant_key`, so a
     consistency test (tests/company/compliance/) can assert the key resolves
     in domain_invariants.ALL_INVARIANTS and that the licence-condition
     citations agree -- the drift now fails a test.

Regime keying (PORTABILITY_DESIGN_CONSTRAINTS.md item 6, REGULATION_COMMONS
doctrine): every obligation declares its `regime` (Ofgem, HMRC, HSE, ICO,
BSC/MRA, DESNZ, ...) rather than implicitly assuming Ofgem, so a second
market's regulator fits behind the same seam. Time-indexing: `effective_from`
/`effective_to` are backfilled ONLY where a real, cited date exists (never
fabricated) -- most rows leave them None, matching domain_invariants.py's
convention.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


# Repo root, for resolving `tracker_paths` against the filesystem. This file
# lives at <root>/company/compliance/obligations_register.py, so the root is
# three parents up. No import of any tracker module -- existence-on-disk only
# (SIMPLICITY GUARD: the simplest construct that makes the claim checkable).
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


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


# Known regulatory regimes. Not exhaustive -- extend as the register grows.
# The point (PORTABILITY item 6): an obligation is keyed by regime, NOT
# implicitly Ofgem, so a second market's regulator fits the same shape.
KNOWN_REGIMES: frozenset[str] = frozenset({
    "Ofgem",          # energy licence conditions (SLCs), GSOP, PSR, smart-meter, disconnection
    "HMRC",           # VAT
    "HSE",            # gas safety
    "ICO",            # data protection / UK GDPR
    "BSC/MRA",        # settlement + metering industry codes
    "DESNZ",          # govt energy schemes (WHD, ECO)
    "Energy Ombudsman",  # ADR / redress scheme
})


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

    `regime` is the regulator/legal regime the obligation lives under (never
    implicitly Ofgem -- PORTABILITY item 6).

    `tracker_paths` are repo-relative module/dir paths that already monitor
    this obligation. Coverage is asserted against them: `tracker_resolves()`
    is True only when they all exist on disk, so a tracker that has been
    deleted/renamed degrades this obligation to a GAP (`degraded_trackers()`)
    instead of reading as covered. `existing_tracker` is the human-readable
    description of the same pointer (kept for the compliance report's prose).
    Genuinely uncovered obligations set BOTH to None/() -- a real gap to flag,
    not to silently backfill here.

    `enforcing_invariant_key` names the domain_invariants.py invariant id that
    ENFORCES this obligation, where one exists -- the traceability link that
    lets a consistency test catch SLC-citation drift between an obligation and
    the invariant that enforces it. None where no single named invariant
    enforces the obligation.

    `effective_from`/`effective_to` are backfilled ONLY where a real, cited
    date exists (never fabricated); None otherwise.

    `testing_frequency` and the tier-derived defaults (control_type/
    testing_depth/reporting_visibility) can be overridden per-obligation when
    judgment differs from the mechanical default -- always paired with
    `rationale` explaining why.
    """
    id: str
    name: str
    source: str  # law/SLC reference, e.g. "Ofgem SLC 6/7", "Consumer Contracts Regulations 2013"
    regime: str  # regulator/legal regime -- keyed, never implicitly Ofgem
    impact: ImpactTier
    likelihood: Likelihood
    rationale: str
    existing_tracker: Optional[str] = None
    tracker_paths: tuple[str, ...] = ()
    enforcing_invariant_key: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
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

    @property
    def claims_coverage(self) -> bool:
        """This obligation asserts a monitoring tracker exists (via either the
        machine-checkable paths or the human free-text pointer)."""
        return bool(self.tracker_paths) or self.existing_tracker is not None


def tracker_resolves(obligation: Obligation) -> bool:
    """A tracker is RESOLVED only when the obligation carries machine-checkable
    `tracker_paths` AND every one of them exists on disk. An obligation that
    claims coverage in free text but carries no resolvable path, or whose cited
    module has been deleted/renamed, does NOT resolve -- the degrade-to-gap
    behaviour the F7 red-team (C7c) required. This is the control that must be
    able to FAIL (R15): point a row at a module that does not exist and it
    returns False."""
    if not obligation.tracker_paths:
        return False
    return all(os.path.exists(os.path.join(_REPO_ROOT, p)) for p in obligation.tracker_paths)


# Seed register. Spans every category the director's principle 2 names, plus
# the F7 coverage expansion (physical-harm rows + previously-absent regimes).
# Not exhaustive -- extending this list (and wiring newly-identified
# `existing_tracker=None` gaps to a real monitor) is ongoing register
# maintenance, not a one-off population exercise.
REGISTER: list[Obligation] = [
    Obligation(
        id="slc_6_7_billing_accuracy",
        name="Billing must be accurate",
        source="Ofgem SLC 6/7",
        regime="Ofgem",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.HIGH,
        rationale=(
            "Director's Principle 1, binding: 100% of bills validated before issue, zero "
            "tolerance, continuous. High likelihood because every bill run hits the same "
            "code paths at volume -- a latent bug class (R10's C6 SME-as-Household "
            "precedent) recurs every run until the class itself is closed, not sampled."
        ),
        existing_tracker=None,  # no single dedicated tracker; the accuracy family is a set of invariants
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="slc_21ba_back_billing_cap",
        name="Back-billing cap -- cannot bill >12 months of unbilled consumption",
        source="Ofgem SLC 21BA (domestic back-billing protection; microbusiness NOT yet enforced)",
        regime="Ofgem",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.MEDIUM,
        rationale=(
            "Real financial harm if breached (surprise multi-year bill). The live control "
            "is now the pre-bill validation gate's back_billing_cap_respected invariant "
            "(fail-closed on a >12-month catch-up with no fault attribution) -- NOT the "
            "meter-reads catch-up mechanism, which the ADVISOR_STEER_BACKBILLING_GATE "
            "programme proved insufficient. Licence citation corrected 31A->21BA to match "
            "the enforcing invariant (F7/C7d: real UK domestic back-billing is SLC 21B/21BA)."
        ),
        existing_tracker="company/billing/pre_bill_validation.py (back_billing_cap_respected invariant)",
        tracker_paths=("company/billing/pre_bill_validation.py", "company/compliance/domain_invariants.py"),
        enforcing_invariant_key="back_billing_cap_respected",
        effective_from=date(2018, 5, 1),  # matches domain_invariants.py / back_billing.py's cited anchor
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="slc_14_credit_refunds",
        name="Credit refunds within 10 working days of account closure",
        source="Ofgem SLC 14",
        regime="Ofgem",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.MEDIUM,
        rationale="Real customer financial harm (delayed money) if the SLA is missed.",
        existing_tracker="company/billing/credit_refund.py + simulation/credit_refund_events.py",
        tracker_paths=("company/billing/credit_refund.py", "simulation/credit_refund_events.py"),
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="gsop_auto_compensation",
        name="Guaranteed Standards of Performance -- automatic compensation payments",
        source="Ofgem GSOP Regulations",
        regime="Ofgem",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.MEDIUM,
        rationale="Missed auto-compensation is direct customer financial harm plus a licence breach.",
        existing_tracker="company/billing (GSOP compensation physics, Phase 3 unhappy-paths)",
        tracker_paths=("company/billing",),
        testing_frequency=ValidationFrequency.DAILY,
    ),
    Obligation(
        id="psr_vulnerability_duties",
        name="Priority Services Register -- vulnerable customer welfare duties",
        source="Ofgem SLC 0 / Consumer Duty / PSR Code of Practice",
        regime="Ofgem",
        impact=ImpactTier.PHYSICAL_HARM,
        likelihood=Likelihood.LOW,
        rationale=(
            "A failure (missing a PSR flag before a supply interruption for a life-support/"
            "medically-dependent customer) can plausibly cause physical harm, not just "
            "financial loss -- Tier 1 regardless of likelihood, per the director's impact "
            "ranking. Likelihood is genuinely low in this sim (no real supply interruptions "
            "modelled yet) but the tier does not relax because of that -- impact alone forces "
            "Tier 1 here."
        ),
        existing_tracker="company/crm (vulnerability_register)",
        tracker_paths=("company/crm/vulnerability_register.py",),
        testing_frequency=ValidationFrequency.CONTINUOUS,
    ),
    # --- F7: previously-absent physical-harm rows (C7a). Live trackers exist;
    #     the register simply had no row, so they could never tier to Tier-1. ---
    Obligation(
        id="gas_safety_incidents",
        name="Gas safety -- incident logging, RIDDOR-reportable events, unsafe-appliance duties",
        source="Gas Safety (Installation and Use) Regulations 1998 / Gas Safety (Management) Regulations 1996",
        regime="HSE",
        impact=ImpactTier.PHYSICAL_HARM,
        likelihood=Likelihood.LOW,
        rationale=(
            "Textbook physical-harm domain (CO poisoning, explosion): a mishandled gas-safety "
            "incident risks life. Low likelihood in this sim but PHYSICAL_HARM impact forces "
            "Tier 1 regardless -- the coverage hole F7/C7a closed (was entirely absent from "
            "the register despite a live tracker). No effective_from backfilled: not fabricating "
            "the precise in-force date."
        ),
        existing_tracker="company/billing/gas_safety_incident_register.py",
        tracker_paths=("company/billing/gas_safety_incident_register.py",),
        testing_frequency=ValidationFrequency.CONTINUOUS,
    ),
    Obligation(
        id="ppm_self_disconnection",
        name="Prepayment self-disconnection safeguards -- emergency/friendly-hours credit, vulnerability checks",
        source="Ofgem SLC 27 / SLC 28 (PPM safeguards)",
        regime="Ofgem",
        impact=ImpactTier.PHYSICAL_HARM,
        likelihood=Likelihood.MEDIUM,
        rationale=(
            "A PPM customer self-disconnecting off supply (no heating/cooking) is a physical-harm "
            "risk, especially for the vulnerable in winter -- Tier 1 on impact. Likelihood MEDIUM: "
            "self-disconnection is a routine, high-frequency PPM event, not a tail risk. Coverage "
            "hole F7/C7a closed."
        ),
        existing_tracker="company/billing/ppm_emergency_credit_register.py",
        tracker_paths=("company/billing/ppm_emergency_credit_register.py",),
        testing_frequency=ValidationFrequency.CONTINUOUS,
    ),
    Obligation(
        id="winter_disconnection_moratorium",
        name="Winter/vulnerable disconnection moratorium -- no disconnection of protected customers Oct-Mar",
        source="Ofgem SLC 27 (winter disconnection moratorium; Energy UK Safety Net)",
        regime="Ofgem",
        impact=ImpactTier.PHYSICAL_HARM,
        likelihood=Likelihood.LOW,
        rationale=(
            "Disconnecting a protected/vulnerable household over winter is a physical-harm risk. "
            "Tier 1 on impact. Coverage hole F7/C7a closed (live moratorium tracker existed with "
            "no register row)."
        ),
        existing_tracker="company/billing/winter_moratorium.py",
        tracker_paths=("company/billing/winter_moratorium.py",),
        testing_frequency=ValidationFrequency.CONTINUOUS,
    ),
    Obligation(
        id="disconnection_conduct",
        name="Disconnection conduct -- ability-to-pay assessment, warning steps, PSR check before disconnection",
        source="Ofgem SLC 27 (disconnection conduct)",
        regime="Ofgem",
        impact=ImpactTier.PHYSICAL_HARM,
        likelihood=Likelihood.LOW,
        rationale=(
            "Wrongful disconnection of a home for debt can cause physical harm -- the whole "
            "point of the SLC 27 warning/ability-to-pay/PSR-check sequence. Tier 1 on impact. "
            "Coverage hole F7/C7b closed (disconnection conduct regime was absent)."
        ),
        existing_tracker="company/billing/disconnection_warning.py",
        tracker_paths=("company/billing/disconnection_warning.py",),
        testing_frequency=ValidationFrequency.CONTINUOUS,
    ),
    # --- F7: previously-absent regimes (C7b), each with a real live tracker. ---
    Obligation(
        id="complaints_ombudsman_timescales",
        name="Complaints handling + Energy Ombudsman referral timescales (8-week / deadlock)",
        source="Ofgem Complaints Handling Standards / Energy Ombudsman scheme rules",
        regime="Energy Ombudsman",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.MEDIUM,
        rationale=(
            "Missed complaint-handling / Ombudsman-referral timescales are a licence-conduct "
            "breach and a customer-redress failure. MEDIUM likelihood: complaints are frequent "
            "and timescale-bound. Whole regime was absent from the register (F7/C7b)."
        ),
        existing_tracker="company/crm/complaint_register.py + company/regulatory/ombudsman_register.py",
        tracker_paths=("company/crm/complaint_register.py", "company/regulatory/ombudsman_register.py"),
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="data_protection_gdpr",
        name="Data protection -- lawful basis, breach reporting, subject rights (UK GDPR)",
        source="UK GDPR / Data Protection Act 2018",
        regime="ICO",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale=(
            "Personal-data mishandling is a regulatory (ICO) and reputational exposure; a "
            "notifiable breach carries a 72-hour reporting clock. LOW likelihood in this sim. "
            "Whole regime (ICO) was absent from the register (F7/C7b)."
        ),
        existing_tracker="company/regulatory/privacy_register.py",
        tracker_paths=("company/regulatory/privacy_register.py",),
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="theft_revenue_protection_conduct",
        name="Energy theft / revenue-protection conduct -- evidence handling, safe & proportionate action",
        source="Ofgem SLC (theft) / Theft Act 1968 / revenue-protection code of practice",
        regime="Ofgem",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale=(
            "Mishandled theft/revenue-protection action (wrongful accusation, unsafe meter work) "
            "is a conduct and safety exposure. LOW likelihood. Regime was absent from the "
            "register despite live trackers (F7/C7b)."
        ),
        existing_tracker="company/billing/energy_theft_book.py + company/billing/revenue_protection_register.py",
        tracker_paths=("company/billing/energy_theft_book.py", "company/billing/revenue_protection_register.py"),
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="vat_by_segment",
        name="VAT must be charged at the correct rate by customer segment",
        source="VAT Act 1994 (domestic 5%, business 20%, de minimis rules)",
        regime="HMRC",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.HIGH,
        rationale=(
            "Same class as R10's C6 defect (SME billed as Household at 20% VAT instead of "
            "5%) -- confirmed high-likelihood given it already happened. Tier 1. Enforced by "
            "the segment-independent vat_segment_matches_consumption invariant (F5): a bill "
            "whose declared segment disagrees with its consumption-implied band is HELD -- a "
            "real control, not the self-consistent VAT-rate tautology the F5 red-team flagged. "
            "Kept existing_tracker=None: no dedicated monitoring MODULE, enforced by a shared "
            "invariant."
        ),
        existing_tracker=None,
        enforcing_invariant_key="vat_segment_matches_consumption",
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
    Obligation(
        id="settlement_industry_code",
        name="Settlement / industry-code duties (BSC, MRA metering data obligations)",
        source="BSC / MRA",
        regime="BSC/MRA",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Licence/regulatory impact, low likelihood given settlement already anchored to real Elexon data.",
        existing_tracker="company/billing/metering_exception.py, meter_read_validation.py",
        tracker_paths=("company/billing/metering_exception.py", "company/billing/meter_read_validation.py"),
        testing_frequency=ValidationFrequency.PHASE_CLOSE,
    ),
    Obligation(
        id="marketing_switching_rules",
        name="Marketing and switching conduct rules (cooling-off, misleading claims)",
        source="Consumer Contracts Regulations 2013 / Ofgem SLC (marketing standards)",
        regime="Ofgem",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Licence/regulatory impact; the 14-day cooling-off constant is already hard-anchored.",
        existing_tracker="simulation/acquisition_funnel.py",
        tracker_paths=("simulation/acquisition_funnel.py",),
        testing_frequency=ValidationFrequency.PHASE_CLOSE,
    ),
    Obligation(
        id="smart_meter_rollout_targets",
        name="Smart meter rollout progress reporting",
        source="Ofgem SLC 22 / SLC 45",
        regime="Ofgem",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Reporting obligation, not a customer-facing control; existing tracker already RAGs this.",
        existing_tracker="company/regulatory/compliance.py, ofgem_obligations.py",
        tracker_paths=("company/regulatory/compliance.py", "company/regulatory/ofgem_obligations.py"),
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="whd_eco_social_obligation_spend",
        name="Warm Home Discount / ECO social obligation spend",
        source="WHD Scheme Regulations 2011 / ECO4 2022-2026",
        regime="DESNZ",
        impact=ImpactTier.LICENCE_REGULATORY,
        likelihood=Likelihood.LOW,
        rationale="Mandatory spend tracked continuously by an existing dedicated register.",
        existing_tracker="company/regulatory/social_obligation_register.py",
        tracker_paths=("company/regulatory/social_obligation_register.py",),
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="green_claims_rego",
        name="Green tariff REGO backing must match claimed renewable supply",
        source="Fuel Mix Disclosure Regulations 2005",
        regime="Ofgem",
        impact=ImpactTier.REPUTATIONAL,
        likelihood=Likelihood.LOW,
        rationale="Mis-selling risk is real but reputational/licence, not direct customer financial harm; existing tracker already audits this.",
        existing_tracker="company/compliance/green_claims_audit.py",
        tracker_paths=("company/compliance/green_claims_audit.py",),
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    Obligation(
        id="consumer_duty_four_outcomes",
        name="Consumer Duty -- good outcomes across products, price, understanding, support",
        source="FCA-style Consumer Duty applied via Ofgem SLC 0 (2023)",
        regime="Ofgem",
        impact=ImpactTier.REPUTATIONAL,
        likelihood=Likelihood.LOW,
        rationale="Broad conduct standard; existing scorecard already RAGs the four pillars periodically.",
        existing_tracker="company/compliance/consumer_duty.py",
        tracker_paths=("company/compliance/consumer_duty.py",),
        testing_frequency=ValidationFrequency.PERIODIC,
    ),
    # --- F7: a genuine, honestly-surfaced GAP (no tracker) -- the acknowledged
    #     microbusiness back-billing hole (domain_invariants.py:336-341). Kept
    #     existing_tracker=None so it degrades to a real gap, not a silent pass. ---
    Obligation(
        id="microbusiness_back_billing_cap",
        name="Microbusiness back-billing protection (NOT yet enforced -- known gap)",
        source="Ofgem SLC 21BA extension to microbusiness customers",
        regime="Ofgem",
        impact=ImpactTier.CUSTOMER_FINANCIAL,
        likelihood=Likelihood.MEDIUM,
        rationale=(
            "Real UK back-billing rules protect microbusinesses too, but the enforcing "
            "invariant (back_billing_cap_respected) is domestic-only by design (is_domestic = "
            "segment == 'resi'); microbusiness protection is a genuine, registered coverage gap "
            "(domain_invariants.py acknowledges it). Surfaced here with no tracker so the "
            "register reports it as an OPEN GAP rather than hiding it."
        ),
        existing_tracker=None,
        testing_frequency=ValidationFrequency.PER_BILL_RUN,
    ),
]


def tier_1_obligations() -> list[Obligation]:
    return [o for o in REGISTER if o.risk_tier == RiskTier.TIER_1]


def physical_harm_obligations() -> list[Obligation]:
    """The highest-impact tier. F7 closed the coverage hole where this was a
    near-empty set (PSR only)."""
    return [o for o in REGISTER if o.impact == ImpactTier.PHYSICAL_HARM]


def obligations_without_a_tracker() -> list[Obligation]:
    """Genuine DECLARED gaps: obligations that claim no tracker at all
    (existing_tracker is None AND no tracker_paths). These are what a real
    compliance function flags as unmonitored -- not something to silently
    paper over here."""
    return [o for o in REGISTER if o.existing_tracker is None and not o.tracker_paths]


def degraded_trackers() -> list[Obligation]:
    """DEGRADED coverage: obligations that CLAIM a tracker but whose coverage
    cannot be machine-verified -- either no resolvable `tracker_paths`, or a
    cited module that has been deleted/renamed off disk. The F7/C7c control:
    an unverified 'covered' claim degrades to a gap rather than reading as a
    silent pass. This control can FAIL by construction (R15): point any row at
    a non-existent path and it appears here."""
    return [o for o in REGISTER if o.claims_coverage and not tracker_resolves(o)]


def register_gaps() -> list[Obligation]:
    """The full set of obligations NOT reliably covered: declared gaps
    (no tracker) plus degraded ones (claimed but unverifiable). This is the
    honest 'unmonitored surface' a Head of Compliance needs."""
    seen: set[str] = set()
    out: list[Obligation] = []
    for o in obligations_without_a_tracker() + degraded_trackers():
        if o.id not in seen:
            seen.add(o.id)
            out.append(o)
    return out


def enforcing_invariant_keys() -> dict[str, str]:
    """Map of obligation id -> the domain_invariants.py invariant id that
    enforces it, for the rows that carry one. A consistency test asserts each
    value resolves in domain_invariants.ALL_INVARIANTS -- the traceability
    link that makes SLC-citation drift (F7/C7d) a test failure."""
    return {o.id: o.enforcing_invariant_key for o in REGISTER if o.enforcing_invariant_key}


def regimes_covered() -> dict[str, int]:
    """Count of obligations by regulatory regime -- proves the register is
    keyed by regime, not implicitly Ofgem (PORTABILITY item 6)."""
    counts: dict[str, int] = {}
    for o in REGISTER:
        counts[o.regime] = counts.get(o.regime, 0) + 1
    return counts


def register_summary() -> dict:
    """Portfolio-level view: counts by tier and regime, Tier-1 and
    physical-harm obligations, real gaps (declared + degraded), and the
    enforcing-invariant traceability map -- the shape a Head of Compliance
    would want on one screen."""
    by_tier = {tier: 0 for tier in RiskTier}
    for o in REGISTER:
        by_tier[o.risk_tier] += 1
    return {
        "total_obligations": len(REGISTER),
        "by_tier": {tier.value: count for tier, count in by_tier.items()},
        "by_regime": regimes_covered(),
        "tier_1_ids": [o.id for o in tier_1_obligations()],
        "physical_harm_ids": [o.id for o in physical_harm_obligations()],
        "gaps_without_tracker": [o.id for o in obligations_without_a_tracker()],
        "degraded_tracker_ids": [o.id for o in degraded_trackers()],
        "enforcing_invariant_keys": enforcing_invariant_keys(),
    }
