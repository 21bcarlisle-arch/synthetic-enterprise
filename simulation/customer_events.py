"""Customer lifecycle event log — Phase 6b / Phase 7e.

Provides `roll_lifecycle_event()`, called by `run_phase2b.main()` at each
billing-account renewal point (electricity legs only; gas legs share the
household decision — see `simulation.household.household_of`, which is the
WORLD's answer to "which supply points are one home", not the supplier's
billing arrangement; KNIFE step 28, register §3w).

The roll is fully deterministic: `random.Random(f"{billing_account}_{term_start}")`.
Two identical runs always produce the same event sequence. Tests can force
specific outcomes by patching `_RANDOM_CLASS` or seeding via a known
`customer_id` + `term_start_str` combination.

Phase 7e adds a second deterministic roll when an account churns: did we win
the home-mover's business? Seed: `f"win_{billing_account}_{term_start_str}"`.
`home_move_won` appears on every event dict (False for renewals; True/False for
churns). When True, `run_phase2b.main()` activates the successor customer.

Architecture note: this module sits at the interface between the sim (raw
settlement records) and the SaaS layer (churn/win-rate models). It imports
from `saas/` (churn_model, home_move_win_rate, customer_reaction) — the same
cross-seam boundary as `simulation/run_phase4c_on_phase2b.py`. This is
intentional: Phase 6b turns existing *risk scores* into actual *events*, and
the models that compute those scores already live in `saas/`.
"""
import random as _random
from datetime import date

from company.crm.churn_model import estimate_churn_probability
from saas.churn_model import build_churn_risk
from saas.home_move_win_rate import build_home_move_win_rates
from simulation.departure_level_anchor import year_level_anchor
from simulation.departure_risks import (
    DECLARED_SENSITIVITY_SCALE,
    DECLARED_SHOCK_WEIGHT,
    ORDERED_CAUSES,
    build_departure_risks,
    resolve_departure,
    total_departure_probability,
)
from simulation.household import GAS_LEG_ID_SUFFIX, IncomeStress, household_of
from simulation.market_switching_propensity import (
    churn_position_multiplier,
    market_switching_multiplier,
    offer_position_multiplier,
    perceived_price_differential,
)
from simulation.satisfaction_churn import satisfaction_churn_multiplier
from simulation.shown_price import shown_annual_bill_gbp
from simulation.switching_propensity import (
    stress_switching_multiplier,
    tenure_switching_multiplier,
)

PRICE_DIFFERENTIAL_PCT = 0.0  # matches run_phase4c_on_phase2b.py

#: The only occasion this module emits. A renewal-point decision is the one place the world
#: currently asks a household whether it stays, and `roll_lifecycle_event` owns it.
DEPARTURE_OCCASION_RENEWAL = "renewal"

#: C1b. A departure from the standard variable product, which happens DURING a cap period and not
#: at any boundary the supplier serves notice of. Named for the occasion and not for the cause --
#: `departure_cause` carries the risk that fired, and the two are separate facts. A reader whose
#: denominator is renewal DECISIONS must select on this to keep its own quantity whole:
#: `tools/population_anchor._churn_by_year` divides by `renewals + churns`, and an SVT departure
#: is a churn with no renewal beside it.
DEPARTURE_OCCASION_SVT_SEGMENT = "svt_segment"


def departure_event(
    *,
    customer_id: str,
    event_date: str,
    commodity: str,
    occasion: str,
    cause: str | None = None,
    **extra,
) -> dict:
    """A lifecycle event for a departure that did NOT happen at a renewal point.

    THE SHAPE, NOT THE PHYSICS, AND THAT SPLIT IS DELIBERATE (2026-08-30). C2's competing-risks
    form is still unwired -- `simulation/departure_risks.py` holds it, the P0 calibration came back
    non-identifying, and the delivery direction holds the wiring until the departure-level
    correction has landed and its run has been read on its own. None of that blocks the SCHEMA
    question, which is the one C1b and C6 are actually stuck behind: a household that never leaves
    SVT never reaches a renewal point, so until now its leaving had no record shape at all. It was
    not that the world said it stayed; it was that there was nowhere to write down that it went.

    `occasion` is what brought the account to a decision and must not be `"renewal"` --
    `roll_lifecycle_event` is the sole producer of renewal-point events because it is the only
    thing holding the roll, the probabilities and the factor decomposition, and a second
    constructor able to mint one would put records in the log that look like renewal decisions and
    carry none of the evidence for one.

    `cause` is which risk fired, and defaults to `None` rather than to a risk. A default of
    `bill_shock` -- first in `ORDERED_CAUSES`, and the tempting one -- would publish a reason mix
    of 100%/0%/0% that a reader could not tell from a measurement.
    """
    if not occasion:
        raise ValueError("a departure must name its occasion; an unnamed one cannot be selected")
    if occasion == DEPARTURE_OCCASION_RENEWAL:
        raise ValueError(
            f"occasion {occasion!r} belongs to roll_lifecycle_event, which is the only producer "
            "holding the roll and the factor decomposition a renewal-point event must carry"
        )
    if cause is not None and cause not in ORDERED_CAUSES:
        raise ValueError(
            f"cause {cause!r} is not a risk this world publishes: {ORDERED_CAUSES}. "
            "(`financial_stress` is a MODULATOR -- see simulation/departure_risks.py.)"
        )
    return {
        "customer_id": customer_id,
        "event_date": event_date,
        "commodity": commodity,
        "event_type": "churned",
        "departure_occasion": occasion,
        "departure_cause": cause,
        **extra,
    }


