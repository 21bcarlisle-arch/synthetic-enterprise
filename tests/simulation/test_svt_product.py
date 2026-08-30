"""The standard variable product is a product, not a label — and nothing is on it yet.

WHAT EACH TEST HERE NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_a_segment_is_a_cap_period_not_a_contract_year` — the defect where the "SVT product" is
    an annual term wearing a new `tariff_type`, which is precisely the label assignment
    `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused.
  * `test_the_rate_is_the_published_series_and_is_never_struck` — the defect where the rate is
    priced by a company module. No supplier prices a capped default tariff; it is handed the
    number. A struck rate here would make the cap a company decision.
  * `test_there_is_no_notice_because_nothing_ends` — the defect where the 42-day statutory
    notice, an artefact of a contract expiring, is copied onto a product that never expires.
  * `test_svt_is_gated_out_of_the_renewal_decision` — the defect where a segment boundary is
    read as a term end, so the world offers a renewal on a tariff that has none and rolls for a
    departure at a moment no household is deciding anything.
  * `test_no_account_is_on_the_svt_product_yet` — THE IMPORTANT ONE. An account on this product
    cannot leave, because the renewal decision is the only place `run_phase2b` rolls a departure
    and this product correctly has none. A book of immortal households earns more than a real
    one, which is a move in the company's favour and is what R13 exists to stop. This test is
    the interlock: assign an account to SVT before the inertia hazard exists and it reds, naming
    the hazard as what is owed.
  * `test_the_inertia_hazard_recomposes_to_the_published_annual_rate` — the defect where a
    quarterly hazard is set to the annual figure, giving four times the intended churn. Driven
    with real numbers rather than reasoned about, per the standing rule.

R15 MUTATIONS, each applied in place and reverted, with the observed result recorded rather
than the intended one:
  * `_next_cap_period_start` returns `day + 365 days`, so segments become annual ->
    **3 red**: `..._is_a_cap_period_not_a_contract_year`, `..._is_the_published_series...` (an
    annual segment reads the January rate all year and misses the Jan-2023 peak) and
    `..._delegates_rather_than_growing_a_fourth_branch` (10 segments, not 40). Recorded as
    three rather than one because a mutation firing more controls than expected is worth
    knowing: the segment length is load-bearing in three separate claims.
  * `notice_date` set to `start - 42 days` -> **1 red**, `..._no_notice_because_nothing_ends`.
  * `SVT_TARIFF_TYPE` dropped from `run_phase2b`'s `_indexed_tariff` tuple -> **1 red**,
    `..._gated_out_of_the_renewal_decision`. Nothing else moves, which is the point: without
    that control, the seam could be un-wired and every other test here would still pass.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest

from simulation.renewal_engagement import PASSIVE_CHURN_CAP
from simulation.renewals import build_renewal_schedule
from simulation.svt_product import (
    CAP_PERIOD_START_MONTHS,
    SVT_TARIFF_TYPE,
    build_svt_schedule,
)
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

PROJECT = Path(__file__).resolve().parents[2]

START = "2016-02-14"
END = "2025-12-31"


@pytest.fixture
def schedule(monkeypatch):
    """A full-record schedule with the forward curve stubbed.

    The forward is stubbed because it is the one value here that is not a property of the
    product -- it is the SIM's own cost estimate, needed by settlement and irrelevant to every
    claim below. Stubbing it keeps these tests from failing on price-record availability, which
    would be a different defect wearing this file's name.
    """
    import simulation.svt_product as sp
    monkeypatch.setattr(sp, "generate_forward_price", lambda *a, **k: 50.0)
    return build_svt_schedule("C-SVT", START, END, [])


def test_a_segment_is_a_cap_period_not_a_contract_year(schedule):
    """Segments start on cap boundaries, are contiguous, and there are ~4 a year, not 1."""
    assert len(schedule) == 40, f"expected 40 quarterly segments over a decade, got {len(schedule)}"

    # First segment starts on arrival, not on a boundary: a household is billed from the day it
    # arrived, at the rate then in force.
    assert schedule[0]["acquisition_date"] == START

    # Every subsequent one starts on a published cap boundary.
    for seg in schedule[1:]:
        start = date.fromisoformat(seg["acquisition_date"])
        assert start.day == 1 and start.month in CAP_PERIOD_START_MONTHS, (
            f"segment starts at {seg['acquisition_date']}, which is not a cap-period boundary")

    # Contiguous, with no gap and no overlap. A gap would be an unbilled household.
    for earlier, later in zip(schedule, schedule[1:]):
        assert earlier["term_end"] == later["acquisition_date"], (
            f"discontinuity: {earlier['term_end']} -> {later['acquisition_date']}")


def test_the_rate_is_the_published_series_and_is_never_struck(schedule):
    """Every segment's rate equals the published cap for its own start date."""
    for seg in schedule:
        published = get_svt_elec_rate_gbp_per_mwh(seg["acquisition_date"])
        assert seg["unit_rate_gbp_per_mwh"] == published, (
            f"{seg['acquisition_date']}: rate {seg['unit_rate_gbp_per_mwh']} is not the "
            f"published {published}")

    # And the series it tracks is the real one: the January 2023 cap ceiling is the record's
    # peak at 67p/kWh. A rate table that has lost the crisis is not the published series.
    peak = max(schedule, key=lambda s: s["unit_rate_gbp_per_mwh"])
    assert peak["acquisition_date"].startswith("2023-01"), (
        f"peak SVT rate falls in {peak['acquisition_date']}, not the Jan-2023 cap ceiling")
    assert peak["unit_rate_gbp_per_mwh"] == pytest.approx(670.0), peak


