"""R15 suite for Phase E -- the evidence pages behind the model-on-a-page nodes.

Atom: SITE_evidence_pages_behind_nodes. `site/moap_evidence.py` is a CONTROL, so the whole
question this file answers is: CAN IT FAIL? Every named defect in the atom's three exit criteria
gets a mutation here, and each mutation is paired with the aligned case proving the control is
not simply always-red.

THE MUTATION SET (each is a real defect this gate exists to catch)
-----------------------------------------------------------------
  criterion 1  a node claiming a non-trivial stage with NO evidence link      -> NODE_NO_EVIDENCE_LINK
               a link whose #anchor names no rendered section                 -> EVIDENCE_ANCHOR_DANGLING
               the evidence page file deleted                                 -> EVIDENCE_PAGE_MISSING
  criterion 2  evidence data missing / empty / malformed / node-less          -> EVIDENCE_DATA_UNUSABLE
               a record that substantiates nothing (no ledger/fidelity/tests) -> NODE_EVIDENCE_EMPTY
               figures that have fallen behind the maturity map               -> EVIDENCE_DATA_STALE
  criterion 3  a claim the node's own evidence computes differently           -> EVIDENCE_STAGE_UNSUPPORTED
  R15 self     the checker itself blowing up                                  -> EVIDENCE_CHECK_UNAVAILABLE

THE TAUTOLOGY KILLER. `test_moving_an_atom_level_alone_flips_the_verdict` holds the site's claim
COMPLETELY FIXED and moves only an atom's level in the map (regenerating the evidence from it).
The verdict flips. That proves the gate reads PRIMARY STATE, not the node's own claim -- the
independence R15 demands.

Every fixture is synthetic and self-contained; no assertion pins a value the sim generates
(feedback_never_pin_generated_values_in_controls). Where the real repo is asserted on, it is
asserted RELATIONALLY (the finding set is empty / a given kind is present), never by figure.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import moap_evidence as ME

SITE = Path(__file__).resolve().parent


# --------------------------------------------------------------------------- #
# A synthetic site with one Live node, one Building node, one Planned node.
# --------------------------------------------------------------------------- #
def _front_door(nodes_html: str) -> str:
    return (
        "<html><body><section><div class=\"nodes\">\n"
        + nodes_html
        + "\n</div></section>\n<p>after the diagram</p>\n</body></html>"
    )


def _node(name: str, stage: str, anchor: str | None) -> str:
    ev = (
        f'      <a class="node-evidence" href="./evidence/#{anchor}">Evidence &rarr;</a>\n'
        if anchor
        else ""
    )
    return (
        '    <div class="node">\n'
        f'      <div class="node-head"><span class="node-name">{name}</span>'
        f'<span class="stage stage-{stage.lower()}">{stage}</span></div>\n'
        f'      <a class="node-look" href="./world/#x">Look &rarr;</a>\n'
        f"{ev}"
        "    </div>"
    )


def _map_yaml(levels: dict[str, tuple[int, int]]) -> str:
    out = []
    for atom, (cur, tgt) in levels.items():
        out.append(f"- id: {atom}")
        out.append(f"  lane: X_lane")
        out.append(f"  level_current: {cur}")
        out.append(f"  level_target: {tgt}")
    return "\n".join(out) + "\n"


def _evidence_record(node_id: str, name: str, claimed: str, atoms: list[dict]) -> dict:
    at_target = sum(1 for a in atoms if a["level_current"] >= a["level_target"])
    return {
        "id": node_id,
        "anchor": f"node-{node_id}",
        "name": name,
        "claimed_stage": claimed,
        "atoms": [
            {
                "id": a["id"],
                "level_current": a["level_current"],
                "level_target": a["level_target"],
                "at_target": a["level_current"] >= a["level_target"],
                "ledger_records": a.get("ledger_records", 1),
                "fidelity_rows": a.get("fidelity_rows", 0),
                "tests": {"test_functions": a.get("test_functions", 12), "test_files": 1, "files": []},
            }
            for a in atoms
        ],
        "totals": {
            "atoms": len(atoms),
            "at_target": at_target,
            "ledger_records": sum(a.get("ledger_records", 1) for a in atoms),
            "fidelity_rows": sum(a.get("fidelity_rows", 0) for a in atoms),
            "test_files": len(atoms),
            "test_functions": sum(a.get("test_functions", 12) for a in atoms),
        },
    }


@pytest.fixture()
def world(tmp_path: Path):
    """A minimal, COHERENT site: two non-trivially-staged nodes and one Planned node, an
    evidence page, and evidence data whose figures match the map exactly."""
    site = tmp_path / "site"
    (site / "data").mkdir(parents=True)
    (site / "evidence").mkdir()

    levels = {"atom_live_a": (3, 3), "atom_live_b": (2, 2), "atom_mid": (1, 3)}
    map_path = tmp_path / "map.yaml"
    map_path.write_text(_map_yaml(levels), encoding="utf-8")

    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(
        json.dumps(
            {
                "nodes": [
                    {"id": "alpha", "name": "Alpha", "declared_stage": "Live",
                     "atoms": ["atom_live_a", "atom_live_b"]},
                    {"id": "beta", "name": "Beta", "declared_stage": "Building",
                     "atoms": ["atom_live_a", "atom_mid"]},
                    {"id": "gamma", "name": "Gamma", "declared_stage": "Planned", "atoms": []},
                ]
            }
        ),
        encoding="utf-8",
    )

    (site / "index.html").write_text(
        _front_door(
            "\n".join(
                [
                    _node("Alpha", "Live", "node-alpha"),
                    _node("Beta", "Building", "node-beta"),
                    _node("Gamma", "Planned", None),
                ]
            )
        ),
        encoding="utf-8",
    )
    (site / "evidence" / "index.html").write_text("<html>rendered from the data</html>", encoding="utf-8")

    data_path = site / "data" / "moap_evidence.json"
    data_path.write_text(
        json.dumps(
            {
                "nodes": [
                    _evidence_record("alpha", "Alpha", "Live", [
                        {"id": "atom_live_a", "level_current": 3, "level_target": 3},
                        {"id": "atom_live_b", "level_current": 2, "level_target": 2},
                    ]),
                    _evidence_record("beta", "Beta", "Building", [
                        {"id": "atom_live_a", "level_current": 3, "level_target": 3},
                        {"id": "atom_mid", "level_current": 1, "level_target": 3},
                    ]),
                ]
            }
        ),
        encoding="utf-8",
    )
    return {
        "site": site,
        "map": map_path,
        "mapping": mapping_path,
        "data": data_path,
        "page": site / "evidence" / "index.html",
    }


def _findings(w, **over):
    return ME.evidence_findings(
        site=over.get("site", w["site"]),
        map_path=over.get("map", w["map"]),
        mapping_path=over.get("mapping", w["mapping"]),
        data_path=over.get("data", w["data"]),
    )


def _kinds(findings):
    return {k for k, _, _ in findings}


# --------------------------------------------------------------------------- #
# Independence / not-always-red: the coherent world is GREEN.
# --------------------------------------------------------------------------- #
def test_a_coherent_world_is_green(world):
    """The control is not always-red: a site whose every non-trivially-staged node walks to a
    fresh, substantiating evidence record produces ZERO findings."""
    assert _findings(world) == []


def test_a_planned_node_needs_no_evidence_page(world):
    """'Planned' claims nothing exists, so it is exempt BY DESIGN -- and the Gamma node in the
    fixture carries no evidence link at all, yet the world is green (above). Prove the exemption
    is the reason, by promoting Gamma's stage word and watching the same node go red."""
    front = world["site"] / "index.html"
    front.write_text(front.read_text(encoding="utf-8").replace(
        '<span class="stage stage-planned">Planned</span>',
        '<span class="stage stage-live">Live</span>',
    ), encoding="utf-8")
    assert ME.NODE_NO_EVIDENCE_LINK in _kinds(_findings(world))


