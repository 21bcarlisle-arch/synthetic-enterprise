#!/usr/bin/env python3
"""Coherence-by-derivation (§6) -- PHASE E: the EVIDENCE behind each model-on-a-page node.

Atom: SITE_evidence_pages_behind_nodes (lane H_harness).

WHY THIS EXISTS
---------------
Phases A-D made a front-door node's Live/Building/Planned word HONEST -- it is computed from
its mapped atoms' levels (site/moap_stage.py) and the publish gate refuses a commit when the
surfaces disagree (tools/moap_coherence_gate.py). What a reader still could NOT do is ASK WHY:
each node's `Look: ...` link pointed at a narrative door anchor, so the stage claim rested on
prose. This phase puts the PRIMARY STATE behind the claim one click away -- the atom levels the
stage is derived from, the artefacts each atom names and whether they actually EXIST on disk,
how many tests those test files really define, the recorded level-move ledger rows, and the
MEASURED belief-vs-truth gaps / fidelity-ledger rows where the harness has produced them.

THE BINDING DESIGN RULE (from the atom): the evidence pages are GENERATED FROM THE DERIVATION.
Nothing here restates a claim in prose -- every rendered figure is read out of a primary artefact
at generation time:
  * docs/design/maturity_map.yaml            -- atom levels, lanes, epochs, loop stage, evidence list
  * site/data/moap_node_atoms.json           -- the canonical node->atom mapping (Phase A)
  * site/moap_stage.py                       -- the stage derivation itself (Phase B), imported, not copied
  * the repo working tree                    -- does each named artefact EXIST; how many tests does it define
  * docs/observability/coupled_gap_ledger.json      -- measured belief-vs-truth gap per atom
  * docs/observability/fidelity_evidence_ledger.json -- measured per-cell lift / relationship figures
  * docs/observability/gate_authorizations.jsonl     -- the recorded level moves (R16: the ledger is the record)
  * docs/observability/test_execution_log.jsonl      -- the suite collection stamp
The map's `simplifications` narrative is DELIBERATELY EXCLUDED (see `_ATOM_FIELDS`): restated
prose is an explicit failure of this atom's exit criterion 2.

THE GATE SURFACE (criteria 1 + 3, R15)
--------------------------------------
`evidence_findings()` is the ready-made pure query tools/moap_coherence_gate.py unions as its
fifth surface. It FIRES when:
  * EVIDENCE_PAGE_MISSING     -- site/evidence/index.html is absent or empty
  * EVIDENCE_DATA_MISSING     -- site/data/moap_evidence.json is absent, unparseable or node-less
  * EVIDENCE_NODE_MISSING     -- a node with a non-trivial claimed stage has no entry in that data
  * EVIDENCE_ANCHOR_NOT_ON_PAGE -- the evidence page carries no id="node-X" section for that node
                                   (the deep-link would land the reader at the page top -- the same
                                   class site/test_link_walk.py::test_live_site_moap_nodes_deep
                                   _anchored gates for the narrative doors)
  * DANGLING_EVIDENCE_ANCHOR  -- the front door links ./evidence/#node-X and X is not in the data
  * NODE_WITHOUT_EVIDENCE_LINK-- a non-trivial node carries no evidence link on the front door
  * EVIDENCE_STAGE_STALE      -- the data's recorded stage for a node != the stage computed NOW
Every one of those is FAIL-CLOSED: a missing, empty or malformed page/data file produces findings
rather than silence (R15's fail-open killer). Mutation-proven both ways in
tests/tools/test_moap_evidence.py.

WHY THE GATE COMPARES ONLY THE STAGE PROJECTION (deliberate, not laziness): the gate fires on a
node's STAGE CLAIM moving, which is exactly what exit criterion 3 names. A level edit that does
NOT move any node's stage (2->3 where the target is 3 and the node was already Building on some
other atom) leaves the page's detail figures one publish behind but its CLAIMS true -- and does
not wedge publishing on an unrelated map edit (feedback_control_false_positive_jams_pipeline).
The page renders its own `generated_at` + map digest so that lag is visible, never hidden.

CLI
---
  python3 tools/moap_evidence.py --write     regenerate site/data/moap_evidence.json
  python3 tools/moap_evidence.py --report    print the cross-surface evidence findings (exit 1 on any)
  python3 tools/moap_evidence.py             the human summary of what the pages will show
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_SITE_DIR = ROOT / "site"
# The moap_* derivation modules live under site/ and import each other by bare name (the
# `pytest site/` rootdir convention), the same way tools/moap_coherence_gate.py reaches them.
if str(_SITE_DIR) not in sys.path:
    sys.path.insert(0, str(_SITE_DIR))

from moap_coherence import _MAP, _MAPPING, SITE, load_mapping  # noqa: E402
from moap_stage import PLANNED, node_stages  # noqa: E402

EVIDENCE_DIR_NAME = "evidence"
EVIDENCE_DATA_NAME = "moap_evidence.json"

OBS = ROOT / "docs" / "observability"
COUPLED_GAP_LEDGER = OBS / "coupled_gap_ledger.json"
FIDELITY_LEDGER = OBS / "fidelity_evidence_ledger.json"
GATE_AUTHORIZATIONS = OBS / "gate_authorizations.jsonl"
TEST_EXECUTION_LOG = OBS / "test_execution_log.jsonl"

# Finding kinds (all HARD -- every one of them is a broken or over-claiming evidence trail).
EVIDENCE_PAGE_MISSING = "EVIDENCE_PAGE_MISSING"
EVIDENCE_DATA_MISSING = "EVIDENCE_DATA_MISSING"
EVIDENCE_NODE_MISSING = "EVIDENCE_NODE_MISSING"
EVIDENCE_ANCHOR_NOT_ON_PAGE = "EVIDENCE_ANCHOR_NOT_ON_PAGE"
DANGLING_EVIDENCE_ANCHOR = "DANGLING_EVIDENCE_ANCHOR"
NODE_WITHOUT_EVIDENCE_LINK = "NODE_WITHOUT_EVIDENCE_LINK"
EVIDENCE_STAGE_STALE = "EVIDENCE_STAGE_STALE"

# The front-door anchor form a node's evidence link must take.
_EVIDENCE_HREF = re.compile(r'href="\./evidence/#node-([A-Za-z0-9_]+)"')

# The ONLY atom fields that reach the page. `simplifications` (the map's long narrative field)
# and `real_world_twin` are excluded BY NAME: this atom's exit criterion 2 fails on restated
# prose, so the pages carry figures, paths and ledger rows -- never the map's story about them.
_ATOM_FIELDS = ("id", "name", "lane", "epoch", "loop_stage", "level_current", "level_target")


# --------------------------------------------------------------------------- primary state


def _repo_top_dirs() -> tuple[str, ...]:
    """The repo's real top-level directories, read off the tree (no hardcoded list) -- used to
    recognise which tokens inside an atom's free-text `evidence:` entry are PATH CLAIMS."""
    return tuple(
        sorted(
            p.name
            for p in ROOT.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        )
    )


