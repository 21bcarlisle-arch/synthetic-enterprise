#!/usr/bin/env python3
"""R15 proof for `tools/maturity_map_store.py` -- the loader the two-file map rests on.

WHAT COULD GO WRONG, and it is the reason the split was designed around this module rather
than around the readers. `site/moap_coherence.py` / `site/moap_stage.py` derive every
front-door node's Live/Building/Planned stage from atom LEVELS. Split the finished atoms into
a sibling file and let ONE reader silently receive only the live half, and that reader finds
no atom at target behind a finished node and renders it Planned -- a wrong answer that looks
entirely reasonable on the public site. That is R15's FAIL-OPEN killer exactly: the control
passes on the missing/empty input it exists to notice.

So the mutations below are not "does the happy path work". Each one BREAKS the closed half a
different way and asserts the loader REFUSES rather than returning a smaller map:
absent, empty, whitespace-only, unparseable, and a well-formed YAML document of the wrong
shape. A loader that returned live-only for any of them would make every one of these tests
pass by returning 74 atoms, which is why each asserts the raise and not the count.

The last test is the one that matters most and is the acceptance test the direction named:
the atom population the WHOLE map reports is exactly the union of the two files on disk, and
nothing was lost or duplicated by the split.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import maturity_map_store as map_store  # noqa: E402

ATOM_A = "- id: A_live\n  lane: X\n  level_current: 0\n  level_target: 3\n"
ATOM_B = "- id: B_done\n  lane: X\n  level_current: 3\n  level_target: 3\n"


@pytest.fixture()
def fixture_map(tmp_path: Path) -> Path:
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A, encoding="utf-8")
    (tmp_path / "maturity_map_closed.yaml").write_text(ATOM_B, encoding="utf-8")
    return live


# ── the union is the map ────────────────────────────────────────────────────────────────────
def test_load_atoms_returns_both_halves(fixture_map: Path):
    ids = [a["id"] for a in map_store.load_atoms(fixture_map)]
    assert ids == ["A_live", "B_done"]


def test_live_and_closed_are_each_only_their_own_half(fixture_map: Path):
    assert [a["id"] for a in map_store.load_live_atoms(fixture_map)] == ["A_live"]
    assert [a["id"] for a in map_store.load_closed_atoms(fixture_map)] == ["B_done"]


def test_map_text_concatenation_parses_as_one_list(fixture_map: Path):
    parsed = yaml.safe_load(map_store.map_text(fixture_map))
    assert [a["id"] for a in parsed] == ["A_live", "B_done"]


def test_map_text_joins_halves_even_when_the_live_half_has_no_trailing_newline(tmp_path: Path):
    """The realistic corruption of a naive concatenation: `- id: B` glued onto the end of the
    live half's last line, silently losing BOTH atoms around the join."""
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A.rstrip("\n"), encoding="utf-8")
    (tmp_path / "maturity_map_closed.yaml").write_text(ATOM_B, encoding="utf-8")
    assert [a["id"] for a in map_store.load_atoms(live)] == ["A_live", "B_done"]


# ── R15 mutations: every way the closed half can be broken must RAISE ───────────────────────
@pytest.mark.parametrize(
    "content",
    [
        pytest.param(None, id="absent"),
        pytest.param("", id="empty"),
        pytest.param("   \n\n\t\n", id="whitespace-only"),
        pytest.param("- id: A\n   bad: [unclosed\n", id="unparseable"),
        pytest.param("atoms:\n  - id: A\n", id="a-mapping-not-a-list"),
        pytest.param("# every line a comment\n", id="comments-only"),
    ],
)
def test_MUTATION_a_broken_closed_half_refuses_at_the_canonical_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content
):
    """Each mutation is a way the closed half stops holding atoms. NONE may resolve to
    live-only: a smaller map is the wrong answer that looks right."""
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A, encoding="utf-8")
    closed = tmp_path / "maturity_map_closed.yaml"
    if content is not None:
        closed.write_text(content, encoding="utf-8")

    # Make THIS fixture the canonical path, so the fail-closed branch is the one under test.
    monkeypatch.setattr(map_store, "LIVE_PATH", live)

    for call in (map_store.load_atoms, map_store.map_text, map_store.load_closed_atoms):
        with pytest.raises(map_store.MapStoreError):
            call(live)


