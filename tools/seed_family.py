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
  household_saving_gbp  what the home's settled kWh would have cost on the published default
                      tariff less what we billed, summed over legs and calendar years
                      (`build_household_value_share`, the M4 measure; a day with no published
                      rate drops out of both sides, as the view does). None where any of the
                      home's leg-years had no rate at all, or none was valued: a partial sum or a
                      zero would read as the whole home's saving.
  kwh_elec / kwh_gas  settled kWh per fuel, summed over the home's legs (M6's input).
  has_gas_leg         the home settled any gas.
  company_vulnerability_flag  the home is on the company's own Priority Services Register, built
                      only from disclosures that crossed the seam. Who we flagged, not who is
                      vulnerable: the world has no vulnerability truth to grade it against. None
                      where the run carried no register (the hidden-state switch was off).

THE POLICY (B11, 2026-10-16). `--policy` runs every member under one named company policy, entered
with `policy_scope(...)` AND passed as `policy=`, as `run_value_cycle_ab` does, so the run loop's
chimera refusal holds. Default `current`, so every existing family is unchanged. The name is
stamped in each member's record and `readout` refuses to pool members run under different ones; a
record from before the stamp existed was run under `current`, the only policy a member could take.

THE LEVEL ARM (B11 prereg arm three, item 4 of the flat-supplier finding). `--policy flat_at_level
--level-from DIR` runs `FLAT_SUPPLIER_POLICY` renewing every account at ONE margin: the median the
value arm chose on the SAME seed, read from DIR's `member_<seed>.json`. It is a second pass because
that level does not exist until the value-arm member has chosen; the median is
`run_value_cycle_ab.arm_decision_shape`'s, the figure that runner's `--level-arm` holds. Every member
stamps that median (None where it priced no value-arm renewal), so any value-arm member can feed
one. The level member refuses before running where the source is missing, refused, not a value-arm
member, another seed, another commit, or carries no median: a level arm at a number this book did
not produce separates nothing.

THE SEED IS A BOOK SEED, so any seed but the default is EP17_varied_population_draw, the
director's. The launcher and the member both refuse a foreign seed his record does not list, and
the member refuses a run whose `_RUN_BASE_SEED` is not the seed it was asked for. A foreign book
also re-draws the renewal dice at floor seed == book seed, because `churn_roll_for_renewal` keys
on (id, date) alone and a shared founder id would otherwise roll the same dice in every book.

Usage:
  python3 -m tools.seed_family launch --seeds 20260724 --tag a --out /var/tmp/sf [--parallel 4]
  python3 -m tools.seed_family member --seed S --founders 40 --out DIR [--policy flat_supplier]
  python3 -m tools.seed_family member --seed S --out DIR2 --policy flat_at_level --level-from DIR
  python3 -m tools.seed_family readout DIR [DIR ...] [--where route=campaign_win] [--mix M.json]
  python3 -m tools.seed_family mix REPORT.json --source "..." --out M.json [--wins-scale 2.75]
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
#: THE TWO BOOK SHAPES (director, 2026-10-10 and 2026-10-11). `all_wins`: 40 founders and every
#: campaign win settled -- mostly selected new shoppers. `founders_only`: the production founder
#: book (400) with NO win settled, for back-book questions. How no win is settled: the budget is
#: 0 customer-years, so the campaign's headroom (`budget - committed`, floored at 0 in
#: `net_new_acquisition.settle_within_budget`) is 0 and its sample rate is 0. The founders are not
#: charged against that headroom's floor, so they all settle. The campaign still RUNS -- it
#: quotes, wins and spends exactly as in production -- and the member refuses a run whose
#: campaign booked any win or whose table holds a campaign-win home.
SHAPES = {"all_wins": {"founders": DEFAULT_FOUNDERS, "budget": ANALYSIS_BUDGET_CUSTOMER_YEARS},
          "founders_only": {"founders": 400, "budget": 0.0}}
#: One member's peak, from the 2026-10-10 measurement at F=40 (2.9 GB PSS) with a margin for the
#: captured payment triad. Admission weighs it against everything resident.
MEMBER_PEAK_MB = 3500
MEMBER_EXPECT_MINUTES = 40

