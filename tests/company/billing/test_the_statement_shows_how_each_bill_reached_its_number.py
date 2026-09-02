"""BRIEF ITEM 2: the statement export -- the bills as issued, line by line, and the running balance.

Director brief, 2026-09-02: *"The issued bills as documents, exactly as the customer saw them;
every bill's calculation shown line by line; and the balance after each event across the account's
life ... This is what the validator's reconstruction is compared against."*

THE MISTAKE THIS MODULE MADE FIRST, because these tests exist mostly to stop it recurring. The
first draft modelled four money lines -- energy, network and policy, standing charge, VAT. Run
across the real book it reported **966 of 11,549 bills whose stored total disagreed with the sum of
its own components**, by up to +/-£1,362. Every one of those 966 was `catchup_applied`, and none of
the other 10,583 was.

The catch-up is a genuine FIFTH printed component, and `tools/generate_billing_ledger` says so in
its own comment: *"it must be in this set or the derived total would drop it -- that omission is
what sank the first F6 build."* So the finding was never "the biller's totals do not add up"; it
was "the reader is missing a term". **A residual is what a discrepancy becomes once you know a term
is missing, and only the measurement tells them apart.** With the fifth line modelled the count is
zero across all 11,549.
"""
from __future__ import annotations

import json

import pytest

from company.billing import statement_export as sx


def _inv(**over):
    base = {
        "invoice_number": 28, "issue_date": "2016-01-31", "due_date": "2016-02-14",
        "period_start": "2016-01-01", "period_end": "2016-01-31", "days_in_period": 31,
        "payment_status": "paid", "consumption_kwh": 1937.9, "unit_rate_p_per_kwh": 2.446,
        "commodity_amount_gbp": 47.40, "standing_charge_gbp_per_day": 0.22,
        "standing_charge_gbp": 6.82, "non_commodity_amount_gbp": 17.44, "vat_gbp": 3.58,
        "total_amount_gbp": 75.24,
    }
    base.update(over)
    return base


# ── it reports what was ISSUED, and never repairs it on the way out ─────────────────────────
def test_the_total_is_the_one_that_was_issued_not_a_sum_of_the_lines():
    """THE LOAD-BEARING PROPERTY. If this summed its own lines to produce the total, a bill whose
    stored total disagreed with its own parts would be silently corrected on export and the
    validator would be handed a repaired copy of the thing it was sent to check.

    MUTATION: return `parts_sum` as `total_amount_gbp` and this fails.
    """
    doc = sx.bill_document(_inv(total_amount_gbp=99.99))
    assert doc["total_amount_gbp"] == 99.99
    assert doc["parts_sum_gbp"] == 75.24
    assert doc["internal_discrepancy_gbp"] == 24.75


def test_a_bill_that_agrees_with_itself_carries_no_discrepancy():
    """The pass branch has to be reachable, or the field is a constant."""
    doc = sx.bill_document(_inv())
    assert doc["parts_sum_gbp"] == doc["total_amount_gbp"] == 75.24
    assert doc["internal_discrepancy_gbp"] is None


def test_a_discrepancy_is_REPORTED_and_never_raised():
    """THE DELIBERATE ASYMMETRY WITH THE RAW EXPORT. `raw_account_export.export_account` RAISES on
    contamination, because a contaminated raw export makes the exercise worthless. Here the
    opposite holds: an internally inconsistent bill is exactly the defect we are hunting, so
    refusing would hide the finding inside an exception."""
    doc = sx.bill_document(_inv(total_amount_gbp=1.0))       # no exception
    assert doc["internal_discrepancy_gbp"] is not None


# ── THE FIFTH LINE, and the false claim it prevents ─────────────────────────────────────────
def test_a_catchup_bill_itemises_the_restatement():
    """MUTATION: drop the `catchup_applied` branch from `bill_lines` and this fails -- and so does
    the whole-book control below, with 966 bills wrongly accused."""
    doc = sx.bill_document(_inv(
        total_amount_gbp=131.24, catchup_applied=True, catchup_adjustment_gbp=56.00,
        catchup_period_start="2015-07-01", catchup_period_end="2015-12-31",
        catchup_direction="undercharge", catchup_raw_delta_gbp=61.0,
        catchup_written_off_gbp=5.0))
    labels = [ln["label"] for ln in doc["lines"]]
    assert len(labels) == 5 and "Catch-up" in labels[4]
    assert doc["internal_discrepancy_gbp"] is None, "the fifth component closes the total"


def test_an_ordinary_bill_has_no_restatement_line():
    """Present only where it applies: a zero catch-up line on every bill would train a reader to
    skip it, the same argument as `conflicts-resolved` on the merge receipt."""
    assert len(sx.bill_document(_inv())["lines"]) == 4


