"""May forward years start? The basics' definition of done, graded.

DIRECTOR, 24 Oct 17:22: "We need the basics of payment, dual fuel, switching etc all working. But
after that we probably want weather and simple wholesale prices and forward products for hedging
simualted for some future years." His ruling's item 2 asks for that definition "as tests and records
rather than prose"; this is the check that grades it, read in the Monday step.

The definition lives in `docs/direction/priority_order.yaml`, step 6's `starts_when`, so the order
and the condition that opens its next step have one home. Two readings, kept apart:

  GATE    every named atom at its target level, read from the map. This alone says whether forward
          runs may start. An atom missing from the map is unmet, by name.
  LINES   what each basic is made of. A line's state is derived, never typed: ABSENT if it names no
          test or a named test file does not exist; PARTIAL if its atom is below target or missing;
          DONE otherwise. A line marked done in prose and absent here is the check working.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ORDER = ROOT / "docs" / "direction" / "priority_order.yaml"
STEP = 6


def load_definition(path: Path = ORDER) -> dict:
    steps = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("steps") or {}
    step = steps.get(STEP) or steps.get(str(STEP)) or {}
    return step.get("starts_when") or {}


def _levels(atoms: list[dict]) -> dict[str, tuple[int, int]]:
    return {a["id"]: (int(a.get("level_current") or 0), int(a.get("level_target") or 0))
            for a in atoms if isinstance(a, dict) and a.get("id")}


def grade(definition: dict, atoms: list[dict], root: Path = ROOT) -> dict:
    levels = _levels(atoms)
    gate = []
    for atom_id in definition.get("gate") or []:
        cur, tgt = levels.get(atom_id, (None, None))
        gate.append({"atom": atom_id, "now": cur, "target": tgt,
                     "met": cur is not None and cur >= tgt})
    lines = []
    for row in definition.get("lines") or []:
        tests = row.get("tests") or []
        missing = [t for t in tests if not (root / t).exists()]
        atom = row.get("atom")
        if not tests:
            state, why = "absent", "names no test"
        elif missing:
            state, why = "absent", "no such test: " + ", ".join(missing)
        elif atom and atom not in levels:
            state, why = "partial", f"{atom} is not on the map"
        elif atom and levels[atom][0] < levels[atom][1]:
            state, why = "partial", f"{atom} at {levels[atom][0]}, target {levels[atom][1]}"
        else:
            state, why = "done", ""
        lines.append({"basic": row.get("basic"), "line": row.get("line"), "state": state, "why": why})
    return {"gate": gate, "lines": lines,
            "ready": bool(gate) and all(g["met"] for g in gate)}


def render(result: dict | None = None) -> str:
    if result is None:
        from tools.maturity_map_store import load_atoms
        result = grade(load_definition(), load_atoms())
    gate, lines = result["gate"], result["lines"]
    met = sum(g["met"] for g in gate)
    counts = {s: sum(x["state"] == s for x in lines) for s in ("done", "partial", "absent")}
    head = ("**The basics are done: forward years may start** (once the director gives his G9 go)."
            if result["ready"] else
            f"**Not yet: {met} of {len(gate)} gate atoms at target.** Forward runs wait.")
    out = [head, "", "| Gate atom | Now → target |", "|---|---|"]
    for g in gate:
        lvl = "not on the map" if g["now"] is None else f"{g['now']} → {g['target']}"
        out.append(f"| {'✓ ' if g['met'] else ''}`{g['atom']}` | {lvl} |")
    out += ["", f"Lines: {counts['done']} done, {counts['partial']} partial, "
            f"{counts['absent']} absent, of {len(lines)}.", ""]
    out += [f"- {x['state'].upper()} ({x['basic']}) {x['line']}" + (f" -- {x['why']}" if x["why"] else "")
            for x in lines if x["state"] != "done"]
    return "\n".join(out)


if __name__ == "__main__":
    print(render())
    sys.exit(0)
