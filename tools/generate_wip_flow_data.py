#!/usr/bin/env python3
"""Generate site/data/wip_flow.json -- the WIP + cycle-time flow dashboard
(atom G7_wip_cycle_time_dashboard, Kanban / queue-theory lens).

The gap this closes (docs/design/METHOD_LENS_AUDIT.md, Kanban + Queue-theory
rows): the project already learned the qualitative lessons ("GPU at 2% isn't the
constraint", multi-atom draw caps parallelism by file_scope) but never surfaced
the QUANTITATIVE flow picture -- how much work is in progress, how long a level
transition actually takes, how many land per period. This door renders that from
REAL repo data, nothing fabricated:

  WIP -- counted live from docs/design/maturity_map.yaml: atoms by loop_stage
  (build / harden / idle) and by lane, plus the current concurrent-BUILD WIP
  (atoms whose loop_stage is `build`). This is inventory, read not asserted.

  CYCLE TIME + THROUGHPUT -- REUSES tools/effort_calibration.py (it already mines
  git-timestamped `<atom> -> L<n>` level transitions and computes per-lane
  duration distributions). We import and call it -- the git mining is NOT
  reinvented here. Per-lane mean/median cycle-time comes straight from its
  `calibration_by_lane`; throughput (transitions per day, whole-history and
  trailing-window) is derived from the same transition timestamps.

THE KANBAN INSIGHT this atom encodes (rendered as a stated PRINCIPLE on the page,
not just a number): WIP is capped by VERIFIED CAPACITY, not raw fork count.
Throughput is bounded by the verification step (the full suite runs ONCE per
integration, PER_ATOM_INTEGRATION_NOT_WAVES; verification never fans out) -- so
spinning up more concurrent build forks past that bound just grows queue, not
flow. Little's Law made concrete for this shop.

DIAL, NOT TARGET (R12 anti-goal-seek, extended to PROCESS metrics exactly as
effort_calibration extends it to effort): every figure here -- WIP count, cycle
time, throughput -- is a DIAGNOSTIC. The moment one becomes a thing to hit or
game, it manufactures the deadline pressure that produces false self-certified
levels. Labelled as such on the page and in this JSON (`dial_not_target`).

Rendering, never authoring (SITE_CONSTITUTION rule 5): every number is read from
the maturity map + git history via effort_calibration; only the principle prose
is transcribed canon.

R14 basis labels: cycle-time / throughput figures carry their clock -- the
"clock" here is git commit-time elapsed between consecutive level-transition
commits (`git_commit_time_between_level_transitions`), stated on the page.
"""
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from tools import effort_calibration as ec

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
OUT_PATH = PROJECT / "site" / "data" / "wip_flow.json"

# Same lane display names as the other doors (method_casebook) -- kept in sync
# by copy because the site generators are deliberately standalone scripts.
LANE_NAMES = {
    "W1_market_weather": "W1 Market & Weather",
    "D_billing_metering": "D Billing & Metering",
    "B_commercial": "B Commercial",
    "C_customer_ops": "C Customer Ops",
    "E_finance_treasury": "E Finance & Treasury",
    "W2_customer_generator": "W2 Customer Generator",
    "W4_the_wall": "W4 The Wall",
    "A_strategy_governance": "A Strategy & Governance",
    "G_data_learning": "G Data & Learning",
    "W3_industry_systems": "W3 Industry Systems",
    "W5_banking_payment_rails": "W5 Banking & Payment Rails",
    "F_risk_compliance": "F Risk & Compliance",
    "H_harness": "H Harness",
}

# loop_stage buckets, in board order (Kanban columns left->right: backlog->done).
# idle = parked for BUILD (DISCOVER/FRAME still available); build = actively
# being built; harden = adversarial sweep before a level banks.
STAGE_ORDER = ["idle", "build", "harden"]
STAGE_LABEL = {
    "idle": "Idle (parked for BUILD)",
    "build": "Build (in progress)",
    "harden": "Harden (adversarial sweep)",
}

WIP_CAP_PRINCIPLE = dict(
    headline="WIP is capped by VERIFIED CAPACITY, not fork count",
    body=(
        "Throughput here is bounded by the verification step, not the number of "
        "concurrent build forks. The full suite runs ONCE per integration "
        "(PER_ATOM_INTEGRATION_NOT_WAVES) and verification never fans out -- so "
        "spinning up more parallel forks past that bound grows the queue, not the "
        "flow (Little's Law: WIP = throughput x cycle-time). Concurrency is "
        "allowed only on provably disjoint file_scopes (the multi-atom draw gate); "
        "everything else serialises through the single verified-integration step. "
        "The cap is a real capacity, measured below, not a guessed fork number."
    ),
)

DIAL_NOT_TARGET = (
    "DIAL not a WALL -- every figure on this page (WIP count, cycle time, "
    "throughput) is a DIAGNOSTIC, never a target or completion gate (R12 "
    "anti-goal-seek, extended to process metrics). The moment a flow number "
    "becomes a thing to hit, it manufactures the deadline pressure that produces "
    "false self-certified levels."
)

# R14: the clock every cycle-time / throughput figure is measured on.
CYCLE_TIME_BASIS = "git_commit_time_between_level_transitions"


