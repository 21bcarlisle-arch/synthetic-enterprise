"""Tests for company/analytics/cohort_discovery.py -- the D-SEGMENT
company-side believed-cohort twin (SEGMENTATION_GENERATOR_BUILD_PLAN.md step
3; SEGMENTATION_RECONCILIATION_FRAME.md §0 canonical wall ruling).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from company.analytics.cohort_discovery import (
    ACCOMMODATION_LEVELS,
    ACCOMMODATION_PRIOR,
    CARS_LEVELS,
    CARS_PRIOR,
    NSSEC_LEVELS,
    NSSEC_PRIOR,
    TENURE_LEVELS,
    TENURE_PRIOR,
    BelievedCohort,
    InteractionObservation,
    PublicPriorObservation,
    believed_book_distribution,
    discover_cohort,
)


# ---------------------------------------------------------------------------
# WALL: this module must never import simulation.*/sim.* -- statically
# verified here as a belt-and-braces check alongside tools/epistemic_verifier
# (which is the mechanised enforcement; this test documents the intent at the
# unit-test level too).
# ---------------------------------------------------------------------------

def test_module_imports_no_simulation_internals():
    src = Path("company/analytics/cohort_discovery.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.split(".")[0] in ("simulation", "sim")
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in ("simulation", "sim")


def test_epistemic_verifier_passes_on_this_module():
    import tools.epistemic_verifier as ev
    passed, violations = ev.scan(files=["company/analytics/cohort_discovery.py"])
    assert passed, violations


# ---------------------------------------------------------------------------
# green_stance: STRUCTURALLY EXCLUDED. No observable exists, ever.
# ---------------------------------------------------------------------------

def test_green_stance_is_always_none():
    for i in range(50):
        prior = PublicPriorObservation(customer_id=f"C{i}", region="London", tenure="own_outright")
        interaction = InteractionObservation(customer_id=f"C{i}", churn_estimate=0.9,
                                             contact_channels_used=["app", "app", "app"])
        belief = discover_cohort(prior, interaction)
        assert belief.green_stance is None


def test_believed_cohort_dataclass_has_no_settable_green_stance():
    # The field exists ONLY as a fixed None default -- cannot be constructed
    # with a real value without explicitly overriding the dataclass contract.
    bc = BelievedCohort(
        customer_id="X", region="London", heating_fuel=None, tenure="own_outright",
        accommodation="flat", cars="0", nssec="higher",
        price_sensitivity=None, channel_pref=None,
    )
    assert bc.green_stance is None


# ---------------------------------------------------------------------------
# Public priors: region/tenure/heating_fuel pass through; undisclosed tenure
# falls back to the national modal category.
# ---------------------------------------------------------------------------

def test_region_and_heating_fuel_pass_through_exactly():
    prior = PublicPriorObservation(customer_id="C1", region="Wales", tenure="social_rent", heating_fuel="oil")
    belief = discover_cohort(prior)
    assert belief.region == "Wales"
    assert belief.heating_fuel == "oil"


def test_disclosed_tenure_is_believed_exactly():
    for t in TENURE_LEVELS:
        prior = PublicPriorObservation(customer_id="C1", region="London", tenure=t)
        belief = discover_cohort(prior)
        assert belief.tenure == t


def test_undisclosed_tenure_falls_back_to_national_modal():
    prior = PublicPriorObservation(customer_id="C1", region="London", tenure=None)
    belief = discover_cohort(prior)
    assert belief.tenure == max(TENURE_PRIOR, key=lambda k: TENURE_PRIOR[k])


def test_unrecognised_tenure_string_falls_back_to_modal_not_silently_kept():
    prior = PublicPriorObservation(customer_id="C1", region="London", tenure="nonsense_value")
    belief = discover_cohort(prior)
    assert belief.tenure in TENURE_LEVELS


# ---------------------------------------------------------------------------
# accommodation/cars/nssec: NO discovery mechanism -- always the flat
# national-prior modal category, regardless of tenure or anything else.
# ---------------------------------------------------------------------------

def test_accommodation_cars_nssec_are_always_the_national_mode():
    for t in TENURE_LEVELS:
        prior = PublicPriorObservation(customer_id="C1", region="London", tenure=t)
        belief = discover_cohort(prior)
        assert belief.accommodation == max(ACCOMMODATION_PRIOR, key=lambda k: ACCOMMODATION_PRIOR[k])
        assert belief.cars == max(CARS_PRIOR, key=lambda k: CARS_PRIOR[k])
        assert belief.nssec == max(NSSEC_PRIOR, key=lambda k: NSSEC_PRIOR[k])


# ---------------------------------------------------------------------------
# price_sensitivity / channel_pref: discovered via interaction observables;
# None until any evidence exists (C-S1).
# ---------------------------------------------------------------------------

def test_no_interaction_observation_yields_no_price_sensitivity_or_channel_belief():
    prior = PublicPriorObservation(customer_id="C1", region="London")
    belief = discover_cohort(prior, interaction_obs=None)
    assert belief.price_sensitivity is None
    assert belief.channel_pref is None


def test_high_churn_estimate_infers_high_price_sensitivity():
    prior = PublicPriorObservation(customer_id="C1", region="London")
    interaction = InteractionObservation(customer_id="C1", churn_estimate=0.8)
    belief = discover_cohort(prior, interaction)
    assert belief.price_sensitivity == "high"


def test_low_churn_estimate_infers_low_price_sensitivity():
    prior = PublicPriorObservation(customer_id="C1", region="London")
    interaction = InteractionObservation(customer_id="C1", churn_estimate=0.02)
    belief = discover_cohort(prior, interaction)
    assert belief.price_sensitivity == "low"


def test_mid_churn_estimate_infers_medium_price_sensitivity():
    prior = PublicPriorObservation(customer_id="C1", region="London")
    interaction = InteractionObservation(customer_id="C1", churn_estimate=0.3)
    belief = discover_cohort(prior, interaction)
    assert belief.price_sensitivity == "medium"


def test_digital_contact_channels_infer_digital_channel_pref():
    prior = PublicPriorObservation(customer_id="C1", region="London")
    interaction = InteractionObservation(customer_id="C1", contact_channels_used=["app", "web", "app"])
    belief = discover_cohort(prior, interaction)
    assert belief.channel_pref == "digital"


def test_phone_contact_channels_infer_phone_channel_pref():
    prior = PublicPriorObservation(customer_id="C1", region="London")
    interaction = InteractionObservation(customer_id="C1", contact_channels_used=["phone", "phone", "app"])
    belief = discover_cohort(prior, interaction)
    assert belief.channel_pref == "phone"


def test_empty_contact_channels_yields_no_belief():
    prior = PublicPriorObservation(customer_id="C1", region="London")
    interaction = InteractionObservation(customer_id="C1", contact_channels_used=[])
    belief = discover_cohort(prior, interaction)
    assert belief.channel_pref is None


# ---------------------------------------------------------------------------
# believed_book_distribution
# ---------------------------------------------------------------------------

def test_believed_book_distribution_sums_to_one():
    population = [
        discover_cohort(PublicPriorObservation(customer_id=f"C{i}", region="London", tenure=t))
        for i, t in enumerate(["own_outright", "own_mortgage", "private_rent", "social_rent"] * 5)
    ]
    dist = believed_book_distribution("tenure", population, TENURE_LEVELS)
    assert abs(sum(dist.values()) - 1.0) < 1e-9


def test_believed_book_distribution_empty_population_raises():
    with pytest.raises(ValueError):
        believed_book_distribution("tenure", [], TENURE_LEVELS)


def test_believed_book_distribution_none_belief_without_fallback_raises():
    population = [discover_cohort(PublicPriorObservation(customer_id="C1", region="London"))]
    with pytest.raises(ValueError):
        believed_book_distribution("price_sensitivity", population, ("high", "medium", "low"))


def test_believed_book_distribution_none_belief_with_fallback_uses_prior():
    population = [discover_cohort(PublicPriorObservation(customer_id="C1", region="London"))]
    fallback = {"high": 0.3, "medium": 0.45, "low": 0.25}
    dist = believed_book_distribution("price_sensitivity", population, ("high", "medium", "low"),
                                      fallback_prior=fallback)
    assert dist == fallback
