"""SITE_EH3_figure_reconciliation_and_periods -- the dashboard/world half.

Closes the 2026-07-29 cold-eyes Expert Hour findings MAJOR-4 / MAJOR-5 /
MAJOR-6, which are three faces of ONE class: a published figure whose own basis
is not defensible.

  MAJOR-4  bad debt was published TWICE (annual/settled series vs ledger/billed
           accrual, ~130x apart, the annual one able to go NEGATIVE) with no
           bridge between them.
  MAJOR-5  margin was the only headline metric with no external plausibility
           band, which is precisely the metric where R12's band matters most.
  MAJOR-6  a part-year stub rendered as an undifferentiated annual row.

R12 (BINDING): every band here is a DIAGNOSTIC FLAG that triggers R4 diagnosis.
Nothing in this file, and nothing the code under test does, moves a model
parameter toward a benchmark. The margin anchor is expected to read RED and is
asserted to be ALLOWED to read RED.

R15 (three killer patterns, mutation-proven both ways):
  TAUTOLOGY   -- the period gate cross-checks two INDEPENDENTLY-STORED fields
                 (period_partial vs period_coverage_fraction, plus period_note);
                 the bad-debt gate re-derives the annual total from the RAW
                 per-year rows and cross-checks the ledger side against the
                 separately-stored financial.ledger.bad_debt_gbp.
  FAIL-OPEN   -- missing / empty / zero-row / out-of-range / non-finite input
                 must FAIL every gate.
  FAIL-SILENT -- an unavailable or malformed block is a FAILED check, never a
                 skipped one.

NEVER PIN A GENERATED VALUE (standing rule; a pinned RNG date once caused a
4-day publish blackout). Every assertion against the LIVE artefacts below is a
RELATIONSHIP -- the published sim_window re-derives the published partial set,
the stored aggregate re-sums from its own rows -- never a literal ratio, date or
figure copied out of today's run.
"""
import json
import math
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))

from tools import generate_dashboard_data  # noqa: E402
from tools.generate_dashboard_data import (  # noqa: E402
    _build_bad_debt_reconciliation,
    _check_bad_debt_reconciliation_present,
    _check_period_coverage_present,
    _load_sim_window,
    _period_note,
    _year_coverage_fraction,
    extract_financial,
)
from tools import generate_world_data  # noqa: E402
from tools.generate_world_data import (  # noqa: E402
    _MARGIN_BAND_HIGH_PCT,
    _MARGIN_BAND_LOW_PCT,
    _margin_anchor_card,
    _margin_plausibility_anchor,
)

DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
WORLD_PATH = PROJECT / "site" / "data" / "world.json"


# ---------------------------------------------------------------------------
# Fixtures -- literal, in-process, deterministic. Nothing here reads live data.
# ---------------------------------------------------------------------------

def _run_data():
    """Run-output-shaped data carrying the exact defect class: a tiny annual
    bad-debt series that goes NEGATIVE one year, against a ledger accrual ~100x
    larger -- the same shape as the real divergence the atom cites."""
    return {
        "years": {
            "2016": {"revenue_gbp": 100_000.0, "net_gbp": 5_000.0,
                     "bad_debt_gbp": 10.0, "bills_count": 50},
            "2017": {"revenue_gbp": 200_000.0, "net_gbp": 8_000.0,
                     "bad_debt_gbp": -5.0, "bills_count": 60},
        },
        "management_accounts": {
            "2016": {"income_statement": {"revenue_gbp": 120_000.0}},
            "2017": {"income_statement": {"revenue_gbp": 240_000.0}},
        },
        "ledger_pnl": {"revenue_gbp": 300_000.0, "bad_debt_gbp": 7_200.0},
    }


def _window_file(tmp_path, period_from="2016-01-01", period_to="2017-06-15"):
    path = tmp_path / "sim_data.json"
    path.write_text(json.dumps(
        {"metadata": {"period_from": period_from, "period_to": period_to}}))
    return path


