"""RUNG 7 -- THE PLANNER: R15 both-ways proof (director ruling WORK_IS_THE_DEFAULT
2026-07-23, commit 48495a455).

The hierarchy: rungs 1-6 (staged docs, open campaigns, atoms+propose-halves, defect
backlog, registered follow-ons, forward-discovery), then RUNG 7 -- when 1-6 are
genuinely empty, MINT the next batch from the director's ratified goals rather than
rest. 'Planning is work; resting instead of planning is the breach.'

R15 both ways:
  * MINT (reproduce the 13:06Z state -- the failing test the ruling demanded): rungs
    1-6 empty + DIRECTOR_AXES populated -> _self_refill_draw returns the PLANNER
    doorbell (not the HARDEN treadmill, not rest), _is_drained_and_gated is False, and
    the whole-set enumeration shows planner=Y.
  * REST (genuinely exhausted): rungs 1-6 empty + axes ABSENT -> planner returns None
    and the enumeration shows planner=. (rest legitimate below rung 7).
  * SHADOW RAIL: the disable flag reverts to prior behaviour with no code change.
"""
import background.supervisor as sup


_POPULATED_AXES = """# DIRECTOR AXES

## v1 axes (director's current priorities)

### 1. Website
- Usefulness as an operational window.

### 2. Segmentation
- Efficiency and sophistication.

### 3. Believability
- Does it feel like the real UK market.
"""

_EMPTY_AXES = "# DIRECTOR AXES\n\n(no ratified axes yet)\n"


def _axes(tmp_path, monkeypatch, contents: str | None):
    """Point DIRECTOR_AXES_PATH at a populated file, an empty file, or an absent path."""
    if contents is None:
        monkeypatch.setattr(sup, "DIRECTOR_AXES_PATH", tmp_path / "absent.md")
        return
    p = tmp_path / "DIRECTOR_AXES.md"
    p.write_text(contents)
    monkeypatch.setattr(sup, "DIRECTOR_AXES_PATH", p)


def _no_disable_flag(tmp_path, monkeypatch):
    """Point the shadow-rail flag at an absent path so the planner is NOT disabled."""
    monkeypatch.setattr(sup, "PLANNER_RUNG_DISABLED_FLAG", tmp_path / ".no_disable_flag")


def _empty_staging(tmp_path, monkeypatch):
    """Point STAGING_DIR at an EMPTY dir so no real PLANNER_MINTED_* batch is pending --
    the state in which the planner is allowed to mint. Without this isolation the real
    repo staging dir (which routinely holds a pending minted batch) would gate every
    'planner mints' assertion. Returns the dir so a test can drop a mint into it."""
    d = tmp_path / "staging"
    d.mkdir(exist_ok=True)
    monkeypatch.setattr(sup, "STAGING_DIR", d)
    return d


