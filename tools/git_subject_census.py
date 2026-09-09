"""Which `git` calls in `background/` and `tools/` can be asking the WRONG TREE.

THE DEFECT CLASS THIS EXISTS FOR (2026-09-09, Lane 0). `PROJECT_DIR` is
`Path(__file__).resolve().parent.parent` — whichever tree the module was IMPORTED from. 44 modules
pass such a root as `cwd=` to git. `seat_continuation.shared_tree_dir` learned on 2026-09-04 that
this is the worktree's own copy, and `origin_reconcile.shared_tree` learned the same thing
independently on 2026-09-08 and fixed it with OPPOSITE failure semantics (one falls back to
`project_dir`, the other refuses with `None`). One legal rule, two implementations, both locally
correct — the VAT shape.

WHAT THE CENSUS ESTABLISHED, and why this module is not a 44-row sweep:

  **In a linked worktree most of git is ALREADY shared.** Objects and ordinary refs live in the
  common dir, so `git log origin/main`, `git rev-list <sha>` and `git cat-file` answer identically
  from either tree. Only `HEAD`, the index, the working tree and per-worktree refs differ. So the
  discriminator is NOT the subcommand — it is whether the call names its subject. Every `_git` in
  `delivery_lane` passes an explicit commit or `origin/main`, so it is immune to the whole class
  while still spelling `cwd=PROJECT_DIR`. A blanket `shared_tree()` sweep would have "fixed" it
  into asking a different question.

  **The hook-chain gates are correct, and NOT because of their `cwd`.** `core.hooksPath` is an
  absolute path into the MAIN tree, so committing from a linked worktree runs the main tree's copy
  of every gate, and `ROOT` inside them resolves to the MAIN tree. They still gate the right commit
  because git exports `GIT_DIR` and `GIT_INDEX_FILE` pointing at the LINKED worktree, and those
  beat `cwd`. Measured, not reasoned about — a main-plus-linked pair in `/tmp`, hook run from the
  worktree, `git diff --cached` executed with `cwd=<main tree>` returned the WORKTREE's staged file.

THE HAZARD THIS GUARDS, which is one edit wide and fails OPEN AND SILENT. That correctness rests
entirely on inheriting `GIT_DIR`. This repository contains TWO functions whose entire purpose is to
strip it — `site_lane_gate._gitless_env` and `pre_commit_test_gate._gitless_env` — because a
git-touching *pytest* child obeying the in-progress commit's index once corrupted the real index.
Both are correctly aimed at `pytest` today. Point either at a `git` call and the gate reads an empty
staged list, finds nothing to object to, and PASSES. In the same `/tmp` pair, scrubbing `GIT_DIR`
turned `git diff --cached --name-only` from `SECOND_WORKTREE_FILE.txt` into empty output.

So the refusal below is deliberately narrow: not "never spell `cwd=PROJECT_DIR`" (44 sites, mostly
correct), but "a **git** call that reads the index or working tree IMPLICITLY must not be handed an
environment that drops `GIT_DIR`". That is the one edit that converts a green gate into a vacuous
one, and nothing else in the tree asserts it.

WHY NOT A TEST OVER THE 44. A control keyed to today's 44 goes red when a module becomes *more*
honest and stays green when the claim rots. This one is keyed to the property.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CENSUS_ROOTS = ("background", "tools")

#: Subcommands whose answer depends on WHICH worktree asks — HEAD, the index, the working tree.
#: `log`/`rev-list`/`show` are absent on purpose: they are per-worktree only when they fall back to
#: an implicit HEAD, which `_names_its_subject` decides separately.
INDEX_OR_WORKTREE = frozenset({
    "status", "add", "commit", "stash", "clean", "checkout", "restore", "apply", "reset",
    "mv", "rm", "write-tree", "ls-files", "diff", "diff-index", "diff-files",
})

#: A call carrying any of these names its subject and is immune: the answer comes from the object
#: store or a shared ref, identically from every worktree.
_EXPLICIT_SUBJECT = re.compile(
    r"origin/|refs/|--cached|HEAD~|[0-9a-f]{7,40}|"
    r"\b(commit|sha|base|since|ref|rev|head_sha|published)\b", re.I)


#: The variables that decide WHICH TREE a git call reads. `GIT_PREFIX` is deliberately absent:
#: stripping it is what `write_time_gate` and `ruling_archive_question_gate` do so that `:<path>`
#: resolves from the repo root, and it changes no tree.
_LOAD_BEARING = ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE")

#: A blanket `GIT_`-prefix filter. This is the `_gitless_env` shape, and it takes the three above
#: with it. Written as a pattern rather than a name because both live implementations are inline
#: comprehensions, not a shared helper — the VAT shape again.
_PREFIX_FILTER = re.compile(r"startswith\(\s*['\"]GIT_?['\"]|\bGIT_\*")


def _preserves_git_dir(env_source: str | None) -> bool:
    """Whether an env expression still carries the variables that name the worktree.

    NOT "does it mention `os.environ`". The first draft of this check asked exactly that and was
    a FAIL-OPEN caught by its own poison round: `{k: v for k, v in os.environ.items() if not
    k.startswith("GIT_")}` mentions `os.environ` and is precisely the defect. What matters is what
    the expression REMOVES, not what it reads from.
    """
    if not env_source or "environ" not in env_source:
        return False                       # built from nothing, or unresolvable -> refuse
    if _PREFIX_FILTER.search(env_source):
        return False
    return not any(var in env_source for var in _LOAD_BEARING)


@dataclass(frozen=True)
class Callsite:
    module: str
    lineno: int
    cwd: str
    argv: str
    env: str | None
    #: `env` with a bare local name substituted for what it was assigned, or `env` unchanged when
    #: it is already an expression. None when no `env=` was passed. UNRESOLVABLE NAMES STAY
    #: UNRESOLVED and are therefore refused: "I could not tell" must not read as "it is fine".
    env_source: str | None = None

    @property
    def subcommands(self) -> set[str]:
        return set(re.findall(r"['\"]([a-z][a-z-]{2,})['\"]", self.argv)) & INDEX_OR_WORKTREE

    @property
    def reads_local_state(self) -> bool:
        """Reads the index/working tree, and does NOT name a subject that would make it shared."""
        if not self.subcommands:
            return False
        # `--cached` alone does not make a call shared; it is the INDEX, which is per-worktree.
        # It appears in `_EXPLICIT_SUBJECT` so that `diff --cached <sha>` is not double-counted,
        # so re-admit the bare-index form here rather than letting the regex swallow it.
        if "--cached" in self.argv and not re.search(r"[0-9a-f]{7,40}|origin/|refs/", self.argv):
            return True
        return not _EXPLICIT_SUBJECT.search(self.argv)

    @property
    def env_preserves_git_dir(self) -> bool | None:
        """True / False / None when no `env=` is passed (inherits, which preserves it).

        `env_source` is the env expression ALREADY RESOLVED through a local binding — see
        `_resolve_env`. Reading `self.env` here instead would refuse `write_time_gate`, whose env
        is environ-derived one line above the call and merely passed by name.
        """
        if self.env is None:
            return None
        return _preserves_git_dir(self.env_source)


def _module_roots(tree: ast.Module) -> set[str]:
    """Module-level names bound to a `Path(__file__)…parent` chain, whatever they are called."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and "__file__" in ast.unparse(node.value) \
                and "parent" in ast.unparse(node.value):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return names


