#!/usr/bin/env python3
"""
REUSE: tools/file_scope_generated_paths.py
CLASS: CUSTOM
INDEX: searched "file_scope", "generated", "derived artefact", "output path", "starvation".
       Two rows are genuinely close and neither covers this.
       `background/derived_artefact_register.py` knows which `docs/design/*.md` files are
       RENDERED rather than authored, and its AST segment-join technique is REUSED here rather
       than reinvented -- the trick of reading `PROJECT / "site" / "data" / "x.json"` as string
       constants inside one assignment, without importing the module, is its idea and the
       comment explaining why (importing every candidate to find out whether it is a candidate
       is slow and a side-effect risk) applies unchanged. It is not extended because its
       REGISTER is a hand-maintained tuple of three design documents with a completeness test,
       and this needs a 116-artefact set derived across five trees; folding a derived set into
       a curated one would break the completeness test that makes the curated half trustworthy.
       `background/supervisor.py::_unmerged_work_paths` is the mechanism whose CONSEQUENCE this
       gate exists to prevent, and deliberately not touched: it is correct, it prevented a real
       double-implementation on 2026-07-30, and the defect is not in the guard but in what the
       map declares to it. Fixing a correct guard to tolerate bad input would be the wrong end.

A `file_scope` MAY NOT NAME A PATH A GENERATOR WRITES -- the class fix (R10) for the defect
that starved G13 for eight days.

THE INSTANCE, 2026-08-19. `G13_projection_consumers` sat at stage `build`, unblocked, with its
dependency satisfied, and was never once drawn. Not blocked: its `file_scope` named `site/data/`,
the PUBLISHER'S OUTPUT directory, which is rewritten every cycle and therefore permanently
carries uncommitted changes. `supervisor._unmerged_work_paths` reported that from git reality --
correctly -- and the BUILD draw deprioritised the atom on every tick, silently, for eight days.
Full record: docs/staging/WORKER_FINDING_A_FILE_SCOPE_NAMING_A_GENERATED_DIRECTORY_IS_
PERMANENTLY_SELF_BLOCKING_2026-08-19.md.

WHY AN INSTANCE FIX IS NOT A CLOSURE (R10). Narrowing G13's scope fixes G13. It does not stop the
next atom naming `site/data/`, and there are TEN others carrying the same declaration today --
one of which, `OPS3_first_post_ruling_publish`, was independently hit by a different control on
the same day, which is what a class looks like when only its instances are being treated.

WHAT THIS GATE IS NOT SAYING. It is not a purity rule about outputs, and the message it prints
says so. An atom that owns a generator has a real argument for declaring what that generator
writes. The objection is the CONSEQUENCE: whatever the intent, the declaration makes the atom
permanently invisible to its own build lane. The gate names the starvation, not a style.

FAIL-CLOSED: an oracle that cannot be computed RAISES. A gate that cannot see which paths are
generated must never report a clean tree -- that reading is indistinguishable from a healthy one
and would restore exactly the silence this exists to end.

RATCHET, not a wall. Eleven declarations are FROZEN as known debt so the tree keeps moving. A
NEW one fails the commit. A frozen entry that has been REPAIRED also fails, so the freeze can
only shrink -- otherwise the list becomes a place where debt goes to be forgotten.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import NamedTuple

from tools import maturity_map_store as map_store

PROJECT_DIR = Path(__file__).resolve().parents[1]
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

# Trees a generator writes into. Each is a (parent, child) segment pair because that is how the
# generators build them -- `PROJECT / "site" / "data" / "dashboard.json"` -- and matching on
# segments is what lets the oracle find 116 artefacts where a full-path literal search finds 17.
GENERATED_TREES: tuple[tuple[str, str], ...] = (
    ("site", "data"),
    ("docs", "observability"),
    ("docs", "market_data"),
)
SCANNED_TREES = ("tools", "background", "simulation", "saas", "company")
ARTEFACT_SUFFIXES = (".json", ".md", ".sqlite", ".csv")

# THE FROZEN DEBT, measured 2026-08-19. Every one of these atoms is deprioritised by the
# unmerged-work guard whenever its named artefact is dirty, which for most of them is always.
FROZEN: frozenset[tuple[str, str]] = frozenset({
    ("H14_judge_validation", "site/data"),
    # ("HX3_counter_published_and_derivable", "docs/observability") removed 2026-08-24:
    # the atom was retired (docs/design/RETIRED_ATOMS_2026-08-24.md), so the debt is gone
    # rather than paid. This control's own message names the reason to delete it rather than
    # leave it -- a freeze list that keeps entries for things that no longer exist stops
    # being a shrinking debt list and becomes a place debt is forgotten.
    ("CA2_coverage_report_realised_cohort", "docs/observability/cohort_coverage_realised.json"),
    ("CA3_segmentation_untestable_ledger_marking",
     "docs/observability/segmentation_testability_ledger.json"),
    ("AO12_scale_probe_10k", "docs/observability/scale_probe_10k/report.json"),
    ("AO12_scale_probe_10k", "docs/observability/scale_probe_10k/prediction_register.json"),
    ("OPS3_first_post_ruling_publish", "docs/observability/.publish_gate_state.json"),
    ("OPS7_provenance_stamps_on_live_pages", "site/data/"),
    ("OPS8_last_known_good_staleness_banner", "site/data/"),
    ("SITE6_knowledge_in_nav_glossary_dissolved", "site/data/glossary.json"),
    ("SITE12_evidence_a_reader_can_use", "site/data/capabilities_door.json"),
})


class OracleUnavailable(RuntimeError):
    """The generated-path set could not be computed. NEVER silently a clean reading."""


def generated_artefacts(root: Path | None = None) -> set[str]:
    """Repo-relative paths that a module in this tree assigns as an output destination.

    Technique borrowed from `derived_artefact_register._design_markdown_constants`: read the
    string constants of one assignment and look for the tree segments, WITHOUT importing the
    module. A module is not imported to find out whether it is a candidate.
    """
    base = Path(root) if root is not None else PROJECT_DIR
    found: set[str] = set()
    scanned = 0
    for tree_name in SCANNED_TREES:
        d = base / tree_name
        if not d.exists():
            continue
        for f in d.rglob("*.py"):
            try:
                mod = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001 - an unparseable file is not an oracle failure
                continue
            scanned += 1
            for node in ast.walk(mod):
                if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                    continue
                parts = [c.value for c in ast.walk(node.value)
                         if isinstance(c, ast.Constant) and isinstance(c.value, str)]
                for a, b in GENERATED_TREES:
                    if a in parts and b in parts:
                        found.update(f"{a}/{b}/{s}" for s in parts
                                     if s.endswith(ARTEFACT_SUFFIXES))
    if not scanned:
        raise OracleUnavailable(
            f"no python files scanned under {SCANNED_TREES} -- the oracle cannot be computed, "
            "and an empty generated set would pass every atom"
        )
    if not found:
        raise OracleUnavailable(
            f"scanned {scanned} modules and found no generated artefact at all -- this project "
            "publishes a site from generated JSON, so zero is a broken oracle, not a clean tree"
        )
    return found


# The calls that make a path an OUTPUT. `open`/`Path.open` count only on a WRITING mode: the same
# call with "r" is what every reader of an authored document does, and counting it would classify
# the whole repository as generated.
WRITE_METHODS = ("write_text", "write_bytes")
# REWRITING modes only. `"a"` is deliberately absent: an APPEND accumulates a record no run can
# reproduce -- `docs/direction/decisions.jsonl` is the director's own decisions, appended one at a
# time -- and the remedy a consumer applies to a generated path is REVERT. A whole-file rewrite
# can be re-run; an append cannot be un-lost. `"r+"` is out for the same reason.
WRITING_MODE_CHARS = ("w", "x")
# Destination argument (0-based) of the stdlib calls whose second operand is unambiguously written:
# `os.replace(tmp, final)`, `shutil.copy(src, dest)`.
DESTINATION_ARG = {"replace": 1, "rename": 1, "copy": 1, "copy2": 1, "copyfile": 1, "move": 1}
# The same two names in their PATHLIB form, where the destination is the only argument:
# `tmp.replace(final)` is the atomic-write idiom, live in `background/seat_continuity.py` and five
# other producers here.
#
# THE ARITY CHECK BELOW IS A FILTER, NOT THE SAFETY -- established by mutation, not assumed.
# `str.replace(old, new)` is everywhere in this tree, so dropping the arity check looks dangerous;
# it is not, because the first argument of a string substitution is a string and `_static_paths`
# resolves only pathlib expressions. Removing the check changes nothing this scan reports, so it
# earns a comment rather than a control that could never have failed.
RECEIVER_DESTINATION = ("replace", "rename")


def _mode_is_writing(call: ast.Call, path_is_receiver: bool) -> bool:
    """Whether an `open(...)` or `.open(...)` call opens for writing.

    A missing mode means "r". That default is why this is asked at all: the same expression that
    proves a path is an output on `"w"` proves a path is an INPUT on nothing.
    """
    mode_pos = 0 if path_is_receiver else 1
    mode: str | None = None
    if len(call.args) > mode_pos and isinstance(call.args[mode_pos], ast.Constant):
        value = call.args[mode_pos].value
        mode = value if isinstance(value, str) else None
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            mode = kw.value.value if isinstance(kw.value.value, str) else mode
    return bool(mode) and any(c in mode for c in WRITING_MODE_CHARS)


SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _own_scope(node: ast.AST) -> list[ast.AST]:
    """Every node belonging to THIS scope, stopping at each nested def rather than entering it.

    SCOPE IS NOT DECORATION HERE, IT IS THE DIFFERENCE BETWEEN A FINDING AND A FALSE ONE. A
    module-wide name map read `Path(p).write_text(...)` in `supervisor._record_harden_cooldown`
    -- where `p` is the cooldown file -- against a `p` bound to `DIRECTOR_AXES.md` in a different
    function, and reported the director's axes as a generated artefact. One-letter destination
    names are everywhere in this tree, so a flat map does not merely blur: it manufactures the
    exact misclassification this oracle exists to avoid, on the most expensive paths in the repo.
    """
    out: list[ast.AST] = []
    stack: list[ast.AST] = list(ast.iter_child_nodes(node))
    while stack:
        current = stack.pop()
        out.append(current)
        if not isinstance(current, SCOPE_NODES):
            stack.extend(ast.iter_child_nodes(current))
    return out


def _nested_scopes(node: ast.AST) -> list[ast.AST]:
    return [n for n in _own_scope(node) if isinstance(n, SCOPE_NODES)]


def _write_destinations(scope: list[ast.AST]) -> list[ast.expr]:
    """Every expression standing where this scope writes. The EXPRESSION, not a name.

    `tools/orphan_ratchet.py` writes its baseline as `(path or BASELINE_PATH).write_text(...)`, so
    a scan that only accepted a bare `Name` receiver would miss the one path this exists for. The
    caller resolves the expression itself AND every name inside it.
    """
    out: list[ast.expr] = []
    for node in scope:
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            if func.attr in WRITE_METHODS:
                out.append(func.value)
            elif func.attr == "open" and _mode_is_writing(node, path_is_receiver=True):
                out.append(func.value)
            elif func.attr in DESTINATION_ARG and len(node.args) > DESTINATION_ARG[func.attr]:
                out.append(node.args[DESTINATION_ARG[func.attr]])
            elif func.attr in RECEIVER_DESTINATION and len(node.args) == 1 and not node.keywords:
                out.append(node.args[0])
        elif isinstance(func, ast.Name):
            if func.id == "open" and node.args and _mode_is_writing(node, path_is_receiver=False):
                out.append(node.args[0])
    return out


def _static_paths(node: ast.expr, module_file: Path,
                  known: dict[str, list[Path]]) -> list[Path]:
    """Every path a pathlib expression can statically be, WITHOUT importing or executing anything.

    Handles the shapes this repository actually builds output paths with:
    `Path(__file__).resolve().parents[N]`, `.parent`, `NAME / "seg" / "file.json"`, and a name
    already resolved from an earlier assignment in the same module.

    A LIST AND NOT ONE PATH, because both of the real destination idioms here are a CHOICE, and
    taking the first branch would silently drop the other:
    `dest = OUT_PATH if out_path is None else out_path` (`tools/generate_value_arms_data.py`) and
    `(path or BASELINE_PATH).write_text(...)` (`tools/orphan_ratchet.py`). Every branch that
    resolves is a destination the module can write, so every branch is returned. An empty list is
    this function saying "I cannot tell" -- never "not a path".
    """
    if isinstance(node, ast.Name):
        return list(known.get(node.id, ()))
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == "Path":
            if (len(node.args) == 1 and isinstance(node.args[0], ast.Name)
                    and node.args[0].id == "__file__"):
                return [module_file]
            return []
        if isinstance(func, ast.Attribute) and func.attr in ("resolve", "absolute", "expanduser"):
            return _static_paths(func.value, module_file, known)
        return []
    if isinstance(node, ast.Attribute) and node.attr == "parent":
        return [p.parent for p in _static_paths(node.value, module_file, known)]
    # `self.project_dir` -- an INSTANCE attribute, looked up under a DOTTED key. A dotted key
    # cannot collide with any Python identifier, so the bare-name map above is untouched by
    # construction and a class body's `PATH` still cannot answer a method's bare `PATH`. Only the
    # literal receiver `self` is read: rebinding the receiver name is what `_class_self_paths`
    # and the signature-shadow strip below exist to refuse.
    if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id == "self"):
        return list(known.get(f"self.{node.attr}", ()))
    if isinstance(node, ast.Subscript):
        value = node.value
        if isinstance(value, ast.Attribute) and value.attr == "parents":
            index = node.slice
            if isinstance(index, ast.Constant) and isinstance(index.value, int):
                out = []
                for base in _static_paths(value.value, module_file, known):
                    parents = list(base.parents)
                    if index.value < len(parents):
                        out.append(parents[index.value])
                return out
        return []
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        right = node.right
        if not (isinstance(right, ast.Constant) and isinstance(right.value, str)):
            return []
        return [p / right.value for p in _static_paths(node.left, module_file, known)]
    if isinstance(node, ast.IfExp):
        return (_static_paths(node.body, module_file, known)
                + _static_paths(node.orelse, module_file, known))
    if isinstance(node, ast.BoolOp):
        return [p for v in node.values for p in _static_paths(v, module_file, known)]
    return []


def _scope_path_names(scope: list[ast.AST], module_file: Path,
                      inherited: dict[str, list[Path]]) -> dict[str, list[Path]]:
    """name -> the paths it can be, for the assignments in ONE scope, over what it inherits.

    In source order, so `ROOT = Path(__file__).parents[1]` is known by the time
    `BASELINE = ROOT / "docs" / ...` is read. A name assigned twice accumulates both, for the same
    reason `_static_paths` returns a list: a rebound destination is still a destination.
    """
    known = {name: list(paths) for name, paths in inherited.items()}
    assigns = [n for n in scope if isinstance(n, (ast.Assign, ast.AnnAssign))]
    for node in sorted(assigns,
                       key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0))):
        if node.value is None:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        resolved = _static_paths(node.value, module_file, known) if names else []
        for name in names:
            for path in resolved:
                if path not in known.setdefault(name, []):
                    known[name].append(path)
    return known


class _Helper(NamedTuple):
    """A same-module `def` that writes somewhere, held so a CALL to it can be resolved.

    `params` keeps EVERY positional parameter in declaration order, including the ones that are
    not bindable, because dropping one would shift every later argument's position onto the wrong
    name -- a resolver that quietly mis-binds is worse than one that declines.
    """

    params: tuple[str, ...]
    bindable: frozenset[str]
    scope: tuple[ast.AST, ...]
    destinations: tuple[ast.expr, ...]


def _module_helpers(module: ast.AST) -> dict[str, _Helper]:
    """The module-level `def`s that write, by name. One frame of reach, and only this file's defs.

    SAME MODULE ONLY, deliberately. A helper imported from elsewhere would need the other module's
    parse and its own name resolution, and the shapes this was built for -- `_write_json`,
    `_dump`, `_save` -- are private helpers beside the constant they write. Cross-module reach is
    a different, larger thing and stays out rather than being half-done.
    """
    out: dict[str, _Helper] = {}
    for node in getattr(module, "body", ()):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        scope = _own_scope(node)
        destinations = _write_destinations(scope)
        if not destinations:
            continue
        args = node.args
        params = tuple(a.arg for a in (*args.posonlyargs, *args.args))
        # A parameter REBOUND in the body is not the argument any more: after `path = OUT_DEFAULT`
        # the write goes somewhere the call site never named, and following it would MANUFACTURE a
        # path. Every Store of the name counts -- assignment, `for`, `with ... as`, walrus --
        # because the question is only ever "can this still be the argument".
        rebound = {n.id for n in scope
                   if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
        bindable = frozenset(
            a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)
            if a.arg not in rebound)
        if not bindable:
            continue
        out[node.name] = _Helper(params, bindable, tuple(scope), tuple(destinations))
    return out


def _paths_written_through_helper(helper: _Helper, call: ast.Call, module_file: Path,
                                  caller_known: dict[str, list[Path]],
                                  module_known: dict[str, list[Path]]) -> set[Path]:
    """Destinations this ONE call reaches, by binding its arguments to the helper's parameters.

    The binding is then handed to the SAME resolver the helper's own scope already gets, so the
    write shape does not have to be enumerated twice: `path.write_text(...)`,
    `Path(path).write_text(...)`, `(path / "f.json").write_text(...)` and
    `dest = path / "f.json"` all follow from `_scope_path_names` + `_static_paths` for free.

    AN ARGUMENT IS RESOLVED BY `_static_paths` ALONE -- NO NAME WALK, and that is the one place
    this is deliberately STRICTER than its neighbour above. A write DESTINATION is structurally a
    path expression, so walking it for any known name is cheap and safe. An ARGUMENT is an
    arbitrary expression: `_save(build_name(REGISTER_DOC))` would walk to a register this module
    only reads and report it as written, one frame down, which is precisely the naming-keyed
    misclassification the write-site key exists to prevent -- and its consumer's remedy is REVERT.
    Missing a path costs a warning; claiming one costs a lane's work.

    THE HELPER INHERITS THE MODULE'S NAMES, NOT THE CALLER'S. A helper called from inside another
    function cannot see that function's locals, and lending them to it is the flat-name-map defect
    that reported the director's axes as generated, arriving through a different door.
    """
    bound: dict[str, list[Path]] = {}
    for index, arg in enumerate(call.args):
        if isinstance(arg, ast.Starred) or index >= len(helper.params):
            break  # `*args`, or more arguments than parameters: positions stop meaning anything
        name = helper.params[index]
        if name not in helper.bindable:
            continue
        paths = _static_paths(arg, module_file, caller_known)
        if paths:
            bound[name] = paths
    for kw in call.keywords:
        if kw.arg is None or kw.arg not in helper.bindable:
            continue
        paths = _static_paths(kw.value, module_file, caller_known)
        if paths:
            bound[kw.arg] = paths
    if not bound:
        return set()
    known = _scope_path_names(list(helper.scope), module_file, {**module_known, **bound})
    found: set[Path] = set()
    for dest in helper.destinations:
        found.update(_static_paths(dest, module_file, known))
        found.update(p for n in ast.walk(dest) if isinstance(n, ast.Name)
                     for p in known.get(n.id, ()))
    return found


def _signature_names(node: ast.AST) -> set[str]:
    """Every name a `def`/`lambda` BINDS in its own signature, and so shadows from outside."""
    args = getattr(node, "args", None)
    if args is None:
        return set()
    names = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
    for extra in (args.vararg, args.kwarg):
        if extra is not None:
            names.add(extra.arg)
    return names


def _default_destinations(node: ast.AST, module_file: Path,
                          inherited: dict[str, list[Path]]) -> dict[str, list[Path]]:
    """param -> the paths its DEFAULT can be, for a `def` whose caller may pass nothing.

    THE DEFAULT IS A WRITE DESTINATION THE MODULE DECLARES, and the evidence is no weaker than a
    module-scope `OUT.write_text(...)`: `def generate(out=OUT_PATH)` followed by `out.write_text`
    writes `OUT_PATH` on every call that names no destination, and `background/
    process_run_complete.py` calls `_ledger.write()` exactly that way. This is the door the helper
    frame left open -- and the bigger one. Thirty-six `def`s in the scanned trees write a parameter
    that carries a default, against the eight paths the helper frame found.

    RESOLVED AGAINST WHAT THE `def` INHERITS, WHICH FOR A METHOD IS NOT THE CLASS BODY. Python
    evaluates a default in the enclosing scope, so a method's default genuinely CAN see a class
    attribute -- and that is still not taken, because `_paths_written_by_scope` hands a class's
    nested scopes what the CLASS inherited. Strictly narrower than the language allows, and
    narrower in the direction that cannot manufacture a path.

    A REBOUND PARAMETER IS REFUSED, for the reason `_module_helpers` refuses one: after
    `path = SOMEWHERE_ELSE` the write does not go where the signature said, and seeding the default
    anyway would hand `_scope_path_names` BOTH -- it accumulates rather than replaces -- so the
    oracle would claim a path this `def` provably never writes.

    A DEFAULT IS AN EXPRESSION IN THE SIGNATURE, NOT AN ARGUMENT AT A CALL SITE, which is why this
    may use `_static_paths` where `_paths_written_through_helper` may not walk names. There is no
    caller to be wrong about: the default is what the `def` itself says it writes.
    """
    args = getattr(node, "args", None)
    if args is None:
        return {}
    positional = [*args.posonlyargs, *args.args]
    pairs: list[tuple[ast.arg, ast.expr]] = list(
        zip(positional[len(positional) - len(args.defaults):], args.defaults))
    pairs += [(a, d) for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None]
    if not pairs:
        return {}
    rebound = {n.id for n in _own_scope(node)
               if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    out: dict[str, list[Path]] = {}
    for arg, default in pairs:
        if arg.arg in rebound:
            continue
        paths = _static_paths(default, module_file, inherited)
        if paths:
            out[arg.arg] = paths
    return out


def _class_self_paths(node: ast.ClassDef, module_file: Path,
                      inherited: dict[str, list[Path]]) -> dict[str, list[Path]]:
    """`"self.<attr>"` -> the paths that attribute can be, for ONE class.

    THE ATTRIBUTE IS THE DESTINATION AND THE METHOD ONLY SPELLS IT. `PublishStepLedger.__init__`
    binds `self.project_dir = Path(project_dir) if project_dir else PROJECT_DIR` and
    `PublishStepLedger.write` falls back to `self.project_dir / "site" / "data" /
    "publish_steps.json"`; `background/process_run_complete.py` calls `_ledger.write()` bare, so
    that path is written on every publish cycle and no expression in `write` names it.

    A DOTTED KEY, WHICH IS WHY THE BARE-NAME MAP IS SAFE BY CONSTRUCTION AND NOT BY CARE. No Python
    identifier contains a `.`, so `"self.project_dir"` can never be returned for a bare `Name`
    lookup and can never be shadowed by one. The rule the module already enforces -- a class body's
    `PATH` is NOT a method's bare `PATH` -- is untouched: what is handed down here is only ever
    reachable by writing `self.` in front of it, which is what Python requires too.

    TWO SOURCES, RESOLVED IN DIFFERENT SCOPES BECAUSE PYTHON EVALUATES THEM IN DIFFERENT SCOPES.
    A class-body `PATH = ROOT / "x.json"` is resolved against the class body's own names; a
    method's `self.X = <expr>` is resolved against THAT METHOD's locals over what the CLASS
    inherited -- never over a sibling method's locals, and never over the class body, which is the
    flat-name-map defect arriving through a third door.

    A REBOUND ATTRIBUTE IS REFUSED, the same guard `_module_helpers` and `_default_destinations`
    carry. Every `self.X` store site ANYWHERE in the class subtree is counted, plus every class-body
    binding of the bare name, and an attribute with more than one is dropped whole. That deliberately
    counts store sites this function cannot resolve -- one inside a closure, one under a `for`, one
    in a nested class -- so an attribute it cannot fully see fails toward refusal rather than toward
    a claim. Only an attribute bound EXACTLY ONCE is handed down, because only then does the
    resolved expression say where the write goes on every path through the class.
    """
    body = _own_scope(node)
    counts: dict[str, int] = {}
    for n in body:
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            counts[n.id] = counts.get(n.id, 0) + 1
    for n in ast.walk(node):
        if (isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
                and isinstance(n.value, ast.Name) and n.value.id == "self"):
            counts[n.attr] = counts.get(n.attr, 0) + 1
    if not counts:
        return {}

    resolved: dict[str, list[Path]] = {}

    def _record(attr: str, paths: list[Path]) -> None:
        for path in paths:
            if path not in resolved.setdefault(attr, []):
                resolved[attr].append(path)

    class_known = _scope_path_names(body, module_file, inherited)
    for n in body:
        if not isinstance(n, (ast.Assign, ast.AnnAssign)) or n.value is None:
            continue
        targets = n.targets if isinstance(n, ast.Assign) else [n.target]
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if names:
            _record_paths = _static_paths(n.value, module_file, class_known)
            for name in names:
                _record(name, _record_paths)

    for method in body:
        if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        scope = _own_scope(method)
        method_inherited = {**inherited,
                            **_default_destinations(method, module_file, inherited)}
        method_known = _scope_path_names(scope, module_file, method_inherited)
        for n in scope:
            if not isinstance(n, (ast.Assign, ast.AnnAssign)) or n.value is None:
                continue
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            attrs = [t.attr for t in targets
                     if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                     and t.value.id == "self"]
            if attrs:
                paths = _static_paths(n.value, module_file, method_known)
                for attr in attrs:
                    _record(attr, paths)

    return {f"self.{attr}": paths for attr, paths in resolved.items()
            if counts.get(attr, 0) == 1 and paths}


def _paths_written_by_scope(node: ast.AST, module_file: Path,
                            inherited: dict[str, list[Path]],
                            helpers: dict[str, _Helper] | None = None,
                            module_known: dict[str, list[Path]] | None = None) -> set[Path]:
    """Absolute destinations this scope writes, then every scope nested inside it.

    The module scope is resolved WHOLE before any nested def is entered, so a function defined
    above the constant it writes to still sees it -- which is what actually happens at call time.
    """
    scope = _own_scope(node)
    inherited = {**inherited, **_default_destinations(node, module_file, inherited)}
    known = _scope_path_names(scope, module_file, inherited)
    if helpers is None:
        helpers = _module_helpers(node)
    if module_known is None:
        module_known = known
    found: set[Path] = set()
    for dest in _write_destinations(scope):
        candidates = list(_static_paths(dest, module_file, known))
        candidates += [p for n in ast.walk(dest) if isinstance(n, ast.Name)
                       for p in known.get(n.id, ())]
        found.update(candidates)
    # ONE FRAME DOWN. A call to a same-module helper that writes a parameter. This is NOT
    # transitive by construction rather than by a depth counter: a call inside the helper is
    # resolved when the helper's OWN scope is walked, where no parameter is bound to anything, so
    # nothing a caller passed can reach a second frame. Two frames would need the binding to
    # travel, and it does not.
    for n in scope:
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id in helpers):
            found |= _paths_written_through_helper(
                helpers[n.func.id], n, module_file, known, module_known)
    # A method does NOT see its class body's names -- `PATH` in a class body is `self.PATH` or
    # `Cls.PATH` inside a method, never a bare `PATH`. So a nested scope of a CLASS inherits what
    # the class inherited, not what the class bound. Same reasoning as the per-function map above,
    # and the same failure if it is skipped: a class attribute silently lending its path to a
    # one-letter destination name in a method.
    #
    # AND THE ONE THING A METHOD *DOES* SEE OF ITS CLASS IS `self.`, which is why the dotted map
    # rides alongside rather than inside. It is rebuilt at every `ClassDef` and the enclosing
    # class's dotted keys are dropped on the way in: `self` inside an inner class is the INNER
    # instance, so lending it the outer class's attributes would be the flat-name-map defect again,
    # one nesting deeper. That drop is correctness by construction, not a measured guard -- there
    # are zero class-in-class definitions in the scanned trees today, so it could not fire, and it
    # is written this way because the alternative is a filter that has to be remembered.
    # For the same reason there is no guard against a method REBINDING the bare name `self`: asked
    # of the tree on 2026-09-15, zero scopes store it, so a control for it could never fail and the
    # module's own arity-check comment above says what to do with one of those.
    if isinstance(node, ast.ClassDef):
        outer_free = {k: v for k, v in inherited.items() if "." not in k}
        handed_down = {**outer_free,
                       **_class_self_paths(node, module_file, outer_free)}
    else:
        handed_down = known
    for nested in _nested_scopes(node):
        # A NAME THE NESTED `def` BINDS IN ITS OWN SIGNATURE IS NOT THE ENCLOSING NAME. Seeding
        # parameter defaults above puts PARAMETER names into this map for the first time, and
        # `path`/`out`/`dest` repeat across nested defs in this tree, so without this the seeded
        # default of an OUTER `def` would be lent to an inner `def`'s same-named parameter -- the
        # flat-name-map defect that reported the director's axes as generated, one scope deeper.
        # It is closed here rather than left for the defect to find it.
        passed = {k: v for k, v in handed_down.items() if k not in _signature_names(nested)}
        found |= _paths_written_by_scope(nested, module_file, passed, helpers, module_known)
    return found


# WRITTEN, AND STILL NOT A PHOTOGRAPH OF A RUN. A module rewrites each of these, so the write-site
# evidence is real -- but their CONTENT does not come from the tree, so no re-run reproduces them
# and a revert loses input nothing can recompute. The consumer's remedy for a generated path is
# `git show HEAD:<path> > <path>`, which is exactly that loss. Both are therefore held on the safe
# side: classified authored, offered a landing. A member that stops being write-reached is STALE
# and `test_the_not_reproducible_carve_out_is_load_bearing` says so, so this can only shrink.
WRITTEN_BUT_NOT_REPRODUCIBLE: frozenset[str] = frozenset({
    # `background/pull_forward_proposal.py` edits one atom's `loop_stage` in place. The map is the
    # tree's DECLARATION of what exists, not a projection of it -- a lane's uncommitted level move
    # lives here and is gone the moment someone reverts to HEAD on this advice.
    "docs/design/maturity_map.yaml",
    # `background/director_twin.py` rewrites the canon to record an overturn. The words are the
    # DIRECTOR'S; a run does not make them again.
    "docs/design/DIRECTOR_CANON.md",
    # BOTH OF THE NEXT TWO WERE FOUND BY THE HELPER FRAME (delivery seat, 2026-09-15) AND BOTH
    # BELONG ON THE AUTHORED SIDE. Reaching one frame into a helper found eight paths; six are
    # photographs of a run and these two are not, which is the whole reason this list is separate
    # from the scan rather than a filter inside it. Neither was write-reached before this change,
    # so neither could have been carved out before it either -- they become load-bearing here.
    #
    # `background/discovery_agent._update_last_checked` reads this file, regex-substitutes ONE
    # date line, and writes it back. The file says of itself: "Updated by discovery agent and
    # manually when phases change assumptions." A daemon touching one line does not make the
    # hand-written anchor rows below it reproducible, and REVERT is what a consumer does with a
    # generated path.
    "docs/market_research/ASSUMPTIONS.md",
    # `background/naive_organ._rewrite_log` rewrites this ledger whole -- so the WRITING-MODE test
    # passes where an `"a"` append would have been excluded by `WRITING_MODE_CHARS`. But the
    # exclusion of append is not about the MODE, it is about a record no run can reproduce, and
    # this is that record: `answer_organ_question` stores an answer and its fetchable evidence
    # refs, supplied by a person and refused if empty. Read-modify-rewrite of an accumulated
    # ledger is an append wearing a rewrite's clothes, and the mode check cannot see the
    # difference. This entry is where that distinction is actually made.
    "docs/observability/naive_organ_log.jsonl",
    # THE NEXT THREE WERE FOUND BY THE DEFAULTED-DESTINATION PARAMETER (delivery seat,
    # 2026-09-15). Nine paths arrived and three of them are the append-wearing-a-rewrite shape
    # above, which is a HIGHER proportion than the helper frame's two in eight -- a default is how
    # a module spells "the one place I keep my running record", so the door that finds them finds
    # more of them. Each is read, merged with what is already there, and written back whole.
    #
    # `tools/space_filling_sample.record_visit` adds ONE RUN's corners to a ledger whose own
    # docstring says coverage is a property of the ENSEMBLE of runs. No single run makes it again.
    "docs/design/visited_corner_ledger.json",
    # `tools/edge_traffic_capture.append` -- the name is the argument. Rows are captured from an
    # external feed hour by hour; a re-run captures the CURRENT window and the history is gone.
    "docs/observability/edge_traffic.jsonl",
    # `tools/fetch_haduk_grid.write_receipt` merges each checkpoint of a 10 GB network pull into
    # the receipt and `os.replace`s it in. Its docstring: a death mid-write must cost "the newest
    # checkpoint and never the record of the 10 GB already bought". A REVERT costs exactly that,
    # and `company/` has no route to the real world to buy it again.
    "docs/market_research/haduk_grid_pull_receipt.json",
})


def _write_reached_paths(root: Path | None = None) -> set[str]:
    """The raw write-site scan, before the not-reproducible carve-out. Separate so the carve-out's
    own staleness can be measured against it."""
    base = (Path(root) if root is not None else PROJECT_DIR).resolve()
    found: set[str] = set()
    scanned = 0
    for tree_name in SCANNED_TREES:
        d = base / tree_name
        if not d.exists():
            continue
        for f in sorted(d.rglob("*.py")):
            try:
                mod = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001 - an unparseable file is not an oracle failure
                continue
            scanned += 1
            module_file = f.resolve()
            for candidate in _paths_written_by_scope(mod, module_file, {}):
                if not candidate.suffix:
                    continue
                try:
                    rel = candidate.relative_to(base)
                except ValueError:  # outside the repo -- a cache or a temp file, not ours
                    continue
                found.add(rel.as_posix())
    if not scanned:
        raise OracleUnavailable(
            f"no python files scanned under {SCANNED_TREES} -- the write-site oracle cannot be "
            "computed, and an empty set would classify every producer's output as somebody's work"
        )
    if not found:
        raise OracleUnavailable(
            f"scanned {scanned} modules and found no module writing any path at all -- this "
            "project publishes a site and freezes ratchets from python, so zero is a broken "
            "oracle, not a tree without generators"
        )
    return found


def written_artefacts(root: Path | None = None) -> set[str]:
    """Repo-relative paths a module in this tree actually WRITES. The union partner, not a widening.

    WHY A THIRD FUNCTION AND NOT A WIDER `generated_artefacts` (delivery seat, 2026-09-15).
    `generated_artefacts` is keyed to generated TREES -- the `(parent, child)` segment pairs in
    `GENERATED_TREES` -- and it feeds the fail-CLOSED `file_scope` starvation gate above, which
    blocks commits. `docs/design/orphan_baseline.json` is a generator's output living in an
    otherwise AUTHORED tree, so it is invisible to a tree-keyed oracle by construction; and adding
    `("docs", "design")` to that set would sweep hundreds of authored design documents into a
    commit-blocking gate to fix one line of remedy prose. So the write-keyed set is computed
    separately and consumed separately: NOTHING in `violations`/`gate_violations` reads it, and the
    frozen debt list stays keyed to exactly the set it was measured against.

    WRITING IS THE PROPERTY, NAMING IS NOT, AND THE ASYMMETRY IS THE WHOLE POINT. Authored paths
    are assigned as module constants all over this repository -- `REGISTER_DOC = REPO_ROOT /
    "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"` in `tools/wall_crossing_
    dispositions.py` is one, and it is only ever READ. A classifier keyed to naming would mark
    that register generated, and the remedy a consumer applies to a generated path is REVERT, so
    the cheap-looking generalisation silently discards a lane's real work. The evidence demanded
    here is a write SITE the constant reaches: `.write_text`/`.write_bytes`, an `open` in a
    writing mode, or the destination of `os.replace`-shaped move.

    ONE FRAME OF REACH, AND WHAT IS STILL OUT (delivery seat, 2026-09-15). The gap this docstring
    used to NAME -- a path handed to a helper (`_write_json(BASELINE_PATH, data)`) and written one
    frame down -- is now followed: `_module_helpers` records each same-module `def` that writes,
    and a call binds its arguments to those parameters before the helper's destination is
    re-resolved. It found EIGHT paths, on seven producers, every one of which factored its write
    into a `_write`-shaped helper and was therefore being offered a landing by the reconciler.
    Two of the eight turned out to belong on the authored side anyway and are carved out below --
    the frame found them, and the judgement about them is a separate question from finding them.

    AND THE DEFAULT IS A DESTINATION TOO (delivery seat, 2026-09-15). `_default_destinations`
    seeds a parameter from the default in its own signature, because `def generate(out=OUT_PATH)`
    writes `OUT_PATH` on every call that names no destination -- and `generate()` with no argument
    is how nine producers here are actually called. It added NINE paths, three of which are the
    append-wearing-a-rewrite shape and are carved out below.

    THE `self._write(...)` FRAME IS NOT MISSING, IT IS MEASURED EMPTY, and the correction is kept
    here beside the claim that sent someone looking for it. This docstring used to list "a method
    called as `self._write(...)`" as the next door, and a Lane 0 item repeated that as "the largest
    door left open". Asked of the tree on 2026-09-15: 2,058 classes in the scanned trees, SEVEN
    with a method whose scope holds a write destination, TWO of those with a bindable parameter
    reaching it (`PublishStepLedger.write`, `ObservableTrace.save`), and ZERO call sites anywhere
    of the shape `self.<writer>(...)`. Five of the seven are `str.replace(old, new)` landing in
    `DESTINATION_ARG` and resolving to nothing, which is the filter-not-safety case noted above.
    Building that frame would be machinery no tree state can exercise, so it is not built; the
    measurement is the deliverable, and it is recorded rather than the door being left named.
    `docs/staging/records/PREREG_WHAT_THE_WRITE_KEYED_ORACLE_GAINS_FROM_A_DEFAULTED_DESTINATION_
    PARAMETER_2026-09-15.md` has the count and the predictions, two of which it falsified.

    AND THE INSTANCE ATTRIBUTE IS FOLLOWED NOW TOO -- ONE PATH, AND THE COUNT IS THE POINT
    (delivery seat, 2026-09-15). `_class_self_paths` resolves `self.<attr>` under a dotted key,
    which is the door this docstring's own "still out" list named and the one the `self._write(...)`
    search should have found. It adds EXACTLY ONE path, `site/data/publish_steps.json`, and the
    population census behind that number is in
    `docs/staging/records/PREREG_WHAT_THE_WRITE_KEYED_ORACLE_GAINS_FROM_AN_INSTANCE_ATTRIBUTE_
    DESTINATION_2026-09-15.md`: 2,058 classes, 8 (class, method) pairs holding a write destination,
    2 touching `self.<attr>`, 1 surviving the rebound guard. Eight, then nine, then one is a curve,
    and it is recorded here rather than left for a fourth frame to rediscover.
    **AND THAT PATH WAS ALREADY CLASSIFIED GENERATED.** It lives under `site/data/`, so the
    TREE-keyed oracle has always had it, and `origin_reconcile` reads the UNION -- which did not
    move. This frame made the write-keyed oracle more honest and changed no consumer's answer on
    the tree it landed against. Kept because the oracle's correctness is a property and not today's
    union; written down because a later reader finding this beside the other two frames would
    otherwise assume it paid like they did.

    STILL OUT, and each on purpose rather than by omission: a helper in ANOTHER module (it needs
    that module's parse and its name resolution -- a larger thing, not a half-done one); a helper
    reached through TWO frames (the binding does not travel, so this is structural, not a depth
    counter); a parameter or attribute REBOUND, which is refused because after
    `path = SOMEWHERE_ELSE` the write no longer goes where the signature, the caller or the
    constructor said; and -- **the largest one left, and this time with a count rather than a
    guess** -- a `/` join whose RIGHT operand is a NAME rather than a string literal. `out = root /
    DEFAULT_REPORT`, where `DEFAULT_REPORT` is a module-level string constant, is 39 of the 364
    unresolved destinations in this tree and the biggest single cluster; the next 32 are a
    module-level `def`'s destination parameter with NO default, reachable only from a call site in
    another module. The census is in the prereg named above.
    All of them degrade the same safe way the whole gap used to: the path stays classified authored,
    so the consumer offers a landing where a revert would have done, rather than the reverse.

    AND WRITING IS NOT SUFFICIENT EITHER, WHICH IS WHY `WRITTEN_BUT_NOT_REPRODUCIBLE` EXISTS. Two
    paths in this tree are rewritten by a module and are still nobody's photograph: the maturity
    map and the director's canon. The reason is the same one that makes the revert remedy cheap
    everywhere else -- a generated path can be made again -- and those two cannot.

    FAIL-CLOSED, like its neighbour: an oracle that cannot be computed RAISES rather than
    returning an empty set that reads exactly like a tree with no generators in it.
    """
    return _write_reached_paths(root) - WRITTEN_BUT_NOT_REPRODUCIBLE


def _tree_prefixes() -> set[str]:
    return {f"{a}/{b}" for a, b in GENERATED_TREES}


def offends(scope_entry: str, generated: set[str]) -> bool:
    """True if this one `file_scope` entry names generated ground.

    Three shapes, all seen live: the artefact itself (`site/data/glossary.json`), the directory
    with a slash (`site/data/`), and the directory without one (`site/data`).
    """
    s = scope_entry.strip()
    if s in generated:
        return True
    bare = s.rstrip("/")
    prefixes = _tree_prefixes()
    return bare in prefixes or any(bare.startswith(p + "/") for p in prefixes)


def violations(root: Path | None = None) -> list[tuple[str, str]]:
    """(atom_id, scope_entry) for every declaration standing on generated ground. Sorted."""
    generated = generated_artefacts(root)
    base = Path(root) if root is not None else PROJECT_DIR
    try:
        loaded = map_store.load_atoms(base / "docs" / "design" / "maturity_map.yaml")
    except Exception as exc:  # noqa: BLE001
        raise OracleUnavailable(f"the maturity map could not be read: {exc}") from exc
    atoms = loaded if isinstance(loaded, list) else (loaded or {}).get("atoms", [])
    atoms = [a for a in atoms if isinstance(a, dict) and a.get("id")]
    if not atoms:
        raise OracleUnavailable("the maturity map parsed to zero atoms")
    out = [
        (a["id"], s)
        for a in atoms
        for s in (a.get("file_scope") or [])
        if offends(s, generated)
    ]
    return sorted(set(out))


def gate_violations(root: Path | None = None) -> list[str]:
    """Commit-time verdict. NEW declarations fail; REPAIRED frozen ones fail too, so the
    freeze can only shrink. Empty list means the commit may proceed."""
    live = set(violations(root))
    problems = [
        f"NEW: {aid} declares `{s}` in its file_scope -- a path a generator rewrites. The "
        "unmerged-work guard will deprioritise this atom on every tick it is dirty, so it will "
        "never be drawn and nothing will say so. Scope the GENERATOR, not the generated."
        for aid, s in sorted(live - FROZEN)
    ]
    problems += [
        f"STALE FREEZE: {aid} no longer declares `{s}` -- remove it from FROZEN so the debt "
        "list keeps shrinking instead of becoming a place debt is forgotten."
        for aid, s in sorted(FROZEN - live)
    ]
    return problems


def main() -> int:
    try:
        problems = gate_violations()
    except OracleUnavailable as exc:
        print(f"file-scope-generated-paths: ORACLE UNAVAILABLE -- {exc}")
        return 2
    if not problems:
        print(f"file-scope-generated-paths: no new generated-path declarations "
              f"({len(FROZEN)} frozen, shrink-only).")
        return 0
    print("file-scope-generated-paths: COMMIT REFUSED.\n")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
