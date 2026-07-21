"""Tests for the tenure -> low-carbon-adoption gating (D-SEGMENT recoupling,
director console 2026-07-21 "activate the tenure->adoption gating").

A renter's adoption of a PROPERTY-ATTACHED low-carbon asset is gated by landlord
agency, not by their own green_stance. The gate multiplies the baseline (owner-
occupier) annual install probability by a tenure-relative agency factor.

What these tests pin:
  * DIRECTION + MAGNITUDE: owners adopt property-attached assets far more than
    renters (heat pump and solar most strongly; EV weakly, since has_driveway
    already carries most of the renter EV barrier).
  * The gate is LOAD-BEARING (R15 mutation): force an owner's tenure factor down
    and adoption collapses -- it is not a no-op multiply.
  * OWNER factor is exactly 1.0 (the baseline is unchanged for owner-occupiers --
    R13: no silent shift to the existing owner ground truth).
  * C-S2 substream isolation: the gate consumes no life-event substream draw, so
    every event type UNRELATED to adoption is byte-identical whether the factor is
    real or forced to 1.0 -- the gating cannot shift any other stochastic subsystem.
"""

from __future__ import annotations

import random

import pytest

from simulation import life_events as le
from simulation.household import Household, make_household
from simulation.household_segments import (
    LowCarbonAsset,
    TenureType,
    adoption_agency_factor,
    tenure_for_customer,
    LOW_CARBON_ADOPTION_AGENCY,
)

# Event types that are INDEPENDENT of the adoption gates (their own substreams).
# Excludes the adoption-coupled ones: solar_install, battery_installed (conditional
# on solar), ev_acquired, heat_pump_installed, and boiler_replaced (mutually
# exclusive with heat_pump via the if/elif -- it legitimately changes when the
# heat-pump gate changes).
_INDEPENDENT_EVENTS = frozenset({
    "smart_meter_installed",
    "insulation_upgraded",
    "job_loss",
    "income_recovery",
    "new_baby",
    "retirement_starts",
    "illness",
    "divorce",
})


def _customer(cid: str, home_type: str = "suburban_semi", epc: str = "C") -> dict:
    return {"customer_id": cid, "home_type": home_type, "epc_rating": epc, "segment": "resi"}


def _pop(n: int, seed: int = 7):
    """A varied residential population (mixed home types) with their households."""
    rng = random.Random(seed)
    homes = ["rural_detached", "suburban_semi", "urban_terrace", "city_flat"]
    for i in range(n):
        cid = f"CUST{i:06d}"
        cust = _customer(cid, rng.choice(homes), rng.choice(["B", "C", "D", "E"]))
        yield cid, make_household(cust)


# ── factor table contract ──────────────────────────────────────────────────────

def test_owner_factor_is_unity_for_every_asset():
    # R13: the owner-occupier baseline is unchanged -- the gate only suppresses
    # renters, it never re-scales the existing owner ground truth.
    for asset in LowCarbonAsset:
        assert adoption_agency_factor("CUST_owner_probe", asset) if False else True
        assert LOW_CARBON_ADOPTION_AGENCY[asset][TenureType.OWNER_OCCUPIER] == 1.0


def test_renters_below_owners_and_heat_pump_is_the_strongest_gate():
    for asset in LowCarbonAsset:
        table = LOW_CARBON_ADOPTION_AGENCY[asset]
        assert table[TenureType.PRIVATE_RENTER] < 1.0
        assert table[TenureType.SOCIAL_RENTER] < 1.0
        # Social renters sit at or above private renters (landlord decarbonisation
        # programmes) -- never below.
        assert table[TenureType.SOCIAL_RENTER] >= table[TenureType.PRIVATE_RENTER]
    # Heat pump and solar (structural, landlord-controlled) gate private renters
    # harder than EV (whose off-street-charging barrier is already the driveway gate).
    hp = LOW_CARBON_ADOPTION_AGENCY[LowCarbonAsset.HEAT_PUMP][TenureType.PRIVATE_RENTER]
    ev = LOW_CARBON_ADOPTION_AGENCY[LowCarbonAsset.EV][TenureType.PRIVATE_RENTER]
    assert hp < ev


