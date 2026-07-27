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
import json

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


def _no_rest_proof(tmp_path, monkeypatch):
    """Point the rest-with-proof marker at an absent path -- the default MINTING state (no fresh
    proof exists), so a populated-axes test mints rather than resting on a leaked real marker."""
    monkeypatch.setattr(sup, "PLANNER_REST_PROOF_PATH", tmp_path / ".no_rest_proof.json")


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
    _no_rest_proof(tmp_path, monkeypatch)


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
    _no_rest_proof(tmp_path, monkeypatch)
    _empty_staging(tmp_path, monkeypatch)
    msg = sup._planner_rung_draw()
    assert msg is not None
    assert "RUNG 7 PLANNER" in msg and "MINT" in msg and "propose-then-proceed" in msg


def test_planner_draw_silent_on_absent_axes(tmp_path, monkeypatch):
    _axes(tmp_path, monkeypatch, None)
    _no_disable_flag(tmp_path, monkeypatch)
    _no_rest_proof(tmp_path, monkeypatch)
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


# ───────────── REST-WITH-PROOF: the SECOND treadmill (mints in in_progress/, R15 both ways) ─────────────
#
# `_pending_planner_mints` only sees staging ROOT. Once a fully-blocked minted batch moves to
# in_progress/ it reads as consumed -> the planner RE-FIRES every tick into a proven-empty ratified-
# goal set. A planning turn that proves "no un-minted non-walled step exists" writes a dated verdict
# (`write_planner_rest_proof`); while that proof stays FRESH the planner rests-with-proof. The proof
# is keyed on LIVE state (UTC day + axes content hash + in_progress blocked-slug set), never a
# constant, so a new ruling / new day / newly-unblocked mint re-plans immediately.


def _write_blocked_in_progress_mint(staging_dir, slug, drawable=False):
    """Drop a PLANNER_MINTED_* doc into in_progress/ with a SUPERVISOR_DRAW marker."""
    ip = staging_dir / "in_progress"
    ip.mkdir(exist_ok=True)
    marker = "self-drawable" if drawable else "blocked"
    (ip / f"PLANNER_MINTED_{slug}.md").write_text(
        f"<!-- SUPERVISOR_DRAW: {marker} -->\n# minted {slug}\n"
    )


def _fresh_rest_proof(tmp_path, monkeypatch, axes_contents, blocked_slugs):
    """Wire a populated-axes + all-blocked-in_progress world with a matching FRESH rest proof.
    Returns (staging_dir, proof_path)."""
    _axes(tmp_path, monkeypatch, axes_contents)
    _no_disable_flag(tmp_path, monkeypatch)
    d = _empty_staging(tmp_path, monkeypatch)
    for s in blocked_slugs:
        _write_blocked_in_progress_mint(d, s)
    proof = tmp_path / ".planner_rest_with_proof.json"
    monkeypatch.setattr(sup, "PLANNER_REST_PROOF_PATH", proof)
    sup.write_planner_rest_proof(
        [f"PLANNER_MINTED_{s}.md" for s in blocked_slugs],
        "every ratified step minted-and-blocked or walled",
    )
    return d, proof


def test_rest_with_proof_rests_when_marker_fresh_and_state_unchanged(tmp_path, monkeypatch):
    """REST: axes populated, mints parked-blocked in in_progress/, a fresh matching proof exists ->
    the planner rests-with-proof (returns None) instead of re-firing into the proven-empty state."""
    _fresh_rest_proof(tmp_path, monkeypatch, _POPULATED_AXES, ["front_mission", "value_chain"])
    assert sup._planner_rest_proof_fresh() is True
    assert sup._planner_rung_draw() is None


def test_rest_with_proof_MINTS_when_no_marker(tmp_path, monkeypatch):
    """MINT (mutation A -- marker absent): the SAME parked-blocked world but NO proof marker ->
    the planner must MINT (a missing marker fails closed to minting, never a phantom rest)."""
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    _no_disable_flag(tmp_path, monkeypatch)
    _no_rest_proof(tmp_path, monkeypatch)
    d = _empty_staging(tmp_path, monkeypatch)
    _write_blocked_in_progress_mint(d, "front_mission")
    assert sup._planner_rest_proof_fresh() is False
    msg = sup._planner_rung_draw()
    assert msg is not None and "RUNG 7 PLANNER" in msg


def test_rest_with_proof_REPLANS_when_axes_change(tmp_path, monkeypatch):
    """MINT (mutation B -- a new director axis/ruling): a fresh proof is written, then DIRECTOR_AXES
    content changes. The recorded axes_sha no longer matches -> the proof is stale -> re-plan.
    This is the independence guarantee (R15): keyed on real axes content, not a constant."""
    _, _ = _fresh_rest_proof(tmp_path, monkeypatch, _POPULATED_AXES, ["front_mission"])
    assert sup._planner_rest_proof_fresh() is True  # baseline: fresh
    # Director adds a 4th ratified axis -> file content (and its sha) changes.
    (tmp_path / "DIRECTOR_AXES.md").write_text(
        _POPULATED_AXES + "\n### 4. Billing\n- Rotate billing + CRM in.\n"
    )
    assert sup._planner_rest_proof_fresh() is False
    assert sup._planner_rung_draw() is not None


