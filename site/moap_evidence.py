#!/usr/bin/env python3
"""Coherence-by-derivation (§6) -- PHASE E: the EVIDENCE PAGE behind every diagram node.

Atom: SITE_evidence_pages_behind_nodes. Phase A (moap_coherence) fixed the node->atom mapping,
Phase B (moap_stage) COMPUTES each node's stage from its atoms' levels, Phase C (moap_render)
proved the front door RENDERS that computed stage, Phase D (tools/moap_coherence_gate) REFUSES a
commit when those surfaces disagree. All four are about the STAGE WORD. None of them requires
that a reader can walk a node to the evidence UNDERNEATH the word.

Phase E is that requirement, and it is the atom's three exit criteria expressed as one query set:

  (1) NO DANGLING ANCHOR. Every front-door node whose rendered stage is NON-TRIVIAL (it claims
      something exists NOW -- 'Live' or 'Building'; 'Planned' claims nothing) must carry an
      evidence link, and that link's #fragment must name a node record that the evidence page
      will actually render.

  (2) PRIMARY-STATE EVIDENCE, NOT RESTATED PROSE. The record behind the anchor must carry real
      figures derived from primary state, and those figures must still AGREE with primary state
      -- a stale or hand-edited moap_evidence.json is a finding, so the page cannot become a
      second, drifting home for the numbers. A node claiming a non-trivial stage whose record
      substantiates it with NOTHING (no atom, no recorded level move, no fidelity row, no test
      function) is a page of words and fails.

  (3) A CLAIM ITS EVIDENCE CANNOT SUPPORT FAILS. The stage word the front door renders is
      compared against the stage the EVIDENCE PAGE's own rows compute. Claim over evidence ->
      finding -> (via tools/moap_coherence_gate, Phase D) commit refused, and (via
      tests/tools/test_moap_evidence_gate.py, which runs under the `tests/` publish root)
      publish refused.

R15 -- THE INDEPENDENCE THAT MAKES THIS FALSIFIABLE (the tautology killer)
--------------------------------------------------------------------------
The CLAIM and the EVIDENCE come from different files and are never allowed to touch:

    claim     <- the hand-typed stage word in site/index.html  (and declared_stage in the mapping)
    evidence  <- site/data/moap_evidence.json, whose atom levels are re-checked here against a
                 fresh read of docs/design/maturity_map.yaml

`claimed_stage` is carried through the evidence data purely so a reader sees the contrast; it is
NEVER an input to any derived value. So moving an atom's level in the map, with the site untouched,
flips the verdict -- proving the gate reads the map, not the claim (mutation-proven in
site/test_moap_evidence.py and tests/tools/test_moap_evidence_gate.py, both ways).

FAIL-OPEN and FAIL-SILENT are findings, never passes: a missing evidence page, a missing/empty/
malformed evidence data file, a node with no record, and an exception inside the checker itself
all RETURN A FINDING. An unavailable check is a FAILED check.

Run standalone for the report:  python3 site/moap_evidence.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

from moap_coherence import _MAP, _MAPPING, load_mapping
from moap_render import rendered_stages
from moap_stage import compute_stage, map_atom_levels

SITE = Path(__file__).resolve().parent
EVIDENCE_PAGE = SITE / "evidence" / "index.html"
EVIDENCE_DATA = SITE / "data" / "moap_evidence.json"

# A stage word that claims the thing EXISTS NOW. 'Planned' claims nothing, so it needs no
# evidence page -- that is the atom's own "non-trivial claimed stage" wording, made mechanical.
NON_TRIVIAL_STAGES = frozenset({"Live", "Building"})

# Finding kinds. Every one of these BLOCKS -- there is no soft kind in Phase E.
FRONT_DOOR_MISSING = "FRONT_DOOR_MISSING"
EVIDENCE_PAGE_MISSING = "EVIDENCE_PAGE_MISSING"
EVIDENCE_DATA_UNUSABLE = "EVIDENCE_DATA_UNUSABLE"
NODE_NO_EVIDENCE_LINK = "NODE_NO_EVIDENCE_LINK"
EVIDENCE_ANCHOR_DANGLING = "EVIDENCE_ANCHOR_DANGLING"
NODE_EVIDENCE_EMPTY = "NODE_EVIDENCE_EMPTY"
EVIDENCE_DATA_STALE = "EVIDENCE_DATA_STALE"
EVIDENCE_STAGE_UNSUPPORTED = "EVIDENCE_STAGE_UNSUPPORTED"
EVIDENCE_CHECK_UNAVAILABLE = "EVIDENCE_CHECK_UNAVAILABLE"

# Front-door node parsing. The NODE NAME span is the anchor of each segment (the same span
# moap_coherence/moap_render key off, so all of Phase A/C/E see the same node set), and a node's
# segment runs to the NEXT node name -- never to a div boundary, so the parse does not depend on
# the diagram's markup scaffolding. Split-based rather than one mega-regex on purpose: a regex
# REQUIRING the evidence link would silently drop exactly the defective node, which is the
# fail-open shape this gate exists to catch. `_NODES_CLOSE` bounds the LAST segment so it cannot
# borrow an unrelated evidence link from further down the page and read as green.
_NAME_SPLIT = '<span class="node-name">'
_NODES_CLOSE = "</section>"
_NAME_END = re.compile(r"(?P<name>.*?)</span>", re.DOTALL)
_STAGE = re.compile(r'<span class="stage stage-\w+">(?P<stage>Live|Building|Planned)</span>')
_EVIDENCE_HREF = re.compile(
    r'<a[^>]*class="node-evidence"[^>]*href=(["\'])(?P<href>[^"\']+)\1', re.IGNORECASE
)


def front_door_nodes(site: Path = SITE) -> list[dict]:
    """[{name, stage, evidence_href}] for every front-door diagram node, in document order.
    `evidence_href` is None when the node carries no evidence link at all (criterion 1's
    dangling case). Names are entity-decoded to the mapping's plain-text convention."""
    front = site / "index.html"
    if not front.is_file():
        return []
    text = front.read_text(encoding="utf-8")
    segments = text.split(_NAME_SPLIT)[1:]
    nodes: list[dict] = []
    for i, segment in enumerate(segments):
        if i == len(segments) - 1:
            segment = segment.split(_NODES_CLOSE, 1)[0]
        m_name = _NAME_END.match(segment)
        m_stage = _STAGE.search(segment)
        if not m_name or not m_stage:
            continue
        m_href = _EVIDENCE_HREF.search(segment)
        nodes.append(
            {
                "name": html.unescape(m_name.group("name")).strip(),
                "stage": m_stage.group("stage"),
                "evidence_href": m_href.group("href") if m_href else None,
            }
        )
    return nodes


