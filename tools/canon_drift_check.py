#!/usr/bin/env python3
"""Something other than the director asks what the page claims that the code no longer supports.

REUSE: tools/canon_drift_check.py
CLASS: CUSTOM
INDEX: searched "drift", "canon", "claim", "attest", "consistency", "surface". Three neighbours and
       why none of them is this. `tools/publish_surface_gate.py` and
       `tools/record_landing_claim_check.py` both check that a CLAIM MADE IN THIS COMMIT is backed
       -- their subject is the act of publishing, and they say nothing about a page that was true
       when it was written and stopped being true afterwards, which is the entire defect here
       (C1 and C2 sat wrong for weeks past their own commits). `background/finding_severity.py`
       parses documents but classifies their headers, never their content against code.
       `tools/epistemic_wall.py` and `tools/company_network_isolation.py` are the closest in SHAPE
       -- AST walks over the tree asserting a property -- and both are REUSED here in spirit
       rather than in code: their property is fixed in Python, and this one is DATA
       (docs/design/canon_claims.yaml), because a claim register that needs a code change per
       claim would never keep up with a page. Nothing existing reads a document and a module and
       reports which of the two moved.

WHY THIS EXISTS
---------------
Director, 2026-08-28 (`DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28.md`, §"One addition to
the delivery seat's subjects"):

    "Today's three corrections were found because the director and advisor happened to read the
     page -- no mechanism ever checks it, so the mission sits structurally outside the machine's
     field of view. Every orientation should ask not only what is drifting in the work, but what
     the page claims that the code no longer supports. That check would have caught C1 and C2
     weeks ago, and it is the machine's job rather than the director's."

All three corrections were GREPPABLE the whole time. C1's traits were read by no response
function; C2's competitor was eleven design documents and no module; C3's collateral was a fixed
cost line and never a call. Nothing about finding them needed judgement -- it needed someone to
look. This module is the someone.

THE DIRECTION RUNS BOTH WAYS, and that is the design constraint that shapes everything below.
C1 came back PARTLY SUPERSEDED: a channel for `price_sensitivity` landed on 2026-08-27, the day
BEFORE the guidance was drafted, so the page was under-claiming, not over-claiming. A drift check
that can only report the page over-claiming would have got C1 wrong in the confident direction --
it would have "confirmed" a claim that had already stopped being true. So a claim carries an
EXPECTED state and the report names which way it moved:

    HOLDS       the code still shows what the page says it shows
    OVER_CLAIM  the page claims a capability the code no longer supports
    SUPERSEDED  the code has moved past the page -- the page under-claims
    UNBOUND     the register's anchor sentence is no longer ON the page (register is stale)
    ERROR       the probe could not run at all -- FAIL CLOSED, never a pass. Includes VACUOUS: an
                absent-claim whose subject exists in no live code, so finding nothing proves nothing

WHY A REGISTER AND NOT AN LLM READ OF THE PAGE. A claim is bound to a PREDICATE OVER THE CODE,
written down, in `docs/design/canon_claims.yaml`. The binding is the artefact: it survives a
context window, it can be mutation-tested, and it is diffable when someone edits the page. An
organ that re-reads the page each time and forms its own opinion cannot be proven to fire on a
named defect, which is exactly what R15 forbids as evidence.

THE THREE R15 KILLERS, AND WHAT IS DONE ABOUT EACH:

  * TAUTOLOGY -- a claim's verdict must not be derived from the same source as the claim. The
    anchor is read from the PAGE; the predicate is evaluated against the CODE; nothing reads the
    page to decide what the code does. The one place the two touch is the anchor check, whose
    only job is to notice the page moved out from under the register.
  * FAIL-OPEN -- a missing register, an empty register, a probe path that does not exist, and a
    file that will not parse are all errors, never passes. `--strict-anchors` is on by default:
    an anchor that has vanished from the page is UNBOUND (drift), not "no claim to check".
  * FAIL-SILENT -- an unavailable check is a failed check. Exit status 2 means the register
    itself could not be used; 1 means drift; 0 means every registered claim holds. There is no
    path through this file that returns 0 while a probe did not run.

COMMENTS AND DOCSTRINGS ARE NOT A CHANNEL. `green_stance` appears in prose in several modules
that never read it; a grep-based probe would have called that a channel and marked C1 wrong. Each
`.py` under a probe's roots is parsed and re-rendered from its AST with docstrings stripped, so
only LIVE SOURCE is searched. That is the same discriminator the 2026-08-28 finding applied by
hand, mechanised.

DELIBERATELY NOT WIRED INTO THE COMMIT GATE. This check is expected to be RED whenever a
published surface has drifted, and a red pre-commit gate wedges every commit in the tree
(precedent: the CLAUDE.md ceiling, four days red, publishing wedged). It is an ORIENTATION
instrument. Its report lands at `docs/observability/canon_drift.json` for the daily self-note to
pick up, and a red register mints its own staging item (`mint_drift_item`), once per drift set.

    python3 -m tools.canon_drift_check              # human-readable, exit 1 on drift
    python3 -m tools.canon_drift_check --json       # machine-readable report on stdout
    python3 -m tools.canon_drift_check --write-report
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    # Run as `python3 tools/canon_drift_check.py` the repository root is not on the path, and an
    # import-path defect is invisible to every test that imports the module. Same shape, and the
    # same two lines, as `tools/level_promotion_gate.py`.
    sys.path.insert(0, str(REPO_ROOT))

# The SHARED low-water mechanism, called rather than copied. `removed_claims()` was the second of
# three hand-rolled implementations of it to land on 2026-09-05; each carried its own copy of the
# or-empty-string null treatment and the None-is-never-empty refusal, which is the shape that lets
# a defect be repaired in one and stay live in another for a month.
from background import register_low_water  # noqa: E402
from tools.python_code_text import code_text  # noqa: E402

DEFAULT_REGISTER = "docs/design/canon_claims.yaml"
DEFAULT_REPORT = "docs/observability/canon_drift.json"

HOLDS = "HOLDS"
OVER_CLAIM = "OVER_CLAIM"
SUPERSEDED = "SUPERSEDED"
UNBOUND = "UNBOUND"
ERROR = "ERROR"

#: Every verdict that is not HOLDS is drift. Spelled as a frozenset rather than `!= HOLDS` so a
#: new verdict cannot be added later and quietly default to "fine".
DRIFT_VERDICTS = frozenset({OVER_CLAIM, SUPERSEDED, UNBOUND, ERROR})

SKIP_DIRS = frozenset({"__pycache__", ".claude", ".git", "node_modules", ".venv"})


class ProbeError(RuntimeError):
    """A probe could not be evaluated. Always a verdict of ERROR -- never a pass."""


# --------------------------------------------------------------------------------------
# Live source: what the machine actually executes, with prose removed.
# --------------------------------------------------------------------------------------

def live_source(path: Path) -> str:
    """The module's source with comments and docstrings removed.

    A trait named only in a docstring is documentation, not a channel -- the distinction the
    2026-08-28 C1 verdict turned on. `ast.unparse` drops comments for free; docstrings are
    stripped explicitly because they survive a round-trip.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:  # a file we cannot read is a check we cannot make
        raise ProbeError(f"{path}: will not parse ({exc})") from exc
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            node.body = body[1:] or ([] if isinstance(node, ast.Module) else [ast.Pass()])
    return ast.unparse(tree)


def _resolve(root: Path, rel: str) -> Path:
    target = root / rel
    if not target.exists():
        raise ProbeError(f"probe path does not exist: {rel}")
    return target


def _iter_py(root: Path, roots: list[str], exclude: list[str]) -> Iterator[Path]:
    excluded = {e.rstrip("/") for e in exclude}
    for rel in roots:
        target = _resolve(root, rel)
        candidates = [target] if target.is_file() else sorted(target.rglob("*.py"))
        for path in candidates:
            if path.suffix != ".py":
                continue
            rel_path = path.relative_to(root).as_posix()
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if rel_path in excluded or any(rel_path.startswith(e + "/") for e in excluded):
                continue
            yield path


# --------------------------------------------------------------------------------------
# Probes. Each returns the EVIDENCE it found; truthiness of that evidence is "present".
# --------------------------------------------------------------------------------------

def probe_token_live(root: Path, spec: dict[str, Any]) -> list[str]:
    """Is `token` referenced in live source anywhere under `roots` (minus `exclude`)?"""
    token = spec["token"]
    pattern = re.compile(rf"\b{re.escape(token)}\b")
    hits: list[str] = []
    for path in _iter_py(root, spec["roots"], spec.get("exclude", [])):
        if pattern.search(live_source(path)):
            hits.append(path.relative_to(root).as_posix())
    return hits


