"""The domain-invariant runner (ruling of 26 Oct, step 4): every evaluator can fire, nothing unrun reads clean, and it reads only the raw export.

The defects these tests name:
  * an evaluator that never reports (a guard that passes everything passes every "does it refuse
    correctly" test), so one broken book must make every registered evaluator report, and one clean
    book must reach every one of them without a breach;
  * an invariant the file marks uncheckable, one whose field the export lacks, or one with no
    evaluator, read as zero breaches;
  * every ID in the committed invariants file has a disposition here, so a new row cannot sit unrun;
  * the runner importing the biller or the pricing tables, and agreeing with them by construction.
"""
from __future__ import annotations

import ast
from pathlib import Path

import yaml

from tools import domain_invariant_runner as runner

RUNNER = Path(runner.__file__)


def _row(lower, upper, **kw):
    return dict({"from": "2020-01-01", "to": "2020-12-31", "lower": lower, "upper": upper}, **kw)


INVARIANTS = [
    {"id": "INV_UNIT_RATE_SVT_ELEC", "tolerance": {"upper_relative": 0.015},
     "rows": [_row(5.0, 18.0, upper_standard_credit=19.0, upper_prepayment=17.0)]},
    {"id": "INV_UNIT_RATE_SVT_ELEC_PRE_CAP", "rows": [_row(5.0, None)]},
    {"id": "INV_UNIT_RATE_SVT_GAS", "rows": [_row(0.0, 4.0)]},
    {"id": "INV_UNIT_RATE_SVT_GAS_PRE_CAP", "rows": [_row(0.0, None)]},
    {"id": "INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER", "rows": [_row(None, 16.0)]},
    {"id": "INV_UNIT_RATE_FIXED", "rows": [_row(5.0, None)]},
    {"id": "INV_STANDING_CHARGE_SVT_ELEC", "rows": [_row(0.0, 0.30)]},
    {"id": "INV_STANDING_CHARGE_SVT_GAS", "rows": [_row(0.0, 0.30)]},
    {"id": "INV_STANDING_CHARGE_FIXED", "lower": 0.0, "upper": None},
    {"id": "INV_ANNUAL_USE_ELEC_ACCOUNT", "lower": 0.0, "upper": 201480,
     "flag_bands": [{"class": "all domestic", "flag_lower": 500, "flag_upper_p99": 14300}]},
    {"id": "INV_ANNUAL_USE_GAS_ACCOUNT", "lower": 0.0, "upper": None, "hard_flag": {"upper": 50000},
     "flag_bands": [{"class": "all gas-heated", "flag_lower": 1000, "flag_upper_p99": 34300}]},
    {"id": "INV_READ_DUTY_ANNUAL", "lower": 0, "upper": 365, "tolerance": {"upper_days": 1}},
    {"id": "INV_SETTLEMENT_ACTUAL_SHARE_ELEC", "lower": 0.97, "upper": 1.0},
    {"id": "INV_BILL_AT_LEAST_TWICE_YEARLY", "lower": 1, "upper": 184},
    {"id": "INV_OPENING_READ", "rows": [{"commodity": "electricity", "lower": -5, "upper": 8},
                                        {"commodity": "gas", "lower": -5, "upper": 10}]},
    {"id": "INV_PAYMENT_PPM_AND_DD_NOT_CONCURRENT"},
    {"id": "INV_PAYMENT_AMOUNT_SIGN"},
    {"id": "INV_DD_CADENCE", "upper": 2},
    {"id": "INV_DD_STEP_CHANGE", "upper": 2.0},
    {"id": "INV_FUEL_IDENTIFIER"},
    {"id": "INV_GAS_SINGLE_REGISTER"},
    {"id": "INV_PERIODS_CONTIGUOUS"},
    {"id": "INV_BACK_BILLING_12M"},
    {"id": "INV_PERIOD_CONSUMPTION_NON_NEGATIVE"},
    {"id": "INV_READ_MONOTONIC"},
]
#: Evaluators this fixture does not reach, each with why. Neither may grow without a reason.
NOT_REACHED_BY_THE_FIXTURE = {
    "INV_ANNUAL_USE_BOOK_MEDIAN": "a book median needs ten account-years per TDCV row",
    "INV_CROSS_FUEL_PRICE_SCALE": "it takes its rows from the two SVT invariants; tested on its own below",
}