# --------------------------------------------------------------------------- #
# CRITERION 1 -- no dangling anchor.
# --------------------------------------------------------------------------- #
def test_a_node_with_no_evidence_link_fires(world):
    """R15: a node claiming 'Live' with no evidence link at all -> NODE_NO_EVIDENCE_LINK."""
    front = world["site"] / "index.html"
    front.write_text(front.read_text(encoding="utf-8").replace(
        '<a class="node-evidence" href="./evidence/#node-alpha">Evidence &rarr;</a>\n', ""
    ), encoding="utf-8")
    findings = _findings(world)
    assert ME.NODE_NO_EVIDENCE_LINK in _kinds(findings)
    assert any(subject == "Alpha" for _, subject, _ in findings)


def test_an_anchor_naming_no_rendered_section_fires(world):
    """R15: the anchor plumbing exists but the PAGE renders no such section -- the exact defect
    this atom was minted for ('the anchors exist, the PAGES they point to do not')."""
    front = world["site"] / "index.html"
    front.write_text(front.read_text(encoding="utf-8").replace(
        "#node-alpha", "#node-nowhere"
    ), encoding="utf-8")
    assert ME.EVIDENCE_ANCHOR_DANGLING in _kinds(_findings(world))


def test_a_missing_evidence_page_fires(world):
    """R15 FAIL-OPEN guard: the evidence page file itself absent must FAIL, never pass."""
    world["page"].unlink()
    assert ME.EVIDENCE_PAGE_MISSING in _kinds(_findings(world))


