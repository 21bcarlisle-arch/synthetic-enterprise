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
    {"id": "INV_PERIOD_MATCHES_READS", "lower": -1, "upper": 1},
    {"id": "INV_OPENING_IS_THE_PREVIOUS_CLOSING", "lower": -0.1, "upper": 0.1},
    {"id": "INV_VAT_RATE", "rows": [
        {"commodity": c, "segment": "domestic", "from": "2016-01-01", "to": "2027-03-31",
         "lower": 0.05, "upper": 0.05} for c in ("electricity", "gas")] + [
        {"commodity": "electricity", "segment": "sme/non-domestic", "from": "2016-01-01",
         "to": "2027-03-31", "lower": 0.05, "upper": 0.2,
         "rule": "0.05 if consumption_kwh/days_in_period <= 33 else 0.20"}]},
    {"id": "INV_NON_COMMODITY_WITHIN_ALL_IN"},
    {"id": "INV_PPM_NOT_CREDIT_BILLED"},
    {"id": "INV_REGISTER_ID_ONE_LABEL"},
    {"id": "INV_SERIAL_REGISTER_COUNT_STABLE"},
    {"id": "INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23"},
    {"id": "INV_MPAN_CORE_FORMAT"},
]
#: Evaluators this fixture does not reach, each with why. Neither may grow without a reason.
NOT_REACHED_BY_THE_FIXTURE = {
    "INV_ANNUAL_USE_BOOK_MEDIAN": "a book median needs ten account-years per TDCV row",
    "INV_CROSS_FUEL_PRICE_SCALE": "it takes its rows from the two SVT invariants; tested on its own below",
    "INV_RENEWAL_NOTICE_42_TO_49_DAYS": "reads the company's statements; every leg tested on its own below",
    "INV_COLLECTIONS_EVENTS_ORDERED": "reads the collections journeys; every leg tested on its own below",
    "INV_OVERDUE_WITHIN_BALANCE": "reads the collections journeys; every leg tested on its own below",
    "INV_STATUTE_BARRED_WRITE_OFF_AGE": "needs a six-year-old debt; every leg tested on its own below",
    "INV_EBSS_CREDIT_ON_THE_BILL": "reads the printed page; every leg tested on its own below",
    "INV_OVERDUE_WITHIN_PAGE_BALANCE": "reads the printed page; every leg tested on its own below",
    "INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE": "reads the printed page; every leg tested on its own below",
    "INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE": "reads the printed page; every leg tested on its own below",
    "INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL": "reads the printed page; every leg tested on its own below",
    "INV_SMART_METER_BILLED_ON_ITS_OWN_READS": "reads the printed page; every leg tested on its own below",
    "INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT": "reads the printed page; every leg tested on its own below",
    "INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS": "reads the printed page; every leg tested on its own below",
    "INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER": "reads the printed page; every leg tested on its own below",
    "INV_TOU_BANDS_SUM_TO_THE_TOTAL": "needs a ToU stretch; every leg tested in test_the_tou_bands_sum_to_the_total.py",
    "INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW": "compares accounts with each other; every leg tested on its own below",
    "INV_UNIT_RATE_EPG_HOUSEHOLD": "needs the EPG windows of 2022-23; every leg tested on its own below",
    "INV_ESTIMATE_RUN_WITHIN_TENURE": "reads the printed page; every leg tested on its own below",
    "INV_METER_SERIAL_ONE_SUPPLY_POINT": "compares accounts with each other; every leg tested in test_one_meter_serial_sits_on_one_supply_point.py",
    "INV_E7_METER_BILLED_ON_TWO_REGISTERS": "needs a registered profile class; every leg tested in test_an_economy_7_meter_is_billed_on_two_registers.py",
}


#: Thirteen digits, Eastern (10), and its check digit (0) by the published weights.
VALID_MPAN = "1000000000110"


def _months(year=2020):
    out = []
    for m in range(1, 13):
        start = "{}-{:02d}-01".format(year, m)
        nxt = "{}-{:02d}-01".format(year + (m == 12), 1 if m == 12 else m + 1)
        end = runner._d(nxt).fromordinal(runner._d(nxt).toordinal() - 1).isoformat()
        out.append((start, end))
    return out


def _account(cid, fuel, *, rate, tariff="svt", sc=0.25, kwh_per_month=250.0, method="direct_debit",
             registers=("1",), read_type="A", start_read=1000.0, year=2020, opening_type="D"):
    """`opening_type` is the supply start's own read, typed, on the first period: the record a
    correct export would carry (None gives today's export, whose first period opens only on the
    carried-forward read)."""
    periods, reading = [], start_read
    for start, end in _months(year):
        reads = []
        if not periods and opening_type:
            reads += [{"register_id": reg, "read_date": start, "read_kwh": reading,
                       "read_type": opening_type} for reg in registers]
        for reg in registers:
            reads += [{"register_id": reg, "read_date": start, "read_kwh": reading,
                       "read_type": "carried_forward"},
                      {"register_id": reg, "read_date": end, "read_kwh": reading + kwh_per_month,
                       "read_type": read_type}]
        reading += kwh_per_month
        periods.append({
            "commodity": fuel, "period_start": start, "period_end": end,
            "days_in_period": (runner._d(end) - runner._d(start)).days + 1,
            "mpan": VALID_MPAN if fuel == "electricity" else None, "mprn": "2" if fuel == "gas" else None,
            "meter_serial": "M" + cid, "standing_charge_gbp_per_day": sc, "reads": reads,
            "volume_basis": "reads", "consumption_kwh": kwh_per_month * len(registers),
            "unit_rate_p_per_kwh": rate, "vat_rate": 0.05, "document_type": "bill",
            "non_commodity_rate_gbp_per_mwh": 50.0 if fuel == "electricity" else 10.0,
            "contracted_terms": [{"tariff_effective_from": "{}-01-01".format(year),
                                  "tariff_effective_to": "{}-01-01".format(year + 1),
                                  "tariff_type": tariff, "unit_rate_p_per_kwh": rate}],
        })
    payments = [{"payment_date": s[:8] + "15", "payment_amount_gbp": 60.0, "payment_method": method}
                for s, _ in _months(year)]
    return {"customer_id": cid, "segment": "resi", "periods": periods, "payments": payments}


def _clean_book():
    book = {
        "E": _account("E", "electricity", rate=15.0),
        "G": _account("G", "gas", rate=3.0, kwh_per_month=900.0),
        "M": _account("M", "electricity", rate=15.0, registers=("1", "2")),
        "F": _account("F", "electricity", rate=12.0, tariff="fixed"),
        "FG": _account("FG", "gas", rate=3.0, tariff="fixed", kwh_per_month=900.0),
        # old enough for its kWh to have settled (14 months before the book's end)
        "OLD": _account("OLD", "electricity", rate=15.0, year=2018),
        "P": _account("P", "electricity", rate=15.0, method="prepayment"),
    }
    for p in book["P"]["periods"]:
        p["document_type"] = "prepayment_statement"
    book.update(_ebss_pair())
    return book


