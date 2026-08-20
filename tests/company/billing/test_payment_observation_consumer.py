"""Tests for `company/billing/payment_observation_consumer.py`, atom
D5_payment_observation_consumer -- the COMPANY-side consumer of the W4_4
payment-observable seam.

Groups:
  (a) basic consumption -> correct allocation / ageing / arrears belief.
  (b) EPISTEMIC test (load-bearing) -- no `sim`/`simulation` import, AST-checked.
  (c) C-S1/C-S3 tolerance -- out-of-order, duplicate, late, missing observations.
  (d) belief tagging -- arrears-risk/mandate fields are explicitly INFERENCE,
      not ground truth, and can be plausibly wrong (not suspiciously "correct").
"""
from __future__ import annotations

import ast
import copy
import dataclasses
import datetime as dt
from pathlib import Path

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.payment_observation_consumer import (
    ArrearsRiskBelief,
    DEFAULT_RECONCILIATION_GRACE_DAYS,
    ExpectedCollectionMiss,
    MandateBeliefState,
    PaymentObservationConsumer,
)
from interface.contracts.payment_observable_seam import (
    AddacsAdvice,
    AddacsAdviceType,
    AuddisReport,
    AuddisStatus,
    BacsArruddOutcome,
    BacsReasonCategory,
    DDOutcomeStatus,
    PaymentNotification,
    PaymentRail,
    RemittanceAdvice,
    SettlementConfirmation,
)
from interface.contracts.wall_envelope import ErrorDetail, WallResponse, WallStatus

MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "company" / "billing" / "payment_observation_consumer.py"
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _resp(payload, correlation_id, observed_at=None, valid_time=None, status=WallStatus.OK, error=None):
    return WallResponse(
        correlation_id=correlation_id,
        status=status,
        schema_version=1,
        observed_at=observed_at or dt.datetime(2026, 1, 15, 9, 0),
        valid_time=valid_time,
        payload=payload if status == WallStatus.OK else None,
        error=error,
    )


def _bill(ledger_book: LedgerBook, account_id: str, invoice_ref: str, amount: float, issue_date: dt.date) -> None:
    ledger_book.post(LedgerEvent(
        event_id=f"bill:{invoice_ref}",
        account_id=account_id,
        event_type=LedgerEventType.BILL_DEBIT,
        amount_gbp=amount,
        valid_time=issue_date,
        transaction_time=dt.datetime.combine(issue_date, dt.time(6, 0)),
        invoice_ref=invoice_ref,
    ))


def _remit_resp(account_id, amount, ref, value_date, corr, observed_at=None):
    return _resp(
        RemittanceAdvice(
            bank_reference=ref, account_id=account_id, amount_gbp=amount,
            rail=PaymentRail.FASTER_PAYMENTS, value_date=value_date,
        ),
        correlation_id=corr, observed_at=observed_at or dt.datetime.combine(value_date, dt.time(10, 0)),
        valid_time=value_date,
    )


def _arrudd_fail_resp(account_id, mandate_ref, amount, reason, value_date, corr, text="unpaid"):
    return _resp(
        BacsArruddOutcome(
            mandate_ref=mandate_ref, account_id=account_id, amount_gbp=amount,
            outcome=DDOutcomeStatus.FAILURE, reason_category=reason, reason_text=text,
            value_date=value_date,
        ),
        correlation_id=corr, observed_at=dt.datetime.combine(value_date, dt.time(6, 0)),
        valid_time=value_date,
    )


def _arrudd_success_resp(account_id, mandate_ref, amount, value_date, corr):
    return _resp(
        BacsArruddOutcome(
            mandate_ref=mandate_ref, account_id=account_id, amount_gbp=amount,
            outcome=DDOutcomeStatus.SUCCESS, reason_category=BacsReasonCategory.OTHER,
            reason_text="", value_date=value_date,
        ),
        correlation_id=corr, observed_at=dt.datetime.combine(value_date, dt.time(6, 0)),
        valid_time=value_date,
    )


