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
2019 electricity pooled over the four quarter ends. MET when 5.1% lies inside its account-clustered
95% interval. Fuel is split on the account id's `g` suffix, the run's own gas-account convention.

THE INTERVAL IS CLUSTERED ON THE ACCOUNT, not Wilson on account-quarters. An account that is behind
stays behind: on the 2026-10-10 captures the 50/99/62 account-quarters are 22/35/29 accounts, about
2.3 quarters each, so Wilson is too narrow and graded the three-seed pool NOT MET, HIGH on a bound
the sample had not earned. The bootstrap resamples account ids and carries each one's quarters
from EVERY pooled capture together, because dice seeds share one cast: the same household in three
captures is one draw from the population, not three. Wilson is still printed beside it.

A DICE SEED re-draws each bill's payment outcome and nothing else. Every payment draw in
`simulation.payment_behaviour_source` (the outcome, its reason, a DD re-presentation, a later
settlement) comes through `_period_substream`. The household's payment method uses `_substream`
directly, and stress is drawn elsewhere. So salting only `_period_substream` keeps the cast, the
weather, the prices and every household's method, and varies the dice. A book seed would change
the cast. That is EP17 and the director's (`tools/book_seed_authorisation.py`), and it is not
reachable from here.

THE AGE READING (W2_38, 2026-10-21) asks how old the >91-day stock is: of the bills unpaid at a
quarter end and due at least 91 days before it, the share due at least 365 days before it. The
comparator is Energy UK's aged (>12-month) arrears, 52% of the stock in 2023 and 65% in 2025
(docs/market_research/debt_and_collections.md §2.5). Its definition is not disclosed, so the bill
share is the primary reading (bills are of similar size, so it stands in for the pound share), and
the account share (accounts whose oldest such bill is a year old) is printed beside it. A capture
that carries the per-bill `bills` side table also gets the pound share. Only Q4 2023 is graded; a
capture ending 2024-12-31 has no 2025 quarter end, so Q4 2024 is printed beside 65%, not graded.

Usage:
  python3 -m tools.grade_world_debt_against_ofgem capture OUT.json [END] [DICE_SEED]  # runs the world
  python3 -m tools.grade_world_debt_against_ofgem grade OUT.json [OUT2.json ...]  # pools seeds
  python3 -m tools.grade_world_debt_against_ofgem age OUT.json [OUT2.json ...]  # the stock's age
"""
from __future__ import annotations

import json
import math
import random
import sys
from datetime import date, timedelta

# Ofgem arrears (2.45%) + debt (2.6%), electricity, Q4 2019. Source and derivation:
# docs/market_research/gb_domestic_bill_payment_failure_and_arrears_prevalence.md.
OFGEM_ARREARS_PLUS_DEBT_2019 = 0.051
BEHIND_DAYS = 91
# Energy UK, aged (>12-month) arrears as a share of arrears: 52% (2023), 65% (2025). Source:
# docs/market_research/debt_and_collections.md §2.5. Definition (count or pounds) undisclosed.
AGED_DAYS = 365
ENERGY_UK_AGED_SHARE = {2023: 0.52, 2025: 0.65}
GRADED_YEAR = 2019
# Resamples for the clustered interval, and a fixed RNG seed so a capture always grades the same.
BOOTSTRAP_DRAWS = 4000
BOOTSTRAP_SEED = 20191231


class dice_seeded:
    """Salt every per-period payment draw with `seed`; restore on exit. `calls` counts the draws
    the salt reached, so a rebind that reaches nothing can be refused, not published as a spread."""

    def __init__(self, seed: int):
        self.seed = seed
        self.calls = 0

    def __enter__(self):
        import simulation.payment_behaviour_source as pbs
        self._pbs, self._orig = pbs, pbs._period_substream

        def salted(base_seed, base_name, period_index):
            self.calls += 1
            return self._orig(base_seed, f"{base_name}::dice{self.seed}", period_index)

        pbs._period_substream = salted
        return self

    def __exit__(self, *exc):
        self._pbs._period_substream = self._orig
        return False


def capture(out_path: str, end: str = "2019-12-31", dice_seed: int | None = None) -> dict:
    """Run the world to `end` and write each account's billed months, method and unpaid spells."""
    import contextlib
    import time

    import background.live_payment_triad as lpt

    captured = []
    orig_init = lpt.LivePaymentTriad.__init__

    def _init(self, *a, **k):
        orig_init(self, *a, **k)
        captured.append(self)

    lpt.LivePaymentTriad.__init__ = _init
    dice = dice_seeded(dice_seed) if dice_seed is not None else contextlib.nullcontext()
    try:
        with dice:
            from simulation.run_phase2b import main
            t0 = time.time()
            main(report_end=end)
            wall = time.time() - t0
    finally:
        lpt.LivePaymentTriad.__init__ = orig_init
    if dice_seed is not None and dice.calls == 0:
        raise AssertionError(f"dice seed {dice_seed} reached no payment draw; the run is the default "
                             "world, and grading it as a second seed would report a spread of zero.")
    raw = spells_from_records(captured[-1].records)
    out = {"end": end, "dice_seed": dice_seed, "dice_draws": getattr(dice, "calls", None),
           "wall_s": round(wall), "raw": raw}
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


