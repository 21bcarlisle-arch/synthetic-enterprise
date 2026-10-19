"""Which registered bare world constants a production run actually reads.

The director, 19 Oct 2026 16:28: anchor the 446 bare world constants "in impact order, not
alphabetically". A constant cannot move a published figure unless the run that publishes reads it,
so reach is the first cut. Pre-registered at
`docs/staging/records/SEAT_PREREG_WHICH_OF_THE_446_BARE_WORLD_CONSTANTS_A_PRODUCTION_RUN_READS_2026-10-19.md`,
which states what a reading site is and the instrument's blind spots (string `getattr`, `globals()`,
dataclass defaults): each makes a reached constant read as unreached, never the reverse.

    python3 -m tools.world_constant_reach --sites            # static: reading sites per constant
    SIM_FAST_MODE=1 SE_FORK_WORKERS=1 python3 -m tools.world_constant_reach \\
        --run --report-end 2017-06-30 --out /tmp/reach.json  # one monitored run

The run is serial (`SE_FORK_WORKERS=1`) because `sys.monitoring` is per process: a forked trace
worker would read constants the monitor never sees.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

from tools.world_constant_anchors import PROJECT, registered

#: Where a reader of a world constant can live. Tests are not readers: a constant only a test reads
#: moves no published figure.
READER_SCOPE = ("simulation", "sim", "company", "saas", "tools")


def _module_of(rel: str) -> str:
    return rel[:-3].replace("/", ".").removesuffix(".__init__")


def _reader_files(root: Path):
    for package in READER_SCOPE:
        base = root / package
        if base.is_dir():
            yield from sorted(p for p in base.rglob("*.py") if "tests" not in p.parts)


class _Sites(ast.NodeVisitor):
    """Loads of the traced names in one file, each tagged by the scope it sits in."""

    def __init__(self, names: dict[str, str], attrs: dict[str, dict[str, str]]):
        self.names = names      # local name -> constant keys it carries
        self.attrs = attrs      # module alias (dotted) -> {attr -> constant keys}
        self.depth = 0          # function nesting
        self.cls = 0
        self.hits: list[tuple[str, int, str]] = []   # (key, line, kind)
        self._default_line: int | None = None

    def _kind(self) -> str:
        if self._default_line is not None:
            return "default"
        if self.depth:
            return "function"
        return "class" if self.cls else "module"

    def _record(self, keys: set[str], node: ast.AST) -> None:
        line = self._default_line if self._default_line is not None else node.lineno
        self.hits.extend((key, line, self._kind()) for key in keys)

    def _visit_function(self, node) -> None:
        for d in node.decorator_list:
            self.visit(d)
        body_line = node.body[0].lineno
        defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
        self._default_line = body_line
        for d in defaults:
            self.visit(d)
        self._default_line = None
        self.depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self.depth -= 1

    visit_FunctionDef = visit_AsyncFunctionDef = _visit_function

    def visit_Lambda(self, node):
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    def visit_ClassDef(self, node):
        self.cls += 1
        self.generic_visit(node)
        self.cls -= 1

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.names:
            self._record(self.names[node.id], node)

    def visit_Attribute(self, node):
        dotted = _dotted(node.value)
        if dotted is not None and dotted in self.attrs and node.attr in self.attrs[dotted]:
            self._record(self.attrs[dotted][node.attr], node)
            return
        self.generic_visit(node)


def _dotted(node: ast.AST) -> str | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _bindings(tree: ast.Module, module: str, traced: dict[str, dict[str, set[str]]]):
    """Local names and module aliases in this file that carry a traced constant."""
    names: dict[str, set[str]] = dict(traced.get(module, {}))
    attrs: dict[str, dict[str, set[str]]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            src = traced.get(node.module, {})
            for a in node.names:
                if a.name in src:
                    names[a.asname or a.name] = src[a.name]
                sub = f"{node.module}.{a.name}"
                if sub in traced:
                    attrs[a.asname or a.name] = traced[sub]
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name in traced:
                    attrs[a.asname or a.name] = traced[a.name]
    return names, attrs


def sites(root: Path | None = None, keys: set[str] | None = None) -> dict[str, list[dict]]:
    """Every reading site of every registered constant: `{key: [{file, line, kind}]}`.

    A module-level assignment computed from a traced name makes its targets traced too, to a
    fixpoint, so a constant read only through a derived table is still followed to its reader.
    """
    root = PROJECT if root is None else root
    keys = registered() if keys is None else keys
    parsed: dict[str, tuple[str, ast.Module]] = {}
    for path in _reader_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            parsed[rel] = (_module_of(rel), ast.parse(path.read_text(encoding="utf-8")))
        except SyntaxError:
            continue
    traced: dict[str, dict[str, set[str]]] = {}
    for key in keys:
        rel, name = key.split("::")
        traced.setdefault(_module_of(rel), {}).setdefault(name, set()).add(key)

    for _ in range(6):
        grew = False
        for rel, (module, tree) in parsed.items():
            names, attrs = _bindings(tree, module, traced)
            if not names and not attrs:
                continue
            for node in tree.body:
                if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                    continue
                v = _Sites(names, attrs)
                v.visit(node.value)
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                carried = {k for k, _, _ in v.hits}
                for t in targets:
                    if not (carried and isinstance(t, ast.Name)):
                        continue
                    have = traced.setdefault(module, {}).setdefault(t.id, set())
                    if not carried <= have:
                        have |= carried
                        grew = True
        if not grew:
            break

    out: dict[str, list[dict]] = {k: [] for k in keys}
    for rel, (module, tree) in parsed.items():
        names, attrs = _bindings(tree, module, traced)
        if not names and not attrs:
            continue
        v = _Sites(names, attrs)
        v.visit(tree)
        for key, line, kind in v.hits:
            if key in out:
                out[key].append({"file": rel, "line": line, "kind": kind})
    return out


#: Which run is monitored or perturbed. `published` is the entry the annual report takes
#: (`tools/run_annual_report.py` calls `run_phase4c_on_phase2b.main`): billing, the emergent
#: arrears that OVERWRITE every `bad_debt_gbp` the settlement loop accrued, and churn. `phase2b` is
#: the settlement loop alone, which is what this instrument ran first -- a constant read only at
#: billing reads as unreached there, and its bad-debt column is the transient in-loop accrual.
ENTRIES = ("published", "phase2b")


def _production_run(report_end: str | None, entry: str, tmp: Path) -> dict:
    """One run through `entry`, its coupled-gap ledger kept out of the tree. Returns phase 2b's
    result, which the published entry has already rewritten in place (emergent bad debt), with the
    published entry's bills attached as `_bills`."""
    if entry not in ENTRIES:
        raise ValueError(f"entry {entry!r} is not one of {ENTRIES}")
    from simulation import run_phase2b
    ledger = tmp / "coupled_gap_ledger.json"
    if entry == "phase2b":
        return run_phase2b.main(report_end=report_end, gap_ledger_path=ledger)
    from simulation import run_phase4c_on_phase2b as p4c
    inner = p4c.run_phase2b
    p4c.run_phase2b = lambda **kw: inner(gap_ledger_path=ledger, **kw)
    try:
        out = p4c.main(report_end=report_end)
    finally:
        p4c.run_phase2b = inner
    result = out["phase2b"]
    result["_bills"] = out.get("bills") or []
    return result


