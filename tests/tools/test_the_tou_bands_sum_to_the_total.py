"""A time-of-use meter's band indices sum to its total index, under every tariff (E4, 2026-10-29).

Defect: a band register advanced only on the bills that printed it, by its printed kWh alone. So a
single-rate stretch left the bands behind the total, and an actual read after estimates moved the
total by the catch-up and the bands by nothing. On the 209c3350ab book's ledger rebuilt, 542 of 1,429
ToU invoices' band indices missed the total. SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_
FROM_ONE_READ_AND_PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md, E4.

The meter records each half-hour in its total and in one band register (SMETS2 5.5.8.1, 5.5.9.1), and
a single rate routes all use to the first band (docs/market_research/a_multi_register_meters_bands_add_
up_to_its_total.md). So the bands advance with the total whatever the tariff, and an actual read's
catch-up is shared across them.

Mutations, each reds this file: the single-rate branch not advancing the first band; a band's closing
leaving out its catch-up share; the export dropping a band's share; the validator or the non-negative
row ignoring it; the new row's evaluator unregistered.
"""
import datetime as dt
import json

from company.billing.raw_account_export import raw_account
from tests.tools.test_a_meter_register_keeps_one_id_and_one_index_for_the_life_of_its_serial import (
    _bill,
)
from tools import domain_invariant_runner as runner
from tools.generate_billing_ledger import generate
from tools.independent_bill_validator import rebuild

PEAK, OFFPEAK = 400.0, 220.0


def _ledger(tmp_path, *, estimate_feb=False, factor=0.5):
    """Single rate, ToU, ToU, single rate. With `estimate_feb`, February is estimated at `factor` of
    its use and March is an actual read whose register spans the catch-up (negative above 1)."""
    d = dt.date
    bills = [_bill(d(2023, 1, 1), d(2023, 2, 1), None),
             _bill(d(2023, 2, 1), d(2023, 3, 1), (PEAK, OFFPEAK)),
             _bill(d(2023, 3, 1), d(2023, 4, 1), (PEAK, OFFPEAK)),
             _bill(d(2023, 4, 1), d(2023, 5, 1), None)]
    run = {"bills": bills, "per_customer_behavioral": {}, "churned_billing_accounts": []}
    if estimate_feb:
        use = [b["total_consumption_kwh"] for b in bills]
        run["meter_read_log"] = [{"customer_id": "SYN-T", "period_end": bills[1]["period_end"],
                                  "status": "estimated", "estimated_consumption_kwh": use[1] * factor}]
        bills[2]["register_opening_kwh"] = use[0] + use[1]
        bills[2]["register_closing_kwh"] = use[0] + use[1] + use[2]
        bills[2]["read_true_up_kwh"] = use[1] * (1 - factor)
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run))
    return generate(rj, tmp_path / "l.json")["customers"]["SYN-T"]


def _tou(record):
    return [i for i in record["invoices"] if len(i["registers"]) > 1]


def _grade(record, inv_id):
    inv = next(i for i in runner.load_invariants() if i["id"] == inv_id)
    return runner.EVALUATORS[inv_id][0](inv, [runner.Account("SYN-T", raw_account("SYN-T", record))])


def test_the_book_reaches_both_seams_and_a_catch_up_on_a_tou_bill(tmp_path):
    """A test of the sum over a book with no single-rate stretch and no catch-up passes vacuously."""
    record = _ledger(tmp_path, estimate_feb=True)
    assert [len(i["registers"]) for i in record["invoices"]] == [1, 2, 2, 1]
    assert _tou(record)[1]["catchup_kwh"] > 0


def test_every_tou_bills_band_indices_sum_to_the_total_index(tmp_path):
    for estimated in (False, True):
        for inv in _tou(_ledger(tmp_path, estimate_feb=estimated)):
            bands = sum(r["closing_read_kwh"] for r in inv["registers"])
            assert abs(bands - inv["closing_read_kwh"]) <= 0.1, (estimated, inv["period_start"])
            advance = sum(r["closing_read_kwh"] - r["opening_read_kwh"] for r in inv["registers"])
            assert abs(advance - (inv["closing_read_kwh"] - inv["opening_read_kwh"])) <= 0.2


def test_the_catch_up_is_shared_and_every_reader_takes_each_bands_share(tmp_path):
    record = _ledger(tmp_path, estimate_feb=True)
    march = _tou(record)[1]
    shares = [r.get("catchup_kwh", 0.0) for r in march["registers"]]
    assert all(s > 0 for s in shares) and abs(sum(shares) - march["catchup_kwh"]) <= 0.1
    period = raw_account("SYN-T", record)["periods"][2]
    assert [r["catchup_kwh"] for r in period["registers"]] == shares
    energy = next(line for line in rebuild(raw_account("SYN-T", record))["periods"][2]["lines"]
                  if line["label"] == "Energy")
    assert abs(energy["volume_kwh"] - march["consumption_kwh"]) <= 0.1
    assert abs(energy["amount_gbp"] - march["commodity_amount_gbp"]) <= 0.01
    graded = _grade(record, "INV_PERIOD_CONSUMPTION_NON_NEGATIVE")
    assert graded.checked and not graded.breaches


def test_an_over_estimate_takes_each_band_back_by_its_share_and_is_not_negative_use(tmp_path):
    """Estimated at three times its use: each band's share is below minus its own March use."""
    record = _ledger(tmp_path, estimate_feb=True, factor=3.0)
    march = _tou(record)[1]
    assert all(r["catchup_kwh"] < -r["consumption_kwh"] for r in march["registers"])
    assert abs(sum(r["closing_read_kwh"] for r in march["registers"]) - march["closing_read_kwh"]) <= 0.1
    graded = _grade(record, "INV_PERIOD_CONSUMPTION_NON_NEGATIVE")
    assert graded.checked and not graded.breaches


def test_the_row_grades_both_seams_and_breaches_bands_left_behind(tmp_path):
    record = _ledger(tmp_path, estimate_feb=True)
    clean = _grade(record, "INV_TOU_BANDS_SUM_TO_THE_TOTAL")
    assert clean.checked == 2 and not clean.breaches, clean.breaches
    # The old ledger: bands open at zero after a single-rate January.
    for reg in record["invoices"][1]["registers"]:
        reg["opening_read_kwh"] = 0.0 if reg["label"] == "Peak" else reg["opening_read_kwh"]
    assert len(_grade(record, "INV_TOU_BANDS_SUM_TO_THE_TOTAL").breaches) == 1
    # And the bands behind the total at April's single-rate opening.
    record["invoices"][2]["registers"][0]["closing_read_kwh"] -= 50.0
    assert len(_grade(record, "INV_TOU_BANDS_SUM_TO_THE_TOTAL").breaches) == 2


def test_the_opening_row_does_not_compare_a_register_the_last_period_did_not_print(tmp_path):
    """The total moved over the ToU stretch unread; the band row grades that seam instead."""
    graded = _grade(_ledger(tmp_path), "INV_OPENING_IS_THE_PREVIOUS_CLOSING")
    assert graded.checked == 2 and not graded.breaches
