"""The distress claim is read from the company's own arrears ledger, not from the bill level.

REUSE: tests/company/crm/test_the_distress_term_is_read_from_the_arrears_ledger.py
INDEX: searched "arrears", "churn", "distress", "hazard", "bill_stress", "CIM", "Table 56",
"collections_snapshot", "ledger". What exists and why none of it is this control:
  * `tests/company/crm/test_the_refuted_bill_stress_term_cannot_outgrow_its_evidence.py` — bounds
    the REFUTED term's magnitude. It asks how large a wrong term may be; it cannot ask whether a
    right one exists, and it stayed green through every day the model had no arrears term at all.
  * `tests/company/crm/test_churn_model.py` — the estimator's arithmetic, including the knee's.
    It has no arrears vocabulary and never supplies one.
  * `tests/company/billing/test_arrears_engine.py` — the ledger's own ageing/dunning physics. It
    proves `collections_snapshot` is right; it does not know the belief reads it.
  * `tests/company/crm/test_the_churn_belief_hears_household_size.py` — the SOURCED size term,
    which multiplies the RATE RESPONSE. A different observable answering a different question.
No existing control asks whether the company's distress claim is keyed to something it can
actually see about a household's finances.

THE DEFECT EACH TEST NAMES
--------------------------
`bill_stress` asserts that a household's SPEND drives its propensity to switch. Ofgem/BMG
(n=3,235) puts that correlation at -0.07 to +0.05 and DESNZ QEP 2.7.1 runs the other way. The
replacement is a per-household hazard against the supplier's own arrears ledger, and every way it
can go wrong is a way this project has already paid for:

  * `test_the_belief_varies_per_household_across_the_WHOLE_arrears_partition`
    — ONE control over the whole partition. A mapping that collapses two states onto one value
    passes every per-state assertion while the belief has stopped distinguishing the households
    it exists to distinguish. Ordering AND distinctness, in one place.
  * `test_the_no_debt_arm_moves_the_belief_DOWN_which_the_refuted_term_COULD_NOT`
    — keyed to the PROPERTY (`max(0, ...)` is one-sided) and not to 0.79 or to today's estimate.
  * `test_both_arms_are_the_published_pair_over_the_SAME_denominator`
    — derivation, never a literal; and it refuses the 1.6x trap the knowledge map names by hand:
    6.8/4.2 is a third quantity against a different base and must not be quoted for either.
  * `test_a_known_arrears_state_makes_the_refuted_bill_knee_unreachable`
    — the retirement leg, with `test_the_knee_is_LIVE_in_the_control_arm` beside it, because a
    probe input at which the knee is inert would make that leg pass for the wrong reason.
  * `test_the_direction_is_keyed_to_the_AMOUNT_and_NOT_to_the_AGE`
    — `max_days_overdue` climbs by one every day an unpaid bill sits there, so keying the
    direction to age reads EVERY static arrears as deteriorating: the partition collapses onto
    one state and the log looks exactly like a working mechanism.
  * `test_one_reading_of_a_household_IN_ARREARS_is_a_LEVEL_and_not_a_DIRECTION`
    — Table 56's positive column is "getting harder", which no single observation can be. This
    is the over-read that would publish a level as a direction and never look wrong.
  * `test_an_unreadable_snapshot_fails_closed_and_asserts_no_distress`
  * `test_an_invented_state_is_refused_BY_NAME`
  * `test_the_domestic_survey_does_not_reach_an_industrial_account`

MUTATION SWEEP, RUN rather than promised and reported as it came back, in an isolated copy of
the tree so a mutated `churn_model.py` could not red another lane's live gate run. Eight
mutations, eight kills, and each one died to the leg written for it rather than to a neighbour:

    M1  no_debt ratio -> 1.0 (delete the down arm)        KILLED by partition, no_debt, published
    M2  in_arrears_steady -> the worsening ratio          KILLED by partition, published
        (closing the declared gap by over-reading it)
    M3  drop `bill_stress = 0.0` on the known branch      KILLED by knee_unreachable, alone
        (the knee survives its own replacement)
    M4  no previous snapshot -> WORSENING                 KILLED by level_not_direction, alone
        (a level published as a direction)
    M5  direction keyed to `max_days_overdue`             KILLED by amount_not_age, alone
    M6  uplift returns the ratio, not base x (ratio-1)    KILLED by partition, no_debt, fail_closed
    M7  invented state -> `.get(state, 1.0)`              KILLED by refused_by_name, alone
    M8  the `segment == RESI_SEGMENT` guard dropped       KILLED by industrial_account, alone
"""
import datetime as dt

import pytest

