"""§4.1 OF THE BILL-VALIDATION BRIEF: "a check that refuses a derived field".

Director brief, 2026-09-02: *"If a derived figure leaks into this export, the validator confirms our
arithmetic against itself and the exercise is worthless."*

The whole exercise rests on this one property, so the check has to be the kind that cannot quietly
stop working. A DENYLIST of forbidden names is fail-open on the very next field — the first derived
quantity nobody thought of exports silently and the check reports clean. An ALLOWLIST of names is
better and still blind to a derived number assigned to a raw-sounding field.

So every field declares its UNIT, and one unit — `GBP_COMPUTED`, "money this company worked out" —
may never appear. Units say what a number IS rather than what it is called, and declaring one forces
the question at the moment a field is added: is this measured, contracted, or calculated?
"""
from __future__ import annotations

import json

import pytest

from company.billing import raw_account_export as rx


# ── the property, both directions ───────────────────────────────────────────────────────────
def test_a_clean_export_has_no_leaks():
    assert rx.derived_leaks({"customer_id": "C1", "consumption_kwh": 100.0}) == []


def test_an_undeclared_field_is_refused_whatever_it_is_called():
    """FAIL-CLOSED ON THE NEXT FIELD, which is the property a denylist cannot have.

    MUTATION: make `derived_leaks` skip unknown fields and this fails — and the first derived
    quantity nobody anticipated rides out silently.
    """
    leaks = rx.derived_leaks({"customer_id": "C1", "some_new_total_gbp": 12.0})
    assert len(leaks) == 1 and "some_new_total_gbp" in leaks[0] and "undeclared" in leaks[0]


def test_a_field_declared_as_computed_money_is_refused(monkeypatch):
    """The second way to fail: someone declares a field honestly as derived and exports it anyway.

    MUTATION: drop the `GBP_COMPUTED` branch and this fails — the declaration becomes decoration.
    """
    monkeypatch.setitem(rx.FIELDS, "total_amount_gbp", (rx.GBP_COMPUTED, "the bill's total"))
    leaks = rx.derived_leaks({"total_amount_gbp": 32.97})
    assert len(leaks) == 1 and rx.GBP_COMPUTED in leaks[0]


def test_it_finds_a_leak_nested_inside_lists_and_dicts():
    """An account export is periods inside an account and reads inside periods. A check that only
    looked at the top level would pass every real export while missing every real leak."""
    leaks = rx.derived_leaks({
        "customer_id": "C1",
        "periods": [{"consumption_kwh": 1.0, "reads": [{"read_kwh": 1.0, "vat_gbp": 0.5}]}],
    })
    assert len(leaks) == 1
    assert "periods[0].reads[0].vat_gbp" in leaks[0]


# ── the real derived fields of a real bill ──────────────────────────────────────────────────
@pytest.mark.parametrize("field", [
    "commodity_amount_gbp", "non_commodity_amount_gbp", "standing_charge_gbp", "vat_gbp",
    "total_amount_gbp", "balance_gbp", "average_unit_rate_gbp_per_mwh", "bill_shock_pct",
    "total_billed_gbp", "total_paid_gbp",
])
def test_every_computed_amount_on_a_real_bill_is_refused(field):
    """These are the actual keys in `billing_ledger.json`. Each is `rate x volume`, a sum of other
    terms, or a running balance — the exact figures a reconstruction has to produce for itself. If
    any one of them can be exported, the validator is checking our arithmetic against our own."""
    assert rx.derived_leaks({field: 1.0}), field


def test_the_forbidden_unit_is_not_one_of_the_raw_ones():
    """A unit that appeared in both sets would make the refusal unreachable."""
    assert rx.GBP_COMPUTED not in rx.RAW_UNITS


def test_every_declared_field_carries_a_raw_unit_and_a_reason():
    """The declaration is the argument. A field with a unit and no reason is a name in a list, which
    is the fail-open thing this replaced."""
    for name, declared in rx.FIELDS.items():
        unit, why = declared
        assert unit in rx.RAW_UNITS, "{} is declared {}, which may not be exported".format(name, unit)
        assert len(why) > 15, "{} declares no reason it is raw".format(name)


