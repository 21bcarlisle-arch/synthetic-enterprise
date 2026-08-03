"""Tests for SITE_EH3_figure_reconciliation_and_periods (2026-07-29 cold-eyes
Expert Hour MAJOR-4/MAJOR-6): the dashboard-side half of the fix -- a bad-debt
reconciliation bridge (mirroring the existing settled<->billed margin_bridge
pattern) and a real, data-derived period-coverage flag per published annual
row (never a hardcoded "this year is partial").

R11: the values asserted here are the actual outputs of extract_financial()
and the two new gates, not a restated source string.
R15 (both ways, three killer patterns guarded explicitly):
  - TAUTOLOGY: the period-coverage gate cross-checks two INDEPENDENTLY
    stored fields (period_partial vs period_coverage_fraction) against each
    other, and the bad-debt gate re-derives the annual total from the raw
    per-year rows rather than trusting the stored aggregate back at itself.
  - FAIL-OPEN: missing/malformed/non-finite inputs must FAIL the gate, not
    pass silently.
  - FAIL-SILENT: an unavailable/corrupt reconciliation block is a FAILED
    check, not a skipped one.
"""
import json
import math
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools import generate_dashboard_data
from tools.generate_dashboard_data import (
    extract_financial,
    _load_sim_window,
    _year_coverage_fraction,
    _period_note,
    _check_bad_debt_reconciliation_present,
    _check_period_coverage_present,
)

DASHBOARD_PATH = Path(__file__).resolve().parents[2] / "site" / "data" / "dashboard.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _financial_data_with_bad_debt():
    """A run-output-shaped fixture with the exact class of defect this atom
    closes: the annual (headline) bad-debt series is tiny and goes negative
    one year, while the ledger (accrual) figure is ~2.4% of revenue -- the
    two are ~100x apart, same shape as the real 129.6x divergence found."""
    return {
        "years": {
            "2016": {"revenue_gbp": 100_000.0, "net_gbp": 5_000.0, "bad_debt_gbp": 10.0, "bills_count": 50},
            "2017": {"revenue_gbp": 200_000.0, "net_gbp": 8_000.0, "bad_debt_gbp": -5.0, "bills_count": 60},
        },
        "ledger_pnl": {"revenue_gbp": 300_000.0, "bad_debt_gbp": 7_200.0},
        "management_accounts": {},
    }


def _sim_window_file(tmp_path, period_from="2016-01-01", period_to="2017-06-15"):
    p = tmp_path / "sim_data.json"
    p.write_text(json.dumps({"metadata": {"period_from": period_from, "period_to": period_to}}))
    return p


# ---------------------------------------------------------------------------
# _load_sim_window / _year_coverage_fraction / _period_note
# ---------------------------------------------------------------------------

def test_load_sim_window_reads_real_dates(tmp_path, monkeypatch):
    p = _sim_window_file(tmp_path)
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", p)
    d_from, d_to = _load_sim_window()
    assert d_from == date(2016, 1, 1)
    assert d_to == date(2017, 6, 15)


