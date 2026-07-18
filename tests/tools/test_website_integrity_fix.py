"""Tests for website-integrity fix (Phase QC): build-info dynamic label +
cross-surface consistency gate, closing the exec-summary/totals contradiction
staged in docs/staging/WEBSITE_INTEGRITY_AND_DESIGN.md Part A."""
import json
import inspect

from tools import generate_dashboard_data
from tools.generate_dashboard_data import (
    _load_build_info, _check_consistency, BUILD_INFO_PATH, count_company_modules,
    _derive_build_from_claude_md, _check_basis_labels_present, extract_portfolio,
    _check_bridge_reconciles,
)


def test_derive_build_from_claude_md_parses_current_state():
    """The stamp is derived live from CLAUDE.md's current-state section so it can
    never drift stale (WEBSITE_FRESHNESS_AND_DEDUP.md item 1).

    2026-07-10: phase is a best-effort label only (never displayed on the
    live site) and may legitimately be None if the newest Current-state
    entries are bare descriptive titles with no "Phase XY" tag -- test_count
    is the part that must always be present and correct."""
    phase, count = _derive_build_from_claude_md()
    assert phase is None or (phase.isalpha() and phase.isupper())
    assert isinstance(count, int) and count > 10000


def test_derive_build_from_claude_md_test_count_independent_of_phase_code(tmp_path, monkeypatch):
    """The exact regression this fix targets: a Current-state entry with no
    phase-letter code at all must still yield a real test_count, not fall
    through to (None, None)."""
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(
        "## Current state\n"
        "**A bare descriptive title, no phase code (2026-07-10):** "
        "did some real work. 12,345 tests collected, epistemic PASS.\n"
    )
    monkeypatch.setattr("tools.generate_dashboard_data.PROJECT", tmp_path)
    phase, count = _derive_build_from_claude_md()
    assert phase is None
    assert count == 12345


def test_derive_build_from_claude_md_finds_phase_code_when_present(tmp_path, monkeypatch):
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(
        "## Current state\n"
        "**Phase ZZ CLOSED (2026-07-10):** did some work. 5,000 tests collected.\n"
    )
    monkeypatch.setattr("tools.generate_dashboard_data.PROJECT", tmp_path)
    phase, count = _derive_build_from_claude_md()
    assert phase == "ZZ"
    assert count == 5000


def _no_claude_md(monkeypatch):
    """Neutralize the CLAUDE.md-derived stamp so the build_info.json FALLBACK path
    can be tested in isolation. Since WEBSITE_FRESHNESS_AND_DEDUP.md (2026-07-08),
    _derive_build_from_claude_md() is the PRIMARY source (never drifts) and
    build_info.json is only consulted when CLAUDE.md can't be parsed."""
    monkeypatch.setattr(
        "tools.generate_dashboard_data._derive_build_from_claude_md",
        lambda: (None, None),
    )


def test_load_build_info_prefers_claude_md(monkeypatch):
    # CLAUDE.md derivation wins over whatever build_info.json says.
    monkeypatch.setattr(
        "tools.generate_dashboard_data._derive_build_from_claude_md",
        lambda: ("ZZ", 42424),
    )
    phase, count, modules = _load_build_info()
    assert phase == "ZZ"
    assert count == 42424
    assert modules == count_company_modules()


def test_load_build_info_reads_file(tmp_path, monkeypatch):
    _no_claude_md(monkeypatch)
    p = tmp_path / "build_info.json"
    p.write_text(json.dumps({"phase": "ZZ", "test_count": 99999, "company_modules": 111}))
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", p)
    phase, count, modules = _load_build_info()
    assert phase == "ZZ"
    assert count == 99999
    # company_modules is always the live repo count now (Phase RO fix) --
    # build_info.json's own value is ignored to kill the RF-RN staleness drift.
    assert modules == count_company_modules()


def test_load_build_info_falls_back_when_missing(tmp_path, monkeypatch):
    _no_claude_md(monkeypatch)
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", tmp_path / "nonexistent.json")
    phase, count, modules = _load_build_info()
    assert phase == "OL"
    assert count == 15148
    assert modules == count_company_modules()


