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
    }
    return verdicts, report


def _render(verdicts: list[Verdict]) -> str:
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

    print(json.dumps(report, indent=2) if args.json else _render(verdicts))
    if args.write_report:
        out = root / DEFAULT_REPORT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 1 if any(v.verdict in DRIFT_VERDICTS for v in verdicts) else 0


if __name__ == "__main__":
    raise SystemExit(main())