COLUMNS = ("home_id", "seed", "segment", "route", "acquired", "first_settled", "tenure_days",
           "still_supplied",
           "net_value_gbp", "bad_debt_gbp", "provisioned_bad_debt_gbp", "max_days_behind",
           "behind_91", "household_saving_gbp", "kwh_elec", "kwh_gas", "has_gas_leg",
           "company_vulnerability_flag")

#: The policies a member may run under, by the name it is stamped with.
POLICY_NAMES = {"current": "CURRENT_POLICY", "value_arm": "VALUE_ARM_POLICY",
                "flat_supplier": "FLAT_SUPPLIER_POLICY"}
#: What a member record from before the policy stamp ran under.
UNSTAMPED_POLICY = "current"
#: The second-pass arm: built per member, at a level read from that seed's value-arm member.
LEVEL_POLICY = "flat_at_level"
MEMBER_POLICIES = sorted([*POLICY_NAMES, LEVEL_POLICY])


def policy_named(name: str, level: float | None = None):
    from company.policy import decision_policy
    if name == LEVEL_POLICY:
        from dataclasses import replace

        from company.pricing.value_based_renewal import FLAT_AT_LEVEL
        if level is None:
            raise SystemExit("seed_family: --policy flat_at_level needs the level its value-arm "
                             "member chose (--level-from)")
        return replace(decision_policy.FLAT_SUPPLIER_POLICY, name=LEVEL_POLICY,
                       renewal_margin_arm=FLAT_AT_LEVEL,
                       renewal_margin_flat_level_gbp_per_mwh=float(level))
    policy = getattr(decision_policy, POLICY_NAMES[name])
    if policy.name != name:
        raise SystemExit(f"seed_family: --policy {name} resolved to a policy named {policy.name!r}")
    return policy


def mixed_policy_refusal(metas: list[dict]) -> str | None:
    """Why these members cannot be pooled into one read-out, or None."""
    by_policy: dict[str, list] = {}
    for meta in metas:
        by_policy.setdefault(meta.get("policy", UNSTAMPED_POLICY), []).append(meta.get("seed"))
    if len(by_policy) <= 1:
        return None
    return ("members ran under {} policies ({}); pooling them would read one arm's homes as "
            "another's. Read each policy's directories apart."
            .format(len(by_policy), "; ".join(f"{p}: seeds {sorted(s)}"
                                               for p, s in sorted(by_policy.items()))))

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


def level_source_refusal(seed: int, source: Path | None, commit: str) -> str | None:
    """Why the value-arm member record at `source` cannot set seed `seed`'s level, or None."""
    if source is None:
        return f"seed {seed}: no --level-from directory, so there is no level to hold"
    path = source / f"member_{seed}.json"
    if not path.exists():
        return f"seed {seed}: {path} does not exist; run the value_arm member of this seed first"
    meta = json.loads(path.read_text(encoding="utf-8"))
    if meta.get("refused"):
        return f"seed {seed}: the value-arm member was refused ({meta['refused']})"
    if meta.get("policy", UNSTAMPED_POLICY) != "value_arm":
        return (f"seed {seed}: {path} ran under {meta.get('policy', UNSTAMPED_POLICY)!r}, not "
                "value_arm, so its median is not the per-customer arm's level")
    if meta.get("seed") != seed:
        return f"seed {seed}: {path} records seed {meta.get('seed')!r}"
    if meta.get("commit") != commit:
        return (f"seed {seed}: the value-arm member ran at {meta.get('commit')!r} and this one "
                f"would run at {commit!r}; a level from other code is not this book's")
    if meta.get("value_arm_median_margin_gbp_per_mwh") is None:
        return (f"seed {seed}: the value-arm member priced no renewal with the value arm, so it "
                "chose no level")
    return None