@pytest.fixture
def windowed(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", _window_file(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# _load_sim_window -- fail-closed on every unreadable shape
# ---------------------------------------------------------------------------

def test_load_sim_window_reads_the_real_dates(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", _window_file(tmp_path))
    assert _load_sim_window() == (date(2016, 1, 1), date(2017, 6, 15))


@pytest.mark.parametrize("payload", [
    None,                                             # file absent
    "not json {{{",                                   # malformed
    '["a", "list"]',                                  # not an object
    '{"metadata": null}',                             # metadata not a dict
    '{"metadata": {}}',                               # no dates
    '{"metadata": {"period_from": "2016-01-01"}}',    # half a window
    '{"metadata": {"period_from": "nonsense", "period_to": "2017-01-01"}}',
    '{"metadata": {"period_from": "2017-01-01", "period_to": "2016-01-01"}}',  # inverted
])
def test_load_sim_window_fails_closed(tmp_path, monkeypatch, payload):
    """FAIL-SILENT closed: every unusable window yields (None, None), which
    callers must treat as UNKNOWN -- never as a silently complete year."""
    path = tmp_path / "sim_data.json"
    if payload is not None:
        path.write_text(payload)
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", path)
    assert _load_sim_window() == (None, None)


# ---------------------------------------------------------------------------
# _year_coverage_fraction / _period_note -- DERIVED, never hardcoded
# ---------------------------------------------------------------------------

def test_full_year_inside_the_window_is_one():
    assert _year_coverage_fraction(2018, date(2015, 11, 7), date(2025, 6, 7)) == 1.0


def test_partial_tail_year_is_the_real_day_count_not_a_flag():
    """The fraction is COMPUTED from two dates: the arithmetic is asserted from
    the same two dates the function was handed, so this cannot pass by pinning."""
    period_to = date(2025, 6, 7)
    frac = _year_coverage_fraction(2025, date(2015, 11, 7), period_to)
    expected_days = (period_to - date(2025, 1, 1)).days + 1
    assert frac == round(expected_days / 365, 4)
    assert 0 < frac < 1


def test_year_entirely_outside_the_window_is_zero():
    assert _year_coverage_fraction(2030, date(2015, 11, 7), date(2025, 6, 7)) == 0.0


def test_unavailable_window_is_unknown_not_full():
    """The whole point: an unreadable window must NOT resolve to 1.0."""
    assert _year_coverage_fraction(2025, None, None) is None
    assert _year_coverage_fraction(2025, date(2020, 1, 1), None) is None


def test_period_note_is_none_for_a_whole_year():
    assert _period_note(2018, 1.0, date(2015, 11, 7), date(2025, 6, 7)) is None


def test_period_note_states_the_dates_months_and_share():
    note = _period_note(2025, 0.4329, date(2015, 11, 7), date(2025, 6, 7))
    assert "PART YEAR" in note
    assert "43%" in note
    assert "5.2 of 12 months" in note
    assert "not comparable" in note.lower()


def test_period_note_says_unknown_when_coverage_is_unknown():
    note = _period_note(2025, None, None, None)
    assert "UNKNOWN" in note
    assert "NOT certified" in note


# ---------------------------------------------------------------------------
# extract_financial -- the period fields land on every published row
# ---------------------------------------------------------------------------

def test_annual_rows_carry_derived_period_coverage(windowed):
    rows = {r["year"]: r for r in extract_financial(_run_data())["annual"]}
    assert rows[2016]["period_coverage_fraction"] == 1.0
    assert rows[2016]["period_partial"] is False
    assert rows[2016]["period_note"] is None
    assert 0 < rows[2017]["period_coverage_fraction"] < 1
    assert rows[2017]["period_partial"] is True
    assert "PART YEAR" in rows[2017]["period_note"]


def test_segment_annual_rows_carry_period_coverage_too(windowed):
    data = _run_data()
    data["years"]["2017"]["segment_split"] = {
        "I&C Electricity": {"revenue_gbp": 1000.0, "gross_gbp": 200.0, "net_gbp": 100.0}}
    seg = {r["year"]: r for r in extract_financial(data)["segment_annual"]}
    assert seg[2016]["period_partial"] is False
    assert seg[2017]["period_partial"] is True
    # The segment taxonomy must be untouched by the two new scalar keys.
    from tools.generate_company_data import segment_revenue_mix
    mix = segment_revenue_mix(list(seg.values()))
    assert mix["available"] is True
    assert mix["revenue_by_segment"]["i&c"] == 1000.0


def test_window_and_its_source_are_published(windowed):
    financial = extract_financial(_run_data())
    assert financial["sim_window"] == "2016-01-01 to 2017-06-15"
    assert financial["sim_window_from"] == "2016-01-01"
    assert financial["sim_window_to"] == "2017-06-15"
    assert "sim_data.json" in financial["period_coverage_source"]


def test_unknown_window_is_disclosed_never_silently_full(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_dashboard_data, "SIM_DATA_PATH", tmp_path / "absent.json")
    financial = extract_financial(_run_data())
    assert financial["sim_window"] is None
    assert financial["period_coverage_source"] == "unavailable"
    for row in financial["annual"]:
        assert row["period_coverage_fraction"] is None
        assert row["period_partial"] is False       # unknown != asserted-partial
        assert "UNKNOWN" in row["period_note"]      # ...but it is DISCLOSED
    # And the gate accepts disclosed-unknown while still rejecting silence.
    assert _check_period_coverage_present(financial) is True


# ---------------------------------------------------------------------------
# extract_financial -- MAJOR-4, one bad-debt series
# ---------------------------------------------------------------------------

def test_bad_debt_reconciliation_bridges_both_bases(windowed):
    recon = extract_financial(_run_data())["bad_debt_reconciliation"]
    assert recon["annual_series_total_gbp"] == 5.0          # 10.0 + (-5.0)
    assert recon["ledger_total_gbp"] == 7_200.0
    assert recon["ratio_x"] == round(7_200.0 / 5.0, 2)
    assert recon["authoritative"] == "ledger"


def test_both_bad_debt_sides_carry_their_clock_r14(windowed):
    recon = extract_financial(_run_data())["bad_debt_reconciliation"]
    assert recon["annual_series_clock"] == "settled"
    assert recon["ledger_clock"] == "billed"
    assert recon["annual_series_rate_pct"] == round(100 * 5.0 / 300_000.0, 3)
    assert recon["ledger_rate_pct"] == round(100 * 7_200.0 / 300_000.0, 3)


def test_negative_year_forces_a_hard_red_with_a_named_cause(windowed):
    """The original defect graded a '-0.0%' bad-debt rate AMBER -- a sign error
    treated as a calibration nudge. A non-positive rate is a HARD RED and must
    name its mechanism."""
    recon = extract_financial(_run_data())["bad_debt_reconciliation"]
    assert recon["annual_series_negative_years"] == [2017]
    assert recon["annual_series_rag"] == "RED"
    assert "NEGATIVE" in recon["annual_series_rag_cause"]
    assert "crisis_bad_debt_validator" in recon["annual_series_rag_cause"]


def test_in_band_positive_series_is_allowed_to_read_green():
    """The RED is not hardcoded: a series that is genuinely in band grades
    GREEN, which is what makes the RED above evidence rather than decoration."""
    recon = _build_bad_debt_reconciliation(
        [{"year": 2016, "bad_debt_gbp": 2_000.0},
         {"year": 2017, "bad_debt_gbp": 2_000.0}],
        ledger_bad_debt_gbp=4_000.0, ledger_revenue_gbp=200_000.0,
    )
    assert recon["annual_series_rag"] == "GREEN"
    assert recon["annual_series_rag_cause"] is None
    assert recon["annual_series_negative_years"] == []


def test_zero_annual_total_yields_no_ratio_never_a_zero_division():
    recon = _build_bad_debt_reconciliation(
        [{"year": 2016, "bad_debt_gbp": 0.0}],
        ledger_bad_debt_gbp=1_000.0, ledger_revenue_gbp=100_000.0,
    )
    assert recon["ratio_x"] is None
    assert recon["annual_series_rag"] == "RED"


def test_unavailable_revenue_denominator_is_red_not_silent():
    recon = _build_bad_debt_reconciliation(
        [{"year": 2016, "bad_debt_gbp": 100.0}],
        ledger_bad_debt_gbp=1_000.0, ledger_revenue_gbp=0.0,
    )
    assert recon["annual_series_rate_pct"] is None
    assert recon["annual_series_rag"] == "RED"
    assert "FAILED check" in recon["annual_series_rag_cause"]


def test_ledger_side_of_the_bridge_matches_the_published_ledger_block(windowed):
    financial = extract_financial(_run_data())
    assert financial["ledger"]["bad_debt_gbp"] == \
        financial["bad_debt_reconciliation"]["ledger_total_gbp"]


# ---------------------------------------------------------------------------
# _check_bad_debt_reconciliation_present -- R15 mutation battery
# ---------------------------------------------------------------------------

def _good_financial(windowed_tmp=None):
    return extract_financial(_run_data())


def test_bad_debt_gate_passes_on_a_correct_block(windowed):
    assert _check_bad_debt_reconciliation_present(extract_financial(_run_data())) is True


def test_bad_debt_gate_fails_when_the_whole_block_is_gone(windowed, capsys):
    financial = extract_financial(_run_data())
    del financial["bad_debt_reconciliation"]
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "missing" in capsys.readouterr().err


@pytest.mark.parametrize("field", [
    "annual_series_basis", "annual_series_clock", "ledger_basis", "ledger_clock",
    "authoritative", "note", "band_source", "evidence",
])
def test_bad_debt_gate_fails_on_any_emptied_required_field(windowed, capsys, field):
    financial = extract_financial(_run_data())
    financial["bad_debt_reconciliation"][field] = ""
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert field in capsys.readouterr().err


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), None, "1.0", True])
def test_bad_debt_gate_rejects_non_finite_totals(windowed, capsys, bad):
    """NaN-blind comparison guards are their own R15 pattern: reject non-finite
    FIRST, before any arithmetic."""
    financial = extract_financial(_run_data())
    financial["bad_debt_reconciliation"]["annual_series_total_gbp"] = bad
    assert _check_bad_debt_reconciliation_present(financial) is False
    err = capsys.readouterr().err
    assert "not a finite number" in err or "missing" in err


