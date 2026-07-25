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


# --- MC-2 §3: the committed trading facility SCALES WITH THE BOOK (2026-07-25) ---
# DIRECTOR RULING (DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY_2026-07-25.md §3): a hardcoded
# £5m liquidity facility standing against ANY book is a DEFECT, not a difficulty setting. At the
# activated N=200 book it is orders of magnitude too large — nothing can kill it, so the MC-2
# death-by-collateral test would be theatre. A real supplier's committed trading facility (bank RCF
# + broker/exchange credit lines) is sized to its book: it covers a plausible peak variation-margin
# posting on the hedge book it actually holds, so a bigger book earns a bigger facility.
#
# MECHANISM (observable, book-derived, wall-clean): the facility is a coverage multiple of the
# book's OWN gross marked exposure — the two-way magnitude of its netted MtM across counterparties,
# the size of the position it must collateralise — at the point the facility is committed
# (origination/first construction), floored at a minimum committed facility. Every input is the
# company's own netted MtM at OBSERVABLE forward prices (the same snapshot the margin feed already
# consumes) — no simulation internal, no future data. It is set ONCE at construction and held: a
# later, more adverse mark is called against this FIXED facility, so a large enough price move
# produces death-by-collateral while the P&L may still survive (the exact 2021–22 shape MC-2 tests).
#
# NAMED SIMPLIFICATION (R10) — NOT a difficulty dial (MC-2 §3 / R12): FACILITY_COVERAGE_MULTIPLE and
# FACILITY_MIN_GBP are sizing parameters pending a real external anchor (published UK-supplier
# RCF-to-book ratios — registered as forward-discovery). They are set to a plausible operational
# default and MUST NOT be tuned in either direction to change the MC-2 outcome: shrinking the
# facility to force a death is the same R12 breach as inflating a multiplier. If the company
# survives the whole breaking-strain sweep, DIAGNOSE the mechanism (R4, MC-2 §4) — never shrink the
# facility. FACILITY_MIN_GBP is deliberately modest (a real supplier holds SOME committed RCF
# regardless of book size) and must stay well below a plausible stress call so it cannot by itself
# make a stressed book unbreakable.
FACILITY_COVERAGE_MULTIPLE = 1.5   # committed headroom above the book's gross marked exposure at origination
FACILITY_MIN_GBP = 250_000.0       # minimum committed operational facility (never zero -> never insta-dead)


def book_scaled_credit_facility_gbp(exposure_by_counterparty: dict) -> float:
    """The committed trading facility, sized to the book's own gross marked exposure.

    ``exposure_by_counterparty`` is the exact output of
    ``company.trading.forward_book.TradingBook.exposure_by_counterparty(prices)`` — per-counterparty
    signed ``netted_mtm_gbp``. The book-size signal is the gross two-way magnitude of that mark
    (``sum |netted_mtm|`` over attributed counterparties): it grows with the number and size of
    positions and with price dislocation, and it is exactly the exposure the facility exists to
    cover. PURE + deterministic (C-S2): same snapshot -> same facility.

    Returns ``max(FACILITY_MIN_GBP, FACILITY_COVERAGE_MULTIPLE × gross_marked_exposure)``. The floor
    guarantees a non-zero facility (a book with no marked exposure is not instantly dead); above it
    the facility scales linearly with the book, so the fixed-£5m defect is gone.
    """
    gross = 0.0
    for cp_id, entry in exposure_by_counterparty.items():
        if cp_id == "UNATTRIBUTED":
            continue
        gross += abs(float(entry.get("netted_mtm_gbp", 0.0)))
    return round(max(FACILITY_MIN_GBP, FACILITY_COVERAGE_MULTIPLE * gross), 2)


class MarginCallBook:
    # NOTE (MC-2 §3): the class-level 5m default is retained ONLY as a bare-constructor fallback for
    # unit tests that build a book with no book context. The LIVE facility is always book-derived via
    # build_margin_calls_from_mtm -> book_scaled_credit_facility_gbp; it is never 5m in a real run.
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
    credit_facility_gbp: "float | None" = None,
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
        # MC-2 §3: the committed facility is book-derived by default (the fixed-£5m defect is gone).
        # An explicit credit_facility_gbp is honoured only where a caller sets one deliberately
        # (unit tests, or a sweep pinning the origination facility); otherwise it scales with the
        # book's own gross marked exposure at this origination snapshot.
        if credit_facility_gbp is None:
            credit_facility_gbp = book_scaled_credit_facility_gbp(exposure_by_counterparty)
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