def level_stamp(run_output: dict, level: float | None, level_from: Path | None) -> dict:
    """What a member records about renewal levels: the median its value arm chose (what a level
    member reads) and, on a level member, the level it held and where that came from."""
    from tools.run_value_cycle_ab import arm_decision_shape
    shape = arm_decision_shape(run_output)
    return {"value_arm_median_margin_gbp_per_mwh": shape.get("median_margin_gbp_per_mwh"),
            "value_arm_priced": shape.get("priced", 0),
            "value_arm_declined": shape.get("declined", 0),
            "flat_level_gbp_per_mwh": level,
            "level_from": str(level_from) if level is not None else None}


def _level_of(seed: int, source: Path) -> float:
    meta = json.loads((source / f"member_{seed}.json").read_text(encoding="utf-8"))
    return float(meta["value_arm_median_margin_gbp_per_mwh"])


def _head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_DIR,
                          capture_output=True, text=True).stdout.strip()


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
    if meta.get("shape", "all_wins") == "founders_only":
        if meta.get("wins_settled") != 0 or meta.get("campaign_win_homes") != 0:
            return ("seed {}: a founders-only book settled {!r} campaign win(s) and its table "
                    "holds {!r} campaign-win home(s); it is not a back book."
                    .format(requested, meta.get("wins_settled"), meta.get("campaign_win_homes")))
    elif meta.get("sample_rate") != 1.0:
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
                                                   "segment": rec.get("segment"),
                                                   "kwh_elec": 0.0, "kwh_gas": 0.0, "gas": False})
        leg["net"] += float(rec.get("net_margin_gbp") or 0.0)
        # The fuel rule `build_household_value_share` reads: a record naming no fuel is
        # electricity, and one naming an unknown fuel is not guessed at.
        fuel = rec["commodity"] if "commodity" in rec else "electricity"
        if fuel not in ("electricity", "gas"):
            raise ValueError(f"{rec['customer_id']} settled a record of fuel {fuel!r}")
        leg["kwh_gas" if fuel == "gas" else "kwh_elec"] += float(rec.get("consumption_kwh") or 0.0)
        leg["gas"] = leg["gas"] or fuel == "gas"
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
        r["kwh_elec"] += leg["kwh_elec"]
        r["kwh_gas"] += leg["kwh_gas"]
        r["has_gas_leg"] = r["has_gas_leg"] or leg["gas"]
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


def _fold_saving(row, records, svt_rate_for) -> None:
    """The household's saving against the published default, per home (M4). A home with a
    leg-year the view could not value, or with none it valued at all, reads None: a partial sum
    or a zero would each read as the whole home's saving."""
    from company.analytics.household_value_share import build_household_value_share
    view = build_household_value_share(records, svt_rate_for=svt_rate_for)
    for (cid, _year), v in view.by_customer_period.items():
        r = row(cid)
        if v.household_saving_gbp is None:
            r["saving_blind"] = True
        else:
            r["household_saving_gbp"] = (r["household_saving_gbp"] or 0.0) + v.household_saving_gbp


def home_rows(seed: int, run: dict, payments: list, founders: set[str], customers=(),
              svt_rate_for=None) -> tuple[list[dict], dict]:
    """One row per home, and the run-level figures its columns must reconcile to. `run` is the
    run's own output (`run_phase4c_on_phase2b.main`), never the rendered report; `customers` is
    the run's supply points (segment, acquisition date); `svt_rate_for` the published default
    tariff by (date, fuel), `run_price_ladder.published_default_tariff` unless given. Pure."""
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
                                    "provisioned_bad_debt_gbp": 0.0, "max_days_behind": 0,
                                    "household_saving_gbp": None, "saving_blind": False,
                                    "kwh_elec": 0.0,
                                    "kwh_gas": 0.0, "has_gas_leg": False})

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
    if svt_rate_for is None:
        from tools.run_price_ladder import published_default_tariff as svt_rate_for
    _fold_saving(row, phase2b["all_records"], svt_rate_for)
    registered = phase2b.get("psr_registrations")
    flagged = (None if registered is None
               else {home_of(str(reg["account_id"])) for reg in registered})
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
        r["company_vulnerability_flag"] = None if flagged is None else h in flagged
        if r["saving_blind"]:
            r["household_saving_gbp"] = None
        for k in ("net_value_gbp", "bad_debt_gbp", "provisioned_bad_debt_gbp",
                  "household_saving_gbp", "kwh_elec", "kwh_gas"):
            if r[k] is not None:
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


