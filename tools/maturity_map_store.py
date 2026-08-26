#!/usr/bin/env python3
"""The canonical loader for the maturity map, now that the map is two files.

WHY THIS EXISTS. `docs/design/maturity_map.yaml` had grown to 298 atoms and 5,420 lines,
of which 224 atoms and 3,947 lines were at-or-above their own target -- work that is
finished. Every draw, every survey and every reader was walking the whole of that to find
the 74 atoms that still carry a gap. The director named it twice on 2026-08-24: *"read those
117, delete what shouldn't exist, close what's finished... I'd rather the map were half the
size and true."*

WHAT THE SPLIT IS. `maturity_map.yaml` holds the atoms that still have somewhere to go.
`maturity_map_closed.yaml`, its sibling, holds the ones that do not. The two files together
are the map; NEITHER is the map on its own. Both are plain top-level YAML lists of atom
records in exactly the hand-authored form they had before the split, byte for byte, so
`tools/merge_atom_status.py`'s in-place text fold and every regex reader still work.

WHAT THIS MODULE GUARANTEES, and it is the whole point of routing readers through it: a
reader that asks for the map gets ALL the atoms. The split is a fact about storage, not
about the population. `site/moap_coherence.py` derives every front-door node's
Live/Building/Planned stage from atom levels; a reader that silently received only the live
file would compute "no atoms at target" for finished nodes and flip Live nodes to Planned on
the public site. That is the named hazard, and it is a FAIL-OPEN of exactly the R15 shape --
a missing file producing a smaller, plausible, wrong answer rather than a refusal.

SO THE CANONICAL PATH IS FAIL-CLOSED. If the closed sibling is missing, unreadable, empty or
malformed, every function here RAISES `MapStoreError`. It never falls back to live-only,
because live-only is the wrong answer that looks right. R15-proven in
`tests/tools/test_maturity_map_store.py` by mutating the store four ways (absent, empty,
malformed, not-a-list) and asserting each one raises rather than returns.

THE ONE DELIBERATE SEAM. Dozens of existing tests build a fixture map at a temp path and pass
it in. For a path that is NOT the canonical `docs/design/maturity_map.yaml`, a missing sibling
resolves to live-only, because an injected single-file fixture has no closed half and never
did. That seam is narrow by construction (it keys on the resolved canonical path, not on a
flag a caller can set) and is itself tested both ways: the canonical path raises on a missing
sibling, a fixture path does not. A NON-canonical path whose sibling EXISTS but is malformed
still raises -- the tolerance is for absence at a fixture path, never for corruption anywhere.

USAGE:
    from tools import maturity_map_store as map_store
    atoms = map_store.load_atoms()                 # every atom, live + closed
    atoms = map_store.load_atoms(SOME_MAP_PATH)    # same, sibling derived from that path
    text  = map_store.map_text()                   # the concatenated YAML text, for the
                                                   # regex/text readers that never used yaml
    live  = map_store.load_live_atoms()            # ONLY the atoms that still carry work
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MAP_REL = "docs/design/maturity_map.yaml"
CLOSED_REL = "docs/design/maturity_map_closed.yaml"
LIVE_PATH = PROJECT / MAP_REL
CLOSED_PATH = PROJECT / CLOSED_REL

# Both halves, repo-relative, for callers that read the map out of git rather than the
# worktree (the level gate reads the staged/HEAD text, not the file on disk).
MAP_PARTS_REL = (MAP_REL, CLOSED_REL)


class MapStoreError(RuntimeError):
    """The map could not be read WHOLE. Never raised for an empty live half -- a map with
    nothing left to build is a legitimate state -- only for a closed half that should be
    there and is not, or is there and is not a list of atoms."""


def closed_path_for(live_path: Path | str) -> Path:
    """The closed half that belongs to `live_path`: its sibling `maturity_map_closed.yaml`.
    Derived from the path rather than configured, so a fixture map and its fixture closed
    half stay together with no wiring."""
    return Path(live_path).resolve().parent / "maturity_map_closed.yaml"


def _is_canonical(live_path: Path | str) -> bool:
    try:
        return Path(live_path).resolve() == LIVE_PATH.resolve()
    except OSError:  # pragma: no cover -- a path that cannot even be resolved is not ours
        return False


# Validation cache. The closed half is ~300KB and `map_text` is called per publish cycle by
# readers that deliberately line-scan rather than YAML-load it for cost (tree_divergence says so
# in its own docstring). Validating it means parsing it, so the parse is done ONCE per (path,
# mtime, size) -- any write by any lane changes the key and re-validates. Never cache the TEXT
# itself keyed on the path alone; that is how a reader ends up serving a file that has moved on.
_VALIDATED: dict[tuple, list] = {}


def _closed_text(live_path: Path | str) -> str:
    """The closed half's text, or '' when this is a fixture path with no closed half.

    FAIL-CLOSED ON THE CANONICAL PATH: absence there is a corrupted store, not a state. And a
    closed half that EXISTS is validated all the way to "parses as a non-empty list of atoms"
    before its text is handed to anybody, wherever it lives. That is deliberately stricter than
    what a text reader would notice on its own: `map_text`'s callers line-scan for `- id:`, so a
    half that parses to nothing, or to a mapping, would hand them a silently shorter map -- the
    same wrong-but-plausible answer the split was built to make impossible."""
    closed = closed_path_for(live_path)
    if not closed.exists():
        if _is_canonical(live_path):
            raise MapStoreError(
                f"{CLOSED_REL} is missing. The map is TWO files and this is the half that "
                "holds every finished atom; reading without it would report finished work as "
                "unstarted and flip Live nodes to Planned on the public site. Restore it from "
                "git rather than proceeding."
            )
        return ""
    try:
        stat = closed.stat()
        text = closed.read_text(encoding="utf-8")
    except OSError as exc:
        raise MapStoreError(f"{closed} exists but could not be read: {exc}") from exc
    if not text.strip():
        raise MapStoreError(
            f"{closed} is empty. An empty closed half is indistinguishable from a truncated "
            "one, so it is refused rather than read as 'nothing is finished'."
        )
    key = (str(closed), stat.st_mtime_ns, stat.st_size)
    if key not in _VALIDATED:
        atoms = _as_atom_list(text, str(closed))
        if not atoms:
            raise MapStoreError(
                f"{closed} carries no atom records. A closed half that holds nothing is a "
                "truncation, not a state -- refused rather than read as 'nothing is finished'."
            )
        _VALIDATED.clear()  # one entry is enough; this is a validation latch, not a store
        _VALIDATED[key] = atoms
    return text


def map_text(live_path: Path | str = LIVE_PATH) -> str:
    """The WHOLE map as YAML text: the live half then the closed half, concatenated.

    Both halves are top-level lists in the same hand-authored form, so the concatenation is
    itself a valid single list -- which is what lets the regex/text readers
    (`site/moap_coherence.py`, `tools/merge_atom_status.py`) keep parsing exactly as before."""
    live = Path(live_path).read_text(encoding="utf-8")
    closed = _closed_text(live_path)
    if not closed:
        return live
    if not live.endswith("\n"):
        live += "\n"
    return live + closed


def _as_atom_list(text: str, where: str) -> list:
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise MapStoreError(f"{where} is not parseable YAML: {exc}") from exc
    if loaded is None:
        return []
    if not isinstance(loaded, list):
        raise MapStoreError(
            f"{where} must be a top-level list of atom records, got {type(loaded).__name__}."
        )
    return loaded


def load_atoms(live_path: Path | str = LIVE_PATH) -> list:
    """EVERY atom -- live half first, then closed half. This is what a reader that asks
    "what does the project consist of" must call."""
    live = _as_atom_list(
        Path(live_path).read_text(encoding="utf-8"), str(live_path)
    )
    closed_text = _closed_text(live_path)
    if not closed_text:
        return live
    closed = _as_atom_list(closed_text, str(closed_path_for(live_path)))
    if not closed:
        raise MapStoreError(
            f"{closed_path_for(live_path)} parsed to no atoms. See the empty-store refusal "
            "above -- the same reasoning applies to a file of comments."
        )
    return live + closed


def load_live_atoms(live_path: Path | str = LIVE_PATH) -> list:
    """ONLY the atoms that still have somewhere to go. This is the DRAWN map -- what a draw,
    a survey of remaining work, or a person opening the file to see what is left should see.
    Deliberately does not touch the closed half, so it cannot be slowed or broken by it."""
    return _as_atom_list(Path(live_path).read_text(encoding="utf-8"), str(live_path))


def load_closed_atoms(live_path: Path | str = LIVE_PATH) -> list:
    """Only the finished atoms. Returns [] for a fixture path with no closed half."""
    text = _closed_text(live_path)
    return _as_atom_list(text, str(closed_path_for(live_path))) if text else []


def _atom_blocks(text: str) -> tuple[list[str], list[tuple[str, int, int]]]:
    """The text's lines, plus `(atom_id, start, end)` line spans for every atom record.

    A record is a `- id:` line at column 0 followed by its INDENTED continuation lines.
    Blank lines and column-0 comments deliberately end a block, so the live half's section
    headers (`# --- EPOCH 3 ...`) belong to the file, never to the atom above them, and are
    left exactly where the author put them when an atom moves out from under one."""
    lines = text.splitlines(keepends=True)
    blocks: list[tuple[str, int, int]] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("- id:"):
            start = i
            i += 1
            while i < len(lines) and lines[i].startswith((" ", "\t")):
                i += 1
            blocks.append((lines[start].split(":", 1)[1].strip(), start, i))
        else:
            i += 1
    return lines, blocks


def _cut_blocks(text: str, ids: set) -> tuple[str, list[str]]:
    """Remove each named atom's record from `text`, returning the new text and the removed
    records verbatim. Each atom owns the blank lines that FOLLOW it, so cutting one leaves its
    neighbours' spacing untouched instead of collapsing two separators into one."""
    lines, blocks = _atom_blocks(text)
    drop: set[int] = set()
    taken: list[str] = []
    for atom_id, start, end in blocks:
        if atom_id not in ids:
            continue
        taken.append("".join(lines[start:end]))
        stop = end
        while stop < len(lines) and not lines[stop].strip():
            stop += 1
        drop.update(range(start, stop))
    kept = "".join(line for n, line in enumerate(lines) if n not in drop)
    return kept, taken


