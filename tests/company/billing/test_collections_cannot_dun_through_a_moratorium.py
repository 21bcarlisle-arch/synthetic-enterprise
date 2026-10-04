"""Collections cannot dun an account inside a Debt Respite moratorium (atom C33, level 2).

Subject: `company/billing/arrears_engine.select_dunning_step` and the control
`assert_no_dunning_through_a_moratorium`; the register `company/billing/breathing_space_register`;
the production caller `PaymentObservationConsumer._collections_view`.
The law: `docs/domain_artefact_library/regulatory/debt_respite_breathing_space_moratorium.json`
(SI 2020/1311 regs 7, 11, 26).

THE PARTITION, NOT THE REFUSAL. "No account is dunned through a moratorium" passes on an empty
register and on a selector that never duns anyone. Every refusal test below therefore sits beside
a reachability test, and the control itself asserts the selector CAN collect before it asserts
that a moratorium stops it.

KEYED TO THE ARTEFACT, NOT THE MODULE. The duration test reads the statutory 60 and its
"beginning with" counting from the commons file, so a module that drifted from the law reds here
rather than agreeing with itself.
"""
from __future__ import annotations

import datetime as dt
import inspect
import json
import re

import pytest

from company.billing import arrears_engine
from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import (
    MORATORIUM_HOLD,
    AgedItem,
    DunningThroughAMoratoriumError,
    assert_no_dunning_through_a_moratorium,
    collections_snapshot,
    current_dunning_step,
    dunning_path,
    select_dunning_step,
)
from company.billing.breathing_space_register import (
    DEBT_RESPITE_COMMONS,
    BreathingSpaceRegister,
    BreathingSpaceType,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.crm.account_hierarchy import Segment

LAW = json.loads(DEBT_RESPITE_COMMONS.read_text())
#: Bound at import, so a test that monkeypatches the module's selector still has the real one.
_SHIPPED_SELECTOR = select_dunning_step
DUE = dt.date(2024, 1, 15)


def _items(days: int) -> list:
    return [AgedItem("INV", 100.0, DUE, days, False)]


# --- the input is required --------------------------------------------------------------------

@pytest.mark.parametrize("fn", [select_dunning_step, collections_snapshot])
def test_the_moratorium_answer_is_a_required_keyword_with_no_default(fn):
    param = inspect.signature(fn).parameters["moratorium_active"]
    assert param.kind is inspect.Parameter.KEYWORD_ONLY
    assert param.default is inspect.Parameter.empty


def test_a_caller_that_did_not_ask_the_register_gets_no_step():
    with pytest.raises(TypeError, match="moratorium_active"):
        select_dunning_step(_items(120), Segment.RESIDENTIAL)


# --- the partition over every segment's whole path ---------------------------------------------

@pytest.mark.parametrize("segment", list(Segment))
def test_the_shipped_selector_collects_outside_and_holds_inside_at_every_trigger(segment):
    # reachability first: outside a moratorium every trigger selects its own real step
    for step in dunning_path(segment):
        _, free = select_dunning_step(
            _items(step.trigger_days_overdue), segment, moratorium_active=False)
        assert free == step and free != MORATORIUM_HOLD
    # then the flip, at the same triggers
    for step in dunning_path(segment):
        _, held = select_dunning_step(
            _items(step.trigger_days_overdue), segment, moratorium_active=True)
        assert held == MORATORIUM_HOLD
    # and a hold is not invented for an account that owes nothing, or nothing yet due
    assert select_dunning_step([], segment, moratorium_active=True) == (None, None)
    assert select_dunning_step(_items(-1), segment, moratorium_active=True)[1] is None
    assert_no_dunning_through_a_moratorium(select_dunning_step, segment=segment)


# --- the control fires on each named defect -----------------------------------------------------

def _ignores_the_moratorium(items, segment, *, moratorium_active):
    # MUTATION: the pre-C33 selector -- days overdue alone, the answer read and then dropped
    return _SHIPPED_SELECTOR(items, segment, moratorium_active=False)


def _holds_only_the_enforcement_end(items, segment, *, moratorium_active):
    # MUTATION: the narrow reading -- hold final notices and agency steps, keep sending reminders.
    # Reg 7(7)(a) forbids "a step to collect", so the first reminder is an offence too.
    worst, step = _ignores_the_moratorium(items, segment, moratorium_active=moratorium_active)
    if step is not None and moratorium_active and step.trigger_days_overdue >= 56:
        return worst, MORATORIUM_HOLD
    return worst, step


def _holds_everything(items, segment, *, moratorium_active):
    # MUTATION: a selector that never collects -- passes every refusal leg vacuously
    worst = max(it.days_overdue for it in items) if items else None
    return worst, (MORATORIUM_HOLD if items else None)


def _holds_an_account_that_owes_nothing(items, segment, *, moratorium_active):
    if moratorium_active and not items:
        return None, MORATORIUM_HOLD
    return select_dunning_step(items, segment, moratorium_active=moratorium_active)


@pytest.mark.parametrize("selector,said", [
    (_ignores_the_moratorium, "reg 7(7)(a)"),
    (_holds_only_the_enforcement_end, "7 days overdue"),
    (_holds_everything, "cannot collect at all"),
    (_holds_an_account_that_owes_nothing, "owing nothing"),
])
def test_the_control_fires_and_names_the_defect(selector, said):
    with pytest.raises(DunningThroughAMoratoriumError, match=re.escape(said)):
        assert_no_dunning_through_a_moratorium(selector, segment=Segment.RESIDENTIAL)


def test_a_snapshot_refuses_at_read_time_if_the_selector_stops_asking(monkeypatch):
    """WIRING: the control runs on every live snapshot, so a regressed selector raises in
    production rather than publishing a final notice."""
    monkeypatch.setattr(arrears_engine, "select_dunning_step", _ignores_the_moratorium)
    book = LedgerBook()
    book.post(_bill("A", dt.date(2024, 1, 1), 100.0))
    with pytest.raises(DunningThroughAMoratoriumError):
        collections_snapshot(book.ledger("A"), Segment.RESIDENTIAL, False, dt.date(2024, 6, 1),
                             moratorium_active=False)


# --- the register reads the statute's counting --------------------------------------------------

def test_a_standard_moratorium_protects_exactly_the_statutory_days_counting_the_start():
    days = LAW["breathing_space_moratorium"]["duration_days"]
    assert LAW["breathing_space_moratorium"]["duration_counts_the_start_day"] is True
    assert "beginning with the date on which it started" in LAW["breathing_space_moratorium"]["quoted"]
    reg = BreathingSpaceRegister()
    start = dt.date(2023, 6, 1)
    reg.register_entry("A", BreathingSpaceType.STANDARD, start, 300.0)
    protected = [d for d in range(-1, days + 2)
                 if reg.moratorium_active("A", start + dt.timedelta(days=d))]
    assert protected == list(range(0, days))          # day 1 .. day 60, nothing either side
    assert reg.moratorium_active("B", start) is False  # keyed to the account


# --- the production caller ----------------------------------------------------------------------

def _bill(acct: str, day: dt.date, amount: float) -> LedgerEvent:
    return LedgerEvent(f"{acct}-{day}", acct, LedgerEventType.BILL_DEBIT, amount, day,
                       dt.datetime.combine(day, dt.time(12)))


def test_the_consumer_holds_an_account_its_register_says_is_in_a_moratorium():
    book = LedgerBook()
    book.post(_bill("A", dt.date(2023, 1, 1), 400.0))   # ~5 months overdue by June
    reg = BreathingSpaceRegister()
    reg.register_entry("A", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0)
    consumer = PaymentObservationConsumer(ledger_book=book, breathing_space=reg)

    inside = consumer._collections_view("A", Segment.RESIDENTIAL, dt.date(2023, 6, 15))
    after = consumer._collections_view("A", Segment.RESIDENTIAL, dt.date(2023, 8, 1))
    assert after["dunning_action"] == "prepayment_or_debt_agency"   # reachability: it CAN enforce
    assert inside["dunning_action"] == MORATORIUM_HOLD.action
    assert inside["moratorium_active"] is True and after["moratorium_active"] is False
    # a moratorium changes the step, never the money: the debt is still owed and still read
    assert inside["undisputed_overdue_gbp"] == after["undisputed_overdue_gbp"] == 400.0


def test_a_consumer_built_without_a_register_holds_an_empty_one_not_none():
    consumer = PaymentObservationConsumer()
    assert isinstance(consumer.breathing_space, BreathingSpaceRegister)
    assert consumer.breathing_space.active_records(dt.date(2024, 1, 1)) == []