def run_book(policy) -> dict:
    """The run, under `policy`: entered as the active policy AND passed, so the collections seam
    (which reads the active one) and the run loop (which is handed one) agree."""
    import simulation.run_phase4c_on_phase2b as p4
    from company.policy.decision_policy import policy_scope
    with policy_scope(policy):
        return p4.main(policy=policy)


def member(seed: int, founders: int, out: Path, shape: str = "all_wins",
           policy: str = "current", level_from: Path | None = None) -> int:
    """ONE book, in this process. Must be the first thing the process does: the seed and the
    founder count are rebound before anything imports `simulation.run_phase2b`, which draws the
    book at import."""
    if "simulation.run_phase2b" in sys.modules:
        raise SystemExit("seed_family member: the book is already drawn in this process")
    refusal = seed_refusal([seed])
    level = None
    if refusal is None and policy == LEVEL_POLICY:
        refusal = level_source_refusal(seed, level_from, _head())
        if refusal is None:
            level = _level_of(seed, level_from)
    if refusal:
        print("REFUSED:", refusal)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    run_policy = policy_named(policy, level)
    import simulation.live_population as lp
    import simulation.net_new_acquisition as nna
    default_seed = lp._DEFAULT_BASE_SEED
    lp._DEFAULT_BASE_SEED = seed
    lp.founder_accounts = lambda: founders
    nna.SETTLEMENT_CUSTOMER_YEAR_BUDGET = SHAPES[shape]["budget"]
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
        run_output = run_book(run_policy)
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
        "shape": shape, "budget_customer_years": SHAPES[shape]["budget"],
        "policy": run_policy.name,
        "retention_offers": len(run_output["phase2b"].get("retention_log") or []),
        **level_stamp(run_output, level, level_from),
        "wins_settled": sum(int(r.get("wins") or 0) for r in camp.get("by_year") or []),
        "funnel_wins": camp.get("funnel_wins"),
        "campaign_win_homes": sum(1 for r in rows if r["route"] == "campaign_win"),
        "rolls_redrawn": calls["redrawn"], "homes": len(rows),
        "triad_captured": bool(triads),
        "bad_debt_reconciliation_gbp": round(sum(r["bad_debt_gbp"] for r in rows)
                                             - totals["bad_debt_gbp"], 4),
        "legs_without_cost_to_serve": totals["legs_without_cost_to_serve"],
        "wall_min": round((time.monotonic() - t0) / 60, 1),
        "peak_cgroup_mb": _cgroup_peak_mb(),
        "ru_maxrss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
        "commit": _head(),
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
           wait_for_pid: int | None = None, sleep=None, queue_deadline_s: float = 6 * 3600,
           shape: str = "all_wins", peak_mb: float = MEMBER_PEAK_MB,
           policy: str = "current", level_from: Path | None = None) -> list[dict]:
    """Every member as its own long-job unit, all at once; admission decides whether they fit.
    More seeds than `parallel` is refused rather than queued: chaining units on a queued unit's
    pid is refused by the launcher's admission, so the caller launches the next wave itself.
    A member the box has no room for yet QUEUES at the launcher's own retry cadence rather than
    refusing: a refusal mid-family left the members already started with nothing following them
    (2026-10-10, 61103 refused behind another lane's 7 GB run)."""
    refusal = seed_refusal(seeds, record)
    if refusal is None and len(seeds) > parallel:
        refusal = (f"{len(seeds)} seeds over --parallel {parallel}; launch them in waves of "
                   f"{parallel}")
    if refusal is None and policy == LEVEL_POLICY:
        # Every seed's source is read before any unit starts: a family half-launched behind one
        # missing value-arm member is the stranded wave the queueing below exists to prevent.
        head = _head()
        refusal = next(filter(None, (level_source_refusal(s, level_from, head) for s in seeds)),
                       None)
    if refusal:
        raise SystemExit("REFUSED: " + refusal)
    level_argv = ["--level-from", str(level_from.resolve())] if policy == LEVEL_POLICY else []
    from background.launch_long_job import QUEUE_RETRY_SECONDS, NoRoom
    if launcher is None:
        from background.launch_long_job import launch as launcher
    if sleep is None:
        sleep = time.sleep
    out = out.resolve()
    expect = run_case.pop("expect_minutes", None) or MEMBER_EXPECT_MINUTES
    entries = []
    for s in seeds:
        member_dir = out / tag
        waited = 0.0
        while True:
            try:
                entries.append(launcher(
                    f"seed-family-{tag}-{s}",
                    [sys.executable, "-m", "tools.seed_family", "member", "--seed", str(s),
                     "--founders", str(founders), "--out", str(member_dir), "--shape", shape,
                     "--policy", policy, *level_argv],
                    artefact=str(member_dir / f"member_{s}.json"), workdir=str(PROJECT_DIR),
                    peak_mb=peak_mb, expect_minutes=expect, run_case=dict(run_case),
                    wait_for_pid=wait_for_pid))
                break
            except NoRoom as exc:
                if waited >= queue_deadline_s:
                    raise
                print(f"QUEUED seed {s} (no room yet): {exc}", flush=True)
                sleep(QUEUE_RETRY_SECONDS)
                waited += QUEUE_RETRY_SECONDS
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


