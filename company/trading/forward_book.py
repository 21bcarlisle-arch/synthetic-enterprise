"""Company Trading Desk — Forward Position Lifecycle (Phase 43a).

The company's trading book tracks electricity forward contracts opened at tariff
signing. This is the first full SIM/company separation for hedging: the SIM no
longer decides what hedge fraction to apply — the company's trading desk does,
and the SIM settles against the company's actual positions.

Epistemic constraint: every decision here uses only company-observable data
(company forward price, portfolio exposure, own P&L records, observable spot prices).
No simulation internals are accessed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import NamedTuple, Optional

from company.trading.wholesale_credit_exposure import (
    ClearingStatus,
    CounterpartyCreditRating,
    CounterpartyType,
)


@dataclass(frozen=True)
class ForwardContract:
    """A single OTC forward contract opened at supply term signing.

    agreed_price_gbp_per_mwh: the company forward price at the time the tariff
        was priced (observable: from company's own tariff engine, which uses
        published forward market data only).
    notional_mwh: hedged volume — EAC × hedge_fraction / 1000.
    bid_ask_cost_gbp: total execution cost paid at signing (bid-ask spread × notional).
        Defaults to 0.0 for backward compatibility.

    VALUE_CHAIN step 1 — counterparty attribution (2026-07-24). A forward hedge is
    executed WITH someone, and the credit/collateral mechanics differ structurally by
    who and how the trade clears (grounded in
    docs/market_research/uk_supplier_hedge_counterparty_distribution_2026-07-24.md):
      - counterparty_type / clearing_status reuse the wholesale credit register's own
        taxonomy so this attribution feeds WholesaleCreditExposureRegister directly.
      - counterparty_rating is a PUBLISHED agency rating band — wall-safe (a real
        supplier reads S&P/Moody's/Fitch headline grades; RQ4). The counterparty's TRUE
        default probability stays sim-internal, inferred from observed settle/dispute
        history, never read here.
      - broker_arranged is a pass-through label only (RQ1): a broker intermediates but
        is not the credit counterparty — the bilateral name it matched carries the risk.
    All fields default to None/False for backward compatibility; assign_default_counterparty()
    supplies a deterministic, reproducible default distribution (R10 simplification — the
    ~50/50 cleared/bilateral split is inferred-best-estimate, NOT an Ofgem/CMA-sourced
    figure; no public supplier-level split exists, RQ2).
    """

    customer_id: str
    term_start: str          # ISO date string
    term_end: str            # ISO date string
    notional_mwh: float
    agreed_price_gbp_per_mwh: float
    hedge_fraction: float
    bid_ask_cost_gbp: float = 0.0  # Phase 43b: execution cost of hedging
    # VALUE_CHAIN step 1: counterparty attribution (all defaulted → backward-compatible).
    counterparty_id: Optional[str] = None
    counterparty_type: Optional[CounterpartyType] = None
    clearing_status: Optional[ClearingStatus] = None
    counterparty_rating: Optional[CounterpartyCreditRating] = None
    broker_arranged: bool = False

    @property
    def is_cleared(self) -> bool:
        """CCP-cleared: credit risk sits with the clearing house, not a named counterparty."""
        return self.clearing_status == ClearingStatus.CLEARED_CCP

    @property
    def is_bilateral(self) -> bool:
        """Bilateral OTC (ISDA/CSA): the named counterparty carries full credit risk."""
        return self.clearing_status == ClearingStatus.BILATERAL_ISDA


class CounterpartyAttribution(NamedTuple):
    """The counterparty fields assigned to a forward contract at signing."""
    counterparty_id: str
    counterparty_type: CounterpartyType
    clearing_status: ClearingStatus
    counterparty_rating: Optional[CounterpartyCreditRating]  # None for CCP (no per-name limit)
    broker_arranged: bool


# --- VALUE_CHAIN step 1: default counterparty distribution (R10 simplification) ---
# Grounded default from the DISCOVER pass (uk_supplier_hedge_counterparty_distribution_2026-07-24.md,
# "Modelling recommendation"): ~50% CCP-cleared / ~50% bilateral, the bilateral half weighted toward
# bank+trader for standard tenors and generator for shaped/PPA volume. Absent a public supplier-level
# split (RQ2 ungrounded-gap), this is an inferred-best-estimate, flagged for external cross-check —
# NOT a sourced figure. Concentration: a small active bilateral pool per type (real ISDA-onboarding
# cost → suppliers concentrate rather than spread thin, RQ2).
_CHANNEL_BANDS = [
    # (upper_exclusive_bucket, counterparty_type, clearing_status, rating, pool_prefix, pool_size)
    (50, CounterpartyType.CLEARING_HOUSE, ClearingStatus.CLEARED_CCP, None, "ICE_CLEAR_EUROPE", 1),
    (70, CounterpartyType.MAJOR_BANK, ClearingStatus.BILATERAL_ISDA, CounterpartyCreditRating.AA, "BANK", 4),
    (90, CounterpartyType.ENERGY_TRADER, ClearingStatus.BILATERAL_ISDA, CounterpartyCreditRating.A, "TRADER", 4),
    (100, CounterpartyType.GENERATOR, ClearingStatus.BILATERAL_ISDA, CounterpartyCreditRating.BBB, "GENERATOR", 3),
]


def assign_default_counterparty(
    customer_id: str, term_start: str, notional_mwh: float
) -> CounterpartyAttribution:
    """Deterministically assign a default counterparty to a forward contract.

    Deterministic and process-independent (uses hashlib, NOT the salted builtin hash(),
    so a replay reproduces identical attribution — C-S2 deterministic replay). The draw
    stands in for the trade-execution desk pending a real execution model, and is an R10
    named simplification (see _CHANNEL_BANDS). Inputs are all company-observable contract
    attributes — no simulation internal is read (epistemic wall).
    """
    h = hashlib.sha256(f"{customer_id}|{term_start}|{notional_mwh}".encode()).hexdigest()
    channel_bucket = int(h[0:8], 16) % 100
    pool_bucket = int(h[8:16], 16)
    broker_bucket = int(h[16:24], 16) % 10
    for upper, cp_type, clearing, rating, prefix, pool_size in _CHANNEL_BANDS:
        if channel_bucket < upper:
            if clearing == ClearingStatus.CLEARED_CCP:
                return CounterpartyAttribution(
                    counterparty_id=prefix,
                    counterparty_type=cp_type,
                    clearing_status=clearing,
                    counterparty_rating=rating,
                    broker_arranged=False,  # a CCP trade is never broker-intermediated as a credit name
                )
            pool_idx = pool_bucket % pool_size
            return CounterpartyAttribution(
                counterparty_id=f"{prefix}-{pool_idx + 1}",
                counterparty_type=cp_type,
                clearing_status=clearing,
                counterparty_rating=rating,
                broker_arranged=(broker_bucket < 3),  # ~30% of bilateral trades broker-arranged (RQ1 flag)
            )
    raise AssertionError("channel_bucket out of range")  # pragma: no cover — bands cover 0..99


class HedgePnL(NamedTuple):
    hedged_mwh: float
    pnl_gbp: float           # positive = hedge won (forward > spot), negative = hedge lost


@dataclass(frozen=True)
class HedgeAmendment:
    customer_id: str
    term_start: str
    amendment_date: str
    old_hedge_fraction: float
    new_hedge_fraction: float
    reason: str = ""


@dataclass(frozen=True)
class PositionClosure:
    customer_id: str
    term_start: str
    close_date: str
    close_price_gbp_per_mwh: float
    realised_pnl_gbp: float




class TradingBook:
    """Tracks all open forward contracts and cumulative P&L.

    Used in run_phase2b.py: one TradingBook instance per full simulation run,
    shared across all customers and years.
    """

    def __init__(self) -> None:
        self._contracts: list[ForwardContract] = []
        self._total_pnl_gbp: float = 0.0
        self._total_hedged_mwh: float = 0.0
        self._total_bid_ask_cost_gbp: float = 0.0
        self._closed_keys: set[tuple[str, str]] = set()
        self._amendments: list[HedgeAmendment] = []
        self._closures: list[PositionClosure] = []
        self._hedge_overrides: dict[tuple[str, str], float] = {}

    def open_hedge(self, contract: ForwardContract) -> None:
        """Register a new forward contract when a supply term is signed."""
        self._contracts.append(contract)
        self._total_bid_ask_cost_gbp += contract.bid_ask_cost_gbp

    def settle_period(
        self,
        customer_id: str,
        term_start: str,
        consumed_kwh: float,
        actual_spot_gbp_per_mwh: float,
    ) -> HedgePnL:
        """Compute hedge P&L for one settlement period within an active term.

        For the matching contract: hedged_mwh = consumed × hedge_fraction / 1000.
        pnl = (agreed_price − actual_spot) × hedged_mwh.
        Positive when the forward price (what the company locked in) is above spot —
        i.e. the company paid over the odds on the hedge but covered its supply risk.

        Returns HedgePnL(0, 0) if no matching contract found (e.g. deemed/flex terms
        which have no locked forward price).
        """
        for c in self._contracts:
            if c.customer_id == customer_id and c.term_start == term_start:
                hedged_mwh = (consumed_kwh / 1000.0) * c.hedge_fraction
                pnl = (c.agreed_price_gbp_per_mwh - actual_spot_gbp_per_mwh) * hedged_mwh
                self._total_pnl_gbp += pnl
                self._total_hedged_mwh += hedged_mwh
                return HedgePnL(hedged_mwh=hedged_mwh, pnl_gbp=pnl)
        return HedgePnL(hedged_mwh=0.0, pnl_gbp=0.0)

    @property
    def total_pnl_gbp(self) -> float:
        return self._total_pnl_gbp

    @property
    def total_hedged_mwh(self) -> float:
        return self._total_hedged_mwh

    @property
    def total_bid_ask_cost_gbp(self) -> float:
        return self._total_bid_ask_cost_gbp

    @property
    def contract_count(self) -> int:
        return len(self._contracts)

    def open_contracts(self) -> list[ForwardContract]:
        return [c for c in self._contracts
                if (c.customer_id, c.term_start) not in self._closed_keys]

    def closed_contracts(self) -> list[ForwardContract]:
        return [c for c in self._contracts
                if (c.customer_id, c.term_start) in self._closed_keys]


    def amend_hedge(
        self,
        customer_id: str,
        term_start: str,
        new_hedge_fraction: float,
        amendment_date: str,
        reason: str = '',
    ) -> HedgeAmendment:
        key = (customer_id, term_start)
        old_fraction = self._hedge_overrides.get(key)
        if old_fraction is None:
            for c in self._contracts:
                if c.customer_id == customer_id and c.term_start == term_start:
                    old_fraction = c.hedge_fraction
                    break
        amendment = HedgeAmendment(
            customer_id=customer_id,
            term_start=term_start,
            amendment_date=amendment_date,
            old_hedge_fraction=old_fraction or 0.0,
            new_hedge_fraction=new_hedge_fraction,
            reason=reason,
        )
        self._amendments.append(amendment)
        self._hedge_overrides[key] = new_hedge_fraction
        return amendment

    def close_position(
        self,
        customer_id: str,
        term_start: str,
        close_date: str,
        close_price_gbp_per_mwh: float,
    ) -> PositionClosure:
        notional = 0.0
        agreed = 0.0
        for c in self._contracts:
            if c.customer_id == customer_id and c.term_start == term_start:
                notional = c.notional_mwh
                agreed = c.agreed_price_gbp_per_mwh
                break
        realised_pnl = round((close_price_gbp_per_mwh - agreed) * notional, 2)
        closure = PositionClosure(
            customer_id=customer_id,
            term_start=term_start,
            close_date=close_date,
            close_price_gbp_per_mwh=close_price_gbp_per_mwh,
            realised_pnl_gbp=realised_pnl,
        )
        self._closures.append(closure)
        self._closed_keys.add((customer_id, term_start))
        return closure

    def amendments(self) -> list[HedgeAmendment]:
        return list(self._amendments)

    def closures(self) -> list[PositionClosure]:
        return list(self._closures)

    def mark_to_market(self, contract: ForwardContract, current_price_gbp_per_mwh: float) -> dict:
        """MTM value of one contract at current market price.

        MTM P&L = (current_market_price - agreed_price) x notional_mwh.
        Positive = contract in-the-money (locked in below current market).
        Negative = contract out-of-the-money (locked in above current market).
        """
        mtm_pnl = (current_price_gbp_per_mwh - contract.agreed_price_gbp_per_mwh) * contract.notional_mwh
        return {
            "customer_id": contract.customer_id,
            "term_start": contract.term_start,
            "notional_mwh": round(contract.notional_mwh, 3),
            "agreed_price": round(contract.agreed_price_gbp_per_mwh, 4),
            "market_price": round(current_price_gbp_per_mwh, 4),
            "mtm_pnl_gbp": round(mtm_pnl, 2),
            "in_the_money": mtm_pnl > 0,
        }

    def portfolio_mtm(self, current_prices: dict[str, float]) -> dict:
        """Portfolio-level MTM valuation.

        current_prices: {customer_id: current_forward_price_gbp_per_mwh}
        Uses the contract's customer_id to look up the current price.
        Returns {total_mtm_pnl_gbp, positions_in_the_money, positions_out_of_money, positions}.
        """
        positions = []
        total = 0.0
        in_money = 0
        out_money = 0
        for c in self.open_contracts():
            price = current_prices.get(c.customer_id)
            if price is None:
                continue
            pos = self.mark_to_market(c, price)
            positions.append(pos)
            total += pos["mtm_pnl_gbp"]
            if pos["in_the_money"]:
                in_money += 1
            else:
                out_money += 1
        return {
            "total_mtm_pnl_gbp": round(total, 2),
            "positions_priced": len(positions),
            "positions_in_the_money": in_money,
            "positions_out_of_money": out_money,
            "positions": positions,
        }

    def exposure_by_counterparty(self, current_prices: dict[str, float]) -> dict:
        """ISDA-netted mark-to-market credit exposure per counterparty.

        VALUE_CHAIN step 1 output — the consumable feed for
        WholesaleCreditExposureRegister (gross_credit_exposure_gbp maps to that record's
        gross_mtm_gbp). Under ISDA netting all trades with the same counterparty net
        BEFORE credit exposure is taken (see wholesale_credit_exposure.py header): so per
        counterparty we sum SIGNED MtM, then credit exposure = max(0, netted) — only an
        in-the-money net position means the counterparty owes the company (replacement
        cost if it defaults now). Out-of-the-money nets to zero exposure (the company owes).

        current_prices: {customer_id: current_forward_price_gbp_per_mwh}.
        Contracts with no counterparty attribution net under the "UNATTRIBUTED" key.
        """
        agg: dict[str, dict] = {}
        for c in self.open_contracts():
            price = current_prices.get(c.customer_id)
            if price is None:
                continue
            cp_id = c.counterparty_id or "UNATTRIBUTED"
            pos = self.mark_to_market(c, price)
            entry = agg.get(cp_id)
            if entry is None:
                entry = {
                    "counterparty_id": cp_id,
                    "counterparty_type": c.counterparty_type.value if c.counterparty_type else None,
                    "clearing_status": c.clearing_status.value if c.clearing_status else None,
                    "counterparty_rating": c.counterparty_rating.value if c.counterparty_rating else None,
                    "netted_mtm_gbp": 0.0,
                    "position_count": 0,
                    "broker_arranged_count": 0,
                }
                agg[cp_id] = entry
            entry["netted_mtm_gbp"] += pos["mtm_pnl_gbp"]
            entry["position_count"] += 1
            if c.broker_arranged:
                entry["broker_arranged_count"] += 1
        for entry in agg.values():
            entry["netted_mtm_gbp"] = round(entry["netted_mtm_gbp"], 2)
            entry["gross_credit_exposure_gbp"] = round(max(0.0, entry["netted_mtm_gbp"]), 2)
        return agg

    def summary(self) -> dict:
        return {
            "contract_count": self.contract_count,
            "total_hedged_mwh": round(self._total_hedged_mwh, 3),
            "total_hedge_pnl_gbp": round(self._total_pnl_gbp, 2),
            "total_bid_ask_cost_gbp": round(self._total_bid_ask_cost_gbp, 2),
        }