def test_the_restatement_is_marked_as_one_and_not_as_a_period_charge():
    """A reconstruction from meter reads must reproduce a catch-up by RE-BILLING the earlier
    periods, never by adding a line to this bill. Marking it with the other four would invite
    exactly that, and the reconstruction would agree with us for the wrong reason."""
    doc = sx.bill_document(_inv(catchup_applied=True, catchup_adjustment_gbp=1.0,
                                total_amount_gbp=76.24))
    assert doc["lines"][4]["kind"] == sx.RESTATEMENT
    assert all(ln["kind"] != sx.RESTATEMENT for ln in doc["lines"][:4])


def test_the_writeoff_reaches_the_statement():
    """Ofgem SLC 31A caps what a supplier may recover on an undercharge. Money barred from recovery
    is the difference between what the meter says a customer used and what they may lawfully be
    asked for -- it belongs on their statement, not only in our ledger."""
    doc = sx.bill_document(_inv(catchup_applied=True, catchup_adjustment_gbp=1.0,
                                catchup_written_off_gbp=12.5, total_amount_gbp=76.24))
    assert doc["lines"][4]["inputs"]["catchup_written_off_gbp"] == 12.5


def test_a_line_with_no_amount_makes_the_check_UNAVAILABLE_not_failed():
    """"I could not check" and "it does not add up" are different answers, and summing only the
    priced lines would report the missing one as a discrepancy -- the exact false claim this
    module already made once.

    MUTATION: sum the priced lines regardless and this fails with a £56 "discrepancy".
    """
    doc = sx.bill_document(_inv(total_amount_gbp=131.24, catchup_applied=True,
                                catchup_adjustment_gbp=None))
    assert doc["parts_sum_gbp"] is None
    assert doc["internal_discrepancy_gbp"] is None
    assert doc["unpriced_lines"] and "Catch-up" in doc["unpriced_lines"][0]


# ── the rates the document does not record are DECLARED, never back-solved ──────────────────
@pytest.mark.parametrize("label,field", [
    ("Network and policy costs", "non_commodity_rate_gbp_per_mwh"),
    ("VAT", "vat_rate"),
])
def test_a_rate_the_bill_does_not_record_is_declared_unavailable(label, field):
    """THE TEMPTATION IS `rate = amount / volume`, AND IT MUST NOT BE TAKEN. A rate derived from
    the answer reproduces the answer by identity, so the line would validate itself and the
    validator would be checking arithmetic it had been handed both sides of.

    This is also where the design gets its teeth. Brief §3 worries that a reconstruction fed our
    own rates checks our arithmetic and not our rates -- true of energy and standing charge. It is
    NOT true of these two, because we cannot hand over a rate: the validator has to fetch the
    statutory VAT rate and the published levy rates from the record itself.
    """
    line = next(ln for ln in sx.bill_lines(_inv()) if ln["label"] == label)
    assert line["inputs"][field] == sx.UNAVAILABLE
    assert line["kind"] == sx.NEEDS_EXTERNAL_RATE
    assert line["inputs"]["why"]


def test_a_reconstructible_line_names_every_input_it_stands_on():
    """When the reconstruction disagrees, "the bill is £2.10 out" is not actionable and "the
    standing charge was billed for 30 days over a 31-day period" is the answer. Same rule as the
    HEAD-red register: a discrepancy with no named term is a number to worry about."""
    line = next(ln for ln in sx.bill_lines(_inv()) if ln["label"] == "Standing charge")
    assert line["inputs"] == {"days_in_period": 31, "standing_charge_gbp_per_day": 0.22}
    assert line["kind"] == sx.RECONSTRUCTIBLE


# ── the running balance ─────────────────────────────────────────────────────────────────────
def _record(invoices, payments):
    return {"segment": "resi", "invoices": list(invoices), "payments": list(payments)}


def test_a_failed_payment_is_shown_and_moves_nothing():
    """MEASURED ON ACCOUNT C1g: 36 payments of which 2 failed, and the sum of ALL 36 is
    £1,922.48 -- equal to the total billed, to the penny -- while the account actually owes
    £70.85. A reconstruction counting ATTEMPTS instead of RECEIPTS lands exactly on zero and looks
    perfect. That coincidence is why this is a test and not a comment.

    MUTATION: move the balance on a failed payment and the closing balance goes to 0.00.
    """
    events = sx.account_events(_record(
        [_inv(issue_date="2016-01-31", total_amount_gbp=100.0)],
        [{"payment_date": "2016-02-14", "amount_gbp": 60.0, "outcome": "success",
          "method": "direct_debit", "invoice_number": 28},
         {"payment_date": "2016-02-15", "amount_gbp": 40.0, "outcome": "failed",
          "method": "direct_debit", "invoice_number": 28}]))
    assert [e["kind"] for e in events] == ["bill", "payment", "payment"]
    assert events[-1]["balance_after_gbp"] == -40.0
    failed = events[-1]
    assert failed["amount_gbp"] == 40.0, "the customer saw it; a statement must show it"
    assert failed["moves_balance_gbp"] == 0.0
    assert "FAILED" in failed["detail"]


