"""Phase QD -- shared payment-outcome and arrears-escalation engine.

Single source of truth for "does this invoice get paid, and if not, does the
arrears case eventually resolve or get written off" -- consumed by both:

  - `tools.generate_billing_ledger` (per-customer invoice/payment ledger), and
  - `simulation.run_phase4c_on_phase2b` (emergent bad debt fed into the board
    P&L's `bad_debt_gbp` / `net_margin_gbp`, replacing the flat
    `saas.cost_to_serve.get_bad_debt_rate()` formula that previously stood in
    for simulated payment behaviour).

Before this phase these were two independently-calibrated RNG-driven models
that happened to use similar probabilities. Moving the primitives here and
having both callers iterate the same `bills` in the same sorted order with a
single seeded RNG means they draw the identical sequence of outcomes -- the
ledger and the P&L bad debt figure are now provably the same source of truth.

Payment method / outcome probabilities:
  I&C / SME (BACS/CHAPS) -- 92% on-time, 7.3% late, 0.7% formal dispute.
  Residential (direct debit) -- driven by income_stress_trajectory:
    LOW -> 92% on-time, 3% DD failure; MODERATE -> 50% / 12%; HIGH -> 10% / 35%.

Arrears escalation (opened the day payment fails):
  Residential:  DD_FAILED -> FIRST_NOTICE(+7d) -> SECOND_NOTICE(+21d)
                -> RESOLVED(+45d) | WRITTEN_OFF(+90d)
  I&C dispute:  INVOICE_DISPUTED -> DISPUTE_NOTICE(+14d)
                -> PAYMENT_PLAN_AGREED(+30d) | WRITTEN_OFF(+60d)

A case resolves if the customer is retained past the case's lifetime, and is
written off if the customer has churned by the end of the run -- the same
"eventually_resolved = cid not in churned" rule Phase PP established.

Phase [debt-branch, docs/design/PROCESS_MODEL.md Section 4] -- debt as a
process past write-off. Every WRITTEN_OFF case is further classified by a
hidden (SIM-side only) behavioural archetype derived from the customer's
income_stress_trajectory shape, then followed through a DCA placement /
recovery-or-sale terminal stage:
  WRITTEN_OFF -> PLACED_WITH_DCA(+30d) -> RECOVERED(+180d) [OVERWHELMED/NEUTRAL]
                                        -> SOLD(+90d)       [AVOIDANT]
`debt_archetype()` is never exposed to company/ code -- only its exhaust (the
stage notes' GBP figures) is company-observable, same epistemic split as the
rest of this engine. See docs/market_research/ASSUMPTIONS.md "Customer &
Portfolio" section for the recovery-rate/commission/haircut sourcing and
caveats (all flagged unverified/illustrative -- genuine research gaps, not
load-bearing precision).
"""
from __future__ import annotations

import random
from datetime import date, timedelta

PAYMENT_TERMS_DAYS = 14

_DD_FAILURE_PROB = {"LOW": 0.03, "MODERATE": 0.12, "HIGH": 0.35}
_ON_TIME_PROB = {"LOW": 0.92, "MODERATE": 0.50, "HIGH": 0.10}
_LATE_DAYS = {"LOW": (3, 14), "MODERATE": (14, 45), "HIGH": (30, 90)}

_CORP_BACS_ON_TIME_PROB = 0.92
_CORP_BACS_LATE_PROB = 0.073
_CORP_BACS_DISPUTE_PROB = 0.007
_CORP_LATE_DAYS = (14, 45)
_IC_SEGMENTS = ("ic", "I&C")

# Phase [debt-branch] -- post-write-off DCA placement / recovery / sale.
# Figures sourced/caveated in docs/market_research/ASSUMPTIONS.md "Customer &
# Portfolio" (2026-07-05 rows); all illustrative/unbenchmarked unless noted.
DCA_PLACEMENT_DAYS = 30          # WRITTEN_OFF -> PLACED_WITH_DCA (illustrative, unbenchmarked -- see ASSUMPTIONS.md)
DCA_OUTCOME_DAYS = 180           # PLACED_WITH_DCA -> RECOVERED (illustrative)
DEBT_SALE_DAYS = 90              # PLACED_WITH_DCA -> SOLD (illustrative)
DCA_RECOVERY_RATE = {"OVERWHELMED": 0.30, "NEUTRAL": 0.20, "AVOIDANT": 0.20}  # AVOIDANT never reaches RECOVERED so its rate is unused, kept for completeness
DCA_COMMISSION_RATE = 0.15       # contingency fee deducted from recovered amount
DEBT_SALE_HAIRCUT_PCT = 0.12     # proceeds as % of face value when sold