def _resolve_env(tree: ast.Module, call: ast.Call, env: str | None) -> str | None:
    """`env` with a bare local name replaced by the expression last assigned to it.

    WHY THIS IS A STRENGTHENING AND NOT A NARROWING. `write_time_gate.staged_additions` builds an
    environ-derived env one line above its git call and passes it as `env=env`; refusing that is a
    false positive. The tempting fix — "a bare name is acceptable" — is a FAIL-OPEN, because
    `env=gitless` is also a bare name and is the exact defect. So the name is RESOLVED, and a name
    that cannot be resolved stays a violation.
    """
    if env is None or not env.isidentifier():
        return env
    best: str | None = None
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        if not (fn.lineno <= call.lineno <= (fn.end_lineno or fn.lineno)):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and node.lineno < call.lineno:
                if any(isinstance(t, ast.Name) and t.id == env for t in node.targets):
                    best = ast.unparse(node.value)
    return best  # None when nothing assigned it in scope -> refused, deliberately


def census_source(source: str, module: str) -> list[Callsite]:
    """Every git callsite in `source` whose `cwd=` is a module-root constant.

    Takes TEXT so a control can feed it a poisoned module: the refusal must be provable without
    editing a real gate, and a census that can only read the tree can only ever confirm the tree.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    roots = _module_roots(tree)
    if not roots:
        return []
    out: list[Callsite] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kwargs = {k.arg: ast.unparse(k.value) for k in node.keywords if k.arg}
        if "cwd" not in kwargs:
            continue
        base = re.sub(r"^str\(|\)$", "", kwargs["cwd"]).split(".")[0].split("/")[0].strip()
        if base not in roots:
            continue
        argv = ast.unparse(node.args[0]) if node.args else ""
        # argv[0] must be the git binary. A `pytest` child handed a gitless env is CORRECT and is
        # the reason this check is not simply "no gitless env near a gate".
        if not re.match(r"^[\(\[]\s*['\"]git['\"]", argv.strip()):
            continue
        env = kwargs.get("env")
        out.append(Callsite(module, node.lineno, kwargs["cwd"], argv, env,
                            _resolve_env(tree, node, env)))
    return out


def census(root: Path | None = None) -> list[Callsite]:
    base = root or PROJECT
    rows: list[Callsite] = []
    for sub in CENSUS_ROOTS:
        for path in sorted((base / sub).rglob("*.py")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            rows.extend(census_source(text, str(path.relative_to(base))))
    return rows


def violations(rows: list[Callsite]) -> list[Callsite]:
    """Git calls reading local state that are handed an env NOT derived from `os.environ`.

    FAILS CLOSED on the env question: an `env=` this cannot recognise as environ-derived counts as
    a violation, because the failure it guards is silent and green.
    """
    return [c for c in rows if c.reads_local_state and c.env_preserves_git_dir is False]


def hooks_path_is_absolute_elsewhere(base: Path | None = None) -> str | None:
    """`core.hooksPath` pointing OUTSIDE this tree, or None. Reported, never refused.

    Not a defect — it is why the gates run the MAIN tree's code against a LINKED worktree's index,
    and a reader who does not know that will mis-attribute the next gate bug to their own copy.
    """
    root = base or PROJECT
    try:
        done = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=str(root),
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    hooks = (done.stdout or "").strip()
    if not hooks or not Path(hooks).is_absolute():
        return None
    return hooks if not str(Path(hooks)).startswith(str(root)) else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="refuse when a git call reading local state is handed a GIT_DIR-less env")
    args = ap.parse_args(argv)

    rows = census()
    local = [c for c in rows if c.reads_local_state]
    print(f"git callsites with a module-root cwd: {len(rows)} "
          f"in {len({c.module for c in rows})} modules")
    print(f"  reading the index/working tree implicitly: {len(local)} "
          f"in {len({c.module for c in local})} modules")
    print(f"  naming their subject (immune by construction): {len(rows) - len(local)}")

    elsewhere = hooks_path_is_absolute_elsewhere()
    if elsewhere:
        print(f"  NOTE core.hooksPath={elsewhere} — gates run THAT tree's code; they gate the "
              f"right commit only via inherited GIT_DIR")

    bad = violations(rows)
    if not args.check:
        for c in sorted(local, key=lambda c: (c.module, c.lineno)):
            print(f"    {c.module}:{c.lineno} {sorted(c.subcommands)} cwd={c.cwd}")
        return 0
    if bad:
        print("\nREFUSED — a git call that reads the index/working tree is handed an environment "
              "that does not derive from os.environ, so GIT_DIR is not preserved. From a linked "
              "worktree it reads an EMPTY index and the check passes having examined nothing:")
        for c in bad:
            print(f"    {c.module}:{c.lineno} env={c.env}")
        return 1
    print("check: PASS (no git call reading local state is handed a GIT_DIR-less env)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
