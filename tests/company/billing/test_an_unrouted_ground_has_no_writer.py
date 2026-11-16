"""A protection ground the gate reads but no company path writes is listed as unrouted, with its
reason (C32 tenth pass, class 2; commons s.5, "The own-hold column is unrouted").

The own-hold column was COVERED on three live rows. On every row it could refuse in a unit test and
never live, because nothing places a hold. Defects these name:
- a writer built later while the column still says unrouted;
- the column taken off the unrouted list with no writer, so the table reads as live again;
- a writer scan that cannot find a writer (the derivation leg);
- a live route that drops the hold it is handed, which the in-operation partition catches.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

from company.billing.collections_journey import CollectionsJourneyDesk
from company.billing.winter_moratorium import (
    OWN_HOLD,
    PROTECTION_GROUNDS,
    UNROUTED_GROUNDS,
    MoratoriumRecord,
    MoratoriumType,
    WinterMoratoriumRegister,
)
from company.crm.account_hierarchy import Segment
from company.market.transfer_objection_register import (
    TransferObjectionRegister,
    decide_debt_objection,
)
from simulation.payment_method_dynamics import meter_recoveries

ROOT = Path(__file__).resolve().parents[3]
HOME = ROOT / "company/billing/winter_moratorium.py"

#: Ground -> the constructor a writer of its input calls. A ground is routed iff company code
#: outside the gate's own module calls it.
WRITTEN_BY = {"own_hold_winter_moratorium": "MoratoriumRecord"}


def _writes(tree, ctor: str) -> bool:
    return any(isinstance(n, ast.Call) and (getattr(n.func, "id", None) == ctor
                                             or getattr(n.func, "attr", None) == ctor)
               for n in ast.walk(tree))


def writers(ctor: str) -> list:
    out = []
    for top in ("company", "saas"):
        for path in (ROOT / top).rglob("*.py"):
            if path != HOME and _writes(ast.parse(path.read_text(encoding="utf-8")), ctor):
                out.append(str(path.relative_to(ROOT)))
    return out


def test_a_ground_is_listed_unrouted_exactly_when_no_company_path_writes_it():
    assert set(UNROUTED_GROUNDS) <= set(PROTECTION_GROUNDS)
    assert set(UNROUTED_GROUNDS) <= set(WRITTEN_BY), "an unrouted ground with no named writer"
    for ground, reason in UNROUTED_GROUNDS.items():
        assert reason.strip(), ground
    for ground, ctor in WRITTEN_BY.items():
        found = writers(ctor)
        assert bool(found) == (ground not in UNROUTED_GROUNDS), (
            f"{ground}: writers {found} but listed unrouted={ground in UNROUTED_GROUNDS}. "
            "A writer built: delete its UNROUTED_GROUNDS row and wire the desk and the objection "
            "door. A writer removed: list the ground with its reason.")
    # The derivation can fail: a hold placed anywhere in company code is a writer.
    planted = ast.parse("rec = MoratoriumRecord('C1', None, None, None)")
    assert _writes(planted, "MoratoriumRecord") and not _writes(ast.parse("x = 1"), "MoratoriumRecord")


class _Meter:
    def __init__(self):
        self.paused_after = None

    def get_meter_supply_events(self, account_id, through):
        return {"interruptions": [], "top_ups": None, "top_ups_reason": "", "on_meter": True,
                "reason": ""}

    def get_meter_recoveries(self, account_id, moved_on, debt, through):
        return meter_recoveries(debt, dt.date.fromisoformat(moved_on),
                                dt.date.fromisoformat(through), suspended_after=self.paused_after)

    def suspend_deduction(self, account_id, after, reason):
        self.paused_after = self.paused_after or dt.date.fromisoformat(after)
        return {"suspended": True, "reason": reason}


def test_the_live_routes_carry_a_hold_both_ways_once_one_is_placed():
    """The whole partition on the two live routes that take the hold: with no hold each permits;
    with a hold in the REAL register (not a stub) each refuses and names it. So the moment a
    writer exists, the column refuses in operation without further wiring at these routes."""
    on = dt.date(2024, 3, 4)
    held = WinterMoratoriumRegister()
    held.register(MoratoriumRecord("C1", MoratoriumType.VULNERABLE_YEAR_ROUND, on, None, "hardship"))
    outcomes = {}
    for name, register in (("free", WinterMoratoriumRegister()), ("held", held)):
        desk = CollectionsJourneyDesk(view_at=lambda *a: {}, plan_offers=_Meter(),
                                      refuse_dunning_of_cleared_debt=lambda *a: None,
                                      post_cash=lambda *a: None)
        desk.own_holds = register
        desk._meters["C1"] = [dt.date(2024, 1, 1), 300.0, 0]
        desk._read_meter_recoveries("C1", on, Segment.RESIDENTIAL)
        objection = decide_debt_objection(
            TransferObjectionRegister(), "C1", "SW-1", on, ((900.0, 60),), prepayment=False,
            fuels=1, own_hold=register.is_protected("C1", on))
        outcomes[name] = (desk.meter_recovery_paused.get("C1"), objection)
    (free_pause, free_obj), (held_pause, held_obj) = outcomes["free"], outcomes["held"]
    assert free_pause is None and free_obj.objected, "the gate refuses with no hold placed"
    assert held_pause is not None and "own_hold_winter_moratorium" in held_pause["grounds"]
    assert not held_obj.objected and OWN_HOLD in held_obj.reason