def probe_module_name(root: Path, spec: dict[str, Any]) -> list[str]:
    """Is there a MODULE under `roots` whose filename matches `pattern`?

    C2's shape exactly: eleven design documents named "competitor" and no `.py` file. A probe
    that searched all file types would have called the frames a mechanism.
    """
    pattern = re.compile(spec["pattern"])
    return [
        path.relative_to(root).as_posix()
        for path in _iter_py(root, spec["roots"], spec.get("exclude", []))
        if pattern.search(path.stem)
    ]


def _literal_value(node: ast.expr) -> Any:
    """The literal a module-level assignment holds, or raise ProbeError.

    `frozenset({...})`, `set(...)`, `tuple(...)` and `list(...)` over one literal are unwrapped,
    because that is how the code spells a membership guard. Anything else is refused rather than
    skipped: until 2026-11-14 a value `literal_eval` could not read was `continue`d past, so a
    probe on `UPLIFTABLE_COMMODITIES = frozenset({...})` found nothing and an absent-claim HELD.
    """
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        pass
    wrappers = {"frozenset": frozenset, "set": frozenset, "tuple": tuple, "list": list}
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in wrappers \
            and len(node.args) <= 1 and not node.keywords:
        try:
            inner = ast.literal_eval(node.args[0]) if node.args else ()
        except (ValueError, SyntaxError):
            inner = None
        if inner is not None:
            return wrappers[node.func.id](inner)
    raise ProbeError(f"line {node.lineno}: value is not a literal this probe can read "
                     f"({ast.unparse(node)[:60]})")


def probe_literal_assign(root: Path, spec: dict[str, Any]) -> list[str]:
    """Is `name` assigned the literal `value` (or, with `contains`, a collection holding it)?

    A name that is never assigned in `file` is an ERROR, not an empty result: an absent-claim
    on a constant that was renamed would otherwise hold forever (MISSION_the_pricing_arm, whose
    `UPLIFTABLE_COMMODITY` was renamed on 2026-09-07 and held vacuously until 2026-11-14).
    """
    path = _resolve(root, spec["file"])
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:
        raise ProbeError(f"{spec['file']}: will not parse ({exc})") from exc
    hits: list[str] = []
    assigned = False
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else \
            ([node.target] if isinstance(node, ast.AnnAssign) and node.value is not None else [])
        for target in targets:
            if isinstance(target, ast.Name) and target.id == spec["name"]:
                assigned = True
                try:
                    actual = _literal_value(node.value)
                except ProbeError as exc:
                    raise ProbeError(f"{spec['file']}:{spec['name']} {exc}") from exc
                if "contains" in spec:
                    matched = isinstance(actual, (frozenset, set, tuple, list)) and spec["contains"] in actual
                else:
                    matched = actual == spec["value"]
                if matched:
                    hits.append(f"{spec['file']}:{node.lineno} {spec['name']} = {actual!r}")
    if not assigned:
        raise ProbeError(f"{spec['file']}: {spec['name']} is not assigned at module level "
                         f"(renamed or removed -- the probe can no longer flip)")
    return hits


def probe_import_edge(root: Path, spec: dict[str, Any]) -> list[str]:
    """Does anything under `roots` import `target` (or a submodule of it)?"""
    target = spec["target"]
    hits: list[str] = []
    for path in _iter_py(root, spec["roots"], spec.get("exclude", [])):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as exc:
            raise ProbeError(f"{path}: will not parse ({exc})") from exc
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                # `from company.carbon import carbon_ledger` imports the module by its leaf name;
                # reading only `node.module` let an absent claim on it hold while the edge existed.
                names = [node.module] + [f"{node.module}.{alias.name}" for alias in node.names]
            for name in names:
                if name == target or name.startswith(target + "."):
                    hits.append(f"{path.relative_to(root).as_posix()}:{node.lineno} imports {name}")
    return hits


def probe_call_site(root: Path, spec: dict[str, Any]) -> list[str]:
    """Calls to `function` under `roots` whose `keyword` argument is NOT the bare name `value`.

    C3's shape: the world marks its margin-call book once, at the run's end (`mark_date=
    effective_end`), and nothing reads it back into cash. A call marked at any other date -- a
    monthly mark inside the loop -- is evidence the call has become something the world can
    press with.
    """
    hits: list[str] = []
    for path in _iter_py(root, spec["roots"], spec.get("exclude", [])):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as exc:
            raise ProbeError(f"{path}: will not parse ({exc})") from exc
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and _called_name(node) == spec["function"]):
                continue
            kw = next((k for k in node.keywords if k.arg == spec["keyword"]), None)
            if kw is None or not (isinstance(kw.value, ast.Name) and kw.value.id == spec["value"]):
                shown = ast.unparse(kw.value) if kw is not None else "(not passed)"
                hits.append(f"{path.relative_to(root).as_posix()}:{node.lineno} "
                            f"{spec['function']}({spec['keyword']}={shown})")
    return hits


def probe_called(root: Path, spec: dict[str, Any]) -> list[str]:
    """Every CALL to `function` under `roots`. The definition is not a call, so it is no hit.

    The tariff channel's shape: the churn decision reads the offered rate only through
    `_price_differential_vs_market`. A `token_live` probe on that name would still match its
    `def` after the call was cut, so it could not go red on the defect it was written for.
    """
    hits: list[str] = []
    for path in _iter_py(root, spec["roots"], spec.get("exclude", [])):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as exc:
            raise ProbeError(f"{path}: will not parse ({exc})") from exc
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _called_name(node) == spec["function"]:
                hits.append(f"{path.relative_to(root).as_posix()}:{node.lineno} calls {spec['function']}")
    return hits


def _called_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def probe_text_in_file(root: Path, spec: dict[str, Any]) -> list[str]:
    """Does `phrase` appear in `file`? (For claims whose subject is a rendered artefact.)"""
    path = _resolve(root, spec["file"])
    text = _normalise(path.read_text(encoding="utf-8", errors="replace"))
    phrase = _normalise(spec["phrase"])
    return [f"{spec['file']} contains {spec['phrase']!r}"] if phrase in text else []


PROBES: dict[str, Callable[[Path, dict[str, Any]], list[str]]] = {
    "token_live": probe_token_live,
    "module_name": probe_module_name,
    "literal_assign": probe_literal_assign,
    "import_edge": probe_import_edge,
    "text_in_file": probe_text_in_file,
    "call_site": probe_call_site,
    "called": probe_called,
}


# --------------------------------------------------------------------------------------
# Witnesses. An "absent" claim HOLDS by finding nothing, and finding nothing is also what a
# probe on a name nobody ever wrote does. Expert Hour, 2026-11-14: 5 of 20 live claims could
# not go red -- three searched for `collateral_call`, a token in no source file anywhere; one
# for a constant renamed two months earlier; one for an archived module. So an absent claim
# must show the thing it watches is REAL somewhere in live code, or it is an ERROR.
# --------------------------------------------------------------------------------------

#: Where a watched name may be shown to exist. Wider than any probe's roots on purpose: the
#: question is "does this name exist", not "does the world read it".
WITNESS_ROOTS = ("company", "saas", "simulation", "sim", "tools", "background")


def _witness(root: Path, spec: dict[str, Any]) -> str | None:
    """Evidence that an absent-probe's subject is real, or None when the probe is vacuous."""
    kind = spec["kind"]
    if kind == "token_live":
        pattern = re.compile(rf"\b{re.escape(spec['token'])}\b")
        roots = [r for r in WITNESS_ROOTS if (root / r).is_dir()]
        for path in _iter_py(root, roots, []):
            # A file that will not parse is no witness (`code_text` is None): a false witness
            # would make a vacuous claim hold, so the closed direction here is "not shown".
            code = code_text(path.read_text(encoding="utf-8", errors="replace"))
            if code is not None and pattern.search(code):
                return path.relative_to(root).as_posix()
        return None
    if kind == "import_edge":
        rel = spec["target"].replace(".", "/")
        for cand in (root / f"{rel}.py", root / rel):
            if cand.exists():
                return cand.relative_to(root).as_posix()
        return None
    if kind == "call_site":
        spec_all = {**spec, "keyword": "\0never", "value": ""}
        calls = probe_call_site(root, spec_all)  # every call reports, since no keyword matches
        return calls[0] if calls else None
    if kind == "called":
        # The function must be DEFINED somewhere live, or "nothing calls it" watches a name.
        roots = [r for r in WITNESS_ROOTS if (root / r).is_dir()]
        for path in _iter_py(root, roots, []):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue  # an unparseable file is no witness: the closed direction
            if any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == spec["function"]
                   for n in ast.walk(tree)):
                return path.relative_to(root).as_posix()
        return None
    if kind == "literal_assign":
        return spec["file"]  # the probe itself refuses a name that is not assigned
    if kind == "text_in_file":
        return spec["file"]  # a rendered artefact: the file is real (`_resolve`), the phrase is a rule
    return None  # module_name and any new kind: no witness defined, so an absent claim is refused