def test_rest_with_proof_REPLANS_when_a_mint_is_unblocked(tmp_path, monkeypatch):
    """MINT (mutation C -- a blocked mint newly unblocked): a fresh proof covers a blocked batch,
    then one parked mint flips blocked -> self-drawable. Real RUNG-1 work now exists -> re-plan."""
    d, _ = _fresh_rest_proof(tmp_path, monkeypatch, _POPULATED_AXES, ["front_mission"])
    assert sup._planner_rest_proof_fresh() is True
    # The mint is unblocked: rewrite its draw marker to self-drawable.
    (d / "in_progress" / "PLANNER_MINTED_front_mission.md").write_text(
        "<!-- SUPERVISOR_DRAW: self-drawable -->\n# minted front_mission (now unblocked)\n"
    )
    assert sup._planner_rest_proof_fresh() is False
    assert sup._planner_rung_draw() is not None


def test_rest_with_proof_REPLANS_when_day_rolls(tmp_path, monkeypatch):
    """MINT (mutation D -- a new UTC day): a proof dated yesterday can never silence today's planner
    -- the daily re-check. A stale/constant marker that never invalidates must RED this test."""
    d, proof = _fresh_rest_proof(tmp_path, monkeypatch, _POPULATED_AXES, ["front_mission"])
    marker = json.loads(proof.read_text())
    marker["date"] = "2020-01-01"  # yesterday, forever ago
    proof.write_text(json.dumps(marker))
    assert sup._planner_rest_proof_fresh() is False
    assert sup._planner_rung_draw() is not None


def test_rest_with_proof_MINTS_on_malformed_marker(tmp_path, monkeypatch):
    """MINT (fail-closed): a malformed / non-dict marker must NOT validate a rest -> the planner
    mints. An unreadable proof is a FAILED proof (R15 fail-open guard)."""
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    _no_disable_flag(tmp_path, monkeypatch)
    d = _empty_staging(tmp_path, monkeypatch)
    _write_blocked_in_progress_mint(d, "front_mission")
    proof = tmp_path / ".planner_rest_with_proof.json"
    proof.write_text("not json {{{")
    monkeypatch.setattr(sup, "PLANNER_REST_PROOF_PATH", proof)
    assert sup._planner_rest_proof_fresh() is False
    proof.write_text("[1, 2, 3]")  # valid json, wrong type
    assert sup._planner_rest_proof_fresh() is False
    assert sup._planner_rung_draw() is not None


# ───────────── EIGHTH CLASS: the pending-batch deadlock (2026-07-27, DIRECTOR_RULING) ─────────────
#
# The 42h stall: six mints parked-blocked in in_progress/, a rest-proof whose date/axes/blocked-set
# all still matched -> the planner rested-with-proof for a whole working day, `authorized_set_
# enumeration` published planner=. as "whole authorized set empty", and the deadman's proven-rest
# fold trusted it. Two class fixes proven here: (H1) a blocked-batch rest-proof ages out after 2h so
# the planner RE-EXAMINES; (honesty) a `blocked_mints` level so the enumeration can never again
# publish "empty" beside open mints. R15 both ways.

from datetime import datetime, timezone, timedelta  # noqa: E402

_WEEKEND_SLUGS = [
    "dd_seasonal_cashflow_physics_2026-07-25", "generator_draw_wiring_2026-07-24",
    "merit_order_reconstruction_discover_2026-07-25", "ssp_negative_lift_cells_2026-07-24",
    "stratified_run_rotation_mechanism_2026-07-25", "value_chain_observation_window_cap_2026-07-24",
]


def test_rest_proof_ages_out_on_blocked_batch_past_max_age(tmp_path, monkeypatch):
    """H1 FIX, the exact weekend state: six mints parked-blocked, a proof whose date+axes+blocked-set
    ALL still match (the pre-fix code rested all 42h on it). Within the 2h cap it still rests (correct,
    no per-tick treadmill); past the cap it ages out -> the planner RE-EXAMINES instead of resting."""
    d, proof = _fresh_rest_proof(tmp_path, monkeypatch, _POPULATED_AXES, _WEEKEND_SLUGS)
    # Baseline (just written, <2h): still fresh -> rests-with-proof. The mechanism is NOT removed.
    assert sup._planner_rest_proof_fresh() is True
    assert sup._planner_rung_draw() is None
    # Age written_at to 42h ago (the weekend). date/axes/blocked-set field are ALL unchanged.
    marker = json.loads(proof.read_text())
    marker["written_at"] = (datetime.now(timezone.utc) - timedelta(hours=42)).isoformat()
    proof.write_text(json.dumps(marker))
    assert sup._planner_rest_proof_fresh() is False   # aged out -> not a valid rest
    assert sup._planner_rung_draw() is not None        # re-plans (mint-around / escalate)