def test_load_build_info_falls_back_on_invalid_json(tmp_path, monkeypatch):
    _no_claude_md(monkeypatch)
    p = tmp_path / "build_info.json"
    p.write_text("not valid json {{{{")
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", p)
    phase, count, modules = _load_build_info()
    assert phase == "OL"


def test_count_company_modules_matches_independent_filesystem_scan():
    import pathlib
    project = pathlib.Path(__file__).resolve().parent.parent.parent
    company_dir = project / "company"
    expected = sum(
        1 for p in company_dir.rglob("*.py")
        if "__pycache__" not in p.parts and not p.name.startswith("test_")
    )
    assert count_company_modules() == expected
    assert expected > 0


def test_load_build_info_keeps_fresh_test_count_when_phase_code_missing(tmp_path, monkeypatch):
    """The exact regression this fix targets: CLAUDE.md yields a real,
    fresh test_count but no phase code -- must NOT discard that test_count
    in favour of a stale build_info.json figure."""
    monkeypatch.setattr(
        "tools.generate_dashboard_data._derive_build_from_claude_md",
        lambda: (None, 16447),
    )
    p = tmp_path / "build_info.json"
    p.write_text(json.dumps({"phase": "OLD", "test_count": 9999}))
    monkeypatch.setattr("tools.generate_dashboard_data.BUILD_INFO_PATH", p)
    phase, count, modules = _load_build_info()
    assert count == 16447
    assert phase == "OLD"


def test_load_build_info_partial_file_uses_defaults_for_missing_keys(tmp_path, monkeypatch):
    _no_claude_md(monkeypatch)
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


def test_check_consistency_fails_closed_when_insights_absent(capsys):
    # R15 (KL-8 fix): an absent/empty run_insights.json is NOT a benign skip --
    # the pipeline guarantees the file is written immediately before this gate,
    # so a missing comparison input is a real failure and must fail CLOSED
    # (raising the consistency alarm), not pass silently.
    portfolio = {"net_margin_gbp": 1445258.0}
    assert _check_consistency(portfolio, None, "x.json") is False
    assert "CONSISTENCY GATE FAILED" in capsys.readouterr().err
    assert _check_consistency(portfolio, {}, "x.json") is False


def test_check_consistency_skips_key_absent_on_both_surfaces():
    # A headline key absent on BOTH surfaces is legitimately not-published and is
    # still skipped (net margin agrees; all other keys absent both sides).
    assert _check_consistency({"net_margin_gbp": 100.0}, {"net_margin_gbp": 100.0}, "x.json") is True


def test_check_consistency_fires_on_one_sided_key(capsys):
    # R15 (KL-8 fix, fail-open closed): a headline key present on one surface but
    # missing on the other is a real disagreement, no longer a silent skip.
    assert _check_consistency({"net_margin_gbp": 100.0}, {"gross_margin_gbp": 5.0}, "x.json") is False
    assert "CONSISTENCY GATE FAILED" in capsys.readouterr().err


def test_check_basis_labels_present_passes_for_real_extract_portfolio():
    """CLOCK_TRUTH_AND_THE_BRIDGE.md (2026-07-12, P0) standing rule: 'No
    financial figure is published without its clock.' extract_portfolio's own
    output must satisfy the gate it's checked against."""
    portfolio = extract_portfolio({"total_net_gbp": 100.0, "enterprise_value_gbp": 200.0})
    assert _check_basis_labels_present(portfolio) is True


def test_check_basis_labels_present_fails_when_basis_missing_entirely(capsys):
    portfolio = {"net_margin_gbp": 100.0, "enterprise_value_gbp": 200.0}
    assert _check_basis_labels_present(portfolio) is False
    err = capsys.readouterr().err
    assert "BASIS-LABEL GATE FAILED" in err
    assert "net_margin_gbp" in err
    assert "enterprise_value_gbp" in err


def test_check_basis_labels_present_fails_when_note_missing(capsys):
    portfolio = {
        "net_margin_gbp": 100.0,
        "basis": {"net_margin_gbp": {"clock": "settled", "provisional": True}},
    }
    assert _check_basis_labels_present(portfolio) is False
    assert "net_margin_gbp" in capsys.readouterr().err