def stress_for_year(behavioral: dict, year: int) -> str:
    trajectory = behavioral.get("income_stress_trajectory") or []
    for entry in trajectory:
        if entry.get("year") == year:
            return (entry.get("stress") or "LOW").upper()
    return "LOW"


def _trajectory_stress_in_year(trajectory: list[dict], year: int) -> str:
    """Same lookup style as stress_for_year(), but over a raw trajectory list
    (debt_archetype() is called both from generate_billing_ledger.py, which
    already has the raw trajectory in hand, and from compute_debt_recovery(),
    which looks it up from the behavioral dict itself)."""
    for entry in trajectory or []:
        if entry.get("year") == year:
            return (entry.get("stress") or "LOW").upper()
    return "LOW"


def debt_archetype(trajectory: list[dict], year: int) -> str:
    """Classify a customer's behavioural response to arrears, from their
    income_stress_trajectory shape alone (SIM-side hidden state -- the
    company never sees this label, only its exhaust via the stage notes).

    OVERWHELMED: stress this year is MODERATE/HIGH but was LOW the prior
    year -- recent-onset stress, "overwhelmed not delinquent" (the pitch's
    Stockport case). More likely to engage with a DCA payment plan.
    AVOIDANT: stress has been HIGH for 2+ consecutive years up to and
    including this year -- persistent stress, contact avoidance sets in.
    More likely to have the debt sold rather than worked by a DCA.
    NEUTRAL: neither pattern -- default/blended treatment.
    """
    cur = _trajectory_stress_in_year(trajectory, year)
    prev = _trajectory_stress_in_year(trajectory, year - 1)

    if cur in ("MODERATE", "HIGH") and prev == "LOW":
        return "OVERWHELMED"

    # Persistent-HIGH run ending at `year`, looking back as far as year - 2
    # (three data points) to measure "2+ consecutive years" robustly.
    run_length = 0
    for offset in range(3):
        if _trajectory_stress_in_year(trajectory, year - offset) == "HIGH":
            run_length += 1
        else:
            break
    if run_length >= 2:
        return "AVOIDANT"

    return "NEUTRAL"


def _dca_recovered_amount(arrears_gbp: float, archetype: str) -> float:
    rate = DCA_RECOVERY_RATE.get(archetype, DCA_RECOVERY_RATE["NEUTRAL"])
    return round(arrears_gbp * rate * (1 - DCA_COMMISSION_RATE), 2)


def _debt_sale_proceeds(arrears_gbp: float) -> float:
    return round(arrears_gbp * DEBT_SALE_HAIRCUT_PCT, 2)


def _post_writeoff_stages(arrears_gbp: float, write_off_date: date, archetype: str) -> list[dict]:
    """Stages appended AFTER WRITTEN_OFF -- never changes the WRITTEN_OFF
    stage itself (date/position), only extends the cascade past it."""
    dca_date = write_off_date + timedelta(days=DCA_PLACEMENT_DAYS)
    stages = [{"stage": "PLACED_WITH_DCA", "date": dca_date.isoformat(),
               "note": "Debt placed with third-party debt collection agency"}]
    if archetype == "AVOIDANT":
        sold_date = dca_date + timedelta(days=DEBT_SALE_DAYS)
        proceeds = _debt_sale_proceeds(arrears_gbp)
        stages.append({
            "stage": "SOLD", "date": sold_date.isoformat(), "amount_gbp": proceeds,
            "note": "Debt sold to purchaser -- GBP%.2f proceeds at %d%% of face value"
                    % (proceeds, int(round(DEBT_SALE_HAIRCUT_PCT * 100))),
        })
    else:
        recovered_date = dca_date + timedelta(days=DCA_OUTCOME_DAYS)
        rate = DCA_RECOVERY_RATE.get(archetype, DCA_RECOVERY_RATE["NEUTRAL"])
        net = _dca_recovered_amount(arrears_gbp, archetype)
        stages.append({
            "stage": "RECOVERED", "date": recovered_date.isoformat(), "amount_gbp": net,
            "note": "DCA recovered GBP%.2f net of commission (%d%% recovery rate, %d%% commission)"
                    % (net, int(round(rate * 100)), int(round(DCA_COMMISSION_RATE * 100))),
        })
    return stages