def twelve_month_window_open(anniversary: date) -> date:
    """The day a 12-month lookback opens for a term starting on `anniversary`.

    THE 29 FEBRUARY CLASS, and it is a crash rather than a wrong number. `d.replace(year=...)`
    raises `ValueError: day 29 must be in range 1..28` on a leap day, so any account whose term
    starts 29 February takes the whole run down. It was latent for as long as no such account
    existed; the director's founder book put 80 accounts into 2016 and one of them landed on
    2016-02-29, which is how it surfaced (`run_phase2b._company_eac_estimate`).

    1 MARCH, NOT 28 FEBRUARY, for two reasons and NOT for a third that looks obvious and is
    wrong. The wrong one first, because it was the draft: "28 February would let the company
    see more than a year". It would not -- it gives a 365-day window against 1 March's 364, and
    an ordinary anniversary across a leap year is 366 days anyway. Neither candidate breaches
    the blindfold. The actual reasons are that 1 March errs SHORTER, which is the safe side of
    a point-in-time window; and that it is the convention this repository already chose the one
    other time it met this edge (`company/billing/fit_legacy_register`, "Feb 29 edge case: use
    March 1"), now stated in one place instead of inlined at each.
    """
    try:
        return anniversary.replace(year=anniversary.year - 1)
    except ValueError:
        return date(anniversary.year - 1, 3, 1)


def _price_differential_vs_market(
    new_rate_gbp_per_mwh: float | None,
    term_start_str: str,
    *,
    position_ledger=None,
    wholesale_gbp_per_mwh: float | None = None,
) -> float | None:
    """Where THIS customer's offered rate sits against the published market reference.

    Returns a fraction: 0.05 = 5% dearer than the SVT, -0.05 = 5% cheaper. `None` when the rate
    or the reference is unavailable, so the caller can fall back rather than treat an unknown
    position as parity -- parity is a claim, and "we do not know where we sit" is not it.

    THE SVT IS THE REFERENCE because it is the published default a real household is compared
    against, it is what `company/pricing/renewal_desk._apply_competitive_ceiling` already prices
    against, and `_build_churn_basis_risk` already reports the same quantity as
    `rate_vs_svt_pct`. Introducing a second notion of "the market" here would be one name and two
    numbers, which this repository has paid for before.
    """
    if new_rate_gbp_per_mwh is None:
        return None
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    reference = get_svt_elec_rate_gbp_per_mwh(term_start_str)

    # THE REFERENCE DEFENDS (2026-08-28, director's C2: "nothing in the world responds to what
    # the company does. Nobody undercuts it, nobody defends, nobody targets its book"). With no
    # ledger this is byte-identically the published cap, which is what every measurement before
    # today was taken against; with one, a rival that has seen the company undercut it follows
    # that price down over quarters, so a price advantage DECAYS instead of persisting.
    #
    # THE LAG IS WHY IT IS SAFE TO READ THE COMPANY'S OWN RATE HERE. The ledger reports the
    # PREVIOUS quarter's mean, never this term's rate, so nothing about the offer being priced
    # right now can reach the reference it is being measured against -- which would be a rival
    # with foresight, and a tautology besides.
    if position_ledger is not None:
        from simulation.competitor_reference import competitor_reference_rate_gbp_per_mwh

        moved = competitor_reference_rate_gbp_per_mwh(
            term_start_str,
            company_rate_gbp_per_mwh=position_ledger.position_for(term_start_str),
            wholesale_gbp_per_mwh=wholesale_gbp_per_mwh,
        )
        if moved is not None:
            reference = moved

    if not reference or reference <= 0:
        return None
    return (float(new_rate_gbp_per_mwh) - float(reference)) / float(reference)


def _svt_position(rate_gbp_per_mwh: float | None, term_start_str: str) -> float | None:
    """This customer's position against the PUBLISHED CAP, whatever the competitor is doing.

    Deliberately re-derived rather than reusing `differential`: the whole point is that it stays
    the SVT position after the reference moves, so it may never be the same call.
    """
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    if rate_gbp_per_mwh is None:
        return None
    svt = get_svt_elec_rate_gbp_per_mwh(term_start_str)
    if not svt or svt <= 0:
        return None
    return round((float(rate_gbp_per_mwh) - float(svt)) / float(svt), 4)


def _market_reference_gbp_per_mwh(
    term_start_str: str, *, position_ledger=None, wholesale_gbp_per_mwh: float | None = None
) -> float | None:
    """The LEVEL the differential above was taken against, for anything that has to reconcile.

    ONE NAME, ONE NUMBER (2026-08-28). The competitor reference caught this the day it landed:
    `tools/run_price_ladder`'s own SVT reconciliation went from `agrees=True` to `agrees=False`
    with a 21.3 percentage-point gap, because the world's logged `price_differential_vs_svt` had
    quietly stopped being against the SVT while keeping the name. The control was right and the
    field was lying. Publishing the LEVEL as well as the ratio means a consumer reconciles
    against the number that was actually used rather than re-deriving one that used to match.
    """
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    if position_ledger is None:
        return get_svt_elec_rate_gbp_per_mwh(term_start_str)
    from simulation.competitor_reference import competitor_reference_rate_gbp_per_mwh

    return competitor_reference_rate_gbp_per_mwh(
        term_start_str,
        company_rate_gbp_per_mwh=position_ledger.position_for(term_start_str),
        wholesale_gbp_per_mwh=wholesale_gbp_per_mwh,
    ) or get_svt_elec_rate_gbp_per_mwh(term_start_str)

