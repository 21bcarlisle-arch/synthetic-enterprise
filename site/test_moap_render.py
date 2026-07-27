"""R15 mechanism self-test for §6 coherence-by-derivation -- PHASE C (the SITE renders from the
derivation). Same two-role pattern as test_moap_stage.py / test_moap_coherence.py:

  1. MECHANISM self-tests (R15 BOTH WAYS): synthetic (index.html, mapping, map) fixtures prove
     render_findings() FIRES when the rendered stage word disagrees with the computed stage --
     both when the site OUTRUNS its atoms (renders 'Live', atoms compute 'Building') and when it
     LAGS -- and is CLEAN when the rendered word matches. Two INDEPENDENT flip paths: change the
     rendered HTML word (holding atoms fixed), OR change an atom's level (holding the rendered
     word fixed). The second path is the tautology killer -- it proves the check reads the map,
     not merely echoes the HTML back at itself.
  2. LIVE GATE: the real front door (site/index.html) renders exactly the derivation -- every
     node's stage word equals its computed stage (render_findings() is empty). This is the
     property that fails the suite at publish if a future edit lets a node over-claim.

Phase D (the dedicated publish-gate hook across model/diagram/site/map with its shadow rail) is
its own atom + test. Phase C REPORTS the drift and this suite asserts the real site is clean.
"""
import json
import tempfile
from pathlib import Path

from moap_render import STAGE_RENDER_DRIFT, render_findings, rendered_stages

_HEAD = (
    '<div class="node-head"><span class="node-name">{name}</span>'
    '<span class="stage stage-{cls}">{stage}</span></div>'
)
_CLS = {"Live": "live", "Building": "building", "Planned": "planned"}


def _index(nodes_rendered):
    """A minimal front-door <div class="nodes"> for [(name, stage_word)] renders."""
    heads = "\n".join(
        _HEAD.format(name=n, cls=_CLS[s], stage=s) for n, s in nodes_rendered
    )
    return f'<div class="nodes">{heads}</div>'


def _build(tmp, nodes, atom_levels, rendered):
    """Synthetic (site/index.html, mapping, map).
      nodes        -> [(name, [atom ids])]                 the node->atom mapping
      atom_levels  -> {id: (current, target)}              the map
      rendered     -> {name: 'Live'|'Building'|'Planned'}  what index.html displays
    Returns (site_dir, map_path, mapping_path) to pass straight into render_findings()."""
    site = tmp / "site"
    (site / "data").mkdir(parents=True, exist_ok=True)
    mapping = {
        "nodes": [
            {"id": n.lower(), "name": n, "declared_stage": None, "atoms": a} for n, a in nodes
        ]
    }
    (site / "data" / "moap_node_atoms.json").write_text(json.dumps(mapping), encoding="utf-8")
    map_txt = "".join(
        f"- id: {i}\n  lane: L\n  level_current: {c}\n  level_target: {t}\n"
        for i, (c, t) in atom_levels.items()
    )
    map_path = tmp / "map.yaml"
    map_path.write_text(map_txt, encoding="utf-8")
    (site / "index.html").write_text(
        _index([(n, rendered[n]) for n, _ in nodes]), encoding="utf-8"
    )
    return site, map_path, site / "data" / "moap_node_atoms.json"


# --- MECHANISM: rendered word vs computed stage, R15 both ways ----------------
def test_clean_when_rendered_matches_computed():
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(
            Path(d),
            nodes=[("Alpha", ["X1"])],
            atom_levels={"X1": (3, 3)},   # computes Live
            rendered={"Alpha": "Live"},   # renders Live -> clean
        )
        assert render_findings(site, m, g) == []


