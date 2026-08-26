"""Contract for the rehomed NARRATIVE NOTE fields (atom H32).

The second tenant of the per-atom record store. `build_note`, `origin_note`,
`harden_note`, `level_hold_note`, `level_note`, `discover_note` and `notes` were
MOVED out of docs/design/maturity_map.yaml into the existing sibling store,
docs/design/simplifications/<atom_id>.yaml, under a `map_notes:` mapping. The map
keeps one `notes_rehomed: [<field>, ...]` line per atom naming which exist.

WHY THIS EXISTS. The 2026-08-09 publish wedge forced the spine size ratchet from
400K to 640K as a stated INTERIM, because the oversized content was the map's own
evidence trail -- "a control that gets angrier the more faithfully the record is
kept will eventually be paid with the record." H32 is the real fix that raise
named. Measured: the note class was 129,750 bytes over 61 atoms, and moving it
took the map 521,770 -> 393,692 bytes, back under the ORIGINAL 400K ratchet.

The invariants guarded here:
  * NO INLINE NOTES -- as a CLASS (R10), not an instance list: any `*_note`-suffixed
    field appearing inline in the map fails, so a future `frame_note` is caught by
    construction. Two sources of truth for one atom's prose are forbidden.
  * DECLARATION MATCHES STORE, both directions -- a map atom's `notes_rehomed` names
    exactly the fields its store file holds. An undeclared stored note is a note the
    spine cannot see; a declared-but-absent one is a lost record.
  * NOTES ARE NON-EMPTY STRINGS -- the migration must not have moved a key and
    dropped its text.
  * NEITHER TENANT DROPS THE OTHER -- the store's writers rebuild the whole file, so
    a writer that only knows about one tenant silently deletes the other. That is the
    live hazard of putting both in one file, so it is proven, not asserted.

Each invariant carries an R15 mutation test proving the check FIRES on its own
named defect (a control that cannot fail is worse than none).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools import simplifications_store as store

PROJECT = Path(__file__).resolve().parent.parent.parent
from tools import maturity_map_store as map_store  # noqa: E402

MAP_PATH = PROJECT / "docs" / "design" / "maturity_map.yaml"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"

DECL = store.NOTES_DECLARATION_FIELD


def _load_atoms(path: Path = MAP_PATH) -> list:
    """BOTH halves of the map (2026-08-26): the rehoming contract this file pins is about every
    atom, and a finished atom is exactly as capable of carrying an inline note as a live one."""
    return map_store.load_atoms(path)


# --------------------------------------------------------------------------
# pure checks (feedable synthetic inputs for mutation testing)
# --------------------------------------------------------------------------
def check_no_inline_notes(atoms: list) -> list[str]:
    """No map atom may carry a note-class field inline. CLASS-level: membership is
    `store.is_note_field`, which matches the named fields AND any `*_note` suffix,
    so a newly-invented note field is caught without editing this test."""
    violations = []
    for a in atoms:
        if not isinstance(a, dict):
            continue
        for k in sorted(a):
            if store.is_note_field(k):
                violations.append(
                    f"{a.get('id')}: `{k}` is inline in the map -- note prose lives "
                    "in the store (two sources of truth forbidden). Write it with "
                    f"`simplifications_store.set_note_for_atom({a.get('id')!r}, {k!r}, ...)` "
                    f"and declare it in that atom's `notes_rehomed:` list."
                )
    return violations


def check_declarations_match(atoms: list, notes_store: dict[str, dict]) -> list[str]:
    """Each atom's `notes_rehomed` must name exactly the fields its store file holds,
    in BOTH directions: a declared field with no stored note is a lost record, and a
    stored note with no declaration is invisible to the spine."""
    violations = []
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
    for aid, atom in by_id.items():
        declared = atom.get(DECL)
        stored = sorted(notes_store.get(aid, {}))
        if declared is None:
            if stored:
                violations.append(
                    f"{aid}: store holds notes {stored} but the map declares no {DECL}"
                )
            continue
        if not isinstance(declared, list):
            violations.append(f"{aid}: {DECL} must be a list, got {type(declared).__name__}")
            continue
        if sorted(declared) != stored:
            violations.append(
                f"{aid}: map {DECL}={sorted(declared)} != store fields {stored}"
            )
    for aid in notes_store:
        if aid not in by_id:
            violations.append(f"{aid}: store holds notes but no such atom in the map")
    return violations


def check_notes_are_nonempty_strings(notes_store: dict[str, dict]) -> list[str]:
    """A moved key whose text was dropped is the migration's worst failure mode: the
    spine still says the note exists, and the prose is gone."""
    violations = []
    for aid, notes in sorted(notes_store.items()):
        for field, text in sorted(notes.items()):
            if not isinstance(text, str) or not text.strip():
                violations.append(f"{aid}.{field}: empty or non-string note ({text!r})")
            if not store.is_note_field(field):
                violations.append(f"{aid}.{field}: not a note-class field")
    return violations


# --------------------------------------------------------------------------
# tests over the LIVE map + store
# --------------------------------------------------------------------------
def _live_notes() -> dict[str, dict]:
    return store.notes_load_all(STORE_DIR)


def test_the_note_tenant_is_populated_precondition():
    """These contract tests are meaningful only once the rehome has run. If the note
    tenant is empty, skip LOUDLY rather than let every check below pass vacuously --
    a fail-open contract suite is exactly the R15 pattern this project bans."""
    if not _live_notes():
        pytest.skip("note tenant empty -- H32 rehome not applied")


def test_map_carries_no_inline_note_fields():
    if not _live_notes():
        pytest.skip("note tenant empty")
    violations = check_no_inline_notes(_load_atoms())
    assert not violations, "inline note fields:\n  " + "\n  ".join(violations)


def test_declarations_match_the_store():
    if not _live_notes():
        pytest.skip("note tenant empty")
    violations = check_declarations_match(_load_atoms(), _live_notes())
    assert not violations, "declaration mismatches:\n  " + "\n  ".join(violations)


def test_stored_notes_are_nonempty_strings():
    if not _live_notes():
        pytest.skip("note tenant empty")
    violations = check_notes_are_nonempty_strings(_live_notes())
    assert not violations, "bad stored notes:\n  " + "\n  ".join(violations)


def test_notes_for_atom_returns_the_old_field_shape():
    """`notes_for_atom(id)[field]` yields exactly what `atom[field]` used to."""
    if not _live_notes():
        pytest.skip("note tenant empty")
    allnotes = _live_notes()
    for aid, notes in allnotes.items():
        assert store.notes_for_atom(aid, STORE_DIR) == notes
        for field, text in notes.items():
            assert isinstance(text, str) and text.strip(), f"{aid}.{field}"


def test_hydrate_restores_the_pre_rehome_atom_shape():
    if not _live_notes():
        pytest.skip("note tenant empty")
    atoms = {a["id"]: a for a in _load_atoms() if isinstance(a, dict) and a.get("id")}
    aid, notes = next(iter(sorted(_live_notes().items())))
    hydrated = store.hydrate(atoms[aid], STORE_DIR)
    for field, text in notes.items():
        assert hydrated[field] == text, f"{aid}.{field} not restored by hydrate"
    assert hydrated["id"] == aid
    assert aid not in str(atoms[aid].get(list(notes)[0], ""))  # was NOT inline


# --------------------------------------------------------------------------
# the one-file-two-tenants hazard: neither writer may drop the other's content
# --------------------------------------------------------------------------
def test_appending_a_simplification_preserves_the_notes(tmp_path):
    store.set_note_for_atom("A1", "build_note", "the record", tmp_path)
    store.append_for_atom("A1", ["a simplification"], tmp_path)
    assert store.notes_for_atom("A1", tmp_path) == {"build_note": "the record"}
    assert store.for_atom("A1", tmp_path) == ["a simplification"]


def test_setting_a_note_preserves_the_simplifications(tmp_path):
    store.append_for_atom("A1", ["first", "second"], tmp_path)
    store.set_note_for_atom("A1", "origin_note", "why it exists", tmp_path)
    assert store.for_atom("A1", tmp_path) == ["first", "second"]
    assert store.notes_for_atom("A1", tmp_path) == {"origin_note": "why it exists"}


def test_set_note_overwrites_by_field_and_keeps_siblings(tmp_path):
    """Notes are REVISABLE (a level_hold_note is superseded when the hold lifts) --
    unlike the append-only simplifications register."""
    store.set_note_for_atom("A1", "build_note", "v1", tmp_path)
    store.set_note_for_atom("A1", "origin_note", "origin", tmp_path)
    store.set_note_for_atom("A1", "build_note", "v2", tmp_path)
    assert store.notes_for_atom("A1", tmp_path) == {"build_note": "v2", "origin_note": "origin"}


def test_set_note_rejects_a_non_note_field(tmp_path):
    """The store is not a general side-channel for the map's structured fields."""
    with pytest.raises(ValueError):
        store.set_note_for_atom("A1", "level_current", "3", tmp_path)


