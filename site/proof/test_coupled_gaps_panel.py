"""Render-side tests for the Proof-door COUPLED-TRIAD gap panel (site/proof/index.html).

The DATA side (tools/generate_proof_data.py::_coupled_gaps) is tested separately in
tests/tools/test_generate_proof_coupled_gaps.py. THIS suite tests the RENDER: it executes
the page's actual inline JavaScript (via a Node/vm harness) against real generated data and
against synthetic mutation cases, then asserts on the produced HTML -- i.e. the rendered
pixel (R11), not the source string.

R15 (a control must be able to FAIL): the panel is a control surface -- it classifies each
measured gap by the reading convention (COUPLED_TRIAD_DESIGN.md 1.2) and must fail closed and
VISIBLE when the data side is absent/empty. Each mutation below feeds the panel its named
defect and asserts the panel fires: null gap -> untested/amber; gap 0 -> wall-leak/red;
gap>1 -> worse-than-blind/red; available:false or empty pairs -> a visible red failure block,
never a silently empty panel.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
PROJECT = HERE.parent.parent  # site/proof -> repo root

NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict) -> dict:
    """Run the page's inline renderCoupledGaps against `data`; return element contents."""
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps({"coupled_gaps": data}),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live_coupled_gaps() -> dict:
    """The real data the generator would emit into proof.json.coupled_gaps."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_proof_data import _coupled_gaps, _load_atoms

    return _coupled_gaps(_load_atoms())


# --------------------------------------------------------------------------- #
# R11: the panel renders the LIVE generated data -- all 7 affordability pairs.
# --------------------------------------------------------------------------- #
def test_live_data_renders_all_seven_pairs():
    cg = _live_coupled_gaps()
    assert cg.get("available") is True
    assert cg["pair_count"] == 7, "affordability cluster should have 7 coupled pairs"

    out = _render(cg)
    body = out["coupled-gaps"]["innerHTML"]

    # Every world<->company pair id must appear in the rendered rows.
    for pair in cg["pairs"]:
        assert pair["world_atom"] in body, f"{pair['world_atom']} not rendered"
        assert pair["company_atom"] in body, f"{pair['company_atom']} not rendered"

    # Exactly 7 gap rows rendered (no pair silently dropped, measured or not).
    assert body.count('class="gap-row"') == 7

    # The measured gap values are rendered to 3 dp (the pixel == the number, R11).
    for pair in cg["pairs"]:
        if pair["value"] is not None:
            assert f"{pair['value']:.3f}" in body, f"gap value for {pair['world_atom']} not rendered"

    # Summary / anti-decay counts are rendered in the KPI strip.
    kpis = out["gap-kpis"]["innerHTML"]
    assert str(cg["pair_count"]) in kpis
    assert str(cg["measured"]) in kpis


def test_live_data_all_measured_no_alarm():
    """With the current ledger every pair is measured, so no >=L2-unmeasured alarm fires,
    and no leak/worse-than-blind chips appear."""
    cg = _live_coupled_gaps()
    out = _render(cg)
    if cg.get("unmeasured_ge_l2"):
        assert "depth nobody copes with yet" in out["gap-alarms"]["innerHTML"]
    else:
        assert out["gap-alarms"]["innerHTML"] == ""
    body = out["coupled-gaps"]["innerHTML"]
    # 0<gap<=1 everywhere in the live data -> only the blue "learning" chip.
    assert 'class="chip red"' not in body


# --------------------------------------------------------------------------- #
# R15 mutation tests: feed the panel each named defect; assert the control fires.
# --------------------------------------------------------------------------- #
def _one_pair(value):
    return {
        "available": True,
        "source": "docs/observability/coupled_gap_ledger.json",
        "pair_count": 1,
        "measured": 0 if value is None else 1,
        "unmeasured": 1 if value is None else 0,
        "blocks_l3_count": 0,
        "wall_leak_count": 1 if (value is not None and value <= 0) else 0,
        "worse_than_blind_count": 1 if (value is not None and value > 1) else 0,
        "unmeasured_ge_l2": ["W2_X_test"] if value is None else [],
        "pairs": [{
            "world_atom": "W2_X_test", "company_atom": "CX_test",
            "world_name": "test world", "company_name": "test company",
            "world_level": 2, "company_level": 2,
            "metric": "belief", "value": value, "baseline_g0": 0.5,
            "raw_gap": None, "components": None, "note": "n",
            "measured_at": None, "run_git_commit": None,
            "trend": "single", "history": [], "chip": None, "severity": None,
            "blocks_l3": False, "blocks_l3_reason": None,
        }],
    }


def test_mutation_null_gap_renders_untested_amber():
    out = _render(_one_pair(None))
    body = out["coupled-gaps"]["innerHTML"]
    assert 'class="chip amber"' in body and "untested" in body
    # The >=L2-with-no-gap anti-decay alarm must fire (binding rule 1 made visible).
    assert "depth nobody copes with yet" in out["gap-alarms"]["innerHTML"]


def test_mutation_zero_gap_renders_wall_leak_red():
    out = _render(_one_pair(0.0))
    body = out["coupled-gaps"]["innerHTML"]
    assert '<span class="chip red">leak</span>' in body


def test_mutation_gap_above_one_renders_worse_than_blind_red():
    out = _render(_one_pair(1.4))
    body = out["coupled-gaps"]["innerHTML"]
    assert 'class="chip red"' in body and "worse than blind" in body


def test_mutation_normal_gap_renders_learning_blue():
    out = _render(_one_pair(0.42))
    body = out["coupled-gaps"]["innerHTML"]
    assert 'class="chip blue"' in body and "learning" in body
    assert "0.420" in body


def test_mutation_blocks_l3_flag_renders_badge():
    data = _one_pair(0.42)
    data["pairs"][0]["blocks_l3"] = True
    data["pairs"][0]["blocks_l3_reason"] = "twin below L2"
    data["blocks_l3_count"] = 1
    out = _render(data)
    assert "blocks L3" in out["coupled-gaps"]["innerHTML"]


def test_fail_closed_when_data_unavailable():
    """available:false must produce a VISIBLE failure, never a silently empty panel."""
    out = _render({"available": False, "note": "module not importable"})
    body = out["coupled-gaps"]["innerHTML"]
    assert "gap-fail" in body
    assert "not available" in body
    assert body.strip() != ""


def test_fail_closed_when_pairs_empty():
    """An empty pair list (ledger drained) must render a visible failure, not blank."""
    data = _one_pair(0.42)
    data["pairs"] = []
    data["pair_count"] = 0
    out = _render(data)
    body = out["coupled-gaps"]["innerHTML"]
    assert "gap-fail" in body
    assert body.strip() != ""


def test_missing_coupled_gaps_key_fails_visible():
    """proof.json with no coupled_gaps block at all -> visible failure."""
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps({}),  # no coupled_gaps key
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert "gap-fail" in out["coupled-gaps"]["innerHTML"]
