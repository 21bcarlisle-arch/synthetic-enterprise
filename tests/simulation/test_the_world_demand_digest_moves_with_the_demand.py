"""The world's DEMAND digest moves under each of the four demand changes of 2026-10-06, and the
home-stock digest moves under none of them.

THE DEFECT. `382545f34` (per-home appliance ownership), `8fe730297` (the boiler's pump and fan),
`53cc04a27` (HES's cooking and laundry season) and `46458b74f`/`a8bf44ef6` (supplementary electric
heating) each changed what a fabric-path home meters, and the world stamp on every run artefact --
departure level plus home stock -- did not move for any of them. Each test below reverts ONE of
those changes in-process and asks whether the world can tell.

The second assertion in each is the reason the demand part exists: the home-stock digest is blind
to every one of these, so a pass of the first assertion cannot have come from the stock part.

R15 -- the mutation that matters: make `home_demand_identity` digest a constant (or drop the
traces from `_demand_vectors`) and every `test_reverting_*` reds; the reproducibility control
stays green, so the reds cannot be noise.
"""

from __future__ import annotations

import pytest

from simulation import premise_trace
from simulation.world_home_identity import home_demand_identity, home_stock_identity


@pytest.fixture(scope="module")
def live():
    return home_demand_identity()["digest"], home_stock_identity()["digest"]


def test_the_demand_digest_is_reproducible(live):
    """Without this, any 'it moved' below could be a non-deterministic probe."""
    assert home_demand_identity()["digest"] == live[0]


def _reverted(monkeypatch, live, name, value):
    monkeypatch.setattr(premise_trace, name, value)
    demand, homes = home_demand_identity()["digest"], home_stock_identity()["digest"]
    assert demand != live[0], (
        "reverting `{}` changed what the probe homes meter and the demand digest did not move, so "
        "a run before that change and one after it read as one world".format(name))
    assert homes == live[1], "the home-stock digest moved too, so the stock part is not blind here"


def test_reverting_382545f34_owned_stock_moves_the_digest(monkeypatch, live):
    _reverted(monkeypatch, live, "owned_stock", lambda *a, **k: premise_trace.FULL_STOCK)


def test_reverting_8fe730297_boiler_pump_and_fan_moves_the_digest(monkeypatch, live):
    _reverted(monkeypatch, live, "boiler_auxiliary_kwh",
              lambda *, space_heat_kwh, **k: [0.0] * len(space_heat_kwh))


def test_reverting_53cc04a27_the_hes_season_moves_the_digest(monkeypatch, live):
    _reverted(monkeypatch, live, "appliance_season_factor", lambda name, month: 1.0)


def test_reverting_46458b74f_supplementary_heating_moves_the_digest(monkeypatch, live):
    _reverted(monkeypatch, live, "has_supplementary_electric_heating", lambda *a, **k: False)


def test_reverting_a8bf44ef6_the_heaters_annual_kwh_moves_the_digest(monkeypatch, live):
    # The value a8bf44ef6 replaced, read from its own subject line.
    _reverted(monkeypatch, live, "SUPPLEMENTARY_ELECTRIC_HEATING_KWH_PER_YEAR", 1505.0)


def test_the_world_identity_carries_the_demand_part(live):
    from simulation.departure_level_anchor import world_level_identity

    assert world_level_identity()["demand"]["digest"] == live[0]
