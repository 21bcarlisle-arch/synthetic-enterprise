"""The default belief learns from what the company itself was not paid, and only from what it knew.

Defect each control names:
  * the book is read but the belief never moves off the prior (a cell defaulting at twice its prior
    leaves the estimate where it was);
  * the belief reads outcomes that resolved AFTER the decision (look-ahead);
  * a persistent debtor reads as clean because FIFO moved its debt onto its newest bills;
  * a closed account's unpaid money is provisioned on the live row (the 5-50x understatement the
    final-bill row exists to stop);
  * an outcome is read before the company could know it;
  * an account the register answers `None` for (not one the price learns from) is learned from anyway;
  * an account that pays down arrears it began the year with is learned as a NEGATIVE loss (the
    release of last year's provision read as this year's gain), so a thin cell of them prices a
    debtor as a source of value (`df9792c57`).
"""

import datetime as dt

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import fifo_unpaid_bills
from company.pricing.default_belief import (
    PRIOR_LOSS_RATE,
    AccountYear,
    default_belief,
    observe_book,
)
from company.pricing.value_based_renewal import (
    RECEIVABLE_PROVISION_RATE_FINAL_BILL,
    RECEIVABLE_PROVISION_RATE_LIVE_PAY_ON_RECEIPT,
    _banded_rate,
)

TT = dt.datetime(2030, 1, 1)
DD, SC = "direct_debit", "standard_credit"


def _post_year(book, acct, first, *, months, unpaid_months=(), amount=100.0):
    for m in range(months):
        day = first + dt.timedelta(days=30 * m)
        book.post(LedgerEvent(f"{acct}-b{m}", acct, LedgerEventType.BILL_DEBIT, amount, day, TT))
        if m not in unpaid_months:
            book.post(LedgerEvent(f"{acct}-p{m}", acct, LedgerEventType.PAYMENT_CREDIT, amount,
                                  day + dt.timedelta(days=10), TT))


def _latest(obs):
    """Each account-year's latest reading, as `default_belief` and `tabulate` take it."""
    out = {}
    for o in obs:
        key = (o.account_id, o.year_start)
        if key not in out or o.resolved_on > out[key].resolved_on:
            out[key] = o
    return out


def _observe(book, as_of, methods):
    return observe_book(book, as_of=as_of, payment_method_of=lambda a, d: methods.get(a),
                        arrears_state_at=lambda a, d: "no_debt")


def test_a_persistent_debt_is_charged_although_later_payments_clear_its_first_bills():
    """FIFO puts a rolling balance's debt on its NEWEST bills, so a reading of "this year's bills
    still unpaid" finds nothing on a household that has owed the same GBP 200 for two years. The
    charge follows the provision wherever FIFO puts it."""
    book = LedgerBook()
    first = dt.date(2017, 1, 1)
    _post_year(book, "LIVE", first, months=30, unpaid_months=(3, 4))
    obs = list(_latest(_observe(book, dt.date(2019, 1, 1), {"LIVE": SC})).values())
    assert len(obs) == 2 and not any(o.closed for o in obs)
    assert sum(o.charge_gbp for o in obs) > 0.0, obs
    # Every pound of the 200 is still owed and live at the second year's end: provisioned on the
    # live pay-on-receipt row at the age FIFO gives it, and no more than that.
    on = obs[-1].resolved_on
    unpaid = fifo_unpaid_bills(book.ledger("LIVE"), on)
    assert round(sum(g for _, g in unpaid), 2) == 200.0
    expected = sum(g * _banded_rate(RECEIVABLE_PROVISION_RATE_LIVE_PAY_ON_RECEIPT, (on - d).days)
                   for d, g in unpaid)
    assert abs(sum(o.charge_gbp for o in obs) - expected) < 0.02


