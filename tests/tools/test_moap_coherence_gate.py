"""R15 mechanism self-test for §6 coherence-by-derivation -- PHASE D (the dedicated cross-surface
publish gate, tools/moap_coherence_gate.py).

Two roles, same pattern as the Phase A/B/C suites:

  1. MECHANISM self-tests (R15 BOTH WAYS, per surface): synthetic (index.html, mapping, map)
     fixtures prove `gather_findings()` FIRES on a defect INTRODUCED ON EACH of the three surfaces
     it unions -- a Phase-A dead-atom mapping ref, a Phase-B declared-vs-computed stage
     disagreement, a Phase-C rendered-vs-computed drift -- and is CLEAN when the surfaces cohere.
     The tautology killer holds the site's claim FIXED and moves only an atom level: the finding
     flips, proving the gate reads the MAP, not merely echoes one surface at another.

     `decide()` is proven both ways INDEPENDENTLY of the mode: ENFORCE returns 1 on findings,
     SHADOW returns 0 on the SAME findings (the risk-clause rail genuinely does not block), and
     both return 0 on none. Scoping (`is_triggered`) is proven: the map is a trigger (the gap the
     site-lane gate misses), an unrelated change is not.

  2. LIVE GATE: the real four surfaces cohere today -- `gather_findings()` on the real repo is
     empty -- so the gate is green in ENFORCE and would fire the moment a future edit lets a node
     over-claim across any surface.
"""
import importlib.util
import json
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_SITE = _ROOT / "site"

# Import the gate module by path (it lives in tools/, not an importable package). The gate itself
# puts site/ on sys.path at import time so its moap_* imports resolve.
_spec = importlib.util.spec_from_file_location(
    "moap_coherence_gate", _ROOT / "tools" / "moap_coherence_gate.py"
)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

# The gate puts site/ on sys.path at import time; reuse the REAL derivation to build fixtures
# whose evidence surface agrees with the stage its own atom levels compute (never a second
# hand-maintained copy of the rule).
from moap_stage import compute_stage  # noqa: E402


_HEAD = (
    '<div class="node-head"><span class="node-name">{name}</span>'
    '<span class="stage stage-{cls}">{stage}</span></div>'
)
_CLS = {"Live": "live", "Building": "building", "Planned": "planned"}


def _build(tmp, nodes, atom_levels):
    """Synthetic (site/index.html, mapping, map, evidence page + evidence data). `nodes` is a
    list of dicts:
      {name, atoms:[ids], declared: 'Live'|.., rendered: 'Live'|..}
    `atom_levels` is {id: (current, target)}. Returns (site_dir, map_path, mapping_path) to pass
    straight into gate.gather_findings().

    The evidence surface (Phase E, atom SITE_evidence_pages_behind_nodes) is built COHERENT with
    whatever stage the fixture's atom levels compute: page present, one evidence anchor per
    non-Planned node, one evidence-data entry per node recording the computed+declared stage. A
    fixture that models a coherent site must model its evidence pages too -- the Phase-E
    mutations (page deleted, anchor dangling, data stale) are exercised in
    tests/tools/test_moap_evidence.py."""
    site = tmp / "site"
    (site / "data").mkdir(parents=True, exist_ok=True)
    (site / "evidence").mkdir(parents=True, exist_ok=True)
    mapping = {
        "nodes": [
            {"id": n["name"].lower(), "name": n["name"],
             "declared_stage": n["declared"], "atoms": n["atoms"]}
            for n in nodes
        ]
    }
    (site / "data" / "moap_node_atoms.json").write_text(json.dumps(mapping), encoding="utf-8")
    map_txt = "".join(
        f"- id: {i}\n  lane: L\n  level_current: {c}\n  level_target: {t}\n"
        for i, (c, t) in atom_levels.items()
    )
    map_path = tmp / "map.yaml"
    map_path.write_text(map_txt, encoding="utf-8")

    computed = {
        n["name"].lower(): compute_stage(
            [
                {"current": atom_levels.get(a, (0, 1))[0], "target": atom_levels.get(a, (0, 1))[1]}
                for a in n["atoms"]
            ]
        )
        for n in nodes
    }
    heads = "\n".join(
        _HEAD.format(name=n["name"], cls=_CLS[n["rendered"]], stage=n["rendered"])
        + (
            f'<a class="node-look" href="./evidence/#node-{n["name"].lower()}">Evidence</a>'
            if computed[n["name"].lower()] != "Planned"
            else ""
        )
        for n in nodes
    )
    (site / "index.html").write_text(f'<div class="nodes">{heads}</div>', encoding="utf-8")
    (site / "evidence" / "index.html").write_text(
        "<html><body>"
        + "".join(f'<section id="node-{nid}"></section>' for nid in computed)
        + "</body></html>",
        encoding="utf-8",
    )
    (site / "data" / "moap_evidence.json").write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": n["name"].lower(),
                        "name": n["name"],
                        "declared_stage": n["declared"],
                        "computed_stage": computed[n["name"].lower()],
                        "atoms": [],
                    }
                    for n in nodes
                ]
            }
        ),
        encoding="utf-8",
    )
    return site, map_path, site / "data" / "moap_node_atoms.json"


def _findings(nodes, atom_levels):
    with tempfile.TemporaryDirectory() as d:
        site, m, g = _build(Path(d), nodes, atom_levels)
        return gate.gather_findings(site, m, g)


# --- MECHANISM: clean baseline ------------------------------------------------
def test_clean_surfaces_yield_no_findings():
    f = _findings(
        [{"name": "Alpha", "atoms": ["X1"], "declared": "Live", "rendered": "Live"}],
        {"X1": (3, 3)},  # at target -> computes Live; declared Live; rendered Live -> cohere
    )
    assert f == [], f


