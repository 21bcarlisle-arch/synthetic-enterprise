"""PW2 -- the census of controls whose FAILURE path writes the state their own ALARM reads.

THE CLASS (director, DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09, OBSERVATIONS):
*"The failure path wrote to the state the alarm reads, so the failure silenced its own alarm.
That is a class, not an instance. Where else can a check's failure clear the signal that the
check failed?"*

The instance: `record_publish_gate_failure`/`record_publish_gate_success` write
`.publish_gate_state.json`; `_episode_phrase` and `supervisor._publish_gate_wedge_active` derive
the alarm's SEVERITY (how long, how many) from that same file. So every failure rewrote the
episode clock the alarm was about to read, and a 10h26m episode paged as a fresh 14 minutes. This
is the second-order form of R15 fail-silent: the check DOES fail and DOES alarm, but the alarm's
severity is derived from state the failure just overwrote -- the louder the failure, the quieter
the signal.

WHY A CENSUS AND NOT A FIX: R10. An absurdity-class defect may not be closed with an instance fix.
Patching `.publish_gate_state.json` alone is exactly the move the steer forbade; the deliverable is
the enumeration of the whole class, then a guard on its shape.

DERIVED, NOT INSPECTED. The census is the INTERSECTION of two sets computed per state path by AST
over the live tree -- the set of functions that WRITE the path and the set that READ it -- never a
hand-listing of files someone thought to look at. Concretely, per state path:

    writers(path) ∩ {functions on a failure path}   x   readers(path) ∩ {functions in an alarm}

Writer/reader membership is a pure derivation: attribute calls (`read_text`/`write_text`/...),
`open()` modes, and a transitive closure over the call graph, so a function that writes only via
`_write_publish_gate_state` still counts as a writer. FAILURE and ALARM membership are derived
CLASSIFIERS -- named lexicons (`_FAILURE_RE`/`_ALARM_RE`), except-handler nesting, and
caller/callee reachability -- and this module says so plainly rather than dressing a heuristic as
a proof: they are recorded in the artefact (`classifiers`) so every verdict is auditable and a
disputed tag is arguable against the recorded rule, not against someone's memory.

THE TEETH (MAKE_IT_STICK -- a census nothing reads is the consumed-not-absorbed shape it exists to
catch): every hit must be DISPOSITIONED in `docs/design/self_clearing_alarm_dispositions.json` as
`real` (the episode-scoped fields are guarded -- see `background/episode_monotonic.py`) or
`benign` WITH a reason. `--check` exits 1 on any UNDISPOSITIONED hit, so a newly-written control of
this shape fails loudly instead of joining the class silently.

AND (PW4) on any `real` hit that is not yet `guarded` with a test citation that EXISTS on disk --
`unguarded_real_hits()`. Without that second rung the `guard` field would be a prose inventory
with no falsifier: a row could say `guarded` while nothing guarded anything. The interim value
`registered` is honest and deliberately stays RED, so a control classified real but never guarded
remains visible debt rather than a settled-looking row.

AND THE INVERSE (2026-09-05) -- `eroded_dispositions()`, a dispositioned row whose HIT has
disappeared. `undispositioned()` only ever asked "a hit with no row"; a path that stopped being a
hit needed no disposition and `--check` exited 0, which is how five carriers left the class the day
the loader sweep repaired them and twelve more had gone in earlier eras. The row set is the
high-water mark -- authored, in git, derived from nothing -- so checking today's derivation against
it is not the read-your-own-output tautology a remembered hit count would be. A repair that
genuinely takes a path out of the class is admitted, but only in writing (`declassified`); a path
the census can no longer see WRITTEN or READ is not a repair and nothing excuses it.

AND THE ANNOTATION ITSELF (2026-09-05) -- `unasked_loader_rows()`, a hit whose row carries no
`loader` field. The dispositions file's `_scope_of_benign` has always said in prose that a row
without one "has not been asked, which is a gap and not a pass", and prose has no falsifier: nine
hours after the sweep annotated all 46 rows, a full-file rewrite in the same lane deleted 33 of
them and every rung above stayed green -- `undispositioned()` asks for a verdict and a reason,
`unguarded_real_hits()` asks `real` rows for a test, and `eroded_dispositions()` asks whether a row
still has a HIT, never whether it still has its ANSWER. Keyed to the property (an unanswered row),
so it fires the same on a row that never had one as on a row that lost one.

AND THE REGISTER'S OWN LOW-WATER MARK (2026-09-05) -- `removed_dispositions()`, a row that has left
the register itself. Every rung above iterates either the hits or the rows, so a key in NEITHER is
the subject of nothing: delete the row and the hit together and all five report clean, which was
measured on the live tree before this was built. That matters because `eroded_dispositions()` rests
on the row set being a HIGH-WATER mark, and nothing made the mark unable to fall -- worse, since
that rung REFUSES a row whose path the census can no longer resolve, deleting the row was the cure
for its own refusal. A red clearable by deleting the evidence is a fail-open with an extra step.
The baseline is the register at HEAD, so this bites on the WORKING COPY at commit time, which is
where the gates run and where the 33-annotation rewrite would have been stopped.

VACUITY GUARD (R15 -- the fail-open shape here is a census that finds NOTHING): a derivation that
silently stops matching -- a renamed attribute, a moved root, a regex that stops firing -- would
report an empty class and read as "clean". `census_is_vacuous()` makes that state an explicit
failure, and `tests/background/test_self_clearing_alarm_census.py` asserts the live tree yields a
non-empty writer set, a non-empty reader set, and at least the known instance as a hit.

INDEPENDENCE (LAW-C pattern, matching `background/primary_state_scan.py` /
`background/shared_primitive_census.py`): imports NOTHING from `supervisor.py` or
`process_run_complete.py` -- the modules it audits. It walks source on disk. Reading the census's
own prior output to decide whether anything changed would be the tautology R15 names first; every
number here is recomputed from source on every run.

CLI:
    python3 -m background.self_clearing_alarm_census            # regenerate + print the hits
    python3 -m background.self_clearing_alarm_census --check    # read-only; exit 1 on undispositioned
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
OBS_DIR = PROJECT_DIR / "docs" / "observability"
CENSUS_PATH = OBS_DIR / "self_clearing_alarm_census.json"
DISPOSITIONS_PATH = PROJECT_DIR / "docs" / "design" / "self_clearing_alarm_dispositions.json"

# The steer scoped the census to the two roots that hold controls. Widening it is a real change
# (more hits to disposition), so it is a named constant rather than a default buried in a call.
SCAN_ROOTS = ("background", "tools")

# What counts as a STATE PATH: a file a control keeps its own memory in. Dotfiles under
# docs/observability (`.publish_gate_state.json`, `.last_tested_hash`) and named registers
# (`action_needed_register.json`, `run_history.json`) both qualify; a `.md` log does not --
# an append-only log cannot shorten an episode, which is the harm being enumerated.
_STATE_SUFFIXES = (".json", ".jsonl", ".state")

_WRITE_ATTRS = frozenset({"write_text", "write_bytes", "unlink"})
_READ_ATTRS = frozenset({"read_text", "read_bytes"})
_WRITE_MODE_CHARS = frozenset("wax+")

# DERIVED CLASSIFIERS, recorded in the artefact so a disputed tag is arguable against the rule.
# Deliberately tight: a lexicon broad enough to tag every function tags nothing, and a census of
# 300 hits is read exactly as reliably as a census of none.
_FAILURE_RE = re.compile(
    r"fail|error|regress|wedge|stall|stuck|breach|violat|_red|red_|kill|timeout|degrade|missing",
    re.IGNORECASE,
)
# `draw` is in here deliberately. In this machine a PRIORITY-ZERO DRAW *is* an alarm -- the
# director's ruling is that alarms preempt the draw -- so a reader that derives draw priority from
# a state file is deriving severity from it just as surely as one that sends an NTFY.
# `_operational_red_persistent_draw` reads `consecutive_red` and RETURNS a rung-1 draw string; it
# notifies nobody, and without this token the census was blind to a textbook member of the class.
_ALARM_RE = re.compile(
    r"alarm|alert|notify|ntfy|escalat|severity|episode|digest|wedge|page_|_page|stale|draw",
    re.IGNORECASE,
)
# Functions that ARE the alarm's exit door. A reader that reaches one of these is in an alarm
# regardless of what it is called -- this is the non-lexical half of the ALARM classifier.
_NOTIFIER_NAMES = frozenset({"send_ntfy", "notify", "register_item", "_fire_publish_gate_alert"})


def _iter_source_files(roots: tuple[str, ...] = SCAN_ROOTS,
                       project_dir: Path = PROJECT_DIR) -> list[Path]:
    """Every .py under the scanned roots, sorted for a stable artefact. Skips __pycache__ and
    test trees -- a test that writes a fixture state file is not a control."""
    files: list[Path] = []
    for root in roots:
        d = project_dir / root
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if "__pycache__" in p.parts or "tests" in p.parts:
                continue
            files.append(p)
    return files


def _state_key(literals: list[str]) -> str | None:
    """The state-file name a path expression resolves to, or None if it is not a state path.

    Takes the LAST string literal in the expression because paths are built left-to-right
    (`PROJECT_DIR / "docs" / "observability" / ".publish_gate_state.json"`), so the filename is
    the final component."""
    for lit in reversed(literals):
        name = lit.rsplit("/", 1)[-1].strip()
        if not name or len(name) > 120:
            continue
        if name.endswith(_STATE_SUFFIXES):
            return name
        # A dotfile with no suffix (`.last_tested_hash`, `.human_last_input`) is state too.
        if name.startswith(".") and len(name) > 1 and "/" not in name and " " not in name:
            return name
    return None


def _string_literals(node: ast.AST) -> list[str]:
    return [n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _is_path_shaped(node: ast.AST) -> bool:
    """Is this assignment's value a PATH being carried, rather than a file's CONTENTS?

    `Path(path)`, `path or DEFAULT`, `base / "x.json"`, a bare rename. Anything else -- notably
    the result of a read -- is not, and treating it as one is how a parameter alias set turns
    into a taint over parsed data."""
    if isinstance(node, (ast.Name, ast.BinOp, ast.BoolOp, ast.IfExp)):
        return True
    if isinstance(node, ast.Call):
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        return name in {"Path", "str", "resolve", "expanduser", "absolute"}
    return False


def _module_state_symbols(tree: ast.Module) -> dict[str, str]:
    """{CONSTANT_NAME: state_file_name} for module-level path constants."""
    out: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        key = _state_key(_string_literals(node.value))
        if key is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                out[target.id] = key
    return out


class _FunctionScan:
    """Read/write/call facts for ONE function body, with intra-function alias tracking.

    Alias tracking is what makes the derivation survive the indirection real code uses:
    `sp = state_path or PUBLISH_GATE_STATE_FILE` then `Path(sp).read_text()` is a read of
    `.publish_gate_state.json`, and a census that missed it would under-report the class.

    AND THE SAME INDIRECTION ONE LEVEL OUT, WHICH COST THE CENSUS FIVE HITS. Symbol attribution
    only reaches a read written in the same function as the module constant. The moment a carrier
    is repaired by routing its read through a shared loader --
    `load_list_prior(RUN_HISTORY_PATH)` -- the `read_text()` moves into `episode_prior`, where the
    path is a PARAMETER and no module symbol names it, and the key is lost at the seam. So this
    scan also records which of its own PARAMETERS are read/written, and every call site's
    arguments; `_attribute_through_parameters` then walks a caller's keyed argument into the
    callee's parameter. See that function for the measurement."""

    def __init__(self, symbols: dict[str, str], params: tuple[str, ...] = ()) -> None:
        self.symbols = dict(symbols)
        self.reads: set[str] = set()
        self.writes: set[str] = set()
        self.calls: set[str] = set()
        self.except_writes: set[str] = set()   # writes lexically inside an `except` handler
        # PARAMETER-POSITION FACTS. `param_aliases` starts as the parameter names and grows only
        # through path-shaped assignments (`p = Path(path)`, `sp = path or DEFAULT`) -- never
        # through a read's RESULT, which would taint the parsed contents as if they were the path.
        self.params = tuple(params)
        #: {local name: the ORIGINAL parameters it stands for}. Keyed to the root parameter and
        #: not the alias, because attribution binds a caller's argument to a POSITION: recording
        #: `p` from `p = Path(path)` would mean nothing to a caller, which knows only `path`.
        self.param_aliases: dict[str, set[str]] = {p: {p} for p in params}
        self.param_reads: set[str] = set()
        self.param_writes: set[str] = set()
        #: (callee_name, positional descriptors, {kwarg: descriptor}). A descriptor is
        #: ("key", name) for a keyed expression, ("param", name) for one of OUR parameters, or
        #: None. Recorded rather than resolved here: resolution needs the whole repo's facts.
        self.callsites: list[tuple[str, list[Any], dict[str, Any]]] = []

    def _keys(self, node: ast.AST | None) -> set[str]:
        """Every state path an expression could denote -- all Names in it, mapped."""
        if node is None:
            return set()
        return {self.symbols[n.id] for n in ast.walk(node)
                if isinstance(n, ast.Name) and n.id in self.symbols}

    def _param_names(self, node: ast.AST | None) -> set[str]:
        """Every ORIGINAL parameter of THIS function an expression could denote, following
        aliases back to the parameter a caller can actually bind."""
        if node is None:
            return set()
        out: set[str] = set()
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                out |= self.param_aliases.get(n.id, set())
        return out

    def _descriptor(self, node: ast.AST | None) -> Any:
        """How a call argument names a state file: by key, by one of our parameters, or not."""
        keys = self._keys(node)
        if keys:
            return ("key", sorted(keys)[0])
        params = self._param_names(node)
        if params:
            return ("param", sorted(params)[0])
        return None

    @staticmethod
    def _is_write_mode(mode: str) -> bool:
        return any(c in _WRITE_MODE_CHARS for c in mode)

    def _mode_of(self, call: ast.Call, arg_index: int) -> str:
        args = call.args
        if len(args) > arg_index and isinstance(args[arg_index], ast.Constant) \
                and isinstance(args[arg_index].value, str):
            return args[arg_index].value
        for kw in call.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant) \
                    and isinstance(kw.value.value, str):
                return kw.value.value
        return "r"

    def visit(self, node: ast.AST, in_except: bool = False) -> None:
        if isinstance(node, ast.Assign):
            keys = self._keys(node.value)
            if keys:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.symbols[target.id] = sorted(keys)[0]
            elif _is_path_shaped(node.value):
                # `p = Path(path)` / `sp = path or DEFAULT`. Deliberately NOT any expression
                # mentioning a parameter: `raw = p.read_text()` would otherwise make the file's
                # CONTENTS an alias of its path, and the next call taking `raw` would be recorded
                # as a read of the state file. The shape screen is what keeps the two apart.
                roots = self._param_names(node.value)
                if roots:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.param_aliases[target.id] = set(roots)
        if isinstance(node, ast.Call):
            self._visit_call(node, in_except)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue  # nested defs are scanned as functions in their own right
            if isinstance(node, ast.Try) and child in node.handlers:
                self.visit(child, True)
            else:
                self.visit(child, in_except)

    def _record_write(self, keys: set[str], in_except: bool) -> None:
        self.writes |= keys
        if in_except:
            self.except_writes |= keys

    def _visit_call(self, call: ast.Call, in_except: bool) -> None:
        func = call.func
        if isinstance(func, ast.Attribute):
            self.calls.add(func.attr)
            self._record_callsite(func.attr, call)
            keys = self._keys(func.value)
            params = self._param_names(func.value)
            if func.attr in _WRITE_ATTRS:
                self._record_write(keys, in_except)
                self.param_writes |= params
            elif func.attr in _READ_ATTRS:
                self.reads |= keys
                self.param_reads |= params
            elif func.attr == "open":
                if self._is_write_mode(self._mode_of(call, 0)):
                    self._record_write(keys, in_except)
                    self.param_writes |= params
                else:
                    self.reads |= keys
                    self.param_reads |= params
            elif func.attr in {"replace", "move", "copy", "copyfile"} and len(call.args) >= 2:
                # os.replace(tmp, STATE) / shutil.move(...) -- the DESTINATION is written.
                self._record_write(self._keys(call.args[1]), in_except)
                self.param_writes |= self._param_names(call.args[1])
        elif isinstance(func, ast.Name):
            self.calls.add(func.id)
            self._record_callsite(func.id, call)
            if func.id == "open":
                arg = call.args[0] if call.args else None
                keys = self._keys(arg)
                params = self._param_names(arg)
                if self._is_write_mode(self._mode_of(call, 1)):
                    self._record_write(keys, in_except)
                    self.param_writes |= params
                else:
                    self.reads |= keys
                    self.param_reads |= params

    def _record_callsite(self, callee: str, call: ast.Call) -> None:
        """Keep a call site only if some argument names a state file or one of our parameters.

        The screen is not an optimisation: every call in the repo would otherwise become an edge
        in the parameter fixpoint, and a derivation that connects everything reports the same
        class as one that connects nothing."""
        positional = [self._descriptor(a) for a in call.args]
        keyword = {kw.arg: self._descriptor(kw.value) for kw in call.keywords if kw.arg}
        keyword = {k: v for k, v in keyword.items() if v is not None}
        if any(d is not None for d in positional) or keyword:
            self.callsites.append((callee, positional, keyword))