def test_check_bridge_reconciles_true_when_file_missing(tmp_path, monkeypatch):
    """D2_three_clocks (2026-07-12, ADVISOR_STEER_TWIN_READONLY.md): degrades
    gracefully rather than blocking every dashboard generation before this
    atom's own bridge output exists for the first time."""
    monkeypatch.setattr(generate_dashboard_data, "MARGIN_BRIDGE_PATH", tmp_path / "margin_bridge.json")
    assert _check_bridge_reconciles() is True


def test_check_bridge_reconciles_passes_within_tolerance(tmp_path, monkeypatch):
    bridge_path = tmp_path / "margin_bridge.json"
    bridge_path.write_text(json.dumps({"unexplained_remainder_gbp": 0.01}))
    monkeypatch.setattr(generate_dashboard_data, "MARGIN_BRIDGE_PATH", bridge_path)
    assert _check_bridge_reconciles() is True


def test_check_bridge_reconciles_fails_when_remainder_exceeds_tolerance(tmp_path, monkeypatch, capsys):
    bridge_path = tmp_path / "margin_bridge.json"
    bridge_path.write_text(json.dumps({"unexplained_remainder_gbp": 500.0}))
    monkeypatch.setattr(generate_dashboard_data, "MARGIN_BRIDGE_PATH", bridge_path)
    assert _check_bridge_reconciles() is False
    err = capsys.readouterr().err
    assert "BRIDGE-RECONCILE GATE FAILED" in err
    assert "500" in err


def test_check_bridge_reconciles_fails_when_remainder_missing(tmp_path, monkeypatch, capsys):
    bridge_path = tmp_path / "margin_bridge.json"
    bridge_path.write_text(json.dumps({"settlement_net_margin_gbp": 100.0}))
    monkeypatch.setattr(generate_dashboard_data, "MARGIN_BRIDGE_PATH", bridge_path)
    assert _check_bridge_reconciles() is False
    assert "unexplained_remainder_gbp missing" in capsys.readouterr().err


def test_check_bridge_reconciles_fails_closed_on_malformed_json(tmp_path, monkeypatch, capsys):
    bridge_path = tmp_path / "margin_bridge.json"
    bridge_path.write_text("not valid json{{{")
    monkeypatch.setattr(generate_dashboard_data, "MARGIN_BRIDGE_PATH", bridge_path)
    assert _check_bridge_reconciles() is False
    assert "unreadable" in capsys.readouterr().err


def test_check_bridge_reconciles_true_against_real_committed_bridge():
    """The real, committed site/data/margin_bridge.json must itself pass --
    it's already fully_explained with a 1-penny remainder."""
    assert _check_bridge_reconciles() is True


def test_check_basis_labels_present_skips_figures_not_in_this_portfolio():
    # A run with no enterprise_value_gbp at all shouldn't fail the gate over
    # a figure that isn't being published.
    portfolio = {
        "net_margin_gbp": 100.0,
        "basis": {
            "net_margin_gbp": {"clock": "settled", "provisional": True, "note": "x"},
        },
    }
    assert _check_basis_labels_present(portfolio) is True


def test_process_run_complete_generates_insights_before_dashboard():
    """Regression test for the step-ordering bug: run-insights generation
    must happen before dashboard/site generation so the exec summary on
    site/shadow/index.html reflects THIS run, not the previous one."""
    import background.process_run_complete as prc
    # main() only wraps the run-lock check; the actual step ordering this
    # test guards lives in _process(), which main() delegates to once the
    # lock is acquired.
    source = inspect.getsource(prc._process)
    insights_pos = source.index("generate_insights(data, git_hash)")
    dashboard_pos = source.index("generate_dashboard_json(json_path, git_hash)")
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

    # main() only wraps the run-lock check; the actual gate/NTFY ordering
    # this test guards lives in _process(), which main() delegates to once
    # the lock is acquired.
    source = inspect.getsource(prc._process)
    gate_pos = source.index("consistency_ok = generate_dashboard_json(json_path, git_hash)")
    # the consistency-gate NTFY goes through the notify() contract now (send_ntfy was the pre-refactor
    # call). The ordering guarantee this test defends is unchanged: gate check BEFORE the page.
    ntfy_pos = source.index("notify(", gate_pos)
    assert gate_pos < ntfy_pos
