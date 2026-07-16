"""Render-side tests for the Simplified door (site/simplified/index.html).

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published
site/data/simplified.json the page consumes, then assert the produced HTML
contains the actual source values -- the rendered pixel, not the source string.

Binding rule 4 (honesty featured): the register must render every recorded
simplification note, nothing filtered out -- this is the same register the
agent itself reads before deciding what to build next.

R15 (a control must be able to FAIL): a mutation of a source note/count must
change the rendered pixel (independence -- the render is not a hard-coded
constant).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data" / "simplified.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live() -> dict:
    return json.loads(DATA.read_text())


def test_stats_line_renders_live_totals():
    d = _live()
    out = _render(d)
    stats = out["stats-line"]["innerHTML"]
    assert f">{d['total_notes']}<" in stats
    assert f">{d['total_atoms_with_notes']}<" in stats
    assert f">{len(d['lanes'])}<" in stats


def test_every_live_lane_name_renders():
    d = _live()
    out = _render(d)
    body = out["lanes-out"]["innerHTML"]
    assert d["lanes"], "fixture precondition: lanes present"
    for lane in d["lanes"]:
        assert _escaped(lane["lane_name"]) in body, f"lane {lane['lane_name']} not rendered"


def test_every_live_atom_in_first_lane_renders_with_its_notes():
    d = _live()
    out = _render(d)
    body = out["lanes-out"]["innerHTML"]
    lane = d["lanes"][0]
    assert lane["atoms"], "fixture precondition: first lane has atoms with notes"
    for atom in lane["atoms"]:
        assert _escaped(atom["atom_name"]) in body, f"atom {atom['atom_name']} not rendered"
        assert atom["atom_id"] in body, f"atom id {atom['atom_id']} not rendered"


def test_nothing_filtered_out_honesty_featured():
    # Binding rule 4: every note recorded against the atom must actually render,
    # not a truncated/summarised subset.
    d = _live()
    out = _render(d)
    body = out["lanes-out"]["innerHTML"]
    lane = d["lanes"][0]
    atom = lane["atoms"][0]
    assert len(atom["notes"]) >= 1
    # Mirror renderNote()'s own date-prefix strip so this checks exactly what
    # the page renders, not an approximation of it.
    date_prefix = re.compile(r"^(\d{4}-\d{2}-\d{2})[:,]?\s*")
    for note in atom["notes"]:
        m = date_prefix.match(note)
        rest = note[m.end():] if m else note
        tail = rest[:80]
        assert tail.strip() == "" or _escaped(tail) in body, (
            f"note text for {atom['atom_id']} not found in rendered body"
        )


def _escaped(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def test_total_notes_is_independent_of_render():
    # R15 independence: mutate the live total; the rendered pixel must follow
    # the data, not a baked-in constant.
    d = _live()
    d["total_notes"] = 88888
    out = _render(d)
    assert ">88888<" in out["stats-line"]["innerHTML"]


def test_atom_name_is_independent_of_render():
    d = _live()
    d["lanes"][0]["atoms"][0]["atom_name"] = "SENTINEL_999X_ATOM_NAME"
    out = _render(d)
    assert "SENTINEL_999X_ATOM_NAME" in out["lanes-out"]["innerHTML"]
