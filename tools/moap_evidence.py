#!/usr/bin/env python3
"""Primary-state DERIVATION behind every model-on-a-page node (atom
``SITE_evidence_pages_behind_nodes``).

WHY THIS EXISTS
---------------
The front-door model-on-a-page diagram makes six present-tense claims ("The world --
Live", "The company -- Building"). ``moap_node_evidence_anchors`` (closed 2026-07-24)
wired each node to a deep anchor on an existing door, so a reader can walk from the
node to *a figure*. What no surface has ever shown is the EVIDENCE FOR THE STAGE WORD
ITSELF: which atoms that claim rests on, what level each is actually at, what moved
them, and what is on record behind them.

Director ruling ``DIRECTOR_RULING_HARNESS_INVESTMENT_AND_ITS_EVIDENCE_2026-07-27``,
section 1: *"A method that has never produced anything is an unfalsifiable claim. The
proof that the harness works is a company it built."* This module is the derivation
that makes that inspectable.

COHERENCE-BY-DERIVATION -- THE BINDING DISCIPLINE
-------------------------------------------------
Everything here is DERIVED from primary state, never transcribed:

  * ``docs/design/maturity_map.yaml``            -- atom levels, lane, stage, expert hour,
                                                   declared evidence documents, file_scope
  * ``docs/observability/gate_authorizations.jsonl`` -- the level-move RECORD (R16)
  * ``docs/observability/fidelity_evidence_ledger.json`` -- measured fidelity rows
  * ``tests/**``                                 -- the test modules that NAME the atom
  * ``git log``                                  -- last commit touching the atom's file_scope

A number hand-copied onto a page is exactly the "restated prose" failure this atom
exists to kill, so nothing in this module accepts a literal figure from anywhere but
the source that owns it.

INDEPENDENCE (R15, the TAUTOLOGY killer)
----------------------------------------
The stage a node CLAIMS (``declared_stage`` in ``site/data/moap_node_atoms.json``, and
the stage word rendered in the built page) is hand-authored. The stage this module
COMPUTES comes from the map's atom levels. They are two different sources and are
therefore able to DISAGREE -- which is the entire point, and what
``tools/moap_evidence_gate.py`` fails the publish gate on.

FAIL-SILENT (R15)
-----------------
An unreadable / empty primary source raises ``DerivationUnavailable``. It never
degrades to an empty result, because an empty result would read as "no atoms below
target -> everything is Live" -- a control that passes when its own input is missing.

Run standalone for the per-node derivation report::

    python3 tools/moap_evidence.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

MAP_PATH = REPO_ROOT / "docs" / "design" / "maturity_map.yaml"
MAPPING_PATH = REPO_ROOT / "site" / "data" / "moap_node_atoms.json"
GATE_LEDGER_PATH = REPO_ROOT / "docs" / "observability" / "gate_authorizations.jsonl"
FIDELITY_LEDGER_PATH = REPO_ROOT / "docs" / "observability" / "fidelity_evidence_ledger.json"
TESTS_ROOT = REPO_ROOT / "tests"
EVIDENCE_ROOT = REPO_ROOT / "site" / "evidence"

# Stage vocabulary -- the exact title-case words the front door and the mapping use, so a
# computed stage compares directly against a declared/rendered one (site/moap_stage.py).
LIVE = "Live"
BUILDING = "Building"
PLANNED = "Planned"

# A node whose derived stage is PLANNED claims nothing exists yet, so it has no primary
# state to show; every OTHER stage is a live present-tense claim and MUST be evidenced.
NON_TRIVIAL_STAGES = frozenset({LIVE, BUILDING})

# A test module that names >= this many distinct atom ids is a map-wide REGISTRY (e.g.
# tests/tools/test_maturity_map_facets.py names 116). It is evidence about the MAP, not
# about any one atom, so its function count is reported separately and never rolled into
# an atom's own test count -- otherwise every atom inherits the same inflated number and
# the figure stops meaning anything.
REGISTRY_ATOM_THRESHOLD = 10

_TEST_FN = re.compile(r"^(?:async\s+)?def\s+(test_\w+)", re.M)


class DerivationUnavailable(RuntimeError):
    """A primary source is missing, unreadable or empty.

    R15 FAIL-SILENT: raised rather than returning a degraded/empty derivation, because an
    empty derivation reads as "nothing is below target" -- a check that passes precisely
    when it cannot see. Callers must treat this as a FAILED check, never a skipped one.
    """


# --------------------------------------------------------------------------- primary state


def load_atoms(map_path: Path = MAP_PATH) -> dict[str, dict]:
    """``{atom id -> atom record}`` for every atom in the maturity map."""
    try:
        raw = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DerivationUnavailable(f"maturity map not found: {map_path}") from exc
    except (OSError, yaml.YAMLError) as exc:
        raise DerivationUnavailable(f"maturity map unreadable: {map_path}: {exc}") from exc
    if not isinstance(raw, list) or not raw:
        raise DerivationUnavailable(f"maturity map is empty or not a list: {map_path}")
    atoms = {a["id"]: a for a in raw if isinstance(a, dict) and a.get("id")}
    if not atoms:
        raise DerivationUnavailable(f"maturity map declares no atoms: {map_path}")
    return atoms


def load_mapping(mapping_path: Path = MAPPING_PATH) -> dict:
    """The canonical node->atom mapping (``site/data/moap_node_atoms.json``)."""
    try:
        data = json.loads(mapping_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DerivationUnavailable(f"node->atom mapping not found: {mapping_path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise DerivationUnavailable(f"node->atom mapping unreadable: {mapping_path}: {exc}") from exc
    nodes = data.get("nodes") if isinstance(data, dict) else None
    if not isinstance(nodes, list) or not nodes:
        raise DerivationUnavailable(f"node->atom mapping declares no nodes: {mapping_path}")
    return data


def load_gate_ledger(path: Path = GATE_LEDGER_PATH) -> dict[str, list[dict]]:
    """``{atom id -> [level-move records]}`` from the append-only gate-authorizations ledger.

    R16: the ledger is the RECORD of a level move. An atom with no row here has no recorded
    move -- which the page states plainly rather than hiding. A missing ledger FILE is a
    failed derivation (fail-silent guard), not "no atom ever moved".
    """
    if not path.exists():
        raise DerivationUnavailable(f"gate-authorizations ledger not found: {path}")
    rows: dict[str, list[dict]] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DerivationUnavailable(f"gate-authorizations ledger unreadable: {path}: {exc}") from exc
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # one corrupt line must not blind the whole ledger
        atom = rec.get("atom")
        if atom:
            rows.setdefault(atom, []).append(rec)
    return rows


def load_fidelity_ledger(path: Path = FIDELITY_LEDGER_PATH) -> dict[str, list[dict]]:
    """``{atom id -> [fidelity-register rows]}`` from the fidelity evidence ledger."""
    if not path.exists():
        raise DerivationUnavailable(f"fidelity evidence ledger not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DerivationUnavailable(f"fidelity evidence ledger unreadable: {path}: {exc}") from exc
    rows: dict[str, list[dict]] = {}
    for key, rec in (data or {}).items():
        if not isinstance(rec, dict):
            continue
        atom = rec.get("atom_id")
        if atom:
            rows.setdefault(atom, []).append({"key": key, **rec})
    return rows


def build_test_index(
    atom_ids: Iterable[str], tests_root: Path = TESTS_ROOT
) -> dict[str, list[dict]]:
    """``{atom id -> [{path, test_functions, registry}]}`` -- the test modules that NAME the atom.

    Provenance, derived by reading the test tree: a module counts for an atom only if the
    atom's id appears literally in it. ``registry`` marks a map-wide module (see
    REGISTRY_ATOM_THRESHOLD) whose functions are reported but never attributed to one atom.
    """
    ids = list(atom_ids)
    if not ids:
        raise DerivationUnavailable("no atom ids to index tests for")
    if not tests_root.is_dir():
        raise DerivationUnavailable(f"test tree not found: {tests_root}")
    index: dict[str, list[dict]] = {a: [] for a in ids}
    for path in sorted(tests_root.rglob("test_*.py")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        present = [a for a in ids if a in text]
        if not present:
            continue
        n_fns = len(_TEST_FN.findall(text))
        registry = len(present) >= REGISTRY_ATOM_THRESHOLD
        rel = str(path.relative_to(REPO_ROOT))
        for atom in present:
            index[atom].append({"path": rel, "test_functions": n_fns, "registry": registry})
    return index


def last_commit_for(paths: Iterable[str], repo_root: Path = REPO_ROOT) -> dict | None:
    """The most recent commit touching any of an atom's ``file_scope`` paths.

    Provenance from git itself. Returns ``None`` when git is unavailable or the scope has no
    history -- the page RENDERS that absence ("not derivable") rather than omitting the row,
    so an unavailable source is visible instead of silently absent.
    """
    scope = [p for p in paths if p]
    if not scope:
        return None
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%h%x1f%aI%x1f%s", "--", *scope],
            cwd=str(repo_root), capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    parts = out.stdout.strip().splitlines()[0].split("\x1f")
    if len(parts) != 3:
        return None
    return {"sha": parts[0], "date": parts[1], "subject": parts[2]}


# --------------------------------------------------------------------------- the derivation


def compute_stage(atom_levels: list[dict]) -> str:
    """A node's stage as a PURE FUNCTION of its atoms' levels.

    THE RULE (``site/data/moap_node_atoms.json::_derivation_rule``, shared with
    ``site/moap_stage.py``): LIVE = every mapped atom at target; PLANNED = none started;
    BUILDING = anything else. An empty atom set resolves to PLANNED, never vacuously LIVE
    (``all([])`` is True) -- the fail-open guard.
    """
    if not atom_levels:
        return PLANNED
    if all(a["level_current"] >= a["level_target"] for a in atom_levels):
        return LIVE
    if all(a["level_current"] == 0 for a in atom_levels):
        return PLANNED
    return BUILDING


def _atom_row(
    atom_id: str,
    atoms: dict[str, dict],
    gate_rows: dict[str, list[dict]],
    fidelity_rows: dict[str, list[dict]],
    test_index: dict[str, list[dict]],
    with_git: bool = True,
) -> dict:
    """Every piece of primary state that stands behind ONE atom's contribution to a claim."""
    rec = atoms.get(atom_id)
    if rec is None:
        # An atom a node names but the map does not declare is a Phase-A coherence defect
        # (DEAD_ATOM_REF, gated in site/moap_coherence.py). It must never false-green a node,
        # so it derives as started-but-below-target: it can only drag a node toward Building.
        rec = {"id": atom_id, "level_current": 0, "level_target": 1, "name": "(absent from the maturity map)"}
        in_map = False
    else:
        in_map = True

    cur = int(rec.get("level_current") or 0)
    # A record with no declared target defaults to 1, not 0, so a target-less atom cannot
    # read as vacuously "at target" and false-green its node (the site/moap_stage convention).
    tgt = int(rec.get("level_target") if rec.get("level_target") is not None else 1)

    file_scope = rec.get("file_scope") or []
    if isinstance(file_scope, str):
        file_scope = [file_scope]

    evidence_docs = []
    for doc in rec.get("evidence") or []:
        doc = str(doc)
        evidence_docs.append({"path": doc, "exists": (REPO_ROOT / doc).exists()})

    modules = sorted(test_index.get(atom_id, []), key=lambda m: m["path"])
    own = [m for m in modules if not m["registry"]]
    registry = [m for m in modules if m["registry"]]

    expert = rec.get("expert_hour") or {}
    ledger = sorted(gate_rows.get(atom_id, []), key=lambda r: r.get("ts") or 0)

    return {
        "id": atom_id,
        "name": str(rec.get("name") or atom_id),
        "in_map": in_map,
        "lane": str(rec.get("lane") or "?"),
        "value_stream": str(rec.get("value_stream") or "?"),
        "epoch": rec.get("epoch"),
        "level_current": cur,
        "level_target": tgt,
        "at_target": cur >= tgt,
        "loop_stage": str(rec.get("loop_stage") or "?"),
        "expert_hour_status": str(expert.get("status") or "not_attempted"),
        "expert_hour_findings": len(expert.get("findings") or []),
        "note_count": len(rec.get("simplifications") or []),
        "file_scope": [str(p) for p in file_scope],
        "evidence_docs": evidence_docs,
        "evidence_docs_resolving": sum(1 for d in evidence_docs if d["exists"]),
        "test_modules": own,
        "test_module_count": len(own),
        "test_function_count": sum(m["test_functions"] for m in own),
        "registry_modules": registry,
        "ledger_rows": [
            {
                "action": str(r.get("action") or "?"),
                "level": r.get("level"),
                "ts": r.get("ts"),
                "authorized_by": str(r.get("authorized_by") or "?"),
                "provenance": str(r.get("provenance") or "")[:400],
            }
            for r in ledger
        ],
        "fidelity_rows": [
            {
                "key": r.get("key"),
                "layer": str(r.get("layer") or "?"),
                "measured_at": r.get("measured_at"),
                "cells": len(r.get("per_cell_lift") or []),
            }
            for r in sorted(fidelity_rows.get(atom_id, []), key=lambda r: str(r.get("measured_at") or ""))
        ],
        "last_commit": last_commit_for(file_scope) if with_git else None,
    }


