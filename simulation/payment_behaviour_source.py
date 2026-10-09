"""W2_11_payment_behaviour_source -- payment-behaviour generator (sim-source,
world-side, coupled-triad W of the D5 decomposition: W2_11 source / W4_4 seam /
D5 consumption / H27 gap).

WHAT THIS IS
------------
The baseline generator of the WORLD's payment TRUTH: who truly pays when, why
a Direct Debit collection truly fails, how the arrears truly ages, and which
payment method a customer truly uses. The company never reads this module --
it observes payments only through the not-yet-built W4_4 seam (bank
statements / remittance advices / Bacs DD outcome reports), and H27
(payment-belief-vs-truth gap) scores the company's D5 inference against this
module's truth. This atom cannot reach L3 alone (COUPLED_TRIAD binding rule:
no world source reaches L3 until the gap is measured against the consuming
company capability) -- assessed honestly at generator-alone level (L1-L2),
never claimed L3 here.

REUSE, NOT REINVENTION (R13 discipline, same law bacs_rails.py states for
itself: "duplicating it here would violate R13")
------------------------------------------------------------------------
The core payment-outcome probability model (on-time / late / DD-failed by
stress tier, I&C BACS/CHAPS behaviour) is NOT reinvented here -- it already
exists, calibrated, at `simulation.arrears_engine.payment_outcome()` /
`.payment_method()` / `.arrears_stages()`, and duplicating a second calibrated
model would create exactly the two-independently-calibrated-models problem
`arrears_engine.py`'s own docstring was written to close. This module WRAPS
that existing core in three things it does not yet have, all requested by the
W2_11 FRAME:

  1. C-S2 RNG SUBSTREAM ISOLATION -- this module gives EVERY customer, and
     every period within a customer's history, its OWN named seeded substream,
     so a per-customer/per-period draw here can never shift any other
     subsystem's sequence, any other customer's sequence, or any other
     period's sequence -- the hard C-S2 requirement for a generator that other
     code (the future W4_4 seam, H27's gap harness) will call per-customer,
     out of population order, on demand.

     CORRECTION (2026-08-08, W2_16). This bullet used to say `arrears_engine`'s
     batch functions advance ONE shared `random.Random(seed)` across bills in
     population iteration order, and that this was "fine for its original
     purpose: a population-level ledger/P&L reconciliation run once". The
     second half was WRONG on its own terms and is withdrawn -- the shared
     stream had already broken the very reconciliation it was called fine for.
     Lockstep was an obligation each of four consumers had to hand-maintain,
     and `tools.generate_billing_ledger` did not: it skips the outcome draw for
     credit invoices, so the ledger and the P&L drew from offset streams and
     disagreed on 42 of 1557 real bills. `arrears_engine` now draws each bill
     from its own `bill_substream(seed, cid, period_end, commodity)`, i.e. it
     has the same isolation property this module has, and the two modules'
     substream discipline no longer differ in kind.
  2. DD-FAILURE REASON (insufficient-funds vs cancelled/other) -- arrears_engine
     returns success/failed/dispute with no "why". This module adds the reason
     split, anchored to the SAME real Bacs ARUDD dominant-code fact
     `simulation.bacs_rails.py` already cites (see ANCHORS below).
  3. PAYMENT-METHOD MIX beyond binary DD/non-DD (standing_order / card /
     prepayment) and ARREARS-AGEING / CHRONIC-vs-TRANSIENT PATTERN
     classification -- neither exists elsewhere in named, queryable form.

COUPLING TO THE HOUSEHOLD HARDSHIP SUBSTRATE (FRAME instruction: "NOT A
SEPARATE MECHANISM ... branches on the SAME hardship substrate")
------------------------------------------------------------------------
Payment behaviour is driven by the caller-supplied `stress` (a
`simulation.household.IncomeStress` value, or an equivalent stress
trajectory) -- the SAME hardship substrate `simulation.household_budget` /
`simulation.arrears_engine` already model. This module does not invent a new
hardship variable; it takes stress as an input (exactly like
`arrears_engine.payment_outcome()` already does) and adds the three
dimensions above on top.

ANCHORS (R13 baseline, decided BLIND to company P&L -- CITED, not invented)
----------------------------------------------------------------------------
- Payment-method mix, DD share: DESNZ "Quarterly Energy Prices: June 2026"
  commentary, "Payment methods" section (fetched 2026-07-08, recorded
  `docs/market_research/ASSUMPTIONS.md` line ~114 and reused directly from
  `simulation.household_segments.DIRECT_DEBIT_SHARE_BY_FUEL`): Direct Debit
  72% of standard electricity customers / 75% of gas customers (end of March
  2026). REUSED here, not re-derived (single source of truth).
- Non-DD sub-split (standard_credit vs prepayment): Ofgem 2026, ~74% DD / 13%
  standard credit / 13% prepayment (recorded in
  `simulation.dd_attribution`'s own ANCHORS section, 2026-07-13 DISCOVER
  pass). The two non-DD shares are near-equal (13% / 13%), so this module
  splits the non-DD residual left after the fuel-specific DD anchor above
  50/50 between standard_credit and prepayment -- an anchored RATIO applied
  to a different (but consistent) DD baseline, not a fabricated split.
- ANCHORED [L], calibration GAP (R10, honestly labelled, not fabricated):
  no published sub-split of "standard credit" payment INSTRUMENT (standing
  order vs debit/credit card) was found in this codebase's research to date
  -- `_STANDARD_CREDIT_SUBMETHOD_SHARE` below is a labelled 50/50 ESTIMATE,
  not a sourced figure. Left as a documented gap for a future research pass.
- DD-failure REASON split (insufficient-funds vs cancelled/other): DIRECTION
  anchored to `simulation.bacs_rails.py`'s own citation (Pay.UK "Bacs System
  Principles" + AccessPaySuite/Hafiz Didarali reason-code references) that
  ARUDD code 0 ("Refer to Payer", i.e. insufficient funds) is the real-world
  DOMINANT DD-failure cause. The exact proportion is NOT published in either
  module's research to date; `_DD_FAILURE_REASON_SPLIT` below is a labelled
  ESTIMATE (0.85 insufficient-funds / 0.15 cancelled-or-other) that respects
  the sourced DIRECTION (insufficient-funds dominant) without claiming
  fabricated precision on the exact split -- same honesty convention
  `bacs_rails.py::resolve_submission` already applies to the full reason-code
  set (a fixed dominant code, never a uniform random pick across all codes).
- On-time/late/DD-failure probabilities by income-stress tier, and I&C
  BACS/CHAPS on-time/late/dispute probabilities: REUSED byte-for-byte from
  `simulation.arrears_engine` (this module's whole point is to not duplicate
  that calibration) -- their own external-sourcing status is inherited from
  that module, not re-asserted here.

CURRICULUM vs BASELINE (R13, Law A) -- NOT THIS MODULE'S DECISION
----------------------------------------------------------------------
Every constant in this module is the BASELINE (decided blind to company P&L,
for real-world fidelity only). Any DIFFICULTY DIAL (a "DD-failure spike"
epoch, a payment-stress scenario) is director-authored CURRICULUM and belongs
elsewhere (a named, versioned scenario artefact) -- this module exposes no
scenario switch and must never be tuned in response to company outcomes.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
------------------------------------------------------
Pure WORLD/sim code. Must not import `company.*` or `saas.*`. Every record
carries `data_regime="synthetic"`.

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md -- non-negotiable, the 01:09Z
incident)
------------------------------------------------------------------------
Every stochastic draw in this module comes from THIS subsystem's OWN named,
sha256-seeded substream (`_substream(base_seed, name)`), never the global
`random` module, and never a substream shared with any other subsystem. A
per-period draw is additionally isolated by period index inside its own
substream name (`f"payment_event::{period_index}"`), so drawing period 5 of
customer A can never shift period 3 of customer A, any period of customer B,
or any other subsystem's sequence (proven by
`tests/sim/test_w2_11_payment_behaviour_source.py`).
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Sequence

from simulation.arrears_engine import PAY_ON_RECEIPT_METHOD, PREPAYMENT_METHOD
from simulation.arrears_engine import payment_outcome as _core_payment_outcome
from simulation.household import household_of
from simulation.household_segments import PaymentChannel, payment_channel_for_customer
from simulation.meter_reads import assumption_toggle
from simulation.rng_substream import substream
from simulation.segment_vocabulary import is_business

STREAM_NAMESPACE = "W2_11_payment_behaviour_source"

# Named RNG substreams -- FIXED (per-customer, drawn once) names (C-S2).
# Per-period draws use a DYNAMIC name built from one of these bases + the
# period index (see `_period_substream`) -- still a single deterministic
# sha256 key per (base_seed, name), so C-S2 isolation holds identically.
_SUBSTREAMS = (
    "payment_method_submethod",    # standing_order vs card sub-draw (standard credit only)
)
_PERIOD_SUBSTREAM_BASE = "payment_event"       # + "::<period_index>"
_REASON_SUBSTREAM_BASE = "dd_failure_reason"   # + "::<period_index>"


def _substream(base_seed: int, name: str) -> random.Random:
    """Return an ISOLATED ``random.Random`` for a named mechanism substream.

    Seed is a STABLE sha256 of ``W2_11_payment_behaviour_source::<name>::<base_seed>``
    (never Python's per-process-salted ``hash()``), so the same (base_seed, name)
    yields the same stream across processes -- the hard C-S2 requirement. Each
    name seeds an independent generator; a draw here can never consume from, or
    shift, any other substream of this or any other subsystem.
    """
    return substream(STREAM_NAMESPACE, name, base_seed)


def _period_substream(base_seed: int, base_name: str, period_index: int) -> random.Random:
    """Per-period substream: same isolation guarantee as `_substream`, keyed
    additionally by `period_index` so no two periods (of the same or a
    different customer) ever share a stream."""
    return _substream(base_seed, f"{base_name}::{period_index}")


def _base_seed_for(customer_id: str, seed: Optional[int]) -> int:
    """Resolve the base seed. Stable md5 of customer_id when no explicit seed
    is given (the built-in ``hash()`` is per-process-salted and would break
    replay across processes)."""
    if seed is not None:
        return seed
    return int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)


# ---------------------------------------------------------------------------
# ANCHORS (see module docstring for full citations).
# ---------------------------------------------------------------------------
DIRECT_DEBIT = "direct_debit"
STANDING_ORDER = "standing_order"
CARD = "card"
PREPAYMENT = "prepayment"
#: Not a payment method a household is ON: the label of the cash that pays off an unpaid bill
#: later (`later_settlement_date`). How arrears are repaid is not modelled, so it maps to no
#: named rail at the seam.
ARREARS_REPAYMENT = "arrears_repayment"

# The DD share and the non-DD prepayment ratio live in `household_segments` alone, and are reached
# here only through `payment_channel_for_customer` (see `generate_payment_method`).

# ESTIMATE (R10 calibration gap, not sourced): standard-credit sub-instrument.
_STANDARD_CREDIT_SUBMETHOD_SHARE = {STANDING_ORDER: 0.50, CARD: 0.50}

# ESTIMATE (direction sourced from bacs_rails.py's ARUDD-dominant-code
# citation; exact split not published).
INSUFFICIENT_FUNDS = "insufficient_funds"
CANCELLED_OTHER = "cancelled_other"
_DD_FAILURE_REASON_SPLIT = {INSUFFICIENT_FUNDS: 0.85, CANCELLED_OTHER: 0.15}

AGEING_BUCKETS = ("current", "0-30", "31-60", "61-90", "90+")


def generate_payment_method(
    customer_id: str,
    fuel: str = "electricity",
    seed: Optional[int] = None,
) -> str:
    """Persistent per-customer payment-method archetype: one of DIRECT_DEBIT,
    STANDING_ORDER, CARD, PREPAYMENT.

    ONE HOME (2026-10-03). The three-way channel -- direct debit, standard credit, prepayment -- is
    `household_segments.payment_channel_for_customer`'s, the same draw the seam reports, the
    arrears engine bills and the churn response reads. This function only refines standard credit
    into its instrument. Until today it took its own DD/non-DD draw on its own stream, and the
    triad paid the company's ledger by it: the ledger and the seam agreed on 112 of the 178 resi
    supply points of the live book, which is what two independent 72% coins give. The DD and
    prepayment households here are exactly the seam's, so `seed` can move only the standing-order /
    card split and never a household's channel.

    The instrument split is keyed on the household's electricity leg, so both fuels of one
    household name the same instrument whenever both are standard credit.
    """
    channel = payment_channel_for_customer(customer_id, fuel)
    if channel is PaymentChannel.DIRECT_DEBIT:
        return DIRECT_DEBIT
    if channel is PaymentChannel.PREPAYMENT:
        return PREPAYMENT
    base_seed = _base_seed_for(f"{household_of(customer_id)}::electricity", seed)
    r_sub = _substream(base_seed, "payment_method_submethod")
    return (
        STANDING_ORDER
        if r_sub.random() < _STANDARD_CREDIT_SUBMETHOD_SHARE[STANDING_ORDER]
        else CARD
    )


#: The seam's three-way vocabulary for each of this module's four methods. Standing order and card
#: are both standard credit -- the instrument is a refinement the company is not told.
SEAM_CHANNEL_FOR_METHOD: dict[str, str] = {
    DIRECT_DEBIT: PaymentChannel.DIRECT_DEBIT.value,
    STANDING_ORDER: PaymentChannel.STANDARD_CREDIT.value,
    CARD: PaymentChannel.STANDARD_CREDIT.value,
    PREPAYMENT: PaymentChannel.PREPAYMENT.value,
    # Not drawn: what a DD household pays on once the supplier has stopped its mandate.
    PAY_ON_RECEIPT_METHOD: PaymentChannel.STANDARD_CREDIT.value,
}


#: The probe `payment_method_identity` digests: these ids, both fuels. Fixed so that the digest moves
#: only when the draw does.
PAYMENT_PROBE_IDS: tuple[str, ...] = tuple(f"PROS-2016-{i:04d}" for i in range(400))


def payment_method_identity() -> dict:
    """WHICH PAYMENT METHODS the world gives its households, as a digest a later artefact can compare.

    The departure part of `world_identity` and its `homes` part are both blind to this: on
    2026-10-03 the triad's method moved onto the seam's draw for a third of the book and neither
    digest could move. Digested over the four-way method, so a change to the standing-order / card
    split moves it too, while the seam's three-way channel moves it whenever the channel moves.
    """
    rows = [[cid, fuel, generate_payment_method(cid, fuel=fuel)]
            for cid in PAYMENT_PROBE_IDS for fuel in ("electricity", "gas")]
    canonical = json.dumps(rows, separators=(",", ":"))
    return {
        "digest": hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16],
        "probe_size": len(PAYMENT_PROBE_IDS),
        "what_this_identifies": (
            "the payment method each household pays by -- `generate_payment_method` over {} fixed "
            "ids on both fuels, the one draw the ledger is paid by and the seam reports. Two runs "
            "sharing this digest billed the same households by the same method.".format(
                len(PAYMENT_PROBE_IDS))),
        "what_this_does_not_cover": (
            "how a method behaves -- failure rates, lateness and arrears are the payment events, "
            "not the method -- and it is not the departure level or the home stock, each of which "
            "is its own part."),
    }


@dataclass(frozen=True)
class PaymentEvent:
    """One period's payment TRUTH (world-side ground truth; observed by the
    company only through the future W4_4 seam, never this object directly)."""
    customer_id: str
    period_index: int
    due_date: str                 # YYYY-MM-DD
    amount_gbp: float
    payment_method: str
    result: str                   # "success" | "failed" | "dispute"
    days_late: int
    payment_date: Optional[str]   # None if unpaid as of generation (failed/dispute)
    dd_failure_reason: Optional[str]  # INSUFFICIENT_FUNDS | CANCELLED_OTHER | None
    data_regime: str = "synthetic"

    @property
    def is_late(self) -> bool:
        return self.result == "success" and self.days_late > 0

    @property
    def is_unresolved(self) -> bool:
        return self.result in ("failed", "dispute")


def generate_payment_event(
    customer_id: str,
    period_index: int,
    due_date: date,
    amount_gbp: float,
    stress: str,
    payment_method: str,
    segment: str = "resi",
    seed: Optional[int] = None,
    dd_failure_prob: Optional[dict] = None,
) -> PaymentEvent:
    """Generate one period's payment truth.

    `dd_failure_prob` is passed to the core model unchanged: None (every world path) is the
    world's tier table; a harness that declares its own population passes its own.

    Draws from this module's OWN period-isolated substream
    (`_period_substream(base_seed, "payment_event", period_index)`), then
    hands that isolated RNG into the EXISTING calibrated core
    (`simulation.arrears_engine.payment_outcome`) -- reuse, not reinvention
    (see module docstring). A second, also period-isolated, substream draws
    the DD-failure reason only when the outcome is a DD failure.

    `payment_method` (this module's own DD/standing_order/card/prepayment
    label) does not change WHICH outcome-probability tier is used: the
    underlying calibrated model (`arrears_engine.payment_outcome`) only
    distinguishes "bacs/chaps" (I&C/SME) from everything else -- there is no
    separately-anchored outcome model for standing_order/card/prepayment
    specifically, and inventing one would be exactly the un-anchored
    duplication R13 warns against (see module docstring). So every
    non-corporate method maps to the same core "direct_debit"-style outcome
    tier; only the METHOD LABEL varies. Prepayment is the exception: a meter is paid before use,
    so it takes the core model's own prepayment branch, which never fails or lates a period.
    """
    base_seed = _base_seed_for(customer_id, seed)
    rng = _period_substream(base_seed, _PERIOD_SUBSTREAM_BASE, period_index)

    # Business segments bill on a corporate rail. Routed through the shared
    # normaliser rather than a literal tuple: the tuple this replaces --
    # `("ic", "I&C", "sme")` -- was case-sensitive, so the canonical "SME" and
    # "I&C" spellings `saas/customers.py` actually stores matched only by
    # accident (W2_sme_segment_case_normalisation).
    #
    # A prepayment meter is paid before use, so its period cannot fail or be late the way a credit
    # bill can: `payment_outcome` has its own `PREPAYMENT_METHOD` branch for exactly that, and this
    # call used to by-pass it by sending every domestic method as "direct_debit" (27 of 227 failed
    # bills on an 80-founder run were on a meter). The PPM household's real debt routes are a named
    # gap on `arrears_engine.PREPAYMENT_METHOD`, not a credit-bill failure.
    if is_business(segment):
        core_method = "bacs"
    elif payment_method == PREPAYMENT:
        core_method = PREPAYMENT_METHOD
    else:
        core_method = "direct_debit"
    # arrears_engine's stress-keyed dicts are upper-cased ("LOW"/"MODERATE"/
    # "HIGH"); household_demand.income_stress_trajectory() emits lower-case
    # IncomeStress.value strings ("low"/"moderate"/"high") -- normalise here
    # so a moderate/high stress period is never silently mis-read as the
    # (coincidentally identical-looking) default low-stress probability.
    core_stress = (stress or "LOW").upper()

    result, days_late = _core_payment_outcome(core_method, core_stress, rng, segment=segment,
                                              dd_failure_prob=dd_failure_prob)

    dd_failure_reason = None
    payment_date: Optional[str] = None
    if result == "failed":
        r_reason = _period_substream(base_seed, _REASON_SUBSTREAM_BASE, period_index)
        dd_failure_reason = (
            INSUFFICIENT_FUNDS
            if r_reason.random() < _DD_FAILURE_REASON_SPLIT[INSUFFICIENT_FUNDS]
            else CANCELLED_OTHER
        )
    elif result == "dispute":
        payment_date = None
    else:  # success (on-time or late)
        payment_date = (due_date + timedelta(days=days_late)).isoformat()

    return PaymentEvent(
        customer_id=customer_id,
        period_index=period_index,
        due_date=due_date.isoformat(),
        amount_gbp=amount_gbp,
        payment_method=payment_method,
        result=result,
        days_late=days_late,
        payment_date=payment_date,
        dd_failure_reason=dd_failure_reason,
    )


# ---------------------------------------------------------------------------
# WHAT HAPPENS AFTER THE DUE DATE: the later settlement of an unpaid domestic bill.
#
# `generate_payment_event` decides whether a bill is paid, paid late or not paid at all, and this
# never changes that draw. Until 2026-10-04 a bill that was not paid stayed unpaid for the rest of
# the run, so every household that ever missed a bill read as a debtor for ever after (56% of
# renewal decisions on a full run were by an "indebted" household). Real unpaid domestic debt is
# mostly repaid. This is the smallest sourced account of that, and of nothing else.
#
# THE ONE PUBLISHED RATE. Ofgem, *Impact assessment on review of domestic objections* (July 2016)
# §1.38-1.39: of the domestic customers debt-blocked in November 2013 and April 2014, "just over
# half ... had paid back their debt at the time of reporting (September 2015). Around 70% of those
# that had paid off their debt at the time of reporting did so within three months."
# `docs/market_research/domestic_debt_objection_rates_gb.md` row 22. That population is debts old
# enough to object to, so the clock here starts on the day an unpaid bill becomes objectionable:
# its due date plus SLC 14's 28 days.
#
# NAMED GAPS, each with the direction it moves eligibility for the debt objection:
#   1. RE-PRESENTATION (closed 2026-10-09 as an ESTIMATE). A returned DD is re-presented (British
#      Gas: retry after 14 days, debt_and_collections.md row P1) and collected with probability
#      `REPRESENTATION_SUCCESS_SHARE` (register `dd_representation_success_share`, vendor figures).
#      The world's failure rate is now first-presentation by construction
#      (`arrears_engine.DD_RETURN_RATE_FIRST_PRESENTATION`), so this cure is not counted twice. The
#      cure is dated 14 days after the DUE date; the return itself lands a few working days after
#      it, so the cure is dated up to that much early. Only a Direct Debit is re-presented.
#   2. DATING, AND THE OTHER HALF. Ofgem gives two windows, not a curve. Each settlement is dated
#      at the END of its window (3 months, or the longer cohort's 22 months), the latest date the
#      source allows. The share not repaid by the report is never repaid here, though Ofgem saw no
#      further than 22 months. Both overstate time in debt; on a full run the second dominates
#      (one never-repaid bill holds a household eligible at every later renewal).
#   3. THE CLOCK START. Ofgem's clock starts at the block, which may be later than day 28.
#      Understates time in debt; partly offsets gap 2.
#   4. PER BILL, NOT PER HOUSEHOLD. Ofgem counts a customer's whole debt; each bill is drawn here on
#      its own, so a household with n unpaid bills clears all of them with probability 0.5^n, not
#      0.5. Chronic non-payers therefore stay in debt -- the conservative side.
#   5. ONE LUMP, NO ARRANGEMENT. The debt is repaid in full on the settlement date; instalments
#      under an SLC 27 arrangement are not modelled, and the debt counts as outstanding until then.
#   6. VINTAGE AND MIX. 2013-2015, all payment methods (PPM "took longest"), applied to credit-meter
#      domestic bills 2016-2025. Business bills (I&C/SME failures and disputes) are never cured:
#      the source is domestic.
#   7. LEAVERS. A bill is drawn at its due date, so a household that later leaves repays at the
#      same rate as one that stays. Final-account debt recovers far worse (Centrica ARA 2025 Note
#      17: 84-88% provisioned), so this overstates what leavers repay.
#   8. SELECTION (narrowed 2026-10-09). The 0.5 is the share for customers BLOCKED FROM SWITCHING
#      by debt, and no published source gives the ordinary failed bill's share or curve (searched
#      2026-10-09: Ofgem indicators, SOR, debt-costs papers, Energy UK, StepChange, Citizens Advice;
#      see SEAT_FINDING_THE_DD_FAILURE_CORRECTION_MOVED_MEASURED_FACTS). The never-repaid share is
#      now `NEVER_REPAID_SHARE_BY_METHOD`: one supplier's (Centrica's) expected-loss provision on
#      live balances over 90 days old, by payment method. A method it does not report (prepayment)
#      keeps the cohort's 0.5. What that substitution carries is stated beside the table.

#: "just over half" of debt-blocked domestic customers had repaid by the time of reporting -- read
#: at its floor. Ofgem IA July 2016 §1.39; domestic_debt_objection_rates_gb.md row 22. That is a
#: selected cohort, standing in for the ordinary failed bill's share, which is unpublished (gap 8).
LATER_SETTLEMENT_REPAID_SHARE = 0.5

#: P(a failed domestic bill not cured on re-presentation is never repaid), by payment method.
#: CITED, ONE SUPPLIER: Centrica plc ARA 2025 Note 17 p.175, UK residential, live accounts,
#: provision / gross on balances >90 days past invoice: Direct Debit 18/243 = 7.4%, payment on
#: receipt of bill 551/1,095 = 50.3% (`docs/market_research/
#: dd_failure_basis_and_live_arrears_provision_rates.md` C6). The world's standing order and card
#: are standard credit (`SEAM_CHANNEL_FOR_METHOD`), which is Centrica's pay-on-receipt row.
#:   WHAT IT COUNTS. An expected loss on a balance already past 90 days, so it applies here only
#:   to a bill that reaches 90 days unpaid. Every bill that takes this draw does: a re-presented
#:   DD is cured at day 14, and the earliest later settlement is due + 28 days + 3 months (about
#:   day 119). Nothing is charged the share at the moment it fails.
#:   WHICH WAY IT ERRS. (a) A provision is a STOCK rate by VALUE; old unpaid balances pile up in a
#:   stock, so the per-bill FLOW share is likely lower -- this overstates never-repaid. (b) One
#:   supplier, one year (2024 read 4.4% for DD). (c) A provision is a belief, not an outcome.
#: Prepayment has no Centrica row and keeps the debt-blocked cohort's share.
NEVER_REPAID_SHARE_BY_METHOD = {
    DIRECT_DEBIT: 18 / 243,
    STANDING_ORDER: 551 / 1095,
    CARD: 551 / 1095,
    PAY_ON_RECEIPT_METHOD: 551 / 1095,
}


def never_repaid_share(payment_method: str) -> float:
    """The never-repaid share for a failed bill on `payment_method` (see the table above)."""
    return NEVER_REPAID_SHARE_BY_METHOD.get(payment_method, 1 - LATER_SETTLEMENT_REPAID_SHARE)

#: "Around 70% of those that had paid off their debt ... did so within three months." Same source.
LATER_SETTLEMENT_WITHIN_FIRST_WINDOW_SHARE = 0.7

#: The first window, "within three months". Same source.
LATER_SETTLEMENT_FIRST_WINDOW_MONTHS = 3

#: The longer of the two cohorts' spans to the report: blocked November 2013, reported September
#: 2015. Computed from those months, never typed. Same source, §1.38-1.39.
LATER_SETTLEMENT_REPORTING_WINDOW_MONTHS = (2015 * 12 + 9) - (2013 * 12 + 11)

#: P(a returned DD is collected on re-presentation): register `dd_representation_success_share`,
#: an ESTIMATE (GoCardless 22%-70%; gb_domestic_bill_payment_failure_and_arrears_prevalence.md
#: s.(e) item 2). Tied to the first-presentation rate: a bracket run moves both together.
REPRESENTATION_SUCCESS_SHARE: float = assumption_toggle("dd_representation_success_share")

#: British Gas re-presents a returned DD after 14 days, then cancels it
#: (`docs/market_research/debt_and_collections.md` row P1). Inside SLC 14's 28 days.
REPRESENTATION_DAYS_AFTER_DUE = 14

_LATER_SETTLEMENT_SUBSTREAM_BASE = "later_settlement"  # + "::<period_index>"
#: Its own substream, so a bill that is NOT cured on re-presentation draws exactly the later
#: settlement it drew before re-presentation existed.
_REPRESENTATION_SUBSTREAM_BASE = "dd_representation"  # + "::<period_index>"


def _add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise AssertionError("every month has a 28th")


def later_settlement_date(event: PaymentEvent, segment: str = "resi",
                          seed: Optional[int] = None) -> Optional[date]:
    """The date the world's household pays an unpaid domestic bill off, or None if it does not.

    Only a domestic `failed` bill is ever settled here: a paid or late bill already carries its
    payment date, and a business failure or dispute has no sourced cure. Drawn from its own
    period-isolated substream, so it never moves `generate_payment_event`'s draws or any other
    period's. See the block above for the sources and the eight named gaps.

    A returned Direct Debit is first re-presented: collected `REPRESENTATION_DAYS_AFTER_DUE` after
    its due date with probability `REPRESENTATION_SUCCESS_SHARE`, from its own substream. The
    bill's record stays `failed` (the return happened and the supplier saw it); only its
    settlement date changes. One not cured has passed 90 days unpaid by its earliest settlement,
    and is never repaid with its method's `never_repaid_share`.
    """
    if event.result != "failed" or is_business(segment):
        return None
    base_seed = _base_seed_for(event.customer_id, seed)
    if event.payment_method == DIRECT_DEBIT:
        r = _period_substream(base_seed, _REPRESENTATION_SUBSTREAM_BASE,
                              event.period_index).random()
        if r < REPRESENTATION_SUCCESS_SHARE:
            return date.fromisoformat(event.due_date) + timedelta(days=REPRESENTATION_DAYS_AFTER_DUE)
    from simulation.debt_objection import DEBT_OBJECTION_MIN_DAYS_OUTSTANDING
    objectionable_from = (date.fromisoformat(event.due_date)
                          + timedelta(days=DEBT_OBJECTION_MIN_DAYS_OUTSTANDING))
    u = _period_substream(base_seed, _LATER_SETTLEMENT_SUBSTREAM_BASE, event.period_index).random()
    repaid = 1 - never_repaid_share(event.payment_method)
    if u < repaid * LATER_SETTLEMENT_WITHIN_FIRST_WINDOW_SHARE:
        return _add_months(objectionable_from, LATER_SETTLEMENT_FIRST_WINDOW_MONTHS)
    if u < repaid:
        return _add_months(objectionable_from, LATER_SETTLEMENT_REPORTING_WINDOW_MONTHS)
    return None


def arrears_age_days(due_date: str, as_of_date: str, payment_date: Optional[str]) -> int:
    """Pure ageing calc: days the amount has been outstanding past its due
    date, as of `as_of_date`. 0 if paid on/before `as_of_date` (or not yet
    due). Never negative."""
    due = date.fromisoformat(due_date)
    as_of = date.fromisoformat(as_of_date)
    if payment_date is not None:
        paid = date.fromisoformat(payment_date)
        if paid <= as_of:
            return 0
    age = (as_of - due).days
    return max(0, age)


def ageing_bucket(age_days: int) -> str:
    """Standard 30/60/90-day ageing bucket (matches the buckets
    H27_payment_belief_gap's FRAME names: 30/60/90+)."""
    if age_days <= 0:
        return "current"
    if age_days <= 30:
        return "0-30"
    if age_days <= 60:
        return "31-60"
    if age_days <= 90:
        return "61-90"
    return "90+"


def classify_payment_pattern(events: Sequence[PaymentEvent]) -> str:
    """Classify a customer's realised payment-event HISTORY into a pattern:
    CHRONIC (persistently late/failed), TRANSIENT (an isolated lapse), or
    CONSISTENT_ON_TIME. Purely DERIVED from already-drawn outcomes (no new
    RNG draw -- the classification is a deterministic function of the
    realised sequence, so it needs no substream of its own)."""
    if not events:
        return "CONSISTENT_ON_TIME"
    problem_count = sum(1 for e in events if e.is_late or e.is_unresolved)
    rate = problem_count / len(events)
    if rate == 0.0:
        return "CONSISTENT_ON_TIME"
    if rate >= 0.5:
        return "CHRONIC"
    return "TRANSIENT"


@dataclass(frozen=True)
class CustomerPaymentProfile:
    """A customer's full payment-behaviour truth over a billing history --
    the object H27_payment_belief_gap scores the company's D5 belief
    against. Never read by company/saas code directly (epistemic wall);
    the future W4_4 seam is the only sanctioned crossing point."""
    customer_id: str
    payment_method: str
    events: tuple  # tuple[PaymentEvent, ...]
    pattern: str
    data_regime: str = "synthetic"

    def ageing_as_of(self, as_of_date: str) -> dict:
        """{period_index: (age_days, bucket)} as of a given date -- the TRUTH
        H27 compares the company's inferred ageing against."""
        out = {}
        for e in self.events:
            age = arrears_age_days(e.due_date, as_of_date, e.payment_date)
            out[e.period_index] = (age, ageing_bucket(age))
        return out


def generate_customer_payment_history(
    customer_id: str,
    due_dates_amounts: Sequence[tuple],
    stress_trajectory: Optional[Sequence[dict]] = None,
    segment: str = "resi",
    fuel: str = "electricity",
    seed: Optional[int] = None,
) -> CustomerPaymentProfile:
    """Generate a customer's full payment-behaviour truth.

    `due_dates_amounts`: sequence of (date, amount_gbp) for each billing
    period, in period order.
    `stress_trajectory`: optional list of {"year": int, "stress": str}
    (same shape `simulation.household_demand.income_stress_trajectory`
    already produces) -- the SAME hardship substrate this module couples to
    (FRAME instruction), never a new one. Defaults every period to "low" if
    omitted or no matching year is found (I&C/SME segments have no household
    stress and should simply omit this argument).
    """
    method = generate_payment_method(customer_id, fuel=fuel, seed=seed)

    def _stress_for_year(year: int) -> str:
        if not stress_trajectory:
            return "low"
        for entry in stress_trajectory:
            if entry.get("year") == year:
                return (entry.get("stress") or "low")
        return "low"

    events = []
    for idx, (due_date, amount_gbp) in enumerate(due_dates_amounts):
        stress = _stress_for_year(due_date.year)
        ev = generate_payment_event(
            customer_id, idx, due_date, amount_gbp, stress, method,
            segment=segment, seed=seed,
        )
        events.append(ev)

    pattern = classify_payment_pattern(events)
    return CustomerPaymentProfile(
        customer_id=customer_id,
        payment_method=method,
        events=tuple(events),
        pattern=pattern,
    )
