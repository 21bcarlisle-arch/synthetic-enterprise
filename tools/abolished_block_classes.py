#!/usr/bin/env python3
"""The registry of ABOLISHED block classes -- and the class guard that stops the
project publishing an abolished permission regime as if it were live.

PURPOSE (OPERATIONAL_LAYER_DESIGN "state purpose/guarantees/why FIRST").
`docs/design/maturity_map.yaml`'s `simplifications` lists are an append-only
honesty register. `tools/generate_simplified_data.py` republishes them verbatim
to `site/data/simplified.json`, which `/proof/` renders as its
"Appendix -- the simplifications register" (SITE_CONSTITUTION rule 5: "the site
is a rendering, never an author"). That verbatim republication is correct, and
it is also how a *dead* rule stays on a live public surface: 73 notes on the
live-served register still say levels are HELD behind `director_level_up`, an
act ABOLISHED 2026-07-29 and swept 2026-08-03. A reader of the honesty register
concludes the company still asks permission to move a level. It does not.

GUARANTEES.
  1. The note text is never rewritten. History stays true; a note that said
     "held behind director_build_open" on 2026-07-27 *was* true on 2026-07-27.
  2. Supersession is DERIVED, never authored: `annotate_notes()` attaches
     structured `superseded_blocks` metadata alongside the untouched string, so
     the renderer can mark it without the generator inventing prose.
  3. It is a CLASS mechanism, not an instance fix (R10). Adding the next
     abolished class to `ABOLISHED_BLOCK_CLASSES` annotates every note that
     mentions it, everywhere, with no note-by-note edit.
  4. `live_blocked_on_violations()` is the harder invariant: an abolished class
     may never appear as a LIVE `blocked_on` on any atom. A note is history; a
     `blocked_on` is a claim about now.

WHY THIS SHAPE AND NOT PROSE (MAKE_IT_STICK). The alternative on the table was
to hand-correct ~25 stale notes. That is the exhortation failure mode: it fixes
the instances, leaves the class, and the register re-grows the moment the next
permission act is abolished. Every rule that decayed in this project was prose;
every rule that held was a mechanism.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"


@dataclass(frozen=True)
class AbolishedClass:
    """One block class that no longer exists, and what replaced it."""

    name: str
    abolished_on: str
    ruling: str
    replaced_by: str
    # Extra spellings of the SAME class seen in the register (case-insensitive).
    aliases: tuple[str, ...] = ()


# The registry. Each entry is evidenced by CLAUDE.md's own rip-out record
# ("The deleted machinery ... must stay deleted") or by the R16 rescope.
ABOLISHED_BLOCK_CLASSES: dict[str, AbolishedClass] = {
    c.name: c
    for c in (
        AbolishedClass(
            name="director_level_up",
            abolished_on="2026-07-29",
            ruling="DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY_2026-07-29.md"
            " (R16 rescoped 2026-08-03)",
            replaced_by="background.gate_authorization.record_level_up_self_certified"
            " -- R16 requires the move to be RECORDED, never AUTHORISED. Levels are"
            " self-certified with evidence.",
        ),
        AbolishedClass(
            name="director_build_open",
            abolished_on="2026-07-29",
            ruling="DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY_2026-07-29.md",
            replaced_by="nothing -- an atom whose loop_stage is `build` is drawn,"
            " full stop. There is no such thing as a BUILD being opened.",
            aliases=("build_open",),
        ),
        AbolishedClass(
            name="director_h_lane_open",
            abolished_on="2026-07-29",
            ruling="DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY_2026-07-29.md",
            replaced_by="nothing -- a per-lane open is a BUILD_OPEN by another"
            " name; lanes are not opened, they are drawn (THREE_LANES).",
        ),
        AbolishedClass(
            name="front_open",
            abolished_on="2026-08-03",
            ruling="CLAUDE.md PROPOSE, RECORD, ACT -- fronts.yaml and"
            " fronts_reconciler.py are deleted and must stay deleted",
            replaced_by="nothing -- there is no such thing as a front being open.",
        ),
        AbolishedClass(
            name="gate_clear",
            abolished_on="2026-08-03",
            ruling="CLAUDE.md PROPOSE, RECORD, ACT -- the"
            " BUILD_OPEN/FRONT_OPEN/GATE_CLEAR family is deleted",
            replaced_by="nothing -- there is no such thing as a gate being cleared.",
        ),
        AbolishedClass(
            name="inbound_ratification",
            abolished_on="2026-08-03",
            ruling="CLAUDE.md PROPOSE, RECORD, ACT --"
            " background/inbound_ratification.py is deleted and guarded by"
            " tests/background/test_gate_authorization.py::test_the_permission_surface_is_gone",
            replaced_by="nothing -- inbound steers are acted on and recorded, never"
            " held pending ratification.",
        ),
        AbolishedClass(
            name="director_authority_channels",
            abolished_on="2026-08-03",
            ruling="CLAUDE.md PROPOSE, RECORD, ACT -- the module is deleted",
            replaced_by="NTFY IS THE DIRECTOR -- anything on his topic is him. Do not"
            " invent authority checks.",
        ),
        AbolishedClass(
            name="ratify_routine_level",
            abolished_on="2026-08-03",
            ruling="CLAUDE.md 'Twin is a voice, not a hand' -- the twin's"
            " ratify_routine_level is deleted",
            replaced_by="nothing -- the twin answers; it has never had the power to"
            " say yes.",
        ),
    )
}

# The four RESERVED real-world classes are NOT abolished and must never be
# registered here. `background/one_way_door.py` is their sole enumeration; this
# module is deliberately about *simulation-internal permission* acts only.
NEVER_ABOLISHED = (
    "real money",
    "real people",
    "public claim",
    "safety",
)


def _pattern_for(cls: AbolishedClass) -> re.Pattern:
    """Match the class token and its level-suffixed spellings, and nothing else.

    Deliberately NOT a bare substring/prefix match: the register also contains
    `director_twin_log`, `director_input_log`, `director_window_delta_view` and
    `director_systemd_deploy` (a LIVE block), none of which is an abolished
    class. A prefix match would sweep them in -- a false positive here would
    annotate a live block as dead, which is worse than the defect being fixed.
    """
    names = "|".join(re.escape(n) for n in (cls.name, *cls.aliases))
    # token, optionally suffixed with a level marker (`_L2`, `_L3`), then a
    # boundary that is not a word character -- so `director_level_up_L3` matches
    # but `director_level_upgrade` would not.
    return re.compile(rf"(?<![A-Za-z0-9_])({names})(_L[0-9])?(?![A-Za-z0-9_])",
                      re.IGNORECASE)


def find_abolished_references(text: str) -> list[AbolishedClass]:
    """Every abolished class this text refers to, in registry order, deduped."""
    if not text:
        return []
    found: list[AbolishedClass] = []
    for cls in ABOLISHED_BLOCK_CLASSES.values():
        if _pattern_for(cls).search(str(text)):
            found.append(cls)
    return found


def supersession_for(text: str) -> list[dict]:
    """The DERIVED supersession metadata for one register note.

    Returns [] for a note that mentions no abolished class -- so the annotation
    is present exactly when it is earned, never a blanket stamp.
    """
    return [asdict(c) for c in find_abolished_references(text)]


def annotate_notes(notes: list) -> tuple[list[str], list[dict]]:
    """Split a register entry's notes into (untouched text, derived markers).

    The text list is returned BYTE-IDENTICAL to the input (rule 5: the site is a
    rendering, never an author). The markers are a parallel index keyed by note
    position, so a renderer can mark the note without the string being edited.
    """
    out_notes = [str(n) for n in notes]
    markers = []
    for i, note in enumerate(out_notes):
        sup = supersession_for(note)
        if sup:
            markers.append({"note_index": i, "superseded_blocks": sup})
    return out_notes, markers


def _load_atoms(path: Path | None = None):
    """Every atom the register is published FROM -- read through the same loader
    the publisher uses.

    THE SUBJECT HAS TO MATCH THE PUBLISHER'S (2026-08-26). This read the map YAML
    directly with `yaml.safe_load` while `generate_simplified_data.py` reads it
    with `map_store.load_atoms`, which also resolves the sharded/closed store.
    The two therefore scanned different books -- 74 atoms here against the
    publisher's 298 -- so this module measured the dead-rule exposure of a
    quarter of the register and reported it as the whole: 29 notes against the
    81 actually published. Both numbers were computed correctly; they were
    answers to different questions, and only one of them was the question the
    docstring asks.

    That is why the count is compared against the PUBLISHED artefact in
    `test_real_register_exposure_is_measured_and_fully_marked` rather than
    against itself -- a self-consistent exposure figure is exactly what a
    narrowed subject produces.

    FAIL-CLOSED (R15) is unchanged: an unavailable or unparseable source returns
    None, and callers must treat that as "cannot verify", never as an empty pass.
    """
    src = path or MATURITY_MAP_YAML
    if not src.is_file():
        return None
    try:
        from tools import maturity_map_store as map_store

        data = map_store.load_atoms(src)
    except Exception:
        return None
    return data if isinstance(data, list) else None


def live_blocked_on_violations(path: Path | None = None) -> list[dict] | None:
    """Atoms whose LIVE `blocked_on` names an abolished class.

    A note is history and may mention a dead act. A `blocked_on` is a claim
    about NOW, so it may never name one. Returns None when the map cannot be
    read at all -- an unavailable check is a FAILED check, not an empty pass.
    """
    atoms = _load_atoms(path)
    if atoms is None:
        return None
    violations = []
    for atom in atoms:
        if not isinstance(atom, dict):
            continue
        blocked = atom.get("blocked_on")
        if not blocked:
            continue
        refs = find_abolished_references(str(blocked))
        if refs:
            violations.append({
                "atom_id": atom.get("id"),
                "blocked_on": blocked,
                "abolished": [c.name for c in refs],
                "replaced_by": [c.replaced_by for c in refs],
            })
    return violations


def register_exposure(path: Path | None = None) -> dict | None:
    """How much of the published honesty register refers to a dead act.

    Reported rather than silently fixed -- the number is the point: it is the
    measure of how long an abolished rule stayed on a live public surface.
    """
    atoms = _load_atoms(path)
    if atoms is None:
        return None
    # simplifications moved to the sibling store (retro FM-1); read the notes
    # through the loader, keyed to the store beside the map being scanned.
    from tools import simplifications_store as store

    src = path or MATURITY_MAP_YAML
    store_dir = Path(src).parent / "simplifications"
    by_class: dict[str, int] = {}
    notes_touched = 0
    atoms_touched = 0
    for atom in atoms:
        if not isinstance(atom, dict):
            continue
        hit_this_atom = False
        for note in store.for_atom(atom.get("id"), store_dir):
            refs = find_abolished_references(str(note))
            if refs:
                notes_touched += 1
                hit_this_atom = True
                for c in refs:
                    by_class[c.name] = by_class.get(c.name, 0) + 1
        if hit_this_atom:
            atoms_touched += 1
    return {
        "notes_referring_to_an_abolished_class": notes_touched,
        "atoms_affected": atoms_touched,
        "by_class": dict(sorted(by_class.items(), key=lambda kv: -kv[1])),
    }


if __name__ == "__main__":
    import json

    print("live blocked_on violations:")
    print(json.dumps(live_blocked_on_violations(), indent=2))
    print("\npublished register exposure:")
    print(json.dumps(register_exposure(), indent=2))
