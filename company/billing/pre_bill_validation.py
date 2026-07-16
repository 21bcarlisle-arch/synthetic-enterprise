"""Tier-1 pre-bill validation gate -- Phase 3 of DOMAIN_SENSE_AND_COMPLIANCE.md.

Director's Principle 1 (binding): "Bills must be accurate, above all. 100% of
bills pass preventive validation before issue; failures are HELD to an
exception queue, never sent. Zero tolerance, continuous, not sampled."

Checks every bill against the Tier-1 obligations named in
company/compliance/obligations_register.py ("slc_6_7_billing_accuracy",
"vat_by_segment") using the anchored predicates in
company/compliance/domain_invariants.py -- the same class of defect R10
names (C6 SME-as-Household at 20% VAT; 4.3x-sigma consumption anomaly).

A HELD bill is a real company-side event, not a silent drop: it is excluded
from this run's normal issuance and recorded on the exception queue with the
specific reason(s). Held bills reaching a customer later (once the
underlying data issue is fixed and the bill re-validates) are exactly the
"billing delayed" scenario Phase 3's existing meter-read-delay/GSOP-
compensation machinery already models -- this gate does not build a second,
parallel consequence mechanism; it produces the HELD signal that mechanism
can act on. Wiring an automatic retry/re-issue cadence and a GSOP-
compensation trigger specifically for a gate-held bill is flagged as
follow-up, not built in this pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from company.compliance.domain_invariants import (
    check_vat,
    check_vat_consistent_with_consumption,
    consumption_implied_vat_rate,
    check_resi_bill_consumption_plausible,
    check_back_billing_cap_respected,
    check_bill_foots,
    check_bill_line_items_non_negative,
    check_bill_period_sane,
    is_credit_bill,
)


class ValidationOutcome(str, Enum):
    PASS = "pass"
    HELD = "held"


@dataclass(frozen=True)
class BillValidationResult:
    customer_id: str
    period_end: str
    outcome: ValidationOutcome
    reasons: list = field(default_factory=list)  # empty when PASS

    @property
    def held(self) -> bool:
        return self.outcome == ValidationOutcome.HELD


def _days_in_period(bill: dict) -> float:
    from datetime import date
    start = date.fromisoformat(bill["period_start"])
    end = date.fromisoformat(bill["period_end"])
    return max((end - start).days + 1, 1)


def _bill_subtotal(bill: dict) -> float:
    return (
        bill.get("commodity_amount_gbp", 0.0)
        + bill.get("non_commodity_amount_gbp", 0.0)
        + bill.get("standing_charge_gbp", 0.0)
    )


def _actual_vat_rate(bill: dict) -> float | None:
    subtotal = _bill_subtotal(bill)
    if subtotal <= 0:
        return None
    return bill.get("vat_gbp", 0.0) / subtotal


def validate_bill(bill: dict) -> BillValidationResult:
    """Run every Tier-1 check against one bill dict (the shape produced by
    saas.bill_generator.generate_bill / tools.generate_billing_ledger's bill
    records: customer_id, period_start, period_end, segment, commodity,
    total_consumption_kwh, commodity_amount_gbp, non_commodity_amount_gbp,
    standing_charge_gbp, vat_gbp). Returns PASS with empty reasons, or HELD
    with every reason that fired (a bill can fail more than one check)."""
    reasons: list[str] = []
    segment = bill.get("segment", "resi")
    commodity = bill.get("commodity", "electricity")

    # F6_rebuild (INVARIANT_LIBRARY_REDTEAM.md gaps 2-4): the three structural
    # sanity controls any real biller has, enforced as class invariants in
    # domain_invariants.py -- arithmetic footing (total foots to its own
    # components, catch-up adjustment included), sign non-negativity, and
    # temporal sanity (start <= end, REJECTED not silently clamped). Each HOLDS
    # the bill (Tier-1) rather than issuing an absurd artefact; each fails
    # CLOSED on missing/malformed input. Additive and side-effect-free: they add
    # HELD reasons only, never touch any bill-amount computation, so the
    # margin-bridge residual and ledger P&L are untouched (the footing check
    # includes catchup_adjustment_gbp precisely so no legitimate catch-up bill
    # is wrongly HELD -- the regression that sank the first F6 build).
    if not check_bill_foots(bill):
        reasons.append(
            f"slc_6_7_billing_accuracy: declared total GBP "
            f"{bill.get('total_amount_gbp')} does not foot to the sum of its "
            f"components (commodity + non-commodity + standing charge + VAT + "
            f"catch-up adjustment) -- HELD"
        )
    if not check_bill_line_items_non_negative(bill):
        reasons.append(
            "slc_6_7_billing_accuracy: a bill line item is negative "
            "(commodity/non-commodity/standing charge/VAT) on a non-credit "
            "bill -- an absurd charge, HELD"
        )
    if not check_bill_period_sane(bill):
        reasons.append(
            f"slc_6_7_billing_accuracy: bill period is temporally impossible or "
            f"unreadable (period_start={bill.get('period_start')!r}, "
            f"period_end={bill.get('period_end')!r} -- start after end, an "
            f"absurdly long single-period span, or missing/malformed) -- "
            f"REJECTED not clamped, HELD"
        )

    # FAIL-OPEN FIX (2026-07-13, CONTROLS_THAT_CANNOT_FAIL.md): _actual_vat_rate()
    # returns None whenever the subtotal is <= 0, which PREVIOUSLY caused BOTH VAT
    # checks below to be silently skipped -- a bill with a zero/negative subtotal
    # sailed through the Tier-1 gate with no VAT validation at all (the exact
    # "passes when data is missing/zero/malformed" killer pattern). A genuinely
    # empty bill (zero subtotal AND zero VAT) is legitimate and still passes; but
    # a negative subtotal is absurd, and any VAT charged on a non-positive subtotal
    # is VAT on nothing -- both now fail CLOSED (HELD) instead of skipping the gate.
    subtotal = _bill_subtotal(bill)
    vat_gbp = bill.get("vat_gbp", 0.0)
    # A catch-up OVERCHARGE correction produces a legitimate CREDIT bill whose
    # subtotal (and VAT) are genuinely negative -- a refund, not an absurdity
    # (D3_catchup_rebilling; test_d3_credit_invoice_has_no_fabricated_payment).
    # The 2026-07-13 fail-open fix wrongly held ALL negative subtotals; that
    # over-fired on legitimate credits and jammed the publish pipeline. Exempt
    # the credit, but do NOT skip its VAT validation (that would re-open the
    # fail-open): validate the rate on magnitudes, which is sign-invariant since
    # a credit's VAT and subtotal share sign. Other credit-note types would
    # extend this same positive-indicator exemption, never a blanket negative pass.
    is_credit = is_credit_bill(bill)
    if subtotal < 0 and not is_credit:
        reasons.append(
            f"slc_6_7_billing_accuracy: bill subtotal GBP {subtotal:.2f} is negative "
            f"(commodity + non-commodity + standing charge) -- an absurd bill, HELD"
        )
    elif subtotal < 0 and is_credit:
        credit_rate = vat_gbp / subtotal  # both negative -> positive effective VAT rate
        if not check_vat(segment, credit_rate):
            reasons.append(
                f"vat_by_segment: credit bill effective VAT rate {credit_rate:.4f} is "
                f"inconsistent with segment={segment!r} -- HELD"
            )
    elif subtotal <= 0 and abs(vat_gbp) > 0.005:
        reasons.append(
            f"vat_by_segment: VAT of GBP {vat_gbp:.2f} charged on a non-positive "
            f"subtotal GBP {subtotal:.2f} -- VAT on nothing, cannot be validated, HELD"
        )

    actual_vat = _actual_vat_rate(bill)
    if actual_vat is not None and not check_vat(segment, actual_vat):
        reasons.append(
            f"vat_by_segment: segment={segment!r} implies a different VAT rate than "
            f"the {actual_vat:.4f} applied on this bill"
        )

    # INVARIANT_LIBRARY_REDTEAM.md C1 (2026-07-13, R10 C6 class): the arithmetic
    # check_vat() above is a tautology against this pipeline -- VAT is derived
    # from `segment` and re-derived from `segment`, so it can never catch a
    # MISLABEL where the declared segment itself is wrong. This independent
    # cross-check re-bases the expected rate on the metered load (a signal
    # independent of the label): an I&C-scale consumption billed at the domestic
    # 5% rate is the SME-as-Household undercharge and is HELD. One-directional by
    # honest design (see check_vat_consistent_with_consumption docstring) -- it
    # never flags a business rate on domestic-scale consumption, because a
    # genuine microbusiness looks identical there.
    if actual_vat is not None:
        vat_kwh = bill.get("total_consumption_kwh", 0.0)
        vat_days = _days_in_period(bill)
        if not check_vat_consistent_with_consumption(
            segment, commodity, actual_vat, vat_kwh, vat_days
        ):
            implied = consumption_implied_vat_rate(commodity, vat_kwh, vat_days)
            reasons.append(
                f"vat_by_segment: declared segment={segment!r} (VAT {actual_vat:.4f} "
                f"applied) is contradicted by a metered load of {vat_kwh:.1f} kWh over "
                f"{vat_days:.0f} days -- consumption independent of the label implies a "
                f"non-domestic {implied:.2f} rate, so this looks like an "
                f"SME-as-Household mislabel"
            )

    if segment == "resi":
        days = _days_in_period(bill)
        kwh = bill.get("total_consumption_kwh", 0.0)
        if not check_resi_bill_consumption_plausible(commodity, kwh, days):
            reasons.append(
                f"slc_6_7_billing_accuracy: {kwh:.1f} kWh over {days:.0f} days is implausible "
                f"for a resi {commodity} account"
            )

    # ADVISOR_STEER_BACKBILLING_GATE.md item 1(c): a catch-up bill breaching
    # the SLC 21BA 12-month window with no recorded fault attribution must be
    # HELD unless the excess has genuinely been written off (not silently
    # charged in full).
    if not check_back_billing_cap_respected(bill):
        reasons.append(
            "slc_21ba_back_billing_cap: catch-up bill breaches the 12-month "
            "recovery window with no recorded fault attribution but the "
            "written-off amount does not match what the cap requires "
            "(missing/malformed data, insufficient, or over-stated)"
        )

    outcome = ValidationOutcome.HELD if reasons else ValidationOutcome.PASS
    return BillValidationResult(
        customer_id=bill.get("customer_id", ""),
        period_end=bill.get("period_end", ""),
        outcome=outcome,
        reasons=reasons,
    )


def check_reads_reconcile(
    opening_read_kwh: float | None,
    closing_read_kwh: float | None,
    billed_consumption_kwh: float | None,
) -> bool:
    """A rendered bill's usage line must equal the printed closing meter read
    minus the printed opening read, at the displayed (1dp) precision.

    ADVISOR_STEER_BILL_ARITHMETIC.md Defect 1 (2026-07-11), R10 class fix:
    a real UK bill's billed quantity is always `closing_read - opening_read`
    computed from the PRINTED (rounded) reads, never a separately-rounded raw
    figure. Compounding the independent rounding of three related numbers
    (opening, closing, raw usage) is exactly what produced the director's
    observed 331.1-vs-331.2 kWh mismatch. Returns True (not applicable) for a
    bill that carries no meter reads."""
    if opening_read_kwh is None or closing_read_kwh is None or billed_consumption_kwh is None:
        return True
    reads_delta = round(round(closing_read_kwh, 1) - round(opening_read_kwh, 1), 1)
    return abs(reads_delta - round(billed_consumption_kwh, 1)) <= 0.05


def validate_rendered_bill_reads(inv: dict) -> list:
    """Reads-reconciliation reason(s) for one rendered invoice dict
    (opening_read_kwh, closing_read_kwh, consumption_kwh). Empty list == the
    bill's usage line reconciles with its printed reads. A non-empty list is
    a Tier-1 billing-accuracy failure -- the caller HOLDS the bill to the
    exception queue rather than issuing it (same zero-tolerance treatment as
    validate_bill's VAT/consumption checks, but this one runs AFTER the
    opening/closing register reads have been computed for the bill)."""
    reasons: list[str] = []
    opening = inv.get("opening_read_kwh")
    closing = inv.get("closing_read_kwh")
    billed = inv.get("consumption_kwh")
    if not check_reads_reconcile(opening, closing, billed):
        reads_delta = round(round(closing, 1) - round(opening, 1), 1)
        reasons.append(
            "slc_6_7_billing_accuracy: billed usage %.1f kWh does not reconcile with the "
            "printed meter reads %.1f -> %.1f (closing - opening = %.1f kWh)"
            % (billed, opening, closing, reads_delta)
        )
    return reasons


def validate_bills(bills: list) -> tuple[list, list[BillValidationResult]]:
    """Partition `bills` into (passing, held) -- passing bills proceed to
    normal issuance unchanged; held bills are the exception queue, keyed by
    (customer_id, period_end) so a caller can look up why any given bill
    didn't issue this cycle."""
    passing = []
    exception_queue: list[BillValidationResult] = []
    for bill in bills:
        result = validate_bill(bill)
        if result.held:
            exception_queue.append(result)
        else:
            passing.append(bill)
    return passing, exception_queue


def exception_queue_as_dicts(exception_queue: list[BillValidationResult]) -> list[dict]:
    """JSON-serialisable form for the ledger output -- the exception queue as
    a real operational surface, not just an internal Python structure."""
    return [
        {
            "customer_id": r.customer_id,
            "period_end": r.period_end,
            "reasons": r.reasons,
        }
        for r in exception_queue
    ]
