"""Render-side tests for the Proof-door FIDELITY INSTRUMENT panel (atom G4,
site/proof/index.html).

The DATA side (tools/generate_fidelity_data.py) is exercised directly here via
`build_fidelity_data()` for the live-data assertions; a dedicated
tools/-level unit-test suite is out of scope for this SITE-lane atom (SITE +
tools/generate_fidelity only). THIS suite tests the RENDER: it executes the
page's actual inline JavaScript (via the Node/vm harness `_fidelity_harness.mjs`)
against real generated data and against synthetic mutation cases, then
asserts on the produced HTML -- i.e. the rendered pixel (R11), not the source
string.

DIRECTOR FIDELITY STEER (docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md):
"the average is a trap" -- the panel must LEAD with the exposure-tail
under-representation and the worst-cell CVaR, and render the calm-year
MAE/lift reading last and visibly subordinate. `test_live_data_leads_with_exposure_tail_not_average`
pins this ordering/emphasis directly, not just presence.

R15 (a control must be able to FAIL): this is a rendering of a fidelity
CONTROL surface, so it must fail closed and VISIBLE when the data side is
absent/empty. Each mutation below feeds the panel a named defect (changed
under-representation ratio, changed worst-cell, unavailable ledger, empty
exposure-tail) and asserts the panel's rendered pixels follow -- never a
hardcoded literal, never a silently blank section.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_fidelity_harness.mjs"
PROJECT = HERE.parent.parent  # site/proof -> repo root

NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data) -> dict:
    """Run the page's inline renderFidelity against `data`; return element contents."""
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live_fidelity_data() -> dict:
    """The real data the generator would emit into fidelity.json."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_fidelity_data import build_fidelity_data

    return build_fidelity_data()


# --------------------------------------------------------------------------- #
# R11: the panel renders the LIVE generated data.
# --------------------------------------------------------------------------- #
def test_live_data_available_and_renders():
    d = _live_fidelity_data()
    assert d["available"] is True
    out = _render(d)

    intro = out["fid-intro"]["innerHTML"]
    assert d["atom_id"] in intro

    tail = out["fid-tail"]["innerHTML"]
    assert "gap-fail" not in tail
    for row in d["exposure_tail"]["rows"]:
        assert row["metric"] in tail

    worst = out["fid-worst"]["innerHTML"]
    assert d["worst_cell"]["cell"] in worst

    chain = out["fid-chain"]["innerHTML"]
    for node in d["inspection_chain"]["nodes"]:
        assert node["label"] in chain

    mae = out["fid-mae"]["innerHTML"]
    for row in d["per_cell_lift"]:
        assert row["year"] in mae


def test_live_worst_cell_is_2022_crisis_year():
    """Pins the director steer's headline finding: worst-scored cell under
    G1's CVaR is the real 2022 gas-crisis year, not merely the lowest-R2 year."""
    d = _live_fidelity_data()
    assert d["worst_cell"]["cell"] == "y2022"
    assert d["worst_cell"]["regime"] == "crisis"
    out = _render(d)
    worst = out["fid-worst"]["innerHTML"]
    assert "y2022" in worst
    assert '<span class="chip red">crisis</span>' in worst


def test_live_data_leads_with_exposure_tail_not_average():
    """DIRECTOR FIDELITY STEER pinned: the exposure-tail block must render
    BEFORE (textually precede) the subordinate MAE/lift block, and the
    MAE block must carry the 'subordinate, low-stakes' framing -- the
    average is never the headline."""
    d = _live_fidelity_data()
    out = _render(d)
    tail_html = out["fid-tail"]["innerHTML"]
    mae_html = out["fid-mae"]["innerHTML"]
    assert "top fidelity gap" in tail_html
    assert "under-represented" in tail_html
    assert "subordinate" in mae_html
    assert "low-stakes" in mae_html
    # The MAE reading states the honest "beats naive in only N/M years" framing,
    # not a flattering summary.
    assert "beats best-of-naive-family" in mae_html


def test_live_exposure_tail_ratios_match_director_steer_order_of_magnitude():
    """The director's steer names ~7x (max spike) and ~170x (negative-price
    frequency) under-representation. Pin the ORDER OF MAGNITUDE (not an exact
    literal -- these are derived, live-recomputed-or-cited numbers) so a
    future change to the underlying fit/doc is caught if it drifts wildly."""
    d = _live_fidelity_data()
    rows = {r["metric"]: r for r in d["exposure_tail"]["rows"]}
    max_row = rows["Extreme spike (max SSP)"]
    neg_row = rows["Negative-price frequency"]
    assert 5.0 < max_row["under_representation_x"] < 10.0
    assert 100.0 < neg_row["under_representation_x"] < 250.0


