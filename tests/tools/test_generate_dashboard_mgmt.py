import json
import pathlib
import pytest
from tools.generate_dashboard_data import extract_management_accounts


def _make_data(years_range=(2016, 2018), rev=500000.0, wholesale=300000.0,
               non_comm=50000.0, capital=20000.0, bad_debt=5000.0,
               cts=10000.0, fixed=15000.0, acq=8000.0, ct_triplet=None):
    gross = rev - wholesale - non_comm
    total_opex = capital + bad_debt + cts + fixed + acq
    net = gross - total_opex
    ma = {}
    for yr in range(years_range[0], years_range[1] + 1):
        stmt = {
            "revenue_gbp": rev,
            "wholesale_cost_gbp": wholesale,
            "non_commodity_cost_gbp": non_comm,
            "gross_margin_gbp": gross,
            "capital_cost_gbp": capital,
            "bad_debt_gbp": bad_debt,
            "cost_to_serve_gbp": cts,
            "fixed_cost_gbp": fixed,
            "acquisition_spend_gbp": acq,
            "total_opex_gbp": total_opex,
            "net_margin_gbp": net,
        }
        if ct_triplet is not None:
            stmt.update(ct_triplet)
        ma[str(yr)] = {"income_statement": stmt}
    return {"management_accounts": ma}


def test_extract_mgmt_accounts_keys():
    result = extract_management_accounts(_make_data())
    assert "annual" in result
    row = result["annual"][0]
    expected = ["year", "revenue_gbp", "wholesale_cost_gbp", "non_commodity_cost_gbp",
                "gross_margin_gbp", "capital_cost_gbp", "bad_debt_gbp",
                "cost_to_serve_gbp", "fixed_cost_gbp", "acquisition_spend_gbp",
                "total_opex_gbp", "net_margin_gbp", "net_margin_pct",
                "profit_before_tax_gbp", "corporation_tax_gbp", "profit_for_year_gbp"]
    for k in expected:
        assert k in row, f"missing key: {k}"


def test_extract_mgmt_accounts_ct_triplet_none_when_absent():
    """E1 Corporation Tax triplet (2026-07-11 HARDEN-sweep Expert Hour finding): must be
    None, not silently defaulted to 0, when the source income_statement never computed it
    (e.g. income_statement() called without a year -- the pre-existing, still-valid case)."""
    result = extract_management_accounts(_make_data())
    row = result["annual"][0]
    assert row["profit_before_tax_gbp"] is None
    assert row["corporation_tax_gbp"] is None
    assert row["profit_for_year_gbp"] is None


def test_extract_mgmt_accounts_ct_triplet_present_when_computed():
    data = _make_data(ct_triplet={
        "profit_before_tax_gbp": 470392.87,
        "corporation_tax_gbp": 117598.22,
        "profit_for_year_gbp": 352794.65,
    })
    row = extract_management_accounts(data)["annual"][0]
    assert row["profit_before_tax_gbp"] == pytest.approx(470392.87)
    assert row["corporation_tax_gbp"] == pytest.approx(117598.22)
    assert row["profit_for_year_gbp"] == pytest.approx(352794.65)


def test_extract_mgmt_accounts_profit_for_year_is_after_tax():
    data = _make_data(ct_triplet={
        "profit_before_tax_gbp": 100000.0,
        "corporation_tax_gbp": 19000.0,
        "profit_for_year_gbp": 81000.0,
    })
    row = extract_management_accounts(data)["annual"][0]
    assert row["profit_for_year_gbp"] == pytest.approx(
        row["profit_before_tax_gbp"] - row["corporation_tax_gbp"]
    )


def test_extract_mgmt_accounts_annual_length():
    data = _make_data(years_range=(2016, 2025))
    result = extract_management_accounts(data)
    assert len(result["annual"]) == 10


def test_extract_mgmt_accounts_years_ordered():
    data = _make_data(years_range=(2016, 2025))
    result = extract_management_accounts(data)
    years = [r["year"] for r in result["annual"]]
    assert years == list(range(2016, 2026))


def test_net_margin_pct_computed():
    data = _make_data(rev=1000000.0)
    result = extract_management_accounts(data)
    row = result["annual"][0]
    expected_pct = round(row["net_margin_gbp"] / row["revenue_gbp"] * 100, 2)
    assert abs(row["net_margin_pct"] - expected_pct) < 0.01


def test_empty_management_accounts():
    result = extract_management_accounts({})
    assert result == {"annual": []}