def account_clustered(per_account: dict, draws: int = BOOTSTRAP_DRAWS, seed: int = BOOTSTRAP_SEED):
    """95% percentile interval on sum(behind)/sum(billed) when whole accounts are resampled.

    `per_account` maps an account id to its (account-quarters behind, account-quarters billed),
    summed over every pooled capture, so one draw of an id carries all of its captures with it."""
    rows = list(per_account.values())
    if not rows:
        return (None, None)
    rng = random.Random(seed)
    shares = []
    for _ in range(draws):
        k = n = 0
        for kb, nb in rng.choices(rows, k=len(rows)):
            k += kb
            n += nb
        shares.append(k / n)
    shares.sort()
    return (shares[int(0.025 * draws)], shares[int(0.975 * draws) - 1])


def _verdict(interval) -> str:
    lo, hi = interval
    if lo <= OFGEM_ARREARS_PLUS_DEBT_2019 <= hi:
        return "MET"
    return "NOT MET, HIGH" if lo > OFGEM_ARREARS_PLUS_DEBT_2019 else "NOT MET, LOW"


def grade(raws: list, fuel: str = "electricity", year: int = GRADED_YEAR) -> dict:
    """Pool the year's four quarter ends over one or more runs' captures, and grade against Ofgem."""
    k = n = prepay = 0
    per_account: dict = {}
    for raw in raws:
        for m, dd in ((3, 31), (6, 30), (9, 30), (12, 31)):
            behind, active = quarter_reading(raw, date(year, m, dd), fuel)
            k += len(behind)
            n += len(active)
            prepay += sum(1 for a in behind if raw[a]["method"] == "prepayment")
            behind_set = set(behind)
            for a in active:
                kb, nb = per_account.get(a, (0, 0))
                per_account[a] = (kb + (a in behind_set), nb + 1)
    if n == 0:
        return {"behind": 0, "accounts": 0, "verdict": "CANNOT TELL -- no account billed in the graded year"}
    wil = wilson(k, n)
    clustered = account_clustered(per_account)
    return {"behind": k, "accounts": n, "share": k / n, "wilson": wil, "clustered": clustered,
            "distinct_accounts": len(per_account),
            "distinct_behind": sum(1 for kb, _ in per_account.values() if kb),
            "ratio": (k / n) / OFGEM_ARREARS_PLUS_DEBT_2019, "verdict": _verdict(clustered),
            "wilson_verdict": _verdict(wil),
            "prepayment_behind": prepay, "prepayment_share_of_behind": prepay / k if k else None}


def age_reading(raw: dict, quarter_end: date, fuel: str = "electricity", amounts: dict | None = None):
    """The >91-day stock at one quarter end, split by age. Returns per-account rows
    {account: (bills aged, bills behind, pounds aged, pounds behind)} over accounts holding at least
    one bill behind; `amounts` maps (account, due iso) to pounds, and pounds are None without it."""
    cutoff = quarter_end - timedelta(days=BEHIND_DAYS)
    aged_line = quarter_end - timedelta(days=AGED_DAYS)
    rows = {}
    for a, v in raw.items():
        if _is_gas(a) != (fuel == "gas"):
            continue
        ka = kb = 0
        pa = pb = 0.0
        for due, paid in v["spells"]:
            d = _d(due)
            if d <= cutoff and (paid is None or _d(paid) > quarter_end):
                gbp = amounts.get((a, due)) if amounts is not None else None
                kb += 1
                pb += gbp or 0.0
                if d <= aged_line:
                    ka += 1
                    pa += gbp or 0.0
        if kb:
            rows[a] = (ka, kb, pa if amounts is not None else None, pb if amounts is not None else None)
    return rows