def _param_names_of(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, ...]:
    """Positional parameter names, in call order, plus keyword-only ones. `*args`/`**kwargs` are
    left out: a state path passed through them cannot be attributed to a position anyway, and
    inventing one would attribute it to the wrong parameter."""
    a = node.args
    ordered = [p.arg for p in (*a.posonlyargs, *a.args)]
    return tuple(ordered + [p.arg for p in a.kwonlyargs])


def _scan_module(path: Path, project_dir: Path) -> dict[str, dict[str, Any]]:
    """{qualified_function_name: facts} for one module. Unparseable source is skipped rather
    than raised -- a syntax error in an unrelated tool must not blind the whole census (and the
    vacuity guard, not silence, is what catches a scan that stops working)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {}
    module = path.relative_to(project_dir).as_posix()
    symbols = _module_state_symbols(tree)
    out: dict[str, dict[str, Any]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        scan = _FunctionScan(symbols, _param_names_of(node))
        for child in node.body:
            scan.visit(child)
        out["{}::{}".format(module, node.name)] = {
            "module": module,
            "name": node.name,
            "params": list(scan.params),
            "param_reads": sorted(scan.param_reads),
            "param_writes": sorted(scan.param_writes),
            "callsites": scan.callsites,
            "reads": sorted(scan.reads),
            "writes": sorted(scan.writes),
            # DIRECT writes stay separate from the propagated set below. The distinction is what
            # keeps the census readable: a daemon's `main()` transitively writes every state file
            # its cycle touches and notifies about every one of them, so a rule that did not
            # measure DISTANCE between the write and the alarm would tag all 27 of them and the
            # census would be read exactly as reliably as no census.
            "direct_writes": sorted(scan.writes),
            "except_writes": sorted(scan.except_writes),
            "calls": sorted(scan.calls),
        }
    return out


def _resolve_calls(facts: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    """Call graph over qualified function names. A call resolves to a same-module definition
    first, else to the unique repo-wide definition of that name; an ambiguous name (defined in
    several modules) is dropped rather than guessed -- an over-connected graph would propagate
    reads/writes into functions that never touch the file and inflate the class."""
    by_name: dict[str, list[str]] = {}
    for qual, f in facts.items():
        by_name.setdefault(f["name"], []).append(qual)
    edges: dict[str, set[str]] = {}
    for qual, f in facts.items():
        targets: set[str] = set()
        for called in f["calls"]:
            candidates = by_name.get(called, [])
            same = [c for c in candidates if facts[c]["module"] == f["module"]]
            if same:
                targets.update(same)
            elif len(candidates) == 1:
                targets.add(candidates[0])
        targets.discard(qual)
        edges[qual] = targets
    return edges


def _attribute_through_parameters(facts: dict[str, dict[str, Any]]) -> int:
    """Walk a keyed ARGUMENT into the callee's PARAMETER, to a fixpoint. Returns how many
    (function, key) read/write facts this recovered.

    WHY THIS EXISTS, MEASURED. The census attributes a state file by module-level symbol, so it
    sees `RUN_HISTORY_PATH.read_text()` and not `load_list_prior(RUN_HISTORY_PATH)`. On
    2026-09-05 the loader sweep repaired six carriers by routing every one of them through
    `background/episode_prior`, whose loaders take the path as an argument -- and the census
    derived over the tree before and after that commit LOST FIVE HITS:
    `run_history.json`, `.harden_cooldown.json`, `.ntfy_digest_state.json`,
    `.supervisor_map_exhausted_state.json` and `retired_paths_served.json` went from 34 hits to
    29, with `run_history.json` dropping to ZERO recorded readers while
    `count_run_history_total` reads it on every dashboard build.

    That is the census's fail-open shape and it was getting STRONGER WITH ADOPTION: the more
    correctly a carrier was repaired -- through the shared helper rather than a hand-rolled loop,
    which is what this project asks for -- the more certainly it left the class the census
    enumerates. `census_is_vacuous()` cannot see it, because it only refuses a TOTALLY empty
    census; `undispositioned()` cannot see it, because it checks hits missing a row and never a
    row whose hit disappeared. A path that stops being a hit needs no disposition and `--check`
    exits 0.

    A parameter is read/written if the callee reads/writes it, transitively through further
    parameter passing -- hence the fixpoint rather than one hop. Attribution is by POSITION for
    positional arguments and by NAME for keywords, and a keyed argument landing on a read
    parameter is a read of that key BY THE CALLER, which is the fact that was missing.

    Recovered writes join `direct_writes` as well as `writes`, deliberately:
    `_writes_at_close_range` already counts "through one hop into a writer helper" as writing it
    yourself, and `preserve_unreadable(STATE_PATH)` is exactly that hop."""
    by_name: dict[str, list[str]] = {}
    for qual, f in facts.items():
        by_name.setdefault(f["name"], []).append(qual)

    def resolve(callee: str, module: str) -> list[str]:
        """Same-module definition first, else the unique repo-wide one. An ambiguous name is
        dropped rather than guessed -- `_resolve_calls` states the reason and it holds here."""
        candidates = by_name.get(callee, [])
        same = [c for c in candidates if facts[c]["module"] == module]
        if same:
            return same
        return candidates if len(candidates) == 1 else []

    recovered = 0
    changed = True
    while changed:
        changed = False
        for qual, f in facts.items():
            for callee, positional, keyword in f["callsites"]:
                for target in resolve(callee, f["module"]):
                    if target == qual:
                        continue
                    g = facts[target]
                    params = g["params"]
                    bound = [(params[i], d) for i, d in enumerate(positional)
                             if d is not None and i < len(params)]
                    bound += [(k, d) for k, d in keyword.items() if k in params]
                    for pname, (kind, name) in bound:
                        for role, key_fields, param_field in (
                            ("param_reads", ("reads",), "param_reads"),
                            ("param_writes", ("writes", "direct_writes"), "param_writes"),
                        ):
                            if pname not in g[role]:
                                continue
                            if kind == "key":
                                for field in key_fields:
                                    if name not in f[field]:
                                        f[field] = sorted(set(f[field]) | {name})
                                        changed = True
                                        recovered += 1
                            elif name not in f[param_field]:
                                # The caller is itself a pass-through: its own parameter is now
                                # known to be read/written, so ITS callers can be attributed too.
                                f[param_field] = sorted(set(f[param_field]) | {name})
                                changed = True
    return recovered


def _propagate(facts: dict[str, dict[str, Any]], edges: dict[str, set[str]]) -> None:
    """Fixpoint: a caller reads/writes whatever its callees read/write.

    This is the step that makes the census a derivation rather than a grep.
    `record_publish_gate_failure` contains no file call at all -- it writes
    `.publish_gate_state.json` only through `_write_publish_gate_state`, and an analysis that
    stopped at the syntactic call site would miss the very instance the steer is about."""
    changed = True
    while changed:
        changed = False
        for qual, callees in edges.items():
            reads = set(facts[qual]["reads"])
            writes = set(facts[qual]["writes"])
            for callee in callees:
                reads |= set(facts[callee]["reads"])
                writes |= set(facts[callee]["writes"])
            if reads != set(facts[qual]["reads"]) or writes != set(facts[qual]["writes"]):
                facts[qual]["reads"] = sorted(reads)
                facts[qual]["writes"] = sorted(writes)
                changed = True


def _reachable(seed: str, edges: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    stack = [seed]
    while stack:
        cur = stack.pop()
        for nxt in edges.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def _invert(edges: dict[str, set[str]]) -> dict[str, set[str]]:
    back: dict[str, set[str]] = {q: set() for q in edges}
    for src, dsts in edges.items():
        for dst in dsts:
            back.setdefault(dst, set()).add(src)
    return back


def _reaches_notifier(qual, facts, edges) -> str | None:
    """Does this function raise the alarm itself, or reach something that does?"""
    if _NOTIFIER_NAMES & set(facts[qual]["calls"]):
        return "calls a notifier directly"
    for callee in _reachable(qual, edges):
        if facts[callee]["name"] in _NOTIFIER_NAMES:
            return "reaches notifier {}".format(facts[callee]["name"])
    return None


def _writes_at_close_range(qual, key, facts, edges) -> bool:
    """Does this function write `key` ITSELF, or through one hop into a writer helper?

    One hop, not the full closure: `record_publish_gate_failure` writes `.publish_gate_state.json`
    only via `_write_publish_gate_state`, and a rule that demanded a syntactic write would miss the
    very instance the steer is about. Beyond one hop the write belongs to the callee, not to this
    function's failure path -- and without that bound a daemon's `main()` is a failure writer for
    every state file its cycle touches, which is a census nobody reads."""
    if key in facts[qual]["direct_writes"]:
        return True
    return any(key in facts[c]["direct_writes"] for c in edges.get(qual, ()))


def _failure_reason(qual, key, facts, edges, back) -> str | None:
    """Why this writer counts as a FAILURE path -- the recorded reason, or None.

    Every rule is gated on `_writes_at_close_range`: you are a failure writer for a path only if
    you actually write it, not because something you eventually call does.

    The rules that need NO lexicon are the load-bearing ones. Read-modify-write of a control's own
    state is the class at its most structural -- `run_operational_layer_signal` reads
    `consecutive_red` and writes it back, and no naming or notifier rule caught it: it notifies
    nobody and says nothing about failure in its name (the deadman's `run_cycle` pages one level
    up). Writing the state AND raising the alarm in the same path is the steer's own phrasing."""
    if not _writes_at_close_range(qual, key, facts, edges):
        return None
    if _FAILURE_RE.search(facts[qual]["name"]):
        return "name matches the failure lexicon"
    if key in facts[qual]["except_writes"]:
        return "writes the path inside an except handler"
    if key in facts[qual]["reads"]:
        return "read-modify-writes its own state (a failure outcome overwrites the episode)"
    reaches = _reaches_notifier(qual, facts, edges)
    if reaches:
        return "writes the path and raises the alarm in the same path ({})".format(reaches)
    for caller in back.get(qual, ()):
        if _FAILURE_RE.search(facts[caller]["name"]):
            return "called from {}".format(facts[caller]["name"])
    return None