#: Every home's origin, in the order the read-out prints them (`_route`).
ORIGINS = ("founder", "campaign_win", "change_of_tenancy", "home_move_successor", "arrival")


def _behind(r: dict) -> bool:
    return str(r["behind_91"]) in ("True", "true", "1")


def _estimate(rows: list[dict]) -> dict:
    """The three quantities on one population, each with its interval and the homes per arm a
    question about it needs. Under two homes, nothing is estimated and the bound is said."""
    from tools.grade_world_debt_against_ofgem import wilson
    n = len(rows)
    if n < 2:
        return {"homes": n, "verdict": f"cannot yet tell: {n} home(s), no interval exists"}
    value = [float(r["net_value_gbp"]) for r in rows]
    debt = [float(r["bad_debt_gbp"]) for r in rows]
    behind = sum(1 for r in rows if _behind(r))
    share = behind / n
    lo, hi = wilson(behind, n)
    v_mean, v_sd = statistics.fmean(value), statistics.stdev(value)
    d_trim, d_se = _trimmed(debt)
    d_wins_sd = d_se * (1 - 2 * TRIM) * math.sqrt(n) if d_se is not None else None
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
    return {"homes": n,
            "net_value_mean_gbp": round(v_mean, 2),
            "net_value_se_gbp": round(v_sd / math.sqrt(n), 2),
            "behind_91": {"homes": behind, "share": round(share, 4),
                          "wilson_95": [round(lo, 4), round(hi, 4)],
                          "se": round(math.sqrt(share * (1 - share) / n), 4)},
            "bad_debt_trimmed_mean_gbp": round(d_trim, 2),
            "bad_debt_trimmed_se_gbp": None if d_se is None else round(d_se, 2),
            "bad_debt_raw_mean_gbp": round(statistics.fmean(debt), 2),
            "questions": questions}


_MIXED = (("net value per home", "net_value_mean_gbp", "net_value_se_gbp"),
          ("share ever >91 days behind", ("behind_91", "share"), ("behind_91", "se")),
          ("trimmed-mean bad debt per home", "bad_debt_trimmed_mean_gbp",
           "bad_debt_trimmed_se_gbp"))


def _get(d: dict, key):
    return d[key[0]][key[1]] if isinstance(key, tuple) else d.get(key)


