#!/usr/bin/env python3
"""THE RAW EXPORT — every fact needed to rebuild an account's bills, and nothing we computed.

Director brief, 2026-09-02 (`DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02`), work item 1:

    "The raw export — the validator's input. Every fact needed to reconstitute an account over its
     life: meter reads with their dates and type; tariff terms with their effective dates; payments
     as received; adjustments and their reasons. **Nothing derived.** No computed rate, no total, no
     running balance — and no bill, because a bill *is* the calculation. If a derived figure leaks
     into this export, the validator confirms our arithmetic against itself and the exercise is
     worthless."

Property §4.1: *"The raw export contains nothing derived. Provable: a check that refuses a derived
field."*

---

## WHY A DENYLIST OF NAMES CANNOT BE THAT CHECK

The obvious check is a list of forbidden field names — `total_amount_gbp`, `vat_gbp`, `balance_gbp`.
It is fail-open on the very next field: the first derived quantity nobody thought of is exported
silently, and the check reports clean. This project has paid for that shape repeatedly (the
`index_is_a_fail_open_control` lesson, and `disk_headroom`'s positive-only identification, which was
written for the same reason).

An ALLOWLIST OF NAMES is better and still not enough, because it cannot see a derived number wearing
a raw name. Nothing about the string `consumption_kwh` stops someone assigning revenue to it.

## SO EVERY FIELD DECLARES ITS UNIT, AND ONE UNIT IS FORBIDDEN

`FIELDS` below maps every exported field to `(unit, why it is raw)`. The check refuses two things:

  * a field present in the export and NOT declared here — fail-closed on the next field;
  * a field declared with unit `GBP_COMPUTED` — the unit that names "money this company worked out".

Units say *what the number is* rather than what it is called, which is this project's own
`before measuring a thing, say what it is` applied to an export schema. And declaring the unit forces
the question that matters at the moment a field is added: **is this measured, contracted, or
calculated?**

## THE THREE HONEST KINDS OF RAW

  MEASURED    a meter read, a volume, a date, a count of days. The world did it.
  CONTRACTED  a unit rate, a standing charge per day, a VAT rate. The rate the account was on. It is
              raw about THIS ACCOUNT — but see the limit below.
  MOVED       money that actually changed hands: a payment received, an adjustment applied. Raw
              because it happened, not because we worked it out.

## THE LIMIT, STATED HERE RATHER THAN DISCOVERED LATER

Exporting the CONTRACTED RATES means the validator recomputes `rate x volume` and gets our answer
whenever our rate is wrong. It validates the ARITHMETIC over the rates, not the RATES. A tariff whose
unit rate was mis-set is invisible to a reconstruction fed that same unit rate.

That is a real hole and it is why the brief's §3 says what it says about shared error. Two things
narrow it, neither of them this module's job: checking the rates themselves against the published
record, and the conservation checks that use no rates at all. Both are named in the design note, and
this module's contribution is to make the hole VISIBLE — every exported rate carries the unit
`CONTRACTED`, so counting what a reconstruction leans on is a `grep`.
"""
from __future__ import annotations

import json
from pathlib import Path

from company.billing.dd_review import billing_account_of

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
LEDGER_PATH = PROJECT_DIR / "docs" / "state" / "billing_ledger.json"

# ── the unit vocabulary ──────────────────────────────────────────────────────────────────────
MEASURED = "MEASURED"            # a volume, a read, a date, a count — the world did it
CONTRACTED = "CONTRACTED"        # a rate the account was on (see the LIMIT in the docstring)
MOVED = "MOVED"                  # money that actually changed hands
IDENTIFIER = "IDENTIFIER"        # an mpan, a meter serial, an account id
EVENT = "EVENT"                  # what kind of thing happened: read type, payment method, reason
#: THE FORBIDDEN UNIT. Money this company worked out. Nothing carrying it may be exported, and
#: declaring a field with it is how a future author says "this is derived" in one word.
GBP_COMPUTED = "GBP_COMPUTED"

RAW_UNITS = (MEASURED, CONTRACTED, MOVED, IDENTIFIER, EVENT)

#: The read_type of an OPENING reading. It is the previous period's CLOSING reading rather than a
#: separate visit, so this bill's `read_type` is not its type -- claiming it would attribute an
#: actual read to an estimated period, or the reverse.
CARRIED_FORWARD = "carried_forward"

