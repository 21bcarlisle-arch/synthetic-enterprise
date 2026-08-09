#!/usr/bin/env python3
"""Loader (and narrow writer) for the extracted per-atom RECORD store.

WHY THIS EXISTS. `docs/design/maturity_map.yaml` is the governance spine and
must stay phone-readable. ~89% of its bytes were the per-atom `simplifications`
register -- an append-only honesty log that grows without bound. That content
was MOVED (retro FM-1 / taxonomy review F1), verbatim, into a sibling store:

    docs/design/simplifications/<atom_id>.yaml

one file per atom that has any record content. In the map, the field is
replaced by `simplifications_count: <N>` (present only where N > 0). The store's
location is by CONVENTION, documented in docs/design/simplifications/README.md.

SECOND TENANT: the NARRATIVE NOTE FIELDS (atom H32, 2026-08-09). The same
unbounded-prose pressure that evicted `simplifications` came back through
`build_note`/`origin_note`/`harden_note`/`level_hold_note`/`level_note`/
`discover_note`/`notes` -- 129,750 bytes, 25% of the map, and the reason the
spine ratchet had to be raised 400K->640K as an interim on 2026-08-09. Those
fields now live in the SAME per-atom file under a `map_notes:` mapping, and the
map keeps a `notes_rehomed: [<field>, ...]` declaration naming which ones exist.
Directory name is historical (its first tenant); this is the atom record store.

ONE MODULE OWNS THE FILE FORMAT, deliberately: a second module writing these
same files would have to re-serialise them, and any writer that does not know
about the other tenant SILENTLY DROPS IT (`_dump` rebuilds the whole file). That
hazard is why `map_notes` support lives here rather than in a sibling module.

WHAT THIS MODULE GUARANTEES.
  * `for_atom(id)` returns EXACTLY the structure consumers saw in the old
    `atom["simplifications"]` field -- the list of note strings, verbatim, or
    an empty list for an atom with no store file.
  * `load_all()` returns {atom_id: simplifications_list} across the whole store
    -- the recombination that must hash-match the original map's field content.
  * `append_for_atom(id, notes)` is the narrow writer the resident worker's map
    maintenance uses (via tools/merge_atom_status.py): it appends notes to an
    atom's store file, creating the file if absent, and returns the new count.
    It never rewrites an existing note (the register is append-only, honest
    history -- SITE_CONSTITUTION rule 5, "the site is a rendering, never an
    author"). It enforces the per-file <=100KB bound. It PRESERVES `map_notes`.
  * `notes_for_atom(id)` returns {field: text} -- exactly what the map atom's
    note fields used to yield -- or {} for an atom with none.
  * `notes_load_all()` is the whole-store recombination for the note tenant.
  * `set_note_for_atom(id, field, text)` is the narrow note writer. Unlike
    simplifications, notes are REVISABLE (a `level_hold_note` is superseded when
    the hold lifts), so this one overwrites by field -- but it preserves every
    other field and the simplifications list.
  * `hydrate(atom)` merges an atom's stored notes back into a map atom dict, for
    a reader that wants the pre-rehome shape.

Stdlib + pyyaml only.
"""
from __future__ import annotations

from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"

# The store's bound (README "bound"): one file per existing atom, each <=100KB.
MAX_FILE_BYTES = 100 * 1024


def _store_dir(store_dir: Path | None = None) -> Path:
    return store_dir if store_dir is not None else STORE_DIR


def _path_for(atom_id: str, store_dir: Path | None = None) -> Path:
    return _store_dir(store_dir) / f"{atom_id}.yaml"


def _dump(atom_id: str, notes: list, map_notes: dict | None = None) -> str:
    """Serialise one atom's store file. Keys are ordered atom_id-then-list so the
    file is self-describing (the orphan test can key off either the filename or
    the in-file atom_id). Note strings are emitted verbatim -- pyyaml quotes only
    where YAML requires it, and round-trips back to the identical Python list.

    `map_notes` is the second tenant (H32). It is emitted ONLY when non-empty, so
    a simplifications-only file keeps its exact historical shape; and `simplifications`
    is emitted only when non-empty, so a notes-only atom does not gain a spurious
    empty register. EVERY writer routes through here precisely so neither tenant
    can be dropped by a writer that only knows about the other."""
    doc: dict = {"atom_id": atom_id}
    if notes:
        doc["simplifications"] = list(notes)
    if map_notes:
        doc["map_notes"] = dict(map_notes)
    return yaml.safe_dump(
        doc,
        sort_keys=False,
        allow_unicode=True,
        width=10 ** 9,
        default_flow_style=False,
    )