def test_MUTATION_the_refusal_is_not_vacuous_the_same_calls_pass_when_intact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """The null control for the mutation test above: with the closed half intact and the same
    path marked canonical, every one of those three calls succeeds. Without this, a loader that
    raised unconditionally would pass every mutation above."""
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A, encoding="utf-8")
    (tmp_path / "maturity_map_closed.yaml").write_text(ATOM_B, encoding="utf-8")
    monkeypatch.setattr(map_store, "LIVE_PATH", live)
    assert len(map_store.load_atoms(live)) == 2
    assert "B_done" in map_store.map_text(live)
    assert len(map_store.load_closed_atoms(live)) == 1


def test_an_injected_fixture_path_with_no_closed_half_reads_live_only(tmp_path: Path):
    """THE ONE DELIBERATE SEAM, pinned so it cannot widen. Dozens of existing tests build a
    single-file fixture map; those have no closed half and never did, so absence there is not
    corruption. It keys on the resolved canonical path -- not on a flag a caller can pass."""
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A, encoding="utf-8")
    assert [a["id"] for a in map_store.load_atoms(live)] == ["A_live"]


def test_a_fixture_path_still_refuses_a_CORRUPT_closed_half(tmp_path: Path):
    """The seam tolerates ABSENCE at a fixture path, never CORRUPTION anywhere. A closed half
    that exists and is broken is a broken store wherever it lives."""
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A, encoding="utf-8")
    (tmp_path / "maturity_map_closed.yaml").write_text("- id: A\n   bad: [\n", encoding="utf-8")
    with pytest.raises(map_store.MapStoreError):
        map_store.load_atoms(live)


# ── the live tree ───────────────────────────────────────────────────────────────────────────
def test_the_real_store_reads_whole_and_both_halves_are_populated():
    whole = map_store.load_atoms()
    live = map_store.load_live_atoms()
    closed = map_store.load_closed_atoms()
    assert len(whole) == len(live) + len(closed)
    assert live and closed, "a half that emptied means the split collapsed back to one file"
    ids = [a["id"] for a in whole]
    assert len(ids) == len(set(ids)), "an atom is in BOTH halves -- the split duplicated it"


# ── the invariant's RELEASE: refile ─────────────────────────────────────────────────────────
#
# The invariant below asserts against the LIVE tree and reds a tree-wide test file, so it
# refuses every commit in every lane the moment an atom reaches its own target -- the success
# path of the machine. `refile` is what satisfies it mechanically. These tests are built around
# the two ways that fix could itself be the next incident: a re-filer that MOVED NOTHING would
# pass any one-directional happy-path test silently (hence the null control), and a re-filer
# that landed HALF of its two-file write would leave the map in the exact state that wedged the
# tree in the first place (hence the rollback test).

REFILE_LIVE = (
    "- id: A_live\n  lane: X\n  level_current: 0\n  level_target: 3\n"
    "\n\n"
    "# --- SECTION HEADER that belongs to the FILE, not to the atom above it\n"
    "- id: C_arrived\n  lane: X\n  level_current: 3\n  level_target: 3\n"
    '  real_world_twin: "bytes:  preserved -- odd   spacing"\n'
)
REFILE_CLOSED = (
    "# closed half header\n"
    "- id: B_done\n  lane: X\n  level_current: 3\n  level_target: 3\n"
    "\n"
    "- id: D_reopened\n  lane: X\n  level_current: 3\n  level_target: 5\n"
)