def _ebss_pair():
    """A household on supply through 2022 into 2023: electricity credited each month, gas nothing.
    Each credit is dated in the month after, so the row's overlapping windows hold two months."""
    elec = _account("EB", "electricity", rate=15.0, year=2022)
    gas = _account("GB", "gas", rate=3.0, kwh_per_month=900.0, year=2022)
    for acct in (elec, gas):
        more = _account(acct["customer_id"], acct["periods"][0]["commodity"],
                        rate=acct["periods"][0]["unit_rate_p_per_kwh"], year=2023,
                        start_read=acct["periods"][-1]["reads"][1]["read_kwh"],
                        kwh_per_month=900.0 if acct is gas else 250.0)
        acct["periods"] += more["periods"][:3]
        acct["payments"] += more["payments"][:3]
        acct["adjustments"] = []
    elec["adjustments"] = [{"adjustment_date": d, "adjustment_amount_gbp": a,
                            "adjustment_reason": "scheme_credit"}
                           for d, a in (("2022-11-05", 66.0), ("2022-12-05", 66.0), ("2023-01-05", 67.0),
                                        ("2023-02-05", 67.0), ("2023-03-05", 67.0), ("2023-04-05", 67.0))]
    return {"EB": elec, "GB": gas}


def _late_reader():
    """Read once in January, estimated after, then caught up 400 days on, far above its average."""
    acct = _account("L", "electricity", rate=15.0, read_type="E")
    acct["periods"][0]["reads"][-1]["read_type"] = "A"
    last = acct["periods"][-1]["reads"][1]
    acct["periods"].append(dict(
        acct["periods"][-1], period_start="2021-01-01", period_end="2021-02-10", days_in_period=41,
        contracted_terms=[], reads=[
            dict(last, read_date="2021-01-01", read_type="carried_forward"),
            dict(last, read_date="2021-02-10", read_type="A", read_kwh=last["read_kwh"] + 9000.0)]))
    return acct


def _labelled(acct, label="Anytime"):
    for p in acct["periods"]:
        for r in p["reads"]:
            r["register_label"] = label
    return acct


def _relabelled():
    """Register 1 is the total from January to June and Peak from July, its index carried straight
    across: the 67a893e749 shape. In March a second register is read on the closing date only."""
    acct = _labelled(_account("R", "electricity", rate=15.0))
    for p in acct["periods"][6:]:
        for r in p["reads"]:
            r["register_label"] = "Peak"
    march = acct["periods"][2]
    march["reads"].append(dict(march["reads"][1], register_id="2", register_label="Off-peak"))
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
    g[0]["reads"][0]["read_date"] = "2020-01-13"                    # typed opening read 12 days late
    for p in book["OLD"]["periods"][1:]:
        for r in p["reads"]:
            if r["read_type"] == "A":
                r["read_type"] = "E"                                # settled kWh not bounded by a read
    book["L"] = _late_reader()
    book["LOW"] = _account("LOW", "electricity", rate=3.0)         # SVT under the floor (flag);
    #                                                                 and under its own levies
    g[1]["consumption_kwh"] += 50.0                                 # billed more than was read
    e[0]["vat_rate"] = 0.20                                         # domestic at the standard rate
    book["EB"]["adjustments"].pop(2)                                # Dec 2022's credit never arrives
    book["GB"]["adjustments"] = [dict(book["EB"]["adjustments"][0])]  # a gas account credited
    for p in e:
        p["mpan"] = "1000000000116"                                 # check digit 6, not 0
    book["R"] = _relabelled()                                       # one register, two identities;
    #                                                                 a register set moving mid-period
    return book                                                     # E's prepayment months were
    #                                                                 sent credit bills


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
    book = _clean_book()
    for acct in book.values():
        for p in acct["periods"]:
            del p["vat_rate"]
    results = runner.run([
        {"id": "INV_UNIT_RATE_SVT_ELEC", "checkable": False, "gap": "no source"},
        {"id": "INV_VAT_RATE"},
        {"id": "INV_SOMETHING_NEW"},
        {"id": "INV_UNIT_RATE_SVT_ELEC", "rows": [_row(None, None)]},
    ], book)
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


def test_the_meter_class_is_the_terms_own_not_the_accounts():
    """SLC 28AD grades by tariff. Defect named: an account that changes from single-rate to two
    registers mid-life had its single-rate SVT spell graded against the multi-register cap (and
    dropped from the single-rate one), because the class was read off every register the account
    ever printed. Each term is graded by the registers its own periods print."""
    single, multi = _account("S", "electricity", rate=17.0), _account("S", "electricity", rate=17.0,
                                                                       registers=("1", "2"))
    acct = single
    for i in range(6, 12):                      # second half of the year: a two-register spell
        p = dict(multi["periods"][i])
        p["contracted_terms"] = [dict(p["contracted_terms"][0], tariff_effective_from="2020-07-01",
                                      tariff_effective_to="2021-01-01", unit_rate_p_per_kwh=17.0)]
        acct["periods"][i] = p
    for p in acct["periods"][:6]:
        p["contracted_terms"][0]["tariff_effective_to"] = "2020-07-01"
    inv = [{"id": "INV_UNIT_RATE_SVT_ELEC", "rows": [_row(5.0, 18.0)]},
           {"id": "INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER", "rows": [_row(None, 16.0)]}]
    res = {r["id"]: r for r in runner.run(inv, {"S": acct})}
    # the single-register spell is checked against the single-rate cap, the two-register one against
    # the multi-register cap: one term each, and only the multi-register one (17 > 16) breaches
    assert res["INV_UNIT_RATE_SVT_ELEC"]["checked"] == 1 and res["INV_UNIT_RATE_SVT_ELEC"]["breached"] == 0
    assert res["INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER"]["checked"] == 1
    assert res["INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER"]["breached"] == 1


def test_a_business_period_is_graded_by_its_de_minimis():
    """The VAT rule for business supply: 5% at or under the fuel's daily average, 20% above."""
    inv = [i for i in INVARIANTS if i["id"] == "INV_VAT_RATE"]

    def breached(kwh_per_month, rate):
        acct = _account("S", "electricity", rate=15.0, kwh_per_month=kwh_per_month)
        acct["segment"] = "SME"
        for p in acct["periods"]:
            p["vat_rate"] = rate
        return runner.run(inv, {"S": acct})[0]["breached"]

    assert (breached(500.0, 0.05), breached(500.0, 0.20),
            breached(3000.0, 0.20), breached(3000.0, 0.05)) == (0, 12, 0, 12)


