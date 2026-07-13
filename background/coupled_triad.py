"""COUPLED-TRIAD draw-coupling gate -- binding rule 1 of THE_COUPLED_TRIAD as
ENFORCED CODE (director P1, MAKE_IT_STICK: "convert policy to mechanism, or
accept it will evaporate").

Binding rule 1: "No SIM/world atom reaches L3 ('fails like reality') until the
company has been tested against it and the belief-vs-truth GAP has been
measured." Mechanised here as a BUILD-lane draw gate: a WORLD atom may not be
drawn for BUILD toward L3 unless (a) its coupled company twin exists in the map
with level_current >= 2, AND (b) a non-null gap measurement exists for the pair
in the gap ledger.

This is HARNESS/orchestration code. It reads the maturity map (atom levels +
depends_on) and the gap ledger only. It NEVER reads SIM internals -- the
epistemic wall is intact.

Design source: docs/design/COUPLED_TRIAD_DESIGN.md (esp. section 4.1, the
L3-ceiling gate). The gap-ledger contract is GIVEN by the task, not redesigned
here:

    docs/observability/coupled_gap_ledger.json
    { "<world_atom_id>": {"twin_atom_id": "<C_id>", "gap": <float 0..1 | null>,
                          "measured_at": "<iso8601>", "run_git_commit": "<sha>",
                          "baseline": "<g0 desc>", "note": "..."}, ... }

An entry with a non-null numeric `gap` means "company faced this world, gap
measured." Absent OR null gap means NOT measured -> block L3.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
GAP_LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "coupled_gap_ledger.json"
MATURITY_MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

# A world atom is identified by lane/id prefix W1_/W2_ (matches how
# supervisor.py names the SIM/world lanes: lane="W2_customer_generator",
# id="W2_7_willingness_classification").
WORLD_PREFIXES = ("W1_", "W2_")

# Authoritative coupling (world short-id -> twin short-id), from
# THE_COUPLED_TRIAD (director P1). Used ONLY as a cross-check against what is
# derived from the live map: build_coupling() raises if the map's C-atom
# depends_on disagree with this table. W2_9 -> C11 is included here because
# C11_segment_debt_policy sits in lane F_risk_compliance with an empty
# depends_on, so its coupling is not derivable from the map and this table is
# its sole source (design section 2.1 notes C11 "may be scoped as a
# company-compliance atom rather than customer-ops").
_AUTHORITATIVE_COUPLING = {
    "W2_7": "C9",
    "W2_8": "C10",
    "W2_5": "C7",
    "W2_4": "C6",
    "W2_10": "C12",
    "W2_6": "C8",
    "W2_9": "C11",
}

_SHORT_ID_RE = re.compile(r"^(W\d+_\d+|[A-Z]+\d+)")


def _short_id(full_id: str) -> str:
    """Reduce a full atom id to its short lane-and-number token, e.g.
    'W2_7_willingness_classification' -> 'W2_7', 'C10_self_rationing_detection'
    -> 'C10'. Falls back to the full id when it does not match the pattern."""
    m = _SHORT_ID_RE.match(full_id or "")
    return m.group(1) if m else (full_id or "")


def is_world_atom(atom: dict) -> bool:
    """True if the atom belongs to a SIM/world lane (W1_/W2_ prefix on its lane
    or id)."""
    if not isinstance(atom, dict):
        return False
    lane = atom.get("lane") or ""
    atom_id = atom.get("id") or ""
    return any(lane.startswith(p) for p in WORLD_PREFIXES) or any(
        atom_id.startswith(p) for p in WORLD_PREFIXES
    )


def build_coupling(atoms: list) -> dict:
    """Return {world_full_id: twin_full_id}, derived from the map's C-atom
    depends_on and cross-checked against _AUTHORITATIVE_COUPLING.

    Derivation: each company twin (id short-form starts with 'C') that names a
    world atom in its depends_on yields a world->twin pair. Every derived pair
    MUST agree with the authoritative table -- a disagreement (same world atom
    coupled to a different twin) raises ValueError, per the task ("raise if they
    disagree"). Authoritative pairs that the map cannot derive (W2_9->C11, whose
    twin has an empty depends_on) are filled in from the table where both atoms
    are present in the map.
    """
    if not isinstance(atoms, list):
        return {}
    short_to_full: dict = {}
    for a in atoms:
        if isinstance(a, dict) and a.get("id"):
            short_to_full.setdefault(_short_id(a["id"]), a["id"])

    derived_short: dict = {}
    for a in atoms:
        if not isinstance(a, dict):
            continue
        twin_short = _short_id(a.get("id") or "")
        if not twin_short.startswith("C"):
            continue
        for dep in a.get("depends_on") or []:
            dep_short = _short_id(dep)
            if any(dep_short.startswith(p) for p in WORLD_PREFIXES):
                derived_short[dep_short] = twin_short

    # Cross-check every derivable pair against the authoritative table.
    for world_short, twin_short in derived_short.items():
        expected = _AUTHORITATIVE_COUPLING.get(world_short)
        if expected is not None and expected != twin_short:
            raise ValueError(
                "COUPLED_TRIAD coupling disagreement: map derives "
                f"{world_short}->{twin_short} but authoritative table has "
                f"{world_short}->{expected}. Reconcile maturity_map.yaml "
                "depends_on with THE_COUPLED_TRIAD before drawing."
            )

    # Final coupling = authoritative table (complete, incl. non-derivable
    # W2_9->C11), resolved to full ids present in the given atom set.
    coupling: dict = {}
    for world_short, twin_short in _AUTHORITATIVE_COUPLING.items():
        world_full = short_to_full.get(world_short)
        twin_full = short_to_full.get(twin_short)
        if world_full and twin_full:
            coupling[world_full] = twin_full
    return coupling


def _twin_id_for(world_atom: dict, atoms: list):
    """Full id of the company twin coupled to the given world atom, or None."""
    world_id = world_atom.get("id") if isinstance(world_atom, dict) else None
    if not world_id:
        return None
    coupling = build_coupling(atoms)
    if world_id in coupling:
        return coupling[world_id]
    # Fall back to short-id lookup in the authoritative table, resolved against
    # the atom set (covers a world atom whose full id differs slightly).
    twin_short = _AUTHORITATIVE_COUPLING.get(_short_id(world_id))
    if not twin_short:
        return None
    for a in atoms:
        if isinstance(a, dict) and _short_id(a.get("id") or "") == twin_short:
            return a["id"]
    return None


def load_gap_ledger(path=None) -> dict:
    """Load the coupled gap ledger. A missing file returns {} (the correct
    current state: nothing measured yet, so ALL world->L3 BUILD draws are
    blocked). A malformed/unreadable file also degrades to {} -- an unavailable
    ledger is treated as 'nothing measured', which fails CLOSED (blocks L3),
    never fails open."""
    p = Path(path) if path is not None else GAP_LEDGER_PATH
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def gap_measured(world_id: str, ledger: dict) -> bool:
    """True iff the ledger has an entry for this world atom carrying a non-null
    numeric gap. Absent OR null OR non-numeric gap -> False (not measured)."""
    if not isinstance(ledger, dict):
        return False
    entry = ledger.get(world_id)
    if not isinstance(entry, dict):
        return False
    gap = entry.get("gap")
    # bool is a subclass of int; a boolean gap is malformed, not a measurement.
    if isinstance(gap, bool):
        return False
    return isinstance(gap, (int, float))


def world_l3_blocked(world_atom: dict, atoms: list, ledger: dict):
    """Binding rule 1 as a predicate.

    Returns (blocked, reason). blocked is True -- with a human-readable reason
    -- when ALL of:
      * the atom is a world atom (W1_/W2_ lane/id prefix), AND
      * its next BUILD step targets L3 or beyond (level_current+1 >= 3 and it
        still has a gap up to a level_target >= 3), AND
      * the coupling is NOT closed: the coupled company twin is missing, or the
        twin's level_current < 1, or the pair's gap is unmeasured in the ledger.

    A non-world atom, an atom not stepping toward L3, or one whose coupling is
    closed returns (False, ...). The gate never blocks BUILD below L3 -- a world
    atom builds freely up to L2 (design section 4.1: cap at L2 until the
    coupling closes).
    """
    if not is_world_atom(world_atom):
        return False, "not a world atom"

    level_current = world_atom.get("level_current")
    level_target = world_atom.get("level_target")
    if not isinstance(level_current, int) or not isinstance(level_target, int):
        return False, "level_current/level_target not integers"

    # Only the step INTO L3 (or beyond) is gated. Building toward <=L2 is free.
    next_target = level_current + 1
    if next_target < 3 or level_target < 3 or level_current >= level_target:
        return False, "next BUILD step does not target L3"

    world_id = world_atom.get("id") or "<unknown>"
    twin_id = _twin_id_for(world_atom, atoms)
    if twin_id is None:
        return (
            True,
            f"{world_id} targets L3 but has no coupled company twin registered "
            "in the map -- binding rule 1: a world mechanism no company "
            "capability has been tested against cannot reach L3 (registration "
            "defect if level_target>=3 with no twin).",
        )

    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
    twin = by_id.get(twin_id)
    twin_level = twin.get("level_current") if isinstance(twin, dict) else None
    if not isinstance(twin_level, int) or twin_level < 2:
        return (
            True,
            f"{world_id} targets L3 but its coupled twin {twin_id} is at "
            f"level_current={twin_level} (<2) -- the company capability is not yet "
            "mechanically real (L2) enough to have coped with this world "
            "(binding rule 1, design section 4.1).",
        )

    if not gap_measured(world_id, ledger):
        return (
            True,
            f"{world_id} targets L3 but the belief-vs-truth GAP for pair "
            f"({world_id} <-> {twin_id}) is unmeasured in the gap ledger -- "
            "binding rule 1: the gap must be measured before L3.",
        )

    return False, f"coupling closed for {world_id} <-> {twin_id}"


def _load_map_atoms() -> list:
    try:
        import yaml
    except ImportError:
        return []
    try:
        atoms = yaml.safe_load(MATURITY_MAP_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []
    return atoms if isinstance(atoms, list) else []


# Module-level coupling derived from the live map, for callers that want it
# without re-loading. A missing/malformed map yields {} rather than an
# import-time crash. A genuine coupling DISAGREEMENT still raises (fail loud),
# per the task.
COUPLING = build_coupling(_load_map_atoms())
