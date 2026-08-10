"""§0 LEVEL-PROMOTION RECORDING gate (2026-07-18; RESCOPED 2026-07-29): an UNRECORDED level_current
increase in docs/design/maturity_map.yaml is STRUCTURALLY IMPOSSIBLE to commit -- not merely detected.

WHY (real incident 2026-07-18): the autonomous worker self-moved `E4 level_current 2->3` in a
commit. `background/fronts_reconciler.py` DETECTED it (SCOPE_VIOLATION / LEVEL_SELF_PROMOTION) after
the fact -- that reconciler was itself deleted on 2026-08-03 with the rest of the permission
machinery, leaving THIS gate as the sole level control -- but nothing PREVENTED the commit landing -- and a recurring unrecorded level move renders
on the director's site as a FALSE level until someone notices the alarm. This gate is the PREVENTION
layer: the reconciler is detection (report-only, after the commit), this refuses the commit at write
time. Same principle as the pre-commit TEST GATE: structural impossibility over a remembered "record
the move" discipline (the discipline already failed once).

THE RULE, RESCOPED (2026-07-29, DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY item 2): "director_level_up
is abolished as a block. Levels are proposed and recorded (ledger-backed per R16), never gated --
recording satisfies R16's real requirement, self-certification does not need a separate permission gate
on top." A level_current increase requires a RECORD in docs/observability/gate_authorizations.jsonl
covering that atom at >= the new level. Since 2026-08-03 that record is ALWAYS a SELF-CERTIFIED entry
(`background.gate_authorization.record_level_up_self_certified`, evidence-bearing, honestly stamped
channel=='self'); the director-console / twin / phone acts it used to also accept no longer exist. What this gate refuses is an UNRECORDED
increase (R16: the ledger is authority, not a commit message) -- it no longer requires that the record be
director-authored.

INDEPENDENCE / REUSE (R15 anti-tautology): the validity predicate is REUSED verbatim from
`background.gate_authorization.is_valid_level_up` -- the SAME check the ledger reader uses -- so a
worker-forged entry that self-declares channel==console (impersonating a director act) still authorizes
NOTHING here exactly as it authorizes nothing there; only an HONEST self-certified/twin/console/phone
record clears it. This module does NOT reimplement those checks.

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

═══════════════════════════════════════════════════════════════════════════════════════════════
SECOND CONTROL (2026-08-10): RECORDED-BUT-UNBUILT -- a level may not be declared for code the
commit does not contain.
═══════════════════════════════════════════════════════════════════════════════════════════════

WHY (WORKER_FINDING_A_LEVEL_CAN_BE_DECLARED_FOR_UNCOMMITTED_CODE_2026-08-10, third instance in
three days, second in two commits): a tick builds, verifies green IN THE WORKING TREE, writes the
map and the simplifications store FROM THE WORKING TREE, and is cut off at its bounded edge before
committing. The map then publishes measured figures that NOTHING IN THE REPOSITORY CAN PRODUCE
(H39 declared L2 with `flatten_to_mean_profile` named in its build_note while that program existed
in no commit). The commit immediately before was itself titled "H38 was the second pass to land
uncommitted" -- three instances, two prior commit-message exhortations, zero mechanisms. That is
the MAKE_IT_STICK signature exactly: convert to mechanism or accept it will evaporate. This is the
same seam a third time -- a control whose subject is the TREE publishing a claim whose subject is
the COMMIT (cousins on file: the capability index reads the working tree; the gate lints the
working tree).

THE RULE: for any atom whose `level_current` INCREASES in this commit, that atom's `file_scope` may
not hold SOURCE that is not landing in this commit. Then a green working tree and a committed repo
say the same thing about the program the level rests on.

"NOT LANDING IN THIS COMMIT" IS THE PORCELAIN WORKTREE COLUMN, NOT A PATH-SET COMPARISON: in
`git status --porcelain` the Y column is worktree-vs-INDEX. Y clean => the worktree equals what is
being committed, whatever the pathspec was. So Y dirty (or untracked) IS the predicate, and it
catches the PARTIALLY-staged file (X=M,Y=M -- half the verified program lands) that comparing the
commit's pathspec against file_scope would wave through.

SCOPED TO SOURCE, DELIBERATELY (the measurement that made this control survivable): the claim a
level makes is about a PROGRAM, so only program text counts (`SOURCE_SUFFIXES`). This tree is a
SHARED working tree with concurrent daemon writers (process_run_complete, sim_runner,
background_worker) that permanently hold `site/data/*.json`, `docs/observability/*` and
`background/.*.json` dirty BY DESIGN -- those are the publisher's OUTPUT, never the program. Measured
on the live tree at build time: an all-dirt predicate blocks 61 of the 209 atoms that carry a
file_scope, i.e. a control that is red for reasons its subject cannot fix, which
`feedback_control_that_can_only_fail_wedges` says is routed around within a day. The source-scoped
predicate blocks 35, and every one of those names genuinely uncommitted program text. A control
that cannot pass is worth nothing; this one passes on an ordinary clean level move (R15 requires
that direction be shown, and `test_clean_file_scope_ALLOWS_the_increase` shows it).

FAIL-CLOSED (R15 fail-silent: an unavailable check is a FAILED check): if the status probe for an
atom cannot be run, that atom is treated as UNBUILT and the commit is refused, rather than passing
for want of an answer.

KNOWN CONTROL-SET HOLE, stated rather than hidden (`feedback_control_set_hole_not_control_defect`):
53 of the 262 atoms carry an EMPTY file_scope, so this control has nothing to check for them and
they pass. That is a gap in the MAP's data, not a fail-open in this predicate -- the gate reports
the hole on stderr when it waves such an atom through, so it is visible at the moment it matters
instead of being silently counted as a pass.
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


def atom_file_scopes(map_text: str) -> dict:
    """{atom_id: [file_scope paths]} for every atom, mirroring atom_levels' walk. An atom with no
    file_scope key, or a non-list one, maps to [] -- the caller reports that as the control-set hole
    it is (nothing to check) rather than treating it as a clean scope."""
    out: dict = {}

    def walk(o):
        if isinstance(o, dict):
            aid = o.get("id")
            if isinstance(aid, str) and "level_current" in o:
                scope = o.get("file_scope")
                out[aid] = [p for p in scope if isinstance(p, str)] if isinstance(scope, list) else []
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    for d in yaml.safe_load_all(map_text):
        walk(d)
    return out


# Program text -- the only thing a level_current claim is ABOUT. Everything else in a file_scope
# (site/data/*.json, docs/observability/*, docs/design/*.md) is either the publisher's regenerated
# OUTPUT or prose; on this shared tree those are permanently dirty and would make the control
# unpassable. See the SCOPED TO SOURCE note in the module docstring for the measured numbers.
SOURCE_SUFFIXES = (".py",)


def is_source(path: str) -> bool:
    """Is `path` program text this gate is willing to block a level move over? Pure."""
    return path.endswith(SOURCE_SUFFIXES)


def dirty_source_paths(porcelain: str) -> list:
    """SOURCE paths in a `git status --porcelain` block that are NOT landing in this commit. Pure ->
    mutation-testable.

    The Y (worktree-vs-index) column is the whole test: Y clean means the worktree equals the content
    being committed, so the file IS landing. Y dirty means the verified bytes differ from the
    committed bytes -- including the PARTIALLY staged X=M,Y=M case. Untracked ('??') is a program
    that exists only in the tree. Ignored ('!!') is not the commit's business.
    """
    out = []
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        xy, rest = line[:2], line[3:]
        if xy == "!!":
            continue
        # Rename/copy entries are "R  old -> new": the path that must be clean is the destination.
        path = rest.split(" -> ")[-1].strip()
        if path.startswith('"') and path.endswith('"'):  # git quotes paths with odd characters
            path = path[1:-1]
        if not is_source(path):
            continue
        if xy == "??" or xy[1] != " ":
            out.append(path)
    return sorted(set(out))


def unbuilt_level_increases(increases: list, scope_status: dict) -> list:
    """THE second predicate: level increases whose file_scope holds source that is not landing.
    Pure -> mutation-testable.

    `scope_status` maps atom_id -> the porcelain text for that atom's file_scope, or None if the
    probe could not be run. None is treated as UNBUILT, never as clean: an unavailable check is a
    FAILED check (R15 fail-silent). An atom absent from `scope_status` had nothing to probe (empty
    file_scope) and is passed through -- the declared control-set hole, reported by the caller.
    """
    out = []
    for inc in increases:
        if inc["atom"] not in scope_status:
            continue
        porcelain = scope_status[inc["atom"]]
        if porcelain is None:
            out.append({**inc, "dirty": [], "unverifiable": True})
            continue
        dirty = dirty_source_paths(porcelain)
        if dirty:
            out.append({**inc, "dirty": dirty, "unverifiable": False})
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
    """Is a level move to `to_level` covered by a valid RECORD for this atom? Reuses
    is_valid_level_up (the sole predicate since fronts_reconciler was deleted): an entry with a
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
    """THE predicate: level increases with NO valid RECORD covering them. Pure -> mutation-testable.
    An empty list means every staged increase left an evidence-bearing trace in the ledger."""
    return [inc for inc in increases if not _level_authorized(inc["atom"], inc["to"], ledger)]


