"""Read a Python file as CODE rather than as text, for controls that scan source by substring.

WHY THIS EXISTS. A control that walks `*.py` and asks `"token" in text` cannot tell a line that
DOES the thing from a comment that DESCRIBES it, and it is wrong in both directions at once:

  * PROSE READ AS CODE. An accurate comment fires the control. Every widening of
    `test_the_only_thing_that_invokes_it_is_the_declared_schedule` was paid for by one --
    `fork_salvage` reading a predicate, `delivery_lane.hand_off_focus` explaining the stand-down,
    and finally `launch_long_job.py` naming the seat-executor cgroup as the worked example of a
    teardown, which left that control RED AT HEAD for eight days. Each fix corrected the instance
    and left the class, so the next accurate comment re-opened it.

  * CODE READ AS PROSE, which is the dangerous half. `"-m background.seat_executor"` is never
    contiguous in `["python3", "-m", "background.seat_executor"]`, so the one control between this
    repository and a second unattended writer was FAIL-OPEN against the exact mutation its own
    docstring offered as proof it worked. Every subprocess call in this repo is written as an argv
    list; a substring check is blind to all of them.

  * A NEGATED check inverts the first direction into the second. `"arrears_ledger" not in text`
    treats a module that merely MENTIONS the shared reader in a comment as one that uses it, so a
    comment is enough to hide a real offender.

WHAT `searchable()` RETURNS. The file's own bytes with comments and bare string expressions
blanked to spaces -- offsets, line numbers and quote style all preserved, so `in` and
`.splitlines()` at the call site behave exactly as before -- followed by every all-string
list/tuple rejoined with spaces, so an argv literal reads the way the shell would receive it.

FAIL-CLOSED. Source that will not parse returns the ORIGINAL text: we did not manage to look, and
that is never evidence of absence. The reading is then exactly today's, never narrower.

`imported_modules()` is the other half, for the import walls: `from sim.scenario import (spine)`
and a line-broken `from x import (\n    y)` are invisible to any single-line spelling, and the
import graph is a property of the AST rather than of how someone typed it.
"""

from __future__ import annotations

import ast
import io
import tokenize

__all__ = ["searchable", "code_text", "code_strings", "imported_modules", "prose_string_ids"]


def prose_string_ids(tree: ast.AST) -> set[int]:
    """The `id()`s of bare string-expression Constants in an already-parsed tree.

    The same discrimination as `searchable`, for a caller that is already walking the AST and
    wants to skip prose nodes in place rather than search text. `tools/launch_shape_census.py`
    walks Constants looking for a transient-unit spelling and must not count the docstring in
    `tools/run_arms_rerun.py` that recites the shell command it replaced.
    """
    return {id(n.value) for n in ast.walk(tree)
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
            and isinstance(n.value.value, str)}


def _blank(source: str, regions: list[tuple[int, int, int, int]]) -> str:
    """Overwrite each (lineno, col, end_lineno, end_col) span with spaces, keeping newlines.

    Offsets are preserved rather than deleted so that a caller which reports `path:lineno` still
    reports the line the token is really on. `col` offsets are Python's: byte-ish columns into the
    UTF-8 line for tokenize, and the same convention for `ast`, so both are applied per line.
    """
    lines = source.splitlines(keepends=True)
    for start_row, start_col, end_row, end_col in regions:
        for row in range(start_row, end_row + 1):
            idx = row - 1
            if idx < 0 or idx >= len(lines):
                continue
            line = lines[idx]
            body = line.rstrip("\r\n")
            tail = line[len(body):]
            lo = start_col if row == start_row else 0
            hi = end_col if row == end_row else len(body)
            lo = max(0, min(lo, len(body)))
            hi = max(lo, min(hi, len(body)))
            lines[idx] = body[:lo] + (" " * (hi - lo)) + body[hi:] + tail
    return "".join(lines)


