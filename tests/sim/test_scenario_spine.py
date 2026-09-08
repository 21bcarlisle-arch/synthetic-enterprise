"""SPINE_1 exit tests — the scenario world-state substrate.

Built with the spine on the director's "start the work" warning (2026-07-29). These are
the R15 failable controls named in the FRAME §R15 (W1/W2/W3) plus the Blindfold-clean
accessor and registry-behaviour tests. Each control has a KILLER MUTATION named inline: a
control that cannot fail is worse than none (R15).

FRAME: docs/design/SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md
"""

import datetime as dt
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sim.scenario import spine as S
from tools.python_code_text import imported_modules

REPO = Path(__file__).resolve().parents[2]


# --- W2: byte-identical baseline dormancy (FRAME §A.5) -----------------------


def test_history_replay_selects_no_overrides():
    """W2: the default world is DORMANT — no exogenous overrides on any field.

    This is the byte-identical guarantee at the spine level: with history_replay every
    field of paths_as_of is NO_OVERRIDE, so callers fall through to the baseline record
    and every existing run reproduces unchanged.

    KILLER MUTATION: give history_replay.yaml a non-empty `paths:` (any override) ->
    selects_no_overrides flips False -> this FAILS. FAIL-OPEN guard: an override valued
    exactly 0.0 is still an override (NO_OVERRIDE is a distinct sentinel, not falsy-zero).
    """
    base = S.default_world()
    assert base.is_baseline
    assert base.selects_no_overrides
    got = base.paths_as_of("2022-01-01")
    assert set(got) == set(S.PATH_FIELDS)
    assert all(v is S.NO_OVERRIDE for v in got.values())


def test_no_override_is_distinct_from_zero():
    """NO_OVERRIDE must never be confused with a real 0.0 override (fail-open guard)."""
    assert S.NO_OVERRIDE is not None
    assert S.NO_OVERRIDE != 0.0
    assert not S.NO_OVERRIDE  # falsy for `if override:` ergonomics
    assert repr(S.NO_OVERRIDE) == "NO_OVERRIDE"
    assert S.NO_OVERRIDE is S._NoOverride()  # singleton


# --- W3: the R13 curriculum/ratification wall --------------------------------


@pytest.mark.parametrize("world_id", ["neso_central", "crisis_2021_22", "supply_glut"])
def test_proposed_worlds_load_but_are_not_rotation_eligible(world_id):
    """W3: proposed worlds LOAD (mechanism sees them) but can NEVER enter rotation unratified.

    KILLER MUTATION: flip a proposal artefact to ratified:true + in_rotation:true WITHOUT a
    ratification block -> load_world raises (fail-closed guard below). With a ratification
    block it would become eligible — which is exactly the director's call, not the agent's.
    """
    w = S.load_world(world_id)
    assert w.provenance == "proposal"
    assert w.ratified is False
    assert w.is_rotation_eligible is False
    assert w.true_probability is None  # curriculum weight is director-owned, unset until ratified
    with pytest.raises(S.ScenarioNotRatified):
        S.select_for_rotation(world_id)


def test_rotation_set_is_empty_until_director_ratifies():
    """W3: no non-baseline world is in rotation today — the wall holds until a real ratification."""
    assert S.rotation_set() == []
    # All four artefacts are nonetheless discoverable by the mechanism.
    assert set(S.available_worlds()) >= {
        "history_replay", "neso_central", "crisis_2021_22", "supply_glut"
    }


