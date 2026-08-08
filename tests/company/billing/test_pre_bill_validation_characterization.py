"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/pre_bill_validation.py — the Tier-1 gate every bill passes
through before issue. Its stated contract is zero-tolerance: a bill either PASSes
or is HELD to an exception queue, and the checks are documented as failing CLOSED
on missing/malformed input.

All inputs are fixed literals; nothing here reads the wall clock.
"""
from __future__ import annotations

import pytest

from company.billing.pre_bill_validation import (
    ValidationOutcome,
    check_reads_reconcile,
    exception_queue_as_dicts,
    validate_bill,
    validate_bills,
    validate_rendered_bill_money,
    validate_rendered_bill_reads,
)


def bill(**kw):
    """A clean resi electricity bill: £90 subtotal + £4.50 VAT at 5% = £94.50."""
    base = dict(
        customer_id="C1",
        period_start="2024-01-01",
        period_end="2024-01-31",
        segment="resi",
        commodity="electricity",
        total_consumption_kwh=300.0,
        commodity_amount_gbp=60.0,
        non_commodity_amount_gbp=20.0,
        standing_charge_gbp=10.0,
        vat_gbp=4.50,
        total_amount_gbp=94.50,
    )
    base.update(kw)
    return base


# ---------------------------------------------------------------------------
# The happy path
# ---------------------------------------------------------------------------


def test_a_clean_resi_bill_passes_with_no_reasons():
    r = validate_bill(bill())
    assert r.outcome == ValidationOutcome.PASS
    assert r.reasons == []
    assert r.held is False
    assert (r.customer_id, r.period_end) == ("C1", "2024-01-31")


def test_a_clean_sme_bill_at_20_percent_passes():
    r = validate_bill(bill(segment="sme", vat_gbp=18.0, total_amount_gbp=108.0,
                           total_consumption_kwh=3000.0))
    assert r.outcome == ValidationOutcome.PASS


# ---------------------------------------------------------------------------
# Individual HELD reasons
# ---------------------------------------------------------------------------


def test_resi_billed_at_20_percent_vat_is_held():
    """The C6 SME-as-Household class: a domestic customer charged the business
    rate."""
    r = validate_bill(bill(vat_gbp=18.0, total_amount_gbp=108.0))
    assert r.held is True
    assert any("vat_by_segment" in x for x in r.reasons)


def test_a_bill_that_does_not_foot_is_held():
    r = validate_bill(bill(total_amount_gbp=999.0))
    assert r.held is True
    assert any("does not foot" in x for x in r.reasons)


def test_a_negative_line_item_is_held_on_a_non_credit_bill():
    r = validate_bill(bill(commodity_amount_gbp=-60.0, vat_gbp=-4.50,
                           total_amount_gbp=-25.50))
    assert r.held is True
    assert any("negative" in x for x in r.reasons)


def test_an_inverted_bill_period_is_rejected_not_clamped():
    r = validate_bill(bill(period_start="2024-02-01", period_end="2024-01-01"))
    assert r.held is True
    assert any("temporally impossible" in x for x in r.reasons)


def test_vat_charged_on_a_zero_subtotal_is_held_rather_than_skipped():
    """The 2026-07-13 fail-open fix: a zero subtotal used to skip VAT validation
    entirely. VAT on nothing is now HELD."""
    r = validate_bill(bill(commodity_amount_gbp=0.0, non_commodity_amount_gbp=0.0,
                           standing_charge_gbp=0.0, vat_gbp=5.0,
                           total_amount_gbp=5.0, total_consumption_kwh=0.0))
    assert any("VAT on nothing" in x for x in r.reasons)


def test_implausible_resi_consumption_is_held():
    r = validate_bill(bill(total_consumption_kwh=99999.0))
    assert r.held is True
    assert any("implausible" in x for x in r.reasons)


def test_a_bill_can_accumulate_several_reasons_at_once():
    r = validate_bill(bill(period_start="2024-02-01", period_end="2024-01-01"))
    assert len(r.reasons) > 1  # period + downstream checks all fire


def test_a_zero_consumption_resi_bill_is_held_by_the_plausibility_check():
    """An entirely empty bill is legitimate to the footing/VAT checks but 0 kWh
    over 31 days trips the resi plausibility band, so it is still HELD."""
    r = validate_bill(bill(commodity_amount_gbp=0.0, non_commodity_amount_gbp=0.0,
                           standing_charge_gbp=0.0, vat_gbp=0.0,
                           total_amount_gbp=0.0, total_consumption_kwh=0.0))
    assert r.held is True
    assert any("implausible" in x for x in r.reasons)


# ---------------------------------------------------------------------------
# Malformed input — the gate's own fail-closed claim
# ---------------------------------------------------------------------------


def test_a_bill_missing_period_start_raises_instead_of_being_held():
    """SURPRISE (boundary class, money-relevant): the module documents these checks
    as failing CLOSED on "missing/malformed" input, and `check_bill_period_sane`
    does correctly add a HELD reason for the missing field. But execution then
    continues to `_days_in_period`, which subscripts `bill["period_start"]`
    directly and raises KeyError — so the already-collected HELD reason is never
    returned. A malformed bill is neither PASSed nor HELD: it escapes the gate as
    an exception."""
    b = bill()
    del b["period_start"]
    with pytest.raises(KeyError, match="period_start"):
        validate_bill(b)


def test_the_same_crash_happens_on_a_business_segment():
    b = bill(segment="sme", vat_gbp=18.0, total_amount_gbp=108.0)
    del b["period_start"]
    with pytest.raises(KeyError, match="period_start"):
        validate_bill(b)


def test_a_null_period_start_raises_a_typeerror():
    with pytest.raises(TypeError, match="fromisoformat"):
        validate_bill(bill(period_start=None))


def test_an_empty_bill_dict_raises():
    with pytest.raises(KeyError):
        validate_bill({})


def test_one_malformed_bill_aborts_the_whole_batch():
    """SURPRISE (boundary class, money-relevant): `validate_bills` calls
    `validate_bill` with no exception guard, so the crash above propagates out of
    the batch. A single malformed bill stops every LATER bill in the run from
    being validated or issued at all — the opposite of "held to an exception queue,
    never sent", and a whole-run outage rather than a one-bill hold."""
    bad = bill(customer_id="C2")
    del bad["period_start"]
    with pytest.raises(KeyError, match="period_start"):
        validate_bills([bill(), bad, bill(customer_id="C3")])


