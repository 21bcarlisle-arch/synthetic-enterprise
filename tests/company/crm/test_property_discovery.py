"""Tests for the C2 discovery-through-interfaces belief layer.

Asserts: (1) beliefs carry source/confidence/as-of, (2) a discovered
attribute reflects the DISCLOSED/OBSERVED value, which may legitimately
differ from any particular ground-truth home, (3) nothing here reads or
imports sim-side ground truth (saas/property_model.py) -- it is built
purely from observable signup/EPC-lookup/tariff-registration events.
"""
import datetime as dt
import inspect

import pytest

from company.crm import property_discovery as pd
from company.crm.property_model import (
    EPCRating, Property, PropertyType, TenureType,
    TRACKED_BELIEF_FIELDS, UNCONFIRMED_DEFAULT_SOURCE,
)


# --- No epistemic-wall leak: this module never imports sim ground truth ---

def test_property_discovery_never_imports_saas_ground_truth():
    src = inspect.getsource(pd)
    assert "saas.property_model" not in src
    assert "saas import" not in src
    assert "import sim" not in src
    assert "import simulation" not in src


# --- Signup disclosure ---

def test_signup_disclosed_attribute_recorded_with_source_and_confidence():
    prop = pd.open_belief_from_signup(
        "UPRN900", dt.date(2024, 3, 1),
        property_type=PropertyType.TERRACED, bedrooms=2,
    )
    assert prop.property_type == PropertyType.TERRACED
    assert prop.source_for("property_type") == pd.SOURCE_SELF_DISCLOSED_SIGNUP
    assert prop.confidence_for("property_type") == pytest.approx(pd.SELF_DISCLOSURE_CONFIDENCE)
    assert prop.as_of_for("property_type") == dt.date(2024, 3, 1)
    assert prop.is_discovered("property_type") is True


def test_signup_undisclosed_attribute_falls_back_to_low_confidence_default():
    # occupants never stated -- must NOT silently claim high confidence
    prop = pd.open_belief_from_signup("UPRN901", dt.date(2024, 3, 1), bedrooms=4)
    assert prop.occupants == pd.DEFAULT_OCCUPANTS
    assert prop.source_for("occupants") == UNCONFIRMED_DEFAULT_SOURCE
    assert prop.confidence_for("occupants") == pytest.approx(pd.DEFAULT_ASSUMPTION_CONFIDENCE)
    assert prop.is_discovered("occupants") is False


def test_signup_never_grants_epc_or_solar_or_ev_knowledge():
    """A customer signing up cannot hand us their EPC rating or reveal solar/EV
    just by disclosing bedrooms/tenure -- those require their own discovery
    events, no matter what else was disclosed at signup."""
    prop = pd.open_belief_from_signup(
        "UPRN902", dt.date(2024, 1, 1),
        property_type=PropertyType.DETACHED, tenure=TenureType.OWNER_OCCUPIED,
        bedrooms=5, occupants=4,
    )
    for field_name in ("epc_rating", "floor_area_m2", "has_solar_pv", "electric_vehicle"):
        assert prop.source_for(field_name) == UNCONFIRMED_DEFAULT_SOURCE
        assert prop.is_discovered(field_name) is False


def test_signup_belief_may_diverge_from_any_real_home():
    """The whole point: this is company BELIEF, not a ground-truth read --
    two different real homes could disclose the same signup facts and get
    the identical (possibly wrong) belief record for their EPC/floor area."""
    prop = pd.open_belief_from_signup("UPRN903", dt.date(2024, 1, 1), bedrooms=3)
    assert prop.epc_rating == pd.DEFAULT_EPC_RATING  # an assumption, not a fact
    assert prop.confidence_for("epc_rating") < 0.5   # low confidence, honestly labelled


# --- EPC certificate lookup ---

def test_epc_lookup_upgrades_confidence_and_source():
    prop = pd.open_belief_from_signup("UPRN910", dt.date(2024, 1, 1))
    assert prop.confidence_for("epc_rating") == pytest.approx(pd.DEFAULT_ASSUMPTION_CONFIDENCE)
    looked_up = pd.apply_epc_lookup(prop, EPCRating.B, dt.date(2024, 2, 15))
    assert looked_up.epc_rating == EPCRating.B
    assert looked_up.source_for("epc_rating") == pd.SOURCE_EPC_CERTIFICATE_LOOKUP
    assert looked_up.confidence_for("epc_rating") == pytest.approx(pd.EPC_LOOKUP_CONFIDENCE)
    assert looked_up.as_of_for("epc_rating") == dt.date(2024, 2, 15)
    # other attributes' provenance is untouched by an EPC-only event
    assert looked_up.source_for("bedrooms") == prop.source_for("bedrooms")


