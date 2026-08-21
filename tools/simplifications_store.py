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

#: libyaml's C scanner where the build has it, the pure-Python one otherwise.
#:
#: NOT A CACHE, deliberately. `supervisor.py`'s own call-site comment rules a cache out by name
#: ("a cache keyed on anything but the current stores is how a record starts outrunning the
#: code it describes") and that decision stands: this reads the same files, on every call, and
#: returns the same objects. Only the parser changes, so there is no freshness question to get
#: wrong.
#:
#: WHY IT IS WORTH A CONSTANT. `load_all()` parses every file in the store TWICE -- once to
#: read its `atom_id`, once via `for_atom` -- so the store's 297 files cost 811 parses per
#: call. That is 2.28s on the live tree (measured 2026-08-21; the supervisor comment recorded
#: 2.1s earlier, so the figure grows with the store), paid by every discovery/FRAME draw and by
#: every test that reaches one. Measured on this tree, CSafeLoader is 24x faster on the same
#: files. The cost was never the disk or the logic, it was the pure-Python scanner.
#:
#: FAIL-SOFT ON ABSENCE, never on content: a wheel built without libyaml has no `CSafeLoader`,
#: and falling back to `SafeLoader` is the same parse at the old speed. Both loaders accept the
#: identical safe YAML subset, so a file that parses under one parses under the other.
_SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def _safe_load(text: str):
    """`yaml.safe_load` with the fastest available safe loader. Same subset, same result."""
    return yaml.load(text, Loader=_SAFE_LOADER)

# The store's bound (README "bound"): one file per existing atom, each <=100KB.
MAX_FILE_BYTES = 100 * 1024

# --------------------------------------------------------------------------
# THE ROLL: the bound that makes a monotonic record survive a bounded control
# --------------------------------------------------------------------------
# WHY (2026-08-11, H_GAP_fabric_belief_truth_gap's sixth Expert Hour). Every drain
# in this store's history moved a STOCK and left the FLOW running, so the same wedge
# came back one level down: the map's `simplifications` field -> this store (FM-1),
# the map's `*_note` fields -> the `map_notes` tenant (H32, back over the ratchet in
# 24h), the map's `evidence`/`expert_hour_findings` -> the `map_records` tenant (H41,
# and H27 wedged publishing on the per-atom cap a day later). This file then reached
# 101,324 B of its own 102,400 B cap with 1,076 B of headroom, against entries
# averaging 5,400 B -- i.e. the atom's NEXT Expert Hour could not record itself, and
# the record store had become the thing that stops the record being kept.
#
# The class is not "this file is big". It is: A BOUNDED CONTROL OVER A MONOTONIC
# APPEND-ONLY RECORD WEDGES THE LANE THAT KEEPS THE RECORD -- and the only two moves
# available at the wedge are to raise the number or to launder the history, both of
# which this project has already refused. The third move is a ROLL: every file stays
# bounded, no entry is ever deleted or reworded, and the drain is a MECHANISM (it
# happens inside the sole write path) rather than a convention a tick must remember.
#
# The live file keeps the newest entries under ROLL_WATERMARK; everything older is
# moved, verbatim and in order, into numbered per-atom chunks under `archive/`. Each
# chunk is written ONCE and never appended to, and is packed against MAX_FILE_BYTES,
# so EVERY file in the store is bounded -- the archive is not a cap-exempt hole (which
# would be the same defect wearing a new directory name). Readers are unaffected:
# `for_atom`/`records_for_atom` concatenate archive-then-live, so an atom's register
# and its declared `simplifications_count` are identical either side of a roll.
ARCHIVE_DIRNAME = "archive"

# Live-file watermark. Below MAX_FILE_BYTES on purpose: the roll must leave headroom
# for several more entries, or a file pinned AT its cap rolls on every single write.
# 64 KiB against this store's 5.4 KB/entry mean leaves ~7 entries of live headroom.
ROLL_WATERMARK = 64 * 1024

# Chunks are `<atom_id>.NNN.yaml`, NNN ascending = oldest-first.
_CHUNK_GLOB_SUFFIX = ".[0-9][0-9][0-9].yaml"


def _store_dir(store_dir: Path | None = None) -> Path:
    return store_dir if store_dir is not None else STORE_DIR


def _path_for(atom_id: str, store_dir: Path | None = None) -> Path:
    return _store_dir(store_dir) / f"{atom_id}.yaml"


def _archive_dir(store_dir: Path | None = None) -> Path:
    return _store_dir(store_dir) / ARCHIVE_DIRNAME


