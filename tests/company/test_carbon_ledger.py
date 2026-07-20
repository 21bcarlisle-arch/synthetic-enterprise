"""R15 tests for the carbon three-ledger data model (company/carbon/carbon_ledger.py).

Covered:
  * THREE LEDGERS derived correctly; NET always reported incl. NEGATIVE (a claim
    that counts one side is not a claim).
  * IDEMPOTENT replay (C-S2) + ARRIVAL-ORDER independence (C-S1).
  * FAIL-LOUD £/tCO2e on net <= 0 (never reads as free/great) -- both directions.
  * FAIL-CLOSED on malformed events.
"""
from __future__ import annotations

import pytest

from company.carbon.carbon_ledger import (
    SAVED,
    SPENT,
    CarbonAbatementUnavailable,
    CarbonEvent,
    CarbonEventMalformed,
    CarbonLedger,
)

_AS_OF = "2025-12-31"


def _ev(eid, ledger, tco2e, source="H1", basis="grid_marginal", prov="estimated_from_data"):
    return CarbonEvent(event_id=eid, ledger=ledger, source=source, tco2e=tco2e,
                       basis=basis, provenance=prov, as_of=_AS_OF)


def test_three_ledgers_derived():
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 3.0), _ev("b", SAVED, 2.0), _ev("c", SPENT, 1.5)])
    assert led.saved() == pytest.approx(5.0)
    assert led.spent() == pytest.approx(1.5)
    assert led.net() == pytest.approx(3.5)
    assert led.three_ledger_view() == {
        "saved_tco2e": pytest.approx(5.0),
        "spent_tco2e": pytest.approx(1.5),
        "net_tco2e": pytest.approx(3.5),
    }


def test_net_reported_even_when_negative():
    # Spend more carbon than saved -> NET is negative and PRESENT, never hidden.
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 1.0), _ev("b", SPENT, 4.0)])
    assert led.net() == pytest.approx(-3.0)
    assert "net_tco2e" in led.three_ledger_view()
    assert led.three_ledger_view()["net_tco2e"] == pytest.approx(-3.0)


def test_idempotent_replay():
    led = CarbonLedger()
    led.add(_ev("a", SAVED, 3.0))
    led.add(_ev("a", SAVED, 3.0))  # same event_id -> no double count
    assert led.saved() == pytest.approx(3.0)
    assert len(led.events()) == 1


def test_arrival_order_independent():
    evs = [_ev("a", SAVED, 3.0), _ev("b", SPENT, 1.0), _ev("c", SAVED, 2.0)]
    a, b = CarbonLedger(), CarbonLedger()
    a.extend(evs)
    b.extend(reversed(evs))
    assert a.three_ledger_view() == b.three_ledger_view()


def test_cost_per_tonne_on_positive_net():
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 5.0), _ev("b", SPENT, 1.0)])  # net 4.0
    assert led.cost_per_tonne_abated(800.0) == pytest.approx(200.0)  # 800 / 4


def test_cost_per_tonne_fails_loud_on_zero_net():
    # net == 0 -> no defensible £/tonne; must RAISE, never return 0/inf ('free').
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 2.0), _ev("b", SPENT, 2.0)])  # net 0
    with pytest.raises(CarbonAbatementUnavailable):
        led.cost_per_tonne_abated(500.0)


def test_cost_per_tonne_fails_loud_on_negative_net():
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 1.0), _ev("b", SPENT, 3.0)])  # net -2
    with pytest.raises(CarbonAbatementUnavailable):
        led.cost_per_tonne_abated(500.0)


def test_empty_ledger_views_zero_but_cost_fails_loud():
    led = CarbonLedger()
    assert led.saved() == 0.0 and led.spent() == 0.0 and led.net() == 0.0
    with pytest.raises(CarbonAbatementUnavailable):
        led.cost_per_tonne_abated(100.0)


@pytest.mark.parametrize("bad", [
    lambda: _ev("", SAVED, 1.0),                       # empty id
    lambda: _ev("a", "reward", 1.0),                   # invalid ledger (not saved/spent)
    lambda: _ev("a", SAVED, -1.0),                     # negative magnitude (sign lives in ledger)
    lambda: CarbonEvent("a", SAVED, "H1", 1.0, "", "estimated_from_data", _AS_OF),   # empty basis
    lambda: CarbonEvent("a", SAVED, "H1", 1.0, "grid", "guess", _AS_OF),             # bad provenance
    lambda: CarbonEvent("a", SAVED, "H1", 1.0, "grid", "asserted", ""),              # empty as_of
])
def test_malformed_events_fail_closed(bad):
    with pytest.raises(CarbonEventMalformed):
        bad()
