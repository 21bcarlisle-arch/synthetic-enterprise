"""INV_OVERDUE_WITHIN_BALANCE's second leg reads a level direct debit leg on its schedule.

The defect this names: the row asked every household for "a bill unpaid past its due date". On a level
leg no bill is due by direct debit, so a journey opened on a returned instalment read "nothing overdue"
(70 of 71 breaches on the 298149a1fc book), while a level household dunned with nothing defaulted on
could pass on a bill the instalment had not covered. What is owed on a level account is a collection
defaulted on (Ofgem, letter of 20 Sep 2011, App. 2 para 2.8; payments_and_direct_debit_2026-10-25.md,
"What is owed"), or the debit an ended scheme left, once demanded ("Leaving level direct debit with a
debit"). The second defect, found on the 9d7dcfc19c control: reading the HOUSEHOLD as level when one leg
is, which breached 23 journeys opened on the other leg's unpaid bill. Each leg is read on its own terms.
The third, found on the 78f82e4242 book (5 -> 60): a leg whose last month the world settled on its face
reads as having LEFT level, and the bill reading calls its scheme's debit paid, because every bill the
scheme sat on was met by its collection. 58 journeys the desk opened on that debit's closing statement,
28 days after leaving, read "nothing overdue". A leaver owes the debit once the statement falls due.
"""
from tools import domain_invariant_runner as runner

OPENED = "2020-03-20"


def _journey(opened=OPENED):
    return {"events": [{"event": "missed_payment", "event_date": opened},
                       {"event": "cured", "event_date": "2020-06-20"}]}


def _level_leg(cid, *, returned=False, made_good=0.0, collects_after=True, final_face=40.0):
    """Monthly GBP 40 level instalments on the 10th, Jan to Mar 2020, each meeting that month's bill.
    `returned` returns March's. `collects_after` keeps collecting in April. `final_face` is March's bill."""
    bills = [{"invoice_number": n, "issue_date": "2020-0{}-01".format(m), "due_date": "2020-0{}-15".format(m),
              "total_amount_gbp": final_face if m == 3 else 40.0, "document_type": "bill"}
             for n, m in ((1, 1), (2, 2), (3, 3))]
    pays = [{"invoice_number": n, "payment_date": "2020-0{}-10".format(m), "amount_gbp": 40.0,
             "method": "direct_debit", "outcome": "failed" if (returned and m == 3) else "success",
             "level_dd": True} for n, m in ((1, 1), (2, 2), (3, 3))]
    if collects_after:
        bills.append({"invoice_number": 4, "issue_date": "2020-04-01", "due_date": "2020-04-15",
                      "total_amount_gbp": 40.0, "document_type": "bill"})
        pays.append({"invoice_number": 4, "payment_date": "2020-04-10", "amount_gbp": 40.0,
                     "method": "direct_debit", "outcome": "success", "level_dd": True})
    if made_good:
        pays.append({"invoice_number": None, "payment_date": "2020-03-15", "amount_gbp": made_good,
                     "method": "card", "outcome": "success"})
    settled = {p["invoice_number"]: p["payment_date"] for p in pays if p["outcome"] == "success"}
    return _acct(cid, bills, pays, settled)


def _bill_leg(cid, *, feb_unpaid):
    """A leg paying its own bills on receipt; February's is never paid when `feb_unpaid`."""
    bills = [{"invoice_number": 10 + m, "issue_date": "2020-0{}-01".format(m), "due_date": "2020-0{}-15".format(m),
              "total_amount_gbp": 30.0, "document_type": "bill"} for m in (1, 2)]
    pays = [{"invoice_number": 10 + m, "payment_date": "2020-0{}-14".format(m), "amount_gbp": 30.0,
             "method": "standard_credit", "outcome": "success"} for m in (1, 2) if not (feb_unpaid and m == 2)]
    return _acct(cid, bills, pays, {p["invoice_number"]: p["payment_date"] for p in pays})


def _acct(cid, bills, pays, settled, opened=OPENED):
    raw = {"billing_account_id": "H", "bill_record": {"invoices": bills, "payments": pays},
           "events": {"bills": [{"due_date": b["due_date"], "settled_date": settled.get(b["invoice_number"])}
                                for b in bills],
                      "collections_journeys": [_journey(opened)] if cid == "H" else []}}
    return runner.Account(cid, raw)