def _dump(
    atom_id: str,
    notes: list,
    map_notes: dict | None = None,
    map_records: dict | None = None,
) -> str:
    """Serialise one atom's store file. Keys are ordered atom_id-then-list so the
    file is self-describing (the orphan test can key off either the filename or
    the in-file atom_id). Note strings are emitted verbatim -- pyyaml quotes only
    where YAML requires it, and round-trips back to the identical Python list.

    `map_notes` (H32) and `map_records` (H41) are the second and third tenants. Each
    is emitted ONLY when non-empty, so a simplifications-only file keeps its exact
    historical shape and a notes-only atom does not gain a spurious empty register.
    EVERY writer routes through here precisely so no tenant can be dropped by a
    writer that only knows about the others -- and since H41 no writer calls this
    directly with a partial tenant set either: `_write_tenants` below is the sole
    write path, and it read-modify-writes, so forgetting a tenant is no longer
    POSSIBLE rather than merely discouraged."""
    doc: dict = {"atom_id": atom_id}
    if notes:
        doc["simplifications"] = list(notes)
    if map_notes:
        doc["map_notes"] = dict(map_notes)
    if map_records:
        doc["map_records"] = dict(map_records)
    return yaml.safe_dump(
        doc,
        sort_keys=False,
        allow_unicode=True,
        width=10 ** 9,
        default_flow_style=False,
    )


def _dump_chunk(atom_id: str, n: int, notes: list, map_records: dict) -> str:
    """Serialise one ARCHIVE chunk. Same serialiser settings as `_dump` (notably
    `width=10**9`) because a reflowed dump costs ~2 KB per file of an atom's budget
    on nothing, and a size gate cannot tell that apart from content."""
    doc: dict = {"atom_id": atom_id, "chunk": n}
    if notes:
        doc["simplifications"] = list(notes)
    if map_records:
        doc["map_records"] = {k: list(v) for k, v in map_records.items()}
    return yaml.safe_dump(
        doc,
        sort_keys=False,
        allow_unicode=True,
        width=10 ** 9,
        default_flow_style=False,
    )


def archive_chunks(atom_id: str, store_dir: Path | None = None) -> list:
    """This atom's archive chunk paths, OLDEST FIRST (numeric filename order)."""
    d = _archive_dir(store_dir)
    if not d.is_dir():
        return []
    return sorted(d.glob(f"{atom_id}{_CHUNK_GLOB_SUFFIX}"))


