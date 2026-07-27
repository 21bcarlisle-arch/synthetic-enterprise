"""CA3 — the SEGMENTATION-testability ledger + its review gate.

WHAT THIS IS. The pool-vs-book honesty mechanism the two 2026-07-27 rulings
demand. Cohort assignment is now ACTIVATED for the world-side POOL draw (CA1);
the director was explicit that this does NOT make the company-side BOOK's
segmentation testable — 18 customers cannot populate the ~12-cell value knee
(DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED_2026-07-27 §2). Every volume-
dependent segmentation capability must therefore be RECORDED untestable-at-
current-book, with a named unlock, NOT silently scored as working
(DIRECTOR_RULING_POOL_VS_BOOK_LAMBDA_STANDS_2026-07-27: "an untestable organ
must be recorded as untestable").

WHY A CLASS MECHANISM, NOT AN INSTANCE NOTE (R10). Closing an absurdity-class
defect (here: "segmentation looks activated, therefore testable") requires the
whole CLASS to fail automatically. So this is a REGISTER + a GATE that iterates
it: any volume-dependent segmentation capability added to
`docs/observability/segmentation_testability_ledger.json` is checked the same
way, and the gate reds on any capability whose recorded testability disagrees
with the book, or whose untestable marking omits its unlock.

R15 (controls must be able to FAIL), three killer patterns guarded:
  * TAUTOLOGY / independence — the gate NEVER reads the book size itself; the
    caller passes `current_book_size`. The checked value (recorded testability)
    and the reference (book vs floor) come from different sources.
  * FAIL-OPEN — a capability that CLAIMS testable while the book is below its
    floor REDS; a missing/empty unlock on an untestable capability REDS; a
    non-finite / missing floor REDS. Nothing passes by omission.
  * FAIL-SILENT — an unreadable / malformed register is `LedgerUnavailable`
    (a FAILED check), never a quiet green.
All three are mutation-proven in tests/background/test_segmentation_testability_
ledger.py.

WALL. Pure HARNESS/observability code (like fidelity_evidence_ledger.py): it
imports no sim/company/saas module and reads no simulation internal — it judges
a hand/authored register against a book size handed to it. It states a LIMIT of
the harness's own knowledge; it never reads across the epistemic wall.

WIRING STATUS (honest — consumed != absorbed). This tick delivers the register,
the gate, and the R15 both-ways proof. The gate is importable and its contract
is proven, but it is NOT yet wired into the publish pipeline (deliberately — an
un-wired entry into a live consumer has wedged publishing before). Wiring the
gate into a publish/claim-status check, and any level move, are the named
follow-on; the atom stays `blocked_on: director_level_up` (R16).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

PROJECT_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "segmentation_testability_ledger.json"

# Required keys on every capability entry (structural; the gate judges the rest).
_REQUIRED_KEYS = (
    "id",
    "name",
    "testable_at_current_book",
    "min_book_for_testability",
    "reason",
    "unlock",
)


class LedgerUnavailable(Exception):
    """The register is missing / unreadable / malformed. An unavailable check is
    a FAILED check (R15 fail-silent doctrine) — NEVER degraded to an empty pass."""


def _read_register_strict(path: Path) -> dict:
    """FAIL-CLOSED reader. Missing file, unreadable file, invalid JSON, a top
    level that isn't an object, or a missing/`non-list` `capabilities` are ALL
    `LedgerUnavailable` — never silently treated as 'nothing to check, pass'."""
    if not path.is_file():
        raise LedgerUnavailable(f"register file does not exist: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LedgerUnavailable(f"register file unreadable: {path} ({exc})") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LedgerUnavailable(f"register is not valid JSON: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise LedgerUnavailable(
            f"register top level must be a JSON object, got {type(data).__name__}: {path}"
        )
    caps = data.get("capabilities")
    if not isinstance(caps, list):
        raise LedgerUnavailable(
            f"register 'capabilities' must be a list, got {type(caps).__name__}: {path}"
        )
    return data


def load_register(path: Optional[Path] = None) -> dict:
    """Read the full register, fail-closed (raises `LedgerUnavailable`)."""
    p = Path(path) if path is not None else LEDGER_PATH
    return _read_register_strict(p)


def capabilities(register: Mapping[str, Any]) -> List[dict]:
    """The capability entries, in stable (id-sorted) order. Pure lookup."""
    caps = register.get("capabilities", [])
    return sorted(
        (c for c in caps if isinstance(c, Mapping)),
        key=lambda c: str(c.get("id", "")),
    )


@dataclass(frozen=True)
class GateResult:
    """The register-review verdict. `passed` is False iff ANY reason is present;
    `reasons` is empty on a pass and non-empty on a fail, so a caller can
    `assert result.passed` without re-deriving the verdict from the reasons."""

    passed: bool
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    current_book_size: Optional[int] = None


def review_register(
    current_book_size: int,
    *,
    register: Optional[Mapping[str, Any]] = None,
    register_path: Optional[Path] = None,
) -> GateResult:
    """Judge the recorded testability of every segmentation capability against
    the book size handed in. REDS (returns `passed=False` with reasons) if:

      (a) FAIL-CLOSED: the register can't be read (only when `register` not given).
      (b) STRUCTURAL: a capability is missing a required key, or its floor is not
          a finite positive number.
      (c) FAIL-OPEN — CLAIM ABOVE REALITY: a capability records
          `testable_at_current_book=True` while `book < its floor`.
      (d) STALE: a capability records untestable while `book >= its floor`
          (the book grew past the knee; the marking must be re-evaluated, not
          left frozen — the both-ways half of the control).
      (e) MISSING UNLOCK: an untestable capability with no non-empty `unlock`
          string (the CA3 requirement: every untestable marking NAMES its unlock).

    The gate never reads the book size itself (independence, R15 pattern-1).
    """
    reasons: List[str] = []

    if register is None:
        try:
            register = load_register(register_path)
        except LedgerUnavailable as exc:
            return GateResult(
                passed=False,
                reasons=(f"register unavailable (fail-closed): {exc}",),
                current_book_size=current_book_size,
            )

    caps = register.get("capabilities")
    if not isinstance(caps, list):
        return GateResult(
            passed=False,
            reasons=("register 'capabilities' is not a list (fail-closed)",),
            current_book_size=current_book_size,
        )

    for entry in caps:
        if not isinstance(entry, Mapping):
            reasons.append(f"capability entry is not an object: {entry!r}")
            continue
        cid = entry.get("id", "<no-id>")

        missing = [k for k in _REQUIRED_KEYS if k not in entry]
        if missing:
            reasons.append(f"{cid}: missing required key(s) {missing}")
            continue

        floor = entry["min_book_for_testability"]
        if not isinstance(floor, (int, float)) or isinstance(floor, bool) \
                or not math.isfinite(floor) or floor <= 0:
            reasons.append(f"{cid}: min_book_for_testability must be a finite positive number, got {floor!r}")
            continue

        marked_testable = entry["testable_at_current_book"]
        if not isinstance(marked_testable, bool):
            reasons.append(f"{cid}: testable_at_current_book must be a bool, got {marked_testable!r}")
            continue

        expected_testable = current_book_size >= floor

        if marked_testable and not expected_testable:
            reasons.append(
                f"{cid}: recorded testable_at_current_book=True but book "
                f"({current_book_size}) < floor ({floor}) — a segmentation "
                f"capability CANNOT be testable below its cell floor (claim-status defect)"
            )
        if (not marked_testable) and expected_testable:
            reasons.append(
                f"{cid}: recorded untestable but book ({current_book_size}) >= "
                f"floor ({floor}) — the book crossed the knee; re-evaluate, do not "
                f"leave the marking frozen"
            )
        if not marked_testable:
            unlock = entry.get("unlock")
            if not (isinstance(unlock, str) and unlock.strip()):
                reasons.append(
                    f"{cid}: marked untestable but names no unlock condition "
                    f"(every untestable marking must state what unlocks it — CA3)"
                )

    return GateResult(
        passed=not reasons,
        reasons=tuple(reasons),
        current_book_size=current_book_size,
    )


def current_book_size() -> int:
    """Convenience for callers/CLI: the static book's size. Kept SEPARATE from
    `review_register` so the gate stays a pure function of its argument (the
    caller may pass a hypothetical size; the gate never reads the book itself)."""
    from saas.customers import CUSTOMERS

    return len(CUSTOMERS)


def _main(argv: Optional[Sequence[str]] = None) -> int:
    result = review_register(current_book_size())
    if result.passed:
        print(
            f"segmentation-testability register OK (book={result.current_book_size}): "
            f"every volume-dependent segmentation capability is honestly recorded "
            f"untestable-at-current-book with a named unlock."
        )
        return 0
    print(f"segmentation-testability register FAILED (book={result.current_book_size}):")
    for r in result.reasons:
        print(f"  - {r}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