def test_outruns_when_site_claims_more_than_atoms():
    """R15 FIRE, OUTRUNS -- the dangerous direction: the site renders 'Live' while an atom sits
    below target (computes 'Building'). The front door over-claims -> a finding."""
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(
            Path(d),
            nodes=[("Alpha", ["X1"])],
            atom_levels={"X1": (1, 3)},   # computes Building
            rendered={"Alpha": "Live"},   # renders Live -> OUTRUNS
        )
        f = render_findings(site, m, g)
        assert len(f) == 1 and f[0][0] == STAGE_RENDER_DRIFT, f
        assert "OUTRUNS" in f[0][2], f


def test_lags_when_site_claims_less_than_atoms():
    """R15 FIRE, LAGS: every atom at target (computes 'Live') but the site still renders
    'Building' -- an under-claim is drift too, and surfaced."""
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(
            Path(d),
            nodes=[("Alpha", ["X1"])],
            atom_levels={"X1": (3, 3)},       # computes Live
            rendered={"Alpha": "Building"},   # renders Building -> LAGS
        )
        f = render_findings(site, m, g)
        assert len(f) == 1 and "LAGS" in f[0][2], f


def test_finding_flips_on_atom_level_alone():
    """R15 SECOND, INDEPENDENT path (the tautology killer): hold the rendered word FIXED at
    'Live' and move only the atom level. Below target -> finding; at target -> clean. Proves the
    check reads the map, not merely the HTML it is comparing against."""
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(
            Path(d) / "below",
            nodes=[("Alpha", ["X1"])],
            atom_levels={"X1": (1, 3)},
            rendered={"Alpha": "Live"},
        )
        assert render_findings(site, m, g), "below-target atom under a 'Live' render must fire"
        site2, m2, g2 = _build(
            Path(d) / "attarget",
            nodes=[("Alpha", ["X1"])],
            atom_levels={"X1": (3, 3)},
            rendered={"Alpha": "Live"},
        )
        assert render_findings(site2, m2, g2) == [], "at-target atom under 'Live' must be clean"


def test_not_always_one_value():
    """Independence: the SAME rendered word 'Live' yields a finding or not depending only on the
    atoms -- the check is not a constant that always passes (or always fails)."""
    with tempfile.TemporaryDirectory() as d:
        s_fire, m_fire, g_fire = _build(
            Path(d) / "a", [("N", ["X"])], {"X": (0, 2)}, {"N": "Live"}
        )
        s_ok, m_ok, g_ok = _build(
            Path(d) / "b", [("N", ["X"])], {"X": (2, 2)}, {"N": "Live"}
        )
        assert render_findings(s_fire, m_fire, g_fire), "below-target must fire under 'Live'"
        assert render_findings(s_ok, m_ok, g_ok) == [], "at-target must be clean under 'Live'"


def test_unmapped_rendered_node_not_double_reported():
    """A rendered node with no mapping entry is a Phase-A coherence defect (DIAGRAM_NODE_UNMAPPED,
    gated in moap_coherence). Phase C must skip it so the same drift is not counted twice -- the
    finding set here names only mapped nodes."""
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(
            Path(d),
            nodes=[("Alpha", ["X1"])],
            atom_levels={"X1": (3, 3)},
            rendered={"Alpha": "Live"},
        )
        # Add a rendered node ('Ghost') the mapping never mentions.
        (site / "index.html").write_text(
            _index([("Alpha", "Live"), ("Ghost", "Live")]), encoding="utf-8"
        )
        f = render_findings(site, m, g)
        assert all(node != "Ghost" for _, node, _ in f), f


# --- LIVE GATE --------------------------------------------------------------
def test_rendered_stages_reads_real_front_door():
    """The parser lifts a stage word for every front-door node off the real index.html."""
    r = rendered_stages()
    assert r, "no rendered stages parsed from the real front door"
    assert set(r.values()) <= {"Live", "Building", "Planned"}, r
    assert "The company" in r and "The score" in r, r


def test_real_site_renders_exactly_the_derivation():
    """LIVE GATE: every front-door node's rendered stage word equals its computed stage -- the
    site is not hand-set ahead of (or behind) the atoms. Fails the suite at publish if a future
    edit lets a node over-claim."""
    assert render_findings() == [], render_findings()
