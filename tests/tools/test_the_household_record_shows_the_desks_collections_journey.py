"""The published per-household record carries the company desk's collections journey.

DEFECT LINE: the 24 Oct build (94b281af7) gave the desk a step past its top rung (a re-offer per
missed bill) and a statute-bar write-off, but `extract_report_data` dropped `collections_journeys`,
so every household page read the billing ledger's two notices and then silence -- the defect the
build fixed, still shown to a reader of explore.

  * `test_the_published_run_carries_the_desks_journeys` -- the report's whitelist passes them.
  * `test_every_dated_stage_of_a_journey_reaches_the_reaction_chain` -- one event per stage, the
    re-offer and the write-off included, beside the ledger's notices rather than replacing them.
  * `test_while_the_desk_holds_the_debt_the_ledgers_letters_yield_and_its_facts_stay` -- one
    narrator per letter: the ledger's notices dated inside a desk hold are not on the record.
  * `test_the_explore_debt_journey_reads_the_desk_and_can_still_refuse` -- the partition: the scorer
    takes the desk branch when the record has one, the ledger branch when not, and refuses a
    journey that never got past a reminder.
"""
from __future__ import annotations

from company.analytics.decision_event_ledger import build_customer_ledger
from tools import generate_explore_cast as gen


def _stage(stage, on, overdue=93.68, **extra):
    return {"stage": stage, "on": on, "decision": stage, "overdue_gbp": overdue,
            "days_overdue": 0, **extra}


#: A journey shaped like the 19 Oct run's £93.68 bill: the five rungs, a re-offer per further bill
#: missed, and the statute bar six years on.
JOURNEY = {"account_id": "ACC-SYN-2016-001", "segment": "residential", "exit": "write_off", "stages": [
    _stage("missed_payment", "2019-02-01"), _stage("reminder", "2019-02-08"),
    _stage("reminder_2", "2019-02-15"), _stage("repayment_plan_offer", "2019-03-01"),
    _stage("arrangement_offered", "2019-03-01", household_acceptance=None, acceptance_gap="the world names why"),
    _stage("final_notice", "2019-03-29"), _stage("prepayment_or_debt_agency", "2019-05-02"),
    _stage("prepayment_offered", "2019-05-02"),
    _stage("repayment_plan_reoffer", "2019-06-01"), _stage("arrangement_offered", "2019-06-01"),
    _stage("write_off", "2025-02-01", written_off_gbp=93.68),
]}

LEDGER_CASE = {"arrears_history": [{"arrears_gbp": 93.68, "stages": [
    {"stage": "PAYMENT_MISSED", "date": "2019-01-18", "note": "missed"},
    {"stage": "FIRST_NOTICE", "date": "2019-01-25", "note": "First overdue notice"},
    {"stage": "SECOND_NOTICE", "date": "2019-02-08", "note": "Second notice"}]}]}


def _run_output(**phase2b):
    base = {"all_records": [], "committee_wake_ups": [], "hedge_evolution": {},
            "starting_treasury": 0.0, "final_treasury": 0.0, "total_gross": 0.0,
            "total_capital": 0.0, "administration_event": None, "customer_events": []}
    base.update(phase2b)
    return {"phase2b": base, "years": {"2017": {}}}


def test_the_published_run_carries_the_desks_journeys():
    from saas.reporting.annual_report import extract_report_data

    assert extract_report_data(_run_output(collections_journeys=[JOURNEY]))["collections_journeys"] == [JOURNEY]
    assert extract_report_data(_run_output())["collections_journeys"] is None


def test_every_dated_stage_of_a_journey_reaches_the_reaction_chain():
    chain = build_customer_ledger("SYN-2016-001", [], [], [], LEDGER_CASE, collections_journeys=[JOURNEY])
    desk = [e for e in chain if e["event_type"].startswith("collections_")]
    assert [e["event_type"] for e in desk] == ["collections_" + s["stage"] for s in JOURNEY["stages"]]
    ledger = [e["event_type"] for e in chain if e["event_type"].startswith("arrears_")]
    assert ledger == ["arrears_payment_missed", "arrears_first_notice"], (
        "the ledger's stages stay, less its letter dated inside the desk's hold")
    reoffer, = [e for e in desk if e["event_type"] == "collections_repayment_plan_reoffer"]
    write_off, = [e for e in desk if e["event_type"] == "collections_write_off"]
    assert "past the top rung" in reoffer["description"]
    assert "statute-barred" in write_off["description"] and write_off["amount_gbp"] == 93.68
    unanswered = [e for e in desk if e["event_type"] == "collections_arrangement_offered"][0]
    assert "the world names why" in unanswered["description"], "an unknown answer says why"
    alone = build_customer_ledger("SYN-2016-001", [], [], [], LEDGER_CASE)
    assert [e for e in chain if not e["event_type"].startswith("collections_")] == [
        e for e in alone if e["event_type"] != "arrears_second_notice"]


