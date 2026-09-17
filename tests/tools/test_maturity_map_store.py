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


# ── the size surface: a limit that speaks BEFORE it refuses ─────────────────────────────────
#
# SEAT_FINDING_THE_MAP_IS_185_BYTES_FROM_ITS_RATCHET_CEILING_2026-09-17. The defect these guard
# is not "the warning is wrong", it is the two ways a warning is worthless: SILENT when it
# should speak (the wedge arrives unannounced, which is the finding) and LOUD always (read as
# decoration and then not read at all). So every test below asserts a boundary in BOTH
# directions, and the population is synthetic text because the live map's headroom is a moving
# number that would pin these to today's answer.


def _text_of_bytes(n: int) -> str:
    """Map text of exactly `n` bytes -- ASCII, so bytes and characters agree."""
    return "#" + "x" * (n - 2) + "\n"


def test_map_bytes_measures_BOTH_halves_and_not_just_the_drawn_one(refile_map: Path):
    """The fail-open the split could have caused: a ceiling met by MOVING atoms to the sibling
    rather than by content leaving the spine. The whole must exceed either half."""
    live_only = len(refile_map.read_text(encoding="utf-8").encode("utf-8"))
    closed_only = len(
        (refile_map.parent / "maturity_map_closed.yaml").read_text(encoding="utf-8").encode("utf-8")
    )
    whole = map_store.map_bytes(live_path=refile_map)
    assert whole > live_only and whole > closed_only
    assert whole == live_only + closed_only, "a half went missing from the measurement"


def test_the_warning_is_SILENT_with_room_and_SPEAKS_inside_the_band():
    """The boundary, from both sides. A warning that only ever fires is not a signal, and one
    that never fires is the finding itself."""
    ceiling = map_store.MAP_SIZE_CEILING
    band = map_store.MAP_SIZE_WARN_HEADROOM
    roomy = map_store.size_warning(_text_of_bytes(ceiling - band - 1))
    assert roomy is None, f"spoke with more than the band's headroom: {roomy}"
    at_the_edge = map_store.size_warning(_text_of_bytes(ceiling - band + 1))
    assert at_the_edge and "headroom" in at_the_edge
    assert "fits" in at_the_edge, "it must say the write SUCCEEDED, or it reads as a refusal"


def test_the_reserve_band_says_the_commit_does_NOT_fit_and_the_band_above_says_it_does():
    """THE CONTRADICTION THIS BAND EXISTS TO PREVENT, from both sides of its edge.

    Once the per-atom bound is derived from this ceiling it refuses at `MAP_PER_ATOM_RESERVE` of
    headroom -- inside what this surface used to describe as "This commit fits". One limit with
    two surfaces telling the reader opposite things is the VAT shape, and it is invisible to any
    test that reads only one of them. So: one byte inside the reserve must not say it fits and
    must name the bound that will refuse; one byte outside it must still say it fits, or the
    reserve has quietly swallowed the warning band it was supposed to sit inside."""
    reserve = map_store.MAP_PER_ATOM_RESERVE
    inside = map_store.size_warning(_text_of_bytes(map_store.MAP_SIZE_CEILING - reserve))
    assert inside and "does not fit" in inside.lower(), \
        f"at the reserve edge the surface still promises the write succeeds: {inside}"
    assert "per-atom" in inside.lower() and "test_map_within_per_atom_budget" in inside, \
        f"it does not name the bound that refuses, so the reader cannot find it: {inside}"
    outside = map_store.size_warning(_text_of_bytes(map_store.MAP_SIZE_CEILING - reserve - 1))
    assert outside and "fits" in outside and "does not fit" not in outside.lower(), \
        f"one byte outside the reserve already reads as a refusal: {outside}"


def test_the_warning_NAMES_THE_NUMBER_and_points_DOWNWARD_never_at_the_ceiling():
    """The finding's own diagnosis: the pressure at a wedge points at raising the line, which is
    the one move the control exists to refuse. A warning read under that pressure must not offer
    it, and must carry the size so the reader can budget an edit instead of discovering the limit
    by hitting it.

    ASKED OF EVERY BAND, not of one headroom (2026-09-17). This probed 250 bytes of headroom and
    matched the literal phrase "never raise the ceiling" -- a control keyed to today's wording,
    which went red when a third band was added between the warning and the breach and said "never
    raise either line" because there are now two lines. The property is what matters: whatever
    `size_warning` says, in whichever band, it states the headroom, names a downward remedy, and
    never offers the upward one. Keyed that way it covers a band nobody has written yet, which is
    exactly what the old shape could not do."""
    bands = (250,                                        # inside the per-atom reserve
             map_store.MAP_PER_ATOM_RESERVE + 250,       # the ordinary warning band
             map_store.MAP_SIZE_WARN_HEADROOM - 1)       # the far edge of it
    for left in bands:
        msg = map_store.size_warning(_text_of_bytes(map_store.MAP_SIZE_CEILING - left))
        assert msg and str(left) in msg, \
            f"at {left} bytes of headroom the warning does not state it: {msg}"
        assert "never raise" in msg.lower(), \
            f"at {left} bytes of headroom the warning does not refuse the upward move: {msg}"
        assert "drain" in msg.lower() and "rehome" in msg.lower(), \
            f"at {left} bytes of headroom no remedy is named: {msg}"


def test_the_warning_reports_a_BREACH_as_a_breach_and_says_it_reds_every_lane():
    """Over the line the message must change, because the reader's situation has: the commit is
    refused, and by a test file naming a subject they never touched. A single message that said
    'headroom -400' would read as the same advisory it read as yesterday."""
    over = map_store.size_warning(_text_of_bytes(map_store.MAP_SIZE_CEILING + 400))
    assert over and "OVER" in over and "400 bytes" in over
    assert "EVERY LANE" in over
    assert map_store.size_headroom(_text_of_bytes(map_store.MAP_SIZE_CEILING + 400)) == -400


def test_the_ratchet_and_the_warning_read_ONE_number():
    """The reason the constant moved here (2026-09-17): the refusal and the warning are two
    readings of one limit. If the test file ever restates it, this fires -- which is the VAT
    shape this project has paid for, one rule with several implementations."""
    import ast

    from tests.design import test_simplifications_store as ratchet

    assert ratchet.MAP_SIZE_CEILING is map_store.MAP_SIZE_CEILING

    # READ AS CODE, not as text (tools/python_code_text.py's subject, and this control was refused
    # once for getting it wrong). A substring check for "400 * 1024" would fire on a comment that
    # merely quotes the number -- this file's own provenance does -- and would miss the same literal
    # spelled `409600`. What must hold is a property of the binding: the ratchet takes the ceiling
    # from somewhere else, so its value node is an ATTRIBUTE and never a literal expression.
    src = Path(__file__).resolve().parents[1] / "design" / "test_simplifications_store.py"
    bindings = [
        node for node in ast.walk(ast.parse(src.read_text(encoding="utf-8")))
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "MAP_SIZE_CEILING" for t in node.targets)
    ]
    assert len(bindings) == 1, f"{len(bindings)} bindings of MAP_SIZE_CEILING in the ratchet"
    assert isinstance(bindings[0].value, ast.Attribute), (
        "the ratchet computes its own ceiling again instead of reading the store's -- the warning "
        "surface will drift from the refusal the moment either number moves"
    )


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
