"""The world's DD failure LEVEL is the register's first-presentation rate, and a returned DD is
re-presented at the register's success share.

Defect it names: `arrears_engine._DD_FAILURE_PROB` was 3%/12%/35% a month, unsourced, and nothing
was cured inside the 28 days (`payment_behaviour_source.REPRESENTATION_SUCCESS_SHARE = None`). The
world's ledger held ~10% of domestic electricity accounts >91 days behind at 2019 quarter ends
against a like-for-like ~5.1% (gb_domestic_bill_payment_failure_and_arrears_prevalence.md s.(e)).

The register-reading controls run in a subprocess with the register path pointed at a copy whose
defaults are changed, so a literal typed to equal today's default cannot pass them.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

from simulation import payment_behaviour_source as pbs
from simulation.meter_reads import ASSUMPTION_TOGGLES_PATH
from simulation.payment_behaviour_source import (
    DIRECT_DEBIT,
    LATER_SETTLEMENT_WITHIN_FIRST_WINDOW_SHARE,
    REPRESENTATION_DAYS_AFTER_DUE,
    REPRESENTATION_SUCCESS_SHARE,
    STANDING_ORDER,
    generate_payment_event,
    later_settlement_date,
)

_REPO = Path(__file__).resolve().parents[2]
_DUE = date(2019, 1, 31)
_PROBE = """
import json, sys
import simulation.meter_reads as m
m.ASSUMPTION_TOGGLES_PATH = __import__("pathlib").Path(sys.argv[1])
import simulation.arrears_engine as a
import simulation.payment_behaviour_source as p
print(json.dumps({"tiers": a._DD_FAILURE_PROB, "share": p.REPRESENTATION_SUCCESS_SHARE}))
"""


def _world_under_register(tmp_path: Path, first: float, share: float) -> dict:
    reg = yaml.safe_load(ASSUMPTION_TOGGLES_PATH.read_text())
    for row in reg["toggles"]:
        if row["id"] == "dd_return_rate_first_presentation":
            row["default"] = first
        if row["id"] == "dd_representation_success_share":
            row["default"] = share
    path = tmp_path / "toggles.yaml"
    path.write_text(yaml.safe_dump(reg))
    out = subprocess.run([sys.executable, "-c", _PROBE, str(path)], cwd=_REPO,
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_the_low_tier_and_the_cure_share_are_read_from_the_register(tmp_path):
    """Move the register's two defaults and the world moves with them; a typed number would not."""
    w = _world_under_register(tmp_path, first=0.0123, share=0.31)
    assert w["tiers"]["LOW"] == pytest.approx(0.0123)
    assert w["share"] == pytest.approx(0.31)


def test_the_tier_ratios_to_low_are_the_old_unsourced_ones_kept(tmp_path):
    """Only the level is sourced: MODERATE stays 4x LOW and HIGH 35/3x LOW, under any level."""
    for first in (0.0057, 0.018):
        t = _world_under_register(tmp_path, first=first, share=0.46)["tiers"]
        assert t["MODERATE"] / t["LOW"] == pytest.approx(0.12 / 0.03)
        assert t["HIGH"] / t["LOW"] == pytest.approx(0.35 / 0.03)


def _failed(n: int, method: str = DIRECT_DEBIT):
    out = []
    for i in range(n):
        ev = generate_payment_event(f"RP-{i}", i, _DUE, 60.0, "high", method)
        if ev.result == "failed":
            out.append(ev)
    return out


def test_a_returned_dd_is_collected_on_re_presentation_at_the_register_share():
    events = _failed(24000)
    assert len(events) > 1500
    cured_on = _DUE + timedelta(days=REPRESENTATION_DAYS_AFTER_DUE)
    cured = sum(1 for e in events if later_settlement_date(e) == cured_on)
    assert 0 < cured < len(events)  # both sides of the branch are reachable
    assert cured / len(events) == pytest.approx(REPRESENTATION_SUCCESS_SHARE, abs=0.03)
    assert REPRESENTATION_DAYS_AFTER_DUE < 28  # inside SLC 14, before the debt is objectionable


def test_only_a_direct_debit_is_re_presented():
    """A standing order or card payment that did not arrive has no mandate to present again."""
    cured_on = _DUE + timedelta(days=REPRESENTATION_DAYS_AFTER_DUE)
    events = _failed(6000, method=STANDING_ORDER)
    assert len(events) > 200
    assert not any(later_settlement_date(e) == cured_on for e in events)


def test_the_cure_is_its_own_draw_and_leaves_every_uncured_bill_as_it_was(monkeypatch):
    """A bill not cured on re-presentation draws exactly the later settlement it drew before
    re-presentation existed, and those draws are independent of the cure (the first-window share
    among the uncured is still Ofgem's, not truncated by a shared uniform)."""
    events = _failed(24000)
    with_cure = [later_settlement_date(e) for e in events]
    monkeypatch.setattr(pbs, "REPRESENTATION_SUCCESS_SHARE", 0.0)
    without = [later_settlement_date(e) for e in events]
    cured_on = _DUE + timedelta(days=REPRESENTATION_DAYS_AFTER_DUE)
    uncured = [(a, b) for a, b in zip(with_cure, without) if a != cured_on]
    assert uncured and all(a == b for a, b in uncured)
    cured_was = [b for a, b in zip(with_cure, without) if a == cured_on]
    early = min(d for d in without if d is not None)
    p_early = (1 - pbs.never_repaid_share(DIRECT_DEBIT)) * LATER_SETTLEMENT_WITHIN_FIRST_WINDOW_SHARE
    for population in (uncured, cured_was):
        dates = [x[1] if isinstance(x, tuple) else x for x in population]
        share_early = sum(1 for d in dates if d == early) / len(dates)
        assert share_early == pytest.approx(p_early, abs=0.05)


def test_a_declared_table_reaches_the_draw_and_none_is_the_worlds():
    """The override is the one door the W2_11 harness uses; absent, the draw is the world's."""
    world = [generate_payment_event(f"OV-{i}", i, _DUE, 60.0, "low", DIRECT_DEBIT) for i in range(400)]
    same = [generate_payment_event(f"OV-{i}", i, _DUE, 60.0, "low", DIRECT_DEBIT,
                                   dd_failure_prob=None) for i in range(400)]
    assert world == same
    forced = [generate_payment_event(f"OV-{i}", i, _DUE, 60.0, "low", DIRECT_DEBIT,
                                     dd_failure_prob={"LOW": 1.0}) for i in range(400)]
    assert all(e.result == "failed" for e in forced)
    assert sum(e.result == "failed" for e in world) < 40


def test_the_w2_11_harness_book_draws_at_its_declared_failure_dense_table():
    """The harness's book is scaffolding at the pre-2026-10-09 tiers, not the world's level: its
    observed failure share sits at the declared table's expectation, far from the world's."""
    from simulation import arrears_engine as ae
    from tools import couple_w2_11_d5 as h

    assert h.HARNESS_BOOK_DD_FAILURE_PROB != ae._DD_FAILURE_PROB
    records, *_ = h.build_scenario(400, seed=7)
    exp = {"harness": 0.0, "world": 0.0}
    n = 0
    for r in records:
        if r.payment_method == "prepayment":
            continue
        tier = h._pick_stress(r.customer_id).upper()
        exp["harness"] += h.HARNESS_BOOK_DD_FAILURE_PROB[tier]
        exp["world"] += ae._DD_FAILURE_PROB[tier]
        n += 1
    observed = sum(1 for r in records if r.result == "failed")
    assert abs(observed - exp["harness"]) < abs(observed - exp["world"])
    assert observed > 2 * exp["world"]
