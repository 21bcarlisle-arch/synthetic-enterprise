"""Phase QD -- shared payment-outcome and arrears-escalation engine.

Single source of truth for "does this invoice get paid, and if not, does the
arrears case eventually resolve or get written off" -- consumed by both:

  - `tools.generate_billing_ledger` (per-customer invoice/payment ledger), and
  - `simulation.run_phase4c_on_phase2b` (emergent bad debt fed into the board
    P&L's `bad_debt_gbp` / `net_margin_gbp`, replacing the flat
    `saas.cost_to_serve.get_bad_debt_rate()` formula that previously stood in
    for simulated payment behaviour).

Before this phase these were two independently-calibrated RNG-driven models
that happened to use similar probabilities. Moving the primitives here made
them one model; what makes the ledger and the P&L bad-debt figure the same
source of truth is that every consumer resolves a given bill's outcome to the
same value.

RNG SUBSTREAM ISOLATION (C-S2, W2_16, 2026-08-08). That agreement used to rest
on every consumer advancing ONE shared `random.Random(seed)` over the same
`bills` in the same sorted order -- so a bill's outcome depended on how many
draws every alphabetically-earlier bill happened to consume. Two things were
wrong with it:

  - It was FRAGILE: improving any one segment's model silently rewrote every
    later customer's history (the W2_sme_segment_case_normalisation fix moved
    resi C7's longest undischarged credit from 1224 days to 32 -- C5/C6 sort
    before C7 and changed their draw count). A baseline that moves whenever an
    unrelated segment improves is one no control can rest on.
  - It was already BROKEN: lockstep is an obligation every consumer had to
    hand-maintain, and `tools.generate_billing_ledger` does not -- it skips
    `payment_outcome` entirely for credit invoices (`amount <= 0`). The real
    run has 24 such bills, the first at sorted index 138 of 1557, so the
    ledger and the P&L drew from streams offset from each other across the
    remaining 91% of bills, and disagreed on the failed/dispute decision for
    42 of them. "Provably the same source of truth" was false.

So a bill's outcome is now drawn from its OWN named, sha256-seeded substream,
keyed by `(customer_id, period_end, commodity)` -- `bill_substream()`. The
outcome is a
pure function of (seed, customer_id, period_end): independent of iteration
order, of how many bills precede it, and of how many draws any other bill or
subsystem consumes. Every consumer therefore agrees BY CONSTRUCTION rather
than by discipline, and a consumer that legitimately skips bills (the ledger's
credit invoices) or filters them (its held-bill validation gate) can no longer
desynchronise anything. Agreeing on each bill's draw is not agreeing on WHICH bills: until
2026-09-28 the engine still resolved held bills and credits the ledger never collects, and wrote
off 6 held bills and two negative credits (£19,135 vs the ledger's £17,359). It now skips both.

Payment method / outcome probabilities:
  I&C / SME (BACS/CHAPS) -- 92% on-time, 7.3% late, 0.7% formal dispute.
  Residential (direct debit) -- driven by income_stress_trajectory:
    LOW -> 92% on-time, 3% DD failure; MODERATE -> 50% / 12%; HIGH -> 10% / 35%.

Arrears escalation (opened the day payment fails):
  Residential:  DD_FAILED -> FIRST_NOTICE(+7d) -> SECOND_NOTICE(+21d)
                -> BALANCE_OPEN | WRITTEN_OFF (the balance-at-close date)
  I&C dispute:  INVOICE_DISPUTED -> DISPUTE_NOTICE(+14d)
                -> BALANCE_OPEN | WRITTEN_OFF (the balance-at-close date)

WHAT IS WRITTEN OFF, AND WHEN (2026-09-27, the balance-at-close rule,
`docs/staging/SEAT_DESIGN_THE_WRITE_OFF_RULE_RE_KEYED_TO_THE_BALANCE_AT_CLOSE_2026-09-27.md`).
A failed or disputed bill is not a terminal case. It adds to the account's
running unpaid balance (`balance_write_offs`). At close -- a churned account's
final bill -- whatever is still unpaid is written off, dated by the labelled C4
convention (`WRITE_OFF_DATE_CONVENTION`). A live balance with no payment for
six years is statute-barred (leg 4a). A stayer's aged arrears cost money
through PROVISION (leg 4b), off by default because its bucket turns on C1, so
`bad_debt_gbp` counts write-offs only (`BAD_DEBT_BASIS`). The rule this replaced wrote off
every failed bill of an eventual leaver at due+90 while it was still on supply.

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

import os
import random
from datetime import date, timedelta

from simulation.rng_substream import substream
from simulation.segment_vocabulary import (
    INDUSTRIAL_AND_COMMERCIAL,
    SME,
    normalise_segment,
)
from simulation.sme_payment_behaviour import sme_payment_outcome

PAYMENT_TERMS_DAYS = 14

#: This subsystem's own RNG namespace (C-S2). Baked into every derived seed so
#: a substream here can never collide with an identically-named substream in
#: another subsystem, even at the same base seed.
STREAM_NAMESPACE = "W2_16_payment_outcome"

#: Substream name for the per-bill payment-outcome draw. A future mechanism in
#: this module gets its outcome by ADDING a name here, never by threading an
#: extra draw through this one -- that is what keeps existing outputs stable.
_PAYMENT_OUTCOME_SUBSTREAM = "payment_outcome"


def _substream(base_seed: int, name: str) -> random.Random:
    """Return an ISOLATED ``random.Random`` for a named mechanism substream.

    Seed is a STABLE sha256 of ``W2_16_payment_outcome::<name>::<base_seed>``
    (never Python's per-process-salted ``hash()``), so the same (base_seed,
    name) yields the same stream in every process -- the hard C-S2 replay
    requirement. Each name seeds an independent generator; a draw here can
    never consume from, or shift, any other substream of this or any other
    subsystem.
    """
    return substream(STREAM_NAMESPACE, name, base_seed)


def bill_substream(base_seed: int, customer_id: str, period_end: str,
                   commodity: str) -> random.Random:
    """The payment-outcome substream for ONE bill, keyed by the bill's own
    identity rather than by its position in an iteration.

    PUBLIC by design: it is the contract every consumer of this engine's
    payment outcomes (`compute_emergent_bad_debt`, `compute_debt_recovery`,
    `tools.generate_billing_ledger`, `simulation.dd_collection_book`) uses to
    resolve a bill. Because the stream is a pure function of
    ``(base_seed, customer_id, period_end, commodity)``, those consumers agree
    on a bill without iterating it in the same order, without visiting the same
    set of bills, and without consuming the same number of draws -- the
    lockstep obligation the shared-stream design imposed on each of them is
    gone.

    `commodity` is REQUIRED, deliberately with no default. It is part of a
    bill's identity: today gas is modelled as its own account (`C1g` beside
    `C1`), so `(customer_id, period_end)` alone is unique across all 1557 real
    bills -- but the moment one account is billed for both fuels in the same
    period, a defaulted/omitted commodity would silently collapse those two
    bills onto ONE stream and tie their outcomes together. That is precisely
    the silent coupling this atom exists to remove, so an un-migrated caller
    fails loudly here instead (the same reasoning that made `method` required
    in `arrears_stages`).
    """
    return _substream(
        base_seed,
        f"{_PAYMENT_OUTCOME_SUBSTREAM}::{customer_id}::{period_end}::{commodity}",
    )


_DD_FAILURE_PROB = {"LOW": 0.03, "MODERATE": 0.12, "HIGH": 0.35}
_ON_TIME_PROB = {"LOW": 0.92, "MODERATE": 0.50, "HIGH": 0.10}
_LATE_DAYS = {"LOW": (3, 14), "MODERATE": (14, 45), "HIGH": (30, 90)}

_CORP_BACS_ON_TIME_PROB = 0.92
_CORP_BACS_LATE_PROB = 0.073
_CORP_BACS_DISPUTE_PROB = 0.007
_CORP_LATE_DAYS = (14, 45)

#: The corporate payment rails. A segment reaching one of these is a business
#: customer, but WHICH business segment still decides the outcome model --
#: I&C and SME are not interchangeable (see `payment_outcome`).
_CORPORATE_METHODS = ("bacs", "chaps")

#: Segment identity is decided by `simulation.segment_vocabulary`, never by a
#: string literal compared here (W2_sme_segment_case_normalisation, completed
#: 2026-08-08). The tuple this replaces -- `_IC_SEGMENTS = ("ic", "I&C")` --
#: was case-SENSITIVE, so a real I&C bill spelled "IC" (the spelling
#: `saas/smart_meter_rollout` uses) matched nothing and was billed as a
#: household; the same defect routed every "SME" bill to the residential rail.
#: Both readers below (`payment_method`, `payment_outcome`) are migrated
#: together and route through the normaliser -- the previous attempt deleted
#: this definition while leaving the readers pointing at it, which killed every
#: run with `NameError: _IC_SEGMENTS` ~180s in. `tools/segment_case_guard.py`
#: fails the commit if a raw segment literal is reintroduced anywhere in
#: `simulation/`, which is what closes the CLASS rather than this instance.

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


# --- public surface for other SIM debt mechanisms to FOLD rather than duplicate
# (W2_12 change-of-tenancy exit debt, simulation/final_bill_outcome.py). These
# are thin, deliberately behaviour-free aliases: a second debt mechanism that
# needs the same DCA/debt-sale cascade or the same stress ladder must reach for
# these, never re-choose its own coefficients, so the two cannot drift apart.

def dca_recovered_amount(arrears_gbp: float, archetype: str) -> float:
    """DCA proceeds on `arrears_gbp` for `archetype`, net of commission."""
    return _dca_recovered_amount(arrears_gbp, archetype)


def debt_sale_proceeds(arrears_gbp: float) -> float:
    """Proceeds from selling `arrears_gbp` of debt at the standing haircut."""
    return _debt_sale_proceeds(arrears_gbp)


def on_time_probability(stress: str) -> float:
    """Population on-time payment probability at an income-stress level."""
    return _ON_TIME_PROB.get((stress or "LOW").upper(), _ON_TIME_PROB["LOW"])


def dd_failure_probability(stress: str) -> float:
    """Population direct-debit failure probability at an income-stress level."""
    return _DD_FAILURE_PROB.get((stress or "LOW").upper(), _DD_FAILURE_PROB["LOW"])


def late_days_band(stress: str) -> tuple[int, int]:
    """(min, max) days late for a late-but-paid bill at an income-stress level."""
    return _LATE_DAYS.get((stress or "LOW").upper(), _LATE_DAYS["LOW"])


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
    canonical = normalise_segment(segment)
    if canonical == INDUSTRIAL_AND_COMMERCIAL:
        return "chaps" if amount_gbp >= 10000 else "bacs"
    if canonical == SME:
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
    known.

    Reads the tone off the company's published collections-communication
    seam (company/interfaces/collections_communication.py), i.e. the world
    learns the tone of a letter that ARRIVED. It deliberately does NOT
    import company.policy.decision_policy: the earlier version of this
    function pulled in CURRENT_POLICY and applied tone_for() itself, and
    its docstring argued that reading "what the company itself decided" was
    not a wall violation. KNIFE pass 3 overruled that argument rather than
    inheriting it (design B5_collections_tone_is_an_event_attribute) -- the
    tone of the letter is observable, but the POLICY OBJECT that chose it,
    with its tone_mode and its A/B cohort split, is the company's internal
    decision machinery and a customer does not read it.

    The APPLICABILITY test below stays here and was deliberately not pushed
    into the seam: which bills involve a dunning letter at all is a fact
    about how this world bills people, not a company decision. The seam
    publishes exactly one thing -- the tone the company chose."""
    if customer_id is None or method not in ("direct_debit", "standard_credit"):
        return None
    from company.interfaces.collections_communication import collections_tone_for
    return collections_tone_for(customer_id, period_end)


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
    company-wide policy attribute, read through the company's published
    seam (company/interfaces/collections_communication.py::
    collections_tone_for) -- not a claim that one specific letter caused one specific
    payment, but that a customer's hidden responsiveness to that general
    communication style (simulation/nudge_physics.py::
    tone_effectiveness_multiplier, hidden from the company) nudges their
    overall on-time probability. Cabinet Office/BIT anchor: +3 to +10pp."""
    if method in _CORPORATE_METHODS:
        canonical = normalise_segment(segment)
        if canonical == INDUSTRIAL_AND_COMMERCIAL:
            r = rng.random()
            if r < _CORP_BACS_ON_TIME_PROB:
                return ("success", 0)
            elif r < 1.0 - _CORP_BACS_DISPUTE_PROB:
                return ("success", rng.randint(*_CORP_LATE_DAYS))
            else:
                return ("dispute", 0)
        if canonical == SME:
            # SME is NOT I&C. Before this branch existed, an SME bill reaching
            # the corporate rail fell through to the bare `("success", 0)`
            # below -- it could never be late, fail, or dispute -- so merely
            # fixing the case bug would have DELETED SME bad debt rather than
            # fixed it. `sme_payment_behaviour` is the separately-anchored
            # outcome model (Ofgem D6 2025 hardship tiers, DBT 2024 aggregate
            # late rate) that has to exist for the case fix to be safe.
            return sme_payment_outcome(rng, customer_id)
        # Unreachable by construction: `payment_method` only returns a
        # corporate method for a business segment. Left as-is rather than
        # raised, so an unforeseen caller degrades exactly as it always has.
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


#: The only method whose failure is a returned Direct Debit. Anything else
#: fails as a payment that did not arrive -- there is no mandate to return.
DD_METHOD = "direct_debit"

#: How a non-DD method's missed payment opens an arrears case. The cascade
#: after this first stage (notices, write-off, DCA) is method-independent: the
#: collections process is the same once the money is late, only the way the
#: money failed to arrive differs.
_NON_DD_OPENING_NOTE = {
    "standard_credit": "Standard credit payment not received",
    "standing_order": "Standing order payment not received",
    "card": "Card payment not received",
    "prepayment": "Prepayment meter -- no vend recorded",
}
_NON_DD_OPENING_NOTE_DEFAULT = "Payment not received"


def opening_arrears_stage(method: str, due_date: date) -> dict:
    """The first arrears stage for `method` -- the ONE stage that is
    method-specific.

    A `DD_FAILED` / "Direct debit returned" stage can only be raised against an
    active Direct Debit Instruction. Emitting it for a standard-credit customer
    is the absurdity atom W2_payment_channel_dd_consistency_invariant closes:
    the customer has no mandate, so nothing exists that could be returned.
    Enforced as a class rule by
    `company.compliance.domain_invariants.check_payment_channel_dd_consistency`.
    """
    if method == DD_METHOD:
        return {"stage": "DD_FAILED", "date": due_date.isoformat(),
                "note": "Direct debit returned"}
    return {"stage": "PAYMENT_MISSED", "date": due_date.isoformat(),
            "note": _NON_DD_OPENING_NOTE.get(method, _NON_DD_OPENING_NOTE_DEFAULT)}


#: The terminal stage of a case that is not written off. It states the balance, and moves no money:
#: a consumer that books a resolution as cash collected must not find one here.
BALANCE_OPEN = "BALANCE_OPEN"
BALANCE_OPEN_NOTE = "Balance still open -- GBP%.2f unpaid, with no payment or arrangement against it"


#: The notes that state an amount, so a credit netted later can restate what was owed that day.
_NOTICE_AMOUNT_NOTES = {"FIRST_NOTICE": "First overdue notice -- GBP%.2f outstanding",
                        "INVOICE_DISPUTED": "Invoice disputed -- GBP%.2f under formal review"}


def arrears_stages(arrears_gbp: float, due_date: date, still_open: bool,
                    archetype: str = "NEUTRAL", *, method: str,
                    write_off_date: date | None = None) -> list[dict]:
    """`method` is REQUIRED and keyword-only, deliberately.

    A default of `"direct_debit"` would have preserved the exact defect this
    parameter exists to remove: every caller not updated would keep silently
    stamping "Direct debit returned" onto non-DD customers, and the build would
    read as done while the book stayed wrong. Making it required means a caller
    that has not decided fails loudly at the call, not quietly in the data.

    `write_off_date` is the date `balance_write_offs` resolved for this case. Without it the
    case falls back to due+90, which is what callers outside the balance rule
    (`final_bill_outcome`) still use. A notice that would fall after the write-off is not sent.

    `still_open` is a case `balance_write_offs` does not write off. Nothing in the world clears
    it -- re-presentation and arrangement paydown are unbuilt -- so it ends on `BALANCE_OPEN`, a
    statement that moves no money, never on a resolution that did not happen.
    """
    stages = [
        opening_arrears_stage(method, due_date),
        {"stage": "FIRST_NOTICE", "date": (due_date + timedelta(days=7)).isoformat(),
         "note": _NOTICE_AMOUNT_NOTES["FIRST_NOTICE"] % arrears_gbp},
        {"stage": "SECOND_NOTICE", "date": (due_date + timedelta(days=21)).isoformat(),
         "note": "Second notice -- payment plan offered"},
    ]
    if still_open:
        stages.append({"stage": BALANCE_OPEN, "date": stages[-1]["date"],
                        "note": BALANCE_OPEN_NOTE % arrears_gbp})
    else:
        if write_off_date is None:
            write_off_date = due_date + timedelta(days=90)
        write_off_date = max(write_off_date, due_date)
        stages = stages[:1] + [st for st in stages[1:] if st["date"] <= write_off_date.isoformat()]
        stages.append({"stage": "WRITTEN_OFF", "date": write_off_date.isoformat(),
                        "note": "Debt written off -- bad debt provision raised"})
        stages.extend(_post_writeoff_stages(arrears_gbp, write_off_date, archetype))
    return stages


#: A credit bill netted against this case (SLC 27.16). It moves no money on the account ledger:
#: the credit invoice itself already reduced the balance, so this stage only says where it went.
CREDIT_APPLIED = "CREDIT_APPLIED"


def with_credits_applied(stages: list[dict], face_gbp: float, credits: list[dict]) -> list[dict]:
    """`stages` with each credit `balance_settlement` netted against the case inserted in date order.

    A case the credits settle in full ends on its last CREDIT_APPLIED, and no notice dated after it
    is sent. The terminal stage of a case left open is dated no earlier than its last credit, so the
    history stays in date order.
    """
    if not credits:
        return stages
    stages = [dict(st) for st in stages]
    opened = stages[0]["date"]
    owed = round(face_gbp, 2)
    credit_stages = []
    for c in sorted(credits, key=lambda c: c["date"]):
        owed = round(owed - c["amount_gbp"], 2)
        # A credit already on the account meets the bill the day the case opens. The ledger's case
        # opens at the issued bill's due date, which can be a day or two after the engine's clock.
        credit_stages.append({
            "stage": CREDIT_APPLIED, "date": max(c["date"].isoformat(), opened),
            "amount_gbp": c["amount_gbp"],
            "note": "Account credit of GBP%.2f (the %s credit bill) netted against this bill -- "
                    "GBP%.2f left owed" % (c["amount_gbp"], c["credit_period_end"], max(owed, 0.0))})
    last = credit_stages[-1]["date"]
    # A notice states what was owed on ITS day, before any later credit.
    for st in stages:
        if st["stage"] in _NOTICE_AMOUNT_NOTES:
            left = face_gbp - sum(c["amount_gbp"] for c in credit_stages if c["date"] <= st["date"])
            st["note"] = _NOTICE_AMOUNT_NOTES[st["stage"]] % max(left, 0.0)
    if owed <= 0:
        kept = stages[:1] + [st for st in stages[1:] if st["date"] <= last
                             and st["stage"] not in (BALANCE_OPEN, "WRITTEN_OFF")]
        return sorted(kept + credit_stages, key=lambda st: st["date"])
    head = [st for st in stages if st["stage"] in (BALANCE_OPEN, "WRITTEN_OFF")]
    cut = stages.index(head[0]) if head else len(stages)
    before, tail = stages[:cut], stages[cut:]
    if tail and tail[0]["stage"] == BALANCE_OPEN:
        tail[0]["date"] = max(tail[0]["date"], last)
    # sorted() is stable, so a credit dated on a notice's day follows the notice.
    return sorted(before + credit_stages, key=lambda st: st["date"]) + tail


def ic_arrears_stages(arrears_gbp: float, due_date: date, still_open: bool,
                       archetype: str = "NEUTRAL", *,
                       write_off_date: date | None = None) -> list[dict]:
    stages = [
        {"stage": "INVOICE_DISPUTED", "date": due_date.isoformat(),
         "note": _NOTICE_AMOUNT_NOTES["INVOICE_DISPUTED"] % arrears_gbp},
        {"stage": "DISPUTE_NOTICE", "date": (due_date + timedelta(days=14)).isoformat(),
         "note": "Dispute notice raised -- escalated to accounts receivable"},
    ]
    if still_open:
        stages.append({"stage": BALANCE_OPEN, "date": stages[-1]["date"],
                        "note": BALANCE_OPEN_NOTE % arrears_gbp})
    else:
        if write_off_date is None:
            write_off_date = due_date + timedelta(days=60)
        write_off_date = max(write_off_date, due_date)
        stages = stages[:1] + [st for st in stages[1:] if st["date"] <= write_off_date.isoformat()]
        stages.append({"stage": "WRITTEN_OFF",
                        "date": write_off_date.isoformat(),
                        "note": "Debt written off -- bad debt provision raised"})
        stages.extend(_post_writeoff_stages(arrears_gbp, write_off_date, archetype))
    return stages


#: C4 (design table). Days from close to write-off is supplier policy and no published source
#: gives an industry clock (Ofgem Appendix 2 Dec 2024 §2.22; CfI Apr 2023 §4.4). The year still
#: needs a date, so this is a CONVENTION, labelled as one: the final bill's due date, the latest
#: point the world's own cash truth fixes.
WRITE_OFF_DATE_CONVENTION = "final_bill_due_date"

#: C7, leg 4a. Limitation Act 1980 s.5 (six years from the cause of action) and s.29(5) (a
#: part-payment restarts the clock). A payment into the running account is read as that
#: part-payment, so a paying stayer never reaches the bar.
STATUTE_BAR_YEARS = 6

#: C6, leg 4b's rates, SOURCED: Centrica plc ARA 2025 Note 17 p.175, UK residential energy, 2025
#: column -- provision / gross billed receivables at 31 Dec, by days beyond invoice date
#: (`docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md`). One supplier, one
#: year, applied to every year. Each band is (upper bound in days, None = open, rate).
LIVE_ARREARS_PROVISION_RATES = {
    "still_in_dd": ((30, 0.0), (90, 0.014), (None, 0.074)),
    "fallen_out_of_dd": ((30, 0.045), (90, 0.151), (None, 0.503)),
}

#: C1, the GAP that picks a row above. A sim DD "failure" (`_DD_FAILURE_PROB`) has no source and no
#: stated basis: if it is a first-presentation bounce the stayer is still a DD account; if it is
#: net of re-presentation the DD is cancelled (British Gas stops it after a second failure) and
#: the arrears sit in pay-on-receipt -- about ten times the rate. Nothing published says which, so
#: there is NO DEFAULT: unset, leg 4b is off and `bad_debt_gbp` is write-offs only. A bracket run
#: sets it to each row in turn from one commit. Read at call time, not import.
STAYER_FAILED_DD_BUCKET_ENV = "SIM_STAYER_FAILED_DD_BUCKET"


def stayer_failed_dd_bucket() -> str | None:
    raw = os.environ.get(STAYER_FAILED_DD_BUCKET_ENV, "").strip()
    if not raw:
        return None
    if raw not in LIVE_ARREARS_PROVISION_RATES:
        raise ValueError(
            f"{STAYER_FAILED_DD_BUCKET_ENV}={raw!r} names no provision bucket; it must be one of "
            f"{sorted(LIVE_ARREARS_PROVISION_RATES)} or unset (leg 4b off -- C1 is unsourced)")
    return raw


def _provision_rate(bucket: str, age_days: int) -> float:
    for upper, rate in LIVE_ARREARS_PROVISION_RATES[bucket]:
        if upper is None or age_days < upper:
            return rate
    raise AssertionError("the last band is open")


def stayer_provision_charges(resolved: list[dict], churned_ids: set[str],
                             written_off: dict[tuple[str, str, str], dict],
                             credited: dict[tuple[str, str, str], list[dict]], bucket: str
                             ) -> dict[tuple[str, int], float]:
    """Leg 4b: the P&L charge for provision on a STAYER's open failed-DD balance, net of credits,
    keyed (customer_id, year). Centrica's rates are a year-end STOCK ratio, so the stock is taken
    at each 31 Dec (the account's last due date in its final year) and the charge is its change.

    Leavers are left out on purpose: a leaver's provision is released into its write-off at close,
    so over the window it nets to the write-off `compute_emergent_bad_debt` already books; only its
    dating is ignored. A statute-barred item leaves the stock the day it is written off.
    """
    by_cid: dict[str, list[dict]] = {}
    horizon_by_cid: dict[str, date] = {}
    for row in resolved:
        cid = row["customer_id"]
        horizon_by_cid[cid] = max(horizon_by_cid.get(cid, row["due_date"]), row["due_date"])
        if cid not in churned_ids and row["outcome"] == "failed":
            by_cid.setdefault(cid, []).append(row)

    out: dict[tuple[str, int], float] = {}
    for cid, rows in by_cid.items():
        horizon = horizon_by_cid[cid]
        prior = 0.0
        for year in range(min(r["due_date"].year for r in rows), horizon.year + 1):
            at = min(date(year, 12, 31), horizon)
            stock = 0.0
            for r in rows:
                key = (cid, r["period_end"], r["commodity"])
                wo = written_off.get(key)
                if r["due_date"] > at or (wo is not None and wo["date"] <= at):
                    continue
                open_gbp = r["amount_gbp"] - sum(
                    c["amount_gbp"] for c in credited.get(key, []) if c["date"] <= at)
                if open_gbp > 0:
                    age = (at - date.fromisoformat(r["period_end"])).days
                    stock += open_gbp * _provision_rate(bucket, age)
            if abs(stock - prior) > 1e-9:
                out[(cid, year)] = round(out.get((cid, year), 0.0) + stock - prior, 2)
            prior = stock
    return out

#: What `bad_debt_gbp` counts. Ofgem's bad-debt charge is provisions PLUS write-offs (Appendix 2,
#: Dec 2024, §2.4). With leg 4b off this line is the narrower quantity, and says so.
BAD_DEBT_BASIS = (
    "write-offs only: the unpaid balance at close (after post-close DCA/sale recovery, applied "
    "separately) plus statute-barred live balances. Provision on a stayer's aged arrears is NOT "
    "included -- its rates are sourced (LIVE_ARREARS_PROVISION_RATES) but which row a failed-DD "
    "stayer sits in turns on C1, which is not (STAYER_FAILED_DD_BUCKET_ENV unset) -- so a stayer's "
    "arrears read as zero cost here, a declared gap, not an established zero.")

#: The two ways a balance reaches write-off.
LEG_CLOSE = "close"
LEG_STATUTE_BAR = "statute_bar"


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 Feb -> 28 Feb
        return d.replace(year=d.year + years, day=28)


def _resolve_bills(bills: list[dict], behavioral: dict, seed: int) -> list[dict]:
    """Each bill's payment outcome, from its own `bill_substream`, in (customer, period_end)
    order. The one place the engine draws an outcome, so every consumer below reads the same one.
    """
    rows = []
    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        commodity = bill.get("commodity", "electricity")
        due_date = date.fromisoformat(period_end) + timedelta(days=PAYMENT_TERMS_DAYS)
        if amount <= 0:
            # A credit bill has nothing to collect, so it can neither fail nor acknowledge a debt.
            rows.append({"customer_id": cid, "period_end": period_end, "commodity": commodity,
                         "amount_gbp": amount, "due_date": due_date, "method": None,
                         "outcome": "credit", "days_late": 0})
            continue
        stress = stress_for_year(behavioral.get(cid) or {}, int(period_end[:4]))
        method = payment_method(segment, amount, cid, commodity)
        outcome, days_late = payment_outcome(
            method, stress, bill_substream(seed, cid, period_end, commodity),
            segment,
            _fuel_poor_for_bill(method, cid),
            _tone_for_bill(method, cid, period_end), cid,
        )
        rows.append({"customer_id": cid, "period_end": period_end, "commodity": commodity,
                     "amount_gbp": amount, "due_date": due_date, "method": method,
                     "outcome": outcome, "days_late": days_late})
    return rows


def balance_settlement_from_outcomes(resolved: list[dict], churned_ids: set[str]
                                     ) -> tuple[dict[tuple[str, str, str], dict],
                                                dict[tuple[str, str, str], list[dict]]]:
    """The balance-at-close rule over already-resolved bills. Pure: no RNG.

    Returns ``(write_offs, credits_applied)``, both keyed ``(customer_id, period_end, commodity)``
    of a failed/disputed bill.

    ``write_offs`` has one entry per bill that is WRITTEN OFF: ``{"date", "amount_gbp", "leg",
    "outcome", "method", "due_date"}``, where ``amount_gbp`` is what is still unpaid on that bill
    once credits are netted. A failed bill that is not here is either still an open balance on a
    live account at the end of the run, or has been cleared by credit.

    ``credits_applied`` lists the account credits netted against each bill:
    ``[{"date", "amount_gbp", "credit_period_end"}]``, where ``amount_gbp`` is positive.

    A successful payment pays its own bill. On a running account balance = bills - payments, so
    it does not reduce the arrears; it restarts the limitation clock (s.29(5)). Re-presentation
    waits on C1/C2b and arrangement paydown on C3b, all None. The one thing that DOES reduce the
    arrears is a credit bill on the same contract. SLC 27.16 defines Credit as payments in excess
    of the charges due "under that Domestic Supply Contract", so a credit exists only net of that
    contract's arrears. The contract is per fuel, so a credit nets per (customer, commodity), never
    across fuels. It discharges the oldest outstanding bill first (Clayton's Case, the
    running-account default). It is not a payment by the debtor, so it does not restart the clock.
    A credit that finds nothing outstanding waits on the account for later arrears, because the
    SLC 27.16 refund-on-request is not modelled.
    """
    by_cid: dict[str, list[dict]] = {}
    for row in resolved:
        by_cid.setdefault(row["customer_id"], []).append(row)

    out: dict[tuple[str, str, str], dict] = {}
    credited: dict[tuple[str, str, str], list[dict]] = {}
    for cid, rows in by_cid.items():
        horizon = max(r["due_date"] for r in rows)
        leaver = cid in churned_ids
        # Contributions sort before credits and payments on the same day: a bill cannot acknowledge
        # itself, and a same-day credit meets the bill it arrives beside.
        events = []
        for r in rows:
            if r["outcome"] in ("failed", "dispute"):
                events.append((r["due_date"], 0, r))
            elif r["outcome"] == "credit":
                events.append((r["due_date"], 1, r))
            elif r["outcome"] == "success":
                events.append((r["due_date"] + timedelta(days=r["days_late"]), 2, r))
        events.sort(key=lambda e: (e[0], e[1]))

        outstanding: list[dict] = []  # oldest first; each {"row", "remaining"}
        unapplied: dict[str, float] = {}  # commodity -> credit waiting on the account
        last_ack: date | None = None

        def _key(row: dict) -> tuple[str, str, str]:
            return (cid, row["period_end"], row["commodity"])

        def _net(item: dict, when: date, credit_period_end: str) -> None:
            commodity = item["row"]["commodity"]
            take = min(item["remaining"], unapplied.get(commodity, 0.0))
            if take <= 0:
                return
            item["remaining"] = round(item["remaining"] - take, 2)
            unapplied[commodity] = round(unapplied[commodity] - take, 2)
            credited.setdefault(_key(item["row"]), []).append(
                {"date": when, "amount_gbp": round(take, 2), "credit_period_end": credit_period_end})
            if item["remaining"] <= 0:
                outstanding.remove(item)

        def _write_off(item: dict, when: date, leg: str) -> None:
            r = item["row"]
            out[_key(r)] = {"date": when, "amount_gbp": item["remaining"], "leg": leg,
                            "outcome": r["outcome"], "method": r["method"],
                            "due_date": r["due_date"]}

        def _bar(until: date) -> None:
            for item in list(outstanding):
                due = item["row"]["due_date"]
                clock = due if last_ack is None else max(due, last_ack)
                barred_at = _add_years(clock, STATUTE_BAR_YEARS)
                if barred_at <= until:
                    outstanding.remove(item)
                    _write_off(item, barred_at, LEG_STATUTE_BAR)

        last_credit_pe: dict[str, str] = {}
        for when, kind, r in events:
            if when > horizon:
                break
            _bar(when)
            if kind == 0:
                item = {"row": r, "remaining": r["amount_gbp"]}
                outstanding.append(item)
                if unapplied.get(r["commodity"], 0.0) > 0:
                    _net(item, when, last_credit_pe[r["commodity"]])
            elif kind == 1:
                c = r["commodity"]
                unapplied[c] = round(unapplied.get(c, 0.0) - r["amount_gbp"], 2)
                last_credit_pe[c] = r["period_end"]
                for item in [i for i in outstanding if i["row"]["commodity"] == c]:
                    _net(item, when, r["period_end"])
            else:
                last_ack = when
        _bar(horizon)
        if leaver:
            for item in outstanding:
                _write_off(item, horizon, LEG_CLOSE)
    return out, credited


def balance_write_offs_from_outcomes(resolved: list[dict], churned_ids: set[str]
                                     ) -> dict[tuple[str, str, str], dict]:
    """The write-off half of `balance_settlement_from_outcomes`."""
    return balance_settlement_from_outcomes(resolved, churned_ids)[0]


def balance_settlement(bills: list[dict], behavioral: dict, churned_ids: set[str],
                       seed: int = 42) -> tuple[dict[tuple[str, str, str], dict],
                                                dict[tuple[str, str, str], list[dict]]]:
    """Every written-off case in the book and every credit netted against a case, under the
    balance-at-close rule. `tools.generate_billing_ledger` reads both, so the household's arrears
    history nets exactly what the P&L nets."""
    # Only the bills the supplier issues: a bill its pre-bill gate holds never reached the customer,
    # so it cannot fail and a held credit was never given. The ledger runs the same gate.
    from company.interfaces.bill_assembly import issued_bills
    return balance_settlement_from_outcomes(
        _resolve_bills(issued_bills(bills), behavioral, seed), churned_ids)


def balance_write_offs(bills: list[dict], behavioral: dict, churned_ids: set[str],
                       seed: int = 42) -> dict[tuple[str, str, str], dict]:
    """Every written-off case in the book, under the balance-at-close rule, net of credits.

    The single source every consumer reads: `compute_emergent_bad_debt` (the P&L),
    `compute_debt_recovery` (post-close proceeds) and, through `balance_settlement`,
    `tools.generate_billing_ledger` (the household's arrears history). None of them re-derives the
    balance, which is what keeps the ledger and the P&L agreeing by construction.
    """
    return balance_settlement(bills, behavioral, churned_ids, seed)[0]


def emergent_bad_debt_lines(bills: list[dict], behavioral: dict, churned_ids: set[str],
                            seed: int = 42) -> dict[str, dict[tuple[str, int], float]]:
    """`compute_emergent_bad_debt`'s charge, kept apart by LINE: the write-off at close, the
    statute-barred write-off, and leg 4b's stayer provision (empty while leg 4b is off). Each is
    keyed (customer_id, year) exactly as the sum is, so a reader can say which rule a household's
    bad debt came from -- the question the C1 bracket could not answer for PROS-2016-0098.

    `"total"` is the sum, accumulated in the order and with the per-step rounding the charge has
    always used; re-adding the lines in another order can move a key by a penny.
    """
    from company.interfaces.bill_assembly import issued_bills
    resolved = _resolve_bills(issued_bills(bills), behavioral, seed)
    written_off, credited = balance_settlement_from_outcomes(resolved, churned_ids)
    lines: dict[str, dict[tuple[str, int], float]] = {
        LEG_CLOSE: {}, LEG_STATUTE_BAR: {}, "stayer_provision": {}, "total": {}}
    total = lines["total"]
    for (cid, _pe, _c), wo in sorted(written_off.items()):
        key = (cid, wo["date"].year)
        line = lines[wo["leg"]]
        line[key] = round(line.get(key, 0.0) + wo["amount_gbp"], 2)
        total[key] = round(total.get(key, 0.0) + wo["amount_gbp"], 2)
    bucket = stayer_failed_dd_bucket()
    if bucket is not None:
        charges = stayer_provision_charges(resolved, churned_ids, written_off, credited, bucket)
        print(f"  [leg 4b] stayer provision ON, C1 bucket={bucket}: "
              f"GBP {sum(charges.values()):,.2f} over {len({c for c, _ in charges})} stayer(s)")
        lines["stayer_provision"] = dict(charges)
        for key, charge in charges.items():
            total[key] = round(total.get(key, 0.0) + charge, 2)
    return lines


def compute_emergent_bad_debt(bills: list[dict], behavioral: dict, churned_ids: set[str],
                               seed: int = 42) -> dict[tuple[str, int], float]:
    """GBP written off, keyed by (customer_id, write_off_year). Its basis is `BAD_DEBT_BASIS`:
    write-offs only, no provision -- unless `stayer_failed_dd_bucket()` names a C1 bucket, when
    leg 4b's stayer provision charge is added on the same keys.
    """
    return emergent_bad_debt_lines(bills, behavioral, churned_ids, seed)["total"]


def _row_for(key: tuple[str, int], last_index_by_cy: dict[tuple[str, int], int]) -> int | None:
    """The record a (customer, year) figure books on. A figure dated after the account's last
    settlement year -- a write-off at a final bill due in January, a recovery months after close
    -- books on the account's last record rather than being dropped. Dropping it was silent, and
    the balance-at-close rule dates 18% of leaver write-offs there
    (`docs/staging/records/SEAT_RESULT_THE_BALANCE_AT_CLOSE_WRITE_OFF_RULE_RUN_ALONE_2026-09-27.md`).
    """
    idx = last_index_by_cy.get(key)
    if idx is not None:
        return idx
    later = [(y, i) for (c, y), i in last_index_by_cy.items() if c == key[0]]
    if later:
        last_year, last_idx = max(later)
        if key[1] > last_year:
            return last_idx
    return None


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
        idx = _row_for(key, last_index_by_cy)
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
    """Post-close DCA-recovered / debt-sale proceeds on the same written-off cases
    `compute_emergent_bad_debt` books, keyed by (customer_id, year of the RECOVERED/SOLD stage).

    Only the close leg is placed with a collector. A statute-barred balance cannot be enforced,
    so it is written off with no recovery stage. debt_archetype() is read at the write-off year,
    SIM-side only.
    """
    result: dict[tuple[str, int], float] = {}
    for (cid, _pe, _c), wo in sorted(balance_write_offs(bills, behavioral, churned_ids, seed).items()):
        if wo["leg"] != LEG_CLOSE:
            continue
        trajectory = (behavioral.get(cid) or {}).get("income_stress_trajectory") or []
        archetype = debt_archetype(trajectory, wo["date"].year)
        terminal = _post_writeoff_stages(wo["amount_gbp"], wo["date"], archetype)[-1]
        key = (cid, int(terminal["date"][:4]))
        result[key] = round(result.get(key, 0.0) + terminal["amount_gbp"], 2)
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
        idx = _row_for(key, last_index_by_cy)
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


#: The per-customer arrears lines `book_arrears_lines` returns, in the order the identity reads.
ARREARS_LINE_KEYS = (
    "pre_4c_net_gbp", "placeholder_bad_debt_released_gbp", "write_off_at_close_gbp",
    "write_off_statute_barred_gbp", "stayer_provision_gbp", "line_rounding_gbp",
    "unbooked_bad_debt_gbp", "dca_recovery_gbp", "unbooked_recovery_gbp",
)


def book_arrears_lines(all_records: list[dict], lines: dict[str, dict[tuple[str, int], float]],
                       recovery_by_customer_year: dict[tuple[str, int], float]
                       ) -> dict[str, dict[str, float]]:
    """Book the arrears engine onto `all_records` (`apply_emergent_bad_debt` then
    `apply_debt_recovery`, unchanged) and return, per customer, the lines that took each
    record's net from the settlement loop's figure to the booked one:

        net = pre_4c_net + placeholder_released
              - (write_off_at_close + write_off_statute_barred + stayer_provision
                 + line_rounding - unbooked_bad_debt)
              + (dca_recovery - unbooked_recovery)

    `unbooked_*` is a figure keyed to a year `_row_for` finds no record for, which the apply
    step drops; it is carried so the drop is visible rather than a gap. `line_rounding` is the
    engine's total less the sum of its lines -- the lines are rounded per line, the total in the
    charge's own order.
    """
    out: dict[str, dict[str, float]] = {}
    last_index_by_cy: dict[tuple[str, int], int] = {}

    def row(cid: str) -> dict[str, float]:
        return out.setdefault(cid, dict.fromkeys(ARREARS_LINE_KEYS, 0.0))

    for i, rec in enumerate(all_records):
        r = row(rec["customer_id"])
        r["pre_4c_net_gbp"] += rec["net_margin_gbp"]
        r["placeholder_bad_debt_released_gbp"] += rec.get("bad_debt_gbp", 0.0)
        last_index_by_cy[(rec["customer_id"], int(rec["settlement_date"][:4]))] = i

    for name, field in ((LEG_CLOSE, "write_off_at_close_gbp"),
                        (LEG_STATUTE_BAR, "write_off_statute_barred_gbp"),
                        ("stayer_provision", "stayer_provision_gbp")):
        for (cid, _y), gbp in lines[name].items():
            row(cid)[field] += gbp
    for key, gbp in lines["total"].items():
        r = row(key[0])
        r["line_rounding_gbp"] += gbp
        if _row_for(key, last_index_by_cy) is None:
            r["unbooked_bad_debt_gbp"] += gbp
    for key, gbp in recovery_by_customer_year.items():
        r = row(key[0])
        r["dca_recovery_gbp"] += gbp
        if _row_for(key, last_index_by_cy) is None:
            r["unbooked_recovery_gbp"] += gbp
    for r in out.values():
        r["line_rounding_gbp"] -= (r["write_off_at_close_gbp"] + r["write_off_statute_barred_gbp"]
                                   + r["stayer_provision_gbp"])

    apply_emergent_bad_debt(all_records, lines["total"])
    apply_debt_recovery(all_records, recovery_by_customer_year)
    return {cid: {k: round(v, 6) for k, v in r.items()} for cid, r in out.items()}
