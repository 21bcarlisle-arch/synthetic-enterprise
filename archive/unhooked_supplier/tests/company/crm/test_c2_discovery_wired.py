# ARCHIVED LEGS of tests/company/crm/test_c2_discovery_wired.py (archive increment 4b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/crm/test_c2_discovery_wired.py.
import datetime as dt
from company.crm.home_registry import HomeRegistry
from company.crm.onboarding_journey import (
    OnboardingJourneyTracker, OnboardingStage,
)
from company.crm.property_model import (
    EPCRating, PropertyType, TenureType, UNCONFIRMED_DEFAULT_SOURCE,
)
from company.crm.property_discovery import (
    SELF_DISCLOSURE_CONFIDENCE, EPC_LOOKUP_CONFIDENCE,
    DEFAULT_ASSUMPTION_CONFIDENCE, SOURCE_SELF_DISCLOSED_SIGNUP,
    SOURCE_EPC_CERTIFICATE_LOOKUP,
)
from company.crm import decarb_recommender
from company.crm.decarb_recommender import recommend_from_registry


SWITCH_DATE = dt.date(2024, 1, 5)


ACCT = "C-WIRED-1"


UPRN = "100012345678"


def _import_lines(module):
    import inspect
    lines = []
    for raw in inspect.getsource(module).splitlines():
        s = raw.strip()
        if s.startswith('import ') or s.startswith('from '):
            lines.append(s)
    return lines


def _ground_truth_import_violations(import_lines):
    """Return the import lines (if any) that reach for sim-side ground truth
    -- the saas belief-of-record property model, or any simulation/sim module.

    The company belief layer builds its property picture from OBSERVED events
    only (company.crm.property_model / property_discovery). Importing
    saas/property_model.py (the ground-truth home record) or a simulation
    module here would be an epistemic-wall breach: the plan would then be able
    to read a truth a real supplier could never see. This is the shared
    checker behind every wall-guard test below; a violation is any offending
    import line.
    """
    bad = []
    for line in import_lines:
        if 'saas' in line or 'simulation' in line:
            bad.append(line)
        elif line.startswith('import sim') or line.startswith('from sim'):
            bad.append(line)
    return bad



def _wired_tracker():
    registry = HomeRegistry()
    tracker = OnboardingJourneyTracker(home_registry=registry)
    return registry, tracker


def test_onboarding_opens_belief_from_signup_disclosure():
    registry, tracker = _wired_tracker()
    tracker.start_journey(
        ACCT, SWITCH_DATE, uprn=UPRN,
        property_disclosure=dict(
            property_type=PropertyType.TERRACED,
            tenure=TenureType.PRIVATE_RENTED,
            bedrooms=2,
        ),
    )
    prop = registry.get_profile(ACCT)
    # Disclosed attributes carry the signup source at moderate confidence.
    assert prop.property_type == PropertyType.TERRACED
    assert prop.source_for('property_type') == SOURCE_SELF_DISCLOSED_SIGNUP
    assert prop.confidence_for('property_type') == SELF_DISCLOSURE_CONFIDENCE
    assert prop.confidence_for('bedrooms') == SELF_DISCLOSURE_CONFIDENCE
    # EPC is never known at signup -- unconfirmed population-average default.
    assert prop.source_for('epc_rating') == UNCONFIRMED_DEFAULT_SOURCE
    assert prop.confidence_for('epc_rating') == DEFAULT_ASSUMPTION_CONFIDENCE
    # As-of clock is the signup date, not "today".
    assert prop.as_of_for('property_type') == SWITCH_DATE


def test_onboarding_without_registry_is_unchanged():
    # Backward compatibility: the pre-existing (unwired) call signature still
    # works and simply opens no belief.
    tracker = OnboardingJourneyTracker()
    j = tracker.start_journey(ACCT, SWITCH_DATE)
    assert j.current_stage == OnboardingStage.SWITCH_REQUESTED
    assert tracker.home_registry is None


def test_onboarding_without_uprn_opens_no_belief():
    registry, tracker = _wired_tracker()
    tracker.start_journey(ACCT, SWITCH_DATE)  # no uprn disclosed
    assert registry.get_profile_or_none(ACCT) is None


