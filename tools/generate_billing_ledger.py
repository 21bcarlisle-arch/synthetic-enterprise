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

Output: docs/state/billing_ledger.json
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from company.billing.dd_review import billing_account_of
from company.billing.pre_bill_validation import (
    BillValidationResult,
    ValidationOutcome,
    exception_queue_as_dicts,
    validate_bills,
    validate_rendered_bill_money,
    validate_rendered_bill_reads,
)
from company.crm.customer_registry import mpan_core
from company.regulatory.energy_bill_support import ebss_credit_gbp
from saas.bill_generator import CHARGED_AT_THE_METER, CREDIT_BILL, TOU_BANDS, applied_rates
from saas.money import (
    MoneyBoundaryError,
    display_rate_gbp_per_day,
    display_rate_p_per_kwh,
    foot_components_to_total,
)
from saas.tariff_pricing import split_flat_rate_to_tou
from simulation.arrears_engine import (
    _CORP_BACS_DISPUTE_PROB,
    _CORP_BACS_LATE_PROB,
    _CORP_BACS_ON_TIME_PROB,
    _CORP_LATE_DAYS,
    _DD_FAILURE_PROB,
    _LATE_DAYS,
    _ON_TIME_PROB,
    PAYMENT_TERMS_DAYS,
    _tone_for_bill,
    bill_due_date,
)
from simulation.arrears_engine import (
    arrears_stages as _arrears_stages,
)
from simulation.arrears_engine import (
    debt_archetype as _debt_archetype,
)
from simulation.arrears_engine import (
    ic_arrears_stages as _ic_arrears_stages,
)
from simulation.arrears_engine import (
    resolved_settlement as _resolved_settlement,
)
from simulation.arrears_engine import (
    stress_for_year as _stress_for_year,
)
from simulation.arrears_engine import (
    with_credits_applied as _with_credits_applied,
)
from simulation.household import households_whose_account_closed, supply_points_that_left
from tools.grade_svt_invoices_over_ceiling import bill_excess, term_of_bill, terms_by_customer
from tools.run_output_store import load_run_output

PROJECT = Path(__file__).parent.parent
#: The read type of a period a prepayment meter charged as it was used: neither an actual read
#: taken for the bill (A) nor an estimate (E), but the meter's own register.
METER_CHARGED_READ_TYPE = "M"
#: The outcome of a bill wholly inside the change-of-tenancy window or the void: the run booked it
#: to the deemed account (the unnamed occupier's or the owner's) and collected nothing from anyone.
DEEMED_OUTCOME = "deemed_account"
#: The method on a bill the government's bill credit (EBSS) settled whole, so the household paid
#: nothing: the engine marks it `outcome: credit` with no method, which the ledger used to copy as
#: a payment of the whole bill by nobody (218 rows on 4ae8da9b0f, all Oct 2022 to Mar 2023).
#: A bill the credit covers in part keeps the household's own method, and its payment carries
#: `scheme_credit_gbp` beside what the household paid (the 2026-10-27 finding).
SCHEME_CREDIT_METHOD = "scheme_credit"

RUN_JSON = PROJECT / "docs" / "reports" / "run_output_latest.json"
# NOT under site/ (2026-10-14): at 57.7 MiB it passed Cloudflare Pages' 25 MiB per-file limit, and
# Pages refuses the whole upload over one file. No page fetches it; every reader is a generator
# reading disk. docs/state/ is also what the GitHub Pages mirror serves, so it stays fetchable there.
OUT_PATH = PROJECT / "docs" / "state" / "billing_ledger.json"


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


#: A register's id is fixed for the life of its meter serial. The total register is "1" whatever
#: the tariff, and each time-of-use band has its own id after it. They were once numbered by position
#: on the bill, so "1" was the total index on a single-rate bill and the Peak index on the next ToU
#: bill: 66 serials on 67a893e749 read 18,568.6 then 2,140.6 on "register 1". A tariff change on a
#: smart or HH meter reconfigures which registers are billed; it does not renumber them.
ANYTIME = "Anytime"
REGISTER_ID = {ANYTIME: "1", **{label: str(i + 2) for i, (_, label) in enumerate(TOU_BANDS)}}


