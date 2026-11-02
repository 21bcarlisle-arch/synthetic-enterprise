"""A gas read is a volume, and the bill converts it (N11 of the fifth cold read).

Page: docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md (C1-C3). The defects
named here: a gas meter whose read carries kWh and no volume; a supplier that bills the settled kWh
whatever the meter's volume says; a world meter that advances twice when a period is asked for two
reads; a printed register in kWh with no CV or correction factor beside it; and a blind row that
passes every record, or none.
"""

from __future__ import annotations

import calendar
import json
from dataclasses import dataclass

import pytest

from company.billing import gas_volume_conversion as G
from company.billing import monthly_bill_assembly as M
from company.billing.raw_account_export import _reads_from_invoice, derived_leaks
from simulation.live_population import GAS_CORRECTION_FACTOR, GAS_CV_FACTOR
from simulation.meter_reads import MeterReadEvent, SimulatedReadFeed
from tools import domain_invariant_runner as runner
from tools.generate_billing_ledger import generate as generate_ledger

ROW = "INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF"


# ── the conversion ─────────────────────────────────────────────────────────────────────────

def test_the_conversion_is_govuks_worked_arithmetic():
    """GOV.UK's steps: volume x 1.02264 x CV / 3.6; an imperial meter's hcf x 2.83 first."""
    assert G.kwh_from_volume(100.0, "m3", 39.5) == pytest.approx(100 * 1.02264 * 39.5 / 3.6)
    assert G.kwh_from_volume(1.0, "hcf", 39.5) == pytest.approx(2.8317 * 1.02264 * 39.5 / 3.6, rel=1e-4)
    assert G.volume_from_kwh(G.kwh_from_volume(123.4, "hcf"), "hcf") == pytest.approx(123.4)
    with pytest.raises(ValueError):
        G.kwh_from_volume(1.0, "kWh")


def test_the_period_cv_is_truncated_not_rounded():
    """R5: 'any amount of less than 0.1 megajoules per cubic metre shall be ignored'."""
    assert G.period_calorific_value([39.59, 39.59]) == 39.5
    assert G.period_calorific_value([39.5, 39.5, 39.5]) == 39.5
    assert G.period_calorific_value([39.2, 39.3]) == 39.2


def test_the_world_and_the_supplier_hold_the_same_stand_in():
    """Until G1 both sides use one CV and factor; if either moves alone, every gas bill moves."""
    assert G.STAND_IN_CALORIFIC_VALUE_MJ_PER_M3 == GAS_CV_FACTOR
    assert G.GAS_VOLUME_CORRECTION_FACTOR == GAS_CORRECTION_FACTOR
    assert G.conversion_terms()["calorific_value_basis"] == G.FIXED_STAND_IN


# ── the world's meter ──────────────────────────────────────────────────────────────────────

def _event(cid, period_end, status="actual"):
    return MeterReadEvent(cid, period_end, "traditional", 0, status)


def _feed(*customers):
    feed = SimulatedReadFeed()
    for c in customers:
        feed.meter_type_for(c)
    return feed


def test_an_actual_gas_read_carries_the_meters_volume_and_advances_once_per_period():
    feed = _feed({"customer_id": "G1g", "commodity": "gas"})
    per_kwh = 3.6 / (GAS_CV_FACTOR * GAS_CORRECTION_FACTOR)
    first = feed._gas_index(_event("G1g", "2023-01-31"), 1000.0)
    # A second read asked for the same period (an instructed visit, a final read) does not advance it.
    again = feed._gas_index(_event("G1g", "2023-01-31"), 1000.0)
    unread = feed._gas_index(_event("G1g", "2023-02-28", "estimated"), 500.0)
    second = feed._gas_index(_event("G1g", "2023-03-31"), 250.0)
    assert (first.read_unit, first.register_volume) == ("m3", pytest.approx(1000 * per_kwh))
    assert again.register_volume == pytest.approx(first.register_volume)
    # The meter turned through the unread month; only no one saw it.
    assert unread.register_volume is None and unread.read_unit is None
    assert second.register_volume == pytest.approx(1750 * per_kwh)