def test_while_the_desk_holds_the_debt_the_ledgers_letters_yield_and_its_facts_stay():
    """DEFECT LINE (209c3350ab, 55 of 402 debt stories): the ledger's per-bill letter and the desk's
    rung narrated one debt at two amounts (OCC-9edd7eed4aab, 22 Jul 2019: GBP18.71 beside GBP60.78).
    One supplier sends one letter per act; the desk's is the one on the record while it holds the
    account (`company_debt_management.md`, "Who sends the overdue notice")."""
    held = {"exit": "cured", "stages": [_stage("missed_payment", "2019-02-01"), _stage("cured", "2019-03-01")]}
    still_open = {"exit": None, "stages": [_stage("missed_payment", "2020-06-01")]}
    case = {"arrears_history": [{"arrears_gbp": 18.71, "stages": [
        {"stage": "FIRST_NOTICE", "date": "2019-01-25"},       # before the hold: the only narrator
        {"stage": "PAYMENT_MISSED", "date": "2019-02-01"},     # a fact, not a letter
        {"stage": "FIRST_NOTICE", "date": "2019-02-08"},       # inside: yields
        {"stage": "SECOND_NOTICE", "date": "2019-03-01"},      # on the exit day: still held
        {"stage": "SECOND_NOTICE", "date": "2019-03-02"},      # after the cure: the only narrator
        {"stage": "FIRST_NOTICE", "date": "2024-01-01"}]}]}   # inside a journey with no exit yet
    chain = build_customer_ledger("SYN-2016-001", [], [], [], case, collections_journeys=[held, still_open])
    kept = [(e["date"], e["event_type"]) for e in chain if e["event_type"].startswith("arrears_")]
    assert kept == [("2019-01-25", "arrears_first_notice"), ("2019-02-01", "arrears_payment_missed"),
                    ("2019-03-02", "arrears_second_notice")]
    # The partition can be taken both ways: with no hold, every letter is on the record.
    assert sum(e["event_type"].startswith("arrears_") for e in
               build_customer_ledger("SYN-2016-001", [], [], [], case)) == 6
    # A dual-fuel gas leg: the desk holds the home on the electricity account. Its letters yield to
    # that journey, and the journey's own events are shown once, on the electricity leg, not here.
    gas = build_customer_ledger("SYN-2016-001", [], [], [], case, collections_journeys=[],
                                desk_journeys=[held, still_open])
    assert [(e["date"], e["event_type"]) for e in gas] == kept


HH = {"legs": ["electricity"]}


def _ev(chain):
    return {"reaction": sorted(chain, key=lambda r: r["date"]), "ledger": [], "timeline": [], "invoice": []}


def test_the_explore_debt_journey_reads_the_desk_and_can_still_refuse():
    with_desk = gen._score_debt({}, _ev(build_customer_ledger(
        "SYN-2016-001", [], [], [], LEDGER_CASE, collections_journeys=[JOURNEY])), {})
    ledger_only = gen._score_debt({}, _ev(build_customer_ledger("SYN-2016-001", [], [], [], {
        "arrears_history": [{"arrears_gbp": 1.0, "stages": LEDGER_CASE["arrears_history"][0]["stages"]
                             + [{"stage": "WRITTEN_OFF", "date": "2019-04-18", "note": "w"}]}]})), {})
    shallow = gen._score_debt({}, _ev(build_customer_ledger("SYN-2016-001", [], [], [], {}, collections_journeys=[
        {**JOURNEY, "exit": None, "stages": JOURNEY["stages"][:2]}])), {})
    assert with_desk and ledger_only and shallow is None
    shown = [r["event_type"] for _, _, r in with_desk[1]]
    assert all(t.startswith("collections_") for t in shown), "one ladder per journey, never both"
    assert shown[0] == "collections_missed_payment" and shown[-1] == "collections_write_off"
    titles = [gen._template(HH, _ev([]), rec["date"], kind, rec)[0] for _, kind, rec in with_desk[1]]
    assert "Arrears" not in titles and "Collections" not in titles, titles


def test_every_stage_the_desk_can_enter_has_words_and_a_depth():
    from company.analytics.decision_event_ledger import _COLLECTIONS_STAGE_WORDS
    from company.billing import collections_journey as cj
    from company.billing.arrears_engine import MORATORIUM_HOLD, dunning_path
    from company.crm.account_hierarchy import Segment

    stages = {step.action for seg in Segment for step in dunning_path(seg)} | {MORATORIUM_HOLD.action} | {
        cj.MISSED_PAYMENT, cj.CURED, cj.PLAN_REOFFER_STEP, cj.ARRANGEMENT_OFFERED, cj.ARRANGEMENT,
        cj.PREPAYMENT_OFFERED, cj.PREPAYMENT, cj.WRITE_OFF}
    assert stages - set(_COLLECTIONS_STAGE_WORDS) == set()
    assert {"collections_" + s for s in stages} - set(gen._DESK_DEPTH) == set()
    assert {"collections_" + s for s in stages} - set(gen._DESK_TITLES) == set()


def test_the_ledgers_notices_are_dated_at_the_desks_rungs_for_one_act_one_ladder():
    """The ledger offered its plan at day 21 and the desk at 28 (`company_debt_management.md`, "One
    ladder for one act"). Keyed to the property: whatever day the desk's rung moves to, the ledger's
    notice moves with it."""
    import datetime as dt

    from company.billing.arrears_engine import dunning_path, ledger_notices
    from company.crm.account_hierarchy import Segment

    rung = {s.action: s.trigger_days_overdue for s in dunning_path(Segment.RESIDENTIAL)}
    due = dt.date(2019, 1, 1)
    days = {n["stage"]: (dt.date.fromisoformat(n["date"]) - due).days for n in ledger_notices(due, 10.0)}
    assert days == {"FIRST_NOTICE": rung["reminder"], "SECOND_NOTICE": rung["repayment_plan_offer"]}
