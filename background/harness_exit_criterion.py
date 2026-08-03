"""HX1 — the harness exit-criterion counter, mechanised.

WHAT THIS IS FOR (R12, binding): this counter gates exactly ONE decision — *may harness
investment resume*. It is NOT a quality score, NOT a fidelity measure, NOT a maturity
number, and it must never appear in any product-quality claim. It is a diagnostic that
answers a yes/no about where the next hour of build effort should go.

THE RATIFIED CRITERION (DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27):

    The harness is "done for now" when THREE consecutive product-content atoms each
    reach their next level with their declared exit criterion landed, across a span in
    which the STALL-class intervention count is ZERO — director DECISION-class touches
    unrestricted.

N is READ from that ruling (`ratified_n`), never hardcoded as truth here. It is the
director's dial; if he moves it, this module moves with it, and if the ruling cannot be
read the counter REFUSES rather than assuming a value.

THE INDEPENDENCE PROPERTY (R15 TAUTOLOGY guard, the reason this module exists at all).
The counter is a pure function of PRIMARY STATE:

    * `docs/observability/gate_authorizations.jsonl`  — which levels actually moved
    * `docs/design/maturity_map.yaml`                 — which atoms are product-lane
    * `docs/observability/fidelity_evidence_ledger.json` — did a fidelity row move
    * `tests/**`                                      — is there a spec-tied acceptance test
    * git history                                     — was the span stall-free

It NEVER reads the tick's own enumeration of what it did, and — the sharp edge — it never
reads a ledger entry's own `provenance` prose. The provenance is the mover's *self-report*
of its evidence; scoring an advance by reading it would be checking the claim against the
claim. Every evidence kind below is resolved from an artefact the mover did not write in
the same breath. `test_provenance_prose_cannot_manufacture_an_advance` pins this.

DIRECTION OF ERROR, chosen deliberately (G5, and stated so a reader can check it): every
unresolvable case makes the count SMALLER or the verdict LESS provable, never larger and
never more confident. A counter that under-counts delays a harness decision; a counter
that over-counts declares the harness done on a span that was not clean. Only the first
is recoverable, so every fail-closed branch here leans that way.

WHAT HX2 HANDED UP, AND WHY `satisfied` IS FALSE ON TODAY'S REAL STATE. HX2 left two
stall classes with NO detector (`harden_while_content_unminted`, `act_later_ruled_reversible`)
and its verdict doc states the consequence in load-bearing terms: *while either hole is
open, a zero stall count is not proof of a clean span.* This module obeys that literally.
`provable` is False whenever any class is uncovered, whenever a `point`-kind class cannot
be reconstructed over a past span, and whenever any detector reports `unavailable`. And
`satisfied` requires `provable`. So the honest reading of today's output is not "the
harness is not done" — it is "this span cannot yet be PROVEN clean", which is a different
and more useful statement.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

RATIFICATION_DOC_PATH = (
    PROJECT_DIR
    / "docs"
    / "staging"
    / "done"
    / "DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27.md"
)
LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "gate_authorizations.jsonl"
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
FIDELITY_PATH = PROJECT_DIR / "docs" / "observability" / "fidelity_evidence_ledger.json"
TESTS_ROOT = PROJECT_DIR / "tests"

# The lane and value_stream that mark an atom as HARNESS MACHINERY rather than product
# content. The ratified definition names both exclusions ("NOT H_harness, NOT a
# close_to_learn machinery atom") because they are not the same set: a few product-lane
# atoms carry value_stream close_to_learn, and those are machinery too.
HARNESS_LANE = "H_harness"
MACHINERY_VALUE_STREAM = "close_to_learn"

# The third ratified evidence kind — an R11-verified live-surface change — has no
# machine-resolvable trace in this repository: R11 verification is a FETCH of the
# deployed surface, and a commit touching site/** is exactly the code-not-pixel evidence
# R11 forbids treating as proof. Rather than accept the weaker artefact and quietly call
# it R11, this kind is UNIMPLEMENTED and named. Its cost is under-counting (an advance
# whose only evidence was a live-surface check reads as lacking), which is the safe
# direction.
UNIMPLEMENTED_EVIDENCE_KINDS = ("r11_live_surface_change",)

_N_PATTERN = re.compile(r"\bN\s*=\s*(\d+)\b")


class ExitCriterionError(RuntimeError):
    """A primary-state input could not be read or is malformed.

    R15 FAIL-OPEN guard: this is raised instead of returning a zero/empty result,
    because "no advances found" and "the ledger is missing" must never be the same
    answer. `evaluate` catches it and returns a verdict carrying the error with
    `satisfied=False` — an unavailable check is a FAILED check, never a clean span.
    """


# ── the ratified dial ───────────────────────────────────────────────────────────


def ratified_n(path: Path | None = None) -> int:
    """N, read from the director's ratification doc.

    Fail-closed on every ambiguity: a missing doc, no `N = <int>` statement, a
    non-positive value, or two statements that DISAGREE all raise. A disagreement in
    particular must not be resolved by picking one — if the ruling has been edited into
    two minds, the machine's job is to say so, not to choose the director's dial for him.
    """
    p = path or RATIFICATION_DOC_PATH
    try:
        text = p.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - missing/unreadable are the same defect
        raise ExitCriterionError(
            f"ratification doc {p} is unreadable ({type(exc).__name__}: {exc}); N is the "
            f"DIRECTOR's dial and must be read, never assumed"
        ) from exc
    values = {int(m.group(1)) for m in _N_PATTERN.finditer(text)}
    if not values:
        raise ExitCriterionError(
            f"ratification doc {p} states no 'N = <int>'; refusing to assume a value for the "
            f"director's dial"
        )
    if len(values) > 1:
        raise ExitCriterionError(
            f"ratification doc {p} states CONFLICTING values for N: {sorted(values)}. The "
            f"machine must not pick one on the director's behalf."
        )
    n = values.pop()
    if n <= 0:
        raise ExitCriterionError(f"ratification doc {p} states N={n}, which is not a count")
    return n


# ── primary-state readers (each distinguishes MISSING from EMPTY) ───────────────


def _read_ledger_strict(path: Path | None = None) -> list[dict]:
    """Ledger entries, raising on an absent or malformed file.

    Deliberately NOT `gate_authorization.read_ledger`, which returns [] for a missing
    file and skips unparseable lines. That is right for its callers and fatal here: an
    empty read would present as "no advances, no problem" — the FAIL-OPEN pattern.
    """
    p = path or LEDGER_PATH
    try:
        raw = p.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        raise ExitCriterionError(
            f"gate-authorizations ledger {p} is unreadable ({type(exc).__name__}: {exc}); a "
            f"missing ledger is an UNAVAILABLE check, never zero advances"
        ) from exc
    entries: list[dict] = []
    for lineno, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            raise ExitCriterionError(
                f"{p}:{lineno} is not valid JSON ({exc}); a ledger that cannot be fully parsed "
                f"cannot be counted from"
            ) from exc
        if not isinstance(obj, dict):
            raise ExitCriterionError(f"{p}:{lineno} is not a JSON object")
        entries.append(obj)
    return entries


def product_atoms(path: Path | None = None) -> dict[str, dict]:
    """Map atoms that count as PRODUCT CONTENT, keyed by id.

    Product content = the world, the company and the site — everything the harness
    exists to serve. Harness machinery is excluded on either marker (lane or
    value_stream), so an atom cannot escape the exclusion by carrying only one.
    """
    import yaml

    p = path or MAP_PATH
    try:
        atoms = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ExitCriterionError(
            f"maturity map {p} is unreadable ({type(exc).__name__}: {exc}); without it no atom "
            f"can be classified product-vs-harness"
        ) from exc
    if not isinstance(atoms, list):
        raise ExitCriterionError(f"maturity map {p} did not parse to a list of atoms")
    out: dict[str, dict] = {}
    for a in atoms:
        if not isinstance(a, dict):
            continue
        atom_id = str(a.get("id") or "").strip()
        if not atom_id:
            continue
        if a.get("lane") == HARNESS_LANE or a.get("value_stream") == MACHINERY_VALUE_STREAM:
            continue
        out[atom_id] = a
    if not out:
        raise ExitCriterionError(
            f"maturity map {p} yielded NO product-lane atoms; that is a parse failure, not a "
            f"project with no product"
        )
    return out


def _read_fidelity(path: Path | None = None) -> dict:
    """The fidelity evidence register. Absent is tolerated (it is genuinely sparse — 5
    rows across the whole project today) but MALFORMED is not: a corrupt register would
    silently withdraw the strongest evidence kind from every atom."""
    p = path or FIDELITY_PATH
    if not p.exists():
        return {}
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ExitCriterionError(
            f"fidelity register {p} is malformed ({exc}); a corrupt register would read as "
            f"'no atom has fidelity evidence'"
        ) from exc
    if not isinstance(obj, dict):
        raise ExitCriterionError(f"fidelity register {p} is not a JSON object")
    return obj


def _finite(value) -> bool:
    """R15 NaN-blindness guard: reject non-finite BEFORE any comparison."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return False
    return f == f and f not in (float("inf"), float("-inf"))