def _normalise(text: str) -> str:
    """Collapse whitespace so a markdown line-wrap cannot orphan an anchor."""
    return re.sub(r"\s+", " ", text)


# --------------------------------------------------------------------------------------
# The register and its verdicts.
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Claim:
    id: str
    page: str
    anchor: str
    claim: str
    expects: str          # "present" | "absent" -- what the CODE must show for the page to hold
    probe: dict[str, Any]
    note: str = ""
    #: Further page sentences asserting the SAME predicate. The page repeats itself (a TIMEFRAME
    #: line and its later correction both say the carbon ledger is called by nothing); each copy
    #: binds to the one probe and each must stay on the page, or the claim is UNBOUND.
    also_anchors: tuple[str, ...] = ()

    @property
    def anchors(self) -> tuple[str, ...]:
        return (self.anchor, *self.also_anchors)


@dataclass
class Verdict:
    claim: Claim
    verdict: str
    evidence: list[str] = field(default_factory=list)
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.claim.id,
            "page": self.claim.page,
            "claim": self.claim.claim,
            "expects": self.claim.expects,
            "verdict": self.verdict,
            "evidence": self.evidence[:12],
            "detail": self.detail,
        }


#: The `_retired` section of the claim register: {claim_id: why it left}. The ONLY way a claim may
#: leave without a refusal. Same shape, and the same argument, as `RETIRED_SECTION` in
#: `background/self_clearing_alarm_census.py` -- the escape hatch exists, it is authored, it is in
#: git, and it is visible in the diff.
RETIRED_SECTION = "_retired"


