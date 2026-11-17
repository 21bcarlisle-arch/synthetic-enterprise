"""Which modules read a data file through a path ASSEMBLED from parts, and so name no file at all.

`sim/scenario/spine.py` opens `base / f"{world_id}.yaml"`, where `base` is `CURRICULUM_DIR`, which
is `Path(__file__).resolve().parent / "curriculum"`. No string in it names `history_replay.yaml`,
so the commit gate's data route (`pre_commit_test_gate.data_surface_tests`, which asks "which
module names this file") has no way back from that file to spine's tests. The 2026-11-17 citation
census found the real reader selected only because a test's docstring happened to name the file.

This answers the other question: for a staged data file in directory D, which non-test modules
JOIN an assembled path with the file's suffix ONTO an expression that resolves to D? Resolution is
static and shallow: constants, `/` chains, `os.path.join`, an f-string's leading parts, names
assigned anywhere in the module, `IfExp`/`or` branches, and the return values of the module's own
functions. A directory segment resolves against the repo root or any ancestor of the module's own
directory, which is what `Path(__file__).parent / "curriculum"` means.

Why joined-onto and not merely co-occurring: "names D somewhere and assembles some path somewhere"
reached 11,902 files over 93 modules, nearly all by coincidence. Joined-onto found 49 modules and
every hand-known reader (census: docs/staging/records/SEAT_PREREG_ASSEMBLED_PATH_READERS_CENSUS_2026-11-17.md).

Markdown is out of scope on purpose: markdown selection was narrowed to path-shaped strings for its
cost (`_names_it_outside_prose`), and the assembled markdown readers are the staging scanners.

Fails toward running in the gate's sense only for what it finds; a reader it cannot resolve (a
directory passed in from a caller, a path built in another module) is still invisible, and the
census record says so.
"""
from __future__ import annotations

import ast
import os
import subprocess
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_DEPTH = 12  # a `/` chain of four segments behind two names and a function is ten deep


def _assembled_suffix(node: ast.AST, suffix: str) -> bool:
    """Is this an f-string or `+` concatenation that ENDS in `suffix` with a variable part?"""
    if isinstance(node, ast.JoinedStr) and node.values:
        last = node.values[-1]
        return (isinstance(last, ast.Constant) and isinstance(last.value, str)
                and last.value.endswith(suffix)
                and any(isinstance(v, ast.FormattedValue) for v in node.values))
    return (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
            and isinstance(node.right, ast.Constant) and node.right.value == suffix)


def _resolver(tree: ast.AST):
    assigns: dict[str, list[ast.AST]] = {}
    returns: dict[str, list[ast.AST]] = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    assigns.setdefault(t.id, []).append(n.value)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value:
            assigns.setdefault(n.target.id, []).append(n.value)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            returns.setdefault(n.name, []).extend(
                r.value for r in ast.walk(n) if isinstance(r, ast.Return) and r.value is not None)

    def tails(e: ast.AST, depth: int = 0) -> set[str]:
        """The literal path tails this expression can evaluate to; an unknowable root is ''."""
        if depth > _DEPTH:
            return set()
        nxt = depth + 1
        if isinstance(e, ast.Constant) and isinstance(e.value, str):
            return {e.value.strip("/")}
        if isinstance(e, ast.Name):
            return set().union(*(tails(v, nxt) for v in assigns.get(e.id, [])))
        if isinstance(e, ast.IfExp):
            return tails(e.body, nxt) | tails(e.orelse, nxt)
        if isinstance(e, ast.BoolOp):
            return set().union(*(tails(v, nxt) for v in e.values))
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Div):
            right = tails(e.right, nxt)
            left = tails(e.left, nxt) or {""}
            return {f"{a}/{b}".strip("/") for a in left for b in right}
        if isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Attribute) and f.attr == "join":
                return _join([tails(a, nxt) for a in e.args])
            if isinstance(f, ast.Attribute) and f.attr in ("resolve", "absolute"):
                return tails(f.value, nxt)
            if isinstance(f, ast.Name) and f.id in ("Path", "PurePath"):
                return _join([tails(a, nxt) for a in e.args])
            if isinstance(f, ast.Name) and f.id in returns:
                return set().union(*(tails(v, nxt) for v in returns[f.id]))
        return set()

    return tails