def test_bad_debt_gate_fails_when_the_stored_total_drifts_from_a_resum(windowed, capsys):
    """ANTI-TAUTOLOGY: corrupt ONLY the stored aggregate, leaving the raw rows
    intact. A gate that trusted the aggregate back at itself would pass."""
    financial = extract_financial(_run_data())
    financial["bad_debt_reconciliation"]["annual_series_total_gbp"] = 999_999.0
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "independent re-sum" in capsys.readouterr().err


def test_bad_debt_gate_fails_when_a_raw_row_drifts_from_the_stored_total(windowed, capsys):
    """The same independence, mutated from the other side: move a ROW and leave
    the aggregate alone."""
    financial = extract_financial(_run_data())
    financial["annual"][0]["bad_debt_gbp"] = 50_000.0
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "independent re-sum" in capsys.readouterr().err


def test_bad_debt_gate_fails_when_the_two_published_ledger_figures_diverge(windowed, capsys):
    """ANTI-TAUTOLOGY, second axis: the bridge's ledger side is cross-checked
    against the separately-stored financial.ledger.bad_debt_gbp -- the very
    drift MAJOR-4 is about."""
    financial = extract_financial(_run_data())
    financial["ledger"]["bad_debt_gbp"] = 1.0
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "drifted apart" in capsys.readouterr().err