def test_zero_revenue_no_crash():
    data = {"management_accounts": {"2022": {"income_statement": {"revenue_gbp": 0}}}}
    result = extract_management_accounts(data)
    assert result["annual"][0]["net_margin_pct"] == 0.0


def test_revenue_positive():
    data = _make_data(years_range=(2016, 2025), rev=500000.0)
    result = extract_management_accounts(data)
    for row in result["annual"]:
        assert row["revenue_gbp"] > 0


def test_gross_margin_relationship():
    result = extract_management_accounts(_make_data())
    row = result["annual"][0]
    implied = row["revenue_gbp"] - row["wholesale_cost_gbp"] - row["non_commodity_cost_gbp"]
    assert abs(row["gross_margin_gbp"] - implied) < 1.0


def test_net_margin_positive_in_good_year():
    data = _make_data(rev=1000000.0, wholesale=400000.0)
    result = extract_management_accounts(data)
    assert result["annual"][0]["net_margin_gbp"] > 0


def test_mgmt_accounts_in_dashboard_json(tmp_path, monkeypatch):
    """generate() writes management_accounts into the dashboard payload.

    HERMETIC (tmp OUTPUT_PATH), matching the sibling generate() tests in
    test_website_integrity_fix.py / test_query_interface.py. It previously wrote
    the REAL site/data/dashboard.json and asserted generate()'s return value,
    which wedged the publish gate for ~5h on 2026-07-29:

      - generate()'s return value is the CONSISTENCY-gate result, which compares
        the loaded run against docs/observability/run_insights.json. The publish
        pipeline writes run_insights.json from the QUEUED MARKER's run json,
        while this test loaded docs/reports/run_output_latest.json -- which the
        sim runner had already advanced to a NEWER run. A sim run completes
        every ~462s but one processing cycle takes ~600s (the 391s gate
        included), so the marker queue is always behind and the two files name
        two different runs. Two runs disagree on every headline figure, so the
        gate went RED every cycle and the queue grew without bound
        (observed: net 1521069.65 from marker run 6b03593b3 vs 1501000.74 from
        run_output_latest.json's run e2f892e4c -- staleness, not a regression).
      - It also rewrote the live site/data/dashboard.json mid-pipeline from a
        source the pipeline had not published.

    Cross-surface consistency is NOT this test's claim and keeps its own
    dedicated coverage (test_website_integrity_fix.py::test_check_consistency_
    gate_result_propagates_from_generate), and the live pipeline still enforces
    it via generate()'s return value in process_run_complete.generate_dashboard_
    json -- so dropping the `ok` assert here opens no fail-open.
    """
    rj = pathlib.Path("docs/reports/run_output_latest.json")
    if not rj.exists():
        pytest.skip("run_output_latest.json not present")
    import tools.generate_dashboard_data as gdd

    out_path = tmp_path / "dashboard.json"
    monkeypatch.setattr(gdd, "OUTPUT_PATH", out_path)
    gdd.generate(rj)

    db = json.loads(out_path.read_text())
    assert "management_accounts" in db
    assert len(db["management_accounts"]["annual"]) >= 1


def test_mgmt_accounts_test_does_not_write_the_live_dashboard():
    """R15 mutation-anchor for the wedge above: the live publish surface must
    not be a test's output path. A publish-gate test that writes the artefact
    the pipeline just published can red on legitimate progress (and can clobber
    it), so pin the tmp-output contract rather than trusting the prose."""
    src = pathlib.Path(__file__).read_text()
    body = src.split("def test_mgmt_accounts_in_dashboard_json", 1)[1]
    body = body.split("\ndef test_mgmt_accounts_test_does_not_write", 1)[0]
    code = "\n".join(ln for ln in body.splitlines() if not ln.strip().startswith("-"))
    assert 'monkeypatch.setattr(gdd, "OUTPUT_PATH"' in code, \
        "the generate() test must redirect OUTPUT_PATH to tmp_path"
    assert 'json.loads(pathlib.Path("site/data/dashboard.json")' not in code, \
        "the generate() test must not read back the live site/data/dashboard.json"


def test_extract_mgmt_accounts_single_year():
    data = _make_data(years_range=(2022, 2022))
    result = extract_management_accounts(data)
    assert len(result["annual"]) == 1
    assert result["annual"][0]["year"] == 2022


def test_total_opex_positive():
    result = extract_management_accounts(_make_data())
    for row in result["annual"]:
        assert row.get("total_opex_gbp", 0) > 0


def test_net_margin_below_gross():
    result = extract_management_accounts(_make_data())
    row = result["annual"][0]
    assert row["net_margin_gbp"] < row["gross_margin_gbp"]