def test_there_is_no_notice_because_nothing_ends(schedule):
    """`notice_date` equals the segment start. A 42-day notice is a contract artefact."""
    for seg in schedule:
        assert seg["notice_date"] == seg["acquisition_date"], (
            f"{seg['acquisition_date']} carries a notice date of {seg['notice_date']}; a "
            "standard variable tariff gives notice of nothing because nothing expires")


def test_the_builder_delegates_rather_than_growing_a_fourth_branch():
    """`build_renewal_schedule(tariff_type='svt')` returns SVT segments, not contract terms."""
    import simulation.svt_product as sp
    original = sp.generate_forward_price
    sp.generate_forward_price = lambda *a, **k: 50.0
    try:
        out = build_renewal_schedule(
            "C-SVT", START, END, [], eac_kwh=3000, tariff_type=SVT_TARIFF_TYPE)
    finally:
        sp.generate_forward_price = original
    assert out, "delegation returned nothing"
    assert {s["tariff_type"] for s in out} == {SVT_TARIFF_TYPE}
    assert len(out) == 40, "delegation did not reach the SVT builder"


def test_svt_is_gated_out_of_the_renewal_decision():
    """`run_phase2b` treats `svt` as indexed, so no renewal is offered and no departure rolled.

    Asserted against the source rather than by running a decade sim, because the claim is about
    which branch the tariff takes and a full run would take longer than every other test in this
    file combined. The source is the thing that decides it.
    """
    src = (PROJECT / "simulation" / "run_phase2b.py").read_text()
    match = re.search(r"_indexed_tariff\s*=\s*term_tariff_type\s+in\s+\(([^)]*)\)", src)
    assert match, (
        "the indexed-tariff seam has moved; this control is keyed to a structure that no "
        "longer exists and would otherwise go quiet rather than loud")
    assert "SVT_TARIFF_TYPE" in match.group(1), (
        "`svt` is not gated out of the renewal decision, so a cap change would be read as a "
        "term end: a renewal offered on a tariff that has none, and a departure rolled at a "
        "moment no household is deciding anything")


def test_no_account_is_on_the_svt_product_yet():
    """THE INTERLOCK. Nothing may be assigned to SVT until it can leave one.

    An SVT account has no renewal decision -- correctly -- and the renewal decision is the only
    place `run_phase2b` rolls a departure. So an account moved here today never churns, and a
    book of immortal households earns more than a real one. That is a change in the company's
    favour and R13 forbids making it blind.

    When this reds, the fix is NOT to delete it. The fix is the inertia hazard named in
    `simulation/svt_product.py`, and the published fixed/SVT split printed beside the result as
    a check. Then this test is replaced by one that asserts the generated split lands in the
    published range.
    """
    from simulation.run_phase2b import ELEC_CUSTOMERS

    on_svt = [c["customer_id"] for c in ELEC_CUSTOMERS
              if c.get("tariff_type") == SVT_TARIFF_TYPE]
    assert not on_svt, (
        f"{len(on_svt)} account(s) are on the SVT product and it has no inertia hazard yet, so "
        f"they can never leave: {on_svt[:5]}. See simulation/svt_product.py, 'what is owed "
        f"before assignment'.")

    # POPULATION FLOOR, dated 2026-08-30, measured at 150 electricity legs -- 90 won by the
    # funnel, 51 drawn by the curriculum, 9 founder, per the addendum to
    # DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md. An emptied roster would satisfy the
    # assertion above by having no subjects, which is how a scanning control goes quiet rather
    # than loud. The floor sits below the measurement with headroom, never AT it: pinning it to
    # today's count would red on any lane that lands one account.
    assert len(ELEC_CUSTOMERS) >= 140, (
        f"only {len(ELEC_CUSTOMERS)} electricity accounts; the check above has lost its subjects")


def test_the_inertia_hazard_recomposes_to_the_published_annual_rate():
    """The per-segment hazard the product's docstring names must recompose to the annual anchor.

    Not yet consumed by any code -- this is the arithmetic the next step will use, pinned now so
    that the four-times-too-high version (setting the quarterly rate to the annual figure) cannot
    ship quietly. `PASSIVE_CHURN_CAP` is the world's own anchored figure for a passive roller's
    realised churn and is imported rather than re-stated.
    """
    annual = PASSIVE_CHURN_CAP
    assert annual == pytest.approx(0.10), (
        "the anchor moved; the docstring's worked figures in simulation/svt_product.py quote "
        "0.10 and must be re-derived, not silently re-based")

    per_segment = 1 - (1 - annual) ** 0.25
    assert per_segment == pytest.approx(0.0260, abs=5e-5), per_segment
    recomposed = 1 - (1 - per_segment) ** 4
    assert recomposed == pytest.approx(annual, abs=1e-9), (
        f"four segments at {per_segment} recompose to {recomposed}, not {annual}")

    # And the naive error this guards: using the annual figure per quarter.
    naive = 1 - (1 - annual) ** 4
    assert naive == pytest.approx(0.3439, abs=5e-4)
    assert naive > 3 * annual, (
        "the naive substitution is meant to be a large, obvious error; if it is not, this "
        "control is not worth its line count")
