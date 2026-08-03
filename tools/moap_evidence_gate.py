#!/usr/bin/env python3
"""PUBLISH GATE for the model-on-a-page evidence pages (atom ``SITE_evidence_pages_behind_nodes``).

WHAT IT REFUSES TO PUBLISH
--------------------------
Three named defects, each an exit criterion of the atom:

  1. ``NO_EVIDENCE_PAGE``       -- a node making a non-trivial claim ("Live"/"Building") that
                                   walks to nothing: no ``evidence_href``, or an href resolving
                                   to no file. THE DANGLING ANCHOR.
  2. ``EVIDENCE_*_DRIFT``       -- a page whose RENDERED figures no longer equal the values
                                   derived from primary state (the node's stage word, or any
                                   atom's level). A stale page is restated prose.
  3. ``DECLARED_STAGE_DRIFT``   -- a node CLAIMING a stage the derivation does not support.
                                   This is the R15 headline: mutate a node to claim "Live"
                                   while an atom sits below target and this fires.

R15 -- THE THREE KILLER PATTERNS, EXPLICITLY GUARDED
----------------------------------------------------
TAUTOLOGY: the gate never reads the generator's own output as its expectation. The EXPECTED
values come from ``docs/design/maturity_map.yaml`` (via ``tools/moap_evidence.py``); the ACTUAL
values are parsed back out of the RENDERED HTML. Two independent sources that can disagree --
and the whole point is that they do the moment the map moves and the page is not regenerated.

FAIL-OPEN: a missing page, a missing ``evidence_href``, an empty page, a page with zero atom
rows, or a node with zero atoms is a FINDING, never a skip. There is no code path in which
"nothing to check" reads as "check passed".

FAIL-SILENT: if the derivation itself cannot be read (map absent, mapping corrupt, ledger
gone) the gate emits ``DERIVATION_UNAVAILABLE`` and FAILS. An unavailable check is a failed
check, never a skipped one.

NO PINNED GENERATED VALUES: the gate asserts RELATIONSHIPS (rendered stage == derived stage;
rendered level == map level; every mapped atom has a row) and never a literal figure. A pinned
generated value in a control caused a four-day publish blackout once already.

WIRING
------
It reaches the publish gate through ``tests/tools/test_site_evidence_pages.py``, which lives
under ``tests/`` and carries no ``operational`` marker -- so it is inside
``background/process_run_complete.publish_gate_pytest_argv("tests/")``'s blocking scope, and
inside ``tools/site_lane_gate.py``'s broad trigger whenever ``site/**`` changes.

Run standalone::

    python3 tools/moap_evidence_gate.py      # exit 1 on any finding
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Sibling-module import without a tools package (the tools/ convention -- see
# level_promotion_gate.py), so this module works imported by path or run directly.
_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from moap_evidence import (  # noqa: E402  (sibling module, same directory)
    MAP_PATH,
    MAPPING_PATH,
    REPO_ROOT,
    DerivationUnavailable,
    evidence_model,
)

SITE_ROOT = REPO_ROOT / "site"

# ---- finding kinds -----------------------------------------------------------------------
DERIVATION_UNAVAILABLE = "DERIVATION_UNAVAILABLE"
NO_EVIDENCE_PAGE = "NO_EVIDENCE_PAGE"
EVIDENCE_PAGE_UNREADABLE = "EVIDENCE_PAGE_UNREADABLE"
EVIDENCE_PAGE_EMPTY = "EVIDENCE_PAGE_EMPTY"
EVIDENCE_STAGE_DRIFT = "EVIDENCE_STAGE_DRIFT"
DECLARED_STAGE_DRIFT = "DECLARED_STAGE_DRIFT"
EVIDENCE_ATOM_MISSING = "EVIDENCE_ATOM_MISSING"
EVIDENCE_ATOM_UNMAPPED = "EVIDENCE_ATOM_UNMAPPED"
EVIDENCE_LEVEL_DRIFT = "EVIDENCE_LEVEL_DRIFT"
NODE_HAS_NO_ATOMS = "NODE_HAS_NO_ATOMS"
EVIDENCE_INDEX_MISSING_NODE = "EVIDENCE_INDEX_MISSING_NODE"
FRONT_DOOR_EVIDENCE_LINK_MISSING = "FRONT_DOOR_EVIDENCE_LINK_MISSING"

# ---- the RENDERED-MARKUP contract --------------------------------------------------------
# The gate parses the values a reader actually sees (R11: verify to the rendered value), so
# these patterns deliberately target visible cell/word content, never a data- attribute or an
# HTML comment. tools/generate_evidence_pages.py emits markup satisfying them; if it ever
# stops, the gate reports EVIDENCE_PAGE_EMPTY/UNREADABLE rather than passing vacuously.
_STAGE_WORD = re.compile(r'<span class="ev-stage-word">\s*(Live|Building|Planned)\s*</span>')
_NODE_ID = re.compile(r'<code class="ev-node-id">\s*([A-Za-z0-9_]+)\s*</code>')
_ATOM_ROW = re.compile(r'<tr class="ev-atom"[^>]*>(.*?)</tr>', re.DOTALL)
_ROW_ID = re.compile(r'<code class="ev-atom-id">\s*([A-Za-z0-9_]+)\s*</code>')
_ROW_LEVEL = re.compile(r'<td class="ev-atom-level">\s*(\d+)\s*/\s*(\d+)\s*</td>')

# ---- front-door wiring state -------------------------------------------------------------
# The front door (site/index.html) is where a reader MEETS the diagram, so the last mile of
# criterion (1) is a per-node evidence link in each .node block. That file was outside this
# build's write scope, so the check ships here READY and OFF, and
# tests/tools/test_site_evidence_pages.py asserts this flag agrees with the real front door --
# add the links and that test goes RED until the flag is flipped, so the wiring can never land
# with its own gate silently disabled (a fail-open by omission).
FRONT_DOOR_LINKS_REQUIRED = False

Finding = tuple[str, str, str]


def _page_path(node_id: str, site_root: Path) -> Path:
    return site_root / "evidence" / node_id / "index.html"


def _href_target(href: str, site_root: Path) -> Path | None:
    """Resolve a node's ``evidence_href`` to a file on disk, or None if it is not a
    site-internal page reference. Site-absolute (``/evidence/x/``) is the canonical form."""
    if not href or not isinstance(href, str):
        return None
    clean = href.split("?", 1)[0].split("#", 1)[0].strip()
    if not clean or "://" in clean:
        return None
    clean = clean.lstrip("/")
    target = site_root / clean
    if clean.endswith("/") or not Path(clean).suffix:
        target = target / "index.html"
    return target


def evidence_index_findings(model: dict, site_root: Path) -> list[Finding]:
    """The evidence index must link every node page -- so the set is walkable as a whole and a
    generated-then-orphaned page cannot hide."""
    index = site_root / "evidence" / "index.html"
    if not index.is_file():
        return [(NO_EVIDENCE_PAGE, "evidence index", f"missing {index}")]
    try:
        text = index.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [(EVIDENCE_PAGE_UNREADABLE, "evidence index", str(exc))]
    out: list[Finding] = []
    for node in model["nodes"]:
        if f'href="./{node["id"]}/"' not in text and f'href="/evidence/{node["id"]}/"' not in text:
            out.append(
                (EVIDENCE_INDEX_MISSING_NODE, node["id"], "evidence index does not link this node's page")
            )
    return out


def front_door_findings(model: dict, site_root: Path = SITE_ROOT) -> list[Finding]:
    """Every non-trivial diagram node on the FRONT DOOR carries a link to its evidence page.

    Held out of the default hard set until the front-door links land (see
    FRONT_DOOR_LINKS_REQUIRED); the function itself is live and mutation-tested now."""
    front = site_root / "index.html"
    if not front.is_file():
        return [(FRONT_DOOR_EVIDENCE_LINK_MISSING, "front door", f"missing {front}")]
    try:
        text = front.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [(FRONT_DOOR_EVIDENCE_LINK_MISSING, "front door", str(exc))]
    out: list[Finding] = []
    for node in model["nodes"]:
        if not node["non_trivial"]:
            continue
        nid = node["id"]
        if f'href="./evidence/{nid}/"' not in text and f'href="/evidence/{nid}/"' not in text:
            out.append(
                (
                    FRONT_DOOR_EVIDENCE_LINK_MISSING,
                    node["name"],
                    f"front-door node links no evidence page (expected href ./evidence/{nid}/)",
                )
            )
    return out


def node_findings(node: dict, site_root: Path) -> list[Finding]:
    """Every defect in ONE node's claim-to-evidence chain."""
    out: list[Finding] = []
    name = node["name"]

    # (a) The CLAIM must agree with the DERIVATION. Independent sources: `declared_stage` is
    #     hand-authored in the mapping, `computed_stage` is derived from the map's levels.
    if node["declared_stage"] is not None and node["declared_stage"] != node["computed_stage"]:
        out.append(
            (
                DECLARED_STAGE_DRIFT,
                name,
                f"node claims stage {node['declared_stage']!r} but its atoms derive "
                f"{node['computed_stage']!r} ({node['atoms_at_target']}/{node['atom_count']} at target)",
            )
        )

    # (b) FAIL-OPEN guard: an atom-less node derives PLANNED and would otherwise escape every
    #     check below by claiming nothing. A diagram node backed by nothing is itself a defect.
    if node["atom_count"] == 0:
        out.append((NODE_HAS_NO_ATOMS, name, "node maps to no atom -- nothing can evidence its stage"))

    if not node["non_trivial"]:
        # A genuinely Planned node claims no present-tense capability; it needs no evidence page.
        return out

    # (c) NO DANGLING ANCHOR: the node must resolve to a page that exists.
    href = node.get("evidence_href")
    target = _href_target(href, site_root)
    fallback = _page_path(node["id"], site_root)
    if not href:
        out.append(
            (NO_EVIDENCE_PAGE, name, f"claims stage {node['computed_stage']!r} but declares no evidence_href")
        )
        target = fallback
    if target is None:
        out.append((NO_EVIDENCE_PAGE, name, f"evidence_href {href!r} is not a site-internal page reference"))
        return out
    if not target.is_file():
        out.append(
            (NO_EVIDENCE_PAGE, name, f"evidence_href {href!r} resolves to no page ({target})")
        )
        return out

    try:
        html_text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        out.append((EVIDENCE_PAGE_UNREADABLE, name, f"{target}: {exc}"))
        return out

    # (d) The page must be the page for THIS node, and must render a stage word at all.
    rendered_node = _NODE_ID.search(html_text)
    if rendered_node is None or rendered_node.group(1) != node["id"]:
        out.append(
            (
                EVIDENCE_PAGE_UNREADABLE,
                name,
                f"{target} renders no ev-node-id for {node['id']!r} "
                f"(found {rendered_node.group(1) if rendered_node else None!r})",
            )
        )
        return out
    stage_match = _STAGE_WORD.search(html_text)
    if stage_match is None:
        out.append((EVIDENCE_PAGE_UNREADABLE, name, f"{target} renders no stage word"))
        return out
    if stage_match.group(1) != node["computed_stage"]:
        out.append(
            (
                EVIDENCE_STAGE_DRIFT,
                name,
                f"page renders stage {stage_match.group(1)!r} but the derivation says "
                f"{node['computed_stage']!r} -- page is stale or over-claims",
            )
        )

    # (e) The page must render PRIMARY STATE, not prose: one row per mapped atom, each showing
    #     the level the map actually holds.
    rendered_levels: dict[str, tuple[int, int]] = {}
    for block in _ATOM_ROW.findall(html_text):
        rid = _ROW_ID.search(block)
        rlv = _ROW_LEVEL.search(block)
        if rid and rlv:
            rendered_levels[rid.group(1)] = (int(rlv.group(1)), int(rlv.group(2)))
    if not rendered_levels:
        out.append(
            (
                EVIDENCE_PAGE_EMPTY,
                name,
                f"{target} renders no atom evidence rows -- prose without primary state",
            )
        )
        return out

    for atom in node["atoms"]:
        got = rendered_levels.get(atom["id"])
        if got is None:
            out.append(
                (EVIDENCE_ATOM_MISSING, name, f"page renders no evidence row for atom {atom['id']!r}")
            )
            continue
        want = (atom["level_current"], atom["level_target"])
        if got != want:
            out.append(
                (
                    EVIDENCE_LEVEL_DRIFT,
                    name,
                    f"atom {atom['id']!r}: page renders level {got[0]}/{got[1]} but the maturity "
                    f"map holds {want[0]}/{want[1]}",
                )
            )
    mapped = {a["id"] for a in node["atoms"]}
    for extra in sorted(set(rendered_levels) - mapped):
        out.append(
            (EVIDENCE_ATOM_UNMAPPED, name, f"page renders atom {extra!r} that the node does not map")
        )
    return out


