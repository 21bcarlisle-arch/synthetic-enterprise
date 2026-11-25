"""An offered household is answered on the SAME renewal roll as its full-rate decision, including when
the noise floor re-draws that roll by `setattr` on `simulation.customer_events`.

DEFECT: `retention_offer` (and two `run_phase2b` sites) imported `churn_roll_for_renewal` by name, so
the redraw reached the full-rate decision but not the offer's answer. An offered leaver then got an
independent die: in s.12g's member runs 52 of 88 offered renewals whose roll was above even the
offered P(stay) still renewed (0.59, against the world's own uplift of about 0.02), and every value
arm that offered more was paid for it.
"""
from __future__ import annotations

import ast
from pathlib import Path

import simulation.customer_events as ce
from simulation.retention_offer import answer_retention_offer

REPO = Path(__file__).resolve().parents[2]


def _event(p, kind):
    return {"customer_id": "SYN-2016-241", "event_date": "2017-05-31", "event_type": kind,
            "effective_retention_probability": p, "realized_churn_probability": 1 - p,
            "company_churn_estimate": 0.3, "churn_estimate_error_pct": 0.0, "departure_cause": None}


def test_the_offer_reads_the_patched_roll_and_the_partition_is_reachable(monkeypatch):
    full, offered = _event(0.50, "churned"), _event(0.52, "churned")
    seen = []
    for roll, expect in ((0.99, "churned"), (0.51, "renewed"), (0.10, "renewed")):
        monkeypatch.setattr(ce, "churn_roll_for_renewal", lambda a, d, r=roll: seen.append(a) or r)
        assert answer_retention_offer(full, offered, discount_pct=0.03)["event_type"] == expect, roll
    assert seen == ["SYN-2016-241"] * 3


def test_no_world_module_binds_the_renewal_roll_by_name():
    """The floor patches the module attribute; a top-level by-name import escapes it."""
    bad = []
    for path in (REPO / "simulation").glob("*.py"):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.ImportFrom) and node.module == "simulation.customer_events" and any(
                    a.name == "churn_roll_for_renewal" for a in node.names):
                bad.append(path.name)
    assert bad == [], bad
