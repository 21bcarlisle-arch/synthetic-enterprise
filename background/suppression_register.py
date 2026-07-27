"""R10 SUPPRESSION SWEEP -- the standing gate (DIRECTOR_RULING_FAILURE_BIAS_LAWS 2026-07-27).

The director's standing consequence, verbatim: *"From now on, when a false positive is
suppressed, the fix must state what will still page if the underlying condition is real.
A suppression proposed without that answer is rejected."*

This module mechanises that consequence (MAKE_IT_STICK: a rule lives as code or not at all).
The register (`docs/observability/suppression_register.json`) enumerates every gate / throttle
/ suppression / fold in the harness, classified by failure direction; this gate asserts that
EVERY registered suppression carries a non-empty `what_still_pages` -- the independent check
that fires if the underlying condition is real.

SCOPE HONESTY (R9): this gate enforces the *declaration* on every REGISTERED suppression.
It does not by itself force a newly-written suppression to be registered -- that remains a
convention backed by the ruling's standing consequence and the R10 sweep discipline. The
mechanised, mutation-tested half is the declaration requirement; the convention half is named
here rather than dressed up as fully mechanical.

FAIL-CLOSED by design (R15): a registered suppression with an empty/missing `what_still_pages`
is a DEFECT and this validator reports it. (Contrast the draw-side gates, which fail-open
toward WORK; here the safe direction is to REFUSE a silence-biased mechanism that names no
pager.) A missing/malformed register file is itself a violation -- an unavailable check is a
failed check (R15 FAIL-SILENT killer), never a silent pass.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
SUPPRESSION_REGISTER_PATH = PROJECT_DIR / "docs" / "observability" / "suppression_register.json"

# The remediation vocabulary a silent-biased suppression may claim.
_VALID_REMEDIATIONS = {"law_a", "law_b", "law_c", "none"}
_VALID_FAILURE_DIRECTIONS = {"noisy", "silent"}


def load_register(path: Path | None = None) -> dict:
    """Load the suppression register. Raises on missing/malformed -- an unavailable
    gate is a FAILED gate (R15), never a silent pass."""
    p = path or SUPPRESSION_REGISTER_PATH
    if not p.exists():
        raise FileNotFoundError(f"suppression register missing: {p}")
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError(f"suppression register malformed (no 'entries' list): {p}")
    return data


def validate_suppression_register(register: dict[str, Any] | None = None,
                                  path: Path | None = None) -> list[str]:
    """Return a list of violation strings (EMPTY == the gate passes).

    Each registered suppression must:
      - carry a non-empty `what_still_pages` (the standing consequence), AND
      - declare a valid `failure_direction` and `remediation`, AND
      - if it fails toward SILENCE, either be `status: compliant` OR name a
        remediation that is not `none` (a silent-biased mechanism with no
        remediation and no compliant status is exactly the defect this law forbids).
    """
    reg = register if register is not None else load_register(path)
    entries = reg.get("entries", [])
    violations: list[str] = []
    for e in entries:
        eid = e.get("id", "<no-id>")
        wsp = (e.get("what_still_pages") or "").strip()
        if not wsp:
            violations.append(
                f"{eid}: empty `what_still_pages` -- the standing consequence forbids a "
                f"suppression that names no independent pager for a real underlying condition."
            )
        fd = e.get("failure_direction")
        if fd not in _VALID_FAILURE_DIRECTIONS:
            violations.append(f"{eid}: failure_direction {fd!r} not in {_VALID_FAILURE_DIRECTIONS}.")
        rem = e.get("remediation")
        # A remediation may be COMPOUND (e.g. "law_a + law_b"): a silence-biased mechanism
        # can need both a time-bound AND lane-isolation. Validate each token.
        rem_tokens = {t.strip() for t in str(rem).split("+")} if rem is not None else set()
        bad_tokens = rem_tokens - _VALID_REMEDIATIONS
        if not rem_tokens or bad_tokens:
            violations.append(f"{eid}: remediation {rem!r} not in {_VALID_REMEDIATIONS} (compound allowed via '+').")
        remediated = bool(rem_tokens - {"none"})
        if fd == "silent" and not remediated and e.get("status") != "compliant":
            violations.append(
                f"{eid}: silent-biased with remediation 'none' and status != 'compliant' -- "
                f"a silence-failing suppression must be either remediated (law_a/b/c) or proven compliant."
            )
    return violations


def register_is_clean(path: Path | None = None) -> bool:
    """True iff every registered suppression declares an independent pager and a valid
    classification. Raises (never silently True) if the register itself is unavailable."""
    return not validate_suppression_register(path=path)
