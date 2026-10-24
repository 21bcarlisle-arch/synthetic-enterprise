"""A time-of-use invoice prints each register's kWh, charge and rate (SLC 22A.3).

Defect this catches: a two-rate bill printed one `Anytime` register at the blended rate, so the
household could not check either of the rates it contracted for. Item 6 of
SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md; K8 page
docs/market_research/a_tou_tariff_needs_the_households_choice_not_its_meter.md.

Mutations, each reds this file: the writer stamping both bands as peak; `tou_registers` returning
(None, None) always; the estimate not scaling the band fields; `_printed_registers` returning None.
"""
import datetime as dt
import json

from company.billing.monthly_bill_assembly import _estimated_settlement_records
from saas.bill_generator import generate_bill
from simulation.hedged_settlement import run_hedged_term
from simulation.settlement_daily import fold_to_days
from tools.generate_billing_ledger import _printed_registers, generate

PEAK, OFFPEAK, FLAT = 400.0, 220.0, 280.0


def _prices():
    out, d = [], dt.date(2023, 3, 1)
    while d < dt.date(2023, 4, 1):
        out += [{"settlementDate": d.isoformat(), "settlementPeriod": p, "systemSellPrice": 120.0}
                for p in range(1, 49)]
        d += dt.timedelta(days=1)
    return out


def _bill(tou_rates, pass_through=False, ratio=None):
    recs = run_hedged_term("SYN-T", "2023-03-01", "2023-04-01", FLAT, 120.0, 0.8, 0.0,
                           lambda ds: [0.25] * 48, _prices(), tou_rates=tou_rates,
                           pass_through=pass_through)
    rows = fold_to_days(recs)
    if ratio is not None:
        rows = _estimated_settlement_records(rows, ratio, "electricity")
    return generate_bill("SYN-T", rows, "fixed_1yr", None, "resi", "electricity")


def _all_in_p(bill, reg):
    nc_per_kwh = bill["non_commodity_amount_gbp"] / bill["total_consumption_kwh"]
    return 100 * (reg["commodity_amount_gbp"] / reg["consumption_kwh"] + nc_per_kwh)


def test_the_partition_split_single_and_withheld_are_each_reachable():
    """A guard that never splits passes every refusal test; this asserts all three outcomes occur."""
    tou, flat, passthrough = _bill((PEAK, OFFPEAK)), _bill(None), _bill((PEAK, OFFPEAK), True)
    assert len(tou["registers"]) == 2 and "tou_registers_withheld" not in tou
    assert "registers" not in flat and "tou_registers_withheld" not in flat
    assert "registers" not in passthrough and "unit charge" in passthrough["tou_registers_withheld"]


def test_each_register_recovers_its_contracted_rate_and_the_registers_sum_to_the_bill():
    for ratio in (None, 0.9):
        bill = _bill((PEAK, OFFPEAK), ratio=ratio)
        peak, off = bill["registers"]
        assert (peak["label"], off["label"]) == ("Peak", "Off-peak")
        assert abs(_all_in_p(bill, peak) - PEAK / 10) < 1e-9
        assert abs(_all_in_p(bill, off) - OFFPEAK / 10) < 1e-9
        assert abs(peak["consumption_kwh"] + off["consumption_kwh"]
                   - bill["total_consumption_kwh"]) < 1e-9
        assert abs(peak["commodity_amount_gbp"] + off["commodity_amount_gbp"]
                   - bill["commodity_amount_gbp"]) < 1e-9


def test_printed_registers_foot_exactly_to_the_printed_lines():
    bill = _bill((PEAK, OFFPEAK))
    kwh, gbp = round(bill["total_consumption_kwh"], 1), round(bill["commodity_amount_gbp"], 2)
    printed = _printed_registers(bill["registers"], kwh, gbp)
    assert [r["register_id"] for r in printed] == ["1", "2"]
    assert round(sum(r["consumption_kwh"] for r in printed), 1) == kwh
    assert round(sum(r["amount_gbp"] for r in printed), 2) == gbp
    assert printed[0]["unit_rate_p_per_kwh"] > printed[1]["unit_rate_p_per_kwh"]
    assert _printed_registers(None, kwh, gbp) is None


def test_the_ledger_invoice_carries_both_registers(tmp_path):
    bill = _bill((PEAK, OFFPEAK))
    run = {"bills": [bill], "per_customer_behavioral": {}, "churned_billing_accounts": []}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run))
    inv = generate(rj, tmp_path / "l.json")["customers"]["SYN-T"]["invoices"][0]
    assert [r["label"] for r in inv["registers"]] == ["Peak", "Off-peak"]
    assert round(sum(r["amount_gbp"] for r in inv["registers"]), 2) == inv["commodity_amount_gbp"]
    assert round(sum(r["consumption_kwh"] for r in inv["registers"]), 1) == inv["consumption_kwh"]
