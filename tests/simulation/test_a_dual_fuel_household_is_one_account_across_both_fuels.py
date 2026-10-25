"""A dual-fuel household is one account across both fuels: one bill, one direct debit, one move, one
switch, and its credit offset and closing balance read per fuel contract (B13 L1).

One run of phase 4c over the real loop to 2017-12-31, with moves on and the company offering to move
households with it, so the run walks its dual households through a bill, a mid-life credit offset
(dac6b90d7), a move-out and a switch. A credit stays on its own fuel's contract (SLC 27.16,
home_moves.md s.8.8a), so the account's balance is the sum of the two legs, never one leg netted
against the other.

Where the run splits a household it is not patched round here. The two splits measured on
2026-10-25 are in docs/staging/SEAT_FINDING_A_DUAL_FUEL_HOUSEHOLD_IS_TWO_ACCOUNTS_IN_COLLECTIONS_
2026-10-25.md: collections runs a journey per fuel leg (189 of 354 dual households, 80 of them two
journeys open at once), and a gas leg already ended at a move to a home with no gas is listed again
when the household switches a year later (1). The first is fixed: the triad keys its ledger by
billing account. The second is a non-strict `xfail` below, so a fix turns it into a pass. The
direct-debit split is NOT a defect of this kind: the payment-channel draw lets the fuels differ in
the 3-point band between their published direct-debit shares (`payment_channel_for_customer`), and
the control asserts that band is the only route.

Window measured 2026-10-25: 354 dual households; 28 move-outs; 65 households switching away; 95
mid-life credits coming off a dual leg's next paid bill (89 gas, 6 electricity); 11 households in
the channel band, all electricity non-DD beside gas on DD; 2 gas legs ended at a move to a home
with no gas. No dual leaver closed with a credit on one fuel and a debt on the other in this
window, so the per-fuel refund is asserted on the legs that closed in credit, not on a mixed one.
"""
from __future__ import annotations

import collections
import dataclasses
import random

import pytest

import simulation.run_phase2b as run
import simulation.run_phase4c_on_phase2b as p4c
from company.policy.decision_policy import CURRENT_POLICY, policy_scope
from simulation.arrears_engine import resolved_settlement
from simulation.household import (
    household_of,
    households_whose_account_closed,
    supply_points_that_left,
)
from simulation.household_segments import DIRECT_DEBIT_SHARE_BY_FUEL

REPORT_END = "2017-12-31"


@pytest.fixture(scope="module")
def walked():
    patch = pytest.MonkeyPatch()
    patch.setattr(run, "moves_active", lambda: True)
    patch.setattr(run, "move_with_us_active", lambda: True)
    patch.setattr(run, "take_up_scale", lambda: 1.0)
    policy = dataclasses.replace(CURRENT_POLICY, move_with_us_offers=True)
    try:
        with policy_scope(policy):
            result = p4c.main(report_end=REPORT_END, policy=policy)
    finally:
        patch.undo()
    phase2b = result["phase2b"]
    bills = result["bills"]
    churned = supply_points_that_left(households_whose_account_closed(phase2b),
                                      {b["customer_id"] for b in bills})
    _, _, credited = resolved_settlement(bills, phase2b["per_customer_behavioral"], churned)
    result["_credited"] = credited
    return result


def _dual_households(result) -> set[str]:
    fuels = collections.defaultdict(set)
    for row in result["phase2b"]["account_state_log"]:
        fuels[household_of(row["customer_id"])].add(row["commodity"])
    return {h for h, f in fuels.items() if f >= {"electricity", "gas"}}


def _last_supplied(result) -> dict[str, str]:
    last: dict[str, str] = {}
    for row in result["phase2b"]["account_state_log"]:
        last[row["customer_id"]] = max(last.get(row["customer_id"], ""), row["term_end"][:10])
    return last


def _gas_ended_at_a_move_to_no_gas(result) -> dict[str, str]:
    """Household -> move date, where it moved with us to a home with no mains gas (home_moves.md
    s.8.7): its gas leg ends at the move and it arrives electricity-only. One account still."""
    return {r["billing_account"]: r["move_out_date"]
            for r in result["phase2b"].get("move_with_us_log", [])
            if r.get("supplied_at_new_home") and r.get("destination_takes_gas") is False}


