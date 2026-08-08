"""Phase PP -- Per-Customer Invoice & Payment Ledger.

Reads bills and per_customer_behavioral from run_output_latest.json and generates
a per-customer billing ledger with invoice records, payment events, and arrears cases.

Payment outcome driven by income_stress_trajectory from behavioral data:
  LOW    -> 92% on-time, 3% DD failure
  MODERATE -> 50% on-time, 12% DD failure
  HIGH   -> 10% on-time, 35% DD failure

Payment method by segment:
  I&C     -> CHAPS (>10k) or BACS
  SME     -> BACS or DD
  Resi    -> DD (default)

Output: site/state/billing_ledger.json
"""
from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

from simulation.arrears_engine import (
    PAYMENT_TERMS_DAYS,
    bill_substream as _bill_substream,
    stress_for_year as _stress_for_year,
    payment_method as _payment_method,
    payment_outcome as _payment_outcome,
    _fuel_poor_for_bill,
    _tone_for_bill,
    arrears_stages as _arrears_stages,
    ic_arrears_stages as _ic_arrears_stages,
    debt_archetype as _debt_archetype,
    _CORP_BACS_ON_TIME_PROB,
    _CORP_BACS_LATE_PROB,
    _CORP_BACS_DISPUTE_PROB,
    _CORP_LATE_DAYS,
    _DD_FAILURE_PROB,
    _ON_TIME_PROB,
    _LATE_DAYS,
)
from company.billing.pre_bill_validation import (
    validate_bills,
    exception_queue_as_dicts,
    validate_rendered_bill_reads,
    validate_rendered_bill_money,
    BillValidationResult,
    ValidationOutcome,
)
from saas.money import (
    MoneyBoundaryError,
    display_rate_gbp_per_day,
    display_rate_p_per_kwh,
    foot_components_to_total,
)

PROJECT = Path(__file__).parent.parent
RUN_JSON = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "state" / "billing_ledger.json"


def _printed_unit_rate(printed_consumption_kwh, printed_commodity_amount_gbp):
    """The p/kWh rate to print on the usage line, or None if none reproduces it.

    None is the honest outcome for a zero-consumption bill and for a line no
    printable rate can express; the portal renders the amount without a rate.
    """
    if not printed_consumption_kwh:
        return None
    rate = display_rate_p_per_kwh(
        printed_consumption_kwh, printed_commodity_amount_gbp
    )
    return None if rate is None else rate[0]


def _printed_daily_rate(days_in_period, printed_standing_charge_gbp):
    """The GBP/day rate to print, or None if the line cannot carry one.

    Deliberately fitted against the PRINTED standing charge rather than the
    bill's raw one, because the printed pair is what the customer multiplies.

    A bill with no day count returns None rather than raising: that line simply
    prints no per-day rate, which claims nothing and so cannot be unreproducible.
    A rate printed WITHOUT its day count is the real defect, and that is caught
    on the other side by `check_printed_line_rederives`, which fails closed on it.
    """
    if days_in_period is None:
        return None
    rate = display_rate_gbp_per_day(days_in_period, printed_standing_charge_gbp)
    return None if rate is None else rate[0]


# BILL_CORRECTNESS_ADDENDUM.md Defect 2 (2026-07-09): every bill must state
# meter serial + MPAN/MPRN. Same deterministic-from-account-id scheme as
# company/crm/customer_registry.py's _mpan()/_mprn() (duplicated rather than
# imported -- that module pulls in sqlite3 for its registry DB, which this
# JSON-only pipeline script has no other reason to depend on; kept
# byte-for-byte identical so the two would agree if that registry is ever
# wired into the real run pipeline).
def _mpan(account_id: str) -> str:
    """Synthetic MPAN (Meter Point Administration Number) -- 13 digits."""
    seed = sum(ord(c) for c in account_id)
    return f"1{seed:012d}"[:13]


def _mprn(account_id: str) -> str:
    """Synthetic MPRN (Meter Point Reference Number) -- 10 digits."""
    seed = sum(ord(c) * 17 for c in account_id)
    return f"{seed:010d}"[:10]


def _meter_serial(account_id: str, commodity: str) -> str:
    """Synthetic meter serial number, deterministic per account+commodity
    (an account with both fuels gets two distinct serials, matching two
    physical meters)."""
    seed = sum(ord(c) * 31 for c in account_id + commodity)
    return f"M{seed % 100000000:08d}"

