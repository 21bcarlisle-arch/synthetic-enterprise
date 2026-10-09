"""B8: the coin-drawn decision set -- a holdout the company can learn a retention offer's effect from.

REUSE: simulation/coin_drawn_decision_set.py
CLASS: CUSTOM
INDEX: searched "holdout", "coin", "decision set", "per decision", "counterfactual". The nearest is
       `tools/decision_probe.py`, which asks the world its true P(stay) at two offers on the SAME
       renewal by re-asking `roll_lifecycle_event` with only the rate changed. That is REUSED here
       as the question, not paralleled: this module asks it the same way. What the probe cannot
       do is supply the decisions -- it needs a full settled run for its book, and a settled
       customer-year costs ~2.7 MB (SEAT_REPLY 2026-10-07 11:52), so the thousands of decisions
       per arm a holdout needs do not fit in memory. `simulation.population_draw.draw_population`
       supplies the households, `company.interfaces.supply_book.register_drawn_points` registers
       them exactly as a run registers its drawn points, and `gas_settlement`'s revenue shape
       (kWh x rate + the daily standing charge, ex VAT) is what each lean day record carries.

WHY (director, 2026-10-07 14:54). Measuring whether a POLICY creates value needs no coin: the probe
scores both options on one customer at one moment. But the company LEARNING an offer's effect from
its own record is part of the method we sell, and there the coin is the subject: the company sees
only who stayed, so it needs thousands of randomised decisions per arm. `3811342db` found the
settled book can never supply them (31 renewals in band in ten years against ~392 per side, and an
offer rule that is a deterministic function of the belief, so nothing is identified). This builds
the set the lean way, as he chose: draw households, ask the world each one's chance of staying at
its offer, and flip a seeded coin per renewal decision.

WHAT "THE OFFER" IS. A cut in the unit rate at renewal, read through the world's own price-response
curve -- the curve the four probe outputs used. Both arms are offered the world's published default
for the fuel, ex VAT; the treated arm is offered `cut_gbp_per_mwh` below it. The run loop's other
retention route, `RETENTION_EFFECTIVENESS = 0.20` scaling departure risk, is NOT used: it is
unsourced, and `3811342db` declined to adopt it. So the world's true effect here is
P(stay | default - cut) - P(stay | default), per decision, and the company never reads it.

THE COIN is the company's own randomiser, drawn from the named substream `HOLDOUT_SUBSTREAM` keyed
on (seed, account, decision date) and NOTHING the world knows, so the arm at a decision is
independent of the household's state at that decision. It is flipped at EVERY renewal: a household
that stays renews again a year later and is drawn again, and the rate it agreed is its next year's
history. A household that leaves is gone.

THE HISTORY (the cost the reply left open). The world's departure roll reads a household's trailing
settled record: monthly bills for the bill-shock event (`experienced_bill_shock`) and the trailing
year's revenue for the scale the price move is felt against (`_annual_bill_gbp`). Neither needs a
half-hour: both sum `revenue_gbp` by month or by year. So the lean history is ONE record per day per
household -- consumption, unit rate, revenue -- over the trailing `HISTORY_DAYS`, which covers the
year-on-year comparison and nothing more. Cost per decision is measured by `build_decision_set`
and returned with the set, never assumed.

THE SAVE ON A LOSS NOTICE (director, 2026-10-08) is asked of the same roll, so it adds no number.
A household leaves at the default iff its roll U > P(stay | default). If the company answers its
loss notice with a Fixed Retention Tariff `c` below the default, the household is saved iff
U <= P(stay | default - c): the same U, the world's own curve, nothing new. So the conditional
save rate is (P(stay|default-c) - P(stay|default)) / (1 - P(stay|default)) -- the world's OUTPUT,
which is what lets a published save rate check the world rather than drive it. `probe_cuts` asks
the world P(stay) at each of several cuts on every decision, so one build serves a whole curve.

NAMED SIMPLIFICATIONS, each a place this world is thinner than the settled one:
  * A day's electricity is the EAC / 365, flat through the year. The world has a day form for gas
    (`gas_settlement.resi_daily_gas_kwh`) and none for electricity outside the half-hourly shape
    path. Season moves a month's bill but not the year-on-year comparison or the annual scale.
  * Electricity only: the draw yields electricity points, so a household's gas leg (which
    `_annual_bill_gbp` would sum) is absent and its felt bill is the electricity bill alone.
  * Held at the world's neutral: the competitor position ledger and the wholesale forward (the
    market reference falls back to the world's own), satisfaction, the passive-churn cap and the
    debt objection. Income stress IS passed, from the drawn premise.
  * `wholesale_cost_gbp` is carried as 0.0. It feeds the company-side exposure measure in
    `saas.customer_reaction` and no departure term; a control proves P(stay) does not move with it.
"""
from __future__ import annotations

