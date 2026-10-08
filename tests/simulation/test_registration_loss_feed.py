"""The world tells the losing supplier of every departure, one notice per supply point (EP12).

The live-run control runs the 2016-01 .. 2017-02 window, which holds a departure on each of
the two routes that add to `churned_billing_accounts` -- the renewal-point roll and the SVT
segment hazard -- and asserts the company's change-of-supplier register holds exactly the
departures the world rolled, no more, with nothing from the departure event riding along.
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

from interface.contracts.registration_loss_seam import (
    CSS_SENDER,
    CSS_SWITCH_PENDING_NOTIFICATION_TYPE,
    OBSERVABLE_PAYLOAD_FIELDS,
    PRE_CSS_ELECTRICITY_SENDER,
    PRE_CSS_GAS_SENDER,
    UNSOLICITED_PAYLOAD_TYPES,
)
from simulation.household import household_of
from simulation.registration_loss_feed import RegistrationLossFeed, supply_points_on_supply

_ELEC = {"C1": [{"acquisition_date": "2016-01-01"}], "C2": [{"acquisition_date": "2016-01-01"}]}
_GAS = {"C1g": [{"acquisition_date": "2016-06-01"}]}


def test_every_supply_point_the_household_held_is_on_supply_and_no_other():
    """Defect guarded: a dual-fuel household notified for one leg only, a
    neighbour's point notified, or a leg whose supply had not yet begun."""
    assert supply_points_on_supply("C1", "2017-01-01", _ELEC, _GAS) == [
        ("C1", "electricity"), ("C1g", "gas")]
    assert supply_points_on_supply("C1", "2016-03-01", _ELEC, _GAS) == [("C1", "electricity")]


def test_each_sender_stream_is_gap_free_and_regime_and_fuel_pick_the_sender():
    """Defect guarded: a shared or skipping sequence (the consumer would read a
    gap that is not a loss), a CSS-era notice on a pre-CSS stream, or a gas loss
    sent by the electricity registration service."""
    feed = RegistrationLossFeed()
    wires = (
        feed.wire_notices_for_departure([("C1", "electricity"), ("C1g", "gas")], "2017-02-21")
        + feed.wire_notices_for_departure([("C2", "electricity"), ("C2g", "gas")], "2023-03-01")
        + feed.wire_notices_for_departure([("C3", "electricity")], "2017-05-01")
    )
    assert [(w["sender"], w["envelope"]["sequence"]) for w in wires] == [
        (PRE_CSS_ELECTRICITY_SENDER, 0), (PRE_CSS_GAS_SENDER, 0),
        (CSS_SENDER, 0), (CSS_SENDER, 1), (PRE_CSS_ELECTRICITY_SENDER, 1)]
    assert wires[2]["envelope"]["observed_at"] == "2023-02-28T17:00:00"



def test_a_css_switch_is_sent_a_pending_notice_before_its_loss_notice_and_a_pre_css_one_is_not():
    """Defect guarded: the Invitation to Intervene missing for a CSS switch, sent for a pre-CSS
    one (no such message existed), carrying more than the loss notice's three fields, or
    sequenced after the Secured Inactive notice on the CSS stream."""
    feed = RegistrationLossFeed()
    points = [("C1", "electricity"), ("C1g", "gas")]
    assert feed.wire_pending_notices_for_departure(points, "2017-02-21") == []
    pending = feed.wire_pending_notices_for_departure(points, "2023-03-01")
    loss = feed.wire_notices_for_departure(points, "2023-03-01")
    assert [w["envelope"]["notification_type"] for w in pending] == [
        CSS_SWITCH_PENDING_NOTIFICATION_TYPE] * 2
    assert [w["envelope"]["sequence"] for w in pending + loss] == [0, 1, 2, 3]
    assert pending[0]["envelope"]["observed_at"] == "2023-02-28T00:00:00"
    for wire in pending:
        assert set(wire["envelope"]["payload"]) == set(
            OBSERVABLE_PAYLOAD_FIELDS["RegistrationLossNotice"])


