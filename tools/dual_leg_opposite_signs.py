"""How many dual households hold a credit on one fuel and a debt on the other: N1 to N5.

WHY THIS EXISTS
---------------
SLC 27.8D gives a dual household the right, from 22 Jan 2021, to offset one fuel's credit against
the other's debt (fuel knowledge page §8b). The DD book and collections keep one balance per leg
and never net. How much of the book that right touches was predicted before any dual-fuel run was
read: `docs/staging/records/SEAT_PREREG_HOW_MANY_DUAL_HOUSEHOLDS_HOLD_A_CREDIT_ON_ONE_FUEL_AND_A_
DEBT_ON_THE_OTHER_ON_THE_PUBLISH_RUN_2026-10-18.md`. This prints N1 to N5 exactly as its §0 and §2
define them, on both arms of `seek_balance_at_review`, so the grade is read off and not composed
after the answer is visible.

DO NOT run it on a dual-book run output before the publish run named in that prereg's §0 is
committed. Reading an earlier run reads the answer before the grade.

THE DEFINITIONS (prereg §0)
---------------------------
* The book is `build_dd_balance_book` with the closed set `review_arms_from_run` uses
  (`closed_ids_from_bills`). A leg's balance is `BalancePoint.balance_gbp`, + = credit held. The
  closed set is passed as the prereg names it, but it cannot move N1 to N5: the book writes a
  trajectory's points before it takes the final-bill bar, so closing a leg changes the bar totals
  and not a balance point.
* A dual household is a `_billing_account_id` with a trajectory on both legs, `X` and `Xg`.
* Opposite signs: one leg above +£1 and the other below -£1 in the same `month`. A month counts
  for a household only when both legs have a balance point in it.
* Open at run end: both legs have a point in the run's last billed month.

THE EPISTEMIC WALL
------------------
Reads one finished run's issued bills and the opening amounts it published, through the book's own
builder. No ground truth.

USAGE
    python3 -m tools.dual_leg_opposite_signs docs/observability/run_output_latest.json.gz
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from statistics import median
from typing import Mapping

from saas.customer_reaction import _billing_account_id
from simulation.dd_balance_book import (
    build_dd_balance_book,
    closed_ids_from_bills,
    forecast_inputs_from_run,
)

#: Prereg §0: the band that keeps rounding noise out of a sign.
SIGN_BAND_GBP = 1.0
#: Prereg §2 N3: the months gas's winter draw falls in.
GAS_DEBIT_SEASON = frozenset({12, 1, 2, 3, 4})


def _sign(balance: float) -> int:
    return 1 if balance > SIGN_BAND_GBP else -1 if balance < -SIGN_BAND_GBP else 0


def _by_month(points: list) -> dict[str, float]:
    """`month -> balance` after the month's last bill."""
    return {p.month: p.balance_gbp for p in points}


def _share(num: int, den: int) -> float | None:
    return round(num / den, 4) if den else None


def dual_households(trajectories: Mapping[str, list]) -> dict[str, tuple[str, str]]:
    """`household -> (electricity leg id, gas leg id)` for households with both legs on DD."""
    out = {}
    for cid in trajectories:
        hh = _billing_account_id(cid)
        if hh == cid and f"{cid}g" in trajectories:
            out[hh] = (cid, f"{cid}g")
    return out


def read_arm(trajectories: Mapping[str, list], run_end: str) -> dict:
    """N1 to N5 over one book's trajectories."""
    pop = dual_households(trajectories)
    hh_months = opposite_months = gas_debit_months = gas_debit_in_season = 0
    ever = 0
    end_pop: list[str] = []
    end_opposite: list[dict] = []
    for hh, (e_id, g_id) in sorted(pop.items()):
        e, g = _by_month(trajectories[e_id]), _by_month(trajectories[g_id])
        hit = False
        for month in sorted(e.keys() & g.keys()):
            hh_months += 1
            se, sg = _sign(e[month]), _sign(g[month])
            if se * sg != -1:
                continue
            hit = True
            opposite_months += 1
            if sg < 0:
                gas_debit_months += 1
                gas_debit_in_season += int(month[5:7]) in GAS_DEBIT_SEASON
        ever += hit
        if run_end in e and run_end in g:
            end_pop.append(hh)
            se, sg = _sign(e[run_end]), _sign(g[run_end])
            if se * sg == -1:
                end_opposite.append({"household": hh, "electricity_gbp": e[run_end],
                                     "gas_gbp": g[run_end]})
    nettable = [min(abs(r["electricity_gbp"]), abs(r["gas_gbp"])) for r in end_opposite]
    return {
        "N1_population": len(pop),
        "N1_open_at_run_end": len(end_pop),
        "N2_opposite_at_run_end": len(end_opposite),
        "N2_share": _share(len(end_opposite), len(end_pop)),
        "N2_share_gas_credit_electricity_debit": _share(
            sum(r["gas_gbp"] > 0 for r in end_opposite), len(end_opposite)),
        "N3_household_months": hh_months,
        "N3_opposite_months": opposite_months,
        "N3_share": _share(opposite_months, hh_months),
        "N3_gas_debit_months": gas_debit_months,
        "N3_gas_debit_share_dec_to_apr": _share(gas_debit_in_season, gas_debit_months),
        "N4_ever_opposite": ever,
        "N4_share": _share(ever, len(pop)),
        "N5_median_nettable_gbp": round(median(nettable), 2) if nettable else None,
        "N5_share_electricity_smaller": _share(
            sum(abs(r["electricity_gbp"]) < abs(r["gas_gbp"]) for r in end_opposite),
            len(end_opposite)),
    }


def read_run(run: Mapping) -> dict:
    """Both arms of `seek_balance_at_review` on one run, with the run's own setting beside them."""
    bills, opening = run.get("bills"), run.get("opening_dd_by_customer")
    if not bills or not opening:
        raise SystemExit("refused: the run carries no bills or no opening DD amounts, so there is "
                         "no DD book to read")
    closed, run_end = closed_ids_from_bills(bills)
    arms = {}
    for name, seek in (("never_seeks", False), ("seeks", True)):
        book = build_dd_balance_book(bills, opening, closed, seek_balance_at_review=seek,
                                     **forecast_inputs_from_run(run))
        arms[name] = read_arm(book.trajectories, run_end)
    return {"run_end_month": run_end,
            "run_seek_balance_at_review": (run.get("dd_balance_book") or {}).get(
                "seek_balance_at_review"),
            "producing_commit": (run.get("producing_commit") or {}).get("commit"),
            "arms": arms}


def _load(path: Path) -> dict:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_output", type=Path)
    args = ap.parse_args(argv)
    print(json.dumps(read_run(_load(args.run_output)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