def test_bad_debt_gate_fails_on_empty_or_missing_annual_rows(windowed, capsys):
    financial = extract_financial(_run_data())
    financial["annual"] = []
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "missing or empty" in capsys.readouterr().err


def test_bad_debt_gate_fails_on_a_non_finite_row(windowed, capsys):
    financial = extract_financial(_run_data())
    financial["annual"][0]["bad_debt_gbp"] = float("nan")
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "non-finite" in capsys.readouterr().err


def test_bad_debt_gate_fails_if_authority_is_switched_off_the_ledger(windowed, capsys):
    financial = extract_financial(_run_data())
    financial["bad_debt_reconciliation"]["authoritative"] = "annual"
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "authoritative" in capsys.readouterr().err.lower()


def test_bad_debt_gate_fails_if_a_negative_series_is_downgraded_to_amber(windowed, capsys):
    """THE ORIGINAL DEFECT, as a mutation: a negative bad-debt series graded
    AMBER must fail the gate."""
    financial = extract_financial(_run_data())
    financial["bad_debt_reconciliation"]["annual_series_rag"] = "AMBER"
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "HARD RED" in capsys.readouterr().err


def test_bad_debt_gate_fails_on_a_red_with_no_named_cause(windowed, capsys):
    financial = extract_financial(_run_data())
    financial["bad_debt_reconciliation"]["annual_series_rag_cause"] = None
    assert _check_bad_debt_reconciliation_present(financial) is False
    assert "colour, not a diagnosis" in capsys.readouterr().err


@pytest.mark.parametrize("nonsense", [None, [], "financial", 7])
def test_bad_debt_gate_treats_an_unavailable_block_as_failed(capsys, nonsense):
    assert _check_bad_debt_reconciliation_present(nonsense) is False
    assert "FAILED check" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _check_period_coverage_present -- R15 mutation battery
# ---------------------------------------------------------------------------

def test_period_gate_passes_on_a_correct_block(windowed):
    assert _check_period_coverage_present(extract_financial(_run_data())) is True


@pytest.mark.parametrize("nonsense", [None, [], "financial", 7])
def test_period_gate_treats_an_unavailable_block_as_failed(capsys, nonsense):
    assert _check_period_coverage_present(nonsense) is False
    assert "FAILED check" in capsys.readouterr().err


def test_period_gate_fails_on_no_annual_rows(capsys):
    """FAIL-OPEN closed: 'no rows' must not mean 'no problem'. A published
    financial block with an empty annual series is itself broken."""
    assert _check_period_coverage_present(
        {"annual": [], "period_coverage_source": "x"}) is False
    assert "missing or empty" in capsys.readouterr().err


def test_period_gate_fails_when_the_coverage_source_is_undeclared(capsys):
    rows = [{"year": 2020, "period_coverage_fraction": 1.0, "period_partial": False}]
    assert _check_period_coverage_present({"annual": rows}) is False
    assert "period_coverage_source" in capsys.readouterr().err


