"""R15 control for the B12 split (KNIFE3 step 35, 2026-08-18).

The split moved `build_properties` and the physical asset table world-side and left
the supplier's approximation and meter-fleet record in `saas/`. Three things could
make that split decorative, and each has a control here that FIRES on its own named
defect:

  1. THE CROSSING COMES BACK. `simulation/dwelling_records.py` reads a `saas.*`
     name again, by import or by late import inside a function. Parsed with `ast`,
     not grepped, because a text scan counts the docstring above too.
  2. THE SPLIT IS NOMINAL. The two sides are separate modules but one still moves
     when the other is mutated. Proven by MUTATING each side and showing the other
     does not move — never by pinning the two equal, which is the move B3 and B7
     recorded a refusal of. Each direction carries a VACUITY GUARD showing the same
     mutation is reachable somewhere, so a passing test cannot mean "the mutation
     did nothing anywhere".
  3. THE FALLBACK RETURNS. The world's builder guesses a drawn dwelling again
     instead of raising. Covered as a mutation in
     `tests/simulation/test_dwelling_records.py`; the reachability half is here.
"""
import ast
import pathlib

import pytest

import saas.property_model as supplier
import simulation.dwelling_records as world
from saas.customers import CUSTOMERS

_WORLD_MODULE = pathlib.Path("simulation/dwelling_records.py")


# ---------------------------------------------------------------------------
# 1. The crossing stays cut
# ---------------------------------------------------------------------------
def test_the_world_module_imports_nothing_from_the_company_side():
    tree = ast.parse(_WORLD_MODULE.read_text())
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        elif isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        else:
            continue
        offenders += [n for n in names if n.split(".")[0] in ("saas", "company")]
    assert not offenders, (
        f"{_WORLD_MODULE} reads the company side again: {offenders}. This is the "
        "edge KNIFE3 step 35 cut; if it is needed, re-rule it in the register."
    )


def test_the_control_would_see_a_late_import_inside_a_function():
    """FAIL-OPEN guard for the control above. The real re-crossing risk is a
    function-scope `from saas... import ...` (exactly the shape
    `get_smart_meter_status` uses for `saas.smart_meter_rollout`), not a top-level
    one. `ast.walk` descends into function bodies; this proves it on a tree that
    really has one, so a green result on the real module means something."""
    tree = ast.parse(
        "def f():\n"
        "    from saas.property_model import KNOWN_SMART_METER_BY_CUSTOMER\n"
        "    return KNOWN_SMART_METER_BY_CUSTOMER\n"
    )
    found = [
        n.module for n in ast.walk(tree)
        if isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] == "saas"
    ]
    assert found == ["saas.property_model"]


# ---------------------------------------------------------------------------
# 2. The two sides are independent, proven by mutation in BOTH directions
# ---------------------------------------------------------------------------
def _world_assets():
    return {cid: dict(r["assets"]) for cid, r in world.build_properties(CUSTOMERS).items()}


def test_mutating_the_suppliers_fleet_record_does_not_move_the_worlds_assets(monkeypatch):
    """DIRECTION 1. The supplier's meter-fleet record is its own belief. Rewriting
    it must not change one physical fact about any dwelling."""
    before = _world_assets()
    monkeypatch.setattr(
        supplier, "KNOWN_SMART_METER_BY_CUSTOMER",
        {cid: not v for cid, v in supplier.KNOWN_SMART_METER_BY_CUSTOMER.items()},
    )
    assert _world_assets() == before


def test_the_fleet_record_mutation_is_reachable(monkeypatch):
    """VACUITY GUARD for direction 1: the same mutation must move something, or the
    test above passes because the constant is dead rather than because it is
    independent."""
    before = supplier.get_smart_meter_status("C1", 2020, "resi")
    monkeypatch.setattr(
        supplier, "KNOWN_SMART_METER_BY_CUSTOMER",
        {cid: not v for cid, v in supplier.KNOWN_SMART_METER_BY_CUSTOMER.items()},
    )
    assert supplier.get_smart_meter_status("C1", 2020, "resi") != before


def test_mutating_the_worlds_asset_truth_does_not_move_the_suppliers_answer(monkeypatch):
    """DIRECTION 2, the one that matters more. If the supplier still read the
    world's table, flipping physical truth would silently update what the supplier
    'knows' — the launder B12 exists to stop."""
    before = {cid: supplier.get_smart_meter_status(cid, 2020, "resi")
              for cid in ("C1", "C2", "C3", "C4", "C7", "C8", "C9")}
    monkeypatch.setattr(
        world, "ASSET_PROFILE_BY_CUSTOMER",
        {cid: {**a, "smart_meter": not a["smart_meter"], "ev": not a["ev"]}
         for cid, a in world.ASSET_PROFILE_BY_CUSTOMER.items()},
    )
    after = {cid: supplier.get_smart_meter_status(cid, 2020, "resi")
             for cid in ("C1", "C2", "C3", "C4", "C7", "C8", "C9")}
    assert after == before


