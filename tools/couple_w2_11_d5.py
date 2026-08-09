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
from company.billing.payment_observation_consumer import (
    DEFAULT_RECONCILIATION_GRACE_DAYS,
    PaymentObservationConsumer,
)

from background.gap_metric import (
    GapResult,
    ageing_gap,
    belief_gap,
    detection_measures,
    format_ageing_summary,
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
                days_late=event.days_late,
            ))

    last_due = FIRST_DUE_DATE + timedelta(days=PERIOD_SPACING_DAYS * (N_PERIODS - 1))
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
        # POINT-IN-TIME WITNESS: a DD failure whose bank-feed report date falls
        # AFTER `as_of` is not yet knowable and is not counted as knowledge.
        "n_dd_observed_after_as_of": int(n_dd_observed_after_as_of),
        "headline_units": DETECTION_LATENCY_HEADLINE_UNITS,
        "normalisation": DETECTION_LATENCY_NO_NORMALISER_REASON,
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
        "why": "HOLDS. Severity distributions over settled facts.",
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
        "counts_both_error_directions": False,
        "scorer": "background.gap_metric.detection_gap",
        "why": (
            "NAMED DEBT, REASON CORRECTED 2026-08-09 by the D13 DISCOVER. NOT "
            "the same shape as W2_5<->C7 -- bracketing the two was the error. "
            "This negative is settled and unambiguous (RationingLabel."
            "NOT_RATIONING is a Bernoulli outcome), but the measure is VACUOUS: "
            "0 of 3752 non-rationers have ANY consumption drop and 0 are "
            "flaggable under any weather factor, so the false-flag rate is "
            "0.0000 for any drop-based detector. Publishing it would report a "
            "property of the WORLD as detector precision (R12). Recall-only "
            "until W2_8 emits non-rationers who genuinely drop -- a world-depth "
            "gap, not a metric gap."
        ),
        "debt_atom": "D14_w2_8_needs_negative_drops",
    },
}




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
    reconciliation_grace_days: int = DEFAULT_RECONCILIATION_GRACE_DAYS,
) -> Dict[str, object]:
    """Score the four gap dimensions (detection / detection_latency / belief /
    ageing) for a coupled-triad population.

    `reconciliation_grace_days` is passed EXPLICITLY to the consumer rather than
    left to its default, because the detection-LATENCY dimension asks the same
    organ for its earliest detection date -- a scorer using one grace window and
    a consumer using another would read a latency that belongs to neither.

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
        snapshot = consumer.snapshot(
            account_id, as_of=as_of, payment_terms_days=payment_terms_days,
            reconciliation_grace_days=reconciliation_grace_days,
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
        candidates = sorted({
            r.due_date + timedelta(days=reconciliation_grace_days) for r in periods
        })
        for cand in candidates:
            if cand > as_of:
                continue
            for m in consumer.expected_collection_misses(
                account_id, as_of=cand, grace_days=reconciliation_grace_days,
                payment_terms_days=payment_terms_days,
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
        true_severity_labels.append(_severity_label(n_unresolved_true, n_hardship_true))
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

    lat = detection_latency_gap(
        dd_lag_days, recon_lag_days,
        n_true_failures=len(truth_set),
        n_recon_detected_undated=n_recon_detected_undated,
        n_dd_observed_after_as_of=n_dd_observed_after_as_of,
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
        "band was, and the rate followed it."
    )

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
    return {"detection": det, "detection_latency": lat, "belief": bel, "ageing": age,
            "stats": stats, "notes": notes, "sets": sets,
            "ageing_inputs": ageing_inputs}


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
    r_bel: GapResult = result["belief"]
    print(f"  [belief] raw_gap={r_bel.raw_gap:.4f}  g0={r_bel.g0:.4f}  GAP={r_bel.gap}")
    # Ageing is NOT a g0-normalised score (D7) -- printing it in the same
    # raw_gap/g0/GAP shape as the other two is exactly how the old scalar got
    # read as one. Its three measures print with their units instead.
    print(f"  [ageing] {format_ageing_summary(result['ageing'])}")
    # Detection latency is not g0-normalised either -- it is an absolute mean in
    # days (D10). It prints with its counterfactual because the counterfactual
    # is the finding: the DD channel moves THIS and not the detection gap.
    print(f"  [detection_latency] {format_detection_latency_summary(result['detection_latency'])}")

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
            f"gaps: belief {result['belief'].gap:.4f}; "
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
