"""A household that leaves at renewal wins no property: it goes to market, and no successor supplies.

HISTORY. Phase 7e rolled, for EVERY renewal leaver, whether "we win the home-mover's business"
(resi 0.55, SME 0.35), and on a win activated a pre-drawn successor supply point instead of going to
market. This file used to hold the controls for that disposition (an undeliverable win must still
go to market, WORKER_FINDING_A_WON_HOME_MOVER_WITH_NO_SUCCESSOR_SUPPLY_POINT_SUPPRESSES_THE_
REPLACEMENT_TOO_2026-08-14.md). RETIRED 2026-10-10 as a factual correction: a household that
switches supplier at renewal does not vacate its home, so no new occupant arrives and there is no
property to win. Real moves are B7's (`sim/customer_state_layer.py`, `_admit_incoming_occupant`).
The seat proposal SEAT_PROPOSAL_HOME_MOVER_RETENTION_AS_A_SUPPLIER_LEVER_2026-10-10.md records why.

What is controlled now, end to end over a truncated real run: a renewal leaver that HAS a
registered successor point (the population the old roll could activate) is a plain loss -- the
company is asked whether to replace it, and the successor never supplies a term. Mutation: restore
the old `if home_move_won: activate` branch with a win forced on the event and this reds.
"""
import pytest

import simulation.fabric_demand_path as fdp
import simulation.run_phase2b as rp
from saas.customers import SUCCESSOR_CUSTOMERS

# Short enough to keep the forced run cheap. Measured 2026-10-01: the first lifecycle event of a
# successor-bearing account is C5's on 2016-12-31. The leg asserts its force fired.
FORCED_RUN_END = "2017-04-30"

_SUCCESSOR_OF = {c["successor_of"]: c["customer_id"] for c in SUCCESSOR_CUSTOMERS
                 if c["commodity"] == "electricity"}


@pytest.fixture
def restore_acquired_book():
    """`run_phase2b` appends won acquisitions to a module-level list; a forced churn
    must not leak a customer into every later test in the session."""
    before = list(rp.ACQUIRED_CUSTOMERS)
    yield
    rp.ACQUIRED_CUSTOMERS[:] = before


@pytest.fixture(scope="module")
def shared_fabric_traces():
    """Both forced legs settle the same 137 premises over the same window, and neither touches the
    physics, so the second reuses the first's traces (~45 s each) -- `fdp.sharing_traces`."""
    with fdp.sharing_traces():
        yield


def _force_one_churn(monkeypatch, candidates) -> dict:
    """Turn the FIRST real lifecycle event of any account in `candidates` into a churn, and hold
    every other account to a renewal, so the forced churn is the window's only lifecycle churn
    and any market approach is its. Stamps `home_move_won=True` on it too: a world that still read
    that field would activate the successor, which is the defect this file controls."""
    real_roll = rp.roll_lifecycle_event
    candidates = set(candidates)
    forced = {"account": None}

    def wrapper(cid, term_start_str, *args, **kwargs):
        event = real_roll(cid, term_start_str, *args, **kwargs)
        if event is None:
            return None
        if forced["account"] is None and event["customer_id"] in candidates:
            event["event_type"] = "churned"
            event["home_move_won"] = True
            forced["account"] = event["customer_id"]
        elif event["customer_id"] != forced["account"]:
            event["event_type"] = "renewed"
        return event

    monkeypatch.setattr(rp, "roll_lifecycle_event", wrapper)
    return forced


def _lifecycle_churns(result: dict) -> list[str]:
    """The accounts that left through `roll_lifecycle_event` -- the route the hold above governs.

    NOT `churned_billing_accounts`. That is the union of every departure route, and since C1b's
    SVT-inertia departures (`_svt_departures`, `DEPARTURE_OCCASION_SVT_SEGMENT`) it also holds
    accounts leaving an SVT stint, which no lifecycle event decides and this hold cannot reach:
    on 2026-09-30 it read `['C7', 'PROS-2016-0003', ...]`, nine accounts, for one forced churn.
    Those departures never go to market -- the only `decide_acquisition` call is in the lifecycle
    branch -- so they cannot pollute the spy, and the attribution rests on this list alone.
    """
    assert result["churned_billing_accounts"], "no departure at all -- the forced churn never ran"
    return sorted(
        e["customer_id"] for e in result["customer_events"] if e.get("event_type") == "churned"
    )


def _spy_on_going_to_market(monkeypatch) -> list:
    real_decide = rp.decide_acquisition
    calls: list = []

    def wrapper(*args, **kwargs):
        calls.append(kwargs or args)
        return real_decide(*args, **kwargs)

    monkeypatch.setattr(rp, "decide_acquisition", wrapper)
    return calls


def test_a_renewal_leaver_with_a_successor_point_goes_to_market_and_no_successor_supplies(
    monkeypatch, restore_acquired_book, shared_fabric_traces
):
    """Defect: a switcher credited with winning its own property, its successor supplied in place
    of a market replacement."""
    assert _SUCCESSOR_OF, "the roster carries no successor point, so this control has no subject"
    forced = _force_one_churn(monkeypatch, _SUCCESSOR_OF)
    went_to_market = _spy_on_going_to_market(monkeypatch)
    result = rp.main(report_end=FORCED_RUN_END)

    account = forced["account"]
    assert account is not None, (
        f"no successor-bearing account {sorted(_SUCCESSOR_OF)} reached a lifecycle event before "
        f"{FORCED_RUN_END} -- the force never fired and every leg below is vacuous"
    )
    assert _lifecycle_churns(result) == [account]
    assert went_to_market, f"{account} left at renewal and the company was never asked to replace it"
    successor = _SUCCESSOR_OF[account]
    assert not [a for a in result["account_state_log"] if a.get("customer_id") == successor], (
        f"{successor} was supplied: a switcher's departure activated a property win"
    )
    assert "won_successor_activations" not in result
