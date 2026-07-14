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


# ==========================================================================
# F7 coverage + traceability (INVARIANT_LIBRARY_REDTEAM.md C7).
# Proves the three F7 capabilities and, per R15, MUTATION-tests the two
# controls (resolve-or-degrade tracker; enforcing-invariant-key traceability)
# by injecting each control's named defect and asserting it FIRES.
# ==========================================================================
from datetime import date

from company.compliance import obligations_register as orr
from company.compliance import domain_invariants as di


# --- 1. Physical-harm coverage hole closed (C7a): the top tier was PSR-only. ---

def test_physical_harm_tier_is_no_longer_psr_only():
    ph_ids = {o.id for o in orr.physical_harm_obligations()}
    for added in (
        "gas_safety_incidents",
        "ppm_self_disconnection",
        "winter_disconnection_moratorium",
        "disconnection_conduct",
    ):
        assert added in ph_ids
    assert len(ph_ids) >= 5


def test_every_physical_harm_row_reaches_tier_1():
    for o in orr.physical_harm_obligations():
        assert o.risk_tier == orr.RiskTier.TIER_1, o.id


# --- 2. Regime keying (PORTABILITY item 6): keyed, never implicitly Ofgem. ---

def test_every_obligation_declares_a_known_regime():
    for o in orr.REGISTER:
        assert o.regime in orr.KNOWN_REGIMES, f"{o.id} has unknown regime {o.regime!r}"


def test_register_spans_more_than_ofgem():
    regimes = set(orr.regimes_covered())
    assert regimes >= {"Ofgem", "HSE", "HMRC", "ICO"}
    assert len(regimes) >= 4


# --- 3. Resolve-or-degrade tracker control (C7c) -- MUTATION TESTED (R15). ---

def test_all_declared_trackers_in_the_live_register_resolve():
    for o in orr.REGISTER:
        if o.tracker_paths:
            assert orr.tracker_resolves(o), f"{o.id} cites a module not on disk"
    assert orr.degraded_trackers() == []


def test_tracker_resolves_true_for_a_real_path():
    good = orr.Obligation(
        id="x", name="x", source="x", regime="Ofgem",
        impact=orr.ImpactTier.REPUTATIONAL, likelihood=orr.Likelihood.LOW,
        rationale="x-rationale-longer-than-twenty",
        tracker_paths=("company/compliance/obligations_register.py",),
    )
    assert orr.tracker_resolves(good) is True


def test_tracker_resolves_FIRES_on_a_deleted_module():
    # MUTATION: point a row at a module that does not exist. The control must
    # NOT read it as covered -- if this ever returns True it is theatre.
    bad = orr.Obligation(
        id="bad", name="bad", source="bad", regime="Ofgem",
        impact=orr.ImpactTier.CUSTOMER_FINANCIAL, likelihood=orr.Likelihood.HIGH,
        rationale="bad-rationale-longer-than-twenty",
        existing_tracker="company/does/not/exist.py",
        tracker_paths=("company/does/not/exist.py",),
    )
    assert orr.tracker_resolves(bad) is False
    assert bad.claims_coverage is True


def test_degraded_trackers_FIRES_when_a_cited_module_is_missing(monkeypatch):
    # MUTATION at register level: a row whose module has "gone away" must be
    # surfaced by degraded_trackers() (a silent pass would be theatre).
    bad = orr.Obligation(
        id="ghost", name="ghost", source="ghost", regime="Ofgem",
        impact=orr.ImpactTier.LICENCE_REGULATORY, likelihood=orr.Likelihood.LOW,
        rationale="ghost-rationale-longer-than-twenty",
        existing_tracker="company/ghost/tracker.py",
        tracker_paths=("company/ghost/tracker.py",),
    )
    monkeypatch.setattr(orr, "REGISTER", orr.REGISTER + [bad])
    assert "ghost" in {o.id for o in orr.degraded_trackers()}
    assert "ghost" in {o.id for o in orr.register_gaps()}