def _read_doc(atom_id: str, store_dir: Path | None = None) -> dict:
    """The raw store document for one atom ({} when absent/malformed)."""
    p = _path_for(atom_id, store_dir)
    if not p.is_file():
        return {}
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def for_atom(atom_id: str, store_dir: Path | None = None) -> list:
    """The simplifications list for one atom -- exactly what `atom["simplifications"]`
    used to yield. Returns [] when the atom has no store file (the old field was
    absent or empty for such atoms, and callers already did `... or []`)."""
    p = _path_for(atom_id, store_dir)
    if not p.is_file():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    notes = data.get("simplifications")
    return notes if isinstance(notes, list) else []


def load_all(store_dir: Path | None = None) -> dict[str, list]:
    """{atom_id: simplifications_list} across atoms that HAVE simplifications. The
    atom_id comes from the file's own `atom_id` field (falling back to the stem), so
    a loader result is independent of any single naming assumption. Non-yaml files
    (README.md) are skipped.

    TENANT-SCOPED (H32): a file holding ONLY the note tenant is not a zero-count
    simplifications entry, it is an atom with no simplifications at all. Reporting it
    as `{aid: []}` made `check_counts_match` fire on all 61 rehomed atoms -- the map
    correctly declares no `simplifications_count`, and the store correctly holds no
    register, but the loader invented an empty one to compare. Each tenant's loader
    reports its own population; `notes_load_all` is scoped the same way. This also
    matches the set the migration hash proof was always computed over ("atoms with a
    NON-EMPTY list -- the exact set the store holds").

    ORPHAN COVERAGE: a notes-only file whose atom died is therefore invisible HERE.
    It is caught by tests/design/test_atom_notes_store.py::check_declarations_match,
    which reports a stored note with no map atom -- the note tenant's own orphan check."""
    out: dict[str, list] = {}
    d = _store_dir(store_dir)
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        atom_id = data.get("atom_id") or p.stem
        notes = data.get("simplifications")
        if isinstance(notes, list) and notes:
            out[str(atom_id)] = notes
    return out


def count_for_atom(atom_id: str, store_dir: Path | None = None) -> int:
    """The number of simplifications recorded for one atom (0 if none)."""
    return len(for_atom(atom_id, store_dir))


