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
# RESTORED 640K -> 400K, 2026-08-09, by H32 (`H32_map_size_ratchet_red_on_head`) — the
# real fix the interim raise named and made a precondition of any second raise.
#
# HISTORY, kept because the reasoning is the point. On 2026-08-09 this ceiling was raised
# 400K -> 640K during the ~10h publish wedge, where it was the SECOND red behind the ruff
# baseline (the publish gate runs `pytest tests/` with `-x`, so tests/design/ does block
# publishing). That was candidate 1 of the two the originating finding named, taken over
# candidate 2 (rehome the long-note fields) because candidate 2 is a real refactor and 32
# run_complete markers were queued behind it. The stated reason for the raise: what was
# oversized is the map's own EVIDENCE TRAIL — `build_note`/`harden_note`/`level_hold_note` —
# and "a control that gets angrier the more faithfully the record is kept will eventually
# be paid with the record."
#
# H32 has now done candidate 2. The narrative note CLASS (`build_note`, `origin_note`,
# `harden_note`, `level_hold_note`, `level_note`, `discover_note`, `notes`) was MOVED
# verbatim into the sibling store's `map_notes:` tenant — 84 fields over 61 atoms,
# 129,750 bytes — taking the map 521,770 -> 393,692. Nothing was trimmed: the record is
# intact and hash-proven identical (tools/migrate_atom_notes.py, three proof layers), it
# simply no longer lives in the spine. So the ORIGINAL ceiling fits again, honestly.
#
# The ratchet is therefore tight ON PURPOSE and will fire again — but what it now measures
# is the map's STRUCTURED spine (245 atoms x id/lane/level/evidence/file_scope), which grows
# with the atom count, not with how much prose an atom writes about itself. That is the
# distinction the raise was reaching for. If it goes red again, the question is whether the
# spine has a new unbounded FIELD to rehome (extend `simplifications_store.NOTE_FIELDS`, and
# tests/design/test_atom_notes_store.py's class guard already fails on any new `*_note`),
# NOT whether to raise the number.
#
# IT WENT RED AGAIN IN 24 HOURS, and the paragraph above asked the right question but named
# the wrong field. H41 (2026-08-10) answered it by measuring the REFILL rather than the
# stock: over the 24h to 2026-08-10 the map grew +67,096 bytes net, of which `evidence`
# was +46,853 and `exit_evidence` +20,652 — i.e. the two record fields WERE the growth, and
# H32 had drained a different one. Those are now the store's `map_records:` tenant
# (tools/migrate_atom_lists.py, same three proof layers, 259 atoms / 21,586 entries moved
# verbatim), taking the map 430,962 -> 300,565. THIS NUMBER IS STILL 400K, unraised, for the
# third time — every wedge in this control's history has been paid by moving content out,
# never by moving the line.
MAP_SIZE_CEILING = 400 * 1024
PER_FILE_CEILING = 100 * 1024

