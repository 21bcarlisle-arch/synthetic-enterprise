#!/usr/bin/env python3
"""R15 proof for the competitor reference (director's C2, 2026-08-28):

    "no module models a rival supplier; the comparison price is the published SVT series read by
     date from a quarterly table... nothing in the world responds to what the company does.
     Nobody undercuts it, nobody defends, nobody targets its book."

THE KILLER MUTATION IS ALSO THE WORLD AS IT STOOD YESTERDAY, which is the strongest form a
mutation can take: setting `chase = 0` reproduces the pre-2026-08-28 behaviour exactly, so any
test that survives it is a test that would have passed on a world with no rival in it. Every
responsiveness assertion below is driven at both `chase = 0` and `chase = CHASE_PER_QUARTER` and
must SEPARATE them.

The second direction, and the one that costs more if it is wrong: this must not move the
historical replay. Every calibration in the churn model was taken against a reference of
`svt(t)`, so a company at or above the cap must get `svt(t)` back to the last decimal, for every
value of chase.
"""
from __future__ import annotations

import pytest

from simulation import competitor_reference as cr
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

DATE = "2019-06-01"
CAP = get_svt_elec_rate_gbp_per_mwh(DATE)


# ---------------------------------------------------------------------------
# THE REPLAY MUST NOT MOVE
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("chase", [0.0, 0.25, cr.CHASE_PER_QUARTER, 1.0])
def test_MUTATION_a_company_AT_the_cap_gets_the_cap_back_for_every_chase(chase):
    """The load-bearing property. `market_switching_multiplier` is calibrated FROM the same
    savings series a market-level reference would be derived from, and `customer_events`
    multiplies the two — so the differential is a DEVIATION from the typical customer and a
    customer at the cap IS the typical customer. A reference that moved off the cap here would
    charge the era's savings twice and raise churn across the whole book while looking like a
    fidelity improvement."""
    assert cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=CAP, chase=chase) == pytest.approx(CAP)


def test_a_company_with_NO_observed_position_gets_the_cap():
    """A rival that has never seen this supplier prices at the market. This is the state of every
    run before its first full quarter, and it must be the pre-module behaviour exactly."""
    assert cr.competitor_reference_rate_gbp_per_mwh(DATE) == pytest.approx(CAP)


def test_MUTATION_chase_zero_reproduces_the_world_as_it_stood(dict_free=None):
    """The killer mutation, stated as a test in its own right: at chase=0 the reference IS the
    published cap at every company position, which is what every measurement taken before
    2026-08-28 was taken against."""
    for position in (0.5, 0.7, 0.9, 1.0, 1.2, 2.0):
        assert cr.competitor_reference_rate_gbp_per_mwh(
            DATE, company_rate_gbp_per_mwh=CAP * position, chase=0.0
        ) == pytest.approx(CAP), f"chase=0 moved the reference at position {position}"


# ---------------------------------------------------------------------------
# IT DEFENDS
# ---------------------------------------------------------------------------

def _gap(company: float, chase: float) -> float:
    ref = cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=company, chase=chase)
    return (company - ref) / ref


def test_MUTATION_a_price_ADVANTAGE_DECAYS_and_that_is_the_whole_point():
    """C2's "nobody defends". A company 10% under the cap holds -10% against a frozen reference
    and must hold materially less against one that follows it down."""
    frozen = _gap(CAP * 0.9, chase=0.0)
    defended = _gap(CAP * 0.9, chase=cr.CHASE_PER_QUARTER)
    assert frozen == pytest.approx(-0.10)
    assert defended > frozen + 0.02, (
        f"the reference did not defend: {frozen:.3f} -> {defended:.3f}. This is the assertion "
        f"the whole atom exists to make true, and chase=0 must not pass it."
    )


def test_a_DEEPER_undercut_is_defended_HARDER_in_absolute_terms():
    """Monotonicity in the right direction: the further the company undercuts, the more ground
    the rival gives up to follow — a rival that responded identically to a 5% and a 30% undercut
    would be a constant wearing a function's clothes."""
    shallow = CAP * 0.95 - cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=CAP * 0.95, chase=cr.CHASE_PER_QUARTER)
    deep = CAP * 0.70 - cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=CAP * 0.70, chase=cr.CHASE_PER_QUARTER)
    assert deep < shallow < 0
    assert abs(deep) > abs(shallow)


