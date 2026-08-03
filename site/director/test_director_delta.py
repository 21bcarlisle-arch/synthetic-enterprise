"""The DURABLE half of the Director-window delta view.

Atom SITE_director_window_delta_view (SPEC_005 s7.10): "what CHANGED since the
director last looked, rather than a full-state page he has to diff by eye."

The page already had a per-BROWSER localStorage marker (tested in
test_director_door.py). This module covers the half that survives a publish: a
last-look stamp committed to the repo (site/data/director_last_look.json),
diffed by tools/generate_director_data.py into site/data/director_delta.json and
rendered at the TOP of site/director/index.html.

R11 (verify to the rendered value): the render assertions execute the page's
ACTUAL inline JavaScript through the Node/vm harness and assert on the produced
innerHTML -- the rendered pixel, not the source string. Live-fetch verification
against poesys.net is pending a publish from main; the harness is the same
mechanism used by every other panel on this page.

R15 (a control must be able to FAIL). Two named defects:
  (a) FAIL-OPEN, the one the atom names explicitly -- a delta view whose
      baseline silently re-bases on every regeneration, or which treats a
      lost/blank/corrupt stamp as "everything is new" (or as a quiet "nothing
      changed"). Proved below at BOTH layers: the generator refuses to compute a
      delta from a lost stamp (changed=None, counts=None) and never advances the
      stamp on a plain regeneration; the page renders that state as a RED
      failure block carrying NO KPI numbers, textually distinguishable from the
      quiet-interval empty state.
  (b) The delta must actually FOLLOW a real change: mutate one underlying value
      and the rendered pixel moves.
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
DATA = HERE.parent / "data"
PROJECT = HERE.parent.parent

sys.path.insert(0, str(PROJECT))
from tools import generate_director_data as gdd  # noqa: E402

NOW = "2026-07-23T16:20:00+00:00"
NOW_DT = datetime(2026, 7, 23, 16, 20, tzinfo=timezone.utc)

NODE = shutil.which("node")


# --------------------------------------------------------------------------- #
# Fixtures: a self-contained site/data directory the generator can chew on.
# --------------------------------------------------------------------------- #
def _feeds(reserved_ids=(), decisions=(), daemons=(), answered=5, open_atoms=55):
    return {
        "decisions.json": {
            "generated_at": NOW,
            "count": len(decisions),
            "decisions": [
                {"timestamp": ts, "what": what} for ts, what in decisions
            ],
        },
        "director_reserved.json": {
            "generated_at": NOW,
            "open_count": len(reserved_ids),
            "items": [
                {"item_id": i, "what": "decide " + i, "how": "reply",
                 "why": "one-way door", "first_asked_at": NOW}
                for i in reserved_ids
            ],
        },
        "agent_status.json": {
            "last_updated": NOW,
            "agents": [
                {"name": name, "status": "idle", "last_heartbeat": hb, "anomaly": None}
                for name, hb in daemons
            ],
        },
        "director_twin.json": {
            "fidelity": {"answered": answered, "routed_to_director": 3,
                         "overturned": 0, "overturn_rate": 0.0, "canon_version": 3},
            "recent_qa": [],
            "note": "",
        },
        "provisional_plan.json": {
            "generated_at": NOW,
            "concurrency": {"total_open_atoms": open_atoms},
            "director_hours": {"estimated_director_hours_per_day": 0.4, "caveat": ""},
        },
    }


def _write_feeds(site_data: Path, feeds: dict):
    site_data.mkdir(parents=True, exist_ok=True)
    for name, payload in feeds.items():
        (site_data / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


FRESH = "2026-07-23T16:00:00+00:00"          # 20 min before the pinned clock
DEAD = "2026-07-16T00:00:00+00:00"           # a week before it


@pytest.fixture
def site_data(tmp_path):
    d = tmp_path / "data"
    _write_feeds(d, _feeds(
        reserved_ids=["ask-1"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision")],
        daemons=[("steady-daemon", FRESH)],
    ))
    return d


def _gen(site_data, mark_seen=False, now=NOW_DT, by="test"):
    return gdd.generate(site_data=site_data, mark_seen=mark_seen,
                        recorded_by=by, now=now)


# --------------------------------------------------------------------------- #
# R15 (a) THE FAIL-OPEN: the stamp must NOT re-base on regeneration.
# --------------------------------------------------------------------------- #
def test_plain_regeneration_never_advances_the_stamp(site_data):
    """The named defect. If a regeneration re-recorded the baseline, the panel
    would report 'nothing changed' forever -- the feature would be a no-op that
    always looks green."""
    _gen(site_data, mark_seen=True)
    stamp_before = json.loads((site_data / gdd.STAMP_NAME).read_text())

    # The world moves: a new decision, a new reserved ask, a daemon dies.
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1", "ask-2"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision"),
                   ("2026-07-23T15:00:00+00:00", "a fresh decision")],
        daemons=[("steady-daemon", DEAD)],
    ))

    # Regenerate repeatedly -- the delta must keep reporting the change and the
    # baseline must not budge.
    for _ in range(3):
        payload = _gen(site_data, now=NOW_DT + timedelta(hours=1))
        stamp_after = json.loads((site_data / gdd.STAMP_NAME).read_text())
        assert stamp_after == stamp_before, "a plain regeneration re-based the stamp"
        assert payload["changed"] is True
        assert payload["counts"]["new_decisions"] == 1
        assert payload["counts"]["reserved_added"] == 1
        assert payload["counts"]["daemons_newly_stale"] == 1


def test_mark_seen_is_the_only_thing_that_advances_the_stamp(site_data):
    _gen(site_data, mark_seen=True)
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1", "ask-2"],
        decisions=[("2026-07-23T15:00:00+00:00", "a fresh decision")],
        daemons=[("steady-daemon", FRESH)],
    ))
    assert _gen(site_data)["changed"] is True
    later = NOW_DT + timedelta(hours=2)
    payload = _gen(site_data, mark_seen=True, now=later)
    assert payload["changed"] is False
    assert payload["last_look_at"] == later.isoformat()


@pytest.mark.parametrize("break_it,expected", [
    (lambda p: p.unlink(), "missing"),
    (lambda p: p.write_text("", encoding="utf-8"), "empty"),
    (lambda p: p.write_text("   \n", encoding="utf-8"), "empty"),
    (lambda p: p.write_text("{not json", encoding="utf-8"), "unreadable"),
    (lambda p: p.write_text("[]", encoding="utf-8"), "malformed"),
    (lambda p: p.write_text(json.dumps({"stamp_version": 1, "recorded_at": NOW,
                                        "state": {}}), encoding="utf-8"), "malformed"),
    (lambda p: p.write_text(json.dumps({"stamp_version": 1, "recorded_at": NOW,
                                        "state": {"latest_decision_ts": None}}),
                            encoding="utf-8"), "malformed"),
    (lambda p: p.write_text(json.dumps({"stamp_version": 99, "recorded_at": NOW,
                                        "state": {}}), encoding="utf-8"),
     "version_mismatch"),
])
def test_lost_stamp_refuses_to_fabricate_a_delta(site_data, break_it, expected):
    """A destroyed / blank / corrupt / half-written / wrong-version stamp must
    FIRE the guard. Note the sixth case especially: `state: {}` is the killer
    fail-open shape -- an empty baseline compares as 'every reserved item is
    new, every daemon just appeared'. Presence of the required keys is checked,
    not truthiness."""
    _gen(site_data, mark_seen=True)
    break_it(site_data / gdd.STAMP_NAME)

    payload = _gen(site_data)
    assert payload["stamp_status"] == expected
    assert payload["stamp_problem"], "a failed check must say why"
    # Neither "everything is new" nor "nothing changed" -- UNKNOWN.
    assert payload["changed"] is None, "a lost stamp must not resolve to True or False"
    assert payload["counts"] is None, "a lost stamp must not produce counts"
    assert payload["changes"] == []
    assert payload["last_look_at"] is None


def test_lost_stamp_is_not_silently_re_bootstrapped(site_data):
    """Auto-writing a fresh stamp when one is missing would convert the failure
    into a permanent 'nothing changed' -- the fail-open by another route."""
    _gen(site_data, mark_seen=True)
    (site_data / gdd.STAMP_NAME).unlink()
    _gen(site_data)
    assert not (site_data / gdd.STAMP_NAME).exists(), \
        "a plain run re-created the stamp; only --mark-seen may write it"


# --------------------------------------------------------------------------- #
# R15 (b) the delta FOLLOWS a real change, field by field.
# --------------------------------------------------------------------------- #
def test_new_decision_moves_the_count(site_data):
    _gen(site_data, mark_seen=True)
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision"),
                   ("2026-07-23T15:00:00+00:00", "a fresh decision")],
        daemons=[("steady-daemon", FRESH)],
    ))
    payload = _gen(site_data)
    assert payload["counts"]["new_decisions"] == 1
    assert payload["detail"]["new_decisions"][0]["what"] == "a fresh decision"
    assert any("a fresh decision" in line for line in payload["changes"])


def test_reserved_queue_add_and_clear_both_register(site_data):
    _gen(site_data, mark_seen=True)
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-2"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision")],
        daemons=[("steady-daemon", FRESH)],
    ))
    payload = _gen(site_data)
    assert payload["detail"]["reserved_added"] == ["ask-2"]
    assert payload["detail"]["reserved_cleared"] == ["ask-1"]
    assert payload["counts"]["reserved_changed"] == 2


def test_daemon_death_and_recovery_register(site_data):
    _gen(site_data, mark_seen=True)
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision")],
        daemons=[("steady-daemon", DEAD)],
    ))
    dead = _gen(site_data)
    assert dead["detail"]["daemons_newly_stale"] == ["steady-daemon"]

    _gen(site_data, mark_seen=True)
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision")],
        daemons=[("steady-daemon", FRESH)],
    ))
    back = _gen(site_data)
    assert back["detail"]["daemons_recovered"] == ["steady-daemon"]


def test_headline_figures_move(site_data):
    _gen(site_data, mark_seen=True)
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision")],
        daemons=[("steady-daemon", FRESH)],
        answered=9, open_atoms=51,
    ))
    payload = _gen(site_data)
    assert payload["counts"]["headline_moves"] == 2
    assert {"field": "answered", "from": 5, "to": 9} in payload["detail"]["fidelity_moves"]
    assert {"field": "total_open_atoms", "from": 55, "to": 51} in \
        payload["detail"]["headline_moves"]


def test_quiet_interval_is_a_definite_false_not_an_unknown(site_data):
    payload = _gen(site_data, mark_seen=True)
    assert payload["changed"] is False, "a quiet interval is KNOWN-quiet, not unknown"
    assert payload["counts"]["new_decisions"] == 0
    assert payload["changes"] == []


def test_delta_records_the_source_stamps_it_used(site_data):
    payload = _gen(site_data, mark_seen=True)
    assert payload["source_stamps"]["reserved_generated_at"] == NOW
    assert payload["source_stamps"]["health_last_updated"] == NOW
    assert payload["source_stamps"]["decisions_generated_at"] == NOW


def test_cli_round_trip(site_data):
    assert gdd.main(["--site-data", str(site_data), "--mark-seen", "--by", "cli-test"]) == 0
    stamp = json.loads((site_data / gdd.STAMP_NAME).read_text())
    assert stamp["recorded_by"] == "cli-test"
    assert gdd.main(["--site-data", str(site_data)]) == 0
    assert json.loads((site_data / gdd.STAMP_NAME).read_text()) == stamp


# --------------------------------------------------------------------------- #
# R11: the RENDERED pixel. Everything below runs the page's own inline script.
# --------------------------------------------------------------------------- #
node_only = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict) -> dict:
    data = dict(data)
    data.setdefault("now", NOW)
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data), capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _page_data(site_data: Path, last_look) -> dict:
    """Feed the page exactly what it fetches: the same site/data files, plus the
    generator's own delta payload."""
    read = lambda n: json.loads((site_data / n).read_text())  # noqa: E731
    return {
        "twin": read("director_twin.json"),
        "plan": read("provisional_plan.json"),
        "sys": {"staging_queue": []},
        "reserved": read("director_reserved.json"),
        "health": read("agent_status.json"),
        "decisions": read("decisions.json"),
        "lastLook": last_look,
        "now": NOW,
    }