def evaluate(old_text: str | None, new_text: str, ledger: list) -> dict:
    """Classify a staged map change. `new_text` is the STAGED content (required); `old_text` is the
    HEAD content, or None if the file is new (=> no baseline, every atom is a new atom -> allowed).
    Returns {status, unauthorized, message}. FAIL-CLOSED: an unparseable new_text -> REJECT."""
    try:
        new_levels = atom_levels(new_text)
    except Exception as exc:  # noqa: BLE001 -- any parse failure is unverifiable -> fail-closed
        return {"status": "REJECT_UNPARSEABLE", "unauthorized": [], "increases": [],
                "message": f"§0: the STAGED {MAP_REL} could not be parsed ({exc}). The level-promotion "
                           f"gate cannot verify it, and an unverifiable map change may not be committed "
                           f"(fail-closed). Fix the YAML, then commit."}
    if old_text is None:
        return {"status": "CLEAN_NEW_FILE", "unauthorized": [], "increases": [],
                "message": f"{MAP_REL} is new (no HEAD baseline) -- no level increase to gate."}
    try:
        old_levels = atom_levels(old_text)
    except Exception:  # noqa: BLE001 -- HEAD passed this same gate, so this is not expected; degrade
        old_levels = {}  # treat every atom as "new" rather than false-reject a map-repair commit
    increases = level_increases(old_levels, new_levels)
    unauth = unauthorized_level_increases(increases, ledger)
    if unauth:
        # (`increases` is returned on every path below so main() can run the RECORDED-BUT-UNBUILT
        # control over the same set without re-parsing the map.)
        lines = []
        for u in unauth:
            lines.append(
                f"§0: level_current {u['from']}->{u['to']} on {u['atom']} has no recorded LEVEL_UP in "
                f"docs/observability/gate_authorizations.jsonl. Record one before committing -- a "
                f"director/twin act still works, or self-certify with evidence: "
                f"background.gate_authorization.record_level_up_self_certified('{u['atom']}', {u['to']}, "
                f"'<evidence -- tests green / R15 proof / fetched artifact>'). Recording is required "
                f"(R16: the ledger is authority, not a commit message); director permission on top of it "
                f"is not (2026-07-29 ruling item 2)."
            )
        return {"status": "REJECT", "unauthorized": unauth, "increases": increases,
                "message": "\n".join(lines)}
    return {"status": "CLEAN", "unauthorized": [], "increases": increases,
            "message": f"all {len(increases)} staged level increase(s) are recorded"}


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