import datetime as dt
import math
import random
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, replace

#: The coin's named substream (C-S2): the B8 frame's own name for it.
HOLDOUT_SUBSTREAM = "B8_holdout::assignment"
#: Prefix that keeps the set's households apart from the live book's own `SYN-` draws, which come
#: from the same generator and would otherwise share ids and so share world traits.
ACCOUNT_PREFIX = "HLD"
#: Days of history the world is handed per decision: two years, so this year's bills can be compared
#: with last year's. The departure terms read nothing older.
HISTORY_DAYS = 731
#: The last day a decision may fall on: the end of the world's 2016-2025 record.
LAST_DECISION = dt.date(2025, 12, 31)
FUEL = "electricity"


@dataclass(frozen=True)
class DecisionSet:
    """The drawn decisions with the world's truth on each row, and what building them cost."""

    seed: int
    cut_gbp_per_mwh: float
    planted_effect: float | None
    rows: list = field(repr=False)
    households: int = 0
    day_records_built: int = 0
    seconds: float = 0.0

    @property
    def per_arm(self) -> dict:
        out = {"treated": 0, "holdout": 0}
        for r in self.rows:
            out[r["arm"]] += 1
        return out

    @property
    def true_effect(self) -> float | None:
        """The world's mean effect over the decisions this set holds: what the estimate is graded
        against. Truth, never handed to the company."""
        if not self.rows:
            return None
        return sum(r["p_stay_treated"] - r["p_stay_holdout"] for r in self.rows) / len(self.rows)


def coin_is_treated(seed: int, account: str, decision_date: str, treat_share: float = 0.5) -> bool:
    """The company's coin for one renewal decision: True = offered the cut, False = held out."""
    return random.Random(f"{HOLDOUT_SUBSTREAM}:{seed}:{account}:{decision_date}").random() < treat_share


def saved_on_loss_notice(roll: float, p_stay_default: float, p_stay_at_cut: float) -> bool:
    """Whether a save at a cut keeps this household, asked of the WORLD'S roll and curve: it was
    leaving at the default (roll above P(stay | default)) and would have stayed at the cut's price
    (roll at or below P(stay | default - cut)). A stayer is never 'saved': it was never leaving."""
    return p_stay_default < roll <= p_stay_at_cut


def implied_save_rate(p_stay_default: float, p_stay_at_cut: float) -> float:
    """The world's conditional chance that a leaver at the default is kept by the cut: the share of
    the departure tail the cut moves below the roll line. Zero where the household cannot leave."""
    leave = 1.0 - p_stay_default
    return 0.0 if leave <= 0.0 else max(0.0, p_stay_at_cut - p_stay_default) / leave


def default_offer_ex_vat(day: dt.date) -> float:
    """The world's published default for the fuel on `day`, ex VAT: what both arms are offered."""
    from simulation.customer_events import _household_svt_gbp_per_mwh
    from simulation.svt_product import _ex_vat

    svt = _household_svt_gbp_per_mwh(FUEL, day.isoformat())
    if not svt:
        raise ValueError(f"the world publishes no {FUEL} default on {day}: no offer can be set")
    return _ex_vat(svt)


def draw_households(seed: int, *, start_year: int, end_year: int,
                    acquisitions_per_year: float) -> list:
    """Draw domestic households and re-id them under `ACCOUNT_PREFIX`."""
    from simulation.population_draw import draw_population

    return [replace(c, customer_id=f"{ACCOUNT_PREFIX}-{c.customer_id.split('-', 1)[1]}")
            for c in draw_population(seed, start_year=start_year, end_year=end_year,
                                     acquisitions_per_year_lambda=acquisitions_per_year)
            if c.segment == "resi" and c.commodity == FUEL]


@contextmanager
def registered(households: list):
    """Register the households on the book the way a run registers its drawn points, so the
    world's per-household traits answer for them, and take back exactly those on the way out: a
    set built inside another process must leave that process's book as it found it."""
    from company.interfaces.supply_book import register_drawn_points, withdraw_drawn_points

    added = {p["customer_id"] for p in register_drawn_points(
        [c.to_customer_dict() for c in households])}
    try:
        yield
    finally:
        withdraw_drawn_points(added)