def mix_check(pooled: dict, by_origin: dict, mix: dict) -> dict:
    """Would the pooled answer change if the book's origins were in `mix`'s shares? Each group's
    estimate is re-weighted to the mix. It CHANGES when the re-weighted figure falls outside the
    pooled 95% interval; it cannot be told when a group the mix weights has no estimate here."""
    shares = {g: float(s) for g, s in mix["shares"].items() if float(s) > 0}
    missing = sorted(g for g in shares if "questions" not in by_origin.get(g, {}))
    out = {"mix_source": mix.get("source"), "shares": shares, "quantities": []}
    for name, key, se_key in _MIXED:
        if missing:
            out["quantities"].append({"quantity": name, "verdict": (
                "cannot yet tell: the mix weights group(s) {} this family cannot estimate"
                .format(missing))})
            continue
        total = sum(shares.values())
        est = sum(s * _get(by_origin[g], key) for g, s in shares.items()) / total
        se = math.sqrt(sum((s / total * (_get(by_origin[g], se_key) or 0.0)) ** 2
                           for g, s in shares.items()))
        p, p_se = _get(pooled, key), _get(pooled, se_key) or 0.0
        lo, hi = p - 1.96 * p_se, p + 1.96 * p_se
        out["quantities"].append({
            "quantity": name, "pooled": p, "pooled_95": [round(lo, 4), round(hi, 4)],
            "at_mix": round(est, 4), "at_mix_se": round(se, 4),
            "verdict": ("CHANGES: the mix moves it outside the pooled interval"
                        if not lo <= est <= hi else "does not change it")})
    return out


def mix_of_report(report: dict, founders: set[str], wins_scale: float = 1.0) -> dict:
    """The origin shares of a run's SETTLED homes (`per_customer_lifetime`). `wins_scale` is
    1/sample rate when that book settled a weighted sample of its wins: it turns the settled
    wins back into the wins the company made."""
    from saas.customer_reaction import _billing_account_id as home_of
    won = {e.get("billing_account") for e in report.get("acquisition_funnel_log") or []
           if e.get("won")}
    homes = {home_of(c) for c in report.get("per_customer_lifetime") or {}}
    founder_homes = {home_of(c) for c in founders}
    counts: dict[str, float] = {}
    for h in homes:
        g = _route(h, founder_homes, won)
        counts[g] = counts.get(g, 0.0) + (wins_scale if g == "campaign_win" else 1.0)
    total = sum(counts.values())
    return {"shares": {g: round(c / total, 4) for g, c in counts.items()},
            "homes": len(homes), "wins_scale": wins_scale}