def _comment_regions(source: str) -> list[tuple[int, int, int, int]]:
    """Comment spans. A tokenize failure yields none -- we blank less, never more."""
    out: list[tuple[int, int, int, int]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                out.append((tok.start[0], tok.start[1], tok.end[0], tok.end[1]))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return []
    return out


def _prose_string_regions(tree: ast.AST) -> list[tuple[int, int, int, int]]:
    """Bare string expressions: module/class/function docstrings and free-standing strings.

    A bare `Expr(Constant(str))` is evaluated and discarded -- it cannot invoke, import or read
    anything, so dropping it costs no coverage. Strings that DO reach code live in an assignment,
    a call argument or a collection, and none of those is a bare `Expr`.
    """
    prose = prose_string_ids(tree)
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and id(node) in prose):
            continue
        end_row = getattr(node, "end_lineno", None)
        end_col = getattr(node, "end_col_offset", None)
        if end_row is None or end_col is None:
            continue
        out.append((node.lineno, node.col_offset, end_row, end_col))
    return out


def _argv_joins(tree: ast.AST) -> list[str]:
    """Every all-string list/tuple, rejoined with spaces -- the shell's view of an argv literal.

    APPENDED rather than substituted, because the list's own spelling stays searchable too: a
    control looking for `"background.seat_executor"` must still find it in the element, and one
    looking for `"-m background.seat_executor"` must now find it in the join.
    """
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Tuple)):
            parts = [e.value for e in node.elts
                     if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            if parts and len(parts) == len(node.elts):
                out.append(" ".join(parts))
    return out


def code_text(source: str) -> str | None:
    """The file as code: prose blanked, argv literals rejoined. None when it will not parse."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return None
    blanked = _blank(source, _comment_regions(source) + _prose_string_regions(tree))
    joins = _argv_joins(tree)
    if not joins:
        return blanked
    return blanked + "\n" + "\n".join(joins) + "\n"


def code_strings(tree: ast.AST) -> list[str]:
    """Every string a running file could hand to a shell, as SEPARATE items. No prose.

    The list-shaped reading, for a caller that searches each string on its own rather than
    searching one blob. `searchable()` is the blob form, and the two are not interchangeable: a
    pattern can straddle two adjacent constructs in the blob and match nothing any running line
    could produce, which for a wall is a false red that gets the wall widened.

    Both halves of `code_text` are here, from the same primitives: prose dropped via
    `prose_string_ids`, argv lists rejoined via `_argv_joins`, and the list's own elements kept
    alongside the join so a caller looking for a bare module name still finds it.

    THIS WAS A THIRD PRIVATE COPY until 2026-09-08 -- `_python_strings_and_argvs` inside
    `tests/background/test_the_seat_executor_stands_down.py`, written independently on the day
    `tools/launch_shape_census.py` gave up its own. Its version dropped only DOCSTRINGS (a body's
    first statement); this drops every bare `Expr(Constant(str))`, which is a superset and costs no
    coverage for the same reason -- a discarded expression cannot invoke, import or read anything.
    """
    prose = prose_string_ids(tree)
    out = _argv_joins(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and id(node) not in prose:
            out.append(node.value)
    return out


def searchable(source: str) -> str:
    """`code_text`, falling back to the original text when the source will not parse.

    The fallback is the fail-closed direction on purpose: an unparseable file gets exactly the
    reading it gets today, so adopting this function can never make a control quieter than it was.
    """
    return code_text(source) or source


def imported_modules(source: str) -> set[str] | None:
    """Dotted module names this source imports, however the import is spelled.

    `import a.b.c`, `from a.b import c`, `from a.b import (c)` and a line-broken parenthesised
    list all yield `a.b` and `a.b.c` alike, so a control can ask about the module rather than
    about somebody's line breaks. Relative imports yield their named suffixes only -- resolving a
    leading dot needs the importing file's package, which a text-level control does not have.
    None when the source will not parse.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return None
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
                out.update(_prefixes(alias.name))
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if base:
                out.add(base)
                out.update(_prefixes(base))
            for alias in node.names:
                out.add(f"{base}.{alias.name}" if base else alias.name)
    return out


def _prefixes(dotted: str) -> set[str]:
    """`a.b.c` -> {`a`, `a.b`}. A wall keyed to a package must see the package in a deeper import."""
    parts = dotted.split(".")
    return {".".join(parts[:i]) for i in range(1, len(parts))}