@node_only
def test_quiet_interval_renders_a_plain_empty_state(site_data):
    payload = _gen(site_data, mark_seen=True)
    out = _render(_page_data(site_data, payload))
    body = out["lastlook-body"]["innerHTML"]
    assert 'data-state="quiet"' in body, body
    assert "nothing has changed since" in body.lower(), body
    assert "fail" not in body.lower(), "a quiet interval must not render as a failure"
    kpis = out["lastlook-kpis"]["innerHTML"]
    assert kpis.count('<div class="kpi-v">0</div>') == 4, kpis


@node_only
def test_a_real_change_moves_the_rendered_pixel(site_data):
    """R15 (b), end to end: mutate ONE underlying value (a reserved ask appears)
    and the rendered delta follows -- generator and page in one chain."""
    _gen(site_data, mark_seen=True)
    before = _render(_page_data(site_data, _gen(site_data)))["lastlook-body"]["innerHTML"]
    assert "nothing has changed" in before.lower()

    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1", "ask-2"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision")],
        daemons=[("steady-daemon", FRESH)],
    ))
    payload = _gen(site_data)
    out = _render(_page_data(site_data, payload))
    body = out["lastlook-body"]["innerHTML"]
    kpis = out["lastlook-kpis"]["innerHTML"]
    assert body != before, "the rendered delta did not move on a real change"
    assert "nothing has changed" not in body.lower()
    assert "ask-2" in body, body
    assert "1 added, 0 cleared" in kpis, kpis
    assert "warn" in kpis


