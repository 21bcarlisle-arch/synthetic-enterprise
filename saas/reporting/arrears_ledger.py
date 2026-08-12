"""The one reader for the billing ledger's arrears history -- and the one place
that knows the difference between "no arrears" and "no ledger".

WHY THIS EXISTS (2026-08-12, closing
`WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN_ON_A_MISSING_LEDGER_2026-08-09.md` as a
CLASS, per R10 -- an absurdity-class defect may not be closed with an instance fix).

Three independent surfaces derived an arrears RAG from their own copy of the same
`site/state/billing_ledger.json` read, each swallowing the absence of the file into
an empty dict:

  * `saas/reporting/annual_report.py::_section_population_anchoring`  (ANNUAL_REPORT.md)
  * `tools/generate_dashboard_data.py::extract_arrears_case_load`     (dashboard.json)
  * `tools/population_anchor.py::generate`                            (population_anchoring.json)

Because the numerator went to zero while the denominator (active customers) stayed
positive, every one of them printed a *confident* 0.0% arrears rate and a GREEN
verdict. The observed-correct figures on the same input are 7.7%-46.2%: two years
GREEN, six RED. Absent data rendered as a perfect compliance record -- the R15
FAIL-OPEN pattern verbatim, and undetectable by eye, because 0.0% is also a
legitimate reading (2025 genuinely renders 0.0% with the ledger present).

THE RULE THIS MODULE ENFORCES: an unavailable check is a FAILED check, never a
green one. `load()` reports `available` as its own field, and every consumer must
branch on it rather than on the emptiness of `arrears_by_year` -- the two are
distinguishable here and nowhere else.

A ledger that parses but carries no customers counts as UNAVAILABLE. That is
deliberate: a populated ledger is the numerator's only source, so "zero customers
on file" cannot support an arrears rate over a non-zero active population any more
than a missing file can. Treating it as available would leave the same absurdity
reachable through a second door.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

# What a consumer prints instead of a RAG when the ledger did not load. Shared so
# the three surfaces cannot drift into three different phrasings of "we don't know".
UNAVAILABLE_NOTE = "arrears not assessed -- billing ledger unavailable"


@dataclass(frozen=True)
class ArrearsLedgerView:
    """A loaded (or explicitly un-loaded) view of the ledger's arrears history.

    `available` is the field that matters. `arrears_by_year` is empty in BOTH the
    unavailable case and the genuine no-arrears case, which is exactly why callers
    must not infer availability from it.
    """

    available: bool
    unavailable_reason: str
    customers: Mapping[str, dict]
    arrears_by_year: Mapping[int, frozenset]

    def customer_ids_for(self, year: int) -> frozenset:
        """Distinct customers who opened an arrears case in `year` (empty frozenset
        when none, or when the ledger is unavailable -- check `available` first)."""
        return self.arrears_by_year.get(year, frozenset())

    def count_for(self, year: int) -> int:
        return len(self.customer_ids_for(year))


def _unavailable(reason: str) -> ArrearsLedgerView:
    return ArrearsLedgerView(
        available=False, unavailable_reason=reason, customers={}, arrears_by_year={}
    )


def load(ledger_path: Path | str) -> ArrearsLedgerView:
    """Read the billing ledger at `ledger_path` into an `ArrearsLedgerView`.

    Never raises on a bad path or bad content -- it reports. Every failure mode
    below used to be an `except: pass` that produced a green arrears column.
    """
    path = Path(ledger_path)
    try:
        raw = path.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError, PermissionError, OSError):
        return _unavailable(f"ledger not readable at {path}")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _unavailable(f"ledger at {path} is not valid JSON ({exc.msg})")

    return from_payload(payload, source=str(path))


def from_payload(payload, source: str = "in-memory ledger") -> ArrearsLedgerView:
    """The same view built from an already-parsed ledger payload.

    Consumers that hold the ledger in memory go through here rather than reading
    `payload["customers"]` themselves, so that the availability question is asked
    in exactly one place no matter which door the data came in by.
    """
    if not isinstance(payload, dict):
        return _unavailable(f"{source} is not an object")

    customers = payload.get("customers")
    if not isinstance(customers, dict) or not customers:
        return _unavailable(f"{source} carries no customers")

    by_year: dict[int, set] = {}
    for cid, cdata in customers.items():
        if not isinstance(cdata, dict):
            continue
        for case in cdata.get("arrears_history") or []:
            if not isinstance(case, dict):
                continue
            opened = case.get("opened_date") or ""
            try:
                year = int(str(opened)[:4])
            except ValueError:
                continue
            by_year.setdefault(year, set()).add(cid)

    return ArrearsLedgerView(
        available=True,
        unavailable_reason="",
        customers=customers,
        arrears_by_year={yr: frozenset(ids) for yr, ids in by_year.items()},
    )