def lean_day_records(account: str, eac_kwh: float, start: dt.date, end: dt.date,
                     rate_gbp_per_mwh: float) -> list[dict]:
    """One settled-shape record per day on [start, end) at one unit rate: what the world's
    departure terms read of a household's history, without a half-hour in it."""
    from simulation.policy_costs import get_electricity_standing_charge_per_day

    kwh = eac_kwh / 365.0
    out = []
    day = start
    while day < end:
        iso = day.isoformat()
        out.append({
            "customer_id": account, "commodity": FUEL, "settlement_date": iso,
            "consumption_kwh": kwh, "unit_rate_gbp_per_mwh": rate_gbp_per_mwh,
            "revenue_gbp": kwh * rate_gbp_per_mwh / 1000.0
            + get_electricity_standing_charge_per_day(iso, "resi"),
            "wholesale_cost_gbp": 0.0,
        })
        day += dt.timedelta(days=1)
    return out


def monthly_bills(records: list[dict], through: dt.date) -> list[float]:
    """The trailing twelve months' bills, oldest first, ex VAT: what the company billed."""
    by_month: dict[str, float] = {}
    for r in records:
        by_month[r["settlement_date"][:7]] = (by_month.get(r["settlement_date"][:7], 0.0)
                                              + r["revenue_gbp"])
    months = sorted(m for m in by_month if m < through.isoformat()[:7])[-12:]
    return [round(by_month[m], 2) for m in months]


def billed_kwh(records: list[dict], through: dt.date) -> float:
    """The kWh billed over the trailing year before `through`: what a cut per MWh is charged on."""
    since = (through - dt.timedelta(days=365)).isoformat()
    return round(sum(r["consumption_kwh"] for r in records
                     if since <= r["settlement_date"] < through.isoformat()), 1)


def world_renewal(customer, decision_date: dt.date, records: list[dict], old_rate: float,
                  offer: float, passive_churn_cap: float | None = None) -> tuple[float, bool] | None:
    """The world's P(stay) for this household at this renewal at `offer`, and whether it stays,
    asked as the probe asks it: `roll_lifecycle_event` with only the rate varying, so the roll is
    the same at either offer. None where the world has no answer."""
    from simulation.customer_events import roll_lifecycle_event

    stress = getattr(getattr(customer.premise, "household", None), "income_stress", None)
    event = roll_lifecycle_event(
        customer.customer_id, decision_date.isoformat(), FUEL, records,
        [customer.to_customer_dict()], old_rate_gbp_per_mwh=old_rate,
        new_rate_gbp_per_mwh=offer, market_year=decision_date.year, income_stress=stress,
        passive_churn_cap=passive_churn_cap)
    if event is None:
        return None
    return float(event["effective_retention_probability"]), event["event_type"] == "renewed"