def _alarm_reason(qual, facts, edges, back) -> str | None:
    """Why this reader counts as an ALARM/severity read -- the recorded reason, or None."""
    if _ALARM_RE.search(facts[qual]["name"]):
        return "name matches the alarm lexicon"
    reaches = _reaches_notifier(qual, facts, edges)
    if reaches:
        return reaches
    for caller in back.get(qual, ()):
        if _ALARM_RE.search(facts[caller]["name"]):
            return "called from {}".format(facts[caller]["name"])
    return None


def _blank_record() -> dict[str, list]:
    return {"writers": [], "readers": [], "failure_writers": [], "alarm_readers": []}


def _index_paths(facts, edges, back) -> dict[str, dict[str, Any]]:
    """Per state path: who writes it, who reads it, and which of those are on a failure path /
    in an alarm. The INTERSECTION of the last two is the census hit."""
    paths: dict[str, dict[str, Any]] = {}
    for qual, f in facts.items():
        for key in f["writes"]:
            rec = paths.setdefault(key, _blank_record())
            rec["writers"].append(qual)
            reason = _failure_reason(qual, key, facts, edges, back)
            if reason:
                rec["failure_writers"].append({"fn": qual, "why": reason})
        for key in f["reads"]:
            rec = paths.setdefault(key, _blank_record())
            rec["readers"].append(qual)
            reason = _alarm_reason(qual, facts, edges, back)
            if reason:
                rec["alarm_readers"].append({"fn": qual, "why": reason})

    for rec in paths.values():
        rec["writers"] = sorted(set(rec["writers"]))
        rec["readers"] = sorted(set(rec["readers"]))
        rec["failure_writers"] = sorted(rec["failure_writers"], key=lambda d: d["fn"])
        rec["alarm_readers"] = sorted(rec["alarm_readers"], key=lambda d: d["fn"])
        # THE INTERSECTION. A hit is a path a failure writes AND an alarm reads -- the shape in
        # which a failure can shorten the episode its own alarm is about to report.
        rec["hit"] = bool(rec["failure_writers"] and rec["alarm_readers"])
    return paths