from company.billing.account_ledger import (
    AccountLedger,
    LedgerEvent,
    LedgerEventType,
)
from company.billing.arrears_engine import collections_snapshot
from company.crm.account_hierarchy import Segment
from company.crm.churn_model import (
    ARREARS_LEDGER_FIELD,
    ARREARS_STATE_IN_ARREARS_STEADY,
    ARREARS_STATE_NO_DEBT,
    ARREARS_STATE_UNKNOWN,
    ARREARS_STATE_WORSENING,
    ARREARS_STATES,
    BASE_CHURN_RATE,
    IC_SEGMENT,
    RESI_SEGMENT,
    arrears_hazard_ratio,
    arrears_state_from_collections,
    arrears_stress_uplift,
    estimate_churn_probability,
)

TT = dt.datetime(2024, 1, 1, 12, 0, 0)

#: Ofgem CIM wave 6, Table 56 (question C4, base n=3,458, six-month reported behaviour). Written
#: out here rather than imported so a control over the published pair cannot be satisfied by the
#: module agreeing with itself -- a cited index fed its own API always does.
CIM_W6_POPULATION = 0.053
CIM_W6_GETTING_HARDER = 0.068
CIM_W6_NO_DEBT = 0.042

#: A household at the Ofgem TDCV Medium band on an ordinary renewal. Every partition control uses
#: THIS household, so the only thing varying across the arms is the ledger state.
HOUSEHOLD = dict(
    old_rate_gbp_per_mwh=250.0,
    new_rate_gbp_per_mwh=275.0,
    tenure_years=3.0,
    annual_consumption_kwh=2500.0,
)

#: A household large enough that the refuted knee IS live at this rate deck -- GBP 250/MWh on
#: 40,000 kWh is a GBP 10,000 previous bill, comfortably above the declared GBP 3,000 threshold.
#: The knee's liveness here is ASSERTED by its own control rather than assumed.
KNEE_IS_LIVE = dict(
    old_rate_gbp_per_mwh=250.0,
    new_rate_gbp_per_mwh=250.0,
    tenure_years=3.0,
    annual_consumption_kwh=40_000.0,
)


def _bill(eid, acct, amount, day, month=1, ref=None):
    return LedgerEvent(eid, acct, LedgerEventType.BILL_DEBIT, amount,
                       dt.date(2024, month, day), TT, invoice_ref=ref)


def _payment(eid, acct, amount, day, month=1):
    return LedgerEvent(eid, acct, LedgerEventType.PAYMENT_CREDIT, amount,
                       dt.date(2024, month, day), TT)


def test_the_belief_varies_per_household_across_the_WHOLE_arrears_partition():
    """The estimate is DISTINCT where Table 56 distinguishes and EQUAL where it does not.

    MUTATION (must fire): set any published arm's ratio to 1.0, or set `in_arrears_steady` to the
    worsening ratio -> RED. A per-state assertion could not see either: each state would still
    return "a number", and the belief would have stopped telling two households apart while every
    individual leg stayed green.
    """
    p = {s: estimate_churn_probability(**HOUSEHOLD, arrears_state=s) for s in ARREARS_STATES}

    # The two PUBLISHED arms straddle the population's own propensity, in the published order.
    assert p[ARREARS_STATE_NO_DEBT] < p[ARREARS_STATE_UNKNOWN] < p[ARREARS_STATE_WORSENING], p

    # The DECLARED GAP sits exactly on the population propensity -- not above it (which would be
    # asserting the "getting harder" column about a household that is not in it) and not below it
    # (which would be asserting the "no debt" column about a household that owes money).
    assert p[ARREARS_STATE_IN_ARREARS_STEADY] == pytest.approx(p[ARREARS_STATE_UNKNOWN])

    # And the whole partition is REACHABLE: three distinct values over four states, which is the
    # shape the table supports and not one value wearing four names.
    assert len({round(v, 9) for v in p.values()}) == 3, p


def test_the_no_debt_arm_moves_the_belief_DOWN_which_the_refuted_term_COULD_NOT():
    """A household the published record says shops LESS than average is estimated below base.

    MUTATION (must fire): clamp `arrears_stress_uplift` at zero, or set the no-debt ratio to 1.0
    -> RED. Keyed to the SIGN and to the structural claim, not to 0.79 or to today's estimate:
    `bill_stress = sens * max(0, bill/threshold - 1)` is one-sided by construction, so the term
    this replaces could only ever hand such a household the population's own propensity.
    """
    assert arrears_stress_uplift(BASE_CHURN_RATE, ARREARS_STATE_NO_DEBT) < 0.0
    assert arrears_stress_uplift(BASE_CHURN_RATE, ARREARS_STATE_WORSENING) > 0.0
    down = estimate_churn_probability(**HOUSEHOLD, arrears_state=ARREARS_STATE_NO_DEBT)
    flat = estimate_churn_probability(**HOUSEHOLD, arrears_state=ARREARS_STATE_UNKNOWN)
    assert down < flat