#: Segments the Ofgem/BMG evidence actually covers. Its sample is 3,235 GB **domestic energy bill
#: payers**; it says nothing whatever about how an industrial site buys power.
_DOMESTIC_SEGMENTS = {"resi"}


def _bill_scale_for(segment: str | None, bill_gbp: float | None) -> float | None:
    """The bill scale to feel the price differential against — or None for the market average.

    THE DOMESTIC CURVE GOVERNS DOMESTIC HOUSEHOLDS AND NOTHING ELSE, and the first version of the
    GBP change forgot to say so. `_savings_to_rate` is calibrated on DESNZ/Ofgem **household**
    switching against annual savings of GBP 0-400, and beyond that ceiling it continues at the last
    informed slope -- a named simplification that is harmless while the input stays near the
    calibrated range and absurd when it does not.

    Scaling by the customer's OWN bill is right for a household (GBP 600-5,000, so a 10%
    differential lands at GBP 60-500, at or near the calibrated range) and catastrophic for an
    industrial site. Measured on `C_IC3`, a 4 GWh chemical plant: a 10% differential on a
    ~GBP 500,000 bill is GBP 50,000 of "annual saving", 125x beyond where the data stops, and the
    linear extrapolation returned a churn multiplier of **x599.6**. The plant left immediately and
    a settlement-records test went red -- which is how this was found.

    NON-DOMESTIC KEEPS THE MARKET-AVERAGE SCALE, deliberately, and that is an honest placeholder
    rather than a fix: industrial supply is TENDERED and broker-mediated on contract terms, not
    chosen off a comparison site, so a domestic switching curve is the wrong model for it at any
    scale. Modelling I&C churn properly is its own piece of work; what this must not do is let a
    domestic curve run 125x past its evidence and call the answer physics.

    AN UNKNOWN SEGMENT FALLS BACK TO THE MARKET AVERAGE, not to domestic. If the roster lookup ever
    fails, the safe answer is the PREVIOUS behaviour -- bounded, and wrong only in the way the world
    was already wrong -- rather than the new unbounded one. Defaulting an unknown to "domestic"
    would apply the extrapolating curve to whatever it could not identify, which is precisely the
    failure above, re-entered through the error path.
    """
    if bill_gbp is None:
        return None
    if segment not in _DOMESTIC_SEGMENTS:
        return None
    return bill_gbp


def _annual_bill_gbp(
    billing_account: str, records_so_far: list[dict], term_start_str: str
) -> float | None:
    """What we billed THIS household over the trailing year, across ALL its supply points.

    THE SCALE THE PRICE RESPONSE IS FELT AGAINST. Ofgem/BMG 2024 found households value savings in
    ABSOLUTE terms, so a percentage differential has to be turned into pounds against the
    household's own spend rather than a market average -- see
    `market_switching_propensity.churn_position_multiplier`.

    SUMMED ACROSS THE LEGS, WHICH IS THE WHOLE POINT OF USING THE HOUSEHOLD AND NOT THE SUPPLY
    POINT. A dual-fuel home's bill is its electricity AND its gas; scoring it on the electricity
    leg alone would understate the money at stake by roughly a third and make every dual-fuel
    household look less price-exposed than it is. This repository has already paid once for
    reasoning about one leg of a two-leg household (the 2026-08-27 gas-leg inversion, where all 18
    apparent anomalies vanished when the legs were summed).

    RETURNS None, NOT A GUESS, when the trailing year is empty -- a first renewal with no settled
    history has no bill to be felt, and the caller's default is the market-average scale. Inventing
    a bill here would put a fabricated number into a churn decision.

    Point-in-Time: `records_so_far` stops before this term by construction (see the caller), so
    this can only ever see settled history.
    """
    billed = _annual_bill_and_volume(billing_account, records_so_far, term_start_str)
    return billed["gbp"] if billed else None


def _annual_bill_and_volume(
    billing_account: str, records_so_far: list[dict], term_start_str: str
) -> dict | None:
    """The same trailing window, returning what was billed AND the volume it was billed on.

    ONE PASS AND ONE POPULATION, which is the whole reason this exists rather than a second
    walker beside `_annual_bill_gbp`. C3 needs pounds and kWh over the identical set of records:
    two walkers with independently-drifting filters would produce a ratio whose numerator and
    denominator count different things, and this repository's most-repeated published defect is
    exactly that -- two true numbers whose ratio is not a quantity.

    `fuels` comes from the records actually settled in the window, not from the roster. A roster
    saying dual-fuel while only the electricity leg billed would have the household shown a
    dual-fuel typical volume it never took, and the shown price has to be built on what was
    supplied.
    """
    start = date.fromisoformat(term_start_str)
    window_start = twelve_month_window_open(start)
    total = 0.0
    kwh = 0.0
    fuels: set[str] = set()
    seen = False
    for rec in records_so_far:
        rec_id = rec.get("customer_id", "")
        if household_of(rec_id) != billing_account:
            continue
        settled = rec.get("settlement_date")
        if not settled or not (window_start <= date.fromisoformat(settled) < start):
            continue
        total += float(rec.get("revenue_gbp") or 0.0)
        kwh += float(rec.get("consumption_kwh") or 0.0)
        fuels.add("gas" if rec_id.endswith(GAS_LEG_ID_SUFFIX) else "electricity")
        seen = True
    if not seen or total <= 0:
        return None
    return {"gbp": total, "kwh": kwh, "fuels": fuels}