def test_load_sim_window_missing_file_returns_none_none(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", tmp_path / "nope.json")
    assert _load_sim_window() == (None, None)


def test_load_sim_window_malformed_json_returns_none_none(tmp_path, monkeypatch):
    p = tmp_path / "sim_data.json"
    p.write_text("not valid json {{{")
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", p)
    assert _load_sim_window() == (None, None)


def test_year_coverage_fraction_full_year_is_one():
    assert _year_coverage_fraction(2016, date(2015, 11, 7), date(2025, 6, 7)) == 1.0


def test_year_coverage_fraction_partial_tail_year():
    # 2025-01-01 .. 2025-06-07 inclusive = 158 days of 365 = 0.4329 (matches
    # the real committed run's own 2025 stub exactly).
    frac = _year_coverage_fraction(2025, date(2015, 11, 7), date(2025, 6, 7))
    assert frac == 0.4329


def test_year_coverage_fraction_unavailable_window_is_none():
    assert _year_coverage_fraction(2025, None, None) is None


def test_period_note_none_for_full_year():
    assert _period_note(2016, 1.0, date(2016, 1, 1), date(2025, 6, 7)) is None


def test_period_note_states_dates_and_fraction_for_partial_year():
    note = _period_note(2025, 0.4329, date(2015, 11, 7), date(2025, 6, 7))
    assert "2025-01-01" in note
    assert "2025-06-07" in note
    assert "43%" in note
    assert "PART YEAR" in note
    assert "excluded" in note.lower()


def test_period_note_unknown_when_coverage_none():
    note = _period_note(2025, None, None, None)
    assert "unknown" in note.lower()


# ---------------------------------------------------------------------------
# extract_financial: bad_debt_reconciliation
# ---------------------------------------------------------------------------

def test_extract_financial_bad_debt_reconciliation_present():
    r = extract_financial(_financial_data_with_bad_debt())
    br = r["bad_debt_reconciliation"]
    assert br["annual_series_total_gbp"] == 5.0  # 10.0 + (-5.0)
    assert br["ledger_total_gbp"] == 7_200.0
    assert br["authoritative"] == "ledger"
    assert br["ratio_x"] == round(7_200.0 / 5.0, 2)
    assert "arrears_engine" in br["annual_series_basis"]
    assert "management_accounts" in br["ledger_basis"] or "PnL" in br["ledger_basis"]


def test_extract_financial_bad_debt_reconciliation_ratio_none_when_annual_total_zero():
    data = _financial_data_with_bad_debt()
    data["years"]["2016"]["bad_debt_gbp"] = 0.0
    data["years"]["2017"]["bad_debt_gbp"] = 0.0
    r = extract_financial(data)
    assert r["bad_debt_reconciliation"]["annual_series_total_gbp"] == 0.0
    assert r["bad_debt_reconciliation"]["ratio_x"] is None  # never a ZeroDivisionError


def test_extract_financial_ledger_bad_debt_matches_reconciliation_ledger_total():
    r = extract_financial(_financial_data_with_bad_debt())
    assert r["ledger"]["bad_debt_gbp"] == r["bad_debt_reconciliation"]["ledger_total_gbp"]


# ---------------------------------------------------------------------------
# extract_financial: period coverage (per annual row + segment_annual row)
# ---------------------------------------------------------------------------

def test_extract_financial_period_coverage_full_and_partial_years(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", _sim_window_file(tmp_path))
    r = extract_financial(_financial_data_with_bad_debt())
    rows = {row["year"]: row for row in r["annual"]}
    assert rows[2016]["period_partial"] is False
    assert rows[2016]["period_coverage_fraction"] == 1.0
    assert rows[2016]["period_note"] is None
    assert rows[2017]["period_partial"] is True
    assert rows[2017]["period_coverage_fraction"] < 1.0
    assert "PART YEAR" in rows[2017]["period_note"]


def test_extract_financial_sim_window_and_source_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", _sim_window_file(tmp_path))
    r = extract_financial(_financial_data_with_bad_debt())
    assert r["sim_window"] == "2016-01-01 to 2017-06-15"
    assert "sim_data.json" in r["period_coverage_source"]


def test_extract_financial_period_coverage_unavailable_when_sim_window_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", tmp_path / "absent.json")
    r = extract_financial(_financial_data_with_bad_debt())
    assert r["sim_window"] is None
    assert r["period_coverage_source"] == "unavailable"
    for row in r["annual"]:
        assert row["period_coverage_fraction"] is None
        assert row["period_partial"] is False  # unknown != asserted-partial
        assert "unknown" in row["period_note"].lower()


def test_extract_financial_segment_annual_carries_period_coverage(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", _sim_window_file(tmp_path))
    data = _financial_data_with_bad_debt()
    data["years"]["2017"]["segment_split"] = {"I&C Electricity": {"revenue_gbp": 1000.0, "gross_gbp": 200.0, "net_gbp": 100.0}}
    r = extract_financial(data)
    seg_2017 = [row for row in r["segment_annual"] if row["year"] == 2017][0]
    assert seg_2017["period_partial"] is True


# ---------------------------------------------------------------------------
# _check_bad_debt_reconciliation_present -- R15 both ways
# ---------------------------------------------------------------------------

def test_check_bad_debt_reconciliation_passes_for_real_extract_financial():
    financial = extract_financial(_financial_data_with_bad_debt())
    assert _check_bad_debt_reconciliation_present(financial) is True


def test_check_bad_debt_reconciliation_fails_when_block_missing(capsys):
    assert _check_bad_debt_reconciliation_present({"annual": []}) is False
    assert "BAD-DEBT RECONCILIATION GATE FAILED" in capsys.readouterr().err


def test_check_bad_debt_reconciliation_fails_when_required_field_missing(capsys):
    financial = extract_financial(_financial_data_with_bad_debt())
    del financial["bad_debt_reconciliation"]["ledger_basis"]
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "ledger_basis" in capsys.readouterr().err


def test_check_bad_debt_reconciliation_fails_on_non_finite_annual_total(capsys):
    financial = extract_financial(_financial_data_with_bad_debt())
    financial["bad_debt_reconciliation"]["annual_series_total_gbp"] = float("nan")
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "not a finite number" in capsys.readouterr().err


def test_check_bad_debt_reconciliation_fails_on_non_finite_ledger_total(capsys):
    financial = extract_financial(_financial_data_with_bad_debt())
    financial["bad_debt_reconciliation"]["ledger_total_gbp"] = float("inf")
    assert _check_bad_debt_reconciliation_present(financial) is False


def test_check_bad_debt_reconciliation_fails_when_stored_total_drifts_from_resum(capsys):
    # Anti-tautology: the gate independently re-sums financial['annual'] --
    # corrupting ONLY the stored aggregate (not the rows) must be caught.
    financial = extract_financial(_financial_data_with_bad_debt())
    financial["bad_debt_reconciliation"]["annual_series_total_gbp"] = 999_999.0
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "disagrees with an independent re-sum" in capsys.readouterr().err


def test_check_bad_debt_reconciliation_fails_when_authoritative_not_ledger(capsys):
    financial = extract_financial(_financial_data_with_bad_debt())
    financial["bad_debt_reconciliation"]["authoritative"] = "annual"
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "authoritative" in capsys.readouterr().err.lower()


def test_check_bad_debt_reconciliation_true_against_real_committed_dashboard():
    """The real, committed site/data/dashboard.json must itself pass this gate."""
    dashboard = json.loads(DASHBOARD_PATH.read_text())
    assert _check_bad_debt_reconciliation_present(dashboard["financial"]) is True


# ---------------------------------------------------------------------------
# _check_period_coverage_present -- R15 both ways
# ---------------------------------------------------------------------------

def test_check_period_coverage_passes_for_real_extract_financial(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", _sim_window_file(tmp_path))
    financial = extract_financial(_financial_data_with_bad_debt())
    assert _check_period_coverage_present(financial) is True


def test_check_period_coverage_passes_when_no_annual_rows():
    assert _check_period_coverage_present({"annual": []}) is True


def test_check_period_coverage_fails_when_fields_missing(capsys):
    assert _check_period_coverage_present({"annual": [{"year": 2020}]}) is False
    assert "missing period_coverage_fraction" in capsys.readouterr().err


def test_check_period_coverage_fails_on_non_finite_fraction(capsys):
    rows = [{"year": 2020, "period_coverage_fraction": float("nan"), "period_partial": False}]
    assert _check_period_coverage_present({"annual": rows}) is False
    assert "not a finite number" in capsys.readouterr().err


def test_check_period_coverage_fails_on_out_of_range_fraction(capsys):
    rows = [{"year": 2020, "period_coverage_fraction": 1.5, "period_partial": False}]
    assert _check_period_coverage_present({"annual": rows}) is False
    assert "out of [0,1] range" in capsys.readouterr().err


def test_check_period_coverage_fails_when_partial_flag_disagrees_with_fraction(capsys):
    # anti-tautology: cross-checks two independently-settable stored fields.
    rows = [{"year": 2025, "period_coverage_fraction": 0.5, "period_partial": False}]
    assert _check_period_coverage_present({"annual": rows}) is False
    assert "disagrees with" in capsys.readouterr().err
    rows2 = [{"year": 2016, "period_coverage_fraction": 1.0, "period_partial": True}]
    assert _check_period_coverage_present({"annual": rows2}) is False


def test_check_period_coverage_fails_when_partial_year_has_no_note(capsys):
    rows = [{"year": 2025, "period_coverage_fraction": 0.4, "period_partial": True, "period_note": None}]
    assert _check_period_coverage_present({"annual": rows}) is False
    assert "no period_note" in capsys.readouterr().err


def test_check_period_coverage_true_against_real_committed_dashboard():
    """The real, committed site/data/dashboard.json must itself pass this gate --
    including its real partial 2025 row."""
    dashboard = json.loads(DASHBOARD_PATH.read_text())
    financial = dashboard["financial"]
    assert _check_period_coverage_present(financial) is True
    partial_years = [r["year"] for r in financial["annual"] if r["period_partial"]]
    assert 2025 in partial_years


def test_real_committed_dashboard_bad_debt_bridge_is_self_consistent():
    """R11 against the live artifact -- but asserting the BRIDGE RELATIONSHIP, not a
    pinned magnitude.

    This test previously pinned ratio_x == 129.61, the divergence the atom's evidence
    happened to observe on the 2026-06-18 run. That is a generated value: it is a
    property of one run's data, not of the mechanism. Regenerating dashboard.json from
    any other run moves it (this run reconciles at 1.0x, both figures GBP 1,944.15) and
    the control would red-flag a perfectly healthy artifact -- the pinned-generated-value
    class that has cost this project a multi-day publish blackout before.

    The invariant the atom actually closes is: bad debt is published ONCE, with both
    measurements present, the ledger named authoritative, and a ratio that genuinely
    bridges the two. That is what is asserted here, so the control still fires on a
    broken or absent bridge (R15) while surviving legitimate data movement.
    """
    dashboard = json.loads(DASHBOARD_PATH.read_text())
    br = dashboard["financial"]["bad_debt_reconciliation"]

    annual = br["annual_series_total_gbp"]
    ledger = br["ledger_total_gbp"]
    ratio = br["ratio_x"]

    # R15, reject non-finite FIRST: a NaN/None ratio is a failed bridge, not a pass.
    for name, val in (("annual", annual), ("ledger", ledger)):
        assert isinstance(val, (int, float)) and math.isfinite(val), f"{name} not finite"
    assert ratio is not None and math.isfinite(ratio), "ratio_x missing/non-finite"

    # The ratio must actually be the bridge between the two published figures.
    assert math.isclose(ratio, ledger / annual, rel_tol=1e-6), (
        f"ratio_x {ratio} does not bridge ledger {ledger} / annual {annual}"
    )

    # Both bases must be stated, and the ledger is the authoritative figure.
    assert br["authoritative"] == "ledger"
    assert br["annual_series_basis"] and br["ledger_basis"]
