#!/usr/bin/env python3
"""
REUSE: tools/seam_door_call_conformance.py
CLASS: CUSTOM
INDEX: searched "signature", "call site", "conformance", "seam", "arity", "keyword argument".
       Nothing asks this question. `tools/internal_seam_verifier.py` and
       `tests/architecture/test_epistemic_wall_ratchet.py` both guard WHICH EDGES MAY EXIST --
       may this module import that one -- and are blind to whether an edge that is allowed still
       type-checks. `tools/annual_report_import_ratchet.py` freezes an edge COUNT. None of the
       three reads a signature. The shape reused, deliberately and visibly, is the annual-report
       ratchet's: AST-only, frozen at zero, fail-closed on an unreadable tree, so a reader who
       knows one knows this. What is NOT reused is its transitive import walk -- this check is
       call-site-local by construction, because the defect it exists for is a call, not an edge.

A DOOR MAY CHANGE ITS SIGNATURE. ITS CALLERS MAY NOT BE LEFT BEHIND.

WHY THIS EXISTS (2026-08-19, PRODUCER STARVATION, 8 consecutive failed simulation runs over 0.7h,
nothing new reaching the live site in that window):

    TypeError: replacement_cost_avoided_gbp() got an unexpected keyword argument 'counted_in_guard'

KNIFE3 step 39 cut a policy bool out of a company door -- `company/interfaces/growth_desk.py::
replacement_cost_avoided_gbp` -- and moved its resolution behind the seam. The door changed, its
own seam test changed with it, and the world-side caller in `simulation/run_phase2b.py` was left
spelling the removed keyword. Every run of the annual report died at that line, 55s in.

WHAT COULD SEE IT AND DID NOT. Nothing, and the reason is structural rather than careless:
  * The pre-commit gate selects tests by FILENAME STEM, so editing `company/interfaces/
    growth_desk.py` runs `tests/company/interfaces/test_growth_desk_seam.py` -- which was updated
    in the same breath and passed -- and never runs anything under `simulation/`. THE FILE THAT
    BREAKS IS NEVER THE FILE THAT IS EDITED, which is the whole shape of this class.
  * The epistemic wall ratchet and the internal seam verifier both permit this call. It is a
    LEGAL edge. Legality is the only question either of them asks.
  * Python binds arguments at CALL time, so an import of either module succeeds and the mismatch
    is invisible to every import-shaped control in the tree. It surfaces only when that specific
    branch executes -- here, inside the term loop of a 55-second run.

MEASURED AGAINST THE REAL DEFECT, not only a fixture. Assembled into a tree, the door as it now
stands plus `simulation/run_phase2b.py` AS IT WAS, this checker reports:

    simulation/run_phase2b.py:1376: replacement_cost_avoided_gbp(*, segment)
      (defined company/interfaces/growth_desk.py:143)
      -- got an unexpected keyword argument 'counted_in_guard'

in 3 seconds, against the 55 seconds each of the 8 failed runs took to say the same thing.

So this control walks CALL SITES, not edges, and it is repo-wide on purpose: the reader that
crashed is rarely the only one. Run it, or let `tests/architecture/test_seam_door_call_
conformance.py` run it (it is in the pre-commit gate's ALWAYS list, for the reason above -- a
per-file selector fires it when this file is edited, the case that needs it least, and stays
silent when a door signature moves, the only case it exists for).

    python3 -m tools.seam_door_call_conformance

Exit 0 = every call site binds. Exit 1 = at least one stale caller. Exit 2 = the scan itself is
broken (no doors found, unreadable tree).

DESIGN STANCE (R15 -- this control must be able to FAIL):
  * NOT A TAUTOLOGY. The signature comes from the DEF in `company/interfaces/**`; the argument
    shape comes from the CALL, anywhere in the repo. Two files, two ASTs, and the check is the
    disagreement between them. Neither side can be derived from the other.
  * NOT FAIL-OPEN. Zero doors found RAISES (rc=2): a clean tree and an unscanned tree are
    indistinguishable from the exit code otherwise, and this control exists precisely to tell
    those apart. An unparseable file under a scanned root RAISES rather than being skipped.
  * NOT FAIL-SILENT. There is no suppression comment and no ignore list a stale caller could be
    hushed with. `_KNOWN_INTENTIONAL` below is empty, and is the only escape hatch: a call that
    deliberately mis-binds (a test asserting TypeError, say) must be named there in the tree,
    where a reader sees it, not annotated at the call.
  * The mutation test in `tests/architecture/test_seam_door_call_conformance.py` plants the exact
    2026-08-19 defect -- a removed keyword still spelled by a caller -- in a fixture tree and
    asserts this checker flags it, and plants the REPAIRED call and asserts it does not.

WHAT THIS DELIBERATELY DOES NOT DO. It checks ARITY AND NAMES, never types: `f(segment=3)` where
the door wants a `str` passes here, and belongs to a type checker. It resolves calls through
imports only, never through a value -- `getattr(door, name)(...)` and a door stored in a dict are
both invisible, and pretending otherwise by string-matching the name would over-attribute (see
the substring-census class). What it covers is the shape the defect actually had, which is the
shape a rename or a parameter removal always has: a direct, imported, spelled-out call.
"""

