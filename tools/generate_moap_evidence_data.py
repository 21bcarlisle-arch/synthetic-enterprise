#!/usr/bin/env python3
"""Coherence-by-derivation (§6) -- PHASE E, the DATA side: the evidence behind each
model-on-a-page node, derived from PRIMARY STATE.

Atom: SITE_evidence_pages_behind_nodes (H_harness, SITE lane). The §A follow-on of the
SITE-model-spine campaign. `moap_node_evidence_anchors` (done, 2026-07-24) wired every
front-door diagram node's "Look:" link to a deep fragment on an existing door. That gave the
reader a VIEW. It did not give them the EVIDENCE: the actual figures, the level history, the
fidelity rows and the test provenance that substantiate the node's Live/Building claim. This
generator produces exactly that, and nothing else.

WHY GENERATED, NEVER HAND-AUTHORED (the crux of the atom's exit criterion 2)
---------------------------------------------------------------------------
A page of narrative DESCRIBING the evidence fails the criterion -- it is the restated prose the
front door already carries. The evidence page must render the REAL NUMBERS, and a hand-authored
number drifts from primary state the moment an atom moves. So every figure on the page is
derived here from a primary source and nothing on the page is typed by a human:

  * docs/design/maturity_map.yaml            -- the atoms' REAL level_current/level_target,
                                                lane, loop_stage, expert-hour status, evidence refs
  * site/data/moap_node_atoms.json           -- the canonical node->atom mapping (Phase A)
  * docs/observability/gate_authorizations.jsonl
                                             -- the level-move LEDGER (R16): every recorded move
                                                for the node's atoms, with its timestamp and
                                                self-certified provenance text
  * docs/observability/fidelity_evidence_ledger.json
                                             -- the fidelity-register rows measured for the atom
  * the repo's own test tree (tests/**, site/**)
                                             -- the count of test functions that NAME the atom
  * docs/observability/test_execution_log.jsonl
                                             -- the last recorded whole-suite execution count,
                                                carried WITH its timestamp (provenance, not a claim)

The node's own CLAIM (`declared_stage` / the front door's hand-typed stage word) is carried
through UNUSED as evidence -- it is rendered beside the derived stage precisely so a reader (and
the gate in site/moap_evidence.py) can see the two disagree. The derived stage is computed by
`moap_stage.compute_stage`, the SAME single rule home Phases B/C/D use: one derivation, four
surfaces, never a second copy of the rule.

HONEST LABELLING. `test_functions` counts test functions whose file NAMES the atom -- it is
provenance ("this much test code is addressed to this atom"), not a claim that they passed.
The passing figure is the whole-suite execution stamp, carried with its own timestamp so a
reader can see how fresh it is. Neither number is ever tuned, and neither is a target (R12).

Run:  python3 tools/generate_moap_evidence_data.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
_SITE_DIR = PROJECT / "site"
# The moap_* derivation modules live under site/ and import each other by bare name (the
# `pytest site/` rootdir convention) -- same sys.path convention tools/moap_coherence_gate.py uses.
if str(_SITE_DIR) not in sys.path:
    sys.path.insert(0, str(_SITE_DIR))

from moap_stage import compute_stage  # noqa: E402

MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
MAPPING = PROJECT / "site" / "data" / "moap_node_atoms.json"
LEDGER = PROJECT / "docs" / "observability" / "gate_authorizations.jsonl"
FIDELITY = PROJECT / "docs" / "observability" / "fidelity_evidence_ledger.json"
TEST_EXEC_LOG = PROJECT / "docs" / "observability" / "test_execution_log.jsonl"
OUT_PATH = PROJECT / "site" / "data" / "moap_evidence.json"

# Where test provenance is scanned from. Both lanes, because this project's tests genuinely live
# in two roots (`tests/` runs at publish, `site/**` runs at the site-lane pre-commit gate).
TEST_ROOTS = ("tests", "site")
_TEST_DEF = re.compile(r"^\s*(?:async\s+)?def\s+test_\w*\s*\(", re.MULTILINE)

# Cap the per-atom lists that reach the page. The page renders EVERY atom of a node, but a single
# atom with 40 level-ledger rows would bury the reader; the totals stay exact (counted before the
# cap) so nothing is silently lost -- the cap is presentation, never arithmetic.
MAX_LEDGER_ROWS = 6
MAX_TEST_FILES = 8
MAX_FIDELITY_ROWS = 4
_PROVENANCE_CHARS = 400


def _iso(ts: float | int | None) -> str | None:
    """Epoch seconds -> ISO-8601 UTC. None/garbage -> None (never a fabricated date)."""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def load_atoms(map_path: Path = MAP_YAML) -> dict[str, dict]:
    """{atom id -> its full map record}. The map is the primary state for every level figure
    on the page; a missing/unparseable map raises rather than resolving to {} -- an evidence
    page built from a map this process could not read would be a FAIL-SILENT surface."""
    records = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError(f"{map_path} did not parse to a list of atom records")
    return {r["id"]: r for r in records if isinstance(r, dict) and r.get("id")}


def load_ledger(path: Path = LEDGER) -> dict[str, list[dict]]:
    """{atom id -> its level-move records}, oldest first, from the gate-authorizations ledger
    (R16: the ledger is the RECORD). A malformed line is skipped, not fatal -- the ledger is
    append-only from many writers -- but an ABSENT ledger yields {} and every atom then renders
    'no recorded level move', which is the honest reading, never a green one."""
    out: dict[str, list[dict]] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        atom = rec.get("atom")
        if not isinstance(atom, str):
            continue
        out.setdefault(atom, []).append(rec)
    return out


def load_fidelity(path: Path = FIDELITY) -> dict[str, list[dict]]:
    """{atom id -> its fidelity-register rows}. Keys in the register are either the atom id or
    `<atom_id>::<measurement>`, and rows also carry an explicit `atom_id`; both routes are
    honoured so a row cannot be missed by key-shape alone."""
    out: dict[str, list[dict]] = {}
    if not path.is_file():
        return out
    try:
        register = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    if not isinstance(register, dict):
        return out
    for key, row in register.items():
        if not isinstance(row, dict):
            continue
        atom = row.get("atom_id") or key.split("::", 1)[0]
        if isinstance(atom, str):
            out.setdefault(atom, []).append({"key": key, "row": row})
    return out


_test_scan_cache: dict[tuple[str, ...], list[tuple[str, str, int]]] = {}


def _test_corpus(project: Path = PROJECT) -> list[tuple[str, str, int]]:
    """[(repo-relative path, file text, test-function count)] for every test file in the repo.
    Read once per process (the scan is ~1100 files); the cache key is the root set so a test
    pointing at a temp tree never reuses the real repo's scan."""
    key = tuple(str(project / r) for r in TEST_ROOTS)
    if key in _test_scan_cache:
        return _test_scan_cache[key]
    corpus: list[tuple[str, str, int]] = []
    for root in TEST_ROOTS:
        base = project / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("test_*.py")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            corpus.append((str(path.relative_to(project)), text, len(_TEST_DEF.findall(text))))
    _test_scan_cache[key] = corpus
    return corpus


