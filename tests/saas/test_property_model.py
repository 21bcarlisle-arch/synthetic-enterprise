"""The SUPPLIER's dwelling derivations — `saas.property_model`.

Everything about `build_properties` moved to `tests/simulation/
test_dwelling_records.py` with the builder itself in the 2026-08-18 B12 split
(KNIFE3 step 35). What is left here is the supplier's own reading of a dwelling it
has not observed: the `consumption_band` derivation, the two accessors that must
agree with it, and the meter-fleet record.

These are ALLOWED TO BE WRONG about the world. Nothing in this file compares them
to `simulation.dwelling_records` — that comparison is the coupled triad's score, not
a test's assertion, and a test pinning the two equal is the move B3 and B7 refused.
"""
from saas.customers import CUSTOMERS
from saas.property_model import (
    _SYN_HOME_TYPE_BY_BAND,
    _SYN_PROPERTY_TYPE_BY_BAND,
    _derive_syn_property_fields,
    _epc_rating_of,
    _home_type_of,
)


def _syn_customer(band, cid="SYN-0001"):
    """A SYN acquisition dict (as `to_customer_dict()` renders it): carries
    `consumption_band`, NOT the static `home_type`/`epc_rating`/`bedrooms`."""
    return {
        "customer_id": cid,
        "acquisition_date": "2023-05-01",
        "acquisition_type": "synthetic_draw",
        "segment": "resi",
        "commodity": "electricity",
        "payment_method": "direct_debit",
        "consumption_band": band,
        "eac_kwh": 2500.0,
        "location": {"lat": None, "lon": None, "region": "London"},
        "tariff_type": None,
        "data_regime": "synthetic",
    }


def test_syn_bedrooms_and_type_track_consumption_band():
    for band, expected in (("LOW", (2, "flat")), ("MEDIUM", (3, "semi")), ("HIGH", (4, "detached"))):
        phys = _derive_syn_property_fields(_syn_customer(band))
        assert (phys["bedrooms"], phys["property_type"]) == expected


def test_syn_epc_falls_to_the_modal_band():
    # There is no per-property EPC observable for a drawn customer, so the supplier
    # answers with the UK domestic modal band and labels it an approximation.
    assert _derive_syn_property_fields(_syn_customer("HIGH"))["epc_rating"] == "D"


def test_syn_dict_missing_band_falls_to_honest_defaults():
    c = _syn_customer("MEDIUM", "SYN-NB")
    del c["consumption_band"]
    phys = _derive_syn_property_fields(c)
    assert phys["property_type"] == "semi"
    assert phys["bedrooms"] == 3
    assert phys["epc_rating"] == "D"


def test_the_derivation_is_pure_and_deterministic():
    """C-S2 replay-safety: no RNG, so two calls on equal inputs agree."""
    c = _syn_customer("HIGH", "SYN-DET")
    assert _derive_syn_property_fields(c) == _derive_syn_property_fields(dict(c))


def test_the_two_vocabularies_of_one_derivation_agree():
    """`_home_type_of` answers in the roster's vocabulary and
    `_derive_syn_property_fields` in the property vocabulary. If they drift, a drawn
    customer and its home-move successor describe different dwellings.

    The join runs through the WORLD's home-type map, which is the vocabulary the
    roster is authored in. A TEST may read both sides of the wall; neither module
    may, which is why this assertion lives here and not in either of them.
    """
    from simulation.dwelling_records import PROPERTY_TYPE_BY_HOME_TYPE

    for band in _SYN_PROPERTY_TYPE_BY_BAND:
        assert PROPERTY_TYPE_BY_HOME_TYPE[_SYN_HOME_TYPE_BY_BAND[band]] == \
            _SYN_PROPERTY_TYPE_BY_BAND[band], f"{band}: the two derivations disagree"


def test_the_accessors_are_byte_identical_on_the_static_roster():
    """The authored roster answers for itself; the derivation is for drawn records
    only. A mutant routing static customers through the derivation flips these."""
    for c in CUSTOMERS:
        if "home_type" in c:
            assert _home_type_of(c) == c["home_type"]
        if "epc_rating" in c:
            assert _epc_rating_of(c) == c["epc_rating"]


def test_the_accessors_answer_for_a_drawn_record_too():
    """The vacuity guard for the test above: the accessors must actually have a
    drawn branch, or the byte-identical assertion is about an empty population."""
    c = _syn_customer("LOW", "SYN-ACC")
    assert _home_type_of(c) == "urban_flat"
    assert _epc_rating_of(c) == "D"


def test_the_world_is_not_imported_here():
    """The supplier must not check its own guess against the world's dwelling: that
    would make it right by construction, which is the defect B12 repairs. Parsed,
    not grepped, so a docstring naming the module cannot trip or mute it."""
    import ast
    import pathlib

    src = pathlib.Path("saas/property_model.py").read_text()
    # POPULATION FLOOR (2026-08-27): every assertion sits INSIDE the walk, so an empty
    # population passes silently and the wall goes unguarded. Zero imports means the scan
    # measures nothing -- fix the scan, do not accept the green.
    assert [n for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.Import, ast.ImportFrom))], \
        "this module parsed to ZERO imports -- the wall check below asserts nothing"
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert root not in ("sim", "simulation"), f"saas/property_model.py imports {node.module}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in ("sim", "simulation"), f"saas/property_model.py imports {alias.name}"
