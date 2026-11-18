"""An EPC certificate is never refreshed after an upgrade, so an old one records a WORSE home.

The defect this names (advisor finding 2026-08-09 §2a, director ruling: "the older a certificate is,
the more wrong it is -- not merely the more uncertain"): the register's certificate was built from
the SIM's own insulation, so it could be old but never wrong. Staleness then only widened the
company's error bars and never moved them.

Mutations this must catch: the certificate reading today's fabric (no worse anywhere); a symmetric
error (some certificate better than the home); an age-blind coin (old no worse than fresh).
"""
from __future__ import annotations

import datetime as dt

from simulation import premise_population as ppop
from simulation.household import InsulationLevel

AS_OF = dt.date(2022, 5, 1)
_RANK = {InsulationLevel.POOR: 0, InsulationLevel.PARTIAL: 1, InsulationLevel.FULL: 2}


def _recorded(population):
    rows = []
    for p in population:
        if p.epc_lodged is None:
            continue
        today = p.household.insulation
        recorded = ppop.register_insulation(p.premise_id, today, p.epc_lodged, AS_OF)
        age = (AS_OF - p.epc_lodged).days / 365.25
        rows.append((age, today, recorded))
    return rows


def test_an_old_certificate_is_pessimistic_and_more_so_the_older_it_is():
    rows = _recorded(ppop.draw_premise_population(3000, base_seed=17, as_of=AS_OF))
    worse = [r for r in rows if r[2] != r[1]]
    # The branch CAN be taken before anything is said about what it does.
    assert worse, "no certificate records worse fabric than the home has: the channel is inert"
    # Direction is the whole finding: never better than the home, never more than one step worse.
    assert all(_RANK[today] - _RANK[rec] == 1 for _, today, rec in worse)
    assert all(today != InsulationLevel.POOR for _, today, _ in worse)
    half = ppop.EPC_VALIDITY_YEARS / 2
    old = [r for r in rows if r[0] >= half and r[1] in ppop._ONE_STEP_WORSE]
    fresh = [r for r in rows if r[0] < half and r[1] in ppop._ONE_STEP_WORSE]
    old_share = sum(r[2] != r[1] for r in old) / len(old)
    fresh_share = sum(r[2] != r[1] for r in fresh) / len(fresh)
    assert old_share > fresh_share, (old_share, fresh_share)


def test_the_same_certificate_always_says_the_same_thing_and_a_fresh_one_is_right():
    lodged = dt.date(2013, 6, 1)
    first = ppop.register_insulation("P0001", InsulationLevel.FULL, lodged, AS_OF)
    assert first == ppop.register_insulation("P0001", InsulationLevel.FULL, lodged, AS_OF)
    # Lodged today: no time for an upgrade the register could have missed.
    assert all(
        ppop.register_insulation(f"P{i:04d}", InsulationLevel.FULL, AS_OF, AS_OF)
        == InsulationLevel.FULL
        for i in range(500)
    )
