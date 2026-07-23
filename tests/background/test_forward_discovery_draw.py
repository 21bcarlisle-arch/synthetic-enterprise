"""R15 both-ways proof of the HARD RULE (director console 2026-07-22):

    THE TICK NEVER RESTS WHILE AUTHORIZED WORK EXISTS AT ANY PRIORITY
    -- core, idle-advance, or forward-discovery. Rest is legitimate ONLY
    with PROOF the authorized set is empty at EVERY level.

The forward-discovery register (F1-F5) is the always-drawable final lane. Before
2026-07-22 it was DESIGNED but never wired into the draw, so a core-gated tick
with a full register RESTED (the 95-min R13-wait stall). These tests prove the
rung is now load-bearing, BOTH ways:

  * test_must_not_rest_with_nonempty_register  -- core/idle gated + register
    NON-EMPTY  => the tick does NOT rest (draws forward-discovery). FAILS if it
    rests. This is the control that fires on the exact defect that stalled.
  * test_may_rest_with_genuinely_empty_authorized_set -- core/idle gated +
    register EMPTY => rest is legitimate. PASSES.
  * test_rung_is_load_bearing_mutation -- MUTATION (R15): simulate the pre-fix
    un-wired state (forward-discovery reader dead) and show the tick RESTS again
    with a full register -- proving the rung, not luck, prevents the stall.
"""
from __future__ import annotations

import background.supervisor as sup

_REGISTER_WITH_TRACKS = """# Forward-Discovery Register

## F1 — Simulating conversations *(highest)*
body
## F2 — Explaining what we do, simply
body
## F3 — Volunteer programme mechanics
body
"""

_EMPTY_REGISTER = "# Forward-Discovery Register\n\n(no drawable tracks)\n"

# A register whose ranking table marks EVERY track DISCOVER-complete: structurally non-empty
# (the ## Fn headers exist) but the authorized drawable set is empty -- the exact state that
# produced the 2026-07-22 "fail-open churn" (the tick re-drew finished tracks every ~4 min).
_REGISTER_ALL_COMPLETE = """# Forward-Discovery Register

| rank | track | class | criticality | status |
|---|---|---|---|---|
| **F1** | Simulating conversations | mission-required | **highest** — x | DISCOVER-complete 2026-07-22 (closed) |
| **F2** | Explaining what we do, simply | committed | high — y | DISCOVER-complete 2026-07-22 (closed) |

## F1 — Simulating conversations *(highest)*
body. Candidate graduation = the coupled-triad build.
## F2 — Explaining what we do, simply
body. graduation = harness bar before site page.
"""

# One track complete, one still OPEN: the drawable set is {F2}, so the tick must NOT rest.
_REGISTER_PARTIAL = """# Forward-Discovery Register

| rank | track | class | criticality | status |
|---|---|---|---|---|
| **F1** | Simulating conversations | mission-required | **highest** — x | DISCOVER-complete 2026-07-22 (closed) |
| **F2** | Explaining what we do, simply | committed | high — y | OPEN — one item still open |

## F1 — Simulating conversations *(highest)*
body. Candidate graduation = the coupled-triad build.
## F2 — Explaining what we do, simply
body still open.
"""