def _join(parts: list[set[str]]) -> set[str]:
    acc = {""}
    for p in parts:
        acc = {f"{a}/{b}".strip("/") for a in acc for b in (p or {""})}
    return acc


def directories_read(module: str, suffix: str, source: str | None = None) -> set[str]:
    """Repo-relative directories this module joins an assembled `*suffix` path onto."""
    try:
        tree = ast.parse(source if source is not None
                         else (ROOT / module).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
        return set()
    tails = _resolver(tree)
    segs: set[str] = set()
    for n in ast.walk(tree):
        if (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)
                and _assembled_suffix(n.right, suffix)):
            segs |= tails(n.left)
        elif isinstance(n, ast.JoinedStr) and _assembled_suffix(n, suffix):
            # f"{WEATHER_DATA_DIR}/{customer_id}.csv": the directory is the text before the last
            # variable part, up to its last slash.
            k = max(i for i, v in enumerate(n.values) if isinstance(v, ast.FormattedValue))
            acc = {""}
            for v in n.values[:k]:
                part = ({v.value} if isinstance(v, ast.Constant) else tails(v.value)) or set()
                acc = {a + b for a in acc for b in part}
            segs |= {a.rsplit("/", 1)[0] for a in acc if "/" in a}
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if (n.func.attr == "join" and len(n.args) >= 2
                    and _assembled_suffix(n.args[-1], suffix)):
                segs |= _join([tails(a) for a in n.args[:-1]])
            elif (n.func.attr in ("glob", "rglob") and n.args
                  and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)
                  and n.args[0].value.endswith(suffix) and "/" not in n.args[0].value):
                segs |= tails(n.func.value)
            elif (n.func.attr == "with_suffix" and n.args
                  and isinstance(n.args[0], ast.Constant) and n.args[0].value == suffix
                  and isinstance(n.func.value, ast.BinOp) and isinstance(n.func.value.op, ast.Div)):
                segs |= tails(n.func.value.left)
    anchors = [""]
    d = os.path.dirname(module)
    while d:
        anchors.append(d)
        d = os.path.dirname(d)
    return {f"{a}/{s}".strip("/") for s in segs if s.strip("/") for a in anchors}


@lru_cache(maxsize=256)
def readers_of_directory(directory: str, suffix: str,
                         prefixes: tuple[str, ...]) -> tuple[str, ...]:
    """Non-test modules under `prefixes` that join an assembled `*suffix` path onto `directory`.
    Candidates come from `git grep` over the index for files holding BOTH the directory's last
    segment, which every resolvable spelling of it contains as a literal, and the suffix."""
    leaf = directory.rsplit("/", 1)[-1]
    r = subprocess.run(["git", "grep", "-l", "--fixed-strings", "-I", "--all-match",
                        "-e", leaf, "-e", suffix, "--", "*.py"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode > 1:
        return ()
    out = []
    for mod in (ln.strip() for ln in r.stdout.splitlines()):
        if (not mod.startswith(prefixes) or mod.startswith("tests/")
                or Path(mod).name.startswith("test_")):
            continue
        if directory in directories_read(mod, suffix):
            out.append(mod)
    return tuple(sorted(out))


def readers_of(path: str, prefixes: tuple[str, ...]) -> tuple[str, ...]:
    """Modules under `prefixes` that read this data file through an assembled path. Markdown is
    out of scope."""
    p = Path(path)
    if not p.suffix or p.suffix.lower() in (".py", ".md"):
        return ()
    return readers_of_directory(str(p.parent), p.suffix, tuple(prefixes))


if __name__ == "__main__":
    import sys

    from tools.pre_commit_test_gate import CODE_PREFIXES
    for arg in sys.argv[1:]:
        print(arg, "->", ", ".join(readers_of(arg, CODE_PREFIXES)) or "(none)")
