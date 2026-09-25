"""The pass ceiling, wired to the CORE draw at a ceiling per loop_stage.

FILENAME NOTE. This file says `harden_rung` and covers the whole core draw. The name is kept
deliberately: `docs/design/simplifications/archive/EP6_wall_protocol_typing.033.yaml` credits
this path as the falsifier that certified a level move, and
`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` resolves that
credit by path. Renaming the file for tidiness would break a real provenance chain in an
archived record to fix a cosmetic inaccuracy that this paragraph fixes for free.

WHY THIS FILE EXISTS. `tools/discovery_pass_ceiling.py` shipped 2026-08-19 against the
director's ruling -- *"make it impossible for the system to run indefinitely on work that
cannot change its own state"* -- and reached exactly ONE consumer,
`supervisor._idle_discover_frame_draw`, which feeds only on `idle` atoms. Of the atoms the
corrected ceiling calls saturated, ONE was idle. The rest were `build` or `harden`, where
nothing consulted it. `WORKER_FINDING_ONE_OLD_LEVEL_MOVE_BOUGHT_AN_ATOM_FORTY_THREE_UNBOUNDED_
PASSES_2026-08-19.md` recorded that as the larger, undischarged half.

THE SUBJECT IS THE ASYMMETRY, not the exclusion -- and on 2026-08-24 the asymmetry stopped
being an exemption and became a ratio. The 2026-08-19 repair gated `harden` and left `build`
untouched, on the argument that drawing a saturated build atom IS the promote path the ruling
demands. Measured on the live store 2026-08-24: `EP6_wall_protocol_typing` had taken **55
build passes since its level last moved**, `SITE2_two_sided_wall_exhibit` 18. A promote path
attempted fifty-five times without a promotion is the unbounded run wearing the one stage
label the gate trusted. So `build` is gated too, at DOUBLE the ceiling (10 against 5), because
the underlying claim -- a build pass can move a level, a harden pass cannot -- is still true
and is what the ratio now carries.

WHERE THE NULL CONTROL LIVES NOW. It moved with the policy. The gate no longer knows about
stages at all; it excludes whatever `core_draw_exclusions()` returns, and the stage ceilings
are that function's business. So the pin that stops the two ceilings collapsing into one is
`test_the_build_ceiling_is_DOUBLE_the_harden_ceiling_on_the_live_reading`, against the ceiling
module, not against the draw.
"""
import pytest

from background import supervisor

_HARDEN_ID = "HX_saturated_harden_atom"
_BUILD_ID = "BX_saturated_build_atom"


def _atom(atom_id: str, stage: str, scope: str) -> dict:
    """A minimal below-target candidate on a NON-world lane.

    `H_harness` is deliberate: the coupled-triad L3 gate in the real draw keys on a
    `W1_`/`W2_` lane prefix, so a world lane here would block these atoms for an unrelated
    reason and the test would pass without the gate under test ever running.
    """
    return {
        "id": atom_id,
        "lane": "H_harness",
        "dial_inherited": 3,
        "level_current": 2,
        "level_target": 3,
        "loop_stage": stage,
        "file_scope": [scope],
    }


def _exclusions_over(ceiling_module, rows: list[dict]) -> set:
    """Run `core_draw_exclusions` against a pinned survey.

    The stage ceilings are what these tests measure, so the survey -- the store read, the
    ledger read, the date parsing -- is pinned rather than exercised. Its own behaviour has
    its own tests in `tests/tools/test_discovery_pass_ceiling.py`.
    """
    import unittest.mock as _mock

    with _mock.patch.object(ceiling_module, "survey", lambda *a, **k: rows):
        return ceiling_module.core_draw_exclusions()


@pytest.fixture
def saturate(monkeypatch):
    """Pin the ceiling's verdict, so these tests measure the GATE and not the ceiling.

    The helper imports `saturated_ids` inside the function body, so patching the module
    attribute is what the call site actually resolves.
    """
    def _pin(ids):
        monkeypatch.setattr(
            "tools.discovery_pass_ceiling.core_draw_exclusions", lambda *a, **k: set(ids)
        )
    return _pin


