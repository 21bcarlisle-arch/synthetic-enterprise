#!/usr/bin/env python3
"""Loader (and narrow writer) for the extracted simplifications store.

WHY THIS EXISTS. `docs/design/maturity_map.yaml` is the governance spine and
must stay phone-readable. ~89% of its bytes were the per-atom `simplifications`
register -- an append-only honesty log that grows without bound. That content
was MOVED (retro FM-1 / taxonomy review F1), verbatim, into a sibling store:

    docs/design/simplifications/<atom_id>.yaml

one file per atom that has any simplifications. In the map, the field is
replaced by `simplifications_count: <N>` (present only where N > 0). The store's
location is by CONVENTION, documented in docs/design/simplifications/README.md.

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
    author"). It enforces the per-file <=100KB bound.

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


def _dump(atom_id: str, notes: list) -> str:
    """Serialise one atom's store file. Keys are ordered atom_id-then-list so the
    file is self-describing (the orphan test can key off either the filename or
    the in-file atom_id). Note strings are emitted verbatim -- pyyaml quotes only
    where YAML requires it, and round-trips back to the identical Python list."""
    return yaml.safe_dump(
        {"atom_id": atom_id, "simplifications": list(notes)},
        sort_keys=False,
        allow_unicode=True,
        width=10 ** 9,
    )


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
    """{atom_id: simplifications_list} across the whole store. The atom_id comes
    from the file's own `atom_id` field (falling back to the stem), so a loader
    result is independent of any single naming assumption. Non-yaml files
    (README.md) are skipped."""
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
        out[str(atom_id)] = notes if isinstance(notes, list) else []
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
    body = _dump(atom_id, combined)
    if len(body.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError(
            f"store file for {atom_id!r} would be {len(body.encode('utf-8'))} bytes, "
            f"over the {MAX_FILE_BYTES}-byte per-file bound"
        )
    d = _store_dir(store_dir)
    d.mkdir(parents=True, exist_ok=True)
    _path_for(atom_id, store_dir).write_text(body, encoding="utf-8")
    return len(combined)


if __name__ == "__main__":
    import json

    alln = load_all()
    print(json.dumps(
        {"atoms_with_store_files": len(alln),
         "total_notes": sum(len(v) for v in alln.values())},
        indent=2,
    ))
