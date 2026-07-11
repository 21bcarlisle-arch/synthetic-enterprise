#!/usr/bin/env python3
"""Generate site/data/simplified.json from docs/design/maturity_map.yaml --
the SIMPLIFIED (honesty door) page's data, per docs/design/SITE_CONSTITUTION.md
Section 4's "quiet fourth door" on the Front Door, and Section 2's own
description: "The consolidated simplifications register, grouped by lane,
each entry: what's cut, why, when it's due. Cheap to build, disproportionate
trust yield."

Each maturity_map.yaml atom's own `simplifications` list is the real,
already-written register this project has been keeping honestly all along
(director-confirmed known gaps, DISCOVER-stage findings, HARDEN-sweep
adjudicated-real gaps) -- this generator only groups and republishes it,
never authors new text (SITE_CONSTITUTION rule 5: "the site is a rendering,
never an author").
"""
import json
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
OUT_PATH = PROJECT / "site" / "data" / "simplified.json"

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


def _load_atoms():
    if not MATURITY_MAP_YAML.is_file():
        return None
    try:
        data = yaml.safe_load(MATURITY_MAP_YAML.read_text())
    except yaml.YAMLError:
        return None
    return data


def generate():
    atoms = _load_atoms()
    if not isinstance(atoms, list):
        return False

    by_lane: dict[str, list[dict]] = {}
    total_entries = 0
    for atom in atoms:
        if not isinstance(atom, dict):
            continue
        notes = atom.get("simplifications") or []
        if not notes:
            continue
        lane = atom.get("lane", "unknown")
        by_lane.setdefault(lane, []).append({
            "atom_id": atom.get("id"),
            "atom_name": atom.get("name"),
            "level_current": atom.get("level_current"),
            "level_target": atom.get("level_target"),
            "notes": notes,
        })
        total_entries += len(notes)

    lanes_out = [
        {
            "lane": lane,
            "lane_name": LANE_NAMES.get(lane, lane),
            "atoms": sorted(entries, key=lambda a: a["atom_id"] or ""),
        }
        for lane, entries in sorted(by_lane.items())
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "lanes": lanes_out,
        "total_atoms_with_notes": sum(len(l["atoms"]) for l in lanes_out),
        "total_notes": total_entries,
    }, indent=2))
    return True


if __name__ == "__main__":
    ok = generate()
    print("Generated site/data/simplified.json" if ok else "FAILED to generate simplified.json")
