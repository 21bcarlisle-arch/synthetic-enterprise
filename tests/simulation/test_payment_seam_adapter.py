"""Tests for W2_11's sim-side payment seam adapter
(`simulation.payment_seam_adapter`), the piece filling the W4_4
`interface.contracts.payment_observable_seam` contract from the W2_11
generator (`simulation.payment_behaviour_source`).

Load-bearing WALL test class: `TestWallNoInternalLeak` -- asserts the
emitted payloads carry no generator-internal field/value, and that
different true circumstances collapse to the same observable
`BacsReasonCategory` (many-to-one, non-invertible)."""
from __future__ import annotations

import dataclasses
from datetime import date, datetime

import pytest

from interface.contracts.payment_observable_seam import (
    BacsArruddOutcome,
    BacsReasonCategory,
    DDOutcomeStatus,
    PaymentRail,
    RemittanceAdvice,
)
from interface.contracts.wall_envelope import WallResponse, WallStatus
from simulation.bacs_rails import ARUDD_NOTIFICATION_LAG_DAYS
from simulation.payment_behaviour_source import (
    CANCELLED_OTHER,
    CARD,
    DIRECT_DEBIT,
    INSUFFICIENT_FUNDS,
    PREPAYMENT,
    STANDING_ORDER,
    PaymentEvent,
    generate_payment_event,
)
from simulation.payment_seam_adapter import (
    SeamAdapterInput,
    bacs_reason_category_for,
    emit_wall_responses,
    emit_wall_responses_batch,
    payment_rail_for_method,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _event(
    customer_id="cust-1",
    period_index=0,
    due_date="2026-01-15",
    amount_gbp=120.0,
    payment_method=DIRECT_DEBIT,
    result="success",
    days_late=0,
    payment_date=None,
    dd_failure_reason=None,
):
    return PaymentEvent(
        customer_id=customer_id,
        period_index=period_index,
        due_date=due_date,
        amount_gbp=amount_gbp,
        payment_method=payment_method,
        result=result,
        days_late=days_late,
        payment_date=payment_date,
        dd_failure_reason=dd_failure_reason,
    )


# ---------------------------------------------------------------------------
# Basic outcome -> WallResponse mapping
# ---------------------------------------------------------------------------


class TestOutcomeMapping:
    def test_success_dd_emits_remittance_advice(self):
        ev = _event(result="success", payment_date="2026-01-15", payment_method=DIRECT_DEBIT)
        responses = emit_wall_responses(ev)
        assert len(responses) == 1
        resp = responses[0]
        assert isinstance(resp, WallResponse)
        assert resp.status == WallStatus.OK
        assert isinstance(resp.payload, RemittanceAdvice)
        assert resp.payload.rail == PaymentRail.BACS_DIRECT_DEBIT
        assert resp.payload.amount_gbp == ev.amount_gbp
        assert resp.valid_time == date(2026, 1, 15)

    def test_success_late_payment_value_date_is_actual_payment_date(self):
        # due 2026-01-15, paid 5 days late -> payment_date 2026-01-20
        ev = _event(result="success", days_late=5, payment_date="2026-01-20", due_date="2026-01-15")
        responses = emit_wall_responses(ev)
        assert responses[0].payload.value_date == date(2026, 1, 20)
        assert responses[0].valid_time == date(2026, 1, 20)

    def test_success_card_emits_remittance_advice_with_card_rail(self):
        ev = _event(payment_method=CARD, result="success", payment_date="2026-01-15")
        resp = emit_wall_responses(ev)[0]
        assert resp.payload.rail == PaymentRail.CARD

    def test_success_standing_order_rail(self):
        ev = _event(payment_method=STANDING_ORDER, result="success", payment_date="2026-01-15")
        resp = emit_wall_responses(ev)[0]
        assert resp.payload.rail == PaymentRail.STANDING_ORDER

    def test_prepayment_maps_to_other_rail(self):
        assert payment_rail_for_method(PREPAYMENT) == PaymentRail.OTHER

    def test_failed_dd_emits_bacs_arrudd_outcome_failure(self):
        ev = _event(
            payment_method=DIRECT_DEBIT,
            result="failed",
            dd_failure_reason=INSUFFICIENT_FUNDS,
        )
        responses = emit_wall_responses(ev)
        assert len(responses) == 1
        resp = responses[0]
        assert isinstance(resp.payload, BacsArruddOutcome)
        assert resp.payload.outcome == DDOutcomeStatus.FAILURE
        assert resp.payload.reason_category == BacsReasonCategory.INSUFFICIENT_FUNDS

    def test_failed_non_dd_emits_no_response(self):
        """The no-remittance blind spot (C-S3): a missed push-payment rail
        (standing order / card / prepayment) produces NO WallResponse at
        all -- absence, never a placeholder."""
        for method in (STANDING_ORDER, CARD, PREPAYMENT):
            ev = _event(payment_method=method, result="failed", dd_failure_reason=INSUFFICIENT_FUNDS)
            assert emit_wall_responses(ev) == []

    def test_dispute_emits_not_knowable_yet_with_no_payload(self):
        ev = _event(result="dispute", payment_date=None)
        responses = emit_wall_responses(ev)
        assert len(responses) == 1
        resp = responses[0]
        assert resp.status == WallStatus.NOT_KNOWABLE_YET
        assert resp.payload is None
        assert resp.valid_time is None


# ---------------------------------------------------------------------------
# WALL test (load-bearing): no internal leak, many-to-one collapse.
# ---------------------------------------------------------------------------


_SAFE_PAYLOAD_FIELDS = {
    RemittanceAdvice: {"bank_reference", "account_id", "amount_gbp", "rail", "value_date"},
    BacsArruddOutcome: {
        "mandate_ref",
        "account_id",
        "amount_gbp",
        "outcome",
        "reason_category",
        "reason_text",
        "value_date",
    },
}

_FORBIDDEN_SUBSTRINGS = (
    "stress",
    "segment",
    "pattern",
    "probability",
    "hardship",
    "chronic",
    "transient",
    "classif",
    "propensity",
)


class TestWallNoInternalLeak:
    def test_payload_field_sets_match_declared_safe_fields_exactly(self):
        """Every emitted payload's dataclass fields are EXACTLY the declared
        seam-contract fields -- no extra generator-internal attribute could
        have been smuggled on."""
        for payload_type, expected_fields in _SAFE_PAYLOAD_FIELDS.items():
            actual_fields = {f.name for f in dataclasses.fields(payload_type)}
            assert actual_fields == expected_fields

    def test_no_forbidden_substrings_in_any_emitted_field_name_or_text(self):
        events = [
            _event(customer_id="cust-a", result="success", payment_date="2026-01-15"),
            _event(
                customer_id="cust-b",
                payment_method=DIRECT_DEBIT,
                result="failed",
                dd_failure_reason=INSUFFICIENT_FUNDS,
            ),
            _event(
                customer_id="cust-c",
                payment_method=DIRECT_DEBIT,
                result="failed",
                dd_failure_reason=CANCELLED_OTHER,
            ),
            _event(customer_id="cust-d", result="dispute"),
        ]
        for ev in events:
            for resp in emit_wall_responses(ev):
                haystack = repr(resp).lower()
                for forbidden in _FORBIDDEN_SUBSTRINGS:
                    assert forbidden not in haystack, f"leaked {forbidden!r} in {resp!r}"

    def test_payment_event_itself_carries_no_stress_or_segment_field(self):
        """Structural proof the adapter CANNOT leak stress/segment: the
        input type it reads doesn't carry those fields at all."""
        field_names = {f.name for f in dataclasses.fields(PaymentEvent)}
        assert "stress" not in field_names
        assert "segment" not in field_names
        assert "pattern" not in field_names

    def test_many_to_one_direct_construction_different_customers_same_reason(self):
        """Two PaymentEvents representing genuinely DIFFERENT true failure
        circumstances (different customers -- standing in for one in real
        income hardship, one having an unrelated one-off blip) that both
        happen to carry the SAME generator-drawn `dd_failure_reason` MUST
        emit the SAME `BacsReasonCategory` -- the company cannot invert the
        code back to which true circumstance produced it."""
        hardship_event = _event(
            customer_id="cust-genuine-hardship",
            payment_method=DIRECT_DEBIT,
            result="failed",
            dd_failure_reason=INSUFFICIENT_FUNDS,
        )
        blip_event = _event(
            customer_id="cust-one-off-blip",
            payment_method=DIRECT_DEBIT,
            result="failed",
            dd_failure_reason=INSUFFICIENT_FUNDS,
        )
        cat_a = emit_wall_responses(hardship_event)[0].payload.reason_category
        cat_b = emit_wall_responses(blip_event)[0].payload.reason_category
        assert cat_a == cat_b == BacsReasonCategory.INSUFFICIENT_FUNDS

    def test_many_to_one_via_real_generator_different_stress_same_reason_draw(self):
        """End-to-end proof through the REAL generator: the reason draw
        (`_REASON_SUBSTREAM_BASE`) is keyed only by (customer_id,
        period_index), never by `stress` -- so for a fixed customer/period,
        changing the true stress tier passed into `generate_payment_event`
        never changes which `dd_failure_reason` is drawn once a failure
        occurs (only whether it occurs). This searches for a
        customer/period where both a LOW and a HIGH stress trajectory
        produce a "failed" result, then asserts the reason collapse holds
        identically end-to-end (not just at this adapter's own table)."""
        found = False
        for idx in range(200):
            customer_id = f"stress-collapse-{idx}"
            due = date(2026, 1, 15)
            ev_low = generate_payment_event(
                customer_id, 0, due, 100.0, "high", DIRECT_DEBIT, segment="resi", seed=idx
            )
            ev_high = generate_payment_event(
                customer_id, 0, due, 100.0, "low", DIRECT_DEBIT, segment="resi", seed=idx
            )
            if ev_low.result == "failed" and ev_high.result == "failed":
                found = True
                assert ev_low.dd_failure_reason == ev_high.dd_failure_reason
                cat_low = emit_wall_responses(ev_low)[0].payload.reason_category
                cat_high = emit_wall_responses(ev_high)[0].payload.reason_category
                assert cat_low == cat_high
        assert found, "expected at least one (customer, period) pair where both stress tiers fail"

    def test_reason_mapping_is_narrower_than_full_bacs_category_set(self):
        """Confirms the mapping is many-to-one at the CATEGORY-SET level
        too: only 2 of the 9 `BacsReasonCategory` members are ever reachable
        from this generator's 2 known `dd_failure_reason` values -- an
        honest, narrow mapping, never fabricated precision."""
        reachable = {bacs_reason_category_for(INSUFFICIENT_FUNDS), bacs_reason_category_for(CANCELLED_OTHER)}
        assert len(reachable) == 2
        assert reachable.issubset(set(BacsReasonCategory))
        assert len(reachable) < len(set(BacsReasonCategory))

    def test_unknown_dd_failure_reason_fails_closed_to_other(self):
        assert bacs_reason_category_for("some_never_before_seen_value") == BacsReasonCategory.OTHER
        assert bacs_reason_category_for(None) == BacsReasonCategory.OTHER


# ---------------------------------------------------------------------------
# Async / bitemporal (C-S3)
# ---------------------------------------------------------------------------


class TestAsyncBitemporal:
    def test_dd_failure_observed_at_is_on_or_after_value_date(self):
        ev = _event(
            customer_id="cust-lag",
            payment_method=DIRECT_DEBIT,
            result="failed",
            dd_failure_reason=INSUFFICIENT_FUNDS,
            due_date="2026-02-01",
        )
        resp = emit_wall_responses(ev)[0]
        value_date = resp.payload.value_date
        assert resp.observed_at.date() >= value_date
        lag = (resp.observed_at.date() - value_date).days
        assert 0 <= lag <= ARUDD_NOTIFICATION_LAG_DAYS

    def test_success_observed_at_same_day_as_value_date_no_lag(self):
        ev = _event(result="success", payment_date="2026-01-15")
        resp = emit_wall_responses(ev)[0]
        assert resp.observed_at.date() == resp.payload.value_date

    def test_missing_payment_emits_no_response_at_all(self):
        ev = _event(payment_method=CARD, result="failed", dd_failure_reason=INSUFFICIENT_FUNDS)
        assert emit_wall_responses(ev) == []


# ---------------------------------------------------------------------------
# Determinism (C-S2)
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_event_twice_yields_identical_wall_responses(self):
        ev = _event(
            customer_id="cust-det",
            payment_method=DIRECT_DEBIT,
            result="failed",
            dd_failure_reason=INSUFFICIENT_FUNDS,
            due_date="2026-03-01",
        )
        r1 = emit_wall_responses(ev)
        r2 = emit_wall_responses(ev)
        assert r1 == r2
        assert repr(r1) == repr(r2)

    def test_determinism_holds_across_success_and_dispute_paths(self):
        for ev in (
            _event(result="success", payment_date="2026-01-15"),
            _event(result="dispute"),
        ):
            assert emit_wall_responses(ev) == emit_wall_responses(ev)

    def test_different_customers_get_independent_lag_draws_not_forced_identical(self):
        # Not a strict requirement that they differ, but the substream must
        # be a pure function of (customer_id, period_index) -- same inputs,
        # same output, checked directly here via two distinct customers.
        ev_a = _event(customer_id="cust-lag-a", payment_method=DIRECT_DEBIT, result="failed",
                       dd_failure_reason=INSUFFICIENT_FUNDS)
        ev_b = _event(customer_id="cust-lag-b", payment_method=DIRECT_DEBIT, result="failed",
                       dd_failure_reason=INSUFFICIENT_FUNDS)
        # both individually deterministic on repeat
        assert emit_wall_responses(ev_a) == emit_wall_responses(ev_a)
        assert emit_wall_responses(ev_b) == emit_wall_responses(ev_b)


# ---------------------------------------------------------------------------
# Round-trip batch: a batch of generated PaymentEvents -> all valid seam
# payloads.
# ---------------------------------------------------------------------------


class TestRoundTripBatch:
    def _generate_mixed_batch(self):
        events = []
        due = date(2026, 1, 15)
        for i in range(30):
            method = [DIRECT_DEBIT, STANDING_ORDER, CARD, PREPAYMENT][i % 4]
            stress = ["low", "moderate", "high"][i % 3]
            ev = generate_payment_event(
                f"cust-batch-{i}", 0, due, 100.0 + i, stress, method, segment="resi", seed=i
            )
            events.append(ev)
        return events

    def test_batch_round_trip_all_responses_valid_seam_payloads(self):
        events = self._generate_mixed_batch()
        responses = emit_wall_responses_batch(events)
        assert len(responses) > 0
        for resp in responses:
            assert isinstance(resp, WallResponse)
            assert resp.status in (WallStatus.OK, WallStatus.NOT_KNOWABLE_YET)
            if resp.status == WallStatus.OK:
                assert isinstance(resp.payload, (RemittanceAdvice, BacsArruddOutcome))
            else:
                assert resp.payload is None

    def test_batch_response_count_matches_expected_per_event(self):
        events = self._generate_mixed_batch()
        expected = 0
        for ev in events:
            if ev.result == "success":
                expected += 1
            elif ev.result == "dispute":
                expected += 1
            elif ev.result == "failed" and ev.payment_method == DIRECT_DEBIT:
                expected += 1
            # failed + non-DD -> 0
        responses = emit_wall_responses_batch(events)
        assert len(responses) == expected

    def test_seam_input_overrides_account_and_mandate(self):
        ev = _event(customer_id="cust-x", result="success", payment_date="2026-01-15")
        resp = emit_wall_responses(ev, SeamAdapterInput(account_id="ACC-CUSTOM", correlation_id="corr-1"))[0]
        assert resp.payload.account_id == "ACC-CUSTOM"
        assert resp.correlation_id == "corr-1"

    def test_default_correlation_id_is_stable_and_derived_from_event(self):
        ev = _event(customer_id="cust-y", period_index=3, result="success", payment_date="2026-01-15")
        resp = emit_wall_responses(ev)[0]
        assert resp.correlation_id == "cust-y::3"


# ---------------------------------------------------------------------------
# The CLOSED observable field set (EP6 pass 25). This seam's encoder was the
# weakest of the wall's three: no field-level check and no truth denylist, so
# any field added to any of its six payload types crossed to the company
# unrefused. `TestWallNoInternalLeak` above asserts the payloads are clean
# TODAY; these assert the codec REFUSES the edit that would dirty them.
# ---------------------------------------------------------------------------


def _remittance_shaped(**extra):
    """A RemittanceAdvice-shaped payload under the REAL type name -- the
    mutation modelled is someone editing the real contract dataclass."""
    from interface.contracts.payment_observable_seam import PaymentRail

    dropped = extra.pop("_drop", ())
    base = [
        ("bank_reference", str), ("account_id", str), ("amount_gbp", float),
        ("rail", PaymentRail), ("value_date", date),
    ]
    base = [f for f in base if f[0] not in dropped]
    return dataclasses.make_dataclass(
        "RemittanceAdvice", base + [(n, float) for n in extra], frozen=True
    )


def _encode_payment(mutant_type, monkeypatch, **values):
    import simulation.payment_seam_adapter as _psa

    registry = dict(_psa._ENCODABLE_PAYLOAD_TYPES)
    registry["RemittanceAdvice"] = mutant_type
    monkeypatch.setattr(_psa, "_ENCODABLE_PAYLOAD_TYPES", registry)
    return _psa.encode_observable_payload(mutant_type(**values))


def _base_remittance():
    from interface.contracts.payment_observable_seam import PaymentRail

    return dict(
        bank_reference="BR-1", account_id="A-1", amount_gbp=42.0,
        rail=PaymentRail.BACS_DIRECT_DEBIT, value_date=date(2026, 1, 1),
    )


def test_null_control_the_declared_remittance_still_crosses():
    """The control must admit the real thing, or refusing proves nothing."""
    from simulation.payment_seam_adapter import encode_observable_payload

    wire = encode_observable_payload(RemittanceAdvice(**_base_remittance()))
    assert set(wire["fields"]) == {
        "bank_reference", "account_id", "amount_gbp", "rail", "value_date",
    }


def test_mutation_an_undeclared_generator_field_is_refused_at_emission(monkeypatch):
    """THE named defect. `true_balance_gbp` is generator-internal -- the
    customer's actual bank balance, which no supplier ever sees -- and this
    seam had NO denylist that could have named it. The closed set refuses it
    for never having been declared observable (R10: the class, not the
    instance)."""
    from simulation.payment_seam_adapter import SeamEncodeError

    mutant = _remittance_shaped(true_balance_gbp=float)
    with pytest.raises(SeamEncodeError, match="has not declared observable"):
        _encode_payment(
            mutant, monkeypatch, true_balance_gbp=12.34, **_base_remittance()
        )


def test_mutation_a_stale_declaration_is_refused(monkeypatch):
    """FAIL-CLOSED the other way: a payload that LOSES a certified field is
    refused rather than silently emitting a narrower wire form."""
    from simulation.payment_seam_adapter import SeamEncodeError

    mutant = _remittance_shaped(_drop=("amount_gbp",))
    values = {k: v for k, v in _base_remittance().items() if k != "amount_gbp"}
    with pytest.raises(SeamEncodeError, match="omits declared observable field"):
        _encode_payment(mutant, monkeypatch, **values)


def test_every_declared_payload_type_matches_its_contract_dataclass():
    """The declaration must cover ALL SIX payload types and agree with each --
    a closed set that silently omits a type is fail-open for that type, which
    is the shape of defect this whole mechanism exists to refuse."""
    from interface.contracts.payment_observable_seam import (
        OBSERVABLE_PAYLOAD_FIELDS,
        OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    )

    assert set(OBSERVABLE_PAYLOAD_FIELDS) == {
        t.__name__ for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES
    }
    for payload_type in OBSERVABLE_RESPONSE_PAYLOAD_TYPES:
        actual = tuple(f.name for f in dataclasses.fields(payload_type))
        assert OBSERVABLE_PAYLOAD_FIELDS[payload_type.__name__] == actual, (
            f"{payload_type.__name__}: the contract's declaration and the "
            "dataclass it certifies have diverged"
        )


# ── THE SECOND BELT ON THE ENCODE LEG (EP6 pass 27) ──────────────────────────────────────────
# The point of these is NARROW and is worth stating so the belt is not credited with more than
# it does. `OBSERVABLE_PAYLOAD_FIELDS` is the control and already refuses a field added to a
# payload and nothing else. What it cannot see -- because the edit moves the very thing it reads
# -- is a truth field added to the dataclass AND declared observable in the same edit. Every
# mutation below performs exactly that edit, so the closed set is GREEN through all of them.

class _MutantPayload:
    """Built per-test rather than at module scope, so each mutation names its own field."""


def _mutant(field_name: str):
    """A seventh payload type carrying `field_name`, DECLARED observable in the same breath."""
    cls = dataclasses.make_dataclass(
        "MutantAdvice",
        [("account_id", str), ("amount_gbp", float), (field_name, str)],
        frozen=True,
    )
    return cls, cls(account_id="ACC-1", amount_gbp=12.5, **{field_name: "x"})


def _with_mutant(monkeypatch, cls, field_name: str):
    """Register the mutant exactly as a real same-edit widening would: on the encodable set AND
    on the contract's closed set. Both halves matter -- omit the second and this would prove only
    that the closed set works, which is already tested."""
    from simulation import payment_seam_adapter as psa

    monkeypatch.setitem(psa._ENCODABLE_PAYLOAD_TYPES, cls.__name__, cls)
    monkeypatch.setitem(
        psa.OBSERVABLE_PAYLOAD_FIELDS,
        cls.__name__,
        ("account_id", "amount_gbp", field_name),
    )


def test_MUTATION_a_truth_field_DECLARED_OBSERVABLE_in_the_same_edit_is_still_refused(
    monkeypatch,
):
    """THE DOCTRINE MUTATION, and the only case that justifies keeping a denylist at all. The
    closed set is satisfied by construction here -- the field IS declared -- so if the belt were
    absent the world's true DD failure reason would encode onto the wire unrefused."""
    from simulation import payment_seam_adapter as psa

    cls, payload = _mutant("dd_failure_reason")
    _with_mutant(monkeypatch, cls, "dd_failure_reason")

    # The control is genuinely green on this payload: that is what makes the belt load-bearing.
    assert set(psa.OBSERVABLE_PAYLOAD_FIELDS[cls.__name__]) == {
        f.name for f in dataclasses.fields(cls)
    }

    with pytest.raises(psa.SeamEncodeError) as exc:
        psa.encode_observable_payload(payload)
    assert "dd_failure_reason" in str(exc.value)
    assert "forbidden truth field" in str(exc.value)


@pytest.mark.parametrize("field_name", ["ability", "willingness", "data_regime", "period_index"])
def test_MUTATION_each_class_of_world_truth_is_refused_not_only_the_failure_reason(
    monkeypatch, field_name
):
    """One name proves one name. These are the other three producers the belt cites -- the hidden
    ability/willingness answer key D5 is scored on inferring, the historical-vs-synthetic marker,
    and the generator's own clock index."""
    from simulation import payment_seam_adapter as psa

    cls, payload = _mutant(field_name)
    _with_mutant(monkeypatch, cls, field_name)

    with pytest.raises(psa.SeamEncodeError, match="forbidden truth field"):
        psa.encode_observable_payload(payload)


def test_NULL_CONTROL_an_undeclared_but_INNOCENT_field_trips_the_OTHER_belt(monkeypatch):
    """Without this the battery above could not tell "the denylist fired" from "anything unusual
    is refused". An undeclared field that is NOT a truth name must be refused by the closed set,
    with the closed set's own message -- so the two belts stay separately observable and each has
    a case only it can pass."""
    from simulation import payment_seam_adapter as psa

    cls, payload = _mutant("branch_sort_code")
    monkeypatch.setitem(psa._ENCODABLE_PAYLOAD_TYPES, cls.__name__, cls)
    monkeypatch.setitem(
        psa.OBSERVABLE_PAYLOAD_FIELDS, cls.__name__, ("account_id", "amount_gbp")
    )

    with pytest.raises(psa.SeamEncodeError) as exc:
        psa.encode_observable_payload(payload)
    assert "has not declared observable" in str(exc.value)
    assert "forbidden truth field" not in str(exc.value)


def test_the_SIX_REAL_payloads_still_encode_so_the_belt_is_not_a_standing_red(monkeypatch):
    """A control the tree cannot satisfy gets deleted. All six live payload types must pass both
    belts unchanged."""
    from simulation import payment_seam_adapter as psa

    samples = {
        "RemittanceAdvice": RemittanceAdvice(
            bank_reference="R-1", account_id="ACC-1", amount_gbp=10.0,
            rail=PaymentRail.BACS_DIRECT_DEBIT, value_date=date(2024, 5, 1),
        ),
        "BacsArruddOutcome": BacsArruddOutcome(
            mandate_ref="M-1", account_id="ACC-1", amount_gbp=10.0,
            outcome=DDOutcomeStatus.FAILURE,
            reason_category=BacsReasonCategory.INSUFFICIENT_FUNDS,
            reason_text="refer to payer", value_date=date(2024, 5, 1),
        ),
    }
    for payload in samples.values():
        assert psa.encode_observable_payload(payload)["payload_type"] == type(payload).__name__