def test_a_closed_accounts_debt_is_charged_on_the_final_bill_row_in_the_year_it_left():
    book = LedgerBook()
    first = dt.date(2017, 1, 1)
    _post_year(book, "GONE", first, months=12, unpaid_months=(10, 11))
    _post_year(book, "STAY", first, months=30, unpaid_months=(10, 11))
    # Each account's FIRST reading of the year: STAY's is re-read a year on, when FIFO has moved the
    # debt onto its second year's bills.
    obs = {}
    for o in _observe(book, dt.date(2019, 1, 1), {"GONE": SC, "STAY": SC}):
        if o.year_start == first:
            obs.setdefault(o.account_id, o)
    gone = obs["GONE"]
    assert gone.closed and gone.resolved_on > first + dt.timedelta(days=365)
    unpaid = fifo_unpaid_bills(book.ledger("GONE"), gone.resolved_on)
    assert gone.charge_gbp == round(sum(
        g * _banded_rate(RECEIVABLE_PROVISION_RATE_FINAL_BILL, (gone.resolved_on - d).days)
        for d, g in unpaid), 2)
    # The same unpaid money on a live account is provisioned several times lower.
    assert gone.charge_gbp > 2 * obs["STAY"].charge_gbp > 0.0, (gone, obs["STAY"])


def test_an_outcome_is_not_observed_before_the_company_could_know_it():
    book = LedgerBook()
    first = dt.date(2017, 1, 1)
    _post_year(book, "A", first, months=24, unpaid_months=(3,))
    end = first + dt.timedelta(days=365)
    assert [o for o in _observe(book, end - dt.timedelta(days=1), {"A": SC})] == []
    assert [o.resolved_on for o in _observe(book, end, {"A": SC})] == [end]


def _year(acct, method, share, resolved, billed=1200.0, state="no_debt"):
    return AccountYear(acct, method, state, resolved - dt.timedelta(days=365), resolved,
                       billed, False, round(billed * share, 2))


def _belief(book, decided_on, state="no_debt"):
    return default_belief(book, decided_on=decided_on, arrears_state=state)


def test_a_state_defaulting_at_twice_the_prior_moves_and_one_at_the_prior_does_not():
    resolved = dt.date(2019, 6, 1)
    after = resolved + dt.timedelta(days=1)
    p = PRIOR_LOSS_RATE
    book = ([_year(f"W{i}", DD, 2 * p, resolved, state="worsening") for i in range(20)]
            + [_year(f"S{i}", SC, p, resolved) for i in range(20)])
    hot, flat = _belief(book, after, "worsening"), _belief(book, after, "no_debt")
    assert hot.account_years == 20 and hot.rate > 1.9 * p, hot
    assert abs(flat.rate - p) < 1e-9, flat


def test_a_decision_dated_before_any_outcome_resolved_sees_only_the_prior():
    resolved = dt.date(2019, 6, 1)
    book = [_year(f"D{i}", DD, 0.30, resolved) for i in range(50)]
    for decided_on in (resolved - dt.timedelta(days=1), resolved):
        b = _belief(book, decided_on)
        assert b.rate == PRIOR_LOSS_RATE and b.account_years == 0, (decided_on, b)


def test_the_belief_can_land_above_at_and_below_its_prior():
    """The partition: a learner that could only ever raise (or only lower) the prior passes the
    twice-the-prior control above and is still wrong."""
    resolved = dt.date(2019, 6, 1)
    after = resolved + dt.timedelta(days=1)
    p = PRIOR_LOSS_RATE
    rates = {share: _belief([_year(f"A{i}", DD, share, resolved) for i in range(10)], after).rate
             for share in (0.0, p, 3 * p)}
    assert rates[0.0] < p and abs(rates[p] - p) < 1e-9 and rates[3 * p] > p, rates


def test_the_belief_is_one_number_for_every_payment_method_in_a_state():
    """The director's 2026-09-23 line: the price may not depend on how a household pays. A book
    whose standard-credit accounts default heavily still gives a direct-debit account in the same
    state the same belief -- there is no argument through which a method could ask for its own."""
    import inspect
    resolved = dt.date(2019, 6, 1)
    book = ([_year(f"S{i}", SC, 0.20, resolved) for i in range(10)]
            + [_year(f"D{i}", DD, 0.0, resolved) for i in range(10)])
    assert "payment_method" not in inspect.signature(default_belief).parameters
    assert _belief(book, resolved + dt.timedelta(days=1)).account_years == 20