def load_retired(path: Path) -> dict[str, str]:
    """The `_retired` section: {claim_id: why it left the register}. Absent or malformed yields {},
    which makes every removal unexplained and the check RED, never green. Same direction of failure
    as `load_register`: toward work, never toward silence."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    rows = data.get(RETIRED_SECTION) if isinstance(data, dict) else None
    return rows if isinstance(rows, dict) else {}


def _claim_ids_in_register(text: str) -> list[str] | None:
    """The claim ids in a raw copy of the register, or None when that copy is unusable as a
    baseline. PARSED, never executed. A raise is caught one level up and becomes the same None --
    an unparseable baseline is an UNESTABLISHED baseline, never an empty one."""
    data = yaml.safe_load(text)
    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list):
        return None
    return [c["id"] for c in claims if isinstance(c, dict) and "id" in c]


def _register_name(register: Path) -> str:
    """How the refusal names this register. Repo-relative where git can name it, absolute
    otherwise -- an ad-hoc `--register` outside the tree still has to identify itself in a report
    that now carries lines from four registers."""
    try:
        return register.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(register)


def _claim_ids_at_head(register: Path) -> frozenset[str] | None:
    """The register's ids as HEAD has them -- the baseline `removed_claims()` measures against.

    A NAMED SEAM ONTO THE SHARED READER, not a second copy of it. `register_low_water.keys_at_head`
    holds the `git show HEAD:` read, the linked-worktree resolution, and the contract that matters
    most here: it returns None, never `frozenset()`, when the baseline cannot be established. Those
    are opposite claims -- an empty set says "HEAD's register held no claims, so nothing can have
    been removed" and would report clean on every tree where git is unavailable, which is the
    fail-silent shape this module's header refuses.

    This function carries no rule of its own. If you are about to add one, it belongs in the shared
    reader, or this is a second implementation again.
    """
    rel = register.resolve().relative_to(REPO_ROOT)
    return register_low_water.keys_at_head(rel.as_posix(), _claim_ids_in_register,
                                           project_dir=REPO_ROOT)


def removed_claims(register: Path | None = None, *,
                   current: set[str] | None = None,
                   retired: dict[str, str] | None = None,
                   baseline: set[str] | None = None) -> list[str]:
    """THE REGISTER'S LOW-WATER MARK: a claim that was in the register at HEAD and is not in it now.

    THE THIRD QUESTION, asked of this register because it was asked of the census's on 2026-09-05
    (`dc5fcbbc8`) and the answer generalises. Every control here iterates the register: `run()`
    evaluates `load_register(...)`, so the register IS the subject set. A claim in the register is
    checked; a claim that has left is the subject of nothing. The register is a high-water mark and
    nothing kept the mark from falling.

    THE SECOND-ORDER SHAPE, which is why this is not merely a missing rung. Every drift verdict --
    OVER_CLAIM, SUPERSEDED, UNBOUND, ERROR -- is a REFUSAL ON A ROW, and `main()` exits non-zero
    for it. Deleting the row clears the refusal. Measured on the live register before this existed:
    fifteen claims with one drifting exits 1; delete the drifting claim and the same tree exits 0
    with "14 registered claim(s) checked ... all HOLD". A red clearable by deleting the evidence is
    a fail-open with an extra step, and the note would have gone on reporting a clean canon.

    WHY `test_the_live_register_membership_is_pinned_literally` IS NOT THIS CONTROL. That test
    pins a LITERAL id set, so it is keyed to today's answer rather than to the property: it reds
    when a claim is legitimately ADDED, and its cure when a claim is deleted is to delete the id
    from the literal -- a two-line diff that travels in the same commit as the deletion and is
    asked for no reason at all. This rung demands an authored sentence instead, and measures
    against HEAD rather than against a constant that moves with the change.

    NO PAGE-GONE EXCEPTION, AND THAT IS THE DESIGN. The tempting rule is "allow the removal if the
    page is gone or the anchor no longer resolves anyway". That is exactly the fail-open above:
    `evaluate()` already returns UNBOUND for a vanished anchor and ERROR for a missing page, so
    granting those cases a free pass here would hand row-deletion the cure for the two verdicts
    most likely to be inconvenient. A page genuinely retired and a register gone stale are the same
    observation from the code alone; only an authored sentence separates them.

    WHERE IT BITES. The baseline is HEAD, so this is a commit-time ratchet against the WORKING
    copy: you cannot drop a claim in a commit without saying why. Once a bad commit has landed,
    HEAD contains the loss and this goes quiet -- said plainly rather than implied, because the
    gates run pre-commit on the working tree and that is the whole enforcement point.

    Takes its baseline and its current set as arguments so the control can be driven without a git
    tree, and defaults to reading HEAD so the live rung has no fixture to drift from.

    ROUTED THROUGH `register_low_water.removed_rows`, NOT A COPY OF IT. This was the second of
    three hand-rolled implementations of one mechanism to land on 2026-09-05, each with its own
    copy of the `or ""` null treatment and the never-empty refusal. The rule lives in one place
    now; what stays here is what is genuinely the CANON's -- which register, the NOT-APPLICABLE
    branch for a register with no committed copy, what a row records, and how to retire one.
    """
    reg = register if register is not None else REPO_ROOT / DEFAULT_REGISTER
    if baseline is None:
        # NOT APPLICABLE is not the same claim as CANNOT ESTABLISH, and collapsing the two would
        # cost this rung either its teeth or its usability. A register outside the repository --
        # every `tmp_path` fixture, and any register handed to `--register` ad hoc -- has no
        # committed copy and never could have one, so there is no high-water mark to fall from and
        # nothing to refuse. A register INSIDE the repository that git cannot answer for is the
        # fail-silent case, and it refuses below.
        try:
            reg.resolve().relative_to(REPO_ROOT)
        except ValueError:
            return []
    base = _claim_ids_at_head(reg) if baseline is None else frozenset(baseline)
    if base is None:
        # The baseline refusal below does not read `current`, and complaining about a second fact
        # when the first already makes the question unanswerable is noise. Ordering preserved from
        # before the convergence: the unestablishable baseline is the refusal that gets reported.
        current = set()
    elif current is None:
        try:
            current = {c.id for c in load_register(reg)}
        except ProbeError as exc:
            return [f"the register's current claims could not be read ({exc}), so whether a claim "
                    f"has been removed cannot be answered -- this is a refusal, not a clean result"]
    ret = load_retired(reg) if retired is None else retired
    return register_low_water.removed_rows(
        register=_register_name(reg),
        current=current,
        baseline=base,
        retired=ret,
        row_is="The row is the only thing that binds a page sentence to a predicate over the "
               "code, and every verdict this register produces -- OVER_CLAIM, SUPERSEDED, "
               "UNBOUND, ERROR -- is a refusal ON A ROW, so deleting the row cures its own red.",
        retire_with="`{}[\"{{key}}\"]`".format(RETIRED_SECTION),
    )


def load_register(path: Path) -> list[Claim]:
    """Load the claim register. Missing, empty or malformed is an ERROR, never an empty pass."""
    if not path.exists():
        raise ProbeError(f"claim register missing: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("claims"), list) or not raw["claims"]:
        raise ProbeError(f"claim register is empty or malformed: {path}")
    claims: list[Claim] = []
    for entry in raw["claims"]:
        missing = [k for k in ("id", "page", "anchor", "claim", "expects", "probe") if k not in entry]
        if missing:
            raise ProbeError(f"claim {entry.get('id', '?')} missing keys: {missing}")
        if entry["expects"] not in ("present", "absent"):
            raise ProbeError(f"claim {entry['id']}: expects must be present|absent")
        if entry["probe"].get("kind") not in PROBES:
            raise ProbeError(f"claim {entry['id']}: unknown probe kind {entry['probe'].get('kind')!r}")
        also = entry.get("also_anchors", [])
        if not isinstance(also, list) or not all(isinstance(a, str) and a.strip() for a in also):
            raise ProbeError(f"claim {entry['id']}: also_anchors must be a list of sentences")
        claims.append(Claim(
            id=entry["id"], page=entry["page"], anchor=entry["anchor"], claim=entry["claim"],
            expects=entry["expects"], probe=entry["probe"], note=entry.get("note", ""),
            also_anchors=tuple(also),
        ))
    ids = [c.id for c in claims]
    if len(set(ids)) != len(ids):
        raise ProbeError("duplicate claim ids in register")
    return claims


def evaluate(claim: Claim, root: Path) -> Verdict:
    page = root / claim.page
    if not page.exists():
        return Verdict(claim, ERROR, detail=f"page missing: {claim.page}")
    page_text = _normalise(page.read_text(encoding="utf-8", errors="replace"))
    for anchor in claim.anchors:
        if _normalise(anchor) not in page_text:
            return Verdict(claim, UNBOUND,
                           detail=f"anchor no longer on {claim.page}: {anchor!r}")
    kind = claim.probe["kind"]
    try:
        evidence = PROBES[kind](root, claim.probe)
    except ProbeError as exc:
        return Verdict(claim, ERROR, detail=str(exc))
    except (OSError, KeyError) as exc:  # a broken register entry is a failed check, not a pass
        return Verdict(claim, ERROR, detail=f"{kind}: {exc!r}")
    found = bool(evidence)
    if claim.expects == "present":
        verdict = HOLDS if found else OVER_CLAIM
        detail = "" if found else "the page claims this and the code does not show it"
    else:
        if not found:
            try:
                witness = _witness(root, claim.probe)
            except ProbeError as exc:
                return Verdict(claim, ERROR, detail=f"witness: {exc}")
            if witness is None:
                return Verdict(claim, ERROR, detail=(
                    f"VACUOUS: the {kind} probe finds nothing, and what it watches exists nowhere in "
                    f"live code ({', '.join(WITNESS_ROOTS)}), so it could never go red"))
        verdict = HOLDS if not found else SUPERSEDED
        detail = "" if not found else "the code has moved past the page -- the page under-claims"
    return Verdict(claim, verdict, evidence=evidence, detail=detail)


def unwatched_sections(root: Path, claims: list[Claim]) -> dict[str, list[str]]:
    """Per markdown page in the register: the `##`/`###` sections that carry no bound claim.

    The denominator "N claims checked, 0 drifting" was printed without. On 2026-11-11 the model
    page had 10 sections and 6 of them -- including the 217-line picture -- held no anchor at all,
    so "all HOLD" was true of 17 sentences and silent on the rest. This names what nothing checks;
    it is coverage, not drift, so it never moves the exit status. A section of director quotes
    makes no code claim and is listed anyway: the reader, not this function, decides that.
    """
    out: dict[str, list[str]] = {}
    for page_rel in sorted({c.page for c in claims if c.page.endswith(".md")}):
        page = root / page_rel
        if not page.exists():
            continue
        anchors = [_normalise(a) for c in claims if c.page == page_rel for a in c.anchors]
        sections = re.split(r"(?m)^(?=#{2,3} )", page.read_text(encoding="utf-8", errors="replace"))
        out[page_rel] = [
            section.splitlines()[0].lstrip("#").strip()
            for section in sections
            if section.startswith("#") and section.lstrip("#").startswith(" ")
            and not any(a in _normalise(section) for a in anchors)
        ]
    return out


#: A45's blind pass of 15 Nov, MAJOR 1: "positive claims are counted per section, so one anchor
#: makes a section watched"; it estimated 20-25% of the page's statements about the code were
#: bound, and said the fix was a per-sentence denominator, not more anchors. This is that
#: denominator. What it counts, said before it is counted:
#:   a SENTENCE is a run of text ending at . ! or ? (and any closing quote, bracket or emphasis)
#:   followed by whitespace (so `app.py` and 0.45 do not end one), and never crossing a markdown block edge (blank line, heading, bullet,
#:   numbered item, table row, quote). Fenced blocks are left out and their lines counted apart.
#:   A sentence NAMES THE CODE OR A FIGURE when it holds a code path, a `.py` file, a snake_case
#:   identifier, an UPPER_SNAKE constant (not a staging-item name), a decimal, a percentage or a
#:   multiplier. That is a lower bound on "statements about the code": "the rival never prices
#:   below its own cost stack" names nothing and is not counted.
#:   It is BOUND when an anchor (or also_anchor) or a judgement excerpt overlaps it.
#: Coverage, like `unwatched_sections`: it never moves the exit status.
_BLOCK_EDGE = re.compile(r"\n(?=[ \t]*(?:\n|#|[-*+] |\d+\. |\||>))")
_FENCE = re.compile(r"(?ms)^[ \t]*```.*?^[ \t]*```[^\n]*$")
_UNIT = re.compile(r"[^\s\x00][^\x00]*?(?:[.!?]+[\"')*_\]]*(?=\s|\x00|$)|(?=\x00)|$)")
NAMES_CODE = re.compile(
    r"\b(?:company|saas|sim|simulation|tools|background|tests)/[\w./-]+|\b\w+\.py\b"
    r"|\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b"
    r"|\b(?!(?:WORKER|SEAT|DIRECTOR|ADVISOR|PLANNER)_)[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b"
    r"|\b\d+\.\d+\b|\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?x\b")


def sentence_coverage(root: Path, claims: list[Claim],
                      judgements: list[Judgement] = ()) -> dict[str, dict[str, Any]]:
    """Per markdown page: {sentences, naming, bound, fenced_lines, unbound: [...]}, as defined above."""
    out: dict[str, dict[str, Any]] = {}
    for page_rel in sorted({c.page for c in claims if c.page.endswith(".md")}):
        page = root / page_rel
        if not page.exists():
            continue
        raw = page.read_text(encoding="utf-8", errors="replace")
        fenced = sum(m.group().count("\n") + 1 for m in _FENCE.finditer(raw))
        raw = _FENCE.sub("\n", raw)
        marked = re.sub(r"\s+", " ", re.sub(r"\s*\x00[\s\x00]*", "\x00", _BLOCK_EDGE.sub("\x00", raw)))
        flat = marked.replace("\x00", " ")
        spans: list[tuple[int, int]] = []
        for excerpt in ([a for c in claims if c.page == page_rel for a in c.anchors]
                        + [j.excerpt for j in judgements if j.page == page_rel]):
            needle = _normalise(excerpt).strip()
            at = flat.find(needle) if needle else -1
            while at >= 0:
                spans.append((at, at + len(needle)))
                at = flat.find(needle, at + 1)
        total = naming = bound = 0
        unbound: list[str] = []
        for unit in _UNIT.finditer(marked):
            sentence = unit.group().strip()
            if not sentence:
                continue
            total += 1
            if not NAMES_CODE.search(sentence):
                continue
            naming += 1
            if any(lo < unit.end() and unit.start() < hi for lo, hi in spans):
                bound += 1
            else:
                unbound.append(sentence[:240])
        out[page_rel] = {"sentences": total, "naming": naming, "bound": bound,
                         "fenced_lines": fenced, "unbound": unbound}
    return out


#: The forms the model page uses to say the CODE lacks something. An under-claim can only be one
#: of these sentences, and an `absent` claim is the only thing that can show one false.
#: A45's Expert Hour (14 Nov, MAJOR 3): "an under-claim is seen only where an absent-claim was
#: pre-registered". The spine said "none of them presses yet ... competition (blocked entirely by
#: C2)" while its own organs line said a rival moves. The sentence counted as watched because its
#: collateral clause carried an anchor. So the unit here is the PHRASE, not the sentence or the
#: section: a phrase outside every anchor is named, even inside a sentence that is otherwise bound.
#: The lexicon is a judgement. A broader one (never|cannot|does not ...) named 50 sentences on
#: 14 Nov, mostly rules and mission prose that make no claim about code. This one names 18.
#: The last three lines are A45's blind pass of 15 Nov, MAJOR 2: negatives with no "not yet" in
#: them ("Nothing optimises", "has no household-side term", "Nothing it computes is ever offered",
#: "carries no competitive consequence"). Bare "never" and "nothing" stay out: on the model page
#: they are rule prose ("ground truth never crosses"), 22 sentences asserting no missing mechanism.
UNDER_CLAIM_FORMS = re.compile(
    r"\b(not yet|none of them|no module|by nothing|read by no|blocked|absent|still cannot|"
    r"cannot yet|no mechanism|unmeasured|unbuilt|nobody yet|"
    r"nothing (?:yet )?(?:supplies|reads|calls|offers|targets)|"
    r"nothing (?:it \w+ (?:is )?(?:ever )?)?(?:optimi[sz]es|computes|prices|offered|uses|feeds)|"
    r"has no|"
    r"no [\w-]+(?:[ -][\w-]+)? (?:consequence|module|reader|caller|mechanism|feedback)s?)\b",
    re.IGNORECASE)
_SENTENCE = re.compile(r"[^.!?]+(?:[.!?]+|$)")


#: Naming a negative is not judging it (A45's Expert Hour, MAJOR 3 residual, 14 Nov). A named
#: sentence is settled one of two ways: an `absent` claim binds it, or a row here says why no
#: predicate can be written for it. A judgement is keyed to its verbatim excerpt, so an edited
#: sentence is named again. Kinds:
#:   no_witness      it asserts a mechanism does not exist, and nothing exists for a probe to watch
#:                   (an absent probe on it would be VACUOUS);
#:   not_about_code  the phrase makes no claim about the code (a heading, a link label, a quote
#:                   being corrected, a decision awaited);
#:   summary         it restates claims that are bound (`of:`); it LAPSES -- is named again --
#:                   the moment any of them stops holding.
#:
#: A `no_witness` row has nothing in the CODE to watch, so it watches the WORK instead (A45's blind
#: Expert Hour, 15 Nov, MAJOR 4): `watch: {atom, level, target}` names the map atom that would build
#: the missing mechanism, at its level and target on the day of the judgement. When either moves,
#: the mechanism may have landed while the page still says it has not -- C2's shape, a rival built
#: and the page saying competition was blocked -- so the judgement LAPSES: the sentence is named
#: again and the lapse is red (exit 1, minted). A row with no atom to watch says why in
#: `watch_none`; a watch naming an atom no map holds is malformed, since it could never fire.
JUDGED_SECTION = "_judged_negatives"
JUDGED_KINDS = ("no_witness", "not_about_code", "summary")
MAP_REL = "docs/design/maturity_map.yaml"


@dataclass(frozen=True)
class Judgement:
    page: str
    excerpt: str
    kind: str
    why: str
    of: tuple[str, ...] = ()
    watch: tuple[str, int, int] | None = None   # (atom, level, target) when judged


def _parse_watch(row: dict[str, Any]) -> tuple[str, int, int] | None:
    watch, none = row.get("watch"), row.get("watch_none")
    if row["kind"] != "no_witness":
        if watch is not None or none is not None:
            raise ProbeError(f"{JUDGED_SECTION}: only a no_witness row watches an atom ({row['excerpt']!r:.60})")
        return None
    if watch is None:
        if isinstance(none, str) and none.strip():
            return None
        raise ProbeError(f"{JUDGED_SECTION}: a no_witness row names the atom that would build its mechanism "
                         f"(`watch`) or says why none can (`watch_none`) ({row['excerpt']!r:.60})")
    if (not isinstance(watch, dict) or not isinstance(watch.get("atom"), str)
            or not all(type(watch.get(k)) is int for k in ("level", "target"))):
        raise ProbeError(f"{JUDGED_SECTION}: `watch` needs atom, level and target ({row['excerpt']!r:.60})")
    return (watch["atom"], watch["level"], watch["target"])


def load_judgements(path: Path, claim_ids: set[str]) -> list[Judgement]:
    """The `_judged_negatives` rows. A malformed row is an ERROR, never a silently hidden sentence."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = raw.get(JUDGED_SECTION, []) if isinstance(raw, dict) else []
    if not isinstance(rows, list):
        raise ProbeError(f"{JUDGED_SECTION} must be a list")
    out: list[Judgement] = []
    for row in rows:
        if not isinstance(row, dict) or not all(
                isinstance(row.get(k), str) and row[k].strip() for k in ("page", "excerpt", "kind", "why")):
            raise ProbeError(f"{JUDGED_SECTION}: every row needs page, excerpt, kind and why ({row!r:.80})")
        if row["kind"] not in JUDGED_KINDS:
            raise ProbeError(f"{JUDGED_SECTION}: unknown kind {row['kind']!r} ({row['excerpt']!r:.60})")
        of = tuple(row.get("of") or ())
        if row["kind"] == "summary" and not of:
            raise ProbeError(f"{JUDGED_SECTION}: a summary names the claims it restates ({row['excerpt']!r:.60})")
        unknown = [c for c in of if c not in claim_ids]
        if unknown:
            raise ProbeError(f"{JUDGED_SECTION}: {row['excerpt']!r:.60} summarises unknown claim(s) {unknown}")
        out.append(Judgement(row["page"], row["excerpt"], row["kind"], row["why"].strip(), of,
                             _parse_watch(row)))
    return out


