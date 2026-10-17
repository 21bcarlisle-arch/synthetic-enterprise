"""Grade the company's ratio screen against the world's voids and thefts on one population (W2_36).

REUSE: tools/theft_void_screen_probe.py
CLASS: CUSTOM
INDEX: searched "theft void screen probe", "void theft screen" -- no existing row covers this.
       `simulation.meter_reads.premise_theft_study` generates a theft and stops; nothing puts the
       world's voids beside it or asks the company's screen which of the two it flags.

WHY. A theft that hides all of a home's use registers 0, and so does a void, so a ratio screen
cannot tell them apart by the ratio. What it can be told apart by is LENGTH: a void runs 0.7-1.15
months, a theft about two years. So the answer turns on the window the ratio is taken over, and
the probe measures a calendar month (a smart read) and a calendar year (an annualised read) apart.
Pre-registration: docs/staging/records/WORKER_PREREG_W2_36_WHAT_A_RATIO_SCREEN_FINDS_AMONG_VOIDS_AND_THEFTS_2026-10-16.md.

THE HARNESS READS THE WORLD'S TRUTH; THE SCREEN DOES NOT. `classify_anomaly` is handed registered
kWh and the EAC only. The cause each flag is filed under is the world's, and stays here.

NAMED SIMPLIFICATION: in `screen_table` occupied use is flat at the EAC, so its only flags are voids
and thefts. Owner-occupier voids are a GAP and are printed as none, which is not a finding that
owners have none.

OCCUPIED HOMES (`occupied_screen_table`) are the third source, priced apart from a published run: the
world's own use per month, against what the company expected for that month from what it could see
(its last three actual reads, or before its first read the registry EAC it was handed). The run
draws no theft. A void IS on an account: B7 slice 6 opens the incoming occupier's account on the
move date and makes its rows before `void_end` the owner's, at 0 kWh. The run does not publish
`void_end`, so an incoming account's periods up to and including its first with any use are filed
to the void (the void starts on the account's first day). An owner's move, whose void is a GAP,
has its first period filed there too; it rarely flags, as it is used.
Pre-registration: docs/staging/records/WORKER_PREREG_W2_36_WHAT_THE_SCREEN_FLAGS_AMONG_OCCUPIED_HOMES_2026-10-16.md.

The structural run table opens each incoming account on its outgoing account's closing read, as a
supplier would (§4a, the opening read at a change of tenancy).
Pre-registration: docs/staging/records/WORKER_PREREG_W2_36_THE_OPENING_READ_AT_A_CHANGE_OF_TENANCY_2026-10-17.md.
"""

from __future__ import annotations

import calendar
import datetime as dt
from collections import Counter

from company.billing.monthly_bill_assembly import ESTIMATE_WINDOW_READS
from company.billing.theft_indicator import (
    annual_window,
    boundary_read_status,
    classify_anomaly,
    empty_period_flags,
)
from company.billing.unread_month_estimate import estimate_unread_kwh, opening_estimate_kwh
from sim.customer_state_layer import Occupancy, TenureType, draw_home_move, void_end
from simulation.meter_reads import THEFT_UNREGISTERED_SHARE, premise_theft_months

FIRST_YEAR, LAST_YEAR = 2016, 2025
MONTHS = [(y, m) for y in range(FIRST_YEAR, LAST_YEAR + 1) for m in range(1, 13)]
CUTS = (0.05, 0.4, 0.65, 0.9)


def _void_span(tenure: TenureType, setting: str) -> tuple[dt.timedelta, str | None]:
    # The world's void is a fixed length per tenure (void_months says why), and void_end re-reads
    # the register on every call, so it is asked once per tenure for the span. void_end is in the
    # key so a substituted one is never answered from the cache.
    key = (tenure, setting, void_end)
    if key not in _SPANS:
        ref = dt.date(FIRST_YEAR, 1, 1)
        end, gap = void_end(ref, tenure, setting)
        _SPANS[key] = (end - ref, gap)
    return _SPANS[key]


_SPANS: dict = {}


def _empty_days_by_month(premise_id: str, tenure: TenureType, base_seed: int,
                         setting: str) -> tuple[list[int], str | None]:
    """Days in each month of MONTHS the premise stands empty, from the world's own moves and voids."""
    occupancy = Occupancy.of_customer(f"{premise_id}-occ0", tenure, premise_id=premise_id)
    span, gap = _void_span(tenure, setting)
    empty: set[dt.date] = set()
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        move = draw_home_move(occupancy, year, base_seed)
        if move is None:
            continue
        day = move.move_date
        while day < move.move_date + span:
            empty.add(day)
            day += dt.timedelta(days=1)
        occupancy = Occupancy(premise_id, move.incoming.occupancy_id, tenure)
    counts = Counter((d.year, d.month) for d in empty)
    return [counts.get(ym, 0) for ym in MONTHS], gap


