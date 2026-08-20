"""The pass ceiling, wired to the HARDEN rung of the CORE draw.

WHY THIS FILE EXISTS. `tools/discovery_pass_ceiling.py` shipped 2026-08-19 against the
director's ruling -- *"make it impossible for the system to run indefinitely on work that
cannot change its own state"* -- and reached exactly ONE consumer,
`supervisor._idle_discover_frame_draw`, which feeds only on `idle` atoms. Of the atoms the
corrected ceiling calls saturated, ONE was idle. The rest were `build` or `harden`, where
nothing consulted it. `WORKER_FINDING_ONE_OLD_LEVEL_MOVE_BOUGHT_AN_ATOM_FORTY_THREE_UNBOUNDED_
PASSES_2026-08-19.md` recorded that as the larger, undischarged half and named the repair:
gate the HARDEN rung, not the build rung. This is that repair.

THE SUBJECT IS THE ASYMMETRY, not the exclusion. Any control that merely drops saturated
atoms is easy to write and wrong: dropping a saturated `build` atom refuses the promote path
the ruling asks for, and the core BUILD rung has nothing beneath it to catch the fall (Rule
0). So the null control below -- a saturated BUILD atom that must SURVIVE -- is doing at
least as much work as the positive case, and is the assertion that reds if someone later
"simplifies" the predicate to `id in saturated_ids()`.
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


@pytest.fixture
def saturate(monkeypatch):
    """Pin the ceiling's verdict, so these tests measure the GATE and not the ceiling.

    The helper imports `saturated_ids` inside the function body, so patching the module
    attribute is what the call site actually resolves.
    """
    def _pin(ids):
        monkeypatch.setattr(
            "tools.discovery_pass_ceiling.saturated_ids", lambda *a, **k: set(ids)
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
    kept = supervisor._exclude_saturated_harden(candidates)
    assert [a["id"] for a in kept] == ["HY_fresh_harden_atom"]


def test_a_saturated_BUILD_atom_is_deliberately_NOT_excluded(saturate):
    """NULL CONTROL ON THE SUBJECT SET, and the assertion that carries the design.

    A saturated `build` atom is saturated by exactly the same ceiling reading as the harden
    one above -- the ONLY thing separating them is `loop_stage`. If this ever goes green by
    exclusion, the gate has started refusing the promote path the ruling demands, and the
    core BUILD rung has nothing beneath it to fall back to. Without this pin, a predicate of
    `a.get("id") in over_ceiling` passes every other test in this file.
    """
    saturate({_BUILD_ID, _HARDEN_ID})
    candidates = [
        _atom(_BUILD_ID, "build", "a.py"),
        _atom(_HARDEN_ID, "harden", "b.py"),
    ]
    kept = supervisor._exclude_saturated_harden(candidates)
    assert [a["id"] for a in kept] == [_BUILD_ID]


def test_an_UNSATURATED_harden_atom_survives(saturate):
    """The gate is keyed on the ceiling's verdict, not on `loop_stage == "harden"` alone."""
    saturate(set())
    candidates = [_atom(_HARDEN_ID, "harden", "a.py")]
    assert supervisor._exclude_saturated_harden(candidates) == candidates


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

    monkeypatch.setattr("tools.discovery_pass_ceiling.saturated_ids", boom)
    candidates = [_atom(_HARDEN_ID, "harden", "a.py")]
    assert supervisor._exclude_saturated_harden(candidates) == candidates


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
    assert supervisor._exclude_saturated_harden(candidates) == candidates


def test_an_empty_candidate_list_is_returned_untouched(saturate):
    """The ceiling is not consulted at all when there is nothing to narrow."""
    saturate({_HARDEN_ID})
    assert supervisor._exclude_saturated_harden([]) == []


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
    monkeypatch.setattr(supervisor, "_exclude_saturated_harden", lambda c: c)
    saturate({_HARDEN_ID})

    atoms = [
        _atom(_HARDEN_ID, "harden", "tests/_fixture_never_exists_a.py"),
        _atom("HY_fresh_harden_atom", "harden", "tests/_fixture_never_exists_b.py"),
    ]
    supervisor.MATURITY_MAP_PATH.write_text(yaml.safe_dump(atoms), encoding="utf-8")

    drawn = {a["id"] for a in supervisor._maturity_map_draw_concurrent()}
    assert _HARDEN_ID in drawn


def test_the_live_map_and_live_ceiling_agree_that_no_saturated_harden_atom_is_drawable():
    """A PROPERTY on the real population, not a count -- so it cannot red on its own success.

    Stated as "none survives", which is vacuously true the day every saturated harden atom
    has been certified or closed. A count assertion here ("at least N are excluded") would
    go red exactly when the ruling started working, get relaxed, and take the real reds with
    it -- the failure mode filed as `a control pinned as a count reds on its own success
    case`. Reads the live map and the live ledger deliberately: the fixtures above prove the
    predicate, this proves it is pointed at the real thing.
    """
    import yaml

    from tools.discovery_pass_ceiling import saturated_ids

    atoms = yaml.safe_load(supervisor.MATURITY_MAP_PATH.read_text(encoding="utf-8"))
    over = saturated_ids()
    below_target_harden = [
        a for a in atoms
        if isinstance(a, dict)
        and a.get("loop_stage") == "harden"
        and isinstance(a.get("level_current"), int)
        and isinstance(a.get("level_target"), int)
        and a["level_current"] < a["level_target"]
    ]
    kept = supervisor._exclude_saturated_harden(below_target_harden)
    assert not [a for a in kept if a.get("id") in over]