def test_a_standing_charge_is_graded_to_the_penny_over_the_period_not_the_printed_day():
    """Catches the per-day tolerance read alone. The bill rounds days x rate to the penny and prints
    the shortest per-day rate that reproduces it, so a household charged exactly the cap can print
    up to 1p/days over it: all 2,237 SVT standing-charge breaches on the 871f674a2 book. Both legs:
    a printed rate under a penny over the period is clean, and one 2p over it still breaches, so a
    tolerance wide enough to pass everything fails here too."""
    inv = {"id": "INV_STANDING_CHARGE_SVT_ELEC", "rows": [_row(0.0, 0.2153)],
           "tolerance": {"upper_absolute_gbp_per_day": 0.0001, "upper_absolute_gbp_per_period": 0.01}}
    # 31 days at the cap is 6.6743, billed 6.67; but a printed 0.2154 sits 0.31p over it.
    rounded = runner.Account("R", _account("R", "electricity", rate=15.0, sc=0.2154))
    over = runner.Account("O", _account("O", "electricity", rate=15.0, sc=0.2153 + 0.02 / 28))
    per_day_only = dict(inv, tolerance={"upper_absolute_gbp_per_day": 0.0001})
    assert len(runner.ev_standing_charge_svt_elec(per_day_only, [rounded]).breaches) == 12, (
        "the per-day tolerance alone passes the rounded rate, so this control proves nothing")
    assert runner.ev_standing_charge_svt_elec(inv, [rounded]).breaches == []
    assert len(runner.ev_standing_charge_svt_elec(inv, [over]).breaches) == 12


def test_an_enforced_verdict_says_refused_only_when_it_refuses():
    """Catches the verdict line keyed to `enforce` alone: the 871f674a2 re-grade, 0 unexcepted and
    4 excepted, printed "the publish is refused" into the run report while the gate let it stand."""
    results = [{"id": "INV_X", "breached": 3}]
    exc = {"invariant": "INV_X", "scope": "s", "reason": "r", "filed": "2026-10-27", "retired_by": "f"}
    clear = runner.render_verdict(runner.gate(results, {"enforce": True, "exceptions": [exc]}))
    refused = runner.render_verdict(runner.gate(results, {"enforce": True, "exceptions": []}))
    assert "refused" not in clear.splitlines()[0] and "stands" in clear.splitlines()[0], clear
    assert "the publish is refused" in refused.splitlines()[0], refused


def _two_periods(n1, n2, *, term_change, label2="Anytime", carried=True, serial2=None):
    """Two months on one serial with n1 then n2 registers; the second month's term starts on its
    first day when `term_change`."""
    acct = _labelled(_account("T", "electricity", rate=15.0, registers=tuple(map(str, range(1, n1 + 1)))))
    acct["periods"] = acct["periods"][:2]
    second = _labelled(_account("T", "electricity", rate=15.0,
                                registers=tuple(map(str, range(1, n2 + 1)))), label2)["periods"][1]
    if not carried:
        for r in second["reads"]:
            r["read_kwh"] += 77.0
    if term_change:
        second["contracted_terms"] = [dict(second["contracted_terms"][0], tariff_type="fixed",
                                           tariff_effective_from=second["period_start"])]
    if serial2:
        second["meter_serial"] = serial2
    acct["periods"][1] = second
    return {"T": acct}


def _one(inv_id, book):
    return _results(book, [{"id": inv_id}])[inv_id]


def test_every_leg_of_the_register_count_row_is_reachable():
    """MUTATION -- the blind INV_SERIAL_REGISTER_COUNT_STABLE row. Each leg is reached before any
    is asserted, so an evaluator that flags everything, or nothing, cannot pass."""
    legs = {
        "flag": _one("INV_SERIAL_REGISTER_COUNT_STABLE", _two_periods(1, 2, term_change=False)),
        "pass_at_term": _one("INV_SERIAL_REGISTER_COUNT_STABLE", _two_periods(1, 2, term_change=True)),
        "pass_at_exchange": _one("INV_SERIAL_REGISTER_COUNT_STABLE",
                                 _two_periods(1, 2, term_change=False, serial2="MNEW")),
        "steady": _one("INV_SERIAL_REGISTER_COUNT_STABLE", _two_periods(2, 2, term_change=False)),
    }
    assert {k: r["status"] for k, r in legs.items()} == {
        "flag": "FLAGGED", "pass_at_term": "CLEAN", "pass_at_exchange": "CLEAN", "steady": "CLEAN"}
    assert legs["pass_at_term"]["book"]["count_changes_at_a_tariff_change"] == 1
    assert legs["steady"]["book"]["count_changes_at_a_tariff_change"] == 0


def test_every_leg_of_the_one_label_row_is_reachable():
    """MUTATION -- the blind INV_REGISTER_ID_ONE_LABEL row: a total relabelled as a band with its
    index carried is one register under two identities (the 39 of the 67a893e749 book); the same
    relabel with a fresh index at a tariff change is a lawful reconfiguration; with neither, a flag."""
    legs = {
        "one_series": _one("INV_REGISTER_ID_ONE_LABEL",
                           _two_periods(1, 1, term_change=True, label2="Peak")),
        "reconfigured": _one("INV_REGISTER_ID_ONE_LABEL",
                             _two_periods(1, 1, term_change=True, label2="Peak", carried=False)),
        "unexplained": _one("INV_REGISTER_ID_ONE_LABEL",
                            _two_periods(1, 1, term_change=False, label2="Peak", carried=False)),
        "steady": _one("INV_REGISTER_ID_ONE_LABEL", _two_periods(1, 1, term_change=False)),
    }
    assert {k: r["status"] for k, r in legs.items()} == {
        "one_series": "BREACHED", "reconfigured": "CLEAN", "unexplained": "FLAGGED", "steady": "CLEAN"}


def test_a_held_month_the_next_bill_takes_up_closes_the_gap_and_an_untaken_one_does_not():
    """MUTATION -- INV_PERIODS_CONTIGUOUS against a pre-bill hold. A month the gate held is billed
    by the catch-up at the next actual read, which names it (`held_periods_reconciled`); the same
    gap with nothing naming it is still a breach, and a name that misses the gap does not close it."""
    def held(named):
        acct = _account("H", "electricity", rate=15.0)
        acct["periods"] = [p for p in acct["periods"] if p["period_start"][5:7] not in ("03", "04")]
        if named is not None:
            acct["periods"][2]["held_periods_reconciled"] = named
        return {"H": acct}
    march_april = [{"period_start": "2020-03-01", "period_end": "2020-03-31"},
                   {"period_start": "2020-04-01", "period_end": "2020-04-30"}]
    legs = {
        "taken_up": _one("INV_PERIODS_CONTIGUOUS", held(march_april)),
        "unnamed": _one("INV_PERIODS_CONTIGUOUS", held(None)),
        "half_named": _one("INV_PERIODS_CONTIGUOUS", held(march_april[:1])),
    }
    assert {k: r["status"] for k, r in legs.items()} == {
        "taken_up": "CLEAN", "unnamed": "BREACHED", "half_named": "BREACHED"}