def build_decision_set(seed: int, *, cut_gbp_per_mwh: float, planted_effect: float | None = None,
                       treat_share: float = 0.5, start_year: int = 2016, end_year: int = 2024,
                       acquisitions_per_year: float = 100.0,
                       probe_cuts: tuple[float, ...] = ()) -> DecisionSet:
    """Draw households and walk each through its renewals, one coin per decision.

    `cut_gbp_per_mwh` 0 is the NULL arm (the treated offer is the holdout offer, so the true effect
    is exactly zero). `planted_effect` is the PLANTED arm: the treated household stays with the
    world's holdout probability plus this, at the holdout's rate, so the truth is known by
    construction and the world's curve is not involved.

    `probe_cuts` re-asks the world on every decision at the default minus each cut, with only the
    rate changed, and keeps P(stay) and the world's own stay/leave per cut on the row (`p_stay_at_cut`,
    `stays_at_cut`, world truth). It does not
    change the path: the household still lives at the offer its coin drew.
    """
    from simulation.customer_events import churn_roll_for_renewal

    t0 = time.perf_counter()
    households = draw_households(seed, start_year=start_year, end_year=end_year,
                                 acquisitions_per_year=acquisitions_per_year)
    rows: list[dict] = []
    built = 0
    with registered(households):
        for c in households:
            joined = dt.date.fromisoformat(c.acquisition_date)
            rate = default_offer_ex_vat(joined)
            records = lean_day_records(c.customer_id, c.eac_kwh, joined,
                                       joined + dt.timedelta(days=365), rate)
            built += len(records)
            decision = joined + dt.timedelta(days=365)
            while decision <= LAST_DECISION:
                iso = decision.isoformat()
                holdout_offer = default_offer_ex_vat(decision)
                treated_offer = holdout_offer - cut_gbp_per_mwh if planted_effect is None else holdout_offer
                hold = world_renewal(c, decision, records, rate, holdout_offer)
                if hold is None:
                    break
                p_hold, stays_held_out = hold
                roll = churn_roll_for_renewal(c.customer_id, iso)
                if planted_effect is not None:
                    # The world's own rule is stay iff roll <= P(stay); a control holds that on the
                    # holdout rows, which is what lets the planted arm reuse the same roll.
                    p_treat = min(1.0, max(0.0, p_hold + planted_effect))
                    stays_treated = roll <= p_treat
                elif cut_gbp_per_mwh == 0:
                    p_treat, stays_treated = p_hold, stays_held_out
                else:
                    p_treat, stays_treated = world_renewal(c, decision, records, rate, treated_offer)
                at_cut, stays_at_cut = {}, {}
                for pc in probe_cuts:
                    asked = world_renewal(c, decision, records, rate, holdout_offer - pc)
                    at_cut[pc], stays_at_cut[pc] = asked if asked is not None else (None, None)
                treated = coin_is_treated(seed, c.customer_id, iso, treat_share)
                stayed = stays_treated if treated else stays_held_out
                offer = treated_offer if treated else holdout_offer
                rows.append({
                    "account": c.customer_id, "decision_date": iso,
                    "arm": "treated" if treated else "holdout",
                    "offer_unit_rate": round(offer, 4), "stayed": stayed,
                    "payment_method": c.payment_method,
                    # The product the account OPENED on: "svt" for a deemed-contract move-in, None
                    # where the draw cannot establish it (not "fixed": see `_draw_tariff_type`).
                    "opened_on": c.tariff_type,
                    # This set never walks the default tariff or an active renewal, so the two
                    # positions are unknown here, not zero: `build_funnel_decision_set` walks both.
                    "acquisition_route": ROUTE_MOVE_IN if c.tariff_type == "svt" else None,
                    "days_on_default": None, "ever_actively_renewed": None,
                    "monthly_bills": monthly_bills(records, decision),
                    "billed_kwh": billed_kwh(records, decision),
                    # WORLD TRUTH below this line: the seam's allow-list never passes it.
                    "p_stay_holdout": p_hold, "p_stay_treated": p_treat, "roll": roll,
                    "p_stay_at_cut": at_cut, "stays_at_cut": stays_at_cut,
                })
                if not stayed:
                    break
                rate = offer
                year = lean_day_records(c.customer_id, c.eac_kwh, decision,
                                        decision + dt.timedelta(days=365), rate)
                built += len(year)
                records = (records + year)[-HISTORY_DAYS:]
                decision += dt.timedelta(days=365)
    return DecisionSet(seed=seed, cut_gbp_per_mwh=cut_gbp_per_mwh, planted_effect=planted_effect,
                       rows=rows, households=len(households), day_records_built=built,
                       seconds=time.perf_counter() - t0)


# --- The funnel-sourced set (director ruling 2, 2026-10-08) -------------------------------------
#
# WHY A SECOND SOURCE. `build_decision_set` draws from `draw_population`, which never passes through
# the growth campaign, so option 1 on and off built byte-identical sets on seeds 101 and 202
# (`docs/staging/SEAT_FINDING_B8S_DECISION_SET_CANNOT_SEE_ACQUISITION_SELECTION_SO_P1_P4_ARE_UNGRADED
# _2026-10-09.md`). This one takes the households the campaign's funnel WON, at the date it won them,
# beside the drawn trickle it competes with for the same stock, and walks each one's renewals the way
# the run's renewal builder does, so a household can roll off a fix onto the default and back.
#
# THE IDS ARE KEPT, NOT RE-PREFIXED. Option 1 selects on each prospect's own latent elasticity and
# engagement, both keyed on its id; a winner re-id'd here would carry a fresh draw of both and the
# selection would be erased on the way in. The set is built in its own process, which holds no live
# book whose ids could collide.
#
# THE WALK, step for step against `run_phase2b`'s renewal builders:
#   * A campaign win opens on a fix (it chose a deal). A trickle move-in opens on the default
#     (`opened_on == "svt"`); the rest of the trickle open on a fix, as the run's builder treats them.
#   * At each anniversary the world rolls `rolls_active_renewal` with the household's own
#     `active_renewal_probability_for_customer`. Off a FIX that anniversary is a rolled renewal
#     point, and it is the company's decision: one coin, the cut or the default, and the world's
#     `roll_lifecycle_event` with the passive cap `passive_churn_cap_for(active)`. A stayer that was
#     active takes the offered fix; a passive one rolls onto the default at the default's rate.
#   * Off the DEFAULT the anniversary carries no departure roll (`departure_rolled_at_renewal`): an
#     active household converts onto a fix at the default's price and a passive one stays.
#   * A year on the default carries the C1b inertia hazard, asked of the run's own terms
#     (`inertia_hazard_for_term`, `build_departure_risks` with no price or shock term, the run's
#     `svt_inertia_{account}_{date}` roll). No coin: it is not a renewal point.
#
# NAMED SIMPLIFICATIONS beyond the module's own:
#   * The active-renewal seed is the household's anniversary count, where the run uses
#     `len(schedule)`, which an SVT stint advances by its cap segments. Same probability, different
#     draw: this is the run's rule, not the run's sequence.
#   * A year on the default is ONE hazard segment, where the run splits it at cap periods.
#   * No contact reaches a household on the default, so the C1b contact response is not asked.
#   * Founders are not in the set: they joined before any route the company acts on.

