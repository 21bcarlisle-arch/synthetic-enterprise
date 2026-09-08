"""The electricity SVT leg reads the regulation commons, and answers the CAP question.

REPLACES `test_the_elec_svt_table_agrees_with_the_published_cap.py`, whose subject no longer
exists. That file measured the drift between a hand-written table in `simulation/svt_rates.py` and
the series the commons publishes -- 11 divergent rows in 32 -- and held it from growing while the
repair was done. The repair landed: there is no post-cap table left to drift, so a control that
compares two homes has one home to compare and would be green for the rest of time.

WHAT IS CONTROLLED NOW, and each of these could not fail before:

  1. THE DELEGATION IS REAL. Perturb the commons and the accessor follows. A value assertion
     cannot tell a commons load from a literal that happens to agree today -- the `vat_book`
     repair on 2026-09-08 recorded exactly that survival, where restoring `33.0`/`145.0` passed
     every value check because the literals and the publication agreed. The mutation that kills
     this one is `_SVT_ELEC_PRECAP_PENCE_PER_KWH` growing post-cap rows back.

  2. WHICH OF THE TWO 2022-23 NUMBERS IT RETURNS. Between 2022-10-01 and 2023-06-30 the Ofgem cap
     and the instrument that bound a household's bill differ by up to 33p/kWh. `svt_rates` answers
     the CAP -- what a default tariff was priced at and what its supplier was compensated to --
     because the Energy Price Guarantee was funded by HM Treasury. Re-pointing THIS accessor at
     the binding instrument would halve the crisis quarters' unit revenue and call it fidelity.
     The control fails with that named. Since 2026-09-08 the household's own number is a separate
     named accessor over the world's receipt leg, and this control is what stops the two being
     collapsed back into one: see `test_the_hmt_receipt_leg_and_the_household_charged_rate.py`.

  3. NO INVENTED FORWARD SERIES. The table used to carry "Extrapolated 2026+ -- moderate decline
     as renewables penetration rises" across 2026-2029, standing exactly where the commons
     publishes Ofgem's own cap level model. Past the published schedule the answer must be the
     last published window, which is the commons' standing-instrument rule, not a curve.

  4. THE PRE-CAP YEARS ARE NOT DELEGATED. Before 2019 there was no cap, and an accessor that
     delegated anyway would answer a 2016 question with a 2019 law.

  5. THE SEGMENT BOUNDARIES COVER THE PUBLISHED ONES. `simulation/svt_product.py` used to carry
     its own copy of `CAP_PERIOD_START_MONTHS` under a comment claiming
     `test_the_segment_starts_match_the_published_series` guarded the duplication. That test has
     never existed in this tree. The duplication is now deleted rather than guarded, and what is
     controlled instead is the property nothing checked: that the months chosen cover every
     boundary the commons actually publishes.

Provenance, including a prediction this work refuted and a prediction it confirmed:
`docs/staging/SEAT_RESULT_THE_ELECTRICITY_SVT_TABLE_IS_A_SECOND_HOME_2026-09-08.md` and
`docs/staging/PREREG_WHAT_THE_ELECTRICITY_SVT_LEG_READING_THE_COMMONS_MOVES_2026-09-08.md`.
"""
from __future__ import annotations

from datetime import date

import pytest

import simulation.price_cap_enforcement as pce
from simulation.svt_rates import (
    _SVT_ELEC_PRECAP_PENCE_PER_KWH,
    CAP_PERIOD_START_MONTHS,
    get_svt_elec_rate_gbp_per_mwh,
)

#: The three windows where an EPG level is published, i.e. where "the cap" and "what the household
#: was charged" are different quantities. Derived from the commons rather than typed, so a fourth
#: published EPG window joins this control instead of slipping past it.
_EPG_WINDOWS = [w for w in pce.PUBLISHED_CAP_WINDOWS if "elec_epg" in w]


def test_the_epg_windows_exist_at_all():
    """REACHABILITY, first: every assertion about the cap-versus-binding split passes vacuously
    over an empty `_EPG_WINDOWS`, and a commons that stopped publishing the EPG overlay would make
    the most expensive control in this file silently green.
    """
    assert _EPG_WINDOWS, (
        "the commons publishes no `elec_epg` overlay at all; the cap-versus-binding distinction "
        "this module exists to hold is unreachable and every control below is vacuous"
    )
    assert any(
        w["elec"] - w["elec_epg"] > 100.0 for w in _EPG_WINDOWS
    ), "no published window has a cap/EPG gap above 100 GBP/MWh; the split is not material here"


def test_the_accessor_follows_a_moved_commons():
    """DEFECT: the leg looks delegated and is a literal. A value check cannot tell those apart --
    move the publication and require the answer to move with it.
    """
    when = "2024-07-01"
    before = get_svt_elec_rate_gbp_per_mwh(when)
    target = pce._window_for(date.fromisoformat(when))
    original = target["elec"]
    try:
        target["elec"] = original + 37.0
        after = get_svt_elec_rate_gbp_per_mwh(when)
    finally:
        target["elec"] = original
    assert after == pytest.approx(before + 37.0), (
        f"the commons moved by +37.0 and the accessor answered {after} against {before}: the "
        "electricity leg is not reading the publication, whatever it says it does"
    )
    assert get_svt_elec_rate_gbp_per_mwh(when) == pytest.approx(before), "fixture leaked"


