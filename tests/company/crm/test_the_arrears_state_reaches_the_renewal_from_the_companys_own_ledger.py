"""The arrears state is READ off the company's own receivable and REACHES the two renewal doors.

WHY THIS FILE EXISTS, and it is a different question from the one
`test_the_distress_term_is_read_from_the_arrears_ledger` asks. That file controls the TERM: that
`arrears_state_from_collections` reads a ledger honestly, that the hazard ratios come off Ofgem CIM
w6 Table 56, and that a known state silences the refuted bill-level knee. All of it passed on the
day it was written while NOTHING IN THE COMPANY CALLED IT -- a sourced belief wired to nobody,
which is this repository's `no_caller_and_never_runs` class and its most expensive recurring shape.

So every control here asserts REACHABILITY and then that the reach MOVES A NUMBER:

  ledger -> `LivePaymentTriad.arrears_state` -> `RenewalObservation` -> `estimate_renewal_churn`
  ledger -> `LivePaymentTriad.arrears_state` -> `decide_margin` -> the offered margin

A forwarding that is dropped anywhere on that chain leaves every control in the sibling file green,
because the term still computes correctly for a caller that supplies it and nothing did.
"""
from __future__ import annotations

import datetime as dt

import pytest

from background.live_payment_triad import LivePaymentTriad
from company.crm.churn_desk import RenewalObservation, estimate_renewal_churn
from company.crm.churn_model import (
    ARREARS_STATE_IN_ARREARS_STEADY,
    ARREARS_STATE_NO_DEBT,
    ARREARS_STATE_UNKNOWN,
    ARREARS_STATE_WORSENING,
)
from company.pricing.value_based_renewal import VALUE_BASED, decide_margin

_RENEWAL = dict(
    old_rate_gbp_per_mwh=250.0,
    new_rate_gbp_per_mwh=280.0,
    tenure_years=3.0,
    annual_consumption_kwh=3100.0,
    renewal_year=2024,
)


def _estimate(**kw) -> float:
    return estimate_renewal_churn(RenewalObservation(**{**_RENEWAL, **kw}))


def _seeded_triad(customer_id: str, *, months: int = 6, amount_gbp: float = 120.0,
                  stress: str = "high") -> LivePaymentTriad:
    """A triad whose company ledger holds `months` of real bills and whatever cash arrived.

    The payment outcomes are W2_11's own draw, not a fixture: `record_period` generates the one
    canonical event and posts both the bill and the observed cash into the company's ledger. That
    is the point -- a control fed hand-written snapshots would prove the mapping and not the wire.
    """
    triad = LivePaymentTriad()
    for month in range(1, months + 1):
        triad.record_period(
            customer_id=customer_id, due_date=dt.date(2023, month, 28),
            amount_gbp=amount_gbp, income_stress_value=stress, segment="resi",
        )
    return triad


# --------------------------------------------------------------------------- #
# The door: a state read off the company's own ledger, and all four reachable   #
# --------------------------------------------------------------------------- #

def test_the_door_returns_every_one_of_the_four_states_over_the_ledger_it_actually_keeps():
    """ONE CONTROL OVER THE WHOLE PARTITION, not a leg per branch.

    A door that returned `unknown` for everything would satisfy every single-state assertion
    written about it, and a door that collapsed `worsening` and `in_arrears_steady` onto one value
    would satisfy every assertion about either -- this project has entered that trap three times.
    So the claim is that the partition is INHABITED: four distinct states, all reached through the
    public door, over ledgers built only from `record_period`.

    MUTATION (must fire): return `ARREARS_STATE_UNKNOWN` unconditionally from
    `LivePaymentTriad.arrears_state`, or drop the `no_debt` branch out of
    `arrears_state_from_collections`.
    """
    reached = set()

    # Never billed: the company has not looked, and an empty ledger reading zero overdue must not
    # be sold as "no debt" -- that would hand an unobserved household Table 56's 0.79x.
    reached.add(LivePaymentTriad().arrears_state("NEVER-BILLED", dt.date(2023, 6, 1)))

    stressed = _seeded_triad("STRESSED", stress="high")
    for month in range(2, 8):
        reached.add(stressed.arrears_state("STRESSED", dt.date(2023, month, 1)))

    # A book that pays: the same door, the same wire, no arrears.
    paying = _seeded_triad("PAYING", stress="low", amount_gbp=15.0)
    for month in range(2, 8):
        reached.add(paying.arrears_state("PAYING", dt.date(2023, month, 1)))

    assert reached == {
        ARREARS_STATE_UNKNOWN, ARREARS_STATE_NO_DEBT,
        ARREARS_STATE_WORSENING, ARREARS_STATE_IN_ARREARS_STEADY,
    }, f"the door does not inhabit its own partition; it reached only {sorted(reached)}"


