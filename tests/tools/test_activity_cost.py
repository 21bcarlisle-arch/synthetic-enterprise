"""Tests for tools/activity_cost.py (G11_activity_cost_utilisation).

Covers, mirroring test_effort_calibration.py's style:
  * commit classification -- every taxonomy branch of the ordered ruleset,
    including the fix-of-product vs fix-of-plumbing split that depends on the
    changed-file domain, and the fail-honest `unattributed` fallback;
  * bounded inter-commit time attribution (gap cap -> WASTE/idle excess,
    first-commit-has-no-anchor, non-positive gaps dropped);
  * token-log parsing + classification + the insufficient_data degrade;
  * director-idle from a fixture escalation register (open vs resolved,
    missing-register degrade);
  * the five headline metrics;
  * one end-to-end build_report() against a real temp git repo.

GUARDRAIL under test: every figure is a DIAGNOSTIC, never a target -- the tests
assert the guardrail string is carried through, not that any metric hits a value.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from tools.activity_cost import (
    ALL_CLASSES,
    DISCOVERY,
    HIT_LIMIT,
    IDLE,
    IDLE_DIRECTOR,
    IDLE_GAP_CAP_SECONDS,
    PRODUCT,
    REWORK,
    SELF_REPAIR,
    UNATTRIBUTED,
    Commit,
    attribute_time,
    attribute_tokens,
    build_report,
    classify_commit,
    classify_commits,
    classify_token_entry,
    compute_metrics,
    director_idle,
    parse_token_log,
    self_maintenance_trend,
    _domain,
)


def _c(subject, ts=1000, files=None, sha="sha"):
    return Commit(sha=sha, timestamp=ts, subject=subject, files=files or [])


# ---------------------------------------------------------------------------
# Commit classification -- the ordered ruleset (pure, no git)
# ---------------------------------------------------------------------------
def test_classify_rework_wins_first():
    cls, rule = classify_commit(_c("Revert bad merge of C9"))
    assert cls == REWORK and rule == "rework_keyword"
    assert classify_commit(_c("H17 Lane-3 re-draw of 6 idle atoms"))[0] == REWORK


def test_classify_hit_limit():
    assert classify_commit(_c("Paused: usage limit reached, auto-resume"))[0] == HIT_LIMIT


def test_classify_director_block():
    assert classify_commit(_c("Escalated one-way door to director via NTFY"))[0] == IDLE_DIRECTOR


def test_classify_level_transition_is_product():
    cls, rule = classify_commit(_c("D2_three_clocks -> L1 bridge wired"))
    assert cls == PRODUCT and rule == "level_transition"


def test_fix_of_product_vs_plumbing_uses_file_domain():
    # A "fix" is self-repair only if it repaired the plumbing; a fix to the
    # product is product work -- decided by the changed-file domain, not the word.
    prod = classify_commit(_c("Fix billing rounding", files=["saas/billing.py"]))
    assert prod == (PRODUCT, "fix_of_product")
    plumb = classify_commit(_c("Fix stale supervisor daemon", files=["background/supervisor.py"]))
    assert plumb == (SELF_REPAIR, "fix_of_plumbing")
    # a fix touching neither domain clearly -> self-repair default (still a fix)
    assert classify_commit(_c("Fix flaky thing", files=[]))[0] == SELF_REPAIR


def test_classify_discovery_keyword():
    assert classify_commit(_c("DISCOVER: benchmark churn against Ofgem"))[0] == DISCOVERY
    assert classify_commit(_c("Register 3 director atoms"))[0] == DISCOVERY


# --- H17 HARDEN class-fix: keyword false-positives from staged-directive prose ---
def test_staging_directive_is_discovery_not_the_activity_its_prose_describes():
    # A commit whose files are ALL under docs/staging/ is a directive being
    # STAGED; its subject QUOTES policy words ("revert", "escalation", "two-strike",
    # "quota") that must NOT keyword-classify it into a WASTE bucket. This was the
    # single largest false-positive source (policy docs mis-billed as rework /
    # idle-on-director / hit-limit). Staging/framing a directive is discovery.
    assert classify_commit(_c(
        "[ADVISOR-STAGED] two-strike auto-escalation policy; revert stale rules",
        files=["docs/staging/PRIORITISATION_RULES.md"],
    )) == (DISCOVERY, "staging_directive")
    assert classify_commit(_c(
        "[ADVISOR-STAGED] ESCALATION IS NTFY NEVER THE WINDOW (one-way door)",
        files=["docs/staging/ESCALATION_IS_NTFY.md"],
    ))[0] == DISCOVERY
    # a real code revert is NOT all-staging -> still rework
    assert classify_commit(_c("Revert bad curve", files=["saas/b.py"]))[0] == REWORK


def test_director_block_requires_director_word_not_a_domain_escalation():
    # "escalation" is an energy-domain term (Ombudsman escalation) and appears in
    # plumbing fixes -- it must not alone mean idle-waiting-on-director.
    assert classify_commit(_c(
        "Phase 155: complaint management and Ombudsman escalation",
        files=["company/crm/complaints.py"],
    ))[0] == PRODUCT
    assert classify_commit(_c(
        "Fix escalation gap in the twin", files=["background/director_twin.py"],
    ))[0] == SELF_REPAIR
    # a genuine block (director word + block cue) still classifies as director-idle
    assert classify_commit(_c("Blocked on director decision, awaiting NTFY"))[0] == IDLE_DIRECTOR


def test_hit_limit_requires_an_interruption_not_building_limit_handling():
    # BUILDING/FIXING usage-limit handling is self-repair, not a hit-limit WASTE event.
    assert classify_commit(_c(
        "fix: tighten usage-limit detection", files=["background/session_watchdog.py"],
    ))[0] == SELF_REPAIR
    assert classify_commit(_c(
        "feat: usage-limit auto-resume in watchdog", files=["background/session_watchdog.py"],
    ))[0] == SELF_REPAIR
    # an ACTUAL interruption still classifies as hit-limit
    assert classify_commit(_c("Paused: usage limit reached, auto-resume"))[0] == HIT_LIMIT


def test_classify_product_keyword():
    assert classify_commit(_c("Auto-process run complete: report + site/"))[0] == PRODUCT
    assert classify_commit(_c("[build] hedge desk VaR"))[0] == PRODUCT


def test_classify_falls_back_to_file_domain_then_unattributed():
    assert classify_commit(_c("misc", files=["company/x.py"]))[0] == PRODUCT
    assert classify_commit(_c("misc", files=["docs/design/x.md"]))[0] == DISCOVERY
    assert classify_commit(_c("misc", files=["background/x.py"]))[0] == SELF_REPAIR
    # no subject signal AND no file signal -> unattributed (fail-honest, never product)
    assert classify_commit(_c("misc", files=["README.md"]))[0] == UNATTRIBUTED


def test_domain_plurality_and_ties():
    assert _domain(["saas/a.py", "saas/b.py", "background/c.py"]) == "product"
    assert _domain(["saas/a.py", "background/b.py"]) == "mixed_or_unknown"  # tie
    assert _domain([]) == "mixed_or_unknown"
    assert _domain(["README.md"]) == "mixed_or_unknown"


# ---------------------------------------------------------------------------
# Time attribution
# ---------------------------------------------------------------------------
def test_attribute_time_first_commit_has_no_anchor():
    r = attribute_time([_c("[build] x", ts=1000, files=["saas/a.py"])])
    assert r["status"] == "insufficient_data"


def test_attribute_time_bounded_gap_and_idle_excess():
    cap = IDLE_GAP_CAP_SECONDS
    commits = [
        _c("[build] a", ts=0, files=["saas/a.py"]),
        _c("[build] b", ts=cap + 3600, files=["saas/b.py"]),  # gap = cap + 1h
    ]
    r = attribute_time(commits)
    assert r["status"] == "ok"
    # product gets the capped work-time; the 1h excess is billed to WASTE/idle
    assert r["by_class_seconds"][PRODUCT] == pytest.approx(cap, abs=1)
    assert r["by_class_seconds"][IDLE] == pytest.approx(3600, abs=1)


def test_attribute_time_drops_non_positive_gap():
    commits = [_c("[build] a", ts=500, files=["saas/a.py"]),
               _c("[build] b", ts=500, files=["saas/b.py"])]  # same ts
    r = attribute_time(commits)
    assert r["status"] == "ok"
    assert r["attributed_seconds"] == 0


def test_attribute_time_unattributed_not_counted_in_denominator():
    commits = [
        _c("[build] a", ts=0, files=["saas/a.py"]),
        _c("misc no signal", ts=600, files=["README.md"]),  # unattributed
    ]
    r = attribute_time(commits)
    assert r["unattributed_seconds"] == pytest.approx(600, abs=1)
    # unattributed excluded from attributed denominator
    assert r["attributed_seconds"] == 0
    assert r["productive_pct"] is None


# ---------------------------------------------------------------------------
# Token log parsing / attribution
# ---------------------------------------------------------------------------
def _write_token_log(tmp_path, body):
    p = tmp_path / "token-log.md"
    p.write_text(body)
    return p


def test_parse_token_log_reads_dated_session_entries(tmp_path):
    body = (
        "# header\n## How to log\n- **Frontier tokens:** should be ignored (not dated)\n"
        "## 2026-06-07 -- Phase 0a -- scaffold\n"
        "- **Frontier tokens:** ~131,168 (in: 192, out: 52,124)\n"
        "## 2026-06-08 -- Phase 0b -- settlement\n"
        "- **Frontier tokens:** 90,000\n"
    )
    entries = parse_token_log(_write_token_log(tmp_path, body))
    assert [e["tokens"] for e in entries] == [131168, 90000]


def test_parse_token_log_missing_file_is_empty(tmp_path):
    assert parse_token_log(tmp_path / "nope.md") == []


def test_classify_token_entry_keywords():
    assert classify_token_entry("2026 -- Fix stale daemon housekeeping")[0] == SELF_REPAIR
    assert classify_token_entry("2026 -- DISCOVER churn research")[0] == DISCOVERY
    assert classify_token_entry("2026 -- Phase 12a customer settlement")[0] == PRODUCT
    assert classify_token_entry("2026 -- opaque")[0] == UNATTRIBUTED


def test_attribute_tokens_insufficient_data_when_none_parse():
    r = attribute_tokens([{"heading": "2026 x", "tokens": None}])
    assert r["status"] == "insufficient_data"
    assert r["n_unparsed"] == 1


def test_attribute_tokens_ok_and_unattributed_surfaced():
    entries = [
        {"heading": "2026 -- Phase 1 settlement", "tokens": 100},   # product
        {"heading": "2026 -- Fix daemon", "tokens": 40},            # self-repair
        {"heading": "2026 -- opaque", "tokens": 60},                # unattributed
    ]
    r = attribute_tokens(entries)
    assert r["status"] == "ok"
    assert r["by_class_tokens"][PRODUCT] == 100
    assert r["by_class_tokens"][SELF_REPAIR] == 40
    assert r["unattributed_tokens"] == 60
    # attributed denominator excludes unattributed
    assert r["attributed_tokens"] == 140
    assert r["productive_pct"] == pytest.approx(100 * 100 / 140, abs=0.1)


# ---------------------------------------------------------------------------
# Director-idle from the escalation register
# ---------------------------------------------------------------------------
def test_director_idle_counts_only_open_items(tmp_path):
    reg = {
        "open_item": {"item_id": "open_item", "resolved": False,
                      "what": "sign the ratio", "first_asked_at": "2026-07-16T00:00:00+00:00"},
        "closed_item": {"item_id": "closed_item", "resolved": True,
                        "what": "done", "first_asked_at": "2026-07-15T00:00:00+00:00"},
    }
    p = tmp_path / "action_needed.json"
    p.write_text(json.dumps(reg))
    now = int(__import__("datetime").datetime(2026, 7, 16, 5, tzinfo=__import__("datetime").timezone.utc).timestamp())
    r = director_idle(p, now=now)
    assert r["status"] == "ok"
    assert r["open_count"] == 1
    assert r["items"][0]["item_id"] == "open_item"
    assert r["oldest_open_hours"] == pytest.approx(5.0, abs=0.1)


def test_director_idle_missing_register_is_honest(tmp_path):
    r = director_idle(tmp_path / "nope.json")
    assert r["status"] == "no_register"
    assert r["open_count"] is None


# ---------------------------------------------------------------------------
# Trend + metrics
# ---------------------------------------------------------------------------
def test_self_maintenance_trend_windows_present():
    now = 100 * 86400
    commits = [
        _c("Fix daemon", ts=now - 3 * 86400, files=["background/a.py"]),
        _c("[build] x", ts=now - 3 * 86400 + 600, files=["saas/a.py"]),
        _c("[build] y", ts=now, files=["saas/b.py"]),
    ]
    tr = self_maintenance_trend(commits, windows=(30, 7))
    assert tr["status"] == "ok"
    assert {w["window_days"] for w in tr["windows"]} == {30, 7}


def test_compute_metrics_shape_and_fail_honest():
    time_attr = attribute_time([
        _c("[build] a", ts=0, files=["saas/a.py"]),
        _c("Fix daemon", ts=600, files=["background/x.py"]),
    ])
    count_attr = classify_commits([
        _c("[build] a", files=["saas/a.py"]),
        _c("Revert x"),
        _c("Fix daemon", files=["background/x.py"]),
    ])
    token_attr = attribute_tokens([{"heading": "2026 -- opaque", "tokens": None}])  # insufficient
    director = director_idle(Path("/definitely/missing.json"))
    trend = {"status": "ok", "windows": []}
    m = compute_metrics(time_attr, count_attr, token_attr, director, trend)
    for k in ("productive_pct", "cost_of_self_maintenance", "rework_rate",
              "value_per_problem", "idle_on_director"):
        assert k in m
    # token side unavailable -> cost_pct is None, not a fabricated number
    assert m["productive_pct"]["cost_pct"] is None
    # rework rate reflects the one revert of three classified commits
    assert m["rework_rate"]["rework_commits"] == 1
    # director register missing -> honest status carried through
    assert m["idle_on_director"]["status"] == "no_register"


# ---------------------------------------------------------------------------
# End-to-end against a real temp git repo (mirrors test_effort_calibration)
# ---------------------------------------------------------------------------
def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_build_report_end_to_end(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "saas").mkdir()
    (repo / "background").mkdir()

    def commit(subject, path, ts):
        f = repo / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(str(ts))
        _git(repo, "add", str(path))
        env_date = f"{ts} +0000"
        subprocess.run(
            ["git", "commit", "-q", "-m", subject,
             "--date", env_date],
            cwd=repo, check=True, capture_output=True, text=True,
            env={**__import__("os").environ, "GIT_COMMITTER_DATE": env_date},
        )

    base = 1_700_000_000
    commit("[build] settlement engine", "saas/a.py", base)
    commit("Fix stale daemon", "background/d.py", base + 600)
    commit("W1_2 -> L2 forward curve", "saas/b.py", base + 1200)
    commit("Revert bad curve", "saas/b.py", base + 1800)

    # token log + escalation register fixtures
    token_log = repo / "token-log.md"
    token_log.write_text(
        "## 2026-06-07 -- Phase 0a -- settlement\n- **Frontier tokens:** 100,000\n"
        "## 2026-06-08 -- Fix daemon housekeeping\n- **Frontier tokens:** 20,000\n"
    )
    action = repo / "action_needed.json"
    action.write_text(json.dumps({
        "x": {"item_id": "x", "resolved": False, "what": "sign it",
              "first_asked_at": "2026-07-16T00:00:00+00:00"},
    }))

    report = build_report(repo, token_log=token_log, action_needed=action)
    assert report["guardrail"]  # guardrail carried through
    assert set(report["taxonomy"]) == set(ALL_CLASSES)
    assert report["commit_classification"]["n_commits"] == 4
    # the revert is a rework commit; the transition + build are product
    counts = report["commit_classification"]["by_class_counts"]
    assert counts[REWORK] == 1
    assert counts[PRODUCT] >= 2
    assert counts[SELF_REPAIR] == 1
    # token side parsed -> productive_pct present, self-repair share present
    assert report["token_attribution"]["status"] == "ok"
    assert report["metrics"]["idle_on_director"]["open_count"] == 1