def payment_method(segment: str, amount_gbp: float, customer_id: str | None = None,
                    fuel: str = "electricity") -> str:
    """`customer_id`/`fuel` are optional and keyword-only in practice --
    default None preserves the original flat "every resi customer is on
    direct debit" behaviour exactly. When a customer_id is supplied for a
    resi customer, the real DD/non-DD population mix from
    `simulation.household_segments.payment_channel_for_customer()` is used
    instead (2026-07-09, closes the named gap in
    docs/market_research/ASSUMPTIONS.md's "Household Segment & Psychology"
    section: payment_method() was segment-aware but not archetype-aware
    within resi)."""
    if segment in _IC_SEGMENTS:
        return "chaps" if amount_gbp >= 10000 else "bacs"
    if segment == "sme":
        return "bacs"
    if customer_id is not None:
        from simulation.household_segments import payment_channel_for_customer
        return payment_channel_for_customer(customer_id, fuel).value
    return "direct_debit"


def _fuel_poor_for_bill(method: str, customer_id: str | None) -> bool:
    """Resolve the fuel-poverty flag for a resi bill's payment_outcome() call
    -- resi-only concept (bacs/chaps corp methods never apply), and only
    meaningful once a customer_id is known (mirrors payment_method()'s own
    optional-customer_id convention)."""
    if customer_id is None or method not in ("direct_debit", "standard_credit"):
        return False
    from simulation.household_segments import PaymentChannel, fuel_poverty_for_customer
    channel = PaymentChannel.DIRECT_DEBIT if method == "direct_debit" else PaymentChannel.STANDARD_CREDIT
    return fuel_poverty_for_customer(customer_id, channel)


def _tone_for_bill(method: str, customer_id: str | None, period_end: str) -> str | None:
    """Resolve the debt-collection letter tone for a resi bill's
    payment_outcome() call (2026-07-10, NUDGE_PHYSICS.md remaining
    mechanism) -- resi-only, and only meaningful once a customer_id is
    known. Reads the company's own CURRENT_POLICY.tone_mode choice
    (company/policy/decision_policy.py::tone_for) -- the SIM legitimately
    consumes the company's own chosen attribute here (same precedent as
    simulation/run_phase2b.py's framing_type_for() call), it is not a wall
    violation to read what the company itself decided."""
    if customer_id is None or method not in ("direct_debit", "standard_credit"):
        return None
    from company.policy.decision_policy import CURRENT_POLICY, tone_for
    return tone_for(CURRENT_POLICY, customer_id, period_end)


FUEL_POVERTY_DD_FAIL_MULTIPLIER = 1.3
FUEL_POVERTY_ON_TIME_MULTIPLIER = 0.9