@pytest.fixture()
def refile_map(tmp_path: Path) -> Path:
    live = tmp_path / "maturity_map.yaml"
    live.write_text(REFILE_LIVE, encoding="utf-8")
    (tmp_path / "maturity_map_closed.yaml").write_text(REFILE_CLOSED, encoding="utf-8")
    return live


def _halves(live: Path) -> tuple[list[str], list[str]]:
    return (
        [a["id"] for a in map_store.load_live_atoms(live)],
        [a["id"] for a in map_store.load_closed_atoms(live)],
    )


def test_refile_moves_BOTH_directions_in_one_call(refile_map: Path):
    """Direction 1: an atom that reached its target leaves the drawn half. Direction 2, the one
    that is easy to forget: an atom whose target was RAISED comes back to the drawn half, or it
    sits where no draw ever looks and the work goes dark."""
    moved = map_store.refile(refile_map)
    assert moved == {"to_closed": ["C_arrived"], "to_live": ["D_reopened"]}
    live_ids, closed_ids = _halves(refile_map)
    assert sorted(live_ids) == ["A_live", "D_reopened"]
    assert sorted(closed_ids) == ["B_done", "C_arrived"]


def test_MUTATION_a_refiler_that_moved_NOTHING_fails_this_null_control(refile_map: Path):
    """THE NULL CONTROL. Every assertion above is about where atoms END UP, and a re-filer whose
    body was `return {"to_closed": [], "to_live": []}` would leave both halves exactly as
    written -- so this pins that the FILES changed and that the misfiled atoms are gone from the
    half they started in. Without it, a no-op re-filer passes the suite."""
    before_live = refile_map.read_text(encoding="utf-8")
    before_closed = map_store.closed_path_for(refile_map).read_text(encoding="utf-8")

    map_store.refile(refile_map)

    assert refile_map.read_text(encoding="utf-8") != before_live
    assert map_store.closed_path_for(refile_map).read_text(encoding="utf-8") != before_closed
    live_ids, closed_ids = _halves(refile_map)
    assert "C_arrived" not in live_ids, "at target and still drawn -- the re-filer did nothing"
    assert "D_reopened" not in closed_ids, "below target and still filed as finished"


def test_refile_satisfies_the_invariant_it_exists_to_satisfy(refile_map: Path):
    """The acceptance test, stated as the invariant itself rather than as a list of ids."""
    map_store.refile(refile_map)
    live = map_store.load_live_atoms(refile_map)
    closed = map_store.load_closed_atoms(refile_map)
    assert not [a["id"] for a in live if map_store.is_closed(a)]
    assert not [a["id"] for a in closed if not map_store.is_closed(a)]


def test_refile_conserves_the_population_and_the_moved_records_BYTES(refile_map: Path):
    """The split is a fact about storage, not about the population: moving a record may not
    lose, duplicate or reformat an atom. The odd interior spacing in `C_arrived` is there
    precisely so a YAML round-trip -- which would reflow every hand-authored block -- fails."""
    before = sorted(a["id"] for a in map_store.load_atoms(refile_map))
    map_store.refile(refile_map)
    after = [a["id"] for a in map_store.load_atoms(refile_map)]
    assert sorted(after) == before
    assert len(after) == len(set(after)), "an atom is in BOTH halves"
    closed_text = map_store.closed_path_for(refile_map).read_text(encoding="utf-8")
    assert '  real_world_twin: "bytes:  preserved -- odd   spacing"\n' in closed_text


def test_refile_leaves_a_section_comment_where_its_author_put_it(refile_map: Path):
    """A column-0 comment is a header for the FILE, never part of the atom beneath it, so an
    atom moving out from under one must not carry it along or delete it."""
    map_store.refile(refile_map)
    assert "# --- SECTION HEADER" in refile_map.read_text(encoding="utf-8")
    assert "# --- SECTION HEADER" not in (
        map_store.closed_path_for(refile_map).read_text(encoding="utf-8")
    )


