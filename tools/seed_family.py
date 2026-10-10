"""A seed family of no-sample books, one per-home table per seed, and a pooled read-out.

REUSE: tools/seed_family.py
CLASS: CUSTOM
INDEX: searched "seed family" -- nearest tools.selection_residual_decomposition, which decomposes
       one A/B's residual and runs no book. `tools/run_value_cycle_ab.py --book-seeds` is the
       nearest runner: it runs the three-arm A/B per book, strictly serially, at the production
       settlement sample, and keeps book-level scalars, not homes. Reused from it: the churn-roll
       re-draw (`resolve_redraw_target`), the seed preamble's shape and the duplicate-seed
       refusal. From `tools/book_seed_authorisation.py`: the EP17 check. From
       `tools/grade_world_debt_against_ofgem.py`: the unpaid-spell rule, 91 days and `wilson`. From
       `background/launch_long_job.py`: the unit, the record and admission.

WHY (director, 2026-10-09/10): "answer our questions at a statistically significant scale,
quickly". An analysis book settles EVERY campaign win (the sample retired for analysis runs only;
`FOUNDER_BOOK.yaml` and `SETTLEMENT_CUSTOMER_YEAR_BUDGET` are untouched, and the patch lives in the
member's own process). Measured 2026-10-10 at F=40: 482 homes, 35 min, 2.9 GB PSS.

A HOME is a billing account: a household's electricity and gas legs folded into one row
(`saas.customer_reaction._billing_account_id`). A home-move successor (`C1_2`) is a different
premise and its own row. Per home, what each column counts:
  route               founder (in this seed's founder book), home_move_successor (`_N` suffix),
                      change_of_tenancy (`OCC-`), campaign_win (a `PROS-` prospect or a won funnel
                      entry), else arrival (the drawn trickle).
  acquired            the earliest acquisition date on the home's supply points.
  first_settled / tenure_days  the home's first settled day; days from it to its last billed
                      period end.
  still_supplied      not in the run's churned billing accounts.
  net_value_gbp       settled net margin (after capital and the arrears charge) less the world's
                      cost to serve, summed over legs: the annual report's
                      `net_margin_after_cost_to_serve_gbp`, computed here from the run's own rows
                      because the report is a rendering nothing reads (ruling 2026-08-19).
                      REALISED IN-WINDOW, not a lifetime: a home won in 2024 has had one year to
                      earn, so read it beside `tenure_days`.
  bad_debt_gbp        the arrears charge the P&L booked on this home: write-offs (at close and
                      statute-barred) plus any stayer provision, less DCA recovery, as
                      `book_arrears_lines` itemises it. Summed over homes it must equal the
                      settled rows' own `bad_debt_gbp`, or the member is refused.
  provisioned_bad_debt_gbp  the settlement loop's flat provision on the same home, the figure the
                      arrears engine replaced (the `provisioned_bad_debt_gbp` clock).
  max_days_behind / behind_91  the longest a bill of this home stayed unpaid past its due date
                      in the world's payment truth (the live payment triad), and whether that
                      reached 91 days. A failed DD or dispute is unpaid until it settles, if ever
                      (aged to the run's last due date if never); a late payment for its days late.
                      The two debt columns come from two payment models the world keeps: the triad
                      for spells, `arrears_engine` for the P&L charge.

THE SEED IS A BOOK SEED, so any seed but the default is EP17_varied_population_draw, the
director's. The launcher and the member both refuse a foreign seed his record does not list, and
the member refuses a run whose `_RUN_BASE_SEED` is not the seed it was asked for. A foreign book
also re-draws the renewal dice at floor seed == book seed, because `churn_roll_for_renewal` keys
on (id, date) alone and a shared founder id would otherwise roll the same dice in every book.

Usage:
  python3 -m tools.seed_family launch --seeds 20260724 --tag a --out /var/tmp/sf [--parallel 4]
  python3 -m tools.seed_family member --seed S --founders 40 --out DIR      (what a unit runs)
  python3 -m tools.seed_family readout DIR [DIR ...] [--where route=campaign_win]
  python3 -m tools.seed_family same A.csv B.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

DEFAULT_FOUNDERS = 40
#: Unbounded for an analysis book: every campaign win settles. The member checks the campaign
#: reported a sample rate of exactly 1.0, so this is a premise the run proves, not a hope.
ANALYSIS_BUDGET_CUSTOMER_YEARS = 1e9
#: One member's peak, from the 2026-10-10 measurement at F=40 (2.9 GB PSS) with a margin for the
#: captured payment triad. Admission weighs it against everything resident.
MEMBER_PEAK_MB = 3500
MEMBER_EXPECT_MINUTES = 40

COLUMNS = ("home_id", "seed", "segment", "route", "acquired", "first_settled", "tenure_days",
           "still_supplied",
           "net_value_gbp", "bad_debt_gbp", "provisioned_bad_debt_gbp", "max_days_behind",
           "behind_91")

#: Read-out thresholds. The effect sizes are the director's questions (2026-10-10 power note):
#: a 10% move in value per home, a 25% move in either debt measure. Two-sided 5%, 80% power.
CLV_EFFECT = 0.10
DEBT_EFFECT = 0.25
Z_ALPHA = 1.959964
Z_POWER = 0.841621
#: Symmetric trim for the heavy-tailed bad debt. Most homes carry none, so a trim can land at
#: zero; the read-out prints the raw mean beside it and says when that has happened.
TRIM = 0.05
RECONCILE_TOLERANCE_GBP = 1.0


def seed_refusal(seeds: list[int], record: Path | None = None) -> str | None:
    """Why this family may not run, or None. Duplicates first: a book counted twice narrows the
    spread by construction. Then EP17: only the default book seed is free."""
    from tools.book_seed_authorisation import book_seed_authorisation_refusal
    dupes = sorted({s for s in seeds if seeds.count(s) > 1})
    if dupes:
        return ("seed(s) {} appear more than once in one family; a repeated book is the same draw "
                "counted twice. Replicate a seed as a separate --tag instead.".format(dupes))
    return book_seed_authorisation_refusal(seeds, record)


def member_refusal(requested: int, meta: dict) -> str | None:
    """Why this member's table does not measure the book asked for, or None."""
    if meta.get("run_base_seed") != requested:
        return ("seed {}: the run recorded _RUN_BASE_SEED = {!r}. The rebind did not reach the "
                "book, so this table is some other book under this seed's label."
                .format(requested, meta.get("run_base_seed")))
    if meta.get("sample_rate") != 1.0:
        return ("seed {}: the campaign settled at sample rate {!r}, not 1.0, so its homes are a "
                "weighted sample and not every win.".format(requested, meta.get("sample_rate")))
    if meta.get("foreign_seed") and not meta.get("rolls_redrawn"):
        return ("seed {}: a foreign book re-drew 0 renewal rolls, so its shared founder ids rolled "
                "the default book's dice.".format(requested))
    if not meta.get("triad_captured"):
        return ("seed {}: no payment triad was captured, so every home would read 0 days behind."
                .format(requested))
    off = meta.get("bad_debt_reconciliation_gbp")
    if off is None or abs(off) > RECONCILE_TOLERANCE_GBP:
        return ("seed {}: the homes' bad debt sums {!r} GBP away from the settled rows', so the "
                "per-home column is not the P&L's charge.".format(requested, off))
    return None