def load_evidence_data(path: Path = EVIDENCE_DATA) -> dict | None:
    """The derived evidence data, or None when it is missing/empty/malformed/node-less. None is
    a FINDING at every call site -- never a silent pass (R15 FAIL-OPEN guard: an absent or empty
    evidence file must not read as 'nothing wrong')."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return None
    return data


def _anchor_of(href: str) -> str:
    return href.split("#", 1)[1] if "#" in href else ""


def evidence_findings(
    site: Path = SITE,
    map_path: Path = _MAP,
    mapping_path: Path = _MAPPING,
    data_path: Path = EVIDENCE_DATA,
    page_path: Path | None = None,
) -> list[tuple[str, str, str]]:
    """Every Phase-E finding as (kind, subject, detail). Empty means: every non-trivially-staged
    front-door node walks to an evidence record that exists, is derived from current primary
    state, carries real substantiating figures, and computes the stage the front door claims."""
    page_path = page_path or (site / "evidence" / "index.html")
    findings: list[tuple[str, str, str]] = []
    try:
        return _evidence_findings(site, map_path, mapping_path, data_path, page_path)
    except Exception as exc:  # noqa: BLE001 -- an unavailable check is a FAILED check (R15)
        findings.append(
            (
                EVIDENCE_CHECK_UNAVAILABLE,
                "phase-e",
                f"the evidence check itself could not run ({type(exc).__name__}: {exc}) -- "
                "treated as a FAILURE, never a pass",
            )
        )
        return findings


def _evidence_findings(
    site: Path, map_path: Path, mapping_path: Path, data_path: Path, page_path: Path
) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []

    if not (site / "index.html").is_file():
        findings.append((FRONT_DOOR_MISSING, "site/index.html", "no front door to read node claims from"))
        return findings
    if not page_path.is_file():
        findings.append(
            (EVIDENCE_PAGE_MISSING, str(page_path.name), f"the evidence page is absent at {page_path}")
        )
        return findings

    data = load_evidence_data(data_path)
    if data is None:
        findings.append(
            (
                EVIDENCE_DATA_UNUSABLE,
                str(data_path.name),
                "the derived evidence data is missing, empty, malformed or carries no nodes -- "
                "the evidence page would render nothing",
            )
        )
        return findings

    # R15 FAIL-SILENT guard on the PARSER itself. Phase C's independent scan of the same front
    # door (moap_render.rendered_stages) is the second opinion: if it can see stage-bearing nodes
    # and this parser cannot, the check has gone blind and every node would vacuously pass. Blind
    # is a FAILURE, never a green.
    parsed = front_door_nodes(site)
    if rendered_stages(site) and not parsed:
        findings.append(
            (EVIDENCE_CHECK_UNAVAILABLE, "front-door parser",
             "the front door renders stage-bearing nodes that this check cannot parse -- the "
             "evidence check has gone blind and is treated as FAILED, never as green")
        )
        return findings

    by_anchor = {n.get("anchor"): n for n in data["nodes"] if isinstance(n, dict)}
    mapping = load_mapping(mapping_path)
    name_to_id = {
        n.get("name", n.get("id")): n.get("id") for n in mapping.get("nodes", [])
    }
    live_levels = map_atom_levels(map_path)

    for node in parsed:
        name, stage = node["name"], node["stage"]
        if stage not in NON_TRIVIAL_STAGES:
            continue  # a 'Planned' node claims nothing; nothing to substantiate.

        href = node["evidence_href"]
        if not href:
            findings.append(
                (NODE_NO_EVIDENCE_LINK, name,
                 f"renders {stage!r} but carries no evidence link -- the claim cannot be walked to its evidence")
            )
            continue

        anchor = _anchor_of(href)
        record = by_anchor.get(anchor)
        if record is None:
            findings.append(
                (EVIDENCE_ANCHOR_DANGLING, name,
                 f"evidence link {href!r} names anchor {anchor!r}, which the evidence page renders no section for")
            )
            continue

        # Criterion 2a -- the record must actually SUBSTANTIATE, not merely exist.
        totals = record.get("totals") or {}
        substantiating = sum(
            int(totals.get(k) or 0)
            for k in ("ledger_records", "fidelity_rows", "test_functions")
        )
        if not (record.get("atoms") or []) or substantiating <= 0:
            findings.append(
                (NODE_EVIDENCE_EMPTY, name,
                 f"renders {stage!r} but its evidence record carries no substantiating figure "
                 f"(atoms={len(record.get('atoms') or [])}, level moves+fidelity rows+test functions={substantiating})")
            )
            continue

        # Criterion 2b -- the rendered figures must still agree with PRIMARY STATE. This is what
        # stops the evidence page becoming a second, drifting home for the numbers.
        stale = []
        for row in record["atoms"]:
            atom_id = row.get("id")
            truth = live_levels.get(atom_id)
            if truth is None:
                stale.append(f"{atom_id}: absent from the maturity map")
                continue
            if (row.get("level_current"), row.get("level_target")) != (truth["current"], truth["target"]):
                stale.append(
                    f"{atom_id}: page shows {row.get('level_current')}/{row.get('level_target')}, "
                    f"map says {truth['current']}/{truth['target']}"
                )
        if stale:
            findings.append(
                (EVIDENCE_DATA_STALE, name,
                 "the evidence page's figures no longer match the maturity map -- regenerate "
                 "site/data/moap_evidence.json: " + "; ".join(stale[:4]))
            )
            continue

        # Criterion 3 -- the CLAIM against what the page's own evidence rows compute. The two
        # sides come from different files (index.html vs the derived data); neither feeds the other.
        evidence_stage = compute_stage(
            [
                {"current": r.get("level_current", 0), "target": r.get("level_target", 1)}
                for r in record["atoms"]
            ]
        )
        if stage != evidence_stage:
            findings.append(
                (EVIDENCE_STAGE_UNSUPPORTED, name,
                 f"the front door claims {stage!r} but this node's evidence computes {evidence_stage!r} "
                 f"({totals.get('at_target')} of {totals.get('atoms')} atoms at target)")
            )

        # A node the mapping does not know is a Phase-A defect, gated there; noted only if the
        # anchor and the mapping disagree about which node this is.
        expected = name_to_id.get(name)
        if expected is not None and anchor != f"node-{expected}":
            findings.append(
                (EVIDENCE_ANCHOR_DANGLING, name,
                 f"evidence link points at {anchor!r} but this node is {expected!r} in the mapping")
            )

    return findings


def main() -> int:
    findings = evidence_findings()
    print("=== §6 coherence-by-derivation -- Phase E: evidence pages behind the diagram nodes ===\n")
    nodes = front_door_nodes()
    data = load_evidence_data()
    records = {n.get("anchor"): n for n in (data or {}).get("nodes", [])}
    print(f"{'node':22s} {'claims':10s} {'evidence':10s}  anchor")
    for node in nodes:
        anchor = _anchor_of(node["evidence_href"] or "")
        rec = records.get(anchor)
        ev = "(none)"
        if rec:
            ev = compute_stage(
                [{"current": r.get("level_current", 0), "target": r.get("level_target", 1)}
                 for r in rec.get("atoms", [])]
            )
        print(f"{node['name']:22s} {node['stage']:10s} {ev:10s}  {anchor or '(no evidence link)'}")
    print(f"\nPHASE-E findings (publish would FAIL here): {len(findings)}")
    for kind, subject, detail in findings:
        print(f"  [{kind}] {subject}: {detail}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
