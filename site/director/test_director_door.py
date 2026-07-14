"""Render-side tests for the Director door (site/director/index.html).

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data JSON the
page consumes, then assert the produced HTML contains the actual source values --
i.e. the rendered pixel, not the source string.

R15 (a control must be able to FAIL): the Q&A panel is a visible surface -- a
mutation that empties the twin history must produce a VISIBLE red failure block,
never a silently empty panel. The overturn KPI must flip to an alarm class when a
twin answer was overturned. These are exercised below.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data"

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
    return {
        "twin": json.loads((DATA / "director_twin.json").read_text()),
        "plan": json.loads((DATA / "provisional_plan.json").read_text()),
        "sys": json.loads((DATA / "system_status.json").read_text()),
    }


# --------------------------------------------------------------------------- #
# R11: the door renders the LIVE published data values.
# --------------------------------------------------------------------------- #
def test_twin_fidelity_renders_live_counts():
    d = _live()
    out = _render(d)
    f = d["twin"]["fidelity"]
    kpis = out["twin-kpis"]["innerHTML"]
    # Answered count from the actual file must appear as a rendered value.
    assert f">{f['answered']}<" in kpis, kpis
    # Canon version rendered with the v-prefix.
    assert f"v{f['canon_version']}" in kpis
    # Overturn rate rendered as a percentage of the real value.
    pct = f"{f['overturn_rate'] * 100:.1f}%"
    assert pct in kpis


def test_action_queue_renders_live_files():
    d = _live()
    out = _render(d)
    q = d["sys"]["staging_queue"]
    body = out["queue-body"]["innerHTML"]
    if q:
        # Every real queued filename must be rendered.
        for it in q:
            assert it["filename"] in body, f"missing {it['filename']} in {body}"
    else:
        assert "Queue empty" in body
    # Director-hours estimate rendered to 2dp.
    dh = d["plan"]["director_hours"]
    kpis = out["queue-kpis"]["innerHTML"]
    assert f"{dh['estimated_director_hours_per_day']:.2f}" in kpis
    assert f">{dh['from_rich_touches']}<" in kpis or str(dh["from_rich_touches"]) in kpis


def test_qa_history_renders_live_questions():
    d = _live()
    out = _render(d)
    qa = d["twin"]["recent_qa"]
    body = out["qa-body"]["innerHTML"]
    assert qa, "fixture precondition: live twin should have recorded Q&A"
    # First recorded question text must be rendered (escaped, but text preserved).
    first_q = qa[0]["question"]
    assert first_q[:30] in body or _esc(first_q)[:30] in body


def test_plan_confidence_tiers_render_live():
    d = _live()
    out = _render(d)
    ct = d["plan"]["confidence_tiers"]
    body = out["plan-body"]["innerHTML"]
    for epoch, conf in ct.items():
        assert f"Epoch {epoch}" in body
        assert conf in body


def test_plan_is_diagnostic_not_target_text_present():
    # Law A must be rendered verbatim on the surface (governance honesty).
    out = _render(_live())
    passport = out["plan-passport"]["innerHTML"]
    assert "diagnostic" in passport.lower()
    assert "never a target" in passport.lower() or "never a target".replace(" ", "") in passport.lower().replace(" ", "")


def test_curriculum_is_director_reserved_and_no_fake_auth():
    out = _render(_live())
    note = out["curriculum-note"]["innerHTML"]
    assert "DIRECTOR-RESERVED" in note
    # Must be explicit that no write/dials UI is rendered (no fake auth).
    assert "does not render a write UI" in note or "console-only" in note


# --------------------------------------------------------------------------- #
# R15: the surface must FAIL VISIBLY on its named defects.
# --------------------------------------------------------------------------- #
def test_empty_qa_history_fails_visibly():
    d = _live()
    d["twin"] = {"fidelity": d["twin"]["fidelity"], "recent_qa": [], "note": ""}
    out = _render(d)
    body = out["qa-body"]["innerHTML"]
    assert "fail" in body.lower(), "empty twin history must render a visible failure, not empty"


def test_overturn_flips_alarm_class():
    d = _live()
    d["twin"]["fidelity"] = dict(d["twin"]["fidelity"])
    d["twin"]["fidelity"]["overturned"] = 3
    d["twin"]["fidelity"]["overturn_rate"] = 0.25
    out = _render(d)
    kpis = out["twin-kpis"]["innerHTML"]
    assert "alarm" in kpis, "a nonzero overturn count must raise the alarm KPI class"


def test_overloaded_staging_queue_alarms():
    d = _live()
    d["sys"] = json.loads(json.dumps(d["sys"]))
    d["sys"]["staging_queue"] = [
        {"filename": f"f{i}.md", "modified_at": "2026-07-14T00:00:00Z", "size_bytes": 10}
        for i in range(5)
    ]
    out = _render(d)
    kpis = out["queue-kpis"]["innerHTML"]
    assert "alarm" in kpis, "a backed-up staging queue (>3) must raise the alarm class"


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
