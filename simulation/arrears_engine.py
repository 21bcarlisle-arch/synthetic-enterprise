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
desynchronise anything.

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

import hashlib
import random
from datetime import date, timedelta

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
    key = f"{STREAM_NAMESPACE}::{name}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


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


def arrears_stages(arrears_gbp: float, due_date: date, eventually_resolved: bool,
                    archetype: str = "NEUTRAL", *, method: str) -> list[dict]:
    """`method` is REQUIRED and keyword-only, deliberately.

    A default of `"direct_debit"` would have preserved the exact defect this
    parameter exists to remove: every caller not updated would keep silently
    stamping "Direct debit returned" onto non-DD customers, and the build would
    read as done while the book stayed wrong. Making it required means a caller
    that has not decided fails loudly at the call, not quietly in the data.
    """
    stages = [
        opening_arrears_stage(method, due_date),
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

    Resolves each bill from its own `bill_substream(seed, cid, period_end,
    commodity)`,
    the same substream `tools.generate_billing_ledger.generate()` resolves it
    from, so a case that reaches WRITTEN_OFF here reaches WRITTEN_OFF there
    too, for the same GBP amount. That agreement no longer depends on the two
    visiting the same bills in the same order (it previously did, and the
    ledger's credit-invoice skip broke it for 42 bills -- see module docstring).
    The sort is retained only for deterministic accumulation order.
    """
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
            method, stress, bill_substream(seed, cid, period_end, bill.get("commodity", "electricity")),
            segment,
            _fuel_poor_for_bill(method, cid),
            _tone_for_bill(method, cid, period_end), cid,
        )

        if outcome not in ("failed", "dispute"):
            continue
        will_be_written_off = cid in churned_ids
        if not will_be_written_off:
            continue
        # Dispatched, not name-called -- which is why a grep for
        # `arrears_stages(` did NOT find this call site. Only making `method`
        # required surfaced it.
        if outcome == "failed":
            stages = arrears_stages(amount, due_date, False, method=method)
        else:
            stages = ic_arrears_stages(amount, due_date, False)
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
    """Run the shared payment/arrears model over `bills` (resolving each bill
    from the same `bill_substream(seed, cid, period_end, commodity)`
    compute_emergent_bad_debt()
    resolves it from, so the two line up on the exact same set of written-off
    cases -- by construction now, not by iterating in lockstep) and return real
    DCA-recovered / debt-sale proceeds, keyed by (customer_id, year of the
    RECOVERED/SOLD stage -- NOT the write-off year).

    debt_archetype() is computed from behavioral[cid]["income_stress_trajectory"]
    at the write-off year, to decide which terminal stage (RECOVERED vs SOLD)
    applies and what the proceeds are -- SIM-side only, never exposed past
    this module's own note text.
    """
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
            method, stress, bill_substream(seed, cid, period_end, bill.get("commodity", "electricity")),
            segment,
            _fuel_poor_for_bill(method, cid),
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

        if outcome == "failed":
            stages = arrears_stages(amount, due_date, False, archetype, method=method)
        else:
            stages = ic_arrears_stages(amount, due_date, False, archetype)
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