def test_a_bill_lands_before_a_payment_made_the_same_day():
    """The tie-break is a CONVENTION, not a discovery, so it is asserted rather than left to fall
    out of a sort: a running balance is order-dependent and a reader comparing two reconstructions
    needs to know somebody chose."""
    events = sx.account_events(_record(
        [_inv(issue_date="2016-02-01", total_amount_gbp=10.0)],
        [{"payment_date": "2016-02-01", "amount_gbp": 10.0, "outcome": "success",
          "method": "card", "invoice_number": 28}]))
    assert [e["kind"] for e in events] == ["bill", "payment"]
    assert [e["balance_after_gbp"] for e in events] == [-10.0, 0.0]


def test_the_sign_convention_is_the_ledgers_own():
    """Negative means the customer owes. It reads backwards to anyone expecting "balance
    outstanding", which is exactly why it is pinned: the statement has to be comparable with the
    ledger's own `balance_gbp` without a reader guessing which way round either is."""
    events = sx.account_events(_record(
        [_inv(issue_date="2016-01-31", total_amount_gbp=50.0)], []))
    assert events[0]["balance_after_gbp"] == -50.0


# ── sealing, so §4.3 is enforceable rather than asserted ────────────────────────────────────
def test_the_digest_is_a_property_of_content_and_not_of_key_order():
    """A digest that moved when nothing moved would be retired after its first false alarm."""
    a = {"customer_id": "C1", "bills": [], "events": []}
    b = {"events": [], "bills": [], "customer_id": "C1"}
    assert sx.statement_digest(a) == sx.statement_digest(b)


def test_the_digest_moves_when_a_figure_moves():
    """MUTATION: hash only the customer id and this fails -- and the seal would certify nothing."""
    a = {"customer_id": "C1", "closing_balance_gbp": -70.85}
    b = {"customer_id": "C1", "closing_balance_gbp": -70.84}
    assert sx.statement_digest(a) != sx.statement_digest(b)


# ── against the real book ───────────────────────────────────────────────────────────────────
def _real_ledger():
    if not sx.LEDGER_PATH.exists():
        pytest.skip("no billing ledger on this box")
    return json.loads(sx.LEDGER_PATH.read_text())


def test_every_issued_bill_agrees_with_the_sum_of_its_own_printed_components():
    """THE FIRST INDEPENDENT STATEMENT THIS BRIEF PRODUCES, and its limit in the same breath.

    It says every bill's total equals the sum of the components printed on it. It says NOTHING
    about whether those components are right -- that is items 3 and 4. An internal check is a floor
    under the document, not a validation of the arithmetic behind it.

    A dated population floor, because a scanning control over an emptied ledger passes quietly
    (`population_floors_and_split_seams`): 11,549 bills over 251 accounts on 2026-09-02.
    """
    ledger = _real_ledger()
    bills = 0
    accused: list[str] = []
    unpriced = 0
    for cid, rec in (ledger.get("customers") or {}).items():
        for inv in rec.get("invoices") or []:
            bills += 1
            doc = sx.bill_document(inv)
            if doc["unpriced_lines"]:
                unpriced += 1
            if doc["internal_discrepancy_gbp"] is not None:
                accused.append("{}/{} out by {}".format(
                    cid, inv.get("invoice_number"), doc["internal_discrepancy_gbp"]))
    assert bills >= 11_000, "only {} bills: this control would pass on an emptied ledger".format(bills)
    assert not accused, (
        "{} of {} bills do not equal the sum of their own printed components. Before reporting "
        "that as a billing defect, check whether a COMPONENT IS MISSING FROM THIS READER -- the "
        "first draft accused 966 bills and every one was a catch-up whose fifth line it had not "
        "modelled. First 5: {}".format(len(accused), bills, accused[:5]))
    assert unpriced == 0, "{} bills carry a component with no recorded amount".format(unpriced)


def test_the_event_walk_closes_where_the_ledger_says_it_closes():
    """Two independent routes to one number: a walk over every bill and payment, against the
    ledger's own stored `balance_gbp`. They agree on all 251 accounts.

    This one is worth more than it looks: it is the only place the failed-payment rule, the sign
    convention and the event ordering are checked together against a figure nobody wrote for this
    test's benefit."""
    ledger = _real_ledger()
    accounts = 0
    disagree = []
    for cid, rec in (ledger.get("customers") or {}).items():
        accounts += 1
        doc = sx.statement(cid, rec)
        if doc["balance_discrepancy_gbp"] is not None:
            disagree.append((cid, doc["closing_balance_gbp"], doc["ledger_balance_gbp"]))
    assert accounts >= 200, "only {} accounts: an emptied ledger would pass".format(accounts)
    assert not disagree, "closing balance disagrees with the ledger on: {}".format(disagree[:5])