def lapsed_watches(root: Path, judgements: list[Judgement]) -> list[str]:
    """Each watched judgement whose atom has moved since it was judged. Raises ProbeError when a
    watched atom is in no map, or the map cannot be read: a watch that cannot fire is not a watch."""
    watched = [j for j in judgements if j.watch]
    if not watched:
        return []
    from tools import maturity_map_store
    try:
        atoms = {a.get("id"): a for a in maturity_map_store.load_atoms(root / MAP_REL)}
    except Exception as exc:  # noqa: BLE001 - re-raised as the check's own refusal
        raise ProbeError(f"{JUDGED_SECTION}: the map cannot be read to check a watch ({exc})") from exc
    lapsed: list[str] = []
    for j in watched:
        atom_id, level, target = j.watch
        atom = atoms.get(atom_id)
        if atom is None:
            raise ProbeError(f"{JUDGED_SECTION}: watches {atom_id!r}, which no map holds ({j.excerpt!r:.60})")
        now = (atom.get("level_current"), atom.get("level_target"))
        if now != (level, target):
            lapsed.append(f"{j.page}: {j.excerpt} -- {atom_id} was L{level}/T{target} when judged, "
                          f"now L{now[0]}/T{now[1]}; re-read the sentence against the code")
    return lapsed


def _stale_judgements(root: Path, judgements: list[Judgement]) -> list[str]:
    """Judgements whose excerpt left its markdown page (or whose page is not markdown): they hide
    nothing, and are printed so the row is cleared."""
    stale: list[str] = []
    for j in judgements:
        page = root / j.page
        text = (_normalise(page.read_text(encoding="utf-8", errors="replace"))
                if j.page.endswith(".md") and page.exists() else "")
        if text.find(_normalise(j.excerpt)) < 0:
            stale.append(f"{j.page}: {j.excerpt}")
    return stale


def unbound_negatives(root: Path, claims: list[Claim], judgements: list[Judgement] = (),
                      holding: set[str] | None = None,
                      lapsed: tuple[str, ...] | list[str] = ()) -> dict[str, list[str]]:
    """Per markdown page: each sentence holding a "the code lacks X" phrase no anchor covers.

    Those are the under-claims nothing can catch. Each needs an `absent` claim, or nothing checks
    it, or a written judgement (`JUDGED_SECTION`) saying why nothing can. A `summary` judgement
    covers only while every claim it restates is in `holding`. Coverage, like `unwatched_sections`,
    so it never moves the exit status.
    """
    out: dict[str, list[str]] = {}
    for page_rel in sorted({c.page for c in claims if c.page.endswith(".md")}):
        page = root / page_rel
        if not page.exists():
            continue
        text = _normalise(page.read_text(encoding="utf-8", errors="replace"))
        spans: list[tuple[int, int]] = []
        gone = {item.split(" -- ")[0] for item in lapsed}
        covering = [_normalise(j.excerpt) for j in judgements if j.page == page_rel
                    and f"{j.page}: {j.excerpt}" not in gone
                    and (j.kind != "summary" or (holding is not None and set(j.of) <= holding))]
        for excerpt in covering:
            at = text.find(excerpt)
            while at >= 0:
                spans.append((at, at + len(excerpt)))
                at = text.find(excerpt, at + 1)
        for claim in claims:
            if claim.page != page_rel:
                continue
            for anchor in map(_normalise, claim.anchors):
                at = text.find(anchor)
                while at >= 0:
                    spans.append((at, at + len(anchor)))
                    at = text.find(anchor, at + 1)
        named: list[str] = []
        for sentence in _SENTENCE.finditer(text):
            for phrase in UNDER_CLAIM_FORMS.finditer(sentence.group()):
                start = sentence.start() + phrase.start()
                end = sentence.start() + phrase.end()
                if not any(lo <= start and end <= hi for lo, hi in spans):
                    named.append(sentence.group().strip()[:240])
                    break
        out[page_rel] = named
    return out


