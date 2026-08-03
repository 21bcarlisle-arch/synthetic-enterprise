"""EXIT CRITERION 3, mechanised: a node whose evidence page is missing -- or whose claimed stage
disagrees with the derivation -- FAILS THE PUBLISH GATE.

Atom: SITE_evidence_pages_behind_nodes.

WHY THIS FILE IS UNDER `tests/` AND NOT UNDER `site/`
-----------------------------------------------------
That location IS the mechanism, not an accident of taste. The publish gate runs
`background/process_run_complete.publish_gate_pytest_argv(test_root="tests/")` -- `tests/`, and
nothing else. A control living only under `site/**` reaches the site-lane PRE-COMMIT gate but is
invisible to publish (the documented seam in tools/site_lane_gate.py: "a red site-door test CANNOT
wedge the publish gate and slips straight onto the director's window"). So the criterion-3 control
lives HERE, is unmarked (the gate deselects only `-m operational`), and is not in the gate's heavy
ignore list -- three properties this suite ASSERTS about itself below, so the wiring cannot rot
silently. The commit-time half is the same finding set unioned into tools/moap_coherence_gate.py
(Phase D), proven here too.

R15 -- BOTH WAYS, ON THE REAL SURFACES
--------------------------------------
  * the live repo is GREEN: every front-door node walks to a real, current evidence record;
  * mutate ONE atom's level in a COPY of the map and regenerate the evidence from it -- the site's
    claim untouched -- and the gate FIRES with EVIDENCE_STAGE_UNSUPPORTED and refuses (rc 1). This
    is the tautology killer: the verdict moved because PRIMARY STATE moved, not because any claim
    was restated;
  * point the gate at a missing evidence file and it FIRES (fail-closed), never passes;
  * SHADOW mode returns 0 on the SAME findings, proving the risk-clause rail still genuinely does
    not block (a new scanner must not be able to wedge publishing).

No assertion pins a generated figure -- the mutations move a level and assert the RELATIONSHIP
(green -> red), never a number (feedback_never_pin_generated_values_in_controls).
"""
import importlib.util
import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_SITE = _ROOT / "site"
_MAP = _ROOT / "docs" / "design" / "maturity_map.yaml"
_EVIDENCE_DATA = _SITE / "data" / "moap_evidence.json"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The gate puts site/ on sys.path at import time so its moap_* imports resolve.
gate = _load("moap_coherence_gate", _ROOT / "tools" / "moap_coherence_gate.py")
generator = _load(
    "generate_moap_evidence_data", _ROOT / "tools" / "generate_moap_evidence_data.py"
)
import moap_evidence as ME  # noqa: E402  (importable only after the gate put site/ on sys.path)


def _evidence_findings(findings):
    return [f for f in findings if f[0] == gate.S_EVIDENCE]


# --------------------------------------------------------------------------- #
# The live surfaces are GREEN (and not vacuously so).
# --------------------------------------------------------------------------- #
def test_live_repo_every_claiming_node_walks_to_its_evidence():
    """The publish-blocking assertion. If this reds, a stage claim on the front page is not
    carried by the state behind it, or a node's evidence page has gone missing/stale."""
    findings = _evidence_findings(gate.gather_findings())
    assert findings == [], f"node->evidence findings on the live site: {findings}"


def test_the_live_check_is_not_vacuous():
    """Guards the assertion above against a silent parser failure: the front door MUST carry
    non-trivially-staged nodes, and every one of them MUST carry an evidence link."""
    claiming = [n for n in ME.front_door_nodes() if n["stage"] in ME.NON_TRIVIAL_STAGES]
    assert claiming, "front door renders no node claiming a non-trivial stage -- parser broke?"
    assert all(n["evidence_href"] for n in claiming)


def test_the_evidence_data_is_current_with_the_map():
    """The committed evidence data must still BE primary state -- otherwise the page renders
    figures the map has moved past. Regenerating is the fix; this is the alarm."""
    data = ME.load_evidence_data(_EVIDENCE_DATA)
    assert data is not None, "site/data/moap_evidence.json is missing, empty or malformed"
    stale = [f for f in _evidence_findings(gate.gather_findings()) if f[1] == ME.EVIDENCE_DATA_STALE]
    assert not stale, f"evidence page figures have fallen behind the map: {stale}"


def test_the_live_gate_returns_zero_in_enforce():
    assert gate.decide(gate.gather_findings(), gate.ENFORCE) == 0


