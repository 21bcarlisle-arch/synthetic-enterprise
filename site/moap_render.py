#!/usr/bin/env python3
"""Coherence-by-derivation (§6) -- PHASE C: the SITE renders from the derivation.

Director ruling DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27, deliverable §6:
the MODEL, the DIAGRAM, the SITE and the MAP "must not be kept in sync by hand; three of
them must be derived from one." Phase A (moap_coherence) fixed the node->atom mapping; Phase B
(moap_stage) COMPUTES each node's Live/Building/Planned stage from its atoms' real levels.
Phase C closes the loop on the SITE: the stage word RENDERED in the front-door diagram
(site/index.html .node-head) must EQUAL the computed stage. A node can no longer hand-type
'Live' while its atoms sit below target.

This makes the editorial reading rule MECHANICAL. The front door speaks in the present tense
-- a node's stage word is a claim that the thing EXISTS NOW ('Live' = every mapped atom at
target). render_findings() surfaces every node whose rendered claim OUTRUNS its atoms (site
says 'Live', atoms compute 'Building' -- the dangerous, over-claiming direction) or LAGS them
(site says 'Building', atoms compute 'Live'). Both are drift; both were previously a human's
job to catch on every edit.

Independence (R15 / LAW C -- the tautology killer): the rendered stage is HAND-TYPED HTML in
index.html; the computed stage is derived from docs/design/maturity_map.yaml -- two independent
sources. They can (and must be able to) DISAGREE; render_findings() is exactly that
disagreement set for the site surface. Phase C REPORTS+tests it, and the site test suite that
runs at publish asserts the real front door renders exactly the derivation. The DEDICATED
publish-gate hook across model/diagram/site/map WITH its shadow rail is Phase D (its own atom +
commit). This module never writes index.html or the map -- it reads both.

Run standalone for the site-render report:  python3 site/moap_render.py
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from moap_stage import BUILDING, LIVE, PLANNED, _MAP, _MAPPING, node_stages

SITE = Path(__file__).resolve().parent

# The front-door .node-head carries the node NAME then its rendered STAGE word, e.g.:
#   <span class="node-name">The company</span><span class="stage stage-building">Building</span>
# Both spans in one head; whitespace between them is tolerated. DOTALL so an entity-laden name
# (which never actually spans lines today) can never silently drop a node from the scan.
_NODE_HEAD = re.compile(
    r'<span class="node-name">(?P<name>.*?)</span>\s*'
    r'<span class="stage stage-\w+">(?P<stage>Live|Building|Planned)</span>',
    re.DOTALL,
)

STAGE_RENDER_DRIFT = "STAGE_RENDER_DRIFT"

# Present-tense strength ordering: a bigger rank is a STRONGER claim that the thing exists now.
# Used only to name the drift DIRECTION (outrun vs lag) -- the finding fires on any inequality.
_RANK = {PLANNED: 0, BUILDING: 1, LIVE: 2}


def rendered_stages(site: Path = SITE) -> dict[str, str]:
    """{front-door node name -> the stage word RENDERED in its .node-head}. Names are
    entity-decoded so they compare equal to the mapping's plain-text names ('Governance &
    method', not 'Governance &amp; method') -- the moap_coherence.diagram_node_names convention."""
    front = site / "index.html"
    if not front.is_file():
        return {}
    return {
        html.unescape(m.group("name")).strip(): m.group("stage").strip()
        for m in _NODE_HEAD.finditer(front.read_text(encoding="utf-8"))
    }


def render_findings(
    site: Path = SITE, map_path: Path = _MAP, mapping_path: Path = _MAPPING
) -> list[tuple[str, str, str]]:
    """Every front-door node whose RENDERED stage word disagrees with the stage COMPUTED from
    its atoms' real levels, as (kind, node, detail). Empty means the site renders exactly the
    derivation -- the present-tense reading rule is then mechanically satisfied, not an editorial
    chore. A node rendering a stage AHEAD of its atoms OUTRUNS (over-claims -- the direction the
    front door must never take); one rendering BEHIND LAGS (under-claims). Both surfaced.

    A rendered node absent from the mapping is a Phase-A coherence defect (DIAGRAM_NODE_UNMAPPED,
    gated in moap_coherence); it is skipped here so the same drift is not reported twice."""
    computed = {s["name"]: s["computed_stage"] for s in node_stages(map_path, mapping_path)}
    findings: list[tuple[str, str, str]] = []
    for name, rendered in rendered_stages(site).items():
        want = computed.get(name)
        if want is None:
            continue
        if rendered != want:
            direction = "OUTRUNS" if _RANK.get(rendered, -1) > _RANK.get(want, -1) else "LAGS"
            findings.append(
                (
                    STAGE_RENDER_DRIFT,
                    name,
                    f"site renders {rendered!r} but atoms compute {want!r} ({direction})",
                )
            )
    return findings


def main() -> int:
    findings = render_findings()
    print("=== §6 coherence-by-derivation -- Phase C: site renders from the derivation ===\n")
    rendered = rendered_stages()
    computed = {s["name"]: s["computed_stage"] for s in node_stages()}
    print(f"{'node':22s} {'rendered':10s} {'computed':10s}")
    for name, r in rendered.items():
        c = computed.get(name, "(unmapped)")
        flag = "" if r == c else "  <-- DRIFT"
        print(f"{name:22s} {r:10s} {c:10s}{flag}")
    print(
        f"\nSTAGE_RENDER_DRIFT (site claim != computed -- Phase D's publish gate fails here): "
        f"{len(findings)}"
    )
    for kind, node, detail in findings:
        print(f"  [{kind}] {node}: {detail}")
    # Standalone report exits 1 on drift (the moap_coherence Phase-A convention); the DEDICATED
    # publish-gate wiring across all four surfaces is Phase D.
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
