"""Anchored domain-invariants library -- Phase 2 of DOMAIN_SENSE_AND_COMPLIANCE.md.

UK domain law and market reality expressed as checkable data, so rendered
artefacts and data surfaces can be tested against real anchors rather than
"looks about right." Harness-side (outside the wall -- the harness plays
Ofgem/external auditor here, not the company).

Every invariant below is pulled from an anchor this codebase already
established (discovery-agent sourced, with its own provenance trail) rather
than freshly guessed for this module:
  - VAT rates, standing charges, non-commodity cost shares, margin and
    bad-debt ranges: docs/market_research/ASSUMPTIONS.md.
  - TDCV (Typical Domestic Consumption Value) bands: Ofgem TDCV review, via
    docs/market_research/ons_consumption_profiles.md.
  - Year-specific plausible unit-rate ranges: company/pricing/ofgem_price_cap.py's
    already-anchored annual cap tables (Phase 47a) -- reused here, not
    re-derived, so the two never drift apart.

This module seeds the library (>=20 invariants, DoD requirement) with
checkable predicates. It does not itself sample or gate anything -- Phase 3
(pre-bill validation gate) and Phase 5 (sanity daemon + population tests)
are the consumers.

R10 (CLAUDE.md): an absurdity-class defect (e.g. the C6 SME-as-Household
20%-VAT bill) closes by EXTENDING this library so the whole class fails
automatically thereafter, never by patching the one instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from company.billing.back_billing import BackBillingAssessment, BackBillingReason
from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh
from company.compliance.segment_debt_policy import (
    LPCDCA_EFFECTIVE_FROM,
    check_debt_terms_lawful_for_segment as _check_debt_terms_lawful_for_segment,
    select_debt_terms as _select_debt_terms,
)

_CAP_ANCHOR_YEARS = range(2019, 2026)
_ELEC_CAP_BY_YEAR = {
    y: get_cap_unit_rate_gbp_per_mwh("electricity", y) for y in _CAP_ANCHOR_YEARS
}
_GAS_CAP_BY_YEAR = {
    y: get_cap_unit_rate_gbp_per_mwh("gas", y) for y in _CAP_ANCHOR_YEARS
}


# ADVISOR_STEER_BACKBILLING_GATE.md item 2 (2026-07-12, "jurisdiction
# discipline for the oracle... add a jurisdiction field to the invariants
# library schema so this is structural, not remembered"): every invariant
# in this library today is UK-specific (VAT rates, Ofgem TDCV bands, Ofgem
# price cap) but carried no explicit tag saying so. Defaults to "UK" for
# every existing invariant (all genuinely are) -- a future non-UK addition
# (AU/FR/BE, per REGULATORY_RULES_AS_FIDELITY_ORACLE.md's portability-lens
# register) must set this explicitly rather than silently inheriting a
# UK-only default, and any consumer validating UK output can assert
# jurisdiction == "UK" structurally rather than relying on someone
# remembering which invariants are which market's law.
_UK = "UK"


# REGULATION_COMMONS_DOCTRINE.md (2026-07-12) item 3: "law is time-indexed --
# the blindfold covers regulation itself... the library schema gains
# effective_from/effective_to." None means "no registered change of law
# within this codebase's evidence" (i.e. treat as in force for all modelled
# years), NOT "no effective date exists in reality" -- only backfilled where
# a specific date is actually anchored (see BACK_BILLING_CAP_RESPECTED
# below); fabricating a date for an invariant with no cited source would be
# worse than leaving it None.


@dataclass(frozen=True)
class RateInvariant:
    """An exact rate/proportion with a small tolerance (e.g. VAT -- there is
    no legitimate reason for a bill to charge 5.4% VAT for a residential
    customer)."""
    id: str
    description: str
    source: str
    value: float
    tolerance: float = 0.0005
    jurisdiction: str = _UK
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    def check(self, actual: float) -> bool:
        return abs(actual - self.value) <= self.tolerance


@dataclass(frozen=True)
class RangeInvariant:
    """A plausible [low, high] envelope (e.g. standing charges, margins) --
    real values vary within a band, so exact-match would be wrong; falling
    outside the band is the absurdity signal."""
    id: str
    description: str
    source: str
    low: float
    high: float
    unit: str
    jurisdiction: str = _UK
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    def check(self, actual: float) -> bool:
        return self.low <= actual <= self.high


@dataclass(frozen=True)
class YearlyRangeInvariant:
    """A plausible envelope around an anchored year-specific point value
    (e.g. the Ofgem domestic price cap). The cap is a CEILING, not a
    target -- a fixed-term customer locked in during a calmer market can
    legitimately sit well below a later-spiked cap, so the band is
    asymmetric: generous downside margin, tighter upside margin (still
    catches gross implausibilities -- order-of-magnitude errors, wrong-year
    rates). Years before `by_year`'s earliest key (e.g. pre-2019, before
    the Ofgem cap existed at all) have no valid anchor to compare against --
    `check()` always passes for those rather than extrapolating backwards
    from the nearest post-cap year, which found real false positives on
    genuine pre-cap competitive-market pricing (Phase 5, 2026-07-09)."""
    id: str
    description: str
    source: str
    by_year: dict
    unit: str
    low_margin: float = 0.6   # allow down to 40% of the anchor (fixed-term downside)
    high_margin: float = 0.5  # allow up to 150% of the anchor
    jurisdiction: str = _UK
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    def plausible_range(self, year: int) -> tuple[float, float]:
        years = sorted(self.by_year)
        anchor_year = year if year in self.by_year else min(years, key=lambda y: abs(y - year))
        point = self.by_year[anchor_year]
        return point * (1 - self.low_margin), point * (1 + self.high_margin)

    def check(self, actual: float, year: int) -> bool:
        if year < min(self.by_year):
            return True  # no valid anchor pre-dating the cap -- can't check
        low, high = self.plausible_range(year)
        return low <= actual <= high


# --- Bill structure (docs/market_research/ASSUMPTIONS.md, "Bill Structure") ---

VAT_RESIDENTIAL = RateInvariant(
    id="vat_residential", description="VAT rate for residential energy supply",
    source="HMRC VAT Notice 701/19 (reduced domestic rate)", value=0.05,
)
VAT_SME = RateInvariant(
    id="vat_sme", description="VAT rate for SME/non-domestic energy supply",
    source="HMRC (standard rate; de minimis <33kWh/day not modelled)", value=0.20,
)
STANDING_CHARGE_ELEC_RESI = RangeInvariant(
    id="standing_charge_elec_resi", description="Electricity standing charge, residential",
    source="Ofgem Price Cap Q1-Q4 2024", low=0.25, high=0.35, unit="GBP/day",
)
STANDING_CHARGE_ELEC_SME = RangeInvariant(
    id="standing_charge_elec_sme", description="Electricity standing charge, SME",
    source="Industry tariff survey", low=0.40, high=0.70, unit="GBP/day",
)
STANDING_CHARGE_GAS_RESI = RangeInvariant(
    id="standing_charge_gas_resi", description="Gas standing charge, residential",
    source="Ofgem Price Cap Q1-Q4 2024", low=0.22, high=0.32, unit="GBP/day",
)
STANDING_CHARGE_GAS_SME = RangeInvariant(
    id="standing_charge_gas_sme", description="Gas standing charge, SME",
    source="Industry", low=0.30, high=0.55, unit="GBP/day",
)
NON_COMMODITY_ELEC_RESI = RangeInvariant(
    id="non_commodity_elec_resi", description="Non-commodity cost, electricity residential",
    source="Ofgem energy price stats, Elexon charges", low=50.0, high=65.0, unit="GBP/MWh",
)
NON_COMMODITY_ELEC_SME = RangeInvariant(
    id="non_commodity_elec_sme", description="Non-commodity cost, electricity SME",
    source="Elexon, Ofgem", low=35.0, high=55.0, unit="GBP/MWh",
)
NON_COMMODITY_GAS_RESI = RangeInvariant(
    id="non_commodity_gas_resi", description="Non-commodity cost, gas residential",
    source="Ofgem, Xoserve", low=8.0, high=15.0, unit="GBP/MWh",
)
NON_COMMODITY_GAS_SME = RangeInvariant(
    id="non_commodity_gas_sme", description="Non-commodity cost, gas SME",
    source="Xoserve, industry", low=6.0, high=12.0, unit="GBP/MWh",
)
NON_COMMODITY_SHARE_OF_BILL = RangeInvariant(
    id="non_commodity_share_of_bill", description="Non-commodity as % of all-in bill",
    source="Ofgem Electricity/Gas Stats", low=0.30, high=0.45, unit="fraction",
)

# --- TDCV consumption bands (Ofgem TDCV review, via ons_consumption_profiles.md) ---

TDCV_ELEC_LOW = RangeInvariant(
    id="tdcv_elec_low", description="TDCV electricity Low band",
    source="Ofgem TDCV 2026 review", low=1400.0, high=1800.0, unit="kWh/year",
)
TDCV_ELEC_MEDIUM = RangeInvariant(
    id="tdcv_elec_medium", description="TDCV electricity Medium band",
    source="Ofgem TDCV 2026 review", low=2300.0, high=2700.0, unit="kWh/year",
)
TDCV_ELEC_HIGH = RangeInvariant(
    id="tdcv_elec_high", description="TDCV electricity High band",
    source="Ofgem TDCV 2026 review", low=3600.0, high=4000.0, unit="kWh/year",
)
TDCV_GAS_LOW = RangeInvariant(
    id="tdcv_gas_low", description="TDCV gas Low band",
    source="Ofgem TDCV 2026 review", low=5500.0, high=6500.0, unit="kWh/year",
)
TDCV_GAS_MEDIUM = RangeInvariant(
    id="tdcv_gas_medium", description="TDCV gas Medium band",
    source="Ofgem TDCV 2026 review", low=9000.0, high=10000.0, unit="kWh/year",
)
TDCV_GAS_HIGH = RangeInvariant(
    id="tdcv_gas_high", description="TDCV gas High band",
    source="Ofgem TDCV 2026 review", low=13000.0, high=15000.0, unit="kWh/year",
)
# Wide population-plausibility envelope (Phase 5/6's population tests): a
# resi customer's annual consumption should sit somewhere near the TDCV
# spread, not off by an order of magnitude (the C6 SME-as-Household class).
RESI_CONSUMPTION_ENVELOPE_ELEC = RangeInvariant(
    id="resi_consumption_envelope_elec", description="Plausible annual resi electricity consumption",
    # High bound widened from an initial 8,000 after Phase 5's population
    # check found real, legitimate HH-metered electric-heated resi
    # customers (C7/C8/C9) at 11,500-13,231 kWh/yr in this sim's own
    # verified-correct population (run_output_latest.json, 2026-07-09) --
    # standard Ofgem TDCV bands don't cover electric heating, a real
    # minority-but-present UK home-heating type this sim explicitly models.
    source="Derived from Ofgem TDCV Low/High with headroom for electric-heated homes",
    low=500.0, high=15000.0, unit="kWh/year",
)
RESI_CONSUMPTION_ENVELOPE_GAS = RangeInvariant(
    id="resi_consumption_envelope_gas", description="Plausible annual resi gas consumption",
    # High bound widened from an initial 25,000 for the same reason --
    # real observed max in this sim's verified population is 35,913 kWh/yr
    # (large/poorly-insulated homes), run_output_latest.json 2026-07-09.
    source="Derived from Ofgem TDCV Low/High with headroom", low=1500.0, high=40000.0, unit="kWh/year",
)

_DAYS_PER_MONTH = 30.44

# Per-bill (sub-annual period) plausibility. Deliberately NOT the annual
# envelope above scaled linearly by period length -- gas and electric-heated
# homes are heavily seasonal (a winter month can carry 20-25% of a whole
# year's gas use), so naively annualizing one month's figure massively
# overstates a true winter peak. Found live wiring Phase 3's gate: linear
# annualization held 401/1550 real, already-verified-correct bills (up to
# ~28,000 kWh/yr projected from a genuine ~2,200 kWh January gas bill).
# These monthly-equivalent bounds are calibrated with real headroom above
# the actual observed range in this sim's verified population (elec
# 52-1,945 kWh/month, gas 382-5,412 kWh/month, run_output_latest.json
# 2026-07-09) -- wide enough to tolerate real seasonal/electric-heating
# variation, narrow enough to still catch a genuine order-of-magnitude
# error (an SME-scale account on a resi record, the R10 C6 class).
RESI_CONSUMPTION_ENVELOPE_ELEC_MONTHLY = RangeInvariant(
    id="resi_consumption_envelope_elec_monthly",
    description="Plausible per-bill (~30 day) resi electricity consumption",
    # High bound sits between the real observed resi max (1,945 kWh/month,
    # run_output_latest.json) and C6's real SME consumption (2,346.8
    # kWh/month, BILL_CORRECTNESS_ADDENDUM.md) -- comfortable margin above
    # genuine domestic variation, still catches that exact defect class
    # (an SME account mislabeled resi) if it recurs.
    source="Calibrated against observed sim population + headroom", low=15.0, high=2100.0, unit="kWh/~30 days",
)
RESI_CONSUMPTION_ENVELOPE_GAS_MONTHLY = RangeInvariant(
    id="resi_consumption_envelope_gas_monthly",
    description="Plausible per-bill (~30 day) resi gas consumption",
    source="Calibrated against observed sim population + headroom", low=100.0, high=8000.0, unit="kWh/~30 days",
)

# --- Year-specific unit-rate plausibility (company/pricing/ofgem_price_cap.py, Phase 47a) ---

UNIT_RATE_ELEC_RESI_BY_YEAR = YearlyRangeInvariant(
    id="unit_rate_elec_resi_by_year", description="Plausible resi electricity unit rate by year",
    source="company/pricing/ofgem_price_cap.py (Ofgem Default Tariff Cap, Phase 47a)",
    by_year=_ELEC_CAP_BY_YEAR, unit="GBP/MWh",
)
UNIT_RATE_GAS_RESI_BY_YEAR = YearlyRangeInvariant(
    id="unit_rate_gas_resi_by_year", description="Plausible resi gas unit rate by year",
    source="company/pricing/ofgem_price_cap.py (Ofgem Default Tariff Cap, Phase 47a)",
    by_year=_GAS_CAP_BY_YEAR, unit="GBP/MWh",
)

# --- Margin & bad-debt plausibility ---

NET_MARGIN_PCT_OF_REVENUE = RangeInvariant(
    id="net_margin_pct_of_revenue", description="Net margin as % of revenue",
    source="Ofgem Retail Market Report; Cornwall Insight", low=0.02, high=0.05, unit="fraction",
)
GROSS_MARGIN_PCT_OF_REVENUE = RangeInvariant(
    id="gross_margin_pct_of_revenue", description="Gross margin as % of revenue",
    source="Ofgem", low=0.08, high=0.15, unit="fraction",
)
BAD_DEBT_RATE_RESI = RangeInvariant(
    id="bad_debt_rate_resi", description="Bad debt rate, residential",
    source="Ofgem Annual Report; Cornwall Insight", low=0.01, high=0.03, unit="fraction",
)
BAD_DEBT_RATE_SME = RangeInvariant(
    id="bad_debt_rate_sme", description="Bad debt rate, SME",
    source="Industry", low=0.005, high=0.02, unit="fraction",
)


@dataclass(frozen=True)
class StructuralInvariant:
    """A named, sourced rule that isn't a single rate/range comparison --
    a compound/structural check over a bill-shaped dict (e.g. 'a capped
    back-billing amount was actually written off, not silently charged in
    full'). The predicate lives in a same-named check_*() function below
    (mirrors check_vat/check_resi_bill_consumption_plausible, which already
    pair a metadata object with a separate predicate function) rather than
    on the dataclass itself, since the input shape varies per rule."""
    id: str
    description: str
    source: str
    jurisdiction: str = _UK
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


# ADVISOR_STEER_BACKBILLING_GATE.md item 1(c): "add the cap as a pre-bill
# Tier-1 invariant (a catch-up bill breaching 12 months without a recorded
# fault attribution is HELD)". Registered here as the named/sourced rule;
# enforced by check_back_billing_cap_respected() below and wired into the
# pre-bill validation gate (company/billing/pre_bill_validation.py).
BACK_BILLING_CAP_RESPECTED = StructuralInvariant(
    id="back_billing_cap_respected",
    description=(
        "A catch-up bill that breaches the SLC 21BA 12-month recovery "
        "window, with no recorded customer-fault attribution, must not "
        "charge the excess -- it must be written off, not billed"
    ),
    # Fresh Expert-Hour finding (2026-07-12): this previously said "domestic/
    # microbusiness", overclaiming coverage the mechanism doesn't enforce --
    # company/billing/back_billing.py is domestic-only by design ("Non-
    # domestic customers NOT protected (B2B commercial terms apply)", its own
    # module docstring), and this check inherits that scope exactly
    # (is_domestic = segment == "resi"). Real UK back-billing rules DO also
    # protect microbusinesses -- that is a genuine, registered coverage gap
    # (PRIORITIES.md backlog), not something to paper over by citing a wider
    # source than what's actually enforced.
    source="Ofgem SLC 21BA (domestic back-billing protection -- microbusiness NOT yet enforced, see PRIORITIES.md)",
    # REGULATION_COMMONS_DOCTRINE.md item 3 backfill: the real anchor date,
    # matching company/billing/back_billing.py's own _BACK_BILLING_RULES_START
    # constant -- not fabricated, cited from the same source that constant
    # already carries. No effective_to: still in force.
    effective_from=date(2018, 5, 1),
)


# BILL_TO_LEDGER_LINKAGE.md (2026-07-12, P0): "for any period, revenue
# recognised on the billed clock == sum of bills issued (to the penny;
# divergence = held exception)". Investigation confirmed the board's
# published headline (total_net_gbp, saas/reporting/annual_report.py:581)
# is settlement-derived and structurally never reads bills at all -- a real,
# already-existing SEPARATE P&L view (saas/ledger.py's derive_pnl(),
# "financial.ledger.*"/"ledger_pnl" in the report) IS bill-derived (its
# billing_event.amount_gbp is literally bill["total_amount_gbp"]), but until
# this steer it recognised revenue for HELD bills too -- a bill the pre-bill
# Tier-1 gate has not cleared for issue, which is a real revenue-recognition
# error (you cannot recognise revenue for a bill you have not sent).
# simulation/run_phase4c_on_phase2b.py now filters to validate_bills()'s
# PASSING population before calling build_ledger() -- this check is the
# regression guard so a future refactor can't silently reintroduce the gap.
BILLED_CLOCK_RECONCILES_WITH_ISSUED_BILLS = StructuralInvariant(
    id="billed_clock_reconciles_with_issued_bills",
    description=(
        "The ledger's recognised billed revenue (sum of billing_event "
        "amounts) must equal the sum of total_amount_gbp across only the "
        "bills that actually passed the pre-bill Tier-1 gate (were "
        "genuinely issued) -- never bills still HELD in the exception queue"
    ),
    source="Real revenue-recognition principle: a supplier cannot book revenue for an unissued bill",
)


# INVARIANT_LIBRARY_REDTEAM.md (2026-07-13) C1: the flagship vat_by_segment
# control was a production tautology -- it checked the bill's VAT rate against
# the rate its own `segment` label implies, both derived from the same label,
# so it could never catch a MISLABEL (the C6 SME-as-Household class it is named
# for). This structural invariant registers the independent cross-check
# (enforced by check_vat_consistent_with_consumption() above and wired into the
# pre-bill validation gate): the applied VAT rate must be consistent with the
# segment IMPLIED BY METERED CONSUMPTION, not only with the declared label.
VAT_SEGMENT_MATCHES_CONSUMPTION = StructuralInvariant(
    id="vat_segment_matches_consumption",
    description=(
        "The VAT rate applied to a bill must be consistent with the segment "
        "IMPLIED BY METERED CONSUMPTION, not only with the bill's own declared "
        "segment label -- a domestic (5%) rate on an I&C-scale metered load is "
        "the C6 SME-as-Household mislabel. Independent of the label, so it "
        "catches a mislabel the arithmetic label-vs-rate check (a tautology) "
        "structurally cannot. One-directional: only a clearly non-domestic "
        "load contradicts a domestic rate; low consumption cannot refute a "
        "business label (a genuine microbusiness consumes domestic volumes)."
    ),
    source="HMRC VAT Notice 701/19 + Ofgem TDCV bands (INVARIANT_LIBRARY_REDTEAM.md C1; R10 C6 class)",
)


# --- Segment debt T&C (atom C11_segment_debt_policy; world twin W2_9) ---
#
# The company applies debt terms & conditions from OBSERVABLE segment +
# PUBLISHED regulation only (company/compliance/segment_debt_policy.py). These
# three structural invariants register the law the company reads; the checker
# below (delegating to that module) is the Tier-1 control that FIRES when a
# wrong-segment T&C is applied. The correct-side is derived independently of
# the applied terms (anti-tautology, R15).

DEBT_INTEREST_BUSINESS_ONLY = StructuralInvariant(
    id="debt_interest_business_only",
    description=(
        "Statutory late-payment interest (base rate + 8pts) applies to BUSINESS "
        "debts only (SME/I&C) under LPCDCA 1998; it is EXCLUDED for domestic "
        "customers, whose energy debt is a consumer contract the Act does not "
        "cover. Charging a domestic arrears account statutory interest is the "
        "named wrong-segment defect this control fires on."
    ),
    source=(
        "Late Payment of Commercial Debts (Interest) Act 1998 (business "
        "statutory interest; domestic consumer debt excluded)"
    ),
    # REGULATION_COMMONS_DOCTRINE.md item 3 backfill: the Act's real
    # commencement date, cited not fabricated (initially small-business
    # creditors; extended to all B2B debt by 7 Aug 2002). No effective_to:
    # still in force.
    effective_from=LPCDCA_EFFECTIVE_FROM,
)

DEBT_NO_DOMESTIC_LATE_CHARGES = StructuralInvariant(
    id="debt_no_domestic_late_charges",
    description=(
        "A DOMESTIC arrears account carries NO late-payment charge -- domestic "
        "late-payment charges are largely regulated out under Ofgem SLC / "
        "Consumer Duty fairness. A late charge applied to a domestic account is "
        "the named wrong-segment defect this control fires on. Business "
        "commercial T&C may include a late charge, so this bites domestic only."
    ),
    source="Ofgem Standard Licence Conditions / Consumer Duty (domestic charge restrictions)",
    # effective_from left None per this module's own convention (no single
    # registered date anchored in this codebase's evidence; treat as in force
    # for all modelled years -- fabricating a date would be worse).
)

DEBT_TARIFF_ELIGIBILITY_PAYMENT_CONDITIONED = StructuralInvariant(
    id="debt_tariff_eligibility_payment_conditioned",
    description=(
        "Payment-conditioned tariff eligibility (DD-discount / good-payer "
        "gating) is LAWFUL for both segments, but constrained: a DD tariff must "
        "be set off a realistic consumption estimate and must not be used to "
        "over-collect credit (Ofgem Direct Debit Market Compliance Review). "
        "Modelled as a permitted-but-constrained policy flag, not a free "
        "parameter -- so 'good payer discount' cannot be read as licence to "
        "over-hold credit from the same reliable payers."
    ),
    source="Ofgem Direct Debit Market Compliance Review (active 2026 enforcement)",
)


def check_debt_terms_lawful_for_segment(segment, applied, as_of) -> bool:
    """Tier-1 control for the segment-debt-T&C invariants above: returns False
    (FIRES) when a wrong-segment debt T&C is applied (a domestic late charge,
    statutory interest on a domestic account, or a business interest charge at
    the wrong statutory rate). Independent of the applied terms and fails
    closed on missing/malformed input (R15). Delegates to
    company/compliance/segment_debt_policy.py -- the company's own reading of
    the law, never a SIM ground-truth read."""
    return _check_debt_terms_lawful_for_segment(segment, applied, as_of)


def correct_debt_terms_for_segment(segment, as_of):
    """The correct debt T&C the company should apply to a segment on a date --
    the company's OWN policy object (segment_debt_policy.select_debt_terms).
    Exposed here so consumers reach the whole segment-debt library through one
    module, matching vat_rate_for_segment's placement."""
    return _select_debt_terms(segment, as_of)


ALL_INVARIANTS: list = [
    VAT_RESIDENTIAL, VAT_SME,
    STANDING_CHARGE_ELEC_RESI, STANDING_CHARGE_ELEC_SME,
    STANDING_CHARGE_GAS_RESI, STANDING_CHARGE_GAS_SME,
    NON_COMMODITY_ELEC_RESI, NON_COMMODITY_ELEC_SME,
    NON_COMMODITY_GAS_RESI, NON_COMMODITY_GAS_SME,
    NON_COMMODITY_SHARE_OF_BILL,
    TDCV_ELEC_LOW, TDCV_ELEC_MEDIUM, TDCV_ELEC_HIGH,
    TDCV_GAS_LOW, TDCV_GAS_MEDIUM, TDCV_GAS_HIGH,
    RESI_CONSUMPTION_ENVELOPE_ELEC, RESI_CONSUMPTION_ENVELOPE_GAS,
    RESI_CONSUMPTION_ENVELOPE_ELEC_MONTHLY, RESI_CONSUMPTION_ENVELOPE_GAS_MONTHLY,
    UNIT_RATE_ELEC_RESI_BY_YEAR, UNIT_RATE_GAS_RESI_BY_YEAR,
    NET_MARGIN_PCT_OF_REVENUE, GROSS_MARGIN_PCT_OF_REVENUE,
    BAD_DEBT_RATE_RESI, BAD_DEBT_RATE_SME,
    BACK_BILLING_CAP_RESPECTED,
    BILLED_CLOCK_RECONCILES_WITH_ISSUED_BILLS,
    VAT_SEGMENT_MATCHES_CONSUMPTION,
    DEBT_INTEREST_BUSINESS_ONLY,
    DEBT_NO_DOMESTIC_LATE_CHARGES,
    DEBT_TARIFF_ELIGIBILITY_PAYMENT_CONDITIONED,
]


def vat_rate_for_segment(segment: str) -> Optional[float]:
    """The correct VAT rate for a segment -- 'resi' -> 5%, anything else
    (SME/I&C) -> 20%. The exact check the C6 SME-as-Household defect
    (billed 20% VAT... no wait, billed as if resi at some point, or the
    reverse -- see R10) would have caught automatically."""
    return VAT_RESIDENTIAL.value if segment == "resi" else VAT_SME.value


def check_vat(segment: str, actual_rate: float) -> bool:
    expected = vat_rate_for_segment(segment)
    invariant = VAT_RESIDENTIAL if segment == "resi" else VAT_SME
    return invariant.check(actual_rate) and abs(actual_rate - expected) <= invariant.tolerance


def consumption_implied_vat_rate(
    commodity: str, kwh: float, days_in_period: float
) -> Optional[float]:
    """The VAT rate IMPLIED by metered consumption alone, independent of the
    bill's declared `segment` label -- the independent signal the vat_by_segment
    control needs so it stops checking the label against itself (C1 red-team,
    docs/design/INVARIANT_LIBRARY_REDTEAM.md 2026-07-13; R10 C6
    SME-as-Household class).

    Returns:
      - VAT_SME.value (0.20) when consumption is CLEARLY above the anchored
        domestic ceiling (Ofgem TDCV bands + electric-heating headroom; the
        RESI_CONSUMPTION_ENVELOPE_*_MONTHLY high bounds, calibrated with
        headroom above the real observed resi max of 1,945 kWh/mo elec) -- the
        load is I&C-scale, so a domestic 5% rate on it is the C6 mislabel.
      - VAT_RESIDENTIAL.value (0.05) when consumption sits within the domestic
        envelope. NOTE this does NOT prove the customer is domestic: a genuine
        small business (corner shop / microbusiness) legitimately consumes
        domestic volumes and correctly pays 20%. This branch is therefore only
        ever used by the cross-check below to REFRAIN from flagging, never to
        force a 5% rate onto a business.
      - None when there is no usable signal (a non-elec/gas commodity, or a
        non-positive kwh / period -- the separate sign / period invariants own
        those cases, not this one).

    Deliberately ONE-DIRECTIONAL in strength: only HIGH consumption carries
    enough information to contradict a label; LOW consumption does not."""
    if commodity not in ("electricity", "gas"):
        return None
    if kwh <= 0 or days_in_period <= 0:
        return None
    envelope = (
        RESI_CONSUMPTION_ENVELOPE_ELEC_MONTHLY if commodity == "electricity"
        else RESI_CONSUMPTION_ENVELOPE_GAS_MONTHLY
    )
    domestic_ceiling = envelope.high * (days_in_period / _DAYS_PER_MONTH)
    if kwh > domestic_ceiling:
        return VAT_SME.value
    return VAT_RESIDENTIAL.value


def check_vat_consistent_with_consumption(
    segment: str,
    commodity: str,
    actual_vat_rate: float,
    kwh: float,
    days_in_period: float,
) -> bool:
    """Independent cross-check for the `vat_by_segment` Tier-1 control.

    The arithmetic `check_vat()` above compares the bill's VAT rate to the rate
    its OWN `segment` label implies. Both sides are the same function of the
    same label, so it is a tautology: it passes every bill the generator can
    emit (`vat = subtotal * vat_rate(segment)`) and structurally CANNOT catch a
    MISLABEL -- the exact C6 SME-as-Household class it is named for
    (docs/design/INVARIANT_LIBRARY_REDTEAM.md C1, 2026-07-13). This check
    re-bases the expected rate on `consumption_implied_vat_rate()` -- a signal
    independent of the label -- so a mislabelled customer whose VAT is
    self-consistent with its WRONG label is still caught.

    Returns True (consistent / not-refutable) UNLESS the metered load is clearly
    I&C-scale (implied 20%) AND the bill applied a domestic (5%) rate -- the C6
    undercharge. The reverse (a business rate on domestic-scale consumption) is
    NEVER flagged: small businesses legitimately consume domestic volumes, so
    low consumption cannot refute a business label without false-positiving
    every microbusiness. Honest signal strength: strong in one direction only,
    which is why the flag is a hard HELD only for the well-anchored direction."""
    implied = consumption_implied_vat_rate(commodity, kwh, days_in_period)
    if implied is None or implied == VAT_RESIDENTIAL.value:
        # No usable signal, or the weak (non-flaggable) direction: consumption
        # looks domestic, which a genuine small business also does.
        return True
    # implied == VAT_SME.value: consumption is clearly non-domestic. The applied
    # rate MUST be the business rate; a domestic (5%) rate here is the mislabel.
    return abs(actual_vat_rate - VAT_SME.value) <= VAT_SME.tolerance


def check_unit_rate_plausible(fuel: str, year: int, unit_rate_gbp_per_mwh: float) -> bool:
    invariant = UNIT_RATE_ELEC_RESI_BY_YEAR if fuel == "electricity" else UNIT_RATE_GAS_RESI_BY_YEAR
    return invariant.check(unit_rate_gbp_per_mwh, year)


def check_resi_consumption_plausible(fuel: str, annual_kwh: float) -> bool:
    """Population/annual-level check (Phase 5/6) -- use on a full year's
    total, never on a single sub-annual bill (see check_resi_bill_consumption_
    plausible for that -- linear annualization of one month badly distorts
    seasonal fuels, see that function's docstring)."""
    invariant = RESI_CONSUMPTION_ENVELOPE_ELEC if fuel == "electricity" else RESI_CONSUMPTION_ENVELOPE_GAS
    return invariant.check(annual_kwh)


def check_resi_bill_consumption_plausible(fuel: str, kwh: float, days_in_period: float) -> bool:
    """Per-bill plausibility check for a sub-annual billing period. Scales
    the monthly-equivalent envelope by the period's actual length rather
    than annualizing the observed value and comparing to an annual band --
    annualizing (kwh * 365/days) would massively overstate a genuine winter
    gas/electric-heating peak as an implausible whole-year projection."""
    invariant = (
        RESI_CONSUMPTION_ENVELOPE_ELEC_MONTHLY if fuel == "electricity"
        else RESI_CONSUMPTION_ENVELOPE_GAS_MONTHLY
    )
    scale = days_in_period / _DAYS_PER_MONTH
    return invariant.low * scale <= kwh <= invariant.high * scale


_BACK_BILLING_LIMIT_DAYS = 365


def check_back_billing_cap_respected(bill: dict) -> bool:
    """ADVISOR_STEER_BACKBILLING_GATE.md item 1(c) enforcement: "a catch-up
    bill breaching 12 months without a recorded fault attribution is HELD."

    Deliberately does NOT trust `bill["catchup_back_billing_cap_applied"]`
    (the flag the assessment step already set) -- it independently
    re-derives the SLC 21BA 12-month test from the bill's own catch-up
    consumption period and accurate-bill date (`period_end`, the date this
    exact bill was issued -- the clock anchors on the accurate bill, not
    the read date, per the steer's element 2). A bill that breaches the
    window must show the excess as a genuine write-off, not silently
    charge it in full; that is what "HELD" means operationally here --
    the excess is blocked from recovery, not that the bill itself is
    withheld from the customer.

    Overcharges (credits owed to the customer) are correctly never capped
    (company/billing/back_billing.py's documented asymmetry) -- not a gap,
    passes trivially.

    R3/R4 self-correction (2026-07-12, invariant_redteam_2026-07-12.md,
    same-session adversarial red-team on this exact function): the first
    version had two real, executed-and-confirmed gaps this rewrite closes.
    (a) Finding 3 -- only checked `written_off_gbp > 0` (existence), never
    the MAGNITUDE, so a 1p token write-off against a five-year, £5,000
    breach passed as "cap respected." Now independently recomputes the
    expected write-off via `BackBillingAssessment` (the same real
    mechanism `_resolve_catchup` itself uses -- R3, reuse not reinvent)
    and compares magnitudes. (b) Finding 4 -- an unrecognised/missing
    `catchup_direction`, or a missing period/delta field, silently
    returned True (fail-OPEN). A Tier-1 compliance gate must fail CLOSED
    on data it cannot verify -- HELD, not silently passed -- so those
    paths now return False.
    """
    if not bill.get("catchup_applied"):
        return True

    direction = bill.get("catchup_direction")
    if direction not in ("undercharge", "overcharge"):
        return False  # fail closed: unrecognised/missing direction
    if direction == "overcharge":
        return True  # credits are never capped -- correct, not a gap

    period_start_raw = bill.get("catchup_period_start")
    period_end_raw = bill.get("catchup_period_end")
    billing_date_raw = bill.get("period_end")
    raw_delta = bill.get("catchup_raw_delta_gbp")
    if not period_start_raw or not period_end_raw or not billing_date_raw or raw_delta is None:
        return False  # fail closed: cannot verify, so do not pass it

    # Fresh Expert-Hour finding (2026-07-12, HARDEN pass on the red-team fix
    # itself): a PRESENT-but-malformed date string (not just a missing one)
    # previously raised an uncaught ValueError here, which propagated all
    # the way up through validate_bills() and aborted validation of the
    # ENTIRE batch -- taking down every other, genuinely fine bill in the
    # same call, the exact "uncaught exception kills the loop" class
    # CLAUDE.md's key-learnings section names. Same fail-closed principle
    # as the missing-field case above, now applied to malformed values too.
    try:
        period_start = datetime.fromisoformat(period_start_raw).date()
        period_end = datetime.fromisoformat(period_end_raw).date()
        billing_date = datetime.fromisoformat(billing_date_raw).date()
    except (ValueError, TypeError):
        return False  # fail closed: cannot parse, so do not pass it

    assessment = BackBillingAssessment(
        account_id=bill.get("customer_id", ""),
        billing_date=billing_date,
        consumption_period_start=period_start,
        consumption_period_end=period_end,
        billed_amount_gbp=raw_delta,
        reason=BackBillingReason.ESTIMATED_READ_CORRECTED,
        is_domestic=bill.get("segment", "resi") == "resi",
    )
    if not assessment.cap_applies:
        return True  # genuinely doesn't breach the window -- nothing to write off

    expected_written_off = assessment.written_off_gbp
    actual_written_off = bill.get("catchup_written_off_gbp", 0.0)
    return abs(actual_written_off - expected_written_off) <= 0.05


def check_billed_clock_reconciles(total_billed_gbp: float, issued_bills: list) -> bool:
    """`total_billed_gbp` is the ledger's own recognised-revenue figure
    (saas.ledger.derive_pnl()'s `total_billed_gbp`, built from
    billing_event amounts). `issued_bills` must be the population that
    ACTUALLY fed build_ledger() -- i.e. validate_bills()'s passing half,
    never the raw unfiltered bill list (which would include HELD bills
    that were never issued and must not count as recognised revenue).
    Exact-to-the-penny match expected by construction; a real divergence
    means something in the pipeline silently changed what feeds the
    ledger without updating this invariant -- fail loud, don't average
    over it."""
    expected = round(sum(b.get("total_amount_gbp", 0.0) for b in issued_bills), 2)
    return abs(round(total_billed_gbp, 2) - expected) <= 0.01


def invariant_count() -> int:
    return len(ALL_INVARIANTS)
