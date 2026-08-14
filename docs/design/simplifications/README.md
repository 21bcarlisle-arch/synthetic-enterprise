# The simplifications store

This directory is the extracted home of the per-atom **simplifications
register** — the append-only honesty log that records, for each maturity-map
atom, what that atom deliberately simplifies, why, and (where known) how wrong
the simplification is.

It was moved out of `docs/design/maturity_map.yaml` on 2026-08-05 (retro FM-1 /
taxonomy review F1). The register was ~89% of the map's bytes and grows without
bound; the map is the governance spine and must stay phone-readable. This was a
**MOVE, verbatim** — no note was reworded or restructured. In the map, each
atom's `simplifications` field is now a single `simplifications_count: <N>`
scalar (present only where N > 0).

## Birth certificate

**Reader.** The resident worker (map maintenance) and advisor audits. Consumers
read through `tools/simplifications_store.py`:

- `for_atom(atom_id)` → the atom's list of note strings, **exactly** what
  `atom["simplifications"]` used to yield (or `[]` if the atom has no file).
- `load_all()` → `{atom_id: [note, ...]}` across the whole store.
- `count_for_atom(atom_id)` → the note count (0 if none).

**Writer.** The resident worker, via map maintenance. The only supported write
path is `tools/simplifications_store.append_for_atom(atom_id, notes)`, driven by
`tools/merge_atom_status.py` when a build fork's write-inbox carries an
`append_simplification`. It is **append-only** (existing notes are never
rewritten — the register is honest history) and it keeps the map's
`simplifications_count` in sync. `tools/migrate_simplifications.py` was the
one-shot that populated this store; it is SINGLE-USE, not a maintenance tool.

**Bound.** One file per existing atom (`<atom_id>.yaml`), each **≤ 100 KB**.
A file's content is that atom's subtree:

```yaml
atom_id: <id>
simplifications:
- <note, verbatim>
- <note, verbatim>
```

The store location (`docs/design/simplifications/`) is **by convention**,
documented here; it sits beside the map so a tool operating on a map copy finds
the store beside that copy.

**Death.** A file is deleted when its atom is deleted or merged away. The orphan
check in `tests/design/test_simplifications_store.py` enforces the invariant
that **every store file maps to an atom id that still exists in the map** — a
store file with no atom is a defect that fails the suite.

## Invariants (enforced by the store test)

1. Every `<id>.yaml` maps to an existing atom id in the map (no orphans).
2. Each atom's map `simplifications_count` equals its store file's note count.
   An **absent** count and `simplifications_count: 0` are the same statement
   ("nothing to declare"); neither requires a file. Declaring 0 while the store
   holds notes is still a defect.
