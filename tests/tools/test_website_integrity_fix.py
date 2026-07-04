"""Tests for website-integrity fix (Phase QC): build-info dynamic label +
cross-surface consistency gate, closing the exec-summary/totals contradiction
staged in docs/staging/WEBSITE_INTEGRITY_AND_DESIGN.md Part A."""
import json
import inspect

from tools.generate_dashboard_data import _load_build_info, _check_consistency, BUILD_INFO_PATH


def test_load_build_info_reads_file(tmp_path, monkeypatch):
    p = tmp_path / "build_info.json"
    p.write_text(json.dumps({"phase": "ZZ", "test_count": 99999, "company_modules": 111}))
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", p)
    phase, count, modules = _load_build_info()
    assert phase == "ZZ"
    assert count == 99999
    assert modules == 111


def test_load_build_info_falls_back_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", tmp_path / "nonexistent.json")
    phase, count, modules = _load_build_info()
    assert phase == "OL"
    assert count == 15148
    assert modules == 405


def test_load_build_info_falls_back_on_invalid_json(tmp_path, monkeypatch):
    p = tmp_path / "build_info.json"
    p.write_text("not valid json {{{{")
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", p)
    phase, count, modules = _load_build_info()
    assert phase == "OL"


def test_load_build_info_partial_file_uses_defaults_for_missing_keys(tmp_path, monkeypatch):
    p = tmp_path / "build_info.json"
    p.write_text(json.dumps({"phase": "QC"}))
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", p)
    phase, count, modules = _load_build_info()
    assert phase == "QC"
    assert count == 15148


def test_check_consistency_passes_when_net_margins_match(capsys):
    portfolio = {"net_margin_gbp": 1445258.0}
    insights = {"net_margin_gbp": 1445258.0}
    assert _check_consistency(portfolio, insights, "run_output_test.json") is True
    assert "CONSISTENCY GATE FAILED" not in capsys.readouterr().err


def test_check_consistency_fails_loudly_on_mismatch(capsys):
    portfolio = {"net_margin_gbp": 1445258.0}
    insights = {"net_margin_gbp": -8317.0}
    assert _check_consistency(portfolio, insights, "run_output_test.json") is False
    err = capsys.readouterr().err
    assert "CONSISTENCY GATE FAILED" in err
    assert "run_output_test.json" in err


def test_check_consistency_within_tolerance_passes():
    portfolio = {"net_margin_gbp": 1445258.4}
    insights = {"net_margin_gbp": 1445258.9}
    assert _check_consistency(portfolio, insights, "x.json", tolerance_gbp=1.0) is True


def test_check_consistency_skips_when_insights_absent(capsys):
    portfolio = {"net_margin_gbp": 1445258.0}
    assert _check_consistency(portfolio, None, "x.json") is True


def test_check_consistency_skips_when_fields_missing():
    assert _check_consistency({}, {}, "x.json") is True


def test_process_run_complete_generates_insights_before_dashboard():
    """Regression test for the step-ordering bug: run-insights generation
    must happen before dashboard/site generation so the exec summary on
    site/shadow/index.html reflects THIS run, not the previous one."""
    import background.process_run_complete as prc
    source = inspect.getsource(prc.main)
    insights_pos = source.index("generate_insights(data, git_hash)")
    dashboard_pos = source.index("generate_dashboard_json(json_path)")
    assert insights_pos < dashboard_pos