def test_both_arms_are_the_published_pair_over_the_SAME_denominator():
    """Each arm is its Table 56 column over the SURVEY's own 5.3% base, derived and not written.

    MUTATION (must fire): replace either ratio with its decimal, or normalise the arrears column
    on the no-debt column (6.8/4.2 = 1.62) -> RED. That second one is the trap the knowledge map
    names by hand: 1.6x is a third quantity against a different denominator and may not be quoted
    for either of these.
    """
    assert arrears_hazard_ratio(ARREARS_STATE_WORSENING) == pytest.approx(
        CIM_W6_GETTING_HARDER / CIM_W6_POPULATION)
    assert arrears_hazard_ratio(ARREARS_STATE_NO_DEBT) == pytest.approx(
        CIM_W6_NO_DEBT / CIM_W6_POPULATION)
    assert arrears_hazard_ratio(ARREARS_STATE_WORSENING) != pytest.approx(
        CIM_W6_GETTING_HARDER / CIM_W6_NO_DEBT), (
        "the arrears arm is normalised on the no-debt column, not on the survey's population "
        "base -- that is the 1.6x the knowledge map says must not be quoted for the 1.28x")
    # Both gaps carry the population's own propensity, and they carry it as a DERIVED 1.0.
    assert arrears_hazard_ratio(ARREARS_STATE_IN_ARREARS_STEADY) == 1.0
    assert arrears_hazard_ratio(ARREARS_STATE_UNKNOWN) == 1.0


def test_the_knee_is_LIVE_in_the_control_arm():
    """The anti-vacuity leg for the retirement control below.

    At `KNEE_IS_LIVE` with NO rate move at all, the refuted bill-level term is what makes the
    estimate exceed the segment's base rate less its tenure discount. If it were inert here, the
    retirement leg would pass while removing nothing.
    """
    with_knee = estimate_churn_probability(**KNEE_IS_LIVE, arrears_state=ARREARS_STATE_UNKNOWN)
    small = dict(KNEE_IS_LIVE, annual_consumption_kwh=1_000.0)
    without_knee = estimate_churn_probability(**small, arrears_state=ARREARS_STATE_UNKNOWN)
    assert with_knee > without_knee, (
        "the probe consumption does not reach the knee, so the retirement leg below would be "
        "asserting the absence of something that was never there")


def test_a_known_arrears_state_makes_the_refuted_bill_knee_unreachable():
    """Where the company can see the ledger, the bill LEVEL stops speaking entirely.

    MUTATION (must fire): drop the `bill_stress = 0.0` on the known branch so the two terms ADD
    -> RED. Two terms asserting the same claim from two observables, summed, is the claim made
    twice and the sum called a model.
    """
    for state in (ARREARS_STATE_NO_DEBT, ARREARS_STATE_IN_ARREARS_STEADY,
                  ARREARS_STATE_WORSENING):
        big = estimate_churn_probability(**KNEE_IS_LIVE, arrears_state=state)
        small = estimate_churn_probability(
            **dict(KNEE_IS_LIVE, annual_consumption_kwh=1_000.0), arrears_state=state)
        assert big == pytest.approx(small), (
            f"consumption still moves the belief under arrears state {state!r}: the refuted "
            f"bill-level knee is reachable alongside its own replacement")


def test_the_state_is_read_from_the_engines_OWN_snapshot():
    """`arrears_state_from_collections` consumes `collections_snapshot`'s real return value.

    MUTATION (must fire): read any field other than the engine's own
    `undisputed_overdue_gbp` -> RED, because nothing else in the snapshot carries the
    undisputed/overdue pair of conditions this state is defined by.
    """
    clear = AccountLedger("CLEAR")
    clear.post(_bill("b1", "CLEAR", 400.0, 1))
    clear.post(_payment("p1", "CLEAR", 400.0, 10))
    snap_clear = collections_snapshot(clear, Segment.RESIDENTIAL, False, dt.date(2024, 4, 1))
    assert ARREARS_LEDGER_FIELD in snap_clear
    assert arrears_state_from_collections(snap_clear) == ARREARS_STATE_NO_DEBT

    owing = AccountLedger("OWING")
    owing.post(_bill("b1", "OWING", 400.0, 1))
    snap_owing = collections_snapshot(owing, Segment.RESIDENTIAL, False, dt.date(2024, 4, 1))
    assert snap_owing[ARREARS_LEDGER_FIELD] > 0.0
    assert arrears_state_from_collections(snap_owing) != ARREARS_STATE_NO_DEBT


