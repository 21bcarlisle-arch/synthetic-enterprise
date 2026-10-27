"""Tests for tools/generate_customer_reaction_chain.py --
CUSTOMER_360_REDESIGN.md v4 items 3 (events perturb the chain, real numeric
effects) and 4 (reaction closes the loop, reusing decision_event_ledger)."""
import json
from pathlib import Path as _P
import sys

sys.path.insert(0, str(_P(__file__).resolve().parents[2]))

from tools.generate_customer_reaction_chain import (
    _base_id, _usage_effect, _economic_effect, _renewal_effect, _add_effects,
    _move_out_events, _predecessor, _ev_effect,
)


def test_base_id_strips_gas_suffix():
    assert _base_id("C2g") == "C2"
    assert _base_id("C2") == "C2"
    assert _base_id("C_IC3g") == "C_IC3"


def test_usage_effect_computes_real_percent_change():
    monthly = [
        {"month": "2020-01", "kwh": 100}, {"month": "2020-02", "kwh": 100},
        {"month": "2020-03", "kwh": 100}, {"month": "2020-04", "kwh": 100},
        {"month": "2020-05", "kwh": 200}, {"month": "2020-06", "kwh": 200},
        {"month": "2020-07", "kwh": 200},
    ]
    effect = _usage_effect(monthly, "2020-05-15")
    assert effect is not None
    assert "+100%" in effect
    assert "100 kWh/mo" in effect
    assert "200 kWh/mo" in effect


def test_usage_effect_none_with_insufficient_data():
    monthly = [{"month": "2020-01", "kwh": 100}]
    assert _usage_effect(monthly, "2020-01-15") is None


def test_usage_effect_none_without_event_date():
    monthly = [{"month": "2020-01", "kwh": 100}]
    assert _usage_effect(monthly, None) is None


def test_economic_effect_reports_stress_step():
    stress = [{"year": 2017, "stress": "low"}, {"year": 2018, "stress": "high"}]
    miss = [
        {"year": 2017, "late": 0, "dd_failed": 0, "total": 12},
        {"year": 2018, "late": 3, "dd_failed": 0, "total": 12},
    ]
    effect = _economic_effect(stress, miss, "2018-06-28")
    assert effect is not None
    assert "low -> high" in effect
    assert "0% -> 25%" in effect


def test_economic_effect_none_when_nothing_changed():
    stress = [{"year": 2017, "stress": "low"}, {"year": 2018, "stress": "low"}]
    miss = [
        {"year": 2017, "late": 0, "dd_failed": 0, "total": 12},
        {"year": 2018, "late": 0, "dd_failed": 0, "total": 12},
    ]
    assert _economic_effect(stress, miss, "2018-06-28") is None


def test_renewal_effect_reports_real_rate_step():
    invoices = [
        {"date": "2019-12-31", "unit_rate_p_per_kwh": 14.0},
        {"date": "2020-01-31", "unit_rate_p_per_kwh": 16.5},
    ]
    effect = _renewal_effect(invoices, "2020-01-01", "electricity")
    assert effect == "Unit rate stepped 14.00p/kWh -> 16.50p/kWh"


def test_renewal_effect_none_when_rate_unchanged():
    invoices = [
        {"date": "2019-12-31", "unit_rate_p_per_kwh": 14.0},
        {"date": "2020-01-31", "unit_rate_p_per_kwh": 14.0},
    ]
    assert _renewal_effect(invoices, "2020-01-01", "electricity") is None


def test_add_effects_wires_renewal_and_life_event_effects():
    timeline = [
        {"date": "2020-01-01", "type": "renewed", "commodity": "electricity", "detail": "Tariff renewed"},
        {"date": "2018-06-28", "type": "life_event", "commodity": None, "detail": "Job loss"},
        {"date": "2022-01-01", "type": "churned", "commodity": "electricity", "detail": "Churned"},
    ]
    invoices = [
        {"date": "2019-12-31", "unit_rate_p_per_kwh": 14.0},
        {"date": "2020-01-31", "unit_rate_p_per_kwh": 16.5},
    ]
    pcb_entry = {
        "income_stress_trajectory": [{"year": 2017, "stress": "low"}, {"year": 2018, "stress": "high"}],
        "payment_miss_trajectory": [
            {"year": 2017, "late": 0, "dd_failed": 0, "total": 12},
            {"year": 2018, "late": 2, "dd_failed": 0, "total": 12},
        ],
    }
    out = _add_effects(timeline, invoices, [], pcb_entry)
    assert "effect" in out[0] and "14.00p/kWh" in out[0]["effect"]
    assert "effect" in out[1] and "low -> high" in out[1]["effect"]
    assert "effect" not in out[2]