def test_an_account_this_company_has_never_billed_reads_unknown_and_not_no_debt():
    """FAIL CLOSED, and this is the leg that would be quietly wrong in the flattering direction.

    An empty ledger has zero undisputed overdue, so the cheap reading is `no_debt` -- which is a
    PUBLISHED column carrying 0.79x, i.e. a claim that this household shops LESS than average, made
    about a household the company has never billed.

    MUTATION (must fire): delete the roster guard in `LivePaymentTriad.arrears_state` so an unknown
    account falls through to the ledger read.
    """
    assert LivePaymentTriad().arrears_state("GHOST", dt.date(2023, 6, 1)) == ARREARS_STATE_UNKNOWN


def test_the_previous_reading_is_the_same_ledger_one_billing_period_back():
    """The DIRECTION column needs two readings, and they must be of the SAME bookkeeping.

    `worsening` is Table 56's "keeping up is getting harder" -- a direction. If the door compared
    a reading against itself, or against a fixed date, no account could ever be `worsening` while
    its balance genuinely grew, and the term would be silently one-sided in exactly the way the
    knee it replaced was.

    MUTATION (must fire): pass `as_of` as the previous reading too, or drop the second argument.
    """
    triad = _seeded_triad("DIRECTION")
    states = [triad.arrears_state("DIRECTION", dt.date(2023, m, 1)) for m in range(2, 8)]
    assert ARREARS_STATE_WORSENING in states, (
        f"no month of a stressed account's ledger reads as deteriorating: {states}"
    )


# --------------------------------------------------------------------------- #
# The reach: the churn desk                                                     #
# --------------------------------------------------------------------------- #

def test_the_desks_default_leaves_every_estimate_this_company_has_ever_published_untouched():
    """A new observable must not move a number by existing.

    MUTATION (must fire): change `RenewalObservation.arrears_state`'s default away from
    `ARREARS_STATE_UNKNOWN`.
    """
    assert _estimate() == _estimate(arrears_state=ARREARS_STATE_UNKNOWN)


def test_the_desk_forwards_the_state_so_the_two_published_columns_move_the_estimate_apart():
    """THE FORWARD IS THE SUBJECT, and both directions of it.

    `no_debt` is 0.79x and MUST come out BELOW the unknown baseline -- the term it replaced was
    one-sided by construction and could not express a household that shops less than average, so a
    forward that only ever raised the estimate would have reproduced the old shape under a new
    name.

    MUTATION (must fire): drop `arrears_state=observation.arrears_state` from the
    `enriched_churn_estimate` call in `churn_desk._estimate_renewal_churn`. Both assertions go
    from strict inequalities to equalities.
    """
    worse = _estimate(arrears_state=ARREARS_STATE_WORSENING)
    none_owed = _estimate(arrears_state=ARREARS_STATE_NO_DEBT)
    baseline = _estimate(arrears_state=ARREARS_STATE_UNKNOWN)
    assert worse > baseline, "a deteriorating arrears position did not reach the estimate"
    assert none_owed < baseline, (
        "a household with no debt did not come out below the base rate, so the sourced term is "
        "still one-sided like the knee it replaced"
    )


