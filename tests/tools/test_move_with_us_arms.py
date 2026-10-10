"""The move-with-us arms comparison: what it counts as a stayer price move and a vulnerable shortfall."""
from __future__ import annotations

from tools.move_with_us_arms import compare


def _state(rate_c2=200.0):
    return [
        {"customer_id": "C1", "billing_account": "C1", "commodity": "electricity",
         "term_start": "2020-01-01", "unit_rate_gbp_per_mwh": 250.0},
        {"customer_id": "C2", "billing_account": "C2", "commodity": "electricity",
         "term_start": "2020-01-01", "unit_rate_gbp_per_mwh": rate_c2},
    ]


def _row(**kw):
    row = {"billing_account": "C1", "supply_point_id": "C1", "move_out_date": "2020-06-01",
           "notified_on": "2020-05-28", "tariff_type": "fixed", "unit_rate_gbp_per_mwh": 250.0,
           "cost_gbp_per_mwh": 200.0, "company_eac_kwh": 3000, "offered": True,
           "no_offer_reason": None, "known_vulnerable": False, "p_stay_at_carried": 0.8,
           "moves_with_us": True}
    row.update(kw)
    return row


def _arm(state, log, k=1.0, net=100.0):
    return {"take_up_scale": k, "account_state": state, "total_net": net, "home_move_outs": 1,
            "move_out_notices_filed": [{}], "move_with_us_log": log}


def test_a_stayers_raised_price_is_counted_and_a_retained_movers_own_price_is_not():
    """Defect: a stayer price move going uncounted (the director's condition unread), or the mover's
    own carried term counted as a stayer's. The counting branch is shown to fire first."""
    res = compare(_arm(_state(), []), _arm(_state(rate_c2=201.0), [_row()]))
    assert res["stayer_price_moves"] == 1 and res["stayer_prices_raised"] == 1
    assert not res["identical_account_terms"]
    res = compare(_arm(_state(), []), _arm(_state(), [_row()]))
    assert res["stayer_price_moves"] == 0 and res["identical_account_terms"]
    assert res["moves_with_us"] == 1 and res["offers_made"] == 1


def test_a_known_vulnerable_mover_left_unoffered_where_its_twin_is_offered_is_a_shortfall():
    """Defect: the twin check passing a vulnerable household the run refused while the same position
    is offered when not vulnerable."""
    log = [_row(known_vulnerable=True, offered=False, moves_with_us=False),
           _row(billing_account="C2", supply_point_id="C2")]
    res = compare(_arm(_state(), []), _arm(_state(), log))
    assert res["vulnerable_twin_shortfalls"] == 1
    assert res["known_vulnerable_movers_not_offered_while_others_are"] == 1
    clean = compare(_arm(_state(), []), _arm(_state(), [_row(known_vulnerable=True)]))
    assert clean["vulnerable_twin_shortfalls"] == 0
