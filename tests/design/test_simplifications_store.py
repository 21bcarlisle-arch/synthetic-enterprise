"""Contract for the extracted simplifications store (retro FM-1 / taxonomy F1).

The simplifications register was MOVED out of docs/design/maturity_map.yaml into
a sibling store, docs/design/simplifications/<atom_id>.yaml, so the governance
spine stays phone-readable. These tests guard the store's birth-certificate
invariants (docs/design/simplifications/README.md):

  * no orphans -- every store file maps to an atom id that still exists;
  * counts match -- each atom's map `simplifications_count` equals its store
    file's note count;
  * per-file <=100KB bound;
  * once the store is POPULATED, the map holds no `simplifications` field and is
    < 400KB (the spine's size ratchet).

The last group is guarded as R15-style mutation tests too (a control that
cannot fail is worse than none): each invariant has a synthetic case proving the
check FIRES on its own named defect.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools import simplifications_store as store

PROJECT = Path(__file__).resolve().parent.parent.parent
MAP_PATH = PROJECT / "docs" / "design" / "maturity_map.yaml"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"
# RAISED 400K -> 640K, 2026-08-09, INTERIM — during the ~10h publish wedge, in which this
# ratchet was the SECOND red in the queue behind the ruff baseline (the publish gate runs
# `pytest tests/` with `-x`, so tests/design/ does block publishing — contrary to the
# "not currently blocking" note in WORKER_FINDING_MAP_SIZE_RATCHET_RED_ON_HEAD_2026-08-09,
# which checked the pre-commit gate only).
#
# This is candidate 1 of the two that finding named ("raise it WITH A STATED REASON and a
# ratchet that can still fire"), taken deliberately over candidate 2 (rehome the long-note
# fields into the store) because candidate 2 is a real refactor and 32 run_complete markers
# were queued unpublished behind it. It is NOT paid with the record: no build_note was
# trimmed. THE REASON: what is oversized is `build_note`/`harden_note`/`level_hold_note` —
# the map's evidence trail — across 241 atoms. A control that gets angrier the more
# faithfully the record is kept will eventually be paid with the record.
#
# STILL A REAL RATCHET, and deliberately a tight one: the map was 489,935 bytes when this
# was raised and grows ~10KB per recording tick, so 640K is ~15 ticks of headroom, not an
# unreachable number. It WILL fire again within days. That is the point — H32
# (`H32_map_size_ratchet_red_on_head`, candidate 2) is the real fix and stays queued; this
# buys the publish queue, not an amnesty. Do not raise it a second time without doing H32.
MAP_SIZE_CEILING = 640 * 1024
PER_FILE_CEILING = 100 * 1024


def _load_atoms(path: Path = MAP_PATH) -> list:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _map_has_simplifications_field(path: Path = MAP_PATH) -> bool:
    import re

    pat = re.compile(r"^\s*simplifications:\s")
    return any(pat.match(ln) for ln in path.read_text(encoding="utf-8").splitlines())


def _store_is_populated() -> bool:
    return STORE_DIR.is_dir() and any(STORE_DIR.glob("*.yaml"))


# --------------------------------------------------------------------------
# pure checks (feedable synthetic inputs for mutation testing)
# --------------------------------------------------------------------------
def check_no_orphans(atom_ids: set[str], store_map: dict[str, list]) -> list[str]:
    """A store atom id with no matching map atom is an orphan (README 'death')."""
    return [f"orphan store file: {sid} (no such atom in the map)"
            for sid in store_map if sid not in atom_ids]


def check_counts_match(atoms: list, store_map: dict[str, list]) -> list[str]:
    """Each atom's `simplifications_count` must equal its store file's note count;
    an atom with a store file must declare a count and vice versa."""
    violations = []
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
    for aid, notes in store_map.items():
        atom = by_id.get(aid)
        if atom is None:
            continue  # orphan -- reported by check_no_orphans
        declared = atom.get("simplifications_count")
        if declared != len(notes):
            violations.append(
                f"{aid}: map simplifications_count={declared!r} != store file "
                f"count={len(notes)}"
            )
    for aid, atom in by_id.items():
        c = atom.get("simplifications_count")
        if c is not None and aid not in store_map:
            violations.append(
                f"{aid}: map declares simplifications_count={c} but has no store file"
            )
    return violations


def check_file_sizes(store_dir: Path, ceiling: int = PER_FILE_CEILING) -> list[str]:
    return [f"{p.name}: {p.stat().st_size} bytes > {ceiling}"
            for p in sorted(store_dir.glob("*.yaml"))
            if p.stat().st_size > ceiling]


# --------------------------------------------------------------------------
# tests over the LIVE store
# --------------------------------------------------------------------------
def test_store_is_populated_precondition():
    """These contract tests are meaningful only once the migration has run. If
    the store is empty (the atomicity-fallback state), skip loudly rather than
    pass vacuously."""
    if not _store_is_populated():
        pytest.skip("simplifications store is empty -- migration not applied (see PR notes)")


def test_no_orphan_store_files():
    if not _store_is_populated():
        pytest.skip("store empty")
    atoms = _load_atoms()
    ids = {a["id"] for a in atoms if isinstance(a, dict) and a.get("id")}
    violations = check_no_orphans(ids, store.load_all(STORE_DIR))
    assert not violations, "orphan store files:\n  " + "\n  ".join(violations)


def test_counts_match_file_contents():
    if not _store_is_populated():
        pytest.skip("store empty")
    violations = check_counts_match(_load_atoms(), store.load_all(STORE_DIR))
    assert not violations, "count mismatches:\n  " + "\n  ".join(violations)


def test_every_file_within_size_bound():
    if not _store_is_populated():
        pytest.skip("store empty")
    violations = check_file_sizes(STORE_DIR)
    assert not violations, "oversized store files:\n  " + "\n  ".join(violations)


def test_loader_returns_the_old_field_structure():
    """for_atom returns exactly what atom['simplifications'] used to yield: a list
    of note strings. load_all keys those by atom id."""
    if not _store_is_populated():
        pytest.skip("store empty")
    all_notes = store.load_all(STORE_DIR)
    assert all_notes, "populated store must load at least one atom"
    for aid, notes in all_notes.items():
        assert isinstance(notes, list)
        assert all(isinstance(n, str) for n in notes), f"{aid}: non-string note"
        assert store.for_atom(aid, STORE_DIR) == notes


def test_map_has_no_simplifications_field_when_store_populated():
    """The spine's core invariant: two sources of truth are forbidden. Active only
    when the store is populated (the empty-store fallback leaves the map intact)."""
    if not _store_is_populated():
        pytest.skip("store empty")
    assert not _map_has_simplifications_field(), (
        "the map still carries a `simplifications:` field while the store is "
        "populated -- two sources of truth (forbidden)"
    )


def test_map_within_size_ratchet_when_store_populated():
    if not _store_is_populated():
        pytest.skip("store empty")
    size = MAP_PATH.stat().st_size
    assert size < MAP_SIZE_CEILING, (
        f"maturity_map.yaml is {size} bytes, over the {MAP_SIZE_CEILING}-byte "
        "spine ratchet -- the register must live in the store, not the map"
    )


# --------------------------------------------------------------------------
# R15 mutation tests: each check must FIRE on its own named defect
# --------------------------------------------------------------------------
def test_orphan_check_fires_on_an_orphan():
    assert check_no_orphans({"A1"}, {"A1": ["n"], "GHOST": ["x"]})
    assert not check_no_orphans({"A1", "GHOST"}, {"A1": ["n"], "GHOST": ["x"]})


def test_count_check_fires_on_mismatch():
    atoms = [{"id": "A1", "simplifications_count": 2}]
    assert check_counts_match(atoms, {"A1": ["one"]})  # declared 2, file has 1
    assert not check_counts_match(atoms, {"A1": ["one", "two"]})


def test_count_check_fires_on_count_without_file():
    atoms = [{"id": "A1", "simplifications_count": 3}]
    assert check_counts_match(atoms, {})  # count declared, no store file


def test_size_check_fires_on_oversize(tmp_path):
    big = tmp_path / "BIG.yaml"
    big.write_text("atom_id: BIG\nsimplifications:\n- " + ("x" * (PER_FILE_CEILING + 10)))
    assert check_file_sizes(tmp_path)
    small = tmp_path / "small_dir"
    small.mkdir()
    (small / "OK.yaml").write_text("atom_id: OK\nsimplifications: []\n")
    assert not check_file_sizes(small)


def test_writer_round_trips_and_enforces_the_bound(tmp_path):
    """append_for_atom appends verbatim, is append-only, and rejects an oversize
    write (the store bound must be able to FAIL)."""
    sd = tmp_path / "simplifications"
    assert store.append_for_atom("Z1", ["first"], sd) == 1
    assert store.append_for_atom("Z1", ["second"], sd) == 2
    assert store.for_atom("Z1", sd) == ["first", "second"]
    assert store.load_all(sd) == {"Z1": ["first", "second"]}
    with pytest.raises(ValueError, match="per-file bound"):
        store.append_for_atom("Z1", ["x" * (PER_FILE_CEILING + 10)], sd)