def _months(year=2020):
    out = []
    for m in range(1, 13):
        start = "{}-{:02d}-01".format(year, m)
        nxt = "{}-{:02d}-01".format(year + (m == 12), 1 if m == 12 else m + 1)
        end = runner._d(nxt).fromordinal(runner._d(nxt).toordinal() - 1).isoformat()
        out.append((start, end))
    return out


def _account(cid, fuel, *, rate, tariff="svt", sc=0.25, kwh_per_month=250.0, method="direct_debit",
             registers=("1",), read_type="A", start_read=1000.0, year=2020):
    periods, reading = [], start_read
    for start, end in _months(year):
        reads = []
        for reg in registers:
            reads += [{"register_id": reg, "read_date": start, "read_kwh": reading,
                       "read_type": "carried_forward"},
                      {"register_id": reg, "read_date": end, "read_kwh": reading + kwh_per_month,
                       "read_type": read_type}]
        reading += kwh_per_month
        periods.append({
            "commodity": fuel, "period_start": start, "period_end": end,
            "days_in_period": (runner._d(end) - runner._d(start)).days + 1,
            "mpan": "1" if fuel == "electricity" else None, "mprn": "2" if fuel == "gas" else None,
            "meter_serial": "M" + cid, "standing_charge_gbp_per_day": sc, "reads": reads,
            "contracted_terms": [{"tariff_effective_from": "{}-01-01".format(year),
                                  "tariff_effective_to": "{}-01-01".format(year + 1),
                                  "tariff_type": tariff, "unit_rate_p_per_kwh": rate}],
        })
    payments = [{"payment_date": s[:8] + "15", "payment_amount_gbp": 60.0, "payment_method": method}
                for s, _ in _months(year)]
    return {"customer_id": cid, "segment": "resi", "periods": periods, "payments": payments}


def _clean_book():
    return {
        "E": _account("E", "electricity", rate=15.0),
        "G": _account("G", "gas", rate=3.0, kwh_per_month=900.0),
        "M": _account("M", "electricity", rate=15.0, registers=("1", "2")),
        "F": _account("F", "electricity", rate=12.0, tariff="fixed"),
        "FG": _account("FG", "gas", rate=3.0, tariff="fixed", kwh_per_month=900.0),
        # old enough for its kWh to have settled (14 months before the book's end)
        "OLD": _account("OLD", "electricity", rate=15.0, year=2018),
    }


def _late_reader():
    """Read once in January, estimated after, then caught up 400 days on, far above its average."""
    acct = _account("L", "electricity", rate=15.0, read_type="E")
    acct["periods"][0]["reads"][1]["read_type"] = "A"
    last = acct["periods"][-1]["reads"][1]
    acct["periods"].append(dict(
        acct["periods"][-1], period_start="2021-01-01", period_end="2021-02-10", days_in_period=41,
        contracted_terms=[], reads=[
            dict(last, read_date="2021-01-01", read_type="carried_forward"),
            dict(last, read_date="2021-02-10", read_type="A", read_kwh=last["read_kwh"] + 9000.0)]))
    return acct