def gate_findings(
    site_root: Path = SITE_ROOT,
    map_path: Path = MAP_PATH,
    mapping_path: Path = MAPPING_PATH,
    model: dict | None = None,
    **model_kwargs,
) -> list[Finding]:
    """Every publish-blocking defect across the model-on-a-page evidence surface.

    Empty means: every non-trivially-claimed node walks to a page that exists, that page is
    the page for that node, and every figure it renders equals the value derived from primary
    state right now.
    """
    if model is None:
        try:
            model = evidence_model(
                map_path=map_path,
                mapping_path=mapping_path,
                with_git=False,
                with_tests=False,
                **model_kwargs,
            )
        except DerivationUnavailable as exc:
            # FAIL-SILENT guard: the checker could not read its own inputs -> FAILED, not skipped.
            return [(DERIVATION_UNAVAILABLE, "primary state", str(exc))]
    findings: list[Finding] = []
    for node in model["nodes"]:
        findings.extend(node_findings(node, site_root))
    findings.extend(evidence_index_findings(model, site_root))
    if FRONT_DOOR_LINKS_REQUIRED:
        findings.extend(front_door_findings(model, site_root))
    return findings


def main() -> int:
    findings = gate_findings()
    print("=== model-on-a-page evidence-page publish gate ===\n")
    if not findings:
        print("PASS -- every non-trivially-claimed node walks to a page whose rendered figures")
        print("        equal the values derived from primary state.")
        return 0
    print(f"FAIL -- {len(findings)} finding(s):")
    for kind, subject, detail in findings:
        print(f"  [{kind}] {subject}: {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