# ── evidence resolvers (never read the mover's own provenance prose) ────────────


def _fidelity_row_moved(atom_id: str, fidelity: dict) -> bool:
    """Did a fidelity-register row MOVE for this atom, against a NAMED baseline?

    "Moved against an unchanged baseline" is resolved as: at least one per-cell lift is
    finite and non-zero, and that cell names the baseline it was measured against. A row
    with no named baseline is not evidence of movement — it is a number with nothing to
    have moved relative to.
    """
    for row in fidelity.values():
        if not isinstance(row, dict) or row.get("atom_id") != atom_id:
            continue
        cells = row.get("per_cell_lift")
        if not isinstance(cells, list):
            continue
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            lift = cell.get("lift")
            if not _finite(lift) or float(lift) == 0.0:
                continue
            if str(cell.get("best_baseline_id") or "").strip():
                return True
    return False


def _test_index(tests_root: Path | None = None) -> list[tuple[Path, str]]:
    """(path, MODULE DOCSTRING) for every test module. Read once per evaluation.

    The docstring, not the source. The first cut of this indexed whole-file text and,
    run against the real repository, immediately over-matched: `W1_6b_merit_order_
    reconstruction` "had" acceptance tests in `test_staging_disposition.py` and
    `test_unmerged_work_draw_guard.py`, where the atom id is a FIXTURE STRING in an
    unrelated test's setup. That is the over-counting direction — the one that would
    declare the harness done on evidence that does not exist — so the spec-tie was
    tightened to the module docstring, which is where the tests that genuinely are an
    atom's acceptance tests declare it (`test_money_boundary.py` line 1,
    `test_payment_channel_dd_consistency.py` line 2). It costs real matches (an atom
    named inside a single test's body no longer counts) and that is the acceptable half.
    """
    import ast

    root = tests_root or TESTS_ROOT
    if not root.exists():
        raise ExitCriterionError(
            f"tests root {root} does not exist; the acceptance-test evidence kind cannot be "
            f"resolved, and an unresolvable evidence kind is not an absent one"
        )
    out: list[tuple[Path, str]] = []
    for p in sorted(root.rglob("test_*.py")):
        try:
            doc = ast.get_docstring(ast.parse(p.read_text(encoding="utf-8", errors="replace")))
        except Exception:  # noqa: BLE001 - unparseable/unreadable: simply not indexed
            continue
        if doc:
            out.append((p, doc))
    return out


