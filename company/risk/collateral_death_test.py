"""MC-2 collateral death-test — the breaking-strain sweep around a real price replay.

DIRECTOR RULING `DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY_2026-07-25` governs this module:

- **No difficulty knob (§1/§2).** The 1.0× point is the REAL price replay; the sweep
  0.8×/1.0×/1.2×/1.5× scales the *price move* around it and records the dose at which death
  arrives. This is a MEASUREMENT, not a curriculum world — sweep points are not ratified
  scenarios and their results are reported as breaking strain, never as EV.
- **Acceptance bar, verbatim and unrelaxed (§1).** A *price move alone* produces a cash call
  (no hand-supplied loss, no injected shock at the cash line), and at least one path shows
  *death-by-collateral while the P&L still survives* (solvent on paper, dead on cash — the
  actual 2021–22 failure shape). The second clause is the load-bearing one: this module
  distinguishes ``collateral_while_solvent`` (the target shape) from ``collateral_insolvent``
  (dead on both cash and paper — ordinary insolvency, NOT the special shape).
- **Facility is fixed at origination (§3).** The committed facility is book-derived ONCE at
  origination (`company.finance.margin_call_book.book_scaled_credit_facility_gbp`) and held
  fixed across the sweep; a later, more adverse mark is called against that fixed facility. It
  must NOT be re-derived per dose (a book that grew its own facility as it got more stressed
  could never die — that is the §3 defect).
- **§4 R12 guard.** If the company survives the whole sweep, DIAGNOSE the mechanism (R4) — do
  NOT shrink the facility or inflate a multiplier to force a death. This module reports the
  diagnosis signals (`any_name_posted_margin`, `peak_margin_call_gbp`, `facility_gbp`) so the
  R4 investigation is data-driven, never a tuning cue. In particular: a pure long hedge book
  goes IN-the-money on a price spike and posts NO variation margin, so it *cannot* die to
  collateral — ``any_name_posted_margin=False`` is exactly the "hedge cover masking the
  exposure" diagnosis §4 anticipates, not a signal to make the test harsher.

SCOPE LINE (two same-day rulings reconciled). MC-2 §2 authorises this *collateral
breaking-strain measurement*. The broader §6 survival-usefulness SCORE / growth-and-leverage
capital organ (RUN_LEDGER_AND_SCORES_BUILD_2026-07-25 §6, and the `RunOutcomes` field comment)
stays director-session gated. So this module computes only the raw measurement fields the
`RunOutcomes` ledger row already carries (``liquidity_headroom_min_gbp`` / ``collateral_cover_min``
/ ``survived`` / ``death_cause``); it builds NO blended survival score, authors NO curriculum
value, and emits NO ledger row itself (the run-loop wiring is a separate, explicit next step).

WALL. Every input is a company observable — netted MtM at observable forward prices, the
company's own committed facility and treasury cash. No simulation internal, no future data. The
1.0× marks are formed point-in-time from real spot history by the caller
(`CompanyTariffEngine.get_forward_price`); this module is agnostic to how they were formed.

C-S2. Pure + deterministic: no clock, no RNG, no I/O. The same origination/stressed exposure
reproduces an identical result.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from company.finance.margin_call_book import (
    book_scaled_credit_facility_gbp,
    build_margin_calls_from_mtm,
)

# The ruling's severity sweep around the real 1.0× replay (§2). NOT a difficulty dial: the dose
# scales the fraction of the OBSERVED price move applied, so 1.0× is the real history exactly.
DEFAULT_DOSES = (0.8, 1.0, 1.2, 1.5)


def _scale_exposure(origination: dict, stressed: dict, dose: float) -> dict:
    """Dose-scaled per-counterparty exposure: ``origination + dose·(stressed − origination)``.

    Because a forward's MtM is LINEAR in the mark price, linearly interpolating the netted MtM
    from its origination value to its stressed value is exactly marking the book at
    ``P_origination + dose·(P_stress − P_origination)`` — i.e. applying ``dose`` fraction of the
    observed price move. ``dose = 1.0`` reproduces the real stressed mark; the sweep scales the
    price MOVE around it (§2), never an injected loss.

    Counterparty attribution metadata is carried through unchanged (from the stressed entry where
    present, else origination) so downstream margin logic sees a real per-name shape.
    """
    out: dict = {}
    for key in set(origination) | set(stressed):
        o_entry = origination.get(key) or {}
        s_entry = stressed.get(key) or {}
        o_net = float(o_entry.get("netted_mtm_gbp", 0.0))
        s_net = float(s_entry.get("netted_mtm_gbp", 0.0))
        scaled = o_net + dose * (s_net - o_net)
        entry = dict(s_entry) if s_entry else dict(o_entry)
        entry["netted_mtm_gbp"] = round(scaled, 2)
        out[key] = entry
    return out


@dataclass(frozen=True)
class DoseOutcome:
    """The collateral position at one sweep dose (§2)."""

    dose: float
    total_margin_call_gbp: float   # variation margin the company must POST (its OTM names)
    facility_gbp: float            # FIXED at origination (§3)
    available_cash_gbp: float      # treasury cash the company can draw to meet a call
    net_liquidity_gbp: float       # facility + cash − margin call (headroom incl. cash)
    cover_ratio: Optional[float]   # (facility + cash) / margin call; None if no call posted
    book_pnl_gbp: float            # total netted MtM across all names (the P&L survival signal)
    is_dead_by_collateral: bool    # net_liquidity < 0 — cannot meet the call even drawing cash
    pnl_survives: bool             # book_pnl > 0 — solvent on paper
    death_while_pnl_survives: bool # the exact 2021–22 shape: dead on cash, solvent on paper


@dataclass(frozen=True)
class BreakingStrainResult:
    """The breaking-strain sweep verdict (§2) + the §4 diagnosis signals."""

    survived: bool
    death_dose: Optional[float]           # smallest dose at which collateral death arrives
    death_cause: Optional[str]            # 'collateral_while_solvent' | 'collateral_insolvent'
    death_while_pnl_survives: bool        # was the acceptance-bar shape produced ANYWHERE?
    liquidity_minimum_gbp: float          # min net liquidity over doses -> liquidity_headroom_min_gbp
    cover_minimum: Optional[float]        # min cover ratio over doses  -> collateral_cover_min
    doses: tuple                          # per-dose DoseOutcome, in sweep order
    facility_gbp: float                   # the fixed origination facility
    # --- §4 R4 diagnosis signals (data-driven; NEVER a tuning cue) ---
    price_move_alone: bool                # calls arose purely from marks, no injected loss (structural)
    any_name_posted_margin: bool          # False on a pure long book -> the §4 "hedge cover" diagnosis
    peak_margin_call_gbp: float           # largest call over the sweep, vs facility_gbp


def breaking_strain_sweep(
    origination_exposure: dict,
    stressed_exposure: dict,
    *,
    available_cash_gbp: float = 0.0,
    facility_gbp: Optional[float] = None,
    doses: tuple = DEFAULT_DOSES,
    as_of_date: str = "MC2_STRESS",
    settlement_deadline: str = "MC2_STRESS",
) -> BreakingStrainResult:
    """Run the MC-2 breaking-strain sweep around a real price replay.

    ``origination_exposure`` / ``stressed_exposure`` are the exact output shape of
    ``company.trading.forward_book.TradingBook.exposure_by_counterparty(prices)`` — a
    ``{counterparty_id: {"netted_mtm_gbp": float, ...}}`` dict — marked at the origination price
    snapshot and at the real stressed (e.g. 2021–22) price snapshot respectively. Both are formed
    point-in-time by the caller; this function reads only the observable marks.

    The facility is set ONCE from ``origination_exposure`` (§3) and held fixed across the sweep;
    pass ``facility_gbp`` only to pin it deliberately (tests, or a caller replaying a real
    committed line). Returns the dose at which death arrives, the min liquidity/cover reached, and
    the §4 diagnosis signals. A pure function — no clock, no RNG, no I/O (C-S2).
    """
    if facility_gbp is None:
        # §3: book-derived at ORIGINATION, fixed. NOT re-derived per dose.
        facility_gbp = book_scaled_credit_facility_gbp(origination_exposure)

    outcomes: list[DoseOutcome] = []
    for dose in doses:
        scaled = _scale_exposure(origination_exposure, stressed_exposure, dose)
        # Variation margin the company must POST, via the real producer, against the FIXED facility.
        mbook = build_margin_calls_from_mtm(
            scaled,
            as_of_date=as_of_date,
            settlement_deadline=settlement_deadline,
            credit_facility_gbp=facility_gbp,
        )
        total_call = mbook.total_outstanding_gbp()
        net_liquidity = round(facility_gbp + available_cash_gbp - total_call, 2)
        cover = round((facility_gbp + available_cash_gbp) / total_call, 4) if total_call > 0 else None
        # Total book MtM = sum of netted MtM across ALL names (incl. UNATTRIBUTED) = the P&L signal.
        book_pnl = round(sum(float(e.get("netted_mtm_gbp", 0.0)) for e in scaled.values()), 2)
        is_dead = net_liquidity < 0.0
        pnl_survives = book_pnl > 0.0
        outcomes.append(
            DoseOutcome(
                dose=dose,
                total_margin_call_gbp=total_call,
                facility_gbp=facility_gbp,
                available_cash_gbp=available_cash_gbp,
                net_liquidity_gbp=net_liquidity,
                cover_ratio=cover,
                book_pnl_gbp=book_pnl,
                is_dead_by_collateral=is_dead,
                pnl_survives=pnl_survives,
                death_while_pnl_survives=is_dead and pnl_survives,
            )
        )

    dead = [o for o in outcomes if o.is_dead_by_collateral]
    death_dose = min((o.dose for o in dead), default=None)
    survived = death_dose is None
    death_while = any(o.death_while_pnl_survives for o in outcomes)

    death_cause: Optional[str] = None
    if not survived:
        first_death = min(dead, key=lambda o: o.dose)
        # The load-bearing distinction (§1): dead on cash while solvent on paper is the MC-2 shape;
        # dead on both is ordinary insolvency and does NOT satisfy the acceptance bar.
        death_cause = (
            "collateral_while_solvent" if first_death.death_while_pnl_survives else "collateral_insolvent"
        )

    liquidity_min = min(o.net_liquidity_gbp for o in outcomes)
    covers = [o.cover_ratio for o in outcomes if o.cover_ratio is not None]
    cover_min = min(covers) if covers else None
    peak_call = max(o.total_margin_call_gbp for o in outcomes)

    return BreakingStrainResult(
        survived=survived,
        death_dose=death_dose,
        death_cause=death_cause,
        death_while_pnl_survives=death_while,
        liquidity_minimum_gbp=liquidity_min,
        cover_minimum=cover_min,
        doses=tuple(outcomes),
        facility_gbp=facility_gbp,
        price_move_alone=True,  # structural: the only inputs are marks; no injected loss line
        any_name_posted_margin=peak_call > 0.0,
        peak_margin_call_gbp=peak_call,
    )


def to_run_outcome_fields(result: BreakingStrainResult) -> dict:
    """Map a sweep result onto the raw `RunOutcomes` ledger fields (§2 'writes directly into the
    run-ledger fields already specified').

    Returns only the four fields the ledger row already carries — no score, no blended scalar. The
    run-loop caller merges these into its `RunOutcomes(...)` when it emits a row; this keeps the
    death-test decoupled from `background.run_manifest` (no ledger emission from here).
    """
    return {
        "survived": result.survived,
        "death_cause": result.death_cause,
        "liquidity_headroom_min_gbp": result.liquidity_minimum_gbp,
        "collateral_cover_min": result.cover_minimum,
    }
