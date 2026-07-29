"""W2_13 — the property record gains a people-count and composition.

`simulation.demand_model` keys both its occupancy responses on `people_count`;
this is the seam that supplies it. The population-level assertions below are
against the published ONS Census 2021 TS017 distribution, not against anything
`property_model` computed (R15).
"""
import pytest

from saas.customers import CUSTOMERS
from saas.property_model import (
    HOUSEHOLD_SIZE_SHARE_ONS_TS017,
    OCCUPANCY_PATTERN_BY_CUSTOMER,
    PEOPLE_COUNT_BY_CUSTOMER,
    _derive_people_count,
    build_properties,
)
from simulation.demand_model import (
    HOUSEHOLD_SIZE_POPULATION_SHARE,
    population_mean_volume_factor,
    volume_factor_is_unbiased,
)


def test_every_property_record_carries_a_people_count_and_children_count():
    properties = build_properties(CUSTOMERS)
    assert properties
    for record in properties.values():
        assert record["people_count"] >= 1
        assert record["children_count"] >= 0
        # The legacy category survives as the coarse shape fallback.
        assert record["occupancy_pattern"] in {"single", "family", "elderly"}


def test_authored_headcounts_are_coherent_with_the_authored_category():
    """A "single" household of four people would be incoherent — the two seed
    estimates must agree with each other."""
    for cid, count in PEOPLE_COUNT_BY_CUSTOMER.items():
        pattern = OCCUPANCY_PATTERN_BY_CUSTOMER[cid]
        if pattern == "single":
            assert count == 1
        elif pattern == "elderly":
            assert count <= 2
        else:  # family
            assert count >= 3


def test_ons_shares_agree_across_the_wall():
    """`property_model` (saas) holds the ONS TS017 shares as a literal because
    it must not import `simulation.*`. This is the guard that the two copies
    have not silently diverged — a divergence would break the volume
    normalisation without any other symptom."""
    assert dict(HOUSEHOLD_SIZE_SHARE_ONS_TS017) == HOUSEHOLD_SIZE_POPULATION_SHARE
    assert sum(s for _, s in HOUSEHOLD_SIZE_SHARE_ONS_TS017) == pytest.approx(1.0)


def test_derived_headcounts_reproduce_the_ons_distribution():
    """Expected values are the published ONS TS017 shares and the published
    mean household size (2.37 persons), not anything derived from the draw."""
    counts = [_derive_people_count(f"ACQ{i}") for i in range(4000)]
    n = len(counts)
    for size, share in HOUSEHOLD_SIZE_SHARE_ONS_TS017:
        assert counts.count(size) / n == pytest.approx(share, abs=0.02)
    # ONS TS017 mean is 2.37; the 5+ band is read as exactly 5 here, so the
    # modelled mean sits marginally below it.
    assert sum(counts) / n == pytest.approx(2.37, abs=0.05)


def test_derivation_is_deterministic_per_customer():
    assert _derive_people_count("ACQ1") == _derive_people_count("ACQ1")
    assert len({_derive_people_count(f"ACQ{i}") for i in range(50)}) > 1


def test_the_generated_population_does_not_shift_aggregate_demand():
    """The mechanism-level claim, measured on the headcounts this module
    actually generates: the occupancy volume factor averages 1.0 over them, so
    switching W2_13 on redistributes demand between households rather than
    re-levelling the book."""
    counts = [_derive_people_count(f"ACQ{i}") for i in range(4000)]
    weights = [1.0] * len(counts)
    for commodity in ("electricity", "gas"):
        mean = population_mean_volume_factor(counts, weights, commodity)
        assert mean == pytest.approx(1.0, abs=0.02)
        assert volume_factor_is_unbiased(counts, weights, commodity)