def _acceptance_test_files(atom_id: str, index: list[tuple[Path, str]]) -> list[Path]:
    """Test modules DECLARING themselves this atom's acceptance tests, by naming the
    atom id in their module docstring. A mention anywhere else in the file is not a
    spec-tie — see `_test_index`."""
    return [p for p, doc in index if atom_id in doc]


def _display_path(p: Path) -> str:
    """Repo-relative where possible, absolute otherwise. `relative_to` RAISES for a path
    outside PROJECT_DIR, which made cosmetic path formatting able to abort the whole
    evaluation whenever the tests root was pointed elsewhere."""
    try:
        return str(p.relative_to(PROJECT_DIR))
    except ValueError:
        return str(p)


@dataclass(frozen=True)
class Evidence:
    """kind: what was found. status: 'confirmed' | 'absent' | 'unchecked'.

    The three are genuinely different and are never collapsed. `absent` means the
    evidence was LOOKED FOR and is not there — the ratified falsification ("a claimed
    advance lacking its exit-criterion delta") and so a reset. `unchecked` means the
    evidence EXISTS but could not be executed here; that does not reset the counter (it
    is not a lack) but it does make the span unprovable.
    """

    kind: str
    status: str
    detail: str = ""


def _resolve_evidence(
    atom_id: str, fidelity: dict, index: list[tuple[Path, str]], test_runner
) -> Evidence:
    if _fidelity_row_moved(atom_id, fidelity):
        return Evidence("fidelity_register_row_moved", "confirmed")
    files = _acceptance_test_files(atom_id, index)
    if not files:
        return Evidence(
            "none",
            "absent",
            "no fidelity row moved and no test module names this atom",
        )
    names = ", ".join(_display_path(f) for f in files[:3])
    if test_runner is None:
        return Evidence(
            "acceptance_test_unexecuted",
            "unchecked",
            f"spec-tied tests exist ({names}) but were not executed, so 'passing' is unproven",
        )
    try:
        passed = bool(test_runner(files))
    except Exception as exc:  # noqa: BLE001 - a runner that blew up checked nothing
        return Evidence(
            "acceptance_test_unexecuted",
            "unchecked",
            f"test runner raised {type(exc).__name__}: {exc}",
        )
    if passed:
        return Evidence("acceptance_test_passing", "confirmed", names)
    return Evidence("acceptance_test_failing", "absent", names)