def run(root: Path, register: Path) -> tuple[list[Verdict], dict[str, Any]]:
    claims = load_register(register)
    judgements = load_judgements(register, {c.id for c in claims})
    verdicts = [evaluate(claim, root) for claim in claims]
    holding = {v.claim.id for v in verdicts if v.verdict == HOLDS}
    lapsed = lapsed_watches(root, judgements)
    counts: dict[str, int] = {}
    for verdict in verdicts:
        counts[verdict.verdict] = counts.get(verdict.verdict, 0) + 1
    report = {
        "register": register.as_posix(),
        "claims_checked": len(verdicts),
        "counts": counts,
        "drift": [v.as_dict() for v in verdicts if v.verdict in DRIFT_VERDICTS],
        "verdicts": [v.as_dict() for v in verdicts],
        # The THIRD question, beside the two the verdicts answer. "Is this claim still true?" and
        # "is the register still bound to its page?" are both questions ABOUT A ROW, so neither can
        # see a row that left. Carried in the report rather than as a verdict because it is not a
        # claim's verdict -- there is no claim left to give one to.
        "removed": removed_claims(register, current={c.id for c in claims}),
        "unwatched_sections": unwatched_sections(root, claims),
        "unbound_negatives": unbound_negatives(root, claims, judgements, holding, lapsed),
        # The per-sentence denominator (A45 blind pass, 15 Nov, MAJOR 1): coverage, not drift.
        "sentence_coverage": sentence_coverage(root, claims, judgements),
        "judged_negatives": len(judgements),
        # Red: the atom that would build a "does not exist" mechanism moved after the judgement.
        "lapsed_watches": lapsed,
        # A judgement whose excerpt left its page hides nothing; it is printed so the row is cleared.
        "stale_judgements": _stale_judgements(root, judgements),
        # The served pages against the canon's words. In `run`, not `main`, because the daily note
        # calls `run`: until 16 Nov the site leg ran from the command line only, so the scheduled
        # trigger never asked it (A45 blind pass, 15 Nov, MINOR).
        "site": site_drift(root),
    }
    return verdicts, report


def _render(verdicts: list[Verdict], removed: list[str] | None = None,
            unwatched: dict[str, list[str]] | None = None,
            negatives: dict[str, list[str]] | None = None,
            judged: int = 0, stale: list[str] | None = None,
            lapsed: list[str] | None = None,
            coverage: dict[str, dict[str, Any]] | None = None) -> str:
    lines = ["CANON DRIFT CHECK -- what the page claims that the code no longer supports", ""]
    for verdict in verdicts:
        lines.append(f"  [{verdict.verdict:<10}] {verdict.claim.id}")
        lines.append(f"               {verdict.claim.claim}")
        lines.append(f"               page: {verdict.claim.page} · expects code {verdict.claim.expects}")
        if verdict.detail:
            lines.append(f"               {verdict.detail}")
        for item in verdict.evidence[:6]:
            lines.append(f"               evidence: {item}")
        lines.append("")
    drift = [v for v in verdicts if v.verdict in DRIFT_VERDICTS]
    lines.append(f"{len(verdicts)} claims checked · {len(drift)} drifting")
    for page, heads in (unwatched or {}).items():
        if heads:
            lines.append(f"UNWATCHED on {page} -- {len(heads)} section(s) no claim is bound to:")
            lines.extend(f"  - {head}" for head in heads)
    for page, sentences in (negatives or {}).items():
        if sentences:
            lines.append(f"UNBOUND NEGATIVES on {page} -- {len(sentences)} \"the code lacks X\" "
                         f"sentence(s) no absent claim checks, so an under-claim there is unseen:")
            lines.extend(f"  - {sentence}" for sentence in sentences)
    for page, cov in (coverage or {}).items():
        lines.append(f"SENTENCE COVERAGE on {page} -- {_coverage_phrase(cov)}; unbound:")
        lines.extend(f"  - {sentence}" for sentence in cov["unbound"])
    if judged:
        lines.append(f"JUDGED NEGATIVES -- {judged} named sentence(s) settled in `{JUDGED_SECTION}` as "
                     "unregisterable, each with its reason")
    for item in lapsed or []:
        lines.append(f"  [LAPSED WATCH] {item}")
    for item in stale or []:
        lines.append(f"  [STALE JUDGEMENT] excerpt no longer on its page, clear the row: {item}")
    if removed:
        lines.append("")
        lines.append("CLAIMS THAT LEFT THE REGISTER -- a row nothing checks any more:")
        lines.extend(f"  [REMOVED   ] {item}" for item in removed)
    return "\n".join(lines)


#: The work item a red register mints. A45's Expert Hour (14 Nov, MAJOR 2): "a red result changes
#: one line in the daily note and mints no work item" -- the docstring's "mint the drift as work"
#: was done by nothing, so drift reached the queue only if someone read the note.
DRIFT_ITEM_STEM = "WORKER_FINDING_THE_CANON_DRIFTS_FROM_THE_CODE_"
DRIFT_ITEM_LANE = "A_strategy_governance"
DRIFT_ITEM_ATOM = "A45_the_canon_is_a_standing_subject"


def _drift_key(report: dict[str, Any]) -> str:
    """The same drift is one item: keyed on which claims are red and how, not on the day."""
    import hashlib
    parts = sorted(f"{d['id']}:{d['verdict']}" for d in report["drift"])
    parts += sorted(f"removed:{item.split(' -- ')[0]}" for item in report["removed"])
    parts += sorted(f"lapsed:{item.split(' -- ')[0]}" for item in report.get("lapsed_watches", []))
    parts += sorted(f"site:{row['page']}:{row.get('phrase') or row.get('canon', '')[:60]}"
                    for row in _site_rows(report))
    return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()[:10].upper()