def payment_outcome(method: str, stress: str, rng: random.Random, segment: str = "resi",
                     fuel_poor: bool = False, tone: str | None = None,
                     customer_id: str | None = None):
    """Returns (outcome, days_late). outcome is one of success/failed/dispute.

    `fuel_poor` is optional -- default False preserves the exact original
    behaviour. When True (2026-07-09, Layer 2 dimension 2 -- fuel poverty
    correlates with payment difficulty in the real DESNZ data this codebase
    already anchors household_segments.py's fuel-poverty flag to), the
    DD-failure probability is nudged up and the on-time probability nudged
    down by FUEL_POVERTY_DD_FAIL_MULTIPLIER/FUEL_POVERTY_ON_TIME_MULTIPLIER.
    These multipliers are a calibration CHOICE (NOT independently sourced --
    the DESNZ anchor is a population fuel-poverty RATE, not a payment-outcome
    multiplier), kept modest and capped at 1.0, per the Anchored-noise law.

    `tone`/`customer_id` are optional -- default None preserves the exact
    original behaviour (2026-07-10, NUDGE_PHYSICS.md remaining mechanism:
    debt-collection letter tone/framing). Represents the company's chosen
    dunning-communication style ("empathetic_toned"/"firm_toned") as a
    company-wide policy attribute (company/policy/decision_policy.py::
    tone_for()) -- not a claim that one specific letter caused one specific
    payment, but that a customer's hidden responsiveness to that general
    communication style (simulation/nudge_physics.py::
    tone_effectiveness_multiplier, hidden from the company) nudges their
    overall on-time probability. Cabinet Office/BIT anchor: +3 to +10pp."""
    if method in ("bacs", "chaps"):
        if segment in _IC_SEGMENTS:
            r = rng.random()
            if r < _CORP_BACS_ON_TIME_PROB:
                return ("success", 0)
            elif r < 1.0 - _CORP_BACS_DISPUTE_PROB:
                return ("success", rng.randint(*_CORP_LATE_DAYS))
            else:
                return ("dispute", 0)
        return ("success", 0)
    dd_fail_prob = _DD_FAILURE_PROB.get(stress, 0.03)
    on_time_prob = _ON_TIME_PROB.get(stress, 0.92)
    if fuel_poor:
        dd_fail_prob = min(1.0, dd_fail_prob * FUEL_POVERTY_DD_FAIL_MULTIPLIER)
        on_time_prob = min(1.0, on_time_prob * FUEL_POVERTY_ON_TIME_MULTIPLIER)
    if tone is not None and customer_id is not None:
        from simulation.nudge_physics import tone_effectiveness_multiplier
        on_time_prob = min(1.0, on_time_prob * tone_effectiveness_multiplier(customer_id, tone))
    if rng.random() < dd_fail_prob:
        return ("failed", 0)
    if rng.random() < on_time_prob:
        return ("success", 0)
    lo, hi = _LATE_DAYS.get(stress, (3, 14))
    return ("success", rng.randint(lo, hi))


def arrears_stages(arrears_gbp: float, due_date: date, eventually_resolved: bool,
                    archetype: str = "NEUTRAL") -> list[dict]:
    stages = [
        {"stage": "DD_FAILED", "date": due_date.isoformat(), "note": "Direct debit returned"},
        {"stage": "FIRST_NOTICE", "date": (due_date + timedelta(days=7)).isoformat(),
         "note": "First overdue notice -- GBP%.2f outstanding" % arrears_gbp},
        {"stage": "SECOND_NOTICE", "date": (due_date + timedelta(days=21)).isoformat(),
         "note": "Second notice -- payment plan offered"},
    ]
    if eventually_resolved:
        stages.append({"stage": "RESOLVED", "date": (due_date + timedelta(days=45)).isoformat(),
                        "note": "Arrears cleared via payment plan"})
    else:
        write_off_date = due_date + timedelta(days=90)
        stages.append({"stage": "WRITTEN_OFF", "date": write_off_date.isoformat(),
                        "note": "Debt written off -- bad debt provision raised"})
        stages.extend(_post_writeoff_stages(arrears_gbp, write_off_date, archetype))
    return stages


def ic_arrears_stages(arrears_gbp: float, due_date: date, eventually_resolved: bool,
                       archetype: str = "NEUTRAL") -> list[dict]:
    stages = [
        {"stage": "INVOICE_DISPUTED", "date": due_date.isoformat(),
         "note": "Invoice disputed -- GBP%.2f under formal review" % arrears_gbp},
        {"stage": "DISPUTE_NOTICE", "date": (due_date + timedelta(days=14)).isoformat(),
         "note": "Dispute notice raised -- escalated to accounts receivable"},
    ]
    if eventually_resolved:
        stages.append({"stage": "PAYMENT_PLAN_AGREED",
                        "date": (due_date + timedelta(days=30)).isoformat(),
                        "note": "Payment plan agreed -- arrears to be settled over 60 days"})
    else:
        write_off_date = due_date + timedelta(days=60)
        stages.append({"stage": "WRITTEN_OFF",
                        "date": write_off_date.isoformat(),
                        "note": "Debt written off -- bad debt provision raised"})
        stages.extend(_post_writeoff_stages(arrears_gbp, write_off_date, archetype))
    return stages


