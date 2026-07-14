"""Render-side tests for the Proof-door CONTROL KILL-LIST panel (site/proof/index.html).

The DATA side (control_killlist) is generated into site/data/proof.json by the proof-data
pipeline. THIS suite tests the RENDER: it executes the page's actual inline JavaScript (via a
Node/vm harness) against the real published data and against synthetic mutation cases, then
asserts on the produced HTML -- i.e. the rendered pixel (R11), not the source string.

R15 (a control must be able to FAIL): the kill-list panel is itself a control surface -- it
re-classifies each control by result/severity, sorts THEATRE controls to the top in red, alarms
on any theatre_remaining>0, and catches a header/row count mismatch. Each mutation below feeds
the panel its named defect and asserts the panel fires: a THEATRE control -> red chip at the top;
theatre_remaining>0 -> alarm; a mismatched header count -> a visible red failure; absent /
available:false / empty controls -> a visible red 'unavailable' block, never a silently missing
panel.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_killlist_harness.mjs"
PROOF_JSON = HERE.parent / "data" / "proof.json"  # site/data/proof.json

NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(control_killlist) -> dict:
    """Run the page's inline renderKilllist against {control_killlist: ...}; return contents."""
    payload = {} if control_killlist is _MISSING else {"control_killlist": control_killlist}
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


_MISSING = object()


def _live_killlist() -> dict:
    """The real control_killlist block published in site/data/proof.json."""
    d = json.loads(PROOF_JSON.read_text())
    return d["control_killlist"]


# --------------------------------------------------------------------------- #
# R11: the panel renders the LIVE published proof.json.control_killlist values.
# --------------------------------------------------------------------------- #
def test_live_data_renders_every_control():
    ck = _live_killlist()
    assert ck.get("available") is True
    out = _render(ck)
    body = out["killlist"]["innerHTML"]

    # Every control name must appear as a rendered row (none silently dropped).
    for c in ck["controls"]:
        assert c["name"] in body, f"{c['name']} not rendered"

    # Exactly one <tr> per control (plus none extra).
    assert body.count("<tr") == len(ck["controls"]) + 1  # +1 header row

    # KPI strip reflects the published cumulative counts (pixel == number, R11).
    kpis = out["kl-kpis"]["innerHTML"]
    assert str(ck["controls_total"]) in kpis
    assert str(ck["mutation_proven"]) in kpis
    assert str(ck["theatre_remaining"]) in kpis


def test_live_theatre_controls_render_red_and_first():
    """Any control the published data marks THEATRE / severity red must render as a red chip,
    sorted above the green (proven) rows."""
    ck = _live_killlist()
    out = _render(ck)
    body = out["killlist"]["innerHTML"]

    theatre = [c for c in ck["controls"]
               if str(c.get("result", "")).upper().find("THEATRE") >= 0
               or str(c.get("severity", "")).lower() == "red"]
    if not theatre:
        pytest.skip("no theatre controls in current published data")

    # Red chip present for the theatre control(s).
    assert 'class="chip red"' in body
    assert "kl-theatre" in body
    # First rendered data row is a theatre (red) row -- sorted to the top.
    first_row_start = body.find("<tr", body.find("<tbody"))
    assert 'class="kl-theatre"' in body[first_row_start:first_row_start + 40]


def test_live_theatre_remaining_alarms_when_positive():
    ck = _live_killlist()
    out = _render(ck)
    alarms = out["kl-alarms"]["innerHTML"]
    if ck.get("theatre_remaining", 0) > 0:
        assert "theatre control" in alarms and "gap-alarm" in alarms
        # theatre_remaining KPI carries the alarm styling.
        assert "kpi alarm" in out["kl-kpis"]["innerHTML"]
    else:
        assert alarms == ""


# --------------------------------------------------------------------------- #
# R15 mutation tests: feed the panel each named defect; assert the control fires.
# --------------------------------------------------------------------------- #
def _one_control(**over):
    c = {
        "name": "check_thing", "location": "company/x.py::check_thing",
        "catches": "a named defect", "mutation": "inject the defect",
        "killer_pattern": "clean", "mutation_tested": True, "fires_on_defect": True,
        "result": "FIRED", "chip": "proven", "severity": "green",
        "last_verified": "2026-07-13",
    }
    c.update(over)
    return c


