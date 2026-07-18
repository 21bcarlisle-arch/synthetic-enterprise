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


# ==========================================================================
# SUPPLIER_REPORTING_STANDARD.md §4: three MANUAL-by-design additions
# (capital adequacy, fuel mix disclosure, cyber/NIS baseline). Proves each is
# registered, correctly tiered, and -- per R15 -- reports MANUAL/unchecked
# rather than a fail-open GREEN, with the control MUTATION-tested.
# ==========================================================================

_SECTION_4_IDS = (
    "capital_adequacy_floor_target",
    "fuel_mix_disclosure",
    "cyber_baseline_nis",
)


def test_all_three_section_4_obligations_are_registered():
    ids = {o.id for o in orr.REGISTER}
    for oid in _SECTION_4_IDS:
        assert oid in ids, f"§4 obligation {oid} missing from register"


def test_section_4_obligations_are_declared_manual_by_design():
    manual_ids = {o.id for o in orr.manual_obligations()}
    for oid in _SECTION_4_IDS:
        assert oid in manual_ids, f"{oid} should be MANUAL-by-design"


def test_every_manual_obligation_states_when_it_becomes_checkable():
    # A MANUAL row that does not say when it becomes checkable is a silent gap.
    for o in orr.manual_obligations():
        assert o.becomes_checkable_when, f"{o.id} MANUAL without becomes_checkable_when"
        assert len(o.becomes_checkable_when) > 20


def test_manual_obligations_are_not_reported_as_covered():
    # R15: a MANUAL obligation must NOT resolve an automated tracker (that would
    # read as automated-covered / a false GREEN). It should instead surface as a
    # declared gap (no tracker) so the register stays honest.
    for o in orr.manual_obligations():
        assert not orr.tracker_resolves(o), f"{o.id} MANUAL yet resolves a tracker"
    gap_ids = {o.id for o in orr.obligations_without_a_tracker()}
    for oid in _SECTION_4_IDS:
        assert oid in gap_ids, f"{oid} should surface as an untracked gap, not covered"


def test_manual_declaration_violations_is_empty_on_the_live_register():
    # The R15 control returns [] only when every MANUAL row is honest. This is
    # an explicit empty-set assertion (not a fail-silent default-pass).
    assert orr.manual_declaration_violations() == []


def test_manual_declaration_control_FIRES_on_a_missing_note(monkeypatch):
    # MUTATION: a MANUAL row with no becomes_checkable_when must be caught.
    bad = orr.Obligation(
        id="manual_no_note", name="x", source="x", regime="Ofgem",
        impact=orr.ImpactTier.LICENCE_REGULATORY, likelihood=orr.Likelihood.LOW,
        rationale="manual-row-missing-its-becomes-checkable-note",
        automation_status=orr.AutomationStatus.MANUAL,
        becomes_checkable_when=None,
    )
    monkeypatch.setattr(orr, "REGISTER", orr.REGISTER + [bad])
    violations = dict(orr.manual_declaration_violations())
    assert "manual_no_note" in violations


def test_manual_declaration_control_FIRES_on_fail_open_green(monkeypatch):
    # MUTATION: a MANUAL row that ALSO resolves a real tracker would read as
    # automated-covered (a false GREEN). The control must catch that.
    bad = orr.Obligation(
        id="manual_but_green", name="x", source="x", regime="Ofgem",
        impact=orr.ImpactTier.LICENCE_REGULATORY, likelihood=orr.Likelihood.LOW,
        rationale="manual-row-that-secretly-resolves-a-real-tracker",
        automation_status=orr.AutomationStatus.MANUAL,
        becomes_checkable_when="when the thing lands and can be checked properly",
        tracker_paths=("company/compliance/obligations_register.py",),  # exists on disk
    )
    monkeypatch.setattr(orr, "REGISTER", orr.REGISTER + [bad])
    reasons = [r for (i, r) in orr.manual_declaration_violations() if i == "manual_but_green"]
    assert any("fail-open-green" in r for r in reasons)


def test_capital_adequacy_registered_no_fabricated_date():
    o = next(x for x in orr.REGISTER if x.id == "capital_adequacy_floor_target")
    assert o.regime == "Ofgem"
    assert o.risk_tier == orr.RiskTier.TIER_3  # LICENCE_REGULATORY + LOW
    assert o.effective_from is None and o.effective_to is None  # not fabricated
    assert "115" in o.name  # the recalled Capital Target figure is carried
    assert o.existing_tracker is None  # honest gap: no cash/balance-sheet layer yet


def test_fuel_mix_disclosure_cross_references_report_without_claiming_coverage():
    o = next(x for x in orr.REGISTER if x.id == "fuel_mix_disclosure")
    # It points at the surface that PRODUCES the disclosure...
    assert o.cross_reference and "annual_report" in o.cross_reference
    # ...but a produce-only cross_reference must NOT count as coverage (else it
    # would fail-open-green: a file existing on disk != the disclosure validated).
    assert o.claims_coverage is False
    assert orr.tracker_resolves(o) is False


def test_cyber_baseline_is_go_live_not_sim_physics():
    o = next(x for x in orr.REGISTER if x.id == "cyber_baseline_nis")
    assert o.regime == "Ofgem"  # Ofgem is the NIS competent authority for energy
    assert "NIS" in o.source or "Network and Information" in o.source
    assert o.effective_from is None  # NIS-2018 in-force date not fabricated
    assert "go-live" in o.becomes_checkable_when.lower() or "deployment" in o.becomes_checkable_when.lower()


def test_section_4_obligations_report_manual_never_green_in_compliance_report():
    # End-to-end through the consumer: even on the happy path (0 held bills,
    # which GREENs the gated Tier-1 rows), the three §4 additions report MANUAL,
    # never GREEN -- the R15 fail-open-green guard at the report boundary.
    from company.compliance.compliance_report import build_compliance_report
    report = build_compliance_report(held_bill_count=0)
    all_rows = [row for rows in report["by_tier"].values() for row in rows]
    by_id = {row["id"]: row for row in all_rows}
    for oid in _SECTION_4_IDS:
        assert by_id[oid]["status"] == "MANUAL", f"{oid} must report MANUAL, got {by_id[oid]['status']}"


def test_register_summary_exposes_manual_fields():
    s = orr.register_summary()
    for oid in _SECTION_4_IDS:
        assert oid in s["manual_ids"]
    assert s["manual_declaration_violations"] == []
