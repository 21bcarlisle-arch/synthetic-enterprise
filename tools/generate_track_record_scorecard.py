#!/usr/bin/env python3
"""Generate site/state/track_record_scorecard.json -- S1's predicted-vs-realised scorecard.

Phase RX (S1 Option B, docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md, Decision 2:
public from day one, misses included). Walks the immutable daily decision log
(site/state/live_decisions_log.jsonl, written by tools/run_live_decisions.py) and joins
each logged, now-elapsed prediction against what the latest live_portfolio.json snapshot
shows actually happened. It is fully expected -- and correct -- for this to show zero
graded entries for a long time after the clock starts: renewal windows are weeks out and
the log itself is only a few days old. This generator must handle that state cleanly, not
as an error case.

Three grading tracks, matching the design note's own scope:

1. Renewal-price flags: did the customer renew at/near the proposed rate? Graded once the
   flag's renewal_date has passed (real wall-clock "today") AND live_portfolio.json shows
   the customer actually renewed since the flag was raised. If the customer has fallen out
   of the active book, this is reported as "churned" -- but honestly caveated: a snapshot
   only says "not currently active", it carries no historical time series and therefore no
   real departure date, so this is an INFERENCE, not a logged event.

2. Hedge recommendations: only graded once real new settlement-price data has actually
   landed since the entry was logged (i.e. the current market_data_stale_days figure is
   smaller than what was recorded for that entry -- meaning the market clock genuinely
   advanced). Until Option A (a rolling live Elexon fetch, not built here) lands, the
   market clock never advances, so every hedge recommendation stays honestly reported as
   "ungraded -- market data has not advanced". Fabricating a grade against a frozen market
   would misrepresent what has actually been tested.

3. Retention EVs (Phase RX's new field, see tools/run_live_decisions.py): no realised-
   outcome signal exists anywhere yet (nothing logs whether an offer was actually made or
   what happened after) -- these are reported as logged-but-ungraded. A grading mechanism
   will need a real "was this customer actually offered a retention discount and did they
   stay" signal before it can exist; inventing one now would not be a real measurement.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parent.parent
LOG_PATH = PROJECT / "site" / "state" / "live_decisions_log.jsonl"
PORTFOLIO_PATH = PROJECT / "site" / "state" / "live_portfolio.json"
OUT_PATH = PROJECT / "site" / "state" / "track_record_scorecard.json"

# Judgment call (explicitly flagged per the task spec): "on target" vs "missed" for a
# renewal-price prediction is defined as the realised rate landing within +/-2% of the
# proposed rate at the time of the flag. 2% is a deliberately tight commercial tolerance
# for a fixed-term energy tariff (bigger than that and a customer would notice the
# difference on their bill) -- not derived from any published benchmark, a reasonable
# starting point that can be revisited once real graded data exists to calibrate against.
RENEWAL_TOLERANCE_PCT = 0.02


def _load_log(log_path=None):
    path = _P(log_path) if log_path else LOG_PATH
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    entries.sort(key=lambda e: e.get("decision_run_at", ""))
    return entries


def _load_portfolio(portfolio_path=None):
    path = _P(portfolio_path) if portfolio_path else PORTFOLIO_PATH
    try:
        data = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return {c["cid"]: c for c in data.get("customers", []) if "cid" in c}


def _grade_renewal_flag(flag, customers_by_cid, tolerance_pct):
    cid = flag.get("cid")
    renewal_date = flag.get("renewal_date")
    proposed_rate = flag.get("proposed_rate_gbp_per_mwh")
    cust = customers_by_cid.get(cid)

    if cust is None:
        return {
            "cid": cid,
            "renewal_date": renewal_date,
            "proposed_rate_gbp_per_mwh": proposed_rate,
            "outcome": "churned",
            "graded": True,
            "note": (
                "cid no longer present in live_portfolio.json's active customer list -- "
                "inferred departure from a single snapshot, not a logged churn event or "
                "date. live_portfolio.json carries no historical time series, so 'absent' "
                "only means 'not currently active', nothing more precise than that."
            ),
        }

    last_renewal = cust.get("last_renewal_date")
    renewed_since_flag = bool(last_renewal) and bool(renewal_date) and last_renewal >= renewal_date
    if not renewed_since_flag:
        return {
            "cid": cid,
            "renewal_date": renewal_date,
            "proposed_rate_gbp_per_mwh": proposed_rate,
            "outcome": "no_renewal_detected_yet",
            "graded": False,
            "note": (
                "the flagged renewal date has passed relative to real wall-clock today, "
                "but live_portfolio.json's last_renewal_date has not advanced past it -- "
                "inconclusive (the portfolio snapshot itself may simply be stale), not "
                "counted as a miss."
            ),
        }

    actual_rate = cust.get("current_rate_gbp_per_mwh")
    if actual_rate is None or not proposed_rate:
        return {
            "cid": cid,
            "renewal_date": renewal_date,
            "proposed_rate_gbp_per_mwh": proposed_rate,
            "outcome": "no_renewal_detected_yet",
            "graded": False,
            "note": "missing rate data (actual or proposed) -- cannot grade.",
        }

    diff_pct = abs(actual_rate - proposed_rate) / proposed_rate
    outcome = "renewed_on_target" if diff_pct <= tolerance_pct else "renewed_off_target"
    return {
        "cid": cid,
        "renewal_date": renewal_date,
        "proposed_rate_gbp_per_mwh": proposed_rate,
        "actual_rate_gbp_per_mwh": actual_rate,
        "diff_pct": round(diff_pct, 4),
        "outcome": outcome,
        "graded": True,
    }


def _grade_renewals(log_entries, customers_by_cid, today, tolerance_pct):
    graded, pending, inconclusive = [], [], []
    for entry in log_entries:
        run_date = entry.get("decision_run_at", "")[:10]
        for flag in entry.get("renewal_flags", []):
            renewal_date = flag.get("renewal_date")
            row_base = {"decision_run_at": run_date, "cid": flag.get("cid"), "renewal_date": renewal_date}
            has_elapsed = bool(renewal_date) and dt.date.fromisoformat(renewal_date) <= today
            if not has_elapsed:
                pending.append({
                    **row_base,
                    "days_to_renewal": flag.get("days_to_renewal"),
                    "proposed_rate_gbp_per_mwh": flag.get("proposed_rate_gbp_per_mwh"),
                })
                continue
            result = _grade_renewal_flag(flag, customers_by_cid, tolerance_pct)
            row = {**row_base, **result}
            if result["graded"]:
                graded.append(row)
            else:
                inconclusive.append(row)
    return graded, pending, inconclusive


def _grade_hedges(log_entries):
    """Grade hedge recommendations once real market data has genuinely advanced since
    the entry was logged. See module docstring track 2."""
    entries_with_stale = [e for e in log_entries if e.get("market_data_stale_days") is not None]
    current_stale_days = entries_with_stale[-1]["market_data_stale_days"] if entries_with_stale else None

    rows = []
    for entry in log_entries:
        stale_at_log_time = entry.get("market_data_stale_days")
        gradeable = (
            current_stale_days is not None
            and stale_at_log_time is not None
            and current_stale_days < stale_at_log_time
        )
        rows.append({
            "decision_run_at": entry.get("decision_run_at", "")[:10],
            "hedge_recommendation": entry.get("hedge_recommendation"),
            "market_data_stale_days_at_log_time": stale_at_log_time,
            "outcome": "ungraded -- market data has not advanced" if not gradeable else "gradeable_but_no_grading_logic_yet",
        })
    graded_count = sum(1 for r in rows if r["outcome"] != "ungraded -- market data has not advanced")
    return {
        "graded_count": graded_count,
        "ungraded_count": len(rows) - graded_count,
        "current_market_data_stale_days": current_stale_days,
        "entries": rows,
    }


def _retention_ev_log(log_entries):
    """No realised-outcome signal exists yet for retention offers -- log only. See
    module docstring track 3."""
    rows = []
    for entry in log_entries:
        run_date = entry.get("decision_run_at", "")[:10]
        for flag in entry.get("renewal_flags", []):
            if flag.get("retention_ev_gbp") is None:
                continue
            rows.append({
                "decision_run_at": run_date,
                "cid": flag.get("cid"),
                "company_churn_estimate": flag.get("company_churn_estimate"),
                "retention_ev_gbp": flag.get("retention_ev_gbp"),
            })
    return {
        "logged_count": len(rows),
        "graded_count": 0,
        "note": (
            "no realized-value join exists yet -- nothing in this codebase records "
            "whether a retention offer was actually made for a flagged renewal, or what "
            "happened after. Entries are logged here for track-record continuity only; "
            "grading them would require building that missing signal first, not "
            "inventing a result now."
        ),
        "entries": rows,
    }


def generate(log_path=None, portfolio_path=None, out_path=None, today=None):
    log_entries = _load_log(log_path)
    customers_by_cid = _load_portfolio(portfolio_path)
    wall_clock_today = today if today is not None else dt.datetime.now(dt.timezone.utc).date()

    clock_started = log_entries[0]["decision_run_at"][:10] if log_entries else None

    graded, pending, inconclusive = _grade_renewals(
        log_entries, customers_by_cid, wall_clock_today, RENEWAL_TOLERANCE_PCT
    )
    on_target = sum(1 for g in graded if g["outcome"] == "renewed_on_target")
    off_target = sum(1 for g in graded if g["outcome"] == "renewed_off_target")
    churned = sum(1 for g in graded if g["outcome"] == "churned")

    hedge = _grade_hedges(log_entries)
    retention = _retention_ev_log(log_entries)

    result = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "wall_clock_today": wall_clock_today.isoformat(),
        "clock_started": clock_started,
        "log_entry_count": len(log_entries),
        "renewal_tolerance_pct": RENEWAL_TOLERANCE_PCT,
        "renewal_grading": {
            "graded_count": len(graded),
            "pending_count": len(pending),
            "inconclusive_count": len(inconclusive),
            "on_target_count": on_target,
            "off_target_count": off_target,
            "churned_count": churned,
            "graded": graded,
            "pending": pending,
            "inconclusive": inconclusive,
        },
        "hedge_grading": hedge,
        "retention_ev_log": retention,
    }

    out = _P(out_path) if out_path else OUT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = generate()
    print("clock_started:", r["clock_started"])
    print("log entries:", r["log_entry_count"])
    rg = r["renewal_grading"]
    print("renewal graded={} pending={} inconclusive={} (on_target={} off_target={} churned={})".format(
        rg["graded_count"], rg["pending_count"], rg["inconclusive_count"],
        rg["on_target_count"], rg["off_target_count"], rg["churned_count"],
    ))
    print("hedge graded={} ungraded={}".format(r["hedge_grading"]["graded_count"], r["hedge_grading"]["ungraded_count"]))
    print("retention EV logged={} graded={}".format(r["retention_ev_log"]["logged_count"], r["retention_ev_log"]["graded_count"]))