# --------------------------------------------------------------------------------------
# The predicate
# --------------------------------------------------------------------------------------

def test_a_saturated_HARDEN_atom_is_excluded_from_the_core_draw(saturate):
    """The positive case: the shape that drew H27 for its forty-third pass since its move."""
    saturate({_HARDEN_ID})
    candidates = [
        _atom(_HARDEN_ID, "harden", "a.py"),
        _atom("HY_fresh_harden_atom", "harden", "b.py"),
    ]
    kept = supervisor._exclude_saturated_from_core_draw(candidates)
    assert [a["id"] for a in kept] == ["HY_fresh_harden_atom"]


def test_a_BUILD_atom_over_its_own_ceiling_is_excluded_too(saturate):
    """The 2026-08-24 extension: the EP6 shape, 55 build passes without a level move.

    Paired with `test_a_saturated_BUILD_atom_UNDER_the_build_ceiling_survives` below, which
    is the half that stops this becoming "drop every build atom the ceiling names".
    """
    saturate({_BUILD_ID, _HARDEN_ID})
    candidates = [
        _atom(_BUILD_ID, "build", "a.py"),
        _atom(_HARDEN_ID, "harden", "b.py"),
        _atom("BY_fresh_build_atom", "build", "c.py"),
    ]
    kept = supervisor._exclude_saturated_from_core_draw(candidates)
    assert [a["id"] for a in kept] == ["BY_fresh_build_atom"]


def test_an_UNSATURATED_harden_atom_survives(saturate):
    """The gate is keyed on the ceiling's verdict, not on `loop_stage == "harden"` alone."""
    saturate(set())
    candidates = [_atom(_HARDEN_ID, "harden", "a.py")]
    assert supervisor._exclude_saturated_from_core_draw(candidates) == candidates


# --------------------------------------------------------------------------------------
# R15: the two ways a guard on a draw lane fails
# --------------------------------------------------------------------------------------

def test_MUTATION_FAIL_OPEN_a_broken_ceiling_does_not_narrow_the_core_draw(monkeypatch):
    """FAIL-OPEN, and deliberately the OPPOSITE direction to `_idle_discover_frame_draw`.

    That tier returns None on an uncomputable ceiling, because its risk is the unbounded
    run. This one is a NARROWING of the primary state-moving lane, so its risk is a broken
    ceiling silently starving the core draw -- an R15 FAIL-OPEN in the abstract, and the
    Rule-0-correct direction here. Asserted rather than left implicit, because the two
    consumers of the same function now fail opposite ways on purpose and a later reader
    would otherwise "fix" one to match the other.
    """
    def boom(*a, **k):
        raise RuntimeError("ledger unreadable")

    monkeypatch.setattr("tools.discovery_pass_ceiling.core_draw_exclusions", boom)
    candidates = [_atom(_HARDEN_ID, "harden", "a.py")]
    assert supervisor._exclude_saturated_from_core_draw(candidates) == candidates


def test_MUTATION_RULE_0_the_gate_never_zeroes_the_feasible_set(saturate):
    """An empty feasible set is a DEFECT IN THE DIALS, not a reason to hold (Rule 0).

    A hard exclusion was chosen over a soft preference on the lesson commit d7d36b46a
    records -- two soft guards composing into a no-op -- so the emptiness backstop has to be
    carried explicitly instead of by the prefer-then-fall-back shape.
    """
    saturate({_HARDEN_ID, "HY_also_saturated"})
    candidates = [
        _atom(_HARDEN_ID, "harden", "a.py"),
        _atom("HY_also_saturated", "harden", "b.py"),
    ]
    assert supervisor._exclude_saturated_from_core_draw(candidates) == candidates