def run(report_end: str | None, out: Path, root: Path | None = None,
        entry: str = "published") -> dict:
    """One monitored production run; returns `{key: [executed function sites]}` and writes `out`."""
    root = PROJECT if root is None else root
    table = sites(root)
    wanted: dict[tuple[str, int], set[str]] = {}
    for key, rows in table.items():
        for r in rows:
            if r["kind"] in ("function", "default"):
                wanted.setdefault((str((root / r["file"]).resolve()), r["line"]), set()).add(key)
    hit: set[tuple[str, int]] = set()
    mon = sys.monitoring
    tool = mon.PROFILER_ID if mon.get_tool(mon.PROFILER_ID) is None else 4
    mon.use_tool_id(tool, "world_constant_reach")

    def _line(code, line):
        k = (code.co_filename, line)
        if k in wanted:
            hit.add(k)
        return mon.DISABLE

    mon.register_callback(tool, mon.events.LINE, _line)
    mon.set_events(tool, mon.events.LINE)
    import tempfile

    try:
        with tempfile.TemporaryDirectory() as tmp:
            _production_run(report_end, entry, Path(tmp))
    finally:
        mon.set_events(tool, 0)
        mon.free_tool_id(tool)
    reached: dict[str, list[str]] = {}
    for k in hit:
        for key in wanted[k]:
            reached.setdefault(key, []).append(f"{Path(k[0]).relative_to(root.resolve())}:{k[1]}")
    record = {
        "report_end": report_end,
        "entry": entry,
        "registered": len(table),
        "with_function_site": sum(1 for rows in table.values()
                                  if any(r["kind"] in ("function", "default") for r in rows)),
        "reached": {k: sorted(v) for k, v in sorted(reached.items())},
        "sites": table,
    }
    out.write_text(json.dumps(record, indent=1), encoding="utf-8")
    return record


def _scaled_source(path: Path, names: set[str], scale: float) -> str:
    """`path`'s source with every float literal in the named module-level assignments scaled.

    A value in [0, 1] stays in [0, 1] (a share or a probability scaled past 1 is a refusal, not a
    sensitivity), and a container whose floats sum to one moves mass rather than scaling. Integers
    are left alone: the population is defined by its floats.
    """
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    edits = []
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target, value = node.target, node.value
        else:
            continue
        if not (isinstance(target, ast.Name) and target.id in names):
            continue
        floats = [c for c in ast.walk(value) if isinstance(c, ast.Constant)
                  and isinstance(c.value, float) and c.lineno == c.end_lineno]
        total = sum(c.value for c in floats)
        if len(floats) > 1 and abs(total - 1.0) < 0.01 and all(c.value >= 0 for c in floats):
            # A DISTRIBUTION: scaling every weight is a no-op once it is normalised, so move mass
            # onto the first entry and take it from the rest in proportion.
            first = min(floats[0].value * scale, 1.0)
            rest = (1.0 - first) / (total - floats[0].value) if total > floats[0].value else 0.0
            values = [first] + [c.value * rest for c in floats[1:]]
        else:
            values = [min(c.value * scale, 1.0) if 0.0 <= c.value <= 1.0 else c.value * scale
                      for c in floats]
        for c, v in zip(floats, values):
            edits.append((c.lineno, c.col_offset, c.end_col_offset, repr(v)))
    for ln, a, b, text in sorted(edits, reverse=True):
        row = lines[ln - 1]
        lines[ln - 1] = row[:a] + text + row[b:]
    return "".join(lines)


