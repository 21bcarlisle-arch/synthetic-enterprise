"""Tests for company/compliance/obligations_register.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 1."""
from company.compliance.obligations_register import (
    REGISTER,
    ImpactTier,
    Likelihood,
    RiskTier,
    ControlType,
    ValidationDepth,
    ReportingVisibility,
    derive_risk_tier,
    tier_1_obligations,
    obligations_without_a_tracker,
    register_summary,
)


def test_physical_harm_is_always_tier_1_regardless_of_likelihood():
    assert derive_risk_tier(ImpactTier.PHYSICAL_HARM, Likelihood.LOW) == RiskTier.TIER_1
    assert derive_risk_tier(ImpactTier.PHYSICAL_HARM, Likelihood.HIGH) == RiskTier.TIER_1


def test_customer_financial_reaches_tier_1_at_medium_or_high_likelihood():
    assert derive_risk_tier(ImpactTier.CUSTOMER_FINANCIAL, Likelihood.HIGH) == RiskTier.TIER_1
    assert derive_risk_tier(ImpactTier.CUSTOMER_FINANCIAL, Likelihood.MEDIUM) == RiskTier.TIER_1
    assert derive_risk_tier(ImpactTier.CUSTOMER_FINANCIAL, Likelihood.LOW) == RiskTier.TIER_2


def test_reputational_is_never_tier_1():
    for likelihood in Likelihood:
        assert derive_risk_tier(ImpactTier.REPUTATIONAL, likelihood) != RiskTier.TIER_1


def test_impact_ranking_order_matches_director_principle():
    # PHYSICAL_HARM > CUSTOMER_FINANCIAL > LICENCE_REGULATORY > COMPANY_FINANCIAL > REPUTATIONAL
    # at matched likelihood, earlier-ranked impacts must never resolve to a
    # laxer tier than later-ranked ones.
    tier_rank = {RiskTier.TIER_1: 0, RiskTier.TIER_2: 1, RiskTier.TIER_3: 2}
    impacts_in_order = [
        ImpactTier.PHYSICAL_HARM, ImpactTier.CUSTOMER_FINANCIAL,
        ImpactTier.LICENCE_REGULATORY, ImpactTier.COMPANY_FINANCIAL, ImpactTier.REPUTATIONAL,
    ]
    for likelihood in Likelihood:
        tiers = [tier_rank[derive_risk_tier(i, likelihood)] for i in impacts_in_order]
        assert tiers == sorted(tiers), f"impact ranking violated at likelihood={likelihood}"


def test_obligation_risk_tier_property_matches_function():
    for o in REGISTER:
        assert o.risk_tier == derive_risk_tier(o.impact, o.likelihood)


def test_tier_1_obligations_get_preventive_full_population_immediate_ntfy_by_default():
    for o in tier_1_obligations():
        if o.control_type_override is None:
            assert o.control_type == ControlType.PREVENTIVE_GATE
        if o.testing_depth_override is None:
            assert o.testing_depth == ValidationDepth.FULL_POPULATION
        if o.reporting_visibility_override is None:
            assert o.reporting_visibility == ReportingVisibility.IMMEDIATE_NTFY


def test_every_obligation_has_a_non_empty_rationale():
    for o in REGISTER:
        assert o.rationale and len(o.rationale) > 20


def test_billing_accuracy_is_tier_1():
    billing = next(o for o in REGISTER if o.id == "slc_6_7_billing_accuracy")
    assert billing.risk_tier == RiskTier.TIER_1


def test_vat_by_segment_is_tier_1():
    # Same class as the R10 C6 defect (SME billed as Household at 20% VAT).
    vat = next(o for o in REGISTER if o.id == "vat_by_segment")
    assert vat.risk_tier == RiskTier.TIER_1


def test_psr_vulnerability_is_tier_1_via_physical_harm_despite_low_likelihood():
    psr = next(o for o in REGISTER if o.id == "psr_vulnerability_duties")
    assert psr.impact == ImpactTier.PHYSICAL_HARM
    assert psr.likelihood == Likelihood.LOW
    assert psr.risk_tier == RiskTier.TIER_1


def test_register_covers_every_category_named_in_the_directors_principle():
    sources_text = " ".join(o.source + o.name for o in REGISTER).lower()
    for keyword in ["billing", "back-billing", "gsop", "vulnerab", "vat", "settlement", "switching", "smart meter"]:
        assert keyword in sources_text, f"register missing coverage for: {keyword}"


def test_obligations_without_a_tracker_are_real_gaps_not_silently_hidden():
    gaps = obligations_without_a_tracker()
    gap_ids = {o.id for o in gaps}
    # billing accuracy and VAT-by-segment are genuine, known, not-yet-built gaps
    # (Phase 3/2 of this programme close them) -- must show up here, not be
    # papered over with a fake tracker reference.
    assert "slc_6_7_billing_accuracy" in gap_ids
    assert "vat_by_segment" in gap_ids


def test_register_summary_shape():
    summary = register_summary()
    assert summary["total_obligations"] == len(REGISTER)
    assert set(summary["by_tier"].keys()) == {"tier_1", "tier_2", "tier_3"}
    assert sum(summary["by_tier"].values()) == len(REGISTER)
    assert "slc_6_7_billing_accuracy" in summary["tier_1_ids"]


def test_register_ids_are_unique():
    ids = [o.id for o in REGISTER]
    assert len(ids) == len(set(ids))


def test_register_has_at_least_twelve_seed_obligations():
    assert len(REGISTER) >= 12
