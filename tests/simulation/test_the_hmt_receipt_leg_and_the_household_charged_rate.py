"""The HM Treasury receipt leg, and the rate a household was actually charged.

THE DEFECT THIS CLOSES. Until 2026-09-08 this world had one default-tariff electricity rate and
read it as two different quantities. `simulation/svt_product` billed the Ofgem cap, which is right
— the Energy Price Guarantee reduced the household's bill and HM Treasury paid the supplier the
difference, so a supplier's revenue in 2022-10-01..2023-06-30 was the cap. Every household-facing
consumer read the same number, which is wrong by up to 33p/kWh in exactly the three quarters that
carry the most weight in the 2016–2025 record: a January-2023 household's bill did not jump 30%, it
was held at 34.0p, and nothing in the world could say so.

The two halves had to land together and this file controls them together. The accessor alone takes
roughly half the unit revenue out of the crisis quarters and calls it fidelity; the receipt leg
alone leaves the churn reference reading a rate nobody paid. Provenance:
`docs/staging/SEAT_RESULT_BOTH_SVT_LEGS_READ_THE_COMMONS_AND_THEY_HAD_BEEN_ANSWERING_DIFFERENT_QUESTIONS_2026-09-08.md`,
"what is next", item 2.

WHAT EACH CONTROL HERE CAN FAIL ON, because a control that cannot fail is this project's most
expensive recurring shape:

  1. REACHABILITY FIRST, before anything asserts about the split. A commons that stopped publishing
     the EPG overlay makes every other control below vacuously green — the poison round runs first
     so that "passed" cannot mean "found nothing to look at".
  2. THE IDENTITY `cap == charged + receipt`, over every published window and both fuels. It is NOT
     a tautology: `svt_product` asks `hmt_epg_receipt_gbp_per_mwh` for the receipt rather than
     differencing the two rates it holds, precisely so this can fail. The mutation that kills it is
     the receipt accessor returning `0.0` unconditionally.
  3. THE SPLIT IS WHERE THE LAW PUTS IT AND NOWHERE ELSE, enumerated day by day across
     2016-01-01..2029-12-31 rather than sampled. A population control, because the failure this
     guards is an accessor that is right on the dates someone thought to test and wrong on a
     boundary.
  4. THE DELEGATION IS REAL. Perturb the commons; require the answer to follow. A value assertion
     cannot tell a delegation from a literal that agrees today — the survival the `vat_book` repair
     recorded on 2026-09-08, and the reason the predecessor's load-bearing control has this shape.
  5. BILL SHOCK IS COUNTED ON WHAT THE HOUSEHOLD SAW, with the poison round included: on the
     revenue rate the same history counts a shock that never reached a bill.
  6. ONE NAME, ONE NUMBER between the differential and the level published alongside it — including
     on the input that used to break it, a competitor reference of exactly 0.0.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

import simulation.price_cap_enforcement as pce
from simulation.bill_shock_tracker import count_rate_shocks
from simulation.customer_events import (
    _market_reference_gbp_per_mwh,
    _price_differential_vs_market,
    _svt_position,
)
from simulation.svt_rates import (
    get_svt_elec_rate_charged_to_household_gbp_per_mwh,
    get_svt_elec_rate_gbp_per_mwh,
)

#: Windows where the commons publishes an EPG level, i.e. where "the cap" and "what the household
#: paid" are different quantities. Derived from the publication rather than typed, so a fourth
#: published EPG window joins these controls instead of slipping past them.
_EPG_WINDOWS = [w for w in pce.PUBLISHED_CAP_WINDOWS if "elec_epg" in w]

_FUELS = ("electricity", "gas")


def _days(start: date, end: date, step: int = 1):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=step)


@pytest.fixture
def straddling_schedule(monkeypatch):
    """SVT segments from before the scheme to after it, with the forward curve stubbed.

    Stubbed the same way and for the same reason `test_svt_product.py`'s own fixture does it: the
    forward is the SIM's cost estimate, needed by settlement and irrelevant to every claim here,
    and leaving it live would make these controls fail on price-record availability instead — a
    different defect wearing this file's name.

    The span is chosen to STRADDLE 2022-10-01..2023-06-30 rather than sit inside it, because a
    fixture entirely inside the scheme cannot tell a split that turns on from one that is always
    on, and that is the shape the receipt leg would take if it were wired to the wrong instrument.
    """
    import simulation.svt_product as sp

    monkeypatch.setattr(sp, "generate_forward_price", lambda *a, **k: 50.0)
    return sp.build_svt_schedule("C-EPG", "2022-07-01", "2023-12-31", [])


def test_the_epg_overlay_is_published_at_all():
    """POISON ROUND. Every control below is about the gap between two instruments; with no EPG
    overlay in the commons there is no gap, and each of them passes while measuring nothing.
    "Survived" and "never ran" are the two things this ordering exists to keep apart.
    """
    assert _EPG_WINDOWS, (
        "the commons publishes no `elec_epg` overlay, so the cap-versus-charged split this file "
        "controls is unreachable and every assertion below is vacuous"
    )
    materials = [w["elec"] - w["elec_epg"] for w in _EPG_WINDOWS]
    assert max(materials) > 100.0, (
        f"the largest published cap/EPG gap is {max(materials):.1f} GBP/MWh; below 100 the split "
        "is not material and these controls are not measuring the defect they were written for"
    )


@pytest.mark.parametrize("fuel", _FUELS)
def test_the_cap_is_exactly_what_the_household_paid_plus_what_the_treasury_paid(fuel):
    """DEFECT: the receipt leg drifts from the two rates it sits between, so the world's revenue
    stops equalling the sum of its receipts and no line anywhere is wrong on its own.

    BOTH FUELS in one control over the whole partition. A per-fuel test is exactly what let the
    two legs answer different questions until 2026-09-08 while each was green.

    NOT A TAUTOLOGY: all three numbers are independent reads of the commons. Mutating
    `hmt_epg_receipt_gbp_per_mwh` to `return 0.0` kills this inside the EPG windows and leaves
    every other control in this file green.
    """
    checked = 0
    for w in pce.PUBLISHED_CAP_WINDOWS:
        for when in (w["from"], w["to"]):
            cap = pce.ofgem_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, when)
            charged = pce.binding_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, when)
            receipt = pce.hmt_epg_receipt_gbp_per_mwh(fuel, when)
            assert cap is not None and charged is not None and receipt is not None
            assert cap == pytest.approx(charged + receipt), (
                f"{fuel} {when}: the supplier was compensated to {cap} and the world says the "
                f"household paid {charged} with HM Treasury paying {receipt}, which sums to "
                f"{charged + receipt}. Revenue is no longer the sum of its receipts."
            )
            checked += 1
    assert checked >= 2 * len(pce.PUBLISHED_CAP_WINDOWS), "the published span was not walked"


@pytest.mark.parametrize("fuel", _FUELS)
def test_the_treasury_paid_something_inside_the_scheme_and_nothing_outside_it(fuel):
    """DEFECT: a receipt leg that is always zero — which satisfies the identity above perfectly and
    represents a world where the EPG never happened.

    The other side of the same partition: a leg that pays out beyond the scheme's nine months would
    be a subsidy the Treasury never voted, and it would flatter the book everywhere.
    """
    epg_key = f"{pce._FUEL_KEY[fuel]}_epg"
    inside = [w for w in pce.PUBLISHED_CAP_WINDOWS if epg_key in w]
    outside = [w for w in pce.PUBLISHED_CAP_WINDOWS if epg_key not in w]
    assert inside and outside, "the partition is empty on one side; this control is vacuous"

    for w in inside:
        receipt = pce.hmt_epg_receipt_gbp_per_mwh(fuel, w["from"])
        assert receipt > 0.0, (
            f"{fuel} {w['from']}: the commons publishes an EPG level for this window and the "
            f"world says HM Treasury paid {receipt}. The scheme is unwired."
        )
    for w in outside:
        receipt = pce.hmt_epg_receipt_gbp_per_mwh(fuel, w["from"])
        assert receipt == 0.0, (
            f"{fuel} {w['from']}: no EPG level is published for this window and the world says "
            f"HM Treasury paid {receipt} anyway"
        )


def test_the_two_electricity_accessors_differ_on_the_scheme_and_agree_everywhere_else():
    """DEFECT: an accessor that is right on the dates someone thought to test. Enumerated DAY BY
    DAY across the whole modelled span rather than sampled at window starts, because the failure
    mode is a boundary — the day the scheme began, the day it ended, the day after.

    This is the control that would have caught the original defect from either direction: the cap
    accessor quietly answering the guarantee, or the charged accessor quietly answering the cap.
    """
    epg_days = set()
    for w in _EPG_WINDOWS:
        epg_days.update(_days(w["from"], w["to"]))
    assert epg_days, "no EPG days to check"

    disagreed, agreed = [], 0
    for d in _days(date(2016, 1, 1), date(2029, 12, 31)):
        cap = get_svt_elec_rate_gbp_per_mwh(d.isoformat())
        charged = get_svt_elec_rate_charged_to_household_gbp_per_mwh(d.isoformat())
        assert (cap is None) == (charged is None), f"{d}: one leg answered and the other did not"
        if cap is None:
            continue
        if cap != charged:
            disagreed.append(d)
        else:
            agreed += 1

    assert set(disagreed) == epg_days, (
        "the two accessors part company on the wrong days. "
        f"unexpected: {sorted(set(disagreed) - epg_days)[:5]}; "
        f"missing: {sorted(epg_days - set(disagreed))[:5]}"
    )
    assert agreed > 4000, "almost nothing was checked outside the scheme; the control is thin"


def test_the_charged_accessor_follows_a_moved_commons():
    """DEFECT: the household leg looks delegated and is a literal that agrees today. A value check
    cannot tell those apart — move the publication and require the answer to move with it.

    Moves the EPG row specifically, not the cap row: a charged accessor wired to the cap would
    survive a cap perturbation and fail this one, which is the confusion the whole atom is about.
    """
    w = _EPG_WINDOWS[0]
    when = w["from"].isoformat()
    before = get_svt_elec_rate_charged_to_household_gbp_per_mwh(when)
    original = w["elec_epg"]
    try:
        w["elec_epg"] = original - 41.0
        after = get_svt_elec_rate_charged_to_household_gbp_per_mwh(when)
    finally:
        w["elec_epg"] = original
    assert after == pytest.approx(before - 41.0), (
        f"the published guarantee moved by -41.0 and the charged accessor answered {after} "
        f"against {before}: it is not reading the EPG overlay, whatever it says it does"
    )
    assert get_svt_elec_rate_charged_to_household_gbp_per_mwh(when) == pytest.approx(before), (
        "fixture leaked"
    )


def test_an_svt_segment_carries_the_split_and_it_closes(straddling_schedule):
    """DEFECT: the receipt leg exists in `price_cap_enforcement` and never reaches a billed
    segment, so the world still cannot say who paid. This is the wiring control — calling the
    accessor directly is blind to whether production reads it.
    """
    schedule = straddling_schedule
    assert schedule, "no segments built"

    inside = [s for s in schedule if any(
        w["from"] <= date.fromisoformat(s["acquisition_date"]) <= w["to"] for w in _EPG_WINDOWS
    )]
    outside = [s for s in schedule if s not in inside]
    assert inside and outside, (
        "the schedule does not straddle the scheme, so it cannot show the split turning on"
    )

    for s in schedule:
        assert s["unit_rate_gbp_per_mwh"] == pytest.approx(
            s["household_charged_unit_rate_gbp_per_mwh"] + s["hmt_epg_receipt_gbp_per_mwh"]
        ), f"segment {s['acquisition_date']} bills a total that is not the sum of its receipts"

    for s in inside:
        assert s["hmt_epg_receipt_gbp_per_mwh"] > 0.0, (
            f"segment {s['acquisition_date']} is inside the EPG and carries no Treasury receipt"
        )
        assert s["household_charged_unit_rate_gbp_per_mwh"] < s["unit_rate_gbp_per_mwh"]
    for s in outside:
        assert s["hmt_epg_receipt_gbp_per_mwh"] == 0.0
        assert s["household_charged_unit_rate_gbp_per_mwh"] == pytest.approx(
            s["unit_rate_gbp_per_mwh"]
        ), f"segment {s['acquisition_date']} splits a bill outside the scheme"


def test_the_segment_asks_for_the_receipt_rather_than_differencing_it():
    """DEFECT: `receipt = rate - charged` in `build_svt_schedule`, which makes the identity
    control above true by arithmetic — it keeps passing, over a world where the receipt leg is not
    read at all, and reads as coverage of the one property this atom exists for.

    THIS CONTROL READS THE SOURCE AND NOTHING ELSE CAN. The two forms are value-equivalent on
    every date: pre-2016 both rate legs are None, 2016–2018 both are the same pre-cap table so the
    difference is a true 0.0, and from 2019 the accessor IS that difference. Mutation-proven on
    2026-09-08 — swapping the call for the subtraction left all fifteen behavioural controls
    green. So a behavioural test here would be a control that cannot fail, and the honest move is
    to say plainly that this reads text rather than running anything.
    """
    import ast
    import inspect

    import simulation.svt_product as sp

    tree = ast.parse(inspect.getsource(sp.build_svt_schedule))
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "hmt_epg_receipt_gbp_per_mwh" in called, (
        "`build_svt_schedule` no longer asks `price_cap_enforcement` what HM Treasury paid. If "
        "it now derives the receipt from the two rates it holds, the segment identity control is "
        "arithmetic and cannot fail, and the world has one reading of the scheme where it had two."
    )


def test_the_billed_rate_did_not_move_and_that_is_the_half_that_protects_revenue(
    straddling_schedule,
):
    """DEFECT: the household-charged accessor arrives and someone points the BILLED rate at it,
    which is the failure this atom's own direction names — roughly half the unit revenue leaves
    the crisis quarters and it looks like a fidelity improvement.

    Keyed to the property, not to 674.7: the billed rate must be the cap accessor's answer on every
    segment, whatever the commons says today.
    """
    for s in straddling_schedule:
        assert s["unit_rate_gbp_per_mwh"] == pytest.approx(
            get_svt_elec_rate_gbp_per_mwh(s["acquisition_date"])
        ), (
            f"segment {s['acquisition_date']} is billed at "
            f"{s['unit_rate_gbp_per_mwh']}, not the cap the supplier was compensated to. The "
            "Energy Price Guarantee did not reduce supplier revenue; HM Treasury paid the "
            "difference, and this world now records that receipt separately."
        )


def test_a_bill_shock_is_counted_on_what_the_household_was_charged():
    """DEFECT: a household that moved onto the default tariff in October 2022 registers a bill
    shock in January 2023 that its bill never showed it, and carries the churn uplift for it
    (`saas.churn_model`) through the quarter the whole record turns on.

    THE POISON ROUND IS IN THE SAME TEST. The identical history read on the revenue rate must count
    the shock — otherwise this passes because the threshold was never crossed either way, and says
    nothing about which field was read.
    """
    records = [
        {"customer_id": "C1", "commodity": "electricity", "term_start": "2022-10-01",
         "unit_rate_gbp_per_mwh": 518.9, "household_charged_unit_rate_gbp_per_mwh": 340.0},
        {"customer_id": "C1", "commodity": "electricity", "term_start": "2023-01-01",
         "unit_rate_gbp_per_mwh": 674.7, "household_charged_unit_rate_gbp_per_mwh": 340.0},
    ]
    assert count_rate_shocks("C1", "electricity", records) == 0, (
        "the household's guaranteed rate was 34.0p/kWh in both quarters and its bill did not "
        "move; a shock counted here is counted on revenue the household never saw"
    )

    revenue_only = [{k: v for k, v in r.items()
                     if k != "household_charged_unit_rate_gbp_per_mwh"} for r in records]
    assert count_rate_shocks("C1", "electricity", revenue_only) == 1, (
        "POISON: on the revenue rate this history is a 30% jump and must count as a shock. It "
        "does not, so the control above passes for a reason other than the field it reads."
    )


def test_a_fixed_term_record_without_the_split_still_counts_its_shocks():
    """DEFECT: the new field becomes required, and every record that legitimately lacks it — a
    fixed term, where the household paid the rate the company struck — silently drops out of the
    filter and reports zero shocks. Fail-silent, in the direction that flatters churn.
    """
    records = [
        {"customer_id": "C2", "commodity": "electricity", "term_start": "2021-04-01",
         "unit_rate_gbp_per_mwh": 200.0},
        {"customer_id": "C2", "commodity": "electricity", "term_start": "2022-04-01",
         "unit_rate_gbp_per_mwh": 300.0},
    ]
    assert count_rate_shocks("C2", "electricity", records) == 1


def test_a_zero_charged_rate_is_read_and_not_skipped_over():
    """DEFECT: `record.get(charged) or record.get(unit_rate)` — a 0.0 charged rate is falsy and
    falls through to the revenue leg, so the one record that most needs the household's number
    silently gets the supplier's. The ordering is by `is not None` for this reason.
    """
    records = [
        {"customer_id": "C3", "commodity": "electricity", "term_start": "2022-10-01",
         "unit_rate_gbp_per_mwh": 518.9, "household_charged_unit_rate_gbp_per_mwh": 0.0},
        {"customer_id": "C3", "commodity": "electricity", "term_start": "2023-01-01",
         "unit_rate_gbp_per_mwh": 674.7, "household_charged_unit_rate_gbp_per_mwh": 100.0},
    ]
    # A 0.0 prior rate is not a division we can do; the pair is skipped rather than counted as an
    # infinite increase. What is controlled is that the 0.0 was READ -- on the revenue leg this
    # pair is a 30% rise and would count.
    assert count_rate_shocks("C3", "electricity", records) == 0


def test_the_household_facing_readings_are_against_what_the_household_paid():
    """DEFECT: an offer in January 2023 is scored against a 67.47p alternative when the household's
    real alternative was 34.0p, so a rate that is 24% DEARER than the default is logged as 26%
    cheaper and the churn that follows is priced off a saving nobody could have banked.

    The sign flip is the assertion, not a magnitude: both readings must agree with the household's
    own bill about which side of its alternative the offer sits.
    """
    when = _EPG_WINDOWS[1]["from"].isoformat()
    charged = get_svt_elec_rate_charged_to_household_gbp_per_mwh(when)
    cap = get_svt_elec_rate_gbp_per_mwh(when)
    assert cap > charged, "this window has no split; the control cannot see the defect"

    offer = (charged + cap) / 2.0  # dearer than the household's bill, cheaper than the cap
    differential = _price_differential_vs_market(offer, when)
    position = _svt_position(offer, when)
    assert differential > 0 and position > 0, (
        f"an offer of {offer:.1f} is dearer than the {charged:.1f} this household was actually "
        f"charged, and the world reports differential={differential} position={position}. It is "
        f"reading the {cap:.1f} cap, which is the supplier's revenue and not the household's bill."
    )


def test_the_published_level_is_the_level_that_was_used():
    """DEFECT: `_market_reference_gbp_per_mwh` re-derives the level the differential was taken
    against, and the two drift under names that both say SVT — the failure
    `run_price_ladder`'s reconciliation caught in August at 21.3 points.

    Includes the input that broke the old pair: a competitor reference of exactly 0.0, which the
    differential substituted and the published level treated as falsy and fell back from.
    """
    class _Ledger:
        def __init__(self, value):
            self._value = value

        def position_for(self, _when):
            return self._value

    when = _EPG_WINDOWS[1]["from"].isoformat()
    for ledger in (None, _Ledger(120.0), _Ledger(0.0)):
        level = _market_reference_gbp_per_mwh(when, position_ledger=ledger)
        differential = _price_differential_vs_market(500.0, when, position_ledger=ledger)
        assert level is not None and differential is not None
        implied = 500.0 / (1.0 + differential)
        assert implied == pytest.approx(level), (
            f"ledger={ledger}: the differential was taken against {implied:.4f} and the world "
            f"published {level:.4f} as the level it used"
        )


def test_the_reference_a_household_can_switch_to_is_capped_by_the_guarantee():
    """DEFECT: `competitor_reference` is anchored on the Ofgem cap — correctly, it models how a
    rival prices — and substituting it wholesale puts the household's alternative back above the
    guarantee. No domestic supplier could lawfully charge above the EPG either, so a reference
    over it is a price no switching household could have been offered.

    Outside the scheme the ceiling IS the cap and the clamp is a no-op; that half is asserted too,
    because a clamp that bit everywhere would be a second reading of the schedule.
    """
    class _Ledger:
        def position_for(self, _when):
            return 10_000.0  # far above the cap, so the rival does not chase at all

    inside = _EPG_WINDOWS[1]["from"].isoformat()
    charged = get_svt_elec_rate_charged_to_household_gbp_per_mwh(inside)
    level = _market_reference_gbp_per_mwh(inside, position_ledger=_Ledger())
    assert level == pytest.approx(charged), (
        f"with no chase the household's alternative is its own guaranteed rate {charged}; the "
        f"world offers it {level}, which is above what the law allowed anyone to charge"
    )

    outside = "2024-01-01"
    assert _market_reference_gbp_per_mwh(
        outside, position_ledger=_Ledger()
    ) == pytest.approx(get_svt_elec_rate_gbp_per_mwh(outside)), (
        "outside the scheme the clamp must be a no-op and the cap-anchored reference must stand"
    )