def _cause(stolen: bool, emptied: bool) -> str | None:
    if stolen and emptied:
        return "both"
    return "theft" if stolen else "void" if emptied else None


def premise_windows(premise_id: str, tenure: TenureType, base_seed: int = 42,
                    setting: str = "default",
                    unregistered_share: float = THEFT_UNREGISTERED_SHARE) -> dict:
    """Each window's registered/EAC ratio and the world's cause for any shortfall."""
    empty, gap = _empty_days_by_month(premise_id, tenure, base_seed, setting)
    stealing = premise_theft_months(premise_id, len(MONTHS))
    monthly = []
    for (year, month), empty_days, stole in zip(MONTHS, empty, stealing):
        days = calendar.monthrange(year, month)[1]
        ratio = (1.0 - empty_days / days) * ((1.0 - unregistered_share) if stole else 1.0)
        monthly.append({"year": year, "month": month, "days": days, "empty_days": empty_days,
                        "ratio": ratio, "cause": _cause(stole, empty_days > 0)})
    annual = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        rows = [r for r in monthly if r["year"] == year]
        days = sum(r["days"] for r in rows)
        causes = {r["cause"] for r in rows if r["cause"]}
        annual.append({
            "year": year,
            "ratio": sum(r["ratio"] * r["days"] for r in rows) / days,
            "cause": ("both" if len(causes) > 1 or "both" in causes else next(iter(causes), None)),
        })
    return {"monthly": monthly, "annual": annual, "void_gap": gap}


def _flagged(ratio: float, cut: float) -> bool:
    # The screen is asked with registered kWh and EAC only; the 3,100 kWh EAC is a scale and cancels.
    status = classify_anomaly(ratio * 3100.0, 3100.0, investigate_below=cut, watch_below=cut)
    return status["status"] == "investigate"


def screen_table(tenure: TenureType, n_premises: int, base_seed: int = 42,
                 setting: str = "default") -> dict:
    """Flags per 10,000 premise-years, by window, cut and the world's cause."""
    counts = {w: {c: Counter() for c in CUTS} for w in ("monthly", "annual")}
    gap = None
    for i in range(n_premises):
        windows = premise_windows(f"PREM-{tenure.value}-{i}", tenure, base_seed, setting)
        gap = gap or windows["void_gap"]
        for w in ("monthly", "annual"):
            for row in windows[w]:
                for cut in CUTS:
                    if _flagged(row["ratio"], cut):
                        counts[w][cut][row["cause"] or "neither"] += 1
    scale = 10_000 / (n_premises * (LAST_YEAR - FIRST_YEAR + 1))
    return {
        "tenure": tenure.value, "setting": setting, "void_gap": gap,
        "per_10k_premise_years": {
            w: {cut: {k: round(v * scale, 1) for k, v in sorted(c.items())} for cut, c in by.items()}
            for w, by in counts.items()
        },
    }


def occupied_windows(run_output: dict) -> list[dict]:
    """Each electricity account's months and calendar years: registered kWh over the company's own
    expectation for the window, and which basis the expectation came from."""
    reads = {(r["customer_id"], r["period_end"]): r for r in run_output["meter_read_log"]}
    registry = run_output.get("opening_registry_kwh_by_customer") or {}
    periods: dict[str, list] = {}
    for bill in run_output["bills"]:
        if bill["commodity"] != "electricity":
            continue
        read = reads.get((bill["customer_id"], bill["period_end"]))
        if read is None:
            continue
        periods.setdefault(bill["customer_id"], []).append(
            (dt.date.fromisoformat(bill["period_start"]), dt.date.fromisoformat(bill["period_end"]),
             float(read["true_consumption_kwh"]), read["status"] == "actual"))
    out = []
    for cid, rows in periods.items():
        trailing: list[tuple[dt.date, dt.date, float]] = []
        months = []
        # `OCC-` is the run's id for an incoming occupier's account (sim/customer_state_layer).
        in_void = cid.startswith("OCC-")
        for start, end, kwh, actual in sorted(rows):
            # As the company stood before this period's read: monthly_bill_assembly's own two steps.
            if trailing:
                expected = estimate_unread_kwh("electricity", trailing[-ESTIMATE_WINDOW_READS:], start, end)
                basis = "own_reads"
            else:
                expected = opening_estimate_kwh("electricity", {"eac_kwh": registry.get(cid)}, start, end)
                basis = "opening"
            if expected and expected > 0:
                months.append({"year": end.year, "month": end.month, "days": (end - start).days + 1, "kwh": kwh,
                               "expected": expected, "ratio": kwh / expected, "basis": basis,
                               "cause": "void" if in_void else "occupied"})
            if kwh > 0:
                in_void = False
            if actual:
                trailing.append((start, end, kwh))
        years: dict[int, list] = {}
        for m in months:
            years.setdefault(m["year"], []).append(m)
        annual = [{"year": y, "days": sum(m["days"] for m in ms),
                   "ratio": sum(m["kwh"] for m in ms) / sum(m["expected"] for m in ms),
                   "basis": ms[0]["basis"],
                   "cause": "void" if any(m["cause"] == "void" for m in ms) else "occupied"}
                  for y, ms in years.items() if sum(m["days"] for m in ms) >= 360]
        out.append({"customer_id": cid, "monthly": months, "annual": annual})
    return out