def test_the_pre_cap_years_do_not_follow_the_commons():
    """The other side of the same property: 2016-2018 predate the cap and must NOT move when the
    publication does. A delegation that reached back before the law would answer a 2016 question
    with a 2019 one, and would still pass the test above.
    """
    when = "2017-06-01"
    before = get_svt_elec_rate_gbp_per_mwh(when)
    first = pce.PUBLISHED_CAP_WINDOWS[0]
    original = first["elec"]
    try:
        first["elec"] = original + 37.0
        after = get_svt_elec_rate_gbp_per_mwh(when)
    finally:
        first["elec"] = original
    assert after == pytest.approx(before)
    assert before == pytest.approx(_SVT_ELEC_PRECAP_PENCE_PER_KWH[2017] * 10)


@pytest.mark.parametrize("fuel", ["electricity", "gas"])
def test_it_answers_the_cap_and_not_what_the_household_was_charged(fuel):
    """DEFECT: an accessor is pointed at the binding instrument because 34p is 'what an SVT
    household paid', and the crisis quarters lose half their unit revenue.

    BOTH FUELS, in one control over the whole partition, because the defect this replaces was
    precisely that they disagreed: until 2026-09-08 the gas leg read the binding instrument and
    the electricity leg read a table carrying the cap, so one field answered two questions in
    exactly the three quarters where the two differ. A per-fuel test would have been green on
    each of them separately.

    Keyed to the property rather than to 674.7: for every window the commons publishes an EPG
    level for, the answer must be the cap row and must NOT be the binding one.
    """
    from simulation.svt_rates import get_svt_gas_rate_gbp_per_mwh

    ask = get_svt_elec_rate_gbp_per_mwh if fuel == "electricity" else get_svt_gas_rate_gbp_per_mwh
    for w in _EPG_WINDOWS:
        when = w["from"]
        got = ask(when.isoformat())
        cap = pce.ofgem_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, when)
        binding = pce.binding_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, when)
        assert got == pytest.approx(cap), f"{fuel} {when}: expected the cap {cap}, got {got}"
        assert got != pytest.approx(binding), (
            f"{fuel} {when}: `svt_rates` returns the BINDING instrument ({binding}) rather than "
            "the Ofgem cap. The Energy Price Guarantee reduced the household's bill and HM "
            "Treasury paid the supplier the difference -- see "
            "`simulation/price_cap_enforcement.hmt_epg_receipt_gbp_per_mwh`, the world's own "
            "receipt leg, wired 2026-09-08. Answering the binding instrument HERE takes revenue "
            "the real supplier received out of the book; the household's number has its own "
            "accessor, `get_svt_elec_rate_charged_to_household_gbp_per_mwh`, and its own "
            "controls in `test_the_hmt_receipt_leg_and_the_household_charged_rate.py`."
        )


def test_past_the_published_schedule_the_last_window_stands():
    """DEFECT: an invented forward curve standing where a publication exists -- the shape this
    whole atom was drawn to close. Until 2026-09-08 this module carried a declining 2026-2029
    series under the comment "moderate decline as renewables penetration rises", 1.69p/kWh away
    from what the commons publishes for 2026-01 and reaching 4p/kWh away by 2029.
    """
    last = pce.PUBLISHED_CAP_WINDOWS[-1]
    expected = last["elec"]
    beyond = [f"{y}-{m:02d}-15" for y in range(last["to"].year + 1, last["to"].year + 4)
              for m in CAP_PERIOD_START_MONTHS]
    assert beyond, "no dates past the published schedule were checked"
    answers = {d: get_svt_elec_rate_gbp_per_mwh(d) for d in beyond}
    assert all(v == pytest.approx(expected) for v in answers.values()), (
        f"past the last published window ({last['to']}) the standing instrument must still bind "
        f"at {expected}; got a varying series instead: {answers}"
    )


def test_the_segment_start_months_cover_every_published_boundary():
    """DEFECT: `svt_product` bills in segments whose starts miss a real cap change, so a household
    is billed one quarter's rate through a window in which the law changed.

    This is the control `simulation/svt_product.py` claimed for its duplicated tuple and never
    had. The duplication is gone; the property is not tautological because the months are a fixed
    tuple and the boundaries come from the commons.
    """
    boundaries = sorted({w["from"].month for w in pce.PUBLISHED_CAP_WINDOWS})
    assert boundaries, "the commons publishes no windows"
    missing = [m for m in boundaries if m not in CAP_PERIOD_START_MONTHS]
    assert not missing, (
        f"the commons publishes cap changes starting in month(s) {missing}, which "
        f"`CAP_PERIOD_START_MONTHS` = {CAP_PERIOD_START_MONTHS} does not begin a billing segment "
        "on. A household would be billed across a boundary at the wrong rate."
    )


def test_the_two_fuels_are_on_one_basis_and_both_delegate():
    """The reason the electricity leg was repaired to look like the gas leg rather than the other
    way round: both must answer inc-VAT, from the commons, for the capped years. A fuel that
    stayed a table would reintroduce the drift on its own timetable.
    """
    from simulation.svt_rates import get_svt_gas_rate_gbp_per_mwh

    when = "2025-04-01"
    d = date.fromisoformat(when)
    assert get_svt_elec_rate_gbp_per_mwh(when) == pytest.approx(
        pce.ofgem_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", d)
    )
    assert get_svt_gas_rate_gbp_per_mwh(when) == pytest.approx(
        pce.ofgem_cap_unit_rate_gbp_per_mwh_inc_vat("gas", d)
    )
    # ...and the post-cap electricity table is gone, which is what makes (1) above load-bearing.
    assert set(_SVT_ELEC_PRECAP_PENCE_PER_KWH) == {2016, 2017, 2018}, (
        "a post-cap year has reappeared in the pre-cap table; the second home is back"
    )
