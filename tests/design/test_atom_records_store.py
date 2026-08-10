"""Contract for the rehomed RECORD fields (atom H41).

The THIRD tenant of the per-atom record store. `evidence` and `exit_evidence` were
MOVED out of docs/design/maturity_map.yaml into the existing sibling store,
docs/design/simplifications/<atom_id>.yaml, under a `map_records:` mapping. The map
keeps one `records_rehomed: [<field>, ...]` line per atom naming which exist.

WHY THIS EXISTS -- AND WHY IT IS NOT A REPEAT OF H32. H32 rehomed the note class and
took the map 464,110 -> 393,692 bytes. Twenty-four hours later it was 430,962 and
wedging publishing again, because H32 drained the field that was largest AT THAT
MOMENT and left the refill running. The originating finding
(WORKER_FINDING_THE_MAP_RATCHET_REPAIR_DID_NOT_HOLD) named the generalisable shape:
*a ratchet with no ongoing drain is a one-time cleanup, not a control*, and put a
condition on any second repair -- it must leave a drain that runs at MINT RATE, or it
is the same finding again in a fortnight and the third one is an R3 redesign.

So H41 was chosen by measuring the FLOW, not the stock. Over the 24h to 2026-08-10,
git-diffed field by field on the committed map:

    evidence        66,699 -> 113,552   +46,853
    exit_evidence        0 ->  20,652   +20,652
                                        (whole map: +67,096 net)

The two record fields ARE the refill; every other field's growth is atom-COUNT driven
(229 -> 260 atoms). Moving them took the map 430,962 -> 300,565 AND cut the growth
rate, because the pipe they grew through -- `tools/merge_atom_status.py`'s
`append_evidence` fold -- now appends to a per-atom store file instead of to the
spine. The drain is that rewiring, not this migration.

The invariants guarded here:
  * NO INLINE RECORDS -- as a CLASS (R10), not an instance list: `evidence` plus any
    `*_evidence` field appearing inline in the map fails, so a future `frame_evidence`
    is caught by construction. Two sources of truth for one atom's record are forbidden.
  * DECLARATION MATCHES STORE, both directions -- a map atom's `records_rehomed` names
    exactly the fields its store file holds. An undeclared stored record is invisible
    to the spine; a declared-but-absent one is a lost artefact trail.
  * RECORDS ARE NON-EMPTY, IN THEIR ORIGINAL SHAPE -- `evidence` is a list on all 259
    atoms that carry it and `exit_evidence` is prose on all 3; a migration that
    coerced either would have silently rewritten the record it was moving.
  * NO TENANT DROPS ANOTHER -- with three tenants in one file, a writer that rebuilds
    the file while knowing about only one silently deletes the other two. That is the
    live hazard of the single-file design, so it is proven, not asserted.
  * THE FOLD NO LONGER GROWS THE MAP -- `_APPENDABLE` must stay empty. This is the
    drain itself, and the one invariant whose failure would reproduce the whole
    incident silently.

Each invariant carries an R15 mutation test proving the check FIRES on its own named
defect (a control that cannot fail is worse than none).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools import merge_atom_status
from tools import simplifications_store as store

PROJECT = Path(__file__).resolve().parent.parent.parent
MAP_PATH = PROJECT / "docs" / "design" / "maturity_map.yaml"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"

DECL = store.RECORDS_DECLARATION_FIELD


def _load_atoms(path: Path = MAP_PATH) -> list:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# pure checks (feedable synthetic inputs for mutation testing)
# --------------------------------------------------------------------------
def check_no_inline_records(atoms: list) -> list[str]:
    """No map atom may carry a record-class field inline. CLASS-level: membership is
    `store.is_record_field` (`evidence` or any `*_evidence`), so a newly-invented
    record field is caught without editing this test."""
    violations = []
    for a in atoms:
        if not isinstance(a, dict):
            continue
        for k in sorted(a):
            if store.is_record_field(k):
                violations.append(
                    f"{a.get('id')}: `{k}` is inline in the map -- the artefact trail "
                    "lives in the store (two sources of truth forbidden)"
                )
    return violations


def check_declarations_match(atoms: list, records_store: dict[str, dict]) -> list[str]:
    """Each atom's `records_rehomed` must name exactly the fields its store file
    holds, in BOTH directions: a declared field with no stored record is a lost
    artefact trail, and a stored record with no declaration is invisible to the
    spine."""
    violations = []
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
    for aid, atom in by_id.items():
        declared = atom.get(DECL)
        stored = sorted(records_store.get(aid, {}))
        if declared is None:
            if stored:
                violations.append(
                    f"{aid}: store holds records {stored} but the map declares no {DECL}"
                )
            continue
        if not isinstance(declared, list):
            violations.append(f"{aid}: {DECL} must be a list, got {type(declared).__name__}")
            continue
        if sorted(declared) != stored:
            violations.append(
                f"{aid}: map {DECL}={sorted(declared)} != store fields {stored}"
            )
    for aid in records_store:
        if aid not in by_id:
            violations.append(f"{aid}: store holds records but no such atom in the map")
    return violations


def check_records_are_nonempty(records_store: dict[str, dict]) -> list[str]:
    """A moved key whose content was dropped is the migration's worst failure mode:
    the spine still says the record exists and the artefact trail is gone.

    Shape is checked too, and deliberately NOT normalised: `evidence` is a list,
    `exit_evidence` is prose, and the tenant carries each verbatim. A check that
    accepted either shape for either field would pass over exactly the coercion bug
    (`list("some prose")` -> a list of characters) that a shape-tolerant migration is
    most likely to introduce."""
    violations = []
    for aid, records in sorted(records_store.items()):
        for field, value in sorted(records.items()):
            if not store.is_record_field(field):
                violations.append(f"{aid}.{field}: not a record-class field")
            if not isinstance(value, (list, str)):
                violations.append(
                    f"{aid}.{field}: {type(value).__name__}, expected a list or a string"
                )
            elif not value or (isinstance(value, str) and not value.strip()):
                violations.append(f"{aid}.{field}: empty record ({value!r})")
            elif isinstance(value, list) and any(
                not isinstance(e, str) or not e.strip() for e in value
            ):
                violations.append(f"{aid}.{field}: contains an empty/non-string entry")
    return violations


# --------------------------------------------------------------------------
# tests over the LIVE map + store
# --------------------------------------------------------------------------
def _live_records() -> dict[str, dict]:
    return store.records_load_all(STORE_DIR)


def test_the_record_tenant_is_populated_precondition():
    """VACUITY GUARD. Every test below is conditioned on the tenant existing, so an
    empty tenant would turn the whole file green while proving nothing -- the
    fail-open shape R15 names. This one test is unconditional."""
    live = _live_records()
    assert len(live) > 100, (
        f"record tenant holds {len(live)} atoms -- the H41 rehome moved 259. An empty "
        "or near-empty tenant makes every other test in this file vacuous."
    )


def test_no_record_field_is_inline_in_the_map():
    violations = check_no_inline_records(_load_atoms())
    assert not violations, "inline record fields:\n  " + "\n  ".join(violations)


def test_declarations_match_the_store_both_directions():
    violations = check_declarations_match(_load_atoms(), _live_records())
    assert not violations, "declaration/store mismatches:\n  " + "\n  ".join(violations)


def test_stored_records_are_non_empty_and_keep_their_shape():
    violations = check_records_are_nonempty(_live_records())
    assert not violations, "bad stored records:\n  " + "\n  ".join(violations)


def test_evidence_is_a_list_and_exit_evidence_is_prose_on_the_live_store():
    """The measured shapes the migration was built around, asserted against the live
    store so a future writer that coerces one into the other is caught."""
    live = _live_records()
    ev = [v for r in live.values() if (v := r.get("evidence")) is not None]
    xe = [v for r in live.values() if (v := r.get("exit_evidence")) is not None]
    assert len(ev) > 100 and all(isinstance(v, list) for v in ev)
    assert xe and all(isinstance(v, str) for v in xe)


def test_hydrate_restores_the_pre_rehome_atom_shape():
    """The compatibility path every reader of a rehomed field goes through."""
    live = _live_records()
    aid, records = next(iter(sorted(live.items())))
    atom = {a["id"]: a for a in _load_atoms() if isinstance(a, dict)}[aid]
    hydrated = store.hydrate(atom, STORE_DIR)
    for field, value in records.items():
        assert hydrated[field] == value, f"{aid}.{field} not restored by hydrate"
    assert hydrated["id"] == aid


def test_the_evidence_fold_no_longer_writes_to_the_map():
    """THE DRAIN ITSELF. `_APPENDABLE` is the set of fields an inbox fold appends
    INTO THE MAP TEXT; `append_evidence` living there is what grew the spine by
    ~47KB/day. If a later change puts a register field back in here, the map starts
    refilling again and the only symptom is another publish wedge a day or two
    later -- so it is asserted, not left to review."""
    assert merge_atom_status._APPENDABLE == {}, (
        "a field was added back to the map-text append fold: "
        f"{merge_atom_status._APPENDABLE}. Append-only registers belong in the store "
        "(store.append_for_atom / store.append_to_record_for_atom)."
    )


# --------------------------------------------------------------------------
# R15 mutation tests: each check must FIRE on its own named defect
# --------------------------------------------------------------------------
def test_inline_check_fires_on_an_inline_record():
    assert check_no_inline_records([{"id": "A1", "evidence": ["x"]}])
    assert check_no_inline_records([{"id": "A1", "exit_evidence": "prose"}])
    # the CLASS half: a field nobody has invented yet
    assert check_no_inline_records([{"id": "A1", "frame_evidence": ["x"]}])
    assert not check_no_inline_records([{"id": "A1", DECL: ["evidence"]}])


def test_the_record_class_covers_the_APPEND_PER_REVIEW_findings_shape():
    """The second unbounded flow (2026-08-10, the fourteenth publish wedge). `expert_hour`'s
    `findings:` member is the same append-forever narrative list as `evidence`, one level down
    inside a structured mapping, so H41's top-level drain never saw it -- 53,526 B across 176
    atoms, and the seventh Hour on one atom crossed the per-atom cap and wedged publishing.

    `*_findings` is a CLASS, not the one instance: a future `coldwalk_findings` (the same shape
    under a different review name) is admissible by construction, and would fail the inline check
    without this test being edited."""
    assert store.is_record_field("expert_hour_findings")
    assert store.is_record_field("coldwalk_findings")
    assert check_no_inline_records([{"id": "A1", "expert_hour_findings": ["an Hour"]}])
    # ...and the class has not swallowed the structured map fields it must never claim
    assert not store.is_record_field("expert_hour")
    assert not store.is_record_field("simplifications_count")
    assert not store.is_record_field("findings")


def test_declaration_check_fires_in_both_directions():
    atoms = [{"id": "A1", DECL: ["evidence"]}]
    # declared but not stored -- a lost artefact trail
    assert check_declarations_match(atoms, {})
    # stored but not declared -- invisible to the spine
    assert check_declarations_match([{"id": "A1"}], {"A1": {"evidence": ["x"]}})
    # orphan: stored against an atom that no longer exists
    assert check_declarations_match(atoms, {"A1": {"evidence": ["x"]}, "GONE": {"evidence": ["y"]}})
    # matching, both directions
    assert not check_declarations_match(atoms, {"A1": {"evidence": ["x"]}})


def test_nonempty_check_fires_on_a_dropped_or_coerced_record():
    assert check_records_are_nonempty({"A1": {"evidence": []}})
    assert check_records_are_nonempty({"A1": {"exit_evidence": "   "}})
    assert check_records_are_nonempty({"A1": {"evidence": ["ok", ""]}})
    assert check_records_are_nonempty({"A1": {"evidence": {"not": "a list"}}})
    assert check_records_are_nonempty({"A1": {"not_a_record_field": ["x"]}})
    assert not check_records_are_nonempty(
        {"A1": {"evidence": ["docs/design/X.md"], "exit_evidence": "prose"}}
    )


def test_no_tenant_drops_another(tmp_path):
    """THE LIVE HAZARD of three tenants in one file, proven rather than asserted.
    Write each tenant in turn through its own narrow writer and check the other two
    survive -- the failure this replaces is silent (the record simply vanishes)."""
    store.append_for_atom("A1", ["note one"], tmp_path)
    store.set_note_for_atom("A1", "build_note", "built it", tmp_path)
    store.set_record_for_atom("A1", "evidence", ["docs/design/X.md"], tmp_path)

    assert store.for_atom("A1", tmp_path) == ["note one"]
    assert store.notes_for_atom("A1", tmp_path) == {"build_note": "built it"}
    assert store.records_for_atom("A1", tmp_path) == {"evidence": ["docs/design/X.md"]}

    # a second write through EACH writer must still preserve the other two
    store.append_for_atom("A1", ["note two"], tmp_path)
    store.append_to_record_for_atom("A1", "evidence", ["docs/design/Y.md"], tmp_path)
    store.set_note_for_atom("A1", "harden_note", "hardened", tmp_path)

    assert store.for_atom("A1", tmp_path) == ["note one", "note two"]
    assert store.records_for_atom("A1", tmp_path) == {
        "evidence": ["docs/design/X.md", "docs/design/Y.md"]
    }
    assert store.notes_for_atom("A1", tmp_path) == {
        "build_note": "built it", "harden_note": "hardened"
    }


def test_record_writers_reject_out_of_class_fields_and_bad_shapes(tmp_path):
    with pytest.raises(ValueError):
        store.set_record_for_atom("A1", "level_current", [3], tmp_path)
    with pytest.raises(ValueError):
        store.set_record_for_atom("A1", "evidence", 3, tmp_path)
    with pytest.raises(ValueError):
        store.append_to_record_for_atom("A1", "evidence", "not a list", tmp_path)
    # appending to PROSE is refused rather than silently turning it into a list
    store.set_record_for_atom("A1", "exit_evidence", "prose", tmp_path)
    with pytest.raises(ValueError):
        store.append_to_record_for_atom("A1", "exit_evidence", ["x"], tmp_path)


def test_write_tenants_rejects_an_unknown_tenant(tmp_path):
    """The sole write path must not silently swallow a typo'd tenant name -- a
    quietly-ignored `map_record=` would write nothing and report success."""
    with pytest.raises(ValueError):
        store._write_tenants("A1", tmp_path, map_record={"evidence": ["x"]})