#: How a period's volume can be established from what is exported. Declared per period so a
#: reconstruction never has to infer whether it may subtract two readings.
VOLUME_FROM_READS = "reads"                 # two readings exported; the validator subtracts
VOLUME_CONSUMPTION_ONLY = "consumption_only"  # no usable readings; our volume is all there is
VOLUME_UNAVAILABLE = "unavailable"          # neither; the period cannot be reconstructed at all

#: The ledger's method on a bill the government's credit settled whole (`generate_billing_ledger`).
SCHEME_CREDIT = "scheme_credit"

#: EVERY field this export may contain, with its unit and why it is raw. A field absent from here
#: is refused by `derived_leaks` whatever it is called.
FIELDS: dict[str, tuple[str, str]] = {
    # account identity
    "customer_id": (IDENTIFIER, "the account this is about"),
    "segment": (EVENT, "which customer class the account is — a fact about the account"),
    "billing_account_id": (IDENTIFIER, "the billing account this supply point bills under: a "
                                       "dual-fuel household's two fuels share one"),
    "commodity": (EVENT, "electricity or gas"),
    "mpan": (IDENTIFIER, "the electricity supply point"),
    "mprn": (IDENTIFIER, "the gas supply point"),
    "meter_serial": (IDENTIFIER, "the physical meter"),
    "meter_type": (EVENT, "smart or traditional: the meter type the supplier holds for the supply "
                          "point when the period was billed, a metering-record fact; None where "
                          "it holds none"),
    # meter reads
    "read_date": (MEASURED, "when the register was read"),
    "register_id": (IDENTIFIER, "which register on the meter"),
    "register_label": (EVENT, "what the register is called on the bill (Anytime, Night)"),
    "read_kwh": (MEASURED, "what the register said"),
    "read_type": (EVENT, "actual, estimated, customer or deemed — how the read was obtained; "
                         "or carried_forward, meaning it is the previous period's closing read"),
    "volume_basis": (EVENT, "whether this period's volume can be established from exported "
                            "readings, or only from the figure we computed — a fact about what "
                            "was observable, not a quantity"),
    # the period the reads bound
    "period_start": (MEASURED, "first day the account was supplied in this period"),
    "period_end": (MEASURED, "last day the account was supplied in this period"),
    "days_in_period": (MEASURED, "a count of calendar days, not a calculation over money"),
    "held_periods_reconciled": (EVENT, "periods a pre-bill hold kept off their own bill, taken "
                                       "up by this bill's catch-up at its actual read"),
    "consumption_kwh": (MEASURED, "the volume the period was billed for: between two reads "
                                  "where it has them, which INV_PERIOD_MATCHES_READS checks"),
    "catchup_kwh": (MEASURED, "the kWh on an actual bill's catch-up line: the meter's use over "
                              "the estimated run before it less the estimates printed for it, so "
                              "the reads span consumption_kwh plus this"),
    "document_type": (EVENT, "what was sent for the period: a credit bill, or a prepayment "
                             "meter's statement"),
    # contracted terms
    "unit_rate_p_per_kwh": (CONTRACTED, "the rate the account was on for this period"),
    "standing_charge_gbp_per_day": (CONTRACTED, "the daily standing charge the account was on"),
    "vat_rate": (CONTRACTED, "the statutory rate for this segment"),
    "non_commodity_rate_gbp_per_mwh": (CONTRACTED, "network and levy pass-through rate for the year"),
    "tariff_effective_from": (MEASURED, "when these terms started applying"),
    "tariff_effective_to": (MEASURED, "when they stopped"),
    "contracted_terms": (CONTRACTED, "every recorded term the period touches, from the account's "
                                     "term record and never from the bill; two where the period "
                                     "crosses a price change"),
    "tariff_type": (CONTRACTED, "the product the term was sold as (fixed, svt, ...)"),
    "fixed_term_end": (CONTRACTED, "the day the contract says a fixed term ends, which a move or "
                                   "a switch can pre-empt; exclusive, as tariff_effective_to"),
    "tou_unit_rates": (CONTRACTED, "a chosen term's peak and off-peak rates, the pair the one "
                                   "product rule strikes from its flat rate"),
    # money that actually moved
    "payment_date": (MEASURED, "when the payment was received"),
    "payment_amount_gbp": (MOVED, "what was actually received — it happened, we did not work it out"),
    "payment_method": (EVENT, "direct debit, card, prepayment top-up"),
    "adjustment_date": (MEASURED, "when the adjustment was applied"),
    "adjustment_amount_gbp": (MOVED, "money actually credited or debited to the account"),
    "adjustment_reason": (EVENT, "why — a stated reason, not a computation"),
    # dated acts the company holds (2026-10-27), in `account_events` and never in the raw export
    # above: what it did and when, never what it was worth
    "due_date": (MEASURED, "the date printed on the bill as the day it falls due"),
    "settled_date": (MEASURED, "the day a collection for this bill succeeded; None where none "
                               "did, so a failed or never-made collection reads as unpaid"),
    "journey_exit": (EVENT, "how a collections journey ended: cured, write-off, still open"),
    "event": (EVENT, "the collections step taken: missed payment, reminder, plan offered, "
                     "write-off"),
    "event_date": (MEASURED, "the day the step was taken"),
    "event_rule": (EVENT, "the rule a write-off was made under, as the company recorded it"),
    "offer_date": (MEASURED, "the day the company made its end-of-term retention offer"),
    "notice_date": (MEASURED, "the day the company sent a fixed term's SLC 22C statement"),
}


