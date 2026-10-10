"""Grade the world's >91-day arrears stock against Ofgem's published share, like for like.

REUSE: tools/grade_world_debt_against_ofgem.py
CLASS: CUSTOM
INDEX: searched "grade world debt against ofgem", "arrears like for like". Nothing tracked covers
       it. `company/billing/debt_objection.WorldDebtBook` applies the same outstanding rule at 28
       days for the objection, on the company side; this grades the WORLD's payment truth at 91
       days and must not live in `company/`. It is `/var/tmp/arrears_like_for_like.py` (capture)
       and `/var/tmp/arrears_slice.py` (grade), moved in unchanged in what they count; three
       verdicts on 2026-10-09 rested on those two untracked files.

WHAT IS COUNTED. A quarter end's numerator is the accounts holding a bill due at least 91 days
before it and still unpaid at it. A failed or disputed bill is unpaid until `settled_on` (never,
if None); a bill paid more than 91 days late is unpaid until due + days_late. A bill paid inside
91 days never counts. The denominator is every account billed in the quarter's last month,
prepayment included, as Ofgem's denominator is all domestic customers.

THE COMPARATOR is Ofgem's arrears PLUS debt, about 5.1% of electricity accounts at Q4 2019
(2.45% + 2.6%): the world has no repayment arrangements, so every world debtor sits in the
no-arrangement bucket, and the sum is the fair line (derivation:
docs/market_research/gb_domestic_bill_payment_failure_and_arrears_prevalence.md). The reading is
2019 electricity pooled over the four quarter ends. MET when 5.1% lies inside its Wilson 95%
interval. Fuel is split on the account id's `g` suffix, the run's own gas-account convention.

Usage:
  python3 -m tools.grade_world_debt_against_ofgem capture OUT.json [END]   # runs the world
  python3 -m tools.grade_world_debt_against_ofgem grade OUT.json [OUT2.json ...]  # pools seeds
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date, timedelta

# Ofgem arrears (2.45%) + debt (2.6%), electricity, Q4 2019. Source and derivation:
# docs/market_research/gb_domestic_bill_payment_failure_and_arrears_prevalence.md.
OFGEM_ARREARS_PLUS_DEBT_2019 = 0.051
BEHIND_DAYS = 91
GRADED_YEAR = 2019


def capture(out_path: str, end: str = "2019-12-31") -> dict:
    """Run the world to `end` and write each account's billed months, method and unpaid spells."""
    import time

    import background.live_payment_triad as lpt

    captured = []
    orig_init = lpt.LivePaymentTriad.__init__

    def _init(self, *a, **k):
        orig_init(self, *a, **k)
        captured.append(self)

    lpt.LivePaymentTriad.__init__ = _init
    try:
        from simulation.run_phase2b import main
        t0 = time.time()
        main(report_end=end)
        wall = time.time() - t0
    finally:
        lpt.LivePaymentTriad.__init__ = orig_init
    raw = spells_from_records(captured[-1].records)
    out = {"end": end, "wall_s": round(wall), "raw": raw}
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    return out


def _d(x):
    return x if isinstance(x, date) else date.fromisoformat(x)


def spells_from_records(records) -> dict:
    """account -> {months billed, payment method, [due, paid-or-None] spells that could age past 91 days}."""
    raw: dict = {}
    for r in records:
        due = _d(r.due_date)
        row = raw.setdefault(r.account_id, {"months": set(), "method": None, "spells": []})
        row["months"].add(due.isoformat()[:7])
        row["method"] = r.payment_method
        if r.result in ("failed", "dispute"):
            row["spells"].append([due.isoformat(), _d(r.settled_on).isoformat() if r.settled_on else None])
        elif r.result == "success" and (r.days_late or 0) > BEHIND_DAYS:
            row["spells"].append([due.isoformat(), (due + timedelta(days=r.days_late)).isoformat()])
    for row in raw.values():
        row["months"] = sorted(row["months"])
    return raw


def _is_gas(account_id: str) -> bool:
    return account_id.endswith("g")


def quarter_reading(raw: dict, quarter_end: date, fuel: str = "electricity"):
    """(accounts behind, accounts billed) at one quarter end; `behind` is a list of account ids."""
    cutoff = quarter_end - timedelta(days=BEHIND_DAYS)
    month = quarter_end.isoformat()[:7]
    active = [a for a, v in raw.items() if month in v["months"] and _is_gas(a) == (fuel == "gas")]
    behind = []
    for a in active:
        for due, paid in raw[a]["spells"]:
            if _d(due) <= cutoff and (paid is None or _d(paid) > quarter_end):
                behind.append(a)
                break
    return behind, active


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def grade(raws: list, fuel: str = "electricity", year: int = GRADED_YEAR) -> dict:
    """Pool the year's four quarter ends over one or more runs' captures, and grade against Ofgem."""
    k = n = prepay = 0
    for raw in raws:
        for m, dd in ((3, 31), (6, 30), (9, 30), (12, 31)):
            behind, active = quarter_reading(raw, date(year, m, dd), fuel)
            k += len(behind)
            n += len(active)
            prepay += sum(1 for a in behind if raw[a]["method"] == "prepayment")
    if n == 0:
        return {"behind": 0, "accounts": 0, "verdict": "CANNOT TELL -- no account billed in the graded year"}
    lo, hi = wilson(k, n)
    if lo <= OFGEM_ARREARS_PLUS_DEBT_2019 <= hi:
        verdict = "MET"
    elif lo > OFGEM_ARREARS_PLUS_DEBT_2019:
        verdict = "NOT MET, HIGH"
    else:
        verdict = "NOT MET, LOW"
    return {"behind": k, "accounts": n, "share": k / n, "wilson": (lo, hi),
            "ratio": (k / n) / OFGEM_ARREARS_PLUS_DEBT_2019, "verdict": verdict,
            "prepayment_behind": prepay, "prepayment_share_of_behind": prepay / k if k else None}


def main(argv: list) -> int:
    if len(argv) >= 2 and argv[0] == "capture":
        capture(argv[1], argv[2] if len(argv) > 2 else "2019-12-31")
        return 0
    if len(argv) >= 2 and argv[0] == "grade":
        raws = [json.load(open(p))["raw"] for p in argv[1:]]
        for fuel in ("electricity", "gas"):
            g = grade(raws, fuel)
            if not g["accounts"]:
                print(fuel, g["verdict"])
                continue
            lo, hi = g["wilson"]
            print(f"{fuel}: {g['behind']}/{g['accounts']} = {g['share']:.1%} ({lo:.1%}-{hi:.1%}), "
                  f"{g['ratio']:.2f}x Ofgem {OFGEM_ARREARS_PLUS_DEBT_2019:.1%}: {g['verdict']}; "
                  f"prepayment {g['prepayment_behind']} of {g['behind']} behind")
        return 0
    print(__doc__.split("Usage:")[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