def derive(roots: tuple[str, ...] = SCAN_ROOTS,
           project_dir: Path = PROJECT_DIR) -> dict[str, Any]:
    """THE DERIVATION: writer set intersected with reader set, per state path, over the live tree.

    Returns the full census. Every field is recomputed from source; nothing is read back from a
    previous artefact (anti-tautology)."""
    facts: dict[str, dict[str, Any]] = {}
    for path in _iter_source_files(roots, project_dir):
        facts.update(_scan_module(path, project_dir))
    # BEFORE the call-graph closure, not after: a key recovered at a parameter seam has to be
    # available to propagate up to the callers, which is where the alarm and failure readings
    # are taken.
    parameter_attributions = _attribute_through_parameters(facts)
    edges = _resolve_calls(facts)
    _propagate(facts, edges)
    paths = _index_paths(facts, edges, _invert(edges))
    return {
        "scan_roots": list(roots),
        "functions_scanned": len(facts),
        # Recorded so the seam attribution is visible in the artefact rather than implicit in a
        # hit count. Zero here with a non-empty tree means the parameter walk stopped matching --
        # the erosion this field exists to make loud.
        "parameter_attributions": parameter_attributions,
        "state_paths": dict(sorted(paths.items())),
        "hits": sorted(k for k, v in paths.items() if v["hit"]),
        "classifiers": {
            "failure_lexicon": _FAILURE_RE.pattern,
            "alarm_lexicon": _ALARM_RE.pattern,
            "notifiers": sorted(_NOTIFIER_NAMES),
            "note": ("writer/reader membership is derived by AST + call-graph closure; FAILURE "
                     "and ALARM membership are derived classifiers over these recorded rules, "
                     "and each hit carries the reason it was tagged."),
        },
    }


