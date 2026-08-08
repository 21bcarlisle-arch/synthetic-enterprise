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
    Per invoice, the TRUE 30/60/90+ bucket (`company.billing.arrears_engine.
    age_bucket`, applied to the true "did this genuinely resolve by as_of"
    fact) vs the BELIEF bucket read off the company's own open-item ageing
    (`PaymentObservationConsumer.snapshot().aged_items`). Both sides use the
    IDENTICAL bucket function.
    THIS DIMENSION USED `misapplication_gap` AND NO LONGER DOES. The D6
    DISCOVER (docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md) refuted
    that shape three ways against the unchanged criterion: gap>1 did NOT mean
    worse-than-no-skill; prevalence alone swung the score twentyfold with the
    company held literally fixed; and a Hamming error rate is blind to bucket
    ORDER (believing a 90+ debt is 60-90 scored the same as not seeing it).
    The buckets are ORDERED, so the dimension now reports date DISPLACEMENT
    plus the two error directions on their own denominators -- understated
    (debt believed settled) and overstated (the wrongful-dunning exposure) --
    and carries no prevalence-shaped baseline at all.
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
import hashlib
import subprocess
from datetime import date, datetime, time, timedelta, timezone
from typing import Callable, Dict, List, Optional, Tuple

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
from company.billing.arrears_engine import age_bucket as company_age_bucket
from company.billing.payment_observation_consumer import PaymentObservationConsumer

from background.gap_metric import (
    GapResult,
    ageing_gap,
    belief_gap,
    detection_gap,
    format_ageing_summary,
    write_gap_entry,
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
        "dd_failure_reason", "correlation_id",
    )

    def __init__(self, customer_id, period_index, invoice_ref, account_id,
                 due_date, issue_date, payment_method, result,
                 dd_failure_reason, correlation_id):
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


def build_scenario(
    n_customers: int, seed: Optional[int] = None
) -> Tuple[List[PeriodRecord], PaymentObservationConsumer, LedgerBook, date]:
    """Run the coupled loop over `n_customers` resi households x `N_PERIODS`
    billing periods each. Returns (truth_records, consumer, ledger_book,
    as_of). The consumer is fed EXCLUSIVELY through
    `simulation.payment_seam_adapter.emit_wall_responses` -- it never sees a
    `PeriodRecord`/`PaymentEvent` (R15 independence, proven in the test
    suite's `test_consumer_never_receives_theta`)."""
    ledger_book = LedgerBook()
    consumer = PaymentObservationConsumer(
        ledger_book=ledger_book, dd_failure_window_days=DD_FAILURE_WINDOW_DAYS
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
        method = generate_payment_method(cid, fuel="electricity")
        account_id = f"ACC-{cid}"

        for p in range(N_PERIODS):
            due = FIRST_DUE_DATE + timedelta(days=PERIOD_SPACING_DAYS * p)
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
            ))

    last_due = FIRST_DUE_DATE + timedelta(days=PERIOD_SPACING_DAYS * (N_PERIODS - 1))
    as_of = last_due + timedelta(days=AS_OF_BUFFER_DAYS)
    return records, consumer, ledger_book, as_of


def measure(n_customers: int = 4000, seed: Optional[int] = None) -> Dict[str, object]:
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
    return score_triad(records, consumer, as_of)