def _in_the_channel_band(household: str) -> bool:
    """The household's electricity-stream uniform falls between the two fuels' direct-debit shares,
    the one band in which `payment_channel_for_customer` lets the fuels pay differently."""
    u = random.Random(f"paychannel_{household}_electricity").random()
    return DIRECT_DEBIT_SHARE_BY_FUEL["electricity"] <= u < DIRECT_DEBIT_SHARE_BY_FUEL["gas"]


def _bills_by_household_month(result):
    dual = _dual_households(result)
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for b in result["bills"]:
        h = household_of(b["customer_id"])
        if h in dual:
            out[(h, b["period_end"][:7])][b["commodity"]].append(b)
    return out


def test_every_route_this_file_asserts_on_is_taken(walked):
    """Defect: a window in which no dual household moves, switches, takes a credit offset, closes,
    sits in the channel band or moves to a home with no gas passes every control below unread."""
    dual = _dual_households(walked)
    p = walked["phase2b"]
    moved = {m["household"] for m in p["home_move_outs"]} & dual
    switched = {d["household"] for d in p["leg_departures"]} & dual
    offset_fuels = {k[2] for k, v in walked["_credited"].items() if household_of(k[0]) in dual
                    and any(c["kind"] == "credit" for c in v)}
    closed = {household_of(c) for c in walked["closing_balances"]} & dual
    in_band = {h for h in dual if _in_the_channel_band(h)}
    assert (dual and moved and switched and offset_fuels == {"electricity", "gas"} and closed
            and in_band and _gas_ended_at_a_move_to_no_gas(walked)), (
        len(dual), len(moved), len(switched), offset_fuels, len(closed), len(in_band))


def test_both_legs_carry_the_households_one_account(walked):
    """Defect: a gas leg billed under an account of its own (`C1g` as its own billing account)."""
    rows = walked["phase2b"]["account_state_log"]
    assert [r for r in rows if r["billing_account"] != household_of(r["customer_id"])] == []


def test_a_households_two_fuels_are_billed_for_one_period(walked):
    """Defect: the fuels of one account on two billing cycles, so the household gets two bills a
    month for two different periods. The only exception is the gas leg's last bill at a move to a
    home with no gas, which stops at the move while the electricity bill runs on."""
    no_gas = _gas_ended_at_a_move_to_no_gas(walked)
    apart = []
    for (h, month), legs in _bills_by_household_month(walked).items():
        if len(legs) < 2:
            continue
        periods = {fuel: {(b["period_start"], b["period_end"]) for b in bills}
                   for fuel, bills in legs.items()}
        if periods["electricity"] != periods["gas"]:
            apart.append((h, month, periods))
    explained = [(h, m) for h, m, _ in apart if no_gas.get(h, "")[:7] == m]
    assert len(explained) == len(apart), [a for a in apart if (a[0], a[1]) not in explained]


def test_a_household_pays_both_fuels_one_way_outside_the_published_band(walked):
    """Defect: the two fuels drawn on independent streams (the pre-2026-09-29 world, 49 of 80
    households disagreeing), so one household holds a DD on one fuel and pays the other some other
    way. Inside the 3-point band the fuels' published DD shares differ, and there the gas leg, the
    higher share, is the one on direct debit."""
    split = collections.defaultdict(set)
    for (h, _m), legs in _bills_by_household_month(walked).items():
        if len(legs) < 2:
            continue
        e = {b["payment_channel"] for b in legs["electricity"]}
        g = {b["payment_channel"] for b in legs["gas"]}
        if e != g:
            split[h].add((frozenset(e), frozenset(g)))
    assert split, "no household paid its fuels differently; the band is not reached"
    outside = [h for h in split if not _in_the_channel_band(h)]
    wrong_way = [(h, s) for h, ss in split.items() for s in ss
                 if s[1] != {"direct_debit"} or "direct_debit" in s[0]]
    assert outside == [] and wrong_way == [], (outside, wrong_way)


def test_a_household_moves_once_on_one_date(walked):
    """Defect: a dual household's legs moving out on different dates, or a supplied leg left
    behind at the old home after the household moved."""
    last = _last_supplied(walked)
    moves = collections.defaultdict(set)
    for m in walked["phase2b"]["home_move_outs"]:
        moves[m["household"]].add((m["customer_id"], m["move_date"]))
    dual = _dual_households(walked)
    bad = []
    for h, rows in moves.items():
        if h not in dual:
            continue
        dates = {d for _, d in rows}
        legs = {c for c, _ in rows}
        left_behind = [c for c in last if household_of(c) == h and c not in legs
                       and last[c] >= min(dates)]
        if len(dates) != 1 or (left_behind and not _followed(walked, h)):
            bad.append((h, rows, left_behind))
    assert bad == [], bad