def _printed_registers(bill_registers, printed_consumption_kwh, printed_commodity_amount_gbp):
    """The bill's time-of-use registers at print precision, or None for a single-rate bill.

    The bill's registers are unrounded. Each is shared out of the PRINTED usage and energy figures
    by its own fraction, and the last register takes the remainder, so the registers sum exactly to
    the printed lines beside them (0.1 kWh, 1p). Each rate is fitted to its own printed pair.
    """
    if not bill_registers or len(bill_registers) < 2:
        return None
    kwh_total = sum(r["consumption_kwh"] for r in bill_registers)
    gbp_total = sum(r["commodity_amount_gbp"] for r in bill_registers)
    if kwh_total <= 0 or gbp_total <= 0:
        return None
    printed = []
    kwh_left, gbp_left = printed_consumption_kwh, printed_commodity_amount_gbp
    for i, reg in enumerate(bill_registers):
        if i == len(bill_registers) - 1:
            kwh, gbp = round(kwh_left, 1), round(gbp_left, 2)
        else:
            kwh = round(printed_consumption_kwh * reg["consumption_kwh"] / kwh_total, 1)
            gbp = round(printed_commodity_amount_gbp * reg["commodity_amount_gbp"] / gbp_total, 2)
            kwh_left -= kwh
            gbp_left -= gbp
        printed.append({
            "register_id": REGISTER_ID[reg["label"]],
            "label": reg["label"],
            "consumption_kwh": kwh,
            "amount_gbp": gbp,
            "unit_rate_p_per_kwh": _printed_unit_rate(kwh, gbp),
        })
    return printed


def _printed_rate_lines(bill_lines, printed_kwh, printed_unit_charge_gbp, opening_read,
                        read_type, contracted_terms=()):
    """A bill across a price change, one line per contracted rate, at print precision; or None.

    Each line's kWh and all-in charge are shared out of the PRINTED usage and the printed energy,
    network-and-policy and EPG figures by the biller's own split (`saas.bill_generator.rate_lines`),
    with the last line taking the remainder, so the lines add up exactly to what is printed beside
    them. Each line carries its own reading pair: the read on the change date is a deemed one,
    flagged estimated (SLC 31H.8), and the last line closes on the bill's own closing read.

    The rate printed is the term's contracted rate wherever kWh x that rate reproduces the line's
    printed amount to the penny, because 22A.3 asks for the Unit Rate and a rate fitted to a small
    line is not it (9 kWh at GBP 1.00 fits 11.11p against a contracted 11.163p). Elsewhere it is
    fitted to the printed pair, as every other usage line is.
    """
    if not bill_lines:
        return None
    kwh_total = sum(line["consumption_kwh"] for line in bill_lines)
    gbp_total = sum(line["unit_charge_gbp"] for line in bill_lines)
    if kwh_total <= 0 or gbp_total <= 0:
        return None
    printed, kwh_left, gbp_left, read = [], printed_kwh, printed_unit_charge_gbp, opening_read
    for i, line in enumerate(bill_lines):
        last = i == len(bill_lines) - 1
        if last:
            kwh, gbp = round(kwh_left, 1), round(gbp_left, 2)
        else:
            kwh = round(printed_kwh * line["consumption_kwh"] / kwh_total, 1)
            gbp = round(printed_unit_charge_gbp * line["unit_charge_gbp"] / gbp_total, 2)
            kwh_left -= kwh
            gbp_left -= gbp
        closing = round(read + kwh, 1)
        term = next((t for t in contracted_terms
                     if t["tariff_effective_from"] == line["term_start"]), None)
        rate = term and not term.get("tou_unit_rates") and term.get("unit_rate_p_per_kwh")
        if not rate or abs(round(kwh * rate / 100, 2) - gbp) > 0.001:
            rate = _printed_unit_rate(kwh, gbp)
        printed.append({
            "tariff_effective_from": line["term_start"],
            "period_start": line["period_start"],
            "period_end": line["period_end"],
            "consumption_kwh": kwh,
            "unit_charge_gbp": gbp,
            "unit_rate_p_per_kwh": rate,
            "time_of_use": line["time_of_use"],
            "opening_read_kwh": read,
            "closing_read_kwh": closing,
            "closing_read_type": read_type if last else "E",
        })
        read = closing
    return printed


#: Terms whose revenue carries the actual policy and network cost on top, so no single rate was
#: contracted and the validator says so rather than checking against one.
_NO_SINGLE_CONTRACTED_RATE = ("pass_through", "flex")


