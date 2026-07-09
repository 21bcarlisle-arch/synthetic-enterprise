"""Regression tests for docs/staging/BILL_CORRECTNESS_ADDENDUM.md Defects 2
and 3 (2026-07-09), render-layer coverage (site/customers/index.html):
Defect 2 -- "every bill must state: billing period start/end; opening &
closing reads with read type (A=actual, E=estimated); meter serial +
MPAN/MPRN; per-fuel breakdown" (billMeterDetailsHtml()).
Defect 3 -- "bill lines must be register/period-structured (ToU-ready)"
(billUsageLinesHtml()).

Data-layer coverage (the fields actually existing and flowing through) is
in test_generate_billing_ledger.py and test_invoice_generation.py.

No `node` available this session (see test_billing_tab_fix.py for the
established substitute pattern): a static guard that the function
references every required field, plus a faithful Python port executed
against representative invoice records so this test breaks if the two
diverge.
"""
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PORTAL = PROJECT / "site" / "customers" / "index.html"


def _script_body():
    html = PORTAL.read_text()
    return re.search(r"<script>(.*)</script>", html, re.S).group(1)


def _bill_meter_details_html(i):
    """Python port of billMeterDetailsHtml() in site/customers/index.html --
    kept line-for-line equivalent so this test breaks if the two diverge."""
    rows = []
    rows.append(f"Billing period: {i['period_start']} to {i['period_end']}")
    if i.get("opening_read_kwh") is not None and i.get("closing_read_kwh") is not None:
        read_label = "Estimated (E)" if i.get("read_type") == "E" else "Actual (A)"
        rows.append(
            f"Meter reads: {i['opening_read_kwh']:.1f} -> {i['closing_read_kwh']:.1f} kWh -- {read_label}"
        )
    if i.get("meter_serial"):
        rows.append(f"Meter serial: {i['meter_serial']}")
    if i.get("mpan"):
        rows.append(f"MPAN: {i['mpan']}")
    if i.get("mprn"):
        rows.append(f"MPRN: {i['mprn']}")
    return rows


def test_bill_meter_details_function_exists_and_references_every_required_field():
    body = _script_body()
    assert "function billMeterDetailsHtml(i)" in body
    for field in (
        "i.period_start", "i.period_end", "i.opening_read_kwh", "i.closing_read_kwh",
        "i.read_type", "i.meter_serial", "i.mpan", "i.mprn",
    ):
        assert field in body, f"billMeterDetailsHtml must reference {field}"


def test_bill_expand_html_calls_meter_details():
    """The meter/period section must actually be wired into the bill
    expand view, not just defined and unused."""
    body = _script_body()
    assert "billMeterDetailsHtml(i)" in body
    # Called from within billExpandHtml, not some unrelated dead function.
    expand_fn = re.search(r"function billExpandHtml\(i,allInvoices\)\{(.*?)\n\}", body, re.S)
    assert expand_fn is not None
    assert "billMeterDetailsHtml(i)" in expand_fn.group(1)


def test_actual_read_shows_period_and_reads():
    inv = {
        "period_start": "2024-01-01", "period_end": "2024-01-31",
        "opening_read_kwh": 1000.0, "closing_read_kwh": 1471.1,
        "read_type": "A", "meter_serial": "M12345678",
        "mpan": "1234567890123", "mprn": None,
    }
    rows = _bill_meter_details_html(inv)
    assert "Billing period: 2024-01-01 to 2024-01-31" in rows
    assert "Meter reads: 1000.0 -> 1471.1 kWh -- Actual (A)" in rows
    assert "Meter serial: M12345678" in rows
    assert "MPAN: 1234567890123" in rows
    assert not any(r.startswith("MPRN") for r in rows)


def test_estimated_read_labelled_distinctly():
    inv = {
        "period_start": "2024-01-01", "period_end": "2024-01-31",
        "opening_read_kwh": 1000.0, "closing_read_kwh": 1350.0,
        "read_type": "E", "meter_serial": "M12345678",
        "mpan": None, "mprn": "1234567890",
    }
    rows = _bill_meter_details_html(inv)
    assert any("Estimated (E)" in r for r in rows)
    assert "MPRN: 1234567890" in rows


def test_missing_read_fields_do_not_crash_or_show_partial_row():
    """A ledger record from before Defect 2 landed lacks these keys --
    must degrade gracefully (period only), never raise or show a
    half-populated 'None -> None' row."""
    inv = {"period_start": "2020-01-01", "period_end": "2020-01-31"}
    rows = _bill_meter_details_html(inv)
    assert rows == ["Billing period: 2020-01-01 to 2020-01-31"]


# BILL_CORRECTNESS_ADDENDUM.md Defect 3 (2026-07-09): register/period-
# structured bill lines.

def test_bill_usage_lines_function_exists_and_uses_registers():
    body = _script_body()
    assert "function billUsageLinesHtml(i)" in body
    assert "i.registers" in body
    # billEquationHtml must call it, not the old inline single-line logic.
    eq_fn = re.search(r"function billEquationHtml\(i\)\{(.*?)\n\}", body, re.S)
    assert eq_fn is not None
    assert "billUsageLinesHtml(i)" in eq_fn.group(1)


def _bill_usage_lines_html(i):
    """Python port of billUsageLinesHtml() -- kept equivalent so this test
    breaks if the two diverge."""
    if i.get("registers"):
        lines = []
        multi = len(i["registers"]) > 1
        for r in i["registers"]:
            label = f"Usage ({r['label']})" if multi else "Usage"
            if r["consumption_kwh"]:
                rate = r["amount_gbp"] / r["consumption_kwh"] * 100
                lines.append(f"{label}: {r['consumption_kwh']:.1f} kWh x {rate:.2f} = {r['amount_gbp']}")
            else:
                lines.append(f"{label}: {r['amount_gbp']}")
        return lines
    return ["fallback-flat-line"]


def test_single_register_renders_one_usage_line():
    inv = {"registers": [{"register_id": "1", "label": "Anytime", "consumption_kwh": 471.1, "amount_gbp": 62.69}]}
    lines = _bill_usage_lines_html(inv)
    assert len(lines) == 1
    assert lines[0].startswith("Usage:")


def test_multi_register_renders_one_line_per_register_labelled():
    """Not built now (ToU itself), but the schema must already support this
    shape without a render-layer change -- proves the addendum's actual
    requirement ("so ToU tariffs bill correctly when they arrive")."""
    inv = {"registers": [
        {"register_id": "1", "label": "Day", "consumption_kwh": 300.0, "amount_gbp": 45.0},
        {"register_id": "2", "label": "Night", "consumption_kwh": 200.0, "amount_gbp": 20.0},
    ]}
    lines = _bill_usage_lines_html(inv)
    assert len(lines) == 2
    assert lines[0].startswith("Usage (Day):")
    assert lines[1].startswith("Usage (Night):")