def test_refile_is_a_genuine_NO_OP_when_every_atom_is_already_filed_right(tmp_path: Path):
    """The other half of the null control. A re-filer that rewrote both halves unconditionally
    would churn the map on every single fold, so a no-op must touch NEITHER file."""
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A, encoding="utf-8")
    closed = tmp_path / "maturity_map_closed.yaml"
    closed.write_text(ATOM_B, encoding="utf-8")
    stamps = (live.stat().st_mtime_ns, closed.stat().st_mtime_ns)

    assert map_store.refile(live) == {"to_closed": [], "to_live": []}

    assert (live.stat().st_mtime_ns, closed.stat().st_mtime_ns) == stamps
    assert live.read_text(encoding="utf-8") == ATOM_A
    assert closed.read_text(encoding="utf-8") == ATOM_B


def test_MUTATION_a_HALF_LANDED_refile_rolls_the_live_half_back(
    refile_map: Path, monkeypatch: pytest.MonkeyPatch
):
    """THE HAZARD THIS FIX REPEATS. `refile` is a two-file atomic write, which is the exact
    shape that wedged the tree behind the finding that asked for it: half of it landing reds
    every lane. So the closed half is made to fail mid-write and the live half must come back
    byte-identical -- both-old or both-new, never half-moved."""
    before_live = refile_map.read_text(encoding="utf-8")
    before_closed = map_store.closed_path_for(refile_map).read_text(encoding="utf-8")
    real_replace = map_store._replace

    def explode(path: Path, text: str) -> None:
        if path.name == "maturity_map_closed.yaml":
            raise OSError("disk full")
        real_replace(path, text)

    monkeypatch.setattr(map_store, "_replace", explode)
    with pytest.raises(map_store.MapStoreError):
        map_store.refile(refile_map)

    assert refile_map.read_text(encoding="utf-8") == before_live
    assert map_store.closed_path_for(refile_map).read_text(encoding="utf-8") == before_closed


def test_MUTATION_the_rollback_test_is_not_vacuous(refile_map: Path):
    """The null control for the rollback above: without the injected failure the SAME call
    changes both files. Otherwise a `refile` that raised unconditionally would pass it."""
    before_live = refile_map.read_text(encoding="utf-8")
    map_store.refile(refile_map)
    assert refile_map.read_text(encoding="utf-8") != before_live


def test_refile_REFUSES_to_empty_the_closed_half(tmp_path: Path):
    """Every reader here refuses an empty closed half as a truncation, so the re-filer may not
    manufacture one: it would satisfy this invariant by breaking the loader's."""
    live = tmp_path / "maturity_map.yaml"
    live.write_text(ATOM_A, encoding="utf-8")
    closed = tmp_path / "maturity_map_closed.yaml"
    closed.write_text("- id: B_done\n  level_current: 1\n  level_target: 4\n", encoding="utf-8")
    with pytest.raises(map_store.MapStoreError):
        map_store.refile(live)
    assert closed.read_text(encoding="utf-8").startswith("- id: B_done")


def test_the_split_predicate_agrees_with_where_every_atom_actually_SITS():
    """The invariant that keeps the two files honest: everything in the live half still has
    somewhere to go, everything in the closed half has arrived. This is what fails if someone
    raises a target without moving the record back."""
    misfiled_live = [a["id"] for a in map_store.load_live_atoms() if map_store.is_closed(a)]
    misfiled_closed = [
        a["id"] for a in map_store.load_closed_atoms() if not map_store.is_closed(a)
    ]
    assert not misfiled_live, (
        f"at target but still in the drawn half: {misfiled_live} -- move them to "
        f"{map_store.CLOSED_REL}"
    )
    assert not misfiled_closed, (
        f"below target but filed as finished: {misfiled_closed} -- move them back to "
        f"{map_store.MAP_REL} in the same commit that raised the target"
    )