def test_rest_proof_max_age_does_not_apply_without_blocked_mints(tmp_path, monkeypatch):
    """MUTATION guard (both-ways): a genuinely-exhausted rest (NO blocked mints) still rests the full
    UTC day -- the 2h cap must fire ONLY on an open blocked batch, never shorten a legitimate rest
    below rung 7. An old written_at with an empty blocked set stays fresh (date/axes bound it)."""
    _axes(tmp_path, monkeypatch, _POPULATED_AXES)
    _no_disable_flag(tmp_path, monkeypatch)
    d = _empty_staging(tmp_path, monkeypatch)  # NO in_progress mints at all
    proof = tmp_path / ".planner_rest_with_proof.json"
    monkeypatch.setattr(sup, "PLANNER_REST_PROOF_PATH", proof)
    sup.write_planner_rest_proof([], "no blocked mints; genuinely exhausted below rung 7")
    marker = json.loads(proof.read_text())
    marker["written_at"] = (datetime.now(timezone.utc) - timedelta(hours=42)).isoformat()
    proof.write_text(json.dumps(marker))
    assert sup._planner_rest_proof_fresh() is True  # empty blocked set -> age cap N/A -> still fresh


def test_blocked_mints_level_forbids_rest_and_is_named(tmp_path, monkeypatch):
    """ENUMERATION HONESTY FIX, the exact breach: mints parked-blocked while every other lane empty
    and the planner silent (axes absent) -> pre-fix the line read 'REST-LEGITIMATE (whole authorized
    set empty)'. Now blocked_mints=Y, verdict MUST-DRAW, each mint NAMED with its reason, and
    _is_drained_and_gated refuses rest (so the deadman's proven-rest fold can't suppress beside it)."""
    _gate_rungs_1_to_6(monkeypatch, tmp_path)   # empties lanes + isolates STAGING_DIR to tmp
    _axes(tmp_path, monkeypatch, None)           # planner silent -> the "whole set empty" illusion
    d = sup.STAGING_DIR
    ip = d / "in_progress"
    ip.mkdir(exist_ok=True)
    (ip / "PLANNER_MINTED_ssp_negative_lift_cells_2026-07-24.md").write_text(
        "<!-- SUPERVISOR_DRAW: blocked -->\nUNBLOCKS ON: the merit-order / gas-first reconstruction has landed\n")
    (ip / "PLANNER_MINTED_generator_draw_wiring_2026-07-24.md").write_text(
        "<!-- SUPERVISOR_DRAW: blocked -->\nblocked_on: director-reserved SE_DRAW population activation\n")
    e = sup.authorized_set_enumeration()
    assert e["blocked_mints"] is True and e["planner"] is False
    line = sup.authorized_set_enumeration_line()
    assert "blocked_mints=Y" in line and "MUST-DRAW" in line
    assert "REST-LEGITIMATE" not in line
    assert "OPEN MINTS (2)" in line and "merit-order" in line and "population activation" in line
    assert sup._is_drained_and_gated() is False


def test_blocked_mints_level_empty_when_no_mints(tmp_path, monkeypatch):
    """MUTATION both-ways: with NO in_progress mints, blocked_mints=. and the verdict is
    REST-LEGITIMATE (a constant-True level would RED this)."""
    _gate_rungs_1_to_6(monkeypatch, tmp_path)
    _axes(tmp_path, monkeypatch, None)
    monkeypatch.setattr(sup, "_rule0_harden_draw", lambda *a, **k: {"id": "AT_TARGET"})
    e = sup.authorized_set_enumeration()
    assert e["blocked_mints"] is False
    assert "blocked_mints=." in sup.authorized_set_enumeration_line()
    assert sup.open_mint_blockers() == []


def test_in_progress_slug_partition_fail_closed_on_unmarked(tmp_path, monkeypatch):
    """An UNMARKED in_progress mint fails closed to 'blocked' (invisible to the draw, per 04fe15d69)
    -- never fabricates phantom self-drawable work that would wrongly re-plan."""
    d = _empty_staging(tmp_path, monkeypatch)
    ip = d / "in_progress"
    ip.mkdir()
    (ip / "PLANNER_MINTED_unmarked.md").write_text("# no draw marker at all\n")
    part = sup._in_progress_minted_slugs()
    assert part["self_drawable"] == []
    assert part["blocked"] == ["PLANNER_MINTED_unmarked.md"]