def test_generate_end_to_end_patches_timeline_effect_and_reaction_chain(tmp_path, monkeypatch):
    import tools.generate_customer_reaction_chain as gcr

    cust_dir = tmp_path / "customers"
    cust_dir.mkdir()
    (cust_dir / "C1.json").write_text(json.dumps(dict(
        account_id="C1",
        timeline=[{"date": "2020-01-01", "type": "renewed", "commodity": "electricity", "detail": "Tariff renewed"}],
        invoices=[
            {"date": "2019-12-31", "unit_rate_p_per_kwh": 14.0},
            {"date": "2020-01-31", "unit_rate_p_per_kwh": 16.5},
        ],
        consumption={"monthly": []},
    )))

    ledger_path = tmp_path / "billing_ledger.json"
    ledger_path.write_text(json.dumps(dict(customers=dict(C1=dict(arrears_history=[])))))

    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps(dict(
        per_customer_behavioral=dict(C1=dict()),
        customer_events=[], retention_log=[], churn_journey_log=[],
        company_event_log=[], acquisition_funnel_log=[],
    )))

    monkeypatch.setattr(gcr, "CUSTOMERS_DIR", cust_dir)
    monkeypatch.setattr(gcr, "LEDGER_PATH", ledger_path)

    count = gcr.generate(str(run_json))
    assert count == 1
    updated = json.loads((cust_dir / "C1.json").read_text())
    assert updated["timeline"][0]["effect"] == "Unit rate stepped 14.00p/kWh -> 16.50p/kWh"
    assert updated["reaction_chain"] == []


def test_generate_returns_zero_when_ledger_missing(tmp_path, monkeypatch):
    import tools.generate_customer_reaction_chain as gcr

    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps(dict(per_customer_behavioral=dict())))
    monkeypatch.setattr(gcr, "LEDGER_PATH", tmp_path / "no_such_ledger.json")

    assert gcr.generate(str(run_json)) == 0


def test_a_mover_gets_a_move_out_event_and_its_final_bill():
    moves = [{"customer_id": "C1", "commodity": "electricity", "move_date": "2016-04-21"},
             {"customer_id": "C2", "commodity": "electricity", "move_date": "2017-01-01"}]
    finals = {"C1": [{"customer_id": "C1", "period_end": "2016-04-20", "final_bill": True,
                      "billing_basis": "estimated", "total_amount_gbp": 11.36}]}
    events = _move_out_events("C1", moves, finals)
    assert [e["type"] for e in events] == ["moved_out", "final_bill"]
    assert events[0]["date"] == "2016-04-21"
    assert events[1]["date"] == "2016-04-20"
    assert "estimated" in events[1]["effect"] and "11.36" in events[1]["effect"]
    assert _move_out_events("C3", moves, finals) == []


def test_an_occupier_names_its_predecessor_or_says_why_not():
    successions = [{"account_id": "OCC-abc", "predecessor_account_id": "C8"}]
    assert _predecessor("OCC-abc", successions) == ("C8", None)
    assert _predecessor("OCC-abc", None)[1] == "the run predates occupier_successions"
    assert _predecessor("OCC-zzz", successions)[0] is None
    assert _predecessor("C8", successions) == (None, None)


def _months(first, n, kwh):
    y, m = map(int, first.split("-"))
    out = []
    for k in range(n):
        yy, mm = y + (m - 1 + k) // 12, (m - 1 + k) % 12 + 1
        out.append({"month": "{}-{:02d}".format(yy, mm), "kwh": kwh(yy, mm)})
    return out


def test_an_ev_effect_is_read_on_electricity_over_a_year_either_side_and_graded_both_ways():
    """The defect: a gas leg's winter-into-summer fall was written as the car's -65%. Every
    partition is asserted reachable, so a reader that refuses everything cannot pass."""
    seasonal_gas = _months("2020-01", 48, lambda y, m: 1300.0 if m in (12, 1, 2, 3) else 400.0)
    assert "not observable by us" in _ev_effect("gas", False, seasonal_gas, "2022-04-16", []).lower()
    assert "electricity account" in _ev_effect("gas", True, seasonal_gas, "2022-04-16", [])
    car = _months("2019-01", 48, lambda y, m: 160.0 + (240.0 if (y, m) >= (2020, 5) else 0.0))
    within = _ev_effect("electricity", True, car, "2020-04-02", [])
    assert "within the 1,750-3,300" in within and "+2,880 kWh a year" in within
    flat = _months("2019-01", 48, lambda y, m: 160.0)
    assert "outside the 1,750-3,300" in _ev_effect("electricity", False, flat, "2020-04-02", [])
    assert "after we stopped" in _ev_effect("electricity", False, flat, "2023-06-01", [])
    assert "before we supplied" in _ev_effect("electricity", False, flat, "2018-06-01", [])
    assert "no full year" in _ev_effect("electricity", False, flat, "2022-06-01", [])
    solar = [{"type": "life_event", "date": "2020-09-01", "detail": "Solar install"}]
    assert "not separable" in _ev_effect("electricity", False, car, "2020-04-02", solar).lower()


def test_add_effects_routes_an_ev_by_the_accounts_fuel_and_clears_a_stale_effect():
    seasonal_gas = _months("2020-01", 48, lambda y, m: 1300.0 if m in (12, 1, 2, 3) else 400.0)
    timeline = [{"date": "2022-04-16", "type": "life_event", "detail": "Ev acquired",
                 "effect": "Usage moved -65% (avg 1353 kWh/mo -> 473 kWh/mo)"}]
    out = _add_effects(timeline, [], seasonal_gas, {}, commodity="gas", is_dual_fuel=False)
    assert "Usage moved" not in out[0]["effect"] and "not observable" in out[0]["effect"].lower()