def _load_atoms():
    if not MATURITY_MAP_YAML.is_file():
        return []
    try:
        data = yaml.safe_load(MATURITY_MAP_YAML.read_text())
    except yaml.YAMLError:
        return []
    return data if isinstance(data, list) else []


def _get(d, *path):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _wip(atoms):
    """WIP inventory read live from the map: totals by loop_stage, by lane, and
    the current concurrent-BUILD count. Nothing derived from git here -- this is
    the present state of the board."""
    by_stage = Counter()
    by_lane = defaultdict(Counter)
    for a in atoms:
        stage = a.get("loop_stage") or "unknown"
        lane = a.get("lane") or "unknown"
        by_stage[stage] += 1
        by_lane[lane][stage] += 1

    stages = []
    for st in STAGE_ORDER:
        stages.append(dict(stage=st, label=STAGE_LABEL.get(st, st), count=by_stage.get(st, 0)))
    # surface any stage the map grows later that we didn't anticipate
    for st, n in sorted(by_stage.items()):
        if st not in STAGE_ORDER:
            stages.append(dict(stage=st, label=st, count=n))

    lanes = []
    for lane, counts in sorted(by_lane.items(), key=lambda kv: -sum(kv[1].values())):
        lanes.append(dict(
            lane=lane,
            lane_name=LANE_NAMES.get(lane, lane),
            total=sum(counts.values()),
            build=counts.get("build", 0),
            harden=counts.get("harden", 0),
            idle=counts.get("idle", 0),
        ))

    return dict(
        total_atoms=len(atoms),
        by_stage=stages,
        by_lane=lanes,
        concurrent_build_wip=by_stage.get("build", 0),
        harden_wip=by_stage.get("harden", 0),
        idle_count=by_stage.get("idle", 0),
    )


def _throughput(transitions):
    """Level transitions per period, from effort_calibration's parsed git
    history. Whole-history rate spans the first->last transition commit;
    trailing windows count transitions in the last N days. Timestamps are git
    commit time (%ct) -- the same clock cycle-time is measured on."""
    ts = sorted(t.timestamp for t in transitions)
    total = len(ts)
    if total < 2:
        return dict(total_transitions=total, span_days=None, per_day_all_time=None, windows=[])

    span_seconds = ts[-1] - ts[0]
    span_days = span_seconds / 86400.0
    per_day = round(total / span_days, 2) if span_days > 0 else None

    now = ts[-1]
    windows = []
    for days in (7, 14, 30):
        cutoff = now - days * 86400
        n = sum(1 for t in ts if t >= cutoff)
        windows.append(dict(
            days=days,
            transitions=n,
            per_day=round(n / days, 2),
        ))

    return dict(
        total_transitions=total,
        span_days=round(span_days, 2),
        per_day_all_time=per_day,
        first_transition=datetime.fromtimestamp(ts[0], tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        last_transition=datetime.fromtimestamp(ts[-1], tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        windows=windows,
    )


def _cycle_time(by_lane_dist):
    """Per-lane cycle-time (mean/median/n) straight from effort_calibration's
    calibration_by_lane -- only lanes with at least one observed duration."""
    lanes = []
    for lane, dist in by_lane_dist.items():
        if not dist.get("n"):
            continue
        lanes.append(dict(
            lane=lane,
            lane_name=LANE_NAMES.get(lane, lane),
            n=dist["n"],
            mean_hours=dist.get("mean_hours"),
            median_hours=dist.get("median_hours"),
            min_hours=dist.get("min_hours"),
            max_hours=dist.get("max_hours"),
        ))
    lanes.sort(key=lambda x: -(x["median_hours"] or 0))
    return lanes


def generate():
    try:
        dashboard = json.loads(DASHBOARD_PATH.read_text())
    except Exception:
        dashboard = {}

    atoms = _load_atoms()

    # REUSE tools/effort_calibration.py for cycle-time -- do not reinvent git mining.
    transitions = ec.git_log_transitions()
    durations = ec.compute_durations(transitions)
    by_lane_dist = ec.calibration_by_lane(durations)

    data = dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        dashboard_generated_at=_get(dashboard, "meta", "generated_at"),
        git_commit=_get(dashboard, "meta", "git_commit"),
        phase=_get(dashboard, "build", "current_phase"),
        test_count=_get(dashboard, "build", "test_count"),
        framing=(
            "The flow picture for this AI-run build, from real repo data: how much "
            "work is in progress (WIP, read live from the maturity map), how long a "
            "level transition actually takes (cycle-time, mined from git-timestamped "
            "transitions), and how many land per period (throughput). The Kanban / "
            "queue-theory lens the METHOD_LENS_AUDIT flagged as missing -- now shown "
            "working, not diagrammed."
        ),
        wip=_wip(atoms),
        cycle_time=dict(
            basis=CYCLE_TIME_BASIS,
            basis_label="git commit-time elapsed between consecutive level-transition commits",
            source_tool="tools/effort_calibration.py",
            n_transitions_parsed=len(transitions),
            n_durations_computed=len(durations),
            by_lane=_cycle_time(by_lane_dist),
        ),
        throughput=dict(
            basis=CYCLE_TIME_BASIS,
            **_throughput(transitions),
        ),
        wip_cap_principle=WIP_CAP_PRINCIPLE,
        dial_not_target=DIAL_NOT_TARGET,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return True


if __name__ == "__main__":
    generate()