def test_MUTATION_the_chase_is_ONE_SIDED_and_over_pricing_buys_NO_relief():
    """THE ERROR THE FIRST DRAFT MADE, kept as a test because it was plausible and wrong. A
    two-sided chase pulled the reference UP toward an expensive company: a 20% over-cap position
    saw its own felt gap fall from +29.7% to +20.0%, i.e. over-pricing bought relief. A rival is
    already cheaper and already winning that customer; raising its price would surrender the
    position it is winning on."""
    for chase in (0.0, cr.CHASE_PER_QUARTER, 1.0):
        assert cr.competitor_reference_rate_gbp_per_mwh(
            DATE, company_rate_gbp_per_mwh=CAP * 1.2, chase=chase) == pytest.approx(CAP)


# ---------------------------------------------------------------------------
# IT CANNOT FOLLOW BELOW ITS OWN COSTS
# ---------------------------------------------------------------------------

def test_MUTATION_the_rival_STOPS_FOLLOWING_at_its_cost_floor():
    """What stops this being an unbounded dial. Below the floor no real rival could match and
    live, so a company pricing under it KEEPS its advantage — which is a different and much more
    interesting outcome than 'the world always catches you'."""
    wholesale = 40.0
    floor = cr.cost_floor_gbp_per_mwh(DATE, wholesale)
    very_cheap = floor * 0.5
    ref = cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=very_cheap, chase=1.0,
        wholesale_gbp_per_mwh=wholesale)
    assert ref == pytest.approx(floor)
    assert ref > very_cheap, "the rival followed a company below its own costs"


def test_the_floor_carries_a_real_margin_over_a_real_cost_stack():
    """Not a hardcoded number: policy and network come from the world's own published stack, and
    the margin is a named curriculum value on top."""
    from simulation.policy_costs import (
        get_electricity_network_cost_per_mwh,
        get_electricity_policy_cost_per_mwh,
    )

    wholesale = 55.0
    stack = (wholesale
             + get_electricity_policy_cost_per_mwh(DATE)
             + get_electricity_network_cost_per_mwh(DATE, segment="resi"))
    assert cr.cost_floor_gbp_per_mwh(DATE, wholesale) == pytest.approx(
        stack * (1 + cr.MIN_RETAIL_MARGIN_PCT))
    assert stack > wholesale, "the non-commodity stack contributed nothing"


def test_MUTATION_without_a_wholesale_price_there_is_NO_floor_and_that_is_reported_not_hidden():
    """FAIL-OPEN is the pattern R15 names, so the no-floor path is asserted deliberately rather
    than left to be discovered: a caller that omits wholesale gets an unfloored reference. It is
    legal (the floor is a refinement, not the mechanism) and it is exactly why the wiring test
    below asserts the live path DOES pass one."""
    unfloored = cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=1.0, chase=1.0)
    assert unfloored < cr.cost_floor_gbp_per_mwh(DATE, 40.0)


# ---------------------------------------------------------------------------
# THE DIAGNOSTICS ARE NOT IN THE REFERENCE PATH
# ---------------------------------------------------------------------------

def test_the_historical_discount_is_derived_from_the_real_series_and_can_go_NEGATIVE():
    """2022 is the year the source series exists to record: fixed deals cost MORE than the
    default, there was nowhere cheaper to go, and switching collapsed to 3-4% on the highest
    bills ever seen. A discount that could not go negative would model a world in which a crisis
    makes rivals cheaper."""
    assert cr.historical_discount_pct(2016) > 0.10
    assert cr.historical_discount_pct(2022) < 0
    assert cr.historical_discount_pct(1999) is None


def test_the_conversion_lands_where_the_source_modules_own_prose_says_it_should():
    """The TDCV conversion is CHECKED rather than asserted. `market_switching_propensity`'s
    docstring says 2016's cheapest fix was ~18% below SVT; a TYPICAL saving should land a little
    under that. Had it come out at 3% or 40% the conversion would be wrong."""
    assert 0.12 < cr.historical_discount_pct(2016) < 0.18