def occupied_screen_table(run_output: dict) -> dict:
    """Flags per 10,000 premise-years on a run's own book, by window, cut, cause/basis."""
    accounts = occupied_windows(run_output)
    premise_years = sum(m["days"] for a in accounts for m in a["monthly"]) / 365.25
    counts = {w: {c: Counter() for c in CUTS} for w in ("monthly", "annual")}
    windows = {w: Counter() for w in ("monthly", "annual")}
    for account in accounts:
        for w in ("monthly", "annual"):
            for row in account[w]:
                key = f'{row["cause"]}/{row["basis"]}'
                windows[w][key] += 1
                for cut in CUTS:
                    if _flagged(row["ratio"], cut):
                        counts[w][cut][key] += 1
    scale = 10_000 / premise_years if premise_years else 0.0
    return {
        "accounts": len(accounts), "premise_years": round(premise_years, 1),
        "windows_by_basis": {w: dict(c) for w, c in windows.items()},
        "per_10k_premise_years": {
            w: {cut: {k: round(v * scale, 1) for k, v in sorted(c.items())} for cut, c in by.items()}
            for w, by in counts.items()
        },
    }


def _empty_period_causes(periods: list[dict], causes: dict, opening: str | None = None) -> Counter:
    # The company's flag is asked with its own fields only; the cause it is filed under is the world's.
    out = Counter()
    for flag in empty_period_flags(periods, opening):
        if flag["status"] == "investigate":
            out[causes[flag["span_end"]] or "neither"] += 1
    return out


def structural_table(tenure: TenureType, n_premises: int, base_seed: int = 42,
                     setting: str = "default") -> dict:
    """The two structural flags on the synthetic premises, per 10,000 premise-years, by cause.

    Every month is an actual read (a smart read). A wholly void month is the owner's (B7 slice 6), so
    it carries `void_owner_share` 1; any occupied day leaves a named occupier on the period."""
    empty, annual_default, annual_cut = Counter(), Counter(), Counter()
    for i in range(n_premises):
        windows = premise_windows(f"PREM-{tenure.value}-{i}", tenure, base_seed, setting)
        periods, causes = [], {}
        for r in windows["monthly"]:
            start = dt.date(r["year"], r["month"], 1).isoformat()
            end = dt.date(r["year"], r["month"], r["days"]).isoformat()
            periods.append({"period_start": start, "period_end": end, "commodity": "electricity",
                            "read_status": "actual", "registered_kwh": r["ratio"] * 3100.0 / 12,
                            "void_owner_share": 1.0 if r["empty_days"] == r["days"] else 0.0})
            causes[end] = r["cause"]
        empty += _empty_period_causes(periods, causes)
        for row in windows["annual"]:
            days = 366 if calendar.isleap(row["year"]) else 365
            cause = row["cause"] or "neither"
            if annual_window(row["ratio"] * 3100.0, 3100.0, days)["status"] != "unscreened":
                annual_default[cause] += 1
            if annual_window(row["ratio"] * 3100.0, 3100.0, days, investigate_below=CUTS[2])["status"] == "investigate":
                annual_cut[cause] += 1
    scale = 10_000 / (n_premises * (LAST_YEAR - FIRST_YEAR + 1))
    return {"tenure": tenure.value, "setting": setting, "per_10k_premise_years": {
        "empty_period": {k: round(v * scale, 1) for k, v in sorted(empty.items())},
        "annual_default_classified": {k: round(v * scale, 1) for k, v in sorted(annual_default.items())},
        f"annual_under_{CUTS[2]}": {k: round(v * scale, 1) for k, v in sorted(annual_cut.items())},
    }}


