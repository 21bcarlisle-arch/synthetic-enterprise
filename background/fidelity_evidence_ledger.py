"""Fidelity-evidence EMIT-LEDGER + emit-DoD phase-close gate -- atom **G2**
(Epoch-2 `G_data_learning` lane, HARNESS-side; sibling to G1's
`background/fidelity_grid_scorer.py`).

Design source (read this pass, no network):
    docs/design/EPOCH2_G_FIDELITY_EVIDENCE_MACHINERY_DISCOVER.md  S2 (the
        evidence-record data model + provenance enum), S3 (the emit-DoD: a
        physics atom is not done until it emits fitted relationship +
        strength + provenance, per-cell lift, binding constraint, and CRN
        ablation Delta where it touches a crisis cell), S3.2 (illustrative
        record shape), S3.3 (the gate), S5 (the R15 mutation requirements).

WHAT THIS MODULE IS. Two pieces:

    1. The SIBLING emit-ledger (`append_record` / `load_ledger` /
       `records_for_atom`), writing to
       `docs/observability/fidelity_evidence_ledger.json`. Deliberately a
       NEW, separate file from `coupled_gap_ledger.json` -- writing an
       un-wired entry into the gap ledger before a real consumer existed has
       previously wedged the publish gate (its existing consumers, Proof
       door / digest, read every entry and choke on an unexpected shape).
       This ledger's only consumer THIS TURN is `fidelity_evidence_gate`
       below; nothing else reads it yet, so nothing else can red.

    2. The emit-DoD phase-close gate (`fidelity_evidence_gate`) -- a
       physics atom's phase-close calls this with its `atom_id` and gets
       back a `GateResult` that REDS on any of the three named defects
       (S3.3/S5), and REDS (fail-closed, R15 fail-silent doctrine) if the
       ledger itself cannot be read.

FIELD-SHAPE REUSE (do NOT invent a divergent schema). Where a field overlaps
with G1's dataclasses (`background/fidelity_grid_scorer.py`), the NAME is
kept identical so a G1 result serialises straight into a ledger record
without a translation layer:
    * `LiftResult.err_model` / `.err_best_naive` / `.lift` / `.commercial_weight`
      -> the `per_cell_lift[i]` entry's `err_model` / `err_naive` / `lift` /
      `commercial_weight` (the DISCOVER doc's S3.2 illustrative shape calls
      G1's `err_best_naive` "`err_naive`"; kept as `err_naive` here to match
      the spec's own worked example verbatim).
    * `AblationResult.delta_worst_cell` / `.crn_substream_isolated` /
      `.verdict` -> the `ablation.delta_worst_cell` / `ablation.crn.
      substream_isolated` / `ablation.verdict` fields below.

THE WALL (CLAUDE.md Architectural Laws). Pure HARNESS code, same standing as
`fidelity_grid_scorer.py` / `gap_metric.py` / `coupled_triad.py`: it sits
OUTSIDE the epistemic wall by design. It never imports `sim.*` /
`simulation.*` / `company.*` / `saas.*` -- it operates purely on
already-computed evidence dicts handed to it by callers on either side of
the wall.

R12 anti-goal-seek: this module never adjusts a record, a threshold, or the
gate's verdict to flatter a "done" reading. R15: each of the gate's three
red conditions below is proven, in `tests/test_fidelity_evidence_ledger.py`,
to fire on its own named defect and clear when the defect is removed
(mutation-tested, not just happy-path-tested).

R10 simplification asserted in this module:
    * The append-time structural validator (`_validate_record`) deliberately
      does NOT enforce "asserted => simplification_id required" or "ablation
      => crn.substream_isolated required" -- those are the GATE's job (S3.3),
      not the writer's. A writer that refused to accept a defective record
      would make the R15 mutation tests un-constructible (there would be no
      way to build the ledger state the gate is supposed to catch). The
      writer only rejects STRUCTURALLY malformed input (wrong types, missing
      required keys) -- never a record that is merely epistemically dishonest.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PROJECT_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "fidelity_evidence_ledger.json"

# The provenance enum (DISCOVER doc S2), unchanged.
PROVENANCE_KINDS: Tuple[str, ...] = ("estimated_from_data", "assumed", "asserted")

_ABLATION_VERDICTS: Tuple[str, ...] = ("load_bearing", "decorative", "deferred")

# Required top-level keys on every ledger record (S3.2).
_REQUIRED_TOP_KEYS = ("rel_id", "atom_id", "relationship")
_REQUIRED_RELATIONSHIP_KEYS = ("kind", "provenance", "simplification_id")


class LedgerMalformed(ValueError):
    """Raised by `append_record` when a record is STRUCTURALLY malformed
    (wrong type / missing required key) -- never raised for a merely
    epistemically-dishonest-but-well-shaped record (that is the gate's job,
    not the writer's; see module R10 note)."""


class LedgerUnavailable(Exception):
    """Raised by the strict ledger reader when the ledger file is missing,
    unreadable, not valid JSON, or not a JSON object. This is the R15
    FAIL-SILENT guard: an unavailable ledger is a FAILED check for anything
    that depends on reading it (`fidelity_evidence_gate`), never treated as
    'zero records, pass'."""


# ===========================================================================
# Record validation (structural only -- see module R10 note)
# ===========================================================================

def _validate_record(record: Mapping[str, Any]) -> None:
    """Structural (type/required-key) validation only. Deliberately does NOT
    enforce the R10 asserted<=>simplification_id rule or the CRN-isolation
    rule -- those are checked by `fidelity_evidence_gate`, not here (a
    writer that rejected them would make the gate's own R15 mutation tests
    unconstructable). Raises `LedgerMalformed` fail-closed on anything that
    is not even a well-shaped record."""
    if not isinstance(record, Mapping):
        raise LedgerMalformed(f"record must be a mapping, got {type(record).__name__}")

    for key in _REQUIRED_TOP_KEYS:
        if key not in record:
            raise LedgerMalformed(f"record missing required top-level key {key!r}")

    if not isinstance(record["rel_id"], str) or not record["rel_id"]:
        raise LedgerMalformed("rel_id must be a non-empty string")
    if not isinstance(record["atom_id"], str) or not record["atom_id"]:
        raise LedgerMalformed("atom_id must be a non-empty string")

    rel = record["relationship"]
    if not isinstance(rel, Mapping):
        raise LedgerMalformed("relationship must be a mapping")
    for key in _REQUIRED_RELATIONSHIP_KEYS:
        if key not in rel:
            raise LedgerMalformed(f"relationship missing required key {key!r}")
    if not isinstance(rel["kind"], str) or not rel["kind"]:
        raise LedgerMalformed("relationship.kind must be a non-empty string")
    if rel["provenance"] not in PROVENANCE_KINDS:
        raise LedgerMalformed(
            f"relationship.provenance must be one of {PROVENANCE_KINDS}, "
            f"got {rel['provenance']!r}"
        )
    simp_id = rel["simplification_id"]
    if simp_id is not None and not isinstance(simp_id, str):
        raise LedgerMalformed("relationship.simplification_id must be str or None")

    per_cell = record.get("per_cell_lift", [])
    if not isinstance(per_cell, list):
        raise LedgerMalformed("per_cell_lift must be a list")
    for entry in per_cell:
        if not isinstance(entry, Mapping):
            raise LedgerMalformed("per_cell_lift entries must be mappings")

    ablation = record.get("ablation")
    if ablation is not None:
        if not isinstance(ablation, Mapping):
            raise LedgerMalformed("ablation must be a mapping or None")
        crn = ablation.get("crn")
        if crn is not None and not isinstance(crn, Mapping):
            raise LedgerMalformed("ablation.crn must be a mapping or None")
        verdict = ablation.get("verdict")
        if verdict is not None and verdict not in _ABLATION_VERDICTS:
            raise LedgerMalformed(
                f"ablation.verdict must be one of {_ABLATION_VERDICTS} or None, "
                f"got {verdict!r}"
            )


# ===========================================================================
# Ledger read/write
# ===========================================================================

def _read_ledger_file_strict(path: Path) -> Dict[str, dict]:
    """The FAIL-CLOSED reader. Missing file, unreadable file, invalid JSON,
    or a top-level value that isn't a JSON object are ALL `LedgerUnavailable`
    -- never silently degraded to `{}` (that would be the FAIL-SILENT pattern
    R15 forbids: an unavailable ledger must be a FAILED check for any caller
    that depends on it, not a quiet 'nothing recorded, pass')."""
    if not path.is_file():
        raise LedgerUnavailable(f"ledger file does not exist: {path}")
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LedgerUnavailable(f"ledger file unreadable: {path} ({exc})") from exc
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise LedgerUnavailable(f"ledger file is not valid JSON: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise LedgerUnavailable(
            f"ledger file top level must be a JSON object, got {type(data).__name__}: {path}"
        )
    return data


def load_ledger(path: Optional[Path] = None) -> Dict[str, dict]:
    """Read the full ledger. Fail-closed: raises `LedgerUnavailable` rather
    than returning `{}` on a missing/malformed file -- callers that want the
    "no ledger yet, that's fine" convenience (e.g. a first-ever append) must
    catch it explicitly, matching this module's own `append_record`."""
    p = Path(path) if path is not None else LEDGER_PATH
    return _read_ledger_file_strict(p)


def append_record(record: Mapping[str, Any], *, ledger_path: Optional[Path] = None) -> Dict[str, dict]:
    """Validate `record` structurally (fail-closed on malformed input, see
    `_validate_record`) and merge it into the ledger, keyed by `rel_id`
    (read-merge-write, preserving other entries). A missing/unreadable
    EXISTING ledger file is treated as 'nothing recorded yet' here (this is
    the writer's own bootstrap case, not the gate's fail-closed read) -- but
    a ledger file that exists and is simply not a JSON object is still a
    hard error, never silently clobbered.

    Returns the full ledger dict after the merge.
    """
    _validate_record(record)

    path = Path(ledger_path) if ledger_path is not None else LEDGER_PATH
    ledger: Dict[str, dict] = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise LedgerMalformed(
                f"existing ledger file is not valid JSON, refusing to clobber: {path} ({exc})"
            ) from exc
        if not isinstance(loaded, dict):
            raise LedgerMalformed(
                f"existing ledger file top level is not a JSON object, refusing to clobber: {path}"
            )
        ledger = loaded

    ledger[record["rel_id"]] = dict(record)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ledger


def records_for_atom(atom_id: str, ledger: Mapping[str, dict]) -> List[dict]:
    """All records in `ledger` emitted by `atom_id`, in stable (sorted by
    rel_id) order. Pure lookup -- no I/O."""
    return [
        rec for rel_id, rec in sorted(ledger.items())
        if isinstance(rec, Mapping) and rec.get("atom_id") == atom_id
    ]


# ===========================================================================
# The emit-DoD phase-close gate (S3.3)
# ===========================================================================

@dataclass(frozen=True)
class GateResult:
    """The gate's verdict for one atom. `passed` is False iff ANY reason is
    present -- `reasons` is never empty on a fail and always empty on a
    pass, so a caller can `assert result.passed` or inspect `result.reasons`
    without re-deriving pass/fail from the reason list itself."""

    atom_id: str
    passed: bool
    reasons: Tuple[str, ...] = field(default_factory=tuple)


def fidelity_evidence_gate(atom_id: str, *, ledger_path: Optional[Path] = None) -> GateResult:
    """The emit-DoD phase-close check (DISCOVER doc S3.3). A physics atom's
    phase-close calls this with its own `atom_id`; the atom is NOT DONE
    (`passed=False`) if ANY of:

        (a) it has ZERO evidence records in the ledger;
        (b) any of its records has `provenance == "asserted"` with
            `simplification_id is None` (R10 mechanised -- an asserted
            relationship dressed as estimated);
        (c) any of its records carries an `ablation` block whose
            `crn.substream_isolated` is not `True` (a CRN ablation Delta
            recorded without proven substream isolation is noise, S1.3/S5
            killer-mutation-B, never a valid emitted number).

    FAIL-CLOSED (R15 fail-silent doctrine): if the ledger itself cannot be
    read (missing / unreadable / malformed JSON / not an object), THIS is
    itself a failure reason -- a check that can't read its input is a FAILED
    check, never a silent pass.
    """
    try:
        ledger = load_ledger(ledger_path)
    except LedgerUnavailable as exc:
        return GateResult(
            atom_id=atom_id, passed=False,
            reasons=(f"fidelity-evidence ledger unavailable, cannot verify emit-DoD: {exc}",),
        )

    records = records_for_atom(atom_id, ledger)
    if not records:
        return GateResult(
            atom_id=atom_id, passed=False,
            reasons=(f"{atom_id}: zero fidelity-evidence records in the ledger",),
        )

    reasons: List[str] = []
    for rec in records:
        rel_id = rec.get("rel_id", "<unknown-rel_id>")
        rel = rec.get("relationship") or {}
        provenance = rel.get("provenance")
        simplification_id = rel.get("simplification_id")
        if provenance == "asserted" and simplification_id is None:
            reasons.append(
                f"{rel_id}: provenance='asserted' with simplification_id=null "
                "(R10 -- an asserted relationship must register a simplification)"
            )

        ablation = rec.get("ablation")
        if ablation is not None:
            crn = ablation.get("crn") or {}
            if crn.get("substream_isolated") is not True:
                reasons.append(
                    f"{rel_id}: ablation recorded without proven CRN substream "
                    "isolation (crn.substream_isolated is not True) -- a Delta "
                    "without isolation is noise, not evidence (S1.3/S5)"
                )

    return GateResult(atom_id=atom_id, passed=not reasons, reasons=tuple(reasons))