# ── the walk ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Advance:
    atom: str
    at: float
    level: int | None
    lane: str
    evidence: Evidence

    @property
    def clean(self) -> bool:
        return self.evidence.status == "confirmed"


@dataclass(frozen=True)
class Verdict:
    count: int
    n_required: int | None
    provable: bool
    satisfied: bool
    reset_cause: str | None = None
    advances: tuple = ()
    stalls: tuple = ()
    unprovable_reasons: tuple = ()
    error: str | None = None

    @property
    def decision(self) -> str:
        """The ONE decision this gates. Never a score (R12)."""
        if self.error:
            return "REFUSED"
        return "HARNESS_INVESTMENT_MAY_RESUME" if self.satisfied else "KEEP_BUILDING_PRODUCT"


def content_advances(
    *,
    ledger_path: Path | None = None,
    map_path: Path | None = None,
    fidelity_path: Path | None = None,
    tests_root: Path | None = None,
    test_runner=None,
) -> list[Advance]:
    """Every product-content level move in the ledger, ascending by time, each carrying
    its independently-resolved evidence.

    Only a RECORDED move counts: `gate_authorization.is_valid_level_up`. A
    LEVEL_UP_PROPOSED entry is a proposal, not a level that was reached, and the ratified
    criterion says *reach* — so proposals are not advances here.
    """
    from background.gate_authorization import is_valid_level_up

    entries = _read_ledger_strict(ledger_path)
    products = product_atoms(map_path)
    fidelity = _read_fidelity(fidelity_path)
    index = _test_index(tests_root)

    out: list[Advance] = []
    for entry in entries:
        if not is_valid_level_up(entry):
            continue
        atom_id = str(entry.get("atom") or "").strip()
        atom = products.get(atom_id)
        if atom is None:
            continue  # harness machinery, or an atom no longer in the map
        ts = entry.get("ts")
        if not _finite(ts):
            raise ExitCriterionError(
                f"ledger entry for {atom_id!r} has a non-finite ts ({ts!r}); advances cannot be "
                f"ordered, so no consecutive run can be established"
            )
        level = entry.get("level")
        out.append(
            Advance(
                atom=atom_id,
                at=float(ts),
                level=int(level) if isinstance(level, int) else None,
                lane=str(atom.get("lane") or "?"),
                evidence=_resolve_evidence(atom_id, fidelity, index, test_runner),
            )
        )
    out.sort(key=lambda a: a.at)
    return out