def test_every_leg_of_the_ebss_row_is_reachable():
    """A credit short, a credit doubled, a gas credit and a prepayment month each grade apart."""
    inv = [{"id": "INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23"}]
    book = _ebss_pair()
    clean = _results(book, inv)["INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23"]
    assert (clean["status"], clean["checked"]) == ("CLEAN", 12), clean
    book["EB"]["adjustments"][0]["adjustment_amount_gbp"] = 40.0         # Oct short
    book["EB"]["adjustments"].append(dict(book["EB"]["adjustments"][3]))  # Jan doubled
    book["GB"]["adjustments"] = [dict(book["EB"]["adjustments"][1])]      # gas credited
    sides = sorted((b["where"].split()[1], b["side"])
                   for b in runner.ev_ebss_credit(None, [runner.Account(k, v) for k, v in book.items()]).breaches)
    assert sides == [("electricity", "above"), ("electricity", "below"), ("gas", "above")], sides
    book = _ebss_pair()
    book["EB"]["payments"] = [dict(p, payment_method="prepayment") for p in book["EB"]["payments"]]
    pp = _results(book, inv)["INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23"]
    assert (pp["checked"], pp["unbounded"]) == (6, 6), pp                # the row's own GAP
    book = _ebss_pair()                                                  # joined 12 Nov 2022:
    book["EB"]["periods"] = [p for p in book["EB"]["periods"] if p["period_start"] >= "2022-11-01"]
    book["EB"]["periods"][0]["period_start"] = "2022-11-12"              # November is not owed
    joiner = runner.ev_ebss_credit(None, [runner.Account("EB", book["EB"])])
    assert [b["side"] for b in joiner.breaches] == ["above"], joiner.breaches  # so its £66 is extra


def test_every_leg_of_the_mpan_row_is_reachable():
    def grade(core):
        acct = _account("X", "electricity", rate=15.0)
        for p in acct["periods"]:
            p["mpan"] = core
        return [b["side"] for b in runner.ev_mpan_core_format(None, [runner.Account("X", acct)]).breaches]
    assert grade(VALID_MPAN) == []
    assert grade("19494047720") == ["format"]                            # O31: eleven digits
    assert grade("0900000000010") == ["format"]                          # no distributor 09
    assert grade("2400000000013") == []                                  # an IDNO, 24 upward
    assert grade("1000000000116") == ["check digit"]
    assert runner.mpan_check_digit("100000000011") == 0


def test_an_electricity_account_takes_its_households_heating_band_through_the_billing_account():
    """The heating-class proxy ("also holds gas") read through `billing_account_id`, both legs: a
    household holding gas flags above the gas-heated p99, one holding none only above the higher
    p99, and an export without the id keeps the all-domestic band."""
    inv = {"id": "INV_ANNUAL_USE_ELEC_ACCOUNT", "lower": 0.0, "upper": 201480, "flag_bands": [
        {"class": "all domestic", "flag_lower": 500, "flag_upper_p99": 14300},
        {"class": "gas-heated (proxy)", "flag_upper_p99": 12200},
        {"class": "gas not main heating fuel (proxy)", "flag_upper_p99": 18200}]}

    def flags(kwh_year, *, holds_gas, with_id=True):
        e = _account("E", "electricity", rate=15.0, kwh_per_month=kwh_year / 12)
        g = _account("G", "gas", rate=3.0, kwh_per_month=900.0)
        if with_id:
            e["billing_account_id"] = "H1"
            g["billing_account_id"] = "H1" if holds_gas else "H2"
        book = [runner.Account(c, r) for c, r in {"E": e, "G": g}.items()]
        return len(runner.ev_annual_use_elec(inv, book).flags)

    assert flags(13000, holds_gas=True) and not flags(13000, holds_gas=False)
    assert flags(16000, holds_gas=True) and not flags(16000, holds_gas=False)
    assert not flags(13000, holds_gas=True, with_id=False) and flags(16000, holds_gas=False, with_id=False)
    assert flags(400, holds_gas=True) and flags(400, holds_gas=False)


LIMITATION = "limitation_act_1980_s5_six_years_from_due_and_from_the_last_payment"


def _bills(acct, *, unpaid=()):
    """Each period due 14 days after it ends and collected that day, except the months in `unpaid`."""
    out = []
    for p in acct["periods"]:
        due = (runner._d(p["period_end"]) + runner.timedelta(days=14)).isoformat()
        out.append({"due_date": due, "settled_date": None if p["period_start"][:7] in unpaid else due})
    return out


def _journey(*steps, exit="cured"):
    return {"journey_exit": exit, "events": [dict({"event": k, "event_date": d}, **(
        {"event_rule": LIMITATION} if k == "write_off" else {})) for k, d in steps]}


def _household(*, journeys=(), unpaid=(), offers=(), tariff="svt", year=2020, payments=True):
    acct = _account("H", "electricity", rate=15.0, tariff=tariff, year=year)
    acct["billing_account_id"] = "H"
    acct["events"] = {"bills": _bills(acct, unpaid=unpaid), "collections_journeys": list(journeys),
                      "renewal_offers": [{"offer_date": d, "commodity": "electricity"} for d in offers]}
    if not payments:
        acct["payments"] = []
    return [runner.Account("H", acct)]


def test_every_leg_of_the_renewal_notice_row_is_reachable():
    """The fix ends on 1 Jan 2021 (exclusive). An offer 47 days before is inside 42-49; one on the
    day (O6) is above; one 60 days before is below; none at all is missing, as no notice is kept."""
    inv = {"lower": -49, "upper": -42}

    def grade(*offers, tariff="fixed"):
        t = runner.ev_renewal_notice(inv, _household(offers=offers, tariff=tariff))
        return t.checked, [b["side"] for b in t.breaches]
    assert grade("2020-11-15") == (1, [])
    assert grade("2021-01-01") == (1, ["above"])
    assert grade("2020-11-02") == (1, ["below"])
    assert grade() == (1, ["missing"])
    assert grade(tariff="svt") == (0, [])                               # a default tariff has no end


def _with_statements(book, *dates, fixed_term_end=None, cut_to=None, segment="resi"):
    """The same household on a book whose run sends the SLC 22C statement (`renewal_notices`)."""
    acct = book[0]
    acct.notices = [{"notice_date": d, "fixed_term_end": fixed_term_end or "2021-01-01"} for d in dates]
    acct.segment = segment
    for p in acct.periods:
        for t in p["contracted_terms"]:
            if fixed_term_end:
                t["fixed_term_end"] = fixed_term_end
            if cut_to:
                t["tariff_effective_to"] = cut_to
    if cut_to:
        acct.periods[:] = [p for p in acct.periods if p["period_start"] < cut_to]
        acct.end = runner._d(acct.periods[-1]["period_end"])
    return book


def test_the_statement_is_graded_where_the_book_carries_it_and_the_offer_is_not():
    """DEFECT: the evaluator still grades the offer on a book that records statements, so an offer
    on the day the fix ends (O6) breaches a term whose statement went out on day 42; or it grades
    a statement outside 42-49 as clean. The fix ends 1 Jan 2021 (exclusive)."""
    inv = {"lower": -49, "upper": -42}

    def grade(*dates, offers=("2021-01-01",), **kw):
        t = runner.ev_renewal_notice(inv, _with_statements(_household(offers=offers, tariff="fixed"),
                                                           *dates, **kw))
        return t.checked, [b["side"] for b in t.breaches]
    assert grade("2020-11-20") == (1, [])                               # day 42, the run's choice
    assert grade("2020-11-13") == (1, [])                               # day 49
    assert grade("2020-11-21") == (1, ["above"])                        # day 41: late
    assert grade("2020-11-12") == (1, ["below"])                        # day 50: early
    assert grade() == (1, ["missing"])                                  # none sent, offer ignored


