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
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Importable both as `tools.generate_simplified_data` (process_run_complete.py)
# and as a bare script (`python3 tools/generate_simplified_data.py`).
if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import simplifications_store as store  # noqa: E402
from tools.abolished_block_classes import (  # noqa: E402
    ABOLISHED_BLOCK_CLASSES,
    annotate_notes,
)

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
    total_superseded = 0
    for atom in atoms:
        if not isinstance(atom, dict):
            continue
        # simplifications now live in the sibling store (retro FM-1); the loader
        # returns EXACTLY the list this field used to hold. The store sits beside
        # the map, so a relocated MATURITY_MAP_YAML relocates the store too.
        notes = store.for_atom(atom.get("id"), MATURITY_MAP_YAML.parent / "simplifications") or []
        if not notes:
            continue
        lane = atom.get("lane", "unknown")
        # `notes` stays byte-identical (rule 5: the site is a rendering, never
        # an author). `superseded` is DERIVED metadata keyed by note index, so a
        # note describing a hold behind an ABOLISHED act can be marked as
        # historical instead of reading as live policy on /proof/.
        note_texts, superseded = annotate_notes(notes)
        by_lane.setdefault(lane, []).append({
            "atom_id": atom.get("id"),
            "atom_name": store.atom_name(atom, MATURITY_MAP_YAML.parent / "simplifications"),
            "level_current": atom.get("level_current"),
            "level_target": atom.get("level_target"),
            "notes": note_texts,
            "superseded": superseded,
        })
        total_entries += len(notes)
        total_superseded += len(superseded)

    lanes_out = [
        {
            "lane": lane,
            "lane_name": LANE_NAMES.get(lane, lane),
            "atoms": sorted(entries, key=lambda a: a["atom_id"] or ""),
        }
        for lane, entries in sorted(by_lane.items())
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # R2 freshness: the honesty register carries its own generation stamp so the
    # Simplified door can show when it was last rebuilt (SITE_CONSTITUTION rule 2).
    OUT_PATH.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lanes": lanes_out,
        "total_atoms_with_notes": sum(len(l["atoms"]) for l in lanes_out),
        "total_notes": total_entries,
        # The dead-rule exposure, published rather than quietly corrected: how
        # many register notes describe a hold behind an act that no longer
        # exists, and what replaced each act. The renderer marks these as
        # historical; the count is itself an honesty figure.
        "total_notes_superseded": total_superseded,
        "abolished_block_classes": [
            {
                "name": c.name,
                "abolished_on": c.abolished_on,
                "ruling": c.ruling,
                "replaced_by": c.replaced_by,
            }
            for c in ABOLISHED_BLOCK_CLASSES.values()
        ],
    }, indent=2))
    return True


if __name__ == "__main__":
    ok = generate()
    print("Generated site/data/simplified.json" if ok else "FAILED to generate simplified.json")