def atom_test_provenance(atom_id: str, project: Path = PROJECT) -> dict:
    """Test provenance for one atom: the test files that NAME it and how many test functions
    each holds. This is provenance, not a pass claim -- see the module docstring."""
    files = [
        {"path": rel, "test_functions": n}
        for rel, text, n in _test_corpus(project)
        if atom_id in text
    ]
    files.sort(key=lambda f: (-f["test_functions"], f["path"]))
    return {
        "test_files": len(files),
        "test_functions": sum(f["test_functions"] for f in files),
        "files": files[:MAX_TEST_FILES],
    }


def suite_execution_stamp(path: Path = TEST_EXEC_LOG) -> dict:
    """The last whole-suite execution recorded in the test-execution log, WITH its timestamp.
    Absent/unreadable -> {'available': False}: the page then says the stamp is unavailable
    rather than rendering a bare number with no clock (R14's discipline, applied to a test
    count -- a figure without its clock is a defect)."""
    if not path.is_file():
        return {"available": False}
    last = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict) and isinstance(rec.get("test_count"), int):
            last = rec
    if last is None:
        return {"available": False}
    return {
        "available": True,
        "test_count": last["test_count"],
        "timestamp": last.get("timestamp"),
    }


def _atom_row(atom_id: str, atoms: dict, ledger: dict, fidelity: dict, project: Path) -> dict:
    """One atom's primary-state evidence row. An atom the map does not contain is a Phase-A
    DEAD_ATOM_REF (gated there); here it renders explicitly as `in_map: false` with level 0/1,
    the same never-false-green convention moap_stage._UNKNOWN_ATOM uses."""
    rec = atoms.get(atom_id)
    in_map = rec is not None
    rec = rec or {}
    current = rec.get("level_current", 0) or 0
    target = rec.get("level_target", 1) if rec.get("level_target") is not None else 1
    rows = ledger.get(atom_id, [])
    fid = fidelity.get(atom_id, [])
    tests = atom_test_provenance(atom_id, project)
    return {
        "id": atom_id,
        "name": rec.get("name"),
        "lane": rec.get("lane"),
        "in_map": in_map,
        "level_current": int(current),
        "level_target": int(target),
        "at_target": int(current) >= int(target),
        "loop_stage": rec.get("loop_stage"),
        "expert_hour": (rec.get("expert_hour") or {}).get("status", "not_attempted"),
        "evidence_refs": [str(e) for e in (rec.get("evidence") or [])],
        "ledger_records": len(rows),
        "ledger": [
            {
                "action": r.get("action"),
                "level": r.get("level"),
                "ts_utc": _iso(r.get("ts")),
                "authorized_by": r.get("authorized_by"),
                "provenance": (r.get("provenance") or "")[:_PROVENANCE_CHARS],
            }
            for r in rows[-MAX_LEDGER_ROWS:]
        ],
        "fidelity_rows": len(fid),
        "fidelity": [
            {
                "key": f["key"],
                "layer": f["row"].get("layer"),
                "measured_at": f["row"].get("measured_at"),
                "metrics": _fidelity_metrics(f["row"]),
            }
            for f in fid[:MAX_FIDELITY_ROWS]
        ],
        "tests": tests,
    }


