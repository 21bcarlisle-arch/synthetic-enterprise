"""Wholesale Credit Exposure Register (Phase DY).

When an energy supplier buys forward contracts, it is exposed to counterparty
credit risk: if the counterparty (bank, generator, trader) defaults before
delivery, the supplier loses the mark-to-market value of those contracts.

Key concepts for UK wholesale energy markets:
- ISDA Master Agreement + CSA (Credit Support Annex): governs collateral
- Initial Margin: posted upfront, returned at contract close
- Variation Margin: marked-to-market daily; call if MtM goes against you
- Netting: ISDA netting means all trades with same counterparty netted before
  calculating credit exposure
- Credit Limit: board-approved maximum exposure per counterparty
- Mark-to-market (MtM): current replacement cost if counterparty defaults now

UK-specific: ICE Endex OTC clearing (cleared through LCH); bilateral OTC
trades have no CCP backing — higher credit risk. Clearing mandated under
EMIR for standardised contracts.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional


class CounterpartyType(str, Enum):
    MAJOR_BANK = "major_bank"
    ENERGY_TRADER = "energy_trader"
    GENERATOR = "generator"
    CLEARING_HOUSE = "clearing_house"
    AGGREGATOR = "aggregator"


class ClearingStatus(str, Enum):
    CLEARED_CCP = "cleared_ccp"        # CCP-cleared; lower credit risk
    BILATERAL_ISDA = "bilateral_isda"  # OTC bilateral
    UNCONFIRMED = "unconfirmed"


class CounterpartyCreditRating(str, Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB_OR_LOWER = "BB_or_lower"
    UNRATED = "unrated"


_CREDIT_LIMIT_BY_RATING: Dict[CounterpartyCreditRating, float] = {
    CounterpartyCreditRating.AAA: 5_000_000.0,
    CounterpartyCreditRating.AA: 3_000_000.0,
    CounterpartyCreditRating.A: 2_000_000.0,
    CounterpartyCreditRating.BBB: 1_000_000.0,
    CounterpartyCreditRating.BB_OR_LOWER: 250_000.0,
    CounterpartyCreditRating.UNRATED: 100_000.0,
}

_CLEARED_EXPOSURE_HAIRCUT = 0.10     # CCP-cleared: 10% of MtM counts (collateral covers most)


# --- VALUE_CHAIN BUILD ladder step 3: the observation-window cap (2026-07-24) ---
# The declared FAIL (PRIORITIES.md PRODUCT-FIRST item 3, verbatim): the credit cap was a
# *static dict* — a fixed rating-band number a 20-year veteran reads as a tell that the
# collateral mechanics are cosmetic (Axis 3 believability). Real credit control does not stop
# at the rating band: a line is TIGHTENED when a counterparty's OWN observed conduct on the
# margin calls it exchanges with the company deteriorates (disputes, then defaults). This is
# the observation-window mechanism — the cap is a rating-anchored PRIOR eroded by the company's
# OWN observed settle/dispute record over the window.
#
# WALL: the erosion signal is the company's own record of how its counterparties honoured the
# margin calls it exchanged with them (MarginCallStatus transitions it observes first-hand) and
# the PUBLIC agency rating band — both company-side observables, never a simulation internal
# (never the counterparty's TRUE default probability, which stays behind the wall). Confirmed by
# tools.epistemic_verifier on the diff.
#
# NAMED SIMPLIFICATION (R10), deliberately one-directional: observed conduct can only ERODE the
# rating-anchored prior, never EARN a line ABOVE the rating band. A real board does not lift a
# rating-based limit merely because a name has paid cleanly — the rating is the ceiling; observed
# misconduct only tightens. Modelling an earn-up above the band is left as a named follow-on, not
# asserted here.
#
# BENIGN DEFAULT (the doc's authorised scope — "mint the mechanism + a benign default"): with NO
# observed conduct over the window the multiplier is exactly 1.0, so the cap equals the rating
# prior and every existing consumer is unchanged. This is HONEST, not cosmetic: a counterparty
# with no adverse history rightly retains its full rating-based line. The LIVE settlement-history
# feed (a multi-period exposure sample + a margin-call settle/dispute RESOLUTION mechanic — both
# verified absent from the run loop today) is the named next drawable step; until it lands the
# mechanism is live and proven but dormant, and this file does NOT claim the live cap moves yet.
_WINDOW_LIMIT_FLOOR_FRACTION = 0.25   # observed misconduct can cut a line to at most 1/4 of the rating prior
_DISPUTE_WEIGHT = 0.5                  # a disputed call is a soft adverse signal
_DEFAULT_WEIGHT = 1.0                  # a defaulted call is the maximal adverse signal


@dataclass(frozen=True)
class ObservedCounterpartyBehaviour:
    """The company's OWN observed record of a counterparty's margin-call conduct over the
    observation window — a through-the-wall observable. The company sees first-hand whether the
    margin calls it exchanged with a counterparty were SETTLED, DISPUTED, or DEFAULTED
    (``MarginCallStatus`` transitions on its own book); it never reads the counterparty's true
    default probability. Counts, so it accumulates idempotently across sample points (C-S2)."""

    n_settled: int = 0
    n_disputed: int = 0
    n_defaulted: int = 0

    @property
    def n_observed(self) -> int:
        return self.n_settled + self.n_disputed + self.n_defaulted

    @property
    def adverse_score(self) -> float:
        """Weighted fraction of observed conduct that was adverse, in [0, 1]. Zero when nothing
        has been observed (the benign default) or when every observed call settled cleanly."""
        if self.n_observed == 0:
            return 0.0
        weighted = _DISPUTE_WEIGHT * self.n_disputed + _DEFAULT_WEIGHT * self.n_defaulted
        return min(1.0, weighted / self.n_observed)


def observation_window_credit_limit(
    rating: CounterpartyCreditRating,
    behaviour: Optional[ObservedCounterpartyBehaviour] = None,
    *,
    rating_prior: Optional[float] = None,
) -> float:
    """The observation-window credit cap: the rating-anchored prior eroded by observed conduct.

    ``rating_prior`` defaults to ``_CREDIT_LIMIT_BY_RATING[rating]``. With no observed conduct
    (``behaviour is None`` or ``n_observed == 0``) the prior stands unchanged — the benign
    default. As observed disputes/defaults accumulate, the cap erodes monotonically toward
    ``_WINDOW_LIMIT_FLOOR_FRACTION`` of the prior (an all-defaulted history). One-directional by
    design (see module note): observed conduct never earns a line above the rating band.
    """
    base = rating_prior if rating_prior is not None else _CREDIT_LIMIT_BY_RATING[rating]
    if behaviour is None or behaviour.n_observed == 0:
        return base
    multiplier = 1.0 - (1.0 - _WINDOW_LIMIT_FLOOR_FRACTION) * behaviour.adverse_score
    return round(base * multiplier, 2)


# --- VALUE_CHAIN BUILD ladder step 3, prerequisite 1: the RESOLUTION-observation seam ---
# (2026-07-24). The observation-window cap above is LIVE but DORMANT: nothing yet feeds an
# ObservedCounterpartyBehaviour with adverse conduct, so on a real run the cap equals the rating
# prior. This is the COMPANY-SIDE CONSUMER CONTRACT that closes that gap — the typed seam a
# resolution stream plugs into.
#
# WALL PLACEMENT (Tier-1, decisive — this seam exists to make it un-crossable):
#   * The adverse signal the cap needs is a COUNTERPARTY's conduct on margin the counterparty
#     OWES the company (the owed-to-us / credit-exposure leg this register tracks) — NOT the
#     company's own conduct on margin the company owes (the liquidity leg tracked by
#     company.finance.margin_call_book.build_margin_calls_from_mtm, the sign-complement). Folding
#     the company-owes calls into this cap would erode a counterparty's line on the COMPANY's own
#     (dis)honour — a semantics inversion. This seam only accepts counterparty-attributed
#     resolutions, so that inversion cannot be wired by accident.
#   * WHETHER a counterparty settles / disputes / defaults is a WORLD property (its true default
#     propensity lives behind the wall). The company may only OBSERVE the outcome (did the cash
#     arrive, was the amount contested). So this function AGGREGATES observed outcomes; it never
#     DECIDES them. In the coupled triad the producer is a WORLD counterparty-behaviour model the
#     company observes through settlement outcomes — authored as its own atom, gated on its own
#     side of the wall. Building the consumer contract first (typed-flow-seam preference) fixes the
#     wall-correct shape before the producer exists; it is a contract, not a board-surfaced empty
#     organ, so it is not the "organ with no blood" the DON'T-ACCRETE rule forbids.
class MarginResolution(str, Enum):
    """The OBSERVED terminal outcome of a margin call a counterparty owed the company: it paid
    (SETTLED), contested the amount (DISPUTED — a soft adverse signal), or failed to pay
    (DEFAULTED — the maximal adverse signal). An observable on the company's own book, never the
    counterparty's hidden default propensity."""

    SETTLED = "settled"
    DISPUTED = "disputed"
    DEFAULTED = "defaulted"


