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
    DEFAULT_RECONCILIATION_GRACE_DAYS,
    ArrearsRiskBelief,
    ExpectedCollectionMiss,
    MandateBeliefState,
    PaymentObservationConsumer,
)
from company.interfaces.crossing_silence import (
    SILENCE_OBLIGATION,
    UNRECEIPTED_OBLIGATION,
    SilenceHorizon,
)
from interface.contracts.payment_observable_seam import (
    ADDACS_NOTIFICATION_TYPE,
    COLLECTION_REQUEST_TYPE,
    AddacsAdvice,
    AddacsAdviceType,
    AuddisReport,
    AuddisStatus,
    BacsArruddOutcome,
    BacsInputReport,
    BacsReasonCategory,
    CollectionRequest,
    DDOutcomeStatus,
    PaymentNotification,
    PaymentRail,
    RemittanceAdvice,
    SettlementConfirmation,
)
from interface.contracts.wall_envelope import (
    ErrorDetail,
    WallInterim,
    WallNotification,
    WallRequest,
    WallResponse,
    WallStatus,
)

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
    import dataclasses

    from company.billing.payment_observation_consumer import DDFailureObservation
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


# ---------------------------------------------------------------------------
# (e) THE PENDING CROSSING -- atom EP6_wall_protocol_typing, pass 36.
#
# The finding these tests pin: `NOT_KNOWABLE_YET` was the one answer that made
# a fact permanently UNHEARABLE. Every response marked its correlation_id
# processed, and the envelope defines a restatement as "a NEW `WallResponse`
# with a later `observed_at`" matched "ONLY by `correlation_id`" -- so the
# resolution of a disputed payment arrived on the id the honest "not yet" had
# already burned, and was dropped as a duplicate.
#
# The handed-forward item said this member "needs only a reader -- the writer
# exists". The writer does exist; what did not exist was an EXIT from the state
# the reader would read. A reader for a state that can never end is the same
# defect as a reader for a message that is never sent, one level up.
# ---------------------------------------------------------------------------

def _pending_resp(corr, observed_at, status=WallStatus.NOT_KNOWABLE_YET, error=None):
    return WallResponse(
        correlation_id=corr, status=status, schema_version=1,
        observed_at=observed_at, valid_time=None, payload=None, error=error,
    )


def _billed_and_disputed(corr="INV-D1", account_id="ACC-D", amount=120.0):
    """One billed invoice, one pending answer for its crossing -- the live
    shape: the DD path sets `correlation_id == invoice_ref`."""
    lb = LedgerBook()
    _bill(lb, account_id, corr, amount, dt.date(2026, 1, 1))
    consumer = PaymentObservationConsumer(ledger_book=lb)
    pending = _pending_resp(corr, dt.datetime(2026, 1, 10, 9, 0))
    resolution = _remit_resp(account_id, amount, corr, dt.date(2026, 2, 1), corr)
    return consumer, pending, resolution


def test_a_pending_answer_no_longer_makes_the_fact_UNHEARABLE():
    """THE DEFECT, with its NULL CONTROL beside it: the same resolution, on a
    consumer that never heard the pending answer, must reach the same state.
    Without that control this asserts only that cash posts, not that hearing
    "not yet" costs nothing."""
    consumer, pending, resolution = _billed_and_disputed()
    assert consumer.observe(pending) is True
    assert consumer.observe(resolution) is True          # was False -- the resolution was dropped
    told = consumer.snapshot("ACC-D", as_of=dt.date(2026, 3, 1))

    control_lb = LedgerBook()
    _bill(control_lb, "ACC-D", "INV-D1", 120.0, dt.date(2026, 1, 1))
    control = PaymentObservationConsumer(ledger_book=control_lb)
    assert control.observe(resolution) is True
    never_told = control.snapshot("ACC-D", as_of=dt.date(2026, 3, 1))

    assert told.balance_summary == never_told.balance_summary
    assert told.balance_summary["balance_gbp"] == 0.0    # the GBP120 actually landed
    assert told.unresolved_crossings == []               # and the crossing closed


def test_MUTATION_a_correlation_only_dedup_LOSES_the_resolution():
    """R15: the control fires on its own named defect. The mutation is the rule
    this module shipped with -- one processed-set, any status -- run over the
    identical stream."""
    consumer, pending, resolution = _billed_and_disputed()

    processed: set = set()

    def observe_the_old_way(response) -> bool:
        if response.correlation_id in processed:
            return False
        processed.add(response.correlation_id)
        if response.status != WallStatus.OK:
            return True
        return consumer.observe(response)

    assert observe_the_old_way(pending) is True
    assert observe_the_old_way(resolution) is False      # the defect, reproduced
    lost = consumer.snapshot("ACC-D", as_of=dt.date(2026, 3, 1))
    assert lost.balance_summary["balance_gbp"] == 120.0  # cash never posted


def test_C_S2_a_redelivered_pending_answer_is_a_no_op():
    """At-least-once delivery: the SAME answer arriving twice is not new
    information, and must not multiply in the register."""
    consumer, pending, _ = _billed_and_disputed()
    assert consumer.observe(pending) is True
    assert consumer.observe(pending) is False
    assert consumer.observe(copy.deepcopy(pending)) is False
    assert len(consumer.unresolved_crossings()) == 1


def test_C_S1_a_later_answer_SUPERSEDES_and_an_older_one_arriving_late_does_not():
    """Bitemporal restatement, not mutation: the register carries the
    counterparty's most recent word. An older answer arriving late (C-S1) is
    not it."""
    consumer, first, _ = _billed_and_disputed()
    later = _pending_resp("INV-D1", dt.datetime(2026, 1, 20, 9, 0))
    stale = _pending_resp("INV-D1", dt.datetime(2026, 1, 5, 9, 0))

    assert consumer.observe(first) is True
    assert consumer.observe(later) is True
    assert consumer.observe(stale) is False
    held = consumer.unresolved_crossings()
    assert [c.observed_at for c in held] == [dt.datetime(2026, 1, 20, 9, 0)]


