"""Tests for website-integrity fix (Phase QC): build-info dynamic label +
cross-surface consistency gate, closing the exec-summary/totals contradiction
staged in docs/staging/WEBSITE_INTEGRITY_AND_DESIGN.md Part A."""
import json
import inspect

from tools import generate_dashboard_data
from tools.generate_dashboard_data import (
    _load_build_info, BUILD_INFO_PATH, count_company_modules,
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


def test_a_failing_check_propagates_out_of_generate(tmp_path, monkeypatch):
    """generate() must return the gate verdict, not an unconditional True -- the
    caller relies on it to decide whether to raise the alarm.

    Driven by monkeypatching ONE of the seven remaining checks rather than by
    feeding a specific bad figure, deliberately: the property under test is the
    propagation, and pinning it to a particular check is how this test would have
    gone green-because-unreachable when the exec-summary comparison was retired
    on 2026-08-20 -- which is exactly what it did, since it drove the verdict
    through the one check that no longer exists."""
    import tools.generate_dashboard_data as gdd

    run_json = tmp_path / "run_output_test.json"
    run_json.write_text(json.dumps({
        "total_net_gbp": 100.0,
        "_cache_meta": {"git_commit": "deadbeef"},
    }))
    out_path = tmp_path / "dashboard.json"

    monkeypatch.setattr(gdd, "OUTPUT_PATH", out_path)
    monkeypatch.setattr(gdd, "load_spot_monthly", lambda: {})
    monkeypatch.setattr(gdd, "_check_bridge_reconciles", lambda *a, **k: False)

    ok = gdd.generate(run_json)
    assert ok is False, "a failing check did not reach generate()'s return value"
    # The DATA is still written on a failed verdict -- the gate reports, it does
    # not withhold the surface.
    assert out_path.exists()


def test_the_retired_exec_summary_comparison_has_not_come_back(tmp_path, monkeypatch):
    """Director ruling 2026-08-20: a surface no reader can reach must never be able
    to block publishing. run_insights.json is fetched by no page on the site, so a
    disagreement between it and the dashboard must not change the verdict.

    The mutation is DIFFERENTIAL, not absolute: generate() is run twice over the
    same run output, once with an exec summary that agrees and once with one that
    is wildly wrong, and the two verdicts must be identical. Asserting `is True`
    instead would couple this control to whatever else a stub run happens to trip
    (it trips the basis-parentage and mix-claim gates, both legitimately), and
    would then be measuring those rather than the thing it names.

    The seven surviving checks are forced GREEN for the same reason, and I got
    this wrong first: without that, both runs returned False for unrelated
    reasons, `agreeing == disagreeing` held trivially, and re-introducing the
    retired comparison did NOT turn this test red. A differential control whose
    difference is masked by a short-circuit is the TAUTOLOGY pattern -- it was
    only visible because the mutation was actually run."""
    import tools.generate_dashboard_data as gdd

    run_json = tmp_path / "run_output_test.json"
    run_json.write_text(json.dumps({
        "total_net_gbp": 100.0,
        "_cache_meta": {"git_commit": "deadbeef"},
    }))
    insights_path = tmp_path / "run_insights.json"
    monkeypatch.setattr(gdd, "RUN_INSIGHTS_PATH", insights_path)
    monkeypatch.setattr(gdd, "OUTPUT_PATH", tmp_path / "dashboard.json")
    monkeypatch.setattr(gdd, "load_spot_monthly", lambda: {})
    for surviving in ("_check_population_consistency", "_check_basis_labels_present",
                      "_check_derived_basis_parentage", "_check_bridge_reconciles",
                      "_check_bad_debt_reconciliation_present",
                      "_check_period_coverage_present", "_check_front_door_segment_claim"):
        assert hasattr(gdd, surviving), f"{surviving} is gone -- update this list"
        monkeypatch.setattr(gdd, surviving, lambda *a, **k: True)

    insights_path.write_text(json.dumps({"net_margin_gbp": 100.0}))
    agreeing = gdd.generate(run_json)
    insights_path.write_text(json.dumps({"net_margin_gbp": -999999.0}))
    disagreeing = gdd.generate(run_json)

    assert agreeing is True, (
        "the seven surviving checks are all forced green, so the verdict can only "
        "be False here if something ELSE joined the conjunction -- find it"
    )

    assert agreeing == disagreeing, (
        "the exec summary still moves the publish verdict: agreeing={} disagreeing={}. "
        "No page on the site fetches run_insights.json, so it cannot be allowed to "
        "decide whether a reader-facing figure publishes.".format(agreeing, disagreeing)
    )
    assert not hasattr(gdd, "_check_consistency"), (
        "the retired dashboard-vs-exec-summary comparison is back in the module"
    )


def test_generate_dashboard_json_returns_gate_status(tmp_path, monkeypatch):
    import background.process_run_complete as prc

    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")  # isolate from real sim-runner-log.md
    # Test throughput fix (TEST_THROUGHPUT_MEASUREMENT_AND_PROPOSAL.md root
    # cause #2). generate_dashboard_json() unconditionally runs the ENTIRE
    # site-regeneration pipeline (~40 generator calls) after the dashboard-data
    # call this test cares about -- most take json_path and fail fast on the
    # nonexistent tmp_path/run.json (caught + logged), but a handful take NO
    # json_path at all and read/write real repo state regardless, with no
    # staleness gate this test can rely on:
    #   - tools.run_frozen_baseline.generate(): weekly-gated internally
    #     (should_refresh_baseline()) -- replays the full decade TWICE
    #     (current vs naive policy) whenever that gate is stale/missing.
    #     The design doc's original profiling attributed the whole ~117s to
    #     this call alone.
    #   - Direct re-profiling (2026-07-19, via a timed instrumentation of
    #     every generate_dashboard_json step with only the two mocks above
    #     applied) found that in THIS repo/test environment the frozen
    #     baseline was already fresh (a fast no-op) but the test still took
    #     ~107s -- almost entirely two OTHER unconditional, non-json_path-gated
    #     calls: tools.generate_provisional_plan_data.main() (~57s) and
    #     tools.generate_test_mix_data.generate() (~47s, documented in that
    #     module as "20 pytest --collect-only subprocess calls"). Neither is
    #     part of what this test asserts (dashboard-data's gate-status return
    #     value propagating through), so they are pure orthogonal cost here.
    # All three are mocked below (frozen-baseline defensively, per the design
    # doc, plus the two calls actually measured as dominant); every other
    # downstream generator in the pipeline is left real since each already
    # runs in well under a second (measured total for the rest: ~3s).
    monkeypatch.setattr(
        "tools.run_frozen_baseline.generate",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "tools.generate_provisional_plan_data.main",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "tools.generate_test_mix_data.generate",
        lambda *args, **kwargs: None,
    )
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