def _broken_book():
    book = _clean_book()
    e, g, m, f = (book[k]["periods"] for k in ("E", "G", "M", "F"))
    for p in e:
        p["contracted_terms"][0]["unit_rate_p_per_kwh"] = 19.0     # SVT elec above the cap
        p["standing_charge_gbp_per_day"] = 0.40                     # SC elec above
    e[2]["mprn"] = "9"                                              # FUEL: both supply points
    for p in g:
        p["contracted_terms"][0]["unit_rate_p_per_kwh"] = -1.0      # gas rate not positive
        p["standing_charge_gbp_per_day"] = 0.40                     # SC gas above
        p["reads"].append(dict(p["reads"][1], register_id="2"))     # gas meter, two registers
    for p in m:
        p["contracted_terms"][0]["unit_rate_p_per_kwh"] = 17.0      # multi-register above
    for p in f:
        p["contracted_terms"][0]["unit_rate_p_per_kwh"] = 4.0       # fixed below its floor (flag)
        p["standing_charge_gbp_per_day"] = -0.01                    # fixed SC negative
        for r in p["reads"]:
            if r["read_type"] == "A":
                r["read_type"] = "E"                                # read duty; settlement share
    f[5]["days_in_period"] = 200                                    # day count; over 184 days
    f[3]["reads"][1]["read_kwh"] = 0.0                              # negative consumption
    for p in e:
        for r in p["reads"]:
            r["read_kwh"] *= 10.0                                   # 30,000 kWh a year: flag
    m[6]["reads"][1]["read_kwh"] = 0.0                              # an actual read goes backwards
    f[7]["period_start"] = "2020-08-03"                             # a gap between bills
    for p in book["FG"]["periods"]:
        for r in p["reads"]:
            r["read_kwh"] *= 6.0                                    # 64,800 kWh gas: hard flag
    book["E"]["payments"] += [
        {"payment_date": "2020-03-20", "payment_amount_gbp": 500.0, "payment_method": "direct_debit"},
        {"payment_date": "2020-03-25", "payment_amount_gbp": None, "payment_method": "direct_debit"},
        {"payment_date": "2020-03-26", "payment_amount_gbp": 1.0, "payment_method": "direct_debit"},
        {"payment_date": "2020-05-20", "payment_amount_gbp": 9.0, "payment_method": "prepayment"},
        {"payment_date": "2020-06-20", "payment_amount_gbp": 9.0, "payment_method": "prepayment"},
    ]
    g[0]["reads"][0]["read_date"] = "2020-01-13"                    # opening read 12 days late
    for p in book["OLD"]["periods"][1:]:
        for r in p["reads"]:
            if r["read_type"] == "A":
                r["read_type"] = "E"                                # settled kWh not bounded by a read
    book["L"] = _late_reader()
    book["LOW"] = _account("LOW", "electricity", rate=3.0)         # SVT under the floor (flag)
    return book


def _results(book, invariants=INVARIANTS):
    return {r["id"]: r for r in runner.run(invariants, book)}


def test_a_clean_book_reaches_every_evaluator_and_breaches_and_flags_nothing():
    results = _results(_clean_book())
    off = {i: (r["status"], r.get("breach_examples"), r.get("flag_examples"))
           for i, r in results.items() if r["status"] != "CLEAN"}
    assert not off, off


#: The invariants whose file severity is a flag on every side the broken book breaks. Every other
#: one must come back BREACHED, so a hard side that stopped firing cannot hide behind a flag.
FLAG_ONLY = {"INV_UNIT_RATE_SVT_ELEC_PRE_CAP", "INV_UNIT_RATE_FIXED", "INV_ANNUAL_USE_ELEC_ACCOUNT",
             "INV_ANNUAL_USE_GAS_ACCOUNT", "INV_READ_DUTY_ANNUAL", "INV_SETTLEMENT_ACTUAL_SHARE_ELEC",
             "INV_BILL_AT_LEAST_TWICE_YEARLY", "INV_OPENING_READ", "INV_DD_CADENCE",
             "INV_DD_STEP_CHANGE", "INV_BACK_BILLING_12M"}


def test_every_evaluator_reports_on_one_broken_book_at_the_files_severity():
    results = _results(_broken_book())
    got = {i: r["status"] for i, r in results.items()}
    want = {i: "FLAGGED" if i in FLAG_ONLY else "BREACHED" for i in got}
    assert got == want, {i: (got[i], want[i]) for i in got if got[i] != want[i]}


def test_the_cross_fuel_scale_reads_both_svt_invariants_rows():
    invs = [INVARIANTS[0], INVARIANTS[2], {"id": "INV_CROSS_FUEL_PRICE_SCALE"}]
    assert _results(_clean_book(), invs)["INV_CROSS_FUEL_PRICE_SCALE"]["status"] == "CLEAN"
    book = _clean_book()
    for p in book["G"]["periods"]:
        p["contracted_terms"][0]["unit_rate_p_per_kwh"] = 15.0      # gas priced like electricity
    assert _results(book, invs)["INV_CROSS_FUEL_PRICE_SCALE"]["status"] == "BREACHED"