def test_period_gate_fails_when_a_row_has_no_period_fields(capsys):
    assert _check_period_coverage_present(
        {"annual": [{"year": 2020}], "period_coverage_source": "x"}) is False
    assert "period_coverage_fraction" in capsys.readouterr().err


def test_period_gate_fails_when_period_partial_is_not_a_bool(capsys):
    rows = [{"year": 2020, "period_coverage_fraction": 1.0, "period_partial": "no"}]
    assert _check_period_coverage_present(
        {"annual": rows, "period_coverage_source": "x"}) is False
    assert "boolean period_partial" in capsys.readouterr().err


@pytest.mark.parametrize("frac", [float("nan"), float("inf"), True, "1.0"])
def test_period_gate_rejects_a_non_finite_fraction(capsys, frac):
    rows = [{"year": 2020, "period_coverage_fraction": frac, "period_partial": False}]
    assert _check_period_coverage_present(
        {"annual": rows, "period_coverage_source": "x"}) is False
    assert "not a finite number" in capsys.readouterr().err


@pytest.mark.parametrize("frac", [-0.01, 1.5])
def test_period_gate_rejects_an_out_of_range_fraction(capsys, frac):
    rows = [{"year": 2020, "period_coverage_fraction": frac, "period_partial": True}]
    assert _check_period_coverage_present(
        {"annual": rows, "period_coverage_source": "x"}) is False
    assert "out of [0,1] range" in capsys.readouterr().err


def test_period_gate_fails_when_the_flag_contradicts_its_own_fraction(capsys):
    """ANTI-TAUTOLOGY: two INDEPENDENTLY-STORED fields, cross-checked. A future
    edit that updates one without the other fails here, in both directions."""
    understated = [{"year": 2025, "period_coverage_fraction": 0.5, "period_partial": False}]
    assert _check_period_coverage_present(
        {"annual": understated, "period_coverage_source": "x"}) is False
    assert "disagrees" in capsys.readouterr().err
    overstated = [{"year": 2016, "period_coverage_fraction": 1.0, "period_partial": True}]
    assert _check_period_coverage_present(
        {"annual": overstated, "period_coverage_source": "x"}) is False


def test_period_gate_fails_when_a_part_year_carries_no_note(capsys):
    rows = [{"year": 2025, "period_coverage_fraction": 0.4,
             "period_partial": True, "period_note": None}]
    assert _check_period_coverage_present(
        {"annual": rows, "period_coverage_source": "x"}) is False
    assert "no period_note" in capsys.readouterr().err


def test_period_gate_fails_when_an_unknown_masquerades_as_a_measured_partial(capsys):
    rows = [{"year": 2025, "period_coverage_fraction": None,
             "period_partial": True, "period_note": "whatever"}]
    assert _check_period_coverage_present(
        {"annual": rows, "period_coverage_source": "x"}) is False
    assert "masquerade" in capsys.readouterr().err


def test_period_gate_fails_when_an_unknown_is_not_disclosed(capsys):
    rows = [{"year": 2025, "period_coverage_fraction": None,
             "period_partial": False, "period_note": None}]
    assert _check_period_coverage_present(
        {"annual": rows, "period_coverage_source": "unavailable"}) is False
    assert "no period_note" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# MAJOR-5 -- the margin plausibility ANCHOR (R12: a flag, never a target)
# ---------------------------------------------------------------------------

def _dashboard_with_margin(rows, segment_annual=None):
    return {"financial": {"annual": rows,
                          "segment_annual": segment_annual or [],
                          "sim_window": "w"}}


# A book whose revenue is overwhelmingly non-domestic, so the register's
# population gate finds the benchmark and the measured figure MATCHED and lets
# the grade publish. Built here rather than read from live data so the grade
# under test cannot move with a run.
_NON_DOMESTIC_BOOK = [{"year": 2018,
                       "i&c_electricity": {"revenue_gbp": 99_000.0, "gross_gbp": 1.0,
                                           "net_gbp": 1.0, "net_margin_pct": 1.0},
                       "resi_electricity": {"revenue_gbp": 1_000.0, "gross_gbp": 1.0,
                                            "net_gbp": 1.0, "net_margin_pct": 1.0}}]


def _row(year, net, revenue, margin_pct, partial=False):
    return {"year": year, "net_gbp": net, "total_revenue_gbp": revenue,
            "net_margin_pct": margin_pct, "period_partial": partial}


def test_the_band_is_the_externally_published_non_domestic_range():
    """R13/R12: the band is a registered external figure, chosen once. If anyone
    ever 'adjusts' it to accommodate an outcome, this fails."""
    assert (_MARGIN_BAND_LOW_PCT, _MARGIN_BAND_HIGH_PCT) == (1.7, 4.5)