def _sides(*legs):
    t = runner.ev_overdue_within_balance(None, list(legs))
    assert t.checked == 1
    return [b["side"] for b in t.breaches]


def test_every_branch_of_the_level_reading_can_be_taken():
    """The partition first: a level leg that owes, one that owes nothing, a bill leg that owes, one that
    does not. A reader that refused everything, or passed everything, fails here."""
    assert _sides(_level_leg("H", returned=True)) == []
    assert _sides(_level_leg("H")) == ["nothing defaulted on"]
    assert _sides(_bill_leg("H", feb_unpaid=True)) == []
    assert _sides(_bill_leg("H", feb_unpaid=False)) == ["nothing overdue"]


def test_a_returned_instalment_is_owed_until_it_is_made_good():
    assert _sides(_level_leg("H", returned=True, made_good=25.0)) == []
    assert _sides(_level_leg("H", returned=True, made_good=40.0)) == ["nothing defaulted on"]


def test_a_level_leg_is_never_owed_on_a_bill_face():
    """March's bill is GBP 90 against a GBP 40 instalment that was taken: a seasonal debit, which the
    schedule recovers. The bill reading would call it settled anyway; the point is that a level leg in
    debit with every collection taken has defaulted on nothing."""
    assert _sides(_level_leg("H", final_face=90.0)) == ["nothing defaulted on"]


def test_an_ended_scheme_owes_its_debit_and_not_its_credit():
    """No level collection after the opening: the scheme has ended. March's final bill of GBP 90 against
    a GBP 40 instalment leaves GBP 50 demanded. A final bill of GBP 30 leaves the leg in credit."""
    assert _sides(_level_leg("H", collects_after=False, final_face=90.0)) == []
    assert _sides(_level_leg("H", collects_after=False, final_face=30.0)) == ["nothing defaulted on"]


def test_each_leg_is_read_on_its_own_terms():
    """The 9d7dcfc19c control's 23: a household whose gas is on level DD and whose electricity pays on
    receipt owes when the electricity bill is unpaid, however its level leg reads."""
    assert _sides(_level_leg("H"), _bill_leg("Hx", feb_unpaid=True)) == []
    assert _sides(_level_leg("H"), _bill_leg("Hx", feb_unpaid=False)) == ["nothing defaulted on"]
    assert _sides(_level_leg("H", returned=True), _bill_leg("Hx", feb_unpaid=False)) == []


def _leaver(opened, *, jan_feb_face=60.0):
    """GBP 40 level instalments meet January's and February's bills (GBP 60 each, so a GBP 40 debit when
    `jan_feb_face` is 60); March's bill, issued 1 Mar, is settled on its face on 14 Mar, off the schedule.
    The leg left level on 1 Mar; its closing statement falls due on 29 Mar."""
    bills = [{"invoice_number": n, "issue_date": "2020-0{}-01".format(m), "due_date": "2020-0{}-15".format(m),
              "total_amount_gbp": jan_feb_face if m < 3 else 30.0, "document_type": "bill"}
             for n, m in ((1, 1), (2, 2), (3, 3))]
    pays = [{"invoice_number": n, "payment_date": "2020-0{}-10".format(m), "amount_gbp": 40.0,
             "method": "direct_debit", "outcome": "success", "level_dd": True} for n, m in ((1, 1), (2, 2))]
    pays.append({"invoice_number": 3, "payment_date": "2020-03-14", "amount_gbp": 30.0,
                 "method": "direct_debit", "outcome": "success"})
    return _acct("H", bills, pays, {p["invoice_number"]: p["payment_date"] for p in pays}, opened)


def test_a_leaver_owes_its_schemes_debit_once_the_closing_statement_falls_due():
    """The partition over the leaver: owed after the term, not within it, and never on a credit. A
    reader that dropped the clause, the term or the debit test fails one leg here."""
    assert _sides(_leaver("2020-03-30")) == []
    assert _sides(_leaver("2020-03-29")) == ["nothing overdue"]
    assert _sides(_leaver("2020-03-30", jan_feb_face=35.0)) == ["nothing overdue"]