def _gate_rungs_1_to_6(monkeypatch, tmp_path):
    """Every rung 1-6 empty/gated -- the exact drained state that must reach the planner."""
    monkeypatch.setattr(sup, "log", lambda *a, **k: None)
    _empty_staging(tmp_path, monkeypatch)
    monkeypatch.setattr(sup, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(sup, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(sup, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(sup, "_actionable_backlog_item", lambda *a, **k: None)
    monkeypatch.setattr(sup, "_open_campaign_draw", lambda *a, **k: None)
    monkeypatch.setattr(sup, "_declared_defect_backlog_draw", lambda *a, **k: None)
    monkeypatch.setattr(sup, "_propose_half_draw", lambda *a, **k: None)
    monkeypatch.setattr(sup, "_forward_discovery_draw", lambda *a, **k: None)
    _no_disable_flag(tmp_path, monkeypatch)


# ─────────────────────────── detector unit (independence, R15) ──────────────────────────

def test_axes_present_true_on_ratified_axes(tmp_path, monkeypatch):
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    assert sup._director_axes_present() is True


def test_axes_present_false_on_empty_and_absent(tmp_path, monkeypatch):
    _axes(tmp_path, monkeypatch, _EMPTY_AXES)
    assert sup._director_axes_present() is False
    _axes(tmp_path, monkeypatch, None)  # absent file
    assert sup._director_axes_present() is False


def test_planner_draw_fires_on_populated_axes(tmp_path, monkeypatch):
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    _no_disable_flag(tmp_path, monkeypatch)
    _empty_staging(tmp_path, monkeypatch)
    msg = sup._planner_rung_draw()
    assert msg is not None
    assert "RUNG 7 PLANNER" in msg and "MINT" in msg and "propose-then-proceed" in msg


def test_planner_draw_silent_on_absent_axes(tmp_path, monkeypatch):
    _axes(tmp_path, monkeypatch, None)
    _no_disable_flag(tmp_path, monkeypatch)
    _empty_staging(tmp_path, monkeypatch)
    assert sup._planner_rung_draw() is None


# ─────────────────── RUNG 1 GATES RUNG 7: pending minted batch (R15, the 2026-07-24 defect) ──────────────────

def test_pending_mints_detector_true_when_batch_in_staging(tmp_path, monkeypatch):
    d = _empty_staging(tmp_path, monkeypatch)
    assert sup._pending_planner_mints() is False
    (d / "PLANNER_MINTED_some_slug_2026-07-24.md").write_text("proposal")
    assert sup._pending_planner_mints() is True


def test_pending_mints_ignores_consumed_subdirs(tmp_path, monkeypatch):
    """A minted doc moved to done/ or in_progress/ is CONSUMED -> no longer gates."""
    d = _empty_staging(tmp_path, monkeypatch)
    (d / "done").mkdir()
    (d / "done" / "PLANNER_MINTED_consumed_2026-07-24.md").write_text("done")
    assert sup._pending_planner_mints() is False


def test_planner_rests_while_minted_batch_pending(tmp_path, monkeypatch):
    """The 2026-07-24 treadmill: axes populated + lanes empty, but a minted batch already
    pends in staging -> the planner must NOT mint another batch on top (rung 1 gates rung 7)."""
    _gate_rungs_1_to_6(monkeypatch, tmp_path)
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    (sup.STAGING_DIR / "PLANNER_MINTED_front_mission_2026-07-24.md").write_text("pending")
    assert sup._planner_rung_draw() is None
    e = sup.authorized_set_enumeration()
    assert e["planner"] is False


# ─────────────────────────── MINT (the 13:06Z failing test) ──────────────────────────

def test_self_refill_mints_when_lanes_empty_and_axes_populated(tmp_path, monkeypatch):
    """Reproduce 13:06Z: rungs 1-6 empty, ratified goals present. The draw MUST mint,
    NOT rest and NOT fall to the RULE-0 HARDEN treadmill."""
    _gate_rungs_1_to_6(monkeypatch, tmp_path)
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    # Even though at-target HARDEN atoms exist (the treadmill would otherwise fire), the
    # planner is checked FIRST and wins.
    monkeypatch.setattr(sup, "_rule0_harden_draw", lambda *a, **k: {"id": "SOME_ATOM"})
    out = sup._self_refill_draw()
    assert out is not None
    assert "RUNG 7 PLANNER" in out
    assert "HARDEN" not in out or "re-verify" not in out  # not the treadmill message


def test_is_drained_refuses_rest_when_planner_can_mint(tmp_path, monkeypatch):
    _gate_rungs_1_to_6(monkeypatch, tmp_path)
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    assert sup._is_drained_and_gated() is False


def test_enumeration_shows_planner_drawable_when_axes_populated(tmp_path, monkeypatch):
    _gate_rungs_1_to_6(monkeypatch, tmp_path)
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    e = sup.authorized_set_enumeration()
    assert e["planner"] is True
    line = sup.authorized_set_enumeration_line()
    assert "planner=Y" in line and "MUST-DRAW" in line


# ─────────────────────────── REST (genuinely exhausted, below rung 7) ──────────────────────────

def test_rests_when_axes_absent(tmp_path, monkeypatch):
    """Genuinely exhausted: rungs 1-6 empty AND no ratified axes -> planner cannot mint.
    Rest is legitimate below rung 7 (here the HARDEN floor exists -> drained-and-gated)."""
    _gate_rungs_1_to_6(monkeypatch, tmp_path)
    _axes(tmp_path, monkeypatch, None)
    monkeypatch.setattr(sup, "_rule0_harden_draw", lambda *a, **k: {"id": "AT_TARGET"})
    assert sup._planner_rung_draw() is None
    assert sup._is_drained_and_gated() is True  # rests on the HARDEN floor


def test_enumeration_planner_empty_when_axes_absent(tmp_path, monkeypatch):
    _gate_rungs_1_to_6(monkeypatch, tmp_path)
    _axes(tmp_path, monkeypatch, None)
    e = sup.authorized_set_enumeration()
    assert e["planner"] is False


# ─────────────────────────── SHADOW RAIL (killable) ──────────────────────────

def test_shadow_rail_flag_disables_planner(tmp_path, monkeypatch):
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    flag = tmp_path / ".planner_rung_disabled"
    flag.write_text("disabled for rollback")
    monkeypatch.setattr(sup, "PLANNER_RUNG_DISABLED_FLAG", flag)
    assert sup._planner_rung_draw() is None