3. Every store file is ≤ 100 KB — **live files and archive chunks alike**.
4. Once the store is populated, the map carries **no** `simplifications` field
   and the map file is **< 400 KB** (the spine's size ratchet).
5. No live file exceeds the **roll watermark** (64 KB) — the roll must have run.
6. No entry appears in both an atom's archive and its live file.

---

## The roll and the archive (2026-08-11)

**The defect.** Every drain in this store's history moved a *stock* and left the
*flow* running, so the same wedge returned one level down: the map's
`simplifications` field → this store; the `*_note` fields → `map_notes` (back
over the ratchet in 24 hours); `evidence`/`expert_hour_findings` → `map_records`
(and `H27_payment_belief_gap` wedged publishing on the per-atom cap a day
later). Then `H_GAP_fabric_belief_truth_gap.yaml` reached **101,324 B of its own
102,400 B cap**, against entries averaging 5,400 B — **1,076 B of headroom**.
Its next Expert Hour could not record itself.

The class is not "this file is big". It is:

> **A bounded control over a monotonic append-only record wedges the lane that
> keeps the record.**

At the wedge only two moves are available — raise the number, or launder the
history — and this project has refused both, three times each. The third move is
a **roll**.

**The mechanism.** The live file keeps the newest entries under
`ROLL_WATERMARK` (64 KB). Older entries are moved, **verbatim and in order**,
into numbered per-atom chunks:

```
docs/design/simplifications/archive/<atom_id>.NNN.yaml   # NNN ascending = oldest first
```

- It happens **inside the sole write path** (`_write_tenants`), so no tick has to
  remember to drain. That is what makes it a mechanism rather than a convention.
- It drains **every** unbounded list tenant — `simplifications` *and* the
  `map_records` lists — taking from whichever is largest. Bounding one list and
  not its siblings is the previous drain's defect re-run.
- Chunks are **packed against the same 100 KB bound** and measured by the same
  check. An archive exempt from the ceiling would be the same defect wearing a
  new directory name.
- Chunks are written **once** and never appended to or rewritten.
- Prose records (`exit_evidence`) are never rolled; a list never rolls empty.

**Readers are unaffected.** `for_atom` and `records_for_atom` concatenate
archive-then-live, so an atom's register, its order, and its declared
`simplifications_count` are identical either side of a roll. Writers use
`live_notes_for_atom`/`live_records_for_atom` — a writer that read the
concatenated view would re-inline the archive on its next append.

**Write order is chosen, not incidental.** Chunks are written before the live
file, so an interruption between the two can only **duplicate** an entry, never
lose one — and invariant 6 detects duplication. A record store fails toward
keeping the record.

**Death.** An archive chunk dies with its atom, exactly as a live file does;
`archived_atom_ids()` puts archive-bearing ids into the orphan check's
population, so a dead atom cannot hide in the archive.

**Maintenance entrypoint.** `python3 -m tools.simplifications_store --roll <atom_id>`
forces a roll without changing content — needed only for files already over the
watermark when the mechanism landed. Ongoing rolls need no caller.

---

## Second tenant: the rehomed narrative notes (atom H32, 2026-08-09)

The same unbounded-prose pressure that evicted `simplifications` came back
through the map's **narrative note fields**. Measured on the 521,770-byte map,
they were 129,750 bytes — 25% of the spine — and they are why the size ratchet
above had to be raised 400K → 640K as an interim on 2026-08-09. That raise
stated its own reason: *"a control that gets angrier the more faithfully the
record is kept will eventually be paid with the record"*, named this rehome as
the real fix, and forbade a second raise without it. H32 did the rehome; the
ratchet is back at its original 400 KB, honestly (map now 393,692 bytes).

**The class.** `build_note`, `discover_note`, `harden_note`, `level_hold_note`,
`level_note`, `name`, `notes`, `origin_note` — defined once in
`tools/simplifications_store.NOTE_FIELDS`, plus **any** `*_note`-suffixed field.
The suffix half makes this a class guard (R10): an atom that grows a `frame_note`
inline is caught without anyone editing a list.

**`name` joined the class on 2026-08-14, and it is the one member whose field name
does not announce it.** Both earlier drains EXEMPTED it in as many words — *"a new
atom's `name`/`lane`/levels … which is the map doing its job"* — on the ground that
it is atom-COUNT driven. That was true when written. Measured on the 296-atom map
that day, by map position (which is mint order):

| atoms | mean `name` | max |
|---|---|---|
| oldest 50 | 91 B | 310 B |
| newest 50 | 860 B | 4,060 B |

150,389 B in total — **37% of the entire spine**, mean 508 B/atom, with 25 atoms
holding 45% of it. A field whose per-atom cost rises 9× from the oldest atoms to
the newest is accretion, not population growth: `name` had quietly become the
atom's narrative **brief** (multi-KB Expert-Hour write-ups), i.e. exactly this
tenant's class under a field name that reads like identity. The count-driven half
of the original claim still holds for `lane`/`level_*`/`loop_stage`, which stay in
the spine. Migration: `tools/migrate_atom_names.py` (four proof layers).

**Consequence for authors, deliberately:** an inline `name:` on a map atom is now
REFUSED at commit time. Minting an atom means writing its brief with
`simplifications_store.set_note_for_atom(<id>, "name", <text>)` and listing `name`
in that atom's `notes_rehomed:`. Readers must hydrate — `simplifications_store.atom_name`
is the single seam, used by the supervisor's draw line and every site generator.

**Where it lives.** The **same** per-atom file, under a `map_notes:` mapping:

```yaml
atom_id: <id>
simplifications:
- <note, verbatim>
map_notes:
  build_note: <prose, verbatim>
  origin_note: <prose, verbatim>
```

In the map, the atom keeps one line naming which notes exist — so the spine
still shows *that* there is a build note without carrying its prose:

```yaml
  notes_rehomed: [build_note, origin_note]
```

**Reader/writer.** Same module, `tools/simplifications_store.py`:
`notes_for_atom(id)` → `{field: text}`, `notes_load_all()` → the whole tenant,
`hydrate(atom)` → the atom dict with its notes merged back (pre-rehome shape),
and `set_note_for_atom(id, field, text)` as the narrow writer.
`tools/migrate_atom_notes.py` was the one-shot; it is SINGLE-USE.

**Why one file and not a second directory.** Both tenants are rebuilt by the
same `_dump`, so a writer that knows about only one **silently deletes the
other**. Keeping both behind one module is what makes that impossible, and the
hazard is proven by test, not asserted:
`test_appending_a_simplification_preserves_the_notes` and
`test_setting_a_note_preserves_the_simplifications`.

**Append vs overwrite.** `append_for_atom` is append-only — the simplifications
register is honest history and rewriting an entry would launder it.
`set_note_for_atom` **overwrites by field**, deliberately: a note is a *current*
statement (a `level_hold_note` is superseded when the hold lifts), and the
history of what changed lives in git, exactly where the map's note fields always
kept it.

### Note invariants (enforced by `tests/design/test_atom_notes_store.py`)

5. No note-class field appears **inline** in the map (two sources of truth
   forbidden) — checked as a class, including unknown `*_note` fields.
6. Each atom's `notes_rehomed` names **exactly** the fields its store file
   holds, in both directions. A stored note with no map atom is an orphan; a
   declared note with no stored text is a lost record.
7. Every stored note is a non-empty string.
