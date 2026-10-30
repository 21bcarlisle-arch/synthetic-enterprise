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

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum

from company.billing.back_billing import BackBillingAssessment, BackBillingReason
from company.compliance.domain_invariants import (
    _FOOTING_COMPONENT_KEYS,
    check_back_billing_cap_respected,
    check_bill_foots,
    check_bill_line_items_non_negative,
    check_bill_period_sane,
    check_printed_bill_foots_exactly,
    check_resi_bill_consumption_plausible,
    check_vat,
    check_vat_consistent_with_consumption,
    consumption_implied_vat_rate,
    is_credit_bill,
)
from saas.bill_generator import CHARGED_AT_THE_METER


class ValidationOutcome(str, Enum):
    PASS = "pass"
    HELD = "held"
    #: Held on consumption scale alone, then confirmed a domestic dwelling on an actual read and
    #: issued -- see `release_confirmed_domestic`. The hold's reasons stay on the result.
    RELEASED = "released_confirmed_domestic"
    #: Held on consumption scale alone in a closed account's closing run, and issued with its
    #: final bill on the closing read -- see `release_at_closing_read`.
    RELEASED_AT_CLOSURE = "released_on_the_final_bill"
    #: Held on consumption scale alone, an estimate on a confirmed dwelling at a daily rate this
    #: account's own meter had already measured -- see `release_on_measured_rate`.
    RELEASED_ON_MEASURED_RATE = "released_on_the_meters_measured_rate"


@dataclass(frozen=True)
class BillValidationResult:
    customer_id: str
    period_end: str
    outcome: ValidationOutcome
    reasons: list = field(default_factory=list)  # empty when PASS
    #: True when EVERY reason is one of the two consumption-scale checks, the only holds a
    #: domestic confirmation can answer. A footing, sign, period, VAT-arithmetic or back-billing
    #: reason alongside them makes this False, and the bill stays held whatever the premise is.
    consumption_scale_only: bool = False

    @property
    def held(self) -> bool:
        return self.outcome == ValidationOutcome.HELD


def _days_in_period(bill: dict) -> float:
    from datetime import date
    start = date.fromisoformat(bill["period_start"])
    end = date.fromisoformat(bill["period_end"])
    return max((end - start).days + 1, 1)


def _bill_subtotal(bill: dict) -> float:
    """The month's own charges before VAT: what the rate check grades its VAT against."""
    return (
        bill.get("commodity_amount_gbp", 0.0)
        + bill.get("non_commodity_amount_gbp", 0.0)
        + bill.get("standing_charge_gbp", 0.0)
    )


def _own_vat(bill: dict) -> float:
    """The month's own VAT: the VAT line less a catch-up's VAT (`catchup_vat_gbp`).

    The catch-up's VAT is each corrected month's VAT at that month's own rate, summed and rounded
    (back_billing_and_liability.md section 15), so over the catch-up line it is not one rate: a
    run across a rate change or a de minimis line, or pennies on a small run, read 0.0494 or -0.2773.
    Graded on the whole line, the check held 38 legitimate catch-up bills on a two-year run, and a
    held final credit bill is a credit never given or refunded. The month's own VAT is what one
    rate must explain; the catch-up's is held by its own construction and test."""
    return bill.get("vat_gbp", 0.0) - (bill.get("catchup_vat_gbp") or 0.0)


def _actual_vat_rate(bill: dict) -> float | None:
    subtotal = _bill_subtotal(bill)
    if subtotal <= 0:
        return None
    return _own_vat(bill) / subtotal


def _vat_volume(bill: dict, commodity: str) -> dict:
    return {"commodity": commodity, "kwh": bill.get("total_consumption_kwh", 0.0),
            "days": _days_in_period(bill)}


def validate_bill(bill: dict) -> BillValidationResult:
    """Run every Tier-1 check against one bill dict (the shape produced by
    saas.bill_generator.generate_bill / tools.generate_billing_ledger's bill
    records: customer_id, period_start, period_end, segment, commodity,
    total_consumption_kwh, commodity_amount_gbp, non_commodity_amount_gbp,
    standing_charge_gbp, vat_gbp). Returns PASS with empty reasons, or HELD
    with every reason that fired (a bill can fail more than one check)."""
    reasons: list[str] = []
    scale_reasons = 0
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
    vat_gbp = _own_vat(bill)
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
        if not check_vat(segment, credit_rate, **_vat_volume(bill, commodity)):
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
    if actual_vat is not None and not check_vat(segment, actual_vat, **_vat_volume(bill, commodity)):
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
            scale_reasons += 1
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
            scale_reasons += 1
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
        consumption_scale_only=bool(reasons) and scale_reasons == len(reasons),
    )


