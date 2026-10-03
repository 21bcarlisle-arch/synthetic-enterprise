"""The renewal price reads what the household has and has not paid -- R15 proof.

Director, 2026-10-03: "The pricing decision is blind to payment history. renewal_margin_uplift
forwards neither arrears nor credit risk to decide_margin... Fix it, and make arrears move the
bad-debt cost, not only the churn hazard."

THREE THINGS CAN GO WRONG, and each has a test that a mutation of it turns red:

  1. THE HISTORY DOES NOT ARRIVE. Every argument has a default, so an adapter or a door that drops
     one is green everywhere and prices blind -- which is exactly how this was found.
  2. ARREARS MOVE ONLY ONE SIDE. The money already owed is cheaper to a supplier that keeps the
     account live than to one that lets it close (Centrica ARA 2025 Note 17, live against
     final-bill rows). Priced alone, that term discounts a debtor to keep them, so the
     non-payment still to come must be priced too, and it must grow with the price.
  3. THE CONTROL ARM LOOKS. A flat-rule run that reads the ledger is no longer the control.
"""
from __future__ import annotations

import datetime as dt

from company.billing.account_ledger import AccountLedger, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import fifo_unpaid_bills
from company.crm.churn_model import ARREARS_STATE_NO_DEBT, ARREARS_STATE_WORSENING
from company.interfaces import renewal_rate_chain as door
from company.policy.decision_policy import CURRENT_POLICY, VALUE_ARM_POLICY, policy_scope
from company.pricing import value_based_renewal as vbr

TT = dt.datetime(2024, 1, 1, 12, 0, 0)

#: Two years of monthly GBP 500 bills, none paid: the shape of the account that cost the value arm
#: most of its worst seed (PROS-2016-0098, about GBP 12k of arrears in both arms).
DEBTOR = tuple((500.0, 30 * k) for k in range(1, 25))
MODEST = ((100.0, 120), (100.0, 75), (100.0, 45))

BASE = dict(
    customer_id="X", current_rate_gbp_per_mwh=250.0, base_rate_gbp_per_mwh=230.0, eac_kwh=2700,
    tenure_years=2.0, cost_to_serve_gbp_per_year=60.0, renewal_year=2019,
    annual_revenue_gbp=675.0, fixed_revenue_gbp_per_year=90.0, expected_periods=3.0,
)


def _settled(account: str = "C1", year: int = 2020) -> list[dict]:
    return [
        {"customer_id": account, "commodity": "electricity",
         "settlement_date": f"{year}-{m:02d}-15", "term_start": f"{year}-01-01",
         "consumption_kwh": 250.0, "revenue_gbp": 45.0, "net_margin_gbp": 1.0,
         "margin_gbp": 5.0, "settlement_periods_folded": 48}
        for m in range(1, 13)
    ]


def _rate(**over) -> float:
    args = dict(
        customer_id="C1", billing_account="C1", commodity="electricity",
        term_start="2021-01-01", tariff_type="fixed", term_index=2,
        struck_unit_rate_gbp_per_mwh=200.0, portfolio_margin_rates=[],
        prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0, is_domestic=False,
        settled_records=_settled(), customer={"metering": "NHH", "smart_meter": False},
    )
    return door.decide_renewal_rate(**{**args, **over}).unit_rate_gbp_per_mwh


def _receivable(bills, billed=6000.0) -> dict:
    return {"unpaid_bills_by_age": bills, "billed_last_year_gbp": billed}


# ── 1. the history arrives ──────────────────────────────────────────────────────────────────

def test_the_door_carries_the_unpaid_bills_all_the_way_to_the_price():
    """Against the SAME ledger with nothing owed, so only the unpaid bills differ -- compared with
    no ledger at all, the billed total alone would move the price and hide a dropped bill list."""
    with policy_scope(VALUE_ARM_POLICY):
        paid_up = _rate(receivable=_receivable((), billed=540.0), payment_method="direct_debit")
        owing = _rate(receivable=_receivable(MODEST, billed=540.0), payment_method="direct_debit")
    assert owing != paid_up, "the unpaid bills crossed the door and moved nothing"


def test_the_door_carries_the_arrears_state_all_the_way_to_the_price():
    """A HOUSEHOLD: Ofgem CIM Table 56 is a domestic survey and the churn model applies it to
    households only, so a business account's price rightly does not move on it."""
    household = dict(is_domestic=True, segment="resi")
    with policy_scope(VALUE_ARM_POLICY):
        steady = _rate(arrears_state=ARREARS_STATE_NO_DEBT, **household)
        worse = _rate(arrears_state=ARREARS_STATE_WORSENING, **household)
    assert steady != worse, "the arrears state crossed the door and moved nothing"


def test_the_control_arm_does_not_read_the_ledger():
    with policy_scope(CURRENT_POLICY):
        blind = _rate()
        seen = _rate(receivable=_receivable(DEBTOR), payment_method="standard_credit",
                     arrears_state=ARREARS_STATE_WORSENING)
    assert seen == blind


# ── 2. arrears move the bad-debt cost, on both sides ─────────────────────────────────────────

def test_every_shape_of_the_debt_already_owed_is_reachable():
    shapes = {
        "nothing owed": vbr.receivable_provision_rates((), "direct_debit"),
        "priced": vbr.receivable_provision_rates(MODEST, "direct_debit"),
        "no published row": vbr.receivable_provision_rates(MODEST, "prepayment"),
    }
    assert shapes["nothing owed"] == (0.0, 0.0, None)
    stay, leave, why = shapes["priced"]
    assert 0.0 < stay < leave and why is None
    assert shapes["no published row"][:2] == (0.0, 0.0) and "prepayment" in shapes["no published row"][2]