def _path_re() -> re.Pattern[str]:
    alts = "|".join(re.escape(d) for d in _repo_top_dirs())
    return re.compile(rf"\b(?:{alts})/[A-Za-z0-9_./+-]*[A-Za-z0-9_]")


def artefact_paths(entry: str, pattern: re.Pattern[str] | None = None) -> list[str]:
    """Every repo path CLAIMED by one `evidence:` entry. Map evidence entries are free text
    that usually leads with one or more real paths and then annotates them
    ('tests/sim/test_weather_engine.py (27 tests)'), so the paths are extracted rather than
    assumed to be the whole string. An entry naming no path yields [] -- it is a note, counted
    as such, never silently treated as a resolving artefact."""
    pattern = pattern or _path_re()
    out: list[str] = []
    for m in pattern.finditer(entry):
        p = m.group(0)
        # Drop a '::symbol' suffix and a ':1234' line reference -- both name a location INSIDE
        # a file, so the file itself is the artefact whose existence is checkable.
        p = p.split("::", 1)[0]
        p = re.sub(r":\d+$", "", p)
        if p and p not in out:
            out.append(p)
    return out


def artefact_kind(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    if path.startswith("tests/") or name.startswith("test_"):
        return "test"
    if path.endswith((".md", ".txt")):
        return "doc"
    if path.endswith((".json", ".jsonl", ".yaml", ".yml", ".csv")):
        return "data"
    if path.endswith((".py", ".mjs", ".js", ".html", ".sh")):
        return "code"
    return "other"


def tests_defined(path: Path) -> int:
    """How many test functions a python test file REALLY defines, counted off its AST (module
    level + methods of any class). A file that will not parse returns 0 -- and, because the
    artefact row also carries `exists`, a 0 can never be read as 'this file is fine'."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return 0
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            n += 1
    return n


def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def coupled_gaps(path: Path = COUPLED_GAP_LEDGER) -> dict[str, dict]:
    """{atom -> the MEASURED belief-vs-truth gap row} (COUPLED TRIAD: 'the gap is the score').
    Only the scalar measurement fields are carried through; the nested `components` blob and the
    free-text `note` stay in the ledger."""
    raw = _load_json(path, {})
    out: dict[str, dict] = {}
    if not isinstance(raw, dict):
        return out
    for atom, row in raw.items():
        if not isinstance(row, dict):
            continue
        out[atom] = {
            "metric": row.get("metric"),
            "gap": row.get("gap"),
            "raw_gap": row.get("raw_gap"),
            "g0": row.get("g0"),
            "measured_at": row.get("measured_at"),
            "run_git_commit": row.get("run_git_commit"),
            "twin_atom_id": row.get("twin_atom_id"),
        }
    return out


def fidelity_rows(path: Path = FIDELITY_LEDGER) -> dict[str, list[dict]]:
    """{atom -> [fidelity-evidence-ledger rows]}, each reduced to its NUMERIC content: the
    scalar metrics of the relationship plus any per-cell lift table."""
    raw = _load_json(path, {})
    out: dict[str, list[dict]] = {}
    if not isinstance(raw, dict):
        return out
    for rel_id, row in raw.items():
        if not isinstance(row, dict):
            continue
        atom = row.get("atom_id")
        if not atom:
            continue
        rel = row.get("relationship") or {}
        metrics = {
            k: v for k, v in rel.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        cells = [
            {
                "cell": c.get("cell"),
                "regime": c.get("regime"),
                "lift": c.get("lift"),
                "err_model": c.get("err_model"),
                "err_naive": c.get("err_naive"),
            }
            for c in (row.get("per_cell_lift") or [])
            if isinstance(c, dict)
        ]
        out.setdefault(atom, []).append(
            {
                "rel_id": rel_id,
                "layer": row.get("layer"),
                "measured_at": row.get("measured_at"),
                "run_git_commit": row.get("run_git_commit"),
                "kind": rel.get("kind"),
                "metrics": metrics,
                "cells": cells,
            }
        )
    return out


def level_ledger(path: Path = GATE_AUTHORIZATIONS) -> dict[str, list[dict]]:
    """{atom -> [recorded level moves]} from gate_authorizations.jsonl. R16: the ledger is the
    RECORD of a level move. Rendering it alongside the map's `level_current` is the point --
    where the map claims a level the ledger never recorded, the reader can see that for himself."""
    out: dict[str, list[dict]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        atom = row.get("atom")
        if not atom:
            continue
        ts = row.get("ts")
        when = None
        if isinstance(ts, (int, float)):
            when = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        out.setdefault(atom, []).append(
            {
                "level": row.get("level"),
                "action": row.get("action"),
                "when": when,
                "authorized_by": row.get("authorized_by"),
            }
        )
    return out


def suite_stamp(path: Path = TEST_EXECUTION_LOG) -> dict:
    """The most recent whole-suite collection this repo recorded: {test_count, timestamp}. The
    page's provenance footer, so a reader can see WHICH suite state the artefact counts sit in."""
    best: dict = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return best
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row.get("test_count"), int) and row["test_count"] > best.get("test_count", 0):
            best = {"test_count": row["test_count"], "timestamp": row.get("timestamp")}
    return best