def compute_emergent_bad_debt(bills: list[dict], behavioral: dict, churned_ids: set[str],
                               seed: int = 42) -> dict[tuple[str, int], float]:
    """Run the shared payment/arrears model over `bills` and return real,
    emergent bad debt: GBP written off, keyed by (customer_id, write_off_year).

    Iterates `bills` in the exact sorted order and RNG seed that
    `tools.generate_billing_ledger.generate()` uses, so a case that reaches
    WRITTEN_OFF here reaches WRITTEN_OFF there too, for the same GBP amount.
    """
    rng = random.Random(seed)
    result: dict[tuple[str, int], float] = {}
    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        year = int(period_end[:4])

        issue_date = date.fromisoformat(period_end)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)
        stress = stress_for_year(behavioral.get(cid) or {}, year)
        method = payment_method(segment, amount, cid, bill.get("commodity", "electricity"))
        outcome, _days_late = payment_outcome(
            method, stress, rng, segment, _fuel_poor_for_bill(method, cid),
            _tone_for_bill(method, cid, period_end), cid,
        )

        if outcome not in ("failed", "dispute"):
            continue
        will_be_written_off = cid in churned_ids
        if not will_be_written_off:
            continue
        stages = (arrears_stages if outcome == "failed" else ic_arrears_stages)(
            amount, due_date, False
        )
        write_off_date = next(s["date"] for s in stages if s["stage"] == "WRITTEN_OFF")
        key = (cid, int(write_off_date[:4]))
        result[key] = round(result.get(key, 0.0) + amount, 2)
    return result


def apply_emergent_bad_debt(all_records: list[dict], emergent_by_customer_year: dict[tuple[str, int], float]) -> None:
    """Replace the flat-rate `bad_debt_gbp` already baked into `all_records`
    (by `simulation.run_phase2b`'s real-time settlement loop) with the real
    emergent figure from `compute_emergent_bad_debt`, then carry the resulting
    net_margin_gbp delta forward through every later record's cumulative
    `treasury_cash_balance_gbp`. Mutates `all_records` in place.

    Applies each customer-year's correction as a delta on top of whatever
    treasury balance was already recorded, rather than re-deriving the
    portfolio's starting treasury -- that keeps this module decoupled from
    `simulation.run_phase2b`'s constants and correct regardless of exactly
    how `all_records` was accumulated.
    """
    old_by_cy: dict[tuple[str, int], float] = {}
    last_index_by_cy: dict[tuple[str, int], int] = {}
    for i, rec in enumerate(all_records):
        key = (rec["customer_id"], int(rec["settlement_date"][:4]))
        old_by_cy[key] = old_by_cy.get(key, 0.0) + rec.get("bad_debt_gbp", 0.0)
        last_index_by_cy[key] = i

    delta_at_index: dict[int, float] = {}
    for key in set(old_by_cy) | set(emergent_by_customer_year):
        delta = emergent_by_customer_year.get(key, 0.0) - old_by_cy.get(key, 0.0)
        if abs(delta) < 1e-9:
            continue
        idx = last_index_by_cy.get(key)
        if idx is None:
            continue
        delta_at_index[idx] = delta_at_index.get(idx, 0.0) + delta

    cumulative_correction = 0.0
    for i, rec in enumerate(all_records):
        delta = delta_at_index.get(i)
        if delta is not None:
            rec["bad_debt_gbp"] = round(rec.get("bad_debt_gbp", 0.0) + delta, 6)
            rec["net_margin_gbp"] = round(rec["net_margin_gbp"] - delta, 6)
            cumulative_correction -= delta
        if cumulative_correction != 0.0 and "treasury_cash_balance_gbp" in rec:
            rec["treasury_cash_balance_gbp"] = round(rec["treasury_cash_balance_gbp"] + cumulative_correction, 2)