def test_a_statement_is_owed_only_where_the_account_is_supplied_on_its_last_day():
    """The partition first: owed and not owed must both be reachable. A fix to 1 Jan 2021 cut by a
    move on 1 Oct 2020 was gone before 20 Nov and is owed none; one cut on 1 Dec was supplied on 20
    Nov and is owed one, graded against the contract's end, not the move. A business account is
    outside 22C."""
    inv = {"lower": -49, "upper": -42}

    def grade(*dates, **kw):
        t = runner.ev_renewal_notice(inv, _with_statements(_household(tariff="fixed"), *dates,
                                                           fixed_term_end="2021-01-01", **kw))
        return t.checked, [b["side"] for b in t.breaches]
    assert grade(cut_to="2020-10-01") == (0, [])
    assert grade(cut_to="2020-12-01") == (1, ["missing"])
    assert grade("2020-11-20", cut_to="2020-12-01") == (1, [])
    assert grade(segment="sme") == (0, [])


def test_every_leg_of_the_collections_order_row_is_reachable():
    def grade(*steps):
        return [b["side"] for b in runner.ev_collections_ordered(None, _household(
            journeys=[_journey(*steps)])).breaches]
    ordered = (("missed_payment", "2020-03-17"), ("reminder", "2020-03-20"),
               ("repayment_plan_offer", "2020-04-01"), ("cured", "2020-04-10"))
    assert grade(*ordered) == []
    assert grade(*ordered[1:]) == ["no opening"]
    assert grade(("reminder", "2020-03-10"), *ordered) == ["before opening"]
    assert grade(ordered[0], ("repayment_plan_offer", "2020-03-18"), ordered[1]) == ["plan before reminder"]


def test_an_open_debt_stage_needs_a_bill_unpaid_past_its_due_date():
    """O18's class: a journey opened when every bill due by then had been collected."""
    journey = [_journey(("missed_payment", "2020-03-17"), ("cured", "2020-04-10"))]
    feb_unpaid = runner.ev_overdue_within_balance(None, _household(journeys=journey, unpaid={"2020-02"}))
    all_paid = runner.ev_overdue_within_balance(None, _household(journeys=journey))
    assert (feb_unpaid.checked, len(feb_unpaid.breaches)) == (1, 0)
    assert [b["side"] for b in all_paid.breaches] == ["nothing overdue"]


def test_every_leg_of_the_statute_bar_row_is_reachable():
    """2010's December bill (due 14 Jan 2011) is never collected. Written off on 1 Jun 2017 it is
    barred; on 1 Dec 2016 it is not yet six years old; and a payment after the bar restarts it."""
    def grade(when, *, payments=False):
        h = _household(journeys=[_journey(("missed_payment", "2011-01-15"), ("write_off", when),
                                          exit="write_off")],
                       unpaid={"2010-12"}, year=2010, payments=payments)
        if payments:
            h[0].payments.append({"payment_date": "2012-01-10", "payment_amount_gbp": 5.0,
                                  "payment_method": "standard_credit"})
        t = runner.ev_statute_barred_write_off(None, h)
        return t.checked, [b["side"] for b in t.breaches]
    assert grade("2017-06-01") == (1, [])
    assert grade("2016-12-01") == (1, ["no bill old enough"])
    assert grade("2017-06-01", payments=True) == (1, ["payment after the bar"])


# ── the twins graded on what the page prints (second cold read, N1) ─────────────────────────────

def _printed_bills(acct, credit=True):
    """One page bill per period, each showing its month's EBSS credit where one is owed."""
    owed = {m.isoformat()[:7]: amt for m, amt in runner.EBSS_CREDIT_GBP}
    return [{"period_start": p["period_start"], "period_end": p["period_end"],
             "scheme_credit_gbp": owed.get(p["period_start"][:7]) if credit else None}
            for p in acct["periods"]]


def test_every_leg_of_the_ebss_bill_row_is_reachable():
    """A bill short of its credit, a month no bill covers and a credited gas bill each grade apart,
    and a book read without its pages is never clean."""
    inv = [{"id": "INV_EBSS_CREDIT_ON_THE_BILL"}]
    book = _ebss_pair()
    assert _results(book, inv)["INV_EBSS_CREDIT_ON_THE_BILL"]["status"] == "NOT_IN_EXPORT"
    book["EB"]["printed"] = {"invoices": _printed_bills(book["EB"])}
    book["GB"]["printed"] = {"invoices": _printed_bills(book["GB"], credit=False)}
    clean = _results(book, inv)["INV_EBSS_CREDIT_ON_THE_BILL"]
    assert (clean["status"], clean["checked"]) == ("CLEAN", 12), clean
    bills = book["EB"]["printed"]["invoices"]
    next(b for b in bills if b["period_start"] == "2022-12-01")["scheme_credit_gbp"] = None  # Dec not shown
    bills.remove(next(b for b in bills if b["period_start"] == "2023-02-01"))                # Feb: no bill
    next(b for b in book["GB"]["printed"]["invoices"]
         if b["period_start"] == "2022-10-01")["scheme_credit_gbp"] = 66.0                   # gas credited
    sides = sorted((b["where"].split()[1], b["side"]) for b in runner.ev_ebss_credit_on_the_bill(
        None, [runner.Account(k, v) for k, v in book.items()]).breaches)
    assert sides == [("electricity", "below"), ("electricity", "missing"), ("gas", "above")], sides
    book = _ebss_pair()                                                  # one account has no page
    book["EB"]["printed"] = {"invoices": _printed_bills(book["EB"])}
    one = runner.ev_ebss_credit_on_the_bill(None, [runner.Account(k, v) for k, v in book.items()])
    assert (one.checked, one.unbounded, one.breaches) == (6, 6, []), one.__dict__


def _page(cid, entries, steps=()):
    return {"customer_id": cid, "billing_account_id": "BA", "segment": "resi", "periods": [],
            "payments": [], "printed": {"page_ledger": [{"date": d, "running_balance_gbp": b}
                                                        for d, b in entries],
                                        "page_steps": list(steps)}}


def _step(on, amount, kind="missed_payment"):
    return {"date": on, "event_type": "collections_" + kind, "amount_gbp": amount}


def test_every_leg_of_the_page_overdue_row_is_reachable():
    """Overdue within the household's balance across both fuel pages, graded once per step; above
    it and below nothing each breach; a cure and a write-off print no overdue figure."""
    def grade(*steps, gas_steps=()):
        book = {"E": _page("E", [("2020-03-01", 40.0), ("2020-03-20", 0.0)], steps),
                "Eg": _page("Eg", [("2020-03-02", 30.0)], gas_steps)}
        r = _results(book, [{"id": "INV_OVERDUE_WITHIN_PAGE_BALANCE"}])["INV_OVERDUE_WITHIN_PAGE_BALANCE"]
        return r["status"], r["checked"], sorted(b["side"] for b in r["breach_examples"])
    within = _step("2020-03-17", 70.0)                                   # 40 + 30, both fuels
    assert grade(within, gas_steps=[within]) == ("CLEAN", 1, [])         # one step, two pages
    assert grade(_step("2020-03-17", 70.02)) == ("BREACHED", 1, ["above"])
    assert grade(_step("2020-03-25", 30.0), _step("2020-03-26", -1.0, "reminder")) == (
        "BREACHED", 2, ["below"])                                        # E paid off by the 20th
    assert grade(_step("2020-02-20", 5.0)) == ("BREACHED", 1, ["above"])  # nothing owed yet
    assert grade(_step("2020-03-25", 0, "cured"), _step("2020-03-26", 99.0, "write_off"))[1] == 0
    no_page = runner.run([{"id": "INV_OVERDUE_WITHIN_PAGE_BALANCE"}], _ebss_pair())
    assert no_page[0]["status"] == "NOT_IN_EXPORT", no_page


