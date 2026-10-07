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


def world_renewal(customer, decision_date: dt.date, records: list[dict], old_rate: float,
                  offer: float) -> tuple[float, bool] | None:
    """The world's P(stay) for this household at this renewal at `offer`, and whether it stays,
    asked as the probe asks it: `roll_lifecycle_event` with only the rate varying, so the roll is
    the same at either offer. None where the world has no answer."""
    from simulation.customer_events import roll_lifecycle_event

    stress = getattr(getattr(customer.premise, "household", None), "income_stress", None)
    event = roll_lifecycle_event(
        customer.customer_id, decision_date.isoformat(), FUEL, records,
        [customer.to_customer_dict()], old_rate_gbp_per_mwh=old_rate,
        new_rate_gbp_per_mwh=offer, market_year=decision_date.year, income_stress=stress)
    if event is None:
        return None
    return float(event["effective_retention_probability"]), event["event_type"] == "renewed"


def build_decision_set(seed: int, *, cut_gbp_per_mwh: float, planted_effect: float | None = None,
                       treat_share: float = 0.5, start_year: int = 2016, end_year: int = 2024,
                       acquisitions_per_year: float = 100.0) -> DecisionSet:
    """Draw households and walk each through its renewals, one coin per decision.

    `cut_gbp_per_mwh` 0 is the NULL arm (the treated offer is the holdout offer, so the true effect
    is exactly zero). `planted_effect` is the PLANTED arm: the treated household stays with the
    world's holdout probability plus this, at the holdout's rate, so the truth is known by
    construction and the world's curve is not involved.
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
                treated = coin_is_treated(seed, c.customer_id, iso, treat_share)
                stayed = stays_treated if treated else stays_held_out
                offer = treated_offer if treated else holdout_offer
                rows.append({
                    "account": c.customer_id, "decision_date": iso,
                    "arm": "treated" if treated else "holdout",
                    "offer_unit_rate": round(offer, 4), "stayed": stayed,
                    "payment_method": c.payment_method,
                    "monthly_bills": monthly_bills(records, decision),
                    # WORLD TRUTH below this line: the seam's allow-list never passes it.
                    "p_stay_holdout": p_hold, "p_stay_treated": p_treat, "roll": roll,
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