@node_only
def test_a_dead_daemon_alarms_the_rendered_delta(site_data):
    _gen(site_data, mark_seen=True)
    _write_feeds(site_data, _feeds(
        reserved_ids=["ask-1"],
        decisions=[("2026-07-10T00:00:00+00:00", "an old decision")],
        daemons=[("steady-daemon", DEAD)],
    ))
    out = _render(_page_data(site_data, _gen(site_data)))
    assert "went stale" in out["lastlook-body"]["innerHTML"]
    assert "alarm" in out["lastlook-kpis"]["innerHTML"]


@node_only
@pytest.mark.parametrize("break_it", [
    lambda p: p.unlink(),
    lambda p: p.write_text("", encoding="utf-8"),
    lambda p: p.write_text("{not json", encoding="utf-8"),
    lambda p: p.write_text(json.dumps({"stamp_version": 1, "recorded_at": NOW,
                                       "state": {}}), encoding="utf-8"),
])
def test_lost_stamp_renders_red_and_distinguishable_from_a_quiet_interval(site_data, break_it):
    """The atom's binding acceptance note: a delta view that silently resets to
    'everything is new' (or to a soothing 'nothing changed') when the stamp is
    lost is the FAIL-OPEN form of the feature. The rendered pixel must be a
    visible failure carrying NO fabricated numbers."""
    _gen(site_data, mark_seen=True)
    break_it(site_data / gdd.STAMP_NAME)
    out = _render(_page_data(site_data, _gen(site_data)))
    body = out["lastlook-body"]["innerHTML"]
    kpis = out["lastlook-kpis"]["innerHTML"]
    assert 'class="fail"' in body, body
    assert "stamp LOST" in body, body
    # The three outcomes are machine-distinguishable, so this assertion cannot be
    # fooled by copy that merely MENTIONS the quiet phrasing.
    assert 'data-state="stamp-lost"' in body, body
    assert 'data-state="quiet"' not in body, "a lost stamp must not claim a quiet interval"
    assert 'data-state="changed"' not in body, "a lost stamp must not claim changes"
    assert "kpi-v" not in kpis, "a lost baseline must render NO numbers, not zeros"
    assert "--mark-seen" in body, "the failure must say how to restore the baseline"