def test_free_text_claim_without_paths_does_not_count_as_resolved():
    prose_only = orr.Obligation(
        id="p", name="p", source="p", regime="Ofgem",
        impact=orr.ImpactTier.REPUTATIONAL, likelihood=orr.Likelihood.LOW,
        rationale="prose-only-rationale-longer-than-twenty",
        existing_tracker="some module somewhere",
    )
    assert orr.tracker_resolves(prose_only) is False


# --- 4. Enforcing-invariant-key traceability (C7c/d) -- MUTATION TESTED (R15). ---

def _invariant_ids():
    return {getattr(i, "id", None) for i in di.ALL_INVARIANTS}


def _unresolved_enforcing_keys(register):
    ids = _invariant_ids()
    return [
        (o.id, o.enforcing_invariant_key)
        for o in register
        if o.enforcing_invariant_key and o.enforcing_invariant_key not in ids
    ]


def test_every_enforcing_invariant_key_resolves():
    assert _unresolved_enforcing_keys(orr.REGISTER) == []
    keys = orr.enforcing_invariant_keys()
    assert keys.get("slc_21ba_back_billing_cap") == "back_billing_cap_respected"
    assert keys.get("vat_by_segment") == "vat_segment_matches_consumption"


def test_enforcing_key_consistency_FIRES_on_a_bogus_key():
    # MUTATION: a row citing an invariant that does not exist must be caught.
    bogus = orr.Obligation(
        id="drift", name="drift", source="drift", regime="Ofgem",
        impact=orr.ImpactTier.CUSTOMER_FINANCIAL, likelihood=orr.Likelihood.HIGH,
        rationale="drift-rationale-longer-than-twenty",
        enforcing_invariant_key="no_such_invariant_id",
    )
    assert ("drift", "no_such_invariant_id") in _unresolved_enforcing_keys(orr.REGISTER + [bogus])


def test_back_billing_slc_citation_no_longer_drifts():
    # C7d: row cited "SLC 31A"; enforcing invariant cited "SLC 21BA". They
    # must now agree on 21BA (and neither mention 31A).
    row = next(o for o in orr.REGISTER if o.id == "slc_21ba_back_billing_cap")
    inv = next(i for i in di.ALL_INVARIANTS if getattr(i, "id", None) == "back_billing_cap_respected")
    assert "21BA" in row.source and "31A" not in row.source
    assert "21BA" in inv.source and "31A" not in inv.source
    assert row.enforcing_invariant_key == inv.id


# --- 5. Time-indexing: backfilled ONLY where a real date is cited. ---

def test_effective_from_backfilled_only_where_cited():
    row = next(o for o in orr.REGISTER if o.id == "slc_21ba_back_billing_cap")
    assert row.effective_from == date(2018, 5, 1)
    gas = next(o for o in orr.REGISTER if o.id == "gas_safety_incidents")
    assert gas.effective_from is None and gas.effective_to is None


# --- 6. Honest gaps + F7 summary fields + backward compatibility. ---

def test_microbusiness_back_billing_gap_is_surfaced():
    gap_ids = {o.id for o in orr.obligations_without_a_tracker()}
    assert "microbusiness_back_billing_cap" in gap_ids


def test_register_summary_includes_f7_fields():
    s = orr.register_summary()
    assert "HSE" in s["by_regime"]
    assert "gas_safety_incidents" in s["physical_harm_ids"]
    assert s["enforcing_invariant_keys"]["vat_by_segment"] == "vat_segment_matches_consumption"
    assert s["degraded_tracker_ids"] == []


def test_compliance_report_still_builds():
    from company.compliance.compliance_report import build_compliance_report
    report = build_compliance_report(held_bill_count=0)
    assert report["obligation_count"] == len(orr.REGISTER)
    assert sum(len(v) for v in report["by_tier"].values()) == len(orr.REGISTER)