@dataclass(frozen=True)
class CounterpartyResolutionOutcome:
    """A single observed, counterparty-attributed margin-call resolution. ``call_id`` is the
    resolved call's stable id — the dedup key that makes the fold idempotent under an
    at-least-once feed (C-S2). One TERMINAL resolution per ``call_id`` is the producer's
    contract; an escalation (dispute→default) is emitted by the producer as the terminal
    DEFAULTED, not modelled here."""

    call_id: str
    counterparty_id: str
    resolution: MarginResolution


def observed_behaviour_from_resolutions(
    outcomes: Iterable[CounterpartyResolutionOutcome],
) -> Dict[str, ObservedCounterpartyBehaviour]:
    """Fold a stream of OBSERVED counterparty margin-call resolutions into the per-counterparty
    ``ObservedCounterpartyBehaviour`` the observation-window cap consumes.

    Order-invariant (C-S1: single / late / out-of-order arrival tolerated — counts do not depend
    on sequence) and idempotent by ``call_id`` (C-S2: the same terminal resolution delivered twice
    is harmless, not double-counted). Deterministic and pure: no clock, no RNG, no I/O — replaying
    the same set reproduces identical counts. A ``call_id`` re-seen with a DIFFERENT resolution is
    a producer contract breach; first-seen wins, deterministically (the producer owns terminality).
    """
    tally: Dict[str, Dict[str, int]] = {}
    seen_call_ids: set[str] = set()
    for o in outcomes:
        if o.call_id in seen_call_ids:
            continue  # C-S2: duplicate delivery of an already-observed call is idempotent
        seen_call_ids.add(o.call_id)
        counts = tally.setdefault(
            o.counterparty_id, {"settled": 0, "disputed": 0, "defaulted": 0}
        )
        counts[o.resolution.value] += 1
    return {
        cp_id: ObservedCounterpartyBehaviour(
            n_settled=c["settled"], n_disputed=c["disputed"], n_defaulted=c["defaulted"]
        )
        for cp_id, c in tally.items()
    }