def _append_blocks(text: str, records: list[str]) -> str:
    """Append whole records to a half, byte for byte, one blank line apart."""
    if not records:
        return text
    out = text
    for record in records:
        if out and not out.endswith("\n"):
            out += "\n"
        if out.strip():
            out += "\n"
        out += record if record.endswith("\n") else record + "\n"
    return out


def refile(live_path: Path | str = LIVE_PATH) -> dict:
    """Move every atom whose HALF disagrees with `is_closed` into the half it belongs in.

    THIS IS THE RELEASE FOR THE SPLIT INVARIANT, and without it that invariant has none.
    `test_the_split_predicate_agrees_with_where_every_atom_actually_SITS` asserts against the
    live tree, so it reds a tree-wide test file and refuses EVERY commit in EVERY lane the
    moment any atom reaches its own target -- which is the success path of the whole machine,
    not an edge case. Before this function existed nothing in the tree could satisfy it: the
    move was a hand edit or it did not happen. R11's *no orphan transitions* clause, applied to
    an invariant rather than to a flag.

    BOTH DIRECTIONS, and the second is the one that is easy to forget: an atom whose target is
    RAISED above its current level must come back to the drawn half, or it sits in the closed
    half where no draw ever looks and the work goes dark. That is the failure the split was
    designed to make impossible, so the re-filer must be able to undo it.

    Returns `{"to_closed": [...], "to_live": [...]}` -- the ids that moved, in that direction.
    Both empty means nothing was written AT ALL (checked, not assumed: a re-filer that
    rewrote both halves on a no-op would churn the map on every merge).

    THE HAZARD THIS REPEATS, named so the fix does not become the next incident: this is a
    TWO-FILE ATOMIC WRITE, the exact shape that wedged the tree behind the finding that asked
    for it. Half of it landing reds every lane. So the whole result -- both texts, the
    conserved population, the invariant itself -- is computed and validated BEFORE either file
    is touched, the two writes then go through `os.replace`, and a failure on the second rolls
    the first back.
    """
    live_p = Path(live_path)
    closed_p = closed_path_for(live_p)
    if not closed_p.exists():
        # THE SAME DELIBERATE SEAM the loader keys on, and for the same reason -- stated here
        # rather than inherited, because getting it wrong in THIS direction writes files. A
        # single-file fixture map is not a split store and never was, so re-filing it would
        # invent a closed half that no one asked for and empty the fixture's only file. At the
        # CANONICAL path a missing sibling is a corrupted store, never a state, so it refuses.
        if _is_canonical(live_p):
            raise MapStoreError(
                f"{CLOSED_REL} is missing, so there is no half to re-file INTO. Restore it "
                "from git rather than letting a re-file recreate it from whatever is left."
            )
        return {"to_closed": [], "to_live": []}
    live_text = live_p.read_text(encoding="utf-8")
    closed_text = closed_p.read_text(encoding="utf-8")

    live_atoms = _as_atom_list(live_text, str(live_p))
    closed_atoms = _as_atom_list(closed_text, str(closed_p)) if closed_text.strip() else []

    to_closed = [a["id"] for a in live_atoms if is_closed(a)]
    to_live = [a["id"] for a in closed_atoms if not is_closed(a)]
    if not to_closed and not to_live:
        return {"to_closed": [], "to_live": []}

    kept_live, out_records = _cut_blocks(live_text, set(to_closed))
    kept_closed, back_records = _cut_blocks(closed_text, set(to_live))
    new_live = _append_blocks(kept_live, back_records)
    new_closed = _append_blocks(kept_closed, out_records)

    if len(out_records) != len(to_closed) or len(back_records) != len(to_live):
        raise MapStoreError(
            "refile could not locate every record it had to move as text "
            f"({len(out_records)}/{len(to_closed)} out, {len(back_records)}/{len(to_live)} "
            "back). Refusing rather than writing a half-moved map."
        )

    # Validate the RESULT before writing either file. Population first: the split is a fact
    # about storage, so an atom may not be lost, duplicated or invented by moving it.
    new_live_atoms = _as_atom_list(new_live, str(live_p))
    new_closed_atoms = _as_atom_list(new_closed, str(closed_p))
    before = sorted(a["id"] for a in live_atoms + closed_atoms)
    after = sorted(a["id"] for a in new_live_atoms + new_closed_atoms)
    if before != after:
        lost = sorted(set(before) - set(after))
        gained = sorted(set(after) - set(before))
        raise MapStoreError(
            f"refile would change the atom population (lost={lost}, gained={gained}, "
            f"{len(before)} -> {len(after)}). Refusing: the split moves records, never atoms."
        )
    if not new_closed_atoms:
        raise MapStoreError(
            "refile would empty the closed half, which every reader here refuses as a "
            "truncation rather than reading it as 'nothing is finished'. Lower the targets in "
            "a commit of their own, or keep the half populated."
        )
    still_wrong = [a["id"] for a in new_live_atoms if is_closed(a)] + [
        a["id"] for a in new_closed_atoms if not is_closed(a)
    ]
    if still_wrong:
        raise MapStoreError(
            f"refile ran and the invariant still fails for {still_wrong}. Refusing to write a "
            "result that does not satisfy the predicate it exists to satisfy."
        )

    _write_both(live_p, new_live, closed_p, new_closed)
    _VALIDATED.clear()
    return {"to_closed": sorted(to_closed), "to_live": sorted(to_live)}


