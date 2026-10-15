"""A hold is re-asked each stretch: a held row naming an atom that has reached target is listed.

Defect it names (`a-hold-condition-is-not-reasked-when-its-premise-moves`, 41 listings): C29's
block_reason said "sequenced behind B10" for five weeks after B10 reached its target, and the stale
hold kept PB4 off L3 until a hand fix.
"""
from __future__ import annotations

import ast
import inspect

from background import delivery_seat
from background.stale_holds import stale_holds


def _atom(aid, cur, tgt, **extra):
    return dict(id=aid, level_current=cur, level_target=tgt, **extra)


def test_the_c29_instance_and_the_whole_partition():
    """Fires on: met inverted or dropped (the done premise is not listed, or the open one is);
    short ids unresolved ("B10" names nothing); closed atoms ignored; an unheld row listed."""
    held = _atom("C29_decisions_stop_being_lookup_tables", 1, 3,
                 block_reason="sequenced behind B10 until its replay lands")
    done = _atom("B10_the_replay", 3, 3)
    other = _atom("Q1_unheld", 0, 2)
    rows = stale_holds([held, done, other], [])
    assert [r["atom"] for r in rows] == ["C29_decisions_stop_being_lookup_tables"]
    assert rows[0]["met"] == ["B10_the_replay"]
    assert "sequenced behind B10" in rows[0]["where"]["B10_the_replay"]
    assert stale_holds([held, _atom("B10_the_replay", 2, 3), other], []) == []   # premise open
    on_closed = _atom("X1_waits", 0, 2, blocked_on=["Z9_the_finished_one"])
    rows = stale_holds([on_closed], [_atom("Z9_the_finished_one", 2, 2)])
    assert rows and rows[0]["where"]["Z9_the_finished_one"] == "blocked_on"


def test_the_seat_brief_carries_the_stale_holds():
    """Fires on: the reading built but no brief carrying it -- a rule with no production caller."""
    tree = ast.parse(inspect.getsource(delivery_seat.build_brief))
    keys = {k.value for n in ast.walk(tree) if isinstance(n, ast.Dict)
            for k in n.keys if isinstance(k, ast.Constant)}
    assert "stale_holds" in keys