def test_letting_an_account_close_never_makes_its_debt_cheaper():
    for row in (vbr.RECEIVABLE_PROVISION_RATE_LIVE_DIRECT_DEBIT,
                vbr.RECEIVABLE_PROVISION_RATE_LIVE_PAY_ON_RECEIPT):
        for days in range(0, 400):
            assert (vbr._banded_rate(vbr.RECEIVABLE_PROVISION_RATE_FINAL_BILL, days)
                    > vbr._live_rate(row, days)), (row, days)


def test_the_debt_already_owed_is_weighted_by_the_chance_the_account_stays_live():
    d = vbr.decide_margin(**BASE, arm=vbr.VALUE_BASED, unpaid_bills_by_age=MODEST,
                          payment_method="direct_debit", billed_last_year_gbp=675.0)
    stay, leave, _ = vbr.receivable_provision_rates(MODEST, "direct_debit")
    assert 0.0 < d.p_retain < 1.0
    assert abs(d.receivable_expected_loss_gbp
               - (d.p_retain * stay + (1.0 - d.p_retain) * leave)) < 1e-9
    assert stay < d.receivable_expected_loss_gbp < leave


def test_a_direct_debit_bill_unpaid_past_re_presentation_is_owed_as_pay_on_receipt():
    dd = vbr.RECEIVABLE_PROVISION_RATE_LIVE_DIRECT_DEBIT
    window = vbr.DIRECT_DEBIT_REPRESENTATION_WINDOW_DAYS
    assert vbr._live_rate(dd, window - 1) == vbr._banded_rate(dd, window - 1)
    assert vbr._live_rate(dd, window) == vbr._banded_rate(
        vbr.RECEIVABLE_PROVISION_RATE_LIVE_PAY_ON_RECEIPT, window)
    assert vbr._live_rate(dd, window) != vbr._banded_rate(dd, window)


def test_both_bad_debt_branches_are_reachable_and_the_ledger_replaces_the_prior():
    """The prior (never asked) and the account's own record (asked) are each taken, and they
    disagree: a clean direct-debit payer's own record is the published 0% on a current DD bill."""
    prior = vbr.decide_margin(**BASE, arm=vbr.VALUE_BASED)
    clean = vbr.decide_margin(**BASE, arm=vbr.VALUE_BASED, unpaid_bills_by_age=(),
                              payment_method="direct_debit", billed_last_year_gbp=675.0)
    owing = vbr.decide_margin(**BASE, arm=vbr.VALUE_BASED, unpaid_bills_by_age=MODEST,
                              payment_method="direct_debit", billed_last_year_gbp=675.0)
    assert prior.costs.bad_debt_gbp > 0.0
    assert clean.costs.bad_debt_gbp == 0.0
    assert owing.costs.bad_debt_gbp > prior.costs.bad_debt_gbp
    assert owing.receivable_expected_loss_gbp > 0.0 == clean.receivable_expected_loss_gbp


def test_the_non_payment_still_to_come_grows_with_the_price():
    def bad_debt_at(level: float) -> float:
        return vbr.decide_margin(
            **BASE, arm=vbr.FLAT_AT_LEVEL, flat_level_gbp_per_mwh=level,
            unpaid_bills_by_age=MODEST, payment_method="standard_credit",
            billed_last_year_gbp=675.0).costs.bad_debt_gbp
    assert bad_debt_at(40.0) > bad_debt_at(20.0) > 0.0


def test_a_household_that_owes_is_priced_up_not_down():
    """The modest debtor -- the common case -- pays MORE than the same household paying cleanly.
    (The extreme debtor is priced down, by the published table's live-vs-final gap; that is
    reported as a practitioner question in the stretch log, not asserted here as right.)"""
    clean = vbr.decide_margin(**BASE, arm=vbr.VALUE_BASED, unpaid_bills_by_age=(),
                              payment_method="direct_debit", billed_last_year_gbp=675.0)
    owing = vbr.decide_margin(**BASE, arm=vbr.VALUE_BASED, unpaid_bills_by_age=MODEST,
                              payment_method="direct_debit", billed_last_year_gbp=675.0)
    assert owing.margin_gbp_per_mwh > clean.margin_gbp_per_mwh


# ── the ledger read the price is built from ─────────────────────────────────────────────────

def test_fifo_leaves_each_unpaid_bill_at_its_own_age():
    led = AccountLedger("A")
    for i, day in enumerate((1, 31, 61)):
        led.post(LedgerEvent(f"b{i}", "A", LedgerEventType.BILL_DEBIT, 100.0,
                             dt.date(2024, 1, 1) + dt.timedelta(days=day - 1), TT))
    led.post(LedgerEvent("p", "A", LedgerEventType.PAYMENT_CREDIT, 150.0, dt.date(2024, 3, 5), TT))
    unpaid = fifo_unpaid_bills(led, dt.date(2024, 4, 1))
    # The first bill is paid, half the second, none of the third -- and the third is NOT aged
    # from the first bill's date, which is what a whole-balance read would have done.
    assert unpaid == [(dt.date(2024, 1, 31), 50.0), (dt.date(2024, 3, 1), 100.0)]