class DerivedFieldLeaked(Exception):
    """The raw export carries something this company calculated. Fail-closed: refuse the export."""


def derived_leaks(record: dict, path: str = "") -> list[str]:
    """Every field in `record` that may not be in a raw export, with why. Recurses into lists/dicts.

    TWO WAYS TO FAIL, both fail-CLOSED:
      * a field nobody declared — the next derived quantity, whatever it gets called;
      * a field declared `GBP_COMPUTED` — someone naming it derived and exporting it anyway.
    """
    out: list[str] = []
    for key, value in sorted(record.items()):
        here = "{}.{}".format(path, key) if path else key
        if isinstance(value, dict):
            out.extend(derived_leaks(value, here))
            continue
        if isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    out.extend(derived_leaks(item, "{}[{}]".format(here, i)))
            continue
        declared = FIELDS.get(key)
        if declared is None:
            out.append("{}: undeclared — a raw export may only carry fields declared in FIELDS "
                       "with their unit. If this is measured, contracted or moved, declare it and "
                       "say so; if it is money this company worked out, it does not belong here."
                       .format(here))
        elif declared[0] == GBP_COMPUTED:
            out.append("{}: declared {} — money this company calculated. The validator must "
                       "recompute it, not be handed it.".format(here, GBP_COMPUTED))
    return out


def _reads_from_invoice(inv: dict) -> list[dict]:
    """The two register READINGS that bound this period — the raw facts inside a derived document.

    THE INVOICE IS NOT EXPORTED, and that is the brief's own correction: *"no bill, because a bill
    IS the calculation."* What is taken from it is only what the WORLD put there — the readings,
    their type, the dates they were taken — never a figure the biller produced.

    ## THE DEFECT THIS REPLACES, FOUND BY BUILDING ITEM 2 (2026-09-02)

    The first version put `consumption_kwh` — 1888.3 for one real period — into `read_kwh`, a field
    this module DECLARES as *"what the register said"*. The register said 1937.9 and then 3826.2;
    1888.3 is the subtraction WE performed between them, and neither actual reading was exported
    at all.

    **A derived number wearing a raw name is the exact failure the unit vocabulary was written to
    catch, and the unit vocabulary did not catch it** — because the unit was not wrong. Both
    quantities are MEASURED kWh. Units separate *measured* from *computed*; they do not separate
    one measured quantity from another, and nothing here stopped a volume being filed as an index.
    Stated so the next reader does not over-trust the check: `derived_leaks` is a floor, not a
    guarantee of meaning.

    It also mattered: a validator handed a volume cannot compute a volume. Exporting both readings
    makes consumption RECONSTRUCTIBLE instead of handed over, which is the difference between
    checking our arithmetic and being told the answer.

    Verified before changing anything, across the whole book: `closing_read_kwh - opening_read_kwh`
    equals `consumption_kwh` on **11,549 of 11,549** bills, so the readings are genuine cumulative
    indices and not a second derived pair.

    ## MULTI-REGISTER METERS: SAY SO RATHER THAN GUESS

    The readings are recorded per INVOICE and the registers per BILL LINE, so with more than one
    register there is no way to say which reading belongs to which. Today every one of the 11,549
    bills is single-register — but keying to that is keying to today's answer, so an unattributable
    case returns NO reads and the period declares `volume_basis: "unattributable"`. A guess here
    would be a fabricated meter reading, which is worse than an absent one.

    SUPERSEDED IN PART, 2026-10-26: ToU invoices print two registers (50001b0b7b) and the ledger
    now records each register's own readings, so `_reads_per_register` exports those. A register
    with no readings of its own still makes the period unattributable.
    """
    registers = inv.get("registers") or [{}]
    # A one-band ToU stub is a band register with its own index, not the total register.
    if len(registers) > 1 or "opening_read_kwh" in registers[0]:
        return _reads_per_register(inv, registers)
    opening, closing = inv.get("opening_read_kwh"), inv.get("closing_read_kwh")
    if opening is None or closing is None:
        return []
    reg = registers[0]
    ident = {"register_id": reg.get("register_id", "1"),
             "register_label": reg.get("label", "Anytime")}
    return [
        # The opening reading is the PREVIOUS period's closing reading, not a separate visit. Its
        # type is that period's, not this one's, so claiming this bill's `read_type` for it would
        # attribute an actual read to an estimated period (or the reverse).
        dict(ident, read_date=inv.get("period_start"), read_kwh=opening,
             read_type=CARRIED_FORWARD),
        dict(ident, read_date=inv.get("period_end"), read_kwh=closing,
             read_type=inv.get("read_type", "U")),
    ]