def test_MUTATION_the_anchor_is_a_DIAGNOSTIC_and_never_the_reference():
    """The second wrong draft, pinned. Moving the reference onto the anchor double-counts
    `MARKET_SAVINGS_BY_YEAR` — once here and once inside `market_switching_multiplier`, which is
    calibrated from the same series. This test fails the moment the reference silently becomes
    the anchor, which is the shape that would look like a fidelity improvement and be a
    calibration error."""
    anchor = cr.anchor_rate_gbp_per_mwh(DATE)
    assert anchor < CAP, "the diagnostic is not doing its job either"
    assert cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=CAP, chase=cr.CHASE_PER_QUARTER
    ) != pytest.approx(anchor)


def test_an_unknown_date_returns_None_rather_than_a_guess():
    assert cr.competitor_reference_rate_gbp_per_mwh("1990-01-01") is None
    assert cr.anchor_rate_gbp_per_mwh("1990-01-01") is None


# ---------------------------------------------------------------------------
# THE LAG
# ---------------------------------------------------------------------------

def test_the_ledger_reports_the_PREVIOUS_quarter_never_the_current_one():
    """A rival that could read the current quarter would be re-pricing against a tariff it has
    not seen yet — a rival with foresight rather than a rival."""
    led = cr.CompanyPositionLedger()
    led.observe("2019-04-10", 100.0)
    led.observe("2019-05-10", 120.0)
    assert led.position_for("2019-06-01") is None, "read its own quarter"
    assert led.position_for("2019-08-01") == pytest.approx(110.0)


def test_the_ledger_crosses_a_YEAR_boundary():
    led = cr.CompanyPositionLedger()
    led.observe("2019-11-15", 200.0)
    assert led.position_for("2020-02-01") == pytest.approx(200.0)


def test_MUTATION_a_missing_or_nonsense_rate_is_NOT_a_position(caplog):
    """FAIL-OPEN again, at the input. A None or zero rate recorded as a position would drag the
    quarter's mean toward zero and make the rival chase a price the company never offered."""
    led = cr.CompanyPositionLedger()
    led.observe("2019-04-10", None)
    led.observe("2019-04-11", 0.0)
    led.observe("2019-04-12", -5.0)
    assert led.position_for("2019-08-01") is None
    led.observe("2019-04-13", 150.0)
    assert led.position_for("2019-08-01") == pytest.approx(150.0)


def test_the_ledger_is_INSTANCE_state_and_never_a_module_global():
    """Two runs must not see each other's book. A global here would make the reference depend on
    the order tests happen to execute in, which is the non-determinism the seeded-run discipline
    exists to forbid."""
    a, b = cr.CompanyPositionLedger(), cr.CompanyPositionLedger()
    a.observe("2019-04-10", 100.0)
    assert b.position_for("2019-08-01") is None
    assert a.position_for("2019-08-01") == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# THE WIRING — a mechanism nothing calls is the no-caller class, 13 in 13 days
# ---------------------------------------------------------------------------

def test_the_CHURN_DIFFERENTIAL_reads_the_reference_when_a_ledger_is_present():
    """The seam. `customer_events._price_differential_vs_market` is where the company's price
    meets the market, and with a ledger it must meet a market that has moved."""
    from simulation.customer_events import _price_differential_vs_market

    cheap = CAP * 0.9
    assert _price_differential_vs_market(cheap, DATE) == pytest.approx(-0.10)

    led = cr.CompanyPositionLedger()
    for day in ("2019-01-15", "2019-02-15", "2019-03-15"):
        led.observe(day, cheap)
    defended = _price_differential_vs_market(cheap, DATE, position_ledger=led)
    assert defended > -0.10 + 0.02, "the seam is wired but the reference did not move"


def test_MUTATION_NO_ledger_leaves_the_differential_byte_identical():
    """Every measurement taken before 2026-08-28 was taken with no ledger, and must still
    reproduce. This is the property that makes the change safe to land before the arms rerun."""
    from simulation.customer_events import _price_differential_vs_market
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    for position in (0.7, 0.9, 1.0, 1.3):
        rate = CAP * position
        svt = get_svt_elec_rate_gbp_per_mwh(DATE)
        assert _price_differential_vs_market(rate, DATE) == pytest.approx((rate - svt) / svt)


