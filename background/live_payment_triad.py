"""LIVE per-run wiring of the W2_11 <-> D5 payment coupled triad.

This is the L3-escalation of the payment triad: the SAME belief-vs-truth flow
already built + tested OFFLINE in `tools/couple_w2_11_d5.py` (a frozen synthetic
population), run LIVE inside `simulation/run_phase2b.py` over the real run
population, once per run, writing the measured gap into the coupled gap ledger.

THE COUPLED LOOP, LIVE (COUPLED_TRIAD_DESIGN.md 1.3):

  1. SIM depth   -- `simulation.payment_behaviour_source.generate_payment_event`
                    is the CANONICAL payment TRUTH for each (customer, period).
                    run_phase2b's old `payment_timing.generate_payment_record`
                    path is REPLACED by this event; the analytics dict the run
                    still needs (`PaymentBehaviourAnalytics.record_payment`) is
                    DERIVED from this one event, so there is exactly ONE payment
                    reality per customer/period (never two generators drawing
                    conflicting results).
  2. COMPANY copes -- that truth crosses the W4_4 seam
                    (`simulation.payment_seam_adapter.emit_wall_responses`) into
                    `WallResponse`s -- the ONLY thing the company ever sees --
                    and `company.billing.payment_observation_consumer` turns the
                    stream into belief. The consumer NEVER receives the
                    `PaymentEvent` (epistemic wall; proven by the D5 module's own
                    AST import-freedom test and the offline
                    `test_consumer_never_receives_theta`).
  3. HARNESS measures -- at run end this module scores the belief-vs-truth GAP
                    using `tools.couple_w2_11_d5.score_triad` (the SAME scorer
                    the offline harness uses -- no bespoke live metric, R15
                    independence) and writes the DETECTION headline into
                    `docs/observability/coupled_gap_ledger.json` via
                    `background.gap_metric.write_gap_entry`.

WHY THIS MODULE LIVES IN background/ (NOT company/ or saas/): it is HARNESS
code -- the one place permitted to hold the hidden SIM truth (`PaymentEvent` /
`PeriodRecord`) and the company's observable-only belief (the consumer) side by
side to compute the gap (design 1.3). background/ is exempt from the epistemic
verifier's company/saas import scan for exactly this reason, identical to
`tools/couple_w2_11_d5.py`. The company-side consumer it drives still sees ONLY
`WallResponse`s -- the wall is intact.

DETERMINISM (C-S2): `period_index` is derived deterministically from the
billing month (`year*12 + (month-1)`), never from iteration order, so the
per-customer/per-period substream draw in `generate_payment_event` is
reproducible run-to-run. This module makes no clock/random draw of its own;
`measured_at`/`run_git_commit` are gathered by the caller-facing helper only at
write time and passed straight through to `write_gap_entry` (which never calls a
clock).

RECENCY-WINDOW NOTE: the consumer is constructed with a run-spanning
`dd_failure_window_days` (`_RUN_SPANNING_WINDOW_DAYS`). The DETECTION headline
(the ledger entry) reads `snapshot().recent_dd_failures`, which is NOT
window-limited, so the headline is window-independent regardless. The window
only affects `arrears_risk_belief`, which feeds the companion BELIEF gap; over a
multi-year live run it must span the whole run so the belief-severity count is
on the SAME all-time basis as the truth-severity count -- otherwise the two
would diverge on a recency artefact rather than on the channel blind spot this
triad is built to measure (the offline scorer's own 400-day window covers its
whole 3-period scenario for the identical reason).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional

from simulation.payment_behaviour_source import (
    DIRECT_DEBIT,
    generate_payment_event,
    generate_payment_method,
)
from simulation.payment_seam_adapter import SeamAdapterInput, emit_wall_responses

from company.billing.account_ledger import (
    LedgerBook,
    LedgerEvent,
    LedgerEventType,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer

from background.gap_metric import GapResult, write_gap_entry
from tools.couple_w2_11_d5 import (
    AS_OF_BUFFER_DAYS,
    PAYMENT_TERMS_DAYS,
    PeriodRecord,
    TWIN_ATOM_ID,
    WORLD_ATOM_ID,
    score_triad,
)

# Run-spanning belief window (see module docstring RECENCY-WINDOW NOTE). A live
# run covers ~2016-2025 (~3650 days); a comfortable ceiling keeps the belief
# severity count on the same all-time basis as the truth count.
_RUN_SPANNING_WINDOW_DAYS = 6000


def _period_index_for(due_date: date) -> int:
    """Deterministic, iteration-order-independent period index for a billing
    month (C-S2). Unique per calendar month, stable run-to-run -- the only
    property `generate_payment_event`'s per-period substream needs."""
    return due_date.year * 12 + (due_date.month - 1)


