"""Grade the ending-term renewal belief on one published book, as pre-registered.

The pre-registration is `docs/staging/records/SEAT_PREREG_THE_ENDING_TERM_BELIEF_ON_THE_COMING_BOOK_2026-11-22.md`.
This file was committed with it, before any book carrying `desk_belief_log` existed, so the analysis
is fixed along with the predictions.

A standing book runs with `renewal_belief_by_ending_term` off, so it shows what the live belief did,
never what the switch would have done to a departure. What it can grade is the ranking: the
switch's belief, recomputed for each renewal year from that same book's earlier desk rows by the
company's own `CompetitivePressureLedger.ending_term_multiplier` and `condition_on_ending_term`,
paired against the live belief on the same states.

Refuses, with the reason, on a book that cannot carry the grade: no `desk_belief_log`, rows without
`ending_term_type`, or too few states or leavers (the floors are the record's §2).

    python3 -m tools.grade_ending_term_belief_on_a_book docs/reports/run_output_<head>_<ts>.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from datetime import date, timedelta

from company.crm.churn_desk import condition_on_ending_term
from company.crm.competitive_pressure import CompetitivePressureLedger
from simulation.household import household_of

GRADE_FROM = date(2019, 1, 1)
#: The last state whose 365-day outcome window closes inside a 2016-2025 book.
GRADE_TO = date(2024, 12, 31)
OUTCOME_DAYS = 365
#: The record's §2 floors: below either, the grade is void, not refuted.
MIN_STATES, MIN_LEAVERS = 100, 15
BOOTSTRAP_DRAWS, BOOTSTRAP_SEED = 1000, 7


def auc(scores: list[float], labels: list[bool]) -> float | None:
    """Mann-Whitney AUC with half credit for ties; None without both classes."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def _ledger(rows: list[dict]) -> CompetitivePressureLedger:
    """The ledger the switch reads, fed this book's typed desk rows: belief booked, loss at the roll."""
    ledger = CompetitivePressureLedger()
    ledger.loss_reporting_armed = True
    for r in rows:
        key = (r["ending_term_type"], int(r["term_start"][:4]))
        sums = ledger.ending_term_sums.setdefault(key, {"n": 0, "sp": 0.0, "losses": 0})
        sums["n"] += 1
        sums["sp"] += float(r["desk_churn_belief"])
        sums["losses"] += int(bool(r["left"]))
    return ledger


def online_conditioned_beliefs(rows: list[dict], ledger: CompetitivePressureLedger) -> list[float]:
    """Each row's belief as the switch would have held it: its type's multiplier from EARLIER years
    only (`ending_term_multiplier` reads `year < renewal_year`), so no row reads its own outcome."""
    return [condition_on_ending_term(
        float(r["desk_churn_belief"]),
        ledger.ending_term_multiplier(r["ending_term_type"], int(r["term_start"][:4]))[0])
        for r in rows]


def _states(rows: list[dict], conditioned: list[float], book: dict) -> list[dict]:
    """The graded states: 2019-2024 desk rows, each with its household's 365-day outcome."""
    left_on: dict[str, list[date]] = defaultdict(list)
    for e in book.get("customer_events") or []:
        if e.get("event_type") == "churned":
            left_on[household_of(e["customer_id"])].append(date.fromisoformat(e["event_date"][:10]))
    states = []
    for r, c in zip(rows, conditioned):
        start = date.fromisoformat(r["term_start"][:10])
        if not GRADE_FROM <= start <= GRADE_TO:
            continue
        end = start + timedelta(days=OUTCOME_DAYS)
        left = any(start <= d < end for d in left_on.get(r["account_id"], ()))
        states.append({"account": r["account_id"], "year": start.year, "type": r["ending_term_type"],
                       "live": float(r["desk_churn_belief"]), "cond": c, "left": left,
                       "left_at_roll": bool(r["left"])})
    return states