def test_an_empty_candidate_list_is_returned_untouched(saturate):
    """The ceiling is not consulted at all when there is nothing to narrow."""
    saturate({_HARDEN_ID})
    assert supervisor._exclude_saturated_from_core_draw([]) == []


# --------------------------------------------------------------------------------------
# The wiring -- the half the finding said was missing
# --------------------------------------------------------------------------------------

def test_the_gate_is_WIRED_into_the_production_core_draw(tmp_path, monkeypatch, saturate):
    """THE POINT OF THE WHOLE REPAIR: a ceiling with no caller is what shipped last time.

    Driven through `_maturity_map_draw_concurrent` -- the function `_self_refill_draw`
    actually calls -- rather than through the helper, so this reds if the call site is
    deleted while the helper keeps passing its own unit tests.
    """
    import yaml

    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".stall.json")
    saturate({_HARDEN_ID})

    atoms = [
        _atom(_HARDEN_ID, "harden", "tests/_fixture_never_exists_a.py"),
        _atom("HY_fresh_harden_atom", "harden", "tests/_fixture_never_exists_b.py"),
    ]
    supervisor.MATURITY_MAP_PATH.write_text(yaml.safe_dump(atoms), encoding="utf-8")

    drawn = {a["id"] for a in supervisor._maturity_map_draw_concurrent()}
    assert _HARDEN_ID not in drawn
    assert "HY_fresh_harden_atom" in drawn


def test_MUTATION_without_the_gate_the_same_draw_hands_out_the_saturated_atom(
    tmp_path, monkeypatch, saturate
):
    """The null control for the wiring test above: same map, same ceiling, gate removed.

    If this fails, the previous test is passing for some other reason (a dependency filter,
    the unmerged-work guard, an empty candidate set) and proves nothing about the gate.
    """
    import yaml

    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".stall.json")
    monkeypatch.setattr(supervisor, "_exclude_saturated_from_core_draw", lambda c: c)
    saturate({_HARDEN_ID})

    atoms = [
        _atom(_HARDEN_ID, "harden", "tests/_fixture_never_exists_a.py"),
        _atom("HY_fresh_harden_atom", "harden", "tests/_fixture_never_exists_b.py"),
    ]
    supervisor.MATURITY_MAP_PATH.write_text(yaml.safe_dump(atoms), encoding="utf-8")

    drawn = {a["id"] for a in supervisor._maturity_map_draw_concurrent()}
    assert _HARDEN_ID in drawn


def test_a_saturated_BUILD_atom_UNDER_the_build_ceiling_survives():
    """THE NULL CONTROL ON THE RATIO, and the assertion that carries the design.

    An atom at 7 passes since its level moved is over the HARDEN ceiling of 5 and under the
    BUILD ceiling of 10. The ONLY thing that decides its fate is `loop_stage`. If this ever
    goes red by exclusion, the two ceilings have collapsed into one, the 2026-08-19 asymmetry
    is gone, and the core BUILD rung has been narrowed by a third for no measured reason --
    which is the failure this whole file exists to make loud rather than silent.

    Drives `core_draw_exclusions` against a pinned survey rather than the gate, because since
    2026-08-24 the stage policy lives in the ceiling module and the gate is deliberately
    stage-blind. Testing the gate here would prove nothing about the ratio.
    """
    from tools import discovery_pass_ceiling as ceiling

    rows = [
        {"atom": "B7", "stage": "build", "passes_since_move": 7},
        {"atom": "H7", "stage": "harden", "passes_since_move": 7},
    ]
    excluded = _exclusions_over(ceiling, rows)
    assert excluded == {"H7"}


def test_the_build_ceiling_is_DOUBLE_the_harden_ceiling_on_the_live_reading():
    """The ratio itself, pinned as a number rather than left implicit in two constants.

    Not a target (R12) -- nothing optimises toward it. It is here because the ratio IS the
    argument: a build pass can move a level and a harden pass cannot, so build gets more rope
    and a bounded amount of it. A future edit that sets them equal, or that restores the
    unbounded build lane by raising BUILD_CEILING out of reach, has to come through this line.
    """
    from tools import discovery_pass_ceiling as ceiling

    assert ceiling.BUILD_CEILING == 2 * ceiling.DEFAULT_CEILING


