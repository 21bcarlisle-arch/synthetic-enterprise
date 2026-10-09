"""The P1-P4 grader can say yes. Every real arm graded "offers nothing", and a grader that cannot
offer passes every such run, so the control is over the whole partition: a planted effect that pays
in one group must give P1, P2 and P3, and the same rows with nothing planted must give none.

Rows are synthetic: the grader reads the world's P(stay) off each row, so a planted truth is a
truth it must find, independent of the world's curve.
"""
from __future__ import annotations

import json

import pytest

from tools import grade_acquisition_selection as g

TRAIN, FRESH, NOISE = [1], [2, 3], [4, 5, 6]


def _rows(seed: int, plant: float, n: int = 2400) -> list[dict]:
    rows = []
    for i in range(n):
        ever = i % 2 == 0
        p0 = 0.6
        pt = p0 + (plant if ever else 0.0)
        treated = (i // 2) % 2 == 0
        roll = (i * 0.6180339887 + seed * 0.1) % 1.0
        rows.append({
            "account": f"PROS-{seed}-{i}", "decision_date": "2020-01-01",
            "arm": "treated" if treated else "holdout", "offer_unit_rate": 200.0,
            "stayed": roll <= (pt if treated else p0), "payment_method": "direct_debit",
            "monthly_bills": [70.0 + seed] * 12, "billed_kwh": 2700.0,
            "acquisition_route": "campaign_win", "days_on_default": 0, "ever_actively_renewed": ever,
            "p_stay_holdout": p0, "p_stay_treated": pt, "roll": roll,
        })
    return rows


def _grade(tmp_path, plant: float) -> dict:
    for seed in TRAIN + FRESH + NOISE:
        (tmp_path / f"I_{seed}.json").write_text(json.dumps({"seed": seed, "rows": _rows(seed, plant)}))
    out = g.grade_arm(tmp_path, "I", train_seeds=TRAIN, fresh_seeds=FRESH, noise_seeds=NOISE, cut=7.5)
    return next(r for r in out if r["observable"] == "ever_actively_renewed" and r["margin_share"] == 0.14)


def test_a_planted_effect_that_pays_in_one_group_passes_p1_p2_p3(tmp_path):
    row = _grade(tmp_path, plant=0.30)
    assert row["P1"] and row["P2"] and row["P3"], row
    assert set(row["cut_offered_by_group_on_fresh"]) == {"True"}


def test_the_same_rows_with_nothing_planted_offer_nothing(tmp_path):
    row = _grade(tmp_path, plant=0.0)
    assert not row["P1"] and row["offers_nothing"], row


def test_the_switches_are_set_on_a_copy_never_on_the_directors_file(monkeypatch):
    import simulation.population_draw as pd

    original = pd.ACQUISITION_RESPONSIVENESS_PATH
    before = original.read_text(encoding="utf-8")
    monkeypatch.setattr(pd, "ACQUISITION_RESPONSIVENESS_PATH", original)
    g.set_switches("off")
    assert pd.ACQUISITION_RESPONSIVENESS_PATH != original
    assert json.loads(pd.ACQUISITION_RESPONSIVENESS_PATH.read_text())["activated"]["value"] is False
    assert original.read_text(encoding="utf-8") == before


@pytest.mark.parametrize("arm", sorted(g.ARMS))
def test_every_arm_names_both_switches(arm):
    on, level = g.ARMS[arm]
    assert isinstance(on, bool) and level in ("independent", "linked")