def score_triad(
    records: List[PeriodRecord],
    consumer: PaymentObservationConsumer,
    as_of: date,
    payment_terms_days: int = PAYMENT_TERMS_DAYS,
) -> Dict[str, object]:
    """Score the three gap dimensions (detection / belief / ageing) for a
    coupled-triad population.

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

    n_true_dd_failures = 0
    n_true_non_dd_failures = 0
    n_flagged_non_dd_via_dd_channel = 0   # the LEAK witness: must stay 0
    n_flagged_non_dd_via_reconciliation = 0  # the carve-out witness: expected > 0
    detection_latency_days: List[int] = []  # latency of each detected miss (ruling §1)
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
        snapshot = consumer.snapshot(account_id, as_of=as_of, payment_terms_days=payment_terms_days)

        due_to_period = {r.due_date: r.period_index for r in periods}
        ref_to_period = {r.invoice_ref: r.period_index for r in periods}
        for dd_fail in snapshot.recent_dd_failures:
            p = due_to_period.get(dd_fail.value_date)
            if p is not None:
                flagged_via_dd_channel.add((cid, p))
            else:
                n_unjoined_dd_failures += 1
        for miss in snapshot.detected_collection_misses:
            p = ref_to_period.get(miss.invoice_ref)
            if p is not None:
                flagged_via_reconciliation.add((cid, p))
                detection_latency_days.append(miss.days_latency)
            else:
                n_unjoined_collection_misses += 1

        n_unresolved_true = sum(1 for r in periods if r.result == "failed")
        n_hardship_true = sum(
            1 for r in periods
            if r.result == "failed" and r.dd_failure_reason == INSUFFICIENT_FUNDS
        )
        true_severity_labels.append(_severity_label(n_unresolved_true, n_hardship_true))
        belief_severity_labels.append(snapshot.arrears_risk_belief.value)

        aged_by_ref = {ai.reference: ai for ai in snapshot.aged_items}
        for r in periods:
            if r.result == "failed":
                n_true_dd_failures += 1 if r.payment_method == DIRECT_DEBIT else 0
                n_true_non_dd_failures += 1 if r.payment_method != DIRECT_DEBIT else 0
                true_days_overdue = (as_of - r.due_date).days
                true_ageing_labels.append(company_age_bucket(true_days_overdue))
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

    det = detection_gap(truth_set, flagged_set)
    det.note = (
        "W2_11 true payment failure (any channel) vs D5's belief, now via TWO "
        "detection paths: observed Bacs/rail failure events AND expected-collection "
        "reconciliation (own bills vs own cash -- director ruling 2026-07-25 §2). "
        "The reconciliation path narrows the push-channel blind spot but never "
        "closes it: a late-but-eventual payment (cash by as_of) is correctly NOT "
        "flagged (detection LATENCY, ruling §1), guaranteeing gap > 0 (R12)."
    )

    bel = belief_gap(
        _severity_distribution(true_severity_labels),
        _severity_distribution(belief_severity_labels),
    )
    bel.note = (
        "population TV distance between the TRUE arrears-severity distribution "
        "(all-channel unresolved-failure count) and D5's own arrears_risk_belief "
        "distribution (DD/rail-observed count only) -- same threshold shape, "
        "different-coverage inputs."
    )

    age = ageing_gap(true_ageing_labels, belief_ageing_labels)
    age.note = (
        "per-invoice 30/60/90+ ageing bucket: truth (resolved-by-as_of fact) vs "
        "D5's own open-item ageing belief; picks up both the raw non-payment "
        "signal and any allocation cross-contamination from the ambiguous-"
        "remittance non-DD population (see module 'ON ALLOCATION' note). "
        "D7 RESHAPE (2026-08-08): three measures on their own denominators, NOT "
        "one prevalence-normalised scalar -- headline `gap` is mean bucket "
        "DISPLACEMENT (buckets, no baseline); read understated_arrears_rate and "
        "overstated_arrears_rate (the wrongful-dunning exposure) in components."
    )

    n_customers = len(by_customer)
    _lat = sorted(detection_latency_days)
    latency_summary = {
        "n": len(_lat),
        "min_days": _lat[0] if _lat else None,
        "median_days": _lat[len(_lat) // 2] if _lat else None,
        "max_days": _lat[-1] if _lat else None,
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
        # Detection LATENCY distribution (ruling §1: register the lag, do not
        # compress it to zero). Days between an invoice's due date and the
        # as_of at which reconciliation first observed the shortfall.
        "detection_latency_days": latency_summary,
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
            "measured limit of this metric, never tuned away (R12)."
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
    return {"detection": det, "belief": bel, "ageing": age, "stats": stats, "notes": notes}


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
) -> Tuple[Dict[str, set], Dict[str, set]]:
    """(truth_by_part, flagged_by_part) -- the shared partitioning both the
    gap scorer and the emission-prep reuse. Each failed (customer, period) case
    is attributed to `partition_of(record)`; each observed DD-failure is mapped
    back to the partition of the exact case its `value_date` matches (so a
    customer spanning regimes contributes each period to the right cell, no
    double-count). `partition_of` reads ONLY the harness-held PeriodRecord."""
    by_customer: Dict[str, List[PeriodRecord]] = {}
    for r in records:
        by_customer.setdefault(r.customer_id, []).append(r)

    truth_by_part: Dict[str, set] = {}
    flagged_by_part: Dict[str, set] = {}
    for cid, periods in by_customer.items():
        account_id = periods[0].account_id
        snapshot = consumer.snapshot(
            account_id, as_of=as_of, payment_terms_days=payment_terms_days
        )
        due_to_period = {r.due_date: r.period_index for r in periods}
        ref_to_period = {r.invoice_ref: r.period_index for r in periods}
        rec_by_period = {r.period_index: r for r in periods}
        for r in periods:
            if r.result == "failed":
                truth_by_part.setdefault(partition_of(r), set()).add((cid, r.period_index))
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
    return truth_by_part, flagged_by_part


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

    truth_by_part, flagged_by_part = _detection_sets_by_partition(
        records, consumer, as_of, regime_of, payment_terms_days
    )
    out: Dict[str, object] = {}
    for regime in set(truth_by_part) | set(flagged_by_part):
        truth = truth_by_part.get(regime, set())
        flagged = flagged_by_part.get(regime, set())
        if not truth:
            continue  # no true failures in this regime -> nothing measured here
        gap = detection_gap(truth, flagged).gap
        if gap is None:
            continue
        cell_id = f"{archetype}_{regime}"
        out[cell_id] = CellMeasurement(
            detection_gap=float(gap),
            true_failures=len(truth),
            believed_failures=len(flagged),
            regime_label=regime,
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
    truth_by_part, flagged_by_part = _detection_sets_by_partition(
        records, consumer, as_of, partition_of, payment_terms_days
    )

    out: Dict[str, GapResult] = {}
    for key in set(truth_by_part) | set(flagged_by_part):
        res = detection_gap(truth_by_part.get(key, set()), flagged_by_part.get(key, set()))
        res.note = (
            f"partition {key!r}: W2_11 true payment failure (any channel) vs "
            "D5's DD-failure-observed belief, over ONLY this partition's cases "
            "(world-side partition, never leaked company-side). The non-DD "
            "no-remittance blind spot recurs here by construction (R12/R13) -- "
            "a near-zero gap would be a leak, not a win."
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
    print(f"  flagged failures (belief) : {stats['n_flagged_failures']}"
          f"  (non-DD leaked: {stats['n_flagged_non_dd_failures']})")

    for name in ("detection", "belief"):
        r: GapResult = result[name]
        print(f"  [{name}] raw_gap={r.raw_gap:.4f}  g0={r.g0:.4f}  GAP={r.gap}")
    # Ageing is NOT a g0-normalised score (D7) -- printing it in the same
    # raw_gap/g0/GAP shape as the other two is exactly how the old scalar got
    # read as one. Its three measures print with their units instead.
    print(f"  [ageing] {format_ageing_summary(result['ageing'])}")

    print(f"  allocation note: {result['notes']['allocation']}")

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
        headline.note = (
            "HEADLINE = DD/non-DD failure DETECTION gap (fraction of true payment "
            "failures the company never observes through the seam -- the "
            "no-remittance blind spot). Companion per-dimension gaps: belief "
            f"{result['belief'].gap:.4f}, {format_ageing_summary(result['ageing'])}; "
            "allocation honestly dropped (metric-shape mismatch). R12: diagnostic, "
            "not a target."
        )
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, headline,
            measured_at=measured_at, run_git_commit=commit,
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