def check_reads_reconcile(
    opening_read_kwh: float | None,
    closing_read_kwh: float | None,
    billed_consumption_kwh: float | None,
    catchup_kwh: float | None = None,
) -> bool:
    """A rendered bill's usage line must equal the printed closing meter read
    minus the printed opening read, at the displayed (1dp) precision.

    ADVISOR_STEER_BILL_ARITHMETIC.md Defect 1 (2026-07-11), R10 class fix:
    a real UK bill's billed quantity is always `closing_read - opening_read`
    computed from the PRINTED (rounded) reads, never a separately-rounded raw
    figure. Compounding the independent rounding of three related numbers
    (opening, closing, raw usage) is exactly what produced the director's
    observed 331.1-vs-331.2 kWh mismatch. Returns True (not applicable) for a
    bill that carries no meter reads.

    An actual bill after an estimated run opens on the last estimated reading, so its reads also
    span the catch-up line's kWh (back_billing_and_liability.md §13): usage + catch-up = advance."""
    if opening_read_kwh is None or closing_read_kwh is None or billed_consumption_kwh is None:
        return True
    reads_delta = round(round(closing_read_kwh, 1) - round(opening_read_kwh, 1), 1)
    billed = round(billed_consumption_kwh, 1) + round(catchup_kwh or 0.0, 1)
    return abs(reads_delta - billed) <= 0.05


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
    catchup = inv.get("catchup_kwh")
    if not check_reads_reconcile(opening, closing, billed, catchup):
        reads_delta = round(round(closing, 1) - round(opening, 1), 1)
        reasons.append(
            "slc_6_7_billing_accuracy: billed usage %.1f kWh (catch-up %.1f kWh) does not "
            "reconcile with the printed meter reads %.1f -> %.1f (closing - opening = %.1f kWh)"
            % (billed, catchup or 0.0, opening, closing, reads_delta)
        )
    return reasons


def validate_rendered_bill_money(inv: dict) -> list:
    """Money-reconciliation reason(s) for one rendered invoice dict. Empty list
    == the printed line items sum exactly to the printed total.

    The money twin of `validate_rendered_bill_reads`, and deliberately the same
    shape: both check the RENDERED bill (after the print-boundary rounding),
    both are zero-tolerance, and both HOLD to the exception queue rather than
    issuing a bill whose own arithmetic a customer can refute.

    D_money_boundary_reconciliation (2026-08-03): before the boundary fix,
    534/1603 printed invoices (33.3%) would have been held by this check.
    After it, this is a standing guard -- it should never fire in normal
    operation, and if it does, a new independent-rounding site has been
    reintroduced somewhere between the computed bill and the printed one.
    """
    reasons: list[str] = []
    if not check_printed_bill_foots_exactly(inv):
        printed = {
            k: inv.get(k) for k in _FOOTING_COMPONENT_KEYS
            if k in inv and inv.get(k) is not None
        }
        shown = " + ".join(f"{k}={v}" for k, v in printed.items()) or "(no printed line items)"
        reasons.append(
            "slc_6_7_billing_accuracy: printed line items do not sum exactly to the "
            "printed total %s -- %s" % (inv.get("total_amount_gbp"), shown)
        )
    return reasons


def release_confirmed_domestic(bill: dict, result: BillValidationResult) -> dict | None:
    """The exception queue's answer to a domestic ceiling hold: the bill to issue, or None.

    THE TWO CEILING CHECKS CATCH TWO DIFFERENT DEFECTS, and a release has to answer both.
    (1) A business premise labelled domestic -- the C6 class, and the reason the implied-VAT check
    exists. A supplier answers that by looking the supply address up on the council tax list
    (HMRC, formerly VOA; public), which is also the population DESNZ NEED counts as domestic. A
    listed dwelling supplied for domestic use takes 5% VAT at any volume -- the de minimis is a
    business-use rule -- so a listing refutes the mislabel outright. (2) A wrong VOLUME -- the five
    2025-06 stub estimates this gate held were a month's estimate on seven days, on listed
    dwellings. A listing says nothing about that, so only a bill on an ACTUAL read is released: the
    meter measured it. An estimate over the ceiling stays held until an actual read replaces it.

    No threshold is introduced. The released bill is a copy carrying `pre_bill_release`, so what
    was held and why it issued is on the bill itself; the input is never mutated.

    Why this and not a higher ceiling: DESNZ NEED 2026 retains domestic electricity only to
    25,000 kWh/yr and 0.34% of all domestic properties -- 5.9% of non-gas pre-1930 detached
    151-200 m2 -- are above even that (docs/market_research/need_domestic_electricity_high_tail.md).
    Volume cannot say where domestic ends; the premise record can.

    A prepayment statement answers the volume half as an actual read does: the meter charged what it
    recorded as used, and the customer has paid it (what_a_prepayment_customer_is_sent_2026-10-26.md,
    choice 6).
    """
    if not (result.held and result.consumption_scale_only):
        return None
    if bill.get("segment", "resi") != "resi":
        return None
    if bill.get("premise_council_tax_listed") is not True:
        return None
    basis = bill.get("billing_basis")
    if basis not in ("actual", CHARGED_AT_THE_METER):
        return None
    released = dict(bill)
    released["pre_bill_release"] = {
        "outcome": ValidationOutcome.RELEASED.value,
        "held_for": list(result.reasons),
        "confirmed_by": "supply address on the council tax list; " + (
            "bill on an actual read" if basis == "actual" else "charged at the prepayment meter"),
    }
    return released