def _scope_status(paths: list) -> str | None:
    """Porcelain status for one atom's file_scope, or None if the probe failed (-> fail-closed).

    `--no-optional-locks` is REQUIRED here, not decorative: an ordinary `git status` refreshes and
    REWRITES the index stat-cache, and in a pre-commit hook GIT_INDEX_FILE points at the in-progress
    commit's index -- writing it is precisely the H24 corruption this module's GIT-ENV SAFETY note
    forbids. With the flag git takes no lock and writes nothing, keeping the whole gate read-only.
    A file_scope path that does not exist in the repo is not an error for `status` (23 such paths
    exist in the map today); it simply contributes no output.
    """
    env = {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}
    try:
        r = subprocess.run(["git", "--no-optional-locks", "status", "--porcelain", "--", *paths],
                           cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001 -- probe unavailable == probe failed (R15 fail-silent)
        return None
    return r.stdout if r.returncode == 0 else None


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
        sys.stderr.write("\n[level-gate] ❌ COMMIT REFUSED (MATURITY_MAP.md §0 -- a level move must be "
                         "RECORDED, self-certified or director's, R16/2026-07-29 ruling item 2):\n"
                         + result["message"] + "\n")
        return 1

    # ── SECOND CONTROL: the level must be declared for code this commit CONTAINS ────────────────
    increases = result.get("increases") or []
    if not increases:
        return 0
    try:
        scopes = atom_file_scopes(new_text)
    except Exception:  # noqa: BLE001 -- new_text already parsed above; unreachable in practice
        scopes = {}
    scope_status, no_scope = {}, []
    for inc in increases:
        paths = scopes.get(inc["atom"]) or []
        if not paths:
            no_scope.append(inc["atom"])  # declared control-set hole -- reported, never silent
            continue
        scope_status[inc["atom"]] = _scope_status(paths)
    if no_scope:
        sys.stderr.write(
            f"\n[level-gate] ⚠ built-check SKIPPED for {', '.join(sorted(no_scope))}: no file_scope in "
            f"{MAP_REL}, so there is nothing to check that the commit contains. Give the atom a "
            f"file_scope to bring it under this control.\n"
        )
    unbuilt = unbuilt_level_increases(increases, scope_status)
    if unbuilt:
        lines = []
        for u in unbuilt:
            if u["unverifiable"]:
                lines.append(
                    f"§0: level_current {u['from']}->{u['to']} on {u['atom']} could not be verified as "
                    f"BUILT -- the `git status` probe over its file_scope failed. An unavailable check "
                    f"is a failed check (R15), so the commit is refused rather than assumed clean."
                )
                continue
            lines.append(
                f"§0: level_current {u['from']}->{u['to']} on {u['atom']} declares a level for source "
                f"this commit does NOT contain -- its file_scope holds program text that is not "
                f"landing:\n    " + "\n    ".join(u["dirty"]) + "\n"
                "  The map would publish a measurement nothing in the repository can reproduce "
                "(WORKER_FINDING_A_LEVEL_CAN_BE_DECLARED_FOR_UNCOMMITTED_CODE_2026-08-10). Fix: "
                "`git add` that source into THIS commit (or commit it first), then re-commit the "
                "level move. If the file genuinely is not part of the claim, take it out of the "
                "atom's file_scope."
            )
        sys.stderr.write("\n[level-gate] ❌ COMMIT REFUSED (a level move must be BUILT in the commit "
                         "that declares it):\n" + "\n".join(lines) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
