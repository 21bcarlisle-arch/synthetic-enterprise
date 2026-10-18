"""C35: how many advice cases a retention rise rescues on a probed book, priced by the company's own code.

A reading aid, not a door. It feeds every renewal row of a `tools/decision_probe.py` output through
`company.crm.next_best_action.price_retention_rise`, using only fields the company holds: its own
flat offer and cost floor, the account's annual volume, the published default
(`company.crm.save_offer.published_default_rate_ex_vat`), and B11's per-account departure p. The p
is read at the two ends slice 13 brackets: the full fit window, and the cut-year window. The cut is
the year before the renewal, floored at the book's first year. The probe's world-truth fields
(`true_p_retain`, the grid's `p` and `paid`) are never read. The three advice effects are the
page's (`docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md` §4).

    python3 -m tools.retention_rise_count <probe.json> [docs/reports/run_output_latest.json] [--per-household]

`--per-household` decides the legs of one billing account renewing on one date once
(`DecisionPolicy.next_best_action_decides_per_household`); without it every renewal row is a decision.
"""
from __future__ import annotations

import dataclasses
import json
import statistics
import sys
from collections import Counter

from company.analytics.forward_clv import (
    _month_index,
    book_from_run_output,
    move_outs_from_run_output,
    run_backtest,
)
from company.crm.next_best_action import (
    AccountState,
    Action,
    ActionEstimate,
    RenewalTerms,
    price_retention_rise,
    states_for_decision,
    value_change,
)
from company.crm.save_offer import published_default_rate_ex_vat
from company.policy.decision_policy import CURRENT_POLICY

HORIZON_MONTHS = 48
EFFECTS = ((2.0, 0.001), (2.0, 0.003), (3.0, 0.003))  # (GBP/month given up, hazard cut), §4
HAZARD_ENDS = ("full_window", "cut_year")


def monthly_hazards(run_output: dict, cuts) -> dict:
    """{(cut, end): {account: constant monthly hazard}} from B11's per-customer departure p."""
    book, last = book_from_run_output(run_output)
    moves = move_outs_from_run_output(run_output)
    out = {}
    for cut in cuts:
        for end in HAZARD_ENDS:
            bt = run_backtest(book, last, cut, None, None, moves,
                              cut if end == "cut_year" else None)
            months = _month_index(bt.held_back_months[1]) - _month_index(bt.held_back_months[0]) + 1
            out[(cut, end)] = {f.account_id: 1.0 - (1.0 - f.per_customer_departure_p) ** (1.0 / months)
                               for f in bt.forecasts}
    return out


def count(rows, hazards, first_year: int, end: str, policy=None) -> dict:
    """Rescues per decision. Under `policy.next_best_action_decides_per_household` the legs of one
    billing account renewing on one date are one decision (`states_for_decision`); off, every row is."""
    rescued, refused, rises, kept, no_forecast = Counter(), Counter(), {}, [], 0
    together: dict = {}
    for r in rows:
        cut = max(first_year, int(r["term_start"][:4]) - 1)
        h = hazards[(cut, end)].get(r["billing_account"])
        if h is None:
            no_forecast += 1
            continue
        vol, flat = r["annual_mwh"], r["offer_gbp_per_mwh"]["flat"]
        terms = RenewalTerms(flat, published_default_rate_ex_vat(r["commodity"], r["term_start"]), vol)
        together.setdefault((r["billing_account"], r["term_start"]), []).append(
            AccountState(r["billing_account"], (flat - r["base_gbp_per_mwh"]) * vol / 12.0, h, 0, (),
                         renewal=terms))
    decisions = 0
    for legs in together.values():
        for state in states_for_decision(legs, policy):
            decisions += 1
            h, terms = state.monthly_departure_hazard, state.renewal
            for g, c in EFFECTS:
                # The cut is clamped at the account's own hazard, so the hazard with advice stays >= 0.
                est = ActionEstimate(Action.TARIFF_ADVICE, g * 12.0, -g, -min(c, h))
                if value_change(state, est, HORIZON_MONTHS) >= 0.0:
                    refused["needs no rise"] += 1
                    continue
                rise, why = price_retention_rise(state, est, terms, HORIZON_MONTHS)
                if rise is None:
                    refused[why.split(" (")[0].split(",")[0]] += 1
                    continue
                rescued[(g, c)] += 1
                rises.setdefault((g, c), []).append(rise.rise_gbp_per_month)
                kept.append(rise.customer_benefit_kept_gbp / (g * HORIZON_MONTHS))
    return {"rescued": rescued, "refused": refused, "rises": rises, "kept": kept,
            "no_forecast": no_forecast, "decisions": decisions}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    per_household = "--per-household" in argv
    argv = [a for a in argv if a != "--per-household"]
    policy = dataclasses.replace(CURRENT_POLICY, next_best_action_decides_per_household=per_household)
    rows = json.load(open(argv[0]))["rows"]
    run_output = json.load(open(argv[1] if len(argv) > 1 else "docs/reports/run_output_latest.json"))
    first_year = min(int(r["term_start"][:4]) for r in rows)
    hazards = monthly_hazards(run_output, sorted({max(first_year, int(r["term_start"][:4]) - 1)
                                                   for r in rows}))
    for end in HAZARD_ENDS:
        res = count(rows, hazards, first_year, end, policy)
        print(f"hazard end {end}: {len(rows)} renewals, {res['no_forecast']} without a forecast")
        # Per household the denominator is decisions, not rows: two legs renewing together are one.
        n = res["decisions"] + res["no_forecast"] if per_household else len(rows)
        if per_household:
            print(f"  decided per household: {res['decisions']} decisions")
        for g, c in EFFECTS:
            need = res["rises"].get((g, c), [])
            print(f"  gives up {g:.0f} GBP/mo, cuts {c * 100:.1f} pt: rescued {res['rescued'][(g, c)]}/{n}"
                  f"  median rise {statistics.median(need) if need else None}")
        print(f"  all: {sum(res['rescued'].values())}/{3 * n}; household keeps median "
              f"{statistics.median(res['kept']) if res['kept'] else None} of its gross benefit")
        print(f"  refused: {dict(res['refused'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
