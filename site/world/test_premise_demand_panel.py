"""Render-side tests for the World-door DEMAND-ARROW evidence panel
(site/world/index.html :: renderPremiseDemand).

The DATA side (tools/generate_premise_demand_data.py) is tested separately in
tests/tools/test_generate_premise_demand_data.py. THIS suite tests the RENDER: it
executes the page's ACTUAL inline JavaScript (via the Node/vm harness) against the
real generated site/data/premise_demand.json and against synthetic mutation cases,
then asserts on the produced HTML -- the rendered pixel (R11), not the source string.

R11 (verify to the rendered value): the worst-cell two-level bar must render the
live measured MAE (2276 L2 / 2190 no-skill MW) and n_train (3337) that appear in
the committed coupled-gap ledger -- the deployed pixel, not a hard-coded constant.

R15 (a control must be able to FAIL): the panel is an evidence surface -- it must
fail closed and VISIBLE when its feed is absent / available:false / has no cells,
never a silently empty or fabricated bar. Each mutation below feeds the panel its
named defect and asserts a red failure block, and one mutation flips the rendered
MAE to prove the pixel tracks the data (independence, not a baked-in string).
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
PROJECT = HERE.parent.parent  # site/world -> repo root
WORLD_JSON = PROJECT / "site" / "data" / "world.json"
FEED = PROJECT / "site" / "data" / "premise_demand.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(premise: dict | None) -> dict:
    """Run the page's renderPremiseDemand against `premise`; return element bodies.

    The harness reads world.json on stdin (argv slots 3-7 unused -> "") and the
    premise-demand feed as argv[8]. When `premise` is None we pass no argv[8], so
    the panel receives null (the absent-feed R15 case).
    """
    import tempfile

    world = json.loads(WORLD_JSON.read_text()) if WORLD_JSON.exists() else {}
    args = [NODE, str(HARNESS), str(INDEX), "", "", "", "", ""]
    tmp = None
    if premise is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(premise, tmp)
        tmp.close()
        args.append(tmp.name)
    proc = subprocess.run(
        args, input=json.dumps(world), capture_output=True, text=True, timeout=30
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live_feed() -> dict:
    """The real feed the generator emits (built fresh, not read off disk)."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_premise_demand_data import build

    return build()


# ---------------------------------------------------------------- R11: live pixel

def test_worst_cell_bar_renders_live_mae_and_n():
    feed = _live_feed()
    assert feed.get("available") is True
    out = _render(feed)
    bar = out["pd-bar"]["innerHTML"]
    # The measured worst-cell MAE (L2 2276 MW, no-skill 2190 MW) is rendered.
    assert ("2,276" in bar or "2276" in bar), bar
    assert ("2,190" in bar or "2190" in bar), bar
    # N of the worst cell is stated on the bar (never an unlabelled figure).
    assert "823" in bar
    # n_train appears in the basis line.
    basis = out["pd-basis"]["innerHTML"]
    assert ("3,337" in basis or "3337" in basis), basis


def test_per_cell_table_renders_every_cell_with_its_n():
    feed = _live_feed()
    out = _render(feed)
    tbl = out["pd-table"]["innerHTML"]
    for label in ("Winter", "Cold", "Shoulder", "Warm", "Summer"):
        assert label in tbl, f"{label} missing from table"
    # N stated per cell (RC6: rates/distributions with N, never a bare total).
    assert "1,160" in tbl  # shoulder N
    assert "823" in tbl    # summer N


def test_honest_near_tie_is_on_surface_not_hidden():
    # R12/R15: the worst-cell near-tie (CWV barely helps) must be stated, and the
    # L2 worst-cell bar labelled worse-than-no-skill (gap 1.039 > 1), not flattered.
    feed = _live_feed()
    out = _render(feed)
    bar = out["pd-bar"]["innerHTML"].lower()
    assert "near-tie" in bar
    assert "worse than no-skill" in bar


# ---------------------------------------------------------------- R15: must FAIL

def test_absent_feed_fails_closed_visible():
    out = _render(None)  # feed did not load at all
    intro = out["pd-intro"]["innerHTML"]
    assert "unavailable" in intro.lower()
    assert "var(--red)" in intro  # visibly red, not a silent blank
    assert out["pd-bar"]["innerHTML"] == ""  # no fabricated bar


def test_available_false_fails_closed_visible():
    out = _render({"available": False, "reason": "ledger missing block", "cells": []})
    intro = out["pd-intro"]["innerHTML"]
    assert "unavailable" in intro.lower()
    assert "ledger missing block" in intro  # the reason is surfaced
    assert out["pd-bar"]["innerHTML"] == ""


def test_empty_cells_fails_closed_visible():
    out = _render({"available": True, "cells": [], "worst": {}})
    assert "unavailable" in out["pd-intro"]["innerHTML"].lower()
    assert out["pd-table"]["innerHTML"] == ""


def test_rendered_mae_tracks_the_data_not_a_constant():
    # R15 independence: mutate the worst-cell headline (L2) MAE to a sentinel value
    # that appears nowhere else in the feed; the rendered L2 bar must follow it,
    # proving the pixel is data-driven, not a baked-in "2276" string.
    feed = _live_feed()
    baseline = _render(feed)["pd-bar"]["innerHTML"]
    assert "31337" not in baseline  # sentinel is genuinely novel
    feed["worst"]["mae_model"] = 31337
    for c in feed["cells"]:
        if c["key"] == feed["worst_cell"]:
            c["mae_model"] = 31337
    bar = _render(feed)["pd-bar"]["innerHTML"]
    assert "31,337" in bar or "31337" in bar
    # The L2 "headline" bar specifically carries the mutated value.
    l2seg = bar.split("headline")[1]
    assert "31,337" in l2seg or "31337" in l2seg
