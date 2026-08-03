#!/usr/bin/env python3
"""Coherence-by-derivation (§6) -- PHASE D: the dedicated cross-surface publish gate.

Director ruling DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27, deliverable §6:
the MODEL, the DIAGRAM, the SITE and the MAP "must not be kept in sync by hand; three of
them must be derived from one" -- and "publish FAILS when model, diagram, site and map disagree."
Phase A (moap_coherence) fixed the node->atom mapping, Phase B (moap_stage) COMPUTES each node's
stage from its atoms' levels, Phase C (moap_render) proved the SITE renders that computed stage.
Each of those ships a ready-made pure query. Phase D is the GATE that unions them and REFUSES a
commit when any surface disagrees.

THE GAP THIS CLOSES (why a dedicated gate, not just the Phase-C site tests)
--------------------------------------------------------------------------
The site-lane gate (`tools/site_lane_gate.py`) runs `pytest site/` -- which includes the Phase
A/B/C tests -- but ONLY when a `site/**` / `site/data/**` / site-producer / site-ledger file is
staged. A stage disagreement can arise with NO site file staged at all: edit an atom's
`level_current` in `docs/design/maturity_map.yaml` and a node whose hand-set `declared_stage`
(and rendered HTML word) said 'Live' now computes 'Building' -- the front door over-claims, yet
`site_lane_gate.plan()` returns (None, None) because nothing under `site/` changed, so the moap
tests never run and the drift slips onto the director's window. This gate triggers on a change to
ANY of the four surfaces' source files -- crucially INCLUDING the map -- so a map-only level edit
can no longer drift a stage claim past publish.

THE SHADOW RAIL (the ruling's risk clause on the scanner change)
----------------------------------------------------------------
A NEW cross-surface scanner must not be able to WEDGE publishing on a false positive (this project
has repeatedly stalled hours on a control that false-fired -- feedback_control_false_positive_jams
_pipeline). `tools/moap_coherence_gate.mode` demotes the gate to report-only (SHADOW) INSTANTLY,
decoupling "the scanner has a bug" from "publish is wedged for hours" -- no code change, no
`--no-verify`. Default is ENFORCE: the four surfaces cohere today (Phases A-C landed clean:
0 hard mapping findings, 0 stage disagreements, 0 render drift), so there is no wedge risk to
defer against -- the rail is the escape hatch, not a permanent shadow.

R15 -- THE GATE MUST BE ABLE TO FAIL (mutation-proven in tests/tools/test_moap_coherence_gate.py)
-------------------------------------------------------------------------------------------------
Proven BOTH WAYS on each surface: inject a stage disagreement / dead-atom ref / render drift ->
ENFORCE returns 1; align the surfaces -> returns 0. The tautology killer holds the site claim
fixed and moves only an atom level -> the finding flips, proving the gate reads the MAP, not just
echoes one surface at another. Independent of the mode: SHADOW returns 0 on the SAME injected
disagreement it reports, proving the rail genuinely does not block. This module never writes the
map, the mapping or index.html -- it reads all four surfaces.

Invoked with NO args (the pre-commit hook path) it is STAGING-AWARE: it runs only when one of the
four surfaces' source files is staged (so an unrelated commit pays nothing), then ENFORCEs.
Invoked `python3 tools/moap_coherence_gate.py --report` it ignores staging and prints the full
cross-surface report (a human diagnostic; exit 1 on any finding, 0 when clean).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_SITE_DIR = ROOT / "site"
# The moap_* derivation modules live under site/ and import each other by bare name (the
# `pytest site/` rootdir convention). Put site/ on the path so this gate can reuse their queries.
if str(_SITE_DIR) not in sys.path:
    sys.path.insert(0, str(_SITE_DIR))

from moap_coherence import (  # noqa: E402
    _HARD,
    _MAP,
    _MAPPING,
    SITE,
    coherence_findings,
)
from moap_evidence import EVIDENCE_DATA, evidence_findings  # noqa: E402
from moap_render import render_findings  # noqa: E402
from moap_stage import stage_disagreements  # noqa: E402

# The four surfaces' source files. A staged change to ANY of these can drift a node's stage
# across surfaces. The MAP is the critical inclusion -- it is the surface the site-lane gate is
# blind to (that gate fires only on site/ edits). THE_MODEL_ON_A_PAGE.md is the human-readable
# model whose truth is ENCODED in the map+mapping the queries read, so gating on those two source
# files gates the model too.
MAP = "docs/design/maturity_map.yaml"
MAPPING = "site/data/moap_node_atoms.json"
DIAGRAM = "site/index.html"
# Phase E (atom SITE_evidence_pages_behind_nodes) adds a FIFTH surface: the evidence page behind
# each node and the primary-state data it renders. A change to either can dangle an anchor or
# leave the page's figures behind the map, so both join the trigger set.
EVIDENCE_PAGE = "site/evidence/index.html"
EVIDENCE_DATA_FILE = "site/data/moap_evidence.json"
TRIGGER_FILES = frozenset({MAP, MAPPING, DIAGRAM, EVIDENCE_PAGE, EVIDENCE_DATA_FILE})

MODE_FILE = ROOT / "tools" / "moap_coherence_gate.mode"
ENFORCE = "enforce"
SHADOW = "shadow"

# Finding-set surface tags (for the operator-facing report).
S_MAPPING = "map<->diagram"
S_STAGE = "map->site(declared)"
S_RENDER = "site-render"
S_EVIDENCE = "node->evidence"


def gate_mode(mode_file: Path = MODE_FILE) -> str:
    """ENFORCE by default; SHADOW only if `tools/moap_coherence_gate.mode` says so (the risk
    clause's report-only escape hatch). Any other/absent value fails SAFE to ENFORCE -- a
    malformed mode file can never silently turn the gate off (R15 fail-closed)."""
    if mode_file.is_file():
        if mode_file.read_text(encoding="utf-8").strip().lower() == SHADOW:
            return SHADOW
    return ENFORCE


def staged_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=str(ROOT), capture_output=True, text=True,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def is_triggered(files: list[str]) -> bool:
    """True if any of the four surfaces' source files is in this change set -- INCLUDING the map,
    which the site-lane gate never sees."""
    return any(f in TRIGGER_FILES for f in files)


def gather_findings(
    site: Path = SITE,
    map_path: Path = _MAP,
    mapping_path: Path = _MAPPING,
    evidence_data_path: Path = EVIDENCE_DATA,
) -> list[tuple[str, str, str, str]]:
    """The union of the four ready-made BLOCKING query sets across the five surfaces, each
    normalized to (surface, kind, subject, detail):
      * Phase A mapping integrity (HARD kinds only -- ORPHAN_ATOM is the soft §5 backlog, excluded)
      * Phase B declared-vs-computed stage disagreements (map/model vs the site's hand-set stage)
      * Phase C rendered-vs-computed drift (the front-door HTML word vs the computed stage)
      * Phase E node->evidence (a non-trivially-staged node with no evidence page, a dangling
        anchor, an evidence record that substantiates nothing, figures that have fallen behind
        the map, or a claim the node's own evidence computes differently)
    Empty means all five surfaces agree, and every claim can be walked to the state behind it."""
    out: list[tuple[str, str, str, str]] = []
    for kind, subject, detail in coherence_findings(site, map_path, mapping_path):
        if kind in _HARD:
            out.append((S_MAPPING, kind, subject, detail))
    for d in stage_disagreements(map_path, mapping_path):
        out.append(
            (S_STAGE, "STAGE_DISAGREEMENT", str(d["name"]),
             f"declared={d['declared_stage']!r} computed={d['computed_stage']!r}")
        )
    for kind, node, detail in render_findings(site, map_path, mapping_path):
        out.append((S_RENDER, kind, node, detail))
    for kind, subject, detail in evidence_findings(
        site, map_path, mapping_path, evidence_data_path
    ):
        out.append((S_EVIDENCE, kind, subject, detail))
    return out


def decide(findings: list[tuple[str, str, str, str]], mode: str) -> int:
    """The pure gate decision, isolated from git/staging so it is mutation-testable:
      * no findings          -> 0 (surfaces cohere)
      * findings, ENFORCE    -> 1 (COMMIT REFUSED)
      * findings, SHADOW     -> 0 (report-only rail -- NEVER blocks, whatever the findings)
    Prints the finding list either way so drift is visible in the commit output."""
    if not findings:
        print("[moap-coherence] ✓ model/diagram/site/map cohere on every node's stage")
        return 0
    sys.stderr.write(
        f"\n[moap-coherence] {len(findings)} cross-surface stage disagreement(s):\n"
    )
    for surface, kind, subject, detail in findings:
        sys.stderr.write(f"  [{surface}] {kind} {subject!r}: {detail}\n")
    if mode == SHADOW:
        sys.stderr.write(
            "[moap-coherence] SHADOW mode (tools/moap_coherence_gate.mode) -- REPORTING ONLY, "
            "commit NOT blocked. Flip the mode file back to enforce once the scanner is trusted.\n"
        )
        return 0
    sys.stderr.write(
        "\n[moap-coherence] ❌ COMMIT REFUSED (§6 coherence-by-derivation, Phase D). A node's "
        "Live/Building/Planned stage must agree across the model, the diagram, the site and the "
        "map. Fix the drift (usually: the site/mapping over-claims a node whose atoms are below "
        "target, or an atom level moved) then commit. To de-fang a scanner false-positive without "
        "wedging publish, write 'shadow' to tools/moap_coherence_gate.mode.\n"
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--report" in argv:
        # Human diagnostic: ignore staging, report across all four surfaces, exit 1 on any finding.
        return decide(gather_findings(), ENFORCE)
    files = staged_files()
    if not is_triggered(files):
        # No cross-surface source file staged -- nothing this gate can be responsible for.
        return 0
    return decide(gather_findings(), gate_mode())


if __name__ == "__main__":
    sys.exit(main())