def test_the_chain_runs_end_to_end_from_a_ledger_the_company_built_itself():
    """LEDGER -> DOOR -> OBSERVATION -> ESTIMATE, with no hand-written state anywhere in it.

    This is the control that would have caught the state the sibling file could not: every
    assertion there passes while the chain is broken, because the term is correct and unreached.

    MUTATION (must fire): break any link -- the door, the dataclass field, or the desk's forward.
    """
    triad = _seeded_triad("CHAIN")
    dated = [(m, triad.arrears_state("CHAIN", dt.date(2023, m, 1))) for m in range(2, 8)]
    known = [(m, state) for m, state in dated if state != ARREARS_STATE_UNKNOWN]
    assert known, f"the company's own ledger yielded no known state at any renewal date: {dated}"

    moved = [
        (m, state) for m, state in known
        if _estimate(arrears_state=state) != _estimate(arrears_state=ARREARS_STATE_UNKNOWN)
    ]
    assert moved, (
        f"every state the ledger produced left the estimate unchanged, so the read reaches "
        f"nothing: {known}"
    )


# --------------------------------------------------------------------------- #
# The reach: the value arm                                                      #
# --------------------------------------------------------------------------- #

_PRICING = dict(
    customer_id="AR-1", arm=VALUE_BASED,
    current_rate_gbp_per_mwh=250.0, base_rate_gbp_per_mwh=200.0,
    eac_kwh=3100.0, tenure_years=3.0, cost_to_serve_gbp_per_year=90.0,
    segment="resi", renewal_year=2024,
)


def test_the_value_arms_default_prices_exactly_as_it_did_before_the_argument_existed():
    """MUTATION (must fire): change `decide_margin`'s `arrears_state` default."""
    a = decide_margin(**_PRICING)
    b = decide_margin(**_PRICING, arrears_state=ARREARS_STATE_UNKNOWN)
    assert a.margin_gbp_per_mwh == b.margin_gbp_per_mwh
    assert a.p_retain == pytest.approx(b.p_retain)


def test_the_value_arm_retains_a_debt_free_household_more_readily_than_a_deteriorating_one():
    """THE THESIS SENTENCE, PRICED. The value arm beats the flat rule exactly to the degree the
    churn belief predicts better, so a sourced per-household distress signal read off this
    supplier's own accounts receivable is where the advantage comes from -- inference on an
    observable we genuinely have, never access to one we do not.

    The claim is on `p_retain` rather than on the chosen margin: the margin is a search over a
    discrete candidate list and two neighbouring beliefs can land on the same rung, so asserting
    the margin moved would be a control that fails for the grid's reasons rather than the belief's.

    MUTATION (must fire): drop `arrears_state=arrears_state` from `_score`'s
    `enriched_churn_estimate` call.
    """
    worse = decide_margin(**_PRICING, arrears_state=ARREARS_STATE_WORSENING)
    none_owed = decide_margin(**_PRICING, arrears_state=ARREARS_STATE_NO_DEBT)
    assert none_owed.p_retain > worse.p_retain, (
        "the arrears position does not reach the price this company offers"
    )


def test_a_state_read_off_the_ledger_prices_differently_from_one_never_looked_up():
    """The priced end of the same chain, sourced from the ledger rather than from a literal.

    MUTATION (must fire): break the door or the `_score` forward.
    """
    triad = _seeded_triad("PRICED")
    states = {triad.arrears_state("PRICED", dt.date(2023, m, 1)) for m in range(2, 8)}
    known = sorted(states - {ARREARS_STATE_UNKNOWN})
    assert known, "the ledger produced no known state to price on"
    baseline = decide_margin(**_PRICING, arrears_state=ARREARS_STATE_UNKNOWN)
    priced = [decide_margin(**_PRICING, arrears_state=s).p_retain for s in known]
    assert any(p != pytest.approx(baseline.p_retain) for p in priced), (
        f"no state this company's own ledger produced changed what it would charge: {known}"
    )


def test_the_passive_estimator_is_deliberately_untouched_by_the_arrears_state():
    """AN EQUIVALENCE, NAMED, so the next reader does not file it as a missing forward.

    The passive branch does not call `estimate_churn_probability`, so it carries neither the
    refuted knee nor anything for the arrears term to replace. Forwarding the state there would
    hand an SVT roller a distress uplift no term on that branch ever claimed -- a new belief
    wearing a wiring change's clothes. This control pins that as a DECISION; if the evidence later
    says Table 56 applies to a passive roll, this is the test that must be rewritten to say so.
    """
    passive = dict(_RENEWAL, active_renewal=False, segment="resi")
    assert _estimate(**passive, arrears_state=ARREARS_STATE_WORSENING) == _estimate(**passive)