def node_ids(mapping: dict) -> list[str]:
    return [str(n.get("id")) for n in mapping.get("nodes", [])]


def evidence_href_for(node_id: str) -> str:
    """The canonical site path of a node's evidence page (the URL the diagram walks to)."""
    return f"/evidence/{node_id}/"


def node_evidence(
    node: dict,
    atoms: dict[str, dict],
    gate_rows: dict[str, list[dict]],
    fidelity_rows: dict[str, list[dict]],
    test_index: dict[str, list[dict]],
    with_git: bool = True,
) -> dict:
    """One node's full derivation: its computed stage plus the primary state behind it."""
    atom_ids = list(node.get("atoms") or [])
    rows = [
        _atom_row(a, atoms, gate_rows, fidelity_rows, test_index, with_git=with_git)
        for a in atom_ids
    ]
    computed = compute_stage(rows)
    declared = node.get("declared_stage")
    return {
        "id": str(node.get("id")),
        "name": str(node.get("name") or node.get("id")),
        "look_href": node.get("look_href"),
        "evidence_href": node.get("evidence_href"),
        "declared_stage": declared,
        "computed_stage": computed,
        "stage_matches": declared is None or declared == computed,
        "non_trivial": computed in NON_TRIVIAL_STAGES,
        "atoms": rows,
        "atom_count": len(rows),
        "atoms_at_target": sum(1 for r in rows if r["at_target"]),
        "test_module_count": sum(r["test_module_count"] for r in rows),
        "test_function_count": sum(r["test_function_count"] for r in rows),
        "ledger_row_count": sum(len(r["ledger_rows"]) for r in rows),
        "fidelity_row_count": sum(len(r["fidelity_rows"]) for r in rows),
        "evidence_doc_count": sum(len(r["evidence_docs"]) for r in rows),
        "evidence_docs_resolving": sum(r["evidence_docs_resolving"] for r in rows),
    }


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except OSError:
        return None


