"""A supply point settled on Profile Class 2 is billed on its Day and Night registers (2026-10-30).

Defect: the world settled every storage-heated home on PC2, "Domestic Economy 7", and the company billed
it single-rate on every term: 36 of 560 electricity accounts and all 537 of their term rows on the
209c3350ab book. K8: docs/market_research/a_storage_heated_homes_default_tariff_is_two_rate.md.

The row is INV_E7_METER_BILLED_ON_TWO_REGISTERS, written by a reader given the pages and not the code.
Red: a PC2 period billed on one register breaches it. Green: the same period billed through the build
(the desk's Day/Night pair, the meter's 00:30-07:30 Night register) is clean.

Mutations, each reds this file: `offers_tou` not reading the meter's class (a default term goes back to
single-rate); the settlement's Night window moved off 00:30-07:30; the evaluator's PC2 leg deleted; the
pair struck off the ToU split instead of the 58/42 one.
"""
import datetime as dt
import json

import pytest

from company.billing.raw_account_export import raw_account
from company.interfaces.tou_offer import ECONOMY_7, request_tou_offer
from saas.bill_generator import generate_bill
from simulation.hedged_settlement import run_hedged_term
from simulation.settlement_daily import fold_to_days
from tools import domain_invariant_runner as runner
from tools.generate_billing_ledger import generate

FLAT = 150.0
E7_RECORD = {"customer_id": "SYN-E7", "segment": "resi", "smart_meter": False,
             "registered_profile_class": 2}
ROW = {"id": "INV_E7_METER_BILLED_ON_TWO_REGISTERS"}


def _prices(start, end):
    out, d = [], start
    while d < end:
        out += [{"settlementDate": d.isoformat(), "settlementPeriod": p, "systemSellPrice": 120.0}
                for p in range(1, 49)]
        d += dt.timedelta(days=1)
    return out


def _bill(start, end, *, pair, profile_class):
    recs = run_hedged_term("SYN-E7", start.isoformat(), end.isoformat(), FLAT, 120.0, 0.8, 0.0,
                           lambda ds: [0.25] * 48, _prices(start, end),
                           tou_rates=pair, economy_7=pair is not None)
    bill = generate_bill("SYN-E7", fold_to_days(recs), "fixed_1yr", None, "resi", "electricity")
    bill["profile_class"] = profile_class
    return bill


def _graded(tmp_path, bills):
    run = {"bills": bills, "per_customer_behavioral": {}, "churned_billing_accounts": []}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run))
    record = generate(rj, tmp_path / "l.json")["customers"]["SYN-E7"]
    raw = raw_account("SYN-E7", record)
    return record, runner.ev_e7_meter_two_registers(ROW, [runner.Account("SYN-E7", raw)])


def _offer(tariff_type, record=E7_RECORD):
    return request_tou_offer(customer=record, tariff_type=tariff_type, flat_unit_rate_gbp_per_mwh=FLAT)


@pytest.mark.parametrize("tariff_type", ["svt", "fixed"])
def test_a_pc2_meter_is_offered_its_day_night_pair_on_every_term(tariff_type):
    offer = _offer(tariff_type)
    assert offer is not None and offer.registers == ECONOMY_7
    day, night = offer.peak_rate_gbp_per_mwh, offer.offpeak_rate_gbp_per_mwh
    assert night < day
    # SLC 28AD.36(a): the cap grades 0.58 x day + 0.42 x night, so the pair blends to the flat rate.
    assert 0.58 * day + 0.42 * night == pytest.approx(FLAT)


def test_a_default_term_without_an_e7_meter_stays_single_rate():
    """The control the rule is keyed to: the meter's class, not every default term."""
    assert _offer("svt", dict(E7_RECORD, registered_profile_class=1)) is None
    assert _offer("svt", {k: v for k, v in E7_RECORD.items() if k != "registered_profile_class"}) is None


def test_the_night_register_is_the_seven_hours_from_0030():
    recs = run_hedged_term("SYN-E7", "2023-01-02", "2023-01-03", FLAT, 120.0, 0.8, 0.0,
                           lambda ds: [0.25] * 48, _prices(dt.date(2023, 1, 2), dt.date(2023, 1, 3)),
                           tou_rates=(200.0, 90.0), economy_7=True)
    night = [r["settlement_period"] for r in recs if "tou_night_kwh" in r]
    assert night == list(range(2, 16))  # 00:30-07:30, weekday and weekend alike
    assert {r["unit_rate_gbp_per_mwh"] for r in recs if "tou_day_kwh" in r} == {200.0}


def test_red_a_pc2_period_billed_single_rate_breaches_the_row(tmp_path):
    _, tally = _graded(tmp_path, [_bill(dt.date(2023, 1, 1), dt.date(2023, 2, 1),
                                        pair=None, profile_class=2)])
    assert tally.checked == 1 and len(tally.breaches) == 1, tally.breaches


def test_green_the_same_period_billed_through_the_build_is_clean(tmp_path):
    offer = _offer("svt")
    pair = (offer.peak_rate_gbp_per_mwh, offer.offpeak_rate_gbp_per_mwh)
    record, tally = _graded(tmp_path, [
        _bill(dt.date(2023, 1, 1), dt.date(2023, 2, 1), pair=pair, profile_class=2),
        _bill(dt.date(2023, 2, 1), dt.date(2023, 3, 1), pair=pair, profile_class=2)])
    assert [[r["label"] for r in inv["registers"]] for inv in record["invoices"]] == [
        ["Day", "Night"], ["Day", "Night"]]
    assert tally.checked == 2 and not tally.breaches and not tally.flags


def test_the_ledger_prints_the_terms_pair_as_day_night_at_the_e7_split():
    from tools.generate_billing_ledger import _contracted_terms, _tou_terms

    terms = {"A": [{"term_start": "2023-01-01", "term_end": "2023-04-01", "tariff_type": "svt",
                    "unit_rate_gbp_per_mwh": FLAT}]}
    bill = {"customer_id": "A", "period_start": "2023-02-01", "period_end": "2023-02-28",
            "registers": [{"band": "day", "label": "Day"}, {"band": "night", "label": "Night"}]}
    rates = _contracted_terms(terms, bill, _tou_terms(terms, [bill]))[0]["tou_unit_rates"]
    offer = _offer("svt")
    assert [r["register_label"] for r in rates] == ["Day", "Night"]
    assert [r["unit_rate_p_per_kwh"] for r in rates] == pytest.approx(
        [offer.peak_rate_gbp_per_mwh / 10.0, offer.offpeak_rate_gbp_per_mwh / 10.0], abs=1e-4)


def test_every_leg_of_the_partition_can_fire(tmp_path):
    """A row that refuses everything passes the red test; each leg must be reachable on its own."""
    def period(pc, labels):
        return {"commodity": "electricity", "period_start": "2023-01-01", "period_end": "2023-01-31",
                "profile_class": pc,
                "reads": [{"register_label": lab} for lab in labels]}

    def grade(*periods):
        a = runner.Account("X", {"segment": "resi", "periods": list(periods)})
        return runner.ev_e7_meter_two_registers(ROW, [a])

    assert len(grade(period(2, ["Anytime"])).breaches) == 1
    assert len(grade(period(2, ["Night"])).flags) == 1
    assert len(grade(period(1, ["Day", "Night"])).breaches) == 1
    clean = grade(period(2, ["Day", "Night"]), period(1, ["Anytime"]))
    assert clean.checked == 2 and not clean.breaches and not clean.flags
    skipped = grade(period(2, ["Peak", "Off-peak"]), period(None, ["Anytime"]), period(3, ["Anytime"]))
    assert skipped.checked == 0
