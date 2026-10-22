"""A storage-heated home is registered on Profile Class 2, from the household the world drew.

In 2016-2025 a domestic meter with an off-peak register was PC2 ("Domestic Economy 7"); the class
followed the meter (docs/data-sources/profile-class-2.md). Until 2026-10-22 every domestic home in
the run was PC1, so a storage-heated home on the legacy path was settled on a daytime shape.
"""

import ast
import inspect
from types import SimpleNamespace

import pytest

import simulation.run_phase2b as run_phase2b
from simulation.household import HeatingSystem
from simulation.run_phase2b import (
    SHAPE_LOADERS,
    _base_profile_eac,
    registered_profile_class,
)


class _Register:
    def __init__(self, heating):
        self.heating = heating
        self.asked = []

    def household_at_date(self, cid, as_of):
        self.asked.append((cid, as_of))
        return None if self.heating is None else SimpleNamespace(heating_system=self.heating)


def _pc(heating, roster=None):
    customer = {"customer_id": "SYN-1"}
    if roster is not None:
        customer["profile_class"] = roster
    return registered_profile_class(customer, _Register(heating), "2019-04-01")


def test_both_classes_are_reachable_from_the_rule():
    """The control over the whole partition, asserted before what either branch does."""
    got = {_pc(h) for h in HeatingSystem}
    assert got == {1, 2}


@pytest.mark.parametrize("heating", [h for h in HeatingSystem if h != HeatingSystem.ELECTRIC_STORAGE])
def test_only_storage_heating_moves_a_home_off_pc1(heating):
    """Direct-electric and heat-pump homes on E7 are a GAP (G3), held at PC1 rather than guessed."""
    assert _pc(heating) == 1


def test_a_storage_heated_home_is_pc2():
    assert _pc(HeatingSystem.ELECTRIC_STORAGE) == 2


def test_a_home_with_no_drawn_household_keeps_the_roster_class():
    assert _pc(None) == 1


def test_a_non_domestic_class_is_never_overwritten():
    """An SME on PC3 with storage heating would be PC4, which the tree has no table for."""
    assert _pc(HeatingSystem.ELECTRIC_STORAGE, roster=3) == 3


def test_the_household_is_read_at_the_date_supply_starts():
    register = _Register(HeatingSystem.ELECTRIC_STORAGE)
    registered_profile_class({"customer_id": "SYN-9"}, register, "2021-02-03")
    assert register.asked == [("SYN-9", "2021-02-03")]


def test_a_pc2_home_has_a_table_and_is_levelled_to_its_own_eac():
    assert len(SHAPE_LOADERS[2]("2019-01-07")) == 48
    assert _base_profile_eac({"profile_class": 2, "eac_kwh": 6_000}) == 6_000.0


def test_no_legacy_shape_in_the_run_reads_the_roster_class_directly():
    """Both `_weather_adjusted_shape_fn` sites -- the book and W1_11's legacy counterfactual --
    must index SHAPE_LOADERS through the registration rule. A site reading
    `customer.get("profile_class")` puts a storage-heated home back on PC1, and nothing else
    would notice: the book still settles, at a daytime shape."""
    src = inspect.getsource(run_phase2b)
    tree = ast.parse(src)
    indexed = [n for n in ast.walk(tree)
               if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
               and n.value.id == "SHAPE_LOADERS"]
    assert len(indexed) >= 2
    for node in indexed:
        key = node.slice
        reads_rule = any(isinstance(n, ast.Name) and n.id in ("profile_class", "registered_profile_class")
                         for n in ast.walk(key))
        assert reads_rule, f"SHAPE_LOADERS indexed at line {node.lineno} without the registration rule"
    assert src.count("profile_class = registered_profile_class(") == 1