def _reads_per_register(inv: dict, registers: list[dict]) -> list[dict]:
    """A multi-register meter's readings, two per register, or none if any register lacks its own.

    Each register carries its own cumulative index (the ledger's 2026-10-26 change), so the
    attribution the docstring above refused to guess is now recorded rather than inferred. One
    register without both readings makes the whole period unattributable: a partial set would let
    a reconstruction subtract some bands and miss the rest.
    """
    if any(r.get("opening_read_kwh") is None or r.get("closing_read_kwh") is None
           for r in registers):
        return []
    reads = []
    for reg in registers:
        ident = {"register_id": reg.get("register_id"), "register_label": reg.get("label")}
        reads.append(dict(ident, read_date=inv.get("period_start"),
                          read_kwh=reg["opening_read_kwh"], read_type=CARRIED_FORWARD))
        reads.append(dict(ident, read_date=inv.get("period_end"),
                          read_kwh=reg["closing_read_kwh"], read_type=inv.get("read_type", "U")))
    return reads


def raw_account(customer_id: str, record: dict) -> dict:
    """One account's raw facts, from its ledger record. Never carries a computed amount."""
    periods = []
    for inv in record.get("invoices") or []:
        reads = _reads_from_invoice(inv)
        period = {
            "period_start": inv.get("period_start"),
            "period_end": inv.get("period_end"),
            "days_in_period": inv.get("days_in_period"),
            "commodity": inv.get("commodity"),
            "mpan": inv.get("mpan"),
            "mprn": inv.get("mprn"),
            "meter_serial": inv.get("meter_serial"),
            "meter_type": inv.get("meter_type"),
            "unit_rate_p_per_kwh": inv.get("unit_rate_p_per_kwh"),
            "standing_charge_gbp_per_day": inv.get("standing_charge_gbp_per_day"),
            "vat_rate": inv.get("vat_rate"),
            "non_commodity_rate_gbp_per_mwh": inv.get("non_commodity_rate_gbp_per_mwh"),
            "document_type": inv.get("document_type"),
            "reads": reads,
        }
        # THE RATE THE ACCOUNT WAS SOLD AT, beside the rate the bill printed. The printed rate is
        # fitted to the printed line, so pricing with it proves the arithmetic and not the tariff;
        # these come from the term record. Absent on a ledger that predates them.
        if "contracted_terms" in inv:
            period["contracted_terms"] = inv["contracted_terms"]
        if inv.get("held_periods_reconciled"):
            period["held_periods_reconciled"] = inv["held_periods_reconciled"]
        # A TWO-RATE BILL HAS NO ONE RATE. The invoice's own `unit_rate_p_per_kwh` on a ToU bill
        # is the energy line over its volume (6.28 / 100.1 = 6.27p on C1/1, against Peak 12.72p and
        # Off-peak 4.21p), which is a quotient we worked out and not a rate anyone contracted. So
        # a multi-register period exports each register's printed rate and no period rate; a
        # reconstruction prices each register's own advance at its own rate (2026-10-26: 1,416
        # periods failed to rebuild for want of exactly this).
        registers = inv.get("registers") or []
        if len(registers) > 1:
            period["unit_rate_p_per_kwh"] = None
            period["registers"] = [{"register_id": r.get("register_id"),
                                    "register_label": r.get("label"),
                                    "unit_rate_p_per_kwh": r.get("unit_rate_p_per_kwh"),
                                    # Its share of the catch-up line, which its readings also span.
                                    **({"catchup_kwh": r["catchup_kwh"]}
                                       if r.get("catchup_kwh") is not None else {})}
                                   for r in registers]
        # A PERIOD ACROSS A PRICE CHANGE prints a line per contracted rate, each bounded by its own
        # two readings (the one on the change date deemed). Exported as the readings and the term
        # each line is on, never its charge, so a reconstruction subtracts each line's volume and
        # prices it at that term's rate itself.
        if inv.get("rate_lines"):
            period["rate_lines"] = [{
                "tariff_effective_from": line.get("tariff_effective_from"),
                "period_start": line.get("period_start"),
                "period_end": line.get("period_end"),
                "reads": [
                    {"read_date": line.get("period_start"), "read_kwh": line.get("opening_read_kwh"),
                     "read_type": CARRIED_FORWARD},
                    {"read_date": line.get("period_end"), "read_kwh": line.get("closing_read_kwh"),
                     "read_type": line.get("closing_read_type", "U")},
                ],
            } for line in inv["rate_lines"]]
        # OUR VOLUME IS EXPORTED BESIDE THE READINGS (2026-10-27). It was withheld where readings
        # exist, so a reconstruction could not take the shortcut; but the reconstruction reads
        # `volume_basis` and subtracts the readings whenever it says "reads"
        # (`independent_bill_validator._volume_from_reads`), so withholding protected nothing, and
        # it left INV_PERIOD_MATCHES_READS -- did we bill the advance we read? -- unaskable.
        period["consumption_kwh"] = inv.get("consumption_kwh")
        # The band registers take their share of the catch-up too (2026-10-29,
        # a_multi_register_meters_bands_add_up_to_its_total.md §3), so every register set spans it.
        if inv.get("catchup_kwh") is not None:
            period["catchup_kwh"] = inv["catchup_kwh"]
        if reads:
            period["volume_basis"] = VOLUME_FROM_READS
        elif inv.get("consumption_kwh") is not None:
            period["volume_basis"] = VOLUME_CONSUMPTION_ONLY
        else:
            period["volume_basis"] = VOLUME_UNAVAILABLE
        periods.append(period)
    payments, adjustments = _money_moved(record.get("payments") or [])
    # The government's credit as the account received it: the month's whole instalment, on the day
    # the bill applied it (`scheme_credit_month_gbp`). A ledger from before that carries only the
    # payment rows' share, read by `_money_moved` above.
    invoiced = [{"adjustment_date": inv.get("issue_date") or inv.get("period_end"),
                 "adjustment_amount_gbp": inv["scheme_credit_month_gbp"],
                 "adjustment_reason": SCHEME_CREDIT}
                for inv in record.get("invoices") or [] if inv.get("scheme_credit_month_gbp")]
    if invoiced:
        adjustments = invoiced
    return {
        "customer_id": customer_id,
        "billing_account_id": billing_account_of(customer_id),
        "segment": record.get("segment"),
        "periods": periods,
        "payments": payments,
        "adjustments": adjustments,
    }