# Phase 3 (CORE_FIDELITY_PHASES.md item 3, unhappy-path audit finding #2):
# "issue_date = period_end -- the bill is issued the same calendar day the
# billing period ends, with no generation or postal delay and zero chance
# of a late bill." Real supplier billing runs process a batch some days
# after period-end before a bill is issued (paperless/portal delivery is
# then near-instant, so the delay is dominated by the internal generation
# run, not post). Provisional distribution pending a dedicated discovery-
# agent anchor (no DESNZ/Ofgem billing-cycle-latency benchmark registered
# yet in docs/market_research/ASSUMPTIONS.md) -- a small mean with an
# occasional longer tail (batch-run slippage / a postal fallback for the
# minority of customers not on paperless billing).
BILL_GENERATION_DELAY_MEAN_DAYS = 3.0


def _bill_generation_delay_days(customer_id: str, period_end: str) -> int:
    delay_rng = random.Random(f"billgen_{customer_id}_{period_end}")
    return max(0, round(delay_rng.expovariate(1.0 / BILL_GENERATION_DELAY_MEAN_DAYS)))


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = RUN_JSON
    if out_path is None:
        out_path = OUT_PATH
    data = json.loads(Path(run_json_path).read_text())

    bills = data.get("bills", [])
    behavioral = data.get("per_customer_behavioral", {})
    churned = set(data.get("churned_billing_accounts", []))

    # DOMAIN_SENSE_AND_COMPLIANCE.md Phase 3: Tier-1 pre-bill validation gate
    # (director's Principle 1 -- 100% of bills validated before issue, zero
    # tolerance). A held bill is excluded from this cycle's normal issuance
    # entirely (never sent) and recorded on the exception queue below rather
    # than silently dropped.
    bills, held_bills = validate_bills(bills)

    # BILL_CORRECTNESS_ADDENDUM.md Defect 2: meter-read status (A=actual,
    # E=estimated) per bill, from Phase 3's real estimation physics
    # (simulation/meter_reads.py), keyed the same way the bills themselves
    # are (customer_id, period_end).
    read_by_key: dict[tuple[str, str], dict] = {}
    for read in data.get("meter_read_log", []):
        read_by_key[(read["customer_id"], read["period_end"])] = read

    # Running cumulative meter register value per (customer_id, commodity) --
    # opening read for a bill is the previous bill's closing read (0.0 for
    # the account's first bill on that meter). An estimated period advances
    # the register by the ESTIMATED consumption, not the true value, exactly
    # modelling what the physical meter/estimate would actually show until
    # the next actual read corrects it.
    running_closing_read: dict[tuple[str, str], float] = {}

    if not bills:
        result = {
            "meta": {"note": "No bill data -- re-run simulation with Phase PP extract_report_data",
                     "invoice_count": 0, "customer_count": 0},
            "customers": {},
            "exception_queue": exception_queue_as_dicts(held_bills),
        }
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(result, indent=2))
        return result

    # C-S2 (W2_16): each bill's payment outcome is drawn from its OWN named
    # substream, keyed by (customer_id, period_end) -- see
    # `arrears_engine.bill_substream`. This function does NOT visit the same
    # bills as `compute_emergent_bad_debt`: it excludes held bills (the
    # validation gate above) and skips the outcome draw entirely for credit
    # invoices. Under the previous single shared `random.Random(42)` those two
    # legitimate differences silently offset this stream from the P&L's,
    # disagreeing on the failed/dispute decision for 42 of 1557 real bills.
    # Per-bill substreams make the two agree without either having to iterate
    # in lockstep with the other.
    _outcome_seed = 42
    held_reads: list[BillValidationResult] = []
    held_money: list[BillValidationResult] = []
    invoices_by_cid = {}
    payments_by_cid = {}
    arrears_by_cid = {}
    segment_by_cid = {}
    invoice_number = 1

    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        segment_by_cid.setdefault(cid, segment)
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        commodity = bill.get("commodity", "electricity")
        year = int(period_end[:4])

        generation_delay_days = _bill_generation_delay_days(cid, period_end)
        issue_date = date.fromisoformat(period_end) + timedelta(days=generation_delay_days)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)

        beh = behavioral.get(cid) or {}
        stress = _stress_for_year(beh, year)
        # D3 step 2: a catch-up overcharge credit can make `amount` <= 0 (the
        # customer is owed money, not billed). Real suppliers carry that as
        # an account credit, not a collected payment -- there is no DD/BACS/
        # CHAPS "collection" of a negative amount to simulate. Route straight
        # to a settled/no-collection outcome rather than feeding a negative
        # figure through the payment-method/outcome model, which assumes a
        # positive amount owed (found while reading a real instance: a credit
        # invoice was otherwise rendered as a "successful direct_debit
        # payment" of a negative sum, which is not a real event).
        is_credit = amount <= 0
        if is_credit:
            method = None
            _tone = None
            outcome, days_late = "success", 0
        else:
            method = _payment_method(segment, amount, cid, commodity)
            _tone = _tone_for_bill(method, cid, period_end)
            outcome, days_late = _payment_outcome(
                method, stress, _bill_substream(_outcome_seed, cid, period_end, commodity),
                segment, _fuel_poor_for_bill(method, cid), _tone, cid,
            )

        # Defect 2: meter-read status, opening/closing reads, meter serial,
        # MPAN/MPRN. read_event is None for a bill Phase 3's meter-read
        # simulation doesn't cover (e.g. a run predating that data) --
        # falls back to "actual" at the bill's own consumption figure
        # rather than omitting the fields.
        read_event = read_by_key.get((cid, period_end))
        if read_event is not None and read_event["status"] == "estimated":
            read_type = "E"
            register_consumption_kwh = read_event["estimated_consumption_kwh"]
        else:
            read_type = "A"
            register_consumption_kwh = bill.get("total_consumption_kwh", 0)
        read_key = (cid, commodity)
        opening_read_kwh = running_closing_read.get(read_key, 0.0)
        closing_read_kwh = opening_read_kwh + register_consumption_kwh
        running_closing_read[read_key] = closing_read_kwh

        # ADVISOR_STEER_BILL_ARITHMETIC.md Defect 1 (2026-07-11), R10 class fix:
        # the DISPLAYED billed usage is derived from the already-rounded
        # displayed reads, NOT an independent round() of the raw total -- so
        # `billed_kwh == closing_read - opening_read` holds exactly as printed,
        # by construction. (Previously opening/closing/usage were each rounded
        # independently from the same full-precision source, and compounding
        # those three roundings produced the director's observed 331.1-vs-331.2
        # kWh mismatch.) This also reconciles ESTIMATED bills on-screen (whose
        # register advances by the estimate): the usage line now equals the
        # printed estimated reads' difference. The residual noted here
        # previously (an estimated bill's commodity amount computed upstream
        # on TRUE consumption, diverging its derived unit rate from the
        # tariff) is CLOSED: D3 step 1 (docs/design/maturity_map.yaml
        # "Estimated billing & catch-up rebilling cycle") now prices
        # `bill["total_amount_gbp"]` on the estimate at the real tariff rate
        # before this module ever sees it -- no change needed here, `amount`
        # above already reads the corrected figure.
        opening_read_rounded = round(opening_read_kwh, 1)
        closing_read_rounded = round(closing_read_kwh, 1)
        displayed_consumption_kwh = round(closing_read_rounded - opening_read_rounded, 1)

        # D_money_boundary_reconciliation (2026-08-03, the [ACT] returned by
        # docs/design/MONEY_REPRESENTATION_EVIDENCE.md): the money analogue of
        # the reads fix immediately above, and the same class fix. Previously
        # each of the four money line items was round()ed independently here
        # and the total was round()ed independently AGAIN from the raw float,
        # so the printed column did not add up to the printed total on 534 of
        # 1603 invoices (33.3%) -- e.g. 94.50 + 34.15 + 8.36 + 6.85 printed
        # against a total of 143.88.
        #
        # Now the printed total is DERIVED from the printed line items via the
        # one declared money boundary (saas/money.py), so the invoice adds up
        # by construction, and no line item is fudged to absorb a residual --
        # every printed line is exactly the quantization of its own raw value.
        # The catch-up adjustment is a genuine FIFTH printed component on a
        # back-billing bill (it is added to the total outside the four category
        # fields), so it must be in this set or the derived total would drop
        # it -- that omission is what sank the first F6 build.
        money_components = {
            "commodity_amount_gbp": bill.get("commodity_amount_gbp", 0.0) or 0.0,
            "non_commodity_amount_gbp": bill.get("non_commodity_amount_gbp", 0.0) or 0.0,
            "standing_charge_gbp": bill.get("standing_charge_gbp", 0.0) or 0.0,
            "vat_gbp": bill.get("vat_gbp", 0.0) or 0.0,
        }
        if bill.get("catchup_applied") and bill.get("catchup_adjustment_gbp") is not None:
            money_components["catchup_adjustment_gbp"] = bill["catchup_adjustment_gbp"]
        try:
            printed_money, printed_total = foot_components_to_total(
                money_components, amount, label=f"{cid}/{period_end}"
            )
        except MoneyBoundaryError as exc:
            # A residual too large to be rounding means the declared total
            # contains money that is not in the printed component set. HOLD the
            # bill rather than print a total nobody can reconcile -- the same
            # treatment the reads check below gives its own failure, and the
            # opposite of falling back to the unreconciled figure (R15: that
            # fallback would be the fail-open).
            held_money.append(BillValidationResult(
                customer_id=cid, period_end=period_end,
                outcome=ValidationOutcome.HELD,
                reasons=["slc_6_7_billing_accuracy: %s" % exc],
            ))
            continue

        inv = {
            "invoice_number": invoice_number,
            "customer_id": cid,
            "period_start": bill["period_start"],
            "period_end": period_end,
            "commodity": commodity,
            "consumption_kwh": displayed_consumption_kwh,
            "commodity_amount_gbp": printed_money["commodity_amount_gbp"],
            # The printed usage rate is decided HERE, once, against the printed
            # pair -- not recomputed downstream by generate_invoice_data or in
            # the browser. Two independent derivations of the same printed
            # figure is how the display precision drifts apart again.
            "unit_rate_p_per_kwh": _printed_unit_rate(
                displayed_consumption_kwh, printed_money["commodity_amount_gbp"]
            ),
            "non_commodity_amount_gbp": printed_money["non_commodity_amount_gbp"],
            "standing_charge_gbp": printed_money["standing_charge_gbp"],
            "days_in_period": bill.get("days_in_period"),
            # D_printed_figure_rederivation (2026-08-03): the daily rate used
            # to be passed through RAW from the bill -- a full-precision
            # standing_charge/days quotient -- so the customer-facing artefact
            # printed binary-float residue (0.23983870967741938) on 324
            # invoices, and the rendered line "31 days x GBP 0.24/day" did not
            # multiply out to the standing charge printed beside it on 243.
            # The rate now comes from the money boundary at a display precision
            # that reproduces the PRINTED standing charge exactly. None when no
            # printable precision does: the bill then shows the charge without
            # a per-day rate rather than printing arithmetic that fails.
            "standing_charge_gbp_per_day": _printed_daily_rate(
                bill.get("days_in_period"), printed_money["standing_charge_gbp"]
            ),
            "vat_gbp": printed_money["vat_gbp"],
            "total_amount_gbp": printed_total,
            "issue_date": issue_date.isoformat(),
            "generation_delay_days": generation_delay_days,
            "due_date": due_date.isoformat(),
            # Expert-Hour finding, 2026-07-12: a credit invoice showing
            # "PAID" is confusing -- nothing was paid, the supplier owes the
            # customer. `is_credit` takes priority over the outcome-derived
            # label (outcome is forced to "success" for a credit, see above).
            "payment_status": (
                "credited" if is_credit else
                "disputed" if outcome == "dispute" else
                ("paid" if outcome == "success" else "overdue")
            ),
            "meter_serial": _meter_serial(cid, commodity),
            "mpan": _mpan(cid) if commodity == "electricity" else None,
            "mprn": _mprn(cid) if commodity == "gas" else None,
            "read_type": read_type,
            "opening_read_kwh": opening_read_rounded,
            "closing_read_kwh": closing_read_rounded,
        }
        # D3 step 2 (docs/design/maturity_map.yaml "Estimated billing &
        # catch-up rebilling cycle"): when a real read resolves a run of
        # estimated bills, the correction (capped per Ofgem SLC 31A where
        # it's an undercharge) is already folded into `amount` above --
        # these fields make the WHY visible on the customer-facing invoice
        # rather than a silent total change. Omitted (None) on every bill
        # that isn't itself the resolving bill, matching the bill dict's own
        # additive-only convention (bill.get() with no catchup key on a
        # normal bill).
        if bill.get("catchup_applied"):
            inv["catchup_applied"] = True
            inv["catchup_period_start"] = bill.get("catchup_period_start")
            inv["catchup_period_end"] = bill.get("catchup_period_end")
            inv["catchup_periods_covered"] = bill.get("catchup_periods_covered")
            inv["catchup_direction"] = bill.get("catchup_direction")
            inv["catchup_raw_delta_gbp"] = bill.get("catchup_raw_delta_gbp")
            # The PRINTED adjustment -- the same penny-quantized figure that
            # went into the derived total above, not a second independent
            # round() of the raw value (which is how the four category lines
            # drifted from their own total in the first place).
            inv["catchup_adjustment_gbp"] = printed_money.get("catchup_adjustment_gbp")
            inv["catchup_written_off_gbp"] = bill.get("catchup_written_off_gbp")
            inv["catchup_back_billing_cap_applied"] = bill.get("catchup_back_billing_cap_applied")
        else:
            inv["catchup_applied"] = False
        # BILL_CORRECTNESS_ADDENDUM.md Defect 3 (2026-07-09): consumption
        # structured as a list of registers/periods, not one flat line --
        # today every tariff is single-register ("Anytime"), so this is
        # always a one-element list, but the SHAPE supports N so a future
        # ToU tariff (Day/Night/Peak registers) bills correctly without a
        # schema change. Do not build ToU itself here -- just the structure
        # that permits it, per the addendum's own instruction.
        # D_printed_figure_rederivation (2026-08-03): the register carries its
        # own printed unit rate. The portal previously computed this rate in
        # the browser (amount/kwh*100, then toFixed(2)), which is where the
        # unreproducible usage line was actually RENDERED -- so the display
        # precision has to be decided here, once, where it can be tested,
        # rather than reimplemented in JS where it would drift from the Python
        # policy. None when no printable precision reproduces the amount.
        inv["registers"] = [{
            "register_id": "1",
            "label": "Anytime",
            "consumption_kwh": inv["consumption_kwh"],
            "amount_gbp": inv["commodity_amount_gbp"],
            "unit_rate_p_per_kwh": inv["unit_rate_p_per_kwh"],
        }]

        # ADVISOR_STEER_BILL_ARITHMETIC.md Defect 1, R10 class-level gate:
        # a rendered bill whose usage line does not reconcile with its printed
        # meter reads is a Tier-1 billing-accuracy failure -- HELD to the
        # exception queue, never issued (same zero-tolerance treatment as the
        # VAT/consumption pre-bill checks). By construction of
        # displayed_consumption_kwh above this never fires in normal operation;
        # it is the standing guard that catches any future reintroduction of
        # the compounding-rounding bug or a bad reads/usage data source. A held
        # bill has no payment/arrears recorded and does not consume an invoice
        # number (register already advanced -- the meter physically moved).
        reads_reasons = validate_rendered_bill_reads(inv)
        if reads_reasons:
            held_reads.append(BillValidationResult(
                customer_id=cid, period_end=period_end,
                outcome=ValidationOutcome.HELD, reasons=reads_reasons,
            ))
            continue

        # D_money_boundary_reconciliation, the money twin of the reads gate
        # above and the same standing-guard role: by construction of
        # printed_total this cannot fire in normal operation, so if it ever
        # does, an independent rounding site has been reintroduced between the
        # computed bill and the printed one. Checked on the assembled `inv`
        # (the exact dict written to the ledger), not on the intermediate
        # values -- the guard must see what the customer sees, or it would
        # only be re-asserting the arithmetic it just did.
        money_reasons = validate_rendered_bill_money(inv)
        if money_reasons:
            held_money.append(BillValidationResult(
                customer_id=cid, period_end=period_end,
                outcome=ValidationOutcome.HELD, reasons=money_reasons,
            ))
            continue

        invoices_by_cid.setdefault(cid, []).append(inv)

        # D3 step 2: a credit invoice (amount <= 0) has nothing to collect --
        # no payment event is recorded, so tools/generate_payment_ledger_data.py's
        # account ledger sees only the (negative) invoice_raised entry, correctly
        # reducing the running balance by the credit. Fabricating a "payment" here
        # too would double-count it (the ledger negates a payment's amount_gbp to
        # get its effect on the balance, which would cancel the credit back out).
        if not is_credit:
            payment_date = due_date + timedelta(days=days_late)
            pay = {
                "invoice_number": invoice_number,
                "payment_date": payment_date.isoformat(),
                # The customer pays what the invoice PRINTS, not the
                # full-precision total behind it -- collecting a figure that
                # differs from the one on the bill is exactly the "maths
                # doesn't add up" surface this atom closes.
                "amount_gbp": printed_total,
                "method": method,
                "outcome": outcome,
                "income_stress_at_time": stress,
                "tone": _tone,
            }
            payments_by_cid.setdefault(cid, []).append(pay)

        if outcome == "failed":
            eventually_resolved = cid not in churned
            write_off_year = (due_date + timedelta(days=90)).year
            archetype = _debt_archetype(beh.get("income_stress_trajectory") or [], write_off_year)
            arr = {
                "case_id": "ARR-%s-%s" % (cid, period_end),
                "invoice_number": invoice_number,
                "arrears_gbp": round(amount, 2),
                "opened_date": due_date.isoformat(),
                # `method` is the SAME label written onto the payment record
                # above -- the arrears case and the payment it opened from must
                # agree, which is the whole point of
                # PAYMENT_CHANNEL_DD_CONSISTENCY. Reading it from anywhere else
                # would reintroduce the two-generator disagreement.
                "stages": _arrears_stages(amount, due_date, eventually_resolved,
                                           archetype, method=method),
            }
            arrears_by_cid.setdefault(cid, []).append(arr)
        elif outcome == "dispute":
            eventually_resolved = cid not in churned
            write_off_year = (due_date + timedelta(days=60)).year
            archetype = _debt_archetype(beh.get("income_stress_trajectory") or [], write_off_year)
            arr = {
                "case_id": "DIS-%s-%s" % (cid, period_end),
                "invoice_number": invoice_number,
                "arrears_gbp": round(amount, 2),
                "opened_date": due_date.isoformat(),
                "stages": _ic_arrears_stages(amount, due_date, eventually_resolved, archetype),
            }
            arrears_by_cid.setdefault(cid, []).append(arr)

        invoice_number += 1

    # ADVISOR_STEER_BILL_ARITHMETIC.md Defect 2 (2026-07-11): an invoice whose
    # arrears case reaches WRITTEN_OFF on or before the book's reference date
    # ("today" == the latest issue_date across the whole ledger, the identical
    # as_of tools.generate_payment_ledger_data uses) is a real credit-loss
    # event, not still-outstanding debt. Its per-invoice payment_status must
    # say so ("written_off"), otherwise the household ledger correctly zeroes
    # the balance via total_written_off_gross_gbp while the per-bill
    # "Outstanding" sum keeps counting it as owed -- exactly the settled-vs-
    # outstanding contradiction the director saw on C1's portal (the write-off
    # is a household-ledger-level event that was never propagated back to the
    # individual invoice record). Point-in-time honesty preserved: a write-off
    # dated AFTER the book date has not happened yet, so that invoice stays
    # overdue and legitimately counts as outstanding.
    all_issue_dates = [inv["issue_date"] for invs in invoices_by_cid.values() for inv in invs]
    book_as_of = max(all_issue_dates) if all_issue_dates else None
    if book_as_of is not None:
        for cid, arrs in arrears_by_cid.items():
            inv_by_num = {inv["invoice_number"]: inv for inv in invoices_by_cid.get(cid, [])}
            for arr in arrs:
                wo = next((s for s in arr["stages"] if s["stage"] == "WRITTEN_OFF"), None)
                if wo is not None and wo["date"] <= book_as_of:
                    inv = inv_by_num.get(arr["invoice_number"])
                    if inv is not None:
                        inv["payment_status"] = "written_off"

    customers = {}
    for cid in sorted(invoices_by_cid):
        invs = invoices_by_cid[cid]
        pays = payments_by_cid.get(cid, [])
        arrs = arrears_by_cid.get(cid, [])
        total_billed = sum(i["total_amount_gbp"] for i in invs)
        total_paid = sum(p["amount_gbp"] for p in pays if p["outcome"] == "success")
        failed_count = sum(1 for p in pays if p["outcome"] in ("failed", "dispute"))
        customers[cid] = {
            "segment": segment_by_cid.get(cid, "resi"),
            "invoice_count": len(invs),
            "total_billed_gbp": round(total_billed, 2),
            "total_paid_gbp": round(total_paid, 2),
            "balance_gbp": round(total_paid - total_billed, 2),
            "failed_payment_count": failed_count,
            "arrears_case_count": len(arrs),
            "invoices": invs,
            "payments": pays,
            "arrears_history": arrs,
        }

    all_held = list(held_bills) + held_reads + held_money
    result = {
        "meta": {
            "source_json": str(run_json_path),
            "invoice_count": invoice_number - 1,
            "customer_count": len(customers),
            "held_bill_count": len(all_held),
            "held_reads_reconciliation_count": len(held_reads),
            "held_money_reconciliation_count": len(held_money),
        },
        "customers": customers,
        "exception_queue": exception_queue_as_dicts(all_held),
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = generate()
    print("Generated %s (%d invoices, %d customers)" % (OUT_PATH, r["meta"]["invoice_count"], r["meta"]["customer_count"]))