def _wrap(controls, **over):
    theatre = sum(1 for c in controls
                  if str(c.get("result", "")).upper().find("THEATRE") >= 0
                  or str(c.get("severity", "")).lower() == "red")
    ck = {
        "available": True, "source": "docs/design/control_registry.json",
        "doctrine": "docs/staging/CONTROLS_THAT_CANNOT_FAIL.md",
        "last_verified": "2026-07-13",
        "controls_total": len(controls),
        "mutation_tested": len(controls),
        "mutation_proven": sum(1 for c in controls if str(c.get("severity")).lower() == "green"),
        "theatre_remaining": theatre,
        "structural_only": sum(1 for c in controls if str(c.get("severity")).lower() == "amber"),
        "controls": controls,
    }
    ck.update(over)
    return ck


def test_mutation_theatre_control_renders_red_top():
    theatre = _one_control(name="check_vat_arithmetic", killer_pattern="TAUTOLOGY",
                           result="THEATRE", chip="theatre", severity="red",
                           fires_on_defect=False)
    green = _one_control(name="range_invariant_check")
    out = _render(_wrap([green, theatre]))  # theatre listed second, must sort first
    body = out["killlist"]["innerHTML"]
    assert '<span class="chip red">THEATRE</span>' in body
    # theatre row is first data row despite being second in the input.
    vat_pos = body.find("check_vat_arithmetic")
    range_pos = body.find("range_invariant_check")
    assert 0 <= vat_pos < range_pos, "theatre control must sort above proven controls"
    # 'does NOT fire' indicator present for the theatre control.
    assert "does NOT fire" in body


def test_mutation_theatre_remaining_positive_alarms():
    theatre = _one_control(result="THEATRE", chip="theatre", severity="red", fires_on_defect=False)
    out = _render(_wrap([theatre]))
    assert "gap-alarm" in out["kl-alarms"]["innerHTML"]
    assert "kpi alarm" in out["kl-kpis"]["innerHTML"]


def test_mutation_all_green_no_alarm():
    out = _render(_wrap([_one_control(), _one_control(name="rate_invariant_check")]))
    assert out["kl-alarms"]["innerHTML"] == ""
    body = out["killlist"]["innerHTML"]
    assert 'class="chip red"' not in body


def test_mutation_structural_only_renders_amber():
    struct = _one_control(name="llm_judge_evaluators_structural", result="STRUCTURAL-ONLY",
                          chip="structural_only", severity="amber", mutation_tested=False,
                          fires_on_defect=None, killer_pattern="partial-coverage")
    out = _render(_wrap([struct]))
    body = out["killlist"]["innerHTML"]
    assert 'class="chip amber"' in body


def test_mutation_count_mismatch_caught():
    """Header claims a different theatre_remaining than the rows classify -> visible red failure.
    This is the panel's own R15 self-consistency control firing."""
    theatre = _one_control(result="THEATRE", chip="theatre", severity="red", fires_on_defect=False)
    ck = _wrap([theatre])
    ck["theatre_remaining"] = 5  # lie: 1 red row, header says 5
    out = _render(ck)
    alarms = out["kl-alarms"]["innerHTML"]
    assert "gap-fail" in alarms
    assert "Count mismatch" in alarms


# --------------------------------------------------------------------------- #
# R15 fail-closed: absent / available:false / empty must be VISIBLE, never blank.
# --------------------------------------------------------------------------- #
def test_fail_closed_when_data_unavailable():
    out = _render({"available": False, "note": "registry not readable"})
    body = out["killlist"]["innerHTML"]
    assert "gap-fail" in body
    assert "not available" in body
    assert body.strip() != ""


def test_fail_closed_when_controls_empty():
    out = _render(_wrap([]))  # zero controls
    body = out["killlist"]["innerHTML"]
    assert "gap-fail" in body
    assert body.strip() != ""


def test_missing_control_killlist_key_fails_visible():
    out = _render(_MISSING)  # proof.json with no control_killlist block at all
    body = out["killlist"]["innerHTML"]
    assert "gap-fail" in body
    assert body.strip() != ""