def mint_drift_item(report: dict[str, Any], staging_dir: Path, *, today: str) -> Path | None:
    """File the register's red as a staging finding, once per distinct drift. Returns the path, or None.

    None when the register is green, or when an item for the same drift already exists anywhere
    under `staging_dir` (root, in_progress/, done/): a daily note re-reading an unchanged red must
    not mint one item a day, and an item closed as done must not be re-minted for a drift a later
    run still sees -- that is the closer's call, recorded in the closed item.

    Severity follows the 12 Aug ruling's own definitions: an OVER_CLAIM is the page publishing a
    capability the code does not have, which is "a published figure may be wrong" -- BLOCKING.
    Every other red (SUPERSEDED, UNBOUND, ERROR, a removed row) leaves no false sentence in front of
    a reader -- LATENT. A served page carrying a superseded framing or a misquoted canon line IS a
    false sentence in front of a reader, so the site leg's rows are BLOCKING too.
    """
    lapsed = report.get("lapsed_watches", [])
    site_rows = _site_rows(report)
    if not report["drift"] and not report["removed"] and not lapsed and not site_rows:
        return None
    key = _drift_key(report)
    if any(staging_dir.rglob(f"{DRIFT_ITEM_STEM}{key}_*.md")):
        return None
    over = [d for d in report["drift"] if d["verdict"] == OVER_CLAIM]
    severity = "BLOCKING" if over or site_rows else "LATENT"
    rows = [f"| `{d['id']}` | {d['verdict']} | {d.get('page', '')} | {d.get('detail') or ''} |"
            for d in report["drift"]]
    rows += [f"| `{item.split(' -- ')[0]}` | REMOVED | | {item} |" for item in report["removed"]]
    rows += [f"| judged negative | LAPSED | {item.split(': ')[0]} | {item.split(': ', 1)[1]} |"
             for item in lapsed]
    rows += [f"| served page | {'SUPERSEDED' if 'phrase' in row else 'MISQUOTED'} | {row['page']} | "
             + (f"{row['phrase']!r} -- {row['why']}" if 'phrase' in row
                else f"canon {row['canon']!r}; page reads {row['page_reads']!r}") + " |"
             for row in site_rows]
    text = "\n".join([
        f"**Severity:** {severity} · **Lane:** {DRIFT_ITEM_LANE} · **Epoch:** 2 · "
        f"**Atom:** `{DRIFT_ITEM_ATOM}`",
        "",
        f"# The canon page and the code disagree on {len(rows)} registered claim(s) ({today})",
        "",
        "**Found by.** `tools/canon_drift_check.note_line`, run by the daily self-note. Minted "
        f"by the check itself, keyed `{key}` on the set of red claims, so the same drift is filed "
        "once.",
        "",
        "| Claim | Verdict | Page | Detail |",
        "|---|---|---|---|",
        *rows,
        "",
        "**What each verdict asks.** OVER_CLAIM: the page says more than the code does -- correct "
        "the page (a director document takes a `Director-doc: correction` trailer) or restore the "
        "code. SUPERSEDED: the code moved past the page -- the page under-claims. UNBOUND: the "
        "register's anchor sentence left the page -- rebind the row. ERROR: the probe could not "
        "run, so nothing is known. REMOVED: a row left the register without a `retired` reason. "
        "LAPSED: the atom that would build a mechanism the page says is missing has moved -- re-read "
        "the sentence, then bind it with an absent claim, correct it, or re-judge at the new level. "
        "A served-page SUPERSEDED or MISQUOTED row: the site presents a withdrawn framing as current, "
        "or a canon line in words the canon does not use -- correct the page, or mark told history "
        "with `data-canon-history`.",
        "",
        f"**Done means.** `python3 tools/canon_drift_check.py` reads none of the rows above as red. "
        f"Full report: `{DEFAULT_REPORT}`.",
        "",
    ])
    path = staging_dir / f"{DRIFT_ITEM_STEM}{key}_{today}.md"
    from background.live_ledger_guard import guard_live_ledger_write
    guard_live_ledger_write(path, writer="canon_drift_check minting its drift")
    staging_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _site_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    site = report.get("site") or {}
    return [*site.get("superseded", []), *site.get("misquoted", [])]


def _site_clause(report: dict[str, Any]) -> str:
    """The site leg's half of the note line: the denominator when it holds, the rows when not."""
    site = report.get("site")
    if not site:
        return ""
    rows = _site_rows(report)
    if not rows:
        return f" Site leg: {site['pages']} served page(s) hold against {site['quotes']} canon quote(s)."
    named = "; ".join(f"{r['page']}: {r['phrase']!r}" if "phrase" in r else f"{r['page']}: misquotes "
                      f"\"{' '.join(r['canon'].split()[:6])}...\"" for r in rows[:5])
    more = "" if len(rows) <= 5 else f" (+{len(rows) - 5} more)"
    return (f" SITE LEG RED: {len(rows)} line(s) on the {site['pages']} served page(s) contradict the "
            f"canon — {named}{more}.")


def _mint_for_the_note(root: Path, report: dict[str, Any]) -> str:
    """Mint the red as work and say so in the note. Never raises: a failed mint must not cost the
    note its drift line, so the failure is printed IN the line instead (fail-silent, R15).

    Under a test process the repo's own staging is never written -- a test reading the live tree
    would otherwise file a real work item. A fixture root under tmp is minted as normal.
    """
    from background.live_ledger_guard import in_test_process
    if in_test_process() and root.resolve() == REPO_ROOT.resolve():
        return ""
    try:
        from datetime import date
        path = mint_drift_item(report, root / "docs" / "staging", today=date.today().isoformat())
    except Exception as exc:  # noqa: BLE001 - reported in the line, never swallowed
        return f" Minting its work item FAILED ({type(exc).__name__}: {exc})."
    return f" Minted `{path.name}`." if path else ""


def note_line(root: Path | None = None, *, write_report: bool = True) -> str:
    """One line for the daily self-note — the TRIGGER half of this atom.

    A standing check nothing runs is an arm with no trigger, and this project has caught itself
    shipping that shape before. The morning note is what asks the question the director should not
    have had to ask. Raises `ProbeError` if the register is unusable, so the note's own fail-closed
    wrapper renders a RED rather than a reassuring silence.
    """
    root = root or REPO_ROOT
    verdicts, report = run(root, root / DEFAULT_REGISTER)
    if write_report:
        try:
            out = root / DEFAULT_REPORT
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        except Exception:  # noqa: BLE001 - see below; the LINE is the deliverable
            # WIDENED FROM `OSError` ON 2026-08-31, to match what this except was always FOR.
            # The comment states the intent exactly -- *"a read-only tree must not suppress it"* --
            # and a test-isolation refusal IS a read-only tree from here: `docs/observability`
            # became a protected surface, `ProductionWriteRefused` is a RuntimeError, and it went
            # straight past an `except OSError`.
            #
            # THE FAILURE THAT FOUND IT LOOKED LIKE SOMETHING ELSE ENTIRELY, which is the part
            # worth remembering. `note_line` raised, `daily_self_note`'s own fail-closed wrapper
            # rendered "canon drift check unavailable", and
            # `test_the_daily_self_note_actually_asks_the_question` failed on a missing substring.
            # A refusal swallowed by one caller's `except` re-surfaces as an unrelated assertion in
            # another, so the narrow `except` cost more than it saved.
            pass
    minted = _mint_for_the_note(root, report) if write_report else ""
    drift = report["drift"]
    checked = report["claims_checked"]
    removed = report["removed"]
    if removed:
        # Named FIRST and unconditionally: a claim that left the register cannot appear in `drift`,
        # because there is no row left to give a verdict to. Reporting "all HOLD" beside a silent
        # removal is exactly the sentence this rung exists to stop being printed.
        named = "; ".join(item.split(" -- ")[0] for item in removed[:5])
        more = "" if len(removed) <= 5 else f" (+{len(removed) - 5} more)"
        return (f"canon drift: {len(removed)} claim(s) LEFT the register since HEAD with no "
                f"`{RETIRED_SECTION}` reason — {named}{more}. A removed claim is not a claim that "
                f"holds; it is a page sentence nothing checks. The other {checked} were checked. "
                f"Full report: `{DEFAULT_REPORT}`.{minted}{_site_clause(report)}")
    lapsed = report.get("lapsed_watches", [])
    if lapsed:
        named = "; ".join(item.split(" -- ")[1].split(" was ")[0] for item in lapsed[:5])
        return (f"canon drift: {len(lapsed)} judged \"does not exist\" sentence(s) LAPSED — the atom "
                f"that would build each has moved ({named}), so the page may now under-claim. "
                f"{len(drift)} of {checked} registered claim(s) drift. Full report: "
                f"`{DEFAULT_REPORT}`.{minted}{_site_clause(report)}{_unwatched_clause(report)}")
    if not drift and _site_rows(report):
        return (f"canon drift: the served site contradicts the canon.{_site_clause(report)} The "
                f"{checked} registered claim(s) all HOLD against the code. Full report: "
                f"`{DEFAULT_REPORT}`.{minted}{_unwatched_clause(report)}")
    if not drift:
        return (f"canon drift: {checked} registered claim(s) checked against the code, all HOLD "
                f"(register `{DEFAULT_REGISTER}`).{_site_clause(report)}{_unwatched_clause(report)}")
    named = "; ".join(f"{d['id']} → {d['verdict']}" for d in drift[:5])
    more = "" if len(drift) <= 5 else f" (+{len(drift) - 5} more)"
    return (f"canon drift: {len(drift)} of {checked} registered claim(s) no longer match the code — "
            f"{named}{more}. Full report: `{DEFAULT_REPORT}`.{minted}{_site_clause(report)}"
            f"{_unwatched_clause(report)}")


def _unwatched_clause(report: dict[str, Any]) -> str:
    """The denominator beside the verdict: which page sections no claim watches."""
    parts = [f"{Path(page).name}: {len(heads)} section(s) carry no bound claim ({'; '.join(heads)})"
             for page, heads in report.get("unwatched_sections", {}).items() if heads]
    parts += [f"{Path(page).name}: {len(sentences)} \"not yet\"-type sentence(s) no absent claim "
              f"checks" for page, sentences in report.get("unbound_negatives", {}).items() if sentences]
    parts += [f"{Path(page).name}: {_coverage_phrase(cov)}"
              for page, cov in report.get("sentence_coverage", {}).items() if cov["naming"] > cov["bound"]]
    return f" Unwatched — {' · '.join(parts)}." if parts else ""