def test_the_exports_carried_forward_read_is_never_graded_as_the_opening_read():
    """Today's export opens every first period on a `carried_forward` read dated period_start, with
    nothing to carry it from. The row graded that read and was CLEAN on 1,293 of 1,293 accounts
    (e6de8acf7). It is a record of no read, so the row says the read is not in the record."""
    book = {"E": _account("E", "electricity", rate=15.0, opening_type=None),
            "G": _account("G", "gas", rate=3.0, kwh_per_month=900.0, opening_type=None)}
    opening = [next(i for i in INVARIANTS if i["id"] == "INV_OPENING_READ")]
    row = _results(book, opening)["INV_OPENING_READ"]
    assert row["status"] == "FLAGGED" and row["flagged"] == row["checked"] == 2, row
    assert all(f["side"].startswith("not in the record") for f in row["flag_examples"])
    # The first CLOSING read is not an opening read either, however early it falls.
    assert row["flag_examples"][0]["value"] is None
    # And the row can be CLEAN: a typed read at supply start is graded.
    typed = {"E": _account("E", "electricity", rate=15.0)}
    assert _results(typed, opening)["INV_OPENING_READ"]["status"] == "CLEAN"


def test_a_catch_up_is_expected_at_its_inclusive_day_count():
    """The prior daily average divides by inclusive days, so the catch-up's days are inclusive too:
    41 days at Jan's 250/31 is 330.6 kWh. 326 kWh is within it; an exclusive count (322.6) flagged it."""
    acct = _late_reader()
    close = acct["periods"][-1]["reads"][-1]
    close["read_kwh"] = acct["periods"][-1]["reads"][0]["read_kwh"] + 326.0
    acct["periods"][-1]["consumption_kwh"] = 326.0
    row = _results({"L": acct}, [{"id": "INV_BACK_BILLING_12M"}])["INV_BACK_BILLING_12M"]
    assert row["status"] == "CLEAN", row["flag_examples"]
    close["read_kwh"] += 6.0                                        # 332 kWh: above 330.6
    row = _results({"L": acct}, [{"id": "INV_BACK_BILLING_12M"}])["INV_BACK_BILLING_12M"]
    assert row["status"] == "FLAGGED", row


def test_the_book_median_classes_an_account_year_by_its_own_registers():
    """A household single-rate in 2020 and two-rate from 2021 is single-rate in 2020. The pooled
    life-time set classed its 2020 as multi-register, so the single-rate row saw none of them."""
    book = {}
    for i in range(10):
        acct = _account("H{}".format(i), "electricity", rate=15.0)
        later = _account("H{}".format(i), "electricity", rate=15.0, year=2021, registers=("1", "2"),
                         start_read=4000.0, opening_type=None)
        acct["periods"] += later["periods"]
        book[acct["customer_id"]] = acct
    inv = {"id": "INV_ANNUAL_USE_BOOK_MEDIAN", "rows": [
        {"from": "2020-01-01", "to": "2020-12-31", "class": "electricity single-rate",
         "lower": 1000, "upper": 2000}]}
    row = _results(book, [inv])["INV_ANNUAL_USE_BOOK_MEDIAN"]
    # Ten single-rate 2020s at 3,000 kWh, above the row's 2,000: graded, and breached.
    assert row["checked"] == 1 and row["status"] == "BREACHED", row


# ── the second cold read's six rows (2026-10-28): each can pass, and each side can fire ──────────

def _printed_account(cid, fuel, printed):
    return {"customer_id": cid, "segment": "resi", "payments": [], "printed": printed,
            "periods": [{"period_start": "2020-01-01", "period_end": "2020-01-31", "commodity": fuel}]}


def _grade_one(inv_id, *accounts, inv=None):
    book = {a["customer_id"]: a for a in accounts}
    r = runner.run([dict(inv or {}, id=inv_id)], book)[0]
    return r["status"], sorted(b["side"] for b in r.get("breach_examples") or ()), r.get("flagged")


def _bill(start, end, kwh=0.0, read="A", close=None, amount=0.0, vat=0.0, **kw):
    return dict(period_start=start, period_end=end, consumption_kwh=kwh, read_type=read,
                closing_read_kwh=close, amount_gbp=amount, vat_gbp=vat, meter_serial="M1", **kw)


def test_every_leg_of_the_revenue_row_is_reachable():
    """Bills before VAT within 1% of the page's revenue pass. Short of it breaches, unless the
    account carries a write-off, which flags (the back-billing write-off is the row's GAP)."""
    def acct(billed, written_off=0.0):
        return _printed_account("R", "electricity", {
            "lifetime_revenue_gbp": 100.0, "page_totals": {"total_written_off_gross_gbp": written_off},
            "invoices": [_bill("2020-01-01", "2020-01-31", amount=billed * 1.05, vat=billed * 0.05)]})
    i = "INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE"
    assert _grade_one(i, acct(100.0))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(80.0))[:2] == ("BREACHED", ["below"])
    assert _grade_one(i, acct(120.0))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct(80.0, written_off=20.0))[0] == "FLAGGED"
    # E: the Energy Price Guarantee support the government paid is revenue the household was not
    # billed, so bills of 60 with 40 of support reconcile to revenue of 100 (residual R2, 2026-10-28).
    crisis = _printed_account("R", "electricity", {
        "lifetime_revenue_gbp": 100.0, "page_totals": {"total_written_off_gross_gbp": 0.0},
        "invoices": [_bill("2023-01-01", "2023-01-31", amount=63.0, vat=3.0, epg_support_gbp=40.0)]})
    assert _grade_one(i, crisis)[:2] == ("CLEAN", [])


def test_every_leg_of_the_payment_record_row_is_reachable():
    """Paid plus missed equal to the bills due passes. A counter of rows, or a missed direct debit
    with no return, breaches."""
    def acct(**rec):
        bills = [_bill("2020-0%d-01" % m, "2020-0%d-28" % m, invoice_number=m, due_date="2020-0%d-15" % (m + 1))
                 for m in (1, 2, 3)]
        return _printed_account("P", "electricity", {
            "invoices": bills, "payment_record": rec, "page_totals": {"as_of_date": "2020-12-31"},
            "page_ledger": [{"invoice_number": m, "method": "direct_debit"} for m in (1, 2, 3)]})
    i = "INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE"
    assert _grade_one(i, acct(payments=2, missed=1, returned=1, missed_dd=1))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(payments=3, missed=4, returned=0))[:2] == ("BREACHED", ["paid + missed != due"])
    assert _grade_one(i, acct(payments=2, missed=1, returned=10))[:2] == (
        "BREACHED", ["returns over three per DD collection"])
    assert _grade_one(i, acct(payments=2, missed=1, returned=0, missed_dd=1))[:2] == (
        "BREACHED", ["missed DD without a return"])