def _followed(result, household) -> bool:
    return any(r["billing_account"] == household and r.get("supplied_at_new_home")
               for r in result["phase2b"].get("move_with_us_log", []))


def test_a_household_switches_away_once_and_takes_every_leg_it_holds(walked):
    """Defect: one leg leaving on a switch while the other stays supplied past it, or the two legs
    leaving on different dates."""
    last = _last_supplied(walked)
    departures = collections.defaultdict(dict)
    for d in walked["phase2b"]["leg_departures"]:
        departures[d["household"]][d["customer_id"]] = d["event_date"][:10]
    bad = []
    for h, legs in departures.items():
        on = set(legs.values())
        # `>=`: a leg whose supply ends ON the departure date and is missing from it is a leg the
        # switch never named (mutation-checked: `>` let a dropped gas row pass).
        stayed = [c for c in last if household_of(c) == h and c not in legs
                  and last[c] >= min(on)]
        if len(on) != 1 or stayed:
            bad.append((h, legs, stayed))
    assert departures and bad == [], bad


def test_a_mid_life_credit_comes_off_its_own_fuels_next_bill(walked):
    """Defect: a credit on one fuel taken off the other fuel's bill. SLC 27.16 defines a credit
    under one Domestic Supply Contract, and each fuel is its own contract."""
    bills = {(b["customer_id"], b["period_end"], b["commodity"]): b for b in walked["bills"]}
    dual = _dual_households(walked)
    taken = [(k, c) for k, v in walked["_credited"].items() if household_of(k[0]) in dual
             for c in v if c["kind"] == "credit"]
    foreign = [(k, c) for k, c in taken
               if (k[0], c["credit_period_end"], k[2]) not in bills
               or bills[(k[0], c["credit_period_end"], k[2])]["total_amount_gbp"] >= 0]
    assert taken and foreign == [], foreign


def test_the_accounts_closing_balance_is_the_sum_of_its_two_fuels(walked):
    """Defect: a closing credit on one fuel netted into the other fuel's balance, so the household is
    refunded the net and not the credit its own contract holds. Each leg closes on its own balance,
    a leg in credit is refunded exactly that credit, and the account owes the sum of the two."""
    dual = _dual_households(walked)
    closing = walked["closing_balances"]
    refunds = collections.defaultdict(float)
    for r in walked["credit_refund_log"]:
        refunds[r["customer_id"]] += r["credit_amount_gbp"]
    account = collections.defaultdict(dict)
    for leg, balance in closing.items():
        if household_of(leg) in dual:
            account[household_of(leg)][leg] = balance
    in_credit = [(leg, b) for legs in account.values() for leg, b in legs.items() if b < 0]
    assert in_credit, "no dual leg closed in credit; the per-fuel refund is not reached"
    assert all(round(refunds[leg], 2) == round(-b, 2) for leg, b in in_credit), in_credit
    for h, legs in account.items():
        balance = round(sum(legs.values()), 2)
        owed = round(sum(b for b in legs.values() if b > 0), 2)
        credit = round(sum(refunds[leg] for leg in legs), 2)
        assert balance == round(owed - credit, 2), (h, legs, credit)


def test_collections_runs_one_journey_per_household(walked):
    """Defect: two collections journeys for one household, one per fuel, open at once. The triad
    keys its ledger by billing account (`live_payment_triad.account_of`)."""
    dual = _dual_households(walked)
    ids = {j["account_id"].removeprefix("ACC-") for j in walked["phase2b"]["collections_journeys"]}
    assert [h for h in dual if h in ids and h + "g" in ids] == []


@pytest.mark.xfail(strict=False, reason=(
    "a gas leg ended at a move to a home with no gas is listed again in leg_departures when the "
    "household switches later: SEAT_FINDING_A_DUAL_FUEL_HOUSEHOLD_IS_TWO_ACCOUNTS_IN_COLLECTIONS_"
    "2026-10-25"))
def test_no_leg_switches_away_after_its_supply_ended(walked):
    """Defect, open: a switch counted on a leg the household stopped taking a year before."""
    last = _last_supplied(walked)
    late = [d for d in walked["phase2b"]["leg_departures"]
            if d["customer_id"] in last and last[d["customer_id"]] < d["event_date"][:10]]
    assert late == []
