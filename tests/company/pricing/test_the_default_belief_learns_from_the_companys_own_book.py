"""The default belief learns from what the company itself was not paid, and only from what it knew.

Defect each control names:
  * the book is read but the belief never moves off the prior (a cell defaulting at twice its prior
    leaves the estimate where it was);
  * the belief reads outcomes that resolved AFTER the decision (look-ahead);
  * a persistent debtor reads as clean because FIFO moved its debt onto its newest bills;
  * a closed account's unpaid money is provisioned on the live row (the 5-50x understatement the
    final-bill row exists to stop);
  * an outcome is read before the company could know it.
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


def _observe(book, as_of, methods):
    return observe_book(book, as_of=as_of, payment_method_of=methods.get,
                        arrears_state_at=lambda a, d: "no_debt")


def test_a_persistent_debt_is_charged_although_later_payments_clear_its_first_bills():
    """FIFO puts a rolling balance's debt on its NEWEST bills, so a reading of "this year's bills
    still unpaid" finds nothing on a household that has owed the same GBP 200 for two years. The
    charge follows the provision wherever FIFO puts it."""
    book = LedgerBook()
    first = dt.date(2017, 1, 1)
    _post_year(book, "LIVE", first, months=30, unpaid_months=(3, 4))
    obs = _observe(book, dt.date(2019, 1, 1), {"LIVE": SC})
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
    obs = {o.account_id: o for o in _observe(book, dt.date(2019, 1, 1), {"GONE": SC, "STAY": SC})
           if o.year_start == first}
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
        VALUE_ARM_POLICY,
        policy_scope,
    )

    rates = (0.0, 0.10)
    with policy_scope(VALUE_ARM_POLICY):
        off = [_chain_rate(r) for r in rates]
    with policy_scope(dataclasses.replace(
            VALUE_ARM_POLICY, renewal_default_belief=DEFAULT_BELIEF_OWN_BOOK)):
        on = [_chain_rate(r) for r in rates]
    assert off[0] == off[1], f"the default policy read the book's rate: {off}"
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

    def method_of(account):
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