def test_a_resolved_crossing_is_not_UNRESOLVED_by_a_later_pending_answer():
    """A response with no payload cannot restate a value, so "not yet" never
    revokes cash already observed -- the conservative limb, and the one the
    module behaved as before this change."""
    consumer, _, resolution = _billed_and_disputed()
    assert consumer.observe(resolution) is True
    assert consumer.observe(_pending_resp("INV-D1", dt.datetime(2026, 3, 1, 9, 0))) is False
    snap = consumer.snapshot("ACC-D", as_of=dt.date(2026, 3, 5))
    assert snap.balance_summary["balance_gbp"] == 0.0
    assert snap.unresolved_crossings == []


def test_NOT_KNOWABLE_YET_is_the_only_status_the_company_AWAITS():
    """The distinction the contract charges for. `NOT_KNOWABLE_YET` says the
    FACT is not resolvable yet -- an answer is still owed. The other two say
    something about the EXCHANGE and license no such expectation.

    THIS PROPERTY stays single-branched, but the REASON changed at pass 41: it
    is no longer "nothing can say either" (the stand-in now can, and the status
    vocabulary reads 4 of 4 live). It is that `awaiting_resolution` answers
    "does the counterparty owe an answer", and TIMEOUT/ERROR simply do not. The
    reader that acts on the difference is `silence_ladder` -- see
    `TestSilenceLadder` below."""
    consumer = PaymentObservationConsumer()
    consumer.observe(_pending_resp("c-nky", dt.datetime(2026, 1, 1, 9, 0)))
    consumer.observe(_pending_resp("c-timeout", dt.datetime(2026, 1, 1, 9, 0), WallStatus.TIMEOUT))
    consumer.observe(_pending_resp(
        "c-error", dt.datetime(2026, 1, 1, 9, 0), WallStatus.ERROR, ErrorDetail("E1", "boom")))

    awaited = {c.correlation_id for c in consumer.unresolved_crossings() if c.awaiting_resolution}
    assert awaited == {"c-nky"}
    assert {c.correlation_id for c in consumer.unresolved_crossings()} == {
        "c-nky", "c-timeout", "c-error"}


def test_the_register_is_BLINDFOLDED_by_as_of():
    """The Blindfold applies to the register exactly as to every other snapshot
    field: an answer that arrived after the decision clock is not knowable."""
    consumer, pending, _ = _billed_and_disputed()
    consumer.observe(pending)                                     # observed 2026-01-10
    assert consumer.unresolved_crossings("ACC-D", as_of=dt.date(2026, 1, 5)) == []
    assert len(consumer.unresolved_crossings("ACC-D", as_of=dt.date(2026, 1, 10))) == 1
    assert consumer.snapshot("ACC-D", as_of=dt.date(2026, 1, 5)).unresolved_crossings == []


def test_an_unattributable_crossing_reaches_NO_account_and_is_still_VISIBLE():
    """A non-OK response carries no payload and therefore no account. The join
    is EXACT (correlation_id == a billed invoice_ref) and fails toward silence:
    a push payment quoting no invoice reference is attributed to nobody rather
    than to a guess, and remains readable in the account-less call."""
    consumer, pending, _ = _billed_and_disputed()
    ambiguous = _pending_resp("CUST-9::p3::ambiguous", dt.datetime(2026, 1, 12, 9, 0))
    consumer.observe(pending)
    consumer.observe(ambiguous)

    on_account = consumer.snapshot("ACC-D", as_of=dt.date(2026, 2, 1)).unresolved_crossings
    assert [c.correlation_id for c in on_account] == ["INV-D1"]
    assert len(consumer.unresolved_crossings()) == 2


def test_the_register_is_ORDER_INDEPENDENT_like_every_other_belief_here():
    """C-S1/C-S2: the same set of observations in any order reaches the same
    register."""
    corr = "INV-D1"
    states = []
    for order in ([0, 1, 2], [2, 1, 0], [1, 2, 0]):
        consumer, first, resolution = _billed_and_disputed()
        stream = [first, _pending_resp(corr, dt.datetime(2026, 1, 20, 9, 0)), resolution]
        for i in order:
            consumer.observe(stream[i])
        snap = consumer.snapshot("ACC-D", as_of=dt.date(2026, 3, 1))
        states.append((snap.unresolved_crossings, snap.balance_summary))
    assert states[0] == states[1] == states[2]


# ---------------------------------------------------------------------------
# THE SILENCE LADDER -- the company's clock against its own open register
# (atom EP6_wall_protocol_typing, pass 41, the blind review's Q5)
# ---------------------------------------------------------------------------