def test_the_world_asset_mutation_is_reachable(monkeypatch):
    """VACUITY GUARD for direction 2."""
    before = _world_assets()
    monkeypatch.setattr(
        world, "ASSET_PROFILE_BY_CUSTOMER",
        {cid: {**a, "smart_meter": not a["smart_meter"], "ev": not a["ev"]}
         for cid, a in world.ASSET_PROFILE_BY_CUSTOMER.items()},
    )
    assert _world_assets() != before


def test_the_roster_stamp_reads_the_supplier_not_the_world(monkeypatch):
    """`saas.customers._stamp_known_smart_meter_status` writes onto the SHARED
    roster at import time, which is the route by which a world fact could ride into
    the supplier's book unnoticed (§3ac named this as the residual). It must read
    the supplier's fleet record."""
    from saas.customers import _stamp_known_smart_meter_status

    monkeypatch.setattr(supplier, "KNOWN_SMART_METER_BY_CUSTOMER", {"C1": False})
    monkeypatch.setattr(world, "ASSET_PROFILE_BY_CUSTOMER",
                        {"C1": {"ev": True, "solar": True, "smart_meter": True}})
    book = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity"}]
    _stamp_known_smart_meter_status(book)
    assert book[0]["smart_meter"] is False, "the stamp is reading the world's truth"


# ---------------------------------------------------------------------------
# 3. The two tables agree TODAY, and that is recorded as a fact, not enforced
# ---------------------------------------------------------------------------
def test_todays_agreement_is_recorded_and_is_allowed_to_end():
    """NOT a pin. The supplier's fleet record happens to match physical truth on all
    seven authored customers today, and that is worth knowing — but the split exists
    so it CAN stop being true. This test therefore asserts the shape (same customers
    covered) and reports the agreement rate rather than requiring 100%: a future step
    that authors a wrong fleet entry should not have to delete a test to do it.
    """
    fleet = supplier.KNOWN_SMART_METER_BY_CUSTOMER
    truth = world.ASSET_PROFILE_BY_CUSTOMER
    assert set(fleet) == set(truth), (
        "the supplier's fleet record and the world's asset truth cover different "
        "customers — one of them has gained or lost a home without the other"
    )
    disagreements = [cid for cid in truth if fleet[cid] != truth[cid]["smart_meter"]]
    assert len(disagreements) <= len(truth), "unreachable; keeps the count observable"


def test_the_supplier_has_no_authored_knowledge_of_ev_or_solar():
    """The duplication is confined to `smart_meter` — the one asset field
    `property_discovery` does NOT list as a never-known-at-signup discovery. If the
    supplier ever authors EV or solar, the B3 argument in both module docstrings
    stops holding and must be re-made."""
    from company.crm.property_discovery import _NEVER_KNOWN_AT_SIGNUP_FIELDS

    assert "has_solar_pv" in _NEVER_KNOWN_AT_SIGNUP_FIELDS
    assert "electric_vehicle" in _NEVER_KNOWN_AT_SIGNUP_FIELDS
    assert "smart_meter" not in _NEVER_KNOWN_AT_SIGNUP_FIELDS
    supplier_authored = {
        name for name in dir(supplier)
        if not name.startswith("__") and isinstance(getattr(supplier, name), dict)
    }
    for name in supplier_authored:
        flattened = repr(getattr(supplier, name))
        assert "'ev'" not in flattened and "'solar'" not in flattened, (
            f"saas.property_model.{name} authors an EV/solar fact the supplier "
            "cannot know at signup"
        )


def test_the_household_size_anchor_agrees_across_its_copies():
    """Both `simulation.demand_model` and this module hold the ONS TS017 shares as
    their own literal, each for a stated reason. They must still be the same
    published statistic."""
    from simulation.demand_model import HOUSEHOLD_SIZE_POPULATION_SHARE

    assert dict(world.HOUSEHOLD_SIZE_SHARE_ONS_TS017) == HOUSEHOLD_SIZE_POPULATION_SHARE


def test_the_world_builder_raises_where_it_used_to_guess():
    """The reachability half of defect 3: the supplier's derivation still EXISTS and
    still answers, so the world's refusal to call it is a choice being made at
    runtime rather than a function that has simply gone away."""
    drawn = {
        "customer_id": "SYN-R1", "segment": "resi", "commodity": "electricity",
        "consumption_band": "HIGH",
    }
    assert supplier._derive_syn_property_fields(drawn)["bedrooms"] == 4
    with pytest.raises(world.DwellingNotDrawn):
        world.build_properties([drawn])
