"""The supplier's own counterparty-credit and collateral position, at one mark.

KNIFE pass 3, `A_composition_lift` step 19, 2026-08-12, disposition register
§3n. Before this, `simulation/run_phase2b.py::main()` ran the whole thing
itself: it marked the company's own trading book at an observable forward
snapshot, built the wholesale credit register, sampled the book semi-annually
for the peak exposure, derived the variation margin the company must post, and
then ran the MC-2 breaking-strain sweep off that same book. Three of that
module's wall crossings — `company.trading.wholesale_credit_exposure`,
`company.finance.margin_call_book` and `company.risk.collateral_death_test`.

WHY THIS IS THE SUPPLIER'S AND NOT THE WORLD'S. Marking your own open positions,
deciding what a counterparty's line is, working out the variation margin you owe
under a CSA and asking at what price move your facility breaks are the treasury
and credit-risk functions of a licensed supplier. They are not physics. The
world's job is to have supplied the energy and to have published the prices;
what the supplier concludes about its own credit exposure from those prices is
its own reading, and it is allowed to be wrong — which is the point, because a
supplier that misjudges exactly this is a supplier that fails in a price spike.

WHAT ARRIVES AND WHAT DOES NOT. The company's own trading book (an object the
world holds today — `company.trading.forward_book` is a separate crossing, ruled
separately and still live), its own customer register's commodity column, and
the two PUBLIC spot histories the marks are estimated from. All DATA through one
signature. This module imports nothing from `simulation/` or `sim/`.

WHY IT IS A GROUP AND NOT THREE ITEMS. All three read ONE shared intermediate:
`exposure_by_counterparty`, the ISDA-netted per-counterparty MtM at the mark.
The credit register is its long side, the margin book is its sign-complement,
and the death test re-marks the same live book at a second date. Worse, the
death test consumes `peak_sample_date` — a value produced INSIDE the credit
block's semi-annual sampling loop. Cutting them separately would have left the
world holding both intermediates and threading them back in, which is a seam
that publishes a pull: half a cut. Threading `peak_sample_date` through the
world was also a live defect surface — the world could hand the death test a
date from a different run's sampling — and this cut closes it by construction.

TWO INDEPENDENT FAILURE DOMAINS, PRESERVED. Before the cut these were two
separate `try/except` blocks in `main()` with the stated property that a failure
in the credit feed must not kill the death test, and that a partially-built
credit summary survives a failure in the margin half. One door with one
`try/except` at the call site would have silently merged them. So the isolation
lives HERE, and the two exceptions are returned on the result for the caller to
report — the caller prints exactly the two warnings it printed before.

BEHAVIOUR IS UNCHANGED BY CONSTRUCTION. Both blocks are transcribed
statement-for-statement off the same inputs, in their original order, with the
same rounding at the same places and the same keys on the same summary dicts.
Two `CompanyTariffEngine` instances are constructed, not one, because the
pre-cut code constructed two and collapsing them would be a behaviour change
smuggled in under a move.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Callable, Mapping, Sequence

from company.finance.margin_call_book import build_margin_calls_from_mtm
from company.pricing.tariff_engine import CompanyTariffEngine
from company.risk.collateral_death_test import breaking_strain_sweep, to_run_outcome_fields
from company.trading.wholesale_credit_exposure import build_credit_register_from_exposure

__all__ = [
    "CounterpartyCollateral",
    "build_counterparty_collateral",
    "collateral_death_test_summary",
]


@dataclass(frozen=True)
class CounterpartyCollateral:
    """One mark's worth of credit, margin and collateral-survival state.

    Every field is independently optional: a run too short to form observable
    marks produces `None` summaries without that being an error, and each of the
    two failure domains reports its own exception rather than suppressing the
    other's result.
    """

    credit_summary: dict | None = None
    margin_call_summary: dict | None = None
    death_test_summary: dict | None = None
    credit_feed_error: BaseException | None = None
    death_test_error: BaseException | None = None


def collateral_death_test_summary(
    trading_book,
    commodity_by_cid: Mapping[str, str],
    price_at: Callable[[str, str], "float | None"],
    effective_end: str,
    *,
    peak_sample_date: "str | None" = None,
    available_cash_gbp: float = 0.0,
) -> "dict | None":
    """MC-2 collateral death-test: the breaking-strain sweep against a REAL 2021-22 replay.

    DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY §2: the 1.0x point IS real history; the
    sweep scales the observed price MOVE (0.8/1.0/1.2/1.5x) and records the dose at which
    death-by-collateral arrives. NO difficulty knob (§1/§2) — the sweep is a MEASUREMENT, not a
    curriculum world. §3: the facility is book-derived at ORIGINATION and held fixed across the
    sweep (breaking_strain_sweep facility_gbp=None). R12: the stressed date is anchored to the
    REAL 2021-22 crisis, NEVER chosen to force a death.

    The SAME live book (calendar-live as-of the stressed date) is marked at two OBSERVABLE
    point-in-time forward prices: a calm ORIGINATION mark (when the positions were struck ->
    near-strike -> ~zero MtM baseline) and the STRESSED 2021-22 mark. Marking one fixed book at
    two prices isolates the pure price move, exactly what MC-2 measures. Wall-clean: own book
    term windows + own observable forwards; no simulation internal, no future leak.

    ``price_at(fuel, date) -> float | None`` is the point-in-time forward-price resolver — in the
    live run a closure over ``CompanyTariffEngine.get_forward_price`` (which itself reads only
    spot history BEFORE the mark date); injected in tests. Returns the summary dict, or ``None``
    if no real 2021-22 stress window / live book exists in this run (a short/fast run).
    """
    # Stressed date = the real 2021-22 gas crisis. Prefer the run's own observed peak-exposure
    # sample if it falls in 2021-22 (the worst mid-run point during the shock); else the crisis
    # anchor 2021-12-31. Both are REAL history — neither is chosen to make death arrive (R12).
    if peak_sample_date and "2021" <= peak_sample_date[:4] <= "2022":
        stressed_date = peak_sample_date
    else:
        stressed_date = "2021-12-31"
    if stressed_date >= effective_end:
        return None  # this run does not reach the real 2021-22 stress window
    live = trading_book.live_contracts_as_of(stressed_date)
    if not live:
        return None  # no positions calendar-live during the stress -> nothing to test

    # Origination mark = when these positions were struck (earliest live term_start): a calm,
    # pre-crisis observable forward. Marking the book there is ~its strike -> near-zero baseline.
    origination_date = min(c.term_start for c in live)
    orig_fwd: dict = {}
    stress_fwd: dict = {}
    for fuel in {commodity_by_cid.get(c.customer_id) for c in live}:
        if fuel is None:
            continue
        o = price_at(fuel, origination_date)
        s = price_at(fuel, stressed_date)
        if o is not None:
            orig_fwd[fuel] = o
        if s is not None:
            stress_fwd[fuel] = s
    orig_prices = {
        c.customer_id: orig_fwd[commodity_by_cid[c.customer_id]]
        for c in live
        if commodity_by_cid.get(c.customer_id) in orig_fwd
    }
    stress_prices = {
        c.customer_id: stress_fwd[commodity_by_cid[c.customer_id]]
        for c in live
        if commodity_by_cid.get(c.customer_id) in stress_fwd
    }
    origination_exposure = trading_book.exposure_by_counterparty_as_of(orig_prices, stressed_date)
    stressed_exposure = trading_book.exposure_by_counterparty_as_of(stress_prices, stressed_date)
    if not origination_exposure and not stressed_exposure:
        return None  # no marks could be formed from observable history at these dates

    result = breaking_strain_sweep(
        origination_exposure,
        stressed_exposure,
        available_cash_gbp=available_cash_gbp,  # facility-only lower bound (see summary note)
        as_of_date=stressed_date,
        settlement_deadline=stressed_date,
    )
    return {
        "stressed_date": stressed_date,
        "origination_date": origination_date,
        "n_live_contracts": len(live),
        "available_cash_gbp": available_cash_gbp,
        **to_run_outcome_fields(result),  # survived / death_cause / liquidity_headroom_min_gbp / collateral_cover_min (§2 run-ledger fields)
        # --- §4 R4 diagnosis signals (data-driven; NEVER a tuning cue, R12) ---
        "death_dose": result.death_dose,
        "death_while_pnl_survives": result.death_while_pnl_survives,
        "facility_gbp": result.facility_gbp,
        "price_move_alone": result.price_move_alone,
        "any_name_posted_margin": result.any_name_posted_margin,
        "peak_margin_call_gbp": result.peak_margin_call_gbp,
        "doses": [
            {
                "dose": d.dose,
                "total_margin_call_gbp": d.total_margin_call_gbp,
                "net_liquidity_gbp": d.net_liquidity_gbp,
                "cover_ratio": d.cover_ratio,
                "book_pnl_gbp": d.book_pnl_gbp,
                "is_dead_by_collateral": d.is_dead_by_collateral,
                "death_while_pnl_survives": d.death_while_pnl_survives,
            }
            for d in result.doses
        ],
        # available_cash_gbp=0.0 is the CONSERVATIVE facility-only liquidity lower bound: treasury
        # at a PAST point-in-time is not reconstructable in this feed. NOT a tuning cue (R12) — it
        # is the module default and a named R10 simplification; wiring point-in-time treasury cash
        # is a follow-on refinement.
        "_scope": (
            "MC-2 §2 breaking-strain MEASUREMENT surfaced to run output. NOT a run_ledger.jsonl "
            "row (§3 per-run RunManifest emission is unwired and semantically distinct from this "
            "collateral verdict) and NOT a §6 survival SCORE / capital organ (director-session gated)."
        ),
    }


def _mcr_accounts_held(
    settled_records: Sequence[dict],
    segment_by_cid: Mapping[str, str],
    mark_date: str,
) -> dict:
    """How many accounts the £130 MCR is levied on at the mark, and what that count SELECTS.

    A thin adapter onto `saas.capital.solvency.mcr_accounts_on_supply`, which owns the selection
    because it owns the £130. It is a function rather than an inline call so the one place the
    credit desk decides "which supplier's book?" is greppable, and so a caller reading this file
    is not sent to another package to find out.
    """
    from saas.capital.solvency import mcr_accounts_on_supply

    return mcr_accounts_on_supply(
        list(settled_records), dict(segment_by_cid), as_of=mark_date
    )


def _credit_and_margin(
    trading_book,
    commodity_by_cid: Mapping[str, str],
    elec_spot_records: Sequence[dict],
    gas_spot_records: Sequence[dict],
    mark_date: str,
    balance_sheet: "dict | None" = None,
    settled_records: "Sequence[dict] | None" = None,
    segment_by_cid: "Mapping[str, str] | None" = None,
) -> "tuple[dict | None, dict | None]":
    """The credit register, its multi-period peak, and the margin book at one mark.

    Transcribed from the pre-cut `run_phase2b.main()` block. Returns
    ``(credit_summary, margin_call_summary)``; the caller isolates the failure.

    `settled_records`/`segment_by_cid`, when both supplied, make this desk COUNT the accounts
    the MCR is levied on rather than being told a number — see `_mcr_accounts_held` below.
    """
    _mark_engine = CompanyTariffEngine()
    _current_fwd_by_commodity: dict[str, float] = {}
    for _fuel, _recs in (("electricity", elec_spot_records), ("gas", gas_spot_records)):
        try:
            _current_fwd_by_commodity[_fuel] = _mark_engine.get_forward_price(
                _fuel, mark_date, _recs
            )
        except ValueError:
            pass  # insufficient observable history at the mark date -> leave that fuel unmarked
    # Portability: derive each open contract's commodity from the customer register, never
    # hardcode a counterparty or fuel. Contracts whose commodity has no current mark are
    # skipped by exposure_by_counterparty (no price -> not marked).
    _mark_prices: dict[str, float] = {}
    for _c in trading_book.open_contracts():
        _px = _current_fwd_by_commodity.get(commodity_by_cid.get(_c.customer_id))
        if _px is not None:
            _mark_prices[_c.customer_id] = _px
    _exposure = trading_book.exposure_by_counterparty(_mark_prices)
    _credit_register = build_credit_register_from_exposure(_exposure)
    _largest = _credit_register.largest_exposure()
    _breaches = _credit_register.limit_breaches()
    credit_summary: dict | None = {
        "mark_date": mark_date,
        "current_forward_price_by_commodity": {
            k: round(v, 4) for k, v in _current_fwd_by_commodity.items()
        },
        "n_counterparties": len(_credit_register.all_records()),
        "total_net_exposure_gbp": round(_credit_register.total_net_exposure_gbp(), 2),
        "total_collateral_held_gbp": round(_credit_register.total_collateral_held_gbp(), 2),
        "largest_counterparty": _largest.counterparty_id if _largest else None,
        "largest_net_exposure_gbp": round(_largest.net_exposure_gbp, 2) if _largest else 0.0,
        "largest_utilisation_pct": round(_largest.utilisation_pct, 2) if _largest else 0.0,
        "is_limit_breached": len(_breaches) > 0,
        "n_breach": len(_breaches),
    }
    # VALUE_CHAIN multi-period sampling (2026-07-24): the single end-of-run mark above
    # marks a near-EMPTY book (almost every 2016-2025 term has delivered by effective_end)
    # -> the board-meaningful PEAK credit exposure, which occurs mid-run at maximum
    # concurrent open position during a price shock, was invisible. Sample the retained
    # book semi-annually at point-in-time forward marks (get_forward_price reads only spot
    # history before each mark date -> point-in-time discipline holds) and capture the peak.
    # Wall-clean: own book calendar windows + own observable forward marks; no sim internal.
    _samples: list[dict] = []
    try:
        _sample_years = sorted({c.term_start[:4] for c in trading_book.all_contracts()})
    except Exception:  # pragma: no cover - defensive
        _sample_years = [mark_date[:4]]
    _sample_dates = [
        f"{_y}{_mmdd}" for _y in _sample_years for _mmdd in ("-06-30", "-12-31")
        if f"{_y}{_mmdd}" < mark_date
    ] + [mark_date]
    for _sd in _sample_dates:
        _fwd_sd: dict[str, float] = {}
        for _fuel, _recs in (("electricity", elec_spot_records), ("gas", gas_spot_records)):
            try:
                _fwd_sd[_fuel] = _mark_engine.get_forward_price(_fuel, _sd, _recs)
            except ValueError:
                pass  # insufficient observable history at this mark date -> skip fuel
        _live_sd = trading_book.live_contracts_as_of(_sd)
        _mp_sd = {
            _c.customer_id: _fwd_sd[commodity_by_cid[_c.customer_id]]
            for _c in _live_sd
            if commodity_by_cid.get(_c.customer_id) in _fwd_sd
        }
        _reg_sd = build_credit_register_from_exposure(
            trading_book.exposure_by_counterparty_as_of(_mp_sd, _sd)
        )
        _samples.append({
            "sample_date": _sd,
            "n_live_contracts": len(_live_sd),
            "n_counterparties": len(_reg_sd.all_records()),
            "total_net_exposure_gbp": round(_reg_sd.total_net_exposure_gbp(), 2),
            "n_breach": len(_reg_sd.limit_breaches()),
        })
    _peak = max(_samples, key=lambda s: s["total_net_exposure_gbp"], default=None)
    credit_summary.update({
        "sampling": "semi-annual point-in-time marks (VALUE_CHAIN multi-period)",
        "n_samples": len(_samples),
        "peak_sample_date": _peak["sample_date"] if _peak else None,
        "peak_total_net_exposure_gbp": _peak["total_net_exposure_gbp"] if _peak else 0.0,
        "peak_n_live_contracts": _peak["n_live_contracts"] if _peak else 0,
        "peak_n_counterparties": _peak["n_counterparties"] if _peak else 0,
        "peak_is_limit_breached": bool(_peak and _peak["n_breach"] > 0),
        "sample_series": _samples,
    })
    # Sign-complement: variation margin the company must POST where its netted position
    # is out-of-the-money at the same mark. Dates are observable run state, not a clock read.
    _settlement_deadline = (
        date.fromisoformat(mark_date) + timedelta(days=1)
    ).isoformat()
    # R6 (2026-08-28): the balance sheet reaches the margin builder, so the independent amount a
    # counterparty demands over the mark stops being identically zero. `balance_sheet=None`
    # reproduces the pre-R6 shape exactly, which is what the desk's own unit tests pin.
    #
    # THE CLOSE-OUT MOVE IS MEASURED HERE rather than handed in, and that is a wall decision as
    # much as a tidiness one. The world hands over what it holds -- what the supplier is worth and
    # how many accounts it holds it against -- and this desk, which is already marking the book
    # against `elec_spot_records`, measures the stressed move in that same series. Measuring it on
    # the world side would have been a live `simulation -> company.risk` crossing, which the
    # register refused, and would have read the price history twice for one quantity.
    # THE ACCOUNT COUNT IS DERIVED HERE FOR THE SAME REASON THE CLOSE-OUT MOVE IS (2026-08-29).
    # The world hands over what it HOLDS -- its settled records and its own customer register --
    # and this desk derives the quantity it needs from them. Counting on the world side would have
    # been a live `simulation -> saas.capital.solvency` crossing, which the wall ratchet refuses,
    # and it would have put a company-side selection rule in a world-side file.
    #
    # WHAT IT REPLACED. `run_phase2b` used to pass `len(_ALL_KNOWN_CUSTOMERS)` = 24: the static
    # founder roster's per-COMMODITY legs. That is not the number of accounts a £130-per-account
    # obligation is levied on and never was -- it double-counts every dual-fuel household, cannot
    # see an account the funnel won (the list is bound at import), counts accounts that have
    # ceased, and makes no domestic/non-domestic split. The published MCR claim was £3,120 against
    # a book obliging £15,600.
    if balance_sheet is not None and settled_records is not None and segment_by_cid is not None:
        balance_sheet = dict(balance_sheet)
        _population = _mcr_accounts_held(settled_records, segment_by_cid, mark_date)
        balance_sheet["accounts_held"] = _population["count"]
        balance_sheet["accounts_population"] = _population["population"]
        balance_sheet["accounts_selection"] = _population["selection"]
    if balance_sheet is not None and "close_out_move_fraction" not in balance_sheet:
        from company.risk.independent_amount import close_out_move_fraction_from_history

        _move = close_out_move_fraction_from_history(elec_spot_records, mark_date)
        balance_sheet = dict(balance_sheet)
        # `None` (too little history to contain one close-out window) travels as NaN, never as a
        # zero: an unmeasurable move must TRIGGER the demand, not waive it.
        balance_sheet["close_out_move_fraction"] = (
            float("nan") if _move is None else _move
        )
    _margin_book = build_margin_calls_from_mtm(
        _exposure, as_of_date=mark_date, settlement_deadline=_settlement_deadline,
        balance_sheet=balance_sheet,
    )
    _summary = _margin_book.margin_call_summary()
    # THE CREDIT VERDICT, ON THE SURFACE RATHER THAN INFERRED FROM A ZERO. An independent amount of
    # £0 has three different meanings -- a strong balance sheet, a flat book, or an input nobody
    # could read -- and a reader of the published margin figures is entitled to know which. Carried
    # even when no balance sheet was supplied, where it says so.
    if balance_sheet is None:
        _summary["independent_amount_basis"] = "not_assessed_no_balance_sheet"
        _summary["total_independent_amount_gbp"] = 0.0
    else:
        from company.risk.independent_amount import independent_amount_gbp

        _gross = sum(
            abs(float(e.get("netted_mtm_gbp", 0.0)))
            for cp, e in _exposure.items() if cp != "UNATTRIBUTED"
        )
        _verdict = independent_amount_gbp(
            _gross,
            balance_sheet.get("net_assets_gbp", float("nan")),
            balance_sheet.get("accounts_held", 0),
            balance_sheet.get("close_out_move_fraction", float("nan")),
        )
        _summary["independent_amount_basis"] = _verdict["reason"]
        _summary["free_equity_gbp"] = _verdict["free_equity_gbp"]
        _summary["gross_marked_exposure_gbp"] = _verdict["gross_exposure_gbp"]
        # WHAT THE MCR WAS NETTED AGAINST, ON THE SURFACE (2026-08-29). Free equity is
        # `net_assets - accounts x £130`, and until this date the published figure said the
        # subtrahend's SIZE and never what it counted -- while five different account populations
        # were live in the run's own artefacts and this desk was multiplying by a sixth. The caller
        # names its population; the name is copied here so the figure and its basis cannot be read
        # apart. A caller that supplies a balance sheet without naming its population says so
        # explicitly rather than defaulting to a plausible label, because a wrong name is worse
        # than no name: it sends the next reader to the wrong roster.
        _summary["accounts_held"] = balance_sheet.get("accounts_held", 0)
        _summary["accounts_population"] = balance_sheet.get(
            "accounts_population", "unnamed -- the caller did not say what it counted"
        )
        _summary["accounts_selection"] = balance_sheet.get("accounts_selection")
        _summary["total_independent_amount_gbp"] = sum(
            c.initial_margin_gbp for c in _margin_book.outstanding_calls()
        )
        # HOW FAR THE COMPANY IS FROM THE TRIGGER, in pounds, whichever side of it it sits. This is
        # the number that makes SURVIVE mean something: it is what the balance sheet would have to
        # lose -- to acquisition spend or anything else -- before counterparties start asking for
        # collateral above the mark.
        _free = _verdict["free_equity_gbp"]
        if _free is not None:
            _summary["free_equity_headroom_to_independent_amount_gbp"] = round(
                _free - _verdict["gross_exposure_gbp"], 2)
    return credit_summary, _summary


def build_counterparty_collateral(
    trading_book: Any,
    *,
    commodity_by_customer_id: Mapping[str, str],
    elec_spot_records: Sequence[dict],
    gas_spot_records: Sequence[dict],
    mark_date: str,
    available_cash_gbp: float = 0.0,
    balance_sheet: "dict | None" = None,
    settled_records: "Sequence[dict] | None" = None,
    segment_by_customer_id: "Mapping[str, str] | None" = None,
) -> CounterpartyCollateral:
    """Mark the book once and return the whole credit/collateral position.

    `elec_spot_records` and `gas_spot_records` are keyword-only and separately
    named on purpose: the pre-cut code paired fuel to record list inline at the
    point of use, so the two could not be confused, and a positional signature
    would have reintroduced that as a swap the impl can never see. §3n's control
    3 asserts the pairing at the real call site anyway.

    Neither block raises: each failure domain is caught and reported on the
    result, exactly as the two `try/except` blocks in the pre-cut `main()` did.
    A partially-built credit summary is NOT discarded when the margin half
    fails, because it was not discarded before.

    `settled_records` and `segment_by_customer_id` are the supplier's own settlement record and
    its own customer register. Supplied together, they make the desk COUNT the accounts the MCR
    is levied on instead of accepting a number it cannot check — the balance sheet's
    `accounts_held` is then overwritten, and the population's NAME travels onto the published
    margin summary beside it. Omitted, the caller's `accounts_held` stands unchanged, which is
    what every existing unit test pins. Both or neither: a segment map with no records cannot
    count anything, and records with no segment map would silently read every non-domestic
    account as domestic.
    """
    credit_summary: dict | None = None
    margin_call_summary: dict | None = None
    credit_feed_error: BaseException | None = None
    death_test_error: BaseException | None = None
    try:
        credit_summary, margin_call_summary = _credit_and_margin(
            trading_book,
            commodity_by_customer_id,
            elec_spot_records,
            gas_spot_records,
            mark_date,
            balance_sheet,
            settled_records,
            segment_by_customer_id,
        )
    except Exception as exc:  # pragma: no cover - defensive, the run must not die
        credit_feed_error = exc

    death_test_summary: dict | None = None
    try:
        _mc2_engine = CompanyTariffEngine()
        _mc2_recs_by_fuel = {
            "electricity": elec_spot_records,
            "gas": gas_spot_records,
        }

        def _mc2_price_at(_fuel, _date):
            _recs = _mc2_recs_by_fuel.get(_fuel)
            if _recs is None:
                return None
            try:
                return _mc2_engine.get_forward_price(_fuel, _date, _recs)
            except ValueError:
                return None  # insufficient observable history before the mark date -> unmarked

        death_test_summary = collateral_death_test_summary(
            trading_book,
            commodity_by_customer_id,
            _mc2_price_at,
            mark_date,
            peak_sample_date=(credit_summary or {}).get("peak_sample_date"),
            available_cash_gbp=available_cash_gbp,
        )
    except Exception as exc:  # pragma: no cover - defensive, the run must not die
        death_test_error = exc

    return CounterpartyCollateral(
        credit_summary=credit_summary,
        margin_call_summary=margin_call_summary,
        death_test_summary=death_test_summary,
        credit_feed_error=credit_feed_error,
        death_test_error=death_test_error,
    )
