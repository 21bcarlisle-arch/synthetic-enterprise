"""CreditBureauPort -- structural interface for the credit-check epistemic boundary.

Adapter implementations satisfy this Protocol without requiring inheritance,
same pattern as tools/market_data_port.py::MarketDataPort (Phase PV).

Epistemic boundary (see CLAUDE.md "Architectural Laws"): a real energy supplier
does not know an applicant's true creditworthiness. It pays a credit bureau for
an imperfect, purchased signal, and that noisy read -- not the ground truth --
is what actually drives the accept/reject decision. CreditCheckResult carries
both the observable bureau read (passed, score_band) and, for evidence/analytics
use only, the SIM's ground truth (true_creditworthy). Company-side decision code
(company/**) must only ever read `passed` / `score_band`.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class CreditCheckResult:
    passed: bool
    score_band: str
    # SIM-internal ground truth for evidence/analytics use only (e.g. false-decline/
    # false-accept divergence reporting). Must NEVER be read by company/** decision code.
    true_creditworthy: bool


@runtime_checkable
class CreditBureauPort(Protocol):
    def check_credit(self, applicant_id: str, segment: str, seed: str) -> CreditCheckResult: ...