def _cgroup_peak_mb() -> float | None:
    """This unit's cgroup memory peak: every process the member started, counted by the kernel."""
    try:
        rel = Path("/proc/self/cgroup").read_text().strip().split("::", 1)[1]
        return int(Path("/sys/fs/cgroup" + rel + "/memory.peak").read_text()) / 2**20
    except (OSError, IndexError, ValueError):
        return None


def _route(account: str, founders: set[str], won: set[str]) -> str:
    if account in founders:
        return "founder"
    if re.search(r"_\d+$", account):
        return "home_move_successor"
    if account.startswith("OCC-"):
        return "change_of_tenancy"
    # The funnel log is a capped sample of the campaign, so a won prospect is read off its id too.
    if account in won or account.startswith("PROS-"):
        return "campaign_win"
    return "arrival"


def _day(x):
    from datetime import date
    return x if isinstance(x, date) else date.fromisoformat(str(x)[:10])


def _fold_records(row, records, cost_to_serve: dict) -> dict:
    """Settled net, segment and first settled day per leg, onto homes; cost to serve off the net.
    Returns the run's own bad-debt total, read off the same rows, for the reconciliation."""
    legs: dict[str, dict] = {}
    for rec in records:
        leg = legs.setdefault(rec["customer_id"], {"net": 0.0, "bad_debt": 0.0, "first": None,
                                                   "segment": rec.get("segment")})
        leg["net"] += float(rec.get("net_margin_gbp") or 0.0)
        leg["bad_debt"] += float(rec.get("bad_debt_gbp") or 0.0)
        day = str(rec["settlement_date"])[:10]
        if leg["first"] is None or day < leg["first"]:
            leg["first"] = day
    missing_cts = 0
    for cid, leg in legs.items():
        r = row(cid)
        r["segment"] = r["segment"] or leg["segment"]
        if r["first_settled"] is None or leg["first"] < r["first_settled"]:
            r["first_settled"] = leg["first"]
        cts = (cost_to_serve.get(cid) or {}).get("cost_to_serve_gbp")
        missing_cts += cts is None
        r["net_value_gbp"] += leg["net"] - float(cts or 0.0)
    return {"bad_debt_gbp": sum(leg["bad_debt"] for leg in legs.values()),
            "legs_without_cost_to_serve": missing_cts}