#: The route a household joined by, as the company recorded it. A campaign win came through the
#: company's own funnel; a move-in arrived on a deemed contract. The rest of the trickle carry None:
#: the draw cannot establish their route (`population_draw._draw_tariff_type`), and None is not a
#: route.
ROUTE_CAMPAIGN_WIN = "campaign_win"
ROUTE_MOVE_IN = "move_in"


def campaign_households(seed: int) -> list[tuple]:
    """(household, acquisition route) for every domestic electricity household the growth campaign's
    funnel won at `seed`, dated the day it was won, then the drawn trickle beside it."""
    from simulation.live_population import _drawn_trickle, _pre_growth_book, _resolve_campaign

    # No settlement ceiling: it samples the wins for a half-hourly run this set does not make.
    outcome = _resolve_campaign(_pre_growth_book(seed), seed, persist=False,
                                customer_year_budget=math.inf)
    if len(outcome["winners"]) != outcome["funnel_wins"]:
        raise ValueError(f"the campaign settled {len(outcome['winners'])} of its "
                         f"{outcome['funnel_wins']} funnel wins with no ceiling: the set would be a sample")
    won = [(replace(p, acquisition_date=on.isoformat()), ROUTE_CAMPAIGN_WIN)
           for p, on in outcome["winners"]]
    trickle = [(c, ROUTE_MOVE_IN if c.tariff_type == "svt" else None) for c in _drawn_trickle(seed)]
    return [(c, route) for c, route in won + trickle
            if c.segment == "resi" and c.commodity == FUEL]


@contextmanager
def world_seed(seed: int):
    """Make `seed` this process's run seed while the set is built, so the per-household traits the
    renewal roll reads are the ones the campaign selected on at the same seed."""
    import simulation.live_population as lp

    before = lp._RUN_BASE_SEED
    lp._RUN_BASE_SEED = seed
    try:
        yield
    finally:
        lp._RUN_BASE_SEED = before


def default_year_departs(customer, start: dt.date, stint_start: dt.date) -> tuple[float, bool]:
    """The world's chance this household leaves during the year on the default from `start`, and
    whether it does: the C1b inertia hazard as the run asks it, with no contact."""
    from simulation.departure_level_anchor import year_level_anchor
    from simulation.departure_risks import (
        DECLARED_SENSITIVITY_SCALE,
        build_departure_risks,
        total_departure_probability,
    )
    from simulation.household_segments import engagement_level_for_customer, tenure_for_customer
    from simulation.svt_product import SVT_TARIFF_TYPE, inertia_hazard_for_term
    from simulation.switching_propensity import (
        stress_switching_multiplier,
        tenure_switching_multiplier,
    )

    account = customer.customer_id
    hazard = inertia_hazard_for_term(
        {"tariff_type": SVT_TARIFF_TYPE, "acquisition_date": start.isoformat(),
         "term_end": (start + dt.timedelta(days=365)).isoformat()},
        stint_start=stint_start.isoformat(),
        engagement_level=engagement_level_for_customer(account).value)
    stress = getattr(getattr(customer.premise, "household", None), "income_stress", None)
    propensity = (stress_switching_multiplier(stress)
                  * tenure_switching_multiplier(tenure_for_customer(account).value)
                  if stress is not None else 1.0)
    p = total_departure_probability(build_departure_risks(
        bill_shock_base=0.0, price_response=0.0, dissatisfaction_response=0.0,
        action_propensity=propensity, sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
        level_anchor=year_level_anchor(start.year), svt_inertia=hazard))
    return p, random.Random(f"svt_inertia_{account}_{start.isoformat()}").random() < p