def append_for_atom(atom_id: str, notes: list, store_dir: Path | None = None) -> int:
    """Append `notes` to an atom's store file (create if absent). Append-only:
    existing notes are never rewritten. Returns the new total count. Raises
    ValueError if the resulting file would exceed the <=100KB store bound."""
    if not isinstance(notes, list):
        raise ValueError(f"notes for {atom_id!r} must be a list, got {type(notes).__name__}")
    existing = for_atom(atom_id, store_dir)
    combined = existing + list(notes)
    # PRESERVE the other tenant: `_dump` rebuilds the whole file, so an append that
    # forgot `map_notes` would silently delete this atom's rehomed note record (H32).
    body = _dump(atom_id, combined, notes_for_atom(atom_id, store_dir))
    if len(body.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError(
            f"store file for {atom_id!r} would be {len(body.encode('utf-8'))} bytes, "
            f"over the {MAX_FILE_BYTES}-byte per-file bound"
        )
    d = _store_dir(store_dir)
    d.mkdir(parents=True, exist_ok=True)
    _path_for(atom_id, store_dir).write_text(body, encoding="utf-8")
    return len(combined)


# --------------------------------------------------------------------------
# Second tenant: the rehomed narrative NOTE fields (atom H32)
# --------------------------------------------------------------------------
# The field CLASS, not a list of instances. `docs/design/simplifications/README.md`
# and tests/design/test_atom_notes_store.py both key off this one definition, and
# the class guard (R10) rejects any NEW `*_note`-suffixed field appearing inline in
# the map -- so a future `frame_note` is caught by construction rather than by
# someone remembering to extend a list.
NOTE_FIELDS = (
    "build_note",
    "discover_note",
    "harden_note",
    "level_hold_note",
    "level_note",
    "notes",
    "origin_note",
)

# The map-side declaration naming which note fields an atom keeps in the store.
NOTES_DECLARATION_FIELD = "notes_rehomed"


def is_note_field(field: str) -> bool:
    """Membership in the rehomed-note CLASS: the named fields, plus anything that
    ends `_note`. The suffix half is what makes this a class guard rather than an
    instance list -- an atom that grows a `frame_note` inline is caught without a
    code change."""
    return field in NOTE_FIELDS or field.endswith("_note")


def notes_for_atom(atom_id: str, store_dir: Path | None = None) -> dict:
    """{field: text} for one atom -- exactly what the map atom's note fields used
    to yield. `{}` when the atom has no store file or no note tenant in it."""
    notes = _read_doc(atom_id, store_dir).get("map_notes")
    return dict(notes) if isinstance(notes, dict) else {}


def notes_load_all(store_dir: Path | None = None) -> dict[str, dict]:
    """{atom_id: {field: text}} across the whole store, over atoms that HAVE notes.

    The note-tenant twin of `load_all`, and the independent recombination the H32
    migration's hash proof matches against. Atom id comes from the file's own
    `atom_id` field (falling back to the stem), same as `load_all`."""
    out: dict[str, dict] = {}
    d = _store_dir(store_dir)
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        notes = data.get("map_notes")
        if isinstance(notes, dict) and notes:
            out[str(data.get("atom_id") or p.stem)] = dict(notes)
    return out


def set_note_for_atom(
    atom_id: str, field: str, text: str, store_dir: Path | None = None
) -> dict:
    """Write one note field for one atom, preserving every other field AND the
    atom's simplifications register. Returns the atom's new note mapping.

    OVERWRITE, not append -- and that asymmetry with `append_for_atom` is
    deliberate. The simplifications register is honest history: rewriting an entry
    would launder the record. A note is a CURRENT statement about the atom (a
    `level_hold_note` describes a hold that later lifts, a `build_note` is
    superseded by the next level's), so revision is the correct semantics; the
    durable history of what changed lives in git, which is where the map's own
    note fields always kept it.

    Raises ValueError for a field outside the note class (the map keeps its own
    structured fields; this store is not a general side-channel for them)."""
    if not is_note_field(field):
        raise ValueError(
            f"{field!r} is not a rehomed-note field (class: {NOTE_FIELDS} or *_note) "
            "-- structured map fields stay in the map"
        )
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"note {field!r} for {atom_id!r} must be a non-empty string")
    merged = notes_for_atom(atom_id, store_dir)
    merged[field] = text
    body = _dump(atom_id, for_atom(atom_id, store_dir), merged)
    if len(body.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError(
            f"store file for {atom_id!r} would be {len(body.encode('utf-8'))} bytes, "
            f"over the {MAX_FILE_BYTES}-byte per-file bound"
        )
    d = _store_dir(store_dir)
    d.mkdir(parents=True, exist_ok=True)
    _path_for(atom_id, store_dir).write_text(body, encoding="utf-8")
    return merged


def hydrate(atom: dict, store_dir: Path | None = None) -> dict:
    """A map atom dict with its stored notes merged back in -- the pre-rehome
    shape, for a reader that wants the whole atom in one object. Does not mutate
    the input. Map-inline values WIN over stored ones: during a partial migration
    the inline field is the one the spine is actually showing, and a silently
    preferred store copy would make the two-sources-of-truth test unfalsifiable."""
    aid = atom.get("id")
    if not aid:
        return dict(atom)
    merged = dict(notes_for_atom(str(aid), store_dir))
    merged.update(atom)
    return merged


if __name__ == "__main__":
    import json

    alln = load_all()
    print(json.dumps(
        {"atoms_with_store_files": len(alln),
         "total_notes": sum(len(v) for v in alln.values())},
        indent=2,
    ))
