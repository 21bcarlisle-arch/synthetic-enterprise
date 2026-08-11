"""COUPLED-TRIAD runner for the W2_11 <-> D5 pair -- payment belief-vs-truth
(atom H27_payment_belief_gap). Fourth piece of the D5 decomposition: W2_11
source / W4_4 seam / D5 consumption / **H27 gap (this module)**.

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the
ONLY layer permitted to hold the hidden SIM truth (`PaymentEvent`, generated
straight from `simulation.payment_behaviour_source`) and the company's
observable-only belief (`PaymentBeliefSnapshot`, built by
`company.billing.payment_observation_consumer.PaymentObservationConsumer`
from nothing but `WallResponse`s crossing the W4_4 seam) side by side to
compute the belief-vs-truth GAP (COUPLED_TRIAD_DESIGN.md 1.3). It lives in
tools/ -- NOT under company/ or saas/ -- so it is not scanned by the
epistemic verifier and may legitimately import ``simulation.*``.

THE COUPLED LOOP (3 loops):

  1. SIM adds depth   -- `simulation.payment_behaviour_source` generates each
                         customer's payment TRUTH (on-time / late / DD-failed
                         / non-DD-failed, and the true DD-failure reason)
                         from a stress-varying resi population.
  2. COMPANY copes    -- the truth crosses the W4_4 seam
                         (`simulation.payment_seam_adapter.emit_wall_responses`)
                         into `WallResponse`s -- the ONLY thing the company
                         ever sees. `PaymentObservationConsumer` turns that
                         stream into belief: cash allocation (via the shared
                         ledger), ageing, and a naive `arrears_risk_belief`
                         built purely from OBSERVED DD-failure/rail-failure
                         counts.
  3. HARNESS measures -- this module scores the gap on THREE dimensions
                         (detection, belief, ageing -- see METRIC CHOICE
                         below), using `background.gap_metric`'s existing
                         scorers, never a bespoke metric.

THE BLIND SPOT THIS SCENARIO IS BUILT TO EXPOSE (C-S1, adapter docstring):
a FAILED non-Direct-Debit payment (standing_order/card/prepayment) produces
NO WallResponse at all -- a real supplier's bank feed has nothing to report
for a missed push-payment. `PaymentObservationConsumer.arrears_risk_belief`
is built ONLY from OBSERVED DD/rail failures, so it structurally CANNOT see
these. Truth still contains them (this harness reads `PaymentEvent.result`
directly). That structural asymmetry is what the detection and belief gaps
below measure -- and per R12/R13 a near-zero gap here would be a RED FLAG
(a leak), never a success.

METRIC CHOICE per dimension (design section 1.4, "pick the shape that fits"):
  * DD-failure detection -> `detection_gap` (formula d). truth_set = every
    (customer, period) that TRULY failed to pay (any channel -- DD or not);
    flagged_set = every (customer, period) the company's belief shows as an
    OBSERVED DD failure (`PaymentBeliefSnapshot.recent_dd_failures`, matched
    back to its period by `value_date`). The no-remittance blind spot means
    every non-DD failure is a guaranteed miss -> gap > 0 by construction, not
    by tuning (R12).
  * arrears/cash-position -> `belief_gap` (formula c, TV distance). Each
    customer gets a FOUR-LEVEL severity label (normal/watch/elevated/high)
    computed by the SAME thresholding shape `PaymentObservationConsumer.
    _arrears_risk_belief` uses (count of unresolved failures, amplified by a
    hardship-suggestive reason) -- applied TWICE, independently: once to the
    TRUTH's full failure count (every channel, this harness's own read of
    `PaymentEvent`), once read straight off the company's own
    `arrears_risk_belief` (DD/rail-observed count only). Same rule, two
    different-coverage inputs -- the R15 independence pattern the W2_9<->C11
    pair already established, not a tautology (the rule is not re-deriving
    its own answer from its own inputs).
  * ageing -> `ageing_gap` (formula g, atom D7_ageing_gap_metric_reshape).
    Per invoice, the TRUE 30/60/90+ bucket (this module's own `_ageing_bucket`,
    applied to the true "did this genuinely resolve by as_of" fact) vs the
    BELIEF bucket read off the company's own open-item ageing
    (`PaymentObservationConsumer.snapshot().aged_items`).
    THE TWO SIDES RUN THE SAME RULE OVER DIFFERENT COVERAGE, and until
    2026-08-10 they ran the same rule because the truth side IMPORTED the
    organ's `age_bucket` (atom D21, H27 Expert Hour #5). That made the
    dimension whose subject is debt DATING structurally unable to see a
    company dating error -- `wrong_bucket` was 0 by construction, not by luck
    -- and it sat under a `COVERAGE_ONLY_CLAIM_CONTRACT` exemption asserting
    the opposite of this paragraph. The rule is now harness-owned and pinned
    against the organ's; the dimension is enrolled in the coverage-only
    control, where it measures a residual of exactly 0 and an organ-only
    dating drift takes it off 0.
    THIS DIMENSION USED `misapplication_gap` AND NO LONGER DOES. The D6
    DISCOVER (docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md) refuted
    that shape three ways against the unchanged criterion: gap>1 did NOT mean
    worse-than-no-skill; prevalence alone swung the score twentyfold with the
    company held literally fixed; and a Hamming error rate is blind to bucket
    ORDER (believing a 90+ debt is 60-90 scored the same as not seeing it).
    The buckets are ORDERED, so the dimension now reports date DISPLACEMENT
    plus the two error directions on their own denominators -- understated
    (debt believed settled) and overstated (the ageing REPORT's overstatement
    at `as_of`; NOT the wrongful-dunning exposure, which the detection
    dimension publishes -- atom D16) -- and carries no prevalence-shaped
    baseline at all. Both directions are scored over the SAME never-flaggable
    band the detection dimension uses, since D16.
  * allocation -- ATTEMPTED, HONESTLY DROPPED (see module note "ON
    ALLOCATION" below): `misapplication_gap`'s no-skill baseline needs a
    SMALL shared label space; a per-invoice `invoice_ref` is effectively
    unique per (customer, period), so a "majority class" over that space is
    meaningless (every class has count 1). Rather than force an ill-fitting
    metric, this scenario still SEEDS the real-world mechanism that would
    drive an allocation gap (non-DD payments carry an AMBIGUOUS,
    account-level `correlation_id` -- no invoice-specific remittance advice,
    same as a real standing-order/card payment that quotes no reference --
    forcing the ledger's oldest-first fallback, `AccountLedger.allocate`)
    and its real-world CONSEQUENCE surfaces honestly in the ageing gap above
    (a misallocated payment shows one invoice believed-settled that's truly
    still open, or vice versa). See `measure()`'s returned `notes` for the
    honest flag.

R15 INDEPENDENCE. `PaymentObservationConsumer` never receives `PaymentEvent`,
`stress`, `segment`, or any generator-internal field -- ONLY `WallResponse`
objects produced by `emit_wall_responses` (itself proven non-invertible by
`payment_seam_adapter.py`'s own docstring/tests). This harness never reads
`PaymentBeliefSnapshot` back into anything the generator consumes. The two
severity-threshold applications above use the SAME rule shape on DIFFERENT
COVERAGE inputs (truth sees every channel; belief sees only what the wall
lets through) -- independence via differing information, not a checked value
derived from the same source it grades (`tests/tools/
test_couple_w2_11_d5.py::test_consumer_never_receives_theta` proves the
harness's own usage, on top of the consumer module's own existing AST-based
import-freedom test).

DETERMINISM (C-S2). `--seed` salts the CUSTOMER_ID NAMESPACE this module
generates (`H27S<seed>C<i>`), never `payment_behaviour_source`'s own `seed`
parameter -- that module's `_base_seed_for` treats an explicit non-None seed
as a GLOBAL override (every customer would collapse onto the identical
base_seed, and therefore the identical draw per period, breaking the exact
per-customer C-S2 isolation this module must preserve). Every generator call
here leaves `seed=None`, so each customer still gets its own stable
hash-of-customer_id substream -- salting only the namespace still gives
`--seed` a real, reproducible effect on which population is drawn. No
wall-clock, no unseeded randomness anywhere in this module's own
scenario-building or gap math; `measured_at`/`run_git_commit` for the ledger
are gathered here (gap_metric never calls a clock).

R13 CURRICULUM NOTE. The stress-tier population mix below (`_STRESS_MIX`) is
a frozen, illustrative harness population (matching the style the W2_9<->C11
runner already uses for its segment mix) -- not a director-authored
curriculum artefact, and not tuned toward any gap number (R12/R13); it exists
only to generate a population with a real mixture of on-time / DD-failed /
non-DD-failed cases so the mechanism above has something to measure.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import random
import re
import subprocess
import sys
import textwrap
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from simulation.payment_behaviour_source import (
    DIRECT_DEBIT,
    INSUFFICIENT_FUNDS,
    generate_payment_event,
    generate_payment_method,
)
from simulation.payment_seam_adapter import SeamAdapterInput, emit_wall_responses

from company.billing.account_ledger import (
    LedgerBook,
    LedgerEvent,
    LedgerEventType,
)
from company.billing.payment_observation_consumer import (
    DEFAULT_RECONCILIATION_GRACE_DAYS,
    PaymentObservationConsumer,
)

from background.gap_metric import (
    GapResult,
    ageing_gap,
    belief_gap,
    belief_measures,
    detection_measures,
    format_ageing_summary,
    format_belief_summary,
    format_detection_summary,
    write_gap_entry,
)
# The shared-quantity CLASS register (R10) lives outside this module on purpose
# -- see its own docstring. Re-exported here because this triad is its first
# registrant and its consumers read it through the pair.
from background.shared_quantity_contract import (   # noqa: F401
    SHARED_QUANTITY_CONTRACT,
    shared_quantity_measurements,
)

WORLD_ATOM_ID = "W2_11_payment_behaviour_source"
TWIN_ATOM_ID = "D5_account_hierarchy_payments"

# ---------------------------------------------------------------------------
# Scenario constants -- frozen, illustrative harness scaffolding (R13-style;
# not a baseline-world fidelity claim, not director curriculum).
# ---------------------------------------------------------------------------

N_PERIODS = 3
PERIOD_SPACING_DAYS = 21
FIRST_DUE_DATE = date(2024, 1, 15)
PAYMENT_TERMS_DAYS = 14          # matches account_ledger/arrears_engine's own default
BILL_AMOUNT_GBP = 120.0
AS_OF_BUFFER_DAYS = 30           # comfortably past payment_terms + the ARUDD lag window
# Generous on purpose: isolates the CHANNEL blind spot as the thing this
# scenario measures, rather than letting the belief's own recency-decay
# window (default 90d in PaymentObservationConsumer) confound the reading.
DD_FAILURE_WINDOW_DAYS = 400

# ---------------------------------------------------------------------------
# THE STAGGERED BILLING BOOK (atom D25_ageing_resolution_is_the_harness_calendar)
# ---------------------------------------------------------------------------
# WHY THIS EXISTS, and it is a RESOLUTION change, never a tuning (R12). Before
# this constant every customer in the book fell due on the SAME three dates, so
# at `as_of` every truly-overdue invoice sat at exactly one of {30, 51, 72}
# days overdue -- three distances, all of them arithmetic over FIRST_DUE_DATE,
# PERIOD_SPACING_DAYS, N_PERIODS and AS_OF_BUFFER_DAYS. The AGEING dimension
# publishes BUCKETS of ordinal displacement (30/60/90), so it can only see a
# company's dating error where that error carries an invoice ACROSS a bucket
# boundary -- and against a book with three ages, that made the smallest
# visible company error a property of the HARNESS's calendar rather than of the
# company being graded. Measured under the declared `organ_terms_drift_days`
# counterfactual (Expert Hour #8, seeds 7/11/23, bit-identical): a supplier
# dating every debt 1 TO 8 DAYS OLDER than the world did -- over-ageing, the
# direction that posts an early dunning letter -- published a BIT-IDENTICAL
# headline, and companies +1d and +12d out published ONE number.
#
# The real-world twin is the whole point: a collections MI pack built from one
# month-end snapshot of a book that all falls due on the same day cannot tell a
# team dating its debts a week early from one dating them right. Real suppliers
# do not bill like that -- a domestic book is spread across the billing cycle,
# one cohort of accounts per working day -- so the fidelity fix and the
# resolution fix are the same change: give each account its own place in the
# cycle. The book then presents a CONTIGUOUS span of ages at `as_of` instead of
# three, every bucket boundary has invoices sitting next to it, and a one-day
# dating error moves the published figure in both directions.
#
# NOT A DIAL ON THE OUTPUT. The spread is the cycle length itself -- accounts
# are distributed over exactly one `PERIOD_SPACING_DAYS` window, the only
# non-arbitrary choice available -- and it was fixed before any post-reshape
# figure was read. R13: this changes the harness's illustrative scaffolding
# (which customers get billed when), not a baseline-world fidelity claim and
# not director curriculum.
BILLING_CYCLE_SPREAD_DAYS = PERIOD_SPACING_DAYS


def _billing_cycle_offset(customer_id: str, spread_days: int) -> int:
    """This account's place in the billing cycle, in days after
    `FIRST_DUE_DATE` -- a deterministic per-customer draw from its OWN named
    substream (C-S2), so adding it never shifts `_pick_stress`,
    `generate_payment_method` or `generate_payment_event`'s draws.

    `spread_days == 1` is the FLAT BOOK: every account falls due on the same
    three dates, which is the pre-D25 scenario and is kept reachable as a
    DECLARED counterfactual population (see `build_scenario`'s
    `cycle_spread_days`) so the resolution this atom bought can be measured
    against the book that did not have it."""
    key = f"h27_billing_cycle:{customer_id}"
    draw = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
    return draw % spread_days

# Illustrative stress-tier population mix (harness scaffolding, see module
# docstring's R13 CURRICULUM NOTE) -- gives a real mixture of on-time /
# DD-failed / non-DD-failed cases across the population.
_STRESS_MIX = (("low", 0.55), ("moderate", 0.30), ("high", 0.15))

_SEVERITY_ORDER = ("normal", "watch", "elevated", "high")


def _pick_stress(customer_id: str) -> str:
    """Deterministic stress-tier draw from `_STRESS_MIX`, seeded per customer
    (C-S2, named substream -- independent of payment_behaviour_source's own
    substreams, this harness's own draw)."""
    key = f"h27_stress_mix:{customer_id}"
    draw = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big") / float(1 << 64)
    cum = 0.0
    for tier, share in _STRESS_MIX:
        cum += share
        if draw < cum:
            return tier
    return _STRESS_MIX[-1][0]


def _severity_label(n_unresolved: int, n_hardship: int) -> str:
    """The SAME thresholding shape
    `PaymentObservationConsumer._arrears_risk_belief` uses, applied here to
    whatever (unresolved-count, hardship-count) pair the caller supplies --
    the TRUTH side feeds it the full-channel count; the BELIEF side reads the
    company's own `arrears_risk_belief` directly (see `measure()`). Mirroring
    the rule, not re-deriving the answer from the same inputs, is the R15
    independence pattern (identical to the W2_9<->C11 pair: same rule,
    different-coverage source)."""
    if n_unresolved == 0:
        return "normal"
    if n_unresolved == 1:
        return "watch"
    if n_unresolved == 2:
        return "high" if n_hardship >= 2 else "elevated"
    return "high"


def _ageing_bucket(days_overdue: int) -> str:
    """The HARNESS's own 30/60/90+ dating rule for the ageing dimension's TRUTH
    side (atom `D21`, H27 Expert Hour #5, 2026-08-10).

    Until this function existed the truth side CALLED
    `company.billing.arrears_engine.age_bucket` -- the company organ's own
    function, imported at module scope -- against a `days_overdue` the scenario
    constructs to be the same integer the organ computes (world
    `issue = due - PAYMENT_TERMS_DAYS`; organ `due = issue_date +
    payment_terms_days`, same 14). Same rule, same input: the two sides could
    not disagree about the bucket of an invoice they both held open, and
    `wrong_bucket` measured 0 at every seed and under every drift tried because
    it was 0 by construction. Worse than the D20 hand-copy, which could at
    least drift apart and be caught: an EDIT to the organ's `age_bucket` moved
    the harness's notion of ground truth with it, so the harness would have
    certified the company's dating correct by definition -- R15's TAUTOLOGY
    pattern, the checked value derived from the source it checks.

    `background.gap_metric` had already written this discipline down for the
    bucket ORDER -- "Redeclared here rather than imported: `background/` is
    harness code and must not take a company import for a constant", pinned
    against the company's by `test_d7_ageing_measures.py` -- and the same
    dimension imported the bucket RULE anyway.

    So: redeclared here, and PINNED against the organ's rule by
    `test_the_truth_side_dating_rule_is_pinned_against_the_organs`, which fails
    loudly and NAMES the divergence if either side moves. R12: logically
    identical to the organ's rule at HEAD, so no published number moves.
    """
    if days_overdue >= 90:
        return "90+"
    if days_overdue >= 60:
        return "60-90"
    if days_overdue >= 30:
        return "30-60"
    return "current"


def _severity_distribution(labels: List[str]) -> List[float]:
    counts = {s: 0 for s in _SEVERITY_ORDER}
    for lbl in labels:
        counts[lbl] += 1
    n = len(labels)
    return [counts[s] / n for s in _SEVERITY_ORDER]


class PeriodRecord:
    """One (customer, period) case's TRUTH -- harness-only, never handed to
    the consumer directly. Only the `WallResponse`(s) built from it cross the
    wall."""

    __slots__ = (
        "customer_id", "period_index", "invoice_ref", "account_id",
        "due_date", "issue_date", "payment_method", "result",
        "dd_failure_reason", "correlation_id", "days_late",
    )

    def __init__(self, customer_id, period_index, invoice_ref, account_id,
                 due_date, issue_date, payment_method, result,
                 dd_failure_reason, correlation_id, days_late=None):
        self.customer_id = customer_id
        self.period_index = period_index
        self.invoice_ref = invoice_ref
        self.account_id = account_id
        self.due_date = due_date
        self.issue_date = issue_date
        self.payment_method = payment_method
        self.result = result
        self.dd_failure_reason = dd_failure_reason
        self.correlation_id = correlation_id
        # HOW LATE the cash actually arrived, days after `due_date` (atom D11).
        # Carried because the detection dimension's FALSE-FLAG denominator needs
        # it: an invoice paid 20 days late was genuinely unpaid past its grace
        # date, so the company flagging it was CORRECT, not wrongful dunning --
        # and scoring it as a false flag would punish the company for being
        # right. `None` means UNKNOWN, never "paid on time": an unknown case is
        # excluded from the denominator with a published witness rather than
        # quietly counted as one the company should not have flagged.
        self.days_late = days_late


def build_scenario(
    n_customers: int, seed: Optional[int] = None,
    force_payment_method: Optional[str] = None,
    cycle_spread_days: Optional[int] = None,
    organ_failure_window_drift_days: int = 0,
) -> Tuple[List[PeriodRecord], PaymentObservationConsumer, LedgerBook, date]:
    """Run the coupled loop over `n_customers` resi households x `N_PERIODS`
    billing periods each. Returns (truth_records, consumer, ledger_book,
    as_of). The consumer is fed EXCLUSIVELY through
    `simulation.payment_seam_adapter.emit_wall_responses` -- it never sees a
    `PeriodRecord`/`PaymentEvent` (R15 independence, proven in the test
    suite's `test_consumer_never_receives_theta`).

    `force_payment_method` overrides `generate_payment_method` for every
    customer. It exists for ONE named purpose -- the COUNTERFACTUAL population
    `measure_coverage_only_residual` needs (atom `D20`), on which the company
    observes every failure channel -- and is never used by the scored
    population. It is a declared parameter rather than a monkeypatch precisely
    so the counterfactual is legible in the repo (IaC) instead of living in a
    test's `setattr`. R13: it does NOT change the baseline world; it builds a
    SECOND, explicitly-labelled world used only to isolate one term.

    `cycle_spread_days` overrides `BILLING_CYCLE_SPREAD_DAYS` -- how many days
    of the billing cycle the book is spread over. It exists for ONE named
    purpose too: `cycle_spread_days=1` is the FLAT BOOK, every account due on
    the same three dates, which is the population this pair scored before atom
    D25 and the one whose ageing headline could not see a working week of
    over-ageing. `measure_ageing_resolution` is run against BOTH so the
    resolution claim is differential rather than a bare assertion about the
    shipped book. Declared here rather than monkeypatched for the same D20
    reason as `force_payment_method`. Never used by the scored population.

    `organ_failure_window_drift_days` is the THIRD declared counterfactual
    company (atom D27, Expert Hour #9): the supplier holds the wrong DD/rail
    FAILURE LOOKBACK WINDOW -- how far back its arrears-severity belief
    remembers a failed collection -- so it counts `DD_FAILURE_WINDOW_DAYS + k`
    days of history instead of the harness's declared window. k < 0 is a
    supplier that FORGETS sooner; k > 0 one that never lets a failure go (the
    direction that keeps a recovered customer in collections). It is the only
    counterfactual in this harness that reaches the two BELIEF dimensions'
    organ: `_arrears_risk_belief` counts observed failure EVENTS inside this
    window and reads no dating at all, which is why the terms drift (D25) and
    the reconciliation drift (D23) both leave it untouched -- and why, until
    this knob existed, those two dimensions had NO graded probe and no measured
    resolution at all. It lives on the CONSTRUCTOR rather than on `score_triad`
    because the window is a property of the consumer, not of a read taken from
    it -- so this counterfactual company must be BUILT, and the world it is
    built over comes out bit-identical (asserted by
    `measure_own_drift_resolution`; R13: a second labelled COMPANY, never a
    second world). Default 0 -- the scored book is never drifted."""
    spread = (BILLING_CYCLE_SPREAD_DAYS if cycle_spread_days is None
              else cycle_spread_days)
    if spread < 1:
        raise ValueError(f"cycle_spread_days must be >= 1, got {spread}")
    window_days = DD_FAILURE_WINDOW_DAYS + organ_failure_window_drift_days
    if window_days < 0:
        raise ValueError(
            f"organ_failure_window_drift_days="
            f"{organ_failure_window_drift_days} takes the company's lookback "
            f"window to {window_days} days -- a negative memory is not a "
            "company this harness can build"
        )
    ledger_book = LedgerBook()
    consumer = PaymentObservationConsumer(
        ledger_book=ledger_book, dd_failure_window_days=window_days
    )
    records: List[PeriodRecord] = []

    # `seed` salts the CUSTOMER_ID NAMESPACE only -- it is never forwarded as
    # payment_behaviour_source's own `seed` argument. That module's
    # `_base_seed_for` treats an explicit non-None seed as a GLOBAL override
    # (every customer would collapse onto the SAME base_seed, and therefore
    # the SAME draw per period regardless of customer -- the exact C-S2
    # per-customer isolation this harness must not break). Leaving
    # `seed=None` on every generator call keeps its own hash-of-customer_id
    # fallback (stable across processes), and salting the namespace here
    # gives `--seed` real, reproducible effect on WHICH population is drawn
    # without touching the generator's isolation contract -- the same
    # pattern the W2_7<->C9 / W2_9<->C11 template runners rely on.
    namespace = f"H27S{seed if seed is not None else 0}"

    for i in range(n_customers):
        cid = f"{namespace}C{i:06d}"
        stress = _pick_stress(cid)
        method = (force_payment_method if force_payment_method is not None
                  else generate_payment_method(cid, fuel="electricity"))
        account_id = f"ACC-{cid}"

        # This account's place in the billing cycle (atom D25): the book is
        # spread across one cycle rather than all falling due on the same day,
        # so the ages the ageing dimension reads at `as_of` are a contiguous
        # span and not three harness constants.
        cycle_offset = _billing_cycle_offset(cid, spread)

        for p in range(N_PERIODS):
            due = FIRST_DUE_DATE + timedelta(
                days=PERIOD_SPACING_DAYS * p + cycle_offset)
            issue = due - timedelta(days=PAYMENT_TERMS_DAYS)
            invoice_ref = f"{cid}::{p}"

            event = generate_payment_event(
                cid, p, due, BILL_AMOUNT_GBP, stress, method,
                segment="resi",
            )

            ledger_book.post(LedgerEvent(
                event_id=f"bill:{cid}:{p}",
                account_id=account_id,
                event_type=LedgerEventType.BILL_DEBIT,
                amount_gbp=BILL_AMOUNT_GBP,
                valid_time=issue,
                transaction_time=datetime.combine(issue, time(0, 0)),
                invoice_ref=invoice_ref,
            ))

            # DD payments carry a period-specific remittance (a real DD
            # mandate collects against a specific billed amount/date), so
            # `correlation_id == invoice_ref` and remittance-directed
            # allocation matches the true invoice exactly. Non-DD methods
            # (standing_order/card/prepayment) carry a STILL-UNIQUE-per-
            # period correlation_id (idempotent dedup, C-S2, needs a fresh
            # id per event -- reusing one across periods would silently
            # drop repeat payments, not model ambiguity) that deliberately
            # does NOT match any real `invoice_ref` string -- no
            # invoice-specific remittance advice, matching a real
            # customer-initiated push payment that quotes no reference.
            # This is the seed for the ledger's oldest-first fallback (see
            # module docstring's "ON ALLOCATION" note); it is NOT a change
            # to the adapter's own truth->observable mapping, only to the
            # caller-supplied identifiers the adapter accepts.
            if method == DIRECT_DEBIT:
                correlation_id = invoice_ref
            else:
                correlation_id = f"{cid}::p{p}::ambiguous"
            seam_input = SeamAdapterInput(account_id=account_id, correlation_id=correlation_id)

            for response in emit_wall_responses(event, seam_input):
                consumer.observe(response)

            records.append(PeriodRecord(
                customer_id=cid, period_index=p, invoice_ref=invoice_ref,
                account_id=account_id, due_date=due, issue_date=issue,
                payment_method=method, result=event.result,
                dd_failure_reason=event.dd_failure_reason,
                correlation_id=correlation_id,
                days_late=event.days_late,
            ))

    # `as_of` is taken from the LATEST due date the cycle can produce, not from
    # the latest one this draw happened to produce: AS_OF_BUFFER_DAYS means
    # "every account's newest invoice is at least this far past due" (its stated
    # job -- clearing payment_terms + the ARUDD lag window for everyone), and a
    # population-dependent `as_of` would quietly shorten that for a small n and
    # make the reading depend on how many customers were drawn.
    last_due = FIRST_DUE_DATE + timedelta(
        days=PERIOD_SPACING_DAYS * (N_PERIODS - 1) + spread - 1)
    as_of = last_due + timedelta(days=AS_OF_BUFFER_DAYS)
    return records, consumer, ledger_book, as_of


# ---------------------------------------------------------------------------
# DETECTION LATENCY (atom D10_detection_headline_is_single_channel)
# ---------------------------------------------------------------------------
# WHY THIS DIMENSION EXISTS. The 2026-08-08 HARDEN pass measured that the
# published DETECTION headline is insensitive to the entire DD-observation
# channel: `flagged_set` is a UNION, `n_flagged_via_dd_channel_only == 0`, so
# deleting the DD channel outright leaves the number bit-identical. That is
# structurally correct -- a rail failure means the cash did not arrive, which
# expected-collection reconciliation also sees -- but it means pure
# set-membership cannot express the only thing the DD channel actually buys:
# EARLIER detection. This dimension gives that a shape.
#
# CORRECTION TO THE 2026-08-08 RESIDUAL (D10, measured not argued). That pass
# recorded, in this atom's simplification register and in its `channel_contri-
# bution` note, that "DD latency cannot be honestly measured in this scenario
# because the adapter emits `value_date == due_date` with no ARUDD lag". That
# claim is FALSE at HEAD and was a misread of the seam: `value_date` is the
# collection date, but `WallResponse.observed_at` -- carried verbatim onto
# `DDFailureObservation.observed_at` -- is the BANK-FEED REPORT date, and
# `payment_seam_adapter` already lags it by a per-case draw of
# `0..ARUDD_NOTIFICATION_LAG_DAYS` (simulation/bacs_rails.py, a cited real
# Bacs constant). Measured DD lags on this population are {0, 1, 2} days. The
# residual was named against the wrong field, so the measurement was available
# all along.
#
# NO NORMALISER, DELIBERATELY (the D7 lesson, applied before it could bite).
# D7 caught, by mutation, that any denominator counting the truth's class
# balance re-imports the prevalence defect whatever the numerator's shape. So
# the headline here is an ABSOLUTE mean in DAYS over the detected population,
# with no no-skill divisor at all, and the coverage witnesses ride beside it
# rather than inside it: an undetected failure is COUNTED, never imputed into
# the mean at some invented cap (that would let a collapse in detection buy a
# better-looking latency).
DETECTION_LATENCY_HEADLINE_UNITS = (
    "days from an invoice's due date to the company's FIRST knowledge of the "
    "shortfall, whichever channel got there first"
)
DETECTION_LATENCY_NO_NORMALISER_REASON = (
    "NONE. An absolute mean in days -- there is no no-skill divisor and no "
    "class-balance denominator anywhere in this measure (D7's mutation-caught "
    "trap: any normaliser counting the truth's class balance re-imports the "
    "prevalence defect whatever the numerator's shape). Undetected failures are "
    "reported as a COUNT beside the mean, never imputed into it."
)


def detection_latency_gap(
    dd_lag_days: Dict[Tuple[str, int], int],
    recon_lag_days: Dict[Tuple[str, int], int],
    *,
    n_true_failures: int,
    n_recon_detected_undated: int = 0,
    n_dd_observed_after_as_of: int = 0,
    n_recon_dated_at_issue_floor: int = 0,
) -> GapResult:
    """How LATE the company learns about a true payment failure, in days, and
    what the DD-observation channel buys in days (formula: absolute mean, no
    baseline).

    `dd_lag_days` / `recon_lag_days` map a truly-failed (customer, period) case
    to the days between its due date and that CHANNEL's first knowledge of it.
    The DD channel's date is `DDFailureObservation.observed_at` (the bank-feed
    report date, ARUDD-lagged at the seam); reconciliation's is the earliest
    date at which the company's OWN `expected_collection_misses` organ returns
    the invoice -- asked of the organ itself, never re-derived here (R15
    independence: a harness re-implementation of `due + grace` would be a
    tautology that could not fail if the organ's rule changed).

    WHAT "ASKED OF THE ORGAN" IS WORTH IS THE GRID IT IS ASKED ON (atom D23,
    2026-08-10). Until this tick that claim was true in FORM and empty in
    VALUE: the organ was asked at exactly ONE date per period, and that date
    was the harness's own `due + grace`, so every faster company published the
    `grace` PARAMETER back and a one-day-slower one was published as +21 days.
    The grid is now DAILY from the invoice's ISSUE date to `as_of`
    (`organ_query_dates`) -- 1-day resolution, and a lower bound that is the
    COMPANY's (it cannot know an unissued bill went unpaid) rather than the
    harness's. `n_recon_dated_at_issue_floor` counts the cases sitting on that
    floor, which are "at or before", not exact. `ORGAN_QUERY_GRID` re-measures
    what the reading can and cannot resolve on every run.

    THE POPULATION IS THE COMPARABLE ONE, and the exclusion is published, not
    silent: the headline and its counterfactual are both means over the cases
    reconciliation dates, so `mean_lag_days` and `mean_lag_days_without_dd_
    channel` differ ONLY in the channel, never in the population. A case only
    the DD channel detects would be lost entirely in the counterfactual world,
    so it is excluded from both means and reported as
    `n_detected_dd_channel_only` (measured 0 today -- it is the same quantity
    the set-membership headline's `n_flagged_via_dd_channel_only` reports).

    FAIL LOUD / VACUITY EXPLICIT (R15): with no dated detected failures the
    means are `None`, not 0.0, and `gap` is `None`. A vacuous population is not
    an instantaneous one.
    """
    dd_only = set(dd_lag_days) - set(recon_lag_days)
    population = sorted(set(recon_lag_days))
    n_pop = len(population)

    def _mean(values: List[int]) -> Optional[float]:
        return round(sum(values) / len(values), 6) if values else None

    with_dd = [
        min(recon_lag_days[c], dd_lag_days[c]) if c in dd_lag_days else recon_lag_days[c]
        for c in population
    ]
    without_dd = [recon_lag_days[c] for c in population]
    earlier_via_dd = [c for c in population
                      if c in dd_lag_days and dd_lag_days[c] < recon_lag_days[c]]

    mean_with = _mean(with_dd)
    mean_without = _mean(without_dd)
    days_earlier = (None if mean_with is None or mean_without is None
                    else round(mean_without - mean_with, 6))

    components: Dict[str, object] = {
        "mean_lag_days": mean_with,
        "median_lag_days": (sorted(with_dd)[len(with_dd) // 2] if with_dd else None),
        "max_lag_days": (max(with_dd) if with_dd else None),
        # THE COUNTERFACTUAL -- the whole point of the dimension. Same cases,
        # same organ, DD channel deleted. `detection_gap` moves by exactly zero
        # under this deletion; this moves by `dd_channel_days_earlier`.
        "mean_lag_days_without_dd_channel": mean_without,
        "dd_channel_days_earlier": days_earlier,
        "n_earliest_via_dd_channel": len(earlier_via_dd),
        # THE DD CHANNEL'S OWN LAG, published separately -- this is the ARUDD
        # notification window as the company actually experiences it, and it is
        # what makes the counterfactual above a reading rather than a constant.
        # A degenerate all-zero distribution here means the scorer has gone back
        # to reading `value_date` (the collection date) instead of `observed_at`
        # (the bank-feed report date) -- the exact misread that made the
        # 2026-08-08 pass believe this was unmeasurable.
        "dd_lag_days_mean": _mean([dd_lag_days[c] for c in sorted(dd_lag_days)]),
        "dd_lag_days_max": (max(dd_lag_days.values()) if dd_lag_days else None),
        "dd_lag_days_min": (min(dd_lag_days.values()) if dd_lag_days else None),
        # COVERAGE WITNESSES -- beside the mean, never inside it. A mean over a
        # collapsing detected population would otherwise improve as detection
        # got worse (fail-open).
        "n_true_failures": int(n_true_failures),
        "n_latency_population": n_pop,
        "n_undetected": int(n_true_failures) - n_pop - len(dd_only),
        "n_detected_dd_channel_only": len(dd_only),
        # PRECISION WITNESS: a case reconciliation reports at `as_of` but at
        # none of its candidate dates (an allocation reshuffle could do it).
        # Excluded from the means rather than dated by guess.
        "n_recon_detected_undated": int(n_recon_detected_undated),
        # FLOOR WITNESS (atom D23): cases first known on the invoice's own ISSUE
        # date -- the earliest a supplier can hold the belief at all. Those
        # readings are "at or before", so a mean over a mostly-floored
        # population is an UPPER bound on the company's speed, not a reading of
        # it. Beside the mean, never inside it.
        "n_recon_dated_at_issue_floor": int(n_recon_dated_at_issue_floor),
        # POINT-IN-TIME WITNESS: a DD failure whose bank-feed report date falls
        # AFTER `as_of` is not yet knowable and is not counted as knowledge.
        "n_dd_observed_after_as_of": int(n_dd_observed_after_as_of),
        "headline_units": DETECTION_LATENCY_HEADLINE_UNITS,
        "normalisation": DETECTION_LATENCY_NO_NORMALISER_REASON,
        # GRID RESOLUTION (atom D23) -- stamped AT SOURCE, so it reaches every
        # caller of this scorer rather than only the one whose Hour found it.
        # The recon arm resolves the organ to the DAY in both directions, and
        # since atom D24 that holds on both sides of the due date too (the
        # organ's clock is signed). What it cannot resolve is a detector faster
        # than the invoice's own ISSUE date -- a bound on what the company can
        # know, owned as such in the register rather than filed as a debt
        # nobody can close. Measured, not asserted --
        # `ORGAN_QUERY_GRID` and its control re-derive every number here on
        # every run, and `organ_improvement_is_visible` is READ FROM the
        # register rather than typed, so a reshape that lost the property again
        # could not leave this claim standing.
        # ...AND IN THIS FIGURE'S OWN UNITS, NOT THE SUB-READING'S (atom D32,
        # Expert Hour #14). The register measures
        # `mean_lag_days_without_dd_channel` and resolves it day for day; this
        # headline is `mean_lag_days` and moves about a THIRD of that, because
        # a case the DD channel saw first does not move when the reconciliation
        # detector does. The caveat used to report the 1.0 as what "is
        # published", so a reader converting a movement into days of company
        # error understated it threefold.
        "organ_query_grid_caveat": organ_query_grid_caveat(
            published_step=predict_published_latency_step_days(
                n_pop, len(earlier_via_dd))),
        # The step BESIDE the sentence, so the number a reader converts with is
        # falsifiable rather than buried in prose (the D22 stamping rule) --
        # and so `check_published_figure_caveat_coverage` has something to hold
        # against a real sweep. Predicted from this book's own coverage
        # witnesses: no seed, no re-scoring, no sweep.
        "published_headline_step_days": predict_published_latency_step_days(
            n_pop, len(earlier_via_dd)),
        # AND WHERE THAT DAY-FOR-DAY TRACKING STOPS (atom D31). The step is a
        # property of the grid; the FLOOR is a property of two harness
        # constants (`PAYMENT_TERMS_DAYS + DEFAULT_RECONCILIATION_GRACE_DAYS`),
        # and a reader given the step without the floor is told the resolution
        # and not its range.
        "organ_query_saturation_caveat": organ_query_grid_saturation_caveat(),
        # THE SECOND KNOB THAT MOVES THIS FIGURE (atom D32). Declared on-path
        # in `DIMENSION_DRIFT_RESOLUTION` since D28, measured, and stamped on
        # nothing until Expert Hour #14 asked whether every knob that moves a
        # published figure reaches its reader.
        "terms_resolution_caveat": latency_terms_resolution_caveat(),
        "organ_query_floor_drift_days": (
            ORGAN_QUERY_GRID["recon_lag_days"]["saturates_below"]),
        "organ_query_floor_constants": tuple(
            ORGAN_QUERY_GRID["recon_lag_days"]["edge_constants"]),
        "organ_query_grid_step_days": (
            ORGAN_QUERY_GRID["recon_lag_days"]["reported_days_for_a_one_day_drift"]),
        "organ_improvement_is_visible": (
            -1 in tuple(ORGAN_QUERY_GRID["recon_lag_days"]["visible_drifts"])),
    }
    if n_pop == 0:
        components["vacuity"] = (
            "NO dated detected failures in this population: the latency means "
            "are UNDEFINED (None), not 0.0. A population nothing was detected "
            "in is not one that was detected instantly."
        )

    return GapResult(
        metric="detection_latency",
        gap=mean_with,
        raw_gap=float(mean_with) if mean_with is not None else 0.0,
        g0=0.0,
        baseline=(
            "NONE -- absolute mean in DAYS from due date to the company's first "
            "knowledge; there is no no-skill divisor here and 1.0 does not mean "
            "'no better than blind' (it means one day)."
        ),
        note=(
            "detection LATENCY of the W2_11<->D5 triad: how late the company "
            "learns a payment failed, and what the DD-observation channel buys "
            "in days. Exists because the set-membership DETECTION headline is "
            "insensitive to that channel by construction (`flagged_set` is a "
            "UNION) -- atom D10. R12: a diagnostic in days, never a target."
        ),
        components=components,
    )


def format_detection_latency_summary(result: GapResult) -> str:
    """Render a `detection_latency_gap` result for a log line / ledger note in
    DAYS with its counterfactual, never as a bare scalar.

    Anti-decay, the same mechanism D7's `format_ageing_summary` is: the reason
    this dimension exists is that a bare number could not express a channel's
    contribution, so no consumer of this module prints the headline without the
    counterfactual and the coverage beside it."""
    c = result.components
    mean = c.get("mean_lag_days")
    without = c.get("mean_lag_days_without_dd_channel")
    earlier = c.get("dd_channel_days_earlier")
    if mean is None:
        return (
            "detection latency UNDEFINED (no dated detected failures in this "
            f"population; {c.get('n_true_failures')} true failures, "
            f"{c.get('n_undetected')} undetected) -- not 0 days"
        )
    return (
        f"detection latency {mean:.2f} days mean "
        f"(without the DD-observation channel {without:.2f} days -- the channel "
        f"buys {earlier:.2f} days EARLIER detection on "
        f"{c.get('n_earliest_via_dd_channel')} of {c.get('n_latency_population')} "
        f"dated cases, while moving the set-membership detection gap by exactly "
        f"zero); {c.get('n_undetected')} of {c.get('n_true_failures')} true "
        "failures never detected at all"
    )


# ---------------------------------------------------------------------------
# THE as_of CONTRACT (atom D11, minted by the H27 Expert-Hour pass 2026-08-09)
# ---------------------------------------------------------------------------
# WHY THIS EXISTS. `score_triad` publishes four numbers, each scored against a
# harness-held TRUTH. Some of those truths genuinely move as the clock moves --
# an unpaid invoice really does age -- and some do not: whether a payment
# FAILED is a fact about the payment, settled forever the moment it happened.
#
# THE CLASS INVARIANT, and it is deliberately DIFFERENTIAL rather than a
# blanket "nothing may move with as_of" (which would fire on the ageing
# dimension, where movement is the correct behaviour, and be a false positive
# that jams the gate):
#
#     if a dimension's TRUTH side is invariant under `as_of`,
#     its published gap MUST be invariant under `as_of` too.
#
# A number that moves while the thing it measures stands still is an artefact
# of the question's timing, not a measurement of the company. This is the same
# defect the RETIRED `detection_latency_days` key was (D10) and the same defect
# D6 found in the ageing scalar's prevalence dependence (D7): a published
# figure moving for a reason that has nothing to do with the company's skill.
# R10 says an absurdity-class defect may not be closed with an instance fix --
# so the property is declared here, for every dimension, and
# `tests/tools/test_couple_w2_11_d5.py` MEASURES the declaration by actually
# moving `as_of` rather than trusting it.
#
# `truth_is_as_of_invariant` is the DECLARATION. The test derives the truth
# signatures independently from `records`, so a wrong declaration fails.
DIMENSION_AS_OF_CONTRACT: Dict[str, Dict[str, object]] = {
    "detection": {
        "truth_is_as_of_invariant": True,
        "truth": "result == 'failed' -- a settled fact about the payment",
        "gap_is_as_of_invariant": True,
        "why": (
            "HOLDS SINCE 2026-08-09 (atom D11). It did NOT hold before: "
            "`flagged_set` was the company's belief held AT as_of, so a case "
            "detected on time and later un-flagged (an ambiguous non-DD payment "
            "allocated oldest-first onto the failed invoice, Clayton's Case) "
            "left the set purely because the clock moved -- measured seed 7 at "
            "0.0725 at as_of and 0.1232 at as_of+60 with company and world "
            "byte-identical. The population is now EVER-FLAGGED, the shape "
            "detection_latency was already built on, and a detection is a fact "
            "about the day it happened."
        ),
    },
    "detection_latency": {
        "truth_is_as_of_invariant": True,
        "truth": "due dates of truly-failed invoices -- fixed at issue",
        "gap_is_as_of_invariant": True,
        "why": ("HOLDS. Built on an EVER-KNEW population precisely so the "
                "answer is a property of the observation, not of when it was "
                "asked for (D10)."),
    },
    "belief": {
        "truth_is_as_of_invariant": True,
        "truth": "per-account count of unresolved true failures -- as_of-free",
        "gap_is_as_of_invariant": True,
        "why": ("HOLDS. Severity labels over settled facts, on both sides: the "
                "company's `arrears_risk_belief` counts unresolved observed "
                "failures, and a failure does not resolve itself by the clock "
                "moving. STILL HOLDS AFTER THE D19 RESHAPE (2026-08-10), which "
                "changed what is done with the two label lists and not when "
                "either is true -- re-measured by the sweep, not assumed to "
                "carry over."),
    },
    "belief_population_mix": {
        "truth_is_as_of_invariant": True,
        "truth": "per-account count of unresolved true failures -- as_of-free",
        "gap_is_as_of_invariant": True,
        "why": ("HOLDS, and for the same reason as `belief` -- it is scored "
                "from the identical two label lists (atom D19). It gets its own "
                "entry rather than an exemption because no published number "
                "escapes this control, and a dimension that shares another's "
                "inputs is exactly the one an author is tempted to assume "
                "inherits its declaration."),
    },
    "ageing": {
        "truth_is_as_of_invariant": False,
        "truth": "30/60/90+ bucket of (as_of - due_date) -- genuinely a clock fact",
        "gap_is_as_of_invariant": False,
        "why": ("EXEMPT, and this is why the invariant is differential: an "
                "invoice really does age, so the truth moves and the gap "
                "following it is correct behaviour, not an artefact."),
        # D16 ASKED WHETHER THIS EXEMPTION IS BROADER THAN ITS JUSTIFICATION,
        # and the answer is YES -- it is recorded here rather than left as the
        # comfortable reading. The justification ("an invoice really does age")
        # licenses the TRUTH side moving with the clock. It says nothing about
        # the BELIEF side, which here is the `as_of` SNAPSHOT of the company's
        # open-item report: an invoice the company chased in month one and
        # dropped from the report by month three leaves this dimension's
        # numerator purely because the clock moved, exactly the way the
        # detection headline's did before D11 made it EVER-FLAGGED. The
        # exemption is therefore kept but NARROWED in what it is allowed to
        # excuse: it covers truth-side ageing, and the belief side's as_of
        # dependence is a REAL property that must be named wherever this rate is
        # published rather than absorbed into the exemption.
        "belief_side_is_as_of_dependent": True,
        "belief_side_note": (
            "The belief is the open-item report AS AT `as_of`, not an "
            "ever-chased population. That is the RIGHT shape for the question "
            "this dimension asks -- is the company's ageing report overstated "
            "today -- and the WRONG shape for the question its rate used to be "
            "named after (was this customer ever wrongly chased), which is why "
            "D16 moved the wrongful-dunning name to the detection dimension "
            "rather than aligning the two belief sides. Aligning them would "
            "have destroyed the misstatement measure to manufacture agreement "
            "between two numbers -- a fix chosen for making the instrument look "
            "consistent, which is the goal-seek R12 forbids."
        ),
    },
}


# ---------------------------------------------------------------------------
# WHO OWNS THE TRUTH SIDE (atom D21, H27 Expert Hour #5, 2026-08-10)
# ---------------------------------------------------------------------------
# WHY THIS EXISTS. D20 found the belief dimension's truth-side rule was a
# hand-copy of the company organ's rule, asserted as "coverage-only" and
# measured nowhere. Expert Hour #5 asked the obvious next question -- which
# OTHER truth sides are the company's own code? -- and found the ageing
# dimension is not a copy of the organ's dating rule but literally IS it:
# `from company.billing.arrears_engine import age_bucket as company_age_bucket`
# at module scope, called to build `true_ageing_labels`.
#
# That is the R15 TAUTOLOGY pattern in the direction nobody checks. The
# epistemic wall is normally enforced company -> sim (can the company see
# something a real supplier could not?). This is the harness -> company
# direction: the GROUND TRUTH a dimension grades against being computed by the
# thing it is grading. A supplier ageing its debt from the wrong date is the
# commonest real ageing-report failure there is, and this dimension -- the one
# whose whole subject is debt DATING -- could not see it, because any edit to
# `age_bucket` moved both sides together.
#
# THE CLASS CONTROL, and it is a call path rather than a declaration (the D19
# lesson: a hand-maintained register skips exactly the entry nobody added).
# `score_triad` resolves its truth-side labelling rules THROUGH this register,
# so `rule.__module__` is a fact about what actually ran, not about what an
# author wrote down. The invariant:
#
#     no dimension's TRUTH-side labelling rule may be owned by `company.*`
#
# `rule: None` is the honest entry for a dimension whose truth is a raw world
# fact with no labelling rule to own -- it is spelled out rather than omitted,
# because an absent entry is how a register fails silent.
#
# NOTE the mutation that reinstates this defect moves NO published number at
# all (the two rules are logically identical at HEAD). That is precisely why
# nothing caught it for the instrument's whole life, and why the control has to
# be about ownership rather than about a value.
TRUTH_SIDE_RULE_OWNERSHIP: Dict[str, Dict[str, object]] = {
    "ageing": {
        "rule": _ageing_bucket,
        "labels": "the TRUE 30/60/90+ bucket of (as_of - due_date)",
        "why": (
            "HARNESS-OWNED SINCE 2026-08-10 (atom D21). It was "
            "`company.billing.arrears_engine.age_bucket` -- the organ's own "
            "function on an input the scenario constructs to be the organ's "
            "own integer, so `wrong_bucket` was 0 by construction at every "
            "seed and the dimension could not see a company dating error at "
            "all. Now redeclared here and PINNED against the organ's rule so "
            "a drift on either side fails loudly and by name."
        ),
    },
    "belief": {
        "rule": _severity_label,
        "labels": "the TRUE arrears severity from the all-channel failure count",
        "why": (
            "HARNESS-OWNED. A deliberate mirror of the organ's thresholding "
            "shape over a different-coverage input, which is what makes the "
            "number a measure of the wall -- and the mirror is MEASURED, not "
            "asserted, by the coverage-only residual (atom D20)."
        ),
    },
    "belief_population_mix": {
        "rule": _severity_label,
        "labels": "the same truth labels as `belief` (atom D19)",
        "why": (
            "HARNESS-OWNED, via the identical label list. It gets its own "
            "entry rather than an exemption for the reason it does in the "
            "other two contracts: a dimension sharing another's inputs is the "
            "one an author assumes inherits a declaration."
        ),
    },
    "detection": {
        "rule": None,
        "labels": "`result == 'failed'` -- a raw world fact, no labelling rule",
        "why": ("NO RULE TO OWN. The truth side is a field on the world's own "
                "`PaymentEvent`, read directly. Recorded as None rather than "
                "omitted: an absent entry is how a register fails silent."),
    },
    "detection_latency": {
        "rule": None,
        "labels": "due dates of truly-failed invoices -- raw world facts",
        "why": ("NO RULE TO OWN. Days between two dates the world fixed; "
                "there is no label to derive and so no rule to own."),
    },
}


def truth_side_rule(dimension: str):
    """Resolve a dimension's truth-side labelling rule THROUGH the ownership
    register, so the register is the call path and not a parallel declaration
    that can quietly stop describing the code (atom D21)."""
    try:
        entry = TRUTH_SIDE_RULE_OWNERSHIP[dimension]
    except KeyError:
        raise KeyError(
            f"no TRUTH_SIDE_RULE_OWNERSHIP entry for '{dimension}' -- a "
            "dimension scoring truth labels through an unregistered rule is "
            "the fail-silent shape this register exists to close"
        ) from None
    rule = entry["rule"]
    if rule is None:
        raise ValueError(
            f"'{dimension}' declares no truth-side labelling rule (its truth "
            "is a raw world fact); asking for one means the scorer and the "
            "register disagree about what this dimension does"
        )
    return rule


# ---------------------------------------------------------------------------
# THE COVERAGE-ONLY CLAIM (atom D20_belief_truth_rule_is_an_unmeasured_mirror)
# ---------------------------------------------------------------------------
# WHAT THE DEFECT WAS. The belief dimension publishes its two sides as "same
# threshold shape, different-coverage inputs": the TRUTH side is
# `_severity_label` (this module) and the BELIEF side is
# `PaymentObservationConsumer._arrears_risk_belief` (the company organ), and
# the claim is that the ONLY difference between them is which failures the
# company got to see. That claim is what makes the published number a measure
# of the WALL. It was asserted in a docstring and in the ledger note the Proof
# door reads, and nothing measured it -- `_severity_label` was a HAND-COPY of
# the organ's thresholds with no test naming the pair (H27 Expert Hour #4,
# 2026-08-10).
#
# MEASURED, not argued. Three plausible drifts of the organ's own rule, applied
# to the organ ALONE, with the world and the truth-side rule untouched:
#
#   organ drift (company rule only)      published belief headline   what fired
#   -----------------------------------  -------------------------  -------------------------
#   one failure no longer raises WATCH   0.1424 -> 0.4146 (2.9x)    a permutation-probe
#                                                                   VACUITY guard
#   hardship amplification 2 -> 1        0.1424 -> (overcall > 0)   "this book's company now
#                                                                   over-calls" -- a POPULATION
#                                                                   premise, not the rule
#   HIGH bar 3+ -> 4+                    0.1424 -> 0.1551           the WALL-LEAK R15 control
#
# Exactly one test fired each time and not one of them named the divergence;
# two gave an actively wrong diagnosis (a weak probe; an epistemic-wall leak).
# A reader would have chased the wrong organ while the headline silently became
# a mixture of coverage loss and rule divergence, still published as coverage.
#
# THE CONTROL. Equalise the coverage and the residual must be ZERO. On a
# counterfactual population where every customer pays by DIRECT DEBIT the
# company observes every failure, so any surviving gap is rule divergence by
# construction -- and it needs no copy of either rule to say so, which is the
# R15 independence a threshold-table test could not have had.
COVERAGE_ONLY_CLAIM_PHRASE = "different-coverage"

COVERAGE_ONLY_CLAIM_CONTRACT: Dict[str, Dict[str, object]] = {
    "belief": {
        "claims_coverage_only": True,
        "why": (
            "Its two sides run the SAME thresholding shape (`_severity_label` "
            "mirrors `PaymentObservationConsumer._arrears_risk_belief`) over "
            "different-coverage counts: all-channel unresolved failures on the "
            "truth side, DD/rail-OBSERVED failures on the belief side. So with "
            "coverage equalised the residual must be exactly 0."
        ),
    },
    "belief_population_mix": {
        "claims_coverage_only": True,
        "why": (
            "Scored from the IDENTICAL two label lists as `belief` (atom D19), "
            "so it inherits the claim in substance. It gets its own entry "
            "rather than an exemption for the same reason it does in "
            "`DIMENSION_AS_OF_CONTRACT`: a dimension that shares another's "
            "inputs is exactly the one an author assumes inherits a declaration."
        ),
    },
    "detection": {
        "claims_coverage_only": False,
        "why": (
            "EXEMPT: its two sides are not one rule over two coverages at all "
            "-- truth is `result == 'failed'` and belief is an ever-flagged set "
            "built by expected-collection reconciliation, a DIFFERENT rule. It "
            "HAPPENS to measure 0.0000 on the all-DD counterfactual (seeds "
            "7/11/23), and that coincidence is exactly why the exemption is "
            "recorded rather than inferred from the number: a control that read "
            "the residual and concluded the claim would license this dimension "
            "into a claim it does not make. Nothing here may assert on it."
        ),
    },
    "detection_latency": {
        "claims_coverage_only": False,
        "why": ("EXEMPT. An absolute mean in DAYS with no truth-side label to "
                "agree with -- there is no 'same rule' to hold. It is also the "
                "LIVE SIDE of this control's differential: it reads ~0.93-1.07 "
                "on the counterfactual (seeds 7/11/23), which is what stops a "
                "population that collapsed every dimension to 0 -- a broken "
                "build, an empty book -- from passing as agreement."),
    },
    "ageing": {
        "claims_coverage_only": True,
        "why": (
            "ENROLLED 2026-08-10 (atom D21). It was EXEMPT, on the stated "
            "ground that 'truth is a clock fact about the due date and belief "
            "is the open-item report; two different rules, not one rule over "
            "two coverages'. Both clauses were false, and this module's own "
            "docstring said so four hundred lines up ('Both sides use the "
            "IDENTICAL bucket function') -- the control believed the "
            "exemption. The two sides run ONE rule (`_ageing_bucket`, which "
            "until D21 was the organ's own `age_bucket`) over ONE integer the "
            "scenario constructs identically on both sides; the only "
            "difference is WHICH invoices the company holds open, which is "
            "coverage exactly. Measured, and this is the signature the "
            "exemption was hiding: residual 0.000000 on the all-DD "
            "counterfactual at seeds 7/11/23, non-vacuous. So the one control "
            "in the repository able to catch the D20 class was switched off "
            "for the dimension with the strongest mirror of the three."
        ),
    },
}


def measure_coverage_only_residual(
    n_customers: int = 800, seed: Optional[int] = None,
) -> Dict[str, object]:
    """Score the COUNTERFACTUAL all-Direct-Debit population and report, per
    dimension, the gap that survives when coverage loss is removed.

    For a dimension declaring `claims_coverage_only`, that residual IS its
    rule divergence: the truth-side rule and the company organ's rule
    disagreeing on inputs they both fully saw. It must be 0.

    INDEPENDENCE (R15 tautology): nothing here re-derives, copies or inspects
    either side's thresholds. Both labels come out of the shipped code paths --
    `_severity_label` on the harness side, `consumer.snapshot(...)` on the
    company side -- over a population built by `build_scenario` and fed through
    the real seam. The control can only be satisfied by the two rules actually
    agreeing.

    VACUITY (R15 fail-open): a residual of 0 proves nothing unless the
    counterfactual really did remove coverage loss that really was there. Both
    halves travel in `witnesses`, and `is_vacuous` is True if either fails --
    the caller must assert on it, because "0" on a population with no coverage
    loss to remove, or with no possible-error population at all, is the
    strongest possible claim handed out for free."""
    cf_records, cf_consumer, _cf_ledger, cf_as_of = build_scenario(
        n_customers, seed=seed, force_payment_method=DIRECT_DEBIT)
    cf = score_triad(cf_records, cf_consumer, cf_as_of)

    real_records, real_consumer, _r_ledger, real_as_of = build_scenario(
        n_customers, seed=seed)
    real = score_triad(real_records, real_consumer, real_as_of)

    residuals: Dict[str, Dict[str, object]] = {}
    for dim, decl in COVERAGE_ONLY_CLAIM_CONTRACT.items():
        residuals[dim] = {
            "claims_coverage_only": bool(decl["claims_coverage_only"]),
            "residual": cf[dim].gap,
            "gap_on_the_scored_book": real[dim].gap,
        }

    witnesses = _coverage_residual_witnesses(cf, real, residuals)
    return {
        "residuals": residuals,
        "witnesses": witnesses,
        # ONE PREDICATE FOLDING ALL FOUR, so a witness that is gathered but
        # never consulted cannot exist -- a reported witness nobody reads is a
        # report, not a control. Written out rather than derived from the key
        # names: witness (2) is the one whose healthy value IS zero, and a fold
        # that inferred polarity from a naming convention would silently invert
        # the next witness someone adds.
        "is_vacuous": (
            witnesses["coverage_loss_removed"] == 0
            or witnesses["cf_non_dd_failures"] != 0
            or witnesses["cf_undercall_population"] == 0
            or witnesses["cf_overcall_population"] == 0
            or witnesses["n_exempt_dimensions_nonzero"] == 0
        ),
        "n_customers": n_customers,
        "seed": seed,
    }


def _coverage_residual_witnesses(
    cf: Dict[str, object], real: Dict[str, object],
    residuals: Dict[str, Dict[str, object]],
) -> Dict[str, int]:
    """The VACUITY APPARATUS for `measure_coverage_only_residual`, kept as one
    named unit because its healthy reading is a ZERO and a zero is what a dead
    control returns too. Four counts, every one of which must be non-degenerate
    before the residual means anything.

    They live beside the measurement rather than in the test file for the reason
    R15 keeps naming: a guard a caller can forget to apply is a guard that gets
    forgotten. `measure_coverage_only_residual` folds all four into a single
    `is_vacuous`, so there is nothing to remember."""
    cf_bel = cf["belief"].components
    return {
        # (1) THE COUNTERFACTUAL REMOVED SOMETHING REAL. The scored population
        # must genuinely carry the coverage loss the claim is about: a failed
        # push payment emits no rail event at all, so it is invisible to the
        # company's severity count. If the real book had none, equalising
        # coverage is a no-op and a zero residual means nothing.
        "coverage_loss_removed": int(real["stats"]["n_true_non_dd_failures"]),
        # (2) IT REALLY DID CLOSE THE CHANNEL. Zero non-DD failures in the
        # counterfactual is what "the company saw everything" means here -- and
        # this is the one witness whose healthy value IS 0, which is why the
        # vacuity fold treats it as the exception rather than reading it the
        # same way as the other three.
        "cf_non_dd_failures": int(cf["stats"]["n_true_non_dd_failures"]),
        # (3) THE COUNTERFACTUAL IS NOT VACUOUSLY ERROR-FREE. Both belief error
        # directions need a non-empty possible-error population there, or a 0
        # residual is arithmetic rather than agreement.
        "cf_undercall_population": int(cf_bel["n_undercall_population"]),
        "cf_overcall_population": int(cf_bel["n_overcall_population"]),
        # (4) THE DIFFERENTIAL. A counterfactual on which EVERY dimension read 0
        # would satisfy the claiming dimensions for a reason that has nothing to
        # do with the two rules agreeing (an empty book, a scorer returning
        # zeros, a build that no longer runs). At least one EXEMPT dimension
        # must come out non-zero on the same population, or the zeros are a
        # property of the run rather than of the rules.
        "n_exempt_dimensions_nonzero": sum(
            1 for v in residuals.values()
            if not v["claims_coverage_only"] and v["residual"]
        ),
    }


# THE AGEING EXCLUSION BAND'S PUBLISHED REASON (atom D16). One constant, so the
# offline scorer, the live scorer and any future ageing caller cannot drift into
# publishing different reasons for the same excluded case -- the same discipline
# `_CELL_EXCLUSION_REASON` carries for the detection cells, and `ageing_gap`
# RAISES if it is missing (D10: the exclusion is published, not silent).
AGEING_EXCLUSION_REASON = (
    "cases in NEITHER ageing population (atom D16, carrying D11's rule across "
    "from the detection dimension of this same instrument): a payment that "
    "eventually succeeded but arrived more than {grace} days (the reconciliation "
    "grace) after its due date really WAS unpaid past grace, so the company "
    "carrying it as owed was CORRECT even though the truth bucket at `as_of` "
    "reads `current`; an unresolved dispute is not a settled success either; and "
    "a record carrying no `days_late` truth is UNKNOWN, never assumed paid on "
    "time. Until this band existed, 94 of this dimension's 101 false ageings "
    "were cases its sibling dimension holds the company was RIGHT about."
)


# ---------------------------------------------------------------------------
# THE ERROR-DIRECTION CONTRACT (atom D11, the R10 half)
# ---------------------------------------------------------------------------
# WHY THIS EXISTS AND WHY IT IS NOT JUST A FIXED FUNCTION. R10: an absurdity-class
# defect may not be closed with an instance fix. The instance was the payment
# triad's detection headline scoring a company 0.0725 -- "nearly perfect" -- while
# 44-51% of everything it flagged was an invoice that had been paid. The CLASS is
# every published set-membership detection score in this repo, because they all
# share one property:
#
#     a one-directional detection score cannot distinguish a precise company
#     from an indiscriminate one, so it MUST either measure both directions or
#     name the atom that will make it
#
# Four dimensions published one direction when this register was written. THREE
# are now fixed (the headline, D11; the regime-partitioned cell grid, D12; the
# W2_5<->C7 life-event pair, D15) and ONE is NAMED DEBT with a reason and an
# owner -- a dated liability, not a silent survivor. The survivor is NOT the same
# problem as the three that were fixed -- and, per the D13 DISCOVER
# (2026-08-09), the two self-rationing pairs were never the same problem as EACH
# OTHER either; bracketing them under one atom was the error, and D15 closing
# while D14 stays open is that finding paying off.
# The premise this comment used to carry -- that "a household that is not
# self-rationing" is a continuum the harness labels by threshold -- was measured
# and is FALSE for both. W2_8 stamps RationingLabel.NOT_RATIONING from a
# Bernoulli onset; W2_5 runs a discrete LOW/MODERATE/HIGH income_stress state
# machine. Both negatives are settled facts. They remain debt for OPPOSITE
# reasons, each carried by its own atom: W2_8's measure is VACUOUS (0 of 3752
# non-rationers have any drop, so the rate is 0.0000 for any detector --
# `D14_w2_8_needs_negative_drops`, a WORLD gap, still open), while W2_5's was
# live and consequential (the exclusion boundary swings it x2.88 because
# income_stress PERSISTS past the event year) and is now published under a NAMED
# exclusion basis with all three candidate rates travelling beside it
# (`D15_w2_5_false_flag_direction_r13_choice`, landed). D11 measured what a
# careless denominator is worth --
# it moved the payment triad's wrongful-dunning rate tenfold -- so neither is
# closed by inventing one to empty this register faster.
# `tests/tools/test_couple_w2_11_d5.py` MEASURES this register rather than
# trusting it: for each entry it actually scores the flag-EVERYTHING degenerate
# through that entry's own scorer and asserts the declared behaviour -- a
# two-directional dimension must NOT hand it a perfect score, a recall-only one
# must (that is what makes it debt). A dimension added without an entry fails the
# control, and an entry claiming to be two-directional while still scoring the
# degenerate perfectly fails it too.
DETECTION_DIRECTION_CONTRACT: Dict[str, Dict[str, object]] = {
    "score_triad.detection": {
        "counts_both_error_directions": True,
        "scorer": "background.gap_metric.detection_measures",
        "why": (
            "FIXED 2026-08-09 (atom D11). Balanced error over both directions on "
            "their own denominators; flag-nobody and flag-EVERYTHING both score "
            "g0 = 0.5."
        ),
        "debt_atom": None,
    },
    "score_detection_by_partition": {
        "counts_both_error_directions": True,
        "scorer": "background.gap_metric.detection_measures",
        "why": (
            "FIXED 2026-08-09 (atom D12). The cells were the recall-only "
            "shape; they now score both directions on their own PER-CELL "
            "denominators. No denominator was invented: the negative "
            "population is the same never-flaggable set the headline uses "
            "(cash within the reconciliation grace), PARTITIONED, because it "
            "is a per-record property. The band was re-derived in the same "
            "change per the atom's own instruction -- the lit cell moved "
            "0.1031 -> 0.0584 on the live fixture with no change in company "
            "behaviour, so every ledger record now names its `detection_"
            "measure` and both direction rates travel with the headline."
        ),
        "debt_atom": None,
    },
    "couple_w2_5_c7.detection": {
        "counts_both_error_directions": True,
        "scorer": "background.gap_metric.detection_measures",
        "why": (
            "FIXED 2026-08-09 (atom D15, on the D13 DISCOVER's finding). The "
            "settled-fact negative the DISCOVER named is now built and scored: "
            "income_stress is a discrete LOW/MODERATE/HIGH state machine, so "
            "'LOW at both year ends' is a state, not a threshold. What made this "
            "publishable rather than merely computable is that the exclusion is "
            "NAMED: `tools.couple_w2_5_c7.EXCLUSION_BASES` enumerates all three "
            "candidate negatives, EVERY run scores all three (0.1661 / 0.1491 / "
            "0.0576 at the reference population -- a x2.88 swing with company "
            "behaviour literally fixed), and the published one is a single "
            "constant the director moves in one edit. The recommendation is "
            "PROVISIONAL and its R12 hazard is stated where a reader sees it: it "
            "produces the LOWEST of the three, and the reason is the SET (the "
            "miss direction's truth is EVENT-shaped, the detector's claim is "
            "STATE-shaped, and the carried-distress band is exactly where they "
            "disagree), never the number. Director's call: docs/design/"
            "D15_FALSE_FLAG_EXCLUSION_R13_CHOICE.md."
        ),
        "debt_atom": None,
    },
    "couple_w2_8_c10.detection": {
        "counts_both_error_directions": True,
        "scorer": "background.gap_metric.detection_measures",
        "why": (
            "FIXED 2026-08-09 (atom D14) -- and fixed in the WORLD first, which "
            "is why it took a second atom rather than a denominator edit. The "
            "D13 DISCOVER measured this measure as VACUOUS: 0 of 3752 "
            "non-rationers had ANY consumption drop, so the false-flag rate was "
            "0.0000 for any drop-based detector -- a property of the world "
            "published as detector precision (R12). D14 added the missing world "
            "depth (`simulation.self_rationing.DropConfounder`: house moves, "
            "voids, retrofits and voluntary cuts now cut consumption with NO "
            "hardship behind them, drawn independently of the rationing label "
            "and anchored to external rates fixed BEFORE the resulting rate was "
            "measured). 695 of 3752 non-rationers now really do drop, and the "
            "detector false-flags 0.0560 of the settled negative -- a rate that "
            "can now move because the world can now produce the error. The "
            "denominator defect the DISCOVER found here is fixed in the same "
            "change: the 43 households that ARE rationing but sit above the "
            "floor are EXCLUDED (a flag on them is right), and both the settled "
            "and the naive rate are published every run via "
            "`tools.couple_w2_8_c10.NEGATIVE_BASES` so the defect cannot return "
            "unnoticed."
        ),
        "debt_atom": None,
    },
}


# ---------------------------------------------------------------------------
# THE AGGREGATE-SCORING CLASS (2026-08-10, H27 Expert-Hour pass #3, atom D19)
# ---------------------------------------------------------------------------
# THE CLASS: a dimension scored on POPULATION AGGREGATES is blind to per-case
# assignment. The company gets the MIX right and every INDIVIDUAL wrong, and the
# published number does not move. `DETECTION_DIRECTION_CONTRACT` above swept the
# four DETECTION dimensions for their degenerate (flag EVERYTHING); it is keyed
# to detection scorers, so the BELIEF dimension -- a total-variation distance
# between two severity distributions -- was never swept, and carries the same
# shape with a different degenerate strategy.
#
# Measured, seed 7 at n=600: permuting the company's per-case severity beliefs
# among cases takes per-case agreement 0.9300 -> 0.6333 and moves the published
# belief gap 0.0700 -> 0.0700, identical to machine precision. Seeds 11 and 23
# agree. What made it invisible is that on this book the company's errors run
# ONE WAY (it under-calls severity), and on a one-directional book TV is
# arithmetically EQUAL to the per-case disagreement rate -- 0.0700/0.0700,
# 0.1033/0.1033, 0.0733/0.0733. The number reads as a per-case error rate and
# numerically IS one here, while being a quantity a permutation leaves alone.
#
# DIFFERENTIAL ON PURPOSE, the DIMENSION_AS_OF_CONTRACT lesson: a blanket "no
# dimension may be permutation-invariant" would fire on `belief` as a DESIGN
# FACT rather than a defect (a distribution distance is supposed to be a
# distribution distance) and on nothing else usefully. What the control asserts
# is the DECLARATION: a dimension declared per-case-sensitive must really move
# under a permutation, and one declared aggregate-only must really not -- and
# must carry a live `witness_key` naming where a reader finds the direction it
# cannot see. A register entry is a claim the control puts on trial.
#
# THE DEFECT IS NOW FIXED (atom D19, landed 2026-08-10), and the register is
# what makes the fix checkable rather than claimed. The belief HEADLINE moved to
# `gap_metric.belief_measures` -- balanced per-case error, both directions on
# their own denominators -- and its declaration flipped to per-case-sensitive,
# so the control now FAILS if that dimension ever goes blind again. The TV
# figure did not disappear: it is published as its own dimension,
# `belief_population_mix`, under a name that says it is about the MIX, which is
# also what keeps the differential honest (a register where every entry landed
# on one side is a blanket rule wearing a register's clothes).
AGGREGATE_SCORING_CONTRACT: Dict[str, Dict[str, object]] = {
    "belief": {
        "is_aggregate_only": False,
        "scorer": "background.gap_metric.belief_measures",
        "witness_key": None,
        "why": (
            "FIXED 2026-08-10 (atom D19), the reshape H27's Expert Hour #3 "
            "named. The headline is now the BALANCED PER-CASE severity error "
            "-- undercall_rate over the accounts that could be under-called, "
            "overcall_rate over those that could be over-called -- so "
            "permuting which account holds which belief really does move it, "
            "and the 'right mix, every individual wrong' degenerate scores g0 "
            "= 0.5 like every other severity-blind rule. R12: the reshape was "
            "designed from the defect, never fitted to a value; the number "
            "moved (0.0713 -> the balanced error) because the measure was "
            "wrong, not because it looked wrong. This entry is the side that "
            "must FAIL if the permutation probe goes inert."
        ),
        "debt_atom": None,
    },
    "belief_population_mix": {
        "is_aggregate_only": True,
        "scorer": "background.gap_metric.belief_gap",
        "witness_key": "per_case_disagreement_rate",
        "why": (
            "DESIGN FACT, and now published under a name that says so (atom "
            "D19). This is the RETIRED headline's own number, kept rather than "
            "deleted because 'does the company have the right MIX?' is a real "
            "question about the book -- a portfolio-level severity view is what "
            "a credit committee actually reads. What was wrong was publishing "
            "it as 'the belief gap', a name that reads as a per-case error "
            "rate; on a one-directional book it even EQUALS one, which is what "
            "hid it. Permutation-invariance is correct behaviour HERE, which is "
            "what keeps this control differential rather than a blanket ban. "
            "The two other pairs still calling `belief_gap` as their headline "
            "(W2_4<->C6, couple_cohort) are NAMED DEBT carried at source in "
            "gap_metric.BELIEF_GAP_PERMUTATION_CAVEAT: they hold distributions "
            "with no per-case pairing, so the reshape needs a per-case join "
            "they do not have, not a scorer swap."
        ),
        "debt_atom": None,
    },
    "ageing": {
        "is_aggregate_only": False,
        "scorer": "background.gap_metric.ageing_gap",
        "witness_key": None,
        "why": (
            "PER-CASE by construction: `ageing_gap` walks truth and belief "
            "bucket labels PAIRWISE per invoice and scores the bucket "
            "DISTANCE, so a permutation really does move it. This entry is "
            "what makes the control differential rather than a blanket ban -- "
            "it is the side that must FAIL if the permutation probe is inert."
        ),
        "debt_atom": None,
    },
    "detection": {
        "is_aggregate_only": False,
        "scorer": "background.gap_metric.detection_measures",
        "witness_key": None,
        "why": (
            "PER-CASE: scored on SET MEMBERSHIP (truth_set vs flagged_set over "
            "(customer, period) keys), so moving a flag from one case to "
            "another changes both direction rates. Its own degenerate is the "
            "flag-EVERYTHING strategy, swept by "
            "DETECTION_DIRECTION_CONTRACT above -- a different blindness, "
            "which is why it needs an entry in BOTH registers."
        ),
        "debt_atom": None,
    },
}


# ---------------------------------------------------------------------------
# THE HEADLINE-DIRECTION CLASS (2026-08-10, H27 Expert-Hour pass #6, atom D22)
# ---------------------------------------------------------------------------
# THE CLASS is the one `DETECTION_DIRECTION_CONTRACT` above already states:
#
#     a one-directional score cannot distinguish a precise company from an
#     indiscriminate one, so it MUST either measure both directions or name
#     the atom that will make it
#
# That register swept the DETECTION dimensions and D11/D12/D14/D15 fixed four.
# D19 then found the same class had escaped into `belief`, because the register
# is KEYED TO DETECTION SCORERS, and fixed it. This is the third time the class
# has been found somewhere the sweep could not reach -- so the sweep, not the
# instance, is what is wrong, and this register is the sweep with the keying
# removed: its keyset is DERIVED from the dimensions `score_triad` actually
# publishes, so a dimension cannot escape by not being a detection scorer, by
# being ordinal instead of a rate, or by being added later.
#
# WHAT IT MEASURES, per published dimension: score that dimension's own
# INDISCRIMINATE DEGENERATE -- the strategy that is PERFECT in the direction the
# headline counts and maximally wrong in the other -- through the dimension's
# OWN shipped scorer, beside a company that is perfect in both. A headline that
# counts both directions must tell those two apart. One that does not is DEBT,
# and must name the atom that will make it.
#
# MEASURED 2026-08-10 (n=4000, seeds 7/11/23), perfect -> degenerate:
#     detection              0.0 -> 0.5      distinguishes
#     belief                 0.0 -> 0.5      distinguishes
#     belief_population_mix  0.0 -> ~0.96    distinguishes
#     ageing                 0.0 -> 0.0      DOES NOT -- 10,758 cases changed
#                                            and the number did not move
#                            0.0 -> 1.5      distinguishes, after D22 landed
# The ageing entry is the finding this register was built for: its ORDINAL
# headline was taken over the truly-overdue alone, so a company that dated every
# overdue invoice perfectly and put its entire current book in `90+` scored a
# perfect 0.000000. Its over-ageing direction was never unmeasured -- the
# DIMENSION publishes `overstated_arrears_rate` -- but the ORDINAL severity,
# which is the whole of what this dimension adds over a rate, existed in one
# direction only. D22 reshaped the headline onto the BALANCED displacement (the
# mean of the two directions, each on its own denominator: `gap_metric`'s own
# comment carries the measurement that rejected the pooled-mean alternative for
# re-importing D6's prevalence sensitivity). The register caught its own entry
# rotting the moment the reshape landed, which is the behaviour the second rule
# in `_check_one_entry` exists for -- and the published offline headline moved
# 0.178744 -> 0.095732 at seed 7, which is why this was a mint and not a fix on
# sight.
#
# THE THIRD STATE, and why it is not a loophole. `detection_latency` is honestly
# conditional: it is a mean over cases the company DID detect, so an
# indiscriminate flagger's extra flags never enter its population at all. Its
# entry therefore names a SIBLING dimension that counts the direction it cannot
# (`detection`, made two-directional by D11) -- and the control MEASURES that
# claim rather than accepting it: the named sibling must itself be a
# both-directions entry that really does tell the degenerate apart, and the
# latency population must really contain no truly-current case. `ageing` may NOT
# claim the same cover, and the reason is already measured: D16 established that
# detection's false_flag_rate and ageing's overstated_arrears_rate are DIFFERENT
# quantities over different populations (that was the "one name, two numbers"
# finding), so nothing in this instrument sees over-ageing SEVERITY.
_DEGENERATE_STRATEGIES: Dict[str, object] = {
    # Perfect on the truly-overdue book; every truly-current invoice dumped in
    # the oldest arrears bucket -- maximal wrongful ageing, zero missed debt.
    "age_the_current_book_at_90_plus":
        lambda true_l: [t if t != "current" else "90+" for t in true_l],
    # Every account graded at the top severity -- no under-call is possible, and
    # every over-call is made.
    "call_every_account_max_severity":
        lambda true_l: [_SEVERITY_ORDER[-1]] * len(true_l),
    # The flag-EVERYTHING strategy DETECTION_DIRECTION_CONTRACT already sweeps,
    # re-expressed in per-case labels so it runs through the same probe as the
    # others rather than through a second copy of the idea.
    "flag_every_case":
        lambda true_l: ["positive"] * len(true_l),
}

HEADLINE_DIRECTION_COVERAGE: Dict[str, Dict[str, object]] = {
    "detection": {
        "headline_counts_both_directions": True,
        "degenerate": "flag_every_case",
        "covered_by": None,
        "debt_atom": None,
        "why": (
            "FIXED 2026-08-09 (atom D11) and re-proven here through a second, "
            "independently-built probe: balanced error over both directions on "
            "their own denominators, so flag-nobody and flag-EVERYTHING both "
            "score 0.5. This entry is one of the sides that must FAIL if the "
            "probe ever goes inert -- a register whose every entry sits on the "
            "debt side is a blanket rule wearing a register's clothes."
        ),
    },
    "belief": {
        "headline_counts_both_directions": True,
        "degenerate": "call_every_account_max_severity",
        "covered_by": None,
        "debt_atom": None,
        "why": (
            "FIXED 2026-08-10 (atom D19). Balanced per-case severity error -- "
            "undercall_rate over the accounts that could be under-called, "
            "overcall_rate over those that could be over-called -- so grading "
            "every account `high` scores 0.5, not 0."
        ),
    },
    "belief_population_mix": {
        "headline_counts_both_directions": True,
        "degenerate": "call_every_account_max_severity",
        "covered_by": None,
        "debt_atom": None,
        "why": (
            "A total-variation distance between two severity DISTRIBUTIONS is "
            "symmetric in the error direction by construction: collapsing the "
            "book onto one severity moves the mix as far as it can go "
            "(~0.96). It is blind to per-case ASSIGNMENT, which is a different "
            "blindness, declared and swept by AGGREGATE_SCORING_CONTRACT -- "
            "which is why this dimension needs an entry in both registers."
        ),
    },
    "ageing": {
        "headline_counts_both_directions": True,
        "degenerate": "age_the_current_book_at_90_plus",
        "covered_by": None,
        "debt_atom": None,
        "why": (
            "FIXED 2026-08-10 (atom D22), the debt this register was built to "
            "find and the entry it then caught rotting. The headline was "
            "`mean_bucket_displacement`, a mean over the TRULY-OVERDUE "
            "population, so no amount of over-ageing could move it: a company "
            "dating its whole current book at `90+` scored 0.000000, "
            "bit-identical to a perfect dater, at seeds 7/11/23 with 10,758 "
            "cases changed. The dimension was never blind to that direction "
            "(it publishes `overstated_arrears_rate`), but its ORDINAL term "
            "was, and the ordinal term is the whole of what this dimension "
            "adds over a rate -- so its own docstring's claim to 'distinguish "
            "off-by-one from stone-blind, which an error rate cannot' held in "
            "one direction only. It is now the BALANCED displacement: the "
            "mean of the two directions, each on its own denominator, so this "
            "degenerate scores 1.5 against a perfect dater's 0.0 and the "
            "pooled-mean alternative -- which would have re-imported D6's "
            "prevalence sensitivity, measured at a 5.05x swing with company "
            "behaviour held fixed -- is pinned as a rejected mutant in "
            "tests/tools/test_d7_ageing_measures.py. NO SIBLING COVER WAS "
            "EVER AVAILABLE HERE, which is why the fix had to be the "
            "headline's own: D16 measured that detection's false_flag_rate is "
            "a DIFFERENT quantity over a different population from this "
            "dimension's overstatement, so nothing else in this instrument "
            "sees over-ageing SEVERITY."
        ),
    },
    "detection_latency": {
        "headline_counts_both_directions": False,
        "degenerate": None,
        "covered_by": "detection",
        "debt_atom": None,
        "why": (
            "HONESTLY CONDITIONAL, and the condition is checked rather than "
            "asserted. The headline is a mean over cases the company DID "
            "detect and that are truly failures, so an indiscriminate "
            "flagger's extra flags never enter its population -- there is no "
            "belief-side degenerate that can move it, which is why this entry "
            "carries no strategy. That is not licence: the control asserts "
            "(a) the named sibling `detection` is itself a both-directions "
            "entry that really does tell its own degenerate apart, and (b) "
            "the latency population really does contain no truly-current "
            "case, so the direction this headline cannot see is the direction "
            "the sibling counts. If either stops holding, this entry is a lie "
            "and the control fails."
        ),
    },
}


def published_dimensions(result: Dict[str, object]) -> List[str]:
    """The dimensions `score_triad` actually PUBLISHES, derived from the result
    rather than listed -- so a dimension added later cannot escape the
    direction sweep by not being written down (the D19 lesson, and the reason
    this register is not keyed to a scorer family the way its predecessor was).
    """
    return sorted(k for k, v in result.items() if isinstance(v, GapResult))


def measure_headline_direction_coverage(
    result: Dict[str, object],
    contract: Optional[Dict[str, Dict[str, object]]] = None,
) -> Dict[str, Dict[str, object]]:
    """MEASURE `HEADLINE_DIRECTION_COVERAGE` rather than trust it: for every
    published dimension, score its INDISCRIMINATE DEGENERATE and a PERFECT
    company through that dimension's OWN shipped scorer and report whether the
    headline tells them apart.

    Returns {dimension: {"declared_counts_both_directions", "perfect_gap",
    "degenerate_gap", "distinguishes", "probe_bit", "covered_by",
    "cover_is_two_directional", "debt_atom"}}.

    `probe_bit` is the VACUITY guard: the degenerate must actually differ from
    the perfect company per-case. A probe that changed nothing proves nothing
    in EITHER direction -- it would hand a silent pass to a both-directions
    claim and a silent failure to a debt entry.

    FAIL LOUD (R15): a published dimension with no register entry, a register
    entry for a dimension that is not published, a `covered_by` naming an
    unregistered dimension, and an entry whose declared degenerate strategy
    does not exist all RAISE at the point of use -- every one of them is a
    shape in which this control would quietly stop covering something.
    """
    contract = HEADLINE_DIRECTION_COVERAGE if contract is None else contract
    _validate_direction_register(contract, set(published_dimensions(result)))

    out: Dict[str, Dict[str, object]] = {}
    for dim in sorted(contract):
        out[dim] = _probe_one_dimension(dim, contract, result)

    # The cover claims are resolved AFTER every row is measured, because a
    # cover is a statement about the sibling's MEASURED behaviour, not about
    # its declaration.
    for row in out.values():
        cover = row.get("covered_by")
        row["cover_is_two_directional"] = (
            None if cover is None
            else bool(out[cover].get("distinguishes"))
        )
    return out


def _validate_direction_register(
    contract: Dict[str, Dict[str, object]], published: set
) -> None:
    """Both keyset directions, each a way this control could stop covering
    something: a published dimension nobody registered is one whose headline has
    never been checked, and a registered dimension nobody publishes is a
    register describing coverage it is not providing."""
    registered = set(contract)
    if published - registered:
        raise ValueError(
            f"HEADLINE_DIRECTION_COVERAGE has no entry for published "
            f"dimension(s) {sorted(published - registered)} -- an unregistered "
            "dimension is one whose headline nobody has checked for direction "
            "coverage, and dropping it silently is how this class escaped the "
            "detection-keyed register twice"
        )
    if registered - published:
        raise ValueError(
            f"HEADLINE_DIRECTION_COVERAGE registers {sorted(registered - published)} "
            "which `score_triad` does not publish -- a register describing a "
            "dimension that no longer exists reads as coverage it is not "
            "providing"
        )


def _probe_one_dimension(
    dim: str, contract: Dict[str, Dict[str, object]], result: Dict[str, object]
) -> Dict[str, object]:
    """Score ONE dimension's indiscriminate degenerate against a perfect company
    through that dimension's own shipped scorer."""
    decl = contract[dim]
    cover = decl.get("covered_by")
    if cover is not None and cover not in contract:
        raise ValueError(
            f"'{dim}' declares its direction is covered by '{cover}', "
            "which is not a registered dimension -- a cover claim naming "
            "nothing is the fail-open shape this third state could take"
        )
    row: Dict[str, object] = {
        "declared_counts_both_directions": bool(
            decl["headline_counts_both_directions"]),
        "covered_by": cover,
        "debt_atom": decl.get("debt_atom"),
    }

    strategy_name = decl.get("degenerate")
    if strategy_name is None:
        # The conditional-population case: there is no belief-side degenerate,
        # so what is measured instead is the CONDITION -- that no truly-current
        # case can reach this headline's population.
        row.update(_measure_conditional_population(dim, result))
        return row

    if strategy_name not in _DEGENERATE_STRATEGIES:
        raise ValueError(
            f"'{dim}' declares degenerate strategy '{strategy_name}', which "
            "is not in `_DEGENERATE_STRATEGIES` -- the register would name a "
            "probe that never runs"
        )
    true_l = (result.get("labels") or {}).get(f"{dim}_truth")
    if true_l is None:
        raise ValueError(
            f"HEADLINE_DIRECTION_COVERAGE declares a degenerate for '{dim}' "
            "but `score_triad` publishes no per-case truth labels for it -- "
            "the control cannot be run on a declaration it cannot reach"
        )
    true_l = list(true_l)
    degenerate = list(_DEGENERATE_STRATEGIES[strategy_name](true_l))
    perfect_gap = _rescore_dimension(dim, list(true_l), list(true_l), result)
    degenerate_gap = _rescore_dimension(dim, list(true_l), degenerate, result)
    n_changed = sum(1 for a, b in zip(true_l, degenerate) if a != b)
    row.update({
        "degenerate_strategy": strategy_name,
        "perfect_gap": perfect_gap,
        "degenerate_gap": degenerate_gap,
        "distinguishes": (
            perfect_gap is not None and degenerate_gap is not None
            and abs(perfect_gap - degenerate_gap) > 1e-12),
        "probe_bit": n_changed > 0,
        "n_cases_changed": n_changed,
    })
    return row


def check_headline_direction_coverage(
    measured: Dict[str, Dict[str, object]],
    contract: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """Put every declaration in `HEADLINE_DIRECTION_COVERAGE` on trial against
    the measurement and return the VIOLATIONS (empty = the register is honest).

    Separate from `measure_...` so the CLI can print the rows every run without
    raising, and so the test suite asserts on named violations rather than on a
    traceback. Each rule below closes a shape in which this register could stop
    describing the code:

      * a both-directions claim that does NOT tell its degenerate apart is the
        original defect, wearing a register entry;
      * a debt entry that DOES tell them apart has been fixed and the entry has
        rotted -- it must be re-derived, not left claiming a blindness the code
        no longer has (the D10 lesson: a characterization note that outlives the
        thing it characterises misleads worse than none);
      * a one-directional entry with neither a `debt_atom` nor a `covered_by` is
        an unowned hole -- the register's own class statement says it MUST name
        the atom that will make it;
      * a `covered_by` whose sibling does not itself count both directions is a
        cover claim covering nothing;
      * a vacuous probe (`probe_bit` false) proves NOTHING in either direction
        and must never be read as a pass.
    """
    contract = HEADLINE_DIRECTION_COVERAGE if contract is None else contract
    violations: List[str] = []
    for dim in sorted(measured):
        violations.extend(_check_one_entry(dim, measured[dim], contract[dim]))
    return violations


def _check_one_entry(
    dim: str, row: Dict[str, object], decl: Dict[str, object]
) -> List[str]:
    """One entry's declaration against its measurement. Split out of
    `check_headline_direction_coverage` so each rule reads on its own."""
    violations: List[str] = []
    both = bool(decl["headline_counts_both_directions"])
    if not row.get("probe_bit"):
        return [
            f"{dim}: the direction probe is VACUOUS (it changed nothing / "
            "scored an empty population), so it proves nothing in either "
            "direction and must not be read as a pass"
        ]
    if both and not row["distinguishes"]:
        violations.append(
            f"{dim}: declared to count BOTH error directions, but its "
            f"indiscriminate degenerate scores {row['degenerate_gap']} -- "
            f"identical to a perfect company ({row['perfect_gap']}). A "
            "one-directional headline cannot tell a precise company from "
            "an indiscriminate one"
        )
    if not both and row["distinguishes"]:
        violations.append(
            f"{dim}: declared ONE-DIRECTIONAL (debt "
            f"{decl.get('debt_atom')!r}), but it DOES tell its degenerate "
            f"apart ({row['perfect_gap']} -> {row['degenerate_gap']}). The "
            "entry has rotted and must be re-derived"
        )
    if not both and not decl.get("debt_atom") and not decl.get("covered_by"):
        violations.append(
            f"{dim}: one-directional with neither a `debt_atom` nor a "
            "`covered_by` -- an unowned hole. This register's own class "
            "statement requires it to measure both directions or NAME the "
            "atom that will make it"
        )
    if decl.get("covered_by") and not row.get("cover_is_two_directional"):
        violations.append(
            f"{dim}: claims its direction is covered by "
            f"'{decl['covered_by']}', which does not itself count both "
            "directions -- a cover claim covering nothing"
        )
    if dim == "detection_latency" and row.get("n_truly_current_in_population"):
        violations.append(
            f"{dim}: {row['n_truly_current_in_population']} truly-current "
            "case(s) reached the latency population, so the headline is no "
            "longer truth-conditioned and its cover claim (the sibling "
            "counts the over-flagging direction) no longer holds"
        )
    return violations


def _measure_conditional_population(
    dim: str, result: Dict[str, object]
) -> Dict[str, object]:
    """The probe for a dimension whose population is TRUTH-CONDITIONED, so no
    belief-side degenerate exists (`detection_latency`). What is measurable is
    the CONDITION: that no truly-current case can reach the headline at all,
    which is what makes 'the sibling counts that direction' a division of
    labour rather than a hole."""
    if dim != "detection_latency":
        raise ValueError(
            f"no conditional-population probe for '{dim}' -- an entry with no "
            "degenerate strategy and no probe would be unmeasured"
        )
    inputs = result.get("latency_inputs")
    if not inputs:
        raise ValueError(
            "score_triad published no `latency_inputs`, so the latency "
            "dimension's population claim cannot be checked -- an unreachable "
            "entry reads exactly like a clean one"
        )
    scored = set(inputs["recon_lag_days"]) | set(inputs["dd_lag_days"])
    truly_failed = set(inputs["truly_failed_keys"])
    intruders = scored - truly_failed
    return {
        "degenerate_strategy": None,
        "perfect_gap": None,
        "degenerate_gap": None,
        # A truth-conditioned headline cannot tell a precise company from an
        # indiscriminate one BY CONSTRUCTION -- stated as the measurement it is,
        # not left absent.
        "distinguishes": False,
        "n_latency_population": len(scored),
        "n_truly_current_in_population": len(intruders),
        # The probe is vacuous if the population is empty: nothing was checked.
        "probe_bit": len(scored) > 0,
        "n_cases_changed": 0,
    }


# ---------------------------------------------------------------------------
# ORGAN_QUERY_GRID -- can this instrument RESOLVE what it publishes? (atom D23,
# H27 Expert Hour #7, 2026-08-10)
#
# THE CLASS. Two of this module's readings are not computed from the company's
# output at all: they are taken by ASKING the company's organ a yes/no question
# on a grid of candidate DATES that the harness builds itself, from the organ's
# own rule (`candidates = {r.due_date + reconciliation_grace_days}`). Wherever a
# harness reads a QUANTITY by querying an organ on a grid of its own making, the
# reading is QUANTISED TO THAT GRID -- and the resolution is a property of the
# harness, not of the company. `detection_latency_gap`'s own docstring claimed
# the opposite in as many words ("asked of the organ itself, never re-derived
# here (R15 independence -- a harness re-implementation of `due + grace` would
# be a tautology that could not fail if the organ's rule changed)"). The organ
# was indeed asked; it was asked at exactly ONE date per period, and that date
# was the harness's re-derivation of `due + grace`. Independent in FORM,
# tautologous in VALUE.
#
# THE GENERAL RULE THIS LEAVES, which outlives the instance: asking an organ is
# not independence. A grid reading's RESOLUTION and its RANGE are properties of
# the harness, so both have to be declared and re-measured beside the number,
# and a grid whose bounds are the organ's own rule reads that rule back whatever
# the organ does. Only a bound the COMPANY imposes (here: it cannot know an
# unissued bill went unpaid) is a bound on the company.
#
# AS FOUND, 2026-08-10 (n=300/600, seeds 7/11/23, via the declared
# `organ_reconciliation_drift_days` counterfactual -- world and every truth-side
# rule untouched, so all movement is the company's detector moving). The grid
# was `sorted({r.due_date + reconciliation_grace_days})`, one candidate per
# period:
#
#   organ drift    recon first-knowledge mean    latency headline    detection
#     -20 d (flags 15 days BEFORE due)   5.0        2.132353          0.012100
#      -5 d (flags the day it is due)    5.0        2.132353          0.012100
#      -1 d                              5.0        2.132353          0.012100
#       0 d (as shipped)                 5.0        2.132353          0.012100
#      +1 d                             26.0        7.124088          0.024362
#      +7 d                             26.0        7.124088          0.024362
#     +21 d                             26.0        7.124088          0.024362
#
# IMPROVEMENT was UNBOUNDED-BLIND (`recon_lag_days` the CONSTANT 5 for all 204
# dated cases: `reconciliation_grace_days`, a harness input parameter, echoed
# back) and DEGRADATION was QUANTISED TO 21 DAYS (`PERIOD_SPACING_DAYS`): a
# one-day-later detector missed its period's only candidate and was next dated
# at the NEXT period's, so +1/+7/+21 were one number and the last period's cases
# left the population entirely (undated 0 -> 59 at seed 7, n=600).
#
# AS RESHAPED, same probe, same seeds (atom D23, this tick). The grid is DAILY
# from the invoice's ISSUE date to `as_of` (`organ_query_dates`):
#
#   organ drift    recon first-knowledge mean    latency headline    detection
#      -20 d                             -14.0      -14.000000        0.500000
#       -5 d                             -14.0      -14.000000        0.500000
#       -1 d                               4.0        2.019608        0.018771
#        0 d (as shipped)                  5.0        2.343137        0.014505
#       +1 d                               6.0        2.666667        0.014505
#       +7 d                              12.0        4.607843        0.009386
#      +21 d                              26.0        8.268041        0.029629
#
# A one-day company movement is now published as one day, in BOTH directions,
# and the same shape holds at seeds 11 and 23 (baseline 5.0, -1d -> 4.0,
# +1d -> 6.0 at all three). `n_recon_detected_undated` is 0 everywhere: no case
# leaves the population for want of a candidate.
#
# THE RESIDUAL WAS THE COMPANY'S FLOOR, NOT THE GRID'S, and it is why this
# register survived its own repair rather than being deleted. Every drift of -5
# or beyond read -14.0 -- one number for companies 15 days apart -- because
# `age_open_items` clamped `days_overdue=max(0, days)`, so any grace <= 0 fired
# from the day the invoice was issued and no earlier detector was representable.
# That was a question about the ORGAN, filed as atom D24, and no candidate grid
# could answer it: the register declared COLLAPSED PAIRS (two different
# companies that must read alike) where it used to declare invisibilities.
#
# ------------------------------------------------------------------------
# AND THEN D24 LANDED, SAME DAY (2026-08-10), and this register's own control
# fired BY NAME the moment it did -- a declared collapse whose two companies
# now read differently is a debt entry outliving its debt. What follows is the
# re-derivation the control demanded, measured on the same probe (n=300, seeds
# 7/11/23), and the shape it leaves is the general lesson:
#
#   organ drift    recon first-knowledge mean    detection    at-issue-floor
#      -30 d                     -14.0            0.500000     102 of 102
#      -20 d                     -14.0            0.500000     102 of 102
#      -15 d                     -10.0            0.500000       0
#       -5 d                       0.0            0.025597       0
#       -1 d                       4.0            0.018771       0
#        0 d (as shipped)          5.0            0.014505       0
#       +1 d                       6.0            0.014505       0
#       +7 d                      12.0            0.009386       0
#
# The -5d/-20d pair is fifteen days apart in fact and is now fifteen days apart
# in BOTH readings. It is therefore declared as a DISTINCT PAIR: two companies
# that must NOT read alike. That declaration is the only thing in this file
# that fails if the clamp comes back, and it is the direction the old register
# could not check -- `collapsed_pairs` could only catch the repair, never the
# reversion.
#
# NOT EVERY RESIDUAL IS A DEBT, and conflating the two is how a register like
# this rots. Three residuals are left and they are three DIFFERENT kinds:
#
#   * -20d and -30d read alike in both readings, and the witness says why:
#     `n_recon_dated_at_issue_floor` is the WHOLE population for both and zero
#     at the baseline. Nothing exists to be reconciled before the invoice is
#     issued, so no company can be built that resolves them. That is a bound on
#     the COMPANY'S KNOWLEDGE, not a debt -- no atom will ever close it, and an
#     entry naming an atom for it would be a promise nobody can keep.
#   * -15d and -20d read alike in the SET reading (both 0.500000: each flags
#     every invoice by `as_of`) while the DATE reading separates them (-10.0 vs
#     -14.0). That is a property of the READING'S SHAPE -- a saturated set has
#     nowhere further to go -- and the sibling entry is its witness.
#   * +1d moves the DATE reading and not the SET one, for the same reason.
#
# So each residual now carries an OWNERSHIP RECORD naming which of the three it
# is, and the control refuses a claim it cannot witness: a "company knowledge"
# bound whose readings are NOT at the floor is a debt in disguise, and a
# "reading shape" bound the sibling reading is equally blind to is a dead
# instrument in disguise. `debt_atom` survives for residuals that ARE debts;
# both entries now carry None, because none of what is left is one.
#
# THE ENTRIES ARE STILL DIFFERENTIAL, and now in two directions rather than
# one: the +1d company moves the DATE reading and leaves the SET reading where
# it was, and the -15d company moves the DATE reading while the SET reading has
# already saturated. They collapse together only at the point where the company
# itself goes blind.
# The atom whose landing separated the pair this register used to declare as a
# collapse. Named in the DISTINCT-pair violation so a reversion says whose
# repair it is reverting, not merely that two numbers agree.
ORGAN_CLOCK_REPAIR_ATOM = "D24_the_latency_floor_is_the_organs_clamped_overdue"

# The witness for a COMPANY-KNOWLEDGE bound on these two readings: a case first
# known on the invoice's own issue date is at the earliest date the company
# could possibly hold the invoice at all. Saturation of this witness (the whole
# latency population sitting on it) is what tells a bound from a debt.
_AT_ISSUE_FLOOR_WITNESS = {
    "dimension": "detection_latency",
    "key": "n_recon_dated_at_issue_floor",
    "population_key": "n_latency_population",
}

# EVERY GROUP OF COUNTERFACTUAL COMPANIES THE SET READING PUBLISHES AS ONE
# NUMBER (atom D31), measured on the book-derived grid at n=300, seeds 7/11/23
# and bit-identical on all three. Written out rather than summarised because
# the rule is EXACTNESS: an undeclared collapse is the blindness a
# register-derived grid could not reach, and a declared collapse the sweep
# reads apart is a debt entry outliving its debt. The first run is the tail the
# two declared pairs sampled; the rest were invisible to this register.
_RECON_SET_COLLAPSED_RUNS = (
    (-30, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6),
    (-4, -3), (0, 1), (6, 7), (9, 10), (11, 12, 13),
    (17, 18, 19, 20, 21, 22, 23, 24), (28, 29), (44, 45), (61, 62),
    (65, 66, 67), (68, 69), (72, 73, 74), (76, 77, 78), (80, 81),
    (82, 83, 84, 85, 86, 87, 88),
)


ORGAN_QUERY_GRID: Dict[str, Dict[str, object]] = {
    "recon_lag_days": {
        "reading": "date",
        "feeds": "detection_latency",
        "headline_key": "mean_lag_days_without_dd_channel",
        # Drifts of the COMPANY's own detector that must move the reading by
        # EXACTLY ZERO, and those that must move it.
        "invisible_drifts": (),
        "visible_drifts": (-15, -5, -1, 1),
        # Two DIFFERENT companies that must read ALIKE. What is left after D24
        # is where the company itself goes blind: a detector wanting to fire
        # more than a payment term before the due date is asking about an
        # invoice that has not been issued.
        "collapsed_pairs": ((-20, -30),),
        # Two different companies that must NOT read alike -- the D24 repair,
        # and the only declaration here that fails if the clamp comes back.
        # `collapsed_pairs` can catch a residual being fixed; only this catches
        # a fix being undone.
        "distinct_pairs": ((-5, -20),),
        # The measured quantisation: what a ONE-day company degradation is
        # published as.
        "reported_days_for_a_one_day_drift": 1.0,
        # WHERE THE READING STOPS RESOLVING THE COMPANY (atom D31), measured on
        # a grid derived from the BOOK rather than from the four lines above.
        # One run, and it is the tail: -19 is
        # `-(PAYMENT_TERMS_DAYS + DEFAULT_RECONCILIATION_GRACE_DAYS)`, the day
        # the drifted detector reaches the invoice's own issue date, and every
        # faster company reads -14.0 with the WHOLE latency population sitting
        # on `n_recon_dated_at_issue_floor`. The register's own grid held one
        # PAIR here (-20, -30) and could confirm neither the edge nor its cause.
        "collapsed_runs": ((-30, -20, -19),),
        "saturates_below": -19,
        "saturates_above": None,
        "saturation_atom": "BOUND:the invoice's own issue date",
        "saturation_atom_below": "BOUND:the invoice's own issue date",
        "saturation_atom_above": None,
        # THE CONSTANTS THAT SET THAT EDGE, and the census answer D30 pointed
        # at without giving: `predict_recon_floor_from_constants` reproduces
        # -19 from these two alone, so the attribution is arithmetic rather
        # than a restatement of the reading (the D30 rule, one band over).
        "edge_constants": ("PAYMENT_TERMS_DAYS",
                           "DEFAULT_RECONCILIATION_GRACE_DAYS"),
        # WHERE THE INSTRUMENT STOPS READING AT ALL. Beyond +86 no failure is
        # detected before `as_of` on every seed, the latency population empties
        # and the mean is None -- and `None != baseline` read as MOVEMENT in
        # the measurement this atom replaced, i.e. an instrument that had
        # stopped reading counted as resolution (the D28 fail-open, live here).
        # Declared WITH its witness: the population itself, which must be 0.
        "undefined_drifts": (87, 88),
        "undefined_witness_key": ("detection_latency", "n_latency_population"),
        "debt_atom": None,   # nothing left here is a debt -- see the ownership
        "residual_ownership": {
            (-20, -30): {
                "kind": "company_knowledge",
                "witness": _AT_ISSUE_FLOOR_WITNESS,
                "why": (
                    "Both read -14.0 because both are dated at the invoice's "
                    "own ISSUE date, and `n_recon_dated_at_issue_floor` is the "
                    "whole latency population for both against 0 at the "
                    "baseline. `expected_collection_misses` reads "
                    "`age_open_items`, which holds nothing for an invoice that "
                    "has not been issued, so no company can be built that "
                    "separates them. A bound on what the company can KNOW, "
                    "never a debt: naming an atom for it would be promising a "
                    "fix nobody can write."
                ),
            },
        },
        "why": (
            "The grid is DAILY from the invoice's issue date to `as_of` (D23), "
            "and since D24 the ORGAN's own overdue clock is signed, so the "
            "reading tracks the company day for day in both directions across "
            "the due date: -15d reads -10.0, -5d reads 0.0, -1d reads 4.0 and "
            "+1d reads 6.0 against a 5.0 baseline. What it cannot resolve is "
            "two detectors that both want to fire before the invoice exists."
        ),
    },
    "flagged_via_reconciliation": {
        "reading": "set_membership",
        "feeds": "detection",
        "headline_key": None,   # the dimension's own `gap`
        # A SET IS NOT A CLOCK, and that is the whole difference between the
        # two entries: the date reading moves on a +1d company and this one
        # does not, because a detector one day slower still flags the SAME
        # invoices by `as_of`. That is a true property of a membership reading,
        # not a grid defect -- and it is why this entry keeps the register from
        # being a rule about days.
        "invisible_drifts": (1,),
        # +7 WAS HERE AND WAS THIS ENTRY'S EVIDENCE OF RESOLUTION (atom D31).
        # The book-derived sweep reads +6 and +7 as ONE number on every seed,
        # so it differs from the baseline and not from the company beside it --
        # D29's rule, one register over, unenforced because this register never
        # routed through the shared saturation check. Replaced by +8, which the
        # sweep reads APART from both its neighbours.
        "visible_drifts": (-1, 8),
        # TWO collapses of two different kinds, which is what makes this entry
        # worth keeping: one where the READING saturates and the sibling can
        # still tell the companies apart, one where the COMPANY goes blind and
        # neither can.
        "collapsed_pairs": ((-15, -20), (-20, -30)),
        "distinct_pairs": ((-5, -20),),
        "reported_days_for_a_one_day_drift": None,   # not a reading in days
        # SIXTEEN GROUPS OF COMPANIES PUBLISHING ONE FIGURE (atom D31), of
        # which the two declared pairs above were a 2-point sample of the first.
        # BELOW -6 every company has flagged every invoice and the gap is the
        # no-skill 0.5; ABOVE +82 nothing further is detected before `as_of`.
        # The interior runs are the quantisation: this reading is not
        # continuous in days anywhere.
        "collapsed_runs": _RECON_SET_COLLAPSED_RUNS,
        "saturates_below": -6,
        "saturates_above": 82,
        "saturation_atom": "BOUND:the flag-everything set",
        "saturation_atom_below": "BOUND:the flag-everything set",
        "saturation_atom_above": (
            "D31_the_recon_grid_saturates_beyond_this_books_window"),
        "undefined_drifts": (),
        "debt_atom": None,
        "residual_ownership": {
            1: {
                "kind": "reading_shape",
                "witness": {"entry": "recon_lag_days"},
                "why": (
                    "A detector one day slower still flags the same invoices "
                    "by `as_of`, so the SET is identical while the DATE "
                    "reading moves 5.0 -> 6.0 on the same drift and the same "
                    "population. The sibling entry is the witness: if it were "
                    "blind here too, this would be a dead instrument rather "
                    "than a property of a membership reading."
                ),
            },
            (-15, -20): {
                "kind": "reading_shape",
                "witness": {"entry": "recon_lag_days"},
                "why": (
                    "Both read 0.500000 -- the flag-everything gap. A company "
                    "flagging from ten days before due and one flagging from "
                    "the issue date have both flagged every invoice by "
                    "`as_of`, so a SET has nowhere further to go. The DATE "
                    "reading separates the same pair (-10.0 vs -14.0), which "
                    "is what proves this is saturation of this reading rather "
                    "than the instrument or the company going blind."
                ),
            },
            (-20, -30): {
                "kind": "company_knowledge",
                "witness": _AT_ISSUE_FLOOR_WITNESS,
                "why": (
                    "The one collapse the two readings SHARE, and the witness "
                    "is the same: the whole population dated at the invoice's "
                    "issue date. Neither reading can separate them because the "
                    "company cannot."
                ),
            },
        },
        "why": (
            "SET membership off the same grid, and it is the DIFFERENTIAL "
            "entry that keeps this register from being a rule about one "
            "reading. It parts company with the date reading in BOTH "
            "directions -- upward at +1d (a set is not a clock) and downward "
            "at -15d (a saturated set has nowhere to go) -- and joins it only "
            "at the issue-date floor, where the company itself is blind."
        ),
    },
}


def measure_organ_query_grid_resolution(
    *,
    n_customers: int = 300,
    seed: int = 7,
    register: Optional[Dict[str, Dict[str, object]]] = None,
    runner: Optional[Callable[[int], Dict[str, object]]] = None,
) -> Dict[str, Dict[str, object]]:
    """MEASURE `ORGAN_QUERY_GRID` rather than trust it: re-score the SAME
    population against a counterfactual COMPANY whose reconciliation detector is
    drifted by each declared number of days, and record which drifts the reading
    actually saw.

    Returns {reading: {"baseline", "by_drift", "moved", "unmoved",
    "one_day_report", "probe_bit"}}.

    `probe_bit` is the VACUITY guard on the probe ITSELF: at least one declared
    drift must move SOMETHING somewhere in the register. A drift parameter that
    had silently stopped drifting the company would otherwise hand every
    `invisible_drifts` declaration a free pass -- the fail-silent shape this
    instrument has now produced five times, most recently inside the control
    written to close the previous one.
    """
    register = ORGAN_QUERY_GRID if register is None else register
    if runner is None:
        def runner(k: int) -> Dict[str, object]:
            return measure(n_customers=n_customers, seed=seed,
                           organ_reconciliation_drift_days=k)

    drifts = sorted(
        {0, 1}
        | {k for e in register.values()
           for k in tuple(e["invisible_drifts"]) + tuple(e["visible_drifts"])}
        # The collapse members are scored too, or a declared collapse would be
        # checked against readings that were never taken (atom D23's reshape).
        | {k for e in register.values()
           for pair in tuple(e.get("collapsed_pairs") or ()) for k in pair}
        # ...and the DISTINCT members likewise (atom D24's re-derivation).
        | {k for e in register.values()
           for pair in tuple(e.get("distinct_pairs") or ()) for k in pair}
    )
    scored = {k: runner(k) for k in drifts}

    def _read(entry: Dict[str, object], result: Dict[str, object]) -> object:
        dim = result[str(entry["feeds"])]
        key = entry["headline_key"]
        return dim.gap if key is None else dim.components[str(key)]

    def _component(result: Dict[str, object], dimension: str, key: str) -> object:
        return result[dimension].components[key]

    out: Dict[str, Dict[str, object]] = {}
    any_movement = False
    for name in sorted(register):
        entry = register[name]
        base = _read(entry, scored[0])
        by_drift = {k: _read(entry, scored[k]) for k in drifts if k != 0}
        moved = sorted(k for k, v in by_drift.items() if v != base)
        unmoved = sorted(k for k, v in by_drift.items() if v == base)
        any_movement = any_movement or bool(moved)
        one_day = by_drift.get(1)
        all_readings = {**by_drift, 0: base}
        out[name] = {
            "baseline": base,
            "by_drift": by_drift,
            "moved": moved,
            "unmoved": unmoved,
            # Which declared collapses actually collapsed (atom D23's reshape):
            # the pair's two readings, and whether they are one number.
            "collapses": {
                pair: {
                    "readings": (all_readings.get(pair[0]), all_readings.get(pair[1])),
                    "collapsed": (all_readings.get(pair[0])
                                  == all_readings.get(pair[1])),
                    "distinct_from_baseline": (all_readings.get(pair[0]) != base),
                }
                for pair in tuple(entry.get("collapsed_pairs") or ())
            },
            # Which declared DISTINCTIONS actually hold (atom D24): two
            # companies the register says must NOT read alike.
            "distinctions": {
                pair: {
                    "readings": (all_readings.get(pair[0]), all_readings.get(pair[1])),
                    "distinct": (all_readings.get(pair[0])
                                 != all_readings.get(pair[1])),
                }
                for pair in tuple(entry.get("distinct_pairs") or ())
            },
            # The WITNESS behind every COMPANY-KNOWLEDGE ownership claim, read
            # per drift as (witness, population) so the control can tell a
            # bound (saturated for the residual, not at the baseline) from a
            # debt wearing a bound's clothes (atom D24).
            "bound_witness": {
                res_key: {
                    k: (_component(scored[k], rec["witness"]["dimension"],
                                   rec["witness"]["key"]),
                        _component(scored[k], rec["witness"]["dimension"],
                                   rec["witness"]["population_key"]))
                    for k in all_readings
                }
                for res_key, rec in (entry.get("residual_ownership") or {}).items()
                if rec.get("kind") == "company_knowledge"
            },
            # How many DAYS a one-day company degradation is published as --
            # None where the reading is not in days, or where either side is.
            "one_day_report": (
                None if entry["reported_days_for_a_one_day_drift"] is None
                or base is None or one_day is None
                else round(float(one_day) - float(base), 6)
            ),
        }
    for row in out.values():
        row["probe_bit"] = any_movement
    return out


def _reading_at(row: Dict[str, object], k: int) -> object:
    """One measured row's reading at drift `k` (0 is the baseline)."""
    return row["baseline"] if k == 0 else row["by_drift"].get(k)


def _check_residual_ownership(
    name: str,
    entry: Dict[str, object],
    row: Dict[str, object],
    measured: Dict[str, Dict[str, object]],
) -> List[str]:
    """Every DECLARED residual must say which KIND of residual it is, and the
    claim must be WITNESSED (atom D24).

    Before this, every residual in the register was a debt: it named an atom
    that would close it. That was true while one was outstanding and false the
    moment D24 landed, because what D24 left behind is not closeable by anyone
    -- nothing exists to reconcile before the invoice is issued. A register with
    only a debt shape has two bad options at that point: name an atom for a
    residual no atom can close (a promise nobody can keep), or delete the entry
    (and lose the only declaration that would catch the repair being undone).

    So a residual is owned as one of three kinds, and NONE of them is takeable
    on trust -- each has a measurement that refutes it:

      * `debt` -- names the atom that will close it (the pre-D24 shape);
      * `company_knowledge` -- no company can resolve it. Refuted unless the
        readings sit ON the company's floor, witnessed by a counter that is NOT
        saturated at the baseline (else the witness is a constant, and a
        constant witnesses nothing);
      * `reading_shape` -- this reading cannot express it. Refuted unless a
        SIBLING reading, on the same grid and the same population, CAN separate
        exactly what this one cannot. Two readings blind to the same thing are
        a dead instrument, not a property of either reading.
    """
    out: List[str] = []
    owned = entry.get("residual_ownership") or {}
    declared = (list(tuple(entry["invisible_drifts"]))
                + list(tuple(entry.get("collapsed_pairs") or ())))
    for res in declared:
        rec = owned.get(res)
        if rec is None:
            if entry.get("debt_atom"):
                continue        # entry-level debt ownership, the pre-D24 shape
            out.append(
                f"{name}: residual {res!r} has no `debt_atom` and no ownership "
                "record -- an unowned hole; say whether it is a DEBT (name the "
                "atom), a bound on what the COMPANY can know, or a property of "
                "this READING's shape, and let the control test the claim"
            )
            continue
        kind = rec.get("kind")
        if kind == "debt":
            if not rec.get("atom"):
                out.append(
                    f"{name}: residual {res!r} is owned as a DEBT with no atom "
                    "named -- an unowned hole"
                )
        elif kind == "company_knowledge":
            witness = row["bound_witness"].get(res) or {}
            members = res if isinstance(res, tuple) else (res,)
            base = witness.get(0)
            if not witness or base is None or base[1] in (None, 0):
                out.append(
                    f"{name}: residual {res!r} claims a bound on what the "
                    "COMPANY can know, but its witness was not measured (or its "
                    "population is empty) -- an unwitnessed bound is a FAILED "
                    "check, never a pass"
                )
                continue
            if base[0] >= base[1]:
                out.append(
                    f"{name}: residual {res!r} claims a COMPANY-KNOWLEDGE bound "
                    f"whose witness is already saturated at the BASELINE "
                    f"({base[0]}/{base[1]}) -- a constant witnesses nothing; the "
                    "bound is unproven"
                )
                continue
            for k in members:
                wit = witness.get(k)
                if wit is None or wit[1] in (None, 0) or wit[0] != wit[1]:
                    out.append(
                        f"{name}: residual {res!r} is owned as a bound on what "
                        f"the COMPANY can know, but drift {k:+d}d reads "
                        f"{wit!r} against that floor rather than sitting ON it. "
                        "It is a DEBT wearing a bound's clothes -- name the "
                        "atom that will close it"
                    )
        elif kind == "reading_shape":
            sib_name = str((rec.get("witness") or {}).get("entry"))
            sib = measured.get(sib_name)
            if sib is None:
                out.append(
                    f"{name}: residual {res!r} claims a property of this "
                    f"READING's shape witnessed by `{sib_name}`, which was not "
                    "measured -- an unwitnessed bound is a FAILED check"
                )
                continue
            if isinstance(res, tuple):
                readings = tuple(_reading_at(sib, k) for k in res)
                if readings[0] == readings[1]:
                    out.append(
                        f"{name}: residual {res!r} is owned as a property of "
                        f"this READING's shape, but `{sib_name}` cannot "
                        f"separate those companies either ({readings!r}). Two "
                        "readings blind to the same thing are a dead "
                        "instrument, not a shape"
                    )
            elif res not in sib["moved"]:
                out.append(
                    f"{name}: drift {res:+d}d is owned as a property of this "
                    f"READING's shape, but `{sib_name}` did not move on it "
                    "either. Two readings blind to the same thing are a dead "
                    "instrument, not a shape"
                )
        else:
            out.append(
                f"{name}: residual {res!r} is owned as {kind!r}, which is not a "
                "kind this control can put on trial -- an ownership claim "
                "nothing checks is worse than none"
            )
    return out


def check_organ_query_grid_resolution(
    measured: Dict[str, Dict[str, object]],
    register: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """Put every `ORGAN_QUERY_GRID` declaration on trial against the measurement
    and return the VIOLATIONS (empty = the register is honest).

    Each rule closes a shape in which this register could stop describing the
    code:

      * a drift declared INVISIBLE that moves the reading means the blindness
        has been REPAIRED (D23 landing is the expected cause) and the entry has
        rotted -- it must be re-derived, never left claiming a blindness the
        code no longer has;
      * a drift declared VISIBLE that moves nothing means the reading has gone
        blinder than the register admits, or the probe is dead;
      * a declared COLLAPSE whose two companies now read DIFFERENTLY has been
        resolved -- the same rot as a repaired invisibility, in the shape this
        register needed once D23 left no invisibility on the date reading;
      * a declared collapse whose two companies read the BASELINE is not a
        collapse at all, it is plain invisibility wearing a pair's clothes,
        and would let an entry claim a falsifiable residual it does not have;
      * a declared DISTINCTION whose two companies read ALIKE means a repair
        this register recorded has been REVERTED (atom D24's clock going back
        behind its clamp is the named cause) -- the direction `collapsed_pairs`
        structurally cannot check, since a collapse rule only ever fires when a
        residual is FIXED;
      * a residual owned as a COMPANY-KNOWLEDGE bound whose readings are not
        actually at the company's floor -- or whose witness is saturated at the
        BASELINE too, so it is a constant rather than a reading -- is a debt
        wearing a bound's clothes, and "no atom can close this" is the one
        claim in a register that must never be takeable on trust;
      * a residual owned as a READING-SHAPE bound that the SIBLING reading is
        equally blind to is a dead instrument wearing a shape's clothes;
      * a residual owned as a DEBT with no atom named is the unowned hole the
        `debt_atom` rule has always caught, now keyed per residual;
      * an entry declaring NEITHER an invisibility NOR a collapse is
        all-visible and cannot fail on the defect this register exists for --
        the same vacuity the all-invisible blanket claim is, from the other
        end;
      * a `reported_days_for_a_one_day_drift` that no longer matches the
        measurement means the quantisation moved and the published caveat, which
        interpolates this number, is now wrong;
      * a vacuous probe (`probe_bit` false) proves NOTHING in either direction
        and must never be read as a pass;
      * a declared blindness with no `debt_atom` is an unowned hole.
    """
    register = ORGAN_QUERY_GRID if register is None else register
    violations: List[str] = []

    def _owner(entry: Dict[str, object], res_key) -> str:
        """Who owns this residual, for the RE-DERIVE diagnostics. An entry-level
        `debt_atom` still answers where one is declared; otherwise the residual's
        own ownership record does."""
        rec = (entry.get("residual_ownership") or {}).get(res_key) or {}
        return str(rec.get("atom") or entry.get("debt_atom")
                   or f"the {rec.get('kind') or 'unrecorded'} residual owner")

    for name in sorted(measured):
        row, entry = measured[name], register[name]
        if not row["probe_bit"]:
            violations.append(
                f"{name}: the drift probe moved NOTHING anywhere in the "
                "register -- an inert counterfactual company cannot evidence "
                "either a blindness or a repair"
            )
        for k in entry["invisible_drifts"]:
            if k in row["moved"]:
                violations.append(
                    f"{name}: drift {k:+d}d is declared INVISIBLE but moved the "
                    f"reading {row['baseline']!r} -> {row['by_drift'][k]!r}. If "
                    f"{_owner(entry, k)} has landed, RE-DERIVE this entry; a "
                    "debt entry outliving its debt misleads worse than none"
                )
        for k in entry["visible_drifts"]:
            if k in row["unmoved"]:
                violations.append(
                    f"{name}: drift {k:+d}d is declared VISIBLE but left the "
                    f"reading at {row['baseline']!r} -- the reading is blinder "
                    "than this register admits"
                )
        pairs = tuple(entry.get("collapsed_pairs") or ())
        if not pairs and not tuple(entry["invisible_drifts"]):
            violations.append(
                f"{name}: declares NO invisibility and NO collapse -- an "
                "all-visible entry cannot fail on the defect this register "
                "exists for; state the residual or delete the entry"
            )
        for pair in pairs:
            got = row["collapses"].get(pair, {})
            if not got.get("collapsed"):
                violations.append(
                    f"{name}: drifts {pair[0]:+d}d and {pair[1]:+d}d are "
                    f"declared to COLLAPSE to one reading but read "
                    f"{got.get('readings')!r}. If "
                    f"{_owner(entry, pair)} has landed, RE-DERIVE this entry; a "
                    "debt entry outliving its debt misleads worse than none"
                )
            elif not got.get("distinct_from_baseline"):
                violations.append(
                    f"{name}: drifts {pair[0]:+d}d and {pair[1]:+d}d read the "
                    f"BASELINE {row['baseline']!r} -- that is an INVISIBILITY, "
                    "not a collapse; declare it in `invisible_drifts` where "
                    "the rule that checks it lives"
                )
        # THE REVERSION DIRECTION (atom D24). A collapse rule fires when a
        # residual is FIXED; nothing here fired when a fix was UNDONE.
        for pair in tuple(entry.get("distinct_pairs") or ()):
            got = row["distinctions"].get(pair, {})
            if not got.get("distinct"):
                violations.append(
                    f"{name}: drifts {pair[0]:+d}d and {pair[1]:+d}d are "
                    f"declared DISTINCT -- two companies {abs(pair[0] - pair[1])} "
                    f"days apart -- but both read {got.get('readings')!r}. The "
                    f"repair recorded by {ORGAN_CLOCK_REPAIR_ATOM} has been "
                    "REVERTED, or this reading has re-collapsed some other way"
                )
        violations.extend(_check_residual_ownership(name, entry, row, measured))
        expected = entry["reported_days_for_a_one_day_drift"]
        if expected is not None and row["one_day_report"] != expected:
            violations.append(
                f"{name}: a one-day company degradation is published as "
                f"{row['one_day_report']} days, not the declared {expected} -- "
                "the grid's quantisation has moved and the caveat travelling "
                "with the number now states the wrong step"
            )
        # The per-residual ownership check above covers the DECLARED residuals.
        # This is the entry-level remainder: a reading whose quantisation is
        # coarser than a day, or which sits blind on drifts it never declared,
        # still owes an owner and has no residual key to hang one on.
        if ((row["unmoved"] or expected not in (None, 1.0))
                and not entry["debt_atom"]
                and not (entry.get("residual_ownership") or {})):
            violations.append(
                f"{name}: declares a blindness with no `debt_atom` and no "
                "ownership record -- an unowned hole; name the atom that will "
                "close it, or the bound that means nobody can"
            )
    return violations


def predict_published_latency_step_days(
    n_latency_population: Optional[int],
    n_earliest_via_dd_channel: Optional[int],
) -> Optional[float]:
    """How far the PUBLISHED `detection_latency` headline moves for one day of
    reconciliation-detector drift, predicted from THIS BOOK's own coverage
    witnesses (atom D32, Expert Hour #14). Reads no sweep, no seed and no
    re-scoring -- the D25/D30 population-side-predictor pattern.

    WHY IT IS NOT 1.0. `ORGAN_QUERY_GRID["recon_lag_days"]` measures
    `mean_lag_days_without_dd_channel` -- the DD-channel-DELETED counterfactual
    -- and resolves it day for day, which is true OF THAT READING. The
    published headline is `mean_lag_days`, a mean over the WHOLE latency
    population, and a case whose earliest knowledge came from the DD channel
    does not move when the reconciliation detector does. So the headline moves
    by the recon arm's SHARE of that population, which is a property of the
    book's payment-method mix and not a constant: 0.32/0.36/0.27 on seeds
    7/11/23 of the offline scenario.

    Returns None when the population is empty -- a book nothing was detected in
    has no step, and a 0.0 there would read as "the headline is inert", which
    is the strongest possible claim handed out for free.
    """
    if not n_latency_population:
        return None
    n_recon_earliest = int(n_latency_population) - int(n_earliest_via_dd_channel or 0)
    return n_recon_earliest / float(n_latency_population)


def organ_query_grid_caveat(one_day_report: Optional[float] = None,
                            published_step: Optional[float] = None) -> str:
    """The resolution caveat that travels WITH the latency number, interpolated
    from the measurement rather than written as prose (the D19/D20/D22 pattern:
    a caveat nobody re-derives decays into a claim).

    `published_step` is atom D32's correction, and it is the whole reason this
    signature grew. Until Expert Hour #14 this sentence reported the register's
    `reported_days_for_a_one_day_drift` -- 1.0 -- as what "is published", while
    the register's own `headline_key` names a SUB-READING and the figure the
    reader is looking at moves about a third of that. A caveat stamped on a
    number must state that NUMBER's resolution; stating an adjacent reading's
    is how a reader converts a movement into three times too few days of
    company error.
    """
    step = (ORGAN_QUERY_GRID["recon_lag_days"]["reported_days_for_a_one_day_drift"]
            if one_day_report is None else one_day_report)
    subject = ORGAN_QUERY_GRID["recon_lag_days"]["headline_key"]
    if published_step is None:
        headline = (
            "THE PUBLISHED HEADLINE'S OWN STEP IS NOT MEASURED ON THIS CALL "
            "-- read it as the sub-reading's, never as this figure's. "
        )
    else:
        headline = (
            f"THAT IS THE STEP OF `{subject}`, THE DD-CHANNEL-DELETED "
            "SUB-READING THE REGISTER MEASURES -- NOT OF THE FIGURE THIS "
            "CAVEAT IS STAMPED ON (atom D32). The published headline is "
            f"`mean_lag_days`, and it moves {published_step:.6f} days per day "
            "of detector drift on THIS book, because a case whose earliest "
            "knowledge came from the DD channel does not move when the "
            "reconciliation detector does. The ratio is the recon arm's share "
            "of the latency population -- a property of this book's "
            "payment-method mix, not a constant (0.32/0.36/0.27 on seeds "
            "7/11/23). A reader converting a movement in this headline into "
            "days of company error with the 1.0 above understates it by about "
            "three times. "
        )
    return (
        "GRID RESOLUTION (atom D23, reshaped and re-measured 2026-08-10): the "
        "reconciliation first-knowledge date behind this number is read by "
        "asking the company's organ on a DAILY grid of candidate dates, from "
        "the invoice's own ISSUE date to `as_of`. So it tracks the company "
        f"day for day: a one-day-slower detector is read as {step} days "
        "later, and a one-day-faster one a day earlier. " + headline
        + "It replaced a grid of "
        "ONE candidate per period at the harness's own `due + grace`, which "
        "published that PARAMETER back for every faster company and reported a "
        "one-day degradation as 21 days. THE REMAINING FLOOR IS THE COMPANY'S, "
        "NOT THE GRID'S, and since atom D24 it is only that: the organ's own "
        "overdue clock no longer clamps at zero, so a detector that fires "
        "BEFORE the due date is read as firing before the due date (a company "
        "flagging on the due date reads 0.0, one flagging ten days early reads "
        "-10.0). What no reading can separate is two detectors that would both "
        "fire before the invoice was ISSUED, because nothing exists to "
        "reconcile until it is. Cases sitting on that floor are counted in "
        "`n_recon_dated_at_issue_floor` and are 'at or before', never exact. "
        "R12: a diagnostic in days, never a target."
    )


# ---------------------------------------------------------------------------
# DIMENSION_DRIFT_RESOLUTION -- what is the SMALLEST company error each
# PUBLISHED dimension can see? (atom D25, H27 Expert Hour #8, 2026-08-10)
#
# THE CLASS, ONE KEYING WIDER THAN D23's. `ORGAN_QUERY_GRID` asks whether a
# reading taken on a grid of the HARNESS's own making is quantised to that
# grid, and answers it for the two readings off the RECONCILIATION candidate
# grid. Every dimension owes that question, and the grid is not always made of
# dates: the AGEING dimension's grid is where this population's invoices SIT
# relative to the 30/60/90 bucket boundaries, and that placement is built
# entirely from harness constants -- `FIRST_DUE_DATE`, `PERIOD_SPACING_DAYS`,
# `N_PERIODS`, `AS_OF_BUFFER_DAYS`. Every truly-overdue invoice in the scenario
# is 30, 51 or 72 days overdue at `as_of`; nothing else exists. Keyed to the
# reconciliation grid, D23's register could not reach that -- the THIRD time a
# register of this instrument has been escaped by its own keying (D19 out of
# the detection scorers, D22 out of the rate-shaped dimensions, this out of the
# date-grid readings).
#
# So the keyset is DERIVED from `published_dimensions`, exactly as
# `HEADLINE_DIRECTION_COVERAGE`'s is, and the perturbation is a DECLARED
# COUNTERFACTUAL COMPANY (`organ_terms_drift_days`) rather than a test's
# monkeypatch (the D20 rule: a counterfactual a reader cannot find in the repo
# is not part of the design).
#
# THREE STATES, CHECKED SEPARATELY -- a register whose entries all land on one
# side is a blanket claim wearing a register's clothes (the Hour #6 lesson):
#   * ON PATH AND BLIND -- declares the drifts it cannot see, and OWES a
#     `debt_atom`;
#   * ON PATH AND SIGHTED -- no blindness at all, which is what keeps the
#     register from being an excuse;
#   * OFF PATH -- the drift has no causal route to this dimension's organ at
#     all. That is the exemption shape D21 was hidden by, so it is the one
#     state that must name ANOTHER probe and have it MEASURED to move the
#     dimension: an unexercised dimension is unfalsifiable, not exempt.
# ---------------------------------------------------------------------------

RESOLUTION_SEEDS = (7, 11, 23)

# ---------------------------------------------------------------------------
# THE GRID THE REGISTER DID NOT CHOOSE
# (atom D28_the_resolution_grid_was_the_registers_own_claims, Expert Hour #10)
# ---------------------------------------------------------------------------
# THE DEFECT THIS CONSTANT EXISTS TO STOP, and it is D23's class escaped into
# the register built to close a resolution hole. `check_dimension_drift_
# resolution` DERIVES ITS KEYSET from what `score_triad` publishes -- that
# keying was removed in D25 and a dimension nobody sweeps now RAISES. Its GRID
# was still built the other way round:
#
#     drifts = {0} | declared invisible | declared visible | declared collapses
#
# so the exactness rule the register exists to enforce ("a band that may only
# shrink is the decay this register exists to stop") was only ever applied AT
# THE POINTS THE BAND ALREADY NAMED. The register was asked exactly where it
# had already answered. A blindness nobody guessed at was unreachable, and two
# undeclared companies publishing ONE number could not be seen at all.
#
# MEASURED (Expert Hour #10, n=300, seeds 7/11/23, all-seed agreement): the
# sparse grid touched {-8,-1,0,+1,+12} and declared `detection` blind to {+1},
# sighted at {-1}, collapsing nowhere. On this grid the same dimension has
# SEVEN groups of companies publishing one bit-identical figure and BOTH TAILS
# ARE SATURATED -- every supplier holding terms 6 TO 21 DAYS SHORTER than the
# world publishes ONE number (sixteen companies, one figure, every seed), as
# does every supplier 17 to 21 days LONGER. Below -6 the detection gap cannot
# tell a supplier a week short on its terms from one three weeks short: the
# direction that flags a paying customer as in arrears and posts the dunning
# letter. The register read -8 as MOVED -- as resolution -- because -8 happened
# to be in the *ageing* band and nothing beside it ever was.
#
# THE FIX IS THE GRID'S PROVENANCE, not its width. It is derived from the
# BOOK's calendar -- every integer drift across one billing cycle either way,
# the span over which this book's due dates are actually spread -- and
# `dense_drift_grid` may never read the register (asserted against its AST).
# The declared drifts are still UNIONED IN so a declaration outside the grid is
# scored rather than silently skipped; they no longer DEFINE what gets asked.
DRIFT_GRID_SPAN_DAYS = PERIOD_SPACING_DAYS


def dense_drift_grid(span_days: int = DRIFT_GRID_SPAN_DAYS) -> Tuple[int, ...]:
    """Every integer company terms-drift across one billing cycle either way.

    DERIVED FROM THE BOOK, NEVER FROM THE REGISTER (atom D28). The span is the
    billing cycle the book is spread over (`BILLING_CYCLE_SPREAD_DAYS ==
    PERIOD_SPACING_DAYS`), which is the only non-arbitrary width available: a
    drift larger than one cycle moves every invoice past the next account's
    place in the book, so nothing about the population is left to resolve.
    """
    return tuple(range(-int(span_days), int(span_days) + 1))


# THE SAME DEFECT, ON THE HALF D28 DID NOT REACH (atom D29, Expert Hour #11).
# D28 fixed the provenance of the TERMS grid and left its own lead standing:
# `measure_own_drift_resolution` still built the memory sweep from
# `own_invisible_drifts | own_visible_drifts`, so the belief saturation edge at
# -308 was an artefact of where D27 happened to sweep rather than a measured
# boundary. Seventh escape of a register's own keying, and this one was named
# in the previous Hour's leads -- a lead is not a control.
#
# The memory knob admits a grid that is not merely dense but COMPLETE. An event
# at age `a` is counted iff `a <= window`, so the counted set -- and therefore
# every reading -- can only change as the window crosses an event age. Between
# two adjacent event ages the reading is constant BY CONSTRUCTION, so scoring
# `{a, a-1 : a in ages}` plus the two extremes measures resolution exactly over
# the whole real line, not just over the swept points. That is strictly
# stronger than the terms grid's density argument, and it is cheaper: 62-66
# points per seed (measured: 65/66/62 on seeds 7/11/23, 70 once the three
# seeds' grids and the register's declarations are unioned) instead of an
# integer sweep from total amnesia to infinity. The count is a property of the
# BOOK, not a constant -- a book with more distinct failure ages scores more
# companies, which is the whole point of deriving it from the book.


def book_memory_grid(records: Sequence["PeriodRecord"], as_of: date,
                     window_days: Optional[int] = None) -> Tuple[int, ...]:
    """Every company MEMORY drift at which this book's reading can change.

    DERIVED FROM THE BOOK, NEVER FROM THE REGISTER (atom D29), and asserted
    against its own AST never to reach one. The drift is
    `organ_failure_window_drift_days`, i.e. `window - DD_FAILURE_WINDOW_DAYS`.

    Three parts, each non-arbitrary:

    * `a` and `a - 1` for every observed failure age `a` -- the window values
      either side of each event's boundary. These are the ONLY places the
      counted set changes, so the grid is complete rather than dense.
    * TOTAL AMNESIA (`window == 0`), the extreme of the parameter: without a
      second point below the newest event, the low tail holds one grid point
      and a collapsed run needs two, which is exactly why D27 measured
      `saturates_below = None` on a book that saturates below.
    * The SHIPPED company (`drift == 0`), the reading everything is compared
      against.
    """
    window = DD_FAILURE_WINDOW_DAYS if window_days is None else window_days
    ages = sorted({(as_of - r.due_date).days
                   for r in records if r.result == "failed"})
    grid = {0, -int(window)}
    for a in ages:
        grid.add(int(a) - window)
        grid.add(int(a) - 1 - window)
    return tuple(sorted(grid))


# WHICH KNOB GETS WHICH BOOK-DERIVED GRID. A knob absent from this mapping
# RAISES rather than falling back to the register's declarations: the fallback
# IS the defect, and a silent one would put the next off-path entry straight
# back where D27's was (atom D29).
OWN_DRIFT_BOOK_GRIDS: Dict[str, Callable[..., Tuple[int, ...]]] = {
    "organ_failure_window_drift_days": book_memory_grid,
}


# ---------------------------------------------------------------------------
# THE SAME DEFECT, ON THE REGISTER THAT FOUND IT
# (atom D31_the_recon_grid_saturates_beyond_this_books_window, Expert Hour #13)
# ---------------------------------------------------------------------------
# D28 fixed the provenance of the TERMS grid; D29 fixed the MEMORY grid and put
# both through ONE shared rule, `_check_saturation_and_collapse`, "so a
# saturation rule can no longer exist on one side of `in_causal_path` and not
# the other". There are THREE counterfactual company knobs in this harness and
# the shared rule reached two. `ORGAN_QUERY_GRID` -- atom D23's register, the
# one that FOUND this class -- still built its sweep the original way:
#
#     drifts = {0, 1} | invisible | visible | collapsed pairs | distinct pairs
#
# so every claim it makes about what the reconciliation readings can resolve was
# checked at exactly the points it had already named, and it had no notion of a
# collapsed RUN, a saturation EDGE, or an UNDEFINED reading at all. Eighth
# escape of a register's own keying, and this time it is the origin register.
#
# MEASURED (Expert Hour #13, n=300, seeds 7/11/23, every seed identical) on the
# grid below:
#
#   * the DATE reading (`recon_lag_days`) saturates BELOW at -19 and publishes
#     NO READING at +87/+88, where the latency population is empty on two of
#     three seeds. `None != baseline`, so the old measurement counted an
#     instrument that had stopped reading as RESOLUTION -- the fail-open D28
#     closed for the other two registers, live here;
#   * the SET reading (`flagged_via_reconciliation`, which IS the published
#     `detection` gap) has SIXTEEN groups of companies publishing one
#     bit-identical figure on every seed, saturating below at -6 (fifteen
#     companies on the flag-everything 0.5) and above at +82. The register
#     declared TWO 2-point pairs out of that;
#   * and +7 -- declared VISIBLE, i.e. offered as this entry's evidence of
#     resolution -- sits inside the collapsed run (+6, +7). That is D29's own
#     rule ("resolution is being told apart from your NEIGHBOURS"), unenforced
#     one register over because this register never routed through it.
#
# THE FIX IS THE ROUTE, not another rule: the knob set is derived from source,
# every knob must name a BOOK-DERIVED grid and a checker, and that checker is
# AST-verified to CALL the shared rule. A fourth knob cannot arrive without one.
RECON_DRIFT_KNOB = "organ_reconciliation_drift_days"


def book_recon_drift_grid(records: Sequence["PeriodRecord"], as_of: date,
                          grace_days: Optional[int] = None) -> Tuple[int, ...]:
    """Every reconciliation-detector drift at which this book's readings can
    change.

    DERIVED FROM THE BOOK, NEVER FROM THE REGISTER (atom D31), and asserted
    against its own AST never to reach one. The drift is
    `organ_reconciliation_drift_days`: the company's detector fires at
    `due + grace + k` instead of `due + grace`.

    COMPLETE, not merely dense, and the argument is `organ_query_dates`'s: the
    organ is asked on a DAILY grid from the invoice's own ISSUE date to
    `as_of`, so a detector wanting to fire before the issue date is read AT the
    issue date (constant below `issue - due - grace`) and one wanting to fire
    after `as_of` is not read at all (constant above `as_of - due - grace`).
    One integer per day between those two crossings -- plus one step outside
    each -- therefore measures resolution over the whole real line. Both ends
    are the BOOK's: the earliest issue relative to its due date, and the oldest
    invoice's distance to `as_of`.
    """
    grace = (DEFAULT_RECONCILIATION_GRACE_DAYS if grace_days is None
             else int(grace_days))
    if not records:
        return (0,)
    lo = min((r.issue_date - r.due_date).days for r in records) - grace - 1
    hi = max((as_of - r.due_date).days for r in records) - grace + 1
    return tuple(range(int(lo), int(hi) + 1))


def predict_recon_floor_from_constants(
    *,
    terms_days: Optional[int] = None,
    grace_days: Optional[int] = None,
) -> int:
    """The drift at which the DATE reading stops resolving the company, from
    the CONSTANTS alone (atom D31) -- reads no book, no draw and no seed.

    THE CENSUS ANSWER D30 POINTED AT AND DID NOT GIVE. `SCENARIO_CONSTANT_CENSUS`
    censuses `PAYMENT_TERMS_DAYS` as `bounds_resolution: False` -- true of the
    invoice-AGE band it measures -- and discharges it with "it bounds the
    DETECTION-LATENCY dimension instead (D23/D24) ... and is registered there".
    It was not registered there: `ORGAN_QUERY_GRID` named no constant at all,
    and the other half of this edge (`DEFAULT_RECONCILIATION_GRACE_DAYS`) is not
    even in the census's subject, which is derived from `build_scenario`'s AST
    while the grace window enters at `score_triad`. A constant discharged onto a
    register that never received it is unowned twice over.

    The identity, straight off `organ_query_dates` and `build_scenario`: the
    organ can first be asked on the invoice's ISSUE date, which is
    `PAYMENT_TERMS_DAYS` before its due date, and the shipped detector fires at
    `due + grace`, so a detector drifted by `-(terms + grace)` days or more is
    read at the floor and every faster company publishes one number.
    """
    terms = PAYMENT_TERMS_DAYS if terms_days is None else int(terms_days)
    grace = (DEFAULT_RECONCILIATION_GRACE_DAYS if grace_days is None
             else int(grace_days))
    return -(terms + grace)


# WHICH COUNTERFACTUAL KNOB IS SWEPT ON WHICH GRID, AND WHOSE CHECKER PUTS ITS
# READINGS THROUGH THE SHARED SATURATION RULE (atom D31). The keyset is DERIVED
# (`counterfactual_knobs`), so a knob added to the harness and left out of this
# route RAISES; and `check_counterfactual_knob_route` reads each named
# checker's AST, because naming a checker is not calling one -- Hour #11's "a
# lead is not a control", in the shape this route could otherwise take.
COUNTERFACTUAL_KNOB_ROUTE: Dict[str, Dict[str, object]] = {
    "organ_reconciliation_drift_days": {
        "grid": "book_recon_drift_grid",
        "checker": "check_organ_query_grid_saturation",
        "register": "ORGAN_QUERY_GRID",
        "why": (
            "The company's reconciliation detector. Swept from D23 and NEVER "
            "on a book-derived grid until D31 -- the register that found this "
            "class was the last to be put through it."
        ),
    },
    "organ_terms_drift_days": {
        "grid": "dense_drift_grid",
        "checker": "check_dimension_drift_resolution",
        "register": "DIMENSION_DRIFT_RESOLUTION",
        "why": "The company's payment terms, on-path for ageing and detection (D28).",
    },
    "organ_failure_window_drift_days": {
        "grid": "book_memory_grid",
        "checker": "check_own_drift_resolution",
        "register": "DIMENSION_DRIFT_RESOLUTION",
        "why": "The company's memory of observed failures, off-path (D29).",
    },
}


def counterfactual_knobs() -> Tuple[str, ...]:
    """THE ROUTE'S SUBJECT, DERIVED FROM SOURCE (atom D31): every counterfactual
    COMPANY knob this harness can build, off the signatures of `score_triad`
    and `build_scenario` rather than a hand-typed list.

    A hand-typed list is the defect the route exists to stop -- the knob nobody
    thought of is exactly the one whose sweep is still the register's own
    claims.
    """
    module_src = inspect.getsource(sys.modules[__name__])
    tree = ast.parse(module_src)
    out: set = set()
    for fn in ("score_triad", "build_scenario"):
        node = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == fn)
        args = node.args
        for a in list(args.args) + list(args.kwonlyargs):
            if a.arg.endswith("_drift_days"):
                out.add(a.arg)
    return tuple(sorted(out))


def check_counterfactual_knob_route() -> List[str]:
    """Put the ROUTE on trial (atom D31). Returns violations; empty = every
    counterfactual knob in this harness is swept on a grid it did not choose and
    its readings reach the ONE shared saturation rule.

      * a knob with no route entry RAISES rather than returning a violation --
        the fallback IS the defect (the D29 rule, one level up);
      * a route naming a grid function that can reach a register is the D28/D29
        defect arriving by declaration;
      * a route naming a checker that does not CALL
        `_check_saturation_and_collapse` is the pre-D31 state of this very
        register: a rule that exists for two of three sweeps.
    """
    module = sys.modules[__name__]
    violations: List[str] = []
    knobs = counterfactual_knobs()
    missing = [k for k in knobs if k not in COUNTERFACTUAL_KNOB_ROUTE]
    if missing:
        raise AssertionError(
            f"counterfactual knob(s) {missing} have no entry in "
            "COUNTERFACTUAL_KNOB_ROUTE -- a knob swept on the register's own "
            "declarations is the atom D28/D29/D31 defect, so this raises "
            "rather than measuring a band exactly where the band answered"
        )
    for knob, row in sorted(COUNTERFACTUAL_KNOB_ROUTE.items()):
        if knob not in knobs:
            violations.append(
                f"{knob}: routed but is not a counterfactual knob of "
                "`score_triad` or `build_scenario` -- a route entry outliving "
                "its knob misleads worse than none"
            )
            continue
        grid_fn = getattr(module, str(row["grid"]), None)
        checker = getattr(module, str(row["checker"]), None)
        if grid_fn is None or checker is None:
            violations.append(
                f"{knob}: names grid `{row['grid']}` / checker "
                f"`{row['checker']}` and this module has no such function"
            )
            continue
        reached = sorted(_names_in(grid_fn) & _register_names())
        if reached:
            violations.append(
                f"{knob}: its grid `{row['grid']}` reads {reached} -- a grid "
                "derived from the register can only ask it what it already "
                "answered"
            )
        if not _reaches(checker, "_check_saturation_and_collapse"):
            violations.append(
                f"{knob}: its checker `{row['checker']}` never calls "
                "`_check_saturation_and_collapse` -- naming the shared rule is "
                "not running it, and a saturation rule that exists for two of "
                "three sweeps is how `ORGAN_QUERY_GRID` kept sixteen collapses "
                "(atom D31)"
            )
    return violations


def _names_in(fn: Callable) -> set:
    """Every NAME and attribute reachable in a function's own source, minus its
    docstring -- the AST test D28 earned, factored so the route can run it on
    functions it was handed rather than on ones a test hard-coded."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    body = tree.body[0]
    if ast.get_docstring(body):
        body.body.pop(0)
    return ({n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)})


def _reaches(fn: Callable, target: str, depth: int = 4) -> bool:
    """Whether `fn` reaches `target` through this module's own helpers.

    TRANSITIVE ON PURPOSE (atom D31). The two older checkers reach the shared
    saturation rule through `_check_on_path_entry` / `_check_own_band`, so a
    one-level name check would have called them defective and taught the next
    reader to weaken the rule rather than route through it. What must not pass
    is a checker that reaches it through NOTHING.
    """
    module = sys.modules[__name__]
    seen: set = set()
    frontier = [fn]
    for _ in range(depth):
        names: set = set()
        for f in frontier:
            names |= _names_in(f)
        if target in names:
            return True
        frontier = []
        for n in sorted(names - seen):
            seen.add(n)
            nxt = getattr(module, n, None)
            if callable(nxt) and getattr(nxt, "__module__", None) == __name__:
                frontier.append(nxt)
        if not frontier:
            break
    return False


def _register_names() -> set:
    """The module's own resolution REGISTERS, by name, derived rather than
    typed -- a new register must not be able to hide from the grid check by
    being new."""
    return {r["register"] for r in COUNTERFACTUAL_KNOB_ROUTE.values()} | {
        "ORGAN_QUERY_GRID", "DIMENSION_DRIFT_RESOLUTION"}


# WHICH CONSTANT REACHES THE FLOOR PREDICTOR THROUGH WHICH KEYWORD -- the
# `_SPAN_PREDICTOR_KNOBS` shape one band over (atom D30/D31). The census
# answers "does this constant bound the reading" by MOVING it, never by reading
# a declaration, and a constant with no knob here cannot be declared to own the
# edge.
_RECON_FLOOR_KNOBS: Dict[str, str] = {
    "PAYMENT_TERMS_DAYS": "terms_days",
    "DEFAULT_RECONCILIATION_GRACE_DAYS": "grace_days",
}


def _predict_declared_edge(constants: Tuple[str, ...]) -> Dict[str, object]:
    """The lower edge predicted from the constants THE ENTRY NAMES, plus the
    one-day perturbation of each (atom D31).

    Returns `predicted_saturates_below` (None where a named constant reaches no
    knob of the predictor, or where a knob is unnamed -- an edge attributed to
    a SUBSET of the constants that set it is the D30 defect), and
    `edge_constants_move` -- which of the named constants actually move the
    prediction. Both are measurements; neither reads the register.
    """
    if not constants:
        return {"predicted_saturates_below": None, "edge_constants_move": {}}
    unknown = [c for c in constants if c not in _RECON_FLOOR_KNOBS]
    missing = [c for c in _RECON_FLOOR_KNOBS if c not in constants]
    if unknown or missing:
        return {
            "predicted_saturates_below": None,
            "edge_constants_move": {},
            "edge_constants_unknown": tuple(unknown),
            "edge_constants_missing": tuple(missing),
        }
    base = predict_recon_floor_from_constants()
    moves = {
        c: predict_recon_floor_from_constants(
            **{_RECON_FLOOR_KNOBS[c]: _current_floor_constant(c) + 1}) != base
        for c in constants
    }
    return {"predicted_saturates_below": base, "edge_constants_move": moves}


def _current_floor_constant(name: str) -> int:
    """The shipped value of a floor constant, read off the module rather than
    re-typed beside the perturbation."""
    return int(globals()[name])


_RECON_RESOLUTION_SCORES: Dict[tuple, tuple] = {}


def measure_organ_query_grid_saturation(
    *,
    n_customers: int = 300,
    seeds: Sequence[int] = RESOLUTION_SEEDS,
    register: Optional[Dict[str, Dict[str, object]]] = None,
    runner: Optional[Callable[[int, int], tuple]] = None,
) -> Dict[str, Dict[str, object]]:
    """SWEEP THE RECONCILIATION KNOB ON THE BOOK'S GRID (atom D31) and produce
    the same row shape `_check_saturation_and_collapse` reads for the other two
    knobs: collapsed runs, both saturation edges, and the undefined readings.

    Returns {reading: {...}} for every `ORGAN_QUERY_GRID` entry.

    COST, MEASURED RATHER THAN WAVED AT (the D23 precedent). The grid is 109
    integers on this scenario (-20..+88) against the 8 points the register's own
    declarations produced, so this is 109 x 3 scorings of a 300-account book:
    ~100s wall-clock, cached per (n, seed, drift) for the process. It buys the
    only measurement that can find a collapse nobody declared, which is the
    whole of atom D31 -- and the sixteen it found on its first run are the
    number to weigh a shorter grid against.
    """
    register = ORGAN_QUERY_GRID if register is None else register
    route = COUNTERFACTUAL_KNOB_ROUTE.get(RECON_DRIFT_KNOB)
    if route is None:
        raise AssertionError(
            f"`{RECON_DRIFT_KNOB}` has no entry in COUNTERFACTUAL_KNOB_ROUTE "
            "-- falling back to the register's own declarations is the atom "
            "D31 defect itself, so this raises"
        )
    grid_fn = globals()[str(route["grid"])]
    if runner is None:
        def runner(seed: int, k: int) -> tuple:
            key = (n_customers, seed, k)
            if key not in _RECON_RESOLUTION_SCORES:
                recs, cons, _ledger, as_of = build_scenario(
                    n_customers, seed=seed)
                _RECON_RESOLUTION_SCORES[key] = (
                    recs,
                    score_triad(recs, cons, as_of,
                                organ_reconciliation_drift_days=k),
                    as_of,
                )
            return _RECON_RESOLUTION_SCORES[key]

    # THE UNDRIFTED BOOK FIRST: the grid is a property of the book it will be
    # swept over, and nothing else knows where the issue dates are.
    base_scored = {(s, 0): runner(s, 0) for s in seeds}
    grid: set = set()
    for s in seeds:
        grid |= set(grid_fn(base_scored[(s, 0)][0], base_scored[(s, 0)][2]))
    # The DECLARATIONS are still unioned in -- a declaration outside the grid
    # must be scored rather than skipped into a free pass (atom D28's rule).
    for entry in register.values():
        for k in (tuple(entry.get("invisible_drifts") or ())
                  + tuple(entry.get("visible_drifts") or ())):
            grid.add(int(k))
        for pair in (tuple(entry.get("collapsed_pairs") or ())
                     + tuple(entry.get("distinct_pairs") or ())):
            grid.update(int(k) for k in pair)
    # `collapsed_runs` and `undefined_drifts` are deliberately NOT unioned in:
    # they are what this sweep is FOR, and a grid that adopted them would put
    # the answer back into the question -- the register choosing where it gets
    # asked, one field later. Both siblings union only the older declarations
    # for the same reason. A run outside the book's grid therefore fails as
    # unconfirmable rather than passing on a point it supplied itself.
    grid.add(0)
    drifts = sorted(grid)
    scored = dict(base_scored)
    scored.update({(s, k): runner(s, k)
                   for s in seeds for k in drifts if k != 0})

    def _read(entry: Dict[str, object], result: Dict[str, object]) -> object:
        dim = result[str(entry["feeds"])]
        key = entry["headline_key"]
        return dim.gap if key is None else dim.components[str(key)]

    out: Dict[str, Dict[str, object]] = {}
    for name in sorted(register):
        entry = register[name]
        by_seed: Dict[int, Dict[str, object]] = {}
        for s in seeds:
            base = _read(entry, scored[(s, 0)][1])
            by_drift = {k: _read(entry, scored[(s, k)][1])
                        for k in drifts if k != 0}
            by_seed[s] = {"baseline": base, "by_drift": by_drift}
        runs = _measure_collapse_runs(by_seed, drifts, seeds)
        wit_key = entry.get("undefined_witness_key")
        witness: Dict[int, tuple] = {}
        if wit_key:
            dim_name, comp = str(wit_key[0]), str(wit_key[1])
            # (is_the_reading_absent, the population it was read over) per seed:
            # the pair is the witness, because an absent reading over a
            # NON-empty population is an instrument that stopped for some other
            # reason -- which is the thing worth failing on.
            witness = {
                k: tuple(
                    ((by_seed[s]["by_drift"][k] if k != 0
                      else by_seed[s]["baseline"]) is None,
                     scored[(s, k)][1][dim_name].components.get(comp))
                    for s in seeds)
                for k in runs["undefined_readings"]
            }
        out[name] = {
            "knob": RECON_DRIFT_KNOB,
            "seeds": tuple(seeds),
            "drifts": tuple(drifts),
            "by_seed": by_seed,
            "baseline": by_seed[seeds[0]]["baseline"],
            "undefined_witness": witness,
            # THE CONSTANT-SIDE SECOND OPINION on the edge this book's calendar
            # sets, built from the constants the ENTRY names -- never from a
            # fixed call, which would make `edge_constants` a label rather than
            # a claim (a declaration that cannot be wrong is not a control).
            # The prediction is None where a named constant reaches no knob of
            # the predictor, and the perturbation below answers "does this
            # constant move the edge" by MOVING IT (the D30 census shape).
            **_predict_declared_edge(tuple(entry.get("edge_constants") or ())),
            **runs,
        }
    return out


def check_organ_query_grid_saturation(
    measured: Dict[str, Dict[str, object]],
    register: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """Put the reconciliation register's COLLAPSE and SATURATION declarations on
    trial against the book-derived sweep (atom D31).

    The body is the SHARED rule -- the same `_check_saturation_and_collapse`
    both other knobs run -- plus the one thing only this edge can carry: a
    saturation edge whose owning CONSTANTS are declared must be reproduced by
    `predict_recon_floor_from_constants`, which reads the constants and never
    the sweep. An edge nobody can predict from outside the measurement is a
    debt; this one is arithmetic, and saying so is what makes it a bound.
    """
    register = ORGAN_QUERY_GRID if register is None else register
    violations: List[str] = []
    for name in sorted(measured):
        row, entry = measured[name], register[name]
        violations.extend(
            _check_saturation_and_collapse(name, row, entry, ""))
        consts = tuple(entry.get("edge_constants") or ())
        if not consts:
            continue
        # PREDICTED FROM THE CHECKED ENTRY'S OWN CONSTANTS, not from the row:
        # the measurement carries the shipped register's prediction, so reading
        # it here would make `edge_constants` unfalsifiable -- a declaration
        # that cannot be wrong is not a control (R15, caught on this Hour's
        # own first draft).
        pred = _predict_declared_edge(consts)
        unknown = tuple(pred.get("edge_constants_unknown") or ())
        missing = tuple(pred.get("edge_constants_missing") or ())
        if unknown:
            violations.append(
                f"{name}: declares its lower edge owned by {list(unknown)}, "
                "which reach no knob of `predict_recon_floor_from_constants` "
                "-- an attribution nobody can perturb is a label, not a claim"
            )
        if missing:
            violations.append(
                f"{name}: names some of the constants that set its lower edge "
                f"and not {list(missing)} -- an edge attributed to a SUBSET of "
                "its owners reads as though the rest were inert (the D30 class)"
            )
        inert = sorted(c for c, moved in
                       (pred.get("edge_constants_move") or {}).items()
                       if not moved)
        if inert:
            violations.append(
                f"{name}: declares {inert} to own its lower edge and moving "
                "them one day moves the prediction by nothing -- a constant "
                "that cannot move the edge does not set it"
            )
        predicted = pred.get("predicted_saturates_below")
        measured_edge = row.get("saturates_below")
        if predicted != measured_edge:
            violations.append(
                f"{name}: declares its lower edge owned by {list(consts)} and "
                f"the constants predict {predicted!r} while the sweep measured "
                f"{measured_edge!r} -- an attribution to a harness constant is "
                "worth having only while the arithmetic reproduces the reading"
            )
    return violations


def organ_query_grid_saturation_caveat(
    measured: Optional[Dict[str, Dict[str, object]]] = None,
) -> str:
    """The saturation caveat that travels WITH the latency and detection
    numbers, interpolated from the register (atom D31, the D22/D25 rule: a
    caveat nobody re-derives decays into a claim)."""
    src = (ORGAN_QUERY_GRID if measured is None
           else {k: dict(ORGAN_QUERY_GRID[k], **{
               "saturates_below": v.get("saturates_below"),
               "saturates_above": v.get("saturates_above"),
           }) for k, v in measured.items()})
    def _d(v: object) -> str:
        # A missing edge prints as UNMEASURED rather than crashing or reading
        # like a zero: an edge nobody measured is not an edge at the origin.
        return "UNMEASURED" if v is None else f"{int(v):+d}"

    date_lo = _d(src["recon_lag_days"]["saturates_below"])
    set_lo = _d(src["flagged_via_reconciliation"]["saturates_below"])
    set_hi = _d(src["flagged_via_reconciliation"]["saturates_above"])
    return (
        "SATURATION (atom D31, measured on a grid derived from the BOOK, "
        f"n=300, seeds {list(RESOLUTION_SEEDS)}): resolution is not the whole "
        "real line. The first-knowledge DATE reading resolves the company day "
        f"for day down to {date_lo}d and no further -- a detector that "
        "would fire before the invoice was ISSUED is read at the issue date, "
        "which is `PAYMENT_TERMS_DAYS + DEFAULT_RECONCILIATION_GRACE_DAYS` and "
        "a bound on what any supplier can know. The SET reading behind the "
        f"published detection gap saturates BELOW {set_lo}d, where every "
        "company has already flagged every invoice and the gap is the no-skill "
        f"0.5, and ABOVE {set_hi}d, where nothing further is detected "
        "before `as_of`. Between them it is quantised, not continuous: "
        "movement in these headlines is not readable as days of company error "
        "outside the declared runs. R12: a diagnostic, never a target."
    )


def latency_terms_resolution_caveat() -> str:
    """The TERMS-knob limit that travels with the latency number (atom D32).

    THE COVERAGE HOLE Expert Hour #14 found. `DIMENSION_DRIFT_RESOLUTION`
    declares `detection_latency` `in_causal_path: True` for
    `organ_terms_drift_days` and measures its band -- and not one word of that
    reached the published figure, whose two stamped caveats are both about the
    RECONCILIATION detector. Measured on this book the two knobs are
    indistinguishable in this dimension (a supplier holding terms k days long
    and one whose detector fires k days late publish a bit-identical latency
    figure on every seed), so a reader given only the recon caveat attributes
    the whole reading to a detector fault it may have no part in.

    Interpolated from the register on every call, never typed once -- the
    D19/D20/D22/D23/D25 rule.
    """
    e = DIMENSION_DRIFT_RESOLUTION["detection_latency"]
    lo = e.get("saturates_below")
    return (
        "AND THE SAME READING MOVES UNDER A SECOND COMPANY ERROR (atom D32). "
        f"`{e['drift']}` -- the supplier holding the wrong payment terms -- is "
        "ON this dimension's causal path, and on the offline scenario it moves "
        "this headline BIT-IDENTICALLY to the reconciliation drift above "
        "(seeds " + "/".join(str(s) for s in RESOLUTION_SEEDS) + "). This "
        "number therefore does not attribute: a movement in it is days of "
        "detector error OR days of terms error and the figure cannot say "
        f"which. It saturates below {lo:+d}d, where every debt is dated before "
        "the earliest candidate the detector has. Residual owned by "
        f"{e.get('saturation_atom')}. R12: a diagnostic, never a target."
    )


# ---------------------------------------------------------------------------
# PUBLISHED_FIGURE_CAVEAT_CONTRACT -- does the caveat a published figure
# carries describe THAT figure, under every knob that moves it?
# (atom D32, H27 Expert Hour #14, 2026-08-11)
#
# THE CLASS, ONE LAYER ABOVE `COUNTERFACTUAL_KNOB_ROUTE`. D31's route proved
# every counterfactual knob is SWEPT on a book-derived grid and reaches the one
# saturation rule. What no control asked is whether the resolution those sweeps
# measure ever reaches the READER of the number -- and asking it found two
# failures at once, in the same dimension:
#
#   * WRONG SUBJECT. `ORGAN_QUERY_GRID["recon_lag_days"]` names
#     `mean_lag_days_without_dd_channel` in `headline_key` and resolves it day
#     for day. `organ_query_grid_caveat` reported that 1.0 as what "is
#     published" -- onto `detection_latency`, whose published figure is
#     `mean_lag_days` and moves 0.32/0.36/0.27 per drift day on seeds 7/11/23.
#     A register may absolutely measure a cleaner sub-reading; what it may not
#     do is let that reading's number be stamped on a different one.
#   * MISSING KNOB. `detection_latency` moves under the TERMS knob too --
#     declared in `DIMENSION_DRIFT_RESOLUTION`, measured, and bit-identical to
#     the recon knob -- and carried no terms caveat at all.
#
# So the keyset is DERIVED both ways: `published_dimensions` x
# `counterfactual_knobs`, and which cells MOVE is MEASURED, never declared. A
# cell that moves and carries no caveat is a violation; a cell whose caveat
# states a step is checked against the PUBLISHED figure's own measured step.
# Nine of the fifteen cells are inert and must be measured inert -- an
# unmeasured cell reads exactly like an inert one, which is the fail-open this
# instrument has now produced in six registers.
# ---------------------------------------------------------------------------

PUBLISHED_FIGURE_CAVEAT_CONTRACT: Dict[str, Dict[str, object]] = {
    "detection": {
        "organ_terms_drift_days": {
            "moves": True,
            "caveat_component": "drift_resolution_caveat",
            "number_source": ("DIMENSION_DRIFT_RESOLUTION", "detection"),
        },
        "organ_reconciliation_drift_days": {
            "moves": True,
            "caveat_component": "recon_saturation_caveat",
            # `headline_key: None` on that entry means "the dimension's own
            # gap", and `feeds` names this dimension -- so the edges this
            # sentence states were swept on the figure it rides on.
            "number_source": ("ORGAN_QUERY_GRID", "flagged_via_reconciliation"),
        },
        "organ_failure_window_drift_days": {"moves": False},
    },
    "detection_latency": {
        # THE TWO CELLS ATOM D32 FIXED. The recon cell carried a caveat whose
        # number belonged to a sub-reading; the terms cell carried nothing.
        "organ_terms_drift_days": {
            "moves": True,
            "caveat_component": "terms_resolution_caveat",
            "number_source": ("DIMENSION_DRIFT_RESOLUTION", "detection_latency"),
        },
        "organ_reconciliation_drift_days": {
            "moves": True,
            "caveat_component": "organ_query_grid_caveat",
            # THE SUB-READING, DECLARED AS ONE (atom D32): this entry's
            # `headline_key` is `mean_lag_days_without_dd_channel`, not this
            # dimension's published figure, so the cell owes a number measured
            # on the PUBLISHED headline as well -- which is what
            # `published_step_component` is.
            "number_source": ("ORGAN_QUERY_GRID", "recon_lag_days"),
            "published_step_component": "published_headline_step_days",
        },
        "organ_failure_window_drift_days": {"moves": False},
    },
    "belief": {
        "organ_terms_drift_days": {"moves": False},
        "organ_reconciliation_drift_days": {"moves": False},
        "organ_failure_window_drift_days": {
            "moves": True,
            "caveat_component": "belief_resolution_caveat",
            # THE CELL EXPERT HOUR #15 FOUND (atom D33). The caveat's number was
            # the BOOK's -- `measure_belief_window_resolution`, which is not
            # keyed by dimension at all and cannot be, so the cell owes a
            # per-figure floor measured through this dimension's own scorer.
            "number_source": ("BOOK", "measure_belief_window_resolution"),
            "published_floor_component": "measured_resolution_floor_days",
        },
    },
    "belief_population_mix": {
        "organ_terms_drift_days": {"moves": False},
        "organ_reconciliation_drift_days": {"moves": False},
        "organ_failure_window_drift_days": {
            "moves": True,
            "caveat_component": "belief_resolution_caveat",
            # THE SAME BOOK NUMBER, ON A FIGURE FOUR DAYS BLUNTER (atom D33):
            # this is the cell where sharing one sentence cost the reader five
            # days on seed 11.
            "number_source": ("BOOK", "measure_belief_window_resolution"),
            "published_floor_component": "measured_resolution_floor_days",
        },
    },
    "ageing": {
        "organ_terms_drift_days": {
            "moves": True,
            "caveat_component": "drift_resolution_caveat",
            "number_source": ("DIMENSION_DRIFT_RESOLUTION", "ageing"),
        },
        # MEASURED INERT, not assumed. The reconciliation detector sets which
        # invoices the company CHASES; the ageing report is built from the
        # ledger's own dating, so no detector drift reaches it.
        "organ_reconciliation_drift_days": {"moves": False},
        "organ_failure_window_drift_days": {"moves": False},
    },
}

# WHOSE NUMBER IS IT? (atom D33, Expert Hour #15.) A moving cell's caveat puts a
# number in the reader's hands, and D32 checked exactly one of them -- the only
# day-linear cell -- against the published figure. The other six state BANDS and
# EDGES, and the two belief cells turned out to be stating the BOOK's bound as
# the figure's own resolution. So every moving cell must now declare WHERE its
# number comes from, and the subject of that source is CHECKED:
#
#   * `DIMENSION_DRIFT_RESOLUTION` -- keyed BY dimension, and the key must be
#     this dimension. A cell pointing at a sibling's entry is the D32 wrong-
#     subject defect and now fails by name.
#   * `ORGAN_QUERY_GRID` -- keyed by READING. The entry must `feed` this
#     dimension, and if its `headline_key` names a sub-reading rather than the
#     dimension's own gap, the cell owes a number measured on the PUBLISHED
#     figure (`published_step_component`).
#   * `BOOK` -- a population-side predictor, which by construction knows nothing
#     about which figure is reading it. Never sufficient on its own: the cell
#     owes a `published_floor_component`, measured per dimension through its own
#     shipped scorer.
_CAVEAT_NUMBER_SOURCE_KINDS = ("DIMENSION_DRIFT_RESOLUTION", "ORGAN_QUERY_GRID",
                               "BOOK")

# Both published gaps are rounded before they are compared, so a difference
# this small is the rounding and not a reading. It is FAR below the defect this
# control exists to catch -- atom D32's mis-stamped step was 1.0 against a
# measured 0.32, a gap of 0.68 -- so the slack cannot swallow the class.
_ROUNDING_SLACK = 1e-5

# The drifts each knob is probed at. Small and either side of zero: this
# register asks REACH ("does the reader owe a caveat here at all"), not band --
# the bands are `DIMENSION_DRIFT_RESOLUTION`'s and `ORGAN_QUERY_GRID`'s, swept
# on book-derived grids. A cell declared inert must be inert at EVERY probe.
CAVEAT_COVERAGE_PROBES: Dict[str, Tuple[int, ...]] = {
    "organ_terms_drift_days": (-1, 1, 5),
    "organ_reconciliation_drift_days": (-1, 1, 5),
    # The memory knob's readable band is far from zero on this book (atom
    # D29/D30: everything from -308 up is one number), so +-1 would probe an
    # inert region and hand every cell a free pass.
    "organ_failure_window_drift_days": (-370, -350, -310),
}


def measure_published_figure_caveat_coverage(
    *,
    n_customers: int = 300,
    seeds: Tuple[int, ...] = RESOLUTION_SEEDS,
    probes: Optional[Dict[str, Tuple[int, ...]]] = None,
) -> Dict[str, Dict[str, object]]:
    """MEASURE which knobs move which PUBLISHED figures, and how far (atom
    D32). Returns {dimension: {knob: {"moves", "moved_at", "step_days",
    "probe_bit"}}}.

    `step_days` is the published headline's OWN movement per day of drift,
    taken at +-1 and only where the two agree to a day-linear reading -- it is
    what the caveat's number is checked against. `probe_bit` is the vacuity
    guard on the knob itself: a knob that has silently stopped drifting the
    company would otherwise certify every `moves: False` cell in its column.
    """
    probes = CAVEAT_COVERAGE_PROBES if probes is None else probes
    dims: Optional[List[str]] = None
    base: Dict[int, Dict[str, object]] = {}
    out: Dict[str, Dict[str, object]] = {}

    def _score(seed: int, knob: str, k: int) -> Dict[str, object]:
        memory = k if knob == "organ_failure_window_drift_days" else 0
        records, consumer, _book, as_of = build_scenario(
            n_customers, seed=seed, organ_failure_window_drift_days=memory)
        kwargs = {n: (k if n == knob else 0)
                  for n in ("organ_reconciliation_drift_days",
                            "organ_terms_drift_days")}
        return score_triad(records, consumer, as_of, **kwargs)

    for seed in seeds:
        records, consumer, _book, as_of = build_scenario(n_customers, seed=seed)
        base[seed] = score_triad(records, consumer, as_of)
        if dims is None:
            dims = published_dimensions(base[seed])
    assert dims is not None
    # WHAT A CONSUMER ACTUALLY RENDERS, per seed -- the subject of the caveat
    # half of this control. It is kept per seed because the published step is a
    # property of the BOOK (0.32/0.36/0.27 across these three), so a single
    # rendering checked against every seed's measurement would fail on two of
    # them for the right reason and the wrong one.
    for dim in dims:
        out.setdefault(dim, {})["_rendered"] = {
            seed: dict(base[seed][dim].components) for seed in seeds
        }

    for knob in sorted(probes):
        readings = {(seed, k): _score(seed, knob, k)
                    for seed in seeds for k in probes[knob]}
        for dim in dims:
            row = out.setdefault(dim, {})
            moved_at = sorted({
                k for (seed, k), res in readings.items()
                if res[dim].gap != base[seed][dim].gap
            })
            step = None
            if -1 in probes[knob] and 1 in probes[knob]:
                ups = [readings[(s, 1)][dim].gap - base[s][dim].gap
                       for s in seeds]
                downs = [base[s][dim].gap - readings[(s, -1)][dim].gap
                         for s in seeds]
                # DAY-LINEAR ONLY. A step is meaningful only where the reading
                # moves the same amount either way; where it does not (the
                # ageing headline), None is the honest answer and the caveat
                # owes no step. The tolerance is `_ROUNDING_SLACK` because
                # both gaps are published rounded, not because the reading is
                # approximate.
                if all(isinstance(u, float) for u in ups) and \
                        all(abs(u - d) < _ROUNDING_SLACK
                            for u, d in zip(ups, downs)):
                    step = {s: u for s, u in zip(seeds, ups)}
            row[knob] = {
                "moves": bool(moved_at),
                "moved_at": tuple(moved_at),
                "step_days": step,
                "probes": tuple(probes[knob]),
            }
        # The knob moved SOMETHING somewhere, or every inert cell below it is
        # certified by a probe that does nothing.
        probe_bit = any(out[d][knob]["moves"] for d in dims)
        for dim in dims:
            out[dim][knob]["probe_bit"] = probe_bit
    return out


def _check_caveat_number_subject(dim: str, knob: str,
                                 entry: Dict[str, object]) -> List[str]:
    """WHOSE NUMBER THE CAVEAT STATES, checked against the source it declares
    (atom D33).

    This is D32's finding made general. D32 caught one wrong subject with one
    step check; the rule is that a caveat number's SOURCE must be about the
    figure it is stamped on, and where the source cannot be (a sub-reading, or
    the book), the cell owes a number measured on the published figure itself.
    """
    out: List[str] = []
    src = entry.get("number_source")
    if not (isinstance(src, (tuple, list)) and len(src) == 2
            and src[0] in _CAVEAT_NUMBER_SOURCE_KINDS):
        raise AssertionError(
            f"{dim}/{knob}: this knob MOVES the published figure and the entry "
            f"declares no usable `number_source` (got {src!r}, want one of "
            f"{_CAVEAT_NUMBER_SOURCE_KINDS}) -- a caveat number whose subject "
            "nobody states is how the belief figures published the BOOK's bound "
            "as their own resolution for six Hours (atom D33)"
        )
    kind, key = src[0], src[1]
    if kind == "DIMENSION_DRIFT_RESOLUTION":
        if key != dim:
            out.append(
                f"{dim}/{knob}: its caveat's number comes from "
                f"DIMENSION_DRIFT_RESOLUTION[{key!r}] -- a register keyed BY "
                f"dimension, pointed at a different one. A band measured on "
                "`{key}`'s figure is not this figure's (atom D32's wrong "
                "subject, generalised)"
            )
        elif key not in DIMENSION_DRIFT_RESOLUTION:
            out.append(
                f"{dim}/{knob}: names DIMENSION_DRIFT_RESOLUTION[{key!r}], "
                "which does not exist -- a caveat sourced from nothing"
            )
    elif kind == "ORGAN_QUERY_GRID":
        entry_src = ORGAN_QUERY_GRID.get(key)
        if entry_src is None:
            out.append(
                f"{dim}/{knob}: names ORGAN_QUERY_GRID[{key!r}], which does "
                "not exist -- a caveat sourced from nothing"
            )
        else:
            if entry_src.get("feeds") != dim:
                out.append(
                    f"{dim}/{knob}: its caveat's number comes from "
                    f"ORGAN_QUERY_GRID[{key!r}], which feeds "
                    f"`{entry_src.get('feeds')}` -- another dimension's reading"
                )
            if (entry_src.get("headline_key") is not None
                    and not entry.get("published_step_component")):
                out.append(
                    f"{dim}/{knob}: its caveat's number is measured on the "
                    f"SUB-READING `{entry_src.get('headline_key')}` and the "
                    "cell declares no `published_step_component` -- publishing "
                    "a sub-reading's resolution as the headline's is atom D32's "
                    "finding, restated"
                )
    elif kind == "BOOK":
        if not entry.get("published_floor_component"):
            out.append(
                f"{dim}/{knob}: its caveat's number comes from the BOOK "
                f"({key}), a population-side predictor that cannot know which "
                "figure is reading it, and the cell declares no "
                "`published_floor_component` -- so a bound on what ANY figure "
                "here could resolve stands where this figure's own resolution "
                "goes (atom D33)"
            )
    return out


def _check_rendered_floor(dim: str, knob: str, floor_key: str,
                          by_seed: Dict[int, Dict[str, object]],
                          floors: Optional[Dict[str, Dict[str, object]]],
                          ) -> List[str]:
    """The per-figure floor a BOOK-sourced cell owes: RENDERED by a real
    `score_triad`, equal to what the sweep measures for THIS dimension, and
    actually present in the caveat sentence the reader meets (atom D33).

    `floors` is the independent side -- `measure_published_resolution_floor`,
    which re-scores the book through each dimension's own shipped scorer and
    never reads this register. Absent, the coverage is UNVERIFIED and says so:
    an unavailable check is a failed check (R15 fail-silent).
    """
    out: List[str] = []
    for seed, comps in sorted(by_seed.items()):
        if floor_key not in comps:
            out.append(
                f"{dim}/{knob}: declares a per-figure resolution floor and a "
                f"real `score_triad` publishes no `{floor_key}` on `{dim}` "
                f"(seed {seed}) -- the reader then has only the book's bound, "
                "which is not this figure's resolution (atom D33)"
            )
            continue
        got = comps[floor_key]
        if got is None:
            out.append(
                f"{dim}/{knob}: publishes `{floor_key}`=None (seed {seed}) -- a "
                "figure whose resolution is unmeasured must say so in the "
                "sentence, not hand the reader a blank where a number goes"
            )
            continue
        caveat = comps.get("belief_resolution_caveat")
        # THE PHRASE THE READER CONVERTS, not merely the digits anywhere in the
        # sentence: the caveat also names the SIBLING's floor (as the sibling's),
        # so "the number appears somewhere" would pass on the exact confusion
        # this atom closes.
        claim = f"smaller than {int(got)}d of forgetting"
        if isinstance(caveat, str) and claim not in caveat:
            out.append(
                f"{dim}/{knob}: publishes `{floor_key}`={got} as a component "
                "and the caveat SENTENCE beside it never states it (seed "
                f"{seed}) -- naming a number is not stamping one (Hour #11)"
            )
    if floors is None:
        out.append(
            f"{dim}/{knob}: its per-figure floor was compared against NOTHING "
            "-- `measure_published_resolution_floor` was not supplied, and an "
            "unavailable check is a failed one (R15 fail-silent)"
        )
        return out
    row = floors.get(dim)
    if row is None:
        out.append(
            f"{dim}/{knob}: declares a per-figure floor and the floor sweep "
            f"never measured `{dim}` -- an unmeasured floor reads exactly like "
            "a verified one"
        )
        return out
    for seed, comps in sorted(by_seed.items()):
        got = comps.get(floor_key)
        if got is None:
            continue
        if int(got) != int(row["floor_days"]):
            out.append(
                f"{dim}/{knob}: publishes a resolution floor of {got}d and the "
                f"sweep measures {row['floor_days']}d for `{dim}` (per seed "
                f"{row['per_seed_floor_days']}) -- a number that is not this "
                "figure's resolution is atom D33's finding"
            )
            break
    return out


def check_published_figure_caveat_coverage(
    measured: Dict[str, Dict[str, object]],
    register: Optional[Dict[str, Dict[str, object]]] = None,
    rendered: Optional[Dict[str, Dict[str, object]]] = None,
    floors: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """Put `PUBLISHED_FIGURE_CAVEAT_CONTRACT` on trial against the measurement
    and the RENDERED components, and return the violations (atom D32).

    `rendered` is {dimension: {seed: components}} from a real `score_triad` --
    the artefact the ledger writer, the live wiring and the dashboard actually
    read. It defaults to the one the MEASUREMENT rendered, so the subject is a
    real consumer's view by construction; checking the register against itself
    would be the tautology this instrument has produced five times. The
    parameter exists so a mutation can hand it a rendering with the caveat
    stripped.

    Both keysets RAISE rather than returning a violation, because a cell that
    was never asked reads exactly like a clean one -- which is the whole
    finding.
    """
    register = PUBLISHED_FIGURE_CAVEAT_CONTRACT if register is None else register
    if rendered is None:
        rendered = {d: row.get("_rendered", {}) for d, row in measured.items()}
    knobs = set(counterfactual_knobs())
    missing = sorted(set(measured) - set(register))
    if missing:
        raise AssertionError(
            f"published dimensions with no PUBLISHED_FIGURE_CAVEAT_CONTRACT "
            f"entry: {missing} -- a dimension whose caveat coverage nobody "
            "asks about is exactly how `detection_latency` carried a "
            "sub-reading's resolution for two Hours"
        )
    orphan = sorted(set(register) - set(measured))
    if orphan:
        raise AssertionError(
            f"PUBLISHED_FIGURE_CAVEAT_CONTRACT entries for dimensions nobody "
            f"publishes: {orphan} -- an unreachable entry reads like a clean one"
        )
    for dim in sorted(register):
        unrouted = sorted(knobs - set(register[dim]))
        if unrouted:
            raise AssertionError(
                f"{dim}: no caveat-coverage declaration for knob(s) "
                f"{unrouted} -- an undeclared cell is not an inert one, and "
                "the fallback IS the defect (the D29/D31 rule, one layer up)"
            )

    violations: List[str] = []
    for dim in sorted(measured):
        for knob in sorted(knobs):
            row, entry = measured[dim][knob], register[dim][knob]
            if not row["probe_bit"]:
                violations.append(
                    f"{dim}/{knob}: the probe moved NOTHING on any published "
                    "dimension -- an inert counterfactual company certifies "
                    "every `moves: False` in its column for free"
                )
            if bool(row["moves"]) != bool(entry.get("moves")):
                violations.append(
                    f"{dim}/{knob}: declared moves={entry.get('moves')} but "
                    f"MEASURED moves={row['moves']} at {row['moved_at']} "
                    f"(probes {row['probes']})"
                )
                continue
            if not row["moves"]:
                continue
            key = entry.get("caveat_component")
            if not key:
                violations.append(
                    f"{dim}/{knob}: this knob MOVES the published figure at "
                    f"{row['moved_at']} and the entry names no caveat "
                    "component -- a resolution measured by a sweep and never "
                    "stamped on the number is one no reader of the number "
                    "ever meets (atom D32)"
                )
                continue
            by_seed = rendered.get(dim, {})
            unstamped = sorted(s for s, comps in by_seed.items()
                               if str(key) not in comps)
            if unstamped:
                violations.append(
                    f"{dim}/{knob}: names caveat component `{key}` and a real "
                    f"`score_triad` publishes no such key on `{dim}` (seeds "
                    f"{unstamped}) -- a caveat the consumer does not render is "
                    "not stamped"
                )
                continue
            # WHOSE NUMBER IS IN THE SENTENCE (atom D33), before any of the
            # number checks below: a component that renders is not a component
            # about this figure.
            violations.extend(_check_caveat_number_subject(dim, knob, entry))
            floor_key = entry.get("published_floor_component")
            if floor_key is not None:
                violations.extend(_check_rendered_floor(
                    dim, knob, floor_key, by_seed, floors))
            step_key = entry.get("published_step_component")
            if step_key is None:
                continue
            for seed, step in sorted((row["step_days"] or {}).items()):
                published = by_seed.get(seed, {}).get(str(step_key))
                if published is None:
                    violations.append(
                        f"{dim}/{knob}: declares its caveat states a step and "
                        f"publishes no `{step_key}` beside it (seed {seed}) -- "
                        "the number a reader converts a movement with is then "
                        "unfalsifiable"
                    )
                    continue
                if abs(float(published) - float(step)) > _ROUNDING_SLACK:
                    violations.append(
                        f"{dim}/{knob}: publishes step {published} while the "
                        f"PUBLISHED headline measurably moves {step} per drift "
                        f"day (seed {seed}) -- a caveat stating an adjacent "
                        "reading's resolution is atom D32's finding, restated"
                    )
    return violations


DIMENSION_DRIFT_RESOLUTION: Dict[str, Dict[str, object]] = {
    "ageing": {
        "drift": "organ_terms_drift_days",
        "in_causal_path": True,
        # RE-DERIVED 2026-08-10 WHEN D25 LANDED, which is what the debt entry
        # it replaces demanded. On the staggered book nothing is invisible and
        # nothing collapses: the headline moves on every declared drift in
        # both directions, down to the one-day error the flat book could not
        # see eight days of.
        "invisible_drifts": (),
        "visible_drifts": (-8, -1, 1, 12),
        "collapsed_pairs": (),
        "structural": True,
        "debt_atom": None,
        # THE DIFFERENTIAL WITNESS OF ATOM D28. On the dense book-derived grid
        # -- 43 counterfactual companies, one per integer day across a billing
        # cycle either way -- this dimension publishes 43 DISTINCT all-seed
        # readings: no collapsed run anywhere and neither tail saturated. It is
        # what stops the register below from being an "everything is quantised"
        # excuse, and it is the D25 reshape holding up under a grid it did not
        # choose (the sparse grid could only ever confirm the four drifts D25
        # itself named).
        "collapsed_runs": (),
        "saturates_below": None,
        "saturates_above": None,
        "saturation_atom": None,
        "why": (
            "THE ENTRY D25 RE-DERIVED. The headline is BUCKETS of ordinal "
            "displacement, so a dating error is visible only where it carries "
            "an invoice across a 30/60/90 boundary -- which makes what it can "
            "resolve a property of where the BOOK's invoices sit. On the flat "
            "book (every account due on the same three dates) that was three "
            "distances, 30/51/72 days overdue at `as_of`, all arithmetic over "
            "FIRST_DUE_DATE + PERIOD_SPACING_DAYS x N_PERIODS and "
            "AS_OF_BUFFER_DAYS: 1 day of under-ageing moved it while EIGHT "
            "days of over-ageing -- the direction that posts an early dunning "
            "letter -- moved nothing, and a company 1 day out and one 12 days "
            "out published ONE number. D25 spread the book across one billing "
            "cycle (`BILLING_CYCLE_SPREAD_DAYS`, the real-world twin: a "
            "domestic book is billed a cohort a day, not all on one date), so "
            "the ages are contiguous and every boundary is straddled. The four "
            "drifts declared visible here are exactly the four the flat book "
            "could not tell apart, kept as the band so a future flattening "
            "fails BY NAME rather than quietly narrowing the caveat. The flat "
            "book stays reachable as `build_scenario(cycle_spread_days=1)` and "
            "`check_ageing_resolution` measures both. R12: nothing was tuned "
            "-- the reshape moves every published ageing figure on this pair "
            "and not one of them was chosen."
        ),
    },
    "detection": {
        "drift": "organ_terms_drift_days",
        "in_causal_path": True,
        "invisible_drifts": (1,),
        "visible_drifts": (-1,),
        "collapsed_pairs": (),
        "structural": True,
        # RE-POINTED WHEN D25 LANDED. This entry cited D25 while D25 was the
        # ageing dimension's reshape; a debt entry outliving its debt is the
        # rot this register's own mutation suite fires on, so the residual has
        # been re-owned rather than left pointing at a closed atom.
        "debt_atom": "D26_detection_grace_line_has_no_book_beside_it",
        # MEASURED ON THE DENSE BOOK-DERIVED GRID (atom D28, Expert Hour #10,
        # n=300, seeds 7/11/23, every run identical on all three). The sparse
        # register-derived grid touched {-8,-1,0,+1,+12} and reported this
        # dimension as blind to {+1} and collapsing NOWHERE. It collapses in
        # seven places, and BOTH TAILS ARE SATURATED: every supplier holding
        # terms 6 or more days SHORTER than the world publishes ONE figure, as
        # does every supplier 17 or more days LONGER. The -8 the old grid read
        # as MOVED -- as evidence of resolution -- sits inside the saturated
        # tail, indistinguishable from -21.
        "collapsed_runs": (
            (-21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9,
             -8, -7, -6),
            (-4, -3), (0, 1), (6, 7), (9, 10), (11, 12, 13),
            (17, 18, 19, 20, 21),
        ),
        "saturates_below": -6,
        "saturates_above": 17,
        "saturation_atom": "D28_the_detection_gap_is_quantised_by_this_books_placement",
        # AN OWNER PER EDGE (atom D29). Both tails of THIS dimension stop for
        # the one reason -- the book sits nowhere near the grace line -- so
        # both name D28; the field exists because the belief dimensions' two
        # tails stop for two DIFFERENT reasons and one field could name only
        # one of them.
        "saturation_atom_below": "D28_the_detection_gap_is_quantised_by_this_books_placement",
        "saturation_atom_above": "D28_the_detection_gap_is_quantised_by_this_books_placement",
        "why": (
            "SET membership by `as_of`, and it is now the register's ONLY "
            "on-path blindness -- D25 spread the book across the billing "
            "cycle, which fixed the ageing dimension's placement problem and "
            "left this one untouched, because this blindness is the GRACE "
            "LINE and not the bucket grid. A company holding terms one day "
            "LONGER still finds every one of these invoices past grace by "
            "`as_of` (the youngest is AS_OF_BUFFER_DAYS overdue and the grace "
            "window is far shorter), so the flagged set is identical; one day "
            "SHORTER pulls extra invoices over the line and the set moves. "
            "Same shape as the defect D25 closed -- the book has no invoice "
            "sitting BESIDE the boundary this dimension reads -- one boundary "
            "further out, which is why it is owned by its own atom (D26) "
            "rather than closed on sight. A reader must not take the ageing "
            "headline as covering this direction (the D16 rule -- aligned "
            "denominators are still different questions). AND IT SATURATES IN "
            "BOTH TAILS (atom D28): below -6d every invoice in the book is "
            "already past the company's grace line however much shorter its "
            "terms get, so sixteen counterfactual suppliers -- a week short "
            "through three weeks short -- publish ONE figure; above +17d none "
            "of them is, and five more publish another. In between the reading "
            "is quantised rather than continuous (five interior collapses), "
            "because the number of invoices sitting BESIDE the grace line at "
            "any one distance is small. A movement in this headline is "
            "therefore not readable as days of terms error, and a supplier "
            "flagging paying customers as in arrears -- the -6d direction, the "
            "one that posts the dunning letter -- is indistinguishable here "
            "from one three weeks out."
        ),
    },
    "detection_latency": {
        "drift": "organ_terms_drift_days",
        "in_causal_path": True,
        # THE SIGHTED ENTRY. Without one, this register would be a blanket
        # 'everything is quantised' claim and could not fail.
        "invisible_drifts": (),
        "visible_drifts": (-1, 1),
        "collapsed_pairs": (),
        "structural": True,
        "debt_atom": None,
        # ATOM D28: sighted to the day across the whole grid EXCEPT its far
        # negative tail. A supplier dating every debt 19 or more days early
        # flags every invoice at the earliest candidate its detector has, so
        # -19, -20 and -21 are one number. Small, but declared: the entry the
        # register leans on as its sighted witness is exactly the one whose
        # unexamined tail would be worth most to a decaying band.
        "collapsed_runs": ((-21, -20, -19),),
        "saturates_below": -19,
        "saturates_above": None,
        "saturation_atom": "D28_the_detection_gap_is_quantised_by_this_books_placement",
        "saturation_atom_below": "D28_the_detection_gap_is_quantised_by_this_books_placement",
        "why": (
            "The one dimension that resolves this company to the DAY in both "
            "directions, because D23 gave it a DAILY candidate grid rather "
            "than one date per period. It is the evidence that the ageing "
            "blindness above is the population's placement and not something "
            "inherent to reading a company through this wall -- and it is the "
            "entry this register cannot do without: an all-blind register is "
            "an excuse, not a control. Its own tail is declared above: the "
            "day-resolution runs out at -19d, where every debt is dated before "
            "the earliest candidate the detector has."
        ),
    },
    "belief": {
        "drift": "organ_terms_drift_days",
        "in_causal_path": False,
        "invisible_drifts": (),
        "visible_drifts": (),
        "collapsed_pairs": (),
        "structural": True,
        "debt_atom": None,
        "exercised_by": "HEADLINE_DIRECTION_COVERAGE",
        # ITS OWN GRADED KNOB (atom D27, Expert Hour #9). Until this existed,
        # `exercised_by` above was the ENTIRE evidence for this entry -- and an
        # indiscriminate degenerate is the LARGEST error there is, so it
        # established non-inertness and measured no resolution whatever. Both
        # belief dimensions were off-path for the register's single drift, so
        # two of five published dimensions had no measured resolution at all.
        "own_drift": "organ_failure_window_drift_days",
        "own_invisible_drifts": (-308, -100, -1, 1, 500),
        # -370 REPLACED -380 (atom D29). -380 does differ from the baseline,
        # which is all D27's sparse grid could ask -- but it takes the memory
        # to 20 days on a book whose youngest failure is 30 days old, so it
        # counts nothing, exactly like total amnesia. That is PROVED by the
        # population-side predictor rather than merely swept: no event is young
        # enough to survive any window below 30, so every one of those
        # companies is one company here. Differing from the scored company is
        # not resolution; -370 is the first drift the sweep reads apart from
        # both its neighbours.
        "own_visible_drifts": (-370, -350, -320, -310),
        "own_debt_atom": "D27_belief_window_saturates_on_this_book",
        # RE-DERIVED ON THE BOOK-DERIVED MEMORY GRID (atom D29, Expert Hour
        # #11, 66 book points + the declarations, n=300, seeds 7/11/23, every
        # run identical on all three). D28 gave these fields the shared checker
        # and D27's sparse grid supplied the readings, so the entry declared
        # ONE collapse and a bounded band. On a grid the register did not
        # choose there are FIVE, and the low tail saturates too.
        "own_collapsed_runs": (
            (-400, -371), (-358, -357, -356), (-333, -332),
            (-331, -330), (-308, -100, -1, 0, 1, 500),
        ),
        "own_saturates_below": -371,
        "own_saturates_above": -308,
        "own_saturation_atom": "D27_belief_window_saturates_on_this_book",
        # TWO TAILS, TWO CAUSES, TWO OWNERS (atom D29). Below: `as_of` sits
        # AS_OF_BUFFER_DAYS past the last event, so nothing is young enough to
        # survive a short memory. A single `own_saturation_atom` could name
        # only one, and named the one that had been looked at.
        #
        # THE UPPER OWNER MOVED D27 -> D30 (Expert Hour #12). D29 recorded it
        # as "the company's memory outruns the book", which is a restatement:
        # the book stops at 92 days because N_PERIODS is 3 and
        # PERIOD_SPACING_DAYS is 21, and that attributes the HARNESS's own
        # calendar to the company being graded. The arithmetic was even written
        # out in `own_why` two lines down -- and no rule was ever built from
        # it, which is Hour #11's "a lead is not a control" one register field
        # over. `_check_edge_owners_are_censused` is that rule: an edge owner
        # outside SCENARIO_CONSTANT_CENSUS now raises. D27 keeps `own_debt_atom`
        # -- it owns where the SCORED COMPANY sits (308d of headroom), which is
        # a different fact from where the edge is.
        "own_saturation_atom_below": "D29_the_as_of_buffer_floors_the_memory_grid",
        "own_saturation_atom_above": "D30_the_belief_band_is_this_books_length",
        # THIS FIGURE'S OWN RESOLUTION, and the number its caveat may state
        # (atom D33). Measured through this dimension's own shipped scorer at
        # the precision every consumer renders it -- 310d on this book against
        # the BOOK's bound of 310/309/309 on seeds 7/11/23, so the bound is
        # tight here and a day loose on two seeds. `own_bit_equality_...` is the
        # witness for the predicate itself; the two agree on this dimension,
        # which is what makes the sibling's disagreement a reading and not an
        # artefact of the measurement.
        "own_readable_resolution_floor_days": 310,
        "own_bit_equality_floor_days": 310,
        "own_floor_predicate_atom": None,
        "own_why": (
            "UNBOUNDED-BLIND ABOVE, and the shipped company sits 308 days "
            "inside the blind band. The book's oldest observed failure is 92d "
            "old at `as_of` (N_PERIODS x PERIOD_SPACING_DAYS + "
            "AS_OF_BUFFER_DAYS + the cycle spread) while the harness builds "
            "the company with DD_FAILURE_WINDOW_DAYS=400, so no event can EVER "
            "fall out of its memory: every window from 92 days to infinity "
            "publishes a bit-identical figure (measured seeds 7/11/23; +1d, "
            "+500d and -308d all read the baseline exactly). The dimension "
            "therefore cannot distinguish this company from one that never "
            "forgets a failure -- the direction that keeps a recovered "
            "customer in collections -- and the organ's OWN shipped default "
            "(90d) sits just BELOW the edge, publishing a different number "
            "(0.1519 -> 0.1709 at seed 7). The 400 was deliberate and its "
            "reason is still in the constant's comment ('generous on purpose', "
            "to stop the recency window confounding the CHANNEL blind spot "
            "this scenario measures) -- what was never measured or declared is "
            "that the same choice costs the dimension all resolution on the "
            "only company parameter it reads. A design note stood in for a "
            "measurement, which is Hour #5's lesson. Same shape as D25 and "
            "D26: the book has no event sitting BESIDE the boundary this "
            "dimension reads. AND IT SATURATES BELOW TOO (atom D29): the "
            "book's YOUNGEST observed failure is 30d old -- AS_OF_BUFFER_DAYS, "
            "a second harness constant chosen to remove a confounder -- so "
            "every company memory of 29 days or less counts nothing at all and "
            "publishes ONE figure. A supplier that forgets a failed collection "
            "after three weeks and one that never remembers it are the same "
            "number here. D27's sparse grid could not see that: a collapsed "
            "run needs two points and the register's own claims put exactly "
            "one below the book. Four further interior collapses "
            "({-358,-357,-356}, {-333,-332}, {-331,-330}) show the sighted "
            "region is quantised rather than continuous, at exactly the window "
            "values where this book happens to have no event."
        ),
        "why": (
            "OFF PATH FOR THE TERMS DRIFT -- which is a claim about the "
            "ORGAN's inputs, not an exemption, and (since D27) no longer the "
            "whole entry: see `own_drift` for the graded knob that DOES reach "
            "this organ and the band it measured. "
            "`PaymentObservationConsumer._arrears_risk_belief` "
            "counts observed DD/rail FAILURE EVENTS and never reads the "
            "ledger's dating, so no terms drift can reach it -- measured "
            "unmoved at every drift on every seed, including drifts that take "
            "the detection dimension to its flag-everything degenerate. An "
            "off-path entry is where D21's defect hid (a control that "
            "BELIEVED an exemption), so this one must name a probe that DOES "
            "move the dimension and have it measured -- its own indiscriminate "
            "degenerate, scored through its own shipped scorer."
        ),
    },
    "belief_population_mix": {
        "drift": "organ_terms_drift_days",
        "in_causal_path": False,
        "invisible_drifts": (),
        "visible_drifts": (),
        "collapsed_pairs": (),
        "structural": True,
        "debt_atom": None,
        "exercised_by": "HEADLINE_DIRECTION_COVERAGE",
        "own_drift": "organ_failure_window_drift_days",
        # -309 JOINED THE BAND (atom D29): the sparse grid never scored it, and
        # it is invisible here on every seed while `belief` splits on it. -310
        # and -311 are still declared NEITHER way on purpose: they move this
        # dimension on seed 7 and not on 11/23. The register's bands are
        # all-seed claims (a band that holds on one seed is not structural), so
        # a seed-split drift belongs in neither list -- and saying so here
        # stops a later reader "completing" the band from the other
        # dimension's.
        "own_invisible_drifts": (-309, -308, -100, -1, 1, 500),
        # -370 REPLACED -380 for the same reason as `belief`: -380 sits inside
        # the low saturated run (atom D29).
        "own_visible_drifts": (-370, -350, -320),
        "own_debt_atom": "D27_belief_window_saturates_on_this_book",
        # RE-DERIVED ON THE BOOK-DERIVED GRID (atom D29). This entry is where
        # the grid's provenance shows most plainly: the register put this
        # dimension's ceiling at its SIBLING's -308, because -309 was never
        # scored. It is one day blinder than `belief` -- dropping the oldest
        # events moves an account's tier without moving the population MIX --
        # and that is a real difference between two published numbers that the
        # register asserted away by never asking. The seed-split {-311,-310}
        # collapse is declared as a collapse, which it is on every seed, while
        # neither member is declared visible or invisible, which they are not.
        "own_collapsed_runs": (
            (-400, -371), (-333, -332), (-311, -310),
            (-309, -308, -100, -1, 0, 1, 500),
        ),
        "own_saturates_below": -371,
        "own_saturates_above": -309,
        "own_saturation_atom": "D27_belief_window_saturates_on_this_book",
        # UPPER OWNER D27 -> D30 for the same reason as `belief` (Expert Hour
        # #12): this edge is set by N_PERIODS/PERIOD_SPACING_DAYS/
        # BILLING_CYCLE_SPREAD_DAYS/AS_OF_BUFFER_DAYS, four harness constants,
        # and naming the company's memory as its owner attributes the harness's
        # calendar to the company. The one-day difference from `belief` (-309
        # vs -308) is this dimension's own bluntness and stays D19's.
        "own_saturation_atom_below": "D29_the_as_of_buffer_floors_the_memory_grid",
        "own_saturation_atom_above": "D30_the_belief_band_is_this_books_length",
        # THIS FIGURE'S OWN RESOLUTION (atom D33), and the number Expert Hour
        # #15 found nobody had ever asked for. 314d, measured through this
        # dimension's own scorer at the 4dp its consumers render -- FIVE days
        # past the BOOK bound its caveat was publishing as its resolution (309d
        # on seed 11) and FOUR days past its sibling's 310d, which it shared a
        # byte-identical sentence with. `own_why` below already SAID this
        # dimension was blunter; nothing turned that into the number the reader
        # gets, which is Hour #11's "a lead is not a control" one field over.
        "own_readable_resolution_floor_days": 314,
        # AND THE PREDICATE (atom D33). Bit-equality reports 312d, because at
        # seed 11 this figure "moves" at -310..-313 by 1.4e-17 -- a difference no
        # 4dp consumer can render, counted as one company being told apart from
        # another. That is what put `own_saturates_above` at -309 rather than
        # -313, and every collapse run above is derived with the same predicate.
        "own_bit_equality_floor_days": 312,
        "own_floor_predicate_atom": "D33_the_collapse_predicate_is_bit_equality",
        "own_why": (
            "SATURATED for the same reason as `belief` and one step blunter: "
            "it is the same labels under a distribution distance (atom D19), "
            "so it needs the dropped events to move the population MIX, not "
            "merely one account's tier. Every window from 91d up publishes a "
            "bit-identical figure on seeds 7/11/23 -- one day EARLIER than "
            "`belief`, which the register could not see while its grid was its "
            "own claims -- and a 310d shortening moves `belief` on all three "
            "seeds while moving this one on only seed 7. It saturates BELOW at "
            "the same -371d and for the same AS_OF_BUFFER_DAYS reason (atom "
            "D29)."
        ),
        "why": (
            "OFF PATH FOR THE TERMS DRIFT for the same organ reason as "
            "`belief` -- it is the same labels under a distribution distance "
            "(atom D19). Its exercising probe is the one that separated the "
            "two dimensions in the first place: the indiscriminate degenerate "
            "moves it, a per-case permutation deliberately does not. Its "
            "graded resolution is measured against `own_drift`, as D27 "
            "requires of every off-path entry."
        ),
    },
}


def measure_dimension_drift_resolution(
    *,
    n_customers: int = 300,
    seeds: Sequence[int] = RESOLUTION_SEEDS,
    register: Optional[Dict[str, Dict[str, object]]] = None,
    runner: Optional[Callable[[int, int], Dict[str, object]]] = None,
) -> Dict[str, Dict[str, object]]:
    """MEASURE `DIMENSION_DRIFT_RESOLUTION` rather than trust it: re-score the
    SAME population against a counterfactual COMPANY holding the wrong payment
    terms, and record which drifts each published dimension's OWN shipped
    scorer actually saw.

    Returns {dimension: {"by_seed", "unmoved", "moved", "collapses",
    "probe_bit", "exercised", "seeds"}} where `unmoved`/`moved` are the drifts
    that behaved that way on EVERY measured seed -- the register's claims are
    structural (they follow from the scenario calendar), so a band that holds
    on one seed and not another is a claim this register must refuse.

    `probe_bit` is the vacuity guard on the probe ITSELF: the counterfactual
    company must move SOMETHING somewhere, or every invisibility declaration in
    the register is being handed a free pass by a drift parameter that has
    silently stopped drifting -- the fail-silent shape this instrument has now
    produced six times, twice inside the control written to close the previous
    one.
    """
    register = DIMENSION_DRIFT_RESOLUTION if register is None else register
    # THE GRID IS THE BOOK'S, AND THE DECLARATIONS ARE ONLY UNIONED IN (atom
    # D28). Deriving it from the register meant the exactness rule was applied
    # exactly where the band had already answered; the declared drifts stay in
    # the union so a declaration OUTSIDE the grid is still scored rather than
    # skipped into a free pass.
    drifts = sorted(
        set(dense_drift_grid())
        | {0}
        | {k for e in register.values()
           for k in tuple(e["invisible_drifts"]) + tuple(e["visible_drifts"])}
        | {k for e in register.values()
           for pair in tuple(e.get("collapsed_pairs") or ()) for k in pair}
    )
    if runner is None:
        def runner(seed: int, k: int) -> Dict[str, object]:
            # ONE population per seed, re-scored per drift: the counterfactual
            # is a different COMPANY over the same world, never a different
            # world (R13). Cached per (n, seed, k) because the dense grid is
            # swept by several controls and by the CLI in one process.
            key = (n_customers, seed, k)
            if key not in _RESOLUTION_SCORES:
                recs, cons, _ledger, as_of = _resolution_population(
                    n_customers, seed)
                _RESOLUTION_SCORES[key] = score_triad(
                    recs, cons, as_of, organ_terms_drift_days=k)
            return _RESOLUTION_SCORES[key]

    scored = {(s, k): runner(s, k) for s in seeds for k in drifts}
    dims = published_dimensions(scored[(seeds[0], 0)])
    out: Dict[str, Dict[str, object]] = {}
    any_movement = False
    for dim in dims:
        by_seed: Dict[int, Dict[str, object]] = {}
        for s in seeds:
            base = scored[(s, 0)][dim].gap
            by_drift = {k: scored[(s, k)][dim].gap for k in drifts if k != 0}
            by_seed[s] = {
                "baseline": base,
                "by_drift": by_drift,
                "moved": sorted(k for k, v in by_drift.items() if v != base),
                "unmoved": sorted(k for k, v in by_drift.items() if v == base),
            }
        moved = sorted(set.intersection(
            *[set(by_seed[s]["moved"]) for s in seeds]))
        unmoved = sorted(set.intersection(
            *[set(by_seed[s]["unmoved"]) for s in seeds]))
        any_movement = any_movement or bool(moved)
        out[dim] = {
            "seeds": tuple(seeds),
            "drifts": tuple(drifts),
            "by_seed": by_seed,
            "moved": moved,
            "unmoved": unmoved,
            "exercised": None,
            **_measure_collapse_runs(by_seed, drifts, seeds),
        }
    for dim in dims:
        out[dim]["collapses"] = {
            pair: _collapse_state(out[dim], pair)
            for pair in tuple(
                (register.get(dim) or {}).get("collapsed_pairs") or ())
            if _collapse_state(out[dim], pair) is not None
        }
    # THE OFF-PATH ENTRIES' OTHER PROBE, measured rather than believed: a
    # dimension nothing in this register can move must still be moved by
    # SOMETHING, or its entry is an exemption no evidence can ever remove.
    hdc = measure_headline_direction_coverage(scored[(seeds[0], 0)])
    for dim, row in out.items():
        row["probe_bit"] = any_movement
        named = (register.get(dim) or {}).get("exercised_by")
        if named == "HEADLINE_DIRECTION_COVERAGE" and dim in hdc:
            row["exercised"] = bool(hdc[dim].get("distinguishes"))
    return out


def _resolution_population(n_customers: int, seed: int):
    """One built scenario per (n, seed), cached: the resolution sweep re-scores
    the SAME population once per drift, and rebuilding it per drift would make
    a slow control slower without changing a single number."""
    key = (n_customers, seed)
    if key not in _RESOLUTION_POPULATIONS:
        _RESOLUTION_POPULATIONS[key] = build_scenario(n_customers, seed=seed)
    return _RESOLUTION_POPULATIONS[key]


_RESOLUTION_POPULATIONS: Dict[tuple, tuple] = {}
_RESOLUTION_SCORES: Dict[tuple, Dict[str, object]] = {}
# The memory sweep BUILDS a company per drift, so its cache holds the world it
# was built over too -- the R13 fingerprint is taken off it (atom D29).
_OWN_RESOLUTION_SCORES: Dict[tuple, tuple] = {}


def _measure_collapse_runs(by_seed: Dict[int, Dict[str, object]],
                           drifts: Sequence[int],
                           seeds: Sequence[int]) -> Dict[str, object]:
    """WHERE THIS DIMENSION STOPS TELLING TWO COMPANIES APART, derived from the
    readings rather than from anybody's declaration (atom D28).

    A COLLAPSED RUN is any group of two or more counterfactual companies on the
    swept grid whose readings are bit-identical ON EVERY SEED -- the register's
    claims are structural, so a coincidence on one seed is not one of these. A
    run touching an END of the grid is SATURATION: resolution has stopped in
    that tail and every company further out reads the same, which is the shape
    D27 found on the belief window and could only ask of an off-path entry.

    `undefined_readings` is the fail-open this measurement would otherwise
    have: a dimension whose population empties under a drift publishes `None`,
    and `None != baseline` reads as MOVEMENT -- an instrument that has stopped
    reading at all, counted as resolution.
    """
    def reading(s: int, k: int):
        return by_seed[s]["baseline"] if k == 0 else by_seed[s]["by_drift"][k]

    ks = sorted(drifts)
    undefined = tuple(k for k in ks
                      if any(reading(s, k) is None for s in seeds))
    groups: Dict[tuple, List[int]] = {}
    for k in ks:
        groups.setdefault(tuple(repr(reading(s, k)) for s in seeds),
                          []).append(k)
    runs = tuple(sorted(tuple(v) for v in groups.values() if len(v) > 1))
    lo, hi = ks[0], ks[-1]
    return {
        "collapsed_runs": runs,
        "saturates_below": next((max(r) for r in runs if lo in r), None),
        "saturates_above": next((min(r) for r in runs if hi in r), None),
        "undefined_readings": undefined,
    }


def _collapse_state(row: Dict[str, object], pair: Tuple[int, int]):
    """Whether a declared pair of counterfactual companies really do publish ONE
    reading, on EVERY measured seed -- re-derived from the raw per-seed readings.
    `None` where either member was never scored."""
    states = []
    for s in row["seeds"]:
        readings = {**row["by_seed"][s]["by_drift"],
                    0: row["by_seed"][s]["baseline"]}
        if pair[0] not in readings or pair[1] not in readings:
            return None
        states.append((readings[pair[0]] == readings[pair[1]],
                       readings[pair[0]] != row["by_seed"][s]["baseline"],
                       (readings[pair[0]], readings[pair[1]])))
    return {
        "collapsed": all(s[0] for s in states),
        "distinct_from_baseline": all(s[1] for s in states),
        "readings": states[0][2],
    }


def check_dimension_drift_resolution(
    measured: Dict[str, Dict[str, object]],
    register: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """Put every `DIMENSION_DRIFT_RESOLUTION` declaration on trial against the
    measurement and return the VIOLATIONS (empty = the register is honest).

    The keyset is DERIVED, so the two ways a register stops describing the code
    both RAISE rather than passing quietly: a dimension published with no entry
    would be swept by nothing (how this class escaped D23's register), and an
    entry for a dimension nobody publishes reads exactly like a clean one.
    """
    register = DIMENSION_DRIFT_RESOLUTION if register is None else register
    missing = sorted(set(measured) - set(register))
    if missing:
        raise AssertionError(
            f"published dimensions with no DIMENSION_DRIFT_RESOLUTION entry: "
            f"{missing} -- a dimension nothing sweeps is exactly how this class "
            "escaped the register before it"
        )
    orphan = sorted(set(register) - set(measured))
    if orphan:
        raise AssertionError(
            f"DIMENSION_DRIFT_RESOLUTION entries for dimensions nobody "
            f"publishes: {orphan} -- an unreachable register entry reads like a "
            "clean one"
        )
    violations: List[str] = []
    for dim in sorted(measured):
        row, entry = measured[dim], register[dim]
        if not row["probe_bit"]:
            violations.append(
                f"{dim}: the terms-drift probe moved NOTHING anywhere in the "
                "register -- an inert counterfactual company cannot evidence "
                "either a blindness or a resolution"
            )
        if not entry["in_causal_path"]:
            violations.extend(_check_off_path_entry(dim, row, entry))
        else:
            violations.extend(_check_on_path_entry(dim, row, entry))
    violations.extend(_check_register_is_differential(register))
    return violations


def _check_off_path_entry(dim: str, row: Dict[str, object],
                          entry: Dict[str, object]) -> List[str]:
    """An entry claiming the drift has no causal route to this dimension's
    organ. It is the EXEMPTION shape D21 hid behind for five Hours, so it earns
    three rules of its own: the claim must still be false-ifiable by
    measurement, the dimension must be moved by SOMETHING, and -- since atom
    D27 -- it must name a GRADED knob on its own organ path and have the band
    measured. The third rule is the one this state was missing: `exercised_by`
    names an INDISCRIMINATE DEGENERATE, the largest error there is, so it
    proves non-inertness and measures no resolution at all. Two of five
    published dimensions sat in this state, and when the graded knob was
    finally built one of them turned out to be unbounded-blind with the
    shipped company 308 days inside its own blind band."""
    out: List[str] = []
    if row["moved"]:
        out.append(
            f"{dim}: declared OFF the drift's causal path but drifts "
            f"{row['moved']} moved it -- the entry has rotted; "
            "re-derive it as an on-path entry with a measured band"
        )
    if not entry.get("exercised_by"):
        out.append(
            f"{dim}: declared off-path and names no `exercised_by` "
            "probe -- a dimension nothing in this repo can move is "
            "unfalsifiable, not exempt"
        )
    elif row["exercised"] is not True:
        out.append(
            f"{dim}: its declared `exercised_by` probe "
            f"({entry['exercised_by']}) did NOT move it "
            f"(exercised={row['exercised']!r}) -- the exemption is "
            "believed, which is the shape D21 hid behind"
        )
    if not entry.get("own_drift"):
        out.append(
            f"{dim}: declared off-path and names no `own_drift` -- an "
            "indiscriminate degenerate establishes that the dimension is not "
            "inert and measures NO resolution; name the graded counterfactual "
            "company on this dimension's own organ path (atom D27)"
        )
    return out


# ---------------------------------------------------------------------------
# THE OFF-PATH ENTRIES' OWN GRADED KNOB (atom D27, H27 Expert Hour #9)
# ---------------------------------------------------------------------------
# THE CLASS, one state wider than D25's. `DIMENSION_DRIFT_RESOLUTION` asks what
# the SMALLEST company error each published dimension can see, and answers it
# for the dimensions the register's single drift happens to reach. The other
# state -- OFF PATH -- was allowed to discharge itself with `exercised_by`, a
# BINARY reading against an indiscriminate degenerate: it says the dimension
# is not inert and says nothing whatever about resolution. Both belief
# dimensions sat there, so 2 of 5 published dimensions had no measured
# resolution, and the hole was in the shape the register was built to close.
#
# So an off-path entry now owes the same graded band as an on-path one, against
# a knob that reaches ITS organ. The measurement is DIFFERENTIAL on purpose:
# the knob must move the dimensions that declare it and NOT the ones that do
# not, which is what makes it evidence about this organ rather than a second
# global perturbation. And because a memory window is a CONSTRUCTOR argument,
# the counterfactual company must be BUILT rather than re-scored -- so the
# world it is built over is compared record by record against the undrifted
# one, and an entry whose world moved is refused (R13: a second company, never
# a second world).
# ---------------------------------------------------------------------------


def measure_own_drift_resolution(
    *,
    n_customers: int = 300,
    seeds: Sequence[int] = RESOLUTION_SEEDS,
    register: Optional[Dict[str, Dict[str, object]]] = None,
    runner: Optional[Callable[[str, int, int], tuple]] = None,
) -> Dict[str, Dict[str, object]]:
    """MEASURE every `own_drift` declaration in the register rather than trust
    it: build the counterfactual COMPANY each off-path dimension names, re-score
    the same world, and record which graded drifts that dimension's OWN shipped
    scorer actually saw.

    Returns {dimension: {...}} for every entry declaring an `own_drift`, plus
    the differential (`off_target`: dimensions that moved under a knob they do
    not declare) and the world-invariance witness.

    THE GRID IS THE BOOK'S (atom D29). D28 fixed that for the terms sweep and
    left this half building its grid from `own_invisible_drifts |
    own_visible_drifts` -- the register asked exactly where it had already
    answered, so D27's saturation edge was a property of where D27 swept. The
    declarations are still UNIONED IN so a declaration outside the grid is
    scored rather than skipped into a free pass; they no longer DEFINE it."""
    register = DIMENSION_DRIFT_RESOLUTION if register is None else register
    knobs: Dict[str, List[int]] = {}
    for entry in register.values():
        knob = entry.get("own_drift")
        if not knob:
            continue
        drifts = knobs.setdefault(str(knob), [0])
        for k in (tuple(entry.get("own_invisible_drifts") or ())
                  + tuple(entry.get("own_visible_drifts") or ())):
            if k not in drifts:
                drifts.append(int(k))
    if runner is None:
        def runner(knob: str, seed: int, k: int) -> tuple:
            # Cached per (n, seed, knob, k): the CLI and several controls sweep
            # the same book-derived grid inside one process, and a company is
            # BUILT per drift here (the window is a constructor argument).
            key = (n_customers, seed, knob, k)
            if key not in _OWN_RESOLUTION_SCORES:
                recs, cons, _ledger, as_of = build_scenario(
                    n_customers, seed=seed, **{knob: k})
                _OWN_RESOLUTION_SCORES[key] = (
                    recs, score_triad(recs, cons, as_of), as_of)
            return _OWN_RESOLUTION_SCORES[key]

    out: Dict[str, Dict[str, object]] = {}
    for knob, drifts in knobs.items():
        if knob not in OWN_DRIFT_BOOK_GRIDS:
            raise AssertionError(
                f"`{knob}` has no book-derived grid in OWN_DRIFT_BOOK_GRIDS -- "
                "falling back to the register's own declarations is the atom "
                "D29 defect itself, so this raises rather than measuring the "
                "band exactly where the band already answered"
            )
        # THE UNDRIFTED COMPANY FIRST, because the grid is a property of the
        # book it will be swept over and nothing else knows the event ages.
        scored: Dict[tuple, tuple] = {
            (s, 0): runner(knob, s, 0) for s in seeds}
        grid: set = set(drifts)
        for s in seeds:
            grid |= set(OWN_DRIFT_BOOK_GRIDS[knob](
                scored[(s, 0)][0], scored[(s, 0)][2]))
        drifts = sorted(grid)
        scored.update({(s, k): runner(knob, s, k)
                       for s in seeds for k in drifts if k != 0})
        dims = published_dimensions(scored[(seeds[0], 0)][1])
        # R13 WITNESS. A knob that moved the WORLD would make every reading
        # below a comparison between two different books, and the whole point
        # of a counterfactual COMPANY is that it does not.
        world_identical = all(
            _world_fingerprint(scored[(s, k)][0])
            == _world_fingerprint(scored[(s, 0)][0])
            for s in seeds for k in drifts)
        moved_any: Dict[str, List[int]] = {}
        for dim in dims:
            by_seed: Dict[int, Dict[str, object]] = {}
            for s in seeds:
                base = scored[(s, 0)][1][dim].gap
                by_drift = {k: scored[(s, k)][1][dim].gap
                            for k in drifts if k != 0}
                by_seed[s] = {
                    "baseline": base,
                    "by_drift": by_drift,
                    "moved": sorted(k for k, v in by_drift.items() if v != base),
                    "unmoved": sorted(k for k, v in by_drift.items()
                                      if v == base),
                }
            moved = sorted(set.intersection(
                *[set(by_seed[s]["moved"]) for s in seeds]))
            unmoved = sorted(set.intersection(
                *[set(by_seed[s]["unmoved"]) for s in seeds]))
            moved_any[dim] = sorted(
                {k for s in seeds for k in by_seed[s]["moved"]})
            if (register.get(dim) or {}).get("own_drift") != knob:
                continue
            out[dim] = {
                "knob": knob,
                "seeds": tuple(seeds),
                "drifts": tuple(drifts),
                "by_seed": by_seed,
                "moved": moved,
                "unmoved": unmoved,
                "world_identical": world_identical,
                # The book's own prediction, taken on the UNDRIFTED company --
                # the claim the sweep is cross-checked against.
                "book": measure_belief_window_resolution(
                    scored[(seeds[0], 0)][0], scored[(seeds[0], 0)][2]),
                # AND ON EVERY SEED (atom D29). Both saturation edges are
                # all-seed claims, so predicting them from one seed's book
                # would make the cross-check depend on which seed came first.
                "books": {s: measure_belief_window_resolution(
                    scored[(s, 0)][0], scored[(s, 0)][2]) for s in seeds},
                # atom D28: the same collapse/saturation measurement the terms
                # grid gets, so the shared checker has something to try here.
                **_measure_collapse_runs(by_seed, drifts, seeds),
            }
        for dim in out:
            if out[dim]["knob"] != knob:
                continue
            # THE DIFFERENTIAL. A knob that moves everything is a second global
            # perturbation, not evidence about one organ.
            out[dim]["off_target"] = {
                d: moved_any[d] for d in dims
                if (register.get(d) or {}).get("own_drift") != knob
                and moved_any[d]
            }
            out[dim]["probe_bit"] = any(moved_any[d] for d in dims)
    return out


def _world_fingerprint(records: Sequence["PeriodRecord"]) -> tuple:
    """The TRUTH side, reduced to a comparable value. Every field the scorers
    read off a `PeriodRecord`, so a counterfactual company that quietly moved
    the world cannot come out equal here."""
    return tuple(sorted(
        (r.customer_id, r.period_index, r.result, r.issue_date, r.due_date,
         r.invoice_ref, r.payment_method, r.days_late)
        for r in records))


def check_own_drift_resolution(
    measured: Dict[str, Dict[str, object]],
    register: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """Put every `own_drift` declaration on trial against the measurement and
    return the VIOLATIONS (empty = the register is honest about what its
    off-path dimensions can resolve)."""
    register = DIMENSION_DRIFT_RESOLUTION if register is None else register
    declared = {d for d, e in register.items() if e.get("own_drift")}
    missing = sorted(declared - set(measured))
    if missing:
        raise AssertionError(
            f"dimensions declaring an `own_drift` that were never measured: "
            f"{missing} -- an unmeasured band reads exactly like a clean one, "
            "which is the fail-silent shape this register exists to refuse"
        )
    orphan = sorted(set(measured) - declared)
    if orphan:
        raise AssertionError(
            f"own-drift measurements for dimensions declaring no `own_drift`: "
            f"{orphan}"
        )
    violations: List[str] = []
    for dim in sorted(measured):
        row, entry = measured[dim], register[dim]
        if not row.get("world_identical"):
            violations.append(
                f"{dim}: the `{row['knob']}` counterfactual CHANGED THE WORLD "
                "-- every reading under it compares two different books, so it "
                "evidences nothing about the company (R13)"
            )
        if not row.get("probe_bit"):
            violations.append(
                f"{dim}: the `{row['knob']}` probe moved NOTHING on any "
                "dimension -- an inert counterfactual company hands every "
                "invisibility declaration below it a free pass"
            )
        if row.get("off_target"):
            violations.append(
                f"{dim}: `{row['knob']}` also moved {sorted(row['off_target'])}"
                ", which do not declare it -- a knob that moves dimensions off "
                "its own organ path is a second global perturbation, not "
                "evidence about this one"
            )
        violations.extend(_check_own_band(dim, row, entry))
    return violations


def _check_own_band(dim: str, row: Dict[str, object],
                    entry: Dict[str, object]) -> List[str]:
    """The declared graded band, on trial -- the same EXACTNESS rule the
    on-path entries earned in D25 (a band that may only shrink is the decay the
    register exists to stop), plus the two rules an off-path entry needs."""
    out: List[str] = []
    swept = set(row["drifts"])
    for k in (tuple(entry.get("own_invisible_drifts") or ())
              + tuple(entry.get("own_visible_drifts") or ())):
        if k not in swept:
            # A declaration checked against a reading nobody took passes for
            # the wrong reason -- the same hole `_check_declared_collapses`
            # names one control over.
            out.append(
                f"{dim}: memory drift {k:+d}d is declared but was never "
                "scored -- a declaration checked against readings nobody took"
            )
    for k in tuple(entry.get("own_invisible_drifts") or ()):
        if k in swept and k not in row["unmoved"]:
            seen = {s: (row["by_seed"][s]["baseline"],
                        row["by_seed"][s]["by_drift"][k]) for s in row["seeds"]}
            out.append(
                f"{dim}: memory drift {k:+d}d is declared INVISIBLE but moved "
                f"the reading on at least one seed ({seen}). If "
                f"{entry.get('own_debt_atom')} has landed, RE-DERIVE this band"
            )
    for k in tuple(entry.get("own_visible_drifts") or ()):
        if k in swept and k not in row["moved"]:
            out.append(
                f"{dim}: memory drift {k:+d}d is declared VISIBLE but left the "
                "reading where it was on at least one seed -- the dimension is "
                "blinder than this register admits"
            )
    undeclared = [k for k in row["unmoved"]
                  if k not in tuple(entry.get("own_invisible_drifts") or ())]
    if undeclared:
        out.append(
            f"{dim}: memory drifts {undeclared} were MEASURED invisible and "
            "are not declared -- the band understates the blindness, and the "
            "caveat that interpolates it publishes a narrower blind spot than "
            "the instrument has"
        )
    blind = tuple(entry.get("own_invisible_drifts") or ())
    if blind and not entry.get("own_debt_atom"):
        out.append(
            f"{dim}: declares a memory blindness with no `own_debt_atom` -- an "
            "unowned hole; name the atom that will close it"
        )
    if not blind and not tuple(entry.get("own_visible_drifts") or ()):
        out.append(
            f"{dim}: declares neither a memory blindness nor a drift it must "
            "see -- an entry that cannot fail either way"
        )
    # THE SHARED RULE (atom D28). This is the same function the on-path entries
    # go through -- there is only one of it, so a saturation rule can no longer
    # exist on one side of `in_causal_path` and not the other.
    out.extend(_check_saturation_and_collapse(dim, row, entry, "own_"))
    # UNBOUNDED ABOVE is its own rule, and it is the D27 defect itself: a
    # blindness declared only over the drifts somebody happened to sweep reads
    # as a bounded band. If a POSITIVE drift is invisible, the parameter is
    # saturated and EVERY larger one is invisible too -- to infinity -- so the
    # band must say so and the book must agree.
    if any(k > 0 for k in blind):
        book = row.get("book") or {}
        if book.get("saturated") is not True:
            out.append(
                f"{dim}: declares a POSITIVE memory drift invisible (band "
                f"{list(blind)}) while the book predicts saturated="
                f"{book.get('saturated')!r} -- the sweep and the "
                "population-side predictor describe different instruments"
            )
        # THE CROSS-CHECK, in the direction the predictor can prove: no drift
        # that leaves the window above the oldest event may move the reading.
        headroom = book.get("headroom_days")
        if headroom is not None:
            for k in row["moved"]:
                if k >= -headroom:
                    out.append(
                        f"{dim}: memory drift {k:+d}d MOVED the reading while "
                        f"leaving {headroom + k}d of headroom above the "
                        f"oldest event ({book.get('oldest_event_age_days')}d)"
                        " -- no event changed side, so something other than "
                        "the window is reading this company's memory"
                    )
    out.extend(_check_book_predicts_both_edges(dim, row))
    return out


def _check_book_predicts_both_edges(dim: str,
                                    row: Dict[str, object]) -> List[str]:
    """BOTH saturation edges, predicted from the population and measured
    through the organ (atom D29) -- an independent pair, not a restatement.

    The predictor reads the WORLD's own event dates and the declared window; it
    never touches `_arrears_risk_belief` (asserted against its AST). The sweep
    re-scores the same book through the dimension's own shipped scorer. So a
    disagreement means one of the two is describing an instrument that is not
    there -- which is exactly how D27's `saturates_below = None` survived: no
    predictor existed for that edge to disagree with.

    Both edges are ALL-SEED claims, so the provable region is bounded by the
    tightest seed: no seed's counted set may change (`min` of the per-seed
    floors, `max` of the per-seed ceilings).

    The claim is ONE-DIRECTIONAL, like the predictor it comes from. Beyond the
    predicted edge NO event changes side, so a sweep that still reads movement
    there is reading something other than the window -- a violation. Inside it
    the dimension may saturate EARLIER (the dropped events did not move that
    particular statistic), which is a real, blinder reading and not a lie: it
    is measured, declared, and left to the register's exactness rule.
    """
    books = row.get("books") or {}
    if not books or any(b.get("saturated") is None for b in books.values()):
        return []
    out: List[str] = []
    for edge, key, agg, worse, label in (
        ("saturates_below", "predicted_saturates_below_drift", min, -1,
         "no event in this book is young enough to count"),
        ("saturates_above", "predicted_saturates_above_drift", max, +1,
         "no event in this book is old enough to fall out"),
    ):
        predicted = agg(b[key] for b in books.values())
        got = row.get(edge)
        if got is None:
            out.append(
                f"{dim}: the book proves resolution stops at {predicted:+d}d "
                f"({label} beyond it) and the sweep measured {edge}=None -- an "
                "unmeasured edge reads exactly like an absent one, which is "
                "how D27 declared a bounded band on a book that saturates"
            )
        elif (got - predicted) * worse > 0:
            out.append(
                f"{dim}: the sweep measured {edge}={got:+d}d and the book "
                f"proves it stops by {predicted:+d}d ({label} beyond it) -- so "
                "the reading moved where no event can change side, and "
                "something other than the memory window is reading this "
                "company"
            )
    return out


def _check_saturation_and_collapse(dim: str, row: Dict[str, object],
                                   entry: Dict[str, object],
                                   prefix: str) -> List[str]:
    """THE RULE THAT MUST NOT BE KEYED TO A REGISTER STATE (atom D28).

    D27 built the saturation rule and put it inside `_check_own_band`, which is
    reached only from `check_own_drift_resolution`, which iterates only the
    entries declaring an `own_drift` -- the OFF-PATH ones. So the register that
    refuses an unbounded-blind band off the causal path accepted one ON it, and
    `detection` had TWO saturated tails nobody had asked about. That is the
    same keying, in the control written to close the previous keying.

    This function is therefore called from BOTH checkers, once per entry, on
    the knob that actually reaches that entry's organ: the terms grid for an
    on-path entry (`prefix=""`), the entry's own graded knob for an off-path
    one (`prefix="own_"`). The rule cannot exist on one side and not the other
    because there is only one of it.

    Every collapse is DERIVED from the readings and must be declared EXACTLY --
    an undeclared collapse is the blindness the sparse grid hid, and a declared
    collapse the sweep cannot find is a debt entry outliving its debt.
    """
    out: List[str] = []
    # AN UNDEFINED READING IS A FAIL-OPEN UNLESS IT IS DECLARED AND WITNESSED
    # (atom D28, extended by D31). The rule was absolute because the two knobs
    # it ran on never emptied a population; the reconciliation knob does, at
    # the far end where no failure is detected before `as_of` at all. That is a
    # BOUND, and D24's distinction applies: a bound is only a bound with a
    # witness. So a declared region must be witnessed by the population itself
    # -- `reading is None` exactly where the population is empty -- and an
    # UNdeclared one is the fail-open it always was.
    undefined = tuple(row.get("undefined_readings") or ())
    declared_undefined = tuple(entry.get(f"{prefix}undefined_drifts") or ())
    undeclared = [k for k in undefined if k not in declared_undefined]
    if undeclared:
        out.append(
            f"{dim}: published NO reading at drifts "
            f"{undeclared} -- an absent reading compares "
            "unequal to the baseline and is therefore counted as RESOLUTION by "
            "every band below; an instrument that stopped reading is not one "
            "that saw the company move"
        )
    for k in declared_undefined:
        if k not in tuple(row.get("drifts") or (k,)):
            out.append(
                f"{dim}: declares NO reading at drift {k:+d}d and the sweep "
                "never scored it -- a declaration checked against readings "
                "nobody took is the D23 shape, one field over"
            )
        elif k not in undefined:
            out.append(
                f"{dim}: declares NO reading at drift {k:+d}d and the sweep "
                "read one -- a debt entry outliving its debt misleads worse "
                "than none; RE-DERIVE it"
            )
            continue
        witness = (row.get("undefined_witness") or {}).get(k)
        if not witness or not all(is_none == (pop == 0)
                                  for is_none, pop in witness):
            out.append(
                f"{dim}: declares NO reading at drift {k:+d}d and the witness "
                f"is {witness!r} -- an absent reading is a BOUND only while "
                "the population it was read over is empty; unwitnessed, it is "
                "an instrument that stopped for some other reason"
            )
    measured = {tuple(r) for r in (row.get("collapsed_runs") or ())}
    declared = {tuple(r) for r in (entry.get(f"{prefix}collapsed_runs") or ())}
    for run in sorted(measured - declared):
        out.append(
            f"{dim}: companies {list(run)} publish ONE bit-identical reading "
            "on every seed and the register declares no such collapse -- this "
            "is the blindness a grid derived from the register's own claims "
            "could not reach (atom D28)"
        )
    for run in sorted(declared - measured):
        out.append(
            f"{dim}: declares companies {list(run)} COLLAPSE and the sweep "
            "reads them apart -- a debt entry outliving its debt misleads "
            "worse than none; RE-DERIVE it"
        )
    for edge, label, worse in (("saturates_below", "BELOW", "shorter"),
                               ("saturates_above", "ABOVE", "longer")):
        got, said = row.get(edge), entry.get(f"{prefix}{edge}")
        if got != said:
            out.append(
                f"{dim}: measured {edge}={got!r} and declares {said!r} -- "
                f"resolution stops {label} that edge, so every company further "
                f"{worse} than it publishes ONE number and the register must "
                "say so"
            )
    # A DRIFT DECLARED SIGHTED THAT SITS INSIDE A COLLAPSED RUN (atom D29).
    # D28 saw this in prose -- "the -8 the old grid read as MOVED, as evidence
    # of resolution, sits inside the saturated tail" -- and built no rule, so
    # the same shape survived one register field over: `belief` declared -380d
    # VISIBLE while a company that forgets everything and one that remembers 20
    # days publish one number. Differing from the baseline is not resolution;
    # resolution is being told apart from your NEIGHBOURS.
    for k in tuple(entry.get(f"{prefix}visible_drifts") or ()):
        for run in sorted(measured):
            if k in run:
                out.append(
                    f"{dim}: drift {k:+d}d is declared VISIBLE and sits inside "
                    f"the collapsed run {list(run)} -- it differs from the "
                    "baseline but not from the companies beside it, so it "
                    "evidences no resolution; declare a drift the sweep reads "
                    "APART from its neighbours"
                )
                break
    saturated = (row.get("saturates_below") is not None
                 or row.get("saturates_above") is not None)
    if (measured or saturated) and not entry.get(f"{prefix}saturation_atom"):
        out.append(
            f"{dim}: has a measured collapse or saturation and names no "
            f"`{prefix}saturation_atom` -- an unowned hole; name the atom that "
            "will close it (and never the atom that owns a DIFFERENT residual "
            "of the same dimension)"
        )
    # AND AN OWNER PER EDGE (atom D29). One `saturation_atom` for both tails is
    # what made two holes with two different causes look like one: the belief
    # dimensions saturate ABOVE because the company's memory outruns the book
    # (D27) and BELOW because `as_of` sits a month past the last event (D29),
    # and a single field could only ever name one of them.
    for edge, field in (("saturates_below", f"{prefix}saturation_atom_below"),
                        ("saturates_above", f"{prefix}saturation_atom_above")):
        if row.get(edge) is not None and not entry.get(field):
            out.append(
                f"{dim}: measured {edge}={row[edge]!r} and names no `{field}` "
                "-- two tails can stop for two different reasons, so each "
                "names the atom that owns IT"
            )
    return out


def _check_on_path_entry(dim: str, row: Dict[str, object],
                         entry: Dict[str, object]) -> List[str]:
    """An entry the drift can actually reach: its declared band, its declared
    sight, and its declared collapses all go on trial against the readings."""
    out: List[str] = []
    for k in entry["invisible_drifts"]:
        if k not in row["unmoved"]:
            seen = {s: (row["by_seed"][s]["baseline"],
                        row["by_seed"][s]["by_drift"][k]) for s in row["seeds"]}
            out.append(
                f"{dim}: drift {k:+d}d is declared INVISIBLE but moved the "
                f"reading on at least one seed ({seen}). "
                f"If {entry['debt_atom']} has landed, RE-DERIVE this entry; "
                "a debt entry outliving its debt misleads worse than none"
            )
    for k in entry["visible_drifts"]:
        if k not in row["moved"]:
            out.append(
                f"{dim}: drift {k:+d}d is declared VISIBLE but left the "
                "reading where it was on at least one seed -- the "
                "dimension is blinder than this register admits"
            )
    # THE BAND MUST BE EXACT, NOT MERELY TRUE. Caught by this sweep on its own
    # first draft: with only the two rules above, UNDER-stating the blindness
    # passed silently -- drop -1 from the ageing band and every declaration
    # still held, while `ageing_resolution_caveat` (which interpolates the band)
    # went on publishing a narrower blind spot than the instrument has. A caveat
    # that can only shrink is the decay this register exists to stop.
    undeclared = [k for k in row["unmoved"]
                  if k not in tuple(entry["invisible_drifts"])]
    if undeclared:
        out.append(
            f"{dim}: drifts {undeclared} were MEASURED invisible and are "
            "not declared -- the band understates the blindness, and the "
            "caveat that interpolates it now publishes a narrower blind "
            "spot than the instrument has"
        )
    out.extend(_check_declared_collapses(dim, row, entry))
    # THE SAME RULE THE OFF-PATH ENTRIES GET, on this entry's own knob (atom
    # D28). It lived only on the other side of the register's `in_causal_path`
    # split until Expert Hour #10.
    out.extend(_check_saturation_and_collapse(dim, row, entry, ""))
    blind = bool(tuple(entry["invisible_drifts"])
                 or tuple(entry.get("collapsed_pairs") or ()))
    if blind and not entry["debt_atom"]:
        out.append(
            f"{dim}: declares a blindness with no `debt_atom` -- an "
            "unowned hole; name the atom that will close it"
        )
    if not blind and not tuple(entry["visible_drifts"]):
        out.append(
            f"{dim}: on-path and declares neither a blindness nor a drift "
            "it must see -- an entry that cannot fail either way"
        )
    return out


def _check_declared_collapses(dim: str, row: Dict[str, object],
                              entry: Dict[str, object]) -> List[str]:
    """Two DIFFERENT companies declared to publish ONE reading. Re-derived from
    the RAW readings rather than read out of the measurement's own summary, so a
    claim is never checked against a reading that was never taken: `measure` is
    told the register only to choose which drifts to score."""
    out: List[str] = []
    for pair in tuple(entry.get("collapsed_pairs") or ()):
        got = _collapse_state(row, pair)
        if got is None:
            out.append(
                f"{dim}: drifts {pair[0]:+d}d and {pair[1]:+d}d are "
                "declared to COLLAPSE but were never scored -- a "
                "declaration checked against readings nobody took"
            )
        elif not got.get("collapsed"):
            out.append(
                f"{dim}: drifts {pair[0]:+d}d and {pair[1]:+d}d are "
                f"declared to COLLAPSE to one reading but read "
                f"{got.get('readings')!r}. If {entry['debt_atom']} has "
                "landed, RE-DERIVE this entry"
            )
        elif not got.get("distinct_from_baseline"):
            out.append(
                f"{dim}: drifts {pair[0]:+d}d and {pair[1]:+d}d read the "
                "BASELINE -- that is an INVISIBILITY, not a collapse; "
                "declare it where the rule that checks it lives"
            )
    return out


def _check_register_is_differential(
        register: Dict[str, Dict[str, object]]) -> List[str]:
    """All three declared states must be OCCUPIED. A register whose entries all
    land on one side is a blanket claim wearing a register's clothes -- it would
    pass whatever the instrument did."""
    kinds = {
        (bool(e["in_causal_path"]),
         bool(tuple(e["invisible_drifts"]) or tuple(e.get("collapsed_pairs") or ())))
        for e in register.values()
    }
    out: List[str] = []
    # ATOM D28's DIFFERENTIAL, and it is a different question from the three
    # states below: those ask whether the register's DECLARED kinds are all
    # occupied, this asks whether the dense grid found any dimension it could
    # NOT collapse. A register in which every dimension saturates somewhere is
    # an "everything is quantised" claim that would pass whatever the
    # instrument did -- the same excuse an all-blind band would be.
    if not any(
        not tuple(e.get("collapsed_runs") or ())
        and e.get("saturates_below") is None
        and e.get("saturates_above") is None
        for e in register.values() if e["in_causal_path"]
    ):
        out.append(
            "register: every on-path dimension collapses somewhere on the "
            "dense grid -- with no entry the grid cannot collapse, this is a "
            "blanket 'the instrument is quantised' claim and could not fail"
        )
    for want, label in (((True, True), "on-path and BLIND"),
                        ((True, False), "on-path and SIGHTED"),
                        ((False, False), "OFF-path")):
        if want not in kinds:
            out.append(
                f"register: no {label} entry -- with every entry on one side "
                "this is a blanket claim wearing a register's clothes, and it "
                "would pass whatever the instrument did"
            )
    return out


# ---------------------------------------------------------------------------
# AGEING RESOLUTION -- what THIS book can resolve, predicted from the book
# (atom D25_ageing_resolution_is_the_harness_calendar)
# ---------------------------------------------------------------------------
# THE POINT OF THE PREDICTOR, and why it is not the drift sweep again. The sweep
# above ANSWERS "did drift k move the reading" by re-scoring; it can only ever
# report on the drifts somebody thought to declare, and it needs the scorer to
# run. This predicts the same answer from the POPULATION and the TRUTH-SIDE
# BUCKET RULE alone -- no scorer, no consumer, no organ -- so the two are
# genuinely independent computations of one quantity and `check_ageing_
# resolution` can put them against each other (R15 independence: a checker
# derived from the thing it checks cannot fail).
#
# The arithmetic is the whole finding in three lines. The organ's dating drift
# `k` shifts what the COMPANY thinks each open invoice's age is (`k < 0` ->
# `age + |k|`, over-ageing; `k > 0` -> `age - k`, under-ageing) while the truth
# side ages from the world's own due date. An ordinal bucket headline changes
# only when some invoice's believed age crosses a bucket BOUNDARY. So the
# smallest company dating error this book can resolve is simply the smallest
# distance from any invoice to the next boundary -- in each direction.
#
# On the flat book that is 9 days one way and 1 the other, which is exactly the
# asymmetry Expert Hour #8 measured by re-scoring. That agreement, checked in
# both directions on both books, is what makes the predictor trustworthy enough
# to travel with a live population whose calendar nobody has swept.
AGEING_RESOLUTION_TARGET_DAYS = 1


def ageing_bucket_boundaries(max_days: int = 400) -> Tuple[int, ...]:
    """The days at which the TRUTH-side dating rule changes bucket, DERIVED by
    walking `truth_side_rule("ageing")` rather than hand-listed as (30, 60, 90).

    Hand-listing them would be the D21 tautology in miniature: an edit to the
    bucket rule would move the boundaries the resolution is measured against
    without moving this list, and the predictor would go on certifying a
    resolution the instrument no longer has."""
    rule = truth_side_rule("ageing")
    out: List[int] = []
    prev = rule(0)
    for d in range(1, max_days + 1):
        cur = rule(d)
        if cur != prev:
            out.append(d)
            prev = cur
    return tuple(out)


def measure_ageing_resolution(
    records: Sequence[PeriodRecord],
    as_of: date,
    boundaries: Optional[Sequence[int]] = None,
) -> Dict[str, object]:
    """The smallest company dating error THIS book's ageing headline could
    resolve, in each direction, predicted from the population alone.

    Returns `{"over_ageing_days", "under_ageing_days", "n_aged", "ages",
    "boundaries"}`. `over_ageing_days` is `k < 0` (the company believes every
    debt is older -- the direction that posts an early dunning letter);
    `under_ageing_days` is `k > 0`. Either is `None` where no invoice in the
    book has a boundary on that side at all, which is a book that cannot
    resolve ANY error in that direction -- distinct from a small number, and
    the callers must not silently read it as one (a fail-open None is the
    shape R15 names third)."""
    bounds = tuple(sorted(ageing_bucket_boundaries() if boundaries is None
                          else boundaries))
    # The set the ageing truth side actually ages: the truly-failed invoices
    # (`score_triad` labels every other case "current" without consulting a
    # date, so no dating drift can move them across a boundary).
    ages = sorted((as_of - r.due_date).days
                  for r in records if r.result == "failed")
    over: List[int] = []
    under: List[int] = []
    for a in ages:
        above = [b for b in bounds if b > a]
        if above:
            over.append(min(above) - a)
        at_or_below = [b for b in bounds if b <= a]
        if at_or_below:
            under.append(a - max(at_or_below) + 1)
    return {
        "over_ageing_days": min(over) if over else None,
        "under_ageing_days": min(under) if under else None,
        "n_aged": len(ages),
        "n_distinct_ages": len(set(ages)),
        "age_span_days": (max(ages) - min(ages)) if ages else None,
        "ages": tuple(sorted(set(ages))),
        "boundaries": bounds,
    }


def check_ageing_resolution(
    resolution: Dict[str, object],
    drift_measurement: Optional[Dict[str, Dict[str, object]]] = None,
    target_days: int = AGEING_RESOLUTION_TARGET_DAYS,
) -> List[str]:
    """Put the predicted resolution on trial and return the VIOLATIONS.

    Two rules, and the second is the one that makes the first mean anything:

    1. THE DELIVERABLE. Atom D25 exists to give the ageing dimension a book
       that resolves a `target_days` dating error in BOTH directions. A book
       that cannot -- the flat book, or a future edit that flattens this one
       back -- fails here by name.
    2. THE AGREEMENT. The prediction must match what the drift sweep MEASURED
       by re-scoring: every declared drift at least as large as the predicted
       resolution must have MOVED the reading, and every declared drift smaller
       than it must NOT have. Two independent computations of one quantity
       disagreeing means one of them is wrong, and neither is allowed to be the
       one that is believed.

    A vacuous book (nothing aged) is a VIOLATION, not a pass -- an empty
    population is exactly how a resolution claim fail-opens.
    """
    out: List[str] = []
    if not resolution["n_aged"]:
        return ["ageing resolution measured over an EMPTY book -- a resolution "
                "claim over no invoices is vacuous, not satisfied"]
    for key, label in (("over_ageing_days", "OVER-ageing (k<0, the early "
                        "dunning letter)"),
                       ("under_ageing_days", "UNDER-ageing (k>0)")):
        got = resolution[key]
        if got is None:
            out.append(
                f"ageing resolution: this book has NO invoice with a bucket "
                f"boundary on the {label} side, so no dating error in that "
                "direction can ever move the headline")
        elif got > target_days:
            out.append(
                f"ageing resolution: the smallest {label} error this book can "
                f"resolve is {got}d, worse than the {target_days}d target -- "
                "the headline is quantised to the harness's calendar again "
                "(atom D25); spread the book across the billing cycle")
    if drift_measurement is None or "ageing" not in drift_measurement:
        return out
    row = drift_measurement["ageing"]
    for k in sorted(set(row["moved"]) | set(row["unmoved"])):
        predicted = resolution["over_ageing_days" if k < 0
                               else "under_ageing_days"]
        if predicted is None:
            continue
        should_move = abs(k) >= predicted
        did_move = k in row["moved"]
        if should_move != did_move:
            out.append(
                f"ageing resolution: drift {k:+d}d was PREDICTED "
                f"{'visible' if should_move else 'invisible'} from this book's "
                f"{predicted}d resolution but MEASURED "
                f"{'visible' if did_move else 'invisible'} by re-scoring -- "
                "the population-side predictor and the drift sweep disagree, "
                "so one of them is describing an instrument that is not there")
    return out


def measure_belief_window_resolution(
    records: Sequence["PeriodRecord"],
    as_of: date,
    window_days: Optional[int] = None,
) -> Dict[str, object]:
    """What company MEMORY error can this book's belief dimensions resolve?
    (atom D27, H27 Expert Hour #9.)

    The two belief dimensions read exactly one company parameter --
    `PaymentObservationConsumer._dd_failure_window_days`, how far back
    `_arrears_risk_belief` still counts an observed failure. An event at age
    `a` days is counted iff `a <= window`, so a company holding a window
    LONGER than the oldest event in the book counts precisely the same events
    as one holding an infinite memory: the parameter is inert, by construction,
    on every population whose span fits inside it.

    PREDICTED FROM THE POPULATION, never from the organ. It uses the WORLD's
    own event dates (`PeriodRecord.due_date`, the value date each observed
    failure carries through the seam) and the harness's own declared window --
    not `_arrears_risk_belief`'s severity thresholds, whose hand-copy was
    exactly the D20 defect. So this is a statement about the BOOK, and it is
    computable for a live `run_phase2b` population no drift sweep has visited.

    The claim is one-directional and stated as such: shortening the memory by
    `<= headroom_days` is PROVABLY invisible (no event changes side), while
    shortening by more MAY be visible -- whether it is depends on whether the
    dropped events carry an account across a severity tier, which is the
    organ's business and not this predictor's. `check_own_drift_resolution`
    cross-checks the provable half against the drift sweep's re-scoring."""
    window = DD_FAILURE_WINDOW_DAYS if window_days is None else window_days
    ages = sorted((as_of - r.due_date).days
                  for r in records if r.result == "failed")
    if not ages:
        return {
            "n_events": 0, "oldest_event_age_days": None,
            "newest_event_age_days": None, "window_days": window,
            "headroom_days": None, "saturated": None,
            "smallest_visible_shortening_days": None,
            "amnesia_floor_window_days": None,
            "predicted_saturates_below_drift": None,
            "predicted_saturates_above_drift": None,
        }
    oldest = ages[-1]
    saturated = window >= oldest
    return {
        "n_events": len(ages),
        "oldest_event_age_days": oldest,
        "newest_event_age_days": ages[0],
        "event_age_span_days": oldest - ages[0],
        "window_days": window,
        # How much memory the company can lose before ANY event changes side.
        "headroom_days": window - oldest,
        # SATURATED: no event in this book can fall out of this window, so
        # every longer memory -- to infinity -- publishes one number.
        "saturated": saturated,
        "smallest_visible_shortening_days": (
            (window - oldest) + 1 if saturated else 1),
        "smallest_visible_lengthening_days": None if saturated else 1,
        # THE OTHER EDGE, which D27 never predicted because the sparse grid
        # held one point below the book and a collapsed run needs two (atom
        # D29). A window BELOW the newest event counts nothing at all, so every
        # shorter memory -- down to total amnesia -- is one company to this
        # dimension. The floor is a property of how far `as_of` sits past the
        # last event, i.e. of AS_OF_BUFFER_DAYS, not of the company.
        "amnesia_floor_window_days": ages[0] - 1,
        "predicted_saturates_below_drift": (ages[0] - 1) - window,
        "predicted_saturates_above_drift": oldest - window,
    }


# ---------------------------------------------------------------------------
# THE CENSUS OF CONFOUNDER-REMOVING CONSTANTS
# (atom D30_the_belief_band_is_this_books_length, H27 Expert Hour #12)
# ---------------------------------------------------------------------------
# WHAT THIS EXISTS TO STOP, and it is the same class three Hours running, one
# level further out. D27 found `DD_FAILURE_WINDOW_DAYS = 400` by tripping over
# it; D29 found `AS_OF_BUFFER_DAYS = 30` by tripping over it. Both comments say
# the constant was chosen to REMOVE A CONFOUNDER -- "generous on purpose",
# "comfortably past" -- and both reasons are sound. Both are also silent
# RESOLUTION decisions, and each was discovered only when an Hour happened to
# sweep across it. There was no census: the set of harness constants that bound
# what this instrument can resolve was being enumerated by accident, one Hour
# at a time, and nobody could say how many were left.
#
# THE FINDING THIS CENSUS PUBLISHES. The two belief dimensions resolve a
# company's failure-memory ONLY between the youngest and oldest invoice age
# this book presents at `as_of`. That interval is not a sensitivity of the
# instrument; it is ARITHMETIC OVER FOUR HARNESS CONSTANTS:
#
#     youngest = AS_OF_BUFFER_DAYS
#     oldest   = AS_OF_BUFFER_DAYS + PERIOD_SPACING_DAYS * (N_PERIODS - 1)
#                                  + BILLING_CYCLE_SPREAD_DAYS - 1
#
# = [30, 92] on the shipped scenario, a band 62 DAYS WIDE, measured identical
# on seeds 7/11/23. D29 attributed the LOWER edge to `AS_OF_BUFFER_DAYS` and
# left the upper one owned by "the company's memory outruns the book" -- which
# is a restatement, not an attribution: the book stops at 92 days because
# N_PERIODS is 3 and PERIOD_SPACING_DAYS is 21, two constants no Hour had
# asked. The upper edge was attributed AWAY FROM THE HARNESS ENTIRELY.
#
# AND THE INSTRUMENT CANNOT RESOLVE THE COMPANY IT SCORES. The scored company
# holds `DD_FAILURE_WINDOW_DAYS = 400` days of memory; the resolvable band tops
# out at 92. So the shipped reading is taken 308 days INSIDE the saturated
# tail: every `belief` and `belief_population_mix` figure this pair publishes
# is read at a point where the one company parameter those dimensions depend on
# is inert by construction. R12: this is REPORTED, never tuned -- the reshape
# is atom D30 and no published number moves in this commit.
#
# CLOSED AT THE CLASS (R10), not at the two constants:
#   * the census KEYSET is derived from `build_scenario`'s own AST -- the
#     constants that build the book -- so a ninth constant added to the
#     scenario and left uncensused RAISES rather than waiting for an Hour to
#     trip over it;
#   * `bounds_resolution` and the EDGE each constant sets are MEASURED by
#     perturbing the predictor, never read from the declaration, so a constant
#     that silently enters the span arithmetic cannot be declared inert (and
#     one declared to bound resolution gets no free credit either);
#   * the predictor is cross-checked against the BUILT book on every seed, so
#     the arithmetic above cannot drift away from the scenario it describes.


def predict_event_age_span_from_constants(
    *,
    as_of_buffer_days: Optional[int] = None,
    n_periods: Optional[int] = None,
    period_spacing_days: Optional[int] = None,
    cycle_spread_days: Optional[int] = None,
) -> Dict[str, int]:
    """The span of invoice AGES this scenario can present at `as_of`, computed
    from the scenario constants ALONE (atom D30).

    Independent of the book by construction: it reads no `PeriodRecord`, no
    draw and no seed, only the four constants `build_scenario` uses to place
    due dates and to choose `as_of`. That is what makes it a second opinion
    rather than a restatement -- `measure_belief_window_resolution` reads the
    same span OFF the built book, and `check_scenario_constant_census` fails if
    the two disagree.

    The identities, straight off `build_scenario`: every account's newest
    invoice is exactly `AS_OF_BUFFER_DAYS` past due (`as_of` is taken from the
    latest due date the CYCLE can produce, not the latest this draw happened to
    make), and the oldest is that plus the whole billing spine -- the periods
    behind it and the account's place in the cycle.
    """
    buf = AS_OF_BUFFER_DAYS if as_of_buffer_days is None else as_of_buffer_days
    n = N_PERIODS if n_periods is None else n_periods
    spacing = (PERIOD_SPACING_DAYS if period_spacing_days is None
               else period_spacing_days)
    spread = (BILLING_CYCLE_SPREAD_DAYS if cycle_spread_days is None
              else cycle_spread_days)
    youngest = int(buf)
    oldest = int(buf) + int(spacing) * (int(n) - 1) + int(spread) - 1
    return {
        "youngest_age_days": youngest,
        "oldest_age_days": oldest,
        "span_days": oldest - youngest,
    }


# WHICH KEYWORD OF THE PREDICTOR CARRIES WHICH CONSTANT. The census perturbs
# the predictor through these, so "does this constant bound resolution" is
# answered by MOVING IT, not by reading a declaration.
_SPAN_PREDICTOR_KNOBS: Dict[str, str] = {
    "AS_OF_BUFFER_DAYS": "as_of_buffer_days",
    "N_PERIODS": "n_periods",
    "PERIOD_SPACING_DAYS": "period_spacing_days",
    "BILLING_CYCLE_SPREAD_DAYS": "cycle_spread_days",
}

_SPAN_EDGES = ("youngest_age_days", "oldest_age_days")


def scenario_constants() -> Tuple[str, ...]:
    """THE CENSUS'S SUBJECT, DERIVED FROM SOURCE (atom D30): every module-level
    constant `build_scenario` reads to build the book.

    Hand-typing this list would supply the very defect the census exists to
    stop -- a constant nobody thought of is exactly the one that has been
    silently setting an edge -- so it comes off `build_scenario`'s AST. A
    constant added to the scenario and left out of `SCENARIO_CONSTANT_CENSUS`
    makes `check_scenario_constant_census` raise, fail-closed.
    """
    module_src = inspect.getsource(sys.modules[__name__])
    tree = ast.parse(module_src)
    consts = {
        t.id
        for node in tree.body if isinstance(node, ast.Assign)
        for t in node.targets
        if isinstance(t, ast.Name) and t.id.isupper() and not t.id.startswith("_")
    }
    builder = next(n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name == "build_scenario")
    return tuple(sorted({n.id for n in ast.walk(builder)
                         if isinstance(n, ast.Name) and n.id in consts}))


SCENARIO_CONSTANT_CENSUS: Dict[str, Dict[str, object]] = {
    # THE FOUR THAT SET THE BAND. `sets_edges` is CHECKED against a
    # perturbation of the predictor, never trusted.
    "AS_OF_BUFFER_DAYS": {
        "bounds_resolution": True,
        "sets_edges": ("youngest_age_days", "oldest_age_days"),
        "owning_atom": "D29_the_as_of_buffer_floors_the_memory_grid",
        "why": (
            "`as_of` sits this far past every account's newest invoice, so no "
            "observed failure is younger than it and a company memory below "
            "it counts NOTHING. Found by tripping over it in Hour #11. It "
            "moves the upper edge too, because every age is measured from an "
            "`as_of` it places -- which is why one owner field could never "
            "have been right."
        ),
    },
    "N_PERIODS": {
        "bounds_resolution": True,
        "sets_edges": ("oldest_age_days",),
        "owning_atom": "D30_the_belief_band_is_this_books_length",
        "why": (
            "THE UPPER EDGE'S REAL OWNER, and the census's own finding. Three "
            "billing periods is why the book stops at 92 days; D29 recorded "
            "that edge as `the company's memory outruns the book`, which "
            "names no constant and attributes the harness's own calendar to "
            "the company being graded."
        ),
    },
    "PERIOD_SPACING_DAYS": {
        "bounds_resolution": True,
        "sets_edges": ("oldest_age_days",),
        "owning_atom": "D30_the_belief_band_is_this_books_length",
        "why": (
            "The other half of the same arithmetic: the oldest invoice is "
            "`(N_PERIODS - 1)` spacings behind the newest. Never asked before "
            "this census."
        ),
    },
    "BILLING_CYCLE_SPREAD_DAYS": {
        "bounds_resolution": True,
        "sets_edges": ("oldest_age_days",),
        "owning_atom": "D25_ageing_resolution_is_the_harness_calendar",
        "why": (
            "D25 introduced the spread as a RESOLUTION fix for the ageing "
            "dimension and measured it there. It widens the BELIEF band too, "
            "by 20 days, and that was never part of D25's claim -- a "
            "resolution constant whose second effect went unrecorded."
        ),
    },
    # THE FOUR THAT DO NOT. Declared so the census is DIFFERENTIAL: a control
    # on which every entry answers the same way cannot discriminate, and the
    # perturbation check fails these if they ever start setting an edge.
    "DD_FAILURE_WINDOW_DAYS": {
        "bounds_resolution": False,
        "sets_edges": (),
        "owning_atom": "D27_belief_window_saturates_on_this_book",
        "why": (
            "NOT A BAND CONSTANT -- it is the ORIGIN the band is measured "
            "from. The book's ages fix where resolution stops; this fixes "
            "where the scored company sits relative to that, which is the "
            "308d of saturated headroom D27 owns. Censused as inert on the "
            "EDGES so the two roles stop being one field."
        ),
    },
    "FIRST_DUE_DATE": {
        "bounds_resolution": False,
        "sets_edges": (),
        "owning_atom": None,
        "why": (
            "Slides the whole book and `as_of` together, so every AGE is "
            "unchanged. The one scenario constant that is genuinely a "
            "relabelling."
        ),
    },
    "PAYMENT_TERMS_DAYS": {
        "bounds_resolution": False,
        "sets_edges": (),
        "owning_atom": "D23_the_latency_grid_resolves_to_the_day",
        "why": (
            "Sets ISSUE dates, not due dates, so it moves no invoice age. It "
            "bounds the DETECTION-LATENCY dimension instead (D23/D24), which "
            "is a resolution claim about a different reading and is registered "
            "there."
        ),
    },
    "BILL_AMOUNT_GBP": {
        "bounds_resolution": False,
        "sets_edges": (),
        "owning_atom": None,
        "why": (
            "A money scale on a book whose every invoice carries it, so it "
            "cancels out of every ratio these dimensions publish and reaches "
            "no date at all."
        ),
    },
}


def measure_scenario_constant_census(
    records: Sequence["PeriodRecord"],
    as_of: date,
    census: Optional[Dict[str, Dict[str, object]]] = None,
) -> Dict[str, object]:
    """MEASURE the census rather than trust it (atom D30).

    Two independent legs, and the census is only worth having because they can
    disagree:

    * PERTURBATION -- move each constant by one day through the predictor and
      record which edges of the age band actually move. This answers
      `bounds_resolution` and `sets_edges` by measurement.
    * CROSS-CHECK -- the predicted band against the band the BUILT book
      presents. The predictor reads only constants; the book is drawn. A
      disagreement means the arithmetic has drifted off the scenario.
    """
    census = SCENARIO_CONSTANT_CENSUS if census is None else census
    base = predict_event_age_span_from_constants()
    moved: Dict[str, Tuple[str, ...]] = {}
    for name in census:
        knob = _SPAN_PREDICTOR_KNOBS.get(name)
        if knob is None:
            moved[name] = ()
            continue
        bumped = predict_event_age_span_from_constants(**{knob: _current(name) + 1})
        moved[name] = tuple(e for e in _SPAN_EDGES if bumped[e] != base[e])
    ages = sorted((as_of - r.due_date).days for r in records)
    window = DD_FAILURE_WINDOW_DAYS
    youngest = ages[0] if ages else None
    oldest = ages[-1] if ages else None
    # THE SCORED COMPANY'S PLACE IN THE BAND IS READ OFF THE BOOK, NOT OFF THE
    # CONSTANTS. `score_triad` also scores live `run_phase2b` populations, whose
    # book these constants do not describe -- and a caveat that quoted the
    # predicted band there would be publishing this scenario's number over
    # somebody else's population, which is the fail-open every Hour since #4 has
    # found in one shape or another. `describes_this_book` is the switch, and
    # the caveat says so out loud when it is False.
    describes = (youngest == base["youngest_age_days"]
                 and oldest == base["oldest_age_days"])
    return {
        "predicted": base,
        "measured_youngest_age_days": youngest,
        "measured_oldest_age_days": oldest,
        "measured_span_days": None if oldest is None else oldest - youngest,
        "describes_this_book": describes,
        "moved_edges": moved,
        "subject": scenario_constants(),
        # R12: REPORTED, not tuned. The scored company's own memory against the
        # top of the band THIS book presents.
        "scored_company_window_days": window,
        "scored_company_headroom_days": None if oldest is None else window - oldest,
        "scored_company_is_inert": None if oldest is None else window >= oldest,
    }


def _current(name: str) -> int:
    """The live value of a scenario constant, by name -- read off the module so
    a perturbation cannot quietly test a stale copy."""
    return int(getattr(sys.modules[__name__], name))


def check_scenario_constant_census(
    measured: Dict[str, object],
    census: Optional[Dict[str, Dict[str, object]]] = None,
    register: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """The census's rules, all four able to fail on their own defect (atom
    D30, R15). Returns violations; empty means the census holds."""
    census = SCENARIO_CONSTANT_CENSUS if census is None else census
    register = DIMENSION_DRIFT_RESOLUTION if register is None else register
    out: List[str] = []
    out += _check_census_is_complete(measured, census)
    out += _check_census_edges_are_measured(measured, census)
    out += _check_predictor_matches_the_book(measured)
    out += _check_edge_owners_are_censused(census, register)
    return out


def _check_census_is_complete(measured: Dict[str, object],
                              census: Dict[str, Dict[str, object]]) -> List[str]:
    """FAIL-CLOSED ON THE KEYSET. The subject comes off `build_scenario`'s AST,
    so a constant added to the scenario and never censused raises here instead
    of waiting for an Hour to trip over it -- which is how the first two were
    found."""
    subject = set(measured.get("subject") or ())
    out: List[str] = []
    for name in sorted(subject - set(census)):
        out.append(
            f"{name}: `build_scenario` reads it and the census does not name "
            "it -- an uncensused scenario constant is exactly the shape "
            "D27 and D29 were each found in, one Hour at a time"
        )
    for name in sorted(set(census) - subject):
        out.append(
            f"{name}: censused but `build_scenario` no longer reads it -- a "
            "census entry outliving its constant is a claim about a scenario "
            "that is not there"
        )
    return out


def _check_census_edges_are_measured(
        measured: Dict[str, object],
        census: Dict[str, Dict[str, object]]) -> List[str]:
    """DECLARATION vs PERTURBATION, both directions. A constant that silently
    enters the span arithmetic cannot be declared inert, and one declared to
    bound resolution gets no free credit for saying so."""
    moved: Dict[str, Tuple[str, ...]] = measured.get("moved_edges") or {}
    out: List[str] = []
    for name, entry in sorted(census.items()):
        got = tuple(moved.get(name) or ())
        declared = tuple(entry.get("sets_edges") or ())
        if set(got) != set(declared):
            out.append(
                f"{name}: declared to set {list(declared)} and moving it one "
                f"day moves {list(got)} -- the census is describing an "
                "arithmetic that is not the predictor's"
            )
        if bool(entry.get("bounds_resolution")) != bool(got):
            out.append(
                f"{name}: bounds_resolution={entry.get('bounds_resolution')} "
                f"and the perturbation moved {list(got)} -- a constant's "
                "effect on the band is measured here, never declared"
            )
        if got and not entry.get("owning_atom"):
            out.append(
                f"{name}: it sets {list(got)} and no atom owns it -- an "
                "unowned resolution constant is a silent one, which is the "
                "whole class"
            )
    return out


def _check_predictor_matches_the_book(measured: Dict[str, object]) -> List[str]:
    """THE INDEPENDENCE LEG. The predictor reads constants and no draw; the
    book is built. If the two disagree the arithmetic has drifted off the
    scenario it claims to describe, and every ownership claim above is being
    made about a band nobody presents."""
    pred = measured.get("predicted") or {}
    out: List[str] = []
    for key, got_key, label in (
        ("youngest_age_days", "measured_youngest_age_days", "youngest"),
        ("oldest_age_days", "measured_oldest_age_days", "oldest"),
    ):
        got = measured.get(got_key)
        if got is None:
            out.append(
                f"the book presents no invoice at all, so the {label} edge "
                "cannot be cross-checked -- an unmeasured band reads exactly "
                "like an agreeing one"
            )
        elif got != pred.get(key):
            out.append(
                f"the constants predict a {label} invoice age of "
                f"{pred.get(key)}d and this book presents {got}d -- the span "
                "arithmetic has drifted off `build_scenario`"
            )
    return out


def _check_edge_owners_are_censused(
        census: Dict[str, Dict[str, object]],
        register: Dict[str, Dict[str, object]]) -> List[str]:
    """THE DEFECT THIS HOUR FOUND, closed as a rule. Every saturation edge the
    drift register attributes must be attributed to an atom the census puts on
    that edge -- so an edge can no longer be owned by a sentence about the
    company ("its memory outruns the book") while a harness constant sets it.
    """
    owners = {
        edge: {str(e["owning_atom"]) for e in census.values()
               if edge in tuple(e.get("sets_edges") or ()) and e.get("owning_atom")}
        for edge in _SPAN_EDGES
    }
    pairs = (("own_saturation_atom_below", "youngest_age_days"),
             ("own_saturation_atom_above", "oldest_age_days"))
    out: List[str] = []
    for dim, entry in sorted(register.items()):
        if entry.get("own_drift") != "organ_failure_window_drift_days":
            continue
        for field, edge in pairs:
            atom = entry.get(field)
            if atom is None:
                continue
            if str(atom) not in owners[edge]:
                out.append(
                    f"{dim}.{field}={atom} names an atom the census does not "
                    f"put on the {edge} edge (censused owners: "
                    f"{sorted(owners[edge])}) -- that edge is set by a harness "
                    "constant, and an owner outside the census attributes the "
                    "harness's own calendar to the company being graded"
                )
    return out


def scenario_constant_census_caveat(measured: Dict[str, object]) -> str:
    """The band, its owning constants and the scored company's place in it --
    re-derived from the measurement each call, never quoted (atom D30).

    Attributes the band to the constants ONLY where they demonstrably describe
    the book in hand. On a live `run_phase2b` population they do not, and
    quoting this scenario's [30, 92] over somebody else's book would be the
    fail-open shape, not the caveat."""
    band_owners = sorted(
        n for n, e in SCENARIO_CONSTANT_CENSUS.items() if e.get("bounds_resolution"))
    head = "THE BAND IS THE BOOK'S LENGTH (atom D30, H27 Expert Hour #12). "
    if measured.get("measured_oldest_age_days") is None:
        return head + (
            "This population presents no invoice at all, so it has no age band "
            "and nothing about the belief dimensions' resolution can be read "
            "off it."
        )
    body = (
        "Both belief dimensions resolve a company memory error only between "
        f"{measured['measured_youngest_age_days']}d and "
        f"{measured['measured_oldest_age_days']}d -- a band "
        f"{measured['measured_span_days']}d wide, and a band is a property of "
        "how long the book is, never a sensitivity of the instrument. "
    )
    if measured.get("describes_this_book"):
        body += (
            f"On THIS book those edges are arithmetic over {band_owners}: "
            "four harness constants, three of which no Expert Hour had asked "
            "before the census. "
        )
    else:
        body += (
            "This is NOT the offline scenario's book, so the census's "
            f"constants ({band_owners}) do not attribute these edges -- the "
            "band above is measured here and owned by whatever placed this "
            "population's invoices. "
        )
    if measured.get("scored_company_is_inert"):
        body += (
            "AND THE SCORED COMPANY SITS OUTSIDE IT: it holds "
            f"{measured['scored_company_window_days']}d of memory, "
            f"{measured['scored_company_headroom_days']}d past the top of the "
            "band, so every belief figure here is read at a point where the "
            "one company parameter these dimensions depend on is inert by "
            "construction (reported, never tuned -- R12)."
        )
    return head + body


# ---------------------------------------------------------------------------
# THE READER'S OWN RESOLUTION, and each belief figure's OWN floor
# (atom D33, H27 Expert Hour #15, 2026-08-11)
#
# HOUR #14 LEFT THIS AS LEAD 2. Its contract checks one cell's number against
# the published figure -- `detection_latency`/recon, the only cell whose reading
# is day-linear either way -- and the other six moving cells carry caveats whose
# numbers are BANDS and EDGES that nothing compares with the figure they ride
# on. Asked of the two belief cells, the answer is that the number is not the
# figure's at all:
#
#   * `measure_belief_window_resolution` computes `smallest_visible_shortening_
#     days` = headroom + 1, the smallest window shortening that drops any
#     observed event out of the company's memory. Its own docstring is careful
#     -- shortening by more "MAY be visible ... which is the organ's business
#     and not this predictor's" -- and NOBODY EVER ASKED THE ORGAN.
#   * `belief_resolution_caveat` published that bound as "the smallest memory
#     error IT can resolve at all", on BOTH belief dimensions, byte-identical.
#     Measured (n=300): the bound is 310/309/309 on seeds 7/11/23 while `belief`
#     resolves 310/310/309 and `belief_population_mix` resolves 310/314/312. So
#     the sentence is a day out on one figure and FIVE days out on the other,
#     and two figures whose measured resolution differs by four days on one seed
#     carried one number between them.
#
# A bound on what ANY figure here could resolve is a real and useful thing to
# publish; what it may not do is stand in the sentence where the figure's own
# resolution goes. That is the D32 wrong-subject class one register over, and
# this time the subject is not an adjacent reading but the BOOK.
#
# WHY THE EPSILON IS NOT A MAGIC NUMBER. Both belief gaps reach their reader
# through a `.4f` render (`background.gap_metric.format_belief_summary` and the
# live writer's own mix line), so a difference below half a step of that is not
# a reading at all -- and bit-equality, which every collapse measurement in
# this module uses, counts one. Measured live: `belief_population_mix` at seed
# 11 "moves" at drifts -310..-313 by 1.4e-17, which is what put its declared
# saturation edge at -309 when the reader's own precision puts it at -313. That
# predicate is D33's reshape and is deliberately NOT changed here.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PUBLISHED_GAP_CONSUMERS -- the precision EACH figure reaches ITS OWN reader
# at (atom D34, H27 Expert Hour #16)
#
# Hour #15 installed the epsilon as "the reader's own precision, not a
# tolerance", re-read out of the consumers' source so that "a consumer that
# starts publishing 6dp fails the control instead of leaving the epsilon
# stale". Measured one Hour later, it failed neither way:
#
#   * IT COULD NOT FAIL ON THE CHANGE IT WAS BUILT FOR. The re-read collected
#     EVERY `.Nf` in the anchored function and asked only whether 4 was among
#     them -- and `format_belief_summary` renders three other RATES at `.4f`
#     and the mean steps at `.2f`, so it already returned {2, 4} rather than a
#     precision. Mutated live: move the BELIEF GAP's own render to `.6f`, the
#     set becomes {2, 4, 6}, and the check still passes. A membership test over
#     every number in a function is not a check on the one number the figure is.
#   * IT WAS THE BELIEF READER'S PRECISION, DECLARED AS EVERY READER'S. The
#     keyset was two hand-typed consumer sites, both BELIEF, while five
#     dimensions are published. Read off the shipped renderers: `detection` and
#     both belief figures 4dp -- and `ageing` **3dp** (`format_ageing_summary`
#     renders `balanced_bucket_displacement`, which IS the gap, at `.3f`) and
#     `detection_latency` **2dp** (`format_detection_latency_summary`:
#     `f"{mean:.2f} days mean"`). One global constant, ten times too fine for
#     one published figure and a HUNDRED times too fine for another.
#
# Not merely latent, either: `_own_floor_clause` publishes "at the 4dp every
# consumer renders these gaps at" to the reader of both belief numbers, and
# that sentence is false of two of the five figures this module publishes.
#
# So the precision is PER DIMENSION, the keyset is DERIVED from
# `published_dimensions`, and each number is read off the format spec that
# renders THAT DIMENSION'S GAP -- through the local alias where the renderer
# uses one (`mean = c.get("mean_lag_days")`), and through the COMPONENT where
# the gap reaches the reader as one, with that alias checked NUMERICALLY
# against the gap rather than believed by name.
#
# WHAT IT DOES NOT CHANGE (R12). Measured at each dimension's OWN reader
# precision, every declared band, edge and collapse run in
# `DIMENSION_DRIFT_RESOLUTION` and `ORGAN_QUERY_GRID` still holds exactly --
# under the terms knob and the recon knob, on the dense book-derived grids,
# n=300, seeds 7/11/23. That answers Hour #15's lead 1: the bit-equality
# divergence atom D33 owns is confined to the belief cells, and no published
# number moves here.
# ---------------------------------------------------------------------------

# WHERE EACH PUBLISHED FIGURE MEETS ITS READER. `decimals` is the DECLARATION;
# `measure_published_reading_precision` reads the real one out of the renderer's
# own source and `check_published_reading_precision` fails on the difference --
# a declared precision nobody re-reads is the claim this atom is about.
#
# `carrier` says HOW the gap reaches the render site, because it does not
# always arrive as `.gap`:
#   ("gap", None)          -- the render formats the `GapResult`'s own `.gap`
#   ("component", "<key>") -- the render formats a COMPONENT that carries the
#                             gap (the ageing headline is published as
#                             `balanced_bucket_displacement`, the latency
#                             headline as `mean_lag_days`). The claim that the
#                             component IS the gap is checked numerically
#                             against a real scoring, never taken on the name.
PUBLISHED_GAP_CONSUMERS: Dict[str, Dict[str, object]] = {
    "belief": {
        "module": "background/gap_metric.py",
        "renderer": "format_belief_summary",
        "carrier": ("gap", None),
        "decimals": 4,
    },
    "belief_population_mix": {
        # NOT a formatter of its own: the mix figure is rendered inline by the
        # live writer, which is why the pre-Hour re-read had to match it by
        # LINE rather than by function.
        "module": "background/live_payment_triad.py",
        "renderer": "measure_and_write",
        "carrier": ("gap", None),
        "decimals": 4,
    },
    "detection": {
        "module": "background/gap_metric.py",
        "renderer": "format_detection_summary",
        "carrier": ("gap", None),
        "decimals": 4,
    },
    "detection_latency": {
        # A HUNDRED TIMES COARSER THAN THE GLOBAL CONSTANT CLAIMED. The reader
        # of this figure is given two decimals of a number around 2.34 days.
        "module": "tools/couple_w2_11_d5.py",
        "renderer": "format_detection_latency_summary",
        "carrier": ("component", "mean_lag_days"),
        "decimals": 2,
    },
    "ageing": {
        # TEN TIMES COARSER. `format_ageing_summary` never renders `.gap` at
        # all -- the headline reaches the reader as the component.
        "module": "background/gap_metric.py",
        "renderer": "format_ageing_summary",
        "carrier": ("component", "balanced_bucket_displacement"),
        "decimals": 3,
    },
}


def published_reading_decimals(dimension: str,
                               register: Optional[Dict[str, Dict[str, object]]] = None) -> int:
    """The decimal places THIS figure's own consumer renders it at (atom D34).

    A dimension nobody declared RAISES rather than falling back to a house
    default: the fallback IS the defect this atom closes -- a global default is
    exactly what put the belief reader's precision on the latency figure.
    """
    register = PUBLISHED_GAP_CONSUMERS if register is None else register
    entry = register.get(dimension)
    if entry is None:
        raise AssertionError(
            f"`{dimension}` has no entry in PUBLISHED_GAP_CONSUMERS, so the "
            "precision its reader is given is UNKNOWN -- and assuming the "
            "house default is atom D34's defect (the belief reader's 4dp was "
            "assumed for a figure published at 2dp). Declare its consumer."
        )
    return int(entry["decimals"])


def published_reading_epsilon(dimension: Optional[str] = None,
                              *,
                              decimals: Optional[int] = None) -> float:
    """HALF A STEP of the precision THIS figure's reader is given (atom D33,
    made per-figure by atom D34).

    A difference smaller than this cannot appear in that figure's published
    rendering, so counting it as one company being told apart from another is
    the D28 fail-open in another costume: an instrument that has stopped
    reading, recorded as resolution.

    A caller that names NEITHER a dimension nor an explicit precision gets an
    explicit REFUSAL, on the `_own_floor_clause` precedent: the figures do not
    share a precision (2dp to 4dp across the five), so a default would hand one
    figure's reader-step to another -- which is how this atom was found.
    """
    if decimals is None:
        if dimension is None:
            raise AssertionError(
                "published_reading_epsilon() was called without naming a "
                "figure. The five published dimensions do NOT share a reader "
                "precision (detection/belief/belief_population_mix 4dp, ageing "
                "3dp, detection_latency 2dp -- measured out of their own "
                "renderers, atom D34), so there is no epsilon to return that "
                "is not some other figure's."
            )
        decimals = published_reading_decimals(dimension)
    return 0.5 * (10.0 ** -int(decimals))


def _format_spec_decimals(node: object) -> Optional[int]:
    """The N of a `.Nf` render, or None where the spec is not a fixed-point one.

    A spec this cannot read is NOT a precision it may assume -- it returns None
    and the caller raises, because an unreadable render is an unmeasured one.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        text = node.value
    elif isinstance(node, ast.JoinedStr):
        if any(not isinstance(p, ast.Constant) for p in node.values):
            return None
        text = "".join(str(p.value) for p in node.values)
    else:
        return None
    m = re.fullmatch(r"[^.]*\.(\d+)f", text.strip())
    return int(m.group(1)) if m else None


def _is_gap_carrier(node: object, dimension: str) -> bool:
    """Whether this expression IS the named dimension's gap.

    `result.gap` inside that dimension's own renderer is it; `result[<dim>].gap`
    is it only for THAT key, which is what lets one shared function (the live
    writer's `measure_and_write`) render several figures without this control
    picking up a sibling's precision -- the D32 wrong-subject rule applied to
    the render site.
    """
    if not (isinstance(node, ast.Attribute) and node.attr == "gap"):
        return False
    base = node.value
    if isinstance(base, ast.Subscript):
        key = base.slice
        if isinstance(key, ast.Index):        # pragma: no cover - py<3.9 shape
            key = key.value                   # type: ignore[attr-defined]
        return isinstance(key, ast.Constant) and key.value == dimension
    return True


def _is_component_carrier(node: object, component: str) -> bool:
    """Whether this expression reads the named component -- `c.get("k")`,
    `c["k"]`, or `result.components.get("k")`."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "get" and node.args:
        first = node.args[0]
        return isinstance(first, ast.Constant) and first.value == component
    if isinstance(node, ast.Subscript):
        key = node.slice
        if isinstance(key, ast.Index):        # pragma: no cover - py<3.9 shape
            key = key.value                   # type: ignore[attr-defined]
        return isinstance(key, ast.Constant) and key.value == component
    return False


def _find_renderer(tree: ast.AST, name: str) -> Optional[ast.AST]:
    """The renderer by name ANYWHERE in the module -- the mix figure's is a
    METHOD, which is why a top-level `def <name>` scan could not find it and the
    pre-Hour control fell back to matching lines."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name == name:
            return node
    return None


def measure_published_reading_precision(
    *,
    register: Optional[Dict[str, Dict[str, object]]] = None,
    repo_root: Optional[Path] = None,
    result: Optional[Dict[str, object]] = None,
) -> Dict[str, Dict[str, object]]:
    """READ EACH FIGURE'S REND PRECISION OFF ITS OWN CONSUMER'S SOURCE (D34).

    Returns, per dimension: `decimals` (the render specs found for THIS gap),
    `declared_decimals`, `epsilon`, and -- for a component carrier -- whether
    that component really is the gap and by how much it differs.

    Everything this cannot read RAISES rather than returning an empty row: an
    absent consumer file, a renderer that is not there, or a gap with no
    fixed-point render at all is an UNAVAILABLE check, which is a FAILED check
    (R15). The pre-Hour version returned `()` for a missing file and its caller
    read that as agreement.
    """
    register = PUBLISHED_GAP_CONSUMERS if register is None else register
    root = Path(__file__).resolve().parents[1] if repo_root is None else Path(repo_root)
    out: Dict[str, Dict[str, object]] = {}
    for dim in sorted(register):
        entry = register[dim]
        rel, fn_name = str(entry["module"]), str(entry["renderer"])
        kind, component = tuple(entry["carrier"])          # type: ignore[misc]
        path = root / rel
        if not path.exists():
            raise AssertionError(
                f"`{dim}` declares its consumer at {rel} and that file is not "
                "there -- an unreadable consumer is an UNMEASURED precision, "
                "never an agreeing one (the pre-Hour re-read returned an empty "
                "tuple here and passed)"
            )
        fn = _find_renderer(ast.parse(path.read_text()), fn_name)
        if fn is None:
            raise AssertionError(
                f"`{dim}` declares its render in {rel}::{fn_name} and no such "
                "function exists -- a renderer nobody can find cannot have "
                "been read"
            )
        # ONE LEVEL OF LOCAL ALIAS. `format_detection_latency_summary` renders
        # `mean`, assigned from the component two lines up; a walker that only
        # matched the carrier expression itself would find no render at all and
        # would have to guess.
        aliases = set()
        for node in ast.walk(fn):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            if kind == "gap" and _is_gap_carrier(node.value, dim):
                aliases.add(target.id)
            elif kind == "component" and _is_component_carrier(
                    node.value, str(component)):
                aliases.add(target.id)

        def _is_carrier(node: object) -> bool:
            if isinstance(node, ast.Name) and node.id in aliases:
                return True
            if kind == "gap":
                return _is_gap_carrier(node, dim)
            return _is_component_carrier(node, str(component))

        found: Dict[int, List[str]] = {}
        for node in ast.walk(fn):
            # (a) f"{x:.Nf}"
            if isinstance(node, ast.FormattedValue) and _is_carrier(node.value):
                d = _format_spec_decimals(node.format_spec)
                if d is not None:
                    found.setdefault(d, []).append("f-string")
            # (b) format(x, ".Nf")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "format" and len(node.args) == 2 \
                    and _is_carrier(node.args[0]):
                d = _format_spec_decimals(node.args[1])
                if d is not None:
                    found.setdefault(d, []).append("format()")
            # (c) HELPER("<component>", ".Nf") -- the ageing headline reaches
            #     its reader through `_num(key, fmt)`, so the carrier is a
            #     CONSTANT argument rather than an expression.
            elif isinstance(node, ast.Call) and kind == "component" \
                    and len(node.args) >= 2 \
                    and isinstance(node.args[0], ast.Constant) \
                    and node.args[0].value == component:
                for arg in node.args[1:]:
                    d = _format_spec_decimals(arg)
                    if d is not None:
                        found.setdefault(d, []).append("helper")
        if not found:
            raise AssertionError(
                f"`{dim}`: no fixed-point render of its gap found in "
                f"{rel}::{fn_name} (carrier {kind}/{component!r}). A figure "
                "whose render this cannot read has an UNMEASURED reader "
                "precision, and every band certified against it would be "
                "certified against a guess"
            )
        row: Dict[str, object] = {
            "module": rel,
            "renderer": fn_name,
            "carrier": (kind, component),
            "decimals": tuple(sorted(found)),
            "sites": {d: tuple(v) for d, v in sorted(found.items())},
            "declared_decimals": int(entry["decimals"]),
            "epsilon": published_reading_epsilon(decimals=int(entry["decimals"])),
            "carrier_is_the_gap": None,
            "carrier_gap_delta": None,
        }
        # THE ALIAS, MEASURED. "`balanced_bucket_displacement` is the ageing
        # gap" is a claim about arithmetic in another module; a component that
        # has drifted from the gap would put this control's precision on a
        # number the reader is not being given.
        if kind == "component" and result is not None:
            gap = result[dim].gap                          # type: ignore[index]
            got = result[dim].components.get(str(component))   # type: ignore[index]
            if gap is None or got is None:
                row["carrier_is_the_gap"] = False
                row["carrier_gap_delta"] = None
            else:
                delta = abs(float(got) - float(gap))
                row["carrier_is_the_gap"] = delta <= published_reading_epsilon(
                    decimals=int(entry["decimals"]))
                row["carrier_gap_delta"] = delta
        out[dim] = row
    return out


def check_published_reading_precision(
    measured: Dict[str, Dict[str, object]],
    published: Optional[Sequence[str]] = None,
) -> List[str]:
    """Put every declared reader precision on trial against the source (D34).

    The keyset is DERIVED from `published_dimensions` when it is supplied, so
    both ways a register stops describing the code RAISE: a figure published
    with no consumer entry has an unknown reader precision (and would be handed
    a default -- this atom's defect), and an entry for a figure nobody publishes
    reads exactly like a live one.
    """
    if published is not None:
        missing = sorted(set(published) - set(measured))
        if missing:
            raise AssertionError(
                f"published {missing} with no PUBLISHED_GAP_CONSUMERS entry -- "
                "the precision those readers are given is undeclared, and the "
                "house default is what put a 4dp epsilon on a 2dp figure"
            )
        orphan = sorted(set(measured) - set(published))
        if orphan:
            raise AssertionError(
                f"PUBLISHED_GAP_CONSUMERS declares {orphan}, which "
                "`published_dimensions` does not publish -- an entry for a "
                "figure nobody renders is the fail-silent shape this register "
                "refuses"
            )
    out: List[str] = []
    for dim in sorted(measured):
        row = measured[dim]
        decimals = tuple(row["decimals"])                  # type: ignore[arg-type]
        declared = row["declared_decimals"]
        if len(decimals) > 1:
            out.append(
                f"{dim}: its gap is rendered at {list(decimals)} decimals in "
                f"{row['module']}::{row['renderer']} -- one figure with two "
                "reader precisions has no epsilon, and picking either is the "
                "guess this control exists to refuse"
            )
        elif decimals[0] != declared:
            out.append(
                f"{dim}: declares {declared}dp and "
                f"{row['module']}::{row['renderer']} renders its gap at "
                f"{decimals[0]}dp -- every band certified against the declared "
                "epsilon was certified at "
                f"{10.0 ** (decimals[0] - int(declared)):g}x the reader's step"
            )
        kind = tuple(row["carrier"])[0]                    # type: ignore[arg-type]
        if kind == "component":
            state = row["carrier_is_the_gap"]
            if state is None:
                out.append(
                    f"{dim}: reaches its reader through the component "
                    f"{tuple(row['carrier'])[1]!r} and NOTHING checked that "
                    "component against the gap -- an unavailable check is a "
                    "failed check (R15), because a component that has drifted "
                    "puts this precision on a number nobody is shown"
                )
            elif state is not True:
                out.append(
                    f"{dim}: publishes {tuple(row['carrier'])[1]!r} as its "
                    "headline and that component differs from the gap by "
                    f"{row['carrier_gap_delta']!r} -- more than the reader's "
                    "own step, so it is not the figure this precision is about"
                )
    return out


# The knob both belief dimensions read, and the ONLY one that reaches them
# (PUBLISHED_FIGURE_CAVEAT_CONTRACT measures the other two inert there).
BELIEF_FLOOR_KNOB = "organ_failure_window_drift_days"

# The two figures that carried ONE resolution sentence between them.
BELIEF_FLOOR_DIMENSIONS = ("belief", "belief_population_mix")


def measure_published_resolution_floor(
    *,
    dimensions: Sequence[str] = BELIEF_FLOOR_DIMENSIONS,
    knob: str = BELIEF_FLOOR_KNOB,
    n_customers: int = 300,
    seeds: Sequence[int] = RESOLUTION_SEEDS,
    epsilon: Optional[float] = None,
    runner: Optional[Callable[[str, int, int], tuple]] = None,
) -> Dict[str, Dict[str, object]]:
    """THE SMALLEST COMPANY ERROR EACH PUBLISHED FIGURE ACTUALLY RESOLVES, per
    dimension, measured through its own shipped scorer (atom D33).

    The grid is the BOOK's (the D29/D31 rule): it starts one day INSIDE the
    book's own provable bound -- where nothing may move, and a reading there
    would mean something other than the memory window is driving the figure --
    and walks outward by at most the book's own event-age span, which is what
    sets the band in the first place.

    Returns, per dimension: `floor_days` (the smallest |drift| whose reading
    differs READABLY on EVERY seed), `per_seed_floor_days`, the
    `bit_equality_floor_days` the current collapse predicate would report, and
    `book_bound_days` -- the number the caveat used to publish as the figure's
    own.
    """
    # PER FIGURE, NOT PER MODULE (atom D34). The epsilon was one global
    # constant read out of the two BELIEF consumers; both belief figures are
    # rendered at 4dp so nothing here moves, but the same call on `ageing` or
    # `detection_latency` would have measured their floors at 10x and 100x the
    # step their own readers are given.
    def _eps_for(dim: str) -> float:
        return (published_reading_epsilon(dim) if epsilon is None
                else float(epsilon))

    if runner is None:
        def runner(knob_name: str, seed: int, k: int) -> tuple:
            key = (n_customers, seed, knob_name, k)
            if key not in _OWN_RESOLUTION_SCORES:
                recs, cons, _ledger, as_of = build_scenario(
                    n_customers, seed=seed, **{knob_name: k})
                _OWN_RESOLUTION_SCORES[key] = (
                    recs, score_triad(recs, cons, as_of), as_of)
            return _OWN_RESOLUTION_SCORES[key]

    base: Dict[int, tuple] = {s: runner(knob, s, 0) for s in seeds}
    books = {s: measure_belief_window_resolution(base[s][0], base[s][2])
             for s in seeds}
    if any(b.get("smallest_visible_shortening_days") is None for b in books.values()):
        raise AssertionError(
            "no book bound to search outward from -- a population with no "
            "observed failure event cannot bound either belief figure, and "
            "measuring a floor against no bound would be a free pass"
        )
    # THE GRID, DERIVED FROM THE BOOK: one day inside the tightest bound, out to
    # the widest bound plus the book's own event span.
    inside = -(min(int(b["smallest_visible_shortening_days"]) for b in books.values()) - 1)
    outer = -(max(int(b["smallest_visible_shortening_days"]) for b in books.values())
              + max(int(b["event_age_span_days"] or 0) for b in books.values()))
    grid = tuple(range(inside, outer - 1, -1))

    readings: Dict[Tuple[str, int, int], object] = {}
    for s in seeds:
        for k in grid:
            res = runner(knob, s, k)[1]
            for dim in dimensions:
                readings[(dim, s, k)] = res[dim].gap

    out: Dict[str, Dict[str, object]] = {}
    for dim in dimensions:
        eps = _eps_for(dim)
        base_gap = {s: base[s][1][dim].gap for s in seeds}

        def _readable(s: int, k: int, tol: float) -> Optional[bool]:
            got, b = readings[(dim, s, k)], base_gap[s]
            if got is None or b is None:
                # An undefined reading is not a resolution (the D28 fail-open).
                return None
            if tol <= 0.0:
                # BIT-EQUALITY, the predicate every collapse measurement in this
                # module uses -- kept here as the witness, never as the reading.
                return got != b
            return abs(float(got) - float(b)) >= tol

        def _floor(tol: float) -> Optional[int]:
            for k in grid:
                states = [_readable(s, k, tol) for s in seeds]
                if all(st is True for st in states):
                    return abs(k)
            return None

        per_seed: Dict[int, Optional[int]] = {}
        for s in seeds:
            per_seed[s] = next((abs(k) for k in grid
                                if _readable(s, k, eps) is True), None)
        floor = _floor(eps)
        beyond = (None if floor is None else all(
            _readable(s, k, eps) is True
            for s in seeds for k in grid if abs(k) >= floor))
        out[dim] = {
            "knob": knob,
            "seeds": tuple(seeds),
            "grid": grid,
            "epsilon": eps,
            "floor_days": floor,
            "per_seed_floor_days": per_seed,
            # WHAT BIT-EQUALITY WOULD HAVE SAID. Where these two differ, the
            # register's declared collapse runs and saturation edges are
            # resting on a difference no reader can see -- atom D33's reshape.
            "bit_equality_floor_days": _floor(0.0),
            "bit_equality_per_seed_floor_days": {
                s: next((abs(k) for k in grid
                         if _readable(s, k, 0.0) is True), None)
                for s in seeds
            },
            "book_bound_days": {
                s: int(books[s]["smallest_visible_shortening_days"])
                for s in seeds
            },
            "readable_at_every_drift_beyond_floor": beyond,
            "undefined_readings": tuple(
                k for k in grid
                if any(_readable(s, k, eps) is None for s in seeds)),
        }
    # THE PROBE ITSELF. A knob that had stopped drifting the company would put
    # every floor at None and certify nothing -- the vacuity shape this module
    # has now produced in seven registers.
    if all(row["floor_days"] is None for row in out.values()):
        raise AssertionError(
            f"`{knob}` moved NO published figure readably anywhere on a "
            f"book-derived grid of {len(grid)} counterfactual companies -- an "
            "inert probe cannot measure a resolution floor, and reporting one "
            "from it would be the free pass this measurement exists to refuse"
        )
    return out


def check_published_resolution_floor(
    measured: Dict[str, Dict[str, object]],
    register: Optional[Dict[str, Dict[str, object]]] = None,
) -> List[str]:
    """Put every declared `own_readable_resolution_floor_days` on trial against
    the measurement, EXACTLY (atom D33).

    Exact, on the D25/D30 rule: a floor declared loosely ("at least 300d") is a
    sentence that survives any reshape, and this atom exists because a loose
    claim about a figure's resolution went unchecked for six Hours.
    """
    register = DIMENSION_DRIFT_RESOLUTION if register is None else register
    declared = {d for d, e in register.items()
                if e.get("own_readable_resolution_floor_days") is not None}
    missing = sorted(set(measured) - declared)
    if missing:
        raise AssertionError(
            f"measured a published resolution floor for {missing} and the "
            "register declares none -- an undeclared floor reads exactly like "
            "an absent limit, and the caveat then has nothing to state but the "
            "book's bound, which is atom D33's finding"
        )
    orphan = sorted(declared - set(measured))
    if orphan:
        raise AssertionError(
            f"register declares a resolution floor for {orphan} that nothing "
            "measured -- a declaration nobody sweeps is the fail-silent shape "
            "this register refuses"
        )
    out: List[str] = []
    for dim in sorted(measured):
        row, entry = measured[dim], register[dim]
        got = row["floor_days"]
        want = entry.get("own_readable_resolution_floor_days")
        if got is None:
            out.append(
                f"{dim}: declares a readable resolution floor of {want}d and "
                "the sweep found NO readable movement anywhere on the "
                "book-derived grid -- a figure that resolves nothing must say "
                "so, not name a number"
            )
        elif int(got) != int(want):
            out.append(
                f"{dim}: declares its published figure resolves no memory "
                f"error smaller than {want}d and the sweep measures {got}d "
                f"(per seed {row['per_seed_floor_days']}, epsilon "
                f"{row['epsilon']:g}) -- a resolution claim that is not this "
                "figure's is atom D33's finding restated"
            )
        # THE BOOK BOUND IS A BOUND, and this is where that is enforced rather
        # than asserted in prose: a figure may be BLINDER than the book proves
        # it must be, never sharper.
        for seed, bound in sorted(row["book_bound_days"].items()):
            per = row["per_seed_floor_days"].get(seed)
            if per is not None and int(per) < int(bound):
                out.append(
                    f"{dim}: reads a difference at {per}d of forgetting on "
                    f"seed {seed} where the book proves no observed event can "
                    f"change side inside {bound}d -- so something other than "
                    "the memory window is moving this figure"
                )
        # THE NOISE WITNESS, kept MEASURED (atom D33). Every collapse run and
        # saturation edge in this module is derived with bit-equality, so where
        # the two predicates disagree the register's declared edges are resting
        # on a difference no consumer can render. Declared exactly, and its
        # owner is required exactly where the divergence is real -- a named
        # owner with no divergence is a debt entry outliving its debt.
        bit, want_bit = (row["bit_equality_floor_days"],
                         entry.get("own_bit_equality_floor_days"))
        if want_bit is None:
            out.append(
                f"{dim}: no `own_bit_equality_floor_days` declared -- the "
                "predicate every collapse measurement here uses is unmeasured "
                "on this dimension, and an unmeasured predicate reads exactly "
                "like an honest one"
            )
        elif bit is None or int(bit) != int(want_bit):
            out.append(
                f"{dim}: declares bit-equality reports {want_bit}d and it "
                f"measures {bit}d -- the witness atom "
                f"{BIT_EQUALITY_FLOOR_ATOM} is being asked for must stay "
                "measured or the reshape loses its evidence"
            )
        diverges = (bit is not None and got is not None and int(bit) != int(got))
        owner = entry.get("own_floor_predicate_atom")
        if diverges and owner != BIT_EQUALITY_FLOOR_ATOM:
            out.append(
                f"{dim}: bit-equality reports {bit}d where the reader's own "
                f"precision reports {got}d, so this dimension's declared "
                "collapse runs and saturation edges rest on a difference no "
                f"consumer renders -- and no atom owns it (want "
                f"{BIT_EQUALITY_FLOOR_ATOM}, got {owner})"
            )
        if not diverges and owner is not None:
            out.append(
                f"{dim}: names {owner} as owning a predicate divergence the "
                f"sweep cannot find (both predicates report {got}d) -- a debt "
                "entry outliving its debt"
            )
    return out


# The atom that owns the predicate itself: every collapse run and saturation
# edge in this module is derived with `repr()` bit-equality, so a 1.4e-17
# difference tells two counterfactual companies apart. Measured, not asserted:
# `belief_population_mix`'s declared ceiling of -309 is one of those readings.
BIT_EQUALITY_FLOOR_ATOM = "D33_the_collapse_predicate_is_bit_equality"


def _own_floor_clause(dimension: Optional[str]) -> str:
    """WHAT THIS FIGURE ITSELF RESOLVES (atom D33) -- interpolated from the
    register per dimension, so the two belief numbers can never again carry one
    resolution between them.

    An unnamed caller gets an explicit REFUSAL rather than a default: handing
    the `belief` floor to a caller stamping `belief_population_mix` is the exact
    defect this clause closes, and a silent default would reinstate it.
    """
    floors = {d: (DIMENSION_DRIFT_RESOLUTION.get(d) or {}).get(
        "own_readable_resolution_floor_days") for d in BELIEF_FLOOR_DIMENSIONS}
    seeds = "/".join(str(s) for s in RESOLUTION_SEEDS)
    listed = ", ".join(f"`{d}` {v}d" for d, v in sorted(floors.items()))
    if dimension is None or dimension not in floors:
        return (
            "NO FIGURE WAS NAMED IN THIS CALL, so no per-figure resolution is "
            f"stated: the belief dimensions do NOT share one ({listed}; "
            "measured atom D33) and stamping either number on an unnamed "
            "figure is the defect this clause refuses. "
        )
    own = floors[dimension]
    other = "; ".join(f"`{d}` {v}d" for d, v in sorted(floors.items())
                      if d != dimension)
    return (
        f"AND WHAT THIS FIGURE ITSELF RESOLVES (atom D33): `{dimension}` "
        f"publishes no readable difference for any memory error smaller than "
        f"{own}d of forgetting, measured through its own shipped scorer on the "
        f"offline scenario (n=300, seeds {seeds}, at the "
        f"{published_reading_decimals(dimension)}dp THIS figure's own consumer "
        f"renders IT at -- atom D34; the five published figures do not share "
        f"one) -- against {other}, so the "
        "belief figures do NOT share a resolution and the number below is a "
        "bound on the book, not this figure's sensitivity. On a live "
        "population no sweep has visited, only that bound is measured here. "
    )


def belief_resolution_caveat(
    resolution: Optional[Dict[str, object]] = None,
    dimension: Optional[str] = None) -> str:
    """The resolution limit that travels WITH both belief numbers (atom D27),
    now naming WHICH figure it is about (atom D33).

    `dimension` is not optional in spirit: the two belief dimensions have
    different measured floors (310d and 314d on this book) and carried one
    byte-identical sentence between them for six Hours. A caller that will not
    say which figure it is stamping gets the shared bound and an explicit
    refusal to name a per-figure resolution -- never the sibling's number.

    Re-derived from the book each call rather than quoted from the register --
    `score_triad` also scores live `run_phase2b` populations whose event span
    no sweep has visited, and a caveat nobody re-derives decays into a claim
    (the D19/D20/D22/D23/D25 pattern)."""
    e = DIMENSION_DRIFT_RESOLUTION["belief"]
    head = (
        "RESOLUTION IS THIS BOOK'S EVENT SPAN (atom D27, measured 2026-08-10, "
        "seeds " + "/".join(str(s) for s in RESOLUTION_SEEDS) + "). Both "
        "belief dimensions read ONE company parameter -- the DD/rail failure "
        "lookback window `_arrears_risk_belief` counts inside -- and an event "
        "can only change side if the window falls BELOW its age. "
    )
    head += _own_floor_clause(dimension)
    if resolution is not None and resolution.get("saturated") is not None:
        if resolution["saturated"]:
            return head + (
                f"This book: {resolution['n_events']} observed failure events, "
                f"oldest {resolution['oldest_event_age_days']}d before "
                f"`as_of`, against a company window of "
                f"{resolution['window_days']}d -- SATURATED, with "
                f"{resolution['headroom_days']}d of headroom. No event in this "
                "book can fall out of that window, so this figure cannot "
                "distinguish this company from one that NEVER forgets a "
                "failure -- the direction that keeps a recovered customer in "
                "collections -- and NO memory error smaller than "
                f"{resolution['smallest_visible_shortening_days']}d of "
                "forgetting can move ANY figure here, because no observed "
                "event changes side inside it (a BOUND on this book, never a "
                "figure's own resolution -- atom D33). A zero here is not "
                "proof the company remembers "
                "the right amount; it is mostly proof this book is shorter "
                "than its memory. AND THE OTHER EDGE (atom D29): the youngest "
                f"observed failure is {resolution['newest_event_age_days']}d "
                "old, so a company whose memory runs "
                f"{resolution['amnesia_floor_window_days']}d or less counts "
                "NOTHING -- every such supplier, down to total amnesia, "
                "publishes one figure as well. This number resolves a memory "
                "error only BETWEEN those two edges."
            )
        return head + (
            f"This book: {resolution['n_events']} observed failure events, "
            f"oldest {resolution['oldest_event_age_days']}d before `as_of`, "
            f"against a company window of {resolution['window_days']}d -- NOT "
            "saturated, so a memory error in either direction can move this "
            "figure by a day."
        )
    blind = tuple(e.get("own_invisible_drifts") or ())
    return head + (
        f"Offline scenario: memory drifts {list(blind)} were measured "
        f"INVISIBLE on seeds {list(RESOLUTION_SEEDS)} "
        f"(debt: {e.get('own_debt_atom')})."
    )


def ageing_resolution_caveat(
    resolution: Optional[Dict[str, object]] = None) -> str:
    """The resolution limit that travels WITH the ageing number.

    Given a `resolution` it describes THE BOOK THE FIGURE WAS COMPUTED ON --
    which matters because `score_triad` also scores LIVE run_phase2b
    populations whose calendar no sweep has ever visited, and until this atom
    those readings carried a caveat written about the offline scenario's three
    due dates. Without one it falls back to the register's declaration for the
    offline book, re-derived each call (the D19/D20/D22/D23 pattern: a caveat
    nobody re-derives decays into a claim)."""
    e = DIMENSION_DRIFT_RESOLUTION["ageing"]
    blind = tuple(e["invisible_drifts"])
    pairs = tuple(e["collapsed_pairs"] or ())
    head = (
        "RESOLUTION IS THIS BOOK'S CALENDAR (atom D25, measured 2026-08-10, "
        "seeds " + "/".join(str(s) for s in RESOLUTION_SEEDS) + "). An ordinal "
        "bucket headline can only see a company dating error that carries an "
        "invoice across a 30/60/90 boundary, so what it can resolve is a "
        "property of where THIS book's invoices sit -- not of the company "
        "being graded. "
    )
    if resolution is not None:
        over, under = (resolution["over_ageing_days"],
                       resolution["under_ageing_days"])
        return head + (
            f"This book: {resolution['n_aged']} aged invoices at "
            f"{resolution['n_distinct_ages']} distinct ages spanning "
            f"{resolution['age_span_days']} days, so the smallest dating error "
            f"it can resolve is {over}d of OVER-ageing (the direction that "
            f"posts an early dunning letter) and {under}d of UNDER-ageing. "
            "Predicted from the population and the truth-side bucket rule "
            "alone and cross-checked against the drift sweep's re-scoring "
            "(`check_ageing_resolution`). A movement smaller than that is not "
            "readable as days, and a zero is not proof of accurate dating."
        )
    if blind or pairs:
        return head + (
            "The offline book's declared band: a supplier dating every debt "
            f"{abs(blind[-1])} to {abs(blind[0])} days OLDER than the world "
            "did publishes a BIT-IDENTICAL headline on every seed"
            + (f", and a supplier {pairs[0][0]} day out and one {pairs[0][1]} "
               "days out are ONE number" if pairs else "")
            + ". Do not read a movement here as days, and do not read a zero "
            "as accurate dating."
        )
    return head + (
        "The offline book is spread across one billing cycle "
        f"({BILLING_CYCLE_SPREAD_DAYS} days), and the drift sweep measures its "
        "ageing headline moving on every declared drift in both directions -- "
        f"including {AGEING_RESOLUTION_TARGET_DAYS}d, the smallest a bucket "
        "headline can express. R12: this is a RESOLUTION change, not a tuning "
        "-- the reshaped book moves every published ageing figure on this pair "
        "and none of them was chosen."
    )


def detection_resolution_caveat() -> str:
    """The resolution limit that travels WITH the detection number (atom D28).

    Interpolated from `DIMENSION_DRIFT_RESOLUTION` on every call rather than
    typed into a sentence once -- the D19/D20/D22/D23/D25 rule: a caveat nobody
    re-derives decays into a claim, and this one exists precisely because a
    declaration that could only be checked where it had already answered had
    decayed into one.

    Unlike `ageing_resolution_caveat` this takes no per-book prediction: what
    the detection gap can resolve is a property of where the book's invoices
    sit relative to the COMPANY's grace line, and no population-side predictor
    of those edges has been built. Saying so is the point -- that predictor is
    the declared residual of atom
    `D28_the_detection_gap_is_quantised_by_this_books_placement`, not something
    this sentence may imply exists.
    """
    e = DIMENSION_DRIFT_RESOLUTION["detection"]
    lo, hi = e.get("saturates_below"), e.get("saturates_above")
    runs = tuple(e.get("collapsed_runs") or ())
    head = (
        "RESOLUTION IS WHERE THIS BOOK SITS BESIDE THE GRACE LINE (atom D28, "
        "measured 2026-08-10 on a grid derived from the book and not from this "
        "register, seeds " + "/".join(str(s) for s in RESOLUTION_SEEDS)
        + "). This headline is SET MEMBERSHIP, so a company's terms error moves "
        "it only where that error carries an invoice across the grace line. "
    )
    if lo is None and hi is None and not runs:
        return head + (
            "On the offline scenario every counterfactual company across a "
            f"{DRIFT_GRID_SPAN_DAYS}-day terms error either way publishes a "
            "distinct figure, in both directions."
        )
    interior = [r for r in runs
                if not (lo is not None and max(r) == lo)
                and not (hi is not None and min(r) == hi)]
    body = (
        f"Offline scenario: the reading SATURATES below {lo:+d}d and above "
        f"{hi:+d}d -- every supplier whose terms are more wrong than that "
        "publishes ONE figure, so a supplier a week short on its terms (the "
        "direction that flags a paying customer as in arrears and posts the "
        "dunning letter) is indistinguishable here from one three weeks short. "
        f"In between it is quantised, not continuous: {len(interior)} further "
        "groups of companies publish one number each "
        + ", ".join("{" + ",".join(f"{k:+d}" for k in r) + "}"
                    for r in interior)
        + ". Do not read a movement in this number as days of company error, "
        "and do not read a zero as accurate flagging. Residual owned by "
        f"{e.get('saturation_atom')}."
    )
    return head + body


def _belief_permutation_note(bel: GapResult) -> str:
    """The published caveat, with its numbers INTERPOLATED FROM THE MEASUREMENT
    rather than typed into a sentence once and left to rot (the D11/D16
    precedent -- a hand-typed witness is a claim about a run that has already
    ended).
    """
    c = bel.components
    rate, n, wrong = (c.get("per_case_disagreement_rate"),
                      c.get("n_cases"), c.get("n_cases_misassigned"))
    if rate is None:
        return (
            "PERMUTATION-INVARIANT and the per-case witness is UNAVAILABLE on "
            "this call, so how much per-case error this number hides is "
            "UNKNOWN -- never read as none. Read the `belief` dimension "
            "instead, which scores per-case assignment directly (atom D19)."
        )
    return (
        "PERMUTATION-INVARIANT BY DESIGN: this compares POPULATION "
        "DISTRIBUTIONS, so permuting which account holds which severity belief "
        f"moves it by exactly zero. Beside it, the direction it cannot see: "
        f"{wrong} of {n} cases carry the wrong severity label per-case "
        f"(disagreement {rate:.4f}). Where the company's errors run ONE WAY, "
        "as they do here (it under-calls severity), TV happens to EQUAL that "
        "per-case rate -- a coincidence of the error direction, not the "
        "quantity being measured, and the coincidence that let this number be "
        "read as a per-case error rate until 2026-08-10. It is no longer the "
        "belief HEADLINE (atom D19): the `belief` dimension scores per-case "
        "assignment in both directions and this one answers the narrower "
        "question it was always answering -- does the company have the right "
        "MIX."
    )


def permute_belief_labels(labels: List[str], seed: int = 1) -> List[str]:
    """The probe the control rests on: a DERANGEMENT-flavoured shuffle of the
    company's per-case labels.

    It preserves the label MULTISET exactly -- so every population aggregate
    built from it is byte-identical -- while moving which case holds which
    label. That is precisely the difference an aggregate-only dimension cannot
    see, and a per-case one must.

    A plain shuffle is used rather than a strict derangement because a strict
    derangement over a heavily-skewed label multiset (this book is ~74%
    `normal`) is not achievable case-by-case anyway; what the control needs is
    that per-case agreement genuinely FALLS, which the vacuity guard asserts
    rather than assumes.
    """
    out = list(labels)
    random.Random(seed).shuffle(out)
    return out


def measure_permutation_sensitivity(
    result: Dict[str, object],
    contract: Optional[Dict[str, Dict[str, object]]] = None,
    seed: int = 1,
) -> Dict[str, Dict[str, object]]:
    """MEASURE the AGGREGATE_SCORING_CONTRACT rather than trust it: for every
    declared dimension, actually permute the company's per-case labels, re-score
    through THAT DIMENSION'S OWN SCORER, and report whether the gap moved.

    Returns {dimension: {"declared_aggregate_only", "gap_before", "gap_after",
    "gap_moved", "agreement_before", "agreement_after", "probe_bit"}}.

    `probe_bit` is the VACUITY guard: the permutation must actually have changed
    per-case assignment for this dimension (agreement fell). A probe that moved
    nothing proves nothing in EITHER direction -- it would hand a silent pass to
    an aggregate-only claim and a silent failure to a per-case one.
    """
    contract = AGGREGATE_SCORING_CONTRACT if contract is None else contract
    labels = result.get("labels") or {}
    out: Dict[str, Dict[str, object]] = {}

    for dim, decl in contract.items():
        true_l = labels.get(f"{dim}_truth")
        bel_l = labels.get(f"{dim}_belief")
        if true_l is None or bel_l is None:
            raise ValueError(
                f"AGGREGATE_SCORING_CONTRACT declares '{dim}' but score_triad "
                f"published no per-case labels for it -- the control cannot be "
                f"run on a declaration it cannot reach"
            )
        permuted = permute_belief_labels(list(bel_l), seed=seed)
        agree_before = sum(1 for a, b in zip(true_l, bel_l) if a == b)
        agree_after = sum(1 for a, b in zip(true_l, permuted) if a == b)
        n = len(true_l) or 1

        before = _rescore_dimension(dim, list(true_l), list(bel_l), result)
        after = _rescore_dimension(dim, list(true_l), permuted, result)

        out[dim] = {
            "declared_aggregate_only": bool(decl["is_aggregate_only"]),
            "gap_before": before,
            "gap_after": after,
            "gap_moved": (before is not None and after is not None
                          and abs(before - after) > 1e-12),
            "agreement_before": round(agree_before / n, 6),
            "agreement_after": round(agree_after / n, 6),
            "probe_bit": agree_after < agree_before,
        }
    return out


def _rescore_dimension(dim: str, true_l: List[str], bel_l: List[str],
                       result: Dict[str, object]) -> Optional[float]:
    """Re-score ONE dimension from per-case labels through its own scorer.

    Detection is scored on SET MEMBERSHIP, not label sequences, so its labels
    are the per-case flagged/true booleans rendered as labels and rebuilt into
    sets here -- the same scorer the headline uses, never a second copy of the
    formula (R15 independence).
    """
    if dim == "belief":
        return belief_measures(true_l, bel_l, order=_SEVERITY_ORDER).gap
    if dim == "belief_population_mix":
        return belief_gap(_severity_distribution(true_l),
                          _severity_distribution(bel_l)).gap
    if dim == "ageing":
        # THE D16 EXCLUSION MASK IS CARRIED, not dropped. Re-scoring without it
        # would make `gap_before` a number the instrument never published, so
        # "the gap moved" would be measuring the mask's removal as well as the
        # permutation. The mask is derived from TRUTH and stays aligned to the
        # case order under a belief-side permutation.
        ai = result.get("ageing_inputs") or {}
        return ageing_gap(true_l, bel_l, excluded=ai.get("excluded"),
                          exclusion_reason=AGEING_EXCLUSION_REASON.format(
                              grace=DEFAULT_RECONCILIATION_GRACE_DAYS)).gap
    if dim == "detection":
        keys = (result.get("labels") or {}).get("detection_keys") or []
        truth_set = {k for k, lab in zip(keys, true_l) if lab == "positive"}
        flagged_set = {k for k, lab in zip(keys, bel_l) if lab == "positive"}
        universe = set(keys)
        negatives = (result.get("labels") or {}).get("detection_negatives")
        if not truth_set or not negatives:
            return None
        return detection_measures(
            truth_set, flagged_set, universe=universe,
            negative_set=set(negatives),
            exclusion_reason="permutation probe: the headline's own band",
        ).gap
    raise ValueError(f"no rescorer for declared dimension '{dim}'")


def measure(n_customers: int = 4000, seed: Optional[int] = None,
            organ_reconciliation_drift_days: int = 0,
            organ_terms_drift_days: int = 0) -> Dict[str, object]:
    """Build the OFFLINE scenario and score all three gap dimensions. Returns a
    dict of {"detection": GapResult, "belief": GapResult, "ageing": GapResult,
    "stats": {...}, "notes": {...}}.

    This is the offline harness entry point (a frozen synthetic population). The
    scoring body it delegates to (`score_triad`) is the SAME code the LIVE
    per-run wiring (`background.live_payment_triad`) calls over a real
    run_phase2b population -- so the live and offline gap are one measurement,
    not two (the reason the live path reuses this module rather than a bespoke
    metric: R15 independence / no second scorer)."""
    records, consumer, ledger_book, as_of = build_scenario(n_customers, seed=seed)
    return score_triad(
        records, consumer, as_of,
        organ_reconciliation_drift_days=organ_reconciliation_drift_days,
        organ_terms_drift_days=organ_terms_drift_days,
    )


def organ_query_dates(
    periods: List[PeriodRecord], as_of: date,
) -> List[date]:
    """The candidate DATES the company's reconciliation organ is asked at, for
    one account (atom D23, the reshape, 2026-08-10).

    A DAILY grid from the account's earliest INVOICE ISSUE DATE to `as_of`
    inclusive. Two properties, and both are the atom:

      * RESOLUTION 1 DAY. The reading is a first-knowledge DATE, so its
        precision is the grid's spacing. The grid this replaced held ONE date
        per period, at the harness's own `due + grace` -- so a company that
        detected a shortfall one day later than the shipped organ missed its
        period's only candidate and was next dated at the NEXT period's,
        publishing a 1-day degradation as +21.0 days.

      * RANGE BOUNDED BY THE COMPANY'S OWN FLOOR, NOT THE HARNESS'S. The grid
        starts at the ISSUE date because a supplier cannot know a bill went
        unpaid before it has issued the bill: `expected_collection_misses`
        reads `age_open_items`, which holds nothing for an unissued invoice, so
        no organ can be dated earlier however fast it reconciles. The old grid
        started at `due + grace` -- the harness's own parameter -- which is why
        every faster company published that parameter back.

    The residual this leaves is declared, measured and owned in
    `ORGAN_QUERY_GRID`: two detectors that both fire on the issue date are one
    reading, because the instrument stops where the company's knowledge does.
    Read a first-knowledge landing on the invoice's own issue date as "at or
    before" -- `n_recon_dated_at_issue_floor` counts them beside the number.

    COST, MEASURED RATHER THAN WAVED AT (2026-08-10). One organ query per day
    per account, against one per period before, so the multiplier is the period
    spacing: 86 dates against 3 on the offline scenario (`measure` at n=4000:
    3.7s), and ~3,470 against 114 on a live 24-account x 114-month run
    (`LivePaymentTriad.measure()`: 1.6s -> 40.6s, ~27x). That is ~40s on a
    5-9 minute sim run, and it buys the actual resolution of the only dimension
    whose whole subject is HOW LATE. It is NOT free, and the number is written
    here so the next person weighing a shorter grid is weighing it against a
    measurement. An early break out of the sweep was tried and reverted -- see
    `score_triad`; it looked exact and moved six tests."""
    if not periods:
        return []
    start = min(r.issue_date for r in periods)
    if start > as_of:
        return []
    return [start + timedelta(days=i) for i in range((as_of - start).days + 1)]


def score_triad(
    records: List[PeriodRecord],
    consumer: PaymentObservationConsumer,
    as_of: date,
    payment_terms_days: int = PAYMENT_TERMS_DAYS,
    reconciliation_grace_days: int = DEFAULT_RECONCILIATION_GRACE_DAYS,
    organ_reconciliation_drift_days: int = 0,
    organ_terms_drift_days: int = 0,
) -> Dict[str, object]:
    """Score the four gap dimensions (detection / detection_latency / belief /
    ageing) for a coupled-triad population.

    `reconciliation_grace_days` is passed EXPLICITLY to the consumer rather than
    left to its default, because the detection-LATENCY dimension asks the same
    organ for its earliest detection date -- a scorer using one grace window and
    a consumer using another would read a latency that belongs to neither.

    `organ_reconciliation_drift_days` is the DECLARED COUNTERFACTUAL COMPANY the
    `ORGAN_QUERY_GRID_RESOLUTION` control needs (atom D23, Expert Hour #7): it
    shifts the company's OWN reconciliation detector by `k` days -- the organ
    stays silent until an invoice is `grace + k` days overdue -- while leaving
    the harness's candidate-date grid, the world, and every truth-side rule
    untouched. Any movement in a published figure under it is therefore the
    company's detector moving, by construction. It lives here as a declared
    parameter rather than in a test's `monkeypatch` for the D20 reason: a
    counterfactual a reader cannot find in the repo is not part of the design.
    R13: it does not touch the baseline world; it builds a second, explicitly
    labelled COMPANY. Default 0 -- the scored book is never drifted.

    `organ_terms_drift_days` is the SECOND declared counterfactual company (atom
    D25, Expert Hour #8): the supplier holds the wrong PAYMENT TERMS on every
    account, so it dates each invoice's due date `k` days later than the world
    did -- k > 0 means it believes every debt is k days YOUNGER (it under-ages),
    k < 0 that every debt is k days OLDER (it over-ages, the direction that
    sends a dunning letter early). It reaches the organ ONLY: the harness's
    truth side ages from the world's own `PeriodRecord.due_date`, and the
    truth-side bucket rule (`_ageing_bucket`, atom D21) is untouched, so every
    movement under it is the company's dating moving. A real and common
    supplier error -- migrated accounts landing on the default terms -- and the
    drift the `DIMENSION_DRIFT_RESOLUTION` register puts each dimension's
    resolution on trial against. Default 0 -- the scored book is never drifted.

    `records` are the harness-held TRUTH (`PeriodRecord`, one per customer x
    period); `consumer` is the company's BELIEF surface, already fed EXCLUSIVELY
    through `emit_wall_responses` (never a PeriodRecord). This function is the
    ONLY place holding both side by side -- harness code, outside the wall by
    design. Callable over EITHER the frozen offline scenario (`measure`) or a
    live run_phase2b population (`background.live_payment_triad`) -- identical
    scoring, so the live per-run gap and the offline gap are the same metric."""
    by_customer: Dict[str, List[PeriodRecord]] = {}
    for r in records:
        by_customer.setdefault(r.customer_id, []).append(r)

    # ------------------------------------------------------------------
    # (1) DD-failure detection
    # ------------------------------------------------------------------
    truth_set = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    # THE NEVER-FLAGGABLE BAND, BUILT ONCE AND USED BY BOTH DIMENSIONS (atom
    # D16). It is constructed here, above the loop, rather than beside the
    # `detection_measures` call, for a reason that is the whole of D16: this set
    # defines which cases a belief can be WRONG about, and until 2026-08-09 only
    # the detection dimension had it. The ageing dimension re-derived nothing and
    # applied no band at all, so the two published one named quantity as two
    # numbers 3.5x apart. A SECOND construction of the same rule would have been
    # the sibling-half class again (two copies drifting apart is how this defect
    # was born); there is one set, and both dimensions read it.
    #
    # An invoice paid 20 days late genuinely WAS unpaid past its grace date, so
    # the company treating it as owing was CORRECT -- scoring it against the
    # company would punish it for being right, and on this population that error
    # inflated the measured false-flag rate from 0.0009 to 0.2834 in D11's first
    # draft. A belief is wrong only about a case that was NEVER legitimately
    # chaseable: the cash arrived on or within grace. Everything else --
    # late-past-grace successes, unresolved disputes, and any record whose
    # `days_late` truth is UNKNOWN (never assumed paid on time) -- is EXCLUDED,
    # counted, and the reason travels in the components (D10's rule: published,
    # not silent).
    never_flaggable = {
        (r.customer_id, r.period_index) for r in records
        if r.result == "success" and r.days_late is not None
        and r.days_late <= reconciliation_grace_days
    }
    flagged_set: set = set()
    # Two INDEPENDENT detection paths, kept apart so their witnesses stay clean
    # (director ruling 2026-07-25 §2, R15 both-ways):
    #   * DD-CHANNEL: an observed Bacs/rail FAILURE event (`recent_dd_failures`).
    #     A non-DD case appearing here would be a LEAK across the wall (the
    #     adapter emits nothing for a missed push payment) -- witness must stay 0.
    #   * RECONCILIATION: expected-collection reconciliation (own bills vs own
    #     cash) legitimately detects a missed push payment WITHOUT any rail event
    #     -- a non-DD case appearing here is the CARVE-OUT WORKING, witness > 0.
    flagged_via_dd_channel: set = set()
    flagged_via_reconciliation: set = set()

    # ------------------------------------------------------------------
    # (2) Belief severity + (3) ageing -- both need one snapshot per account
    # ------------------------------------------------------------------
    true_severity_labels: List[str] = []
    belief_severity_labels: List[str] = []
    true_ageing_labels: List[str] = []
    belief_ageing_labels: List[str] = []
    # D16: the ageing dimension's own view of the never-flaggable band, parallel
    # to the two label lists, plus the case keys so the two dimensions'
    # NUMERATORS (not just their denominators) can be compared case by case by
    # the shared-quantity control without either being re-derived.
    ageing_excluded: List[bool] = []
    ageing_case_keys: List[Tuple[str, int]] = []

    n_true_dd_failures = 0
    n_true_non_dd_failures = 0
    n_flagged_non_dd_via_dd_channel = 0   # the LEAK witness: must stay 0
    n_flagged_non_dd_via_reconciliation = 0  # the carve-out witness: expected > 0
    # Days-overdue AT `as_of` of each reconciliation detection (ruling §1's
    # registered residual). NOT a detection latency -- see the stats key's own
    # comment; the real latency is the `detection_latency` dimension below.
    recon_days_overdue_at_as_of: List[int] = []
    # DETECTION-LATENCY inputs (atom D10), per truly-failed (customer, period):
    # days from due date to each CHANNEL's own first knowledge of the shortfall.
    dd_lag_days: Dict[Tuple[str, int], int] = {}
    recon_lag_days: Dict[Tuple[str, int], int] = {}
    n_recon_detected_undated = 0
    n_dd_observed_after_as_of = 0
    # Atom D23: cases dated at the invoice's own ISSUE date -- the grid's floor
    # AND the company's, so "at or before", never exact.
    n_recon_dated_at_issue_floor = 0
    # JOIN WITNESSES (R15 fail-silent, 2026-08-08 HARDEN). Every belief-side
    # observation below is joined back to a truth case by a KEY (`value_date` ->
    # due date, `invoice_ref`/`reference` -> the harness's own invoice_ref). A
    # `.get()` miss silently DROPS the observation -- so a drift in either key
    # convention would push the measured gap toward the no-skill baseline with
    # nothing firing. Count the misses and the ageing-side matches so the
    # vacuous case is distinguishable from the honest one.
    n_unjoined_dd_failures = 0
    n_unjoined_collection_misses = 0
    n_ageing_refs_matched = 0

    for cid, periods in by_customer.items():
        account_id = periods[0].account_id
        organ_terms_days = payment_terms_days + organ_terms_drift_days
        snapshot = consumer.snapshot(
            account_id, as_of=as_of, payment_terms_days=organ_terms_days,
            reconciliation_grace_days=(
                reconciliation_grace_days + organ_reconciliation_drift_days),
        )

        due_to_period = {r.due_date: r.period_index for r in periods}
        ref_to_period = {r.invoice_ref: r.period_index for r in periods}
        due_by_period = {r.period_index: r.due_date for r in periods}
        truly_failed = {r.period_index for r in periods if r.result == "failed"}
        for dd_fail in snapshot.recent_dd_failures:
            p = due_to_period.get(dd_fail.value_date)
            if p is None:
                n_unjoined_dd_failures += 1
                continue
            # FIRST-KNOWLEDGE date for the DD channel: the bank-feed REPORT
            # date (`observed_at`), ARUDD-lagged at the seam -- NOT
            # `value_date`, which is the collection date and would read a
            # flat 0 (the 2026-08-08 residual's misread, see the
            # `detection_latency_gap` docstring). A report landing after
            # `as_of` is not yet knowledge: witnessed, never counted.
            #
            # POINT-IN-TIME FIX (D11, 2026-08-09): the not-yet-knowable case is
            # now excluded from `flagged_via_dd_channel` as well, not only from
            # the latency inputs. Until this tick it was counted as a detection
            # -- crediting the company with knowing something its own bank feed
            # had not reported yet, which is the detection dimension's own small
            # version of a point-in-time blindfold breach.
            observed_on = dd_fail.observed_at.date()
            if observed_on > as_of:
                n_dd_observed_after_as_of += 1
                continue
            flagged_via_dd_channel.add((cid, p))
            if p in truly_failed:
                lag = (observed_on - due_by_period[p]).days
                dd_lag_days[(cid, p)] = min(dd_lag_days.get((cid, p), lag), lag)
        for miss in snapshot.detected_collection_misses:
            p = ref_to_period.get(miss.invoice_ref)
            if p is not None:
                flagged_via_reconciliation.add((cid, p))
                recon_days_overdue_at_as_of.append(miss.days_latency)
            else:
                n_unjoined_collection_misses += 1

        # RECONCILIATION first-knowledge date, asked of the company's OWN organ
        # at each candidate date rather than re-derived here as `due + grace`
        # (R15 independence -- a harness copy of the rule could not fail if the
        # organ's rule changed). Candidates are the earliest dates the detector
        # could possibly fire for each truly-failed period.
        #
        # THE POPULATION IS "EVER KNEW", NOT "STILL BELIEVES AT as_of", and the
        # difference is the whole point of the dimension. `flagged_set` above is
        # a belief held AT `as_of`, so an invoice detected on time and settled
        # late leaves it -- which makes any mean over that set drift with the
        # date the scorer happens to ask on (measured: moving `as_of` 30 days
        # moved the mean 1.96 -> 1.80 while not one detection date changed).
        # That is the same as_of artefact the retired `detection_latency_days`
        # key was, so this dimension asks its question of every TRULY-FAILED
        # case: the company detecting a shortfall on day 5 is a fact about day
        # 5, whatever the cash did afterwards. A case reported at `as_of` but at
        # none of its candidates (an allocation reshuffle can do it) is left
        # UNDATED and witnessed, never dated by guess.
        # THE EVER-FLAGGED SWEEP (atom D11, 2026-08-09). Until this tick this
        # loop ran over the truly-FAILED periods only, and only to date the
        # latency dimension; the detection headline's `flagged_set` came from the
        # `as_of` snapshot alone. That made the headline a belief held AT `as_of`
        # scored against a truth that does not move at all, so moving only the
        # date the scorer asks on walked the published figure +70% over 60 days
        # (H27 Expert Hour). It now sweeps EVERY period -- truly-failed and
        # truly-succeeded alike, because the false-flag direction needs the
        # succeeded ones too -- and a case the company flagged at ANY date up to
        # `as_of` stays flagged. Detecting a shortfall on day 5 is a fact about
        # day 5, whatever a later oldest-first allocation did to the invoice.
        #
        # Cost is one organ query per distinct due+grace date per account. The
        # early-break that used to stop once every failure was dated is gone
        # deliberately: it could only ever be correct for a truly-failed
        # population, and leaving it in would have silently truncated the
        # false-flag sweep.
        # THE GRID IS DAILY, FROM THE ISSUE DATE (atom D23, the reshape,
        # 2026-08-10). It used to be `sorted({r.due_date + grace})` -- one
        # candidate per period, at the harness's OWN re-derivation of the
        # organ's rule, which is what made this reading quantised to 21 days
        # upward and pinned to the `grace` parameter downward. See
        # `organ_query_dates` for why the issue date is the floor and what
        # residual that leaves.
        candidates = organ_query_dates(periods, as_of)
        issue_by_period = {r.period_index: r.issue_date for r in periods}
        # NO EARLY BREAK. One was tried while landing D23 and reverted the same
        # hour: "stop once every period of this account is flagged" looks exact
        # -- the set is a union, the dates keep their first hit -- and it moved
        # six tests, including the `as_of`-contract pair. The D11 early-break
        # this module already deleted had the same shape and the same story. The
        # sweep is dense on purpose; the cost is in `organ_query_dates`.
        for cand in candidates:
            for m in consumer.expected_collection_misses(
                account_id, as_of=cand,
                grace_days=(
                    reconciliation_grace_days + organ_reconciliation_drift_days),
                payment_terms_days=organ_terms_days,
            ):
                # An unjoinable ref is counted once, at `as_of`, in the snapshot
                # loop above -- same key convention, so witnessing it twice would
                # double-count the drift rather than detect it twice.
                p = ref_to_period.get(m.invoice_ref)
                if p is None:
                    continue
                flagged_via_reconciliation.add((cid, p))
                if p in truly_failed and (cid, p) not in recon_lag_days:
                    recon_lag_days[(cid, p)] = (cand - due_by_period[p]).days
                    # THE FLOOR WITNESS (atom D23). A first knowledge landing on
                    # the invoice's OWN issue date is the earliest this
                    # instrument can represent -- and the earliest the company
                    # could hold, since it had not billed before then. Read
                    # those as "at or before", never as an exact date; counted
                    # here so a population that is mostly floored is
                    # distinguishable from one that is not.
                    if cand == issue_by_period.get(p):
                        n_recon_dated_at_issue_floor += 1
        if truly_failed:
            still_flagged = {
                ref_to_period[m.invoice_ref] for m in snapshot.detected_collection_misses
                if m.invoice_ref in ref_to_period
            } & truly_failed
            n_recon_detected_undated += len(
                still_flagged - {p for (c, p) in recon_lag_days if c == cid}
            )

        n_unresolved_true = sum(1 for r in periods if r.result == "failed")
        n_hardship_true = sum(
            1 for r in periods
            if r.result == "failed" and r.dd_failure_reason == INSUFFICIENT_FUNDS
        )
        # Through the ownership register (atom D21), same as the ageing
        # truth side -- the register is the call path for every truth-side
        # labelling rule this module has, not just the one that was wrong.
        true_severity_labels.append(
            truth_side_rule("belief")(n_unresolved_true, n_hardship_true))
        belief_severity_labels.append(snapshot.arrears_risk_belief.value)

        aged_by_ref = {ai.reference: ai for ai in snapshot.aged_items}
        for r in periods:
            # D16: the SAME band the detection dimension uses, read from the SAME
            # set. A case is scored here only if it is one the company's ageing
            # report could be right or wrong about in an unambiguous way: a true
            # failure (truly overdue) or a payment that landed within grace
            # (truly current). A payment that arrived past grace is NEITHER --
            # the company was right that it was owed and the truth bucket at
            # `as_of` says "current", which is precisely the disagreement that
            # made 94 of this dimension's 101 false ageings land on cases the
            # sibling dimension holds the company was RIGHT about.
            ageing_case_keys.append((r.customer_id, r.period_index))
            ageing_excluded.append(
                r.result != "failed"
                and (r.customer_id, r.period_index) not in never_flaggable
            )
            if r.result == "failed":
                n_true_dd_failures += 1 if r.payment_method == DIRECT_DEBIT else 0
                n_true_non_dd_failures += 1 if r.payment_method != DIRECT_DEBIT else 0
                true_days_overdue = (as_of - r.due_date).days
                # Resolved THROUGH the ownership register (atom D21) rather
                # than by a bare name, so what the control inspects is what
                # actually runs. This call used to be the company organ's own
                # `age_bucket`.
                true_ageing_labels.append(
                    truth_side_rule("ageing")(true_days_overdue))
            else:
                true_ageing_labels.append("current")

            # An absent ref is the HONEST default for a settled invoice (it
            # leaves the open-item ageing entirely), so a miss cannot be an
            # error on its own -- but a TOTAL miss (key-convention drift) would
            # read as "the company believes everything is current" and inflate
            # the ageing gap silently. `n_ageing_refs_matched` is the vacuity
            # witness that tells those two apart.
            ai = aged_by_ref.get(r.invoice_ref)
            if ai is not None:
                n_ageing_refs_matched += 1
            belief_ageing_labels.append(ai.bucket if ai is not None else "current")

    flagged_set = flagged_via_dd_channel | flagged_via_reconciliation

    for (cid, p) in flagged_via_dd_channel:
        rec = next(r for r in by_customer[cid] if r.period_index == p)
        if rec.payment_method != DIRECT_DEBIT:
            n_flagged_non_dd_via_dd_channel += 1  # a LEAK -- must never increment
    for (cid, p) in flagged_via_reconciliation:
        rec = next(r for r in by_customer[cid] if r.period_index == p)
        if rec.payment_method != DIRECT_DEBIT:
            n_flagged_non_dd_via_reconciliation += 1  # the carve-out working

    # THE UNIVERSE, passed as a SET rather than a count (D11): a flag landing
    # outside the scored universe -- a join-key drift -- RAISES instead of
    # quietly shrinking a denominator.
    universe = {(r.customer_id, r.period_index) for r in records}
    # THE FALSE-FLAG DENOMINATOR IS NOT `universe - truth_set`, and getting this
    # wrong was the first thing the D11 build got wrong about itself. The band
    # itself is built ONCE, above the loop -- see its comment there for why, and
    # for what "never flaggable" means.
    det = detection_measures(
        truth_set, flagged_set, universe=universe,
        negative_set=never_flaggable,
        exclusion_reason=(
            "cases in NEITHER direction's population: a payment that eventually "
            f"succeeded but arrived more than {reconciliation_grace_days} days "
            "(the reconciliation grace) after its due date really was unpaid "
            "past grace, so flagging it was correct and counting it as a false "
            "flag would score the company down for being right; an unresolved "
            "dispute is not a settled success either; and a record carrying no "
            "`days_late` truth is UNKNOWN, never assumed paid on time."
        ),
    )
    det.note = (
        "W2_11 true payment failure (any channel) vs D5's belief, now via TWO "
        "detection paths: observed Bacs/rail failure events AND expected-collection "
        "reconciliation (own bills vs own cash -- director ruling 2026-07-25 §2). "
        "The reconciliation path narrows the push-channel blind spot but never "
        "closes it: a late-but-eventual payment (cash by as_of) is correctly NOT "
        "flagged (detection LATENCY, ruling §1), guaranteeing gap > 0 (R12). "
        "READ THIS NUMBER AS RECONCILIATION-DETERMINED ALONE (atom D10, measured "
        "not asserted): `flagged_set` is a UNION and the DD-observation channel "
        "contributes ZERO unique detections, so deleting that channel outright "
        "leaves this figure BIT-IDENTICAL. What the channel does buy is EARLIER "
        "detection, which set-membership cannot express -- it is measured, in "
        "days, by the companion `detection_latency` dimension. "
        "AND READ IT AS A BELIEF HELD AT as_of, NOT AS 'NEVER OBSERVED' (D10, "
        "second finding): the residual is NOT the no-remittance blind spot it "
        "was described as. Every truly-failed case in this population was "
        "flagged by reconciliation at due+grace -- `n_undetected` is 0 on seeds "
        "7/11/23 -- and the misses counted here are cases the company detected "
        "ON TIME and then UN-flagged, because a later period's ambiguous non-DD "
        "payment was allocated oldest-first onto the failed invoice (Clayton's "
        "Case; atom D8_ambiguous_remittance_misdating). The blind spot is real "
        "(a failed non-DD payment emits no rail event at all) but it is not what "
        "this residual measures. "
        "RESHAPED 2026-08-09 (atom D11) -- the two limits the H27 Expert Hour "
        "measured are FIXED, not caveated, and the headline is a DIFFERENT "
        "NUMBER from every ledger entry written before that date. What changed, "
        "and what each change was for: "
        "(1) THE POPULATION. `flagged_set` was a belief held AT `as_of` scored "
        "against a truth (`result == 'failed'`) that does not move at all, so "
        "holding the company AND the world literally fixed and moving only the "
        "date the scorer asks on walked the old figure 0.0725 -> 0.1232 (+70% "
        "over 60 days, seed 7). It is now EVER-FLAGGED: a case the company "
        "flagged at any date up to `as_of` stays flagged, whatever a later "
        "oldest-first allocation did to the invoice (Clayton's Case, atom D8). "
        "That is the shape the companion `detection_latency` dimension was "
        "deliberately built on (D10) and the headline had been left behind. "
        "`DIMENSION_AS_OF_CONTRACT` now declares this dimension invariant and "
        "the class control MEASURES the declaration by sweeping `as_of`. "
        "(2) THE DIRECTION. The old figure was a RECALL gap -- a company that "
        "flagged every invoice scored a perfect 0.0 while 44-51% of what this "
        "company actually flags is an invoice that truly SUCCEEDED. The headline "
        "is now the BALANCED error: the mean of missed_failure_rate (over the "
        "truly-failed) and false_flag_rate (over the never-flaggable -- THE "
        "wrongful-dunning exposure, and since atom D16 the only figure that "
        "carries that name: the ageing dimension's `overstated_arrears_rate` "
        "measures the REPORT's overstatement at `as_of` over the same "
        "population but a different belief side, and was measured to be a "
        "strict SUBSET of these cases, not the same number). Both degenerate "
        "strategies now score g0 = 0.5. The "
        "retired figure is NOT restated in components: it was scored over a "
        "different flagged population, so no arithmetic on these sets reproduces "
        "it, and a restatement would be a false continuity between two numbers "
        "that were never the same measurement. "
        "(3) THE FALSE-FLAG DENOMINATOR IS NOT 'everything that did not fail'. "
        "An invoice paid past the reconciliation grace really was unpaid past "
        "grace, so flagging it was CORRECT; those cases, unresolved disputes, "
        "and any record with no `days_late` truth are EXCLUDED and counted "
        "(`n_excluded`), never quietly folded into either direction. Getting "
        "this wrong inflated the first draft of this very measure from 0.0009 "
        "to 0.2834. "
        "R12: the reshape was designed from the defect, never fitted to a value; "
        "the number moved because the measure was wrong, not because it looked "
        "wrong."
    )
    # STAMPED AT SOURCE, on the note AND the components (atom D28). The ledger
    # writer, the live wiring and the dashboard read `components` and never the
    # prose (D22), and a control the reader about to quote this gap never meets
    # protects the test suite rather than the figure (D25).
    det.note += " " + detection_resolution_caveat()
    det.components["drift_resolution_caveat"] = detection_resolution_caveat()
    # AND WHERE THE RECONCILIATION KNOB'S OWN SWEEP STOPS RESOLVING IT (atom
    # D31). The detection gap is the SET reading of `ORGAN_QUERY_GRID`, and it
    # saturates in both tails of that knob too -- a second blindness of the
    # same published number, found only once the register was swept on a grid
    # it did not choose. Interpolated from the register so a reshape that moved
    # the edges could not leave this sentence standing.
    det.note += " " + organ_query_grid_saturation_caveat()
    det.components["recon_saturation_caveat"] = (
        organ_query_grid_saturation_caveat())
    det.components["recon_saturation_band_days"] = (
        ORGAN_QUERY_GRID["flagged_via_reconciliation"]["saturates_below"],
        ORGAN_QUERY_GRID["flagged_via_reconciliation"]["saturates_above"],
    )

    lat = detection_latency_gap(
        dd_lag_days, recon_lag_days,
        n_true_failures=len(truth_set),
        n_recon_detected_undated=n_recon_detected_undated,
        n_dd_observed_after_as_of=n_dd_observed_after_as_of,
        n_recon_dated_at_issue_floor=n_recon_dated_at_issue_floor,
    )

    # THE BELIEF HEADLINE IS PER-CASE SINCE 2026-08-10 (atom D19). It used to be
    # the population TV distance below, which a permutation of the company's
    # per-case labels left bit-identical -- so the degenerate "right mix, every
    # individual wrong" scored exactly what the real company scored. Both
    # numbers are published, each under a name that says which question it
    # answers; neither is a restatement of the other.
    bel = belief_measures(
        true_severity_labels, belief_severity_labels, order=_SEVERITY_ORDER,
    )
    bel.note = (
        "BALANCED PER-CASE arrears-severity error: the company's own "
        "`arrears_risk_belief` (DD/rail-observed unresolved count) vs the TRUE "
        "severity (all-channel unresolved count) -- same threshold shape, "
        "different-coverage inputs -- scored ACCOUNT BY ACCOUNT in both "
        "directions on their own denominators. "
        "THE 'SAME THRESHOLD SHAPE' CLAIM IS MEASURED, NOT ASSERTED, SINCE "
        "2026-08-10 (atom D20). It is the claim that makes this number a "
        "measure of the WALL, and until that date it lived only in a docstring: "
        "the truth-side rule is a HAND-COPY of the company organ's own "
        "thresholds, so an organ-only change would have turned this figure into "
        "a mixture of coverage loss and rule divergence while it went on being "
        "published as coverage. Measured: three plausible organ drifts moved it "
        "by up to 2.9x, and the single test that fired each time named a weak "
        "permutation probe or an epistemic-wall leak -- never the divergence. "
        "`measure_coverage_only_residual` now equalises the coverage (an all-DD "
        "counterfactual population on which the company observes every failure) "
        "and the surviving residual, which is rule divergence by construction "
        "and needs no copy of either rule to say so, must be exactly 0. It is, "
        "on seeds 7/11/23, with every vacuity witness non-empty. "
        "RESHAPED 2026-08-10 (atom D19) "
        "and NOT COMPARABLE with any belief figure published before that date: "
        "the retired headline was a population TV distance, which a permutation "
        "of the per-case labels left identical to machine precision (0.0713 -> "
        "0.0713, per-case agreement 0.9287 -> 0.6432). That figure survives as "
        "the `belief_population_mix` dimension, which is what it always "
        "measured. R12: the reshape was designed from the defect, never fitted "
        "to a value; the number moved because the measure was wrong, not "
        "because it looked wrong."
    )

    # What MEMORY error this book can resolve (atom D27), predicted from the
    # population's own event span before the figure is published -- so the
    # caveat travelling with the number describes the book the number came
    # from, including live populations no drift sweep has visited.
    belief_resolution = measure_belief_window_resolution(records, as_of)
    # AND WHAT SETS THAT BAND (atom D30). D27/D29 said where the two edges are;
    # this says WHICH HARNESS CONSTANTS PUT THEM THERE, and that the scored
    # company's own memory sits outside the band entirely. It travels with the
    # figure for the D22 reason -- a limit only an Expert-Hour register carries
    # is one no reader of the number ever sees.
    constant_census = measure_scenario_constant_census(records, as_of)
    census_caveat = scenario_constant_census_caveat(constant_census)
    bel.note += " " + belief_resolution_caveat(belief_resolution, "belief")
    bel.note += " " + census_caveat
    # AND AS COMPONENTS, not only in the prose: the ledger writer, the live
    # wiring and the dashboard take `components` and never read `note`, so a
    # limit only the prose carries is one the machine strips off (D22).
    bel.components["belief_resolution_caveat"] = belief_resolution_caveat(
        belief_resolution, "belief")
    # THIS FIGURE'S OWN FLOOR, as structure and not only prose (atom D33): the
    # ledger writer, the live wiring and the dashboard read `components`, so a
    # per-figure resolution the machine strips off is one the reader never gets.
    bel.components["measured_resolution_floor_days"] = (
        DIMENSION_DRIFT_RESOLUTION["belief"]["own_readable_resolution_floor_days"])
    bel.components["book_bound_floor_days"] = belief_resolution.get(
        "smallest_visible_shortening_days")
    bel.components["belief_window_resolution"] = dict(belief_resolution)
    bel.components["scenario_constant_census_caveat"] = census_caveat
    bel.components["band_owning_constants"] = tuple(
        sorted(n for n, e in SCENARIO_CONSTANT_CENSUS.items()
               if e.get("bounds_resolution")))
    bel.components["scored_company_is_inert"] = constant_census[
        "scored_company_is_inert"]
    bel.components["memory_blind_band_days"] = tuple(
        DIMENSION_DRIFT_RESOLUTION["belief"]["own_invisible_drifts"])

    mix = belief_gap(
        _severity_distribution(true_severity_labels),
        _severity_distribution(belief_severity_labels),
        # THE PER-CASE WITNESS (atom D19). These are the SAME two label lists
        # the two distributions above are built from, in the same case order,
        # so the direction the distribution distance is blind to travels with
        # the number instead of needing a reader to go and compute it. It stays
        # here after the reshape: this dimension is STILL blind, by design, and
        # a reader who takes the mix figure alone must see that in the same
        # breath rather than one dimension over.
        truth_labels=true_severity_labels,
        belief_labels=belief_severity_labels,
    )
    mix.metric = "belief_population_mix"
    mix.note = (
        "POPULATION MIX ONLY -- TV distance between the TRUE arrears-severity "
        "distribution (all-channel unresolved-failure count) and D5's own "
        "arrears_risk_belief distribution (DD/rail-observed count only). This "
        "is the pre-2026-08-10 'belief gap' under a name that says what it "
        "measures (atom D19); the per-case headline is the `belief` dimension. "
        + _belief_permutation_note(mix)
        + " " + belief_resolution_caveat(belief_resolution,
                                        "belief_population_mix")
        + " " + census_caveat
    )
    mix.components["belief_resolution_caveat"] = belief_resolution_caveat(
        belief_resolution, "belief_population_mix")
    # FOUR DAYS BLUNTER THAN ITS SIBLING, and the whole of atom D33: this figure
    # published `belief`'s resolution for six Hours because one function rendered
    # one sentence for both.
    mix.components["measured_resolution_floor_days"] = (
        DIMENSION_DRIFT_RESOLUTION["belief_population_mix"][
            "own_readable_resolution_floor_days"])
    mix.components["book_bound_floor_days"] = belief_resolution.get(
        "smallest_visible_shortening_days")
    mix.components["belief_window_resolution"] = dict(belief_resolution)
    mix.components["scenario_constant_census_caveat"] = census_caveat
    mix.components["band_owning_constants"] = tuple(
        sorted(n for n, e in SCENARIO_CONSTANT_CENSUS.items()
               if e.get("bounds_resolution")))
    mix.components["scored_company_is_inert"] = constant_census[
        "scored_company_is_inert"]
    mix.components["memory_blind_band_days"] = tuple(
        DIMENSION_DRIFT_RESOLUTION["belief_population_mix"][
            "own_invisible_drifts"])

    # What THIS book can resolve (atom D25), predicted from the population and
    # the truth-side bucket rule before the figure is published, so the caveat
    # travelling with the number describes the book the number came from.
    ageing_resolution = measure_ageing_resolution(records, as_of)

    age = ageing_gap(
        true_ageing_labels, belief_ageing_labels,
        excluded=ageing_excluded,
        exclusion_reason=AGEING_EXCLUSION_REASON.format(
            grace=reconciliation_grace_days),
    )
    age.note = (
        "per-invoice 30/60/90+ ageing bucket: truth (resolved-by-as_of fact) vs "
        "D5's own open-item ageing belief; picks up both the raw non-payment "
        "signal and any allocation cross-contamination from the ambiguous-"
        "remittance non-DD population (see module 'ON ALLOCATION' note). "
        "D7 RESHAPE (2026-08-08): three measures on their own denominators, NOT "
        "one prevalence-normalised scalar -- headline `gap` is mean bucket "
        "DISPLACEMENT (buckets, no baseline); read understated_arrears_rate and "
        "overstated_arrears_rate in components. "
        "D16 ALIGNMENT (2026-08-09) -- TWO CHANGES, and the second is the one a "
        "reader must not skip. (1) THE DENOMINATOR. This dimension carried no "
        "exclusion band at all while its sibling applied D11's rule (a payment "
        "that arrived past the reconciliation grace really WAS unpaid past "
        "grace, so the company treating it as owed was CORRECT), so 94 of its "
        "101 false ageings landed on cases the DETECTION dimension of this same "
        "instrument holds the company was RIGHT about. The band is now the SAME "
        "SET, built once and read by both, and `n_excluded` publishes it. "
        "(2) THE NAME. `overstated_arrears_rate` was published as 'the "
        "wrongful-dunning exposure' -- the same words the detection dimension's "
        "`false_flag_rate` carries. Aligning the denominators did NOT make them "
        "one number, and that is the finding, not a residual: the two BELIEF "
        "sides ask different questions. Detection asks whether the company EVER "
        "chased this invoice -- which is what wrongful dunning IS, an event that "
        "either happened to a customer or did not. Ageing asks whether the "
        "company's open-item report STILL shows it overdue at `as_of` -- a "
        "misstatement question, which is what a provision or a board pack is "
        "built from. A customer wrongly chased in month one and dropped from the "
        "report by month three was still wrongly chased. So this rate keeps its "
        "denominator alignment and LOSES the name: it is the AGEING-REPORT "
        "OVERSTATEMENT at `as_of`. The wrongful-dunning exposure is published "
        "ONCE, by the detection dimension. R12: neither number was chosen; the "
        "band was, and the rate followed it. "
        + ageing_resolution_caveat(ageing_resolution)
    )
    # AND AS A COMPONENT, not only inside the prose: a reader who takes
    # `components` programmatically -- the ledger writer, the live wiring, the
    # dashboard -- never reads `note`, and a limit only the prose carries is one
    # the machine strips off (the D22 stamping lesson).
    age.components["drift_resolution_caveat"] = ageing_resolution_caveat(
        ageing_resolution)
    age.components["drift_blind_band_days"] = tuple(
        DIMENSION_DRIFT_RESOLUTION["ageing"]["invisible_drifts"])
    # THIS BOOK's own resolution, not the offline scenario's (atom D25). The
    # live wiring scores populations no drift sweep has ever visited, so the
    # only honest resolution to stamp on a figure is the one predicted from the
    # book that figure was computed over.
    age.components["ageing_resolution_days"] = {
        "over_ageing": ageing_resolution["over_ageing_days"],
        "under_ageing": ageing_resolution["under_ageing_days"],
    }
    age.components["ageing_resolution_book"] = {
        "n_aged": ageing_resolution["n_aged"],
        "n_distinct_ages": ageing_resolution["n_distinct_ages"],
        "age_span_days": ageing_resolution["age_span_days"],
    }

    n_customers = len(by_customer)
    _od = sorted(recon_days_overdue_at_as_of)
    days_overdue_summary = {
        "n": len(_od),
        "min_days": _od[0] if _od else None,
        "median_days": _od[len(_od) // 2] if _od else None,
        "max_days": _od[-1] if _od else None,
    }
    stats = {
        "n_customers": n_customers,
        "n_periods_per_customer": (len(records) // n_customers) if n_customers else 0,
        "n_cases": len(records),
        "as_of": as_of.isoformat(),
        "n_true_failures": len(truth_set),
        "n_true_dd_failures": n_true_dd_failures,
        "n_true_non_dd_failures": n_true_non_dd_failures,
        "n_flagged_failures": len(flagged_set),
        # LEAK witness (a non-DD case reaching belief via the DD-failure event
        # channel): must stay 0 -- the adapter emits nothing for a missed push
        # payment, so a non-zero value would be a wall leak.
        "n_flagged_non_dd_failures": n_flagged_non_dd_via_dd_channel,
        # CARVE-OUT witness (ruling §2): non-DD misses now legitimately detected
        # by expected-collection reconciliation (own bills vs own cash). Expected
        # > 0 -- this is the sensing organ working, not a leak.
        "n_flagged_non_dd_via_reconciliation": n_flagged_non_dd_via_reconciliation,
        "n_flagged_via_dd_channel": len(flagged_via_dd_channel),
        "n_flagged_via_reconciliation": len(flagged_via_reconciliation),
        # OVER-FLAGGING witnesses (atom D11, H27 Expert Hour 2026-08-09). The
        # detection headline is a RECALL gap: flagging everything scores a
        # perfect 0, so the score alone cannot tell a precise company from an
        # indiscriminate one. These carry the other error direction, on its own
        # denominator (the D7 rule -- a rate over the whole population would
        # re-import the class-balance dependence D7 exists to remove).
        "n_flagged_not_truly_failed": det.components["n_false_flags"],
        "false_flag_rate_over_truly_current": det.components["false_flag_rate"],
        # CHANNEL-CONTRIBUTION witnesses (R15 fail-silent, 2026-08-08 HARDEN).
        # `flagged_set` is a UNION, so a channel that detects nothing the other
        # channel does not already detect moves the headline detection gap by
        # EXACTLY ZERO. Measured (seeds 7/11/23, 400 customers):
        # `n_flagged_via_dd_channel_only == 0` every time -- the DD-observation
        # channel is currently SUBSUMED by expected-collection reconciliation
        # for this metric, so the published detection gap is reconciliation-
        # determined alone. That is a measured finding reported honestly, not a
        # defect to tune away (R12): a rail failure necessarily means the cash
        # did not arrive, so reconciliation sees the same shortfall. What the
        # DD channel really buys is EARLIER detection, which pure set-membership
        # cannot express -- registered, not papered over.
        "n_flagged_via_dd_channel_only": len(flagged_via_dd_channel - flagged_via_reconciliation),
        "n_flagged_via_reconciliation_only": len(flagged_via_reconciliation - flagged_via_dd_channel),
        # JOIN witnesses -- see the block where they are accumulated. The two
        # unjoined counts must stay 0 (a dropped observation is a silently
        # inflated gap); `n_ageing_refs_matched` must stay > 0 (a zero would
        # mean the ageing belief joined to nothing at all).
        "n_unjoined_dd_failures": n_unjoined_dd_failures,
        "n_unjoined_collection_misses": n_unjoined_collection_misses,
        "n_ageing_refs_matched": n_ageing_refs_matched,
        # RETIRED KEY `detection_latency_days` (atom D10, 2026-08-09). It was
        # never a detection latency: `ExpectedCollectionMiss.days_latency` is
        # days-overdue at the SINGLE `as_of` the scorer happens to ask at, so on
        # this scenario's fixed period grid it read exactly {30, 51, 72} days --
        # a pure artefact of `as_of`, carrying zero information about WHEN the
        # company first knew. Retired, not re-labelled (the D7 precedent): the
        # key now says what it actually measures, and the real per-channel
        # latency is the `detection_latency` DIMENSION.
        "reconciliation_days_overdue_at_as_of": days_overdue_summary,
        # Detection LATENCY, the real one (ruling §1: register the lag, do not
        # compress it to zero) -- headline mean in days, its DD-channel-deleted
        # counterfactual, and the coverage witnesses. Full shape in
        # `result["detection_latency"].components`.
        "detection_latency_days_mean": lat.components["mean_lag_days"],
        "detection_latency_days_mean_without_dd_channel":
            lat.components["mean_lag_days_without_dd_channel"],
        "dd_channel_days_earlier": lat.components["dd_channel_days_earlier"],
        "n_latency_population": lat.components["n_latency_population"],
        "n_recon_detected_undated": n_recon_detected_undated,
        "n_dd_observed_after_as_of": n_dd_observed_after_as_of,
    }
    notes = {
        "reconciliation": (
            "director ruling 2026-07-25 §2 carve-out: expected-collection "
            "reconciliation detects missed push payments (all channels) from own "
            "bills vs own cash, no rail event required. SENSING ONLY -- no dunning/ "
            "vulnerability/provisioning (reserved, ruling §3). Residual (never 0, "
            "R12): late-but-eventual payments (latency), ambiguous-remittance "
            "mis-allocation, and partial payments. n_flagged_non_dd_failures (the "
            "DD-channel leak witness) stays 0; n_flagged_non_dd_via_reconciliation "
            "is the carve-out working."
        ),
        "channel_contribution": (
            "2026-08-08 HARDEN finding (R15 fail-silent, measured not asserted): "
            "the DD-observation channel contributes ZERO unique detections -- "
            "n_flagged_via_dd_channel_only == 0 across seeds 7/11/23 -- so the "
            "published DETECTION gap is determined by expected-collection "
            "reconciliation alone, and killing the DD channel outright leaves the "
            "headline number bit-identical. Structurally reasonable (a rail "
            "failure means the cash did not arrive, which reconciliation also "
            "sees) but it means set-membership detection is blind to the only "
            "thing the DD channel actually buys: EARLIER detection. Reported as a "
            "measured limit of this metric, never tuned away (R12). "
            "CLOSED 2026-08-09 by atom D10, and one claim of the 2026-08-08 "
            "residual CORRECTED: that pass recorded that DD latency could not be "
            "honestly measured here because the adapter emits `value_date == "
            "due_date` with no ARUDD lag. False -- it was the wrong field. "
            "`WallResponse.observed_at` (the bank-feed REPORT date, carried onto "
            "`DDFailureObservation.observed_at`) is already lagged "
            "0..ARUDD_NOTIFICATION_LAG_DAYS per case by the seam. The companion "
            "`detection_latency` dimension now measures it, and the channel's "
            "contribution IS visible there in days while remaining exactly zero "
            "here (R12: the set-membership number was not moved by a single "
            "digit -- a fix that made this channel 'count' without the company "
            "detecting anything earlier would have been goal-seeking)."
        ),
        "detection_residual_is_misallocation_not_blindness": (
            "2026-08-09 D10 finding, OBSERVED case by case, not inferred. The "
            "detection residual was described everywhere as 'failures the "
            "company never observes through the seam -- the no-remittance blind "
            "spot'. It is not. Asking the company's OWN reconciliation organ at "
            "each invoice's due+grace date shows every truly-failed case in this "
            "population was flagged on time (n_undetected == 0, seeds 7/11/23). "
            "The cases the headline counts as missed are ones the company "
            "detected correctly and then UN-detected: a later period's ambiguous "
            "non-DD payment carries no invoice reference, so AccountLedger's "
            "oldest-first fallback allocates it onto the FAILED invoice, which "
            "goes quiet while a later, genuinely-paid invoice takes its place in "
            "the open-item view (inspected directly: e.g. seed 7 C000024 p0 "
            "prepayment failed, flagged at due+5, and at as_of the open item is "
            "p2 instead). That is Clayton's Case -- the mechanism atom "
            "D8_ambiguous_remittance_misdating exists for -- surfacing in the "
            "DETECTION dimension, not only the ageing one. R12: nothing was "
            "tuned; the detection gap is byte-for-byte what it was, and what "
            "changed is the sentence describing what it counts. The no-remittance "
            "blind spot is still REAL (a failed non-DD payment emits no rail "
            "event); it is simply not what this residual is made of."
        ),
        "allocation": (
            "attempted, honestly dropped: misapplication_gap's no-skill "
            "baseline needs a small shared label space, but invoice_ref is "
            "effectively unique per (customer, period) -- a majority class "
            "over that space is meaningless. The scenario still seeds the "
            "real mechanism (ambiguous account-level correlation_id for "
            "non-DD payments, forcing AccountLedger's oldest-first fallback); "
            "its consequence surfaces honestly inside the ageing gap above "
            "rather than being forced into a fourth, ill-fitting metric."
        ),
    }
    # THE SETS THEMSELVES (atom D11). Returned so a caller -- in practice the
    # R15 mutation tests -- can score a MUTATED belief through the SAME scorer
    # rather than re-deriving the ever-flagged sweep in a second implementation.
    # A test that re-implemented this loop would be asserting a copy against a
    # copy: the tautology R15 names first (and the one this repo has already
    # caught twice inside its own R15 tests).
    # THE AGEING DIMENSION'S OWN CASE SETS (atom D16). Returned for the same
    # reason the detection sets are: the shared-quantity control has to compare
    # the two dimensions' NUMERATORS case by case, and a control that rebuilt
    # this loop to do it would be asserting a copy against a copy. These are the
    # cases the ageing scorer actually counted, not a re-derivation of them.
    ageing_false_ageing_cases = {
        k for k, t, b, x in zip(ageing_case_keys, true_ageing_labels,
                                belief_ageing_labels, ageing_excluded)
        if not x and t == "current" and b != "current"
    }
    ageing_scored_current_cases = {
        k for k, t, x in zip(ageing_case_keys, true_ageing_labels, ageing_excluded)
        if not x and t == "current"
    }
    sets = {
        "truth": truth_set,
        "flagged": flagged_set,
        "flagged_via_dd_channel": flagged_via_dd_channel,
        "flagged_via_reconciliation": flagged_via_reconciliation,
        "never_flaggable": never_flaggable,
        "universe": universe,
        # The detection dimension's own false-flag CASES, named so the
        # shared-quantity control can compare numerators case by case exactly as
        # it compares denominators. `detection_measures` computes `D & N`
        # internally on these same two sets; this names the result rather than
        # asking the control to know the formula.
        "detection_false_flags": flagged_set & never_flaggable,
        "ageing_false_ageings": ageing_false_ageing_cases,
        "ageing_truly_current": ageing_scored_current_cases,
        "ageing_excluded": {
            k for k, x in zip(ageing_case_keys, ageing_excluded) if x
        },
    }
    # THE AGEING SCORER'S ACTUAL INPUTS (atom D16), returned for the same reason
    # `sets` is: the R15 mutation that matters here is "fold the excluded band
    # back into the denominator and prove the rate moves", and a test that
    # rebuilt these three lists to do it would be scoring a copy. It re-scores
    # THESE, through `gap_metric.ageing_gap`, with the mask removed.
    ageing_inputs = {
        "truth_labels": true_ageing_labels,
        "belief_labels": belief_ageing_labels,
        "excluded": ageing_excluded,
        "case_keys": ageing_case_keys,
    }
    # THE PER-CASE LABELS, published for the AGGREGATE_SCORING_CONTROL (atom
    # D19). Same reason `sets` and `ageing_inputs` are published: the control
    # permutes these and re-scores through the dimensions' OWN scorers, so it
    # is measuring the shipped instrument rather than a copy of it (R15
    # independence). Detection is scored on SET MEMBERSHIP, so its per-case
    # form is rendered here on ONE shared key order -- the same `universe`
    # ordering for truth and belief alike, or a permutation of one would be
    # scored against a different case list.
    _det_keys = sorted(universe)
    labels = {
        "belief_truth": true_severity_labels,
        "belief_belief": belief_severity_labels,
        # THE SAME TWO LISTS under the mix dimension's own key (atom D19). The
        # control looks up `<dimension>_truth`/`_belief`, and a dimension that
        # cannot be reached drops silently out of the sweep -- an unreachable
        # register entry reads exactly like a clean one. Sharing the lists is
        # the point: the two dimensions score the SAME per-case data and differ
        # only in what they do with it, which is what makes "one moves, one does
        # not" a statement about the measures rather than about their inputs.
        "belief_population_mix_truth": true_severity_labels,
        "belief_population_mix_belief": belief_severity_labels,
        "ageing_truth": true_ageing_labels,
        "ageing_belief": belief_ageing_labels,
        "detection_keys": _det_keys,
        # ONE SHARED VOCABULARY for truth and belief. Rendering these as
        # failed/ok against flagged/clear would make per-case agreement 0 on
        # EVERY case by construction, so the probe's vacuity guard could never
        # be satisfied and the dimension would be silently unprobed -- the
        # `probe_bit` would report "the permutation changed nothing" when what
        # it really meant was "these two label sets never agree in the first
        # place". Caught by the guard on its first run.
        "detection_truth": ["positive" if k in truth_set else "negative"
                            for k in _det_keys],
        "detection_belief": ["positive" if k in flagged_set else "negative"
                             for k in _det_keys],
        "detection_negatives": never_flaggable,
    }
    # THE LATENCY DIMENSION'S OWN INPUTS (atom D22). Published for the same
    # reason `ageing_inputs` and the per-case `labels` are: a dimension a
    # control cannot reach drops silently out of the sweep, and an unreachable
    # entry reads exactly like a clean one. This dimension has no per-case
    # belief labels to permute -- its population is TRUTH-CONDITIONED -- so what
    # `measure_headline_direction_coverage` checks is the condition itself.
    # ADDITIVE: it moves no published figure, it only makes one checkable.
    latency_inputs = {
        "recon_lag_days": dict(recon_lag_days),
        "dd_lag_days": dict(dd_lag_days),
        "truly_failed_keys": sorted(truth_set),
    }
    return {"detection": det, "detection_latency": lat, "belief": bel,
            "belief_population_mix": mix, "ageing": age,
            "stats": stats, "notes": notes, "sets": sets,
            "ageing_inputs": ageing_inputs, "latency_inputs": latency_inputs,
            "labels": labels}


# UK gas-crisis regime window (HISTORICAL FACT, not a curriculum knob -- R13).
# Wholesale gas/power ran at sustained crisis levels from the autumn-2021
# supply squeeze through the 2022 Russia-Ukraine spike; the domestic price cap
# rose from ~£1,277 (Oct-2021) to ~£3,549-capped (Oct-2022, EPG-shielded). This
# window classifies which of a live run's periods sit in the crisis regime (G2)
# vs calm (G1) for the DETECTION per-cell partition. It is a WORLD-side reading
# of REAL history (citeable to Ofgem's cap trajectory), never an agent-tuned
# difficulty setting, and never crosses the wall into company belief. The
# boundaries are deliberately conservative (the core sustained-spike window);
# the residual (periods near the boundary) collapses honestly into whichever
# side it falls, registered by the emit-side simplification.
_GAS_CRISIS_START = date(2021, 9, 1)
_GAS_CRISIS_END = date(2023, 3, 31)


def uk_price_regime(due_date: date) -> str:
    """WORLD-side price-regime label for a billing period's due date: 'G2'
    (crisis / sustained spike) inside the 2021-09..2023-03 UK gas-crisis
    window, else 'G1' (calm / soft market). Reads only the date -- a real
    supplier's own calendar knowledge -- never simulation internals. G3 (acute
    correlated tail) is NOT assigned here: an acute cold-and-still tail is a
    within-regime event, not a calendar window, so asserting it from a date
    would be a fabricated attribution."""
    if _GAS_CRISIS_START <= due_date <= _GAS_CRISIS_END:
        return "G2"
    return "G1"


def _detection_sets_by_partition(
    records: List[PeriodRecord],
    consumer: PaymentObservationConsumer,
    as_of: date,
    partition_of: Callable[[PeriodRecord], str],
    payment_terms_days: int,
    reconciliation_grace_days: int = DEFAULT_RECONCILIATION_GRACE_DAYS,
) -> Tuple[Dict[str, set], Dict[str, set], Dict[str, set], Dict[str, set]]:
    """(truth_by_part, flagged_by_part, universe_by_part, negative_by_part) --
    the shared partitioning both the gap scorer and the emission-prep reuse.
    Each failed (customer, period) case is attributed to `partition_of(record)`;
    each observed DD-failure is mapped back to the partition of the exact case
    its `value_date` matches (so a customer spanning regimes contributes each
    period to the right cell, no double-count). `partition_of` reads ONLY the
    harness-held PeriodRecord.

    THE LAST TWO ARE WHAT MAKE THE CELLS TWO-DIRECTIONAL (atom D12), and they
    are PARTITIONED, never re-derived: `universe_by_part` is every case scored
    in that cell and `negative_by_part` is that cell's slice of the SAME
    `never_flaggable` set `score_triad` builds for the headline -- a payment
    that arrived on or within the reconciliation grace, the only case a flag is
    genuinely WRONG on. Both are per-RECORD properties, so splitting them by
    partition is arithmetic rather than a modelling choice; that is precisely
    why the cell grid could be fixed in this atom while the two self-rationing
    pairs (whose negative population is a thresholded continuum) could not, and
    inventing one for them was explicitly refused (see
    `docs/design/D13_SELF_RATIONING_NEGATIVE_POPULATION_DISCOVER.md`).
    Deriving the negatives as `universe - truth` instead would charge the
    company for correctly flagging a payment that arrived three weeks late --
    the error that inflated D11's first draft tenfold."""
    by_customer: Dict[str, List[PeriodRecord]] = {}
    for r in records:
        by_customer.setdefault(r.customer_id, []).append(r)

    truth_by_part: Dict[str, set] = {}
    flagged_by_part: Dict[str, set] = {}
    universe_by_part: Dict[str, set] = {}
    negative_by_part: Dict[str, set] = {}
    for cid, periods in by_customer.items():
        account_id = periods[0].account_id
        snapshot = consumer.snapshot(
            account_id, as_of=as_of, payment_terms_days=payment_terms_days
        )
        due_to_period = {r.due_date: r.period_index for r in periods}
        ref_to_period = {r.invoice_ref: r.period_index for r in periods}
        rec_by_period = {r.period_index: r for r in periods}
        for r in periods:
            key = partition_of(r)
            universe_by_part.setdefault(key, set()).add((cid, r.period_index))
            if r.result == "failed":
                truth_by_part.setdefault(key, set()).add((cid, r.period_index))
            elif (r.result == "success" and r.days_late is not None
                    and r.days_late <= reconciliation_grace_days):
                # The ONLY cases a flag is wrong on, sliced per cell. Everything
                # else -- late-past-grace successes, disputes, and any record
                # whose `days_late` truth is unknown -- falls in NEITHER
                # population and is published as this cell's own `n_excluded`.
                negative_by_part.setdefault(key, set()).add((cid, r.period_index))
        for dd_fail in snapshot.recent_dd_failures:
            p = due_to_period.get(dd_fail.value_date)
            if p is not None:
                key = partition_of(rec_by_period[p])
                flagged_by_part.setdefault(key, set()).add((cid, p))
        # Expected-collection reconciliation flags (ruling 2026-07-25 §2), mapped
        # back to the exact period's partition -- same per-cell attribution as
        # the DD-channel path (a spanning customer contributes each period to the
        # right cell, no double-count).
        for miss in snapshot.detected_collection_misses:
            p = ref_to_period.get(miss.invoice_ref)
            if p is not None:
                key = partition_of(rec_by_period[p])
                flagged_by_part.setdefault(key, set()).add((cid, p))
    return truth_by_part, flagged_by_part, universe_by_part, negative_by_part


# The per-cell exclusion reason. Kept as ONE constant used by both cell paths so
# the grid and the per-cell gap scorer cannot drift into publishing different
# reasons for the same excluded case (D10: the exclusion is published, not
# silent, and `detection_measures` RAISES if it is missing).
_CELL_EXCLUSION_REASON = (
    "cases in NEITHER direction's population within this cell: a payment that "
    "eventually succeeded but arrived after the reconciliation grace really was "
    "unpaid past grace, so flagging it was CORRECT and counting it as a false "
    "flag would score the company down for being right (the tenfold error D11's "
    "first draft made); an unresolved dispute is not a settled success; and a "
    "record carrying no `days_late` truth is UNKNOWN, never assumed paid on time."
)


def detection_cell_measurements(
    records: List[PeriodRecord],
    consumer: PaymentObservationConsumer,
    as_of: date,
    regime_of: Callable[[PeriodRecord], str] = None,
    payment_terms_days: int = PAYMENT_TERMS_DAYS,
    archetype: str = "A1",
) -> Dict[str, "object"]:
    """Per-cell DETECTION measurements ready for
    `background.live_fidelity_evidence.emit_live_fidelity_cells`: maps each
    observed regime to grid cell `f"{archetype}_{regime}"` and returns
    `{cell_id: CellMeasurement(detection_gap, true_failures, believed_failures,
    regime_label)}`. `regime_of` defaults to `uk_price_regime` on the record's
    due date (the payment scenario's cast is the affordability-stressed A1
    archetype throughout -- the honest dimension this pair varies is regime).

    Imports `CellMeasurement` lazily so this harness stays free of an
    import-time dependency on the emit bridge (and the bridge stays free of
    any sim import). Cells with no failures at all are omitted (nothing
    honestly measured -> stays dark via the grid's fail-open floor)."""
    from background.live_fidelity_evidence import CellMeasurement

    if regime_of is None:
        regime_of = lambda rec: uk_price_regime(rec.due_date)  # noqa: E731

    truth_by_part, flagged_by_part, universe_by_part, negative_by_part = (
        _detection_sets_by_partition(
            records, consumer, as_of, regime_of, payment_terms_days
        )
    )
    out: Dict[str, object] = {}
    for regime in set(truth_by_part) | set(flagged_by_part):
        truth = truth_by_part.get(regime, set())
        flagged = flagged_by_part.get(regime, set())
        if not truth:
            continue  # no true failures in this regime -> nothing measured here
        res = detection_measures(
            truth, flagged,
            universe=universe_by_part.get(regime, set()),
            negative_set=negative_by_part.get(regime, set()),
            exclusion_reason=_CELL_EXCLUSION_REASON,
        )
        # VACUITY IS EXPLICIT, NEVER FAIL-OPEN (R15). A cell with no negative
        # cases has no false-flag denominator, so `detection_measures` hands
        # back gap=None. Publishing the recall half alone under the same name
        # would be exactly the silent one-directional reading this atom exists
        # to kill, so the cell stays DARK and the grid's fail-open floor keeps
        # scoring it at least as badly as the worst measured cell.
        if res.gap is None:
            continue
        cell_id = f"{archetype}_{regime}"
        comp = res.components
        out[cell_id] = CellMeasurement(
            detection_gap=float(res.gap),
            true_failures=len(truth),
            believed_failures=len(flagged),
            regime_label=regime,
            missed_failure_rate=comp["missed_failure_rate"],
            false_flag_rate=comp["false_flag_rate"],
            n_false_flags=comp["n_false_flags"],
            n_negatives=comp["n_negatives"],
            n_excluded=comp["n_excluded"],
            exclusion_reason=comp["exclusion_reason"],
        )
    return out


def score_detection_by_partition(
    records: List[PeriodRecord],
    consumer: PaymentObservationConsumer,
    as_of: date,
    partition_of: Callable[[PeriodRecord], str],
    payment_terms_days: int = PAYMENT_TERMS_DAYS,
) -> Dict[str, GapResult]:
    """Score the DETECTION dimension SEPARATELY per partition key -- the
    honestly-partitionable half of the triad (SOURCE 2 of PLANNER_MINTED_
    payment_grid_coverage_2026-07-25, "light the dark payment-gap grid cells").

    `partition_of(record) -> key` is a WORLD-side classifier (e.g. the observed
    price regime of `record.due_date`): it reads ONLY the harness-held
    `PeriodRecord` truth and NEVER crosses the wall into the company belief.
    Returns `{key: GapResult}`, each cell's gap computed by the SAME
    `detection_gap` scorer `score_triad` uses (R15 independence -- no second
    metric), over ONLY that partition's (customer, period) cases.

    WHY ONLY DETECTION (the named residual, `_DETECTION_REGIME_PARTITIONED_
    SIMP_ID` on the emit side). Detection is pure set-membership over the
    passed cases: each (customer, period) failure is attributed to its OWN
    partition, and each observed DD-failure is mapped back to the partition of
    the exact case its `value_date` matches -- so a customer whose life spans
    two regimes contributes each period to the correct cell, no double-count.
    BELIEF and AGEING cannot be split this way: they read the company's
    account-level arrears/ageing snapshot, a single running belief per account
    that would be double-counted if a spanning customer's belief were charged
    to two cells. Those stay regime-MIXED (the honest residual), never silently
    partitioned. R12: emits what was measured per cell, tunes nothing."""
    truth_by_part, flagged_by_part, universe_by_part, negative_by_part = (
        _detection_sets_by_partition(
            records, consumer, as_of, partition_of, payment_terms_days
        )
    )

    out: Dict[str, GapResult] = {}
    for key in set(truth_by_part) | set(flagged_by_part):
        truth = truth_by_part.get(key, set())
        if not truth:
            continue  # nothing to detect in this partition -> nothing measured
        res = detection_measures(
            truth, flagged_by_part.get(key, set()),
            universe=universe_by_part.get(key, set()),
            negative_set=negative_by_part.get(key, set()),
            exclusion_reason=_CELL_EXCLUSION_REASON,
        )
        res.note = (
            f"partition {key!r}: W2_11 true payment failure (any channel) vs "
            "D5's DD-failure-observed belief, over ONLY this partition's cases "
            "(world-side partition, never leaked company-side). BOTH ERROR "
            "DIRECTIONS on their own denominators (atom D12): the headline is "
            "the mean of the missed-failure rate over this cell's true failures "
            "and the wrongful-dunning rate over this cell's never-flaggable "
            "cases, so flagging EVERY case in the partition can no longer score "
            "it a perfect 0. The non-DD no-remittance blind spot recurs here by "
            "construction (R12/R13) -- a near-zero gap would be a leak, not a win."
        )
        out[key] = res
    return out


def _git_head() -> Optional[str]:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gaps into coupled_gap_ledger.json")
    ap.add_argument("--coverage-residual", action="store_true",
                    help=("also score the all-DD counterfactual and print the "
                          "coverage-only residual (atom D20) -- builds a "
                          "SECOND population, so it is opt-in"))
    ap.add_argument("--coverage-residual-customers", type=int, default=800,
                    help="population size for --coverage-residual (default 800)")
    args = ap.parse_args()

    result = measure(args.customers, seed=args.seed)
    stats = result["stats"]

    print("W2_11 <-> D5 coupled payment-belief-vs-truth scenario")
    print(f"  customers                 : {stats['n_customers']}")
    print(f"  periods/customer          : {stats['n_periods_per_customer']}")
    print(f"  cases (cust x period)     : {stats['n_cases']}")
    print(f"  as_of                     : {stats['as_of']}")
    print(f"  true failures (all chan.) : {stats['n_true_failures']}"
          f"  (DD {stats['n_true_dd_failures']}, non-DD {stats['n_true_non_dd_failures']})")
    print(f"  ever-flagged (belief)     : {stats['n_flagged_failures']}"
          f"  (non-DD leaked: {stats['n_flagged_non_dd_failures']})")

    # DETECTION is not a g0-normalised recall score any more (D11) -- it is a
    # BALANCED error over two directions, and printing it in the raw_gap/g0/GAP
    # shape is how the retired figure got read as "nearly perfect detection"
    # while half the company's flags were on invoices that had been paid. It
    # prints as both directions with their own denominators.
    print(f"  [detection] {format_detection_summary(result['detection'])}")
    print(f"              g0={result['detection'].g0} "
          f"(both degenerate strategies -- flag nobody AND flag everything)")
    # BELIEF is not a g0-normalised TV distance any more (D19) -- it is a
    # BALANCED per-case error, and printing it as a bare scalar is how the
    # retired figure got read as "7% of accounts mis-graded" by a number that
    # could not say WHICH accounts. Both directions print with their own
    # denominators.
    print(f"  [belief] {format_belief_summary(result['belief'])}")
    print(f"           g0={result['belief'].g0} (every severity-blind rule, "
          f"incl. right mix / wrong accounts)")
    r_mix: GapResult = result["belief_population_mix"]
    print(f"  [belief_population_mix] raw_gap={r_mix.raw_gap:.4f}  "
          f"g0={r_mix.g0:.4f}  GAP={r_mix.gap}")
    print(f"           {_belief_permutation_note(r_mix)}")
    # THE PERMUTATION CONTROL, printed every run rather than living only in the
    # test suite: a limit a reader has to go looking for is one they will read
    # past. Each row is the DECLARATION put on trial against a measurement.
    print("  [aggregate-scoring control] permute the company's per-case labels:")
    for dim, v in measure_permutation_sensitivity(result).items():
        verdict = ("BLIND to per-case assignment (declared, atom D19)"
                   if v["declared_aggregate_only"] else "per-case sensitive")
        print(f"           {dim:<10} agreement {v['agreement_before']:.4f} -> "
              f"{v['agreement_after']:.4f}, gap {v['gap_before']:.4f} -> "
              f"{v['gap_after']:.4f} ({'moved' if v['gap_moved'] else 'UNMOVED'})"
              f" -- {verdict}")
    # THE HEADLINE-DIRECTION CONTROL, printed every run for the same reason the
    # permutation control above is: a limit a reader has to go looking for is
    # one they will read past. Each row scores that dimension's own
    # indiscriminate degenerate through its own shipped scorer.
    print("  [headline-direction control] score each dimension's indiscriminate "
          "degenerate:")
    _hdc = measure_headline_direction_coverage(result)
    for dim, v in _hdc.items():
        if v["degenerate_strategy"] is None:
            print(f"           {dim:<22} TRUTH-CONDITIONED population "
                  f"(n={v['n_latency_population']}, truly-current in it: "
                  f"{v['n_truly_current_in_population']}) -- direction counted "
                  f"by `{v['covered_by']}`, which distinguishes: "
                  f"{v['cover_is_two_directional']}")
            continue
        verdict = ("counts BOTH directions"
                   if v["declared_counts_both_directions"]
                   else f"ONE-DIRECTIONAL, named debt: {v['debt_atom']}")
        print(f"           {dim:<22} perfect {v['perfect_gap']:.6f} -> "
              f"degenerate {v['degenerate_gap']:.6f} "
              f"({'distinguishes' if v['distinguishes'] else 'IDENTICAL'}, "
              f"{v['n_cases_changed']} cases changed) -- {verdict}")
    _hdc_violations = check_headline_direction_coverage(_hdc)
    print("           verdict: "
          + ("every declaration held" if not _hdc_violations
             else f"{len(_hdc_violations)} VIOLATION(S)"))
    for v in _hdc_violations:
        print(f"           !! {v}")
    # Ageing is NOT a g0-normalised score (D7) -- printing it in the same
    # raw_gap/g0/GAP shape as the other two is exactly how the old scalar got
    # read as one. Its three measures print with their units instead.
    print(f"  [ageing] {format_ageing_summary(result['ageing'])}")
    # Detection latency is not g0-normalised either -- it is an absolute mean in
    # days (D10). It prints with its counterfactual because the counterfactual
    # is the finding: the DD channel moves THIS and not the detection gap.
    print(f"  [detection_latency] {format_detection_latency_summary(result['detection_latency'])}")
    # THE GRID RESOLUTION (atom D23). Printed where the latency number is read,
    # for the reason the direction control is: a control living only in the test
    # suite is one a reader of the instrument's own output never meets -- and
    # this reader is exactly the one about to quote a latency in days.
    _oqg = measure_organ_query_grid_resolution(n_customers=300, seed=7)
    print("           organ-query grid resolution (D23), company detector "
          "drifted, world untouched:")
    for name, row in _oqg.items():
        step = ("" if row["one_day_report"] is None
                else f", a +1d company reads as {row['one_day_report']:+g}d")
        print(f"           {name:<26} blind to {row['unmoved']}, "
              f"sees {row['moved']}{step}")
        # The COLLAPSE is the residual after D23's reshape, and printing only
        # `unmoved` would show an empty list beside a reading that still cannot
        # tell two companies apart -- "blind to []" read as "blind to nothing".
        for (a, b), got in row["collapses"].items():
            print(f"           {'':<26} {a:+d}d and {b:+d}d COLLAPSE to "
                  f"{got['readings'][0]!r} (residual, atom "
                  f"{ORGAN_QUERY_GRID[name]['debt_atom']})")
    _oqg_violations = check_organ_query_grid_resolution(_oqg)
    print("           verdict: "
          + ("every declaration held" if not _oqg_violations
             else f"{len(_oqg_violations)} VIOLATION(S)"))
    for v in _oqg_violations:
        print(f"           !! {v}")

    # ...AND WHERE THAT REGISTER STOPS RESOLVING THE COMPANY AT ALL (atom D31).
    # The block above is read off the register's OWN declarations; this one is
    # read off a grid derived from the book, which is the only place a collapse
    # nobody declared can show up. Printed here for the D25 reason: a reader
    # about to quote either of these two readings needs its RANGE beside its
    # step, not just its step.
    _route_violations = check_counterfactual_knob_route()
    print("           knob route: "
          f"{len(COUNTERFACTUAL_KNOB_ROUTE)} counterfactual knob(s), each on a "
          "book-derived grid through the one saturation rule -- "
          + ("clean" if not _route_violations
             else f"{len(_route_violations)} VIOLATION(S)"))
    for v in _route_violations:
        print(f"           !! {v}")
    _oqs = measure_organ_query_grid_saturation(n_customers=300)
    for name, row in _oqs.items():
        entry = ORGAN_QUERY_GRID[name]
        print(f"           {name:<26} SATURATES below "
              f"{row['saturates_below']}d ({entry['saturation_atom_below']}) / "
              f"above {row['saturates_above']}d "
              f"({entry['saturation_atom_above']}), "
              f"{len(row['collapsed_runs'])} collapsed run(s) on the "
              f"{len(row['drifts'])}-point book-derived grid")
        if row["undefined_readings"]:
            print(f"           {'':<26} NO READING at "
                  f"{list(row['undefined_readings'])} -- population empty, "
                  "witnessed; an absent reading is not a resolved company")
    _oqs_violations = check_organ_query_grid_saturation(_oqs)
    print("           verdict: "
          + ("every declaration held" if not _oqs_violations
             else f"{len(_oqs_violations)} VIOLATION(S)"))
    for v in _oqs_violations:
        print(f"           !! {v}")

    # THE DIMENSION RESOLUTION CONTROL (atom D25). Printed for the same reason
    # the two above are, and this one answers the question a reader of ANY of
    # these headlines is entitled to ask: how wrong does the company have to be
    # before this number notices?
    _ddr = measure_dimension_drift_resolution(n_customers=300)
    print("  [drift-resolution control] company holds the wrong payment terms "
          f"(world untouched), seeds {RESOLUTION_SEEDS}:")
    for dim, row in _ddr.items():
        entry = DIMENSION_DRIFT_RESOLUTION[dim]
        if not entry["in_causal_path"]:
            print(f"           {dim:<22} OFF the drift's path (organ reads "
                  f"failure events, not dating) -- moved by "
                  f"{entry['exercised_by']}: {row['exercised']}")
            continue
        print(f"           {dim:<22} blind to {row['unmoved']}, "
              f"sees {row['moved']}")
        # ATOM D28. The line above is read off a grid the register no longer
        # chooses; this one says where the reading stops telling two companies
        # apart at all, which is the question a reader quoting the gap has.
        if row["saturates_below"] is not None or row["saturates_above"] is not None:
            print(f"           {'':<22} SATURATES below "
                  f"{row['saturates_below']}d / above "
                  f"{row['saturates_above']}d on the "
                  f"{len(row['drifts'])}-point book-derived grid; "
                  f"{len(row['collapsed_runs'])} collapsed run(s) (atom "
                  f"{entry['saturation_atom']})")
        for (a, b), got in row["collapses"].items():
            print(f"           {'':<22} {a:+d}d and {b:+d}d COLLAPSE to "
                  f"{got['readings'][0]!r} (residual, atom "
                  f"{entry['debt_atom']})")
    _ddr_violations = check_dimension_drift_resolution(_ddr)
    print("           verdict: "
          + ("every declaration held" if not _ddr_violations
             else f"{len(_ddr_violations)} VIOLATION(S)"))
    for v in _ddr_violations:
        print(f"           !! {v}")

    # THE OFF-PATH DIMENSIONS' OWN GRADED BAND (atom D27). Until this ran, the
    # two lines printed "OFF the drift's path ... moved by
    # HEADLINE_DIRECTION_COVERAGE: True" and stopped -- a reader could not tell
    # from this output that the belief numbers had no measured resolution at
    # all. A control living only in the tests is one the reader about to quote
    # a belief gap never meets (the D25 rule).
    _own = measure_own_drift_resolution(n_customers=300)
    print("  [memory-resolution control] company holds the wrong DD/rail "
          f"failure lookback window (world untouched), seeds "
          f"{RESOLUTION_SEEDS}:")
    for dim, row in _own.items():
        entry = DIMENSION_DRIFT_RESOLUTION[dim]
        book = row["book"]
        print(f"           {dim:<22} blind to {row['unmoved']}, "
              f"sees {row['moved']} (atom {entry['own_debt_atom']})")
        # ATOM D28: the SAME shared rule the on-path lines above now print,
        # re-deriving D27's saturation edge from the readings alone. ATOM D29:
        # on a grid derived from the BOOK rather than from this register's own
        # claims, and BOTH edges are printed -- the low one existed all along
        # and no sparse grid could reach it.
        print(f"           {'':<22} saturates below "
              f"{row['saturates_below']}d (atom "
              f"{entry['own_saturation_atom_below']}) / above "
              f"{row['saturates_above']}d (atom "
              f"{entry['own_saturation_atom_above']}), "
              f"{len(row['collapsed_runs'])} collapsed run(s) on the "
              f"{len(row['drifts'])}-point book-derived grid [shared rule]")
        print(f"           {'':<22} book: {book['n_events']} failure events, "
              f"oldest {book['oldest_event_age_days']}d / youngest "
              f"{book['newest_event_age_days']}d vs a "
              f"{book['window_days']}d memory -> "
              + ("SATURATED, so every longer memory -- to infinity -- "
                 f"publishes ONE number ({book['headroom_days']}d headroom), "
                 f"and every memory of {book['amnesia_floor_window_days']}d or "
                 "less counts nothing and publishes another"
                 if book["saturated"] else "not saturated"))
    _own_violations = check_own_drift_resolution(_own)
    print("           verdict: "
          + ("every declaration held" if not _own_violations
             else f"{len(_own_violations)} VIOLATION(S)"))
    for v in _own_violations:
        print(f"           !! {v}")

    # THE AGEING RESOLUTION (atom D25), predicted from THIS run's own book and
    # printed beside the sweep it is checked against -- the reader about to
    # quote an ageing displacement is exactly who needs to know how wrong the
    # company would have to be for that number to move. The flat book beside it
    # is what makes the claim differential rather than an assertion.
    # Read back off the published components rather than re-measured here: what
    # the CLI prints is then literally the caveat the figure carries, and a
    # stamping that silently stopped happening cannot be papered over by the
    # printer recomputing it (the D22 stamping lesson).
    _ac = result["ageing"].components
    _res = {**_ac["ageing_resolution_book"],
            "over_ageing_days": _ac["ageing_resolution_days"]["over_ageing"],
            "under_ageing_days": _ac["ageing_resolution_days"]["under_ageing"]}
    _flat_recs, _fc, _fl, _flat_as_of = build_scenario(
        min(args.customers, 300), seed=args.seed, cycle_spread_days=1)
    _flat = measure_ageing_resolution(_flat_recs, _flat_as_of)
    print("  [ageing-resolution control] smallest company dating error this "
          "book can resolve, predicted from the population:")
    for label, r in (("this book (staggered)", _res), ("flat book", _flat)):
        print(f"           {label:<22} over-ageing {r['over_ageing_days']}d / "
              f"under-ageing {r['under_ageing_days']}d "
              f"({r['n_distinct_ages']} distinct ages over "
              f"{r['age_span_days']} days)")
    _res_violations = check_ageing_resolution(_res, _ddr)
    print("           verdict: "
          + ("prediction and drift sweep agree, target met"
             if not _res_violations
             else f"{len(_res_violations)} VIOLATION(S)"))
    for v in _res_violations:
        print(f"           !! {v}")

    print(f"  allocation note: {result['notes']['allocation']}")

    # THE COVERAGE-ONLY RESIDUAL (atom D20). Printed beside the headline it
    # qualifies rather than left to the test suite: the claim that the belief
    # dimension's two sides differ ONLY in coverage is what makes that number a
    # measure of the wall, and a reader of this output is exactly who is
    # entitled to it. It builds a second population, so it is off by default at
    # the CLI's 4000-customer setting and sized separately.
    if args.coverage_residual:
        cov = measure_coverage_only_residual(
            n_customers=args.coverage_residual_customers, seed=args.seed)
        w = cov["witnesses"]
        print(f"  [coverage-only residual] counterfactual all-DD population, "
              f"n={cov['n_customers']}, VACUOUS={cov['is_vacuous']}")
        for dim, v in cov["residuals"].items():
            claim = "CLAIMS coverage-only" if v["claims_coverage_only"] else "exempt"
            print(f"      {dim:<24} {claim:<21} residual={v['residual']:.6f} "
                  f"(on the scored book {v['gap_on_the_scored_book']:.6f})")
        print(f"      witnesses: coverage loss removed from the scored book "
              f"{w['coverage_loss_removed']} non-DD true failures; "
              f"counterfactual non-DD failures {w['cf_non_dd_failures']}; "
              f"error populations {w['cf_undercall_population']}/"
              f"{w['cf_overcall_population']}; exempt dimensions reading "
              f"non-zero {w['n_exempt_dimensions_nonzero']}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        commit = _git_head()
        # ONE bare-keyed entry per pair -- the contract coupled_triad.gap_measured()
        # + the Proof door (_coupled_gaps) read. Do NOT write ::suffixed keys: they
        # are not map-coupled pairs, so the Proof door counts them as unmapped extras
        # and wedges the publish gate (the 2026-07-18 lesson). The headline is the
        # DETECTION gap (the core belief-vs-truth divergence -- the no-remittance
        # blind spot); the belief/ageing gaps ride inline in the note, and the full
        # per-dimension detail lives in the result's components for a reader.
        headline: GapResult = result["detection"]
        # DO NOT CLOBBER `det.note`, APPEND TO IT (H27 Expert Hour, 2026-08-09).
        # This branch used to overwrite the measured note with one sentence --
        # "the fraction of true payment failures the company NEVER OBSERVES
        # through the seam -- the no-remittance blind spot" -- which D10 measured
        # FALSE (n_undetected == 0 on seeds 7/11/23; the residual is detections
        # the company UN-made under oldest-first allocation) and which D11 then
        # made wrong a second way (the headline is a BALANCED error over two
        # directions, not a fraction of failures at all). Both callers write the
        # SAME bare `WORLD_ATOM_ID` key, so whichever ran last decided what the
        # Proof door showed: the live path's note was corrected on 2026-08-09 and
        # this offline sibling was left behind, publishing the refuted sentence
        # over the corrected one. The corrected description is `det.note`, built
        # from the measurement a few hundred lines above -- so the ledger gets
        # THAT, with the headline framing and the companions in front of it.
        headline.note = (
            "HEADLINE = the BALANCED DETECTION error of the W2_11 payment TRUTH "
            "vs D5's belief: the mean of missed_failure_rate (over the "
            "truly-failed) and false_flag_rate (over the never-flaggable), each "
            "on its own denominator, g0 = 0.5 for EVERY prevalence-blind rule "
            "including flagging everything (atom D11). It is NOT a fraction of "
            "failures the company never observes -- that description was "
            "measured false by D10 and is not what any figure here counts. "
            f"{format_detection_summary(headline)}. Companion per-dimension "
            f"gaps: {format_belief_summary(result['belief'])} "
            "[RESHAPED 2026-08-10, atom D19: the population-TV belief figure "
            "that used to sit here was permutation-invariant -- 'right mix, "
            "every individual wrong' scored what the real company scored -- and "
            "is now published as its own dimension, belief_population_mix "
            f"{result['belief_population_mix'].gap:.4f}, under the name it "
            "always measured]; "
            f"{format_detection_latency_summary(result['detection_latency'])}; "
            f"{format_ageing_summary(result['ageing'])}; allocation honestly "
            "dropped (metric-shape mismatch). ONE NAME, ONE NUMBER (atom D16, "
            "2026-08-09): the wrongful-dunning exposure is `false_flag_rate` "
            "above and NOTHING ELSE. Until D16 the ageing dimension published "
            "its `overstated_arrears_rate` under the same name over a "
            "population carrying no exclusion band, so one output block gave a "
            "reader two numbers 3.5x apart for one real-world quantity. Both "
            "dimensions now score the SAME never-flaggable population -- "
            "measured as the identical case set, not merely the same size -- "
            "and the ageing rate is renamed to what it measures: the ageing "
            "REPORT's overstatement AT `as_of`. The residual between them is "
            "belief-side and deliberate (detection is EVER-CHASED, because "
            "wrongful dunning is an event that happened to a customer; ageing "
            "is the `as_of` snapshot, because a misstatement is a fact about "
            "the report today), and ageing's cases were measured to be a "
            "STRICT SUBSET of detection's at seeds 7/11/23 and two grace "
            "windows. The declared relationship is held and measured by "
            "SHARED_QUANTITY_CONTRACT. R12: diagnostic, not "
            "a target. == THE MEASURED NOTE FOLLOWS == " + (headline.note or "")
        )
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, headline,
            measured_at=measured_at, run_git_commit=commit,
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