def evaluate(
    now: float | None = None,
    *,
    since: float | None = None,
    ledger_path: Path | None = None,
    map_path: Path | None = None,
    fidelity_path: Path | None = None,
    ratification_path: Path | None = None,
    tests_root: Path | None = None,
    test_runner=None,
    stall_detector=None,
    uncovered_ids: list[str] | None = None,
    point_kind_ids: list[str] | None = None,
) -> Verdict:
    """Compute the counter over the span [since, now].

    The walk is a merged timeline of advances and stall events in time order:

        stall event            -> count = 0     (the ratified falsification)
        advance, evidence absent -> count = 0   (a claimed advance lacking its delta)
        advance, evidence confirmed -> count += 1
        advance, evidence unchecked -> count unchanged, span not provable

    `satisfied` is `provable and count >= N`. Nothing else can set it — in particular a
    large count on an unprovable span does not satisfy it, which is the whole point of
    keeping the two apart.
    """
    import time

    from background import stall_class_register as scr

    now = float(now) if _finite(now) else time.time()

    try:
        n_required = ratified_n(ratification_path)
        advances = content_advances(
            ledger_path=ledger_path,
            map_path=map_path,
            fidelity_path=fidelity_path,
            tests_root=tests_root,
            test_runner=test_runner,
        )
    except ExitCriterionError as exc:
        return Verdict(
            count=0,
            n_required=None,
            provable=False,
            satisfied=False,
            error=str(exc)[:500],
            unprovable_reasons=("a primary-state input could not be read",),
        )

    span_start = float(since) if _finite(since) else (advances[0].at if advances else now)

    detect = stall_detector or scr.detect_progress_gap_stalls
    try:
        stalls = list(detect(span_start, now))
    except Exception as exc:  # noqa: BLE001 - a detector that blew up detected nothing
        stalls = [
            scr.StallEvent(
                "meaningful_progress_gap",
                None,
                f"stall detector raised {type(exc).__name__}: {exc}",
                unavailable=True,
            )
        ]

    reasons: list[str] = []

    # HX2's load-bearing consequence, obeyed literally.
    uncov = list(uncovered_ids) if uncovered_ids is not None else scr.uncovered_class_ids()
    if uncov:
        reasons.append(
            f"stall classes with NO detector: {', '.join(uncov)} — a zero stall count is not "
            f"proof of a clean span (HX2_STALL_SET_COVERAGE_VERDICT.md)"
        )

    # `point`-kind classes hold state that is overwritten in place and never committed,
    # so they cannot be reconstructed over a PAST span. Sampling them each tick is the
    # named HX1 residual; until it exists, their silence over the span proves nothing.
    if point_kind_ids is not None:
        points = list(point_kind_ids)
    else:
        points = [
            c.id for c in scr.STALL_CLASSES if c.evidence_kind == "point" and c.detector is not None
        ]
    if points:
        reasons.append(
            f"point-kind stall classes are not reconstructible over a past span: "
            f"{', '.join(points)} — they must be SAMPLED each tick (HX1 residual)"
        )

    if any(getattr(s, "unavailable", False) for s in stalls):
        reasons.append(
            "a stall detector reported UNAVAILABLE — an unavailable check is a FAILED check (R15)"
        )

    # The walk.
    timeline: list[tuple[float, int, object]] = []
    for s in stalls:
        if _finite(getattr(s, "at", None)):
            timeline.append((float(s.at), 0, s))  # a stall at the same instant lands FIRST
    for a in advances:
        timeline.append((a.at, 1, a))
    timeline.sort(key=lambda row: (row[0], row[1]))

    count = 0
    reset_cause: str | None = None
    saw_absent = False
    for _ts, kind, item in timeline:
        if kind == 0:
            count = 0
            reset_cause = f"stall-class event {item.class_id}: {item.detail[:160]}"
            continue
        if item.evidence.status == "confirmed":
            count += 1
        elif item.evidence.status == "absent":
            saw_absent = True
            count = 0
            reset_cause = (
                f"{item.atom} reached level {item.level} with no resolvable exit-criterion "
                f"delta ({item.evidence.detail or item.evidence.kind})"
            )
        else:
            reasons.append(
                f"{item.atom}: {item.evidence.detail or item.evidence.kind}"
            )

    if saw_absent:
        reasons.append(
            f"evidence kinds not machine-resolvable here: {', '.join(UNIMPLEMENTED_EVIDENCE_KINDS)} "
            f"— an advance resting only on one of these reads as lacking, which under-counts"
        )

    provable = not reasons
    return Verdict(
        count=count,
        n_required=n_required,
        provable=provable,
        satisfied=provable and count >= n_required,
        reset_cause=reset_cause,
        advances=tuple(advances),
        stalls=tuple(stalls),
        unprovable_reasons=tuple(dict.fromkeys(reasons)),
    )


def summary_line(verdict: Verdict | None = None) -> str:
    """One markdown line. Publication (daily self-note, and the derivability gate that
    stops a hand-written 'harness is done' claim anywhere else) is HX3's scope, not this
    module's — this is the value HX3 renders, kept here so there is exactly one
    computation of it."""
    v = verdict if verdict is not None else evaluate()
    if v.error:
        return f"🔴 **Harness exit criterion: REFUSED** — {v.error}"
    n = v.n_required
    if v.satisfied:
        return (
            f"🟢 Harness exit criterion MET: {v.count}/{n} consecutive clean product-content "
            f"advances across a provably stall-free span — harness investment may resume."
        )
    if not v.provable:
        return (
            f"🟠 Harness exit criterion: count {v.count}/{n}, span NOT PROVABLY clean — "
            f"{'; '.join(v.unprovable_reasons)[:400]}"
        )
    return (
        f"🟠 Harness exit criterion: {v.count}/{n} consecutive clean advances"
        + (f" — last reset: {v.reset_cause}" if v.reset_cause else "")
    )
