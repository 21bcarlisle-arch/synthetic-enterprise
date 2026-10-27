"""A meter register keeps one id and one cumulative index for the life of its serial.

Defect this catches: ToU registers were numbered by position on the bill, so "register 1" was the
total index on a single-rate bill and the Peak index on the next ToU bill. On 67a893e749, 66 serials
read 18,568.6 and then 2,140.6 on "register 1", and every one of the suite's 29 backwards
actual-to-actual reads (`INV_READ_MONOTONIC`) was on them. A one-band ToU stub printed its band's
label on the total index. Breach class 3 of
SEAT_FINDING_THE_BLIND_INVARIANT_SUITE_ON_THE_67A893E749_BOOK_..._2026-10-26.md.

The register COUNT may change under one serial: a ToU tariff is a contract "regardless of the
metering equipment employed" (SLC 28AD; docs/market_research/a_tou_tariff_needs_the_households_choice_not_its_meter.md),
and a smart or HH meter is reconfigured for it, not exchanged. So the control is keyed to the
property that physics fixes (one register, one id, an index that never runs backwards), not to a
count.

Mutations, each reds this file: `_printed_registers` numbering by position again; the one-band stub
reading the total index; the export ignoring a stub register's own reads.
"""
import datetime as dt
import json
from collections import defaultdict

from company.billing.raw_account_export import raw_account
from saas.bill_generator import generate_bill
from simulation.hedged_settlement import run_hedged_term
from simulation.settlement_daily import fold_to_days
from simulation.tou_periods import is_peak_period
from tools.generate_billing_ledger import generate

PEAK, OFFPEAK, FLAT = 400.0, 220.0, 280.0


def _prices(start, end):
    out, d = [], start
    while d < end:
        out += [{"settlementDate": d.isoformat(), "settlementPeriod": p, "systemSellPrice": 120.0}
                for p in range(1, 49)]
        d += dt.timedelta(days=1)
    return out


def _bill(start, end, tou_rates, offpeak_only=False):
    def shape(ds):
        return [0.0 if offpeak_only and is_peak_period(ds, p) else 0.25 for p in range(1, 49)]
    recs = run_hedged_term("SYN-T", start.isoformat(), end.isoformat(), FLAT, 120.0, 0.8, 0.0,
                           shape, _prices(start, end), tou_rates=tou_rates)
    return generate_bill("SYN-T", fold_to_days(recs), "fixed_1yr", None, "resi", "electricity")


def _book(tmp_path):
    """Single rate, two-rate, single rate, then a two-rate stub with use in one band only."""
    d = dt.date
    bills = [_bill(d(2023, 1, 1), d(2023, 2, 1), None),
             _bill(d(2023, 2, 1), d(2023, 3, 1), (PEAK, OFFPEAK)),
             _bill(d(2023, 3, 1), d(2023, 4, 1), None),
             _bill(d(2023, 4, 1), d(2023, 4, 3), (PEAK, OFFPEAK), offpeak_only=True),
             _bill(d(2023, 4, 3), d(2023, 5, 1), (PEAK, OFFPEAK))]
    run = {"bills": bills, "per_customer_behavioral": {}, "churned_billing_accounts": []}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run))
    record = generate(rj, tmp_path / "l.json")["customers"]["SYN-T"]
    return record, raw_account("SYN-T", record)


def test_the_book_reaches_one_register_two_registers_and_a_one_band_stub(tmp_path):
    """A test of identity over a book that never changes count would pass vacuously."""
    record, _ = _book(tmp_path)
    labels = [[r["label"] for r in inv["registers"]] for inv in record["invoices"]]
    assert labels == [["Anytime"], ["Peak", "Off-peak"], ["Anytime"], ["Off-peak"],
                      ["Peak", "Off-peak"]]


def test_one_register_id_names_one_register_on_a_serial(tmp_path):
    _, raw = _book(tmp_path)
    names = defaultdict(set)
    for p in raw["periods"]:
        for r in p["reads"]:
            names[(p["meter_serial"], r["register_id"])].add(r["register_label"])
    assert names and all(len(v) == 1 for v in names.values()), dict(names)


def test_no_register_index_runs_backwards(tmp_path):
    _, raw = _book(tmp_path)
    reads = defaultdict(list)
    for p in raw["periods"]:
        assert p["reads"], p["period_start"]
        for r in p["reads"]:
            reads[(p["meter_serial"], r["register_id"])].append((r["read_date"], r["read_kwh"]))
    for key, rs in reads.items():
        rs.sort()
        assert all(b[1] >= a[1] for a, b in zip(rs, rs[1:])), (key, rs)


def test_each_period_reconstructs_its_volume_from_its_own_registers(tmp_path):
    record, raw = _book(tmp_path)
    for inv, p in zip(record["invoices"], raw["periods"]):
        by_reg = defaultdict(list)
        for r in p["reads"]:
            by_reg[r["register_id"]].append(r["read_kwh"])
        advance = sum(max(v) - min(v) for v in by_reg.values())
        assert abs(advance - inv["consumption_kwh"]) <= 0.1 * len(by_reg), (p["period_start"],)