from __future__ import annotations

import argparse
import ast
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The doors. Every public module-level function defined under here is a seam a caller elsewhere
# may bind against.
DOOR_ROOT = "company/interfaces"

# Directories that are not this repo's source: other checkouts, caches, vendored trees.
_SKIP_PARTS = frozenset({".git", ".claude", "__pycache__", "node_modules", ".venv", "venv"})

# THE ONE EXEMPTION, and it is a SHAPE rather than a list. A call inside `with pytest.raises(
# TypeError):` does not bind ON PURPOSE -- the mis-binding IS the assertion. `company/interfaces/
# wall_protocol.py::encode_request` has exactly such a test, which asserts its payload codec has
# no default, and calling that a stale caller would be reading the control backwards.
#
# It is not a hole. To hide a real stale call behind it you must wrap the call in an assertion
# that it raises TypeError -- at which point the crash is PROVEN rather than hidden, and the
# caller is a test of the signature, not a consumer of the door. Only `TypeError` exempts;
# `pytest.raises(ValueError)` around a mis-bound call is still a finding, because that test would
# be claiming something the interpreter will never let it reach.
_EXEMPTING_EXCEPTION = "TypeError"

# The last-resort escape hatch, for a deliberate mis-bind that is not the shape above. Named
# here, in the tree, rather than annotated at the call -- an inline suppression comment is how a
# control goes fail-silent one line at a time. Entries are (path, lineno, door-name), and the
# lineno churn is the POINT: an entry here is meant to be uncomfortable to keep.
# EMPTY, and measured empty: at the commit that introduced this file, the only mis-binding call
# in the whole repo was the `pytest.raises(TypeError)` one above.
_KNOWN_INTENTIONAL: tuple[tuple[str, int, str], ...] = ()

# A stand-in for "an argument was supplied here". Binding cares about arity and names; the value
# is never read.
_SUPPLIED = object()


@dataclass(frozen=True)
class Door:
    """One public function defined on the company side of the seam."""

    module: str
    name: str
    signature: inspect.Signature
    path: str
    lineno: int


@dataclass(frozen=True)
class StaleCall:
    """A call site whose arguments no longer bind to the door it names."""

    path: str
    lineno: int
    door: Door
    reason: str

    def render(self) -> str:
        return (
            f"{self.path}:{self.lineno}: {self.door.name}{self.door.signature} "
            f"(defined {self.door.path}:{self.door.lineno}) -- {self.reason}"
        )