def test_a_missing_front_door_fires(world):
    """R15 FAIL-OPEN guard: no front door means no claims could be read -- a FAILED check."""
    (world["site"] / "index.html").unlink()
    assert ME.FRONT_DOOR_MISSING in _kinds(_findings(world))


# --------------------------------------------------------------------------- #
# CRITERION 2 -- primary-state evidence, not restated prose.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "payload,label",
    [
        (None, "file deleted"),
        ("", "empty file"),
        ("{not json", "malformed"),
        ('{"nodes": []}', "no nodes"),
        ('{"nodes": {}}', "nodes not a list"),
        ("[]", "not an object"),
    ],
)
def test_unusable_evidence_data_fires(world, payload, label):
    """R15 FAIL-OPEN guard, six ways: a missing, empty, malformed, node-less or wrongly-shaped
    evidence file must FAIL. A page that would render nothing is not a page of evidence."""
    if payload is None:
        world["data"].unlink()
    else:
        world["data"].write_text(payload, encoding="utf-8")
    assert ME.EVIDENCE_DATA_UNUSABLE in _kinds(_findings(world)), label


def test_a_record_that_substantiates_nothing_fires(world):
    """R15, the crux of criterion 2: a record with atoms but ZERO recorded level moves, ZERO
    fidelity rows and ZERO test functions substantiates nothing -- it is prose wearing a table."""
    data = json.loads(world["data"].read_text(encoding="utf-8"))
    for node in data["nodes"]:
        if node["id"] != "alpha":
            continue
        node["totals"]["ledger_records"] = 0
        node["totals"]["fidelity_rows"] = 0
        node["totals"]["test_functions"] = 0
    world["data"].write_text(json.dumps(data), encoding="utf-8")
    findings = _findings(world)
    assert ME.NODE_EVIDENCE_EMPTY in _kinds(findings)
    assert any(subject == "Alpha" for _, subject, _ in findings)


def test_an_empty_atom_list_fires(world):
    """R15: a record with no atoms at all cannot substantiate any stage claim."""
    data = json.loads(world["data"].read_text(encoding="utf-8"))
    data["nodes"][0]["atoms"] = []
    world["data"].write_text(json.dumps(data), encoding="utf-8")
    assert ME.NODE_EVIDENCE_EMPTY in _kinds(_findings(world))


def test_figures_that_fell_behind_the_map_fire(world):
    """R15: the page's figures must still BE primary state. Move the map and leave the page
    behind -> EVIDENCE_DATA_STALE. This is what stops the evidence page becoming a second,
    drifting home for the numbers (the coherence-by-derivation law)."""
    world["map"].write_text(
        _map_yaml({"atom_live_a": (1, 3), "atom_live_b": (2, 2), "atom_mid": (1, 3)}),
        encoding="utf-8",
    )
    findings = _findings(world)
    assert ME.EVIDENCE_DATA_STALE in _kinds(findings)


def test_an_atom_that_left_the_map_fires(world):
    """R15: a page row for an atom the map no longer contains is stale evidence, not evidence."""
    world["map"].write_text(
        _map_yaml({"atom_live_b": (2, 2), "atom_mid": (1, 3)}), encoding="utf-8"
    )
    assert ME.EVIDENCE_DATA_STALE in _kinds(_findings(world))