def _fold_debt(row, arrears_lines: dict, payments: list) -> None:
    for cid, ln in arrears_lines.items():
        r = row(cid)
        r["bad_debt_gbp"] += (ln["write_off_at_close_gbp"] + ln["write_off_statute_barred_gbp"]
                              + ln["stayer_provision_gbp"] + ln["line_rounding_gbp"]
                              - ln["unbooked_bad_debt_gbp"]
                              - (ln["dca_recovery_gbp"] - ln["unbooked_recovery_gbp"]))
        r["provisioned_bad_debt_gbp"] += ln["placeholder_bad_debt_released_gbp"]
    # The unpaid-spell rule of `grade_world_debt_against_ofgem.spells_from_records`, kept for
    # every late payment rather than only those past 91 days, so the column is a length.
    run_end = max((_day(p.due_date) for p in payments), default=None)
    for p in payments:
        if p.result in ("failed", "dispute"):
            days = ((_day(p.settled_on) if p.settled_on else run_end) - _day(p.due_date)).days
        elif p.result == "success":
            days = p.days_late or 0
        else:
            continue
        # `customer_id` is the leg; the triad's `account_id` is `ACC-<leg>`, which folds to no home.
        r = row(p.customer_id)
        r["max_days_behind"] = max(r["max_days_behind"], days)