def _addacs_resp(account_id, mandate_ref, advice_type, value_date, corr, text="advice"):
    return _resp(
        AddacsAdvice(
            mandate_ref=mandate_ref, account_id=account_id, advice_type=advice_type,
            advice_text=text, value_date=value_date,
        ),
        correlation_id=corr, observed_at=dt.datetime.combine(value_date, dt.time(6, 0)),
        valid_time=value_date,
    )


def _auddis_resp(account_id, mandate_ref, status, value_date, corr, text="status"):
    return _resp(
        AuddisReport(
            mandate_ref=mandate_ref, account_id=account_id, status=status,
            status_text=text, value_date=value_date,
        ),
        correlation_id=corr, observed_at=dt.datetime.combine(value_date, dt.time(6, 0)),
        valid_time=value_date,
    )


# ---------------------------------------------------------------------------
# (a) basic consumption
# ---------------------------------------------------------------------------

def test_remittance_advice_allocates_against_billed_invoice():
    lb = LedgerBook()
    _bill(lb, "ACC-1", "INV-1", 100.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    resp = _remit_resp("ACC-1", 100.0, "INV-1", dt.date(2026, 1, 10), "corr-1")
    assert consumer.observe(resp) is True

    snap = consumer.snapshot("ACC-1", as_of=dt.date(2026, 1, 15))
    assert snap.balance_summary["balance_gbp"] == 0.0
    assert snap.allocation.total_outstanding_gbp == 0.0
    assert snap.allocation.open_items[0].is_settled is True


def test_remittance_partial_leaves_open_item_outstanding_and_ages():
    lb = LedgerBook()
    _bill(lb, "ACC-2", "INV-2", 100.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    resp = _remit_resp("ACC-2", 40.0, "INV-2", dt.date(2026, 1, 10), "corr-2")
    consumer.observe(resp)

    snap = consumer.snapshot("ACC-2", as_of=dt.date(2026, 3, 1), payment_terms_days=14)
    assert snap.balance_summary["arrears_gbp"] == 60.0
    assert snap.allocation.total_outstanding_gbp == 60.0
    # issue 2026-01-01 + 14d terms = due 2026-01-15; as_of 2026-03-01 is 45
    # days overdue -> the 30-60 bucket.
    assert any(it.bucket == "30-60" for it in snap.aged_items)
    assert snap.ageing_buckets["30-60"]["amount_gbp"] == 60.0


def test_successful_dd_collection_posts_cash_and_clears_balance():
    lb = LedgerBook()
    _bill(lb, "ACC-3", "INV-3", 75.0, dt.date(2026, 2, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    resp = _arrudd_success_resp("ACC-3", "MREF-3", 75.0, dt.date(2026, 2, 15), "corr-3")
    consumer.observe(resp)
    snap = consumer.snapshot("ACC-3", as_of=dt.date(2026, 2, 20))
    assert snap.balance_summary["balance_gbp"] == 0.0


def test_failed_dd_records_face_value_observation_not_ground_truth():
    lb = LedgerBook()
    _bill(lb, "ACC-4", "INV-4", 50.0, dt.date(2026, 3, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    resp = _arrudd_fail_resp(
        "ACC-4", "MREF-4", 50.0, BacsReasonCategory.INSUFFICIENT_FUNDS,
        dt.date(2026, 3, 15), "corr-4", text="Refer to payer",
    )
    consumer.observe(resp)
    snap = consumer.snapshot("ACC-4", as_of=dt.date(2026, 3, 20))
    # no cash posted -- invoice still fully outstanding
    assert snap.balance_summary["arrears_gbp"] == 50.0
    assert len(snap.recent_dd_failures) == 1
    obs = snap.recent_dd_failures[0]
    assert obs.reason_category == BacsReasonCategory.INSUFFICIENT_FUNDS
    assert obs.reason_text == "Refer to payer"
    # exactly one observed failure -> WATCH, not a stronger claim
    assert snap.arrears_risk_belief == ArrearsRiskBelief.WATCH


def test_repeated_failures_raise_arrears_risk_belief_but_stay_labelled_belief():
    lb = LedgerBook()
    consumer = PaymentObservationConsumer(ledger_book=lb)
    for i, d in enumerate([dt.date(2026, 4, 1), dt.date(2026, 4, 15), dt.date(2026, 4, 29)]):
        consumer.observe(_arrudd_fail_resp(
            "ACC-5", "MREF-5", 60.0, BacsReasonCategory.INSUFFICIENT_FUNDS, d, f"corr-5-{i}",
        ))
    snap = consumer.snapshot("ACC-5", as_of=dt.date(2026, 5, 1))
    assert snap.arrears_risk_belief == ArrearsRiskBelief.HIGH
    # this is a NAME on the class ArrearsRiskBelief -- structurally an
    # inference type, never a ground-truth type (see (d) group below).


def test_addacs_and_auddis_update_mandate_belief():
    lb = LedgerBook()
    consumer = PaymentObservationConsumer(ledger_book=lb)
    consumer.observe(_auddis_resp(
        "ACC-6", "MREF-6", AuddisStatus.NEW_INSTRUCTION_ACCEPTED, dt.date(2026, 1, 1), "corr-6a",
    ))
    assert consumer.mandate_belief("MREF-6").state == MandateBeliefState.ACTIVE_BELIEVED

    consumer.observe(_addacs_resp(
        "ACC-6", "MREF-6", AddacsAdviceType.PAYER_CANCELLED, dt.date(2026, 2, 1), "corr-6b",
    ))
    assert consumer.mandate_belief("MREF-6").state == MandateBeliefState.LIKELY_DEAD_BELIEVED


def test_mandate_amended_is_at_risk_not_terminal():
    lb = LedgerBook()
    consumer = PaymentObservationConsumer(ledger_book=lb)
    consumer.observe(_addacs_resp(
        "ACC-7", "MREF-7", AddacsAdviceType.PAYER_AMENDED, dt.date(2026, 1, 1), "corr-7",
    ))
    assert consumer.mandate_belief("MREF-7").state == MandateBeliefState.AT_RISK_BELIEVED


def test_settlement_confirmation_does_not_double_count_already_recognised_cash():
    lb = LedgerBook()
    _bill(lb, "ACC-8", "INV-8", 100.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    consumer.observe(_remit_resp("ACC-8", 100.0, "REF-8", dt.date(2026, 1, 5), "corr-8a"))
    consumer.observe(_resp(
        SettlementConfirmation(
            reference="REF-8", account_id="ACC-8", amount_gbp=100.0,
            rail=PaymentRail.FASTER_PAYMENTS, cleared_value_date=dt.date(2026, 1, 6),
        ),
        correlation_id="corr-8b", observed_at=dt.datetime(2026, 1, 6, 9, 0),
        valid_time=dt.date(2026, 1, 6),
    ))
    snap = consumer.snapshot("ACC-8", as_of=dt.date(2026, 1, 10))
    assert snap.balance_summary["balance_gbp"] == 0.0  # not -100 (double credit)


def test_settlement_confirmation_recognises_cash_when_no_prior_advice():
    lb = LedgerBook()
    _bill(lb, "ACC-9", "INV-9", 30.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    consumer.observe(_resp(
        SettlementConfirmation(
            reference="REF-9", account_id="ACC-9", amount_gbp=30.0,
            rail=PaymentRail.CARD, cleared_value_date=dt.date(2026, 1, 6),
        ),
        correlation_id="corr-9", observed_at=dt.datetime(2026, 1, 6, 9, 0),
        valid_time=dt.date(2026, 1, 6),
    ))
    snap = consumer.snapshot("ACC-9", as_of=dt.date(2026, 1, 10))
    assert snap.balance_summary["balance_gbp"] == 0.0


def test_non_ok_response_is_honest_non_update_not_a_crash():
    consumer = PaymentObservationConsumer()
    resp = _resp(None, correlation_id="corr-10", status=WallStatus.NOT_KNOWABLE_YET)
    assert consumer.observe(resp) is True
    resp2 = _resp(None, correlation_id="corr-11", status=WallStatus.ERROR, error=ErrorDetail("E1", "boom"))
    assert consumer.observe(resp2) is True
    # no accounts/mandates created by a non-OK response
    assert consumer.mandate_belief("nonexistent").state == MandateBeliefState.UNKNOWN


# ---------------------------------------------------------------------------
# (b) EPISTEMIC test -- LOAD-BEARING
# ---------------------------------------------------------------------------

def test_no_sim_or_generator_import():
    """The consumer must be structurally unable to see W2_11's ground truth:
    parse the module's own import statements (AST, not a substring grep so a
    docstring mentioning 'sim' can't cause a false pass/fail) and assert no
    `sim`/`simulation` root is ever imported."""
    tree = ast.parse(MODULE_PATH.read_text())
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    forbidden_roots = {"sim", "simulation"}
    assert imported_roots.isdisjoint(forbidden_roots), (
        f"payment_observation_consumer.py imports forbidden root(s): "
        f"{imported_roots & forbidden_roots}"
    )
    # Positive check this test can actually fail (not a tautology): the
    # module DOES import from company/interface/stdlib -- if the parse found
    # nothing at all, the test itself would be broken/vacuous.
    assert imported_roots >= {"company", "interface"}


def test_dd_failure_never_carries_a_generator_truth_field():
    """`DDFailureObservation` must expose only the observable seam's own
    fields -- no segment/hardship/probability field could ever be attached
    even in principle (dataclass fields introspection, not a runtime check)."""
    from company.billing.payment_observation_consumer import DDFailureObservation
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(DDFailureObservation)}
    forbidden_terms = {"segment", "hardship", "probability", "propensity", "true_reason", "ground_truth"}
    assert not (field_names & forbidden_terms)


# ---------------------------------------------------------------------------
# (c) C-S1/C-S3 tolerance: out-of-order, duplicate, late, missing
# ---------------------------------------------------------------------------

def _build_stream():
    return [
        _remit_resp("ACC-X", 50.0, "INV-X1", dt.date(2026, 1, 10), "s-1"),
        _arrudd_fail_resp("ACC-X", "MREF-X", 20.0, BacsReasonCategory.INSUFFICIENT_FUNDS,
                           dt.date(2026, 1, 20), "s-2"),
        _addacs_resp("ACC-X", "MREF-X", AddacsAdviceType.PAYER_AMENDED, dt.date(2026, 1, 25), "s-3"),
        _auddis_resp("ACC-X", "MREF-X", AuddisStatus.NEW_INSTRUCTION_ACCEPTED, dt.date(2026, 1, 5), "s-4"),
        _arrudd_success_resp("ACC-X", "MREF-X", 30.0, dt.date(2026, 2, 1), "s-5"),
    ]


def _snapshot_summary(consumer, account_id, as_of):
    snap = consumer.snapshot(account_id, as_of=as_of)
    return (
        snap.balance_summary["balance_gbp"],
        snap.allocation.total_outstanding_gbp,
        snap.arrears_risk_belief,
        snap.mandate_beliefs["MREF-X"].state if "MREF-X" in snap.mandate_beliefs else None,
        tuple(sorted((k, v["amount_gbp"]) for k, v in snap.ageing_buckets.items())),
    )


def test_order_independence_same_belief_regardless_of_arrival_order():
    lb1, lb2 = LedgerBook(), LedgerBook()
    for lb in (lb1, lb2):
        _bill(lb, "ACC-X", "INV-X1", 50.0, dt.date(2026, 1, 1))

    stream = _build_stream()
    forward = PaymentObservationConsumer(ledger_book=lb1)
    for r in stream:
        forward.observe(r)

    backward = PaymentObservationConsumer(ledger_book=lb2)
    for r in reversed(stream):
        backward.observe(r)

    as_of = dt.date(2026, 3, 1)
    assert _snapshot_summary(forward, "ACC-X", as_of) == _snapshot_summary(backward, "ACC-X", as_of)


def test_shuffled_order_matches_too():
    import random
    lb_ref = LedgerBook()
    _bill(lb_ref, "ACC-X", "INV-X1", 50.0, dt.date(2026, 1, 1))
    ref = PaymentObservationConsumer(ledger_book=lb_ref)
    stream = _build_stream()
    for r in stream:
        ref.observe(r)
    ref_summary = _snapshot_summary(ref, "ACC-X", dt.date(2026, 3, 1))

    rnd = random.Random(42)
    for trial in range(3):
        shuffled = list(stream)
        rnd.shuffle(shuffled)
        lb = LedgerBook()
        _bill(lb, "ACC-X", "INV-X1", 50.0, dt.date(2026, 1, 1))
        c = PaymentObservationConsumer(ledger_book=lb)
        for r in shuffled:
            c.observe(r)
        assert _snapshot_summary(c, "ACC-X", dt.date(2026, 3, 1)) == ref_summary, f"trial {trial} diverged"


def test_duplicate_observation_is_idempotent():
    lb = LedgerBook()
    _bill(lb, "ACC-Y", "INV-Y1", 80.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    resp = _remit_resp("ACC-Y", 80.0, "INV-Y1", dt.date(2026, 1, 10), "corr-dup")

    assert consumer.observe(resp) is True
    first = consumer.snapshot("ACC-Y", as_of=dt.date(2026, 1, 20))

    assert consumer.observe(resp) is False   # duplicate -- rejected at the gate
    assert consumer.observe(copy.deepcopy(resp)) is False  # even a distinct equal object, same correlation_id
    second = consumer.snapshot("ACC-Y", as_of=dt.date(2026, 1, 20))

    assert first.balance_summary == second.balance_summary
    assert second.balance_summary["balance_gbp"] == 0.0  # not -80 (double credited)


def test_late_arrival_reaches_same_state_as_prompt_arrival():
    """A response processed weeks after its value_date reaches the identical
    ledger/allocation state as one processed promptly -- `observed_at`
    (when we learned it) never leaks into the belief maths, only
    `valid_time`/`value_date` (what it's about) does."""
    lb1, lb2 = LedgerBook(), LedgerBook()
    for lb in (lb1, lb2):
        _bill(lb, "ACC-Z", "INV-Z1", 45.0, dt.date(2026, 1, 1))

    prompt = _remit_resp("ACC-Z", 45.0, "INV-Z1", dt.date(2026, 1, 10), "corr-prompt",
                          observed_at=dt.datetime(2026, 1, 10, 9, 0))
    late = _remit_resp("ACC-Z", 45.0, "INV-Z1", dt.date(2026, 1, 10), "corr-late",
                        observed_at=dt.datetime(2026, 3, 1, 9, 0))

    c1 = PaymentObservationConsumer(ledger_book=lb1)
    c1.observe(prompt)
    c2 = PaymentObservationConsumer(ledger_book=lb2)
    c2.observe(late)

    as_of = dt.date(2026, 4, 1)
    assert (c1.snapshot("ACC-Z", as_of).balance_summary["balance_gbp"]
            == c2.snapshot("ACC-Z", as_of).balance_summary["balance_gbp"])


def test_missing_payment_degrades_gracefully_never_assumed_paid():
    """No WallResponse ever arrives for a billed invoice -- this must NOT
    crash, and must NOT be read as paid. The ageing engine (fed only by
    postable facts) correctly ages it as outstanding; note the belief gap
    this leaves: `arrears_risk_belief` stays NORMAL because no DD failure
    was ever OBSERVED for it either (there simply is no bounce report) --
    the consumer has no signal to explain WHY, and must not fabricate one."""
    lb = LedgerBook()
    _bill(lb, "ACC-MISS", "INV-MISS", 65.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    # deliberately: no observe() call at all for this account

    snap = consumer.snapshot("ACC-MISS", as_of=dt.date(2026, 6, 1), payment_terms_days=14)
    assert snap.balance_summary["in_arrears"] is True
    assert snap.balance_summary["arrears_gbp"] == 65.0
    assert not snap.allocation.open_items[0].is_settled
    assert any(it.bucket == "90+" for it in snap.aged_items)
    # the honest gap: no observed reason -> no elevated risk belief, even
    # though the account genuinely is arrears-aged (a real, expected
    # divergence for H27 to measure, not a bug to "fix" here).
    assert snap.arrears_risk_belief == ArrearsRiskBelief.NORMAL
    assert "arrears" in snap.cash_position_note.lower()


def test_stream_processed_one_at_a_time_with_gaps_reaches_final_state():
    """Simulates events arriving one at a time with arbitrary gaps between
    calls (C-S1) -- interleaving `snapshot()` reads between `observe()`
    calls must never raise and must be monotonically consistent with more
    information arriving over time."""
    lb = LedgerBook()
    _bill(lb, "ACC-GAP", "INV-GAP", 200.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)

    snap0 = consumer.snapshot("ACC-GAP", as_of=dt.date(2026, 1, 5))
    assert snap0.balance_summary["arrears_gbp"] == 200.0

    consumer.observe(_remit_resp("ACC-GAP", 120.0, "INV-GAP", dt.date(2026, 1, 20), "corr-gap-1"))
    snap1 = consumer.snapshot("ACC-GAP", as_of=dt.date(2026, 1, 25))
    assert snap1.balance_summary["arrears_gbp"] == 80.0

    consumer.observe(_remit_resp("ACC-GAP", 80.0, "INV-GAP", dt.date(2026, 2, 1), "corr-gap-2"))
    snap2 = consumer.snapshot("ACC-GAP", as_of=dt.date(2026, 2, 5))
    assert snap2.balance_summary["balance_gbp"] == 0.0


# ---------------------------------------------------------------------------
# (d) belief tagging -- inference, not truth; allowed to be plausibly wrong
# ---------------------------------------------------------------------------

def test_arrears_risk_belief_is_a_distinctly_named_inference_type():
    """The belief type's own name/values must read as a guess, not a fact --
    a structural nudge against ever wiring ground truth into this enum."""
    for member in ArrearsRiskBelief:
        assert "belief" not in member.value  # values are plain english (normal/watch/...)
    assert ArrearsRiskBelief.__name__.endswith("Belief")
    assert MandateBeliefState.__name__.endswith("BeliefState")
    for member in MandateBeliefState:
        if member != MandateBeliefState.UNKNOWN:
            assert member.value.endswith("_believed")


def test_arrears_risk_belief_can_be_wrong_by_construction():
    """Two accounts with IDENTICAL true arrears (never observed here -- this
    module cannot see it) produce DIFFERENT arrears_risk_belief purely
    because one happened to generate an ARUDD bounce report and the other's
    non-payment was silent (e.g. a standing order simply never set up) --
    proof this belief tracks OBSERVATION, not underlying truth, and is
    therefore not suspiciously "always correct"."""
    lb = LedgerBook()
    _bill(lb, "ACC-A", "INV-A", 90.0, dt.date(2026, 1, 1))
    _bill(lb, "ACC-B", "INV-B", 90.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    consumer.observe(_arrudd_fail_resp(
        "ACC-A", "MREF-A", 90.0, BacsReasonCategory.INSUFFICIENT_FUNDS, dt.date(2026, 1, 20), "corr-a",
    ))
    # ACC-B: identical non-payment, but no observation at all reaches this consumer

    as_of = dt.date(2026, 4, 1)
    snap_a = consumer.snapshot("ACC-A", as_of=as_of)
    snap_b = consumer.snapshot("ACC-B", as_of=as_of)
    assert snap_a.balance_summary["arrears_gbp"] == snap_b.balance_summary["arrears_gbp"] == 90.0
    assert snap_a.arrears_risk_belief != snap_b.arrears_risk_belief
    assert snap_a.arrears_risk_belief == ArrearsRiskBelief.WATCH
    assert snap_b.arrears_risk_belief == ArrearsRiskBelief.NORMAL


# ---------------------------------------------------------------------------
# Expected-collection reconciliation detector (director ruling 2026-07-25 §2):
# detect missed PUSH payments (no rail event) from own bills vs own cash.
# ---------------------------------------------------------------------------

def test_reconciliation_detects_a_never_paid_invoice_of_any_channel():
    """The carve-out: an invoice billed, past due+grace, with NO cash observed
    is a detected expected-collection miss -- WITHOUT any failure event (the
    missed push payment a real supplier notices only by reconciliation)."""
    lb = LedgerBook()
    _bill(lb, "ACC-1", "INV-1", 120.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    # no observe() at all -- a push payment that simply never arrived
    misses = consumer.expected_collection_misses("ACC-1", as_of=dt.date(2026, 3, 1))
    assert len(misses) == 1
    m = misses[0]
    assert isinstance(m, ExpectedCollectionMiss)
    assert m.invoice_ref == "INV-1"
    assert m.billed_gbp == 120.0
    assert m.received_gbp == 0.0
    assert m.shortfall_gbp == 120.0
    assert m.days_latency > DEFAULT_RECONCILIATION_GRACE_DAYS


def test_reconciliation_silent_within_grace_window():
    """Detection LATENCY (ruling §1): the detector does not fire the instant a
    due date passes -- a bank credit can be in transit; it waits out the grace
    window, so the latency is registered, not compressed to zero."""
    lb = LedgerBook()
    issue = dt.date(2026, 1, 1)
    _bill(lb, "ACC-1", "INV-1", 120.0, issue)
    consumer = PaymentObservationConsumer(ledger_book=lb)
    due = issue + dt.timedelta(days=14)  # _bill uses 14-day terms
    # 2 days past due -> inside a 5-day grace -> not yet observable
    assert consumer.expected_collection_misses(
        "ACC-1", as_of=due + dt.timedelta(days=2), grace_days=5
    ) == []
    # 6 days past due -> observable
    assert len(consumer.expected_collection_misses(
        "ACC-1", as_of=due + dt.timedelta(days=6), grace_days=5
    )) == 1


def test_reconciliation_does_not_flag_a_paid_late_invoice():
    """Fail-open guard (ruling §2, R15): a payment that arrived LATE (cash by
    as_of) leaves outstanding == 0, so it is NOT a miss. Reading real cash is
    what stops the detector fail-opening to 'everyone overdue is a failure'."""
    lb = LedgerBook()
    _bill(lb, "ACC-1", "INV-1", 120.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    consumer.observe(_remit_resp("ACC-1", 120.0, "INV-1", dt.date(2026, 2, 10), "corr-1"))
    assert consumer.expected_collection_misses("ACC-1", as_of=dt.date(2026, 3, 1)) == []


def test_reconciliation_flags_partial_payment_shortfall():
    """A partial payment leaves a residual shortfall -- detected, with the
    received/shortfall split reported honestly (a real arrears signal)."""
    lb = LedgerBook()
    _bill(lb, "ACC-1", "INV-1", 120.0, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    consumer.observe(_remit_resp("ACC-1", 50.0, "INV-1", dt.date(2026, 2, 10), "corr-1"))
    misses = consumer.expected_collection_misses("ACC-1", as_of=dt.date(2026, 3, 1))
    assert len(misses) == 1
    assert misses[0].received_gbp == 50.0
    assert misses[0].shortfall_gbp == 70.0


def test_reconciliation_is_order_independent():
    """C-S1/C-S2: the detector is a pure function of the observed ledger set,
    not of observe() arrival order."""
    def build(order):
        lb = LedgerBook()
        _bill(lb, "ACC-1", "INV-1", 120.0, dt.date(2026, 1, 1))
        _bill(lb, "ACC-1", "INV-2", 120.0, dt.date(2026, 1, 20))
        c = PaymentObservationConsumer(ledger_book=lb)
        resps = [_remit_resp("ACC-1", 120.0, "INV-1", dt.date(2026, 2, 1), "c1")]
        for r in (resps if order else list(reversed(resps))):
            c.observe(r)
        return c.expected_collection_misses("ACC-1", as_of=dt.date(2026, 4, 1))
    a, b = build(True), build(False)
    assert [m.invoice_ref for m in a] == [m.invoice_ref for m in b] == ["INV-2"]


# ── THE SECOND BELT ON THE DECODE LEG (EP6 pass 27) ──────────────────────────────────────────
# THIS LEG IS WHERE THE BELT DOES THE MOST WORK, and the reason is structural rather than
# stylistic. `decode_observable_payload`'s permitted key set is `get_type_hints(t)` of the
# contract's own dataclasses: it WIDENS whenever they widen, so for the question "could a real
# supplier know this" it is an R15 TAUTOLOGY. The encode leg has a non-derived answer (the
# contract's independently-declared `OBSERVABLE_PAYLOAD_FIELDS`); until pass 27 this leg had
# none at all. That matters because of what this seam is for: at go-live the encoder belongs to
# a bank and this leg is the only side of the crossing the company still owns.

def _mutant_decode_type(field_name: str):
    return dataclasses.make_dataclass(
        "RemittanceAdvice",
        [("bank_reference", str), ("account_id", str), (field_name, str)],
        frozen=True,
    )


def _widen_decoder(monkeypatch, field_name: str) -> dict:
    """Perform the same-edit widening on the DECODE side and return a wire body that fits it."""
    from company.billing import payment_observation_consumer as poc

    cls = _mutant_decode_type(field_name)
    monkeypatch.setitem(poc._OBSERVABLE_PAYLOAD_TYPES, "RemittanceAdvice", cls)
    monkeypatch.setitem(
        poc._OBSERVABLE_PAYLOAD_HINTS,
        "RemittanceAdvice",
        {"bank_reference": str, "account_id": str, field_name: str},
    )
    return {
        "payload_type": "RemittanceAdvice",
        "fields": {"bank_reference": "R-1", "account_id": "ACC-1", field_name: "x"},
    }


def test_MUTATION_a_counterparty_shipping_the_TRUE_failure_reason_is_refused(monkeypatch):
    """THE DOCTRINE MUTATION for this leg. The wire body matches the declared hints EXACTLY, so
    every derived check here -- `absent`, `extra`, the per-field type decode -- is green. Only
    the denylist stands between this message and the company folding the world's answer key into
    its own arrears belief, which is the one thing the D5/H27 gap exists to measure."""
    from company.billing import payment_observation_consumer as poc

    raw = _widen_decoder(monkeypatch, "dd_failure_reason")
    # The derived check is genuinely satisfied: that is what makes the belt load-bearing here.
    assert set(raw["fields"]) == set(poc._OBSERVABLE_PAYLOAD_HINTS["RemittanceAdvice"])

    with pytest.raises(poc.WallProtocolError) as exc:
        poc.decode_observable_payload(raw)
    assert exc.value.reason == "CONTRACT_VIOLATION"
    assert "dd_failure_reason" in str(exc.value)


@pytest.mark.parametrize("field_name", ["ability", "willingness", "quadrant", "hardship_tier"])
def test_MUTATION_the_hidden_answer_key_is_refused_by_every_name_the_belt_cites(
    monkeypatch, field_name
):
    """The ability x willingness quadrant is the thing the can't-pay/won't-pay classifier is
    SCORED on inferring. Handed it directly, the company would be reading the answer key."""
    from company.billing import payment_observation_consumer as poc

    raw = _widen_decoder(monkeypatch, field_name)

    with pytest.raises(poc.WallProtocolError) as exc:
        poc.decode_observable_payload(raw)
    assert exc.value.reason == "CONTRACT_VIOLATION"


def test_NULL_CONTROL_an_INNOCENT_unknown_key_trips_the_OTHER_refusal(monkeypatch):
    """Without this, the tests above could not tell "the denylist fired" from "anything the
    decoder does not recognise is refused". An unknown key that is not a truth name must come
    back as UNKNOWN_FIELD, so the two refusals stay separately observable."""
    from company.billing import payment_observation_consumer as poc

    raw = {
        "payload_type": "RemittanceAdvice",
        "fields": {
            "bank_reference": "R-1", "account_id": "ACC-1", "amount_gbp": 10.0,
            "rail": "bacs_direct_debit", "value_date": "2024-05-01",
            "branch_sort_code": "20-00-00",
        },
    }
    with pytest.raises(poc.WallProtocolError) as exc:
        poc.decode_observable_payload(raw)
    assert exc.value.reason == "UNKNOWN_FIELD"


def test_a_clean_payload_still_decodes_so_the_belt_is_not_a_standing_red():
    """A control the real traffic cannot satisfy gets deleted."""
    from company.billing import payment_observation_consumer as poc

    decoded = poc.decode_observable_payload({
        "payload_type": "RemittanceAdvice",
        "fields": {
            "bank_reference": "R-1", "account_id": "ACC-1", "amount_gbp": 10.0,
            "rail": "bacs_direct_debit", "value_date": "2024-05-01",
        },
    })
    assert decoded.bank_reference == "R-1"