# --------------------------------------------------------------------------- #
# CRITERION 3 -- a claim the evidence cannot support FAILS.
# --------------------------------------------------------------------------- #
def test_a_claim_the_evidence_cannot_support_fires(world):
    """R15, the atom's own named mutation: promote a node's stage word to a stage its evidence
    cannot support -> EVIDENCE_STAGE_UNSUPPORTED. Only the CLAIM moves; the evidence is untouched."""
    front = world["site"] / "index.html"
    front.write_text(front.read_text(encoding="utf-8").replace(
        '<span class="stage stage-building">Building</span>',
        '<span class="stage stage-live">Live</span>',
    ), encoding="utf-8")
    findings = _findings(world)
    assert ME.EVIDENCE_STAGE_UNSUPPORTED in _kinds(findings)
    assert any(subject == "Beta" for _, subject, _ in findings)


def test_a_claim_that_lags_its_evidence_also_fires(world):
    """Both directions: under-claiming is drift too. Demote Alpha's word to 'Building' while its
    evidence computes 'Live' -> the same finding. A one-directional control is half a control."""
    front = world["site"] / "index.html"
    front.write_text(front.read_text(encoding="utf-8").replace(
        '<span class="node-name">Alpha</span><span class="stage stage-live">Live</span>',
        '<span class="node-name">Alpha</span><span class="stage stage-building">Building</span>',
    ), encoding="utf-8")
    findings = _findings(world)
    assert ME.EVIDENCE_STAGE_UNSUPPORTED in _kinds(findings)
    assert any(subject == "Alpha" for _, subject, _ in findings)


def test_moving_an_atom_level_alone_flips_the_verdict(world):
    """THE TAUTOLOGY KILLER (R15 independence). The site's claim is held COMPLETELY FIXED. Only
    an atom's level in the map moves -- and the evidence data is regenerated from that map, as it
    would be in life. The verdict flips green -> red, proving the gate reads PRIMARY STATE and
    never the node's own claim."""
    assert _findings(world) == []
    front_before = (world["site"] / "index.html").read_text(encoding="utf-8")

    # Only the map moves: atom_live_b drops below target.
    world["map"].write_text(
        _map_yaml({"atom_live_a": (3, 3), "atom_live_b": (0, 2), "atom_mid": (1, 3)}),
        encoding="utf-8",
    )
    # ...and the page is regenerated from it (figures stay honest, so this is NOT a staleness hit).
    data = json.loads(world["data"].read_text(encoding="utf-8"))
    for row in data["nodes"][0]["atoms"]:
        if row["id"] == "atom_live_b":
            row["level_current"] = 0
            row["at_target"] = False
    data["nodes"][0]["totals"]["at_target"] = 1
    world["data"].write_text(json.dumps(data), encoding="utf-8")

    findings = _findings(world)
    assert (world["site"] / "index.html").read_text(encoding="utf-8") == front_before
    assert ME.EVIDENCE_STAGE_UNSUPPORTED in _kinds(findings)
    assert ME.EVIDENCE_DATA_STALE not in _kinds(findings)


# --------------------------------------------------------------------------- #
# R15 FAIL-SILENT: the checker itself must not be able to pass by breaking.
# --------------------------------------------------------------------------- #
def test_an_exploding_checker_is_a_failed_check(world, monkeypatch):
    """R15 FAIL-SILENT guard: if the check cannot run, it must report a FINDING, never an empty
    (green) set. An unavailable check is a FAILED check."""
    def boom(*_a, **_k):
        raise RuntimeError("primary state unreadable")

    monkeypatch.setattr(ME, "map_atom_levels", boom)
    findings = _findings(world)
    assert ME.EVIDENCE_CHECK_UNAVAILABLE in _kinds(findings)


# --------------------------------------------------------------------------- #
# The LIVE repo (relational assertions only -- no pinned figures).
# --------------------------------------------------------------------------- #
def test_live_repo_every_node_walks_to_its_evidence():
    """The real front door: every non-trivially-staged node resolves to a real evidence record
    whose figures match the map and whose derivation carries the claim. If this reds, a claim on
    the front page is not backed by the state behind it."""
    findings = ME.evidence_findings()
    assert findings == [], f"Phase-E findings on the live site: {findings}"


def test_live_repo_has_non_trivially_staged_nodes():
    """Guards the live assertion against a vacuous pass: if the parser ever stopped seeing nodes,
    the suite above would be green over an empty set. The front door MUST carry claims."""
    nodes = ME.front_door_nodes()
    claiming = [n for n in nodes if n["stage"] in ME.NON_TRIVIAL_STAGES]
    assert claiming, "front door renders no non-trivially-staged node -- parser broke?"
    assert all(n["evidence_href"] for n in claiming)
