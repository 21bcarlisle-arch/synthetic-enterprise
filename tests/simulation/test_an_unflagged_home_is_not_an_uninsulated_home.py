"""NEED's LI_FLAG / CWI_FLAG record a SCHEME install, so a missing flag is not a missing measure.

The world read "neither flag" as POOR and drew 72% of homes POOR. The property this keys to is a
published bound, not today's share: a home with NEITHER measure present cannot be commoner than a
loft below 125 mm, which is 1 - HEE's 67% = 33% of lofted homes. The must-fail arm is the
flag-only reading on the SAME draws (each household keeps its flags in `has_*_insulation`), so the
test reds if the flags are ever read as presence again.
Note: docs/market_research/wall_insulation_by_dwelling_age_ehs_2023_2026-11-13.md.
"""
from __future__ import annotations

import datetime as dt
import math

import pytest

from simulation import premise_population as pp
from simulation.household import InsulationLevel

N = 2000


@pytest.fixture(scope="module")
def drawn():
    return [pp.draw_premise_from_joint(f"INS{i}", base_seed=42, as_of=dt.date(2020, 1, 1)).household
            for i in range(N)]


def test_homes_with_neither_measure_stay_under_the_published_loft_bound(drawn):
    bound = 1.0 - pp.HEE_LOFT_INSULATED_SHARE
    slack = 3 * math.sqrt(bound * (1 - bound) / N)
    poor = sum(h.insulation is InsulationLevel.POOR for h in drawn) / N
    flag_only_poor = sum(not h.has_loft_insulation and not h.has_cavity_wall_insulation
                         for h in drawn) / N
    assert flag_only_poor > bound + slack, "the must-fail arm no longer fails: flags changed meaning"
    assert poor <= bound + slack, f"POOR {poor:.3f} exceeds the published bound {bound:.2f}"


def test_every_insulation_level_is_reachable_and_a_drawn_measure_can_be_present(drawn):
    levels = {h.insulation for h in drawn}
    assert levels == {InsulationLevel.POOR, InsulationLevel.PARTIAL, InsulationLevel.FULL}
    # A home with no scheme flag can still be FULL: the drawn-present branch is taken.
    assert any(h.insulation is InsulationLevel.FULL
               and not h.has_loft_insulation and not h.has_cavity_wall_insulation for h in drawn)


def test_the_presence_rates_reproduce_the_published_shares_and_refuse_a_contradiction(monkeypatch):
    rates = pp.insulation_presence_rates()
    assert 0.0 < rates["loft"] < 1.0
    assert set(rates["wall"]) == set(pp.EHS_WALLS_INSULATED_000S)
    assert all(0.0 < q < 1.0 for q in rates["wall"].values())
    # Older walls are less insulated than newer, as EHS publishes (21.7% / 68.0% / 89.2%).
    w = rates["wall"]
    assert w["pre_1945"] < w["1945_2012"] < w["post_2012"]
    pp.insulation_presence_rates.cache_clear()
    monkeypatch.setattr(pp, "HEE_LOFT_INSULATED_SHARE", 0.01)
    try:
        with pytest.raises(ValueError, match="loft: scheme flags"):
            pp.insulation_presence_rates()
    finally:
        pp.insulation_presence_rates.cache_clear()
