"""The gas supply point's charging area (LDZ) crosses the seam, from the home's output area (step 2)."""
import csv
import gzip
import types

import pytest

from company.interfaces.sim_interface import LiveSimInterface, SimInterface, StubSimInterface
from sim.ldz_calorific_value import CHARGING_AREAS, OUTPUT_AREA_LDZ_FILE


def _areas():
    seen = {}
    with gzip.open(OUTPUT_AREA_LDZ_FILE, "rt", newline="") as fh:
        for r in csv.DictReader(fh):
            seen.setdefault(r["ldz"], r["output_area"])
    return seen


def test_the_area_comes_from_the_homes_output_area_not_a_region(monkeypatch):
    by_ldz = _areas()
    homes = {f"H{ldz}": types.SimpleNamespace(output_area=oa) for ldz, oa in by_ldz.items()}
    homes["Hnone"] = types.SimpleNamespace(output_area=None)
    monkeypatch.setattr("simulation.live_population.live_drawn_households", lambda *a, **k: homes)
    sim = LiveSimInterface()
    got = {ldz: sim.get_gas_charging_area(f"H{ldz}") for ldz in by_ldz}
    assert got == {ldz: ldz for ldz in by_ldz}
    # Control over the partition: the published areas AND an independent network both occur.
    assert any(a in CHARGING_AREAS for a in got) and any(a not in CHARGING_AREAS for a in got)
    assert sim.get_gas_charging_area("Hnone") is None


def test_an_unknown_account_is_refused_not_booked_as_no_area(monkeypatch):
    monkeypatch.setattr("simulation.live_population.live_drawn_households", lambda *a, **k: {})
    with pytest.raises(ValueError, match="drew no home"):
        LiveSimInterface().get_gas_charging_area("ghost")


def test_the_base_seam_declares_it_and_the_stub_knows_no_area():
    with pytest.raises(NotImplementedError):
        SimInterface().get_gas_charging_area("x")
    assert StubSimInterface().get_gas_charging_area("x") is None
