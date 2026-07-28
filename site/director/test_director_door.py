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
        "decisions": json.loads((DATA / "decisions.json").read_text()),
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
# Honesty of the access model: reads are open (off-nav/noindex), and this pane
# now carries NO write affordance -- the PIN-authenticated page-comment box was
# retired as a director-authority path on 2026-07-24 (director ruling).
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
    assert "retired" in src            # the page-comment authority path is retired (2026-07-24 ruling)
    assert "console-only" in src


def test_page_comment_write_channel_is_retired():
    # DIRECTOR RULING 2026-07-24: the PIN-authenticated page-comment channel was
    # decommissioned as a director-authority path. The widget must be GONE from
    # this pane (no script tag, no server-side-PIN claim), and the banner must
    # honestly state the retirement rather than advertise an authenticated box.
    src = INDEX.read_text()
    assert "director-comments.js" not in src, "retired widget must be removed from the pane"
    assert "retired" in src.lower()


# --------------------------------------------------------------------------- #
# DELTA VIEW: "what changed since I last looked" (backlog item, ranked back in
# 2026-07-28). Client-side only -- a localStorage marker in the visitor's own
# browser, compared against the SAME published feeds already on the page
# (decisions.json, director_reserved.json, agent_status.json). No new
# server/auth affordance: the harness seeds/observes localStorage directly
# (see _render_harness.mjs's `lastSeenSnapshot` input and `__localStorage`
# output) so both the R11 rendered-pixel claim and the R15 mutation/honesty
# proof are against the REAL inline script, not a reimplementation.
# --------------------------------------------------------------------------- #
def _render_with_snapshot(data: dict, snapshot) -> dict:
    data = dict(data)
    data["lastSeenSnapshot"] = snapshot
    return _render(data)


def test_delta_first_visit_renders_honestly_not_a_fabricated_zero():
    # No prior marker in this browser -> must say so plainly, not show 0/0/0 as if
    # a real comparison happened (that would be a fabricated, misleadingly-precise
    # delta -- the R15 fail-open shape this test guards against).
    out = _render(_live())
    body = out["delta-body"]["innerHTML"]
    kpis = out["delta-kpis"]["innerHTML"]
    assert "first visit" in body.lower(), body
    assert "kpi-v" not in kpis, "a first visit must render no KPI numbers at all, not fabricated zeros"


def test_delta_new_decision_flips_the_pixel():
    # R11/R15 FIRES: a decision newer than the stored marker must move the rendered count.
    d = _live()
    d["decisions"] = {"decisions": [
        {"timestamp": "2026-07-23T15:00:00+00:00", "what": "a fresh decision", "why": "x"},
    ]}
    d["reserved"] = {"generated_at": NOW, "open_count": 0, "items": []}
    d["health"] = {"agents": [], "last_updated": NOW}
    snapshot = {
        "seen_at": "2026-07-20T00:00:00+00:00",
        "latest_decision_ts": "2026-07-10T00:00:00+00:00",
        "reserved_ids": [],
        "stale_daemons": [],
    }
    out = _render_with_snapshot(d, snapshot)
    kpis = out["delta-kpis"]["innerHTML"]
    body = out["delta-body"]["innerHTML"]
    assert '<div class="kpi-v">1</div>' in kpis, kpis
    assert "warn" in kpis
    assert "<b>1</b> new decision" in body, body


def test_delta_reserved_change_flips_the_pixel():
    d = _live()
    d["decisions"] = {"decisions": []}
    d["health"] = {"agents": [], "last_updated": NOW}
    d["reserved"] = {"generated_at": NOW, "open_count": 1, "items": [
        {"item_id": "new-ask", "what": "decide something", "how": "reply",
         "why": "one-way door", "first_asked_at": NOW},
    ]}
    snapshot = {
        "seen_at": "2026-07-20T00:00:00+00:00",
        "latest_decision_ts": None,
        "reserved_ids": [],
        "stale_daemons": [],
    }
    out = _render_with_snapshot(d, snapshot)
    kpis = out["delta-kpis"]["innerHTML"]
    body = out["delta-body"]["innerHTML"]
    assert "1 added, 0 cleared" in kpis, kpis
    assert "warn" in kpis
    assert "reserved-queue item(s) changed" in body