def measured_daily_rates(own_bills: list) -> list[tuple[str, float]]:
    """(period_end, kWh a day) of each actual-read bill in one account's `own_bills`, read to read.

    The energy is the bill's own kWh plus what its catch-up reconciled for the estimated run before
    it (billed and true-up): together, the register's advance since the previous read. The days run
    from the previous actual-read bill's period end, or the account's first bill, to this one's."""
    rates: list[tuple[str, float]] = []
    start = None
    for bill in sorted(own_bills, key=lambda b: b["period_end"]):
        if start is None:
            start = dt.date.fromisoformat(bill["period_start"])
        if bill.get("billing_basis") != "actual":
            continue
        end = dt.date.fromisoformat(bill["period_end"])
        kwh = (bill.get("total_consumption_kwh", 0.0) + (bill.get("read_true_up_billed_kwh") or 0.0)
               + (bill.get("read_true_up_kwh") or 0.0))
        rates.append((bill["period_end"], kwh / max((end - start).days + 1, 1)))
        start = end + dt.timedelta(days=1)
    return rates


def release_on_measured_rate(
    bill: dict, result: BillValidationResult, own_bills: list,
) -> dict | None:
    """A domestic ceiling hold on an estimate the account's own meter has already measured: the
    bill to issue, or None. `own_bills` is the account's bills; only actual reads before this bill
    are read, so the supplier knew the rate when it billed.

    The listing answers the mislabel half of the ceiling, as in `release_confirmed_domestic`. The
    volume half asks whether the estimate is wrong in scale. An earlier read-to-read rate at the same
    meter at least as high as the estimate's says it is not, and holding it only defers the energy to
    one late catch-up: PROS-2017-0336 went 14 months unbilled (SLC 21B.5 asks a bill twice a year).
    An estimate above every rate measured, or before any read, stays held. No threshold is
    introduced. Rules and choices: docs/market_research/unbilled_energy_and_revenue_assurance.md §4d.
    The assembly's catch-up asks this same function, so a released estimate is reconciled as billed.
    """
    if not (result.held and result.consumption_scale_only):
        return None
    if bill.get("segment", "resi") != "resi":
        return None
    if bill.get("premise_council_tax_listed") is not True:
        return None
    if bill.get("billing_basis") != "estimated":
        return None
    prior = [rate for end, rate in measured_daily_rates(own_bills) if end < bill["period_end"]]
    if not prior:
        return None
    measured = max(prior)
    if bill.get("total_consumption_kwh", 0.0) / _days_in_period(bill) > measured:
        return None
    released = dict(bill)
    released["pre_bill_release"] = {
        "outcome": ValidationOutcome.RELEASED_ON_MEASURED_RATE.value,
        "held_for": list(result.reasons),
        "confirmed_by": ("supply address on the council tax list; estimate at or under a daily rate "
                         "this meter's own earlier reads measured"),
        "measured_kwh_per_day": measured,
    }
    return released


def _closing_runs(bills: list) -> dict[tuple[str, str], tuple[dict, dict]]:
    """(customer_id, period_end) of each bill in a closed account's closing run -> (the bill, its
    final bill).

    The closing run is the estimated bills after the account's last actual read, through its final
    bill (`final_bill`, stamped by `monthly_bill_assembly.build_monthly_bills`). A final bill on an
    actual read is that last read, so its run is empty: its catch-up carries the energy."""
    by_customer: dict[str, list[dict]] = {}
    for bill in bills:
        by_customer.setdefault(bill.get("customer_id", ""), []).append(bill)
    runs: dict[tuple[str, str], tuple[dict, dict]] = {}
    for customer_id, own in by_customer.items():
        final = next((b for b in own if b.get("final_bill")), None)
        if final is None:
            continue
        last_read = max(
            (b["period_end"] for b in own if b.get("billing_basis") == "actual"), default="")
        for b in own:
            if (b.get("billing_basis") == "estimated"
                    and last_read < b["period_end"] <= final["period_end"]):
                runs[(customer_id, b["period_end"])] = (b, final)
    return runs


