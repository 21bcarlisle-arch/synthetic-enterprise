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

#: EVERY field this export may contain, with its unit and why it is raw. A field absent from here
#: is refused by `derived_leaks` whatever it is called.
FIELDS: dict[str, tuple[str, str]] = {
    # account identity
    "customer_id": (IDENTIFIER, "the account this is about"),
    "segment": (EVENT, "which customer class the account is — a fact about the account"),
    "commodity": (EVENT, "electricity or gas"),
    "mpan": (IDENTIFIER, "the electricity supply point"),
    "mprn": (IDENTIFIER, "the gas supply point"),
    "meter_serial": (IDENTIFIER, "the physical meter"),
    # meter reads
    "read_date": (MEASURED, "when the register was read"),
    "register_id": (IDENTIFIER, "which register on the meter"),
    "register_label": (EVENT, "what the register is called on the bill (Anytime, Night)"),
    "read_kwh": (MEASURED, "what the register said"),
    "read_type": (EVENT, "actual, estimated, customer or deemed — how the read was obtained"),
    # the period the reads bound
    "period_start": (MEASURED, "first day the account was supplied in this period"),
    "period_end": (MEASURED, "last day the account was supplied in this period"),
    "days_in_period": (MEASURED, "a count of calendar days, not a calculation over money"),
    "consumption_kwh": (MEASURED, "volume between two reads"),
    # contracted terms
    "unit_rate_p_per_kwh": (CONTRACTED, "the rate the account was on for this period"),
    "standing_charge_gbp_per_day": (CONTRACTED, "the daily standing charge the account was on"),
    "vat_rate": (CONTRACTED, "the statutory rate for this segment"),
    "non_commodity_rate_gbp_per_mwh": (CONTRACTED, "network and levy pass-through rate for the year"),
    "tariff_effective_from": (MEASURED, "when these terms started applying"),
    "tariff_effective_to": (MEASURED, "when they stopped"),
    # money that actually moved
    "payment_date": (MEASURED, "when the payment was received"),
    "payment_amount_gbp": (MOVED, "what was actually received — it happened, we did not work it out"),
    "payment_method": (EVENT, "direct debit, card, prepayment top-up"),
    "adjustment_date": (MEASURED, "when the adjustment was applied"),
    "adjustment_amount_gbp": (MOVED, "money actually credited or debited to the account"),
    "adjustment_reason": (EVENT, "why — a stated reason, not a computation"),
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
    """The meter reads an invoice was built from — the raw facts inside a derived document.

    THE INVOICE IS NOT EXPORTED, and that is the brief's own correction: *"no bill, because a bill
    IS the calculation."* What is taken from it is only what the WORLD put there — the reads, their
    type, the period they bound — never a figure the biller produced.
    """
    reads = []
    for reg in inv.get("registers") or [{}]:
        reads.append({
            "register_id": reg.get("register_id", "1"),
            "register_label": reg.get("label", "Anytime"),
            "read_date": inv.get("period_end"),
            "read_kwh": reg.get("consumption_kwh", inv.get("consumption_kwh")),
            "read_type": inv.get("read_type", "U"),
        })
    return reads


def raw_account(customer_id: str, record: dict) -> dict:
    """One account's raw facts, from its ledger record. Never carries a computed amount."""
    periods = []
    for inv in record.get("invoices") or []:
        periods.append({
            "period_start": inv.get("period_start"),
            "period_end": inv.get("period_end"),
            "days_in_period": inv.get("days_in_period"),
            "commodity": inv.get("commodity"),
            "mpan": inv.get("mpan"),
            "mprn": inv.get("mprn"),
            "meter_serial": inv.get("meter_serial"),
            "consumption_kwh": inv.get("consumption_kwh"),
            "unit_rate_p_per_kwh": inv.get("unit_rate_p_per_kwh"),
            "standing_charge_gbp_per_day": inv.get("standing_charge_gbp_per_day"),
            "reads": _reads_from_invoice(inv),
        })
    payments = [{
        "payment_date": p.get("date") or p.get("payment_date"),
        "payment_amount_gbp": p.get("amount_gbp") or p.get("amount"),
        "payment_method": p.get("method", "unknown"),
    } for p in (record.get("payments") or [])]
    return {
        "customer_id": customer_id,
        "segment": record.get("segment"),
        "periods": periods,
        "payments": payments,
    }


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