# Disposition of a churned account's home-move outcome. Three-valued because the
# WIN roll and the DELIVERY of that win are two different facts.
HOME_MOVE_ACTIVATE_SUCCESSOR = "activate_successor"
HOME_MOVE_GO_TO_MARKET = "go_to_market"


def home_move_disposition(home_move_won: bool, successor_id: str | None) -> str:
    """What actually happens to a churned billing account, given the win roll and
    whether the property HAS a successor supply point on the book.

    A win is only real once there is a supply point to activate. The roster
    carries successors for 6 of 13 billing accounts (and none at all for the
    curriculum's drawn SYN-* points), so `home_move_won=True` with
    `successor_id=None` is a live, common state, not an edge case.

    The rule this function exists to hold: **an undeliverable win is a plain
    loss.** It disposes to `GO_TO_MARKET`, exactly as a lost home-mover does.
    Written as an `if won: ... elif replace: ...` chain instead, the outer branch
    swallows the undeliverable win and the account is lost with no successor AND
    no market replacement — making a won roll strictly worse for the company than
    a lost one (WORKER_FINDING_A_WON_HOME_MOVER_WITH_NO_SUCCESSOR_SUPPLY_POINT_
    SUPPRESSES_THE_REPLACEMENT_TOO_2026-08-14.md, BLOCKING).

    This deliberately does NOT touch `win_probability`: the missing successor is a
    ROSTER limitation, not a world fact about that property, so zeroing the
    probability would encode a book artefact as a belief about the world. The
    consequence — the realised win rate runs below its parameter for accounts with
    no successor point — is recorded, not tuned away.
    """
    if home_move_won and successor_id:
        return HOME_MOVE_ACTIVATE_SUCCESSOR
    return HOME_MOVE_GO_TO_MARKET