def test_an_in_band_book_reads_green():
    anchor = _margin_plausibility_anchor(
        _dashboard_with_margin([_row(2020, 3_000.0, 100_000.0, 3.0)]))
    assert anchor["rag"] == "GREEN"
    assert anchor["verdict"] == "IN BAND"


def test_a_far_above_band_book_reads_red_and_is_allowed_to():
    """The anchor exists to LET an implausible figure read RED. A flagged
    implausible figure is credible; an unflagged one is not."""
    anchor = _margin_plausibility_anchor(
        _dashboard_with_margin([_row(2018, 17_000.0, 100_000.0, 17.0)]))
    assert anchor["rag"] == "RED"
    assert anchor["verdict"] == "FAR ABOVE"


def test_a_loss_making_book_also_reads_red():
    anchor = _margin_plausibility_anchor(
        _dashboard_with_margin([_row(2021, -6_000.0, 100_000.0, -6.0)]))
    assert anchor["rag"] == "RED"
    assert anchor["verdict"] == "BELOW"


def test_the_worst_published_full_year_sets_the_grade_not_the_average():
    """The doors publish PER-YEAR margins. An average that hides a 17% year is
    not the figure a reader sees, so it may not be the figure that is graded."""
    rows = [_row(2018, 17_000.0, 100_000.0, 17.0),
            _row(2019, 3_000.0, 900_000.0, 0.33)]
    anchor = _margin_plausibility_anchor(_dashboard_with_margin(rows))
    assert anchor["margin_pct"] == 2.0            # the flattering aggregate...
    assert anchor["worst_full_year"] == 2018      # ...but the grade follows 2018
    assert anchor["rag"] == "RED"
    assert "worst full year" in anchor["graded_on"]


def test_a_part_year_never_sets_the_grade():
    """MAJOR-6 coupling: a part-year margin is not comparable to a full-year
    benchmark, so it is excluded from the per-year reading -- which is exactly
    why the period flag has to exist before this anchor can be honest."""
    rows = [_row(2024, 3_000.0, 100_000.0, 3.0),
            _row(2025, 40_000.0, 100_000.0, 40.0, partial=True)]
    anchor = _margin_plausibility_anchor(_dashboard_with_margin(rows))
    assert anchor["worst_full_year"] == 2024
    assert anchor["partial_years"] == [2025]


@pytest.mark.parametrize("dashboard, reason_fragment", [
    ({}, "unavailable"),
    ({"financial": None}, "unavailable"),
    ({"financial": {"annual": []}}, "missing or empty"),
    ({"financial": {"annual": [{"year": 2020}]}}, "no annual row"),
    ({"financial": {"annual": [_row(2020, 1.0, 0.0, 1.0)]}}, "no annual row"),
    ({"financial": {"annual": [_row(2020, float("nan"), 100.0, 1.0)]}}, "no annual row"),
])
def test_margin_anchor_fails_closed_and_says_why(dashboard, reason_fragment):
    """FAIL-OPEN/FAIL-SILENT closed: an unmeasurable anchor never fabricates a
    0% margin and never quietly disappears."""
    anchor = _margin_plausibility_anchor(dashboard)
    assert anchor["available"] is False
    assert reason_fragment in anchor["reason"]


def test_an_unmeasurable_margin_still_publishes_a_visible_not_measured_card():
    """A missing row is indistinguishable from a passing one, so the row is
    emitted either way -- with no grade and a stated reason."""
    card = _margin_anchor_card({"financial": None})
    assert card["sim_value"] is None
    assert card["rag"] is None
    assert "NOT MEASURED" in card["note"]
    assert "FAILED anchor" in card["note"]


def test_the_margin_card_carries_its_band_source_and_its_r12_warning():
    card = _margin_anchor_card(_dashboard_with_margin(
        [_row(2018, 17_000.0, 100_000.0, 17.0)], _NON_DOMESTIC_BOOK))
    assert card["rag"] == "RED"
    assert card["population_status"] == "MATCHED"
    assert "Consolidated Segmental Statements" in card["note"]
    assert "never a target" in card["note"]
    assert "ASSUMPTIONS.md" in card["note"]


def test_the_margin_grade_is_withheld_when_the_benchmark_cannot_grade_the_book():
    """The margin row is subject to the SAME population gate as every other
    anchor: a non-domestic benchmark may not grade a book whose composition is
    unknown. The measured RAG survives in rag_measured (R12 -- a diagnostic is
    never destroyed to make a page look better)."""
    card = _margin_anchor_card(_dashboard_with_margin(
        [_row(2018, 17_000.0, 100_000.0, 17.0)]))          # no segment mix
    assert card["gradeable"] is False
    assert card["rag"] is None
    assert card["rag_measured"] == "RED"


