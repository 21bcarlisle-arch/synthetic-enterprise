"""Control: on the book the run builds, `own_forecast_plus_balance` TAKES both forecast legs.

The director's DD rule (2026-10-11) prices the days the account's current term still covers at the
known rate and the days beyond at the company's forward. Its own test proved the split reachable by
calling `reviewed_standing` directly; no caller supplied a term end or a forward, so on every book
the run built it equalled `consumption_at_rates_in_force`. This holds the wiring: the inputs the
production caller reads off the run (`forecast_inputs_from_run`) reach the review, a term ending
inside the forecast year splits it and moves the price, and a term running the whole year does not.

Defects it names: the book ignoring `term_records` (no review takes either leg); the production
inputs read from the wrong keys (same); the forward leg dropped (`forward_taken` 0, price unmoved);
the guard returning inputs for a term that outlives the forecast year (C2 takes a leg); the legs
tool pricing a different review from the book (`decompose` raises); the default rule reading the
terms (the inert leg moves).
"""
from __future__ import annotations

from datetime import date

from simulation.dd_balance_book import build_dd_balance_book, forecast_inputs_from_run
from tools.dd_book_legs import decompose

KWH = 300.0


def _bill(cid: str, y: int, m: int, unit: float) -> dict:
    start = date(y, m, 1)
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    days = (nxt - start).days
    return {"customer_id": cid, "segment": "resi", "commodity": "electricity",
            "period_start": start.isoformat(),
            "period_end": date.fromordinal(nxt.toordinal() - 1).isoformat(),
            "days_in_period": days, "total_consumption_kwh": KWH,
            "average_unit_rate_gbp_per_mwh": unit, "standing_charge_gbp_per_day": 0.20,
            "total_amount_gbp": (KWH / 1000.0 * unit + days * 0.20) * 1.05}


def _run() -> dict:
    bills = [_bill(c, y, m, 120.0) for c in ("C1", "C2") for y in (2017, 2018) for m in range(1, 13)]
    # C1 is on the default tariff, re-priced each quarter: at its review (2018-01-01) the term in
    # force began 2017-11-01 and ends 2018-02-01, inside the forecast year. C2 holds a fix to
    # 2019-03-01, past it.
    bounds = ["2017-01-01", "2017-05-01", "2017-08-01", "2017-11-01", "2018-02-01", "2018-05-01",
              "2018-08-01", "2018-11-01", "2019-02-01"]
    terms = [{"customer_id": "C1", "term_start": a, "term_end": b} for a, b in zip(bounds, bounds[1:])]
    terms.append({"customer_id": "C2", "term_start": "2017-03-01", "term_end": "2019-03-01"})
    # The company's own forward rose £10/MWh between the start of C1's term and its review.
    forwards = [{"customer_id": "X", "commodity": "electricity", "term_start": d,
                 "company_fwd_gbp_per_mwh": v, "sim_fwd_gbp_per_mwh": 999.0}
                for d, v in (("2017-03-01", 40.0), ("2017-10-01", 45.0), ("2017-12-15", 55.0))]
    return {"bills": bills, "opening_dd_by_customer": {"C1": 30.0, "C2": 30.0},
            "account_state_log": terms, "basis_risk_terms": forwards}


def _standing(book, cid: str, month: str) -> float:
    return next(p.collected_gbp for p in book.trajectories[cid] if p.month == month)


def test_both_forecast_legs_are_taken_on_the_book_the_run_builds():
    run = _run()
    inputs = forecast_inputs_from_run(run)
    rule = "own_forecast_plus_balance"
    wired = build_dd_balance_book(run["bills"], run["opening_dd_by_customer"], review_rule=rule, **inputs)
    bare = build_dd_balance_book(run["bills"], run["opening_dd_by_customer"], review_rule=rule)

    # The partition, whole: two reviews, one splits and prices a forward, one does neither.
    assert (wired.forecast_reviews, wired.forecast_term_end_taken, wired.forecast_forward_taken) == (2, 1, 1)
    assert (bare.forecast_reviews, bare.forecast_term_end_taken, bare.forecast_forward_taken) == (0, 0, 0)
    # The forward reached the price: +£10/MWh on the eleven months after 2018-02-01 raises C1's debit.
    assert _standing(wired, "C1", "2018-06") > _standing(bare, "C1", "2018-06")
    assert _standing(wired, "C2", "2018-06") == _standing(bare, "C2", "2018-06")

    # The legs tool prices the same reviews the book does (it raises if the two books disagree).
    legs = decompose(run["bills"], run["opening_dd_by_customer"], "2018-06", rule, **inputs)
    assert legs["forecast_legs"] == {"reviews": 2, "term_end_taken": 1, "forward_taken": 1}

    # Under the default rule the same inputs are inert.
    default = build_dd_balance_book(run["bills"], run["opening_dd_by_customer"], **inputs)
    plain = build_dd_balance_book(run["bills"], run["opening_dd_by_customer"])
    assert default.forecast_reviews == 0
    assert default.serialise() == plain.serialise()