# ── The scale-invariant half of the control (H41) ────────────────────────────────
# A FIXED ceiling on a GROWING population is the defect this control kept re-expressing.
# 31 atoms were minted in that same 24h window, and an honestly-recorded 260-atom map
# legitimately costs more bytes than a 229-atom one — so a whole-file ceiling cannot tell
# "the company did more work" (fine, and the map's whole purpose) from "one atom accreted
# 4KB of prose" (the thing that actually needs draining). It reds on both, which is why it
# twice arrived as a publish wedge carrying no information about what to fix.
#
# The per-atom budget is invariant to atom count by construction: minting never moves it,
# accretion always does, and when it fires it NAMES the offending atom instead of handing
# the reader a total. Both numbers are derived from the map AFTER the H41 drain (mean 1,156
# B/atom over 260 atoms; largest atom SITE1_expert_doors at 10,552 B) — derived from a
# cleaned map, never from the pressure of a wedge, which is the condition the originating
# finding put on any re-derivation.
MAP_MEAN_BYTES_PER_ATOM = 1400
MAP_MAX_BYTES_PER_ATOM = 12 * 1024


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
    an atom with a NON-ZERO count must have a store file.

    ABSENT AND ZERO ARE THE SAME STATEMENT (H32, 2026-08-09). The migration's own
    contract is "an atom with an EMPTY list gets no count and no store file", but
    four atoms were later hand-authored with an explicit `simplifications_count: 0`,
    and `load_all` is tenant-scoped so an empty register is not in `store_map` at
    all. Requiring a file for a zero count would fail those four for stating, in the
    permitted alternative spelling, that they have nothing to declare.

    This does NOT weaken the control: an atom that HAS notes in the store while
    declaring 0 is still caught by the first loop (0 != len(notes)), which is the
    defect that actually matters -- a register the spine under-reports."""
    violations = []
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
    for aid, notes in store_map.items():
        atom = by_id.get(aid)
        if atom is None:
            continue  # orphan -- reported by check_no_orphans
        declared = atom.get("simplifications_count")
        if (declared or 0) != len(notes):
            violations.append(
                f"{aid}: map simplifications_count={declared!r} != store file "
                f"count={len(notes)}"
            )
    for aid, atom in by_id.items():
        c = atom.get("simplifications_count")
        if c and aid not in store_map:
            violations.append(
                f"{aid}: map declares simplifications_count={c} but has no store file"
            )
    return violations


def check_file_sizes(store_dir: Path, ceiling: int = PER_FILE_CEILING) -> list[str]:
    """Every file in the store is bounded -- LIVE FILES AND ARCHIVE CHUNKS ALIKE.

    The archive (2026-08-11) exists because this ceiling, over a monotonic
    append-only record, wedges the lane that keeps the record: this atom's own store
    file reached 101,324 B of 102,400 with entries averaging 5,400 B, so its next
    Expert Hour could not record itself. The roll answers that by bounding the LIVE
    file and moving older entries out verbatim.

    An archive EXEMPT from this ceiling would be the same defect wearing a new
    directory name -- one uncapped file per atom, growing forever, and the first
    reader to walk it back into memory pays for all of it. So the chunks are packed
    against the same bound and measured by the same check. `glob("*.yaml")` alone
    would have silently skipped them (a subdirectory does not match), which is the
    fail-open shape: a control that stops seeing the population it was widened for."""
    files = sorted(store_dir.glob("*.yaml")) + sorted(
        (store_dir / store.ARCHIVE_DIRNAME).glob("*.yaml")
    )
    return [f"{p.name}: {p.stat().st_size} bytes > {ceiling}"
            for p in files if p.stat().st_size > ceiling]


def check_no_duplicate_entries(store_dir: Path) -> list[str]:
    """No entry may be in BOTH an atom's archive and its live file.

    This is the roll's own failure mode, and the one its write ORDER deliberately
    chooses: chunks are written before the live file, so an interruption between the
    two duplicates an entry rather than losing it. Duplication has to be DETECTED for
    that trade to be honest -- an undetected duplicate is a silently double-counted
    register, and `simplifications_count` would then disagree with the map for a
    reason no one could see."""
    violations = []
    for p in sorted(store_dir.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        aid = str(data.get("atom_id") or p.stem)
        archived = set(store.archived_notes_for_atom(aid, store_dir))
        both = archived & set(store.live_notes_for_atom(aid, store_dir))
        if both:
            violations.append(
                f"{aid}: {len(both)} simplifications entry/entries in BOTH the "
                f"archive and the live file (first 60 chars: {sorted(both)[0][:60]!r})"
            )
        arch_recs = store.archived_records_for_atom(aid, store_dir)
        live_recs = store.live_records_for_atom(aid, store_dir)
        for field, entries in arch_recs.items():
            live = live_recs.get(field)
            if not isinstance(live, list):
                continue
            dupes = {str(e) for e in entries} & {str(e) for e in live}
            if dupes:
                violations.append(
                    f"{aid}.{field}: {len(dupes)} entry/entries in BOTH the archive "
                    "and the live file"
                )
    return violations


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


def test_no_entry_is_in_both_the_archive_and_the_live_file():
    if not _store_is_populated():
        pytest.skip("store empty")
    violations = check_no_duplicate_entries(STORE_DIR)
    assert not violations, "duplicated store entries:\n  " + "\n  ".join(violations)


def test_the_live_store_has_roll_headroom():
    """THE WEDGE ITSELF, as a standing control rather than a thing noticed once.

    The size bound above fires only once a file is ALREADY over -- by which point the
    lane is wedged and the only moves left are to raise the number or launder the
    record. This fires while there is still somewhere to go: a live file over the
    watermark means the roll did not run (or did not shrink it), and that is knowable
    a whole entry BEFORE it costs anyone a publish.

    It is not a duplicate of the ceiling test in the direction that matters: the
    ceiling passed at 101,324 B of 102,400 on the day the next Hour could not be
    written down."""
    if not _store_is_populated():
        pytest.skip("store empty")
    over = [
        f"{p.name}: {p.stat().st_size} B over the {store.ROLL_WATERMARK} B watermark"
        for p in sorted(STORE_DIR.glob("*.yaml"))
        if p.stat().st_size > store.ROLL_WATERMARK
    ]
    assert not over, (
        "live store files above the roll watermark -- the roll has not drained them:"
        "\n  " + "\n  ".join(over)
    )


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


def atom_byte_sizes(text: str) -> dict[str, int]:
    """{atom_id: bytes its `- id:` block occupies in the map text}.

    Text-measured, not yaml-measured: what the ratchet cares about is the bytes on
    disk, and a re-serialised atom is not the same size as the hand-authored one."""
    lines = text.splitlines(keepends=True)
    starts = [i for i, ln in enumerate(lines) if ln.startswith("- id: ")]
    out: dict[str, int] = {}
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        out[lines[i][len("- id: "):].strip()] = sum(
            len(ln.encode("utf-8")) for ln in lines[i:end]
        )
    return out


def check_per_atom_budget(
    sizes: dict[str, int],
    mean_budget: int = MAP_MEAN_BYTES_PER_ATOM,
    max_budget: int = MAP_MAX_BYTES_PER_ATOM,
) -> list[str]:
    """Violations of the scale-invariant budget. Empty list == within budget.

    VACUITY GUARD: an empty map is not a passing map. A control whose population can
    be zero passes loudest exactly when its input has gone missing, which is the
    fail-open shape R15 names -- so no atoms is itself the violation."""
    if not sizes:
        return ["no atoms measured -- an empty map is not a map within budget"]
    out = []
    mean = sum(sizes.values()) / len(sizes)
    if mean > mean_budget:
        out.append(
            f"mean {mean:.0f} B/atom over {len(sizes)} atoms, above the "
            f"{mean_budget} B/atom budget -- atoms are accreting prose; rehome the "
            "growing FIELD to the record store rather than raising this number"
        )
    for aid, n in sorted(sizes.items(), key=lambda kv: -kv[1]):
        if n > max_budget:
            out.append(f"{aid}: {n} B, above the {max_budget} B per-atom cap")
    return out


def test_map_within_per_atom_budget():
    """The scale-invariant companion to the whole-file ratchet: minting atoms must
    never red this, accreting prose into one always must."""
    if not _store_is_populated():
        pytest.skip("store empty")
    violations = check_per_atom_budget(
        atom_byte_sizes(MAP_PATH.read_text(encoding="utf-8"))
    )
    assert not violations, "per-atom budget:\n  " + "\n  ".join(violations)


def test_per_atom_budget_is_invariant_to_atom_COUNT():
    """R15 both-ways, and the property that distinguishes this control from the
    whole-file ceiling it backs up: 10x the atoms at the same size per atom is NOT a
    violation. A control that fires on honest growth is the one that arrives as a
    publish wedge carrying no information about what to fix."""
    small = {f"A{i}": 1000 for i in range(10)}
    large = {f"A{i}": 1000 for i in range(1000)}
    assert not check_per_atom_budget(small)
    assert not check_per_atom_budget(large)


def test_per_atom_budget_fires_on_accretion_and_on_one_fat_atom():
    """R15: the check must FIRE on each of its own named defects."""
    # (a) broad accretion -- every atom over the mean budget, none over the cap
    assert check_per_atom_budget({f"A{i}": 2000 for i in range(50)})
    # (b) one atom over the per-atom cap, with a mean well inside budget
    fat = {f"A{i}": 100 for i in range(500)}
    fat["FAT"] = MAP_MAX_BYTES_PER_ATOM + 1
    violations = check_per_atom_budget(fat)
    assert violations and "FAT" in violations[0], violations
    # (c) FAIL-OPEN guard: an empty population is a violation, not a pass
    assert check_per_atom_budget({})


def test_atom_byte_sizes_measures_the_real_map():
    """The measurement must be anchored to the live map, not only to synthetic
    fixtures -- a sizer that returned {} would make every budget test above vacuous
    while still passing (the tautology R15 warns about, one layer down)."""
    sizes = atom_byte_sizes(MAP_PATH.read_text(encoding="utf-8"))
    assert len(sizes) > 100, f"only {len(sizes)} atoms parsed out of the live map"
    assert sum(sizes.values()) > 0.9 * MAP_PATH.stat().st_size, (
        "atom blocks account for <90% of the map -- the sizer is missing content, so "
        "the budget it feeds is measuring the wrong thing"
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


def test_count_check_still_fires_when_a_zero_count_hides_real_notes():
    """The half of the zero-count relaxation that must NOT go soft: declaring 0 while
    the store holds notes is the spine under-reporting its own register."""
    assert check_counts_match([{"id": "A1", "simplifications_count": 0}], {"A1": ["real"]})
    assert check_counts_match([{"id": "A1"}], {"A1": ["real"]})  # absent count, notes exist


def test_count_check_permits_zero_or_absent_for_an_empty_register():
    """Both spellings of "nothing to declare" are legal, and neither needs a file."""
    assert not check_counts_match([{"id": "A1", "simplifications_count": 0}], {})
    assert not check_counts_match([{"id": "A1"}], {})


def test_size_check_fires_on_oversize(tmp_path):
    big = tmp_path / "BIG.yaml"
    big.write_text("atom_id: BIG\nsimplifications:\n- " + ("x" * (PER_FILE_CEILING + 10)))
    assert check_file_sizes(tmp_path)
    small = tmp_path / "small_dir"
    small.mkdir()
    (small / "OK.yaml").write_text("atom_id: OK\nsimplifications: []\n")
    assert not check_file_sizes(small)


# --------------------------------------------------------------------------
# THE ROLL (2026-08-11): the archive, and the controls over it
# --------------------------------------------------------------------------
def _fat(marker: str, n: int = 6000) -> str:
    return f"{marker} " + "x" * n


def test_size_check_fires_on_an_oversized_ARCHIVE_chunk(tmp_path):
    """R15, and the specific fail-open the archive introduces. `glob("*.yaml")` does
    not descend into a subdirectory, so a check left unwidened would have gone silent
    on exactly the files the roll creates -- passing loudest about a population it can
    no longer see."""
    sd = tmp_path / "simplifications"
    (sd / store.ARCHIVE_DIRNAME).mkdir(parents=True)
    (sd / "OK.yaml").write_text("atom_id: OK\nsimplifications: []\n")
    assert not check_file_sizes(sd)
    (sd / store.ARCHIVE_DIRNAME / "OK.001.yaml").write_text(
        "atom_id: OK\nchunk: 1\nsimplifications:\n- " + "x" * (PER_FILE_CEILING + 10)
    )
    violations = check_file_sizes(sd)
    assert violations and "OK.001.yaml" in violations[0], violations


def test_duplicate_check_fires_on_an_entry_in_both_places(tmp_path):
    """R15: the roll's chosen failure direction has to be detectable, or the trade
    (duplicate rather than lose) is a claim nobody can check."""
    sd = tmp_path / "simplifications"
    (sd / store.ARCHIVE_DIRNAME).mkdir(parents=True)
    (sd / "A1.yaml").write_text("atom_id: A1\nsimplifications:\n- shared\n- live-only\n")
    (sd / store.ARCHIVE_DIRNAME / "A1.001.yaml").write_text(
        "atom_id: A1\nchunk: 1\nsimplifications:\n- older\n"
    )
    assert not check_no_duplicate_entries(sd)
    (sd / store.ARCHIVE_DIRNAME / "A1.001.yaml").write_text(
        "atom_id: A1\nchunk: 1\nsimplifications:\n- older\n- shared\n"
    )
    violations = check_no_duplicate_entries(sd)
    assert violations and "A1" in violations[0], violations


def test_duplicate_check_fires_on_a_duplicated_RECORD_entry(tmp_path):
    """The record tenant is rolled too, so it needs the same guard -- a check that
    covered only `simplifications` would be blind in the half H41 proved is the
    faster-growing flow."""
    sd = tmp_path / "simplifications"
    (sd / store.ARCHIVE_DIRNAME).mkdir(parents=True)
    (sd / "A1.yaml").write_text(
        "atom_id: A1\nmap_records:\n  evidence:\n  - shared\n"
    )
    (sd / store.ARCHIVE_DIRNAME / "A1.001.yaml").write_text(
        "atom_id: A1\nchunk: 1\nmap_records:\n  evidence:\n  - shared\n"
    )
    violations = check_no_duplicate_entries(sd)
    assert violations and "evidence" in violations[0], violations


def test_orphan_check_sees_an_atom_that_exists_ONLY_in_the_archive(tmp_path):
    """A dead atom must not be able to hide in the archive. `load_all` unions the
    archive-bearing ids in for exactly this: the orphan check reads that population,
    so leaving the archive out of it would have made the archive a place where a
    store file with no atom is no longer a defect."""
    sd = tmp_path / "simplifications"
    (sd / store.ARCHIVE_DIRNAME).mkdir(parents=True)
    (sd / store.ARCHIVE_DIRNAME / "GHOST.001.yaml").write_text(
        "atom_id: GHOST\nchunk: 1\nsimplifications:\n- an entry whose atom died\n"
    )
    loaded = store.load_all(sd)
    assert loaded == {"GHOST": ["an entry whose atom died"]}, loaded
    assert check_no_orphans({"A1"}, loaded)
    assert not check_no_orphans({"A1", "GHOST"}, loaded)


def test_the_roll_preserves_the_register_verbatim_and_bounds_every_file(tmp_path):
    """The property the whole mechanism rests on: appending past the watermark must
    change WHERE entries live and nothing else. Same list, same order, same count,
    every file bounded -- so a roll is invisible to the map's declared count and to
    every consumer that reads through `for_atom`."""
    sd = tmp_path / "simplifications"
    written = [_fat(f"entry-{i}") for i in range(40)]
    for note in written:
        store.append_for_atom("R1", [note], sd)

    live = (sd / "R1.yaml").stat().st_size
    assert live <= store.ROLL_WATERMARK, f"live file not drained: {live} B"
    assert store.archive_chunks("R1", sd), "nothing was archived"
    assert store.for_atom("R1", sd) == written, "the register did not survive the roll"
    assert store.count_for_atom("R1", sd) == 40
    assert store.load_all(sd) == {"R1": written}
    assert not check_file_sizes(sd)
    assert not check_no_duplicate_entries(sd)


def test_the_roll_drains_the_RECORD_tenant_too(tmp_path):
    """H41's drain bounded one list and left its siblings flowing, and the wedge came
    back a level down inside `expert_hour_findings`. The roll takes from whichever
    unbounded list is largest, so a store file cannot be pinned at its cap by a tenant
    the drain does not know about."""
    sd = tmp_path / "simplifications"
    findings = [_fat(f"hour-{i}") for i in range(30)]
    for f in findings:
        store.append_to_record_for_atom("R2", "expert_hour_findings", [f], sd)

    assert (sd / "R2.yaml").stat().st_size <= store.ROLL_WATERMARK
    assert store.archived_records_for_atom("R2", sd).get("expert_hour_findings")
    assert store.records_for_atom("R2", sd)["expert_hour_findings"] == findings
    assert not check_file_sizes(sd)
    assert not check_no_duplicate_entries(sd)


def test_a_roll_never_empties_a_tenant_and_prose_records_are_never_rolled(tmp_path):
    """Two bounds on what the roll may take. It always leaves one entry live (so the
    live file keeps declaring its own shape), and it never touches a prose record --
    `exit_evidence` is a string on the live map, and chopping a string into archived
    pieces is the coercion the record tenant exists to refuse."""
    sd = tmp_path / "simplifications"
    store.set_record_for_atom("R3", "exit_evidence", _fat("prose", 40000), sd)
    for i in range(10):
        store.append_for_atom("R3", [_fat(f"note-{i}")], sd)

    assert store.live_notes_for_atom("R3", sd), "the roll emptied the live tenant"
    assert store.records_for_atom("R3", sd)["exit_evidence"].startswith("prose ")
    assert not store.archived_records_for_atom("R3", sd).get("exit_evidence")
    assert store.for_atom("R3", sd) == [_fat(f"note-{i}") for i in range(10)]


def test_a_second_roll_appends_a_new_chunk_rather_than_rewriting_one(tmp_path):
    """Chunks are written ONCE. A roll that rewrote an existing chunk would be an
    edit to honest history, and would reopen the bound the packing closes."""
    sd = tmp_path / "simplifications"
    for i in range(40):
        store.append_for_atom("R4", [_fat(f"a-{i}")], sd)
    first = {p.name: p.read_bytes() for p in store.archive_chunks("R4", sd)}
    assert first
    for i in range(40, 80):
        store.append_for_atom("R4", [_fat(f"a-{i}")], sd)
    after = {p.name: p.read_bytes() for p in store.archive_chunks("R4", sd)}
    assert len(after) > len(first), "the second roll produced no new chunk"
    for name, body in first.items():
        assert after[name] == body, f"{name} was rewritten by a later roll"
    assert store.for_atom("R4", sd) == [_fat(f"a-{i}") for i in range(80)]


def test_an_append_does_not_re_inline_the_archive(tmp_path):
    """The writer reads the LIVE tenant, never the concatenated view. Reading
    `for_atom` there would pull every archived entry back into the live file on the
    next append -- the roll would undo itself and duplicate the record into the
    chunks, which is the failure the duplicate check exists to catch."""
    sd = tmp_path / "simplifications"
    for i in range(40):
        store.append_for_atom("R5", [_fat(f"b-{i}")], sd)
    archived = store.archived_notes_for_atom("R5", sd)
    assert archived
    live = store.live_notes_for_atom("R5", sd)
    assert not (set(archived) & set(live))
    assert store.append_for_atom("R5", ["one more"], sd) == 41
    assert store.for_atom("R5", sd)[-1] == "one more"
    assert not check_no_duplicate_entries(sd)


def test_a_single_entry_larger_than_the_bound_still_raises(tmp_path):
    """The roll must not become a way to absorb an entry that cannot be stored. One
    note bigger than the whole per-file bound is a defect to surface; a mechanism that
    quietly swallowed it would make the bound unfalsifiable."""
    sd = tmp_path / "simplifications"
    store.append_for_atom("R6", ["small"], sd)
    with pytest.raises(ValueError):
        store.append_for_atom("R6", ["x" * (PER_FILE_CEILING + 10)], sd)
    assert store.for_atom("R6", sd) == ["small"], "a failed write damaged the file"


def test_a_whole_field_record_write_over_an_archive_is_refused(tmp_path):
    """`set_record_for_atom` is the migration's one-shot writer. Over an atom with
    archived entries it would duplicate them silently, so it refuses."""
    sd = tmp_path / "simplifications"
    for i in range(30):
        store.append_to_record_for_atom("R7", "evidence", [_fat(f"e-{i}")], sd)
    assert store.archived_records_for_atom("R7", sd).get("evidence")
    with pytest.raises(ValueError, match="archived entries"):
        store.set_record_for_atom("R7", "evidence", ["replacement"], sd)


def test_the_watermark_leaves_real_headroom_below_the_cap():
    """The watermark is the whole point of the repair: a roll target equal to the cap
    would leave a file rolling on every write, and one just under it would re-wedge
    within an entry. This store's entries average ~5.4 KB, so the gap must hold
    several of them."""
    assert store.ROLL_WATERMARK < store.MAX_FILE_BYTES
    assert store.MAX_FILE_BYTES - store.ROLL_WATERMARK >= 5 * 5400


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