def test_the_margin_row_declares_the_population_it_is_graded_against():
    """A benchmark may not grade a population it does not measure. The margin
    row joins the register's population gate like every other row."""
    assert "net_margin" in generate_world_data._ANCHOR_POPULATIONS
    decl = generate_world_data._ANCHOR_POPULATIONS["net_margin"]
    assert decl["benchmark_class"] == generate_world_data._POP_NON_DOMESTIC
    assert decl["measured_scope"] == "whole_book"


def test_the_register_always_contains_a_margin_row():
    """MAJOR-5 in one assertion: margin can never again be the metric with no
    band. The row is appended unconditionally, so it cannot vanish silently."""
    register = generate_world_data._anchors_runtime(
        {"overall_rag": "RED"},
        _dashboard_with_margin([_row(2018, 17_000.0, 100_000.0, 17.0)]),
    )
    keys = [c["metric_key"] for c in register["cards"]]
    assert keys.count("net_margin") == 1


# ---------------------------------------------------------------------------
# R11 -- the LIVE published artefacts, asserted as RELATIONSHIPS only
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DASHBOARD_PATH.exists(), reason="dashboard.json not generated")
def test_live_dashboard_passes_both_gates():
    financial = json.loads(DASHBOARD_PATH.read_text())["financial"]
    assert _check_bad_debt_reconciliation_present(financial) is True
    assert _check_period_coverage_present(financial) is True


@pytest.mark.skipif(not DASHBOARD_PATH.exists(), reason="dashboard.json not generated")
def test_live_partial_years_are_re_derivable_from_the_published_window():
    """NEVER PIN A GENERATED VALUE. This asserts the RELATIONSHIP -- the set of
    rows flagged partial is exactly the set the published window implies -- so a
    legitimately-changed sim window moves both sides together and stays green.
    A hardcoded 'this year is partial' would fail here the moment the window
    moved, which is precisely the defect being closed."""
    financial = json.loads(DASHBOARD_PATH.read_text())["financial"]
    window_from, window_to = financial["sim_window_from"], financial["sim_window_to"]
    assert window_from and window_to, "the published window is the whole basis"
    d_from = date.fromisoformat(window_from)
    d_to = date.fromisoformat(window_to)
    flagged = {r["year"] for r in financial["annual"] if r["period_partial"]}
    rederived = {
        r["year"] for r in financial["annual"]
        if (_year_coverage_fraction(r["year"], d_from, d_to) or 0.0)
        < generate_dashboard_data._PERIOD_PARTIAL_THRESHOLD
    }
    assert flagged == rederived
    for row in financial["annual"]:
        assert (row["period_note"] is not None) == row["period_partial"]


@pytest.mark.skipif(not DASHBOARD_PATH.exists(), reason="dashboard.json not generated")
def test_live_bad_debt_bridge_reconciles_to_its_own_sources():
    """RELATIONSHIP, not a pinned 129.6x: whatever the run produces, the two
    published sides must each equal what they claim to summarise, and the ratio
    must be their honest quotient."""
    financial = json.loads(DASHBOARD_PATH.read_text())["financial"]
    recon = financial["bad_debt_reconciliation"]
    resum = round(sum(r["bad_debt_gbp"] for r in financial["annual"]), 2)
    assert math.isclose(recon["annual_series_total_gbp"], resum, abs_tol=1.0)
    assert math.isclose(recon["ledger_total_gbp"], financial["ledger"]["bad_debt_gbp"],
                        abs_tol=1.0)
    if recon["annual_series_total_gbp"]:
        assert math.isclose(
            recon["ratio_x"],
            round(recon["ledger_total_gbp"] / recon["annual_series_total_gbp"], 2),
            rel_tol=1e-6)
    assert recon["annual_series_clock"] and recon["ledger_clock"]   # R14


@pytest.mark.skipif(not WORLD_PATH.exists(), reason="world.json not generated")
def test_live_world_register_carries_the_margin_row_with_its_band():
    cards = json.loads(WORLD_PATH.read_text())["anchors"]["runtime"]["cards"]
    margin = [c for c in cards if c["metric_key"] == "net_margin"]
    assert len(margin) == 1, "margin must always have a band (MAJOR-5)"
    card = margin[0]
    assert str(_MARGIN_BAND_LOW_PCT) in card["benchmark_value"]
    assert str(_MARGIN_BAND_HIGH_PCT) in card["benchmark_value"]
    assert "never a target" in card["note"]


@pytest.mark.skipif(not WORLD_PATH.exists() or not DASHBOARD_PATH.exists(),
                    reason="artefacts not generated")