def _gate_core_and_idle_lanes(monkeypatch):
    """Put the core (BUILD/SITE) and idle-advance (DISCOVER/FRAME + backlog)
    lanes into the authority-gated/drained state: every one returns empty. This
    is exactly the state the seat was in for 95 minutes awaiting the R13 number."""
    monkeypatch.setattr(sup, "log", lambda *a, **k: None)
    monkeypatch.setattr(sup, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(sup, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(sup, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(sup, "_actionable_backlog_item", lambda *a, **k: None)
    # SEVENTH-CLASS open-campaign lane gated too (director ruling 2026-07-23): these tests prove the
    # FORWARD-DISCOVERY rung in isolation, so the open-campaign rung above it must be empty here, else
    # the real (open SITE_V5) register would leak in and forbid the rest these tests exercise.
    monkeypatch.setattr(sup, "_open_campaign_draw", lambda *a, **k: None)


def _point_register_at(monkeypatch, tmp_path, contents: str):
    reg = tmp_path / "FORWARD_DISCOVERY_REGISTER.md"
    reg.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(sup, "FORWARD_DISCOVERY_REGISTER_PATH", reg)
    return reg


# --------------------------------------------------------------------------- #
# Parse / independence (R15: keyed on ACTUAL register content, never a constant)
# --------------------------------------------------------------------------- #

def test_tracks_parse_highest_rank_first(monkeypatch, tmp_path):
    _point_register_at(monkeypatch, tmp_path, _REGISTER_WITH_TRACKS)
    tracks = sup._forward_discovery_tracks()
    assert [t[0] for t in tracks] == ["F1", "F2", "F3"]  # file order = rank order
    assert tracks[0][1].startswith("Simulating conversations")


def test_absent_register_is_honestly_empty(monkeypatch, tmp_path):
    # An ABSENT register IS an empty authorized set at this level (the PROOF rest needs).
    missing = tmp_path / "does_not_exist.md"
    monkeypatch.setattr(sup, "FORWARD_DISCOVERY_REGISTER_PATH", missing)
    assert sup._forward_discovery_tracks() == []
    assert sup._forward_discovery_draw() is None


def test_real_register_is_nonempty():
    # The shipped register carries F1-F5 -- so by construction the tick rests rarely.
    tracks = sup._forward_discovery_tracks()  # default = real docs/design/FORWARD_DISCOVERY_REGISTER.md
    ids = {t[0] for t in tracks}
    assert {"F1", "F2", "F3", "F4", "F5"} <= ids, f"real register lost its standing tracks: {ids}"


# --------------------------------------------------------------------------- #
# BOTH-WAYS R15 PROOF of the HARD RULE
# --------------------------------------------------------------------------- #

def test_must_not_rest_with_nonempty_register(monkeypatch, tmp_path):
    """Core + idle-advance gated, forward-discovery register NON-EMPTY.
    The tick MUST draw forward-discovery, NOT rest. FAILS if it rests."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_WITH_TRACKS)

    # The draw falls through to forward-discovery (not None, not the HARDEN treadmill).
    refill = sup._self_refill_draw()
    assert refill is not None
    assert "FORWARD-DISCOVERY self-refill" in refill
    assert "RULE 0" not in refill  # forward-discovery is preferred over the HARDEN treadmill

    # And the rest predicate REFUSES to rest -- this is the assertion that fails if the
    # tick rests (find_work rests iff `refill and _is_drained_and_gated()`).
    assert sup._is_drained_and_gated() is False, (
        "TICK RESTED while the forward-discovery register had drawable work -- "
        "the exact 95-min R13-wait stall class. HARD RULE breach (R10)."
    )


def test_may_rest_with_genuinely_empty_authorized_set(monkeypatch, tmp_path):
    """Core + idle-advance gated AND forward-discovery register EMPTY: the
    authorized set is genuinely empty at every level -> rest is LEGITIMATE."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _EMPTY_REGISTER)

    assert sup._forward_discovery_draw() is None  # nothing drawable at the forward level

    # With the register empty, the only remaining draw is the Rule-0 HARDEN treadmill on
    # at-target atoms (the real map has them) -> a legitimate quiet-rest state.
    assert sup._is_drained_and_gated() is True, (
        "rest was refused even though the authorized set is genuinely empty at every "
        "level -- the rule must PERMIT rest here, not livelock the HARDEN treadmill forever."
    )


def test_rung_is_load_bearing_mutation(monkeypatch, tmp_path):
    """R15 MUTATION: reintroduce the pre-fix defect -- the forward-discovery
    reader is dead (returns None as if never wired) -- while the register is
    FULL. The tick RESTS again. This proves the rung (not coincidence) is what
    prevents the stall: kill it, the 95-min stall returns."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_WITH_TRACKS)

    # Sanity: with the rung LIVE, the register non-empty means no rest (control passes).
    assert sup._is_drained_and_gated() is False

    # MUTATE: simulate the un-wired lane (the state that stalled for 95 min).
    monkeypatch.setattr(sup, "_forward_discovery_draw", lambda *a, **k: None)
    assert sup._is_drained_and_gated() is True, (
        "MUTATION not caught: with the forward-discovery rung dead, _is_drained_and_gated "
        "must fall back to a rest -- if it still returns False, some OTHER lane is masking "
        "the rung and the both-ways proof is not isolating the forward-discovery lane."
    )


# --------------------------------------------------------------------------- #
# R17 FAIL-OPEN FIX (director console 2026-07-22): a DISCOVER-complete track LEAVES
# the authorized drawable set; rest with that PROOF is legitimate. BOTH ways below.
# --------------------------------------------------------------------------- #

def test_complete_tracks_leave_the_drawable_set(monkeypatch, tmp_path):
    """Structural parse still sees both tracks; the DRAWABLE set is empty; the draw
    returns None -- the completed tracks are no longer re-drawn (the churn is gone)."""
    _point_register_at(monkeypatch, tmp_path, _REGISTER_ALL_COMPLETE)
    assert [t[0] for t in sup._forward_discovery_tracks()] == ["F1", "F2"]  # parse unchanged
    assert sup._forward_discovery_complete_ids() == {"F1", "F2"}
    assert sup._forward_discovery_drawable_tracks() == []
    assert sup._forward_discovery_draw() is None


def test_all_complete_register_permits_rest(monkeypatch, tmp_path):
    """R17 direction A: core+idle gated AND every forward track DISCOVER-complete ->
    the authorized set is empty at every level -> rest is LEGITIMATE. This is the exact
    'fail-open churn' state (finished register, tick grinding) now resolved to rest."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_ALL_COMPLETE)
    assert sup._is_drained_and_gated() is True, (
        "rest refused with EVERY forward track DISCOVER-complete -- the fail-open churn "
        "(re-drawing finished tracks every cycle) would return. R17 permits rest here."
    )


def test_partial_complete_still_forbids_rest(monkeypatch, tmp_path):
    """R17 direction B: one track complete, one still OPEN -> the open track is drawable
    -> the tick MUST draw it, NOT rest. Incomplete register still forbids rest."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_PARTIAL)
    assert [t[0] for t in sup._forward_discovery_drawable_tracks()] == ["F2"]
    refill = sup._self_refill_draw()
    assert refill is not None and "FORWARD-DISCOVERY self-refill" in refill and "F2" in refill
    assert sup._is_drained_and_gated() is False, (
        "TICK RESTED while an OPEN forward track (F2) remained drawable -- R17 breach."
    )


def test_completion_filter_is_load_bearing_mutation(monkeypatch, tmp_path):
    """R15 MUTATION for the NEW rung: neuter the completion filter (pretend nothing is ever
    complete) with an ALL-COMPLETE register -> the finished tracks re-enter the drawable set
    and the tick REFUSES to rest = the fail-open churn returns. Proves the filter, not luck,
    is what makes rest legitimate."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_ALL_COMPLETE)
    # Control: with the filter LIVE, an all-complete register rests.
    assert sup._is_drained_and_gated() is True

    # MUTATE: completion detection dead -> every track looks drawable again.
    monkeypatch.setattr(sup, "_forward_discovery_complete_ids", lambda *a, **k: set())
    assert sup._is_drained_and_gated() is False, (
        "MUTATION not caught: with the completion filter dead, a fully-finished register "
        "must look like live work and REFUSE rest -- if it still rests, the filter is not "
        "the thing gating rest and the churn could silently return."
    )


def test_malformed_status_table_fails_safe_toward_work(monkeypatch, tmp_path):
    """FAIL-SAFE (R15): a register with tracks but NO parseable status table marks NOTHING
    complete -> all tracks stay drawable -> the tick works, never wrongly rests."""
    _point_register_at(monkeypatch, tmp_path, _REGISTER_WITH_TRACKS)  # no status table at all
    assert sup._forward_discovery_complete_ids() == set()
    assert [t[0] for t in sup._forward_discovery_drawable_tracks()] == ["F1", "F2", "F3"]


# --------------------------------------------------------------------------- #
# Graduation proposal: exactly ONE batched [ACT] per complete-set (decision 3)
# --------------------------------------------------------------------------- #

def test_graduation_proposal_batches_complete_tracks(monkeypatch, tmp_path):
    _point_register_at(monkeypatch, tmp_path, _REGISTER_ALL_COMPLETE)
    result = sup.forward_discovery_graduation_proposal()
    assert result is not None
    msg, ids = result
    assert ids == ["F1", "F2"]
    assert "[ACT]" in msg and "will NOT self-open" in msg
    assert "F1" in msg and "F2" in msg
    assert "coupled-triad build" in msg  # grounded in the track's own candidate-graduation line


def test_no_graduation_proposal_when_nothing_complete(monkeypatch, tmp_path):
    _point_register_at(monkeypatch, tmp_path, _REGISTER_WITH_TRACKS)  # tracks, none complete
    assert sup.forward_discovery_graduation_proposal() is None


# A register where the director has RULED on every complete track (graduated/held/folded). They
# stay DISCOVER-complete (non-drawable) but must NOT be re-surfaced in the [ACT] -- the call is made.
_REGISTER_ALL_DISPOSITIONED = """# Forward-Discovery Register

| rank | track | class | criticality | status |
|---|---|---|---|---|
| **F1** | Simulating conversations | mission-required | **highest** — x | DISCOVER-complete; GRADUATED → FRAME (director 2026-07-22) |
| **F2** | Explaining what we do, simply | committed | high — y | DISCOVER-complete; FOLDED into site (director 2026-07-22) |
| **F3** | Volunteer programme mechanics | mission-required | high — z | DISCOVER-complete; HELD (director 2026-07-22) |

## F1 — Simulating conversations *(highest)*
body. Candidate graduation = the coupled-triad build.
## F2 — Explaining what we do, simply
body. graduation = harness bar before site page.
## F3 — Volunteer programme mechanics
body.
"""


def test_dispositioned_tracks_stay_non_drawable_but_drop_from_the_act(monkeypatch, tmp_path):
    """Director-ruled tracks (graduated/held/folded) keep DISCOVER-complete in their cell, so the
    tick still RESTS (they are non-drawable) -- but the graduation [ACT] no longer re-asks for a
    call already made. Both properties at once."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_ALL_DISPOSITIONED)
    # Still non-drawable -> rest holds (the fix's rest guarantee survives the ruling).
    assert sup._forward_discovery_drawable_tracks() == []
    assert sup._is_drained_and_gated() is True
    # But no [ACT] -- every complete track has been ruled on (awaiting set empty).
    assert sup._forward_discovery_dispositioned_ids() == {"F1", "F2", "F3"}
    assert sup.forward_discovery_graduation_proposal() is None


def test_act_surfaces_only_the_still_awaiting_track(monkeypatch, tmp_path):
    """Mixed register: F1 ruled (graduated), F2 still awaiting a call. The [ACT] names ONLY F2."""
    reg = _REGISTER_ALL_DISPOSITIONED.replace(
        "| DISCOVER-complete; FOLDED into site (director 2026-07-22) |",
        "| DISCOVER-complete 2026-07-22 (awaiting a ruling) |",
    )
    _point_register_at(monkeypatch, tmp_path, reg)
    result = sup.forward_discovery_graduation_proposal()
    assert result is not None
    msg, ids = result
    assert ids == ["F2"]                 # only the un-ruled track
    assert "F2" in msg and "1 track(s)" in msg


def test_graduation_emit_fires_once_per_complete_set(monkeypatch, tmp_path):
    """The batched [ACT] fires ONCE for a given complete-set and is suppressed as unchanged
    thereafter (transition-only via the notify contract). A CHANGED set re-fires."""
    _point_register_at(monkeypatch, tmp_path, _REGISTER_ALL_COMPLETE)
    calls = []

    def fake_notify(msg, **kw):
        calls.append((msg, kw))
        # Mimic the contract's transition store: suppress an unchanged (key, state).
        key, state = kw.get("transition_key"), kw.get("state")
        seen = fake_notify.__dict__.setdefault("_seen", {})
        if seen.get(key) == state:
            return f"suppressed:unchanged:{key}"
        seen[key] = state
        return "id-1"

    first = sup.maybe_emit_graduation_proposal(notify_fn=fake_notify)
    second = sup.maybe_emit_graduation_proposal(notify_fn=fake_notify)
    assert first is not None          # first emit sends
    assert second is None             # unchanged complete-set suppressed (no re-page churn)
    assert len(calls) == 2 and calls[0][1]["kind"] == "digest"
    assert calls[0][1]["transition_key"] == "forward_discovery_graduation"
    assert calls[0][1]["state"] == "F1,F2"


# --------------------------------------------------------------------------- #
# PROPOSE-HALF CLASS FIX (director ruling 2026-07-23, DIRECTOR_RULING_R17_BREACH_AND_CLASS_FIX):
# an R10-breach-of-R17. A BUILD-gated item's UNGATED build-PROPOSAL step is ALWAYS drawable. The
# overnight stall: F1 graduated to FRAME, its build proposal drawable all night, no lane enumerated
# it -> the tick rested over doable work. These prove the new rung is load-bearing BOTH ways.
# --------------------------------------------------------------------------- #

# F1 graduated to FRAME with a build-proposal step (the exact overnight shape); F2 FOLDED and F3 HELD
# carry NO build-proposal step. Every track is DISCOVER-complete, so the forward-discovery DRAWABLE set
# is empty -- the ONLY thing forbidding rest here is F1's open propose-half (clean isolation).
_REGISTER_F1_PROPOSE_HALF = """# Forward-Discovery Register

| rank | track | class | criticality | status |
|---|---|---|---|---|
| **F1** | Simulating conversations | mission-required | **highest** — x | DISCOVER-complete; GRADUATED → FRAME (director): coupled-triad design, build proposal via gate → docs/design/frame/F1.md |
| **F2** | Explaining what we do, simply | committed | high — y | DISCOVER-complete; FOLDED into site work (director) |
| **F3** | Volunteer programme mechanics | mission-required | high — z | DISCOVER-complete; HELD (director) |

## F1 — Simulating conversations *(highest)*
body.
## F2 — Explaining what we do, simply
body.
## F3 — Volunteer programme mechanics
body.
"""


def _point_proposals_at(monkeypatch, tmp_path, *written_ids: str):
    """Point the proposal-dir constant at a tmp dir, optionally pre-seeding it with written
    proposal artefacts (F1_x.md ...) so the propose-half for those tracks reads as DRAINED."""
    d = tmp_path / "proposals"
    d.mkdir(exist_ok=True)
    for tid in written_ids:
        (d / f"{tid}_build_proposal.md").write_text("proposal", encoding="utf-8")
    monkeypatch.setattr(sup, "FORWARD_PROPOSAL_DIR_PATH", d)
    return d


def test_propose_half_parses_only_the_frame_plus_proposal_track(monkeypatch, tmp_path):
    """Independence (R15): the propose-half is keyed on the ACTUAL cell text -- FRAME *and* a
    'build proposal' step. F2 (FOLDED) and F3 (HELD) carry no build-proposal step -> excluded."""
    _point_register_at(monkeypatch, tmp_path, _REGISTER_F1_PROPOSE_HALF)
    _point_proposals_at(monkeypatch, tmp_path)  # nothing written yet
    tracks = sup._forward_discovery_propose_half_tracks()
    assert [t[0] for t in tracks] == ["F1"], "only the FRAME+build-proposal track is a drawable propose-half"
    assert sup._propose_half_draw() is not None
    assert "PROPOSE-HALF self-refill" in sup._propose_half_draw()


def test_propose_half_forbids_rest_the_overnight_breach(monkeypatch, tmp_path):
    """THE FAILING TEST FIRST (ruling §2): core+idle+backlog gated, every forward track DISCOVER-
    complete, BUT F1's build proposal is unwritten -> the propose half is drawable -> the tick MUST
    draw it, NOT rest. This is the EXACT overnight state (a pending-proposal item, everything else
    gated). FAILS if the tick rests."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_F1_PROPOSE_HALF)
    _point_proposals_at(monkeypatch, tmp_path)  # F1 proposal NOT written

    # Forward-discovery DISCOVER lane is empty (all complete) -> the draw falls to the propose-half.
    assert sup._forward_discovery_draw() is None
    refill = sup._self_refill_draw()
    assert refill is not None and "PROPOSE-HALF self-refill" in refill and "F1" in refill
    assert "RULE 0" not in refill  # propose-half is preferred over the HARDEN treadmill

    assert sup._is_drained_and_gated() is False, (
        "TICK RESTED while a graduated-but-unproposed track (F1) had an open propose half -- "
        "the exact overnight R10-breach-of-R17 the ruling declares."
    )


def test_propose_half_drains_when_proposal_written_permits_rest(monkeypatch, tmp_path):
    """THE OTHER DIRECTION (ruling §2): once F1's build proposal IS written, the propose half drains;
    with everything else gated and all forward tracks complete, the authorized set is genuinely empty
    at every level -> rest is LEGITIMATE. Writing the proposal is the concrete, self-releasing transition
    (R11 no-orphan)."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_F1_PROPOSE_HALF)
    _point_proposals_at(monkeypatch, tmp_path, "F1")  # F1 proposal WRITTEN -> propose-half drained

    assert sup._forward_discovery_propose_half_tracks() == []
    assert sup._propose_half_draw() is None
    assert sup._is_drained_and_gated() is True, (
        "rest refused even though F1's proposal is written and the whole authorized set is empty -- "
        "the rule must PERMIT rest here, not livelock forever on a drained propose-half."
    )


def test_propose_half_rung_is_load_bearing_mutation(monkeypatch, tmp_path):
    """R15 MUTATION: with ONLY propose-half work present, neuter the propose-half draw (simulate the
    pre-fix un-wired state) -> the tick RESTS again. Proves the rung, not luck, prevents the stall:
    kill it, the overnight breach returns."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_F1_PROPOSE_HALF)
    _point_proposals_at(monkeypatch, tmp_path)  # F1 propose-half OPEN

    # Control: with the rung LIVE, the open propose-half means no rest.
    assert sup._is_drained_and_gated() is False

    # MUTATE: the propose-half reader is dead (the pre-fix state, no lane enumerates it).
    monkeypatch.setattr(sup, "_propose_half_draw", lambda *a, **k: None)
    assert sup._is_drained_and_gated() is True, (
        "MUTATION not caught: with the propose-half rung dead, a graduated-but-unproposed track must "
        "return the tick to a (wrong) rest -- if it still refuses rest, some OTHER lane is masking the "
        "rung and the both-ways proof is not isolating the propose-half lane."
    )


def test_propose_half_marker_absent_does_not_forbid_rest(monkeypatch, tmp_path):
    """FOLDED/HELD graduations (no build-proposal step) must NOT be read as propose-halves: they carry
    no ungated proposal work, so they correctly permit rest. Guards against the rung firing on every
    graduation (which would make rest impossible)."""
    _gate_core_and_idle_lanes(monkeypatch)
    # Strip F1's build-proposal marker -> now NO track has a build-proposal step.
    reg = _REGISTER_F1_PROPOSE_HALF.replace(
        "GRADUATED → FRAME (director): coupled-triad design, build proposal via gate → docs/design/frame/F1.md",
        "GRADUATED → FRAME (director): folded, no separate build proposal-step-here",
    ).replace("build proposal-step-here", "step")  # remove the literal marker phrase entirely
    _point_register_at(monkeypatch, tmp_path, reg)
    _point_proposals_at(monkeypatch, tmp_path)
    assert sup._forward_discovery_propose_half_tracks() == []
    assert sup._is_drained_and_gated() is True


def test_authorized_set_enumeration_names_every_level(monkeypatch, tmp_path):
    """The WHOLE-SET enumeration (ruling §2) names every level and forbids rest while ANY holds work.
    Here only the propose-half is open -> enumeration reports it and the verdict is MUST-DRAW."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_F1_PROPOSE_HALF)
    _point_proposals_at(monkeypatch, tmp_path)
    e = sup.authorized_set_enumeration()
    assert set(e) == {"build", "site", "discover_frame", "open_campaign", "backlog", "propose_half", "forward_discovery"}
    assert e["propose_half"] is True and e["build"] is False and e["forward_discovery"] is False
    line = sup.authorized_set_enumeration_line()
    assert "propose_half=Y" in line and "MUST-DRAW" in line and "propose_half" in line


def test_authorized_set_enumeration_all_empty_is_rest_legitimate(monkeypatch, tmp_path):
    """When every level is empty (F1 proposal written), the enumeration verdict is REST-LEGITIMATE."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _REGISTER_F1_PROPOSE_HALF)
    _point_proposals_at(monkeypatch, tmp_path, "F1")
    line = sup.authorized_set_enumeration_line()
    assert "REST-LEGITIMATE" in line and "=Y" not in line