# --- MECHANISM: R15 FIRE on each of the three surfaces -------------------------
def test_fires_on_stage_disagreement_map_vs_declared():
    """Phase-B surface: the site's hand-set declared_stage says 'Live' but the atom is below
    target (computes 'Building'). A map/model-vs-site disagreement -> a finding."""
    f = _findings(
        [{"name": "Alpha", "atoms": ["X1"], "declared": "Live", "rendered": "Building"}],
        {"X1": (1, 3)},  # below target -> computes Building; declared 'Live' disagrees
    )
    kinds = {kind for _, kind, _, _ in f}
    assert "STAGE_DISAGREEMENT" in kinds, f


def test_fires_on_render_drift_html_vs_computed():
    """Phase-C surface: the front-door HTML renders 'Live' while the atoms compute 'Building'
    (declared_stage is null so it is not itself a stage disagreement -- isolates render drift)."""
    f = _findings(
        [{"name": "Alpha", "atoms": ["X1"], "declared": None, "rendered": "Live"}],
        {"X1": (1, 3)},  # computes Building; rendered 'Live' OUTRUNS
    )
    kinds = {kind for _, kind, _, _ in f}
    assert "STAGE_RENDER_DRIFT" in kinds, f


def test_fires_on_dead_atom_ref_mapping():
    """Phase-A surface: the mapping references an atom absent from the map -- a hard mapping
    integrity defect the gate must block on."""
    f = _findings(
        [{"name": "Alpha", "atoms": ["GONE"], "declared": None, "rendered": "Planned"}],
        {"X1": (0, 3)},  # 'GONE' is not in the map -> DEAD_ATOM_REF
    )
    kinds = {kind for _, kind, _, _ in f}
    assert "DEAD_ATOM_REF" in kinds, f


# --- MECHANISM: the tautology killer (reads the MAP, not just one surface) -----
def test_finding_flips_on_atom_level_alone():
    """Hold the site's declared+rendered claim FIXED at 'Live'; move ONLY the atom level. Below
    target -> a finding; at target -> clean. Proves the gate reads the map, not merely compares
    two hand-authored surfaces to each other."""
    fixed = [{"name": "Alpha", "atoms": ["X1"], "declared": "Live", "rendered": "Live"}]
    assert _findings(fixed, {"X1": (1, 3)}), "below-target under a 'Live' claim must fire"
    assert _findings(fixed, {"X1": (3, 3)}) == [], "at-target under a 'Live' claim must be clean"


# --- MECHANISM: soft orphan atom does NOT block -------------------------------
def test_orphan_atom_alone_does_not_block():
    """An atom in the map behind no node is a soft §5-backlog ORPHAN_ATOM, never a gate failure.
    With every node's stage cohering, the presence of an extra unmapped atom yields no finding."""
    f = _findings(
        [{"name": "Alpha", "atoms": ["X1"], "declared": "Live", "rendered": "Live"}],
        {"X1": (3, 3), "ORPHAN": (2, 2)},  # ORPHAN mapped to no node -> soft, excluded
    )
    assert f == [], f


# --- MECHANISM: decide() both ways, independent of mode -----------------------
def test_decide_enforce_blocks_on_findings():
    findings = [(gate.S_STAGE, "STAGE_DISAGREEMENT", "Alpha", "declared='Live' computed='Building'")]
    assert gate.decide(findings, gate.ENFORCE) == 1


def test_decide_enforce_passes_when_clean():
    assert gate.decide([], gate.ENFORCE) == 0


def test_decide_shadow_never_blocks_even_with_findings():
    """The risk-clause rail: SHADOW returns 0 on the SAME findings ENFORCE blocks on -- proving the
    report-only escape hatch genuinely does not wedge publishing."""
    findings = [(gate.S_STAGE, "STAGE_DISAGREEMENT", "Alpha", "declared='Live' computed='Building'")]
    assert gate.decide(findings, gate.SHADOW) == 0
    assert gate.decide(findings, gate.ENFORCE) == 1  # the same findings DO block in enforce


# --- MECHANISM: mode file (fail-safe to ENFORCE) ------------------------------
def test_gate_mode_defaults_enforce_and_fails_safe():
    with tempfile.TemporaryDirectory() as d:
        missing = Path(d) / "absent.mode"
        assert gate.gate_mode(missing) == gate.ENFORCE, "absent mode file must default to ENFORCE"
        malformed = Path(d) / "bad.mode"
        malformed.write_text("off\n", encoding="utf-8")
        assert gate.gate_mode(malformed) == gate.ENFORCE, "a malformed mode must fail SAFE to ENFORCE"
        shadow = Path(d) / "shadow.mode"
        shadow.write_text("shadow\n", encoding="utf-8")
        assert gate.gate_mode(shadow) == gate.SHADOW


# --- MECHANISM: trigger scoping (the map is the gap the site-lane gate misses) -
def test_is_triggered_includes_the_map_excludes_unrelated():
    assert gate.is_triggered(["docs/design/maturity_map.yaml"]), "a map-only edit MUST trigger"
    assert gate.is_triggered(["site/data/moap_node_atoms.json"])
    assert gate.is_triggered(["site/index.html"])
    assert not gate.is_triggered(["saas/billing/engine.py", "docs/status/LATEST.md"])
    assert not gate.is_triggered([])


# --- LIVE GATE ----------------------------------------------------------------
def test_real_four_surfaces_cohere_and_gate_is_green():
    """The real repo's model/diagram/site/map agree on every node's stage today, so the gate is
    green in ENFORCE. This fails the suite if a future edit lets a node over-claim across surfaces."""
    real = gate.gather_findings()
    assert real == [], real
    assert gate.decide(real, gate.ENFORCE) == 0