def test_set_note_rejects_empty_text(tmp_path):
    with pytest.raises(ValueError):
        store.set_note_for_atom("A1", "build_note", "   ", tmp_path)


def test_notes_survive_a_multiline_value_round_trip(tmp_path):
    """The migration's real content risk: folded block scalars carrying paragraph
    breaks. A blank line inside a `>-` block is a literal newline in the value, and
    dropping it silently reflows the prose."""
    text = "first paragraph line one\nline two\n\nsecond paragraph after a blank"
    store.set_note_for_atom("A1", "notes", text, tmp_path)
    assert store.notes_for_atom("A1", tmp_path)["notes"] == text


# --------------------------------------------------------------------------
# R15 mutation tests: each check must FIRE on its own named defect
# --------------------------------------------------------------------------
def test_inline_check_fires_on_an_inline_note():
    assert check_no_inline_notes([{"id": "A1", "build_note": "x"}])
    assert not check_no_inline_notes([{"id": "A1", "notes_rehomed": ["build_note"]}])


def test_inline_check_fires_on_an_UNKNOWN_note_field():
    """The class half (R10): a note field nobody has invented yet must still fail,
    without this test being edited. `frame_note` does not exist in the map today."""
    assert check_no_inline_notes([{"id": "A1", "frame_note": "invented tomorrow"}])


def test_declaration_check_fires_on_an_undeclared_stored_note():
    assert check_declarations_match([{"id": "A1"}], {"A1": {"build_note": "x"}})


def test_declaration_check_fires_on_a_declared_but_missing_note():
    assert check_declarations_match([{"id": "A1", DECL: ["build_note"]}], {})


def test_declaration_check_fires_on_a_partial_declaration():
    atoms = [{"id": "A1", DECL: ["build_note"]}]
    assert check_declarations_match(atoms, {"A1": {"build_note": "x", "origin_note": "y"}})
    assert not check_declarations_match(
        [{"id": "A1", DECL: ["build_note", "origin_note"]}],
        {"A1": {"build_note": "x", "origin_note": "y"}},
    )


def test_declaration_check_fires_on_an_orphan_note_file():
    assert check_declarations_match([{"id": "A1"}], {"GHOST": {"build_note": "x"}})


def test_nonempty_check_fires_on_a_dropped_text():
    assert check_notes_are_nonempty_strings({"A1": {"build_note": ""}})
    assert check_notes_are_nonempty_strings({"A1": {"build_note": None}})
    assert not check_notes_are_nonempty_strings({"A1": {"build_note": "real prose"}})