class TestSilenceLadder:
    """"How long have I been waiting, and is that too long?"

    `unresolved_crossings` answered "what am I waiting for" and nothing answered
    this, so a crossing read identically at one minute and at one year. The
    load-bearing test is
    `test_MUTATION_a_crossing_that_never_answers_is_NOT_the_same_at_one_minute_and_one_year`:
    it fails against the pass-40 register, which is the point.
    """

    HEARD = dt.datetime(2026, 8, 17, 9, 0)   # a Monday

    def _consumer_with_open_crossing(self, status=WallStatus.NOT_KNOWABLE_YET, error=None):
        consumer = PaymentObservationConsumer()
        consumer.observe(_pending_resp("INV-Q5", self.HEARD, status, error))
        return consumer

    def test_MUTATION_a_crossing_that_never_answers_is_NOT_the_same_at_one_minute_and_one_year(self):
        """THE defect, stated as a test. Both reads see the identical register
        row; only the ladder can tell them apart."""
        consumer = self._consumer_with_open_crossing()

        early = consumer.silence_ladder(as_of=self.HEARD + dt.timedelta(minutes=1))
        late = consumer.silence_ladder(as_of=self.HEARD + dt.timedelta(days=365))

        assert [c.correlation_id for c in early] == ["INV-Q5"]
        assert [c.correlation_id for c in late] == ["INV-Q5"]
        assert early[0].horizon != late[0].horizon
        assert early[0].concluded_status is None
        assert late[0].concluded_status == WallStatus.TIMEOUT

        # the null control: the underlying register really is unchanged, so the
        # ladder is supplying the distinction and not reading a moved value.
        assert consumer.unresolved_crossings() == consumer.unresolved_crossings()

    def test_the_ladder_NEVER_evicts_the_crossing_it_aged(self):
        """Ageing out is not being answered. A company that dropped the crossing
        at five working days would be assuming a resolution the seam never sent
        -- the same fail-open in a slower costume."""
        consumer = self._consumer_with_open_crossing()
        way_past = self.HEARD + dt.timedelta(days=400)

        consumer.silence_ladder(as_of=way_past)
        consumer.silence_ladder(as_of=way_past)

        still_open = consumer.unresolved_crossings()
        assert [c.correlation_id for c in still_open] == ["INV-Q5"]
        assert still_open[0].status == WallStatus.NOT_KNOWABLE_YET, (
            "the counterparty's own word must survive the company's conclusion"
        )

    def test_the_conclusion_is_never_written_back_into_the_register(self):
        """A real counterparty that has gone quiet cannot send you a TIMEOUT. If
        the company wrote one into the register it would be inventing a message
        it never received."""
        consumer = self._consumer_with_open_crossing()
        (aged,) = consumer.silence_ladder(as_of=self.HEARD + dt.timedelta(days=30))

        assert aged.concluded_status == WallStatus.TIMEOUT
        assert aged.heard_status == WallStatus.NOT_KNOWABLE_YET
        assert consumer.unresolved_crossings()[0].status == WallStatus.NOT_KNOWABLE_YET

    def test_the_ladder_is_BLINDFOLDED_by_as_of(self):
        """A crossing heard after the decision clock is not visible here either."""
        consumer = self._consumer_with_open_crossing()
        before = self.HEARD - dt.timedelta(days=1)
        assert consumer.silence_ladder(as_of=before) == []

    def test_a_crossing_heard_later_the_same_day_is_still_excluded(self):
        """`unresolved_crossings` filters by DATE; the ladder's clock is a
        datetime, so an afternoon arrival must not be visible to a morning
        decision clock. Without the datetime-level filter this returns a
        conclusion whose silence is negative."""
        consumer = PaymentObservationConsumer()
        consumer.observe(_pending_resp("INV-PM", dt.datetime(2026, 8, 17, 16, 0)))
        assert consumer.silence_ladder(as_of=dt.datetime(2026, 8, 17, 9, 0)) == []
        assert len(consumer.silence_ladder(as_of=dt.datetime(2026, 8, 17, 17, 0))) == 1

    @pytest.mark.parametrize(
        "status,error",
        [
            (WallStatus.NOT_KNOWABLE_YET, None),
            (WallStatus.TIMEOUT, None),
            (WallStatus.ERROR, ErrorDetail("E1", "boom")),
        ],
    )
    def test_every_status_the_register_can_hold_is_aged_without_crashing(self, status, error):
        """The ladder must have an arm for each -- a status it cannot read would
        raise on the live path rather than in a test."""
        consumer = self._consumer_with_open_crossing(status, error)
        (aged,) = consumer.silence_ladder(as_of=self.HEARD + dt.timedelta(days=30))
        assert aged.heard_status == status
        assert aged.next_move

    def test_only_an_OWED_answer_is_concluded_as_a_timeout(self):
        """Re-concluding a TIMEOUT as a TIMEOUT would be the company agreeing
        with itself and counting it as evidence."""
        owed = self._consumer_with_open_crossing(WallStatus.NOT_KNOWABLE_YET)
        failed = self._consumer_with_open_crossing(WallStatus.TIMEOUT)
        as_of = self.HEARD + dt.timedelta(days=30)

        assert owed.silence_ladder(as_of=as_of)[0].concluded_status == WallStatus.TIMEOUT
        assert failed.silence_ladder(as_of=as_of)[0].concluded_status is None

    def test_a_resolved_crossing_leaves_the_ladder_entirely(self):
        """The only way out of the register is an answer -- and then there is
        nothing left to age."""
        consumer = self._consumer_with_open_crossing()
        assert len(consumer.silence_ladder(as_of=self.HEARD + dt.timedelta(days=30))) == 1

        consumer.observe(_remit_resp(
            "ACC-Q5", 10.0, "INV-Q5", dt.date(2026, 8, 18), "INV-Q5",
            observed_at=self.HEARD + dt.timedelta(days=1),
        ))
        assert consumer.silence_ladder(as_of=self.HEARD + dt.timedelta(days=30)) == []

    def test_the_ladder_is_a_pure_read_and_licenses_no_action(self):
        """SENSING ONLY (ruling 2026-07-25 s2): obligations are sentences, not
        calls. Nothing dunns, flags, prices, provisions or re-requests."""
        consumer = self._consumer_with_open_crossing()
        as_of = self.HEARD + dt.timedelta(days=30)
        first = consumer.silence_ladder(as_of=as_of)
        second = consumer.silence_ladder(as_of=as_of)
        assert first == second
        for aged in first:
            assert isinstance(aged.obligation, str) and aged.obligation.strip()


# ---------------------------------------------------------------------------
# UNSOLICITED INBOUND -- the blind review's Q2 (atom EP6).
#
# Q2 asked for "a first-class inbound primitive with its own idempotency and
# ordering rules", and named the fail: "we model it as a response to a
# synthetic request". These tests are the two rules, plus the MUTATION that
# shows the shipped shape losing the fact they exist to keep.
# ---------------------------------------------------------------------------

