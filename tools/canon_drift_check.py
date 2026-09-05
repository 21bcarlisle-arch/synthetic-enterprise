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
    ERROR       the probe could not run at all -- FAIL CLOSED, never a pass

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
instrument: run it, read it, mint the drift as work. Its report lands at
`docs/observability/canon_drift.json` for the daily self-note to pick up.

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
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
# `register_low_water` is the SHARED low-water mechanism, CALLED rather than copied. This module
# hand-rolled its own on 2026-09-05 (`605ec3995`) at the same hour the census hand-rolled a second
# (`dc5fcbbc8`) and the generic was extracted from both (`6f4e6b1f4`) -- three copies of the
# or-empty-string null treatment, the None-never-empty refusal and the no-subject-gone-exception
# argument. That is the VAT shape: one rule, several implementations, a defect fixed in one and
# live in another. Neither lane was wrong; a bounded invocation cannot see the whole, which is why
# converging them is the seat's.
from background import register_low_water  # noqa: E402

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


def probe_literal_assign(root: Path, spec: dict[str, Any]) -> list[str]:
    """Is `name` assigned the literal `value` at module level in `file`?"""
    path = _resolve(root, spec["file"])
    wanted = spec["value"]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:
        raise ProbeError(f"{spec['file']}: will not parse ({exc})") from exc
    hits: list[str] = []
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else \
            ([node.target] if isinstance(node, ast.AnnAssign) else [])
        for target in targets:
            if isinstance(target, ast.Name) and target.id == spec["name"]:
                try:
                    actual = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    continue
                if actual == wanted:
                    hits.append(f"{spec['file']}:{node.lineno} {spec['name']} = {actual!r}")
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
                names = [node.module]
            for name in names:
                if name == target or name.startswith(target + "."):
                    hits.append(f"{path.relative_to(root).as_posix()}:{node.lineno} imports {name}")
    return hits


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
}


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

#: How the shared low-water mechanism names THIS register in a refusal. Several registers report
#: through the same wording now, so a reader of a mixed report has to be told which one spoke.
REGISTER_NAME = "CANON CLAIM REGISTER"


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


def claim_ids_in_register_text(text: str) -> list[str] | None:
    """HEAD's raw register TEXT -> the claim ids in it, or None when that text is not a register.

    The `extract` half of `register_low_water.keys_at_head`. It PARSES and never execs, which
    matters less for YAML than for a register living in a module, but the contract is the shared
    one and this is the half that is specific to this register's shape.

    None, never [], for every unusable shape -- unparseable YAML, a document that is not a mapping,
    a `claims` key that is not a list. The shared reader turns each of those into an
    UNESTABLISHABLE baseline, and the caller turns that into a refusal that names itself. Returning
    [] would be the claim "HEAD's register held no claims, so nothing can have been removed".
    """
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list):
        return None
    return [c["id"] for c in claims if isinstance(c, dict) and "id" in c]


def _claim_ids_at_head(register: Path) -> frozenset[str] | None:
    """The register's ids as HEAD has them -- the baseline `removed_claims()` measures against.

    Routed through `register_low_water.keys_at_head`, so the `git show HEAD:` read, the timeout,
    the OSError leg and the None-never-empty contract are the ones that were mutation-proved once
    rather than a second copy of them. What stays here is the only part that is this register's:
    where the file is, and how to read claim ids out of its text.
    """
    rel = register.resolve().relative_to(REPO_ROOT)
    return register_low_water.keys_at_head(rel.as_posix(), claim_ids_in_register_text,
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
    base = _claim_ids_at_head(reg) if baseline is None else baseline
    if base is not None and current is None:
        # Only reached when there IS a baseline to measure against. With none, the refusal below
        # is about the baseline and reading the working copy would only be a second way to fail.
        try:
            current = {c.id for c in load_register(reg)}
        except ProbeError as exc:
            return [f"the register's current claims could not be read ({exc}), so whether a claim "
                    f"has been removed cannot be answered -- this is a refusal, not a clean result"]
    # The rule itself -- the null-reason treatment, the never-empty refusal, the no-subject-gone
    # exception -- belongs to the shared mechanism, so a repair to any one of them reaches this
    # register too. What is passed in is the part that is only true HERE: what a claim row records,
    # and the exact hatch to author.
    return register_low_water.removed_rows(
        register=REGISTER_NAME,
        current=() if current is None else current,
        baseline=None if base is None else frozenset(base),
        retired=load_retired(reg) if retired is None else retired,
        row_is="The row is the only thing that binds this page sentence to a predicate over the "
               "code; removing it removes the drift check that the page still tells the truth.",
        retire_with="`" + RETIRED_SECTION + "[\"{key}\"]` in the register",
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
        claims.append(Claim(
            id=entry["id"], page=entry["page"], anchor=entry["anchor"], claim=entry["claim"],
            expects=entry["expects"], probe=entry["probe"], note=entry.get("note", ""),
        ))
    ids = [c.id for c in claims]
    if len(set(ids)) != len(ids):
        raise ProbeError("duplicate claim ids in register")
    return claims


def evaluate(claim: Claim, root: Path) -> Verdict:
    page = root / claim.page
    if not page.exists():
        return Verdict(claim, ERROR, detail=f"page missing: {claim.page}")
    if _normalise(claim.anchor) not in _normalise(page.read_text(encoding="utf-8", errors="replace")):
        return Verdict(claim, UNBOUND,
                       detail=f"anchor no longer on {claim.page}: {claim.anchor!r}")
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
        verdict = HOLDS if not found else SUPERSEDED
        detail = "" if not found else "the code has moved past the page -- the page under-claims"
    return Verdict(claim, verdict, evidence=evidence, detail=detail)


def run(root: Path, register: Path) -> tuple[list[Verdict], dict[str, Any]]:
    claims = load_register(register)
    verdicts = [evaluate(claim, root) for claim in claims]
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
    }
    return verdicts, report


def _render(verdicts: list[Verdict], removed: list[str] | None = None) -> str:
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
    if removed:
        lines.append("")
        lines.append("CLAIMS THAT LEFT THE REGISTER -- a row nothing checks any more:")
        lines.extend(f"  [REMOVED   ] {item}" for item in removed)
    return "\n".join(lines)


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
                f"Full report: `{DEFAULT_REPORT}`.")
    if not drift:
        return (f"canon drift: {checked} registered claim(s) checked against the code, all HOLD "
                f"(register `{DEFAULT_REGISTER}`).")
    named = "; ".join(f"{d['id']} → {d['verdict']}" for d in drift[:5])
    more = "" if len(drift) <= 5 else f" (+{len(drift) - 5} more)"
    return (f"canon drift: {len(drift)} of {checked} registered claim(s) no longer match the code — "
            f"{named}{more}{'' if not more else ''}. Full report: `{DEFAULT_REPORT}`.")


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

    print(json.dumps(report, indent=2) if args.json else _render(verdicts, report["removed"]))
    if args.write_report:
        out = root / DEFAULT_REPORT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    # A claim that LEFT is a failure of the same rank as a claim that drifted -- the whole point of
    # the rung is that deleting the row must not be cheaper than fixing the page.
    return 1 if (any(v.verdict in DRIFT_VERDICTS for v in verdicts) or report["removed"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