class LivePaymentTriad:
    """Accumulates the live coupled triad across one run_phase2b invocation.

    Usage (from simulation/run_phase2b.py):
        triad = LivePaymentTriad()
        ...
        analytics_rec = triad.record_period(
            customer_id=cid, due_date=due, amount_gbp=amount,
            income_stress_value=stress_str, segment=cust_segment,
        )
        _payment_analytics.record_payment(cid, analytics_rec)
        ...
        triad.measure_and_write(run_git_commit=head_sha)
    """

    def __init__(self, dd_failure_window_days: int = _RUN_SPANNING_WINDOW_DAYS) -> None:
        self._ledger_book = LedgerBook()
        self._consumer = PaymentObservationConsumer(
            ledger_book=self._ledger_book,
            dd_failure_window_days=dd_failure_window_days,
        )
        self._records: List[PeriodRecord] = []
        # persistent per-customer method archetype cache (drawn once, C-S2)
        self._method_cache: dict = {}

    @property
    def consumer(self) -> PaymentObservationConsumer:
        return self._consumer

    @property
    def records(self) -> List[PeriodRecord]:
        return self._records

    def _method_for(self, customer_id: str) -> str:
        m = self._method_cache.get(customer_id)
        if m is None:
            # Method is a persistent per-customer archetype (W2_11's own model);
            # drawn once with a fixed fuel so a customer never flips method
            # between their gas and electricity months.
            m = generate_payment_method(customer_id, fuel="electricity")
            self._method_cache[customer_id] = m
        return m

    def record_period(
        self,
        *,
        customer_id: str,
        due_date: date,
        amount_gbp: float,
        income_stress_value: Optional[str],
        segment: str = "resi",
    ) -> dict:
        """Generate the ONE canonical W2_11 payment event for this
        (customer, period), cross the seam + feed the company consumer LIVE,
        record the harness-side truth, and RETURN the derived analytics dict for
        the run's existing `PaymentBehaviourAnalytics`.

        Returns the analytics record (ON_TIME/LATE/DD_FAILED) DERIVED from the
        single W2_11 event -- the caller feeds it to `record_payment`. There is
        never a second, independent payment draw."""
        period_index = _period_index_for(due_date)
        method = self._method_for(customer_id)
        account_id = f"ACC-{customer_id}"
        invoice_ref = f"{customer_id}::{period_index}"
        issue_date = due_date - timedelta(days=PAYMENT_TERMS_DAYS)

        stress = income_stress_value if income_stress_value else "low"
        event = generate_payment_event(
            customer_id, period_index, due_date, amount_gbp, stress, method,
            segment=segment,
        )

        # Post the bill into the COMPANY's own belief ledger so unpaid invoices
        # age (the ageing gap) exactly as the offline scenario does. This is the
        # company's isolated ledger, never the run's main treasury ledger.
        self._ledger_book.post(LedgerEvent(
            event_id=f"bill:{customer_id}:{period_index}",
            account_id=account_id,
            event_type=LedgerEventType.BILL_DEBIT,
            amount_gbp=amount_gbp,
            valid_time=issue_date,
            transaction_time=datetime.combine(issue_date, time(0, 0)),
            invoice_ref=invoice_ref,
        ))

        # DD payments carry a period-specific remittance (correlation_id ==
        # invoice_ref -> remittance-directed allocation matches the invoice).
        # Non-DD methods carry a still-unique-per-period but deliberately
        # invoice-AMBIGUOUS correlation_id (no remittance advice on a
        # customer-initiated push payment), forcing the ledger's oldest-first
        # fallback -- identical to the offline scenario's seeding.
        if method == DIRECT_DEBIT:
            correlation_id = invoice_ref
        else:
            correlation_id = f"{customer_id}::p{period_index}::ambiguous"
        seam_input = SeamAdapterInput(account_id=account_id, correlation_id=correlation_id)

        for response in emit_wall_responses(event, seam_input):
            self._consumer.observe(response)

        self._records.append(PeriodRecord(
            customer_id=customer_id, period_index=period_index,
            invoice_ref=invoice_ref, account_id=account_id,
            due_date=due_date, issue_date=issue_date,
            payment_method=method, result=event.result,
            dd_failure_reason=event.dd_failure_reason,
            correlation_id=correlation_id,
        ))

        return _derive_analytics_record(customer_id, due_date, amount_gbp, event)

    def measure(self, as_of: Optional[date] = None) -> Optional[dict]:
        """Score the accumulated triad (detection / belief / ageing). Returns
        the score_triad result dict, or None if the run produced no true payment
        failures at all (nothing for the detection metric to measure -- guarded
        rather than raising, so a defensible empty population never crashes)."""
        if not self._records:
            return None
        if not any(r.result == "failed" for r in self._records):
            return None
        if as_of is None:
            as_of = max(r.due_date for r in self._records) + timedelta(days=AS_OF_BUFFER_DAYS)
        return score_triad(self._records, self._consumer, as_of)

    def measure_and_write(
        self,
        run_git_commit: Optional[str] = None,
        as_of: Optional[date] = None,
        ledger_path=None,
    ) -> Optional[dict]:
        """Measure the live gap and write the DETECTION headline into the
        coupled gap ledger (bare `WORLD_ATOM_ID` key -- the Proof door / contract
        reader key; NO ::suffixed keys, which the Proof door counts as unmapped
        extras and would wedge the publish gate). The companion belief/ageing
        gaps ride inline in the note. Returns the full score_triad result (with
        the headline note attached), or None if there was nothing to measure.

        R12: the gap is a DIAGNOSTIC, never a target."""
        result = self.measure(as_of=as_of)
        if result is None:
            return None

        headline: GapResult = result["detection"]
        headline.note = (
            "LIVE per-run coupled-triad gap (W2_11 payment TRUTH -> W4_4 seam -> "
            "D5 consumer belief, measured in-run by run_phase2b). HEADLINE = "
            "DD/non-DD failure DETECTION gap (fraction of true payment failures "
            "the company never observes through the seam -- the no-remittance "
            "blind spot). Companion per-dimension gaps: belief "
            f"{result['belief'].gap:.4f}, ageing {result['ageing'].gap:.4f}; "
            "allocation honestly dropped (metric-shape mismatch). R12: diagnostic, "
            "not a target."
        )
        measured_at = datetime.now(timezone.utc).isoformat()
        write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, headline,
            measured_at=measured_at, run_git_commit=run_git_commit,
            ledger_path=ledger_path,
        )
        return result