def test_one_reading_of_a_household_IN_ARREARS_is_a_LEVEL_and_not_a_DIRECTION():
    """Table 56's positive column is "getting harder", which one observation cannot establish.

    MUTATION (must fire): return WORSENING when there is no previous snapshot -> RED. That is the
    over-read that would publish a level as a direction and never look wrong from inside.
    """
    owing = AccountLedger("OWING")
    owing.post(_bill("b1", "OWING", 400.0, 1))
    snap = collections_snapshot(owing, Segment.RESIDENTIAL, False, dt.date(2024, 4, 1))
    assert arrears_state_from_collections(snap, previous=None) == ARREARS_STATE_UNKNOWN


def test_the_direction_is_keyed_to_the_AMOUNT_and_NOT_to_the_AGE():
    """A static arrears observed a month later is OLDER and is not deteriorating.

    MUTATION (must fire): key the direction to `max_days_overdue` -> RED. That reading climbs by
    one every day an unpaid bill sits there, so every static arrears reads as "getting harder",
    the partition collapses onto one state, and the log looks exactly like a working mechanism.
    """
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 400.0, 1))
    earlier = collections_snapshot(led, Segment.RESIDENTIAL, False, dt.date(2024, 3, 1))
    later = collections_snapshot(led, Segment.RESIDENTIAL, False, dt.date(2024, 4, 1))
    assert later["max_days_overdue"] > earlier["max_days_overdue"], "probe is not ageing"
    assert later[ARREARS_LEDGER_FIELD] == earlier[ARREARS_LEDGER_FIELD], "probe amount moved"
    assert arrears_state_from_collections(later, previous=earlier) == \
        ARREARS_STATE_IN_ARREARS_STEADY

    # And the DIRECTION leg is reachable: a household that fell further behind IS the column.
    led.post(_bill("b2", "A", 300.0, 1, month=3))
    worse = collections_snapshot(led, Segment.RESIDENTIAL, False, dt.date(2024, 4, 1))
    assert arrears_state_from_collections(worse, previous=earlier) == ARREARS_STATE_WORSENING

    # ...and a household PAYING ITS ARREARS DOWN is not, which is the other side of the same
    # partition and the one a magnitude-blind test would never reach.
    led.post(_payment("p1", "A", 500.0, 2, month=4))
    better = collections_snapshot(led, Segment.RESIDENTIAL, False, dt.date(2024, 4, 15))
    assert arrears_state_from_collections(better, previous=worse) != ARREARS_STATE_WORSENING


def test_an_unreadable_snapshot_fails_closed_and_asserts_no_distress():
    """A snapshot that cannot say returns `unknown`, and `unknown` asserts nothing."""
    for bad in (None, {}, {ARREARS_LEDGER_FIELD: None}, {ARREARS_LEDGER_FIELD: "120.00"},
                {ARREARS_LEDGER_FIELD: True}, "not a snapshot"):
        assert arrears_state_from_collections(bad) == ARREARS_STATE_UNKNOWN, bad
    assert arrears_stress_uplift(BASE_CHURN_RATE, ARREARS_STATE_UNKNOWN) == 0.0


def test_an_invented_state_is_refused_BY_NAME():
    """A fifth state is a claim about a household, and it is refused rather than defaulted.

    MUTATION (must fire): `return _ARREARS_HAZARD_RATIO.get(state, 1.0)` -> RED. A silent 1.0
    would publish an invented state's assertion as "no effect found", which is the reading a
    refusal exists to prevent.
    """
    with pytest.raises(ValueError) as excinfo:
        arrears_hazard_ratio("struggling_a_bit")
    message = str(excinfo.value)
    assert "struggling_a_bit" in message
    assert "Table 56" in message and "published column" in message


def test_the_domestic_survey_does_not_reach_an_industrial_account():
    """Table 56 surveys HOUSEHOLDS; an industrial site gets no distress term from either source.

    MUTATION (must fire): drop the `segment == RESI_SEGMENT` guard -> RED. Extrapolating a
    domestic banner onto an industrial account is the x599.6 mistake this repository already
    documents and refuses elsewhere.
    """
    ic = dict(HOUSEHOLD, segment=IC_SEGMENT, annual_consumption_kwh=3_900_000.0)
    flat = estimate_churn_probability(**ic, arrears_state=ARREARS_STATE_UNKNOWN)
    for state in (ARREARS_STATE_NO_DEBT, ARREARS_STATE_WORSENING):
        assert estimate_churn_probability(**ic, arrears_state=state) == pytest.approx(flat)

    # ...while the domestic segment the survey DOES cover moves, so this is a scope guard and
    # not a term that never fires.
    resi = dict(HOUSEHOLD, segment=RESI_SEGMENT)
    assert estimate_churn_probability(**resi, arrears_state=ARREARS_STATE_WORSENING) != \
        pytest.approx(estimate_churn_probability(**resi, arrears_state=ARREARS_STATE_UNKNOWN))