def test_epc_lookup_does_not_mutate_original_property():
    prop = pd.open_belief_from_signup("UPRN911", dt.date(2024, 1, 1))
    pd.apply_epc_lookup(prop, EPCRating.A, dt.date(2024, 2, 1))
    assert prop.epc_rating == pd.DEFAULT_EPC_RATING  # frozen, unaffected


# --- Tariff registration ---

def test_tariff_registration_records_solar_and_ev():
    prop = pd.open_belief_from_signup("UPRN920", dt.date(2024, 1, 1))
    updated = pd.apply_tariff_registration(
        prop, dt.date(2024, 4, 1), has_solar_pv=True, electric_vehicle=True,
    )
    assert updated.has_solar_pv is True
    assert updated.electric_vehicle is True
    assert updated.source_for("has_solar_pv") == pd.SOURCE_TARIFF_REGISTRATION
    assert updated.source_for("electric_vehicle") == pd.SOURCE_TARIFF_REGISTRATION
    assert updated.confidence_for("has_solar_pv") == pytest.approx(pd.TARIFF_REGISTRATION_CONFIDENCE)


def test_tariff_registration_partial_update_leaves_other_attribute_untouched():
    prop = pd.open_belief_from_signup("UPRN921", dt.date(2024, 1, 1))
    updated = pd.apply_tariff_registration(prop, dt.date(2024, 4, 1), has_solar_pv=True)
    assert updated.has_solar_pv is True
    assert updated.electric_vehicle is False
    assert updated.source_for("electric_vehicle") == UNCONFIRMED_DEFAULT_SOURCE


def test_tariff_registration_no_kwargs_is_a_noop():
    prop = pd.open_belief_from_signup("UPRN922", dt.date(2024, 1, 1))
    updated = pd.apply_tariff_registration(prop, dt.date(2024, 4, 1))
    assert updated is prop


# --- Engineer visit ---

def test_engineer_visit_corrects_floor_area_and_occupants():
    prop = pd.open_belief_from_signup("UPRN930", dt.date(2024, 1, 1), occupants=2)
    visited = pd.apply_engineer_visit(
        prop, dt.date(2024, 6, 1), floor_area_m2=112.0, occupants=3,
    )
    assert visited.floor_area_m2 == pytest.approx(112.0)
    assert visited.occupants == 3
    assert visited.source_for("floor_area_m2") == pd.SOURCE_ENGINEER_VISIT
    assert visited.source_for("occupants") == pd.SOURCE_ENGINEER_VISIT
    assert visited.confidence_for("floor_area_m2") == pytest.approx(pd.ENGINEER_VISIT_CONFIDENCE)


# --- Overall confidence gauge ---

def test_overall_confidence_rises_as_more_is_discovered():
    prop = pd.open_belief_from_signup("UPRN940", dt.date(2024, 1, 1), bedrooms=3)
    baseline = prop.overall_confidence
    after_epc = pd.apply_epc_lookup(prop, EPCRating.C, dt.date(2024, 2, 1))
    assert after_epc.overall_confidence > baseline
    after_all = pd.apply_engineer_visit(
        pd.apply_tariff_registration(after_epc, dt.date(2024, 3, 1), has_solar_pv=True, electric_vehicle=False),
        dt.date(2024, 4, 1), floor_area_m2=95.0,
    )
    assert after_all.overall_confidence > after_epc.overall_confidence


def test_overall_confidence_never_exceeds_one_or_drops_below_zero():
    prop = pd.open_belief_from_signup("UPRN941", dt.date(2024, 1, 1))
    assert 0.0 <= prop.overall_confidence <= 1.0
    full = pd.apply_engineer_visit(
        pd.apply_tariff_registration(
            pd.apply_epc_lookup(prop, EPCRating.A, dt.date(2024, 1, 2)),
            dt.date(2024, 1, 3), has_solar_pv=True, electric_vehicle=True,
        ),
        dt.date(2024, 1, 4), floor_area_m2=100.0, bedrooms=4, occupants=2,
    )
    assert 0.0 <= full.overall_confidence <= 1.0


def test_tracked_belief_fields_all_have_provenance_after_full_discovery():
    prop = pd.open_belief_from_signup(
        "UPRN950", dt.date(2024, 1, 1),
        property_type=PropertyType.FLAT, tenure=TenureType.PRIVATE_RENTED,
        bedrooms=1, occupants=1,
    )
    prop = pd.apply_epc_lookup(prop, EPCRating.E, dt.date(2024, 1, 5))
    prop = pd.apply_tariff_registration(prop, dt.date(2024, 1, 10), has_solar_pv=False, electric_vehicle=True)
    prop = pd.apply_engineer_visit(prop, dt.date(2024, 1, 15), floor_area_m2=48.0)
    for field_name in TRACKED_BELIEF_FIELDS:
        assert prop.is_discovered(field_name), f"{field_name} should be discovered"