def test_MUTATION_an_idle_atom_is_NEVER_in_the_core_draw_exclusions():
    """FAIL-CLOSED IN THE WRONG DIRECTION is the risk here, and this is its pin.

    The core draw does not hand out `idle` atoms at all, so an idle id appearing in this set
    would be a stage-key bug quietly widening a gate into a lane it was never measured
    against. The discovery tier gates idle separately, at `DEFAULT_CEILING`, through
    `saturated_ids`.
    """
    from tools import discovery_pass_ceiling as ceiling

    rows = [
        {"atom": "I99", "stage": "idle", "passes_since_move": 99},
        {"atom": "H99", "stage": "harden", "passes_since_move": 99},
    ]
    assert _exclusions_over(ceiling, rows) == {"H99"}


def test_the_live_map_and_live_ceiling_agree_that_no_atom_over_its_ceiling_is_drawable():
    """A PROPERTY on the real population, not a count -- so it cannot red on its own success.

    Stated as "none survives", which is vacuously true the day every atom over its ceiling
    has been certified, retargeted or closed. A count assertion here ("at least N are
    excluded") would go red exactly when the ruling started working, get relaxed, and take
    the real reds with it -- the failure mode filed as `a control pinned as a count reds on
    its own success case`. Reads the live map and the live ledger deliberately: the fixtures
    above prove the predicate, this proves it is pointed at the real thing.
    """
    import yaml

    from tools.discovery_pass_ceiling import core_draw_exclusions

    atoms = yaml.safe_load(supervisor.MATURITY_MAP_PATH.read_text(encoding="utf-8"))
    over = core_draw_exclusions()
    below_target_core = [
        a for a in atoms
        if isinstance(a, dict)
        and a.get("loop_stage") in ("harden", "build")
        and isinstance(a.get("level_current"), int)
        and isinstance(a.get("level_target"), int)
        and a["level_current"] < a["level_target"]
    ]
    kept = supervisor._exclude_saturated_from_core_draw(below_target_core)
    assert not [a for a in kept if a.get("id") in over]


# --------------------------------------------------------------------------------------
# The IDLE tier has TWO doors, and the ceiling was on the one nothing calls
#
# This file's own docstring records that `tools/discovery_pass_ceiling.py` "reached exactly
# ONE consumer, `supervisor._idle_discover_frame_draw`". True, and it was the wrong one.
# `_self_refill_draw()` -- the function that composes the LANE 3 doorbell a worker tick is
# woken with -- calls `_idle_discover_frame_draw_concurrent`, the singular function's twin,
# and until 2026-09-06 that twin applied no ceiling at all. Both halves of the 2026-08-19
# repair therefore missed the live idle path: the core-draw extension above gated `build`
# and `harden`, and the idle gate sat on a draw with no production caller.
#
# MEASURED, 2026-09-06: a LANE 3 doorbell drew `EP17_varied_population_draw` for a SEVENTH
# DISCOVER/FRAME pass. `python3 -m tools.discovery_pass_ceiling` had it at 6 passes / 0 moves
# since, under "investigating again is no longer an available answer".
# --------------------------------------------------------------------------------------

_IDLE_SATURATED = "EPX_saturated_idle_atom"
_IDLE_FRESH = "EPY_fresh_idle_atom"


def _idle_atom(atom_id: str) -> dict:
    """A minimal idle below-target candidate with no `evidence` and no `blocked_on`.

    Deliberately the shape the two SIBLING guards read as drawable, so this test measures
    the ceiling and nothing else: `_is_externally_blocked` reads `blocked_on` (absent here,
    and set on 0 of the live map's 336 rows), and `_is_frame_saturated` reads the atom's
    `evidence` list for a `*_FRAME.md` (absent here, and absent on EP17 too -- six passes
    wrote a FRAME doc and never added it to the list). If either sibling started refusing
    this atom, the FIRES test below would pass for the wrong reason -- which is what the
    QUIET test exists to catch.
    """
    return {
        "id": atom_id,
        "lane": "H_harness",
        "dial_inherited": 3,
        "level_current": 0,
        "level_target": 3,
        "loop_stage": "idle",
        "file_scope": [],
    }