def census_is_vacuous(census: dict[str, Any]) -> str | None:
    """R15 VACUITY GUARD. The fail-open shape for a census is finding NOTHING and reading as
    clean -- a renamed attribute or a moved root would do exactly that, silently. Returns the
    reason the census must not be believed, or None if it is substantive."""
    if census.get("functions_scanned", 0) < 100:
        return "only {} functions scanned -- the roots did not resolve".format(
            census.get("functions_scanned", 0))
    paths = census.get("state_paths") or {}
    if not paths:
        return "no state paths resolved at all -- the path derivation has stopped matching"
    if not any(p["writers"] for p in paths.values()):
        return "no writers found on any state path -- the write derivation has stopped matching"
    if not any(p["readers"] for p in paths.values()):
        return "no readers found on any state path -- the read derivation has stopped matching"
    if not census.get("hits"):
        return "zero hits on a tree known to contain the publish-gate instance -- the census is blind"
    return None


def load_dispositions(path: Path | None = None) -> dict[str, dict[str, str]]:
    """The AUTHORED half: {state_file: {"verdict": "real"|"benign", "why": ...}}. Absent or
    malformed yields {} -- which makes every hit undispositioned and `--check` RED, never green
    (fail toward work, never toward silence)."""
    p = path if path is not None else DISPOSITIONS_PATH
    try:
        data = json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
    rows = data.get("dispositions") if isinstance(data, dict) else None
    return rows if isinstance(rows, dict) else {}