@dataclass(frozen=True)
class WholesaleCreditRecord:
    counterparty_id: str
    counterparty_type: CounterpartyType
    credit_rating: CounterpartyCreditRating
    clearing_status: ClearingStatus
    gross_mtm_gbp: float
    collateral_held_gbp: float
    credit_limit_override_gbp: Optional[float] = None
    # Observation-window signal: the company's OWN observed margin-call conduct for this name over
    # the window. Absent (None) → the rating-anchored prior stands (benign default, backward-
    # compatible). Present with adverse conduct → the cap erodes via observation_window_credit_limit.
    observed_behaviour: Optional[ObservedCounterpartyBehaviour] = None

    @property
    def net_exposure_gbp(self) -> float:
        raw = self.gross_mtm_gbp - self.collateral_held_gbp
        if self.clearing_status == ClearingStatus.CLEARED_CCP:
            raw *= _CLEARED_EXPOSURE_HAIRCUT
        return max(0.0, raw)

    @property
    def credit_limit_gbp(self) -> float:
        if self.credit_limit_override_gbp is not None:
            return self.credit_limit_override_gbp
        # Observation-window cap: rating-anchored prior eroded by observed conduct. With no
        # observed_behaviour this equals the static rating prior (benign default), so an override
        # (e.g. CCP no-per-name-limit) and every prior consumer are unchanged.
        return observation_window_credit_limit(self.credit_rating, self.observed_behaviour)

    @property
    def utilisation_pct(self) -> float:
        if self.credit_limit_gbp <= 0:
            return 0.0
        return self.net_exposure_gbp / self.credit_limit_gbp * 100

    @property
    def is_limit_breached(self) -> bool:
        return self.net_exposure_gbp > self.credit_limit_gbp

    @property
    def headroom_gbp(self) -> float:
        return max(0.0, self.credit_limit_gbp - self.net_exposure_gbp)


class WholesaleCreditExposureRegister:
    """Board-level view of all wholesale counterparty credit exposures."""

    def __init__(self) -> None:
        self._records: Dict[str, WholesaleCreditRecord] = {}

    def register(self, record: WholesaleCreditRecord) -> WholesaleCreditRecord:
        self._records[record.counterparty_id] = record
        return record

    def get(self, counterparty_id: str) -> Optional[WholesaleCreditRecord]:
        return self._records.get(counterparty_id)

    def all_records(self) -> List[WholesaleCreditRecord]:
        return list(self._records.values())

    def limit_breaches(self) -> List[WholesaleCreditRecord]:
        return [r for r in self._records.values() if r.is_limit_breached]

    def cleared_records(self) -> List[WholesaleCreditRecord]:
        return [r for r in self._records.values()
                if r.clearing_status == ClearingStatus.CLEARED_CCP]

    def bilateral_records(self) -> List[WholesaleCreditRecord]:
        return [r for r in self._records.values()
                if r.clearing_status == ClearingStatus.BILATERAL_ISDA]

    def total_net_exposure_gbp(self) -> float:
        return sum(r.net_exposure_gbp for r in self._records.values())

    def total_collateral_held_gbp(self) -> float:
        return sum(r.collateral_held_gbp for r in self._records.values())

    def largest_exposure(self) -> Optional[WholesaleCreditRecord]:
        if not self._records:
            return None
        return max(self._records.values(), key=lambda r: r.net_exposure_gbp)

    def credit_exposure_summary(self) -> str:
        n = len(self._records)
        n_breach = len(self.limit_breaches())
        total = self.total_net_exposure_gbp()
        collateral = self.total_collateral_held_gbp()
        return (
            f"Wholesale Credit Exposure: {n} counterparties. "
            f"Total net exposure: £{total:,.0f}. "
            f"Collateral held: £{collateral:,.0f}. "
            f"Limit breaches: {n_breach}. "
            f"ISDA/CSA governs bilateral OTC; EMIR clearing mandate."
        )