def test_the_route_share_is_read_from_the_register_and_a_set_share_is_refused(monkeypatch):
    """Defect guarded: the route share typed in code instead of read from
    assumption_toggles.yaml, or a share someone sets in the register silently ignored while
    every switch is still sent on the ASAP floor. Both arms are taken: the register's own
    null row builds a feed, and the same row set to a number refuses by name."""
    from simulation import registration_loss_feed as feed_mod

    assert feed_mod._toggle_row(feed_mod.SWITCH_ROUTE_TOGGLE)["default"] is None
    assert feed_mod.asap_route_share() == 1.0
    RegistrationLossFeed()
    monkeypatch.setattr(
        feed_mod, "_toggle_row", lambda toggle_id: {"id": toggle_id, "default": 0.6})
    with pytest.raises(ValueError, match="q4_css_switch_route_share_asap is set to 0.6"):
        RegistrationLossFeed()

def test_the_world_refuses_to_send_a_notice_carrying_world_truth(monkeypatch):
    """Defect guarded: the world-side belt. A payload field named like a
    departure-event field (here the roll) must refuse at encode, not cross."""
    from simulation import registration_loss_feed as feed_mod

    monkeypatch.setattr(feed_mod, "FORBIDDEN_TRUTH_FIELDS", ("supply_point_id",))
    with pytest.raises(ValueError, match="would carry world truth"):
        RegistrationLossFeed().wire_notices_for_departure([("C1", "electricity")], "2017-02-21")


def test_a_world_notice_is_accepted_by_the_company_end_to_end():
    """Defect guarded: a producer and a consumer that each pass their own tests and
    do not speak to each other (credential, version, key set, sender)."""
    from company.crm.cos_process import CoSRegister

    reg = CoSRegister(holds={"C1", "C1g"}.__contains__)
    for wire in RegistrationLossFeed().wire_notices_for_departure(
            [("C1", "electricity"), ("C1g", "gas")], "2023-03-01"):
        assert reg.receive_loss_wire(wire)
    assert [(n["supply_point_id"], n["notified_on"]) for n in reg.losses_notified()] == [
        ("C1", "2023-02-28"), ("C1g", "2023-02-28")]


@pytest.fixture(scope="module")
def _run(tmp_path_factory):
    from simulation.run_phase2b import main

    return main(
        report_end="2017-02-28",
        gap_ledger_path=tmp_path_factory.mktemp("gap") / "coupled_gap_ledger.json",
    )


def _departures(result) -> dict[str, tuple[str, list[dict]]]:
    """Household -> (effective date, the world's departure events for it), both routes."""
    out: dict[str, tuple[str, list[dict]]] = {}
    events = [e for e in result["customer_events"] if e["event_type"] == "churned"]
    for e in events + list(result["svt_departures"]):
        hh = household_of(e["customer_id"])
        out.setdefault(hh, (e["event_date"], []))[1].append(e)
    return out


def test_both_departure_routes_occur_in_the_window(_run):
    """The partition control: without a departure on each route, the test
    below could pass with one call site unwired."""
    assert any(e["event_type"] == "churned" for e in _run["customer_events"])
    assert _run["svt_departures"]


def test_every_departure_reaches_the_company_as_exactly_one_notice_per_supply_point(_run):
    """Defect guarded: a departure route the company never hears of, a notice
    for a household that stayed, a duplicate, a wrong effective date, or a
    notice dated after the switch it reports."""
    departures = _departures(_run)
    held = _run["registration_losses_notified"]
    assert set(departures) == set(_run["churned_billing_accounts"])
    assert {household_of(n["supply_point_id"]) for n in held} == set(departures)
    points = [n["supply_point_id"] for n in held]
    assert len(points) == len(set(points))
    for n in held:
        effective, _ = departures[household_of(n["supply_point_id"])]
        assert n["supply_effective_from"] == effective
        assert n["notified_on"] <= effective


def test_every_live_departure_is_on_the_losing_suppliers_book_when_its_notice_arrives(_run):
    """Defect guarded, in its live direction: the book check refusing a REAL departure --
    a register that refuses everything passes the unit leg's refusal arm, not this one."""
    assert _run["registration_losses_notified"]
    assert _run["registration_loss_exceptions"] == []


def test_nothing_the_world_knows_about_a_departure_crosses(_run):
    """Defect guarded: a departure-event field (the roll, the cause, the
    probability) riding on the notice or on what the company holds."""
    world_keys = {k for _, evs in _departures(_run).values() for e in evs for k in e}
    notice_fields = {f.name for t in UNSOLICITED_PAYLOAD_TYPES for f in dataclasses.fields(t)}
    held_keys = {k for n in _run["registration_losses_notified"] for k in n}
    assert "random_roll" in world_keys  # the reading is of real events, not an empty set
    assert not notice_fields & world_keys
    assert not held_keys & world_keys