def home_rows(seed: int, run: dict, payments: list, founders: set[str], customers=()
              ) -> tuple[list[dict], dict]:
    """One row per home, and the run-level figures its columns must reconcile to. `run` is the
    run's own output (`run_phase4c_on_phase2b.main`), never the rendered report; `customers` is
    the run's supply points (segment, acquisition date). Pure."""
    from saas.customer_reaction import _billing_account_id as home_of
    from tools.grade_world_debt_against_ofgem import BEHIND_DAYS
    phase2b = run["phase2b"]
    phase2b_ids = {rec["customer_id"] for rec in phase2b["all_records"]}
    homes: dict[str, dict] = {}

    def row(cid: str) -> dict:
        h = home_of(cid)
        return homes.setdefault(h, {"home_id": h, "seed": seed, "segment": None,
                                    "acquired": None, "first_settled": None, "last_billed": None,
                                    "net_value_gbp": 0.0, "bad_debt_gbp": 0.0,
                                    "provisioned_bad_debt_gbp": 0.0, "max_days_behind": 0})

    for c in customers:
        if c.get("customer_id") not in phase2b_ids:
            continue
        r = row(c["customer_id"])
        r["segment"] = r["segment"] or c.get("segment")
        acq = str(c.get("acquisition_date") or "")[:10] or None
        if acq and (r["acquired"] is None or acq < r["acquired"]):
            r["acquired"] = acq
    totals = _fold_records(row, phase2b["all_records"],
                           (run.get("cost_to_serve") or {}).get("by_customer") or {})
    for b in run.get("bills") or []:
        r = row(b["customer_id"])
        if r["last_billed"] is None or b["period_end"] > r["last_billed"]:
            r["last_billed"] = b["period_end"]
    _fold_debt(row, phase2b.get("arrears_lines_by_customer") or {}, payments)
    churned = {str(a) for a in phase2b.get("churned_billing_accounts") or []}
    won = {e.get("billing_account") for e in phase2b.get("acquisition_funnel_log") or []
           if e.get("won")}
    out = []
    for h in sorted(homes):
        r = homes[h]
        last, first = r["last_billed"], r["first_settled"]
        r["route"] = _route(h, founders, won)
        r["tenure_days"] = (_day(last) - _day(first)).days if last and first else None
        r["still_supplied"] = h not in churned
        r["behind_91"] = r["max_days_behind"] >= BEHIND_DAYS
        for k in ("net_value_gbp", "bad_debt_gbp", "provisioned_bad_debt_gbp"):
            r[k] = round(r[k], 4)
        out.append({c: r[c] for c in COLUMNS})
    return out, totals


def write_table(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)