def map_atom_records(path: Path = _MAP) -> dict[str, dict]:
    """{atom id -> its map record}, restricted to `_ATOM_FIELDS` + `evidence`. Parsed with yaml
    (this runs in tools/, where yaml is already a dependency -- the site-scope modules avoid it)."""
    import yaml  # local import: keeps the site-scope import graph yaml-free

    try:
        atoms = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except (OSError, yaml.YAMLError):
        return {}
    out: dict[str, dict] = {}
    for a in atoms:
        if not isinstance(a, dict) or not a.get("id"):
            continue
        rec = {k: a.get(k) for k in _ATOM_FIELDS}
        rec["evidence"] = list(a.get("evidence") or [])
        out[a["id"]] = rec
    return out


def map_digest(path: Path = _MAP) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    except OSError:
        return ""


# --------------------------------------------------------------------------- the payload


def build_payload(
    site: Path = SITE, map_path: Path = _MAP, mapping_path: Path = _MAPPING
) -> dict:
    """The evidence payload for every model-on-a-page node -- generated FROM the derivation
    (Phase B's node_stages) plus the primary artefacts named above. Nothing in here is
    hand-authored: re-run the generator and the same repo state produces the same figures."""
    records = map_atom_records(map_path)
    gaps = coupled_gaps()
    fidelity = fidelity_rows()
    ledger = level_ledger()
    path_pat = _path_re()
    mapping = load_mapping(mapping_path)
    hrefs = {n.get("id"): n.get("look_href") for n in mapping.get("nodes", [])}

    nodes: list[dict] = []
    for stage in node_stages(map_path, mapping_path):
        atoms: list[dict] = []
        for detail in stage["atoms"]:
            aid = detail["id"]
            rec = records.get(aid, {})
            artefacts: list[dict] = []
            notes = 0
            for entry in rec.get("evidence", []):
                paths = artefact_paths(str(entry), path_pat)
                if not paths:
                    notes += 1
                    continue
                for p in paths:
                    if any(a["path"] == p for a in artefacts):
                        continue
                    fp = ROOT / p
                    exists = fp.exists()
                    kind = artefact_kind(p)
                    artefacts.append(
                        {
                            "path": p,
                            "exists": exists,
                            "kind": kind,
                            "tests_defined": (
                                tests_defined(fp) if exists and kind == "test" and p.endswith(".py") else None
                            ),
                        }
                    )
            atoms.append(
                {
                    "id": aid,
                    "name": rec.get("name"),
                    "lane": rec.get("lane"),
                    "epoch": rec.get("epoch"),
                    "loop_stage": rec.get("loop_stage"),
                    "level_current": detail["current"],
                    "level_target": detail["target"],
                    "at_target": detail["at_target"],
                    "in_map": detail["in_map"],
                    "artefacts": artefacts,
                    "artefacts_resolving": sum(1 for a in artefacts if a["exists"]),
                    "tests_defined": sum(a["tests_defined"] or 0 for a in artefacts),
                    "notes": notes,
                    "coupled_gap": gaps.get(aid),
                    "fidelity_rows": fidelity.get(aid, []),
                    "level_ledger": ledger.get(aid, []),
                }
            )
        nodes.append(
            {
                "id": stage["id"],
                "name": stage["name"],
                "declared_stage": stage["declared_stage"],
                "computed_stage": stage["computed_stage"],
                "look_href": hrefs.get(stage["id"]),
                "atoms_total": len(atoms),
                "atoms_at_target": sum(1 for a in atoms if a["at_target"]),
                "artefacts_total": sum(len(a["artefacts"]) for a in atoms),
                "artefacts_resolving": sum(a["artefacts_resolving"] for a in atoms),
                "tests_defined": sum(a["tests_defined"] for a in atoms),
                "measured_atoms": sum(1 for a in atoms if a["coupled_gap"] or a["fidelity_rows"]),
                "atoms": atoms,
            }
        )

    return {
        "_doc": (
            "GENERATED by tools/moap_evidence.py -- the primary-state evidence behind every "
            "model-on-a-page node. Never hand-edit: every figure is read out of the maturity map, "
            "the repo tree and the observability ledgers at generation time."
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "map_digest": map_digest(map_path),
        "derivation_rule": load_mapping(mapping_path).get("_derivation_rule", ""),
        "sources": [
            "docs/design/maturity_map.yaml",
            "site/data/moap_node_atoms.json",
            "docs/observability/coupled_gap_ledger.json",
            "docs/observability/fidelity_evidence_ledger.json",
            "docs/observability/gate_authorizations.jsonl",
            "docs/observability/test_execution_log.jsonl",
        ],
        "suite_stamp": suite_stamp(),
        "totals": {
            "nodes": len(nodes),
            "atoms": sum(n["atoms_total"] for n in nodes),
            "atoms_at_target": sum(n["atoms_at_target"] for n in nodes),
            "artefacts_total": sum(n["artefacts_total"] for n in nodes),
            "artefacts_resolving": sum(n["artefacts_resolving"] for n in nodes),
            "tests_defined": sum(n["tests_defined"] for n in nodes),
        },
        "nodes": nodes,
    }


def data_path(site: Path = SITE) -> Path:
    return site / "data" / EVIDENCE_DATA_NAME


def page_path(site: Path = SITE) -> Path:
    return site / EVIDENCE_DIR_NAME / "index.html"


def write_payload(
    site: Path = SITE, map_path: Path = _MAP, mapping_path: Path = _MAPPING
) -> Path:
    out = data_path(site)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload(site, map_path, mapping_path)
    out.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return out


# --------------------------------------------------------------------------- the gate surface


def front_door_evidence_anchors(site: Path = SITE) -> set[str]:
    """Every node id the front door links an evidence page for (`./evidence/#node-<id>`)."""
    front = site / "index.html"
    try:
        text = front.read_text(encoding="utf-8")
    except OSError:
        return set()
    return {m.group(1) for m in _EVIDENCE_HREF.finditer(text)}


def evidence_findings(
    site: Path = SITE, map_path: Path = _MAP, mapping_path: Path = _MAPPING
) -> list[tuple[str, str, str]]:
    """Every broken or stale evidence trail behind a front-door node, as (kind, subject, detail).
    Empty means: every node with a non-trivial claimed stage links to an evidence page that
    exists, the page's data carries that node, and the stage the data records is the stage the
    map computes RIGHT NOW.

    FAIL-CLOSED by construction (R15): an absent/empty page, an absent/unparseable/node-less data
    file, and a node missing from the data each PRODUCE findings. There is no input on which this
    query goes quiet -- the only way to an empty result is a real, complete evidence trail."""
    findings: list[tuple[str, str, str]] = []

    # Which nodes MUST have evidence: those making a non-trivial (non-Planned) present-tense claim.
    stages = node_stages(map_path, mapping_path)
    required = [s for s in stages if s["computed_stage"] != PLANNED]
    if not required:
        return findings  # nothing on the diagram claims anything yet -- nothing to substantiate

    page = page_path(site)
    page_text = ""
    try:
        page_text = page.read_text(encoding="utf-8")
    except OSError:
        page_text = ""
    if not page_text.strip():
        findings.append(
            (
                EVIDENCE_PAGE_MISSING,
                str(page.relative_to(site.parent)) if site.parent in page.parents else str(page),
                "the evidence page is absent or empty -- every node's 'look at the evidence' link dangles",
            )
        )

    raw = _load_json(data_path(site), None)
    data_nodes = raw.get("nodes") if isinstance(raw, dict) else None
    if not isinstance(data_nodes, list) or not data_nodes:
        findings.append(
            (
                EVIDENCE_DATA_MISSING,
                EVIDENCE_DATA_NAME,
                "the evidence data is absent, unparseable or carries no nodes -- the pages would render nothing",
            )
        )
        data_nodes = []
    by_id = {n.get("id"): n for n in data_nodes if isinstance(n, dict)}

    anchors = front_door_evidence_anchors(site)
    for node_id in sorted(anchors - set(by_id)):
        findings.append(
            (
                DANGLING_EVIDENCE_ANCHOR,
                node_id,
                "the front door links ./evidence/#node-%s but the evidence data has no such node" % node_id,
            )
        )

    for s in required:
        nid = s["id"]
        if nid not in anchors:
            findings.append(
                (
                    NODE_WITHOUT_EVIDENCE_LINK,
                    s["name"],
                    f"claims stage {s['computed_stage']!r} but the front door links no evidence page "
                    f"(expected href=\"./evidence/#node-{nid}\")",
                )
            )
        if page_text.strip() and f'id="node-{nid}"' not in page_text:
            findings.append(
                (
                    EVIDENCE_ANCHOR_NOT_ON_PAGE,
                    s["name"],
                    f"the evidence page carries no section id=\"node-{nid}\" -- the front-door "
                    f"deep link would land at the page top, not on this part's evidence",
                )
            )
        entry = by_id.get(nid)
        if entry is None:
            findings.append(
                (
                    EVIDENCE_NODE_MISSING,
                    s["name"],
                    f"claims stage {s['computed_stage']!r} but the evidence data carries no entry "
                    f"for node id {nid!r}",
                )
            )
            continue
        if entry.get("computed_stage") != s["computed_stage"] or entry.get(
            "declared_stage"
        ) != s["declared_stage"]:
            findings.append(
                (
                    EVIDENCE_STAGE_STALE,
                    s["name"],
                    "the evidence page records declared=%r computed=%r but the map computes "
                    "declared=%r computed=%r -- regenerate with "
                    "`python3 tools/moap_evidence.py --write`"
                    % (
                        entry.get("declared_stage"),
                        entry.get("computed_stage"),
                        s["declared_stage"],
                        s["computed_stage"],
                    ),
                )
            )
    return findings


# --------------------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--write" in argv:
        out = write_payload()
        payload = _load_json(out, {})
        t = payload.get("totals", {})
        print(f"wrote {out.relative_to(ROOT)}")
        print(
            f"  {t.get('nodes')} nodes  {t.get('atoms')} atoms "
            f"({t.get('atoms_at_target')} at target)  "
            f"{t.get('artefacts_resolving')}/{t.get('artefacts_total')} artefacts resolve  "
            f"{t.get('tests_defined')} tests defined"
        )
        return 0
    if "--report" in argv:
        findings = evidence_findings()
        print("=== §6 coherence-by-derivation -- Phase E: evidence pages behind the nodes ===\n")
        print(f"EVIDENCE findings (a node's evidence trail is broken or stale): {len(findings)}")
        for kind, subject, detail in findings:
            print(f"  [{kind}] {subject}: {detail}")
        return 1 if findings else 0

    payload = build_payload()
    t = payload["totals"]
    print("=== §6 Phase E -- what the evidence pages show ===\n")
    print(
        f"{t['nodes']} nodes | {t['atoms']} atoms ({t['atoms_at_target']} at target) | "
        f"{t['artefacts_resolving']}/{t['artefacts_total']} named artefacts resolve on disk | "
        f"{t['tests_defined']} tests defined in the named test files\n"
    )
    print(f"{'node':22s} {'stage':10s} {'at target':11s} {'artefacts':12s} {'tests':7s} measured")
    for n in payload["nodes"]:
        print(
            f"{n['name']:22s} {n['computed_stage']:10s} "
            f"{str(n['atoms_at_target']) + '/' + str(n['atoms_total']):11s} "
            f"{str(n['artefacts_resolving']) + '/' + str(n['artefacts_total']):12s} "
            f"{n['tests_defined']:<7d} {n['measured_atoms']} atom(s) with a measured gap/ledger row"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
