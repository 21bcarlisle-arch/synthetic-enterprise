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
    # NOTE (2026-08-19): this assertion previously read
    #     assert led.three_ledger_view() == {"saved_tco2e": approx(5.0), ...}
    # i.e. it SPECIFIED the three-bare-floats shape that was the defect -- the block
    # was correct by construction because the test described exactly what it did.
    # Rewritten against the labelled row; the tonnages are unchanged.
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 3.0), _ev("b", SAVED, 2.0), _ev("c", SPENT, 1.5)])
    assert led.saved() == pytest.approx(5.0)
    assert led.spent() == pytest.approx(1.5)
    assert led.net() == pytest.approx(3.5)
    view = led.three_ledger_view()
    assert {k: v.tco2e for k, v in view.items()} == {
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
    assert led.three_ledger_view()["net_tco2e"].tco2e == pytest.approx(-3.0)


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


# --- C1: THE ABSENT-FEED FAIL-OPEN (2026-08-19, E5 FRAME control C1) -----------------
# NAMED DEFECT: with no SPENT events, net() == saved() - 0.0 == saved(). The mission
# metric therefore reports its BEST POSSIBLE value exactly WHEN the operational-carbon
# feed is missing -- and the FRAME established that feed IS unbuilt (no token sensor,
# no compute-kWh meter exists in the tree), so this was the ledger's live behaviour,
# not a hypothetical. Arithmetic cannot tell "emitted nothing" from "did not measure".
# MUTATION (must go RED): delete the `if status != OK: raise` block from
# cost_per_tonne_abated -- test_one_sided_net_refuses_to_price then returns 160.0.

def test_one_sided_net_reports_a_number_but_refuses_to_price_it():
    """SAVED-only: NET is still REPORTED (never hidden, per the module's own rule),
    but it must not be priced -- an unbounded estimate is not a conservative one."""
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 5.0)])
    view = led.three_ledger_view()
    assert view["net_tco2e"].tco2e == pytest.approx(5.0)      # reported...
    assert view["net_tco2e"].status == "one_sided"            # ...and labelled as half a ledger
    assert view["spent_tco2e"].status == "no_source"          # the absence, not a measured 0.0
    with pytest.raises(CarbonAbatementUnavailable):
        led.cost_per_tonne_abated(800.0)


def test_one_sided_the_other_way_is_also_refused():
    """The control is about MISSING A SIDE, not about missing SPENT specifically --
    a SPENT-only ledger is equally unpriceable (and its net is negative anyway)."""
    led = CarbonLedger()
    led.extend([_ev("a", SPENT, 5.0)])
    assert led.three_ledger_view()["net_tco2e"].status == "one_sided"
    with pytest.raises(CarbonAbatementUnavailable):
        led.cost_per_tonne_abated(800.0)


def test_empty_ledger_is_no_source_not_a_measured_zero():
    """C1 proper: 0.0 with no events behind it is an ABSENCE. A row that reports a
    bare 0.0 invites reading it as 'we emitted nothing', which is a claim."""
    view = CarbonLedger().three_ledger_view()
    assert [r.status for r in view.values()] == ["no_source"] * 3
    assert all(r.event_count == 0 for r in view.values())
    assert all(r.provenance_mix == {} for r in view.values())


def test_two_sided_ledger_still_prices_normally():
    """FIRES-ON-DEFECT-ONLY: the C1 guard must not refuse an ordinary complete
    ledger. Without this, 'raise always' would pass every test above."""
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 5.0), _ev("b", SPENT, 1.0)])   # net 4.0
    assert led.three_ledger_view()["net_tco2e"].status == "ok"
    assert led.cost_per_tonne_abated(800.0) == pytest.approx(200.0)


# --- R14 FOR CARBON: THE LABELS MUST SURVIVE AGGREGATION -----------------------------
# NAMED DEFECT: CarbonEvent spends four fail-closed guards making basis/provenance/as_of
# MANDATORY on every event, and three_ledger_view() then returned three bare floats --
# destroying all three at the one method whose output is the publishable headline. The
# labels were never missing; aggregation dropped them.
# MUTATION (must go RED): restore
#     return {"saved_tco2e": self.saved(), "spent_tco2e": self.spent(), "net_tco2e": self.net()}

def test_basis_and_provenance_survive_aggregation():
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 3.0, basis="grid_marginal", prov="estimated_from_data"),
                _ev("b", SPENT, 1.0, basis="activity_based", prov="assumed")])
    saved_row = led.three_ledger_view()["saved_tco2e"]
    assert saved_row.bases == ("grid_marginal",)
    assert saved_row.provenance_mix == {"estimated_from_data": pytest.approx(1.0)}
    assert saved_row.as_of_earliest == _AS_OF and saved_row.as_of_latest == _AS_OF


def test_net_inherits_every_basis_behind_it_and_says_it_is_mixed():
    """A grid-marginal tonne and a grid-average tonne are not the same unit. A scalar
    basis label on a mixed aggregate would be a false claim about a real number, so
    the row carries the SET -- not whichever basis happened to arrive first."""
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 3.0, basis="grid_marginal"),
                _ev("b", SAVED, 1.0, basis="grid_average"),
                _ev("c", SPENT, 1.0, basis="activity_based")])
    net_row = led.three_ledger_view()["net_tco2e"]
    assert net_row.bases == ("activity_based", "grid_average", "grid_marginal")
    assert net_row.mixed_basis is True


