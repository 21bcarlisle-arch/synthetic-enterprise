#!/usr/bin/env python3
"""THE STATEMENT EXPORT — what we CLAIM: the bills as issued, line by line, and the running balance.

Director brief, 2026-09-02 (`DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02`), work item 2:

    "The statement export -- what we claim. The issued bills as documents, exactly as the customer
     saw them; every bill's calculation shown line by line; and the balance after each event across
     the account's life -- the transaction history a real supplier gives a customer, and a bill that
     shows how it reached its number. This is what the validator's reconstruction is compared
     against."

This is the MIRROR of `raw_account_export`. That one refuses everything derived; this one carries
almost nothing else, because the derived figures ARE the claim under test. The two are meant to be
read together: the validator gets the raw export, rebuilds, and only then is shown this.

---

## IT REPORTS WHAT WAS ISSUED. IT NEVER RECOMPUTES.

The single most important property here, and the easiest to lose. If this module computed
`total_amount_gbp` by summing the lines it renders, then a bill whose stored total DISAGREES with
its own components would be invisible -- the export would quietly repair the document on the way
out and the validator would be handed a corrected copy of the thing it was sent to check. Every
figure below is read from the ledger as issued. Where a total and its own parts disagree, that
disagreement is REPORTED as a field.

## AND IT REPORTS RATHER THAN REFUSES — the deliberate asymmetry with the raw export

`export_account` in the raw module RAISES on contamination, because a contaminated raw export makes
the whole exercise worthless and there is nothing to learn from it. Here the opposite holds: an
internally inconsistent bill is exactly the defect this project is trying to find, so refusing to
export it would hide the finding inside an exception. Report, and let item 4's comparison file it.

## THE INPUTS THE DOCUMENT DOES NOT RECORD, AND WHY THAT IS THE STRONGEST PART

Two of the four money lines cannot name all their inputs from the issued document:

  * the NON-COMMODITY line: the bill stores `non_commodity_amount_gbp` but not the levy rate it
    used (`saas/bill_generator` takes it from `non_commodity_rate(commodity, segment, year)`);
  * the VAT line: the bill stores `vat_gbp` but not the rate.

The tempting move is to back-solve -- `rate = amount / volume` -- and it must not be made: a rate
derived FROM the answer reproduces the answer by identity, and the line would validate itself. So
both are declared `UNAVAILABLE` with the input named.

That is not a weakness in this export, it is where the validation gets its teeth. Section 3 of the
brief worries that a reconstruction fed our own rates checks our arithmetic and not our rates --
true of the energy and standing-charge lines. It is NOT true of these two, precisely because we
cannot hand over a rate: the validator has to obtain the statutory VAT rate and the published levy
rates from the record itself (`docs/domain_artefact_library/`), and those two lines are then
genuinely externally checked. **The lines we can least explain are the ones we can best validate.**

## SEALING, so §4.3 can be enforced rather than promised

    "the validator must not see the statement before rebuilding"

An instruction like that is unfalsifiable after the fact. `statement_digest()` gives it an
artefact: the comparison records the reconstruction's digest BEFORE opening the statement, so a
reconstruction that had seen the answer can be told from one that had not.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
LEDGER_PATH = PROJECT_DIR / "docs" / "state" / "billing_ledger.json"

#: A money line whose inputs the issued document records in full. The validator can reproduce it
#: arithmetically -- and only arithmetically; see the module docstring on what that is worth.
RECONSTRUCTIBLE = "RECONSTRUCTIBLE"
#: A money line whose rate the document does not record. The validator must fetch it from the
#: published record, which is the only place in this design where a RATE is independently checked.
NEEDS_EXTERNAL_RATE = "NEEDS_EXTERNAL_RATE"
#: Read straight off the document with no formula of its own.
AS_ISSUED = "AS_ISSUED"
#: A correction to bills ALREADY ISSUED, folded into this bill's total. A reconstruction from meter
#: reads must reproduce it by re-billing the earlier periods, never by adding a line -- so it is
#: called out separately rather than sitting among the four period charges it is not one of.
RESTATEMENT = "RESTATEMENT"

UNAVAILABLE = "UNAVAILABLE"

#: A BILL IS MIXED-BASIS, AND A RECONSTRUCTION THAT DOES NOT KNOW THAT WILL REPORT A FALSE DEFECT
#: ON EVERY CATCH-UP BILL. The four period charges are NET; the VAT line is computed over them; the
#: catch-up correction is GROSS.
#:
#: Established rather than assumed (2026-09-02). All 966 catch-up bills compute VAT on a base that
#: EXCLUDES the correction, which looks like a VAT undercharge — on `C1g`/41, £3.22 charged where
#: 5% of the corrected supply would be £4.79. It is not one. `monthly_bill_assembly._resolve_catchup`
#: builds the delta as `sum(true_total_amount_gbp - total_amount_gbp)` over the estimated run, and
#: `total_amount_gbp` is the VAT-INCLUSIVE total, so the correction already carries its own VAT.
#: Charging VAT on it again would double-count.
#:
#: I nearly filed that as a finding across 966 bills. The check that stopped it was asking what the
#: quantity IS before differencing it — and this constant exists so the next reader does not have to
#: repeat the trace to find out.
VAT_INCLUSIVE = "vat_inclusive"

#: Pennies. Two figures agreeing to less than this are the same figure rendered twice; the ledger
#: stores 2dp, so anything at or above one penny is a real disagreement and not float noise.
PENNY = 0.005


def _line(label, basis, inputs, amount, kind):
    return {"label": label, "basis": basis, "inputs": inputs,
            "amount_gbp": amount, "kind": kind}


def bill_lines(inv: dict) -> list[dict]:
    """The calculation of one bill, line by line, each naming the inputs it stands on.

    WHY NAMED INPUTS AND NOT JUST AMOUNTS. When the reconstruction disagrees, "the bill is £2.10
    out" is not actionable and "the standing charge was billed for 30 days over a 31-day period"
    is the answer. This is the same rule the HEAD-red register was built on: a discrepancy with no
    named term is a number to worry about rather than a thing to fix.
    """
    days = inv.get("days_in_period")
    kwh = inv.get("consumption_kwh")
    rate_p = inv.get("unit_rate_p_per_kwh")
    sc_day = inv.get("standing_charge_gbp_per_day")
    lines = [
        _line("Energy", "consumption_kwh x unit_rate_p_per_kwh / 100",
              {"consumption_kwh": kwh, "unit_rate_p_per_kwh": rate_p},
              inv.get("commodity_amount_gbp"), RECONSTRUCTIBLE),
        _line("Standing charge", "days_in_period x standing_charge_gbp_per_day",
              {"days_in_period": days, "standing_charge_gbp_per_day": sc_day},
              inv.get("standing_charge_gbp"), RECONSTRUCTIBLE),
        _line("Network and policy costs", "consumption_kwh / 1000 x levy rate for the year",
              # NOT BACK-SOLVED FROM THE ANSWER. See the module docstring: a rate derived from the
              # amount reproduces the amount by identity and the line would validate itself.
              {"consumption_kwh": kwh, "non_commodity_rate_gbp_per_mwh": UNAVAILABLE,
               "why": "the issued bill does not record the levy rate it used"},
              inv.get("non_commodity_amount_gbp"), NEEDS_EXTERNAL_RATE),
        _line("VAT", "vat_rate x (energy + network and policy + standing charge)",
              {"vat_rate": UNAVAILABLE,
               "why": "the issued bill does not record the rate; the statutory rate is a "
                      "published fact the validator must fetch rather than be handed"},
              inv.get("vat_gbp"), NEEDS_EXTERNAL_RATE),
    ]
    if inv.get("catchup_applied"):
        # THE FIFTH PRINTED COMPONENT, AND THE FIRST DRAFT OF THIS MODULE DROPPED IT.
        #
        # `tools/generate_billing_ledger` says so in its own comment -- *"a genuine FIFTH printed
        # component on a back-billing bill (it is added to the total outside the four category
        # fields), so it must be in this set or the derived total would drop it -- that omission
        # is what sank the first F6 build."* I reproduced the omission it warns about, and
        # measured the result before believing it: **966 of 11,549 bills** appeared to disagree
        # with their own totals, by up to +/-£1,362, and **every single one** of them was
        # `catchup_applied` -- 966 of 966, and none of the other 10,583.
        #
        # Reported as "the biller's totals do not add up" that would have been a false claim about
        # the billing engine, published off a defect in the reader. The residual was not a
        # discrepancy; it was a TERM I had not modelled. Those are different findings and only
        # the measurement distinguishes them.
        lines.append(_line(
            "Catch-up correction (bills already issued, restated)",
            "a real read resolved a run of estimates; the correction for "
            "{}..{} is folded into THIS bill's total, VAT-INCLUSIVE".format(
                inv.get("catchup_period_start"), inv.get("catchup_period_end")),
            {"vat_basis": VAT_INCLUSIVE,
             "catchup_direction": inv.get("catchup_direction"),
             "catchup_periods_covered": inv.get("catchup_periods_covered"),
             "catchup_raw_delta_gbp": inv.get("catchup_raw_delta_gbp"),
             # Ofgem SLC 31A caps what a supplier may recover on an undercharge. Money barred from
             # recovery belongs on the customer's statement: it is the difference between what the
             # meter says they used and what they may lawfully be asked for.
             "catchup_written_off_gbp": inv.get("catchup_written_off_gbp")},
            inv.get("catchup_adjustment_gbp"), RESTATEMENT))
    return lines


def bill_document(inv: dict) -> dict:
    """One issued bill as the customer saw it, with its calculation and its own internal check.

    `total_amount_gbp` is the STORED total, never the sum of the lines above -- see the module
    docstring. `parts_sum_gbp` is that sum, carried beside it so a document that disagrees with
    itself says so on its face.
    """
    lines = bill_lines(inv)
    parts = [ln["amount_gbp"] for ln in lines if isinstance(ln["amount_gbp"], (int, float))]
    # A LINE WITH NO AMOUNT MAKES THE CHECK UNAVAILABLE, AND THAT MUST BE SAID. Summing the lines
    # that do have amounts would compare a partial sum against a full total and report the missing
    # line as a discrepancy -- which is precisely the false claim this module already made once
    # (see `bill_lines`). "I could not check" and "it does not add up" are different answers.
    unpriced = [ln["label"] for ln in lines if not isinstance(ln["amount_gbp"], (int, float))]
    parts_sum = round(sum(parts), 2) if not unpriced else None
    issued_total = inv.get("total_amount_gbp")
    discrepancy = None
    if parts_sum is not None and isinstance(issued_total, (int, float)):
        diff = round(issued_total - parts_sum, 2)
        if abs(diff) >= PENNY:
            discrepancy = diff
    return {
        "unpriced_lines": unpriced,
        "invoice_number": inv.get("invoice_number"),
        "issue_date": inv.get("issue_date"),
        "due_date": inv.get("due_date"),
        "period_start": inv.get("period_start"),
        "period_end": inv.get("period_end"),
        "payment_status": inv.get("payment_status"),
        "lines": lines,
        "total_amount_gbp": issued_total,          # AS ISSUED. Never recomputed.
        "parts_sum_gbp": parts_sum,
        "internal_discrepancy_gbp": discrepancy,   # None when the document agrees with itself
        "kind": AS_ISSUED,
    }


#: Two events on one day need an order, and the choice is arbitrary rather than discovered, so it
#: is declared here instead of falling out of a sort. A supplier issues a bill and then receives
#: money against it, so on a tie the bill lands first. State it, because a running balance is
#: order-dependent and a reader comparing two reconstructions needs to know this was a convention.
_EVENT_ORDER = {"bill": 0, "payment": 1, "adjustment": 2}


def account_events(record: dict) -> list[dict]:
    """Every money event across the account's life, in order, with the balance after each.

    SIGN CONVENTION, taken from the ledger's own `balance_gbp` and not invented here: a bill moves
    the balance DOWN and a payment moves it UP, so a negative balance means the customer owes. It
    reads backwards to anyone expecting "balance outstanding", which is exactly why it is written
    down rather than left to be inferred from an example.

    A FAILED PAYMENT IS AN EVENT AND MOVES NOTHING. It appears -- the customer saw it fail, and a
    statement that hid it would not be the transaction history a supplier gives -- but it does not
    touch the balance. Measured on account C1g: 36 payments, 2 failed, and the sum of ALL 36
    (£1,922.48) equals the total billed to the penny while the account actually owes £70.85. A
    reconstruction that counted attempts instead of receipts would land exactly on zero and look
    perfect.
    """
    events: list[dict] = []
    for inv in record.get("invoices") or []:
        events.append({
            "date": inv.get("issue_date"), "kind": "bill",
            "reference": inv.get("invoice_number"),
            "amount_gbp": inv.get("total_amount_gbp"),
            "moves_balance_gbp": -(inv.get("total_amount_gbp") or 0.0),
            "detail": "bill issued for {} to {}".format(
                inv.get("period_start"), inv.get("period_end")),
        })
    for pay in record.get("payments") or []:
        ok = pay.get("outcome") == "success"
        amount = pay.get("amount_gbp") or 0.0
        events.append({
            "date": pay.get("payment_date"), "kind": "payment",
            "reference": pay.get("invoice_number"),
            "amount_gbp": amount,
            "moves_balance_gbp": amount if ok else 0.0,
            "outcome": pay.get("outcome"),
            "detail": "payment by {} {}".format(
                pay.get("method"), "received" if ok else "FAILED -- balance unchanged"),
        })
    events.sort(key=lambda e: (e["date"] or "", _EVENT_ORDER.get(e["kind"], 9),
                               e["reference"] if isinstance(e["reference"], int) else 0))
    balance = 0.0
    for e in events:
        balance = round(balance + e["moves_balance_gbp"], 2)
        e["balance_after_gbp"] = balance
    return events


def statement(customer_id: str, record: dict) -> dict:
    """One account's statement: what we issued, how each bill was reached, and the balance after
    every event -- with the ledger's own totals beside ours so a disagreement is on the face of it.
    """
    bills = [bill_document(inv) for inv in (record.get("invoices") or [])]
    events = account_events(record)
    closing = events[-1]["balance_after_gbp"] if events else 0.0
    ledger_balance = record.get("balance_gbp")
    balance_discrepancy = None
    if isinstance(ledger_balance, (int, float)) and abs(closing - ledger_balance) >= PENNY:
        balance_discrepancy = round(closing - ledger_balance, 2)
    return {
        "customer_id": customer_id,
        "segment": record.get("segment"),
        # `issued_bills` AND NOT `bills`, AND THE REASON IS NOT STYLE. `tools/wall_channel_census`
        # enumerates channel F -- a business-side module reading a published run-output key -- by
        # matching STRING LITERALS in subscripts against that artefact's top-level keys, which it
        # states plainly is a lower bound and cannot make more precise. `bills` is one of those
        # keys, so `doc["bills"]` on a dict of our OWN making reads to that control as a wall
        # crossing, and the commit is refused. It is a PHANTOM: this module reads the billing
        # ledger, never the run output.
        #
        # The honest fix is to rename, not to rule and freeze the crossing. Freezing would put a
        # crossing that does not exist into a shrink-only baseline, and a baseline carrying
        # phantoms cannot be read for the real ones -- the next author has no way to tell which
        # entries mean anything. Measured 2026-09-02: 134 frozen channel-F crossings, exactly one
        # of them on `bills` (`saas/reporting/annual_report.py`, which genuinely reads it), and
        # none at all in `company/billing`. Keep it that way.
        "issued_bills": bills,
        "events": events,
        "closing_balance_gbp": closing,
        # The ledger's OWN headline figures, carried unaltered. Two independent routes to one
        # number, and where they differ this says so rather than picking one.
        "ledger_balance_gbp": ledger_balance,
        "ledger_total_billed_gbp": record.get("total_billed_gbp"),
        "ledger_total_paid_gbp": record.get("total_paid_gbp"),
        "balance_discrepancy_gbp": balance_discrepancy,
        "issued_bills_with_internal_discrepancy": [
            b["invoice_number"] for b in bills if b["internal_discrepancy_gbp"] is not None],
    }


def statement_digest(doc: dict) -> str:
    """A stable content hash of a statement, so §4.3 can be ENFORCED rather than asserted.

    *"The validator must not see the statement before rebuilding"* is unfalsifiable after the fact.
    With this, the comparison records the reconstruction's digest first; a reconstruction produced
    after the statement was opened cannot then be presented as one produced before.

    `sort_keys` so the digest is a property of the CONTENT and not of dict insertion order -- a
    digest that moved when nothing moved would be worse than none, because the first false alarm
    would retire it.
    """
    return hashlib.sha256(
        json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def export_statement(customer_id: str, ledger_path: Path | None = None) -> dict:
    ledger = json.loads((ledger_path or LEDGER_PATH).read_text())
    record = (ledger.get("customers") or {}).get(customer_id)
    if record is None:
        raise KeyError("no such account in the ledger: {!r}".format(customer_id))
    return statement(customer_id, record)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("customer_id")
    ap.add_argument("--out", type=Path, help="write the statement here instead of stdout")
    ap.add_argument("--digest", action="store_true", help="print only the sealing digest")
    args = ap.parse_args(argv)
    doc = export_statement(args.customer_id)
    if args.digest:
        print(statement_digest(doc))
        return 0
    text = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
        print("wrote {} ({} bill(s), {} event(s), closing {:.2f}, digest {})".format(
            args.out, len(doc["issued_bills"]), len(doc["events"]),
            doc["closing_balance_gbp"], statement_digest(doc)[:12]))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
