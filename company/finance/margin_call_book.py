from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MarginCallStatus(str, Enum):
    RECEIVED = "received"
    SETTLED = "settled"
    DISPUTED = "disputed"
    DEFAULTED = "defaulted"


@dataclass(frozen=True)
class MarginCallEvent:
    call_id: str
    call_date: str
    counterparty: str
    contract_id: str
    initial_margin_gbp: float
    variation_margin_gbp: float
    settlement_deadline: str
    status: MarginCallStatus = MarginCallStatus.RECEIVED

    @property
    def total_margin_required_gbp(self) -> float:
        return round(self.initial_margin_gbp + self.variation_margin_gbp, 2)

    @property
    def is_settled(self) -> bool:
        return self.status == MarginCallStatus.SETTLED

    @property
    def is_stress_event(self) -> bool:
        return self.variation_margin_gbp > 500_000.0


class MarginCallBook:
    def __init__(self, credit_facility_gbp: float = 5_000_000.0) -> None:
        self._calls: list[MarginCallEvent] = []
        self.credit_facility_gbp = credit_facility_gbp

    def record_call(self, call: MarginCallEvent) -> MarginCallEvent:
        self._calls.append(call)
        return call

    def settle_call(self, call_id: str) -> Optional[MarginCallEvent]:
        for i, c in enumerate(self._calls):
            if c.call_id == call_id and not c.is_settled:
                from dataclasses import replace
                settled = replace(c, status=MarginCallStatus.SETTLED)
                self._calls[i] = settled
                return settled
        return None

    def calls_for_date(self, date: str) -> list[MarginCallEvent]:
        return [c for c in self._calls if c.call_date == date]

    def outstanding_calls(self) -> list[MarginCallEvent]:
        return [c for c in self._calls if not c.is_settled and c.status != MarginCallStatus.DEFAULTED]

    def total_outstanding_gbp(self) -> float:
        return round(sum(c.total_margin_required_gbp for c in self.outstanding_calls()), 2)

    def headroom_gbp(self) -> float:
        return round(self.credit_facility_gbp - self.total_outstanding_gbp(), 2)

    def is_liquidity_stressed(self) -> bool:
        return self.total_outstanding_gbp() > self.credit_facility_gbp * 0.8

    def stress_events(self) -> list[MarginCallEvent]:
        return [c for c in self._calls if c.is_stress_event]

    def margin_call_summary(self) -> dict:
        outstanding = self.outstanding_calls()
        return {
            "total_calls": len(self._calls),
            "outstanding_calls": len(outstanding),
            "total_outstanding_gbp": self.total_outstanding_gbp(),
            "credit_facility_gbp": self.credit_facility_gbp,
            "headroom_gbp": self.headroom_gbp(),
            "is_liquidity_stressed": self.is_liquidity_stressed(),
            "stress_events": len(self.stress_events()),
        }


# --- VALUE_CHAIN observation feed: variation margin from netted MtM (2026-07-24) ---
# Under an ISDA Credit Support Annex, whichever party's netted position is out-of-the-money
# posts variation margin to cover the other's replacement-cost exposure. So a counterparty
# whose netted MtM has moved AGAINST the company (netted_mtm < 0 -> the company owes) draws a
# variation-margin call on the company's OWN credit facility -- the liquidity leg this book
# tracks (outstanding, headroom, stress). This is the sign-complement of
# WholesaleCreditExposureRegister, which tracks the other side (the company is owed, credit
# exposure to the counterparty). Both are populated from the same netted-MtM snapshot.
def build_margin_calls_from_mtm(
    exposure_by_counterparty: dict,
    *,
    as_of_date: str,
    settlement_deadline: str,
    credit_facility_gbp: float = 5_000_000.0,
    book: "MarginCallBook | None" = None,
) -> "MarginCallBook":
    """Derive the variation-margin calls the company must POST from ISDA-netted MtM.

    Input is the exact output of
    ``company.trading.forward_book.TradingBook.exposure_by_counterparty(prices)`` --
    per-counterparty SIGNED ``netted_mtm_gbp`` at a point-in-time observable forward-price
    snapshot.

    PURE + deterministic (C-S2): the same snapshot reproduces identical calls; no RNG, no
    clock read (both dates are passed in from the run loop's own observable state). Wall-clean:
    every input is the company's OWN netted MtM marked at OBSERVABLE prices -- no simulation
    internal.

    C-S1 (single/late/out-of-order arrival tolerated): each call is keyed by a deterministic
    ``call_id`` (``VM-<counterparty>-<as_of_date>``); feeding the same snapshot twice is
    idempotent -- a ``call_id`` already present is skipped, not double-counted. Pass ``book`` to
    accumulate across sample points; omit it for a fresh book.

    NAMED SIMPLIFICATION (R10): variation margin at a single mark = the amount by which the
    company is out-of-the-money, ``max(0, -netted_mtm)`` (the CSA collateral the OTM party must
    post). Initial margin is modelled by the credit/observation step, so it is 0 here. The
    ``UNATTRIBUTED`` bucket and rows with no counterparty identity form no call.
    """
    if book is None:
        book = MarginCallBook(credit_facility_gbp=credit_facility_gbp)
    existing = {c.call_id for c in book._calls}
    for cp_id in sorted(exposure_by_counterparty):
        if cp_id == "UNATTRIBUTED":
            continue
        entry = exposure_by_counterparty[cp_id]
        netted = float(entry.get("netted_mtm_gbp", 0.0))
        variation_margin = round(max(0.0, -netted), 2)
        if variation_margin <= 0.0:
            continue  # company is in-the-money (or flat) with this name -> it owes no margin
        call_id = f"VM-{cp_id}-{as_of_date}"
        if call_id in existing:
            continue  # C-S1 idempotency: this name's call for this snapshot already recorded
        book.record_call(
            MarginCallEvent(
                call_id=call_id,
                call_date=as_of_date,
                counterparty=cp_id,
                contract_id=f"NETTED-{cp_id}",  # netted position, not a single contract
                initial_margin_gbp=0.0,
                variation_margin_gbp=variation_margin,
                settlement_deadline=settlement_deadline,
            )
        )
        existing.add(call_id)
    return book