def release_at_closing_read(
    bill: dict, result: BillValidationResult, final_bill: dict,
) -> dict | None:
    """A domestic ceiling hold in a closed account's closing run: the bill to issue on the final
    bill, or None. `final_bill` is the account's final bill, whose closing run this bill is in.

    The volume half of the ceiling waits for an actual read, and after closure none reaches this
    supplier: the meter's next read is the gaining supplier's. The closing read is the one the
    losing supplier is settled on, and it moves only by dispute, so billing it is billing what the
    supplier is charged for. The mislabel half still needs the listing, as `release_confirmed_domestic`
    does. A held interim goes out on the final bill (SLC 27.17), so its billing date is the final
    bill's, and SLC 21BA bars it if any part of it is over 12 months before that: it stays held.
    Rules and choices: docs/market_research/unbilled_energy_and_revenue_assurance.md, K6, "A held
    bill on an account that closes".
    """
    if not (result.held and result.consumption_scale_only):
        return None
    if bill.get("segment", "resi") != "resi":
        return None
    if bill.get("premise_council_tax_listed") is not True:
        return None
    barred = BackBillingAssessment(
        account_id=bill.get("customer_id", ""),
        billing_date=dt.date.fromisoformat(final_bill["period_end"]),
        consumption_period_start=dt.date.fromisoformat(bill["period_start"]),
        consumption_period_end=dt.date.fromisoformat(bill["period_end"]),
        billed_amount_gbp=bill.get("total_amount_gbp", 0.0),
        reason=BackBillingReason.SUPPLIER_ERROR,
    ).cap_applies
    if barred:
        return None
    released = dict(bill)
    released["pre_bill_release"] = {
        "outcome": ValidationOutcome.RELEASED_AT_CLOSURE.value,
        "held_for": list(result.reasons),
        "confirmed_by": ("supply address on the council tax list; account closed, billed to its "
                         "closing read, the read the losing supplier is settled on"),
        "issued_with_final_bill": final_bill["period_end"],
    }
    return released


def issued_with_final_bill(bills: list) -> dict[tuple[str, str], str]:
    """(customer_id, period_end) of each held bill `validate_bills` issues on a final bill -> that
    final bill's period end. Until then the bill was not issued, which is what the unbilled accrual
    asks. Only closing-run bills are validated, so this is cheap to ask at every month end."""
    late = {}
    by_customer = _by_customer(bills)
    for key, (bill, final) in _closing_runs(bills).items():
        result = validate_bill(bill)
        if release_on_measured_rate(bill, result, by_customer[key[0]]) is not None:
            continue
        if release_at_closing_read(bill, result, final) is not None:
            late[key] = final["period_end"]
    return late


def _by_customer(bills: list) -> dict[str, list[dict]]:
    by_customer: dict[str, list[dict]] = {}
    for bill in bills:
        by_customer.setdefault(bill.get("customer_id", ""), []).append(bill)
    return by_customer


def validate_bills(bills: list) -> tuple[list, list[BillValidationResult]]:
    """Partition `bills` into (passing, held) -- passing bills proceed to
    normal issuance unchanged; held bills are the exception queue, keyed by
    (customer_id, period_end) so a caller can look up why any given bill
    didn't issue this cycle. A consumption-scale hold the queue confirms
    domestic (`release_confirmed_domestic`) issues, as a marked copy, and so does an estimate at a
    rate the meter measured (`release_on_measured_rate`) and one in a closed account's closing run
    (`release_at_closing_read`), on its final bill."""
    passing = []
    exception_queue: list[BillValidationResult] = []
    closing = _closing_runs(bills)
    by_customer = _by_customer(bills)
    for bill in bills:
        result = validate_bill(bill)
        if result.held:
            released = release_confirmed_domestic(bill, result)
            if released is None:
                released = release_on_measured_rate(
                    bill, result, by_customer[bill.get("customer_id", "")])
            run = closing.get((bill.get("customer_id", ""), bill.get("period_end", "")))
            if released is None and run is not None:
                released = release_at_closing_read(bill, result, run[1])
            if released is not None:
                passing.append(released)
            else:
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