@node_only
def test_absent_delta_feed_renders_unknown_not_quiet(site_data):
    """FAIL-SILENT: an unavailable check is a FAILED check. If
    director_delta.json 404s the page must say the delta is unknown."""
    out = _render(_page_data(site_data, None))
    body = out["lastlook-body"]["innerHTML"]
    assert 'class="fail"' in body
    assert "unknown" in body.lower()
    assert 'data-state="feed-absent"' in body
    assert 'data-state="quiet"' not in body
    assert out["lastlook-kpis"]["innerHTML"] == ""


@node_only
def test_frozen_delta_feed_is_caught_against_the_live_feeds(site_data):
    """G4: the generator cannot certify its own freshness. If the delta was
    computed against older feeds than the page fetched (the shape an unwired
    generator produces), the page says so."""
    payload = _gen(site_data, mark_seen=True)
    data = _page_data(site_data, payload)
    assert "out of date" not in _render(data)["lastlook-body"]["innerHTML"]

    data["reserved"] = dict(data["reserved"])
    data["reserved"]["generated_at"] = "2026-07-24T09:00:00+00:00"
    body = _render(data)["lastlook-body"]["innerHTML"]
    assert "out of date with the feeds on this page" in body, body
    assert "reserved_generated_at" in body


@node_only
def test_lastlook_states_its_falsifiable_claim_and_is_a_diagnostic(site_data):
    out = _render(_page_data(site_data, _gen(site_data, mark_seen=True)))
    hyp = out["lastlook-hyp"]["innerHTML"]
    assert "diagnostic" in hyp.lower() and "never a target" in hyp.lower()
    assert "survives a publish" in hyp.lower()
    assert "can fail honestly" in hyp.lower()
    passport = out["lastlook-passport"]["innerHTML"]
    assert "director_last_look.json" in passport
    assert "--mark-seen" in passport, "the passport must state how the stamp advances"
    assert "recorded" in passport.lower()


