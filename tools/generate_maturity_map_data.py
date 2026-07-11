#!/usr/bin/env python3
"""Generate site/data/maturity_map.json from docs/design/maturity_map.yaml.

Director page-comment priority (2026-07-11, from_rich_20260711_075004.md):
the maturity-map rendering (four views over the canonical YAML, per
docs/design/MATURITY_MAP.md Section 6) "never shipped to the Project page --
it's now the epoch's primary window." All four views (function matrix,
value-stream flow, campaign, activity) are renderings of the SAME flat atom
list -- this generator emits the atoms plus the lane-level equaliser
(level/dial/loop_stage per lane, MATURITY_MAP.md Section 8, restated here
since that table is prose in the .md, not structured in the .yaml) and lets
the site's own JS group/toggle between views client-side.
"""
import json
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
OUT_PATH = PROJECT / "site" / "data" / "maturity_map.json"

# MATURITY_MAP.md Section 8 (the director-ratified equaliser table) restated
# here in structured form -- lane-level dial/loop-stage-now, distinct from
# any individual atom's own dial_inherited/loop_stage. Update this dict
# alongside that table (kept in sync manually; the .md table is the
# authoritative source director/advisor edit directly).
LANE_EQUALISER = {
    "W1_market_weather": {"name": "W1 Market & Weather", "level_now": "L1", "dial": 4, "loop_stage_now": "discover"},
    "D_billing_metering": {"name": "D Billing & Metering", "level_now": "L2", "dial": 4, "loop_stage_now": "frame"},
    "B_commercial": {"name": "B Commercial", "level_now": "L2", "dial": 3, "loop_stage_now": "discover"},
    "C_customer_ops": {"name": "C Customer Ops", "level_now": "L2→3", "dial": 3, "loop_stage_now": "build"},
    "E_finance_treasury": {"name": "E Finance & Treasury", "level_now": "L1→2", "dial": 3, "loop_stage_now": "frame"},
    "W2_customer_generator": {"name": "W2 Customer Generator", "level_now": "L1→2", "dial": 3, "loop_stage_now": "build"},
    "W4_the_wall": {"name": "W4 The Wall", "level_now": "L1", "dial": 3, "loop_stage_now": "frame"},
    "A_strategy_governance": {"name": "A Strategy & Governance", "level_now": "L2", "dial": 2, "loop_stage_now": "idle"},
    "G_data_learning": {"name": "G Data & Learning", "level_now": "L2", "dial": 2, "loop_stage_now": "idle"},
    "W3_industry_systems": {"name": "W3 Industry Systems", "level_now": "L1", "dial": 2, "loop_stage_now": "idle"},
    "W5_banking_payment_rails": {"name": "W5 Banking & Payment Rails", "level_now": "L0", "dial": 2, "loop_stage_now": "idle"},
    "F_risk_compliance": {"name": "F Risk & Compliance", "level_now": "L3", "dial": 1, "loop_stage_now": "harden"},
    "H_harness": {"name": "H Harness", "level_now": "L3", "dial": 1, "loop_stage_now": "harden"},
}

VALUE_STREAM_LABELS = {
    "wholesale_to_price": "Wholesale to Price",
    "price_to_bill": "Price to Bill",
    "meter_to_cash": "Meter to Cash",
    "close_to_learn": "Close to Learn",
}

# THE_VALUE_CYCLE_FRAMING.md section 4 -- four movements, their own exit
# tests (quoted verbatim from the ratified framing), and REAL current status
# as of each phase close (updated by hand at phase close, same discipline as
# CLAUDE.md's "Current state" -- not auto-derived, since "exit test passing"
# is a judgement call, not a mechanical atom-count).
EPOCH2_MOVEMENTS = [
    {
        "id": "M1", "name": "The clock and the log",
        "exit_test": "The hedge decision literally cannot see past ‘now’; a restatement lands as an event and downstream values version correctly.",
        "status": "in_progress",
        "status_note": "Bitemporal log + as-of interfaces built; hedge-decision price history migrated onto PointInTimeView (2026-07-11) -- 'cannot see past now' half of the exit test now structurally true and tested. Investigated the remaining two sub-components before building (docs/design/M1_EVENT_DRAIN_MATERIALITY_FRAME.md): the sim's outer decision loop is already event-shaped; the real step-based cost is settlement-record generation itself (hedged_settlement.py), which is ground truth, not overhead -- a same-day rewrite risks corrupting real data for a scaling concern that isn't live yet (~8min/run today, not blocking). Deliberately deferred pending a director/advisor sequencing call, not built blind.",
    },
    {
        "id": "M2", "name": "Three clocks through the books",
        "exit_test": "The two revenue series reconcile BY DESIGN, and a bill can be lawfully wrong then corrected on the portal.",
        "status": "audit_complete",
        "status_note": "Entry-gate payments maturity audit complete 2026-07-11 (docs/design/M2_PAYMENTS_AUDIT_DD_RAILS.md + M2_PAYMENTS_AUDIT_BILLING_COLLECTIONS.md): verdict HARDEN-EXISTING for the company-logic layer, NEW BUILD for the Banking & Payment Rails simulator (Bacs rails-physics layer is entirely absent). Build not yet started -- waits on M1's exit test per the framing's own sequencing.",
    },
    {
        "id": "M3", "name": "Discovery and the draw",
        "exit_test": "The company mis-estimates a new customer's consumption, bills wrong, discovers, rebills -- end to end on surfaces; two runs with different draws produce different books.",
        "status": "not_started",
        "status_note": "Design-only in background forks per the framing's own spike integration (section 5). Not yet started.",
    },
    {
        "id": "M4", "name": "Rederivation and the reckoning",
        "exit_test": "The director reads the rederived decade and recognises a real supplier's life.",
        "status": "not_started",
        "status_note": "Strictly last, per the framing. All headline public figures are PROVISIONAL until this lands (site/supplier/index.html banners, 2026-07-11).",
    },
]


def _load_atoms():
    with open(MATURITY_MAP_YAML) as f:
        return yaml.safe_load(f)


def generate():
    atoms = _load_atoms()
    if not isinstance(atoms, list):
        return False

    out_atoms = []
    for a in atoms:
        if not isinstance(a, dict):
            continue
        out_atoms.append({
            "id": a.get("id"),
            "name": a.get("name"),
            "lane": a.get("lane"),
            "value_stream": a.get("value_stream"),
            "value_stream_label": VALUE_STREAM_LABELS.get(a.get("value_stream"), a.get("value_stream")),
            "epoch": a.get("epoch"),
            "level_current": a.get("level_current"),
            "level_target": a.get("level_target"),
            "loop_stage": a.get("loop_stage"),
            "dial_inherited": a.get("dial_inherited"),
            "expert_hour_status": (a.get("expert_hour") or {}).get("status", "not_attempted"),
            "depends_on": a.get("depends_on", []),
            "at_target": a.get("level_current") is not None and a.get("level_target") is not None
                and a["level_current"] >= a["level_target"],
        })

    data = {
        "atoms": out_atoms,
        "lanes": LANE_EQUALISER,
        "total_atoms": len(out_atoms),
        "epoch2_movements": EPOCH2_MOVEMENTS,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=2))
    print(f"Generated {len(out_atoms)} atoms -> {OUT_PATH}")
    return True


if __name__ == "__main__":
    generate()