def test_an_imperial_meter_reads_hundreds_of_cubic_feet_and_electricity_reads_no_volume():
    feed = _feed({"customer_id": "G2g", "commodity": "gas", "gas_meter_imperial": True},
                 {"customer_id": "E1", "commodity": "electricity"})
    imperial = feed._gas_index(_event("G2g", "2023-01-31"), 1000.0)
    assert imperial.read_unit == "hcf"
    assert G.kwh_from_volume(imperial.register_volume, "hcf") == pytest.approx(1000.0)
    assert feed._gas_index(_event("E1", "2023-01-31"), 1000.0).register_volume is None


# ── the supplier's bill ────────────────────────────────────────────────────────────────────

@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int
    read_unit: str | None = None
    register_volume: float | None = None


class _VolumeFeed:
    """Every month read; the meter's index is `scale` times the settled energy as volume."""

    def __init__(self, scale=1.0, unit="m3"):
        self.scale, self.unit, self.volume = scale, unit, 0.0

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        self.volume += G.volume_from_kwh(true_kwh * self.scale, self.unit)
        return _Read("actual", None, 0, self.unit, self.volume)

    final_read_for = instructed_read_for = read_for


def _gas_month(cid, month, kwh):
    days = calendar.monthrange(2023, month)[1]
    return [{"customer_id": cid, "settlement_date": f"2023-{month:02d}-{d:02d}",
             "settlement_period": 1, "consumption_kwh": kwh / days,
             "unit_rate_gbp_per_mwh": 60.0, "revenue_gbp": kwh / days / 1000 * 60.0 + 0.3,
             "gas_standing_charge_gbp": 0.3, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
            for d in range(1, days + 1)]


def _bills(feed):
    rows = _gas_month("C1g", 1, 1500.0) + _gas_month("C1g", 2, 1200.0)
    return M.build_monthly_bills(rows, feed)


def test_a_gas_bill_bills_the_converted_volume_and_says_what_it_converted_at():
    """Both legs reached first: a meter agreeing with the settled kWh moves nothing, and one that
    reads 10% more is billed 10% more. A supplier billing the settled kWh fails the second."""
    agree, more = _bills(_VolumeFeed()), _bills(_VolumeFeed(scale=1.1))
    assert [b["total_consumption_kwh"] for b in agree] == pytest.approx([1500.0, 1200.0])
    assert [b["total_consumption_kwh"] for b in more] == pytest.approx([1650.0, 1320.0])
    assert more[0]["commodity_amount_gbp"] == pytest.approx(agree[0]["commodity_amount_gbp"] * 1.1)
    for b in agree:
        assert b["calorific_value_basis"] == G.FIXED_STAND_IN and b["gas_read_unit"] == "m3"
        assert G.kwh_from_volume(b["register_closing_volume"] - b["register_opening_volume"], "m3") \
            == pytest.approx(b["total_consumption_kwh"])


# ── the printed record and the blind row ──────────────────────────────────────────────────

def _invoice(opening_kwh, closing_kwh, opening_v, closing_v, **kw):
    return dict({"period_start": "2023-01-01", "period_end": "2023-01-31", "commodity": "gas",
                 "read_type": "A", "opening_read_kwh": opening_kwh, "closing_read_kwh": closing_kwh,
                 "read_unit": "m3", "imperial_meter": False, "opening_read_volume": opening_v,
                 "closing_read_volume": closing_v, "calorific_value_mj_per_m3": 39.5,
                 "calorific_value_basis": G.FIXED_STAND_IN, "correction_factor": 1.02264}, **kw)


def test_the_raw_export_carries_the_volume_beside_each_reading_and_nothing_undeclared():
    reads = _reads_from_invoice(_invoice(0.0, 1122.0, 0.0, 100.0))
    assert [(r["read_unit"], r["read_volume"]) for r in reads] == [("m3", 0.0), ("m3", 100.0)]
    assert not derived_leaks({"reads": reads, "calorific_value_mj_per_m3": 39.5,
                              "calorific_value_basis": G.FIXED_STAND_IN, "correction_factor": 1.02264,
                              "imperial_meter": False})


def _book(*periods):
    return {"G": {"segment": "resi", "periods": [dict(p, reads=_reads_from_invoice(p), **{
        k: p[k] for k in ("imperial_meter", "calorific_value_mj_per_m3", "calorific_value_basis",
                          "correction_factor") if k in p}) for p in periods]}}


def _grade(*periods):
    return runner.run([{"id": ROW}], _book(*periods))[0]


def test_every_leg_of_the_gas_volume_row_is_reachable():
    """MUTATION: the blind row. A kWh-only register breaches, a converted one is clean, a kWh that is
    not the converted volume breaches, and an imperial register converts through 2.8317."""
    kwh = round(100.0 * 1.02264 * 39.5 / 3.6, 1)
    hcf_kwh = round(G.kwh_from_volume(35.0, "hcf", 39.5), 1)
    legs = {
        "kwh_register": _grade({"period_start": "2023-01-01", "period_end": "2023-01-31",
                                "commodity": "gas", "read_type": "A",
                                "opening_read_kwh": 0.0, "closing_read_kwh": kwh}),
        "converted": _grade(_invoice(0.0, kwh, 0.0, 100.0)),
        "not_converted": _grade(_invoice(0.0, kwh + 5.0, 0.0, 100.0)),
        "imperial": _grade(_invoice(0.0, hcf_kwh, 0.0, 35.0, read_unit="hcf", imperial_meter=True)),
        "imperial_flag_wrong": _grade(_invoice(0.0, hcf_kwh, 0.0, 35.0, read_unit="hcf")),
    }
    assert {k: r["status"] for k, r in legs.items()} == {
        "kwh_register": "BREACHED", "converted": "CLEAN", "not_converted": "BREACHED",
        "imperial": "CLEAN", "imperial_flag_wrong": "BREACHED"}


# ── the meter against the run (both blind readers, pairs 1 and 2, 2 Nov) ───────────────────

class _ScriptedFeed(_VolumeFeed):
    """Reads as scripted per month: None is an unread month; a number is the kWh the meter's
    advance since the last actual read converts to."""

    def __init__(self, script):
        super().__init__()
        self.script, self.run = list(script), 0

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        advance = self.script.pop(0)
        if advance is None:
            self.run += 1
            return _Read("estimated", None, self.run)
        self.run = 0
        self.volume += G.volume_from_kwh(advance, self.unit)
        return _Read("actual", None, 0, self.unit, self.volume)

    final_read_for = instructed_read_for = read_for


def test_a_meter_reading_below_the_run_is_a_credit_on_the_run_never_a_negative_month():
    """MUTATION: month = converted - run's settled use, unbounded. Three months settled at 1000 kWh go
    unread, then the meter's advance over them and May converts to 2500 kWh while May settled 200:
    the month billed -500 kWh. Now May bills nothing and the run's true-up is the meter's 2500 less
    the estimates billed, a credit. Both legs reached: a meter above the run still bills the month."""
    rows = (_gas_month("C2g", 1, 1000.0) + _gas_month("C2g", 2, 1000.0) + _gas_month("C2g", 3, 1000.0)
            + _gas_month("C2g", 4, 1000.0) + _gas_month("C2g", 5, 200.0))
    low = M.build_monthly_bills(rows, _ScriptedFeed([1000.0, None, None, None, 2500.0]))
    high = M.build_monthly_bills(rows, _ScriptedFeed([1000.0, None, None, None, 3300.0]))
    assert [b["billing_basis"] for b in low][1:4] == ["estimated"] * 3
    run_billed = sum(b["total_consumption_kwh"] for b in low[1:4])
    may = low[4]
    assert all(b["total_consumption_kwh"] >= 0 for b in low)
    assert may["total_consumption_kwh"] == pytest.approx(0.0, abs=0.01)
    assert may["read_true_up_kwh"] == pytest.approx(2500.0 - run_billed, abs=0.01)
    assert run_billed > 2500.0  # the estimates ran above the meter, so the credit leg is reached
    assert may["catchup_direction"] == "overcharge" and may["catchup_adjustment_gbp"] < 0
    # The meter above the run: the month bills the advance less the run's settled 3000.
    assert high[4]["total_consumption_kwh"] == pytest.approx(300.0, abs=0.01)
    assert high[4]["read_true_up_kwh"] == pytest.approx(3000.0 - run_billed, abs=0.01)


def test_a_month_that_settled_nothing_bills_the_meters_advance():
    """MUTATION: the `settled kWh > 0` guard. February settled 0 kWh, the meter advanced 100: the bill
    charged 0 and the printed kWh no longer matched the printed volume advance."""
    rows = _gas_month("C3g", 1, 1000.0) + _gas_month("C3g", 2, 0.0)
    jan, feb = M.build_monthly_bills(rows, _ScriptedFeed([1000.0, 100.0]))
    assert feb["total_consumption_kwh"] == pytest.approx(100.0)
    assert feb["commodity_amount_gbp"] > 0
    assert G.kwh_from_volume(feb["register_closing_volume"] - feb["register_opening_volume"], "m3") \
        == pytest.approx(feb["total_consumption_kwh"])


def test_volume_from_kwh_refuses_a_unit_no_gas_register_reads():
    """MUTATION: any unit other than m3 was taken as hcf, so 100 'kWh' came back in hcf."""
    assert G.volume_from_kwh(G.kwh_from_volume(10.0, "m3"), "m3") == pytest.approx(10.0)
    with pytest.raises(ValueError):
        G.volume_from_kwh(100.0, "kWh")


def test_the_printed_imperial_flag_is_the_metering_record_not_the_reads_unit(monkeypatch, tmp_path):
    """MUTATION: the ledger printed imperial_meter = (unit == 'hcf'), from the unit leg (c) checks it
    against, so leg (c) could not fail. The flag is now the account's gas_meter_imperial."""
    monkeypatch.setattr(M, "get_customer", lambda cid: {"customer_id": cid, "commodity": "gas",
                                                    "gas_meter_imperial": True})
    (bill,) = M.build_monthly_bills(_gas_month("C4g", 1, 1000.0), _VolumeFeed(unit="m3"))
    assert bill["gas_read_unit"] == "m3" and bill["gas_meter_imperial"] is True
    # What the ledger prints is the record, so the record and the read's unit can disagree on paper.
    run = tmp_path / "run.json"
    run.write_text(json.dumps({"bills": [bill], "per_customer_behavioral": {},
                               "churned_billing_accounts": [], "occupier_successions": []}))
    (inv, *_) = generate_ledger(run, tmp_path / "ledger.json")["customers"]["C4g"]["invoices"]
    assert (inv["read_unit"], inv["imperial_meter"]) == ("m3", True)
    assert _grade(_invoice(0.0, round(G.kwh_from_volume(100.0, "m3"), 1), 0.0, 100.0,
                           imperial_meter=bill["gas_meter_imperial"]))["status"] == "BREACHED"


def test_a_volume_without_its_conversion_terms_is_flagged_and_a_kwh_register_is_breached():
    """MUTATION: every missing field was sent to band(None), a breach, where the row's severity calls
    a volume present without its CV or factor a flag."""
    kwh = round(100.0 * 1.02264 * 39.5 / 3.6, 1)
    no_cv = _invoice(0.0, kwh, 0.0, 100.0)
    del no_cv["calorific_value_mj_per_m3"]
    assert _grade(no_cv)["status"] == "FLAGGED"
    assert _grade({"period_start": "2023-01-01", "period_end": "2023-01-31", "commodity": "gas",
                   "read_type": "A", "opening_read_kwh": 0.0,
                   "closing_read_kwh": kwh})["status"] == "BREACHED"