def roll_lifecycle_event(
    customer_id: str,
    term_start_str: str,
    commodity: str,
    records_so_far: list[dict],
    customers: list[dict],
    price_differential_pct: float = PRICE_DIFFERENTIAL_PCT,
    old_rate_gbp_per_mwh: float | None = None,
    new_rate_gbp_per_mwh: float | None = None,
    retention_modifier: float | None = None,
    precomputed_company_estimate: float | None = None,
    passive_churn_cap: float | None = None,
    income_stress: IncomeStress | None = None,
    satisfaction_score: float | None = None,
    market_year: int | None = None,
    position_ledger=None,
    wholesale_gbp_per_mwh: float | None = None,
) -> dict | None:
    """Compute and roll the churn/renewal event for a billing account at a
    renewal point.

    Call only for electricity legs (`commodity == "electricity"`) at
    `term_index >= 1` — gas legs share the billing-account-level decision.

    `records_so_far` must contain only settlement records up to (not
    including) the current term start — Point-in-Time safe by construction
    when called from `run_phase2b.main()` before the current term is settled.

    Returns a lifecycle event dict:
      {customer_id (billing account), event_date, commodity,
       event_type: "renewed"|"churned",
       departure_occasion: "renewal", departure_cause: None,
       churn_probability, win_probability, effective_retention_probability,
       realized_churn_probability, random_roll}

    `departure_occasion` is always "renewal" here — this function is the sole producer of
    renewal-point events. `simulation.customer_events.departure_event` is the constructor for a
    departure that is not a renewal (C1b, C6), and refuses the "renewal" occasion for that reason.
    `departure_cause` is None until C2's competing-risks form is wired.

    `churn_probability` is the raw, pre-adjustment SIM base rate (bill-shock
    driven, from `saas.churn_model`) -- informational only, never what the
    dice roll actually used. `effective_retention_probability` is the true
    probability used for the roll, after every adjustment (passive cap,
    market conditions, income stress, satisfaction, retention offer).
    `realized_churn_probability` (Phase QA) is `1 - effective_retention_probability`
    captured BEFORE the retention-offer adjustment -- the correct ground
    truth to compare a company churn estimate against, since the estimate is
    computed before the company decides whether to make an offer.

    Returns None if no renewal data is available in the churn model (can
    happen when `records_so_far` is too short to compute bill-shock history
    for this account's first renewal point).
    """
    billing_account = household_of(customer_id)
    term_month = term_start_str[:7]

    # ASK ABOUT THE RENEWAL WE ARE ACTUALLY PRICING (2026-08-27). `records_so_far` stops before
    # this term by construction (Point-in-Time), so without `through_period` the churn model's
    # horizon ends one period short of the very renewal being rolled and returns no entry for it.
    # See the note in `saas.churn_model.build_churn_risk`: this silenced churn entirely for
    # every account whose anniversary fell on the 1st of a month rather than the 31st.
    churn_risk = build_churn_risk(records_so_far, customers, through_period=term_month)
    win_rates = build_home_move_win_rates(churn_risk, customers, price_differential_pct)

    renewal_data = next(
        (r for r in win_rates.get(billing_account, []) if r["renewal_period"] == term_month),
        None,
    )
    if renewal_data is None:
        return None

    roll = _random.Random(f"{billing_account}_{term_start_str}").random()
    effective_p_retain = renewal_data["effective_retention_probability"]
    # Phase 33: passive renewers have lower SIM ground-truth churn — cap the
    # churn probability at passive_churn_cap before applying any retention modifier.
    if passive_churn_cap is not None:
        p_churn_raw = 1.0 - effective_p_retain
        effective_p_retain = 1.0 - min(p_churn_raw, passive_churn_cap)
    # C2 (2026-08-30): the four factor values the competing-risks form needs as hazard inputs,
    # captured as they are computed rather than reconstructed afterwards. They are emitted on the
    # event dict below as SIM ground truth -- same class as `engagement_level`, and like it they
    # MUST NEVER be read by company/** decision code. Reconstructing them later is not equivalent:
    # `renewal_data["churn_probability"]` (the raw base rate on the event) is NOT the number the
    # chain starts from, which is `1 - effective_retention_probability`, and the difference is
    # exactly the quantity the P0 calibration is fitted against.
    _bill_shock_base = 1.0 - effective_p_retain
    _market_opportunity = 1.0
    _price_response = 1.0
    _action_propensity = 1.0
    _dissatisfaction_response = 1.0
    # Phase NS: apply market-conditions switching multiplier (savings elasticity).
    # Suppresses churn in crisis years (2022: no cheaper alternatives); amplifies in
    # high-competition years (2016-2018). Applied before income_stress so market
    # opportunity ceiling is set first, then individual customer frictions modify it.
    if market_year is not None:
        _market_opportunity = market_switching_multiplier(market_year)
    # OUR OWN PRICE POSITION, and until 2026-08-25 the world could not see it.
    #
    # THE DEFECT, MEASURED. `price_differential_pct` arrived here as a parameter and was used at
    # exactly ONE site: `build_home_move_win_rates`. It touched the WIN side and nothing in the
    # churn chain at all. So an existing customer's chance of leaving read bill shock, income
    # stress, satisfaction, market conditions and tenure -- and never what this supplier was
    # charging them relative to everyone else. The company could price itself to any level and
    # lose nobody for it.
    #
    # WHAT THAT COST, and it is the whole thesis rather than a detail. The director's frame is a
    # supplier that "should behave like an average player by default, and beat average precisely
    # to the degree it understands and predicts the truth better than average", measured against
    # "the same book run by a supplier applying flat rules". With price disconnected from
    # departure there is no such measurement: over-pricing has no consequence, so a flat-rules
    # baseline can be neither beaten nor lost to on the one lever a supplier actually holds. It
    # also explains the world's observed churn never exceeding 0.41 against its own 0.95 ceiling
    # -- the largest lever was not attached.
    #
    # THE MIRROR OF THE WIN SIDE, on purpose. `50274434a` (PB3 b1, the same day) gave the WIN
    # side `offer_position_multiplier`, and its docstring proves `m(d) * m(-d) == 1` so that
    # "there is no d at which both legs improve". The loss side takes the reciprocal, which by
    # that identity is `m(-d)`: being dearer costs departures in exactly the proportion it costs
    # wins. Reusing the same curve is what keeps the guarantee exact rather than approximate --
    # two independently-shaped price responses would leave a differential at which the company
    # gained on both legs, which is the goal-seeking hole R12 exists to close.
    #
    # R13: BASELINE, not curriculum. Real households leave suppliers that become expensive; a
    # world where they cannot is less faithful, not easier. It was decided blind to company P&L
    # and it moves AGAINST the company -- it introduces a way to lose customers that did not
    # exist before, and no way to gain any.
    # PER CUSTOMER, NOT PER RUN, and that difference is what makes per-customer pricing
    # testable at all. A run-level constant would move the whole book together and could never
    # distinguish a supplier that prices two customers differently from one that prices them the
    # same -- which is the only distinction the thesis is about. The differential is therefore
    # derived from THIS customer's own offered rate against the published SVT, the same
    # market reference `renewal_desk._apply_competitive_ceiling` already prices against and the
    # one `_build_churn_basis_risk` already reports as `rate_vs_svt_pct`. The run-level parameter
    # remains as the fallback for a caller that has no rate to hand.
    differential = _price_differential_vs_market(
        new_rate_gbp_per_mwh, term_start_str,
        position_ledger=position_ledger, wholesale_gbp_per_mwh=wholesale_gbp_per_mwh,
    )
    if differential is None:
        differential = price_differential_pct
    if differential:
        # `churn_position_multiplier`, not `1 / offer_position_multiplier`, and the difference
        # only appears past +25%: the shared curve saturates there, so a supplier 25% above the
        # market and one 200% above it were losing the SAME third of their book. The loss leg
        # continues at the last slope the data informs; the win leg keeps the saturation, because
        # you cannot win more customers than the market has to give. See that function for the
        # measurement and for what would discharge the assumption.
        #
        # AND THE HOUSEHOLD'S OWN SENSITIVITY WEIGHTS IT (2026-08-27). Until this line existed,
        # every household in the world shared ONE price-response curve: two customers in identical
        # circumstances responded identically, so there was no household TYPE to infer and the
        # company could demonstrate no inference advantage however good its model got. The
        # `price_sensitivity` axis was already drawn per household, coverage-tested, walled off
        # from the company and mutation-tested against leaks -- and read by nothing. The
        # curriculum file even states it is "discoverable via rate-change churn response", a
        # channel that did not exist until this call. See
        # `docs/design/WHAT_A_HOUSEHOLD_DECIDES_ON.md`.
        #
        # R13 BASELINE, NOT CURRICULUM, on both halves of the test. FIDELITY: real households
        # differ in how hard they feel a price move, and a world where they cannot is less
        # faithful, not easier. The MARGINALS (how many households are highly elastic) remain
        # the director's.
        #
        # BLIND TO COMPANY P&L -- BUT NOT AGGREGATE-NEUTRAL, AND THE FIRST DRAFT OF THIS COMMENT
        # SAID IT WAS. The weights are mean-preserving in the WEIGHT (population mean exactly
        # 1.000 against the curriculum's own shares, `medium` exactly 1.0) but NOT in the
        # RESPONSE: `churn_position_multiplier` is CONVEX, so by Jensen a mean-preserving spread
        # in its ARGUMENT raises the mean response. Measured in that function's own module note,
        # `E[m(d*w)] / m(d)` = 1.142 at -20% and 1.118 at +20% -- the book churns MORE, by up to
        # ~14%, purely from households now differing. That is recorded rather than tuned away:
        # renormalising the weights until aggregate churn held still would be selecting
        # parameters to hit an output, which R12 forbids. The DIRECTION is why it is safe to make
        # without the director -- it moves AGAINST the company, never for it -- and it was fixed
        # before any pricing arm was re-run against it. Pinned by
        # `test_the_spread_RAISES_average_churn_and_that_is_recorded_not_tuned_away`.
        #
        # THE RUN'S SEED, NOT THE MODULE DEFAULT. `run_base_seed()` returns the seed THIS run's
        # book was drawn at; resolving the trait from the default instead would be correct only
        # until something passed `base_seed=`, and would then hand this customer a sensitivity
        # its own cohort does not carry -- the disagreement `price_sensitivity_for_customer`'s
        # single-mechanism design exists to prevent. The deferred import is this module's
        # existing pattern for `household_segments` below, and is required here: `population_draw`
        # cannot import `live_population` (that direction is already taken).
        #
        # A CONTINUOUS PER-HOUSEHOLD ELASTICITY, NOT A SEGMENT MEAN (2026-08-27, director). The
        # Ofgem subgroup range is a BETWEEN-GROUP statistic and says nothing about spread between
        # individuals; real elasticity is close to orthogonal to observables, which is why
        # couponing, time-limited offers and price walks work at all -- you cannot tell in advance
        # who responds. Using the three subgroup means alone modelled a world where a household's
        # segment gave its elasticity exactly, which is not a small spread but the WRONG QUANTITY.
        from simulation.live_population import run_base_seed
        from simulation.population_draw import price_elasticity_for_customer

        elasticity = price_elasticity_for_customer(billing_account, run_base_seed())
        felt = perceived_price_differential(differential, elasticity)
        #
        # AND THE SCALE IS THIS HOUSEHOLD'S OWN BILL, IN POUNDS, NOT A PERCENTAGE. The calibrated
        # curve was always a function of an absolute annual saving; the conversion into it used one
        # market-average bill for every household, so a small flat and a large house at the same
        # percentage were modelled as facing the same money. Ofgem/BMG 2024: *"consumers value
        # savings in absolute terms rather than in proportion to their bill."* Derived from what we
        # have actually BILLED this household -- a fact a real supplier plainly has, and
        # Point-in-Time safe because `records_so_far` stops before this term by construction.
        # C3, 2026-08-30: THE SCALE IS THE BILL THE HOUSEHOLD IS SHOWN, NOT THE ONE IT PAYS.
        # The paragraph above is right that a percentage has to become pounds, and right about the
        # source. What it got wrong is WHICH pounds: a household's own settled trailing-year bill
        # is a number only its supplier holds, and nothing a household is ever shown is built from
        # it. The published convention -- an annual figure at typical consumption -- is what the
        # cap headline and every comparison listing use, so that is what the decision keys on.
        # The SETTLEMENT is untouched and still bills the true volume at the true rate; the gap
        # between the two is now a real quantity in the world instead of an unmodelled
        # convenience. See `simulation/shown_price.py` and the pre-registration filed before it.
        _segment = next(
            (c.get("segment") for c in customers if c.get("customer_id") == billing_account), None)
        _billed = _annual_bill_and_volume(billing_account, records_so_far, term_start_str)
        _shown_bill = shown_annual_bill_gbp(
            billed_gbp=(_billed or {}).get("gbp"),
            billed_kwh=(_billed or {}).get("kwh"),
            fuels=(_billed or {}).get("fuels"))
        _price_response = churn_position_multiplier(
            felt, annual_bill_gbp=_bill_scale_for(_segment, _shown_bill))
    # Phase MZ: income_stress switching propensity. Layer 2 dimension 3 (2026-07-09): tenure in
    # the same product -- renters switch less (see switching_propensity.py's module note). Order
    # no longer matters here: under competing risks these are hazard INPUTS, not a chain of
    # multiplications into a running probability, so nothing depends on what was applied first.
    if income_stress is not None:
        from simulation.household_segments import tenure_for_customer
        tenure = tenure_for_customer(billing_account).value
        # The same product `switching_propensity.adjust_churn_probability` applies internally and
        # is no longer called from here: C2 treats it as the ACTION PROPENSITY modulator scaling
        # every risk, rather than as the fourth risk the design listed -- high income stress
        # (0.65) and renting (0.75-0.80) make a household leave LESS, and a competing-risks model
        # has no negative hazards. See `simulation/departure_risks.py`.
        _action_propensity = (
            stress_switching_multiplier(income_stress) * tenure_switching_multiplier(tenure)
        )
    # Phase NF: SIM-side satisfaction score. A RISK, not a modulator: it runs 1.30 / 1.00 / 0.85,
    # and the protective 0.85 branch is a smaller dissatisfaction hazard rather than a negative
    # one, so it passes the test income stress fails.
    if satisfaction_score is not None:
        _dissatisfaction_response = satisfaction_churn_multiplier(satisfaction_score)
    # ═══════════════════════════════════════════════════════════════════════════════════════
    # C2 — COMPETING RISKS, AND THE YEAR'S LEVEL IS THE PUBLISHED RECORD'S (2026-08-30)
    # ═══════════════════════════════════════════════════════════════════════════════════════
    #
    # WHAT THIS REPLACED. The five factors above used to be multiplied into one scalar and rolled
    # once. By the time the die was cast the causes were gone, so a departure was not merely
    # unlabelled -- it was UNCAUSED BY CONSTRUCTION, and any reason bolted onto the record could
    # only be a story invented after the roll. Now each risk keeps its own hazard, survival is the
    # product of the survivals, and the risk that fires names the departure. See
    # `simulation/departure_risks.py` for the risk/modulator split and why there are three risks
    # and not the design's four.
    #
    # TWO CHANGES LANDED TOGETHER BECAUSE THE RUN REFUTED HOLDING THEM APART. The intent was to
    # correct the world's departure LEVEL first and change the MECHANISM second, so a level move
    # and a physics change would not land in one churn series and make neither attributable.
    # `56718a719` measured that the level correction is impossible without the mechanism: no single
    # multiplicative scale on the market term reaches the published band (the derived 1.99x puts
    # 2022 at 6.0% against 2.9-4.3% and 2016 at 29.2% against 17.0-17.6%), and the per-year
    # divisors that would fix each year have an empty intersection. There is no run in which they
    # are separable. Attribution is bought a different way instead: the band is an external anchor
    # this tree does not generate, the prediction was filed before the run
    # (`docs/market_research/gb_switching_rate_denominators.md` §8), and the reason mix is
    # published as an interval because its parameter is unidentified.
    #
    # AND THE OLD P0 TARGET WAS CONTAMINATED BY THE DEFECT BEING REMOVED, which is why it is not
    # what this is fitted to. The composed form let `_price_response` scale the BILL-SHOCK term: in
    # 74.4% of these renewals the company is cheaper than the market reference, so being cheaper
    # than average discounted a household's churn from its own bill doubling, by 13% on average.
    # "We are cheaper than average" is not a reason to fail to notice your own bill. Holding the
    # level constant across this change would have PRESERVED that discount, so P0 is restated as a
    # predicted MOVE -- the level lands inside the published band -- and not as an invariance.
    _level_anchor = year_level_anchor(int(term_start_str[:4]))
    _risk_inputs = dict(
        bill_shock_base=_bill_shock_base,
        price_response=_price_response,
        dissatisfaction_response=_dissatisfaction_response,
        market_opportunity=_market_opportunity,
        action_propensity=_action_propensity,
        sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
        shock_weight=DECLARED_SHOCK_WEIGHT,
        level_anchor=_level_anchor,
    )
    # Phase QA: the true PRE-retention-offer probability -- what the company's estimate (computed
    # before any retention decision) is trying to predict. Comparing against a probability that
    # already baked in the company's own intervention would make the company look wrong precisely
    # when its intervention worked. It is a separate `build_departure_risks` call rather than a
    # captured intermediate because the offer now scales ONE hazard, not the total.
    risks_pre_offer = build_departure_risks(
        retention_offer_retained_fraction=1.0, **_risk_inputs)
    effective_p_retain_pre_offer = 1.0 - total_departure_probability(risks_pre_offer)
    # P6, AND IT IS THE FIRST ACTIONABLE CONSEQUENCE IN THIS PROGRAMME. A retention offer is a
    # PRICE cut, so it scales the price-position hazard and nothing else: a discount cannot retain
    # a service-driven churner. The composed form scaled the whole probability, which modelled a
    # world where money buys back a customer who left because we failed them. This moves against
    # the company -- offers retain strictly fewer accounts than they used to -- and the answer to a
    # service-driven churner is now a service intervention, which is a thing a supplier can
    # actually observe about itself.
    risks = build_departure_risks(
        retention_offer_retained_fraction=(
            1.0 - retention_modifier if retention_modifier is not None else 1.0),
        **_risk_inputs)
    effective_p_retain = 1.0 - total_departure_probability(risks)
    # ONE ROLL, SAME DIRECTION AS THE FORM THIS REPLACES: a departure is the upper tail, and the
    # cause is read from WHERE in that tail the roll landed, so it costs no second draw and cannot
    # decorrelate from the departure it explains.
    departed, departure_cause = resolve_departure(risks, roll)
    retained = not departed

    # Phase 7e: when an account churns, roll whether we win the home-mover's
    # business. Separate seed so it never interferes with the churn roll.
    home_move_won = False
    if not retained:
        win_roll = _random.Random(f"win_{billing_account}_{term_start_str}").random()
        home_move_won = win_roll <= renewal_data["win_probability"]

    # Phase 11b: company's observable-data churn estimate
    company_churn_estimate: float | None = precomputed_company_estimate
    churn_estimate_error_pct: float | None = None
    if company_churn_estimate is None and old_rate_gbp_per_mwh is not None and new_rate_gbp_per_mwh is not None:
        acq_date = next(
            (c["acquisition_date"] for c in customers if c["customer_id"] == billing_account),
            term_start_str,
        )
        tenure_years = (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date)).days / 365.25
        company_churn_estimate = round(
            estimate_churn_probability(old_rate_gbp_per_mwh, new_rate_gbp_per_mwh, tenure_years), 4
        )
    # Phase QA: realized_churn_probability is the true, fully-adjusted (passive
    # cap / market conditions / income stress / satisfaction) probability that
    # was actually rolled against, captured BEFORE any retention-offer effect.
    # Prior to this phase, churn_estimate_error_pct compared the company's
    # estimate against renewal_data["churn_probability"] -- the raw, pre-
    # adjustment bill-shock base rate that was never the number the dice roll
    # used. That mismatch was the source of the apparent systematic ~-80%
    # "underestimate" pattern the company's model showed at nearly every
    # renewal: the comparison was against a number the SIM itself discarded.
    realized_churn_probability = round(1.0 - effective_p_retain_pre_offer, 4)
    if company_churn_estimate is not None:
        sim_prob = realized_churn_probability
        if sim_prob:
            churn_estimate_error_pct = round(
                (company_churn_estimate - sim_prob) / sim_prob, 4
            )

    return {
        "customer_id": billing_account,
        "event_date": term_start_str,
        "commodity": commodity,
        "event_type": "renewed" if retained else "churned",
        # THE OCCASION AND THE CAUSE ARE TWO FACTS AND BOTH ARE NOW KNOWN (2026-08-30).
        # Occasion is what brought this account to a decision; it is "renewal" for everything this
        # function emits, and it exists so that a reader whose denominator is renewal DECISIONS can
        # still select its own population once C1b and C6 start emitting departures that are not
        # renewals -- `tools/population_anchor._churn_by_year` divides by `renewals + churns`, and
        # the first non-renewal departure would move that rate with no reader able to say which
        # quantity had changed. Cause is the risk that fired, and it is `None` on a RETENTION for
        # the reason `departure_event` states: a cause on an account that stayed would be a reason
        # mix that no departure supports.
        "departure_occasion": DEPARTURE_OCCASION_RENEWAL,
        "departure_cause": departure_cause,
        "churn_probability": round(renewal_data["churn_probability"], 4),
        "win_probability": round(renewal_data["win_probability"], 4),
        "effective_retention_probability": round(effective_p_retain, 4),
        "realized_churn_probability": realized_churn_probability,
        "random_roll": round(roll, 4),
        "home_move_won": home_move_won,
        "company_churn_estimate": company_churn_estimate,
        "churn_estimate_error_pct": churn_estimate_error_pct,
        "retention_offered": retention_modifier is not None,
        # TWO GENUINELY DIFFERENT QUANTITIES, TWO NAMES (2026-08-28). `..._vs_svt` is this
        # customer's position against the PUBLISHED CAP and is what it has always been -- every
        # consumer that reconciles against `svt_rates` keeps working and stays comparable across
        # this change. `..._vs_market_reference` is the number the churn decision ACTUALLY used,
        # which is the same thing until a competitor reference moves and is the only one that
        # explains the roll after it does. Keeping one name for both is what made
        # `run_price_ladder`'s reconciliation go red at 21.3pp on the day this landed.
        "price_differential_vs_svt": _svt_position(new_rate_gbp_per_mwh, term_start_str),
        "price_differential_vs_market_reference": round(differential, 4) if differential else None,
        "market_reference_gbp_per_mwh": _market_reference_gbp_per_mwh(
            term_start_str, position_ledger=position_ledger,
            wholesale_gbp_per_mwh=wholesale_gbp_per_mwh),
        "offer_position_multiplier": (
            round(offer_position_multiplier(differential), 4) if differential else None
        ),
        "churn_position_multiplier": (
            round(churn_position_multiplier(differential), 4) if differential else None
        ),
        "market_switching_multiplier": round(market_switching_multiplier(market_year), 4) if market_year is not None else None,
        # C2 FACTOR DECOMPOSITION -- SIM ground truth, never readable by company/** decision code
        # (pinned by tests/architecture). These are the hazard inputs the competing-risks form
        # consumes, published so that the departure decomposition is reproducible from the event
        # log alone rather than only from a re-run.
        "sim_bill_shock_base": round(_bill_shock_base, 6),
        "sim_market_opportunity": round(_market_opportunity, 6),
        "sim_price_response": round(_price_response, 6),
        "sim_action_propensity": round(_action_propensity, 6),
        "sim_dissatisfaction_response": round(_dissatisfaction_response, 6),
        # The year's level, emitted so the decomposition is reproducible from the log alone. A
        # reader who cannot see it would find the hazards not reconstructing and have no way to
        # tell a level anchor from a defect.
        "sim_level_anchor": round(_level_anchor, 6),
    }
