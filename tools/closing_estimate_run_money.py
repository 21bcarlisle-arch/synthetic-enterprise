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
counted. `summarise` is raw money; `departing_view` applies the SLC 21BA bar and the direct-debit
balance (below).

    python3 -m tools.closing_estimate_run_money [--departing | --read-duty [--instructed-read] | --must-read] RUN_OUTPUT [RUN_OUTPUT ...]
"""

from __future__ import annotations

import datetime as dt
import gzip
import json
from collections import defaultdict
from pathlib import Path

from company.interfaces.bill_assembly import barred_at_charge_recovery
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


def _period(bill: dict) -> tuple[dt.date, dt.date]:
    end = dt.date.fromisoformat(bill["period_end"][:10])
    start = bill.get("period_start")
    return (dt.date.fromisoformat(start[:10]) if start else end.replace(day=1)), end


def what_closure_shows(bills: list[dict], run_bills: int, collected: list[float] | None = None,
                       balance_gbp: float = 0.0) -> dict:
    """An open run's money as it would land if it were trued up at the last bill.

    `bills` is the supply point's bills in period order; the last `run_bills` are the open run.
    `collected` is what the direct debit took per bill and `balance_gbp` the billed-basis balance at
    the last bill (positive is credit); without them the account pays what it is billed and leaves
    with nothing owed either way. The 21BA bar is taken at the last bill's end, capped at the debit
    the demand seeks, and counted over what the billed balance already barred, so it is the bar the
    open money ADDS. An overcharge is never barred. Returns the money (true - billed), the bar it
    adds, the new demand (what is asked of someone who has left, beyond what the billed balance
    already asked) and the rest, which the balance absorbs as a smaller refund or a smaller debt."""
    run = bills[len(bills) - run_bills:] if run_bills else []
    money = sum(b["true_total_amount_gbp"] - b["total_amount_gbp"] for b in run)
    recovered = collected if collected is not None else [b["total_amount_gbp"] for b in bills]
    in_run = {id(b) for b in run}
    billed_periods, true_periods = [], []
    for bill, took in zip(bills, recovered):
        start, end = _period(bill)
        billed_periods.append((start, end, bill["total_amount_gbp"], took))
        true = bill["true_total_amount_gbp"] if id(bill) in in_run else bill["total_amount_gbp"]
        true_periods.append((start, end, true, took))
    demand_date = _period(bills[-1])[1]
    debit_before, debit_after = max(-balance_gbp, 0.0), max(money - balance_gbp, 0.0)
    barred_before = min(debit_before, barred_at_charge_recovery(billed_periods, demand_date))
    barred_after = min(debit_after, barred_at_charge_recovery(true_periods, demand_date))
    new_demand = (debit_after - barred_after) - (debit_before - barred_before)
    added_bar = barred_after - barred_before
    return {"gbp": round(money, 2), "added_bar_gbp": round(added_bar, 2),
            "new_demand_gbp": round(new_demand, 2),
            "absorbed_gbp": round(money - added_bar - new_demand, 2)}


def departing_view(run_output: dict, rows: list[dict] | None = None,
                   keep_accounts: bool = False) -> dict:
    """`what_closure_shows` over every open closing run, by fuel and direction, beside the raw money.

    The direct-debit book is rebuilt (`simulation.dd_balance_book.build_dd_balance_book`) over the
    closed set `review_arms_from_run` uses, and its summary is checked against the run's own: a
    rebuild that does not reproduce the published book is not one whose balances can be read."""
    from simulation.dd_balance_book import build_dd_balance_book, forecast_inputs_from_run

    rows = closing_accounts(run_output) if rows is None else rows
    bills = run_output["bills"]
    last_month: dict[str, str] = {}
    for b in bills:
        last_month[b["customer_id"]] = max(last_month.get(b["customer_id"], ""), b["period_end"][:7])
    run_end = max(last_month.values())
    closed = {cid for cid, month in last_month.items() if month < run_end}
    book = build_dd_balance_book(bills, run_output.get("opening_dd_by_customer"), closed,
                                 **forecast_inputs_from_run(run_output))
    published = (run_output.get("dd_balance_book") or {}).get("summary") or {}
    rebuilt = book.summary()
    keys = ("n_customers", "portfolio_final_balance_gbp", "back_billing_barred_at_final_bills_gbp")
    reproduced = all(published.get(k) == rebuilt.get(k) for k in keys)
    by_cust: dict[str, list[dict]] = defaultdict(list)
    for b in bills:
        by_cust[b["customer_id"]].append(b)
    table: dict = {}
    accounts = []
    no_dd_balance = 0
    for row in rows:
        if row["outcome"] != "open" or row["run_bills"] == 0:
            continue
        account_bills = sorted(by_cust[row["customer_id"]], key=lambda b: b["period_end"])
        points = book.trajectories.get(row["customer_id"])
        collected, balance = None, 0.0
        if points is not None and len(points) == len(account_bills):
            channel = "direct_debit"
            collected = [p.collected_gbp * p.n_collections for p in points]
            balance = points[-1].balance_gbp
        else:
            no_dd_balance += row["payment_channel"] == "direct_debit"
            channel = "no_dd_balance"
        shown = what_closure_shows(account_bills, row["run_bills"], collected, balance)
        direction = "undercharge" if shown["gbp"] > 0 else "overcharge" if shown["gbp"] < 0 else "nil"
        accounts.append({"customer_id": row["customer_id"], "commodity": row["commodity"],
                         "channel": channel, "run_bills": row["run_bills"], **shown,
                         **({"collected": collected, "balance_gbp": balance} if keep_accounts else {})})
        cell = table.setdefault(row["commodity"], {}).setdefault(direction, {}).setdefault(
            channel, {"accounts": 0, "with_added_bar": 0, "with_new_demand": 0,
                      "with_new_demand_over_10": 0, "gbp": 0.0,
                      "added_bar_gbp": 0.0, "new_demand_gbp": 0.0, "absorbed_gbp": 0.0})
        cell["accounts"] += 1
        cell["with_added_bar"] += abs(shown["added_bar_gbp"]) >= 0.01
        cell["with_new_demand"] += shown["new_demand_gbp"] >= 0.01
        cell["with_new_demand_over_10"] += shown["new_demand_gbp"] > 10
        for k in ("gbp", "added_bar_gbp", "new_demand_gbp", "absorbed_gbp"):
            cell[k] = round(cell[k] + shown[k], 2)
    accounts.sort(key=lambda a: -abs(a["gbp"]))
    kept = {"accounts": accounts} if keep_accounts else {}
    return {**kept, "dd_book_reproduced": reproduced, "dd_book_published": {k: published.get(k) for k in keys},
            "dd_book_rebuilt": {k: rebuilt.get(k) for k in keys},
            "dd_channel_without_a_balance": no_dd_balance,
            "by_fuel_direction_channel": table, "largest_accounts": accounts[:10]}


def dispute_reach(run_output: dict, arm: str = "ceiling") -> dict:
    """How much of the switcher closing-estimate money a disputed switch read returns.

    For each open switcher run (a household on `churned_billing_accounts` and not a home mover),
    the world's `switch_read_dispute` draws the gaining supplier's first read from the switch date
    and decides the dispute under `arm`. A disputed run's money comes back as the amended final bill
    REC Schedule 30 8.1(b) asks for, priced as `what_closure_shows` prices it (21BA bar and DD balance
    kept: whether the amended bill is a back-bill is a GAP, and keeping the bar errs against it).
    The agreed read is taken as the true register, which is the ceiling's own assumption: a real one
    is deemed backwards from the gaining supplier's read. Runs whose 12 months reach past the run's
    end are counted as censored, not as unreached."""
    from simulation.household import household_of
    from simulation.meter_reads import SWITCH_READ_DISPUTE_THRESHOLD_KWH, switch_read_dispute

    rows = closing_accounts(run_output)
    view = departing_view(run_output, rows, keep_accounts=True)
    shown = {a["customer_id"]: a for a in view["accounts"]}
    switched = set(run_output.get("churned_billing_accounts") or [])
    movers = {m["household"] for m in run_output.get("home_move_outs") or []}
    run_end = max(b["period_end"][:10] for b in run_output["bills"])
    table: dict = {}
    reached = []
    for row in rows:
        hh = household_of(row["customer_id"])
        if row["customer_id"] not in shown or hh not in switched or hh in movers:
            continue
        a = shown[row["customer_id"]]
        over = row["kwh"] > SWITCH_READ_DISPUTE_THRESHOLD_KWH[row["commodity"]]
        if a["gbp"] <= 0 or not over:
            continue
        verdict = switch_read_dispute(row["customer_id"], row["commodity"], row["last_period_end"],
                                      row["meter_type"] or "traditional", row["kwh"], arm=arm)
        window_end = dt.date.fromisoformat(row["last_period_end"][:10]).replace(
            year=int(row["last_period_end"][:4]) + 1).isoformat()
        state = ("disputed" if verdict["disputed"] else
                 "censored" if window_end > run_end and verdict["first_read_period_end"] is None
                 else "no_first_read" if verdict["first_read_period_end"] is None else "not_raised")
        cell = table.setdefault(state, {"runs": 0, "new_demand_gbp": 0.0, "gbp": 0.0})
        cell["runs"] += 1
        cell["new_demand_gbp"] = round(cell["new_demand_gbp"] + a["new_demand_gbp"], 2)
        cell["gbp"] = round(cell["gbp"] + a["gbp"], 2)
        reached.append({"customer_id": row["customer_id"], "commodity": row["commodity"],
                        "last_period_end": row["last_period_end"], "kwh": row["kwh"],
                        "run_bills": row["run_bills"], "new_demand_gbp": a["new_demand_gbp"],
                        "state": state, "first_read": verdict["first_read_period_end"]})
    reached.sort(key=lambda r: -r["new_demand_gbp"])
    return {"arm": arm, "dd_book_reproduced": view["dd_book_reproduced"], "by_state": table,
            "seed_new_demand_gbp": round(sum(c["new_demand_gbp"] for c in table.values()), 2),
            "runs": reached}


def duty_year_dates(bills: list[dict]) -> set[tuple[str, str]]:
    """(account, period_end) of each SLC 21B.4 register row where the duty applies."""
    from company.billing.read_duty_register import read_duty_register

    return {(r["account_id"], r["date"]) for r in read_duty_register(bills) if r["duty_applies"]}


def year_split(run: list[dict], year_dates: set[tuple[str, str]]) -> tuple[int | None, float]:
    """Where in an open run of estimates the 21B.4 year fell, and the money (true - billed) up to it.

    `year_dates` is `duty_year_dates` over the run's bills. Returns
    (None, 0.0) for a run that closed inside the year."""
    at = next((i for i, b in enumerate(run) if (b["customer_id"], b["period_end"]) in year_dates), None)
    return at, (_run_money(run[:at + 1])[0] if at is not None else 0.0)


def read_duty_reach(run_output: dict) -> dict:
    """How much of the open closing money sits on runs that crossed the SLC 21B.4 year before closure.

    An open run crossed the year if `company.billing.read_duty_register` wrote a row on one of its
    bills: the company could see the year pass while the customer was on supply. The run's money is
    split at that bill. Bills up to it are what a read at the year would have trued up on supply,
    all inside 21BA's 12 months; bills after it would have begun a fresh run. A decomposition, not
    a counterfactual: whether a request at the year gets a read is a GAP, and the world cannot
    answer one."""
    from simulation.household import household_of
    from simulation.meter_reads import is_hard_to_read

    rows = closing_accounts(run_output)
    view = departing_view(run_output, rows, keep_accounts=True)
    shown = {a["customer_id"]: a for a in view["accounts"]}
    year_dates = duty_year_dates(run_output["bills"])
    by_cust: dict[str, list[dict]] = defaultdict(list)
    for b in run_output["bills"]:
        by_cust[b["customer_id"]].append(b)
    switched = set(run_output.get("churned_billing_accounts") or [])
    movers = {m["household"] for m in run_output.get("home_move_outs") or []}
    table: dict = {}
    crossed = []
    for row in rows:
        a = shown.get(row["customer_id"])
        if a is None:
            continue
        run = sorted(by_cust[row["customer_id"]], key=lambda b: b["period_end"])[-row["run_bills"]:]
        at, to_year = year_split(run, year_dates)
        state = "crossed_the_year" if at is not None else "closed_inside_the_year"
        cell = table.setdefault(state, {"runs": 0, "gbp": 0.0, "new_demand_gbp": 0.0,
                                        "undercharge_runs": 0, "undercharge_gbp": 0.0,
                                        "undercharge_new_demand_gbp": 0.0})
        cell["runs"] += 1
        cell["gbp"] = round(cell["gbp"] + a["gbp"], 2)
        cell["new_demand_gbp"] = round(cell["new_demand_gbp"] + a["new_demand_gbp"], 2)
        if a["gbp"] > 0:
            cell["undercharge_runs"] += 1
            cell["undercharge_gbp"] = round(cell["undercharge_gbp"] + a["gbp"], 2)
            cell["undercharge_new_demand_gbp"] = round(
                cell["undercharge_new_demand_gbp"] + a["new_demand_gbp"], 2)
        if at is None:
            continue
        hh = household_of(row["customer_id"])
        crossed.append({
            "customer_id": row["customer_id"], "commodity": row["commodity"],
            "channel": a["channel"], "run_bills": row["run_bills"],
            "year_bill": run[at]["period_end"][:10], "last_period_end": row["last_period_end"][:10],
            "left_by": "move" if hh in movers else "switch" if hh in switched else "other",
            "hard_to_read": is_hard_to_read(row["customer_id"]),
            "gbp": a["gbp"], "gbp_to_the_year": round(to_year, 2),
            "gbp_after_the_year": round(a["gbp"] - to_year, 2),
            "added_bar_gbp": a["added_bar_gbp"], "new_demand_gbp": a["new_demand_gbp"]})
    crossed.sort(key=lambda r: -r["new_demand_gbp"])
    return {"dd_book_reproduced": view["dd_book_reproduced"], "by_state": table,
            "open_new_demand_gbp": round(sum(c["new_demand_gbp"] for c in table.values()), 2),
            "undercharge_new_demand_gbp": round(
                sum(c["undercharge_new_demand_gbp"] for c in table.values()), 2),
            "crossed": crossed}


def _instruction_visits(bills: list[dict]) -> list[int]:
    """Indices of an account's bills (period order) on which an instructed read's visit falls:
    `read_instruction_due` on the estimates in a row before it. An actual bill ends a run and asks
    for no visit, so these are the same bills at either access end."""
    from company.billing.read_duty_register import read_instruction_due

    visits, incoming = [], 0
    for i, bill in enumerate(bills):
        if bill.get("billing_basis") != "estimated":
            incoming = 0
            continue
        if read_instruction_due(incoming, bill.get("payment_channel")):
            visits.append(i)
        incoming += 1
    return visits


def read_instruction_reach(run_output: dict) -> dict:
    """What the company's read instruction at the 11th estimate (read_access_and_theft_duties.md
    s.2.8) reaches on a run's own bills, at both access ends. The visit's outcome is a GAP.

    `no_access`: no visit reads, so the bills are the run's own. The instructions are counted, the
    open closing money and its 21BA bar are `departing_view`'s, and the on-supply bar is what the
    run's catch-ups wrote off on runs of 12 or more. `read`: every visit reads, so the run is trued
    up on supply at the visit and a fresh run starts. What a visit trues up is barred over its own
    periods at the visit's date. An open closing run keeps only the estimates after its last visit,
    priced by `what_closure_shows` with the run's own collections and closing balance.

    A decomposition, not a re-run, and the read end is an upper bound. After a read, a real run
    would re-estimate from it and its direct debit would be reviewed, and neither is modelled here."""
    from company.billing.read_duty_register import read_duty_register

    bills = run_output["bills"]
    by_cust: dict[str, list[dict]] = defaultdict(list)
    for b in bills:
        by_cust[b["customer_id"]].append(b)
    for account in by_cust.values():
        account.sort(key=lambda b: b["period_end"])
    rows = closing_accounts(run_output)
    view = departing_view(run_output, rows, keep_accounts=True)
    shown = {a["customer_id"]: a for a in view["accounts"]}
    instructions: dict[str, int] = defaultdict(int)
    prepayment_instructions = 0
    read_trued_up_gbp = read_trued_up_bar_gbp = 0.0
    on_supply_bar_no_access = 0.0
    visits_of: dict[str, list[int]] = {}
    for cid, account in by_cust.items():
        visits = _instruction_visits(account)
        visits_of[cid] = visits
        for i in visits:
            instructions[account[i].get("commodity", "electricity")] += 1
            prepayment_instructions += account[i].get("payment_channel") == "prepayment"
            start = i
            while start > 0 and account[start - 1].get("billing_basis") == "estimated" and (
                    start - 1) not in visits:
                start -= 1
            trued = account[start:i + 1]
            read_trued_up_gbp += _run_money(trued)[0]
            read_trued_up_bar_gbp += barred_at_charge_recovery(
                [(*_period(b), b["true_total_amount_gbp"], b["total_amount_gbp"]) for b in trued],
                _period(account[i])[1])
        on_supply_bar_no_access += sum(
            b.get("catchup_written_off_gbp") or 0.0 for b in account
            if (b.get("catchup_periods_covered") or 0) >= 12)
    ends = {"no_access": defaultdict(float), "read": defaultdict(float)}
    runs_reached = 0
    for row in rows:
        a = shown.get(row["customer_id"])
        if a is None:
            continue
        account = by_cust[row["customer_id"]]
        start = len(account) - row["run_bills"]
        last = max((i for i in visits_of[row["customer_id"]] if i >= start), default=None)
        if last is None:
            at_read = a
        else:
            runs_reached += 1
            tail = len(account) - last - 1
            at_read = (what_closure_shows(account, tail, a["collected"], a["balance_gbp"]) if tail
                       else {"gbp": 0.0, "added_bar_gbp": 0.0, "new_demand_gbp": 0.0})
        # Signed by the run as billed, so both ends count the same runs.
        direction = "undercharge_" if a["gbp"] > 0 else "overcharge_"
        for end, money in (("no_access", a), ("read", at_read)):
            for k in ("gbp", "added_bar_gbp", "new_demand_gbp"):
                ends[end][k] += money[k]
                ends[end][direction + k] += money[k]
                if last is not None:
                    ends[end]["reached_" + k] += money[k]
                    ends[end]["reached_" + direction + k] += money[k]
    duty_rows = sum(r["duty_applies"] for r in read_duty_register(bills))
    rounded = {end: {k: round(v, 2) for k, v in cell.items()} for end, cell in ends.items()}
    rounded["no_access"]["on_supply_bar_on_runs_of_12_or_more_gbp"] = round(on_supply_bar_no_access, 2)
    rounded["read"]["trued_up_at_visits_gbp"] = round(read_trued_up_gbp, 2)
    rounded["read"]["bar_on_what_visits_true_up_gbp"] = round(read_trued_up_bar_gbp, 2)
    return {"dd_book_reproduced": view["dd_book_reproduced"],
            "instructions_by_fuel": dict(instructions), "prepayment_instructions": prepayment_instructions,
            "duty_register_rows": duty_rows, "open_closing_runs_reached": runs_reached,
            "by_end": rounded}


def must_read_reach(run_output: dict) -> dict:
    """Where the UNC M5.10 gas must-read falls on a run's own bills, and what its ceiling arm reaches.

    An attempt falls on an estimated bill that `simulation.meter_reads.must_read_due` names: gas, a
    traditional meter, 24 or more estimates before it. Under the register arm (the visit outcome is a
    GAP) no attempt reads, so the bills are the run's own and every attempt is counted. Under the
    ceiling arm each attempt reads, which ends the run of estimates there: the 24 before it are trued
    up on supply and a fresh run starts. A decomposition of this run's money, not a re-run: a closing
    run keeps only the estimates after its last ceiling read, so its `new_demand_gbp` is the most
    the ceiling can take off it."""
    from simulation.meter_reads import MUST_READ_UNREAD_MONTHS, must_read_due

    reads = run_output["meter_read_log"]
    bills = run_output["bills"]
    if len(reads) != len(bills):
        raise ValueError(f"read log ({len(reads)}) and bills ({len(bills)}) are not aligned")
    by_account: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for bill, read in zip(bills, reads):
        by_account[bill["customer_id"]].append((bill, read))
    rows = closing_accounts(run_output)
    closing = {r["customer_id"]: r for r in rows if r["outcome"] == "open"}
    shown = {a["customer_id"]: a for a in departing_view(run_output, rows, keep_accounts=True)["accounts"]}
    attempts = {"gas": 0, "electricity": 0}
    accounts = []
    for cid, pairs in by_account.items():
        pairs.sort(key=lambda p: p[0]["period_end"])
        incoming, hits = 0, []
        for i, (bill, read) in enumerate(pairs):
            if bill.get("billing_basis") != "estimated":
                incoming = 0
                continue
            if must_read_due(bill.get("commodity", "electricity"), read.get("meter_type"), incoming):
                hits.append(i)
            incoming += 1
        if not hits:
            continue
        commodity = pairs[0][0].get("commodity", "electricity")
        attempts[commodity] = attempts.get(commodity, 0) + len(hits)
        # Ceiling: an attempt reads, so the next falls MUST_READ_UNREAD_MONTHS + 1 bills later.
        ceiling, nxt = [], None
        for i in hits:
            if nxt is None or i >= nxt:
                ceiling.append(i)
                nxt = i + MUST_READ_UNREAD_MONTHS + 1
        open_row = closing.get(cid)
        tail_gbp = None
        if open_row is not None:
            run = [b for b, _ in pairs][-open_row["run_bills"]:]
            start = len(pairs) - open_row["run_bills"]
            last = max((i for i in ceiling if i >= start), default=None)
            tail_gbp = round(_run_money(run[last - start + 1:])[0], 2) if last is not None else None
        accounts.append({
            "customer_id": cid, "commodity": commodity, "bills": len(pairs),
            "register_attempts": len(hits), "first_attempt": pairs[hits[0]][0]["period_end"][:10],
            "ceiling_reads": len(ceiling), "closing_open_run": open_row is not None,
            "open_run_bills": open_row["run_bills"] if open_row else None,
            "open_gbp": open_row["gbp"] if open_row else None,
            "open_gbp_after_ceiling": tail_gbp,
            "new_demand_gbp": (shown.get(cid) or {}).get("new_demand_gbp") if open_row else None})
    accounts.sort(key=lambda a: -a["register_attempts"])
    on_closing = [a for a in accounts if a["closing_open_run"]]
    return {"register_attempts_by_fuel": attempts, "accounts_reached": len(accounts),
            "closing_runs_reached": len(on_closing),
            "ceiling_new_demand_bound_gbp": round(sum(a["new_demand_gbp"] or 0.0 for a in on_closing), 2),
            "accounts": accounts}


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--departing", action="store_true",
                        help="apply the 21BA bar and the direct-debit balance to the open runs")
    parser.add_argument("--dispute", choices=("register", "ceiling"),
                        help="what a disputed switch read returns of the over-threshold switcher money")
    parser.add_argument("--read-duty", action="store_true",
                        help="split the open money by whether its run crossed the SLC 21B.4 year")
    parser.add_argument("--instructed-read", action="store_true",
                        help="with --read-duty: the company's read instruction at the 11th estimate, at both access ends")
    parser.add_argument("--must-read", action="store_true",
                        help="where the UNC M5.10 gas must-read falls, and what its ceiling arm reaches")
    parser.add_argument("run_outputs", nargs="+")
    args = parser.parse_args(argv)
    for path in args.run_outputs:
        run_output = load_run_output(path)
        stamp = (run_output.get("producing_commit") or {}).get("commit")
        rows = closing_accounts(run_output)
        view = (must_read_reach(run_output) if args.must_read
                else read_instruction_reach(run_output) if args.read_duty and args.instructed_read
                else read_duty_reach(run_output) if args.read_duty
                else dispute_reach(run_output, args.dispute) if args.dispute
                else departing_view(run_output, rows) if args.departing else summarise(rows))
        print(json.dumps({"run_output": str(path), "producing_commit": stamp, **view}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
