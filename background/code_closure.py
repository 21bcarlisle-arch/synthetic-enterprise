"""The set of repo files a daemon ACTUALLY LOADS — its own import closure (PW1 half (b)).

Why this exists: boot-SHA drift used to ask "has HEAD moved since this daemon booted?". On a repo
that commits every tick, that question is answered YES for every daemon within minutes of any boot,
so the signal is permanently red — and the director's ruling is that *"a detector for that failure
mode that is always red will be ignored exactly as reliably as one that is blind"*
(DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09, DECIDED #2). The question that actually matters is
narrower: **has any module THIS daemon imported changed since it booted?** A daemon whose loaded
code is untouched is not stale no matter how far HEAD has moved; a daemon running pre-fix code for a
module it imports is stale even if only one file changed.

What this module does NOT do: derive its own import graph. `tools/select_impacted_tests.py` already
owns this repo's static one (`build_graph` -> file -> the repo files it imports, with dotted-name
resolution and the root/skip conventions). This module stands on it and adds only the two things
that graph has no opinion about — the manifest `command` -> entry-file mapping, and a BFS from one
daemon's entry point. (`capability_index` maps callers, not a per-entry-point closure;
`epistemic_verifier`/`internal_seam_verifier` walk imports to judge seam legality, not reachability.)

The closure is STATIC, not runtime, because the comparison must be reproducible for a daemon booted
from an OLD tree (replay), and because reading another process's live module table is not available
to us. It over-approximates in the safe direction: a conditional/lazy import that never executes
still counts as loaded, so the signal errs toward RED, never toward a false green.

Consumed by `process_reconciler.loaded_code_drift`. REPORT ONLY — nothing here restarts anything.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_GRAPH_CACHE: dict[str, dict[str, set[str]]] = {}


def _forward_graph(repo: Path) -> dict[str, set[str]]:
    """`{repo-relative file: files it imports}` from the shared static import graph. Cached per
    process: the twelve daemon closures overlap heavily, and the graph costs one parse of the tree."""
    key = str(repo)
    if key not in _GRAPH_CACHE:
        from tools.select_impacted_tests import build_graph
        _GRAPH_CACHE[key] = build_graph(repo)[1]
    return _GRAPH_CACHE[key]


def entry_path(command: str, repo: Path | None = None) -> str | None:
    """The repo-relative entry script for a manifest `command`, or None if it names none.

    Handles both launch forms actually used in process_manifest.yaml:
      `python3 background/sim_runner.py`          -> background/sim_runner.py
      `python3 -m background.naive_organ daemon`  -> background/naive_organ.py
    """
    repo = repo or _REPO
    tokens = command.split()
    for i, tok in enumerate(tokens):
        if tok == "-m" and i + 1 < len(tokens):
            rel = Path(*tokens[i + 1].split(".")).with_suffix(".py")
            if (repo / rel).is_file():
                return rel.as_posix()
            init = Path(*tokens[i + 1].split(".")) / "__init__.py"
            return init.as_posix() if (repo / init).is_file() else None
        if tok.endswith(".py") and (repo / tok).is_file():
            return Path(tok).as_posix()
    return None


def import_closure(entry_rel: str, repo: Path | None = None) -> set[str]:
    """Every repo file transitively imported by `entry_rel`, including itself (repo-relative posix
    paths). An entry that does not exist, or one outside the graph's analysed roots, returns the
    EMPTY set — callers must treat empty as UNRESOLVED, never as 'nothing changed' (that is the
    fail-open shape, R15)."""
    repo = repo or _REPO
    entry_rel = Path(entry_rel).as_posix()
    if not (repo / entry_rel).is_file():
        return set()
    forward = _forward_graph(repo)
    if entry_rel not in forward:
        return set()
    seen: set[str] = set()
    queue = [entry_rel]
    while queue:
        cur = queue.pop()
        if cur in seen:
            continue
        seen.add(cur)
        queue.extend(n for n in forward.get(cur, ()) if n not in seen)
    return seen


def closure_for_session(session: str, path: Path | None = None,
                        repo: Path | None = None) -> set[str]:
    """The import closure of the manifest entry named `session` (empty if it has no entry point)."""
    from background.process_reconciler import load_manifest
    repo = repo or _REPO
    for entry in load_manifest(path):
        if entry.get("session") == session:
            rel = entry_path(entry.get("command", ""), repo)
            return import_closure(rel, repo) if rel else set()
    return set()


if __name__ == "__main__":  # pragma: no cover - operator inspection aid
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/code_closure.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("code_closure")
    for s in sys.argv[1:]:
        c = closure_for_session(s)
        print(f"{s}: {len(c)} modules")
        for p in sorted(c):
            print(f"  {p}")