def test_live_margin_card_agrees_with_a_recomputation_from_the_dashboard():
    """INDEPENDENCE: world.json's published card is checked against a fresh
    computation from dashboard.json -- two separately-generated files."""
    dashboard = json.loads(DASHBOARD_PATH.read_text())
    card = [c for c in json.loads(WORLD_PATH.read_text())["anchors"]["runtime"]["cards"]
            if c["metric_key"] == "net_margin"][0]
    recomputed = _margin_plausibility_anchor(dashboard)
    assert recomputed["available"] is True
    assert card["sim_value"] == "{}%".format(recomputed["margin_pct"])


# ---------------------------------------------------------------------------
# R11 -- the RENDERED pixel on the Company door
# ---------------------------------------------------------------------------

COMPANY_DIR = PROJECT / "site" / "company"
HARNESS = COMPANY_DIR / "_render_harness.mjs"
COMPANY_JSON = PROJECT / "site" / "data" / "company.json"


def _node():
    import shutil
    return shutil.which("node")


def _render(payload):
    proc = subprocess.run(
        [_node(), str(HARNESS), str(COMPANY_DIR / "index.html")],
        input=json.dumps(payload), capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


_needs_render = pytest.mark.skipif(
    _node() is None or not COMPANY_JSON.exists() or not DASHBOARD_PATH.exists(),
    reason="node or the published artefacts are unavailable",
)


@_needs_render
def test_rendered_company_door_states_the_period_and_the_bridge():
    out = _render({"company": json.loads(COMPANY_JSON.read_text())})
    panel = out["period-coverage"]["innerHTML"]
    dashboard = json.loads(DASHBOARD_PATH.read_text())["financial"]
    assert dashboard["sim_window"] in panel          # the window, as published
    assert "Bad debt &mdash; one series, bridged." in panel
    assert str(dashboard["bad_debt_reconciliation"]["ratio_x"]) in panel
    if any(r["period_partial"] for r in dashboard["annual"]):
        assert "PART YEAR" in panel


@_needs_render
def test_rendered_year_labelled_kpi_carries_its_period_not_just_its_clock():
    """The named MAJOR-6 defect at the rendered value: '/company/ shows a
    full-year Corp. tax on 5.2 months of trading'."""
    company = json.loads(COMPANY_JSON.read_text())
    out = _render({"company": company})
    kpis = out["finance-kpis"]["innerHTML"]
    latest_year = company["finance"]["latest_year"]
    dashboard = json.loads(DASHBOARD_PATH.read_text())["financial"]
    row = [r for r in dashboard["annual"] if r["year"] == latest_year]
    assert "Corp. tax {}".format(latest_year) in kpis
    if row and row[0]["period_partial"]:
        assert "PART YEAR" in kpis
    elif row:
        assert "full year {}".format(latest_year) in kpis


@_needs_render
def test_rendered_period_label_follows_the_data_r15_independence():
    """MUTATION: flip the SOURCE row's period flags and prove the rendered pixel
    moves. A label that stayed put would be decoration, not a rendering."""
    company = json.loads(COMPANY_JSON.read_text())
    dashboard = json.loads(DASHBOARD_PATH.read_text())
    latest_year = company["finance"]["latest_year"]
    for row in dashboard["financial"]["annual"]:
        row["period_partial"] = (row["year"] == latest_year)
        row["period_coverage_fraction"] = 0.25 if row["year"] == latest_year else 1.0
        row["period_note"] = "PART YEAR -- injected" if row["year"] == latest_year else None
    mutated = _render({"company": company, "dashboard": dashboard})
    assert "PART YEAR (25% of {})".format(latest_year) in mutated["finance-kpis"]["innerHTML"]

    for row in dashboard["financial"]["annual"]:
        row["period_partial"] = False
        row["period_coverage_fraction"] = 1.0
        row["period_note"] = None
    whole = _render({"company": company, "dashboard": dashboard})
    assert "full year {}".format(latest_year) in whole["finance-kpis"]["innerHTML"]
    assert "PART YEAR" not in whole["finance-kpis"]["innerHTML"]
    assert "whole calendar year" in whole["period-coverage"]["innerHTML"]


@_needs_render
def test_rendered_door_fails_closed_when_the_dashboard_is_unavailable():
    """FAIL-SILENT closed at the pixel: with no dashboard, no figure may be
    rendered as though its period were known."""
    company = json.loads(COMPANY_JSON.read_text())
    out = _render({"company": company, "dashboard": None})
    assert "Period coverage unknown" in out["period-coverage"]["innerHTML"]
    assert "failed check" in out["period-coverage"]["innerHTML"].lower()
    assert "period coverage unknown" in out["finance-kpis"]["innerHTML"].lower()