@pytest.fixture
def idle_candidates(monkeypatch):
    """Feed the concurrent idle draw a two-atom map. Returns a `pin(ids)` for the ceiling.

    `saturated_ids` is imported inside the function body, so the module attribute is what
    the call site resolves -- the same reason the `saturate` fixture above patches there.
    """
    rows = [_idle_atom(_IDLE_SATURATED), _idle_atom(_IDLE_FRESH)]
    monkeypatch.setattr(supervisor.map_store, "load_atoms", lambda *a, **k: list(rows))

    def _pin(ids):
        monkeypatch.setattr(
            "tools.discovery_pass_ceiling.saturated_ids", lambda *a, **k: set(ids)
        )
    return _pin


def test_a_saturated_IDLE_atom_is_excluded_from_the_CONCURRENT_discovery_draw(idle_candidates):
    """FIRES -- the EP17 shape, the seventh pass on an atom the ceiling had already closed.

    Width 3 against two candidates, so a pass here cannot be the width cap doing the work:
    without the ceiling BOTH atoms come back.
    """
    idle_candidates({_IDLE_SATURATED})
    picked = supervisor._idle_discover_frame_draw_concurrent(width=3)
    assert [a["id"] for a in picked] == [_IDLE_FRESH]


def test_an_UNSATURATED_idle_atom_still_reaches_the_concurrent_draw(idle_candidates):
    """QUIET / the poison round -- proves the FIRES test above is not passing vacuously.

    A gate that refused everything would satisfy the FIRES assertion just as well, and the
    fail-closed direction of this control makes that the LIKELY way for it to be wrong. With
    the ceiling naming nobody, both atoms must come back -- so the exclusion is reachable in
    both directions and the draw is not simply empty.
    """
    idle_candidates(set())
    picked = supervisor._idle_discover_frame_draw_concurrent(width=3)
    assert sorted(a["id"] for a in picked) == sorted([_IDLE_FRESH, _IDLE_SATURATED])


def test_an_UNREADABLE_ceiling_closes_the_concurrent_draw_rather_than_reopening_it(
        idle_candidates, monkeypatch):
    """FAIL-CLOSED, and it is the direction the ruling names.

    The sibling guard `_is_frame_saturated` fails toward OFFERING because its risk is
    starving real work; this one fails toward an EMPTY tier because its risk is the
    indefinite run the 2026-08-19 ruling exists to end. An unreadable ceiling reported as
    "nothing is saturated" is exactly the reading that would restore the unbounded lane.
    """
    idle_candidates(set())

    def _boom(*a, **k):
        raise RuntimeError("ledger unreadable")

    monkeypatch.setattr("tools.discovery_pass_ceiling.saturated_ids", _boom)
    assert supervisor._idle_discover_frame_draw_concurrent(width=3) == []


def test_no_atom_over_the_idle_ceiling_survives_the_live_concurrent_draw():
    """A PROPERTY on the real population, the idle-tier twin of the core-draw control above.

    Stated as "none survives" for the same reason: it is vacuously true the day every
    saturated idle atom has been promoted or closed, so it cannot red on its own success.
    Reads the live map through `map_store` rather than parsing MATURITY_MAP_PATH directly --
    the map is a two-file store, and a direct read of one half is how an atom census comes
    back short.
    """
    from tools.discovery_pass_ceiling import saturated_ids

    over = saturated_ids()
    picked = supervisor._idle_discover_frame_draw_concurrent(width=99)
    assert not [a for a in picked if a.get("id") in over]
