"""§0 LEVEL-PROMOTION PREVENTION gate (2026-07-18): an UNAUTHORIZED level_current increase in
docs/design/maturity_map.yaml is STRUCTURALLY IMPOSSIBLE to commit -- not merely detected.

WHY (real incident 2026-07-18): the autonomous worker self-moved `E4 level_current 2->3` in a
commit. `background/fronts_reconciler.py` DETECTED it (SCOPE_VIOLATION / LEVEL_SELF_PROMOTION) after
the fact, but nothing PREVENTED the commit landing -- and a recurring unauthorized level move
renders on the director's site as a FALSE level until someone notices the alarm. This gate is the
PREVENTION layer: the reconciler is detection (report-only, after the commit), this refuses the
commit at write time. Same principle as the pre-commit TEST GATE: structural impossibility over a
remembered "don't move the cell" discipline (the discipline already failed once).

THE RULE (MATURITY_MAP.md §0): the director+advisor own levels; the agent PROPOSES a level-up with
evidence (docs/observability/level_up_proposals.jsonl), it NEVER moves a cell. The ONLY thing that
authorizes a level_current increase is a valid director-console LEVEL_UP_PROPOSED in
docs/observability/gate_authorizations.jsonl covering that atom at >= the new level.

INDEPENDENCE / REUSE (R15 anti-tautology): the validity predicate is REUSED verbatim from
`background.gate_authorization.is_valid_level_up` -- the SAME check the reconciler uses -- so a
worker-forged ledger entry (channel != console, or no provenance) authorizes NOTHING here exactly
as it authorizes nothing there. This module does NOT reimplement the four console checks.

SCOPE (what this gate does and does NOT block):
  * level_current INCREASE (old->new, new>old, both ints) with no valid authorization -> REJECT.
  * the SAME increase WITH a valid director LEVEL_UP_PROPOSED at >= the new level -> ALLOW.
  * level DECREASE (a revert/un-promotion, e.g. L3->L2) -> ALLOW (un-promoting is not self-promoting).
  * a NEW atom appearing at a level (absent from the HEAD map) -> ALLOW (the reconciler + LEVEL
    baseline own new atoms; gating a new atom landing at >L1 without authorization is noted below
    as a possible extension, deliberately not built to avoid over-blocking a legitimate seed).
  * the map file NOT staged -> do nothing (return 0): a non-map commit is never blocked.

FAIL-CLOSED conceptually: if the map IS staged but the STAGED (new) content cannot be parsed, the
gate REFUSES the commit -- an increase could be hidden in a syntactically-broken diff, and silently
allowing an unverifiable map change is exactly the fail-open pattern R15 forbids. It never blocks a
commit that does not touch the map.

GIT-ENV SAFETY (H24_precommit_gate_git_env_isolation): during `git commit` the hook inherits GIT_*
pointing at the in-progress index. This gate ONLY runs READ-ONLY plumbing reads (`git show :<path>`
for the staged blob, `git show HEAD:<path>` for the baseline) -- it never runs a git command that
WRITES the index/worktree, so it cannot corrupt the commit (the H24 failure was git-touching tests
that WROTE via a leaked GIT_DIR/GIT_INDEX_FILE). `git show :<path>` deliberately WANTS the commit's
index -- that is precisely the staged content to inspect -- so inheriting GIT_INDEX_FILE is correct
here, not dangerous. GIT_PREFIX is stripped so the `:<path>` pathspec resolves from the repo root
regardless of the subdirectory the commit was launched from.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

# Reuse the SAME validity predicate + ledger reader the reconciler uses -- do NOT reimplement.
_TOOLS_DIR = Path(__file__).resolve().parent
ROOT = _TOOLS_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from background.gate_authorization import is_valid_level_up, read_ledger  # noqa: E402

MAP_REL = "docs/design/maturity_map.yaml"


# ── pure map parsing (mutation-testable) ────────────────────────────────────────────────────
def atom_levels(map_text: str) -> dict:
    """{atom_id: level_current} for every atom (keyed on `id`, matching the reconciler). Raises on
    a yaml parse error -- the caller turns that into a fail-closed REJECT for staged content."""
    out: dict = {}

    def walk(o):
        if isinstance(o, dict):
            aid = o.get("id")
            if isinstance(aid, str) and "level_current" in o:
                out[aid] = o.get("level_current")
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    for d in yaml.safe_load_all(map_text):
        walk(d)
    return out


def level_increases(old_levels: dict, new_levels: dict) -> list:
    """Atoms whose level_current INCREASED (both ints, new > old). Pure. A decrease/no-change is not
    returned (a revert is allowed); an atom absent from `old_levels` (new atom) is not returned."""
    out = []
    for atom, new in new_levels.items():
        old = old_levels.get(atom)
        if isinstance(old, int) and isinstance(new, int) and new > old:
            out.append({"atom": atom, "from": old, "to": new})
    return out


def _level_authorized(atom_id: str, to_level, ledger: list) -> bool:
    """Is a level move to `to_level` authorized by a valid director-console LEVEL_UP_PROPOSED for this
    atom? Mirrors fronts_reconciler._level_cleared exactly, reusing is_valid_level_up: an entry with a
    `level` bounds clearance to that target (to_level <= level); without one it clears any increase
    for the atom. A forged (non-console / no-provenance) entry fails is_valid_level_up -> clears nothing."""
    for e in ledger:
        if not is_valid_level_up(e) or e.get("atom") != atom_id:
            continue
        lvl = e.get("level")
        if lvl is None or (isinstance(to_level, int) and isinstance(lvl, int) and to_level <= lvl):
            return True
    return False


def unauthorized_level_increases(increases: list, ledger: list) -> list:
    """THE predicate: level increases with NO valid director-console LEVEL_UP_PROPOSED covering them.
    Pure -> mutation-testable. An empty list means every staged increase is director-authorized."""
    return [inc for inc in increases if not _level_authorized(inc["atom"], inc["to"], ledger)]


def evaluate(old_text: str | None, new_text: str, ledger: list) -> dict:
    """Classify a staged map change. `new_text` is the STAGED content (required); `old_text` is the
    HEAD content, or None if the file is new (=> no baseline, every atom is a new atom -> allowed).
    Returns {status, unauthorized, message}. FAIL-CLOSED: an unparseable new_text -> REJECT."""
    try:
        new_levels = atom_levels(new_text)
    except Exception as exc:  # noqa: BLE001 -- any parse failure is unverifiable -> fail-closed
        return {"status": "REJECT_UNPARSEABLE", "unauthorized": [],
                "message": f"§0: the STAGED {MAP_REL} could not be parsed ({exc}). The level-promotion "
                           f"gate cannot verify it, and an unverifiable map change may not be committed "
                           f"(fail-closed). Fix the YAML, then commit."}
    if old_text is None:
        return {"status": "CLEAN_NEW_FILE", "unauthorized": [],
                "message": f"{MAP_REL} is new (no HEAD baseline) -- no level increase to gate."}
    try:
        old_levels = atom_levels(old_text)
    except Exception:  # noqa: BLE001 -- HEAD passed this same gate, so this is not expected; degrade
        old_levels = {}  # treat every atom as "new" rather than false-reject a map-repair commit
    increases = level_increases(old_levels, new_levels)
    unauth = unauthorized_level_increases(increases, ledger)
    if unauth:
        lines = []
        for u in unauth:
            lines.append(
                f"§0: level_current {u['from']}->{u['to']} on {u['atom']} has no director LEVEL_UP "
                f"authorization. The agent PROPOSES level-ups (docs/observability/level_up_proposals.jsonl), "
                f"it never moves the cell. Remove the level_current change from this commit; the "
                f"orchestrator moves it on director+advisor ratification."
            )
        return {"status": "REJECT", "unauthorized": unauth, "message": "\n".join(lines)}
    return {"status": "CLEAN", "unauthorized": [],
            "message": f"all {len(increases)} staged level increase(s) are director-authorized"}


# ── git-env-safe read-only helpers ──────────────────────────────────────────────────────────
def _git_show(spec: str) -> str | None:
    """Read a blob via `git show <spec>` (read-only plumbing). Returns None if the object is absent
    (path not in the index / not in HEAD). GIT_PREFIX is stripped so `:<path>` resolves from the repo
    root regardless of the launching subdir; GIT_INDEX_FILE is intentionally kept -- for `:<path>` it
    points at the commit's index, exactly the staged content to inspect. No git WRITE is ever run."""
    env = {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}
    r = subprocess.run(["git", "show", spec], cwd=str(ROOT), env=env,
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout


def _staged_names() -> list[str]:
    """Paths staged in this commit (read-only)."""
    r = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                       cwd=str(ROOT), env={k: v for k, v in os.environ.items() if k != "GIT_PREFIX"},
                       capture_output=True, text=True)
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def main() -> int:
    if MAP_REL not in _staged_names():
        return 0  # the map is not part of this commit -- never block a non-map commit
    new_text = _git_show(f":{MAP_REL}")
    if new_text is None:
        # Staged per the name list but the staged blob is unreadable -> cannot verify -> fail-closed.
        sys.stderr.write(
            f"\n[level-gate] ❌ §0: {MAP_REL} is staged but its staged content could not be read -- "
            f"COMMIT REFUSED (fail-closed; an unverifiable map change may hide a level increase).\n"
        )
        return 1
    old_text = _git_show(f"HEAD:{MAP_REL}")  # None => new file, allowed
    result = evaluate(old_text, new_text, read_ledger())
    if result["status"] in ("REJECT", "REJECT_UNPARSEABLE"):
        sys.stderr.write("\n[level-gate] ❌ COMMIT REFUSED (MATURITY_MAP.md §0 -- levels are the "
                         "director+advisor's, not the agent's):\n" + result["message"] + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