def readout(rows: list[dict], mixes: list[dict] | None = None) -> dict:
    """Pool homes across seeds, then the same read-out per origin (director's condition 1, 2026-10-10:
    a 40-founder book is mostly selected new shoppers, not a mature back book), and whether each
    pooled answer survives re-weighting to another book's origin mix. Homes in one book share a
    world, so the per-seed figures are printed for the between-book check."""
    seeds = sorted({int(r["seed"]) for r in rows})
    pooled = _estimate(rows)
    by_origin = {g: _estimate([r for r in rows if r["route"] == g]) for g in ORIGINS}
    per_seed = {s: {k: v for k, v in _estimate([r for r in rows if int(r["seed"]) == s]).items()
                    if k in ("homes", "net_value_mean_gbp", "behind_91")} for s in seeds}
    out = {"seeds": seeds, "one_book": len(seeds) == 1, **pooled,
           "by_origin": by_origin, "per_seed": per_seed}
    if "questions" in pooled:
        out["mix_checks"] = [mix_check(pooled, by_origin, m) for m in mixes or []]
    return out


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
    m.add_argument("--founders", type=int, help="default: the shape's own")
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--shape", choices=sorted(SHAPES), default="all_wins")
    m.add_argument("--policy", choices=MEMBER_POLICIES, default="current")
    m.add_argument("--level-from", type=Path,
                   help="flat_at_level only: the directory holding this seed's value_arm member")
    la = sub.add_parser("launch")
    la.add_argument("--seeds", required=True)
    la.add_argument("--founders", type=int, help="default: the shape's own")
    la.add_argument("--shape", choices=sorted(SHAPES), default="all_wins")
    la.add_argument("--policy", choices=MEMBER_POLICIES, default="current")
    la.add_argument("--level-from", type=Path)
    la.add_argument("--peak-mb", type=float, default=MEMBER_PEAK_MB,
                    help="one member's declared peak, from its own last run")
    la.add_argument("--out", type=Path, required=True)
    la.add_argument("--tag", required=True)
    la.add_argument("--parallel", type=int, default=4)
    la.add_argument("--expect-minutes", type=float)
    la.add_argument("--question")
    la.add_argument("--why-not-minutes")
    la.add_argument("--would-change")
    la.add_argument("--detach", action="store_true",
                    help="return once the units are scheduled. The default follows every member "
                         "to its end, so whoever ran this is woken when the FAMILY finishes")
    la.add_argument("--wait-for-pid", type=int,
                    help="start when this resident exits, if admission names it (the launcher's)")
    r = sub.add_parser("readout")
    r.add_argument("dirs", nargs="+", type=Path)
    r.add_argument("--where", action="append", default=[], metavar="COLUMN=VALUE")
    r.add_argument("--mix", action="append", default=[], type=Path,
                   help="an origin mix written by `mix`; the pooled answer is re-weighted to it")
    mx = sub.add_parser("mix", help="the origin mix of a run's settled homes, at the default "
                                    "book seed and the production founder count")
    mx.add_argument("report", type=Path)
    mx.add_argument("--wins-scale", type=float, default=1.0,
                    help="1/sample rate, to count the wins a weighted-sample book made")
    mx.add_argument("--source", required=True)
    mx.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("same")
    s.add_argument("a", type=Path)
    s.add_argument("b", type=Path)
    args = ap.parse_args(argv)

    if args.cmd == "member":
        return member(args.seed, args.founders or SHAPES[args.shape]["founders"], args.out,
                      args.shape, args.policy, args.level_from)
    if args.cmd == "launch":
        seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
        from background.launch_long_job import LaunchRefused, follow_unit
        try:
            entries = launch(seeds, args.founders or SHAPES[args.shape]["founders"], args.out,
                             args.tag, args.parallel,
                             {"question": args.question, "why_not_minutes": args.why_not_minutes,
                              "would_change": args.would_change,
                              "expect_minutes": args.expect_minutes},
                             wait_for_pid=args.wait_for_pid, shape=args.shape,
                             peak_mb=args.peak_mb, policy=args.policy,
                             level_from=args.level_from)
        except LaunchRefused as exc:
            print("REFUSED:", exc)
            return 2
        if args.detach:
            return 0
        # Director, 2026-10-10: "Every job you queue must wake you when it finishes."
        rcs = [follow_unit(e["unit"], e.get("artefact")) for e in entries]
        return max(rcs, default=0)
    if args.cmd == "mix":
        import simulation.live_population as lp
        founders = {r["customer_id"] for r in lp.founder_book(lp._DEFAULT_BASE_SEED)}
        mix = mix_of_report(json.loads(args.report.read_text(encoding="utf-8")), founders,
                            args.wins_scale)
        mix.update(source=args.source, founder_accounts=lp.founder_accounts())
        args.out.write_text(json.dumps(mix, indent=1), encoding="utf-8")
        print(json.dumps(mix))
        return 0
    if args.cmd == "same":
        diffs = tables_identical(read_table(args.a), read_table(args.b))
        print("IDENTICAL" if not diffs else "DIFFERS:\n" + "\n".join(diffs[:40]))
        return 1 if diffs else 0
    rows, refused, pooled = [], [], []
    for d in args.dirs:
        for meta_path in sorted(d.glob("member_*.json")):
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            why = member_refusal(int(meta["seed"]), meta)
            table = d / f"homes_{meta['seed']}.csv"
            if why or not table.exists():
                refused.append(why or f"{table} missing")
                continue
            pooled.append(meta)
            rows += read_table(table)
    mixed = mixed_policy_refusal(pooled)
    if mixed:
        print("REFUSED:", mixed)
        return 2
    if len({(r["seed"], r["home_id"]) for r in rows}) != len(rows):
        print("REFUSED: one seed's homes appear twice across the directories given")
        return 2
    for cond in args.where:
        col, _, val = cond.partition("=")
        rows = [r for r in rows if r.get(col) == val]
    mixes = [json.loads(m.read_text(encoding="utf-8")) for m in args.mix]
    policy = pooled[0].get("policy", UNSTAMPED_POLICY) if pooled else None
    print(json.dumps({"refused_members": refused, "policy": policy, **readout(rows, mixes)},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