def test_MUTATION_the_run_FEEDS_and_READS_the_ledger_and_feeds_it_AFTER_the_roll():
    """The no-caller class is 13 instances in 13 days, 8 found by accident, so the wiring is
    asserted rather than assumed — and the ORDER is asserted too, because recording the offer
    BEFORE the roll would make the differential partly a function of the very rate being
    measured. That is the tautology R15 names first, and it would not show up as a wrong number,
    only as a suspiciously well-behaved one."""
    import re
    from pathlib import Path

    src = Path("simulation/run_phase2b.py").read_text(encoding="utf-8")
    assert "CompanyPositionLedger()" in src, "no ledger is created by the run"
    assert "position_ledger=_competitor_position_ledger" in src, "the run does not pass it"
    assert "_competitor_position_ledger.observe(" in src, "the run never feeds it"
    # THE FLOOR MUST NOT BE INERT IN THE LIVE PATH. `wholesale_gbp_per_mwh=None` is a legal
    # call and gives an UNFLOORED reference -- fine in a unit test, wrong in the run, where it
    # would let the rival follow a company below any rival's costs. Named here because that is
    # exactly the fail-open shape that gets written, noticed, and then not wired.
    assert "wholesale_gbp_per_mwh=forward_price" in src, (
        "the run does not pass a wholesale price, so the rival has no cost floor and the "
        "mechanism is the unbounded dial it was designed not to be"
    )
    assert "wholesale_gbp_per_mwh=company_fwd" not in src, (
        "the rival's cost floor is built from the COMPANY's forecast of wholesale, which makes "
        "a rival's costs a function of this company's forecasting skill"
    )

    roll_at = src.index("position_ledger=_competitor_position_ledger")
    observe_at = src.index("_competitor_position_ledger.observe(")
    assert observe_at > roll_at, (
        "the offer is recorded BEFORE the churn roll that measures it -- the rival can see the "
        "tariff it is being compared against, in the same term"
    )


def test_the_curriculum_dials_are_NAMED_and_the_baseline_is_recoverable_from_them():
    """R13. The existence of a defending rival is baseline; its aggressiveness is the director's.
    Both dials must be reachable by name, and setting the chase to zero must give the pre-module
    world back — otherwise 'the director can turn it down' is not true."""
    assert isinstance(cr.CHASE_PER_QUARTER, float) and 0.0 <= cr.CHASE_PER_QUARTER <= 1.0
    assert isinstance(cr.MIN_RETAIL_MARGIN_PCT, float) and cr.MIN_RETAIL_MARGIN_PCT > 0
    assert cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=CAP * 0.5, chase=0.0) == pytest.approx(CAP)


# ---------------------------------------------------------------------------
# ONE NAME, ONE NUMBER
# ---------------------------------------------------------------------------

def test_MUTATION_the_SVT_position_stays_the_SVT_position_after_the_reference_moves():
    """CAUGHT BY A CONTROL ON THE DAY THIS LANDED, which is why it is pinned rather than
    described. `tools/run_price_ladder`'s SVT reconciliation went from `agrees=True` to
    `agrees=False` with a 21.3 percentage-point gap: the world's logged
    `price_differential_vs_svt` had quietly stopped being against the SVT while keeping the name.

    They are two genuinely different quantities and now carry two names. `..._vs_svt` is the
    position against the published cap and must be UNMOVED by any competitor;
    `..._vs_market_reference` is the number the churn decision actually used."""
    from simulation.customer_events import _price_differential_vs_market, _svt_position

    cheap = CAP * 0.9
    led = cr.CompanyPositionLedger()
    for day in ("2019-01-15", "2019-02-15", "2019-03-15"):
        led.observe(day, cheap)

    against_market = _price_differential_vs_market(cheap, DATE, position_ledger=led)
    against_cap = _svt_position(cheap, DATE)
    assert against_cap == pytest.approx(-0.10), "the SVT position moved when the rival did"
    assert against_market != pytest.approx(against_cap), (
        "the two references produced the same number, so one of them is not being used"
    )