def compute_debt_recovery(bills: list[dict], behavioral: dict, churned_ids: set[str],
                           seed: int = 42) -> dict[tuple[str, int], float]:
    """Run the shared payment/arrears model over `bills` (same sorted order
    and seed as compute_emergent_bad_debt(), so the two line up on the exact
    same set of written-off cases) and return real DCA-recovered / debt-sale
    proceeds, keyed by (customer_id, year of the RECOVERED/SOLD stage --
    NOT the write-off year).

    debt_archetype() is computed from behavioral[cid]["income_stress_trajectory"]
    at the write-off year, to decide which terminal stage (RECOVERED vs SOLD)
    applies and what the proceeds are -- SIM-side only, never exposed past
    this module's own note text.
    """
    rng = random.Random(seed)
    result: dict[tuple[str, int], float] = {}
    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        year = int(period_end[:4])

        issue_date = date.fromisoformat(period_end)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)
        beh = behavioral.get(cid) or {}
        stress = stress_for_year(beh, year)
        method = payment_method(segment, amount, cid, bill.get("commodity", "electricity"))
        outcome, _days_late = payment_outcome(
            method, stress, rng, segment, _fuel_poor_for_bill(method, cid),
            _tone_for_bill(method, cid, period_end), cid,
        )

        if outcome not in ("failed", "dispute"):
            continue
        if cid not in churned_ids:
            continue

        write_off_offset = 90 if outcome == "failed" else 60
        write_off_date = due_date + timedelta(days=write_off_offset)
        trajectory = beh.get("income_stress_trajectory") or []
        archetype = debt_archetype(trajectory, write_off_date.year)

        stages = (arrears_stages if outcome == "failed" else ic_arrears_stages)(
            amount, due_date, False, archetype
        )
        terminal = stages[-1]
        if terminal["stage"] == "SOLD":
            proceeds = _debt_sale_proceeds(amount)
        elif terminal["stage"] == "RECOVERED":
            proceeds = _dca_recovered_amount(amount, archetype)
        else:
            continue
        key = (cid, int(terminal["date"][:4]))
        result[key] = round(result.get(key, 0.0) + proceeds, 2)
    return result


def apply_debt_recovery(all_records: list[dict], recovery_by_customer_year: dict[tuple[str, int], float]) -> None:
    """Apply real DCA-recovered / debt-sale proceeds (compute_debt_recovery())
    as a REDUCTION to `bad_debt_gbp` and a matching INCREASE to
    `net_margin_gbp`, on the last matching record for that customer-year,
    carrying the correction forward through `treasury_cash_balance_gbp` --
    same structural pattern as apply_emergent_bad_debt(), opposite sign.

    Unlike apply_emergent_bad_debt() (which replaces an existing flat-rate
    bad_debt_gbp already baked into all_records with a new emergent figure,
    so the delta is new-minus-old), recovery has no pre-existing baseline to
    replace -- it is a pure addition on top of whatever bad debt is already
    recorded, so the delta applied here is simply the recovered amount
    itself. Cash recovered increases treasury (opposite of the bad-debt
    case, where more bad debt reduces it).
    """
    last_index_by_cy: dict[tuple[str, int], int] = {}
    for i, rec in enumerate(all_records):
        key = (rec["customer_id"], int(rec["settlement_date"][:4]))
        last_index_by_cy[key] = i

    delta_at_index: dict[int, float] = {}
    for key, delta in recovery_by_customer_year.items():
        if abs(delta) < 1e-9:
            continue
        idx = last_index_by_cy.get(key)
        if idx is None:
            continue
        delta_at_index[idx] = delta_at_index.get(idx, 0.0) + delta

    cumulative_correction = 0.0
    for i, rec in enumerate(all_records):
        delta = delta_at_index.get(i)
        if delta is not None:
            rec["bad_debt_gbp"] = round(rec.get("bad_debt_gbp", 0.0) - delta, 6)
            rec["net_margin_gbp"] = round(rec["net_margin_gbp"] + delta, 6)
            cumulative_correction += delta
        if cumulative_correction != 0.0 and "treasury_cash_balance_gbp" in rec:
            rec["treasury_cash_balance_gbp"] = round(rec["treasury_cash_balance_gbp"] + cumulative_correction, 2)