# --------------------------------------------------------------------------- #
# The reach: the run's door -> the rate chain -> the price, behind the policy  #
# --------------------------------------------------------------------------- #

def _chain_rate(default_belief_rate):
    # The DOOR, which is what the run calls -- the desk behind it is not enough.
    from company.interfaces.renewal_rate_chain import decide_renewal_rate
    settled = [{"customer_id": "C0001", "commodity": "electricity",
                "settlement_date": f"2020-{m:02d}-15", "term_start": "2020-01-01",
                "consumption_kwh": 250.0, "revenue_gbp": 45.0, "net_margin_gbp": 1.0,
                "margin_gbp": 5.0, "settlement_periods_folded": 48} for m in range(1, 13)]
    return decide_renewal_rate(
        customer_id="C0001", billing_account="C0001", commodity="electricity",
        term_start="2021-01-01", tariff_type="fixed", term_index=2,
        struck_unit_rate_gbp_per_mwh=200.0, portfolio_margin_rates=[],
        prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0, is_domestic=False,
        settled_records=settled, customer={"metering": "NHH", "smart_meter": False},
        default_belief_rate=default_belief_rate,
    ).unit_rate_gbp_per_mwh


def test_the_book_rate_reaches_the_price_only_when_the_policy_prices_on_it():
    import dataclasses

    from company.policy.decision_policy import (
        DEFAULT_BELIEF_OWN_BOOK,
        DEFAULT_BELIEF_SEGMENT_TABLE,
        VALUE_ARM_POLICY,
        policy_scope,
    )

    rates = (0.0, 0.10)
    with policy_scope(dataclasses.replace(
            VALUE_ARM_POLICY, renewal_default_belief=DEFAULT_BELIEF_SEGMENT_TABLE)):
        off = [_chain_rate(r) for r in rates]
    with policy_scope(dataclasses.replace(
            VALUE_ARM_POLICY, renewal_default_belief=DEFAULT_BELIEF_OWN_BOOK)):
        on = [_chain_rate(r) for r in rates]
    assert off[0] == off[1], f"the segment-table policy read the book's rate: {off}"
    assert on[0] < on[1], f"a higher learned default did not raise the price: {on}"