def _tou_terms(account_terms, bills):
    """(customer, term_start) of every term the biller settled on a peak/off-peak pair.

    LIMIT: the run records which terms were SOLD as ToU nowhere (`demand_response_log` is not in
    the run output, and the term row carries only the flat rate), so a term counts as ToU when any
    bill inside it carries band registers. Only that a pair existed is read from the bills; the
    pair's RATES are the product rule's, so a bill charging the wrong band rate still disagrees.
    """
    out = set()
    for b in bills:
        if b.get("registers"):
            term = term_of_bill(account_terms, b)
            if term is not None:
                out.add((b["customer_id"], term["term_start"]))
    return out


def _contracted_terms(account_terms, bill, tou_terms):
    """Every recorded term the bill's period touches, at the rate the account was SOLD at.

    From `account_state_log`, never from the bill, so a bill that charged the wrong rate disagrees
    with it instead of being fitted to it. The rate is all-in p/kWh, the figure the term is struck
    at and the cap is set on. A chosen term also carries the peak/off-peak pair the one product rule
    strikes from that flat rate (`split_flat_rate_to_tou`) where the term was settled as ToU (see
    `_tou_terms`); the term row records only the flat rate, so the pair is derived here. A default
    term is single-rate (`tou_desk.offers_tou`). A period touching two terms is a bill across a
    price change and carries both.
    """
    start, end = str(bill["period_start"])[:10], str(bill["period_end"])[:10]
    out = []
    for t in account_terms.get(bill["customer_id"], ()):
        if not (t["term_start"] <= end and start < t["term_end"]):
            continue
        rate = t.get("unit_rate_gbp_per_mwh")
        no_rate = rate is None or t["tariff_type"] in _NO_SINGLE_CONTRACTED_RATE
        pair = (split_flat_rate_to_tou(rate)
                if not no_rate and (bill["customer_id"], t["term_start"]) in tou_terms else None)
        out.append({
            "tariff_effective_from": t["term_start"],
            "tariff_effective_to": t["term_end"],
            "tariff_type": t["tariff_type"],
            **({"fixed_term_end": t["fixed_term_end"]} if t.get("fixed_term_end") else {}),
            "unit_rate_p_per_kwh": None if no_rate else round(rate / 10.0, 4),
            "tou_unit_rates": None if pair is None else [
                {"register_label": "Peak", "unit_rate_p_per_kwh": round(pair[0] / 10.0, 4)},
                {"register_label": "Off-peak", "unit_rate_p_per_kwh": round(pair[1] / 10.0, 4)}],
        })
    return out


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
# meter serial + MPAN/MPRN. The MPAN core has one home, company/crm/customer_registry.mpan_core;
# the MPRN keeps the registry's scheme, duplicated here.
_mpan = mpan_core


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