def test_decarb_consumes_discovered_belief_not_ground_truth():
    registry, tracker = _wired_tracker()
    tracker.start_journey(
        ACCT, SWITCH_DATE, uprn=UPRN,
        property_disclosure=dict(property_type=PropertyType.TERRACED),
    )
    plan = recommend_from_registry(registry, ACCT)
    # A real plan was produced from the belief layer.
    assert plan.customer_id == ACCT
    assert len(plan.recommendations) > 0
    # The plan is built at the confidence the company actually holds, and
    # that confidence equals the registry's own belief gauge -- not 1.0.
    belief = registry.belief_confidence(ACCT)
    assert plan.belief_confidence == belief['overall_confidence']
    assert 0.0 < plan.belief_confidence < 1.0


def test_decarb_plan_provisional_when_belief_weak():
    registry, tracker = _wired_tracker()
    # Bare signup: almost everything is unconfirmed default -> weak belief.
    tracker.start_journey(ACCT, SWITCH_DATE, uprn=UPRN)
    plan = recommend_from_registry(registry, ACCT)
    assert plan.is_provisional_on_weak_belief
    assert plan.summary()['provisional_on_weak_belief'] is True


def test_epc_lookup_upgrades_confidence_and_flows_to_decision():
    registry, tracker = _wired_tracker()
    tracker.start_journey(ACCT, SWITCH_DATE, uprn=UPRN)
    before = recommend_from_registry(registry, ACCT).belief_confidence
    # A real EPC-register lookup arrives later as its own event over time.
    tracker.record_epc_lookup(ACCT, EPCRating.F, as_of=dt.date(2024, 3, 1))
    prop = registry.get_profile(ACCT)
    assert prop.epc_rating == EPCRating.F
    assert prop.source_for('epc_rating') == SOURCE_EPC_CERTIFICATE_LOOKUP
    assert prop.confidence_for('epc_rating') == EPC_LOOKUP_CONFIDENCE
    after = recommend_from_registry(registry, ACCT).belief_confidence
    # Confidence rose because a discovery event landed.
    assert after > before
    # And the now-known poor EPC changes the actual recommendation content
    # (F-band terraced-class homes get wall insulation the default D did not).
    plan_after = recommend_from_registry(registry, ACCT)
    measures = {r.measure.value for r in plan_after.recommendations}
    assert 'cavity_wall_insulation' in measures or 'solid_wall_insulation' in measures


def test_recommend_from_registry_reads_only_the_belief_object():
    # The consumer must get its facts from the registry's belief, so if the
    # belief diverges from any hypothetical real home, the plan follows the
    # BELIEF. Prove it: disclose a value, then confirm the plan reflects the
    # disclosed/believed value, with no path to a "true" one.
    registry, tracker = _wired_tracker()
    tracker.start_journey(
        ACCT, SWITCH_DATE, uprn=UPRN,
        property_disclosure=dict(property_type=PropertyType.FLAT),
    )
    # Overwrite belief EPC via an observed lookup to a good band.
    tracker.record_epc_lookup(ACCT, EPCRating.B, as_of=dt.date(2024, 2, 1))
    plan = recommend_from_registry(registry, ACCT)
    measures = {r.measure.value for r in plan.recommendations}
    # Good EPC (B) -> no wall/loft insulation recommended: the decision
    # tracked the BELIEF, not some other truth.
    assert 'cavity_wall_insulation' not in measures
    assert 'solid_wall_insulation' not in measures
    assert 'loft_insulation' not in measures


def test_decarb_recommender_imports_no_ground_truth():
    assert _ground_truth_import_violations(_import_lines(decarb_recommender)) == []


def test_onboarding_journey_imports_no_ground_truth():
    from company.crm import onboarding_journey
    assert _ground_truth_import_violations(_import_lines(onboarding_journey)) == []


def test_home_registry_imports_no_ground_truth():
    from company.crm import home_registry
    assert _ground_truth_import_violations(_import_lines(home_registry)) == []