def test_the_runs_door_answers_off_the_ledger_record_period_built():
    """End to end over the triad's own books: bills and cash posted by `record_period` (W2_11's
    draw, not a fixture), read back as a plain float through the door the run calls."""
    from background.live_payment_triad import LivePaymentTriad

    triad = LivePaymentTriad()
    ids = [f"DB{i}" for i in range(12)]
    for m in range(40):
        due = dt.date(2017 + (m // 12), m % 12 + 1, 28)
        for cid in ids:
            triad.record_period(customer_id=cid, due_date=due, amount_gbp=120.0,
                                income_stress_value="high", segment="resi")

    def method_of(account, on):
        return SC

    early = triad.default_belief_rate(dt.date(2017, 12, 1), "unknown", payment_method_of=method_of)
    assert early == PRIOR_LOSS_RATE
    late = triad.default_belief_rate(dt.date(2020, 4, 1), "unknown", payment_method_of=method_of)
    assert late != PRIOR_LOSS_RATE, "two resolved years of a stressed book moved nothing"


def test_on_the_book_rate_a_clean_prepayment_household_pays_what_a_clean_direct_debit_one_does():
    """The cost-shift the director ruled out on 2026-09-23, priced. On the segment-table path a
    clean prepayment household falls to the table's 2% while a clean direct-debit one reads its own
    zero, so it is offered a higher margin for how it pays (measured 2026-10-03: +2.00 GBP/MWh at a
    215 GBP/MWh rate). On the book's rate the two are one price."""
    from company.pricing.value_based_renewal import decide_margin

    base = dict(customer_id="X", arm="value_based", current_rate_gbp_per_mwh=215.0,
                base_rate_gbp_per_mwh=205.0, eac_kwh=2700, tenure_years=2.0,
                cost_to_serve_gbp_per_year=60.0, fixed_revenue_gbp_per_year=99.0,
                unpaid_bills_by_age=(), billed_last_year_gbp=580.0)
    margins = {m: decide_margin(**base, payment_method=m, default_belief_rate=0.02).margin_gbp_per_mwh
               for m in ("direct_debit", "standard_credit", "prepayment")}
    assert len(set(margins.values())) == 1, margins


def test_a_dd_the_supplier_stopped_is_provisioned_on_the_pay_on_receipt_row_from_its_notice_on():
    """PB8: the company's own desk stops a failing DD and the household then pays on receipt. Read
    once per account, the method never moved and the stopped household's debt stayed on the DD row,
    so the book's charge was the household's drawn channel, not the supplier's own mandate record.
    The year's covariate stays the method at its start: that is what a renewal then could see."""
    first = dt.date(2018, 1, 1)
    stop = dt.date(2018, 9, 1)
    asked: list = []

    def stopped(account, on):
        asked.append(on)
        return SC if on >= stop else DD

    def observe(method_of):
        book = LedgerBook()
        _post_year(book, "A", first, months=24, unpaid_months=(8, 9, 10))
        return observe_book(book, as_of=dt.date(2020, 6, 1), payment_method_of=method_of,
                            arrears_state_at=lambda a, d: "no_debt")

    def first_readings(obs):
        return [o for o in obs if o.resolved_on == o.year_start + dt.timedelta(days=365)
                or o.closed and not any(p.year_start == o.year_start and p.resolved_on < o.resolved_on
                                        for p in obs)]
    moved = first_readings(observe(stopped))
    never = first_readings(observe(lambda a, d: DD))
    assert asked and max(asked) <= dt.date(2020, 6, 1), "the register was asked past the decision date"
    assert any(d < stop for d in asked) and any(d >= stop for d in asked), (
        "the register was never asked on both sides of the stop, so the stop could not reach a charge")
    assert [o.payment_method for o in moved] == [DD, SC], (
        "a year's method is the one at its start: the stopped household's first year began on DD")
    assert moved[0].charge_gbp > never[0].charge_gbp, (
        "the stopped account's year-end debt was still provisioned on the direct-debit row")


def test_an_account_the_register_does_not_answer_for_is_not_learned_from():
    """The run's register answers `None` for its SME accounts: the resi price does not learn from
    them. `observe_book` used to turn that `None` into `""` and keep the year, so C6's GBP 75
    final-bill charge sat in the resi belief's `unknown` cell. The control runs over BOTH answers on
    the same book, so a reader that dropped every account would fail the first assertion."""
    def observe(methods):
        book = LedgerBook()
        _post_year(book, "SME", dt.date(2017, 1, 1), months=12, unpaid_months=(10, 11))
        _post_year(book, "HOME", dt.date(2017, 1, 1), months=12)
        return {o.account_id for o in _observe(book, dt.date(2019, 1, 1), methods)}

    assert observe({"SME": SC, "HOME": DD}) == {"SME", "HOME"}, "an answered account was not read"
    assert observe({"HOME": DD}) == {"HOME"}, "an account the register does not answer for was read"


def _paying_down(book, acct, first):
    """Year 1: two bills unpaid. Year 2: every bill paid, and the arrears cleared in month 14."""
    _post_year(book, acct, first, months=30, unpaid_months=(10, 11))
    book.post(LedgerEvent(f"{acct}-catchup", acct, LedgerEventType.PAYMENT_CREDIT, 200.0,
                          first + dt.timedelta(days=30 * 14 + 12), TT))


def test_an_account_paying_down_its_arrears_is_never_learned_as_a_negative_loss():
    """The defect in `df9792c57`: the year's whole charge (closing less opening provision) is
    negative on a household that clears last year's arrears, and one such account-year in a thin
    cell takes the belief below zero. Read by vintage, the release lowers LAST year's reading."""
    book = LedgerBook()
    first = dt.date(2017, 1, 1)
    for i in range(3):
        _paying_down(book, f"PD{i}", first)
    raw = _observe(book, dt.date(2019, 6, 1), {f"PD{i}": SC for i in range(3)})
    assert all(o.charge_gbp is not None and o.charge_gbp >= 0.0 for o in raw), raw
    # The rare branch is reachable: year 1 WAS read with a loss, and its later reading released it.
    first_reads = [o for o in raw if o.year_start == first and o.resolved_on == first + dt.timedelta(days=365)]
    revisions = [o for o in raw if o.year_start == first and o.resolved_on > first + dt.timedelta(days=365)]
    assert first_reads and all(o.charge_gbp > 0.0 for o in first_reads), first_reads
    assert revisions and all(o.charge_gbp == 0.0 for o in revisions), revisions
    # Year 2's own billing is all paid, so its loss is 0 -- not minus last year's provision.
    year2 = [o for o in raw if o.year_start == first + dt.timedelta(days=365)]
    assert year2 and all(o.charge_gbp == 0.0 for o in year2), year2
    # The cell is year-2 debtors only (arrears state at year 2's start): one account-year each,
    # the thin cell the defect showed on. The belief shrinks a 0.0 observation towards the prior.
    debtors = default_belief(raw, decided_on=dt.date(2019, 6, 1), arrears_state="no_debt")
    assert debtors.account_years == 3 and 0.0 <= debtors.rate < PRIOR_LOSS_RATE, debtors


def test_the_latest_readings_sum_to_the_telescoped_charge():
    """Nothing is lost or counted twice: an account's latest readings by year add up to what the
    old whole-year charge summed to over the same years -- its provision now, plus write-offs."""
    book = LedgerBook()
    first = dt.date(2017, 1, 1)
    _paying_down(book, "PD", first)
    _post_year(book, "ROLL", first, months=30, unpaid_months=(3, 4))
    on = dt.date(2019, 1, 1)
    latest = _latest(_observe(book, on, {"PD": SC, "ROLL": SC}))
    for acct in ("PD", "ROLL"):
        unpaid = fifo_unpaid_bills(book.ledger(acct), on)
        provision = sum(g * _banded_rate(RECEIVABLE_PROVISION_RATE_LIVE_PAY_ON_RECEIPT, (on - d).days)
                        for d, g in unpaid)
        mine = sum(o.charge_gbp for (a, _), o in latest.items() if a == acct)
        assert abs(mine - provision) < 0.02, (acct, mine, provision)


def test_a_negative_belief_is_refused_wherever_it_reaches_a_price():
    """The invariant as a class: a belief below 0 (or above 1) is refused by the producer and by the
    price that consumes it, whatever built it."""
    import pytest

    from company.compliance.domain_invariants import (
        ExpectedLossBeliefOutOfRangeError,
        check_expected_loss_belief_within_zero_and_one,
        refuse_expected_loss_belief_out_of_range,
    )
    assert check_expected_loss_belief_within_zero_and_one(0.0)
    assert check_expected_loss_belief_within_zero_and_one(PRIOR_LOSS_RATE)
    for bad in (-0.0083, 1.01, float("nan"), None):
        assert not check_expected_loss_belief_within_zero_and_one(bad), bad
    with pytest.raises(ExpectedLossBeliefOutOfRangeError, match="release"):
        refuse_expected_loss_belief_out_of_range(-0.0083, where="test")
    # The producer: a hand-built negative observation (the old whole-year charge) is refused.
    resolved = dt.date(2018, 1, 1)
    with pytest.raises(ExpectedLossBeliefOutOfRangeError):
        default_belief([_year("NEG", SC, -0.05, resolved)], decided_on=dt.date(2018, 2, 1),
                       arrears_state="no_debt")
    # The consumer, on the policy that prices with the book's rate.
    import dataclasses

    from company.policy.decision_policy import (
        DEFAULT_BELIEF_OWN_BOOK,
        VALUE_ARM_POLICY,
        policy_scope,
    )
    with policy_scope(dataclasses.replace(VALUE_ARM_POLICY,
                                          renewal_default_belief=DEFAULT_BELIEF_OWN_BOOK)):
        assert _chain_rate(0.0) is not None
        with pytest.raises(ExpectedLossBeliefOutOfRangeError):
            _chain_rate(-0.0083)