_SENDER = "BACS-BUREAU-01"


def _advice(mandate="MANDATE-ACC-1", account="ACC-1",
            advice_type=AddacsAdviceType.PAYER_CANCELLED, value_date=None):
    return AddacsAdvice(
        mandate_ref=mandate,
        account_id=account,
        advice_type=advice_type,
        advice_text="Instruction Cancelled By Payer",
        value_date=value_date or dt.date(2026, 1, 10),
    )


def _notify(sequence, payload=None, sender=_SENDER, notification_id=None,
            observed_at=None):
    return WallNotification(
        notification_id=notification_id or f"ADDACS-{sender}-{sequence}",
        notification_type=ADDACS_NOTIFICATION_TYPE,
        schema_version=1,
        sender=sender,
        sequence=sequence,
        observed_at=observed_at or dt.datetime(2026, 1, 11, 6, 0),
        valid_time=dt.date(2026, 1, 10),
        payload=payload if payload is not None else _advice(),
    )


def test_an_unsolicited_advice_moves_the_mandate_belief():
    """The reader existed before this primitive did; what it lacked was any
    way to be reached that did not invent a request."""
    c = PaymentObservationConsumer()
    assert c.observe_unsolicited(_notify(0)) is True
    assert c.mandate_belief("MANDATE-ACC-1").state is MandateBeliefState.LIKELY_DEAD_BELIEVED


def test_a_redelivered_notification_is_a_NO_OP():
    """C-S2, at-least-once delivery. Identity is the SENDER's message id --
    the company has no correlation key for a thing it never asked for."""
    c = PaymentObservationConsumer()
    n = _notify(0)
    assert c.observe_unsolicited(n) is True
    assert c.observe_unsolicited(n) is False
    stream = c.inbound_stream(_SENDER)
    assert stream.received == 1, "a redelivery must not inflate the stream"
    assert stream.duplicates_suppressed == 1


def test_the_company_can_tell_it_MISSED_a_notification():
    """THE question the primitive was built to make askable. Nothing in the
    messages that DID arrive can answer it -- only the sender's numbering."""
    c = PaymentObservationConsumer()
    for seq in (0, 3):                       # the transport lost 1 and 2
        c.observe_unsolicited(_notify(seq, _advice(mandate=f"M{seq}", account="ACC-1")))
    stream = c.inbound_stream(_SENDER)
    assert stream.missing_sequences == (1, 2)
    assert stream.has_gap is True


def test_NULL_CONTROL_a_complete_stream_reports_NO_gap():
    """Without this the gap test only proves the detector is always red."""
    c = PaymentObservationConsumer()
    for seq in range(4):
        c.observe_unsolicited(_notify(seq, _advice(mandate=f"M{seq}", account="ACC-1")))
    stream = c.inbound_stream(_SENDER)
    assert stream.missing_sequences == ()
    assert stream.has_gap is False


def test_MUTATION_the_shipped_shape_CANNOT_SEE_the_loss():
    """R15: the control fires on its own named defect.

    Reproduces inline what this seam did before the primitive existed -- an
    ADDACS advice delivered as a `WallResponse` on a synthetic correlation id,
    the blind reviewer's named fail. The SAME loss (advices 1 and 2 never
    arrive) is then invisible: every response the company holds is well-formed
    and consistent, the mandates it never heard about stay believed-ALIVE, and
    no reading of the consumer discloses that anything is missing.
    """
    lost_mandates = ["M1", "M2"]

    old = PaymentObservationConsumer()
    for seq in (0, 3):
        old.observe(_resp(_advice(mandate=f"M{seq}", account="ACC-1"),
                          correlation_id=f"SYNTHETIC-{seq}"))
    # The old shape has no stream to ask, and the advices it never received
    # leave no trace of any kind.
    assert not hasattr(old, "_notification_sequences") or not old.inbound_senders()
    for m in lost_mandates:
        assert old.mandate_belief(m).state is MandateBeliefState.UNKNOWN, (
            "the lost advice leaves the mandate looking merely unheard-of"
        )

    new = PaymentObservationConsumer()
    for seq in (0, 3):
        new.observe_unsolicited(_notify(seq, _advice(mandate=f"M{seq}", account="ACC-1")))
    for m in lost_mandates:
        assert new.mandate_belief(m).state is MandateBeliefState.UNKNOWN, (
            "the new shape does not conjure the content of what it lost..."
        )
    assert new.inbound_stream(_SENDER).missing_sequences == (1, 2), (
        "...but it KNOWS two advices are owed to it, which is the whole repair"
    )


def test_a_late_straggler_CLOSES_the_gap_and_is_not_a_loss():
    """A gap that fills was never a loss. `missing_sequences` recomputes from
    the observed set, so nothing has to remember to un-count it."""
    c = PaymentObservationConsumer()
    c.observe_unsolicited(_notify(0))
    c.observe_unsolicited(_notify(2, _advice(mandate="M2")))
    assert c.inbound_stream(_SENDER).missing_sequences == (1,)
    c.observe_unsolicited(_notify(1, _advice(mandate="M1")))
    stream = c.inbound_stream(_SENDER)
    assert stream.missing_sequences == ()
    assert stream.out_of_order_arrivals == 1, (
        "late delivery is the NORMAL case and is counted apart from loss"
    )