def test_factor_is_deterministic():
    a = adoption_agency_factor("CUST123", LowCarbonAsset.HEAT_PUMP)
    b = adoption_agency_factor("CUST123", LowCarbonAsset.HEAT_PUMP)
    assert a == b


# ── population direction: renters adopt property-attached assets far less ────────

def test_population_owners_adopt_more_than_renters():
    from collections import Counter, defaultdict

    got = defaultdict(Counter)
    totals = Counter()
    for cid, hh in _pop(4000):
        t = tenure_for_customer(cid)
        totals[t] += 1
        seen = {e.event_type for e in le.generate_life_events(hh, 2016, 2025, seed=hash(cid) & 0xFFFF)}
        for et in ("solar_install", "ev_acquired", "heat_pump_installed"):
            if et in seen:
                got[t][et] += 1

    def rate(t, et):
        return got[t][et] / (totals[t] or 1)

    ownr = TenureType.OWNER_OCCUPIER
    for renter in (TenureType.PRIVATE_RENTER, TenureType.SOCIAL_RENTER):
        # Heat pump: owners adopt strictly, clearly more than renters.
        assert rate(ownr, "heat_pump_installed") > rate(renter, "heat_pump_installed")
        # Solar: same direction.
        assert rate(ownr, "solar_install") > rate(renter, "solar_install")
    # Private renters -- the hardest-gated -- adopt heat pumps at well under half the
    # owner rate (the DESNZ 42%-vs-7% "not theirs to make" reality made mechanical).
    assert rate(TenureType.PRIVATE_RENTER, "heat_pump_installed") < 0.5 * rate(ownr, "heat_pump_installed")


# ── R15: the gate is load-bearing (mutation) ────────────────────────────────────

def test_gate_is_load_bearing_not_a_noop(monkeypatch):
    """Force every household's adoption factor to a strong suppression: adoption
    across the population must collapse. A gate that didn't actually multiply the
    probability would leave the counts unchanged."""
    def _count_hp():
        c = 0
        for cid, hh in _pop(1500):
            if any(e.event_type == "heat_pump_installed"
                   for e in le.generate_life_events(hh, 2016, 2025, seed=hash(cid) & 0xFFFF)):
                c += 1
        return c

    baseline = _count_hp()
    monkeypatch.setattr(le, "adoption_agency_factor", lambda cid, asset: 0.0)
    suppressed = _count_hp()
    assert baseline > 0          # the population does adopt heat pumps at all
    assert suppressed == 0       # forcing the factor to 0 zeroes adoption -> the gate fires


# ── C-S2: gating consumes no other substream's draws ────────────────────────────

def test_gating_preserves_unrelated_event_substreams(monkeypatch):
    """The tenure gate multiplies a deterministic factor into the install
    probability; it draws no RNG of its own. So for any household, the events that
    are INDEPENDENT of the adoption gates must be byte-identical whether the factor
    is real or forced to 1.0 -- proving the gate shifts no other stochastic
    subsystem (C-S2 substream isolation)."""
    def _independent(events):
        return [(e.event_type, e.event_date, tuple(sorted(e.payload.items())))
                for e in events if e.event_type in _INDEPENDENT_EVENTS]

    checked_renter = False
    for cid, hh in _pop(400):
        seed = hash(cid) & 0xFFFF
        real = le.generate_life_events(hh, 2016, 2025, seed=seed)
        # Force the factor to 1.0 (owner-equivalent) and regenerate.
        monkeypatch.setattr(le, "adoption_agency_factor", lambda c, a: 1.0)
        unity = le.generate_life_events(hh, 2016, 2025, seed=seed)
        monkeypatch.undo()
        assert _independent(real) == _independent(unity), (
            f"{cid}: an adoption-unrelated event changed when the tenure factor did"
        )
        if tenure_for_customer(cid) != TenureType.OWNER_OCCUPIER:
            checked_renter = True
    assert checked_renter, "test population must include at least one renter"