# --------------------------------------------------------------------------- #
# R15 mutation tests: feed the panel each named defect; assert the control fires.
# --------------------------------------------------------------------------- #
def _base_available_data(**overrides):
    data = {
        "available": True,
        "atom_id": "W1_6_physics_price_signal",
        "measured_at": "2026-07-19T00:00:00+00:00",
        "source_ledger": "docs/observability/fidelity_evidence_ledger.json",
        "steer_doc": "docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md",
        "exposure_tail": {
            "available": True,
            "basis": "cited_from_fidelity_doc",
            "source": "docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md S2.3",
            "rows": [
                {"metric": "Extreme spike (max SSP)", "unit": "£/MWh",
                 "model": 574.22, "real": 4037.80, "under_representation_x": 7.03,
                 "why": "test why max"},
                {"metric": "Negative-price frequency", "unit": "% of periods",
                 "model": 0.013, "real": 2.241, "under_representation_x": 172.4,
                 "why": "test why neg"},
            ],
        },
        "worst_cell": {
            "cell": "y2022", "year": "2022", "severity_mae_gbp_per_mwh": 79.16,
            "q": 0.1, "cvar_aggregate_gbp_per_mwh": 79.16, "tail_k": 1,
            "regime": "crisis", "lift": 5.55, "commentary": "test commentary",
        },
        "per_cell_lift": [
            {"cell": "y2022", "year": "2022", "regime": "crisis", "stakes": "high",
             "err_model": 79.16, "err_naive": 84.71, "lift": 5.55, "beats_naive": True},
            {"cell": "y2019", "year": "2019", "regime": "calm", "stakes": "low",
             "err_model": 18.82, "err_naive": 18.02, "lift": -0.79, "beats_naive": False},
        ],
        "mae_reading": {
            "subordinate": True,
            "headline": "structural model beats best-of-naive-family in only 4/10 years",
            "note": "THE AVERAGE TRAP (director steer): this reading is low-stakes.",
            "full_window_mae": 32.79, "full_window_r2": 0.419,
        },
        "inspection_chain": {
            "available": True,
            "note": "No BELIEF_ACTION node.",
            "nodes": [
                {"node_id": "EVIDENCE::x", "layer": "EVIDENCE", "label": "residual_demand_scarcity_price_calibration",
                 "detail": "MAE=£32.79/MWh"},
                {"node_id": "WORLD::x", "layer": "WORLD", "label": "elexon_ssp_calibration_full",
                 "detail": "variables: a, b"},
            ],
            "links": [{"cause_id": "EVIDENCE::x", "consequence_id": "WORLD::x", "kind": "produces"}],
        },
    }
    data.update(overrides)
    return data


def test_mutation_max_ratio_change_follows_in_pixels():
    """Change the max-under-representation ratio -- the rendered ratio must
    follow, proving the number is data-driven, not hardcoded on the page."""
    data = _base_available_data()
    data["exposure_tail"]["rows"][0]["under_representation_x"] = 42.5
    out = _render(data)
    tail = out["fid-tail"]["innerHTML"]
    assert "42.5" in tail


def test_mutation_worst_cell_change_follows_in_pixels():
    """Change the worst-cell id/regime -- the rendered cell + chip must follow."""
    data = _base_available_data()
    data["worst_cell"]["cell"] = "y2019"
    data["worst_cell"]["year"] = "2019"
    data["worst_cell"]["regime"] = "calm"
    out = _render(data)
    worst = out["fid-worst"]["innerHTML"]
    assert "y2019" in worst
    assert '<span class="chip blue">calm</span>' in worst
    assert "y2022" not in worst


def test_mutation_live_recomputed_basis_note_follows():
    data = _base_available_data()
    data["exposure_tail"]["basis"] = "live_recomputed"
    out = _render(data)
    tail = out["fid-tail"]["innerHTML"]
    assert "live-recomputed" in tail
    assert "cited from" not in tail


def test_fail_closed_when_data_unavailable():
    """available:false must produce a VISIBLE failure, never a silently empty panel."""
    out = _render({"available": False, "note": "ledger has zero records for this atom"})
    tail = out["fid-tail"]["innerHTML"]
    assert "gap-fail" in tail
    assert "No fidelity evidence yet" in tail
    assert "ledger has zero records" in tail
    assert out["fid-worst"]["innerHTML"] == ""
    assert out["fid-chain"]["innerHTML"] == ""
    assert out["fid-mae"]["innerHTML"] == ""


def test_fail_closed_when_null_payload():
    """No JSON body at all (fetch resolved to null/undefined-shaped) must still
    render a visible failure, never throw or blank silently."""
    out = _render(None)
    assert "gap-fail" in out["fid-tail"]["innerHTML"]


def test_fail_closed_when_exposure_tail_unavailable_but_rest_present():
    """The exposure-tail's own independent failure domain (e.g. live
    recomputation AND the cited fallback both failed) must fail closed and
    visible WITHOUT blanking the rest of the page (worst-cell, chain, MAE
    reading are independent sections)."""
    data = _base_available_data(exposure_tail={"available": False, "note": "no data at all"})
    out = _render(data)
    tail = out["fid-tail"]["innerHTML"]
    assert "gap-fail" in tail
    assert "no data at all" in tail
    # The rest of the page must still render -- one section's failure does not
    # blank the others.
    assert "y2022" in out["fid-worst"]["innerHTML"]
    assert "residual_demand_scarcity_price_calibration" in out["fid-chain"]["innerHTML"]


def test_fail_closed_when_exposure_tail_rows_empty():
    """An empty rows list (data drained) must render a visible failure, not blank."""
    data = _base_available_data()
    data["exposure_tail"]["rows"] = []
    out = _render(data)
    tail = out["fid-tail"]["innerHTML"]
    assert "gap-fail" in tail
    assert tail.strip() != ""


def test_fail_closed_when_inspection_chain_unavailable():
    data = _base_available_data(inspection_chain={"available": False, "note": "chain construction failed"})
    out = _render(data)
    chain = out["fid-chain"]["innerHTML"]
    assert "gap-fail" in chain
    assert "chain construction failed" in chain
