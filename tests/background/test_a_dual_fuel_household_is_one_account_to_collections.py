"""A dual-fuel household is one account to collections: one ledger, one journey, each fuel's bill
still its own item on it (SEAT_FINDING_A_DUAL_FUEL_HOUSEHOLD_IS_TWO_ACCOUNTS_IN_COLLECTIONS_
2026-10-25, split 1).

Defect each control names:

  * `test_both_legs_post_to_one_account_and_keep_their_own_bills` -- the triad keys the ledger by
    supply point, so `C1` and `C1g` are two journeys, two reminder ladders, for one household; or
    the merge loses a leg's bill because the two share a period.
  * `test_the_journey_waits_for_the_leg_still_to_post` -- whole terms post in turn, electricity
    before gas, so walking the account on the electricity leg alone steps past gas bills not yet on
    the ledger. The partition is asserted first: a single-fuel household in the same book IS walked
    mid-run, so a walk that never happens cannot pass for one that waits.
  * `test_held_cash_crosses_in_date_order_whichever_leg_it_came_from` -- the account's held lumps
    were appended in arrival order, so electricity cash held for its whole term crossed before gas
    cash dated earlier, the journey was walked past the gas day, and a step already taken there
    read as dunning a cleared debt (ACC-SYN-2016-048, reminder_2 on 2020-10-12, every default-book
    run at c5a3e96fe). The partition is asserted first: an earlier lump DID arrive behind a later
    one, so a book that never mixes the legs' cash cannot pass for one that orders it.
"""
from __future__ import annotations

from datetime import date

from background.live_payment_triad import LivePaymentTriad

_HOUSEHOLDS = [f"RESI{i:05d}" for i in range(40)]
_SINGLE = "SOLO00001"


def _post(triad, leg: str, months) -> None:
    for m in months:
        triad.record_period(customer_id=leg, due_date=date(2020, m, 28), amount_gbp=120.0,
                            income_stress_value="high", segment="resi",
                            fuel="gas" if leg.endswith("g") else "electricity")


def test_both_legs_post_to_one_account_and_keep_their_own_bills():
    triad = LivePaymentTriad()
    for h in _HOUSEHOLDS:  # the run's order: a whole electricity term, then the gas term
        _post(triad, h, range(1, 13))
        _post(triad, h + "g", range(1, 13))
    journeys = triad.collections_journeys(date(2021, 6, 30))
    accounts = {j["account_id"] for j in journeys}
    assert accounts, "no household ever entered collections: the control asks nothing"
    assert not [a for a in accounts if a.endswith("g")], "a gas leg has a journey of its own"
    ledgers = set(triad._ledger_book.accounts())
    assert ledgers == {f"ACC-{h}" for h in _HOUSEHOLDS}, "a leg still posts to a ledger of its own"
    refs = {r.invoice_ref for r in triad.records if r.account_id == f"ACC-{_HOUSEHOLDS[0]}"}
    assert len(refs) == 24, f"two legs' bills for one period collapsed into one item: {len(refs)}"


def test_the_journey_waits_for_the_leg_still_to_post():
    triad = LivePaymentTriad()
    pending = {h: {h, h + "g"} for h in _HOUSEHOLDS}
    triad.legs_still_posting = lambda household: pending.get(household, {household})
    walked = triad._consumer.collections_journeys._through
    _post(triad, _SINGLE, range(1, 13))
    assert walked.get(f"ACC-{_SINGLE}") is not None, (
        "a single-fuel household was never walked mid-run: the wait cannot be told from no walk")
    for h in _HOUSEHOLDS:
        _post(triad, h, range(1, 13))
    early = {h: walked.get(f"ACC-{h}") for h in _HOUSEHOLDS if walked.get(f"ACC-{h}")}
    assert early == {}, f"walked on electricity alone, before any gas bill posted: {early}"
    for h in _HOUSEHOLDS:
        _post(triad, h + "g", range(1, 13))
    assert all(walked.get(f"ACC-{h}") for h in _HOUSEHOLDS), "the account was never walked"
    assert max(walked[f"ACC-{h}"] for h in _HOUSEHOLDS) <= date(2020, 12, 28)


def test_held_cash_crosses_in_date_order_whichever_leg_it_came_from():
    triad = LivePaymentTriad()
    triad.legs_still_posting = lambda household: {household, household + "g"}
    walked = triad._consumer.collections_journeys._through
    behind, past = [], []
    hold, cross = triad._hold, triad._cross_settlement

    def _hold(item):
        held = triad._held_settlements.get(item[3], [])
        if any(other[0] > item[0] for other in held):
            behind.append(item[3])
        hold(item)

    def _cross(item):
        if walked.get(item[3]) is not None and item[0] <= walked[item[3]]:
            past.append((item[3], item[0], walked[item[3]]))
        cross(item)

    triad._hold, triad._cross_settlement = _hold, _cross
    for h in _HOUSEHOLDS:
        _post(triad, h, range(1, 13))
        _post(triad, h + "g", range(1, 13))
    triad.collections_journeys(date(2021, 6, 30))
    assert behind, "no earlier lump arrived behind a later one held: the control asks nothing"
    assert past == [], f"cash crossed on a day its account was already walked past: {past[:3]}"