def test_provenance_mix_is_weighted_by_tonnage_not_event_count():
    """NULL CONTROL for the weighting: one LARGE assumed event among many small
    estimated ones. By event count assumed is 1-of-4 (25%); by tonnage it is 97%.
    The reader's question is 'how much of this number is assumed?', so tonnage wins.
    MUTATION (must go RED): weight by len(events) instead of tonnage share."""
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 1.0, prov="estimated_from_data"),
                _ev("b", SAVED, 1.0, prov="estimated_from_data"),
                _ev("c", SAVED, 1.0, prov="estimated_from_data"),
                _ev("d", SAVED, 97.0, prov="assumed")])
    mix = led.three_ledger_view()["saved_tco2e"].provenance_mix
    assert mix["assumed"] == pytest.approx(0.97)
    assert mix["estimated_from_data"] == pytest.approx(0.03)
    assert sum(mix.values()) == pytest.approx(1.0)


def test_all_zero_tonnage_invents_no_provenance_mix():
    """With no tonnage to attribute, ANY mix is invented -- and an invented
    '100% estimated_from_data' is exactly the flattering label the block prevents."""
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 0.0, prov="asserted"), _ev("b", SPENT, 0.0, prov="assumed")])
    view = led.three_ledger_view()
    assert view["saved_tco2e"].provenance_mix == {}
    assert view["saved_tco2e"].status == "ok"      # events DO exist -- it is not no_source
    assert view["saved_tco2e"].event_count == 1


def test_as_of_span_is_reported_not_collapsed():
    """A block aggregating a year-old event with a fresh one must show the SPAN."""
    led = CarbonLedger()
    led.add(CarbonEvent("a", SAVED, "H1", 2.0, "grid_marginal", "estimated_from_data", "2024-01-31"))
    led.add(CarbonEvent("b", SAVED, "H1", 2.0, "grid_marginal", "estimated_from_data", "2025-12-31"))
    row = led.three_ledger_view()["saved_tco2e"]
    assert row.as_of_earliest == "2024-01-31" and row.as_of_latest == "2025-12-31"


def test_there_is_no_unlabelled_variant_of_the_headline_block():
    """R14's rule is that the figure cannot be obtained WITHOUT its clock. A second
    accessor returning bare floats would be the escape hatch a publisher reaches for.
    Guard the ABSENCE, since absence is what nothing else can test."""
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 3.0), _ev("b", SPENT, 1.0)])
    for row in led.three_ledger_view().values():
        assert not isinstance(row, float), "headline row degraded to a bare float"
        assert row.bases and row.status


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


# --- NON-FINITE FAIL-OPEN (2026-07-29, found by the E5 FRAME pass) -------------------
# NAMED DEFECT: `__post_init__` guarded tonnage with `not isinstance(...) or tco2e < 0`.
# That guard is NaN-BLIND -- `nan < 0` is False and `nan` IS a float -- so NaN and inf
# both passed validation. The damage is downstream, not local: NaN propagates through
# saved()/spent() into net(), and `nan <= 0` is ALSO False, so the fail-loud door in
# cost_per_tonne_abated was BYPASSED and the mission metric RETURNED nan as though it
# were a rate. Sibling half of the class already hardened on the D5 billing ledger.
# MUTATION (must go RED): restore the single-line guard
#     if not isinstance(self.tco2e, (int, float)) or self.tco2e < 0:
# and delete the math.isfinite check in cost_per_tonne_abated.

@pytest.mark.parametrize("bad_tonnage", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_tonnage_is_rejected_at_the_event(bad_tonnage):
    """A comparison guard cannot catch NaN, so the rejection must not BE a comparison."""
    with pytest.raises(CarbonEventMalformed):
        _ev("a", SAVED, bad_tonnage)


def test_nan_tonnage_cannot_make_the_mission_metric_return_a_number():
    """THE CONSEQUENCE, tested end-to-end rather than at the guard: a NaN tonnage must
    never produce a £/tCO2e. Before the fix this returned nan -- a non-number published
    where a rate belongs, past the very door that exists to stop exactly that."""
    with pytest.raises(CarbonEventMalformed):
        led = CarbonLedger()
        led.extend([_ev("a", SAVED, float("nan")), _ev("b", SPENT, 1.0)])
        led.cost_per_tonne_abated(500.0)


def test_cost_per_tonne_fails_loud_on_non_finite_net_directly():
    """DEFENCE IN DEPTH: the door does not delegate its own safety to a guard in another
    class. Bypass the event validator entirely (dataclasses.replace-free construction via
    object.__setattr__ is not needed -- we forge the view) and assert the door still holds."""
    class _ForgedLedger(CarbonLedger):
        def net(self):  # noqa: D102 -- stands in for any upstream that yields a non-finite net
            return float("nan")

    with pytest.raises(CarbonAbatementUnavailable):
        _ForgedLedger().cost_per_tonne_abated(500.0)


def test_boolean_tonnage_is_malformed_not_one_tonne():
    """`isinstance(True, int)` is True, so a boolean would have been accepted as 1 tCO2e --
    a type confusion that reads as a real measurement. FIRES-ON-DEFECT-ONLY control."""
    with pytest.raises(CarbonEventMalformed):
        _ev("a", SAVED, True)


def test_finite_tonnage_still_accepted():
    """The guard must fire ONLY on the defect: ordinary finite values, including 0.0 and a
    large magnitude, still construct and still derive a real rate."""
    led = CarbonLedger()
    led.extend([_ev("a", SAVED, 0.0), _ev("b", SAVED, 1e6), _ev("c", SPENT, 1.0)])
    assert led.cost_per_tonne_abated(1000.0) > 0