def _fidelity_metrics(row: dict) -> dict:
    """The scalar figures on a fidelity row, flattened for rendering. Only genuine numbers are
    carried (a dict/list value is summarised by its length) so the page never prints a blob."""
    out: dict[str, object] = {}
    for key, value in row.items():
        if key in {"atom_id", "layer", "measured_at", "key"}:
            continue
        if isinstance(value, bool):
            out[key] = value
        elif isinstance(value, (int, float)):
            out[key] = value
        elif isinstance(value, (list, dict)) and value:
            out[f"{key}_n"] = len(value)
    return out


def build_evidence_data(
    map_path: Path = MAP_YAML,
    mapping_path: Path = MAPPING,
    ledger_path: Path = LEDGER,
    fidelity_path: Path = FIDELITY,
    test_exec_path: Path = TEST_EXEC_LOG,
    project: Path = PROJECT,
) -> dict:
    """The whole evidence derivation, as a pure function of primary state. Every figure in the
    returned structure traces to one of the five sources named in the module docstring; nothing
    here is authored."""
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    atoms = load_atoms(map_path)
    ledger = load_ledger(ledger_path)
    fidelity = load_fidelity(fidelity_path)

    nodes = []
    for node in mapping.get("nodes", []):
        atom_ids = node.get("atoms", []) or []
        rows = [_atom_row(a, atoms, ledger, fidelity, project) for a in atom_ids]
        # THE derivation -- the same single rule home Phases B/C/D use, never a second copy.
        derived = compute_stage(
            [{"current": r["level_current"], "target": r["level_target"]} for r in rows]
        )
        nodes.append(
            {
                "id": node.get("id"),
                "anchor": f"node-{node.get('id')}",
                "name": node.get("name", node.get("id")),
                # The CLAIM, carried for contrast only. It is never an input to `derived_stage`.
                "claimed_stage": node.get("declared_stage"),
                "derived_stage": derived,
                "supported": node.get("declared_stage") in (None, derived),
                "atoms": rows,
                "totals": {
                    "atoms": len(rows),
                    "at_target": sum(1 for r in rows if r["at_target"]),
                    "ledger_records": sum(r["ledger_records"] for r in rows),
                    "fidelity_rows": sum(r["fidelity_rows"] for r in rows),
                    "test_files": sum(r["tests"]["test_files"] for r in rows),
                    "test_functions": sum(r["tests"]["test_functions"] for r in rows),
                },
            }
        )

    return {
        "_doc": (
            "DERIVED evidence behind every model-on-a-page node (atom "
            "SITE_evidence_pages_behind_nodes). Every figure is read from primary state by "
            "tools/generate_moap_evidence_data.py -- nothing on the evidence page is authored. "
            "A node's derived_stage is computed from its atoms' real levels in "
            "docs/design/maturity_map.yaml; claimed_stage is the site's own hand-set claim, "
            "carried ONLY so the two can be seen to disagree."
        ),
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "sources": {
            "map": str(map_path.relative_to(project)) if _under(map_path, project) else str(map_path),
            "mapping": str(mapping_path.relative_to(project)) if _under(mapping_path, project) else str(mapping_path),
            "level_ledger": str(ledger_path.relative_to(project)) if _under(ledger_path, project) else str(ledger_path),
            "fidelity_register": str(fidelity_path.relative_to(project)) if _under(fidelity_path, project) else str(fidelity_path),
            "test_roots": list(TEST_ROOTS),
        },
        "suite_execution": suite_execution_stamp(test_exec_path),
        "totals": {
            "nodes": len(nodes),
            "atoms": sum(n["totals"]["atoms"] for n in nodes),
            "ledger_records": sum(n["totals"]["ledger_records"] for n in nodes),
            "fidelity_rows": sum(n["totals"]["fidelity_rows"] for n in nodes),
            "test_functions": sum(n["totals"]["test_functions"] for n in nodes),
        },
        "nodes": nodes,
    }


def _under(path: Path, project: Path) -> bool:
    try:
        path.relative_to(project)
        return True
    except ValueError:
        return False


def generate(out_path: Path = OUT_PATH) -> bool:
    data = build_evidence_data()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(
        f"Generated evidence for {data['totals']['nodes']} node(s) / "
        f"{data['totals']['atoms']} atom(s) -> {out_path}"
    )
    return True


if __name__ == "__main__":
    generate()
