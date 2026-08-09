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
    `.publish_gate_state.json`, and a census that missed it would under-report the class."""

    def __init__(self, symbols: dict[str, str]) -> None:
        self.symbols = dict(symbols)
        self.reads: set[str] = set()
        self.writes: set[str] = set()
        self.calls: set[str] = set()
        self.except_writes: set[str] = set()   # writes lexically inside an `except` handler

    def _keys(self, node: ast.AST | None) -> set[str]:
        """Every state path an expression could denote -- all Names in it, mapped."""
        if node is None:
            return set()
        return {self.symbols[n.id] for n in ast.walk(node)
                if isinstance(n, ast.Name) and n.id in self.symbols}

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
            keys = self._keys(func.value)
            if func.attr in _WRITE_ATTRS:
                self._record_write(keys, in_except)
            elif func.attr in _READ_ATTRS:
                self.reads |= keys
            elif func.attr == "open":
                if self._is_write_mode(self._mode_of(call, 0)):
                    self._record_write(keys, in_except)
                else:
                    self.reads |= keys
            elif func.attr in {"replace", "move", "copy", "copyfile"} and len(call.args) >= 2:
                # os.replace(tmp, STATE) / shutil.move(...) -- the DESTINATION is written.
                self._record_write(self._keys(call.args[1]), in_except)
        elif isinstance(func, ast.Name):
            self.calls.add(func.id)
            if func.id == "open":
                keys = self._keys(call.args[0]) if call.args else set()
                if self._is_write_mode(self._mode_of(call, 1)):
                    self._record_write(keys, in_except)
                else:
                    self.reads |= keys


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
        scan = _FunctionScan(symbols)
        for child in node.body:
            scan.visit(child)
        out["{}::{}".format(module, node.name)] = {
            "module": module,
            "name": node.name,
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
    edges = _resolve_calls(facts)
    _propagate(facts, edges)
    paths = _index_paths(facts, edges, _invert(edges))
    return {
        "scan_roots": list(roots),
        "functions_scanned": len(facts),
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
        elif row["verdict"] == "benign" and not str(row.get("why", "")).strip():
            out.append(key)  # "benign" with no reason is not a disposition
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
                    help="read-only: exit 1 on a vacuous census or an undispositioned hit")
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
    if not args.check:
        write_census(census)
        print("census written to {}".format(CENSUS_PATH))
    if missing:
        print("UNDISPOSITIONED HITS: {}".format(", ".join(missing)))
    if unguarded:
        print("REAL HITS NOT YET GUARDED: {}".format(", ".join(unguarded)))
    if missing or unguarded:
        return 1
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/self_clearing_alarm_census.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("self_clearing_alarm_census")
    raise SystemExit(main())