def test_delta_daemon_stale_flip_alarms():
    # Named defect: a daemon that WAS healthy at last-seen and has since died must
    # alarm the delta panel, same class of failure as machine-health's own STALE proof.
    d = _live()
    d["decisions"] = {"decisions": []}
    d["reserved"] = {"generated_at": NOW, "open_count": 0, "items": []}
    d["health"] = {"agents": [
        {"name": "zombie-daemon", "status": "idle",
         "last_heartbeat": "2026-07-16T00:00:00+00:00", "anomaly": None},
    ], "last_updated": NOW}
    snapshot = {
        "seen_at": "2026-07-20T00:00:00+00:00",
        "latest_decision_ts": None,
        "reserved_ids": [],
        "stale_daemons": [],
    }
    out = _render_with_snapshot(d, snapshot)
    kpis = out["delta-kpis"]["innerHTML"]
    assert "1 newly stale" in kpis, kpis
    assert "alarm" in kpis


def test_delta_no_change_renders_honest_empty_not_blank():
    # NEUTERED direction of the R15 proof: a genuinely quiet interval must render
    # "nothing changed" with explicit zero KPIs -- never a blank/error that looks
    # indistinguishable from a broken panel.
    d = _live()
    d["decisions"] = {"decisions": [
        {"timestamp": "2026-07-10T00:00:00+00:00", "what": "old decision"},
    ]}
    d["reserved"] = {"generated_at": NOW, "open_count": 1, "items": [
        {"item_id": "steady-ask", "what": "x", "how": "y", "why": "z", "first_asked_at": NOW},
    ]}
    d["health"] = {"agents": [
        {"name": "steady-daemon", "status": "idle", "last_heartbeat": NOW, "anomaly": None},
    ], "last_updated": NOW}
    snapshot = {
        "seen_at": "2026-07-22T00:00:00+00:00",
        "latest_decision_ts": "2026-07-10T00:00:00+00:00",
        "reserved_ids": ["steady-ask"],
        "stale_daemons": [],
    }
    out = _render_with_snapshot(d, snapshot)
    kpis = out["delta-kpis"]["innerHTML"]
    body = out["delta-body"]["innerHTML"]
    assert "nothing changed" in body.lower(), body
    assert kpis.count('<div class="kpi-v">0</div>') == 3, kpis
    assert "alarm" not in kpis
    assert "warn" not in kpis


def test_delta_persists_a_snapshot_for_the_next_visit():
    # R15 fail-silent guard: if the render computed a delta but never wrote the new
    # marker back, every FUTURE visit would silently show "first visit" forever.
    d = _live()
    d["decisions"] = {"decisions": [
        {"timestamp": "2026-07-23T15:00:00+00:00", "what": "x"},
    ]}
    d["reserved"] = {"generated_at": NOW, "open_count": 1, "items": [
        {"item_id": "ask-1", "what": "x", "how": "y", "why": "z", "first_asked_at": NOW},
    ]}
    d["health"] = {"agents": [
        {"name": "steady", "status": "idle", "last_heartbeat": NOW, "anomaly": None},
    ], "last_updated": NOW}
    out = _render(d)
    stored = out["__localStorage"]["setCalls"]
    assert stored, "the render must persist a marker for the NEXT visit"
    snapshot = json.loads(stored[-1])
    assert snapshot["latest_decision_ts"] == "2026-07-23T15:00:00+00:00"
    assert snapshot["reserved_ids"] == ["ask-1"]
    assert snapshot["stale_daemons"] == []


def test_delta_is_named_a_diagnostic_not_a_target():
    # R12: delta counts are a diagnostic, never a headline/target.
    out = _render(_live())
    hyp = out["delta-hyp"]["innerHTML"]
    assert "diagnostic" in hyp.lower() and "never a target" in hyp.lower()
    passport = out["delta-passport"]["innerHTML"]
    assert "client-local marker" in passport
    assert "no server read-receipt" in passport


def test_delta_view_adds_no_new_auth_affordance():
    # A client-side gate here would be R15 theatre (per the atom brief) -- the delta
    # panel must stay pure presentation over the existing open reads, same access
    # model as the rest of the pane.
    src = INDEX.read_text()
    assert "poesys_director_delta_v1" in src
    assert 'class="veil"' not in src and 'id="veil"' not in src
    assert "ops-hidden" not in src


def test_hero_text_states_delta_view_is_live_and_client_only():
    src = INDEX.read_text()
    assert "delta view" in src.lower()
    assert "your own browser" in src.lower()