def test_every_leg_of_the_carbon_and_usage_row_is_reachable():
    def acct(kwh, months):
        return _printed_account("C", "gas", {
            "carbon_years": {2020: {"kwh": kwh, "months_billed": months}},
            "usage_monthly": [{"month": "2020-01", "kwh": 600.0}, {"month": "2020-02", "kwh": 600.0}]})
    i = "INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL"
    assert _grade_one(i, acct(1205.0, 2))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(1000.0, 2))[:2] == ("BREACHED", ["below"])
    assert _grade_one(i, acct(1205.0, 3))[:2] == ("BREACHED", ["months"])


def test_leg_three_of_the_carbon_row_breaches_a_part_year_that_prints_a_figure():
    """A whole year printing its kg passes, and so does a part year printing none. A part year
    printing a kg breaches, whether the leg says `full_year` false or (a panel from before the
    field) only its months say so. The partition has a pass on each side and a breach on each."""
    def acct(year_leg):
        return _printed_account("C", "electricity", {"carbon_years": {2020: year_leg}})
    i = "INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL"
    whole = {"kwh": 2700.0, "months_billed": 12, "full_year": True, "co2e_kg": 450.0}
    assert _grade_one(i, acct(whole))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(dict(whole, months_billed=4, full_year=False, co2e_kg=None)))[0] == "UNREACHED"
    assert _grade_one(i, acct(dict(whole, months_billed=4, full_year=False)))[:2] == (
        "BREACHED", ["part year prints a figure"])
    old_panel = {"kwh": 900.0, "months_billed": 4, "co2e_kg": 150.0}
    assert _grade_one(i, acct(old_panel))[:2] == ("BREACHED", ["part year prints a figure"])


def test_every_leg_of_the_smart_meter_row_is_reachable():
    """A Smart account's estimated share within its band passes; above it breaches; none at all
    flags; a traditional meter is not graded; the first bill is not counted."""
    def acct(reads, meter="Smart"):
        bills = [_bill("2020-%02d-01" % m, "2020-%02d-28" % m, read=r) for m, r in enumerate(reads, 1)]
        return _printed_account("S", "electricity", {"meter_type": meter, "invoices": bills})
    i, inv = "INV_SMART_METER_BILLED_ON_ITS_OWN_READS", {"lower": 0.01, "upper": {"electricity": 0.15}}
    assert _grade_one(i, acct("E" + "A" * 9 + "E"), inv=inv)[:2] == ("CLEAN", [])
    assert _grade_one(i, acct("AEEEAAAAAA"), inv=inv)[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct("AAAAAAAAAA"), inv=inv)[0] == "FLAGGED"
    assert _grade_one(i, acct("EEEEEEEEEE", meter="Traditional"), inv=inv)[0] == "UNREACHED"


def test_every_leg_of_the_meter_type_row_is_reachable():
    """The panels agreeing passes (a dash, 'Not recorded' and a null are one state, and HH sits beside
    it); a panel contradicting the header breaches, and so does a missing type rendered as a value
    (omission is not neutrality); a header unlike the meter its reads were taken on breaches; a
    page printing no meter type is not graded. Leg 2 reads the bills' own `meter_type`: a header
    unlike the latest bill's breaches, and so does a type that changes between bills with no
    exchange date on the record. The control: the partition has both a pass and a breach."""
    def acct(header, sample, cast=None, bills=None):
        pm = {"header": header, "sample": sample}
        if cast is not None:
            pm["cast"] = cast
        a = _printed_account("M", "electricity", {"meter_type": header, "panel_meters": pm})
        if bills is not None:
            a["periods"] = [{"period_start": "2020-%02d-01" % m, "period_end": "2020-%02d-28" % m,
                             "commodity": "electricity", "meter_type": t} for m, t in enumerate(bills, 1)]
        return a
    i = "INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT"
    assert _grade_one(i, acct("Smart", True, ["Yes", "Yes"], ["smart", "smart"]))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(None, None, None, [None]))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(None, None, ["Not recorded"]))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct("HH", None, ["Not recorded"]))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct("Traditional", True))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct("Smart", True, ["Yes", "No"]))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct(None, False))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct("HH", True))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct("Traditional", False, None, ["smart"]))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct("Smart", True, None, ["traditional", "smart"]))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct("HH", None, None, ["traditional", "traditional"]))[:2] == ("CLEAN", [])
    assert _grade_one(i, _printed_account("M", "electricity", {"invoices": []}))[0] == "NOT_IN_EXPORT"
    # A book whose bills predate the field (every period None) skips leg 2. One typed bill anywhere
    # in the book and an untyped bill under a Smart header is a breach again.
    old_book = acct("Smart", True, None, [None, None])
    assert _grade_one(i, old_book)[:2] == ("CLEAN", [])
    typed = dict(acct("Smart", True, None, ["smart"]), customer_id="T")
    assert _grade_one(i, old_book, typed)[:2] == ("BREACHED", ["above"])


def test_every_leg_of_the_estimate_follows_the_reads_row_is_reachable():
    """An estimate at the rate the last reads show passes; three times it breaches; one bill with a
    single read before it is not graded."""
    def acct(est_kwh_per_day):
        bills = [_bill("2020-01-01", "2020-01-31", 310.0, "A", close=310.0),
                 _bill("2020-02-01", "2020-02-29", 290.0, "A", close=600.0),
                 _bill("2020-03-01", "2020-03-31", est_kwh_per_day * 31, "E", days_in_period=31)]
        return _printed_account("E", "electricity", {"invoices": bills})
    i = "INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS"
    assert _grade_one(i, acct(10.0))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(30.0))[:2] == ("BREACHED", ["above"])
    assert _grade_one(i, acct(1.0))[:2] == ("BREACHED", ["below"])
    one = _printed_account("E", "electricity", {"invoices": [
        _bill("2020-01-01", "2020-01-31", 310.0, "A", close=310.0),
        _bill("2020-02-01", "2020-02-29", 999.0, "E", days_in_period=29)]})
    assert _grade_one(i, one)[0] == "UNREACHED"