def account_events(customer_id: str, record: dict) -> dict:
    """What the company DID on this account and when: the domain-invariant suite's second input.

    Kept out of `raw_account` on purpose. That export is the bill validator's, and a bill's due date
    is a property of the document, which the validator must not see before it rebuilds
    (`test_no_bill_document_is_exported`). The suite needs the dates to ask whether a debt stage
    opened on a bill actually overdue, or a write-off was six years old. So the same facts are a
    separate export under the same FIELDS check, and the validator never reads it.
    """
    # A bill's settlement is the day its collection succeeded, whatever the household paid (account
    # credit can cover a bill in whole); a failed or disputed collection settles nothing.
    settled = {}
    for p in record.get("payments") or []:
        if p.get("outcome", "success") == "success" and p.get("invoice_number") is not None:
            settled.setdefault(p["invoice_number"], p.get("payment_date") or p.get("date"))
    return {
        "customer_id": customer_id,
        "billing_account_id": billing_account_of(customer_id),
        "bills": [{"due_date": inv.get("due_date"), "settled_date": settled.get(inv.get("invoice_number"))}
                  for inv in record.get("invoices") or [] if inv.get("due_date")],
        "collections_journeys": [_journey_events(j) for j in record.get("collections_desk_journeys") or []],
        # The company's offer at a term's end, and its SLC 22C statement before it
        # (`company/crm/renewal_notice_register.end_of_fixed_term_statement`). A book from a run
        # that predates the statement carries no `renewal_notices` key at all, not an empty list.
        "renewal_offers": [{"offer_date": r.get("event_date"), "commodity": r.get("commodity")}
                           for r in record.get("renewal_offers") or []],
        **({"renewal_notices": [{"notice_date": r.get("notice_date"),
                                 "fixed_term_end": r.get("fixed_term_end")}
                                for r in record["renewal_notices"]]}
           if "renewal_notices" in record else {}),
    }


