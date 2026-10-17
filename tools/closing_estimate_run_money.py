"""The money a closing account's run of estimates carries at its last bill, from a run output.

Since 600be30bc a churned account's closing read is actual only where the world has a reason (a
smart meter in smart mode, `simulation/meter_reads.simulate_final_read`). Otherwise the last bill
is estimated and the run of estimates before it is never trued up. A replay counts those runs and
cannot price them, because it does not re-bill; this reads the money off a fresh run's own bills.

Every estimated bill carries its true total beside the total it billed
(`company/billing/monthly_bill_assembly._annotate_billing_basis`), so a run's money is
sum(true - billed), the same sum `_resolve_catchup` forms when an actual read arrives. Positive is
an undercharge the supplier never recovers; negative is an overcharge never credited.

For each supply point whose account closed -- the departures and the home movers, through the run's
own `simulation.household.supply_points_that_left`, which is the set the assembly asks the closing
read for -- the last bill is either:
  * `open`    -- estimated: the trailing run of estimates, last bill included, is left as it is;
  * `settled` -- actual: the run of estimates before it is trued up on that bill. A `forced` read
                 is one the final-read request produced (`forced_catch_up`), and that is what the
                 old rule did for every closing account.

The read log is aligned with the bills one to one (the assembly appends both in one step).

LIMITS. A held estimate went out as nothing (`_resolve_catchup` reconciles it as billed 0), but the
bill list keeps its estimated total, so a held bill's billed side is overstated here. Where the
book carries `catchup_raw_delta_gbp` the settled sum is checked against it and the mismatches are
counted. Money is raw: the SLC 21BA bar and the direct-debit balance are not applied.

    python3 -m tools.closing_estimate_run_money RUN_OUTPUT [RUN_OUTPUT ...]
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from pathlib import Path

from simulation.household import households_whose_account_closed, supply_points_that_left


def load_run_output(path: str | Path) -> dict:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _run_money(bills: list[dict]) -> tuple[float, float]:
    """(GBP, kWh) of true minus billed over a run of estimated bills."""
    gbp = sum(b["true_total_amount_gbp"] - b["total_amount_gbp"] for b in bills)
    kwh = sum(b["true_consumption_kwh"] - b["total_consumption_kwh"] for b in bills)
    return gbp, kwh


def _trailing_estimates(bills: list[dict]) -> list[dict]:
    run = []
    for bill in reversed(bills):
        if bill.get("billing_basis") != "estimated":
            break
        run.append(bill)
    return run[::-1]


def closing_accounts(run_output: dict) -> list[dict]:
    """One row per closed supply point with a bill: how its last bill left the run of estimates."""
    reads = run_output["meter_read_log"]
    bills = run_output["bills"]
    if len(reads) != len(bills):
        raise ValueError(f"read log ({len(reads)}) and bills ({len(bills)}) are not aligned")
    churned = supply_points_that_left(
        households_whose_account_closed(run_output), {b["customer_id"] for b in bills})
    by_account: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for bill, read in zip(bills, reads):
        if (bill["customer_id"], bill["period_end"]) != (read["customer_id"], read["period_end"]):
            raise ValueError(f"read log out of step with bills at {bill['customer_id']} {bill['period_end']}")
        if bill["customer_id"] in churned:
            by_account[bill["customer_id"]].append((bill, read))
    rows = []
    for cid, pairs in by_account.items():
        pairs.sort(key=lambda p: p[0]["period_end"])
        account_bills = [b for b, _ in pairs]
        last_bill, last_read = pairs[-1]
        if last_bill.get("billing_basis") == "estimated":
            run, outcome = _trailing_estimates(account_bills), "open"
        else:
            run = _trailing_estimates(account_bills[:-1])
            outcome = "settled"
        gbp, kwh = _run_money(run)
        rows.append({
            "customer_id": cid, "commodity": last_bill["commodity"],
            "payment_channel": last_bill.get("payment_channel"),
            "meter_type": last_read.get("meter_type"), "last_period_end": last_bill["period_end"],
            "outcome": outcome, "forced": bool(last_read.get("forced_catch_up")),
            "run_bills": len(run), "gbp": round(gbp, 2), "kwh": round(kwh, 2),
            "book_raw_delta_gbp": last_bill.get("catchup_raw_delta_gbp") if outcome == "settled" else None,
        })
    return rows


def summarise(rows: list[dict]) -> dict:
    """By outcome, fuel and direction: accounts, GBP, kWh. Empty runs are counted, never signed."""
    table: dict = {}
    for row in rows:
        if row["run_bills"] == 0:
            direction = "no_run"
        else:
            direction = "undercharge" if row["gbp"] > 0 else "overcharge" if row["gbp"] < 0 else "nil"
        label = row["outcome"] + ("_forced" if row["outcome"] == "settled" and row["forced"] else "")
        cell = table.setdefault(label, {}).setdefault(row["commodity"], {}).setdefault(
            direction, {"accounts": 0, "gbp": 0.0, "kwh": 0.0, "run_bills": 0})
        cell["accounts"] += 1
        cell["gbp"] = round(cell["gbp"] + row["gbp"], 2)
        cell["kwh"] = round(cell["kwh"] + row["kwh"], 2)
        cell["run_bills"] += row["run_bills"]
    checked = [r for r in rows if r["book_raw_delta_gbp"] is not None]
    mismatched = [r for r in checked if abs(r["book_raw_delta_gbp"] - r["gbp"]) > 0.02]
    return {"closing_accounts": len(rows), "by_outcome_fuel_direction": table,
            "settled_checked_against_book": len(checked),
            "settled_mismatched": len(mismatched),
            "settled_mismatch_gbp": round(sum(r["gbp"] - r["book_raw_delta_gbp"] for r in mismatched), 2)}


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_outputs", nargs="+")
    args = parser.parse_args(argv)
    for path in args.run_outputs:
        run_output = load_run_output(path)
        stamp = (run_output.get("producing_commit") or {}).get("commit")
        print(json.dumps({"run_output": str(path), "producing_commit": stamp,
                          **summarise(closing_accounts(run_output))}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