def test_the_LEVEL_the_differential_was_taken_against_is_PUBLISHED():
    """A consumer must be able to reconcile against the number that was used, not re-derive one
    that used to match. Re-deriving is exactly how a control goes quiet after a reference moves."""
    from simulation.customer_events import _market_reference_gbp_per_mwh

    assert _market_reference_gbp_per_mwh(DATE) == pytest.approx(CAP)
    led = cr.CompanyPositionLedger()
    for day in ("2019-01-15", "2019-02-15", "2019-03-15"):
        led.observe(day, CAP * 0.9)
    moved = _market_reference_gbp_per_mwh(DATE, position_ledger=led)
    assert moved < CAP, "the published level did not move with the rival"
    assert moved == pytest.approx(
        cr.competitor_reference_rate_gbp_per_mwh(
            DATE, company_rate_gbp_per_mwh=CAP * 0.9))


# ---------------------------------------------------------------------------
# THE CURRICULUM SURFACE — a dial the director can actually reach
# ---------------------------------------------------------------------------

def test_the_aggression_file_EXISTS_and_the_defaults_are_reachable_through_it():
    """A docstring that promises a config file the code does not read is a claim the code does
    not support -- the exact class the canon drift check was minted for. This asserts the file is
    real and that reading it is the live path."""
    assert cr.AGGRESSION_PATH.is_file(), "the curriculum file this module documents does not exist"
    a = cr.aggression()
    assert set(a) == {"chase_per_quarter", "min_retail_margin_pct"}
    assert 0.0 <= a["chase_per_quarter"] <= 1.0


def test_MUTATION_a_MALFORMED_file_falls_back_to_the_DEFAULTS_and_never_to_zero(tmp_path, monkeypatch):
    """FAIL-SILENT, the third pattern R15 names. A world that quietly stopped defending because of
    a YAML typo would look exactly like a world with no rival in it, and nothing would say so."""
    bad = tmp_path / "COMPETITOR_AGGRESSION.yaml"
    for content in ("{{{ not yaml", "", "- a list, not a mapping", "chase_per_quarter: banana"):
        bad.write_text(content, encoding="utf-8")
        monkeypatch.setattr(cr, "AGGRESSION_PATH", bad)
        assert cr.aggression()["chase_per_quarter"] == cr.CHASE_PER_QUARTER, (
            f"a malformed file ({content!r}) changed the chase"
        )
    monkeypatch.setattr(cr, "AGGRESSION_PATH", tmp_path / "absent.yaml")
    assert cr.aggression()["chase_per_quarter"] == cr.CHASE_PER_QUARTER


def test_MUTATION_an_OUT_OF_RANGE_value_is_IGNORED_rather_than_applied(tmp_path, monkeypatch):
    """A chase of 5.0 would send the reference through the company and out the other side; a
    negative one would make the rival RAISE its price when undercut. Both are rejected with the
    default kept, rather than clamped -- a clamped value silently becomes a different curriculum
    from the one that was written down."""
    f = tmp_path / "a.yaml"
    monkeypatch.setattr(cr, "AGGRESSION_PATH", f)
    for value in (5.0, -0.5, 1.0001):
        f.write_text(f"chase_per_quarter: {value}\n", encoding="utf-8")
        assert cr.aggression()["chase_per_quarter"] == cr.CHASE_PER_QUARTER


def test_the_director_CAN_turn_the_rival_off_and_get_the_prior_world_back(tmp_path, monkeypatch):
    """R13's own test: 'the director can turn it down' has to be true, not merely stated. Zero is
    a LEGITIMATE setting and must reproduce 2026-08-27 exactly."""
    f = tmp_path / "a.yaml"
    f.write_text("chase_per_quarter: 0.0\n", encoding="utf-8")
    monkeypatch.setattr(cr, "AGGRESSION_PATH", f)
    assert cr.aggression()["chase_per_quarter"] == 0.0
    assert cr.competitor_reference_rate_gbp_per_mwh(
        DATE, company_rate_gbp_per_mwh=CAP * 0.5) == pytest.approx(CAP)