def build_funnel_decision_set(seed: int, *, cut_gbp_per_mwh: float, treat_share: float = 0.5,
                              households: list[tuple] | None = None) -> DecisionSet:
    """The campaign's won households and the trickle, walked through fixes and the default, one coin
    per renewal point. Rows carry `acquisition_route`, `days_on_default` (days on the default tariff
    before this decision, over the account's life) and `ever_actively_renewed` (an active renewal or
    a conversion off the default before this decision) beside the module's own observables."""
    from simulation.household_segments import active_renewal_probability_for_customer
    from simulation.renewal_engagement import passive_churn_cap_for, rolls_active_renewal

    t0 = time.perf_counter()
    with world_seed(seed):
        pairs = households if households is not None else campaign_households(seed)
        rows: list[dict] = []
        built = 0
        with registered([c for c, _ in pairs]):
            for c, route in pairs:
                account = c.customer_id
                joined = dt.date.fromisoformat(c.acquisition_date)
                on_default = c.tariff_type == "svt" and route == ROUTE_MOVE_IN
                rate = default_offer_ex_vat(joined)
                records: list[dict] = []
                days_on_default, ever_active, stint_start = 0, False, joined
                start, term = joined, 0
                while True:
                    year = lean_day_records(account, c.eac_kwh, start,
                                            start + dt.timedelta(days=365), rate)
                    built += len(year)
                    records = (records + year)[-HISTORY_DAYS:]
                    if on_default:
                        _p, departs = default_year_departs(c, start, stint_start)
                        if departs:
                            break
                        days_on_default += 365
                    decision = start + dt.timedelta(days=365)
                    if decision > LAST_DECISION:
                        break
                    iso = decision.isoformat()
                    term += 1
                    active = rolls_active_renewal(iso, f"{account}_{term}",
                                                  active_renewal_probability_for_customer(account))
                    holdout_offer = default_offer_ex_vat(decision)
                    if on_default:
                        if active:
                            on_default, ever_active, rate = False, True, holdout_offer
                        else:
                            rate = holdout_offer
                        start = decision
                        continue
                    cap = passive_churn_cap_for(active)
                    treated_offer = holdout_offer - cut_gbp_per_mwh
                    hold = world_renewal(c, decision, records, rate, holdout_offer, cap)
                    if hold is None:
                        break
                    p_hold, stays_held_out = hold
                    if cut_gbp_per_mwh == 0:
                        p_treat, stays_treated = p_hold, stays_held_out
                    else:
                        p_treat, stays_treated = world_renewal(c, decision, records, rate,
                                                               treated_offer, cap)
                    treated = coin_is_treated(seed, account, iso, treat_share)
                    stayed = stays_treated if treated else stays_held_out
                    offer = treated_offer if treated else holdout_offer
                    rows.append({
                        "account": account, "decision_date": iso,
                        "arm": "treated" if treated else "holdout",
                        "offer_unit_rate": round(offer, 4), "stayed": stayed,
                        "payment_method": c.payment_method, "opened_on": c.tariff_type,
                        "acquisition_route": route, "days_on_default": days_on_default,
                        "ever_actively_renewed": ever_active,
                        "monthly_bills": monthly_bills(records, decision),
                        "billed_kwh": billed_kwh(records, decision),
                        # WORLD TRUTH below this line: the seam's allow-list never passes it.
                        "p_stay_holdout": p_hold, "p_stay_treated": p_treat,
                        "roll": churn_roll_for_renewal_of(account, iso), "active_renewal": active,
                    })
                    if not stayed:
                        break
                    if active:
                        ever_active, rate = True, offer
                    else:
                        on_default, stint_start, rate = True, decision, holdout_offer
                    start = decision
    return DecisionSet(seed=seed, cut_gbp_per_mwh=cut_gbp_per_mwh, planted_effect=None,
                       rows=rows, households=len(pairs), day_records_built=built,
                       seconds=time.perf_counter() - t0)


def churn_roll_for_renewal_of(account: str, iso: str) -> float:
    from simulation.customer_events import churn_roll_for_renewal

    return churn_roll_for_renewal(account, iso)
