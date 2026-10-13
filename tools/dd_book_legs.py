"""Split the level direct-debit book's portfolio balance at one month into named legs that sum to it.

WHY THIS EXISTS
---------------
On the single-levy run (7379375f6) the DD book is -£20.6k net debit at 2018-06 and holds only
£2-6k of credit across ~600 accounts. The levy fix removed £40-45k of steady debit but no summer
credit appeared, and the levy finding (`SEAT_FINDING_EVERY_SETTLED_BILL_CHARGED_THE_LEVIES_TWICE`)
could not say why. Five causes were candidates. A number that is the sum of five causes cannot
be argued down one cause at a time. It can be split, and each part checked against what was
predicted for it.

THE IDENTITY
------------
The book (`simulation/dd_balance_book.py`) gives each account a standing amount `S_w` per
12-month window `w` counted from its first bill: `S_0` is the opening amount and `S_w` is
`reviewed_monthly_amount(A_{w-1})`, last window's billed spend reset to a monthly figure. The
balance after a bill is `sum(S_w * n - bill)`. Write `T` for the supplier's own true charge
(`_true_charges`), `L_w = T_w / N_w` for the true average per collection over the WHOLE window
(as far as the run has it), and `<=` for the part of the window billed by the cutoff. Then
for each window, exactly:

    S_w*N<= - B<=  =  (S_w - L_w)*N<=   +   (L_w*N<= - T<=)   +   (T<= - B<=)
                      level mismatch        seasonal phase       estimate vs actual

and the level mismatch for `w >= 1` splits further, again exactly, because
`S_w = R(A_prev)`:

    S_w - L_w = (R(A_prev) - A_prev/12)  +  (A_prev - T_prev)/12  +  (T_prev/12 - L_w)
                 rounding                   estimate fed to review   review lag

Under the rule that prices last year's consumption at the rates in force
(`--rule consumption_at_rates_in_force`), the review feeds `X_prev`, the year re-priced, and not
`A_prev`. Rounding becomes `R(X_prev) - X_prev/12` and the review lag
`(T_prev + X_prev - A_prev)/12 - L_w`: last year's true charge, re-priced as the review re-priced
it, against this year's level. Under the spend rule `X_prev = A_prev`, so every leg is as before.

So the legs are: opening sizing (window 0's level mismatch), review lag, rounding, seasonal
phase, and estimate versus actual (both parts). Collection failure is not a leg: the book
collects `S_w` every month and never reads `dd_collection_book`. That is reported as a
structural zero rather than left out.

The tool rebuilds the book with the module's own `build_dd_balance_book` and refuses to print
legs that do not sum to the book's own balance for every account. Without that check the legs
could describe some other book.

THE EPISTEMIC WALL
------------------
This reads one finished run's issued bills and the opening amounts it published. It reaches no
ground truth, and `T` is the supplier's own figure, not the world's.

USAGE
    python3 -m tools.dd_book_legs /var/tmp/single_levy/run_output_abb925ec7.json --month 2018-06
    python3 -m tools.dd_book_legs RUN --month 2018-06 --rule consumption_at_rates_in_force
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Mapping

from company.billing.dd_review import bill_days as _bill_days
from company.compliance.domain_invariants import vat_rate_for_segment
from simulation.arrears_engine import payment_method
from simulation.dd_balance_book import (
    DEFAULT_REVIEW_RULE,
    REVIEW_RULES,
    _months_between,
    _true_charges,
    build_dd_balance_book,
    reviewed_standing,
    simple_balance_after_window,
)

LEGS = ("opening_sizing", "review_lag", "rounding", "seasonal_phase",
        "estimate_vs_actual", "collection_failure", "balance_recovery")

#: Months whose window opening counts as a winter start: an account that opened its current year
#: in one of them has consumed a whole winter on level instalments by the summer.
WINTER_MONTHS = frozenset({10, 11, 12, 1, 2, 3})


def _priced_annual(rule: str, completed: list[Mapping], first_of_new: Mapping | None) -> float:
    """`X`, the annual figure the review priced before rounding: last year's spend, or its
    consumption at the rates on the new window's first bill. Mirrors `reviewed_standing`,
    including its fallback; a mismatch would move money between rounding and lag, never the sum.
    """
    spend = sum(float(b["total_amount_gbp"]) for b in completed)
    if rule == "last_year_spend" or first_of_new is None:
        return spend
    unit = first_of_new.get("average_unit_rate_gbp_per_mwh")
    sc = first_of_new.get("standing_charge_gbp_per_day")
    if not unit or sc is None or any(b.get("total_consumption_kwh") is None for b in completed):
        return spend
    kwh = sum(float(b["total_consumption_kwh"]) for b in completed)
    days = sum(_bill_days(b) for b in completed)
    adj = sum(float(b.get("catchup_adjustment_gbp") or 0.0) for b in completed if b.get("catchup_applied"))
    return (kwh / 1000.0 * float(unit) + days * float(sc)) * (1.0 + vat_rate_for_segment("resi")) + adj


def _dd_supplies(bills: list[dict]) -> dict[str, list[tuple[date, date, float, float, dict]]]:
    """`customer_id -> [(end, start, billed, true, bill)]` for direct-debit bills, by end date.

    The same population gate and the same true charges the book itself uses.
    """
    true_of = _true_charges(bills)
    out: dict[str, list] = {}
    for b in bills:
        if payment_method(b.get("segment", "resi"), float(b["total_amount_gbp"]),
                          b["customer_id"], b.get("commodity", "electricity")) != "direct_debit":
            continue
        end = date.fromisoformat(b["period_end"][:10])
        start = (date.fromisoformat(b["period_start"][:10]) if b.get("period_start")
                 else end.replace(day=1))
        out.setdefault(b["customer_id"], []).append(
            (end, start, float(b["total_amount_gbp"]), true_of[id(b)], b))
    for seq in out.values():
        seq.sort(key=lambda t: t[0])
    return out


def account_legs(seq: list[tuple], opening: float, month: str,
                 rule: str = DEFAULT_REVIEW_RULE) -> dict | None:
    """One account's balance at `month` and its legs, or None if the book does not count it then.

    Counted means what the book's portfolio sum means: first bill on or before `month` and last
    bill on or after it. The balance is the one after the last bill on or before `month`.
    Each row is `(end, start, billed, true)`, with the bill dict as a fifth element where the rule
    needs the rates it carries.
    """
    def ym(d: date) -> str:
        return f"{d.year:04d}-{d.month:02d}"

    if not seq or ym(seq[0][0]) > month or ym(seq[-1][0]) < month:
        return None
    anchor = seq[0][0]
    rows = []
    prev = None
    for row in seq:
        end, billed, true = row[0], row[2], row[3]
        n = 1 if prev is None else max(1, _months_between(prev, end))
        rows.append((_months_between(anchor, end) // 12, n, billed, true, ym(end),
                     row[4] if len(row) > 4 else {"total_amount_gbp": billed}))
        prev = end
    windows = sorted({r[0] for r in rows})
    tot = {w: [0, 0.0, 0.0] for w in windows}          # N, billed, true over the whole window
    for w, n, billed, true, _, _ in rows:
        tot[w][0] += n
        tot[w][1] += billed
        tot[w][2] += true
    bills_in = {w: [r[5] for r in rows if r[0] == w] for w in windows}
    standing = {windows[0]: float(opening)}
    # `own_forecast_plus_balance` adds the balance carried into the window to the standing amount, as
    # `build_dd_balance_book` does (same running balance, same sign: the review recovers
    # `-balance_entering`). The addition is its own leg, `balance_recovery`, so `rounding` keeps
    # measuring only the forecast's own rounding and the other legs match the rates-in-force rule.
    recovery = {windows[0]: 0.0}
    balance_entering = {windows[0]: 0.0}
    priced = {}
    for prev_w, w in zip(windows, windows[1:]):
        balance_entering[w] = simple_balance_after_window(
            balance_entering[prev_w], standing[prev_w], bills_in[prev_w])
        without = reviewed_standing(rule, bills_in[prev_w], bills_in[w][0])
        if rule == "own_forecast_plus_balance":
            standing[w] = reviewed_standing(rule, bills_in[prev_w], bills_in[w][0],
                                            balance_to_clear_gbp=-balance_entering[w])
        else:
            standing[w] = without
        recovery[w] = standing[w] - without
        priced[w] = _priced_annual(rule, bills_in[prev_w], bills_in[w][0])

    legs = dict.fromkeys(LEGS, 0.0)
    balance = 0.0
    current_window = windows[0]
    for i, w in enumerate(windows):
        upto = [r for r in rows if r[0] == w and r[4] <= month]
        if not upto:
            continue
        current_window = w
        n_le = sum(r[1] for r in upto)
        b_le = sum(r[2] for r in upto)
        t_le = sum(r[3] for r in upto)
        level = tot[w][2] / tot[w][0]
        balance += standing[w] * n_le - b_le
        legs["seasonal_phase"] += level * n_le - t_le
        legs["estimate_vs_actual"] += t_le - b_le
        if i == 0:
            legs["opening_sizing"] += (standing[w] - level) * n_le
        else:
            _, a_prev, t_prev = tot[windows[i - 1]]
            x_prev = priced[w]
            legs["rounding"] += (standing[w] - recovery[w] - x_prev / 12.0) * n_le
            legs["balance_recovery"] += recovery[w] * n_le
            legs["estimate_vs_actual"] += (a_prev - t_prev) / 12.0 * n_le
            legs["review_lag"] += ((t_prev + x_prev - a_prev) / 12.0 - level) * n_le
    window_start_month = (anchor.month - 1 + 12 * current_window) % 12 + 1
    return {"balance_gbp": balance, "legs": legs, "window": current_window,
            "window_start_month": window_start_month,
            "winter_start": window_start_month in WINTER_MONTHS}


def decompose(bills: list[dict], opening_dd: Mapping[str, float], month: str,
              rule: str = DEFAULT_REVIEW_RULE) -> dict:
    """The portfolio's balance at `month`, its legs, and the same split by fuel, window and start.

    Raises if any account's legs do not sum to the balance the book itself carries for it.
    """
    book = build_dd_balance_book(bills, opening_dd, review_rule=rule)
    supplies = _dd_supplies(bills)
    per = {}
    for cid, seq in supplies.items():
        opening = opening_dd.get(cid)
        if opening is None or opening <= 0.0:
            continue
        got = account_legs(seq, opening, month, rule)
        if got is None:
            continue
        pts = [p for p in book.trajectories[cid] if p.month <= month]
        book_balance = pts[-1].balance_gbp
        if abs(got["balance_gbp"] - book_balance) > 0.01 or \
                abs(sum(got["legs"].values()) - got["balance_gbp"]) > 1e-6:
            raise ValueError(
                f"{cid}: legs {sum(got['legs'].values()):.2f} / rebuilt {got['balance_gbp']:.2f}"
                f" / book {book_balance:.2f} disagree at {month}; the legs describe another book")
        per[cid] = got

    def total(ids) -> dict:
        ids = list(ids)
        out = {leg: round(sum(per[c]["legs"][leg] for c in ids), 2) for leg in LEGS}
        out["balance_gbp"] = round(sum(per[c]["balance_gbp"] for c in ids), 2)
        out["held_credit_gbp"] = round(sum(max(0.0, per[c]["balance_gbp"]) for c in ids), 2)
        out["n_accounts"] = len(ids)
        return out

    groups = {
        "all": per,
        "electricity": [c for c in per if not c.endswith("g")],
        "gas": [c for c in per if c.endswith("g")],
        "window_0": [c for c in per if per[c]["window"] == 0],
        "window_1_plus": [c for c in per if per[c]["window"] >= 1],
        "current_window_opened_oct_mar": [c for c in per if per[c]["winter_start"]],
        "current_window_opened_apr_sep": [c for c in per if not per[c]["winter_start"]],
    }
    series = {m["month"]: m["portfolio_balance_gbp"] for m in book.serialise()["monthly_held_credit_series"]}
    return {"month": month, "review_rule": rule, "book_portfolio_balance_gbp": round(series.get(month, 0.0), 2),
            "collection_failure_note": "structural zero: the book collects the standing amount "
                                       "every month and never reads dd_collection_book",
            "groups": {k: total(v) for k, v in groups.items()}}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_output", type=Path)
    ap.add_argument("--month", default="2018-06")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--rule", choices=REVIEW_RULES, default=DEFAULT_REVIEW_RULE)
    args = ap.parse_args(argv)
    run = json.loads(args.run_output.read_text())
    out = decompose(run["bills"], run["opening_dd_by_customer"], args.month, args.rule)
    published = {m["month"]: m["portfolio_balance_gbp"]
                 for m in run["dd_balance_book"]["monthly_held_credit_series"]}
    out["published_portfolio_balance_gbp"] = published.get(args.month)
    out["producing_commit"] = run.get("producing_commit", {}).get("commit")
    text = json.dumps(out, indent=2)
    if args.json:
        args.json.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