def _archived_docs(atom_id: str, store_dir: Path | None = None) -> list:
    out = []
    for p in archive_chunks(atom_id, store_dir):
        data = _safe_load(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            out.append(data)
    return out


def archived_notes_for_atom(atom_id: str, store_dir: Path | None = None) -> list:
    """The rolled-out half of this atom's simplifications register, in order."""
    out: list = []
    for doc in _archived_docs(atom_id, store_dir):
        notes = doc.get("simplifications")
        if isinstance(notes, list):
            out.extend(notes)
    return out


def archived_records_for_atom(atom_id: str, store_dir: Path | None = None) -> dict:
    """{field: [entry, ...]} rolled out of this atom's record tenant, in order."""
    out: dict = {}
    for doc in _archived_docs(atom_id, store_dir):
        recs = doc.get("map_records")
        if not isinstance(recs, dict):
            continue
        for field, value in recs.items():
            if isinstance(value, list):
                out.setdefault(field, []).extend(value)
    return out


def archived_atom_ids(store_dir: Path | None = None) -> set:
    """Atom ids that have archive chunks -- INCLUDING any whose live file is gone.
    The orphan check reads this: an archive is not a place a dead atom can hide."""
    d = _archive_dir(store_dir)
    if not d.is_dir():
        return set()
    out = set()
    for p in sorted(d.glob("*.yaml")):
        data = _safe_load(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("atom_id"):
            out.add(str(data["atom_id"]))
        else:  # fall back to the filename, so a malformed chunk is still attributable
            out.add(p.name.rsplit(".", 2)[0])
    return out


def _plan_chunks(atom_id: str, first_n: int, notes: list, records: dict) -> list:
    """Pack moved entries into [(path_name, body)] chunks, each <= MAX_FILE_BYTES.

    Greedy and per-tenant, which is sufficient because a reader concatenates chunks
    in ascending order and each tenant's own entries therefore stay in order however
    they are distributed across chunks. Raises when a SINGLE entry cannot fit a chunk
    -- one note larger than the whole per-file bound is a defect to surface, not to
    absorb by silently widening the bound."""
    planned: list = []
    cur_notes: list = []
    cur_records: dict = {}

    def body() -> str:
        return _dump_chunk(atom_id, first_n + len(planned), cur_notes, cur_records)

    def over() -> bool:
        return len(body().encode("utf-8")) > MAX_FILE_BYTES

    def flush() -> None:
        nonlocal cur_notes, cur_records
        if not cur_notes and not cur_records:
            return
        n = first_n + len(planned)
        planned.append((f"{atom_id}.{n:03d}.yaml", body()))
        cur_notes, cur_records = [], {}

    for entry in notes:
        cur_notes.append(entry)
        if over():
            cur_notes.pop()
            if not cur_notes and not cur_records:
                raise ValueError(
                    f"a single simplifications entry for {atom_id!r} exceeds the "
                    f"{MAX_FILE_BYTES}-byte chunk bound"
                )
            flush()
            cur_notes = [entry]
    for field, entries in records.items():
        for entry in entries:
            cur_records.setdefault(field, []).append(entry)
            if over():
                cur_records[field].pop()
                if not cur_records[field]:
                    del cur_records[field]
                if not cur_notes and not cur_records:
                    raise ValueError(
                        f"a single {field!r} entry for {atom_id!r} exceeds the "
                        f"{MAX_FILE_BYTES}-byte chunk bound"
                    )
                flush()
                cur_records = {field: [entry]}
    flush()
    return planned


def _roll(atom_id: str, tenants: dict, store_dir: Path | None = None) -> list:
    """Move oldest entries out of `tenants` (MUTATED IN PLACE) until the live body
    is within ROLL_WATERMARK. Returns the planned chunks; writes nothing.

    Drains EVERY unbounded list tenant, not just `simplifications`: `map_records`
    holds `evidence` and `expert_hour_findings`, which are the same append-per-review
    shape and are exactly what H41's drain left flowing one level down. A drain that
    bounds one list and not its siblings is the previous drain's defect re-run.

    Always leaves at least one entry live in each list, so the live file keeps saying
    what shape it is and a reader never sees a tenant vanish."""
    moved_notes: list = []
    moved_records: dict = {}

    def live_body() -> int:
        body = _dump(
            atom_id, tenants["notes"], tenants["map_notes"], tenants["map_records"]
        )
        return len(body.encode("utf-8"))

    while live_body() > ROLL_WATERMARK:
        # Take from the largest rollable list: draining the biggest contributor first
        # is what keeps the number of rolls (and so of chunks) small.
        candidates = []
        if len(tenants["notes"]) > 1:
            candidates.append((_entry_bytes(tenants["notes"]), "notes", None))
        for field, value in tenants["map_records"].items():
            if isinstance(value, list) and len(value) > 1:
                candidates.append((_entry_bytes(value), "map_records", field))
        if not candidates:
            break  # nothing left to roll -- the cap check below is the real verdict
        _, tenant, field = max(candidates, key=lambda c: c[0])
        if tenant == "notes":
            moved_notes.append(tenants["notes"].pop(0))
        else:
            moved_records.setdefault(field, []).append(
                tenants["map_records"][field].pop(0)
            )

    if not moved_notes and not moved_records:
        return []
    existing = archive_chunks(atom_id, store_dir)
    first_n = 1 + max(
        (int(p.name.rsplit(".", 2)[1]) for p in existing), default=0
    )
    return _plan_chunks(atom_id, first_n, moved_notes, moved_records)


def _entry_bytes(entries: list) -> int:
    return sum(len(str(e).encode("utf-8")) for e in entries)


def _write_tenants(atom_id: str, store_dir: Path | None = None, **changed) -> str:
    """THE SOLE WRITE PATH. Read-modify-write one atom's store file: apply only the
    tenants named in `changed` (`notes`, `map_notes`, `map_records`) and carry every
    other tenant through verbatim.

    WHY THIS EXISTS (H41). `_dump` rebuilds the whole file, so with three tenants
    each of the three writers had to remember to re-read and pass the other two --
    and the H32 comment on `append_for_atom` ("an append that forgot `map_notes`
    would silently delete this atom's rehomed note record") is a warning that the
    hazard was real and was being held off by convention. Convention does not
    survive a fourth tenant. This makes the drop structurally impossible: a writer
    that says nothing about a tenant preserves it.

    Enforces the per-file bound before touching disk, so an over-bound write leaves
    the existing file intact rather than half-replacing it."""
    doc = _read_doc(atom_id, store_dir)
    existing_notes = doc.get("simplifications")
    existing_map_notes = doc.get("map_notes")
    existing_map_records = doc.get("map_records")
    tenants = {
        "notes": list(existing_notes) if isinstance(existing_notes, list) else [],
        "map_notes": dict(existing_map_notes) if isinstance(existing_map_notes, dict) else {},
        "map_records": dict(existing_map_records) if isinstance(existing_map_records, dict) else {},
    }
    unknown = set(changed) - set(tenants)
    if unknown:
        raise ValueError(f"unknown store tenant(s): {sorted(unknown)}")
    tenants.update(changed)
    body = _dump(atom_id, tenants["notes"], tenants["map_notes"], tenants["map_records"])

    # THE ROLL, inside the sole write path so no tick has to remember to drain.
    # Planned in memory first: every chunk AND the resulting live file are checked
    # against the bound BEFORE anything touches disk, so an over-bound write still
    # leaves the existing file intact rather than half-replacing it.
    planned: list = []
    if len(body.encode("utf-8")) > ROLL_WATERMARK:
        planned = _roll(atom_id, tenants, store_dir)
        if planned:
            body = _dump(
                atom_id, tenants["notes"], tenants["map_notes"], tenants["map_records"]
            )
    if len(body.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError(
            f"store file for {atom_id!r} would be {len(body.encode('utf-8'))} bytes, "
            f"over the {MAX_FILE_BYTES}-byte per-file bound"
        )
    d = _store_dir(store_dir)
    d.mkdir(parents=True, exist_ok=True)
    if planned:
        # CHUNKS BEFORE LIVE, deliberately. The two writes are not one transaction, so
        # the order chooses which way a crash between them fails: chunks-first can only
        # duplicate an entry (detectable, and `check_no_duplicate_entries` in
        # tests/design/test_simplifications_store.py asserts it over the live store),
        # live-first would LOSE one. A record store fails toward keeping the record.
        ad = _archive_dir(store_dir)
        ad.mkdir(parents=True, exist_ok=True)
        for name, chunk_body in planned:
            (ad / name).write_text(chunk_body, encoding="utf-8")
    _path_for(atom_id, store_dir).write_text(body, encoding="utf-8")
    return body


def roll_for_atom(atom_id: str, store_dir: Path | None = None) -> int:
    """Force the roll for one atom without changing its content; returns the number
    of entries archived. The maintenance entrypoint (`--roll <atom_id>`) for an atom
    already at its cap when the mechanism lands -- ongoing rolls need no caller."""
    before = len(archived_notes_for_atom(atom_id, store_dir)) + sum(
        len(v) for v in archived_records_for_atom(atom_id, store_dir).values()
    )
    _write_tenants(atom_id, store_dir)
    after = len(archived_notes_for_atom(atom_id, store_dir)) + sum(
        len(v) for v in archived_records_for_atom(atom_id, store_dir).values()
    )
    return after - before


def _read_doc(atom_id: str, store_dir: Path | None = None) -> dict:
    """The raw store document for one atom ({} when absent/malformed)."""
    p = _path_for(atom_id, store_dir)
    if not p.is_file():
        return {}
    data = _safe_load(p.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def live_notes_for_atom(atom_id: str, store_dir: Path | None = None) -> list:
    """Only the entries in the atom's LIVE file -- the writers' subject. Callers who
    want the register want `for_atom`; this exists so an append cannot re-inline the
    archive (which would undo the roll on the very next write)."""
    notes = _read_doc(atom_id, store_dir).get("simplifications")
    return list(notes) if isinstance(notes, list) else []


def for_atom(atom_id: str, store_dir: Path | None = None) -> list:
    """The simplifications list for one atom -- exactly what `atom["simplifications"]`
    used to yield. Returns [] when the atom has no store file (the old field was
    absent or empty for such atoms, and callers already did `... or []`).

    ARCHIVE THEN LIVE: rolled-out entries are older, so concatenating them ahead of
    the live file reproduces the append order the register was written in. A roll is
    therefore invisible here -- same list, same order, same count -- which is the
    property that lets the map's `simplifications_count` stay untouched across one."""
    return archived_notes_for_atom(atom_id, store_dir) + live_notes_for_atom(
        atom_id, store_dir
    )


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
    ids = set()
    for p in sorted(d.glob("*.yaml")):
        data = _safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        ids.add(str(data.get("atom_id") or p.stem))
    # ARCHIVE-BEARING ATOMS ARE IN THE POPULATION even if their live file went away:
    # otherwise the orphan check reading this becomes blind in exactly the direction
    # the archive added, and a dead atom's record could sit there unreported.
    ids |= archived_atom_ids(store_dir)
    for atom_id in sorted(ids):
        notes = for_atom(atom_id, store_dir)
        if notes:
            out[atom_id] = notes
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
    # LIVE, not `for_atom`: appending onto the concatenated view would re-inline every
    # archived entry, so the very next write would undo the roll and duplicate the
    # history into the chunks. The return is still the atom's TOTAL count, because
    # that is what the map's `simplifications_count` declares.
    combined = live_notes_for_atom(atom_id, store_dir) + list(notes)
    # PRESERVE the other tenants: `_write_tenants` carries `map_notes`/`map_records`
    # through untouched, so an append can no longer delete this atom's rehomed
    # note or list record (the H32 hazard, now structural rather than remembered).
    _write_tenants(atom_id, store_dir, notes=combined)
    return len(archived_notes_for_atom(atom_id, store_dir)) + len(
        live_notes_for_atom(atom_id, store_dir)
    )


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
    "name",
    "notes",
    "origin_note",
)

# `name` JOINED THIS CLASS 2026-08-14 (the fourth drain), and it is the one member
# whose name does not announce it, so the reason is recorded here rather than in a
# commit message. Both earlier drains EXEMPTED `name` in as many words -- "a new
# atom's `name`/`lane`/levels ... which is the map doing its job" -- on the ground
# that it is atom-COUNT driven. Measured on the live map that day (296 atoms), by
# map position, which is mint order:
#
#     oldest 50 atoms   mean    91 B    max   310 B    <- a name
#     newest 50 atoms   mean   860 B    max 4,060 B    <- a brief
#     whole field: 150,389 B = 37% OF THE SPINE, mean 508 B/atom
#
# A 9x rise in per-atom cost from the oldest atoms to the newest is accretion, not
# population growth: `name` had become the atom's narrative BRIEF (multi-KB Expert
# Hour write-ups), i.e. the same unbounded-prose class this tenant already holds,
# under a field name that reads like identity. The count-driven half of the earlier
# claim is still true of `lane`/`level_*`/`loop_stage`, which stay in the spine.
#
# CONSEQUENCE, deliberately: `check_no_inline_notes` now REFUSES an inline `name`,
# so a mint cannot put the brief back in the spine. Readers must hydrate -- see
# `hydrate`, `background/supervisor.py::_atom_name`, and the site generators.

# The map-side declaration naming which note fields an atom keeps in the store.
NOTES_DECLARATION_FIELD = "notes_rehomed"

# --------------------------------------------------------------------------
# THE NOTE RATCHET: the one tenant the roll cannot drain
# --------------------------------------------------------------------------
# WHY (2026-08-18, H27_payment_belief_gap's owed item (B)). The roll above bounds
# every LIST tenant, and that is genuinely every tenant it CAN bound: it moves whole
# entries into ordered chunks, and `map_notes` holds single strings. Chopping a
# string into archived pieces is the coercion `_roll` already refuses for a prose
# record (test_a_roll_never_empties_a_tenant_and_prose_records_are_never_rolled).
# So the note tenant is the one place the wedge this module exists to close can
# still happen -- and on 2026-08-17 it DID: H27's `level_hold_note` reached 54,930 B,
# 81% of its file, the write crossed ROLL_WATERMARK, and `roll_for_atom` returned 0
# because there was no list left to take from. The record of the atom had become
# unwritable, and the only surviving remedy was a convention -- "every Hour must
# compact as it writes" -- i.e. exactly the prose-only rule this project has
# repeatedly measured as evaporating.
#
# IT IS NOT A HYPOTHETICAL AND NOT H27's ALONE. Measured over the live store the day
# this landed, 297 atoms carry notes (mean tenant 1,595 B, p90 4,233 B) and ONE is
# already past the point of rescue: `OPS2_publish_gate_head_worktree` is 62,301 B, of
# which 60,906 B (98%) is its note tenant and 56,846 B is a single `build_note`, with
# ZERO live list entries. It sits 3,235 B under the watermark, so the next paragraph
# appended to that note wedges it -- and the roll has literally nothing to drain.
#
# THE MECHANISM IS A RATCHET, NOT A CAP, and the distinction is what stops this fix
# from becoming the defect it fixes. A flat cap enforced in `_write_tenants` would
# refuse EVERY write to an already-over atom -- including appending a simplification
# entry, which is the record-keeping this store exists for -- so it would wedge the
# lane in the name of unwedging it. Instead the bound is checked only on a NOTE write
# and only in the direction that makes things worse: a note write that leaves the
# tenant over budget is refused IF it is bigger than what it replaces. Therefore
#   * growing an over-budget note is impossible (the flow stops, everywhere, at once);
#   * COMPACTING one is always available, however far over it already is (the remedy
#     can never be locked behind the bound);
#   * every other tenant of an over-budget atom writes exactly as before.
# The existing stock is thus monotonically non-increasing without anyone editing
# another lane's narrative, which is why no exemption list is needed here.
#
# THE NUMBER IS DERIVED, not fitted. `_roll` guarantees it can reach the watermark
# only by draining lists down to one live entry each, so the irreducible live body is
# the note tenant plus one entry per list tenant. Three list tenants at this store's
# 5.4 KB mean entry is ~16 KB, so half the watermark leaves the roll 2x the room it
# can ever need. Checked against reality afterwards rather than before: 296 of the
# 297 live note tenants are already inside it, the sole exception being the OPS2
# file above, and it is ~8x the p90 -- so it bounds accretion without touching
# normal use. `test_the_note_bound_leaves_the_roll_room_to_reach_the_watermark`
# holds the derivation, so raising the number cannot silently break the roll.
NOTE_TENANT_MAX_BYTES = 32 * 1024


def note_tenant_bytes(notes: dict) -> int:
    """Bytes of one atom's whole note tenant -- the subject the bound is about.

    THE TENANT, NOT THE FIELD, deliberately. An atom carries up to eight note fields;
    bounding each one individually would let eight compliant notes sum to a file no
    roll can drain, which is the same wedge wearing a smaller number."""
    return sum(len(str(v).encode("utf-8")) for v in notes.values())


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
        data = _safe_load(p.read_text(encoding="utf-8"))
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

    # THE NOTE RATCHET (see NOTE_TENANT_MAX_BYTES). Refuse only a write that leaves
    # the tenant over budget AND bigger than it found it, so the flow stops while the
    # compaction that clears it stays available. Checked here rather than in
    # `_write_tenants` on purpose: this is the only writer that can grow the tenant,
    # and a check upstream would refuse an over-budget atom's unrelated writes too.
    before = note_tenant_bytes(merged)
    after = note_tenant_bytes({**merged, field: text})
    if after > NOTE_TENANT_MAX_BYTES and after > before:
        biggest, biggest_n = max(
            (
                (k, len(str(v).encode("utf-8")))
                for k, v in {**merged, field: text}.items()
            ),
            key=lambda kv: kv[1],
        )
        raise ValueError(
            f"note write to {field!r} would take {atom_id!r}'s note tenant to {after} "
            f"bytes (from {before}), over the {NOTE_TENANT_MAX_BYTES}-byte note "
            f"budget. The roll cannot drain a note -- it moves whole list entries and "
            f"a note is one string -- so an unbounded note tenant is the one way this "
            f"store still becomes unwritable. Largest note is {biggest!r} at "
            f"{biggest_n} bytes: COMPACT IT. A note is a CURRENT statement and its "
            f"history lives in git, so a smaller replacement is always accepted, "
            f"however far over budget the tenant already is."
        )

    merged[field] = text
    _write_tenants(atom_id, store_dir, map_notes=merged)
    return merged


# --------------------------------------------------------------------------
# Third tenant: the rehomed unbounded RECORD LIST fields (atom H41)
# --------------------------------------------------------------------------
# WHY. `evidence` and `exit_evidence` are append-per-level-move narrative lists.
# Measured over the 24h to 2026-08-10 they grew +46,853 and +20,652 bytes against
# a map that grew +67,096 net -- i.e. THEY ARE ESSENTIALLY THE WHOLE REFILL. That
# is why H32's note rehome, which drained a different field, was back over the
# spine ratchet inside a day: it removed a stock and left the flow running. This
# tenant moves the flow. Every other map field's growth is atom-COUNT driven
# (a new atom's `lane`/levels), which the per-atom budget control in
# tests/design/test_simplifications_store.py is deliberately invariant to.
#
# `name` WAS NAMED HERE AS COUNT-DRIVEN AND THAT WAS WRONG BY 2026-08-14 -- it had
# grown 91 B/atom (oldest 50) to 860 B/atom (newest 50) and was 37% of the spine.
# It is now the note tenant's; see the note beside NOTE_FIELDS above. The sentence
# is corrected rather than deleted because "which field is the flow" is the question
# this whole store exists to keep re-asking, and a drain that exempts a field on a
# stated ground should show when that ground expired.
#
# CLASS GUARD, not an instance list (R10): `evidence` plus any `*_evidence`, so a
# future `frame_evidence` appearing inline in the map is caught by construction
# rather than by someone remembering to extend a tuple.
#
# SHAPE-TOLERANT BY MEASUREMENT, not by taste: on the live map `evidence` is a list
# on all 259 atoms that carry it and `exit_evidence` is a prose STRING on all 3 --
# the class is "the unbounded record fields", which is why the tenant is called
# `map_records` and not `map_records`. Values are carried VERBATIM in whatever shape
# the map held them; nothing here coerces, because a coercion in a migration is a
# silent content edit (`list("some prose")` would have exploded a string into
# characters and still round-tripped through a naive hash).
RECORD_FIELDS = ("evidence", "exit_evidence", "expert_hour_findings")

# THE SECOND UNBOUNDED FLOW, found one level down (2026-08-10, the fourteenth publish wedge).
# H41 drained the TOP-LEVEL record lists and the map's growth did slow -- but `expert_hour` is a
# structured mapping whose `findings:` member is the same shape hiding inside it: one narrative
# entry appended per Expert Hour, forever, and nothing above the map's top level was looking.
# H27_payment_belief_gap took its seventh Hour and crossed the 12,288 B per-atom cap by 617 B,
# wedging publishing behind a control that was working exactly as designed ("accreting prose into
# one atom always must red this"). 53,526 B live in this member across 176 atoms, power-law
# distributed: two atoms carry 22,000 B of it.
#
# The map keeps `expert_hour: {last, status}` -- the STRUCTURED members every consumer reads
# (generate_proof_data's status counts, generate_maturity_map_data's expert_hour_status,
# supervisor's re-stamp check). Only the unbounded list moves, and it moves ONE ATOM AT A TIME as
# the cap names it: the declaration is per-atom, so a partial migration is representable, and an
# atom whose findings are in the store never grows the map again because the next Hour appends
# through `append_to_record_for_atom`. That is the drain H32 lacked.
RECORDS_DECLARATION_FIELD = "records_rehomed"


def is_record_field(field: str) -> bool:
    """Membership in the rehomed-record CLASS: `evidence` itself, plus anything
    ending `_evidence` or `_findings`.

    The `_findings` half is a CLASS guard, not an instance (R10): a future
    `coldwalk_findings` or `harden_sweep_findings` -- the same append-per-review shape
    under a different review name -- is admissible here by construction, rather than by
    someone remembering to extend a tuple after the next wedge."""
    return (
        field == "evidence"
        or field.endswith("_evidence")
        or field.endswith("_findings")
    )


def live_records_for_atom(atom_id: str, store_dir: Path | None = None) -> dict:
    """Only the entries in the atom's LIVE file -- the writers' subject (see
    `live_notes_for_atom` for why the writers must not see the archive)."""
    recs = _read_doc(atom_id, store_dir).get("map_records")
    if not isinstance(recs, dict):
        return {}
    return {k: (list(v) if isinstance(v, list) else v) for k, v in recs.items()}


def records_for_atom(atom_id: str, store_dir: Path | None = None) -> dict:
    """{field: value} for one atom -- exactly what the map atom's record fields
    used to yield, in their original shape. `{}` when the atom has no store file
    or no record tenant in it.

    ARCHIVE THEN LIVE for the LIST-shaped fields, same as `for_atom`. Prose fields
    (`exit_evidence`) are never rolled, so they only ever appear live."""
    archived = archived_records_for_atom(atom_id, store_dir)
    live = live_records_for_atom(atom_id, store_dir)
    merged = {k: list(v) for k, v in archived.items()}
    for field, value in live.items():
        if isinstance(value, list) and field in merged:
            merged[field] = merged[field] + list(value)
        else:
            merged[field] = list(value) if isinstance(value, list) else value
    return merged


def records_load_all(store_dir: Path | None = None) -> dict[str, dict]:
    """{atom_id: {field: value}} across the whole store, over atoms that HAVE
    record fields. The record-tenant twin of `load_all`/`notes_load_all`, and the
    independent recombination the H41 migration's hash proof matches against.
    Tenant-scoped for the same reason `load_all` is (see its docstring)."""
    out: dict[str, dict] = {}
    d = _store_dir(store_dir)
    if not d.is_dir():
        return out
    ids = set()
    for p in sorted(d.glob("*.yaml")):
        data = _safe_load(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            ids.add(str(data.get("atom_id") or p.stem))
    ids |= archived_atom_ids(store_dir)  # see `load_all` -- the archive is in scope
    for atom_id in sorted(ids):
        recs = records_for_atom(atom_id, store_dir)
        if recs:
            out[atom_id] = recs
    return out


def append_to_record_for_atom(
    atom_id: str, field: str, entries: list, store_dir: Path | None = None
) -> list:
    """Append entries to one rehomed LIST-shaped record field, preserving every
    other tenant. Returns the field's new full list.

    APPEND, not overwrite -- matching `append_for_atom` and for the same reason:
    `evidence` is honest history (the artefact trail behind a level move), so
    rewriting an entry would launder the record. THIS IS THE ONGOING DRAIN: the
    fold path that used to grow the map's `evidence:` line now grows a store file
    instead, so the map's byte count no longer tracks how much work was done. That
    is the difference between this repair and H32's, which moved a stock and left
    the flow running (the map was back over the ratchet in 24h).

    Refuses to append to a non-list existing value: `exit_evidence` is prose, and
    silently turning a string into a list is the coercion this tenant exists to
    avoid. Use `set_record_for_atom` to revise a prose record."""
    if not is_record_field(field):
        raise ValueError(
            f"{field!r} is not a rehomed-record field (class: `evidence` or *_evidence) "
            "-- structured map fields stay in the map"
        )
    if not isinstance(entries, list):
        raise ValueError(
            f"entries for {atom_id}.{field} must be a list, got {type(entries).__name__}"
        )
    # LIVE, not `records_for_atom` -- see `append_for_atom` for why a writer must
    # never read across the archive.
    merged = live_records_for_atom(atom_id, store_dir)
    existing = merged.get(field, [])
    if not isinstance(existing, list):
        raise ValueError(
            f"{atom_id}.{field} holds a {type(existing).__name__}, not a list "
            "-- cannot append to a prose record"
        )
    merged[field] = existing + list(entries)
    _write_tenants(atom_id, store_dir, map_records=merged)
    return records_for_atom(atom_id, store_dir)[field]


def set_record_for_atom(
    atom_id: str, field: str, value, store_dir: Path | None = None
) -> dict:
    """Write one rehomed record field WHOLE (the migration's writer), preserving
    every other tenant. Ongoing evidence writes should use
    `append_to_record_for_atom`; this exists for the one-shot move, which must
    reproduce the map's value verbatim in its original shape."""
    if not is_record_field(field):
        raise ValueError(
            f"{field!r} is not a rehomed-record field (class: `evidence` or *_evidence) "
            "-- structured map fields stay in the map"
        )
    if not isinstance(value, (list, str)):
        raise ValueError(
            f"{atom_id}.{field} must be a list or a string, got {type(value).__name__}"
        )
    # A WHOLE-FIELD write over an atom that has ROLLED entries for that field would
    # silently duplicate them (the archive keeps its copy, the live file gets the
    # caller's whole list). Refuse rather than absorb: this is the one-shot migration
    # writer, and an atom with an archive is by definition past its migration.
    if field in archived_records_for_atom(atom_id, store_dir):
        raise ValueError(
            f"{atom_id}.{field} has archived entries -- a whole-field write would "
            "duplicate them; use append_to_record_for_atom"
        )
    merged = live_records_for_atom(atom_id, store_dir)
    merged[field] = list(value) if isinstance(value, list) else value
    _write_tenants(atom_id, store_dir, map_records=merged)
    return records_for_atom(atom_id, store_dir)


def atom_name(atom: dict, store_dir: Path | None = None) -> str:
    """One atom's BRIEF, wherever it now lives (the 2026-08-14 `name` drain).

    Every reader of `name` routes through here so the rehome has ONE seam rather
    than one per call site, and so a reader added later cannot silently read a
    field that is no longer inline and conclude the atom has no brief. That
    failure would be quiet and user-visible: the supervisor's draw line degrades
    to `?`, and three site surfaces render an empty atom name -- nothing raises.

    Inline WINS over stored, matching `hydrate` and for the same reason: during a
    partial migration the inline value is the one the spine is actually showing,
    and a silently-preferred store copy would make the two-sources-of-truth
    contract unfalsifiable. Returns `""` (never None) so format strings and
    truthiness tests at the call sites behave as they did pre-drain."""
    if atom.get("name"):
        return str(atom["name"])
    aid = atom.get("id")
    if not aid:
        return ""
    return str(notes_for_atom(str(aid), store_dir).get("name") or "")


def hydrate(atom: dict, store_dir: Path | None = None) -> dict:
    """A map atom dict with its stored notes AND list fields merged back in -- the
    pre-rehome shape, for a reader that wants the whole atom in one object. Does not
    mutate the input. Map-inline values WIN over stored ones: during a partial
    migration the inline field is the one the spine is actually showing, and a
    silently preferred store copy would make the two-sources-of-truth test
    unfalsifiable."""
    aid = atom.get("id")
    if not aid:
        return dict(atom)
    merged = dict(notes_for_atom(str(aid), store_dir))
    merged.update(records_for_atom(str(aid), store_dir))
    merged.update(atom)
    return merged


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) == 3 and sys.argv[1] == "--roll":
        aid = sys.argv[2]
        before = _path_for(aid).stat().st_size if _path_for(aid).is_file() else 0
        n = roll_for_atom(aid)
        print(json.dumps({
            "atom_id": aid,
            "entries_archived": n,
            "live_bytes_before": before,
            "live_bytes_after": _path_for(aid).stat().st_size,
            "chunks": [p.name for p in archive_chunks(aid)],
            "register_count": len(for_atom(aid)),
        }, indent=2))
        raise SystemExit(0)

    alln = load_all()
    print(json.dumps(
        {"atoms_with_store_files": len(alln),
         "total_notes": sum(len(v) for v in alln.values())},
        indent=2,
    ))
