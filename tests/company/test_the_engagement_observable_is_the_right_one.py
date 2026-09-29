"""PB6 VERIFY: the four ways the payment-method observable could be wrong and every control stayed green.

A mutation battery over `test_the_engagement_observable_crosses_the_seam.py` (2026-09-29) killed
4 of 9 non-equivalent mutations. The survivors were: the seam dropping `fuel`, the fail-safe
branch never reached, the standard-credit rate, the normalising base, and the run passing `None`
for the method. Each test below names the survivor it kills; the last survivor's control lives in
`tests/simulation/test_run_phase2b_hands_the_company_its_payment_method.py`, where the gate's
stem selection runs it on any commit that touches the run.
"""
from __future__ import annotations

import pytest

from company.crm.enriched_churn_estimate import payment_method_engagement_factor
from company.interfaces.sim_interface import LiveSimInterface

_METHODS = ("direct_debit", "standard_credit", "prepayment")


def test_the_seam_answers_for_the_fuel_it_was_asked_about():
    """SURVIVOR: `get_payment_method` dropping `fuel` and answering electricity for every account.

    A household's electricity and gas are two accounts with two mandates, and the world draws them
    separately (72% vs 75% direct debit) -- they differ on 160 of the first 400 ids. The existing
    agreement test asked only about electricity, so a seam that ignored the fuel agreed with it.
    """
    from simulation.household_segments import payment_channel_for_customer

    live = LiveSimInterface()
    ids = [f"CUST{i:05d}" for i in range(200)]
    differ = [cid for cid in ids
              if live.get_payment_method(cid, "gas") != live.get_payment_method(cid, "electricity")]
    assert differ, "no account pays for its gas differently from its electricity -- fuel is ignored"
    for cid in ids:
        assert live.get_payment_method(cid, "gas") == payment_channel_for_customer(cid, "gas").value


def test_the_fail_safe_branch_is_reached_and_answers_direct_debit(monkeypatch):
    """SURVIVOR: the fallback returning prepayment. The existing test passes `None` as the id, and
    `None` never reaches the fallback -- the world's draw seeds a stream from any value, so it
    resolved `None` like any other id and answered direct debit by chance. The branch has to be
    TAKEN before what it returns can be asserted.
    """
    import simulation.household_segments as world

    def unresolvable(*_args, **_kwargs):
        raise LookupError("no CRM record")

    monkeypatch.setattr(world, "payment_channel_for_customer", unresolvable)
    assert LiveSimInterface().get_payment_method("CUST00001") == "direct_debit"


def test_the_published_ordering_of_the_three_channels_holds():
    """SURVIVOR: the standard-credit rate. Only prepayment-against-direct-debit was asserted, so
    standard credit could be set to prepayment's rate unseen. Ofgem CIM w6 puts standard credit at
    or above direct debit (5.7% vs 5.6%) and both well above prepayment (3.1%).
    """
    f = {m: payment_method_engagement_factor(m) for m in _METHODS}
    assert f["standard_credit"] >= f["direct_debit"] > f["prepayment"], f


@pytest.mark.parametrize("fuel", ["electricity", "gas"])
def test_a_book_of_average_composition_is_left_where_it_was(fuel):
    """SURVIVOR: the normalising base. The factor's docstring promises that a book of average mix
    is unchanged and only the MIX moves the answer; nothing asserted it, so dividing by any other
    base -- a blanket uplift wearing a payment method's name -- kept every ratio and every test.

    The mix is the company's own, read through the seam over 4,000 accounts. At the real mix the
    average factor is 0.993 (electricity) and 1.000 (gas); the tolerance admits the CIM table's
    own rounding (rates to 0.1pp against a 5.3% base) and sampling, and nothing like the ~1.7 a
    wrong base gives.
    """
    live = LiveSimInterface()
    n = 4000
    mean = sum(payment_method_engagement_factor(live.get_payment_method(f"CUST{i:05d}", fuel))
               for i in range(n)) / n
    assert abs(mean - 1.0) < 0.03, f"{fuel}: book-average engagement factor {mean:.4f}, not ~1.0"