def test_ratified_true_without_record_is_rejected_fail_closed(tmp_path):
    """W3 killer: a difficulty world claiming ratified:true with NO ratification record is REJECTED.

    The agent controls both sides of the wall, so 'ratified' cannot be self-asserted — it
    requires a director record. This is the fail-CLOSED direction: a malformed/self-granted
    ratification must raise, never load as silently rotation-eligible.
    """
    art = tmp_path / "sneaky_world.yaml"
    art.write_text(yaml.safe_dump({
        "world_id": "sneaky_world",
        "version": "0.0.1",
        "provenance": "proposal",
        "ratified": True,       # self-asserted...
        "in_rotation": True,
        # ...but NO `ratification:` block.
        "paths": {"gas_trend": {"2022-01-01": 300.0}},
    }))
    with pytest.raises(S.ScenarioArtefactError):
        S.load_world("sneaky_world", curriculum_dir=tmp_path)


def test_ratified_world_with_record_becomes_eligible(tmp_path):
    """W3 both-ways: a properly director-ratified world (with a record) DOES enter rotation.

    Proves the guard is not a tautology that blocks everything — the release actually fires
    when the director's record is present (R15: controls must be able to pass on real input too).
    """
    art = tmp_path / "ratified_world.yaml"
    art.write_text(yaml.safe_dump({
        "world_id": "ratified_world",
        "version": "1.0.0",
        "provenance": "ratified",
        "ratified": True,
        "in_rotation": True,
        "true_probability": 0.15,
        "sampling_weight": 0.4,
        "ratification": {"by": "director", "date": "2026-07-29", "record": "test-fixture"},
        "paths": {"gas_trend": {"2022-01-01": 226.0}},
    }))
    w = S.load_world("ratified_world", curriculum_dir=tmp_path)
    assert w.is_rotation_eligible is True
    assert S.select_for_rotation("ratified_world", curriculum_dir=tmp_path).world_id == "ratified_world"
    assert S.rotation_set(curriculum_dir=tmp_path) == ["ratified_world"]


def test_spine_is_frozen_no_pnl_writeback():
    """W3 (C-S2): the object is frozen — there is no path to write a P&L outcome back into a world."""
    w = S.load_world("neso_central")
    with pytest.raises(Exception):  # FrozenInstanceError (a dataclasses.FrozenInstanceError)
        w.true_probability = 0.9  # type: ignore[misc]


# --- Blindfold-clean accessor (FRAME §A.4) -----------------------------------


def test_paths_as_of_never_returns_future_value():
    """paths_as_of(t) never returns a value dated after t (Blindfold-clean by construction)."""
    w = S.load_world("neso_central")
    # neso_central gas_trend anchors: 2024->84, 2030->71, 2050->66.
    assert w.paths_as_of("2025-06-01")["gas_trend"] == 84.0   # sees 2024, NOT 2030
    assert w.paths_as_of("2031-01-01")["gas_trend"] == 71.0   # sees 2030, NOT 2050
    assert w.paths_as_of("2055-01-01")["gas_trend"] == 66.0   # sees 2050
    # Before the first anchor -> NO_OVERRIDE (no leakage of the earliest future value).
    assert w.paths_as_of("2019-01-01")["gas_trend"] is S.NO_OVERRIDE
    # A field this world does not override is NO_OVERRIDE at any time.
    assert w.paths_as_of("2030-01-01")["storage_capacity"] is S.NO_OVERRIDE


def test_paths_as_of_accepts_date_and_datetime():
    w = S.load_world("crisis_2021_22")
    assert w.paths_as_of(dt.date(2022, 6, 1))["gas_trend"] == 226.0
    assert w.paths_as_of(dt.datetime(2022, 6, 1, 12, 30))["gas_trend"] == 226.0


def test_unknown_world_raises():
    with pytest.raises(S.ScenarioArtefactError):
        S.load_world("no_such_world")


# --- W1: the epistemic wall (FRAME §A.3) -------------------------------------


_SPINE = "sim.scenario.spine"