def _signature_of(node: ast.FunctionDef | ast.AsyncFunctionDef) -> inspect.Signature:
    """The def's signature, as `inspect` understands binding.

    Defaults are carried as PRESENCE only (the sentinel), because a default's VALUE never changes
    whether a call binds -- only whether the parameter may be omitted.
    """
    a = node.args
    params: list[inspect.Parameter] = []

    n_pos = len(a.posonlyargs) + len(a.args)
    pos_defaults = [None] * (n_pos - len(a.defaults)) + [_SUPPLIED] * len(a.defaults)
    for arg, default in zip(a.posonlyargs, pos_defaults[: len(a.posonlyargs)]):
        params.append(_param(arg.arg, inspect.Parameter.POSITIONAL_ONLY, default))
    for arg, default in zip(a.args, pos_defaults[len(a.posonlyargs) :]):
        params.append(_param(arg.arg, inspect.Parameter.POSITIONAL_OR_KEYWORD, default))

    if a.vararg:
        params.append(inspect.Parameter(a.vararg.arg, inspect.Parameter.VAR_POSITIONAL))
    for arg, default_node in zip(a.kwonlyargs, a.kw_defaults):
        default = _SUPPLIED if default_node is not None else None
        params.append(_param(arg.arg, inspect.Parameter.KEYWORD_ONLY, default))
    if a.kwarg:
        params.append(inspect.Parameter(a.kwarg.arg, inspect.Parameter.VAR_KEYWORD))

    return inspect.Signature(params)


def _param(name: str, kind, default) -> inspect.Parameter:
    if default is None:
        return inspect.Parameter(name, kind)
    return inspect.Parameter(name, kind, default=default)


def _module_name(path: Path, root: Path) -> str:
    return ".".join(path.relative_to(root).with_suffix("").parts)


def _python_files(root: Path):
    for path in sorted(root.rglob("*.py")):
        if any(part in _SKIP_PARTS for part in path.relative_to(root).parts):
            continue
        yield path


def _parse(path: Path, root: Path) -> ast.Module:
    """FAIL-CLOSED: a file that cannot be read or parsed stops the scan."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        raise RuntimeError(
            f"{path.relative_to(root)}: cannot be scanned ({exc}). An unscannable file is an "
            "UNCHECKED file, not a clean one."
        ) from exc


def collect_doors(root: Path = ROOT) -> dict[tuple[str, str], Door]:
    """Every public module-level function defined under `company/interfaces/`."""
    door_root = root / DOOR_ROOT
    if not door_root.is_dir():
        raise RuntimeError(
            f"{DOOR_ROOT} does not exist under {root}. There is no seam to check, which is a "
            "broken scan and not a clean one."
        )

    doors: dict[tuple[str, str], Door] = {}
    for path in _python_files(door_root):
        module = _module_name(path, root)
        for node in _parse(path, root).body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            doors[(module, node.name)] = Door(
                module=module,
                name=node.name,
                signature=_signature_of(node),
                path=str(path.relative_to(root)),
                lineno=node.lineno,
            )
    if not doors:
        raise RuntimeError(
            f"no public functions found under {DOOR_ROOT}. Zero doors is indistinguishable from "
            "zero doors CHECKED, so this is a scan failure."
        )
    return doors


def _dotted(node: ast.expr) -> str | None:
    """`a.b.c` -> "a.b.c"; anything computed -> None."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def _aliases(tree: ast.Module) -> tuple[dict[str, tuple[str, str]], dict[str, str]]:
    """What this file calls the doors it imported.

    Returns (bare-name -> (module, door-name), module-alias -> module). Imports nested inside
    functions count: this repo defers most seam imports to the call site.
    """
    by_name: dict[str, tuple[str, str]] = {}
    by_module: dict[str, str] = {}
    prefix = DOOR_ROOT.replace("/", ".")

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            if node.module == prefix:
                # from company.interfaces import growth_desk [as gd]
                for alias in node.names:
                    by_module[alias.asname or alias.name] = f"{prefix}.{alias.name}"
            elif node.module.startswith(prefix + "."):
                for alias in node.names:
                    by_name[alias.asname or alias.name] = (node.module, alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == prefix or alias.name.startswith(prefix + "."):
                    # `import company.interfaces.growth_desk` binds the ROOT name, but the call
                    # is spelled with the full dotted path, so key on that.
                    by_module[alias.asname or alias.name] = alias.name
    return by_name, by_module


def _resolve(call: ast.Call, by_name, by_module) -> tuple[str, str] | None:
    func = call.func
    if isinstance(func, ast.Name):
        return by_name.get(func.id)
    dotted = _dotted(func)
    if dotted is None or "." not in dotted:
        return None
    module_alias, _, attr = dotted.rpartition(".")
    module = by_module.get(module_alias)
    return (module, attr) if module else None


def _asserted_type_errors(tree: ast.Module) -> set[int]:
    """Calls whose failure to bind is the assertion -- see `_EXEMPTING_EXCEPTION`."""
    exempt: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.With, ast.AsyncWith)):
            continue
        for item in node.items:
            expr = item.context_expr
            if not isinstance(expr, ast.Call):
                continue
            dotted = _dotted(expr.func)
            if dotted is None or dotted.rpartition(".")[2] != "raises":
                continue
            expected = expr.args[0] if expr.args else None
            names = expected.elts if isinstance(expected, ast.Tuple) else [expected]
            if not any(isinstance(n, ast.Name) and n.id == _EXEMPTING_EXCEPTION for n in names):
                continue
            for statement in node.body:
                for inner in ast.walk(statement):
                    if isinstance(inner, ast.Call):
                        exempt.add(id(inner))
    return exempt