#: The AUTHORED record of a row deliberately taken OUT of the register: {state_file: reason}. The
#: only thing that distinguishes a carrier genuinely deleted from the tree from the register being
#: quietly tidied to match a census that went blind -- which, from the census alone, are the same
#: observation. Same shape and same reasoning as `DECLASSIFIED_FIELD` one rung over.
RETIRED_SECTION = "_retired"


def load_retired(path: Path | None = None) -> dict[str, str]:
    """The `_retired` section: {state_file: why it left the register}. Absent or malformed yields
    {} -- which makes every removal unexplained and `--check` RED, never green. Same direction of
    failure as `load_dispositions`: toward work, never toward silence."""
    p = path if path is not None else DISPOSITIONS_PATH
    try:
        data = json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
    rows = data.get(RETIRED_SECTION) if isinstance(data, dict) else None
    return rows if isinstance(rows, dict) else {}


def _dispositions_at_head() -> dict[str, dict[str, str]] | None:
    """The register as HEAD has it -- the baseline `removed_dispositions()` measures against.

    Returns None, never {}, when the baseline cannot be established. The two are opposite claims:
    {} says "HEAD's register was empty, so nothing can have been removed" and would report clean on
    every tree where git is unavailable, which is the fail-silent shape this whole module exists to
    refuse. The caller turns None into a refusal that names itself.

    `git show HEAD:<path>` and not a working-tree read: the point is to compare the working copy
    against the last committed judgement, and it resolves correctly from a linked worktree, which
    is the only environment `seat_executor` runs in.
    """
    rel = DISPOSITIONS_PATH.relative_to(PROJECT_DIR)
    try:
        proc = subprocess.run(["git", "show", "HEAD:{}".format(rel.as_posix())],
                              cwd=PROJECT_DIR, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        return None
    rows = data.get("dispositions") if isinstance(data, dict) else None
    return rows if isinstance(rows, dict) else None


def removed_dispositions(dispositions: dict[str, dict[str, str]] | None = None,
                         retired: dict[str, str] | None = None,
                         baseline: dict[str, dict[str, str]] | None = None) -> list[str]:
    """THE REGISTER'S LOW-WATER MARK: a row that was in the register at HEAD and is not in it now.

    `eroded_dispositions()` asks whether a ROW still has a HIT. It is the inverse of
    `undispositioned()` and it closed a real hole. But it iterates `sorted(disp)`, so its subject
    set IS the register, and its own docstring rests the whole non-tautology argument on the
    register being a HIGH-WATER mark. Nothing made the mark unable to fall. Measured on the live
    tree on 2026-09-05, before this existed: take a row that is currently a hit, delete the row and
    the hit together, and `undispositioned`, `eroded_dispositions`, `unasked_loader_rows`,
    `unguarded_real_hits` and `census_is_vacuous` ALL return clean. A key in neither the hits nor
    the rows is the subject of nothing.

    THE SECOND-ORDER SHAPE, which is why this is not merely a missing rung. `eroded_dispositions()`
    REFUSES a row whose path the census can no longer resolve. Deleting that row clears the
    refusal. A control whose red can be cleared by deleting the evidence is a fail-open with an
    extra step, and every rung here would have gone on reporting a clean class.

    NO CENSUS-SHAPE EXCEPTION, AND THAT IS THE DESIGN. The tempting rule is "allow the removal if
    the census no longer resolves the path anyway -- the carrier is gone from the tree". That is
    exactly the fail-open above. `eroded_dispositions()` refuses the path-gone case precisely
    BECAUSE a genuinely deleted carrier and a derivation gone blind are the same observation from
    the census alone; granting that case a free pass here would hand row-deletion the cure. Only an
    authored sentence can tell them apart, so the only way out is `_retired` with a reason -- the
    same shape, and the same argument, as `declassified` one rung over.

    WHERE IT BITES. The baseline is HEAD, so this is a commit-time ratchet against the WORKING
    copy: you cannot drop a row in a commit without saying why. Once a bad commit has landed, HEAD
    contains the loss and this goes quiet again -- said plainly rather than implied, because the
    gates run pre-commit on the working tree and that is the whole enforcement point. It is where
    `9857c0edb` -- the rewrite from a pre-sweep copy that deleted 33 annotations -- would have been
    stopped.

    Takes its baseline as an argument so the control can be driven without a git tree, and defaults
    to reading HEAD so the live rung has no fixture to drift from.
    """
    disp = load_dispositions() if dispositions is None else dispositions
    ret = load_retired() if retired is None else retired
    base = _dispositions_at_head() if baseline is None else baseline
    if base is None:
        return ["the register's baseline at HEAD could not be established (git show failed, or "
                "HEAD's copy is absent or unparseable), so whether a row has been removed cannot "
                "be answered -- this is a refusal, not a clean result"]
    out: list[str] = []
    for key in sorted(set(base) - set(disp)):
        # `or ""` BEFORE `str`, not `.get(key, "")`: a `_retired` entry carrying an explicit JSON
        # `null` stringifies to "None", which is truthy, and the reason requirement falls open.
        # The same slip was live in `undispositioned` and `eroded_dispositions` until 2026-09-05;
        # an absurdity is fixed as a class, so the new escape hatch is born with the treatment.
        if not str(ret.get(key) or "").strip():
            out.append("{} -- this row was in the register at HEAD and is not in it now, and "
                       "`{}` does not say why. A row is the only record that this carrier was ever "
                       "in the class; removing it removes the alarm that its hit vanished. Restore "
                       "it, or add `{}[\"{}\"]` naming what took the carrier out of the tree.".format(
                           key, RETIRED_SECTION, RETIRED_SECTION, key))
    return out


def undispositioned(census: dict[str, Any], dispositions: dict[str, dict[str, str]] | None = None
                    ) -> list[str]:
    """Hits with no verdict on record. This is what gives the census teeth: a NEW control of this
    shape lands RED rather than joining the class quietly."""
    disp = load_dispositions() if dispositions is None else dispositions
    out = []
    for key in census.get("hits", []):
        row = disp.get(key)
        if not isinstance(row, dict) or row.get("verdict") not in {"real", "benign"}:
            out.append(key)
        elif row["verdict"] == "benign" and not str(row.get("why") or "").strip():
            # `or ""` BEFORE `str`: `{"verdict": "benign", "why": null}` stringified to "None",
            # which is truthy, so a row asserting nothing passed as a disposition. Found
            # 2026-09-05 by the inverse control's own partition leg, and repaired in both places.
            out.append(key)  # "benign" with no reason is not a disposition
    return out


#: A row may stop being a hit for an HONEST reason: the control was repaired, and its failure path
#: no longer writes what its alarm reads. That is a change of CLASSIFICATION, not a loss of the
#: subject, and the row records it here in prose. It is deliberately NOT an escape hatch for the
#: census going blind -- a path with no writers or no readers at all is not declassified, it is
#: LOST, and this field does not excuse it.
DECLASSIFIED_FIELD = "declassified"
#: The field carrying a row's answer to `_scope_of_benign` -- absent vs present-but-unreadable.
LOADER_FIELD = "loader"


def eroded_dispositions(census: dict[str, Any],
                        dispositions: dict[str, dict[str, str]] | None = None) -> list[str]:
    """THE INVERSE OF `undispositioned()`: a dispositioned row whose census hit has DISAPPEARED.

    `undispositioned()` asks "is there a hit with no row". Until 2026-09-05 nothing asked the other
    direction, and that is the door the class walked out of. On 2026-09-05 the loader sweep repaired
    six carriers by routing their reads through a shared loader; the census attributes a state file
    by module-level symbol, so the key died at the parameter seam and FIVE paths left the census
    altogether -- `run_history.json` dropping to ZERO recorded readers while `count_run_history_total`
    read it on every dashboard build. Twelve more had eroded the same way in earlier eras. Nothing
    could notice: `census_is_vacuous()` refuses only a TOTALLY empty census, and a path that stops
    being a hit needs no disposition, so `--check` exited 0 the whole time. **The instrument should
    fail loud on a SHRINKING subject set, not only on an empty one.**

    THE DISPOSITIONS FILE IS THE HIGH-WATER MARK, and that is why this is not a tautology. The
    obvious implementation -- remember last run's hit count and refuse a drop -- would read the
    census's own prior output to decide whether the census is right, which is the first thing this
    module's header forbids. `undispositioned()` already forces every hit to acquire an AUTHORED
    row, so the row set is a human-attested record of what the class contained, kept in git,
    reviewable, and derived from nothing. Checking today's derivation against it is checking source
    against judgement, not against yesterday's source.

    THE PARTITION, and the split is the whole design. A row can stop being a hit four ways:

      * the path is gone from `state_paths` entirely -- the derivation lost it;
      * the path is there with NO writers -- the write derivation went blind on it;
      * the path is there with NO readers -- the read derivation went blind on it (this is exactly
        `run_history.json` at the parameter seam);
      * the path is fully visible, written AND read, but the classifiers no longer tag a FAILURE
        writer or an ALARM reader.

    Only the last of those is what a genuine REPAIR looks like, so only the last can be excused --
    and only by a row that authors `declassified` with a reason. **Refusing every non-hit row
    outright would make this control go red precisely when the code became more honest**, which is
    this project's named backwards-control shape (`feedback_key_a_control_to_the_property`). The
    first three are not repairs and no field excuses them: the census cannot see its own subject,
    and that state is indistinguishable from the erosion this exists to catch.

    Returns one line per eroded row, each naming which leg it failed on -- a refusal that says why
    is how you find out the refusal itself was wrong.
    """
    disp = load_dispositions() if dispositions is None else dispositions
    paths = census.get("state_paths") or {}
    hits = set(census.get("hits") or [])
    out: list[str] = []
    for key in sorted(disp):
        if key in hits:
            continue
        row = disp[key] if isinstance(disp[key], dict) else {}
        rec = paths.get(key)
        if not isinstance(rec, dict):
            out.append("{} -- dispositioned, but the census no longer resolves the path at "
                       "all".format(key))
        elif not rec.get("writers"):
            out.append("{} -- dispositioned, still read by {} function(s), but the census records "
                       "NO WRITERS: the write derivation went blind on it".format(
                           key, len(rec.get("readers") or [])))
        elif not rec.get("readers"):
            out.append("{} -- dispositioned, still written by {} function(s), but the census "
                       "records NO READERS: the read derivation went blind on it".format(
                           key, len(rec.get("writers") or [])))
        # `or ""` BEFORE `str`, not `.get(field, "")`: a row carrying an explicit JSON `null`
        # stringifies to "None", which is truthy, and the reason requirement falls open. Caught by
        # the partition leg below on its first run, and the same slip is one line up in
        # `undispositioned` -- fixed there too rather than here only (an absurdity is a class).
        elif not str(row.get(DECLASSIFIED_FIELD) or "").strip():
            out.append("{} -- dispositioned and still written ({}) and read ({}), but no longer a "
                       "hit, and the row does not say why: add `{}` naming the repair that took "
                       "it out of the class, or remove the row".format(
                           key, len(rec.get("writers") or []), len(rec.get("readers") or []),
                           DECLASSIFIED_FIELD))
    return out


def unasked_loader_rows(census: dict[str, Any],
                        dispositions: dict[str, dict[str, str]] | None = None) -> list[str]:
    """A HIT WHOSE ROW HAS NO `loader` FIELD -- the answer to the question `_scope_of_benign` asks.

    `benign` answers ONE question: can a write SHORTEN an episode. It says nothing about whether
    the carrier's loader tells ABSENT from PRESENT-BUT-UNREADABLE, and a seen-set or a
    read-modify-write store can be perfectly benign on the episode question while destroying its
    own record on a corrupt read. The dispositions file has said in prose since the 2026-09-05
    sweep that a row without a `loader` "has not been asked, which is a gap and not a pass". That
    sentence had no falsifier, and it cost 33 rows the same day it was written: `c30738d77`
    annotated all 46, `9857c0edb` rewrote the file nine hours later from a pre-sweep copy and
    deleted 33 of the annotations, and the merge to origin diffed its resolution against the
    rewriting side's own copy, so neither side could see the loss. `--check` was green throughout.

    WHY THE THREE EXISTING RUNGS ALL MISS IT. `undispositioned()` is satisfied by a verdict and a
    reason. `unguarded_real_hits()` interrogates `real` rows only, and 27 of the 33 lost rows are
    `benign`. `eroded_dispositions()` -- the erosion inverse, which landed in the same MINUTE as
    this erosion -- asks whether a dispositioned row still has a hit; every one of the 33 still
    did. Each rung guards the row's EXISTENCE or its VERDICT; none guarded its ANSWER.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. It does not compare against a remembered set or
    a recorded count, so it cannot go red for becoming more honest: it fires on a row with no
    answer, identically whether the row never had one or lost one, and a genuinely new hit lands
    RED until someone opens its loader -- which is the same teeth `undispositioned()` has.

    `or ""` BEFORE `str`: a row carrying an explicit JSON `null` stringifies to "None", which is
    truthy, and a mandatory field falls open. The same slip is live twice above and fixed there.
    """
    disp = load_dispositions() if dispositions is None else dispositions
    out = []
    for key in census.get("hits", []):
        row = disp.get(key)
        if not isinstance(row, dict):
            continue  # no row at all is `undispositioned()`'s refusal, not this one
        if not str(row.get(LOADER_FIELD) or "").strip():
            out.append("{} -- dispositioned `{}` but its row has no `{}`: nobody has asked whether "
                       "its loader tells ABSENT from PRESENT-BUT-UNREADABLE".format(
                           key, row.get("verdict") or "?", LOADER_FIELD))
    return out


def unguarded_real_hits(census: dict[str, Any],
                        dispositions: dict[str, dict[str, str]] | None = None) -> list[str]:
    """PW4 -- `real` hits whose guard is not yet BUILT and NAMED by a test that exists.

    Without this the `guard` field would be a prose inventory with no falsifier: four rows could
    say `guarded` while nothing guarded anything, and the census would read exactly as reliably
    as no census (`feedback_prose_inventory_needs_a_falsifier`). A row is satisfied only when
    `guard == "guarded"` AND its `why` cites a test path that is on disk -- the citation is
    checked against the filesystem, not taken on the row's word.

    `registered` is the honest interim state and stays RED on `--check`: PW2 used it for the
    four episodes whose close condition had not been chosen yet, and a control registered but
    never built is exactly the debt this is meant to keep visible."""
    disp = load_dispositions() if dispositions is None else dispositions
    out = []
    for key in census.get("hits", []):
        row = disp.get(key)
        if not isinstance(row, dict) or row.get("verdict") != "real":
            continue
        if row.get("guard") != "guarded":
            out.append("{} (guard={})".format(key, row.get("guard") or "MISSING"))
            continue
        cited = [tok.rstrip(".,;:") for tok in str(row.get("why", "")).split()
                 if tok.startswith("tests/")]
        named = [c.split("::")[0] for c in cited]
        if not named or not any((PROJECT_DIR / n).exists() for n in named):
            out.append("{} (guard=guarded but names no test that exists)".format(key))
    return out


def write_census(census: dict[str, Any] | None = None, path: Path | None = None) -> Path:
    census = derive() if census is None else census
    out = path if path is not None else CENSUS_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(census, indent=2, sort_keys=True) + "\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="read-only: exit 1 on a vacuous census, an undispositioned hit, an "
                         "unguarded real hit, an eroded row, an unasked loader question or a row "
                         "removed from the register without a reason")
    args = ap.parse_args()
    census = derive()
    vacuous = census_is_vacuous(census)
    if vacuous:
        print("CENSUS VACUOUS (R15): {}".format(vacuous))
        return 1
    print("{} functions scanned, {} state paths, {} hits".format(
        census["functions_scanned"], len(census["state_paths"]), len(census["hits"])))
    disp = load_dispositions()
    for key in census["hits"]:
        row = disp.get(key) or {}
        print("  {:<44} {:<8} {}".format(key, row.get("verdict", "UNDISPOSITIONED"),
                                         row.get("why", "")[:90]))
    missing = undispositioned(census, disp)
    unguarded = unguarded_real_hits(census, disp)
    eroded = eroded_dispositions(census, disp)
    unasked = unasked_loader_rows(census, disp)
    removed = removed_dispositions(disp)
    if not args.check:
        write_census(census)
        print("census written to {}".format(CENSUS_PATH))
    if missing:
        print("UNDISPOSITIONED HITS: {}".format(", ".join(missing)))
    if unguarded:
        print("REAL HITS NOT YET GUARDED: {}".format(", ".join(unguarded)))
    if eroded:
        print("DISPOSITIONED ROWS WHOSE HIT HAS DISAPPEARED (the census's subject set is "
              "shrinking):")
        for line in eroded:
            print("  {}".format(line))
    if unasked:
        print("DISPOSITIONED HITS WHOSE LOADER QUESTION HAS NEVER BEEN ASKED (or whose answer has "
              "been deleted):")
        for line in unasked:
            print("  {}".format(line))
    if removed:
        print("ROWS REMOVED FROM THE REGISTER WITHOUT A REASON (the register's high-water mark is "
              "falling, and the row is the only record the carrier was ever in the class):")
        for line in removed:
            print("  {}".format(line))
    if missing or unguarded or eroded or unasked or removed:
        return 1
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/self_clearing_alarm_census.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("self_clearing_alarm_census")
    raise SystemExit(main())