def _derive_analytics_record(
    customer_id: str, due_date: date, amount_gbp: float, event
) -> dict:
    """DERIVE the run's legacy analytics dict from the ONE canonical W2_11
    `PaymentEvent` -- so `PaymentBehaviourAnalytics` is fed from the single
    payment truth, never a second independent draw. Result mapping:

      * event.result == "failed"  -> "DD_FAILED" (unpaid, no cash)
      * event.result == "dispute" -> "DD_FAILED" (NAMED SIMPLIFICATION: the
        legacy analytics vocabulary has only ON_TIME/LATE/DD_FAILED; an I&C/SME
        BACS dispute -- a contested, unresolved collection -- is closest to
        DD_FAILED. Disputes arise only on the bacs/chaps path, i.e. I&C/SME
        segments; the legacy path never produced them for resi.)
      * event.result == "success", days_late>0 -> "LATE"
      * event.result == "success", days_late==0 -> "ON_TIME"

    `days_late` is now carried through (the legacy `generate_payment_record`
    omitted it, so `avg_days_late` was always 0.0); it is a genuine fidelity
    gain, unused by the on_time_rate/dd_fail_rate scoring that drives the churn
    signal."""
    if event.result in ("failed", "dispute"):
        return {
            "customer_id": customer_id,
            "due_date": due_date,
            "result": "DD_FAILED",
            "payment_date": None,
            "amount_gbp": amount_gbp,
            "amount_paid": 0.0,
            "days_late": 0,
        }
    # success
    if event.days_late > 0:
        payment_date = (
            date.fromisoformat(event.payment_date)
            if event.payment_date else due_date + timedelta(days=event.days_late)
        )
        return {
            "customer_id": customer_id,
            "due_date": due_date,
            "result": "LATE",
            "payment_date": payment_date,
            "amount_gbp": amount_gbp,
            "amount_paid": amount_gbp,
            "days_late": event.days_late,
        }
    return {
        "customer_id": customer_id,
        "due_date": due_date,
        "result": "ON_TIME",
        "payment_date": due_date,
        "amount_gbp": amount_gbp,
        "amount_paid": amount_gbp,
        "days_late": 0,
    }