def _coverage_phrase(cov: dict[str, Any]) -> str:
    """The per-sentence denominator in words (A45 blind pass, 15 Nov, MAJOR 1)."""
    return (f"{cov['bound']} of {cov['naming']} sentence(s) naming code or a figure are bound "
            f"({cov['sentences']} sentences on the page; {cov['fenced_lines']} fenced line(s) not read)")


# --------------------------------------------------------------------------------------
# THE SITE LEG: canon against the served pages, not only against the standing documents.
#
# Director's front-door steer, 2026-10-22, Checks: "no superseded line presented as current on
# any served page, and quoted canon lines verbatim". The register above binds a page's claim to
# the CODE; this leg binds a served page's words to the CANON, so it needs no register rows.
#
# It reads what a reader sees: visible HTML text, with `<script>`, `<style>` and comments
# skipped. The first sweep (item 1) hit "cheapest tonne" only inside an HTML comment explaining
# its withdrawal, which is not presented to anyone. Text a page's JavaScript writes at load is
# NOT read here -- that is the door tests' subject, and this leg says so rather than claiming it.
# --------------------------------------------------------------------------------------

CANON_DOC = "docs/design/DIRECTOR_CANON.md"     # also spelled out in `site_drift`, for the census
SITE_ROOT = "site"

#: Framings canon §16 marks superseded (and the withdrawn headline item 1 replaced). A served page
#: may still TELL their history: wrap that text in an element carrying `data-canon-history`, which
#: makes the choice visible in the page source rather than a silent allowance here.
SUPERSEDED_ON_SITE: tuple[tuple[str, str], ...] = (
    ("cheapest tonne", "the July carbon-abatement headline; CO1 and canon v4 decision 4"),
    ("carbon abatement through personalisation", "the 19 July mission; §16 Mission"),
    ("grown toward go-live", "the first mission; §16 Mission"),
    ("non-commercial", "the 21 July mission; §16 Mission"),
    ("public domain", "the 21 July mission; §16 Mission"),
    ("80 founders", "the book before 6 Oct; §16 Book size"),
    ("director twin", "the twin as approver; §16, void since 29 July"),
    ("cut carbon through personalisation", "the 19 July mission on the front-door diagram; §16 Mission"),
    ("carbon becomes the headline", "decision 4: £/tCO₂e is an internal diagnostic (CO1, CO3)"),
    ("tco₂e on the front page", "decision 4: £/tCO₂e is an internal diagnostic (CO1, CO3)"),
    ("ev is fitness", "decision 14: the fitness function is open until Phase 3 (§2)"),
)

#: A canon quote is policed on a page only once the page has started to quote it: these many
#: opening words, verbatim, commit the page to the whole line. Fewer would match ordinary prose
#: ("The enterprise value is"); the M1 opening is seven words before it can be anything else.
QUOTE_OPENING_WORDS = 7
QUOTE_MIN_WORDS = 10


class _VisibleText(HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._stack: list[tuple[str, bool]] = []    # (tag, hides its text)

    def handle_starttag(self, tag, attrs):
        if tag in {"br", "img", "meta", "link", "input", "hr", "wbr", "source", "area", "col"}:
            self.parts.append(" ")
            return
        hides = tag in self.SKIP or any(k == "data-canon-history" for k, _ in attrs)
        self._stack.append((tag, hides))
        self.parts.append(" ")

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                break
        self.parts.append(" ")

    def handle_data(self, data):
        if not any(hides for _, hides in self._stack):
            self.parts.append(data)


def _plain(text: str) -> str:
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    return re.sub(r"\s+", " ", text).strip()


def visible_text(html: str) -> str:
    parser = _VisibleText()
    parser.feed(html)
    parser.close()
    return _plain(" ".join(parser.parts))


def canon_quotes(canon_text: str) -> list[str]:
    """Every double-quoted canon line of at least QUOTE_MIN_WORDS words, whitespace-normalised.

    An opening quote is one at the start of a line or after a space or bracket, followed by a
    letter, so the gap between two quotes ('", "') is never read as a quote itself.
    """
    flat = _plain(canon_text)
    found = re.findall(r'(?:(?<=^)|(?<=[\s(]))"([A-Za-z][^"]*?)"', flat)
    return sorted({q.strip() for q in found if len(q.split()) >= QUOTE_MIN_WORDS})


def served_pages(root: Path) -> list[Path]:
    """Every served `site/**/*.html` and `*.svg`. The SVGs are here for the front-door diagram
    (director's steer, 24 Oct): its words are text nodes, read by the same parser, so a withdrawn
    line or a misquoted M1 on the picture reds this leg exactly as it would on a page."""
    site = root / SITE_ROOT
    return sorted(p for ext in ("*.html", "*.svg") for p in site.rglob(ext)
                  if not (set(p.relative_to(site).parts) & SKIP_DIRS))


def site_drift(root: Path) -> dict[str, Any]:
    """{superseded: [...], misquoted: [...], pages, quotes} over every served `site/**/*.html`.

    Raises ProbeError when the canon cannot be read or yields no quotes (fail closed: a leg that
    found nothing to check must not read as a page that drifted nowhere). A root with no `site/`
    is a fixture tree, not this repository, and is reported as `pages: 0`.
    """
    if not (root / SITE_ROOT).is_dir():
        return {"pages": 0, "quotes": 0, "superseded": [], "misquoted": []}
    canon = root / "docs/design/DIRECTOR_CANON.md"      # markdown, never Python source
    try:
        quotes = canon_quotes(canon.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProbeError(f"the site leg cannot read {CANON_DOC}: {exc}") from exc
    if not quotes:
        raise ProbeError(f"the site leg found no quoted canon line in {CANON_DOC}")
    superseded, misquoted = [], []
    pages = served_pages(root)
    for page in pages:
        if page.suffix not in {".html", ".svg"}:
            continue
        rel = page.relative_to(root).as_posix()
        text = visible_text(page.read_text(encoding="utf-8", errors="replace"))
        lower = text.lower()
        for phrase, why in SUPERSEDED_ON_SITE:
            if phrase in lower:
                superseded.append({"page": rel, "phrase": phrase, "why": why})
        for quote in quotes:
            opening = " ".join(quote.split()[:QUOTE_OPENING_WORDS])
            if opening in text and quote not in text:
                at = text.index(opening)
                misquoted.append({"page": rel, "canon": quote,
                                  "page_reads": text[at:at + len(quote) + 20]})
    return {"pages": len(pages), "quotes": len(quotes),
            "superseded": superseded, "misquoted": misquoted}


def _render_site(site: dict[str, Any]) -> str:
    lines = ["", f"SITE LEG -- {site['pages']} served page(s) against {site['quotes']} canon "
                 "quote(s) and the superseded framings (visible text of HTML and SVG only)"]
    for row in site["superseded"]:
        lines.append(f"  [SUPERSEDED] {row['page']}: {row['phrase']!r} -- {row['why']}")
    for row in site["misquoted"]:
        lines.append(f"  [MISQUOTED ] {row['page']}: canon {row['canon']!r}")
        lines.append(f"               page reads {row['page_reads']!r}")
    if not (site["superseded"] or site["misquoted"]):
        lines.append("  every served page holds")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(REPO_ROOT), help="repo root to check")
    parser.add_argument("--register", default=None, help="claim register (default docs/design/canon_claims.yaml)")
    parser.add_argument("--json", action="store_true", help="emit the JSON report on stdout")
    parser.add_argument("--write-report", action="store_true",
                        help=f"also write the report to {DEFAULT_REPORT}")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    register = Path(args.register) if args.register else root / DEFAULT_REGISTER
    try:
        verdicts, report = run(root, register)
    except ProbeError as exc:
        print(f"CANON DRIFT CHECK UNAVAILABLE: {exc}", file=sys.stderr)
        return 2  # an unavailable check is a FAILED check (R15 fail-silent)

    print(json.dumps(report, indent=2) if args.json
          else _render(verdicts, report["removed"], report.get("unwatched_sections"),
                       report.get("unbound_negatives"), report.get("judged_negatives", 0),
                       report.get("stale_judgements"), report.get("lapsed_watches"),
                       report.get("sentence_coverage"))
          + _render_site(report["site"]))
    if args.write_report:
        out = root / DEFAULT_REPORT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    # A claim that LEFT is a failure of the same rank as a claim that drifted -- the whole point of
    # the rung is that deleting the row must not be cheaper than fixing the page.
    site_drifted = report["site"]["superseded"] or report["site"]["misquoted"]
    return 1 if (any(v.verdict in DRIFT_VERDICTS for v in verdicts) or report["removed"]
                 or report.get("lapsed_watches") or site_drifted) else 0


if __name__ == "__main__":
    raise SystemExit(main())
