#!/usr/bin/env python3
"""Measure what `SETTLEMENT_CUSTOMER_YEAR_BUDGET` actually costs, at the shape the live run uses.

WHY THIS EXISTS
---------------
`simulation/net_new_acquisition.py::SETTLEMENT_CUSTOMER_YEAR_BUDGET` is the single constant that
decides how big the published book is allowed to get. Everything downstream that needs decisions to
grade -- B10's ladder, PB4/PB5's heterogeneity models, R6's growth mechanism -- is bounded by it.

WHAT THIS CONSTANT DOES CHANGED ON 2026-08-29 AND THE PARAGRAPH ABOVE USED TO SAY OTHERWISE. It
read: "it currently refuses 335 of the campaign's 380 funnel wins and is the `binding` reason in
nine of the ten published growth years". Both clauses were true when written and both are now
false, so they are struck rather than left for a reader to trust. The ceiling was spent FIRST-COME
on a cohort whose settlement tails cost 9.83 customer-years each, so it emptied inside 2017 and
booked zero in every year after; it now sets a uniform SAMPLE RATE over the campaign's own wins and
`binding` reports what limited the COMPANY. On the record of that day: 505 funnel wins, 92 settled,
a rate of 0.1834, and ten of ten years commercial-bound. Two runs of the same code at the same seed
produced 90/0.1789 and 92/0.1834 -- an OPENING-book difference, not a campaign one, filed open in
the design doc. Read the rate from the record, never from this sentence.
`docs/design/SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md`.

WHAT THAT MEANS FOR THIS PROBE, which still measures the right thing but answers a different
question. Cost still rises with SETTLED CUSTOMER-YEARS and that is still this instrument's x-axis.
What changed is the consequence of getting the ceiling wrong: it used to decide WHICH YEARS EXISTED,
so the number was decisive and a bad one was unrecoverable; it now scales the whole book uniformly,
so a bad one costs precision. Measure it as carefully -- but the urgency this file was written with
is gone, and saying so is more useful than leaving the alarm ringing.

It is an ENGINEERING ceiling: what this box can settle inside a publish cycle. It has no
counterpart in the modelled world, so moving it removes an artefact rather than changing the
curriculum, and it moves the experiment toward being MORE falsifiable (more gradable decisions is
more chances to be refuted), which is the opposite of the usual direction of a dial that makes a
book bigger.

THE PROVENANCE HAD DECAYED, WHICH IS WHY A RE-MEASUREMENT AND NOT AN ARGUMENT
----------------------------------------------------------------------------
Three numbers the current value was set against have all moved since 2026-08-24:

  * the guest's memory (read it, never quote it: `background.resource_headroom.sample()`),
  * the publish cadence (1,500s, not the 1,800s the constant's note reasons against),
  * the run itself -- the note's own design point is "12.4 minutes"; the live producer's last
    five runs took 437-508s.

And the campaign's RUNTIME NOTE still tells every reader of the published book-growth page that
1,200 is "60% of the 465 measured in AO12's scale probe", which the constant's own note has
said is superseded since 2026-08-24. A ceiling justified by a number nobody has re-taken is a
constant chosen because a number was needed.

WHAT IT MEASURES
----------------
For each candidate budget, ONE child process running the live path's own compute --
`tools.run_annual_report._run_and_extract(report_end=None)`, which is exactly what
`background/sim_runner.py` invokes, full window, NOT `--fast` -- and records:

    wall clock (s)      parent-side, monotonic, around the child
    peak RSS (MB)       `os.wait4`'s `ru_maxrss`, which survives a SIGKILL
    customer-years      what the campaign actually COMMITTED at that budget
    wins / refusals     from the campaign's own record

The x-axis is therefore SETTLED CUSTOMER-YEARS and not the budget: a budget above what the funnel
can supply buys nothing, and reporting cost against the budget rather than against what was spent
would show a cost curve flattening for a reason that has nothing to do with cost.

Per-customer-year cost is reported as a MARGINAL slope between adjacent points, never as
total/committed. The run has a large fixed component (build, report, everything that is not
settlement), so an average that divides the whole run by its customer-years attributes the fixed
cost to the variable one and over-states what the next customer-year costs -- which is the
direction that under-sets the ceiling.

WHAT IT DOES NOT MEASURE, said rather than left to be assumed
------------------------------------------------------------
The PUBLISHER's half of the cycle. The budget has to fit `run + publish gate` inside the cadence,
and this probe times the run only. `docs/observability/publish_gate_duration.jsonl` carries the
gate's own duration for the same cycles and the report reads the recent worst case from it rather
than assuming the remainder is free.

SAFETY ON A SHARED BOX
----------------------
This box runs a live producer on a 1,500s cadence. Two full runs at once compete for exactly the
memory being measured, so the probe REFUSES when one is in flight -- reusing
`tools.settlement_footprint_probe.a_run_is_in_flight`, which already fails closed when `pgrep`
cannot be run, and re-checking before EVERY point rather than once at the start.

The child computes but does not persist: no `--save-json`, no report render, no ledger write.
One canonical artefact is written anyway and cannot be suppressed from here --
`docs/observability/book_growth_campaign.json`, written inside `live_population._resolve_campaign`
-- so the parent snapshots it before the first point and restores it after the last. It is READ
in between, because it is where the campaign says what it committed.

USAGE
    python3 -m tools.settlement_ceiling_probe --budgets 1200 2000 2800
    python3 -m tools.settlement_ceiling_probe --run-point 1200 --out FILE   # the child protocol
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

#: The probe's deliverable. The constant's note cites this path as its evidence, the way the
#: 2026-08-24 wall-clock measurement cites `docs/design/SETTLEMENT_CEILING_2026-08-24.md`.
REPORT_PATH = PROJECT / "docs" / "observability" / "settlement_ceiling_probe.json"

#: Written by `live_population._resolve_campaign` on an absolute path, so a probe child clobbers
#: the live one. Snapshotted and restored by the parent.
CAMPAIGN_RECORD = PROJECT / "docs" / "observability" / "book_growth_campaign.json"

#: The publisher's own record of how long its gate took, per cycle, with the cadence it ran
#: against. The probe reads the cadence and the gate cost from here rather than restating either.
PUBLISH_DURATION_LOG = PROJECT / "docs" / "observability" / "publish_gate_duration.jsonl"


# ── The child ────────────────────────────────────────────────────────────────────────────────

def run_point(budget: float, out_path: Path) -> int:
    """IN THE CHILD. Set the ceiling, run the live path's compute, report what it committed.

    THE CAMPAIGN IS READ IN-PROCESS, AND THE FIRST DRAFT READ IT FROM DISK. That draft is the
    reason this paragraph exists, because the failure was silent and read as a result. It parsed
    `docs/observability/book_growth_campaign.json` after the run -- but `_resolve_campaign`
    writes that path on an ABSOLUTE path from every process that assembles a book, and the live
    producer assembles one every ~25 minutes. So the 2,000 point reported `customer_years_
    committed = 1199.9, wins = 45`: not its own campaign at all, but the LIVE producer's, written
    over the top of it mid-run. It read as "the funnel is what bounds this range" -- a coherent,
    publishable, entirely false finding -- while the same point's wall clock and RSS (measured
    parent-side, and therefore uncontaminated) had just DOUBLED, which is what a bigger book
    actually looks like. Two of this run's own fields disagreed and only one of them was wrong.

    Ask who WRITES each side. `LAST_CAMPAIGN` is this process's own campaign and no other writer
    can reach it, so it is the only honest source here. The file is still compared against
    (`campaign_record_agrees`) precisely so a future divergence is REPORTED rather than adopted.
    """
    import simulation.net_new_acquisition as nna

    # Assignable because `plan_growth_campaign` reads the constant AT CALL TIME rather than
    # binding it as a default argument -- a correction made on 2026-08-24 precisely so that the
    # sensitivity of this dial could be measured. Without it every sweep silently measured 279.
    nna.SETTLEMENT_CUSTOMER_YEAR_BUDGET = float(budget)

    import tools.run_annual_report as rar
    from simulation.live_population import LAST_CAMPAIGN
    from tools.settlement_footprint_probe import a_run_is_in_flight

    producer_at_start = a_run_is_in_flight()
    t0 = time.monotonic()
    data = rar._run_and_extract(report_end=None)
    elapsed = time.monotonic() - t0
    producer_at_end = a_run_is_in_flight()

    by_year = LAST_CAMPAIGN.get("by_year", [])
    committed = LAST_CAMPAIGN.get("customer_years_committed")

    # The shared file is compared, never trusted. Equal is reassurance; unequal is the finding
    # that another writer reached this run's artefact, and it is reported rather than resolved.
    on_disk = None
    if CAMPAIGN_RECORD.exists():
        try:
            on_disk = json.loads(CAMPAIGN_RECORD.read_text(encoding="utf-8")).get(
                "customer_years_committed")
        except (OSError, json.JSONDecodeError):
            on_disk = None

    out_path.write_text(json.dumps({
        "budget": float(budget),
        "child_wall_s": elapsed,
        "customer_years_committed": committed,
        "customer_year_budget_seen": LAST_CAMPAIGN.get("customer_year_budget"),
        "wins": sum(r.get("wins", 0) for r in by_year),
        "funnel_wins": sum(r.get("funnel_wins", 0) for r in by_year),
        "wins_refused_by_settlement_budget": sum(
            r.get("wins_refused_by_settlement_budget", 0) for r in by_year
        ),
        "accounts_after_final_year": by_year[-1]["accounts_after"] if by_year else None,
        "settlement_bound_years": [
            r["year"] for r in by_year if r.get("binding") == "settlement_engine"
        ],
        "years_reported": len(data.get("years", [])),
        # CONTAMINATION, recorded by the point that suffered it rather than inferred later. A
        # producer sharing this box competes for exactly the memory and CPU being measured, so a
        # point that overlapped one has an inflated wall clock and is not comparable with one
        # that did not. The guard at the parent only checks BEFORE a point starts; a producer
        # that arrives mid-run is invisible to it, and that is the case that actually happened.
        "producer_in_flight_at_start": producer_at_start,
        "producer_in_flight_at_end": producer_at_end,
        "campaign_record_agrees": (on_disk == committed),
        "campaign_record_on_disk_said": on_disk,
    }, indent=2) + "\n", encoding="utf-8")
    return 0


# ── The parent ───────────────────────────────────────────────────────────────────────────────

def measure(budget: float, scratch: Path) -> dict:
    """Run one point in a child and return wall clock, peak RSS and what it committed."""
    out = scratch / f"point_{int(budget)}.json"
    argv = [sys.executable, "-m", "tools.settlement_ceiling_probe",
            "--run-point", str(budget), "--out", str(out)]
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, cwd=str(PROJECT),
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    # `os.wait4` is the only way to get the child's peak RSS after it has gone, and it survives
    # a kill -- which matters because the failure mode this probe is looking for at the top of
    # the range is an OOM, and an OOMed point that reports how much it was holding when it died
    # is a measurement, not a lost run.
    _, status, usage = os.wait4(proc.pid, 0)
    elapsed = time.monotonic() - t0
    stderr = proc.stderr.read() if proc.stderr else ""
    proc.stderr and proc.stderr.close()

    row: dict = {
        "budget": float(budget),
        "wall_s": round(elapsed, 1),
        "peak_rss_mb": round(usage.ru_maxrss / 1024.0, 1),
        "exit_status": status,
        "ok": status == 0 and out.exists(),
    }
    if out.exists():
        row.update({k: v for k, v in json.loads(out.read_text()).items() if k != "budget"})
    else:
        row["stderr_tail"] = "\n".join(stderr.strip().splitlines()[-12:])
    row.update(cleanliness(row))
    return row


def cleanliness(row: dict) -> dict:
    """Is this point comparable with the others? FAIL-CLOSED on anything it cannot establish.

    A point that shared the box with the live producer measured two jobs, and a point whose
    campaign record was overwritten by another process measured somebody else's book. Either
    makes it unusable for a SLOPE while leaving it perfectly readable as a single observation --
    so the field is `clean`, not `ok`, and both are kept.

    Absent evidence is NOT cleanliness. A point recorded before this check existed carries none
    of these fields, and it is marked unclean with `reason: not recorded` rather than passing by
    default -- the missing-key fail-open is how a control ends up certifying exactly the runs it
    could not see.
    """
    if not row.get("ok"):
        return {"clean": False, "unclean_reasons": ["the point did not complete"]}
    reasons = []
    for key in ("producer_in_flight_at_start", "producer_in_flight_at_end"):
        if key not in row:
            reasons.append(f"{key}: not recorded")
        elif row[key]:
            reasons.append(f"{key}: pid {row[key]} -- competed for the memory being measured")
    if "campaign_record_agrees" not in row:
        reasons.append("campaign_record_agrees: not recorded")
    elif row["campaign_record_agrees"] is False:
        reasons.append(
            f"campaign_record_agrees: False -- another process wrote {CAMPAIGN_RECORD.name} "
            f"during this run (it said {row.get('campaign_record_on_disk_said')!r}), so this "
            f"point's committed customer-years are not its own")
    return {"clean": not reasons, "unclean_reasons": reasons}


def marginal_costs(rows: list[dict]) -> list[dict]:
    """Cost of the NEXT customer-year, between adjacent measured points.

    Never total/committed: the run's fixed cost is large and dividing the whole run by its
    customer-years charges the fixed part to the variable one, which over-states the marginal
    cost and therefore sets the ceiling too low. A pair whose committed customer-years did not
    move is reported as `null` rather than as a division by something near zero -- that pair is
    evidence the FUNNEL ran out, not evidence about cost.
    """
    good = [r for r in rows if r.get("clean") and r.get("customer_years_committed") is not None]
    good.sort(key=lambda r: r["customer_years_committed"])
    out = []
    for lo, hi in zip(good, good[1:]):
        d_cy = hi["customer_years_committed"] - lo["customer_years_committed"]
        row = {
            "from_customer_years": lo["customer_years_committed"],
            "to_customer_years": hi["customer_years_committed"],
            "delta_customer_years": round(d_cy, 1),
        }
        if d_cy < 1.0:
            row["marginal_s_per_customer_year"] = None
            row["marginal_mb_per_customer_year"] = None
            row["note"] = ("committed customer-years did not move between these budgets -- the "
                           "funnel, not the ceiling, is what bounds the higher one")
        else:
            row["marginal_s_per_customer_year"] = round((hi["wall_s"] - lo["wall_s"]) / d_cy, 4)
            row["marginal_mb_per_customer_year"] = round(
                (hi["peak_rss_mb"] - lo["peak_rss_mb"]) / d_cy, 4)
        out.append(row)
    return out


def publisher_context(n: int = 20) -> dict:
    """The cadence and the publisher's own gate cost, from the publisher's record.

    Fails CLOSED and says so: with no record the probe cannot tell how much of the cycle is
    already spoken for, and a ceiling set as if the remainder were free is exactly the
    fail-open shape. `cadence_seconds` is None then, and `recommend` refuses to use a time
    budget at all rather than substituting a plausible one.
    """
    if not PUBLISH_DURATION_LOG.exists():
        return {"available": False, "reason": f"{PUBLISH_DURATION_LOG.name} not present"}
    rows = []
    for line in PUBLISH_DURATION_LOG.read_text(encoding="utf-8").splitlines()[-n:]:
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not rows:
        return {"available": False, "reason": "no parseable rows"}
    cadences = {r.get("cadence_seconds") for r in rows if r.get("cadence_seconds")}
    durations = [r["duration_seconds"] for r in rows if isinstance(r.get("duration_seconds"),
                                                                   (int, float))]
    return {
        "available": True,
        "rows_read": len(rows),
        "cadence_seconds": max(cadences) if cadences else None,
        # The MAX, not the mean. The cycle has to fit its worst recent case, not its typical one.
        "cycle_duration_worst_s": max(durations) if durations else None,
        "cycle_duration_median_s": sorted(durations)[len(durations) // 2] if durations else None,
        "ceiling_seconds_watched": max(
            (r["ceiling_seconds"] for r in rows if r.get("ceiling_seconds")), default=None),
        "note": ("`duration_seconds` here is the PUBLISH CYCLE the watcher timed, which is not "
                 "the same subject as this probe's run-only wall clock. It is reported as "
                 "context for how much of the cadence is already spoken for, and the "
                 "recommendation below charges the difference between the two as overhead "
                 "rather than assuming it is zero."),
    }


def recommend(rows: list[dict], pub: dict, headroom: dict, *, time_share: float,
              rss_share: float, publish_interval_s: float | None = None) -> dict:
    """What ceiling the measurement supports. Refuses rather than guesses.

    Two bounds, and the answer is the SMALLER -- a ceiling that fits the clock but not the
    memory is not a ceiling. Each is stated with the quantity it is derived from so a reader can
    see which one binds, because "which constraint binds" is the whole question the published
    `binding` reason exists to answer.

    THE TWO BOUNDS ARE NOT EQUALLY GOOD, AND SAYING SO IS THE POINT OF THIS DOCSTRING.

    MEMORY is a real, external bound. The guest's size is a fact this process cannot influence,
    so `peak_rss` against it is a constraint in the ordinary sense: exceed it and the kernel
    picks a victim. `oom_kills_total` in the headroom sample is the record of it having done so.

    TIME IS CIRCULAR AS THIS PROJECT CURRENTLY MEASURES IT, and the ceiling's own note walks
    into it. `background/suite_duration_watch.PUBLISH_CADENCE_SECONDS` is not a budget anyone
    chose -- its own comment says so: *"it is a measurement of how often runs actually arrive"*,
    taken as the median inter-arrival of `run_complete_*` markers. Run duration is what sets
    marker inter-arrival. So raising this ceiling makes runs slower, which makes markers arrive
    further apart, which RAISES the measured cadence, which enlarges the allowance a ceiling
    argued "against the cadence" is being checked against. The quantity moves with the answer
    (the same shape as a variance evaluated at the estimate), and it moves in the flattering
    direction: a slower run silences the gate-speed alarm by widening the interval that alarm
    compares against.

    The consequence for THIS function is not that time is ignored -- it is that time cannot be
    read off a measurement. `publish_interval_s` is therefore a CHOSEN publish interval, passed
    in and named, and when nobody passes one the time bound is reported as
    `chosen: false` with the measured cadence used only as a description of today. A reader
    can then see that the memory bound is evidence and the time bound is a preference, which is
    exactly the distinction the circularity above destroys if both are printed as "measured".
    """
    ok = [r for r in rows if r.get("clean")]
    if len(ok) < 2:
        unclean = [{"budget": r.get("budget"), "why": r.get("unclean_reasons")}
                   for r in rows if r.get("ok") and not r.get("clean")]
        return {"decidable": False,
                "reason": (f"{len(ok)} CLEAN point(s); a slope needs at least two. A contaminated "
                           f"point is still a valid single observation and is reported above -- "
                           f"it is only barred from the slope."),
                "unclean_points": unclean}

    marg = [m for m in marginal_costs(rows) if m.get("marginal_s_per_customer_year") is not None]
    if not marg:
        return {"decidable": False,
                "reason": ("no adjacent pair moved the committed customer-years, so the probe "
                           "measured no marginal cost at all -- the funnel bounds this range")}

    # The WORST observed marginal slope, not the mean: setting a ceiling from the friendliest
    # segment is how a probe recommends a value the box cannot actually carry.
    s_per_cy = max(m["marginal_s_per_customer_year"] for m in marg)
    mb_per_cy = max(m["marginal_mb_per_customer_year"] for m in marg)
    base = min(ok, key=lambda r: r["customer_years_committed"])
    base_cy = base["customer_years_committed"]

    out: dict = {
        "decidable": True,
        "worst_marginal_s_per_customer_year": s_per_cy,
        "worst_marginal_mb_per_customer_year": mb_per_cy,
        "measured_from": {"customer_years": base_cy, "wall_s": base["wall_s"],
                          "peak_rss_mb": base["peak_rss_mb"]},
        "bounds": {},
    }

    interval = publish_interval_s if publish_interval_s else pub.get("cadence_seconds")
    if interval:
        # The GATE's cost is charged, never assumed away. `run + gate <= interval` is the cycle,
        # and the gate is measured independently of this probe -- it is the publisher's own
        # record of its own duration, so it is the one part of the cycle neither circular nor
        # estimated. Its WORST recent value, because a cycle has to fit its bad days.
        gate_s = pub.get("cycle_duration_worst_s") or 0.0
        allowed_run_s = interval * time_share - gate_s
        cy_time = base_cy + (allowed_run_s - base["wall_s"]) / s_per_cy
        out["bounds"]["time"] = {
            "chosen": publish_interval_s is not None,
            "publish_interval_s": interval,
            "safety_share_of_the_interval": time_share,
            "measured_gate_worst_s": round(gate_s, 1),
            "allowed_run_s": round(allowed_run_s, 1),
            "customer_years": round(cy_time, 1),
            "circularity": (
                "NOT a measured constraint unless `chosen` is true. The fallback interval is "
                "`suite_duration_watch.PUBLISH_CADENCE_SECONDS`, which is measured FROM run "
                "inter-arrival -- so it grows when this ceiling grows. Read an unchosen time "
                "bound as a description of today, not as a bound."
            ),
        }
    else:
        out["bounds"]["time"] = {"decidable": False, "reason": pub.get("reason", "no cadence")}

    total_mb = headroom.get("total_mb")
    if total_mb:
        allowed_rss = total_mb * rss_share
        cy_rss = base_cy + (allowed_rss - base["peak_rss_mb"]) / mb_per_cy if mb_per_cy > 0 else None
        out["bounds"]["memory"] = {
            "guest_total_mb": total_mb,
            "guest_available_mb": headroom.get("available_mb"),
            "share_of_guest_the_run_may_hold": rss_share,
            "allowed_peak_rss_mb": round(allowed_rss, 1),
            "customer_years": round(cy_rss, 1) if cy_rss is not None else None,
            "note": ("share is of TOTAL, not AVAILABLE: the run has to fit beside daemons that "
                     "come and go, and sizing to a momentary `available_mb` sets a ceiling that "
                     "was true for one second."),
        }
    else:
        out["bounds"]["memory"] = {"decidable": False, "reason": "no total_mb from resource_headroom"}

    candidates = [b["customer_years"] for b in out["bounds"].values()
                  if isinstance(b, dict) and isinstance(b.get("customer_years"), (int, float))]
    if candidates:
        out["supported_customer_years"] = round(min(candidates), 1)
        out["binding_bound"] = min(
            (k for k, v in out["bounds"].items()
             if isinstance(v.get("customer_years"), (int, float))),
            key=lambda k: out["bounds"][k]["customer_years"])
        # WHETHER THE BINDING BOUND IS EVIDENCE OR A PREFERENCE, stated as a field rather than
        # left to whoever reads the JSON. A ceiling bound by memory is bound by the box; a
        # ceiling bound by an UNCHOSEN publish interval is bound by a number that will move
        # the moment the ceiling does, and a reader who cannot tell those apart will quote the
        # second as if it were the first.
        out["binding_bound_is_evidence"] = (
            out["binding_bound"] == "memory"
            or bool(out["bounds"].get("time", {}).get("chosen"))
        )
    else:
        out["decidable"] = False
        out["reason"] = "neither bound could be computed"

    # What the funnel can actually supply. A ceiling above this is inert -- worth SAYING,
    # because a ceiling raised past the supply reads on the page like a bigger book and is not.
    demanded = [r["customer_years_committed"] + 0.0 for r in ok
                if r.get("wins_refused_by_settlement_budget") == 0]
    if demanded:
        out["funnel_supply_customer_years"] = max(demanded)
        out["note_supply"] = ("at least one measured point refused nothing, so the campaign's own "
                              "demand is bounded here and a ceiling above it buys no accounts")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budgets", type=float, nargs="+", default=[1200.0, 2000.0, 2800.0],
                    help="customer-year budgets to measure (default: 1200 2000 2800)")
    ap.add_argument("--time-share", type=float, default=0.5,
                    help="share of the publish cadence the RUN may take (default: 0.5)")
    ap.add_argument("--rss-share", type=float, default=0.25,
                    help="share of the guest's TOTAL memory the run may hold (default: 0.25)")
    ap.add_argument("--json", type=Path, default=REPORT_PATH)
    ap.add_argument("--force", action="store_true",
                    help="measure even with a producer run in flight (it will compete)")
    ap.add_argument("--publish-interval", type=float, default=None,
                    help="CHOSEN publish interval in seconds for the time bound. Omit and the "
                         "time bound falls back to the MEASURED cadence, which is circular "
                         "(see `recommend`) and is reported as `chosen: false`.")
    ap.add_argument("--reanalyse", type=Path, default=None,
                    help="recompute the marginals and the recommendation from an existing "
                         "report's measured points, without re-running anything. For when the "
                         "ANALYSIS was wrong and the measurement was not -- re-running three "
                         "full-window runs to fix a division is how a measurement gets "
                         "quietly rounded instead of recomputed.")
    ap.add_argument("--run-point", type=float, help="CHILD PROTOCOL: measure one budget")
    ap.add_argument("--out", type=Path, help="CHILD PROTOCOL: where the child writes its row")
    args = ap.parse_args()

    if args.run_point is not None:
        if args.out is None:
            ap.error("--run-point requires --out")
        return run_point(args.run_point, args.out)

    from background.resource_headroom import sample
    from tools.settlement_footprint_probe import a_run_is_in_flight

    if args.reanalyse is not None:
        prior = json.loads(args.reanalyse.read_text(encoding="utf-8"))
        rows = prior["points"]
        # RE-JUDGED, not carried over. Cleanliness is derived from the point's recorded fields,
        # so a report written before the check existed -- or annotated afterwards from evidence
        # outside it -- gets the verdict its fields now support rather than the one it shipped.
        for r in rows:
            r.update(cleanliness(r))
        pub = publisher_context()
        prior["marginal"] = marginal_costs(rows)
        prior["publisher"] = pub
        prior["recommendation"] = recommend(
            rows, pub, prior.get("headroom_before") or sample(),
            time_share=args.time_share, rss_share=args.rss_share,
            publish_interval_s=args.publish_interval)
        prior["reanalysed_at_utc"] = datetime.now(timezone.utc).isoformat()
        args.json.write_text(json.dumps(prior, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(prior["recommendation"], indent=2))
        return 0

    scratch = Path.home() / ".cache" / "synthetic-enterprise" / "settlement_ceiling_probe"
    scratch.mkdir(parents=True, exist_ok=True)
    snapshot = scratch / "book_growth_campaign.live.json"
    if CAMPAIGN_RECORD.exists():
        shutil.copy2(CAMPAIGN_RECORD, snapshot)

    headroom_before = sample()
    rows: list[dict] = []
    try:
        for budget in args.budgets:
            in_flight = a_run_is_in_flight()
            if in_flight and not args.force:
                rows.append({"budget": float(budget), "ok": False,
                             "skipped": f"producer run in flight (pid {in_flight})"})
                print(f"[skip] budget {budget}: producer in flight (pid {in_flight})", flush=True)
                continue
            print(f"[run ] budget {budget} ...", flush=True)
            row = measure(budget, scratch)
            rows.append(row)
            print(f"[done] budget {budget}: {row.get('wall_s')}s  {row.get('peak_rss_mb')}MB  "
                  f"cy={row.get('customer_years_committed')}  wins={row.get('wins')}  "
                  f"refused={row.get('wins_refused_by_settlement_budget')}", flush=True)
    finally:
        if snapshot.exists():
            shutil.copy2(snapshot, CAMPAIGN_RECORD)

    headroom_after = sample()
    report = {
        "artefact": "settlement_ceiling_probe",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "subject": ("simulation/net_new_acquisition.py::SETTLEMENT_CUSTOMER_YEAR_BUDGET, measured "
                    "on the live path's own compute (tools.run_annual_report._run_and_extract, "
                    "full window, not --fast) -- the same call background/sim_runner.py makes"),
        "git_head": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT),
                                   capture_output=True, text=True).stdout.strip(),
        "headroom_before": headroom_before,
        "headroom_after": headroom_after,
        "points": rows,
        "marginal": marginal_costs(rows),
        "publisher": publisher_context(),
        "recommendation": recommend(rows, publisher_context(), headroom_before,
                                    time_share=args.time_share, rss_share=args.rss_share,
                                    publish_interval_s=args.publish_interval),
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {args.json}")
    print(json.dumps(report["recommendation"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