def _point(sub: list[dict], label: str = "left") -> tuple:
    """(live AUC, conditioned AUC, conditioned minus live) on these states."""
    lab = [s[label] for s in sub]
    a_live, a_cond = auc([s["live"] for s in sub], lab), auc([s["cond"] for s in sub], lab)
    return a_live, a_cond, (None if a_live is None or a_cond is None else a_cond - a_live)


def _clustered_bounds(states: list[dict]) -> tuple[list[list[float]], int]:
    """95% bounds on each of `_point`'s three figures, resampling whole accounts."""
    by_account: dict[str, list[dict]] = defaultdict(list)
    for s in states:
        by_account[s["account"]].append(s)
    accounts = sorted(by_account)
    rng = random.Random(BOOTSTRAP_SEED)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        p = _point([s for a in rng.choices(accounts, k=len(accounts)) for s in by_account[a]])
        if None not in p:
            draws.append(p)
    bounds = []
    for i in range(3):
        xs = sorted(d[i] for d in draws)
        bounds.append([round(xs[int(0.025 * len(xs))], 3), round(xs[int(0.975 * len(xs)) - 1], 3)])
    return bounds, len(draws)


def grade(book: dict) -> dict:
    log = book.get("desk_belief_log")
    if not log:
        return {"refused": "the book carries no desk_belief_log"}
    rows = [r for r in log if r.get("desk_asked") and r.get("desk_churn_belief") is not None]
    if any("ending_term_type" not in r for r in rows):
        return {"refused": "desk_belief_log rows carry no ending_term_type (book predates the field)"}
    rows = [r for r in rows if r["ending_term_type"] is not None]
    ledger = _ledger(rows)
    states = _states(rows, online_conditioned_beliefs(rows, ledger), book)
    leavers = sum(s["left"] for s in states)
    result: dict = {"states": len(states), "leavers": leavers,
                    "accounts": len({s["account"] for s in states}),
                    "producing_commit": (book.get("producing_commit") or {}).get("commit")}
    if len(states) < MIN_STATES or leavers < MIN_LEAVERS:
        result["refused"] = (f"{len(states)} states and {leavers} leavers, under the floors "
                             f"{MIN_STATES} and {MIN_LEAVERS}: the grade is void, not refuted")
        return result
    (b_live, b_cond, b_diff), used = _clustered_bounds(states)
    a_live, a_cond, diff = _point(states)
    by_type: dict[str, dict] = defaultdict(lambda: {"states": 0, "leavers": 0})
    for s in states:
        by_type[s["type"]]["states"] += 1
        by_type[s["type"]]["leavers"] += int(s["left"])
    y2019 = [s for s in states if s["year"] == 2019]
    result.update({
        "auc_live": round(a_live, 3), "auc_live_95": b_live,
        "auc_conditioned": round(a_cond, 3), "auc_conditioned_95": b_cond,
        "paired_conditioned_minus_live": round(diff, 3), "paired_95": b_diff,
        "bootstrap_draws_used": used,
        "leavers_at_fix_end_share": round(by_type.get("fixed", {}).get("leavers", 0) / leavers, 3),
        "by_type": dict(by_type),
        "multiplier_for_2019": {t: ledger.ending_term_multiplier(t, 2019)[0]
                                for t in ("fixed", "default", "default_after_declined_fix")},
        "secondary_2019_only": dict(zip(("auc_live", "auc_conditioned", "paired"),
                                        _point(y2019))) if y2019 else None,
        "secondary_left_at_roll": dict(zip(("auc_live", "auc_conditioned"),
                                           _point(states, "left_at_roll")[:2])),
    })
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("book")
    args = ap.parse_args(argv)
    with open(args.book) as fh:
        out = grade(json.load(fh))
    print(json.dumps(out, indent=2, default=str))
    return 1 if "refused" in out else 0


if __name__ == "__main__":
    sys.exit(main())