def age_grade(raws: list, quarter_end: date, fuel: str = "electricity", amounts_list: list | None = None) -> dict:
    """Pool one quarter end's stock over captures; the interval resamples accounts (as `grade`)."""
    per_account: dict = {}
    accounts_behind = accounts_aged = 0
    pa = pb = 0.0
    have_gbp = amounts_list is not None and all(m is not None for m in amounts_list)
    for i, raw in enumerate(raws):
        amounts = amounts_list[i] if have_gbp else None
        for a, (ka, kb, gpa, gpb) in age_reading(raw, quarter_end, fuel, amounts).items():
            accounts_behind += 1
            accounts_aged += ka > 0
            if have_gbp:
                pa += gpa
                pb += gpb
            k0, n0 = per_account.get(a, (0, 0))
            per_account[a] = (k0 + ka, n0 + kb)
    k = sum(r[0] for r in per_account.values())
    n = sum(r[1] for r in per_account.values())
    out = {"quarter_end": quarter_end.isoformat(), "bills_aged": k, "bills_behind": n,
           "accounts_behind": accounts_behind, "accounts_aged": accounts_aged,
           "distinct_accounts": len(per_account)}
    if n == 0:
        out["verdict"] = "CANNOT TELL -- no bill is over 91 days unpaid at this quarter end"
        return out
    out["share"] = k / n
    out["account_share"] = accounts_aged / accounts_behind
    out["gbp_share"] = pa / pb if have_gbp and pb else None
    out["clustered"] = account_clustered(per_account)
    target = ENERGY_UK_AGED_SHARE.get(quarter_end.year) if quarter_end.month == 12 else None
    if target is None:
        out["verdict"] = "NOT GRADED -- Energy UK publishes no aged share for this year"
    else:
        lo, hi = out["clustered"]
        out["target"] = target
        out["verdict"] = ("MET" if lo <= target <= hi else
                          "NOT MET, HIGH" if lo > target else "NOT MET, LOW")
    return out


def _amounts(capture_json: dict):
    """(account, due iso) -> pounds from a capture's `bills` side table, or None if it has none."""
    bills = capture_json.get("bills")
    if not bills:
        return None
    return {(a, row[0]): float(row[1]) for a, rows in bills.items() for row in rows}


def main(argv: list) -> int:
    if len(argv) >= 2 and argv[0] == "capture":
        capture(argv[1], argv[2] if len(argv) > 2 else "2019-12-31",
                int(argv[3]) if len(argv) > 3 else None)
        return 0
    if len(argv) >= 2 and argv[0] == "grade":
        raws = [json.load(open(p))["raw"] for p in argv[1:]]
        for fuel in ("electricity", "gas"):
            g = grade(raws, fuel)
            if not g["accounts"]:
                print(fuel, g["verdict"])
                continue
            lo, hi = g["clustered"]
            wlo, whi = g["wilson"]
            print(f"{fuel}: {g['behind']}/{g['accounts']} account-quarters = {g['share']:.1%}, "
                  f"{g['ratio']:.2f}x Ofgem {OFGEM_ARREARS_PLUS_DEBT_2019:.1%}; "
                  f"{g['distinct_behind']} of {g['distinct_accounts']} accounts ever behind\n"
                  f"  account-clustered {lo:.1%}-{hi:.1%}: {g['verdict']}\n"
                  f"  Wilson on account-quarters {wlo:.1%}-{whi:.1%}: {g['wilson_verdict']} "
                  f"(treats account-quarters as independent)\n"
                  f"  prepayment {g['prepayment_behind']} of {g['behind']} behind")
        return 0
    if len(argv) >= 2 and argv[0] == "age":
        caps = [json.load(open(p)) for p in argv[1:]]
        raws = [c["raw"] for c in caps]
        amounts = [_amounts(c) for c in caps]
        last = min(_d(c["end"]) for c in caps)
        for fuel in ("electricity", "gas"):
            print(f"{fuel}: share of the >91-day stock due a year or more before the quarter end")
            for year in range(2017, last.year + 1):
                qe = date(year, 12, 31)
                if qe > last:
                    break
                g = age_grade(raws, qe, fuel, amounts)
                if "share" not in g:
                    print(f"  {qe}: {g['verdict']}")
                    continue
                lo, hi = g["clustered"]
                gbp = f", pounds {g['gbp_share']:.0%}" if g["gbp_share"] is not None else ""
                beside = (f" (Energy UK 2025: {ENERGY_UK_AGED_SHARE[2025]:.0%}, beside, not graded)"
                          if year == 2024 else "")
                print(f"  {qe}: bills {g['bills_aged']}/{g['bills_behind']} = {g['share']:.0%} "
                      f"[{lo:.0%}-{hi:.0%}]; accounts {g['accounts_aged']}/{g['accounts_behind']} = "
                      f"{g['account_share']:.0%}{gbp}; {g['verdict']}{beside}")
        return 0
    print(__doc__.split("Usage:")[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