# ---------------------------------------------------------------------------
# validate_bills / exception_queue_as_dicts
# ---------------------------------------------------------------------------


def test_validate_bills_partitions_passing_from_held():
    passing, queue = validate_bills([bill(), bill(customer_id="C2", total_amount_gbp=999.0)])
    assert [b["customer_id"] for b in passing] == ["C1"]
    assert [r.customer_id for r in queue] == ["C2"]


def test_validate_bills_on_an_empty_list():
    assert validate_bills([]) == ([], [])


def test_exception_queue_serialises_to_the_operational_shape():
    _, queue = validate_bills([bill(total_amount_gbp=999.0)])
    (row,) = exception_queue_as_dicts(queue)
    assert row["customer_id"] == "C1"
    assert row["period_end"] == "2024-01-31"
    assert isinstance(row["reasons"], list) and row["reasons"]


def test_exception_queue_as_dicts_on_an_empty_queue():
    assert exception_queue_as_dicts([]) == []


# ---------------------------------------------------------------------------
# check_reads_reconcile / validate_rendered_bill_reads
# ---------------------------------------------------------------------------


def test_reads_reconcile_against_the_printed_rounded_reads():
    """The director's observed 331.1-vs-331.2 defect: the billed quantity must be
    closing minus opening computed from the PRINTED reads."""
    assert check_reads_reconcile(100.0, 431.1, 331.1) is True
    assert check_reads_reconcile(100.0, 431.1, 331.2) is False


@pytest.mark.parametrize(
    "opening,closing,billed",
    [(None, 431.1, 331.1), (100.0, None, 331.1), (100.0, 431.1, None)],
)
def test_reads_reconcile_is_not_applicable_when_a_read_is_absent(opening, closing, billed):
    """Returns True (not applicable) rather than failing — a bill carrying no meter
    reads is not checked by this control at all."""
    assert check_reads_reconcile(opening, closing, billed) is True


def test_reads_tolerance_is_half_a_tenth_of_a_kwh():
    assert check_reads_reconcile(100.0, 431.1, 331.15) is True   # within 0.05
    assert check_reads_reconcile(100.0, 431.1, 331.16) is False


def test_validate_rendered_bill_reads_returns_a_reason_on_a_mismatch():
    reasons = validate_rendered_bill_reads(
        {"opening_read_kwh": 100.0, "closing_read_kwh": 431.1, "consumption_kwh": 331.2}
    )
    assert len(reasons) == 1
    assert "does not reconcile" in reasons[0]


def test_validate_rendered_bill_reads_is_silent_when_reads_are_missing():
    assert validate_rendered_bill_reads({}) == []


# ---------------------------------------------------------------------------
# validate_rendered_bill_money
# ---------------------------------------------------------------------------


def test_rendered_money_check_passes_on_a_bill_that_foots_exactly():
    assert validate_rendered_bill_money(bill()) == []


def test_rendered_money_check_fires_when_printed_items_do_not_sum_to_the_total():
    reasons = validate_rendered_bill_money(bill(total_amount_gbp=95.00))
    assert len(reasons) == 1
    assert "do not sum exactly" in reasons[0]