def _outgoing_accounts(run_output: dict, accounts: dict) -> tuple[dict, int]:
    """Each incoming electricity account's outgoing account at the same meter point, and how many
    could not be linked. A supplier knows this from its own book (`incoming_occupant_of`). Runs
    before `home_move_ins` was published are matched on move date and registry EAC, and a match
    that is still ambiguous is left unlinked rather than guessed."""
    incoming = {cid: min(p["period_start"] for p in ps) for cid, ps in accounts.items()
                if cid.startswith("OCC-")}
    if "home_move_ins" in run_output:
        links = {m["customer_id"]: m["premise"] for m in run_output["home_move_ins"]
                 if m["commodity"] == "electricity" and m["customer_id"] in incoming}
        return links, len(incoming) - len(links)
    registry = run_output.get("opening_registry_kwh_by_customer") or {}
    links = {}
    for cid, opened_on in incoming.items():
        found = [m["customer_id"] for m in run_output.get("home_move_outs", [])
                 if m["commodity"] == "electricity" and m["move_date"] == opened_on]
        if len(found) > 1:
            found = [f for f in found if registry.get(f) is not None and registry.get(f) == registry.get(cid)]
        if len(found) == 1:
            links[cid] = found[0]
    return links, len(incoming) - len(links)


def structural_run_table(run_output: dict) -> dict:
    """The two structural flags on a run's electricity book: occupied homes and incoming-account voids."""
    reads = {(r["customer_id"], r["period_end"]): r for r in run_output["meter_read_log"]}
    accounts: dict[str, list] = {}
    for bill in run_output["bills"]:
        read = reads.get((bill["customer_id"], bill["period_end"]))
        if bill["commodity"] != "electricity" or read is None:
            continue
        accounts.setdefault(bill["customer_id"], []).append({
            "customer_id": bill["customer_id"], "commodity": "electricity",
            "period_start": bill["period_start"], "period_end": bill["period_end"],
            "read_status": read["status"], "registered_kwh": float(read["true_consumption_kwh"]),
            "void_owner_share": bill.get("void_owner_share"), "occupier_share": bill.get("occupier_share")})
    outgoing, unlinked = _outgoing_accounts(run_output, accounts)
    empty, statuses, openings = Counter(), Counter(), Counter()
    for cid, periods in accounts.items():
        causes, in_void = {}, cid.startswith("OCC-")
        for p in sorted(periods, key=lambda p: p["period_start"]):
            causes[p["period_end"]] = "void" if in_void else "occupied"
            if p["registered_kwh"] > 0:
                in_void = False
        opening = None
        if cid in outgoing:
            opened_on = min(p["period_start"] for p in periods)
            opening = boundary_read_status(accounts.get(outgoing[cid], []), opened_on)
            openings[str(opening)] += 1
        for flag in empty_period_flags(periods, opening):
            statuses[f'{causes[flag["span_end"]]}/{flag["status"]}'] += 1
        empty += _empty_period_causes(periods, causes, opening)
    annual_default, annual_cut = Counter(), Counter()
    for account in occupied_windows(run_output):
        for row in account["annual"]:
            ms = [m for m in account["monthly"] if m["year"] == row["year"]]
            kwh, expected = sum(m["kwh"] for m in ms), sum(m["expected"] for m in ms)
            if annual_window(kwh, expected, row["days"])["status"] != "unscreened":
                annual_default[row["cause"]] += 1
            if annual_window(kwh, expected, row["days"], investigate_below=CUTS[2])["status"] == "investigate":
                annual_cut[row["cause"]] += 1
    premise_years = sum(m["days"] for a in occupied_windows(run_output) for m in a["monthly"]) / 365.25
    scale = 10_000 / premise_years if premise_years else 0.0
    return {"accounts": len(accounts), "premise_years": round(premise_years, 1),
            "incoming_accounts_by_opening_read": dict(openings),
            "incoming_accounts_unlinked": unlinked,
            "zero_advance_spans_by_cause_and_status": dict(statuses),
            "per_10k_premise_years": {
                "empty_period": {k: round(v * scale, 1) for k, v in sorted(empty.items())},
                "annual_default_classified": {k: round(v * scale, 1) for k, v in sorted(annual_default.items())},
                f"annual_under_{CUTS[2]}": {k: round(v * scale, 1) for k, v in sorted(annual_cut.items())},
            }}


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--premises", type=int, default=5000)
    parser.add_argument("--setting", default="default")
    parser.add_argument("--occupied-run", help="a run output; prices the occupied-home flags instead")
    parser.add_argument("--structural", action="store_true",
                        help="grade the empty-period and annual-window flags instead of the ratio screen")
    args = parser.parse_args()
    if args.occupied_run:
        from tools.run_output_store import load_run_output

        table = structural_run_table if args.structural else occupied_screen_table
        print(json.dumps(table(load_run_output(args.occupied_run)), indent=1))
        raise SystemExit(0)
    for t in TenureType:
        table = structural_table if args.structural else screen_table
        print(json.dumps(table(t, args.premises, setting=args.setting), indent=1))