def _bind_failure(call: ast.Call, signature: inspect.Signature) -> str | None:
    """The reason this call does not bind, or None."""
    positional = [_SUPPLIED for arg in call.args if not isinstance(arg, ast.Starred)]
    starred = len(positional) != len(call.args)

    keywords: dict[str, object] = {}
    double_starred = False
    for keyword in call.keywords:
        if keyword.arg is None:
            double_starred = True
        else:
            keywords[keyword.arg] = _SUPPLIED

    try:
        if starred or double_starred:
            # A spread may supply anything, so only OVER-supply is decidable: an unexpected
            # keyword or too many positionals still fails, a missing one is unknowable.
            signature.bind_partial(*positional, **keywords)
        else:
            signature.bind(*positional, **keywords)
    except TypeError as exc:
        return str(exc)
    return None


def find_stale_calls(root: Path = ROOT) -> list[StaleCall]:
    doors = collect_doors(root)
    stale: list[StaleCall] = []

    for path in _python_files(root):
        tree = _parse(path, root)
        by_name, by_module = _aliases(tree)
        if not by_name and not by_module:
            continue
        relative = str(path.relative_to(root))
        exempt = _asserted_type_errors(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or id(node) in exempt:
                continue
            resolved = _resolve(node, by_name, by_module)
            if resolved is None:
                continue
            door = doors.get(resolved)
            if door is None:
                continue
            reason = _bind_failure(node, door.signature)
            if reason is None:
                continue
            if (relative, node.lineno, door.name) in _KNOWN_INTENTIONAL:
                continue
            stale.append(StaleCall(relative, node.lineno, door, reason))
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[3])
    parser.add_argument("--root", default=str(ROOT), help="tree to scan (tests pass a fixture)")
    args = parser.parse_args(argv)

    try:
        stale = find_stale_calls(Path(args.root))
    except RuntimeError as exc:
        print(f"SCAN FAILED: {exc}", file=sys.stderr)
        return 2

    if stale:
        print(f"STALE SEAM CALLS: {len(stale)}")
        for call in stale:
            print(f"  {call.render()}")
        return 1
    print("PASS: every call to a company/interfaces door binds to its current signature.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
