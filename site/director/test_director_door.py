"""Render-side tests for the Director window (site/director/index.html).

Surface 5 of the SITE_V5 rebuild: the off-nav authenticated-ops pane whose single
job is (1) the RESERVED QUEUE -- the decisions the machine parked for the director
-- and (2) MACHINE HEALTH -- the live daemon set, honest about what is stale.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data JSON the
page consumes, then assert the produced HTML contains the actual source values --
i.e. the rendered pixel, not the source string. The clock is PINNED (data.now) so
time-relative renders (reserved-item age, daemon-heartbeat staleness) are
deterministic.

R15 (a control must be able to FAIL): machine health's named defect is a dead
daemon -- a stale heartbeat must render a VISIBLE red STALE badge and flip the
Stale KPI to alarm, never a silent green. An empty daemon table must render a
visible failure block. The reserved queue's overload must alarm. These are
exercised below with mutations.
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

# Pinned clock for deterministic time-relative renders.
NOW = "2026-07-23T16:20:00+00:00"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict) -> dict:
    data = dict(data)
    data.setdefault("now", NOW)
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
        "reserved": json.loads((DATA / "director_reserved.json").read_text()),
        "health": json.loads((DATA / "agent_status.json").read_text()),
        "now": NOW,
    }


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# --------------------------------------------------------------------------- #
# R11: the two MVP panels render the LIVE published data values.
# --------------------------------------------------------------------------- #
def test_reserved_queue_renders_live_items():
    d = _live()
    out = _render(d)
    items = d["reserved"].get("items", [])
    body = out["reserved-body"]["innerHTML"]
    if items:
        for it in items:
            assert it["item_id"] in body, f"missing reserved item {it['item_id']}"
            # The concrete ask (What:) must be rendered, not just the id.
            assert "What:" in body
    else:
        assert "empty" in body.lower(), body
    # Director-hours estimate rendered to 2dp in the reserved KPIs.
    dh = d["plan"]["director_hours"]
    kpis = out["reserved-kpis"]["innerHTML"]
    assert f"{dh['estimated_director_hours_per_day']:.2f}" in kpis


def test_reserved_open_count_matches_feed():
    d = _live()
    out = _render(d)
    n = len(d["reserved"].get("items", []))
    kpis = out["reserved-kpis"]["innerHTML"]
    assert f'<div class="kpi-v">{n}</div>' in kpis, kpis


def test_reserved_states_falsifiable_claim():
    out = _render(_live())
    hyp = out["reserved-hyp"]["innerHTML"]
    assert "Falsifiable claim" in hyp
    assert "may NOT take itself" in hyp


def test_health_renders_every_live_daemon():
    d = _live()
    out = _render(d)
    agents = d["health"]["agents"]
    body = out["health-body"]["innerHTML"]
    assert agents, "fixture precondition: agent_status should list daemons"
    for a in agents:
        assert a["name"] in body, f"daemon {a['name']} not rendered"
    # Daemons-tracked KPI equals the real count.
    kpis = out["health-kpis"]["innerHTML"]
    assert f'<div class="kpi-v">{len(agents)}</div>' in kpis


def test_health_states_freshness_window_and_can_fail():
    out = _render(_live())
    hyp = out["health-hyp"]["innerHTML"]
    assert "6h" in hyp
    assert "STALE" in hyp
    assert "can fail" in hyp.lower()


# --------------------------------------------------------------------------- #
# R15: machine health FAILS VISIBLY on its named defect (a dead daemon).
# --------------------------------------------------------------------------- #
def test_stale_daemon_renders_stale_and_alarms():
    d = _live()
    d["health"] = json.loads(json.dumps(d["health"]))
    # A daemon whose last heartbeat is a week before the pinned clock is dead.
    d["health"]["agents"] = [
        {"name": "zombie-daemon", "status": "idle",
         "last_heartbeat": "2026-07-16T00:00:00+00:00", "anomaly": None},
    ]
    out = _render(d)
    body = out["health-body"]["innerHTML"]
    kpis = out["health-kpis"]["innerHTML"]
    assert "STALE" in body, "a week-old heartbeat must render the STALE badge"
    assert "alarm" in kpis, "a stale daemon must flip the Stale KPI to alarm"


def test_live_daemon_renders_live_not_stale():
    d = _live()
    d["health"] = json.loads(json.dumps(d["health"]))
    d["health"]["agents"] = [
        {"name": "fresh-daemon", "status": "idle",
         "last_heartbeat": "2026-07-23T16:10:00+00:00", "anomaly": None},
    ]
    out = _render(d)
    body = out["health-body"]["innerHTML"]
    assert ">LIVE<" in body, "a 10-min-old heartbeat must render LIVE"
    assert "STALE" not in body


def test_daemon_anomaly_renders():
    d = _live()
    d["health"] = json.loads(json.dumps(d["health"]))
    d["health"]["agents"] = [
        {"name": "faulty-daemon", "status": "idle",
         "last_heartbeat": NOW, "anomaly": "wrote 0-byte output twice"},
    ]
    out = _render(d)
    body = out["health-body"]["innerHTML"]
    kpis = out["health-kpis"]["innerHTML"]
    assert "wrote 0-byte output twice" in body, "a self-reported anomaly must render"
    assert "alarm" in kpis


def test_empty_health_table_fails_visibly():
    d = _live()
    d["health"] = {"agents": [], "last_updated": NOW}
    out = _render(d)
    body = out["health-body"]["innerHTML"]
    assert "fail" in body.lower(), "an empty daemon table must render a visible failure"


# --------------------------------------------------------------------------- #
# R15: the reserved queue alarms on overload and states an empty queue plainly.
# --------------------------------------------------------------------------- #
def test_reserved_overload_alarms():
    d = _live()
    d["reserved"] = {
        "generated_at": NOW, "open_count": 5,
        "items": [
            {"item_id": f"decision-{i}", "what": "sign the ratio", "how": "reply",
             "why": "one-way door", "first_asked_at": NOW}
            for i in range(5)
        ],
    }
    out = _render(d)
    kpis = out["reserved-kpis"]["innerHTML"]
    body = out["reserved-body"]["innerHTML"]
    assert "alarm" in kpis, "more than 3 open reserved items must raise the alarm class"
    assert "decision-0" in body and "sign the ratio" in body


def test_reserved_empty_states_plainly():
    d = _live()
    d["reserved"] = {"generated_at": NOW, "open_count": 0, "items": []}
    out = _render(d)
    body = out["reserved-body"]["innerHTML"]
    assert "empty" in body.lower()


def test_old_reserved_item_flags_age_alarm():
    d = _live()
    d["reserved"] = {
        "generated_at": NOW, "open_count": 1,
        "items": [
            {"item_id": "stale-ask", "what": "decide the curriculum world",
             "how": "reply", "why": "R13 dial", "first_asked_at": "2026-07-18T00:00:00+00:00"},
        ],
    }
    out = _render(d)
    kpis = out["reserved-kpis"]["innerHTML"]
    # >48h waiting must raise the "oldest waiting" alarm.
    assert "alarm" in kpis
    body = out["reserved-body"]["innerHTML"]
    assert "stale-ask" in body


# --------------------------------------------------------------------------- #
# Deeper-context governance panels (unchanged behaviour, still rendered).
# --------------------------------------------------------------------------- #
def test_twin_fidelity_renders_live_counts():
    d = _live()
    out = _render(d)
    f = d["twin"]["fidelity"]
    kpis = out["twin-kpis"]["innerHTML"]
    assert f">{f['answered']}<" in kpis, kpis
    assert f"v{f['canon_version']}" in kpis
    assert f"{f['overturn_rate'] * 100:.1f}%" in kpis


def test_empty_qa_history_fails_visibly():
    d = _live()
    d["twin"] = {"fidelity": d["twin"]["fidelity"], "recent_qa": [], "note": ""}
    out = _render(d)
    body = out["qa-body"]["innerHTML"]
    assert "fail" in body.lower()


def test_overturn_flips_alarm_class():
    d = _live()
    d["twin"]["fidelity"] = dict(d["twin"]["fidelity"])
    d["twin"]["fidelity"]["overturned"] = 3
    d["twin"]["fidelity"]["overturn_rate"] = 0.25
    out = _render(d)
    kpis = out["twin-kpis"]["innerHTML"]
    assert "alarm" in kpis


def test_plan_is_diagnostic_not_target_text_present():
    out = _render(_live())
    passport = out["plan-passport"]["innerHTML"]
    assert "diagnostic" in passport.lower()


def test_curriculum_is_director_reserved_and_no_fake_auth():
    out = _render(_live())
    note = out["curriculum-note"]["innerHTML"]
    assert "DIRECTOR-RESERVED" in note
    assert "does not render a write UI" in note or "console-only" in note


# --------------------------------------------------------------------------- #
# Honesty of the access model: reads are open (off-nav/noindex), and the ONLY
# authenticated affordance is the server-checked comment box -- no theatre lock.
# --------------------------------------------------------------------------- #
def test_no_fake_read_gate():
    # There must be no client-side PIN veil pretending to gate the read view --
    # a lock that opens with any key is theatre (R15). The ops content must NOT
    # be hidden behind such a gate.
    src = INDEX.read_text()
    assert 'class="veil"' not in src and 'id="veil"' not in src
    assert "ops-hidden" not in src
    assert '<div id="ops">' in src, "the ops pane renders open, not behind a fake lock"


def test_access_model_is_honestly_stated():
    src = INDEX.read_text()
    assert 'id="access-banner"' in src
    assert "noindex" in src
    assert "theatre" in src            # names the failure mode it avoids
    assert "server-side" in src        # the real auth is the server-checked PIN
    assert "console-only" in src


def test_authenticated_write_channel_is_the_comments_box():
    # "Reuse the comments-box auth pattern" -> the real server-checked write
    # channel is included on the pane.
    src = INDEX.read_text()
    assert "../shared/director-comments.js" in src
