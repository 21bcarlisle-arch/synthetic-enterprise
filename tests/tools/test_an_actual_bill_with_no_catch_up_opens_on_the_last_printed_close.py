"""An actual bill with no estimated run to true up opens its usage line on the last printed close.

Defect this catches: SYN-2016-604g's July 2017 gas bill (4669d77ddd book) took its usage line from the
register's opening, 5001.450000000001, after June closed at 5001.45. June printed 5001.4, July's usage
started at 5001.5, and the 0.1 kWh between them went to a catch-up line a bill with no true-up never
prints. The bill read 5001.4 -> 5255.0 beside 253.5 kWh, the SLC 6.7 gate held it, and the leg had a
month-long hole: INV_PERIODS_CONTIGUOUS, INV_OPENING_IS_THE_PREVIOUS_CLOSING and the revenue row, one
gap. It was the only such bill in 8,030 on that book.
"""
import json

from saas.bill_generator import generate_bill
from tools.generate_billing_ledger import generate

#: June closes on a float that prints down (200.2); July's register opens a hair above it (prints 200.3).
CLOSES = [0.0, 200.25, 453.7835]


def _record(tmp_path, true_up_on_july=None):
    bills = []
    for n, (start, end) in enumerate((("2017-06-01", "2017-07-01"), ("2017-07-01", "2017-08-01"))):
        days = [{"customer_id": "SYN-T", "settlement_date": "%s-%02d" % (start[:7], d),
                 "consumption_kwh": 8.0, "revenue_gbp": 2.5, "standing_charge_gbp": 0.2}
                for d in range(1, 31 if n == 0 else 32)]
        bill = generate_bill("SYN-T", days, "svt", None, "resi", "electricity")
        bill["register_opening_kwh"] = CLOSES[n] if n == 0 else 200.25 + 1e-12
        bill["register_closing_kwh"] = CLOSES[n + 1]
        bill["total_consumption_kwh"] = round(bill["register_closing_kwh"]
                                              - bill["register_opening_kwh"], 4)
        bills.append(bill)
    if true_up_on_july is not None:
        bills[1]["read_true_up_kwh"] = true_up_on_july
    reads = [{"customer_id": "SYN-T", "period_end": b["period_end"], "meter_type": "smart",
              "delay_days": 1, "status": "actual", "estimated_consumption_kwh": None,
              "true_consumption_kwh": b["total_consumption_kwh"], "consecutive_estimated_count": 0}
             for b in bills]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps({"bills": bills, "meter_read_log": reads}))
    out = generate(rj, tmp_path / "l.json")
    return out["customers"]["SYN-T"]["invoices"], out["exception_queue"]


def test_the_july_bill_is_issued_and_opens_on_junes_printed_close(tmp_path):
    invoices, held = _record(tmp_path)
    assert held == []
    june, july = invoices
    assert july["opening_read_kwh"] == june["closing_read_kwh"] == 200.2
    assert [inv["consumption_kwh"] for inv in invoices] == [200.2, 253.6]


def test_a_bill_that_trues_up_an_estimated_run_still_opens_its_usage_on_the_register(tmp_path):
    """The other arm, so a fix that dropped the register's opening everywhere reds: a true-up prints
    the gap between the register and the last printed close as its catch-up line."""
    invoices, held = _record(tmp_path, true_up_on_july=0.0)
    assert held == []
    assert invoices[1]["catchup_kwh"] == 0.1