def read_table(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _supply_points() -> list[dict]:
    """Every supply point the run held: its drawn book plus the runtime lists (successors,
    occupants, drawn arrivals, acquisitions), first copy of each id kept."""
    import saas.customers as sc
    import simulation.run_phase2b as runner
    seen, out = set(), []
    for c in (list(runner.CUSTOMERS) + list(runner.SUCCESSOR_CUSTOMERS) + sc.SUCCESSOR_CUSTOMERS
              + sc.DRAWN_CUSTOMERS + sc.INCOMING_OCCUPANT_CUSTOMERS + sc.ACQUIRED_CUSTOMERS):
        cid = c.get("customer_id") if isinstance(c, dict) else getattr(c, "customer_id", None)
        if cid and cid not in seen:
            seen.add(cid)
            out.append(c if isinstance(c, dict) else {
                "customer_id": cid, "segment": getattr(c, "segment", None),
                "acquisition_date": getattr(c, "acquisition_date", None)})
    return out


def member(seed: int, founders: int, out: Path) -> int:
    """ONE book, in this process. Must be the first thing the process does: the seed and the
    founder count are rebound before anything imports `simulation.run_phase2b`, which draws the
    book at import."""
    if "simulation.run_phase2b" in sys.modules:
        raise SystemExit("seed_family member: the book is already drawn in this process")
    refusal = seed_refusal([seed])
    if refusal:
        print("REFUSED:", refusal)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    import simulation.live_population as lp
    import simulation.net_new_acquisition as nna
    default_seed = lp._DEFAULT_BASE_SEED
    lp._DEFAULT_BASE_SEED = seed
    lp.founder_accounts = lambda: founders
    nna.SETTLEMENT_CUSTOMER_YEAR_BUDGET = ANALYSIS_BUDGET_CUSTOMER_YEARS
    founder_ids = {r["customer_id"] for r in lp.founder_book(seed)}

    import background.live_payment_triad as lpt
    triads = []
    real_init = lpt.LivePaymentTriad.__init__

    def _init(self, *a, **k):
        real_init(self, *a, **k)
        triads.append(self)
    lpt.LivePaymentTriad.__init__ = _init

    calls = {"n": 0, "redrawn": 0, "held": 0, "ids": set()}
    foreign = seed != default_seed
    import importlib

    import tools.run_value_cycle_ab as ab
    module_name, name, factory = ab.resolve_redraw_target("churn_roll")
    roll_module = importlib.import_module(module_name)
    real_roll = getattr(roll_module, name)
    if foreign:
        setattr(roll_module, name, factory(real_roll, seed, lambda _a: True, calls))
    try:
        import simulation.run_phase4c_on_phase2b as p4
        run_output = p4.main()
    finally:
        setattr(roll_module, name, real_roll)
        lpt.LivePaymentTriad.__init__ = real_init

    payments = list(triads[-1].records) if triads else []
    try:
        rows, totals = home_rows(seed, run_output, payments, founder_ids, _supply_points())
    except Exception:
        # Thirty-five minutes of book is not lost to a shape error in the table: keep its inputs.
        import pickle
        with open(out / f"inputs_{seed}.pickle", "wb") as fh:
            pickle.dump({"run": run_output, "founders": founder_ids,
                         "payments": [{k: getattr(p, k) for k in p.__slots__} for p in payments]},
                        fh, protocol=5)
        raise
    camp = getattr(lp, "LAST_CAMPAIGN", {}) or {}
    meta = {
        "seed": seed, "run_base_seed": lp._RUN_BASE_SEED, "foreign_seed": foreign,
        "founders": founders, "sample_rate": camp.get("settlement_sample_rate"),
        "rolls_redrawn": calls["redrawn"], "homes": len(rows),
        "triad_captured": bool(triads),
        "bad_debt_reconciliation_gbp": round(sum(r["bad_debt_gbp"] for r in rows)
                                             - totals["bad_debt_gbp"], 4),
        "legs_without_cost_to_serve": totals["legs_without_cost_to_serve"],
        "wall_min": round((time.monotonic() - t0) / 60, 1),
        "peak_cgroup_mb": _cgroup_peak_mb(),
        "ru_maxrss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_DIR,
                                 capture_output=True, text=True).stdout.strip(),
    }
    refusal = member_refusal(seed, meta)
    meta["refused"] = refusal
    (out / f"member_{seed}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    if refusal:
        print("REFUSED:", refusal)
        return 2
    write_table(rows, out / f"homes_{seed}.csv")
    print("MEMBER", json.dumps(meta))
    return 0


def launch(seeds: list[int], founders: int, out: Path, tag: str, parallel: int,
           run_case: dict, launcher=None, record: Path | None = None,
           wait_for_pid: int | None = None) -> list[dict]:
    """Every member as its own long-job unit, all at once; admission decides whether they fit.
    More seeds than `parallel` is refused rather than queued: chaining units on a queued unit's
    pid is refused by the launcher's admission, so the caller launches the next wave itself."""
    refusal = seed_refusal(seeds, record)
    if refusal is None and len(seeds) > parallel:
        refusal = (f"{len(seeds)} seeds over --parallel {parallel}; launch them in waves of "
                   f"{parallel}")
    if refusal:
        raise SystemExit("REFUSED: " + refusal)
    if launcher is None:
        from background.launch_long_job import launch as launcher
    out = out.resolve()
    expect = run_case.pop("expect_minutes", None) or MEMBER_EXPECT_MINUTES
    entries = []
    for s in seeds:
        member_dir = out / tag
        entries.append(launcher(
            f"seed-family-{tag}-{s}",
            [sys.executable, "-m", "tools.seed_family", "member", "--seed", str(s),
             "--founders", str(founders), "--out", str(member_dir)],
            artefact=str(member_dir / f"member_{s}.json"), workdir=str(PROJECT_DIR),
            peak_mb=MEMBER_PEAK_MB, expect_minutes=expect, run_case=run_case,
            wait_for_pid=wait_for_pid))
    return entries


# --- the read-out -------------------------------------------------------------------------------

def _trimmed(xs: list[float], g: float = TRIM) -> tuple[float, float | None]:
    """Trimmed mean and its standard error (Tukey-McLaughlin: winsorised sd over (1-2g) sqrt n)."""
    xs = sorted(xs)
    n = len(xs)
    k = int(math.floor(g * n))
    core = xs[k:n - k] or xs
    mean = statistics.fmean(core)
    if n < 2:
        return mean, None
    wins = [min(max(x, xs[k]), xs[n - 1 - k]) for x in xs]
    return mean, statistics.stdev(wins) / ((1 - 2 * g) * math.sqrt(n))


def n_per_arm_mean(sd: float, delta: float) -> int | None:
    """Homes per arm to detect a difference `delta` in a mean with this sd (two-sided 5%, 80%)."""
    if not delta or sd is None:
        return None
    return math.ceil(2 * ((Z_ALPHA + Z_POWER) * sd / delta) ** 2)


def n_per_arm_share(p: float, rel: float) -> int | None:
    """Homes per arm to detect share p moving to p*(1+rel)."""
    p2 = min(p * (1 + rel), 1.0)
    if p <= 0 or p2 == p:
        return None
    pbar = (p + p2) / 2
    num = Z_ALPHA * math.sqrt(2 * pbar * (1 - pbar)) + Z_POWER * math.sqrt(p * (1 - p) + p2 * (1 - p2))
    return math.ceil((num / (p2 - p)) ** 2)


def _question(name: str, n: int, needed: int | None, estimate: str) -> dict:
    if needed is None:
        verdict = "cannot yet tell: the effect size is undefined at this estimate"
    elif n >= needed:
        verdict = "powered"
    else:
        verdict = f"cannot yet tell: {n} homes per arm of {needed} needed"
    return {"question": name, "estimate": estimate, "homes_per_arm_needed": needed,
            "homes_still_needed": None if needed is None else max(0, needed - n),
            "verdict": verdict}


def readout(rows: list[dict]) -> dict:
    """Pool homes across seeds. Every home is weighted once; homes in one book are not fully
    independent (they share a world), so the per-seed means are printed for the between-book
    check, and a single book says so."""
    from tools.grade_world_debt_against_ofgem import wilson
    n = len(rows)
    seeds = sorted({int(r["seed"]) for r in rows})
    if n < 2:
        return {"homes": n, "seeds": seeds, "verdict": "cannot yet tell: fewer than two homes"}
    value = [float(r["net_value_gbp"]) for r in rows]
    debt = [float(r["bad_debt_gbp"]) for r in rows]
    behind = sum(1 for r in rows if str(r["behind_91"]) in ("True", "true", "1"))
    share = behind / n
    lo, hi = wilson(behind, n)
    v_mean, v_sd = statistics.fmean(value), statistics.stdev(value)
    d_trim, d_se = _trimmed(debt)
    d_wins_sd = d_se * (1 - 2 * TRIM) * math.sqrt(n) if d_se is not None else None
    per_seed = {}
    for s in seeds:
        sub = [r for r in rows if int(r["seed"]) == s]
        per_seed[s] = {"homes": len(sub),
                       "net_value_mean_gbp": round(statistics.fmean(
                           float(r["net_value_gbp"]) for r in sub), 2),
                       "behind_91_share": round(sum(1 for r in sub if str(r["behind_91"])
                                                    in ("True", "true", "1")) / len(sub), 4)}
    questions = [
        _question("net value per home, 10% effect", n,
                  n_per_arm_mean(v_sd, CLV_EFFECT * abs(v_mean)),
                  f"{v_mean:.2f} GBP +/- {1.96 * v_sd / math.sqrt(n):.2f} (95%)"),
        _question("share ever >91 days behind, 25% effect", n, n_per_arm_share(share, DEBT_EFFECT),
                  f"{share:.4f} [{lo:.4f}, {hi:.4f}] (Wilson 95%)"),
        _question("trimmed-mean bad debt per home, 25% effect", n,
                  n_per_arm_mean(d_wins_sd, DEBT_EFFECT * d_trim) if d_trim > 0 else None,
                  f"{d_trim:.2f} GBP +/- {1.96 * (d_se or 0):.2f} (95%, {TRIM:.0%} trim); "
                  f"raw mean {statistics.fmean(debt):.2f}"
                  + ("; the trim removed every non-zero home" if d_trim == 0 and any(debt) else "")),
    ]
    return {"homes": n, "seeds": seeds,
            "one_book": len(seeds) == 1,
            "net_value_mean_gbp": round(v_mean, 2),
            "net_value_se_gbp": round(v_sd / math.sqrt(n), 2),
            "behind_91": {"homes": behind, "share": round(share, 4),
                          "wilson_95": [round(lo, 4), round(hi, 4)]},
            "bad_debt_trimmed_mean_gbp": round(d_trim, 2),
            "bad_debt_trimmed_se_gbp": None if d_se is None else round(d_se, 2),
            "bad_debt_raw_mean_gbp": round(statistics.fmean(debt), 2),
            "per_seed": per_seed, "questions": questions}


def tables_identical(a: list[dict], b: list[dict]) -> list[str]:
    """Where two per-home tables differ, as readable lines; empty when identical."""
    ka, kb = {r["home_id"]: r for r in a}, {r["home_id"]: r for r in b}
    diffs = [f"{h}: only in {'A' if h in ka else 'B'}" for h in sorted(set(ka) ^ set(kb))]
    columns = sorted({c for r in (*a[:1], *b[:1]) for c in r} - {"seed"})
    for h in sorted(set(ka) & set(kb)):
        for c in columns:
            if ka[h].get(c) != kb[h].get(c):
                diffs.append(f"{h}.{c}: {ka[h].get(c)} != {kb[h].get(c)}")
    return diffs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("member")
    m.add_argument("--seed", type=int, required=True)
    m.add_argument("--founders", type=int, default=DEFAULT_FOUNDERS)
    m.add_argument("--out", type=Path, required=True)
    la = sub.add_parser("launch")
    la.add_argument("--seeds", required=True)
    la.add_argument("--founders", type=int, default=DEFAULT_FOUNDERS)
    la.add_argument("--out", type=Path, required=True)
    la.add_argument("--tag", required=True)
    la.add_argument("--parallel", type=int, default=4)
    la.add_argument("--expect-minutes", type=float)
    la.add_argument("--question")
    la.add_argument("--why-not-minutes")
    la.add_argument("--would-change")
    la.add_argument("--wait-for-pid", type=int,
                    help="start when this resident exits, if admission names it (the launcher's)")
    r = sub.add_parser("readout")
    r.add_argument("dirs", nargs="+", type=Path)
    r.add_argument("--where", action="append", default=[], metavar="COLUMN=VALUE")
    s = sub.add_parser("same")
    s.add_argument("a", type=Path)
    s.add_argument("b", type=Path)
    args = ap.parse_args(argv)

    if args.cmd == "member":
        return member(args.seed, args.founders, args.out)
    if args.cmd == "launch":
        seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
        from background.launch_long_job import LaunchRefused
        try:
            launch(seeds, args.founders, args.out, args.tag, args.parallel,
                   {"question": args.question, "why_not_minutes": args.why_not_minutes,
                    "would_change": args.would_change, "expect_minutes": args.expect_minutes},
                   wait_for_pid=args.wait_for_pid)
        except LaunchRefused as exc:
            print("REFUSED:", exc)
            return 2
        return 0
    if args.cmd == "same":
        diffs = tables_identical(read_table(args.a), read_table(args.b))
        print("IDENTICAL" if not diffs else "DIFFERS:\n" + "\n".join(diffs[:40]))
        return 1 if diffs else 0
    rows, refused = [], []
    for d in args.dirs:
        for meta_path in sorted(d.glob("member_*.json")):
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            why = member_refusal(int(meta["seed"]), meta)
            table = d / f"homes_{meta['seed']}.csv"
            if why or not table.exists():
                refused.append(why or f"{table} missing")
                continue
            rows += read_table(table)
    if len({(r["seed"], r["home_id"]) for r in rows}) != len(rows):
        print("REFUSED: one seed's homes appear twice across the directories given")
        return 2
    for cond in args.where:
        col, _, val = cond.partition("=")
        rows = [r for r in rows if r.get(col) == val]
    print(json.dumps({"refused_members": refused, **readout(rows)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