def _journey_events(journey: dict) -> dict:
    """A collections journey as its dated steps. Each step's overdue sum is money the company worked
    out, so it stays behind; the step, its date and a write-off's rule are what was done."""
    events = []
    for st in journey.get("stages") or []:
        e = {"event": st.get("stage"), "event_date": st.get("on")}
        if st.get("rule"):
            e["event_rule"] = st["rule"]
        events.append(e)
    return {"journey_exit": journey.get("exit"), "events": events}


def _money_moved(ledger_payments: list[dict]) -> tuple[list[dict], list[dict]]:
    """What the household paid, and what was credited to its account, from the ledger's payment rows.

    A ledger payment row is a bill's SETTLEMENT, not a receipt, so three kinds are told apart here
    (2026-10-27; on the 4ae8da9b0f ledger these were 98 payments with amount None and 218 with
    method None):
      * a row the household paid: its amount, which may be 0.00 where account credit covered the
        bill. A zero amount is NOT exported -- nothing was received -- where the old
        `amount_gbp or amount` exported it as None;
      * a FAILED or disputed collection received nothing, so it is not a payment; a mover's final
        bill paid in part exports the part it received;
      * a bill the government's credit (EBSS) settled whole: the household paid nothing and the
        account was credited, so it is an ADJUSTMENT with its reason, not a payment by nobody;
      * a bill the credit covered in part (2026-10-27): the credit is an adjustment and the
        household's payment is the rest. The ledger row's `scheme_credit_gbp` is the credit and
        its amount is what the household paid. A ledger from before that carries neither split, so
        its whole-settled rows still read their amount as the credit.
    """
    payments, adjustments = [], []
    for p in ledger_payments:
        when = p.get("payment_date") or p.get("date")
        amount = p.get("amount_gbp", p.get("amount"))
        credit = p.get("scheme_credit_gbp")
        if credit is None and p.get("method") == SCHEME_CREDIT:
            credit, amount = amount, 0.0
        if credit:
            adjustments.append({"adjustment_date": when, "adjustment_amount_gbp": credit,
                                "adjustment_reason": SCHEME_CREDIT})
        if p.get("method") == SCHEME_CREDIT:
            continue
        if p.get("outcome") in ("failed", "dispute"):
            amount = p.get("part_paid_gbp") or 0.0
        if not amount:
            continue
        payments.append({"payment_date": when, "payment_amount_gbp": amount,
                         "payment_method": p.get("method")})
    return payments, adjustments


def export_account(customer_id: str, ledger_path: Path | None = None) -> dict:
    """The raw export for one account, REFUSED if anything derived is in it.

    The check runs on the way OUT, not as a separate test somebody remembers to run. An export that
    could be produced and then found to be contaminated is an export that has already been read.
    """
    ledger = json.loads((ledger_path or LEDGER_PATH).read_text())
    record = (ledger.get("customers") or {}).get(customer_id)
    if record is None:
        raise KeyError("no such account in the ledger: {!r}".format(customer_id))
    out = raw_account(customer_id, record)
    leaks = derived_leaks(out)
    if leaks:
        raise DerivedFieldLeaked(
            "the raw export for {} carries {} derived field(s), so it was NOT produced:\n  {}"
            .format(customer_id, len(leaks), "\n  ".join(leaks)))
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("customer_id")
    ap.add_argument("--out", type=Path, help="write the export here instead of stdout")
    args = ap.parse_args(argv)
    data = export_account(args.customer_id)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
        print("wrote {} ({} period(s), {} payment(s))".format(
            args.out, len(data["periods"]), len(data["payments"])))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