def test_the_estimate_row_holds_every_advance_the_published_methods_allow_and_none_past_them():
    """The row's long reference is an advance of six months (the AA) to 36 months (Xoserve's AQ),
    from an actual read or the change-of-supply opening read: an estimate following a 425-day
    advance, or one opening on the change-of-supply read, is lawful. The row used to stop at 365
    days and at actual reads, and breached 67 such bills on the 209c3350ab book. Past 36 months the
    old level is no reference, and the same estimate still breaches."""
    i = "INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS"

    def over_a_year(first_read_day):
        # 10 kWh a day from the first read, then a month at 2: the estimate follows the long advance.
        days = (runner._d("2020-02-29") - runner._d(first_read_day)).days
        return _printed_account("Y", "electricity", {"invoices": [
            _bill(first_read_day[:8] + "01", first_read_day, 310.0, "A", close=20000.0 - 10.0 * days),
            _bill("2020-02-01", "2020-02-29", 290.0, "A", close=20000.0),
            _bill("2020-03-01", "2020-03-31", 62.0, "A", close=20062.0),
            _bill("2020-04-01", "2020-04-30", 8.0 * 30, "E", days_in_period=30)]})
    assert _grade_one(i, over_a_year("2019-01-31"))[:2] == ("CLEAN", [])
    assert _grade_one(i, over_a_year("2016-12-31"))[:2] == ("BREACHED", ["above"])
    from_the_switch = _printed_account("C", "electricity", {"invoices": [
        _bill("2019-09-01", "2019-09-30", 300.0, "E", opening_read_kwh=0.0, days_in_period=30),
        _bill("2019-10-01", "2020-02-29", 1500.0, "A", close=1800.0),
        _bill("2020-03-01", "2020-03-31", 62.0, "A", close=1862.0),
        _bill("2020-04-01", "2020-04-30", 8.0 * 30, "E", days_in_period=30)]})
    assert _grade_one(i, from_the_switch)[:2] == ("CLEAN", [])
    from_the_switch["printed"]["invoices"][0]["opening_read_kwh"] = None
    assert _grade_one(i, from_the_switch)[:2] == ("BREACHED", ["above"])


def test_every_leg_of_the_estimated_run_against_the_meter_row_is_reachable():
    """A run billed near the meter's own rate passes; a run at zero while the meter advanced (the
    occupier's zero window) breaches; twice the meter only flags; a single estimate is not a run."""
    def acct(per_day, n=2):
        bills = [_bill("2020-01-01", "2020-01-31", 310.0, "A", close=310.0)]
        bills += [_bill("2020-%02d-01" % m, "2020-%02d-28" % m, per_day * 28, "E") for m in range(2, 2 + n)]
        bills += [_bill("2020-%02d-01" % (2 + n), "2020-%02d-28" % (2 + n), 0.0, "A",
                        close=310.0 + 10.0 * (28 * (n + 1) + 3))]
        return _printed_account("M", "electricity", {"invoices": bills})
    i = "INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER"
    assert _grade_one(i, acct(10.0))[:2] == ("CLEAN", [])
    assert _grade_one(i, acct(0.0))[:2] == ("BREACHED", ["below"])
    assert _grade_one(i, acct(22.0))[0] == "FLAGGED"
    assert _grade_one(i, acct(0.0, n=1))[0] == "UNREACHED"


# ── the five rows the raw export could not grade (2026-10-30): each can pass, and each leg can fire ──

def _count(inv_id, *accounts, inv=None):
    """(status, breaches, the sides breached): the count, since the examples stop at five."""
    r = runner.run([dict(inv or {}, id=inv_id)], {a["customer_id"]: a for a in accounts})[0]
    return r["status"], r.get("breached"), {b["side"] for b in r.get("breach_examples") or ()}


def test_every_leg_of_the_svt_one_price_row_is_reachable():
    row = "INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW"
    same = [_account(c, "electricity", rate=15.0) for c in ("A", "B", "C")]
    assert _grade_one(row, *same)[0] == "CLEAN"
    assert _count(row, *same, _account("D", "electricity", rate=16.0)) == ("BREACHED", 12, {"above"})
    assert _count(row, *same, _account("D", "electricity", rate=15.0, sc=0.30)) == ("BREACHED", 12, {"above"})
    # Another payment method is another price, and an account alone in its group is not compared.
    assert _grade_one(row, *same, _account("P", "electricity", rate=16.0, method="prepayment"))[0] == "CLEAN"
    assert _grade_one(row, *same, _account("F", "electricity", rate=16.0, tariff="fixed"))[0] == "CLEAN"


def test_the_svt_one_price_standing_charge_is_graded_to_the_penny_over_a_one_day_bill():
    """Catches the half-penny-a-day tolerance read alone. The 3dc5a92948 book's one SVT breach after
    the writers-1-2 gate was SYN-2016-101g's one-day final gas bill: 0.215 x 1 day billed 0.22, printed
    0.22/day. Both legs: that print is clean, and the same one-day bill 2p over the period breaches."""
    row = "INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW"
    same = [_account(c, "gas", rate=2.5714, sc=0.215) for c in ("A", "B", "C")]

    def one_day(sc):
        acct = _account("D", "gas", rate=2.5714, sc=0.215)
        p = acct["periods"][2]
        p.update(period_end=p["period_start"], days_in_period=1, standing_charge_gbp_per_day=sc)
        return acct
    assert _grade_one(row, *same, one_day(0.22))[0] == "CLEAN"
    assert _count(row, *same, one_day(0.235)) == ("BREACHED", 1, {"above"})


def test_every_leg_of_the_epg_row_is_reachable():
    inv = {"rows": [{"from": "2022-10-01", "to": "2023-06-30", "commodity": "electricity", "upper": 32.381}]}
    row = "INV_UNIT_RATE_EPG_HOUSEHOLD"
    # The fixture's network and policy rate is 50 GBP/MWh, 5p: the household's all-in rate is rate + 5.
    assert _grade_one(row, _account("E", "electricity", rate=27.38, year=2022), inv=inv)[0] == "CLEAN"
    assert _count(row, _account("E", "electricity", rate=27.5, year=2022), inv=inv) == ("BREACHED", 3, {"above"})
    assert _grade_one(row, _account("E", "electricity", rate=27.5, year=2022, tariff="fixed"), inv=inv)[0] == "UNREACHED"
    assert _grade_one(row, _account("E", "electricity", rate=27.5, year=2021), inv=inv)[0] == "UNREACHED"


def _estimated(runs, actual_month=None):
    acct = _account("G", "gas", rate=3.0, read_type="E", kwh_per_month=900.0)
    if actual_month is not None:
        p = acct["periods"][actual_month]
        next(r for r in p["reads"] if r["read_date"] == p["period_end"])["read_type"] = "A"
    acct["printed"] = {"estimate_runs": [dict(n=n, iso=iso, never_read=never) for n, iso, never in runs]}
    return acct


def test_every_leg_of_the_estimate_run_row_is_reachable():
    row = "INV_ESTIMATE_RUN_WITHIN_TENURE"
    assert _grade_one(row, _estimated([(12, "2020-12-31", True)]))[0] == "CLEAN"
    assert _grade_one(row, _estimated([(12, "2020-06-30", False)]))[1] == ["above bills issued"]
    assert _grade_one(row, _estimated([(9, "2020-12-31", False)], actual_month=2))[0] == "CLEAN"
    assert _grade_one(row, _estimated([(10, "2020-12-31", False)], actual_month=2))[1] == [
        "above the longest estimated run"]
    assert _grade_one(row, _estimated([(9, "2020-12-31", True)], actual_month=2))[1] == [
        "actual reads on a leg printed as never read"]
    # Without the page the row is unrun, never clean.
    bare = _estimated([])
    bare["printed"] = {}
    assert _grade_one(row, bare)[0] == "NOT_IN_EXPORT"