def _figures(result: dict) -> dict:
    """What a run publishes, summed: every numeric field over the settled records, plus counts."""
    sums: dict[str, float] = {}
    for r in result.get("all_records") or []:
        for k, v in r.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                sums[k] = sums.get(k, 0.0) + float(v)
    out = {f"sum:{k}": round(v, 6) for k, v in sums.items()}
    out["records"] = len(result.get("all_records") or [])
    bills = result.get("_bills") or []
    if isinstance(bills, dict):  # keyed by account
        bills = [b for v in bills.values() for b in (v if isinstance(v, list) else [v])]
    if bills:
        out["bills"] = len(bills)
        bsums: dict[str, float] = {}
        for b in bills:
            for k, v in (b.items() if isinstance(b, dict) else ()):
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    bsums[k] = bsums.get(k, 0.0) + float(v)
        out.update({f"bills:{k}": round(v, 6) for k, v in bsums.items()})
    out["churned_billing_accounts"] = len(result.get("churned_billing_accounts") or [])
    out["svt_departures"] = len(result.get("svt_departures") or [])
    for k in ("total_gross", "total_capital", "total_bad_debt"):
        if isinstance(result.get(k), (int, float)):
            out[k] = round(float(result[k]), 6)
    return out


def arm(keys: list[str], scale: float, report_end: str | None, out: Path,
        root: Path | None = None, entry: str = "published") -> dict:
    """One production run with the named constants' floats scaled, served from patched source.

    The patch is applied at import by a meta-path finder, so every binding -- a derived table, a
    `from M import NAME` copy, a default argument -- sees the scaled value, which patching the
    module attribute after import would not. An empty `keys` is the baseline arm.
    """
    import importlib.abc
    import importlib.util
    import tempfile

    root = PROJECT if root is None else root
    by_module: dict[str, set[str]] = {}
    for key in keys:
        rel, name = key.split("::")
        by_module.setdefault(rel, set()).add(name)
    patched = {_module_of(rel): (root / rel, _scaled_source(root / rel, names, scale))
               for rel, names in by_module.items()}
    for mod in patched:
        if mod in sys.modules:
            raise RuntimeError(f"{mod} already imported; an arm must run in a fresh process")

    class _Loader(importlib.abc.SourceLoader):
        def __init__(self, path, text):
            self.path, self.text = path, text

        def get_filename(self, fullname):
            return str(self.path)

        def get_data(self, path):
            return self.text.encode("utf-8")

    class _Finder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            if fullname in patched:
                p, text = patched[fullname]
                return importlib.util.spec_from_file_location(fullname, p, loader=_Loader(p, text))
            return None

    sys.meta_path.insert(0, _Finder())
    error = None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            figures = _figures(_production_run(report_end, entry, Path(tmp)))
    except Exception as exc:  # a refusal under the perturbation is itself the reading
        figures, error = {}, f"{type(exc).__name__}: {exc}"[:500]
    record = {"keys": keys, "scale": scale, "report_end": report_end, "entry": entry,
              "figures": figures, "error": error}
    out.write_text(json.dumps(record, indent=1), encoding="utf-8")
    return record


def _main() -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sites", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--report-end", default=None)
    ap.add_argument("--out", type=Path, default=Path("/tmp/world_constant_reach.json"))
    ap.add_argument("--arm", default=None,
                    help="comma-separated keys to scale ('' is the baseline arm)")
    ap.add_argument("--scale", type=float, default=1.1)
    ap.add_argument("--entry", choices=ENTRIES, default="published")
    args = ap.parse_args()
    if args.arm is not None:
        keys = [k for k in args.arm.split(",") if k]
        rec = arm(keys, args.scale, args.report_end, args.out, entry=args.entry)
        print(f"arm {len(keys)} keys x{args.scale}: error={rec['error']}  -> {args.out}")
        return 0
    if args.run:
        rec = run(args.report_end, args.out, entry=args.entry)
        print(f"registered {rec['registered']}  with a function site {rec['with_function_site']}  "
              f"reached {len(rec['reached'])}  -> {args.out}")
        return 0
    table = sites()
    kinds: dict[str, int] = {}
    for rows in table.values():
        best = ("function" if any(r["kind"] in ("function", "default") for r in rows)
                else rows[0]["kind"] if rows else "none")
        kinds[best] = kinds.get(best, 0) + 1
    print(f"registered {len(table)}: " + "  ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