# --- VALUE_CHAIN BUILD ladder step 2: the live feed (2026-07-24) ---
# A CCP-cleared position carries no per-name credit limit — the clearing house's default
# waterfall (initial margin + default fund + skin-in-the-game) absorbs a member default,
# so a supplier does not set a bilateral-style credit line against ICE Clear Europe / LCH.
# The register still counts CCP *net* exposure (haircut by _CLEARED_EXPOSURE_HAIRCUT) but it
# can never breach a per-name limit. Expressed as a large finite override (JSON-safe, unlike
# float('inf')) rather than a rating-band cap, which would false-breach a big cleared book.
_CCP_NO_PER_NAME_LIMIT_GBP = 1e15


def build_credit_register_from_exposure(
    exposure_by_counterparty: Dict[str, dict],
) -> "WholesaleCreditExposureRegister":
    """Populate a WholesaleCreditExposureRegister from the trading book's live feed.

    VALUE_CHAIN BUILD ladder step 2 — the feed transform. Input is the exact output of
    ``company.trading.forward_book.TradingBook.exposure_by_counterparty(prices)`` (ISDA-netted
    per-counterparty MtM credit exposure at a point-in-time forward-price snapshot). This is a
    PURE transform (no I/O, no clock, deterministic) so a replay of the same exposure reproduces
    an identical register (C-S2). It is wall-clean: every input field is the company's OWN book
    (netted MtM of its own positions) or a PUBLIC agency rating band — no simulation internal.

    Mapping decisions (each an R10-flagged modelling choice, not a sourced figure):
    - ``gross_credit_exposure_gbp`` (already ``max(0, netted)`` under ISDA netting) → the record's
      ``gross_mtm_gbp``. An out-of-the-money net position (company owes) is zero credit exposure.
    - ``collateral_held_gbp`` = 0.0 here — CSA collateral/variation-margin postings are modelled by
      the observation-window step (ladder step 3), not this feed. NAMED SIMPLIFICATION: this feed
      reports GROSS-of-collateral bilateral exposure; it is an upper bound on the true net line.
    - CCP-cleared rows (``counterparty_rating is None``) get ``_CCP_NO_PER_NAME_LIMIT_GBP`` as a
      limit override (no per-name limit — the default waterfall absorbs) and a nominal AAA rating
      slot only to satisfy the required field; the override, not the rating, governs the limit.
    - The ``"UNATTRIBUTED"`` bucket (contracts opened with no counterparty — a wiring regression the
      book's ``counterparty_distribution().unattributed_count`` self-check already surfaces) is
      SKIPPED: it has no counterparty identity/rating to form a credit record from.

    Returns a freshly-built register (does not mutate any shared state).
    """
    register = WholesaleCreditExposureRegister()
    for cp_id, entry in exposure_by_counterparty.items():
        if cp_id == "UNATTRIBUTED":
            continue
        type_val = entry.get("counterparty_type")
        clearing_val = entry.get("clearing_status")
        if type_val is None or clearing_val is None:
            # No counterparty identity → not a formable credit record (same class as UNATTRIBUTED).
            continue
        counterparty_type = CounterpartyType(type_val)
        clearing_status = ClearingStatus(clearing_val)
        rating_val = entry.get("counterparty_rating")
        if rating_val is None:
            # CCP-cleared: no per-name rating/limit.
            credit_rating = CounterpartyCreditRating.AAA
            limit_override: Optional[float] = _CCP_NO_PER_NAME_LIMIT_GBP
        else:
            credit_rating = CounterpartyCreditRating(rating_val)
            limit_override = None
        register.register(
            WholesaleCreditRecord(
                counterparty_id=cp_id,
                counterparty_type=counterparty_type,
                credit_rating=credit_rating,
                clearing_status=clearing_status,
                gross_mtm_gbp=float(entry.get("gross_credit_exposure_gbp", 0.0)),
                collateral_held_gbp=0.0,
                credit_limit_override_gbp=limit_override,
            )
        )
    return register