def test_every_evaluator_is_exercised_here_or_named_with_why_not():
    covered = {i["id"] for i in INVARIANTS} | set(NOT_REACHED_BY_THE_FIXTURE)
    evaluated = {i for i, (fn, _needs) in runner.EVALUATORS.items() if fn is not None}
    assert evaluated <= covered, evaluated - covered


def test_an_unrun_invariant_is_never_reported_clean():
    results = runner.run([
        {"id": "INV_UNIT_RATE_SVT_ELEC", "checkable": False, "gap": "no source"},
        {"id": "INV_VAT_RATE"},
        {"id": "INV_SOMETHING_NEW"},
        {"id": "INV_UNIT_RATE_SVT_ELEC", "rows": [_row(None, None)]},
    ], _clean_book())
    assert [r["status"] for r in results] == ["UNCHECKABLE", "NOT_IN_EXPORT", "NO_EVALUATOR", "UNREACHED"]
    assert results[0]["reason"] == "no source" and results[3]["unbounded"] > 0


def test_the_payment_method_picks_the_cap_column():
    row = _row(5.0, 18.0, upper_standard_credit=19.0, upper_prepayment=17.0)
    pick = runner._upper_for_methods
    assert (pick(row, {"direct_debit"}), pick(row, {"prepayment", "direct_debit"}),
            pick(row, {"standard_credit"}), pick(row, {"direct_debit", "standard_credit"}),
            pick(row, set())) == (18.0, 17.0, 19.0, 19.0, 19.0)


def test_every_id_in_the_committed_file_has_a_disposition():
    ids = {i["id"] for i in yaml.safe_load(runner.INVARIANTS_PATH.read_text())["invariants"]
           if i.get("checkable", True)}
    assert ids <= set(runner.EVALUATORS), ids - set(runner.EVALUATORS)


def test_the_committed_file_cites_a_source_or_a_gap_for_every_invariant():
    for inv in yaml.safe_load(runner.INVARIANTS_PATH.read_text())["invariants"]:
        assert inv.get("source") or inv.get("gap"), inv["id"]


def test_the_runner_imports_nothing_from_the_repository_but_the_raw_export():
    mods = set()
    for node in ast.walk(ast.parse(RUNNER.read_text())):
        if isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add(node.module or "")
    repo = {m for m in mods if m.split(".")[0] in {"company", "saas", "simulation", "sim", "tools",
                                                   "background", "site"}}
    assert repo == {"company.billing.raw_account_export"}, repo


def test_gas_grades_each_payment_method_against_its_own_column_and_flags_under_the_floor():
    """The gas rows carry per-method columns and a commodity floor since 2026-10-27. Defects named:
    a gas evaluator still reading the DD column for a prepayment account, and a floor nobody reads."""
    inv = [{"id": "INV_UNIT_RATE_SVT_GAS", "tolerance": {"upper_relative": 0.005},
            "rows": [_row(2.0, 4.0, upper_standard_credit=4.2, upper_prepayment=3.9)]}]

    def verdict(**kw):
        result = runner.run(inv, {"G": _account("G", "gas", kwh_per_month=900.0, **kw)})[0]
        return result["breached"], result["flagged"]

    outcomes = {
        "dd_at_dd_cap": verdict(rate=4.0),
        "pp_at_dd_cap": verdict(rate=4.0, method="prepayment"),
        "sc_at_dd_cap": verdict(rate=4.0, method="standard_credit"),
        "under_floor": verdict(rate=1.5),
    }
    assert outcomes["dd_at_dd_cap"] == (0, 0)
    assert outcomes["pp_at_dd_cap"][0] > 0
    assert outcomes["sc_at_dd_cap"] == (0, 0)
    assert outcomes["under_floor"][0] == 0 and outcomes["under_floor"][1] > 0
