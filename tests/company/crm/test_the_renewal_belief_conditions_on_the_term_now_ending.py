"""The renewal churn belief, conditioned on the term the renewal ends (2026-10-21).

Off on every standing policy. Graded out of sample in
`docs/staging/records/SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md`
§10; the knowledge behind it is
`docs/market_research/switching_gradient_by_tariff_and_payment_what_the_record_can_grade.md` §5.
"""
from __future__ import annotations

import dataclasses

import simulation.run_phase2b as run_phase2b
from company.crm import churn_desk
from company.crm.churn_desk import (
    ENDING_TERM_DEFAULT,
    ENDING_TERM_DEFAULT_AFTER_DECLINED_FIX,
    ENDING_TERM_FIXED,
    RenewalObservation,
    condition_on_ending_term,
    ending_term_type,
    estimate_renewal_churn,
)
from company.crm.competitive_pressure import CompetitivePressureLedger, pressure_ledger_scope
from company.policy.decision_policy import CURRENT_POLICY, DecisionPolicy

OBS = RenewalObservation(old_rate_gbp_per_mwh=150.0, new_rate_gbp_per_mwh=170.0, tenure_years=2.0,
                         annual_consumption_kwh=2900.0, renewal_year=2019, active_renewal=True,
                         account_id="ACC-NOW", term_start="2019-03-01", fuel="electricity")


def _book(ledger: CompetitivePressureLedger, kind: str, n: int, lost: int, year: int = 2017) -> None:
    for i in range(n):
        account = f"{kind}-{year}-{i}"
        ledger.observe_ending_term(year, kind, account, 0.3)
        if i < lost:
            ledger.observe_competitive_loss(year, account_id=account)


def _a_book_that_loses_at_fix_end_only() -> CompetitivePressureLedger:
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    _book(ledger, ENDING_TERM_FIXED, 40, 20)
    _book(ledger, ENDING_TERM_DEFAULT, 40, 0)
    return ledger


def test_every_ending_term_type_is_reachable_from_the_book():
    """The partition first: a mapper that collapsed two types would pass every leg below."""
    seen = {ending_term_type(prev, previous_term_spliced=spliced, default_tariff_type="svt")
            for prev in ("fixed", "svt", "deemed", None) for spliced in (False, True)}
    assert seen == {ENDING_TERM_FIXED, ENDING_TERM_DEFAULT, ENDING_TERM_DEFAULT_AFTER_DECLINED_FIX, None}
    assert ending_term_type("svt", previous_term_spliced=True, default_tariff_type="svt") == (
        ENDING_TERM_DEFAULT_AFTER_DECLINED_FIX)
    assert ending_term_type("fixed", previous_term_spliced=True, default_tariff_type="svt") == (
        ENDING_TERM_FIXED)


def test_the_roll_type_reaches_the_belief():
    """The DONE control. One household, one renewal, two ending terms: the belief must differ, and
    in the direction the company's own book taught it. Reds if the desk stops reading the type."""
    with pressure_ledger_scope(_a_book_that_loses_at_fix_end_only()):
        off = estimate_renewal_churn(OBS)
        at_fix_end = estimate_renewal_churn(dataclasses.replace(OBS, ending_term_type=ENDING_TERM_FIXED))
        on_default = estimate_renewal_churn(dataclasses.replace(OBS, ending_term_type=ENDING_TERM_DEFAULT))
    assert at_fix_end > off > on_default > 0.0


def test_no_type_leaves_the_belief_exactly_as_it_was():
    ledger = _a_book_that_loses_at_fix_end_only()
    with pressure_ledger_scope(ledger):
        on_book = estimate_renewal_churn(OBS)
    with pressure_ledger_scope(CompetitivePressureLedger()):
        fresh = estimate_renewal_churn(OBS)
    assert on_book == fresh
    assert ledger.ending_term_sums == _a_book_that_loses_at_fix_end_only().ending_term_sums


def test_every_other_learner_is_booked_the_unconditioned_belief():
    """The switch must move no other learner's evidence: the pressure ledger's expected losses are
    the same whether or not the type was supplied."""
    plain, typed = _a_book_that_loses_at_fix_end_only(), _a_book_that_loses_at_fix_end_only()
    with pressure_ledger_scope(plain):
        unconditioned = estimate_renewal_churn(OBS)
    with pressure_ledger_scope(typed):
        conditioned = estimate_renewal_churn(dataclasses.replace(OBS, ending_term_type=ENDING_TERM_DEFAULT))
    assert conditioned < unconditioned
    assert typed.expected_by_year == plain.expected_by_year
    assert typed.ending_term_sums[(ENDING_TERM_DEFAULT, 2019)]["sp"] == unconditioned


def test_a_loss_in_the_year_being_priced_does_not_move_its_own_reading():
    ledger = _a_book_that_loses_at_fix_end_only()
    before, _ = ledger.ending_term_multiplier(ENDING_TERM_DEFAULT, 2019)
    _book(ledger, ENDING_TERM_DEFAULT, 10, 10, year=2019)
    after, _ = ledger.ending_term_multiplier(ENDING_TERM_DEFAULT, 2019)
    assert before == after
    assert ledger.ending_term_multiplier(ENDING_TERM_DEFAULT, 2020)[0] > before


def test_a_loss_is_credited_to_the_type_of_the_accounts_latest_roll():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    ledger.observe_ending_term(2017, ENDING_TERM_FIXED, "A", 0.2)
    ledger.observe_ending_term(2018, ENDING_TERM_DEFAULT, "A", 0.2)
    ledger.observe_competitive_loss(2018, account_id="A")
    assert ledger.ending_term_sums[(ENDING_TERM_DEFAULT, 2018)]["losses"] == 1
    assert ledger.ending_term_sums[(ENDING_TERM_FIXED, 2017)]["losses"] == 0


def test_the_multiplier_refuses_with_its_reason_where_there_is_nothing_to_learn():
    unarmed = CompetitivePressureLedger()
    _book(unarmed, ENDING_TERM_FIXED, 5, 1)
    assert unarmed.ending_term_multiplier(ENDING_TERM_FIXED, 2019) == (
        None, "departures are not being reported to this ledger")
    armed = _a_book_that_loses_at_fix_end_only()
    m, why = armed.ending_term_multiplier(ENDING_TERM_DEFAULT_AFTER_DECLINED_FIX, 2019)
    assert m is None and "no closed renewals" in why
    # Never lost one: small, not zero (Jeffreys).
    m, _ = armed.ending_term_multiplier(ENDING_TERM_DEFAULT, 2019)
    assert 0.0 < m < 0.1


def test_conditioning_keeps_the_order_inside_a_type_and_stays_a_probability():
    beliefs = [0.0, 0.05, 0.3, 0.9, 1.0]
    for m in (0.01, 0.5, 1.0, 3.0):
        out = [condition_on_ending_term(p, m) for p in beliefs]
        assert out == sorted(out) and all(0.0 <= p <= 1.0 for p in out)
    assert condition_on_ending_term(0.3, None) == 0.3


def test_the_switch_is_off_on_the_standing_policy_and_the_run_imports_the_desks_mapper():
    default = {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}
    assert default["renewal_belief_by_ending_term"] is False
    assert CURRENT_POLICY.renewal_belief_by_ending_term is False
    assert run_phase2b.ending_term_type is churn_desk.ending_term_type
