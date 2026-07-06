"""Tests for tools/generate_case_study_recommender.py --
WEBSITE_AS_SHOWCASE.md tab 4 (CUSTOMER PORTAL -- MICRO MEETS MACRO): the
case-study recommender."""
import json
from pathlib import Path as _P
import sys

sys.path.insert(0, str(_P(__file__).resolve().parents[2]))

from tools.generate_case_study_recommender import (
    _max_divergence, _writeoffs, _retention_then_churn, _life_events,
    _score_households, _pick, _fmt_pct, build, generate,
)


def test_max_divergence_picks_largest_abs_error():
    sample = {"C1": {"churn_accuracy_by_renewal": [
        {"term_start": "2016-12-31", "sim_churn_probability": 0.1, "company_churn_estimate": 0.12, "churn_estimate_error_pct": 0.2},
        {"term_start": "2017-12-31", "sim_churn_probability": 0.1, "company_churn_estimate": 0.02, "churn_estimate_error_pct": -0.8},
    ]}}
    worst = _max_divergence(sample, "C1")
    assert worst["term_start"] == "2017-12-31"


def test_max_divergence_none_when_missing():
    assert _max_divergence({}, "C1") is None
    assert _max_divergence({"C1": {}}, "C1") is None


def test_writeoffs_filters_by_outcome():
    chain = [{"outcome": "FIRST_NOTICE"}, {"outcome": "WRITTEN_OFF", "date": "2016-01-01"}, {"outcome": "WRITTEN_OFF", "date": "2017-01-01"}]
    assert len(_writeoffs(chain)) == 2


def test_retention_then_churn_true_when_retention_precedes_churn():
    timeline = [{"type": "renewed", "date": "2018-01-01"}, {"type": "churned", "date": "2020-01-01"}]
    chain = [{"event_type": "retention_decision", "date": "2018-12-31", "outcome": "retained"}]
    assert _retention_then_churn(timeline, chain) is True


def test_retention_then_churn_false_when_retention_after_churn():
    timeline = [{"type": "churned", "date": "2020-01-01"}]
    chain = [{"event_type": "retention_decision", "date": "2021-01-01", "outcome": "retained"}]
    assert _retention_then_churn(timeline, chain) is False


def test_retention_then_churn_false_without_churn():
    timeline = [{"type": "renewed", "date": "2018-01-01"}]
    chain = [{"event_type": "retention_decision", "date": "2018-12-31", "outcome": "retained"}]
    assert _retention_then_churn(timeline, chain) is False


def test_life_events_filters_by_type():
    timeline = [{"type": "renewed"}, {"type": "life_event", "detail": "New baby"}]
    out = _life_events(timeline)
    assert len(out) == 1 and out[0]["detail"] == "New baby"


def test_fmt_pct_uses_absolute_value():
    assert _fmt_pct(-0.25) == "25%"
    assert _fmt_pct(0.5) == "50%"


def test_pick_excludes_already_used_and_respects_filter():
    scored = [
        {"base": "A", "score": 5, "ok": True},
        {"base": "B", "score": 10, "ok": False},
        {"base": "C", "score": 3, "ok": True},
    ]
    used = set()
    best = _pick(scored, used, lambda c: c["score"], filt=lambda c: c["ok"])
    assert best["base"] == "A"
    assert "A" in used
    best2 = _pick(scored, used, lambda c: c["score"], filt=lambda c: c["ok"])
    assert best2["base"] == "C"


def test_pick_returns_none_when_pool_empty():
    assert _pick([], set(), lambda c: c["score"]) is None


def _customer(cid, base, commodity="electricity", timeline=None, reaction_chain=None, segment="resi"):
    return (cid, dict(
        account_id=cid, base_account_id=base, commodity=commodity, segment=segment,
        timeline=timeline or [], reaction_chain=reaction_chain or [],
    ))


def test_build_selects_distinct_households_per_category():
    by_base = dict()
    by_base["C1"] = _customer(
        "C1", "C1",
        timeline=[{"type": "renewed", "date": str(y) + "-01-01"} for y in range(2016, 2026)],
    )
    c2_timeline = [{"type": "renewed", "date": "2018-01-01"}, {"type": "churned", "date": "2021-01-01"}]
    by_base["C2"] = _customer(
        "C2", "C2",
        timeline=c2_timeline,
        reaction_chain=[{"event_type": "retention_decision", "date": "2020-06-01", "outcome": "retained"}],
    )
    by_base["C3"] = _customer(
        "C3", "C3",
        reaction_chain=[
            {"outcome": "WRITTEN_OFF", "date": "2019-01-01"},
            {"outcome": "WRITTEN_OFF", "date": "2019-06-01"},
        ],
    )
    by_base["C7"] = _customer(
        "C7", "C7",
        timeline=[{"type": "life_event", "date": "2020-01-01", "detail": "New baby", "effect": "income stress low -> high"}],
    )
    by_base["C_IC2"] = _customer("C_IC2", "C_IC2", segment="I&C")

    sample = {"C_IC2": {"churn_accuracy_by_renewal": [
        {"term_start": "2019-12-31", "sim_churn_probability": 0.05, "company_churn_estimate": 0.9, "churn_estimate_error_pct": 17.0},
    ]}}
    cases = build(by_base, sample)
    categories = [c["category"] for c in cases]
    assert "Most eventful journey" in categories
    assert "Largest company-vs-SIM churn divergence" in categories
    assert "Retention save, then churned anyway" in categories
    assert "Heaviest arrears cascade" in categories
    assert "Notable life event" in categories
    for c in cases:
        assert "acc" in c["link"] and "tab" in c["link"]
    # every category picked a distinct household
    assert len({c["base_account_id"] for c in cases}) == len(cases)


def test_generate_skips_when_inputs_missing(tmp_path, monkeypatch):
    import tools.generate_case_study_recommender as gcs
    monkeypatch.setattr(gcs, "SAMPLE_PATH", tmp_path / "no_sample.json")
    monkeypatch.setattr(gcs, "CUSTOMERS_DIR", tmp_path / "no_dir")
    assert generate() == 0


def test_generate_end_to_end_writes_case_studies_json(tmp_path, monkeypatch):
    import tools.generate_case_study_recommender as gcs

    cust_dir = tmp_path / "customers"
    cust_dir.mkdir()
    (cust_dir / "_index.json").write_text(json.dumps(["C1"]))
    (cust_dir / "C1.json").write_text(json.dumps(dict(
        account_id="C1", base_account_id="C1", commodity="electricity", segment="resi",
        timeline=[{"type": "renewed", "date": "2018-01-01"}],
        reaction_chain=[],
    )))

    sample_path = tmp_path / "customer_sample.json"
    sample_path.write_text(json.dumps(dict(
        meta=dict(generated_at="2026-01-01T00:00:00Z", git_commit="abc123"),
        customers=dict(C1=dict(churn_accuracy_by_renewal=[])),
    )))

    out_path = tmp_path / "case_studies.json"
    monkeypatch.setattr(gcs, "CUSTOMERS_DIR", cust_dir)
    monkeypatch.setattr(gcs, "SAMPLE_PATH", sample_path)
    monkeypatch.setattr(gcs, "OUT_PATH", out_path)

    count = gcs.generate()
    assert count == 1
    out = json.loads(out_path.read_text())
    assert out["meta"]["household_count"] == 1
    assert out["meta"]["git_commit"] == "abc123"
    assert out["cases"][0]["category"] == "Most eventful journey"
