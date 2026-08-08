"""JOIN 2 — the physical chain: weather → premise demand → settlement → the book.

Design: `docs/design/JOIN_TEST_TIER.md`. R15 cut-proofs: `test_join_cut_mutation.py`.

Asserts the change propagates end to end AND arrives at the right MAGNITUDE, not
merely that each stage runs. The magnitude clause is the point: a chain whose
middle link has been replaced by a constant still produces a plausible number at
the far end, and only the volume×price identity catches it.

REPORT-ONLY first landing — see JOIN_TEST_TIER.md §3.
"""

import pytest

from tests.system import chains

pytestmark = pytest.mark.join_report_only


def test_the_physical_chain_join_conducts():
    """A colder national temperature reaches the book, at the settled volume ×
    price magnitude."""
    chain = chains.run_physical_chain()
    chains.assert_physical_join(chain)


def test_the_local_temperature_not_the_national_one_drives_the_premise():
    """The W1_5 L2 property, at the join: the premise responds to its OWN local
    weather. A regional deviation must move the premise's demand even with the
    national temperature held fixed — otherwise the regional link is decorative.
    """
    warm_region = chains.run_physical_chain(regional_deviation_c=+3.0)
    cold_region = chains.run_physical_chain(regional_deviation_c=-3.0)
    assert cold_region["cold"]["local_temp_c"] < warm_region["cold"]["local_temp_c"]
    assert cold_region["cold"]["daily_kwh"] > warm_region["cold"]["daily_kwh"], (
        "the regional deviation did not reach the premise: same national temperature, "
        f"same demand ({cold_region['cold']['daily_kwh']:.4f} vs "
        f"{warm_region['cold']['daily_kwh']:.4f} kWh)"
    )


def test_a_warmer_day_does_not_raise_heating_demand():
    """The opposite direction. Without it, 'colder → more demand' passes on any
    chain that simply returns a larger number for the second leg."""
    chain = chains.run_physical_chain()
    assert chain["warm"]["daily_kwh"] <= chain["cold"]["daily_kwh"]
    assert chain["warm"]["wholesale_cost_gbp"] <= chain["cold"]["wholesale_cost_gbp"]


def test_no_wall_crossing_in_the_physical_chain_participants():
    chains.assert_no_wall_crossing(
        ["company/pricing/weather_normalisation_belief.py"]
    )