# ── the export itself ───────────────────────────────────────────────────────────────────────
def _ledger(tmp_path, invoices, payments=()):
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps({"customers": {"C1": {
        "segment": "resi", "invoices": list(invoices), "payments": list(payments)}}}))
    return p


def test_a_real_account_exports_and_carries_no_derived_field(tmp_path):
    ledger = _ledger(tmp_path, [{
        "period_start": "2016-01-01", "period_end": "2016-01-31", "days_in_period": 31,
        "commodity": "electricity", "consumption_kwh": 144.1, "unit_rate_p_per_kwh": 11.42,
        "standing_charge_gbp_per_day": 0.24, "read_type": "A", "meter_serial": "M1",
        "mpan": "10000", "mprn": None,
        # everything below is derived and must NOT appear in the export
        "commodity_amount_gbp": 16.46, "vat_gbp": 1.57, "total_amount_gbp": 32.97,
        "registers": [{"register_id": "1", "label": "Anytime", "consumption_kwh": 144.1,
                       "amount_gbp": 16.46}],
    }], [{"date": "2016-03-04", "amount_gbp": 32.97, "method": "direct_debit"}])
    out = rx.export_account("C1", ledger)
    assert rx.derived_leaks(out) == []
    # Checked on the KEYS, not on a substring of the rendered JSON: `payment_amount_gbp` is
    # legitimately MOVED money, and a naive `"amount_gbp" in text` matches it. A test that reads a
    # rendering rather than the structure is how a passing assertion means nothing.
    def _keys(node):
        if isinstance(node, dict):
            for k, v in node.items():
                yield k
                yield from _keys(v)
        elif isinstance(node, list):
            for item in node:
                yield from _keys(item)

    present = set(_keys(out))
    for derived in ("total_amount_gbp", "vat_gbp", "commodity_amount_gbp", "amount_gbp"):
        assert derived not in present, derived


def test_the_export_REFUSES_rather_than_producing_a_contaminated_file(tmp_path, monkeypatch):
    """The check runs on the way OUT, not as a test somebody remembers. An export that could be
    produced and only later found contaminated is an export that has already been read.

    MUTATION: return `out` without calling `derived_leaks` and this fails.
    """
    monkeypatch.setattr(rx, "raw_account", lambda cid, rec: {"customer_id": cid, "vat_gbp": 1.0})
    ledger = _ledger(tmp_path, [])
    with pytest.raises(rx.DerivedFieldLeaked) as e:
        rx.export_account("C1", ledger)
    assert "vat_gbp" in str(e.value) and "NOT produced" in str(e.value)


def test_no_bill_document_is_exported(tmp_path):
    """THE DIRECTOR'S OWN CORRECTION, on the seat's objection: the first draft of the brief listed
    "the issued bills as documents" in the raw export, two sentences after "nothing derived". A bill
    IS the calculation, and §4.3 says the validator must not see the statement before rebuilding.

    So the invoice is a source of raw facts — the reads, their type, the period — and never a thing
    that is passed through.
    """
    ledger = _ledger(tmp_path, [{
        "invoice_number": 1, "issue_date": "2016-02-05", "due_date": "2016-02-19",
        "payment_status": "paid", "period_start": "2016-01-01", "period_end": "2016-01-31",
        "days_in_period": 31, "consumption_kwh": 144.1, "total_amount_gbp": 32.97,
    }])
    flat = json.dumps(rx.export_account("C1", ledger))
    for bill_only in ("invoice_number", "issue_date", "due_date", "payment_status"):
        assert bill_only not in flat, "{} is a property of the DOCUMENT, not of the account".format(bill_only)


def test_the_contracted_rates_ARE_exported_and_the_limit_is_stated():
    """A reconstruction needs the terms the account was on, so they are exported — and that means
    the validator recomputes `rate x volume` and gets our answer whenever our RATE is wrong. It
    checks the arithmetic over the rates, not the rates.

    A real hole, and this asserts it is written down where the next reader will meet it rather than
    left to be discovered by someone trusting the reconstruction further than it can carry."""
    assert rx.FIELDS["unit_rate_p_per_kwh"][0] == rx.CONTRACTED
    assert "validates the ARITHMETIC over the rates, not the RATES" in rx.__doc__