def _rel(path: Path) -> str:
    """Repo-relative path where possible, absolute otherwise (a source pointed at a sandbox
    copy in a test must not raise -- provenance formatting is never a reason to fail)."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def evidence_model(
    map_path: Path = MAP_PATH,
    mapping_path: Path = MAPPING_PATH,
    gate_ledger_path: Path = GATE_LEDGER_PATH,
    fidelity_path: Path = FIDELITY_LEDGER_PATH,
    tests_root: Path = TESTS_ROOT,
    with_git: bool = True,
    with_tests: bool = True,
) -> dict:
    """The whole derivation: every node, its computed stage and its primary-state evidence.

    Raises ``DerivationUnavailable`` if any primary source is missing/unreadable/empty.

    ``with_git`` / ``with_tests`` control the two EXPENSIVE provenance passes (a subprocess
    per atom; a full read of the test tree). Both are page CONTENT, never gate inputs, so the
    publish-gate path turns them off: the gate's verdict must not depend on -- and must not be
    slowed by -- material it does not check.
    """
    atoms = load_atoms(map_path)
    mapping = load_mapping(mapping_path)
    gate_rows = load_gate_ledger(gate_ledger_path)
    fidelity_rows = load_fidelity_ledger(fidelity_path)
    referenced = sorted({a for n in mapping["nodes"] for a in (n.get("atoms") or [])})
    test_index = (
        build_test_index(sorted(set(atoms) | set(referenced)), tests_root)
        if with_tests
        else {}
    )
    nodes = [
        node_evidence(n, atoms, gate_rows, fidelity_rows, test_index, with_git=with_git)
        for n in mapping["nodes"]
    ]
    return {
        "nodes": nodes,
        "derivation_rule": str(mapping.get("_derivation_rule") or ""),
        "sources": [
            {"path": _rel(p), "sha256_16": _sha256(p)}
            for p in (map_path, mapping_path, gate_ledger_path, fidelity_path)
        ],
        "map_atom_count": len(atoms),
        "node_count": len(nodes),
    }


def main() -> int:
    model = evidence_model()
    print("=== model-on-a-page node evidence -- primary-state derivation ===\n")
    for n in model["nodes"]:
        flag = "" if n["stage_matches"] else "   <-- DECLARED/DERIVED DISAGREE"
        print(
            f"{n['name']:22s} declared={str(n['declared_stage']):9s} derived={n['computed_stage']:9s}"
            f" atoms={n['atoms_at_target']}/{n['atom_count']} at target"
            f" tests={n['test_function_count']} in {n['test_module_count']} modules"
            f" ledger={n['ledger_row_count']} fidelity={n['fidelity_row_count']}{flag}"
        )
    print(f"\nsources: {[s['path'] for s in model['sources']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
