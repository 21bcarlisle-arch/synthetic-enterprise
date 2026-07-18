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
  * ageing -> `misapplication_gap` (formula e). Per invoice, the TRUE 30/60/
    90+ bucket (`company.billing.arrears_engine.age_bucket`, applied to the
    true "did this genuinely resolve by as_of" fact) vs the BELIEF bucket
    read off the company's own open-item ageing
    (`PaymentObservationConsumer.snapshot().aged_items`). Both sides use the
    IDENTICAL bucket function -- the bucket SET is small and shared
    (current/30-60/60-90/90+), which is what makes a majority-class baseline
    meaningful here (unlike allocation, see below).
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
from typing import Dict, List, Optional, Tuple

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
    belief_gap,
    detection_gap,
    misapplication_gap,
    write_gap_entry,
)

WORLD_ATOM_ID = "W2_11_payment_behaviour_source"
TWIN_ATOM_ID = "D5_payment_observation_consumer"

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
    """Build the scenario and score all three gap dimensions. Returns a dict
    of {"detection": GapResult, "belief": GapResult, "ageing": GapResult,
    "stats": {...}, "notes": {...}}."""
    records, consumer, ledger_book, as_of = build_scenario(n_customers, seed=seed)

    by_customer: Dict[str, List[PeriodRecord]] = {}
    for r in records:
        by_customer.setdefault(r.customer_id, []).append(r)

    # ------------------------------------------------------------------
    # (1) DD-failure detection
    # ------------------------------------------------------------------
    truth_set = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    flagged_set: set = set()

    # ------------------------------------------------------------------
    # (2) Belief severity + (3) ageing -- both need one snapshot per account
    # ------------------------------------------------------------------
    true_severity_labels: List[str] = []
    belief_severity_labels: List[str] = []
    true_ageing_labels: List[str] = []
    belief_ageing_labels: List[str] = []

    n_true_dd_failures = 0
    n_true_non_dd_failures = 0
    n_flagged_non_dd = 0  # sanity: should stay 0 -- the blind spot's own witness

    for cid, periods in by_customer.items():
        account_id = periods[0].account_id
        snapshot = consumer.snapshot(account_id, as_of=as_of, payment_terms_days=PAYMENT_TERMS_DAYS)

        due_to_period = {r.due_date: r.period_index for r in periods}
        for dd_fail in snapshot.recent_dd_failures:
            p = due_to_period.get(dd_fail.value_date)
            if p is not None:
                flagged_set.add((cid, p))

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

            ai = aged_by_ref.get(r.invoice_ref)
            belief_ageing_labels.append(ai.bucket if ai is not None else "current")

    for (cid, p) in flagged_set:
        rec = next(r for r in by_customer[cid] if r.period_index == p)
        if rec.payment_method != DIRECT_DEBIT:
            n_flagged_non_dd += 1  # would indicate a leak -- should never increment

    det = detection_gap(truth_set, flagged_set)
    det.note = (
        "W2_11 true payment failure (any channel) vs D5's DD-failure-observed "
        "belief; the no-remittance blind spot (non-DD failure -> no WallResponse "
        "at all) is structurally undetectable, guaranteeing gap > 0."
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

    age = misapplication_gap(true_ageing_labels, belief_ageing_labels)
    age.note = (
        "per-invoice 30/60/90+ ageing bucket: truth (resolved-by-as_of fact) vs "
        "D5's own open-item ageing belief; picks up both the raw non-payment "
        "signal and any allocation cross-contamination from the ambiguous-"
        "remittance non-DD population (see module 'ON ALLOCATION' note)."
    )

    stats = {
        "n_customers": n_customers,
        "n_periods_per_customer": N_PERIODS,
        "n_cases": len(records),
        "as_of": as_of.isoformat(),
        "n_true_failures": len(truth_set),
        "n_true_dd_failures": n_true_dd_failures,
        "n_true_non_dd_failures": n_true_non_dd_failures,
        "n_flagged_failures": len(flagged_set),
        "n_flagged_non_dd_failures": n_flagged_non_dd,
    }
    notes = {
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

    for name in ("detection", "belief", "ageing"):
        r: GapResult = result[name]
        print(f"  [{name}] raw_gap={r.raw_gap:.4f}  g0={r.g0:.4f}  GAP={r.gap}")

    print(f"  allocation note: {result['notes']['allocation']}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        commit = _git_head()
        # HEADLINE entry under the BARE world_atom_id -- this is the contract
        # background/coupled_triad.gap_measured() reads to unblock W2_11->L3
        # (all pairs carry one bare-keyed entry). The detection gap is the
        # headline: it is the core belief-vs-truth divergence (the no-remittance
        # blind spot -- non-DD failures the company never observes). The belief
        # and ageing gaps are kept as ::suffixed detail entries alongside.
        headline: GapResult = result["detection"]
        headline.note = (
            "HEADLINE = DD/non-DD failure DETECTION gap (fraction of true payment "
            "failures the company never observes through the seam -- the "
            "no-remittance blind spot). Companion per-dimension gaps in the "
            f"::belief ({result['belief'].gap:.4f}) and ::ageing "
            f"({result['ageing'].gap:.4f}) entries; allocation honestly dropped "
            "(metric-shape mismatch). R12: diagnostic, not a target."
        )
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, headline,
            measured_at=measured_at, run_git_commit=commit,
        )
        print(f"  ledger written (HEADLINE): {WORLD_ATOM_ID} -> "
              f"gap={ledger[WORLD_ATOM_ID]['gap']}")
        for name in ("detection", "belief", "ageing"):
            r: GapResult = result[name]
            ledger = write_gap_entry(
                f"{WORLD_ATOM_ID}::{name}", TWIN_ATOM_ID, r,
                measured_at=measured_at, run_git_commit=commit,
            )
            print(f"  ledger written: {WORLD_ATOM_ID}::{name} -> "
                  f"gap={ledger[f'{WORLD_ATOM_ID}::{name}']['gap']}")


if __name__ == "__main__":
    main()