@node_only
def test_lastlook_renders_against_the_committed_live_feeds():
    """R11 on the REAL published data the page consumes (not a fixture), so the
    committed stamp/delta pair is proven to render. Live-fetch of poesys.net is
    pending a publish from main."""
    data = {
        "twin": json.loads((DATA / "director_twin.json").read_text()),
        "plan": json.loads((DATA / "provisional_plan.json").read_text()),
        "sys": json.loads((DATA / "system_status.json").read_text()),
        "reserved": json.loads((DATA / "director_reserved.json").read_text()),
        "health": json.loads((DATA / "agent_status.json").read_text()),
        "decisions": json.loads((DATA / "decisions.json").read_text()),
        "lastLook": json.loads((DATA / "director_delta.json").read_text()),
        "now": NOW,
    }
    out = _render(data)
    body = out["lastlook-body"]["innerHTML"]
    ll = data["lastLook"]
    assert ll["stamp_status"] == "ok", "the committed stamp must be readable"
    if ll["changed"]:
        assert "since your last recorded look" in body.lower(), body
    else:
        assert "nothing has changed" in body.lower(), body


# --------------------------------------------------------------------------- #
# Placement + no new affordance.
# --------------------------------------------------------------------------- #
def test_the_delta_leads_the_page():
    """s7.10's actual ask: the director should not have to scroll a full-state
    page to find what moved."""
    src = INDEX.read_text()
    assert src.index('id="lastlook-hyp"') < src.index('id="reserved-hyp"'), \
        "the delta must render ABOVE the full-state panels"
    assert "What changed since you last looked" in src


def test_the_two_delta_halves_are_distinguishable_on_the_page():
    src = INDEX.read_text()
    assert "This browser&#39;s last visit" in src or "This browser's last visit" in src
    assert src.index('id="lastlook-hyp"') < src.index('id="delta-hyp"')


def test_delta_adds_no_write_or_auth_affordance():
    src = INDEX.read_text()
    assert 'class="veil"' not in src and 'id="veil"' not in src
    assert "<form" not in src.lower()
    # The stamp is a build-time/operator artefact, never a server-side record of
    # the director's browsing.
    assert "no server read-receipt" in src or "not a server-side read receipt" in src


def test_committed_stamp_is_honest_about_its_provenance():
    stamp = json.loads((DATA / gdd.STAMP_NAME).read_text())
    assert stamp["stamp_version"] == gdd.STAMP_VERSION
    assert "--mark-seen" in stamp["note"]
    assert stamp["recorded_by"], "the stamp must say who recorded the look"
    status, _, problem = gdd.load_stamp(DATA / gdd.STAMP_NAME)
    assert status == "ok", problem