def _held_spans(bills: list, held: list) -> dict[tuple, list[tuple[str, str]]]:
    """(customer_id, commodity) -> (period_start, period_end) of each bill the pre-bill gate held."""
    keys = {(r.customer_id, r.period_end) for r in held}
    spans: dict[tuple, list[tuple[str, str]]] = {}
    for b in bills:
        if (b.get("customer_id"), b.get("period_end")) in keys:
            spans.setdefault((b["customer_id"], b.get("commodity")), []).append(
                (b["period_start"], b["period_end"]))
    return spans


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = RUN_JSON
    if out_path is None:
        out_path = OUT_PATH
    data = load_run_output(run_json_path)

    bills = data.get("bills", [])
    behavioral = data.get("per_customer_behavioral", {})
    # By supply point, as the engine tests each bill's own id: see `supply_points_that_left`.
    churned = supply_points_that_left(
        households_whose_account_closed(data), {b["customer_id"] for b in bills})
    # Each bill's outcome, which failed bills are written off, when, and what credit or repayment
    # is netted against each, is READ from the engine over the same unfiltered bills the P&L sees
    # -- never re-derived here. The engine drops held bills and credits itself, so the ledger and
    # `bad_debt_gbp` agree per account;
    # tests/tools/test_the_ledger_and_the_pnl_write_off_agree_on_the_real_book.py holds that on the
    # real run.
    resolved, write_offs, credits_applied = _resolved_settlement(bills, behavioral, churned, seed=42)

    # DOMAIN_SENSE_AND_COMPLIANCE.md Phase 3: Tier-1 pre-bill validation gate
    # (director's Principle 1 -- 100% of bills validated before issue, zero
    # tolerance). A held bill is excluded from this cycle's normal issuance
    # entirely (never sent) and recorded on the exception queue below rather
    # than silently dropped.
    bills, held_bills = validate_bills(bills)
    held_spans = _held_spans(data.get("bills", []), held_bills)
    account_terms = terms_by_customer(data)
    tou_terms = _tou_terms(account_terms, bills)

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
    # A time-of-use meter has one cumulative index per register, keyed by its band label.
    running_register_read: dict[tuple[str, str, str], float] = {}

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

        due_date = bill_due_date(cid, period_end)
        issue_date = due_date - timedelta(days=PAYMENT_TERMS_DAYS)
        generation_delay_days = (issue_date - date.fromisoformat(period_end)).days

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
        part_paid = 0.0
        # What the named payer is asked for: the bill less any occupier or owner share (B7).
        asked = amount
        # The government's credit applied to this bill, which the household did not pay. Only a bill
        # the engine collects carries it: the engine nets it there (`owed_after_scheme_credit`).
        scheme_credit = 0.0
        deemed_payer = None
        row = resolved.get((cid, period_end, commodity))
        occupier_held_credit = bool(bill.get("occupier_scheme_credit_gbp")
                                    or bill.get("occupier_scheme_month_credit_gbp"))
        # The engine's own test for a bill nobody named is asked for (`_resolve_bills`), so a
        # catch-up credit inside the window is the deemed account's too: on the named payer it stood
        # as credit nothing ever drew (OCC-2e29bf263cb4, OCC-86e666eb2f01).
        in_window = row is None and (bill.get("occupier_share", 0.0)
                                     + bill.get("void_owner_share", 0.0)) >= 1.0 - 1e-9
        if in_window:
            # The run booked it as the unnamed occupier's debt or the owner's charge, billed and
            # never collected (B7 slices 4 and 6; back_billing_and_liability.md s.13, "Billed, not
            # collected"). That is its outcome. This branch used to draw a payer and an outcome of
            # its own, so the named household showed DD collections and failed DDs for money nobody
            # asked it for (OCC-3c914ee8cef5g, OCC-561d240ea21a: the O27 never-chased debits).
            scheme_credit = bill.get("occupier_scheme_credit_gbp", 0.0)
            method, _tone, outcome, days_late = None, None, DEEMED_OUTCOME, 0
            deemed_payer = ("owner" if bill.get("void_owner_share", 0.0) > bill.get("occupier_share", 0.0)
                            else "occupier")
        elif is_credit:
            method = None
            _tone = None
            outcome, days_late = "success", 0
        elif row is not None:
            # The engine's outcome, which reads the world's payment truth where a draw cannot.
            method, outcome, days_late = row["method"], row["outcome"], row["days_late"]
            if outcome == "credit":
                method = SCHEME_CREDIT_METHOD
            part_paid = row.get("part_paid_gbp", 0.0)
            asked = round(row["amount_gbp"] + part_paid, 2)
            # The engine nets the month's EBSS from the payer only where the unnamed occupier's
            # account did not hold it (`_resolve_bills`); a part-window month whose credit the
            # occupier held left the payer owing its share whole (OCC-25ff8966357a).
            scheme_credit = (0.0 if occupier_held_credit else ebss_credit_gbp(
                segment, commodity, period_end[:7], bill.get("account_held_from")))
            _tone = None if outcome == "credit" else _tone_for_bill(method, cid, period_end)
        else:
            raise ValueError("no engine outcome for %s %s %s, which is not inside the window"
                             % (cid, period_end, commodity))

        # Defect 2: meter-read status, opening/closing reads, meter serial,
        # MPAN/MPRN. read_event is None for a bill Phase 3's meter-read
        # simulation doesn't cover (e.g. a run predating that data) --
        # falls back to "actual" at the bill's own consumption figure
        # rather than omitting the fields.
        read_event = read_by_key.get((cid, period_end))
        if bill.get("billing_basis") == CHARGED_AT_THE_METER:
            # A prepayment meter charged this period as it was used: the statement shows the
            # meter's own register, never an estimate, whatever reached the supplier for settlement.
            read_type = METER_CHARGED_READ_TYPE
            register_consumption_kwh = bill.get("total_consumption_kwh", 0)
        elif read_event is not None and read_event["status"] == "estimated":
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

        # The term this bill sits in, as the run recorded it, and the default-tariff verdict on the
        # bill's UNROUNDED amounts: the printed lines are rounded, which on a 1-22 day stub moves a
        # unit rate past the 0.5% tolerance. Both None where the run records no term / cannot grade.
        # The rates this bill was charged at, from the biller's own function and the bill's own
        # inputs: the raw export carries them as contracted terms (INV_VAT_RATE and
        # INV_NON_COMMODITY_WITHIN_ALL_IN read them).
        vat_rate, non_commodity_gbp_per_mwh = applied_rates(
            bill.get("segment", "resi"), commodity, bill.get("total_consumption_kwh", 0.0),
            bill.get("days_in_period") or 0, bill["period_start"])
        term = term_of_bill(account_terms, bill)
        term_type = term["tariff_type"] if term else None
        term_excess = bill_excess(bill, term_type) if term_type else None
        inv = {
            "invoice_number": invoice_number,
            "customer_id": cid,
            # A prepayment household is sent a statement of what its meter charged, not a bill.
            "document_type": bill.get("document", CREDIT_BILL),
            "term_tariff_type": term_type,
            "default_tariff_excess_p_per_kwh": None if term_excess is None else round(term_excess, 4),
            "contracted_terms": _contracted_terms(account_terms, bill, tou_terms),
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
            "vat_rate": vat_rate,
            "non_commodity_rate_gbp_per_mwh": round(non_commodity_gbp_per_mwh, 4),
            "issue_date": issue_date.isoformat(),
            "generation_delay_days": generation_delay_days,
            "due_date": due_date.isoformat(),
            # Expert-Hour finding, 2026-07-12: a credit invoice showing
            # "PAID" is confusing -- nothing was paid, the supplier owes the
            # customer. `is_credit` takes priority over the outcome-derived
            # label (outcome is forced to "success" for a credit, see above).
            "payment_status": (
                "billed_to_the_" + deemed_payer if outcome == DEEMED_OUTCOME else
                "credited" if is_credit else
                "disputed" if outcome == "dispute" else
                ("paid" if outcome in ("success", "credit") else "overdue")
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
            # A HELD BILL IS RELEASED HERE, at the next actual read: the assembly reconciles a held
            # month as billed nothing, so this catch-up is its first demand. The held periods are
            # named so the record shows which days this bill took up, not a gap.
            reconciled = [
                {"period_start": start, "period_end": end}
                for start, end in held_spans.get((bill["customer_id"], bill.get("commodity")), [])
                if inv["catchup_period_start"] <= start and end <= inv["catchup_period_end"]]
            if reconciled:
                inv["held_periods_reconciled"] = reconciled
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
        # 2026-10-24: a time-of-use bill prints one register per band, each with its kWh, charge
        # and rate (SLC 22A.3; a_tou_tariff_needs_the_households_choice_not_its_meter.md, item 6).
        inv["registers"] = _printed_registers(
            bill.get("registers"), inv["consumption_kwh"], inv["commodity_amount_gbp"],
        ) or [{
            # A ToU term's bill with use in one band only (a one-day stub) has one register, and
            # it is that band's, at that band's rate: printed "Anytime" it read as the flat rate
            # charged at 0.786 of itself (2 of 52,782 on 4ae8da9b0f, against the contracted pair).
            "label": (bill["registers"][0]["label"]
                      if len(bill.get("registers") or []) == 1 else ANYTIME),
            "consumption_kwh": inv["consumption_kwh"],
            "amount_gbp": inv["commodity_amount_gbp"],
            "unit_rate_p_per_kwh": inv["unit_rate_p_per_kwh"],
        }]
        inv["registers"][0].setdefault("register_id", REGISTER_ID[inv["registers"][0]["label"]])
        if bill.get("tou_registers_withheld"):
            inv["tou_registers_withheld"] = bill["tou_registers_withheld"]
        # 2026-10-26: a register's own readings. A two-rate meter is read register by register, so
        # the one opening/closing pair above cannot say how its volume splits, and the raw export
        # exported 1,416 ToU periods of the 4ae8da9b0f book as `consumption_only`. Each index
        # advances by its printed kWh, so closing - opening reproduces the register to 0.1 kWh.
        # LIMIT: a register's index advances only over periods that print it; a household back on
        # a single rate records no band split, so the index does not move while it is. The total
        # register ("1") is the invoice's own opening/closing pair and advances under every tariff.
        # A one-band stub reads its band's own index too: on the total index it went backwards
        # against the band's next read.
        if any(reg["label"] != ANYTIME for reg in inv["registers"]):
            for reg in inv["registers"]:
                reg_key = (cid, commodity, reg["label"])
                reg_opening = running_register_read.get(reg_key, 0.0)
                reg["opening_read_kwh"] = reg_opening
                reg["closing_read_kwh"] = round(reg_opening + reg["consumption_kwh"], 1)
                running_register_read[reg_key] = reg["closing_read_kwh"]
        # The Treasury's EPG share on this bill's volume (4ef70aba92). It is supplier revenue the
        # household never pays, so it is NOT in the total; it is printed beside it because gross
        # margin counts it and a reader comparing the two needs both (the 2026-10-26 finding).
        if bill.get("hmt_epg_receipt_gbp"):
            inv["hmt_epg_receipt_gbp"] = round(bill["hmt_epg_receipt_gbp"], 2)
        # 2026-10-26: a period across a price change prints a line per contracted rate (SLC 22A.3;
        # tariffs_and_the_default_tariff_2026-10-25.md, "A bill across a price change"). The lines'
        # all-in charge is the printed energy, network-and-policy and EPG figures together.
        printed_lines = _printed_rate_lines(
            bill.get("rate_lines"), inv["consumption_kwh"],
            round(inv["commodity_amount_gbp"] + inv["non_commodity_amount_gbp"]
                  + inv.get("hmt_epg_receipt_gbp", 0.0), 2),
            opening_read_rounded, read_type, inv["contracted_terms"])
        if printed_lines is not None:
            inv["rate_lines"] = printed_lines

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

        # The month's WHOLE credit, as the account received it when this bill applied it. The
        # payment row below carries only what this bill used (capped at the bill, dated at the
        # household's payment), and a credit invoice has no payment row at all: on the 2eeb3f0b3
        # book that read as 283 short, late or missing EBSS months (INV_EBSS_CREDIT_EACH_MONTH).
        # The engine netted the month's credit wherever it resolved the bill, unless the unnamed
        # occupier's account held it (`arrears_engine`, `occupier_scheme_credit_gbp`).
        # A bill the engine resolved posts only a credit the payer's own account received.
        if row is None:
            whole_credit = (bill.get("occupier_scheme_month_credit_gbp")
                            or bill.get("occupier_scheme_credit_gbp"))
        elif occupier_held_credit:
            whole_credit = 0.0
        else:
            whole_credit = ebss_credit_gbp(segment, commodity, period_end[:7],
                                           bill.get("account_held_from"))
        if whole_credit:
            inv["scheme_credit_month_gbp"] = round(whole_credit, 2)
        invoices_by_cid.setdefault(cid, []).append(inv)

        # D3 step 2: a credit invoice (amount <= 0) has nothing to collect --
        # no payment event is recorded, so tools/generate_payment_ledger_data.py's
        # account ledger sees only the (negative) invoice_raised entry, correctly
        # reducing the running balance by the credit. Fabricating a "payment" here
        # too would double-count it (the ledger negates a payment's amount_gbp to
        # get its effect on the balance, which would cancel the credit back out).
        if outcome == DEEMED_OUTCOME:
            # Nobody at this account was asked, so nothing was received or missed. What the page
            # takes off the named payer is the bill less the credit the deemed account held.
            inv["billed_to"] = deemed_payer
            inv["deemed_debt_gbp"] = round(printed_total - (whole_credit or 0.0), 2)
        elif not is_credit:
            payment_date = due_date + timedelta(days=days_late)
            # A bill only partly inside the window or the void: the engine asks the named payer for
            # its own share alone (`_resolve_bills`), and the rest is the deemed account's. This
            # used to collect the full printed total, so the payer paid the occupier's days, or a
            # failed bill was written off at the payer's share and owed in full (OCC-87206d346f15g,
            # GBP 19.16; 239 bills on 5e3e9966a5).
            deemed_share = ((bill.get("occupier_share", 0.0) or 0.0)
                            + (bill.get("void_owner_share", 0.0) or 0.0))
            payer_face = printed_total
            if 0.0 < deemed_share < 1.0:
                payer_face = round(printed_total * (1.0 - deemed_share), 2)
                inv["deemed_share_gbp"] = round(printed_total - payer_face, 2)
                inv["deemed_share_to"] = ("owner" if bill.get("void_owner_share", 0.0)
                                          > bill.get("occupier_share", 0.0) else "occupier")
            # No more of the credit than the bill: what it exceeds by stays on the account, and the
            # engine nets that from the next bill (`credits_applied`, kind "credit").
            scheme_applied = round(min(scheme_credit, payer_face), 2)
            pay = {
                "invoice_number": invoice_number,
                "payment_date": payment_date.isoformat(),
                # The customer pays what the invoice PRINTS, not the
                # full-precision total behind it -- collecting a figure that
                # differs from the one on the bill is exactly the "maths
                # doesn't add up" surface this atom closes. Less the scheme
                # credit, which the account received and the household did not
                # pay: part-covered bills were recorded as paid in full (the
                # 2026-10-27 finding).
                "amount_gbp": round(payer_face - scheme_applied, 2),
                "method": method,
                "outcome": outcome,
                "income_stress_at_time": stress,
                "tone": _tone,
            }
            if part_paid:
                # A mover's final bill paid in part: the case below is for the rest.
                pay["part_paid_gbp"] = part_paid
            if scheme_applied:
                pay["scheme_credit_gbp"] = scheme_applied
                inv["scheme_credit_gbp"] = scheme_applied
            payments_by_cid.setdefault(cid, []).append(pay)

        written_off = write_offs.get((cid, period_end, commodity))
        # A case is for what is still owed once account credit on the same contract is netted
        # (SLC 27.16) -- the amount the engine writes off or leaves open. `face` is the bill.
        credits = credits_applied.get((cid, period_end, commodity), [])
        face = amount
        amount = round(asked - part_paid, 2)
        if credits:
            amount = max(round(amount - sum(c["amount_gbp"] for c in credits), 2), 0.0) + 0.0
        if outcome == "failed":
            # A case that is not written off is still an open balance, and ends on BALANCE_OPEN.
            still_open = written_off is None
            wo_date = None if written_off is None else written_off["date"]
            write_off_year = (wo_date or due_date + timedelta(days=90)).year
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
                "stages": _arrears_stages(amount, due_date, still_open,
                                           archetype, method=method, write_off_date=wo_date),
            }
            arrears_by_cid.setdefault(cid, []).append(arr)
        elif outcome == "dispute":
            still_open = written_off is None
            wo_date = None if written_off is None else written_off["date"]
            write_off_year = (wo_date or due_date + timedelta(days=60)).year
            archetype = _debt_archetype(beh.get("income_stress_trajectory") or [], write_off_year)
            arr = {
                "case_id": "DIS-%s-%s" % (cid, period_end),
                "invoice_number": invoice_number,
                "arrears_gbp": round(amount, 2),
                "opened_date": due_date.isoformat(),
                "stages": _ic_arrears_stages(amount, due_date, still_open, archetype,
                                              write_off_date=wo_date),
            }
            arrears_by_cid.setdefault(cid, []).append(arr)
        elif outcome == "success" and credits and not is_credit:
            # The bill asks for its charges less the credit on the account (SLC 31H.12,
            # home_moves.md s.8.8a choice 11), so the household pays the rest. Only a credit bill's
            # credit is netted here: a repayment's excess was never shown as money in, so taking
            # it off this payment would show less collected than the household paid.
            netted = round(sum(c["amount_gbp"] for c in credits if c.get("kind") == "credit"), 2)
            # No more credit than the bill: a credit a penny over it was a -0.01 "payment" (25 on
            # 4ae8da9b0f, INV_PAYMENT_AMOUNT_SIGN); the penny stays on the account as credit.
            netted = min(netted, pay["amount_gbp"])
            if netted > 0:
                pay["amount_gbp"] = round(pay["amount_gbp"] - netted, 2)
                pay["credit_applied_gbp"] = netted
                inv["credit_applied_gbp"] = netted
                if pay["amount_gbp"] <= 0:
                    inv["payment_status"] = "settled_by_credit"
        # What is still owed on THIS invoice: its case's arrears_gbp, the one figure the household
        # balance also nets credit from -- never the face, which a part-credited bill no longer owes.
        inv["outstanding_gbp"] = 0.0
        if outcome in ("failed", "dispute"):
            # Credit bills and the household's own repayments both net the case, but only a
            # repayment is money in, so the two are kept apart.
            repaid = round(sum(c["amount_gbp"] for c in credits if c.get("kind") == "repayment"), 2)
            arr.update(face_gbp=round(face, 2),
                       credit_applied_gbp=round(asked - part_paid - amount - repaid, 2),
                       repaid_gbp=repaid,
                       stages=_with_credits_applied(arr["stages"], asked - part_paid, credits))
            inv["outstanding_gbp"] = arr["arrears_gbp"]
            inv["credit_applied_gbp"] = arr["credit_applied_gbp"]
            if credits and amount == 0:
                inv["payment_status"] = "paid_late" if repaid else "settled_by_credit"

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
                        inv["outstanding_gbp"] = 0.0

    journeys_by_account: dict[str, list] = {}
    for j in data.get("collections_journeys") or []:
        journeys_by_account.setdefault(str(j.get("account_id")).removeprefix("ACC-"), []).append(j)
    offers_by_account: dict[str, list] = {}
    for r in data.get("retention_log") or []:
        offers_by_account.setdefault(r.get("customer_id"), []).append(r)
    # SLC 22C statements are per supply point (one per fuel's fixed term). None on a run that
    # predates them, so the export can tell "sent none" from "the run did not record them".
    notices_by_cid: dict[str, list] | None = (
        None if "renewal_notice_log" not in data else {})
    for r in data.get("renewal_notice_log") or []:
        notices_by_cid.setdefault(r.get("customer_id"), []).append(r)

    customers = {}
    for cid in sorted(invoices_by_cid):
        invs = invoices_by_cid[cid]
        pays = payments_by_cid.get(cid, [])
        arrs = arrears_by_cid.get(cid, [])
        total_billed = sum(i["total_amount_gbp"] for i in invs)
        # Billed to the unnamed occupier's or the owner's deemed account at this supply point.
        total_deemed = sum(i.get("deemed_debt_gbp", 0.0) + i.get("deemed_share_gbp", 0.0)
                           for i in invs)
        total_paid = sum(p["amount_gbp"] if p["outcome"] == "success" else p.get("part_paid_gbp", 0.0)
                         for p in pays)
        failed_count = sum(1 for p in pays if p["outcome"] in ("failed", "dispute"))
        customers[cid] = {
            "segment": segment_by_cid.get(cid, "resi"),
            "invoice_count": len(invs),
            "total_billed_gbp": round(total_billed, 2),
            "total_paid_gbp": round(total_paid, 2),
            "balance_gbp": round(total_paid - total_billed + total_deemed, 2),
            "total_deemed_gbp": round(total_deemed, 2),
            "failed_payment_count": failed_count,
            "arrears_case_count": len(arrs),
            "invoices": invs,
            "payments": pays,
            "arrears_history": arrs,
            # The company's own collections journeys and end-of-term retention offers, for the billing
            # account this supply point bills under: dated acts the raw export carries as events, so
            # the domain-invariant suite can ask whether they happened when the rules allow.
            # (`renewal_decisions_log` is the HOUSEHOLD's choice on its journey, not the company's.)
            "collections_desk_journeys": journeys_by_account.get(billing_account_of(cid), []),
            "renewal_offers": offers_by_account.get(billing_account_of(cid), []),
            **({"renewal_notices": notices_by_cid.get(cid, [])}
               if notices_by_cid is not None else {}),
        }

    # Reg 6D: the credit a leaver's final bill closed in is paid back. The run logs the refund; the
    # ledger carries it so the page ledger can post the money leaving (cold read O27, 33 accounts
    # that stood in credit for ever).
    for refund in data.get("credit_refund_log", []):
        if refund["customer_id"] in customers:
            customers[refund["customer_id"]].setdefault("refunds", []).append({
                "paid_date": refund["paid_date"], "amount_gbp": refund["credit_amount_gbp"]})

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