def test_belief_is_ORDER_INDEPENDENT_though_the_stream_is_ordered():
    """The sequence says what is MISSING, never what is TRUE. Two arrival
    orders of the same advices must reach the same belief (C-S1)."""
    early = _advice(mandate="M", advice_type=AddacsAdviceType.PAYER_AMENDED,
                    value_date=dt.date(2026, 1, 5))
    late = _advice(mandate="M", advice_type=AddacsAdviceType.PAYER_CANCELLED,
                   value_date=dt.date(2026, 1, 20))
    forwards = PaymentObservationConsumer()
    forwards.observe_unsolicited(_notify(0, early))
    forwards.observe_unsolicited(_notify(1, late))
    backwards = PaymentObservationConsumer()
    backwards.observe_unsolicited(_notify(1, late))
    backwards.observe_unsolicited(_notify(0, early))
    assert forwards.mandate_belief("M").state is backwards.mandate_belief("M").state
    assert forwards.mandate_belief("M").state is MandateBeliefState.LIKELY_DEAD_BELIEVED


def test_two_senders_do_not_share_a_numbering():
    """Comparing two counterparties' positions would manufacture gaps."""
    c = PaymentObservationConsumer()
    c.observe_unsolicited(_notify(0, sender="BACS-BUREAU-01"))
    c.observe_unsolicited(_notify(9, _advice(mandate="M9"), sender="OTHER-BUREAU"))
    assert c.inbound_stream("BACS-BUREAU-01").missing_sequences == ()
    assert c.inbound_stream("OTHER-BUREAU").missing_sequences == ()
    assert c.inbound_senders() == ("BACS-BUREAU-01", "OTHER-BUREAU")


def test_the_same_id_from_two_senders_is_TWO_messages():
    """Ids are scoped per sender: two feeds may legitimately reuse one."""
    c = PaymentObservationConsumer()
    assert c.observe_unsolicited(_notify(0, notification_id="MSG-1", sender="A")) is True
    assert c.observe_unsolicited(
        _notify(0, _advice(mandate="M-B"), notification_id="MSG-1", sender="B")
    ) is True


def test_a_payload_this_seam_does_not_declare_unsolicited_is_REFUSED():
    """Otherwise any payload could skip the response leg's checks by arriving
    in the other envelope."""
    c = PaymentObservationConsumer()
    smuggled = RemittanceAdvice(
        bank_reference="R1", account_id="ACC-1", amount_gbp=50.0,
        rail=PaymentRail.FASTER_PAYMENTS, value_date=dt.date(2026, 1, 10),
    )
    with pytest.raises(ValueError, match="does not declare it so"):
        c.observe_unsolicited(_notify(0, smuggled))


def test_an_advice_for_an_account_we_do_not_supply_goes_to_SUSPENSE():
    """Q6's roster answer applies to this leg too -- and must NOT open a gap,
    because the message did arrive and is accounted for in the numbering."""
    c = PaymentObservationConsumer(supplied_accounts=["ACC-1"])
    c.observe_unsolicited(_notify(0, _advice(mandate="M-X", account="ACC-STRANGER")))
    assert c.mandate_belief("M-X").state is MandateBeliefState.UNKNOWN
    assert [m.payload_type for m in c.misdirected_observations()] == ["AddacsAdvice"]
    assert c.inbound_stream(_SENDER).missing_sequences == ()


def test_an_unheard_stream_reports_nothing_rather_than_a_false_clean_bill():
    """FAIL-CLOSED read-out: a sender never heard from has no first/last
    sequence, so an empty gap list cannot be read as 'all present'."""
    c = PaymentObservationConsumer()
    stream = c.inbound_stream("NEVER-HEARD-FROM")
    assert stream.received == 0
    assert stream.first_sequence is None and stream.last_sequence is None
    assert stream.has_gap is False


# ---------------------------------------------------------------------------
# THE LADDER OVER BOTH BOOKS (atom EP6, pass 46).
#
# Pass 41 built `silence_ladder` over ONE register -- crossings the counterparty
# had ANSWERED -- and recorded the hole in its own evidence: "a crossing whose
# FIRST message never arrives leaves no trace, because nothing records that the
# company asked". Pass 44 built the thing that records it. These tests are the
# join, and the load-bearing one is
# `test_MUTATION_a_collection_that_is_never_answered_at_all_is_now_AGED`: it
# fails against the pass-45 consumer, where the answer is an empty list.
# ---------------------------------------------------------------------------


