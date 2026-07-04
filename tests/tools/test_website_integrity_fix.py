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


# --- Phase QF: Part C -- widened consistency gate + loud-failure NTFY wiring ---

def _insights_with_areas(**area_metrics):
    """Build a run_insights.json-shaped dict from {area: {key: val}} kwargs."""
    blocks = []
    for area, metrics in area_metrics.items():
        blocks.append({"area": area, "key_metrics": metrics})
    return {"insights": blocks}


def test_check_consistency_catches_bills_mismatch(capsys):
    portfolio = {"net_margin_gbp": 100.0, "bills_total": 1605}
    extra = _insights_with_areas(operations={"bills_total": 1117})
    insights = dict(extra, net_margin_gbp=100.0)
    assert _check_consistency(portfolio, insights, "x.json") is False
    err = capsys.readouterr().err
    assert "CONSISTENCY GATE FAILED" in err
    assert "bills total" in err


def test_check_consistency_catches_committee_interventions_mismatch(capsys):
    portfolio = {"net_margin_gbp": 100.0, "committee_interventions_total": 38}
    extra = _insights_with_areas(risk={"committee_interventions_total": 323})
    insights = dict(extra, net_margin_gbp=100.0)
    assert _check_consistency(portfolio, insights, "x.json") is False
    assert "committee interventions" in capsys.readouterr().err


def test_check_consistency_catches_enterprise_value_and_retention_mismatches(capsys):
    portfolio = {
        "net_margin_gbp": 100.0,
        "enterprise_value_gbp": 8826938.57,
        "retention_offers": 14,
        "retention_retained": 14,
        "churn_count": 6,
    }
    extra = _insights_with_areas(customers={
        "enterprise_value_gbp": 0.0,
        "retention_offers": 0,
        "retained": 0,
        "total_churned": 0,
    })
    insights = dict(extra, net_margin_gbp=100.0)
    assert _check_consistency(portfolio, insights, "x.json") is False
    err = capsys.readouterr().err
    assert "enterprise value" in err
    assert "retention offers" in err
    assert "retention retained" in err
    assert "churn count" in err


def test_check_consistency_passes_when_all_headline_numbers_agree():
    portfolio = {
        "net_margin_gbp": 1445258.0,
        "gross_margin_gbp": 6467308.57,
        "enterprise_value_gbp": 8826938.57,
        "bills_total": 1605,
        "committee_interventions_total": 38,
        "retention_offers": 14,
        "retention_retained": 14,
        "churn_count": 6,
    }
    extra = _insights_with_areas(
        financial={"gross_margin_gbp": 6467308.57},
        customers={
            "enterprise_value_gbp": 8826938.57,
            "retention_offers": 14,
            "retained": 14,
            "total_churned": 6,
        },
        operations={"bills_total": 1605},
        risk={"committee_interventions_total": 38},
    )
    insights = dict(extra, net_margin_gbp=1445258.0)
    assert _check_consistency(portfolio, insights, "x.json") is True


def test_check_consistency_gate_result_propagates_from_generate(tmp_path, monkeypatch):
    """generate() must return the consistency-gate result (Part C), not an
    unconditional True -- the caller relies on this to decide whether to NTFY."""
    import tools.generate_dashboard_data as gdd

    run_json = tmp_path / "run_output_test.json"
    run_json.write_text(json.dumps({
        "total_net_gbp": 100.0,
        "_cache_meta": {"git_commit": "deadbeef"},
    }))
    insights_path = tmp_path / "run_insights.json"
    insights_path.write_text(json.dumps({"net_margin_gbp": -999999.0}))
    out_path = tmp_path / "dashboard.json"

    monkeypatch.setattr(gdd, "RUN_INSIGHTS_PATH", insights_path)
    monkeypatch.setattr(gdd, "OUTPUT_PATH", out_path)
    monkeypatch.setattr(gdd, "load_spot_monthly", lambda: {})

    ok = gdd.generate(run_json)
    assert ok is False
    assert out_path.exists()


def test_generate_dashboard_json_returns_gate_status(tmp_path, monkeypatch):
    import background.process_run_complete as prc

    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")  # isolate from real sim-runner-log.md
    monkeypatch.setattr(
        "tools.generate_dashboard_data.generate",
        lambda json_path: False,
    )
    result = prc.generate_dashboard_json(tmp_path / "run.json")
    assert result is False


def test_main_ntfys_immediately_on_consistency_gate_failure():
    """Part C acceptance: a consistency-gate failure must NTFY Rich immediately,
    not just log to a file nobody is watching in real time."""
    import background.process_run_complete as prc

    source = inspect.getsource(prc.main)
    gate_pos = source.index("consistency_ok = generate_dashboard_json(json_path)")
    ntfy_pos = source.index("send_ntfy(", gate_pos)
    assert gate_pos < ntfy_pos
