"""A household converting off the SVT records a stayed decision on its journey.

Defect this catches: taking the departure roll off an SVT conversion (`1cd4b03dc`) also dropped
the `record_decision` call that sat inside `if event is not None:`, so a converter's journey stayed
wherever `advance()` had put it -- read by `churn_journey_log` as still comparing years after it had
decided to stay.

Mutations, run on a copy and recorded as observed:

  * the call site moved back under `if event is not None:` -> red:
    `test_the_world_records_the_decision_whether_or_not_it_rolled`.
  * `switched` hard-wired False -> red: `..._every_shape_of_renewal_records_its_own_decision`.
  * `switched` hard-wired True -> red: the same control and `..._says_whether_the_world_rolled`.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

from simulation.churn_journey import ChurnJourneyRegister, ChurnJourneyState
from simulation.run_phase2b import _record_renewal_decision

_WORLD = Path(__file__).resolve().parents[2] / "simulation" / "run_phase2b.py"


def _decide(rolled: bool, event: dict | None):
    journey = ChurnJourneyRegister().register_customer("HH-1")
    log: list[dict] = []
    _record_renewal_decision(journey, log, customer_id="HH-1", event_date="2019-03-01",
                             commodity="electricity", rolled=rolled, event=event)
    return journey, log


def test_every_shape_of_renewal_records_its_own_decision():
    # One control over the whole partition: a recorder that always says "stayed" fails the
    # churned leg, one that always says "switched" fails the other two.
    plan = {
        name: (_decide(rolled, event)[0].state, _decide(rolled, event)[1][0]["switched"])
        for name, rolled, event in (
            ("svt_conversion", False, None),
            ("rolled_and_stayed", True, {"event_type": "renewed"}),
            ("rolled_and_left", True, {"event_type": "churned"}),
        )
    }
    assert plan == {
        "svt_conversion": (ChurnJourneyState.STAYED_SVT, False),
        "rolled_and_stayed": (ChurnJourneyState.STAYED_SVT, False),
        "rolled_and_left": (ChurnJourneyState.SWITCHED, True),
    }


def test_the_decision_row_says_whether_the_world_rolled():
    journey, log = _decide(False, None)
    assert log == [{"customer_id": "HH-1", "event_date": "2019-03-01",
                    "commodity": "electricity", "rolled": False, "switched": False}]
    assert journey.decided_at == dt.date(2019, 3, 1)


def test_the_world_records_the_decision_whether_or_not_it_rolled():
    tree = ast.parse(_WORLD.read_text())
    calls: list[list[ast.AST]] = []

    def walk(node, ancestors):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_record_renewal_decision"):
            calls.append(ancestors)
        for child in ast.iter_child_nodes(node):
            walk(child, ancestors + [node])

    walk(tree, [])
    assert len(calls) == 1, "the world must record the renewal decision at exactly one site"
    gating = [a for a in calls[0] if isinstance(a, ast.If)
              and any(isinstance(n, ast.Name) and n.id in {"event", "_rolled"}
                      for n in ast.walk(a.test))]
    assert not gating, "the decision is recorded only when the world rolled, so a conversion is lost"