def _write_both(live_p: Path, live_text: str, closed_p: Path, closed_text: str) -> None:
    """Write both halves as close to atomically as two files allow: each through a temp file
    in the same directory and `os.replace` (atomic per file), the second failure rolling the
    first back, so the observable states are both-old and both-new."""
    previous_live = live_p.read_text(encoding="utf-8")
    _replace(live_p, live_text)
    try:
        _replace(closed_p, closed_text)
    except OSError as exc:
        _replace(live_p, previous_live)
        raise MapStoreError(
            f"the closed half could not be written ({exc}); the live half was rolled back so "
            "the map is not left half-moved."
        ) from exc


def _replace(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".refile.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def is_closed(atom: dict) -> bool:
    """The predicate the split is made on, stated ONCE so the splitter, the loader and any
    future auditor cannot drift: an atom belongs in the closed half when it has reached its
    own target. `closed:` prose is a REASON attached by whoever closed it, not the test --
    an atom can be closed with a reason and still sit below a target nobody lowered, and the
    two-file split must not silently disagree with the draw's own `has_gap` predicate."""
    try:
        return int(atom.get("level_current", 0)) >= int(atom.get("level_target", 0))
    except (TypeError, ValueError):
        return False


if __name__ == "__main__":  # pragma: no cover -- operator convenience
    live = load_live_atoms()
    closed = load_closed_atoms()
    print(f"live (still carrying work): {len(live)}")
    print(f"closed (at or above target): {len(closed)}")
    print(f"whole map: {len(load_atoms())}")