def _spine_importers(*roots: Path) -> tuple[int, list[str]]:
    """(files scanned, files importing the spine) — from the AST, not from a line spelling.

    THE WALL IS KEYED TO THE IMPORT, NOT TO HOW SOMEBODY TYPED IT. The two spellings this used
    to match missed `from sim.scenario import (spine)` and the line-broken parenthesised form
    entirely, and fired on any docstring that named the module — so an accurate comment about
    the wall read as a breach of it, and a legal-looking line break walked straight through.

    UNREADABLE IS A BREACH, not a pass: a file we could not parse is one we did not check, and
    a wall that goes quiet on what it cannot read is the failure it exists to prevent.
    """
    scanned = 0
    offenders = []
    for root in roots:
        for py in root.rglob("*.py"):
            scanned += 1
            mods = imported_modules(py.read_text(encoding="utf-8", errors="ignore"))
            if mods is None or _SPINE in mods:
                offenders.append(str(py))
    return scanned, offenders


def test_wall_company_and_saas_never_import_the_spine():
    """W1: no company/** or saas/** code may import sim.scenario.spine.

    The company discovers the world through prices and its own book, never by reading
    scenario state (FRAME §A.3). This is an import-direction check — the same structurally
    detectable law F1b proved for company comms.

    KILLER MUTATION: add `from sim.scenario.spine import ScenarioSpine` to any company/saas
    module -> this FAILS, and so does every other spelling of that import (see
    `test_wall_check_can_actually_fail`). FAIL-SILENT guard: the test asserts it actually
    scanned a non-trivial number of files, so an empty/blind scan can never pass green.
    """
    scanned, offenders = _spine_importers(REPO / "company", REPO / "saas")
    # FAIL-SILENT guard: an unavailable/blind scan is a FAILED check, not skipped-green.
    assert scanned > 50, f"wall scan saw only {scanned} files — scan is blind, treat as FAILED"
    assert offenders == [], f"company/saas modules import the scenario spine (wall breach): {offenders}"


@pytest.mark.parametrize("spelling", [
    "from sim.scenario.spine import ScenarioSpine",
    "import sim.scenario.spine",
    "from sim.scenario import spine",
    "from sim.scenario import (spine)",
    "from sim.scenario import (\n    spine,\n)",
    "import sim.scenario.spine as sp",
])
def test_wall_check_can_actually_fail(tmp_path, spelling):
    """W1 mutation self-test: prove the wall flags a real breach (control can fail).

    THIS NOW EXERCISES THE PRODUCTION SCAN. It used to re-implement the loop inline, which
    proved only that the COPY could fail — a wall could have been narrowed to nothing and this
    would have stayed green. Each spelling is one a supplier could plausibly write; the last
    three were invisible to the line-matching this replaced.
    """
    fake_company = tmp_path / "company"
    fake_company.mkdir()
    (fake_company / "leaky.py").write_text(spelling + "\n")
    scanned, offenders = _spine_importers(fake_company)
    assert scanned == 1
    assert len(offenders) == 1, f"the wall is blind to {spelling!r}"


def test_prose_about_the_wall_is_not_a_breach_of_it(tmp_path):
    """THE OTHER DIRECTION, and the one that makes a wall unmaintainable. A company module that
    documents why it must not read scenario state has to name what it must not read. Keying on
    mention means every accurate comment is a breach, and a wall nobody can explain gets deleted.

    MUTATION: fall back to `"sim.scenario.spine" in text` and this fires.
    """
    root = tmp_path / "company"
    root.mkdir()
    (root / "honest.py").write_text(
        '"""Reads prices only. Must never import sim.scenario.spine (FRAME A.3)."""\n'
        "# from sim.scenario import spine  <- would be a wall breach\n"
        "VALUE = 1\n"
    )
    scanned, offenders = _spine_importers(root)
    assert scanned == 1
    assert offenders == [], "a docstring naming the spine was read as importing it"


# --- import hygiene ----------------------------------------------------------


def test_module_imports_clean_in_subprocess():
    """The spine imports without side effects (no run-time synthesis, no network)."""
    r = subprocess.run(
        [sys.executable, "-c", "import sim.scenario.spine; print('ok')"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "ok" in r.stdout