# --------------------------------------------------------------------------- #
# R15 -- the gate FIRES on the atom's own named defect.
# --------------------------------------------------------------------------- #
def test_a_claim_its_evidence_cannot_support_fails_the_gate(tmp_path):
    """THE NAMED MUTATION (exit criterion 3 + the tautology killer). Demote one atom in a COPY of
    the maturity map, regenerate the evidence page's data from that copy, leave site/index.html
    COMPLETELY UNTOUCHED -- the gate must FIRE and REFUSE."""
    live = ME.evidence_findings()
    assert live == [], f"precondition: the live surfaces must be green first, got {live}"

    # Pick a node that currently claims 'Live' (all atoms at target) and demote one of its atoms.
    data = ME.load_evidence_data(_EVIDENCE_DATA)
    node = next(
        n for n in data["nodes"] if n["atoms"] and all(r["at_target"] for r in n["atoms"])
    )
    victim = node["atoms"][0]["id"]

    map_copy = tmp_path / "maturity_map.yaml"
    text = _MAP.read_text(encoding="utf-8")
    # Demote the victim atom's level_current to 0 -- edit ONLY inside its own record.
    start = text.index(f"- id: {victim}\n")
    end = text.find("\n- id: ", start + 1)
    record = text[start:end if end != -1 else len(text)]
    demoted = re.sub(r"level_current:\s*\d+", "level_current: 0", record, count=1)
    assert demoted != record, "mutation did not apply -- the map record shape changed?"
    map_copy.write_text(text[:start] + demoted + (text[end:] if end != -1 else ""), encoding="utf-8")

    # Regenerate the evidence from the MUTATED map, exactly as the generator would in life.
    regenerated = generator.build_evidence_data(map_path=map_copy)
    data_copy = tmp_path / "moap_evidence.json"
    data_copy.write_text(json.dumps(regenerated), encoding="utf-8")

    front_before = (_SITE / "index.html").read_text(encoding="utf-8")
    findings = ME.evidence_findings(map_path=map_copy, data_path=data_copy)
    assert (_SITE / "index.html").read_text(encoding="utf-8") == front_before, "the site was mutated"

    kinds = {k for k, _, _ in findings}
    assert ME.EVIDENCE_STAGE_UNSUPPORTED in kinds, f"gate did not fire: {findings}"
    assert ME.EVIDENCE_DATA_STALE not in kinds, "the page was regenerated -- staleness is not the defect here"

    # ...and the GATE refuses the commit on it.
    gated = gate.gather_findings(map_path=map_copy, evidence_data_path=data_copy)
    assert gate.decide(gated, gate.ENFORCE) == 1


def test_a_missing_evidence_file_fails_the_gate(tmp_path):
    """R15 FAIL-OPEN guard at gate level: the derived evidence absent must REFUSE, never pass."""
    findings = gate.gather_findings(evidence_data_path=tmp_path / "absent.json")
    kinds = {f[1] for f in _evidence_findings(findings)}
    assert ME.EVIDENCE_DATA_UNUSABLE in kinds
    assert gate.decide(findings, gate.ENFORCE) == 1


def test_the_shadow_rail_still_does_not_block(tmp_path):
    """The risk clause: a NEW cross-surface scanner must never be able to wedge publishing. On the
    SAME findings it refuses in ENFORCE, SHADOW returns 0."""
    findings = gate.gather_findings(evidence_data_path=tmp_path / "absent.json")
    assert findings, "precondition: this mutation must produce findings"
    assert gate.decide(findings, gate.ENFORCE) == 1
    assert gate.decide(findings, gate.SHADOW) == 0


# --------------------------------------------------------------------------- #
# The gate's SCOPE -- so the wiring cannot rot silently.
# --------------------------------------------------------------------------- #
def test_the_evidence_surfaces_trigger_the_commit_gate():
    """A commit touching the evidence page or its data must RUN this gate; an unrelated file
    must not pay for it."""
    assert gate.is_triggered(["site/evidence/index.html"])
    assert gate.is_triggered(["site/data/moap_evidence.json"])
    assert gate.is_triggered(["docs/design/maturity_map.yaml"])
    assert not gate.is_triggered(["README.md"])


def test_this_control_actually_reaches_the_publish_gate():
    """R11 'no orphan transitions', applied to the control itself: exit criterion 3 says the
    publish gate must FAIL. Assert the three properties that make that true, rather than trusting
    the file's location -- an unreachable control is theatre."""
    import sys

    sys.path.insert(0, str(_ROOT))
    from background.process_run_complete import (
        PUBLISH_GATE_HEAVY_IGNORES,
        PUBLISH_GATE_MARKER_EXPR,
        publish_gate_pytest_argv,
    )

    rel = str(Path(__file__).resolve().relative_to(_ROOT))
    argv = publish_gate_pytest_argv()
    assert "tests/" in argv, "the publish gate no longer runs the tests/ root"
    assert rel.startswith("tests/"), "this control moved out of the publish gate's root"
    assert not any(rel.startswith(ig) or ig == rel for ig in PUBLISH_GATE_HEAVY_IGNORES)
    # Unmarked: the gate deselects only the operational layer.
    assert PUBLISH_GATE_MARKER_EXPR == "not operational"
    assert "@pytest.mark.operational" not in Path(__file__).read_text(encoding="utf-8")