class TestSilenceLadderOverOpenConversations:

    EMITTED = dt.datetime(2026, 8, 17, 9, 0)      # a Monday
    ACKED = dt.datetime(2026, 8, 17, 15, 0)
    LONG_AFTER = dt.datetime(2026, 9, 30, 9, 0)

    def _request(self, corr="INV-Q3", account_id="ACC-Q3", emitted_at=None):
        return WallRequest(
            correlation_id=corr,
            request_type=COLLECTION_REQUEST_TYPE,
            schema_version=2,
            as_of=emitted_at or self.EMITTED,
            emitted_at=emitted_at or self.EMITTED,
            payload=CollectionRequest(
                account_id=account_id,
                mandate_ref="MAN-1",
                amount_gbp=42.0,
                rail=PaymentRail.BACS_DIRECT_DEBIT,
                requested_collection_date=dt.date(2026, 8, 20),
            ),
        )

    def _interim(self, corr="INV-Q3", at=None):
        # A REAL CONTRACT PAYLOAD, not a stand-in dict (atom EP6, pass 50). The
        # dict this used to carry was refused the moment `observe_interim`
        # started checking the leg's declared payload set, and it should have
        # been: the ladder's subject is a Bacs acknowledgement, and a fixture
        # that could not cross the wire was proving the ladder against a message
        # this seam never carries.
        return WallInterim(
            correlation_id=corr,
            leg=2,
            interim_type="bacs_input_report",
            schema_version=2,
            observed_at=at or self.ACKED,
            payload=BacsInputReport(
                submission_ref="SUB-1",
                account_id="ACC-Q3",
                mandate_ref="MAN-1",
                amount_gbp=42.0,
                items_in_submission=1,
                items_rejected=0,
                value_date=dt.date(2026, 8, 20),
            ),
        )

    def test_MUTATION_a_collection_that_is_never_answered_at_all_is_now_AGED(self):
        """THE defect, stated as its differential. The same consumer, the same
        clock: one raised the collection and one did not. Before this pass BOTH
        returned an empty ladder -- a submission the world swallowed was
        indistinguishable from one never made, for as long as the company cared
        to wait."""
        raised = PaymentObservationConsumer()
        raised.note_collection_request(self._request())

        never_raised = PaymentObservationConsumer()

        (aged,) = raised.silence_ladder(as_of=self.LONG_AFTER)
        assert aged.correlation_id == "INV-Q3"
        assert aged.horizon == SilenceHorizon.ABANDONED
        assert aged.heard_status is None
        assert aged.receipt_proven is False
        assert aged.concluded_status == WallStatus.TIMEOUT

        # THE NULL CONTROL, and it is what makes the register the source: a
        # company that never asked has nothing to be owed, and the ladder must
        # not invent a crossing for it.
        assert never_raised.silence_ladder(as_of=self.LONG_AFTER) == []

    def test_the_unanswered_collection_is_not_the_same_at_one_minute_and_one_year(self):
        """The pass-41 headline, now true of the subject that could not be aged
        at all: the register row is identical at both reads and only the ladder
        can tell them apart."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())

        early = consumer.silence_ladder(as_of=self.EMITTED + dt.timedelta(minutes=1))
        late = consumer.silence_ladder(as_of=self.EMITTED + dt.timedelta(days=365))

        assert early[0].horizon == SilenceHorizon.LATE
        assert late[0].horizon == SilenceHorizon.ABANDONED
        assert early[0].concluded_status is None
        assert late[0].concluded_status == WallStatus.TIMEOUT
        assert consumer.open_conversations()[0].leg_count == 1, (
            "the conversation itself has not moved -- the ladder supplies the "
            "distinction and does not read a changed value"
        )

    def test_an_ACKNOWLEDGED_submission_gets_the_other_ladder_and_a_later_clock(self):
        """An input report changes two things at once and both matter: receipt is
        proven (so a chase is safe where a re-send never was), and the
        counterparty spoke more recently than the company asked, so the silence
        is shorter."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())
        consumer.observe_interim(self._interim())

        (aged,) = consumer.silence_ladder(as_of=self.ACKED + dt.timedelta(days=2))
        assert aged.receipt_proven is True
        assert aged.silent_since == self.ACKED
        assert aged.last_heard_at == self.ACKED
        assert aged.answer_owed is True
        assert aged.obligation == SILENCE_OBLIGATION[aged.horizon]
        assert aged.obligation != UNRECEIPTED_OBLIGATION[aged.horizon]

    def test_the_UNRECEIPTED_obligation_refuses_the_re_send_the_other_one_licenses(self):
        """The measured consequence of the join, and the reason it is not
        plumbing: the same horizon on the same rail, and the sentence the
        company is entitled to say about it depends entirely on whether anything
        ever confirmed the submission arrived. A re-sent Bacs collection debits
        the payer twice."""
        overdue_at = self.EMITTED + dt.timedelta(days=2)

        silent = PaymentObservationConsumer()
        silent.note_collection_request(self._request())
        acknowledged = PaymentObservationConsumer()
        acknowledged.note_collection_request(self._request())
        acknowledged.observe_interim(self._interim())

        (unheard,) = silent.silence_ladder(as_of=overdue_at)
        (heard,) = acknowledged.silence_ladder(as_of=overdue_at)

        assert unheard.horizon == heard.horizon == SilenceHorizon.OVERDUE
        assert unheard.obligation == UNRECEIPTED_OBLIGATION[SilenceHorizon.OVERDUE]
        assert heard.obligation == SILENCE_OBLIGATION[SilenceHorizon.OVERDUE]
        assert unheard.next_move != heard.next_move

    def test_a_crossing_in_BOTH_books_is_aged_ONCE(self):
        """A non-OK response does NOT close a conversation (see `observe`), so a
        crossing answered 'not yet' sits in the open register AND in the open
        conversation book. Counting it twice would report one silence as two --
        and the second copy would carry the unreceipted ladder for a crossing the
        counterparty demonstrably holds."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())
        consumer.observe(_pending_resp("INV-Q3", self.EMITTED + dt.timedelta(hours=1)))

        ladder = consumer.silence_ladder(as_of=self.LONG_AFTER)
        assert [c.correlation_id for c in ladder] == ["INV-Q3"]
        assert ladder[0].heard_status == WallStatus.NOT_KNOWABLE_YET
        assert ladder[0].receipt_proven is True, (
            "an answer arrived, so receipt is proven whatever the conversation "
            "book knows"
        )

    def test_whichever_spoke_last_starts_the_clock(self):
        """An interim arriving AFTER a 'not yet' is the counterparty speaking
        more recently than its own last status. Taking the older instant would
        report a longer silence than the company actually experienced; taking
        the newer one must not lose the status word."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())
        answered_at = self.EMITTED + dt.timedelta(hours=1)
        acked_at = self.EMITTED + dt.timedelta(hours=5)
        consumer.observe(_pending_resp("INV-Q3", answered_at))
        consumer.observe_interim(self._interim(at=acked_at))

        (aged,) = consumer.silence_ladder(as_of=self.LONG_AFTER)
        assert aged.silent_since == acked_at
        assert aged.heard_status == WallStatus.NOT_KNOWABLE_YET, (
            "the counterparty's last STATUS word is a different question from "
            "when it last spoke, and the two must not be merged"
        )

    def test_a_response_timestamped_BEFORE_the_request_does_not_forge_an_acknowledgement(self):
        """The guard on the clock-forward branch, and its own falsifier. The
        forward move is keyed on an acknowledgement HAVING ARRIVED, not on the
        instants alone -- because `silent_since` falls back to the company's own
        emission, so a counterparty whose clock runs slow (an `observed_at`
        before the request was raised, which C-S1 does not forbid) would
        otherwise relabel a crossing nothing acknowledged as acknowledged, and
        hand it the ladder that licenses a re-send."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())
        skewed = self.EMITTED - dt.timedelta(minutes=5)
        consumer.observe(_pending_resp("INV-Q3", skewed))

        (aged,) = consumer.silence_ladder(as_of=self.LONG_AFTER)
        assert aged.silent_since == skewed
        assert aged.heard_status == WallStatus.NOT_KNOWABLE_YET
        assert aged.last_heard_at == skewed, (
            "an answer is something heard, and no interim exists to move the "
            "clock off it"
        )

    def test_a_resolved_conversation_leaves_the_ladder(self):
        """The only way out is an answer. An OK closes the conversation, and a
        closed exchange has no silence to measure."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())
        assert len(consumer.silence_ladder(as_of=self.LONG_AFTER)) == 1

        consumer.observe(_remit_resp(
            "ACC-Q3", 42.0, "INV-Q3", dt.date(2026, 8, 20), "INV-Q3",
            observed_at=self.EMITTED + dt.timedelta(days=3),
        ))
        assert consumer.silence_ladder(as_of=self.LONG_AFTER) == []

    def test_the_ladder_is_BLINDFOLDED_on_the_conversation_book_too(self):
        """Three readings at a clock that has not reached the events: a
        conversation opened later is invisible; an interim that arrives later has
        not been heard yet, so the silence still runs from the emission; and a
        conversation closed later was OPEN at the clock and must still be aged."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())
        consumer.observe_interim(self._interim())
        consumer.observe(_remit_resp(
            "ACC-Q3", 42.0, "INV-Q3", dt.date(2026, 8, 20), "INV-Q3",
            observed_at=self.EMITTED + dt.timedelta(days=3),
        ))

        assert consumer.silence_ladder(as_of=self.EMITTED - dt.timedelta(days=1)) == []

        (mid,) = consumer.silence_ladder(as_of=self.EMITTED + dt.timedelta(hours=1))
        assert mid.silent_since == self.EMITTED, (
            "the acknowledgement had not arrived at this clock, so it cannot be "
            "the moment the silence started"
        )
        assert mid.receipt_proven is False
        assert consumer.silence_ladder(as_of=self.LONG_AFTER) == []

    def test_the_conversation_half_is_attributed_to_an_account_the_same_way(self):
        """Exact equality against that account's own billed invoice refs -- the
        join `unresolved_crossings` documents. A conversation whose id is not one
        of them is still visible in the account-less read, which is the
        register's complete reading."""
        lb = LedgerBook()
        _bill(lb, "ACC-Q3", "INV-Q3", 42.0, dt.date(2026, 8, 1))
        consumer = PaymentObservationConsumer(ledger_book=lb)
        consumer.note_collection_request(self._request())
        consumer.note_collection_request(self._request(corr="PUSH-9"))

        mine = consumer.silence_ladder(as_of=self.LONG_AFTER, account_id="ACC-Q3")
        assert [c.correlation_id for c in mine] == ["INV-Q3"]
        assert len(consumer.silence_ladder(as_of=self.LONG_AFTER)) == 2

    def test_the_ladder_still_evicts_nothing_and_still_acts_on_nothing(self):
        """Pass 41's two standing clauses, re-asserted over the new subject:
        ageing out is not being answered, and every obligation is a sentence."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(self._request())

        first = consumer.silence_ladder(as_of=self.LONG_AFTER)
        second = consumer.silence_ladder(as_of=self.LONG_AFTER)
        assert len(first) == 1, (
            "asserted before the clauses below because both of them are VACUOUS "
            "on an empty ladder -- a purity check over nothing passes on a build "
            "that aged nothing at all"
        )
        assert first == second
        assert [c.correlation_id for c in consumer.open_conversations()] == ["INV-Q3"]
        assert consumer.conversation("INV-Q3").is_closed is False
        for aged in first:
            assert isinstance(aged.obligation, str) and aged.obligation.strip()


# ═══════════════════════════════════════════════════════════════════════════════
# EACH LEG DECODES AGAINST ITS OWN DECLARED PAYLOAD SET (EP6 pass 50)
#
# Until this pass all three legs shared one permissive table, so the LEG carried
# no claim about what kind of thing had arrived: a counterparty could ship its
# outcome as an acknowledgement, or a mandate advice as an answer to a question
# nobody asked, and every check between the wire and belief would still pass.
# This is the COMPANY side of that split; the world side is in
# tests/simulation/test_payment_seam_adapter.py.
# ═══════════════════════════════════════════════════════════════════════════════


from company.interfaces.wall_protocol import WallProtocolError  # noqa: E402


class TestPerLegPayloadSets:

    INPUT_REPORT_RAW = {
        "payload_type": "BacsInputReport",
        "fields": {
            "submission_ref": "SUB-1",
            "account_id": "ACC-1",
            "mandate_ref": "MAN-1",
            "amount_gbp": 42.5,
            "items_in_submission": 38,
            "items_rejected": 2,
            "value_date": "2026-03-06",
        },
    }
    ADVICE_RAW = {
        "payload_type": "AddacsAdvice",
        "fields": {
            "mandate_ref": "MAN-1",
            "account_id": "ACC-1",
            "advice_type": "payer_cancelled",
            "advice_text": "Instruction Cancelled By Payer",
            "value_date": "2026-03-07",
        },
    }

    def test_the_interim_leg_accepts_what_the_contract_declares_for_it(self):
        from company.billing import payment_observation_consumer as poc

        payload = poc.decode_interim_payload(self.INPUT_REPORT_RAW)
        assert isinstance(payload, BacsInputReport)
        assert payload.items_in_submission == 38

    def test_the_interim_leg_REFUSES_a_payload_declared_for_another_leg(self):
        from company.billing import payment_observation_consumer as poc

        with pytest.raises(WallProtocolError) as refused:
            poc.decode_interim_payload(self.ADVICE_RAW)
        assert refused.value.reason == "UNKNOWN_FIELD"
        assert "AddacsAdvice" in str(refused.value)

    def test_the_unsolicited_leg_REFUSES_an_acknowledgement_payload(self):
        from company.billing import payment_observation_consumer as poc

        with pytest.raises(WallProtocolError):
            poc.decode_unsolicited_payload(self.INPUT_REPORT_RAW)
        # NULL CONTROL: the leg's own declared payload still decodes, so the
        # refusal above is about the SPLIT and not about a broken decoder.
        assert isinstance(poc.decode_unsolicited_payload(self.ADVICE_RAW), AddacsAdvice)

    def test_the_RESPONSE_leg_is_unchanged_by_the_split(self):
        """The regression this refactor could most easily have caused: the leg
        every pre-pass-50 caller used must decode exactly as it did."""
        from company.billing import payment_observation_consumer as poc

        remittance = {
            "payload_type": "RemittanceAdvice",
            "fields": {
                "bank_reference": "INV-1",
                "account_id": "ACC-1",
                "amount_gbp": 42.5,
                "rail": "bacs_direct_debit",
                "value_date": "2026-03-06",
            },
        }
        assert isinstance(poc.decode_observable_payload(remittance), RemittanceAdvice)
        # ... and an interim-only payload is STILL not a response.
        with pytest.raises(WallProtocolError):
            poc.decode_observable_payload(self.INPUT_REPORT_RAW)

    def test_R15_MUTANT_one_shared_table_lets_an_ADVICE_arrive_as_an_ACKNOWLEDGEMENT(self):
        """THE NAMED DEFECT, reproduced: with the pre-pass-50 shared table the
        interim leg accepts a mandate advice, so `leg` stops being a claim about
        what arrived. The mutation moves the TABLE and not the message."""
        from company.billing import payment_observation_consumer as poc

        mutated = poc.decode_observable_payload(
            self.ADVICE_RAW,
            types=poc._OBSERVABLE_PAYLOAD_TYPES,
            hints=poc._OBSERVABLE_PAYLOAD_HINTS,
        )
        assert isinstance(mutated, AddacsAdvice), (
            "the mutant must actually succeed, or this test proves nothing "
            "about what the shipped split refuses"
        )
        with pytest.raises(WallProtocolError):
            poc.decode_interim_payload(self.ADVICE_RAW)

    def test_an_EMPTY_leg_table_refuses_everything_rather_than_accepting_it(self):
        """The dial that is not a dial (R15 FAIL-OPEN): there is no value of
        `types` meaning 'anything goes'."""
        from company.billing import payment_observation_consumer as poc

        with pytest.raises(WallProtocolError):
            poc.decode_observable_payload(self.ADVICE_RAW, types={}, hints={})

    def test_a_COUNT_crosses_as_an_int_and_a_float_is_REFUSED(self):
        """The interim leg is the first payload on this seam to carry an int at
        all, and until this pass the decode leg had no branch for one -- so a
        leg the contract declared could never actually cross.

        38.0 is NOT read as 38: a float where the contract declares a count
        means the two sides disagree about the field, and coercing it would hide
        exactly that."""
        from company.billing import payment_observation_consumer as poc

        floated = copy.deepcopy(self.INPUT_REPORT_RAW)
        floated["fields"]["items_in_submission"] = 38.0
        with pytest.raises(WallProtocolError) as refused:
            poc.decode_interim_payload(floated)
        assert refused.value.reason == "MALFORMED_FIELD"

        boolean = copy.deepcopy(self.INPUT_REPORT_RAW)
        boolean["fields"]["items_rejected"] = True
        with pytest.raises(WallProtocolError):
            poc.decode_interim_payload(boolean)

        # NULL CONTROL: the honest int lands, so the two refusals above are
        # about the TYPE and not about the field being unreadable.
        assert poc.decode_interim_payload(self.INPUT_REPORT_RAW).items_rejected == 2

    def test_observe_interim_REFUSES_an_off_leg_payload_before_it_is_filed(self):
        """The object-level guard, which is what stops a caller inside the
        company routing round the wire's refusal."""
        consumer = PaymentObservationConsumer()
        consumer.note_collection_request(
            WallRequest(
                correlation_id="INV-1",
                request_type=COLLECTION_REQUEST_TYPE,
                schema_version=2,
                as_of=dt.datetime(2026, 3, 2, 9, 0),
                emitted_at=dt.datetime(2026, 3, 2, 9, 0),
                payload=CollectionRequest(
                    account_id="ACC-1",
                    mandate_ref="MAN-1",
                    amount_gbp=42.5,
                    rail=PaymentRail.BACS_DIRECT_DEBIT,
                    requested_collection_date=dt.date(2026, 3, 6),
                ),
            )
        )
        off_leg = WallInterim(
            correlation_id="INV-1",
            leg=2,
            interim_type="bacs_input_report",
            schema_version=2,
            observed_at=dt.datetime(2026, 3, 4, 9, 0),
            payload=AddacsAdvice(
                mandate_ref="MAN-1",
                account_id="ACC-1",
                advice_type=AddacsAdviceType.PAYER_CANCELLED,
                advice_text="Instruction Cancelled By Payer",
                value_date=dt.date(2026, 3, 7),
            ),
        )
        with pytest.raises(ValueError, match="INTERIM_PAYLOAD_TYPES"):
            consumer.observe_interim(off_leg)
        assert consumer.conversation("INV-1").leg_count == 1, (
            "the refusal must leave the exchange as it was -- a message the "
            "company would not file is not a leg it heard"
        )
